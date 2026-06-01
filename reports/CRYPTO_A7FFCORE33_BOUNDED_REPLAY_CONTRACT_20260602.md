# CRYPTO A7FF-CORE33 BOUNDED REPLAY CONTRACT

Generated: 2026-06-01T19:06:07Z

## Decision

`PASS_A7FFCORE33_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE33E`

CORE33 defines bounded replay execution over CORE32E preflight survivors. It does not execute search, large search, alpha proof, shadow, paper, or live.

## Gate Audit

| gate                   | threshold                               |   observed | pass   |
|:-----------------------|:----------------------------------------|-----------:|:-------|
| replay_candidate_count | >= 12                                   |  21        | True   |
| family_count           | >= 3                                    |   3        | True   |
| cluster_unique         | all selected candidates unique clusters |  21        | True   |
| top_family_share       | <= 0.50                                 |   0.380952 | True   |

## Family Summary

| family_id                         |   replay_candidate_count |   cluster_count |   median_control_ratio |   median_abs_ic |
|:----------------------------------|-------------------------:|----------------:|-----------------------:|----------------:|
| F1a_aggtrades_flow_microstructure |                        7 |               7 |              0.0791233 |       0.0125352 |
| F1b_taker_flow_market_panel       |                        6 |               6 |              0.448885  |       0.0111356 |
| F2a_basis_funding_independent     |                        8 |               8 |              0.226403  |       0.0128131 |

## Replay Protocol

| item            | value                                                                                       |
|:----------------|:--------------------------------------------------------------------------------------------|
| portfolio_proxy | hourly cross-sectional top/bottom decile spread; equal-weight and liquidity-capped variants |
| labels          | L0/L1/L3/L5 primary; L7 diagnostic only                                                     |
| horizons        | 4h, 8h, 24h                                                                                 |
| costs           | 2bps, 5bps, 10bps proxy                                                                     |
| controls        | row shuffle, time shuffle, wrong-lag future, stale, sign flip, same-family placebo          |
| robust_stats    | non-overlap offset tstat; simple block bootstrap; split consistency                         |
| concentration   | family, cluster, symbol, month, and dataset contribution caps                               |
| boundary        | bounded replay only; no search, alpha proof, shadow, paper, live                            |

## Replay Candidate Queue

| replay_candidate_id   | family_id                         | motif                            | operator        | primary_field                      | partner_field          |   max_abs_ic |   min_control_ratio |
|:----------------------|:----------------------------------|:---------------------------------|:----------------|:-----------------------------------|:-----------------------|-------------:|--------------------:|
| a7ffcore33_000        | F1b_taker_flow_market_panel       | taker_flow_x_liquidity           | WinsorZ         | trade_volume                       | trade_quote_volume     |   0.0406095  |           0.513661  |
| a7ffcore33_001        | F1b_taker_flow_market_panel       | low_turnover_flow_state          | WinsorZ         | taker_buy_quote_volume             | funding_rate           |   0.0185618  |           0.0141414 |
| a7ffcore33_002        | F2a_basis_funding_independent     | basis_x_flow                     | Delta           | funding_rate                       | taker_buy_quote_volume |   0.0175978  |           0.210195  |
| a7ffcore33_003        | F2a_basis_funding_independent     | basis_delta_x_funding            | SpreadShortLong | mark_index_basis_bps               | trade_volume           |   0.0159636  |           0.214964  |
| a7ffcore33_004        | F2a_basis_funding_independent     | H8_H24_dislocation               | Delta           | funding_rate                       | trade_volume           |   0.0152978  |           0.180123  |
| a7ffcore33_005        | F2a_basis_funding_independent     | basis_delta_x_funding            | WinsorZ         | premium_close_bps                  | taker_buy_quote_volume |   0.0118417  |           0.418207  |
| a7ffcore33_006        | F1b_taker_flow_market_panel       | taker_flow_x_liquidity           | Delta           | trade_volume                       | premium_close_bps      |   0.0112295  |           0.658019  |
| a7ffcore33_007        | F1a_aggtrades_flow_microstructure | flow_x_low_turnover              | TSRank          | agg_signed_aggressor_notional      | premium_index_bps      |   0.0167541  |           0.0136915 |
| a7ffcore33_008        | F1a_aggtrades_flow_microstructure | flow_x_low_turnover              | Delta           | agg_large_notional_ratio_100k_plus | premium_index_bps      |   0.020876   |           0.179445  |
| a7ffcore33_009        | F2a_basis_funding_independent     | funding_persistence_low_turnover | WinsorZ         | funding_rate                       | trade_volume           |   0.0137844  |           0.161448  |
| a7ffcore33_010        | F2a_basis_funding_independent     | funding_persistence_low_turnover | Delta           | funding_rate                       | trade_quote_volume     |   0.0101673  |           0.554471  |
| a7ffcore33_011        | F2a_basis_funding_independent     | basis_x_flow                     | Delta           | premium_close                      | trade_quote_volume     |   0.00774844 |           0.237843  |
| a7ffcore33_012        | F1b_taker_flow_market_panel       | taker_flow_x_basis               | WinsorZ         | trade_volume                       | premium_close_bps      |   0.0042023  |           0.384108  |
| a7ffcore33_013        | F2a_basis_funding_independent     | basis_delta_x_funding            | Delta           | mark_index_basis_bps               | trade_volume           |   0.00338079 |           0.329188  |
| a7ffcore33_014        | F1b_taker_flow_market_panel       | low_turnover_flow_state          | WinsorZ         | trade_quote_volume                 | funding_rate           |   0.0110418  |           0.672046  |
| a7ffcore33_015        | F1a_aggtrades_flow_microstructure | flow_reversal                    | TSRank          | agg_signed_aggressor_notional      | mark_index_basis_bps   |   0.00889689 |           0.615915  |
| a7ffcore33_016        | F1a_aggtrades_flow_microstructure | flow_x_dislocation               | TSRank          | agg_large_notional_ratio_100k_plus | agg_price_range_bps    |   0.0148567  |           0.0791233 |
| a7ffcore33_017        | F1a_aggtrades_flow_microstructure | flow_x_dislocation               | TSRank          | agg_large_notional_ratio_100k_plus | premium_index_bps      |   0.0125352  |           0.0104259 |
| a7ffcore33_018        | F1a_aggtrades_flow_microstructure | flow_reversal                    | WinsorZ         | agg_signed_aggressor_notional      | mark_index_basis_bps   |   0.012175   |           0.155522  |
| a7ffcore33_019        | F1b_taker_flow_market_panel       | taker_flow_x_liquidity           | ZScore          | trade_quote_volume                 | funding_rate           |   0.00942396 |           0.105082  |
| a7ffcore33_020        | F1a_aggtrades_flow_microstructure | flow_reversal                    | TSRank          | agg_max_trade_notional             | mark_index_basis_bps   |   0.00807632 |           0.0229927 |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE33E bounded replay execution": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core33e_bounded_replay": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE33_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE33E",
  "executes_replay": false,
  "executes_search": false,
  "family_count": 3,
  "generated_at": "2026-06-01T19:06:07Z",
  "next_allowed": "A7FF-CORE33E bounded replay execution",
  "replay_candidate_count": 21,
  "source_decision": "PASS_A7FFCORE32E_REPLAY_PREFLIGHT_READY_FOR_CORE33_CONTRACT",
  "source_stage": "A7FF-CORE32E",
  "stage": "A7FF-CORE33"
}
```
