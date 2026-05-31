# CRYPTO A7FF-55R1 SUPPLEMENTAL QUEUE FEASIBILITY

Generated: 2026-05-31T11:45:14Z

## Decision

`HOLD_A7FF55R1_SUPPLEMENTAL_QUEUE_ATLAS_COVERAGE_FAIL`

A7FF-55R1 checks whether the current A7FF v20260530 formula atlas can satisfy the A7FF-55R supplemental family quotas. It does not run numeric replay or search.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "open_interest_like_absent_from_formula_index",
    "liquidity_like_absent_from_materialization_queue",
    "taker_flow_like_absent_from_formula_index"
  ],
  "decision": "HOLD_A7FF55R1_SUPPLEMENTAL_QUEUE_ATLAS_COVERAGE_FAIL",
  "executes_replay": false,
  "executes_search": false,
  "families_feasible_from_formula_index": 3,
  "families_feasible_from_materialized_queue": 2,
  "families_required_positive_quota": 5,
  "formula_index_rows": 20599,
  "generated_at": "2026-05-31T11:45:14Z",
  "next_allowed": "A7FF-55R2 atlas field-family generation repair",
  "quota_rows": 7,
  "stage": "A7FF-55R1",
  "uses_may": false
}
```

## Family Feasibility

| field_family       |   required_min_primary_candidates |   formula_count |   materialization_queue_count |   company_wave_queue_count |   semantic_pair_count |   motif_count | feasible_for_supplemental_numeric   | feasible_for_existing_materialized_numeric   |
|:-------------------|----------------------------------:|----------------:|------------------------------:|---------------------------:|----------------------:|--------------:|:------------------------------------|:---------------------------------------------|
| open_interest_like |                                12 |               0 |                             0 |                          0 |                     0 |             0 | False                               | False                                        |
| positioning_like   |                                12 |           10781 |                           413 |                         13 |                     2 |             9 | True                                | True                                         |
| liquidity_like     |                                10 |             186 |                             0 |                          0 |                     2 |             8 | True                                | False                                        |
| volatility_like    |                                10 |            2384 |                           595 |                        595 |                     5 |            10 | True                                | True                                         |
| taker_flow_like    |                                 8 |               0 |                             0 |                          0 |                     0 |             0 | False                               | False                                        |
| basis_premium_like |                                 0 |           13744 |                          2377 |                       2177 |                     9 |            10 | False                               | False                                        |
| regime_state       |                                 0 |               0 |                             0 |                          0 |                     0 |             0 | False                               | False                                        |

## Top Atlas Family / Motif Availability

| semantic_pair                          | motif               |   formula_count |   materialization_count |   company_wave_count |
|:---------------------------------------|:--------------------|----------------:|------------------------:|---------------------:|
| basis_premium_like\|funding_like       | relative_shock      |            1091 |                     314 |                  314 |
| basis_premium_like\|funding_like       | mean_reversion_gate |            1004 |                     256 |                  256 |
| basis_premium_like\|price_like         | smooth_mul          |             243 |                     172 |                  172 |
| basis_premium_like\|basis_premium_like | smooth_mul          |             178 |                     165 |                  165 |
| basis_premium_like\|volatility_like    | smooth_mul          |             510 |                     129 |                  129 |
| basis_premium_like\|funding_like       | gated_sign          |             331 |                     127 |                  127 |
| basis_premium_like\|volatility_like    | spread_rank         |             257 |                     114 |                  114 |
| basis_premium_like\|price_like         | spread_rank         |             119 |                      87 |                   87 |
| basis_premium_like                     | single              |              81 |                      81 |                   81 |
| basis_premium_like\|basis_premium_like | spread_rank         |              79 |                      66 |                   66 |
| basis_premium_like\|volatility_like    | gated_sign          |             148 |                      64 |                   64 |
| basis_premium_like\|volatility_like    | mul                 |             148 |                      64 |                   64 |
| basis_premium_like\|funding_like       | mul                 |             315 |                      62 |                   62 |
| basis_premium_like\|price_like         | gated_sign          |              77 |                      62 |                   62 |
| basis_premium_like\|price_like         | mul                 |              77 |                      62 |                   62 |
| basis_premium_like\|price_like         | safe_div_abs        |              77 |                      62 |                   62 |
| basis_premium_like\|price_like         | sub                 |              77 |                      52 |                   52 |
| volatility_like                        | single              |              84 |                      48 |                   48 |
| price_like\|volatility_like            | smooth_mul          |             112 |                      42 |                   42 |
| basis_premium_like\|basis_premium_like | mul                 |              50 |                      41 |                   41 |
| basis_premium_like\|basis_premium_like | sub                 |              50 |                      41 |                   41 |
| basis_premium_like\|basis_premium_like | gated_sign          |              43 |                      34 |                   34 |
| price_like                             | single              |              34 |                      34 |                   34 |
| basis_premium_like\|basis_premium_like | safe_div_abs        |              42 |                      33 |                   33 |
| price_like\|volatility_like            | spread_rank         |              62 |                      32 |                   32 |
| basis_premium_like\|volatility_like    | safe_div_abs        |             147 |                      24 |                   24 |
| basis_premium_like\|volatility_like    | sub                 |             147 |                      24 |                   24 |
| basis_premium_like\|funding_like       | safe_div_abs        |             331 |                      22 |                   22 |
| basis_premium_like\|funding_like       | signed_spread       |            1274 |                     219 |                   19 |
| funding_like\|positioning_like         | gated_sign          |             466 |                     162 |                   13 |
| price_like\|volatility_like            | mul                 |              58 |                      12 |                   12 |
| price_like\|volatility_like            | gated_sign          |              56 |                      12 |                   12 |
| volatility_like\|volatility_like       | smooth_mul          |              56 |                      11 |                   11 |
| volatility_like\|volatility_like       | spread_rank         |              31 |                      11 |                   11 |
| price_like\|volatility_like            | sub                 |              58 |                       2 |                    2 |
| price_like\|volatility_like            | safe_div_abs        |              56 |                       2 |                    2 |
| volatility_like\|volatility_like       | gated_sign          |              31 |                       1 |                    1 |
| volatility_like\|volatility_like       | mul                 |              31 |                       1 |                    1 |
| volatility_like\|volatility_like       | safe_div_abs        |              31 |                       1 |                    1 |
| volatility_like\|volatility_like       | sub                 |              31 |                       1 |                    1 |
| funding_like\|positioning_like         | mean_reversion_gate |             896 |                      97 |                    0 |
| funding_like\|positioning_like         | mul                 |             505 |                      82 |                    0 |
| funding_like\|positioning_like         | relative_shock      |             854 |                      65 |                    0 |
| funding_like\|positioning_like         | signed_spread       |             962 |                       5 |                    0 |
| funding_like\|positioning_like         | safe_div_abs        |             465 |                       2 |                    0 |
| basis_premium_like\|positioning_like   | signed_spread       |            1178 |                       0 |                    0 |
| basis_premium_like\|positioning_like   | mean_reversion_gate |            1021 |                       0 |                    0 |
| basis_premium_like\|positioning_like   | smooth_mul          |             885 |                       0 |                    0 |
| basis_premium_like\|funding_like       | smooth_mul          |             834 |                       0 |                    0 |
| funding_like\|positioning_like         | smooth_mul          |             729 |                       0 |                    0 |
| funding_like\|positioning_like         | spread_rank         |             613 |                       0 |                    0 |
| basis_premium_like\|positioning_like   | spread_rank         |             552 |                       0 |                    0 |
| funding_like\|positioning_like         | sub                 |             510 |                       0 |                    0 |
| basis_premium_like\|funding_like       | spread_rank         |             505 |                       0 |                    0 |
| basis_premium_like\|positioning_like   | relative_shock      |             485 |                       0 |                    0 |
| basis_premium_like\|funding_like       | sub                 |             315 |                       0 |                    0 |
| basis_premium_like\|positioning_like   | mul                 |             169 |                       0 |                    0 |
| basis_premium_like\|positioning_like   | sub                 |             169 |                       0 |                    0 |
| basis_premium_like\|positioning_like   | gated_sign          |             161 |                       0 |                    0 |
| basis_premium_like\|positioning_like   | safe_div_abs        |             161 |                       0 |                    0 |
| basis_premium_like\|volatility_like    | mean_reversion_gate |              98 |                       0 |                    0 |
| basis_premium_like\|volatility_like    | signed_spread       |              96 |                       0 |                    0 |
| basis_premium_like\|price_like         | mean_reversion_gate |              49 |                       0 |                    0 |
| basis_premium_like\|price_like         | signed_spread       |              48 |                       0 |                    0 |
| liquidity_like\|volatility_like        | mean_reversion_gate |              36 |                       0 |                    0 |
| liquidity_like\|volatility_like        | signed_spread       |              36 |                       0 |                    0 |
| liquidity_like\|volatility_like        | smooth_mul          |              26 |                       0 |                    0 |
| liquidity_like\|volatility_like        | spread_rank         |              26 |                       0 |                    0 |
| basis_premium_like\|liquidity_like     | smooth_mul          |              15 |                       0 |                    0 |
| basis_premium_like\|liquidity_like     | spread_rank         |              15 |                       0 |                    0 |
| basis_premium_like\|volatility_like    | relative_shock      |              12 |                       0 |                    0 |
| basis_premium_like\|liquidity_like     | gated_sign          |               8 |                       0 |                    0 |
| basis_premium_like\|liquidity_like     | mul                 |               8 |                       0 |                    0 |
| basis_premium_like\|liquidity_like     | safe_div_abs        |               8 |                       0 |                    0 |
| basis_premium_like\|liquidity_like     | sub                 |               8 |                       0 |                    0 |
| basis_premium_like\|generic_numeric    | smooth_mul          |               6 |                       0 |                    0 |
| basis_premium_like\|generic_numeric    | spread_rank         |               6 |                       0 |                    0 |
| basis_premium_like\|price_like         | relative_shock      |               6 |                       0 |                    0 |
| basis_premium_like\|state_or_taxonomy  | signed_spread       |               6 |                       0 |                    0 |
| basis_premium_like\|state_or_taxonomy  | smooth_mul          |               6 |                       0 |                    0 |

## Boundary

```text
feasibility audit executed: true
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
