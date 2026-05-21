from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports"
OUT_DIR = ROOT / "runtime" / "a7s2_field_semantics"
DATE_TAG = "20260521"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def build_source_feasibility() -> pd.DataFrame:
    rows = [
        {
            "source": "open_interest_hist",
            "field_family": "open_interest",
            "official_endpoint_or_source": "GET /futures/data/openInterestHist",
            "official_doc_url": "https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest-Statistics",
            "documented_history_limit": "latest_1_month_only",
            "local_status": "recent29d_plus_forward_collector",
            "pit_semantics": "timestamp is event time; observable only after API publication/collector time",
            "2024_2026_backfill_feasibility": "not_feasible_from_binance_rest_history",
            "usable_for_next_search": "no_historical_alpha_search",
            "usable_for_forward": "yes_append_only",
            "risk": "Cannot be used to validate 2024-2026 fixed split unless an independent historical vendor exists.",
        },
        {
            "source": "global_long_short_account_ratio",
            "field_family": "positioning_crowding",
            "official_endpoint_or_source": "GET /futures/data/globalLongShortAccountRatio",
            "official_doc_url": "https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Long-Short-Ratio",
            "documented_history_limit": "latest_30_days_only",
            "local_status": "recent29d_plus_forward_collector",
            "pit_semantics": "timestamp is account ratio observation time; observable only after API publication/collector time",
            "2024_2026_backfill_feasibility": "not_feasible_from_binance_rest_history",
            "usable_for_next_search": "no_historical_alpha_search",
            "usable_for_forward": "yes_append_only",
            "risk": "Crowding signal may be valuable but cannot be retrofitted into historical proof.",
        },
        {
            "source": "top_trader_long_short_position_ratio",
            "field_family": "positioning_crowding",
            "official_endpoint_or_source": "GET /futures/data/topLongShortPositionRatio",
            "official_doc_url": "https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Top-Trader-Long-Short-Ratio",
            "documented_history_limit": "latest_30_days_only",
            "local_status": "recent29d_plus_forward_collector",
            "pit_semantics": "timestamp is top-trader position ratio observation time; observable only after API publication/collector time",
            "2024_2026_backfill_feasibility": "not_feasible_from_binance_rest_history",
            "usable_for_next_search": "no_historical_alpha_search",
            "usable_for_forward": "yes_append_only",
            "risk": "Useful as forward stress/crowding telemetry, not historical alpha proof.",
        },
        {
            "source": "basis_rest",
            "field_family": "basis_premium",
            "official_endpoint_or_source": "GET /futures/data/basis",
            "official_doc_url": "https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Basis",
            "documented_history_limit": "latest_30_days_only",
            "local_status": "not_collected_separately; mark/index/premium klines already exist long-history",
            "pit_semantics": "REST basis timestamp is event time; local long-history basis should use mark/index/premium klines instead",
            "2024_2026_backfill_feasibility": "not_needed_for_single_venue_basis; not_feasible_for_rest_basis_history",
            "usable_for_next_search": "only_if_new_cross_exchange_or_new_contract",
            "usable_for_forward": "yes_if_collected_append_only",
            "risk": "Single-venue Binance basis is already represented; REST basis does not add new long-history state.",
        },
        {
            "source": "aggTrades",
            "field_family": "microstructure_trades",
            "official_endpoint_or_source": "Binance Vision monthly aggTrades or GET /fapi/v1/aggTrades",
            "official_doc_url": "https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Compressed-Aggregate-Trades-List",
            "documented_history_limit": "REST_not_older_than_24h; Binance_Vision_monthly_history_available_by_file",
            "local_status": "SOLUSDT_2026_04_pilot_only",
            "pit_semantics": "trade timestamp is event time; monthly files can be historical if checksum and timestamp unit pass",
            "2024_2026_backfill_feasibility": "feasible_but_storage_heavy_for_core12",
            "usable_for_next_search": "not_until_core12_backfill_contract_and_storage_budget_pass",
            "usable_for_forward": "yes_if_collected_or_backfilled_with_versioned_manifest",
            "risk": "Large storage/compute; not a quick fix for A7P objective failure.",
        },
        {
            "source": "orderbook_depth_snapshot",
            "field_family": "orderbook_depth_spread",
            "official_endpoint_or_source": "GET /fapi/v1/depth",
            "official_doc_url": "https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book",
            "documented_history_limit": "snapshot_current_only_from_rest",
            "local_status": "not_found_local",
            "pit_semantics": "message output time and transaction time must be retained; historical backfill requires archived snapshots or continuous collector",
            "2024_2026_backfill_feasibility": "not_feasible_from_rest_without_archive_vendor",
            "usable_for_next_search": "no_historical_alpha_search",
            "usable_for_forward": "yes_after_collector_contract",
            "risk": "High timestamp/storage risk; snapshot sampling can create artificial spread/depth signals.",
        },
        {
            "source": "liquidation_events",
            "field_family": "forced_flow",
            "official_endpoint_or_source": "websocket liquidation/order stream or vendor archive",
            "official_doc_url": "contract_required",
            "documented_history_limit": "not_verified_in_local_assets",
            "local_status": "not_found_local",
            "pit_semantics": "event time and receive time must be separated; aggregation lag required",
            "2024_2026_backfill_feasibility": "requires_vendor_or_preexisting_archive",
            "usable_for_next_search": "no_until_source_contract",
            "usable_for_forward": "yes_after_collector_contract",
            "risk": "Expected value high for stress regimes but unavailable in current proof pack.",
        },
        {
            "source": "cross_exchange_basis_funding",
            "field_family": "venue_relative_value",
            "official_endpoint_or_source": "multi-venue vendor/API inventory required",
            "official_doc_url": "contract_required",
            "documented_history_limit": "venue_dependent",
            "local_status": "not_found_local",
            "pit_semantics": "venue clocks, symbol mapping, funding schedules, and publication delays must be normalized",
            "2024_2026_backfill_feasibility": "unknown_until_vendor_review",
            "usable_for_next_search": "no_until_vendor_contract",
            "usable_for_forward": "possible_after_contract",
            "risk": "Could change hypothesis space materially; also highest semantic mismatch risk.",
        },
    ]
    return pd.DataFrame(rows)


def build_pit_contract(feasibility: pd.DataFrame) -> pd.DataFrame:
    required = [
        "event_time",
        "observable_time",
        "collector_time",
        "publication_delay",
        "aggregation_lag",
        "symbol_mapping",
        "missingness_policy",
        "restatement_policy",
        "forward_only_flag",
    ]
    rows = []
    for _, source in feasibility.iterrows():
        for field in required:
            rows.append(
                {
                    "source": source["source"],
                    "required_field": field,
                    "required": True,
                    "status": "contract_required" if source["usable_for_next_search"] != "no_historical_alpha_search" else "required_before_any_future_use",
                }
            )
    return pd.DataFrame(rows)


def build_backfill_priority(feasibility: pd.DataFrame) -> pd.DataFrame:
    priority = {
        "aggTrades": (1, "large_but_feasible_with_official_files", "storage_budget_and_core12_monthly_backfill_manifest"),
        "open_interest_hist": (2, "not_historical_from_binance_rest", "external_archive_or_forward_only"),
        "global_long_short_account_ratio": (3, "not_historical_from_binance_rest", "external_archive_or_forward_only"),
        "liquidation_events": (4, "requires_vendor_or_collector", "source_contract_first"),
        "orderbook_depth_snapshot": (5, "requires_archive_or_collector", "probably_forward_only_initially"),
        "cross_exchange_basis_funding": (6, "requires_multi_venue_contract", "vendor_inventory_first"),
        "basis_rest": (7, "not_incremental_for_single_venue_history", "deprioritize_unless_cross_venue"),
        "top_trader_long_short_position_ratio": (8, "not_historical_from_binance_rest", "external_archive_or_forward_only"),
    }
    rows = []
    for _, row in feasibility.iterrows():
        rank, conclusion, next_action = priority.get(row["source"], (99, "unranked", "manual_review"))
        rows.append(
            {
                "priority": rank,
                "source": row["source"],
                "conclusion": conclusion,
                "next_action": next_action,
                "authorized_now": False,
            }
        )
    return pd.DataFrame(rows).sort_values("priority")


def write_report(now: str, feasibility: pd.DataFrame, pit: pd.DataFrame, priority: pd.DataFrame, authorization: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Crypto A7S-2 Field Semantics / Backfill Feasibility",
        "",
        f"- generated_at: `{now}`",
        "- decision: `HOLD_A7S2_DATA_BACKFILL_CONTRACT_REQUIRED`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- executes_download: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Decision",
        "",
        "A7S-2 confirms that the highest-value missing state variables cannot be used immediately for historical alpha search. Open interest and long/short ratios are locally recent/forward-only and the official REST history is short-window. Orderbook and liquidation require collectors or vendor archives. AggTrades is the only locally demonstrated scalable official-file path, but current local coverage is only one symbol/month and needs a storage/backfill contract before research use.",
        "",
        "## Source Feasibility Matrix",
        "",
        table(feasibility),
        "",
        "## PIT Semantics Contract",
        "",
        table(pit, max_rows=120),
        "",
        "## Backfill Priority",
        "",
        table(priority),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## External References Checked",
        "",
        "- Binance USD-M Open Interest Statistics: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest-Statistics",
        "- Binance USD-M Long/Short Ratio: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Long-Short-Ratio",
        "- Binance USD-M Top Trader Position Ratio: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Top-Trader-Long-Short-Ratio",
        "- Binance USD-M Aggregate Trades: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Compressed-Aggregate-Trades-List",
        "- Binance USD-M Order Book: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book",
        "- Binance USD-M Basis: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Basis",
    ]
    (REPORT_DIR / f"CRYPTO_A7S2_FIELD_SEMANTICS_BACKFILL_FEASIBILITY_{DATE_TAG}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    now = utc_stamp()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    feasibility = build_source_feasibility()
    pit = build_pit_contract(feasibility)
    priority = build_backfill_priority(feasibility)
    authorization = {
        "generated_at": now,
        "decision": "HOLD_A7S2_DATA_BACKFILL_CONTRACT_REQUIRED",
        "executes_search": False,
        "executes_replay": False,
        "executes_download": False,
        "authorizes_alpha_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_data_download": False,
        "authorizes_a7s3_costed_backfill_plan": True,
        "authorizes_a7t0_forward_locked_observation_contract": True,
        "primary_next": "A7S3_costed_backfill_plan_or_A7T0_forward_locked_observation",
        "blocking_findings": [
            "official_open_interest_and_long_short_rest_history_is_short_window",
            "orderbook_depth_requires_archive_or_forward_collector",
            "liquidation_events_require_source_contract",
            "cross_exchange_sources_absent_and_need_vendor_contract",
            "aggTrades_backfill_feasible_but_storage_heavy_and_not_currently_core12_complete",
        ],
    }

    feasibility.to_csv(OUT_DIR / "a7s2_source_feasibility_matrix.csv", index=False)
    pit.to_csv(OUT_DIR / "a7s2_pit_semantics_contract.csv", index=False)
    priority.to_csv(OUT_DIR / "a7s2_backfill_priority.csv", index=False)
    write_json(OUT_DIR / "a7s2_authorization_matrix.json", authorization)
    write_json(
        OUT_DIR / "a7s2_manifest.json",
        {
            "generated_at": now,
            "script": str(Path(__file__).relative_to(ROOT)),
            "outputs": [
                str((OUT_DIR / "a7s2_source_feasibility_matrix.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7s2_pit_semantics_contract.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7s2_backfill_priority.csv").relative_to(ROOT)),
                str((OUT_DIR / "a7s2_authorization_matrix.json").relative_to(ROOT)),
                f"reports/CRYPTO_A7S2_FIELD_SEMANTICS_BACKFILL_FEASIBILITY_{DATE_TAG}.md",
            ],
            "decision": authorization["decision"],
        },
    )
    write_report(now, feasibility, pit, priority, authorization)


if __name__ == "__main__":
    main()
