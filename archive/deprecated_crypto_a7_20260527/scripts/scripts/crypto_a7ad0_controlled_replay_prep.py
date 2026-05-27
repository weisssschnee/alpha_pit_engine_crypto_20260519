from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
PANEL_PATH = DATA_ROOT / "gold" / "panels" / "crypto_core48_1h_with_metrics_candidate_v1.parquet"
A7AC3_MANIFEST = ROOT / "runtime" / "a7ac3_core48_panel_integrity_audit" / "a7ac3_manifest.json"

OUT_DIR = ROOT / "runtime" / "a7ad0_controlled_replay_prep"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AD0_CONTROLLED_REPLAY_PREP_20260522.md"

COMMON_WINDOW_START = pd.Timestamp("2024-03-16 12:00:00", tz="UTC")
COMMON_WINDOW_END = pd.Timestamp("2026-04-30 23:00:00", tz="UTC")

SPLITS = [
    ("train_2024_common", pd.Timestamp("2024-03-16 12:00:00", tz="UTC"), pd.Timestamp("2024-12-31 23:00:00", tz="UTC")),
    ("validation_2025H1", pd.Timestamp("2025-01-01 00:00:00", tz="UTC"), pd.Timestamp("2025-06-30 23:00:00", tz="UTC")),
    ("recent_2025H2_2026Apr", pd.Timestamp("2025-07-01 00:00:00", tz="UTC"), pd.Timestamp("2026-04-30 23:00:00", tz="UTC")),
]

FEATURE_FAMILIES: dict[str, list[str]] = {
    "market_ohlcv_return": [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_asset_volume",
        "number_of_trades",
        "ret_1",
        "ret_3",
        "ret_6",
        "ret_12",
        "ret_24",
        "realized_vol_6",
        "realized_vol_12",
        "realized_vol_24",
    ],
    "mark_index_basis_premium": [
        "mark_close",
        "index_close",
        "mark_index_ratio",
        "mark_minus_index",
        "premium_index",
        "spot_perp_basis",
    ],
    "funding_observable": [
        "latest_known_funding_rate",
        "funding_rate_z_24",
        "funding_rate_sign",
        "funding_rate_persistence_3",
    ],
    "binance_metrics_positioning": [
        "open_interest",
        "open_interest_value",
        "global_long_short_account_ratio",
        "top_long_short_account_ratio",
        "top_long_short_position_ratio",
        "taker_buy_sell_volume_ratio",
        "open_interest_change_1h",
        "open_interest_change_4h",
        "open_interest_change_24h",
        "open_interest_zscore_168h",
        "open_interest_value_zscore_168h",
        "global_long_short_account_ratio_zscore_168h",
        "top_long_short_account_ratio_zscore_168h",
        "top_long_short_position_ratio_zscore_168h",
        "taker_buy_sell_volume_ratio_zscore_168h",
    ],
    "aggtrades_core_subset_only": [
        "agg_features_available",
        "agg_notional",
        "agg_trade_count",
        "agg_signed_aggressor_notional",
        "agg_volume_imbalance",
        "agg_flow_imbalance_notional_24h",
        "agg_signed_flow_z_24h",
        "agg_large_notional_share_24h",
        "agg_cross_symbol_signed_flow_share",
    ],
}

REQUIRED_CORE48_FAMILIES = [
    "market_ohlcv_return",
    "mark_index_basis_premium",
    "funding_observable",
    "binance_metrics_positioning",
]

FAMILY_REQUIRED_COLUMNS: dict[str, list[str]] = {
    "market_ohlcv_return": ["open", "high", "low", "close", "quote_asset_volume", "number_of_trades", "ret_24", "realized_vol_24"],
    "mark_index_basis_premium": ["mark_close", "index_close", "mark_index_ratio", "mark_minus_index", "premium_index"],
    "funding_observable": ["latest_known_funding_rate", "funding_rate_sign", "funding_rate_persistence_3"],
    "binance_metrics_positioning": [
        "open_interest",
        "open_interest_value",
        "global_long_short_account_ratio",
        "top_long_short_account_ratio",
        "top_long_short_position_ratio",
        "taker_buy_sell_volume_ratio",
    ],
    "aggtrades_core_subset_only": ["agg_features_available"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def md_table(df: pd.DataFrame, max_rows: int = 60) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def load_a7ac3() -> dict[str, Any]:
    if not A7AC3_MANIFEST.exists():
        return {"decision": "MISSING_A7AC3_MANIFEST"}
    return json.loads(A7AC3_MANIFEST.read_text(encoding="utf-8"))


def split_manifest(df: pd.DataFrame, symbols: list[str]) -> pd.DataFrame:
    rows = []
    for split_name, start, end in SPLITS:
        mask = df["timestamp"].between(start, end, inclusive="both") & df["core48_common_window_eligible"].eq(True)
        part = df.loc[mask]
        rows.append(
            {
                "split": split_name,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "rows": int(len(part)),
                "symbols": int(part["symbol"].nunique()),
                "expected_rows": int(len(symbols) * (int((end - start) / pd.Timedelta(hours=1)) + 1)),
                "complete": bool(len(part) == len(symbols) * (int((end - start) / pd.Timedelta(hours=1)) + 1)),
                "feature_time_rule": "feature_available_time = bar timestamp + 1h",
                "execution_rule": "execution_time >= next 1h bar open",
                "label_rule": "label_start_time = execution_time; label_end_time depends on tested horizon",
            }
        )
    return pd.DataFrame(rows)


def universe_manifest(df: pd.DataFrame) -> pd.DataFrame:
    common = df[df["core48_common_window_eligible"].eq(True)].copy()
    grouped = common.groupby("symbol", observed=True)
    rows = []
    for symbol, part in grouped:
        track = str(part["track"].dropna().iloc[0]) if "track" in part and part["track"].notna().any() else ""
        tier = str(part["tier"].dropna().iloc[0]) if "tier" in part and part["tier"].notna().any() else ""
        rows.append(
            {
                "symbol": symbol,
                "track": track,
                "tier": tier,
                "common_window_rows": int(len(part)),
                "timestamp_min": str(part["timestamp"].min()),
                "timestamp_max": str(part["timestamp"].max()),
                "market_price_available_rate": clean_float(part["close"].notna().mean()) if "close" in part else None,
                "funding_available_rate": clean_float(part["latest_known_funding_rate"].notna().mean()) if "latest_known_funding_rate" in part else None,
                "metrics_available_rate": clean_float(part["metrics_features_available"].fillna(False).mean()) if "metrics_features_available" in part else None,
                "agg_available_rate": clean_float(part["agg_features_available"].fillna(False).mean()) if "agg_features_available" in part else None,
            }
        )
    return pd.DataFrame(rows).sort_values(["track", "symbol"]).reset_index(drop=True)


def feature_family_availability(df: pd.DataFrame, symbols: list[str]) -> pd.DataFrame:
    common = df[df["core48_common_window_eligible"].eq(True)].copy()
    rows = []
    for family, cols in FEATURE_FAMILIES.items():
        present = [c for c in cols if c in common.columns]
        missing = [c for c in cols if c not in common.columns]
        required_cols = FAMILY_REQUIRED_COLUMNS.get(family, cols)
        required_present = [c for c in required_cols if c in common.columns]
        required_missing = [c for c in required_cols if c not in common.columns]
        symbol_rates = []
        required_symbol_rates = []
        for _, part in common.groupby("symbol", observed=True):
            if not present:
                symbol_rates.append(0.0)
            else:
                rates = [float(part[c].notna().mean()) for c in present if c in part.columns]
                symbol_rates.append(min(rates) if rates else 0.0)
            if not required_present:
                required_symbol_rates.append(0.0)
            else:
                req_rates = [float(part[c].notna().mean()) for c in required_present if c in part.columns]
                required_symbol_rates.append(min(req_rates) if req_rates else 0.0)
        rows.append(
            {
                "feature_family": family,
                "columns_expected": len(cols),
                "columns_present": len(present),
                "missing_columns": ";".join(missing),
                "required_columns": ";".join(required_cols),
                "required_missing_columns": ";".join(required_missing),
                "required_common_non_null_rate_min_symbol": clean_float(min(required_symbol_rates) if required_symbol_rates else 0.0),
                "required_common_non_null_rate_median_symbol": clean_float(pd.Series(required_symbol_rates).median() if required_symbol_rates else 0.0),
                "common_non_null_rate_min_symbol": clean_float(min(symbol_rates) if symbol_rates else 0.0),
                "common_non_null_rate_median_symbol": clean_float(pd.Series(symbol_rates).median() if symbol_rates else 0.0),
                "symbols_with_family_rate_ge_95pct": int(sum(rate >= 0.95 for rate in symbol_rates)),
                "symbols_with_required_rate_ge_95pct": int(sum(rate >= 0.95 for rate in required_symbol_rates)),
                "symbols_total": len(symbols),
                "core48_first_smoke_allowed": family in REQUIRED_CORE48_FAMILIES,
                "usage_note": (
                    "allowed for A7AD core48 small controlled replay prep"
                    if family in REQUIRED_CORE48_FAMILIES
                    else "not allowed in first core48 replay; aggtrades coverage is core subset only"
                ),
            }
        )
    return pd.DataFrame(rows)


def metadata_timing_audit(df: pd.DataFrame) -> pd.DataFrame:
    common = df[df["core48_common_window_eligible"].eq(True)].copy()
    rows = []
    for field in ["feature_available_time", "metrics_feature_available_time"]:
        if field not in common.columns:
            rows.append({"field": field, "present": False, "non_null_rate": 0.0, "matches_timestamp_plus_1h_rate": None, "note": "missing"})
            continue
        values = pd.to_datetime(common[field], utc=True, errors="coerce")
        expected = common["timestamp"] + pd.Timedelta(hours=1)
        rows.append(
            {
                "field": field,
                "present": True,
                "non_null_rate": clean_float(values.notna().mean()),
                "matches_timestamp_plus_1h_rate": clean_float((values.eq(expected) & values.notna()).mean()),
                "note": (
                    "primary timing contract field"
                    if field == "feature_available_time"
                    else "supplemental metadata; incomplete on primary additions, do not use as replay gate"
                ),
            }
        )
    return pd.DataFrame(rows)


def candidate_family_contract() -> pd.DataFrame:
    rows = [
        {
            "family_id": "F0",
            "family_name": "low_turnover_price_basis",
            "allowed_fields": "ret_12;ret_24;realized_vol_24;mark_index_ratio;premium_index",
            "purpose": "baseline non-funding price/basis family with low-turnover bias",
            "a7ad1_quota_hint": 80,
        },
        {
            "family_id": "F1",
            "family_name": "funding_residual_controls",
            "allowed_fields": "latest_known_funding_rate;funding_rate_z_24;funding_rate_persistence_3",
            "purpose": "mandatory benchmark/control; cannot promote by itself",
            "a7ad1_quota_hint": 48,
        },
        {
            "family_id": "F2",
            "family_name": "metrics_crowding_oi_interaction",
            "allowed_fields": "open_interest;open_interest_change_24h;open_interest_zscore_168h;global_long_short_account_ratio;top_long_short_position_ratio;taker_buy_sell_volume_ratio",
            "purpose": "new independent historical metrics source interaction smoke",
            "a7ad1_quota_hint": 120,
        },
        {
            "family_id": "F3",
            "family_name": "cross_symbol_relative_strength",
            "allowed_fields": "ret_24;quote_asset_volume;open_interest_value;market_cap/liquidity tier proxies",
            "purpose": "cross-sectional core48 relative structure, not single-symbol trend",
            "a7ad1_quota_hint": 80,
        },
        {
            "family_id": "F4",
            "family_name": "volatility_liquidity_capped",
            "allowed_fields": "realized_vol_24;quote_asset_volume;number_of_trades;open_interest_value",
            "purpose": "allowed only under family cap because previous searches collapsed into liquidity-volatility motifs",
            "a7ad1_quota_hint": 40,
        },
        {
            "family_id": "F5",
            "family_name": "placebo_null_controls",
            "allowed_fields": "row_shuffle;time_shuffle;sign_flip;wrong_lag_stale;random_placebo",
            "purpose": "negative controls; must be zero promotable",
            "a7ad1_quota_hint": 72,
        },
    ]
    return pd.DataFrame(rows)


def negative_control_contract() -> pd.DataFrame:
    controls = [
        ("sign_flip", "same formula with inverted sign; should not pass as comparable candidate"),
        ("row_shuffle", "symbol-row shuffled within split; detects cross-sectional artifact"),
        ("time_shuffle", "time shuffled signal; detects temporal leakage or static exposure"),
        ("wrong_lag_stale_24h", "stale/wrong-lag control; previous A7O blocker, must be explicitly dominated"),
        ("random_placebo", "seeded random signal matched to universe/split"),
    ]
    return pd.DataFrame(
        [
            {
                "control_mode": mode,
                "description": desc,
                "promotion_allowed": False,
                "dominance_rule": "candidate robust score must exceed matched controls; any control research-like pass blocks cell/family",
            }
            for mode, desc in controls
        ]
    )


def cost_lag_contract() -> pd.DataFrame:
    rows = []
    for cost_bps in [10, 20, 30]:
        for lag_bars in [0, 1, 2]:
            rows.append(
                {
                    "cost_bps": cost_bps,
                    "lag_bars": lag_bars,
                    "required_in_a7ad1": cost_bps in {10, 20} and lag_bars in {0, 1},
                    "usage": "primary" if cost_bps == 10 and lag_bars == 0 else "stress",
                    "execution_rule": "signal at hour close; position no earlier than next eligible hourly bar plus lag_bars",
                }
            )
    return pd.DataFrame(rows)


def baseline_residual_contract() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "baseline_id": "FundingCore_proxy_core48",
                "formula": "Rank(latest_known_funding_rate) / ZScore(latest_known_funding_rate) variants",
                "role": "mandatory residual baseline and benchmark, not promotable candidate",
                "required": True,
            },
            {
                "baseline_id": "Core4_research_benchmark",
                "formula": "legacy Core4 motif family where fields exist; benchmark only",
                "role": "residual/control benchmark; not alpha proof and not shadow proof",
                "required": True,
            },
            {
                "baseline_id": "market_beta_price_momentum",
                "formula": "ret_12 / ret_24 cross-sectional rank",
                "role": "simple price baseline",
                "required": True,
            },
            {
                "baseline_id": "metrics_standalone",
                "formula": "open_interest / long-short / taker-ratio single-source standalone baselines",
                "role": "test whether interactions add information beyond independent metrics source",
                "required": True,
            },
        ]
    )


def authorization_matrix(decision: str, blockers: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "authorizes_a7ad1_small_controlled_replay_smoke": decision.startswith("PASS_"),
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_a7o_l1_or_a7m_large_continuation": False,
        "may_policy": {
            "core48_common_panel_has_may_stress": False,
            "may_use": "not available for core48 common proof; when available after monthly backfill, stress-only/post-selection only",
            "may_for_ranking": False,
            "may_for_generation": False,
            "may_for_weight_selection": False,
            "may_for_threshold_tuning": False,
        },
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    a7ac3 = load_a7ac3()

    df = pd.read_parquet(PANEL_PATH, engine="pyarrow")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    symbols = sorted(df["symbol"].dropna().astype(str).unique().tolist())
    common = df[df["core48_common_window_eligible"].eq(True)].copy()

    duplicate_keys = int(df.duplicated(["symbol", "timestamp"]).sum())
    common_duplicate_keys = int(common.duplicated(["symbol", "timestamp"]).sum())
    common_symbols = sorted(common["symbol"].dropna().astype(str).unique().tolist())
    common_rows_expected = len(common_symbols) * (int((COMMON_WINDOW_END - COMMON_WINDOW_START) / pd.Timedelta(hours=1)) + 1)

    splits = split_manifest(df, common_symbols)
    universe = universe_manifest(df)
    availability = feature_family_availability(df, common_symbols)
    timing = metadata_timing_audit(df)
    family_contract = candidate_family_contract()
    controls = negative_control_contract()
    cost_lag = cost_lag_contract()
    baselines = baseline_residual_contract()

    blockers: list[str] = []
    warnings: list[str] = []
    if a7ac3.get("decision") != "PASS_A7AC3_CORE48_PANEL_READY_FOR_CONTROLLED_REPLAY_PREP":
        blockers.append("a7ac3_not_passed")
    if duplicate_keys or common_duplicate_keys:
        blockers.append("duplicate_symbol_timestamp_keys")
    if len(common_symbols) != 48:
        blockers.append("core48_common_symbol_count_not_48")
    if len(common) != common_rows_expected:
        blockers.append("core48_common_window_row_count_incomplete")
    if not bool(splits["complete"].all()):
        blockers.append("split_row_count_incomplete")
    required_availability = availability[availability["feature_family"].isin(REQUIRED_CORE48_FAMILIES)]
    if (required_availability["required_common_non_null_rate_min_symbol"] < 0.95).any():
        blockers.append("required_feature_family_common_availability_below_95pct")
    optional_sparse = required_availability[
        required_availability["common_non_null_rate_min_symbol"] < required_availability["required_common_non_null_rate_min_symbol"]
    ]
    if not optional_sparse.empty:
        warnings.append("optional_derived_or_spot_fields_sparse_use_required_columns_for_a7ad1")

    metric_time_row = timing[timing["field"].eq("metrics_feature_available_time")]
    if not metric_time_row.empty and float(metric_time_row["non_null_rate"].iloc[0]) < 0.95:
        warnings.append("metrics_feature_available_time_metadata_incomplete_use_panel_timestamp_plus_1h_contract")
    agg_family = availability[availability["feature_family"].eq("aggtrades_core_subset_only")]
    if not agg_family.empty and int(agg_family["symbols_with_family_rate_ge_95pct"].iloc[0]) < 48:
        warnings.append("aggtrades_features_not_core48_wide_excluded_from_first_core48_smoke")

    decision = "PASS_A7AD0_CONTROLLED_REPLAY_PREP_READY" if not blockers else "HOLD_A7AD0_CONTROLLED_REPLAY_PREP_BLOCKED"
    auth = authorization_matrix(decision, blockers, warnings)
    manifest = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "input_panel": str(PANEL_PATH),
        "input_panel_sha256": file_sha256(PANEL_PATH),
        "input_rows": int(len(df)),
        "input_columns": int(len(df.columns)),
        "input_symbols": int(len(symbols)),
        "timestamp_min": str(df["timestamp"].min()),
        "timestamp_max": str(df["timestamp"].max()),
        "common_window_start": COMMON_WINDOW_START.isoformat(),
        "common_window_end": COMMON_WINDOW_END.isoformat(),
        "common_window_rows": int(len(common)),
        "common_window_expected_rows": int(common_rows_expected),
        "common_window_symbols": int(len(common_symbols)),
        "duplicate_keys": duplicate_keys,
        "common_duplicate_keys": common_duplicate_keys,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_a7ad1_small_controlled_replay_smoke": auth["authorizes_a7ad1_small_controlled_replay_smoke"],
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }

    splits.to_csv(OUT_DIR / "a7ad0_split_manifest.csv", index=False)
    universe.to_csv(OUT_DIR / "a7ad0_replay_universe.csv", index=False)
    availability.to_csv(OUT_DIR / "a7ad0_feature_family_availability.csv", index=False)
    timing.to_csv(OUT_DIR / "a7ad0_timing_metadata_audit.csv", index=False)
    family_contract.to_csv(OUT_DIR / "a7ad0_candidate_family_contract.csv", index=False)
    controls.to_csv(OUT_DIR / "a7ad0_negative_control_contract.csv", index=False)
    cost_lag.to_csv(OUT_DIR / "a7ad0_cost_lag_contract.csv", index=False)
    baselines.to_csv(OUT_DIR / "a7ad0_baseline_residual_contract.csv", index=False)
    write_json(OUT_DIR / "a7ad0_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ad0_manifest.json", manifest)

    report = f"""# CRYPTO A7AD-0 Controlled Replay Prep

Generated: {now}

## Decision

```text
{decision}
```

This stage does not run replay and does not run formula search. It prepares the core48 panel for a small controlled replay smoke only.

## Input Panel

```text
panel: {PANEL_PATH}
sha256: {manifest['input_panel_sha256']}
rows: {manifest['input_rows']}
columns: {manifest['input_columns']}
symbols: {manifest['input_symbols']}
timestamp range: {manifest['timestamp_min']} .. {manifest['timestamp_max']}
common window: {manifest['common_window_start']} .. {manifest['common_window_end']}
common rows: {manifest['common_window_rows']} / {manifest['common_window_expected_rows']}
duplicate keys: {duplicate_keys}
```

## Authorization

```json
{json.dumps(auth, indent=2, sort_keys=True)}
```

## Split Manifest

{md_table(splits)}

## Feature Family Availability

{md_table(availability)}

## Timing Metadata Audit

{md_table(timing)}

Replay contract uses `feature_available_time = timestamp + 1h` and `execution_time >= next 1h bar`.
`metrics_feature_available_time` is supplemental metadata and is not used as the replay gate because it is incomplete on primary additions.

## Candidate Family Contract

{md_table(family_contract)}

## Negative Control Contract

{md_table(controls)}

## Cost / Lag Contract

{md_table(cost_lag)}

## Baseline / Residual Contract

{md_table(baselines)}

## Replay Boundary

- Use only rows where `core48_common_window_eligible = true`.
- May 2026 is not part of the core48 common proof panel. When monthly 2026-05 data is backfilled, May remains stress-only and cannot enter ranking, generation, threshold tuning, weight selection, or authorization.
- `aggtrades_core_subset_only` is excluded from the first core48 small replay because it is not core48-wide.
- FundingCore/Core4 remain benchmarks/residual baselines, not promotable candidates.
- A7AD-1, if run, must remain a small controlled smoke and must include matched negative controls.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
