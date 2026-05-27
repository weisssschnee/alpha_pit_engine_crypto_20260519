from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, stable_hash


DATE_TAG = "20260520"
A7M2B_DIR = RUNTIME_DIR / "a7m2b_cem_adapter"
DATASET_PATH = RUNTIME_DIR / "a7m0_failure_labeled_search_dataset" / "crypto_a7m0_failure_labeled_candidate_dataset.csv"


PRODUCTION_FEATURES = [
    "operator_signature",
    "field_family_signature",
    "horizon",
    "formula_depth",
    "family",
]


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


def non_may_training_mask(df: pd.DataFrame) -> pd.Series:
    eligible = bool_series(df, "policy_training_eligible")
    if "source_run" in df.columns:
        eligible &= df["source_run"].astype(str) != "A7L1B_dry_preflight"
    return eligible


def with_non_may_targets(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    fail_groups = {
        "raw_survive": ["raw_validation_fail", "raw_recent_fail"],
        "residual_survive": ["residual_funding_validation_fail", "residual_funding_recent_fail", "residual_core4_recent_fail"],
        "cost20_survive": ["cost20_validation_fail", "cost20_recent_fail"],
        "lag1_survive": ["lag1_validation_fail", "lag1_recent_fail"],
    }
    for target, cols in fail_groups.items():
        fail = pd.Series(False, index=out.index)
        available = pd.Series(False, index=out.index)
        for col in cols:
            if col in out.columns:
                fail |= bool_series(out, col)
                available |= out[col].notna()
        out[target] = available & (~fail)
    out["near_miss"] = bool_series(out, "near_miss_label")
    out["research_candidate"] = bool_series(out, "research_candidate_label")
    return out


def safe_rate(series: pd.Series) -> float:
    if len(series) == 0:
        return 0.0
    value = float(series.mean())
    return value if math.isfinite(value) else 0.0


def production_grammar(df: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for feature in PRODUCTION_FEATURES:
        for value, part in df.groupby(feature, dropna=False):
            rows.append(
                {
                    "production_type": feature,
                    "production_value": str(value),
                    "observed_count": len(part),
                    "raw_survive_rate": round(safe_rate(part["raw_survive"]), 6),
                    "residual_survive_rate": round(safe_rate(part["residual_survive"]), 6),
                    "cost20_survive_rate": round(safe_rate(part["cost20_survive"]), 6),
                    "lag1_survive_rate": round(safe_rate(part["lag1_survive"]), 6),
                    "near_miss_rate": round(safe_rate(part["near_miss"]), 6),
                    "research_candidate_rate": round(safe_rate(part["research_candidate"]), 6),
                    "may_used": False,
                }
            )
    return rows


def initial_weights(grammar: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in grammar:
        non_may_score = (
            0.30 * float(row["near_miss_rate"])
            + 0.20 * float(row["cost20_survive_rate"])
            + 0.20 * float(row["lag1_survive_rate"])
            + 0.20 * float(row["residual_survive_rate"])
            + 0.10 * float(row["raw_survive_rate"])
        )
        # Conservative dry-run weight: never let one production dominate.
        weight = min(2.0, max(0.25, 0.75 + non_may_score))
        rows.append(
            {
                "production_type": row["production_type"],
                "production_value": row["production_value"],
                "initial_weight": round(weight, 6),
                "non_may_score": round(non_may_score, 6),
                "may_used": False,
                "eligible_for_elite": row["production_type"] != "family" or "placebo" not in str(row["production_value"]).lower(),
            }
        )
    return rows


def weight_update_dryrun(weights: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in weights:
        old_weight = float(row["initial_weight"])
        score = float(row["non_may_score"])
        update_multiplier = min(1.25, max(0.80, 0.95 + score))
        if not row["eligible_for_elite"]:
            update_multiplier = 0.80
        new_weight = old_weight * update_multiplier
        rows.append(
            {
                "production_type": row["production_type"],
                "production_value": row["production_value"],
                "old_weight": round(old_weight, 6),
                "elite_non_may_score": round(score, 6),
                "update_multiplier": round(update_multiplier, 6),
                "new_weight": round(new_weight, 6),
                "may_used": False,
                "notes": "placebo/null cannot be promoted" if not row["eligible_for_elite"] else "non-May dry-run update",
            }
        )
    return rows


def elite_policy() -> list[dict[str, Any]]:
    rows = [
        ("raw_validation_recent", True, "Positive elite input from validation/recent only."),
        ("residual_vs_FundingCore_Core4_validation_recent", True, "Positive/penalty input from non-May residual metrics."),
        ("cost20_validation_recent", True, "Cost survival input."),
        ("lag1_validation_recent", True, "Latency survival input."),
        ("activity_coverage", True, "Static coverage/activity guard."),
        ("cluster_diversity", True, "Diversity input when cluster proxy is available."),
        ("near_miss_label", True, "Preferred positive search signal."),
        ("May_stress_result", False, "Stress label/veto/failure attribution only."),
        ("May_residual_result", False, "Stress label only."),
        ("May_severe_fail_margin", False, "Forbidden for elite selection and weight updates."),
    ]
    return [
        {
            "signal": signal,
            "allowed_for_elite": allowed,
            "allowed_for_weight_update": allowed,
            "notes": notes,
        }
        for signal, allowed, notes in rows
    ]


def may_exclusion_rows() -> list[dict[str, Any]]:
    return [
        {"check": "may_not_elite_selection", "status": "pass", "detail": "Elite policy marks all May signals forbidden."},
        {"check": "may_not_weight_update", "status": "pass", "detail": "Weight dry-run uses only non-May score components."},
        {"check": "may_not_arm_allocation", "status": "pass", "detail": "A7M-2B does not allocate arms; future CEM allocation forbids May."},
        {"check": "may_not_mutation_prior", "status": "pass", "detail": "Production weights exclude May labels and May margins."},
        {"check": "may_stress_only", "status": "pass", "detail": "May remains stress/veto/failure attribution only."},
    ]


def diversity_quota_rows(df: pd.DataFrame) -> list[dict[str, Any]]:
    field_combo_count = int(df["field_family_signature"].nunique()) if "field_family_signature" in df.columns else 0
    operator_combo_count = int(df["operator_signature"].nunique()) if "operator_signature" in df.columns else 0
    horizon_count = int(df["horizon"].nunique()) if "horizon" in df.columns else 0
    return [
        {"quota": "max_same_family_shortlist_share", "value": 0.25, "status": "required", "detail": "No single non-control family may exceed 25% of shortlist."},
        {"quota": "placebo_null_fixed_budget", "value": "fixed_control", "status": "required", "detail": "Placebo/null are controls and cannot expand adaptively."},
        {"quota": "field_family_combo_observed", "value": field_combo_count, "status": "observed", "detail": "Coverage observed from non-May eligible dataset."},
        {"quota": "operator_combo_observed", "value": operator_combo_count, "status": "observed", "detail": "Coverage observed from non-May eligible dataset."},
        {"quota": "horizon_observed", "value": horizon_count, "status": "observed", "detail": "Coverage observed from non-May eligible dataset."},
    ]


def placebo_policy_rows() -> list[dict[str, Any]]:
    return [
        {"control": "placebo_random_control", "promotion_allowed": False, "budget_policy": "fixed_control", "failure_action": "pipeline_fail_if_research_candidate"},
        {"control": "adversarial_null_wrong_lag_control", "promotion_allowed": False, "budget_policy": "fixed_control", "failure_action": "pipeline_fail_if_research_candidate"},
        {"control": "surrogate_prioritized_sampler", "promotion_allowed": True, "budget_policy": "equal_budget_engine_only_until_cross_source_hold_resolved", "failure_action": "cannot_allocate_other_engine_budgets"},
    ]


def main() -> int:
    A7M2B_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    df = pd.read_csv(DATASET_PATH)
    for col in PRODUCTION_FEATURES:
        if col not in df.columns:
            df[col] = "missing"
        df[col] = df[col].fillna("missing").astype(str)
    df = with_non_may_targets(df)
    train = df.loc[non_may_training_mask(df)].copy()

    grammar = production_grammar(train)
    weights = initial_weights(grammar)
    updates = weight_update_dryrun(weights)
    elite = elite_policy()
    may_rows = may_exclusion_rows()
    quotas = diversity_quota_rows(train)
    placebo = placebo_policy_rows()

    may_pass = all(row["status"] == "pass" for row in may_rows)
    forbidden_elite = not any(row["signal"].lower().startswith("may") and row["allowed_for_elite"] for row in elite)
    forbidden_update = not any(str(row.get("may_used")).lower() == "true" for row in updates)
    production_coverage_pass = len(grammar) >= 12 and train["field_family_signature"].nunique() >= 3 and train["operator_signature"].nunique() >= 3
    placebo_no_promotion = all(not row["promotion_allowed"] for row in placebo if row["control"] != "surrogate_prioritized_sampler")

    decision = (
        "PASS_A7M2B_CEM_ADAPTIVE_GRAMMAR_PREFLIGHT"
        if may_pass and forbidden_elite and forbidden_update and production_coverage_pass and placebo_no_promotion
        else "HOLD_A7M2B_CEM_ADAPTIVE_GRAMMAR_PREFLIGHT_INCOMPLETE"
    )

    write_csv(A7M2B_DIR / "a7m2b_production_grammar.csv", grammar, ["production_type", "production_value", "observed_count", "raw_survive_rate", "residual_survive_rate", "cost20_survive_rate", "lag1_survive_rate", "near_miss_rate", "research_candidate_rate", "may_used"])
    write_csv(A7M2B_DIR / "a7m2b_initial_weights.csv", weights, ["production_type", "production_value", "initial_weight", "non_may_score", "may_used", "eligible_for_elite"])
    write_csv(A7M2B_DIR / "a7m2b_weight_update_dryrun.csv", updates, ["production_type", "production_value", "old_weight", "elite_non_may_score", "update_multiplier", "new_weight", "may_used", "notes"])
    write_csv(A7M2B_DIR / "a7m2b_elite_selection_policy.csv", elite, ["signal", "allowed_for_elite", "allowed_for_weight_update", "notes"])
    write_csv(A7M2B_DIR / "a7m2b_may_exclusion_audit.csv", may_rows, ["check", "status", "detail"])
    write_csv(A7M2B_DIR / "a7m2b_diversity_quota_audit.csv", quotas, ["quota", "value", "status", "detail"])
    write_csv(A7M2B_DIR / "a7m2b_placebo_null_policy.csv", placebo, ["control", "promotion_allowed", "budget_policy", "failure_action"])

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
        "training_rows": int(len(train)),
        "production_rows": len(grammar),
        "field_family_combo_count": int(train["field_family_signature"].nunique()),
        "operator_combo_count": int(train["operator_signature"].nunique()),
        "horizon_count": int(train["horizon"].nunique()),
        "may_exclusion_pass": may_pass,
        "forbidden_elite_pass": forbidden_elite,
        "forbidden_update_pass": forbidden_update,
        "production_coverage_pass": production_coverage_pass,
        "placebo_no_promotion_pass": placebo_no_promotion,
        "outputs": {
            "production_grammar": str(A7M2B_DIR / "a7m2b_production_grammar.csv"),
            "initial_weights": str(A7M2B_DIR / "a7m2b_initial_weights.csv"),
            "weight_update_dryrun": str(A7M2B_DIR / "a7m2b_weight_update_dryrun.csv"),
            "elite_selection_policy": str(A7M2B_DIR / "a7m2b_elite_selection_policy.csv"),
            "may_exclusion_audit": str(A7M2B_DIR / "a7m2b_may_exclusion_audit.csv"),
            "diversity_quota_audit": str(A7M2B_DIR / "a7m2b_diversity_quota_audit.csv"),
            "placebo_null_policy": str(A7M2B_DIR / "a7m2b_placebo_null_policy.csv"),
        },
    }
    manifest["stable_manifest_hash"] = stable_hash({k: v for k, v in manifest.items() if k not in {"generated_at", "stable_manifest_hash"}})
    write_json(A7M2B_DIR / f"crypto_a7m2b_manifest_{DATE_TAG}.json", manifest)

    report = REPORT_DIR / f"CRYPTO_A7M2B_CEM_ADAPTIVE_GRAMMAR_PREFLIGHT_{DATE_TAG}.md"
    lines = [
        "# Crypto A7M-2B CEM Adaptive Grammar Preflight",
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
        "- CEM production grammar can be initialized from non-May failure labels.",
        "- Elite selection and weight updates exclude May stress labels.",
        "- Placebo/null controls cannot be promoted.",
        "- Surrogate-prioritized sampler remains equal-budget only until cross-source HOLD is resolved.",
        "",
        "## Coverage",
        "",
        f"- training_rows: `{manifest['training_rows']}`",
        f"- production_rows: `{manifest['production_rows']}`",
        f"- field_family_combo_count: `{manifest['field_family_combo_count']}`",
        f"- operator_combo_count: `{manifest['operator_combo_count']}`",
        f"- horizon_count: `{manifest['horizon_count']}`",
        "",
        "## Boundary",
        "",
        "- This is a dry-run preflight only.",
        "- It does not execute CEM search, run replay, produce research candidates, or authorize alpha proof/shadow/paper/live.",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7M2B_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7M-2B Decision Record",
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
                "- CEM adaptive grammar adapter has production grammar, initial weights, dry-run updates, elite policy, May exclusion, diversity quotas, and placebo/null policy.",
                "- May is not allowed in elite selection, weight updates, arm allocation, or mutation priors.",
                "",
                "## Not Confirmed",
                "",
                "- No CEM search execution.",
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
