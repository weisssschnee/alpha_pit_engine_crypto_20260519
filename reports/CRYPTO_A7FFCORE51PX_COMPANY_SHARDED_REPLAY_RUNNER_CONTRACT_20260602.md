# CRYPTO A7FF-CORE51PX COMPANY-MACHINE SHARDED REPLAY RUNNER CONTRACT

Generated: 2026-06-02T02:35:47Z

## Decision

`PASS_A7FFCORE51PX_COMPANY_SHARDED_REPLAY_CONTRACT_READY_FOR_COMPANY_EXECUTION`

CORE51PX packages the filtered replay queue for company-machine sharded execution. It does not execute replay locally and does not authorize formula search, large search, proof, promotion, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_company_sharded_replay_execution": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_shard_count": 16,
  "decision": "PASS_A7FFCORE51PX_COMPANY_SHARDED_REPLAY_CONTRACT_READY_FOR_COMPANY_EXECUTION",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-02T02:35:47Z",
  "missing_field_count": 0,
  "next_allowed": "A7FF-CORE51PXE company-machine sharded replay execution",
  "operator_count": 7,
  "required_field_count": 42,
  "selected_candidate_count": 384,
  "semantic_pair_count": 39,
  "shard_size": 24,
  "source_decision": "HOLD_A7FFCORE51PR_LOCAL_REPLAY_RUNNER_INSUFFICIENT_USE_COMPANY_SHARDS",
  "source_stage": "A7FF-CORE51PR",
  "stage": "A7FF-CORE51PX"
}
```

## Input Sources

| input_id                    | path                                                                                                   | role                                      | required   |
|:----------------------------|:-------------------------------------------------------------------------------------------------------|:------------------------------------------|:-----------|
| I0_selected_candidate_queue | runtime/a7ffcore51px_company_sharded_replay_runner_contract/a7ffcore51px_selected_candidate_queue.csv  | balanced 384-candidate replay queue       | True       |
| I1_candidate_shards         | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/                          | 16 x 24-candidate shard CSVs              | True       |
| I2_compact_frame_contract   | runtime/a7ffcore51px_company_sharded_replay_runner_contract/a7ffcore51px_compact_frame_contract.csv    | required columns and source panel routing | True       |
| I3_base_panel               | G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v2_20260527                     | base universe498 replay panel             | True       |
| I4_latent_panel             | G:/AlphaFactory_CryptoData/gold/features/binance_universe498_latent_state_features_v1_20260527.parquet | latent/listing/liquidity overlay          | True       |

## Candidate Shard Plan

| shard_id          |   candidate_count |   candidate_start |   candidate_end_exclusive | relative_path                                                                                      |   max_runtime_minutes | resume_safe   |
|:------------------|------------------:|------------------:|--------------------------:|:---------------------------------------------------------------------------------------------------|----------------------:|:--------------|
| core51px_shard_00 |                24 |                 0 |                        24 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_00.csv |                    90 | True          |
| core51px_shard_01 |                24 |                24 |                        48 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_01.csv |                    90 | True          |
| core51px_shard_02 |                24 |                48 |                        72 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_02.csv |                    90 | True          |
| core51px_shard_03 |                24 |                72 |                        96 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_03.csv |                    90 | True          |
| core51px_shard_04 |                24 |                96 |                       120 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_04.csv |                    90 | True          |
| core51px_shard_05 |                24 |               120 |                       144 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_05.csv |                    90 | True          |
| core51px_shard_06 |                24 |               144 |                       168 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_06.csv |                    90 | True          |
| core51px_shard_07 |                24 |               168 |                       192 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_07.csv |                    90 | True          |
| core51px_shard_08 |                24 |               192 |                       216 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_08.csv |                    90 | True          |
| core51px_shard_09 |                24 |               216 |                       240 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_09.csv |                    90 | True          |
| core51px_shard_10 |                24 |               240 |                       264 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_10.csv |                    90 | True          |
| core51px_shard_11 |                24 |               264 |                       288 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_11.csv |                    90 | True          |
| core51px_shard_12 |                24 |               288 |                       312 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_12.csv |                    90 | True          |
| core51px_shard_13 |                24 |               312 |                       336 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_13.csv |                    90 | True          |
| core51px_shard_14 |                24 |               336 |                       360 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_14.csv |                    90 | True          |
| core51px_shard_15 |                24 |               360 |                       384 | runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/core51px_shard_15.csv |                    90 | True          |

## Compact Frame Contract

| field_name                           | source_panel        | status   |
|:-------------------------------------|:--------------------|:---------|
| age_percentile_active_universe       | latent_state_v1     | present  |
| age_x_funding_abs                    | latent_state_v1     | present  |
| age_x_volatility                     | latent_state_v1     | present  |
| execution_time                       | base_universe498_v2 | present  |
| funding_rate                         | base_universe498_v2 | present  |
| funding_rate_abs_168h                | latent_state_v1     | present  |
| funding_rate_mean_168h               | latent_state_v1     | present  |
| gap_hours_recent_168h                | latent_state_v1     | present  |
| global_long_short_account_ratio_last | base_universe498_v2 | present  |
| global_long_short_account_ratio_mean | base_universe498_v2 | present  |
| history_length_hours                 | latent_state_v1     | present  |
| index_close                          | base_universe498_v2 | present  |
| kline_taker_buy_quote_share          | base_universe498_v2 | present  |
| listing_age_days                     | latent_state_v1     | present  |
| mark_close                           | base_universe498_v2 | present  |
| mark_index_basis_bps                 | base_universe498_v2 | present  |
| mark_trade_basis_bps                 | base_universe498_v2 | present  |
| open_interest_last                   | base_universe498_v2 | present  |
| open_interest_mean                   | base_universe498_v2 | present  |
| premium_close                        | base_universe498_v2 | present  |
| premium_close_bps                    | base_universe498_v2 | present  |
| realized_vol_168h                    | latent_state_v1     | present  |
| realized_vol_24h                     | latent_state_v1     | present  |
| rolling_coverage_168h                | latent_state_v1     | present  |
| source_market_funding                | base_universe498_v2 | present  |
| source_metrics                       | base_universe498_v2 | present  |
| split                                | latent_state_v1     | present  |
| sqrt_listing_age_days                | latent_state_v1     | present  |
| symbol                               | key                 | present  |
| taker_buy_quote_volume               | base_universe498_v2 | present  |
| taker_buy_sell_volume_ratio_last     | base_universe498_v2 | present  |
| taker_buy_sell_volume_ratio_mean     | base_universe498_v2 | present  |
| timestamp                            | key                 | present  |
| trade_close                          | base_universe498_v2 | present  |
| trade_count                          | base_universe498_v2 | present  |
| trade_high                           | base_universe498_v2 | present  |
| trade_low                            | base_universe498_v2 | present  |
| trade_open                           | base_universe498_v2 | present  |
| trade_quote_volume                   | base_universe498_v2 | present  |
| trade_return_1h                      | base_universe498_v2 | present  |
| trade_return_24h                     | latent_state_v1     | present  |
| trade_volume                         | base_universe498_v2 | present  |

## Deployment Policy

| policy_id              | policy                                                             |
|:-----------------------|:-------------------------------------------------------------------|
| P0_no_local_retry      | do not rerun local pandas replay runner                            |
| P1_company_shards      | run candidate shards independently on company machine              |
| P2_compact_frame       | build compact frame with only required columns before shard replay |
| P3_incremental_outputs | write one metrics CSV and one manifest JSON per shard              |
| P4_resume_safe         | skip completed shards with PASS manifest unless force flag is set  |
| P5_no_search           | no formula generation/search/proof/promotion/shadow/paper/live     |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE51PXE company-machine sharded replay execution": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "local_runner_retry": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```
