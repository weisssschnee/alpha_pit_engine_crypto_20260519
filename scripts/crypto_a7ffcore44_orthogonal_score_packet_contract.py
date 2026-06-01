from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore44_orthogonal_score_packet_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE44_ORTHOGONAL_SCORE_PACKET_CONTRACT_20260602.md"
CORE43E = REPO / "runtime" / "a7ffcore43e_control_vector_rebuild_audit" / "a7ffcore43e_manifest.json"
CORE43E_ARTIFACT = (
    REPO
    / "runtime"
    / "a7ffcore43e_control_vector_rebuild_audit"
    / "a7ffcore43e_control_vector_artifact_manifest.csv"
)


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
    source = read_json(CORE43E)
    if source.get("decision") != "PASS_A7FFCORE43E_CONTROL_VECTOR_REBUILD_READY_FOR_CORE44":
        raise SystemExit(f"CORE43E not ready for CORE44: {source.get('decision')}")

    artifact = pd.read_csv(CORE43E_ARTIFACT) if CORE43E_ARTIFACT.exists() else pd.DataFrame()
    input_contract = pd.DataFrame(
        [
            {
                "input_id": "I0_core43e_full_universe_control_vector_sample",
                "path": source.get("external_sample_path"),
                "required": True,
                "status": "AVAILABLE" if source.get("external_sample_path") else "MISSING",
                "notes": "external parquet remains outside git; committed manifest references it",
            },
            {
                "input_id": "I1_core33_candidate_queue",
                "path": "runtime/a7ffcore33_bounded_replay_contract/a7ffcore33_replay_candidate_queue.csv",
                "required": True,
                "status": "AVAILABLE",
                "notes": "candidate metadata source; no stale selected packet reuse",
            },
        ]
    )
    packet_schema = pd.DataFrame(
        [
            {"field": "candidate_id", "level": "key", "required": True},
            {"field": "dataset", "level": "key", "required": True},
            {"field": "family_id", "level": "key", "required": True},
            {"field": "cluster_key", "level": "key", "required": True},
            {"field": "timestamp", "level": "key", "required": True},
            {"field": "symbol", "level": "key", "required": True},
            {"field": "split", "level": "key", "required": True},
            {"field": "quote_volume", "level": "liquidity", "required": True},
            {"field": "candidate_score_original", "level": "control_vector", "required": True},
            {"field": "candidate_score_stale", "level": "control_vector", "required": True},
            {"field": "candidate_score_sign_flip", "level": "control_vector", "required": True},
            {"field": "candidate_score_shuffle_time", "level": "control_vector", "required": True},
            {"field": "candidate_score_shuffle_symbol", "level": "control_vector", "required": True},
            {"field": "residual_score_stale_orthogonal", "level": "orthogonal_score", "required": True},
            {"field": "residual_score_null_orthogonal", "level": "orthogonal_score", "required": True},
            {"field": "selected_score_variant", "level": "policy", "required": True},
            {"field": "book_rank", "level": "book_input", "required": True},
            {"field": "book_side", "level": "book_input", "required": True},
            {"field": "book_weight", "level": "book_input", "required": True},
            {"field": "control_margin_metadata", "level": "diagnostic", "required": True},
        ]
    )
    construction_policy = pd.DataFrame(
        [
            {
                "policy_id": "P0_full_universe_before_selection",
                "description": "compute residual scores over full timestamp-symbol universe before any top/bottom selection",
                "hard_requirement": True,
            },
            {
                "policy_id": "P1_primary_score_variant",
                "description": "use residual_score_null_orthogonal as primary book ranking score; stale-only residual is diagnostic fallback only",
                "hard_requirement": True,
            },
            {
                "policy_id": "P2_train_only_orientation",
                "description": "if orientation is required, fit sign only on train_2024 and apply unchanged to validation/test/recent",
                "hard_requirement": True,
            },
            {
                "policy_id": "P3_control_margin_required",
                "description": "book packet must retain original/stale/sign/shuffle score ranks for control dominance checks",
                "hard_requirement": True,
            },
            {
                "policy_id": "P4_no_selected_packet_backfill",
                "description": "CORE39E selected top/bottom packet must not be used as orthogonalization input",
                "hard_requirement": True,
            },
            {
                "policy_id": "P5_no_search",
                "description": "CORE44 and CORE44E do not authorize formula generation, formula search, large search, proof, shadow, paper, or live",
                "hard_requirement": True,
            },
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE44E",
                "action": "construct bounded orthogonal score packet from CORE43E full-universe vectors",
                "executes_new_generation": False,
                "executes_search": False,
                "writes_large_artifact_to_git": False,
            },
            {
                "stage": "A7FF-CORE45",
                "action": "if CORE44E passes, define bounded orthogonal book replay contract",
                "executes_new_generation": False,
                "executes_search": False,
                "writes_large_artifact_to_git": False,
            },
        ]
    )
    authorization = {
        "authorized": {"A7FF-CORE44E orthogonal score packet construction audit": True},
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "new_generation": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
            "selected_packet_control_orthogonalization": True,
        },
    }
    decision = "PASS_A7FFCORE44_ORTHOGONAL_SCORE_PACKET_CONTRACT_READY_FOR_CORE44E"
    manifest = {
        "stage": "A7FF-CORE44",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE43E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "source_vector_sample_rows": source.get("vector_sample_rows"),
        "source_vector_sample_columns": source.get("vector_sample_columns"),
        "source_external_sample_path": source.get("external_sample_path"),
        "executes_new_generation": False,
        "executes_search": False,
        "authorizes_core44e_packet_construction": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE44E orthogonal score packet construction audit",
    }
    input_contract.to_csv(RUNTIME / "a7ffcore44_input_contract.csv", index=False)
    packet_schema.to_csv(RUNTIME / "a7ffcore44_orthogonal_packet_schema.csv", index=False)
    construction_policy.to_csv(RUNTIME / "a7ffcore44_construction_policy.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ffcore44_execution_plan.csv", index=False)
    artifact.to_csv(RUNTIME / "a7ffcore44_source_artifact_manifest_copy.csv", index=False)
    write_json(RUNTIME / "a7ffcore44_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore44_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE44 ORTHOGONAL SCORE PACKET CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE44 defines how to turn CORE43E full-universe control vectors into an orthogonal score packet. It is a contract only and does not execute replay, generation, search, proof, shadow, paper, or live.",
        "",
        "## Input Contract",
        "",
        md_table(input_contract),
        "",
        "## Packet Schema",
        "",
        md_table(packet_schema),
        "",
        "## Construction Policy",
        "",
        md_table(construction_policy),
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
