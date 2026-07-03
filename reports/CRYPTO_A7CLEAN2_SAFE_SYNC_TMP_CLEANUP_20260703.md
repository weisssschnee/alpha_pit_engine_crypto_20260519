# CRYPTO A7CLEAN2 Safe Sync/Tmp Cleanup

Generated: 2026-07-03T14:19:16.831784+00:00

## Decision

`PASS_A7CLEAN2_SAFE_SYNC_TMP_CLEANED`

A7CLEAN-2 deletes only codex_sync/tmp artifacts identified by A7CLEAN-1. It does not delete raw, gold, silver, transfer, or incoming alpha data packages.

## Counts

- deleted_scope: `codex_sync/tmp artifacts only`
- raw_gold_silver_transfer_incoming_deleted: `False`
- deleted_rows: `4`
- failed_rows: `0`
- total_freed_gb_by_path_scan: `0.596`
- disk_free_gb_before: `9.847`
- disk_free_gb_after: `10.453`
- disk_free_delta_gb: `0.606`

## Delete Log

| relative_path | size_gb_before | freed_gb | status | error |
|---|---:|---:|---|---|
| `codex_sync/sessions_2026_05` | 0.0 | 0.0 | `MISSING` | path not present |
| `codex_sync/tmp` | 0.451 | 0.451 | `DELETED` |  |
| `codex_sync/.tmp` | 0.071 | 0.071 | `DELETED` |  |
| `tmp/inspect_THETAUSDT_bookTicker_2024-03-19.zip` | 0.052 | 0.052 | `DELETED` |  |
| `tmp/binance_vision` | 0.022 | 0.022 | `DELETED` |  |

## Outputs

- delete_log: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7clean2_safe_sync_tmp_cleanup_20260703\a7clean2_safe_delete_log.csv`
- manifest: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7clean2_safe_sync_tmp_cleanup_20260703\a7clean2_manifest.json`
