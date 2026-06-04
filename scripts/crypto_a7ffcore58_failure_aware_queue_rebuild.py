from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
VERSION = REPO / "runtime" / "a7ff_version_20260530"
CORE56 = REPO / "runtime" / "a7ffcore56_bounded_replay_preflight"
CORE57 = REPO / "runtime" / "a7ffcore57_replay_failure_decomposition"
RUNTIME = REPO / "runtime" / "a7ffcore58_failure_aware_queue_rebuild"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE58_FAILURE_AWARE_QUEUE_REBUILD_20260604.md"


NUMERIC_QUEUE_TARGET = 1200
MATERIALIZATION_REPAIR_TARGET = 1200


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 60) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def queue_score(row: pd.Series, failed_semantics: set[str], failed_motifs: set[str]) -> float:
    score = 0.0
    semantic = str(row.get("semantic_pair", ""))
    motif = str(row.get("motif", ""))
    role = str(row.get("candidate_role", ""))
    level = str(row.get("level", ""))
    priority = str(row.get("generation_priority", ""))
    if semantic not in failed_semantics:
        score += 50.0
    if "funding_like" in semantic:
        score += 24.0
    if "positioning_like" in semantic:
        score += 18.0
    if "liquidity_like" in semantic:
        score += 10.0
    if "state_or_taxonomy" in semantic or level.startswith("L3"):
        score += 8.0
    if role == "ordinary_alpha_valid":
        score += 12.0
    elif role == "role_mixed_allowed":
        score += 6.0
    if priority == "P0":
        score += 8.0
    elif priority == "P1":
        score += 5.0
    if motif not in failed_motifs:
        score += 6.0
    # CORE56 showed repeated sign/shape controls; do not ban these motifs, but lower their default priority.
    if motif in {"safe_div_abs", "mul", "single", "gated_sign", "sub", "spread_rank", "smooth_mul", "signed_spread"}:
        score -= 3.0
    return score


def balanced_select(
    pool: pd.DataFrame,
    target: int,
    semantic_cap_share: float,
    motif_cap_share: float,
    skeleton_cap_share: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    semantic_counts: Counter[str] = Counter()
    motif_counts: Counter[str] = Counter()
    skeleton_counts: Counter[str] = Counter()
    production_seen: set[str] = set()
    semantic_cap = max(1, int(target * semantic_cap_share))
    motif_cap = max(1, int(target * motif_cap_share))
    skeleton_cap = max(1, int(target * skeleton_cap_share))
    for _, row in pool.iterrows():
        reasons = []
        semantic = str(row.get("semantic_pair", ""))
        motif = str(row.get("motif", ""))
        skeleton = str(row.get("skeleton_key", ""))
        production = str(row.get("production_key", ""))
        if len(selected) >= target:
            reasons.append("queue_full")
        if semantic_counts[semantic] >= semantic_cap:
            reasons.append("semantic_cap")
        if motif_counts[motif] >= motif_cap:
            reasons.append("motif_cap")
        if skeleton and skeleton_counts[skeleton] >= skeleton_cap:
            reasons.append("skeleton_cap")
        if production and production in production_seen:
            reasons.append("production_duplicate")
        if reasons:
            out = row.to_dict()
            out["reject_reason"] = "|".join(reasons)
            rejected.append(out)
            continue
        out = row.to_dict()
        selected.append(out)
        semantic_counts[semantic] += 1
        motif_counts[motif] += 1
        if skeleton:
            skeleton_counts[skeleton] += 1
        if production:
            production_seen.add(production)
    return pd.DataFrame(selected), pd.DataFrame(rejected)


def summary_by(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    return (
        df.groupby(keys, as_index=False, dropna=False)
        .agg(
            row_count=("blueprint_id", "count"),
            formula_count=("blueprint_id", "nunique"),
            median_score=("core58_score", "median"),
            max_score=("core58_score", "max"),
        )
        .sort_values(["formula_count", "row_count"], ascending=[False, False])
    )


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    source = read_json(CORE57 / "a7ffcore57_manifest.json")
    if not source.get("authorizes_core58_failure_aware_queue_rebuild"):
        raise SystemExit(f"CORE57 does not authorize CORE58: {source.get('decision')}")

    index = read_csv(VERSION / "a7ff_v20260530_formula_index.csv")
    failed = read_csv(CORE56 / "a7ffcore56_replay_metrics.csv")
    policy = read_csv(CORE57 / "a7ffcore57_repair_policy.csv")
    if index.empty:
        raise SystemExit("missing A7FF version formula index")
    failed_blueprints = set(failed["blueprint_id"].astype(str)) if not failed.empty else set()
    failed_productions = set(failed["production_key"].dropna().astype(str)) if not failed.empty else set()
    failed_skeletons = set(failed["skeleton_key"].dropna().astype(str)) if not failed.empty else set()
    failed_semantics = set(
        policy.loc[policy["policy_scope"].eq("semantic_pair") & policy["action"].eq("downweight_or_block_as_alpha"), "key"].astype(str)
    )
    failed_motifs = set(
        policy.loc[policy["policy_scope"].eq("motif") & policy["action"].eq("downweight_or_block_as_alpha"), "key"].astype(str)
    )

    work = index.copy()
    work["in_company_numeric_wave_queue"] = as_bool(work["in_company_numeric_wave_queue"])
    work["in_materialization_queue"] = as_bool(work["in_materialization_queue"])
    work["core58_exact_core56_blueprint"] = work["blueprint_id"].astype(str).isin(failed_blueprints)
    work["core58_exact_core56_production"] = work["production_key"].astype(str).isin(failed_productions)
    work["core58_core56_skeleton"] = work["skeleton_key"].astype(str).isin(failed_skeletons)
    work["core58_failed_semantic_pair"] = work["semantic_pair"].astype(str).isin(failed_semantics)
    work["core58_failed_motif"] = work["motif"].astype(str).isin(failed_motifs)
    work["core58_score"] = work.apply(queue_score, axis=1, failed_semantics=failed_semantics, failed_motifs=failed_motifs)
    work["core58_score"] -= np.where(work["core58_exact_core56_production"], 1000.0, 0.0)
    work["core58_score"] -= np.where(work["core58_exact_core56_blueprint"], 1000.0, 0.0)
    work["core58_score"] -= np.where(work["core58_core56_skeleton"], 15.0, 0.0)
    work["core58_score"] -= np.where(work["core58_failed_semantic_pair"], 10.0, 0.0)
    work["core58_score"] -= np.where(work["core58_failed_motif"], 5.0, 0.0)

    eligible = work[
        ~work["core58_exact_core56_blueprint"]
        & ~work["core58_exact_core56_production"]
        & work["candidate_role"].isin(["ordinary_alpha_valid", "role_mixed_allowed", "exploratory_signal_probe"])
    ].copy()

    numeric_pool = eligible[eligible["in_company_numeric_wave_queue"]].sort_values(
        ["core58_score", "generation_priority", "blueprint_id"], ascending=[False, True, True]
    )
    numeric_queue, numeric_rejects = balanced_select(numeric_pool, NUMERIC_QUEUE_TARGET, 0.30, 0.18, 0.12)
    numeric_queue["core58_queue"] = "numeric_replay_repair"
    numeric_rejects["core58_queue"] = "numeric_replay_repair_rejected"

    material_pool = eligible[~eligible["in_company_numeric_wave_queue"]].sort_values(
        ["core58_score", "generation_priority", "blueprint_id"], ascending=[False, True, True]
    )
    material_queue, material_rejects = balanced_select(material_pool, MATERIALIZATION_REPAIR_TARGET, 0.28, 0.18, 0.12)
    material_queue["core58_queue"] = "materialization_repair"
    material_rejects["core58_queue"] = "materialization_repair_rejected"

    combined = pd.concat([numeric_queue, material_queue], ignore_index=True)
    rejected = pd.concat([numeric_rejects, material_rejects], ignore_index=True)
    combined.to_csv(RUNTIME / "a7ffcore58_failure_aware_queue.csv", index=False)
    numeric_queue.to_csv(RUNTIME / "a7ffcore58_numeric_replay_repair_queue.csv", index=False)
    material_queue.to_csv(RUNTIME / "a7ffcore58_materialization_repair_queue.csv", index=False)
    rejected.to_csv(RUNTIME / "a7ffcore58_rejected_queue_rows.csv", index=False)

    coverage_semantic = summary_by(combined, ["core58_queue", "semantic_pair"])
    coverage_motif = summary_by(combined, ["core58_queue", "motif"])
    coverage_level = summary_by(combined, ["core58_queue", "level"])
    coverage_role = summary_by(combined, ["core58_queue", "candidate_role"])
    exclusion_summary = (
        work[[
            "core58_exact_core56_blueprint",
            "core58_exact_core56_production",
            "core58_core56_skeleton",
            "core58_failed_semantic_pair",
            "core58_failed_motif",
        ]]
        .sum()
        .reset_index()
        .rename(columns={"index": "exclusion_or_penalty_flag", 0: "row_count"})
    )
    reject_summary = (
        rejected.assign(reject_reason=rejected["reject_reason"].astype(str).str.split("|"))
        .explode("reject_reason")
        .groupby(["core58_queue", "reject_reason"], as_index=False, dropna=False)
        .size()
        .rename(columns={"size": "row_count"})
        .sort_values("row_count", ascending=False)
        if not rejected.empty
        else pd.DataFrame()
    )
    coverage_semantic.to_csv(RUNTIME / "a7ffcore58_coverage_by_semantic_pair.csv", index=False)
    coverage_motif.to_csv(RUNTIME / "a7ffcore58_coverage_by_motif.csv", index=False)
    coverage_level.to_csv(RUNTIME / "a7ffcore58_coverage_by_level.csv", index=False)
    coverage_role.to_csv(RUNTIME / "a7ffcore58_coverage_by_role.csv", index=False)
    exclusion_summary.to_csv(RUNTIME / "a7ffcore58_exclusion_penalty_summary.csv", index=False)
    reject_summary.to_csv(RUNTIME / "a7ffcore58_reject_reason_summary.csv", index=False)

    numeric_semantic_count = int(numeric_queue["semantic_pair"].nunique()) if not numeric_queue.empty else 0
    material_semantic_count = int(material_queue["semantic_pair"].nunique()) if not material_queue.empty else 0
    numeric_top_semantic_share = float(numeric_queue["semantic_pair"].value_counts(normalize=True).iloc[0]) if not numeric_queue.empty else 0.0
    material_top_semantic_share = float(material_queue["semantic_pair"].value_counts(normalize=True).iloc[0]) if not material_queue.empty else 0.0
    blockers = []
    if len(numeric_queue) < 512:
        blockers.append("numeric_queue_lt_512")
    if numeric_semantic_count < 4:
        blockers.append("numeric_semantic_pair_count_lt_4")
    if numeric_top_semantic_share > 0.35:
        blockers.append("numeric_top_semantic_share_gt_35pct")
    if material_semantic_count < 4:
        blockers.append("materialization_semantic_pair_count_lt_4")
    decision = "PASS_A7FFCORE58_FAILURE_AWARE_QUEUE_REBUILT_READY_FOR_CORE59" if not blockers else "HOLD_A7FFCORE58_QUEUE_COVERAGE_WEAK"
    manifest = {
        "stage": "A7FF-CORE58",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE57",
        "source_decision": source.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "formula_index_rows": int(len(index)),
        "eligible_rows": int(len(eligible)),
        "numeric_queue_rows": int(len(numeric_queue)),
        "materialization_repair_queue_rows": int(len(material_queue)),
        "numeric_semantic_pair_count": numeric_semantic_count,
        "materialization_semantic_pair_count": material_semantic_count,
        "numeric_top_semantic_share": numeric_top_semantic_share,
        "materialization_top_semantic_share": material_top_semantic_share,
        "failed_semantic_pair_count_from_core57": int(len(failed_semantics)),
        "failed_motif_count_from_core57": int(len(failed_motifs)),
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core59_numeric_repair_execution": decision.startswith("PASS_"),
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffcore58_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ffcore58_authorization_matrix.json",
        {
            "authorized": {"A7FF-CORE59 numeric repair execution": decision.startswith("PASS_")},
            "not_authorized": {"large_search": True, "alpha_proof": True, "shadow_paper_live": True},
        },
    )

    report = [
        "# CRYPTO A7FF-CORE58 FAILURE-AWARE QUEUE REBUILD",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE58 rebuilds numeric/materialization queues from the A7FF version index using CORE56/57 failure evidence. It does not execute replay or search.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Coverage By Semantic Pair",
        "",
        md_table(coverage_semantic),
        "",
        "## Coverage By Motif",
        "",
        md_table(coverage_motif),
        "",
        "## Coverage By Role",
        "",
        md_table(coverage_role),
        "",
        "## Exclusion / Penalty Summary",
        "",
        md_table(exclusion_summary),
        "",
        "## Reject Reason Summary",
        "",
        md_table(reject_summary),
        "",
        "## Boundary",
        "",
        "```text",
        "replay executed: false",
        "search executed: false",
        "May used: false",
        "large search / alpha proof / shadow / paper / live: false",
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
