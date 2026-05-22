from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path("G:/AlphaFactory_CryptoData")
PANEL_PATH = DATA_ROOT / "gold" / "panels" / "crypto_core12_1h_with_aggtrades_features_v1.parquet"
PANEL_REPORT_GLOB = DATA_ROOT / "reports"
AGG_ROOT = DATA_ROOT / "gold" / "microstructure" / "aggtrades_1h_flow_enhanced_v1"
ORDERBOOK_FORWARD_ROOT = DATA_ROOT / "silver" / "binance_api" / "orderbook_forward_snapshot"
POSITIONING_FORWARD_STATE = DATA_ROOT / "metadata" / "positioning_forward_state.csv"

OUT_DIR = ROOT / "runtime" / "a7s0_data_horizon_contract"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7S0_DATA_HORIZON_CONTRACT_20260522.md"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def latest_panel_report() -> dict[str, Any]:
    reports = sorted(PANEL_REPORT_GLOB.glob("crypto_core12_1h_with_aggtrades_features_v1_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not reports:
        return {}
    return json.loads(reports[0].read_text(encoding="utf-8"))


def panel_inventory(report: dict[str, Any]) -> pd.DataFrame:
    rows = []
    if report.get("coverage_by_symbol"):
        for rec in report["coverage_by_symbol"]:
            rows.append(
                {
                    "symbol": rec["symbol"],
                    "panel_rows": rec["rows"],
                    "agg_rows": rec["agg_rows"],
                    "agg_coverage": rec["agg_coverage"],
                    "timestamp_min": rec["timestamp_min"],
                    "timestamp_max": rec["timestamp_max"],
                    "agg_status": "agg_ready_core3" if rec["agg_rows"] else "agg_missing_for_symbol",
                }
            )
    return pd.DataFrame(rows)


def data_source_inventory(report: dict[str, Any]) -> pd.DataFrame:
    rows = [
        {
            "source_id": "base_core12_1h_market_funding_mark_index",
            "local_path": str(DATA_ROOT / "gold" / "panels" / "crypto_core12_1h_v1.parquet"),
            "current_status": "READY_EXISTING_PANEL",
            "historical_proof_allowed": True,
            "forward_only": False,
            "pit_requirements": "existing A7 linkage/funding contracts remain binding; feature_time < execution_time",
            "next_action": "usable as baseline panel only; do not treat prior funding-family results as alpha proof",
        },
        {
            "source_id": "aggtrades_enhanced_v1_core3",
            "local_path": str(AGG_ROOT),
            "current_status": "READY_CORE3_SOURCE_TRACE_PASS",
            "historical_proof_allowed": True,
            "forward_only": False,
            "pit_requirements": "timestamp is hour bucket start; feature observable only after hour close; raw checksum/source trace must remain closed",
            "next_action": "use as state/interaction/horizon feature; do not expand failed activity-liquidity standalone family",
        },
        {
            "source_id": "aggtrades_enhanced_v1_remaining_core12",
            "local_path": str(AGG_ROOT),
            "current_status": "MISSING_FOR_9_CORE12_SYMBOLS",
            "historical_proof_allowed": False,
            "forward_only": False,
            "pit_requirements": "same raw zip checksum/source trace as A7U-0R before experiment use",
            "next_action": "data-line can backfill; experiment-line must wait for source trace pass before core12 agg search",
        },
        {
            "source_id": "orderbook_forward_snapshot",
            "local_path": str(ORDERBOOK_FORWARD_ROOT),
            "current_status": "FORWARD_ONLY_AVAILABLE",
            "historical_proof_allowed": False,
            "forward_only": True,
            "pit_requirements": "collector_time/observable_time/event_time retained; no historical backfill into 2024-2026 proof",
            "next_action": "use only for A7T forward observation/live-shadow context until sufficient append-only history exists",
        },
        {
            "source_id": "positioning_forward_oi_longshort_taker_ratio",
            "local_path": str(POSITIONING_FORWARD_STATE),
            "current_status": "FORWARD_ONLY_AVAILABLE",
            "historical_proof_allowed": False,
            "forward_only": True,
            "pit_requirements": "event_time/observable_time/collector_time and forward_only_flag required; no historical proof use",
            "next_action": "append-only observation only; historical use requires separate PIT contract and raw trace",
        },
        {
            "source_id": "liquidation_forced_flow",
            "local_path": "",
            "current_status": "NOT_PRESENT_CONTRACT_REQUIRED",
            "historical_proof_allowed": False,
            "forward_only": False,
            "pit_requirements": "event_time and exchange publication semantics; no future aggregate leakage; raw/source trace required",
            "next_action": "high-value candidate source after data contract, sample audit, and checksum trace",
        },
        {
            "source_id": "cross_exchange_basis_funding_depth",
            "local_path": "",
            "current_status": "NOT_PRESENT_CONTRACT_REQUIRED",
            "historical_proof_allowed": False,
            "forward_only": False,
            "pit_requirements": "venue-specific observable_time, symbol mapping, trading calendar, fee/cost convention, and missingness contract",
            "next_action": "do not search before venue/PIT/symbol contract",
        },
    ]
    for row in rows:
        path = row["local_path"]
        row["path_exists"] = bool(path and Path(path).exists())
    row_meta = {
        "source_id": "unified_core12_1h_with_aggtrades_features_v1",
        "local_path": str(PANEL_PATH),
        "current_status": "READY_PANEL_FOR_CONTROLLED_EXPERIMENTS",
        "historical_proof_allowed": True,
        "forward_only": False,
        "pit_requirements": "inherits base panel plus aggTrades feature availability mask",
        "next_action": "primary experiment input for controlled diagnostics only",
        "path_exists": PANEL_PATH.exists(),
        "panel_rows": report.get("output_rows"),
        "panel_columns": report.get("output_columns"),
        "agg_feature_columns": report.get("agg_feature_columns"),
        "agg_symbol_month_count": report.get("agg_symbol_month_count"),
    }
    return pd.concat([pd.DataFrame([row_meta]), pd.DataFrame(rows)], ignore_index=True)


def pit_timestamp_contract() -> pd.DataFrame:
    rows = [
        {
            "field_family": "base_1h_ohlcv_mark_index_premium",
            "timestamp_semantics": "1h bar bucket start",
            "observable_time_rule": "bar close plus processing lag; usable next bar or later",
            "historical_proof_status": "allowed_if_existing_A7_alignment_holds",
            "forbidden_use": "same-bar close execution or feature_time >= execution_time",
        },
        {
            "field_family": "funding_observable",
            "timestamp_semantics": "funding event / known funding field time",
            "observable_time_rule": "latest-known only; settlement-after-use forbidden",
            "historical_proof_status": "allowed only under A7D/A7E funding semantics",
            "forbidden_use": "next_funding_rate or future settlement rate as signal",
        },
        {
            "field_family": "aggtrades_enhanced_1h",
            "timestamp_semantics": "floor(event_time, 1h) bucket start",
            "observable_time_rule": "1h aggregate visible only after hour end",
            "historical_proof_status": "allowed for BTC/ETH/SOL after A7U-0R source trace pass",
            "forbidden_use": "using current hour aggregate for execution inside same hour",
        },
        {
            "field_family": "orderbook_forward_snapshot",
            "timestamp_semantics": "collector_time / observable_time / event_time snapshot",
            "observable_time_rule": "forward-only snapshot visible after collector_time",
            "historical_proof_status": "not allowed for 2024-2026 historical proof",
            "forbidden_use": "backfill into historical search or May stress proof",
        },
        {
            "field_family": "positioning_forward",
            "timestamp_semantics": "API event_time plus collector_time",
            "observable_time_rule": "append-only forward observation only",
            "historical_proof_status": "not allowed until separate historical PIT contract",
            "forbidden_use": "retroactive history fill for alpha proof",
        },
    ]
    return pd.DataFrame(rows)


def feature_family_contract() -> pd.DataFrame:
    rows = [
        {
            "feature_family": "aggtrades_flow_state",
            "allowed_role": "state/interactor/horizon diagnostic",
            "blocked_role": "standalone activity/liquidity alpha expansion",
            "must_report": "standalone ablation; matched controls; 20bps; lag stress; May stress-only label",
        },
        {
            "feature_family": "aggtrades_large_trade_intensity",
            "allowed_role": "liquidity stress / size regime feature",
            "blocked_role": "raw large-trade bucket rank as candidate without controls",
            "must_report": "control dominance and symbol-tier attribution",
        },
        {
            "feature_family": "basis_premium_interaction",
            "allowed_role": "interaction with aggTrades or volatility state",
            "blocked_role": "funding/basis wrapper without residual vs FundingCore/Core4",
            "must_report": "FundingCore/Core4 residual and wrong-lag funding warning",
        },
        {
            "feature_family": "orderbook_depth_forward",
            "allowed_role": "forward observation context",
            "blocked_role": "historical alpha proof",
            "must_report": "append-only collector_time/observable_time audit",
        },
        {
            "feature_family": "liquidation_forced_flow_future_contract",
            "allowed_role": "new data candidate after PIT/source contract",
            "blocked_role": "search before field semantics and publication delay are verified",
            "must_report": "event-time availability, liquidation side convention, venue coverage, source trace",
        },
    ]
    return pd.DataFrame(rows)


def horizon_execution_contract() -> pd.DataFrame:
    horizons = ["H4", "H8", "H12", "H24", "H48", "H72", "H96", "mixed_H12_H48", "mixed_H24_H96"]
    rows = []
    for horizon in horizons:
        rows.append(
            {
                "horizon_class": horizon,
                "signal_frequency": "1h source panel with slower aggregation/rebalance",
                "execution_lags_required": "1bar;2bar;3bar",
                "primary_cost_bps": 10,
                "stress_cost_bps": "20;30",
                "success_metric_for_diagnostic": "cost/lag survival improves without negative-control contamination",
                "authorization": "diagnostic_only_not_alpha_proof",
            }
        )
    return pd.DataFrame(rows)


def cost_lag_contract() -> pd.DataFrame:
    rows = [
        {"scenario": "normal", "cost_bps": 10, "execution_lag": "1bar", "required_for": "all diagnostics"},
        {"scenario": "stress", "cost_bps": 20, "execution_lag": "1bar", "required_for": "candidate clue label"},
        {"scenario": "severe", "cost_bps": 30, "execution_lag": "2bar;3bar", "required_for": "horizon reset comparison"},
        {"scenario": "zero_cost_diagnostic", "cost_bps": 0, "execution_lag": "1bar", "required_for": "failure attribution only, never promotion"},
    ]
    return pd.DataFrame(rows)


def write_report(
    now: str,
    inventory: pd.DataFrame,
    panel: pd.DataFrame,
    pit: pd.DataFrame,
    features: pd.DataFrame,
    horizons: pd.DataFrame,
    costs: pd.DataFrame,
    authorization: dict[str, Any],
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Crypto A7S-0 Data / Horizon Contract",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7S-0 defines what data and horizons may enter the next crypto research stage after A7X-4. It does not run alpha search.",
        "",
        "The key distinction is historical-proof eligible vs forward-only. Forward-only fields can support observation and future locked tests, not 2024-2026 historical proof.",
        "",
        "## Source Inventory",
        "",
        table(inventory, max_rows=40),
        "",
        "## Panel Coverage",
        "",
        table(panel, max_rows=20),
        "",
        "## PIT Timestamp Contract",
        "",
        table(pit, max_rows=20),
        "",
        "## Feature Family Contract",
        "",
        table(features, max_rows=20),
        "",
        "## Horizon / Execution Contract",
        "",
        table(horizons, max_rows=20),
        "",
        "## Cost / Lag Contract",
        "",
        table(costs, max_rows=20),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- A7S-1 field availability/source-trace audit when additional data arrives.",
        "- A7R/A7S horizon diagnostic only after the contract is frozen.",
        "- No historical proof use of orderbook or positioning forward fields until append-only history exists.",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    report = latest_panel_report()
    panel = panel_inventory(report)
    inventory = data_source_inventory(report)
    pit = pit_timestamp_contract()
    features = feature_family_contract()
    horizons = horizon_execution_contract()
    costs = cost_lag_contract()
    blockers = []
    if not PANEL_PATH.exists():
        blockers.append("unified_panel_missing")
    if panel.empty:
        blockers.append("panel_coverage_missing")

    decision = "PASS_A7S0_DATA_HORIZON_CONTRACT_READY" if not blockers else "HOLD_A7S0_CONTRACT_INPUT_MISSING"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "unified_panel": str(PANEL_PATH),
        "panel_exists": PANEL_PATH.exists(),
        "panel_rows": report.get("output_rows"),
        "panel_columns": report.get("output_columns"),
        "agg_feature_columns": report.get("agg_feature_columns"),
        "agg_symbol_month_count": report.get("agg_symbol_month_count"),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7s1_field_availability_audit": not blockers,
        "authorizes_a7r_horizon_diagnostic_contract": not blockers,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "forward_only_fields_allowed_for_historical_proof": False,
        "may_policy": "stress_only_not_ranking_generation_threshold_or_allocation",
        "required_next": [
            "A7S-1 audit any newly delivered OI/liquidation/orderbook/cross-exchange data before search",
            "A7R horizon diagnostic may run only as diagnostic, not alpha proof",
            "A7T forward-locked observation contract for forward-only fields",
        ],
    }

    inventory.to_csv(OUT_DIR / "a7s0_candidate_data_sources.csv", index=False)
    panel.to_csv(OUT_DIR / "a7s0_panel_coverage.csv", index=False)
    pit.to_csv(OUT_DIR / "a7s0_pit_timestamp_contract.csv", index=False)
    features.to_csv(OUT_DIR / "a7s0_feature_family_contract.csv", index=False)
    horizons.to_csv(OUT_DIR / "a7s0_horizon_execution_contract.csv", index=False)
    costs.to_csv(OUT_DIR / "a7s0_cost_lag_contract.csv", index=False)
    write_json(OUT_DIR / "a7s0_authorization_matrix.json", authorization)
    write_json(OUT_DIR / "a7s0_manifest.json", {"generated_at": now, "decision": decision, "output_dir": str(OUT_DIR), "report": str(REPORT_PATH)})
    write_report(now, inventory, panel, pit, features, horizons, costs, authorization)
    print(json.dumps({"decision": decision, "blockers": blockers, "authorizes_a7s1": authorization["authorizes_a7s1_field_availability_audit"]}, indent=2))


if __name__ == "__main__":
    main()
