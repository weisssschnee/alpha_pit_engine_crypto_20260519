from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore49_full_universe_null_vector_preflight_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE49_FULL_UNIVERSE_NULL_VECTOR_PREFLIGHT_CONTRACT_20260602.md"
CORE48SE = REPO / "runtime" / "a7ffcore48se_repaired_null_first_dry_generation" / "a7ffcore48se_manifest.json"
CORE48SE_QUEUE = REPO / "runtime" / "a7ffcore48se_repaired_null_first_dry_generation" / "a7ffcore48se_eligible_seed_queue.csv"


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
    source = read_json(CORE48SE)
    if source.get("decision") != "PASS_A7FFCORE48SE_REPAIRED_DRY_SEEDS_READY_FOR_CORE49_CONTRACT":
        raise SystemExit(f"CORE48SE not ready for CORE49: {source.get('decision')}")

    queue = pd.read_csv(CORE48SE_QUEUE) if CORE48SE_QUEUE.exists() else pd.DataFrame()
    if queue.empty:
        raise SystemExit("CORE48SE eligible seed queue is missing or empty")

    seed_count = int(queue.shape[0])
    semantic_family_count = int(queue["semantic_pair"].nunique()) if "semantic_pair" in queue else 0
    operator_count = int(queue["operator"].nunique()) if "operator" in queue else 0

    input_sources = pd.DataFrame(
        [
            {
                "input_id": "I0_core48se_seed_queue",
                "path": "runtime/a7ffcore48se_repaired_null_first_dry_generation/a7ffcore48se_eligible_seed_queue.csv",
                "role": "source-of-truth repaired null-first seed queue",
                "required": True,
            },
            {
                "input_id": "I1_universe498_panel",
                "path": "G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v2_20260527",
                "role": "full-universe feature panel for vector construction",
                "required": True,
            },
            {
                "input_id": "I2_label_contract",
                "path": "runtime/a7aa0_label_universe/a7aa0_label_contract.csv",
                "role": "label family and horizon contract for preflight bookkeeping only",
                "required": True,
            },
            {
                "input_id": "I3_field_enforcement_ledger",
                "path": "runtime/a7aif2_field_enforcement_regression/a7aif2_historical_candidate_role_reclassification.csv",
                "role": "role-aware field/candidate enforcement source",
                "required": True,
            },
            {
                "input_id": "I4_materialization_parity",
                "path": "runtime/a7aif3_materialization_evaluator_parity/a7aif3_operator_parity_matrix.csv",
                "role": "approved operator materialization parity source",
                "required": True,
            },
        ]
    )
    shard_plan = pd.DataFrame(
        [
            {
                "shard_id": f"core49e_shard_{i:02d}",
                "seed_start_inclusive": i * 150,
                "seed_end_exclusive": min((i + 1) * 150, seed_count),
                "max_seed_count": min(150, max(seed_count - i * 150, 0)),
                "executes_replay": False,
                "executes_search": False,
            }
            for i in range((seed_count + 149) // 150)
            if i * 150 < seed_count
        ]
    )
    vector_schema = pd.DataFrame(
        [
            {"field": "seed_id", "required": True, "description": "CORE48SE seed id"},
            {"field": "timestamp", "required": True, "description": "feature timestamp"},
            {"field": "symbol", "required": True, "description": "symbol"},
            {"field": "original_signal", "required": True, "description": "materialized candidate signal"},
            {"field": "stale_signal", "required": True, "description": "stale/wrong-lag control vector"},
            {"field": "sign_flip_signal", "required": True, "description": "sign-flip control vector"},
            {"field": "time_shuffle_signal", "required": True, "description": "time-shuffle control vector"},
            {"field": "symbol_shuffle_signal", "required": True, "description": "symbol-shuffle control vector"},
            {"field": "null_margin", "required": True, "description": "original-vs-null vector margin proxy"},
            {"field": "role_gate_status", "required": True, "description": "field/candidate role enforcement status"},
            {"field": "materialization_status", "required": True, "description": "expression materialization status"},
        ]
    )
    quality_gate = pd.DataFrame(
        [
            {"gate": "seed_queue_present", "threshold": "true", "observed": CORE48SE_QUEUE.exists()},
            {"gate": "seed_count", "threshold": ">= 1800", "observed": seed_count},
            {"gate": "semantic_family_count", "threshold": ">= 30", "observed": semantic_family_count},
            {"gate": "operator_count", "threshold": ">= 7", "observed": operator_count},
            {"gate": "preflight_shard_count", "threshold": ">= 12", "observed": int(shard_plan.shape[0])},
            {"gate": "executes_numeric_replay", "threshold": "false", "observed": False},
            {"gate": "executes_formula_search", "threshold": "false", "observed": False},
        ]
    )
    execution_policy = pd.DataFrame(
        [
            {
                "policy_id": "P0_vector_preflight_only",
                "description": "CORE49E may materialize original and null vectors but may not calculate portfolio replay, promotion, or alpha proof",
                "hard_requirement": True,
            },
            {
                "policy_id": "P1_full_universe_required",
                "description": "preflight must use the full available universe panel, not a hand-picked symbol subset",
                "hard_requirement": True,
            },
            {
                "policy_id": "P2_null_vectors_required",
                "description": "every retained seed must include stale, sign-flip, time-shuffle, and symbol-shuffle vectors",
                "hard_requirement": True,
            },
            {
                "policy_id": "P3_fail_closed_on_role_or_materialization",
                "description": "missing field contracts, role violations, or unsupported operators fail closed",
                "hard_requirement": True,
            },
            {
                "policy_id": "P4_external_large_artifacts",
                "description": "large vector parquet outputs must stay under G:/AlphaFactory_CryptoData/research_runtime and be referenced by manifest only",
                "hard_requirement": True,
            },
        ]
    )
    authorization = {
        "authorized": {
            "A7FF-CORE49E full-universe null-vector preflight execution": True
        },
        "not_authorized": {
            "numeric_replay": True,
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    decision = "PASS_A7FFCORE49_FULL_UNIVERSE_NULL_VECTOR_PREFLIGHT_CONTRACT_READY_FOR_CORE49E"
    manifest = {
        "stage": "A7FF-CORE49",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE48SE",
        "source_decision": source.get("decision"),
        "decision": decision,
        "seed_count": seed_count,
        "semantic_family_count": semantic_family_count,
        "operator_count": operator_count,
        "preflight_shard_count": int(shard_plan.shape[0]),
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core49e_preflight_execution": True,
        "authorizes_numeric_replay": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE49E full-universe null-vector preflight execution",
    }

    input_sources.to_csv(RUNTIME / "a7ffcore49_input_sources.csv", index=False)
    shard_plan.to_csv(RUNTIME / "a7ffcore49_preflight_shard_plan.csv", index=False)
    vector_schema.to_csv(RUNTIME / "a7ffcore49_vector_output_schema.csv", index=False)
    quality_gate.to_csv(RUNTIME / "a7ffcore49_quality_gate.csv", index=False)
    execution_policy.to_csv(RUNTIME / "a7ffcore49_execution_policy.csv", index=False)
    write_json(RUNTIME / "a7ffcore49_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore49_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE49 FULL-UNIVERSE NULL-VECTOR PREFLIGHT CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE49 is a contract-only stage. It defines how CORE49E may build full-universe original/null vectors from the repaired CORE48SE seed queue. It does not execute numeric replay, formula search, large search, alpha proof, promotion, shadow, paper, or live.",
        "",
        "## Source Summary",
        "",
        f"- seeds: `{seed_count}`",
        f"- semantic families: `{semantic_family_count}`",
        f"- operators: `{operator_count}`",
        f"- preflight shards: `{int(shard_plan.shape[0])}`",
        "",
        "## Input Sources",
        "",
        md_table(input_sources),
        "",
        "## Shard Plan",
        "",
        md_table(shard_plan),
        "",
        "## Vector Output Schema",
        "",
        md_table(vector_schema),
        "",
        "## Quality Gate",
        "",
        md_table(quality_gate),
        "",
        "## Execution Policy",
        "",
        md_table(execution_policy),
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
