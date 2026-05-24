from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
PANEL_PATH = DATA_ROOT / "gold" / "features" / "binance_core12_all_features_metrics_market_structure_aggtrades_v1_20260524.parquet"
A7AH0_AUTH = ROOT / "runtime" / "a7ah0_core12_aggtrades_final_handoff_audit" / "a7ah0_authorization_matrix.json"

OUT_DIR = ROOT / "runtime" / "a7ai0_core12_aggtrades_experiment_contract"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AI0_CORE12_AGGTRADES_EXPERIMENT_CONTRACT_20260524.md"

CORE12 = [
    "ADAUSDT",
    "AVAXUSDT",
    "BCHUSDT",
    "BNBUSDT",
    "BTCUSDT",
    "DOGEUSDT",
    "ETHUSDT",
    "LINKUSDT",
    "LTCUSDT",
    "SOLUSDT",
    "SUIUSDT",
    "XRPUSDT",
]

SPLITS = [
    ("train_2024", "2024-01-01 00:00:00+00:00", "2024-12-31 23:00:00+00:00", "selection_training_only"),
    ("validation_2025H1", "2025-01-01 00:00:00+00:00", "2025-06-30 23:00:00+00:00", "ranking_allowed_non_may"),
    ("recent_2025H2_2026Apr", "2025-07-01 00:00:00+00:00", "2026-04-30 23:00:00+00:00", "ranking_allowed_non_may"),
    ("may_2026_stress_caveated", "2026-05-01 00:00:00+00:00", "2026-05-20 23:00:00+00:00", "post_selection_stress_only_core3_current_month_caveat"),
]

FIELD_CONTRACT = [
    ("agg_volume_imbalance", "agg_flow_balance", "allowed", "bounded [-1,1] hourly buy/sell volume pressure"),
    ("agg_signed_aggressor_notional", "agg_flow_size", "allowed_with_zscore", "raw notional must be normalized before ranking"),
    ("agg_buy_sell_notional_ratio", "agg_flow_balance", "allowed_with_clip", "ratio can be heavy-tailed; clip/winsor before use"),
    ("agg_large_notional_ratio_100k_plus", "agg_large_trade", "allowed", "large trade notional share"),
    ("agg_large_trade_count_ratio_100k_plus", "agg_large_trade", "allowed", "large trade count share"),
    ("agg_max_trade_notional", "agg_large_trade", "allowed_with_zscore", "raw notional must be normalized"),
    ("agg_price_range_bps", "agg_intrahour_price", "allowed", "hour range from aggTrades"),
    ("agg_close_to_open_bps", "agg_intrahour_price", "allowed", "intra-hour direction proxy"),
    ("agg_vwap", "agg_micro_price", "derive_only", "raw VWAP; use with close price to derive vwap-close bps"),
    ("agg_close_price", "agg_micro_price", "derive_only", "raw close price for derived vwap-close bps"),
    ("agg_buy_vwap", "agg_micro_price", "derive_only", "raw buy VWAP for derived buy-sell VWAP spread"),
    ("agg_sell_vwap", "agg_micro_price", "derive_only", "raw sell VWAP for derived buy-sell VWAP spread"),
    ("agg_trade_count", "agg_trade_structure", "derive_only", "used with underlying trade count"),
    ("agg_underlying_trade_count", "agg_trade_structure", "derive_only", "used to derive avg underlying trades per agg"),
    ("open_interest_change_24h", "positioning_context", "context_only", "interaction context, not aggTrades source"),
    ("mark_index_basis_change_24h", "basis_context", "context_only", "interaction context"),
    ("premium_index_change_24h", "basis_context", "context_only", "interaction context"),
    ("top_long_short_position_ratio_zscore_168h", "crowding_context", "context_only", "interaction context"),
    ("ret_24", "price_context", "context_only", "trend/reversal context"),
    ("funding_rate_bps", "funding_baseline", "baseline_only", "residual/control baseline"),
]

DERIVED_IN_RUNNER = [
    ("ts_zscore_24h", "past-only rolling zscore over 24h"),
    ("ts_zscore_72h", "past-only rolling zscore over 72h"),
    ("ts_delta_4h", "past-only 4h change"),
    ("ts_delta_24h", "past-only 24h change"),
    ("rank_cross_symbol_core12", "cross-sectional rank among symbols with agg availability"),
    ("interaction_mul_context", "agg field x context field; no standalone activity promotion"),
    ("vwap_close_bps", "(agg_vwap / agg_close_price - 1) * 10000, guarded for zero close"),
    ("buy_sell_vwap_spread_bps", "(agg_buy_vwap / agg_sell_vwap - 1) * 10000, guarded for zero sell vwap"),
    ("avg_underlying_trades_per_agg", "agg_underlying_trade_count / agg_trade_count, guarded for zero count"),
]

BLOCKED_PATTERNS = [
    ("blind_654_column_search", "blocked", "wide panel includes non-selected, derived, and benchmark fields"),
    ("standalone_raw_notional_level", "blocked", "size/liquidity level without normalization is capacity/exposure proxy"),
    ("may_tuned_symbol_subset", "blocked", "May agg coverage is core3 current-month caveated only"),
    ("core12_may_stress_claim_without_rem9_may_agg", "blocked", "rem9 has agg through 2026-04 only"),
    ("funding_standalone_promotion", "blocked", "funding remains benchmark/control"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 100) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def availability(df: pd.DataFrame, fields: list[str]) -> pd.DataFrame:
    rows = []
    for field in fields:
        if field not in df.columns:
            rows.append({"field_name": field, "present": False, "core12_non_null_rate": 0.0, "min_symbol_rate": 0.0})
            continue
        part = df[df["symbol"].isin(CORE12)]
        rates = part.groupby("symbol", observed=True)[field].apply(lambda x: x.notna().mean())
        rows.append(
            {
                "field_name": field,
                "present": True,
                "core12_non_null_rate": float(part[field].notna().mean()),
                "min_symbol_rate": float(rates.min()),
                "median_symbol_rate": float(rates.median()),
                "max_symbol_rate": float(rates.max()),
            }
        )
    return pd.DataFrame(rows)


def split_manifest(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for split, start_text, end_text, usage in SPLITS:
        start = pd.Timestamp(start_text)
        end = pd.Timestamp(end_text)
        part = df[df["symbol"].isin(CORE12) & df["timestamp"].between(start, end, inclusive="both")]
        agg_available = pd.to_numeric(part.get("agg_features_available", 0), errors="coerce").fillna(0).gt(0)
        rows.append(
            {
                "split": split,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "usage": usage,
                "rows": int(len(part)),
                "symbols": int(part["symbol"].nunique()),
                "agg_available_rows": int(agg_available.sum()),
                "agg_available_symbol_count": int(part.loc[agg_available, "symbol"].nunique()),
                "may_allowed_for_ranking": False if "may" in split else True,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    auth_prev = json.loads(A7AH0_AUTH.read_text(encoding="utf-8"))
    if not auth_prev.get("authorizes_a7ai0_core12_aggtrades_experiment_contract"):
        raise RuntimeError("A7AH0 does not authorize A7AI0")

    schema = pq.read_schema(PANEL_PATH)
    fields = sorted(set(["symbol", "timestamp", "agg_features_available"] + [x[0] for x in FIELD_CONTRACT]))
    cols = [field for field in fields if field in schema.names]
    df = pd.read_parquet(PANEL_PATH, columns=cols, engine="pyarrow")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    contract = pd.DataFrame(FIELD_CONTRACT, columns=["field_name", "source_family", "status", "usage_note"])
    avail = availability(df, contract["field_name"].tolist())
    contract = contract.merge(avail, on="field_name", how="left")
    splits = split_manifest(df)
    derived = pd.DataFrame(DERIVED_IN_RUNNER, columns=["derived_transform", "rule"])
    blocked = pd.DataFrame(BLOCKED_PATTERNS, columns=["pattern", "status", "reason"])

    blockers = []
    warnings = [
        "final_panel_contains_raw_enhanced_agg_fields_not_precomputed_rolling_cross_symbol_agg_features",
        "may_2026_agg_coverage_is_core3_current_month_caveat_not_core12_monthly_history",
        "A7AI0 is contract only; no replay and no alpha evidence",
    ]
    missing = contract[~contract["present"].fillna(False)]
    if not missing.empty:
        blockers.append("selected_experiment_fields_missing")
    non_may = splits[~splits["split"].str.contains("may")]
    if int(non_may["agg_available_symbol_count"].min()) < 12:
        blockers.append("non_may_split_does_not_have_core12_agg_availability")

    decision = "PASS_A7AI0_CORE12_AGGTRADES_EXPERIMENT_CONTRACT_READY" if not blockers else "HOLD_A7AI0_CORE12_AGGTRADES_EXPERIMENT_CONTRACT_BLOCKED"
    auth = {
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "authorizes_a7ai1_small_controlled_raw_agg_smoke": decision.startswith("PASS_"),
        "authorizes_direct_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_policy": "May is post-selection stress only and is core3-current-month caveated; do not rank or tune on it",
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "panel_path": str(PANEL_PATH),
        "core12_rows": int(df[df["symbol"].isin(CORE12)].shape[0]),
        "field_count": int(len(contract)),
        "executes_replay": False,
        "executes_search": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }

    contract.to_csv(OUT_DIR / "a7ai0_experiment_field_contract.csv", index=False)
    splits.to_csv(OUT_DIR / "a7ai0_split_manifest.csv", index=False)
    derived.to_csv(OUT_DIR / "a7ai0_derived_in_runner_contract.csv", index=False)
    blocked.to_csv(OUT_DIR / "a7ai0_blocked_pattern_registry.csv", index=False)
    write_json(OUT_DIR / "a7ai0_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ai0_manifest.json", manifest)

    report = f"""# CRYPTO A7AI-0 Core12 aggTrades Experiment Contract

Generated: {now}

## Decision

```text
{decision}
```

This stage defines the controlled experiment contract for the accepted core12 aggTrades handoff. It does not run replay and does not run search.

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

## Experiment Field Contract

{md_table(contract)}

## Derived-In-Runner Contract

{md_table(derived)}

## Blocked Pattern Registry

{md_table(blocked)}

## Boundary

- Use selected aggTrades fields only; no blind 654-column search.
- Raw notional/size fields require zscore/rank/normalization before use.
- May 2026 agg coverage is not full core12 monthly history and cannot be used for ranking/tuning.
- Funding remains baseline/control only.
- No direct formula search, large search, alpha proof, shadow, paper, or live is authorized.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
