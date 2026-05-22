from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

A7AA0_AUTH = ROOT / "runtime" / "a7aa0_new_source_feasibility_contract" / "a7aa0_authorization_matrix.json"
A7AB0_AUTH = ROOT / "runtime" / "a7ab0_forward_data_handoff_audit" / "a7ab0_authorization_matrix.json"

CROSS_SNAPSHOT = DATA_ROOT / "silver" / "cross_exchange_forward_snapshot" / "cross_exchange_forward_snapshot_20260522_core12_probe2.parquet"
ORDERBOOK_ROOT = DATA_ROOT / "silver" / "binance_api" / "orderbook_forward_snapshot"
POSITIONING_MANIFEST_ROOT = DATA_ROOT / "manifests"
POSITIONING_STATE = DATA_ROOT / "metadata" / "positioning_forward_state.csv"

OUT_DIR = ROOT / "runtime" / "a7t0_forward_telemetry_contract"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7T0_FORWARD_TELEMETRY_CONTRACT_20260522.md"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 100) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def audit_cross_snapshot() -> dict[str, Any]:
    if not CROSS_SNAPSHOT.exists():
        return {
            "source_id": "cross_exchange_forward_snapshot",
            "path": str(CROSS_SNAPSHOT),
            "exists": False,
            "rows": 0,
            "symbols": 0,
            "providers": "",
            "latest_observable_time": "",
            "decision": "HOLD_MISSING",
        }
    df = pd.read_parquet(CROSS_SNAPSHOT)
    return {
        "source_id": "cross_exchange_forward_snapshot",
        "path": str(CROSS_SNAPSHOT),
        "exists": True,
        "rows": int(len(df)),
        "symbols": int(df["symbol"].nunique()) if "symbol" in df.columns else 0,
        "providers": ",".join(sorted(map(str, df["provider"].dropna().unique()))) if "provider" in df.columns else "",
        "feature_groups": ",".join(sorted(map(str, df["feature_group"].dropna().unique()))) if "feature_group" in df.columns else "",
        "latest_observable_time": str(pd.to_datetime(df["observable_time"], errors="coerce", utc=True).max()) if "observable_time" in df.columns else "",
        "forward_only_rows": int(df["is_forward_only"].fillna(False).sum()) if "is_forward_only" in df.columns else 0,
        "historical_backfill_rows": int(df["is_historical_backfill"].fillna(False).sum()) if "is_historical_backfill" in df.columns else 0,
        "decision": "READY_FORWARD_TELEMETRY_SAMPLE",
    }


def audit_orderbook_runs() -> dict[str, Any]:
    files = sorted(ORDERBOOK_ROOT.glob("run=*/part.parquet")) if ORDERBOOK_ROOT.exists() else []
    rows = 0
    symbols: set[str] = set()
    latest = None
    for path in files:
        try:
            df = pd.read_parquet(path)
        except Exception:
            continue
        rows += int(len(df))
        if "symbol" in df.columns:
            symbols.update(map(str, df["symbol"].dropna().unique()))
        if "observable_time" in df.columns:
            ts = pd.to_datetime(df["observable_time"], errors="coerce", utc=True).max()
            if pd.notna(ts) and (latest is None or ts > latest):
                latest = ts
    return {
        "source_id": "binance_orderbook_forward_snapshot",
        "path": str(ORDERBOOK_ROOT),
        "exists": ORDERBOOK_ROOT.exists(),
        "runs": int(len(files)),
        "rows": rows,
        "symbols": int(len(symbols)),
        "providers": "binance",
        "feature_groups": "orderbook_depth",
        "latest_observable_time": str(latest) if latest is not None else "",
        "forward_only_rows": rows,
        "historical_backfill_rows": 0,
        "decision": "READY_FORWARD_TELEMETRY_SAMPLE" if files else "HOLD_MISSING",
    }


def audit_positioning_forward() -> dict[str, Any]:
    manifests = sorted(POSITIONING_MANIFEST_ROOT.glob("positioning_forward_5m_*_manifest.csv")) if POSITIONING_MANIFEST_ROOT.exists() else []
    rows = 0
    downloaded = 0
    errors = 0
    endpoints: set[str] = set()
    symbols: set[str] = set()
    latest_manifest = ""
    for path in manifests:
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        latest_manifest = str(path)
        rows += int(df["row_count"].sum()) if "row_count" in df.columns else 0
        downloaded += int((df["status"] == "downloaded").sum()) if "status" in df.columns else 0
        errors += int((df["status"] == "error").sum()) if "status" in df.columns else 0
        if "endpoint" in df.columns:
            endpoints.update(map(str, df["endpoint"].dropna().unique()))
        if "symbol" in df.columns:
            symbols.update(map(str, df["symbol"].dropna().unique()))
    state_rows = 0
    if POSITIONING_STATE.exists():
        try:
            state_rows = int(len(pd.read_csv(POSITIONING_STATE)))
        except Exception:
            state_rows = 0
    return {
        "source_id": "binance_positioning_forward_5m",
        "path": str(POSITIONING_MANIFEST_ROOT),
        "exists": bool(manifests),
        "runs": int(len(manifests)),
        "rows": rows,
        "symbols": int(len(symbols)),
        "providers": "binance",
        "feature_groups": ",".join(sorted(endpoints)),
        "latest_manifest": latest_manifest,
        "downloaded_manifest_rows": downloaded,
        "error_manifest_rows": errors,
        "state_file": str(POSITIONING_STATE),
        "state_rows": state_rows,
        "forward_only_rows": rows,
        "historical_backfill_rows": 0,
        "decision": "READY_FORWARD_TELEMETRY_SAMPLE" if manifests and errors == 0 else "HOLD_FORWARD_MANIFEST_ERRORS",
    }


def build_inventory() -> pd.DataFrame:
    return pd.DataFrame([audit_cross_snapshot(), audit_orderbook_runs(), audit_positioning_forward()]).fillna("")


def build_schema_contract() -> pd.DataFrame:
    rows = [
        {
            "schema_section": "identity",
            "required_fields": "source_id; provider; dataset; symbol; venue_symbol; feature_group",
            "purpose": "Stable routing, venue mapping, and symbol-level coverage.",
            "blocking_if_missing": True,
        },
        {
            "schema_section": "time_contract",
            "required_fields": "collection_time; observable_time; event_time; feature_available_time; timezone",
            "purpose": "PIT alignment and append-only evidence boundary.",
            "blocking_if_missing": True,
        },
        {
            "schema_section": "source_trace",
            "required_fields": "raw_path; raw_sha256; source_url; request_time; response_status; collector_version",
            "purpose": "Reproducibility and source audit.",
            "blocking_if_missing": True,
        },
        {
            "schema_section": "forward_flags",
            "required_fields": "forward_only_flag; no_historical_backfill_flag; is_historical_backfill",
            "purpose": "Prevents accidental historical proof use.",
            "blocking_if_missing": True,
        },
        {
            "schema_section": "orderbook_depth",
            "required_fields": "best_bid; best_ask; spread_bps; depth_bid_notional_5/10/20; depth_ask_notional_5/10/20; depth_imbalance_5/10/20",
            "purpose": "Displayed liquidity telemetry.",
            "blocking_if_missing": False,
        },
        {
            "schema_section": "liquidation_recent",
            "required_fields": "liquidation_buy_notional; liquidation_sell_notional; liquidation_count; large_liquidation_notional; liquidation_imbalance",
            "purpose": "Forward/recent forced-flow pressure telemetry.",
            "blocking_if_missing": False,
        },
        {
            "schema_section": "positioning_forward",
            "required_fields": "openInterestHist; globalLongShortAccountRatio; topLongShortAccountRatio; topLongShortPositionRatio; takerlongshortRatio",
            "purpose": "Append-only positioning telemetry.",
            "blocking_if_missing": False,
        },
        {
            "schema_section": "basis_funding_cross_exchange",
            "required_fields": "funding_rate; basis; basis_rate; premium; mark_price; index_price; next_funding_time; venue",
            "purpose": "Cross-venue basis/funding dispersion telemetry.",
            "blocking_if_missing": False,
        },
    ]
    return pd.DataFrame(rows)


def build_append_only_policy() -> pd.DataFrame:
    rows = [
        {
            "policy_id": "A7T_APPEND_001",
            "rule": "All forward telemetry writes are append-only; existing raw/silver rows cannot be overwritten.",
            "enforcement": "partition by run/date; write new manifest per run; quarantine repairs in separate repair path",
        },
        {
            "policy_id": "A7T_APPEND_002",
            "rule": "Forward-only fields cannot be joined to historical proof windows before their collection timestamp.",
            "enforcement": "feature_available_time >= observable_time; no_historical_backfill_flag must remain true",
        },
        {
            "policy_id": "A7T_APPEND_003",
            "rule": "Any schema change increments collector_version and starts a new compatibility segment.",
            "enforcement": "collector_version and schema_hash in manifest",
        },
        {
            "policy_id": "A7T_APPEND_004",
            "rule": "May 2026 remains stress/failure-attribution only and is never used for telemetry ranking/tuning.",
            "enforcement": "May columns absent from collector, ranking, and scheduler inputs",
        },
        {
            "policy_id": "A7T_APPEND_005",
            "rule": "Telemetry may become alpha evidence only after a locked forward window and a separate replay/proof gate.",
            "enforcement": "A7T cannot authorize alpha proof; later stage must freeze candidate definitions before forward window",
        },
    ]
    return pd.DataFrame(rows)


def build_schedule() -> pd.DataFrame:
    rows = [
        {
            "collector": "cross_exchange_forward_snapshot",
            "cadence": "hourly or 15min during experiment hours",
            "minimum_fields": "provider/dataset/symbol/observable_time/raw_sha256/feature_group",
            "primary_use": "forward telemetry dashboard and source coverage",
            "historical_proof_use": "blocked",
        },
        {
            "collector": "binance_orderbook_forward_snapshot",
            "cadence": "hourly baseline; 15min optional during stress periods",
            "minimum_fields": "best bid/ask, spread, depth notional, depth imbalance",
            "primary_use": "liquidity state and depth telemetry",
            "historical_proof_use": "blocked",
        },
        {
            "collector": "binance_positioning_forward_5m",
            "cadence": "daily append catch-up; source period remains 5m",
            "minimum_fields": "event_time, observable_time, collector_time, forward flags, raw sha256",
            "primary_use": "positioning telemetry and future append-only history",
            "historical_proof_use": "blocked until accumulated after collector freeze",
        },
        {
            "collector": "daily_forward_health_report",
            "cadence": "daily",
            "minimum_fields": "row counts, missing symbols, stale feeds, schema hash, error count",
            "primary_use": "collector operations and proof hygiene",
            "historical_proof_use": "audit metadata only",
        },
    ]
    return pd.DataFrame(rows)


def build_evidence_boundary() -> pd.DataFrame:
    rows = [
        {
            "evidence_type": "source_audit",
            "allowed_now": True,
            "minimum_condition": "raw_path/raw_sha256/source_url/time fields present",
            "notes": "A7T can support source audit and telemetry design.",
        },
        {
            "evidence_type": "forward_telemetry",
            "allowed_now": True,
            "minimum_condition": "append-only collector with manifest and schema version",
            "notes": "Telemetry only; no trading authorization.",
        },
        {
            "evidence_type": "historical_alpha_proof",
            "allowed_now": False,
            "minimum_condition": "not allowed from forward-only snapshots",
            "notes": "Requires independent historical source contract or future append-only proof window.",
        },
        {
            "evidence_type": "research_candidate",
            "allowed_now": False,
            "minimum_condition": "candidate definitions frozen before forward window; controls/cost/lag/LOO required",
            "notes": "A7T does not produce candidates.",
        },
        {
            "evidence_type": "shadow_paper_live",
            "allowed_now": False,
            "minimum_condition": "separate alpha proof gate",
            "notes": "Explicitly blocked.",
        },
    ]
    return pd.DataFrame(rows)


def build_authorization(inventory: pd.DataFrame) -> dict[str, Any]:
    ready_sources = int(inventory["decision"].eq("READY_FORWARD_TELEMETRY_SAMPLE").sum()) if not inventory.empty else 0
    warnings = []
    not_ready = inventory[~inventory["decision"].eq("READY_FORWARD_TELEMETRY_SAMPLE")] if not inventory.empty else pd.DataFrame()
    for _, row in not_ready.iterrows():
        warnings.append(f"{row.get('source_id')}: {row.get('decision')}")
    return {
        "decision": "PASS_A7T0_FORWARD_TELEMETRY_CONTRACT_READY",
        "generated_at": utc_stamp(),
        "executes_download": False,
        "executes_search": False,
        "executes_replay": False,
        "ready_forward_sources": ready_sources,
        "total_forward_sources": int(len(inventory)),
        "authorizes_forward_telemetry_collection_design": True,
        "authorizes_append_only_observation": True,
        "authorizes_historical_alpha_proof": False,
        "authorizes_research_candidate": False,
        "authorizes_shadow_paper_live": False,
        "blockers": [
            "forward-only snapshots cannot be historical proof",
            "liquidation retention/pagination contract unresolved",
            "orderbook historical source not validated",
            "no candidate definitions are frozen in A7T-0",
        ],
        "warnings": warnings,
        "required_next": [
            "Implement daily forward telemetry health report",
            "Add collector_version/schema_hash to forward manifests",
            "Keep A7AA-1 contracts for liquidation/cross-exchange historical feasibility separate",
        ],
    }


def write_report(
    inventory: pd.DataFrame,
    schema: pd.DataFrame,
    policy: pd.DataFrame,
    schedule: pd.DataFrame,
    boundary: pd.DataFrame,
    auth: dict[str, Any],
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# CRYPTO A7T-0 Forward Telemetry Contract",
        "",
        f"Generated: {auth['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{auth['decision']}`",
        "",
        "A7T-0 defines the forward telemetry contract. It does not download data, run replay, search formulas, or authorize historical alpha proof.",
        "",
        "## Source Inventory",
        "",
        table(inventory),
        "",
        "## Telemetry Schema Contract",
        "",
        table(schema),
        "",
        "## Append-Only Policy",
        "",
        table(policy),
        "",
        "## Collector Schedule",
        "",
        table(schedule),
        "",
        "## Evidence Boundary",
        "",
        table(boundary),
        "",
        "## Authorization",
        "",
        table(pd.DataFrame([auth])),
        "",
        "## Required Next Action",
        "",
        "1. Add `collector_version` and `schema_hash` to forward collector manifests.",
        "2. Produce a daily forward health report covering row counts, stale feeds, missing symbols, schema drift, and error count.",
        "3. Keep liquidation/orderbook/cross-exchange historical use blocked until A7AA-1 contracts close.",
        "4. Do not promote telemetry to alpha evidence without a separately locked forward proof window.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    a7aa0 = read_json(A7AA0_AUTH)
    a7ab0 = read_json(A7AB0_AUTH)
    inventory = build_inventory()
    schema = build_schema_contract()
    policy = build_append_only_policy()
    schedule = build_schedule()
    boundary = build_evidence_boundary()
    auth = build_authorization(inventory)
    manifest = {
        "decision": auth["decision"],
        "generated_at": auth["generated_at"],
        "a7aa0_decision": a7aa0.get("decision"),
        "a7ab0_decision": a7ab0.get("decision"),
        "source_count": int(len(inventory)),
        "schema_rows": int(len(schema)),
        "executes_download": False,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_alpha_proof": False,
    }
    inventory.to_csv(OUT_DIR / "a7t0_forward_source_inventory.csv", index=False)
    schema.to_csv(OUT_DIR / "a7t0_telemetry_schema_contract.csv", index=False)
    policy.to_csv(OUT_DIR / "a7t0_append_only_policy.csv", index=False)
    schedule.to_csv(OUT_DIR / "a7t0_collector_schedule.csv", index=False)
    boundary.to_csv(OUT_DIR / "a7t0_evidence_boundary.csv", index=False)
    write_json(OUT_DIR / "a7t0_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7t0_manifest.json", manifest)
    write_report(inventory, schema, policy, schedule, boundary, auth)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
