from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore15x_objective_surface_reset_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE15X_OBJECTIVE_SURFACE_RESET_CONTRACT_20260601.md"
CORE14SER = REPO / "runtime" / "a7ffcore14ser_repaired_replay_forensic" / "a7ffcore14ser_manifest.json"
CORE14SER_FAMILY = REPO / "runtime" / "a7ffcore14ser_repaired_replay_forensic" / "a7ffcore14ser_family_summary.csv"
CORE14SER_SENS = REPO / "runtime" / "a7ffcore14ser_repaired_replay_forensic" / "a7ffcore14ser_gate_sensitivity.csv"


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
    core14ser = read_json(CORE14SER)
    if core14ser.get("decision") != "PASS_A7FFCORE14SER_REPAIRED_REPLAY_FORENSIC_COMPLETE_STOP_REPLAY_EXPANSION":
        raise SystemExit(f"A7FF-CORE14SER is not ready: {core14ser.get('decision')}")

    family = pd.read_csv(CORE14SER_FAMILY)
    sens = pd.read_csv(CORE14SER_SENS)
    reset_axes = pd.DataFrame(
        [
            {
                "axis": "A0_label_surface",
                "problem": "numeric clue selection does not translate into validation+recent 5bps replay clean breadth",
                "repair_requirement": "score objectives by split-separate replay stability proxy before packet construction",
            },
            {
                "axis": "A1_control_surface",
                "problem": "wrong-lag/shuffle/placebo controls dominate most replay rows",
                "repair_requirement": "make max non-signflip control margin a pre-packet hard gate, not only replay attribution",
            },
            {
                "axis": "A2_cost_surface",
                "problem": "many high-tstat candidates lose positive spread after 5bps adjustment",
                "repair_requirement": "use 5bps cost floor in objective-surface construction",
            },
            {
                "axis": "A3_family_surface",
                "problem": "clean evidence collapses to one semantic/motif family",
                "repair_requirement": "treat single-family clean evidence as non-expandable diagnostic, not search seed",
            },
            {
                "axis": "A4_expression_surface",
                "problem": "packet repair increased outside-old coverage but did not improve replay stability",
                "repair_requirement": "stop queue reshuffling; rebuild objectives from replay-stability features",
            },
        ]
    )
    allowed_families = pd.DataFrame(
        [
            {
                "family": "split_stable_basis_taker",
                "status": "diagnostic_only_until_stability_proven",
                "rule": "allowed only if validation and recent both pass before any search expansion",
            },
            {
                "family": "control_margin_first_liquidity_volatility",
                "status": "conditional",
                "rule": "allowed only with control_ratio < 0.8 in validation and recent at 5bps",
            },
            {
                "family": "oi_positioning_retest",
                "status": "weak_prior_retest_only",
                "rule": "requires non-replay numeric evidence plus split-stable replay proxy; no direct expansion",
            },
            {
                "family": "fresh_objective_surface",
                "status": "preferred",
                "rule": "construct from primitive response fields that survive split/control/cost gates before formula mutation",
            },
        ]
    )
    blocked = pd.DataFrame(
        [
            {"item": "CORE14 packet rerun", "reason": "already failed; CORE14R attributed control/cost/split collapse"},
            {"item": "CORE14SE repaired packet rerun", "reason": "already failed; CORE14SER found only one clean candidate"},
            {"item": "CORE15 search-readiness", "reason": "blocked; clean pool breadth is insufficient"},
            {"item": "large search", "reason": "blocked; replay-stable objective surface is not established"},
            {"item": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )
    next_contract = {
        "stage": "A7FF-CORE15Y",
        "action": "build replay-stability objective surface from existing response/replay rows; no formula generation",
        "inputs": [
            "CORE13E numeric clues",
            "CORE14E replay rows",
            "CORE14SEE repaired replay rows",
            "CORE14R and CORE14SER forensic maps",
        ],
        "must_output": [
            "candidate replay-stability feature matrix",
            "family stability scorecard",
            "control/cost/split bottleneck map",
            "objective-surface allowed seed policy",
        ],
        "pass_minimum": {
            "candidate_count_with_split_stable_proxy": 32,
            "semantic_bucket_count": 5,
            "motif_bucket_count": 4,
            "top_family_share_max": 0.35,
        },
        "forbidden": [
            "new formula generation",
            "bounded replay rerun",
            "large search",
            "alpha proof",
            "shadow/paper/live",
        ],
    }
    reset_axes.to_csv(RUNTIME / "a7ffcore15x_reset_axes.csv", index=False)
    allowed_families.to_csv(RUNTIME / "a7ffcore15x_allowed_family_policy.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore15x_blocked_actions.csv", index=False)
    family.to_csv(RUNTIME / "a7ffcore15x_source_family_summary.csv", index=False)
    sens.to_csv(RUNTIME / "a7ffcore15x_source_gate_sensitivity.csv", index=False)
    write_json(RUNTIME / "a7ffcore15x_next_contract.json", next_contract)

    decision = "PASS_A7FFCORE15X_OBJECTIVE_SURFACE_RESET_CONTRACT_READY_FOR_CORE15Y"
    manifest = {
        "stage": "A7FF-CORE15X",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE14SER",
        "source_decision": core14ser.get("decision"),
        "decision": decision,
        "dominant_failure": core14ser.get("dominant_failure"),
        "authorizes_core15y": True,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE15Y replay-stability objective-surface builder",
    }
    write_json(RUNTIME / "a7ffcore15x_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE15X OBJECTIVE SURFACE RESET CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE15X stops replay expansion after CORE14SER and defines a reset contract for replay-stability objective-surface construction. It does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Reset Axes",
        "",
        md_table(reset_axes),
        "",
        "## Allowed Family Policy",
        "",
        md_table(allowed_families),
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
