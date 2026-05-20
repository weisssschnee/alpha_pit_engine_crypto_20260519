# Crypto A7N Regime-Invariant Counterfactual

- generated_at: `2026-05-20T11:44:48Z`
- decision: `HOLD_A7N2_OBJECTIVE_STILL_COLLAPSES`
- executes_search: `False`
- executes_replay: `False`
- alpha_proof_status: `NOT_ALPHA_PROOF`
- authorizes_a7n3: `False`
- blockers: `['strict_liquidity_volatility_share_lte_30pct', 'strict_field_families_gte_4', 'deep_rc000_share_lte_35pct', 'deep_return_corr_clusters_gte_6', 'deep_field_families_gte_4']`

## A7N-0 Objective Contract

The objective replaces mean validation/recent strength with non-May worst-case survival terms:

- min raw validation/recent
- min residual vs FundingCore/Core4 validation/recent
- min cost20 validation/recent
- min 1bar-lag validation/recent
- positive non-May term rate
- field/operator/formula concentration penalties

May is stress-only and is not used in score construction, ranking, generation, arm allocation, or mutation.

## A7N-1 Non-May Fold Library

| fold_id                         | generated_at         | feature_source                                  | definition                                                                  | purpose                                                    | may_allowed   | status                     |
|:--------------------------------|:---------------------|:------------------------------------------------|:----------------------------------------------------------------------------|:-----------------------------------------------------------|:--------------|:---------------------------|
| F0_calendar_block_folds         | 2026-05-20T11:44:48Z | timestamp                                       | validation/recent monthly or biweekly calendar blocks                       | avoid one block supporting candidate ranking               | False         | contract_only_not_replayed |
| F1_high_realized_vol_fold       | 2026-05-20T11:44:48Z | realized_vol_6/12/24                            | top non-May realized volatility quantile inside validation/recent           | stress volatility-regime dependence                        | False         | contract_only_not_replayed |
| F2_low_liquidity_fold           | 2026-05-20T11:44:48Z | quote_volume/trade_count/activity               | bottom non-May liquidity/activity quantile inside validation/recent         | stress liquidity fragility                                 | False         | contract_only_not_replayed |
| F3_high_liquidity_high_vol_fold | 2026-05-20T11:44:48Z | quote volume x realized volatility              | intersection of high liquidity and high volatility inside validation/recent | constrain liquidity-volatility collapse without May labels | False         | contract_only_not_replayed |
| F4_basis_dislocation_fold       | 2026-05-20T11:44:48Z | mark_index_ratio/premium_index/mark_minus_index | large absolute basis or premium dislocation inside validation/recent        | stress basis-regime dependence                             | False         | contract_only_not_replayed |
| F5_funding_neutral_fold         | 2026-05-20T11:44:48Z | latest_known_funding_rate/funding persistence   | non-extreme funding state inside validation/recent                          | detect hidden funding-family wrappers                      | False         | contract_only_not_replayed |
| F6_cross_symbol_dispersion_fold | 2026-05-20T11:44:48Z | cross-symbol returns/vol/basis dispersion       | high cross-symbol dispersion inside validation/recent                       | stress cross-sectional stability                           | False         | contract_only_not_replayed |
| F7_trend_reversal_fold          | 2026-05-20T11:44:48Z | non-May trend/reversal state                    | trend to reversal or reverse-shock blocks inside validation/recent          | avoid one-direction trend-only alpha wrappers              | False         | contract_only_not_replayed |

These are fold contracts only. Existing A7M-2 artifacts do not contain per-regime-fold replay metrics, so A7N-2 uses split-level non-May metrics plus structural diversity proxies.

## A7N-2 Counterfactual Summary

| pool                                   | score_col                  |   count |   return_corr_cluster_count |   top_return_corr_cluster_share |   rc_000_share |   field_family_count |   top_field_family_share |   liquidity_volatility_share |   engine_count |   placebo_or_null_count |   operator_horizon_count |   top_operator_horizon_share |
|:---------------------------------------|:---------------------------|--------:|----------------------------:|--------------------------------:|---------------:|---------------------:|-------------------------:|-----------------------------:|---------------:|------------------------:|-------------------------:|-----------------------------:|
| strict_old_a7m_top_decile              | a7m_rank_score             |     409 |                           0 |                        0        |       0        |                    4 |                 0.831296 |                     0.899756 |              6 |                       0 |                        3 |                     0.518337 |
| strict_a7n_raw_top_decile              | a7n_regime_invariant_score |     409 |                           0 |                        0        |       0        |                    4 |                 0.775061 |                     0.885086 |              6 |                       0 |                        6 |                     0.511002 |
| strict_a7n_diversity_capped_top_decile | a7n_regime_invariant_score |     250 |                           0 |                        0        |       0        |                    3 |                 0.512    |                     0.488    |              6 |                       0 |                        4 |                     0.408    |
| deep_old_a7m_top_decile                | a7m_rank_score             |      51 |                           3 |                        0.901961 |       0.901961 |                    1 |                 1        |                     1        |              6 |                       0 |                        3 |                     0.901961 |
| deep_a7n_raw_top_decile                | a7n_regime_invariant_score |      51 |                           4 |                        0.784314 |       0.784314 |                    2 |                 0.901961 |                     0.901961 |              6 |                       0 |                        3 |                     0.784314 |
| deep_a7n_diversity_capped_top_decile   | a7n_regime_invariant_score |      26 |                           5 |                        0.461538 |       0.461538 |                    2 |                 0.576923 |                     0.576923 |              5 |                       0 |                        3 |                     0.461538 |

## Gate Summary

| gate                                        | pass   |
|:--------------------------------------------|:-------|
| may_excluded_from_score_components          | True   |
| strict_liquidity_volatility_share_lte_30pct | False  |
| strict_field_families_gte_4                 | False  |
| strict_engines_gte_4                        | True   |
| strict_placebo_null_zero                    | True   |
| deep_rc000_share_lte_35pct                  | False  |
| deep_return_corr_clusters_gte_6             | False  |
| deep_field_families_gte_4                   | False  |
| deep_engines_gte_4                          | True   |
| deep_placebo_null_zero                      | True   |

## Decision

- A7N-3 is authorized only if A7N-2 gates pass.
- A7M-3 remains unauthorized.
- No alpha proof, shadow, paper, or live deployment is authorized.