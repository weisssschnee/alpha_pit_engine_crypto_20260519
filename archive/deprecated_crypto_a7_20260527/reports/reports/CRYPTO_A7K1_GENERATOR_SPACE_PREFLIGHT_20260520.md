# Crypto A7K-1 Generator-Space Preflight

- generated_at: `2026-05-19T17:38:29Z`
- decision: `HOLD_A7K1_PREFLIGHT_BLOCKED`
- evidence_level: `generator_preflight_not_alpha_proof`
- executes_search: `False`
- executes_replay: `False`
- authorizes_a7k2: `False`
- authorizes_alpha_proof: `False`
- may_exclusion_pass: `True`
- old_pool_a7k_preselection_pass_count: `11/1000`
- blockers: `['old_a7j_pool_still_has_candidates_passing_a7k_preselection', 'old_pool_family_cap_fail']`

## Interpretation

- A7K-1 validates the redesigned preselection gates against the frozen failed A7J/A7I pool.
- A pass here means the old failure modes are mechanically screened; it does not mean a new generator can produce alpha candidates.
- A7K-2 remains blocked until a new-space generator implementation is reviewed with the same contract.

## Feature Coverage

| feature | required lane | coverage_all | symbols >=95% | core12 pass |
|---|---|---:|---:|---:|
| `abs_ret_1` | `core12` | 1.0000 | 12/12 | `True` |
| `avg_trade_size_quote` | `core12` | 1.0000 | 12/12 | `True` |
| `cs_z_mark_index_ratio` | `core12` | 1.0000 | 12/12 | `True` |
| `cs_z_premium_index` | `core12` | 1.0000 | 12/12 | `True` |
| `hl_range` | `core12` | 1.0000 | 12/12 | `True` |
| `mark_index_ratio` | `core12` | 1.0000 | 12/12 | `True` |
| `mark_minus_index` | `core12` | 1.0000 | 12/12 | `True` |
| `number_of_trades` | `core12` | 1.0000 | 12/12 | `True` |
| `premium_index` | `core12` | 1.0000 | 12/12 | `True` |
| `quote_asset_volume` | `core12` | 1.0000 | 12/12 | `True` |
| `quote_volume_mean_12` | `core12` | 1.0000 | 12/12 | `True` |
| `quote_volume_mean_24` | `core12` | 1.0000 | 12/12 | `True` |
| `quote_volume_mean_6` | `core12` | 1.0000 | 12/12 | `True` |
| `realized_vol_12` | `core12` | 0.9997 | 12/12 | `True` |
| `realized_vol_24` | `core12` | 0.9994 | 12/12 | `True` |
| `realized_vol_6` | `core12` | 0.9999 | 12/12 | `True` |
| `taker_buy_ratio` | `core12` | 1.0000 | 12/12 | `True` |
| `taker_imbalance` | `core12` | 1.0000 | 12/12 | `True` |

## Tightest Old-Pool Gates

| gate | pass_count | fail_count | pass_rate |
|---|---:|---:|---:|
| `raw_recent_positive` | 57 | 943 | 0.0570 |
| `cost20_recent_nonnegative` | 70 | 930 | 0.0700 |
| `cost20_validation_nonnegative` | 93 | 907 | 0.0930 |
| `raw_validation_positive` | 93 | 907 | 0.0930 |
| `lag1_recent_nonnegative` | 103 | 897 | 0.1030 |
| `lag1_validation_nonnegative` | 147 | 853 | 0.1470 |
| `residual_funding_validation_positive` | 531 | 469 | 0.5310 |
| `residual_core4_recent_positive` | 560 | 440 | 0.5600 |

## May Exclusion

| check | pass |
|---|---:|
| `contract_forbids_may_in_generator_tuning` | `True` |
| `preselection_gate_columns_exclude_may` | `True` |
| `score_columns_exclude_may` | `True` |
| `may_columns_present_only_as_stress_metrics` | `True` |

## Boundary

- May remains stress-only.
- This preflight does not authorize alpha proof, shadow, paper, live, or production.
- Do not expand the old A7J generator budget. Next valid engineering work is new-space generator implementation review or forward wait.
