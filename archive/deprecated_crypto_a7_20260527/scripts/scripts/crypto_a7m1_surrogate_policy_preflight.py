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
A7M0_DIR = RUNTIME_DIR / "a7m0_failure_labeled_search_dataset"
A7M1_DIR = RUNTIME_DIR / "a7m1_surrogate_policy_preflight"
DATASET_PATH = A7M0_DIR / "crypto_a7m0_failure_labeled_candidate_dataset.csv"

FEATURE_COLUMNS = [
    "family",
    "arm",
    "field_family_signature",
    "operator_signature",
    "horizon",
    "formula_depth",
]

TARGETS = {
    "raw_survive": ["raw_validation_fail", "raw_recent_fail"],
    "residual_survive": [
        "residual_funding_validation_fail",
        "residual_funding_recent_fail",
        "residual_core4_recent_fail",
    ],
    "cost20_survive": ["cost20_validation_fail", "cost20_recent_fail"],
    "lag1_survive": ["lag1_validation_fail", "lag1_recent_fail"],
    "near_miss": ["near_miss_label"],
    "research_candidate": ["research_candidate_label"],
}

FORBIDDEN_POLICY_TARGETS = [
    "may_raw_severe_fail_stress_only",
    "may_residual_funding_negative_stress_only",
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


def build_targets(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for target, fail_cols in TARGETS.items():
        if target in {"near_miss", "research_candidate"}:
            out[target] = bool_series(out, fail_cols[0])
            continue
        fail_any = pd.Series(False, index=out.index)
        available_any = pd.Series(False, index=out.index)
        for col in fail_cols:
            if col in out.columns:
                fail_any |= bool_series(out, col)
                available_any |= out[col].notna()
        out[target] = available_any & (~fail_any)
    return out


def laplace_rate(success: int, total: int, prior: float, strength: float = 20.0) -> float:
    if total <= 0:
        return prior
    return (success + prior * strength) / (total + strength)


def feature_table(train: pd.DataFrame, targets: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    priors = {target: float(train[target].mean()) for target in targets}
    for feature in FEATURE_COLUMNS:
        for value, part in train.groupby(feature, dropna=False):
            row: dict[str, Any] = {
                "feature": feature,
                "value": str(value),
                "n": int(len(part)),
            }
            for target in targets:
                success = int(part[target].sum())
                row[f"{target}_rate"] = round(success / len(part), 6) if len(part) else 0.0
                row[f"{target}_smoothed"] = round(laplace_rate(success, len(part), priors[target]), 6)
            rows.append(row)
    return pd.DataFrame(rows)


def score_candidates(df: pd.DataFrame, table: pd.DataFrame, targets: list[str]) -> pd.DataFrame:
    out = df.copy()
    lookup: dict[tuple[str, str, str], float] = {}
    for _, row in table.iterrows():
        for target in targets:
            lookup[(str(row["feature"]), str(row["value"]), target)] = float(row[f"{target}_smoothed"])

    for target in targets:
        scores = []
        for _, row in out.iterrows():
            vals = []
            for feature in FEATURE_COLUMNS:
                key = (feature, str(row.get(feature)), target)
                if key in lookup:
                    vals.append(lookup[key])
            scores.append(sum(vals) / len(vals) if vals else 0.0)
        out[f"pred_{target}"] = scores

    out["expected_audit_value"] = (
        0.20 * out["pred_raw_survive"]
        + 0.20 * out["pred_residual_survive"]
        + 0.20 * out["pred_cost20_survive"]
        + 0.20 * out["pred_lag1_survive"]
        + 0.20 * out["pred_near_miss"]
    )
    out["novelty_proxy"] = (
        out["field_family_signature"].astype(str).map(lambda x: len(set(x.split(";")) if x and x != "nan" else set()))
        + out["operator_signature"].astype(str).map(lambda x: len(set(x.split(";")) if x and x != "nan" else set()))
        + out["horizon"].astype(str).map(lambda x: 0.5 if x in {"48", "48.0"} else 0.0)
    )
    return out


def lift_rows(scored: pd.DataFrame, targets: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    eligible = scored[scored["policy_training_eligible"].fillna(False).astype(str).str.lower().isin(["true", "1"])]
    for target in targets:
        if eligible.empty:
            rows.append({"target": target, "base_rate": 0.0, "top_decile_rate": 0.0, "lift": 0.0, "n": 0})
            continue
        base = float(eligible[target].mean())
        cutoff = eligible[f"pred_{target}"].quantile(0.90)
        top = eligible[eligible[f"pred_{target}"] >= cutoff]
        top_rate = float(top[target].mean()) if len(top) else 0.0
        rows.append(
            {
                "target": target,
                "base_rate": round(base, 6),
                "top_decile_rate": round(top_rate, 6),
                "lift": round((top_rate / base), 6) if base > 0 else "",
                "n": int(len(eligible)),
                "top_n": int(len(top)),
            }
        )
    return rows


def main() -> int:
    A7M1_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    df = pd.read_csv(DATASET_PATH)
    df = build_targets(df)

    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = "missing"
        df[col] = df[col].fillna("missing").astype(str)

    # Only historical selection labels can train policy. May labels and static-only dry preflight rows are excluded.
    train = df[
        df["policy_training_eligible"].fillna(False).astype(str).str.lower().isin(["true", "1"])
        & (df["source_run"] != "A7L1B_dry_preflight")
    ].copy()
    targets = list(TARGETS.keys())
    ft = feature_table(train, targets)
    scored = score_candidates(df, ft, targets)
    lift = lift_rows(scored, targets)

    may_columns_used = [col for col in FORBIDDEN_POLICY_TARGETS if col in targets or col in FEATURE_COLUMNS]
    policy_audit_rows = [
        {
            "check": "may_labels_excluded_from_targets",
            "status": "pass" if not may_columns_used else "hold",
            "detail": ";".join(may_columns_used) if may_columns_used else "no May stress label used as policy target",
        },
        {
            "check": "dry_preflight_rows_excluded_from_training",
            "status": "pass",
            "detail": "A7L1B rows may be scored but not used to estimate rates",
        },
        {
            "check": "surrogate_type",
            "status": "pass",
            "detail": "laplace_smoothed_empirical_group_model; no external ML dependency",
        },
        {
            "check": "large_search_authorization",
            "status": "pass",
            "detail": "A7M-1 does not authorize adaptive large search",
        },
    ]

    feature_table_path = A7M1_DIR / "a7m1_surrogate_feature_table.csv"
    scored_path = A7M1_DIR / "a7m1_candidate_surrogate_scores.csv"
    lift_path = A7M1_DIR / "a7m1_target_lift.csv"
    audit_path = A7M1_DIR / "a7m1_policy_training_audit.csv"

    ft.to_csv(feature_table_path, index=False)
    scored.to_csv(scored_path, index=False)
    write_csv(lift_path, lift, ["target", "base_rate", "top_decile_rate", "lift", "n", "top_n"])
    write_csv(audit_path, policy_audit_rows, ["check", "status", "detail"])

    lift_map = {row["target"]: row for row in lift}
    near_miss_lift = float(lift_map.get("near_miss", {}).get("lift") or 0.0)
    residual_lift = float(lift_map.get("residual_survive", {}).get("lift") or 0.0)
    cost_lift = float(lift_map.get("cost20_survive", {}).get("lift") or 0.0)
    useful = near_miss_lift >= 1.2 or (residual_lift >= 1.1 and cost_lift >= 1.1)
    decision = "PASS_A7M1_SURROGATE_PREFLIGHT" if useful and not may_columns_used else "HOLD_A7M1_SURROGATE_LIFT_WEAK"

    manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_search": False,
        "executes_replay": False,
        "trains_large_model": False,
        "surrogate_type": "laplace_smoothed_empirical_group_model",
        "authorizes_a7m2_adaptive_search": False,
        "authorizes_alpha_proof": False,
        "may_policy": {
            "may_labels_available_as_stress": True,
            "may_used_as_policy_target": False,
            "may_used_as_feature": False,
        },
        "inputs": {"failure_labeled_dataset": str(DATASET_PATH)},
        "outputs": {
            "surrogate_feature_table": str(feature_table_path),
            "candidate_surrogate_scores": str(scored_path),
            "target_lift": str(lift_path),
            "policy_training_audit": str(audit_path),
        },
        "training_rows": int(len(train)),
        "scored_rows": int(len(scored)),
        "near_miss_lift": near_miss_lift,
        "residual_survive_lift": residual_lift,
        "cost20_survive_lift": cost_lift,
    }
    manifest["stable_manifest_hash"] = stable_hash({k: v for k, v in manifest.items() if k not in {"generated_at", "stable_manifest_hash"}})
    write_json(A7M1_DIR / f"crypto_a7m1_manifest_{DATE_TAG}.json", manifest)

    report_path = REPORT_DIR / f"CRYPTO_A7M1_SURROGATE_POLICY_PREFLIGHT_{DATE_TAG}.md"
    report_lines = [
        "# Crypto A7M-1 Surrogate Policy Preflight",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- authorizes_a7m2_adaptive_search: `False`",
        f"- training_rows: `{len(train)}`",
        f"- scored_rows: `{len(scored)}`",
        "",
        "## Method",
        "",
        "A7M-1 uses a Laplace-smoothed empirical group model over family, arm, field-family signature, operator signature, horizon, and depth. It is a preflight surrogate, not an alpha model.",
        "",
        "## May Boundary",
        "",
        "- May stress labels are not policy targets.",
        "- May stress labels are not features.",
        "- May stress labels may only remain in the dataset for reporting/veto/failure attribution.",
        "",
        "## Target Lift",
        "",
        "| target | base_rate | top_decile_rate | lift |",
        "|---|---:|---:|---:|",
    ]
    for row in lift:
        report_lines.append(f"| `{row['target']}` | {row['base_rate']} | {row['top_decile_rate']} | {row['lift']} |")
    report_lines += [
        "",
        "## Decision",
        "",
        "A7M-1 is only a surrogate preflight. It does not authorize adaptive large search. A7M-2 still requires an explicit protocol and budget approval.",
    ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7M1_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7M-1 Decision Record",
                "",
                f"- decision: `{decision}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                "- search_executed: `False`",
                "- replay_executed: `False`",
                "- authorizes_a7m2_adaptive_search: `False`",
                "",
                "## Confirmed",
                "",
                "- Failure labels can be transformed into a basic non-May surrogate score.",
                "- May labels are excluded from policy targets and features.",
                "- Near-miss prediction is treated as more important than rare research-candidate prediction.",
                "",
                "## Not Confirmed",
                "",
                "- No large adaptive search is authorized.",
                "- No research candidate is created.",
                "- No alpha proof, shadow, paper, live, or production readiness.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
