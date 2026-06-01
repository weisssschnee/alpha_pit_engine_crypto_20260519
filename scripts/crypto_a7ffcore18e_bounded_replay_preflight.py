from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore18e_bounded_replay_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE18E_BOUNDED_REPLAY_PREFLIGHT_20260601.md"
CORE18 = REPO / "runtime" / "a7ffcore18_bounded_replay_preflight_contract" / "a7ffcore18_manifest.json"
PACKET = REPO / "runtime" / "a7ffcore17e_objective_seed_packet_construction" / "a7ffcore17e_objective_seed_packet.csv"
A7AA0_FIELDS = REPO / "runtime" / "a7aa0_label_feature_response_contract" / "a7aa0_candidate_primitive_fields.csv"


ALLOWED_OPERATORS = {"Mul", "SafeDiv", "Sub"}


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
    core18 = read_json(CORE18)
    if core18.get("decision") != "PASS_A7FFCORE18_BOUNDED_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE18E":
        raise SystemExit(f"CORE18 is not ready for CORE18E: {core18.get('decision')}")
    packet = pd.read_csv(PACKET)
    fields = pd.read_csv(A7AA0_FIELDS)
    known_fields = set(fields["field_name"].astype(str))
    packet_fields = set(packet["left_field"].astype(str)) | set(packet["right_field"].astype(str))
    missing_fields = sorted(packet_fields - known_fields)
    bad_ops = sorted(set(packet["operator"].astype(str)) - ALLOWED_OPERATORS)
    duplicate_keys = int(packet.duplicated(subset=["blueprint_id", "label_family", "label_horizon_h"]).sum())
    direct_replay_flags = int(packet.get("allowed_for_direct_replay", pd.Series(dtype=bool)).astype(str).str.lower().eq("true").sum())
    search_flags = int(packet.get("allowed_for_search", pd.Series(dtype=bool)).astype(str).str.lower().eq("true").sum())
    alpha_flags = int(packet.get("allowed_for_alpha_proof", pd.Series(dtype=bool)).astype(str).str.lower().eq("true").sum())
    role_counts = packet["packet_role"].value_counts().rename_axis("packet_role").reset_index(name="rows") if "packet_role" in packet.columns else pd.DataFrame()
    lane_summary = (
        packet.groupby(["seed_lane"], dropna=False)
        .agg(
            rows=("packet_rank", "size"),
            label_family_count=("label_family", "nunique"),
            horizon_count=("label_horizon_h", "nunique"),
            operator_count=("operator", "nunique"),
            left_field_count=("left_field", "nunique"),
            right_field_count=("right_field", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    top_lane_share = float(packet["seed_lane"].value_counts(normalize=True).max()) if not packet.empty else 0.0
    non_l5_share = float(packet["label_family"].astype(str).ne("L5_vol_adjusted_return").mean()) if not packet.empty else 0.0
    blockers: list[str] = []
    if len(packet) != 96:
        blockers.append("packet_size_not_96")
    if missing_fields:
        blockers.append("missing_field_contract_entries")
    if bad_ops:
        blockers.append("unsupported_operator")
    if duplicate_keys:
        blockers.append("duplicate_packet_keys")
    if direct_replay_flags:
        blockers.append("direct_replay_flag_present")
    if search_flags:
        blockers.append("search_flag_present")
    if alpha_flags:
        blockers.append("alpha_proof_flag_present")
    if packet["seed_lane"].nunique() < 4:
        blockers.append("seed_lane_count_lt_4")
    if top_lane_share > 0.35:
        blockers.append("top_lane_share_gt_35pct")
    if non_l5_share < 0.40:
        blockers.append("non_l5_share_lt_40pct")
    if packet["operator"].nunique() < 3:
        blockers.append("operator_count_lt_3")
    decision = "PASS_A7FFCORE18E_BOUNDED_REPLAY_PREFLIGHT_READY_FOR_CORE19_CONTRACT" if not blockers else "HOLD_A7FFCORE18E_BOUNDED_REPLAY_PREFLIGHT_FAIL"

    field_audit = pd.DataFrame(
        [
            {"field_name": field, "in_field_contract": field in known_fields}
            for field in sorted(packet_fields)
        ]
    )
    gate = pd.DataFrame(
        [
            {"gate": "packet_size", "value": len(packet), "threshold": "96", "pass": len(packet) == 96},
            {"gate": "missing_fields", "value": len(missing_fields), "threshold": "0", "pass": len(missing_fields) == 0},
            {"gate": "unsupported_operators", "value": len(bad_ops), "threshold": "0", "pass": len(bad_ops) == 0},
            {"gate": "duplicate_keys", "value": duplicate_keys, "threshold": "0", "pass": duplicate_keys == 0},
            {"gate": "direct_replay_flags", "value": direct_replay_flags, "threshold": "0", "pass": direct_replay_flags == 0},
            {"gate": "search_flags", "value": search_flags, "threshold": "0", "pass": search_flags == 0},
            {"gate": "alpha_flags", "value": alpha_flags, "threshold": "0", "pass": alpha_flags == 0},
            {"gate": "top_lane_share", "value": top_lane_share, "threshold": "<=0.35", "pass": top_lane_share <= 0.35},
            {"gate": "non_l5_share", "value": non_l5_share, "threshold": ">=0.40", "pass": non_l5_share >= 0.40},
        ]
    )
    field_audit.to_csv(RUNTIME / "a7ffcore18e_field_contract_audit.csv", index=False)
    lane_summary.to_csv(RUNTIME / "a7ffcore18e_lane_summary.csv", index=False)
    role_counts.to_csv(RUNTIME / "a7ffcore18e_packet_role_counts.csv", index=False)
    gate.to_csv(RUNTIME / "a7ffcore18e_gate_audit.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE18E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE18",
        "source_decision": core18.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "packet_size": int(len(packet)),
        "missing_field_count": len(missing_fields),
        "unsupported_operator_count": len(bad_ops),
        "duplicate_keys": duplicate_keys,
        "seed_lane_count": int(packet["seed_lane"].nunique()),
        "top_lane_share": top_lane_share,
        "non_l5_share": non_l5_share,
        "authorizes_core19_contract": not blockers,
        "authorizes_bounded_replay_execution": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE19 bounded replay contract" if not blockers else "A7FF-CORE18ER preflight forensic",
    }
    write_json(RUNTIME / "a7ffcore18e_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE18E BOUNDED REPLAY PREFLIGHT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE18E verifies bounded replay preflight readiness for the locked packet. It does not execute bounded replay, formula generation, search, alpha proof, shadow, paper, or live.",
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
        "## Lane Summary",
        "",
        md_table(lane_summary),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
