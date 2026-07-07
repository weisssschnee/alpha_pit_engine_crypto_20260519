# CRYPTO A7V3S9 Pre-Reward OOS/Control Proxy Aggregate 20260614

Decision: `PASS_A7V3S9_PROXY_AGGREGATE_SELECTED`

## Counts

- expected_shards: `64`
- manifest_count: `64`
- leaderboard_rows: `16384`
- eval_error_rows: `0`
- strict_pass_rows: `23`
- near_miss_rows: `131`
- selected_rows: `102`

## Bucket Summary

| proxy_bucket    |   count |
|:----------------|--------:|
| proxy_reject    |   16253 |
| proxy_near_miss |     108 |
| proxy_pass      |      23 |

## Selected Pairs

| semantic_pair               |   count |
|:----------------------------|--------:|
| open_interest|positioning   |      24 |
| positioning|positioning     |      15 |
| funding_dense|open_interest |      14 |
| open_interest|premium       |      10 |
| positioning|regime          |      10 |
| positioning|taker_flow      |       8 |
| basis|open_interest         |       6 |
| liquidity|positioning       |       4 |
| basis|positioning           |       3 |
| funding_dense|positioning   |       3 |
| funding_basis|positioning   |       2 |
| basis|funding_dense         |       1 |
| basis|basis                 |       1 |
| basis|funding_basis         |       1 |

## Selected Motifs

| motif                        |   count |
|:-----------------------------|--------:|
| positive_prior_safe_div_rank |      16 |
| positive_prior_signed_rank   |      14 |
| positive_prior_safe_div_abs  |      14 |
| raw_add_rank                 |       9 |
| raw_signed_gate              |       7 |
| raw_rank_mul                 |       6 |
| shadow_selected_rank_wrap    |       5 |
| shadow_selected_exact_probe  |       5 |
| flow_liquidity_rank_mul      |       4 |
| regime_conditioned_scaled    |       4 |
| regime_conditioned_rank      |       4 |
| raw_safe_div_abs             |       4 |
| funding_basis_spread         |       3 |
| raw_spread_rank              |       2 |
| funding_basis_state_mul      |       2 |
| regime_conditioned_sign      |       2 |
| flow_liquidity_scaled        |       1 |

## Top Selected

| blueprint_id               | semantic_pair               | motif                        |   horizon_h | proxy_bucket    |   proxy_score |   recent_sortino |   min_oos_floor_sortino |   stress_floor_sortino |   recent_shuffle_control_ratio | expression                                                                                                          |
|:---------------------------|:----------------------------|:-----------------------------|------------:|:----------------|--------------:|-----------------:|------------------------:|-----------------------:|-------------------------------:|:--------------------------------------------------------------------------------------------------------------------|
| a7search7_1579560a060d20ec | funding_dense|open_interest | shadow_selected_exact_probe  |           8 | proxy_pass      |      37.3388  |         18.3882  |               8.50321   |               1.27322  |                     0.39088    | CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))))         |
| a7search7_9168babaa32dc76c | funding_dense|open_interest | shadow_selected_rank_wrap    |           8 | proxy_pass      |      37.3388  |         18.3882  |               8.50321   |               1.27322  |                     0.148847   | CSRank(CSRank(SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))))) |
| a7search7_f75f5679c40c117e | open_interest|positioning   | positive_prior_safe_div_abs  |          24 | proxy_pass      |      30.585   |         14.1533  |               5.45308   |               2.83757  |                     0.0845035  | SafeDiv(ZScore(open_interest_value_last),Abs(Decay(account_position_divergence,24)))                                |
| a7search7_2c3057f692b8365e | open_interest|positioning   | positive_prior_safe_div_rank |           8 | proxy_pass      |      27.3277  |          9.22695 |               3.95617   |               4.25648  |                     0.252803   | SafeDiv(TSRank(open_interest_value_last,240),CSRank(Delta(top_long_short_position_ratio_last,240)))                 |
| a7search7_37c11ae930ea6da0 | open_interest|positioning   | positive_prior_safe_div_rank |           8 | proxy_pass      |      26.6695  |         11.4036  |               3.95484   |               3.37854  |                     0.332685   | SafeDiv(ZScore(Mean(open_interest_value_last,48)),CSRank(top_long_short_account_ratio_last))                        |
| a7search7_37c11ae930ea6da0 | open_interest|positioning   | positive_prior_safe_div_rank |          24 | proxy_pass      |      25.2134  |         12.6552  |               3.351     |               1.5154   |                     0.0561731  | SafeDiv(ZScore(Mean(open_interest_value_last,48)),CSRank(top_long_short_account_ratio_last))                        |
| a7search7_ba69d19a8c649556 | open_interest|positioning   | positive_prior_safe_div_rank |           8 | proxy_pass      |      24.3338  |         11.5952  |               4.27917   |               1.40601  |                     0.44494    | SafeDiv(TSRank(open_interest_value_last,240),CSRank(Decay(global_long_short_account_ratio_last,504)))               |
| a7search7_4e22e196bfeb8bce | open_interest|positioning   | positive_prior_safe_div_abs  |          24 | proxy_pass      |      23.066   |         16.2218  |               1.06354   |               8.19878  |                     0.316695   | SafeDiv(Delta(open_interest_value_last,240),Abs(ZScore(Mean(global_long_short_account_ratio_last,96))))             |
| a7search7_bd1d959f8579aa9b | open_interest|positioning   | positive_prior_safe_div_rank |          24 | proxy_pass      |      20.8928  |         14.0387  |               3.92251   |               0.269601 |                     0.153251   | SafeDiv(CSRank(Delta(open_interest_value_last,240)),CSRank(Mean(global_long_short_account_ratio_last,96)))          |
| a7search7_e7180b1ba6a1df1a | funding_dense|open_interest | shadow_selected_exact_probe  |          24 | proxy_pass      |      20.5965  |         12.0121  |               0.497889  |               6.40622  |                     0.201243   | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72)))                       |
| a7search7_52353a2ad0ece8e8 | funding_dense|open_interest | shadow_selected_rank_wrap    |          24 | proxy_pass      |      20.5965  |         12.0121  |               0.497889  |               6.40622  |                     0.109697   | CSRank(Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(Decay(mark_index_basis_bps,72))))               |
| a7search7_d404a68b39d27dbd | funding_dense|open_interest | shadow_selected_exact_probe  |          24 | proxy_pass      |      20.3112  |         12.6676  |               0.318659  |               7.40948  |                     0.00986138 | Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12))))               |
| a7search7_124582cf9a6d54a0 | funding_dense|open_interest | shadow_selected_rank_wrap    |          24 | proxy_pass      |      20.3112  |         12.6676  |               0.318659  |               7.40948  |                     0.35457    | CSRank(Mul(CSRank(CSRank(Delta(open_interest_value_mean,240))),Sign(CSRank(Delta(mark_index_basis_bps,12)))))       |
| a7search7_b2e42dec52899bd0 | funding_dense|open_interest | shadow_selected_exact_probe  |          24 | proxy_pass      |      20.2318  |         12.6676  |               0.318659  |               7.40948  |                     0.087228   | Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504)))                                |
| a7search7_8ecc4a9a053a0d59 | funding_dense|open_interest | shadow_selected_rank_wrap    |          24 | proxy_pass      |      20.2318  |         12.6676  |               0.318659  |               7.40948  |                     0.225111   | CSRank(Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,504))))                        |
| a7search7_67dc50bd046872a3 | open_interest|premium       | positive_prior_signed_rank   |          24 | proxy_pass      |      20.2318  |         12.6676  |               0.318659  |               7.40948  |                     0.0101282  | Mul(CSRank(Delta(open_interest_value_mean,240)),Sign(TSRank(premium_abs_state,240)))                                |
| a7search7_09c0989e6ce981f1 | open_interest|positioning   | positive_prior_safe_div_rank |           8 | proxy_pass      |      17.7214  |         10.6782  |               0.0389259 |              10.1879   |                     0.43798    | SafeDiv(CSRank(Delta(open_interest_value_mean,240)),CSRank(Delta(global_long_short_account_ratio_last,168)))        |
| a7search7_4647205ea0246251 | open_interest|premium       | positive_prior_signed_rank   |          24 | proxy_pass      |      17.5037  |          2.8671  |               1.71103   |               3.5541   |                     0.478769   | Mul(CSRank(Mean(open_interest_mean,12)),Sign(Mean(premium_close_bps,168)))                                          |
| a7search7_fa2bcb9f82277249 | funding_dense|open_interest | shadow_selected_exact_probe  |           8 | proxy_pass      |      16.2631  |          4.08333 |               2.11649   |               0.860626 |                     0.335554   | SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24)))                  |
| a7search7_f57e92c650f903b6 | funding_dense|open_interest | shadow_selected_rank_wrap    |           8 | proxy_pass      |      16.2631  |          4.08333 |               2.11649   |               0.860626 |                     0.496774   | CSRank(SafeDiv(TSRank(open_interest_value_mean,240),Abs(TSRank(global_long_short_account_ratio_last,24))))          |
| a7search7_fd8d40c9266d7142 | positioning|regime          | regime_conditioned_sign      |          24 | proxy_pass      |      13.7611  |         16.8943  |               0.373399  |               5.15979  |                     0.149712   | Mul(CSRank(ZScore(global_long_short_account_ratio_last)),Sign(Mean(liquidity_cycle_state,336)))                     |
| a7search7_5b09e223680c431d | funding_basis|positioning   | funding_basis_state_mul      |          24 | proxy_pass      |      13.5456  |         12.534   |               1.23627   |               1.51107  |                     0.152444   | Mul(ZScore(Mean(funding_state_x_basis_delta,240)),TSRank(Mean(top_long_short_account_ratio_last,504),24))           |
| a7search7_d53ef56f26e0c5b4 | open_interest|positioning   | positive_prior_safe_div_abs  |          24 | proxy_pass      |       9.72339 |         15.5683  |               0.175593  |               1.03571  |                     0.0212703  | SafeDiv(Mean(open_interest_value_mean,4),Abs(Decay(account_position_divergence,96)))                                |
| a7search7_2423aa9b0add87bc | open_interest|positioning   | positive_prior_safe_div_abs  |           8 | proxy_near_miss |      41.4454  |         18.1146  |              11.9195    |               5.83853  |                     0.181369   | SafeDiv(TSRank(open_interest_value_mean,336),Abs(Mean(account_position_divergence,96)))                             |
| a7search7_96bf10495ae8bb22 | open_interest|positioning   | positive_prior_safe_div_abs  |          24 | proxy_near_miss |      38.7178  |         17.6098  |               8.6261    |               7.63314  |                     0.0915948  | SafeDiv(CSRank(Delta(open_interest_value_last,240)),Abs(Mean(account_position_divergence,12)))                      |
| a7search7_62a58e6cf94ec5f7 | open_interest|positioning   | positive_prior_safe_div_rank |           8 | proxy_near_miss |      31.0923  |         17.7821  |               5.8073    |               8.01116  |                     0.199443   | SafeDiv(TSRank(open_interest_value_mean,504),CSRank(Mean(global_long_short_account_ratio_last,48)))                 |
| a7search7_2423aa9b0add87bc | open_interest|positioning   | positive_prior_safe_div_abs  |          24 | proxy_near_miss |      30.5057  |         20.9393  |               6.08195   |               2.73925  |                     0.0377212  | SafeDiv(TSRank(open_interest_value_mean,336),Abs(Mean(account_position_divergence,96)))                             |
| a7search7_4203b1df7f337838 | open_interest|positioning   | positive_prior_safe_div_abs  |           8 | proxy_near_miss |      30.0371  |          8.66941 |               7.30527   |               3.1137   |                     0.326242   | SafeDiv(ZScore(Mean(open_interest_value_last,504)),Abs(Mean(account_position_divergence,48)))                       |
| a7search7_4322ceaddf5bee38 | open_interest|positioning   | positive_prior_safe_div_rank |           8 | proxy_near_miss |      29.9479  |         19.6041  |               4.06583   |               9.93942  |                     0.23474    | SafeDiv(TSRank(open_interest_value_last,336),CSRank(Decay(global_long_short_account_ratio_last,12)))                |
| a7search7_c918f24e6bcc64dd | open_interest|positioning   | positive_prior_safe_div_abs  |           8 | proxy_near_miss |      29.04    |         10.7469  |               6.07175   |               3.23709  |                     0.151645   | SafeDiv(ZScore(Mean(open_interest_value_last,504)),Abs(Abs(global_long_short_account_ratio_last)))                  |

## Boundary

This aggregate can authorize only bounded full reward on the selected proxy queue. It does not authorize alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_bounded_full_reward": true,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7V3S9_PROXY_AGGREGATE_SELECTED",
  "eval_error_rows": 0,
  "expected_shards": 64,
  "generated_at": "2026-07-07T14:38:28Z",
  "leaderboard_rows": 16384,
  "manifest_count": 64,
  "near_miss_rows": 131,
  "report": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\reports\\CRYPTO_A7SEARCH8_SEED_EXPANSION_PROXY_AGGREGATE_20260707.md",
  "run_root": "D:\\HermesWorker\\runtime\\a7search8_seed_expansion_proxy_20260706",
  "runtime": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7search8_seed_expansion_proxy_aggregate_20260707",
  "selected_queue": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7search8_seed_expansion_proxy_aggregate_20260707\\a7v3s9_proxy_selected_for_reward.csv",
  "selected_rows": 102,
  "selected_unique_blueprints": 95,
  "stage": "A7V3S9_PROXY_AGGREGATE",
  "strict_pass_rows": 23
}
```
