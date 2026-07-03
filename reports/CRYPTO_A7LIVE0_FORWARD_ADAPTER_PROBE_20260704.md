# CRYPTO A7LIVE0 Forward Adapter Probe

Generated: 2026-07-03T18:12:40Z

## Decision

`PASS_A7LIVE0_FORWARD_ADAPTER_PROBE_READY`

A7LIVE-0 validates that the A7SHADOW-7 review packet can be materialized from the forward-only recent patch field path. It does not run backtest, alpha proof, shadow, paper, or live trading.

## Counts

- loaded_symbol_count: `96` / `96`
- timestamp_start: `2026-05-26T00:00:00`
- timestamp_end: `2026-06-11T23:00:00`
- timestamp_count: `408`
- candidate_count: `2`
- eval_error_count: `0`
- min_field_finite_share: `0.9411764705882353`
- min_formula_non_null_ratio: `0.884446`
- min_formula_active_ratio: `0.884446`

## Field Health

| field                        | status   |   finite_share |   active_share |
|:-----------------------------|:---------|---------------:|---------------:|
| funding_rate_delta_state_24h | OK       |       0.941176 |       0.610396 |
| open_interest_mean           | OK       |       0.999643 |       0.999643 |
| open_interest_value_last     | OK       |       0.999643 |       0.999643 |
| premium_close_bps            | OK       |       1        |       0.567274 |

## Formula Materialization

| candidate_key      | blueprint_id   |   horizon_h | expression                                                                                          | eval_success   | error   |   rows |   non_null_rows |   finite_rows |   nan_rows |   inf_rows |   active_rows |   non_null_ratio |   active_ratio |      std |
|:-------------------|:---------------|------------:|:----------------------------------------------------------------------------------------------------|:---------------|:--------|-------:|----------------:|--------------:|-----------:|-----------:|--------------:|-----------------:|---------------:|---------:|
| a7shadow2_c007|h8  | a7shadow2_c007 |           8 | SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72)))) | True           |         |  39168 |           34642 |         34642 |       4526 |          0 |         34642 |         0.884446 |       0.884446 | 6.10321  |
| a7shadow2_c002|h24 | a7shadow2_c002 |          24 | Mul(CSRank(Mean(open_interest_mean,8)),Sign(Mean(premium_close_bps,48)))                            | True           |         |  39168 |           36946 |         36946 |       2222 |          0 |         36345 |         0.94327  |       0.927926 | 0.374081 |

## Interpretation

This is a forward adapter/materialization smoke, not a trading validation. Passing it means the selected formulas can be computed on the recent patch path with past-only derived funding delta; it does not validate execution, slippage, or future live behavior.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_live_adapter_probe_only": true,
  "authorizes_shadow_book": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "candidate_count": 2,
  "decision": "PASS_A7LIVE0_FORWARD_ADAPTER_PROBE_READY",
  "eval_error_count": 0,
  "generated_at": "2026-07-03T18:12:40Z",
  "loaded_symbol_count": 96,
  "min_field_finite_share": 0.9411764705882353,
  "min_formula_active_ratio": 0.884446,
  "min_formula_non_null_ratio": 0.884446,
  "missing_fields": [],
  "next_required": [
    "Build a source-lag and checksum audit for the forward patch before any proof claim.",
    "Keep this as adapter/materialization evidence only; it is not a live-trading authorization.",
    "Feed selected A7SHADOW-7 packet and overlap rejections into the next family-diversified search memory."
  ],
  "packet_path": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote\\runtime\\a7shadow7_dedup_review_packet_20260704\\a7shadow7_selected_review_packet.csv",
  "patch_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_recent_patch_1h_v1_20260612",
  "row_count": 39168,
  "stage": "A7LIVE-0",
  "symbol_count": 96,
  "timestamp_count": 408,
  "timestamp_end": "2026-06-11T23:00:00",
  "timestamp_start": "2026-05-26T00:00:00",
  "warnings": []
}
```
