# CRYPTO A7FF-R11 FEATURE / LABEL OBJECTIVE RESET

Generated: 2026-05-30T18:55:00Z

## Decision

`PASS_A7FFR11_FEATURE_LABEL_OBJECTIVE_RESET_READY_FOR_A7FF51_CONTRACT_NO_SEARCH_AUTH`

A7FF-R11 is a compact reset stage. It converts the A7FF-49 hold into a stricter non-L5-first objective policy and adds an artifact budget for future A7FF work.

## Manifest

```json
{
  "authorizes_a7ff51_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_generation_execution": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFR11_FEATURE_LABEL_OBJECTIVE_RESET_READY_FOR_A7FF51_CONTRACT_NO_SEARCH_AUTH",
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T18:55:00Z",
  "next_contract": {
    "artifact_budget": {
      "max_new_reports": 1,
      "max_new_runtime_tables": 3,
      "required_manifest": true
    },
    "authorized": true,
    "blocked": [
      "formula_search",
      "large_search",
      "alpha_proof",
      "shadow",
      "paper",
      "live"
    ],
    "execution_type": "contract_only",
    "hard_requirements": {
      "control_ratio_max": 0.8,
      "min_non_reference_families_before_replay": 2,
      "min_non_reference_rows_before_replay": 6,
      "primary_labels": [
        "L0_raw_forward_return",
        "L1_cross_sectional_relative_return",
        "L3_liquidity_tier_relative_return"
      ],
      "reference_family_cannot_count_as_primary": true
    },
    "name": "non-L5-first derived generation contract",
    "no_search": true,
    "stage": "A7FF-51"
  },
  "reason": "A7FF-49 found zero non-reference non-L5 candidates in existing maps",
  "source_a7ff49_decision": "HOLD_A7FF49_NO_NON_REFERENCE_NON_L5_CANDIDATES",
  "stage": "A7FF-R11",
  "uses_may": false,
  "warnings": [
    "artifact_budget_enforced_for_future_a7ff_stages"
  ]
}
```

## Compact Reset Policy

| policy_area      | rule                                                                                       | reason                                                                          |
|:-----------------|:-------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------|
| artifact_hygiene | future A7FF stages should emit one report, one manifest, and only essential machine tables | avoid runtime sprawl and preserve source-of-truth clarity                       |
| label_target     | promotion requires non-reference evidence on L0/L1/L3 before L5 can support a clue         | current frozen pool is L5-only and does not translate to raw or relative labels |
| reference_family | basis_premium self-pair is reference-only until confirmed by non-self semantic pair        | A7FF-49 found all non-L5 evidence only inside the reference family              |
| next_execution   | authorize only a compact A7FF-51 non-L5-first generation contract; no search execution     | existing numeric maps do not contain a usable non-reference non-L5 pool         |

## A7FF-49 Non-L5 Summary

| candidate_role              | semantic_pair                         | label_family                       |   rows |   blueprints |   motifs |   median_control_ratio |   min_cost10 |   min_robust_floor |
|:----------------------------|:--------------------------------------|:-----------------------------------|-------:|-------------:|---------:|-----------------------:|-------------:|-------------------:|
| reference_non_l5_diagnostic | basis_premium_like|basis_premium_like | L0_raw_forward_return              |      2 |            2 |        1 |               0.636908 |  6.79017e-05 |            1.39731 |
| reference_non_l5_diagnostic | basis_premium_like|basis_premium_like | L1_cross_sectional_relative_return |      2 |            2 |        1 |               0.636908 |  6.79017e-05 |            1.39731 |

## Boundary

```text
generation executed: false
numeric probe executed: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
