# CRYPTO A7SEARCH4 Final Aggregate Status 20260628

## Decision

`PASS_A7SEARCH4_PROXY_SEARCH_COMPLETED_WITH_STRICT_CANDIDATES`

Boundary: proxy search aggregate only. This does not authorize alpha proof, shadow, paper, or live.

## Runtime

- source run root: `G:\AlphaFactory_CryptoData\research_runtime\a7search4_mixed_constrained_train_aligned_proxy_65k_20260626`
- company aggregate root: `H:\AlphaFactory_CryptoData_archive\a7search4_final_aggregate_20260628`
- task: `job_20260626_095150_3f9a9e`
- task exit code: `0`

## Counts

- completed shards: `128 / 128`
- leaderboard rows: `32768`
- strict pass rows: `42`
- selected rows: `266`
- near-miss rows: `266`
- eval error rows: `0`

## Strict Pair Counts

- `open_interest|taker_flow`: `10`
- `liquidity|open_interest`: `7`
- `open_interest|premium`: `6`
- `basis|open_interest`: `5`
- `liquidity|positioning`: `3`
- `positioning|positioning`: `3`
- `open_interest|positioning`: `3`
- `positioning|premium`: `1`
- `positioning|taker_flow`: `1`
- `basis|positioning`: `1`
- `funding_dense|positioning`: `1`
- `open_interest|open_interest`: `1`

## Strict Motif Counts

- `additive_composite`: `13`
- `spread`: `8`
- `safe_div_abs_gated`: `6`
- `spread_gated`: `4`
- `smooth_mul`: `3`
- `additive_composite_gated`: `3`
- `smooth_mul_gated`: `3`
- `safe_div_abs`: `2`

## Best Strict Candidate

```text
Mul(
  SafeDiv(Decay(mark_index_basis_bps,240),Abs(Decay(account_position_divergence,120))),
  Sign(Decay(trade_quote_volume,336))
)
```

- semantic pair: `basis|positioning`
- motif: `safe_div_abs_gated`
- horizon: `24h`
- train_sortino: `2.7448`
- validation_sortino: `4.6964`
- test_sortino: `17.7582`
- recent_sortino: `10.4142`
- min_oos_floor_sortino: `2.8687`
- stress_floor_sortino: `3.1594`
- recent_control_ratio: `0.9896`
- recent_shuffle_control_ratio: `0.0976`
- hard_reject: `False`

## Review Notes

- Top selected rows include high-scoring near-miss candidates rejected by control or lag-stale dominance; strict rows must be preferred for next stage.
- Several strict rows share identical split metrics, indicating duplicated economic exposure or evaluator-equivalent formulas; next stage must cluster/dedupe before expensive replay.
- Strict candidates are still proxy-stage candidates, not alpha proof.

## Disk Status

- D:/G: had reached zero free space after the run.
- Old search runtime archival to `H:\AlphaFactory_CryptoData_archive\research_runtime_archived_20260628` was started.
- At last check, D:/G: free space had recovered to about `5.1GB`, and archival was still running.
- A7SEARCH4 aggregate outputs were written to H: to avoid filling D:/G: again.
