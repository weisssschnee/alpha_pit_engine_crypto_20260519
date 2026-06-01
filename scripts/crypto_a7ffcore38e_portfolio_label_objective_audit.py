from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore38e_portfolio_label_objective_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE38E_PORTFOLIO_LABEL_OBJECTIVE_AUDIT_20260602.md"
CORE38 = REPO / "runtime" / "a7ffcore38_portfolio_label_objective_contract" / "a7ffcore38_manifest.json"
OBJECTIVE_CONTRACT = REPO / "runtime" / "a7ffcore38_portfolio_label_objective_contract" / "a7ffcore38_objective_book_contract.csv"
LABEL_CONTRACT = REPO / "runtime" / "a7ffcore38_portfolio_label_objective_contract" / "a7ffcore38_label_contract.csv"
CORE33E_RESULTS = REPO / "runtime" / "a7ffcore33e_bounded_replay_execution" / "a7ffcore33e_replay_results.csv"
CORE36E_CANDIDATES = REPO / "runtime" / "a7ffcore36e_replay_objective_reset_execution" / "a7ffcore36e_candidate_rescore.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE38)
    if source.get("decision") != "PASS_A7FFCORE38_PORTFOLIO_LABEL_OBJECTIVE_CONTRACT_READY_FOR_CORE38E":
        raise SystemExit(f"CORE38 not ready for CORE38E: {source.get('decision')}")

    objective_contract = pd.read_csv(OBJECTIVE_CONTRACT)
    label_contract = pd.read_csv(LABEL_CONTRACT)
    replay_cols = pd.read_csv(CORE33E_RESULTS, nrows=5).columns.tolist()
    rescore_cols = pd.read_csv(CORE36E_CANDIDATES, nrows=5).columns.tolist()

    required = pd.DataFrame(
        [
            {
                "objective_id": "B0_legacy_net_spread",
                "required_columns": "replay_candidate_id, split, label_family, horizon_h, net_spread, control_ratio",
                "available_status": "AVAILABLE",
                "missing_columns": "",
                "audit_result": "available_but_already_failed",
            },
            {
                "objective_id": "B1_cross_sectional_rank_book",
                "required_columns": "timestamp, symbol, candidate_score, forward_return, rank_weight",
                "available_status": "MISSING_SYMBOL_LEVEL_INPUT",
                "missing_columns": "timestamp, symbol, candidate_score, forward_return, rank_weight",
                "audit_result": "cannot_compute_from_aggregate_replay_rows",
            },
            {
                "objective_id": "B2_market_beta_residual_book",
                "required_columns": "timestamp, symbol, forward_return, btc_eth_market_return, beta_residual_return",
                "available_status": "MISSING_SYMBOL_LEVEL_INPUT",
                "missing_columns": "timestamp, symbol, forward_return, btc_eth_market_return, beta_residual_return",
                "audit_result": "cannot_compute_from_aggregate_replay_rows",
            },
            {
                "objective_id": "B3_vol_adjusted_rank_book",
                "required_columns": "timestamp, symbol, candidate_score, forward_return, realized_vol, vol_adjusted_return",
                "available_status": "MISSING_SYMBOL_LEVEL_INPUT",
                "missing_columns": "timestamp, symbol, candidate_score, forward_return, realized_vol, vol_adjusted_return",
                "audit_result": "cannot_compute_from_aggregate_replay_rows",
            },
            {
                "objective_id": "B4_liquidity_cost_capped_book",
                "required_columns": "timestamp, symbol, candidate_score, quote_volume, turnover, cost_bucket, position_weight",
                "available_status": "PARTIAL_AGGREGATE_ONLY",
                "missing_columns": "timestamp, symbol, candidate_score, quote_volume, cost_bucket, position_weight",
                "audit_result": "aggregate turnover exists but cannot enforce symbol-level caps",
            },
            {
                "objective_id": "B5_family_role_book",
                "required_columns": "family_id, split, net_spread, control_ratio, train_oos_diagnosis",
                "available_status": "PARTIAL_DIAGNOSTIC_ONLY",
                "missing_columns": "symbol-level hedge/regime book attribution",
                "audit_result": "can diagnose family role but cannot compute executable family book",
            },
        ]
    )
    available_columns = pd.DataFrame(
        [
            {"artifact": "CORE33E aggregate replay", "column": col}
            for col in replay_cols
        ]
        + [
            {"artifact": "CORE36E candidate rescore", "column": col}
            for col in rescore_cols
        ]
    )
    label_audit = label_contract.copy()
    label_audit["symbol_level_required"] = label_audit["label_id"].isin(
        ["L1_cross_sectional_relative_return", "L2_market_beta_residual_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"]
    )
    label_audit["computable_from_current_artifacts"] = False
    label_audit.loc[label_audit["label_id"].eq("L0_raw_forward_return"), "computable_from_current_artifacts"] = True
    label_audit.loc[label_audit["label_id"].eq("L7_ranked_future_return"), "computable_from_current_artifacts"] = False
    label_audit["audit_note"] = "requires symbol-level score/return panel, not aggregate replay summary"
    label_audit.loc[label_audit["label_id"].eq("L0_raw_forward_return"), "audit_note"] = "aggregate proxy exists but cannot be sole proof label"

    blocker_matrix = pd.DataFrame(
        [
            {
                "blocker": "aggregate_replay_summary_only",
                "severity": "HIGH",
                "impact": "B1/B2/B3/B4 portfolio objectives cannot be computed",
                "required_fix": "build symbol-level candidate score and label/book input packet",
            },
            {
                "blocker": "missing_position_weight_trace",
                "severity": "HIGH",
                "impact": "cannot enforce max symbol/family/liquidity caps",
                "required_fix": "emit per-timestamp selected long/short weights before spread aggregation",
            },
            {
                "blocker": "missing_beta_residual_label_panel",
                "severity": "MEDIUM",
                "impact": "cannot test B2 market-beta residual objective",
                "required_fix": "construct BTC/ETH/market residual return labels with PIT split metadata",
            },
            {
                "blocker": "legacy_net_spread_reference_only",
                "severity": "HIGH",
                "impact": "the only fully computable objective is already known to fail",
                "required_fix": "do not rerun B0 as primary objective",
            },
        ]
    )
    authorization = pd.DataFrame(
        [
            {
                "task": "A7FF-CORE39 symbol-level book input packet contract",
                "status": "AUTHORIZED_CONTRACT_ONLY",
                "reason": "CORE38E shows book objectives need symbol-level score/return/weight inputs",
            },
            {
                "task": "A7FF-CORE38E book objective execution from current aggregate rows",
                "status": "NOT_AUTHORIZED",
                "reason": "current artifacts are aggregate summaries and cannot compute B1/B2/B3/B4",
            },
            {"task": "formula_search", "status": "NOT_AUTHORIZED", "reason": "book objective input packet missing"},
            {"task": "large_search", "status": "NOT_AUTHORIZED", "reason": "book objective input packet missing"},
            {"task": "alpha_proof / shadow / paper / live", "status": "NOT_AUTHORIZED", "reason": "no proof object"},
        ]
    )
    decision = "HOLD_A7FFCORE38E_BOOK_OBJECTIVE_AUDIT_REQUIRES_SYMBOL_LEVEL_REPLAY_INPUT"
    manifest = {
        "stage": "A7FF-CORE38E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE38",
        "source_decision": source.get("decision"),
        "decision": decision,
        "computable_primary_objectives": 0,
        "reference_objectives_available": 1,
        "dominant_blocker": "symbol_level_book_input_missing",
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core39_contract": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE39 symbol-level book input packet contract",
    }
    objective_contract.to_csv(RUNTIME / "a7ffcore38e_source_objective_contract_snapshot.csv", index=False)
    required.to_csv(RUNTIME / "a7ffcore38e_objective_computability_audit.csv", index=False)
    available_columns.to_csv(RUNTIME / "a7ffcore38e_available_column_inventory.csv", index=False)
    label_audit.to_csv(RUNTIME / "a7ffcore38e_label_computability_audit.csv", index=False)
    blocker_matrix.to_csv(RUNTIME / "a7ffcore38e_blocker_matrix.csv", index=False)
    authorization.to_csv(RUNTIME / "a7ffcore38e_authorization_matrix.csv", index=False)
    write_json(RUNTIME / "a7ffcore38e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE38E PORTFOLIO-LABEL OBJECTIVE AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE38E audits whether the portfolio-label objectives from CORE38 can be computed from existing artifacts. It does not execute replay, generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Main Finding",
        "",
        "Current replay artifacts are aggregate candidate summaries. They are enough to re-score legacy B0 net spread, but not enough for B1/B2/B3/B4 portfolio/book objectives because symbol-level score, return, rank, residual label, and position-weight traces are absent.",
        "",
        "## Objective Computability Audit",
        "",
        md_table(required),
        "",
        "## Label Computability Audit",
        "",
        md_table(label_audit),
        "",
        "## Blocker Matrix",
        "",
        md_table(blocker_matrix),
        "",
        "## Authorization Matrix",
        "",
        md_table(authorization),
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
