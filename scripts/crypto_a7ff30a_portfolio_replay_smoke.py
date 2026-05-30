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

from scripts.crypto_a7aa1_primitive_response_map import horizon_label, label_family_matrix, summarize_spread  # noqa: E402
from scripts.crypto_a7ab4_materialization_preflight import A7AB4Evaluator  # noqa: E402
from scripts.crypto_a7al2l_fast_derived_replay_preflight import SPLIT_ORDER, split_for_timestamps  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import (  # noqa: E402
    BASE_DIR,
    LATENT_PANEL,
    load_base,
    load_group_fields,
    load_latent_numeric,
    parquet_schema,
)
from scripts.crypto_a7al2z4_broader_non_oi_numeric_replay_preflight import smoke_column_indices, spread_series  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ff30a_portfolio_replay_smoke"
REPORT = REPO / "reports" / "CRYPTO_A7FF30A_PORTFOLIO_REPLAY_SMOKE_20260530.md"
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
LABELS = [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return",
]
HORIZONS = [1, 4, 8, 24]
PREMAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]


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
    fields: set[str] = set()
    for token in FIELD_RE.findall(str(expression)):
        if token in OPERATORS or token in {"nan", "inf"}:
            continue
        fields.add(token)
    return fields


def strict_symbols_full() -> list[str]:
    cov = pd.read_csv(SPLIT_COVERAGE)
    symbols = (
        cov.loc[cov["search_eligibility"].eq("strict_full_history"), "symbol"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )
    return symbols


def rank_signal(signal: np.ndarray) -> np.ndarray:
    ranks = pd.DataFrame(signal).rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)
    return (ranks - 0.5) * 2.0


def split_oriented(summary: dict[str, Any], split_name: str, orientation: float) -> float:
    value = summary.get(f"{split_name}_mean_spread", np.nan)
    return orientation * float(value) if np.isfinite(value) else np.nan


def cost_fields(recent_oriented: float) -> dict[str, float]:
    return {
        "cost2_recent_oriented": recent_oriented - (2 * 2 / 10000) if np.isfinite(recent_oriented) else np.nan,
        "cost5_recent_oriented": recent_oriented - (2 * 5 / 10000) if np.isfinite(recent_oriented) else np.nan,
        "cost10_recent_oriented": recent_oriented - (2 * 10 / 10000) if np.isfinite(recent_oriented) else np.nan,
    }


def evaluate_portfolio(name: str, signal: np.ndarray, label: np.ndarray, split: np.ndarray, label_family: str, horizon: int) -> dict[str, Any]:
    spread, valid_counts = spread_series(signal, label)
    summary = summarize_spread(spread, split, horizon)
    train = summary.get("train_2024_mean_spread", np.nan)
    orientation = 1.0 if not np.isfinite(train) or train >= 0 else -1.0
    premay = {s: split_oriented(summary, s, orientation) for s in PREMAY_SPLITS}
    recent = premay["recent_oos_2026JanApr"]
    payload = {
        "portfolio_name": name,
        "label_family": label_family,
        "label_horizon_h": horizon,
        "orientation_from_train": orientation,
        "premay_positive_split_count": int(sum(np.isfinite(v) and v > 0 for v in premay.values())),
        "premay_all_positive": bool(all(np.isfinite(v) and v > 0 for v in premay.values())),
        "avg_active_symbols_recent": float(np.nanmean(valid_counts[split == "recent_oos_2026JanApr"])) if np.any(split == "recent_oos_2026JanApr") else np.nan,
        **cost_fields(recent),
    }
    for key, value in summary.items():
        payload[key] = value
    return payload


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    contract = read_json(A7FF30 / "a7ff30_manifest.json")
    if not contract.get("authorizes_a7ff30a_portfolio_replay_smoke"):
        raise SystemExit("A7FF-30 does not authorize A7FF-30A")

    queue = read_csv(A7FF30 / "a7ff30_frozen_portfolio_replay_queue.csv")
    if queue.empty:
        raise SystemExit("empty A7FF-30 queue")

    fields = {"trade_close", "realized_vol_168h", "realized_vol_24h"}
    for expression in queue["expression"].astype(str):
        fields.update(expression_fields(expression))
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    base_fields = {x for x in fields if x in base_schema}
    latent_fields = {x for x in fields if x in latent_schema and x not in base_fields}
    missing_fields = sorted(fields - base_fields - latent_fields)

    symbols = strict_symbols_full()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_fields))
    groups = load_group_fields(loaded_symbols, timestamps, {"liquidity_tier"})
    full_timestamp_count = int(len(timestamps))
    idx = smoke_column_indices(timestamps)
    timestamps = pd.DatetimeIndex(timestamps[idx])
    numeric = {key: value[:, idx] for key, value in numeric.items()}
    groups = {key: value[:, idx] for key, value in groups.items()}
    split = split_for_timestamps(timestamps)

    raw_labels = {h: horizon_label(numeric["trade_close"], timestamps, split, h) for h in HORIZONS}
    vol = numeric.get("realized_vol_168h")
    liquidity_tier = groups.get("liquidity_tier")
    label_mats = {
        (label_family, horizon): label_family_matrix(raw, label_family, vol, liquidity_tier)
        for horizon, raw in raw_labels.items()
        for label_family in LABELS
    }
    evaluator = A7AB4Evaluator(numeric, groups)

    signal_rows: list[dict[str, Any]] = []
    oriented_ranked_signals: dict[str, np.ndarray] = {}
    response_lookup = read_csv(REPO / "runtime" / "a7ff28a_bounded_deep_replay" / "a7ff28a_label_response_metrics.csv")
    for _, row in queue.iterrows():
        cid = row["blueprint_id"]
        signal = evaluator.eval(row["expression"])
        best = response_lookup[
            response_lookup["blueprint_id"].eq(cid)
            & response_lookup["label_family"].eq(row["best_label_family"])
            & response_lookup["label_horizon_h"].eq(int(row["best_label_horizon_h"]))
        ].head(1)
        orientation = float(best["orientation_from_train"].iloc[0]) if not best.empty else 1.0
        oriented_ranked_signals[cid] = rank_signal(signal * orientation)
        signal_rows.append(
            {
                "blueprint_id": cid,
                "expression": row["expression"],
                "orientation_source_label": row["best_label_family"],
                "orientation_source_horizon": row["best_label_horizon_h"],
                "orientation": orientation,
                "finite_share": float(np.isfinite(signal).mean()),
                "nonzero_share": float((np.isfinite(signal) & (np.abs(signal) > 1e-12)).mean()),
            }
        )
    pd.DataFrame(signal_rows).to_csv(RUNTIME / "a7ff30a_signal_materialization.csv", index=False)

    stacked = np.stack(list(oriented_ranked_signals.values()), axis=0)
    ensemble = np.nanmean(stacked, axis=0)
    portfolios: dict[str, np.ndarray] = {"ensemble_equal": ensemble}
    for cid, sig in oriented_ranked_signals.items():
        portfolios[f"single_{cid}"] = sig
        if len(oriented_ranked_signals) > 1:
            others = [v for k, v in oriented_ranked_signals.items() if k != cid]
            portfolios[f"leave_one_out_without_{cid}"] = np.nanmean(np.stack(others, axis=0), axis=0)

    rows: list[dict[str, Any]] = []
    for name, sig in portfolios.items():
        for (label_family, horizon), label in label_mats.items():
            rows.append(evaluate_portfolio(name, sig, label, split, label_family, horizon))
    metrics = pd.DataFrame(rows)
    metrics.to_csv(RUNTIME / "a7ff30a_portfolio_label_metrics.csv", index=False)

    ensemble_metrics = metrics[metrics["portfolio_name"].eq("ensemble_equal")].copy()
    ensemble_clues = ensemble_metrics[
        ensemble_metrics["premay_all_positive"].astype(bool)
        & (pd.to_numeric(ensemble_metrics["cost2_recent_oriented"], errors="coerce") > 0)
    ].copy()
    ensemble_clues.to_csv(RUNTIME / "a7ff30a_ensemble_clue_metrics.csv", index=False)

    loo = metrics[metrics["portfolio_name"].str.startswith("leave_one_out_without_")].copy()
    if not loo.empty:
        baseline = ensemble_metrics.set_index(["label_family", "label_horizon_h"])["recent_oos_2026JanApr_mean_spread"]
        deltas = []
        for _, row in loo.iterrows():
            key = (row["label_family"], row["label_horizon_h"])
            base = baseline.get(key, np.nan)
            deltas.append(row["recent_oos_2026JanApr_mean_spread"] - base if np.isfinite(base) else np.nan)
        loo["delta_recent_vs_ensemble"] = deltas
    loo.to_csv(RUNTIME / "a7ff30a_leave_one_out_metrics.csv", index=False)

    selected = ensemble_clues.sort_values(
        ["cost2_recent_oriented", "recent_oos_2026JanApr_tstat"],
        ascending=[False, False],
    )
    selected.to_csv(RUNTIME / "a7ff30a_selected_ensemble_clues.csv", index=False)

    concentration_rows = [
        {"axis": "candidate_count", "value": "ensemble_equal", "count": len(oriented_ranked_signals)}
    ]
    concentration_rows.extend(
        {"axis": "semantic_pair", "value": k, "count": int(v)}
        for k, v in queue["semantic_pair"].value_counts().items()
    )
    concentration = pd.DataFrame(concentration_rows)
    concentration.to_csv(RUNTIME / "a7ff30a_concentration_summary.csv", index=False)

    warnings = list(contract.get("warnings", []))
    if len(selected) == 0:
        warnings.append("ensemble_has_no_positive_cost2_clue")
    if queue["semantic_pair"].astype(str).str.contains("basis_premium_like", regex=False).all():
        warnings.append("ensemble_is_basis_premium_root_concentrated")
    decision = (
        "PASS_A7FF30A_PORTFOLIO_REPLAY_SMOKE_FOUND_ENSEMBLE_CLUES_NO_SEARCH_AUTH"
        if len(selected) > 0
        else "HOLD_A7FF30A_PORTFOLIO_REPLAY_SMOKE_NO_ENSEMBLE_CLUE"
    )
    manifest = {
        "stage": "A7FF-30A",
        "generated_at": now_utc(),
        "decision": decision,
        "candidate_count": int(len(queue)),
        "symbol_count": int(len(loaded_symbols)),
        "timestamp_count": int(len(timestamps)),
        "full_timestamp_count": full_timestamp_count,
        "portfolio_metric_rows": int(len(metrics)),
        "ensemble_clue_rows": int(len(selected)),
        "missing_fields": missing_fields,
        "warnings": warnings,
        "executes_generation": False,
        "executes_replay": True,
        "executes_search": False,
        "authorizes_a7ff31_portfolio_forensic_contract": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff30a_manifest.json", manifest)
    write_json(RUNTIME / "a7ff30a_decision_record.json", manifest)

    lines = [
        "# CRYPTO A7FF-30A PORTFOLIO REPLAY SMOKE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-30A runs a bounded portfolio replay smoke on the frozen six-candidate queue. Candidate weights are equal; no formula generation, learned weights, search, alpha proof, shadow, paper, or live execution is authorized.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Selected Ensemble Clues",
        "",
        md_table(selected[["portfolio_name", "label_family", "label_horizon_h", "premay_positive_split_count", "cost2_recent_oriented", "cost5_recent_oriented", "cost10_recent_oriented", "recent_oos_2026JanApr_tstat"]] if not selected.empty else selected, 40),
        "",
        "## Signal Materialization",
        "",
        md_table(pd.DataFrame(signal_rows), 20),
        "",
        "## Leave-One-Out Metrics",
        "",
        md_table(loo.head(40), 40),
        "",
        "## Concentration",
        "",
        md_table(concentration, 20),
        "",
        "## Boundary",
        "",
        "```text",
        "A7FF-30A is a portfolio smoke only. It does not authorize formula search, alpha proof, shadow, paper, or live execution.",
        "Basis/premium-root concentration remains an active warning.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
