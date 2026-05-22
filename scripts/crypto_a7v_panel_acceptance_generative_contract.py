from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
OUT_DIR = ROOT / "runtime" / "a7v_panel_generative_contract"
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
PANEL_PATH = DATA_ROOT / "gold" / "panels" / "crypto_core12_1h_with_aggtrades_features_v1.parquet"
BUILD_REPORT = DATA_ROOT / "reports" / "crypto_core12_1h_with_aggtrades_features_v1_20260522_015937.json"
DATE_TAG = "20260522"

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
AGG_SYMBOLS = {"BTCUSDT", "ETHUSDT", "SOLUSDT"}


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def classify_agg_column(col: str) -> str:
    if col in {"agg_features_available", "agg_feature_schema"}:
        return "availability_or_schema"
    if col.startswith("agg_universe_") or col.startswith("agg_cross_symbol_") or "minus_btcusdt" in col or "minus_ethusdt" in col or "btcusdt_" in col or "ethusdt_" in col:
        return "cross_symbol"
    if col.endswith("_4h") or col.endswith("_24h") or "_4h_" in col or "_24h_" in col:
        return "rolling"
    if "shock" in col or "accel" in col or "_z_" in col:
        return "shock_acceleration"
    if "large" in col:
        return "large_trade"
    if "vwap" in col or "price" in col or "open" in col or "close" in col:
        return "price_microstructure"
    if "flow" in col or "imbalance" in col or "signed" in col or "buy" in col or "sell" in col:
        return "flow"
    if "notional" in col or "quantity" in col or "trade_count" in col:
        return "activity_liquidity"
    return "other"


def panel_audit() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    parquet = pq.ParquetFile(PANEL_PATH)
    columns = parquet.schema_arrow.names
    agg_cols = [c for c in columns if c.startswith("agg_")]
    numeric_agg_cols = [c for c in agg_cols if c not in {"agg_features_available", "agg_feature_schema"}]
    feature_contract = pd.DataFrame(
        [
            {
                "field_name": col,
                "field_group": classify_agg_column(col),
                "generator_base_field": bool(col not in {"agg_features_available", "agg_feature_schema"}),
                "role": "availability" if col == "agg_features_available" else "schema" if col == "agg_feature_schema" else "feature",
                "feature_available_time_rule": "available_after_hour_close_plus_join_lag" if col.startswith("agg_") else "",
            }
            for col in agg_cols
        ]
    )
    use_cols = ["symbol", "timestamp", "agg_features_available"] + numeric_agg_cols
    df = pd.read_parquet(PANEL_PATH, columns=use_cols)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    coverage = (
        df.groupby("symbol")
        .agg(
            rows=("timestamp", "size"),
            min_timestamp=("timestamp", "min"),
            max_timestamp=("timestamp", "max"),
            agg_rows=("agg_features_available", "sum"),
            agg_coverage=("agg_features_available", "mean"),
        )
        .reset_index()
    )
    coverage["expected_agg_symbol"] = coverage["symbol"].isin(AGG_SYMBOLS)
    coverage["coverage_decision"] = np.where(
        coverage["expected_agg_symbol"],
        np.where(coverage["agg_coverage"].between(0.95, 0.99), "PASS_EXPECTED_CORE3_PARTIAL_TO_2026_04", "HOLD_UNEXPECTED_CORE3_COVERAGE"),
        np.where(coverage["agg_rows"].eq(0), "PASS_EXPECTED_NO_AGG_COVERAGE", "HOLD_UNEXPECTED_NON_CORE3_AGG_ROWS"),
    )
    coverage["min_timestamp"] = coverage["min_timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    coverage["max_timestamp"] = coverage["max_timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    agg_available = df[df["agg_features_available"].fillna(False).astype(bool)]
    missing_rows = []
    for col in numeric_agg_cols:
        s = agg_available[col]
        missing_rows.append(
            {
                "field_name": col,
                "field_group": classify_agg_column(col),
                "non_null_rate_when_available": float(s.notna().mean()) if len(s) else 0.0,
                "finite_rate_when_available": float(np.isfinite(s.dropna().to_numpy(dtype=float)).mean()) if s.notna().any() else 0.0,
                "min": float(s.min()) if s.notna().any() else None,
                "max": float(s.max()) if s.notna().any() else None,
            }
        )
    field_quality = pd.DataFrame(missing_rows)
    return coverage, feature_contract, field_quality


def build_generator_contract(feature_contract: pd.DataFrame) -> pd.DataFrame:
    base_groups = sorted(g for g in feature_contract["field_group"].unique() if g not in {"availability_or_schema"})
    rows = []
    for group in base_groups:
        rows.append(
            {
                "production_family": f"base_{group}",
                "allowed_inputs": group,
                "allowed_transforms": "Rank,ZScore,WinsorZScore,Clip,SafeDiv,Sign,Abs,Neg",
                "allowed_windows": "none",
                "may_use_missing_as_signal": False,
                "requires_agg_available_mask": True,
                "must_residualize_against": "FundingCore,Core4 for scoring",
                "notes": "Base agg feature use; generator may combine with existing mark/index/funding fields only under availability mask.",
            }
        )
    rows.extend(
        [
            {
                "production_family": "rolling_self_reproduction",
                "allowed_inputs": "all_numeric_agg_features",
                "allowed_transforms": "TSMean,TSStd,TSRank,Delta,Decay,RollingMin,RollingMax,ZScore",
                "allowed_windows": "4h,8h,12h,24h,48h,72h,96h",
                "may_use_missing_as_signal": False,
                "requires_agg_available_mask": True,
                "must_residualize_against": "FundingCore,Core4",
                "notes": "Formula generator may create rolling descendants, but windows must be past-only and feature_available_time shifts by the full rolling lookback plus one completed hour.",
            },
            {
                "production_family": "cross_symbol_self_reproduction_core3",
                "allowed_inputs": "BTCUSDT,ETHUSDT,SOLUSDT agg features only",
                "allowed_transforms": "CrossSymbolRank,CrossSymbolZScore,ShareOfUniverse,RelativeToBTC,RelativeToETH",
                "allowed_windows": "1h,4h,24h",
                "may_use_missing_as_signal": False,
                "requires_agg_available_mask": True,
                "must_residualize_against": "FundingCore,Core4",
                "notes": "Cross-symbol transforms are core3-only until agg coverage expands. Do not rank non-agg core12 symbols as zeros.",
            },
            {
                "production_family": "interaction_self_reproduction",
                "allowed_inputs": "agg_features plus existing market/funding/basis fields",
                "allowed_transforms": "Mul,Add,Sub,SafeDiv,HorizonSpread,SmoothInteraction",
                "allowed_windows": "same input windows only",
                "may_use_missing_as_signal": False,
                "requires_agg_available_mask": True,
                "must_residualize_against": "FundingCore,Core4",
                "notes": "Interactions are allowed only after both sides pass PIT availability. Funding remains a baseline/control, not an unrestricted discovery target.",
            },
            {
                "production_family": "blocked_missingness_or_core12_zero_fill",
                "allowed_inputs": "none",
                "allowed_transforms": "none",
                "allowed_windows": "none",
                "may_use_missing_as_signal": False,
                "requires_agg_available_mask": True,
                "must_residualize_against": "n/a",
                "notes": "Generator must not treat missing agg rows for non-core3 symbols as negative/zero signal. No zero-fill cross-section ranking.",
            },
            {
                "production_family": "blocked_future_or_same_hour",
                "allowed_inputs": "none",
                "allowed_transforms": "none",
                "allowed_windows": "none",
                "may_use_missing_as_signal": False,
                "requires_agg_available_mask": True,
                "must_residualize_against": "n/a",
                "notes": "Same-hour close execution and future rolling windows are forbidden.",
            },
        ]
    )
    return pd.DataFrame(rows)


def build_join_contract() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "rule_id": "panel_source",
                "rule": str(PANEL_PATH),
                "status": "primary_experiment_panel",
            },
            {
                "rule_id": "coverage_scope",
                "rule": "Agg features are valid only for BTCUSDT/ETHUSDT/SOLUSDT through 2026-04-30 23:00 UTC; non-core3 rows remain unavailable.",
                "status": "required",
            },
            {
                "rule_id": "availability_mask",
                "rule": "Every formula using agg fields must require agg_features_available == true for the symbol/timestamp.",
                "status": "required",
            },
            {
                "rule_id": "feature_available_time",
                "rule": "For hour bucket timestamp t, agg features are available after t + 1h; rolling descendants are available after the last required input hour closes.",
                "status": "required",
            },
            {
                "rule_id": "execution",
                "rule": "Primary replay must execute no earlier than next bar after feature availability. Same-hour close execution is forbidden.",
                "status": "required",
            },
            {
                "rule_id": "negative_controls",
                "rule": "Every agg feature smoke must retain row/time shuffle, wrong-lag, sign-flip, and no-agg controls.",
                "status": "required",
            },
        ]
    )


def write_report(now: str, coverage: pd.DataFrame, feature_contract: pd.DataFrame, field_quality: pd.DataFrame, generator_contract: pd.DataFrame, join_contract: pd.DataFrame, authorization: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    build_report = read_json(BUILD_REPORT)
    lines = [
        "# Crypto A7V Unified AggTrades Panel Acceptance and Generative Feature Contract",
        "",
        f"- generated_at: `{now}`",
        f"- panel: `{PANEL_PATH}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Build Report Summary",
        "",
        "```json",
        json.dumps(
            {
                "panel_rows": build_report.get("panel_rows"),
                "output_rows": build_report.get("output_rows"),
                "output_columns": build_report.get("output_columns"),
                "agg_feature_columns_reported_numeric": build_report.get("agg_feature_columns"),
                "agg_like_columns_detected_in_panel": int(len(feature_contract)),
                "agg_symbols": build_report.get("agg_symbols"),
                "agg_symbol_month_count": build_report.get("agg_symbol_month_count"),
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Acceptance Decision",
        "",
        "The unified panel is accepted for controlled experiment-line feature joins. It is not a final alpha panel: agg coverage is core3-only, May 2026 agg features are absent by design, and every generator using agg fields must obey the availability/timing mask.",
        "",
        "## Coverage by Symbol",
        "",
        table(coverage),
        "",
        "## Field Quality",
        "",
        table(field_quality, max_rows=120),
        "",
        "## Feature Contract",
        "",
        table(feature_contract, max_rows=140),
        "",
        "## Generator Self-Reproduction Contract",
        "",
        table(generator_contract, max_rows=120),
        "",
        "## Join and Timing Contract",
        "",
        table(join_contract),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    (REPORT_DIR / f"CRYPTO_A7V_UNIFIED_PANEL_GENERATIVE_CONTRACT_{DATE_TAG}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    now = utc_stamp()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    coverage, feature_contract, field_quality = panel_audit()
    generator_contract = build_generator_contract(feature_contract)
    join_contract = build_join_contract()

    core3_ok = coverage[coverage["symbol"].isin(AGG_SYMBOLS)]["coverage_decision"].eq("PASS_EXPECTED_CORE3_PARTIAL_TO_2026_04").all()
    non_core3_ok = coverage[~coverage["symbol"].isin(AGG_SYMBOLS)]["coverage_decision"].eq("PASS_EXPECTED_NO_AGG_COVERAGE").all()
    quality_ok = (field_quality["non_null_rate_when_available"] >= 0.99).all() and (field_quality["finite_rate_when_available"] >= 0.99).all()
    decision = "PASS_A7V_UNIFIED_PANEL_ACCEPTED_FOR_CONTROLLED_FEATURE_EXPERIMENTS" if core3_ok and non_core3_ok and quality_ok else "HOLD_A7V_UNIFIED_PANEL_REVIEW"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_controlled_feature_join_experiments": decision.startswith("PASS"),
        "authorizes_generator_self_reproduction_under_contract": decision.startswith("PASS"),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_core12_agg_claim": False,
        "authorizes_zero_fill_for_missing_agg": False,
        "primary_panel": str(PANEL_PATH),
        "required_next": [
            "A7V-1 implement feature family registry in formula generator",
            "A7V-2 small no-search feature smoke with negative controls",
            "A7V-3 if smoke passes, define agg-aware search cells; no full search yet",
        ],
    }

    coverage.to_csv(OUT_DIR / "a7v_panel_coverage_by_symbol.csv", index=False)
    feature_contract.to_csv(OUT_DIR / "a7v_feature_contract.csv", index=False)
    field_quality.to_csv(OUT_DIR / "a7v_field_quality.csv", index=False)
    generator_contract.to_csv(OUT_DIR / "a7v_generator_self_reproduction_contract.csv", index=False)
    join_contract.to_csv(OUT_DIR / "a7v_join_timing_contract.csv", index=False)
    write_json(OUT_DIR / "a7v_authorization_matrix.json", authorization)
    write_json(
        OUT_DIR / "a7v_manifest.json",
        {
            "generated_at": now,
            "script": str(Path(__file__).relative_to(ROOT)),
            "outputs": [
                str((OUT_DIR / "a7v_panel_coverage_by_symbol.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7v_feature_contract.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7v_field_quality.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7v_generator_self_reproduction_contract.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7v_join_timing_contract.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7v_authorization_matrix.json").relative_to(ROOT)),
                f"reports/CRYPTO_A7V_UNIFIED_PANEL_GENERATIVE_CONTRACT_{DATE_TAG}.md",
            ],
            "decision": decision,
        },
    )
    write_report(now, coverage, feature_contract, field_quality, generator_contract, join_contract, authorization)


if __name__ == "__main__":
    main()
