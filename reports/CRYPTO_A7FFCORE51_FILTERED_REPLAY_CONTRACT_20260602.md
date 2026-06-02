# CRYPTO A7FF-CORE51 FILTERED REPLAY CONTRACT

Generated: 2026-06-02T01:24:00Z

## Decision

`PASS_A7FFCORE51_FILTERED_REPLAY_CONTRACT_READY_FOR_CORE51E`

CORE51 defines the filtered replay contract after CORE50 null-vector arbitration. It does not execute replay/search/proof/promotion.

## Candidate Summary

| metric                   |   value |
|:-------------------------|--------:|
| filtered_candidate_count |    1462 |
| semantic_pair_count      |      39 |
| operator_count           |       7 |
| stale_risk_tier_count    |       3 |

## Input Sources

| input_id                        | path                                                                                                   | role                                             | required   |
|:--------------------------------|:-------------------------------------------------------------------------------------------------------|:-------------------------------------------------|:-----------|
| I0_core50_filtered_seed_preview | runtime/a7ffcore50_null_vector_preflight_arbitration/a7ffcore50_filtered_seed_preview.csv              | source-of-truth replay candidate queue           | True       |
| I1_core49e_vector_metrics       | runtime/a7ffcore49e_full_universe_null_vector_preflight_execution/a7ffcore49e_seed_vector_metrics.csv  | materialization and null-vector diagnostics      | True       |
| I2_universe498_panel            | G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v2_20260527                     | market/metrics panel for replay labels and costs | True       |
| I3_latent_state_panel           | G:/AlphaFactory_CryptoData/gold/features/binance_universe498_latent_state_features_v1_20260527.parquet | latent/liquidity/listing neutralization support  | True       |

## Replay Candidate Policy

| gate                   | rule                                                                      | hard_gate   |
|:-----------------------|:--------------------------------------------------------------------------|:------------|
| materialization_status | must pass CORE49E                                                         | True        |
| null_vector_filter     | must pass CORE50 active/symbol/time-shuffle filters                       | True        |
| semantic_pair_cap      | selected replay queue share <= 0.25                                       | True        |
| operator_cap           | selected replay queue share <= 0.25                                       | True        |
| stale_risk_balance     | include low/medium/high stale-risk tiers; high tier is allowed but capped | True        |
| non_label_source       | May/stress labels cannot enter selection/ranking/scoring                  | True        |
| control_dominance      | matched null controls must be reported per split and can veto promotion   | True        |

## Replay Design

| design_id                |   candidate_input_count |   max_replay_candidates | selection_method                                                                | executes_replay_in_contract   |
|:-------------------------|------------------------:|------------------------:|:--------------------------------------------------------------------------------|:------------------------------|
| D0_filtered_queue_replay |                    1462 |                     384 | balanced by semantic_pair, operator, stale_risk_tier, and active_ratio quartile | False                         |
| D1_control_book          |                    1462 |                     384 | same selected expressions with stale/sign/time/symbol null vectors              | False                         |

## Label And Cost Policy

| item           | policy                                                                                                            |
|:---------------|:------------------------------------------------------------------------------------------------------------------|
| label_horizons | 1h/4h/8h/24h forward labels; report separately                                                                    |
| primary_labels | L0 raw, L1 cross-sectional relative, L3 liquidity-tier relative, L5 vol-adjusted; L7 ranked label cannot dominate |
| cost_proxy     | 2bps/5bps/10bps proxy tiers; no promotion if only 0-cost survives                                                 |
| neutralization | global, liquidity-tier, latent-state, major/meme/multiplier diagnostics                                           |
| stats          | non-overlap offset stats and block/Newey-West style robust t-stat where available                                 |
| stress_policy  | known stress may be post-selection veto/attribution only; never ranking input                                     |

## Pass Gate

| gate                         | threshold                                           |
|:-----------------------------|:----------------------------------------------------|
| selected_candidate_count     | >= 128 for CORE51E                                  |
| selected_semantic_pair_count | >= 20                                               |
| selected_operator_count      | >= 5                                                |
| top_semantic_pair_share      | <= 0.25                                             |
| top_operator_share           | <= 0.25                                             |
| selected_non_l7_evidence     | must be present; L7-only cannot pass                |
| matched_null_controls        | controls must be weaker than original for promotion |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE51E filtered replay preflight/execution": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "direct_live_replay_without_controls": true,
    "formula_search": true,
    "large_search": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core51e_filtered_replay": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE51_FILTERED_REPLAY_CONTRACT_READY_FOR_CORE51E",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "filtered_candidate_count": 1462,
  "generated_at": "2026-06-02T01:24:00Z",
  "next_allowed": "A7FF-CORE51E filtered replay preflight/execution",
  "operator_count": 7,
  "semantic_pair_count": 39,
  "source_decision": "PASS_A7FFCORE50_NULL_VECTOR_ARBITRATION_READY_FOR_CORE51_FILTERED_REPLAY_CONTRACT",
  "source_stage": "A7FF-CORE50",
  "stage": "A7FF-CORE51"
}
```
