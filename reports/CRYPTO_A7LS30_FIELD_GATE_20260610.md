# CRYPTO A7LS30 Field Gate 20260610

## Decision

`PASS_A7LS_FIELD_GATE_CURRENT_QUEUE_CLEAN`

This is a field ingress gate for the A7LS30 productive follow-up queue. It does not run numeric compute, replay, search, or alpha proof.

## Counts

- queue_rows: 8192
- expression_field_count: 31
- total_field_count_including_system: 33
- unresolved_field_count: 0
- contract_drift_field_count: 0
- blocked_formula_count: 0
- contract_drift_formula_count: 0
- authorizes_current_running_wave_to_continue: true
- authorizes_next_search_expansion: true

## Interpretation

Unresolved fields block execution. Fields resolved only through runner-local aliases or derived dependency code are not immediate execution blockers, but they are contract drift until they are backfilled into the shared field registry / A7AIF materialization matrix.

## Route Summary

| route                 | contract_status                     |   field_count |   formula_usage_count |
|:----------------------|:------------------------------------|--------------:|----------------------:|
| latent_schema         | OK_BACKFILLED_BY_EXTENSION_REGISTRY |             8 |                  2699 |
| upper_alias           | OK_BACKFILLED_BY_EXTENSION_REGISTRY |             5 |                  2128 |
| derived_dep_generated | OK_BACKFILLED_BY_EXTENSION_REGISTRY |             3 |                  1503 |
| base_schema           | OK_IN_A7AIF3_CONTRACT               |            15 |                 11594 |
| latent_schema         | OK_IN_A7AIF3_CONTRACT               |             2 |                    65 |

## Drift Fields

`<empty>`

## Blocked Fields

`<empty>`

## Formula Gate Summary

| gate_decision   | semantic_pair                                          |   formula_count |
|:----------------|:-------------------------------------------------------|----------------:|
| PASS            | basis_premium_like\|positioning_like                   |            2804 |
| PASS            | open_interest_like\|positioning_like\|regime_state     |            2048 |
| PASS            | open_interest_like\|positioning_like                   |            1536 |
| PASS            | open_interest_like\|positioning_like\|listing_age_like |            1235 |
| PASS            | basis_premium_like\|age_x_volatility\|positioning_like |             569 |

## Outputs

- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls30_field_gate_20260610\a7ls_field_gate_manifest.json`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls30_field_gate_20260610\a7ls_field_gate_field_route_map.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls30_field_gate_20260610\a7ls_field_gate_formula_audit.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls30_field_gate_20260610\a7ls_field_gate_contract_drift_fields.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls30_field_gate_20260610\a7ls_field_gate_blocked_fields.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls30_field_gate_20260610\a7ls_field_gate_route_summary.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7ls30_field_gate_20260610\a7ls_field_gate_formula_gate_summary.csv`
