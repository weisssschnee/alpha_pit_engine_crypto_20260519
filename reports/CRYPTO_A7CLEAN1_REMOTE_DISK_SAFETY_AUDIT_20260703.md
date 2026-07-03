# CRYPTO A7CLEAN1 Remote Disk Safety Audit

Generated: 2026-07-03T14:10:19.109155+00:00

## Decision

`PASS_A7CLEAN1_CLEANUP_CANDIDATES_AUDITED`

This audit identifies remote disk cleanup candidates without deleting data. It does not authorize deletion of raw/gold/silver datasets.

## Counts

- candidate_rows: `10`
- total_candidate_gb: `13.684`
- delete_candidate_after_manifest_check_gb: `9.937`
- likely_safe_delete_or_archive_gb: `3.747`
- authorizes_delete: `False`

## Largest Candidates

| name | size_gb | coverage_roots | cleanup_decision | reason |
|---|---:|---|---|---|
| `a7al1_basepanel_chunks` | 4.39 | `gold|reports` | `DELETE_CANDIDATE_AFTER_MANIFEST_CHECK` | incoming package appears downstreamed |
| `crypto_universe500_20260525` | 3.66 | `gold|raw|silver` | `DELETE_CANDIDATE_AFTER_MANIFEST_CHECK` | transfer package has downstream coverage hits |
| `sessions_2026_05` | 1.58 | `` | `LIKELY_SAFE_TO_ARCHIVE_OR_DELETE` | codex_sync mirror/session artifact; not alpha data source |
| `.codex` | 1.571 | `` | `LIKELY_SAFE_TO_ARCHIVE_OR_DELETE` | codex_sync mirror/session artifact; not alpha data source |
| `crypto_universe500_complete_silver_20260525` | 1.031 | `gold|raw|silver` | `DELETE_CANDIDATE_AFTER_MANIFEST_CHECK` | transfer package has downstream coverage hits |
| `crypto_universe500_silver_20260525` | 0.856 | `gold|raw|silver` | `DELETE_CANDIDATE_AFTER_MANIFEST_CHECK` | transfer package has downstream coverage hits |
| `tmp` | 0.451 | `` | `LIKELY_SAFE_TO_ARCHIVE_OR_DELETE` | codex_sync mirror/session artifact; not alpha data source |
| `.tmp` | 0.071 | `` | `LIKELY_SAFE_TO_ARCHIVE_OR_DELETE` | codex_sync mirror/session artifact; not alpha data source |
| `inspect_THETAUSDT_bookTicker_2024-03-19.zip` | 0.052 | `` | `LIKELY_SAFE_TO_DELETE` | tmp directory/file |
| `binance_vision` | 0.022 | `` | `LIKELY_SAFE_TO_DELETE` | tmp directory/file |

## Outputs

- audit: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7clean1_remote_disk_safety_audit_20260703\a7clean1_cleanup_candidate_audit.csv`
- summary: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7clean1_remote_disk_safety_audit_20260703\a7clean1_cleanup_decision_summary.csv`
- manifest: `D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7clean1_remote_disk_safety_audit_20260703\a7clean1_manifest.json`
