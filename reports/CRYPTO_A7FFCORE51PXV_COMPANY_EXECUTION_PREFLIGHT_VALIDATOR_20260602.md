# CRYPTO A7FF-CORE51PXV COMPANY EXECUTION PREFLIGHT VALIDATOR

Generated: 2026-06-02T02:53:57Z

## Decision

`PASS_A7FFCORE51PXV_COMPANY_EXECUTION_PREFLIGHT_READY`

CORE51PXV validates the company-machine replay execution package. It does not execute replay/search/proof.

## Checks

| check                                                               | status   | detail                                                                                                                                                          |
|:--------------------------------------------------------------------|:---------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| base_panel_exists                                                   | PASS     | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527                                                                              |
| latent_panel_exists                                                 | PASS     | G:\AlphaFactory_CryptoData\gold\features\binance_universe498_latent_state_features_v1_20260527.parquet                                                          |
| selected_candidate_count                                            | PASS     | 384                                                                                                                                                             |
| shard_file_count                                                    | PASS     | 16                                                                                                                                                              |
| shard_plan_count                                                    | PASS     | 16                                                                                                                                                              |
| missing_field_count                                                 | PASS     | 0                                                                                                                                                               |
| command_template_exists                                             | PASS     | G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ffcore51px_company_sharded_replay_runner_contract\a7ffcore51px_company_execution_commands.ps1 |
| external_output_dir_writable                                        | PASS     | G:\AlphaFactory_CryptoData\research_runtime\a7ffcore51px_company_sharded_replay_20260602                                                                        |
| compile_crypto_a7ffcore51px_company_compact_frame_builder.py        | PASS     |                                                                                                                                                                 |
| compile_crypto_a7ffcore51px_company_shard_worker.py                 | PASS     |                                                                                                                                                                 |
| compile_crypto_a7ffcore51pxe_company_sharded_replay_orchestrator.py | PASS     |                                                                                                                                                                 |
| compile_crypto_a7ffcore51pxe_company_result_aggregator.py           | PASS     |                                                                                                                                                                 |
| compile_crypto_a7ffcore51pxe_company_status.py                      | PASS     |                                                                                                                                                                 |
| compile_crypto_a7ffcore51pxe_import_company_results.py              | PASS     |                                                                                                                                                                 |

## Script Compile Audit

| script                                                              | exists   | compile_status   | error   |
|:--------------------------------------------------------------------|:---------|:-----------------|:--------|
| scripts/crypto_a7ffcore51px_company_compact_frame_builder.py        | True     | PASS             |         |
| scripts/crypto_a7ffcore51px_company_shard_worker.py                 | True     | PASS             |         |
| scripts/crypto_a7ffcore51pxe_company_sharded_replay_orchestrator.py | True     | PASS             |         |
| scripts/crypto_a7ffcore51pxe_company_result_aggregator.py           | True     | PASS             |         |
| scripts/crypto_a7ffcore51pxe_company_status.py                      | True     | PASS             |         |
| scripts/crypto_a7ffcore51pxe_import_company_results.py              | True     | PASS             |         |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE51PXE company-machine sharded replay execution": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```
