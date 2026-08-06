# Crypto Replication-Aware Search Gate V1

- Engineering status: `PASS_REPLICATION_AWARE_SEARCH_GATE_V1_COMPLETE`; research gate: `NOT_QUALIFIED_FOR_VALIDATION`.
- Producer source: `fd6220d56e0632b5084c2ed7574992c8bc2803fb`.
- Development-only strict evaluations: `1,536` from `2,077` attempts; sealed reads `0`.
- Scope: existing 115-field aligned carrier, 4h binary mechanisms, Binance USD-M target, existing mapping, matched controls and frozen 5 bps cost.
- Checkpoints: `3/3`; exact restore: `True`.
- Validation/OOS/promotion: `NOT_AUTHORIZED` / `NOT_AUTHORIZED` / `FORBIDDEN`.

| Arm | Strict | Attempts | Families | Replicated 2/3+ | Replicated 3/3 | Replicated / CPU-hour |
|---|---:|---:|---:|---:|---:|---:|
| block_robust_typed_random_v1 | 512 | 534 | 511 | 13 | 1 | 32.376 |
| block_robust_evolution_current_v1 | 512 | 792 | 487 | 27 | 2 | 66.903 |
| block_robust_evolution_replication_v1 | 512 | 751 | 474 | 29 | 0 | 74.651 |

Gate checks that failed: `leave_best_template_out_delta_positive`.
Supported templates with positive robust-minus-current delta: `FLOW_INTENSITY_CONVICTION, FUNDING_FLOW_CROWDING`.

The robust arm changes only development parent ordering. It does not change the
reward formula, target, mapping, cost, mechanism catalog, compiler, AST, or
evaluator. Passing this gate authorizes nothing automatically; any development
validation requires a separate instruction and frozen cohort.
