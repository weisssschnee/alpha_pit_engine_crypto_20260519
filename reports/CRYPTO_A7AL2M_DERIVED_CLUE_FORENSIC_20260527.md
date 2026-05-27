# CRYPTO A7AL-2M Derived Clue Forensic

Generated: 2026-05-27T12:59:41Z

## Decision

```text
PASS_A7AL2M_DERIVED_CLUE_POOL_READY_FOR_DEEP_AUDIT
```

This stage classifies A7AL-2L replay-preflight clues. It does not run new replay and does not authorize formula search execution or alpha proof.

## Manifest

```json
{
  "authorizes_a7al2n_deep_audit": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "cell_count": 4,
  "clue_count": 10,
  "decision": "PASS_A7AL2M_DERIVED_CLUE_POOL_READY_FOR_DEEP_AUDIT",
  "deep_audit_candidate_count": 4,
  "field_family_count": 6,
  "generated_at": "2026-05-27T12:59:41Z",
  "input_a7al2l_decision": "PASS_A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUES_FOUND_EXECUTION_HOLD",
  "quality_counts": {
    "A7AL2M_CONTROL_MARGIN_THIN_CLUE": 1,
    "A7AL2M_DEEP_AUDIT_CANDIDATE": 4,
    "A7AL2M_STRESS_DIVERGENT_CLUE": 5
  },
  "stress_divergent_clue_count": 5,
  "warnings": [
    "stress_divergent_clues_present"
  ]
}
```

## Quality Summary

| quality_label                   |   count |
|:--------------------------------|--------:|
| A7AL2M_STRESS_DIVERGENT_CLUE    |       5 |
| A7AL2M_DEEP_AUDIT_CANDIDATE     |       4 |
| A7AL2M_CONTROL_MARGIN_THIN_CLUE |       1 |

## Cell / Family Summary

| cell                        | family                      | field_families          |   count |
|:----------------------------|:----------------------------|:------------------------|--------:|
| J0_oi_derived_state         | derived_oi_price_state      | open_interest           |       1 |
| J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     |       3 |
| J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity|price         |       1 |
| J3_basis_funding_derived    | derived_basis_funding_state | basis|funding           |       1 |
| J4_upper_regime_interaction | derived_upper_regime_proxy  | basis|liquidity         |       2 |
| J4_upper_regime_interaction | derived_upper_regime_proxy  | liquidity|open_interest |       2 |

## Clue Shortlist

| candidate_id            | cell                        | family                      | field_families          | quality_label                   |   premay_mean_spread |   original_may_stress_spread |   lag_recent_retention |   control_dominance_ratio_premay_max |
|:------------------------|:----------------------------|:----------------------------|:------------------------|:--------------------------------|---------------------:|-----------------------------:|-----------------------:|-------------------------------------:|
| a7al2k_0096829c83c908a8 | J4_upper_regime_interaction | derived_upper_regime_proxy  | liquidity|open_interest | A7AL2M_STRESS_DIVERGENT_CLUE    |          -0.00139574 |                  0.000152454 |               0.978343 |                             1.05137  |
| a7al2k_01bdc8d049fffe52 | J4_upper_regime_interaction | derived_upper_regime_proxy  | liquidity|open_interest | A7AL2M_STRESS_DIVERGENT_CLUE    |          -0.00203605 |                  0.0011895   |               0.972014 |                             1.22977  |
| a7al2k_01759e5da72c472c | J4_upper_regime_interaction | derived_upper_regime_proxy  | basis|liquidity         | A7AL2M_DEEP_AUDIT_CANDIDATE     |          -0.00207791 |                 -0.00338678  |               0.978613 |                             0.946342 |
| a7al2k_0cf817ef95787b3d | J4_upper_regime_interaction | derived_upper_regime_proxy  | basis|liquidity         | A7AL2M_DEEP_AUDIT_CANDIDATE     |          -0.00345631 |                 -0.00648685  |               0.968958 |                             1.04108  |
| a7al2k_046e806368e99c76 | J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     | A7AL2M_STRESS_DIVERGENT_CLUE    |           0.0016886  |                 -0.00164923  |               0.985509 |                             0.79335  |
| a7al2k_16eeb579c992bb45 | J3_basis_funding_derived    | derived_basis_funding_state | basis|funding           | A7AL2M_CONTROL_MARGIN_THIN_CLUE |          -0.001847   |                 -0.00127831  |               0.719808 |                             1.15123  |
| a7al2k_09e91fd6263c0156 | J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     | A7AL2M_STRESS_DIVERGENT_CLUE    |           0.0015923  |                 -0.0016712   |               0.993134 |                             1.02337  |
| a7al2k_134ec76b5d7444f9 | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity|price         | A7AL2M_DEEP_AUDIT_CANDIDATE     |          -0.00283629 |                 -0.00385336  |               0.961596 |                             1.06869  |
| a7al2k_0a247ec03472983b | J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     | A7AL2M_STRESS_DIVERGENT_CLUE    |           0.0015688  |                 -0.00166771  |               0.989259 |                             0.88085  |
| a7al2k_01298a6b5902f416 | J0_oi_derived_state         | derived_oi_price_state      | open_interest           | A7AL2M_DEEP_AUDIT_CANDIDATE     |          -0.00138889 |                 -0.00171216  |               0.990979 |                             0.932378 |

## Boundary

```text
Deep audit candidate:
  clean enough for A7AL-2N forensic only.

Stress divergent clue:
  may still be useful as a regime clue, but not a promotion candidate.

Not authorized:
  alpha proof
  shadow / paper / live
  large formula search
```
