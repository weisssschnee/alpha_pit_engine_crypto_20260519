# CRYPTO A7LS-14 SCALED MULTI-AXIS SEARCH CONTRACT

Generated: 2026-06-06T03:20:51Z

## Decision

`PASS_A7LS14_SCALED_MULTI_AXIS_SEARCH_CONTRACT_READY`

## Scale

- generated_total: 1,000,000
- materialization_total: 100,000
- numeric_total: 25,000
- company_numeric_shard_target: 256
- raw_reserved_generated_budget: 320,000
- raw_reserved_numeric_budget: 8,000

This is a real scale-up. The previous A7LS0 contract was 240k generated / 8k numeric. A7LS14 raises the next wave to 1,000,000 generated / 100,000 materialization / 25,000 numeric, with one protected raw multi-axis lane.

## Lane Budget Map

| lane_id   | lane_name                           | search_role           |   generated_budget |   materialization_budget |   numeric_budget |   min_numeric_before_kill | source                                    | field_axes                                                                   | allowed_depth                     | notes                                                                                              |   generated_share |   numeric_share |
|:----------|:------------------------------------|:----------------------|-------------------:|-------------------------:|-----------------:|--------------------------:|:------------------------------------------|:-----------------------------------------------------------------------------|:----------------------------------|:---------------------------------------------------------------------------------------------------|------------------:|----------------:|
| A7LS14_A  | exploit_a7ls13_multi_label_packet   | evidence_exploitation |             320000 |                    32000 |             8000 |                      2500 | A7LS13 replay packet seeds                | basis_premium;vol_liquidity;raw_multi_axis;listing_state;positioning_flow    | typed_l1_l2_l3_plus_seed_mutation | Exploit 25 candidate-level packet formulas with multi-label evidence.                              |              0.32 |            0.32 |
| A7LS14_B  | raw_multi_axis_reserved_search      | raw_discovery         |             320000 |                    32000 |             8000 |                      3000 | raw field ontology plus typed random axes | price;basis;funding;OI;positioning;taker;liquidity;volatility;listing;regime | raw_l1_l2_bounded_interactions    | Protected full route. It must not be prematurely killed by basis/premium exploitation.             |              0.32 |            0.32 |
| A7LS14_C  | underrepresented_axis_rescue        | coverage_repair       |             240000 |                    24000 |             6000 |                      2000 | A7LS12/13 weak-but-present axes           | positioning;listing_state;OI;taker_flow;funding_state                        | typed_l1_l2_l3_interactions       | Explicitly expands axes that survived weakly but were underrepresented in A7LS13 packet.           |              0.24 |            0.24 |
| A7LS14_D  | null_control_and_high_entropy_probe | control_and_entropy   |             120000 |                    12000 |             3000 |                      1000 | controls plus high-entropy grammar probes | controls;placebo;wrong_lag;shuffle;low_prior;entropy_probe                   | control_plus_bounded_raw          | Keeps one route honest: detects selector/reward self-deception and samples high-entropy raw space. |              0.12 |            0.12 |

## Axis Quota Policy

| axis            |   min_numeric_share |   max_numeric_share | can_dominate   |
|:----------------|--------------------:|--------------------:|:---------------|
| basis_premium   |                0.08 |                0.22 | False          |
| vol_liquidity   |                0.08 |                0.2  | False          |
| raw_multi_axis  |                0.2  |                0.35 | False          |
| positioning     |                0.08 |                0.18 | False          |
| listing_state   |                0.06 |                0.15 | False          |
| OI              |                0.06 |                0.16 | False          |
| taker_flow      |                0.05 |                0.14 | False          |
| funding_state   |                0.05 |                0.14 | False          |
| control_entropy |                0.08 |                0.18 | False          |

## A7LS13 Seed Packet Summary

| source_info_axis       | next_wave_family                |   a7ls13_packet_rows |
|:-----------------------|:--------------------------------|---------------------:|
| vol_liquidity_x_basis  | vol_liquidity_interaction       |                    8 |
| raw_multi_axis         | raw_multi_axis_probe            |                    6 |
| vol_liquidity_x_basis  | basis_context_interaction       |                    4 |
| listing_x_basis_regime | listing_state_interaction       |                    2 |
| positioning_x_basis    | positioning_context_interaction |                    2 |
| vol_liquidity_x_basis  | vol_liquidity_deep              |                    2 |
| positioning_x_basis    | positioning_flow_recovery       |                    1 |

## Execution Plan

| step     | name                                            | runs_heavy_compute   | output                                    |
|:---------|:------------------------------------------------|:---------------------|:------------------------------------------|
| A7LS14-0 | scaled contract and seed-map freeze             | False                | this stage                                |
| A7LS15   | million-scale multi-axis blueprint generation   | False                | 1,000,000 blueprint index plus shard plan |
| A7LS16   | local preflight and field/materialization smoke | False                | 512-row preflight                         |
| A7LS17   | company sharded materialization                 | True                 | 100,000 materialized queue rows           |
| A7LS18   | company sharded numeric wave                    | True                 | 25,000 numeric rows with checkpoints      |
| A7LS19   | checkpoint arbitration and lane resize          | False                | continue/kill/expand decisions per lane   |

## Checkpoint Policy

```json
{
  "checkpoint_numeric_intervals": [
    2000,
    5000,
    10000,
    15000,
    20000,
    25000
  ],
  "company_max_parallel_default": 3,
  "company_max_parallel_if_memory_free_gb_ge_18": 4,
  "company_numeric_shard_target": 256,
  "execution_style": "large_scale_checkpointed_multi_axis",
  "generated_total": 1000000,
  "global_kill_rules": [
    "eval_failure_rate > 0.05 after 2000 numeric rows",
    "control_dominated_rate > 0.65 after 5000 numeric rows",
    "non_l7_numeric_clue_rate == 0 after 5000 numeric rows",
    "single_source_axis_share > 0.55 after checkpoint diversity repair",
    "single_skeleton_share > 0.20 in selected queue",
    "L7_ranked_label_share > 0.55 in selected queue"
  ],
  "hard_boundaries": {
    "alpha_proof": false,
    "may_in_selector": false,
    "same_objective_single_lane_capture": false,
    "shadow_paper_live": false,
    "unbounded_full_grammar": false
  },
  "lane_expand_rules": [
    "non_l7_numeric_clue_rate >= 0.006",
    "control_dominated_rate <= 0.35",
    "at least 3 label families survive",
    "at least 4 semantic pairs survive",
    "selected queue has >= 8 candidates after caps"
  ],
  "lane_minimum_runtime": {
    "raw_multi_axis_reserved_search": "do_not_kill_before_3000_numeric_rows_unless_eval_failure_or_control_dominates",
    "underrepresented_axis_rescue": "do_not_kill_before_2000_numeric_rows_unless_eval_failure_or_control_dominates"
  },
  "local_light_preflight_rows": 512,
  "materialization_total": 100000,
  "numeric_rows_per_shard_target": 96,
  "numeric_total": 25000,
  "stage": "A7LS-14"
}
```

## Authorization

- A7LS15 million-scale blueprint generation: authorized
- A7LS17 company materialization: authorized after A7LS16 local preflight
- A7LS18 company numeric wave: authorized after materialization
- alpha proof / shadow / paper / live: not authorized
