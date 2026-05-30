# CRYPTO A7FF-25R4 NO-ACTIVITY TAIL AUDIT

Generated: 2026-05-30T09:07:10Z

## Decision

`PASS_A7FF25R4_NO_ACTIVITY_TAIL_CAUSE_IDENTIFIED_REPAIR_REQUIRED`

A7FF-25R4 audits why A7FF-25R3 shards 08-11 had eval success but zero activity-ok blueprints. It does not generate, replay, search, or prove alpha.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_queue_repair": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7FF25R4_NO_ACTIVITY_TAIL_CAUSE_IDENTIFIED_REPAIR_REQUIRED",
  "executes_generation": false,
  "executes_numeric_probe": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T09:07:10Z",
  "no_activity_shards": [
    "08",
    "09",
    "10",
    "11"
  ],
  "prior_decision": "PASS_A7FF25R3_FULL_NUMERIC_WAVE_COMPLETED_WITH_WARNINGS_NO_SEARCH_AUTH",
  "prior_stage": "A7FF-25R3",
  "stage": "A7FF-25R4",
  "tail_blueprint_count": 800,
  "tail_funding_rate_expression_count": 800,
  "tail_low_finite_share_count": 800,
  "warnings": [
    "no_activity_tail_shards",
    "all_tail_failures_low_finite_share",
    "tail_all_uses_funding_rate"
  ]
}
```

## Failure Summary

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

## Tail Family/Motif Failures

|   shard | semantic_pair                   | motif               | failure_reason   |   count |
|--------:|:--------------------------------|:--------------------|:-----------------|--------:|
|      08 | basis_premium_like|funding_like | gated_sign          | low_finite_share |     114 |
|      08 | basis_premium_like|funding_like | mean_reversion_gate | low_finite_share |      86 |
|      09 | basis_premium_like|funding_like | mean_reversion_gate | low_finite_share |     170 |
|      09 | basis_premium_like|funding_like | mul                 | low_finite_share |      30 |
|      10 | basis_premium_like|funding_like | relative_shock      | low_finite_share |     168 |
|      10 | basis_premium_like|funding_like | mul                 | low_finite_share |      32 |
|      11 | basis_premium_like|funding_like | relative_shock      | low_finite_share |     146 |
|      11 | basis_premium_like|funding_like | safe_div_abs        | low_finite_share |      22 |
|      11 | basis_premium_like|funding_like | signed_spread       | low_finite_share |      19 |
|      11 | funding_like|positioning_like   | gated_sign          | low_finite_share |      13 |

## Repair Policy

| policy_id                     | applies_to                                    | action                                                                                                               | reason                                                                            |
|:------------------------------|:----------------------------------------------|:---------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------|
| funding_raw_sparse_quarantine | raw funding_rate expressions in company queue | do_not_count_as_healthy_company_queue_until dense funding-state transforms exist                                     | eval_success but low finite_share caused all activity_ok=0 in shards 08-11        |
| funding_state_rebuild         | funding_like semantic family                  | replace raw funding_rate wrappers with settlement-aware or forward-filled funding state features before numeric wave | sparse event-style funding field is not suitable as a direct dense 1h alpha field |
| queue_tail_backfill           | A7FF company queue                            | backfill shards 08-11 with activity-capable semantic pairs before full replay authorization                          | 2400-row queue contains 800 rows that materialize to no activity                  |

## Boundary

```text
No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.
Funding-like raw sparse expressions are not deleted; they are quarantined from healthy company-wave evidence until rebuilt as dense funding-state features.
```
