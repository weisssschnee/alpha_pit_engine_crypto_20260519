from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore39_symbol_level_book_packet_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE39_SYMBOL_LEVEL_BOOK_PACKET_CONTRACT_20260602.md"
CORE38E = REPO / "runtime" / "a7ffcore38e_portfolio_label_objective_audit" / "a7ffcore38e_manifest.json"


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
    source = read_json(CORE38E)
    if source.get("decision") != "HOLD_A7FFCORE38E_BOOK_OBJECTIVE_AUDIT_REQUIRES_SYMBOL_LEVEL_REPLAY_INPUT":
        raise SystemExit(f"CORE38E not ready for CORE39: {source.get('decision')}")

    packet_schema = pd.DataFrame(
        [
            {"field": "candidate_id", "required": True, "role": "key", "note": "stable candidate id"},
            {"field": "timestamp", "required": True, "role": "key", "note": "feature timestamp / decision timestamp"},
            {"field": "feature_available_time", "required": True, "role": "timing", "note": "must be <= execution timestamp"},
            {"field": "execution_time", "required": True, "role": "timing", "note": "book entry timestamp"},
            {"field": "symbol", "required": True, "role": "key", "note": "instrument id"},
            {"field": "split", "required": True, "role": "evaluation", "note": "train/validation/test/recent"},
            {"field": "family_id", "required": True, "role": "candidate_metadata", "note": "data family / motif group"},
            {"field": "cluster_key", "required": True, "role": "candidate_metadata", "note": "diversity and dedup key"},
            {"field": "label_id", "required": True, "role": "label", "note": "L1/L2/L3/L5 primary labels"},
            {"field": "horizon_h", "required": True, "role": "label", "note": "book horizon"},
            {"field": "candidate_score", "required": True, "role": "signal", "note": "symbol-level formula score before ranking"},
            {"field": "candidate_rank", "required": True, "role": "signal", "note": "cross-sectional rank at timestamp"},
            {"field": "raw_weight", "required": True, "role": "portfolio", "note": "top/bottom book weight before caps"},
            {"field": "capped_weight", "required": True, "role": "portfolio", "note": "after symbol/liquidity/family caps"},
            {"field": "side", "required": True, "role": "portfolio", "note": "long/short/flat"},
            {"field": "forward_return", "required": True, "role": "label", "note": "raw return"},
            {"field": "cs_relative_return", "required": True, "role": "label", "note": "cross-sectional relative return"},
            {"field": "market_beta_residual_return", "required": True, "role": "label", "note": "BTC/ETH/market residual"},
            {"field": "liquidity_tier_relative_return", "required": True, "role": "label", "note": "within liquidity tier"},
            {"field": "vol_adjusted_return", "required": True, "role": "label", "note": "return normalized by realized vol"},
            {"field": "quote_volume", "required": True, "role": "cost_capacity", "note": "liquidity cap input"},
            {"field": "turnover_proxy", "required": True, "role": "cost_capacity", "note": "turnover/cost proxy"},
            {"field": "cost_bps", "required": True, "role": "cost_capacity", "note": "2/5/10 bps variants"},
            {"field": "control_variant", "required": True, "role": "control", "note": "original/wrong_lag/stale/shuffle/sign_flip"},
        ]
    )
    build_requirements = pd.DataFrame(
        [
            {"requirement": "symbol_level_materialization", "description": "candidate_score must be emitted per candidate/timestamp/symbol before aggregation", "hard_gate": True},
            {"requirement": "point_in_time_timing", "description": "feature_available_time and execution_time must be explicit", "hard_gate": True},
            {"requirement": "book_weight_trace", "description": "raw and capped weights must be retained for every selected symbol", "hard_gate": True},
            {"requirement": "primary_label_panel", "description": "L1/L2/L3/L5 labels must be available at symbol level", "hard_gate": True},
            {"requirement": "control_packet", "description": "wrong-lag/stale/shuffle/sign-flip controls must be materialized with same schema", "hard_gate": True},
            {"requirement": "aggregation_reproducibility", "description": "aggregate spread rows must be reproducible from the symbol-level packet", "hard_gate": True},
        ]
    )
    packet_outputs = pd.DataFrame(
        [
            {"artifact": "a7ffcore39e_symbol_level_score_packet.parquet", "purpose": "raw symbol-level candidate scores and labels"},
            {"artifact": "a7ffcore39e_book_weight_trace.parquet", "purpose": "long/short/capped weights and cost inputs"},
            {"artifact": "a7ffcore39e_control_packet.parquet", "purpose": "matched control variants with identical schema"},
            {"artifact": "a7ffcore39e_aggregate_replay_reconciliation.csv", "purpose": "prove aggregate replay can be reconstructed"},
            {"artifact": "a7ffcore39e_packet_quality_audit.csv", "purpose": "missingness, NaN/inf, timing, coverage, cap audit"},
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE39E",
                "action": "construct a bounded symbol-level packet for existing CORE33 candidate queue",
                "scope": "existing candidates only; no new formula generation; no search",
            },
            {
                "stage": "A7FF-CORE40",
                "action": "if CORE39E packet passes, define bounded book-objective replay execution",
                "scope": "contract only until explicitly authorized",
            },
        ]
    )
    authorization = {
        "authorized": {"A7FF-CORE39E symbol-level book packet construction audit": True},
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
            "book_objective_replay_execution": True,
        },
    }
    decision = "PASS_A7FFCORE39_SYMBOL_LEVEL_BOOK_PACKET_CONTRACT_READY_FOR_CORE39E"
    manifest = {
        "stage": "A7FF-CORE39",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE38E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "required_packet_fields": int(packet_schema.shape[0]),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core39e_packet_audit": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE39E symbol-level book packet construction audit",
    }
    packet_schema.to_csv(RUNTIME / "a7ffcore39_symbol_level_packet_schema.csv", index=False)
    build_requirements.to_csv(RUNTIME / "a7ffcore39_packet_build_requirements.csv", index=False)
    packet_outputs.to_csv(RUNTIME / "a7ffcore39_expected_outputs.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore39_execution_plan.csv", index=False)
    write_json(RUNTIME / "a7ffcore39_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore39_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE39 SYMBOL-LEVEL BOOK PACKET CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE39 defines the symbol-level packet required to compute CORE38 portfolio/book objectives. It does not run replay, generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Packet Schema",
        "",
        md_table(packet_schema),
        "",
        "## Build Requirements",
        "",
        md_table(build_requirements),
        "",
        "## Expected Outputs",
        "",
        md_table(packet_outputs),
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
