from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore17_objective_seed_policy_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE17_OBJECTIVE_SEED_POLICY_CONTRACT_20260601.md"
CORE16L = REPO / "runtime" / "a7ffcore16l_strict_preseed_queue_lock" / "a7ffcore16l_manifest.json"
LOCKED_QUEUE = REPO / "runtime" / "a7ffcore16l_strict_preseed_queue_lock" / "a7ffcore16l_locked_strict_preseed_queue.csv"


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
    core16l = read_json(CORE16L)
    if core16l.get("decision") != "PASS_A7FFCORE16L_STRICT_PRESEED_QUEUE_LOCKED_READY_FOR_CORE17_CONTRACT":
        raise SystemExit(f"CORE16L is not ready for CORE17: {core16l.get('decision')}")
    queue = pd.read_csv(LOCKED_QUEUE)

    lane_policy = pd.DataFrame(
        [
            {
                "seed_lane": "S0_positioning_price_basis",
                "source_family": "H0_I3_deconcentration",
                "seed_role": "objective_seed",
                "max_share": 0.35,
                "allowed_next_use": "seed_packet_construction_only",
            },
            {
                "seed_lane": "S1_liquidity_basis_positioning",
                "source_family": "H1_I5_deconcentration",
                "seed_role": "objective_seed",
                "max_share": 0.35,
                "allowed_next_use": "seed_packet_construction_only",
            },
            {
                "seed_lane": "S2_taker_flow_liquidity_oi",
                "source_family": "H2_I4_near_miss_repair",
                "seed_role": "objective_seed_floor_lane",
                "max_share": 0.20,
                "allowed_next_use": "seed_packet_construction_only",
            },
            {
                "seed_lane": "S3_cross_family_bridge",
                "source_family": "H3_cross_family_bridge",
                "seed_role": "objective_seed_bridge_lane",
                "max_share": 0.25,
                "allowed_next_use": "seed_packet_construction_only",
            },
        ]
    )
    queue = queue.merge(lane_policy[["seed_lane", "source_family", "seed_role"]], left_on="second_pass_family", right_on="source_family", how="left")
    queue["seed_status"] = "locked_preseed_not_replayed"
    queue["allowed_for_replay"] = False
    queue["allowed_for_search"] = False
    queue["allowed_for_alpha_proof"] = False
    seed_summary = (
        queue.groupby(["seed_lane", "second_pass_family"], dropna=False)
        .agg(
            rows=("blueprint_id", "size"),
            label_family_count=("label_family", "nunique"),
            horizon_count=("label_horizon_h", "nunique"),
            operator_count=("operator", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            lag_ok_count=("lag_ok", lambda s: int(s.astype(str).str.lower().eq("true").sum())),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    objective_policy = pd.DataFrame(
        [
            {
                "policy_id": "P0_seed_packet_only",
                "rule": "CORE17 authorizes only CORE17E seed packet construction",
                "reason": "locked preseed rows still require packet-level dedup, label/horizon balance, and replay preflight before numeric replay",
            },
            {
                "policy_id": "P1_no_search",
                "rule": "no open grammar formula generation or large search",
                "reason": "CORE16 produced a governed seed queue, not an alpha pool",
            },
            {
                "policy_id": "P2_no_direct_promotion",
                "rule": "no seed row can become research_candidate without bounded replay and controls",
                "reason": "current evidence is pre-replay response/control surface only",
            },
            {
                "policy_id": "P3_preserve_breadth",
                "rule": "CORE17E must preserve all four seed lanes and cap top lane share",
                "reason": "prior failure mode was family concentration",
            },
        ]
    )
    blocked = pd.DataFrame(
        [
            {"blocked_task": "A7FF bounded replay", "reason": "blocked until CORE17E seed packet and CORE18 replay preflight contract pass"},
            {"blocked_task": "A7FF formula generation/search", "reason": "blocked: CORE17 is seed policy contract only"},
            {"blocked_task": "A7FF large search", "reason": "blocked until bounded replay produces control-clean evidence"},
            {"blocked_task": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )
    queue.to_csv(RUNTIME / "a7ffcore17_seed_policy_queue.csv", index=False)
    lane_policy.to_csv(RUNTIME / "a7ffcore17_seed_lane_policy.csv", index=False)
    seed_summary.to_csv(RUNTIME / "a7ffcore17_seed_lane_summary.csv", index=False)
    objective_policy.to_csv(RUNTIME / "a7ffcore17_objective_policy.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore17_blocked_tasks.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE17",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16L",
        "source_decision": core16l.get("decision"),
        "decision": "PASS_A7FFCORE17_OBJECTIVE_SEED_POLICY_CONTRACT_READY_FOR_CORE17E",
        "seed_queue_size": int(len(queue)),
        "seed_lane_count": int(queue["seed_lane"].nunique()),
        "top_seed_lane_share": float(queue["seed_lane"].value_counts(normalize=True).max()),
        "authorizes_core17e": True,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE17E objective seed packet construction audit",
    }
    write_json(RUNTIME / "a7ffcore17_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE17 OBJECTIVE SEED POLICY CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE17 converts the locked CORE16L strict queue into objective seed policy for packet construction only. It does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Seed Lane Summary",
        "",
        md_table(seed_summary),
        "",
        "## Objective Policy",
        "",
        md_table(objective_policy),
        "",
        "## Blocked",
        "",
        md_table(blocked),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
