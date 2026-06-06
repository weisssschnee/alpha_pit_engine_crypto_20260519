# CRYPTO A7LS-16X 4M SCALE-UP AUTHORIZATION

Generated: 2026-06-06T05:30:32Z

## Decision

`PASS_A7LS16X_4M_SCALE_UP_AUTHORIZATION_READY`

## Scale Upgrade

- generated_total_limit: 4,000,000
- materialization_total_limit: 400,000
- numeric_total_limit: 100,000
- company_materialization_shards: 400
- company_numeric_shard_target: 1024
- raw_reserved_generated_budget: 1,400,000
- raw_reserved_numeric_budget: 35,000

A7LS-14 remains the 1M baseline. A7LS-16X raises the next company-machine execution ceiling to 4,000,000 generated / 400,000 materialization / 100,000 numeric rows after A7LS-16 preflight passed.

This is not alpha proof and not live authorization. It is a larger checkpointed search budget with a protected raw multi-axis lane and explicit anti-collapse rules.

## Lane Budget Map

| lane_id   | lane_name                       | search_role              |   generated_budget |   materialization_budget |   numeric_budget |   min_numeric_before_kill | field_axes                                                                                 | notes                                                                                                                       |   generated_share |   numeric_share |
|:----------|:--------------------------------|:-------------------------|-------------------:|-------------------------:|-----------------:|--------------------------:|:-------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------|------------------:|----------------:|
| A7LS16X_A | evidence_exploitation_deep      | exploit_confirmed_packet |             800000 |                    80000 |            20000 |                      6000 | basis_premium;vol_liquidity;listing_state;positioning_flow;raw_multi_axis                  | Expands A7LS13 packet-derived axes without allowing basis/premium to monopolize the total run.                              |              0.2  |            0.2  |
| A7LS16X_B | raw_multi_axis_frontier         | raw_discovery            |            1400000 |                   140000 |            35000 |                     12000 | price;basis;funding;OI;positioning;taker;liquidity;volatility;listing;regime;cross_axis    | Protected raw route. This is the main system-availability proof lane and must not be killed early for low initial hit rate. |              0.35 |            0.35 |
| A7LS16X_C | underrepresented_axis_expansion | coverage_repair          |            1000000 |                   100000 |            25000 |                      8000 | OI;positioning;taker_flow;funding_state;listing_state;regime_state                         | Keeps non-basis state variables alive at real scale instead of letting selector history starve them.                        |              0.25 |            0.25 |
| A7LS16X_D | control_entropy_and_nulls       | control_and_entropy      |             400000 |                    40000 |            10000 |                      3000 | controls;placebo;wrong_lag;shuffle;null_vector;entropy_probe                               | Maintains false-positive pressure and high-entropy exploration under the same compute budget.                               |              0.1  |            0.1  |
| A7LS16X_E | mapping_memory_cross_axis       | mapping_layer_probe      |             400000 |                    40000 |            10000 |                      3000 | mapping_clusters;memory_keys;semantic_pairs;signal_vector_novelty;portfolio_marginal_proxy | Reserved lane for mapping-layer guided cross-axis candidates, not a single-objective rerun.                                 |              0.1  |            0.1  |

## Checkpoint Policy

```json
{
  "expand_rules": [
    "lane non_l7_numeric_clue_rate >= 0.004 and control_dominated_rate <= 0.45",
    "at least 3 label families and 4 semantic pairs survive in lane",
    "portfolio_marginal_proxy positive after cluster cap"
  ],
  "hard_boundaries": {
    "alpha_proof": false,
    "local_heavy_numeric_execution": false,
    "may_in_selector_or_reward": false,
    "shadow_paper_live": false,
    "single_lane_budget_capture": false,
    "unbounded_full_grammar": false
  },
  "kill_rules_after_minimum_runtime": [
    "eval_failure_rate > 0.06 after lane minimum numeric rows",
    "control_dominated_rate > 0.72 after lane minimum numeric rows",
    "field_contract_violation_count > 0 after adapter repair window",
    "single_skeleton_share > 0.25 after checkpoint diversity repair"
  ],
  "non_kill_rules": [
    "do not kill raw_multi_axis_frontier for low non-L7 rate before 12,000 numeric rows",
    "do not kill underrepresented_axis_expansion for low hit rate before 8,000 numeric rows",
    "do not collapse all lanes into basis_premium even if early checkpoints favor it"
  ]
}
```

## Source Of Truth

```json
{
  "current_queue_status": "A7LS15 100k materialization queue remains usable as first wave; A7LS16X authorizes expansion queue generation after A7LS17 checkpoints",
  "does_not_rewrite_historical_artifacts": true,
  "local_execution_allowed": "schema/checkpoint bookkeeping only",
  "remote_execution_required": true,
  "requires": [
    "A7LS-14X",
    "A7LS-15",
    "A7LS-16"
  ],
  "supersedes_scale_limits_from": "A7LS-14 for future A7LS17/A7LS18 execution ceilings only"
}
```

## Authorization

```json
{
  "authorizes_a7ls15x_expansion_blueprint_generation": true,
  "authorizes_a7ls17_company_materialization": true,
  "authorizes_a7ls18_company_numeric_wave": true,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": true,
  "authorizes_scoped_large_search": true,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7LS16X_4M_SCALE_UP_AUTHORIZATION_READY",
  "generated_total_limit": 4000000,
  "materialization_total_limit": 400000,
  "numeric_total_limit": 100000,
  "scope_boundary": "checkpointed A7LS company-machine pipeline only",
  "stage": "A7LS-16X"
}
```
