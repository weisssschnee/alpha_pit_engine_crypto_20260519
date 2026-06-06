from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ls16x_scale_up_authorization"
REPORT = REPO / "reports" / "CRYPTO_A7LS16X_SCALE_UP_AUTHORIZATION_20260606.md"
A7LS14X = REPO / "runtime" / "a7ls14x_authorization_arbitration" / "a7ls14x_manifest.json"
A7LS15 = REPO / "runtime" / "a7ls15_million_scale_blueprint_generation" / "a7ls15_manifest.json"
A7LS16 = REPO / "runtime" / "a7ls16_local_preflight" / "a7ls16_manifest.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def build() -> dict[str, Any]:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ls14x = read_json(A7LS14X)
    a7ls15 = read_json(A7LS15)
    a7ls16 = read_json(A7LS16)

    blockers: list[str] = []
    if a7ls14x.get("decision") != "PASS_A7LS14X_CHECKPOINT_LARGE_SEARCH_AUTHORIZATION_ARBITRATED":
        blockers.append("a7ls14x_scoped_authorization_not_ready")
    if a7ls15.get("decision") != "PASS_A7LS15_MILLION_SCALE_BLUEPRINT_GENERATION_READY_FOR_A7LS16":
        blockers.append("a7ls15_blueprint_generation_not_ready")
    if a7ls16.get("decision") != "PASS_A7LS16_LOCAL_SCHEMA_PREFLIGHT_READY_FOR_A7LS17_COMPANY_MATERIALIZATION":
        blockers.append("a7ls16_preflight_not_ready")

    lanes = pd.DataFrame(
        [
            {
                "lane_id": "A7LS16X_A",
                "lane_name": "evidence_exploitation_deep",
                "search_role": "exploit_confirmed_packet",
                "generated_budget": 800_000,
                "materialization_budget": 80_000,
                "numeric_budget": 20_000,
                "min_numeric_before_kill": 6_000,
                "field_axes": "basis_premium;vol_liquidity;listing_state;positioning_flow;raw_multi_axis",
                "notes": "Expands A7LS13 packet-derived axes without allowing basis/premium to monopolize the total run.",
            },
            {
                "lane_id": "A7LS16X_B",
                "lane_name": "raw_multi_axis_frontier",
                "search_role": "raw_discovery",
                "generated_budget": 1_400_000,
                "materialization_budget": 140_000,
                "numeric_budget": 35_000,
                "min_numeric_before_kill": 12_000,
                "field_axes": "price;basis;funding;OI;positioning;taker;liquidity;volatility;listing;regime;cross_axis",
                "notes": "Protected raw route. This is the main system-availability proof lane and must not be killed early for low initial hit rate.",
            },
            {
                "lane_id": "A7LS16X_C",
                "lane_name": "underrepresented_axis_expansion",
                "search_role": "coverage_repair",
                "generated_budget": 1_000_000,
                "materialization_budget": 100_000,
                "numeric_budget": 25_000,
                "min_numeric_before_kill": 8_000,
                "field_axes": "OI;positioning;taker_flow;funding_state;listing_state;regime_state",
                "notes": "Keeps non-basis state variables alive at real scale instead of letting selector history starve them.",
            },
            {
                "lane_id": "A7LS16X_D",
                "lane_name": "control_entropy_and_nulls",
                "search_role": "control_and_entropy",
                "generated_budget": 400_000,
                "materialization_budget": 40_000,
                "numeric_budget": 10_000,
                "min_numeric_before_kill": 3_000,
                "field_axes": "controls;placebo;wrong_lag;shuffle;null_vector;entropy_probe",
                "notes": "Maintains false-positive pressure and high-entropy exploration under the same compute budget.",
            },
            {
                "lane_id": "A7LS16X_E",
                "lane_name": "mapping_memory_cross_axis",
                "search_role": "mapping_layer_probe",
                "generated_budget": 400_000,
                "materialization_budget": 40_000,
                "numeric_budget": 10_000,
                "min_numeric_before_kill": 3_000,
                "field_axes": "mapping_clusters;memory_keys;semantic_pairs;signal_vector_novelty;portfolio_marginal_proxy",
                "notes": "Reserved lane for mapping-layer guided cross-axis candidates, not a single-objective rerun.",
            },
        ]
    )
    lanes["generated_share"] = lanes["generated_budget"] / lanes["generated_budget"].sum()
    lanes["numeric_share"] = lanes["numeric_budget"] / lanes["numeric_budget"].sum()

    execution_scale = {
        "stage": "A7LS-16X",
        "scale_profile": "large_company_checkpointed_4m",
        "baseline_stage": "A7LS-14",
        "generated_total": int(lanes["generated_budget"].sum()),
        "materialization_total": int(lanes["materialization_budget"].sum()),
        "numeric_total": int(lanes["numeric_budget"].sum()),
        "company_materialization_shards": 400,
        "materialization_rows_per_shard": 1_000,
        "company_numeric_shard_target": 1_024,
        "numeric_rows_per_shard_target": 96,
        "company_parallel_default": 3,
        "company_parallel_if_free_memory_gb_ge_24": 5,
        "company_parallel_hard_cap": 6,
        "checkpoint_numeric_intervals": [5_000, 12_000, 25_000, 50_000, 75_000, 100_000],
        "checkpoint_materialization_intervals": [25_000, 50_000, 100_000, 200_000, 300_000, 400_000],
        "raw_reserved_generated_budget": int(lanes.loc[lanes["lane_id"].eq("A7LS16X_B"), "generated_budget"].iloc[0]),
        "raw_reserved_numeric_budget": int(lanes.loc[lanes["lane_id"].eq("A7LS16X_B"), "numeric_budget"].iloc[0]),
        "raw_lane_minimum_numeric_before_kill": 12_000,
        "uses_may": False,
    }

    checkpoint_policy = {
        "hard_boundaries": {
            "alpha_proof": False,
            "shadow_paper_live": False,
            "may_in_selector_or_reward": False,
            "unbounded_full_grammar": False,
            "single_lane_budget_capture": False,
            "local_heavy_numeric_execution": False,
        },
        "kill_rules_after_minimum_runtime": [
            "eval_failure_rate > 0.06 after lane minimum numeric rows",
            "control_dominated_rate > 0.72 after lane minimum numeric rows",
            "field_contract_violation_count > 0 after adapter repair window",
            "single_skeleton_share > 0.25 after checkpoint diversity repair",
        ],
        "non_kill_rules": [
            "do not kill raw_multi_axis_frontier for low non-L7 rate before 12,000 numeric rows",
            "do not kill underrepresented_axis_expansion for low hit rate before 8,000 numeric rows",
            "do not collapse all lanes into basis_premium even if early checkpoints favor it",
        ],
        "expand_rules": [
            "lane non_l7_numeric_clue_rate >= 0.004 and control_dominated_rate <= 0.45",
            "at least 3 label families and 4 semantic pairs survive in lane",
            "portfolio_marginal_proxy positive after cluster cap",
        ],
    }

    source_of_truth = {
        "requires": ["A7LS-14X", "A7LS-15", "A7LS-16"],
        "supersedes_scale_limits_from": "A7LS-14 for future A7LS17/A7LS18 execution ceilings only",
        "does_not_rewrite_historical_artifacts": True,
        "current_queue_status": "A7LS15 100k materialization queue remains usable as first wave; A7LS16X authorizes expansion queue generation after A7LS17 checkpoints",
        "remote_execution_required": True,
        "local_execution_allowed": "schema/checkpoint bookkeeping only",
    }

    authorization = {
        "stage": "A7LS-16X",
        "decision": "PASS_A7LS16X_4M_SCALE_UP_AUTHORIZATION_READY" if not blockers else "HOLD_A7LS16X_INPUT_NOT_READY",
        "authorizes_scoped_large_search": not blockers,
        "authorizes_large_search": not blockers,
        "authorizes_a7ls17_company_materialization": not blockers,
        "authorizes_a7ls18_company_numeric_wave": not blockers,
        "authorizes_a7ls15x_expansion_blueprint_generation": not blockers,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "scope_boundary": "checkpointed A7LS company-machine pipeline only",
        "generated_total_limit": execution_scale["generated_total"],
        "materialization_total_limit": execution_scale["materialization_total"],
        "numeric_total_limit": execution_scale["numeric_total"],
    }

    manifest = {
        "stage": "A7LS-16X",
        "generated_at": now_iso(),
        "decision": authorization["decision"],
        "blockers": blockers,
        "input_a7ls14x_decision": a7ls14x.get("decision"),
        "input_a7ls15_decision": a7ls15.get("decision"),
        "input_a7ls16_decision": a7ls16.get("decision"),
        "lane_count": int(len(lanes)),
        **execution_scale,
        "authorizes_scoped_large_search": authorization["authorizes_scoped_large_search"],
        "authorizes_large_search": authorization["authorizes_large_search"],
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    lanes.to_csv(RUNTIME / "a7ls16x_lane_budget_map.csv", index=False)
    write_json(RUNTIME / "a7ls16x_execution_scale.json", execution_scale)
    write_json(RUNTIME / "a7ls16x_checkpoint_policy.json", checkpoint_policy)
    write_json(RUNTIME / "a7ls16x_source_of_truth.json", source_of_truth)
    write_json(RUNTIME / "a7ls16x_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ls16x_manifest.json", manifest)

    report_lines = [
        "# CRYPTO A7LS-16X 4M SCALE-UP AUTHORIZATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "## Scale Upgrade",
        "",
        f"- generated_total_limit: {execution_scale['generated_total']:,}",
        f"- materialization_total_limit: {execution_scale['materialization_total']:,}",
        f"- numeric_total_limit: {execution_scale['numeric_total']:,}",
        f"- company_materialization_shards: {execution_scale['company_materialization_shards']}",
        f"- company_numeric_shard_target: {execution_scale['company_numeric_shard_target']}",
        f"- raw_reserved_generated_budget: {execution_scale['raw_reserved_generated_budget']:,}",
        f"- raw_reserved_numeric_budget: {execution_scale['raw_reserved_numeric_budget']:,}",
        "",
        "A7LS-14 remains the 1M baseline. A7LS-16X raises the next company-machine execution ceiling to 4,000,000 generated / 400,000 materialization / 100,000 numeric rows after A7LS-16 preflight passed.",
        "",
        "This is not alpha proof and not live authorization. It is a larger checkpointed search budget with a protected raw multi-axis lane and explicit anti-collapse rules.",
        "",
        "## Lane Budget Map",
        "",
        md_table(lanes),
        "",
        "## Checkpoint Policy",
        "",
        "```json",
        json.dumps(checkpoint_policy, indent=2, sort_keys=True),
        "```",
        "",
        "## Source Of Truth",
        "",
        "```json",
        json.dumps(source_of_truth, indent=2, sort_keys=True),
        "```",
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return manifest


if __name__ == "__main__":
    result = build()
    print(json.dumps(result, indent=2, sort_keys=True))
