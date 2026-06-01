from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import crypto_a7ffcore9e_bounded_replay_execution as replay9e  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ffcore14e_bounded_replay"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE14E_BOUNDED_REPLAY_EXECUTION_20260601.md"
A7FFCORE14 = REPO / "runtime" / "a7ffcore14_replay_preflight_contract" / "a7ffcore14_manifest.json"
PACKET = REPO / "runtime" / "a7ffcore14_replay_preflight_contract" / "a7ffcore14_replay_packet.csv"
CLUES = REPO / "runtime" / "a7ffcore13e_numeric_response" / "a7ffcore13e_numeric_clues.csv"

HORIZONS = replay9e.HORIZONS
LABELS = replay9e.LABELS
COST_BPS = replay9e.COST_BPS
SPLITS_FOR_CLEAN = ["validation", "recent"]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def choose_best_clue(clues: pd.DataFrame) -> pd.DataFrame:
    clues = clues[clues["label_id"].isin(LABELS)].copy()
    clues["abs_corr"] = pd.to_numeric(clues["corr"], errors="coerce").abs()
    return (
        clues.sort_values(["candidate_id", "control_ratio", "abs_corr"], ascending=[True, True, False])
        .groupby("candidate_id", as_index=False)
        .head(1)[["candidate_id", "label_id", "horizon", "corr", "control_ratio"]]
        .rename(columns={"corr": "orientation_corr", "control_ratio": "numeric_control_ratio"})
    )


def build_placebo_map(packet: pd.DataFrame) -> dict[str, str]:
    placebo: dict[str, str] = {}
    ordered = packet.sort_values(["semantic_bucket", "motif_bucket", "core14_rank"], ascending=[True, True, False])
    for _, group in ordered.groupby(["semantic_bucket", "motif_bucket"], dropna=False):
        ids = group["candidate_id"].astype(str).tolist()
        exprs = group["expression"].astype(str).tolist()
        if len(ids) < 2:
            continue
        for idx, candidate_id in enumerate(ids):
            placebo[candidate_id] = exprs[(idx + 1) % len(exprs)]
    return placebo


def symbol_shuffle(values: np.ndarray, frame: pd.DataFrame) -> np.ndarray:
    out = np.full(len(frame), np.nan, dtype=float)
    tmp = frame[["timestamp", "symbol"]].copy()
    tmp["_pos"] = np.arange(len(frame))
    tmp["_v"] = values
    for _, group in tmp.groupby("timestamp", sort=False):
        if len(group) < 2:
            out[group["_pos"].to_numpy()] = group["_v"].to_numpy(dtype=float)
            continue
        ordered = group.sort_values("symbol")
        shuffled = np.roll(ordered["_v"].to_numpy(dtype=float), 7 % len(ordered))
        out[ordered["_pos"].to_numpy()] = shuffled
    return out


def replay_control_stats(frame: pd.DataFrame, label_col_name: str) -> dict[str, dict[str, float]]:
    stats = {"original": replay9e.replay_stats(frame, "signal", label_col_name)}
    for col in ["wrong_lag_future", "wrong_lag_stale", "time_shuffle", "symbol_shuffle", "same_family_placebo"]:
        if col in frame.columns:
            stats[col] = replay9e.replay_stats(frame, col, label_col_name)
    return stats


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    replay9e.MAX_TIMESTAMPS_PER_SPLIT = 512

    core14 = read_json(A7FFCORE14)
    if core14.get("decision") != "PASS_A7FFCORE14_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE14E":
        raise SystemExit(f"A7FF-CORE14 is not ready: {core14.get('decision')}")

    packet = pd.read_csv(PACKET)
    clues = pd.read_csv(CLUES)
    best = choose_best_clue(clues)
    packet = packet.merge(best, on="candidate_id", how="inner", validate="one_to_one")
    placebo_map = build_placebo_map(packet)

    required_fields = replay9e.split_fields(packet["raw_inputs"])
    panel = replay9e.load_panel(required_fields)
    replay9e.add_labels(panel)
    panel["split_group"] = panel["split"].map(replay9e.SPLIT_MAP).fillna(panel["split"])
    mask = replay9e.sample_mask(panel)
    label_columns = [replay9e.label_col(label, h) for label in LABELS for h in HORIZONS]
    sampled = panel.loc[mask, ["symbol", "timestamp", "split", "split_group"] + label_columns].copy()
    sample_positions = np.flatnonzero(mask)
    evaluator = replay9e.CachedCryptoFeatureAlgebra(
        panel,
        allowed_fields=required_fields | {"trade_close", "realized_vol_168h", "liquidity_tier_static"},
    )

    rows: list[dict[str, Any]] = []
    eval_errors = 0
    for cand in packet.to_dict("records"):
        try:
            signal = evaluator.evaluate(str(cand["expression"])).values.to_numpy(dtype=float)
        except Exception as exc:
            eval_errors += 1
            rows.append({"candidate_id": cand["candidate_id"], "status": "eval_error", "error": str(exc)})
            continue

        orient = 1.0 if float(cand["orientation_corr"]) >= 0 else -1.0
        signal_oriented = signal * orient
        replay_frame = sampled.copy()
        replay_frame["signal"] = signal_oriented[sample_positions]
        replay_frame["wrong_lag_future"] = (
            pd.Series(signal).groupby(panel["symbol"], sort=False).shift(-1).to_numpy(dtype=float)[sample_positions] * orient
        )
        replay_frame["wrong_lag_stale"] = (
            pd.Series(signal).groupby(panel["symbol"], sort=False).shift(1).to_numpy(dtype=float)[sample_positions] * orient
        )
        replay_frame["time_shuffle"] = np.roll(signal_oriented[sample_positions], 97 % len(sample_positions))
        replay_frame["symbol_shuffle"] = symbol_shuffle(signal_oriented[sample_positions], replay_frame)

        placebo_expr = placebo_map.get(str(cand["candidate_id"]))
        if placebo_expr:
            try:
                placebo_signal = evaluator.evaluate(placebo_expr).values.to_numpy(dtype=float) * orient
                replay_frame["same_family_placebo"] = placebo_signal[sample_positions]
            except Exception:
                replay_frame["same_family_placebo"] = np.nan

        ycol = replay9e.label_col(str(cand["label_id"]), int(cand["horizon"]))
        for split_name in ["train", "validation", "recent"]:
            split_frame = replay_frame[replay_frame["split_group"].eq(split_name)]
            stats = replay_control_stats(split_frame, ycol)
            original = stats["original"]
            control_spreads = [
                abs(v["spread"])
                for k, v in stats.items()
                if k != "original" and np.isfinite(v.get("spread", math.nan))
            ]
            max_control = max(control_spreads) if control_spreads else 0.0
            orig_score = abs(original["spread"]) if np.isfinite(original["spread"]) else 0.0
            control_ratio = max_control / max(orig_score, 1e-12)
            for cost in COST_BPS:
                cost_adjusted = original["spread"] - (2.0 * cost / 10000.0) if np.isfinite(original["spread"]) else math.nan
                rows.append(
                    {
                        "candidate_id": cand["candidate_id"],
                        "semantic_bucket": cand["semantic_bucket"],
                        "motif_bucket": cand["motif_bucket"],
                        "label_id": cand["label_id"],
                        "horizon": int(cand["horizon"]),
                        "split": split_name,
                        "cost_bps": cost,
                        "spread": original["spread"],
                        "cost_adjusted_spread": cost_adjusted,
                        "tstat": original["tstat"],
                        "hours": original["hours"],
                        "max_control_spread": max_control,
                        "control_ratio": control_ratio,
                        "wrong_lag_future_spread": stats.get("wrong_lag_future", {}).get("spread", math.nan),
                        "wrong_lag_stale_spread": stats.get("wrong_lag_stale", {}).get("spread", math.nan),
                        "time_shuffle_spread": stats.get("time_shuffle", {}).get("spread", math.nan),
                        "symbol_shuffle_spread": stats.get("symbol_shuffle", {}).get("spread", math.nan),
                        "same_family_placebo_spread": stats.get("same_family_placebo", {}).get("spread", math.nan),
                        "status": "ok",
                    }
                )

    result = pd.DataFrame(rows)
    ok = result[result["status"].eq("ok")].copy()
    clean_by_split = ok[
        ok["split"].isin(SPLITS_FOR_CLEAN)
        & ok["cost_bps"].eq(5)
        & pd.to_numeric(ok["cost_adjusted_spread"], errors="coerce").gt(0)
        & pd.to_numeric(ok["control_ratio"], errors="coerce").lt(1.0)
    ]
    clean_counts = clean_by_split.groupby("candidate_id")["split"].nunique()
    clean_candidates = set(clean_counts[clean_counts >= len(SPLITS_FOR_CLEAN)].index.astype(str))

    candidate_summary = (
        ok.groupby(["candidate_id", "semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            replay_rows=("candidate_id", "size"),
            validation_recent_clean_splits=("split", lambda s: int(clean_counts.get(str(s.name), 0)) if False else 0),
            median_spread=("spread", "median"),
            median_cost_adjusted_spread=("cost_adjusted_spread", "median"),
            max_tstat=("tstat", "max"),
            min_control_ratio=("control_ratio", "min"),
        )
        .reset_index()
    )
    clean_split_df = clean_counts.rename("validation_recent_clean_splits").reset_index()
    candidate_summary = candidate_summary.drop(columns=["validation_recent_clean_splits"]).merge(
        clean_split_df, on="candidate_id", how="left"
    )
    candidate_summary["validation_recent_clean_splits"] = candidate_summary["validation_recent_clean_splits"].fillna(0).astype(int)
    candidate_summary["replay_clean"] = candidate_summary["candidate_id"].astype(str).isin(clean_candidates)
    candidate_summary = candidate_summary.sort_values(["replay_clean", "max_tstat"], ascending=[False, False])

    family_summary = (
        ok.groupby(["semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            candidate_count=("candidate_id", "nunique"),
            median_cost_adjusted_spread=("cost_adjusted_spread", "median"),
            median_control_ratio=("control_ratio", "median"),
        )
        .reset_index()
    )
    clean_family = (
        candidate_summary[candidate_summary["replay_clean"]]
        .groupby(["semantic_bucket", "motif_bucket"], dropna=False)["candidate_id"]
        .nunique()
        .rename("clean_candidate_count")
        .reset_index()
    )
    family_summary = family_summary.merge(clean_family, on=["semantic_bucket", "motif_bucket"], how="left")
    family_summary["clean_candidate_count"] = family_summary["clean_candidate_count"].fillna(0).astype(int)
    family_summary = family_summary.sort_values(["clean_candidate_count", "candidate_count"], ascending=[False, False])

    clean_frame = candidate_summary[candidate_summary["replay_clean"]]
    clean_semantic = int(clean_frame["semantic_bucket"].nunique())
    clean_motif = int(clean_frame["motif_bucket"].nunique())
    decision = (
        "PASS_A7FFCORE14E_BOUNDED_REPLAY_CLEAN_CANDIDATES_READY_FOR_CORE15"
        if len(clean_candidates) >= 24 and clean_semantic >= 4 and clean_motif >= 4 and eval_errors == 0
        else "HOLD_A7FFCORE14E_BOUNDED_REPLAY_INSUFFICIENT"
    )
    blockers: list[str] = []
    if len(clean_candidates) < 24:
        blockers.append("clean_candidate_count_lt_24")
    if clean_semantic < 4:
        blockers.append("clean_semantic_bucket_count_lt_4")
    if clean_motif < 4:
        blockers.append("clean_motif_bucket_count_lt_4")
    if eval_errors:
        blockers.append("eval_errors_nonzero")

    result.to_csv(RUNTIME / "a7ffcore14e_replay_rows.csv", index=False)
    candidate_summary.to_csv(RUNTIME / "a7ffcore14e_candidate_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore14e_family_summary.csv", index=False)
    clean_frame[["candidate_id", "semantic_bucket", "motif_bucket", "validation_recent_clean_splits"]].to_csv(
        RUNTIME / "a7ffcore14e_replay_clean_candidates.csv", index=False
    )
    manifest = {
        "stage": "A7FF-CORE14E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE14",
        "source_decision": core14.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "candidate_count": int(packet.shape[0]),
        "eval_error_count": int(eval_errors),
        "sample_rows": int(sampled.shape[0]),
        "sample_timestamp_count": int(sampled["timestamp"].nunique()),
        "replay_rows": int(result.shape[0]),
        "replay_clean_candidate_count": int(len(clean_candidates)),
        "replay_clean_semantic_bucket_count": clean_semantic,
        "replay_clean_motif_bucket_count": clean_motif,
        "controls": ["wrong_lag_future", "wrong_lag_stale", "time_shuffle", "symbol_shuffle", "same_family_placebo"],
        "clean_rule": "validation and recent both positive at 5bps with max non-signflip control_ratio < 1.0",
        "executes_replay": True,
        "executes_search": False,
        "authorizes_core15_contract": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE15 replay-clean consolidation / search-readiness audit" if decision.startswith("PASS_") else "A7FF-CORE14R replay failure forensic",
    }
    write_json(RUNTIME / "a7ffcore14e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE14E executes bounded replay over the CORE14 128-candidate packet. It does not execute formula search, large search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Candidate Summary",
        "",
        md_table(candidate_summary, max_rows=100),
        "",
        "## Boundary",
        "",
        "```text",
        "bounded replay: true",
        "formula search / large search: false",
        "promotion: false",
        "alpha proof / shadow / paper / live: false",
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
