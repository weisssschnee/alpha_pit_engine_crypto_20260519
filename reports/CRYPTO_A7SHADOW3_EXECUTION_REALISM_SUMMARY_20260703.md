# CRYPTO A7SHADOW3 Execution Realism Summary

Generated: 2026-07-03T15:50:14.370481+00:00

## Decision

`PASS_A7SHADOW3_EXECUTION_REALISM_REWARD_ACCEPTED`

A7SHADOW-3 reruns the A7SHADOW-2 deduplicated keep leaders through the strict A7REWARD portfolio evaluator at 5bps cost. The first run exposed a queue adapter issue: empty `blueprint_id` values caused reward grouping to collapse multiple candidates into one blank id. R2 fixes this by assigning `blueprint_id = candidate_id` before evaluation.

This does not authorize alpha proof, shadow, paper, or live trading.

## Counts

- queue_rows: `5`
- reward_rows: `20`
- accepted_rows: `4`
- accepted_unique_blueprints: `3`
- hard_reject_rows: `16`
- eval_error_rows: `0`
- cost_bps: `5.0`
- train_crash_like_hours: `2312`
- may_stress_hours: `601`

## Accepted Rows

| blueprint_id | horizon | pareto | pass_count | train | validation | test | recent | min_oos_floor | stress_floor | turnover | capacity_proxy | expression |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| a7shadow2_c002 | 24 | 1 | 13 | 2.702454234750805 | 7.716974209683252 | 2.9251446047230125 | 5.964498019940686 | 1.9038409869878903 | 3.8769944978553337 | 0.004416534047068004 | 10971775.234606192 | `Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))` |
| a7shadow2_c006 | 24 | 1 | 13 | 0.7344125210610865 | 6.946148085453986 | 2.5037565195685585 | 2.4416335512125498 | 1.3646549978752314 | 6.105075206711021 | 0.0026674623842593897 | 11426024.185942467 | `Mul(open_interest_last,Mean(premium_close_bps,504))` |
| a7shadow2_c007 | 4 | 1 | 12 | 2.1779643196323804 | 10.163919317822558 | 10.216245843420882 | 13.542655057984913 | 8.633900693694594 | 2.390686280165006 | 0.0638846918159872 | 5811007.897889441 | `SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))` |
| a7shadow2_c007 | 8 | 1 | 12 | 2.4473052293036317 | 15.88145686150245 | 11.87446709225261 | 18.388209619597987 | 8.503209785655452 | 1.2732180686016796 | 0.0638846918159872 | 5811007.897889441 | `SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))` |

## Rejection Summary

| count | reasons |
|---:|---|
| 5 | `oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;shuffle_control_dominated_recent;source_lag_required_not_proven` |
| 2 | `oos_nonoverlap_floor_not_positive;oos_net_mean_not_all_positive;shuffle_control_dominated_recent;source_lag_required_not_proven` |
| 1 | `oos_control_dominated;oos_shuffle_dominated;shuffle_control_dominated_recent` |
| 1 | `oos_control_dominated;oos_lag_stale_dominated` |
| 1 | `train_sortino_non_positive;train_orientation_no_positive_edge;shuffle_control_dominated_recent;source_lag_required_not_proven` |
| 1 | `oos_control_dominated;oos_lag_stale_dominated;shuffle_control_dominated_recent;source_lag_required_not_proven` |
| 1 | `oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;shuffle_control_dominated_recent` |
| 1 | `stress_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;source_lag_required_not_proven` |
| 1 | `train_sortino_non_positive;train_orientation_no_positive_edge;oos_control_dominated;oos_lag_stale_dominated;shuffle_control_dominated_recent` |
| 1 | `oos_nonoverlap_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;source_lag_required_not_proven` |
| 1 | `oos_nonoverlap_floor_not_positive;stress_floor_not_positive;oos_control_dominated;oos_lag_stale_dominated;oos_shuffle_dominated;oos_net_mean_not_all_positive;source_lag_required_not_proven` |

## Interpretation

The execution/reward gate did not erase all historical candidates after the adapter fix. Four horizon rows survived, covering three deduplicated blueprints. The surviving set is still narrow: OI/premium and OI/funding dominate. That supports continuing engineering review for these mechanisms while treating broader formula-generation and feature-supply as still unresolved.

## Outputs

- accepted: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7shadow3_execution_realism_summary_20260703\a7shadow3_execution_accepted.csv`
- accepted_by_blueprint: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7shadow3_execution_realism_summary_20260703\a7shadow3_accepted_by_blueprint.csv`
- rejection_summary: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7shadow3_execution_realism_summary_20260703\a7shadow3_rejection_reason_summary.csv`
- manifest: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7shadow3_execution_realism_summary_20260703\a7shadow3_manifest.json`
