# CRYPTO A7FF-0 FIELD-TO-FACTOR COMPILER

Generated: 2026-05-29T16:16:57Z

## Decision

`PASS_A7FF0_FIELD_ONTOLOGY_V2_BUILT`

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "decision": "PASS_A7FF0_FIELD_ONTOLOGY_V2_BUILT",
  "executes_replay": false,
  "executes_search": false,
  "field_count": 81,
  "generated_at": "2026-05-29T16:16:57Z",
  "semantic_type_count": 8,
  "signal_seed_candidate_count": 1,
  "stage": "A7FF-0"
}
```

## Semantic Type Summary

| semantic_type      | compiler_role                |   field_count |
|:-------------------|:-----------------------------|--------------:|
| basis_premium_like | forbidden_or_unlicensed      |             2 |
| basis_premium_like | regime_or_diagnostic_input   |            17 |
| basis_premium_like | signal_seed_candidate        |             1 |
| categorical_state  | regime_or_diagnostic_input   |             8 |
| generic_numeric    | forbidden_or_unlicensed      |             8 |
| generic_numeric    | regime_or_diagnostic_input   |             3 |
| liquidity_like     | forbidden_or_unlicensed      |             3 |
| liquidity_like     | regime_or_diagnostic_input   |             8 |
| positioning_like   | regime_or_diagnostic_input   |             8 |
| positioning_like   | risk_exposure_or_neutralizer |             7 |
| price_like         | forbidden_label_or_future    |             1 |
| price_like         | regime_or_diagnostic_input   |             2 |
| price_like         | risk_exposure_or_neutralizer |             1 |
| rate_like          | forbidden_or_unlicensed      |             4 |
| rate_like          | regime_or_diagnostic_input   |             2 |
| volatility_like    | regime_or_diagnostic_input   |             6 |

## Boundary

No replay, no formula search, no alpha proof.
