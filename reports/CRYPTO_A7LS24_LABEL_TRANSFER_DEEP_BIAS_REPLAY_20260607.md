# CRYPTO A7LS-24 Label-Transfer Deep Bias Replay (20260607)

## Decision

`PASS_A7LS24_LABEL_TRANSFER_PACKET_READY_FOR_A7LS25`

## Summary

- input candidates: 7
- label-transfer seeds: 3
- strong label-transfer: 1
- mechanism label-transfer: 2
- L5-only holds: 4
- label-transfer semantic pairs: 3

## Main Finding

A7LS23 correctly flagged the main risk: the selected queue is L5-heavy. A7LS24 narrows it to candidates that transfer beyond L5 into raw/relative/liquidity-tier labels. The rest are retained only as L5 controls.

## Label-Transfer Seeds

### a7ls15_982c459fa90224ed

- decision: `PASS_A7LS24_STRONG_LABEL_TRANSFER`
- semantic_pair: `positioning_like|basis_premium_like`
- selected label: `L5_vol_adjusted_return / 4h`
- non-L5/non-L7 clue rows: `3`
- non-L5/non-L7 label families: `3`
- score_no_may: `173.3326`
- control_ratio_premay_max: `0.7410`
- principle: basis/premium dislocation versus positioning crowding
- expression: `Sub(CSRank(top_long_short_account_ratio_last),CSRank(mark_index_basis_bps))`

### a7ls15_04d0fe57519a6e45

- decision: `PASS_A7LS24_MECHANISM_LABEL_TRANSFER`
- semantic_pair: `open_interest_like|positioning_like`
- selected label: `L5_vol_adjusted_return / 4h`
- non-L5/non-L7 clue rows: `1`
- non-L5/non-L7 label families: `1`
- score_no_may: `63.4718`
- control_ratio_premay_max: `0.6466`
- principle: leverage expansion/contraction combined with trader positioning imbalance
- expression: `Mean(Mul(Decay(open_interest_mean,16),Delta(top_long_short_position_ratio_mean,4)),4)`

### a7ls15_78478a819e0cd255

- decision: `PASS_A7LS24_MECHANISM_LABEL_TRANSFER`
- semantic_pair: `open_interest_like|taker_flow_like`
- selected label: `L5_vol_adjusted_return / 1h`
- non-L5/non-L7 clue rows: `1`
- non-L5/non-L7 label families: `1`
- score_no_may: `28.3254`
- control_ratio_premay_max: `0.8316`
- principle: open-interest crowding combined with aggressive taker-flow pressure
- expression: `Mean(Mul(Abs(ZScore(Mean(open_interest_value_mean,120))),Abs(ZScore(Mean(kline_taker_buy_quote_share,96)))),4)`

## Boundaries

- This stage uses existing A7LS21 label-response metrics; it does not generate or replay new formulas.
- May is not used.
- A7LS25 is authorized only as a label-transfer portfolio contribution replay packet.
- Search, alpha proof, shadow, paper, and live remain blocked.

## Decision Counts

| decision                             |   count |
|:-------------------------------------|--------:|
| HOLD_A7LS24_L5_ONLY                  |       4 |
| PASS_A7LS24_MECHANISM_LABEL_TRANSFER |       2 |
| PASS_A7LS24_STRONG_LABEL_TRANSFER    |       1 |
