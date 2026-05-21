from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
RUNTIME_DIR = ROOT / "runtime"
OUT_DIR = RUNTIME_DIR / "a7s1_data_source_availability"
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
DATE_TAG = "20260521"

MANIFEST_DIR = DATA_ROOT / "manifests"
GOLD_DIR = DATA_ROOT / "gold"
METADATA_DIR = DATA_ROOT / "metadata"

CORE12 = {
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
}

MANIFESTS = {
    "silver": MANIFEST_DIR / "crypto_silver_manifest_20260519.csv",
    "funding_rate": MANIFEST_DIR / "fundingRate_core12_202401_current_manifest.csv",
    "positioning_recent29d": MANIFEST_DIR / "positioning_core12_recent29d_5m_manifest.csv",
    "positioning_recent30d": MANIFEST_DIR / "positioning_core12_recent30d_5m_manifest.csv",
    "positioning_forward_20260519": MANIFEST_DIR / "positioning_forward_5m_2026-05-19_manifest.csv",
    "positioning_forward_20260520": MANIFEST_DIR / "positioning_forward_5m_2026-05-20_manifest.csv",
    "microstructure_pilot": MANIFEST_DIR / "microstructure_pilot_20260519_manifest.csv",
    "spot_core6": MANIFEST_DIR / "spot_core6_202401_202604_manifest.csv",
}

PANELS = {
    "core12_1h": GOLD_DIR / "panels" / "crypto_core12_1h_v1.parquet",
    "core12_1h_forward_updated": GOLD_DIR / "panels" / "crypto_core12_1h_v1_forward_updated.parquet",
    "core12_5m": GOLD_DIR / "panels" / "crypto_core12_5m_v1.parquet",
}

CONTRACT_PATH = GOLD_DIR / "contracts" / "crypto_gold_contract_20260519.json"
SANITY_PATH = GOLD_DIR / "reports" / "crypto_core12_panel_v1_sanity.json"
POSITIONING_STATE = METADATA_DIR / "positioning_forward_state.csv"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def table(df: pd.DataFrame, max_rows: int = 60) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def status_counts(df: pd.DataFrame, col: str = "status") -> dict[str, int]:
    if col not in df.columns:
        return {}
    return {str(k): int(v) for k, v in df[col].fillna("<NA>").value_counts(dropna=False).sort_index().items()}


def summarize_manifest(name: str, path: Path) -> dict[str, Any]:
    row: dict[str, Any] = {
        "source_id": name,
        "path": str(path),
        "exists": path.exists(),
        "file_size_bytes": path.stat().st_size if path.exists() else 0,
    }
    if not path.exists():
        row.update(
            {
                "manifest_rows": 0,
                "status_counts": "{}",
                "data_type_count": 0,
                "symbol_count": 0,
                "row_count_sum": 0,
                "date_range_min": "",
                "date_range_max": "",
            }
        )
        return row

    df = pd.read_csv(path)
    row["manifest_rows"] = int(len(df))
    row["status_counts"] = json.dumps(status_counts(df), sort_keys=True)
    row["data_type_count"] = int(df["data_type"].nunique()) if "data_type" in df.columns else int(df["endpoint"].nunique()) if "endpoint" in df.columns else 0
    row["symbol_count"] = int(df["symbol"].nunique()) if "symbol" in df.columns else 0
    row["row_count_sum"] = int(pd.to_numeric(df.get("row_count", pd.Series(dtype=float)), errors="coerce").fillna(0).sum())
    if "date_range" in df.columns and not df["date_range"].dropna().empty:
        ranges = df["date_range"].dropna().astype(str)
        row["date_range_min"] = str(ranges.min())
        row["date_range_max"] = str(ranges.max())
    elif {"start_ms", "end_ms"}.issubset(df.columns):
        starts = pd.to_numeric(df["start_ms"], errors="coerce")
        ends = pd.to_numeric(df["end_ms"], errors="coerce")
        row["date_range_min"] = ms_to_iso(starts.min())
        row["date_range_max"] = ms_to_iso(ends.max())
    else:
        row["date_range_min"] = ""
        row["date_range_max"] = ""
    return row


def ms_to_iso(value: Any) -> str:
    try:
        if pd.isna(value):
            return ""
        return datetime.fromtimestamp(float(value) / 1000.0, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return ""


def panel_coverage() -> pd.DataFrame:
    sanity = read_json(SANITY_PATH)
    rows: list[dict[str, Any]] = []
    for panel_id, path in PANELS.items():
        row: dict[str, Any] = {
            "panel_id": panel_id,
            "path": str(path),
            "exists": path.exists(),
            "rows": 0,
            "columns": 0,
            "symbol_count": "",
            "min_timestamp": "",
            "max_timestamp": "",
            "has_positioning_columns": False,
            "has_open_interest": False,
            "has_long_short": False,
            "has_liquidation": False,
            "has_orderbook": False,
            "has_cross_exchange": False,
        }
        if path.exists():
            parquet = pq.ParquetFile(path)
            schema_names = parquet.schema_arrow.names
            row["rows"] = int(parquet.metadata.num_rows)
            row["columns"] = int(len(schema_names))
            joined = " ".join(schema_names).lower()
            row["has_positioning_columns"] = "positioning_historical_allowed" in schema_names
            row["has_open_interest"] = "openinterest" in joined or "open_interest" in joined
            row["has_long_short"] = "longshort" in joined or "long_short" in joined
            row["has_liquidation"] = "liquidation" in joined
            row["has_orderbook"] = "orderbook" in joined or "depth" in joined or "bid_" in joined or "ask_" in joined
        result_key = "1h" if "1h" in panel_id else "5m"
        result = sanity.get("results", {}).get(result_key, {})
        if result:
            row["duplicate_key_count"] = result.get("duplicate_key_count")
            row["positioning_recent_excluded"] = result.get("positioning_recent_excluded")
            row["checksum_ok_rows"] = result.get("checksum_status_counts", {}).get("ok")
            row["spot_close_missing_rate"] = result.get("missing_rate_top20", {}).get("spot_close")
            row["spot_perp_basis_missing_rate"] = result.get("missing_rate_top20", {}).get("spot_perp_basis")
            symbols = result.get("symbol_summary", {})
            row["symbol_count"] = len(symbols)
            if symbols:
                mins = [v.get("min_timestamp") for v in symbols.values() if isinstance(v, dict) and v.get("min_timestamp")]
                maxs = [v.get("max_timestamp") for v in symbols.values() if isinstance(v, dict) and v.get("max_timestamp")]
                row["min_timestamp"] = min(mins) if mins else ""
                row["max_timestamp"] = max(maxs) if maxs else ""
        rows.append(row)
    return pd.DataFrame(rows)


def candidate_source_contract(manifest_summary: pd.DataFrame, panel_df: pd.DataFrame) -> pd.DataFrame:
    def summary_row(source_id: str) -> dict[str, Any]:
        rows = manifest_summary[manifest_summary["source_id"] == source_id]
        return rows.iloc[0].to_dict() if not rows.empty else {}

    silver = summary_row("silver")
    funding = summary_row("funding_rate")
    positioning_recent = summary_row("positioning_recent29d")
    positioning_forward_20 = summary_row("positioning_forward_20260520")
    micro = summary_row("microstructure_pilot")
    spot = summary_row("spot_core6")

    return pd.DataFrame(
        [
            {
                "source": "futures_ohlcv_mark_index_premium",
                "local_status": "available_long_history",
                "local_evidence": "crypto_silver_manifest_20260519.csv",
                "history_window": "2024-01_to_2026-04",
                "core12_coverage": "core12",
                "pit_status": "research_usable_existing_panel",
                "alpha_search_status": "already_exhausted_by_A7P_A7R_current_line",
                "next_action": "do_not_continue_current_1h_objective_without_new_contract",
                "notes": f"silver rows={silver.get('row_count_sum', 0)}",
            },
            {
                "source": "funding_rate",
                "local_status": "available_long_history",
                "local_evidence": "fundingRate_core12_202401_current_manifest.csv",
                "history_window": "2024-01_to_current",
                "core12_coverage": "core12",
                "pit_status": "usable_as_observable_latest_known_after_A7D_A7E_controls",
                "alpha_search_status": "mandatory_baseline_not_new_edge_source",
                "next_action": "keep_residual_baseline_and_wrong_lag_controls",
                "notes": f"rows={funding.get('row_count_sum', 0)}",
            },
            {
                "source": "spot_perp_basis",
                "local_status": "available_partial",
                "local_evidence": "spot_core6_202401_202604_manifest.csv and panel spot_available mask",
                "history_window": "2024-01_to_2026-04",
                "core12_coverage": "core6_only",
                "pit_status": "usable_only_with_availability_mask_or_core6_universe",
                "alpha_search_status": "not_core12_full_universe_without_contract",
                "next_action": "if used, run core6-only or masked proof line",
                "notes": f"spot rows={spot.get('row_count_sum', 0)}; panel spot_perp_missing_rate={panel_df.get('spot_perp_basis_missing_rate', pd.Series(dtype=object)).dropna().iloc[0] if not panel_df.empty and 'spot_perp_basis_missing_rate' in panel_df.columns and not panel_df['spot_perp_basis_missing_rate'].dropna().empty else ''}",
            },
            {
                "source": "open_interest",
                "local_status": "recent_and_forward_only",
                "local_evidence": "positioning_recent29d + positioning_forward manifests",
                "history_window": "recent29d_plus_forward_from_2026-05-19",
                "core12_coverage": "core12_recent",
                "pit_status": "not_eligible_for_2024_2026_historical_alpha_search",
                "alpha_search_status": "forward_observation_or_requires_historical_backfill",
                "next_action": "A7S2_field_semantics_and_backfill_feasibility",
                "notes": f"recent rows={positioning_recent.get('row_count_sum', 0)}; latest forward rows={positioning_forward_20.get('row_count_sum', 0)}",
            },
            {
                "source": "long_short_positioning",
                "local_status": "recent_and_forward_only",
                "local_evidence": "positioning_recent29d + positioning_forward manifests",
                "history_window": "recent29d_plus_forward_from_2026-05-19",
                "core12_coverage": "core12_recent",
                "pit_status": "not_eligible_for_2024_2026_historical_alpha_search",
                "alpha_search_status": "forward_observation_or_requires_historical_backfill",
                "next_action": "A7S2_field_semantics_and_backfill_feasibility",
                "notes": "includes global/top account/position ratios where downloaded",
            },
            {
                "source": "aggTrades_microstructure",
                "local_status": "single_symbol_month_pilot_only",
                "local_evidence": "microstructure_pilot_20260519_manifest.csv",
                "history_window": "SOLUSDT_2026-04_only",
                "core12_coverage": "not_core12",
                "pit_status": "data_feasibility_sample_only",
                "alpha_search_status": "not_eligible_for_core12_historical_proof",
                "next_action": "only use for parser/storage/cost feasibility unless broader backfill contract passes",
                "notes": f"rows={micro.get('row_count_sum', 0)}",
            },
            {
                "source": "liquidation_events_or_volume",
                "local_status": "not_found_local",
                "local_evidence": "no local manifest detected",
                "history_window": "none",
                "core12_coverage": "none",
                "pit_status": "contract_required",
                "alpha_search_status": "not_authorized",
                "next_action": "source/vendor inventory and PIT timestamp contract",
                "notes": "high expected value for forced-flow state, but no local proof asset",
            },
            {
                "source": "orderbook_depth_spread_imbalance",
                "local_status": "not_found_local",
                "local_evidence": "no depth/orderbook manifest detected",
                "history_window": "none",
                "core12_coverage": "none",
                "pit_status": "contract_required",
                "alpha_search_status": "not_authorized",
                "next_action": "source/vendor inventory and storage/timestamp feasibility",
                "notes": "high timestamp and storage risk",
            },
            {
                "source": "cross_exchange_basis_or_funding",
                "local_status": "not_found_local",
                "local_evidence": "single-venue Binance data only",
                "history_window": "none",
                "core12_coverage": "none",
                "pit_status": "contract_required",
                "alpha_search_status": "not_authorized",
                "next_action": "venue inventory and symbol mapping contract",
                "notes": "would change hypothesis space; currently absent",
            },
        ]
    )


def positioning_audit() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for source_id in ["positioning_recent29d", "positioning_recent30d", "positioning_forward_20260519", "positioning_forward_20260520"]:
        path = MANIFESTS[source_id]
        if not path.exists():
            rows.append({"source_id": source_id, "exists": False})
            continue
        df = pd.read_csv(path)
        endpoint_col = "endpoint" if "endpoint" in df.columns else "data_type"
        for endpoint, g in df.groupby(endpoint_col):
            rows.append(
                {
                    "source_id": source_id,
                    "endpoint": endpoint,
                    "exists": True,
                    "manifest_rows": int(len(g)),
                    "symbols": int(g["symbol"].nunique()) if "symbol" in g.columns else 0,
                    "status_counts": json.dumps(status_counts(g), sort_keys=True),
                    "row_count_sum": int(pd.to_numeric(g.get("row_count", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()),
                    "min_start": ms_to_iso(pd.to_numeric(g["start_ms"], errors="coerce").min()) if "start_ms" in g.columns else "",
                    "max_end": ms_to_iso(pd.to_numeric(g["end_ms"], errors="coerce").max()) if "end_ms" in g.columns else "",
                    "date_range_sample": str(g["date_range"].dropna().iloc[0]) if "date_range" in g.columns and not g["date_range"].dropna().empty else "",
                    "pit_use_status": "recent_forward_only_not_historical_proof",
                }
            )
    if POSITIONING_STATE.exists():
        state = pd.read_csv(POSITIONING_STATE)
        now_ms = datetime.now(timezone.utc).timestamp() * 1000.0
        for endpoint, g in state.groupby("endpoint"):
            max_ts = pd.to_numeric(g["max_timestamp_ms"], errors="coerce").max()
            rows.append(
                {
                    "source_id": "positioning_forward_state",
                    "endpoint": endpoint,
                    "exists": True,
                    "manifest_rows": int(len(g)),
                    "symbols": int(g["symbol"].nunique()) if "symbol" in g.columns else 0,
                    "status_counts": "{}",
                    "row_count_sum": "",
                    "min_start": "",
                    "max_end": ms_to_iso(max_ts),
                    "date_range_sample": "",
                    "pit_use_status": "state_file_forward_only",
                    "future_timestamp_warning": bool(float(max_ts) > now_ms + 24 * 3600 * 1000) if pd.notna(max_ts) else False,
                }
            )
    return pd.DataFrame(rows)


def pit_matrix(contract: pd.DataFrame) -> pd.DataFrame:
    status_map = {
        "available_long_history": ("usable_existing", "No new alpha authorization; already evaluated under A7P/A7R current-space failure."),
        "available_partial": ("usable_with_mask_only", "Core6/availability mask required; not full core12."),
        "recent_and_forward_only": ("not_historical_proof", "Can support forward observation; cannot backfill 2024-2026 proof."),
        "single_symbol_month_pilot_only": ("feasibility_only", "Parser/storage feasibility; not research proof."),
        "not_found_local": ("contract_required", "Need source, PIT, coverage, and cost contract before collection/search."),
    }
    rows = []
    for _, row in contract.iterrows():
        pit_status, blocker = status_map.get(row["local_status"], ("hold", "Unclassified."))
        rows.append(
            {
                "source": row["source"],
                "local_status": row["local_status"],
                "pit_readiness": pit_status,
                "alpha_search_authorization": "not_authorized",
                "data_download_authorization": "not_authorized",
                "forward_observation_authorization": "authorized_if_append_only" if row["local_status"] in {"recent_and_forward_only", "available_long_history"} else "not_authorized",
                "blocking_reason": blocker,
            }
        )
    return pd.DataFrame(rows)


def microstructure_audit() -> pd.DataFrame:
    path = MANIFESTS["microstructure_pilot"]
    if not path.exists():
        return pd.DataFrame([{"source": "microstructure_pilot", "exists": False, "status": "not_found"}])
    df = pd.read_csv(path)
    return pd.DataFrame(
        [
            {
                "source": "microstructure_pilot",
                "exists": True,
                "symbol_count": int(df["symbol"].nunique()) if "symbol" in df.columns else 0,
                "symbols": ",".join(sorted(df["symbol"].dropna().astype(str).unique())) if "symbol" in df.columns else "",
                "date_ranges": ",".join(sorted(df["date_range"].dropna().astype(str).unique())) if "date_range" in df.columns else "",
                "data_types": ",".join(sorted(df["data_type"].dropna().astype(str).unique())) if "data_type" in df.columns else "",
                "row_count_sum": int(pd.to_numeric(df.get("row_count", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()),
                "checksum_status_counts": json.dumps(status_counts(df, "checksum_status"), sort_keys=True),
                "research_status": "parser_storage_feasibility_only_not_core12_alpha_proof",
            }
        ]
    )


def write_report(
    now: str,
    manifest_df: pd.DataFrame,
    panel_df: pd.DataFrame,
    source_contract: pd.DataFrame,
    pit_df: pd.DataFrame,
    positioning_df: pd.DataFrame,
    micro_df: pd.DataFrame,
    authorization: dict[str, Any],
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = [
        "# Crypto A7S-1 Data Source Availability / PIT Audit",
        "",
        f"- generated_at: `{now}`",
        "- decision: `HOLD_A7S1_NEW_DATA_NOT_READY_FOR_ALPHA_SEARCH`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- executes_download: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Decision",
        "",
        "A7S-1 confirms the current local data can support continued engineering and append-only forward observation, but it does not authorize a new crypto alpha search. The only long-history research-ready families are the same Binance futures/mark/index/premium/funding/spot-core6 data already used by A7P/A7R. The genuinely new state variables are either recent/forward-only or absent locally.",
        "",
        "## Existing Manifest Inventory",
        "",
        table(manifest_df),
        "",
        "## Gold Panel Coverage",
        "",
        table(panel_df),
        "",
        "## Candidate Source Contract",
        "",
        table(source_contract),
        "",
        "## PIT Readiness Matrix",
        "",
        table(pit_df),
        "",
        "## Positioning Audit",
        "",
        table(positioning_df),
        "",
        "## Microstructure Pilot Audit",
        "",
        table(micro_df),
        "",
        "## Authorization Matrix",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next Action",
        "",
        "1. `A7S-2`: field semantics and backfill feasibility review for open interest / long-short / liquidation / orderbook / cross-exchange sources.",
        "2. `A7T-0`: forward-locked observation contract using append-only data only.",
        "3. Do not restart current 1h formula search from A7P/A7R/A7O without a new data or horizon contract.",
    ]
    (REPORT_DIR / f"CRYPTO_A7S1_DATA_SOURCE_AVAILABILITY_AUDIT_{DATE_TAG}.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    now = utc_stamp()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest_df = pd.DataFrame([summarize_manifest(name, path) for name, path in MANIFESTS.items()])
    panel_df = panel_coverage()
    source_contract = candidate_source_contract(manifest_df, panel_df)
    pit_df = pit_matrix(source_contract)
    positioning_df = positioning_audit()
    micro_df = microstructure_audit()

    authorization = {
        "generated_at": now,
        "decision": "HOLD_A7S1_NEW_DATA_NOT_READY_FOR_ALPHA_SEARCH",
        "executes_search": False,
        "executes_replay": False,
        "executes_download": False,
        "authorizes_alpha_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_forward_observation_contract": True,
        "authorizes_a7s2_field_semantics_review": True,
        "authorizes_data_download": False,
        "required_before_download": [
            "source_cost_and_access_contract",
            "PIT_timestamp_contract",
            "symbol_coverage_contract",
            "storage_cost_contract",
            "small_sample_timestamp_audit",
        ],
        "blocking_findings": [
            "open_interest_and_long_short_are_recent_forward_only_not_2024_2026_historical_proof",
            "liquidation_orderbook_cross_exchange_sources_not_found_locally",
            "spot_perp_basis_is_core6_partial_not_core12_full_universe",
            "aggTrades_microstructure_is_SOLUSDT_2026_04_pilot_only",
            "current_long_history_panel_is_same_feature_space_that_A7P_A7R_already_rejected_for_alpha_search",
        ],
    }

    manifest_df.to_csv(OUT_DIR / "a7s1_existing_inventory.csv", index=False)
    panel_df.to_csv(OUT_DIR / "a7s1_panel_feature_coverage.csv", index=False)
    source_contract.to_csv(OUT_DIR / "a7s1_candidate_source_contract.csv", index=False)
    pit_df.to_csv(OUT_DIR / "a7s1_pit_readiness_matrix.csv", index=False)
    positioning_df.to_csv(OUT_DIR / "a7s1_positioning_manifest_audit.csv", index=False)
    micro_df.to_csv(OUT_DIR / "a7s1_microstructure_manifest_audit.csv", index=False)
    write_json(OUT_DIR / "a7s1_authorization_matrix.json", authorization)
    write_json(
        OUT_DIR / "a7s1_manifest.json",
        {
            "generated_at": now,
            "script": str(Path(__file__).relative_to(ROOT)),
            "data_root": str(DATA_ROOT),
            "outputs": [
                str((OUT_DIR / "a7s1_existing_inventory.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7s1_panel_feature_coverage.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7s1_candidate_source_contract.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7s1_pit_readiness_matrix.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7s1_positioning_manifest_audit.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7s1_microstructure_manifest_audit.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7s1_authorization_matrix.json").relative_to(ROOT)),
                f"reports/CRYPTO_A7S1_DATA_SOURCE_AVAILABILITY_AUDIT_{DATE_TAG}.md",
            ],
            "decision": authorization["decision"],
        },
    )

    write_report(now, manifest_df, panel_df, source_contract, pit_df, positioning_df, micro_df, authorization)


if __name__ == "__main__":
    main()
