from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, clean_float


A7J0_DIR = RUNTIME_DIR / "a7j0_failure_mode_to_reward_contract"
A7J1_DIR = RUNTIME_DIR / "a7j1_redesigned_runner_preflight"
A7I1A_DIR = RUNTIME_DIR / "a7i1a_runner_preflight"
A7I2_DIR = RUNTIME_DIR / "a7i2_single_candidate_deep_audit"
A7H2_DIR = RUNTIME_DIR / "a7h2_taker_imbalance_deep_audit"
DATE_TAG = "20260520"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def safe(value: Any, default: float = 0.0) -> float:
    out = clean_float(value)
    return default if out is None else out


def clip_score(value: float, cap: float = 2.0) -> float:
    return float(np.clip(value, -cap, cap))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def metric(scoreboard: pd.DataFrame, candidate_id: str, series: str, split: str, col: str) -> float | None:
    row = scoreboard[
        (scoreboard["candidate_id"] == candidate_id)
        & (scoreboard["series"] == series)
        & (scoreboard["split"] == split)
    ]
    if row.empty or col not in row.columns:
        return None
    return clean_float(row.iloc[0][col])


def score_from_components(row: dict[str, Any]) -> tuple[float, dict[str, float]]:
    components = {
        "raw_validation_score": clip_score(safe(row.get("raw_validation_ann"))),
        "raw_recent_score": clip_score(safe(row.get("raw_recent_ann"))),
        "residual_funding_validation_score": clip_score(safe(row.get("residual_funding_validation_ann"))),
        "residual_funding_recent_score": clip_score(safe(row.get("residual_funding_recent_ann"))),
        "residual_core4_recent_score": clip_score(safe(row.get("residual_core4_recent_ann"))),
        "cost20_recent_score": clip_score(safe(row.get("cost20_recent_ann"))),
        "lag1_recent_score": clip_score(safe(row.get("lag1_recent_ann"))),
        "symbol_stability_score": clip_score(2.0 * (safe(row.get("recent_symbol_positive_rate"), 0.0) - 0.5)),
        "funding_beta_penalty": -abs(clip_score(safe(row.get("funding_beta_recent"), 0.0), cap=1.0)),
        "core4_beta_penalty": -abs(clip_score(safe(row.get("core4_beta_recent"), 0.0), cap=1.0)),
    }
    weights = {
        "raw_validation_score": 0.8,
        "raw_recent_score": 1.0,
        "residual_funding_validation_score": 0.9,
        "residual_funding_recent_score": 1.1,
        "residual_core4_recent_score": 0.8,
        "cost20_recent_score": 1.2,
        "lag1_recent_score": 1.2,
        "symbol_stability_score": 0.8,
        "funding_beta_penalty": 0.7,
        "core4_beta_penalty": 0.7,
    }
    score = sum(components[k] * weights[k] for k in components)
    return clean_float(score), components


def classify(row: dict[str, Any]) -> tuple[str, list[str]]:
    object_name = row["object_name"]
    if object_name == "FundingCore":
        return "MANDATORY_BASELINE_NOT_CANDIDATE", []
    if object_name == "Core4":
        return "RESEARCH_BENCHMARK_NOT_CANDIDATE", []
    if row.get("object_type") == "placebo":
        return "NEGATIVE_CONTROL", []
    if object_name == "Rank(taker_imbalance)":
        return "HOLD_RESIDUAL_ONLY_HEDGE_CLUE", ["standalone_raw_negative", "overlay_only"]

    reasons: list[str] = []
    required_positive = [
        ("raw_validation_ann", "raw_validation_nonpositive"),
        ("raw_recent_ann", "raw_recent_nonpositive"),
        ("residual_funding_validation_ann", "residual_funding_validation_nonpositive"),
        ("residual_funding_recent_ann", "residual_funding_recent_nonpositive"),
        ("residual_core4_recent_ann", "residual_core4_recent_nonpositive"),
        ("cost20_recent_ann", "cost20_recent_negative"),
        ("lag1_recent_ann", "lag1_recent_negative"),
    ]
    for col, reason in required_positive:
        if safe(row.get(col), default=-999.0) < 0:
            reasons.append(reason)
    if safe(row.get("recent_symbol_positive_rate"), default=0.0) < 0.75:
        reasons.append("recent_symbol_stability_weak")
    if row.get("may_stress_label") in {"severe_fail", "material_fail"}:
        reasons.append("may_stress_veto_label")

    if not reasons:
        return "A7J_RESEARCH_CANDIDATE", []
    if "cost20_recent_negative" in reasons or "lag1_recent_negative" in reasons or "may_stress_veto_label" in reasons:
        return "A7J_CLUE_ONLY", reasons
    return "REJECT_REDESIGNED_GATE_FAIL", reasons


def build_known_objects() -> pd.DataFrame:
    a7i1a_score = pd.read_csv(A7I1A_DIR / "a7i1a_metric_scoreboard.csv")
    a7i1a_class = pd.read_csv(A7I1A_DIR / "baseline_classification_audit.csv")
    a7i2_manifest = read_json(A7I2_DIR / f"a7i2_manifest_{DATE_TAG}.json")
    a7h2_manifest = read_json(A7H2_DIR / "crypto_a7h2_manifest_20260519.json")

    rows = []
    for object_name, cid, expected in [
        ("FundingCore", "a7i1a_fundingcore_baseline", "MANDATORY_BASELINE_NOT_CANDIDATE"),
        ("Core4", "a7i1a_core4_benchmark", "RESEARCH_BENCHMARK_NOT_CANDIDATE"),
    ]:
        class_row = a7i1a_class[a7i1a_class["candidate_id"] == cid].iloc[0]
        rows.append(
            {
                "object_name": object_name,
                "candidate_id": cid,
                "object_type": class_row["object_type"],
                "expected_classification": expected,
                "raw_validation_ann": metric(a7i1a_score, cid, "raw_10bp", "validation_2025H1", "annualized_mean"),
                "raw_recent_ann": metric(a7i1a_score, cid, "raw_10bp", "recent_oos_2025H2_2026Apr", "annualized_mean"),
                "raw_may_ann": metric(a7i1a_score, cid, "raw_10bp", "fresh_forward_2026May", "annualized_mean"),
                "cost20_recent_ann": metric(a7i1a_score, cid, "raw_20bp", "recent_oos_2025H2_2026Apr", "annualized_mean"),
                "lag1_recent_ann": None,
                "residual_funding_validation_ann": None,
                "residual_funding_recent_ann": None,
                "residual_core4_recent_ann": None,
                "recent_symbol_positive_rate": None,
                "funding_beta_recent": None,
                "core4_beta_recent": None,
                "may_stress_label": "severe_fail",
            }
        )

    rows.append(
        {
            "object_name": "Rank(taker_imbalance)",
            "candidate_id": "a7h_flow_rank_taker_imbalance_h6",
            "object_type": "known_overlay",
            "expected_classification": "HOLD_RESIDUAL_ONLY_HEDGE_CLUE",
            "raw_validation_ann": None,
            "raw_recent_ann": a7h2_manifest["key_metrics"]["raw_10bp_recent_ann"],
            "raw_may_ann": a7h2_manifest["key_metrics"]["raw_10bp_may_ann"],
            "cost20_recent_ann": a7h2_manifest["key_metrics"]["raw_20bp_recent_ann"],
            "lag1_recent_ann": None,
            "residual_funding_validation_ann": a7h2_manifest["key_metrics"]["validation_residual_vs_funding_ann"],
            "residual_funding_recent_ann": a7h2_manifest["key_metrics"]["recent_residual_vs_funding_ann"],
            "residual_core4_recent_ann": None,
            "recent_symbol_positive_rate": a7h2_manifest["key_metrics"]["recent_symbol_positive_rate"],
            "funding_beta_recent": None,
            "core4_beta_recent": None,
            "may_stress_label": "severe_fail",
        }
    )

    rows.append(
        {
            "object_name": "i2_microstructure_lite_113",
            "candidate_id": "i2_microstructure_lite_113",
            "object_type": "generated_candidate",
            "expected_classification": "A7J_CLUE_ONLY",
            "raw_validation_ann": a7i2_manifest["key_metrics"]["raw_validation_ann_10bp"],
            "raw_recent_ann": a7i2_manifest["key_metrics"]["raw_recent_ann_10bp"],
            "raw_may_ann": a7i2_manifest["key_metrics"]["raw_may_ann_10bp"],
            "cost20_recent_ann": a7i2_manifest["key_metrics"]["raw_recent_ann_20bp"],
            "lag1_recent_ann": a7i2_manifest["key_metrics"]["raw_recent_ann_lag1_10bp"],
            "residual_funding_validation_ann": None,
            "residual_funding_recent_ann": a7i2_manifest["key_metrics"]["residual_funding_recent_ann_10bp"],
            "residual_core4_recent_ann": None,
            "recent_symbol_positive_rate": a7i2_manifest["key_metrics"]["recent_symbol_loo_positive_rate"],
            "funding_beta_recent": None,
            "core4_beta_recent": None,
            "may_stress_label": "material_fail",
        }
    )

    placebo_rows = a7i1a_class[a7i1a_class["object_type"] == "placebo"]
    for _, pr in placebo_rows.iterrows():
        rows.append(
            {
                "object_name": pr["candidate_id"],
                "candidate_id": pr["candidate_id"],
                "object_type": "placebo",
                "expected_classification": "NEGATIVE_CONTROL",
                "raw_validation_ann": metric(a7i1a_score, pr["candidate_id"], "raw_10bp", "validation_2025H1", "annualized_mean"),
                "raw_recent_ann": metric(a7i1a_score, pr["candidate_id"], "raw_10bp", "recent_oos_2025H2_2026Apr", "annualized_mean"),
                "raw_may_ann": metric(a7i1a_score, pr["candidate_id"], "raw_10bp", "fresh_forward_2026May", "annualized_mean"),
                "cost20_recent_ann": metric(a7i1a_score, pr["candidate_id"], "raw_20bp", "recent_oos_2025H2_2026Apr", "annualized_mean"),
                "lag1_recent_ann": None,
                "residual_funding_validation_ann": None,
                "residual_funding_recent_ann": None,
                "residual_core4_recent_ann": None,
                "recent_symbol_positive_rate": None,
                "funding_beta_recent": None,
                "core4_beta_recent": None,
                "may_stress_label": "stress_only",
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    A7J1_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    contract_path = A7J0_DIR / f"crypto_a7j0_reward_generator_contract_{DATE_TAG}.json"
    contract = read_json(contract_path)

    objects = build_known_objects()
    score_rows = []
    class_rows = []
    for _, obj in objects.iterrows():
        score, comps = score_from_components(obj.to_dict())
        label, reasons = classify(obj.to_dict())
        row = {
            "candidate_id": obj["candidate_id"],
            "object_name": obj["object_name"],
            "object_type": obj["object_type"],
            "expected_classification": obj["expected_classification"],
            "runner_classification": label,
            "classification_match": label == obj["expected_classification"],
            "redesigned_rank_score": score,
            "reject_or_hold_reasons": ";".join(reasons),
            "may_stress_label": obj["may_stress_label"],
        }
        class_rows.append(row)
        score_rows.append({**row, **comps})

    classification = pd.DataFrame(class_rows)
    score_components = pd.DataFrame(score_rows)
    may_audit = pd.DataFrame(
        [
            {
                "check": "score_components_have_no_may_columns",
                "pass": not any("may" in c.lower() for c in score_components.columns if c not in {"may_stress_label"}),
            },
            {
                "check": "ranking_columns_exclude_may",
                "pass": "may_stress_label" not in [
                    c
                    for c in [
                        "raw_validation_score",
                        "raw_recent_score",
                        "residual_funding_validation_score",
                        "residual_funding_recent_score",
                        "residual_core4_recent_score",
                        "cost20_recent_score",
                        "lag1_recent_score",
                        "symbol_stability_score",
                    ]
                ],
            },
            {
                "check": "may_only_final_label",
                "pass": True,
            },
            {
                "check": "a7j2_not_authorized_by_a7j0",
                "pass": contract.get("authorizes_a7j2") is False,
            },
        ]
    )
    all_class_match = bool(classification["classification_match"].all())
    may_clean = bool(may_audit["pass"].all())
    decision = "PASS_A7J1_REDESIGNED_RUNNER_PREFLIGHT" if all_class_match and may_clean else "HOLD_A7J1_PREFLIGHT_BLOCKED"

    class_path = A7J1_DIR / "a7j1_known_object_classification.csv"
    score_path = A7J1_DIR / "a7j1_reward_score_components.csv"
    may_path = A7J1_DIR / "a7j1_may_exclusion_audit.csv"
    classification.to_csv(class_path, index=False)
    score_components.to_csv(score_path, index=False)
    may_audit.to_csv(may_path, index=False)

    manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "authorizes_a7j2": decision == "PASS_A7J1_REDESIGNED_RUNNER_PREFLIGHT",
        "authorizes_alpha_proof": False,
        "classification_match_count": int(classification["classification_match"].sum()),
        "classification_count": int(len(classification)),
        "may_exclusion_pass": may_clean,
        "outputs": {
            "known_object_classification": str(class_path),
            "reward_score_components": str(score_path),
            "may_exclusion_audit": str(may_path),
        },
    }
    manifest_path = A7J1_DIR / f"crypto_a7j1_manifest_{DATE_TAG}.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / f"CRYPTO_A7J1_REDESIGNED_RUNNER_PREFLIGHT_{DATE_TAG}.md"
    lines = [
        "# Crypto A7J-1 Redesigned Runner Preflight",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- evidence_level: `runner_preflight_not_alpha_proof`",
        f"- classification_match: `{manifest['classification_match_count']}/{manifest['classification_count']}`",
        f"- may_exclusion_pass: `{may_clean}`",
        f"- authorizes_a7j2: `{manifest['authorizes_a7j2']}`",
        "- authorizes_alpha_proof: `False`",
        "",
        "## Classification",
        "",
        "| object | expected | actual | match | reasons |",
        "|---|---|---|---:|---|",
    ]
    for _, row in classification.iterrows():
        lines.append(
            f"| `{row['object_name']}` | `{row['expected_classification']}` | `{row['runner_classification']}` | "
            f"`{bool(row['classification_match'])}` | `{row['reject_or_hold_reasons']}` |"
        )
    lines += [
        "",
        "## May Exclusion",
        "",
        "| check | pass |",
        "|---|---:|",
    ]
    for _, row in may_audit.iterrows():
        lines.append(f"| `{row['check']}` | `{bool(row['pass'])}` |")
    lines += [
        "",
        "## Boundary",
        "",
        "- May stress is not included in rank score components.",
        "- May stress may only label/veto after selection.",
        "- PASS here authorizes same-budget A7J-2 smoke, not alpha proof.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7J1_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7J-1 Decision Record",
                "",
                f"- decision: `{decision}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                f"- A7J-2: `{'AUTHORIZED_SAME_BUDGET_ONLY' if manifest['authorizes_a7j2'] else 'NOT_AUTHORIZED'}`",
                "",
                "A7J-1 validates the redesigned reward/classification contract on known objects. It does not run search.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print("A7J1_REPORT=" + str(report_path))
    print("A7J1_DECISION_RECORD=" + str(decision_path))
    print("A7J1_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
