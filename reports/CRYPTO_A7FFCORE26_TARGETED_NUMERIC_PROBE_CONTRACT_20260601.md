# CRYPTO A7FF-CORE26 TARGETED NUMERIC PROBE CONTRACT

Generated: 2026-06-01T15:47:32Z

## Decision

`PASS_A7FFCORE26_TARGETED_NUMERIC_PROBE_CONTRACT_READY_FOR_CORE26E`

CORE26 defines a bounded numeric probe over the CORE25E targeted preflight packet. It does not authorize search, large search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core26e": true,
  "authorizes_formula_generation": false,
  "authorizes_large_search": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FFCORE26_TARGETED_NUMERIC_PROBE_CONTRACT_READY_FOR_CORE26E",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T15:47:32Z",
  "next_allowed": "A7FF-CORE26E targeted numeric probe execution",
  "numeric_probe_quota": 480,
  "source_decision": "PASS_A7FFCORE25E_TARGETED_GENERATION_PREFLIGHT_PACKET_READY_FOR_CORE26_CONTRACT",
  "source_stage": "A7FF-CORE25E",
  "stage": "A7FF-CORE26"
}
```

## Probe Policy

| lane                           |   numeric_probe_quota | priority                        |
|:-------------------------------|----------------------:|:--------------------------------|
| S0_positioning_price_basis     |                   160 | primary missing executable lane |
| S1_liquidity_basis_positioning |                   160 | primary one-bar conversion lane |
| S2_taker_flow_liquidity_oi     |                    80 | calibration executable lane     |
| S3_cross_family_bridge         |                    80 | calibration non-L5 bridge lane  |

## Gates

| gate                           | threshold                   |
|:-------------------------------|:----------------------------|
| eval_failure_count             | 0                           |
| missing_field_count            | 0 or documented unsupported |
| one_bar_executable_clean_count | >= 6                        |
| one_bar_executable_lane_count  | >= 3                        |
| non_l5_clean_count             | >= 3                        |
| same_bar_only_policy           | diagnostic only             |
| search_authorization           | false                       |

## Expected Outputs

| artifact                          | description                                        |
|:----------------------------------|:---------------------------------------------------|
| a7ffcore26e_numeric_rows.csv      | candidate split/cost/horizon numeric response rows |
| a7ffcore26e_candidate_summary.csv | candidate-level clean/control/lag summary          |
| a7ffcore26e_lane_summary.csv      | lane-level executable clean supply                 |
| a7ffcore26e_eval_errors.csv       | fail-closed evaluator errors                       |
