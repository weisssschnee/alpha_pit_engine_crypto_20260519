# CRYPTO A7FF-17 FOLLOWUP SELECTOR TRIAGE

Generated: 2026-05-30T04:50:48Z

## Decision

`HOLD_A7FF17_INTERNAL_SELECTOR_LABEL_CONCENTRATION_PERSISTS`

A7FF-17 compares the A7FF-16 numeric clue surface with the A7FF-8 internal selected portfolio queue. The clue surface remains label-diverse, but the internal selector is still label-concentrated.

## Manifest

```json
{
  "authorizes_a7ff18_external_label_balanced_selector": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "HOLD_A7FF17_INTERNAL_SELECTOR_LABEL_CONCENTRATION_PERSISTS",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T04:50:48Z",
  "raw_non_l7_clue_rows": 402,
  "raw_non_l7_label_families": 4,
  "raw_top_label_share": 0.3034825870646766,
  "selected_non_l7_label_families": 4,
  "selected_non_l7_rows": 57,
  "selected_non_l7_top_label_share": 0.8596491228070176,
  "selected_rows": 59,
  "selected_top_label_share": 0.8305084745762712,
  "source_a7ff16_decision": "PASS_A7FF16_COMPANY_NUMERIC_FOLLOWUP_AGGREGATE_BUILT",
  "stage": "A7FF-17-FOLLOWUP-SELECTOR-TRIAGE",
  "uses_may": false
}
```

## Raw Non-L7 Clue Label Distribution

| label_family                       |   count |    share |
|:-----------------------------------|--------:|---------:|
| L5_vol_adjusted_return             |     122 | 0.303483 |
| L1_cross_sectional_relative_return |      97 | 0.241294 |
| L0_raw_forward_return              |      92 | 0.228856 |
| L3_liquidity_tier_relative_return  |      91 | 0.226368 |

## Internal Selected Label Distribution

| label_family                       |   count |     share |
|:-----------------------------------|--------:|----------:|
| L5_vol_adjusted_return             |      49 | 0.830508  |
| L3_liquidity_tier_relative_return  |       5 | 0.0847458 |
| L1_cross_sectional_relative_return |       2 | 0.0338983 |
| L7_ranked_future_return            |       2 | 0.0338983 |
| L0_raw_forward_return              |       1 | 0.0169492 |

## Internal Selected Non-L7 Label Distribution

| label_family                       |   count |     share |
|:-----------------------------------|--------:|----------:|
| L5_vol_adjusted_return             |      49 | 0.859649  |
| L3_liquidity_tier_relative_return  |       5 | 0.0877193 |
| L1_cross_sectional_relative_return |       2 | 0.0350877 |
| L0_raw_forward_return              |       1 | 0.0175439 |

## Raw Non-L7 Semantic Distribution

| semantic_pair                          |   count |    share |
|:---------------------------------------|--------:|---------:|
| basis_premium_like\|positioning_like   |     131 | 0.325871 |
| basis_premium_like\|volatility_like    |     120 | 0.298507 |
| basis_premium_like\|basis_premium_like |     103 | 0.256219 |
| basis_premium_like\|price_like         |      48 | 0.119403 |

## Internal Selected Semantic Distribution

| semantic_pair                          |   count |    share |
|:---------------------------------------|--------:|---------:|
| basis_premium_like\|basis_premium_like |      19 | 0.322034 |
| basis_premium_like\|positioning_like   |      19 | 0.322034 |
| basis_premium_like\|volatility_like    |      15 | 0.254237 |
| basis_premium_like\|price_like         |       6 | 0.101695 |

## Interpretation

The numeric surface is not L5-only. The internal A7FF-8 portfolio selector remains L5-heavy and must not be used as the final selector target for the next expansion.

## Boundary

- Uses May: `false`
- Executes generation: `false`
- Executes replay: `false`
- Executes search: `false`
- Authorizes alpha proof / shadow / paper / live: `false`
