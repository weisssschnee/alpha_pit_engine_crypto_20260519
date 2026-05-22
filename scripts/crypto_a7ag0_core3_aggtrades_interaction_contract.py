from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
PANEL_PATH = DATA_ROOT / "gold" / "features" / "binance_core3_all_features_metrics_market_structure_aggtrades_v1.parquet"
A7AF2_AUTH = ROOT / "runtime" / "a7af2_selected_field_failure_forensic" / "a7af2_authorization_matrix.json"

OUT_DIR = ROOT / "runtime" / "a7ag0_core3_aggtrades_interaction_contract"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AG0_CORE3_AGGTRADES_INTERACTION_CONTRACT_20260522.md"

SPLITS = [
    ("train_2024", "2024-01-01 00:00:00+00:00", "2024-12-31 23:00:00+00:00", "selection_training_only"),
    ("validation_2025H1", "2025-01-01 00:00:00+00:00", "2025-06-30 23:00:00+00:00", "ranking_allowed_non_may"),
    ("recent_2025H2_2026Apr", "2025-07-01 00:00:00+00:00", "2026-04-30 23:00:00+00:00", "ranking_allowed_non_may"),
    ("may_2026_stress", "2026-05-01 00:00:00+00:00", "2026-05-20 23:00:00+00:00", "post_selection_stress_only"),
]

BASE_FIELDS = ["symbol", "timestamp", "ret_1", "ret_24"]

FIELD_CONTRACT = [
    ("agg_signed_flow_z_24h", "aggtrades_flow", "state_interaction_allowed", "signed aggressor flow shock; not standalone alpha"),
    ("agg_flow_imbalance_notional_24h", "aggtrades_flow", "state_interaction_allowed", "24h buy/sell pressure balance"),
    ("agg_large_notional_share_24h", "aggtrades_large_trade", "state_interaction_allowed", "large trade share, capped as context"),
    ("agg_cross_symbol_signed_flow_share", "aggtrades_cross_symbol", "state_interaction_allowed", "core3 relative signed flow share"),
    ("agg_notional_accel_4h_vs_24h", "aggtrades_activity", "state_interaction_allowed", "activity acceleration; standalone blocked"),
    ("agg_flow_accel_4h_vs_24h", "aggtrades_flow", "state_interaction_allowed", "signed flow acceleration"),
    ("agg_large_notional_share_4h", "aggtrades_large_trade", "state_interaction_allowed", "shorter large-trade pressure"),
    ("agg_cross_symbol_large_notional_share", "aggtrades_cross_symbol", "state_interaction_allowed", "large trade cross-symbol share"),
    ("mark_index_basis_change_24h", "basis_market_structure", "interaction_context_allowed", "basis dynamic context"),
    ("premium_index_change_24h", "basis_market_structure", "interaction_context_allowed", "premium dynamic context"),
    ("open_interest_change_24h", "positioning", "interaction_context_allowed", "positioning pressure context"),
    ("top_long_short_position_ratio_zscore_168h", "positioning_crowding", "interaction_context_allowed", "crowding context"),
    ("flow_pressure_score_v1", "derived_existing_flow", "benchmark_context_only", "existing derived flow benchmark, not independent source"),
]

BLOCKED_PATTERNS = [
    ("agg_activity_liquidity_self_reproduction", "blocked", "A7V rejected activity/liquidity clue family after source trace pass"),
    ("raw_agg_notional_or_trade_count_standalone", "blocked", "standalone activity level can be control-contaminated and May-fragile"),
    ("core3_agg_projected_to_core39", "blocked", "aggTrades panel covers BTC/ETH/SOL only"),
    ("may_tuned_symbol_specific_btc_eth_sol_rule", "blocked", "May is stress-only and cannot tune symbol weights"),
    ("blind_699_column_search", "blocked", "wide table includes derived fields; selected contract required"),
]


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


def split_manifest(df: pd.DataFrame, symbols: list[str]) -> pd.DataFrame:
    rows = []
    for name, start_text, end_text, usage in SPLITS:
        start = pd.Timestamp(start_text)
        end = pd.Timestamp(end_text)
        part = df[df["timestamp"].between(start, end, inclusive="both")]
        expected_hours = int((end - start) / pd.Timedelta(hours=1)) + 1
        expected_rows = expected_hours * len(symbols)
        rows.append(
            {
                "split": name,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "usage": usage,
                "rows": int(len(part)),
                "symbols": int(part["symbol"].nunique()),
                "expected_rows_if_full": int(expected_rows),
                "row_coverage": len(part) / expected_rows if expected_rows else None,
                "may_allowed_for_ranking": False if "may" in name else True,
                "feature_time_rule": "aggTrades 1h bucket feature available only after hour close",
                "execution_rule": "execution_time >= next 1h bar; lag stress required",
            }
        )
    return pd.DataFrame(rows)


def availability(df: pd.DataFrame, fields: list[str]) -> pd.DataFrame:
    rows = []
    for field in fields:
        if field not in df.columns:
            rows.append({"field_name": field, "present": False, "non_null_rate": 0.0, "min_symbol_rate": 0.0, "median_symbol_rate": 0.0})
            continue
        rates = df.groupby("symbol", observed=True)[field].apply(lambda x: x.notna().mean())
        rows.append(
            {
                "field_name": field,
                "present": True,
                "non_null_rate": float(df[field].notna().mean()),
                "min_symbol_rate": float(rates.min()),
                "median_symbol_rate": float(rates.median()),
                "max_symbol_rate": float(rates.max()),
            }
        )
    return pd.DataFrame(rows)


def split_availability(df: pd.DataFrame, fields: list[str]) -> pd.DataFrame:
    rows = []
    for split, start_text, end_text, _usage in SPLITS:
        part = df[df["timestamp"].between(pd.Timestamp(start_text), pd.Timestamp(end_text), inclusive="both")]
        for field in fields:
            if field not in part.columns:
                rate = 0.0
            else:
                rate = float(part[field].notna().mean())
            rows.append({"split": split, "field_name": field, "non_null_rate": rate})
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    auth_prev = json.loads(A7AF2_AUTH.read_text(encoding="utf-8"))
    if not auth_prev.get("authorizes_a7ag0_core3_aggtrades_contract"):
        raise RuntimeError("A7AF2 does not authorize A7AG0")

    schema = pq.read_schema(PANEL_PATH)
    schema_names = set(schema.names)
    contract = pd.DataFrame(FIELD_CONTRACT, columns=["field_name", "source_family", "status", "usage_note"])
    fields = sorted(set(BASE_FIELDS + contract["field_name"].tolist() + ["agg_features_available"]))
    present_fields = [field for field in fields if field in schema_names]
    df = pd.read_parquet(PANEL_PATH, columns=present_fields, engine="pyarrow")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values(["timestamp", "symbol"]).reset_index(drop=True)
    symbols = sorted(df["symbol"].dropna().unique().tolist())

    duplicate_keys = int(df.duplicated(["symbol", "timestamp"]).sum())
    splits = split_manifest(df, symbols)
    field_avail = availability(df, fields)
    split_avail = split_availability(df, fields)
    contract = contract.merge(field_avail, on="field_name", how="left")
    blocked = pd.DataFrame(BLOCKED_PATTERNS, columns=["pattern", "status", "reason"])

    agg_available = df.get("agg_features_available")
    agg_available_rate = float(pd.to_numeric(agg_available, errors="coerce").fillna(0.0).mean()) if agg_available is not None else 0.0
    blockers = []
    warnings = []
    if symbols != ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        blockers.append("unexpected_symbol_set")
    if duplicate_keys:
        blockers.append("duplicate_symbol_timestamp")
    missing_fields = contract[~contract["present"].fillna(False)]
    if not missing_fields.empty:
        blockers.append("selected_aggtrades_contract_fields_missing")
    low_avail = contract[contract["min_symbol_rate"].fillna(0.0) < 0.90]
    if not low_avail.empty:
        warnings.append("some_selected_fields_have_below_90pct_min_symbol_availability")
    if agg_available_rate < 0.95:
        warnings.append("agg_features_available_rate_below_95pct")
    warnings.append("A7AG0 is a contract only; no replay and no alpha evidence")
    warnings.append("A7V activity/liquidity standalone family remains rejected")

    decision = "PASS_A7AG0_CORE3_AGGTRADES_INTERACTION_CONTRACT_READY" if not blockers else "HOLD_A7AG0_CORE3_AGGTRADES_INTERACTION_CONTRACT_BLOCKED"
    auth = {
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "authorizes_a7ag1_small_controlled_interaction_smoke": decision.startswith("PASS_"),
        "authorizes_aggtrades_standalone_activity_expansion": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_policy": "May 2026 stress-only; not ranking, field selection, symbol weighting, or threshold tuning",
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "panel": str(PANEL_PATH),
        "rows": int(len(df)),
        "columns_read": int(len(present_fields)),
        "symbols": symbols,
        "timestamp_min": str(df["timestamp"].min()),
        "timestamp_max": str(df["timestamp"].max()),
        "duplicate_keys": duplicate_keys,
        "agg_features_available_rate": agg_available_rate,
        "executes_replay": False,
        "executes_search": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }

    splits.to_csv(OUT_DIR / "a7ag0_split_manifest.csv", index=False)
    field_avail.to_csv(OUT_DIR / "a7ag0_field_availability.csv", index=False)
    split_avail.to_csv(OUT_DIR / "a7ag0_split_field_availability.csv", index=False)
    contract.to_csv(OUT_DIR / "a7ag0_interaction_field_contract.csv", index=False)
    blocked.to_csv(OUT_DIR / "a7ag0_blocked_pattern_registry.csv", index=False)
    write_json(OUT_DIR / "a7ag0_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ag0_manifest.json", manifest)

    report = f"""# CRYPTO A7AG-0 Core3 aggTrades Interaction Contract

Generated: {now}

## Decision

```text
{decision}
```

This stage validates the core3 aggTrades-enhanced panel for a small interaction smoke. It does not run replay and does not run search.

## Summary

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Authorization

```json
{json.dumps(auth, indent=2, sort_keys=True)}
```

## Split Manifest

{md_table(splits)}

## Interaction Field Contract

{md_table(contract)}

## Field Availability

{md_table(field_avail)}

## Blocked Pattern Registry

{md_table(blocked)}

## Boundary

- Core3 aggTrades fields cover BTCUSDT, ETHUSDT, and SOLUSDT only.
- aggTrades activity/liquidity standalone family remains blocked by A7V.
- A7AG-1, if run, must use aggTrades only as interaction/state inputs.
- May is stress-only and cannot tune symbols, weights, thresholds, generation, or ranking.
- No formula search, large search, alpha proof, shadow, paper, or live is authorized.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
