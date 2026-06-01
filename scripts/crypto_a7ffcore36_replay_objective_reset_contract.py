from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore36_replay_objective_reset_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE36_REPLAY_OBJECTIVE_RESET_CONTRACT_20260602.md"
CORE35 = REPO / "runtime" / "a7ffcore35_search_readiness_arbitration" / "a7ffcore35_manifest.json"
CORE35_AUTH = REPO / "runtime" / "a7ffcore35_search_readiness_arbitration" / "a7ffcore35_authorization_matrix.csv"


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
    source = read_json(CORE35)
    if source.get("decision") != "HOLD_A7FFCORE35_SEARCH_NOT_READY_REPLAY_TRANSLATION_FAILURE":
        raise SystemExit(f"CORE35 not in expected HOLD state: {source.get('decision')}")
    auth = pd.read_csv(CORE35_AUTH)
    objective_reset = pd.DataFrame(
        [
            {
                "objective_id": "R0_executable_spread_first",
                "description": "rank candidates by train executable spread after cost before IC-like response",
                "allowed": True,
                "forbidden": "IC-only or numeric-only ranking",
            },
            {
                "objective_id": "R1_control_margin_first",
                "description": "require train stale/control margin before queue inclusion",
                "allowed": True,
                "forbidden": "post-hoc control filtering after selected queue",
            },
            {
                "objective_id": "R2_oos_split_balance",
                "description": "score requires validation/test/recent split presence, not aggregate pass count",
                "allowed": True,
                "forbidden": "single-split or train-only success",
            },
            {
                "objective_id": "R3_family_role_specific",
                "description": "treat flow/microstructure as directional or hedge-like depending on train spread role",
                "allowed": True,
                "forbidden": "same objective for all data families",
            },
            {
                "objective_id": "R4_search",
                "description": "formula or large search",
                "allowed": False,
                "forbidden": "any search before replay-objective reset execution proves survivors",
            },
        ]
    )
    metric_contract = pd.DataFrame(
        [
            {"metric": "train_net_spread_after_cost", "role": "orientation and primary gate"},
            {"metric": "train_control_ratio", "role": "hard reject if >= 1.0"},
            {"metric": "oos_min_split_net_spread", "role": "split-balance gate"},
            {"metric": "oos_control_clean_count", "role": "control survival gate"},
            {"metric": "turnover_cost_sensitivity_2_5_10bps", "role": "cost fragility check"},
            {"metric": "family_cluster_diversity", "role": "queue concentration cap"},
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE36E",
                "action": "re-score existing CORE33 queue using replay-objective reset metrics",
                "executes_new_generation": False,
                "executes_search": False,
            },
            {
                "stage": "A7FF-CORE37",
                "action": "only if CORE36E finds survivors, write bounded replay repair/replay contract",
                "executes_new_generation": False,
                "executes_search": False,
            },
        ]
    )
    authorization = {
        "authorized": {"A7FF-CORE36E replay-objective reset execution": True},
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
        },
    }
    decision = "PASS_A7FFCORE36_REPLAY_OBJECTIVE_RESET_CONTRACT_READY_FOR_CORE36E"
    manifest = {
        "stage": "A7FF-CORE36",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE35",
        "source_decision": source.get("decision"),
        "decision": decision,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core36e_execution": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE36E replay-objective reset execution",
    }
    objective_reset.to_csv(RUNTIME / "a7ffcore36_objective_reset_policy.csv", index=False)
    metric_contract.to_csv(RUNTIME / "a7ffcore36_metric_contract.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore36_execution_plan.csv", index=False)
    auth.to_csv(RUNTIME / "a7ffcore36_source_authorization_snapshot.csv", index=False)
    write_json(RUNTIME / "a7ffcore36_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore36_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE36 REPLAY OBJECTIVE RESET CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE36 resets the replay objective after CORE35 determined search is not ready. It does not execute search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Objective Reset Policy",
        "",
        md_table(objective_reset),
        "",
        "## Metric Contract",
        "",
        md_table(metric_contract),
        "",
        "## Execution Plan",
        "",
        md_table(execution_plan),
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
