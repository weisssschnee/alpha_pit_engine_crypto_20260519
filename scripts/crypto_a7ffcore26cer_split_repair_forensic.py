from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore26cer_split_repair_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE26CER_SPLIT_REPAIR_FORENSIC_20260602.md"
CORE26CE = REPO / "runtime" / "a7ffcore26ce_split_consistency_repair_probe" / "a7ffcore26ce_manifest.json"
CLEAN = REPO / "runtime" / "a7ffcore26ce_split_consistency_repair_probe" / "a7ffcore26ce_clean_candidates.csv"
NEAR = REPO / "runtime" / "a7ffcore26ce_split_consistency_repair_probe" / "a7ffcore26ce_near_miss_candidates.csv"
LANE = REPO / "runtime" / "a7ffcore26ce_split_consistency_repair_probe" / "a7ffcore26ce_lane_summary.csv"


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
    source = read_json(CORE26CE)
    if source.get("decision") != "HOLD_A7FFCORE26CE_SPLIT_REPAIR_INSUFFICIENT":
        raise SystemExit(f"CORE26CE is not in expected HOLD state: {source.get('decision')}")
    clean = pd.read_csv(CLEAN) if CLEAN.exists() else pd.DataFrame()
    near = pd.read_csv(NEAR) if NEAR.exists() else pd.DataFrame()
    lane = pd.read_csv(LANE) if LANE.exists() else pd.DataFrame()

    clean_lane_count = int(clean["seed_lane"].nunique()) if not clean.empty else 0
    clean_count = int(clean["blueprint_id"].nunique()) if not clean.empty else 0
    s0_clean = int(clean["seed_lane"].astype(str).eq("S0_positioning_price_basis").sum()) if not clean.empty else 0
    s3_clean = int(clean["seed_lane"].astype(str).eq("S3_cross_family_bridge").sum()) if not clean.empty else 0
    s3_near = int(near["seed_lane"].astype(str).eq("S3_cross_family_bridge").sum()) if not near.empty else 0
    dominant_failure = "single_lane_clean_supply_after_split_repair"

    diagnosis = pd.DataFrame(
        [
            {"finding": "clean_count", "value": clean_count, "interpretation": "strict three-split clean candidates after repair"},
            {"finding": "clean_lane_count", "value": clean_lane_count, "interpretation": "strict clean lane breadth"},
            {"finding": "s0_clean_count", "value": s0_clean, "interpretation": "S0 is the only productive clean lane"},
            {"finding": "s3_clean_count", "value": s3_clean, "interpretation": "S3 repair did not reach strict clean"},
            {"finding": "s3_near_miss_count", "value": s3_near, "interpretation": "S3 still has near-miss structure worth isolated repair"},
            {"finding": "dominant_failure", "value": dominant_failure, "interpretation": "cannot advance to replay with one clean lane only"},
        ]
    )
    recommended = pd.DataFrame(
        [
            {
                "next_stage": "A7FF-CORE26D",
                "action": "non-S0 lane independence repair contract",
                "rationale": "S0 has local clean evidence, but replay/search requires at least one additional independent executable lane",
                "authorized": True,
            },
            {
                "next_stage": "A7FF-CORE27 bounded replay contract",
                "action": "blocked",
                "rationale": "clean supply remains 4 candidates / 1 lane",
                "authorized": False,
            },
        ]
    )
    diagnosis.to_csv(RUNTIME / "a7ffcore26cer_diagnosis.csv", index=False)
    recommended.to_csv(RUNTIME / "a7ffcore26cer_recommended_actions.csv", index=False)
    clean.to_csv(RUNTIME / "a7ffcore26cer_clean_candidates_snapshot.csv", index=False)
    near.to_csv(RUNTIME / "a7ffcore26cer_near_miss_snapshot.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE26CER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE26CE",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE26CER_SPLIT_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE26D",
        "dominant_failure": dominant_failure,
        "three_split_clean_count": clean_count,
        "three_split_clean_lane_count": clean_lane_count,
        "s0_clean_count": s0_clean,
        "s3_clean_count": s3_clean,
        "s3_near_miss_count": s3_near,
        "authorizes_core26d_contract": True,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE26D non-S0 lane independence repair contract",
    }
    write_json(RUNTIME / "a7ffcore26cer_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE26CER SPLIT REPAIR FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE26CER freezes the CORE26CE hold. It does not authorize replay, search, large search, alpha proof, shadow, paper, or live.",
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
        "## Lane Summary From CORE26CE",
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
