# CRYPTO A7LS-22 Clue Attribution / Promotion Triage (20260607)

## Decision

`PASS_A7LS22_RESEARCH_REVIEW_QUEUE_READY`

## Summary

- input selected queue: 13
- keep-review allowed: 7
- non-L7 keep-review allowed: 7
- duplicate clusters: 12
- semantic pairs: 11
- top label family share: 61.54%
- top semantic pair share: 15.38%

## Main Finding

A7LS21 did not collapse into one formula shape. It produced a small but usable research-review queue across basis/liquidity, basis/listing-age, basis/positioning, OI/positioning, and OI/taker-flow structures. The main risk is label concentration: L5 vol-adjusted return remains the dominant label family.

## Keep-Review Queue

### a7ls15_6b338a109f660b8c

- semantic_pair: `basis_premium_like|liquidity_like`
- motif: `signed_spread`
- label: `L5_vol_adjusted_return / 24h`
- score_no_may: `363.4710`
- control_ratio_premay_max: `0.6678`
- principle: basis/premium dislocation filtered by liquidity or volume state
- 简释: 基差/溢价异常只有在特定流动性状态下更可能有预测意义。 核心标签：basis/premium dislocation；liquidity / volume state；liquidity state
- expression: `Mul(Sub(CSRank(Decay(premium_abs_state,240)),CSRank(ZScore(Mean(trade_volume,12)))),Sign(ZScore(Mean(trade_volume,12))))`

### a7ls15_7355ef8aa37d5217

- semantic_pair: `basis_premium_like`
- motif: `signed_spread`
- label: `L5_vol_adjusted_return / 8h`
- score_no_may: `285.9897`
- control_ratio_premay_max: `0.7046`
- principle: typed state interaction
- 简释: 多个已知状态变量的类型化交互，需要继续检查增量信息。 核心标签：basis/premium dislocation
- expression: `Mul(Sub(CSRank(Delta(mark_trade_basis_bps,2)),CSRank(TSRank(mark_index_basis_bps,336))),Sign(TSRank(mark_index_basis_bps,336)))`

### a7ls15_42dc6539d51aca8b

- semantic_pair: `basis_premium_like|positioning_like`
- motif: `mul`
- label: `L5_vol_adjusted_return / 8h`
- score_no_may: `259.0615`
- control_ratio_premay_max: `0.8968`
- principle: basis/premium dislocation versus positioning crowding
- 简释: 基差/溢价偏离与多空持仓拥挤之间的相对状态。 核心标签：basis/premium dislocation；positioning crowding
- expression: `Mul(CSRank(mark_trade_basis_bps),Abs(ZScore(Mean(global_long_short_account_ratio_mean,120))))`

### a7ls15_982c459fa90224ed

- semantic_pair: `positioning_like|basis_premium_like`
- motif: `spread_rank`
- label: `L5_vol_adjusted_return / 4h`
- score_no_may: `173.3326`
- control_ratio_premay_max: `0.7410`
- principle: basis/premium dislocation versus positioning crowding
- 简释: 基差/溢价偏离与多空持仓拥挤之间的相对状态。 核心标签：basis/premium dislocation；positioning crowding
- expression: `Sub(CSRank(top_long_short_account_ratio_last),CSRank(mark_index_basis_bps))`

### a7ls15_83b2ec53c58ee01a

- semantic_pair: `listing_age_like|basis_premium_like`
- motif: `mul`
- label: `L5_vol_adjusted_return / 24h`
- score_no_may: `148.8799`
- control_ratio_premay_max: `0.8941`
- principle: basis/premium dislocation conditioned on listing lifecycle
- 简释: 新老币生命周期会改变基差/溢价异常的含义。 核心标签：basis/premium dislocation；listing lifecycle
- expression: `Mul(ZScore(Mean(listing_age_days,336)),Delta(mark_index_basis_bps,3))`

### a7ls15_04d0fe57519a6e45

- semantic_pair: `open_interest_like|positioning_like`
- motif: `smooth_mul`
- label: `L5_vol_adjusted_return / 4h`
- score_no_may: `63.4718`
- control_ratio_premay_max: `0.6466`
- principle: leverage expansion/contraction combined with trader positioning imbalance
- 简释: 杠杆仓位变化和多空拥挤共同刻画拥挤交易状态。 核心标签：leverage / open-interest state；positioning crowding
- expression: `Mean(Mul(Decay(open_interest_mean,16),Delta(top_long_short_position_ratio_mean,4)),4)`

### a7ls15_78478a819e0cd255

- semantic_pair: `open_interest_like|taker_flow_like`
- motif: `smooth_mul`
- label: `L5_vol_adjusted_return / 1h`
- score_no_may: `28.3254`
- control_ratio_premay_max: `0.8316`
- principle: open-interest crowding combined with aggressive taker-flow pressure
- 简释: 持仓扩张叠加主动买卖压力，用来识别杠杆资金流方向。 核心标签：leverage / open-interest state；aggressive taker flow
- expression: `Mean(Mul(Abs(ZScore(Mean(open_interest_value_mean,120))),Abs(ZScore(Mean(kline_taker_buy_quote_share,96)))),4)`

## Boundaries

- This stage does not execute search or replay.
- May is not used.
- ALLOW_KEEP_REVIEW is not alpha proof; it only authorizes strict candidate-factor review / bias audit packet.
- Shadow, paper, and live remain blocked.

## Triage Counts

| triage_decision                 |   count |
|:--------------------------------|--------:|
| ALLOW_KEEP_REVIEW               |       7 |
| DIAGNOSTIC_ONLY_RANK_LABEL      |       3 |
| HOLD_DUPLICATE_CLUSTER_FOLLOWER |       1 |
| HOLD_STABILITY_OR_COST_WEAK     |       1 |
| HOLD_LOW_MARGINAL_SCORE         |       1 |
