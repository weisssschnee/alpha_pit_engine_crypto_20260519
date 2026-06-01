from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore11_small_expansion_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE11_SMALL_EXPANSION_CONTRACT_20260601.md"
A7FFCORE10E = REPO / "runtime" / "a7ffcore10e_search_readiness_audit" / "a7ffcore10e_manifest.json"
SEED_POOL = REPO / "runtime" / "a7ffcore10e_search_readiness_audit" / "a7ffcore10e_search_ready_seed_pool.csv"


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
    core10e = read_json(A7FFCORE10E)
    if core10e.get("decision") != "PASS_A7FFCORE10E_READY_FOR_CORE11_SMALL_SEARCH_CONTRACT":
        raise SystemExit(f"A7FF-CORE10E is not ready: {core10e.get('decision')}")
    seeds = pd.read_csv(SEED_POOL)
    family_budget = (
        seeds.groupby(["semantic_bucket", "motif_bucket"], dropna=False)
        .agg(seed_count=("candidate_id", "nunique"), max_tstat=("max_tstat", "max"), median_control_ratio=("replay_min_control_ratio", "median"))
        .reset_index()
        .sort_values(["seed_count", "max_tstat"], ascending=[False, False])
    )
    family_budget["generated_budget"] = (4000 * family_budget["seed_count"] / max(1, family_budget["seed_count"].sum())).round().astype(int).clip(lower=80)
    diff = 4000 - int(family_budget["generated_budget"].sum())
    if diff != 0 and not family_budget.empty:
        family_budget.loc[family_budget.index[0], "generated_budget"] += diff

    grammar = {
        "allowed_transforms": ["Mean", "Delta", "ZScore", "Rank", "CSRank", "TSRank", "SafeDiv", "Mul", "Sub", "Add", "Neg", "Abs", "Sign", "Clip", "Decay"],
        "allowed_window_set": [4, 8, 12, 24, 48, 72, 168, 336],
        "mutation_modes": [
            "window_neighbor",
            "operator_neighbor",
            "seed_field_sibling",
            "semantic_pair_preserving_interaction",
            "motif_preserving_simplification",
            "motif_preserving_complexification_depth_lte_4",
        ],
        "forbidden": [
            "raw expression construction bypassing typed AST gate",
            "legacy quarantined generator entrypoints",
            "May-informed thresholds or masks",
            "label/future/target fields",
            "sign_flip as max-control dominance",
            "full open FormulaGenV2 grammar",
            "large search budget",
        ],
    }
    execution_plan = {
        "generated_total": 4000,
        "materialization_preflight": 512,
        "numeric_response": 256,
        "bounded_replay": 64,
        "primary_labels": ["L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"],
        "horizons": [1, 4, 8, 24],
        "cost_bps": [0, 2, 5, 10],
        "controls": ["wrong_lag_future", "wrong_lag_stale", "time_shuffle", "symbol_shuffle", "same_family_placebo"],
        "selection_caps": {
            "top_semantic_bucket_share": 0.35,
            "top_motif_bucket_share": 0.35,
            "top_skeleton_share": 0.20,
            "top_signal_vector_cluster_share": 0.25,
        },
    }
    pass_gates = {
        "materialization_eval_errors": 0,
        "numeric_primary_non_l7_clue_candidates_min": 64,
        "bounded_replay_clean_candidates_min": 16,
        "bounded_replay_clean_semantic_buckets_min": 5,
        "bounded_replay_clean_motif_buckets_min": 5,
        "control_ratio_lt_1_required": True,
        "large_search_authorization": False,
    }
    family_budget.to_csv(RUNTIME / "a7ffcore11_family_budget.csv", index=False)
    seeds.to_csv(RUNTIME / "a7ffcore11_seed_pool.csv", index=False)
    write_json(RUNTIME / "a7ffcore11_grammar_contract.json", grammar)
    write_json(RUNTIME / "a7ffcore11_execution_plan.json", execution_plan)
    write_json(RUNTIME / "a7ffcore11_pass_gates.json", pass_gates)
    authorization = {
        "A7FF-CORE11E small gate-native dry generation": True,
        "A7FF-CORE11F materialization preflight": False,
        "A7FF-CORE11G numeric response": False,
        "large_search": False,
        "alpha_proof": False,
        "shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffcore11_authorization_matrix.json", authorization)
    manifest = {
        "stage": "A7FF-CORE11",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE10E",
        "source_decision": core10e.get("decision"),
        "decision": "PASS_A7FFCORE11_SMALL_EXPANSION_CONTRACT_READY_FOR_CORE11E",
        "seed_candidate_count": int(len(seeds)),
        "semantic_bucket_count": int(seeds["semantic_bucket"].nunique()),
        "motif_bucket_count": int(seeds["motif_bucket"].nunique()),
        "generated_total_budget": 4000,
        "authorizes_core11e": True,
        "authorizes_materialization_execution": False,
        "authorizes_numeric_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE11E small gate-native dry generation",
    }
    write_json(RUNTIME / "a7ffcore11_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE11 SMALL GATE-NATIVE EXPANSION CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        "`PASS_A7FFCORE11_SMALL_EXPANSION_CONTRACT_READY_FOR_CORE11E`",
        "",
        "A7FF-CORE11 defines a small gate-native formula expansion from replay-clean seeds. It does not execute generation, materialization, numeric response, replay, large search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Budget",
        "",
        md_table(family_budget),
        "",
        "## Grammar Contract",
        "",
        "```json",
        json.dumps(grammar, indent=2, sort_keys=True),
        "```",
        "",
        "## Execution Plan",
        "",
        "```json",
        json.dumps(execution_plan, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
