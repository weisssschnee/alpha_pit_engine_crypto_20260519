from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore51pr_local_runner_blocker_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE51PR_LOCAL_RUNNER_BLOCKER_FORENSIC_20260602.md"
CORE51ER = REPO / "runtime" / "a7ffcore51er_replay_runner_performance_forensic" / "a7ffcore51er_manifest.json"


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
    source = read_json(CORE51ER)
    if source.get("decision") != "HOLD_A7FFCORE51ER_REPLAY_RUNNER_PERFORMANCE_BLOCKER":
        raise SystemExit(f"CORE51ER not ready for CORE51PR: {source.get('decision')}")

    attempts = pd.DataFrame(
        [
            {
                "attempt_id": "A0_naive_runner",
                "candidate_count": 16,
                "timeout_seconds": 1200,
                "result": "timeout",
                "dominant_issue": "repeated full-frame groupby/rank",
            },
            {
                "attempt_id": "A1_dense_matrix_runner",
                "candidate_count": 16,
                "timeout_seconds": 900,
                "result": "timeout",
                "dominant_issue": "full-frame load/materialization plus dense control matrix construction still too slow locally",
            },
        ]
    )
    route = pd.DataFrame(
        [
            {
                "route_id": "R0_local_pandas_retry",
                "decision": "REJECT",
                "reason": "two 16-candidate smokes timed out; local retry wastes time",
            },
            {
                "route_id": "R1_company_machine_sharded_runner",
                "decision": "SELECT",
                "reason": "parallel shard execution and higher memory are required for 384-candidate filtered replay",
            },
            {
                "route_id": "R2_compact_replay_frame",
                "decision": "REQUIRED",
                "reason": "prebuild compact label/feature frame and per-shard candidate files before replay",
            },
        ]
    )
    requirements = pd.DataFrame(
        [
            {"requirement": "shard_count", "value": "at least 16 candidate shards, <=24 candidates/shard"},
            {"requirement": "compact_frame", "value": "symbol/timestamp/trade_close/split/needed feature columns only"},
            {"requirement": "incremental_outputs", "value": "write per-shard metrics before aggregation; resume-safe"},
            {"requirement": "controls", "value": "original/stale/time/symbol/sign controls required"},
            {"requirement": "authorization", "value": "no search/proof/promotion; replay diagnostics only"},
        ]
    )
    decision = "HOLD_A7FFCORE51PR_LOCAL_REPLAY_RUNNER_INSUFFICIENT_USE_COMPANY_SHARDS"
    manifest = {
        "stage": "A7FF-CORE51PR",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE51ER",
        "source_decision": source.get("decision"),
        "decision": decision,
        "dominant_failure": "local_runner_timeout_after_naive_and_dense_attempts",
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core51px_company_sharded_runner_contract": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE51PX company-machine sharded replay runner contract",
    }
    authorization = {
        "authorized": {"A7FF-CORE51PX company-machine sharded replay runner contract": True},
        "not_authorized": {
            "local_runner_retry": True,
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    attempts.to_csv(RUNTIME / "a7ffcore51pr_timeout_attempts.csv", index=False)
    route.to_csv(RUNTIME / "a7ffcore51pr_route_decision.csv", index=False)
    requirements.to_csv(RUNTIME / "a7ffcore51pr_company_runner_requirements.csv", index=False)
    write_json(RUNTIME / "a7ffcore51pr_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore51pr_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE51PR LOCAL RUNNER BLOCKER FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "The filtered replay candidate pool is not rejected. Local pandas replay execution is rejected after both naive and dense-matrix 16-candidate smokes timed out. Next work must move to a company-machine sharded runner with compact frame and incremental outputs.",
        "",
        "## Attempts",
        "",
        md_table(attempts),
        "",
        "## Route Decision",
        "",
        md_table(route),
        "",
        "## Company Runner Requirements",
        "",
        md_table(requirements),
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
