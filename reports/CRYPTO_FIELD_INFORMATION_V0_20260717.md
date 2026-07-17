# Crypto Field Information V0

Development-only field qualification; no OOS read, performance search, or promotion.

- Source SHA: `057e31df71f55f9e3a6e8ea3b48d53293d7d2e13`
- Token rows: 5388
- Census rows: 135
- Core Pack tokens: 120
- Unmaterialized derived specs: 5211

## BROAD_PANEL_BASELINE

- Fields audited: 41
- Census-loaded fields: 41
- Current-runtime members: 10
- Median coverage: 0.998090
- Missingness flags: 1
- Redundancy clusters: 31

Top residual-information fields:

- `trade_count`: residual excess=0.0278852, coverage=1.0000, block-positive=1.000
- `premium_high`: residual excess=0.0244126, coverage=1.0000, block-positive=0.917
- `trade_return_1h`: residual excess=0.0173588, coverage=0.9994, block-positive=1.000
- `trade_quote_volume`: residual excess=0.0170942, coverage=1.0000, block-positive=1.000
- `taker_buy_quote_volume`: residual excess=0.0168905, coverage=1.0000, block-positive=1.000
- `open_interest_value_last_change_24h`: residual excess=0.0141835, coverage=0.9959, block-positive=1.000
- `open_interest_value_last_change_4h`: residual excess=0.0137064, coverage=0.9972, block-positive=1.000
- `open_interest_value_last_change_1h`: residual excess=0.012225, coverage=0.9977, block-positive=1.000
- `taker_buy_sell_volume_ratio_mean`: residual excess=0.0101313, coverage=0.9981, block-positive=1.000
- `premium_open`: residual excess=0.00887432, coverage=1.0000, block-positive=0.833

## CORE3_MICROSTRUCTURE_PILOT

- Fields audited: 94
- Census-loaded fields: 94
- Current-runtime members: 0
- Median coverage: 1.000000
- Missingness flags: 0
- Redundancy clusters: 44

Top residual-information fields:

- `agg_price_range_bps_max_4h`: residual excess=0.0365897, coverage=1.0000, block-positive=1.000
- `agg_price_range_bps`: residual excess=0.0350346, coverage=1.0000, block-positive=1.000
- `agg_price_range_bps_max_24h`: residual excess=0.0322271, coverage=0.9989, block-positive=1.000
- `agg_notional_100_1k`: residual excess=0.0258935, coverage=1.0000, block-positive=1.000
- `agg_trade_count_1k_10k`: residual excess=0.0240158, coverage=1.0000, block-positive=1.000
- `agg_quantity_sum_24h`: residual excess=0.0208803, coverage=0.9989, block-positive=1.000
- `agg_quantity_sum_4h`: residual excess=0.0194578, coverage=1.0000, block-positive=1.000
- `agg_notional_1k_10k`: residual excess=0.0188747, coverage=1.0000, block-positive=1.000
- `agg_trade_count_100_1k`: residual excess=0.0187076, coverage=1.0000, block-positive=1.000
- `agg_buy_quantity`: residual excess=0.0182548, coverage=1.0000, block-positive=1.000

## Claim boundary

The Core3 result is `CORE3_MICROSTRUCTURE_MECHANISM_EVIDENCE` only. The Core Pack is a context-bound proposed model surface, not an active runtime registry, alpha proof, OOS result, or promotion candidate.
