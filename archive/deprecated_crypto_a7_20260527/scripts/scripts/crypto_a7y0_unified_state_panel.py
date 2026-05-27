from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path("G:/AlphaFactory_CryptoData")
BASE_PANEL_PATH = DATA_ROOT / "gold" / "panels" / "crypto_core12_1h_with_aggtrades_features_v1.parquet"
METRICS_PATH = DATA_ROOT / "gold" / "features" / "binance_metrics_1h_features_v1.parquet"
OUT_PANEL_PATH = DATA_ROOT / "gold" / "panels" / "crypto_core12_1h_with_aggtrades_metrics_features_v1.parquet"
A7S1_AUTH = ROOT / "runtime" / "a7s1_metrics_acceptance_audit" / "a7s1_acceptance_authorization_matrix.json"
A7U0R_AUTH = ROOT / "runtime" / "a7u0r_source_trace_audit" / "a7u0r_manifest.json"

OUT_DIR = ROOT / "runtime" / "a7y0_unified_state_panel"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7Y0_UNIFIED_STATE_PANEL_20260522.md"

METRICS_INDEPENDENT = [
    "open_interest",
    "open_interest_value",
    "global_long_short_account_ratio",
    "top_long_short_account_ratio",
    "top_long_short_position_ratio",
    "taker_buy_sell_volume_ratio",
]

METRICS_DERIVED = [
    "open_interest_change_1h",
    "open_interest_change_4h",
    "open_interest_change_24h",
    "open_interest_zscore_168h",
    "open_interest_value_change_1h",
    "open_interest_value_change_4h",
    "open_interest_value_change_24h",
    "open_interest_value_zscore_168h",
    "global_long_short_account_ratio_change_1h",
    "global_long_short_account_ratio_change_4h",
    "global_long_short_account_ratio_change_24h",
    "global_long_short_account_ratio_zscore_168h",
    "top_long_short_account_ratio_change_1h",
    "top_long_short_account_ratio_change_4h",
    "top_long_short_account_ratio_change_24h",
    "top_long_short_account_ratio_zscore_168h",
    "top_long_short_position_ratio_change_1h",
    "top_long_short_position_ratio_change_4h",
    "top_long_short_position_ratio_change_24h",
    "top_long_short_position_ratio_zscore_168h",
    "taker_buy_sell_volume_ratio_change_1h",
    "taker_buy_sell_volume_ratio_change_4h",
    "taker_buy_sell_volume_ratio_change_24h",
    "taker_buy_sell_volume_ratio_zscore_168h",
    "open_interest_x_price_move_1h",
    "open_interest_x_taker_imbalance",
]

METRICS_CONTEXT_OVERLAP = {"ret_1", "ret_24", "taker_imbalance"}


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def feature_registry(base_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for col in base_cols:
        role = "aggtrades_feature" if col.startswith("agg_") else "base_market_feature"
        if col in {"symbol", "timestamp"}:
            role = "key"
        rows.append(
            {
                "field_name": col,
                "source_layer": "base_aggtrades_panel",
                "field_role": role,
                "is_independent_source": False,
                "is_derived": role != "key",
                "feature_available_rule": "base panel/A7U contracts; execute next 1h bar or later",
            }
        )
    for col in METRICS_INDEPENDENT:
        rows.append(
            {
                "field_name": col,
                "source_layer": "binance_vision_metrics_daily",
                "field_role": "metrics_independent_source",
                "is_independent_source": True,
                "is_derived": False,
                "feature_available_rule": "metrics raw observable_time = timestamp + 5min; 1h feature_available_time = hour + 1h",
            }
        )
    for col in METRICS_DERIVED:
        rows.append(
            {
                "field_name": col,
                "source_layer": "binance_metrics_derived",
                "field_role": "metrics_derived_feature",
                "is_independent_source": False,
                "is_derived": True,
                "feature_available_rule": "past-only transform after metrics 1h feature availability",
            }
        )
    return pd.DataFrame(rows).drop_duplicates("field_name", keep="last")


def coverage_summary(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    agg_available = panel["agg_features_available"].fillna(False).astype(bool) if "agg_features_available" in panel.columns else pd.Series(False, index=panel.index)
    metrics_available = panel["metrics_features_available"].fillna(False).astype(bool)
    for symbol, part in panel.groupby("symbol", sort=True):
        rows.append(
            {
                "symbol": symbol,
                "rows": int(len(part)),
                "timestamp_min": str(part["timestamp"].min()),
                "timestamp_max": str(part["timestamp"].max()),
                "agg_available_hours": int(agg_available.loc[part.index].sum()),
                "agg_available_rate": float(agg_available.loc[part.index].mean()),
                "metrics_available_hours": int(metrics_available.loc[part.index].sum()),
                "metrics_available_rate": float(metrics_available.loc[part.index].mean()),
            }
        )
    return pd.DataFrame(rows)


def write_report(now: str, panel_summary: pd.DataFrame, coverage: pd.DataFrame, registry: pd.DataFrame, checks: pd.DataFrame, auth: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    registry_summary = registry.groupby(["source_layer", "field_role", "is_independent_source"]).size().reset_index(name="fields")
    lines = [
        "# Crypto A7Y-0 Unified State Panel",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{auth['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / full search / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7Y-0 merges the accepted aggTrades-enhanced panel and Binance metrics 1h feature panel into a single experiment panel. It is a data integration gate, not a signal proof.",
        "",
        "Metrics vendor 5m warnings and aggTrades availability flags are preserved. Derived fields are not independent data sources.",
        "",
        "## Output Panel",
        "",
        f"`{OUT_PANEL_PATH}`",
        "",
        "## Panel Summary",
        "",
        table(panel_summary, max_rows=20),
        "",
        "## Coverage",
        "",
        table(coverage, max_rows=20),
        "",
        "## Registry Summary",
        "",
        table(registry_summary, max_rows=80),
        "",
        "## Checks",
        "",
        table(checks, max_rows=40),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(auth, indent=2, sort_keys=True),
        "```",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    a7s1 = load_json(A7S1_AUTH)
    a7u0r = load_json(A7U0R_AUTH)
    base = pd.read_parquet(BASE_PANEL_PATH)
    metrics_cols = ["symbol", "timestamp"] + METRICS_INDEPENDENT + METRICS_DERIVED
    metrics = pd.read_parquet(METRICS_PATH, columns=metrics_cols)
    base["timestamp"] = pd.to_datetime(base["timestamp"], utc=True)
    metrics["timestamp"] = pd.to_datetime(metrics["timestamp"], utc=True)
    panel = base.merge(metrics, on=["symbol", "timestamp"], how="left", validate="one_to_one")
    independent_available = np.ones(len(panel), dtype=bool)
    for col in METRICS_INDEPENDENT:
        independent_available &= np.isfinite(pd.to_numeric(panel[col], errors="coerce").to_numpy(dtype=float))
    panel["metrics_features_available"] = independent_available
    panel["metrics_vendor_warning_caveat"] = True
    panel["metrics_feature_available_time"] = panel["timestamp"] + pd.Timedelta(hours=1)
    panel["feature_available_time"] = panel["timestamp"] + pd.Timedelta(hours=1)
    panel["execution_time_min"] = panel["timestamp"] + pd.Timedelta(hours=1)
    panel["unified_feature_schema"] = "crypto_core12_1h_with_aggtrades_metrics_features_v1"
    OUT_PANEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(OUT_PANEL_PATH, index=False)

    registry = feature_registry(list(base.columns) + METRICS_INDEPENDENT + METRICS_DERIVED)
    coverage = coverage_summary(panel)
    numeric = panel.select_dtypes("number")
    inf_count = int(np.isinf(numeric.to_numpy(dtype=float, copy=False)).sum())
    duplicate_keys = int(panel.duplicated(["symbol", "timestamp"]).sum())
    checks = pd.DataFrame(
        [
            {"check": "a7s1_metrics_acceptance", "value": a7s1.get("decision", "missing"), "status": "PASS" if str(a7s1.get("decision", "")).startswith("PASS") else "WARNING"},
            {"check": "a7u0r_source_trace", "value": a7u0r.get("decision", "missing"), "status": "PASS" if str(a7u0r.get("decision", "")).startswith("PASS") else "WARNING"},
            {"check": "rows", "value": int(len(panel)), "status": "PASS" if len(panel) > 250000 else "WARNING"},
            {"check": "columns", "value": int(panel.shape[1]), "status": "PASS"},
            {"check": "symbols", "value": int(panel["symbol"].nunique()), "status": "PASS" if panel["symbol"].nunique() == 12 else "BLOCKER"},
            {"check": "duplicate_symbol_timestamp", "value": duplicate_keys, "status": "PASS" if duplicate_keys == 0 else "BLOCKER"},
            {"check": "inf_numeric_cells", "value": inf_count, "status": "PASS" if inf_count == 0 else "BLOCKER"},
            {"check": "metrics_independent_fields", "value": len(METRICS_INDEPENDENT), "status": "PASS"},
            {"check": "metrics_derived_fields", "value": len(METRICS_DERIVED), "status": "PASS"},
            {"check": "derived_fields_not_independent", "value": True, "status": "PASS"},
            {"check": "feature_available_time_rule", "value": "timestamp+1h", "status": "PASS"},
        ]
    )
    blockers = checks[checks["status"].eq("BLOCKER")]["check"].tolist()
    decision = "PASS_A7Y0_UNIFIED_STATE_PANEL_READY" if not blockers else "HOLD_A7Y0_PANEL_BLOCKERS"
    auth = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "output_panel": str(OUT_PANEL_PATH),
        "rows": int(len(panel)),
        "columns": int(panel.shape[1]),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7y1_small_interaction_diagnostic": not blockers,
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "vendor_5m_warning_caveat_required": True,
        "feature_available_time_rule": "feature_available_time = timestamp + 1h; execution_time >= next 1h bar",
        "required_next": [
            "A7Y-1 small interaction diagnostic",
            "Do not treat metrics derived fields as independent sources",
            "Preserve agg_features_available and metrics_features_available masks",
        ],
    }
    panel_summary = pd.DataFrame(
        [
            {
                "panel_path": str(OUT_PANEL_PATH),
                "rows": int(len(panel)),
                "columns": int(panel.shape[1]),
                "timestamp_min": str(panel["timestamp"].min()),
                "timestamp_max": str(panel["timestamp"].max()),
                "file_size_mb": round(OUT_PANEL_PATH.stat().st_size / 1024 / 1024, 2),
            }
        ]
    )
    registry.to_csv(OUT_DIR / "a7y0_feature_registry.csv", index=False)
    coverage.to_csv(OUT_DIR / "a7y0_coverage_by_symbol.csv", index=False)
    checks.to_csv(OUT_DIR / "a7y0_check_matrix.csv", index=False)
    panel_summary.to_csv(OUT_DIR / "a7y0_panel_summary.csv", index=False)
    write_json(OUT_DIR / "a7y0_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7y0_manifest.json", {"generated_at": now, "decision": decision, "output_dir": str(OUT_DIR), "report": str(REPORT_PATH), "output_panel": str(OUT_PANEL_PATH)})
    write_report(now, panel_summary, coverage, registry, checks, auth)
    print(json.dumps({"decision": decision, "blockers": blockers, "rows": len(panel), "columns": panel.shape[1], "panel": str(OUT_PANEL_PATH)}, indent=2))


if __name__ == "__main__":
    main()
