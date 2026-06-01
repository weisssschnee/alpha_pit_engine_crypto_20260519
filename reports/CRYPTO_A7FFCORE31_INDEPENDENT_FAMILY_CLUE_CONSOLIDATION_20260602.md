# CRYPTO A7FF-CORE31 INDEPENDENT FAMILY CLUE CONSOLIDATION

Generated: 2026-06-01T18:55:09Z

## Decision

`PASS_A7FFCORE31_CLUE_CONSOLIDATION_READY_FOR_CORE32_REPLAY_PREFLIGHT_CONTRACT`

CORE31 consolidates bounded numeric clues into a replay-preflight candidate queue. It does not execute replay, search, large search, alpha proof, shadow, paper, or live.

## Summary

- selected_clue_count: `113`
- cluster_count: `113`
- family_count: `3`
- replay_preflight_queue_count: `24`

## Gate Audit

| gate                          | threshold   |   observed | pass   |
|:------------------------------|:------------|-----------:|:-------|
| selected_clue_count           | >= 24       | 113        | True   |
| selected_family_count         | >= 3        |   3        | True   |
| cluster_count                 | >= 12       | 113        | True   |
| replay_queue_count            | >= 18       |  24        | True   |
| replay_queue_family_count     | >= 3        |   3        | True   |
| top_family_share_replay_queue | <= 0.50     |   0.333333 | True   |

## Family Summary

| family_id                         |   clue_count |   cluster_count |   median_control_ratio |   median_ic |    max_ic |
|:----------------------------------|-------------:|----------------:|-----------------------:|------------:|----------:|
| F1a_aggtrades_flow_microstructure |           56 |              56 |               0.279541 |  0.0186309  | 0.0386704 |
| F1b_taker_flow_market_panel       |           28 |              28 |               0.405793 |  0.0119605  | 0.0434873 |
| F2a_basis_funding_independent     |           29 |              29 |               0.404108 |  0.00789751 | 0.0164739 |

## Replay Queue Family Summary

| family_id                         |   replay_preflight_candidate_count |   cluster_count |   median_control_ratio |   median_ic |
|:----------------------------------|-----------------------------------:|----------------:|-----------------------:|------------:|
| F1a_aggtrades_flow_microstructure |                                  8 |               8 |               0.121165 |   0.0222737 |
| F1b_taker_flow_market_panel       |                                  8 |               8 |               0.247276 |   0.0137988 |
| F2a_basis_funding_independent     |                                  8 |               8 |               0.343755 |   0.0121263 |

## Concentration Audit

| metric                           |      value |
|:---------------------------------|-----------:|
| top_family_share_selected_clues  | 0.495575   |
| top_cluster_share_selected_clues | 0.00884956 |
| top_family_share_replay_queue    | 0.333333   |
| top_cluster_share_replay_queue   | 0.0416667  |

## Replay Preflight Queue Preview

| numeric_probe_id   | family_id                         |   max_oriented_ic |   max_oriented_spread |   min_control_ratio |   clean_label_count |   eval_rows | candidate_id     | dataset                       | motif                            | operator        | primary_field                      | partner_field          |   window_h | expression                                                                                      | cluster_key                                                                                                        |   quality_score | replay_preflight_role                   | executes_replay   |
|:-------------------|:----------------------------------|------------------:|----------------------:|--------------------:|--------------------:|------------:|:-----------------|:------------------------------|:---------------------------------|:----------------|:-----------------------------------|:-----------------------|-----------:|:------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------|----------------:|:----------------------------------------|:------------------|
| a7ffcore30_0028    | F1a_aggtrades_flow_microstructure |        0.0330341  |             0.0853606 |           0.181799  |                   9 |        8886 | a7ffcore29e_0035 | core12_aggtrades_all_features | flow_x_dislocation               | TSRank          | agg_large_notional_ratio_100k_plus | premium_index_bps      |          4 | TSRank(agg_large_notional_ratio_100k_plus,4)*ZScore(Delta(premium_index_bps,4))                 | F1a_aggtrades_flow_microstructure|flow_x_dislocation|TSRank|agg_large_notional_ratio_100k_plus|premium_index_bps   |         97.3944 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0031    | F1a_aggtrades_flow_microstructure |        0.0320523  |             0.192387  |           0.229452  |                   9 |        9030 | a7ffcore29e_0111 | core12_aggtrades_all_features | flow_x_dislocation               | TSRank          | agg_large_notional_ratio_100k_plus | agg_price_range_bps    |          8 | TSRank(agg_large_notional_ratio_100k_plus,8)*ZScore(Delta(agg_price_range_bps,8))               | F1a_aggtrades_flow_microstructure|flow_x_dislocation|TSRank|agg_large_notional_ratio_100k_plus|agg_price_range_bps |         97.058  | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0014    | F1a_aggtrades_flow_microstructure |        0.0217793  |             0.135965  |           0.0384799 |                   9 |        9030 | a7ffcore29e_0072 | core12_aggtrades_all_features | flow_reversal                    | WinsorZ         | agg_signed_aggressor_notional      | mark_index_basis_bps   |         24 | Clip(ZScore(Delta(agg_signed_aggressor_notional,24)),-3,3)*Sign(Delta(mark_index_basis_bps,24)) | F1a_aggtrades_flow_microstructure|flow_reversal|WinsorZ|agg_signed_aggressor_notional|mark_index_basis_bps         |         96.9855 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0008    | F1a_aggtrades_flow_microstructure |        0.0224852  |             0.0388048 |           0.0548475 |                   9 |        9030 | a7ffcore29e_0010 | core12_aggtrades_all_features | flow_reversal                    | TSRank          | agg_max_trade_notional             | mark_index_basis_bps   |          4 | TSRank(agg_max_trade_notional,4)*ZScore(Delta(mark_index_basis_bps,4))                          | F1a_aggtrades_flow_microstructure|flow_reversal|TSRank|agg_max_trade_notional|mark_index_basis_bps                 |         96.9743 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0011    | F1a_aggtrades_flow_microstructure |        0.0220621  |             0.0671471 |           0.0605304 |                   9 |        9030 | a7ffcore29e_0136 | core12_aggtrades_all_features | flow_reversal                    | TSRank          | agg_signed_aggressor_notional      | mark_index_basis_bps   |          8 | TSRank(agg_signed_aggressor_notional,8)*ZScore(Delta(mark_index_basis_bps,8))                   | F1a_aggtrades_flow_microstructure|flow_reversal|TSRank|agg_signed_aggressor_notional|mark_index_basis_bps          |         96.9036 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0041    | F1a_aggtrades_flow_microstructure |        0.0172383  |             0.0650903 |           0.0489872 |                   9 |        8886 | a7ffcore29e_0051 | core12_aggtrades_all_features | flow_x_low_turnover              | Delta           | agg_large_notional_ratio_100k_plus | premium_index_bps      |          8 | Delta(agg_large_notional_ratio_100k_plus,8)*ZScore(Delta(premium_index_bps,8))                  | F1a_aggtrades_flow_microstructure|flow_x_low_turnover|Delta|agg_large_notional_ratio_100k_plus|premium_index_bps   |         96.4789 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0019    | F1a_aggtrades_flow_microstructure |        0.0338372  |             0.143456  |           0.390003  |                   9 |        8886 | a7ffcore29e_0131 | core12_aggtrades_all_features | flow_reversal                    | ZScore          | agg_large_notional_ratio_100k_plus | premium_index_bps      |          8 | ZScore(agg_large_notional_ratio_100k_plus,8)*ZScore(Delta(premium_index_bps,8))                 | F1a_aggtrades_flow_microstructure|flow_reversal|ZScore|agg_large_notional_ratio_100k_plus|premium_index_bps        |         96.4337 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0051    | F1a_aggtrades_flow_microstructure |        0.0203867  |             0.0494303 |           0.18374   |                   9 |        8886 | a7ffcore29e_0112 | core12_aggtrades_all_features | flow_x_low_turnover              | TSRank          | agg_signed_aggressor_notional      | premium_index_bps      |         24 | TSRank(agg_signed_aggressor_notional,24)*ZScore(Delta(premium_index_bps,24))                    | F1a_aggtrades_flow_microstructure|flow_x_low_turnover|TSRank|agg_signed_aggressor_notional|premium_index_bps       |         96.12   | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0134    | F1b_taker_flow_market_panel       |        0.0398347  |             0.120055  |           0.573142  |                   9 |      252906 | a7ffcore29e_0207 | top498_replay_v2              | taker_flow_x_liquidity           | WinsorZ         | trade_volume                       | trade_quote_volume     |         24 | Clip(ZScore(Delta(trade_volume,24)),-3,3)*Sign(Delta(trade_quote_volume,24))                    | F1b_taker_flow_market_panel|taker_flow_x_liquidity|WinsorZ|trade_volume|trade_quote_volume                         |         96.1178 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0102    | F1b_taker_flow_market_panel       |        0.0188396  |             0.0765715 |           0.217774  |                   9 |       36812 | a7ffcore29e_0235 | top498_replay_v2              | taker_flow_x_basis               | Delta           | trade_volume                       | funding_rate           |          4 | Delta(trade_volume,4)*ZScore(Delta(funding_rate,4))                                             | F1b_taker_flow_market_panel|taker_flow_x_basis|Delta|trade_volume|funding_rate                                     |         95.7951 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0183    | F2a_basis_funding_independent     |        0.00511623 |             0.0559739 |           0.0313792 |                   9 |      252652 | a7ffcore29e_0396 | top498_replay_v2              | basis_delta_x_funding            | Delta           | mark_index_basis_bps               | trade_volume           |          8 | Delta(mark_index_basis_bps,8)*ZScore(Delta(trade_volume,8))                                     | F2a_basis_funding_independent|basis_delta_x_funding|Delta|mark_index_basis_bps|trade_volume                        |         95.3547 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0163    | F2a_basis_funding_independent     |        0.0158873  |             0.0285665 |           0.295654  |                   9 |       49044 | a7ffcore29e_0446 | top498_replay_v2              | H8_H24_dislocation               | Delta           | funding_rate                       | trade_volume           |          8 | Delta(funding_rate,8)*ZScore(Delta(trade_volume,8))                                             | F2a_basis_funding_independent|H8_H24_dislocation|Delta|funding_rate|trade_volume                                   |         95.1105 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0113    | F1b_taker_flow_market_panel       |        0.00997094 |             0.0728295 |           0.178204  |                   9 |      252918 | a7ffcore29e_0231 | top498_replay_v2              | taker_flow_x_basis               | WinsorZ         | trade_volume                       | premium_close_bps      |          8 | Clip(ZScore(Delta(trade_volume,8)),-3,3)*Sign(Delta(premium_close_bps,8))                       | F1b_taker_flow_market_panel|taker_flow_x_basis|WinsorZ|trade_volume|premium_close_bps                              |         95.1061 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0092    | F1b_taker_flow_market_panel       |        0.00527051 |             0.031496  |           0.126942  |                   9 |      251387 | a7ffcore29e_0208 | top498_replay_v2              | low_turnover_flow_state          | WinsorZ         | kline_taker_buy_quote_share        | mark_index_basis_bps   |         72 | Clip(ZScore(Delta(kline_taker_buy_quote_share,72)),-3,3)*Sign(Delta(mark_index_basis_bps,72))   | F1b_taker_flow_market_panel|low_turnover_flow_state|WinsorZ|kline_taker_buy_quote_share|mark_index_basis_bps       |         94.8923 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0094    | F1b_taker_flow_market_panel       |        0.0125441  |             0.0874071 |           0.276778  |                   9 |       49044 | a7ffcore29e_0281 | top498_replay_v2              | low_turnover_flow_state          | WinsorZ         | taker_buy_quote_volume             | funding_rate           |          8 | Clip(ZScore(Delta(taker_buy_quote_volume,8)),-3,3)*Sign(Delta(funding_rate,8))                  | F1b_taker_flow_market_panel|low_turnover_flow_state|WinsorZ|taker_buy_quote_volume|funding_rate                    |         94.8705 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0195    | F2a_basis_funding_independent     |        0.0120862  |             0.0877237 |           0.391856  |                   9 |      251782 | a7ffcore29e_0393 | top498_replay_v2              | basis_delta_x_funding            | WinsorZ         | premium_close_bps                  | taker_buy_quote_volume |         72 | Clip(ZScore(Delta(premium_close_bps,72)),-3,3)*Sign(Delta(taker_buy_quote_volume,72))           | F2a_basis_funding_independent|basis_delta_x_funding|WinsorZ|premium_close_bps|taker_buy_quote_volume               |         94.2493 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0222    | F2a_basis_funding_independent     |        0.0133018  |             0.0851465 |           0.417903  |                   9 |       48940 | a7ffcore29e_0422 | top498_replay_v2              | funding_persistence_low_turnover | Delta           | funding_rate                       | trade_quote_volume     |         24 | Delta(funding_rate,24)*ZScore(Delta(trade_quote_volume,24))                                     | F2a_basis_funding_independent|funding_persistence_low_turnover|Delta|funding_rate|trade_quote_volume               |         94.2407 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0201    | F2a_basis_funding_independent     |        0.0121664  |             0.0578484 |           0.404108  |                   9 |       49044 | a7ffcore29e_0346 | top498_replay_v2              | basis_x_flow                     | Delta           | funding_rate                       | taker_buy_quote_volume |          8 | Delta(funding_rate,8)*ZScore(Delta(taker_buy_quote_volume,8))                                   | F2a_basis_funding_independent|basis_x_flow|Delta|funding_rate|taker_buy_quote_volume                               |         94.1961 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0187    | F2a_basis_funding_independent     |        0.0118174  |             0.0565328 |           0.415256  |                   9 |      252566 | a7ffcore29e_0460 | top498_replay_v2              | basis_delta_x_funding            | SpreadShortLong | mark_index_basis_bps               | trade_volume           |          4 | Sub(ZScore(Mean(mark_index_basis_bps,4)),ZScore(Mean(trade_volume,16)))                         | F2a_basis_funding_independent|basis_delta_x_funding|SpreadShortLong|mark_index_basis_bps|trade_volume              |         94.1055 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0095    | F1b_taker_flow_market_panel       |        0.0150535  |             0.0759986 |           0.501775  |                   9 |       48940 | a7ffcore29e_0282 | top498_replay_v2              | low_turnover_flow_state          | WinsorZ         | trade_quote_volume                 | funding_rate           |         24 | Clip(ZScore(Delta(trade_quote_volume,24)),-3,3)*Sign(Delta(funding_rate,24))                    | F1b_taker_flow_market_panel|low_turnover_flow_state|WinsorZ|trade_quote_volume|funding_rate                        |         93.9965 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0123    | F1b_taker_flow_market_panel       |        0.0120529  |             0.0700904 |           0.740268  |                   9 |      251782 | a7ffcore29e_0263 | top498_replay_v2              | taker_flow_x_liquidity           | Delta           | trade_volume                       | premium_close_bps      |         72 | Delta(trade_volume,72)*ZScore(Delta(premium_close_bps,72))                                      | F1b_taker_flow_market_panel|taker_flow_x_liquidity|Delta|trade_volume|premium_close_bps                            |         92.5039 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0138    | F1b_taker_flow_market_panel       |        0.0172539  |             0.179017  |           0.170604  |                   6 |       49010 | a7ffcore29e_0266 | top498_replay_v2              | taker_flow_x_liquidity           | ZScore          | trade_quote_volume                 | funding_rate           |          8 | ZScore(trade_quote_volume,8)*ZScore(Delta(funding_rate,8))                                      | F1b_taker_flow_market_panel|taker_flow_x_liquidity|ZScore|trade_quote_volume|funding_rate                          |         65.8724 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0233    | F2a_basis_funding_independent     |        0.0125961  |             0.148026  |           0.165166  |                   6 |       49010 | a7ffcore29e_0366 | top498_replay_v2              | funding_persistence_low_turnover | WinsorZ         | funding_rate                       | trade_volume           |          8 | Clip(ZScore(Delta(funding_rate,8)),-3,3)*Sign(Delta(trade_volume,8))                            | F2a_basis_funding_independent|funding_persistence_low_turnover|WinsorZ|funding_rate|trade_volume                   |         65.4338 | candidate_for_replay_preflight_contract | False             |
| a7ffcore30_0203    | F2a_basis_funding_independent     |        0.00789746 |             0.0798745 |           0.090128  |                   6 |      252918 | a7ffcore29e_0471 | top498_replay_v2              | basis_x_flow                     | Delta           | premium_close                      | trade_quote_volume     |          8 | Delta(premium_close,8)*ZScore(Delta(trade_quote_volume,8))                                      | F2a_basis_funding_independent|basis_x_flow|Delta|premium_close|trade_quote_volume                                  |         65.3391 | candidate_for_replay_preflight_contract | False             |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core32_contract": true,
  "authorizes_large_search": false,
  "authorizes_replay_execution": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "cluster_count": 113,
  "decision": "PASS_A7FFCORE31_CLUE_CONSOLIDATION_READY_FOR_CORE32_REPLAY_PREFLIGHT_CONTRACT",
  "executes_replay": false,
  "executes_search": false,
  "family_count": 3,
  "generated_at": "2026-06-01T18:55:09Z",
  "next_allowed": "A7FF-CORE32 replay preflight contract",
  "replay_preflight_queue_count": 24,
  "selected_clue_count": 113,
  "source_decision": "PASS_A7FFCORE30E_NUMERIC_PROBE_CLUES_READY_FOR_CORE31_CONTRACT",
  "source_stage": "A7FF-CORE30E",
  "stage": "A7FF-CORE31"
}
```
