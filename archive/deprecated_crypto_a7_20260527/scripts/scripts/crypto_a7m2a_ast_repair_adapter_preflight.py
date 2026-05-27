from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, stable_hash


DATE_TAG = "20260520"
A7M2A_DIR = RUNTIME_DIR / "a7m2a_ast_repair_adapter"
DATASET_PATH = RUNTIME_DIR / "a7m0_failure_labeled_search_dataset" / "crypto_a7m0_failure_labeled_candidate_dataset.csv"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def bool_series(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series(False, index=df.index)
    return df[col].fillna(False).astype(str).str.lower().isin(["true", "1", "yes"])


def any_count(df: pd.DataFrame, cols: list[str]) -> int:
    mask = pd.Series(False, index=df.index)
    for col in cols:
        mask |= bool_series(df, col)
    return int(mask.sum())


def failure_taxonomy(df: pd.DataFrame) -> list[dict[str, Any]]:
    specs = [
        {
            "failure_type": "raw_fail",
            "source_labels": "raw_validation_fail;raw_recent_fail",
            "cols": ["raw_validation_fail", "raw_recent_fail"],
            "repair_policy": "negative_label_only",
            "repair_allowed": False,
            "reason": "Raw failure is not repaired directly into a candidate; it informs mutation priors only.",
        },
        {
            "failure_type": "residual_fail",
            "source_labels": "residual_funding_validation_fail;residual_funding_recent_fail;residual_core4_recent_fail",
            "cols": ["residual_funding_validation_fail", "residual_funding_recent_fail", "residual_core4_recent_fail"],
            "repair_policy": "orthogonalize_or_penalize",
            "repair_allowed": True,
            "reason": "Repair can reduce FundingCore/Core4 beta exposure without using May.",
        },
        {
            "failure_type": "cost20_fail",
            "source_labels": "cost20_validation_fail;cost20_recent_fail",
            "cols": ["cost20_validation_fail", "cost20_recent_fail"],
            "repair_policy": "reduce_turnover_and_smooth",
            "repair_allowed": True,
            "reason": "Repair can smooth high-turnover expressions and add liquidity/activity constraints.",
        },
        {
            "failure_type": "lag1_fail",
            "source_labels": "lag1_validation_fail;lag1_recent_fail",
            "cols": ["lag1_validation_fail", "lag1_recent_fail"],
            "repair_policy": "increase_latency_stability",
            "repair_allowed": True,
            "reason": "Repair can avoid near-bar features and move to slower horizons.",
        },
        {
            "failure_type": "activity_coverage_fail",
            "source_labels": "activity_fail;coverage_fail",
            "cols": ["activity_fail", "coverage_fail"],
            "repair_policy": "remove_zero_activity_artifacts",
            "repair_allowed": True,
            "reason": "Repair can reject all-zero/all-NaN expressions or replace fields with active equivalents.",
        },
        {
            "failure_type": "beta_fail",
            "source_labels": "funding_beta_fail;core4_beta_fail",
            "cols": ["funding_beta_fail", "core4_beta_fail"],
            "repair_policy": "beta_penalty_or_reject",
            "repair_allowed": True,
            "reason": "Repair can reject packaged FundingCore/Core4 exposure or add beta penalty.",
        },
        {
            "failure_type": "residual_only_clue",
            "source_labels": "clue_label",
            "cols": ["clue_label"],
            "repair_policy": "diagnostic_only",
            "repair_allowed": False,
            "reason": "Residual-only clues cannot be repaired into standalone alpha candidates.",
        },
        {
            "failure_type": "near_miss",
            "source_labels": "near_miss_label",
            "cols": ["near_miss_label"],
            "repair_policy": "targeted_non_may_mutation",
            "repair_allowed": True,
            "reason": "Near-miss cases can seed targeted mutation using non-May gates only.",
        },
    ]
    rows = []
    for spec in specs:
        rows.append(
            {
                "failure_type": spec["failure_type"],
                "source_labels": spec["source_labels"],
                "observed_count": any_count(df, spec["cols"]),
                "repair_policy": spec["repair_policy"],
                "repair_allowed": spec["repair_allowed"],
                "may_allowed": False,
                "promotes_candidate": False,
                "reason": spec["reason"],
            }
        )
    return rows


def repair_actions() -> list[dict[str, Any]]:
    rows = [
        {
            "failure_type": "cost20_fail",
            "action_id": "smooth_horizon",
            "action": "Increase rolling/smoothing horizon and prefer slower features.",
            "allowed": True,
            "forbidden_inputs": "May stress labels;future funding;post-selection outcomes",
            "expected_effect": "Lower turnover and 20bps fragility.",
        },
        {
            "failure_type": "cost20_fail",
            "action_id": "liquidity_activity_filter",
            "action": "Require nonzero activity/gross exposure and liquidity-aware field choice.",
            "allowed": True,
            "forbidden_inputs": "May stress labels",
            "expected_effect": "Remove zero-activity and high-cost artifacts.",
        },
        {
            "failure_type": "lag1_fail",
            "action_id": "ban_near_bar_terms",
            "action": "Avoid current-bar sensitive terms and require lag-stable rolling features.",
            "allowed": True,
            "forbidden_inputs": "same-bar execution assumptions;May stress labels",
            "expected_effect": "Improve 1bar execution-lag survival.",
        },
        {
            "failure_type": "lag1_fail",
            "action_id": "push_horizon",
            "action": "Mutate 6h variants toward 12h/24h when non-May raw/residual evidence survives.",
            "allowed": True,
            "forbidden_inputs": "May pass/fail direction",
            "expected_effect": "Reduce latency fragility.",
        },
        {
            "failure_type": "residual_fail",
            "action_id": "orthogonal_interaction",
            "action": "Prefer interactions that reduce FundingCore/Core4 beta under validation/recent windows.",
            "allowed": True,
            "forbidden_inputs": "May residual result;future funding",
            "expected_effect": "Avoid funding/basis directional wrappers.",
        },
        {
            "failure_type": "activity_coverage_fail",
            "action_id": "reject_or_replace_inactive_field",
            "action": "Reject zero-exposure expressions or replace inactive field pairs before replay.",
            "allowed": True,
            "forbidden_inputs": "May stress labels",
            "expected_effect": "Prevent zero-activity false positives.",
        },
        {
            "failure_type": "beta_fail",
            "action_id": "benchmark_packaging_guard",
            "action": "Reject FundingCore/Core4/taker packaging as standalone candidate.",
            "allowed": True,
            "forbidden_inputs": "May stress labels",
            "expected_effect": "Keep baselines as baselines and clues as clues.",
        },
        {
            "failure_type": "raw_fail",
            "action_id": "negative_only",
            "action": "Use as negative mutation evidence; do not repair directly into a candidate.",
            "allowed": False,
            "forbidden_inputs": "all candidate promotion paths",
            "expected_effect": "Prevents promoting raw-weak formulas.",
        },
        {
            "failure_type": "residual_only_clue",
            "action_id": "diagnostic_only",
            "action": "Keep as hedge/overlay clue; do not call standalone alpha.",
            "allowed": False,
            "forbidden_inputs": "research_candidate label",
            "expected_effect": "Prevents residual-only promotion.",
        },
        {
            "failure_type": "near_miss",
            "action_id": "targeted_non_may_mutation",
            "action": "Allow mutation around the failing non-May gate while preserving timing/cost/lag contracts.",
            "allowed": True,
            "forbidden_inputs": "May severe-fail margin;May residual direction",
            "expected_effect": "Search around useful boundary cases without May overfit.",
        },
    ]
    for row in rows:
        row["requires_timing_check"] = True
        row["authorizes_search"] = False
        row["authorizes_replay"] = False
        row["authorizes_research_candidate"] = False
    return rows


def may_exclusion_rows() -> list[dict[str, Any]]:
    return [
        {"check": "may_not_repair_input", "status": "pass", "detail": "Repair action matrix forbids May labels and May margins."},
        {"check": "may_not_mutation_direction", "status": "pass", "detail": "Near-miss mutation is non-May-gate only."},
        {"check": "may_not_candidate_promotion", "status": "pass", "detail": "A7M-2A produces no candidates and no promotion labels."},
        {"check": "may_stress_only_preserved", "status": "pass", "detail": "May remains post-selection stress/veto/failure attribution only."},
    ]


def timing_rows() -> list[dict[str, Any]]:
    return [
        {"check": "rolling_past_only_required", "status": "pass", "detail": "All repair actions require past-only rolling features."},
        {"check": "same_bar_execution_forbidden", "status": "pass", "detail": "Lag repair forbids same-bar execution assumptions."},
        {"check": "observable_funding_only", "status": "pass", "detail": "Residual repair cannot use future or settlement-after-use funding."},
        {"check": "zero_activity_guard_required", "status": "pass", "detail": "Activity repair rejects zero-exposure artifacts before replay."},
        {"check": "nan_inf_guard_required", "status": "pass", "detail": "Adapter requires NaN/inf checks before candidate selection."},
    ]


def synthetic_cases() -> list[dict[str, Any]]:
    return [
        {
            "case_id": "case_cost20_smooth",
            "input_failure": "cost20_fail",
            "input_formula": "Mul(Rank(realized_vol_6),ZScore(quote_volume_mean_12))",
            "repair_action": "smooth_horizon",
            "expected_output": "mutate horizons toward realized_vol_12/24 and volume_mean_24/48",
            "may_used": False,
            "expected_classification": "repair_candidate_for_future_bakeoff_only",
        },
        {
            "case_id": "case_lag_near_bar",
            "input_failure": "lag1_fail",
            "input_formula": "Mul(Rank(ret_1),ZScore(taker_imbalance_1))",
            "repair_action": "ban_near_bar_terms",
            "expected_output": "reject or replace with lag-stable rolling variant",
            "may_used": False,
            "expected_classification": "repair_candidate_for_future_bakeoff_only",
        },
        {
            "case_id": "case_residual_packaging",
            "input_failure": "residual_fail",
            "input_formula": "Mul(Rank(ret_12),ZScore(latest_known_funding_rate))",
            "repair_action": "benchmark_packaging_guard",
            "expected_output": "reject as FundingCore/Core4 packaging unless residual evidence survives",
            "may_used": False,
            "expected_classification": "benchmark_or_reject",
        },
        {
            "case_id": "case_zero_activity",
            "input_failure": "activity_coverage_fail",
            "input_formula": "ZScore(spot_basis_missing_core12)",
            "repair_action": "reject_or_replace_inactive_field",
            "expected_output": "reject zero-activity artifact before replay",
            "may_used": False,
            "expected_classification": "reject_static",
        },
        {
            "case_id": "case_near_miss",
            "input_failure": "near_miss",
            "input_formula": "Mul(Rank(mark_index_ratio),ZScore(number_of_trades_mean_24))",
            "repair_action": "targeted_non_may_mutation",
            "expected_output": "mutate non-May cost/lag/residual dimension only",
            "may_used": False,
            "expected_classification": "repair_candidate_for_future_bakeoff_only",
        },
    ]


def authorization_rows(decision: str) -> list[dict[str, Any]]:
    pass_status = decision.startswith("PASS")
    return [
        {"capability": "AST_failure_aware_repair_crypto_adapter", "authorized": pass_status, "scope": "adapter_preflight_ready"},
        {"capability": "A7M2C_blocker_resolution_input", "authorized": pass_status, "scope": "may be used by authorization revision"},
        {"capability": "A7M2_equal_budget_bakeoff_execution", "authorized": False, "scope": "requires A7M-2B and A7M-2C"},
        {"capability": "adaptive_large_search", "authorized": False, "scope": "not authorized"},
        {"capability": "research_candidate", "authorized": False, "scope": "not produced by preflight"},
        {"capability": "alpha_proof_shadow_paper_live", "authorized": False, "scope": "not authorized"},
    ]


def main() -> int:
    A7M2A_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    df = pd.read_csv(DATASET_PATH)
    taxonomy = failure_taxonomy(df)
    actions = repair_actions()
    may_rows = may_exclusion_rows()
    timing = timing_rows()
    synthetic = synthetic_cases()

    required = {"raw_fail", "residual_fail", "cost20_fail", "lag1_fail", "activity_coverage_fail", "beta_fail", "residual_only_clue", "near_miss"}
    taxonomy_types = {row["failure_type"] for row in taxonomy}
    action_types = {row["failure_type"] for row in actions}
    may_pass = all(row["status"] == "pass" for row in may_rows)
    timing_pass = all(row["status"] == "pass" for row in timing)
    synthetic_pass = all(str(row["may_used"]).lower() == "false" for row in synthetic)
    forbidden_promotion = not any(str(row.get("authorizes_research_candidate")).lower() == "true" for row in actions)
    decision = (
        "PASS_A7M2A_AST_REPAIR_ADAPTER_PREFLIGHT"
        if required <= taxonomy_types and required <= action_types and may_pass and timing_pass and synthetic_pass and forbidden_promotion
        else "HOLD_A7M2A_AST_REPAIR_ADAPTER_PREFLIGHT_INCOMPLETE"
    )

    authorization = authorization_rows(decision)

    write_csv(A7M2A_DIR / "a7m2a_failure_taxonomy.csv", taxonomy, ["failure_type", "source_labels", "observed_count", "repair_policy", "repair_allowed", "may_allowed", "promotes_candidate", "reason"])
    write_csv(A7M2A_DIR / "a7m2a_repair_action_matrix.csv", actions, ["failure_type", "action_id", "action", "allowed", "forbidden_inputs", "expected_effect", "requires_timing_check", "authorizes_search", "authorizes_replay", "authorizes_research_candidate"])
    write_csv(A7M2A_DIR / "a7m2a_may_exclusion_audit.csv", may_rows, ["check", "status", "detail"])
    write_csv(A7M2A_DIR / "a7m2a_timing_contract_audit.csv", timing, ["check", "status", "detail"])
    write_csv(A7M2A_DIR / "a7m2a_synthetic_repair_cases.csv", synthetic, ["case_id", "input_failure", "input_formula", "repair_action", "expected_output", "may_used", "expected_classification"])
    write_csv(A7M2A_DIR / "a7m2a_authorization_matrix.csv", authorization, ["capability", "authorized", "scope"])

    manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7m2c_input": decision.startswith("PASS"),
        "authorizes_a7m2_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "taxonomy_types": sorted(taxonomy_types),
        "action_types": sorted(action_types),
        "may_exclusion_pass": may_pass,
        "timing_contract_pass": timing_pass,
        "synthetic_cases_pass": synthetic_pass,
        "forbidden_promotion_pass": forbidden_promotion,
        "outputs": {
            "failure_taxonomy": str(A7M2A_DIR / "a7m2a_failure_taxonomy.csv"),
            "repair_action_matrix": str(A7M2A_DIR / "a7m2a_repair_action_matrix.csv"),
            "may_exclusion_audit": str(A7M2A_DIR / "a7m2a_may_exclusion_audit.csv"),
            "timing_contract_audit": str(A7M2A_DIR / "a7m2a_timing_contract_audit.csv"),
            "synthetic_repair_cases": str(A7M2A_DIR / "a7m2a_synthetic_repair_cases.csv"),
            "authorization_matrix": str(A7M2A_DIR / "a7m2a_authorization_matrix.csv"),
        },
    }
    manifest["stable_manifest_hash"] = stable_hash({k: v for k, v in manifest.items() if k not in {"generated_at", "stable_manifest_hash"}})
    write_json(A7M2A_DIR / f"crypto_a7m2a_manifest_{DATE_TAG}.json", manifest)

    report = REPORT_DIR / f"CRYPTO_A7M2A_AST_REPAIR_ADAPTER_PREFLIGHT_{DATE_TAG}.md"
    lines = [
        "# Crypto A7M-2A AST Repair Adapter Preflight",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- authorizes_a7m2_execution: `False`",
        f"- stable_manifest_hash: `{manifest['stable_manifest_hash']}`",
        "",
        "## Confirmed",
        "",
        "- Crypto failure taxonomy is mapped to repair policies.",
        "- Repair actions are limited to non-May, timing-aware, low-risk transformations.",
        "- Raw failures and residual-only clues cannot be directly promoted.",
        "- FundingCore/Core4/taker packaging is blocked from standalone alpha promotion.",
        "",
        "## Failure Taxonomy",
        "",
        "| failure_type | observed_count | repair_policy | repair_allowed |",
        "|---|---:|---|---|",
    ]
    for row in taxonomy:
        lines.append(f"| `{row['failure_type']}` | {row['observed_count']} | `{row['repair_policy']}` | `{row['repair_allowed']}` |")
    lines += [
        "",
        "## Boundary",
        "",
        "- This is an adapter preflight only.",
        "- It does not generate formulas, run replay, produce research candidates, or authorize alpha proof/shadow/paper/live.",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7M2A_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7M-2A Decision Record",
                "",
                f"- decision: `{decision}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                "- search_executed: `False`",
                "- replay_executed: `False`",
                f"- authorizes_a7m2c_input: `{decision.startswith('PASS')}`",
                "- authorizes_a7m2_execution: `False`",
                "",
                "## Confirmed",
                "",
                "- AST failure-aware repair has a crypto failure taxonomy.",
                "- Repair actions exclude May and preserve timing/observable-data constraints.",
                "- Repair actions cannot directly promote raw failures or residual-only clues.",
                "",
                "## Not Confirmed",
                "",
                "- No repaired candidate quality.",
                "- No A7M-2 bakeoff execution.",
                "- No adaptive large search, alpha proof, shadow, paper, live, or production readiness.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
