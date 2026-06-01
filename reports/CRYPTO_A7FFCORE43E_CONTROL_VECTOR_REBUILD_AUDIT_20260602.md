# CRYPTO A7FF-CORE43E CONTROL VECTOR REBUILD AUDIT

Generated: 2026-06-01T20:42:57Z

## Decision

`PASS_A7FFCORE43E_CONTROL_VECTOR_REBUILD_READY_FOR_CORE44`

CORE43E rebuilds bounded full-universe candidate/control score vectors from existing CORE33 candidates and panels. It is audit-only: no new formula generation, search, alpha proof, shadow, paper, or live authorization.

## Dataset Summary

| dataset                       |   source_rows |   source_symbols |   source_timestamps |   sample_timestamps |   candidate_count | quote_col          |
|:------------------------------|--------------:|-----------------:|--------------------:|--------------------:|------------------:|:-------------------|
| core12_aggtrades_all_features |        815818 |               39 |               20919 |                  48 |                 7 | agg_notional       |
| top498_replay_v2              |       6949596 |              498 |               21025 |                  48 |                14 | trade_quote_volume |

## Sample Quality Gate

| metric                          |            value | pass   |
|:--------------------------------|-----------------:|:-------|
| vector_sample_rows              | 255236           | True   |
| candidate_count                 |     21           | True   |
| required_vector_columns_present |      7           | True   |
| min_original_non_null_ratio     |      0.2558      | True   |
| min_residual_null_std           |      0.000162635 | True   |
| min_null_fit_rows               |     37           | True   |

## Candidate Vector Quality

| candidate_id   | family_id                         | dataset                       |   sample_rows |   sample_symbols |   sample_timestamps | candidate_timestamp_selection   |   original_non_null_ratio |   stale_non_null_ratio |   shuffle_time_non_null_ratio |   shuffle_symbol_non_null_ratio |   original_std |   residual_stale_std |   residual_null_std |
|:---------------|:----------------------------------|:------------------------------|--------------:|-----------------:|--------------------:|:--------------------------------|--------------------------:|-----------------------:|------------------------------:|--------------------------------:|---------------:|---------------------:|--------------------:|
| a7ffcore33_007 | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |          1872 |               39 |                  48 | signal_valid_control_ready      |                  0.30235  |               0.302885 |                      0.30235  |                        0.30235  |    0.197844    |          0.195238    |         0.227017    |
| a7ffcore33_008 | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |          1872 |               39 |                  48 | signal_valid_control_ready      |                  0.30235  |               0.302885 |                      0.30235  |                        0.30235  |    0.0306946   |          0.0306722   |         0.0308685   |
| a7ffcore33_015 | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |          1872 |               39 |                  48 | signal_valid_control_ready      |                  0.307692 |               0.307692 |                      0.307692 |                        0.307692 |    0.18908     |          0.18906     |         0.192397    |
| a7ffcore33_016 | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |          1872 |               39 |                  48 | signal_valid_control_ready      |                  0.307692 |               0.307692 |                      0.307692 |                        0.307692 |    0.253941    |          0.253543    |         0.277295    |
| a7ffcore33_017 | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |          1872 |               39 |                  48 | signal_valid_control_ready      |                  0.30235  |               0.302885 |                      0.30235  |                        0.30235  |    0.206486    |          0.206191    |         0.215694    |
| a7ffcore33_018 | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |          1872 |               39 |                  48 | signal_valid_control_ready      |                  0.307692 |               0.307692 |                      0.307692 |                        0.307692 |    0.949384    |          0.932792    |         1.15859     |
| a7ffcore33_020 | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |          1872 |               39 |                  48 | signal_valid_control_ready      |                  0.307692 |               0.307692 |                      0.307692 |                        0.307692 |    0.182319    |          0.182257    |         0.198008    |
| a7ffcore33_000 | F1b_taker_flow_market_panel       | top498_replay_v2              |         15883 |              498 |                  48 | signal_valid_control_ready      |                  0.998993 |               0.997796 |                      0.998678 |                        0.998993 |    0.322061    |          0.23224     |         0.214343    |
| a7ffcore33_001 | F1b_taker_flow_market_panel       | top498_replay_v2              |         18697 |              498 |                  48 | signal_valid_control_ready      |                  0.26999  |               0.259774 |                      0.161363 |                        0.26999  |    0.286348    |          0.276631    |         0.678201    |
| a7ffcore33_002 | F2a_basis_funding_independent     | top498_replay_v2              |         18697 |              498 |                  48 | signal_valid_control_ready      |                  0.26999  |               0.259774 |                      0.161363 |                        0.26999  |    0.00400631  |          0.00268322  |         0.00442497  |
| a7ffcore33_003 | F2a_basis_funding_independent     | top498_replay_v2              |         15880 |              498 |                  48 | signal_valid_control_ready      |                  0.997544 |               0.996222 |                      0.997166 |                        0.997544 |    1.39884     |          1.39568     |         1.39553     |
| a7ffcore33_004 | F2a_basis_funding_independent     | top498_replay_v2              |         18697 |              498 |                  48 | signal_valid_control_ready      |                  0.26999  |               0.259774 |                      0.161363 |                        0.26999  |    0.000277213 |          0.000238864 |         0.000162635 |
| a7ffcore33_005 | F2a_basis_funding_independent     | top498_replay_v2              |         15903 |              498 |                  48 | signal_valid_control_ready      |                  0.995787 |               0.994844 |                      0.995598 |                        0.995787 |    0.747199    |          0.745077    |         0.741162    |
| a7ffcore33_006 | F1b_taker_flow_market_panel       | top498_replay_v2              |         15903 |              498 |                  48 | signal_valid_control_ready      |                  0.995787 |               0.994844 |                      0.995598 |                        0.995787 |    4.57574e+09 |          4.57638e+09 |         4.5859e+09  |
| a7ffcore33_009 | F2a_basis_funding_independent     | top498_replay_v2              |         18710 |              498 |                  48 | signal_valid_control_ready      |                  0.421807 |               0.411491 |                      0.116195 |                        0.421807 |    0.604252    |          0.602801    |         0.898184    |
| a7ffcore33_010 | F2a_basis_funding_independent     | top498_replay_v2              |         18706 |              498 |                  48 | signal_valid_control_ready      |                  0.2558   |               0.246178 |                      0.265316 |                        0.2558   |    0.00293861  |          0.00164448  |         0.0152639   |
| a7ffcore33_011 | F2a_basis_funding_independent     | top498_replay_v2              |         15880 |              498 |                  48 | signal_valid_control_ready      |                  0.998678 |               0.997607 |                      0.998489 |                        0.998678 |    0.00519141  |          0.00519026  |         0.00479264  |
| a7ffcore33_012 | F1b_taker_flow_market_panel       | top498_replay_v2              |         15880 |              498 |                  48 | signal_valid_control_ready      |                  0.998678 |               0.997607 |                      0.998489 |                        0.998678 |    0.284958    |          0.284719    |         0.284858    |
| a7ffcore33_013 | F2a_basis_funding_independent     | top498_replay_v2              |         15880 |              498 |                  48 | signal_valid_control_ready      |                  0.997607 |               0.996222 |                      0.997229 |                        0.997607 |   32.4685      |         32.485       |        32.4099      |
| a7ffcore33_014 | F1b_taker_flow_market_panel       | top498_replay_v2              |         18706 |              498 |                  48 | signal_valid_control_ready      |                  0.2558   |               0.246178 |                      0.265316 |                        0.2558   |    0.374622    |          0.358617    |         0.804701    |
| a7ffcore33_019 | F1b_taker_flow_market_panel       | top498_replay_v2              |         18710 |              498 |                  48 | signal_valid_control_ready      |                  0.369802 |               0.359594 |                      0.088295 |                        0.369802 |    1.6086      |          0.821251    |         2.61892     |

## Residualization Quality

| candidate_id   | family_id                         | dataset                       |   stale_fit_rows |    stale_r2 |   stale_original_std |   stale_residual_std |   null_fit_rows |     null_r2 |   null_original_std |   null_residual_std | residual_nonzero   |
|:---------------|:----------------------------------|:------------------------------|-----------------:|------------:|---------------------:|---------------------:|----------------:|------------:|--------------------:|--------------------:|:-------------------|
| a7ffcore33_007 | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |              566 | 0.0261612   |          0.197844    |          0.195238    |             230 | 0.0487221   |         0.197844    |         0.227017    | True               |
| a7ffcore33_008 | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |              566 | 0.00145581  |          0.0306946   |          0.0306722   |             230 | 0.00961578  |         0.0306946   |         0.0308685   | True               |
| a7ffcore33_015 | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |              576 | 0.000211283 |          0.18908     |          0.18906     |             240 | 0.0197699   |         0.18908     |         0.192397    | True               |
| a7ffcore33_016 | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |              576 | 0.00313096  |          0.253941    |          0.253543    |             240 | 0.0306359   |         0.253941    |         0.277295    | True               |
| a7ffcore33_017 | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |              566 | 0.00284842  |          0.206486    |          0.206191    |             230 | 0.00608949  |         0.206486    |         0.215694    | True               |
| a7ffcore33_018 | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |              576 | 0.0346478   |          0.949384    |          0.932792    |             240 | 0.0385455   |         0.949384    |         1.15859     | True               |
| a7ffcore33_020 | F1a_aggtrades_flow_microstructure | core12_aggtrades_all_features |              576 | 0.000679213 |          0.182319    |          0.182257    |             240 | 0.0115963   |         0.182319    |         0.198008    | True               |
| a7ffcore33_000 | F1b_taker_flow_market_panel       | top498_replay_v2              |            15848 | 0.480402    |          0.322061    |          0.23224     |           15832 | 0.557805    |         0.322061    |         0.214343    | True               |
| a7ffcore33_001 | F1b_taker_flow_market_panel       | top498_replay_v2              |             4852 | 0.00257997  |          0.286348    |          0.276631    |              58 | 0.0470409   |         0.286348    |         0.678201    | True               |
| a7ffcore33_002 | F2a_basis_funding_independent     | top498_replay_v2              |             4852 | 0.00768459  |          0.00400631  |          0.00268322  |              58 | 0.305733    |         0.00400631  |         0.00442497  | True               |
| a7ffcore33_003 | F2a_basis_funding_independent     | top498_replay_v2              |            15820 | 0.000810348 |          1.39884     |          1.39568     |           15781 | 0.00232222  |         1.39884     |         1.39553     | True               |
| a7ffcore33_004 | F2a_basis_funding_independent     | top498_replay_v2              |             4852 | 0.00254244  |          0.000277213 |          0.000238864 |              58 | 0.318873    |         0.000277213 |         0.000162635 | True               |
| a7ffcore33_005 | F2a_basis_funding_independent     | top498_replay_v2              |            15818 | 0.00401868  |          0.747199    |          0.745077    |           15751 | 0.0122894   |         0.747199    |         0.741162    | True               |
| a7ffcore33_006 | F1b_taker_flow_market_panel       | top498_replay_v2              |            15818 | 0.000853375 |          4.57574e+09 |          4.57638e+09 |           15751 | 0.000940554 |         4.57574e+09 |         4.5859e+09  | True               |
| a7ffcore33_009 | F2a_basis_funding_independent     | top498_replay_v2              |             7696 | 0.00751296  |          0.604252    |          0.602801    |              72 | 0.0152745   |         0.604252    |         0.898184    | True               |
| a7ffcore33_010 | F2a_basis_funding_independent     | top498_replay_v2              |             4596 | 0.142149    |          0.00293861  |          0.00164448  |              37 | 0.0334102   |         0.00293861  |         0.0152639   | True               |
| a7ffcore33_011 | F2a_basis_funding_independent     | top498_replay_v2              |            15841 | 0.000732281 |          0.00519141  |          0.00519026  |           15820 | 0.149102    |         0.00519141  |         0.00479264  | True               |
| a7ffcore33_012 | F1b_taker_flow_market_panel       | top498_replay_v2              |            15841 | 0.00264941  |          0.284958    |          0.284719    |           15820 | 0.00285892  |         0.284958    |         0.284858    | True               |
| a7ffcore33_013 | F2a_basis_funding_independent     | top498_replay_v2              |            15820 | 0.000196081 |         32.4685      |         32.485       |           15782 | 0.00720095  |        32.4685      |        32.4099      | True               |
| a7ffcore33_014 | F1b_taker_flow_market_panel       | top498_replay_v2              |             4596 | 0.035171    |          0.374622    |          0.358617    |              37 | 0.145829    |         0.374622    |         0.804701    | True               |
| a7ffcore33_019 | F1b_taker_flow_market_panel       | top498_replay_v2              |             6725 | 0.595117    |          1.6086      |          0.821251    |              51 | 0.512643    |         1.6086      |         2.61892     | True               |

## External Artifact

| artifact                            | path                                                                                                                                     | committed_to_git   |   rows |   columns |   bytes |
|:------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------|:-------------------|-------:|----------:|--------:|
| full_universe_control_vector_sample | G:/AlphaFactory_CryptoData/research_runtime/a7ffcore43e_control_vectors_20260602/a7ffcore43e_full_universe_control_vector_sample.parquet | False              | 255236 |        18 | 7840897 |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE44 full-universe orthogonal score packet construction contract": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "book_replay_execution_from_selected_packet": true,
    "formula_search": true,
    "large_search": true,
    "new_generation": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core44_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 21,
  "dataset_count": 2,
  "decision": "PASS_A7FFCORE43E_CONTROL_VECTOR_REBUILD_READY_FOR_CORE44",
  "executes_new_generation": false,
  "executes_search": false,
  "external_sample_path": "G:/AlphaFactory_CryptoData/research_runtime/a7ffcore43e_control_vectors_20260602/a7ffcore43e_full_universe_control_vector_sample.parquet",
  "generated_at": "2026-06-01T20:42:57Z",
  "min_residual_fit_rows_required": 30,
  "next_allowed": "A7FF-CORE44 full-universe orthogonal score packet construction contract",
  "source_decision": "PASS_A7FFCORE43_CONTROL_ORTHOGONALIZATION_CONTRACT_READY_FOR_CORE43E",
  "source_stage": "A7FF-CORE43",
  "stage": "A7FF-CORE43E",
  "vector_sample_columns": 18,
  "vector_sample_rows": 255236
}
```
