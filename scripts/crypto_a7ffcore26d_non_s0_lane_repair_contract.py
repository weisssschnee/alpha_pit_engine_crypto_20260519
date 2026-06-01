from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore26d_non_s0_lane_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE26D_NON_S0_LANE_REPAIR_CONTRACT_20260602.md"
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
    source = read_json(CORE26CER)
    if source.get("decision") != "PASS_A7FFCORE26CER_SPLIT_REPAIR_FORENSIC_COMPLETE_READY_FOR_CORE26D":
        raise SystemExit(f"CORE26CER is not ready: {source.get('decision')}")

    lane_policy = pd.DataFrame(
        [
            {
                "lane": "S3_cross_family_bridge",
                "status": "primary_non_s0_repair",
                "allowed": "basis/OI/liquidity bridge variants around existing S3 near-miss; H8/H24; one-bar executable only",
                "blocked": "S0 fields, S3-only promotion, same-bar-only candidates",
            },
            {
                "lane": "S1_liquidity_basis_positioning",
                "status": "secondary_repair",
                "allowed": "liquidity x basis/positioning variants with stricter control filtering",
                "blocked": "basis-only/funding-only wrappers and H1 variants",
            },
            {
                "lane": "S0_positioning_price_basis",
                "status": "calibration_only",
                "allowed": "retain existing 4 clean candidates as reference",
                "blocked": "further S0 expansion in CORE26D",
            },
        ]
    )
    gates = pd.DataFrame(
        [
            {"gate": "non_s0_three_split_clean_count", "threshold": ">= 2"},
            {"gate": "total_three_split_clean_lane_count", "threshold": ">= 2 including S0 reference"},
            {"gate": "control_ratio_policy", "threshold": "< 1.0 all pre-May splits"},
            {"gate": "search_authorization", "threshold": "false"},
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE26DE",
                "action": "non-S0 lane repair numeric probe",
                "input": "S3 near-miss + S1 secondary repair policy + S0 reference",
                "authorized": True,
            },
            {
                "stage": "A7FF-CORE27",
                "action": "bounded replay contract",
                "input": "CORE26DE pass only",
                "authorized": False,
            },
        ]
    )
    lane_policy.to_csv(RUNTIME / "a7ffcore26d_lane_policy.csv", index=False)
    gates.to_csv(RUNTIME / "a7ffcore26d_gate_policy.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore26d_execution_plan.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE26D",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE26CER",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE26D_NON_S0_LANE_REPAIR_CONTRACT_READY_FOR_CORE26DE",
        "dominant_failure": source.get("dominant_failure"),
        "authorizes_core26de": True,
        "authorizes_formula_generation": False,
        "authorizes_open_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE26DE non-S0 lane repair numeric probe",
    }
    write_json(RUNTIME / "a7ffcore26d_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE26D NON-S0 LANE REPAIR CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE26D authorizes only a bounded non-S0 lane repair numeric probe. S0 clean candidates are calibration-only. No search, large search, alpha proof, shadow, paper, or live is authorized.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Lane Policy",
        "",
        md_table(lane_policy),
        "",
        "## Gates",
        "",
        md_table(gates),
        "",
        "## Execution Plan",
        "",
        md_table(execution_plan),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
