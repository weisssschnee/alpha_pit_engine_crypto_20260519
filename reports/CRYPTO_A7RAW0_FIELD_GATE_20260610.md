# CRYPTO A7RAW0 Field Gate 20260610

## Decision

`PASS_A7LS_FIELD_GATE_CURRENT_QUEUE_CLEAN`

This is a field ingress gate for the A7RAW0 lightly governed large-space queue. It does not run numeric compute, replay, search, or alpha proof.

## Counts

- queue_rows: 16384
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
| latent_schema         | OK_BACKFILLED_BY_EXTENSION_REGISTRY |             8 |                  6749 |
| derived_dep_generated | OK_BACKFILLED_BY_EXTENSION_REGISTRY |             3 |                  3724 |
| upper_alias           | OK_BACKFILLED_BY_EXTENSION_REGISTRY |             5 |                  3708 |
| base_schema           | OK_IN_A7AIF3_CONTRACT               |            15 |                 16947 |
| latent_schema         | OK_IN_A7AIF3_CONTRACT               |             2 |                  1224 |

## Drift Fields

`<empty>`

## Blocked Fields

`<empty>`

## Formula Gate Summary

| gate_decision   | semantic_pair                |   formula_count |
|:----------------|:-----------------------------|----------------:|
| PASS            | basis\|positioning           |            1907 |
| PASS            | open_interest\|positioning   |            1860 |
| PASS            | positioning\|positioning     |            1416 |
| PASS            | basis\|open_interest         |            1238 |
| PASS            | positioning\|regime          |            1116 |
| PASS            | age\|positioning             |             861 |
| PASS            | positioning\|taker_flow      |             745 |
| PASS            | open_interest\|regime        |             712 |
| PASS            | basis\|regime                |             710 |
| PASS            | basis\|basis                 |             579 |
| PASS            | age\|open_interest           |             570 |
| PASS            | age\|basis                   |             556 |
| PASS            | open_interest\|open_interest |             537 |
| PASS            | open_interest\|taker_flow    |             483 |
| PASS            | basis\|taker_flow            |             418 |
| PASS            | age\|regime                  |             341 |
| PASS            | regime\|taker_flow           |             283 |
| PASS            | age_vol\|positioning         |             252 |
| PASS            | age\|taker_flow              |             231 |
| PASS            | coverage\|positioning        |             205 |
| PASS            | regime\|regime               |             201 |
| PASS            | basis\|coverage              |             148 |
| PASS            | coverage\|open_interest      |             135 |
| PASS            | age_vol\|basis               |             134 |
| PASS            | age_vol\|open_interest       |             125 |
| PASS            | age\|age                     |             116 |
| PASS            | age_vol\|regime              |              98 |
| PASS            | taker_flow\|taker_flow       |              84 |
| PASS            | coverage\|regime             |              82 |
| PASS            | age\|age_vol                 |              68 |
| PASS            | age\|coverage                |              56 |
| PASS            | age_vol\|taker_flow          |              53 |
| PASS            | coverage\|taker_flow         |              42 |
| PASS            | age_vol\|coverage            |              17 |
| PASS            | coverage\|coverage           |               4 |
| PASS            | age_vol\|age_vol             |               1 |

## Outputs

- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7raw0_field_gate_20260610\a7ls_field_gate_manifest.json`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7raw0_field_gate_20260610\a7ls_field_gate_field_route_map.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7raw0_field_gate_20260610\a7ls_field_gate_formula_audit.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7raw0_field_gate_20260610\a7ls_field_gate_contract_drift_fields.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7raw0_field_gate_20260610\a7ls_field_gate_blocked_fields.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7raw0_field_gate_20260610\a7ls_field_gate_route_summary.csv`
- `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7raw0_field_gate_20260610\a7ls_field_gate_formula_gate_summary.csv`
