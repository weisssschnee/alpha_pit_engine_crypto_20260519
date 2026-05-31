# CRYPTO A7FF-CORE3 FORMULAGEN SUBGRAPH GATE

Generated: 2026-05-31T17:41:30Z

## Decision

`PASS_A7FFCORE3_FORMULAGEN_SUBGRAPH_GATE_READY_FOR_CORE4`

A7FF-CORE3 defines the FormulaGen subgraph gate from the CORE2 reusable subgraph registry and audits legacy generation scripts for bypass risk. It does not execute formula generation, numeric evaluation, replay, or search.

## Manifest

```json
{
  "approved_reusable_subgraph_count": 2820,
  "authorizes_alpha_proof": false,
  "authorizes_core4": true,
  "authorizes_generation": false,
  "authorizes_numeric": false,
  "authorizes_replay": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blocked_or_unknown_subgraph_count": 0,
  "blockers": [],
  "decision": "PASS_A7FFCORE3_FORMULAGEN_SUBGRAPH_GATE_READY_FOR_CORE4",
  "diagnostic_root_count": 9240,
  "executes_generation": false,
  "executes_numeric": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-31T17:41:30Z",
  "generation_script_count": 17,
  "high_bypass_risk_script_count": 12,
  "low_bypass_risk_script_count": 5,
  "medium_bypass_risk_script_count": 0,
  "next_allowed": "A7FF-CORE4 FormulaGen gate implementation regression",
  "registry_subgraph_count": 12064,
  "source_decision": "PASS_A7FFCORE2_FEATURE_SUBGRAPH_REGISTRY_READY_FOR_CORE3",
  "source_stage": "A7FF-CORE2",
  "stage": "A7FF-CORE3",
  "uses_may": false
}
```

## Gate Matrix

| gate                         |   count | status                      | authorizes_generation   |
|:-----------------------------|--------:|:----------------------------|:------------------------|
| approved_reusable_subgraphs  |    2820 | allowed_for_feature_factory | False                   |
| diagnostic_roots             |    9240 | diagnostic_or_repair_only   | False                   |
| blocked_or_unknown_subgraphs |       0 | fail_closed                 | False                   |

## Bypass Summary

| bypass_risk   | gate_status                |   script_count |
|:--------------|:---------------------------|---------------:|
| high          | needs_core4_wiring         |             12 |
| low           | no_obvious_generation_path |              5 |

## High-Risk Generation Scripts

| script_path                                                | executes_generation_marker   |   direct_expression_hit_count |   core2_reference_hit_count | gate_status        |
|:-----------------------------------------------------------|:-----------------------------|------------------------------:|----------------------------:|:-------------------|
| scripts\crypto_a7ab3_seed_constrained_dry_generation.py    | True                         |                            80 |                           0 | needs_core4_wiring |
| scripts\crypto_a7al2k_derived_generator_smoke.py           | True                         |                            87 |                           0 | needs_core4_wiring |
| scripts\crypto_a7al2p1_selector_feature_generation.py      | False                        |                             6 |                           0 | needs_core4_wiring |
| scripts\crypto_a7al2q_local_oi_price_formula_search.py     | False                        |                            37 |                           0 | needs_core4_wiring |
| scripts\crypto_a7al2x3_family_balanced_dry_generation.py   | True                         |                            56 |                           0 | needs_core4_wiring |
| scripts\crypto_a7al2z1_broader_non_oi_dry_generation.py    | False                        |                            49 |                           0 | needs_core4_wiring |
| scripts\crypto_a7al2z7_response_guided_dry_generation.py   | False                        |                            36 |                           0 | needs_core4_wiring |
| scripts\crypto_a7ar1_formula_engine_adapter_smoke.py       | False                        |                             1 |                           0 | needs_core4_wiring |
| scripts\crypto_a7ff24r_dry_generation_plan.py              | False                        |                            33 |                           0 | needs_core4_wiring |
| scripts\crypto_a7ff33_family_diversified_dry_generation.py | True                         |                            28 |                           0 | needs_core4_wiring |
| scripts\crypto_a7ff51e_non_l5_heavy_generation.py          | True                         |                            23 |                           0 | needs_core4_wiring |
| scripts\crypto_a7ff55r3_repaired_atlas_dry_generation.py   | True                         |                            26 |                           0 | needs_core4_wiring |

## Policy Boundary

```text
generation executed: false
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```

## Next

`A7FF-CORE4 FormulaGen gate implementation regression` should wire the gate into active generation entrypoints or explicitly quarantine legacy generation scripts. CORE3 itself only creates the source-of-truth policy and bypass audit.
