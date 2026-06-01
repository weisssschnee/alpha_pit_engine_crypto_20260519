from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore41er_book_control_repair_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE41ER_BOOK_CONTROL_REPAIR_FORENSIC_20260602.md"
CORE41E = REPO / "runtime" / "a7ffcore41e_book_control_repair_execution" / "a7ffcore41e_manifest.json"
CANDIDATE_SUMMARY = REPO / "runtime" / "a7ffcore41e_book_control_repair_execution" / "a7ffcore41e_candidate_summary.csv"
FAMILY_SUMMARY = REPO / "runtime" / "a7ffcore41e_book_control_repair_execution" / "a7ffcore41e_family_summary.csv"
SURVIVORS = REPO / "runtime" / "a7ffcore41e_book_control_repair_execution" / "a7ffcore41e_survivors.csv"


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
    source = read_json(CORE41E)
    if source.get("decision") != "HOLD_A7FFCORE41E_BOOK_CONTROL_REPAIR_INSUFFICIENT":
        raise SystemExit(f"CORE41E not in expected HOLD state: {source.get('decision')}")
    candidates = pd.read_csv(CANDIDATE_SUMMARY)
    families = pd.read_csv(FAMILY_SUMMARY)
    survivors = pd.read_csv(SURVIVORS)

    candidates["forensic_class"] = "candidate"
    candidates.loc[candidates["train_median_repaired_control_ratio"].fillna(99).ge(1.0), "forensic_class"] = "train_control_dominated"
    candidates.loc[
        candidates["train_median_repaired_control_ratio"].fillna(99).lt(1.0)
        & candidates["oos_positive_split_count"].fillna(0).lt(2),
        "forensic_class",
    ] = "oos_positive_fail"
    candidates.loc[
        candidates["train_median_repaired_control_ratio"].fillna(99).lt(1.0)
        & candidates["oos_positive_split_count"].fillna(0).ge(2)
        & candidates["oos_control_clean_split_count"].fillna(0).lt(2),
        "forensic_class",
    ] = "oos_control_fail"
    candidates.loc[candidates["repair_survivor"].fillna(False).astype(bool), "forensic_class"] = "partial_survivor"
    if not survivors.empty:
        survivors["survivor_quality"] = "weak_partial_survivor"
        survivors.loc[
            survivors["oos_min_repaired_net_book_return"].fillna(-1).gt(0)
            & survivors["oos_worst_repaired_control_ratio"].fillna(99).lt(1.0),
            "survivor_quality",
        ] = "strict_survivor"
    failure_counts = (
        candidates.groupby(["family_id", "forensic_class"], as_index=False)
        .agg(candidate_count=("candidate_id", "count"))
        .sort_values(["family_id", "candidate_count"], ascending=[True, False])
    )
    authorization = pd.DataFrame(
        [
            {
                "task": "A7FF-CORE42 book-control route arbitration / freeze contract",
                "status": "AUTHORIZED_CONTRACT_ONLY",
                "reason": "CORE41E produced only one weak partial survivor in one family; expansion is not authorized",
            },
            {"task": "F1b survivor expansion", "status": "NOT_AUTHORIZED", "reason": "single weak survivor, OOS tail and control still unstable"},
            {"task": "formula_search", "status": "NOT_AUTHORIZED", "reason": "no multi-family strict book survivor"},
            {"task": "large_search", "status": "NOT_AUTHORIZED", "reason": "no multi-family strict book survivor"},
            {"task": "alpha_proof / shadow / paper / live", "status": "NOT_AUTHORIZED", "reason": "no proof object"},
        ]
    )
    decision = "PASS_A7FFCORE41ER_BOOK_CONTROL_REPAIR_FORENSIC_READY_FOR_CORE42"
    manifest = {
        "stage": "A7FF-CORE41ER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE41E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "dominant_failure": "single_family_weak_partial_survivor_after_control_repair",
        "candidate_count": int(candidates.shape[0]),
        "partial_survivor_count": int(survivors.shape[0]),
        "partial_survivor_family_count": int(survivors["family_id"].nunique()) if not survivors.empty else 0,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core42_contract": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE42 book-control route arbitration / freeze contract",
    }
    candidates.to_csv(RUNTIME / "a7ffcore41er_candidate_forensic_classification.csv", index=False)
    families.to_csv(RUNTIME / "a7ffcore41er_family_summary_snapshot.csv", index=False)
    survivors.to_csv(RUNTIME / "a7ffcore41er_partial_survivor_snapshot.csv", index=False)
    failure_counts.to_csv(RUNTIME / "a7ffcore41er_failure_counts.csv", index=False)
    authorization.to_csv(RUNTIME / "a7ffcore41er_authorization_matrix.csv", index=False)
    write_json(RUNTIME / "a7ffcore41er_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE41ER BOOK CONTROL REPAIR FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE41ER freezes the CORE41E repair result. It does not run generation, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Main Finding",
        "",
        "`single_family_weak_partial_survivor_after_control_repair`",
        "",
        "CORE41E found one partial survivor, but it is a single F1b candidate and remains weak because OOS tail and control instability persist. It is not expansion evidence.",
        "",
        "## Partial Survivor Snapshot",
        "",
        md_table(survivors),
        "",
        "## Failure Counts",
        "",
        md_table(failure_counts),
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
