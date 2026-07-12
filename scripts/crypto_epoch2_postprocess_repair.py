from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import scripts.crypto_epoch2 as epoch2
from alphafactory_crypto.nextgen_epoch import effective_count


ROOT = epoch2.ROOT
REPAIRED_STRICT = ROOT / "strict_evaluations_repaired.csv"
ATTRIBUTION = ROOT / "repair_child_attribution.csv"
LINEAGE = ROOT / "repair_lineage_attribution.csv"
SURROGATE = ROOT / "surrogate_crossfit_diagnostic.csv"
POLICY = ROOT / "admission_policy_comparison.csv"
LANE = ROOT / "lane_comparison.csv"
ADAPTIVE = ROOT / "adaptive_vs_matched_controls.csv"
REPORT = ROOT / "EPOCH2_COMPACT_RESULT.md"
RECOVERY = ROOT / "epoch2_postprocess_recovery_manifest.json"
INDEX = ROOT / "epoch2_artifact_index.csv"


def reconstruct_proposal_ids(strict: pd.DataFrame, assignments: pd.DataFrame) -> pd.DataFrame:
    """Recover the omitted report key without evaluating or rematerializing a signal."""
    if len(strict) != 2304 or len(assignments) != 2304:
        raise ValueError("postprocess repair requires the complete frozen 2304-row strict execution")
    keys = ["admission_policy", "panel_id", "exact_identity"]
    if assignments.duplicated(keys).any() or strict.duplicated(keys).any():
        raise ValueError("postprocess join key is not one-to-one")
    lookup = assignments[keys + ["proposal_id"]]
    repaired = strict.merge(lookup, on=keys, how="left", validate="one_to_one", sort=False)
    if repaired["proposal_id"].isna().any() or len(repaired) != len(strict):
        raise ValueError("proposal_id reconstruction is incomplete")
    return repaired


def _summary_tables(strict: pd.DataFrame, attribution: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    policy_rows = []
    for policy_name, group in strict.groupby("admission_policy", sort=True):
        counts = group.full_behaviour_cluster.value_counts()
        policy_rows.append({
            "admission_policy": policy_name,
            "rows": len(group),
            "exact_identities": group.exact_identity.nunique(),
            "survivors": int(group.survivor.sum()),
            "near_misses": int(group.near_miss.sum()),
            "positive_net_lcb": int((group.net_lcb > 0).sum()),
            "behaviour_clusters": group.full_behaviour_cluster.nunique(),
            "n_eff": effective_count(group.full_behaviour_cluster),
            "top_cluster_share": float(counts.iloc[0] / len(group)),
            "hypotheses": group.hypothesis.nunique(),
            "mechanisms": group.mechanism_id.nunique(),
        })
    lane_rows = []
    for lane_name, group in strict.groupby("lane_id", sort=True):
        counts = group.full_behaviour_cluster.value_counts()
        lane_rows.append({
            "lane_id": lane_name,
            "rows": len(group),
            "survivors": int(group.survivor.sum()),
            "near_misses": int(group.near_miss.sum()),
            "positive_net_lcb": int((group.net_lcb > 0).sum()),
            "net_lcb_mean": float(group.net_lcb.mean()),
            "behaviour_clusters": group.full_behaviour_cluster.nunique(),
            "n_eff": effective_count(group.full_behaviour_cluster),
            "top_cluster_share": float(counts.iloc[0] / len(group)),
        })
    comparisons = []
    for adaptive, control in epoch2.MATCHED_REPAIR_LANES:
        left = strict[strict.lane_id == adaptive]
        right = strict[strict.lane_id == control]
        left_attr = attribution[attribution.lane_id == adaptive]
        right_attr = attribution[attribution.lane_id == control]
        wins = sum((
            left.survivor.mean() > right.survivor.mean(),
            left.near_miss.mean() > right.near_miss.mean(),
            left_attr.blocker_distance_delta.median() > right_attr.blocker_distance_delta.median(),
        ))
        comparisons.append({
            "adaptive_lane": adaptive,
            "control_lane": control,
            "adaptive_rows": len(left),
            "control_rows": len(right),
            "adaptive_survivor_rate": float(left.survivor.mean()),
            "control_survivor_rate": float(right.survivor.mean()),
            "adaptive_near_miss_rate": float(left.near_miss.mean()),
            "control_near_miss_rate": float(right.near_miss.mean()),
            "adaptive_blocker_delta_median": float(left_attr.blocker_distance_delta.median()),
            "control_blocker_delta_median": float(right_attr.blocker_distance_delta.median()),
            "adaptive_behaviour_clusters": left.full_behaviour_cluster.nunique(),
            "control_behaviour_clusters": right.full_behaviour_cluster.nunique(),
            "verdict": "ADAPTIVE_SUCCESS" if wins >= 2 else "NO_ADAPTIVE_SUCCESS",
        })
    return pd.DataFrame(policy_rows), pd.DataFrame(lane_rows), pd.DataFrame(comparisons)


def recover() -> dict[str, object]:
    started = time.perf_counter()
    frozen = epoch2.verify()
    failure_sha = epoch2.sha(epoch2.FAILURE)
    assignments = pd.read_csv(epoch2.ASSIGN)
    original_strict = pd.read_csv(epoch2.STRICT)
    strict = reconstruct_proposal_ids(original_strict, assignments)
    strict["parent_row_id"] = strict["parent_row_id"].fillna("")
    strict["repair_action"] = strict["repair_action"].fillna("")
    strict.to_csv(REPAIRED_STRICT, index=False)

    parents = pd.read_csv(epoch2.PARENTS)
    parent_lookup = parents.set_index("frozen_parent_row_id").to_dict("index")
    attribution_rows = []
    for row in strict[strict.parent_row_id != ""].to_dict("records"):
        parent = parent_lookup[row["parent_row_id"]]
        blocker = str(parent["blocker_type"])
        before = epoch2.blocker_distance(parent, blocker)
        after = epoch2.blocker_distance(row, blocker)
        attribution_rows.append({
            "admission_policy": row["admission_policy"],
            "proposal_id": row["proposal_id"],
            "lane_id": row["lane_id"],
            "parent_row_id": row["parent_row_id"],
            "repair_action": row["repair_action"],
            "blocker_type": blocker,
            "parent_failed_gate": parent["failed_gate"],
            "child_failed_gates": row["failed_gates"],
            "blocker_distance_before": before,
            "blocker_distance_after": after,
            "blocker_distance_delta": after - before,
            "target_gate_improved": after > before,
            "target_gate_passed": after > 0,
            "parent_scalar": float(parent["development_scalar"]),
            "child_scalar": float(row["development_scalar"]),
            "scalar_improved": float(row["development_scalar"]) > float(parent["development_scalar"]),
            "survivor": row["survivor"],
            "near_miss": row["near_miss"],
        })
    attribution = pd.DataFrame(attribution_rows)
    attribution.to_csv(ATTRIBUTION, index=False)
    lineage = attribution.groupby(["lane_id", "repair_action"], sort=True).agg(
        children=("proposal_id", "count"),
        survivors=("survivor", "sum"),
        near_misses=("near_miss", "sum"),
        blocker_improvement_rate=("target_gate_improved", "mean"),
        target_gate_pass_rate=("target_gate_passed", "mean"),
        blocker_distance_delta_median=("blocker_distance_delta", "median"),
        scalar_improvement_rate=("scalar_improved", "mean"),
    ).reset_index()
    lineage.to_csv(LINEAGE, index=False)
    surrogate = epoch2.surrogate_crossfit(strict)
    surrogate.to_csv(SURROGATE, index=False)
    policy, lane, adaptive = _summary_tables(strict, attribution)
    policy.to_csv(POLICY, index=False)
    lane.to_csv(LANE, index=False)
    adaptive.to_csv(ADAPTIVE, index=False)

    survivors = int(strict.survivor.sum())
    near_misses = int(strict.near_miss.sum())
    positive_net = int((strict.net_lcb > 0).sum())
    adaptive_successes = int((adaptive.verdict == "ADAPTIVE_SUCCESS").sum())
    role = pd.read_csv(ROOT / "search_role_diagnostics.csv")
    mcts = role[role.lane_id == "local_mcts_repair"].iloc[0]
    mcts_concentration = max(float(mcts.top_mechanism_share), float(mcts.top_primitive_share))
    median_blocker_delta = float(attribution.blocker_distance_delta.median())
    decision = "FROZEN_DEVELOPMENT_EPOCH2_COMPLETED" if survivors > 0 else "FROZEN_DEVELOPMENT_EPOCH2_PARTIALLY_COMPLETED"
    if survivors > 0 and adaptive_successes > 0 and mcts_concentration < .5426:
        recommendation = "PREPARE_ROTATING_CHALLENGE_EPOCH"
    elif survivors == 0 and positive_net > 2 and median_blocker_delta > 0:
        recommendation = "REVISE_SURVIVOR_CONTRACT_WITHOUT_OOS_ACCESS"
    else:
        recommendation = "REVISE_BLOCKER_DIRECTED_SEARCH_AND_REPEAT"

    recovery = {
        "status": "STRICT_EXECUTION_COMPLETE_POSTPROCESS_SCHEMA_REPAIRED",
        "repair_scope": "RESTORE_OMITTED_PROPOSAL_ID_AND_GENERATE_REPORTS_ONLY",
        "frozen_manifest_sha256": frozen["frozen_manifest_sha256"],
        "original_failure_path": epoch2.rel(epoch2.FAILURE),
        "original_failure_sha256": failure_sha,
        "assignment_sha256": epoch2.sha(epoch2.ASSIGN),
        "original_strict_sha256": epoch2.sha(epoch2.STRICT),
        "strict_rows_reused": len(strict),
        "new_proposals": 0,
        "new_strict_evaluations": 0,
        "new_performance_queries": 0,
        "return_label_reread": False,
        "forward_read": False,
        "candidate_promotion": False,
        "cross_epoch_memory": False,
        "online_contract_change": False,
    }
    RECOVERY.write_text(json.dumps(recovery, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = [
        "# Epoch-2 Compact Result", "",
        f"Decision: `{decision}`", f"Recommendation: `{recommendation}`", "",
        "The frozen strict execution completed all 2,304 logical rows. A post-strict report schema omission was repaired without a new performance query.", "",
        policy.to_markdown(index=False), "", adaptive.to_markdown(index=False), "",
        f"- Shared exact evaluation queries: {strict.groupby(['panel_id', 'exact_identity']).ngroups} / 2304 logical strict rows",
        f"- Median parent-to-child blocker distance delta: {median_blocker_delta:.8g}",
        f"- Local MCTS top mechanism/primitive concentration: {mcts_concentration:.6f}",
        "- `FORWARD_SEALED`", "- `NO_CANDIDATE_PROMOTION`", "- `NO_CROSS_EPOCH_ADAPTIVE_MEMORY`",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    artifact_paths = [
        epoch2.FROZEN, epoch2.PACK, epoch2.ASSIGN, epoch2.STRICT, epoch2.FAILURE,
        REPAIRED_STRICT, ROOT / "search_role_diagnostics.csv", ROOT / "cem_diagnostic.csv",
        ROOT / "local_mcts_root_visits.csv", ATTRIBUTION, LINEAGE, SURROGATE, POLICY, LANE,
        ADAPTIVE, REPORT, RECOVERY,
    ]
    index = pd.DataFrame([{"path": epoch2.rel(path), "sha256": epoch2.sha(path), "exists": True} for path in artifact_paths])
    index.to_csv(INDEX, index=False)
    outputs = artifact_paths + [INDEX]
    policy_counts = {str(key): int(value) for key, value in assignments.groupby("admission_policy").size().items()}
    manifest = {
        "experiment_id": frozen["experiment_id"],
        "execution_status": "STRICT_COMPLETED_POSTPROCESS_RECOVERED",
        "decision": decision,
        "recommendation": recommendation,
        "frozen_manifest_sha256": frozen["frozen_manifest_sha256"],
        "proposal_rows": 49152,
        "logical_strict_rows": len(strict),
        "shared_cache_queries": strict.groupby(["panel_id", "exact_identity"]).ngroups,
        "policy_counts": policy_counts,
        "survivors": survivors,
        "near_misses": near_misses,
        "positive_net_lcb": positive_net,
        "adaptive_successes": adaptive_successes,
        "mcts_top_concentration": mcts_concentration,
        "median_blocker_distance_delta": median_blocker_delta,
        "postprocess_recovery": True,
        "new_performance_queries_for_recovery": 0,
        "runtime_seconds_postprocess_only": time.perf_counter() - started,
        "outputs": [{"path": epoch2.rel(path), "sha256": epoch2.sha(path)} for path in outputs],
        "forward_status": "FORWARD_SEALED",
        "candidate_promotion": False,
        "a7mem_updated": False,
        "cross_epoch_memory": False,
        "online_change": False,
        "additional_budget": False,
        "oos_claim": False,
    }
    epoch2.RUN.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({key: manifest[key] for key in (
        "decision", "recommendation", "logical_strict_rows", "shared_cache_queries",
        "survivors", "near_misses", "positive_net_lcb", "adaptive_successes",
        "mcts_top_concentration", "median_blocker_distance_delta",
    )}, indent=2))
    return manifest


def check() -> None:
    epoch2.check()
    manifest = epoch2.load(epoch2.RUN)
    recovery = epoch2.load(RECOVERY)
    repaired = pd.read_csv(REPAIRED_STRICT)
    if len(repaired) != 2304 or repaired.proposal_id.isna().any():
        raise ValueError("postprocess-repaired strict table is incomplete")
    if recovery["new_performance_queries"] != 0 or manifest["new_performance_queries_for_recovery"] != 0:
        raise PermissionError("postprocess repair performed a new performance query")
    if epoch2.sha(epoch2.FAILURE) != recovery["original_failure_sha256"]:
        raise ValueError("original failure evidence drift")
    print("PASS_EPOCH2_POSTPROCESS_RECOVERY_VALID")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("recover", "check"))
    args = parser.parse_args()
    {"recover": recover, "check": check}[args.action]()


if __name__ == "__main__":
    main()
