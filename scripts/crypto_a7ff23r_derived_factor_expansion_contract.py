from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff23r_derived_factor_expansion_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF23R_DERIVED_FACTOR_EXPANSION_CONTRACT_20260530.md"

A7FFR1_MANIFEST = REPO / "runtime" / "a7ffr1_field_ontology_v3" / "a7ffr1_manifest.json"
A7FFR1_ONTOLOGY = REPO / "runtime" / "a7ffr1_field_ontology_v3" / "a7ffr1_field_ontology_v3.csv"
A7FFR2_MANIFEST = REPO / "runtime" / "a7ffr2_operator_probing_v2" / "a7ffr2_manifest.json"
A7FFR2_OPERATORS = REPO / "runtime" / "a7ffr2_operator_probing_v2" / "a7ffr2_operator_probe_policy.csv"
A7FFR3_MANIFEST = REPO / "runtime" / "a7ffr3_feature_pair_policy_v2" / "a7ffr3_manifest.json"
A7FFR3_PAIRS = REPO / "runtime" / "a7ffr3_feature_pair_policy_v2" / "a7ffr3_feature_pair_policy_v2.csv"
A7FFR4_MANIFEST = REPO / "runtime" / "a7ffr4_coarse_to_fine_generation_redesign" / "a7ffr4_manifest.json"
A7FFR4_LEVELS = REPO / "runtime" / "a7ffr4_coarse_to_fine_generation_redesign" / "a7ffr4_generation_levels.csv"
A7FFR5_MANIFEST = REPO / "runtime" / "a7ffr5_response_backed_promotion_redesign" / "a7ffr5_manifest.json"
A7FFR5_SEEDS = REPO / "runtime" / "a7ffr5_response_backed_promotion_redesign" / "a7ffr5_seed_preview.csv"


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
    safe = df.head(max_rows).copy()
    for col in safe.select_dtypes(include=["object"]).columns:
        safe[col] = safe[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return safe.to_markdown(index=False)
    except ImportError:
        return "```text\n" + safe.to_string(index=False) + "\n```"


def require_ready(manifest: dict[str, Any], stage: str, expected_prefix: str = "PASS") -> None:
    decision = str(manifest.get("decision", ""))
    if not decision.startswith(expected_prefix):
        raise SystemExit(f"{stage} is not ready: {decision}")


def build_seed_policy(seeds: pd.DataFrame) -> pd.DataFrame:
    seed = seeds.copy()
    seed["best_control_ratio"] = pd.to_numeric(seed["best_control_ratio"], errors="coerce")
    seed["primitive_candidate_count"] = pd.to_numeric(seed["primitive_candidate_count"], errors="coerce").fillna(0).astype(int)
    seed["non_l7_candidate_count"] = pd.to_numeric(seed["non_l7_candidate_count"], errors="coerce").fillna(0).astype(int)
    seed["a7ff23r_seed_route"] = "blocked"
    seed.loc[seed["compiler_role_v3"].eq("ordinary_alpha_seed"), "a7ff23r_seed_route"] = "primary_signal_seed"
    seed.loc[seed["compiler_role_v3"].eq("exploratory_signal_seed"), "a7ff23r_seed_route"] = "exploratory_signal_seed"
    seed.loc[seed["compiler_role_v3"].eq("regime_neutralizer_interaction_seed"), "a7ff23r_seed_route"] = "modifier_only_seed"
    seed["standalone_alpha_allowed"] = seed["a7ff23r_seed_route"].eq("primary_signal_seed")
    seed["interaction_allowed"] = seed["a7ff23r_seed_route"].isin(
        ["primary_signal_seed", "exploratory_signal_seed", "modifier_only_seed"]
    )
    seed["numeric_probe_required"] = True
    seed["promotion_requirement"] = seed["a7ff23r_seed_route"].map(
        {
            "primary_signal_seed": "non_l7_confirm; control_ratio_lt_0_8; label_balanced_selector",
            "exploratory_signal_seed": "non_l7_confirm_required_before_alpha_role; control_ratio_lt_1_0_for_diagnostic",
            "modifier_only_seed": "may_condition_or_neutralize_only; no_standalone_alpha",
            "blocked": "not_available",
        }
    )
    return seed[
        [
            "field_name",
            "semantic_type_v3",
            "compiler_role_v3",
            "a7ff23r_seed_route",
            "standalone_alpha_allowed",
            "interaction_allowed",
            "numeric_probe_required",
            "non_l7_candidate_count",
            "primitive_candidate_count",
            "best_control_ratio",
            "promotion_requirement",
        ]
    ]


def build_pair_policy(pairs: pd.DataFrame) -> pd.DataFrame:
    allowed = pairs[pairs["pair_policy_v2"].isin(["allow_high_priority", "probe_high_priority"])].copy()
    if allowed.empty:
        return allowed
    allowed["a7ff23r_pair_route"] = allowed["pair_policy_v2"].map(
        {
            "allow_high_priority": "generation_priority",
            "probe_high_priority": "exploratory_generation_priority",
        }
    )
    allowed["standalone_pair_alpha_allowed"] = (
        allowed["left_role"].isin(["ordinary_alpha_seed", "exploratory_signal_seed"])
        | allowed["right_role"].isin(["ordinary_alpha_seed", "exploratory_signal_seed"])
    )
    allowed["requires_modifier_guard"] = allowed["left_role"].eq("regime_neutralizer_interaction_seed") | allowed[
        "right_role"
    ].eq("regime_neutralizer_interaction_seed")
    return allowed


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    r1 = read_json(A7FFR1_MANIFEST)
    r2 = read_json(A7FFR2_MANIFEST)
    r3 = read_json(A7FFR3_MANIFEST)
    r4 = read_json(A7FFR4_MANIFEST)
    r5 = read_json(A7FFR5_MANIFEST)
    require_ready(r1, "A7FF-R1")
    require_ready(r2, "A7FF-R2")
    require_ready(r3, "A7FF-R3")
    require_ready(r4, "A7FF-R4")
    if not bool(r5.get("authorizes_a7ff23r_contract")):
        raise SystemExit(f"A7FF-R5 does not authorize A7FF-23R: {r5.get('decision')}")

    ontology = pd.read_csv(A7FFR1_ONTOLOGY)
    operators = pd.read_csv(A7FFR2_OPERATORS)
    pairs = pd.read_csv(A7FFR3_PAIRS)
    levels = pd.read_csv(A7FFR4_LEVELS)
    seeds = pd.read_csv(A7FFR5_SEEDS)

    seed_policy = build_seed_policy(seeds)
    pair_policy = build_pair_policy(pairs)
    operator_policy = operators.copy()
    operator_policy["a7ff23r_operator_route"] = operator_policy["operator_policy_v2"].map(
        {
            "promote_for_generation": "primary_generation_operator",
            "diagnostic_only": "diagnostic_generation_operator",
            "probe_required": "probe_generation_operator",
        }
    ).fillna("probe_generation_operator")

    seed_family_summary = (
        seed_policy.groupby(["semantic_type_v3", "a7ff23r_seed_route"], dropna=False)
        .agg(
            field_count=("field_name", "count"),
            standalone_alpha_allowed=("standalone_alpha_allowed", "sum"),
            interaction_allowed=("interaction_allowed", "sum"),
            non_l7_candidate_rows=("non_l7_candidate_count", "sum"),
            primitive_candidate_rows=("primitive_candidate_count", "sum"),
            best_control_ratio=("best_control_ratio", "min"),
        )
        .reset_index()
        .sort_values(["a7ff23r_seed_route", "semantic_type_v3"])
    )
    pair_family_summary = (
        pair_policy.groupby(["semantic_pair", "a7ff23r_pair_route"], dropna=False)
        .agg(pair_count=("left_field", "count"), modifier_guard_pairs=("requires_modifier_guard", "sum"))
        .reset_index()
        .sort_values("pair_count", ascending=False)
        if not pair_policy.empty
        else pd.DataFrame()
    )

    generation_budget = {
        "generated_blueprints_target": 24000,
        "materialization_target": 3000,
        "company_numeric_wave_blueprints": 2400,
        "company_numeric_shards": 12,
        "company_numeric_shard_size": 200,
        "max_parallel_company_shards": 4,
        "external_label_balanced_selector_target_rows": 640,
        "deep_diagnostic_target": 128,
        "minimum_selected_label_families": 4,
        "minimum_selected_semantic_families": 4,
        "minimum_selected_signal_vector_clusters": 8,
    }
    generation_level_budget = pd.DataFrame(
        [
            {
                "level": "L1_single_field_transform",
                "target_blueprints": 5000,
                "source": "ordinary_alpha_seed + exploratory_signal_seed",
                "purpose": "probe whether single-source transforms have non-L7 response",
            },
            {
                "level": "L2_typed_two_field_interaction",
                "target_blueprints": 12000,
                "source": "A7FF-R3 allow/probe priority pairs",
                "purpose": "expand OI/funding/liquidity/vol/price interactions without open grammar",
            },
            {
                "level": "L3_state_conditioned_feature",
                "target_blueprints": 5000,
                "source": "modifier_only_seed as condition/neutralizer only",
                "purpose": "test regime/state conditioning without standalone state alpha",
            },
            {
                "level": "L4_factor_candidate_probe",
                "target_blueprints": 2000,
                "source": "response-backed candidates from L1-L3",
                "purpose": "produce selector-ready factor probes",
            },
        ]
    )
    selector_policy = {
        "selector": "external_label_balanced_selector_v2",
        "forbidden_selector": ["A7FF8_internal_selected_queue", "raw_pass_count_only", "L7_only_rank_label"],
        "allowed_labels": [
            "L0_raw_forward_return",
            "L1_cross_sectional_relative_return",
            "L2_BTC_ETH_beta_residual_return",
            "L3_liquidity_tier_relative_return",
            "L4_latent_state_relative_return",
            "L5_vol_adjusted_return",
            "L6_downside_avoidance_or_crash_beta",
        ],
        "ranked_label_policy": "L7 diagnostic only; cannot be sole promotion evidence",
        "max_top_label_share": 0.25,
        "max_top_semantic_family_share": 0.35,
        "max_top_pair_family_share": 0.30,
        "max_top_motif_share": 0.30,
        "min_non_l7_selected_share": 0.75,
        "control_ratio_diagnostic_gate": 1.0,
        "control_ratio_promotion_gate": 0.8,
        "uses_may_in_selector": False,
    }
    blocked_policy = {
        "blocked": [
            "old_A7FF23_direct_expansion_execution",
            "full_open_formula_search",
            "A7FF8_internal_queue_as_source_of_truth",
            "L7_ranked_future_return_only_promotion",
            "risk_or_regime_field_as_standalone_alpha",
            "May_in_generation_selector_mutation_or_thresholds",
            "alpha_proof_shadow_paper_live",
        ],
        "allowed_next": [
            "A7FF24R_company_execution_plan_contract",
            "A7FF24R_dry_generation_plan",
        ],
    }
    reproducibility = {
        "experiment_id": "20260530_a7ff23r_derived_factor_expansion_contract",
        "objective": "define heavier R-policy-derived feature-to-factor expansion without executing search",
        "input_files": [
            str(A7FFR1_ONTOLOGY),
            str(A7FFR2_OPERATORS),
            str(A7FFR3_PAIRS),
            str(A7FFR4_LEVELS),
            str(A7FFR5_SEEDS),
        ],
        "commands": [
            "G:\\PythonProject\\.venv\\Scripts\\python.exe scripts\\crypto_a7ff23r_derived_factor_expansion_contract.py"
        ],
        "mode": "contract_only",
        "reproducible": "yes",
        "continuation": "Implement A7FF24R company execution plan only from this contract; do not execute old A7FF23.",
    }

    decision = "PASS_A7FF23R_DERIVED_FACTOR_EXPANSION_CONTRACT_READY_FOR_A7FF24R_PLAN"
    manifest = {
        "stage": "A7FF-23R-DERIVED-FACTOR-EXPANSION-CONTRACT",
        "generated_at": now_utc(),
        "decision": decision,
        "source_r5_decision": r5.get("decision", ""),
        "source_seed_preview_rows": int(len(seeds)),
        "source_signal_semantic_family_count": int(r5.get("signal_semantic_family_count", 0)),
        "seed_route_counts": seed_policy["a7ff23r_seed_route"].value_counts().to_dict(),
        "allowed_pair_count": int(len(pair_policy)),
        "generation_budget": generation_budget,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff24r_company_execution_plan_contract": True,
        "authorizes_old_a7ff23_execution": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    seed_policy.to_csv(RUNTIME / "a7ff23r_seed_policy.csv", index=False)
    seed_family_summary.to_csv(RUNTIME / "a7ff23r_seed_family_summary.csv", index=False)
    operator_policy.to_csv(RUNTIME / "a7ff23r_operator_policy.csv", index=False)
    pair_policy.to_csv(RUNTIME / "a7ff23r_pair_policy.csv", index=False)
    pair_family_summary.to_csv(RUNTIME / "a7ff23r_pair_family_summary.csv", index=False)
    generation_level_budget.to_csv(RUNTIME / "a7ff23r_generation_level_budget.csv", index=False)
    write_json(RUNTIME / "a7ff23r_generation_budget.json", generation_budget)
    write_json(RUNTIME / "a7ff23r_selector_policy.json", selector_policy)
    write_json(RUNTIME / "a7ff23r_blocked_policy.json", blocked_policy)
    write_json(RUNTIME / "a7ff23r_reproducibility_record.json", reproducibility)
    write_json(RUNTIME / "a7ff23r_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-23R DERIVED FACTOR EXPANSION CONTRACT

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-23R replaces the old A7FF-23 execution path. It defines a heavier derived factor expansion from the A7FF-R ontology/operator/pair/promotion redesign. It does not execute generation, replay, search, or alpha proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Generation Budget

```json
{json.dumps(generation_budget, indent=2, sort_keys=True)}
```

## Generation Levels

{md_table(generation_level_budget)}

## Seed Family Summary

{md_table(seed_family_summary, 120)}

## Pair Family Summary

{md_table(pair_family_summary, 120)}

## Selector Policy

```json
{json.dumps(selector_policy, indent=2, sort_keys=True)}
```

## Blocked Policy

```json
{json.dumps(blocked_policy, indent=2, sort_keys=True)}
```

## Reproducibility

```json
{json.dumps(reproducibility, indent=2, sort_keys=True)}
```

## Boundary

- Executes generation: `false`
- Executes replay: `false`
- Executes search: `false`
- Uses May in selector/generation: `false`
- Authorizes old A7FF-23 execution: `false`
- Authorizes alpha proof / shadow / paper / live: `false`
- Authorizes next step: `A7FF-24R company execution plan contract`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
