from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore45r_orthogonal_book_replay_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE45R_ORTHOGONAL_BOOK_REPLAY_FORENSIC_20260602.md"
CORE45E = REPO / "runtime" / "a7ffcore45e_orthogonal_book_replay_execution" / "a7ffcore45e_manifest.json"
OBJECTIVE_SUMMARY = REPO / "runtime" / "a7ffcore45e_orthogonal_book_replay_execution" / "a7ffcore45e_objective_summary.csv"
FAMILY_SUMMARY = REPO / "runtime" / "a7ffcore45e_orthogonal_book_replay_execution" / "a7ffcore45e_family_summary.csv"
CANDIDATE_SUMMARY = REPO / "runtime" / "a7ffcore45e_orthogonal_book_replay_execution" / "a7ffcore45e_candidate_summary.csv"


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
    source = read_json(CORE45E)
    if source.get("decision") != "HOLD_A7FFCORE45E_ORTHOGONAL_BOOK_REPLAY_INSUFFICIENT":
        raise SystemExit(f"CORE45E not ready for CORE45R: {source.get('decision')}")
    objective_summary = pd.read_csv(OBJECTIVE_SUMMARY)
    family_summary = pd.read_csv(FAMILY_SUMMARY)
    candidate_summary = pd.read_csv(CANDIDATE_SUMMARY)

    objective_forensic = objective_summary.copy()
    objective_forensic["failure_mode"] = objective_forensic.apply(
        lambda r: "control_dominated"
        if float(r["median_control_ratio"]) >= 1.0
        else ("negative_or_weak_book_return" if float(r["median_net_book_return"]) <= 0 else "mixed"),
        axis=1,
    )
    family_forensic = family_summary.copy()
    family_forensic["failure_mode"] = family_forensic.apply(
        lambda r: "control_dominated_no_survivor"
        if int(r["survivor_count"]) == 0 and float(r["median_control_ratio"]) >= 1.0
        else "mixed",
        axis=1,
    )
    candidate_forensic = candidate_summary.copy()
    candidate_forensic["failure_mode"] = candidate_forensic.apply(
        lambda r: "control_dominated"
        if float(r["median_control_ratio"]) >= 1.0
        else ("train_or_oos_unstable" if str(r.get("book_survivor", "")).lower() != "true" else "survivor"),
        axis=1,
    )
    route_options = pd.DataFrame(
        [
            {
                "route_id": "R0_expand_current_candidates",
                "decision": "REJECT",
                "reason": "CORE45E has zero survivors after full-universe residual control orthogonalization",
            },
            {
                "route_id": "R1_large_search",
                "decision": "REJECT",
                "reason": "book objective remains control dominated; search would amplify control-like structures",
            },
            {
                "route_id": "R2_same_family_rerun",
                "decision": "REJECT",
                "reason": "F1a/F1b/F2a all have zero survivors and median control ratio above one",
            },
            {
                "route_id": "R3_route_arbitration",
                "decision": "SELECT",
                "reason": "freeze current orthogonal book replay failure and choose between label/control redesign or new objective family",
            },
        ]
    )
    dominant_failure = "orthogonal_book_replay_control_dominated_zero_survivors"
    decision = "PASS_A7FFCORE45R_ORTHOGONAL_BOOK_REPLAY_FORENSIC_READY_FOR_CORE46_ROUTE_ARBITRATION"
    manifest = {
        "stage": "A7FF-CORE45R",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE45E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "dominant_failure": dominant_failure,
        "survivor_count": source.get("survivor_count"),
        "survivor_family_count": source.get("survivor_family_count"),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core46_route_arbitration": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE46 orthogonal replay failure route arbitration",
    }
    objective_forensic.to_csv(RUNTIME / "a7ffcore45r_objective_forensic.csv", index=False)
    family_forensic.to_csv(RUNTIME / "a7ffcore45r_family_forensic.csv", index=False)
    candidate_forensic.to_csv(RUNTIME / "a7ffcore45r_candidate_forensic.csv", index=False)
    route_options.to_csv(RUNTIME / "a7ffcore45r_route_options.csv", index=False)
    write_json(RUNTIME / "a7ffcore45r_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE45R ORTHOGONAL BOOK REPLAY FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        f"Dominant failure: `{dominant_failure}`.",
        "",
        "CORE45R is forensic only. It does not authorize formula generation, large search, alpha proof, shadow, paper, live, or promotion.",
        "",
        "## Objective Forensic",
        "",
        md_table(objective_forensic),
        "",
        "## Family Forensic",
        "",
        md_table(family_forensic),
        "",
        "## Route Options",
        "",
        md_table(route_options),
        "",
        "## Candidate Forensic",
        "",
        md_table(candidate_forensic),
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
