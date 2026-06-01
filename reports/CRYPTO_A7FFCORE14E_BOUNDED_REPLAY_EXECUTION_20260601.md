# CRYPTO A7FF-CORE14E BOUNDED REPLAY EXECUTION

Generated: 2026-06-01T04:37:43Z

## Decision

`HOLD_A7FFCORE14E_BOUNDED_REPLAY_INSUFFICIENT`

A7FF-CORE14E executes bounded replay over the CORE14 128-candidate packet. It does not execute formula search, large search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core15_contract": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "clean_candidate_count_lt_24",
    "clean_semantic_bucket_count_lt_4",
    "clean_motif_bucket_count_lt_4"
  ],
  "candidate_count": 128,
  "clean_rule": "validation and recent both positive at 5bps with max non-signflip control_ratio < 1.0",
  "controls": [
    "wrong_lag_future",
    "wrong_lag_stale",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_placebo"
  ],
  "decision": "HOLD_A7FFCORE14E_BOUNDED_REPLAY_INSUFFICIENT",
  "eval_error_count": 0,
  "executes_replay": true,
  "executes_search": false,
  "generated_at": "2026-06-01T04:37:43Z",
  "next_allowed": "A7FF-CORE14R replay failure forensic",
  "replay_clean_candidate_count": 2,
  "replay_clean_motif_bucket_count": 1,
  "replay_clean_semantic_bucket_count": 1,
  "replay_rows": 1536,
  "sample_rows": 511589,
  "sample_timestamp_count": 1536,
  "source_decision": "PASS_A7FFCORE14_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE14E",
  "source_stage": "A7FF-CORE14",
  "stage": "A7FF-CORE14E"
}
```

## Family Summary

| semantic_bucket                      | motif_bucket       |   candidate_count |   median_cost_adjusted_spread |   median_control_ratio |   clean_candidate_count |
|:-------------------------------------|:-------------------|------------------:|------------------------------:|-----------------------:|------------------------:|
| liquidity_like\|volatility_like      | liquidity_shock    |                28 |                  -0.000557083 |                1.47976 |                       2 |
| open_interest_like\|positioning_like | delta_x_divergence |                28 |                  -0.00061929  |                3.05575 |                       0 |
| taker_flow_like\|basis_premium_like  | gated_sign         |                24 |                  -0.000463243 |                2.77483 |                       0 |
| taker_flow_like\|open_interest_like  | flow_x_leverage    |                24 |                  -0.000840708 |                2.59949 |                       0 |
| liquidity_like                       | single             |                20 |                  -0.000921918 |                3.15779 |                       0 |
| open_interest_like                   | single             |                 4 |                  -0.000694157 |                4.77404 |                       0 |

## Candidate Summary

| candidate_id                   | semantic_bucket                      | motif_bucket       |   replay_rows |   median_spread |   median_cost_adjusted_spread |   max_tstat |   min_control_ratio |   validation_recent_clean_splits | replay_clean   |
|:-------------------------------|:-------------------------------------|:-------------------|--------------:|----------------:|------------------------------:|------------:|--------------------:|---------------------------------:|:---------------|
| a7ffcore11e_34c80c6d72709214b6 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.00148006  |                   0.000497137 |    2.48624  |            0.674706 |                                2 | True           |
| a7ffcore11e_47e7feb2ae3fd724af | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.00170492  |                   0.000427613 |    2.30997  |            0.839641 |                                2 | True           |
| a7ffcore11e_915089a6e339233ea8 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000516535 |                  -0.000276032 |    4.27475  |            1.25074  |                                0 | False          |
| a7ffcore11e_e2ef38c0251e5f9d9f | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000402368 |                  -0.000302803 |    4.22989  |            0.966124 |                                0 | False          |
| a7ffcore11e_e5f7689834367b6808 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000402771 |                  -0.000439246 |    3.92097  |            1.53874  |                                0 | False          |
| a7ffcore11e_a8bc245f20ba6f090e | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000538126 |                  -0.000346648 |    3.55001  |            1.81321  |                                0 | False          |
| a7ffcore11e_3de814e190a09da7c5 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000349639 |                  -0.00041639  |    3.04729  |            2.16903  |                                0 | False          |
| a7ffcore11e_10950375da87ec66dc | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000295445 |                  -0.000483475 |    2.8795   |            2.3548   |                                0 | False          |
| a7ffcore11e_a8d20b6bdd9fb53e86 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.00102972  |                  -3.83035e-05 |    2.85705  |            0.832834 |                                1 | False          |
| a7ffcore11e_fc238d0a2f892c56c8 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000446065 |                  -0.000442001 |    2.83909  |            1.95524  |                                0 | False          |
| a7ffcore11e_0e0f0e07398f95176c | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000324298 |                  -0.000495959 |    2.77688  |            2.34297  |                                0 | False          |
| a7ffcore11e_ce389ddfa48b59e0f7 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000329079 |                  -0.0002081   |    2.75121  |            0.844464 |                                1 | False          |
| a7ffcore11e_108bca7372512beafd | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000788985 |                  -0.000224956 |    2.71713  |            0.681327 |                                1 | False          |
| a7ffcore11e_7c8802ba202be3239e | liquidity_like                       | single             |            12 |    -0.000183155 |                  -0.000594835 |    2.53184  |            0.830308 |                                0 | False          |
| a7ffcore11e_55aaf9f22b9764a1a2 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000873399 |                  -7.53749e-05 |    2.44686  |            0.79794  |                                1 | False          |
| a7ffcore11e_c70bbc5022a6f28dd1 | liquidity_like                       | single             |            12 |    -0.000164158 |                  -0.000606517 |    2.43088  |            0.98088  |                                0 | False          |
| a7ffcore11e_4c3d00558447cd47dd | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000153736 |                  -0.000561689 |    2.4296   |            0.902629 |                                0 | False          |
| a7ffcore11e_941cf981f5d72cff80 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.00241403  |                   0.00171403  |    2.41737  |            0.825688 |                                0 | False          |
| a7ffcore11e_b42a7e3dcfc5ad4c16 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000270128 |                  -0.000639902 |    2.41444  |            0.681013 |                                0 | False          |
| a7ffcore11e_0700ec30c6b8fb8e9c | liquidity_like\|volatility_like      | liquidity_shock    |            12 |    -0.000352479 |                  -0.000753804 |    2.30354  |            0.642948 |                                0 | False          |
| a7ffcore11e_835cc04ca784ccc502 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     2.78777e-05 |                  -0.000608725 |    2.11106  |            0.797382 |                                0 | False          |
| a7ffcore11e_2414f8e2f51a8e9e85 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.000526365 |                  -0.000290205 |    2.07505  |            1.00723  |                                0 | False          |
| a7ffcore11e_f19f4cce024077a6bc | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000640382 |                  -0.000318999 |    2.01879  |            1.48883  |                                0 | False          |
| a7ffcore11e_c6c5696a8e9141f9bf | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.00060992  |                  -0.000300686 |    1.99737  |            0.330598 |                                0 | False          |
| a7ffcore11e_3a5ff4c4fdf2df5a9f | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000172651 |                  -0.000597115 |    1.9699   |            0.440684 |                                0 | False          |
| a7ffcore11e_3a24520d5c00abc2a3 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000152148 |                  -0.000530471 |    1.94192  |            1.03803  |                                0 | False          |
| a7ffcore11e_4ce0c8b245d5808abe | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.00112935  |                   0.000333791 |    1.90956  |            0.91164  |                                1 | False          |
| a7ffcore11e_39a12c5e1a821ba4d7 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |    -0.000146097 |                  -0.000553627 |    1.88313  |            0.769139 |                                0 | False          |
| a7ffcore11e_7d56c9ecbc9ab9d958 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.0078873   |                   0.0071873   |    1.88105  |            0.658309 |                                1 | False          |
| a7ffcore11e_123c59e7517b7ef3c6 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000352472 |                  -0.000243024 |    1.86718  |            0.489802 |                                0 | False          |
| a7ffcore11e_393e6f44827ee26050 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000126082 |                  -0.000631634 |    1.85969  |            1.13443  |                                0 | False          |
| a7ffcore11e_11882b391b74beae55 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.000535207 |                  -0.000350629 |    1.82812  |            1.11221  |                                0 | False          |
| a7ffcore11e_5ba23f43a8b1fe6632 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |    -0.000220232 |                  -0.000697547 |    1.80217  |            1.90382  |                                0 | False          |
| a7ffcore11e_7dd7c256aff9e3f288 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000102287 |                  -0.000335041 |    1.78265  |            1.0837   |                                0 | False          |
| a7ffcore11e_0645e71850908e893a | open_interest_like\|positioning_like | delta_x_divergence |            12 |     8.7499e-05  |                  -0.000564344 |    1.76934  |            1.39103  |                                0 | False          |
| a7ffcore11e_8f6b5c507d07d416bf | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000114904 |                  -0.000296139 |    1.74504  |            1.26103  |                                0 | False          |
| a7ffcore11e_e8c050ca94b5544a55 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     9.79183e-05 |                  -0.000566791 |    1.70166  |            1.1824   |                                0 | False          |
| a7ffcore11e_927921c104d8413250 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.0282518   |                   0.0275518   |    1.69887  |            0.78485  |                                0 | False          |
| a7ffcore11e_efeeb5b717de848eab | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.00013393  |                  -0.000535714 |    1.6603   |            0.985213 |                                0 | False          |
| a7ffcore11e_a632ea315826e6f709 | liquidity_like                       | single             |            12 |    -0.000665921 |                  -0.00128854  |    1.65606  |            0.62564  |                                1 | False          |
| a7ffcore11e_c21abf533e137c4adb | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.00026114  |                  -0.000276485 |    1.58812  |            0.765847 |                                0 | False          |
| a7ffcore11e_972c137febb8270f5e | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.00079976  |                   0.000215177 |    1.56079  |            1.18412  |                                0 | False          |
| a7ffcore11e_2e9ceddde79416ef0f | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |    -9.92464e-05 |                  -0.000590856 |    1.55728  |            1.51876  |                                0 | False          |
| a7ffcore11e_1f2c1c1b532d84483b | liquidity_like\|volatility_like      | liquidity_shock    |            12 |    -5.65859e-05 |                  -0.000721818 |    1.54494  |            0.743862 |                                0 | False          |
| a7ffcore11e_2589c8bd01327ba35c | open_interest_like\|positioning_like | delta_x_divergence |            12 |    -5.01777e-05 |                  -0.000494972 |    1.53919  |            1.4538   |                                0 | False          |
| a7ffcore11e_1942160ee15398d457 | open_interest_like                   | single             |            12 |     7.89736e-06 |                  -0.00037444  |    1.48582  |            0.914855 |                                1 | False          |
| a7ffcore11e_2672660b483c4cfb0e | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.00104714  |                  -0.000258458 |    1.48211  |            0.524937 |                                0 | False          |
| a7ffcore11e_40f891be37b850af13 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.000544398 |                  -0.000378465 |    1.43744  |            0.876423 |                                0 | False          |
| a7ffcore11e_64b7c6f83d3aa012b4 | liquidity_like                       | single             |            12 |     0.000240904 |                  -0.000550588 |    1.38158  |            1.40191  |                                0 | False          |
| a7ffcore11e_954ca2e0b13697327e | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.00074322  |                  -1.94176e-05 |    1.34927  |            1.17391  |                                0 | False          |
| a7ffcore11e_1aec87731a157bc5be | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     1.48376e-05 |                  -0.000619063 |    1.34653  |            1.54897  |                                0 | False          |
| a7ffcore11e_49182c09dd3b9c5213 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -6.36038e-05 |                  -0.000633043 |    1.32967  |            0.868324 |                                0 | False          |
| a7ffcore11e_117db61a4c24d455a6 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.00015863  |                  -0.00062656  |    1.28437  |            0.664006 |                                0 | False          |
| a7ffcore11e_f8d5c4e118d204c286 | liquidity_like                       | single             |            12 |    -0.000170575 |                  -0.000725944 |    1.27588  |            2.4508   |                                0 | False          |
| a7ffcore11e_3103906ad46d1df38b | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     6.00253e-05 |                  -0.000699488 |    1.22077  |            1.03394  |                                0 | False          |
| a7ffcore11e_b22e934b8b01b76133 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000227412 |                  -0.000328586 |    1.20301  |            1.4845   |                                0 | False          |
| a7ffcore11e_12acb7538ac2c1de85 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.000996357 |                  -0.000469335 |    1.20151  |            0.537039 |                                0 | False          |
| a7ffcore11e_2a2d48956a572ac1ab | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.0372133   |                   0.0365133   |    1.18513  |            0.93515  |                                1 | False          |
| a7ffcore11e_557114329870cf4f2d | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.000172045 |                  -0.000727878 |    1.1793   |            1.04372  |                                0 | False          |
| a7ffcore11e_182f68b6ba2a032d4a | liquidity_like                       | single             |            12 |     0.00029625  |                  -0.000861572 |    1.17083  |            0.892843 |                                0 | False          |
| a7ffcore11e_0ba480ce00fc18d6d2 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |    -0.00150182  |                  -0.00197477  |    1.16608  |            0.341581 |                                0 | False          |
| a7ffcore11e_620048b49bc3dfd43f | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |    -9.20697e-05 |                  -0.000537917 |    1.16573  |            1.84745  |                                0 | False          |
| a7ffcore11e_7f4ddd6ba1891e3a2c | liquidity_like                       | single             |            12 |    -7.23436e-05 |                  -0.000896871 |    1.15422  |            2.13067  |                                0 | False          |
| a7ffcore11e_0dd21d80949fec5fb7 | liquidity_like                       | single             |            12 |    -0.000126744 |                  -0.000928274 |    1.14401  |            2.00929  |                                0 | False          |
| a7ffcore11e_669405f740974badf1 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.000124417 |                  -0.000277485 |    1.13195  |            0.925524 |                                0 | False          |
| a7ffcore11e_3133e9ebd2783af2e9 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |    -3.34039e-05 |                  -0.000797041 |    1.06136  |            0.50701  |                                0 | False          |
| a7ffcore11e_a7ceb9c23859d4f00b | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000288158 |                  -0.000452713 |    1.05999  |            2.35951  |                                0 | False          |
| a7ffcore11e_2d54ba78481e4e85dd | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.0021449   |                  -0.0028449   |    1.04898  |            0.831678 |                                0 | False          |
| a7ffcore11e_5c55acbd5042b16e79 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.000191527 |                  -0.000681303 |    1.02314  |            1.92267  |                                0 | False          |
| a7ffcore11e_317c3a2eaa7e3a189f | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.00090256  |                  -0.000591923 |    1.00835  |            0.814489 |                                0 | False          |
| a7ffcore11e_8e9f45a5dc22a8ab8f | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000452385 |                  -0.000162787 |    0.988027 |            1.8176   |                                0 | False          |
| a7ffcore11e_08873be32daaf18f8f | liquidity_like                       | single             |            12 |     0.000243825 |                  -0.000909258 |    0.98623  |            0.959573 |                                0 | False          |
| a7ffcore11e_4831794c3f43dcc5d1 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.00042717  |                  -0.000171952 |    0.964775 |            1.49913  |                                0 | False          |
| a7ffcore11e_24d118bdee2c46d2f8 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000413503 |                  -0.000451782 |    0.919262 |            1.13231  |                                0 | False          |
| a7ffcore11e_3da94ac56d8fd1b291 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |     0.0101943   |                   0.00949429  |    0.886728 |            2.27328  |                                0 | False          |
| a7ffcore11e_6265acb2b7aaeed67c | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000364317 |                  -0.000372566 |    0.879317 |            2.20715  |                                0 | False          |
| a7ffcore11e_7b72349fd51af1e863 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.000102918 |                  -0.000693149 |    0.861787 |            1.13006  |                                0 | False          |
| a7ffcore11e_08612111456ef74614 | liquidity_like\|volatility_like      | liquidity_shock    |            12 |    -0.000505974 |                  -0.00120597  |    0.839116 |            1.57892  |                                0 | False          |
| a7ffcore11e_20915977e99a094b82 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     2.4456e-05  |                  -0.00072402  |    0.83192  |            1.8876   |                                0 | False          |
| a7ffcore11e_52fdc3bb64b98000d3 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.000186537 |                  -0.000501902 |    0.817608 |            1.40224  |                                0 | False          |
| a7ffcore11e_01b7a408bae766f6b9 | open_interest_like                   | single             |            12 |     0.000102613 |                  -0.000818321 |    0.801498 |            1.64301  |                                0 | False          |
| a7ffcore11e_3c9e132afdab6a61c6 | taker_flow_like\|basis_premium_like  | gated_sign         |            12 |     0.000353988 |                  -0.000981966 |    0.793679 |            1.27891  |                                0 | False          |
| a7ffcore11e_6dfea25769981420cd | liquidity_like                       | single             |            12 |     0.000129675 |                  -0.000515837 |    0.787119 |            4.22491  |                                0 | False          |
| a7ffcore11e_b50799eaf4f797bc7c | liquidity_like                       | single             |            12 |     0.000225797 |                  -0.000501103 |    0.759929 |            4.07865  |                                0 | False          |
| a7ffcore11e_7036d028e1478c3480 | liquidity_like                       | single             |            12 |    -0.000160239 |                  -0.000887171 |    0.746512 |            2.1902   |                                0 | False          |
| a7ffcore11e_534bb9195a9174cfa9 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.0056666   |                  -0.0063666   |    0.740119 |            2.0755   |                                0 | False          |
| a7ffcore11e_37bd4029b21e5907ea | liquidity_like\|volatility_like      | liquidity_shock    |            12 |    -0.000148137 |                  -0.000860159 |    0.701553 |            1.19116  |                                0 | False          |
| a7ffcore11e_2c46230d8041995149 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |     0.000171686 |                  -0.000598245 |    0.679826 |            1.83783  |                                0 | False          |
| a7ffcore11e_498cf2fdb232c85d26 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     3.98932e-05 |                  -0.000699851 |    0.620462 |            1.87546  |                                0 | False          |
| a7ffcore11e_597c2efceacc2a97eb | open_interest_like\|positioning_like | delta_x_divergence |            12 |    -2.6139e-05  |                  -0.000658559 |    0.60537  |            1.465    |                                0 | False          |
| a7ffcore11e_1c294ee13a07d9e36a | liquidity_like                       | single             |            12 |     0.000170893 |                  -0.000903385 |    0.583497 |            2.48949  |                                0 | False          |
| a7ffcore11e_1c0ea6a158e2272181 | liquidity_like                       | single             |            12 |    -0.000124938 |                  -0.000807752 |    0.572169 |            2.28337  |                                0 | False          |
| a7ffcore11e_205fca9713a5ecddcf | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.00282659  |                  -0.00352659  |    0.509494 |            1.18111  |                                0 | False          |
| a7ffcore11e_cfcfbc2592d847facd | liquidity_like                       | single             |            12 |    -0.000109224 |                  -0.00101797  |    0.484445 |            2.70768  |                                0 | False          |
| a7ffcore11e_75b0b94e2607e97c77 | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.000171386 |                  -0.000764649 |    0.454089 |            0.947692 |                                0 | False          |
| a7ffcore11e_ceecd13760f1f015e9 | liquidity_like                       | single             |            12 |    -0.000657455 |                  -0.00150117  |    0.445758 |            0.991123 |                                0 | False          |
| a7ffcore11e_94fc8621dfeb133185 | liquidity_like                       | single             |            12 |     8.28713e-05 |                  -0.000937774 |    0.398906 |            2.65244  |                                0 | False          |
| a7ffcore11e_7adbce68940be45d6b | taker_flow_like\|open_interest_like  | flow_x_leverage    |            12 |    -0.00815691  |                  -0.00885691  |    0.387735 |            1.29187  |                                0 | False          |
| a7ffcore11e_b7574831145f932936 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     0.000114629 |                  -0.000800716 |    0.377963 |            2.9654   |                                0 | False          |
| a7ffcore11e_af83cce5829bc7c751 | open_interest_like\|positioning_like | delta_x_divergence |            12 |     7.10525e-05 |                  -0.000888014 |    0.363076 |            2.00681  |                                0 | False          |

## Boundary

```text
bounded replay: true
formula search / large search: false
promotion: false
alpha proof / shadow / paper / live: false
```
