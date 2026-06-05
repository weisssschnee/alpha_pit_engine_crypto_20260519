# CRYPTO A7LS-1 MULTI-ARM BLUEPRINT GENERATION

Generated: 2026-06-05T03:53:36Z

## Decision

`PASS_A7LS1_MULTI_ARM_BLUEPRINT_GENERATION_READY_FOR_A7LS2`

A7LS-1 generates the four-arm checkpoint large-search blueprint atlas. The full 240k atlas is stored externally; repo artifacts keep the executable materialization and numeric checkpoint queues.

## Manifest

```json
{
  "arm_count": 4,
  "authorizes_a7ls2_materialization_wave": true,
  "authorizes_a7ls3_numeric_wave": false,
  "authorizes_alpha_proof": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7LS1_MULTI_ARM_BLUEPRINT_GENERATION_READY_FOR_A7LS2",
  "executes_generation": true,
  "executes_materialization": false,
  "executes_numeric_probe": false,
  "executes_search": false,
  "full_blueprint_pool_external_path": "G:/AlphaFactory_CryptoData/research_runtime/a7ls1_multi_arm_blueprint_generation_20260605/a7ls1_full_blueprint_pool.csv",
  "full_blueprint_pool_rows": 240000,
  "generated_at": "2026-06-05T03:53:36Z",
  "materialization_wave_rows": 40000,
  "numeric_wave_rows": 8000,
  "raw_arm_generated_rows": 60000,
  "raw_arm_numeric_active_axes": 10,
  "raw_arm_numeric_rows": 2000,
  "source_decision": "PASS_A7LS0_CHECKPOINT_LARGE_SEARCH_CONTRACT_READY",
  "source_stage": "A7LS-0",
  "stage": "A7LS-1"
}
```

## Arm Summary

| a7ls_arm   |   generated_rows |   unique_expressions |   semantic_pair_count |   motif_count |   skeleton_count |   primary_field_count |   secondary_field_count |   materialization_rows |   materialization_semantic_pairs |   materialization_motifs |   materialization_skeletons |   numeric_rows |   numeric_semantic_pairs |   numeric_motifs |   numeric_skeletons |
|:-----------|-----------------:|---------------------:|----------------------:|--------------:|-----------------:|----------------------:|------------------------:|-----------------------:|---------------------------------:|-------------------------:|----------------------------:|---------------:|-------------------------:|-----------------:|--------------------:|
| A7LS_A     |            60000 |                60000 |                     6 |            12 |              115 |                    10 |                       7 |                  10000 |                                6 |                       12 |                         115 |           2000 |                        6 |               12 |                  97 |
| A7LS_B     |            60000 |                60000 |                    55 |            10 |              114 |                    49 |                      16 |                  10000 |                               52 |                       10 |                         114 |           2000 |                       16 |                9 |                 104 |
| A7LS_C     |            60000 |                60000 |                    14 |            12 |              104 |                    29 |                       8 |                  10000 |                               14 |                       12 |                         104 |           2000 |                       12 |               12 |                  92 |
| A7LS_D     |            60000 |                60000 |                    11 |             5 |               51 |                    20 |                      10 |                  10000 |                               11 |                        5 |                          51 |           2000 |                        8 |                5 |                  46 |

## Raw Arm Axis Summary

| primary_semantic   |   rows |   semantic_pairs |   motifs |
|:-------------------|-------:|-----------------:|---------:|
| price_like         |  12412 |               10 |       10 |
| basis_premium_like |  11160 |                9 |       10 |
| funding_state_like |   8728 |                8 |       10 |
| open_interest_like |   8728 |                7 |       10 |
| positioning_like   |   6278 |                6 |       10 |
| taker_flow_like    |   5008 |                5 |       10 |
| liquidity_like     |   3828 |                4 |       10 |
| volatility_like    |   2522 |                3 |        6 |
| listing_age_like   |   1276 |                2 |        6 |
| regime_state       |     60 |                1 |        1 |

## Output Artifacts

| path                                                                                                                                      |   rows | location   | purpose                             |
|:------------------------------------------------------------------------------------------------------------------------------------------|-------:|:-----------|:------------------------------------|
| G:/AlphaFactory_CryptoData/research_runtime/a7ls1_multi_arm_blueprint_generation_20260605/a7ls1_full_blueprint_pool.csv                   | 240000 | external   | full 240k generated blueprint atlas |
| G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519/runtime/a7ls1_multi_arm_blueprint_generation/a7ls1_materialization_wave_queue.csv |  40000 | repo       | 40k materialization wave queue      |
| G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519/runtime/a7ls1_multi_arm_blueprint_generation/a7ls1_numeric_wave_queue.csv         |   8000 | repo       | 8k numeric checkpoint wave queue    |

## Boundary

```text
generation executed: true
materialization executed: false
numeric probe executed: false
search/proof/shadow/live: false
```