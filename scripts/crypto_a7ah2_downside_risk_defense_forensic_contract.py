from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ah2_downside_risk_defense_forensic_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AH2_DOWNSIDE_RISK_DEFENSE_FORENSIC_CONTRACT_20260529.md"

A7AH0_MANIFEST = REPO / "runtime" / "a7ah0_post_a7ag_role_split_decision" / "a7ah0_manifest.json"
A7AG4_CLUES = REPO / "runtime" / "a7ag4_clue_forensic_contract" / "a7ag4_role_classified_clues.csv"


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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ah0 = read_json(A7AH0_MANIFEST)
    if not a7ah0.get("authorizes_a7ah2_downside_risk_defense_forensic_contract"):
        raise SystemExit("A7AH-0 does not authorize A7AH-2")

    clues = pd.read_csv(A7AG4_CLUES)
    downside = clues[clues["clue_role"].eq("downside_risk_defense_clue")].copy()
    if downside.empty:
        raise SystemExit("A7AH-2 requires downside_risk_defense_clue inputs")

    audit_rows = [
        {
            "audit_id": "D0_cost_ladder",
            "purpose": "separate 5bps pilot clues from 10/20bps robust risk-defense clues",
            "required_outputs": "cost5|cost10|cost20 survivor counts by candidate",
            "pass_signal": "risk-defense candidate survives >=10bps diagnostic and reports 20bps status",
        },
        {
            "audit_id": "D1_crash_state_conditioning",
            "purpose": "test whether downside clue is state-conditional rather than universal short-vol exposure",
            "required_outputs": "performance by drawdown/breadth/volatility state",
            "pass_signal": "benefit concentrated in adverse states without normal-state damage dominating",
        },
        {
            "audit_id": "D2_loss_hour_attribution",
            "purpose": "detect whether signal only avoids a few known loss hours",
            "required_outputs": "top gain/loss hour contribution and leave-one-month-out contribution",
            "pass_signal": "no single hour/month dominates",
        },
        {
            "audit_id": "D3_negative_controls_downside",
            "purpose": "ensure downside label is not trivially easier for wrong-lag/shuffle controls",
            "required_outputs": "matched controls by candidate and split",
            "pass_signal": "control ratio < 1 in all pre-May splits",
        },
        {
            "audit_id": "D4_overlay_boundary",
            "purpose": "prevent risk-defense clue from being promoted as ordinary alpha or live overlay",
            "required_outputs": "allowed/not-allowed use matrix",
            "pass_signal": "only forensic/risk-defense research remains authorized",
        },
    ]
    audit_plan = pd.DataFrame(audit_rows)
    seed_summary = (
        downside.groupby(["seed_field", "interaction_field"], dropna=False)
        .agg(
            clue_count=("candidate_id", "count"),
            skeleton_count=("skeleton_key", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            cost10_survivors=("survives_10bps_proxy", "sum"),
            cost20_survivors=("survives_20bps_proxy", "sum"),
        )
        .reset_index()
        .sort_values(["clue_count", "cost20_survivors"], ascending=False)
    )
    promotion_boundary = {
        "allowed": [
            "forensic audit",
            "risk-defense clue classification",
            "state-conditioned diagnostic",
        ],
        "not_allowed": [
            "ordinary alpha evidence",
            "standalone alpha proof",
            "shadow/paper/live overlay",
            "large search seed without A7AH2F pass",
        ],
        "required_before_any_risk_overlay_research": [
            "cost ladder pass",
            "state-conditioned downside benefit",
            "negative controls clean",
            "loss-hour/month concentration clean",
            "explicit ordinary alpha separation",
        ],
    }

    decision = "PASS_A7AH2_DOWNSIDE_RISK_DEFENSE_FORENSIC_CONTRACT_READY_FOR_A7AH2F"
    manifest = {
        "stage": "A7AH-2",
        "generated_at": now_utc(),
        "decision": decision,
        "input_a7ah0_decision": a7ah0.get("decision"),
        "executes_contract_only": True,
        "executes_formula_generation": False,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_a7ah2f_downside_forensic_audit": True,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may": False,
        "downside_clue_count": int(len(downside)),
        "downside_seed_pair_count": int(seed_summary[["seed_field", "interaction_field"]].drop_duplicates().shape[0]),
    }

    audit_plan.to_csv(RUNTIME / "a7ah2_forensic_audit_plan.csv", index=False)
    seed_summary.to_csv(RUNTIME / "a7ah2_downside_seed_pair_summary.csv", index=False)
    write_json(RUNTIME / "a7ah2_promotion_boundary.json", promotion_boundary)
    write_json(RUNTIME / "a7ah2_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ah2_authorization_matrix.json",
        {
            "A7AH-2": {"status": decision},
            "a7ah2f_downside_forensic_audit": {"authorized": True},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AH-2 DOWNSIDE RISK-DEFENSE FORENSIC CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AH-2 defines forensic work for downside/risk-defense clues. It does not promote them to ordinary alpha and does not execute search or replay.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Audit Plan",
        "",
        md_table(audit_plan),
        "",
        "## Downside Seed Pair Summary",
        "",
        md_table(seed_summary, 80),
        "",
        "## Promotion Boundary",
        "",
        "```json",
        json.dumps(promotion_boundary, indent=2, sort_keys=True),
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "A7AH-2 is risk-defense forensic only.",
        "It does not authorize ordinary alpha promotion, live overlay, alpha proof, or formula search.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
