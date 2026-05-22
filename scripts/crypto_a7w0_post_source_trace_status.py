from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "runtime" / "a7w0_post_source_trace_status"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7W0_POST_SOURCE_TRACE_STATUS_20260522.md"

AUTH_FILES = {
    "A7U-0R": ROOT / "runtime" / "a7u0r_source_trace_audit" / "a7u0r_authorization_matrix.json",
    "A7V-5": ROOT / "runtime" / "a7v5_small_replay_smoke" / "a7v5_authorization_matrix.json",
    "A7V-6": ROOT / "runtime" / "a7v6_candidate_control_dominance_forensic" / "a7v6_authorization_matrix.json",
    "A7V-7": ROOT / "runtime" / "a7v7_failure_attribution" / "a7v7_authorization_matrix.json",
}


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def load_auth() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for stage, path in AUTH_FILES.items():
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "stage": stage,
                "decision": payload.get("decision", ""),
                "blockers": ";".join(payload.get("blockers", [])),
                "executes_search": payload.get("executes_search", False),
                "executes_replay": payload.get("executes_replay", False),
                "authorizes_alpha_proof": payload.get("authorizes_alpha_proof", False),
                "authorizes_full_search": payload.get("authorizes_full_search", False),
                "authorizes_expanded_replay": payload.get("authorizes_expanded_replay", False),
                "authorizes_shadow_paper_live": payload.get("authorizes_shadow_paper_live", False),
            }
        )
    return pd.DataFrame(rows)


def write_report(now: str, stage_status: pd.DataFrame, authorization: dict[str, Any]) -> None:
    lines = [
        "# Crypto A7W-0 Post Source-Trace Status",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Purpose",
        "",
        "A7W-0 separates the data-line result from the alpha-line result after A7U-0R was repaired.",
        "",
        "Data status: the enhanced aggTrades panel source trace is complete. The previous `source_trace_incomplete` caveat is removed.",
        "",
        "Signal status: A7V smoke positives still fail May stress and control dominance checks. A7U-0R PASS does not revive A7V candidates.",
        "",
        "## Stage Status",
        "",
        table(stage_status, max_rows=20),
        "",
        "## Current Boundary",
        "",
        "- The unified panel can be used for controlled experiments without the prior source-trace caveat.",
        "- A7V-5 remains method-only smoke.",
        "- A7V-6 and A7V-7 block expanded replay from the current activity/liquidity clue family.",
        "- No alpha proof, shadow, paper, live, or production claim is authorized.",
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- Do not expand the current A7V activity/liquidity clue family.",
        "- If continuing aggTrades research, start from objective/horizon/family redesign, not from A7V-5 positive labels.",
        "- Any new panel refresh must rerun A7U-0R before source-trace claims.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    status = load_auth()
    a7u_pass = status[status["stage"].eq("A7U-0R")]["decision"].astype(str).str.startswith("PASS").all()
    a7v_holds = status[status["stage"].isin(["A7V-6", "A7V-7"])]["decision"].astype(str).str.startswith("HOLD").all()
    blockers: list[str] = []
    if not a7u_pass:
        blockers.append("source_trace_not_complete")
    if a7v_holds:
        blockers.append("a7v_signal_family_blocked")
    decision = "PASS_A7W0_SOURCE_TRACE_RESOLVED_SIGNAL_LINE_STILL_HOLD" if a7u_pass else "HOLD_A7W0_SOURCE_TRACE_UNRESOLVED"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "source_trace_incomplete_caveat_removed": bool(a7u_pass),
        "current_a7v_activity_liquidity_family_promotable": False,
        "authorizes_controlled_experiments_without_source_trace_caveat": bool(a7u_pass),
        "authorizes_expanded_replay": False,
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": [
            "Do not expand current A7V activity/liquidity clue family",
            "Use A7U-0R PASS only as data provenance closure, not alpha evidence",
            "If continuing, define a new aggTrades objective/horizon/family redesign stage",
        ],
    }
    status.to_csv(OUT_DIR / "a7w0_stage_status.csv", index=False)
    write_json(OUT_DIR / "a7w0_authorization_matrix.json", authorization)
    write_json(OUT_DIR / "a7w0_manifest.json", {"generated_at": now, "decision": decision, "output_dir": str(OUT_DIR), "report": str(REPORT_PATH)})
    write_report(now, status, authorization)
    print(json.dumps({"decision": decision, "blockers": blockers, "source_trace_caveat_removed": bool(a7u_pass)}, indent=2))


if __name__ == "__main__":
    main()
