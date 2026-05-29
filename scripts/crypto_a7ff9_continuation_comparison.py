from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff9_continuation_comparison"
REPORT = REPO / "reports" / "CRYPTO_A7FF9_CONTINUATION_COMPARISON_20260530.md"

A7FF8 = REPO / "runtime" / "a7ff8_expanded_numeric_probe"
A7FF9 = REPO / "runtime" / "a7ff9_expanded_numeric_probe_continuation"


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
    safe = df.head(max_rows).copy()
    for col in safe.select_dtypes(include=["object"]).columns:
        safe[col] = safe[col].astype(str).str.replace("|", r"\|", regex=False)
    return safe.to_markdown(index=False)


def stage_row(stage: str, manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    blueprints = int(manifest.get("input_blueprint_count", 0) or 0)
    non_l7 = int(manifest.get("non_l7_numeric_clue_rows", 0) or 0)
    rank = int(manifest.get("rank_label_diagnostic_clue_rows", 0) or 0)
    return {
        "stage": stage,
        "decision": manifest.get("decision", ""),
        "input_blueprint_count": blueprints,
        "materialized_activity_ok_count": int(manifest.get("materialized_activity_ok_count", 0) or 0),
        "label_response_rows": int(manifest.get("label_response_rows", 0) or 0),
        "non_l7_numeric_clue_rows": non_l7,
        "rank_label_diagnostic_clue_rows": rank,
        "portfolio_queue_count": int(manifest.get("portfolio_queue_count", 0) or 0),
        "selected_portfolio_queue_count": int(manifest.get("selected_portfolio_queue_count", 0) or 0),
        "non_l7_clues_per_blueprint": round(non_l7 / blueprints, 4) if blueprints else 0.0,
        "rank_clues_per_blueprint": round(rank / blueprints, 4) if blueprints else 0.0,
        "uses_may": bool(manifest.get("uses_may", False)),
        "authorizes_search": bool(manifest.get("authorizes_search", False)),
    }


def family_clues(stage: str, path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["stage", "semantic_pair", "decision_kind", "count"])
    df = pd.read_csv(path)
    clue = df[df["decision"].astype(str).str.contains("CLUE", na=False)].copy()
    if clue.empty:
        return pd.DataFrame(columns=["stage", "semantic_pair", "decision_kind", "count"])
    clue["stage"] = stage
    clue["decision_kind"] = clue["decision"].astype(str).str.replace(r"A7FF[0-9]+_", "", regex=True)
    return clue[["stage", "semantic_pair", "decision_kind", "count"]]


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    summary = pd.DataFrame(
        [
            stage_row("A7FF-8_64", A7FF8 / "a7ff8_manifest.json"),
            stage_row("A7FF-9_96", A7FF9 / "a7ff9_manifest.json"),
        ]
    )
    family = pd.concat(
        [
            family_clues("A7FF-8_64", A7FF8 / "a7ff8_family_decision_summary.csv"),
            family_clues("A7FF-9_96", A7FF9 / "a7ff9_family_decision_summary.csv"),
        ],
        ignore_index=True,
    )

    timeout_note = {
        "attempted_stage": "A7FF-9_128",
        "attempted_blueprints": 128,
        "result": "timeout_no_manifest",
        "timeout_seconds": 1800,
        "action": "reran as 96-blueprint continuation to produce complete auditable artifacts",
    }
    manifest = {
        "stage": "A7FF-9-COMPARISON",
        "generated_at": now_utc(),
        "decision": "PASS_A7FF9_CONTINUATION_COMPARISON_BUILT",
        "compares": ["A7FF-8_64", "A7FF-9_96"],
        "timeout_note": timeout_note,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    summary.to_csv(RUNTIME / "a7ff9_comparison_summary.csv", index=False)
    family.to_csv(RUNTIME / "a7ff9_family_clue_comparison.csv", index=False)
    write_json(RUNTIME / "a7ff9_manifest.json", manifest)

    lines = [
        "# CRYPTO A7FF-9 CONTINUATION COMPARISON",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        "`PASS_A7FF9_CONTINUATION_COMPARISON_BUILT`",
        "",
        "A7FF-9 expands the A7FF-8 numeric probe from 64 to 96 auditable blueprints. A 128-blueprint attempt exceeded the local 30 minute execution window and produced no manifest, so it is recorded as a compute-cost fact rather than evidence.",
        "",
        "## Summary",
        "",
        md_table(summary),
        "",
        "## Family Clue Comparison",
        "",
        md_table(family),
        "",
        "## Timeout Note",
        "",
        "```json",
        json.dumps(timeout_note, indent=2, sort_keys=True),
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "A7FF-9 is numeric-probe continuation only.",
        "It does not execute generation, replay, search, alpha proof, shadow, paper, or live trading.",
        "May is not used in scoring or authorization.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
