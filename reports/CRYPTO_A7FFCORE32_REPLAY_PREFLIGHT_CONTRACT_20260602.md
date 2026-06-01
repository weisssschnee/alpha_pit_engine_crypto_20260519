# CRYPTO A7FF-CORE32 REPLAY PREFLIGHT CONTRACT

Generated: 2026-06-01T18:58:17Z

## Decision

`PASS_A7FFCORE32_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE32E`

CORE32 is a replay-preflight contract. It does not execute tradable replay, search, large search, alpha proof, shadow, paper, or live.

## Gate Audit

| gate             | threshold          | observed                                                                                          | pass   |
|:-----------------|:-------------------|:--------------------------------------------------------------------------------------------------|:-------|
| queue_count      | 24                 | 24                                                                                                | True   |
| family_count     | 3                  | 3                                                                                                 | True   |
| per_family_count | 8 each             | F1a_aggtrades_flow_microstructure:8,F1b_taker_flow_market_panel:8,F2a_basis_funding_independent:8 | True   |
| cluster_unique   | 24 unique clusters | 24                                                                                                | True   |

## Family Balance

| family_id                         |   preflight_count |   cluster_count |   median_control_ratio |   median_ic |
|:----------------------------------|------------------:|----------------:|-----------------------:|------------:|
| F1a_aggtrades_flow_microstructure |                 8 |               8 |               0.121165 |   0.0222737 |
| F1b_taker_flow_market_panel       |                 8 |               8 |               0.247276 |   0.0137988 |
| F2a_basis_funding_independent     |                 8 |               8 |               0.343755 |   0.0121263 |

## Preflight Checks

| check                   | requirement                                                                        | blocking   |
|:------------------------|:-----------------------------------------------------------------------------------|:-----------|
| candidate_rebuild       | re-materialize expression from source datasets, not reuse CORE30E vectors          | True       |
| split_coverage          | train/validation/test/recent coverage by symbol and timestamp                      | True       |
| label_set               | L0/L1/L3/L5/L7 at 4h/8h/24h with L7 diagnostic-only                                | True       |
| controls                | row shuffle, time shuffle, wrong-lag future, stale, sign flip, same-family placebo | True       |
| non_overlap_stats       | offset non-overlap tstats and simple block bootstrap summary                       | True       |
| family_and_cluster_caps | no single family > 40%; no repeated cluster representatives                        | True       |
| turnover_cost_proxy     | 2/5/10 bps proxy and one-bar executable alignment                                  | True       |
| source_boundary         | cross-exchange forward-only and liquidation/orderbook excluded                     | True       |

## Replay Preflight Queue

| preflight_candidate_id   | numeric_probe_id   | family_id                         | motif                            | operator        | primary_field                      | partner_field          |   quality_score |
|:-------------------------|:-------------------|:----------------------------------|:---------------------------------|:----------------|:-----------------------------------|:-----------------------|----------------:|
| a7ffcore32_000           | a7ffcore30_0028    | F1a_aggtrades_flow_microstructure | flow_x_dislocation               | TSRank          | agg_large_notional_ratio_100k_plus | premium_index_bps      |         97.3944 |
| a7ffcore32_001           | a7ffcore30_0031    | F1a_aggtrades_flow_microstructure | flow_x_dislocation               | TSRank          | agg_large_notional_ratio_100k_plus | agg_price_range_bps    |         97.058  |
| a7ffcore32_002           | a7ffcore30_0014    | F1a_aggtrades_flow_microstructure | flow_reversal                    | WinsorZ         | agg_signed_aggressor_notional      | mark_index_basis_bps   |         96.9855 |
| a7ffcore32_003           | a7ffcore30_0008    | F1a_aggtrades_flow_microstructure | flow_reversal                    | TSRank          | agg_max_trade_notional             | mark_index_basis_bps   |         96.9743 |
| a7ffcore32_004           | a7ffcore30_0011    | F1a_aggtrades_flow_microstructure | flow_reversal                    | TSRank          | agg_signed_aggressor_notional      | mark_index_basis_bps   |         96.9036 |
| a7ffcore32_005           | a7ffcore30_0041    | F1a_aggtrades_flow_microstructure | flow_x_low_turnover              | Delta           | agg_large_notional_ratio_100k_plus | premium_index_bps      |         96.4789 |
| a7ffcore32_006           | a7ffcore30_0019    | F1a_aggtrades_flow_microstructure | flow_reversal                    | ZScore          | agg_large_notional_ratio_100k_plus | premium_index_bps      |         96.4337 |
| a7ffcore32_007           | a7ffcore30_0051    | F1a_aggtrades_flow_microstructure | flow_x_low_turnover              | TSRank          | agg_signed_aggressor_notional      | premium_index_bps      |         96.12   |
| a7ffcore32_008           | a7ffcore30_0134    | F1b_taker_flow_market_panel       | taker_flow_x_liquidity           | WinsorZ         | trade_volume                       | trade_quote_volume     |         96.1178 |
| a7ffcore32_009           | a7ffcore30_0102    | F1b_taker_flow_market_panel       | taker_flow_x_basis               | Delta           | trade_volume                       | funding_rate           |         95.7951 |
| a7ffcore32_010           | a7ffcore30_0113    | F1b_taker_flow_market_panel       | taker_flow_x_basis               | WinsorZ         | trade_volume                       | premium_close_bps      |         95.1061 |
| a7ffcore32_011           | a7ffcore30_0092    | F1b_taker_flow_market_panel       | low_turnover_flow_state          | WinsorZ         | kline_taker_buy_quote_share        | mark_index_basis_bps   |         94.8923 |
| a7ffcore32_012           | a7ffcore30_0094    | F1b_taker_flow_market_panel       | low_turnover_flow_state          | WinsorZ         | taker_buy_quote_volume             | funding_rate           |         94.8705 |
| a7ffcore32_013           | a7ffcore30_0095    | F1b_taker_flow_market_panel       | low_turnover_flow_state          | WinsorZ         | trade_quote_volume                 | funding_rate           |         93.9965 |
| a7ffcore32_014           | a7ffcore30_0123    | F1b_taker_flow_market_panel       | taker_flow_x_liquidity           | Delta           | trade_volume                       | premium_close_bps      |         92.5039 |
| a7ffcore32_015           | a7ffcore30_0138    | F1b_taker_flow_market_panel       | taker_flow_x_liquidity           | ZScore          | trade_quote_volume                 | funding_rate           |         65.8724 |
| a7ffcore32_016           | a7ffcore30_0183    | F2a_basis_funding_independent     | basis_delta_x_funding            | Delta           | mark_index_basis_bps               | trade_volume           |         95.3547 |
| a7ffcore32_017           | a7ffcore30_0163    | F2a_basis_funding_independent     | H8_H24_dislocation               | Delta           | funding_rate                       | trade_volume           |         95.1105 |
| a7ffcore32_018           | a7ffcore30_0195    | F2a_basis_funding_independent     | basis_delta_x_funding            | WinsorZ         | premium_close_bps                  | taker_buy_quote_volume |         94.2493 |
| a7ffcore32_019           | a7ffcore30_0222    | F2a_basis_funding_independent     | funding_persistence_low_turnover | Delta           | funding_rate                       | trade_quote_volume     |         94.2407 |
| a7ffcore32_020           | a7ffcore30_0201    | F2a_basis_funding_independent     | basis_x_flow                     | Delta           | funding_rate                       | taker_buy_quote_volume |         94.1961 |
| a7ffcore32_021           | a7ffcore30_0187    | F2a_basis_funding_independent     | basis_delta_x_funding            | SpreadShortLong | mark_index_basis_bps               | trade_volume           |         94.1055 |
| a7ffcore32_022           | a7ffcore30_0233    | F2a_basis_funding_independent     | funding_persistence_low_turnover | WinsorZ         | funding_rate                       | trade_volume           |         65.4338 |
| a7ffcore32_023           | a7ffcore30_0203    | F2a_basis_funding_independent     | basis_x_flow                     | Delta           | premium_close                      | trade_quote_volume     |         65.3391 |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE32E replay preflight execution": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "shadow_paper_live": true,
    "tradable_replay": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core32e_preflight": true,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "authorizes_tradable_replay": false,
  "cluster_count": 24,
  "decision": "PASS_A7FFCORE32_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE32E",
  "executes_replay": false,
  "executes_search": false,
  "family_count": 3,
  "generated_at": "2026-06-01T18:58:17Z",
  "next_allowed": "A7FF-CORE32E replay preflight execution",
  "preflight_queue_count": 24,
  "source_decision": "PASS_A7FFCORE31_CLUE_CONSOLIDATION_READY_FOR_CORE32_REPLAY_PREFLIGHT_CONTRACT",
  "source_stage": "A7FF-CORE31",
  "stage": "A7FF-CORE32"
}
```
