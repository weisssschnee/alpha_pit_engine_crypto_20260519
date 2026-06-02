# CRYPTO A7FF-CORE49E FULL-UNIVERSE NULL-VECTOR PREFLIGHT EXECUTION

Generated: 2026-06-02T01:16:18Z

## Decision

`PASS_A7FFCORE49E_NULL_VECTOR_PREFLIGHT_READY_FOR_CORE50_CONTRACT`

CORE49E materializes original/null vector diagnostics over the full available universe frame. It does not execute replay, search, proof, promotion, shadow, paper, or live.

## Summary

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core49e_full_run": false,
  "authorizes_core50_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_numeric_replay": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE49E_NULL_VECTOR_PREFLIGHT_READY_FOR_CORE50_CONTRACT",
  "eval_failure_count": 0,
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "external_vector_sample": "G:/AlphaFactory_CryptoData/research_runtime/a7ffcore49e_full_universe_null_vector_preflight_20260602/a7ffcore49e_vector_sample.parquet",
  "frame_rows": 6949596,
  "frame_symbols": 498,
  "generated_at": "2026-06-02T01:16:18Z",
  "is_partial_smoke": false,
  "materialization_pass_count": 1728,
  "missing_field_count": 0,
  "next_allowed": "A7FF-CORE50 null-vector preflight forensic or replay contract arbitration",
  "required_field_count": 54,
  "seed_count": 1800,
  "source_decision": "PASS_A7FFCORE49_FULL_UNIVERSE_NULL_VECTOR_PREFLIGHT_CONTRACT_READY_FOR_CORE49E",
  "source_seed_count": 1800,
  "source_stage": "A7FF-CORE49",
  "stage": "A7FF-CORE49E"
}
```

## Family / Operator Summary

| semantic_pair                         | operator        |   seed_count |   pass_count |   median_active_ratio |   median_stale_corr |   median_time_shuffle_corr |
|:--------------------------------------|:----------------|-------------:|-------------:|----------------------:|--------------------:|---------------------------:|
| basis_premium_like                    | CSRank          |            8 |            8 |             0.999416  |         0.749341    |                0.697355    |
| basis_premium_like                    | Delta           |            8 |            8 |             0.889735  |         0.781461    |               -0.0149382   |
| basis_premium_like                    | Identity        |            8 |            8 |             0.999416  |         0.799589    |                0.695554    |
| basis_premium_like|basis_premium_like | CSRank          |            8 |            8 |             0.791608  |         0.0895523   |                0.00594125  |
| basis_premium_like|basis_premium_like | Delta           |            8 |            8 |             0.888707  |         0.780888    |                0.000151891 |
| basis_premium_like|basis_premium_like | Identity        |            8 |            8 |             0.987993  |         0.179762    |                0.0147829   |
| basis_premium_like|funding_like       | CSRank          |            8 |            8 |             9e-06     |         0.697261    |               -3.46513e-08 |
| basis_premium_like|funding_like       | Delta           |            8 |            8 |             0.0022125 |         0.0414639   |                0.101654    |
| basis_premium_like|funding_like       | Identity        |            8 |            8 |             9e-06     |         0.915608    |               -2.30894e-09 |
| basis_premium_like|liquidity_like     | CSRank          |            8 |            8 |             0.997726  |         0.310421    |                0.0967863   |
| basis_premium_like|liquidity_like     | Delta           |            8 |            8 |             0.889278  |         0.720894    |                0.000307064 |
| basis_premium_like|liquidity_like     | Identity        |            8 |            8 |             0.996735  |         0.421153    |                0.173361    |
| basis_premium_like|positioning_like   | CSRank          |            8 |            8 |             0.997311  |         0.635453    |                0.0159238   |
| basis_premium_like|positioning_like   | Delta           |            8 |            8 |             0.888341  |         0.082828    |                0.00893433  |
| basis_premium_like|positioning_like   | Identity        |            8 |            8 |             0.996323  |         0.802121    |                0.0375065   |
| basis_premium_like|price_like         | CSRank          |            8 |            8 |             0.992884  |        -0.0143299   |               -0.0100891   |
| basis_premium_like|price_like         | Delta           |            8 |            8 |             0.88919   |         0.0577141   |                2.68286e-05 |
| basis_premium_like|price_like         | Identity        |            8 |            8 |             0.995297  |        -0.0326786   |                0.00284175  |
| basis_premium_like|state_or_taxonomy  | Identity        |            8 |            8 |             0.989628  |         0.00615654  |                0.00543264  |
| basis_premium_like|volatility_like    | CSRank          |            8 |            8 |             0.952195  |         0.652877    |                0.0952007   |
| basis_premium_like|volatility_like    | Delta           |            8 |            8 |             0.849384  |         0.914417    |               -0.00075527  |
| basis_premium_like|volatility_like    | Identity        |            8 |            8 |             0.951307  |         0.833581    |                0.127652    |
| funding_like                          | Delta           |            8 |            8 |             0.410506  |         0.980441    |                0.365546    |
| funding_like|funding_like             | CSRank          |            8 |            8 |             0.118484  |         0.762809    |                0.22629     |
| funding_like|funding_like             | Delta           |            8 |            8 |             0.342874  |         0.984932    |                0.269235    |
| funding_like|funding_like             | Identity        |            8 |            8 |             0.11834   |         0.446878    |                0.263719    |
| funding_like|generic_numeric          | CSRank          |            8 |            8 |             8.35e-05  |         0.466497    |                0.53868     |
| basis_premium_like                    | AbsDelta        |            7 |            7 |             0.997509  |         0.901612    |                0.551032    |
| basis_premium_like                    | SignedRankDelta |            7 |            7 |             0.997922  |         0.734424    |               -0.013949    |
| basis_premium_like                    | SpreadShortLong |            7 |            7 |             0.996839  |         0.976173    |                0.130537    |
| basis_premium_like                    | WinsorZ         |            7 |            7 |             0.997922  |         0.677745    |               -0.0015706   |
| basis_premium_like|basis_premium_like | AbsDelta        |            7 |            7 |             0.991388  |         0.245287    |                0.0157904   |
| basis_premium_like|basis_premium_like | SignedRankDelta |            7 |            7 |             0.991418  |         0.103624    |                0.00385576  |
| basis_premium_like|basis_premium_like | SpreadShortLong |            7 |            7 |             0.99672   |         0.998984    |                0.902697    |
| basis_premium_like|basis_premium_like | WinsorZ         |            7 |            7 |             0.991418  |         0.126432    |                0.00931915  |
| basis_premium_like|funding_like       | SpreadShortLong |            7 |            7 |             0.055209  |         1           |                0.999991    |
| basis_premium_like|liquidity_like     | AbsDelta        |            7 |            7 |             0.996989  |         0.469956    |                0.142546    |
| basis_premium_like|liquidity_like     | SignedRankDelta |            7 |            7 |             0.997105  |         0.381369    |                0.0981005   |
| basis_premium_like|liquidity_like     | SpreadShortLong |            7 |            7 |             0.996933  |         0.999774    |                0.976184    |
| basis_premium_like|liquidity_like     | WinsorZ         |            7 |            7 |             0.997105  |         0.322043    |                0.00960556  |
| basis_premium_like|positioning_like   | AbsDelta        |            7 |            7 |             0.996761  |         0.723133    |                0.039161    |
| basis_premium_like|positioning_like   | SignedRankDelta |            7 |            7 |             0.996876  |         0.719364    |                0.0167699   |
| basis_premium_like|positioning_like   | SpreadShortLong |            7 |            7 |             0.996224  |         0.999999    |                0.999703    |
| basis_premium_like|positioning_like   | WinsorZ         |            7 |            7 |             0.996876  |         0.527695    |                0.0196256   |
| basis_premium_like|price_like         | AbsDelta        |            7 |            7 |             0.994732  |        -0.0284122   |               -0.00361279  |
| basis_premium_like|price_like         | SignedRankDelta |            7 |            7 |             0.995267  |        -0.0192037   |               -0.00234263  |
| basis_premium_like|price_like         | SpreadShortLong |            7 |            7 |             0.996864  |         0.982865    |                0.619592    |
| basis_premium_like|price_like         | WinsorZ         |            7 |            7 |             0.995267  |        -0.0240391   |                0.026411    |
| basis_premium_like|state_or_taxonomy  | AbsDelta        |            7 |            7 |             0.992679  |         0.00232393  |               -0.000606118 |
| basis_premium_like|state_or_taxonomy  | SignedRankDelta |            7 |            7 |             0.992711  |         0.0241544   |                0.00107705  |
| basis_premium_like|state_or_taxonomy  | SpreadShortLong |            7 |            7 |             0.996358  |         0.999521    |                0.984738    |
| basis_premium_like|state_or_taxonomy  | WinsorZ         |            7 |            7 |             0.992711  |         7.46265e-05 |                0.00284022  |
| basis_premium_like|volatility_like    | AbsDelta        |            7 |            7 |             0.951044  |         0.788663    |                0.184658    |
| basis_premium_like|volatility_like    | SignedRankDelta |            7 |            7 |             0.951151  |         0.743303    |                0.107956    |
| basis_premium_like|volatility_like    | SpreadShortLong |            7 |            7 |             0.953644  |         0.999954    |                0.986742    |
| basis_premium_like|volatility_like    | WinsorZ         |            7 |            7 |             0.951151  |         0.560967    |                0.000825268 |
| funding_like                          | AbsDelta        |            7 |            7 |             0.112973  |         0.843668    |                0.320674    |
| funding_like                          | SignedRankDelta |            7 |            7 |             0.195961  |         0.668829    |                0.163483    |
| funding_like                          | SpreadShortLong |            7 |            7 |             0.01026   |         0.994299    |                0.350416    |
| funding_like                          | WinsorZ         |            7 |            7 |             0.195846  |         0.708347    |                0.211631    |
| funding_like|funding_like             | AbsDelta        |            7 |            7 |             0.072829  |         0.661825    |                0.15297     |
| funding_like|funding_like             | SignedRankDelta |            7 |            7 |             0.113015  |         0.793867    |                0.178822    |
| funding_like|funding_like             | SpreadShortLong |            7 |            7 |             0.00886   |         0.998326    |                0.945336    |
| funding_like|funding_like             | WinsorZ         |            7 |            7 |             0.112906  |         0.516498    |                0.0227348   |
| funding_like|generic_numeric          | AbsDelta        |            7 |            7 |             1.3e-05   |         0.705774    |                0.214894    |
| funding_like|generic_numeric          | Identity        |            7 |            7 |             4.9e-05   |         0.470301    |                0.413803    |
| funding_like|generic_numeric          | SignedRankDelta |            7 |            7 |             2.6e-05   |         0.46644     |                0.00784917  |
| funding_like|generic_numeric          | SpreadShortLong |            7 |            7 |             0.002758  |         0.991353    |                0.779965    |
| funding_like|generic_numeric          | WinsorZ         |            7 |            7 |             2.6e-05   |         0.529335    |                0.00695933  |
| funding_like|liquidity_like           | AbsDelta        |            7 |            7 |             0.105468  |         0.541388    |                0.0340928   |
| funding_like|liquidity_like           | CSRank          |            7 |            7 |             0.196501  |         0.372453    |                0.0893837   |
| funding_like|liquidity_like           | Delta           |            7 |            7 |             0.371287  |         0.615272    |                0.00512353  |
| funding_like|liquidity_like           | Identity        |            7 |            7 |             0.19634   |         0.267596    |                0.064083    |
| funding_like|liquidity_like           | SignedRankDelta |            7 |            7 |             0.194477  |         0.412677    |                0.090358    |
| funding_like|liquidity_like           | SpreadShortLong |            7 |            7 |             0.008947  |         0.996156    |                0.813527    |
| funding_like|liquidity_like           | WinsorZ         |            7 |            7 |             0.194343  |         0.340588    |                0.0363648   |
| funding_like|positioning_like         | AbsDelta        |            7 |            7 |             0.105407  |         0.586505    |               -0.00420035  |
| funding_like|positioning_like         | CSRank          |            7 |            7 |             0.196463  |         0.632103    |               -0.00975645  |
| funding_like|positioning_like         | Delta           |            7 |            7 |             0.371169  |         0.891535    |               -0.00337959  |
| funding_like|positioning_like         | Identity        |            7 |            7 |             0.196303  |         0.376435    |               -0.00876222  |

## Missing Fields

`<empty>`

## Eval Failures

`<empty>`

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE49E full run": false,
    "A7FF-CORE49ER preflight forensic": false,
    "A7FF-CORE50 contract/arbitration": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "formula_search": true,
    "large_search": true,
    "numeric_replay": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```
