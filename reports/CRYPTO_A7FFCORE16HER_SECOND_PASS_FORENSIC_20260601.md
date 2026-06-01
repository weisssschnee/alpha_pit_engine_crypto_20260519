# CRYPTO A7FF-CORE16HER SECOND-PASS FORENSIC

Generated: 2026-06-01T12:41:55Z

## Decision

`PASS_A7FFCORE16HER_SECOND_PASS_FORENSIC_READY_FOR_CORE16I`

CORE16HER freezes CORE16HE. The second-pass probe produced enough raw candidate supply and four families, but failed concentration and H2 floor gates. A balanced pre-seed queue is possible only if H2 near-miss rows remain explicitly forensic and cannot be promoted as alpha seeds.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core16i": true,
  "authorizes_core17": false,
  "authorizes_formula_generation": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "balanced_queue_family_count": 4,
  "balanced_queue_h2_count": 12,
  "balanced_queue_meets_targets": true,
  "balanced_queue_near_miss_count": 3,
  "balanced_queue_non_l5_share": 0.8854166666666666,
  "balanced_queue_size": 96,
  "balanced_queue_strict_count": 93,
  "balanced_queue_top_family_share": 0.34375,
  "decision": "PASS_A7FFCORE16HER_SECOND_PASS_FORENSIC_READY_FOR_CORE16I",
  "dominant_failure": "breadth_gate_near_pass_with_h2_floor_shortfall",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T12:41:55Z",
  "next_allowed": "A7FF-CORE16I balanced interaction pre-seed queue audit",
  "source_candidate_count": 357,
  "source_decision": "HOLD_A7FFCORE16HE_SECOND_PASS_BREADTH_INSUFFICIENT",
  "source_family_count": 4,
  "source_stage": "A7FF-CORE16HE",
  "stage": "A7FF-CORE16HER"
}
```

## Source Family Summary

| second_pass_family     |   response_rows |   blueprint_count |   candidate_count |   near_miss_count |   label_family_count |   operator_count |   median_control_ratio |
|:-----------------------|----------------:|------------------:|------------------:|------------------:|---------------------:|-----------------:|-----------------------:|
| H1_I5_deconcentration  |           13824 |               864 |               200 |               237 |                    4 |                3 |                9.45841 |
| H0_I3_deconcentration  |            6048 |               378 |               128 |               106 |                    4 |                3 |                7.99019 |
| H3_cross_family_bridge |           11520 |               720 |                20 |                50 |                    4 |                2 |                7.34262 |
| H2_I4_near_miss_repair |            8960 |               560 |                 9 |                41 |                    4 |                2 |                6.16451 |

## Balanced Queue Summary

| second_pass_family     | queue_role                        |   rows |   lag_ok_count |   median_control_ratio |   label_family_count |   operator_count |
|:-----------------------|:----------------------------------|-------:|---------------:|-----------------------:|---------------------:|-----------------:|
| H1_I5_deconcentration  | strict_candidate                  |     33 |             33 |               0.71876  |                    3 |                2 |
| H0_I3_deconcentration  | strict_candidate                  |     31 |             31 |               0.555319 |                    3 |                2 |
| H3_cross_family_bridge | strict_candidate                  |     20 |             15 |               0.830484 |                    4 |                2 |
| H2_I4_near_miss_repair | strict_candidate                  |      9 |              4 |               0.738901 |                    4 |                2 |
| H2_I4_near_miss_repair | forensic_near_miss_not_alpha_seed |      3 |              3 |               1.01141  |                    3 |                1 |

## Repair Actions

| action_id                 | action                                                                                                           | reason                                                                            |
|:--------------------------|:-----------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|
| R0_balanced_preseed_queue | use capped H0/H1, preserve H3, and top up H2 with explicitly flagged near-miss rows                              | strict candidates are abundant but concentrated; H2 strict count is 9 vs floor 12 |
| R1_no_core17_yet          | do not authorize objective seed policy until near-miss rows are either upgraded or excluded by a dedicated audit | balanced queue may need forensic rows to satisfy H2 breadth                       |
| R2_execute_core16i        | run balanced pre-seed queue audit with role-aware near-miss isolation                                            | supply is now nonzero enough to test queue governance, not search                 |

## Next Contract

```json
{
  "authorized": true,
  "executes_replay": false,
  "executes_search": false,
  "forbidden": [
    "objective seed promotion from near-miss rows",
    "open grammar FormulaGen",
    "bounded replay",
    "large search",
    "alpha proof",
    "shadow/paper/live"
  ],
  "inputs": [
    "CORE16HE second-pass candidates",
    "CORE16HE near-miss rows",
    "CORE16H cap policy"
  ],
  "name": "balanced interaction pre-seed queue audit",
  "queue_targets": {
    "family_count": 4,
    "h2_floor": 12,
    "near_miss_rows_must_be_role_flagged": true,
    "non_l5_share_min": 0.4,
    "queue_size": 96,
    "top_family_share_max": 0.45
  },
  "stage": "A7FF-CORE16I"
}
```
