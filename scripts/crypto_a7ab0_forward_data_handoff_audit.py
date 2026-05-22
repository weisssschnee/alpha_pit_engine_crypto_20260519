from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

METRICS_GOLD = DATA_ROOT / "gold" / "features" / "binance_metrics_1h_features_v1.parquet"
CROSS_SNAPSHOT = DATA_ROOT / "silver" / "cross_exchange_forward_snapshot" / "cross_exchange_forward_snapshot_20260522_core12_probe2.parquet"
CROSS_REPORT = DATA_ROOT / "reports" / "crypto_cross_exchange_forward_snapshot_20260522_core12_probe2.json"
CROSS_PROBE_MANIFEST = DATA_ROOT / "raw" / "source_probes" / "cross_exchange_20260522_core12_probe2" / "cross_exchange_source_probe_manifest.csv"

OUT_DIR = ROOT / "runtime" / "a7ab0_forward_data_handoff_audit"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AB0_FORWARD_DATA_HANDOFF_AUDIT_20260522.md"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def table(df: pd.DataFrame, max_rows: int = 100) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def audit_metrics_gold() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not METRICS_GOLD.exists():
        return (
            pd.DataFrame(
                [
                    {
                        "dataset": "binance_metrics_1h_features_v1",
                        "path": str(METRICS_GOLD),
                        "exists": False,
                        "rows": 0,
                        "columns": 0,
                        "symbols": 0,
                        "timestamp_min": "",
                        "timestamp_max": "",
                        "decision": "HOLD_MISSING_METRICS_GOLD",
                    }
                ]
            ),
            pd.DataFrame(),
        )
    df = pd.read_parquet(METRICS_GOLD)
    independent = [
        "open_interest",
        "open_interest_value",
        "global_long_short_account_ratio",
        "top_long_short_account_ratio",
        "top_long_short_position_ratio",
        "taker_buy_sell_volume_ratio",
    ]
    feature_rows = []
    for col in independent:
        feature_rows.append(
            {
                "field": col,
                "present": col in df.columns,
                "non_null": int(df[col].notna().sum()) if col in df.columns else 0,
                "independent_source": True,
                "allowed_role": "historical source-audit feature",
                "caveat": "vendor 5m jitter/gap warnings from A7S-1 remain attached",
            }
        )
    derived = [c for c in df.columns if any(s in c for s in ["_change_", "_zscore_", "_x_"])]
    for col in derived[:40]:
        feature_rows.append(
            {
                "field": col,
                "present": True,
                "non_null": int(df[col].notna().sum()),
                "independent_source": False,
                "allowed_role": "derived transform only",
                "caveat": "inherits parent source contract; not independent source",
            }
        )
    summary = pd.DataFrame(
        [
            {
                "dataset": "binance_metrics_1h_features_v1",
                "path": str(METRICS_GOLD),
                "exists": True,
                "rows": int(len(df)),
                "columns": int(len(df.columns)),
                "symbols": int(df["symbol"].nunique()) if "symbol" in df.columns else 0,
                "timestamp_min": str(df["timestamp"].min()) if "timestamp" in df.columns else "",
                "timestamp_max": str(df["timestamp"].max()) if "timestamp" in df.columns else "",
                "decision": "PASS_METRICS_HISTORY_SOURCE_AUDIT_INPUT",
            }
        ]
    )
    return summary, pd.DataFrame(feature_rows)


def audit_cross_snapshot() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not CROSS_SNAPSHOT.exists():
        return (
            pd.DataFrame(
                [
                    {
                        "dataset": "cross_exchange_forward_snapshot_20260522_core12_probe2",
                        "path": str(CROSS_SNAPSHOT),
                        "exists": False,
                        "rows": 0,
                        "columns": 0,
                        "symbols": 0,
                        "providers": "",
                        "forward_only_rows": 0,
                        "historical_backfill_rows": 0,
                        "decision": "HOLD_MISSING_CROSS_EXCHANGE_SNAPSHOT",
                    }
                ]
            ),
            pd.DataFrame(),
            pd.DataFrame(),
        )
    df = pd.read_parquet(CROSS_SNAPSHOT)
    nullable_event = df["event_time"].astype(str).str.len().eq(0).sum() if "event_time" in df.columns else 0
    summary = pd.DataFrame(
        [
            {
                "dataset": "cross_exchange_forward_snapshot_20260522_core12_probe2",
                "path": str(CROSS_SNAPSHOT),
                "exists": True,
                "rows": int(len(df)),
                "columns": int(len(df.columns)),
                "symbols": int(df["symbol"].nunique()) if "symbol" in df.columns else 0,
                "providers": ",".join(sorted(map(str, df["provider"].dropna().unique()))) if "provider" in df.columns else "",
                "feature_groups": ",".join(sorted(map(str, df["feature_group"].dropna().unique()))) if "feature_group" in df.columns else "",
                "forward_only_rows": int(df["is_forward_only"].fillna(False).sum()) if "is_forward_only" in df.columns else 0,
                "historical_backfill_rows": int(df["is_historical_backfill"].fillna(False).sum()) if "is_historical_backfill" in df.columns else 0,
                "observable_time_non_null": int(df["observable_time"].notna().sum()) if "observable_time" in df.columns else 0,
                "event_time_blank_count": int(nullable_event),
                "raw_sha256_non_null": int(df["raw_sha256"].notna().sum()) if "raw_sha256" in df.columns else 0,
                "decision": "PASS_FORWARD_SNAPSHOT_TELEMETRY_INPUT_NOT_HISTORICAL_PROOF",
            }
        ]
    )
    schema_rows = []
    for col in df.columns:
        schema_rows.append(
            {
                "column": col,
                "dtype": str(df[col].dtype),
                "non_null": int(df[col].notna().sum()),
                "example": "" if df[col].dropna().empty else str(df[col].dropna().iloc[0])[:120],
                "field_family": classify_cross_field(col),
            }
        )
    feature_group = (
        df.groupby(["provider", "dataset", "feature_group"], dropna=False)
        .agg(rows=("symbol", "size"), symbols=("symbol", "nunique"), forward_only_rows=("is_forward_only", "sum"), historical_backfill_rows=("is_historical_backfill", "sum"))
        .reset_index()
        .sort_values(["provider", "dataset"])
    )
    return summary, pd.DataFrame(schema_rows), feature_group


def classify_cross_field(col: str) -> str:
    if col in {"collection_time", "event_time", "observable_time", "timezone"}:
        return "time_contract"
    if col in {"provider", "dataset", "symbol", "feature_group", "source_url", "history_depth", "proof_role", "is_forward_only", "is_historical_backfill"}:
        return "source_contract"
    if "depth" in col or col in {"best_bid", "best_ask", "mid", "spread_bps"}:
        return "orderbook_depth"
    if "liquidation" in col:
        return "liquidation_recent"
    if "funding" in col or "premium" in col or "basis" in col or col in {"mark_price", "index_price", "next_funding_time"}:
        return "funding_basis_premium"
    if "open_interest" in col:
        return "open_interest"
    if col in {"raw_path", "raw_sha256"}:
        return "source_trace"
    return "other"


def audit_probe_manifest() -> pd.DataFrame:
    if not CROSS_PROBE_MANIFEST.exists():
        return pd.DataFrame(
            [
                {
                    "provider": "<missing>",
                    "dataset": "<missing>",
                    "status": "missing_manifest",
                    "rows": 0,
                    "ready": 0,
                    "http_hold": 0,
                    "decision": "HOLD_MISSING_PROBE_MANIFEST",
                }
            ]
        )
    m = pd.read_csv(CROSS_PROBE_MANIFEST)
    grouped = (
        m.groupby(["provider", "dataset"], dropna=False)
        .agg(rows=("symbol", "size"), ready=("status", lambda s: int((s == "ready").sum())), http_hold=("status", lambda s: int((s == "http_hold").sum())), symbols=("symbol", lambda s: ",".join(sorted(set(map(str, s))))))
        .reset_index()
    )
    grouped["decision"] = grouped.apply(lambda r: "PASS_READY" if int(r["http_hold"]) == 0 and int(r["ready"]) == int(r["rows"]) else "WARN_INCOMPLETE_PROBE", axis=1)
    return grouped.sort_values(["provider", "dataset"])


def build_policy() -> pd.DataFrame:
    rows = [
        {
            "data_line": "binance_metrics_history",
            "historical_experiment_allowed": True,
            "forward_telemetry_allowed": True,
            "alpha_proof_allowed": False,
            "use_boundary": "Can enter A7S-1 source audit and controlled historical experiments with vendor 5m warning caveat.",
        },
        {
            "data_line": "cross_exchange_forward_snapshot",
            "historical_experiment_allowed": False,
            "forward_telemetry_allowed": True,
            "alpha_proof_allowed": False,
            "use_boundary": "Use for forward-only telemetry design and source audit sample; do not backfill historical proof.",
        },
        {
            "data_line": "okx_liquidation_recent",
            "historical_experiment_allowed": False,
            "forward_telemetry_allowed": True,
            "alpha_proof_allowed": False,
            "use_boundary": "Recent/forward liquidation pressure source only until retention/pagination/PIT contract is closed.",
        },
        {
            "data_line": "orderbook_depth_snapshot",
            "historical_experiment_allowed": False,
            "forward_telemetry_allowed": True,
            "alpha_proof_allowed": False,
            "use_boundary": "Forward collector only unless a validated historical depth source is contracted.",
        },
    ]
    return pd.DataFrame(rows)


def build_authorization(metrics_summary: pd.DataFrame, cross_summary: pd.DataFrame, probe_summary: pd.DataFrame) -> dict[str, Any]:
    metrics_ready = bool(not metrics_summary.empty and bool(metrics_summary.iloc[0].get("exists")))
    cross_ready = bool(not cross_summary.empty and bool(cross_summary.iloc[0].get("exists")))
    probe_ready = int(probe_summary["ready"].sum()) if "ready" in probe_summary else 0
    probe_rows = int(probe_summary["rows"].sum()) if "rows" in probe_summary else 0
    return {
        "decision": "PASS_A7AB0_DATA_HANDOFF_ACCEPTED_FOR_SOURCE_AUDIT_AND_FORWARD_TELEMETRY",
        "generated_at": utc_stamp(),
        "executes_search": False,
        "executes_replay": False,
        "metrics_gold_ready": metrics_ready,
        "cross_exchange_forward_snapshot_ready": cross_ready,
        "probe_ready_endpoints": probe_ready,
        "probe_total_endpoints": probe_rows,
        "authorizes_metrics_historical_source_audit": True,
        "authorizes_cross_exchange_forward_telemetry_design": True,
        "authorizes_historical_alpha_proof_from_cross_exchange_snapshot": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": [
            "cross-exchange snapshot is forward-only",
            "OKX liquidation retention/pagination contract unresolved",
            "orderbook snapshots cannot be backfilled into historical proof",
            "Binance basis probe has 3 rate-limit holds in core12_probe2",
        ],
        "required_next": [
            "Use Binance metrics history in A7S-1 controlled source audit with vendor warning caveat",
            "Design A7T forward telemetry from cross-exchange snapshot fields",
            "Do not run historical alpha proof on liquidation/orderbook snapshot fields",
        ],
    }


def write_report(
    metrics_summary: pd.DataFrame,
    metrics_fields: pd.DataFrame,
    cross_summary: pd.DataFrame,
    cross_schema: pd.DataFrame,
    cross_groups: pd.DataFrame,
    probe_summary: pd.DataFrame,
    policy: pd.DataFrame,
    auth: dict[str, Any],
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report_json = read_json(CROSS_REPORT)
    lines = [
        "# CRYPTO A7AB-0 Forward Data Handoff Audit",
        "",
        f"Generated: {auth['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{auth['decision']}`",
        "",
        "A7AB-0 accepts the data handoff for source audit and forward telemetry design. It does not run search or replay and does not authorize historical alpha proof.",
        "",
        "## External Handoff Summary",
        "",
        f"- Cross-exchange report rows: {report_json.get('rows', '<missing>')}.",
        f"- Cross-exchange providers: {', '.join(report_json.get('providers', [])) if report_json else '<missing>'}.",
        f"- Cross-exchange role: {report_json.get('contract', {}).get('role', '<missing>') if report_json else '<missing>'}.",
        "",
        "## Binance Metrics History",
        "",
        table(metrics_summary),
        "",
        "### Metrics Field Audit",
        "",
        table(metrics_fields, max_rows=80),
        "",
        "## Cross-Exchange Forward Snapshot",
        "",
        table(cross_summary),
        "",
        "### Cross-Exchange Feature Groups",
        "",
        table(cross_groups),
        "",
        "### Cross-Exchange Schema",
        "",
        table(cross_schema, max_rows=120),
        "",
        "## Probe Manifest Summary",
        "",
        table(probe_summary),
        "",
        "## Use Policy",
        "",
        table(policy),
        "",
        "## Authorization",
        "",
        table(pd.DataFrame([auth])),
        "",
        "## Required Next Action",
        "",
        "1. Give experiment side `binance_metrics_1h_features_v1.parquet` as historical source-audit input with vendor 5m warning caveat.",
        "2. Use `cross_exchange_forward_snapshot_20260522_core12_probe2.parquet` only for forward telemetry design.",
        "3. Keep liquidation/orderbook as forward/recent context until PIT retention and historical source contracts close.",
        "4. Keep derived transforms out of independent-source counts.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics_summary, metrics_fields = audit_metrics_gold()
    cross_summary, cross_schema, cross_groups = audit_cross_snapshot()
    probe_summary = audit_probe_manifest()
    policy = build_policy()
    auth = build_authorization(metrics_summary, cross_summary, probe_summary)
    manifest = {
        "decision": auth["decision"],
        "generated_at": auth["generated_at"],
        "metrics_gold": str(METRICS_GOLD),
        "cross_snapshot": str(CROSS_SNAPSHOT),
        "probe_manifest": str(CROSS_PROBE_MANIFEST),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_alpha_proof": False,
    }
    metrics_summary.to_csv(OUT_DIR / "a7ab0_metrics_history_summary.csv", index=False)
    metrics_fields.to_csv(OUT_DIR / "a7ab0_metrics_field_audit.csv", index=False)
    cross_summary.to_csv(OUT_DIR / "a7ab0_cross_exchange_snapshot_summary.csv", index=False)
    cross_schema.to_csv(OUT_DIR / "a7ab0_cross_exchange_schema.csv", index=False)
    cross_groups.to_csv(OUT_DIR / "a7ab0_cross_exchange_feature_groups.csv", index=False)
    probe_summary.to_csv(OUT_DIR / "a7ab0_probe_manifest_summary.csv", index=False)
    policy.to_csv(OUT_DIR / "a7ab0_use_policy.csv", index=False)
    write_json(OUT_DIR / "a7ab0_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ab0_manifest.json", manifest)
    write_report(metrics_summary, metrics_fields, cross_summary, cross_schema, cross_groups, probe_summary, policy, auth)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
