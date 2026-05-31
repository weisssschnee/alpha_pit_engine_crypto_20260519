# CRYPTO A7FF-55 SELECTOR REPAIR CONTRACT

Generated: 2026-05-31T08:32:22Z

## Decision

`PASS_A7FF55_SELECTOR_REPAIR_CONTRACT_READY_NO_EXECUTION_AUTH`

A7FF-55 converts the A7FF-54 selected-queue failure into a selector repair contract. It does not execute selector repair, replay, search, alpha proof, shadow, paper, or live trading.

## Current Failure Snapshot

```json
{
  "a7ff54_blockers": [
    "selected_queue_has_no_L0_L1_L3_primary_label_rows",
    "selected_non_l7_rows_are_L5_only",
    "selected_top_motif_share_above_0p35"
  ],
  "a7ff54_decision": "HOLD_A7FF54_SELECTED_QUEUE_LABEL_REPAIR_REQUIRED_NO_REPLAY_AUTH",
  "selected_l5_count": 51,
  "selected_non_l7_count": 51,
  "selected_primary_L0_L1_L3_count": 0,
  "top_selected_family_share": 0.16216216216216217,
  "top_selected_motif_share": 0.44594594594594594
}
```

## Label Quota Policy

| label_family                       | role            |   min_selected_rows |   max_selected_share | selection_rule                                             |
|:-----------------------------------|:----------------|--------------------:|---------------------:|:-----------------------------------------------------------|
| L0_raw_forward_return              | primary         |                   4 |                 0.35 | must compete before L5/L7 rows; cannot be backfilled by L5 |
| L1_cross_sectional_relative_return | primary         |                   4 |                 0.35 | must compete before L5/L7 rows; cannot be backfilled by L5 |
| L3_liquidity_tier_relative_return  | primary         |                   4 |                 0.35 | must compete before L5/L7 rows; cannot be backfilled by L5 |
| L5_vol_adjusted_return             | secondary       |                   0 |                 0.35 | allowed only after primary-label quota is met              |
| L7_ranked_future_return            | diagnostic_only |                   0 |                 0.25 | never promotes replay; diagnostic coverage only            |

## Family / Motif Cap Policy

| cap                           |   limit | action                       |
|:------------------------------|--------:|:-----------------------------|
| top_semantic_pair_share       |    0.3  | downrank_or_reject_after_cap |
| top_motif_share               |    0.3  | downrank_or_reject_after_cap |
| top_label_family_share        |    0.35 | downrank_or_reject_after_cap |
| L5_share_without_primary_rows |    0    | reject_queue                 |
| L7_replay_promotion_share     |    0    | diagnostic_only              |

## Required Inputs For Future Execution

| artifact                         | required_columns                                                                    | status                                 | reason                                                                                                                                              |
|:---------------------------------|:------------------------------------------------------------------------------------|:---------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------|
| A7FF-53E label response metrics  | blueprint_id,label_family,label_horizon_h,semantic_pair,motif,decision,score_no_may | required_for_selector_repair_execution | A7FF-54 compact selected queue lacks primary-label candidates; rerank must start from full response rows or a compact clue table with L0/L1/L3 rows |
| A7FF-53E control metrics         | blueprint_id,label_family,label_horizon_h,control_ratio_premay_max,decision         | required_for_selector_repair_execution | selector cannot select control-dominated rows                                                                                                       |
| A7FF-53E materialization metrics | blueprint_id,semantic_pair,motif,finite_share,nonzero_share,activity_ok             | required_for_selector_repair_execution | low-activity and diagnostic-only families must be excluded from primary replay queue                                                                |

## Current Selected Label Distribution

| label_family            |   selected_count |
|:------------------------|-----------------:|
| L5_vol_adjusted_return  |               51 |
| L7_ranked_future_return |               97 |

## Current Selected Family / Label Distribution

| semantic_pair                        | label_family            |   selected_count |
|:-------------------------------------|:------------------------|-----------------:|
| basis_premium_like|price_return_like | L5_vol_adjusted_return  |               20 |
| basis_premium_like|price_return_like | L7_ranked_future_return |                4 |
| liquidity_like|price_return_like     | L5_vol_adjusted_return  |                3 |
| liquidity_like|price_return_like     | L7_ranked_future_return |               20 |
| open_interest_like|price_return_like | L7_ranked_future_return |               20 |
| positioning_like|price_return_like   | L5_vol_adjusted_return  |                5 |
| positioning_like|price_return_like   | L7_ranked_future_return |               19 |
| regime_state|price_return_like       | L5_vol_adjusted_return  |               20 |
| regime_state|price_return_like       | L7_ranked_future_return |                4 |
| taker_flow_like|basis_premium_like   | L7_ranked_future_return |               11 |
| volatility_like|basis_premium_like   | L5_vol_adjusted_return  |                3 |
| volatility_like|basis_premium_like   | L7_ranked_future_return |               19 |

## Current Selected Motif Distribution

| motif               |   selected_count |
|:--------------------|-----------------:|
| spread_rank         |               66 |
| safe_div_abs        |               25 |
| sub                 |               23 |
| signed_spread       |               20 |
| mean_reversion_gate |                8 |
| relative_shock      |                6 |

## Selector Policy

```json
{
  "authorizes_execution": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "hard_reject": [
    "label_family == L7_ranked_future_return for replay promotion",
    "diagnostic_only_low_activity family as primary replay row",
    "control_ratio >= 0.80",
    "decision not in NUMERIC_CLUE for non-L7 rows",
    "missing primary label quota",
    "top motif share > 0.30",
    "top semantic pair share > 0.30"
  ],
  "purpose": "repair selector target before any replay preflight",
  "score_inputs_allowed": [
    "non_l7_primary_label_indicator",
    "control_margin",
    "premay_split_stability",
    "one_bar_lag_survival",
    "nonoverlap_robustness",
    "cost_proxy_survival",
    "family_diversity_bonus",
    "motif_diversity_bonus"
  ],
  "score_inputs_forbidden": [
    "May pass/fail",
    "May return",
    "L7 ranked label as primary proof",
    "raw score without control margin",
    "stale selected queue from A7FF-54"
  ],
  "source": "A7FF-54",
  "stage": "A7FF-55",
  "target_queue": {
    "L5_allowed_only_after_primary_quota": true,
    "L7_diagnostic_only": true,
    "motif_min_count": 4,
    "primary_label_families_present": [
      "L0_raw_forward_return",
      "L1_cross_sectional_relative_return",
      "L3_liquidity_tier_relative_return"
    ],
    "primary_label_min_rows_total": 12,
    "selected_rows": "32 to 64",
    "semantic_pair_min_count": 4
  }
}
```

## Boundary

```text
selector repair executed: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
