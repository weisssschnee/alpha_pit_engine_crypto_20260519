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
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7ab4_materialization_preflight import A7AB4Evaluator, load_numeric_fields, shift_matrix  # noqa: E402
from scripts.crypto_a7ab6_small_numeric_replay_preflight import (  # noqa: E402
    CONTROL_VARIANTS,
    PRE_MAY_SPLITS,
    label_matrix,
    nonoverlap_tstats,
    split_for_timestamps,
    tstat,
    variant_signals,
)
from scripts.crypto_a7al2l_fast_derived_replay_preflight import SPLIT_ORDER  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ab8_clue_forensic_execution"
REPORT = REPO / "reports" / "CRYPTO_A7AB8_CLUE_FORENSIC_EXECUTION_20260529.md"

A7AB7_MANIFEST = REPO / "runtime" / "a7ab7_clue_forensic_contract" / "a7ab7_manifest.json"
A7AB7_CLUES = REPO / "runtime" / "a7ab7_clue_forensic_contract" / "a7ab7_clue_queue_input.csv"
A7AB7_DETAIL = REPO / "runtime" / "a7ab7_clue_forensic_contract" / "a7ab7_clue_candidate_detail.csv"

MIN_ACTIVE_SYMBOLS = 30
COST_BPS = [2, 5, 10]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
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


def split_pipe(value: Any) -> list[str]:
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]


def selected_fields(detail: pd.DataFrame) -> set[str]:
    fields = {"trade_close"}
    for text in detail["source_fields"].dropna().astype(str):
        fields.update(split_pipe(text))
    return fields


def spread_and_masks(signal: np.ndarray, label: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    valid = np.isfinite(signal) & np.isfinite(label)
    valid_counts = valid.sum(axis=0)
    enough = valid_counts >= MIN_ACTIVE_SYMBOLS
    sig = np.where(valid, signal, np.nan)
    ranks = pd.DataFrame(sig).rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)
    top = valid & enough.reshape(1, -1) & (ranks >= 0.90)
    bottom = valid & enough.reshape(1, -1) & (ranks <= 0.10)
    top_count = top.sum(axis=0)
    bottom_count = bottom.sum(axis=0)
    spread = np.full(signal.shape[1], np.nan)
    ok = (top_count > 0) & (bottom_count > 0)
    spread[ok] = (
        np.where(top, label, 0.0).sum(axis=0)[ok] / top_count[ok]
        - np.where(bottom, label, 0.0).sum(axis=0)[ok] / bottom_count[ok]
    )
    active = top | bottom
    return spread, valid_counts, top, bottom


def turnover_proxy(top: np.ndarray, bottom: np.ndarray) -> float:
    book = top.astype(np.int8) - bottom.astype(np.int8)
    prev = shift_matrix(book.astype(np.float64), 1)
    change = np.abs(book.astype(np.float64) - prev)
    with np.errstate(invalid="ignore"):
        active = np.abs(book).sum(axis=0)
        changed = np.nansum(change, axis=0)
        turnover = changed / np.maximum(active, 1)
    finite = turnover[np.isfinite(turnover)]
    return float(np.nanmean(finite)) if len(finite) else np.nan


def contribution_concentration(
    label: np.ndarray,
    top: np.ndarray,
    bottom: np.ndarray,
    timestamps: pd.DatetimeIndex,
    split: np.ndarray,
    symbols: list[str],
) -> tuple[float, str, float, str]:
    top_count = np.maximum(top.sum(axis=0), 1)
    bottom_count = np.maximum(bottom.sum(axis=0), 1)
    contrib = np.where(top, label / top_count.reshape(1, -1), 0.0) - np.where(
        bottom, label / bottom_count.reshape(1, -1), 0.0
    )
    mask = np.isin(split, PRE_MAY_SPLITS)
    abs_contrib = np.abs(contrib[:, mask])
    by_symbol = abs_contrib.sum(axis=1)
    total = float(by_symbol.sum())
    if total > 0:
        top_idx = int(np.nanargmax(by_symbol))
        top_symbol_share = float(by_symbol[top_idx] / total)
        top_symbol = symbols[top_idx]
    else:
        top_symbol_share = np.nan
        top_symbol = ""
    months = pd.Series(timestamps[mask]).dt.strftime("%Y-%m").to_numpy()
    by_month: dict[str, float] = {}
    for i, month in enumerate(months):
        by_month[month] = by_month.get(month, 0.0) + float(np.nansum(abs_contrib[:, i]))
    if by_month and sum(by_month.values()) > 0:
        top_month, top_value = max(by_month.items(), key=lambda item: item[1])
        top_month_share = float(top_value / sum(by_month.values()))
    else:
        top_month = ""
        top_month_share = np.nan
    return top_symbol_share, top_symbol, top_month_share, top_month


def summarize_split_metrics(
    candidate_id: str,
    label_family: str,
    horizon: int,
    variant: str,
    spread: np.ndarray,
    valid_counts: np.ndarray,
    split: np.ndarray,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split_name in SPLIT_ORDER:
        mask = (split == split_name) & np.isfinite(spread)
        x = spread[mask]
        med_t, min_t = nonoverlap_tstats(spread, split == split_name, horizon=horizon)
        rows.append(
            {
                "candidate_id": candidate_id,
                "label_family": label_family,
                "horizon_h": horizon,
                "variant": variant,
                "split": split_name,
                "n_dates": int(mask.sum()),
                "avg_n_obs": float(np.nanmean(valid_counts[mask])) if mask.any() else np.nan,
                "mean_spread": float(np.nanmean(x)) if len(x) else np.nan,
                "spread_tstat": tstat(x) if len(x) else np.nan,
                "nonoverlap_median_tstat": med_t,
                "nonoverlap_min_tstat": min_t,
                "positive_rate": float(np.nanmean(x > 0)) if len(x) else np.nan,
            }
        )
    return rows


def classify_forensic(metrics: pd.DataFrame, row: dict[str, Any]) -> dict[str, Any]:
    cid = str(row["candidate_id"])
    label_family = str(row["label_family"])
    horizon = int(row["horizon_h"])
    sub = metrics[
        metrics["candidate_id"].eq(cid)
        & metrics["label_family"].eq(label_family)
        & metrics["horizon_h"].eq(horizon)
    ]
    pivot = sub.pivot_table(index="variant", columns="split", values="mean_spread", aggfunc="first")

    def v(variant: str, split_name: str) -> float:
        try:
            return float(pivot.loc[variant, split_name])
        except Exception:
            return np.nan

    orientation = float(row.get("orientation_from_train", 1.0))
    premay = [orientation * v("original", s) for s in PRE_MAY_SPLITS]
    premay_ok = all(np.isfinite(x) and x > 0 for x in premay)
    recent = orientation * v("original", "recent_oos_2026JanApr")
    lag_recent = orientation * v("one_bar_lag", "recent_oos_2026JanApr")
    lag_ok = np.isfinite(recent) and np.isfinite(lag_recent) and lag_recent > 0 and abs(lag_recent) >= 0.25 * abs(recent)
    ratios: list[float] = []
    warning_ratio = False
    for split_name in PRE_MAY_SPLITS:
        original_abs = abs(v("original", split_name))
        vals = [abs(v(control, split_name)) for control in CONTROL_VARIANTS if control != "one_bar_lag"]
        vals = [x for x in vals if np.isfinite(x)]
        if vals and np.isfinite(original_abs) and original_abs > 1e-12:
            ratio = max(vals) / original_abs
            ratios.append(ratio)
            warning_ratio = warning_ratio or ratio >= 0.80
    control_ratio = max(ratios) if ratios else np.nan
    hard_control_clean = np.isfinite(control_ratio) and control_ratio < 1.0
    cost_turnover = float(row.get("turnover_proxy", np.nan))
    cost10_recent = recent - (10.0 / 10000.0) * cost_turnover if np.isfinite(recent) and np.isfinite(cost_turnover) else np.nan
    cost10_ok = np.isfinite(cost10_recent) and cost10_recent > 0
    top_symbol_share = float(row.get("top_symbol_abs_contribution_share", np.nan))
    top_month_share = float(row.get("top_month_abs_contribution_share", np.nan))
    concentration_ok = (
        np.isfinite(top_symbol_share)
        and np.isfinite(top_month_share)
        and top_symbol_share <= 0.35
        and top_month_share <= 0.35
    )
    if not premay_ok:
        decision = "HOLD_A7AB8_FULL_WINDOW_PREMAY_UNSTABLE"
    elif not lag_ok:
        decision = "HOLD_A7AB8_LAG_FRAGILE"
    elif not hard_control_clean:
        decision = "HOLD_A7AB8_CONTROL_DOMINATED"
    elif not cost10_ok:
        decision = "HOLD_A7AB8_COST_FRAGILE"
    elif not concentration_ok:
        decision = "HOLD_A7AB8_CONCENTRATED"
    else:
        decision = "A7AB8_FORENSIC_SURVIVOR"
    return {
        "candidate_id": cid,
        "label_family": label_family,
        "horizon_h": horizon,
        "orientation_from_train": orientation,
        "oriented_validation_spread": premay[0],
        "oriented_test_spread": premay[1],
        "oriented_recent_spread": recent,
        "one_bar_lag_recent_oriented": lag_recent,
        "control_ratio_premay_max": control_ratio,
        "control_ratio_warning_ge_0_80": warning_ratio,
        "turnover_proxy": cost_turnover,
        "cost10_recent_oriented": cost10_recent,
        "top_symbol_abs_contribution_share": top_symbol_share,
        "top_symbol": row.get("top_symbol", ""),
        "top_month_abs_contribution_share": top_month_share,
        "top_month": row.get("top_month", ""),
        "decision": decision,
    }


def greedy_corr_clusters(spreads: pd.DataFrame, threshold: float = 0.80) -> pd.DataFrame:
    if spreads.empty:
        return pd.DataFrame()
    ids = spreads["clue_key"].tolist()
    matrix = np.vstack(spreads["spread_vector"].to_list())
    corr = np.corrcoef(np.nan_to_num(matrix, nan=0.0))
    assigned: dict[str, int] = {}
    cluster_id = 0
    for i, clue_id in enumerate(ids):
        if clue_id in assigned:
            continue
        assigned[clue_id] = cluster_id
        for j in range(i + 1, len(ids)):
            if ids[j] not in assigned and np.isfinite(corr[i, j]) and abs(corr[i, j]) >= threshold:
                assigned[ids[j]] = cluster_id
        cluster_id += 1
    return pd.DataFrame([{"clue_key": key, "return_corr_cluster": value} for key, value in assigned.items()])


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ab7 = read_json(A7AB7_MANIFEST)
    if not a7ab7.get("authorizes_a7ab8_clue_forensic_execution"):
        raise SystemExit("A7AB-7 does not authorize A7AB-8")
    clues = pd.read_csv(A7AB7_CLUES)
    detail = pd.read_csv(A7AB7_DETAIL).drop_duplicates("candidate_id")
    fields = selected_fields(detail)
    loaded_symbols, timestamps, numeric, missing, full_timestamp_count = load_numeric_fields(fields, timestamp_cap=None)
    if missing:
        raise SystemExit(f"missing fields: {missing}")
    split = split_for_timestamps(timestamps)
    evaluator = A7AB4Evaluator(numeric, {})
    rng = np.random.default_rng(20260529)

    signal_cache: dict[str, np.ndarray] = {}
    metric_rows: list[dict[str, Any]] = []
    clue_augmented: list[dict[str, Any]] = []
    spread_vectors: list[dict[str, Any]] = []
    for idx, clue in enumerate(clues.to_dict("records"), start=1):
        cid = str(clue["candidate_id"])
        label_family = str(clue["label_family"])
        horizon = int(clue["horizon_h"])
        info = detail.loc[detail["candidate_id"].astype(str).eq(cid)].iloc[0].to_dict()
        expression = str(info["expression"])
        if cid not in signal_cache:
            signal_cache[cid] = evaluator.eval(expression)
        base_signal = signal_cache[cid]
        label = label_matrix(label_family, horizon, numeric["trade_close"], timestamps, split)
        variants = variant_signals(base_signal, rng)
        original_spread, valid_counts, top, bottom = spread_and_masks(base_signal, label)
        turnover = turnover_proxy(top, bottom)
        top_symbol_share, top_symbol, top_month_share, top_month = contribution_concentration(
            label, top, bottom, timestamps, split, loaded_symbols
        )
        clue_key = f"{cid}|{label_family}|{horizon}"
        spread_vectors.append({"clue_key": clue_key, "spread_vector": original_spread})
        augmented = dict(clue)
        augmented.update(
            {
                "family_id": info["family_id"],
                "primary_seed_field": info["primary_seed_field"],
                "skeleton_key": info["skeleton_key"],
                "expression": expression,
                "turnover_proxy": turnover,
                "top_symbol_abs_contribution_share": top_symbol_share,
                "top_symbol": top_symbol,
                "top_month_abs_contribution_share": top_month_share,
                "top_month": top_month,
                "clue_key": clue_key,
            }
        )
        clue_augmented.append(augmented)
        for variant, signal in variants.items():
            spread, counts, _top, _bottom = spread_and_masks(signal, label)
            metric_rows.extend(summarize_split_metrics(cid, label_family, horizon, variant, spread, counts, split))
        if idx % 8 == 0:
            print(f"[A7AB-8] forensic {idx}/{len(clues)}", flush=True)

    metrics = pd.DataFrame(metric_rows)
    clue_aug = pd.DataFrame(clue_augmented)
    decisions = pd.DataFrame([classify_forensic(metrics, row) for row in clue_aug.to_dict("records")])
    clusters = greedy_corr_clusters(pd.DataFrame(spread_vectors))
    decisions["clue_key"] = decisions["candidate_id"] + "|" + decisions["label_family"] + "|" + decisions["horizon_h"].astype(str)
    decisions = decisions.merge(clusters, on="clue_key", how="left")
    clue_aug = clue_aug.merge(clusters, on="clue_key", how="left")

    decision_counts = decisions["decision"].value_counts().rename_axis("decision").reset_index(name="count")
    survivors = decisions[decisions["decision"].eq("A7AB8_FORENSIC_SURVIVOR")].copy()
    cluster_summary = (
        decisions.groupby("return_corr_cluster", as_index=False).agg(
            clue_rows=("clue_key", "count"),
            survivor_rows=("decision", lambda x: int((x == "A7AB8_FORENSIC_SURVIVOR").sum())),
            candidate_count=("candidate_id", "nunique"),
        )
        if "return_corr_cluster" in decisions
        else pd.DataFrame()
    )
    survivor_count = int(len(survivors))
    survivor_candidate_count = int(survivors["candidate_id"].nunique()) if survivor_count else 0
    decision = (
        "PASS_A7AB8_FORENSIC_SURVIVORS_FOUND_EXECUTION_HOLD"
        if survivor_count > 0
        else "HOLD_A7AB8_NO_FORENSIC_SURVIVORS"
    )
    manifest = {
        "stage": "A7AB-8",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_clue_forensic": True,
        "executes_formula_generation": False,
        "executes_large_search": False,
        "executes_training": False,
        "uses_may": False,
        "input_clue_rows": int(len(clues)),
        "input_clue_candidates": int(clues["candidate_id"].nunique()),
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "full_timestamps_before_subset": int(full_timestamp_count),
        "metric_rows": int(len(metrics)),
        "decision_counts": {str(r["decision"]): int(r["count"]) for _, r in decision_counts.iterrows()},
        "forensic_survivor_rows": survivor_count,
        "forensic_survivor_candidates": survivor_candidate_count,
        "return_corr_cluster_count": int(decisions["return_corr_cluster"].nunique()) if not decisions.empty else 0,
        "authorizes_a7ab9_survivor_freeze_contract": bool(survivor_count > 0),
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    metrics.to_csv(RUNTIME / "a7ab8_full_window_variant_metrics.csv", index=False)
    clue_aug.to_csv(RUNTIME / "a7ab8_clue_augmented.csv", index=False)
    decisions.to_csv(RUNTIME / "a7ab8_forensic_decisions.csv", index=False)
    survivors.to_csv(RUNTIME / "a7ab8_forensic_survivors.csv", index=False)
    clusters.to_csv(RUNTIME / "a7ab8_return_corr_clusters.csv", index=False)
    cluster_summary.to_csv(RUNTIME / "a7ab8_return_corr_cluster_summary.csv", index=False)
    decision_counts.to_csv(RUNTIME / "a7ab8_decision_counts.csv", index=False)
    write_json(RUNTIME / "a7ab8_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ab8_authorization_matrix.json",
        {
            "A7AB-8": {"status": decision},
            "A7AB-9_survivor_freeze_contract": {"authorized": bool(survivor_count > 0)},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AB-8 CLUE FORENSIC EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AB-8 runs full-window forensic checks on A7AB-6 clues. It does not authorize formula search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Decision Counts",
        "",
        md_table(decision_counts),
        "",
        "## Forensic Survivors",
        "",
        md_table(survivors, 80),
        "",
        "## Return-Corr Cluster Summary",
        "",
        md_table(cluster_summary),
        "",
        "## Decision Sample",
        "",
        md_table(decisions.head(80)),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
