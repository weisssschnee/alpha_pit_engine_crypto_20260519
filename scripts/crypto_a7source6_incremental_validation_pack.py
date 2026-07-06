from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts import crypto_a7search6_validation_pack as base  # noqa: E402


STAGE = "A7SOURCE6-INCREMENTAL-VALIDATION-PACK"
DEFAULT_ACCEPTED_ROOT = REPO / "runtime" / "a7search7_strict_validation_reward_source5_py_aggregate_20260706"
DEFAULT_RUNTIME = REPO / "runtime" / "a7source6_incremental_validation_pack_20260706"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SOURCE6_INCREMENTAL_VALIDATION_PACK_20260706.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def md_table(frame: pd.DataFrame, max_rows: int = 40) -> str:
    if frame.empty:
        return "`<empty>`"
    view = frame.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```text\n" + view.to_string(index=False) + "\n```"


def read_csv(path: Path) -> pd.DataFrame:
    return base.read_csv_or_empty(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build(args: argparse.Namespace) -> dict[str, Any]:
    queue_path = base.build_queue(args.accepted_root, args.runtime, args.max_fields_per_formula)
    queue = read_csv(queue_path)
    compressed = read_csv(args.runtime / "a7search6_validation_compressed_mechanisms.csv")
    risks = read_csv(args.runtime / "a7search6_validation_field_timing_risk.csv")
    group_summary = read_csv(args.runtime / "a7search6_validation_queue_group_summary.csv")

    alias_outputs = {
        "compressed_mechanisms": args.runtime / "a7source6_validation_compressed_mechanisms.csv",
        "field_timing_risk": args.runtime / "a7source6_validation_field_timing_risk.csv",
        "queue": args.runtime / "a7source6_validation_ablation_queue.csv",
        "queue_group_summary": args.runtime / "a7source6_validation_queue_group_summary.csv",
    }
    compressed.to_csv(alias_outputs["compressed_mechanisms"], index=False)
    risks.to_csv(alias_outputs["field_timing_risk"], index=False)
    queue.to_csv(alias_outputs["queue"], index=False)
    group_summary.to_csv(alias_outputs["queue_group_summary"], index=False)

    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": "PASS_A7SOURCE6_INCREMENTAL_VALIDATION_QUEUE_BUILT" if not queue.empty else "HOLD_A7SOURCE6_EMPTY_QUEUE",
        "accepted_root": str(args.accepted_root),
        "accepted_root_relative": repo_relative(args.accepted_root),
        "runtime": str(args.runtime),
        "runtime_relative": repo_relative(args.runtime),
        "compressed_unique_blueprints": int(compressed["blueprint_id"].nunique()) if "blueprint_id" in compressed else 0,
        "queue_rows": int(queue.shape[0]),
        "field_timing_rows": int(risks.shape[0]),
        "max_fields_per_formula": int(args.max_fields_per_formula),
        "authorizes_validation_reward": not queue.empty,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "outputs": {key: str(value) for key, value in alias_outputs.items()},
        "outputs_relative": {key: repo_relative(value) for key, value in alias_outputs.items()},
        "compatibility_queue": str(queue_path),
        "compatibility_queue_relative": repo_relative(queue_path),
    }
    write_json(args.runtime / "a7source6_validation_build_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def attach_queue_metadata(frame: pd.DataFrame, queue: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "blueprint_id",
        "source_blueprint_id",
        "validation_group",
        "validation_note",
        "source_rank",
        "source_min_oos_floor_sortino",
        "semantic_pair",
        "motif",
    ]
    if frame.empty or queue.empty:
        return frame
    existing = [col for col in cols if col in queue.columns]
    meta = queue[existing].drop_duplicates("blueprint_id") if "blueprint_id" in existing else pd.DataFrame()
    if meta.empty or "blueprint_id" not in frame.columns:
        return frame
    return frame.merge(meta, on="blueprint_id", how="left", suffixes=("", "_queue"))


def summarize(args: argparse.Namespace) -> dict[str, Any]:
    queue = read_csv(args.runtime / "a7source6_validation_ablation_queue.csv")
    if queue.empty:
        queue = read_csv(args.runtime / "a7search6_validation_ablation_queue.csv")
    compressed = read_csv(args.runtime / "a7source6_validation_compressed_mechanisms.csv")
    if compressed.empty:
        compressed = read_csv(args.runtime / "a7search6_validation_compressed_mechanisms.csv")
    risks = read_csv(args.runtime / "a7source6_validation_field_timing_risk.csv")
    if risks.empty:
        risks = read_csv(args.runtime / "a7search6_validation_field_timing_risk.csv")

    leaderboard = attach_queue_metadata(
        read_csv(args.reward_aggregate_root / "a7v3s0_reward_candidate_leaderboard_all.csv"), queue
    )
    accepted = attach_queue_metadata(read_csv(args.reward_aggregate_root / "a7v3s0_reward_accepted_enriched.csv"), queue)
    rejections = attach_queue_metadata(read_csv(args.reward_aggregate_root / "a7v3s0_reward_rejections_enriched.csv"), queue)
    errors = read_csv(args.reward_aggregate_root / "a7v3s0_reward_eval_errors_all.csv")
    reward_manifest = read_json(args.reward_aggregate_root / "a7v3s0_reward_sharded_aggregate_manifest.json")

    accepted_summary = (
        accepted.groupby(["source_blueprint_id", "validation_group", "blueprint_id", "horizon_h"], dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            train_sortino=("train_sortino", "max"),
            validation_sortino=("validation_sortino", "max"),
            test_sortino=("test_sortino", "max"),
            recent_sortino=("recent_sortino", "max"),
            min_oos_floor_sortino=("min_oos_floor_sortino", "max"),
            stress_floor_sortino=("stress_floor_sortino", "max"),
            recent_shuffle_control_ratio=("recent_shuffle_control_ratio", "min"),
            formula=("formula", "first"),
        )
        .reset_index()
        .sort_values(["min_oos_floor_sortino", "recent_sortino"], ascending=False)
        if not accepted.empty
        else pd.DataFrame()
    )
    group_summary = (
        leaderboard.groupby("validation_group", dropna=False)
        .agg(
            candidates=("blueprint_id", "nunique"),
            gate_pass_rows=("gate_pass", lambda s: int(s.astype(bool).sum())),
            accepted_unique=("blueprint_id", lambda s: int(accepted.loc[accepted["blueprint_id"].isin(set(s)), "blueprint_id"].nunique()) if not accepted.empty else 0),
            max_recent_sortino=("recent_sortino", "max"),
            max_min_oos_floor_sortino=("min_oos_floor_sortino", "max"),
        )
        .reset_index()
        .sort_values(["gate_pass_rows", "max_min_oos_floor_sortino"], ascending=False)
        if not leaderboard.empty
        else pd.DataFrame()
    )

    source_rows: list[dict[str, Any]] = []
    if "source_blueprint_id" in queue.columns:
        for source_id, source_queue in queue.groupby("source_blueprint_id", dropna=False):
            acc = accepted[accepted["source_blueprint_id"].astype(str).eq(str(source_id))] if not accepted.empty else pd.DataFrame()
            canonical = int(acc["validation_group"].eq("canonical").sum()) if not acc.empty else 0
            single = int(acc["validation_group"].eq("single_leg").sum()) if not acc.empty else 0
            neighbor = int(acc["validation_group"].isin(["operator_neighbor", "operator_text_ablation"]).sum()) if not acc.empty else 0
            if canonical > 0 and single == 0 and neighbor == 0:
                decision = "PASS_INCREMENTAL_INTERACTION_EVIDENCE"
            elif canonical > 0:
                decision = "HOLD_NON_UNIQUE_INFORMATION"
            else:
                decision = "HOLD_CANONICAL_DID_NOT_REPASS"
            source_rows.append(
                {
                    "source_blueprint_id": source_id,
                    "source_rank": pd.to_numeric(source_queue["source_rank"], errors="coerce").min()
                    if "source_rank" in source_queue
                    else "",
                    "canonical_accepted_rows": canonical,
                    "single_leg_accepted_rows": single,
                    "operator_neighbor_accepted_rows": neighbor,
                    "accepted_rows": int(acc.shape[0]),
                    "decision": decision,
                }
            )
    source_decisions = pd.DataFrame(source_rows).sort_values(["decision", "source_rank"]) if source_rows else pd.DataFrame()

    risk_summary = (
        risks.groupby(["field_family", "timing_risk_note"], dropna=False)
        .agg(fields=("field", "nunique"), source_blueprints=("source_blueprint_id", "nunique"))
        .reset_index()
        .sort_values(["source_blueprints", "fields"], ascending=False)
        if not risks.empty
        else pd.DataFrame()
    )
    rejection_summary = (
        rejections.groupby(["validation_group", "hard_reject_reason"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        if not rejections.empty and "hard_reject_reason" in rejections.columns
        else pd.DataFrame()
    )

    outputs = {
        "accepted_summary": args.runtime / "a7source6_validation_accepted_summary.csv",
        "group_summary": args.runtime / "a7source6_validation_group_summary.csv",
        "source_decisions": args.runtime / "a7source6_validation_source_decisions.csv",
        "field_timing_risk_summary": args.runtime / "a7source6_validation_field_timing_risk_summary.csv",
        "rejection_summary": args.runtime / "a7source6_validation_rejection_summary.csv",
    }
    accepted_summary.to_csv(outputs["accepted_summary"], index=False)
    group_summary.to_csv(outputs["group_summary"], index=False)
    source_decisions.to_csv(outputs["source_decisions"], index=False)
    risk_summary.to_csv(outputs["field_timing_risk_summary"], index=False)
    rejection_summary.to_csv(outputs["rejection_summary"], index=False)

    incremental_count = int(source_decisions["decision"].eq("PASS_INCREMENTAL_INTERACTION_EVIDENCE").sum()) if not source_decisions.empty else 0
    non_unique_count = int(source_decisions["decision"].eq("HOLD_NON_UNIQUE_INFORMATION").sum()) if not source_decisions.empty else 0
    canonical_failed_count = int(source_decisions["decision"].eq("HOLD_CANONICAL_DID_NOT_REPASS").sum()) if not source_decisions.empty else 0
    eval_error_rows = int(reward_manifest.get("eval_error_rows", errors.shape[0]) or 0)
    if eval_error_rows > 0:
        decision = "HOLD_A7SOURCE6_VALIDATION_EVAL_ERRORS"
    elif incremental_count > 0:
        decision = "PASS_A7SOURCE6_INCREMENTAL_EVIDENCE_FOUND"
    elif non_unique_count > 0:
        decision = "HOLD_A7SOURCE6_NON_UNIQUE_INFORMATION"
    else:
        decision = "HOLD_A7SOURCE6_CANONICAL_FAILED"

    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": decision,
        "runtime": str(args.runtime),
        "runtime_relative": repo_relative(args.runtime),
        "report": str(args.report),
        "report_relative": repo_relative(args.report),
        "reward_aggregate_root": str(args.reward_aggregate_root),
        "reward_aggregate_root_relative": repo_relative(args.reward_aggregate_root),
        "queue_rows": int(queue.shape[0]),
        "compressed_unique_blueprints": int(compressed["blueprint_id"].nunique()) if "blueprint_id" in compressed else 0,
        "reward_rows": int(reward_manifest.get("reward_rows", leaderboard.shape[0]) or 0),
        "accepted_rows": int(reward_manifest.get("accepted_rows", accepted.shape[0]) or 0),
        "accepted_unique_blueprints": int(reward_manifest.get("accepted_unique_blueprints", accepted["blueprint_id"].nunique() if "blueprint_id" in accepted else 0) or 0),
        "eval_error_rows": eval_error_rows,
        "incremental_source_count": incremental_count,
        "non_unique_source_count": non_unique_count,
        "canonical_failed_source_count": canonical_failed_count,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_next_search_seed_triage": decision.startswith("PASS_"),
        "outputs": {key: str(value) for key, value in outputs.items()},
        "outputs_relative": {key: repo_relative(value) for key, value in outputs.items()},
    }
    write_json(args.runtime / "a7source6_validation_manifest.json", manifest)

    lines = [
        "# CRYPTO A7SOURCE6 Incremental Validation Pack",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This validates whether A7SOURCE5 accepted survivors add information beyond single-leg and nearby-operator baselines. It is not alpha proof and does not authorize shadow, paper, live, or production portfolio construction.",
        "",
        "## Counts",
        "",
        f"- compressed_unique_blueprints: `{manifest['compressed_unique_blueprints']}`",
        f"- validation_queue_rows: `{manifest['queue_rows']}`",
        f"- reward_rows: `{manifest['reward_rows']}`",
        f"- accepted_rows: `{manifest['accepted_rows']}`",
        f"- accepted_unique_blueprints: `{manifest['accepted_unique_blueprints']}`",
        f"- eval_error_rows: `{manifest['eval_error_rows']}`",
        f"- incremental_source_count: `{incremental_count}`",
        f"- non_unique_source_count: `{non_unique_count}`",
        f"- canonical_failed_source_count: `{canonical_failed_count}`",
        "",
        "## Validation Group Summary",
        "",
        md_table(group_summary, 30),
        "",
        "## Source Decisions",
        "",
        md_table(source_decisions, 40),
        "",
        "## Accepted Validation Rows",
        "",
        md_table(accepted_summary, 40),
        "",
        "## Field Timing Risk Summary",
        "",
        md_table(risk_summary, 30),
        "",
        "## Rejection Summary",
        "",
        md_table(rejection_summary, 30),
        "",
        "## Boundary",
        "",
        "- This stage can authorize seed triage only.",
        "- It does not authorize alpha proof, shadow, paper, live, or deployment.",
    ]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accepted-root", type=Path, default=DEFAULT_ACCEPTED_ROOT)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--reward-aggregate-root", type=Path, default=DEFAULT_RUNTIME / "reward_aggregate")
    parser.add_argument("--mode", choices=["build", "summarize"], default="build")
    parser.add_argument("--max-fields-per-formula", type=int, default=3)
    args = parser.parse_args()

    if args.mode == "build":
        build(args)
    else:
        summarize(args)


if __name__ == "__main__":
    main()
