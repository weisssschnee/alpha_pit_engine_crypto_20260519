# CRYPTO A7LIVE1 Source-Lag / Checksum Audit

Generated: 2026-07-03T18:29:05Z

## Decision

`PASS_A7LIVE1_CONTROLLED_RESEARCH_SOURCE_LAG_OK_CHECKSUM_PENDING`

A7LIVE-1 audits the A7LIVE-0 forward patch path for timestamp lag, source trace, alias policy, and checksum boundary. It does not run backtest, alpha proof, shadow, paper, or live trading.

## Summary

- patch report decision: `PASS_BINANCE_UNIVERSE498_RECENT_PATCH_READY_WITH_SYMBOL_GAPS_FAST_CHECKSUM_PENDING`
- candidate_count: `2`
- selected_fields: `funding_rate_delta_state_24h, open_interest_mean, open_interest_value_last, premium_close_bps`
- controlled_research_blockers: `none`
- final_proof_blockers: `official_checksum_not_closed;recent_patch_report_fast_checksum_pending;rest_source_has_no_exchange_checksum`
- authorizes_family_diversified_search: `True`
- authorizes_alpha_proof: `False`
- authorizes_shadow_book/paper/live: `False`

## Selected Field Source Audit

| field                        | source_family      | raw_source                                         | controlled_research_status   | final_proof_status               |   local_sha256_count | checksum_status_values    | source_declared_in_contract   | lag_policy_ok   | availability_policy                                                      | same_bar_policy                            | controlled_blockers   | final_proof_blockers                                              |
|:-----------------------------|:-------------------|:---------------------------------------------------|:-----------------------------|:---------------------------------|---------------------:|:--------------------------|:------------------------------|:----------------|:-------------------------------------------------------------------------|:-------------------------------------------|:----------------------|:------------------------------------------------------------------|
| funding_rate_delta_state_24h | funding_rest       | Binance USD-M futures REST fapi/v1/fundingRate     | PASS_CONTROLLED_RESEARCH     | HOLD_FINAL_PROOF_SOURCE_EVIDENCE |                    0 | rest_no_exchange_checksum | True                          | True            | derived from event funding_rate, ffilled only from known past event rows | 24h lagged delta; no negative lag allowed  |                       | official_checksum_not_closed;rest_source_has_no_exchange_checksum |
| open_interest_mean           | metrics            | Binance Vision futures/um/daily/metrics            | PASS_CONTROLLED_RESEARCH     | HOLD_FINAL_PROOF_SOURCE_EVIDENCE |                 8466 |                           | True                          | True            | timestamp + 1h conservative bucket close availability                    | usable at execution_time timestamp+1h only |                       | official_checksum_not_closed                                      |
| open_interest_value_last     | metrics            | Binance Vision futures/um/daily/metrics            | PASS_CONTROLLED_RESEARCH     | HOLD_FINAL_PROOF_SOURCE_EVIDENCE |                 8466 |                           | True                          | True            | timestamp + 1h conservative bucket close availability                    | usable at execution_time timestamp+1h only |                       | official_checksum_not_closed                                      |
| premium_close_bps            | premiumIndexKlines | Binance Vision futures/um/daily/premiumIndexKlines | PASS_CONTROLLED_RESEARCH     | HOLD_FINAL_PROOF_SOURCE_EVIDENCE |                 8463 |                           | True                          | True            | timestamp + 1h conservative bucket close availability                    | usable at execution_time timestamp+1h only |                       | official_checksum_not_closed                                      |

## Timestamp Lag Audit

| item                         | policy                                                                                    | status   |
|:-----------------------------|:------------------------------------------------------------------------------------------|:---------|
| timestamp                    | 1h bucket start UTC naive                                                                 | PASS     |
| feature_available_time       | timestamp + 1h conservative bucket close availability                                     | PASS     |
| execution_time               | timestamp + 1h                                                                            | PASS     |
| funding_rate_delta_state_24h | adapter derives from ffilled current-or-past funding_rate minus 24h lag; no forward shift | PASS     |

## Alias Policy

| requested_field              | patch_field   | adapter_field                | status            | policy                                                                                  |
|:-----------------------------|:--------------|:-----------------------------|:------------------|:----------------------------------------------------------------------------------------|
| premium_close_bps            | premium_bps   | premium_close_bps            | alias_required    | rename premium_bps to premium_close_bps before formula evaluation                       |
| funding_rate_delta_state_24h | funding_rate  | funding_rate_delta_state_24h | derived_past_only | ffill funding_rate within symbol up to 8h, then subtract 24h lagged dense funding value |

## Patch Manifest Audit

| check                    |   rows |   duplicate_timestamp_sum |   inf_cell_sum | checksum_status_values                        | min_timestamp       | max_timestamp       | status   |   min_coverage |   min_mark_coverage |   min_metrics_coverage |   min_funding_coverage |
|:-------------------------|-------:|--------------------------:|---------------:|:----------------------------------------------|:--------------------|:--------------------|:---------|---------------:|--------------------:|-----------------------:|-----------------------:|
| gold_manifest            |    498 |                         0 |              0 | vision_fast_checksum_pending_rest_no_checksum | 2026-05-26 00:00:00 | 2026-06-11 23:00:00 | PASS     |            nan |                 nan |             nan        |                    nan |
| selected_symbol_coverage |     96 |                           |                |                                               | 2026-05-26 00:00:00 | 2026-06-11 23:00:00 | PASS     |              1 |                   1 |               0.965686 |                      1 |

## Download Manifest Family Summary

| source               | family             |   rows | status_values                 | checksum_status_values   |   sha256_present_count |   error_count |
|:---------------------|:-------------------|-------:|:------------------------------|:-------------------------|-----------------------:|--------------:|
| binance_fapi_rest    | fundingRate        |    498 | downloaded;exists             | rest_no_checksum         |                    498 |             0 |
| binance_vision_daily | indexPriceKlines   |   8466 | downloaded;exists             | not_checked_fast_path    |                   8466 |             0 |
| binance_vision_daily | klines             |   8466 | downloaded;exists             | not_checked_fast_path    |                   8466 |             0 |
| binance_vision_daily | markPriceKlines    |   8466 | downloaded;exists             | not_checked_fast_path    |                   8466 |             0 |
| binance_vision_daily | metrics            |   8466 | downloaded;exists             | not_checked_fast_path    |                   8466 |             0 |
| binance_vision_daily | premiumIndexKlines |   8466 | downloaded;exists;missing_404 | not_checked_fast_path    |                   8463 |             3 |

## Interpretation

The forward patch has enough declared timestamp-lag policy and local source trace for controlled research continuation if controlled blockers are empty. It is still not final proof because the recent patch explicitly remains fast-checksum-pending and REST funding has no exchange checksum.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_family_diversified_search": true,
  "authorizes_final_proof": false,
  "authorizes_shadow_book": false,
  "authorizes_shadow_paper_live": false,
  "candidate_count": 2,
  "controlled_research_blockers": [],
  "coverage_rows": 498,
  "decision": "PASS_A7LIVE1_CONTROLLED_RESEARCH_SOURCE_LAG_OK_CHECKSUM_PENDING",
  "download_manifest_rows": 42828,
  "field_audit_rows": 4,
  "final_proof_blockers": [
    "official_checksum_not_closed",
    "recent_patch_report_fast_checksum_pending",
    "rest_source_has_no_exchange_checksum"
  ],
  "generated_at": "2026-07-03T18:29:05Z",
  "gold_manifest_rows": 498,
  "next_required": [
    "Close official Binance Vision CHECKSUM audit before any final proof claim.",
    "Treat REST funding source as controlled-research evidence unless an independent archive/source trace is added.",
    "Proceed to A7SEARCH7 family-diversified queue only if controlled_research_blockers is empty."
  ],
  "packet_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7shadow7_dedup_review_packet_20260704\\a7shadow7_selected_review_packet.csv",
  "patch_dataset": "binance_universe498_recent_patch_1h_v1_20260612",
  "patch_report_decision": "PASS_BINANCE_UNIVERSE498_RECENT_PATCH_READY_WITH_SYMBOL_GAPS_FAST_CHECKSUM_PENDING",
  "patch_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_recent_patch_1h_v1_20260612",
  "selected_fields": [
    "funding_rate_delta_state_24h",
    "open_interest_mean",
    "open_interest_value_last",
    "premium_close_bps"
  ],
  "stage": "A7LIVE-1"
}
```
