from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16kr_h2_repair_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16KR_H2_REPAIR_FORENSIC_20260601.md"
CORE16KE = REPO / "runtime" / "a7ffcore16ke_h2_strict_floor_execution" / "a7ffcore16ke_manifest.json"
KE_RESPONSE = REPO / "runtime" / "a7ffcore16ke_h2_strict_floor_execution" / "a7ffcore16ke_h2_repair_response_map.csv"
KE_CANDIDATES = REPO / "runtime" / "a7ffcore16ke_h2_strict_floor_execution" / "a7ffcore16ke_h2_repair_candidates.csv"
KE_ADDED = REPO / "runtime" / "a7ffcore16ke_h2_strict_floor_execution" / "a7ffcore16ke_h2_added_strict_rows.csv"
KE_QUEUE = REPO / "runtime" / "a7ffcore16ke_h2_strict_floor_execution" / "a7ffcore16ke_repaired_strict_preseed_queue.csv"
KE_DECISIONS = REPO / "runtime" / "a7ffcore16ke_h2_strict_floor_execution" / "a7ffcore16ke_decision_counts.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


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
    ke = read_json(CORE16KE)
    if ke.get("decision") != "HOLD_A7FFCORE16KE_H2_STRICT_FLOOR_REPAIR_INSUFFICIENT":
        raise SystemExit(f"CORE16KE is not in forensic state: {ke.get('decision')}")

    response = load_csv(KE_RESPONSE)
    candidates = load_csv(KE_CANDIDATES)
    added = load_csv(KE_ADDED)
    queue = load_csv(KE_QUEUE)
    decisions = load_csv(KE_DECISIONS)

    candidate_summary = (
        candidates.groupby(["left_transform", "operator", "right_transform"], dropna=False)
        .agg(
            candidate_rows=("blueprint_id", "size"),
            label_family_count=("label_family", "nunique"),
            min_control_ratio=("control_ratio_premay_max", "min"),
            lag_ok_count=("lag_ok", lambda s: int(s.astype(str).str.lower().eq("true").sum())),
        )
        .reset_index()
        .sort_values(["candidate_rows", "min_control_ratio"], ascending=[False, True])
        if not candidates.empty
        else pd.DataFrame()
    )
    near_summary = (
        response[response["near_miss"].astype(str).str.lower().eq("true")]
        .groupby(["left_transform", "operator", "right_transform"], dropna=False)
        .agg(
            near_miss_rows=("blueprint_id", "size"),
            min_control_ratio=("control_ratio_premay_max", "min"),
            label_family_count=("label_family", "nunique"),
        )
        .reset_index()
        .sort_values(["near_miss_rows", "min_control_ratio"], ascending=[False, True])
        if not response.empty and "near_miss" in response.columns
        else pd.DataFrame()
    )
    queue_summary = (
        queue.groupby(["second_pass_family", "queue_role"], dropna=False)
        .agg(rows=("blueprint_id", "size"), label_family_count=("label_family", "nunique"))
        .reset_index()
        .sort_values("rows", ascending=False)
        if not queue.empty
        else pd.DataFrame()
    )
    candidate_summary.to_csv(RUNTIME / "a7ffcore16kr_candidate_transform_summary.csv", index=False)
    near_summary.to_csv(RUNTIME / "a7ffcore16kr_nearmiss_transform_summary.csv", index=False)
    queue_summary.to_csv(RUNTIME / "a7ffcore16kr_repaired_queue_summary.csv", index=False)

    needed = max(0, 96 - int(ke.get("repaired_queue_size", 0)))
    h2_needed = max(0, 12 - int(ke.get("repaired_queue_h2_count", 0)))
    recommended_actions = pd.DataFrame(
        [
            {
                "action_id": "A0_no_core16l",
                "action": "do not lock the strict pre-seed queue",
                "reason": "CORE16KE repaired queue is still below size and H2 floors",
            },
            {
                "action_id": "A1_core16m_floor_arbitration",
                "action": "write a floor arbitration contract before any further execution",
                "reason": "the gap is one row, but weakening the floor silently would corrupt governance",
            },
            {
                "action_id": "A2_core16me_optional_broader_h2_wave",
                "action": "if strict floor is retained, run a broader H2 wave with additional transforms and checkpointing",
                "reason": "current narrow wave found 2 of 3 required rows and the remaining gap is localized",
            },
        ]
    )
    recommended_actions.to_csv(RUNTIME / "a7ffcore16kr_recommended_actions.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE16KR",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16KE",
        "source_decision": ke.get("decision"),
        "decision": "PASS_A7FFCORE16KR_H2_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE16M",
        "dominant_failure": "strict_h2_floor_short_by_one_after_repair",
        "response_rows": int(ke.get("response_rows", 0)),
        "h2_repair_candidate_count": int(ke.get("h2_repair_candidate_count", 0)),
        "added_strict_h2_count": int(ke.get("added_strict_h2_count", 0)),
        "repaired_queue_size": int(ke.get("repaired_queue_size", 0)),
        "repaired_queue_h2_count": int(ke.get("repaired_queue_h2_count", 0)),
        "queue_rows_needed": needed,
        "h2_rows_needed": h2_needed,
        "authorizes_core16m": True,
        "authorizes_core16l": False,
        "authorizes_core17": False,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE16M H2 floor arbitration contract",
    }
    write_json(RUNTIME / "a7ffcore16kr_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE16KR H2 REPAIR FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE16KR freezes the CORE16KE result. It does not execute replay, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## CORE16KE Decision Counts",
        "",
        md_table(decisions),
        "",
        "## Added Strict H2 Rows",
        "",
        md_table(added),
        "",
        "## Candidate Transform Summary",
        "",
        md_table(candidate_summary),
        "",
        "## Recommended Actions",
        "",
        md_table(recommended_actions),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
