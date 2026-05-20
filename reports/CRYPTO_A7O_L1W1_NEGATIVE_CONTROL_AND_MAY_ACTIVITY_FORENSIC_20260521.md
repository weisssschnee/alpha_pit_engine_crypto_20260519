# Crypto A7O-L1W1 Negative-Control And May-Activity Forensic

- date_tag: `20260521`
- scope: `A7O-L1W1 checkpoints 03-06`
- decision: `HOLD_A7O_L1W1`
- executes_new_search: `False`
- authorizes_w2: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`

## Finding

The first W1 attempt exposed a stress-gate loophole: candidates with `fresh_forward_2026May` gross exposure equal to zero were treated as post-May eligible when their May return and May residual were exactly zero.

The runner was repaired so post-May eligibility now requires:

```text
raw_10bp__fresh_forward_2026May__gross_exposure > 0
residual_vs_funding_10bp__fresh_forward_2026May__gross_exposure > 0
```

May remains stress-only. The repair does not add May to score, ranking, generation, allocation, mutation, or surrogate targets.

## Final W1 Result After Repair

| metric | value |
|:--|--:|
| generated | 524288 |
| strict replay | 6144 |
| deep audit | 768 |
| wave post-May eligible survivors | 40 |
| wave post-May eligible rate | 0.052083 |
| wave liquidity-volatility deep share | 0.132812 |
| wave single return-corr cluster share | 0.020833 |
| placebo/null research-like candidates | 2 |

## Remaining Negative Controls

After the May-activity repair, only checkpoint `04` still has negative-control research-like candidates:

| checkpoint | candidate_id | signal_mode | source families | May raw | May raw gross | May residual | May residual gross |
|:--|:--|:--|:--|--:|--:|--:|--:|
| 04 | `a7o_l1_C0208_1344` | `wrong_lag_stale_24h` | `liquidity;volatility` | 1.257068 | 0.497625 | 5.156704 | 0.497625 |
| 04 | `a7o_l1_C0223_0289` | `wrong_lag_stale_24h` | `liquidity;price` | 0.616668 | 0.463008 | 5.353100 | 0.463008 |

## Interpretation

The wave-level diversity and concentration controls passed, but W1 cannot advance because:

```text
1. placebo/null research-like candidates remain nonzero;
2. post-May eligible survivor count collapsed from 171 to 40 after requiring real May activity;
3. post-May eligible rate is 5.21%, below the 15% wave threshold.
```

This is a valid blocker. The next action is negative-control/wrong-lag forensic and stress-gate policy repair, not W2 or full L1.
