# Crypto A7P Final Failure Decision Record

- generated_at: `2026-05-21T00:27:34Z`
- decision: `HOLD_CRYPTO_A7P_PRODUCTIVITY_AND_OBJECTIVE_FAILURE`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`

## Evidence Summary

| evidence_item         | status    | value                                                     | interpretation                                                                                       |
|:----------------------|:----------|:----------------------------------------------------------|:-----------------------------------------------------------------------------------------------------|
| runner_stability      | validated | eval_failure_count=0                                      | Protected W2 pilot executed without evaluator failures.                                              |
| fold_replay_stability | validated | fold_metric_missing_rate=0.0                              | Fold replay metrics were present for the pilot shard.                                                |
| negative_controls     | validated | strict=0, dominance=0, placebo=0                          | Negative controls did not penetrate after the A7P runner gate repair.                                |
| diversity_caps        | validated | liqvol=0.046875, cluster=0.09375                          | A7M/A7N-style single-cluster and liquidity-volatility collapse did not recur in the protected pilot. |
| productivity          | failed    | post_may_eligible=13/192=0.067708                         | Post-May eligible productivity is below the 15% continuation target.                                 |
| rank_alignment        | failed    | top_decile=0.0, bottom_decile=0.25                        | The current non-May rank score is directionally inverted against post-selection stress survival.     |
| stress_analog_repair  | failed    | stress_analog_top_decile=0.0, overall=0.06770833333333333 | A simple non-May difficult-fold stress analog did not repair the rank inversion.                     |

## Blocker Matrix

| blocker                                  | source      | severity   | blocks                                | does_not_block                                           |
|:-----------------------------------------|:------------|:-----------|:--------------------------------------|:---------------------------------------------------------|
| post_may_eligible_productivity_low       | A7P-3/A7P-4 | blocking   | W2 continuation, full L1, alpha proof | failure analysis, route decision, data/horizon contracts |
| non_may_rank_inverted_vs_post_may_stress | A7P-4       | blocking   | current high-score objective reuse    | objective reset analysis                                 |
| stress_analog_top_decile_weak            | A7P-5       | blocking   | simple worst-fold-rank repair         | new horizon/data contract                                |

## Interpretation

A7P is an engineering and audit-system success, but a search-objective failure. The protected W2 pilot ran cleanly after the runner gate repair, yet the eligible pool stayed too small and the non-May rank selected May-vetoed structures.

May remains stress-only and is not authorized for ranking, reward, generation, allocation, mutation, threshold tuning, or surrogate targets.