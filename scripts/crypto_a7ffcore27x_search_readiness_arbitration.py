from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore27x_search_readiness_arbitration"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE27X_SEARCH_READINESS_ARBITRATION_20260602.md"
CORE26DER = REPO / "runtime" / "a7ffcore26der_non_s0_repair_forensic" / "a7ffcore26der_manifest.json"
CORE26CER = REPO / "runtime" / "a7ffcore26cer_split_repair_forensic" / "a7ffcore26cer_manifest.json"


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
    source = read_json(CORE26DER)
    s0_source = read_json(CORE26CER)
    if source.get("decision") != "PASS_A7FFCORE26DER_NON_S0_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE27X":
        raise SystemExit(f"CORE26DER is not ready: {source.get('decision')}")
    verdict = pd.DataFrame(
        [
            {
                "axis": "S0 local clue",
                "evidence": f"{s0_source.get('three_split_clean_count', 0)} clean candidates / {s0_source.get('three_split_clean_lane_count', 0)} lane",
                "verdict": "diagnostic clue only; cannot support replay/search alone",
            },
            {
                "axis": "non-S0 independent lane",
                "evidence": f"{source.get('non_s0_three_split_clean_count', 0)} clean, {source.get('non_s0_two_split_near_miss_count', 0)} near-miss",
                "verdict": "no strict independent lane",
            },
            {
                "axis": "bounded replay readiness",
                "evidence": "requires multi-lane strict clean supply",
                "verdict": "not ready",
            },
            {
                "axis": "large search readiness",
                "evidence": "single-lane S0 clue and non-S0 repair failure",
                "verdict": "not authorized",
            },
        ]
    )
    allowed = pd.DataFrame(
        [
            {
                "task": "A7FF-CORE28 objective/data-family reset contract",
                "reason": "current S0/S1/S3 field set cannot produce independent executable lane breadth",
                "authorized": True,
            },
            {
                "task": "A7FF-CORE27 bounded replay contract",
                "reason": "blocked until multi-lane strict clean supply exists",
                "authorized": False,
            },
            {
                "task": "large search / formula search",
                "reason": "blocked; would amplify a single-lane clue",
                "authorized": False,
            },
        ]
    )
    verdict.to_csv(RUNTIME / "a7ffcore27x_readiness_verdict.csv", index=False)
    allowed.to_csv(RUNTIME / "a7ffcore27x_authorization_matrix.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE27X",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE26DER",
        "source_decision": source.get("decision"),
        "decision": "HOLD_A7FFCORE27X_SEARCH_NOT_READY_SINGLE_LANE_SUPPLY",
        "dominant_failure": "single_lane_s0_clue_without_independent_executable_lane",
        "s0_clean_count": s0_source.get("three_split_clean_count", 0),
        "s0_clean_lane_count": s0_source.get("three_split_clean_lane_count", 0),
        "non_s0_clean_count": source.get("non_s0_three_split_clean_count", 0),
        "non_s0_near_miss_count": source.get("non_s0_two_split_near_miss_count", 0),
        "authorizes_core28_contract": True,
        "authorizes_core27_replay_contract": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE28 objective/data-family reset contract",
    }
    write_json(RUNTIME / "a7ffcore27x_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE27X SEARCH READINESS ARBITRATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE27X arbitrates whether the current A7FF chain is ready for bounded replay or larger search. It is not ready: clean evidence is single-lane S0 only, and non-S0 repair produced no strict clean candidates.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Readiness Verdict",
        "",
        md_table(verdict),
        "",
        "## Authorization Matrix",
        "",
        md_table(allowed),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
