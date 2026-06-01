from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore45_orthogonal_book_replay_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE45_ORTHOGONAL_BOOK_REPLAY_CONTRACT_20260602.md"
CORE44E = REPO / "runtime" / "a7ffcore44e_orthogonal_score_packet_construction" / "a7ffcore44e_manifest.json"


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
    source = read_json(CORE44E)
    if source.get("decision") != "PASS_A7FFCORE44E_ORTHOGONAL_SCORE_PACKET_READY_FOR_CORE45_CONTRACT":
        raise SystemExit(f"CORE44E not ready for CORE45: {source.get('decision')}")

    replay_objectives = pd.DataFrame(
        [
            {
                "objective_id": "OB1_cross_sectional_relative_book",
                "label_column": "cs_relative_return",
                "description": "long/short book return using cross-sectional relative return",
                "primary": True,
            },
            {
                "objective_id": "OB2_market_beta_residual_book",
                "label_column": "market_beta_residual_return",
                "description": "book return after BTC/ETH market residual label",
                "primary": True,
            },
            {
                "objective_id": "OB3_liquidity_tier_relative_book",
                "label_column": "liquidity_tier_relative_return",
                "description": "book return relative to timestamp liquidity tier",
                "primary": True,
            },
            {
                "objective_id": "OB4_vol_adjusted_book",
                "label_column": "vol_adjusted_return",
                "description": "vol-adjusted book return diagnostic",
                "primary": False,
            },
        ]
    )
    replay_policy = pd.DataFrame(
        [
            {
                "policy_id": "P0_use_core44e_packet_only",
                "description": "CORE45E must use CORE44E orthogonal packet and must not use CORE39E selected packet",
                "hard_requirement": True,
            },
            {
                "policy_id": "P1_recompute_labels_from_panel",
                "description": "CORE45E must attach labels from panel data at replay time; CORE44E packet contains scores/weights only",
                "hard_requirement": True,
            },
            {
                "policy_id": "P2_split_separated_reporting",
                "description": "report train/validation/test/recent separately before any aggregate metric",
                "hard_requirement": True,
            },
            {
                "policy_id": "P3_control_rank_margin",
                "description": "compare residual book against original/stale/sign/shuffle rank books where possible",
                "hard_requirement": True,
            },
            {
                "policy_id": "P4_no_search_or_promotion",
                "description": "CORE45/CORE45E do not authorize formula generation, search, proof, shadow, paper, or live",
                "hard_requirement": True,
            },
        ]
    )
    pass_gate = pd.DataFrame(
        [
            {"gate": "packet_rows_positive", "threshold": "packet_rows > 0"},
            {"gate": "candidate_count_positive", "threshold": "candidate_count >= 4"},
            {"gate": "split_coverage", "threshold": "train/validation/test/recent reported separately"},
            {"gate": "net_book_positive", "threshold": "median net book return > 0 in at least two pre-recent splits"},
            {"gate": "control_margin", "threshold": "residual book must beat stale/sign/shuffle controls"},
            {"gate": "family_breadth", "threshold": "survivors from >=2 families required for any later expansion"},
        ]
    )
    horizon_policy = pd.DataFrame(
        [
            {
                "horizon_h": 8,
                "role": "primary_short_horizon",
                "description": "shorter executable horizon used by prior CORE39/40 book packet diagnostics",
            },
            {
                "horizon_h": 24,
                "role": "primary_slow_horizon",
                "description": "slower executable horizon used by prior CORE39/40 book packet diagnostics",
            },
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE45E",
                "action": "bounded orthogonal book replay execution over CORE44E packet",
                "executes_replay": True,
                "executes_search": False,
                "writes_large_artifact_to_git": False,
            },
            {
                "stage": "A7FF-CORE45R",
                "action": "if CORE45E holds, classify replay/control failure",
                "executes_replay": False,
                "executes_search": False,
                "writes_large_artifact_to_git": False,
            },
        ]
    )
    authorization = {
        "authorized": {"A7FF-CORE45E bounded orthogonal book replay execution": True},
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "new_generation": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
            "promotion": True,
        },
    }
    decision = "PASS_A7FFCORE45_ORTHOGONAL_BOOK_REPLAY_CONTRACT_READY_FOR_CORE45E"
    manifest = {
        "stage": "A7FF-CORE45",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE44E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "source_packet_rows": source.get("packet_rows"),
        "source_external_packet_path": source.get("external_packet_path"),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core45e_replay_execution": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE45E bounded orthogonal book replay execution",
    }
    replay_objectives.to_csv(RUNTIME / "a7ffcore45_replay_objectives.csv", index=False)
    horizon_policy.to_csv(RUNTIME / "a7ffcore45_horizon_policy.csv", index=False)
    replay_policy.to_csv(RUNTIME / "a7ffcore45_replay_policy.csv", index=False)
    pass_gate.to_csv(RUNTIME / "a7ffcore45_pass_gate.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore45_execution_plan.csv", index=False)
    write_json(RUNTIME / "a7ffcore45_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore45_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE45 ORTHOGONAL BOOK REPLAY CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE45 defines bounded book replay over the CORE44E orthogonal score packet. It does not execute replay itself and does not authorize formula generation, large search, alpha proof, shadow, paper, live, or promotion.",
        "",
        "## Replay Objectives",
        "",
        md_table(replay_objectives),
        "",
        "## Horizon Policy",
        "",
        md_table(horizon_policy),
        "",
        "## Replay Policy",
        "",
        md_table(replay_policy),
        "",
        "## Pass Gate",
        "",
        md_table(pass_gate),
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
