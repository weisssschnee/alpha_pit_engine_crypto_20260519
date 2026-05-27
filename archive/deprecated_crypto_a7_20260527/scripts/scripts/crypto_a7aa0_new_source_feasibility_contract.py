from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
PROBE_DIR = DATA_ROOT / "raw" / "source_probes" / "cross_exchange_20260522_core12_probe2"
PROBE_MANIFEST = PROBE_DIR / "cross_exchange_source_probe_manifest.csv"
OUT_DIR = ROOT / "runtime" / "a7aa0_new_source_feasibility_contract"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AA0_NEW_SOURCE_FEASIBILITY_PIT_CONTRACT_20260522.md"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 100) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def read_probe_manifest() -> pd.DataFrame:
    if not PROBE_MANIFEST.exists():
        return pd.DataFrame()
    return pd.read_csv(PROBE_MANIFEST)


def build_probe_summary(probe: pd.DataFrame) -> pd.DataFrame:
    if probe.empty:
        return pd.DataFrame(
            [
                {
                    "provider": "<missing>",
                    "dataset": "<missing>",
                    "ready": 0,
                    "total": 0,
                    "ready_rate": 0.0,
                    "history_depth": "missing_probe_manifest",
                    "proof_role": "not_available",
                    "decision": "HOLD_SOURCE_PROBE_MISSING",
                }
            ]
        )
    grouped = (
        probe.groupby(["provider", "dataset", "history_depth", "proof_role"], dropna=False)
        .agg(ready=("status", lambda s: int((s == "ready").sum())), total=("status", "size"), symbols=("symbol", lambda s: ",".join(sorted(set(map(str, s))))))
        .reset_index()
    )
    grouped["ready_rate"] = grouped["ready"] / grouped["total"].where(grouped["total"].ne(0), 1)
    grouped["decision"] = grouped.apply(classify_probe_row, axis=1)
    return grouped[
        [
            "provider",
            "dataset",
            "ready",
            "total",
            "ready_rate",
            "history_depth",
            "proof_role",
            "decision",
            "symbols",
        ]
    ].sort_values(["provider", "dataset"])


def classify_probe_row(row: pd.Series) -> str:
    if float(row["ready_rate"]) < 1.0:
        return "HOLD_COVERAGE_INCOMPLETE_OR_SYMBOL_MAPPING"
    history = str(row["history_depth"])
    role = str(row["proof_role"])
    dataset = str(row["dataset"])
    if "snapshot_only" in history:
        return "FORWARD_OBSERVATION_ONLY"
    if dataset == "liquidation_orders_probe":
        return "CONTRACT_REQUIRED_RECENT_LIQUIDATION_ONLY"
    if "recent" in history:
        return "RECENT_CONTEXT_ONLY_UNTIL_RETENTION_CONTRACT"
    if "historical" in role:
        return "CONTRACT_REVIEW_REQUIRED"
    return "CONTRACT_REQUIRED"


def build_source_feasibility(probe_summary: pd.DataFrame) -> pd.DataFrame:
    source_rows = [
        {
            "source_group": "liquidation_forced_flow",
            "local_evidence": evidence_for(probe_summary, "liquidation_orders_probe"),
            "independent_information": "forced deleveraging event flow; not derivable from OHLCV, aggTrades, OI, or funding",
            "current_local_status": "okx_recent_probe_ready_core12" if any(probe_summary["dataset"].eq("liquidation_orders_probe")) else "not_present",
            "historical_2024_2026_proof_allowed": False,
            "forward_observation_allowed": True,
            "priority": "P0",
            "next_action": "A7AA-1 liquidation event contract and retention-window audit",
            "blocking_questions": "event_time vs observable_time; state/side convention; retention window; pagination completeness; raw checksum/source trace",
        },
        {
            "source_group": "historical_orderbook_depth",
            "local_evidence": evidence_for(probe_summary, "orderbook_depth"),
            "independent_information": "displayed liquidity, spread, depth imbalance, and book pressure",
            "current_local_status": "snapshot_probe_ready_not_historical",
            "historical_2024_2026_proof_allowed": False,
            "forward_observation_allowed": True,
            "priority": "P0_if_vendor_history_exists_else_forward_only",
            "next_action": "A7AA-1 depth vendor/history feasibility; otherwise A7T forward snapshots only",
            "blocking_questions": "snapshot cadence; exchange update time; observable time; missingness; no historical backfill from current snapshots",
        },
        {
            "source_group": "cross_exchange_basis_funding_premium",
            "local_evidence": evidence_for(probe_summary, "funding_rate_history") + "; " + evidence_for(probe_summary, "basis_1h_recent"),
            "independent_information": "venue dispersion across funding, premium, basis, OI and liquidity",
            "current_local_status": "recent_or_snapshot_probe_ready_multiple_venues",
            "historical_2024_2026_proof_allowed": False,
            "forward_observation_allowed": True,
            "priority": "P0",
            "next_action": "A7AA-1 venue timestamp/symbol mapping and retention contract",
            "blocking_questions": "venue symbol map; settlement timing; funding availability; basis formula consistency; fee/cost convention",
        },
        {
            "source_group": "binance_metrics_historical",
            "local_evidence": "A7S-1 source trace complete with vendor 5m warnings",
            "independent_information": "open interest and long/short account/positioning state",
            "current_local_status": "accepted_data_line_state_layer",
            "historical_2024_2026_proof_allowed": True,
            "forward_observation_allowed": True,
            "priority": "completed",
            "next_action": "weak-prior state only; do not use standalone crowding motif",
            "blocking_questions": "vendor jitter warnings must remain attached to experiments",
        },
        {
            "source_group": "aggtrades_enhanced_historical",
            "local_evidence": "A7U-0R source trace complete for enhanced aggTrades panel",
            "independent_information": "trade-level aggressor flow and trade-size distribution",
            "current_local_status": "accepted_data_line_state_layer",
            "historical_2024_2026_proof_allowed": True,
            "forward_observation_allowed": True,
            "priority": "completed_core3_extend_core12_optional",
            "next_action": "state/interaction only; no standalone activity-liquidity replay expansion",
            "blocking_questions": "core12 expansion requires same raw checksum/source trace discipline",
        },
    ]
    return pd.DataFrame(source_rows)


def evidence_for(probe_summary: pd.DataFrame, dataset_fragment: str) -> str:
    if probe_summary.empty:
        return "no probe manifest"
    sub = probe_summary[probe_summary["dataset"].str.contains(dataset_fragment, case=False, na=False)]
    if sub.empty:
        return "no local probe rows"
    parts = []
    for _, row in sub.iterrows():
        parts.append(f"{row['provider']}:{row['dataset']} {int(row['ready'])}/{int(row['total'])} {row['history_depth']} {row['decision']}")
    return " ; ".join(parts)


def build_field_contract() -> pd.DataFrame:
    rows = [
        {
            "field_family": "liquidation_forced_flow",
            "candidate_fields": "liquidation_count; liquidation_notional; liquidation_buy_notional; liquidation_sell_notional; liquidation_imbalance; large_liquidation_count; liquidation_vwap; time_since_last_liquidation; liquidation_burst_1h_4h_24h",
            "independent_source": "yes",
            "required_raw_fields": "event_time; side/position_side; price; quantity; notional; instrument; venue; state=filled; request_time; collector_time",
            "observable_time_rule": "max(exchange_event_publish_time, collector_time) until publication semantics are proven",
            "allowed_use_before_contract": "none for historical proof; forward observation only",
            "blocked_use": "ranking/search/replay on 2024-2026 until retention and pagination are proven",
        },
        {
            "field_family": "orderbook_depth",
            "candidate_fields": "spread_bps; depth_bid_notional_5_10_20_50; depth_ask_notional_5_10_20_50; depth_imbalance; book_slope; depth_pressure; depth_change; cross_venue_depth_dispersion",
            "independent_source": "yes",
            "required_raw_fields": "exchange_update_time; bids/asks levels; collector_time; venue; symbol; snapshot_id or request sequence",
            "observable_time_rule": "collector_time for snapshots unless exchange update timestamp and collection delay are validated",
            "allowed_use_before_contract": "A7T forward-only observation",
            "blocked_use": "historical proof from forward snapshots; synthetic historical depth backfill",
        },
        {
            "field_family": "cross_exchange_basis_funding_premium",
            "candidate_fields": "funding_spread_by_venue; premium_spread_by_venue; basis_spread_by_venue; venue_oi_dispersion; funding_rank_by_venue; basis_rank_by_venue; perp_spot_basis_dispersion",
            "independent_source": "yes",
            "required_raw_fields": "venue; symbol_map; mark/index/premium/funding timestamp; funding settlement time; contract type; quote currency; fees",
            "observable_time_rule": "field-specific latest-known observable time; settlement-after-use values forbidden",
            "allowed_use_before_contract": "recent context diagnostics only",
            "blocked_use": "merged venue panel without timestamp and symbol mapping contract",
        },
        {
            "field_family": "derived_transforms",
            "candidate_fields": "change_1h_4h_24h; zscore_168h; interactions; residuals",
            "independent_source": "no",
            "required_raw_fields": "inherits parent source",
            "observable_time_rule": "past-only rolling windows; no forward fill through missing vendor gaps unless explicitly marked",
            "allowed_use_before_contract": "only if parent field contract passes",
            "blocked_use": "counting transforms as new independent sources",
        },
    ]
    return pd.DataFrame(rows)


def build_pit_policy() -> pd.DataFrame:
    rows = [
        {
            "policy_id": "PIT_001",
            "requirement": "Every new field must record raw_event_time, observable_time, collector_time, and feature_available_time.",
            "reason": "Prevents settlement-after-use and snapshot backfill leakage.",
            "blocking_if_missing": True,
        },
        {
            "policy_id": "PIT_002",
            "requirement": "Snapshot-only orderbook/OI endpoints are forward observation, not historical proof.",
            "reason": "Current probes collect current state only.",
            "blocking_if_missing": True,
        },
        {
            "policy_id": "PIT_003",
            "requirement": "Recent-history endpoints need retention-window and pagination completeness audit before backfill use.",
            "reason": "A recent API window does not prove 2024-2026 historical availability.",
            "blocking_if_missing": True,
        },
        {
            "policy_id": "PIT_004",
            "requirement": "May stress remains post-selection stress/veto/failure attribution only.",
            "reason": "Avoids known-stress overfit.",
            "blocking_if_missing": True,
        },
        {
            "policy_id": "PIT_005",
            "requirement": "No source enters replay without cost/lag/residual/control/symbol-month LOO reporting plan.",
            "reason": "Maintains A7 validation standard.",
            "blocking_if_missing": True,
        },
    ]
    return pd.DataFrame(rows)


def build_authorization(probe_summary: pd.DataFrame) -> dict[str, Any]:
    ready = int(probe_summary["ready"].sum()) if not probe_summary.empty and "ready" in probe_summary else 0
    total = int(probe_summary["total"].sum()) if not probe_summary.empty and "total" in probe_summary else 0
    return {
        "decision": "PASS_A7AA0_SOURCE_FEASIBILITY_CONTRACT_READY_HISTORICAL_BACKFILL_NOT_AUTHORIZED",
        "generated_at": utc_stamp(),
        "executes_download": False,
        "executes_search": False,
        "executes_replay": False,
        "probe_ready_endpoints": ready,
        "probe_total_endpoints": total,
        "authorizes_a7aa1_liquidation_contract": True,
        "authorizes_a7aa1_cross_exchange_contract": True,
        "authorizes_a7t_forward_observation": True,
        "authorizes_historical_alpha_replay": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": [
            "liquidation retention/pagination/PIT contract unresolved",
            "historical orderbook depth source not validated; current snapshots are forward-only",
            "cross-exchange recent probes do not establish 2024-2026 historical proof",
        ],
        "required_next": [
            "A7AA-1 liquidation event source contract and sample retention audit",
            "A7AA-1 cross-exchange venue mapping/PIT contract",
            "A7T forward-only observation for orderbook/depth and positioning snapshots",
        ],
    }


def write_report(
    probe_summary: pd.DataFrame,
    feasibility: pd.DataFrame,
    fields: pd.DataFrame,
    pit: pd.DataFrame,
    auth: dict[str, Any],
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# CRYPTO A7AA-0 New Source Feasibility PIT Contract",
        "",
        f"Generated: {auth['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{auth['decision']}`",
        "",
        "A7AA-0 is a contract stage only. It does not download new data, search formulas, run replay, or authorize alpha proof.",
        "",
        "## Summary",
        "",
        f"- Cross-exchange/local probe endpoints ready: {auth['probe_ready_endpoints']} / {auth['probe_total_endpoints']}.",
        "- Ready probe endpoint does not imply historical proof. Snapshot-only endpoints remain forward observation.",
        "- Liquidation, historical depth, and cross-exchange dispersion are independent information sources, but require PIT/source contracts before replay.",
        "",
        "## Probe Dataset Summary",
        "",
        table(probe_summary, max_rows=120),
        "",
        "## Source Feasibility",
        "",
        table(feasibility),
        "",
        "## Field Contract",
        "",
        table(fields),
        "",
        "## PIT Policy",
        "",
        table(pit),
        "",
        "## Authorization",
        "",
        table(pd.DataFrame([auth])),
        "",
        "## Practical Next Tasks",
        "",
        "1. For liquidation: audit OKX liquidation rows for event timestamp, side convention, retention window, pagination, and whether Bybit/Binance provide comparable historical forced-flow fields.",
        "2. For orderbook/depth: keep current snapshots in A7T forward observation unless a validated historical depth vendor/source is available.",
        "3. For cross-exchange: build venue symbol mapping and timestamp contracts before constructing any merged feature panel.",
        "4. Do not count derived transforms as independent sources; `change`, `zscore`, `spread`, and interactions inherit their parent source contract.",
        "",
        "## Blocked",
        "",
        "- No historical alpha replay on probe files.",
        "- No A7V/A7S/A7Y clue expansion.",
        "- No alpha proof, shadow, paper, or live.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    probe = read_probe_manifest()
    probe_summary = build_probe_summary(probe)
    feasibility = build_source_feasibility(probe_summary)
    fields = build_field_contract()
    pit = build_pit_policy()
    auth = build_authorization(probe_summary)
    manifest = {
        "decision": auth["decision"],
        "generated_at": auth["generated_at"],
        "probe_manifest": str(PROBE_MANIFEST),
        "probe_rows": int(len(probe)),
        "probe_summary_rows": int(len(probe_summary)),
        "field_contract_rows": int(len(fields)),
        "executes_download": False,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_alpha_proof": False,
    }
    probe_summary.to_csv(OUT_DIR / "a7aa0_probe_dataset_summary.csv", index=False)
    feasibility.to_csv(OUT_DIR / "a7aa0_source_feasibility_matrix.csv", index=False)
    fields.to_csv(OUT_DIR / "a7aa0_field_contract.csv", index=False)
    pit.to_csv(OUT_DIR / "a7aa0_pit_policy.csv", index=False)
    write_json(OUT_DIR / "a7aa0_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7aa0_manifest.json", manifest)
    write_report(probe_summary, feasibility, fields, pit, auth)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
