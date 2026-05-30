from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7pm3_experiment_board"
REPORT = REPO / "reports" / "CRYPTO_A7PM3_CURRENT_EXPERIMENT_BOARD_20260529.md"
A7PM0 = REPO / "runtime" / "a7pm0_source_of_truth_registry" / "a7pm0_manifest.json"
A7PM2 = REPO / "runtime" / "a7pm2_candidate_lifecycle" / "a7pm2_manifest.json"


ALLOWED = {
    "A7FF-R7": "operator-pair repair after A7FF-40 single-family selected evidence; no search",
    "A7FF-24R4": "repaired-queue numeric wave contract after A7FF-24R3 dense materializer preflight; no search",
    "A7PM-0/3 maintenance": "governance registry maintenance",
}

BLOCKED = {
    "A7FF-41 control-strict expansion": "not authorized by A7FF-40; selected control-strict non-L7 evidence remains single-family",
    "A7FF search execution": "numeric wave has clues but still no replay/search authorization",
    "A7AL-2Y generation": "not authorized",
    "A7AL-3 large search": "not authorized",
    "direct OI-price rerun": "superseded weak prior / not authorized",
    "A7AL-2Q": "not authorized by A7AL-2X0",
    "alpha proof": "not authorized",
    "shadow/paper/live": "not authorized",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    pm0 = read_json(A7PM0)
    pm2 = read_json(A7PM2)
    if not pm0.get("authorizes_a7pm3") and not pm2.get("authorizes_a7pm3"):
        raise SystemExit("A7PM source stages do not authorize A7PM-3")

    active = pd.DataFrame(
        [
            {"workstream": "governance", "current_stage": "A7PM-0/1/2/3", "status": "pass", "next": "keep registry as source-of-truth"},
            {"workstream": "a7ff_family_diversification", "current_stage": "A7FF-40", "status": "hold_selected_single_family", "next": "A7FF-R7 operator-pair repair"},
            {"workstream": "a7ff_funding_tail", "current_stage": "A7FF-24R3", "status": "pass_dense_materializer_preflight", "next": "A7FF-24R4 repaired-queue numeric wave contract"},
            {"workstream": "search_execution", "current_stage": "blocked", "status": "not_authorized", "next": "none"},
        ]
    )
    manifest = {
        "stage": "A7PM-3",
        "generated_at": now_utc(),
        "decision": "PASS_A7PM3_CURRENT_EXPERIMENT_BOARD_BUILT",
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "allowed_next_task_count": len(ALLOWED),
        "blocked_task_count": len(BLOCKED),
    }
    write_json(RUNTIME / "a7pm3_allowed_next_tasks.json", ALLOWED)
    write_json(RUNTIME / "a7pm3_blocked_tasks.json", BLOCKED)
    active.to_csv(RUNTIME / "a7pm3_active_workstreams.csv", index=False)
    write_json(
        RUNTIME / "a7pm3_latest_source_of_truth.json",
        {"a7pm0": pm0, "a7pm2": pm2, "head_equals_origin_main": pm0.get("head_equals_origin_main")},
    )
    write_json(RUNTIME / "a7pm3_manifest.json", manifest)
    allowed_df = pd.DataFrame([{"task": k, "reason": v} for k, v in ALLOWED.items()])
    blocked_df = pd.DataFrame([{"task": k, "reason": v} for k, v in BLOCKED.items()])
    lines = [
        "# CRYPTO A7PM-3 CURRENT EXPERIMENT BOARD",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "## Active Workstreams",
        "",
        md_table(active),
        "",
        "## Allowed Next Tasks",
        "",
        md_table(allowed_df),
        "",
        "## Blocked Tasks",
        "",
        md_table(blocked_df),
        "",
        "## Boundary",
        "",
        "```text",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "The next technical work is A7FF-R7 operator-pair repair and A7FF-24R4 repaired-queue numeric wave contract.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
