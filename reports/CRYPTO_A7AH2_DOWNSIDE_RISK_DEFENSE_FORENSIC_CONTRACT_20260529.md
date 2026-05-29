# CRYPTO A7AH-2 DOWNSIDE RISK-DEFENSE FORENSIC CONTRACT

Generated: 2026-05-29T08:59:34Z

## Decision

`PASS_A7AH2_DOWNSIDE_RISK_DEFENSE_FORENSIC_CONTRACT_READY_FOR_A7AH2F`

A7AH-2 defines forensic work for downside/risk-defense clues. It does not promote them to ordinary alpha and does not execute search or replay.

## Manifest

```json
{
  "authorizes_a7ah2f_downside_forensic_audit": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AH2_DOWNSIDE_RISK_DEFENSE_FORENSIC_CONTRACT_READY_FOR_A7AH2F",
  "downside_clue_count": 19,
  "downside_seed_pair_count": 16,
  "executes_contract_only": true,
  "executes_formula_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T08:59:34Z",
  "input_a7ah0_decision": "PASS_A7AH0_POST_A7AG_ROLE_SPLIT_READY_FOR_A7AH1_A7AH2_CONTRACTS",
  "stage": "A7AH-2",
  "uses_may": false
}
```

## Audit Plan

| audit_id                      | purpose                                                                                  | required_outputs                                                     | pass_signal                                                                   |
|:------------------------------|:-----------------------------------------------------------------------------------------|:---------------------------------------------------------------------|:------------------------------------------------------------------------------|
| D0_cost_ladder                | separate 5bps pilot clues from 10/20bps robust risk-defense clues                        | cost5\|cost10\|cost20 survivor counts by candidate                   | risk-defense candidate survives >=10bps diagnostic and reports 20bps status   |
| D1_crash_state_conditioning   | test whether downside clue is state-conditional rather than universal short-vol exposure | performance by drawdown/breadth/volatility state                     | benefit concentrated in adverse states without normal-state damage dominating |
| D2_loss_hour_attribution      | detect whether signal only avoids a few known loss hours                                 | top gain/loss hour contribution and leave-one-month-out contribution | no single hour/month dominates                                                |
| D3_negative_controls_downside | ensure downside label is not trivially easier for wrong-lag/shuffle controls             | matched controls by candidate and split                              | control ratio < 1 in all pre-May splits                                       |
| D4_overlay_boundary           | prevent risk-defense clue from being promoted as ordinary alpha or live overlay          | allowed/not-allowed use matrix                                       | only forensic/risk-defense research remains authorized                        |

## Downside Seed Pair Summary

| seed_field                           | interaction_field                    |   clue_count |   skeleton_count |   median_control_ratio |   cost10_survivors |   cost20_survivors |
|:-------------------------------------|:-------------------------------------|-------------:|-----------------:|-----------------------:|-------------------:|-------------------:|
| top_long_short_account_ratio_last    | realized_vol_24h                     |            2 |                2 |               0.668744 |                  1 |                  1 |
| top_long_short_account_ratio_last    | oi_x_price_move_24h                  |            2 |                2 |               0.64606  |                  1 |                  0 |
| top_long_short_account_ratio_last    | open_interest_last                   |            2 |                2 |               0.397388 |                  1 |                  0 |
| realized_vol_24h                     | oi_x_price_move_24h                  |            1 |                1 |               0.808366 |                  1 |                  1 |
| realized_vol_24h                     | open_interest_last                   |            1 |                1 |               0.918219 |                  1 |                  1 |
| global_long_short_account_ratio_last | oi_x_price_move_24h                  |            1 |                1 |               0.428842 |                  0 |                  0 |
| global_long_short_account_ratio_last | open_interest_last                   |            1 |                1 |               0.804676 |                  0 |                  0 |
| global_long_short_account_ratio_last | realized_vol_24h                     |            1 |                1 |               0.731564 |                  0 |                  0 |
| global_long_short_account_ratio_last | top_long_short_account_ratio_last    |            1 |                1 |               0.616851 |                  0 |                  0 |
| oi_x_price_move_24h                  | global_long_short_account_ratio_last |            1 |                1 |               0.777268 |                  1 |                  0 |
| oi_x_price_move_24h                  | realized_vol_24h                     |            1 |                1 |               0.817623 |                  1 |                  0 |
| oi_x_price_move_24h                  | top_long_short_account_ratio_last    |            1 |                1 |               0.816487 |                  1 |                  0 |
| oi_x_price_move_24h                  | trade_count                          |            1 |                1 |               0.92351  |                  0 |                  0 |
| top_long_short_account_ratio_last    | global_long_short_account_ratio_last |            1 |                1 |               0.409366 |                  0 |                  0 |
| trade_count                          | global_long_short_account_ratio_last |            1 |                1 |               0.876265 |                  0 |                  0 |
| trade_count                          | oi_x_price_move_24h                  |            1 |                1 |               0.913005 |                  0 |                  0 |

## Promotion Boundary

```json
{
  "allowed": [
    "forensic audit",
    "risk-defense clue classification",
    "state-conditioned diagnostic"
  ],
  "not_allowed": [
    "ordinary alpha evidence",
    "standalone alpha proof",
    "shadow/paper/live overlay",
    "large search seed without A7AH2F pass"
  ],
  "required_before_any_risk_overlay_research": [
    "cost ladder pass",
    "state-conditioned downside benefit",
    "negative controls clean",
    "loss-hour/month concentration clean",
    "explicit ordinary alpha separation"
  ]
}
```

## Boundary

```text
A7AH-2 is risk-defense forensic only.
It does not authorize ordinary alpha promotion, live overlay, alpha proof, or formula search.
```
