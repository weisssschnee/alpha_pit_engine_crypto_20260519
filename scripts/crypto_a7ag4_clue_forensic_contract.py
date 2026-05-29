from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ag4_clue_forensic_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AG4_CLUE_FORENSIC_CONTRACT_20260529.md"

A7AG3_MANIFEST = REPO / "runtime" / "a7ag3_numeric_replay_pilot" / "a7ag3_manifest.json"
A7AG3_CLUES = REPO / "runtime" / "a7ag3_numeric_replay_pilot" / "a7ag3_replay_clues.csv"
A7AG3_METRICS = REPO / "runtime" / "a7ag3_numeric_replay_pilot" / "a7ag3_candidate_replay_metrics.csv"

ORDINARY_LABELS = {"L0_raw_forward_return", "L1_cross_sectional_relative_return"}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
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


def clue_role(row: dict[str, Any]) -> str:
    track = str(row.get("track_id", ""))
    label = str(row.get("label_family", ""))
    if track == "G0_ordinary_alpha_basis_premium" and label in ORDINARY_LABELS:
        return "ordinary_raw_relative_alpha_clue"
    if track == "G0_ordinary_alpha_basis_premium":
        return "basis_premium_vol_adjusted_diagnostic"
    if track == "G1_neutralized_alpha_diagnostic":
        return "neutralized_vol_adjusted_diagnostic"
    if track == "G2_downside_risk_defense":
        return "downside_risk_defense_clue"
    return "unclassified_clue"


def share_summary(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    if frame.empty or column not in frame.columns:
        return pd.DataFrame(columns=[column, "count", "share"])
    out = frame[column].fillna("missing").astype(str).value_counts().rename_axis(column).reset_index(name="count")
    out["share"] = out["count"] / max(1, int(len(frame)))
    return out


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ag3 = read_json(A7AG3_MANIFEST)
    if not a7ag3.get("authorizes_a7ag4_forensic_contract"):
        raise SystemExit("A7AG-3 does not authorize A7AG-4")

    clues = pd.read_csv(A7AG3_CLUES)
    metrics = pd.read_csv(A7AG3_METRICS)
    clues["clue_role"] = [clue_role(row) for row in clues.to_dict("records")]
    clues["survives_10bps_proxy"] = pd.to_numeric(clues.get("cost10_recent_oriented", np.nan), errors="coerce") > 0
    clues["survives_20bps_proxy"] = pd.to_numeric(clues.get("cost20_recent_oriented", np.nan), errors="coerce") > 0
    clues["near_control_boundary"] = pd.to_numeric(clues.get("control_ratio_premay_max", np.nan), errors="coerce") >= 0.80

    role_summary = (
        clues.groupby(["clue_role", "track_id", "label_family"], dropna=False)
        .agg(
            clue_count=("candidate_id", "count"),
            seed_field_count=("seed_field", "nunique"),
            interaction_field_count=("interaction_field", "nunique"),
            skeleton_count=("skeleton_key", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            max_control_ratio=("control_ratio_premay_max", "max"),
            cost10_survivors=("survives_10bps_proxy", "sum"),
            cost20_survivors=("survives_20bps_proxy", "sum"),
            near_control_boundary=("near_control_boundary", "sum"),
        )
        .reset_index()
        if not clues.empty
        else pd.DataFrame()
    )
    concentration = pd.concat(
        [
            share_summary(clues, "seed_field").assign(axis="seed_field").rename(columns={"seed_field": "value"}),
            share_summary(clues, "interaction_field").assign(axis="interaction_field").rename(columns={"interaction_field": "value"}),
            share_summary(clues, "skeleton_key").assign(axis="skeleton_key").rename(columns={"skeleton_key": "value"}),
            share_summary(clues, "production_key").assign(axis="production_key").rename(columns={"production_key": "value"}),
            share_summary(clues, "label_family").assign(axis="label_family").rename(columns={"label_family": "value"}),
        ],
        ignore_index=True,
    )
    top_concentration = concentration.sort_values(["axis", "share"], ascending=[True, False]).groupby("axis").head(5)

    ordinary_alpha_clue_count = int((clues["clue_role"] == "ordinary_raw_relative_alpha_clue").sum())
    vol_adjusted_diagnostic_count = int(
        clues["clue_role"].isin(["basis_premium_vol_adjusted_diagnostic", "neutralized_vol_adjusted_diagnostic"]).sum()
    )
    downside_clue_count = int((clues["clue_role"] == "downside_risk_defense_clue").sum())
    cost20_survivor_count = int(clues["survives_20bps_proxy"].sum())
    near_control_count = int(clues["near_control_boundary"].sum())

    forensic_contract = {
        "scope": "forensic contract only; no generation, no search, no alpha proof",
        "inputs": [
            str(A7AG3_CLUES.relative_to(REPO)),
            str(A7AG3_METRICS.relative_to(REPO)),
        ],
        "required_a7ag5_audits": [
            "role_specific_label_translation",
            "symbol_month_latent_concentration",
            "cost_ladder_5_10_20bps",
            "expanded_negative_control_margin",
            "ordinary_alpha_vs_risk_defense_separation",
            "duplicate_skeleton_and_production_key_cap",
        ],
        "ordinary_alpha_rule": "Only L0/L1 G0 clues can be ordinary alpha evidence. L5 vol-adjusted and L6 downside clues remain diagnostic or risk-defense only.",
        "not_authorized": [
            "formula_search_execution",
            "large_search",
            "alpha_proof",
            "shadow_paper_live",
        ],
    }

    decision = (
        "PASS_A7AG4_CLUE_FORENSIC_CONTRACT_READY_FOR_A7AG5"
        if int(len(clues)) > 0
        else "HOLD_A7AG4_NO_CLUES_TO_FORENSIC"
    )
    manifest = {
        "stage": "A7AG-4",
        "generated_at": now_utc(),
        "decision": decision,
        "input_a7ag3_decision": a7ag3.get("decision"),
        "executes_contract_only": True,
        "executes_formula_generation": False,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_a7ag5_clue_forensic_audit": decision.startswith("PASS_"),
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may": False,
        "input_clue_count": int(len(clues)),
        "ordinary_alpha_clue_count": ordinary_alpha_clue_count,
        "vol_adjusted_diagnostic_count": vol_adjusted_diagnostic_count,
        "downside_risk_defense_clue_count": downside_clue_count,
        "cost20_proxy_survivor_count": cost20_survivor_count,
        "near_control_boundary_count": near_control_count,
    }

    clues.to_csv(RUNTIME / "a7ag4_role_classified_clues.csv", index=False)
    role_summary.to_csv(RUNTIME / "a7ag4_role_summary.csv", index=False)
    top_concentration.to_csv(RUNTIME / "a7ag4_concentration_summary.csv", index=False)
    write_json(RUNTIME / "a7ag4_forensic_contract.json", forensic_contract)
    write_json(RUNTIME / "a7ag4_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ag4_authorization_matrix.json",
        {
            "A7AG-4": {"status": decision},
            "a7ag5_clue_forensic_audit": {"authorized": bool(manifest["authorizes_a7ag5_clue_forensic_audit"])},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AG-4 CLUE FORENSIC CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AG-4 classifies A7AG-3 pilot clues by evidence role and defines the next forensic audit. It does not generate formulas, replay, search, train, or authorize proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Forensic Contract",
        "",
        "```json",
        json.dumps(forensic_contract, indent=2, sort_keys=True),
        "```",
        "",
        "## Role Summary",
        "",
        md_table(role_summary, 80),
        "",
        "## Concentration Summary",
        "",
        md_table(top_concentration, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "A7AG-4 separates ordinary alpha evidence from vol-adjusted diagnostics and downside/risk-defense clues.",
        "There are no ordinary raw/relative alpha clues unless ordinary_alpha_clue_count > 0.",
        "Formula search, large search, alpha proof, shadow, paper, and live remain not authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
