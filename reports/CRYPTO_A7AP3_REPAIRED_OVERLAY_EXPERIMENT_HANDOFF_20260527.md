# CRYPTO A7AP-3 Repaired Overlay Experiment Handoff

Generated: 2026-05-27T01:17:59Z

## Decision

```text
PASS_A7AP3_REPAIRED_OVERLAY_HANDOFF_DIAGNOSTIC_ONLY
```

This stage does not run search or replay. It freezes the experiment-facing rules for the repaired OKX/Binance cross-exchange overlay.

## Summary

```json
{
  "generated_at": "2026-05-27T01:17:59Z",
  "decision": "PASS_A7AP3_REPAIRED_OVERLAY_HANDOFF_DIAGNOSTIC_ONLY",
  "input_a7ap0_decision": "PASS_A7AP0_CROSS_EXCHANGE_OVERLAY_ACCEPTED_WITH_PRICE_SCALE_QUARANTINE",
  "input_a7ap1_decision": "PASS_A7AP1_CROSS_EXCHANGE_FIELD_SMOKE_DIAGNOSTIC_ONLY",
  "input_a7ap2_decision": "PASS_A7AP2_MULTIPLIER_PRICE_SCALE_REPAIR_DIAGNOSTIC_READY",
  "repaired_gold_root": "G:\\AlphaFactory_CryptoData\\gold\\features\\okx_binance_cross_exchange_1h_30d_v1_price_scale_repaired_20260527",
  "symbols": 218,
  "rows": 22345,
  "unique_hours": 103,
  "price_scale_repair_symbol_count": 4,
  "price_scale_repair_symbols": [
    "1000BONKUSDT",
    "1000FLOKIUSDT",
    "1000PEPEUSDT",
    "1000SHIBUSDT"
  ],
  "post_repair_extreme_symbol_count": 0,
  "diagnostic_clue_count": 0,
  "authorizes_diagnostic_use_repaired_fields": true,
  "authorizes_broad_search": false,
  "authorizes_alpha_proof": false,
  "authorizes_shadow_paper_live": false,
  "executes_search": false,
  "executes_replay": false,
  "blockers": [],
  "warnings": [
    "Use repaired contract-unit fields for cross-venue price comparisons",
    "Original raw cross-venue price differences remain audit-only for multiplier contracts",
    "Overlap is only 103 hours; no historical alpha proof"
  ]
}
```

## Field Use Policy

| field_or_family | status | reason | scope |
| --- | --- | --- | --- |
| mark_basis_bps_okx_contract_unit_minus_binance | allowed_diagnostic | OKX mark price is converted to Binance contract unit before comparison | short_window_overlay_diagnostic_only |
| index_spread_bps_okx_contract_unit_minus_binance | allowed_diagnostic | OKX index price is converted to Binance contract unit before comparison | short_window_overlay_diagnostic_only |
| funding_spread_okx_minus_binance | allowed_diagnostic_with_coverage_caveat | Only 20.1 percent valid rows in the 103-hour overlap due sparse Binance funding rows | coverage_audit_and_diagnostic_only |
| okx_internal_mark_index_basis_bps | allowed_diagnostic | Single-venue internal basis; not affected by multiplier cross-venue scale mismatch | short_window_overlay_diagnostic_only |
| binance_internal_mark_index_basis_bps | allowed_diagnostic | Single-venue internal basis; useful as baseline context | short_window_overlay_diagnostic_only |
| raw okx/binance mark/index price columns | allowed_source_context_only | Raw fields are preserved for audit but should not be used directly for cross-venue basis on multiplier contracts | source_audit_only |

## Blocked Field Aliases

| blocked_field_or_alias | replacement | block_reason |
| --- | --- | --- |
| mark_basis_bps_okx_minus_binance | mark_basis_bps_okx_contract_unit_minus_binance | Unsafe for multiplier contracts; caused about -9990 bps false basis |
| index_spread_bps_okx_minus_binance | index_spread_bps_okx_contract_unit_minus_binance | Unsafe for multiplier contracts; caused about -9990 bps false index spread |
| okx_mark_close - binance_mark_close direct comparison | okx_mark_close_contract_unit - binance_mark_close | Direct price comparison mixes underlying-unit and contract-unit prices |
| okx_index_close - binance_index_close direct comparison | okx_index_close_contract_unit - binance_index_close | Direct price comparison mixes underlying-unit and contract-unit prices |

## Authorization Matrix

| item | authorized | notes |
| --- | --- | --- |
| repaired overlay field diagnostics | True | Use repaired contract-unit fields only |
| short-window field smoke | True | Diagnostic only; 103 hourly timestamps |
| forward telemetry design | True | Append-only/forward context only |
| broad formula search | False | Overlap too short and A7AP1/A7AP2 found no clue |
| historical alpha proof | False | No historical OKX overlay proof window |
| shadow / paper / live | False | Not a tradable proof object |

## Next Work

| task | priority | why |
| --- | --- | --- |
| A7AP-4 forward overlay collector contract | P0 | Current OKX/Binance overlap is 103 hours; useful proof needs append-only forward accumulation |
| A7AP-5 longer overlap source feasibility | P1 | Check whether OKX historical mark/index/funding can be extended without PIT ambiguity |
| A7AP-6 integrate allowed fields into formula registry with blocked alias guard | P1 | Prevent future generators from using unsafe raw cross-venue basis aliases |

## Boundary

```text
AUTHORIZED:
  repaired cross-exchange fields for diagnostic use
  forward telemetry / collector design

NOT AUTHORIZED:
  broad formula search
  historical alpha proof
  shadow / paper / live

REASON:
  A7AP-2 repaired multiplier scale mismatch, but the overlap window remains 103 hours and the field smoke found 0 diagnostic clues.
```
