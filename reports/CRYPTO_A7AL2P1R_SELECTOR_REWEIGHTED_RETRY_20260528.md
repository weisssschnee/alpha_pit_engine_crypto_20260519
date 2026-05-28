# CRYPTO A7AL-2P1R Selector-Reweighted Retry

Generated: 2026-05-28T07:23:21Z

## Decision

```text
PASS_A7AL2P1R_SELECTOR_REWEIGHTED_POOL_READY_FOR_P0R_RETRY
```

This stage reruns a mini replay only on A7AL-2P1 selector-eligible candidates. It uses no May inputs for selection and does not authorize formula-search execution.

## Manifest

```json
{
  "authorizes_a7al2p_contract": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "candidate_count": 2,
  "decision": "PASS_A7AL2P1R_SELECTOR_REWEIGHTED_POOL_READY_FOR_P0R_RETRY",
  "decision_counts": {
    "A7AL2P1R_SELECTOR_REWEIGHTED_DIAGNOSTIC_PASS": 2
  },
  "diagnostic_pass_count": 2,
  "executes_alpha_proof": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T07:23:21Z",
  "input": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7al2p1_selector_feature_generation\\a7al2p1_selector_feature_matrix.csv",
  "required_next": "freeze selector-reweighted diagnostic pool; do not execute A7AL-2 search without separate contract",
  "uses_may_for_selection": false,
  "warnings": []
}
```

## Decision Counts

| decision                                     |   count |
|:---------------------------------------------|--------:|
| A7AL2P1R_SELECTOR_REWEIGHTED_DIAGNOSTIC_PASS |       2 |

## Candidate Decisions

| candidate_id            | decision                                     | reasons   | warnings      | pass_variants                                                                                                                                                            | net_2bps_pass_variants                                                                                                                                                   |   neutralized_pass_variant_count |   recent_turnover |   control_ratio_premay_max_by_split |   latent_positive_premay_splits |
|:------------------------|:---------------------------------------------|:----------|:--------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------:|------------------:|------------------------------------:|--------------------------------:|
| a7al2k_046e806368e99c76 | A7AL2P1R_SELECTOR_REWEIGHTED_DIAGNOSTIC_PASS |           |               | original\|one_bar_lag\|neutral_liquidity_tier\|neutral_meme_contract_group\|neutral_multiplier_flag\|neutral_major_flag\|exclude_meme\|exclude_multiplier\|exclude_major | original\|one_bar_lag\|neutral_liquidity_tier\|neutral_meme_contract_group\|neutral_multiplier_flag\|neutral_major_flag\|exclude_meme\|exclude_multiplier\|exclude_major |                                7 |        0.00326183 |                             0.79335 |                               3 |
| a7al2k_0a247ec03472983b | A7AL2P1R_SELECTOR_REWEIGHTED_DIAGNOSTIC_PASS |           | control_close | original\|one_bar_lag\|neutral_liquidity_tier\|neutral_meme_contract_group\|neutral_multiplier_flag\|neutral_major_flag\|exclude_meme\|exclude_multiplier\|exclude_major | original\|one_bar_lag\|neutral_liquidity_tier\|neutral_meme_contract_group\|neutral_multiplier_flag\|neutral_major_flag\|exclude_meme\|exclude_multiplier\|exclude_major |                                7 |        0.00189813 |                             0.88085 |                               3 |

## Variant Split Summary

| candidate_id            | variant                       | split                 |   n_dates |   mean_spread_24h |   spread_tstat |   positive_spread_rate |   avg_one_way_turnover |   avg_top_count |   avg_bottom_count |   net_mean_spread_2bps |   net_mean_spread_5bps |   net_mean_spread_10bps |
|:------------------------|:------------------------------|:----------------------|----------:|------------------:|---------------:|-----------------------:|-----------------------:|----------------:|-------------------:|-----------------------:|-----------------------:|------------------------:|
| a7al2k_046e806368e99c76 | original                      | validation_2025H1     |      4320 |       0.00128866  |       7.39059  |               0.553704 |             0.00499445 |         18.8308 |            18.8308 |            0.00128766  |            0.00128616  |             0.00128366  |
| a7al2k_046e806368e99c76 | original                      | test_2025H2           |      4392 |       0.00191171  |      10.4451   |               0.582423 |             0.00463762 |         19      |            19      |            0.00191078  |            0.00190939  |             0.00190707  |
| a7al2k_046e806368e99c76 | original                      | recent_oos_2026JanApr |      2856 |       0.00186543  |       8.38356  |               0.583683 |             0.00326183 |         19      |            19      |            0.00186478  |            0.0018638   |             0.00186217  |
| a7al2k_046e806368e99c76 | original                      | known_may2026_stress  |       576 |      -0.00164923  |      -3.2968   |               0.522569 |             0.00420322 |         19      |            19      |           -0.00165007  |           -0.00165133  |            -0.00165343  |
| a7al2k_046e806368e99c76 | one_bar_lag                   | validation_2025H1     |      4320 |       0.001268    |       7.25808  |               0.553241 |             0.00498227 |         18.8308 |            18.8308 |            0.00126701  |            0.00126551  |             0.00126302  |
| a7al2k_046e806368e99c76 | one_bar_lag                   | test_2025H2           |      4392 |       0.00191682  |      10.4632   |               0.583333 |             0.0046496  |         19      |            19      |            0.00191589  |            0.00191449  |             0.00191217  |
| a7al2k_046e806368e99c76 | one_bar_lag                   | recent_oos_2026JanApr |      2856 |       0.0018384   |       8.27585  |               0.584384 |             0.00326183 |         19      |            19      |            0.00183774  |            0.00183677  |             0.00183514  |
| a7al2k_046e806368e99c76 | one_bar_lag                   | known_may2026_stress  |       576 |      -0.00163298  |      -3.268    |               0.520833 |             0.00420322 |         19      |            19      |           -0.00163383  |           -0.00163509  |            -0.00163719  |
| a7al2k_046e806368e99c76 | neutral_liquidity_tier        | validation_2025H1     |      4320 |       0.000948132 |       3.46278  |               0.524306 |             0.0057383  |         18.8308 |            18.8308 |            0.000946985 |            0.000945263 |             0.000942394 |
| a7al2k_046e806368e99c76 | neutral_liquidity_tier        | test_2025H2           |      4392 |       0.0017894   |       7.35132  |               0.534381 |             0.00502109 |         19      |            19      |            0.00178839  |            0.00178689  |             0.00178438  |
| a7al2k_046e806368e99c76 | neutral_liquidity_tier        | recent_oos_2026JanApr |      2856 |       0.00100964  |       3.4631   |               0.517507 |             0.00457025 |         19      |            19      |            0.00100873  |            0.00100736  |             0.00100507  |
| a7al2k_046e806368e99c76 | neutral_liquidity_tier        | known_may2026_stress  |       576 |       0.00106295  |       1.83566  |               0.543403 |             0.00539108 |         19      |            19      |            0.00106187  |            0.00106025  |             0.00105756  |
| a7al2k_046e806368e99c76 | neutral_meme_contract_group   | validation_2025H1     |      4320 |       0.00109445  |       6.06388  |               0.538426 |             0.00477941 |         17      |            17      |            0.00109349  |            0.00109206  |             0.00108967  |
| a7al2k_046e806368e99c76 | neutral_meme_contract_group   | test_2025H2           |      4392 |       0.00179208  |       9.33154  |               0.583333 |             0.00423229 |         17      |            17      |            0.00179123  |            0.00178996  |             0.00178785  |
| a7al2k_046e806368e99c76 | neutral_meme_contract_group   | recent_oos_2026JanApr |      2856 |       0.00212253  |       9.41992  |               0.579482 |             0.00306887 |         17      |            17      |            0.00212192  |            0.002121    |             0.00211946  |
| a7al2k_046e806368e99c76 | neutral_meme_contract_group   | known_may2026_stress  |       576 |      -0.00230133  |      -4.42666  |               0.487847 |             0.00428922 |         17      |            17      |           -0.00230219  |           -0.00230348  |            -0.00230562  |
| a7al2k_046e806368e99c76 | neutral_multiplier_flag       | validation_2025H1     |      4320 |       0.000879907 |       4.90734  |               0.528472 |             0.00393586 |         18.8308 |            18.8308 |            0.00087912  |            0.000877939 |             0.000875971 |
| a7al2k_046e806368e99c76 | neutral_multiplier_flag       | test_2025H2           |      4392 |       0.00196965  |       9.81858  |               0.566485 |             0.00377481 |         19      |            19      |            0.00196889  |            0.00196776  |             0.00196587  |
| a7al2k_046e806368e99c76 | neutral_multiplier_flag       | recent_oos_2026JanApr |      2856 |       0.00201949  |      10.42     |               0.588235 |             0.00261684 |         19      |            19      |            0.00201897  |            0.00201818  |             0.00201688  |
| a7al2k_046e806368e99c76 | neutral_multiplier_flag       | known_may2026_stress  |       576 |      -0.00250729  |      -5.10363  |               0.491319 |             0.00429459 |         19      |            19      |           -0.00250815  |           -0.00250944  |            -0.00251158  |
| a7al2k_046e806368e99c76 | neutral_major_flag            | validation_2025H1     |      4320 |       0.00103326  |       5.08952  |               0.534954 |             0.00552984 |         18      |            18      |            0.00103215  |            0.0010305   |             0.00102773  |
| a7al2k_046e806368e99c76 | neutral_major_flag            | test_2025H2           |      4392 |       0.00137624  |       6.90149  |               0.568534 |             0.00509765 |         18      |            18      |            0.00137522  |            0.00137369  |             0.00137114  |
| a7al2k_046e806368e99c76 | neutral_major_flag            | recent_oos_2026JanApr |      2856 |       0.00255711  |      10.006    |               0.595238 |             0.00412387 |         18      |            18      |            0.00255628  |            0.00255505  |             0.00255298  |
| a7al2k_046e806368e99c76 | neutral_major_flag            | known_may2026_stress  |       576 |      -0.0017026   |      -3.07182  |               0.506944 |             0.00405093 |         18      |            18      |           -0.00170341  |           -0.00170463  |            -0.00170666  |
| a7al2k_046e806368e99c76 | neutral_dominant_latent_state | validation_2025H1     |      4320 |      -0.00140102  |      -5.74616  |               0.459954 |             0.00379051 |          8      |             8      |           -0.00140177  |           -0.00140291  |            -0.00140481  |
| a7al2k_046e806368e99c76 | neutral_dominant_latent_state | test_2025H2           |      4392 |       0.00171262  |       5.25145  |               0.542577 |             0.00583447 |          8      |             8      |            0.00171146  |            0.00170971  |             0.00170679  |
| a7al2k_046e806368e99c76 | neutral_dominant_latent_state | recent_oos_2026JanApr |      2856 |      -0.000171612 |      -0.493702 |               0.497549 |             0.00730917 |          8      |             8      |           -0.000173073 |           -0.000175266 |            -0.000178921 |
| a7al2k_046e806368e99c76 | neutral_dominant_latent_state | known_may2026_stress  |       576 |      -0.000702223 |      -1.41856  |               0.498264 |             0.00694444 |          8      |             8      |           -0.000703612 |           -0.000705696 |            -0.000709168 |
| a7al2k_046e806368e99c76 | exclude_meme                  | validation_2025H1     |      4320 |       0.000951325 |       5.33615  |               0.532407 |             0.00469393 |         18      |            18      |            0.000950386 |            0.000948978 |             0.000946631 |
| a7al2k_046e806368e99c76 | exclude_meme                  | test_2025H2           |      4392 |       0.00164804  |       8.63497  |               0.573087 |             0.00406041 |         18      |            18      |            0.00164723  |            0.00164601  |             0.00164398  |
| a7al2k_046e806368e99c76 | exclude_meme                  | recent_oos_2026JanApr |      2856 |       0.00198411  |       8.93038  |               0.567227 |             0.00328743 |         18      |            18      |            0.00198345  |            0.00198246  |             0.00198082  |
| a7al2k_046e806368e99c76 | exclude_meme                  | known_may2026_stress  |       576 |      -0.00158974  |      -3.0706   |               0.510417 |             0.00434028 |         18      |            18      |           -0.00159061  |           -0.00159191  |            -0.00159408  |
| a7al2k_046e806368e99c76 | exclude_multiplier            | validation_2025H1     |      4320 |       0.00106352  |       5.90812  |               0.55463  |             0.00452675 |         18      |            18      |            0.00106261  |            0.00106125  |             0.00105899  |
| a7al2k_046e806368e99c76 | exclude_multiplier            | test_2025H2           |      4392 |       0.00185932  |       9.99828  |               0.583333 |             0.00402247 |         18      |            18      |            0.00185852  |            0.00185731  |             0.0018553   |
| a7al2k_046e806368e99c76 | exclude_multiplier            | recent_oos_2026JanApr |      2856 |       0.00215606  |      10.0451   |               0.579482 |             0.00359866 |         18      |            18      |            0.00215534  |            0.00215426  |             0.00215246  |
| a7al2k_046e806368e99c76 | exclude_multiplier            | known_may2026_stress  |       576 |      -0.00194321  |      -3.7242   |               0.513889 |             0.00414738 |         18      |            18      |           -0.00194404  |           -0.00194528  |            -0.00194736  |
| a7al2k_046e806368e99c76 | exclude_major                 | validation_2025H1     |      4320 |       0.00103326  |       5.08952  |               0.534954 |             0.00552984 |         18      |            18      |            0.00103215  |            0.0010305   |             0.00102773  |
| a7al2k_046e806368e99c76 | exclude_major                 | test_2025H2           |      4392 |       0.00137624  |       6.90149  |               0.568534 |             0.00509765 |         18      |            18      |            0.00137522  |            0.00137369  |             0.00137114  |
| a7al2k_046e806368e99c76 | exclude_major                 | recent_oos_2026JanApr |      2856 |       0.00255711  |      10.006    |               0.595238 |             0.00412387 |         18      |            18      |            0.00255628  |            0.00255505  |             0.00255298  |
| a7al2k_046e806368e99c76 | exclude_major                 | known_may2026_stress  |       576 |      -0.0017026   |      -3.07182  |               0.506944 |             0.00405093 |         18      |            18      |           -0.00170341  |           -0.00170463  |            -0.00170666  |
| a7al2k_0a247ec03472983b | original                      | validation_2025H1     |      4320 |       0.00122938  |       7.33721  |               0.555787 |             0.00220517 |         18.9002 |            18.9002 |            0.00122894  |            0.00122828  |             0.00122717  |
| a7al2k_0a247ec03472983b | original                      | test_2025H2           |      4392 |       0.00159185  |       8.74035  |               0.567395 |             0.00227687 |         19      |            19      |            0.00159139  |            0.00159071  |             0.00158957  |
| a7al2k_0a247ec03472983b | original                      | recent_oos_2026JanApr |      2856 |       0.00188517  |       8.55105  |               0.606443 |             0.00189813 |         19      |            19      |            0.00188479  |            0.00188422  |             0.00188328  |
| a7al2k_0a247ec03472983b | original                      | known_may2026_stress  |       576 |      -0.00166771  |      -3.6598   |               0.503472 |             0.0031981  |         19      |            19      |           -0.00166835  |           -0.00166931  |            -0.00167091  |
| a7al2k_0a247ec03472983b | one_bar_lag                   | validation_2025H1     |      4320 |       0.00122385  |       7.30938  |               0.556944 |             0.00220517 |         18.9002 |            18.9002 |            0.00122341  |            0.00122275  |             0.00122165  |
| a7al2k_0a247ec03472983b | one_bar_lag                   | test_2025H2           |      4392 |       0.0015963   |       8.75937  |               0.567851 |             0.00227687 |         19      |            19      |            0.00159585  |            0.00159517  |             0.00159403  |
| a7al2k_0a247ec03472983b | one_bar_lag                   | recent_oos_2026JanApr |      2856 |       0.00186493  |       8.45858  |               0.605042 |             0.00189813 |         19      |            19      |            0.00186455  |            0.00186398  |             0.00186303  |
| a7al2k_0a247ec03472983b | one_bar_lag                   | known_may2026_stress  |       576 |      -0.00166943  |      -3.67253  |               0.501736 |             0.0031981  |         19      |            19      |           -0.00167007  |           -0.00167103  |            -0.00167263  |
| a7al2k_0a247ec03472983b | neutral_liquidity_tier        | validation_2025H1     |      4320 |       0.00128889  |       4.79505  |               0.529861 |             0.00278184 |         18.9002 |            18.9002 |            0.00128834  |            0.0012875   |             0.00128611  |
| a7al2k_0a247ec03472983b | neutral_liquidity_tier        | test_2025H2           |      4392 |       0.00190534  |       8.06985  |               0.530965 |             0.00299588 |         19      |            19      |            0.00190475  |            0.00190385  |             0.00190235  |
| a7al2k_0a247ec03472983b | neutral_liquidity_tier        | recent_oos_2026JanApr |      2856 |       0.000940252 |       3.26721  |               0.509804 |             0.00230355 |         19      |            19      |            0.000939791 |            0.0009391   |             0.000937948 |
| a7al2k_0a247ec03472983b | neutral_liquidity_tier        | known_may2026_stress  |       576 |       0.000556724 |       1.02741  |               0.505208 |             0.00310673 |         19      |            19      |            0.000556102 |            0.00055517  |             0.000553617 |
| a7al2k_0a247ec03472983b | neutral_meme_contract_group   | validation_2025H1     |      4320 |       0.00137661  |       7.83113  |               0.557407 |             0.00227397 |         17      |            17      |            0.00137615  |            0.00137547  |             0.00137433  |
| a7al2k_0a247ec03472983b | neutral_meme_contract_group   | test_2025H2           |      4392 |       0.00131339  |       6.77566  |               0.557149 |             0.00214293 |         17      |            17      |            0.00131296  |            0.00131231  |             0.00131124  |
| a7al2k_0a247ec03472983b | neutral_meme_contract_group   | recent_oos_2026JanApr |      2856 |       0.0023441   |      10.4162   |               0.603641 |             0.0017301  |         17      |            17      |            0.00234375  |            0.00234323  |             0.00234237  |
| a7al2k_0a247ec03472983b | neutral_meme_contract_group   | known_may2026_stress  |       576 |      -0.00200398  |      -4.15628  |               0.496528 |             0.0033701  |         17      |            17      |           -0.00200466  |           -0.00200567  |            -0.00200735  |
| a7al2k_0a247ec03472983b | neutral_multiplier_flag       | validation_2025H1     |      4320 |       0.0010336   |       6.01446  |               0.532407 |             0.00208333 |         18.9002 |            18.9002 |            0.00103318  |            0.00103256  |             0.00103152  |
| a7al2k_0a247ec03472983b | neutral_multiplier_flag       | test_2025H2           |      4392 |       0.00148434  |       7.68109  |               0.548725 |             0.0019653  |         19      |            19      |            0.00148395  |            0.00148336  |             0.00148237  |
| a7al2k_0a247ec03472983b | neutral_multiplier_flag       | recent_oos_2026JanApr |      2856 |       0.00198185  |      10.5993   |               0.603291 |             0.00167699 |         19      |            19      |            0.00198152  |            0.00198101  |             0.00198017  |
| a7al2k_0a247ec03472983b | neutral_multiplier_flag       | known_may2026_stress  |       576 |      -0.00188741  |      -4.12323  |               0.505208 |             0.0028326  |         19      |            19      |           -0.00188798  |           -0.00188883  |            -0.00189025  |
| a7al2k_0a247ec03472983b | neutral_major_flag            | validation_2025H1     |      4320 |       0.00105642  |       5.33711  |               0.536111 |             0.00266204 |         18      |            18      |            0.00105589  |            0.00105509  |             0.00105376  |
| a7al2k_0a247ec03472983b | neutral_major_flag            | test_2025H2           |      4392 |       0.00110754  |       5.63652  |               0.540301 |             0.00265634 |         18      |            18      |            0.00110701  |            0.00110621  |             0.00110488  |
| a7al2k_0a247ec03472983b | neutral_major_flag            | recent_oos_2026JanApr |      2856 |       0.00229131  |       9.07698  |               0.607843 |             0.00235372 |         18      |            18      |            0.00229083  |            0.00229013  |             0.00228895  |
| a7al2k_0a247ec03472983b | neutral_major_flag            | known_may2026_stress  |       576 |      -0.00203991  |      -3.9622   |               0.482639 |             0.00298997 |         18      |            18      |           -0.00204051  |           -0.0020414   |            -0.0020429   |
| a7al2k_0a247ec03472983b | neutral_dominant_latent_state | validation_2025H1     |      4320 |      -0.00176809  |      -6.97062  |               0.44838  |             0.00202546 |          8      |             8      |           -0.00176849  |           -0.0017691   |            -0.00177011  |
| a7al2k_0a247ec03472983b | neutral_dominant_latent_state | test_2025H2           |      4392 |       0.00165578  |       5.18874  |               0.532332 |             0.00350068 |          8      |             8      |            0.00165507  |            0.00165402  |             0.00165227  |
| a7al2k_0a247ec03472983b | neutral_dominant_latent_state | recent_oos_2026JanApr |      2856 |      -0.000423931 |      -1.35318  |               0.491947 |             0.00380777 |          8      |             8      |           -0.000424693 |           -0.000425835 |            -0.000427739 |
| a7al2k_0a247ec03472983b | neutral_dominant_latent_state | known_may2026_stress  |       576 |      -0.00139285  |      -2.93141  |               0.494792 |             0.00434028 |          8      |             8      |           -0.00139372  |           -0.00139502  |            -0.00139719  |
| a7al2k_0a247ec03472983b | exclude_meme                  | validation_2025H1     |      4320 |       0.00126496  |       7.24364  |               0.544213 |             0.00227623 |         18      |            18      |            0.00126451  |            0.00126382  |             0.00126269  |
| a7al2k_0a247ec03472983b | exclude_meme                  | test_2025H2           |      4392 |       0.00133714  |       7.13239  |               0.559426 |             0.00201123 |         18      |            18      |            0.00133674  |            0.00133613  |             0.00133513  |
| a7al2k_0a247ec03472983b | exclude_meme                  | recent_oos_2026JanApr |      2856 |       0.00190798  |       8.82867  |               0.586485 |             0.0017896  |         18      |            18      |            0.00190762  |            0.00190708  |             0.00190619  |
| a7al2k_0a247ec03472983b | exclude_meme                  | known_may2026_stress  |       576 |      -0.00174773  |      -3.51336  |               0.496528 |             0.00327932 |         18      |            18      |           -0.00174838  |           -0.00174937  |            -0.00175101  |
| a7al2k_0a247ec03472983b | exclude_multiplier            | validation_2025H1     |      4320 |       0.00133     |       7.56358  |               0.571296 |             0.00216049 |         18      |            18      |            0.00132957  |            0.00132892  |             0.00132784  |
| a7al2k_0a247ec03472983b | exclude_multiplier            | test_2025H2           |      4392 |       0.00152658  |       8.33655  |               0.566485 |             0.00206183 |         18      |            18      |            0.00152617  |            0.00152555  |             0.00152452  |
| a7al2k_0a247ec03472983b | exclude_multiplier            | recent_oos_2026JanApr |      2856 |       0.00208895  |       9.95146  |               0.590686 |             0.00180906 |         18      |            18      |            0.00208859  |            0.00208805  |             0.00208714  |
| a7al2k_0a247ec03472983b | exclude_multiplier            | known_may2026_stress  |       576 |      -0.00180185  |      -3.58266  |               0.520833 |             0.00327932 |         18      |            18      |           -0.00180251  |           -0.00180349  |            -0.00180513  |
| a7al2k_0a247ec03472983b | exclude_major                 | validation_2025H1     |      4320 |       0.00105642  |       5.33711  |               0.536111 |             0.00266204 |         18      |            18      |            0.00105589  |            0.00105509  |             0.00105376  |
| a7al2k_0a247ec03472983b | exclude_major                 | test_2025H2           |      4392 |       0.00110754  |       5.63652  |               0.540301 |             0.00265634 |         18      |            18      |            0.00110701  |            0.00110621  |             0.00110488  |
| a7al2k_0a247ec03472983b | exclude_major                 | recent_oos_2026JanApr |      2856 |       0.00229131  |       9.07698  |               0.607843 |             0.00235372 |         18      |            18      |            0.00229083  |            0.00229013  |             0.00228895  |
| a7al2k_0a247ec03472983b | exclude_major                 | known_may2026_stress  |       576 |      -0.00203991  |      -3.9622   |               0.482639 |             0.00298997 |         18      |            18      |           -0.00204051  |           -0.0020414   |            -0.0020429   |

## Boundary

```text
Not authorized:
  A7AL-2P search contract
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
