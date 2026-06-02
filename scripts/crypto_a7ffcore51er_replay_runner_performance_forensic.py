from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore51er_replay_runner_performance_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE51ER_REPLAY_RUNNER_PERFORMANCE_FORENSIC_20260602.md"
CORE51 = REPO / "runtime" / "a7ffcore51_filtered_replay_contract" / "a7ffcore51_manifest.json"


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
    source = read_json(CORE51)
    if source.get("decision") != "PASS_A7FFCORE51_FILTERED_REPLAY_CONTRACT_READY_FOR_CORE51E":
        raise SystemExit(f"CORE51 not ready for CORE51ER forensic: {source.get('decision')}")

    incident = pd.DataFrame(
        [
            {
                "incident_id": "I0_core51e_smoke_timeout",
                "attempted_command": "$env:A7FFCORE51E_MAX_CANDIDATES='16'; py scripts/crypto_a7ffcore51e_filtered_replay_execution.py",
                "timeout_seconds": 1200,
                "candidate_count": 16,
                "frame_rows": 6949596,
                "frame_symbols": 498,
                "result": "timeout_no_replay_artifacts",
            }
        ]
    )
    bottlenecks = pd.DataFrame(
        [
            {
                "bottleneck_id": "B0_repeated_full_frame_rank",
                "description": "runner recomputes timestamp rank/top-bottom spread for every seed, control, label family, and horizon",
                "severity": "critical",
                "fix": "precompute timestamp group codes and use vectorized top/bottom masks per signal",
            },
            {
                "bottleneck_id": "B1_repeated_control_replay",
                "description": "stale/sign/time/symbol controls trigger four additional full-frame spread passes per label",
                "severity": "critical",
                "fix": "compute original/control spreads in one vectorized block and cache label arrays",
            },
            {
                "bottleneck_id": "B2_full_frame_reload",
                "description": "runner rebuilds full 498-symbol frame and latent overlay inside execution",
                "severity": "medium",
                "fix": "persist compact replay frame or memory-map only symbol/timestamp/labels/required fields",
            },
            {
                "bottleneck_id": "B3_no_shard_resume",
                "description": "timeout leaves no shard-level partial metrics because replay writes only at the end",
                "severity": "high",
                "fix": "write per-shard/per-candidate metrics incrementally with resume manifest",
            },
        ]
    )
    repair_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE51P",
                "action": "optimized replay runner contract and implementation",
                "requirements": "sharded, resumable, vectorized label arrays, incremental writes",
                "executes_replay": False,
            },
            {
                "stage": "A7FF-CORE51PE",
                "action": "optimized 16-candidate smoke",
                "requirements": "complete within 180 seconds and produce metrics",
                "executes_replay": True,
            },
            {
                "stage": "A7FF-CORE51E-R",
                "action": "rerun bounded filtered replay with optimized runner",
                "requirements": "384 candidates max, shard outputs, no search/proof/promotion",
                "executes_replay": True,
            },
        ]
    )
    decision = "HOLD_A7FFCORE51ER_REPLAY_RUNNER_PERFORMANCE_BLOCKER"
    manifest = {
        "stage": "A7FF-CORE51ER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE51",
        "source_decision": source.get("decision"),
        "decision": decision,
        "dominant_failure": "replay_runner_repeated_full_frame_groupby_rank_timeout",
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core51p_runner_optimization": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE51P optimized replay runner contract / implementation",
    }
    authorization = {
        "authorized": {"A7FF-CORE51P optimized replay runner contract / implementation": True},
        "not_authorized": {
            "CORE51E_current_runner_rerun": True,
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    incident.to_csv(RUNTIME / "a7ffcore51er_timeout_incident.csv", index=False)
    bottlenecks.to_csv(RUNTIME / "a7ffcore51er_bottleneck_matrix.csv", index=False)
    repair_plan.to_csv(RUNTIME / "a7ffcore51er_repair_plan.csv", index=False)
    write_json(RUNTIME / "a7ffcore51er_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore51er_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE51ER REPLAY RUNNER PERFORMANCE FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE51E candidate logic is not rejected. The current runner implementation is rejected because the 16-candidate smoke timed out after 1200 seconds. The blocker is repeated full-frame groupby/rank replay, not field/data/source readiness.",
        "",
        "## Incident",
        "",
        md_table(incident),
        "",
        "## Bottleneck Matrix",
        "",
        md_table(bottlenecks),
        "",
        "## Repair Plan",
        "",
        md_table(repair_plan),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
