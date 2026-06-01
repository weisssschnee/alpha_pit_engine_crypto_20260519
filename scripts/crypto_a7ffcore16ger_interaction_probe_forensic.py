from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16ger_interaction_probe_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16GER_INTERACTION_PROBE_FORENSIC_20260601.md"
CORE16GE = REPO / "runtime" / "a7ffcore16ge_family_native_interaction_probe" / "a7ffcore16ge_manifest.json"
SUMMARY = REPO / "runtime" / "a7ffcore16ge_family_native_interaction_probe" / "a7ffcore16ge_interaction_family_summary.csv"
CANDIDATES = REPO / "runtime" / "a7ffcore16ge_family_native_interaction_probe" / "a7ffcore16ge_interaction_probe_candidates.csv"
NEAR_RESPONSE = REPO / "runtime" / "a7ffcore16ge_family_native_interaction_probe" / "a7ffcore16ge_interaction_response_map.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


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

    core16ge = read_json(CORE16GE)
    if core16ge.get("decision") != "HOLD_A7FFCORE16GE_INTERACTION_PROBE_SUPPLY_INSUFFICIENT":
        raise SystemExit(f"CORE16GE is not in forensic state: {core16ge.get('decision')}")

    summary = load_csv(SUMMARY)
    candidates = load_csv(CANDIDATES)
    response = load_csv(NEAR_RESPONSE)

    if candidates.empty:
        candidate_breakdown = pd.DataFrame()
    else:
        candidate_breakdown = (
            candidates.groupby(["interaction_family", "operator", "label_family"], dropna=False)
            .agg(
                candidate_count=("blueprint_id", "size"),
                lag_ok_count=("lag_ok", "sum"),
                median_control_ratio=("control_ratio_premay_max", "median"),
                median_recent_lag=("one_bar_lag_recent_oriented", "median"),
            )
            .reset_index()
            .sort_values("candidate_count", ascending=False)
        )

    near = response[response.get("near_miss", pd.Series(dtype=bool)).astype(str).str.lower().eq("true")].copy() if not response.empty else pd.DataFrame()
    near_breakdown = (
        near.groupby(["interaction_family", "operator", "label_family"], dropna=False)
        .agg(near_miss_count=("blueprint_id", "size"), median_control_ratio=("control_ratio_premay_max", "median"))
        .reset_index()
        .sort_values("near_miss_count", ascending=False)
        if not near.empty
        else pd.DataFrame()
    )

    repair_actions = pd.DataFrame(
        [
            {
                "action_id": "R0_cap_successful_interactions",
                "target": "I3/I5",
                "action": "cap selected share and require operator/label diversity before any objective seed policy",
                "reason": "CORE16GE found candidates, but only from two interaction families",
            },
            {
                "action_id": "R1_expand_near_miss_I4",
                "target": "I4_taker_flow_x_OI_or_liquidity",
                "action": "repair near-miss rows with asymmetric transforms and tighter control-dominance diagnostics",
                "reason": "I4 produced near misses but no strict candidates; it is the best non-I3/I5 expansion lane",
            },
            {
                "action_id": "R2_block_dead_interactions",
                "target": "I0/I1/I2/I6",
                "action": "keep as diagnostic-only unless a later primitive/field update changes response evidence",
                "reason": "these interaction families produced no strict supply in CORE16GE",
            },
            {
                "action_id": "R3_second_pass_interaction_probe",
                "target": "CORE16H",
                "action": "run a bounded second-pass probe with asymmetric transforms and family caps; no open grammar",
                "reason": "nonzero supply exists, but breadth gates failed",
            },
        ]
    )

    next_contract = {
        "stage": "A7FF-CORE16H",
        "name": "second-pass interaction breadth repair contract",
        "authorized": True,
        "executes_replay": False,
        "executes_search": False,
        "scope": [
            "cap I3/I5 concentration",
            "expand I4 near-miss lane",
            "asymmetric left/right transforms",
            "operator/label diversity gates",
        ],
        "targets": {
            "min_candidate_count": 96,
            "min_interaction_family_count": 3,
            "top_interaction_family_share_max": 0.45,
            "min_operator_count": 2,
            "min_non_L5_label_share": 0.40,
        },
        "forbidden": [
            "open grammar FormulaGen",
            "bounded replay",
            "large search",
            "alpha proof",
            "shadow/paper/live",
        ],
    }

    blocked = pd.DataFrame(
        [
            {"item": "A7FF-CORE17 objective seed policy", "reason": "blocked: CORE16GE interaction breadth failed"},
            {"item": "formula generation", "reason": "blocked: only second-pass typed interaction probe is authorized"},
            {"item": "bounded replay", "reason": "blocked: no broad objective atlas"},
            {"item": "large search", "reason": "blocked"},
            {"item": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )

    decision = "PASS_A7FFCORE16GER_INTERACTION_FORENSIC_COMPLETE_READY_FOR_CORE16H"
    manifest = {
        "stage": "A7FF-CORE16GER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16GE",
        "source_decision": core16ge.get("decision"),
        "decision": decision,
        "dominant_failure": "interaction_candidate_supply_narrow_but_nonzero",
        "interaction_probe_candidate_count": int(core16ge.get("interaction_probe_candidate_count", 0)),
        "interaction_family_count": int(core16ge.get("interaction_family_count", 0)),
        "top_interaction_family_share": float(core16ge.get("top_interaction_family_share", 0.0)),
        "authorizes_core16h_contract": True,
        "authorizes_core17": False,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE16H second-pass interaction breadth repair contract",
    }

    summary.to_csv(RUNTIME / "a7ffcore16ger_source_interaction_family_summary.csv", index=False)
    candidate_breakdown.to_csv(RUNTIME / "a7ffcore16ger_candidate_breakdown.csv", index=False)
    near_breakdown.to_csv(RUNTIME / "a7ffcore16ger_near_miss_breakdown.csv", index=False)
    repair_actions.to_csv(RUNTIME / "a7ffcore16ger_repair_actions.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore16ger_blocked_actions.csv", index=False)
    write_json(RUNTIME / "a7ffcore16ger_next_contract.json", next_contract)
    write_json(RUNTIME / "a7ffcore16ger_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE16GER INTERACTION PROBE FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16GER freezes the CORE16GE result. Typed interactions produced nonzero candidate supply, but only two interaction families contributed candidates. This blocks CORE17 and all search, while authorizing a second-pass interaction breadth repair contract.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Source Family Summary",
        "",
        md_table(summary),
        "",
        "## Candidate Breakdown",
        "",
        md_table(candidate_breakdown),
        "",
        "## Near-Miss Breakdown",
        "",
        md_table(near_breakdown),
        "",
        "## Repair Actions",
        "",
        md_table(repair_actions),
        "",
        "## Next Contract",
        "",
        "```json",
        json.dumps(next_contract, indent=2, sort_keys=True),
        "```",
        "",
        "## Blocked Actions",
        "",
        md_table(blocked),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
