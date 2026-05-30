# CRYPTO A7FF-52E MATERIALIZATION PREFLIGHT

Generated: 2026-05-30T20:11:46Z

## Decision

`PASS_A7FF52E_MATERIALIZATION_PREFLIGHT_READY_FOR_NUMERIC_CONTRACT`

A7FF-52E evaluates a 1,200-row family-balanced materialization sample from A7FF51E. It does not compute labels, numeric replay, or search.

## Manifest

```json
{
  "activity_ok_rate": 0.875,
  "authorizes_alpha_proof": false,
  "authorizes_numeric_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "base_field_count": 4,
  "blockers": [],
  "decision": "PASS_A7FF52E_MATERIALIZATION_PREFLIGHT_READY_FOR_NUMERIC_CONTRACT",
  "dense_field_count": 0,
  "eval_failure_count": 0,
  "executes_materialization": true,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "execution_authorization_source": "latest_user_continue_request_after_A7FF52_contract",
  "families_retained": 7,
  "generated_at": "2026-05-30T20:11:46Z",
  "latent_field_count": 4,
  "low_activity_families": [
    "funding_like|basis_premium_like"
  ],
  "missing_fields": [],
  "sample_family_count": 8,
  "sample_rows": 1200,
  "stage": "A7FF-52E",
  "uses_may": false
}
```

## Family Summary

| semantic_pair                        |   rows |   eval_success_rows |   activity_ok_rows |   median_finite_share |   median_nonzero_share |   median_std |
|:-------------------------------------|-------:|--------------------:|-------------------:|----------------------:|-----------------------:|-------------:|
| basis_premium_like|price_return_like |    150 |                 150 |                150 |            0.820741   |               0.999993 |  2.09564     |
| funding_like|basis_premium_like      |    150 |                 150 |                  0 |            0.00335452 |               0.995041 |  0.707107    |
| liquidity_like|price_return_like     |    150 |                 150 |                150 |            0.820741   |               0.996074 |  0.953852    |
| open_interest_like|price_return_like |    150 |                 150 |                150 |            0.820681   |               1        |  0.99051     |
| positioning_like|price_return_like   |    150 |                 150 |                150 |            0.992531   |               1        |  0.994682    |
| regime_state|price_return_like       |    150 |                 150 |                150 |            0.820741   |               0.999993 |  2.09564     |
| taker_flow_like|basis_premium_like   |    150 |                 150 |                150 |            0.82505    |               1        |  1.32395e+07 |
| volatility_like|basis_premium_like   |    150 |                 150 |                150 |            0.820741   |               1        |  0.99472     |

## Boundary

```text
materialization executed: true
numeric replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
