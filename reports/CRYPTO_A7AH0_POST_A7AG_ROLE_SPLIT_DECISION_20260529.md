# CRYPTO A7AH-0 POST-A7AG ROLE SPLIT DECISION

Generated: 2026-05-29T08:56:57Z

## Decision

`PASS_A7AH0_POST_A7AG_ROLE_SPLIT_READY_FOR_A7AH1_A7AH2_CONTRACTS`

A7AH-0 freezes the A7AG result and splits ordinary alpha work from downside/risk-defense diagnostics. It does not generate formulas, replay, search, train, or authorize proof.

## Manifest

```json
{
  "authorizes_a7ah1_ordinary_alpha_objective_rewrite_contract": true,
  "authorizes_a7ah2_downside_risk_defense_forensic_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "concentration_blocker_count": 0,
  "decision": "PASS_A7AH0_POST_A7AG_ROLE_SPLIT_READY_FOR_A7AH1_A7AH2_CONTRACTS",
  "executes_formula_generation": false,
  "executes_replay": false,
  "executes_role_split_decision": true,
  "executes_search": false,
  "executes_training": false,
  "generated_at": "2026-05-29T08:56:57Z",
  "input_a7ag5_decision": "HOLD_A7AG5_NO_ORDINARY_LABEL_TRANSLATION",
  "ordinary_label_translation_clue_count": 0,
  "stage": "A7AH-0",
  "uses_may": false
}
```

## Evidence Summary

| metric                                | value                                                 |
|:--------------------------------------|:------------------------------------------------------|
| a7ag5_decision                        | HOLD_A7AG5_NO_ORDINARY_LABEL_TRANSLATION              |
| a7ag3_to_a7ag5_clues                  | 24                                                    |
| ordinary_label_translation_clue_count | 0                                                     |
| cost20_original_survivor_count        | 8                                                     |
| concentration_blocker_count           | 0                                                     |
| formula_generation_overconservative   | false; A7AG3 evaluated 96/96 and found 24 pilot clues |
| ordinary_alpha_status                 | HOLD                                                  |
| risk_defense_status                   | forensic_only                                         |

## Branch Decision Matrix

| branch_id                  | status           | evidence                                                                        | authorized_next                                                 | not_authorized                                                         |
|:---------------------------|:-----------------|:--------------------------------------------------------------------------------|:----------------------------------------------------------------|:-----------------------------------------------------------------------|
| B0_ordinary_alpha          | HOLD             | A7AG5 ordinary_label_translation_clue_count=0                                   | A7AH1_ordinary_alpha_objective_rewrite_contract_only            | formula_search_execution\|large_search\|alpha_proof\|shadow_paper_live |
| B1_vol_adjusted_diagnostic | DIAGNOSTIC_ONLY  | A7AG4 has L5 vol-adjusted diagnostic clues but A7AG5 shows no L0/L1 translation | A7AH1_may_reuse_as_objective_input_no; diagnostic evidence only | ordinary_alpha_promotion\|formula_search_execution\|alpha_proof        |
| B2_downside_risk_defense   | FORENSIC_ALLOWED | A7AG4 downside risk-defense clues=19; A7AG5 concentration_blockers=0            | A7AH2_downside_risk_defense_forensic_contract_only              | ordinary_alpha_promotion\|live_risk_overlay\|alpha_proof               |

## A7AH-1 Ordinary Alpha Contract Stub

```json
{
  "allowed_contract_work": [
    "define L0/L1-first selector objective",
    "require ordinary label response before formula expansion",
    "keep vol-adjusted/downside fields as diagnostics or controls only",
    "define bounded A7AH1 dry rerank on existing A7AG queue"
  ],
  "must_not_use": [
    "L5_vol_adjusted_return_as_primary_alpha_label",
    "L6_downside_avoidance_as_primary_alpha_label",
    "May",
    "formula_search_execution"
  ],
  "name": "ordinary alpha objective rewrite contract",
  "purpose": "rewrite ordinary alpha objective after A7AG5 showed no L0/L1 translation",
  "stage": "A7AH-1"
}
```

## A7AH-2 Risk Defense Contract Stub

```json
{
  "must_audit": [
    "cost_ladder_5_10_20bps",
    "crash_state_conditioning",
    "top_loss_hour_attribution",
    "symbol_month_latent_concentration",
    "negative_controls_by_downside_label",
    "tradeability_as_risk_overlay_only"
  ],
  "name": "downside risk-defense forensic contract",
  "not_authorized": [
    "ordinary_alpha_promotion",
    "live_risk_overlay",
    "alpha_proof"
  ],
  "purpose": "audit whether L6 downside clues represent a coherent risk-defense state, not ordinary alpha",
  "stage": "A7AH-2"
}
```

## Boundary

```text
A7AG did not fail because formulas were over-constrained: 96/96 evaluated and 24 pilot clues were found.
A7AG failed ordinary alpha promotion because no clue translated to L0/L1 ordinary labels.
Downside/risk-defense clues are separated from ordinary alpha evidence.
No formula search, large search, alpha proof, shadow, paper, or live is authorized.
```
