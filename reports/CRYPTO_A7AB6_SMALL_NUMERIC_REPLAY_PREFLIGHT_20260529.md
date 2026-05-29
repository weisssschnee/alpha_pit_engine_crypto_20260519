# CRYPTO A7AB-6 SMALL NUMERIC REPLAY PREFLIGHT

Generated: 2026-05-29T06:23:22Z

## Decision

`PASS_A7AB6_SMALL_NUMERIC_REPLAY_PREFLIGHT_CLUES_FOUND_EXECUTION_HOLD`

A7AB-6 is a bounded numeric replay preflight on A7AB-5 queue. It does not authorize formula search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7ab7_forensic_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "clue_candidate_count": 27,
  "clue_count": 33,
  "decision": "PASS_A7AB6_SMALL_NUMERIC_REPLAY_PREFLIGHT_CLUES_FOUND_EXECUTION_HOLD",
  "decision_counts": {
    "A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE": 33,
    "HOLD_A7AB6_CONTROL_DOMINATED": 260,
    "HOLD_A7AB6_ONE_BAR_LAG_FRAGILE": 125,
    "HOLD_A7AB6_PREMAY_UNSTABLE": 350
  },
  "eval_error_count": 0,
  "executes_formula_generation": false,
  "executes_large_search": false,
  "executes_small_numeric_replay_preflight": true,
  "executes_training": false,
  "full_timestamps_before_subset": 21025,
  "generated_at": "2026-05-29T06:23:22Z",
  "horizons": [
    1,
    4
  ],
  "hours_per_split": 720,
  "input_queue_count": 128,
  "labels": [
    "L7_ranked_future_return",
    "L1_cross_sectional_relative_return",
    "L0_raw_forward_return"
  ],
  "metric_rows": 26880,
  "stage": "A7AB-6",
  "symbols_loaded": 96,
  "timestamps": 3481,
  "uses_may": false
}
```

## Decision Counts

| decision                          |   count |
|:----------------------------------|--------:|
| HOLD_A7AB6_PREMAY_UNSTABLE        |     350 |
| HOLD_A7AB6_CONTROL_DOMINATED      |     260 |
| HOLD_A7AB6_ONE_BAR_LAG_FRAGILE    |     125 |
| A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |      33 |

## Clue Queue

| candidate_id           | label_family                       |   horizon_h |   orientation_from_train | premay_all_positive   | one_bar_lag_ok   |   control_ratio_premay_max |   oriented_validation_spread |   oriented_test_spread |   oriented_recent_spread | decision                          |
|:-----------------------|:-----------------------------------|------------:|-------------------------:|:----------------------|:-----------------|---------------------------:|-----------------------------:|-----------------------:|-------------------------:|:----------------------------------|
| a7ab3_4092255ee6888704 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   0.742223 |                  0.0283688   |            0.0204193   |              0.0447428   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_ced6188c184ada50 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   0.98199  |                  0.02751     |            0.0198761   |              0.0454216   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_2af478d1ff284e21 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.948962 |                  0.0245258   |            0.0289143   |              0.0361537   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_3edc6f38cc9be3f3 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.948962 |                  0.0245258   |            0.0289143   |              0.0361537   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_6e301587da1c1fa3 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.882557 |                  0.0204831   |            0.0265494   |              0.0345867   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_6e301587da1c1fa3 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   0.963308 |                  0.0290778   |            0.0446459   |              0.059893    | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_da7270f10c2caee8 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.948962 |                  0.0245258   |            0.0289143   |              0.0361537   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_d4939ee84cb32793 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.975123 |                  0.0195696   |            0.0246783   |              0.0324775   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_165c7d8966b27a17 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   0.612648 |                  0.0168662   |            0.0371154   |              0.038156    | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_6eb23cd8ce4aeef1 | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.935474 |                  0.00716361  |            0.0224839   |              0.024909    | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_f0f4c568b02b1b72 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.877438 |                  0.0083343   |            0.0218926   |              0.0216956   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_0bc78809db3a1428 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   0.828236 |                  0.0170234   |            0.0306543   |              0.045593    | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_87c3ee594944936f | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.781213 |                  0.036546    |            0.0232496   |              0.0188253   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_12f53c28ae64a7c9 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.648849 |                  0.0174612   |            0.0260326   |              0.0141261   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_db425196e6b15b0a | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.661493 |                  0.0189146   |            0.0230662   |              0.0152592   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_0b7b3deaa9bdd1bc | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.750091 |                  0.0213145   |            0.031414    |              0.0237997   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_0b7b3deaa9bdd1bc | L1_cross_sectional_relative_return |           1 |                       -1 | True                  | True             |                   0.958687 |                  0.000213123 |            0.000325761 |              0.000330006 | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_0b7b3deaa9bdd1bc | L0_raw_forward_return              |           1 |                       -1 | True                  | True             |                   0.958687 |                  0.000213123 |            0.000325761 |              0.000330006 | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_0caf6e64238a4009 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.75522  |                  0.0138671   |            0.0179734   |              0.0219498   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_259e51a3d817578c | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.93     |                  0.00550839  |            0.0169654   |              0.0253293   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_3144de7015d18195 | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.947557 |                  0.0129939   |            0.014327    |              0.0217931   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_3144de7015d18195 | L1_cross_sectional_relative_return |           1 |                        1 | True                  | True             |                   0.823571 |                  0.000244054 |            0.000274848 |              0.000559947 | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_3144de7015d18195 | L0_raw_forward_return              |           1 |                        1 | True                  | True             |                   0.823571 |                  0.000244054 |            0.000274848 |              0.000559947 | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_7005b0d4aa2dce2e | L1_cross_sectional_relative_return |           4 |                       -1 | True                  | True             |                   0.574381 |                  0.000349483 |            0.000705173 |              0.000693984 | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_7005b0d4aa2dce2e | L0_raw_forward_return              |           4 |                       -1 | True                  | True             |                   0.574381 |                  0.000349483 |            0.000705173 |              0.000693984 | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_2ad4a9e8d3c38900 | L7_ranked_future_return            |           4 |                        1 | True                  | True             |                   0.986254 |                  0.0101661   |            0.00683493  |              0.0120394   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_7935162ab6cc52c9 | L7_ranked_future_return            |           4 |                        1 | True                  | True             |                   0.777695 |                  0.0174483   |            0.0266896   |              0.0257525   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_e142ac349de3313f | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.904059 |                  0.0076644   |            0.0161337   |              0.0102138   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_fdd86cd8983e9d9b | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.438893 |                  0.0211199   |            0.0371599   |              0.0278053   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_04daf24ce962db97 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.999732 |                  0.00842556  |            0.014248    |              0.0162893   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_e5d6e69d28752387 | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.886676 |                  0.0187043   |            0.0261566   |              0.037109    | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_5f3490d60d842a6e | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.443923 |                  0.0247989   |            0.0345525   |              0.0256028   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_6406fc0cf7ff3b35 | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.818843 |                  0.0119762   |            0.0207953   |              0.0127102   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |

## Ranked Decision Queue Sample

| candidate_id           | label_family                       |   horizon_h |   orientation_from_train | premay_all_positive   | one_bar_lag_ok   |   control_ratio_premay_max |   oriented_validation_spread |   oriented_test_spread |   oriented_recent_spread | decision                          |
|:-----------------------|:-----------------------------------|------------:|-------------------------:|:----------------------|:-----------------|---------------------------:|-----------------------------:|-----------------------:|-------------------------:|:----------------------------------|
| a7ab3_fdd86cd8983e9d9b | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.438893 |                  0.0211199   |            0.0371599   |              0.0278053   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_5f3490d60d842a6e | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.443923 |                  0.0247989   |            0.0345525   |              0.0256028   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_7005b0d4aa2dce2e | L0_raw_forward_return              |           4 |                       -1 | True                  | True             |                   0.574381 |                  0.000349483 |            0.000705173 |              0.000693984 | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_7005b0d4aa2dce2e | L1_cross_sectional_relative_return |           4 |                       -1 | True                  | True             |                   0.574381 |                  0.000349483 |            0.000705173 |              0.000693984 | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_165c7d8966b27a17 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   0.612648 |                  0.0168662   |            0.0371154   |              0.038156    | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_12f53c28ae64a7c9 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.648849 |                  0.0174612   |            0.0260326   |              0.0141261   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_db425196e6b15b0a | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.661493 |                  0.0189146   |            0.0230662   |              0.0152592   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_4092255ee6888704 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   0.742223 |                  0.0283688   |            0.0204193   |              0.0447428   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_0b7b3deaa9bdd1bc | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.750091 |                  0.0213145   |            0.031414    |              0.0237997   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_0caf6e64238a4009 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.75522  |                  0.0138671   |            0.0179734   |              0.0219498   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_7935162ab6cc52c9 | L7_ranked_future_return            |           4 |                        1 | True                  | True             |                   0.777695 |                  0.0174483   |            0.0266896   |              0.0257525   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_87c3ee594944936f | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.781213 |                  0.036546    |            0.0232496   |              0.0188253   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_6406fc0cf7ff3b35 | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.818843 |                  0.0119762   |            0.0207953   |              0.0127102   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_3144de7015d18195 | L1_cross_sectional_relative_return |           1 |                        1 | True                  | True             |                   0.823571 |                  0.000244054 |            0.000274848 |              0.000559947 | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_3144de7015d18195 | L0_raw_forward_return              |           1 |                        1 | True                  | True             |                   0.823571 |                  0.000244054 |            0.000274848 |              0.000559947 | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_0bc78809db3a1428 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   0.828236 |                  0.0170234   |            0.0306543   |              0.045593    | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_f0f4c568b02b1b72 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.877438 |                  0.0083343   |            0.0218926   |              0.0216956   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_6e301587da1c1fa3 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.882557 |                  0.0204831   |            0.0265494   |              0.0345867   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_e5d6e69d28752387 | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.886676 |                  0.0187043   |            0.0261566   |              0.037109    | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_e142ac349de3313f | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.904059 |                  0.0076644   |            0.0161337   |              0.0102138   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_259e51a3d817578c | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.93     |                  0.00550839  |            0.0169654   |              0.0253293   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_6eb23cd8ce4aeef1 | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.935474 |                  0.00716361  |            0.0224839   |              0.024909    | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_3144de7015d18195 | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   0.947557 |                  0.0129939   |            0.014327    |              0.0217931   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_2af478d1ff284e21 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.948962 |                  0.0245258   |            0.0289143   |              0.0361537   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_3edc6f38cc9be3f3 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.948962 |                  0.0245258   |            0.0289143   |              0.0361537   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_da7270f10c2caee8 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.948962 |                  0.0245258   |            0.0289143   |              0.0361537   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_0b7b3deaa9bdd1bc | L1_cross_sectional_relative_return |           1 |                       -1 | True                  | True             |                   0.958687 |                  0.000213123 |            0.000325761 |              0.000330006 | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_0b7b3deaa9bdd1bc | L0_raw_forward_return              |           1 |                       -1 | True                  | True             |                   0.958687 |                  0.000213123 |            0.000325761 |              0.000330006 | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_6e301587da1c1fa3 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   0.963308 |                  0.0290778   |            0.0446459   |              0.059893    | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_d4939ee84cb32793 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.975123 |                  0.0195696   |            0.0246783   |              0.0324775   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_ced6188c184ada50 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   0.98199  |                  0.02751     |            0.0198761   |              0.0454216   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_2ad4a9e8d3c38900 | L7_ranked_future_return            |           4 |                        1 | True                  | True             |                   0.986254 |                  0.0101661   |            0.00683493  |              0.0120394   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_04daf24ce962db97 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   0.999732 |                  0.00842556  |            0.014248    |              0.0162893   | A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE |
| a7ab3_2af478d1ff284e21 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   1.01267  |                  0.0284173   |            0.0502835   |              0.0625932   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_3edc6f38cc9be3f3 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   1.01267  |                  0.0284173   |            0.0502835   |              0.0625932   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_da7270f10c2caee8 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   1.01267  |                  0.0284173   |            0.0502835   |              0.0625932   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_6eb23cd8ce4aeef1 | L7_ranked_future_return            |           4 |                        1 | True                  | True             |                   1.01945  |                  0.017643    |            0.0348654   |              0.0475618   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_9b74006f5f8908f8 | L7_ranked_future_return            |           4 |                        1 | True                  | True             |                   1.01945  |                  0.017643    |            0.0348654   |              0.0475618   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_39e2cf80d4b57fa7 | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   1.02143  |                  0.016126    |            0.0273136   |              0.0268116   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_249b631ed84be563 | L1_cross_sectional_relative_return |           1 |                       -1 | True                  | True             |                   1.02563  |                  0.000459874 |            0.00046741  |              0.000700631 | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_249b631ed84be563 | L0_raw_forward_return              |           1 |                       -1 | True                  | True             |                   1.02563  |                  0.000459874 |            0.00046741  |              0.000700631 | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_2942692cc4933504 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   1.03044  |                  0.0155721   |            0.0295514   |              0.0458983   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_f0f4c568b02b1b72 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   1.03044  |                  0.0155721   |            0.0295514   |              0.0458983   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_d4939ee84cb32793 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   1.03267  |                  0.0259417   |            0.0458025   |              0.061645    | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_7c68909e8aa7f6ea | L7_ranked_future_return            |           4 |                        1 | True                  | True             |                   1.03683  |                  0.016391    |            0.0373348   |              0.0201839   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_a40bddb7136ef900 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   1.03767  |                  0.0222395   |            0.0434469   |              0.0629826   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_27293c9fb29d33c4 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   1.03898  |                  0.0206761   |            0.0426063   |              0.0635733   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_2a0039bf30a6a7d0 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   1.07236  |                  0.018178    |            0.0397342   |              0.0605137   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_3ce43ff8d3208a0f | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   1.07336  |                  0.0118171   |            0.0190051   |              0.0293561   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_2a0039bf30a6a7d0 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   1.08041  |                  0.0155788   |            0.0212348   |              0.0314017   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_7935162ab6cc52c9 | L0_raw_forward_return              |           1 |                        1 | True                  | True             |                   1.09549  |                  0.000341098 |            0.000559111 |              0.00018803  | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_7935162ab6cc52c9 | L1_cross_sectional_relative_return |           1 |                        1 | True                  | True             |                   1.09549  |                  0.000341098 |            0.000559111 |              0.00018803  | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_e5d6e69d28752387 | L7_ranked_future_return            |           4 |                        1 | True                  | True             |                   1.10227  |                  0.022265    |            0.0473867   |              0.0642688   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_1f9142d27f055f5f | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   1.10849  |                  0.0187865   |            0.0227675   |              0.0420017   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_0bc78809db3a1428 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   1.11841  |                  0.00618802  |            0.0210187   |              0.0219292   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_0ec11b8f07b0f3e5 | L1_cross_sectional_relative_return |           1 |                       -1 | True                  | True             |                   1.11919  |                  0.000913429 |            0.00135093  |              0.001243    | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_0ec11b8f07b0f3e5 | L0_raw_forward_return              |           1 |                       -1 | True                  | True             |                   1.11919  |                  0.000913429 |            0.00135093  |              0.001243    | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_b5cbf40bc83635e6 | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   1.12143  |                  0.0207513   |            0.0280765   |              0.0388711   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_27293c9fb29d33c4 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   1.12973  |                  0.0155064   |            0.0238071   |              0.0341355   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_58203eba4254d6d4 | L7_ranked_future_return            |           1 |                        1 | True                  | True             |                   1.13254  |                  0.0206602   |            0.0280063   |              0.0390184   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_a40bddb7136ef900 | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   1.16648  |                  0.0156611   |            0.023945    |              0.0327818   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_9e4c76ac7a668ba0 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   1.1885   |                  0.00888189  |            0.0160615   |              0.021792    | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_28e51a0e6693cfec | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   1.1935   |                  0.00765376  |            0.0168438   |              0.0110731   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_87c3ee594944936f | L7_ranked_future_return            |           4 |                        1 | True                  | True             |                   1.19399  |                  0.0182916   |            0.0191297   |              0.0179948   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_5d4caf4e15cc5120 | L1_cross_sectional_relative_return |           1 |                       -1 | True                  | True             |                   1.20142  |                  0.000483165 |            0.000879204 |              0.00121856  | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_5d4caf4e15cc5120 | L0_raw_forward_return              |           1 |                       -1 | True                  | True             |                   1.20142  |                  0.000483165 |            0.000879204 |              0.00121856  | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_5f3490d60d842a6e | L1_cross_sectional_relative_return |           1 |                        1 | True                  | True             |                   1.22482  |                  0.000232247 |            0.000522389 |              0.000887754 | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_5f3490d60d842a6e | L0_raw_forward_return              |           1 |                        1 | True                  | True             |                   1.22482  |                  0.000232247 |            0.000522389 |              0.000887754 | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_1f9142d27f055f5f | L7_ranked_future_return            |           1 |                       -1 | True                  | True             |                   1.24076  |                  0.0170283   |            0.0137769   |              0.0206701   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_b5cbf40bc83635e6 | L7_ranked_future_return            |           4 |                        1 | True                  | True             |                   1.25114  |                  0.0233389   |            0.0493889   |              0.0685136   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_58203eba4254d6d4 | L7_ranked_future_return            |           4 |                        1 | True                  | True             |                   1.2536   |                  0.0233748   |            0.0494029   |              0.0686413   | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_fdd86cd8983e9d9b | L1_cross_sectional_relative_return |           1 |                        1 | True                  | True             |                   1.29497  |                  0.000212061 |            0.000646401 |              0.000882776 | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_fdd86cd8983e9d9b | L0_raw_forward_return              |           1 |                        1 | True                  | True             |                   1.29497  |                  0.000212061 |            0.000646401 |              0.000882776 | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_177d9ba31efe9ca9 | L1_cross_sectional_relative_return |           1 |                        1 | True                  | True             |                   1.30742  |                  0.000438621 |            0.000886428 |              0.000977826 | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_177d9ba31efe9ca9 | L0_raw_forward_return              |           1 |                        1 | True                  | True             |                   1.30742  |                  0.000438621 |            0.000886428 |              0.000977826 | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_d4939ee84cb32793 | L0_raw_forward_return              |           4 |                       -1 | True                  | True             |                   1.31463  |                  0.000206583 |            0.00123419  |              0.00080159  | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_d4939ee84cb32793 | L1_cross_sectional_relative_return |           4 |                       -1 | True                  | True             |                   1.31463  |                  0.000206583 |            0.00123419  |              0.00080159  | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_209db83affacfa08 | L1_cross_sectional_relative_return |           1 |                       -1 | True                  | True             |                   1.3173   |                  0.000457179 |            0.00088332  |              0.000930002 | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_209db83affacfa08 | L0_raw_forward_return              |           1 |                       -1 | True                  | True             |                   1.3173   |                  0.000457179 |            0.00088332  |              0.000930002 | HOLD_A7AB6_CONTROL_DOMINATED      |
| a7ab3_2851ccb20396dab9 | L7_ranked_future_return            |           4 |                       -1 | True                  | True             |                   1.3423   |                  0.0161969   |            0.0168197   |              0.0147926   | HOLD_A7AB6_CONTROL_DOMINATED      |
