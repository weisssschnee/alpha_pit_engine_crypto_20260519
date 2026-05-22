from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import crypto_a7s2m_metrics_registry_diagnostic as a7s2m
import crypto_a7y1_interaction_diagnostic as a7y1


ROOT = Path(__file__).resolve().parents[1]
A7Y1_DIR = ROOT / "runtime" / "a7y1_interaction_diagnostic"
OUT_DIR = ROOT / "runtime" / "a7y2_interaction_clue_forensic"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7Y2_INTERACTION_CLUE_FORENSIC_20260522.md"

VALIDATION = "validation_2025H1"
RECENT = "recent_oos_2025H2_2026Apr"
MAY = "fresh_may_2026"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def clean_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def position_book(signal: np.ndarray, target: np.ndarray, orientation: float, cost_bps: float, k: int) -> dict[str, np.ndarray]:
    oriented = signal * orientation
    valid = np.isfinite(oriented) & np.isfinite(target)
    valid_rows = valid.sum(axis=1) >= (2 * k)
    pos = np.zeros_like(target, dtype=float)
    if np.any(valid_rows):
        high = np.where(valid, oriented, -np.inf)
        low = np.where(valid, oriented, np.inf)
        rows = np.where(valid_rows)[0]
        long_idx = np.argpartition(high[valid_rows], -k, axis=1)[:, -k:]
        short_idx = np.argpartition(low[valid_rows], k - 1, axis=1)[:, :k]
        weight = 0.5 / k
        for r_pos, r in enumerate(rows):
            pos[r, long_idx[r_pos]] = weight
            pos[r, short_idx[r_pos]] = -weight
    gross_by_symbol = pos * target
    gross = np.nansum(gross_by_symbol, axis=1)
    prev = np.vstack([np.zeros((1, pos.shape[1])), pos[:-1, :]])
    turnover_by_symbol = np.abs(pos - prev) / 2.0
    fee_by_symbol = turnover_by_symbol * (cost_bps / 10000.0)
    return {
        "pos": pos,
        "gross_by_symbol": gross_by_symbol,
        "fee_by_symbol": fee_by_symbol,
        "net_by_symbol": gross_by_symbol - fee_by_symbol,
        "net": gross - np.nansum(fee_by_symbol, axis=1),
        "turnover": np.nansum(turnover_by_symbol, axis=1),
        "gross_exposure": np.nansum(np.abs(pos), axis=1),
    }


def evaluate_clue(index: pd.DatetimeIndex, symbols: list[str], matrices: dict[str, np.ndarray], ctx: a7s2m.ExprContext, row: pd.Series) -> dict[str, Any]:
    lane = str(row["lane"])
    k = 3 if lane == "core12_metrics" else 1
    signal = np.where(matrices["lane_features_available"].astype(bool), ctx.eval(str(row["expression"])), np.nan)
    target = a7s2m.forward_open_return(matrices["open"], int(row["horizon"]))
    train = a7s2m.split_mask(index, "train_2024")
    train_ic = np.nanmean(a7s2m.row_ic(signal[train], target[train]))
    orientation = 1.0 if not np.isfinite(train_ic) or train_ic >= 0 else -1.0
    book10 = position_book(signal, target, orientation, a7y1.PRIMARY_COST_BPS, k)
    book20 = position_book(signal, target, orientation, a7y1.SEVERE_COST_BPS, k)
    lag1_signal = np.where(matrices["lane_features_available"].astype(bool), a7s2m.apply_control(signal, "lag1_stress", str(row["candidate_id"])), np.nan)
    lag1 = position_book(lag1_signal, target, orientation, a7y1.PRIMARY_COST_BPS, k)
    return {"row": row, "symbols": symbols, "signal": signal, "target": target, "orientation": orientation, "train_ic": train_ic, "book10": book10, "book20": book20, "lag1": lag1, "k": k}


def split_rows(index: pd.DatetimeIndex, result: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    row = result["row"]
    for split in a7s2m.SPLITS:
        mask = a7s2m.split_mask(index, split)
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "lane": row["lane"],
                "production_family": row["production_family"],
                "expression": row["expression"],
                "horizon": int(row["horizon"]),
                "split": split,
                "orientation": result["orientation"],
                "train_ic": clean_float(result["train_ic"]),
                "active_hours": int(np.sum(result["book10"]["gross_exposure"][mask] > 0)),
                "net10": clean_float(np.nansum(result["book10"]["net"][mask])),
                "net20": clean_float(np.nansum(result["book20"]["net"][mask])),
                "lag1_net10": clean_float(np.nansum(result["lag1"]["net"][mask])),
                "turnover_mean": clean_float(np.nanmean(result["book10"]["turnover"][mask])),
                "gross_exposure_mean": clean_float(np.nanmean(result["book10"]["gross_exposure"][mask])),
            }
        )
    return rows


def symbol_rows(index: pd.DatetimeIndex, result: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    row = result["row"]
    for split in a7s2m.SPLITS:
        mask = a7s2m.split_mask(index, split)
        net_by_symbol = np.nansum(result["book10"]["net_by_symbol"][mask], axis=0)
        for i, symbol in enumerate(result["symbols"]):
            rows.append(
                {
                    "candidate_id": row["candidate_id"],
                    "lane": row["lane"],
                    "horizon": int(row["horizon"]),
                    "split": split,
                    "symbol": symbol,
                    "net10": clean_float(net_by_symbol[i]),
                    "active_hours": int(np.sum(np.abs(result["book10"]["pos"][mask, i]) > 0)),
                }
            )
    return rows


def month_rows(index: pd.DatetimeIndex, result: dict[str, Any]) -> pd.DataFrame:
    row = result["row"]
    df = pd.DataFrame({"timestamp": index, "net10": result["book10"]["net"], "gross_exposure": result["book10"]["gross_exposure"]})
    df["month"] = df["timestamp"].dt.strftime("%Y-%m")
    out = df.groupby("month").agg(net10=("net10", "sum"), active_hours=("gross_exposure", lambda x: int(np.sum(np.asarray(x) > 0)))).reset_index()
    out.insert(0, "horizon", int(row["horizon"]))
    out.insert(0, "lane", row["lane"])
    out.insert(0, "candidate_id", row["candidate_id"])
    return out


def control_rows(index: pd.DatetimeIndex, result: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    row = result["row"]
    k = result["k"]
    for mode in ["sign_flip", "wrong_lag", "row_shuffle", "time_shuffle"]:
        ctrl = a7s2m.apply_control(result["signal"], mode, str(row["candidate_id"]) + mode)
        ctrl = np.where(np.isfinite(result["signal"]), ctrl, np.nan)
        book = position_book(ctrl, result["target"], result["orientation"], a7y1.PRIMARY_COST_BPS, k)
        for split in a7s2m.SPLITS:
            mask = a7s2m.split_mask(index, split)
            rows.append(
                {
                    "candidate_id": row["candidate_id"],
                    "lane": row["lane"],
                    "horizon": int(row["horizon"]),
                    "control_mode": mode,
                    "split": split,
                    "net10": clean_float(np.nansum(book["net"][mask])),
                    "active_hours": int(np.sum(book["gross_exposure"][mask] > 0)),
                }
            )
    return rows


def robustness_summary(split_df: pd.DataFrame, symbol_df: pd.DataFrame, month_df: pd.DataFrame, control_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cid, group in split_df.groupby("candidate_id"):
        rec = group.set_index("split")
        horizon = int(group["horizon"].iloc[0])
        lane = group["lane"].iloc[0]
        s_recent = symbol_df[(symbol_df["candidate_id"].eq(cid)) & (symbol_df["split"].eq(RECENT))]
        recent_total = float(rec.loc[RECENT, "net10"])
        s_recent = s_recent.assign(loo_net10=recent_total - s_recent["net10"].astype(float))
        m = month_df[(month_df["candidate_id"].eq(cid)) & (month_df["month"] >= "2025-07") & (month_df["month"] <= "2026-04")].copy()
        m = m.assign(loo_net10=recent_total - m["net10"].astype(float))
        c_recent = control_df[(control_df["candidate_id"].eq(cid)) & (control_df["split"].eq(RECENT))]
        rows.append(
            {
                "candidate_id": cid,
                "lane": lane,
                "horizon": horizon,
                "validation_net10": clean_float(rec.loc[VALIDATION, "net10"]),
                "validation_net20": clean_float(rec.loc[VALIDATION, "net20"]),
                "recent_net10": clean_float(rec.loc[RECENT, "net10"]),
                "recent_net20": clean_float(rec.loc[RECENT, "net20"]),
                "may_net10": clean_float(rec.loc[MAY, "net10"]),
                "lag1_recent_net10": clean_float(rec.loc[RECENT, "lag1_net10"]),
                "recent_symbol_loo_positive_rate": clean_float((s_recent["loo_net10"] > 0).mean()),
                "recent_min_symbol_loo_net10": clean_float(s_recent["loo_net10"].min()),
                "recent_month_loo_positive_rate": clean_float((m["loo_net10"] > 0).mean()),
                "recent_min_month_loo_net10": clean_float(m["loo_net10"].min()),
                "recent_control_positive_count": int((c_recent["net10"] > 0).sum()),
                "passes_20bps": bool(float(rec.loc[VALIDATION, "net20"]) > 0 and float(rec.loc[RECENT, "net20"]) > 0),
                "passes_lag1": bool(float(rec.loc[RECENT, "lag1_net10"]) > 0),
                "passes_symbol_loo": bool((s_recent["loo_net10"] > 0).mean() >= (0.75 if lane == "core12_metrics" else 1.0) and s_recent["loo_net10"].min() > 0),
                "passes_month_loo": bool((m["loo_net10"] > 0).mean() >= 0.70 and m["loo_net10"].min() > 0),
                "passes_controls": bool((c_recent["net10"] > 0).sum() == 0),
                "passes_may": bool(float(rec.loc[MAY, "net10"]) > 0),
            }
        )
    return pd.DataFrame(rows)


def write_report(now: str, summary: pd.DataFrame, split_df: pd.DataFrame, symbol_df: pd.DataFrame, auth: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Crypto A7Y-2 Interaction Clue Forensic",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{auth['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `forensic_on_a7y1_clues_only`",
        "- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7Y-2 audits the four A7Y-1 interaction clues. It does not generate new formulas and keeps core12 and core3 lanes separate.",
        "",
        "## Robustness Summary",
        "",
        table(summary, max_rows=40),
        "",
        "## Split Metrics",
        "",
        table(split_df, max_rows=80),
        "",
        "## Recent Symbol Contribution",
        "",
        table(symbol_df[symbol_df["split"].eq(RECENT)].sort_values(["candidate_id", "net10"], ascending=[True, False]), max_rows=80),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(auth, indent=2, sort_keys=True),
        "```",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    labels = pd.read_csv(A7Y1_DIR / "a7y1_candidate_labels.csv")
    selected = pd.read_csv(A7Y1_DIR / "a7y1_selected_candidates.csv")
    clue_ids = labels[labels["a7y1_label"].eq("A7Y1_INTERACTION_RESEARCH_CLUE_FOR_FORENSIC")]["candidate_id"]
    clues = selected[selected["candidate_id"].isin(set(clue_ids))].copy()
    if clues.empty:
        raise RuntimeError("No A7Y1 clues available for forensic")

    split_all: list[dict[str, Any]] = []
    symbol_all: list[dict[str, Any]] = []
    month_parts: list[pd.DataFrame] = []
    control_all: list[dict[str, Any]] = []
    for lane in sorted(clues["lane"].unique()):
        lane_clues = clues[clues["lane"].eq(lane)].copy()
        index, symbols, matrices = a7y1.load_matrices(lane_clues, lane)
        ctx = a7s2m.ExprContext(matrices)
        for _, row in lane_clues.iterrows():
            res = evaluate_clue(index, symbols, matrices, ctx, row)
            split_all.extend(split_rows(index, res))
            symbol_all.extend(symbol_rows(index, res))
            month_parts.append(month_rows(index, res))
            control_all.extend(control_rows(index, res))
    split_df = pd.DataFrame(split_all)
    symbol_df = pd.DataFrame(symbol_all)
    month_df = pd.concat(month_parts, ignore_index=True)
    control_df = pd.DataFrame(control_all)
    summary = robustness_summary(split_df, symbol_df, month_df, control_df)
    clean = summary[
        summary["passes_20bps"]
        & summary["passes_lag1"]
        & summary["passes_symbol_loo"]
        & summary["passes_month_loo"]
        & summary["passes_controls"]
        & summary["passes_may"]
    ]
    blockers = []
    warnings = []
    if clean.empty:
        blockers.append("no_interaction_clue_passes_robustness")
    if int(summary["recent_control_positive_count"].sum()) > 0:
        blockers.append("recent_control_positive")
    if (summary["passes_symbol_loo"] == False).any():  # noqa: E712
        warnings.append("symbol_loo_weak_for_some_clues")
    if (summary["passes_month_loo"] == False).any():  # noqa: E712
        warnings.append("month_loo_weak_for_some_clues")
    decision = "PASS_A7Y2_INTERACTION_ROBUST_CLUE_FOR_SMALL_REPLAY_REVIEW" if not blockers else "HOLD_A7Y2_INTERACTION_CLUES_NOT_ROBUST"
    auth = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "clue_count": int(len(clues)),
        "robust_clue_count": int(len(clean)),
        "executes_search": False,
        "executes_replay": "forensic_on_a7y1_clues_only",
        "authorizes_a7y3_small_replay_review": bool(len(clean) > 0 and not blockers),
        "authorizes_expanded_replay": False,
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": [
            "If robust clues exist, run A7Y-3 small replay review only",
            "Do not combine core12 and core3 lanes into a single proof object",
            "No alpha proof or full search",
        ],
    }
    split_df.to_csv(OUT_DIR / "a7y2_clue_split_metrics.csv", index=False)
    symbol_df.to_csv(OUT_DIR / "a7y2_symbol_contribution.csv", index=False)
    month_df.to_csv(OUT_DIR / "a7y2_month_contribution.csv", index=False)
    control_df.to_csv(OUT_DIR / "a7y2_control_detail.csv", index=False)
    summary.to_csv(OUT_DIR / "a7y2_robustness_summary.csv", index=False)
    clean.to_csv(OUT_DIR / "a7y2_robust_clues.csv", index=False)
    write_json(OUT_DIR / "a7y2_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7y2_manifest.json", {"generated_at": now, "decision": decision, "output_dir": str(OUT_DIR), "report": str(REPORT_PATH)})
    write_report(now, summary, split_df, symbol_df, auth)
    print(json.dumps({"decision": decision, "blockers": blockers, "robust_clues": len(clean), "clues": len(clues)}, indent=2))


if __name__ == "__main__":
    main()
