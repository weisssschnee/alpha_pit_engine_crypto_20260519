# CRYPTO A7LS-14X AUTHORIZATION ARBITRATION

Generated: 2026-06-06T03:30:45Z

## Decision

`PASS_A7LS14X_CHECKPOINT_LARGE_SEARCH_AUTHORIZATION_ARBITRATED`

## Arbitration Result

A7LS-14X resolves the source-of-truth conflict between older global `large_search = not authorized` records and the newer A7LS-14 scaled multi-axis search contract.

The resolution is scoped: large search is authorized only for the checkpointed A7LS14 pipeline, namely A7LS15 blueprint generation, A7LS16 preflight, A7LS17 company materialization, and A7LS18 company numeric wave.

This arbitration does not authorize alpha proof, shadow, paper, live, May-informed selector/reward use, unbounded grammar, or any legacy large-search path outside A7LS14.

## Allowed Scope

| scope_id   | scope                                         | authorized   | heavy_compute   | limit                                                                            | checkpoint_required   |
|:-----------|:----------------------------------------------|:-------------|:----------------|:---------------------------------------------------------------------------------|:----------------------|
| A7LS15     | million_scale_multi_axis_blueprint_generation | True         | False           | generated_total <= 1,000,000                                                     | True                  |
| A7LS16     | local_preflight_and_materialization_smoke     | True         | False           | local_light_preflight_rows = 512                                                 | True                  |
| A7LS17     | company_sharded_materialization               | True         | True            | materialization_total <= 100,000                                                 | True                  |
| A7LS18     | company_sharded_numeric_wave                  | True         | True            | numeric_total <= 25,000; shards = 256; parallel = 3 default / 4 if memory allows | True                  |
| A7LS19     | checkpoint_arbitration_and_lane_resize        | True         | False           | continue / kill / expand decisions only                                          | True                  |

## Forbidden Scope

| scope                              | authorized   | reason                                                               |
|:-----------------------------------|:-------------|:---------------------------------------------------------------------|
| alpha_proof                        | False        | A7LS14 is search infrastructure, not proof                           |
| shadow_paper_live                  | False        | no production or trading authorization                               |
| May_in_selector_or_reward          | False        | May remains stress/failure attribution only                          |
| unbounded_full_grammar             | False        | search is bounded by typed lanes and quota policy                    |
| single_lane_budget_capture         | False        | axis quota and checkpoint policy required                            |
| legacy_large_search_outside_A7LS14 | False        | old A7AL/A7FF large-search denials remain valid outside A7LS14 scope |

## Supersession

| superseded_rule                    | superseded_by      | replacement                                                                           | still_forbidden_outside_scope   |
|:-----------------------------------|:-------------------|:--------------------------------------------------------------------------------------|:--------------------------------|
| global_large_search_not_authorized | A7LS-14X           | large search authorized only inside A7LS14 checkpointed multi-axis A7LS15-A7LS18 path | True                            |
| A7LS13_no_search_auth              | A7LS-14 / A7LS-14X | A7LS13 packet promoted to A7LS14 seed map and scoped large-search contract            | True                            |

## Authorization

```json
{
  "authorizes_a7ls15_generation": true,
  "authorizes_a7ls16_local_preflight": true,
  "authorizes_a7ls17_company_materialization": true,
  "authorizes_a7ls18_company_numeric": true,
  "authorizes_alpha_proof": false,
  "authorizes_large_search": true,
  "authorizes_scoped_large_search": true,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7LS14X_CHECKPOINT_LARGE_SEARCH_AUTHORIZATION_ARBITRATED",
  "does_not_supersede_alpha_proof_block": true,
  "does_not_supersede_shadow_paper_live_block": true,
  "scope_boundary": "A7LS14 checkpointed multi-axis pipeline only",
  "stage": "A7LS-14X",
  "supersedes_global_large_search_block": true
}
```
