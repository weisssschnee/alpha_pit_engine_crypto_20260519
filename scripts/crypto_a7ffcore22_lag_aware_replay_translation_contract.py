from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore22_lag_aware_replay_translation_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE22_LAG_AWARE_REPLAY_TRANSLATION_CONTRACT_20260601.md"
CORE21R = REPO / "runtime" / "a7ffcore21r_translation_matrix_forensic" / "a7ffcore21r_manifest.json"


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
    source = read_json(CORE21R)
    if source.get("decision") != "PASS_A7FFCORE21R_TRANSLATION_MATRIX_FORENSIC_COMPLETE_READY_FOR_CORE22":
        raise SystemExit(f"CORE21R is not ready: {source.get('decision')}")
    lag_policy = pd.DataFrame(
        [
            {
                "lag_bucket": "same_bar_diagnostic",
                "allowed": "diagnostic attribution only",
                "promotion_allowed": False,
                "reason": "same-bar behavior may be timing-fragile",
            },
            {
                "lag_bucket": "one_bar_primary",
                "allowed": "primary promotion gate for replay-clean candidates",
                "promotion_allowed": True,
                "reason": "field-native executable timing baseline",
            },
            {
                "lag_bucket": "stale_lag_control",
                "allowed": "negative/control comparison only",
                "promotion_allowed": False,
                "reason": "stale survival alone is not alpha evidence",
            },
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE22E",
                "action": "lag-aware replay translation audit",
                "input": "CORE19E rows + CORE21E lag matrix",
                "authorized": True,
            },
            {
                "stage": "A7FF-CORE23",
                "action": "lane repair or search-readiness contract",
                "input": "CORE22E pass only",
                "authorized": False,
            },
        ]
    )
    blocked = pd.DataFrame(
        [
            {"blocked_task": "large search", "reason": "blocked until one-bar lag and lane breadth are both repaired"},
            {"blocked_task": "formula generation/search", "reason": "blocked: CORE22 authorizes lag-aware translation audit only"},
            {"blocked_task": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )
    lag_policy.to_csv(RUNTIME / "a7ffcore22_lag_policy.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore22_execution_plan.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore22_blocked_tasks.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE22",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE21R",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE22_LAG_AWARE_REPLAY_TRANSLATION_CONTRACT_READY_FOR_CORE22E",
        "dominant_failure": source.get("dominant_failure"),
        "authorizes_core22e": True,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE22E lag-aware replay translation audit",
    }
    write_json(RUNTIME / "a7ffcore22_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE22 LAG-AWARE REPLAY TRANSLATION CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE22 defines lag-aware replay translation only. It does not execute formula generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Lag Policy",
        "",
        md_table(lag_policy),
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
