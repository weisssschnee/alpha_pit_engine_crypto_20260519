# CRYPTO A7SHADOW0 Historical Strong Candidate Consolidation

Generated: 2026-07-03T14:45:57.443253+00:00

## Decision

`PASS_A7SHADOW0_HISTORICAL_STRONG_CANDIDATES_CONSOLIDATED`

This stage consolidates historical strong candidates into a shadow-readiness review queue. It does not authorize alpha proof, paper trading, shadow trading, or live trading.

## Counts

- input_sources: `10`
- input_rows: `464`
- consolidated_unique_formula_horizon_rows: `423`
- shadow_readiness_review_rows: `9`
- source_lag_retest_required_rows: `26`
- hold_or_diagnostic_rows: `388`

## Shadow-Readiness Review Queue

| rank | semantic_pair | horizon_h | sources | tier | train_sortino | validation_sortino | test_sortino | recent_sortino | min_oos_floor | stress_floor | expression |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | `open_interest|funding_state` | 8 | 5 | `TIER1_REPEATED_STRICT_EVIDENCE` | 2.4473052293036317 | 3.249800166301023 | 0.9630842884017243 | 7.559932085877106 | 0.2598951543447928 | 1.2732180686016796 | `SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))` |
| 2 | `open_interest|premium` | 24 | 2 | `TIER1_SOURCE_LAG_STRICT` | 2.702454234750805 | 7.716974209683252 | 2.9251446047230125 | 5.964498019940686 | 1.9038409869878905 | 3.8769944978553337 | `Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))` |
| 3 | `open_interest` | 24 | 2 | `TIER1_SOURCE_LAG_STRICT` | 3.4985599741227675 | 2.551076502062724 | 3.891615500928222 | 4.392425060799842 | 1.781994350944033 | 0.13792916060062388 | `TSRank(open_interest_mean,504)` |
| 4 | `open_interest` | 24 | 2 | `TIER1_SOURCE_LAG_STRICT` | 3.4985599741227675 | 2.551076502062724 | 3.891615500928222 | 4.392425060799842 | 1.781994350944033 | 0.13792916060062388 | `CSRank(TSRank(open_interest_mean,504))` |
| 5 | `open_interest|premium` | 24 | 2 | `TIER1_SOURCE_LAG_STRICT` | 2.686465423009736 | 7.659977926659238 | 3.1015925816130734 | 5.808610213843688 | 1.7382108706045547 | 3.874363020584573 | `Mul(CSRank(Mean(open_interest_mean,12)),Sign(Mean(premium_close_bps,48)))` |
| 6 | `open_interest|premium` | 24 | 2 | `TIER1_SOURCE_LAG_STRICT` | 0.7344125210610865 | 6.946148085453986 | 2.5037565195685585 | 2.4416335512125498 | 1.3646549978752314 | 6.105075206711021 | `Mul(open_interest_last,Mean(premium_close_bps,504))` |
| 7 | `funding_dense|open_interest` | 4 | 2 | `TIER1_SOURCE_LAG_STRICT` | 2.1779643196323804 | 10.163919317822558 | 10.216245843420882 | 13.542655057984913 | 8.633900693694594 | 2.390686280165006 | `SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))` |
| 8 | `open_interest|premium` | 8 | 1 | `TIER1_SOURCE_LAG_STRICT` | 1.6738290056815706 | 3.26076368248325 | 1.5093742087075606 | 8.624545933433998 | 0.0306556339170487 | 5.9974362789799525 | `Mul(CSRank(open_interest_mean),Decay(premium_close_bps,168))` |
| 9 | `basis|premium` | 24 | 1 | `TIER2_STRICT_CONTROLLED_FIELD` | 1.200553313309487 | 6.330483749690659 | 5.510858270897706 | 1.8147482368255796 | 0.8522200631450245 | 6.497715977476842 | `Mul(Decay(premium_abs_state,336),Abs(ZScore(Mean(mark_trade_basis_bps,168))))` |

## Interpretation

Historical strong evidence is concentrated in a small number of mechanisms: OI/funding, OI/positioning, and basis/premium. The review queue is suitable for shadow-readiness engineering checks, not for direct shadow deployment.

## Outputs

- source_inventory: `runtime\a7shadow0_historical_strong_candidate_consolidation_20260703\a7shadow0_source_inventory.csv`
- consolidated: `runtime\a7shadow0_historical_strong_candidate_consolidation_20260703\a7shadow0_consolidated_candidates.csv`
- shadow_review_queue: `runtime\a7shadow0_historical_strong_candidate_consolidation_20260703\a7shadow0_shadow_readiness_review_queue.csv`
- source_lag_retest_queue: `runtime\a7shadow0_historical_strong_candidate_consolidation_20260703\a7shadow0_source_lag_retest_required_queue.csv`
- hold_or_diagnostic_queue: `runtime\a7shadow0_historical_strong_candidate_consolidation_20260703\a7shadow0_hold_or_diagnostic_queue.csv`
- family_summary: `runtime\a7shadow0_historical_strong_candidate_consolidation_20260703\a7shadow0_family_summary.csv`
- manifest: `runtime\a7shadow0_historical_strong_candidate_consolidation_20260703\a7shadow0_manifest.json`
