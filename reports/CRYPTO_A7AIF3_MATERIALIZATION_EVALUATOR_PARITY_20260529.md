# CRYPTO A7AI-F3 MATERIALIZATION EVALUATOR PARITY

Generated: 2026-06-02T01:17:24Z

## Decision

`PASS_A7AIF3_REPLAY_MATERIALIZATION_PARITY_READY`

## Field Materialization

| field_name                           | semantic_role                         | ordinary_alpha_allowed   | diagnostic_allowed   | risk_defense_allowed   | resolution   | error   |
|:-------------------------------------|:--------------------------------------|:-------------------------|:---------------------|:-----------------------|:-------------|:--------|
| global_long_short_account_ratio_last | risk_exposure_or_control_like         | False                    | False                | True                   | resolved     |         |
| global_long_short_account_ratio_mean | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| index_close                          | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| kline_taker_buy_quote_share          | regime_state_or_interaction_input     | False                    | True                 | False                  | resolved     |         |
| mark_close                           | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| mark_high                            | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| mark_index_basis_bps                 | ordinary_signal_candidate             | True                     | False                | False                  | resolved     |         |
| mark_low                             | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| mark_trade_basis_bps                 | regime_state_or_interaction_input     | False                    | True                 | False                  | resolved     |         |
| oi_x_price_move_24h                  | risk_exposure_or_control_like         | False                    | False                | True                   | resolved     |         |
| open_interest_change_24h             | risk_exposure_or_control_like         | False                    | False                | True                   | resolved     |         |
| open_interest_last                   | risk_exposure_or_control_like         | False                    | False                | True                   | resolved     |         |
| open_interest_mean                   | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| open_interest_value_last             | risk_exposure_or_control_like         | False                    | False                | True                   | resolved     |         |
| open_interest_value_mean             | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| premium_close                        | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| premium_close_bps                    | diagnostic_rank_or_nonordinary_signal | False                    | True                 | False                  | resolved     |         |
| realized_vol_168h                    | diagnostic_rank_or_nonordinary_signal | False                    | True                 | False                  | resolved     |         |
| realized_vol_24h                     | diagnostic_rank_or_nonordinary_signal | False                    | True                 | False                  | resolved     |         |
| taker_buy_quote_volume               | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| taker_buy_sell_volume_ratio_last     | regime_state_or_interaction_input     | False                    | True                 | False                  | resolved     |         |
| taker_buy_sell_volume_ratio_mean     | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| top_long_short_account_ratio_last    | risk_exposure_or_control_like         | False                    | False                | True                   | resolved     |         |
| top_long_short_account_ratio_mean    | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| top_long_short_position_ratio_last   | risk_exposure_or_control_like         | False                    | False                | True                   | resolved     |         |
| top_long_short_position_ratio_mean   | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| trade_close                          | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| trade_high                           | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| trade_low                            | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |
| trade_return_1h                      | diagnostic_rank_or_nonordinary_signal | False                    | True                 | False                  | resolved     |         |
| trade_return_24h                     | risk_exposure_or_control_like         | False                    | False                | True                   | resolved     |         |
| trade_volume                         | unclassified_generator_ingredient     | False                    | True                 | False                  | resolved     |         |

## Operator Parity

| operator   | expression                                                           | supported   |   finite_rows |   max_abs_diff_contract_vs_plain | error   | resolution   |
|:-----------|:---------------------------------------------------------------------|:------------|--------------:|---------------------------------:|:--------|:-------------|
| Mean       | Mean(mark_index_basis_bps,4)                                         | True        |           244 |                                0 |         | resolved     |
| Delta      | Delta(mark_index_basis_bps,4)                                        | True        |           240 |                                0 |         | resolved     |
| ZScore     | ZScore(mark_index_basis_bps)                                         | True        |           256 |                                0 |         | resolved     |
| Rank       | Rank(mark_index_basis_bps)                                           | True        |           256 |                                0 |         | resolved     |
| CSRank     | CSRank(mark_index_basis_bps)                                         | True        |           256 |                                0 |         | resolved     |
| Mul        | Mul(ZScore(mark_index_basis_bps),Rank(premium_close_bps))            | True        |           256 |                                0 |         | resolved     |
| Sub        | Sub(ZScore(mark_index_basis_bps),ZScore(premium_close_bps))          | True        |           256 |                                0 |         | resolved     |
| Add        | Add(ZScore(mark_index_basis_bps),ZScore(premium_close_bps))          | True        |           256 |                                0 |         | resolved     |
| Neg        | Neg(ZScore(mark_index_basis_bps))                                    | True        |           256 |                                0 |         | resolved     |
| Abs        | Abs(ZScore(mark_index_basis_bps))                                    | True        |           256 |                                0 |         | resolved     |
| Sign       | Sign(Delta(mark_index_basis_bps,4))                                  | True        |           240 |                                0 |         | resolved     |
| SafeDiv    | SafeDiv(ZScore(mark_index_basis_bps),Abs(ZScore(premium_close_bps))) | True        |           256 |                                0 |         | resolved     |
| Clip       | Clip(ZScore(mark_index_basis_bps),-2,2)                              | True        |           256 |                                0 |         | resolved     |
| TSRank     | TSRank(mark_index_basis_bps,24)                                      | True        |           164 |                                0 |         | resolved     |
| Decay      | Decay(mark_index_basis_bps,24)                                       | True        |           164 |                                0 |         | resolved     |

## Boundary

```text
This is a synthetic materialization/evaluator parity sprint only.
No formula search, full replay, alpha proof, shadow, paper, or live execution is authorized.
```
