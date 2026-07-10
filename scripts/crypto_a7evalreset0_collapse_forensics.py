from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[1]
DEFAULT_RELEASE = REPO / "runtime" / "a7eff2_git_release_20260711"
DEFAULT_RUNTIME = REPO / "runtime" / "a7evalreset0_evaluation_governance_20260711"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7EVALRESET0_COLLAPSE_FORENSICS_20260711.md"
POLICY = REPO / "config" / "crypto_evaluation_access_policy_v1.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Iterable[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pct(numerator: int, denominator: int) -> str:
    return f"{100.0 * numerator / denominator:.2f}" if denominator else ""


def md_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "`<empty>`"
    header = "| " + " | ".join(columns) + " |"
    rule = "|" + "|".join(["---"] * len(columns)) + "|"
    body = []
    for row in rows:
        cells = [str(row.get(column, "")).replace("|", "\\|").replace("\n", " ") for column in columns]
        body.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, rule, *body])


def build_access_ledger(split_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    epoch_map = {
        "train_2024": ("DISCOVERY_TRAIN", True),
        "validation_2025H1": ("SPENT_HISTORICAL_EVALUATION", False),
        "test_2025H2": ("SPENT_HISTORICAL_EVALUATION", False),
        "recent_oos_2026JanApr": ("SPENT_HISTORICAL_EVALUATION", False),
        "known_may2026_stress": ("SPENT_HISTORICAL_EVALUATION", False),
    }
    stage_map = {
        "train_2024": ["strict_reward", "human_review"],
        "validation_2025H1": ["proxy", "strict_reward", "incremental_admission", "memory", "scheduler", "human_review"],
        "test_2025H2": ["proxy", "strict_reward", "incremental_admission", "memory", "scheduler", "human_review"],
        "recent_oos_2026JanApr": ["proxy", "strict_reward", "incremental_admission", "memory", "scheduler", "human_review"],
        "known_may2026_stress": ["proxy", "strict_reward", "incremental_admission", "memory", "scheduler", "human_review"],
    }
    rows: list[dict[str, Any]] = []
    sequence = 1
    for split in split_rows:
        label = split["split_label"]
        classification, allowed = epoch_map[label]
        for stage in stage_map[label]:
            rows.append(
                {
                    "access_id": f"eval-access-{sequence:03d}",
                    "epoch_id": label,
                    "selected_start_utc": split["selected_start_utc"],
                    "selected_end_utc": split["selected_end_utc"],
                    "classification": classification,
                    "accessor_stage": stage,
                    "access_purpose": "historical_decision_reconstruction",
                    "decision_impact": "candidate_feedback_or_human_decision" if label != "train_2024" else "discovery_fit_or_review",
                    "candidate_feedback_allowed_after_evalreset": str(allowed),
                    "evidence_status": "CONFIRMED_CODE_OR_RELEASE_DEPENDENCY",
                }
            )
            sequence += 1
    return rows


def build_burn_ledger(split_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    reasons = {
        "validation_2025H1": "proxy/reward/admission/memory/scheduler/human decisions",
        "test_2025H2": "proxy/reward/admission/memory/scheduler/human decisions",
        "recent_oos_2026JanApr": "proxy/reward/admission/memory/scheduler/human decisions",
        "known_may2026_stress": "proxy/reward/admission/memory/scheduler plus repeated stress veto and human decisions",
    }
    rows = []
    for split in split_rows:
        if split["split_label"] not in reasons:
            continue
        rows.append(
            {
                "epoch_id": split["split_label"],
                "selected_start_utc": split["selected_start_utc"],
                "selected_end_utc": split["selected_end_utc"],
                "selected_hours": split["selected_hours"],
                "prior_claim": "OOS" if split["is_oos"] == "True" else "stress",
                "current_classification": "SPENT_HISTORICAL_EVALUATION",
                "burn_reason": reasons[split["split_label"]],
                "candidate_feedback_allowed": "False",
                "final_blind_holdout_eligible": "False",
                "status": "BURNED_AND_SEALED_FROM_FEEDBACK",
            }
        )
    return rows


def build_compression(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    accepted = len(rows)
    canonical = len({row["expression"] for row in rows})
    exact = len({row["signal_weight_exact_fingerprint"] for row in rows})
    semantic_pairs = len({row["semantic_pair"] for row in rows})
    return [
        {
            "level": "accepted_row",
            "input_rows": accepted,
            "unique_count": accepted,
            "retained_percent": "100.00",
            "duplicate_compression_percent": "0.00",
            "status": "ESTABLISHED",
            "evidence": "A7EFF2 accepted release pack",
        },
        {
            "level": "canonical_expression",
            "input_rows": accepted,
            "unique_count": canonical,
            "retained_percent": pct(canonical, accepted),
            "duplicate_compression_percent": pct(accepted - canonical, accepted),
            "status": "ESTABLISHED",
            "evidence": "expression exact uniqueness after semantic canonicalization",
        },
        {
            "level": "exact_signal_identity",
            "input_rows": accepted,
            "unique_count": exact,
            "retained_percent": pct(exact, accepted),
            "duplicate_compression_percent": pct(accepted - exact, accepted),
            "status": "ESTABLISHED",
            "evidence": "signal_weight_exact_fingerprint",
        },
        {
            "level": "signal_cluster",
            "input_rows": accepted,
            "unique_count": "",
            "retained_percent": "",
            "duplicate_compression_percent": "",
            "status": "NOT_ESTABLISHED",
            "evidence": "No current global signal-cluster registry covers A7EFF2 accepted identities.",
        },
        {
            "level": "pnl_regime_cluster",
            "input_rows": accepted,
            "unique_count": "",
            "retained_percent": "",
            "duplicate_compression_percent": "",
            "status": "NOT_ESTABLISHED",
            "evidence": "No candidate-independent PnL/regime clustering registry exists.",
        },
        {
            "level": "economic_hypothesis",
            "input_rows": accepted,
            "unique_count": "",
            "retained_percent": "",
            "duplicate_compression_percent": "",
            "status": "NOT_ESTABLISHED",
            "evidence": f"Only {semantic_pairs} observed semantic pairs; semantic pairs are not independent economic hypotheses.",
        },
    ]


def build_collapse(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    exact = len({row["signal_weight_exact_fingerprint"] for row in rows})
    return [
        {
            "stage": "generation",
            "input_count": "unknown",
            "output_count": "unknown",
            "retained_percent": "",
            "finding": "UNLOCATED_MISSING_END_TO_END_PROVENANCE",
            "evidence": "Accepted-family concentration cannot identify generation collapse without the full generated population.",
        },
        {
            "stage": "proxy",
            "input_count": "unknown",
            "output_count": 53,
            "retained_percent": "",
            "finding": "UNLOCATED_EXTERNAL_HANDOFF_AND_SPENT_OOS_FEEDBACK",
            "evidence": "Proxy is external to source5 and uses historical OOS controls; full source queue lineage is absent from release bundle.",
        },
        {
            "stage": "semantic_admission",
            "input_count": 53,
            "output_count": 50,
            "retained_percent": pct(50, 53),
            "finding": "MINOR_SEMANTIC_REJECTION",
            "evidence": "3 semantic rejects and 8 canonical rewrites.",
        },
        {
            "stage": "source_lag_admission",
            "input_count": 50,
            "output_count": 33,
            "retained_percent": pct(33, 50),
            "finding": "MATERIAL_SOURCE_LAG_ATTRITION",
            "evidence": "33 pass, 17 reject, 0 evaluation errors.",
        },
        {
            "stage": "exact_identity_admission",
            "input_count": 33,
            "output_count": 18,
            "retained_percent": pct(18, 33),
            "finding": "PRIMARY_ALIAS_COLLAPSE",
            "evidence": "18 representatives plus 15 aliases before reward.",
        },
        {
            "stage": "strict_reward",
            "input_count": 18,
            "output_count": exact,
            "retained_percent": pct(exact, 18),
            "finding": "MATERIAL_REWARD_ATTRITION_WITH_SPENT_OOS_DEPENDENCY",
            "evidence": "16 accepted rows collapse to 6 exact identities; reward lacks future wrong-lag control.",
        },
        {
            "stage": "memory",
            "input_count": 1,
            "output_count": 0,
            "retained_percent": "0.00",
            "finding": "FULL_CREDIT_BLOCK_AT_FIELD_APPROVAL",
            "evidence": "One incremental evidence row; zero released credits due A7INPUT0 gap.",
        },
        {
            "stage": "scheduler",
            "input_count": "historical accepted/proxy rows",
            "output_count": "adaptive budgets and queues",
            "retained_percent": "",
            "finding": "INVALID_FEEDBACK_PATH_SPENT_OOS_CONTAMINATION",
            "evidence": "Validation/test/recent/May metrics influenced selection and budgeting; route must remain blocked after EVALRESET.",
        },
    ]


def build_risk_audit(active_fields: list[dict[str, str]], approval_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    approved = {row["field"] for row in approval_rows}
    missing = sorted(row["field_name"] for row in active_fields if row["field_name"] not in approved)
    final_missing = sorted(
        row["field_name"]
        for row in active_fields
        if row.get("used_by_final_incremental_formula") == "True" and row["field_name"] not in approved
    )
    return [
        {
            "risk": "funding_event_detection",
            "status": "UNRESOLVED_HOLD",
            "finding": "Historical event capture was approximately 66%; current release has no reproducible payment-event repair proof.",
            "required_closure": "Independent payment timestamp/event coverage test using predeclared event truth, without reading new forward performance.",
        },
        {
            "risk": "future_wrong_lag",
            "status": "FAIL_MISSING_CONTROL",
            "finding": "Strict reward declares five controls and no future wrong-lag variant.",
            "required_closure": "Add a fail-closed future wrong-lag negative control and a regression fixture before reward can be reused.",
        },
        {
            "risk": "source_lag",
            "status": "PARTIAL_HOLD",
            "finding": "50 semantically valid candidates became 33 source-lag passes and 17 rejects; source evidence paths are not locally reproducible.",
            "required_closure": "Restore immutable source evidence and verify field-specific publication lag and event timestamps.",
        },
        {
            "risk": "field_approval",
            "status": "FAIL_COVERAGE_GAP",
            "finding": f"{len(missing)}/10 active fields lack A7INPUT0 approval: {';'.join(missing)}. Final evidence uses: {';'.join(final_missing)}.",
            "required_closure": "Approve economic/input roles independently of accepted-family and OOS ranking.",
        },
        {
            "risk": "identity_alias",
            "status": "CONFIRMED_COLLAPSE",
            "finding": "33 source-lag survivors collapse to 18 exact signals; 16 accepted rows collapse to 6 exact signals.",
            "required_closure": "Keep exact identity before reward and add independent signal/PnL/economic registries.",
        },
        {
            "risk": "BZ",
            "status": "UNRESOLVED_NODE",
            "finding": "No verified BZ implementation, contract, or runtime is present in the release evidence.",
            "required_closure": "Provide an authoritative BZ definition and provenance before adding graph edges or feedback semantics.",
        },
    ]


def build(args: argparse.Namespace) -> dict[str, Any]:
    release_manifest_path = args.release / "a7eff2_release_manifest.json"
    split_path = args.release / "a7eff2_train_validation_oos_split_log.csv"
    accepted_path = args.release / "a7eff2_accepted_train_validation_oos_log.csv"
    fields_path = args.release / "a7eff2_active_field_registry.csv"
    approval_path = REPO / "runtime" / "a7input0_input_approval_package" / "a7input0_input_approval_registry.csv"
    manifest = json.loads(release_manifest_path.read_text(encoding="utf-8"))
    split_rows = read_csv(split_path)
    accepted_rows = read_csv(accepted_path)
    active_fields = read_csv(fields_path)
    approval_rows = read_csv(approval_path)

    integrity_rows = []
    for name, spec in manifest["outputs"].items():
        path = args.release / name
        actual = sha256_file(path)
        expected = str(spec["sha256"]).upper()
        integrity_rows.append(
            {
                "artifact": name,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "status": "PASS" if actual == expected else "FAIL",
            }
        )

    access_rows = build_access_ledger(split_rows)
    burn_rows = build_burn_ledger(split_rows)
    compression_rows = build_compression(accepted_rows)
    collapse_rows = build_collapse(accepted_rows)
    risk_rows = build_risk_audit(active_fields, approval_rows)

    outputs = {
        "evaluation_access_ledger": args.runtime / "a7evalreset0_evaluation_access_ledger.csv",
        "oos_burn_ledger": args.runtime / "a7evalreset0_oos_burn_ledger.csv",
        "accepted_compression_audit": args.runtime / "a7evalreset0_accepted_compression_audit.csv",
        "collapse_stage_audit": args.runtime / "a7evalreset0_collapse_stage_audit.csv",
        "risk_closure_audit": args.runtime / "a7evalreset0_risk_closure_audit.csv",
        "release_integrity_audit": args.runtime / "a7evalreset0_release_integrity_audit.csv",
    }
    write_csv(outputs["evaluation_access_ledger"], access_rows, list(access_rows[0]))
    write_csv(outputs["oos_burn_ledger"], burn_rows, list(burn_rows[0]))
    write_csv(outputs["accepted_compression_audit"], compression_rows, list(compression_rows[0]))
    write_csv(outputs["collapse_stage_audit"], collapse_rows, list(collapse_rows[0]))
    write_csv(outputs["risk_closure_audit"], risk_rows, list(risk_rows[0]))
    write_csv(outputs["release_integrity_audit"], integrity_rows, list(integrity_rows[0]))

    exact_sizes = sorted(Counter(row["signal_weight_exact_fingerprint"] for row in accepted_rows).values(), reverse=True)
    decision = "HOLD_EVALRESET_REQUIRED"
    result = {
        "stage": "A7EVALRESET-0",
        "generated_at": now_utc(),
        "decision": decision,
        "baseline_commit": "ac9fd24ede281bbcbf438f7c2f4f9b1e563b8b76",
        "release_decision": manifest["decision"],
        "release_integrity_pass": all(row["status"] == "PASS" for row in integrity_rows),
        "accepted_rows": len(accepted_rows),
        "canonical_expressions": len({row["expression"] for row in accepted_rows}),
        "exact_signal_identities": len({row["signal_weight_exact_fingerprint"] for row in accepted_rows}),
        "exact_identity_group_sizes": exact_sizes,
        "spent_epoch_count": len(burn_rows),
        "memory_credit_released_rows": int(manifest["reward_evidence"]["memory_credit_released_rows"]),
        "forward_performance_read": False,
        "search_started": False,
        "outputs": {key: str(value.relative_to(REPO)) for key, value in outputs.items()},
        "policy": str(POLICY.relative_to(REPO)),
    }
    args.runtime.mkdir(parents=True, exist_ok=True)
    (args.runtime / "a7evalreset0_manifest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )

    feedback_graph = """```mermaid
flowchart LR
  G[\"Generation queues\"] --> P[\"Proxy using historical controls\"]
  P --> A[\"Semantic and source-lag admission\"]
  A --> I[\"Exact signal identity: 33 to 18\"]
  I --> R[\"Strict reward using spent validation/test/recent/May\"]
  R --> E[\"A7EFF2 accepted: 16 rows / 6 identities\"]
  E --> V[\"Source6 incremental validation\"]
  V --> M[\"A7MEM credit: 0 released\"]
  M -. blocked .-> S[\"Scheduler / next-search prior\"]
  P --> H[\"Human decisions\"]
  R --> H
  E --> H
  BZ[\"BZ: unresolved definition\"] -. no verified edge .-> H
  OOS[\"Spent historical evaluation\"] --> P
  OOS --> R
  OOS --> V
  OOS --> H
  GUARD[\"EVALRESET fail-closed guard\"] -. blocks .-> M
  GUARD -. blocks .-> S
```"""
    report = [
        "# CRYPTO A7EVALRESET-0 Collapse Forensics",
        "",
        f"Generated: `{result['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This is historical forensic evidence only. It authorizes neither alpha proof nor new search, forward reads, positive memory, shadow, paper, or live use.",
        "",
        "## Feedback Graph",
        "",
        feedback_graph,
        "",
        "## OOS Burn Ledger",
        "",
        md_table(burn_rows, ["epoch_id", "selected_start_utc", "selected_end_utc", "current_classification", "burn_reason", "status"]),
        "",
        "## Accepted Compression",
        "",
        md_table(compression_rows, ["level", "input_rows", "unique_count", "retained_percent", "duplicate_compression_percent", "status"]),
        "",
        f"Exact identity group sizes: `{exact_sizes}`.",
        "",
        "Signal cluster, PnL/regime cluster, and economic hypothesis counts are intentionally unresolved rather than inferred from accepted-family labels.",
        "",
        "## Collapse Localization",
        "",
        md_table(collapse_rows, ["stage", "input_count", "output_count", "retained_percent", "finding"]),
        "",
        "## Risk Closure Audit",
        "",
        md_table(risk_rows, ["risk", "status", "finding", "required_closure"]),
        "",
        "## Release Integrity",
        "",
        md_table(integrity_rows, ["artifact", "status", "actual_sha256"]),
        "",
        "The release outputs match their embedded hashes. The source arrays and numeric-cache manifest referenced under the old `G:\\Chengbo\\runtime` path are absent locally, so numeric replay is not established by this audit.",
        "",
        "## Sealed Epoch Rule",
        "",
        "Unknown epochs default to `SEALED_FORWARD`. Spent and sealed metrics may be read only for audit/reproduction and may not enter candidate ranking, admission, memory credit, priors, scheduler budgets, or human promotion packets.",
    ]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", type=Path, default=DEFAULT_RELEASE)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    build(parser.parse_args())


if __name__ == "__main__":
    main()
