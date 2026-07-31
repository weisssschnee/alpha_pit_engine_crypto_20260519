# Crypto Search Economic V1

- Status: `ENGINE_BUDGET_EXHAUSTED` (`RAW_GENERATION_ATTEMPT_LIMIT`)
- Producer source: `17d5b5f19acd1366cf5b8f332249d78e918556f1`
- Closure source: `da7842dabacf7c98e62475014666877eeda86664`
- Surface: existing 115-field OI/mark x aggTrades aligned carrier; receipt-bound Binance USD-M target; frozen cost assumption `5 bps`.
- Strict completed: `1,190` from `95,776` raw attempts.
- Behavior families: `1,160`; duplicate rate `2.52%`.
- Emergency checkpoint restore verified: `True`.

## Arm evidence

| Arm | Raw attempts | Compile-valid | Strict | Families | Mean search reward | Top-decile search reward | Mean pair reward | Top-decile pair reward |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| canonical_typed_random | 411 | 411 | 397 | 397 | -0.537082 | -0.105266 | -5.188884 | -2.797846 |
| cem_distribution_v1 | 47,236 | 0 | 0 | 0 | n/a | n/a | n/a | n/a |
| evolutionary_typed_v1 | 47,233 | 0 | 0 | 0 | n/a | n/a | n/a | n/a |
| hierarchical_typed_cem_v2 | 411 | 411 | 399 | 399 | -0.509507 | -0.052529 | -5.023316 | -2.097396 |
| typed_evolution_v2 | 485 | 478 | 394 | 364 | -0.369273 | 0.042797 | -4.450877 | -1.320651 |

Strict `pair_reward` positives: `0`;
matched-positive discoveries: `0`;
positive joint search rewards: `35`.
Joint search-reward positives are partial train diagnostics and do not override
the strict matched authority.

## Terminal diagnosis

The two fresh-state V1 controls consumed almost the entire raw-attempt budget
before compilation.  Their legacy proposal path re-required a complete Broad
role surface after a compatible carrier-specific skeleton subset had already
been frozen, and failed on the absent `oi_change` role.  This is a proposal
layer defect, not evidence that the carrier lacks economic information.

The campaign did not reach `checkpoint_000`; validation, adaptive checkpoint
updates, OOS, promotion, challenge, and any next Arena remain unstarted.
No seed, parameter, or rescue rerun was used.
