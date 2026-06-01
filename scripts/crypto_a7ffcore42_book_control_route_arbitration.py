from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore42_book_control_route_arbitration"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE42_BOOK_CONTROL_ROUTE_ARBITRATION_20260602.md"
CORE41ER = REPO / "runtime" / "a7ffcore41er_book_control_repair_forensic" / "a7ffcore41er_manifest.json"
PARTIAL_SURVIVOR = REPO / "runtime" / "a7ffcore41er_book_control_repair_forensic" / "a7ffcore41er_partial_survivor_snapshot.csv"
FAILURE_COUNTS = REPO / "runtime" / "a7ffcore41er_book_control_repair_forensic" / "a7ffcore41er_failure_counts.csv"


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
    source = read_json(CORE41ER)
    if source.get("decision") != "PASS_A7FFCORE41ER_BOOK_CONTROL_REPAIR_FORENSIC_READY_FOR_CORE42":
        raise SystemExit(f"CORE41ER not ready for CORE42: {source.get('decision')}")
    survivor = pd.read_csv(PARTIAL_SURVIVOR)
    failures = pd.read_csv(FAILURE_COUNTS)
    route_scorecard = pd.DataFrame(
        [
            {
                "route": "R0_expand_F1b_partial_survivor",
                "status": "REJECT",
                "reason": "only one weak partial survivor; OOS tail and control instability remain",
                "authorizes_next": False,
            },
            {
                "route": "R1_large_search",
                "status": "REJECT",
                "reason": "search would optimize toward control-dominated book responses",
                "authorizes_next": False,
            },
            {
                "route": "R2_same_packet_rerun",
                "status": "REJECT",
                "reason": "CORE40E/41E already consumed the current packet and controls",
                "authorizes_next": False,
            },
            {
                "route": "R3_control_orthogonalization_contract",
                "status": "AUTHORIZE_CONTRACT_ONLY",
                "reason": "next valid work is to redesign controls/orthogonalization before any search",
                "authorizes_next": True,
            },
        ]
    )
    frozen_paths = pd.DataFrame(
        [
            {"path": "CORE33-41 current candidate queue", "status": "FROZEN", "reason": "no multi-family strict survivor"},
            {"path": "F1b partial survivor expansion", "status": "BLOCKED", "reason": "single weak survivor only"},
            {"path": "large search / formula search", "status": "BLOCKED", "reason": "book responses are control-dominated"},
            {"path": "alpha proof / shadow / paper / live", "status": "BLOCKED", "reason": "no proof object"},
        ]
    )
    authorized_next = pd.DataFrame(
        [
            {
                "task": "A7FF-CORE43 control orthogonalization / null-model contract",
                "status": "AUTHORIZED_CONTRACT_ONLY",
                "scope": "define control-orthogonal score residuals, stale dominance decomposition, and sign-arbitrariness rejection before generation",
            }
        ]
    )
    decision = "PASS_A7FFCORE42_ROUTE_ARBITRATION_READY_FOR_CORE43_CONTROL_ORTHOGONALIZATION_CONTRACT"
    manifest = {
        "stage": "A7FF-CORE42",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE41ER",
        "source_decision": source.get("decision"),
        "decision": decision,
        "selected_route": "R3_control_orthogonalization_contract",
        "dominant_failure": source.get("dominant_failure"),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core43_contract": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE43 control orthogonalization / null-model contract",
    }
    survivor.to_csv(RUNTIME / "a7ffcore42_partial_survivor_snapshot.csv", index=False)
    failures.to_csv(RUNTIME / "a7ffcore42_failure_counts_snapshot.csv", index=False)
    route_scorecard.to_csv(RUNTIME / "a7ffcore42_route_scorecard.csv", index=False)
    frozen_paths.to_csv(RUNTIME / "a7ffcore42_frozen_paths.csv", index=False)
    authorized_next.to_csv(RUNTIME / "a7ffcore42_authorized_next.csv", index=False)
    write_json(RUNTIME / "a7ffcore42_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE42 BOOK CONTROL ROUTE ARBITRATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE42 arbitrates the route after CORE41ER found only a single weak partial survivor. It does not run replay, generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Selected Route",
        "",
        "`R3_control_orthogonalization_contract`",
        "",
        "The current queue is frozen. The next valid work is a control/null-model redesign, not expansion of the weak F1b survivor.",
        "",
        "## Route Scorecard",
        "",
        md_table(route_scorecard),
        "",
        "## Partial Survivor Snapshot",
        "",
        md_table(survivor),
        "",
        "## Frozen Paths",
        "",
        md_table(frozen_paths),
        "",
        "## Authorized Next",
        "",
        md_table(authorized_next),
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
