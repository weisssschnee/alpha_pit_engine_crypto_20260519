# Explicit/Latent Adaptive implementation qualification

This note supersedes broad interpretations of the original development report. It does not alter the frozen runtime artifacts or rerun the economic comparison.

## Qualified conclusion

The observed result is an **implementation-specific informative negative** for the fixed residual TCN and overlapping field-family grouped multi-branch TCN on the authorized adaptive-development splits. Both arms had non-collapsed predictions and portfolio differences, but their positive mean gross increments became negative after full-L1 turnover at 5 bps.

It does not establish that all 41 fields were learned or used, that structured market-state latents are generally ineffective, or that the result is OOS-qualified.

## Capability gate scope

The original 41/41 result establishes that all registry fields were loadable from the existing panel cache and met the configured minimum adaptive-surface nonmissing and variance checks. The tensor was structurally wired to the model.

It did not independently re-verify source lineage or PIT semantics, measure per-field batch exposure or gradient reachability, establish learned output utilization, or test whether a field carried nonredundant information. Future capability output uses these separate names and no longer emits `PIT_qualified` or `model_input_exposed` from loadability alone.

## Arm D

The Known checkpoint is loaded, put in evaluation mode, frozen, and evaluated under `no_grad`. Arm D adds its residual prediction to the frozen Known prediction. The five arms share the same splits, t+2 execution, 4h target, zero-net portfolio mapping, full-L1 turnover, and 5 bps cost. This comparison is implementation-verified.

## Arm E

Implemented:

- four field-family grouped TCN branches;
- overlapping field membership across branches;
- shared return, future-volatility, and masked-reconstruction losses;
- inference-time zero-out slot ablation.

Not implemented or not verified:

- slot-specific semantic targets;
- exclusive field ownership or disentanglement constraints;
- causal identification;
- within-slot permutation or representation-replacement ablations.

Because overlapping fields are written into the shared reconstruction tensor with `index_copy_`, later branches can overwrite earlier reconstruction values for the same field. The accurate name is **structured proxy**, not an identified ecosystem latent model.

## Matched-control qualification

The config declares parameter-matched Known MLP, window-matched explicit model, and random-permuted latent controls. The runtime metrics contain only Ridge and HistGradientBoosting fit diagnostics; they are not common-bridge economic matched controls. Therefore the three declared controls are **DECLARED_NOT_EXECUTED** and cannot support a matched-control claim for Arm E.

## Field-surface inventory

The 41-field TCN surface is not the repository's full representational inventory. It contains seven raw volume/activity inputs (`taker_buy_quote_volume`, `taker_buy_volume`, `trade_count`, `trade_quote_volume`, `trade_volume`, and two taker buy/sell ratio summaries), but few normalized or interaction features.

The separate recovered aggTrades inventory contains 94 enabled base specifications and 5,211 derived specifications: 4,606 rolling transforms, 395 cross-symbol transforms, and 210 interactions. The base set includes quantity/notional, signed aggressor flow, buy/sell splits, size buckets, VWAP, large-trade shares, impact/range measures, 4h/24h aggregates, shocks/acceleration, universe shares, and BTC/ETH-relative flow. The derived set spans rolling mean/std/delta/decay/min/max/z-score at 4–96h, cross-symbol rank/z-score/share, BTC/ETH relatives, and arithmetic/interactions.

These are not currently equivalent to 18-month model inputs: 5,378 of 5,388 inventory rows are `runtime_loaded=False`, and the recovered aggTrades base registry is limited to `core3_available_rows_only`. They should be activated only after ingress coverage, PIT lag, variance, and independent-block adequacy pass—not bulk-injected because a static formula exists.
