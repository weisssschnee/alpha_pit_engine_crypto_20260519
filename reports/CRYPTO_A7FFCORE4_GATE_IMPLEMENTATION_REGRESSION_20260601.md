# CRYPTO A7FF-CORE4 GATE IMPLEMENTATION REGRESSION

Generated: 2026-05-31T17:56:46Z

## Decision

`PASS_A7FFCORE4_GATE_IMPLEMENTATION_REGRESSION_READY_FOR_CORE5`

A7FF-CORE4 adds a reusable FormulaGen subgraph gate implementation, quarantines legacy high-bypass generation scripts as non-active generation entrypoints, and runs allow/reject regression cases against CORE2 approved subgraphs. It does not execute formula generation, numeric evaluation, replay, or search.

## Manifest

```json
{
  "allowed_generation_entrypoints": 5,
  "audited_generation_scripts": 17,
  "authorizes_alpha_proof": false,
  "authorizes_core5": true,
  "authorizes_generation": false,
  "authorizes_numeric": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE4_GATE_IMPLEMENTATION_REGRESSION_READY_FOR_CORE5",
  "executes_generation": false,
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "gate_regression_case_count": 145,
  "gate_regression_failures": 0,
  "generated_at": "2026-05-31T17:56:46Z",
  "high_risk_unquarantined_entrypoints": 0,
  "next_allowed": "A7FF-CORE5 gate-native generation compatibility dryrun",
  "quarantined_legacy_generation_scripts": 12,
  "source_decision": "PASS_A7FFCORE3_FORMULAGEN_SUBGRAPH_GATE_READY_FOR_CORE4",
  "source_stage": "A7FF-CORE3",
  "stage": "A7FF-CORE4",
  "uses_may": false
}
```

## Entrypoint Route Summary

| entrypoint_route                     | core4_status                                  |   scripts |   generation_entrypoints_allowed |   rewrite_required |
|:-------------------------------------|:----------------------------------------------|----------:|---------------------------------:|-------------------:|
| quarantined_legacy_generation        | blocked_until_rewritten_against_subgraph_gate |        12 |                                0 |                 12 |
| contract_or_non_generation_reference | allowed_as_non_generation_reference           |         5 |                                5 |                  0 |

## Gate Regression Summary

| mode              | input_type   | expected_allowed   | actual_allowed   |   cases |
|:------------------|:-------------|:-------------------|:-----------------|--------:|
| ordinary_alpha    | expression   | True               | True             |      50 |
| ordinary_alpha    | subgraph_id  | True               | True             |      50 |
| diagnostic_repair | subgraph_id  | True               | True             |      20 |
| ordinary_alpha    | subgraph_id  | False              | False            |      20 |
| ordinary_alpha    | expression   | False              | False            |       5 |

## Quarantined Legacy Generation Scripts

| script_path                                                | bypass_risk   | core4_status                                  |   direct_expression_hit_count |   core2_reference_hit_count |
|:-----------------------------------------------------------|:--------------|:----------------------------------------------|------------------------------:|----------------------------:|
| scripts\crypto_a7ab3_seed_constrained_dry_generation.py    | high          | blocked_until_rewritten_against_subgraph_gate |                            80 |                           0 |
| scripts\crypto_a7al2k_derived_generator_smoke.py           | high          | blocked_until_rewritten_against_subgraph_gate |                            87 |                           0 |
| scripts\crypto_a7al2p1_selector_feature_generation.py      | high          | blocked_until_rewritten_against_subgraph_gate |                             6 |                           0 |
| scripts\crypto_a7al2q_local_oi_price_formula_search.py     | high          | blocked_until_rewritten_against_subgraph_gate |                            37 |                           0 |
| scripts\crypto_a7al2x3_family_balanced_dry_generation.py   | high          | blocked_until_rewritten_against_subgraph_gate |                            56 |                           0 |
| scripts\crypto_a7al2z1_broader_non_oi_dry_generation.py    | high          | blocked_until_rewritten_against_subgraph_gate |                            49 |                           0 |
| scripts\crypto_a7al2z7_response_guided_dry_generation.py   | high          | blocked_until_rewritten_against_subgraph_gate |                            36 |                           0 |
| scripts\crypto_a7ar1_formula_engine_adapter_smoke.py       | high          | blocked_until_rewritten_against_subgraph_gate |                             1 |                           0 |
| scripts\crypto_a7ff24r_dry_generation_plan.py              | high          | blocked_until_rewritten_against_subgraph_gate |                            33 |                           0 |
| scripts\crypto_a7ff33_family_diversified_dry_generation.py | high          | blocked_until_rewritten_against_subgraph_gate |                            28 |                           0 |
| scripts\crypto_a7ff51e_non_l5_heavy_generation.py          | high          | blocked_until_rewritten_against_subgraph_gate |                            23 |                           0 |
| scripts\crypto_a7ff55r3_repaired_atlas_dry_generation.py   | high          | blocked_until_rewritten_against_subgraph_gate |                            26 |                           0 |

## Boundary

```text
generation executed: false
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```

## Next

`A7FF-CORE5 gate-native generation compatibility dryrun` may build a new generation entrypoint that emits only CORE4-gated subgraph references. Legacy generation scripts remain quarantined until rewritten or retired.
