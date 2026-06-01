from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore23_executable_horizon_redesign_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE23_EXECUTABLE_HORIZON_REDESIGN_CONTRACT_20260601.md"
CORE22R = REPO / "runtime" / "a7ffcore22r_lag_translation_forensic" / "a7ffcore22r_manifest.json"


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
    source = read_json(CORE22R)
    if source.get("decision") != "PASS_A7FFCORE22R_LAG_TRANSLATION_FORENSIC_COMPLETE_READY_FOR_CORE23":
        raise SystemExit(f"CORE22R is not ready: {source.get('decision')}")
    horizon_policy = pd.DataFrame(
        [
            {
                "axis": "execution_horizon",
                "allowed": "4h/8h/24h holding and lower-turnover replay diagnostics",
                "forbidden": "same-bar promotion or one-hour high-turnover search expansion",
            },
            {
                "axis": "signal_source",
                "allowed": "reuse locked seed packet and replay-clean diagnostic clues as anchors",
                "forbidden": "open grammar FormulaGen or large search",
            },
            {
                "axis": "cost_model",
                "allowed": "cost tier must be tied to turnover bucket and horizon",
                "forbidden": "choosing lowest cost tier as proof",
            },
            {
                "axis": "lane_repair",
                "allowed": "S0/S1/S2/S3 lane-specific lower-turnover diagnostics",
                "forbidden": "single-lane promotion",
            },
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE23E",
                "action": "executable-horizon diagnostic audit",
                "input": "CORE17E locked packet + CORE19E rows where applicable",
                "authorized": True,
            },
            {
                "stage": "A7FF-CORE24",
                "action": "lower-turnover bounded replay contract",
                "input": "CORE23E pass only",
                "authorized": False,
            },
        ]
    )
    blocked = pd.DataFrame(
        [
            {"blocked_task": "large search", "reason": "blocked: one-bar executable supply insufficient and same-bar dominates"},
            {"blocked_task": "formula generation/search", "reason": "blocked: CORE23 authorizes horizon redesign diagnostics only"},
            {"blocked_task": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )
    horizon_policy.to_csv(RUNTIME / "a7ffcore23_horizon_policy.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore23_execution_plan.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore23_blocked_tasks.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE23",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE22R",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE23_EXECUTABLE_HORIZON_REDESIGN_CONTRACT_READY_FOR_CORE23E",
        "dominant_failure": source.get("dominant_failure"),
        "authorizes_core23e": True,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE23E executable-horizon diagnostic audit",
    }
    write_json(RUNTIME / "a7ffcore23_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE23 EXECUTABLE-HORIZON REDESIGN CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE23 redirects the current packet from same-bar-dominated replay toward executable-horizon diagnostics. It does not execute formula generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Horizon Policy",
        "",
        md_table(horizon_policy),
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
