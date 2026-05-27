from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "runtime" / "a7x_reset_contract"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7X_AGGTRADES_RESET_CONTRACT_20260522.md"

AUTH_FILES = {
    "A7U-0R": ROOT / "runtime" / "a7u0r_source_trace_audit" / "a7u0r_authorization_matrix.json",
    "A7W-0": ROOT / "runtime" / "a7w0_post_source_trace_status" / "a7w0_authorization_matrix.json",
    "A7V-5": ROOT / "runtime" / "a7v5_small_replay_smoke" / "a7v5_authorization_matrix.json",
    "A7V-6": ROOT / "runtime" / "a7v6_candidate_control_dominance_forensic" / "a7v6_authorization_matrix.json",
    "A7V-7": ROOT / "runtime" / "a7v7_failure_attribution" / "a7v7_authorization_matrix.json",
}


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
    return json.loads(path.read_text(encoding="utf-8"))


def stage_freeze_matrix() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for stage, path in AUTH_FILES.items():
        payload = load_json(path)
        rows.append(
            {
                "stage": stage,
                "decision": payload.get("decision", ""),
                "blockers": ";".join(payload.get("blockers", [])),
                "data_line_status": "PASS" if stage == "A7U-0R" and str(payload.get("decision", "")).startswith("PASS") else "",
                "signal_line_status": "HOLD" if stage in {"A7V-6", "A7V-7"} and str(payload.get("decision", "")).startswith("HOLD") else "",
                "authorizes_expanded_replay": payload.get("authorizes_expanded_replay", False),
                "authorizes_full_search": payload.get("authorizes_full_search", False),
                "authorizes_alpha_proof": payload.get("authorizes_alpha_proof", False),
                "authorizes_shadow_paper_live": payload.get("authorizes_shadow_paper_live", False),
            }
        )
    return pd.DataFrame(rows)


def weak_prior_registry() -> pd.DataFrame:
    rows = [
        {
            "registry_id": "weak_prior_activity_liquidity_self_reproduction_v1",
            "status": "WEAK_PRIOR_DO_NOT_EXPAND",
            "family": "activity_liquidity_self_reproduction",
            "blocked_pattern": "Decay(agg_notional_bucket,4)",
            "source_stage": "A7V-6/A7V-7",
            "failure_reason": "pre-May can look good; matched controls can be positive; all pre-May dominance clues fail May stress; family concentration high",
            "allowed_future_use": "regime_state_or_interaction_feature_only",
            "disallowed_use": "standalone alpha family expansion or A7V-5 positive replay expansion",
        },
        {
            "registry_id": "weak_prior_activity_liquidity_trade_count_bucket_v1",
            "status": "WEAK_PRIOR_DO_NOT_EXPAND",
            "family": "activity_liquidity_self_reproduction",
            "blocked_pattern": "Decay(agg_trade_count_bucket,4)",
            "source_stage": "A7V-6/A7V-7",
            "failure_reason": "same activity-liquidity motif as failed A7V pre-May clues",
            "allowed_future_use": "interaction with non-May regime/horizon constraints",
            "disallowed_use": "standalone rolling self-reproduction clue",
        },
        {
            "registry_id": "weak_prior_cross_symbol_activity_bucket_v1",
            "status": "WEAK_PRIOR_CAPPED",
            "family": "cross_symbol_activity_liquidity_rank",
            "blocked_pattern": "CrossSymbolRank(agg_notional_bucket)",
            "source_stage": "A7V-6/A7V-7",
            "failure_reason": "one pre-May clue survives controls but fails May; related cross-symbol positives show cost/control issues",
            "allowed_future_use": "symbol-tier neutralized diagnostic with matched controls",
            "disallowed_use": "unconstrained core3 rank alpha",
        },
    ]
    return pd.DataFrame(rows)


def direction_contract() -> pd.DataFrame:
    rows = [
        {
            "direction_id": "X2A_horizon_reset_for_aggtrades",
            "objective": "test whether slower horizons reduce cost/lag and May-stress fragility",
            "horizons": "4h;8h;12h;24h;48h",
            "execution_lags": "1bar;2bar;3bar",
            "allowed_features": "slow_decay;persistence;compression_expansion;relative_to_own_history",
            "blocked_features": "standalone short-horizon activity/liquidity self-reproduction expansion",
            "required_controls": "row_shuffle;time_shuffle;wrong_lag;sign_flip;matched_family_controls",
            "success_is": "diagnostic improvement only, not alpha proof",
        },
        {
            "direction_id": "X2B_aggtrades_state_interaction",
            "objective": "use aggTrades as state/interactor rather than standalone signal",
            "horizons": "12h;24h;48h",
            "execution_lags": "1bar;2bar",
            "allowed_features": "aggTrades_x_basis;aggTrades_x_vol_compression;aggTrades_x_cross_symbol_dispersion;aggTrades_x_funding_neutral;aggTrades_x_trend_reversal",
            "blocked_features": "Rank(agg_notional);Decay(agg_trade_count_bucket);CrossSymbolRank(agg_bucket) as standalone alpha",
            "required_controls": "standalone agg ablation;market-only ablation;matched negative controls;FundingCore/Core4 residual check",
            "success_is": "A7X_RESEARCH_CLUE only",
        },
        {
            "direction_id": "X2C_symbol_tier_attribution",
            "objective": "test whether A7V failure is symbol-tier exposure mismatch rather than universal agg alpha",
            "horizons": "12h;24h;48h",
            "execution_lags": "1bar;2bar",
            "allowed_features": "major_vs_alt_state;symbol_tier_neutralization;BTC_ETH_SOL tier diagnostics",
            "blocked_features": "May-tuned BTC long / SOL short parameter selection",
            "required_controls": "non-May split validation;symbol leave-one-out;matched controls;forward-locked review before promotion",
            "success_is": "failure hypothesis or A7X_RESEARCH_CLUE only",
        },
    ]
    return pd.DataFrame(rows)


def experiment_spec() -> pd.DataFrame:
    rows = [
        {"parameter": "experiment_id", "value": "20260522_crypto_a7x_aggtrades_reset_001"},
        {"parameter": "objective", "value": "small controlled diagnostic for aggTrades objective/horizon/family reset"},
        {"parameter": "generated_cap", "value": "5000"},
        {"parameter": "strict_replay_cap", "value": "256"},
        {"parameter": "deep_audit_cap", "value": "64"},
        {"parameter": "families", "value": "F0_slow_aggtrades_horizon;F1_aggtrades_basis_interaction;F2_aggtrades_vol_compression_interaction;F3_aggtrades_cross_symbol_dispersion;F4_symbol_tier_neutralized_aggtrades;F5_controls"},
        {"parameter": "primary_cost", "value": "10bps"},
        {"parameter": "severe_cost", "value": "20bps"},
        {"parameter": "lag_stress", "value": "1bar;2bar;3bar"},
        {"parameter": "may_policy", "value": "post-selection stress only; not ranking/tuning/generation/allocation"},
        {"parameter": "negative_controls", "value": "row_shuffle;time_shuffle;wrong_lag;sign_flip;matched_family_controls"},
        {"parameter": "pass_label_max", "value": "A7X_RESEARCH_CLUE"},
        {"parameter": "forbidden_labels", "value": "ALPHA_PROOF;SHADOW_READY;PAPER_READY;LIVE_READY"},
        {"parameter": "reproducibility", "value": "must record selected formulas, seeds, input manifests, output hashes"},
    ]
    return pd.DataFrame(rows)


def write_report(now: str, freeze: pd.DataFrame, weak: pd.DataFrame, directions: pd.DataFrame, spec: pd.DataFrame, authorization: dict[str, Any]) -> None:
    lines = [
        "# Crypto A7X AggTrades Reset Contract",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Summary",
        "",
        "A7X freezes the current result as `data-line: PASS` and `signal-line: HOLD`. It does not revive A7V positives. It authorizes only a new objective/horizon/family reset contract for aggTrades.",
        "",
        "A7U-0R closes raw-level source trace. A7V-6/A7V-7 still reject the current activity/liquidity clue family for promotion or expanded replay.",
        "",
        "## Stage Freeze Matrix",
        "",
        table(freeze, max_rows=20),
        "",
        "## Weak-Prior Registry",
        "",
        table(weak, max_rows=20),
        "",
        "## New Direction Contract",
        "",
        table(directions, max_rows=20),
        "",
        "## Small Experiment Spec",
        "",
        table(spec, max_rows=40),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- Implement A7X-3 only as a small controlled diagnostic under this cap.",
        "- Do not replay old A7V-5 positives as candidates.",
        "- Do not use May for ranking, threshold selection, weight selection, generation, mutation, or allocation.",
        "- Keep source trace PASS separate from signal evidence.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    freeze = stage_freeze_matrix()
    weak = weak_prior_registry()
    directions = direction_contract()
    spec = experiment_spec()
    a7u_pass = freeze[freeze["stage"].eq("A7U-0R")]["decision"].astype(str).str.startswith("PASS").all()
    a7v_signal_hold = freeze[freeze["stage"].isin(["A7V-6", "A7V-7"])]["decision"].astype(str).str.startswith("HOLD").all()
    blockers: list[str] = []
    if not a7u_pass:
        blockers.append("data_line_not_pass")
    if not a7v_signal_hold:
        blockers.append("signal_line_not_frozen")
    decision = "PASS_A7X_RESET_CONTRACT_READY" if not blockers else "HOLD_A7X_RESET_CONTRACT_INCOMPLETE"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "data_line_status": "PASS" if a7u_pass else "HOLD",
        "signal_line_status": "HOLD" if a7v_signal_hold else "UNRESOLVED",
        "executes_search": False,
        "executes_replay": False,
        "source_trace_incomplete_caveat_removed": bool(a7u_pass),
        "current_a7v_activity_liquidity_family_promotable": False,
        "authorizes_a7x3_small_controlled_diagnostic": decision.startswith("PASS"),
        "a7x3_generated_cap": 5000,
        "a7x3_strict_replay_cap": 256,
        "a7x3_deep_audit_cap": 64,
        "authorizes_replay_old_a7v5_positives": False,
        "authorizes_expanded_replay": False,
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": [
            "A7X-3 small controlled diagnostic under fixed cap",
            "Use aggTrades as horizon/state/interaction feature, not standalone A7V activity-liquidity expansion",
            "Preserve May stress-only policy",
        ],
    }
    freeze.to_csv(OUT_DIR / "a7x_stage_freeze_matrix.csv", index=False)
    weak.to_csv(OUT_DIR / "a7x_weak_prior_registry.csv", index=False)
    directions.to_csv(OUT_DIR / "a7x_direction_contract.csv", index=False)
    spec.to_csv(OUT_DIR / "a7x_small_experiment_spec.csv", index=False)
    write_json(OUT_DIR / "a7x_authorization_matrix.json", authorization)
    write_json(OUT_DIR / "a7x_manifest.json", {"generated_at": now, "decision": decision, "output_dir": str(OUT_DIR), "report": str(REPORT_PATH)})
    write_report(now, freeze, weak, directions, spec, authorization)
    print(json.dumps({"decision": decision, "blockers": blockers, "data_line": authorization["data_line_status"], "signal_line": authorization["signal_line_status"]}, indent=2))


if __name__ == "__main__":
    main()
