# CRYPTO A7FF-CORE58 FAILURE-AWARE QUEUE REBUILD

Generated: 2026-06-04T12:37:49Z

## Decision

`PASS_A7FFCORE58_FAILURE_AWARE_QUEUE_REBUILT_READY_FOR_CORE59`

CORE58 rebuilds numeric/materialization queues from the A7FF version index using CORE56/57 failure evidence. It does not execute replay or search.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core59_numeric_repair_execution": true,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE58_FAILURE_AWARE_QUEUE_REBUILT_READY_FOR_CORE59",
  "eligible_rows": 20485,
  "executes_replay": false,
  "executes_search": false,
  "failed_motif_count_from_core57": 8,
  "failed_semantic_pair_count_from_core57": 9,
  "formula_index_rows": 20599,
  "generated_at": "2026-06-04T12:37:49Z",
  "materialization_repair_queue_rows": 1200,
  "materialization_semantic_pair_count": 9,
  "materialization_top_semantic_share": 0.28,
  "numeric_queue_rows": 1200,
  "numeric_semantic_pair_count": 10,
  "numeric_top_semantic_share": 0.3,
  "source_decision": "PASS_A7FFCORE57_FAILURE_DECOMPOSITION_BUILT",
  "source_stage": "A7FF-CORE57",
  "stage": "A7FF-CORE58",
  "uses_may": false
}
```

## Coverage By Semantic Pair

| core58_queue           | semantic_pair                         |   row_count |   formula_count |   median_score |   max_score |
|:-----------------------|:--------------------------------------|------------:|----------------:|---------------:|------------:|
| numeric_replay_repair  | basis_premium_like|funding_like       |         360 |             360 |             99 |          99 |
| materialization_repair | basis_premium_like|funding_like       |         336 |             336 |             85 |          99 |
| materialization_repair | funding_like|positioning_like         |         336 |             336 |            117 |         117 |
| numeric_replay_repair  | basis_premium_like|price_like         |         282 |             282 |             -4 |          -4 |
| numeric_replay_repair  | basis_premium_like|volatility_like    |         213 |             213 |            -19 |          -4 |
| numeric_replay_repair  | basis_premium_like|basis_premium_like |         200 |             200 |             -4 |          -4 |
| materialization_repair | basis_premium_like|positioning_like   |         194 |             194 |              6 |           6 |
| materialization_repair | volatility_like|volatility_like       |         185 |             185 |             41 |          56 |
| materialization_repair | basis_premium_like|liquidity_like     |          62 |              62 |             43 |          58 |
| numeric_replay_repair  | price_like|volatility_like            |          51 |              51 |            -19 |          -4 |
| numeric_replay_repair  | basis_premium_like                    |          38 |              38 |            -13 |           2 |
| materialization_repair | basis_premium_like|volatility_like    |          27 |              27 |             -4 |          -4 |
| numeric_replay_repair  | volatility_like|volatility_like       |          26 |              26 |             56 |          56 |
| materialization_repair | basis_premium_like|generic_numeric    |          24 |              24 |             33 |          48 |
| materialization_repair | basis_premium_like|state_or_taxonomy  |          18 |              18 |             41 |          56 |
| materialization_repair | price_like|volatility_like            |          18 |              18 |             -4 |          -4 |
| numeric_replay_repair  | volatility_like                       |          14 |              14 |            -13 |         -13 |
| numeric_replay_repair  | funding_like|positioning_like         |          13 |              13 |            103 |         103 |
| numeric_replay_repair  | price_like                            |           3 |               3 |            -13 |         -13 |

## Coverage By Motif

| core58_queue           | motif               |   row_count |   formula_count |   median_score |   max_score |
|:-----------------------|:--------------------|------------:|----------------:|---------------:|------------:|
| materialization_repair | mean_reversion_gate |         216 |             216 |            117 |         117 |
| materialization_repair | relative_shock      |         216 |             216 |            117 |         117 |
| materialization_repair | signed_spread       |         216 |             216 |              6 |          85 |
| materialization_repair | smooth_mul          |         216 |             216 |             56 |          85 |
| numeric_replay_repair  | relative_shock      |         216 |             216 |             99 |          99 |
| numeric_replay_repair  | smooth_mul          |         216 |             216 |             -4 |          56 |
| numeric_replay_repair  | spread_rank         |         216 |             216 |            -19 |          56 |
| numeric_replay_repair  | mean_reversion_gate |         144 |             144 |             99 |          99 |
| numeric_replay_repair  | gated_sign          |         122 |             122 |            -19 |         103 |
| numeric_replay_repair  | mul                 |         117 |             117 |            -19 |          41 |
| materialization_repair | spread_rank         |         110 |             110 |             41 |          85 |
| materialization_repair | safe_div_abs        |          79 |              79 |             41 |          85 |
| numeric_replay_repair  | sub                 |          67 |              67 |            -19 |          41 |
| materialization_repair | sub                 |          55 |              55 |             41 |          85 |
| numeric_replay_repair  | single              |          55 |              55 |            -13 |           2 |
| materialization_repair | gated_sign          |          48 |              48 |             41 |          85 |
| numeric_replay_repair  | safe_div_abs        |          47 |              47 |            -19 |          41 |
| materialization_repair | mul                 |          44 |              44 |             41 |          43 |

## Coverage By Role

| core58_queue           | candidate_role           |   row_count |   formula_count |   median_score |   max_score |
|:-----------------------|:-------------------------|------------:|----------------:|---------------:|------------:|
| materialization_repair | role_mixed_allowed       |        1200 |            1200 |             85 |         117 |
| numeric_replay_repair  | role_mixed_allowed       |        1145 |            1145 |             -4 |         103 |
| numeric_replay_repair  | ordinary_alpha_valid     |          31 |              31 |            -13 |           2 |
| numeric_replay_repair  | exploratory_signal_probe |          24 |              24 |            -13 |         -13 |

## Exclusion / Penalty Summary

| exclusion_or_penalty_flag      |   row_count |
|:-------------------------------|------------:|
| core58_exact_core56_blueprint  |         114 |
| core58_exact_core56_production |         114 |
| core58_core56_skeleton         |        6170 |
| core58_failed_semantic_pair    |        8284 |
| core58_failed_motif            |       15047 |

## Reject Reason Summary

| core58_queue                    | reject_reason   |   row_count |
|:--------------------------------|:----------------|------------:|
| materialization_repair_rejected | semantic_cap    |        9187 |
| materialization_repair_rejected | motif_cap       |        5761 |
| materialization_repair_rejected | queue_full      |        3069 |
| numeric_replay_repair_rejected  | motif_cap       |         482 |
| numeric_replay_repair_rejected  | queue_full      |         430 |
| numeric_replay_repair_rejected  | semantic_cap    |         421 |

## Boundary

```text
replay executed: false
search executed: false
May used: false
large search / alpha proof / shadow / paper / live: false
```
