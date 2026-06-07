# CRYPTO A7LS-23 Strict Candidate Bias Audit (20260607)

## Decision

`PASS_A7LS23_STRICT_BIAS_AUDIT_READY_FOR_A7LS24`

## Summary

- input keep-review candidates: 7
- A7LS24 deep replay queue: 7
- priority deep replay: 3
- secondary deep replay: 4
- selected L5 share: 100.00%
- semantic pairs: 7

## Interpretation

The queue is usable for the next deep-bias replay packet. It is not proof. The strongest risk remains label concentration around L5 vol-adjusted return, so A7LS24 must test label transfer and portfolio contribution explicitly.

## A7LS24 Queue

### a7ls15_6b338a109f660b8c

- decision: `PRIORITY_DEEP_BIAS_REPLAY`
- semantic_pair: `basis_premium_like|liquidity_like`
- selected label: `L5_vol_adjusted_return / 24h`
- score_no_may: `363.4710`
- control_ratio_premay_max: `0.6678`
- non_l7_clue_rows_all_labels: `2`
- flags: `selected_l5_vol_adjusted|limited_label_transfer|basis_premium_dependent`
- principle: basis/premium dislocation filtered by liquidity or volume state
- expression: `Mul(Sub(CSRank(Decay(premium_abs_state,240)),CSRank(ZScore(Mean(trade_volume,12)))),Sign(ZScore(Mean(trade_volume,12))))`

### a7ls15_7355ef8aa37d5217

- decision: `PRIORITY_DEEP_BIAS_REPLAY`
- semantic_pair: `basis_premium_like`
- selected label: `L5_vol_adjusted_return / 8h`
- score_no_may: `285.9897`
- control_ratio_premay_max: `0.7046`
- non_l7_clue_rows_all_labels: `1`
- flags: `selected_l5_vol_adjusted|limited_label_transfer|basis_premium_dependent`
- principle: typed state interaction
- expression: `Mul(Sub(CSRank(Delta(mark_trade_basis_bps,2)),CSRank(TSRank(mark_index_basis_bps,336))),Sign(TSRank(mark_index_basis_bps,336)))`

### a7ls15_42dc6539d51aca8b

- decision: `SECONDARY_LABEL_TRANSFER_REPLAY`
- semantic_pair: `basis_premium_like|positioning_like`
- selected label: `L5_vol_adjusted_return / 8h`
- score_no_may: `259.0615`
- control_ratio_premay_max: `0.8968`
- non_l7_clue_rows_all_labels: `1`
- flags: `selected_l5_vol_adjusted|limited_label_transfer|thin_control_margin|basis_premium_dependent`
- principle: basis/premium dislocation versus positioning crowding
- expression: `Mul(CSRank(mark_trade_basis_bps),Abs(ZScore(Mean(global_long_short_account_ratio_mean,120))))`

### a7ls15_982c459fa90224ed

- decision: `PRIORITY_DEEP_BIAS_REPLAY`
- semantic_pair: `positioning_like|basis_premium_like`
- selected label: `L5_vol_adjusted_return / 4h`
- score_no_may: `173.3326`
- control_ratio_premay_max: `0.7410`
- non_l7_clue_rows_all_labels: `4`
- flags: `selected_l5_vol_adjusted|basis_premium_dependent`
- principle: basis/premium dislocation versus positioning crowding
- expression: `Sub(CSRank(top_long_short_account_ratio_last),CSRank(mark_index_basis_bps))`

### a7ls15_83b2ec53c58ee01a

- decision: `SECONDARY_LABEL_TRANSFER_REPLAY`
- semantic_pair: `listing_age_like|basis_premium_like`
- selected label: `L5_vol_adjusted_return / 24h`
- score_no_may: `148.8799`
- control_ratio_premay_max: `0.8941`
- non_l7_clue_rows_all_labels: `1`
- flags: `selected_l5_vol_adjusted|limited_label_transfer|thin_control_margin|basis_premium_dependent`
- principle: basis/premium dislocation conditioned on listing lifecycle
- expression: `Mul(ZScore(Mean(listing_age_days,336)),Delta(mark_index_basis_bps,3))`

### a7ls15_04d0fe57519a6e45

- decision: `SECONDARY_DEEP_BIAS_REPLAY`
- semantic_pair: `open_interest_like|positioning_like`
- selected label: `L5_vol_adjusted_return / 4h`
- score_no_may: `63.4718`
- control_ratio_premay_max: `0.6466`
- non_l7_clue_rows_all_labels: `2`
- flags: `selected_l5_vol_adjusted`
- principle: leverage expansion/contraction combined with trader positioning imbalance
- expression: `Mean(Mul(Decay(open_interest_mean,16),Delta(top_long_short_position_ratio_mean,4)),4)`

### a7ls15_78478a819e0cd255

- decision: `SECONDARY_DEEP_BIAS_REPLAY`
- semantic_pair: `open_interest_like|taker_flow_like`
- selected label: `L5_vol_adjusted_return / 1h`
- score_no_may: `28.3254`
- control_ratio_premay_max: `0.8316`
- non_l7_clue_rows_all_labels: `2`
- flags: `selected_l5_vol_adjusted`
- principle: open-interest crowding combined with aggressive taker-flow pressure
- expression: `Mean(Mul(Abs(ZScore(Mean(open_interest_value_mean,120))),Abs(ZScore(Mean(kline_taker_buy_quote_share,96)))),4)`

## Boundaries

- May is not used.
- No search is executed or authorized.
- A7LS24 is authorized only as a deeper replay/bias packet for this queue.
- Alpha proof, shadow, paper, and live remain blocked.

## Decision Counts

| decision                        |   count |
|:--------------------------------|--------:|
| PRIORITY_DEEP_BIAS_REPLAY       |       3 |
| SECONDARY_LABEL_TRANSFER_REPLAY |       2 |
| SECONDARY_DEEP_BIAS_REPLAY      |       2 |
