# CRYPTO A7V3S5 Prefiltered Reward Queue - 20260613

## Decision

`PASS_A7V3S5_PREFILTERED_QUEUE_READY`

A7V3S5 applies the A7V3S4 search-space prefilter rules to the existing A7V3S0 activity-ok queue. It builds a filtered reward queue and a redesign-hold queue. It does not execute reward, replay, alpha proof, shadow, paper, or live.

## Inputs

- Activity queue: `D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_v3_native_large_search_c2_aggregate_20260613\a7ls17_activity_ok_queue.csv`
- Prefilter rules: `a7v3s4_search_space_prefilter_rules.json`
- Input activity-ok rows: `60,640`

## Filter Result

| bucket | rows |
| --- | ---: |
| structural excluded | 9,187 |
| hard-blocked by A7V3S4 | 14,363 |
| deprioritized recent-only by A7V3S4 | 532 |
| redesign-only hold by A7V3S4 | 2,194 |
| eligible after hard filters | 34,364 |
| selected reward prequeue | 2,963 |

The requested target was 4,096, but bounded lane/pair/motif/skeleton caps selected 2,963 rows. This is acceptable for the next smoke because the point of A7V3S5 is not to fill quota; it is to avoid pushing known control/stale-dominated patterns into expensive reward evaluation.

## Selected Coverage

- Selected semantic pairs: `42`
- Selected motifs: `10`
- Selected skeletons: `2,695`

Top selected semantic pairs are cap-balanced at 96 rows each, including:

| semantic_pair | count |
| --- | ---: |
| basis\|funding_basis | 96 |
| basis\|funding_dense | 96 |
| basis\|regime | 96 |
| basis\|open_interest | 96 |
| basis\|premium | 96 |
| basis\|positioning | 96 |
| basis\|taker_flow | 96 |
| funding_basis\|regime | 96 |
| funding_basis\|premium | 96 |
| funding_basis\|open_interest | 96 |
| positioning\|premium | 96 |
| positioning\|regime | 96 |
| positioning\|taker_flow | 96 |
| funding_dense\|open_interest | 96 |
| liquidity\|positioning | 96 |

Selected motif distribution:

| motif | count |
| --- | ---: |
| smooth_mul | 640 |
| signed_rank_gate | 640 |
| spread_rank | 640 |
| safe_div_abs | 624 |
| state_conditioned_signed | 179 |
| state_conditioned_rank_mul | 163 |
| oi_flow_scaled_spread | 41 |
| funding_basis_delta_sign | 12 |
| funding_basis_spread_24h | 12 |
| oi_flow_delta_rank | 12 |

## Outputs

Runtime:

`runtime/a7v3s5_prefiltered_queue_20260613/`

Files:

- `a7v3s5_prefiltered_reward_prequeue.csv`
- `a7v3s5_redesign_hold_queue.csv`
- `a7v3s5_prefilter_reject_summary.csv`
- `a7v3s5_selected_pair_summary.csv`
- `a7v3s5_selected_motif_summary.csv`
- `a7v3s5_selected_pair_motif_summary.csv`
- `a7v3s5_manifest.json`

## Interpretation

A7V3S5 confirms that the A7V3S4 filter is not over-killing the space. It removes a large polluted block while preserving a broad selected queue:

- hard-blocked known control/stale-dominated pair-motif patterns,
- separated redesign-only near-miss structures,
- retained enough semantic/motif/skeleton diversity for a reward smoke.

## Authorization

Allowed next:

- small strict reward smoke on the A7V3S5 prefiltered queue,
- then aggregate and compare accepted/rejection rates against A7V3S3 early-stop baseline.

Not authorized:

- full reward wave before smoke,
- continuing the old A7V3S3 queue,
- alpha proof,
- shadow / paper / live.

