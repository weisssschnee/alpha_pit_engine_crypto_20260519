from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
A7LS13 = REPO / "runtime" / "a7ls13_consolidation_replay_packet"
RUNTIME = REPO / "runtime" / "a7ls14_scaled_multi_axis_search_contract"
REPORT = REPO / "reports" / "CRYPTO_A7LS14_SCALED_MULTI_AXIS_SEARCH_CONTRACT_20260606.md"


def now_iso() -> str:
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


def build() -> dict[str, Any]:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifest13 = read_json(A7LS13 / "a7ls13_manifest.json")
    packet = pd.read_csv(A7LS13 / "a7ls13_replay_packet.csv")

    lanes = pd.DataFrame(
        [
            {
                "lane_id": "A7LS14_A",
                "lane_name": "exploit_a7ls13_multi_label_packet",
                "search_role": "evidence_exploitation",
                "generated_budget": 320000,
                "materialization_budget": 32000,
                "numeric_budget": 8000,
                "min_numeric_before_kill": 2500,
                "source": "A7LS13 replay packet seeds",
                "field_axes": "basis_premium;vol_liquidity;raw_multi_axis;listing_state;positioning_flow",
                "allowed_depth": "typed_l1_l2_l3_plus_seed_mutation",
                "notes": "Exploit 25 candidate-level packet formulas with multi-label evidence.",
            },
            {
                "lane_id": "A7LS14_B",
                "lane_name": "raw_multi_axis_reserved_search",
                "search_role": "raw_discovery",
                "generated_budget": 320000,
                "materialization_budget": 32000,
                "numeric_budget": 8000,
                "min_numeric_before_kill": 3000,
                "source": "raw field ontology plus typed random axes",
                "field_axes": "price;basis;funding;OI;positioning;taker;liquidity;volatility;listing;regime",
                "allowed_depth": "raw_l1_l2_bounded_interactions",
                "notes": "Protected full route. It must not be prematurely killed by basis/premium exploitation.",
            },
            {
                "lane_id": "A7LS14_C",
                "lane_name": "underrepresented_axis_rescue",
                "search_role": "coverage_repair",
                "generated_budget": 240000,
                "materialization_budget": 24000,
                "numeric_budget": 6000,
                "min_numeric_before_kill": 2000,
                "source": "A7LS12/13 weak-but-present axes",
                "field_axes": "positioning;listing_state;OI;taker_flow;funding_state",
                "allowed_depth": "typed_l1_l2_l3_interactions",
                "notes": "Explicitly expands axes that survived weakly but were underrepresented in A7LS13 packet.",
            },
            {
                "lane_id": "A7LS14_D",
                "lane_name": "null_control_and_high_entropy_probe",
                "search_role": "control_and_entropy",
                "generated_budget": 120000,
                "materialization_budget": 12000,
                "numeric_budget": 3000,
                "min_numeric_before_kill": 1000,
                "source": "controls plus high-entropy grammar probes",
                "field_axes": "controls;placebo;wrong_lag;shuffle;low_prior;entropy_probe",
                "allowed_depth": "control_plus_bounded_raw",
                "notes": "Keeps one route honest: detects selector/reward self-deception and samples high-entropy raw space.",
            },
        ]
    )
    lanes["generated_share"] = lanes["generated_budget"] / lanes["generated_budget"].sum()
    lanes["numeric_share"] = lanes["numeric_budget"] / lanes["numeric_budget"].sum()

    axis_policy = pd.DataFrame(
        [
            {"axis": "basis_premium", "min_numeric_share": 0.08, "max_numeric_share": 0.22, "can_dominate": False},
            {"axis": "vol_liquidity", "min_numeric_share": 0.08, "max_numeric_share": 0.20, "can_dominate": False},
            {"axis": "raw_multi_axis", "min_numeric_share": 0.20, "max_numeric_share": 0.35, "can_dominate": False},
            {"axis": "positioning", "min_numeric_share": 0.08, "max_numeric_share": 0.18, "can_dominate": False},
            {"axis": "listing_state", "min_numeric_share": 0.06, "max_numeric_share": 0.15, "can_dominate": False},
            {"axis": "OI", "min_numeric_share": 0.06, "max_numeric_share": 0.16, "can_dominate": False},
            {"axis": "taker_flow", "min_numeric_share": 0.05, "max_numeric_share": 0.14, "can_dominate": False},
            {"axis": "funding_state", "min_numeric_share": 0.05, "max_numeric_share": 0.14, "can_dominate": False},
            {"axis": "control_entropy", "min_numeric_share": 0.08, "max_numeric_share": 0.18, "can_dominate": False},
        ]
    )

    checkpoint = {
        "stage": "A7LS-14",
        "execution_style": "large_scale_checkpointed_multi_axis",
        "generated_total": int(lanes["generated_budget"].sum()),
        "materialization_total": int(lanes["materialization_budget"].sum()),
        "numeric_total": int(lanes["numeric_budget"].sum()),
        "company_numeric_shard_target": 256,
        "numeric_rows_per_shard_target": 96,
        "company_max_parallel_default": 3,
        "company_max_parallel_if_memory_free_gb_ge_18": 4,
        "local_light_preflight_rows": 512,
        "checkpoint_numeric_intervals": [2000, 5000, 10000, 15000, 20000, 25000],
        "lane_minimum_runtime": {
            "raw_multi_axis_reserved_search": "do_not_kill_before_3000_numeric_rows_unless_eval_failure_or_control_dominates",
            "underrepresented_axis_rescue": "do_not_kill_before_2000_numeric_rows_unless_eval_failure_or_control_dominates",
        },
        "global_kill_rules": [
            "eval_failure_rate > 0.05 after 2000 numeric rows",
            "control_dominated_rate > 0.65 after 5000 numeric rows",
            "non_l7_numeric_clue_rate == 0 after 5000 numeric rows",
            "single_source_axis_share > 0.55 after checkpoint diversity repair",
            "single_skeleton_share > 0.20 in selected queue",
            "L7_ranked_label_share > 0.55 in selected queue",
        ],
        "lane_expand_rules": [
            "non_l7_numeric_clue_rate >= 0.006",
            "control_dominated_rate <= 0.35",
            "at least 3 label families survive",
            "at least 4 semantic pairs survive",
            "selected queue has >= 8 candidates after caps",
        ],
        "hard_boundaries": {
            "may_in_selector": False,
            "same_objective_single_lane_capture": False,
            "unbounded_full_grammar": False,
            "alpha_proof": False,
            "shadow_paper_live": False,
        },
    }

    execution_plan = pd.DataFrame(
        [
            {"step": "A7LS14-0", "name": "scaled contract and seed-map freeze", "runs_heavy_compute": False, "output": "this stage"},
            {"step": "A7LS15", "name": "million-scale multi-axis blueprint generation", "runs_heavy_compute": False, "output": "1,000,000 blueprint index plus shard plan"},
            {"step": "A7LS16", "name": "local preflight and field/materialization smoke", "runs_heavy_compute": False, "output": "512-row preflight"},
            {"step": "A7LS17", "name": "company sharded materialization", "runs_heavy_compute": True, "output": "100,000 materialized queue rows"},
            {"step": "A7LS18", "name": "company sharded numeric wave", "runs_heavy_compute": True, "output": "25,000 numeric rows with checkpoints"},
            {"step": "A7LS19", "name": "checkpoint arbitration and lane resize", "runs_heavy_compute": False, "output": "continue/kill/expand decisions per lane"},
        ]
    )

    seed_summary = (
        packet.groupby(["source_info_axis", "next_wave_family"], dropna=False)
        .size()
        .reset_index(name="a7ls13_packet_rows")
        .sort_values("a7ls13_packet_rows", ascending=False)
        if not packet.empty
        else pd.DataFrame(columns=["source_info_axis", "next_wave_family", "a7ls13_packet_rows"])
    )

    lanes.to_csv(RUNTIME / "a7ls14_lane_budget_map.csv", index=False)
    axis_policy.to_csv(RUNTIME / "a7ls14_axis_quota_policy.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ls14_execution_plan.csv", index=False)
    seed_summary.to_csv(RUNTIME / "a7ls14_seed_packet_summary.csv", index=False)
    write_json(RUNTIME / "a7ls14_checkpoint_policy.json", checkpoint)

    authorization = {
        "authorized": {
            "A7LS15_million_scale_blueprint_generation": True,
            "A7LS16_local_preflight": True,
            "A7LS17_company_materialization": True,
            "A7LS18_company_numeric_wave": True,
            "raw_multi_axis_reserved_lane": True,
        },
        "not_authorized": {
            "alpha_proof": True,
            "shadow_paper_live": True,
            "May_in_selector_or_reward": True,
            "unbounded_full_grammar": True,
            "single_lane_budget_capture": True,
        },
    }
    write_json(RUNTIME / "a7ls14_authorization_matrix.json", authorization)

    manifest = {
        "stage": "A7LS-14",
        "decision": "PASS_A7LS14_SCALED_MULTI_AXIS_SEARCH_CONTRACT_READY",
        "generated_at": now_iso(),
        "input_stage": manifest13.get("stage"),
        "input_decision": manifest13.get("decision"),
        "input_replay_packet_rows": int(manifest13.get("replay_packet_rows", len(packet))),
        "lane_count": int(len(lanes)),
        "generated_total": int(lanes["generated_budget"].sum()),
        "materialization_total": int(lanes["materialization_budget"].sum()),
        "numeric_total": int(lanes["numeric_budget"].sum()),
        "raw_reserved_generated_budget": int(lanes.loc[lanes["lane_id"].eq("A7LS14_B"), "generated_budget"].iloc[0]),
        "raw_reserved_numeric_budget": int(lanes.loc[lanes["lane_id"].eq("A7LS14_B"), "numeric_budget"].iloc[0]),
        "company_numeric_shard_target": checkpoint["company_numeric_shard_target"],
        "authorizes_a7ls15_generation": True,
        "authorizes_a7ls17_company_materialization": True,
        "authorizes_a7ls18_company_numeric": True,
        "authorizes_large_search": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may": False,
        "executes_search": False,
        "blockers": [],
    }
    write_json(RUNTIME / "a7ls14_manifest.json", manifest)

    report = [
        "# CRYPTO A7LS-14 SCALED MULTI-AXIS SEARCH CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "## Scale",
        "",
        f"- generated_total: {manifest['generated_total']:,}",
        f"- materialization_total: {manifest['materialization_total']:,}",
        f"- numeric_total: {manifest['numeric_total']:,}",
        f"- company_numeric_shard_target: {manifest['company_numeric_shard_target']}",
        f"- raw_reserved_generated_budget: {manifest['raw_reserved_generated_budget']:,}",
        f"- raw_reserved_numeric_budget: {manifest['raw_reserved_numeric_budget']:,}",
        "",
        "This is a real scale-up. The previous A7LS0 contract was 240k generated / 8k numeric. A7LS14 raises the next wave to 1,000,000 generated / 100,000 materialization / 25,000 numeric, with one protected raw multi-axis lane.",
        "",
        "## Lane Budget Map",
        "",
        md_table(lanes),
        "",
        "## Axis Quota Policy",
        "",
        md_table(axis_policy),
        "",
        "## A7LS13 Seed Packet Summary",
        "",
        md_table(seed_summary),
        "",
        "## Execution Plan",
        "",
        md_table(execution_plan),
        "",
        "## Checkpoint Policy",
        "",
        "```json",
        json.dumps(checkpoint, indent=2, sort_keys=True),
        "```",
        "",
        "## Authorization",
        "",
        "- A7LS15 million-scale blueprint generation: authorized",
        "- A7LS17 company materialization: authorized after A7LS16 local preflight",
        "- A7LS18 company numeric wave: authorized after materialization",
        "- alpha proof / shadow / paper / live: not authorized",
        "",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
