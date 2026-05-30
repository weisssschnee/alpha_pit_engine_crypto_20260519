from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7aa1_primitive_response_map import horizon_label, label_family_matrix  # noqa: E402
from scripts.crypto_a7ab4_materialization_preflight import A7AB4Evaluator  # noqa: E402
from scripts.crypto_a7al2l_fast_derived_replay_preflight import split_for_timestamps  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import (  # noqa: E402
    BASE_DIR,
    LATENT_PANEL,
    load_base,
    load_group_fields,
    load_latent_numeric,
    parquet_schema,
)
from scripts.crypto_a7al2z4_broader_non_oi_numeric_replay_preflight import smoke_column_indices, tstat  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ff31_portfolio_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FF31_PORTFOLIO_FORENSIC_20260530.md"
A7FF30A = REPO / "runtime" / "a7ff30a_portfolio_replay_smoke"
A7FF30 = REPO / "runtime" / "a7ff30_portfolio_replay_contract"
SPLIT_COVERAGE = REPO / "runtime" / "a7al0_top498_alpha_search_contract" / "a7al_split_coverage_by_symbol.csv"

FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
OPERATORS = {
    "Mean",
    "Delta",
    "TSRank",
    "Decay",
    "Rank",
    "CSRank",
    "ZScore",
    "Mul",
    "Sub",
    "Add",
    "Neg",
    "Abs",
    "Sign",
    "SafeDiv",
    "Clip",
    "Winsor",
}
SELECTED_LABELS = [
    ("L5_vol_adjusted_return", 8),
    ("L1_cross_sectional_relative_return", 8),
    ("L0_raw_forward_return", 8),
    ("L3_liquidity_tier_relative_return", 8),
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


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
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def expression_fields(expression: str) -> set[str]:
    out: set[str] = set()
    for token in FIELD_RE.findall(str(expression)):
        if token in OPERATORS or token in {"nan", "inf"}:
            continue
        out.add(token)
    return out


def expression_operators(expression: str) -> list[str]:
    return [token for token in FIELD_RE.findall(str(expression)) if token in OPERATORS]


def strict_symbols_full() -> list[str]:
    cov = pd.read_csv(SPLIT_COVERAGE)
    return (
        cov.loc[cov["search_eligibility"].eq("strict_full_history"), "symbol"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )


def rank_signal(signal: np.ndarray) -> np.ndarray:
    ranks = pd.DataFrame(signal).rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)
    return (ranks - 0.5) * 2.0


def top_bottom_spread_and_contrib(
    score: np.ndarray,
    label: np.ndarray,
    symbols: list[str],
    timestamps: pd.DatetimeIndex,
    split: np.ndarray,
    split_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    valid = np.isfinite(score) & np.isfinite(label)
    ranks = pd.DataFrame(np.where(valid, score, np.nan)).rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)
    enough = valid.sum(axis=0) >= 20
    top = valid & enough.reshape(1, -1) & (ranks >= 0.90)
    bottom = valid & enough.reshape(1, -1) & (ranks <= 0.10)
    mask_t = split == split_name
    sym_rows: list[dict[str, Any]] = []
    for i, symbol in enumerate(symbols):
        top_vals = label[i, mask_t] * top[i, mask_t]
        bottom_vals = label[i, mask_t] * bottom[i, mask_t]
        top_count = int(top[i, mask_t].sum())
        bottom_count = int(bottom[i, mask_t].sum())
        if top_count + bottom_count == 0:
            continue
        sym_rows.append(
            {
                "symbol": symbol,
                "split": split_name,
                "top_count": top_count,
                "bottom_count": bottom_count,
                "top_label_sum": float(np.nansum(top_vals)),
                "bottom_label_sum": float(np.nansum(bottom_vals)),
                "net_label_sum": float(np.nansum(top_vals) - np.nansum(bottom_vals)),
                "abs_label_sum": float(abs(np.nansum(top_vals)) + abs(np.nansum(bottom_vals))),
            }
        )
    sym_df = pd.DataFrame(sym_rows)
    if not sym_df.empty:
        total_abs = sym_df["abs_label_sum"].sum()
        sym_df["abs_contribution_share"] = sym_df["abs_label_sum"] / total_abs if total_abs else np.nan
        sym_df = sym_df.sort_values("abs_contribution_share", ascending=False)

    spreads: list[dict[str, Any]] = []
    months = pd.Series(timestamps[mask_t]).dt.strftime("%Y-%m").to_numpy()
    top_counts = top[:, mask_t].sum(axis=0)
    bottom_counts = bottom[:, mask_t].sum(axis=0)
    top_sum = np.where(top[:, mask_t], label[:, mask_t], 0.0).sum(axis=0)
    bottom_sum = np.where(bottom[:, mask_t], label[:, mask_t], 0.0).sum(axis=0)
    ok = (top_counts > 0) & (bottom_counts > 0)
    hourly = np.full(len(months), np.nan)
    hourly[ok] = (top_sum[ok] / top_counts[ok]) - (bottom_sum[ok] / bottom_counts[ok])
    for month in sorted(set(months)):
        m = months == month
        x = hourly[m]
        spreads.append(
            {
                "month": month,
                "split": split_name,
                "hour_count": int(np.isfinite(x).sum()),
                "mean_spread": float(np.nanmean(x)) if np.isfinite(x).any() else np.nan,
                "tstat": tstat(x),
                "positive_rate": float(np.nanmean(x[np.isfinite(x)] > 0)) if np.isfinite(x).any() else np.nan,
            }
        )
    return sym_df, pd.DataFrame(spreads)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    prior = read_json(A7FF30A / "a7ff30a_manifest.json")
    if not prior.get("authorizes_a7ff31_portfolio_forensic_contract"):
        raise SystemExit("A7FF-30A does not authorize A7FF-31")

    queue = read_csv(A7FF30 / "a7ff30_frozen_portfolio_replay_queue.csv")
    selected_clues = read_csv(A7FF30A / "a7ff30a_selected_ensemble_clues.csv")
    loo = read_csv(A7FF30A / "a7ff30a_leave_one_out_metrics.csv")

    fields = {"trade_close", "realized_vol_168h", "realized_vol_24h"}
    for expression in queue["expression"].astype(str):
        fields.update(expression_fields(expression))
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    base_fields = {x for x in fields if x in base_schema}
    latent_fields = {x for x in fields if x in latent_schema and x not in base_fields}
    symbols = strict_symbols_full()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_fields))
    groups = load_group_fields(loaded_symbols, timestamps, {"liquidity_tier"})
    idx = smoke_column_indices(timestamps)
    timestamps = pd.DatetimeIndex(timestamps[idx])
    numeric = {key: value[:, idx] for key, value in numeric.items()}
    groups = {key: value[:, idx] for key, value in groups.items()}
    split = split_for_timestamps(timestamps)

    evaluator = A7AB4Evaluator(numeric, groups)
    response_lookup = read_csv(REPO / "runtime" / "a7ff28a_bounded_deep_replay" / "a7ff28a_label_response_metrics.csv")
    oriented: dict[str, np.ndarray] = {}
    review_rows: list[dict[str, Any]] = []
    for _, row in queue.iterrows():
        cid = row["blueprint_id"]
        signal = evaluator.eval(row["expression"])
        best = response_lookup[
            response_lookup["blueprint_id"].eq(cid)
            & response_lookup["label_family"].eq(row["best_label_family"])
            & response_lookup["label_horizon_h"].eq(int(row["best_label_horizon_h"]))
        ].head(1)
        orientation = float(best["orientation_from_train"].iloc[0]) if not best.empty else 1.0
        oriented[cid] = rank_signal(signal * orientation)
        review_rows.append(
            {
                "factor_id": cid,
                "name": f"{row['semantic_pair']}::{row['motif']}",
                "formula": row["expression"],
                "provenance": "generated_by_A7FF_24R_then_filtered_by_A7FF28A_A7FF29",
                "operator_path": "|".join(expression_operators(str(row["expression"]))),
                "raw_fields": "|".join(sorted(expression_fields(str(row["expression"])))),
                "feature_family": row["semantic_pair"],
                "nearest_known_family": "basis_premium_root",
                "overlap_assessment": "high_family_overlap",
                "family_diversity_impact": "reduces_breadth_because_all_candidates_keep_basis_premium_root",
                "cluster_coverage": row.get("skeleton_key", ""),
                "keep_list_decision": "HOLD_RESEARCH",
                "required_next_action": "portfolio_forensic_and_outlier_winsorized_replay_before_any_keep_review",
            }
        )
    review = pd.DataFrame(review_rows)
    review.to_csv(RUNTIME / "a7ff31_candidate_factor_review.csv", index=False)

    ids = list(oriented)
    corr_rows: list[dict[str, Any]] = []
    for i, left in enumerate(ids):
        for right in ids[i + 1 :]:
            x = oriented[left].reshape(-1)
            y = oriented[right].reshape(-1)
            m = np.isfinite(x) & np.isfinite(y)
            corr = float(np.corrcoef(x[m], y[m])[0, 1]) if m.sum() >= 10 else np.nan
            corr_rows.append({"left": left, "right": right, "pairwise_corr": corr})
    corr = pd.DataFrame(corr_rows)
    corr.to_csv(RUNTIME / "a7ff31_candidate_signal_correlation.csv", index=False)

    ensemble = np.nanmean(np.stack(list(oriented.values()), axis=0), axis=0)
    raw_8 = horizon_label(numeric["trade_close"], timestamps, split, 8)
    vol = numeric.get("realized_vol_168h")
    liquidity = groups.get("liquidity_tier")
    forensic_label = label_family_matrix(raw_8, "L5_vol_adjusted_return", vol, liquidity)
    sym_recent, month_recent = top_bottom_spread_and_contrib(
        ensemble,
        forensic_label,
        loaded_symbols,
        timestamps,
        split,
        "recent_oos_2026JanApr",
    )
    sym_recent.to_csv(RUNTIME / "a7ff31_recent_symbol_contribution.csv", index=False)
    month_recent.to_csv(RUNTIME / "a7ff31_recent_month_contribution.csv", index=False)

    if not loo.empty:
        loo_focus = loo[
            loo["label_family"].eq("L5_vol_adjusted_return")
            & pd.to_numeric(loo["label_horizon_h"], errors="coerce").eq(8)
        ].copy()
    else:
        loo_focus = pd.DataFrame()
    loo_focus.to_csv(RUNTIME / "a7ff31_leave_one_out_focus.csv", index=False)

    top_symbol_share = float(sym_recent["abs_contribution_share"].max()) if not sym_recent.empty else None
    max_corr = float(corr["pairwise_corr"].abs().max()) if not corr.empty else None
    mean_abs_corr = float(corr["pairwise_corr"].abs().mean()) if not corr.empty else None
    positive_month_rate = float((month_recent["mean_spread"] > 0).mean()) if not month_recent.empty else None
    warnings = list(prior.get("warnings", []))
    if max_corr is not None and max_corr > 0.80:
        warnings.append("candidate_pairwise_corr_gt_0_80")
    if mean_abs_corr is not None and mean_abs_corr > 0.60:
        warnings.append("candidate_mean_abs_corr_gt_0_60")
    if top_symbol_share is not None and top_symbol_share > 0.20:
        warnings.append("top_symbol_contribution_share_gt_0_20")
    if positive_month_rate is not None and positive_month_rate < 0.60:
        warnings.append("recent_month_positive_rate_lt_0_60")
    warnings.append("basis_premium_root_concentration_requires_family_diversification_before_search")

    decision = "HOLD_A7FF31_PORTFOLIO_FORENSIC_CONCENTRATED_CLUE_NO_SEARCH_AUTH"
    manifest = {
        "stage": "A7FF-31",
        "generated_at": now_utc(),
        "decision": decision,
        "candidate_count": int(len(queue)),
        "selected_ensemble_clue_rows": int(len(selected_clues)),
        "max_pairwise_corr_abs": max_corr,
        "mean_pairwise_corr_abs": mean_abs_corr,
        "top_symbol_contribution_share": top_symbol_share,
        "recent_month_positive_rate": positive_month_rate,
        "warnings": warnings,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_a7ff24r2_queue_repair": True,
        "authorizes_a7ff32_family_diversification_contract": True,
    }
    write_json(RUNTIME / "a7ff31_manifest.json", manifest)
    write_json(RUNTIME / "a7ff31_decision_record.json", manifest)

    lines = [
        "# CRYPTO A7FF-31 PORTFOLIO FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-31 reviews the A7FF-30A ensemble clues as candidate factors. The result remains a concentrated research clue, not alpha proof.",
        "",
        "## Experiment Record",
        "",
        "```text",
        "experiment_id: 20260530_a7ff31_portfolio_forensic",
        "objective: determine whether A7FF-30A ensemble clues are diversified enough for expansion",
        "inputs: A7FF-30A outputs, A7FF-30 frozen queue, strict_full_history universe",
        "parameters: no generation, no search, candidate factor review, pairwise signal corr, symbol/month contribution",
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Candidate Factor Review",
        "",
        md_table(review, 20),
        "",
        "## Signal Correlation",
        "",
        md_table(corr.sort_values("pairwise_corr", key=lambda s: s.abs(), ascending=False), 40),
        "",
        "## Recent Symbol Contribution",
        "",
        md_table(sym_recent.head(30), 30),
        "",
        "## Recent Month Contribution",
        "",
        md_table(month_recent, 40),
        "",
        "## Leave-One-Out Focus",
        "",
        md_table(loo_focus, 40),
        "",
        "## Boundary",
        "",
        "```text",
        "A7FF-31 explicitly holds the current portfolio clue as concentrated.",
        "It authorizes only queue repair/family diversification contracts, not formula search or promotion.",
        "No alpha proof, shadow, paper, or live execution is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
