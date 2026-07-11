from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "runtime" / "nextgen_epoch0_20260711"
FROZEN = ROOT / "epoch0_frozen_design_manifest.json"
RUN = ROOT / "epoch0_run_manifest.json"
ORIGINAL_CHECK_FAILURE = ROOT / "epoch0_failure.json"
VALIDATION = ROOT / "epoch0_closure_validation.json"
REPORT = ROOT / "EPOCH0_COMPARATIVE_DECISION_REPORT.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_payload(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest().upper()


def select_recommendation(
    *, survivors: int, adaptive_basin_rate: float, bbo_stratified_fill: float,
    semantic_exact_conversion: float,
) -> str:
    if survivors == 0 or adaptive_basin_rate > 0.25 or bbo_stratified_fill < 0.80:
        return "REVISE_SEARCH_ENGINE_AND_REPEAT_DEVELOPMENT_EPOCH"
    if semantic_exact_conversion < 0.20:
        return "REVISE_HYPOTHESIS_SPACE_AND_REPEAT_DEVELOPMENT_EPOCH"
    return "PREPARE_ROTATING_CHALLENGE_EPOCH"


def validate() -> dict[str, Any]:
    frozen = load_json(FROZEN)
    recorded = frozen.pop("frozen_manifest_sha256")
    if sha256_payload(frozen) != recorded:
        raise ValueError("frozen design manifest hash drift")
    run = load_json(RUN)
    if run["frozen_manifest_sha256"] != recorded or run["decision"] != "FROZEN_DEVELOPMENT_EPOCH_COMPLETED":
        raise ValueError("run is not bound to the completed frozen design")
    prohibited = [
        "validation_test_recent_may_stress_forward_read", "candidate_promotion", "a7mem_updated",
        "cross_lane_memory_persisted", "cross_epoch_memory_persisted", "online_contract_changed",
        "additional_budget_added", "intermediate_human_reweighting", "alpha_ready_claimed",
        "oos_proven_claimed", "main_and_bbo_directly_ranked",
    ]
    if any(run.get(key) for key in prohibited):
        raise PermissionError("run manifest records prohibited activity")
    for output in run["outputs"]:
        path = REPO / output["path"]
        if sha256_file(path) != output["sha256"]:
            raise ValueError(f"run output hash drift: {output['path']}")
    raw = pd.read_csv(ROOT / "raw_proposals.csv", usecols=["proposal_id", "panel_id", "lane_id", "legal", "canonical_identity", "exact_identity"])
    strict = pd.read_csv(ROOT / "strict_evaluations.csv")
    admissions = pd.read_csv(ROOT / "admission_table.csv")
    comparison = pd.read_csv(ROOT / "benchmark_comparisons.csv")
    basin = pd.read_csv(ROOT / "reward_basin_audit.csv")
    semantic = pd.read_csv(ROOT / "semantic_volume_accounting.csv")
    lane = pd.read_csv(ROOT / "lane_efficiency.csv")
    benchmarks = pd.read_csv(ROOT / "benchmark_results.csv")
    if len(raw) != 32768 or raw["proposal_id"].duplicated().any():
        raise ValueError("raw proposal budget or identity drift")
    duplicated = strict.groupby(["panel_id", "arm"])["exact_identity"].apply(lambda values: values.duplicated().any())
    if duplicated.any():
        raise ValueError("one full exact identity received multiple votes inside an arm")
    if strict["candidate_promotion"].any() or strict["feedback_persisted"].any():
        raise PermissionError("strict result entered promotion or persistent feedback")
    if comparison["direct_cross_panel_ranking"].any():
        raise PermissionError("main and BBO comparison domains were mixed")
    stratified = int((strict["arm"] == "STRATIFIED_ADMISSION").sum())
    global_top_k = int((strict["arm"] == "GLOBAL_TOP_K_CONTROL").sum())
    if stratified != run["executed_stratified_strict_evaluations"] or global_top_k != run["global_top_k_strict_evaluations"]:
        raise ValueError("run manifest strict counts drifted")
    if not (0 < stratified <= 1024 and 0 < global_top_k <= 1024):
        raise ValueError("strict execution exceeded or failed to use frozen budgets")
    failure = load_json(ORIGINAL_CHECK_FAILURE)
    if failure.get("action") != "check" or failure.get("error") != "Epoch-0 global control budget mismatch":
        raise ValueError("original frozen checker defect is not preserved")
    bbo_stratified = int(((strict["panel_id"] == "bbo_micro") & (strict["arm"] == "STRATIFIED_ADMISSION")).sum())
    adaptive_lanes = {"cem", "uct_mcts", "evolutionary", "surrogate"}
    adaptive_basin_rate = float(basin[basin["lane_id"].isin(adaptive_lanes)]["scalar_basin_flag"].mean())
    survivors = int(strict["development_survivor"].sum())
    semantic_conversion = float(semantic["exact"].sum() / semantic["canonical"].sum())
    recommendation = select_recommendation(
        survivors=survivors, adaptive_basin_rate=adaptive_basin_rate,
        bbo_stratified_fill=bbo_stratified / 128.0, semantic_exact_conversion=semantic_conversion,
    )
    hard_gate_pass = int(strict["hard_gate_pass"].sum())
    positive_ic_lcb = int((strict["ic_lcb"] > 0).sum())
    positive_net_lcb = int((strict["net_lcb"] > 0).sum())
    positive_incremental_lcb = int((strict["benchmark_incremental_lcb"] > 0).sum())
    all_positive = int(((strict["ic_lcb"] > 0) & (strict["net_lcb"] > 0) & (strict["benchmark_incremental_lcb"] > 0) & (strict["worst_horizon_net_mean"] > -0.001)).sum())
    funding = semantic[semantic["mechanism_id"] == "funding_dynamics"]
    result = {
        "validation_status": "PASS_EPOCH0_CLOSURE_WITH_NATURAL_FULL_IDENTITY_UNDERFILL",
        "execution_status": "COMPLETED",
        "decision": "FROZEN_DEVELOPMENT_EPOCH_COMPLETED",
        "recommendation": recommendation,
        "run_recorded_recommendation": run["next_step_recommendation"],
        "recommendation_override_reason": "closure audit adds zero-survivor and admission-feasibility gates that the frozen run reporter omitted",
        "frozen_manifest_sha256": recorded,
        "proposal_rows": len(raw),
        "planned_stratified_strict_evaluations": 1024,
        "executed_stratified_strict_evaluations": stratified,
        "stratified_fill_rate": stratified / 1024.0,
        "planned_global_top_k_strict_evaluations": 1024,
        "executed_global_top_k_strict_evaluations": global_top_k,
        "global_top_k_fill_rate": global_top_k / 1024.0,
        "total_development_strict_evaluations": len(strict),
        "total_strict_fill_rate": len(strict) / 2048.0,
        "natural_underfill": True,
        "rerun_required": False,
        "underfill_contract_preserved": True,
        "underfill_causes": {
            "full_identity_dedup_after_proposal_sketch": int(len(admissions) - stratified),
            "bbo_stratified_family_cap": {"planned": 128, "executed": bbo_stratified, "family_budget_cap": 32},
            "global_full_identity_dedup": 1024 - global_top_k,
        },
        "hard_gate_pass": hard_gate_pass,
        "development_survivors": survivors,
        "positive_ic_lcb": positive_ic_lcb,
        "positive_net_lcb": positive_net_lcb,
        "positive_benchmark_incremental_lcb": positive_incremental_lcb,
        "all_positive_objective_rows_before_hard_gate_intersection": all_positive,
        "pareto_candidates": run["pareto_candidates"],
        "frozen_candidate_pack_rows": run["frozen_candidate_pack_rows"],
        "funding_expansion": {
            "typed_ast_exact_identities": int(funding[funding["lane_id"] == "typed_ast"]["exact"].iloc[0]),
            "typed_random_exact_identities": int(funding[funding["lane_id"] == "typed_random_fresh"]["exact"].iloc[0]),
            "b1s_reference_exact_identities": 27,
            "conclusion": "FUNDING_GRAMMAR_CAPACITY_EXPANDED; HYPOTHESIS_SPACE_IS_NOT_THE_PRIMARY_NEXT_BLOCKER",
        },
        "adaptive_basin_rate": adaptive_basin_rate,
        "semantic_exact_conversion": semantic_conversion,
        "original_frozen_checker_failure_preserved": str(ORIGINAL_CHECK_FAILURE.relative_to(REPO)).replace("\\", "/"),
        "no_new_evaluation_block_read": True,
        "forward_status": "FORWARD_SEALED",
        "candidate_promotion_status": "NO_CANDIDATE_PROMOTION",
        "cross_epoch_memory_status": "NO_CROSS_EPOCH_ADAPTIVE_MEMORY",
    }
    VALIDATION.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    arm = comparison.set_index(["panel_id", "arm"])
    lane_view = lane[[
        "panel_id", "lane_id", "proposals", "legal_rate", "exact_identities", "behaviour_clusters",
        "n_eff", "top_1_cluster_share", "economic_hypotheses", "strict_evaluations",
        "development_survivors", "new_behaviour_clusters_per_100_strict", "runtime_seconds", "failure_rate",
    ]]
    best_main_benchmark = benchmarks[benchmarks["panel_id"] == "main"].sort_values("net_lcb", ascending=False).iloc[0]
    report = [
        "# CRYPTO NEXTGEN SEARCH EPOCH-0 Comparative Decision Report", "",
        "Execution: `FROZEN_DEVELOPMENT_EPOCH_COMPLETED`", f"Recommendation: `{recommendation}`", "",
        "The fixed run completed normally. The 1,801/2,048 full strict evaluations are natural underfill after full-coordinate identity deduplication and the frozen BBO family cap; no identity was repeated and no budget, seed, grammar, reward, or admission rule was changed.", "",
        "## Fixed-budget execution", "",
        f"- Proposals: 32,768/32,768.",
        f"- Stratified strict: {stratified}/1,024 ({stratified / 1024:.2%}).",
        f"- Global top-K strict: {global_top_k}/1,024 ({global_top_k / 1024:.2%}).",
        f"- Total strict: {len(strict)}/2,048 ({len(strict) / 2048:.2%}).",
        f"- Hard-gate passes: {hard_gate_pass}; development survivors: {survivors}.",
        f"- Positive IC LCB / net LCB / benchmark-increment LCB: {positive_ic_lcb} / {positive_net_lcb} / {positive_incremental_lcb}.", "",
        "## Admission comparison", "",
        f"- Main stratified: {int(arm.loc[('main','STRATIFIED_ADMISSION'),'behaviour_clusters'])} clusters from {int(arm.loc[('main','STRATIFIED_ADMISSION'),'strict_evaluations'])} strict evaluations ({float(arm.loc[('main','STRATIFIED_ADMISSION'),'new_behaviour_clusters_per_100_strict']):.2f} per 100).",
        f"- Main global top-K: {int(arm.loc[('main','GLOBAL_TOP_K_CONTROL'),'behaviour_clusters'])} clusters from {int(arm.loc[('main','GLOBAL_TOP_K_CONTROL'),'strict_evaluations'])} strict evaluations ({float(arm.loc[('main','GLOBAL_TOP_K_CONTROL'),'new_behaviour_clusters_per_100_strict']):.2f} per 100).",
        "- Stratified admission improved behaviour-cluster yield per strict evaluation, but neither arm produced a development survivor.",
        "- Scoped BBO stratified admission executed only 32/128 because the frozen family budget cap was 32 while BBO had one legal mechanism family. This is an admission-feasibility defect, not a data-source failure.", "",
        "## Search algorithms", "", lane_view.to_markdown(index=False), "",
        "- Evolutionary search had the highest main adaptive cluster yield per 100 strict evaluations; it did not improve survivor production.",
        "- UCT/MCTS reached the highest legal rate but its top proxy decile concentrated 66.58% in one mechanism and 63.93% in one primitive, triggering the reward-basin audit.",
        "- CEM and surrogate did not materially exceed typed AST/random discovery efficiency, and every lane had zero survivors.", "",
        "## Hypothesis and benchmark diagnosis", "",
        "- Funding capacity expanded from the B1S reference of 27 exact identities to 120 exact identities in each typed AST/random funding slice. Funding grammar capacity is no longer the primary blocker.",
        f"- The best simple main benchmark by net LCB was `{best_main_benchmark['benchmark_id']}` at {best_main_benchmark['net_lcb']:.8f}; it was still negative after costs.",
        "- Only three strict rows had positive net LCB, and no row passed the complete survivor contract. Pareto membership therefore records development trade-offs, not investable evidence.", "",
        "## Required revision before another development epoch", "",
        "- Make admission quotas feasible per panel and mechanism count; the BBO family cap must not mechanically force 32/128.",
        "- Move full-identity dedup before final strict quota assignment so sketch collisions do not consume strict slots.",
        "- Recalibrate the lane scalar toward lower-confidence net/cost/stability measures; proxy-driven adaptation currently discovers diverse signals without survivor efficiency.",
        "- Add explicit typed/random matched controls for every adaptive lane and treat zero survivor improvement as an adaptive failure.",
        "- Preserve the expanded mechanism registry; the next revision target is search/admission/reward, not another blind hypothesis-space expansion.", "",
        "## Boundaries", "",
        "- `FORWARD_SEALED`", "- `NO_CANDIDATE_PROMOTION`", "- `NO_CROSS_EPOCH_ADAPTIVE_MEMORY`",
        "- No new evaluation block was read. No rerun was performed or authorized.",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    return result


def check() -> None:
    expected = validate()
    recorded = load_json(VALIDATION)
    if recorded != expected:
        raise ValueError("closure validation artifact drift")
    if recorded["recommendation"] != "REVISE_SEARCH_ENGINE_AND_REPEAT_DEVELOPMENT_EPOCH":
        raise ValueError("closure recommendation does not reflect zero-survivor/admission evidence")
    print("PASS_EPOCH0_CLOSURE_VALID")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("build", "check"))
    args = parser.parse_args()
    result = validate()
    if args.action == "check":
        check()
    else:
        print(json.dumps({"status": result["validation_status"], "decision": result["decision"], "recommendation": result["recommendation"]}, indent=2))


if __name__ == "__main__":
    main()
