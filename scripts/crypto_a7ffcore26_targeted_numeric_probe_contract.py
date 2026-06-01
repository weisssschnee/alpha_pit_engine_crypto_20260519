from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore26_targeted_numeric_probe_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE26_TARGETED_NUMERIC_PROBE_CONTRACT_20260601.md"
CORE25E = REPO / "runtime" / "a7ffcore25e_targeted_lane_horizon_generation" / "a7ffcore25e_manifest.json"


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
    source = read_json(CORE25E)
    if source.get("decision") != "PASS_A7FFCORE25E_TARGETED_GENERATION_PREFLIGHT_PACKET_READY_FOR_CORE26_CONTRACT":
        raise SystemExit(f"CORE25E is not ready: {source.get('decision')}")

    probe_policy = pd.DataFrame(
        [
            {"lane": "S0_positioning_price_basis", "numeric_probe_quota": 160, "priority": "primary missing executable lane"},
            {"lane": "S1_liquidity_basis_positioning", "numeric_probe_quota": 160, "priority": "primary one-bar conversion lane"},
            {"lane": "S2_taker_flow_liquidity_oi", "numeric_probe_quota": 80, "priority": "calibration executable lane"},
            {"lane": "S3_cross_family_bridge", "numeric_probe_quota": 80, "priority": "calibration non-L5 bridge lane"},
        ]
    )
    gates = pd.DataFrame(
        [
            {"gate": "eval_failure_count", "threshold": "0"},
            {"gate": "missing_field_count", "threshold": "0 or documented unsupported"},
            {"gate": "one_bar_executable_clean_count", "threshold": ">= 6"},
            {"gate": "one_bar_executable_lane_count", "threshold": ">= 3"},
            {"gate": "non_l5_clean_count", "threshold": ">= 3"},
            {"gate": "same_bar_only_policy", "threshold": "diagnostic only"},
            {"gate": "search_authorization", "threshold": "false"},
        ]
    )
    outputs = pd.DataFrame(
        [
            {"artifact": "a7ffcore26e_numeric_rows.csv", "description": "candidate split/cost/horizon numeric response rows"},
            {"artifact": "a7ffcore26e_candidate_summary.csv", "description": "candidate-level clean/control/lag summary"},
            {"artifact": "a7ffcore26e_lane_summary.csv", "description": "lane-level executable clean supply"},
            {"artifact": "a7ffcore26e_eval_errors.csv", "description": "fail-closed evaluator errors"},
        ]
    )
    probe_policy.to_csv(RUNTIME / "a7ffcore26_probe_policy.csv", index=False)
    gates.to_csv(RUNTIME / "a7ffcore26_gate_policy.csv", index=False)
    outputs.to_csv(RUNTIME / "a7ffcore26_expected_outputs.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE26",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE25E",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE26_TARGETED_NUMERIC_PROBE_CONTRACT_READY_FOR_CORE26E",
        "numeric_probe_quota": 480,
        "authorizes_core26e": True,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE26E targeted numeric probe execution",
    }
    write_json(RUNTIME / "a7ffcore26_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE26 TARGETED NUMERIC PROBE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE26 defines a bounded numeric probe over the CORE25E targeted preflight packet. It does not authorize search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Probe Policy",
        "",
        md_table(probe_policy),
        "",
        "## Gates",
        "",
        md_table(gates),
        "",
        "## Expected Outputs",
        "",
        md_table(outputs),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
