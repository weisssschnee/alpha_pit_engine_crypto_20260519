from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
A7AE0_AUTH = ROOT / "runtime" / "a7ae0_new_data_intake_audit" / "a7ae0_authorization_matrix.json"
OUT_DIR = ROOT / "runtime" / "a7ae1_field_selection_contract"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AE1_FIELD_SELECTION_CONTRACT_20260522.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def selected_field_contract() -> pd.DataFrame:
    rows = [
        # Independent metrics source fields.
        ("metrics_source", "open_interest", "independent", "core39", "allowed", "source field; use level/change/zscore variants only after selection"),
        ("metrics_source", "open_interest_value", "independent", "core39", "allowed", "source field; stale-level controls required"),
        ("metrics_source", "global_long_short_account_ratio", "independent", "core39", "allowed", "crowding/account state source"),
        ("metrics_source", "top_long_short_account_ratio", "independent", "core39", "allowed", "crowding/account state source"),
        ("metrics_source", "top_long_short_position_ratio", "independent", "core39", "allowed", "position crowding source"),
        ("metrics_source", "taker_buy_sell_volume_ratio", "independent", "core39", "allowed", "vendor 5m metrics source, not aggTrades"),
        # Market structure source fields.
        ("market_structure", "mark_index_basis_bps", "independent_derived_from_mark_index", "core39", "allowed", "basis level from mark/index source"),
        ("market_structure", "mark_index_basis_change_24h", "derived", "core39", "allowed", "basis dynamic; preferred over static basis for stale-control risk"),
        ("market_structure", "mark_index_basis_zscore_168h", "derived", "core39", "allowed", "basis state"),
        ("market_structure", "premium_index_bps", "independent_derived_from_premium", "core39", "allowed", "premium source state"),
        ("market_structure", "premium_index_change_24h", "derived", "core39", "allowed", "premium dynamic"),
        ("market_structure", "premium_minus_funding_bps", "derived", "core39", "caution", "missing can be high; funding asof semantics required"),
        ("market_structure", "funding_rate_bps", "independent_asof", "core39", "benchmark_only", "mandatory baseline/control; not promotable standalone"),
        ("market_structure", "funding_rate_change_3obs", "derived_asof", "core39", "benchmark_only", "funding family benchmark/control"),
        # Core3 aggtrades.
        ("aggtrades_core3", "agg_signed_flow_z_24h", "independent_aggtrades", "core3_only", "allowed_core3_only", "order-flow state; not core39-wide"),
        ("aggtrades_core3", "agg_flow_imbalance_notional_24h", "independent_aggtrades", "core3_only", "allowed_core3_only", "signed aggressor flow"),
        ("aggtrades_core3", "agg_large_notional_share_24h", "independent_aggtrades", "core3_only", "allowed_core3_only", "large trade intensity"),
        ("aggtrades_core3", "agg_cross_symbol_signed_flow_share", "derived_cross_symbol_core3", "core3_only", "allowed_core3_only", "core3 relative flow only"),
        ("aggtrades_core3", "agg_notional_accel_4h_vs_24h", "derived_aggtrades", "core3_only", "allowed_core3_only", "flow acceleration"),
    ]
    return pd.DataFrame(rows, columns=["source_family", "field_name", "field_type", "scope", "status", "usage_note"])


def blocked_patterns() -> pd.DataFrame:
    rows = [
        ("static_oi_level_x_realized_vol", "blocked_initial", "A7AD wrong-lag controls dominated static OI x volatility/trend motifs"),
        ("raw_603_column_blind_search", "blocked", "core39 all-features table is derived-wide; field selection required first"),
        ("core3_agg_projected_to_core39", "blocked", "aggTrades coverage is BTC/ETH/SOL only"),
        ("funding_standalone_promotion", "blocked", "funding family remains benchmark/control after A7D/A7B history"),
        ("liquidity_volatility_uncapped", "blocked", "previous A7M/A7O collapse risk"),
    ]
    return pd.DataFrame(rows, columns=["pattern", "status", "reason"])


def next_experiment_contract() -> pd.DataFrame:
    rows = [
        ("A7AF0", "core39 selected-field replay contract", "no replay; build selected field panel/schema and controls"),
        ("A7AF1", "core39 selected-field small controlled smoke", "<=120 candidates; controls mandatory; no May ranking"),
        ("A7AG0", "core3 aggtrades integration contract", "core3-only order-flow diagnostics, separate from core39"),
    ]
    return pd.DataFrame(rows, columns=["stage", "name", "scope"])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    if not A7AE0_AUTH.exists():
        raise FileNotFoundError(A7AE0_AUTH)
    auth0 = json.loads(A7AE0_AUTH.read_text(encoding="utf-8"))
    if not auth0.get("authorizes_field_selection_contract"):
        raise RuntimeError("A7AE0 does not authorize A7AE1")

    fields = selected_field_contract()
    blocked = blocked_patterns()
    next_contract = next_experiment_contract()

    decision = "PASS_A7AE1_FIELD_SELECTION_CONTRACT_READY"
    auth = {
        "decision": decision,
        "authorizes_a7af0_core39_selected_field_contract": True,
        "authorizes_a7af1_replay": False,
        "authorizes_core3_aggtrades_contract": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "selected_fields": int(len(fields)),
        "blocked_patterns": int(len(blocked)),
        "executes_replay": False,
        "executes_search": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }
    fields.to_csv(OUT_DIR / "a7ae1_selected_field_contract.csv", index=False)
    blocked.to_csv(OUT_DIR / "a7ae1_blocked_pattern_registry.csv", index=False)
    next_contract.to_csv(OUT_DIR / "a7ae1_next_experiment_contract.csv", index=False)
    write_json(OUT_DIR / "a7ae1_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ae1_manifest.json", manifest)

    report = f"""# CRYPTO A7AE-1 Field Selection Contract

Generated: {now}

## Decision

```text
{decision}
```

This stage defines which newly received fields can enter controlled experiments. It does not run replay or search.

## Authorization

```json
{json.dumps(auth, indent=2, sort_keys=True)}
```

## Selected Field Contract

{md_table(fields)}

## Blocked Pattern Registry

{md_table(blocked)}

## Next Experiment Contract

{md_table(next_contract)}

## Boundary

- Do not feed all 603 core39 columns into generator/search.
- Keep core39 selected-field smoke separate from core3 aggTrades diagnostics.
- Keep funding as benchmark/control only.
- Static OI level x realized volatility/trend motifs require redesign before any replay because wrong-lag controls dominated A7AD.
- No large search, alpha proof, shadow, paper, or live is authorized.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
