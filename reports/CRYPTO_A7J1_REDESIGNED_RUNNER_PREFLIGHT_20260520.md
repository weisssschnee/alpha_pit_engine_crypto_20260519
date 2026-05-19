# Crypto A7J-1 Redesigned Runner Preflight

- generated_at: `2026-05-19T17:07:24Z`
- decision: `PASS_A7J1_REDESIGNED_RUNNER_PREFLIGHT`
- evidence_level: `runner_preflight_not_alpha_proof`
- classification_match: `9/9`
- may_exclusion_pass: `True`
- authorizes_a7j2: `True`
- authorizes_alpha_proof: `False`

## Classification

| object | expected | actual | match | reasons |
|---|---|---|---:|---|
| `FundingCore` | `MANDATORY_BASELINE_NOT_CANDIDATE` | `MANDATORY_BASELINE_NOT_CANDIDATE` | `True` | `` |
| `Core4` | `RESEARCH_BENCHMARK_NOT_CANDIDATE` | `RESEARCH_BENCHMARK_NOT_CANDIDATE` | `True` | `` |
| `Rank(taker_imbalance)` | `HOLD_RESIDUAL_ONLY_HEDGE_CLUE` | `HOLD_RESIDUAL_ONLY_HEDGE_CLUE` | `True` | `standalone_raw_negative;overlay_only` |
| `i2_microstructure_lite_113` | `A7J_CLUE_ONLY` | `A7J_CLUE_ONLY` | `True` | `residual_funding_validation_nonpositive;residual_core4_recent_nonpositive;cost20_recent_negative;may_stress_veto_label` |
| `a7i1a_taker_imbalance_sign_flip` | `NEGATIVE_CONTROL` | `NEGATIVE_CONTROL` | `True` | `` |
| `a7i1a_taker_imbalance_row_shuffle` | `NEGATIVE_CONTROL` | `NEGATIVE_CONTROL` | `True` | `` |
| `a7i1a_taker_imbalance_time_shuffle` | `NEGATIVE_CONTROL` | `NEGATIVE_CONTROL` | `True` | `` |
| `a7i1a_taker_imbalance_wrong_lag` | `NEGATIVE_CONTROL` | `NEGATIVE_CONTROL` | `True` | `` |
| `a7i1a_random_noise_placebo` | `NEGATIVE_CONTROL` | `NEGATIVE_CONTROL` | `True` | `` |

## May Exclusion

| check | pass |
|---|---:|
| `score_components_have_no_may_columns` | `True` |
| `ranking_columns_exclude_may` | `True` |
| `may_only_final_label` | `True` |
| `a7j2_not_authorized_by_a7j0` | `True` |

## Boundary

- May stress is not included in rank score components.
- May stress may only label/veto after selection.
- PASS here authorizes same-budget A7J-2 smoke, not alpha proof.
