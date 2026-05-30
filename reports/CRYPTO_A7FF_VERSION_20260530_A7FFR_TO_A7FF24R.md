# CRYPTO A7FF VERSION 20260530: A7FF-R TO A7FF-24R

Generated: 2026-05-30T06:31:35Z

## Version Decision

`PASS_A7FF_VERSION_FILE_BUILT`

This is the canonical version file for the A7FF-R -> A7FF-23R -> A7FF-24R line. Future A7FF work should use this format: one human version file under `reports/`, plus machine-readable indexes under a matching `runtime/a7ff_version_*` directory.

## Upload / Git Status At Generation

```json
{
  "origin_main_at_generation": "f3e3e347e0e8c120552fa07353d2cfe303923f91",
  "source_artifacts_uploaded_at_generation": true,
  "source_commit_head_at_generation": "f3e3e347e0e8c120552fa07353d2cfe303923f91",
  "version_file_pending_commit_at_generation": true,
  "worktree_status_at_generation": "?? reports/CRYPTO_A7FF_VERSION_20260530_A7FFR_TO_A7FF24R.md\n?? runtime/a7ff_version_20260530/\n?? scripts/crypto_a7ff_version_file_20260530.py"
}
```

Note: this version file itself is committed after generation. `source_artifacts_uploaded_at_generation` refers to the source artifacts summarized here, not to this newly generated version file.

## Scope

Included stages:

```text
A7FF-R0/R1/R2/R3/R4/R5
A7FF-23R
A7FF-24R
```

Excluded from this version:

```text
numeric probe execution
replay execution
formula search
large search
alpha proof
shadow / paper / live
```

## Key Stage Decisions

| stage | decision |
|---|---|
| A7FF-R1 | `PASS_A7FFR1_FIELD_ONTOLOGY_V3_BUILT` |
| A7FF-R5 | `PASS_A7FFR5_PROMOTION_REDESIGN_READY_BUT_SEARCH_STILL_HOLD` |
| A7FF-23R | `PASS_A7FF23R_DERIVED_FACTOR_EXPANSION_CONTRACT_READY_FOR_A7FF24R_PLAN` |
| A7FF-24R | `PASS_A7FF24R_DRY_GENERATION_PLAN_READY_FOR_COMPANY_NUMERIC` |

## Main Counts

```json
{
  "blueprint_count": 20599,
  "company_shard_count": 12,
  "company_wave_queue_count": 2400,
  "derived_field_catalog_rows": 848,
  "formula_index_rows": 20599,
  "materialization_queue_count": 3000,
  "motif_count": 10,
  "semantic_pair_count": 15
}
```

## Complete Formula Index

The complete formula list is not embedded inline because it has `20599` rows. It is stored here:

```text
G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ff_version_20260530\a7ff_v20260530_formula_index.csv
```

Columns include:

```text
blueprint_id
level
candidate_role
generation_priority
semantic_pair
motif
primary_field / secondary_field
primary_transform / secondary_transform
skeleton_key
production_key
queue membership
expression
```

## Formula Samples

| blueprint_id             | level                     | semantic_pair      | motif   | primary_field        |   secondary_field | primary_transform   |   secondary_transform | in_materialization_queue   | in_company_numeric_wave_queue   | expression                                  |
|:-------------------------|:--------------------------|:-------------------|:--------|:---------------------|------------------:|:--------------------|----------------------:|:---------------------------|:--------------------------------|:--------------------------------------------|
| a7ff24r_547c0ff8380f3778 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | abs_zmean_8h        |                   nan | True                       | True                            | Abs(ZScore(Mean(mark_index_basis_bps,8)))   |
| a7ff24r_7f71b2e363dddbd6 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | abs_zmean_168h      |                   nan | True                       | True                            | Abs(ZScore(Mean(mark_index_basis_bps,168))) |
| a7ff24r_d7ef0776f1dae5df | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | abs_zmean_24h       |                   nan | True                       | True                            | Abs(ZScore(Mean(mark_index_basis_bps,24)))  |
| a7ff24r_e582d2a2908a95d8 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | abs_zmean_72h       |                   nan | True                       | True                            | Abs(ZScore(Mean(mark_index_basis_bps,72)))  |
| a7ff24r_1313bae0f47d683a | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | mean_168h           |                   nan | True                       | True                            | Mean(mark_index_basis_bps,168)              |
| a7ff24r_1c3b5e472e010cc0 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | mean_4h             |                   nan | True                       | True                            | Mean(mark_index_basis_bps,4)                |
| a7ff24r_3c18085739c75d99 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | decay_168h          |                   nan | True                       | True                            | Decay(mark_index_basis_bps,168)             |
| a7ff24r_49df8a5d77c3bce5 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | mean_24h            |                   nan | True                       | True                            | Mean(mark_index_basis_bps,24)               |
| a7ff24r_57e00327a34e91e3 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | delta_24h           |                   nan | True                       | True                            | Delta(mark_index_basis_bps,24)              |
| a7ff24r_5e3756c09dd9800d | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | mean_1h             |                   nan | True                       | True                            | Mean(mark_index_basis_bps,1)                |
| a7ff24r_6511aa6092778791 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | mean_2h             |                   nan | True                       | True                            | Mean(mark_index_basis_bps,2)                |
| a7ff24r_6a8e4e33dbe4b09c | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | delta_168h          |                   nan | True                       | True                            | Delta(mark_index_basis_bps,168)             |
| a7ff24r_6b9e4107d4ce11d4 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | delta_4h            |                   nan | True                       | True                            | Delta(mark_index_basis_bps,4)               |
| a7ff24r_858ff2210f276fcf | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | delta_12h           |                   nan | True                       | True                            | Delta(mark_index_basis_bps,12)              |
| a7ff24r_8bf0eefef7542ccd | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | delta_1h            |                   nan | True                       | True                            | Delta(mark_index_basis_bps,1)               |
| a7ff24r_8ee65f030b52e93f | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | decay_24h           |                   nan | True                       | True                            | Decay(mark_index_basis_bps,24)              |
| a7ff24r_a39fead768620491 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | mean_336h           |                   nan | True                       | True                            | Mean(mark_index_basis_bps,336)              |
| a7ff24r_acdf1de7772e8224 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | delta_336h          |                   nan | True                       | True                            | Delta(mark_index_basis_bps,336)             |
| a7ff24r_ba91531e12984292 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | mean_8h             |                   nan | True                       | True                            | Mean(mark_index_basis_bps,8)                |
| a7ff24r_bb78ec0b9ce75244 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | mean_72h            |                   nan | True                       | True                            | Mean(mark_index_basis_bps,72)               |
| a7ff24r_daaa1b56bc5d5709 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | mean_12h            |                   nan | True                       | True                            | Mean(mark_index_basis_bps,12)               |
| a7ff24r_e2c62815ca1308e7 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | decay_8h            |                   nan | True                       | True                            | Decay(mark_index_basis_bps,8)               |
| a7ff24r_e66cb2221d4873e6 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | decay_72h           |                   nan | True                       | True                            | Decay(mark_index_basis_bps,72)              |
| a7ff24r_eab92902c63036e3 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | delta_2h            |                   nan | True                       | True                            | Delta(mark_index_basis_bps,2)               |
| a7ff24r_eb94ce69b7faa44c | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | delta_72h           |                   nan | True                       | True                            | Delta(mark_index_basis_bps,72)              |
| a7ff24r_ec49ba0ff46743d0 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | delta_48h           |                   nan | True                       | True                            | Delta(mark_index_basis_bps,48)              |
| a7ff24r_fad5886189793630 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | delta_8h            |                   nan | True                       | True                            | Delta(mark_index_basis_bps,8)               |
| a7ff24r_ffbf24e72b8becc7 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | mean_48h            |                   nan | True                       | True                            | Mean(mark_index_basis_bps,48)               |
| a7ff24r_44729f0f6d18b9fe | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | zmean_2h            |                   nan | True                       | True                            | ZScore(Mean(mark_index_basis_bps,2))        |
| a7ff24r_49641183569fa632 | L1_single_field_transform | basis_premium_like | single  | mark_index_basis_bps |               nan | zmean_1h            |                   nan | True                       | True                            | ZScore(Mean(mark_index_basis_bps,1))        |

## Formula Family Summary

| level                          | semantic_pair                          | motif               |   formula_count |   materialization_count |   company_wave_count |   skeleton_count |   production_key_count |
|:-------------------------------|:---------------------------------------|:--------------------|----------------:|------------------------:|---------------------:|-----------------:|-----------------------:|
| L4_factor_candidate_probe      | basis_premium_like\|positioning_like   | signed_spread       |            1178 |                       0 |                    0 |                5 |                   1178 |
| L4_factor_candidate_probe      | basis_premium_like\|positioning_like   | mean_reversion_gate |            1021 |                       0 |                    0 |                5 |                   1021 |
| L4_factor_candidate_probe      | basis_premium_like\|positioning_like   | smooth_mul          |             885 |                       0 |                    0 |                5 |                    885 |
| L4_factor_candidate_probe      | basis_premium_like\|funding_like       | signed_spread       |             792 |                       0 |                    0 |                8 |                    792 |
| L4_factor_candidate_probe      | basis_premium_like\|funding_like       | mean_reversion_gate |             643 |                       0 |                    0 |                7 |                    643 |
| L4_factor_candidate_probe      | basis_premium_like\|funding_like       | relative_shock      |             629 |                       0 |                    0 |                6 |                    629 |
| L4_factor_candidate_probe      | basis_premium_like\|positioning_like   | spread_rank         |             552 |                       0 |                    0 |                4 |                    552 |
| L3_state_conditioned_feature   | funding_like\|positioning_like         | mean_reversion_gate |             512 |                      97 |                    0 |                9 |                    512 |
| L3_state_conditioned_feature   | funding_like\|positioning_like         | smooth_mul          |             512 |                       0 |                    0 |                9 |                    512 |
| L3_state_conditioned_feature   | funding_like\|positioning_like         | signed_spread       |             512 |                       5 |                    0 |                9 |                    512 |
| L3_state_conditioned_feature   | funding_like\|positioning_like         | relative_shock      |             512 |                      65 |                    0 |                9 |                    512 |
| L4_factor_candidate_probe      | basis_premium_like\|positioning_like   | relative_shock      |             485 |                       0 |                    0 |                2 |                    485 |
| L3_state_conditioned_feature   | basis_premium_like\|funding_like       | smooth_mul          |             482 |                       0 |                    0 |                9 |                    482 |
| L3_state_conditioned_feature   | basis_premium_like\|funding_like       | signed_spread       |             482 |                     219 |                   19 |                9 |                    482 |
| L3_state_conditioned_feature   | funding_like\|positioning_like         | spread_rank         |             472 |                       0 |                    0 |                9 |                    472 |
| L3_state_conditioned_feature   | funding_like\|positioning_like         | sub                 |             466 |                       0 |                    0 |                9 |                    466 |
| L3_state_conditioned_feature   | basis_premium_like\|funding_like       | relative_shock      |             462 |                     314 |                  314 |                8 |                    462 |
| L3_state_conditioned_feature   | funding_like\|positioning_like         | mul                 |             461 |                      82 |                    0 |                9 |                    461 |
| L4_factor_candidate_probe      | funding_like\|positioning_like         | signed_spread       |             450 |                       0 |                    0 |                9 |                    450 |
| L2_typed_two_field_interaction | basis_premium_like\|volatility_like    | smooth_mul          |             439 |                     129 |                  129 |                8 |                    439 |
| L3_state_conditioned_feature   | funding_like\|positioning_like         | gated_sign          |             421 |                     162 |                   13 |                9 |                    421 |
| L3_state_conditioned_feature   | funding_like\|positioning_like         | safe_div_abs        |             420 |                       2 |                    0 |                9 |                    420 |
| L4_factor_candidate_probe      | funding_like\|positioning_like         | mean_reversion_gate |             384 |                       0 |                    0 |                7 |                    384 |
| L3_state_conditioned_feature   | basis_premium_like\|funding_like       | mean_reversion_gate |             361 |                     256 |                  256 |                9 |                    361 |
| L4_factor_candidate_probe      | basis_premium_like\|funding_like       | smooth_mul          |             352 |                       0 |                    0 |                6 |                    352 |
| L4_factor_candidate_probe      | funding_like\|positioning_like         | relative_shock      |             342 |                       0 |                    0 |                6 |                    342 |
| L4_factor_candidate_probe      | basis_premium_like\|funding_like       | spread_rank         |             274 |                       0 |                    0 |                5 |                    274 |
| L3_state_conditioned_feature   | basis_premium_like\|funding_like       | spread_rank         |             231 |                       0 |                    0 |                8 |                    231 |
| L4_factor_candidate_probe      | funding_like\|positioning_like         | smooth_mul          |             217 |                       0 |                    0 |                6 |                    217 |
| L2_typed_two_field_interaction | basis_premium_like\|price_like         | smooth_mul          |             212 |                     172 |                  172 |                8 |                    212 |
| L3_state_conditioned_feature   | basis_premium_like\|funding_like       | gated_sign          |             196 |                     127 |                  127 |                7 |                    196 |
| L3_state_conditioned_feature   | basis_premium_like\|funding_like       | safe_div_abs        |             196 |                      22 |                   22 |                7 |                    196 |
| L2_typed_two_field_interaction | basis_premium_like\|volatility_like    | spread_rank         |             184 |                     114 |                  114 |                6 |                    184 |
| L4_factor_candidate_probe      | basis_premium_like\|positioning_like   | sub                 |             169 |                       0 |                    0 |                2 |                    169 |
| L4_factor_candidate_probe      | basis_premium_like\|positioning_like   | mul                 |             169 |                       0 |                    0 |                2 |                    169 |
| L2_typed_two_field_interaction | basis_premium_like\|basis_premium_like | smooth_mul          |             165 |                     165 |                  165 |                9 |                    165 |
| L4_factor_candidate_probe      | basis_premium_like\|funding_like       | mul                 |             164 |                       0 |                    0 |                4 |                    164 |
| L4_factor_candidate_probe      | basis_premium_like\|funding_like       | sub                 |             164 |                       0 |                    0 |                4 |                    164 |
| L4_factor_candidate_probe      | basis_premium_like\|positioning_like   | safe_div_abs        |             161 |                       0 |                    0 |                2 |                    161 |
| L4_factor_candidate_probe      | basis_premium_like\|positioning_like   | gated_sign          |             161 |                       0 |                    0 |                2 |                    161 |
| L3_state_conditioned_feature   | basis_premium_like\|funding_like       | sub                 |             151 |                       0 |                    0 |                6 |                    151 |
| L3_state_conditioned_feature   | basis_premium_like\|funding_like       | mul                 |             151 |                      62 |                   62 |                6 |                    151 |
| L4_factor_candidate_probe      | funding_like\|positioning_like         | spread_rank         |             141 |                       0 |                    0 |                5 |                    141 |
| L4_factor_candidate_probe      | basis_premium_like\|funding_like       | gated_sign          |             135 |                       0 |                    0 |                4 |                    135 |
| L4_factor_candidate_probe      | basis_premium_like\|funding_like       | safe_div_abs        |             135 |                       0 |                    0 |                4 |                    135 |
| L2_typed_two_field_interaction | basis_premium_like\|volatility_like    | sub                 |             124 |                      24 |                   24 |                5 |                    124 |
| L2_typed_two_field_interaction | basis_premium_like\|volatility_like    | gated_sign          |             124 |                      64 |                   64 |                5 |                    124 |
| L2_typed_two_field_interaction | basis_premium_like\|volatility_like    | mul                 |             124 |                      64 |                   64 |                5 |                    124 |
| L2_typed_two_field_interaction | basis_premium_like\|volatility_like    | safe_div_abs        |             124 |                      24 |                   24 |                5 |                    124 |
| L2_typed_two_field_interaction | price_like\|volatility_like            | smooth_mul          |             112 |                      42 |                   42 |                6 |                    112 |
| L4_factor_candidate_probe      | basis_premium_like\|volatility_like    | mean_reversion_gate |              98 |                       0 |                    0 |                3 |                     98 |
| L4_factor_candidate_probe      | basis_premium_like\|volatility_like    | signed_spread       |              96 |                       0 |                    0 |                3 |                     96 |
| L2_typed_two_field_interaction | basis_premium_like\|price_like         | spread_rank         |              87 |                      87 |                   87 |                6 |                     87 |
| L1_single_field_transform      | volatility_like                        | single              |              84 |                      48 |                   48 |                6 |                     84 |
| L1_single_field_transform      | basis_premium_like                     | single              |              81 |                      81 |                   81 |                6 |                     81 |
| L4_factor_candidate_probe      | basis_premium_like\|volatility_like    | spread_rank         |              73 |                       0 |                    0 |                1 |                     73 |
| L4_factor_candidate_probe      | basis_premium_like\|volatility_like    | smooth_mul          |              71 |                       0 |                    0 |                1 |                     71 |
| L2_typed_two_field_interaction | basis_premium_like\|basis_premium_like | spread_rank         |              66 |                      66 |                   66 |                7 |                     66 |
| L2_typed_two_field_interaction | price_like\|volatility_like            | spread_rank         |              62 |                      32 |                   32 |                5 |                     62 |
| L2_typed_two_field_interaction | basis_premium_like\|price_like         | sub                 |              62 |                      52 |                   52 |                5 |                     62 |
| L2_typed_two_field_interaction | basis_premium_like\|price_like         | safe_div_abs        |              62 |                      62 |                   62 |                5 |                     62 |
| L2_typed_two_field_interaction | basis_premium_like\|price_like         | mul                 |              62 |                      62 |                   62 |                5 |                     62 |
| L2_typed_two_field_interaction | basis_premium_like\|price_like         | gated_sign          |              62 |                      62 |                   62 |                5 |                     62 |
| L2_typed_two_field_interaction | price_like\|volatility_like            | sub                 |              58 |                       2 |                    2 |                5 |                     58 |
| L2_typed_two_field_interaction | price_like\|volatility_like            | mul                 |              58 |                      12 |                   12 |                5 |                     58 |
| L2_typed_two_field_interaction | volatility_like\|volatility_like       | smooth_mul          |              56 |                      11 |                   11 |                6 |                     56 |
| L2_typed_two_field_interaction | price_like\|volatility_like            | safe_div_abs        |              56 |                       2 |                    2 |                5 |                     56 |
| L2_typed_two_field_interaction | price_like\|volatility_like            | gated_sign          |              56 |                      12 |                   12 |                5 |                     56 |
| L4_factor_candidate_probe      | basis_premium_like\|price_like         | mean_reversion_gate |              49 |                       0 |                    0 |                3 |                     49 |
| L4_factor_candidate_probe      | basis_premium_like\|price_like         | signed_spread       |              48 |                       0 |                    0 |                3 |                     48 |
| L4_factor_candidate_probe      | funding_like\|positioning_like         | gated_sign          |              45 |                       0 |                    0 |                4 |                     45 |
| L4_factor_candidate_probe      | funding_like\|positioning_like         | safe_div_abs        |              45 |                       0 |                    0 |                4 |                     45 |
| L4_factor_candidate_probe      | funding_like\|positioning_like         | sub                 |              44 |                       0 |                    0 |                4 |                     44 |
| L4_factor_candidate_probe      | funding_like\|positioning_like         | mul                 |              44 |                       0 |                    0 |                4 |                     44 |
| L2_typed_two_field_interaction | basis_premium_like\|basis_premium_like | sub                 |              41 |                      41 |                   41 |                6 |                     41 |
| L2_typed_two_field_interaction | basis_premium_like\|basis_premium_like | mul                 |              41 |                      41 |                   41 |                6 |                     41 |
| L4_factor_candidate_probe      | liquidity_like\|volatility_like        | mean_reversion_gate |              36 |                       0 |                    0 |                1 |                     36 |
| L4_factor_candidate_probe      | liquidity_like\|volatility_like        | signed_spread       |              36 |                       0 |                    0 |                1 |                     36 |
| L2_typed_two_field_interaction | basis_premium_like\|basis_premium_like | gated_sign          |              34 |                      34 |                   34 |                6 |                     34 |
| L1_single_field_transform      | price_like                             | single              |              34 |                      34 |                   34 |                5 |                     34 |

## Derived Field Catalog

The full derived field and transform catalog is stored here:

```text
G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ff_version_20260530\a7ff_v20260530_derived_field_catalog.csv
```

Top base fields:

| base_field                           | semantic_type      | seed_route              |   transform_count |   formula_count |   materialization_count |   company_wave_count |
|:-------------------------------------|:-------------------|:------------------------|------------------:|----------------:|------------------------:|---------------------:|
| funding_rate                         | funding_like       | modifier_only_seed      |                20 |           12000 |                    1413 |                  813 |
| global_long_short_account_ratio_last | positioning_like   | modifier_only_seed      |                20 |            4897 |                     246 |                    9 |
| global_long_short_account_ratio_mean | positioning_like   | modifier_only_seed      |                20 |            3301 |                     167 |                    4 |
| index_close                          | basis_premium_like | modifier_only_seed      |                20 |            2601 |                     585 |                  477 |
| mark_index_basis_bps                 | basis_premium_like | primary_signal_seed     |                39 |            2350 |                     928 |                  928 |
| mark_close                           | basis_premium_like | modifier_only_seed      |                20 |            1949 |                     415 |                  323 |
| premium_close_bps                    | basis_premium_like | exploratory_signal_seed |                42 |            1540 |                     829 |                  829 |
| mark_high                            | basis_premium_like | modifier_only_seed      |                20 |            1212 |                       0 |                    0 |
| realized_vol_168h                    | volatility_like    | exploratory_signal_seed |                42 |            1102 |                     322 |                  322 |
| realized_vol_24h                     | volatility_like    | exploratory_signal_seed |                42 |            1057 |                     299 |                  299 |
| trade_return_1h                      | price_like         | exploratory_signal_seed |                34 |            1041 |                     633 |                  633 |
| mark_low                             | basis_premium_like | modifier_only_seed      |                20 |             807 |                       0 |                    0 |
| mark_trade_basis_bps                 | basis_premium_like | modifier_only_seed      |                20 |             737 |                       0 |                    0 |
| premium_close                        | basis_premium_like | modifier_only_seed      |                20 |             475 |                       0 |                    0 |
| index_count                          | basis_premium_like | modifier_only_seed      |                20 |             454 |                       0 |                    0 |
| open_interest_value_last             | positioning_like   | modifier_only_seed      |                20 |             442 |                       0 |                    0 |
| open_interest_last                   | positioning_like   | modifier_only_seed      |                20 |             442 |                       0 |                    0 |
| open_interest_mean                   | positioning_like   | modifier_only_seed      |                20 |             442 |                       0 |                    0 |
| index_high                           | basis_premium_like | modifier_only_seed      |                20 |             395 |                       0 |                    0 |
| open_interest_value_mean             | positioning_like   | modifier_only_seed      |                20 |             338 |                       0 |                    0 |
| index_low                            | basis_premium_like | modifier_only_seed      |                20 |             232 |                       0 |                    0 |
| taker_buy_sell_volume_ratio_last     | positioning_like   | modifier_only_seed      |                20 |             218 |                       0 |                    0 |
| index_open                           | basis_premium_like | modifier_only_seed      |                20 |             210 |                       0 |                    0 |
| mark_count                           | basis_premium_like | modifier_only_seed      |                20 |             210 |                       0 |                    0 |
| mark_open                            | basis_premium_like | modifier_only_seed      |                17 |             190 |                       0 |                    0 |
| premium_abs_168h                     | basis_premium_like | modifier_only_seed      |                 7 |             164 |                       0 |                    0 |
| premium_count                        | basis_premium_like | modifier_only_seed      |                 7 |             144 |                       0 |                    0 |
| premium_open                         | basis_premium_like | modifier_only_seed      |                 7 |             140 |                       0 |                    0 |
| premium_low                          | basis_premium_like | modifier_only_seed      |                 7 |             140 |                       0 |                    0 |
| premium_high                         | basis_premium_like | modifier_only_seed      |                 7 |             140 |                       0 |                    0 |
| age_x_volatility                     | volatility_like    | modifier_only_seed      |                 1 |             124 |                       0 |                    0 |
| trade_high                           | volatility_like    | modifier_only_seed      |                 5 |             124 |                       0 |                    0 |
| trade_low                            | volatility_like    | modifier_only_seed      |                 1 |             114 |                       0 |                    0 |
| taker_buy_sell_volume_ratio_mean     | positioning_like   | modifier_only_seed      |                 7 |             104 |                       0 |                    0 |
| top_long_short_account_ratio_last    | positioning_like   | modifier_only_seed      |                 7 |             104 |                       0 |                    0 |
| top_long_short_account_ratio_mean    | positioning_like   | modifier_only_seed      |                 7 |             104 |                       0 |                    0 |
| trade_close                          | price_like         | modifier_only_seed      |                 7 |             102 |                       0 |                    0 |
| top_long_short_position_ratio_last   | positioning_like   | modifier_only_seed      |                 7 |             102 |                       0 |                    0 |
| top_long_short_position_ratio_mean   | positioning_like   | modifier_only_seed      |                 7 |             102 |                       0 |                    0 |
| basis_abs_168h                       | basis_premium_like | modifier_only_seed      |                 1 |              96 |                       0 |                    0 |
| realized_vol_72h                     | volatility_like    | modifier_only_seed      |                 1 |              74 |                       0 |                    0 |
| trade_return_24h                     | price_like         | modifier_only_seed      |                 1 |              66 |                       0 |                    0 |
| metrics_n_5m                         | positioning_like   | modifier_only_seed      |                 1 |              65 |                       0 |                    0 |
| open_interest_change_24h             | positioning_like   | modifier_only_seed      |                 1 |              60 |                       0 |                    0 |
| oi_x_price_move_24h                  | positioning_like   | modifier_only_seed      |                 1 |              60 |                       0 |                    0 |
| age_x_liquidity                      | liquidity_like     | modifier_only_seed      |                 1 |              24 |                       0 |                    0 |
| volume_volatility_ratio_168h         | liquidity_like     | modifier_only_seed      |                 1 |              20 |                       0 |                    0 |
| taker_buy_quote_volume               | liquidity_like     | modifier_only_seed      |                 1 |              20 |                       0 |                    0 |
| trade_count                          | liquidity_like     | modifier_only_seed      |                 1 |              20 |                       0 |                    0 |
| trade_volume                         | liquidity_like     | modifier_only_seed      |                 1 |              20 |                       0 |                    0 |
| trade_quote_volume                   | liquidity_like     | modifier_only_seed      |                 1 |              20 |                       0 |                    0 |
| liquidity_rank_active_universe       | liquidity_like     | modifier_only_seed      |                 1 |              14 |                       0 |                    0 |
| log_quote_volume_168h                | liquidity_like     | modifier_only_seed      |                 1 |              14 |                       0 |                    0 |
| trade_count_168h                     | liquidity_like     | modifier_only_seed      |                 1 |              12 |                       0 |                    0 |
| taker_buy_volume                     | liquidity_like     | modifier_only_seed      |                 1 |              12 |                       0 |                    0 |
| median_quote_volume_168h             | liquidity_like     | modifier_only_seed      |                 1 |              10 |                       0 |                    0 |
| source_metrics                       | generic_numeric    | modifier_only_seed      |                 1 |               8 |                       0 |                    0 |
| source_trade_klines                  | generic_numeric    | modifier_only_seed      |                 1 |               8 |                       0 |                    0 |
| trade_open                           | generic_numeric    | modifier_only_seed      |                 1 |               8 |                       0 |                    0 |
| sqrt_listing_age_days                | state_or_taxonomy  | modifier_only_seed      |                 1 |               6 |                       0 |                    0 |

## Queue Summary

| queue                      |   rows | file                                                                                                                               |
|:---------------------------|-------:|:-----------------------------------------------------------------------------------------------------------------------------------|
| blueprint_pool             |  20599 | G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ff24r_dry_generation_plan\a7ff24r_blueprint_pool.csv             |
| materialization_queue      |   3000 | G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ff24r_dry_generation_plan\a7ff24r_materialization_queue.csv      |
| company_numeric_wave_queue |   2400 | G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ff24r_dry_generation_plan\a7ff24r_company_numeric_wave_queue.csv |

## Company Shard Plan

| company_shard   |   row_count |   semantic_pairs |   motifs |   skeletons |
|:----------------|------------:|-----------------:|---------:|------------:|
| shard_00        |         200 |                2 |        5 |          20 |
| shard_01        |         200 |                1 |        3 |          17 |
| shard_02        |         200 |                2 |        4 |          10 |
| shard_03        |         200 |                1 |        3 |          12 |
| shard_04        |         200 |                2 |        4 |          12 |
| shard_05        |         200 |                1 |        4 |          12 |
| shard_06        |         200 |                2 |        6 |          14 |
| shard_07        |         200 |                6 |        7 |          17 |
| shard_08        |         200 |                1 |        2 |           6 |
| shard_09        |         200 |                1 |        2 |           8 |
| shard_10        |         200 |                1 |        2 |           6 |
| shard_11        |         200 |                2 |        4 |           7 |

## Version Classification Standard For Future Work

Each future version must include:

```text
1. version_id
2. source commits and upload status
3. included stages and excluded stages
4. decisions and authorization boundaries
5. complete formula index path
6. derived field catalog path
7. queue membership and shard plan
8. selector / label / control policy
9. what is authorized next
10. what remains blocked
```

Required runtime files:

```text
a7ff_vYYYYMMDD_formula_index.csv
a7ff_vYYYYMMDD_derived_field_catalog.csv
a7ff_vYYYYMMDD_formula_family_summary.csv
a7ff_vYYYYMMDD_base_field_usage.csv
a7ff_vYYYYMMDD_queue_summary.csv
a7ff_vYYYYMMDD_output_manifest.csv
a7ff_vYYYYMMDD_manifest.json
```

## Authorization Boundary

```text
authorizes_search = false
authorizes_alpha_proof = false
authorizes_shadow_paper_live = false
next_allowed = company numeric execution adapter / A7FF-25R
```
