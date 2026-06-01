from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore19_bounded_replay_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE19_BOUNDED_REPLAY_CONTRACT_20260601.md"
CORE18E = REPO / "runtime" / "a7ffcore18e_bounded_replay_preflight" / "a7ffcore18e_manifest.json"
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
    core18e = read_json(CORE18E)
    if core18e.get("decision") != "PASS_A7FFCORE18E_BOUNDED_REPLAY_PREFLIGHT_READY_FOR_CORE19_CONTRACT":
        raise SystemExit(f"CORE18E is not ready for CORE19: {core18e.get('decision')}")
    packet = pd.read_csv(PACKET)
    replay_scope = pd.DataFrame(
        [
            {"item": "input_packet", "value": "A7FF-CORE17E objective seed packet", "hard_gate": True},
            {"item": "candidate_count", "value": str(len(packet)), "hard_gate": True},
            {"item": "selection_mode", "value": "bounded locked packet only; no generation; no mutation; no selector expansion", "hard_gate": True},
            {"item": "book", "value": "top/bottom cross-sectional replay proxy with dollar-neutral and lane/family caps", "hard_gate": True},
            {"item": "controls", "value": "wrong-lag future, stale, row/time/symbol shuffle, same-family placebo", "hard_gate": True},
            {"item": "latency", "value": "field-native timing plus one-bar lag stress", "hard_gate": True},
            {"item": "cost", "value": "2/5/10/20 bps proxy tiers", "hard_gate": True},
            {"item": "neutralization", "value": "global, liquidity tier, latent state, meme/multiplier aware", "hard_gate": True},
            {"item": "statistics", "value": "overlap robust and non-overlap offset stats", "hard_gate": True},
        ]
    )
    pass_gates = pd.DataFrame(
        [
            {"gate": "control_clean", "requirement": "no selected candidate with control_ratio >= 1.0 in any pre-May split"},
            {"gate": "lane_breadth", "requirement": "selected lanes >= 3 and top lane share <= 0.40"},
            {"gate": "non_l5_translation", "requirement": "non-L5 evidence must remain nonzero; L5-only pass is diagnostic only"},
            {"gate": "lag_survival", "requirement": "one-bar lag replay proxy must not flip or collapse for selected candidates"},
            {"gate": "cost_survival", "requirement": "5bps and 10bps tiers must remain directionally positive before deep audit"},
            {"gate": "stress_policy", "requirement": "May/stress labels post-selection only; no May in ranking, mutation, or weight update"},
        ]
    )
    blocked = pd.DataFrame(
        [
            {"blocked_task": "A7FF large search", "reason": "blocked until CORE19E bounded replay produces control-clean candidates and later selector governance passes"},
            {"blocked_task": "formula generation/search expansion", "reason": "blocked: CORE19 authorizes bounded replay execution only"},
            {"blocked_task": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )
    lane_counts = packet["seed_lane"].value_counts().rename_axis("seed_lane").reset_index(name="rows")
    replay_scope.to_csv(RUNTIME / "a7ffcore19_replay_scope.csv", index=False)
    pass_gates.to_csv(RUNTIME / "a7ffcore19_pass_gate_matrix.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore19_blocked_tasks.csv", index=False)
    lane_counts.to_csv(RUNTIME / "a7ffcore19_input_lane_counts.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE19",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE18E",
        "source_decision": core18e.get("decision"),
        "decision": "PASS_A7FFCORE19_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE19E",
        "input_packet_size": int(len(packet)),
        "authorizes_core19e_bounded_replay_execution": True,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE19E bounded replay execution on locked packet",
    }
    write_json(RUNTIME / "a7ffcore19_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE19 BOUNDED REPLAY CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE19 authorizes bounded replay execution on the locked packet only. It does not authorize formula generation, search expansion, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Replay Scope",
        "",
        md_table(replay_scope),
        "",
        "## Pass Gates",
        "",
        md_table(pass_gates),
        "",
        "## Input Lane Counts",
        "",
        md_table(lane_counts),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
