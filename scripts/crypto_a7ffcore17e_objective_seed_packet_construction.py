from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore17e_objective_seed_packet_construction"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE17E_OBJECTIVE_SEED_PACKET_CONSTRUCTION_20260601.md"
CORE17 = REPO / "runtime" / "a7ffcore17_objective_seed_policy_contract" / "a7ffcore17_manifest.json"
SEED_QUEUE = REPO / "runtime" / "a7ffcore17_objective_seed_policy_contract" / "a7ffcore17_seed_policy_queue.csv"


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
    core17 = read_json(CORE17)
    if core17.get("decision") != "PASS_A7FFCORE17_OBJECTIVE_SEED_POLICY_CONTRACT_READY_FOR_CORE17E":
        raise SystemExit(f"CORE17 is not ready for CORE17E: {core17.get('decision')}")
    queue = pd.read_csv(SEED_QUEUE)
    packet = queue.copy()
    packet = packet.drop_duplicates(subset=["blueprint_id", "label_family", "label_horizon_h"], keep="first")
    packet = packet.sort_values(["seed_lane", "queue_rank"]).reset_index(drop=True)
    packet.insert(0, "packet_rank", range(1, len(packet) + 1))
    packet["packet_stage"] = "A7FF-CORE17E"
    packet["packet_role"] = "objective_seed_pre_replay"
    packet["allowed_for_core18_preflight"] = True
    packet["allowed_for_direct_replay"] = False
    packet["allowed_for_search"] = False
    packet["allowed_for_alpha_proof"] = False

    lane_summary = (
        packet.groupby(["seed_lane", "second_pass_family"], dropna=False)
        .agg(
            rows=("packet_rank", "size"),
            label_family_count=("label_family", "nunique"),
            horizon_count=("label_horizon_h", "nunique"),
            operator_count=("operator", "nunique"),
            left_field_count=("left_field", "nunique"),
            right_field_count=("right_field", "nunique"),
            lag_ok_count=("lag_ok", lambda s: int(s.astype(str).str.lower().eq("true").sum())),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    label_summary = (
        packet.groupby(["label_family", "label_horizon_h"], dropna=False)
        .agg(rows=("packet_rank", "size"), seed_lane_count=("seed_lane", "nunique"))
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    operator_summary = (
        packet.groupby(["operator"], dropna=False)
        .agg(rows=("packet_rank", "size"), seed_lane_count=("seed_lane", "nunique"))
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    duplicate_keys = int(packet.duplicated(subset=["blueprint_id", "label_family", "label_horizon_h"]).sum())
    top_lane_share = float(packet["seed_lane"].value_counts(normalize=True).max()) if not packet.empty else 0.0
    non_l5_share = float(packet["label_family"].astype(str).ne("L5_vol_adjusted_return").mean()) if not packet.empty else 0.0
    blockers: list[str] = []
    if len(packet) < 96:
        blockers.append("packet_size_lt_96")
    if packet["seed_lane"].nunique() < 4:
        blockers.append("seed_lane_count_lt_4")
    if top_lane_share > 0.35:
        blockers.append("top_seed_lane_share_gt_35pct")
    if duplicate_keys:
        blockers.append("duplicate_packet_keys")
    if non_l5_share < 0.40:
        blockers.append("non_l5_share_lt_40pct")
    if packet["operator"].nunique() < 3:
        blockers.append("operator_count_lt_3")
    if packet["label_family"].nunique() < 3:
        blockers.append("label_family_count_lt_3")
    passed = not blockers
    decision = "PASS_A7FFCORE17E_OBJECTIVE_SEED_PACKET_READY_FOR_CORE18_CONTRACT" if passed else "HOLD_A7FFCORE17E_OBJECTIVE_SEED_PACKET_FAIL"

    packet.to_csv(RUNTIME / "a7ffcore17e_objective_seed_packet.csv", index=False)
    lane_summary.to_csv(RUNTIME / "a7ffcore17e_seed_lane_summary.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ffcore17e_label_horizon_summary.csv", index=False)
    operator_summary.to_csv(RUNTIME / "a7ffcore17e_operator_summary.csv", index=False)
    gate = pd.DataFrame(
        [
            {"gate": "packet_size", "value": len(packet), "threshold": ">=96", "pass": len(packet) >= 96},
            {"gate": "seed_lane_count", "value": packet["seed_lane"].nunique(), "threshold": ">=4", "pass": packet["seed_lane"].nunique() >= 4},
            {"gate": "top_seed_lane_share", "value": top_lane_share, "threshold": "<=0.35", "pass": top_lane_share <= 0.35},
            {"gate": "duplicate_keys", "value": duplicate_keys, "threshold": "0", "pass": duplicate_keys == 0},
            {"gate": "non_l5_share", "value": non_l5_share, "threshold": ">=0.40", "pass": non_l5_share >= 0.40},
            {"gate": "operator_count", "value": packet["operator"].nunique(), "threshold": ">=3", "pass": packet["operator"].nunique() >= 3},
            {"gate": "label_family_count", "value": packet["label_family"].nunique(), "threshold": ">=3", "pass": packet["label_family"].nunique() >= 3},
        ]
    )
    gate.to_csv(RUNTIME / "a7ffcore17e_gate_audit.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE17E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE17",
        "source_decision": core17.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "packet_size": int(len(packet)),
        "seed_lane_count": int(packet["seed_lane"].nunique()),
        "top_seed_lane_share": top_lane_share,
        "non_l5_share": non_l5_share,
        "operator_count": int(packet["operator"].nunique()),
        "label_family_count": int(packet["label_family"].nunique()),
        "authorizes_core18_contract": passed,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE18 bounded replay preflight contract" if passed else "A7FF-CORE17ER packet forensic",
    }
    write_json(RUNTIME / "a7ffcore17e_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE17E OBJECTIVE SEED PACKET CONSTRUCTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE17E builds and audits the objective seed packet for preflight contract drafting only. It does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Gate Audit",
        "",
        md_table(gate),
        "",
        "## Seed Lane Summary",
        "",
        md_table(lane_summary),
        "",
        "## Label/Horizon Summary",
        "",
        md_table(label_summary),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
