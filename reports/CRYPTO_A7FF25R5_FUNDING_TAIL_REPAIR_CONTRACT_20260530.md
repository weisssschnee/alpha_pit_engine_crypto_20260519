# CRYPTO A7FF-25R5 FUNDING TAIL REPAIR CONTRACT

Generated: 2026-05-30T09:30:43Z

## Decision

`PASS_A7FF25R5_FUNDING_TAIL_REPAIR_CONTRACT_BUILT_NO_SEARCH_AUTH`

A7FF-25R5 converts the A7FF-25R4 no-activity funding tail failure into a repair contract. It does not generate formulas, run replay, execute search, or prove alpha.

## Experiment Record

```text
experiment_id: 20260530_a7ff25r5_funding_tail_repair_contract
objective: prevent raw sparse funding_rate wrappers from entering healthy company wave evidence
input: runtime/a7ff25r4_no_activity_tail_audit/*
parameters: no execution; contract-only
decision: funding state repair required before funding-like tail queue can count as healthy
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_funding_state_materialization_audit": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blocked_pattern_count": 2,
  "decision": "PASS_A7FF25R5_FUNDING_TAIL_REPAIR_CONTRACT_BUILT_NO_SEARCH_AUTH",
  "dense_funding_state_field_count": 5,
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T09:30:43Z",
  "prior_decision": "PASS_A7FF25R4_NO_ACTIVITY_TAIL_CAUSE_IDENTIFIED_REPAIR_REQUIRED",
  "prior_stage": "A7FF-25R4",
  "queue_policy_gate_count": 4,
  "stage": "A7FF-25R5"
}
```

## Prior Failure Summary

| failure_reason   |   rows |   finite_share_median |   finite_share_max |   nonzero_share_median |
|:-----------------|-------:|----------------------:|-------------------:|-----------------------:|
| low_finite_share |    800 |           0.000670305 |            0.13129 |               0.958106 |

## Tail Field Usage

| field                                |   tail_expression_count |
|:-------------------------------------|------------------------:|
| funding_rate                         |                     800 |
| index_close                          |                     482 |
| mark_close                           |                     324 |
| global_long_short_account_ratio_last |                       9 |
| global_long_short_account_ratio_mean |                       4 |

## Dense Funding-State Field Contract

| field_name                       | source_field                                        | feature_class           | definition                                                                             | pit_rule                                                                              | allowed_role                         | caveat                                                     |
|:---------------------------------|:----------------------------------------------------|:------------------------|:---------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------|:-------------------------------------|:-----------------------------------------------------------|
| funding_rate_state_last_ffill_8h | funding_rate                                        | dense_funding_state     | last observed funding_rate carried forward up to 8h; stale beyond 8h becomes NaN       | feature available at timestamp after source observation, then usable from next 1h bar | signal_candidate_or_regime           | must record age/staleness; no unlimited forward fill       |
| funding_rate_update_age_hours    | funding_rate                                        | funding_observation_age | hours since latest observed funding_rate for symbol                                    | computed only from past observations                                                  | neutralizer_or_regime                | not standalone alpha                                       |
| funding_rate_abs_state_168h_z    | funding_rate_state_last_ffill_8h                    | funding_crowding_state  | rolling 168h zscore of absolute dense funding state                                    | past rolling window only; min_period >= 48                                            | regime_or_interaction_seed           | direct alpha use requires response evidence                |
| funding_rate_delta_state_24h     | funding_rate_state_last_ffill_8h                    | funding_state_change    | 24h change in dense funding state                                                      | past 24h diff only                                                                    | signal_candidate_or_interaction_seed | must pass activity and control checks before company queue |
| funding_state_x_basis_delta      | funding_rate_delta_state_24h + mark_index_basis_bps | typed_interaction       | interaction between dense funding-state change and basis/premium dislocation transform | inherits max lag of both inputs                                                       | interaction_seed_only                | no funding-only wrapper promotion                          |

## Blocked Funding Patterns

| pattern                         | examples                                                                  | status                             | reason                                                                               |
|:--------------------------------|:--------------------------------------------------------------------------|:-----------------------------------|:-------------------------------------------------------------------------------------|
| raw funding_rate direct wrapper | Mean(funding_rate,*), Delta(funding_rate,*), ZScore(Mean(funding_rate,*)) | blocked_from_healthy_company_queue | A7FF-25R4 showed 800/800 tail blueprints fail low finite_share                       |
| funding_only_alpha_objective    | funding_rate as standalone signal family                                  | blocked                            | funding field is sparse/event-like and must be rebuilt as dense state or interaction |

## Queue Repair Policy

| gate                       | rule                                                                                                    | failure_action                                         |
|:---------------------------|:--------------------------------------------------------------------------------------------------------|:-------------------------------------------------------|
| dense_state_required       | funding-like formulas must use approved dense funding-state fields, not raw funding_rate                | reject from company wave queue                         |
| activity_precheck          | finite_share >= 0.20 and nonzero_share >= 0.01 on smoke panel before queue admission                    | quarantine and backfill with non-funding semantic pair |
| family_backfill            | replace shards 08-11 with activity-capable basis/price/volatility or rebuilt funding-state interactions | do not treat 2400-row queue as uniformly healthy       |
| response_evidence_required | dense funding-state fields need non-L7/control-clean response before promotion beyond diagnostic        | diagnostic_only                                        |

## Boundary

```text
Raw funding_rate is not removed from the data layer.
Raw funding_rate direct wrappers are blocked from healthy company-wave evidence until dense funding-state repair passes.
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
```
