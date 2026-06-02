from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore50_null_vector_preflight_arbitration"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE50_NULL_VECTOR_PREFLIGHT_ARBITRATION_20260602.md"
CORE49E = REPO / "runtime" / "a7ffcore49e_full_universe_null_vector_preflight_execution" / "a7ffcore49e_manifest.json"
METRICS = REPO / "runtime" / "a7ffcore49e_full_universe_null_vector_preflight_execution" / "a7ffcore49e_seed_vector_metrics.csv"


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


def safe_abs(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").abs()


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE49E)
    if source.get("decision") != "PASS_A7FFCORE49E_NULL_VECTOR_PREFLIGHT_READY_FOR_CORE50_CONTRACT":
        raise SystemExit(f"CORE49E not ready for CORE50: {source.get('decision')}")
    metrics = pd.read_csv(METRICS)

    metrics["abs_stale_corr"] = safe_abs(metrics.get("stale_signal_corr", pd.Series(dtype=float)))
    metrics["abs_time_shuffle_corr"] = safe_abs(metrics.get("time_shuffle_signal_corr", pd.Series(dtype=float)))
    metrics["abs_symbol_shuffle_corr"] = safe_abs(metrics.get("symbol_shuffle_signal_corr", pd.Series(dtype=float)))
    metrics["active_ratio_num"] = pd.to_numeric(metrics.get("active_ratio", pd.Series(dtype=float)), errors="coerce")

    filter_policy = pd.DataFrame(
        [
            {"gate": "materialization_status", "rule": "must equal pass", "hard_gate": True},
            {"gate": "active_ratio", "rule": ">= 0.001", "hard_gate": True},
            {"gate": "symbol_shuffle_corr_abs", "rule": "<= 0.35 or missing", "hard_gate": True},
            {"gate": "time_shuffle_corr_abs", "rule": "<= 0.95 or missing", "hard_gate": True},
            {"gate": "stale_corr_abs", "rule": "record as risk tier; do not hard reject before replay contract", "hard_gate": False},
            {"gate": "family_cap", "rule": "replay contract must cap semantic_pair share <= 0.25", "hard_gate": True},
            {"gate": "operator_cap", "rule": "replay contract must cap operator share <= 0.25", "hard_gate": True},
        ]
    )
    eligible = metrics[
        metrics["materialization_status"].eq("pass")
        & metrics["active_ratio_num"].ge(0.001)
        & (metrics["abs_symbol_shuffle_corr"].isna() | metrics["abs_symbol_shuffle_corr"].le(0.35))
        & (metrics["abs_time_shuffle_corr"].isna() | metrics["abs_time_shuffle_corr"].le(0.95))
    ].copy()
    eligible["stale_risk_tier"] = pd.cut(
        eligible["abs_stale_corr"],
        bins=[-np.inf, 0.25, 0.75, np.inf],
        labels=["low", "medium", "high"],
    ).astype(str)

    summary = pd.DataFrame(
        [
            {"metric": "seed_count", "value": int(metrics.shape[0])},
            {"metric": "materialization_pass_count", "value": int(metrics["materialization_status"].eq("pass").sum())},
            {"metric": "eligible_after_null_filter_count", "value": int(eligible.shape[0])},
            {"metric": "semantic_family_count", "value": int(metrics["semantic_pair"].nunique())},
            {"metric": "eligible_semantic_family_count", "value": int(eligible["semantic_pair"].nunique())},
            {"metric": "operator_count", "value": int(metrics["operator"].nunique())},
            {"metric": "eligible_operator_count", "value": int(eligible["operator"].nunique())},
            {"metric": "median_abs_stale_corr", "value": float(metrics["abs_stale_corr"].median(skipna=True))},
            {"metric": "median_abs_time_shuffle_corr", "value": float(metrics["abs_time_shuffle_corr"].median(skipna=True))},
            {"metric": "median_abs_symbol_shuffle_corr", "value": float(metrics["abs_symbol_shuffle_corr"].median(skipna=True))},
        ]
    )
    family_summary = (
        eligible.groupby(["semantic_pair", "operator"], as_index=False)
        .agg(
            eligible_count=("seed_id", "count"),
            median_active_ratio=("active_ratio_num", "median"),
            median_abs_stale_corr=("abs_stale_corr", "median"),
            median_abs_time_shuffle_corr=("abs_time_shuffle_corr", "median"),
            median_abs_symbol_shuffle_corr=("abs_symbol_shuffle_corr", "median"),
        )
        .sort_values(["eligible_count", "median_abs_symbol_shuffle_corr"], ascending=[False, True])
    )
    stale_risk = (
        eligible.groupby(["stale_risk_tier"], as_index=False)
        .agg(seed_count=("seed_id", "count"), semantic_family_count=("semantic_pair", "nunique"), operator_count=("operator", "nunique"))
        .sort_values("seed_count", ascending=False)
    )
    inactive = metrics[~metrics["materialization_status"].eq("pass")].copy()

    eligible.to_csv(RUNTIME / "a7ffcore50_filtered_seed_preview.csv", index=False)
    summary.to_csv(RUNTIME / "a7ffcore50_arbitration_summary.csv", index=False)
    filter_policy.to_csv(RUNTIME / "a7ffcore50_replay_filter_policy.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore50_filtered_family_operator_summary.csv", index=False)
    stale_risk.to_csv(RUNTIME / "a7ffcore50_stale_risk_tier_summary.csv", index=False)
    inactive.to_csv(RUNTIME / "a7ffcore50_inactive_or_empty_seed_audit.csv", index=False)

    blockers = []
    if int(eligible.shape[0]) < 512:
        blockers.append("filtered_seed_count_too_low")
    if int(eligible["semantic_pair"].nunique()) < 20:
        blockers.append("filtered_semantic_family_count_too_low")
    if int(eligible["operator"].nunique()) < 5:
        blockers.append("filtered_operator_count_too_low")

    decision = (
        "PASS_A7FFCORE50_NULL_VECTOR_ARBITRATION_READY_FOR_CORE51_FILTERED_REPLAY_CONTRACT"
        if not blockers
        else "HOLD_A7FFCORE50_NULL_VECTOR_ARBITRATION_REPLAY_CONTRACT_BLOCKED"
    )
    authorization = {
        "authorized": {
            "A7FF-CORE51 filtered replay contract": decision.startswith("PASS_"),
            "A7FF-CORE50R null-vector filter repair": not decision.startswith("PASS_"),
        },
        "not_authorized": {
            "direct_replay_execution": True,
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    manifest = {
        "stage": "A7FF-CORE50",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE49E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "seed_count": int(metrics.shape[0]),
        "materialization_pass_count": int(metrics["materialization_status"].eq("pass").sum()),
        "eligible_after_null_filter_count": int(eligible.shape[0]),
        "eligible_semantic_family_count": int(eligible["semantic_pair"].nunique()),
        "eligible_operator_count": int(eligible["operator"].nunique()),
        "executes_replay": False,
        "executes_search": False,
        "executes_generation": False,
        "authorizes_core51_filtered_replay_contract": decision.startswith("PASS_"),
        "authorizes_direct_replay_execution": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE51 filtered replay contract" if decision.startswith("PASS_") else "A7FF-CORE50R null-vector filter repair",
    }
    write_json(RUNTIME / "a7ffcore50_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore50_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE50 NULL-VECTOR PREFLIGHT ARBITRATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE50 arbitrates CORE49E vector materialization results. It writes replay-contract filters only; it does not execute replay, search, proof, promotion, shadow, paper, or live.",
        "",
        "## Summary",
        "",
        md_table(summary),
        "",
        "## Replay Filter Policy",
        "",
        md_table(filter_policy),
        "",
        "## Stale Risk Tiers",
        "",
        md_table(stale_risk),
        "",
        "## Filtered Family / Operator Summary",
        "",
        md_table(family_summary, 80),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
