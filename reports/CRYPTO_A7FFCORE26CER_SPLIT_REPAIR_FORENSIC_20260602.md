# CRYPTO A7FF-CORE26CER SPLIT REPAIR FORENSIC

Generated: 2026-06-01T18:02:33Z

## Decision

`PASS_A7FFCORE26CER_SPLIT_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE26D`

CORE26CER freezes the CORE26CE hold. It does not authorize replay, search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core26d_contract": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE26CER_SPLIT_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE26D",
  "dominant_failure": "single_lane_clean_supply_after_split_repair",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T18:02:33Z",
  "next_allowed": "A7FF-CORE26D non-S0 lane independence repair contract",
  "s0_clean_count": 4,
  "s3_clean_count": 0,
  "s3_near_miss_count": 4,
  "source_decision": "HOLD_A7FFCORE26CE_SPLIT_REPAIR_INSUFFICIENT",
  "source_stage": "A7FF-CORE26CE",
  "stage": "A7FF-CORE26CER",
  "three_split_clean_count": 4,
  "three_split_clean_lane_count": 1
}
```

## Diagnosis

| finding            | value                                       | interpretation                                         |
|:-------------------|:--------------------------------------------|:-------------------------------------------------------|
| clean_count        | 4                                           | strict three-split clean candidates after repair       |
| clean_lane_count   | 1                                           | strict clean lane breadth                              |
| s0_clean_count     | 4                                           | S0 is the only productive clean lane                   |
| s3_clean_count     | 0                                           | S3 repair did not reach strict clean                   |
| s3_near_miss_count | 4                                           | S3 still has near-miss structure worth isolated repair |
| dominant_failure   | single_lane_clean_supply_after_split_repair | cannot advance to replay with one clean lane only      |

## Lane Summary From CORE26CE

| seed_lane                  |   candidates |   clean_3_split |   near_2_split |   median_control |   median_spread |
|:---------------------------|-------------:|----------------:|---------------:|-----------------:|----------------:|
| S0_positioning_price_basis |          180 |               4 |             20 |          3.03872 |    -0.000165727 |
| S3_cross_family_bridge     |          180 |               0 |              4 |          5.44    |    -0.000422158 |

## Recommended Actions

| next_stage                          | action                                   | rationale                                                                                                   | authorized   |
|:------------------------------------|:-----------------------------------------|:------------------------------------------------------------------------------------------------------------|:-------------|
| A7FF-CORE26D                        | non-S0 lane independence repair contract | S0 has local clean evidence, but replay/search requires at least one additional independent executable lane | True         |
| A7FF-CORE27 bounded replay contract | blocked                                  | clean supply remains 4 candidates / 1 lane                                                                  | False        |
