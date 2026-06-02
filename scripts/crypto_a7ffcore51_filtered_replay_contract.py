from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore51_filtered_replay_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE51_FILTERED_REPLAY_CONTRACT_20260602.md"
CORE50 = REPO / "runtime" / "a7ffcore50_null_vector_preflight_arbitration" / "a7ffcore50_manifest.json"
FILTERED = REPO / "runtime" / "a7ffcore50_null_vector_preflight_arbitration" / "a7ffcore50_filtered_seed_preview.csv"


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
    source = read_json(CORE50)
    if source.get("decision") != "PASS_A7FFCORE50_NULL_VECTOR_ARBITRATION_READY_FOR_CORE51_FILTERED_REPLAY_CONTRACT":
        raise SystemExit(f"CORE50 not ready for CORE51: {source.get('decision')}")
    filtered = pd.read_csv(FILTERED)

    input_sources = pd.DataFrame(
        [
            {
                "input_id": "I0_core50_filtered_seed_preview",
                "path": "runtime/a7ffcore50_null_vector_preflight_arbitration/a7ffcore50_filtered_seed_preview.csv",
                "role": "source-of-truth replay candidate queue",
                "required": True,
            },
            {
                "input_id": "I1_core49e_vector_metrics",
                "path": "runtime/a7ffcore49e_full_universe_null_vector_preflight_execution/a7ffcore49e_seed_vector_metrics.csv",
                "role": "materialization and null-vector diagnostics",
                "required": True,
            },
            {
                "input_id": "I2_universe498_panel",
                "path": "G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v2_20260527",
                "role": "market/metrics panel for replay labels and costs",
                "required": True,
            },
            {
                "input_id": "I3_latent_state_panel",
                "path": "G:/AlphaFactory_CryptoData/gold/features/binance_universe498_latent_state_features_v1_20260527.parquet",
                "role": "latent/liquidity/listing neutralization support",
                "required": True,
            },
        ]
    )
    replay_candidate_policy = pd.DataFrame(
        [
            {"gate": "materialization_status", "rule": "must pass CORE49E", "hard_gate": True},
            {"gate": "null_vector_filter", "rule": "must pass CORE50 active/symbol/time-shuffle filters", "hard_gate": True},
            {"gate": "semantic_pair_cap", "rule": "selected replay queue share <= 0.25", "hard_gate": True},
            {"gate": "operator_cap", "rule": "selected replay queue share <= 0.25", "hard_gate": True},
            {"gate": "stale_risk_balance", "rule": "include low/medium/high stale-risk tiers; high tier is allowed but capped", "hard_gate": True},
            {"gate": "non_label_source", "rule": "May/stress labels cannot enter selection/ranking/scoring", "hard_gate": True},
            {"gate": "control_dominance", "rule": "matched null controls must be reported per split and can veto promotion", "hard_gate": True},
        ]
    )
    replay_design = pd.DataFrame(
        [
            {
                "design_id": "D0_filtered_queue_replay",
                "candidate_input_count": int(filtered.shape[0]),
                "max_replay_candidates": 384,
                "selection_method": "balanced by semantic_pair, operator, stale_risk_tier, and active_ratio quartile",
                "executes_replay_in_contract": False,
            },
            {
                "design_id": "D1_control_book",
                "candidate_input_count": int(filtered.shape[0]),
                "max_replay_candidates": 384,
                "selection_method": "same selected expressions with stale/sign/time/symbol null vectors",
                "executes_replay_in_contract": False,
            },
        ]
    )
    label_and_cost_policy = pd.DataFrame(
        [
            {"item": "label_horizons", "policy": "1h/4h/8h/24h forward labels; report separately"},
            {"item": "primary_labels", "policy": "L0 raw, L1 cross-sectional relative, L3 liquidity-tier relative, L5 vol-adjusted; L7 ranked label cannot dominate"},
            {"item": "cost_proxy", "policy": "2bps/5bps/10bps proxy tiers; no promotion if only 0-cost survives"},
            {"item": "neutralization", "policy": "global, liquidity-tier, latent-state, major/meme/multiplier diagnostics"},
            {"item": "stats", "policy": "non-overlap offset stats and block/Newey-West style robust t-stat where available"},
            {"item": "stress_policy", "policy": "known stress may be post-selection veto/attribution only; never ranking input"},
        ]
    )
    pass_gate = pd.DataFrame(
        [
            {"gate": "selected_candidate_count", "threshold": ">= 128 for CORE51E"},
            {"gate": "selected_semantic_pair_count", "threshold": ">= 20"},
            {"gate": "selected_operator_count", "threshold": ">= 5"},
            {"gate": "top_semantic_pair_share", "threshold": "<= 0.25"},
            {"gate": "top_operator_share", "threshold": "<= 0.25"},
            {"gate": "selected_non_l7_evidence", "threshold": "must be present; L7-only cannot pass"},
            {"gate": "matched_null_controls", "threshold": "controls must be weaker than original for promotion"},
        ]
    )
    candidate_summary = pd.DataFrame(
        [
            {"metric": "filtered_candidate_count", "value": int(filtered.shape[0])},
            {"metric": "semantic_pair_count", "value": int(filtered["semantic_pair"].nunique())},
            {"metric": "operator_count", "value": int(filtered["operator"].nunique())},
            {"metric": "stale_risk_tier_count", "value": int(filtered["stale_risk_tier"].nunique())},
        ]
    )
    authorization = {
        "authorized": {
            "A7FF-CORE51E filtered replay preflight/execution": True,
        },
        "not_authorized": {
            "large_search": True,
            "formula_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
            "direct_live_replay_without_controls": True,
        },
    }
    decision = "PASS_A7FFCORE51_FILTERED_REPLAY_CONTRACT_READY_FOR_CORE51E"
    manifest = {
        "stage": "A7FF-CORE51",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE50",
        "source_decision": source.get("decision"),
        "decision": decision,
        "filtered_candidate_count": int(filtered.shape[0]),
        "semantic_pair_count": int(filtered["semantic_pair"].nunique()),
        "operator_count": int(filtered["operator"].nunique()),
        "executes_replay": False,
        "executes_search": False,
        "executes_generation": False,
        "authorizes_core51e_filtered_replay": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE51E filtered replay preflight/execution",
    }

    input_sources.to_csv(RUNTIME / "a7ffcore51_input_sources.csv", index=False)
    replay_candidate_policy.to_csv(RUNTIME / "a7ffcore51_replay_candidate_policy.csv", index=False)
    replay_design.to_csv(RUNTIME / "a7ffcore51_replay_design.csv", index=False)
    label_and_cost_policy.to_csv(RUNTIME / "a7ffcore51_label_and_cost_policy.csv", index=False)
    pass_gate.to_csv(RUNTIME / "a7ffcore51_pass_gate.csv", index=False)
    candidate_summary.to_csv(RUNTIME / "a7ffcore51_candidate_summary.csv", index=False)
    write_json(RUNTIME / "a7ffcore51_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore51_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE51 FILTERED REPLAY CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE51 defines the filtered replay contract after CORE50 null-vector arbitration. It does not execute replay/search/proof/promotion.",
        "",
        "## Candidate Summary",
        "",
        md_table(candidate_summary),
        "",
        "## Input Sources",
        "",
        md_table(input_sources),
        "",
        "## Replay Candidate Policy",
        "",
        md_table(replay_candidate_policy),
        "",
        "## Replay Design",
        "",
        md_table(replay_design),
        "",
        "## Label And Cost Policy",
        "",
        md_table(label_and_cost_policy),
        "",
        "## Pass Gate",
        "",
        md_table(pass_gate),
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
