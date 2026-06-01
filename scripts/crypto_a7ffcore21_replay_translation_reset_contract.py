from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore21_replay_translation_reset_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE21_REPLAY_TRANSLATION_RESET_CONTRACT_20260601.md"
CORE19SER = REPO / "runtime" / "a7ffcore19ser_replay_repair_forensic" / "a7ffcore19ser_manifest.json"


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
    source = read_json(CORE19SER)
    if source.get("decision") != "PASS_A7FFCORE19SER_REPLAY_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE21":
        raise SystemExit(f"CORE19SER is not ready: {source.get('decision')}")
    reset_policy = pd.DataFrame(
        [
            {
                "axis": "label_translation",
                "allowed": "evaluate raw, cross-sectional, liquidity-tier, vol-adjusted, and ranked labels as separate objectives",
                "forbidden": "using ranked/L5-only evidence as search-ready proof",
            },
            {
                "axis": "cost_model",
                "allowed": "report 2/5/10/20bps tiers separately and define low-turnover lane gates",
                "forbidden": "selecting by the easiest cost tier without diagnostic labeling",
            },
            {
                "axis": "lag_model",
                "allowed": "separate same-bar, one-bar, stale-lag, and label horizon effects",
                "forbidden": "promoting same-bar-only behavior",
            },
            {
                "axis": "lane_breadth",
                "allowed": "treat S2/S3 clean clues as diagnostic anchors and require S0/S1 translation repair",
                "forbidden": "single-lane replay-clean promotion",
            },
            {
                "axis": "candidate_source",
                "allowed": "reuse locked packet and CORE19E rows for attribution; no new formula generation",
                "forbidden": "open grammar expansion or large search",
            },
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE21E",
                "action": "label/cost/lag/lane translation matrix audit",
                "input": "CORE19E replay rows + CORE17E locked packet",
                "authorized": True,
            },
            {
                "stage": "A7FF-CORE22",
                "action": "bounded replay objective repair contract",
                "input": "CORE21E pass only",
                "authorized": False,
            },
        ]
    )
    blocked = pd.DataFrame(
        [
            {"blocked_task": "CORE20", "reason": "superseded by CORE19SER hold; replay-clean supply insufficient"},
            {"blocked_task": "large search", "reason": "blocked until replay translation reset produces robust multi-lane clean evidence"},
            {"blocked_task": "formula generation/search", "reason": "blocked: CORE21 is translation reset only"},
            {"blocked_task": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )
    reset_policy.to_csv(RUNTIME / "a7ffcore21_reset_policy.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore21_execution_plan.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore21_blocked_tasks.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE21",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE19SER",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE21_REPLAY_TRANSLATION_RESET_CONTRACT_READY_FOR_CORE21E",
        "source_best_clean_candidate_count": int(source.get("best_clean_candidate_count", 0)),
        "source_best_clean_seed_lane_count": int(source.get("best_clean_seed_lane_count", 0)),
        "authorizes_core21e": True,
        "authorizes_core20": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE21E replay translation matrix audit",
    }
    write_json(RUNTIME / "a7ffcore21_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE21 REPLAY TRANSLATION RESET CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE21 resets replay translation objectives after bounded replay supply failure. It does not execute formula generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Reset Policy",
        "",
        md_table(reset_policy),
        "",
        "## Execution Plan",
        "",
        md_table(execution_plan),
        "",
        "## Blocked",
        "",
        md_table(blocked),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
