# CRYPTO A7SOURCE-1 Field Timing Proof

Generated: `2026-07-03T02:28:54Z`

## Decision

`HOLD_A7SOURCE1_FIELD_TIMING_PROOF_INCOMPLETE`

This audits source timing proof for June-diagnostic A7SEARCH6 survivors. It is a bias gate, not a return-improvement step.

## Summary

| field_family   | proof_decision                        |   fields |   formulas |
|:---------------|:--------------------------------------|---------:|-----------:|
| open_interest  | HOLD_PUBLICATION_LAG_PROOF_REQUIRED   |        2 |          3 |
| basis_premium  | PASS_CONTROLLED_EXPERIMENT            |        1 |          1 |
| funding_state  | HOLD_EVENT_PUBLICATION_PROOF_REQUIRED |        1 |          1 |
| positioning    | HOLD_PUBLICATION_LAG_PROOF_REQUIRED   |        1 |          1 |

## Formula Gate

| source_blueprint_id        | blueprint_id                                      |   horizon_h |   june_sortino |   june_nonoverlap_floor_sortino | formula_decision           | field_proof_decisions                                                     | blocking_issues                                                                                                                                                                                                                                                                                                                  | formula                                                                                             |
|:---------------------------|:--------------------------------------------------|------------:|---------------:|--------------------------------:|:---------------------------|:--------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------|
| a7search6_afa93f504b4c29d0 | a7search6_vp_a7search6_afa93f504b4c29d0_canonical |           4 |       14.4965  |                       13.8609   | HOLD_SOURCE_PROOF_REQUIRED | HOLD_EVENT_PUBLICATION_PROOF_REQUIRED|HOLD_PUBLICATION_LAG_PROOF_REQUIRED | funding_rate_delta_state_24h:dense funding state uses past-only ffill/delta, but funding event publication timestamp is not independently carried into reward rows;open_interest_value_last:Binance metrics create_time is observation timestamp; vendor publication lag is not independently proven for full 498 recent patch   | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) |
| a7search6_2e796ac0b2a688c4 | a7search6_vp_a7search6_2e796ac0b2a688c4_canonical |          24 |        2.48831 |                        0.471413 | HOLD_SOURCE_PROOF_REQUIRED | HOLD_PUBLICATION_LAG_PROOF_REQUIRED|PASS_CONTROLLED_EXPERIMENT            | premium_close_bps:final proof still requires official CHECKSUM audit;open_interest_last:Binance metrics create_time is observation timestamp; vendor publication lag is not independently proven for full 498 recent patch                                                                                                       | Mul(open_interest_last,Mean(premium_close_bps,504))                                                 |
| a7search6_e7ee64f0ef980aca | a7search6_vp_a7search6_e7ee64f0ef980aca_canonical |           4 |        1.83127 |                        0.264097 | HOLD_SOURCE_PROOF_REQUIRED | HOLD_PUBLICATION_LAG_PROOF_REQUIRED                                       | open_interest_value_last:Binance metrics create_time is observation timestamp; vendor publication lag is not independently proven for full 498 recent patch;top_long_short_account_ratio_last:Binance metrics create_time is observation timestamp; vendor publication lag is not independently proven for full 498 recent patch | SafeDiv(TSRank(open_interest_value_last,504),Abs(Mean(top_long_short_account_ratio_last,8)))        |

## Blocking Interpretation

- Metrics fields have good historical source trace for core12 and controlled recent-patch coverage, but full 498 recent-patch publication lag is not independently proven.
- Funding dense state is mechanically past-only, but event publication timestamp is not carried into reward rows.
- Therefore source-lag retest is authorized as diagnostic, while alpha proof/search expansion remains blocked.

