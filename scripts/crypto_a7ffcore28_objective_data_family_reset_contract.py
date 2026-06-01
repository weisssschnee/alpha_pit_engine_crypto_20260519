from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore28_objective_data_family_reset_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE28_OBJECTIVE_DATA_FAMILY_RESET_CONTRACT_20260602.md"
CORE27X = REPO / "runtime" / "a7ffcore27x_search_readiness_arbitration" / "a7ffcore27x_manifest.json"


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
    source = read_json(CORE27X)
    if source.get("decision") != "HOLD_A7FFCORE27X_SEARCH_NOT_READY_SINGLE_LANE_SUPPLY":
        raise SystemExit(f"CORE27X is not in expected HOLD state: {source.get('decision')}")

    reset_policy = pd.DataFrame(
        [
            {
                "family": "F0_positioning_price_basis_s0",
                "status": "diagnostic_reference_only",
                "allowed": "use 4 clean S0 candidates as calibration and anti-overfit control",
                "blocked": "standalone search objective, replay contract, large search seed",
            },
            {
                "family": "F1_independent_flow_microstructure",
                "status": "primary_reset_candidate",
                "allowed": "taker flow, aggTrades flow, liquidity/volume state, low-turnover interactions",
                "blocked": "A7V activity/liquidity self-reproduction patterns",
            },
            {
                "family": "F2_independent_basis_funding",
                "status": "primary_reset_candidate",
                "allowed": "basis/funding dislocation with non-S0 neutralization and H8/H24 executable horizons",
                "blocked": "basis-only or funding-only wrappers",
            },
            {
                "family": "F3_cross_exchange_forward_context",
                "status": "diagnostic_forward_only",
                "allowed": "forward telemetry / state context only",
                "blocked": "historical alpha proof or backfilled proof",
            },
            {
                "family": "F4_new_data_family_contract",
                "status": "contract_required",
                "allowed": "liquidation/orderbook/cross-exchange only after PIT/source contract",
                "blocked": "untraced historical proof",
            },
        ]
    )
    next_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE28E",
                "action": "independent data-family atlas contract/audit",
                "input": "CORE27X arbitration + current field/source registry",
                "authorized": True,
            },
            {
                "stage": "A7FF large search",
                "action": "blocked",
                "input": "requires independent multi-lane executable evidence",
                "authorized": False,
            },
        ]
    )
    gates = pd.DataFrame(
        [
            {"gate": "independent_lane_requirement", "threshold": ">= 2 non-S0 lanes before replay/search"},
            {"gate": "s0_concentration_cap", "threshold": "S0 diagnostic reference only"},
            {"gate": "forward_only_source_policy", "threshold": "cannot enter historical proof"},
            {"gate": "large_search_authorization", "threshold": "false"},
        ]
    )
    reset_policy.to_csv(RUNTIME / "a7ffcore28_reset_policy.csv", index=False)
    next_plan.to_csv(RUNTIME / "a7ffcore28_execution_plan.csv", index=False)
    gates.to_csv(RUNTIME / "a7ffcore28_gate_policy.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE28",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE27X",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE28_OBJECTIVE_DATA_FAMILY_RESET_CONTRACT_READY_FOR_CORE28E",
        "dominant_failure": source.get("dominant_failure"),
        "authorizes_core28e": True,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE28E independent data-family atlas contract/audit",
    }
    write_json(RUNTIME / "a7ffcore28_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE28 OBJECTIVE/DATA-FAMILY RESET CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE28 resets the next search-prep path after CORE27X concluded that current evidence is single-lane S0 only. It does not authorize search, large search, alpha proof, shadow, paper, or live.",
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
        "## Gates",
        "",
        md_table(gates),
        "",
        "## Execution Plan",
        "",
        md_table(next_plan),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
