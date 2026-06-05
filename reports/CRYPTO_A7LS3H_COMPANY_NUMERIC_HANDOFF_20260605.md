# CRYPTO A7LS-3H COMPANY NUMERIC HANDOFF

Generated: 2026-06-05T05:14:13Z

## Decision

`PASS_A7LS3H_COMPANY_NUMERIC_HANDOFF_READY`

A7LS-3H converts the local A7LS-3 timeout into a company-machine async numeric handoff. It uses A7LS-2 activity-ok materialized rows, cuts 32-row shards, and records resume/checkpoint rules.

## Manifest

```json
{
  "arm_count": 4,
  "authorizes_alpha_proof": false,
  "authorizes_company_numeric_async": true,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7LS3H_COMPANY_NUMERIC_HANDOFF_READY",
  "executes_numeric_probe": false,
  "executes_search": false,
  "generated_at": "2026-06-05T05:14:13Z",
  "handoff_queue_rows": 1024,
  "input_activity_ok_rows": 1273,
  "local_a7ls3_timeout": true,
  "rows_per_shard": 32,
  "shard_count": 32,
  "source_a7ls2_decision": "PASS_A7LS2_FIRST_CHECKPOINT_MATERIALIZATION_READY",
  "source_local_a7ls3_decision": "HOLD_A7LS3_NUMERIC_CHECKPOINT_WEAK",
  "stage": "A7LS-3H"
}
```

## Queue Summary

| a7ls_arm   | semantic_pair                     |   rows |   motif_count |   skeleton_count |   median_materialization_score |
|:-----------|:----------------------------------|-------:|--------------:|-----------------:|-------------------------------:|
| A7LS_A     | basis_premium_like                |    303 |             2 |               24 |                       0.994272 |
| A7LS_B     | liquidity_like                    |     47 |             1 |                5 |                       0.981798 |
| A7LS_B     | positioning_like                  |     45 |             1 |                5 |                       0.999149 |
| A7LS_B     | listing_age_like                  |     43 |             1 |                3 |                       0.981769 |
| A7LS_B     | funding_state_like                |     42 |             1 |                5 |                       0.958936 |
| A7LS_B     | taker_flow_like                   |     40 |             1 |                5 |                       0.999149 |
| A7LS_B     | volatility_like                   |     38 |             1 |                5 |                       0.981512 |
| A7LS_B     | basis_premium_like                |     34 |             1 |                9 |                       0.993835 |
| A7LS_B     | open_interest_like                |     32 |             1 |                9 |                       0.998863 |
| A7LS_B     | price_like                        |     31 |             1 |                9 |                       0.998739 |
| A7LS_B     | volatility_like|listing_age_like  |      5 |             1 |                5 |                       0.981211 |
| A7LS_B     | taker_flow_like|liquidity_like    |      4 |             1 |                2 |                       0.998676 |
| A7LS_B     | regime_state                      |      3 |             1 |                2 |                       0.981798 |
| A7LS_B     | funding_state_like|liquidity_like |      2 |             1 |                2 |                       0.895979 |
| A7LS_B     | positioning_like|liquidity_like   |      1 |             1 |                1 |                       0.997237 |
| A7LS_C     | basis_premium_like                |     66 |             1 |                3 |                       0.998533 |
| A7LS_D     | low_prior_axes|basis_premium_like |    201 |             1 |               16 |                       0.979184 |
| A7LS_D     | basis_premium_like                |     65 |             1 |                3 |                       0.998529 |
| A7LS_D     | liquidity_like                    |     20 |             1 |                2 |                       0.998935 |
| A7LS_D     | low_prior_axes                    |      2 |             1 |                1 |                       0.99947  |

## Shard Plan

| company_numeric_shard   | a7ls_arm   |   rows |   semantic_pair_count |   motif_count |   skeleton_count |
|:------------------------|:-----------|-------:|----------------------:|--------------:|-----------------:|
| a7ls3h_s000             | A7LS_A     |     32 |                     1 |             1 |                6 |
| a7ls3h_s001             | A7LS_A     |     32 |                     1 |             2 |                9 |
| a7ls3h_s002             | A7LS_A     |     32 |                     1 |             1 |                6 |
| a7ls3h_s003             | A7LS_A     |     32 |                     1 |             1 |                7 |
| a7ls3h_s004             | A7LS_A     |     32 |                     1 |             1 |                9 |
| a7ls3h_s005             | A7LS_A     |     32 |                     1 |             2 |               10 |
| a7ls3h_s006             | A7LS_A     |     32 |                     1 |             1 |                7 |
| a7ls3h_s007             | A7LS_A     |     32 |                     1 |             2 |               11 |
| a7ls3h_s008             | A7LS_B     |     32 |                     3 |             2 |               13 |
| a7ls3h_s009             | A7LS_B     |     32 |                     4 |             2 |               11 |
| a7ls3h_s010             | A7LS_B     |     32 |                     7 |             2 |               11 |
| a7ls3h_s011             | A7LS_B     |     32 |                     7 |             2 |                6 |
| a7ls3h_s012             | A7LS_B     |     32 |                     6 |             2 |                9 |
| a7ls3h_s013             | A7LS_B     |     32 |                     8 |             2 |                7 |
| a7ls3h_s014             | A7LS_B     |     32 |                     6 |             2 |                6 |
| a7ls3h_s015             | A7LS_B     |     32 |                     6 |             2 |                6 |
| a7ls3h_s016             | A7LS_C     |     32 |                     1 |             1 |                3 |
| a7ls3h_s017             | A7LS_C     |     32 |                     1 |             1 |                2 |
| a7ls3h_s018             | A7LS_C     |      2 |                     1 |             1 |                1 |
| a7ls3h_s018             | A7LS_D     |     30 |                     4 |             2 |                5 |
| a7ls3h_s019             | A7LS_D     |     32 |                     2 |             2 |                7 |
| a7ls3h_s020             | A7LS_D     |     32 |                     3 |             2 |                5 |
| a7ls3h_s021             | A7LS_D     |     32 |                     2 |             2 |                8 |
| a7ls3h_s022             | A7LS_D     |     32 |                     2 |             2 |                6 |
| a7ls3h_s023             | A7LS_D     |     32 |                     3 |             2 |                8 |
| a7ls3h_s024             | A7LS_D     |     32 |                     2 |             2 |                8 |
| a7ls3h_s025             | A7LS_D     |     32 |                     2 |             2 |               10 |
| a7ls3h_s026             | A7LS_B     |     30 |                     5 |             2 |                8 |
| a7ls3h_s026             | A7LS_D     |      2 |                     1 |             1 |                1 |
| a7ls3h_s027             | A7LS_B     |     32 |                     7 |             2 |               11 |
| a7ls3h_s028             | A7LS_B     |     32 |                     4 |             1 |                2 |
| a7ls3h_s029             | A7LS_A     |     15 |                     1 |             1 |                5 |
| a7ls3h_s029             | A7LS_B     |     17 |                     4 |             1 |                3 |
| a7ls3h_s030             | A7LS_A     |     17 |                     1 |             1 |                6 |
| a7ls3h_s030             | A7LS_D     |     15 |                     1 |             1 |                5 |
| a7ls3h_s031             | A7LS_A     |     15 |                     1 |             1 |                5 |
| a7ls3h_s031             | A7LS_D     |     17 |                     1 |             1 |                7 |

## Command Template

```json
{
  "checkpoint_policy": {
    "parallelism_recommended": "4-8 shards depending on company-machine memory",
    "resume_rule": "skip shard if manifest exists and returncode==0",
    "rows_per_shard": 32,
    "shard_count": 32,
    "timeout_seconds_per_shard": 3600
  },
  "per_shard_env": {
    "A7FF8_AUTH_DECISION": "PASS_A7LS2_FIRST_CHECKPOINT_MATERIALIZATION_READY",
    "A7FF8_AUTH_MANIFEST": "G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519/runtime/a7ls2_sharded_materialization_wave/a7ls2_manifest.json",
    "A7FF8_FAST_NUMERIC_CAP": "32",
    "A7FF8_FILE_PREFIX": "a7ls3h_${SHARD}",
    "A7FF8_MATERIALIZE_CAP": "32",
    "A7FF8_PORTFOLIO_CAP": "64",
    "A7FF8_QUEUE_LIMIT": "32",
    "A7FF8_QUEUE_PATH": "G:/AlphaFactory_CryptoData/research_runtime/a7ls3h_company_numeric/${SHARD}/queue.csv",
    "A7FF8_REPORT": "G:/AlphaFactory_CryptoData/research_runtime/a7ls3h_company_numeric/${SHARD}/A7LS3H_NUMERIC_DETAIL.md",
    "A7FF8_RUNTIME": "G:/AlphaFactory_CryptoData/research_runtime/a7ls3h_company_numeric/${SHARD}",
    "A7FF8_STAGE": "A7LS-3H-${SHARD}",
    "A7FF8_WRITE_CONTROL_DETAIL": "1"
  },
  "runner": "scripts/crypto_a7ff8_expanded_numeric_probe.py",
  "stage": "A7LS-3H"
}
```

## Boundary

```text
handoff generated: true
local numeric execution: not in this stage
search/proof/shadow/live: false
```