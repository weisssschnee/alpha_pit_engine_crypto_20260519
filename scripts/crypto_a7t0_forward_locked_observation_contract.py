from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path("G:/AlphaFactory_CryptoData")
OUT_DIR = ROOT / "runtime" / "a7t0_forward_locked_observation_contract"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7T0_FORWARD_LOCKED_OBSERVATION_CONTRACT_20260522.md"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def forward_field_registry() -> pd.DataFrame:
    rows = [
        {
            "field_group": "orderbook_forward_snapshot",
            "local_path": str(DATA_ROOT / "silver" / "binance_api" / "orderbook_forward_snapshot"),
            "current_status": "FORWARD_ONLY_AVAILABLE",
            "append_only_key": "collector_time;symbol",
            "historical_proof_allowed": False,
            "allowed_use": "forward context; spread/depth telemetry; future locked observation after sufficient history",
            "blocked_use": "2024-2026 historical alpha proof or May retro-fit",
        },
        {
            "field_group": "positioning_forward",
            "local_path": str(DATA_ROOT / "metadata" / "positioning_forward_state.csv"),
            "current_status": "FORWARD_ONLY_AVAILABLE",
            "append_only_key": "event_time;observable_time;symbol;endpoint",
            "historical_proof_allowed": False,
            "allowed_use": "append-only telemetry for OI/long-short/taker-ratio after collection time",
            "blocked_use": "backfilled historical proof before PIT/source contract",
        },
        {
            "field_group": "aggtrades_enhanced_panel",
            "local_path": str(DATA_ROOT / "gold" / "panels" / "crypto_core12_1h_with_aggtrades_features_v1.parquet"),
            "current_status": "HISTORICAL_CORE3_READY_SOURCE_TRACE_PASS",
            "append_only_key": "symbol;timestamp",
            "historical_proof_allowed": True,
            "allowed_use": "controlled diagnostics with availability mask; future observation if panel refresh is append-only",
            "blocked_use": "standalone activity/liquidity family promotion",
        },
    ]
    for row in rows:
        row["path_exists"] = bool(Path(row["local_path"]).exists())
    return pd.DataFrame(rows)


def observation_object_registry() -> pd.DataFrame:
    rows = [
        {
            "object_id": "FundingCore",
            "status": "BENCHMARK_ONLY",
            "forward_observation_allowed": True,
            "proof_use": "excluded_until_new_locked_window",
            "notes": "funding line remains HOLD; observation is telemetry, not promotion",
        },
        {
            "object_id": "Core4",
            "status": "RESEARCH_OBJECT_ONLY",
            "forward_observation_allowed": True,
            "proof_use": "excluded_until_new_locked_window",
            "notes": "A7 baseline failures and drawdown issues remain unresolved",
        },
        {
            "object_id": "A7X3_near_miss_horizon_spread_flow_minus_btc_eth",
            "status": "STRESS_CLUE_NOT_CANDIDATE",
            "forward_observation_allowed": True,
            "proof_use": "monitor_only",
            "notes": "two A7X-3 near-misses were control-clean pre-May but May-negative; not promotable",
        },
        {
            "object_id": "negative_controls",
            "status": "MANDATORY_CONTROL",
            "forward_observation_allowed": True,
            "proof_use": "framework_health_only",
            "notes": "wrong-lag/row-shuffle/time-shuffle/sign-flip must remain non-promotable",
        },
    ]
    return pd.DataFrame(rows)


def append_only_rules() -> pd.DataFrame:
    rows = [
        {
            "rule_id": "freeze_before_window",
            "rule": "candidate list, formulas, scoring, gates, costs, lag rules, and negative controls must be frozen before a forward window starts",
            "violation_action": "window evidence invalid for proof",
        },
        {
            "rule_id": "no_may_or_seen_forward_tuning",
            "rule": "known May stress and observed forward outcomes cannot tune ranking, thresholds, weights, generation, or allocation",
            "violation_action": "downgrade to post-hoc diagnostic",
        },
        {
            "rule_id": "append_only_storage",
            "rule": "forward snapshots and positioning records must append with collector_time/observable_time; no overwrite without restatement log",
            "violation_action": "hold affected window until restatement audit",
        },
        {
            "rule_id": "negative_controls_required",
            "rule": "negative controls must be reported beside every monitored object",
            "violation_action": "hold framework health claim",
        },
        {
            "rule_id": "no_trade_authorization",
            "rule": "A7T telemetry cannot authorize shadow, paper, live, or production book",
            "violation_action": "promotion blocked",
        },
    ]
    return pd.DataFrame(rows)


def output_contract() -> pd.DataFrame:
    rows = [
        {"artifact": "hourly_forward_snapshot", "required_fields": "timestamp;symbol;object_id;signal;position_proxy;source_version;collector_time", "proof_status": "telemetry_only"},
        {"artifact": "hourly_forward_pnl_proxy", "required_fields": "timestamp;object_id;gross_pnl;fee_proxy;funding_proxy;net_pnl;cost_bps;lag_bars", "proof_status": "telemetry_only_until_locked_window_complete"},
        {"artifact": "negative_control_log", "required_fields": "timestamp;control_id;control_mode;net_pnl_proxy;status", "proof_status": "framework_health"},
        {"artifact": "forward_window_manifest", "required_fields": "window_start;window_end;frozen_commit;input_data_hash;gate_version;restatement_count", "proof_status": "required_for_any_future_claim"},
    ]
    return pd.DataFrame(rows)


def write_report(now: str, fields: pd.DataFrame, objects: pd.DataFrame, rules: pd.DataFrame, outputs: pd.DataFrame, authorization: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Crypto A7T-0 Forward-Locked Observation Contract",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7T-0 defines append-only observation rules for forward-only and research-only objects. It does not authorize trading or alpha proof.",
        "",
        "## Forward Field Registry",
        "",
        table(fields, max_rows=20),
        "",
        "## Observation Object Registry",
        "",
        table(objects, max_rows=20),
        "",
        "## Append-Only Rules",
        "",
        table(rules, max_rows=20),
        "",
        "## Output Contract",
        "",
        table(outputs, max_rows=20),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- Implement A7T-1 only after selecting a frozen commit/window.",
        "- Keep all forward-only fields out of historical proof.",
        "- Report negative controls beside every forward object.",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    fields = forward_field_registry()
    objects = observation_object_registry()
    rules = append_only_rules()
    outputs = output_contract()
    blockers = []
    if not bool(fields[fields["field_group"].eq("orderbook_forward_snapshot")]["path_exists"].iloc[0]):
        blockers.append("orderbook_forward_snapshot_path_missing")
    decision = "PASS_A7T0_FORWARD_LOCKED_OBSERVATION_CONTRACT_READY" if not blockers else "HOLD_A7T0_FORWARD_INPUT_MISSING"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7t1_forward_observation_runner_design": not blockers,
        "authorizes_historical_proof_from_forward_only_fields": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_policy": "known_stress_not_training_or_tuning_input",
        "required_next": [
            "A7T-1 forward observation runner design after frozen commit/window selection",
            "A7S-1 field availability/source-trace audit for newly delivered historical fields",
            "No promotion from A7T telemetry alone",
        ],
    }
    fields.to_csv(OUT_DIR / "a7t0_forward_field_registry.csv", index=False)
    objects.to_csv(OUT_DIR / "a7t0_observation_object_registry.csv", index=False)
    rules.to_csv(OUT_DIR / "a7t0_append_only_rules.csv", index=False)
    outputs.to_csv(OUT_DIR / "a7t0_output_contract.csv", index=False)
    write_json(OUT_DIR / "a7t0_authorization_matrix.json", authorization)
    write_json(OUT_DIR / "a7t0_manifest.json", {"generated_at": now, "decision": decision, "output_dir": str(OUT_DIR), "report": str(REPORT_PATH)})
    write_report(now, fields, objects, rules, outputs, authorization)
    print(json.dumps({"decision": decision, "blockers": blockers}, indent=2))


if __name__ == "__main__":
    main()
