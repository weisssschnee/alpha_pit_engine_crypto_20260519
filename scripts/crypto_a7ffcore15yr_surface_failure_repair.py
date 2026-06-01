from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore15yr_surface_failure_repair"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE15YR_SURFACE_FAILURE_REPAIR_20260601.md"
CORE15Y = REPO / "runtime" / "a7ffcore15y_replay_stability_surface" / "a7ffcore15y_manifest.json"
SURFACE = REPO / "runtime" / "a7ffcore15y_replay_stability_surface" / "a7ffcore15y_candidate_surface_matrix.csv"
FAMILY = REPO / "runtime" / "a7ffcore15y_replay_stability_surface" / "a7ffcore15y_family_scorecard.csv"


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
    core15y = read_json(CORE15Y)
    if core15y.get("decision") != "HOLD_A7FFCORE15Y_REPLAY_STABILITY_SURFACE_INSUFFICIENT":
        raise SystemExit(f"A7FF-CORE15Y is not in repair state: {core15y.get('decision')}")
    surface = pd.read_csv(SURFACE)
    family = pd.read_csv(FAMILY)
    weak_points = pd.DataFrame(
        [
            {
                "weak_point": "W0_low_surface_candidate_count",
                "evidence": f"surface_candidate_count={core15y.get('surface_candidate_count')}",
                "repair": "do not replay current queue; rebuild candidate objectives from primitive response and non-replay split proxies",
            },
            {
                "weak_point": "W1_family_concentration",
                "evidence": f"top_family_share={core15y.get('top_family_share')}",
                "repair": "require objective-surface candidate quota by semantic family before any materialization queue",
            },
            {
                "weak_point": "W2_control_ratio_surface",
                "evidence": "family scorecard median control ratios mostly above 1",
                "repair": "make control margin a generation-side objective, not post-replay filter only",
            },
            {
                "weak_point": "W3_replay_before_surface",
                "evidence": "two bounded replay packets consumed but surface remains too narrow",
                "repair": "next stage must be surface reconstruction, not another bounded replay packet",
            },
        ]
    )
    next_contract = {
        "stage": "A7FF-CORE16",
        "action": "primitive-response replay-stability atlas rebuild",
        "scope": "no new formula grammar expansion; build candidate objectives from primitive/derived fields with replay-stability quotas",
        "required_inputs": [
            "A7AA primitive response maps",
            "A7FF CORE13E numeric clue rows",
            "A7FF CORE14E/14SEE replay rows",
            "field ontology and role enforcement ledgers",
        ],
        "required_outputs": [
            "field_type_by_label_horizon_stability.csv",
            "operator_by_field_type_stability.csv",
            "semantic_family_replay_stability_quota.csv",
            "core16_candidate_objective_atlas.csv",
            "core16_manifest.json",
        ],
        "pass_gate": {
            "objective_surface_candidate_count": 64,
            "semantic_bucket_count": 6,
            "motif_bucket_count": 5,
            "top_family_share_max": 0.30,
            "control_margin_policy": "median_control_ratio < 1.0 by selected family",
        },
        "forbidden": [
            "CORE14/CORE14SE packet rerun",
            "new formula search",
            "large search",
            "alpha proof",
            "shadow/paper/live",
        ],
    }
    blocked = pd.DataFrame(
        [
            {"item": "CORE15Z seed policy", "reason": "blocked: CORE15Y surface candidate breadth failed"},
            {"item": "bounded replay rerun", "reason": "blocked: replay has already shown objective-surface instability"},
            {"item": "formula search", "reason": "blocked: search would amplify an unstable objective surface"},
            {"item": "large search", "reason": "blocked until CORE16 atlas passes breadth/control gates"},
            {"item": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )
    weak_points.to_csv(RUNTIME / "a7ffcore15yr_weak_points.csv", index=False)
    family.to_csv(RUNTIME / "a7ffcore15yr_source_family_scorecard.csv", index=False)
    surface.to_csv(RUNTIME / "a7ffcore15yr_source_surface_matrix.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore15yr_blocked_actions.csv", index=False)
    write_json(RUNTIME / "a7ffcore15yr_next_contract.json", next_contract)
    decision = "PASS_A7FFCORE15YR_SURFACE_FAILURE_REPAIR_READY_FOR_CORE16_ATLAS"
    manifest = {
        "stage": "A7FF-CORE15YR",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE15Y",
        "source_decision": core15y.get("decision"),
        "decision": decision,
        "authorizes_core16": True,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE16 primitive-response replay-stability atlas rebuild",
    }
    write_json(RUNTIME / "a7ffcore15yr_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE15YR SURFACE FAILURE REPAIR",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE15YR stops replay/packet retries and defines the next atlas rebuild stage. It does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Weak Points",
        "",
        md_table(weak_points),
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
