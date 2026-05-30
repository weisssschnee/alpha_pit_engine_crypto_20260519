# CRYPTO A7FF-24R DRY GENERATION PLAN

Generated: 2026-05-30T06:20:13Z

## Decision

`PASS_A7FF24R_DRY_GENERATION_PLAN_READY_FOR_COMPANY_NUMERIC`

A7FF-24R turns the A7FF-23R contract into a concrete blueprint pool and a company-machine numeric wave queue. It does not run numeric evaluation, replay, search, or alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_company_numeric_execution": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "blueprint_count": 20599,
  "company_shard_count": 12,
  "company_wave_queue_count": 2400,
  "decision": "PASS_A7FF24R_DRY_GENERATION_PLAN_READY_FOR_COMPANY_NUMERIC",
  "executes_blueprint_generation": true,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T06:20:13Z",
  "materialization_motif_count": 10,
  "materialization_queue_count": 3000,
  "materialization_semantic_pair_count": 10,
  "motif_count": 10,
  "selector_policy": {
    "allowed_labels": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L2_BTC_ETH_beta_residual_return",
      "L3_liquidity_tier_relative_return",
      "L4_latent_state_relative_return",
      "L5_vol_adjusted_return",
      "L6_downside_avoidance_or_crash_beta"
    ],
    "control_ratio_diagnostic_gate": 1.0,
    "control_ratio_promotion_gate": 0.8,
    "forbidden_selector": [
      "A7FF8_internal_selected_queue",
      "raw_pass_count_only",
      "L7_only_rank_label"
    ],
    "max_top_label_share": 0.25,
    "max_top_motif_share": 0.3,
    "max_top_pair_family_share": 0.3,
    "max_top_semantic_family_share": 0.35,
    "min_non_l7_selected_share": 0.75,
    "ranked_label_policy": "L7 diagnostic only; cannot be sole promotion evidence",
    "selector": "external_label_balanced_selector_v2",
    "uses_may_in_selector": false
  },
  "semantic_pair_count": 15,
  "source_a7ff23r_decision": "PASS_A7FF23R_DERIVED_FACTOR_EXPANSION_CONTRACT_READY_FOR_A7FF24R_PLAN",
  "stage": "A7FF-24R-DRY-GENERATION-PLAN",
  "uses_may": false
}
```

## Level Summary

| level                          |   count |
|:-------------------------------|--------:|
| L1_single_field_transform      |     199 |
| L2_typed_two_field_interaction |    2659 |
| L3_state_conditioned_feature   |    7000 |
| L4_factor_candidate_probe      |   10741 |

## Materialization Queue Summary

| level                          |   materialization_count |
|:-------------------------------|------------------------:|
| L1_single_field_transform      |                     163 |
| L2_typed_two_field_interaction |                    1424 |
| L3_state_conditioned_feature   |                    1413 |

## Top Semantic Pairs

| semantic_pair                          |   count |
|:---------------------------------------|--------:|
| basis_premium_like\|funding_like       |    6000 |
| funding_like\|positioning_like         |    6000 |
| basis_premium_like\|positioning_like   |    4781 |
| basis_premium_like\|volatility_like    |    1563 |
| basis_premium_like\|price_like         |     773 |
| basis_premium_like\|basis_premium_like |     442 |
| price_like\|volatility_like            |     402 |
| volatility_like\|volatility_like       |     211 |
| liquidity_like\|volatility_like        |     124 |
| volatility_like                        |      84 |
| basis_premium_like                     |      81 |
| basis_premium_like\|liquidity_like     |      62 |
| price_like                             |      34 |
| basis_premium_like\|generic_numeric    |      24 |
| basis_premium_like\|state_or_taxonomy  |      18 |

## Company Shard Plan

| company_shard   |   row_count |   semantic_pairs |   motifs |   skeletons |
|:----------------|------------:|-----------------:|---------:|------------:|
| shard_00        |         200 |                2 |        5 |          20 |
| shard_01        |         200 |                1 |        3 |          17 |
| shard_02        |         200 |                2 |        4 |          10 |
| shard_03        |         200 |                1 |        3 |          12 |
| shard_04        |         200 |                2 |        4 |          12 |
| shard_05        |         200 |                1 |        4 |          12 |
| shard_06        |         200 |                2 |        6 |          14 |
| shard_07        |         200 |                6 |        7 |          17 |
| shard_08        |         200 |                1 |        2 |           6 |
| shard_09        |         200 |                1 |        2 |           8 |
| shard_10        |         200 |                1 |        2 |           6 |
| shard_11        |         200 |                2 |        4 |           7 |

## Remote Plan

```json
{
  "company_shard_size": 200,
  "company_shards": 12,
  "execution_status": "not_started",
  "local_queue": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7ff24r_dry_generation_plan\\a7ff24r_company_numeric_wave_queue.csv",
  "max_parallel_company_shards": 4,
  "next_required_script": "A7FF25R company numeric runner implementation or adapter against crypto_a7ff8_expanded_numeric_probe.py",
  "remote_python": "D:\\HermesWorker\\venvs\\phase3z33\\Scripts\\python.exe",
  "remote_repo": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote"
}
```

## Boundary

- Blueprint generation executed: `true`
- Numeric probe executed: `false`
- Replay/search executed: `false`
- Uses May: `false`
- Authorizes company numeric execution only after runner/adapter check: `true`
- Authorizes alpha proof / shadow / paper / live: `false`
