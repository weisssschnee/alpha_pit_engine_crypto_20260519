# CRYPTO A7FF-CORE51PXE COMPANY SHARDED REPLAY IMPORT

Generated: 2026-06-02T09:38:22Z

## Decision

`PASS_A7FFCORE51PXE_COMPANY_RESULTS_IMPORTED_READY_FOR_CORE52_ARBITRATION`

This imports external company-machine shard results into repo runtime. It does not execute replay/search/proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core52_arbitration": true,
  "authorizes_shadow_paper_live": false,
  "completed_shards": 16,
  "control_clean_positive_seed_count": 35,
  "decision": "PASS_A7FFCORE51PXE_COMPANY_RESULTS_IMPORTED_READY_FOR_CORE52_ARBITRATION",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-02T09:38:22Z",
  "metric_rows": 3072,
  "source_decision": "PASS_A7FFCORE51PXE_COMPANY_SHARDED_REPLAY_AGGREGATED",
  "source_output_dir": "G:/AlphaFactory_CryptoData/research_runtime/a7ffcore51px_company_sharded_replay_20260602",
  "stage": "A7FF-CORE51PXE-IMPORT"
}
```

## Label Summary

| label_key   |   row_count |   seed_count |   control_clean_positive_count |   median_control_ratio |   median_original_spread |
|:------------|------------:|-------------:|-------------------------------:|-----------------------:|-------------------------:|
| L0_raw_1h   |         384 |          384 |                             17 |                1.07807 |             -1.83747e-05 |
| L0_raw_24h  |         384 |          384 |                             14 |                1.11992 |             -6.07262e-05 |
| L0_raw_4h   |         384 |          384 |                             11 |                1.13561 |             -4.16569e-05 |
| L0_raw_8h   |         384 |          384 |                             12 |                1.07944 |             -4.42174e-05 |
| L1_xs_1h    |         384 |          384 |                             17 |                1.07807 |             -1.83747e-05 |
| L1_xs_24h   |         384 |          384 |                             14 |                1.11992 |             -6.07262e-05 |
| L1_xs_4h    |         384 |          384 |                             11 |                1.13561 |             -4.16569e-05 |
| L1_xs_8h    |         384 |          384 |                             12 |                1.07944 |             -4.42174e-05 |

## Family Summary

| semantic_pair                         | operator        |   row_count |   seed_count |   control_clean_positive_count |   median_control_ratio |
|:--------------------------------------|:----------------|------------:|-------------:|-------------------------------:|-----------------------:|
| basis_premium_like                    | Delta           |          32 |            4 |                             12 |               1        |
| price_like|price_like                 | Identity        |          16 |            2 |                             10 |               0.997812 |
| basis_premium_like|basis_premium_like | Identity        |          16 |            2 |                              8 |               0.999397 |
| basis_premium_like|price_like         | Identity        |           8 |            1 |                              8 |               0.99657  |
| positioning_like|state_or_taxonomy    | Identity        |          16 |            2 |                              6 |               1.05459  |
| state_or_taxonomy|state_or_taxonomy   | SignedRankDelta |          16 |            2 |                              6 |               1.06775  |
| funding_like|funding_like             | WinsorZ         |           8 |            1 |                              6 |               0.968402 |
| funding_like|positioning_like         | Identity        |           8 |            1 |                              4 |               0.964986 |
| funding_like|price_like               | WinsorZ         |           8 |            1 |                              4 |               2.94719  |
| basis_premium_like                    | CSRank          |          24 |            3 |                              2 |               1.18436  |
| basis_premium_like                    | Identity        |          16 |            2 |                              2 |               1.11567  |
| basis_premium_like|basis_premium_like | WinsorZ         |          16 |            2 |                              2 |               1.30054  |
| basis_premium_like|liquidity_like     | CSRank          |          16 |            2 |                              2 |               1.37226  |
| basis_premium_like|positioning_like   | WinsorZ         |          16 |            2 |                              2 |               2.48795  |
| funding_like|liquidity_like           | WinsorZ         |          16 |            2 |                              2 |               1.02024  |
| funding_like|state_or_taxonomy        | AbsDelta        |          16 |            2 |                              2 |               1.02729  |
| funding_like|state_or_taxonomy        | SignedRankDelta |          16 |            2 |                              2 |               1.12509  |
| funding_like|volatility_like          | AbsDelta        |          16 |            2 |                              2 |               0.954081 |
| funding_like|volatility_like          | Delta           |          16 |            2 |                              2 |               1.16032  |
| generic_numeric|price_like            | Identity        |          16 |            2 |                              2 |               1.55151  |
| generic_numeric|volatility_like       | AbsDelta        |          16 |            2 |                              2 |               1.25482  |
| positioning_like|positioning_like     | CSRank          |          16 |            2 |                              2 |              23.4702   |
| price_like|volatility_like            | Identity        |          16 |            2 |                              2 |               1.58064  |
| state_or_taxonomy                     | WinsorZ         |          16 |            2 |                              2 |               1        |
| funding_like|positioning_like         | WinsorZ         |           8 |            1 |                              2 |               1.18111  |
| generic_numeric|state_or_taxonomy     | WinsorZ         |           8 |            1 |                              2 |               4.07641  |
| liquidity_like|positioning_like       | CSRank          |           8 |            1 |                              2 |               1.05273  |
| liquidity_like|state_or_taxonomy      | SpreadShortLong |           8 |            1 |                              2 |               1.01228  |
| liquidity_like|state_or_taxonomy      | WinsorZ         |           8 |            1 |                              2 |               1.88148  |
| positioning_like                      | Delta           |           8 |            1 |                              2 |               2.19935  |
| price_like|state_or_taxonomy          | SpreadShortLong |           8 |            1 |                              2 |               1        |
| basis_premium_like                    | SignedRankDelta |          32 |            4 |                              0 |               1.05233  |
| basis_premium_like|liquidity_like     | Delta           |          24 |            3 |                              0 |               1.73242  |
| price_like                            | SignedRankDelta |          24 |            3 |                              0 |               1.00557  |
| price_like                            | WinsorZ         |          24 |            3 |                              0 |               1.01728  |
| price_like|volatility_like            | Delta           |          24 |            3 |                              0 |               1.16082  |
| basis_premium_like                    | AbsDelta        |          16 |            2 |                              0 |               1.00294  |
| basis_premium_like                    | WinsorZ         |          16 |            2 |                              0 |               1.28187  |
| basis_premium_like|basis_premium_like | AbsDelta        |          16 |            2 |                              0 |               1        |
| basis_premium_like|basis_premium_like | Delta           |          16 |            2 |                              0 |               1        |
| basis_premium_like|basis_premium_like | SignedRankDelta |          16 |            2 |                              0 |               1.5209   |
| basis_premium_like|funding_like       | Delta           |          16 |            2 |                              0 |               2.37995  |
| basis_premium_like|liquidity_like     | WinsorZ         |          16 |            2 |                              0 |               0.999457 |
| basis_premium_like|positioning_like   | AbsDelta        |          16 |            2 |                              0 |               1.8693   |
| basis_premium_like|positioning_like   | Identity        |          16 |            2 |                              0 |               2.06841  |
| basis_premium_like|positioning_like   | SignedRankDelta |          16 |            2 |                              0 |               1.28749  |
| basis_premium_like|price_like         | CSRank          |          16 |            2 |                              0 |               1.05811  |
| basis_premium_like|price_like         | Delta           |          16 |            2 |                              0 |               2.13831  |
| basis_premium_like|state_or_taxonomy  | AbsDelta        |          16 |            2 |                              0 |               1.29288  |
| basis_premium_like|state_or_taxonomy  | SignedRankDelta |          16 |            2 |                              0 |               1.99533  |
| basis_premium_like|state_or_taxonomy  | WinsorZ         |          16 |            2 |                              0 |               1.22488  |
| basis_premium_like|volatility_like    | AbsDelta        |          16 |            2 |                              0 |               1.37076  |
| basis_premium_like|volatility_like    | CSRank          |          16 |            2 |                              0 |               1.33128  |
| basis_premium_like|volatility_like    | Delta           |          16 |            2 |                              0 |               1.98062  |
| basis_premium_like|volatility_like    | Identity        |          16 |            2 |                              0 |               2.37184  |
| basis_premium_like|volatility_like    | SignedRankDelta |          16 |            2 |                              0 |               1.00023  |
| basis_premium_like|volatility_like    | WinsorZ         |          16 |            2 |                              0 |               1.00213  |
| funding_like                          | AbsDelta        |          16 |            2 |                              0 |               1.01332  |
| funding_like                          | CSRank          |          16 |            2 |                              0 |               1.01435  |
| funding_like                          | SignedRankDelta |          16 |            2 |                              0 |               1.02905  |
| funding_like                          | WinsorZ         |          16 |            2 |                              0 |               1.02916  |
| funding_like|funding_like             | AbsDelta        |          16 |            2 |                              0 |               1.25768  |
| funding_like|funding_like             | CSRank          |          16 |            2 |                              0 |               1.45371  |
| funding_like|funding_like             | SignedRankDelta |          16 |            2 |                              0 |               1.26096  |
| funding_like|liquidity_like           | AbsDelta        |          16 |            2 |                              0 |               1.19495  |
| funding_like|liquidity_like           | Identity        |          16 |            2 |                              0 |               2.05105  |
| funding_like|positioning_like         | AbsDelta        |          16 |            2 |                              0 |               1.00585  |
| funding_like|positioning_like         | CSRank          |          16 |            2 |                              0 |               0.947145 |
| funding_like|positioning_like         | Delta           |          16 |            2 |                              0 |               1.04193  |
| funding_like|positioning_like         | SignedRankDelta |          16 |            2 |                              0 |               1.12389  |
| funding_like|price_like               | Delta           |          16 |            2 |                              0 |               1.39309  |
| funding_like|state_or_taxonomy        | CSRank          |          16 |            2 |                              0 |               1.04229  |
| funding_like|state_or_taxonomy        | Delta           |          16 |            2 |                              0 |               4.1477   |
| funding_like|state_or_taxonomy        | Identity        |          16 |            2 |                              0 |               1.06822  |
| funding_like|state_or_taxonomy        | WinsorZ         |          16 |            2 |                              0 |               1.12345  |
| funding_like|volatility_like          | CSRank          |          16 |            2 |                              0 |               1.27511  |
| funding_like|volatility_like          | SignedRankDelta |          16 |            2 |                              0 |               2.13345  |
| generic_numeric|positioning_like      | AbsDelta        |          16 |            2 |                              0 |               1        |
| generic_numeric|positioning_like      | SignedRankDelta |          16 |            2 |                              0 |               1        |
| generic_numeric|positioning_like      | WinsorZ         |          16 |            2 |                              0 |               1        |
