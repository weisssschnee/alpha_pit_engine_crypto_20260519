from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "runtime" / "a7al2x_objective_family_reset"
REPORT = REPO / "reports" / "CRYPTO_A7AL2X_OBJECTIVE_FAMILY_RESET_CONTRACT_20260528.md"

A7AL2X0_AUTH = REPO / "runtime" / "a7al2x0_authorization_arbitration" / "a7al2x0_authorization_matrix.json"
A7AL2X0_NEXT = REPO / "runtime" / "a7al2x0_authorization_arbitration" / "a7al2x0_required_next.json"
A7AR7_POOL = REPO / "runtime" / "a7ar7_shared_candidate_pool" / "a7ar7_shared_candidate_pool.csv"
A7AR8_REGISTRY = REPO / "runtime" / "a7ar8_signal_vector_cluster_registry" / "a7ar8_signal_cluster_registry.csv"
A7AL2W_MANIFEST = REPO / "runtime" / "a7al2w_signal_vector_selector_repair" / "a7al2w_manifest.json"


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
    for path in [A7AL2X0_AUTH, A7AL2X0_NEXT, A7AR7_POOL, A7AR8_REGISTRY, A7AL2W_MANIFEST]:
        require(path)

    x0_auth = read_json(A7AL2X0_AUTH)
    x0_next = read_json(A7AL2X0_NEXT)
    w_manifest = read_json(A7AL2W_MANIFEST)
    if x0_auth.get("a7al2x_objective_family_reset_contract") != "AUTHORIZED_CONTRACT_ONLY":
        raise SystemExit("A7AL-2X0 does not authorize A7AL-2X contract")
    if not w_manifest.get("authorizes_a7al2x_objective_family_reset_contract"):
        raise SystemExit("A7AL-2W does not authorize A7AL-2X contract")

    allowed = pd.DataFrame(
        [
            {
                "family_id": "F0_OI_delta_price_interaction",
                "status": "allowed_contract_only",
                "field_scope": "open_interest_delta|open_interest_value_delta|price_move",
                "economic_role": "leverage expansion or contraction under price move",
                "example_patterns": "Delta(OI,w)*Delta(price,w); Delta(OI_value,w)*price_move",
                "standalone_allowed": False,
                "requires_control_gate": True,
                "requires_signal_vector_cap": True,
            },
            {
                "family_id": "F1_OI_basis_premium_interaction",
                "status": "allowed_contract_only",
                "field_scope": "OI|OI_change|premium_abs|basis_dislocation",
                "economic_role": "leverage change under basis or premium dislocation",
                "example_patterns": "Delta(OI,w)*premium_abs; OI_change*basis_dislocation_state",
                "standalone_allowed": False,
                "requires_control_gate": True,
                "requires_signal_vector_cap": True,
            },
            {
                "family_id": "F2_OI_funding_crowding_interaction",
                "status": "allowed_contract_only",
                "field_scope": "OI|OI_change|funding_abs|funding_persistence|funding_neutral_state",
                "economic_role": "leverage under funding crowding or neutral funding state",
                "example_patterns": "Delta(OI,w)*funding_abs; OI_change*funding_persistence",
                "standalone_allowed": False,
                "requires_control_gate": True,
                "requires_signal_vector_cap": True,
            },
            {
                "family_id": "F3_positioning_divergence",
                "status": "allowed_contract_only",
                "field_scope": "global_long_short|top_account_long_short|top_position_long_short|account_position_divergence",
                "economic_role": "crowding divergence between accounts and position size",
                "example_patterns": "Sub(top_position_ratio,global_account_ratio); Delta(top_account_ratio,w)*price_state",
                "standalone_allowed": False,
                "requires_control_gate": True,
                "requires_signal_vector_cap": True,
            },
            {
                "family_id": "F4_OI_taker_flow_interaction",
                "status": "allowed_contract_only",
                "field_scope": "OI_change|taker_buy_sell_volume_ratio|aggressive_flow_reversal",
                "economic_role": "aggressive flow under leverage expansion or contraction",
                "example_patterns": "Delta(OI,w)*taker_buy_sell_ratio; OI_contraction*flow_reversal",
                "standalone_allowed": False,
                "requires_control_gate": True,
                "requires_signal_vector_cap": True,
            },
            {
                "family_id": "F5_OI_upper_regime_interaction",
                "status": "allowed_contract_only",
                "field_scope": "OI_features|leverage_crowding_state|basis_dislocation_state|stress_proxy_state|breadth|liquidity_cycle",
                "economic_role": "OI behavior conditional on upper market regime",
                "example_patterns": "OI_change*leverage_crowding_state; OI_value_delta*stress_proxy_state",
                "standalone_allowed": False,
                "requires_control_gate": True,
                "requires_signal_vector_cap": True,
            },
            {
                "family_id": "F6_OI_latent_state_interaction",
                "status": "allowed_contract_only",
                "field_scope": "OI|positioning|listing_age_latent|liquidity_tier|meme_multiplier_major_neutral_state",
                "economic_role": "OI/positioning within latent lifecycle and symbol-state buckets",
                "example_patterns": "latent_neutral_rank(OI_change); OI_state*meme_neutral_state",
                "standalone_allowed": False,
                "requires_control_gate": True,
                "requires_signal_vector_cap": True,
            },
        ]
    )

    forbidden = pd.DataFrame(
        [
            {"item": "same_direct_OI_price_objective_rerun", "status": "forbidden", "reason": "superseded by A7AL-2X0 and zero stress-clean selected candidates"},
            {"item": "direct_OI_price_expansion", "status": "forbidden", "reason": "direct OI x price is stress-vetoed weak prior only"},
            {"item": "funding_only_wrapper", "status": "forbidden", "reason": "must be interaction, not standalone wrapper"},
            {"item": "basis_only_wrapper", "status": "forbidden", "reason": "must be interaction, not standalone wrapper"},
            {"item": "liquidity_volatility_old_family", "status": "forbidden", "reason": "previous crypto path produced cluster/stress failures"},
            {"item": "A7V_activity_liquidity_self_reproduction_family", "status": "forbidden", "reason": "A7V family failed control/May attribution"},
            {"item": "stale_J5_overlay_aliases", "status": "forbidden", "reason": "canonical alias audit required; no stale fallback"},
            {"item": "raw_OKX_Binance_direct_price_comparison", "status": "forbidden", "reason": "contract-unit canonical fields only"},
            {"item": "full_open_FormulaGenV2_grammar", "status": "forbidden", "reason": "A7AL-2X is not an open grammar search"},
            {"item": "May_informed_regime_mask", "status": "forbidden", "reason": "May stress-only policy"},
            {"item": "May_in_ranking_selector_mutation_generation_weight_update", "status": "forbidden", "reason": "May allowed only for post-selection veto/attribution"},
        ]
    )

    selector_feature_contract = {
        "allowed_selector_features": {
            "replay_alignment": ["pre_may_replay_alignment", "label_entry_alignment", "split_dispersion"],
            "control_dominance": ["matched_control_margin", "wrong_lag_margin", "shuffle_control_margin"],
            "latency_cost": ["one_bar_lag_survival", "cost_proxy_survival", "turnover_proxy"],
            "neutralization": ["timevarying_latent_neutral_survival", "liquidity_tier_neutral_survival", "meme_multiplier_neutral_survival"],
            "robust_statistics": ["newey_west_tstat", "block_bootstrap_tstat", "nonoverlap_offset_tstat"],
            "diversity": ["signal_vector_cluster_id", "field_family_pair", "skeleton_key", "production_key"],
        },
        "forbidden_selector_features": [
            "May_return",
            "May_residual",
            "May_pass_fail",
            "May_stress_margin",
            "May_tuned_threshold",
            "promotion_label",
            "alpha_proof_label",
            "shadow_paper_live_label",
        ],
        "hard_gates": {
            "control_ratio_ge_1": "reject",
            "timevarying_latent_neutral_fail": "reject",
            "wrong_lag_or_shuffle_control_stronger": "reject",
            "same_signal_vector_cluster_over_cap": "reject_or_downrank",
            "same_skeleton_over_cap": "reject_or_downrank",
        },
        "uses_may_for_selector": False,
    }

    signal_vector_cap = {
        "selected_signal_vector_clusters": ">= min(selected_count, 4)",
        "selected_top_signal_vector_cluster_share": "<= 0.35",
        "selected_max_pairwise_corr": "<= 0.80",
        "same_skeleton_share": "<= 0.25",
        "same_production_key_share": "<= 0.20",
        "same_field_family_pair_share": "<= 0.35",
        "small_pool_rule": "for selected_count <= 4, selected candidates should be in distinct signal-vector clusters unless no eligible alternatives exist",
        "uses_may_for_cluster": False,
    }

    source_of_truth = {
        "required_inputs": {
            "shared_candidate_pool": str(A7AR7_POOL.relative_to(REPO)),
            "signal_vector_cluster_registry": str(A7AR8_REGISTRY.relative_to(REPO)),
            "selector_diversity_repair_manifest": str(A7AL2W_MANIFEST.relative_to(REPO)),
            "authorization_arbitration": str(A7AL2X0_AUTH.relative_to(REPO)),
        },
        "forbidden_inputs": [
            "direct A7AL-2P2 seed pool reads",
            "direct stale A7AL-2L or A7AL-2O single-stage artifact reads",
            "selector bypassing A7AR-7 shared candidate pool",
        ],
        "a7al2p2_status": x0_auth.get("a7al2p2_final_status"),
        "a7al2q_local_execution": x0_auth.get("a7al2q_local_execution"),
    }

    may_policy = {
        "allowed": ["post_selection_veto", "failure_attribution", "stress_report_label"],
        "forbidden": [
            "ranking",
            "selector_score",
            "threshold_tuning",
            "weight_selection",
            "generation",
            "mutation",
            "lane_allocation",
            "training_target",
            "regime_mask",
        ],
        "policy_source": "A7AL-2X0 authorization arbitration",
    }

    authorization = {
        "decision": "PASS_A7AL2X_OBJECTIVE_FAMILY_RESET_CONTRACT_READY_FOR_A7AL2X1",
        "a7al2x1_dry_rerank": "AUTHORIZED",
        "a7al2y_generation": "NOT_AUTHORIZED",
        "a7al2q_local_execution": "NOT_AUTHORIZED",
        "same_objective_rerun": "NOT_AUTHORIZED",
        "direct_oi_price_expansion": "NOT_AUTHORIZED",
        "large_formula_search": "NOT_AUTHORIZED",
        "alpha_proof": "NOT_AUTHORIZED",
        "shadow_paper_live": "NOT_AUTHORIZED",
    }

    manifest = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AL2X_OBJECTIVE_FAMILY_RESET_CONTRACT_READY_FOR_A7AL2X1",
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "allowed_objective_family_count": int(allowed.shape[0]),
        "forbidden_objective_count": int(forbidden.shape[0]),
        "direct_oi_price_status": "stress_vetoed_weak_prior_not_standalone_objective",
        "source_of_truth": "A7AR-7 shared candidate pool plus A7AR-8 clusters plus A7AL-2W repair plus A7AL-2X0 authorization",
        "authorizes_a7al2x1_dry_rerank": True,
        "authorizes_a7al2y_generation": False,
        "authorizes_a7al2q_local_execution": False,
        "authorizes_same_objective_rerun": False,
        "authorizes_direct_oi_price_expansion": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may_for_selector": False,
        "uses_may_for_generation": False,
        "uses_may_for_mutation": False,
        "uses_may_for_weight_update": False,
        "uses_may_for_veto_or_attribution": True,
    }

    allowed.to_csv(OUT_DIR / "a7al2x_allowed_objective_families.csv", index=False)
    forbidden.to_csv(OUT_DIR / "a7al2x_forbidden_objective_families.csv", index=False)
    write_json(OUT_DIR / "a7al2x_selector_feature_contract.json", selector_feature_contract)
    write_json(OUT_DIR / "a7al2x_signal_vector_cap_policy.json", signal_vector_cap)
    write_json(OUT_DIR / "a7al2x_shared_pool_source_of_truth.json", source_of_truth)
    write_json(OUT_DIR / "a7al2x_may_policy_audit.json", may_policy)
    write_json(OUT_DIR / "a7al2x_authorization_matrix.json", authorization)
    write_json(OUT_DIR / "a7al2x_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2X Objective Family Reset Contract

Generated: {manifest["generated_at"]}

## Decision

```text
{manifest["decision"]}
```

This is an objective-family reset contract. It executes no generation, no replay, no training, and no proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Core Reset

```text
direct OI x price:
  status = stress-vetoed weak prior
  not standalone objective
  not eligible for same-objective rerun
  not eligible for direct expansion
```

## Allowed Objective Families

{md_table(allowed, 80)}

## Forbidden Objective Families / Paths

{md_table(forbidden, 80)}

## Selector Feature Contract

```json
{json.dumps(selector_feature_contract, indent=2, sort_keys=True)}
```

## Signal-Vector Cap Policy

```json
{json.dumps(signal_vector_cap, indent=2, sort_keys=True)}
```

## Source of Truth

```json
{json.dumps(source_of_truth, indent=2, sort_keys=True)}
```

## May Policy

```json
{json.dumps(may_policy, indent=2, sort_keys=True)}
```

## Authorization

```json
{json.dumps(authorization, indent=2, sort_keys=True)}
```

## Next Stage

```text
A7AL-2X1 dry rerank:
  authorized after this contract
  no generation
  no replay
  no search
  no alpha proof
```
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
