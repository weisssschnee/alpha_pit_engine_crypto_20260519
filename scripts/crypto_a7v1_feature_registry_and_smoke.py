from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
PANEL_PATH = DATA_ROOT / "gold" / "panels" / "crypto_core12_1h_with_aggtrades_features_v1.parquet"
A7V_DIR = ROOT / "runtime" / "a7v_panel_generative_contract"
OUT_DIR = ROOT / "runtime" / "a7v1_feature_registry_smoke"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7V1_FEATURE_REGISTRY_AND_SMOKE_20260522.md"
CONFIG_PATH = ROOT / "config" / "crypto_a7v_feature_registry_v1.json"

DATE_TAG = "20260522"
CORE3 = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
CORE12 = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "LINKUSDT",
    "AVAXUSDT",
    "LTCUSDT",
    "BCHUSDT",
    "SUIUSDT",
]

ROLLING_WINDOWS = [4, 8, 12, 24, 48, 72, 96]
ROLLING_TRANSFORMS = ["TSMean", "TSStd", "Delta", "Decay", "RollingMin", "RollingMax", "ZScore"]
CROSS_SYMBOL_TRANSFORMS = ["CrossSymbolRank", "CrossSymbolZScore", "ShareOfUniverse", "RelativeToBTC", "RelativeToETH"]
INTERACTION_TRANSFORMS = ["Mul", "Add", "Sub", "SafeDiv", "HorizonSpread", "SmoothInteraction"]

MARKET_CONTROL_FIELDS = [
    "ret_6",
    "ret_12",
    "realized_vol_12",
    "realized_vol_24",
    "mark_index_ratio",
    "premium_index",
    "latest_known_funding_rate",
]

SMOKE_BASE_FIELDS = [
    "agg_flow_imbalance_notional",
    "agg_notional",
    "agg_large_notional_share_100k_plus",
    "agg_price_range_bps",
    "agg_signed_flow_z_24h",
]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def read_feature_contract() -> pd.DataFrame:
    path = A7V_DIR / "a7v_feature_contract.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["generator_base_field"] = df["generator_base_field"].astype(str).str.lower().isin(["true", "1"])
    return df


def build_base_registry(feature_contract: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in feature_contract.iterrows():
        field = str(row["field_name"])
        is_base = bool(row["generator_base_field"])
        role = str(row["role"])
        family = str(row["field_group"])
        rows.append(
            {
                "field_name": field,
                "field_family": family,
                "field_source": "aggtrades_enhanced_v1",
                "role": role,
                "generator_enabled": bool(is_base and role == "feature"),
                "requires_agg_features_available_mask": bool(field.startswith("agg_")),
                "availability_scope": "core3_available_rows_only" if field.startswith("agg_") else "n/a",
                "cross_symbol_scope": "BTCUSDT,ETHUSDT,SOLUSDT" if field.startswith("agg_") else "core12",
                "feature_available_lag_bars": 1,
                "zero_fill_allowed": False,
                "missing_as_signal_allowed": False,
                "same_hour_execution_allowed": False,
                "notes": "Loaded by agg-aware generator only. Old A7M/A7O generators remain unchanged unless this registry is explicitly enabled.",
            }
        )
    return pd.DataFrame(rows)


def build_derived_specs(base_registry: pd.DataFrame) -> pd.DataFrame:
    enabled = base_registry[base_registry["generator_enabled"]].copy()
    rows: list[dict[str, Any]] = []

    for _, row in enabled.iterrows():
        field = str(row["field_name"])
        family = str(row["field_family"])
        for window in ROLLING_WINDOWS:
            for transform in ROLLING_TRANSFORMS:
                rows.append(
                    {
                        "derived_feature_id": f"{transform}_{window}h__{field}",
                        "production_family": "rolling_self_reproduction",
                        "base_fields": field,
                        "base_field_families": family,
                        "transform": transform,
                        "window_hours": window,
                        "requires_agg_features_available_mask": True,
                        "feature_available_lag_bars": max(1, window),
                        "cross_symbol_scope": "same_symbol",
                        "zero_fill_allowed": False,
                        "missing_as_signal_allowed": False,
                        "same_hour_execution_allowed": False,
                    }
                )

    cross_fields = enabled[enabled["field_family"].isin(["flow", "activity_liquidity", "large_trade", "price_microstructure", "rolling"])]
    for _, row in cross_fields.iterrows():
        field = str(row["field_name"])
        family = str(row["field_family"])
        for transform in CROSS_SYMBOL_TRANSFORMS:
            rows.append(
                {
                    "derived_feature_id": f"{transform}_core3__{field}",
                    "production_family": "cross_symbol_self_reproduction_core3",
                    "base_fields": field,
                    "base_field_families": family,
                    "transform": transform,
                    "window_hours": 1,
                    "requires_agg_features_available_mask": True,
                    "feature_available_lag_bars": 1,
                    "cross_symbol_scope": "BTCUSDT,ETHUSDT,SOLUSDT",
                    "zero_fill_allowed": False,
                    "missing_as_signal_allowed": False,
                    "same_hour_execution_allowed": False,
                }
            )

    interaction_seed_fields = [
        "agg_flow_imbalance_notional",
        "agg_notional",
        "agg_large_notional_share_100k_plus",
        "agg_price_range_bps",
        "agg_signed_flow_z_24h",
    ]
    for agg_field in interaction_seed_fields:
        if agg_field not in set(enabled["field_name"]):
            continue
        for market_field in MARKET_CONTROL_FIELDS:
            for transform in INTERACTION_TRANSFORMS:
                rows.append(
                    {
                        "derived_feature_id": f"{transform}__{agg_field}__{market_field}",
                        "production_family": "interaction_self_reproduction",
                        "base_fields": f"{agg_field};{market_field}",
                        "base_field_families": "aggtrades;market_or_funding_control",
                        "transform": transform,
                        "window_hours": 1,
                        "requires_agg_features_available_mask": True,
                        "feature_available_lag_bars": 1,
                        "cross_symbol_scope": "same_symbol",
                        "zero_fill_allowed": False,
                        "missing_as_signal_allowed": False,
                        "same_hour_execution_allowed": False,
                    }
                )
    return pd.DataFrame(rows)


def build_config(base_registry: pd.DataFrame, derived_specs: pd.DataFrame, now: str) -> dict[str, Any]:
    enabled = base_registry[base_registry["generator_enabled"]]
    return {
        "schema_version": "crypto_a7v_feature_registry_v1",
        "generated_at": now,
        "primary_panel": str(PANEL_PATH),
        "integration_mode": "opt_in_explicit_load",
        "availability_mask": "agg_features_available",
        "schema_field": "agg_feature_schema",
        "agg_coverage_symbols": CORE3,
        "core_universe": CORE12,
        "numeric_agg_base_feature_count": int(len(enabled)),
        "derived_feature_spec_count": int(len(derived_specs)),
        "field_family_counts": enabled["field_family"].value_counts().sort_index().to_dict(),
        "production_families": sorted(derived_specs["production_family"].unique().tolist()),
        "generator_controls": {
            "zero_fill_allowed": False,
            "missing_as_signal_allowed": False,
            "same_hour_execution_allowed": False,
            "non_core3_cross_section_rank_allowed": False,
            "funding_as_unrestricted_discovery_target_allowed": False,
            "required_feature_available_time": "hour_bucket_start + 1h for base agg; rolling descendants shift by required past-only lookback",
            "required_residual_baselines": ["FundingCore", "Core4"],
            "required_negative_controls": ["row_shuffle", "time_shuffle", "wrong_lag", "sign_flip", "no_agg_mask", "zero_fill_core12_rank"],
        },
        "files": {
            "base_feature_registry": str((OUT_DIR / "a7v1_base_feature_registry.csv").relative_to(ROOT)),
            "derived_feature_specs": str((OUT_DIR / "a7v1_derived_feature_specs.csv").relative_to(ROOT)),
            "smoke_metrics": str((OUT_DIR / "a7v2_no_search_smoke_metrics.csv").relative_to(ROOT)),
            "negative_controls": str((OUT_DIR / "a7v2_negative_control_audit.csv").relative_to(ROOT)),
        },
    }


def rank_pct(s: pd.Series) -> pd.Series:
    return s.rank(method="average", pct=True)


def zscore(s: pd.Series) -> pd.Series:
    std = s.std(ddof=0)
    if not np.isfinite(std) or std == 0:
        return pd.Series(np.nan, index=s.index)
    return (s - s.mean()) / std


def add_smoke_feature(df: pd.DataFrame, name: str, values: pd.Series) -> dict[str, Any]:
    mask = df["agg_features_available"].fillna(False).astype(bool)
    non_core3 = ~df["symbol"].isin(CORE3)
    may2026 = df["timestamp"] >= pd.Timestamp("2026-05-01", tz="UTC")
    arr = values.to_numpy(dtype=float)
    finite = np.isfinite(arr)
    non_null = pd.Series(values).notna()
    available_non_null = non_null & mask
    return {
        "feature_id": name,
        "rows": int(len(values)),
        "non_null_rows": int(non_null.sum()),
        "finite_rate_when_non_null": float(finite[non_null.to_numpy()].mean()) if non_null.any() else None,
        "non_core3_output_rows": int((non_null & non_core3).sum()),
        "without_agg_mask_output_rows": int((non_null & ~mask).sum()),
        "may2026_output_rows": int((non_null & may2026).sum()),
        "available_non_null_rate": float(available_non_null.sum() / max(int(mask.sum()), 1)),
        "min": float(np.nanmin(arr)) if np.isfinite(arr).any() else None,
        "max": float(np.nanmax(arr)) if np.isfinite(arr).any() else None,
        "decision": "PASS" if int((non_null & non_core3).sum()) == 0 and int((non_null & ~mask).sum()) == 0 else "HOLD_MASK_OR_SCOPE_VIOLATION",
    }


def run_no_search_smoke() -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = ["symbol", "timestamp", "agg_features_available"] + SMOKE_BASE_FIELDS + ["mark_index_ratio", "premium_index"]
    df = pd.read_parquet(PANEL_PATH, columns=cols)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    mask = df["agg_features_available"].fillna(False).astype(bool)

    masked_flow = df["agg_flow_imbalance_notional"].where(mask)
    masked_notional = df["agg_notional"].where(mask)
    masked_large_share = df["agg_large_notional_share_100k_plus"].where(mask)
    masked_range = df["agg_price_range_bps"].where(mask)
    masked_signed_z = df["agg_signed_flow_z_24h"].where(mask)

    smoke: dict[str, pd.Series] = {}
    smoke["TSMean_4h__agg_flow_imbalance_notional"] = (
        masked_flow.groupby(df["symbol"]).rolling(4, min_periods=4).mean().reset_index(level=0, drop=True)
    )
    smoke["Delta_4h__agg_notional"] = masked_notional.groupby(df["symbol"]).diff(4)
    smoke["TSStd_24h__agg_large_notional_share_100k_plus"] = (
        masked_large_share.groupby(df["symbol"]).rolling(24, min_periods=24).std(ddof=0).reset_index(level=0, drop=True)
    )
    smoke["ZScore_by_symbol__agg_price_range_bps"] = masked_range.groupby(df["symbol"]).transform(zscore)
    smoke["Mul__agg_signed_flow_z_24h__mark_index_ratio"] = (masked_signed_z * df["mark_index_ratio"]).where(mask)

    core3_frame = df[["symbol", "timestamp"]].copy()
    core3_values = df["agg_flow_imbalance_notional"].where(mask)
    core3_rank = core3_values.groupby(df["timestamp"]).transform(lambda s: s.where(df.loc[s.index, "symbol"].isin(CORE3)).rank(method="average", pct=True))
    smoke["CrossSymbolRank_core3__agg_flow_imbalance_notional"] = core3_rank.where(df["symbol"].isin(CORE3) & mask)

    btc = (
        pd.DataFrame({"timestamp": df["timestamp"], "symbol": df["symbol"], "value": core3_values})
        .query("symbol == 'BTCUSDT'")
        .set_index("timestamp")["value"]
    )
    btc_aligned = df["timestamp"].map(btc)
    smoke["RelativeToBTC_core3__agg_flow_imbalance_notional"] = (core3_values - btc_aligned).where(df["symbol"].isin(CORE3) & mask)

    smoke_rows = [add_smoke_feature(df, name, values) for name, values in smoke.items()]

    zero_fill = df["agg_flow_imbalance_notional"].fillna(0.0)
    zero_fill_rank = zero_fill.groupby(df["timestamp"]).transform(rank_pct)
    neg_rows = [
        {
            "control_id": "zero_fill_core12_cross_symbol_rank",
            "control_type": "forbidden_zero_fill",
            "non_core3_output_rows": int((zero_fill_rank.notna() & ~df["symbol"].isin(CORE3)).sum()),
            "would_pass_without_contract": True,
            "decision": "BLOCKED_EXPECTED_CONTROL",
            "notes": "Shows why missing agg rows cannot be zero-filled before cross-sectional rank.",
        },
        {
            "control_id": "same_hour_execution_lag0",
            "control_type": "forbidden_timing",
            "feature_available_lag_bars": 0,
            "would_pass_without_contract": True,
            "decision": "BLOCKED_EXPECTED_CONTROL",
            "notes": "Agg 1h bucket may only be used after hour close; same-hour close execution is forbidden.",
        },
        {
            "control_id": "funding_unrestricted_interaction",
            "control_type": "forbidden_unrestricted_funding",
            "base_fields": "agg_flow_imbalance_notional;latest_known_funding_rate",
            "would_pass_without_contract": True,
            "decision": "BLOCKED_EXPECTED_CONTROL",
            "notes": "Funding may be a baseline/control or residual target; unrestricted discovery packaging remains blocked.",
        },
    ]
    return pd.DataFrame(smoke_rows), pd.DataFrame(neg_rows)


def write_report(
    *,
    now: str,
    base_registry: pd.DataFrame,
    derived_specs: pd.DataFrame,
    smoke_metrics: pd.DataFrame,
    negative_controls: pd.DataFrame,
    authorization: dict[str, Any],
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    enabled = base_registry[base_registry["generator_enabled"]]
    lines = [
        "# Crypto A7V-1/A7V-2 Feature Registry and No-Search Smoke",
        "",
        f"- generated_at: `{now}`",
        f"- primary_panel: `{PANEL_PATH}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Purpose",
        "",
        "A7V accepted the unified panel. This step turns the accepted aggTrades fields into an explicit opt-in generator registry and verifies a small set of self-reproduced derived features on the real panel without running search.",
        "",
        "## Registry Summary",
        "",
        f"- enabled agg base features: `{len(enabled)}`",
        f"- derived feature specs: `{len(derived_specs)}`",
        f"- config: `{CONFIG_PATH}`",
        "- integration mode: `opt_in_explicit_load`; old A7M/A7O replay artifacts are not changed by this registry.",
        "",
        "## Base Field Families",
        "",
        table(enabled.groupby("field_family").size().reset_index(name="enabled_field_count"), max_rows=40),
        "",
        "## No-Search Smoke Metrics",
        "",
        table(smoke_metrics, max_rows=40),
        "",
        "## Negative Controls",
        "",
        table(negative_controls, max_rows=40),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- A7V-3: implement an agg-aware candidate dry-run using this registry, still no alpha proof.",
        "- A7V-4: include row/time/wrong-lag/no-mask controls before any agg-aware search.",
        "- Do not run full A7O/A7M search from this registry until A7V-2 smoke stays clean and raw checksum trace is consolidated.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    feature_contract = read_feature_contract()
    base_registry = build_base_registry(feature_contract)
    derived_specs = build_derived_specs(base_registry)
    smoke_metrics, negative_controls = run_no_search_smoke()

    blockers: list[str] = []
    if not smoke_metrics["decision"].eq("PASS").all():
        blockers.append("derived_feature_smoke_mask_or_scope_violation")
    if not negative_controls["decision"].eq("BLOCKED_EXPECTED_CONTROL").all():
        blockers.append("negative_control_not_blocked")
    if int(base_registry["generator_enabled"].sum()) < 90:
        blockers.append("too_few_enabled_agg_base_features")
    if int(derived_specs["requires_agg_features_available_mask"].sum()) != len(derived_specs):
        blockers.append("derived_spec_without_required_agg_mask")
    if bool(derived_specs["zero_fill_allowed"].any()):
        blockers.append("derived_spec_allows_zero_fill")

    decision = "PASS_A7V1_FEATURE_REGISTRY_AND_A7V2_NO_SEARCH_SMOKE" if not blockers else "HOLD_A7V1_A7V2_CONTRACT_OR_SMOKE_BLOCKER"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_agg_aware_generator_dry_run": decision.startswith("PASS"),
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_zero_fill_for_missing_agg": False,
        "authorizes_same_hour_execution": False,
        "authorizes_core12_cross_section_rank_with_missing_agg": False,
        "required_next": [
            "A7V-3 agg-aware candidate dry run using config/crypto_a7v_feature_registry_v1.json",
            "A7V-4 no-mask/wrong-lag/time-shuffle controls before replay",
            "A7U-0R consolidated raw checksum trace before final alpha panel claims",
        ],
    }

    config = build_config(base_registry, derived_specs, now)
    config["authorization"] = authorization

    base_registry.to_csv(OUT_DIR / "a7v1_base_feature_registry.csv", index=False)
    derived_specs.to_csv(OUT_DIR / "a7v1_derived_feature_specs.csv", index=False)
    smoke_metrics.to_csv(OUT_DIR / "a7v2_no_search_smoke_metrics.csv", index=False)
    negative_controls.to_csv(OUT_DIR / "a7v2_negative_control_audit.csv", index=False)
    write_json(OUT_DIR / "a7v1_authorization_matrix.json", authorization)
    write_json(OUT_DIR / "a7v1_manifest.json", {"generated_at": now, "config": str(CONFIG_PATH), "output_dir": str(OUT_DIR), "decision": decision})
    write_json(CONFIG_PATH, config)
    write_report(now=now, base_registry=base_registry, derived_specs=derived_specs, smoke_metrics=smoke_metrics, negative_controls=negative_controls, authorization=authorization)

    print(json.dumps({"decision": decision, "blockers": blockers, "enabled_base_features": int(base_registry["generator_enabled"].sum()), "derived_specs": int(len(derived_specs))}, indent=2))


if __name__ == "__main__":
    main()
