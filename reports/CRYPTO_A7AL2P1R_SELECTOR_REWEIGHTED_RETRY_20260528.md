# CRYPTO A7AL-2P1R Selector-Reweighted Retry

Generated: 2026-05-28T02:38:13Z

## Decision

```text
HOLD_A7AL2P1R_NO_SELECTOR_ELIGIBLE_CANDIDATES
```

No A7AL-2P1 selector-eligible candidates were available. This file intentionally replaces any previous P1R pass artifacts so stale selector output cannot be used downstream.

## Manifest

```json
{
  "authorizes_a7al2p_contract": false,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "no_selector_eligible_candidates"
  ],
  "candidate_count": 0,
  "decision": "HOLD_A7AL2P1R_NO_SELECTOR_ELIGIBLE_CANDIDATES",
  "decision_counts": {},
  "diagnostic_pass_count": 0,
  "executes_alpha_proof": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-28T02:38:13Z",
  "input": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7al2p1_selector_feature_generation\\a7al2p1_selector_feature_matrix.csv",
  "required_next": "regenerate or adjust non-May selector inputs; do not use stale P1R pass artifacts",
  "uses_may_for_selection": false,
  "warnings": []
}
```

## Boundary

```text
Not authorized:
  A7AL-2P contract
  formula search execution
  alpha proof
  shadow / paper / live
```
