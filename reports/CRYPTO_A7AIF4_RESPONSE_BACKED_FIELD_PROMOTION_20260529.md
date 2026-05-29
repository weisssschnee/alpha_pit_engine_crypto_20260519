# CRYPTO A7AI-F4 RESPONSE-BACKED FIELD PROMOTION

Generated: 2026-05-29T14:39:14Z

## Decision

`PASS_A7AIF4_ORDINARY_ALPHA_SEEDS_FOUND`

A7AI-F4 promotes fields only when non-L7 primitive response evidence is control-clean, lag-surviving, materialized, and ordinary-alpha contract clean.

## Manifest

```json
{
  "active_non_l7_labels": [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return"
  ],
  "authorizes_a7pool0": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AIF4_ORDINARY_ALPHA_SEEDS_FOUND",
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-29T14:39:14Z",
  "promoted_evidence_rows": 2,
  "promoted_field_count": 1,
  "promotion_audit_rows": 11,
  "response_candidate_rows": 11,
  "stage": "A7AI-F4",
  "uses_may": false
}
```

## Promoted Ordinary-Alpha Fields

| field_name           | field_family   | source_family      | feature_class   | transform   | label_family                       |   label_horizon_h |   control_ratio_premay_max | lag_ok   | premay_all_positive   | resolution   | semantic_role             | enforcement_status   | promotion_decision          |
|:---------------------|:---------------|:-------------------|:----------------|:------------|:-----------------------------------|------------------:|---------------------------:|:---------|:----------------------|:-------------|:--------------------------|:---------------------|:----------------------------|
| mark_index_basis_bps | basis_premium  | mark_index_premium | raw_source      | delta_24h   | L0_raw_forward_return              |                 1 |                   0.785786 | True     | True                  | resolved     | ordinary_signal_candidate | OK_ORDINARY_ALPHA    | PROMOTE_ORDINARY_ALPHA_SEED |
| mark_index_basis_bps | basis_premium  | mark_index_premium | raw_source      | delta_24h   | L1_cross_sectional_relative_return |                 1 |                   0.785786 | True     | True                  | resolved     | ordinary_signal_candidate | OK_ORDINARY_ALPHA    | PROMOTE_ORDINARY_ALPHA_SEED |

## Blocked Response Candidates

| field_name        | field_family   | source_family       | feature_class   | transform   | label_family            |   label_horizon_h |   control_ratio_premay_max | lag_ok   | premay_all_positive   | resolution   | semantic_role                         | enforcement_status      | promotion_decision   |
|:------------------|:---------------|:--------------------|:----------------|:------------|:------------------------|------------------:|---------------------------:|:---------|:----------------------|:-------------|:--------------------------------------|:------------------------|:---------------------|
| trade_return_1h   | price_return   | derived_replay_base | derived_rolling | level       | L7_ranked_future_return |                 1 |                   0.254317 | True     | True                  | resolved     | diagnostic_rank_or_nonordinary_signal | OK_DIAGNOSTIC_OR_REGIME | HOLD_L7_ONLY         |
| trade_return_1h   | price_return   | derived_replay_base | derived_rolling | level       | L7_ranked_future_return |                 4 |                   0.267545 | True     | True                  | resolved     | diagnostic_rank_or_nonordinary_signal | OK_DIAGNOSTIC_OR_REGIME | HOLD_L7_ONLY         |
| trade_return_1h   | price_return   | derived_replay_base | derived_rolling | cs_rank     | L7_ranked_future_return |                 1 |                   0.254317 | True     | True                  | resolved     | diagnostic_rank_or_nonordinary_signal | OK_DIAGNOSTIC_OR_REGIME | HOLD_L7_ONLY         |
| trade_return_1h   | price_return   | derived_replay_base | derived_rolling | cs_rank     | L7_ranked_future_return |                 4 |                   0.267545 | True     | True                  | resolved     | diagnostic_rank_or_nonordinary_signal | OK_DIAGNOSTIC_OR_REGIME | HOLD_L7_ONLY         |
| realized_vol_24h  | volatility     | trade_ohlcv         | derived_rolling | level       | L7_ranked_future_return |                 1 |                   0.939508 | True     | True                  | resolved     | diagnostic_rank_or_nonordinary_signal | OK_DIAGNOSTIC_OR_REGIME | HOLD_L7_ONLY         |
| realized_vol_24h  | volatility     | trade_ohlcv         | derived_rolling | cs_rank     | L7_ranked_future_return |                 1 |                   0.939508 | True     | True                  | resolved     | diagnostic_rank_or_nonordinary_signal | OK_DIAGNOSTIC_OR_REGIME | HOLD_L7_ONLY         |
| realized_vol_168h | volatility     | trade_ohlcv         | derived_rolling | level       | L7_ranked_future_return |                 1 |                   0.879498 | True     | True                  | resolved     | diagnostic_rank_or_nonordinary_signal | OK_DIAGNOSTIC_OR_REGIME | HOLD_L7_ONLY         |
| realized_vol_168h | volatility     | trade_ohlcv         | derived_rolling | cs_rank     | L7_ranked_future_return |                 1 |                   0.879498 | True     | True                  | resolved     | diagnostic_rank_or_nonordinary_signal | OK_DIAGNOSTIC_OR_REGIME | HOLD_L7_ONLY         |
| premium_close_bps | basis_premium  | derived_replay_base | derived_rolling | delta_24h   | L7_ranked_future_return |                 1 |                   0.791438 | True     | True                  | resolved     | diagnostic_rank_or_nonordinary_signal | OK_DIAGNOSTIC_OR_REGIME | HOLD_L7_ONLY         |

## Boundary

```text
A7AI-F4 does not generate formulas, replay candidates, or authorize alpha proof.
Risk-defense and diagnostic-only fields are not promoted as standalone ordinary-alpha seeds.
L7 ranked-return-only evidence is insufficient for ordinary-alpha promotion.
```
