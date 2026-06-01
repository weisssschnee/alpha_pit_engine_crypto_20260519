from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore26der_non_s0_repair_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE26DER_NON_S0_REPAIR_FORENSIC_20260602.md"
CORE26DE = REPO / "runtime" / "a7ffcore26de_non_s0_lane_repair_probe" / "a7ffcore26de_manifest.json"
LANE = REPO / "runtime" / "a7ffcore26de_non_s0_lane_repair_probe" / "a7ffcore26de_lane_summary.csv"
NEAR = REPO / "runtime" / "a7ffcore26de_non_s0_lane_repair_probe" / "a7ffcore26de_near_miss_candidates.csv"


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
    source = read_json(CORE26DE)
    if source.get("decision") != "HOLD_A7FFCORE26DE_NON_S0_REPAIR_INSUFFICIENT":
        raise SystemExit(f"CORE26DE is not in expected HOLD state: {source.get('decision')}")
    lane = pd.read_csv(LANE) if LANE.exists() else pd.DataFrame()
    near = pd.read_csv(NEAR) if NEAR.exists() else pd.DataFrame()
    s1_near = int(near["seed_lane"].astype(str).eq("S1_liquidity_basis_positioning").sum()) if not near.empty else 0
    s3_near = int(near["seed_lane"].astype(str).eq("S3_cross_family_bridge").sum()) if not near.empty else 0
    diagnosis = pd.DataFrame(
        [
            {"finding": "non_s0_three_split_clean_count", "value": source.get("three_split_clean_count", 0), "interpretation": "strict non-S0 executable clean supply"},
            {"finding": "non_s0_two_split_near_miss_count", "value": source.get("two_split_near_miss_count", 0), "interpretation": "partial non-S0 supply"},
            {"finding": "s1_near_miss_count", "value": s1_near, "interpretation": "S1 has partial but unstable response"},
            {"finding": "s3_near_miss_count", "value": s3_near, "interpretation": "S3 remains weaker than S1 after repair"},
            {"finding": "dominant_failure", "value": "non_s0_lane_repair_no_strict_clean", "interpretation": "cannot create independent second executable lane from current field set"},
        ]
    )
    recommended = pd.DataFrame(
        [
            {
                "next_stage": "A7FF-CORE27X",
                "action": "search readiness arbitration / objective reset",
                "rationale": "S0 local clue exists, but independent lane cannot be repaired from current S1/S3 targeted probes",
                "authorized": True,
            },
            {
                "next_stage": "A7FF-CORE27 bounded replay contract",
                "action": "blocked",
                "rationale": "non-S0 repair has zero three-split clean candidates",
                "authorized": False,
            },
            {
                "next_stage": "large search",
                "action": "blocked",
                "rationale": "search would expand a single-lane S0 clue without independent lane support",
                "authorized": False,
            },
        ]
    )
    diagnosis.to_csv(RUNTIME / "a7ffcore26der_diagnosis.csv", index=False)
    recommended.to_csv(RUNTIME / "a7ffcore26der_recommended_actions.csv", index=False)
    near.to_csv(RUNTIME / "a7ffcore26der_near_miss_snapshot.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE26DER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE26DE",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE26DER_NON_S0_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE27X",
        "dominant_failure": "non_s0_lane_repair_no_strict_clean",
        "non_s0_three_split_clean_count": source.get("three_split_clean_count", 0),
        "non_s0_two_split_near_miss_count": source.get("two_split_near_miss_count", 0),
        "s1_near_miss_count": s1_near,
        "s3_near_miss_count": s3_near,
        "authorizes_core27x_contract": True,
        "authorizes_core27_replay_contract": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE27X search-readiness arbitration / objective reset contract",
    }
    write_json(RUNTIME / "a7ffcore26der_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE26DER NON-S0 REPAIR FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE26DER freezes the non-S0 lane repair failure. It does not authorize replay, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Diagnosis",
        "",
        md_table(diagnosis),
        "",
        "## Lane Summary From CORE26DE",
        "",
        md_table(lane),
        "",
        "## Recommended Actions",
        "",
        md_table(recommended),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
