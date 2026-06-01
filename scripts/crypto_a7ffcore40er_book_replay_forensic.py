from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore40er_book_replay_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE40ER_BOOK_REPLAY_FORENSIC_20260602.md"
CORE40E = REPO / "runtime" / "a7ffcore40e_book_objective_replay_execution" / "a7ffcore40e_manifest.json"
CANDIDATE_SUMMARY = REPO / "runtime" / "a7ffcore40e_book_objective_replay_execution" / "a7ffcore40e_candidate_summary.csv"
OBJECTIVE_SUMMARY = REPO / "runtime" / "a7ffcore40e_book_objective_replay_execution" / "a7ffcore40e_objective_summary.csv"
FAMILY_SUMMARY = REPO / "runtime" / "a7ffcore40e_book_objective_replay_execution" / "a7ffcore40e_family_summary.csv"
REPLAY = REPO / "runtime" / "a7ffcore40e_book_objective_replay_execution" / "a7ffcore40e_book_replay_original_vs_controls.csv"


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
    source = read_json(CORE40E)
    if source.get("decision") != "HOLD_A7FFCORE40E_BOOK_OBJECTIVE_REPLAY_INSUFFICIENT":
        raise SystemExit(f"CORE40E not in expected HOLD state: {source.get('decision')}")

    candidates = pd.read_csv(CANDIDATE_SUMMARY)
    objectives = pd.read_csv(OBJECTIVE_SUMMARY)
    families = pd.read_csv(FAMILY_SUMMARY)
    replay = pd.read_csv(REPLAY)

    candidates["failure_reason"] = "candidate"
    candidates.loc[candidates["train_median_net_book_return"].fillna(-1).le(0), "failure_reason"] = "train_book_net_nonpositive"
    candidates.loc[
        candidates["train_median_net_book_return"].fillna(-1).gt(0)
        & candidates["train_median_control_ratio"].fillna(99).ge(1.0),
        "failure_reason",
    ] = "train_control_dominated"
    candidates.loc[
        candidates["train_median_net_book_return"].fillna(-1).gt(0)
        & candidates["train_median_control_ratio"].fillna(99).lt(1.0)
        & candidates["oos_positive_split_count"].fillna(0).lt(2),
        "failure_reason",
    ] = "oos_positive_split_fail"
    candidates.loc[
        candidates["train_median_net_book_return"].fillna(-1).gt(0)
        & candidates["train_median_control_ratio"].fillna(99).lt(1.0)
        & candidates["oos_positive_split_count"].fillna(0).ge(2)
        & candidates["oos_control_clean_split_count"].fillna(0).lt(2),
        "failure_reason",
    ] = "oos_control_dominated"
    failure_counts = (
        candidates.groupby(["family_id", "failure_reason"], as_index=False)
        .agg(candidate_count=("candidate_id", "count"))
        .sort_values(["family_id", "candidate_count"], ascending=[True, False])
    )
    objective_forensic = objectives.copy()
    objective_forensic["diagnosis"] = "control_dominated" 
    objective_forensic.loc[
        objective_forensic["median_net_book_return"].le(0),
        "diagnosis",
    ] = "net_nonpositive"
    objective_forensic.loc[
        objective_forensic["median_net_book_return"].gt(0) & objective_forensic["median_control_ratio"].lt(1.0),
        "diagnosis",
    ] = "potentially_clean"
    split_objective = (
        replay.groupby(["objective_id", "split"], as_index=False)
        .agg(
            replay_rows=("candidate_id", "count"),
            positive_rows=("positive_net", "sum"),
            control_clean_rows=("control_clean", "sum"),
            median_net_book_return=("net_book_return", "median"),
            median_control_ratio=("control_ratio", "median"),
        )
        .sort_values(["objective_id", "split"])
    )
    authorization = pd.DataFrame(
        [
            {
                "task": "A7FF-CORE41 book-objective control repair contract",
                "status": "AUTHORIZED_CONTRACT_ONLY",
                "reason": "book objectives show positive medians but are dominated by stale/sign-flip controls",
            },
            {
                "task": "book objective survivor promotion",
                "status": "NOT_AUTHORIZED",
                "reason": "survivor_count=0",
            },
            {"task": "formula_search", "status": "NOT_AUTHORIZED", "reason": "book response is control-dominated"},
            {"task": "large_search", "status": "NOT_AUTHORIZED", "reason": "book response is control-dominated"},
            {"task": "alpha_proof / shadow / paper / live", "status": "NOT_AUTHORIZED", "reason": "no proof object"},
        ]
    )
    decision = "PASS_A7FFCORE40ER_BOOK_REPLAY_FORENSIC_READY_FOR_CORE41_CONTRACT"
    manifest = {
        "stage": "A7FF-CORE40ER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE40E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "dominant_failure": "book_objective_control_dominated",
        "candidate_count": int(candidates.shape[0]),
        "book_survivor_count": int(candidates["book_survivor"].fillna(False).astype(bool).sum()),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core41_contract": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE41 book-objective control repair contract",
    }
    candidates.to_csv(RUNTIME / "a7ffcore40er_candidate_failure_classification.csv", index=False)
    failure_counts.to_csv(RUNTIME / "a7ffcore40er_failure_counts.csv", index=False)
    objectives.to_csv(RUNTIME / "a7ffcore40er_objective_summary_snapshot.csv", index=False)
    objective_forensic.to_csv(RUNTIME / "a7ffcore40er_objective_forensic.csv", index=False)
    families.to_csv(RUNTIME / "a7ffcore40er_family_summary_snapshot.csv", index=False)
    split_objective.to_csv(RUNTIME / "a7ffcore40er_split_objective_forensic.csv", index=False)
    authorization.to_csv(RUNTIME / "a7ffcore40er_authorization_matrix.csv", index=False)
    write_json(RUNTIME / "a7ffcore40er_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE40ER BOOK REPLAY FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE40ER freezes the CORE40E book replay failure. It does not run replay, generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Main Finding",
        "",
        "`book_objective_control_dominated`",
        "",
        "The symbol-level book packet makes the objective computable, and several objective medians are positive. The blocker is that stale/sign-flip controls remain as strong or stronger than the original book response.",
        "",
        "## Objective Forensic",
        "",
        md_table(objective_forensic),
        "",
        "## Failure Counts",
        "",
        md_table(failure_counts),
        "",
        "## Split Objective Forensic",
        "",
        md_table(split_objective),
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
