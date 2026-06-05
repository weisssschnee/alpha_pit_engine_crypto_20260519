# CRYPTO A7LS-0 CHECKPOINT LARGE SEARCH CONTRACT

Generated: 2026-06-05T01:58:27Z

## Decision

`PASS_A7LS0_CHECKPOINT_LARGE_SEARCH_CONTRACT_READY`

A7LS-0 defines a four-arm checkpoint-driven large search. One full route is reserved for raw multi-axis discovery, as a direct test of system usability beyond single-objective convergence.

## Core Change

The search is not a one-way basis/premium convergence. `A7LS_B raw_multi_axis_discovery` receives a full 25% budget share and is protected until at least 2,000 numeric rows unless controls dominate.

## Manifest

```json
{
  "arm_count": 4,
  "authorizes_a7ls1_blueprint_generation": true,
  "authorizes_a7ls2_materialization_wave": true,
  "authorizes_a7ls3_numeric_wave": true,
  "authorizes_alpha_proof": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7LS0_CHECKPOINT_LARGE_SEARCH_CONTRACT_READY",
  "executes_generation": false,
  "executes_materialization": false,
  "executes_numeric_probe": false,
  "executes_search": false,
  "generated_at": "2026-06-05T01:58:27Z",
  "raw_multi_axis_arm_id": "A7LS_B",
  "raw_multi_axis_generated_budget": 60000,
  "stage": "A7LS-0",
  "total_generated_budget": 240000,
  "total_materialization_budget": 40000,
  "total_numeric_budget": 8000
}
```

## Arm Budget Map

| arm_id   | arm_name                                | purpose                                                                                                      |   generated_budget |   materialization_budget |   numeric_budget |   priority | allowed_field_axes                                                                                                                                                | allowed_transform_depth        | checkpoint_policy   | search_role       |   generated_share |   numeric_share |
|:---------|:----------------------------------------|:-------------------------------------------------------------------------------------------------------------|-------------------:|-------------------------:|-----------------:|-----------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------|:--------------------|:------------------|------------------:|----------------:|
| A7LS_A   | basis_premium_price_vol_evidence_guided | Exploit the strongest current evidence from CORE65A: basis/premium with price and volatility transforms.     |              60000 |                    10000 |             2000 |          1 | basis_premium_like;price_like;volatility_like                                                                                                                     | typed_l1_l2_l3                 | normal              | evidence_guided   |              0.25 |            0.25 |
| A7LS_B   | raw_multi_axis_discovery                | Reserve one full route for raw multi-axis search to test system utility beyond hand-shaped objectives.       |              60000 |                    10000 |             2000 |          2 | price_like;basis_premium_like;funding_state_like;open_interest_like;positioning_like;taker_flow_like;liquidity_like;volatility_like;listing_age_like;regime_state | raw_or_simple_typed_l1_l2_only | strict_efficiency   | raw_discovery     |              0.25 |            0.25 |
| A7LS_C   | state_interaction_repair                | Use repaired state variables, especially funding_state_8h, OI/positioning/taker, as controlled interactions. |              60000 |                    10000 |             2000 |          3 | funding_state_like;open_interest_like;positioning_like;taker_flow_like;basis_premium_like;regime_state                                                            | typed_l1_l2_l3                 | normal              | state_interaction |              0.25 |            0.25 |
| A7LS_D   | control_and_selector_stress             | Keep a budgeted negative/control arm to detect selector self-deception and raw-axis false positives.         |              60000 |                    10000 |             2000 |          4 | placebo;wrong_lag;shuffle;sign_flip;same_family_control;low_prior_axes                                                                                            | control_only                   | control             | negative_control  |              0.25 |            0.25 |

## Raw Multi-Axis Policy

| axis               | raw_fields                                                                                                |   quota_share_within_raw_arm | notes                                                                  |
|:-------------------|:----------------------------------------------------------------------------------------------------------|-----------------------------:|:-----------------------------------------------------------------------|
| price_like         | trade_close;mark_close;index_close;trade_return_1h                                                        |                         0.12 | No single price axis may dominate raw arm.                             |
| basis_premium_like | mark_index_basis_bps;premium_close_bps                                                                    |                         0.14 | Allowed because strongest current evidence, but capped inside raw arm. |
| funding_state_like | funding_rate_state_last_ffill_8h;funding_event_age_hours                                                  |                         0.1  | Use repaired PIT state, not sparse raw funding_rate.                   |
| open_interest_like | open_interest_last;open_interest_mean;open_interest_value_last;open_interest_value_mean                   |                         0.12 | Raw OI axis gets real quota despite weak prior.                        |
| positioning_like   | global_long_short_account_ratio_last;top_long_short_account_ratio_last;top_long_short_position_ratio_last |                         0.1  | Positioning axis included to test independent information.             |
| taker_flow_like    | taker_buy_sell_volume_ratio_last;taker_buy_sell_volume_ratio_mean;kline_taker_buy_quote_share             |                         0.1  | Flow proxy axis.                                                       |
| liquidity_like     | quote_volume;trade_count;liquidity_rank_active_universe                                                   |                         0.1  | Must survive neutralization, not standalone liquidity beta.            |
| volatility_like    | realized_vol_24h;realized_vol_72h;realized_vol_168h                                                       |                         0.08 | Mostly interaction/state axis.                                         |
| listing_age_like   | listing_age_days;age_x_liquidity;age_x_volatility                                                         |                         0.07 | Allowed as lifecycle axis; not proof universe substitute.              |
| regime_state       | upper_regime_state;latent_state;liquidity_tier;major_meme_multiplier_tags                                 |                         0.07 | Conditioning and neutralization axis; direct signal use capped.        |

## Checkpoint Policy

```json
{
  "arm_survival_gates": {
    "activity_ok_rate_min": 0.5,
    "control_dominated_rate_max": 0.45,
    "l7_share_max": 0.6,
    "non_l7_clue_rate_min_after_1000": 0.003,
    "selected_queue_min_after_1000": 4,
    "top_semantic_pair_share_max": 0.4
  },
  "authorization_boundary": {
    "authorizes_alpha_proof": false,
    "authorizes_blueprint_generation": true,
    "authorizes_materialization_wave": true,
    "authorizes_numeric_wave": true,
    "authorizes_shadow_paper_live": false
  },
  "checkpoint_interval_numeric_rows": 1000,
  "early_checkpoint_interval_numeric_rows": 500,
  "expand_rules": [
    "non_l7_clue_rate >= 0.008 and selected_queue >= 8",
    "control_dominated_rate <= 0.25",
    "at least three semantic pairs or five raw axes active"
  ],
  "kill_rules": [
    "eval_failure_rate > 0.05",
    "activity_ok_rate < 0.35 after first checkpoint",
    "control_dominated_rate > 0.60 after first checkpoint",
    "non_l7_clue_rate == 0 and selected_queue == 0 after two checkpoints",
    "single semantic pair share > 0.55 after diversity repair"
  ],
  "raw_arm_special_rules": {
    "arm_id": "A7LS_B",
    "min_active_axes_after_checkpoint": 5,
    "must_keep_until_numeric_rows": 2000,
    "reason": "Raw multi-axis search is reserved to test system utility and should not be killed by first-checkpoint noise unless controls dominate.",
    "top_axis_share_max": 0.25
  },
  "stage": "A7LS-0",
  "total_generated_budget": 240000,
  "total_materialization_budget": 40000,
  "total_numeric_budget": 8000
}
```

## Boundary

```text
This contract authorizes A7LS-1/2/3 generation and checkpoint waves.
It does not authorize alpha proof, shadow, paper, live, May-informed selector score, or unbounded full grammar.
Raw multi-axis search is budgeted, not merely diagnostic, but remains checkpoint-governed.
```