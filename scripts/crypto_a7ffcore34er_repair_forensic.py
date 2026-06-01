from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore34er_repair_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE34ER_REPAIR_FORENSIC_20260602.md"
CORE34E = REPO / "runtime" / "a7ffcore34e_orientation_control_repair_execution" / "a7ffcore34e_manifest.json"
SUMMARY = REPO / "runtime" / "a7ffcore34e_orientation_control_repair_execution" / "a7ffcore34e_candidate_summary.csv"
FAMILY = REPO / "runtime" / "a7ffcore34e_orientation_control_repair_execution" / "a7ffcore34e_family_summary.csv"
SPLIT = REPO / "runtime" / "a7ffcore34e_orientation_control_repair_execution" / "a7ffcore34e_split_summary.csv"


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
    source = read_json(CORE34E)
    if source.get("decision") != "HOLD_A7FFCORE34E_REPAIR_INSUFFICIENT":
        raise SystemExit(f"CORE34E is not in expected HOLD state: {source.get('decision')}")
    summary = pd.read_csv(SUMMARY)
    family = pd.read_csv(FAMILY)
    split = pd.read_csv(SPLIT)

    candidate_diag = summary.copy()
    candidate_diag["failure_mode"] = "mixed"
    candidate_diag.loc[~candidate_diag["train_control_filter_pass"].astype(bool), "failure_mode"] = "train_control_filter_fail"
    candidate_diag.loc[
        candidate_diag["train_control_filter_pass"].astype(bool)
        & candidate_diag["oos_positive_count"].lt(15),
        "failure_mode",
    ] = "orientation_repair_oos_positive_insufficient"
    candidate_diag.loc[
        candidate_diag["train_control_filter_pass"].astype(bool)
        & candidate_diag["oos_control_clean_count"].lt(15),
        "failure_mode",
    ] = "orientation_repair_oos_control_insufficient"
    family_diag = (
        candidate_diag.groupby(["family_id", "failure_mode"], as_index=False)
        .agg(candidate_count=("replay_candidate_id", "count"))
        .sort_values(["family_id", "failure_mode"])
    )
    split_diag = (
        split.groupby(["family_id", "split"], as_index=False)
        .agg(
            median_positive_count=("positive_count", "median"),
            median_control_clean_count=("control_clean_count", "median"),
            median_repaired_net_spread=("median_repaired_net_spread", "median"),
            median_control_ratio=("median_control_ratio", "median"),
        )
        .sort_values(["family_id", "split"])
    )
    arbitration_inputs = pd.DataFrame(
        [
            {
                "evidence": "numeric_probe_response",
                "status": "pass",
                "detail": "CORE30E produced 113 numeric clues across 3 families",
            },
            {
                "evidence": "replay_preflight",
                "status": "pass",
                "detail": "CORE32E selected 21 preflight candidates across 3 families",
            },
            {
                "evidence": "bounded_replay",
                "status": "hold",
                "detail": "CORE33E survivor_count=0",
            },
            {
                "evidence": "orientation_control_repair",
                "status": "hold",
                "detail": "CORE34E survivor_count=0 after train-only sign/control repair",
            },
        ]
    )
    next_policy = pd.DataFrame(
        [
            {
                "next_action": "A7FF-CORE35 search-readiness arbitration",
                "authorized": True,
                "reason": "must decide whether independent-family line can justify further bounded repair or should reset again",
            },
            {
                "next_action": "large_search",
                "authorized": False,
                "reason": "bounded replay and repair produced zero survivors",
            },
            {
                "next_action": "same_queue_rerun",
                "authorized": False,
                "reason": "same train-only orientation/control repair exhausted without survivors",
            },
            {
                "next_action": "alpha_proof_shadow_paper_live",
                "authorized": False,
                "reason": "no replay survivors and no proof object",
            },
        ]
    )
    train_control_fail_count = int((~candidate_diag["train_control_filter_pass"].astype(bool)).sum())
    oos_positive_fail_count = int(
        (
            candidate_diag["train_control_filter_pass"].astype(bool)
            & candidate_diag["oos_positive_count"].lt(15)
        ).sum()
    )
    decision = "PASS_A7FFCORE34ER_REPAIR_FORENSIC_READY_FOR_CORE35_ARBITRATION"
    manifest = {
        "stage": "A7FF-CORE34ER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE34E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "train_control_fail_count": train_control_fail_count,
        "oos_positive_fail_count": oos_positive_fail_count,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core35_arbitration": True,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE35 search-readiness arbitration",
    }
    candidate_diag.to_csv(RUNTIME / "a7ffcore34er_candidate_failure_diagnostic.csv", index=False)
    family_diag.to_csv(RUNTIME / "a7ffcore34er_family_failure_diagnostic.csv", index=False)
    split_diag.to_csv(RUNTIME / "a7ffcore34er_split_failure_map.csv", index=False)
    arbitration_inputs.to_csv(RUNTIME / "a7ffcore34er_arbitration_inputs.csv", index=False)
    next_policy.to_csv(RUNTIME / "a7ffcore34er_next_policy.csv", index=False)
    write_json(RUNTIME / "a7ffcore34er_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE34ER REPAIR FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE34ER freezes the failed train-only orientation/control repair. It does not execute replay, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Summary",
        "",
        f"- train_control_fail_count: `{train_control_fail_count}`",
        f"- oos_positive_fail_count_after_train_filter: `{oos_positive_fail_count}`",
        "",
        "## Family Failure Diagnostic",
        "",
        md_table(family_diag),
        "",
        "## Split Failure Map",
        "",
        md_table(split_diag),
        "",
        "## Arbitration Inputs",
        "",
        md_table(arbitration_inputs),
        "",
        "## Next Policy",
        "",
        md_table(next_policy),
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
