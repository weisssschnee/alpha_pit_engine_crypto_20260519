from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.api.types import is_numeric_dtype
from pandas.errors import EmptyDataError


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7reward1_portfolio_reward_model import (  # noqa: E402
    accepted_for_next_search,
    aggregate_rewards,
    apply_source_lag_policy,
    load_source_lag_passes,
    load_source_policy,
)


DEFAULT_RUN_ROOT = Path(
    r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_reward_sharded_720h_r2_20260613"
)
DEFAULT_RUNTIME = Path(
    r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_reward_sharded_720h_r2_aggregate_20260613"
)
DEFAULT_REPORT = Path(
    r"D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\reports\CRYPTO_A7V3S0_REWARD_SHARDED_AGGREGATE_20260613.md"
)
SHARD_ID_RE = re.compile(r"^a7v3s0_reward_s\d{3}$")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except EmptyDataError:
        return pd.DataFrame()


def md_table(frame: pd.DataFrame, max_rows: int = 30) -> str:
    if frame.empty:
        return "`<empty>`"
    view = frame.head(max_rows).copy()
    for col in view.columns:
        if not is_numeric_dtype(view[col]):
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```text\n" + view.to_string(index=False) + "\n```"


def shard_id_from_path(path: Path) -> str:
    for part in path.parts:
        if SHARD_ID_RE.match(part):
            return part
    return ""


def collect_file(run_root: Path, filename: str) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for path in sorted(run_root.glob(f"shards/a7v3s0_reward_s*/reward_runtime/{filename}")):
        frame = read_csv(path)
        if frame.empty:
            continue
        frame.insert(0, "shard_id", shard_id_from_path(path))
        frame.insert(1, "source_file", str(path))
        rows.append(frame)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def collect_manifests(run_root: Path) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for path in sorted(run_root.glob("shards/a7v3s0_reward_s*/reward_runtime/a7reward1_manifest.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["shard_id"] = shard_id_from_path(path)
        payload["source_file"] = str(path)
        records.append(payload)
    return pd.DataFrame(records)


def collect_queue(run_root: Path) -> pd.DataFrame:
    queue_rows: list[pd.DataFrame] = []
    for path in sorted((run_root / "queue_shards").glob("a7v3s0_reward_s*.csv")):
        frame = read_csv(path)
        if frame.empty:
            continue
        frame.insert(0, "queue_shard_id", path.stem)
        frame.insert(1, "queue_file", str(path))
        queue_rows.append(frame)
    return pd.concat(queue_rows, ignore_index=True) if queue_rows else pd.DataFrame()


def enrich_with_queue(frame: pd.DataFrame, queue: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    out = frame.copy()
    if "expression" not in out.columns:
        out["expression"] = ""
    out["formula"] = out["expression"].fillna("").astype(str)
    if queue.empty or "blueprint_id" not in queue.columns:
        return out

    keep = [
        col
        for col in [
            "blueprint_id",
            "expression",
            "primary_field",
            "secondary_field",
            "level",
            "candidate_role",
            "search_role",
            "production_key",
            "queue_shard_id",
            "representative_blueprint_id",
            "is_signal_identity_representative",
            "signal_weight_exact_fingerprint",
            "signal_weight_quantized_fingerprint",
        ]
        if col in queue.columns
    ]
    lookup = queue[keep].drop_duplicates("blueprint_id", keep="first").copy()
    merged = out.merge(lookup, on="blueprint_id", how="left", suffixes=("", "_queue"))
    for col in [
        "expression",
        "primary_field",
        "secondary_field",
        "level",
        "candidate_role",
        "search_role",
        "production_key",
        "representative_blueprint_id",
        "is_signal_identity_representative",
        "signal_weight_exact_fingerprint",
        "signal_weight_quantized_fingerprint",
    ]:
        qcol = f"{col}_queue"
        if qcol in merged.columns:
            if col in merged.columns:
                merged[col] = merged[col].fillna("").astype(str)
                merged[col] = merged[col].where(merged[col].str.len() > 0, merged[qcol].fillna(""))
            else:
                merged[col] = merged[qcol]
            merged = merged.drop(columns=[qcol])
    if "queue_shard_id" in merged.columns:
        merged["source_queue_shard_id"] = merged["queue_shard_id"]
        merged = merged.drop(columns=["queue_shard_id"])
    merged["formula"] = merged["expression"].fillna("").astype(str)
    return merged


def explode_reasons(rejections: pd.DataFrame) -> pd.DataFrame:
    if rejections.empty or "hard_reject_reasons" not in rejections.columns:
        return pd.DataFrame(columns=["hard_reject_reason", "count"])
    rows: list[dict[str, Any]] = []
    for reasons in rejections["hard_reject_reasons"].fillna("").astype(str):
        parts = [part for part in reasons.split(";") if part]
        if not parts:
            parts = ["<none>"]
        for part in parts:
            rows.append({"hard_reject_reason": part})
    if not rows:
        return pd.DataFrame(columns=["hard_reject_reason", "count"])
    return (
        pd.DataFrame(rows)
        .groupby("hard_reject_reason", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )


def status_audit(run_root: Path, manifests: pd.DataFrame) -> pd.DataFrame:
    status_frames: list[pd.DataFrame] = []
    for path in sorted(run_root.glob("a7v3s0_reward*_status.csv")):
        frame = read_csv(path)
        if frame.empty:
            continue
        frame.insert(0, "status_file", str(path))
        status_frames.append(frame)
    if not status_frames:
        return pd.DataFrame()
    status = pd.concat(status_frames, ignore_index=True)
    done = set(manifests.get("shard_id", pd.Series(dtype=str)).astype(str))
    status["manifest_exists"] = status["shard_id"].astype(str).isin(done)
    status["status_manifest_conflict"] = status["manifest_exists"] & ~status["status"].astype(str).eq("done")
    return status


def expand_exact_signal_aliases(frame: pd.DataFrame, alias_map: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or alias_map.empty:
        return frame.copy()
    required = {"blueprint_id", "representative_blueprint_id"}
    if not required.issubset(alias_map.columns):
        raise RuntimeError(f"alias map missing columns: {sorted(required - set(alias_map.columns))}")
    aliases = alias_map.copy()
    aliases["representative_blueprint_id"] = aliases["representative_blueprint_id"].astype(str)
    aliases["blueprint_id"] = aliases["blueprint_id"].astype(str)
    out = frame.copy()
    out["blueprint_id"] = out["blueprint_id"].astype(str)
    base_columns = list(out.columns)
    merged = out.merge(
        aliases,
        left_on="blueprint_id",
        right_on="representative_blueprint_id",
        how="inner",
        suffixes=("", "_alias"),
    )
    merged["representative_evaluated_blueprint_id"] = merged["blueprint_id"]
    merged["blueprint_id"] = merged["blueprint_id_alias"].astype(str)
    overlay_columns = [
        "expression",
        "semantic_pair",
        "motif",
        "skeleton_key",
        "signal_weight_exact_fingerprint",
        "signal_weight_quantized_fingerprint",
        "signal_weight_similarity_sketch",
        "safediv_node_count",
        "safediv_denominator_min_abs_q01",
        "safediv_denominator_min_abs_q05",
        "safediv_denominator_min_q01_to_median",
        "safediv_denominator_max_near_zero_ratio",
        "safediv_local_rank_stability_min",
        "signal_abs_p99_to_median",
        "signal_top1pct_abs_mass_share",
        "safediv_review_flag",
        "safediv_review_reasons",
    ]
    for column in overlay_columns:
        alias_column = f"{column}_alias"
        if alias_column in merged.columns:
            merged[column] = merged[alias_column]
    keep = list(dict.fromkeys([*base_columns, *overlay_columns, "representative_evaluated_blueprint_id"]))
    return merged[[column for column in keep if column in merged.columns]].copy()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--alias-map", type=Path)
    parser.add_argument("--source-policy", type=Path)
    parser.add_argument("--source-lag-summary", type=Path)
    args = parser.parse_args()

    run_root = args.run_root
    runtime = args.runtime
    runtime.mkdir(parents=True, exist_ok=True)

    queue = collect_queue(run_root)
    manifests = collect_manifests(run_root)
    split_metrics = collect_file(run_root, "a7reward1_split_reward_metrics.csv")
    eval_errors = collect_file(run_root, "a7reward1_eval_errors.csv")
    alias_map = read_csv(args.alias_map) if args.alias_map else pd.DataFrame()
    if not alias_map.empty:
        if not args.source_policy or not args.source_lag_summary:
            raise RuntimeError("alias expansion requires --source-policy and --source-lag-summary")
        split_metrics = expand_exact_signal_aliases(split_metrics, alias_map)
        eval_errors = expand_exact_signal_aliases(eval_errors, alias_map)
        rewards = aggregate_rewards(split_metrics)
        source_policy = load_source_policy(args.source_policy)
        source_lag_pass_ids, source_lag_pass_formulas = load_source_lag_passes(args.source_lag_summary)
        rewards = apply_source_lag_policy(
            rewards,
            source_policy,
            source_lag_pass_ids,
            source_lag_pass_formulas,
        )
        accepted = accepted_for_next_search(rewards)
        rejections = rewards[~rewards.index.isin(accepted.index)].copy()
        queue = alias_map.copy()
    else:
        accepted = collect_file(run_root, "a7reward1_accepted_for_next_search.csv")
        rejections = collect_file(run_root, "a7reward1_validation_gate_rejections.csv")
        rewards = collect_file(run_root, "a7reward1_candidate_reward_leaderboard.csv")
    accepted = enrich_with_queue(accepted, queue)
    rejections = enrich_with_queue(rejections, queue)
    rewards = enrich_with_queue(rewards, queue)
    status = status_audit(run_root, manifests)
    reason_summary = explode_reasons(rejections)

    sort_cols = [col for col in ["min_oos_floor_sortino", "min_oos_sortino", "recent_sortino"] if col in accepted.columns]
    if sort_cols:
        for col in sort_cols:
            accepted[col] = pd.to_numeric(accepted[col], errors="coerce")
        accepted = accepted.sort_values(sort_cols, ascending=[False] * len(sort_cols))

    if not accepted.empty:
        unique_best = accepted.sort_values(sort_cols or ["blueprint_id"], ascending=[False] * len(sort_cols or ["blueprint_id"]))
        unique_best = unique_best.drop_duplicates("blueprint_id", keep="first")
    else:
        unique_best = pd.DataFrame()

    def summary(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
        if frame.empty or not all(key in frame.columns for key in keys):
            return pd.DataFrame()
        return frame.groupby(keys, dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)

    accepted_pair_summary = summary(accepted, ["semantic_pair"])
    accepted_motif_summary = summary(accepted, ["motif"])
    accepted_horizon_summary = summary(accepted, ["horizon_h"])
    accepted_pair_motif_summary = summary(accepted, ["semantic_pair", "motif"])
    decision_summary = summary(manifests, ["decision"])
    if "is_signal_identity_representative" in accepted.columns:
        representative_feedback = accepted[
            accepted["is_signal_identity_representative"].fillna(False).astype(bool)
        ].copy()
    else:
        representative_feedback = accepted.copy()

    outputs = {
        "accepted": runtime / "a7v3s0_reward_accepted_enriched.csv",
        "unique_best": runtime / "a7v3s0_reward_unique_blueprint_best.csv",
        "rejections": runtime / "a7v3s0_reward_rejections_enriched.csv",
        "rejection_reasons": runtime / "a7v3s0_reward_rejection_reason_summary.csv",
        "rewards": runtime / "a7v3s0_reward_candidate_leaderboard_all.csv",
        "split_metrics": runtime / "a7v3s0_reward_split_metrics_all.csv",
        "eval_errors": runtime / "a7v3s0_reward_eval_errors_all.csv",
        "manifests": runtime / "a7v3s0_reward_manifest_summary.csv",
        "status_audit": runtime / "a7v3s0_reward_launcher_status_audit.csv",
        "pair_summary": runtime / "a7v3s0_reward_accepted_pair_summary.csv",
        "motif_summary": runtime / "a7v3s0_reward_accepted_motif_summary.csv",
        "horizon_summary": runtime / "a7v3s0_reward_accepted_horizon_summary.csv",
        "pair_motif_summary": runtime / "a7v3s0_reward_accepted_pair_motif_summary.csv",
        "decision_summary": runtime / "a7v3s0_reward_decision_summary.csv",
        "representative_feedback": runtime / "a7v3s0_reward_identity_representative_feedback.csv",
    }
    accepted.to_csv(outputs["accepted"], index=False)
    unique_best.to_csv(outputs["unique_best"], index=False)
    rejections.to_csv(outputs["rejections"], index=False)
    reason_summary.to_csv(outputs["rejection_reasons"], index=False)
    rewards.to_csv(outputs["rewards"], index=False)
    split_metrics.to_csv(outputs["split_metrics"], index=False)
    eval_errors.to_csv(outputs["eval_errors"], index=False)
    manifests.to_csv(outputs["manifests"], index=False)
    status.to_csv(outputs["status_audit"], index=False)
    accepted_pair_summary.to_csv(outputs["pair_summary"], index=False)
    accepted_motif_summary.to_csv(outputs["motif_summary"], index=False)
    accepted_horizon_summary.to_csv(outputs["horizon_summary"], index=False)
    accepted_pair_motif_summary.to_csv(outputs["pair_motif_summary"], index=False)
    decision_summary.to_csv(outputs["decision_summary"], index=False)
    representative_feedback.to_csv(outputs["representative_feedback"], index=False)

    expected_shards = len(pd.read_csv(run_root / "a7v3s0_reward_shard_plan.csv")) if (run_root / "a7v3s0_reward_shard_plan.csv").exists() else 0
    manifest_count = int(manifests.shape[0])
    accepted_rows = int(accepted.shape[0])
    accepted_unique = int(accepted["blueprint_id"].nunique()) if not accepted.empty and "blueprint_id" in accepted else 0
    accepted_expression_missing = int(accepted["formula"].fillna("").astype(str).eq("").sum()) if not accepted.empty else 0
    status_conflicts = int(status["status_manifest_conflict"].sum()) if not status.empty and "status_manifest_conflict" in status else 0
    eval_error_rows = int(eval_errors.shape[0])
    hard_reject_rows = int(rewards["hard_reject"].fillna(False).astype(bool).sum()) if "hard_reject" in rewards else 0
    valid_reward_rows = int((~rewards["hard_reject"].fillna(True).astype(bool)).sum()) if "hard_reject" in rewards else 0

    decision = (
        "PASS_A7V3S0_REWARD_SHARDED_AGGREGATE_READY"
        if manifest_count == expected_shards and accepted_rows > 0 and accepted_expression_missing == 0 and eval_error_rows == 0
        else "HOLD_A7V3S0_REWARD_SHARDED_AGGREGATE_INCOMPLETE_OR_DIRTY"
    )
    manifest = {
        "stage": "A7V3S0-REWARD-SHARDED-AGGREGATE",
        "generated_at": now_utc(),
        "decision": decision,
        "run_root": str(run_root),
        "runtime": str(runtime),
        "report": str(args.report),
        "expected_shards": expected_shards,
        "manifest_count": manifest_count,
        "accepted_rows": accepted_rows,
        "accepted_unique_blueprints": accepted_unique,
        "accepted_expression_missing": accepted_expression_missing,
        "rejection_rows": int(rejections.shape[0]),
        "reward_rows": int(rewards.shape[0]),
        "split_metric_rows": int(split_metrics.shape[0]),
        "eval_error_rows": eval_error_rows,
        "hard_reject_rows": hard_reject_rows,
        "valid_reward_rows": valid_reward_rows,
        "representative_reward_queue_rows": int(queue["is_signal_identity_representative"].fillna(False).astype(bool).sum()) if "is_signal_identity_representative" in queue else int(queue.shape[0]),
        "expanded_alias_rows": int(alias_map.shape[0]) if not alias_map.empty else 0,
        "exact_signal_alias_rows_saved": int(alias_map.shape[0] - alias_map["representative_blueprint_id"].nunique()) if not alias_map.empty else 0,
        "identity_representative_feedback_rows": int(representative_feedback.shape[0]),
        "identity_representative_feedback_unique_blueprints": int(representative_feedback["blueprint_id"].nunique()) if not representative_feedback.empty else 0,
        "safediv_review_rows": int(rewards["safediv_review_flag"].fillna(False).astype(bool).sum()) if "safediv_review_flag" in rewards else 0,
        "alias_map": str(args.alias_map) if args.alias_map else "",
        "launcher_status_conflicts": status_conflicts,
        "authorizes_next_validation_pack": decision.startswith("PASS"),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "outputs": {key: str(value) for key, value in outputs.items()},
    }
    write_json(runtime / "a7v3s0_reward_sharded_aggregate_manifest.json", manifest)

    top_cols = [
        col
        for col in [
            "blueprint_id",
            "semantic_pair",
            "motif",
            "horizon_h",
            "min_oos_floor_sortino",
            "min_oos_sortino",
            "recent_sortino",
            "recent_shuffle_control_ratio",
            "formula",
        ]
        if col in accepted.columns
    ]
    report_lines = [
        "# CRYPTO A7V3S0 Reward Sharded Aggregate 20260613",
        "",
        f"Decision: `{decision}`",
        "",
        "## Counts",
        "",
        f"- expected_shards: `{expected_shards}`",
        f"- manifest_count: `{manifest_count}`",
        f"- accepted_rows: `{accepted_rows}`",
        f"- accepted_unique_blueprints: `{accepted_unique}`",
        f"- accepted_expression_missing: `{accepted_expression_missing}`",
        f"- reward_rows: `{manifest['reward_rows']}`",
        f"- split_metric_rows: `{manifest['split_metric_rows']}`",
        f"- eval_error_rows: `{eval_error_rows}`",
        f"- launcher_status_conflicts: `{status_conflicts}`",
        "",
        "## Accepted By Semantic Pair",
        "",
        md_table(accepted_pair_summary),
        "",
        "## Accepted By Motif",
        "",
        md_table(accepted_motif_summary),
        "",
        "## Accepted By Horizon",
        "",
        md_table(accepted_horizon_summary),
        "",
        "## Top Accepted With Full Formula",
        "",
        md_table(accepted[top_cols], 20) if top_cols else "`<missing columns>`",
        "",
        "## Rejection Reasons",
        "",
        md_table(reason_summary, 30),
        "",
        "## Shard Decisions",
        "",
        md_table(decision_summary, 20),
        "",
        "## Notes",
        "",
        "- This is a reward-gate aggregate, not alpha proof.",
        "- Full formula is taken from the candidate `expression` column and backfilled from shard queues when needed.",
        "- Launcher status conflicts are diagnostic because shard manifests are the source of truth.",
    ]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
