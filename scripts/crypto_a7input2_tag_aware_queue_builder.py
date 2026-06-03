from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
A7INPUT0 = REPO / "runtime" / "a7input0_input_approval_package"
A7INPUT1 = REPO / "runtime" / "a7input1_integration_smoke"
A7FF_VERSION = REPO / "runtime" / "a7ff_version_20260530"
RUNTIME = REPO / "runtime" / "a7input2_tag_aware_queue_builder"
REPORT = REPO / "reports" / "CRYPTO_A7INPUT2_TAG_AWARE_QUEUE_BUILDER_20260603.md"

FIELD_RE = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b")
FUNCTION_TOKENS = {
    "Abs",
    "Add",
    "Clip",
    "CSRank",
    "Decay",
    "Delta",
    "Identity",
    "Mean",
    "Mul",
    "Neg",
    "Rank",
    "SafeDiv",
    "Sign",
    "SignedRankDelta",
    "SpreadShortLong",
    "Sub",
    "TSRank",
    "WinsorZ",
    "ZScore",
}

LEVEL_PRIORITY = {
    "L1_single_field_transform": 0,
    "L2_typed_two_field_interaction": 1,
    "L3_state_conditioned_feature": 2,
    "L4_factor_candidate_probe": 3,
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict) -> None:
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


def parse_fields(row: pd.Series, known_fields: set[str]) -> list[str]:
    fields: set[str] = set()
    for col in ["primary_field", "secondary_field"]:
        val = str(row.get(col, "") or "").strip()
        if val in known_fields:
            fields.add(val)
    for token in FIELD_RE.findall(str(row.get("expression", ""))):
        if token in FUNCTION_TOKENS:
            continue
        if token in known_fields:
            fields.add(token)
    return sorted(fields)


def boolish(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def enrich_candidates(formulas: pd.DataFrame, registry_df: pd.DataFrame) -> pd.DataFrame:
    registry = registry_df.set_index("field").to_dict("index")
    known_fields = set(registry)
    rows = []
    for _, row in formulas.iterrows():
        fields = parse_fields(row, known_fields)
        missing = []
        tags = []
        clusters = []
        semantic_types = []
        routes = []
        for field in fields:
            item = registry.get(field)
            if not item:
                missing.append(field)
                continue
            tags.append(item["input_tag"])
            clusters.append(item["info_cluster_id"])
            semantic_types.append(item["semantic_type"])
            routes.append(item["input_route"])
        rows.append(
            {
                **row.to_dict(),
                "input_fields": "|".join(fields),
                "input_field_count": len(fields),
                "input_tags": "|".join(sorted(set(tags))),
                "input_clusters": "|".join(sorted(set(clusters))),
                "input_semantic_types": "|".join(sorted(set(semantic_types))),
                "input_routes": "|".join(sorted(set(routes))),
                "missing_registry_fields": "|".join(missing),
                "has_missing_registry_field": bool(missing),
                "has_signal_tag": bool(
                    set(tags)
                    & {
                        "A7INPUT_APPROVED_SIGNAL_PRIMARY",
                        "A7INPUT_APPROVED_REDUNDANT_CAP",
                    }
                ),
                "has_condition_tag": "A7INPUT_CONDITION_NEUTRALIZER_ONLY" in set(tags),
                "has_rescue_tag": bool(
                    set(tags)
                    & {
                        "A7INPUT_RESCUE_SPARSE_EVENT",
                        "A7INPUT_RESCUE_TS_STATE",
                    }
                ),
                "has_hard_block_tag": bool(
                    set(tags)
                    & {
                        "A7INPUT_HARD_BLOCKED",
                        "A7INPUT_REVIEW_REQUIRED",
                    }
                ),
                "all_tags": set(tags),
                "all_clusters": set(clusters),
                "all_semantics": set(semantic_types),
                "level_priority": LEVEL_PRIORITY.get(str(row.get("level", "")), 99),
                "in_company_numeric_wave_queue_bool": boolish(row.get("in_company_numeric_wave_queue", False)),
                "in_materialization_queue_bool": boolish(row.get("in_materialization_queue", False)),
            }
        )
    return pd.DataFrame(rows)


def classify_mode(row: pd.Series, mode: str, policy: dict) -> tuple[str, str]:
    tags = set(row["all_tags"])
    if row["has_missing_registry_field"]:
        return "reject", "missing_registry_field"
    if not tags:
        return "reject", "no_approved_input_field"
    if row["has_hard_block_tag"]:
        return "reject", "hard_block_or_review_required"
    if mode == "ordinary_alpha":
        allowed = set(policy["ordinary_alpha"]["allowed_tags"])
        blocked = set(policy["ordinary_alpha"]["blocked_tags"])
        if tags & blocked:
            return "reject", "ordinary_alpha_blocked_tag"
        if not tags <= allowed:
            return "reject", "ordinary_alpha_tag_not_allowed"
        return "accept", "ordinary_alpha_route"
    if mode == "interaction_alpha":
        allowed = set(policy["interaction_alpha"]["allowed_tags"])
        if not tags <= allowed:
            return "reject", "interaction_tag_not_allowed"
        if policy["interaction_alpha"].get("requires_at_least_one_signal_tag") and not row["has_signal_tag"]:
            return "reject", "interaction_missing_signal_tag"
        if int(row["input_field_count"]) < 2 and not row["has_condition_tag"]:
            return "reject", "interaction_requires_pair_or_condition"
        return "accept", "interaction_route"
    if mode == "rescue_lane":
        allowed = set(policy["rescue_lane"]["allowed_tags"])
        if not tags <= allowed:
            return "reject", "rescue_requires_only_rescue_tags"
        return "accept", "rescue_lane_route"
    return "reject", "unknown_mode"


def sort_candidates(df: pd.DataFrame) -> pd.DataFrame:
    priority_map = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    view = df.copy()
    view["generation_priority_rank"] = view["generation_priority"].map(priority_map).fillna(9).astype(int)
    return view.sort_values(
        [
            "in_company_numeric_wave_queue_bool",
            "in_materialization_queue_bool",
            "generation_priority_rank",
            "level_priority",
            "blueprint_id",
        ],
        ascending=[False, False, True, True, True],
    )


def cap_queue(
    candidates: pd.DataFrame,
    target_count: int,
    max_cluster_share: float,
    max_semantic_share: float,
    max_semantic_pair_share: float,
    max_skeleton_share: float,
) -> pd.DataFrame:
    if candidates.empty:
        return candidates.copy()
    selected = []
    cluster_counts: Counter[str] = Counter()
    semantic_counts: Counter[str] = Counter()
    semantic_pair_counts: Counter[str] = Counter()
    skeleton_counts: Counter[str] = Counter()
    cluster_cap = max(1, int(target_count * max_cluster_share))
    semantic_cap = max(1, int(target_count * max_semantic_share))
    semantic_pair_cap = max(1, int(target_count * max_semantic_pair_share))
    skeleton_cap = max(1, int(target_count * max_skeleton_share))
    for _, row in sort_candidates(candidates).iterrows():
        if len(selected) >= target_count:
            break
        clusters = set(row["all_clusters"])
        semantics = set(row["all_semantics"])
        semantic_pair = str(row.get("semantic_pair", ""))
        skeleton = str(row.get("skeleton_key", ""))
        if any(cluster_counts[c] >= cluster_cap for c in clusters):
            continue
        if any(semantic_counts[s] >= semantic_cap for s in semantics):
            continue
        if semantic_pair and semantic_pair_counts[semantic_pair] >= semantic_pair_cap:
            continue
        if skeleton and skeleton_counts[skeleton] >= skeleton_cap:
            continue
        selected.append(row)
        for cluster in clusters:
            cluster_counts[cluster] += 1
        for semantic in semantics:
            semantic_counts[semantic] += 1
        if semantic_pair:
            semantic_pair_counts[semantic_pair] += 1
        if skeleton:
            skeleton_counts[skeleton] += 1
    return pd.DataFrame(selected).drop(columns=["all_tags", "all_clusters", "all_semantics"], errors="ignore")


def summarize_queue(df: pd.DataFrame, queue_name: str) -> dict:
    if df.empty:
        return {
            "queue": queue_name,
            "row_count": 0,
            "semantic_type_count": 0,
            "semantic_pair_count": 0,
            "info_cluster_count": 0,
            "skeleton_count": 0,
            "top_semantic_type_share": 0.0,
            "top_semantic_pair_share": 0.0,
            "top_info_cluster_share": 0.0,
            "top_skeleton_share": 0.0,
        }
    semantics = Counter()
    clusters = Counter()
    semantic_pairs = Counter(df["semantic_pair"].astype(str))
    skeletons = Counter(df["skeleton_key"].astype(str))
    for val in df["input_semantic_types"].fillna(""):
        for item in str(val).split("|"):
            if item:
                semantics[item] += 1
    for val in df["input_clusters"].fillna(""):
        for item in str(val).split("|"):
            if item:
                clusters[item] += 1
    rows = len(df)
    return {
        "queue": queue_name,
        "row_count": rows,
        "semantic_type_count": len(semantics),
        "semantic_pair_count": len(semantic_pairs),
        "info_cluster_count": len(clusters),
        "skeleton_count": len(skeletons),
        "top_semantic_type_share": max(semantics.values(), default=0) / rows,
        "top_semantic_pair_share": max(semantic_pairs.values(), default=0) / rows,
        "top_info_cluster_share": max(clusters.values(), default=0) / rows,
        "top_skeleton_share": max(skeletons.values(), default=0) / rows,
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source0 = read_json(A7INPUT0 / "a7input0_manifest.json")
    source1 = read_json(A7INPUT1 / "a7input1_manifest.json")
    if not source0.get("decision", "").startswith("PASS_"):
        raise SystemExit(f"A7INPUT-0 not ready: {source0.get('decision')}")
    if not source1.get("authorizes_core54_queue_builder_contract"):
        raise SystemExit(f"A7INPUT-1 does not authorize queue builder: {source1.get('decision')}")

    registry_df = pd.read_csv(A7INPUT0 / "a7input0_input_approval_registry.csv")
    policy = read_json(A7INPUT0 / "a7input0_routing_policy.json")
    formulas = pd.read_csv(A7FF_VERSION / "a7ff_v20260530_formula_index.csv")
    enriched = enrich_candidates(formulas, registry_df)

    mode_rows = []
    for mode in ["ordinary_alpha", "interaction_alpha", "rescue_lane"]:
        decisions = enriched.apply(lambda row: classify_mode(row, mode, policy), axis=1)
        view = enriched.copy()
        view["mode"] = mode
        view["mode_decision"] = [item[0] for item in decisions]
        view["mode_reason"] = [item[1] for item in decisions]
        mode_rows.append(view)
    trace = pd.concat(mode_rows, ignore_index=True)
    accepted = trace[trace["mode_decision"].eq("accept")].copy()
    rejected = trace[trace["mode_decision"].eq("reject")].copy()

    ordinary_candidates = accepted[accepted["mode"].eq("ordinary_alpha")].copy()
    interaction_candidates = accepted[accepted["mode"].eq("interaction_alpha")].copy()
    rescue_candidates = accepted[accepted["mode"].eq("rescue_lane")].copy()

    ordinary_queue = cap_queue(
        ordinary_candidates,
        target_count=2400,
        max_cluster_share=float(policy["ordinary_alpha"].get("max_same_info_cluster_share", 0.2)),
        max_semantic_share=0.4,
        max_semantic_pair_share=0.15,
        max_skeleton_share=0.25,
    )
    interaction_queue = cap_queue(
        interaction_candidates,
        target_count=2400,
        max_cluster_share=0.25,
        max_semantic_share=0.45,
        max_semantic_pair_share=0.15,
        max_skeleton_share=0.25,
    )
    rescue_queue = cap_queue(
        rescue_candidates,
        target_count=600,
        max_cluster_share=0.5,
        max_semantic_share=0.8,
        max_semantic_pair_share=0.8,
        max_skeleton_share=0.5,
    )

    columns_to_drop = ["all_tags", "all_clusters", "all_semantics"]
    rejected_out = rejected.drop(columns=columns_to_drop, errors="ignore")
    mode_summary = (
        trace.groupby(["mode", "mode_decision", "mode_reason"], as_index=False)
        .agg(row_count=("blueprint_id", "count"))
        .sort_values(["mode", "mode_decision", "row_count"], ascending=[True, True, False])
    )
    queue_summary = pd.DataFrame(
        [
            summarize_queue(ordinary_queue, "ordinary_alpha"),
            summarize_queue(interaction_queue, "interaction_alpha"),
            summarize_queue(rescue_queue, "rescue_lane"),
        ]
    )
    reject_summary = (
        rejected_out.groupby(["mode", "mode_reason"], as_index=False)
        .agg(row_count=("blueprint_id", "count"))
        .sort_values(["mode", "row_count"], ascending=[True, False])
    )
    family_balance = (
        pd.concat(
            [
                ordinary_queue.assign(queue="ordinary_alpha"),
                interaction_queue.assign(queue="interaction_alpha"),
                rescue_queue.assign(queue="rescue_lane"),
            ],
            ignore_index=True,
        )
        .groupby(["queue", "semantic_pair", "motif"], as_index=False)
        .agg(row_count=("blueprint_id", "count"))
        .sort_values(["queue", "row_count"], ascending=[True, False])
    )
    cluster_audit = (
        pd.concat(
            [
                ordinary_queue.assign(queue="ordinary_alpha"),
                interaction_queue.assign(queue="interaction_alpha"),
                rescue_queue.assign(queue="rescue_lane"),
            ],
            ignore_index=True,
        )
        .assign(input_clusters=lambda df: df["input_clusters"].fillna(""))
        .loc[:, ["queue", "blueprint_id", "input_clusters", "input_semantic_types", "skeleton_key"]]
    )
    cluster_rows = []
    for _, row in cluster_audit.iterrows():
        for cluster in str(row["input_clusters"]).split("|"):
            if cluster:
                cluster_rows.append(
                    {
                        "queue": row["queue"],
                        "info_cluster_id": cluster,
                        "blueprint_id": row["blueprint_id"],
                        "input_semantic_types": row["input_semantic_types"],
                        "skeleton_key": row["skeleton_key"],
                    }
                )
    cluster_df = pd.DataFrame(cluster_rows)
    if not cluster_df.empty:
        cluster_summary = (
            cluster_df.groupby(["queue", "info_cluster_id"], as_index=False)
            .agg(row_count=("blueprint_id", "count"))
            .sort_values(["queue", "row_count"], ascending=[True, False])
        )
        cluster_summary = cluster_summary.merge(
            cluster_summary.groupby("queue", as_index=False).agg(queue_rows=("row_count", "sum")),
            on="queue",
            how="left",
        )
        cluster_summary["share"] = cluster_summary["row_count"] / cluster_summary["queue_rows"].clip(lower=1)
    else:
        cluster_summary = pd.DataFrame(columns=["queue", "info_cluster_id", "row_count", "queue_rows", "share"])

    ordinary_ok = len(ordinary_queue) > 0
    interaction_ok = len(interaction_queue) > 0
    rescue_separated = "rescue_lane" in set(queue_summary["queue"])
    no_hard_blocked_accepted = not (
        pd.concat([ordinary_queue, interaction_queue, rescue_queue], ignore_index=True)["input_tags"]
        .fillna("")
        .str.contains("A7INPUT_HARD_BLOCKED|A7INPUT_REVIEW_REQUIRED")
        .any()
    )
    no_condition_only_alpha = not ordinary_queue["input_tags"].fillna("").str.contains(
        "A7INPUT_CONDITION_NEUTRALIZER_ONLY"
    ).any()
    ordinary_top_cluster = float(queue_summary.loc[queue_summary["queue"].eq("ordinary_alpha"), "top_info_cluster_share"].iloc[0])
    ordinary_top_semantic = float(queue_summary.loc[queue_summary["queue"].eq("ordinary_alpha"), "top_semantic_type_share"].iloc[0])
    ordinary_top_pair = float(queue_summary.loc[queue_summary["queue"].eq("ordinary_alpha"), "top_semantic_pair_share"].iloc[0])
    interaction_top_pair = float(queue_summary.loc[queue_summary["queue"].eq("interaction_alpha"), "top_semantic_pair_share"].iloc[0])
    decision = (
        "PASS_A7INPUT2_TAG_AWARE_QUEUE_BUILDER_READY_FOR_CORE54"
        if ordinary_ok
        and interaction_ok
        and rescue_separated
        and no_hard_blocked_accepted
        and no_condition_only_alpha
        and ordinary_top_cluster <= 0.30
        and ordinary_top_semantic <= 0.45
        and ordinary_top_pair <= 0.20
        and interaction_top_pair <= 0.20
        else "HOLD_A7INPUT2_TAG_AWARE_QUEUE_BUILDER_NEEDS_REPAIR"
    )
    manifest = {
        "stage": "A7INPUT-2",
        "generated_at": now_utc(),
        "source_stages": ["A7INPUT-0", "A7INPUT-1", "A7FF-v20260530"],
        "source_decisions": [source0.get("decision"), source1.get("decision")],
        "decision": decision,
        "formula_index_rows": int(len(formulas)),
        "ordinary_alpha_candidate_count_before_caps": int(len(ordinary_candidates)),
        "interaction_candidate_count_before_caps": int(len(interaction_candidates)),
        "rescue_candidate_count_before_caps": int(len(rescue_candidates)),
        "ordinary_alpha_queue_count": int(len(ordinary_queue)),
        "interaction_queue_count": int(len(interaction_queue)),
        "rescue_queue_count": int(len(rescue_queue)),
        "rejected_route_rows": int(len(rejected_out)),
        "ordinary_top_info_cluster_share": ordinary_top_cluster,
        "ordinary_top_semantic_type_share": ordinary_top_semantic,
        "ordinary_top_semantic_pair_share": ordinary_top_pair,
        "interaction_top_semantic_pair_share": interaction_top_pair,
        "queue_pass_thresholds": {
            "ordinary_top_info_cluster_share_lte": 0.30,
            "ordinary_top_semantic_type_share_lte": 0.45,
            "ordinary_top_semantic_pair_share_lte": 0.20,
            "interaction_top_semantic_pair_share_lte": 0.20,
        },
        "no_hard_blocked_fields_accepted": bool(no_hard_blocked_accepted),
        "no_condition_only_ordinary_alpha_accepted": bool(no_condition_only_alpha),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core54_queue_builder_contract": decision.startswith("PASS_"),
        "authorizes_core55_numeric_preflight": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    authorization = {
        "authorized": {
            "A7FF-CORE54 input-tag-aware queue builder contract": decision.startswith("PASS_"),
        },
        "not_authorized": {
            "numeric_replay": True,
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
        },
    }

    ordinary_queue.to_csv(RUNTIME / "a7input2_ordinary_alpha_queue.csv", index=False)
    interaction_queue.to_csv(RUNTIME / "a7input2_interaction_queue.csv", index=False)
    rescue_queue.to_csv(RUNTIME / "a7input2_rescue_queue.csv", index=False)
    rejected_out.to_csv(RUNTIME / "a7input2_rejected_queue.csv", index=False)
    mode_summary.to_csv(RUNTIME / "a7input2_mode_filter_summary.csv", index=False)
    queue_summary.to_csv(RUNTIME / "a7input2_queue_summary.csv", index=False)
    cluster_summary.to_csv(RUNTIME / "a7input2_info_cluster_cap_audit.csv", index=False)
    family_balance.to_csv(RUNTIME / "a7input2_field_family_balance.csv", index=False)
    reject_summary.to_csv(RUNTIME / "a7input2_reject_reason_summary.csv", index=False)
    write_json(RUNTIME / "a7input2_queue_manifest.json", manifest)
    write_json(RUNTIME / "a7input2_authorization_matrix.json", authorization)

    report = [
        "# CRYPTO A7INPUT-2 TAG-AWARE QUEUE BUILDER",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7INPUT-2 converts the independent input approval tags into concrete ordinary-alpha, interaction-alpha, and rescue-lane queues. It does not execute replay, formula search, alpha proof, or live/paper/shadow routing.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Queue Summary",
        "",
        md_table(queue_summary),
        "",
        "## Mode Filter Summary",
        "",
        md_table(mode_summary, 80),
        "",
        "## Info Cluster Cap Audit",
        "",
        md_table(cluster_summary, 80),
        "",
        "## Field Family Balance",
        "",
        md_table(family_balance, 80),
        "",
        "## Reject Reason Summary",
        "",
        md_table(reject_summary, 80),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
