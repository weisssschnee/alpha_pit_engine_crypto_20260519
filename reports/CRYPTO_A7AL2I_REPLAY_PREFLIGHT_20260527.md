# CRYPTO A7AL-2I Replay Preflight

Generated: 2026-05-27T10:17:21Z

## Decision

```text
HOLD_A7AL2I_NO_CLUES
```

This is a replay preflight on selected control-gated candidates. It does not execute new formula generation/search and does not authorize alpha proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "no_replay_preflight_clues",
    "control_dominated_candidates_present"
  ],
  "candidates_replayed": 15,
  "controls": [
    "one_bar_lag",
    "wrong_lag_future_24h",
    "wrong_lag_stale_168h",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_random"
  ],
  "decision": "HOLD_A7AL2I_NO_CLUES",
  "decision_counts": {
    "HOLD_A7AL2I_CONTROL_DOMINATED": 5,
    "HOLD_A7AL2I_UNSTABLE_PRE_MAY": 10
  },
  "executes_alpha_proof": false,
  "executes_formula_generation": false,
  "executes_formula_search": false,
  "generated_at": "2026-05-27T10:17:21Z",
  "input_base": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_replay_1h_v2_20260527",
  "replay_preflight_clue_count": 0,
  "rows": 3779411,
  "strict_symbols": 181
}
```

## Decision Counts

| decision                      |   count |
|:------------------------------|--------:|
| HOLD_A7AL2I_UNSTABLE_PRE_MAY  |      10 |
| HOLD_A7AL2I_CONTROL_DOMINATED |       5 |

## Candidate Decisions

| candidate_id                | family                       | field_families       | decision                      |   original_validation_spread |   original_test_spread |   original_recent_spread |   original_may_stress_spread |   one_bar_lag_recent_spread |   control_dominance_ratio_premay_max |
|:----------------------------|:-----------------------------|:---------------------|:------------------------------|-----------------------------:|-----------------------:|-------------------------:|-----------------------------:|----------------------------:|-------------------------------------:|
| crypto_fg2_3cbd1218eef4d5c7 | oi_price_interaction         | open_interest|price  | HOLD_A7AL2I_UNSTABLE_PRE_MAY  |                 -0.000524107 |            0.000517701 |             -0.000343549 |                  0.00399967  |                -0.000191229 |                             84.7821  |
| crypto_fg2_ab5daaf2d4bb1b38 | oi_price_interaction         | open_interest|price  | HOLD_A7AL2I_UNSTABLE_PRE_MAY  |                 -0.00105085  |            3.49839e-05 |              0.00199482  |                  0.00430411  |                 0.00199208  |                            202.643   |
| crypto_fg2_115383654a40dc95 | liquidity_volatility_guarded | liquidity|volatility | HOLD_A7AL2I_UNSTABLE_PRE_MAY  |                 -0.000862584 |            0.00116017  |              0.00112577  |                  0.00136471  |                 0.0010387   |                              3.26774 |
| crypto_fg2_2b9c738ec11bacea | oi_price_interaction         | open_interest|price  | HOLD_A7AL2I_UNSTABLE_PRE_MAY  |                 -0.000726305 |            0.000455898 |             -0.000855151 |                 -0.0022837   |                -0.000758212 |                              2.12347 |
| crypto_fg2_18f056370a194b1f | price_volatility_structure   | price|volatility     | HOLD_A7AL2I_UNSTABLE_PRE_MAY  |                 -0.000668248 |            0.000453409 |              0.000668235 |                  0.00143546  |                 0.000755116 |                             26.8341  |
| crypto_fg2_19a3f95b8076131b | oi_price_interaction         | open_interest|price  | HOLD_A7AL2I_UNSTABLE_PRE_MAY  |                 -0.000969554 |            0.000157018 |              0.000642059 |                  0.00133884  |                 0.000800566 |                             55.7898  |
| crypto_fg2_949d47bb2314fba0 | price_volatility_structure   | price|volatility     | HOLD_A7AL2I_UNSTABLE_PRE_MAY  |                  0.000421795 |           -0.00126118  |             -0.00503812  |                 -0.00153185  |                -0.00503358  |                             31.8779  |
| crypto_fg2_f3ffa3b8cccb6ae4 | price_volatility_structure   | price|volatility     | HOLD_A7AL2I_CONTROL_DOMINATED |                 -0.00138061  |           -0.00148657  |             -0.000263075 |                 -0.00175804  |                -0.00024041  |                              4.44151 |
| crypto_fg2_63b89c2c6cfee9d5 | price_volatility_structure   | price|volatility     | HOLD_A7AL2I_UNSTABLE_PRE_MAY  |                  0.00127949  |           -0.000894091 |             -0.00234856  |                 -0.000805904 |                -0.00238942  |                              1.8394  |
| crypto_fg2_80f9ad40dcfdd668 | price_volatility_structure   | price|volatility     | HOLD_A7AL2I_UNSTABLE_PRE_MAY  |                  0.000401548 |            0.000712178 |             -1.64203e-05 |                 -0.00138185  |                 0.000134595 |                            991.19    |
| crypto_fg2_b4ade21adee157d4 | price_volatility_structure   | price|volatility     | HOLD_A7AL2I_CONTROL_DOMINATED |                  0.00151464  |            0.000653174 |              0.0014931   |                  0.00108039  |                 0.00142817  |                             40.4328  |
| crypto_fg2_c649a241fed6a55f | liquidity_volatility_guarded | liquidity|volatility | HOLD_A7AL2I_UNSTABLE_PRE_MAY  |                  5.03432e-05 |           -0.00237397  |             -0.00159297  |                 -0.00264783  |                -0.00145624  |                             79.439   |
| crypto_fg2_7035940e742f28d3 | liquidity_volatility_guarded | liquidity|volatility | HOLD_A7AL2I_CONTROL_DOMINATED |                 -0.00111901  |           -0.00132893  |             -0.00260146  |                  3.85264e-05 |                -0.00254091  |                             20.2257  |
| crypto_fg2_71afa051e89efe97 | liquidity_volatility_guarded | liquidity|volatility | HOLD_A7AL2I_CONTROL_DOMINATED |                 -0.000264014 |           -0.00164329  |             -0.00432515  |                 -0.000575473 |                -0.00428377  |                             71.5678  |
| crypto_fg2_6dabc7639d6211d3 | liquidity_volatility_guarded | liquidity|volatility | HOLD_A7AL2I_CONTROL_DOMINATED |                 -0.000892421 |           -0.000338121 |             -0.000684644 |                 -0.00107856  |                -0.000824757 |                             67.8366  |

## Boundary

```text
Allowed interpretation:
  A7AL2I_REPLAY_PREFLIGHT_CLUE means a derived/interacted structure deserves controlled follow-up.

Not authorized:
  alpha proof
  shadow / paper / live
  large formula search
```
