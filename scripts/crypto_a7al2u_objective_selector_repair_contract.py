from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "runtime" / "a7al2u_objective_selector_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AL2U_OBJECTIVE_SELECTOR_REPAIR_CONTRACT_20260528.md"

A7AL2Q_MANIFEST = REPO / "runtime" / "company_a7al2q2r_full_20260528" / "runtime" / "a7al2q_local_oi_price_formula_search" / "a7al2q_manifest.json"
A7AL2R_MANIFEST = REPO / "runtime" / "company_a7al2q2r_full_20260528" / "runtime" / "a7al2r_local_forensic" / "a7al2r_manifest.json"
A7AL2S_MANIFEST = REPO / "runtime" / "a7al2s_company_full_followup_contract" / "a7al2s_manifest.json"
A7AL2T_MANIFEST = REPO / "runtime" / "a7al2t_company_may_stress_failure_attribution" / "a7al2t_manifest.json"
A7AL2T_FAILURE = REPO / "runtime" / "a7al2t_company_may_stress_failure_attribution" / "a7al2t_candidate_failure_summary.csv"
A7AL2R_DECISIONS = REPO / "runtime" / "company_a7al2q2r_full_20260528" / "runtime" / "a7al2r_local_forensic" / "a7al2r_decision_record.csv"
A7AL2R_OVERLAP = REPO / "runtime" / "company_a7al2q2r_full_20260528" / "runtime" / "a7al2r_local_forensic" / "a7al2r_overlap_robust_tstats.csv"


def utc_now() -> str:
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
        if pd.api.types.is_object_dtype(view[col]) or pd.api.types.is_string_dtype(view[col]):
            view[col] = view[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```\n" + view.to_string(index=False) + "\n```"


def require(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Missing required artifact: {path}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in [A7AL2Q_MANIFEST, A7AL2R_MANIFEST, A7AL2S_MANIFEST, A7AL2T_MANIFEST, A7AL2T_FAILURE, A7AL2R_DECISIONS, A7AL2R_OVERLAP]:
        require(path)

    q_manifest = read_json(A7AL2Q_MANIFEST)
    r_manifest = read_json(A7AL2R_MANIFEST)
    s_manifest = read_json(A7AL2S_MANIFEST)
    t_manifest = read_json(A7AL2T_MANIFEST)
    if not t_manifest.get("authorizes_a7al2u_objective_repair_contract"):
        raise SystemExit("A7AL-2T does not authorize A7AL-2U")

    failures = pd.read_csv(A7AL2T_FAILURE)
    decisions = pd.read_csv(A7AL2R_DECISIONS)
    overlap = pd.read_csv(A7AL2R_OVERLAP)

    failure_mode_summary = pd.DataFrame(
        [
            {
                "metric": "q_generated_total",
                "value": q_manifest.get("generated_total"),
                "interpretation": "local OI x price search budget executed on company machine",
            },
            {
                "metric": "q_executed_fast_replay",
                "value": q_manifest.get("executed_fast_replay"),
                "interpretation": "fast replay candidates scored before deep forensic",
            },
            {
                "metric": "q_diagnostic_candidates",
                "value": q_manifest.get("diagnostic_candidate_count"),
                "interpretation": "pre-May diagnostic candidates before deep forensic",
            },
            {
                "metric": "q_control_dominated",
                "value": q_manifest.get("decision_counts", {}).get("HOLD_A7AL2Q_CONTROL_DOMINATED"),
                "interpretation": "selector allowed many variants that controls could explain",
            },
            {
                "metric": "r_forensic_pass",
                "value": r_manifest.get("forensic_pass_count"),
                "interpretation": "pre-May deep forensic pass count",
            },
            {
                "metric": "t_unique_candidates",
                "value": t_manifest.get("unique_candidates"),
                "interpretation": "company full pool sent to May stress attribution",
            },
            {
                "metric": "t_sign_flip_rows",
                "value": t_manifest.get("sign_flip_rows"),
                "interpretation": "all candidate-entry rows flip sign in May",
            },
            {
                "metric": "t_may_control_dominated_rows",
                "value": t_manifest.get("may_control_dominated_rows"),
                "interpretation": "all candidate-entry rows are weaker than matched controls in May",
            },
        ]
    )

    pre_may_overlap = overlap[~overlap["split"].eq("known_may2026_stress")].copy()
    robust_summary = (
        pre_may_overlap.groupby("candidate_id", as_index=False)
        .agg(
            premay_min_newey_west_tstat=("newey_west_tstat_lag24", "min"),
            premay_min_block_bootstrap_tstat=("block_bootstrap_tstat_block24", "min"),
            premay_min_mean_spread=("mean_spread", "min"),
        )
        .merge(decisions[["candidate_id", "decision", "reasons", "warnings", "control_ratio_premay_max", "latent_positive_premay_splits"]], on="candidate_id", how="left")
    )

    selector_feature_contract = pd.DataFrame(
        [
            {"feature_group": "formula_lineage", "required_features": "expression_key;skeleton_key;production_key;operator_signature;field_family_set;window_signature;parent_seed_id", "may_allowed": False, "purpose": "dedup, diversity, and narrow-family cap"},
            {"feature_group": "replay_alignment", "required_features": "label_t1_spread_by_split;label_t2_spread_by_split;entry_label_agreement;min_split_spread;split_dispersion", "may_allowed": False, "purpose": "avoid one-entry alignment artifacts"},
            {"feature_group": "control_dominance", "required_features": "max_control_ratio_by_premay_split;control_margin_by_mode;control_close_count;control_hold_count", "may_allowed": False, "purpose": "reduce 114/128 control-dominated replay waste"},
            {"feature_group": "latency_cost", "required_features": "one_bar_lag_spread_by_split;net_2bps;net_5bps;net_10bps;turnover_proxy", "may_allowed": False, "purpose": "penalize timing and cost fragility without blanket +2h stress"},
            {"feature_group": "neutralization", "required_features": "timevarying_latent_spread;latent_positive_split_count;liquidity_tier_neutral_spread;age_or_listing_state_coverage", "may_allowed": False, "purpose": "avoid latent-state-only artifacts"},
            {"feature_group": "robust_statistics", "required_features": "newey_west_tstat_lag24;block_bootstrap_tstat_block24;nonoverlap_offset_min_tstat", "may_allowed": False, "purpose": "replace naive overlapping hourly t-stat in selector"},
            {"feature_group": "concentration", "required_features": "top_symbol_share;top_month_share;top_latent_share;top_skeleton_share;top_field_family_share", "may_allowed": False, "purpose": "cap single symbol/month/state/skeleton dominance"},
            {"feature_group": "stress_attribution", "required_features": "may_spread;may_control_ratio;may_sign_flip;may_failure_label", "may_allowed": "veto_and_report_only", "purpose": "never selector score; only post-selection attribution/veto"},
        ]
    )

    selector_gate_contract = pd.DataFrame(
        [
            {"gate": "premay_control_dominance_hard_gate", "rule": "reject if any pre-May split control_ratio >= 1.00", "applies_to": "selector and forensic", "uses_may": False},
            {"gate": "premay_control_close_penalty", "rule": "penalize 0.80 <= control_ratio < 1.00 instead of treating as clean seed", "applies_to": "selector score", "uses_may": False},
            {"gate": "entry_alignment_gate", "rule": "require label_t1 and label_t2 positive in validation/test/recent; require small dispersion between entry labels", "applies_to": "selector score", "uses_may": False},
            {"gate": "latent_survival_gate", "rule": "require time-varying latent-neutral positive in all pre-May evaluation splits", "applies_to": "selector score", "uses_may": False},
            {"gate": "robust_tstat_gate", "rule": "rank by min(Newey-West, block-bootstrap, non-overlap offset) not naive hourly t-stat", "applies_to": "selector score", "uses_may": False},
            {"gate": "family_diversity_gate", "rule": "top skeleton <= 15%, top production key <= 20%, top field-family <= 25% in selected replay pool", "applies_to": "selector pool", "uses_may": False},
            {"gate": "direct_oi_price_expansion_hold", "rule": "do not expand direct OI x price seeds until a repaired selector passes dry-run and control audit", "applies_to": "authorization", "uses_may": "veto_only"},
        ]
    )

    authorization_matrix = pd.DataFrame(
        [
            {"action": "a7al2v_replay_aware_selector_dryrun", "status": "AUTHORIZED", "reason": "repair selector features and dry-run on existing Q/R/T artifacts without search"},
            {"action": "a7al2q_rerun_same_objective", "status": "NOT_AUTHORIZED", "reason": "same objective produced all-candidate May sign flip/control domination"},
            {"action": "direct_oi_price_local_expansion", "status": "NOT_AUTHORIZED", "reason": "A7AL-2T company full stress attribution failed for all candidates"},
            {"action": "large_formula_search", "status": "NOT_AUTHORIZED", "reason": "selector/objective failure is unresolved"},
            {"action": "alpha_proof_shadow_paper_live", "status": "NOT_AUTHORIZED", "reason": "diagnostic only; no append-only proof"},
        ]
    )

    manifest = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AL2U_OBJECTIVE_SELECTOR_REPAIR_CONTRACT_READY",
        "input_a7al2q_decision": q_manifest.get("decision"),
        "input_a7al2r_decision": r_manifest.get("decision"),
        "input_a7al2s_decision": s_manifest.get("decision"),
        "input_a7al2t_decision": t_manifest.get("decision"),
        "company_full_unique_candidates": int(t_manifest.get("unique_candidates", 0) or 0),
        "company_full_sign_flip_rows": int(t_manifest.get("sign_flip_rows", 0) or 0),
        "company_full_may_control_dominated_rows": int(t_manifest.get("may_control_dominated_rows", 0) or 0),
        "authorizes_a7al2v_selector_dryrun": True,
        "authorizes_same_objective_rerun": False,
        "authorizes_direct_expansion": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may_for_selector": False,
        "uses_may_for_ranking": False,
        "uses_may_for_mutation": False,
        "uses_may_for_veto_or_attribution": True,
        "required_next": "Implement A7AL-2V replay-aware selector dry-run using non-May selector features; do not rerun same Q objective.",
    }

    failure_mode_summary.to_csv(OUT_DIR / "a7al2u_failure_mode_summary.csv", index=False)
    robust_summary.to_csv(OUT_DIR / "a7al2u_premay_robust_candidate_summary.csv", index=False)
    selector_feature_contract.to_csv(OUT_DIR / "a7al2u_selector_feature_contract.csv", index=False)
    selector_gate_contract.to_csv(OUT_DIR / "a7al2u_selector_gate_contract.csv", index=False)
    authorization_matrix.to_csv(OUT_DIR / "a7al2u_authorization_matrix.csv", index=False)
    write_json(OUT_DIR / "a7al2u_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2U Objective / Selector Repair Contract

Generated: {manifest["generated_at"]}

## Decision

```text
{manifest["decision"]}
```

This is a contract only. It executes no formula search, no training, no replay, and no proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Failure Mode Summary

{md_table(failure_mode_summary, 40)}

## Pre-May Robust Candidate Summary

{md_table(robust_summary, 40)}

## Selector Feature Contract

{md_table(selector_feature_contract, 40)}

## Selector Gate Contract

{md_table(selector_gate_contract, 40)}

## Authorization Matrix

{md_table(authorization_matrix, 20)}

## Boundary

```text
Authorized:
  A7AL-2V replay-aware selector dry-run on existing artifacts

Not authorized:
  same-objective A7AL-2Q rerun
  direct OI x price expansion
  large formula search
  alpha proof
  shadow / paper / live

May:
  allowed only as post-selection veto/attribution
  forbidden for selector score, ranking, mutation, generation, and training target
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
