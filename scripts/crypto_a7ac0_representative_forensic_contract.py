from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ac0_representative_forensic_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AC0_REPRESENTATIVE_FORENSIC_CONTRACT_20260529.md"

A7AB9_MANIFEST = REPO / "runtime" / "a7ab9_survivor_freeze_contract" / "a7ab9_manifest.json"
A7AB9_REPS = REPO / "runtime" / "a7ab9_survivor_freeze_contract" / "a7ab9_representative_survivor_pool.csv"
A7AB9_SURVIVORS = REPO / "runtime" / "a7ab9_survivor_freeze_contract" / "a7ab9_survivor_pool.csv"


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


def representative_risk_flags(reps: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    dup_candidate_counts = reps["candidate_id"].astype(str).value_counts()
    top_symbol_counts = reps["top_symbol"].astype(str).value_counts()
    for _, row in reps.iterrows():
        flags: list[str] = []
        control_ratio = float(row.get("control_ratio_premay_max", 0.0))
        if control_ratio >= 1.0:
            flags.append("control_ratio_hard_hold_ge_1")
        elif control_ratio >= 0.80:
            flags.append("control_ratio_warning_ge_0_80")
        if dup_candidate_counts[str(row["candidate_id"])] > 1:
            flags.append("same_candidate_multi_horizon")
        if top_symbol_counts[str(row.get("top_symbol", ""))] >= max(3, len(reps) // 2):
            flags.append("top_symbol_repeats_in_representative_pool")
        if float(row.get("oriented_recent_spread", 0.0)) <= 0:
            flags.append("recent_spread_nonpositive")
        if float(row.get("one_bar_lag_recent_oriented", 0.0)) <= 0:
            flags.append("one_bar_lag_nonpositive")
        rows.append(
            {
                "representative_rank": int(row["representative_rank"]),
                "candidate_id": row["candidate_id"],
                "label_family": row["label_family"],
                "horizon_h": int(row["horizon_h"]),
                "return_corr_cluster": int(row["return_corr_cluster"]),
                "control_ratio_premay_max": control_ratio,
                "top_symbol": row.get("top_symbol", ""),
                "top_month": row.get("top_month", ""),
                "risk_flag_count": len(flags),
                "risk_flags": ";".join(flags) if flags else "none",
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ab9 = read_json(A7AB9_MANIFEST)
    if not a7ab9.get("authorizes_a7ac0_representative_forensic_contract"):
        raise SystemExit("A7AB-9 does not authorize A7AC-0")

    reps = pd.read_csv(A7AB9_REPS)
    survivors = pd.read_csv(A7AB9_SURVIVORS)
    risk_flags = representative_risk_flags(reps)

    label_summary = (
        reps.groupby(["label_family", "horizon_h"], as_index=False)
        .agg(
            representative_rows=("candidate_id", "count"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_validation_spread=("oriented_validation_spread", "median"),
            median_test_spread=("oriented_test_spread", "median"),
            median_recent_spread=("oriented_recent_spread", "median"),
        )
        .sort_values(["representative_rows", "median_recent_spread"], ascending=[False, False])
    )
    cluster_summary = (
        reps.groupby("return_corr_cluster", as_index=False)
        .agg(
            representative_rows=("candidate_id", "count"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_recent_spread=("oriented_recent_spread", "median"),
        )
        .sort_values(["representative_rows", "median_recent_spread"], ascending=[False, False])
    )
    risk_summary = (
        risk_flags.assign(has_risk=lambda df: df["risk_flags"].ne("none"))
        .groupby("risk_flags", as_index=False)
        .agg(rows=("candidate_id", "count"))
        .sort_values("rows", ascending=False)
    )

    required_tests = pd.DataFrame(
        [
            {
                "test": "source_of_truth_provenance",
                "purpose": "confirm every representative comes from A7AB-9 and no stale A7AB artifacts are reused",
                "blocking": True,
            },
            {
                "test": "full_window_metric_reproduction",
                "purpose": "rerun representative metrics from expressions and compare with A7AB-8 values",
                "blocking": True,
            },
            {
                "test": "control_dominance_by_split_and_type",
                "purpose": "wrong-lag, stale, shuffle, sign-flip, random-field controls must remain weaker in train/validation/test/recent",
                "blocking": True,
            },
            {
                "test": "nonoverlap_and_block_robust_stats",
                "purpose": "replace naive overlapping-hour confidence with horizon-aware non-overlap and block bootstrap summaries",
                "blocking": True,
            },
            {
                "test": "label_family_specificity",
                "purpose": "all current representatives are L7 ranked-return clues; audit whether this is a label artifact",
                "blocking": False,
            },
            {
                "test": "field_native_lag_and_cost_ladder",
                "purpose": "check one-bar execution and 2/5/10/20bps cost proxy survival without artificial two-hour delay policy",
                "blocking": True,
            },
            {
                "test": "symbol_month_tier_concentration",
                "purpose": "audit symbol, month, listing-age, meme, multiplier, major/alt, and latent-state concentration",
                "blocking": True,
            },
            {
                "test": "cluster_representative_independence",
                "purpose": "verify one representative per return-corr cluster remains diverse after reproduction",
                "blocking": True,
            },
            {
                "test": "beta_liquidity_latent_neutral_survival",
                "purpose": "measure BTC/ETH beta, liquidity-tier, latent-state, meme, and multiplier neutral survival",
                "blocking": True,
            },
            {
                "test": "May_stress_label_only_if_available",
                "purpose": "May can only be post-selection stress/veto/failure attribution; never selector, score, generation, or threshold",
                "blocking": True,
            },
        ]
    )
    pass_gates = pd.DataFrame(
        [
            {"gate": "provenance_clean", "rule": "all representatives trace to A7AB-9 source-of-truth artifacts"},
            {"gate": "metric_reproduction_tolerance", "rule": "reproduced validation/test/recent spreads match A7AB-8 within 1e-10 or documented rounding"},
            {"gate": "control_hard_gate", "rule": "reject any representative with control_ratio >= 1.0 in any pre-May split"},
            {"gate": "control_warning_gate", "rule": "representatives with 0.80 <= control_ratio < 1.0 remain diagnostic only"},
            {"gate": "robust_stats_positive", "rule": "nonoverlap or block-robust statistics remain positive for validation/test/recent"},
            {"gate": "lag_and_cost_survival", "rule": "one-bar lag and 10bps/20bps cost proxies remain positive"},
            {"gate": "concentration_cap", "rule": "no single symbol, month, latent state, meme group, or multiplier group dominates surviving representatives"},
            {"gate": "label_concentration_caveat", "rule": "single-label-family dominance blocks promotion beyond forensic until independently diversified"},
            {"gate": "no_may_leakage", "rule": "May remains stress-only and cannot enter selector, ranking, mutation, generation, or thresholds"},
        ]
    )
    experiment_record = {
        "date": "2026-05-29",
        "experiment_id": "20260529_a7ac0_representative_forensic_contract",
        "objective": "Define the forensic execution contract for A7AB-9 representative survivors.",
        "status": "completed",
        "mode": "light_contract",
        "inputs": {
            "manifest": str(A7AB9_MANIFEST),
            "representative_pool": str(A7AB9_REPS),
            "survivor_pool": str(A7AB9_SURVIVORS),
            "input_decision": a7ab9.get("decision"),
        },
        "parameters": {
            "replay_execution": False,
            "formula_generation": False,
            "search_execution": False,
            "May_usage": "stress_only_if_available; not used by A7AC0",
        },
        "outputs": {
            "runtime": str(RUNTIME),
            "report": str(REPORT),
        },
        "decision": "contract_only",
        "next_action": "A7AC-1 representative forensic execution",
    }

    top_label_share = float(a7ab9.get("top_label_share", 0.0))
    top_cluster_share = float(a7ab9.get("top_cluster_share", 0.0))
    warnings = list(a7ab9.get("warnings", []))
    if (risk_flags["control_ratio_premay_max"] >= 0.80).any():
        warnings.append("representatives_with_control_ratio_warning_ge_0_80")
    if reps["candidate_id"].astype(str).duplicated(keep=False).any():
        warnings.append("same_candidate_selected_in_multiple_horizons")

    decision = "PASS_A7AC0_REPRESENTATIVE_FORENSIC_CONTRACT_READY_FOR_A7AC1_WITH_WARNINGS" if warnings else "PASS_A7AC0_REPRESENTATIVE_FORENSIC_CONTRACT_READY_FOR_A7AC1"
    manifest = {
        "stage": "A7AC-0",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_contract_only": True,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may": False,
        "input_a7ab9_decision": a7ab9.get("decision"),
        "representative_rows": int(len(reps)),
        "source_survivor_rows": int(len(survivors)),
        "representative_candidate_count": int(reps["candidate_id"].nunique()),
        "representative_cluster_count": int(reps["return_corr_cluster"].nunique()),
        "top_label_share": top_label_share,
        "top_cluster_share_before_representative_freeze": top_cluster_share,
        "representatives_control_warning_ge_0_80": int((risk_flags["control_ratio_premay_max"] >= 0.80).sum()),
        "representatives_control_hard_hold_ge_1": int((risk_flags["control_ratio_premay_max"] >= 1.0).sum()),
        "warnings": sorted(set(warnings)),
        "authorizes_a7ac1_representative_forensic_execution": True,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    reps.to_csv(RUNTIME / "a7ac0_representative_input_pool.csv", index=False)
    survivors.to_csv(RUNTIME / "a7ac0_source_survivor_pool.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ac0_label_summary.csv", index=False)
    cluster_summary.to_csv(RUNTIME / "a7ac0_representative_cluster_summary.csv", index=False)
    risk_flags.to_csv(RUNTIME / "a7ac0_representative_risk_flags.csv", index=False)
    risk_summary.to_csv(RUNTIME / "a7ac0_risk_summary.csv", index=False)
    required_tests.to_csv(RUNTIME / "a7ac0_required_forensic_tests.csv", index=False)
    pass_gates.to_csv(RUNTIME / "a7ac0_pass_gates.csv", index=False)
    write_json(RUNTIME / "a7ac0_experiment_record.json", experiment_record)
    write_json(RUNTIME / "a7ac0_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ac0_authorization_matrix.json",
        {
            "A7AC-0": {"status": decision},
            "A7AC-1_representative_forensic_execution": {"authorized": True},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AC-0 REPRESENTATIVE FORENSIC CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AC-0 defines the next forensic execution contract for A7AB-9 representative survivors. It does not execute replay, train, search, or authorize alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Representative Label Summary",
        "",
        md_table(label_summary),
        "",
        "## Representative Cluster Summary",
        "",
        md_table(cluster_summary),
        "",
        "## Representative Risk Flags",
        "",
        md_table(risk_flags),
        "",
        "## Required Forensic Tests",
        "",
        md_table(required_tests),
        "",
        "## Pass Gates",
        "",
        md_table(pass_gates),
        "",
        "## Experiment Record",
        "",
        "```json",
        json.dumps(experiment_record, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
