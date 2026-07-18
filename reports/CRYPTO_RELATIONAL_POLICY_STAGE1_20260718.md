# Crypto Relational Policy Stage 1 — Layer Attribution

- Decision: `RELATIONAL_REPRESENTATION_INCREMENT_NOT_ESTABLISHED`
- Source SHA: `7421d4c0ef78f9212f692c46fa9e023438257ed2`
- PC2 parity: `PASS`
- Seeds: `[20260718, 20260719]`
- Fixed optimizer steps per arm/seed: `245`
- Parameter count per arm: `12993`
- Actual machine wall: `508.92s`

## What was attributed

A, B, and N used the same 38 asset-local fields, one current market-state field, full-window causal temporal encoder, prediction head, initialization, batches, optimizer, and target. B alone received synchronized peer K/V; N received t-336h peer K/V with the current self query, current market context, and current membership mask.

This is spent development representation attribution. It is not economic alpha, OOS, fresh evidence, deployment, challenge admission, or promotion evidence.

## Primary block deltas

Positive delta means lower MSE for B.

| Block | Seed | Comparison | Control MSE - B MSE | Win |
|---|---:|---|---:|---|
| ATTR_2024_01 | 20260718 | B_MINUS_A | 2.2967446482e-06 | True |
| ATTR_2024_01 | 20260718 | B_MINUS_N | 7.21090691221e-06 | True |
| ATTR_2024_01 | 20260719 | B_MINUS_A | -1.74210295178e-06 | False |
| ATTR_2024_01 | 20260719 | B_MINUS_N | 2.45167017773e-06 | True |
| ATTR_2024_02 | 20260718 | B_MINUS_A | -1.76053568605e-06 | False |
| ATTR_2024_02 | 20260718 | B_MINUS_N | -2.78560291413e-06 | False |
| ATTR_2024_02 | 20260719 | B_MINUS_A | -4.61059784471e-07 | False |
| ATTR_2024_02 | 20260719 | B_MINUS_N | 5.95360692541e-07 | True |
| ATTR_2024_03 | 20260718 | B_MINUS_A | -2.0303063868e-06 | False |
| ATTR_2024_03 | 20260718 | B_MINUS_N | -3.39698614336e-06 | False |
| ATTR_2024_03 | 20260719 | B_MINUS_A | -1.50669414812e-06 | False |
| ATTR_2024_03 | 20260719 | B_MINUS_N | 1.87376983367e-07 | True |
| ATTR_2024_04 | 20260718 | B_MINUS_A | 4.06542644102e-06 | True |
| ATTR_2024_04 | 20260718 | B_MINUS_N | 1.61833564348e-05 | True |
| ATTR_2024_04 | 20260719 | B_MINUS_A | -1.01770308926e-05 | False |
| ATTR_2024_04 | 20260719 | B_MINUS_N | 4.61011551811e-06 | True |
| ATTR_2024_05 | 20260718 | B_MINUS_A | 1.06869075427e-06 | True |
| ATTR_2024_05 | 20260718 | B_MINUS_N | 1.53480602332e-06 | True |
| ATTR_2024_05 | 20260719 | B_MINUS_A | -2.59794496173e-06 | False |
| ATTR_2024_05 | 20260719 | B_MINUS_N | 7.57168672836e-07 | True |
| ATTR_2024_06 | 20260718 | B_MINUS_A | 2.59170250373e-06 | True |
| ATTR_2024_06 | 20260718 | B_MINUS_N | 1.20237646324e-05 | True |
| ATTR_2024_06 | 20260719 | B_MINUS_A | -7.22545434194e-06 | False |
| ATTR_2024_06 | 20260719 | B_MINUS_N | 4.15722414237e-06 | True |

## Data and non-degeneracy

- Broad fields: 39 loadable; block-variable counts are persisted per block in `decision.json`.
- All three arms non-degenerate: `True`
- B/A outputs materially differ: `True`
- Shifted donor/current membership mismatch is reported, not hidden or forced to equality.

## Boundaries and expiry

No recent, May-stress, forward, challenge, validation/test, candidate promotion, hyperparameter search, extra seed, or Stage 2 execution occurred. Calibration/selection/stability provenance labels did not feed training or model selection.

Temporary lifecycle action: `DELETE_STAGE1_RUNNER_CONFIG_AND_A_B_N_CONTROL_CODE_AFTER_EVIDENCE_COMMIT`
