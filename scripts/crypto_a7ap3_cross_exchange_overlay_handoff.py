from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ap3_repaired_overlay_experiment_handoff"
REPORT = REPO / "reports" / "CRYPTO_A7AP3_REPAIRED_OVERLAY_EXPERIMENT_HANDOFF_20260527.md"

A7AP0_MANIFEST = REPO / "runtime" / "a7ap0_cross_exchange_overlay_acceptance" / "a7ap0_manifest.json"
A7AP1_MANIFEST = REPO / "runtime" / "a7ap1_cross_exchange_field_smoke" / "a7ap1_manifest.json"
A7AP2_MANIFEST = REPO / "runtime" / "a7ap2_multiplier_price_scale_repair" / "a7ap2_manifest.json"


def read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict]) -> str:
    if not rows:
        return ""
    fields = list(rows[0].keys())
    out = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(f, "")) for f in fields) + " |")
    return "\n".join(out)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    a7ap0 = read_json(A7AP0_MANIFEST)
    a7ap1 = read_json(A7AP1_MANIFEST)
    a7ap2 = read_json(A7AP2_MANIFEST)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    field_policy = [
        {
            "field_or_family": "mark_basis_bps_okx_contract_unit_minus_binance",
            "status": "allowed_diagnostic",
            "reason": "OKX mark price is converted to Binance contract unit before comparison",
            "scope": "short_window_overlay_diagnostic_only",
        },
        {
            "field_or_family": "index_spread_bps_okx_contract_unit_minus_binance",
            "status": "allowed_diagnostic",
            "reason": "OKX index price is converted to Binance contract unit before comparison",
            "scope": "short_window_overlay_diagnostic_only",
        },
        {
            "field_or_family": "funding_spread_okx_minus_binance",
            "status": "allowed_diagnostic_with_coverage_caveat",
            "reason": "Only 20.1 percent valid rows in the 103-hour overlap due sparse Binance funding rows",
            "scope": "coverage_audit_and_diagnostic_only",
        },
        {
            "field_or_family": "okx_internal_mark_index_basis_bps",
            "status": "allowed_diagnostic",
            "reason": "Single-venue internal basis; not affected by multiplier cross-venue scale mismatch",
            "scope": "short_window_overlay_diagnostic_only",
        },
        {
            "field_or_family": "binance_internal_mark_index_basis_bps",
            "status": "allowed_diagnostic",
            "reason": "Single-venue internal basis; useful as baseline context",
            "scope": "short_window_overlay_diagnostic_only",
        },
        {
            "field_or_family": "raw okx/binance mark/index price columns",
            "status": "allowed_source_context_only",
            "reason": "Raw fields are preserved for audit but should not be used directly for cross-venue basis on multiplier contracts",
            "scope": "source_audit_only",
        },
    ]

    blocked_aliases = [
        {
            "blocked_field_or_alias": "mark_basis_bps_okx_minus_binance",
            "replacement": "mark_basis_bps_okx_contract_unit_minus_binance",
            "block_reason": "Unsafe for multiplier contracts; caused about -9990 bps false basis",
        },
        {
            "blocked_field_or_alias": "index_spread_bps_okx_minus_binance",
            "replacement": "index_spread_bps_okx_contract_unit_minus_binance",
            "block_reason": "Unsafe for multiplier contracts; caused about -9990 bps false index spread",
        },
        {
            "blocked_field_or_alias": "okx_mark_close - binance_mark_close direct comparison",
            "replacement": "okx_mark_close_contract_unit - binance_mark_close",
            "block_reason": "Direct price comparison mixes underlying-unit and contract-unit prices",
        },
        {
            "blocked_field_or_alias": "okx_index_close - binance_index_close direct comparison",
            "replacement": "okx_index_close_contract_unit - binance_index_close",
            "block_reason": "Direct price comparison mixes underlying-unit and contract-unit prices",
        },
    ]

    authorization = [
        {"item": "repaired overlay field diagnostics", "authorized": True, "notes": "Use repaired contract-unit fields only"},
        {"item": "short-window field smoke", "authorized": True, "notes": "Diagnostic only; 103 hourly timestamps"},
        {"item": "forward telemetry design", "authorized": True, "notes": "Append-only/forward context only"},
        {"item": "broad formula search", "authorized": False, "notes": "Overlap too short and A7AP1/A7AP2 found no clue"},
        {"item": "historical alpha proof", "authorized": False, "notes": "No historical OKX overlay proof window"},
        {"item": "shadow / paper / live", "authorized": False, "notes": "Not a tradable proof object"},
    ]

    next_work = [
        {
            "task": "A7AP-4 forward overlay collector contract",
            "priority": "P0",
            "why": "Current OKX/Binance overlap is 103 hours; useful proof needs append-only forward accumulation",
        },
        {
            "task": "A7AP-5 longer overlap source feasibility",
            "priority": "P1",
            "why": "Check whether OKX historical mark/index/funding can be extended without PIT ambiguity",
        },
        {
            "task": "A7AP-6 integrate allowed fields into formula registry with blocked alias guard",
            "priority": "P1",
            "why": "Prevent future generators from using unsafe raw cross-venue basis aliases",
        },
    ]

    decision = "PASS_A7AP3_REPAIRED_OVERLAY_HANDOFF_DIAGNOSTIC_ONLY"
    manifest = {
        "generated_at": generated_at,
        "decision": decision,
        "input_a7ap0_decision": a7ap0.get("decision"),
        "input_a7ap1_decision": a7ap1.get("decision"),
        "input_a7ap2_decision": a7ap2.get("decision"),
        "repaired_gold_root": a7ap2.get("output_gold_root"),
        "symbols": a7ap2.get("symbols"),
        "rows": a7ap2.get("rows"),
        "unique_hours": a7ap2.get("unique_hours"),
        "price_scale_repair_symbol_count": a7ap2.get("price_scale_repair_symbol_count"),
        "price_scale_repair_symbols": a7ap2.get("price_scale_repair_symbols"),
        "post_repair_extreme_symbol_count": a7ap2.get("post_repair_extreme_symbol_count"),
        "diagnostic_clue_count": a7ap2.get("diagnostic_clue_count"),
        "authorizes_diagnostic_use_repaired_fields": True,
        "authorizes_broad_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_search": False,
        "executes_replay": False,
        "blockers": [],
        "warnings": [
            "Use repaired contract-unit fields for cross-venue price comparisons",
            "Original raw cross-venue price differences remain audit-only for multiplier contracts",
            "Overlap is only 103 hours; no historical alpha proof",
        ],
    }

    (RUNTIME / "a7ap3_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_csv(RUNTIME / "a7ap3_field_use_policy.csv", field_policy)
    write_csv(RUNTIME / "a7ap3_blocked_field_aliases.csv", blocked_aliases)
    write_csv(RUNTIME / "a7ap3_authorization_matrix.csv", authorization)
    write_csv(RUNTIME / "a7ap3_next_work_queue.csv", next_work)

    report = f"""# CRYPTO A7AP-3 Repaired Overlay Experiment Handoff

Generated: {generated_at}

## Decision

```text
{decision}
```

This stage does not run search or replay. It freezes the experiment-facing rules for the repaired OKX/Binance cross-exchange overlay.

## Summary

```json
{json.dumps(manifest, indent=2)}
```

## Field Use Policy

{markdown_table(field_policy)}

## Blocked Field Aliases

{markdown_table(blocked_aliases)}

## Authorization Matrix

{markdown_table(authorization)}

## Next Work

{markdown_table(next_work)}

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
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
