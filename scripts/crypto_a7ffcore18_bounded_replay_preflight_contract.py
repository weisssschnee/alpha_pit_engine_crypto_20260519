from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore18_bounded_replay_preflight_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE18_BOUNDED_REPLAY_PREFLIGHT_CONTRACT_20260601.md"
CORE17E = REPO / "runtime" / "a7ffcore17e_objective_seed_packet_construction" / "a7ffcore17e_manifest.json"
PACKET = REPO / "runtime" / "a7ffcore17e_objective_seed_packet_construction" / "a7ffcore17e_objective_seed_packet.csv"


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
    core17e = read_json(CORE17E)
    if core17e.get("decision") != "PASS_A7FFCORE17E_OBJECTIVE_SEED_PACKET_READY_FOR_CORE18_CONTRACT":
        raise SystemExit(f"CORE17E is not ready for CORE18: {core17e.get('decision')}")
    packet = pd.read_csv(PACKET)
    replay_contract = pd.DataFrame(
        [
            {
                "contract_item": "input_packet",
                "requirement": "use A7FF-CORE17E objective seed packet as the only candidate source",
                "hard_gate": True,
            },
            {
                "contract_item": "candidate_count",
                "requirement": "packet_size == 96; no extra generation, no stale candidate injection",
                "hard_gate": True,
            },
            {
                "contract_item": "labels",
                "requirement": "evaluate locked label_family/label_horizon plus replay book labels; report non-L5 separately",
                "hard_gate": True,
            },
            {
                "contract_item": "controls",
                "requirement": "wrong-lag future, stale lag, row/time/symbol shuffle, same-family placebo weaker than candidate",
                "hard_gate": True,
            },
            {
                "contract_item": "neutralization",
                "requirement": "global, liquidity-tier, latent-state, meme/multiplier aware summaries required",
                "hard_gate": True,
            },
            {
                "contract_item": "cost_lag",
                "requirement": "1bar lag and cost proxy stress required before any deep audit authorization",
                "hard_gate": True,
            },
            {
                "contract_item": "breadth",
                "requirement": "preserve four seed lanes; top selected lane share <= 35%",
                "hard_gate": True,
            },
            {
                "contract_item": "authorization",
                "requirement": "CORE18 authorizes only CORE18E replay preflight execution, not bounded replay/search",
                "hard_gate": True,
            },
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE18E",
                "action": "bounded replay preflight execution",
                "input": "A7FF-CORE17E objective seed packet",
                "output": "materialization/eval/control readiness for bounded replay",
                "authorized": True,
            },
            {
                "stage": "A7FF-CORE19",
                "action": "bounded replay contract",
                "input": "A7FF-CORE18E preflight pass",
                "output": "contract only",
                "authorized": False,
            },
        ]
    )
    blocked = pd.DataFrame(
        [
            {"blocked_task": "A7FF bounded replay execution", "reason": "blocked until CORE18E preflight passes and CORE19 contract exists"},
            {"blocked_task": "A7FF formula generation/search", "reason": "blocked: CORE18 is replay preflight contract only"},
            {"blocked_task": "A7FF large search", "reason": "blocked until bounded replay produces control-clean candidates"},
            {"blocked_task": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )
    packet_summary = (
        packet.groupby(["seed_lane", "label_family"], dropna=False)
        .agg(rows=("packet_rank", "size"), operator_count=("operator", "nunique"), horizon_count=("label_horizon_h", "nunique"))
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    replay_contract.to_csv(RUNTIME / "a7ffcore18_replay_preflight_contract.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore18_execution_plan.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore18_blocked_tasks.csv", index=False)
    packet_summary.to_csv(RUNTIME / "a7ffcore18_packet_summary.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE18",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE17E",
        "source_decision": core17e.get("decision"),
        "decision": "PASS_A7FFCORE18_BOUNDED_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE18E",
        "packet_size": int(len(packet)),
        "authorizes_core18e": True,
        "authorizes_bounded_replay_execution": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE18E bounded replay preflight execution",
    }
    write_json(RUNTIME / "a7ffcore18_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE18 BOUNDED REPLAY PREFLIGHT CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE18 defines the bounded replay preflight contract only. It does not execute bounded replay, formula generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Replay Preflight Contract",
        "",
        md_table(replay_contract),
        "",
        "## Execution Plan",
        "",
        md_table(execution_plan),
        "",
        "## Blocked",
        "",
        md_table(blocked),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
