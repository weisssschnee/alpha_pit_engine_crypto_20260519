from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError

LOCAL_REPO = Path(__file__).resolve().parents[1]
if str(LOCAL_REPO) not in sys.path:
    sys.path.insert(0, str(LOCAL_REPO))

from alphafactory_crypto.engines.semantic_domains import (
    canonicalize_semantic_expression,
    is_numeric_constant_expression,
)
from alphafactory_crypto.engines.signal_identity import sketch_correlation


DEFAULT_REPO = Path(r"D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote")
DEFAULT_STRICT_PACK_RUNTIME = DEFAULT_REPO / "runtime" / "a7search7_strict_accepted_pack_20260706"
DEFAULT_VALIDATION_QUEUE = DEFAULT_STRICT_PACK_RUNTIME / "a7search7_validation_ablation_queue.csv"
DEFAULT_SOURCE_RUN_ROOT = Path(r"D:\HermesWorker\runtime\a7source5_a7search7_source_lag_retest_py_20260706")
DEFAULT_SOURCE_AGG_RUNTIME = DEFAULT_REPO / "runtime" / "a7source5_a7search7_source_lag_retest_py_aggregate_20260706"
DEFAULT_SOURCE_AGG_REPORT = DEFAULT_REPO / "reports" / "CRYPTO_A7SOURCE5_PY_A7SEARCH7_SOURCE_LAG_RETEST_AGGREGATE_20260706.md"
DEFAULT_REWARD_RUN_ROOT = Path(r"D:\HermesWorker\runtime\a7search7_strict_validation_reward_source5_py_20260706")
DEFAULT_REWARD_AGG_RUNTIME = DEFAULT_REPO / "runtime" / "a7search7_strict_validation_reward_source5_py_aggregate_20260706"
DEFAULT_REWARD_AGG_REPORT = DEFAULT_REPO / "reports" / "CRYPTO_A7SEARCH7_STRICT_VALIDATION_REWARD_SOURCE5_PY_AGGREGATE_20260706.md"


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


def log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")


def acquire_lock(run_root: Path) -> bool:
    run_root.mkdir(parents=True, exist_ok=True)
    lock = run_root / "a7source5_py_flow.lock"
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(f"{os.getpid()} {datetime.now().isoformat()}\n")
        return True
    except FileExistsError:
        return False


def split_queue(queue_path: Path, shard_dir: Path, rows_per_shard: int) -> pd.DataFrame:
    queue = read_csv(queue_path)
    if queue.empty:
        raise RuntimeError(f"empty validation queue: {queue_path}")
    if "horizon_h" not in queue.columns:
        for alias in ["source_horizon_h", "horizon", "label_horizon_h"]:
            if alias in queue.columns:
                queue["horizon_h"] = queue[alias]
                break
    if "horizon_h" not in queue.columns:
        raise RuntimeError(f"validation queue requires horizon_h or horizon alias; columns={list(queue.columns)}")
    shard_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for idx, start in enumerate(range(0, len(queue), rows_per_shard)):
        shard_id = f"a7source5_s{idx:03d}"
        shard = queue.iloc[start : start + rows_per_shard].copy()
        path = shard_dir / f"{shard_id}.csv"
        shard.to_csv(path, index=False)
        rows.append({"shard_id": shard_id, "queue_path": str(path), "row_count": int(len(shard))})
    return pd.DataFrame(rows)


def apply_semantic_gate(
    input_path: Path,
    valid_output: Path,
    rejection_output: Path,
    rewrite_output: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    queue = read_csv(input_path)
    if queue.empty:
        raise RuntimeError(f"empty validation queue: {input_path}")
    if "expression" not in queue.columns and "formula" in queue.columns:
        queue["expression"] = queue["formula"]
    audits = queue["expression"].fillna("").astype(str).map(canonicalize_semantic_expression)
    queue["original_expression"] = queue["expression"].astype(str)
    queue["semantic_canonical_expression"] = audits.map(lambda item: item[0])
    queue["semantic_degeneracy_reasons"] = audits.map(lambda item: ";".join(item[1]))
    queue["semantic_rewrite_applied"] = queue["original_expression"].ne(queue["semantic_canonical_expression"])
    queue["semantic_constant_collapse"] = queue["semantic_canonical_expression"].map(is_numeric_constant_expression)
    rejected = queue[queue["semantic_constant_collapse"]].copy()
    valid = queue[~queue["semantic_constant_collapse"]].copy()
    valid["expression"] = valid["semantic_canonical_expression"]
    if "formula" in valid.columns:
        valid["formula"] = valid["semantic_canonical_expression"]
    rewrites = valid[valid["semantic_rewrite_applied"]].copy()
    valid_output.parent.mkdir(parents=True, exist_ok=True)
    rejection_output.parent.mkdir(parents=True, exist_ok=True)
    rewrite_output.parent.mkdir(parents=True, exist_ok=True)
    valid.to_csv(valid_output, index=False)
    rejected.to_csv(rejection_output, index=False)
    rewrites.to_csv(rewrite_output, index=False)
    return valid, rejected, rewrites


def deduplicate_reward_survivors(
    survivors: pd.DataFrame,
    source_summary: pd.DataFrame,
    representative_output: Path,
    alias_output: Path,
    similarity_output: Path,
    similarity_threshold: float = 0.995,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if survivors.empty:
        raise RuntimeError("cannot deduplicate an empty survivor queue")
    identity_columns = [
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
    available = [column for column in identity_columns if column in source_summary.columns]
    lookup_columns = ["blueprint_id", "horizon_h", *available]
    lookup = source_summary[lookup_columns].copy()
    lookup["blueprint_id"] = lookup["blueprint_id"].astype(str)
    lookup["_horizon_key"] = pd.to_numeric(lookup["horizon_h"], errors="coerce").astype("Int64").astype(str)
    lookup = lookup.drop(columns=["horizon_h"]).drop_duplicates(["blueprint_id", "_horizon_key"], keep="first")

    aliases = survivors.copy()
    aliases["blueprint_id"] = aliases["blueprint_id"].astype(str)
    aliases["_horizon_key"] = pd.to_numeric(aliases["horizon_h"], errors="coerce").astype("Int64").astype(str)
    aliases = aliases.merge(lookup, on=["blueprint_id", "_horizon_key"], how="left", suffixes=("", "_source"))
    aliases = aliases.drop(columns=["_horizon_key"])
    fingerprint = aliases.get("signal_weight_exact_fingerprint", pd.Series(index=aliases.index, dtype=str)).fillna("").astype(str)
    aliases["_identity_group"] = [value if value else f"missing:{idx}:{bid}" for idx, (value, bid) in enumerate(zip(fingerprint, aliases["blueprint_id"]))]
    aliases["_expression_length"] = aliases["expression"].fillna("").astype(str).str.len()
    aliases = aliases.sort_values(["_identity_group", "_expression_length", "blueprint_id"], kind="stable")
    aliases["representative_blueprint_id"] = aliases.groupby("_identity_group", sort=False)["blueprint_id"].transform("first")
    representative_expression = aliases.groupby("_identity_group", sort=False)["expression"].transform("first")
    aliases["representative_expression"] = representative_expression
    aliases["is_signal_identity_representative"] = aliases["blueprint_id"].astype(str).eq(aliases["representative_blueprint_id"].astype(str))
    representatives = aliases[aliases["is_signal_identity_representative"]].copy()
    representatives = representatives.drop(columns=["_identity_group", "_expression_length"])
    aliases = aliases.drop(columns=["_identity_group", "_expression_length"])

    review_rows: list[dict[str, Any]] = []
    records = aliases.to_dict("records")
    for left_index, left in enumerate(records):
        for right in records[left_index + 1 :]:
            if str(left.get("signal_weight_exact_fingerprint", "")) == str(right.get("signal_weight_exact_fingerprint", "")):
                continue
            same_quantized = (
                bool(left.get("signal_weight_quantized_fingerprint"))
                and str(left.get("signal_weight_quantized_fingerprint")) == str(right.get("signal_weight_quantized_fingerprint"))
            )
            correlation = sketch_correlation(
                str(left.get("signal_weight_similarity_sketch", "")),
                str(right.get("signal_weight_similarity_sketch", "")),
            )
            if same_quantized or (math.isfinite(correlation) and abs(correlation) >= similarity_threshold):
                review_rows.append(
                    {
                        "left_blueprint_id": left.get("blueprint_id", ""),
                        "right_blueprint_id": right.get("blueprint_id", ""),
                        "left_expression": left.get("expression", ""),
                        "right_expression": right.get("expression", ""),
                        "same_quantized_fingerprint": same_quantized,
                        "similarity_sketch_correlation": correlation,
                        "decision": "REVIEW_HIGH_SIGNAL_SIMILARITY_NOT_HARD_REJECT",
                    }
                )
    similarity = pd.DataFrame(review_rows)
    representative_output.parent.mkdir(parents=True, exist_ok=True)
    representatives.to_csv(representative_output, index=False)
    aliases.to_csv(alias_output, index=False)
    similarity.to_csv(similarity_output, index=False)
    return representatives, aliases, similarity


def run_parallel(
    plan: pd.DataFrame,
    max_parallel: int,
    make_command,
    manifest_for,
    log_path: Path,
    kind: str,
    cwd: Path,
) -> pd.DataFrame:
    running: list[dict[str, Any]] = []
    status_rows: list[dict[str, Any]] = []
    remaining = plan.to_dict("records")
    while remaining or running:
        while remaining and len(running) < max_parallel:
            row = remaining.pop(0)
            shard_id = str(row["shard_id"])
            manifest = Path(manifest_for(shard_id))
            if manifest.exists():
                status_rows.append({"shard_id": shard_id, "status": "skip_existing", "exit_code": 0, "queue_path": row.get("queue_path", "")})
                continue
            cmd, out_path, err_path = make_command(row)
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            out = open(out_path, "w", encoding="utf-8")
            err = open(err_path, "w", encoding="utf-8")
            proc = subprocess.Popen(cmd, cwd=str(cwd), stdout=out, stderr=err)
            running.append({"row": row, "proc": proc, "out": out, "err": err, "started_at": now_utc()})
            log(log_path, f"START {kind} {shard_id} pid={proc.pid}")
        time.sleep(15)
        still: list[dict[str, Any]] = []
        for entry in running:
            proc: subprocess.Popen = entry["proc"]
            code = proc.poll()
            shard_id = str(entry["row"]["shard_id"])
            manifest = Path(manifest_for(shard_id))
            if code is None:
                still.append(entry)
                continue
            entry["out"].close()
            entry["err"].close()
            status = "done" if manifest.exists() and code == 0 else "failed"
            status_rows.append(
                {
                    "shard_id": shard_id,
                    "status": status,
                    "exit_code": int(code),
                    "started_at": entry["started_at"],
                    "ended_at": now_utc(),
                    "queue_path": entry["row"].get("queue_path", ""),
                    "manifest": str(manifest),
                }
            )
            log(log_path, f"{status.upper()} {kind} {shard_id} exit={code} manifest={manifest.exists()}")
        running = still
        status_frame = pd.DataFrame(status_rows)
        if not status_frame.empty:
            status_frame.to_csv(log_path.with_name(f"{kind}_status.csv"), index=False)
    return pd.DataFrame(status_rows)


def build_reward_survivor_queue(
    validation_queue_path: Path,
    source_summary: pd.DataFrame,
    output_path: Path,
) -> pd.DataFrame:
    queue = read_csv(validation_queue_path)
    if queue.empty:
        raise RuntimeError(f"empty validation queue: {validation_queue_path}")
    if source_summary.empty:
        survivors = queue.iloc[0:0].copy()
    else:
        required = {"blueprint_id", "horizon_h", "source_lag_gate"}
        missing = required - set(source_summary.columns)
        if missing:
            raise RuntimeError(f"source-lag summary missing columns: {sorted(missing)}")
        pass_rows = source_summary[
            source_summary["source_lag_gate"].astype(str).eq("PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC")
        ].copy()
        pass_keys = set(
            zip(
                pass_rows["blueprint_id"].astype(str),
                pd.to_numeric(pass_rows["horizon_h"], errors="coerce").astype("Int64").astype(str),
            )
        )
        queue_horizons = pd.to_numeric(queue["horizon_h"], errors="coerce").astype("Int64").astype(str)
        keep = [
            (str(blueprint_id), str(horizon)) in pass_keys
            for blueprint_id, horizon in zip(queue["blueprint_id"], queue_horizons)
        ]
        survivors = queue.loc[keep].copy()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    survivors.to_csv(output_path, index=False)
    return survivors


def concat_csv(pattern: str, output: Path) -> pd.DataFrame:
    frames = []
    for path in sorted(Path().glob(pattern)):
        frame = read_csv(path)
        if frame.empty:
            continue
        frame.insert(0, "source_file", str(path))
        frames.append(frame)
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output, index=False)
    return out


def concat_csv_files(paths: list[Path], output: Path) -> pd.DataFrame:
    frames = []
    for path in sorted(paths):
        frame = read_csv(path)
        if frame.empty:
            continue
        frame.insert(0, "source_file", str(path))
        frames.append(frame)
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output, index=False)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--validation-queue", type=Path, default=DEFAULT_VALIDATION_QUEUE)
    parser.add_argument("--source-run-root", type=Path, default=DEFAULT_SOURCE_RUN_ROOT)
    parser.add_argument("--source-aggregate-runtime", type=Path, default=DEFAULT_SOURCE_AGG_RUNTIME)
    parser.add_argument("--source-aggregate-report", type=Path, default=DEFAULT_SOURCE_AGG_REPORT)
    parser.add_argument("--reward-run-root", type=Path, default=DEFAULT_REWARD_RUN_ROOT)
    parser.add_argument("--reward-aggregate-runtime", type=Path, default=DEFAULT_REWARD_AGG_RUNTIME)
    parser.add_argument("--reward-aggregate-report", type=Path, default=DEFAULT_REWARD_AGG_REPORT)
    parser.add_argument("--reward-numeric-cache", type=Path)
    parser.add_argument("--rows-per-shard", type=int, default=16)
    parser.add_argument("--max-parallel", type=int, default=8)
    args = parser.parse_args()
    flow_started = time.perf_counter()

    globals()["DEFAULT_REPO"] = args.repo
    log_path = args.source_run_root / "a7source5_py_flow.log"
    if not acquire_lock(args.source_run_root):
        log(args.source_run_root / "a7source5_py_duplicate_launch.log", "lock exists; duplicate launch exits")
        return

    log(log_path, "A7SOURCE5 Python source-lag -> strict reward flow start")
    log(log_path, f"validation_queue={args.validation_queue}")
    log(log_path, f"max_parallel={args.max_parallel} rows_per_shard={args.rows_per_shard}")

    semantic_valid_queue_path = args.source_run_root / "a7source5_semantic_valid_queue.csv"
    semantic_rejection_path = args.source_aggregate_runtime / "a7source5_semantic_gate_rejections.csv"
    semantic_rewrite_path = args.source_aggregate_runtime / "a7source5_semantic_canonical_rewrites.csv"
    semantic_valid, semantic_rejections, semantic_rewrites = apply_semantic_gate(
        args.validation_queue,
        semantic_valid_queue_path,
        semantic_rejection_path,
        semantic_rewrite_path,
    )
    original_validation_queue_rows = int(len(read_csv(args.validation_queue)))
    log(
        log_path,
        f"semantic_gate input={original_validation_queue_rows} valid={len(semantic_valid)} "
        f"rewritten={len(semantic_rewrites)} constant_rejected={len(semantic_rejections)}",
    )
    if semantic_valid.empty:
        raise RuntimeError("semantic gate rejected the entire validation queue")

    try:
        log(log_path, "split_queue_begin")
        source_plan = split_queue(semantic_valid_queue_path, args.source_run_root / "source_queue_shards", args.rows_per_shard)
        log(log_path, f"split_queue_done rows={len(source_plan)}")
    except Exception as exc:
        log(log_path, f"FATAL split_queue {type(exc).__name__}: {exc!r}")
        raise
    source_plan.to_csv(args.source_run_root / "a7source5_source_lag_shard_plan.csv", index=False)
    log(log_path, f"source_shard_count={len(source_plan)}")

    def source_manifest(shard_id: str) -> Path:
        return args.source_run_root / "shards" / shard_id / "runtime" / "a7source4_manifest.json"

    def source_command(row: dict[str, Any]):
        shard_id = str(row["shard_id"])
        shard_root = args.source_run_root / "shards" / shard_id
        runtime = shard_root / "runtime"
        report = shard_root / f"CRYPTO_{shard_id}_SOURCE_LAG_RETEST.md"
        cmd = [
            args.python,
            "scripts/crypto_a7source4_batch_source_lag_retest.py",
            "--input",
            str(row["queue_path"]),
            "--runtime",
            str(runtime),
            "--report",
            str(report),
            "--max-rows",
            "100000",
            "--cost-bps",
            "5",
        ]
        return cmd, shard_root / "source_lag.out.log", shard_root / "source_lag.err.log"

    source_stage_started = time.perf_counter()
    source_status = run_parallel(
        source_plan,
        args.max_parallel,
        source_command,
        source_manifest,
        log_path,
        "source_lag",
        args.repo,
    )
    source_stage_seconds = time.perf_counter() - source_stage_started
    failed_source = source_status[source_status["status"].eq("failed")] if not source_status.empty else pd.DataFrame()
    if not failed_source.empty:
        raise RuntimeError(f"source-lag shard failures: {failed_source[['shard_id', 'exit_code']].to_dict('records')}")

    summary_paths = list(args.source_run_root.glob("shards/a7source5_s*/runtime/a7source4_source_lag_summary.csv"))
    metric_paths = list(args.source_run_root.glob("shards/a7source5_s*/runtime/a7source4_source_lag_metrics.csv"))
    error_paths = list(args.source_run_root.glob("shards/a7source5_s*/runtime/a7source4_eval_errors.csv"))
    log(log_path, f"source_aggregate_begin summary_paths={len(summary_paths)} metric_paths={len(metric_paths)} error_paths={len(error_paths)}")
    source_summary = concat_csv_files(summary_paths, args.source_aggregate_runtime / "a7source5_source_lag_summary.csv")
    log(log_path, f"source_summary_concat_done rows={len(source_summary)}")
    concat_csv_files(metric_paths, args.source_aggregate_runtime / "a7source5_source_lag_metrics.csv")
    log(log_path, "source_metrics_concat_done")
    source_errors = concat_csv_files(error_paths, args.source_aggregate_runtime / "a7source5_source_lag_eval_errors.csv")
    log(log_path, f"source_errors_concat_done rows={len(source_errors)}")
    source_pass_count = int(source_summary.get("source_lag_gate", pd.Series(dtype=str)).astype(str).eq("PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC").sum())
    log(log_path, f"source_pass_count={source_pass_count}")
    reward_survivor_queue_path = args.source_aggregate_runtime / "a7source5_source_lag_survivor_reward_queue.csv"
    reward_survivors = build_reward_survivor_queue(
        semantic_valid_queue_path,
        source_summary,
        reward_survivor_queue_path,
    )
    validation_queue_rows = original_validation_queue_rows
    reward_input_rows = int(len(reward_survivors))
    source_lag_rejected_before_reward_rows = int(len(semantic_valid)) - reward_input_rows
    total_rejected_before_reward_rows = validation_queue_rows - reward_input_rows
    reward_representative_queue_path = args.source_aggregate_runtime / "a7source5_signal_identity_representative_reward_queue.csv"
    reward_alias_map_path = args.source_aggregate_runtime / "a7source5_signal_identity_alias_map.csv"
    similarity_review_path = args.source_aggregate_runtime / "a7source5_signal_similarity_review.csv"
    reward_representatives, reward_aliases, similarity_review = deduplicate_reward_survivors(
        reward_survivors,
        source_summary,
        reward_representative_queue_path,
        reward_alias_map_path,
        similarity_review_path,
    )
    reward_representative_rows = int(len(reward_representatives))
    exact_signal_alias_rows_saved = reward_input_rows - reward_representative_rows
    reward_rows_per_shard = min(
        int(args.rows_per_shard),
        max(1, math.ceil(reward_representative_rows / max(1, int(args.max_parallel)))),
    )
    reward_numeric_cache = args.reward_numeric_cache or (args.reward_run_root / "shared_numeric_cache")
    log(
        log_path,
        "reward_survivor_queue_built "
        f"input_rows={validation_queue_rows} survivor_rows={reward_input_rows} "
        f"representative_rows={reward_representative_rows} exact_aliases_saved={exact_signal_alias_rows_saved} "
        f"prefiltered_rows={total_rejected_before_reward_rows}",
    )
    if reward_survivors.empty:
        raise RuntimeError("no source-lag survivors available for strict reward")
    source_manifest_payload = {
        "stage": "A7SOURCE5-PY-A7SEARCH7-SOURCE-LAG-AGGREGATE",
        "generated_at": now_utc(),
        "decision": "PASS_A7SOURCE5_SOURCE_LAG_SURVIVORS_FOUND" if source_pass_count > 0 else "HOLD_A7SOURCE5_SOURCE_LAG_NO_SURVIVORS",
        "source_shards_expected": int(len(source_plan)),
        "source_manifest_count": int(len(summary_paths)),
        "source_lag_summary_rows": int(len(source_summary)),
        "source_lag_pass_count": source_pass_count,
        "source_eval_error_rows": int(len(source_errors)),
        "source_lag_summary": str(args.source_aggregate_runtime / "a7source5_source_lag_summary.csv"),
        "validation_queue_rows": validation_queue_rows,
        "semantic_valid_rows": int(len(semantic_valid)),
        "semantic_reject_rows": int(len(semantic_rejections)),
        "semantic_rewrite_rows": int(len(semantic_rewrites)),
        "semantic_rewrite_audit": str(semantic_rewrite_path),
        "reward_input_rows": reward_input_rows,
        "reward_representative_rows": reward_representative_rows,
        "exact_signal_alias_rows_saved": exact_signal_alias_rows_saved,
        "signal_similarity_review_rows": int(len(similarity_review)),
        "safediv_review_rows": int(source_summary["safediv_review_flag"].fillna(False).astype(bool).sum()) if "safediv_review_flag" in source_summary else 0,
        "reward_rows_per_shard": reward_rows_per_shard,
        "reward_numeric_cache": str(reward_numeric_cache),
        "source_lag_rejected_before_reward_rows": source_lag_rejected_before_reward_rows,
        "total_rejected_before_reward_rows": total_rejected_before_reward_rows,
        "reward_survivor_queue": str(reward_survivor_queue_path),
        "reward_representative_queue": str(reward_representative_queue_path),
        "signal_identity_alias_map": str(reward_alias_map_path),
        "signal_similarity_review": str(similarity_review_path),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(args.source_aggregate_runtime / "a7source5_manifest.json", source_manifest_payload)
    args.source_aggregate_report.parent.mkdir(parents=True, exist_ok=True)
    args.source_aggregate_report.write_text(
        "\n".join(
            [
                "# CRYPTO A7SOURCE5 Python A7SEARCH7 Source-Lag Retest Aggregate",
                "",
                "## Decision",
                "",
                "PASS_A7SOURCE5_SOURCE_LAG_SURVIVORS_FOUND" if source_pass_count > 0 else "HOLD_A7SOURCE5_SOURCE_LAG_NO_SURVIVORS",
                "",
                "## Counts",
                "",
                f"- source_shards_expected: {len(source_plan)}",
                f"- source_manifest_count: {len(summary_paths)}",
                f"- source_lag_summary_rows: {len(source_summary)}",
                f"- source_lag_pass_count: {source_pass_count}",
                f"- source_eval_error_rows: {len(source_errors)}",
                f"- reward_input_rows: {reward_input_rows}",
                f"- reward_representative_rows: {reward_representative_rows}",
                f"- exact_signal_alias_rows_saved: {exact_signal_alias_rows_saved}",
                f"- semantic_reject_rows: {len(semantic_rejections)}",
                f"- semantic_rewrite_rows: {len(semantic_rewrites)}",
                f"- signal_similarity_review_rows: {len(similarity_review)}",
                f"- reward_rows_per_shard: {reward_rows_per_shard}",
                f"- source_lag_rejected_before_reward_rows: {source_lag_rejected_before_reward_rows}",
                "",
                "This is a source-lag diagnostic and strict reward input, not alpha proof.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    log(log_path, f"source aggregate pass_count={source_pass_count} rows={len(source_summary)} errors={len(source_errors)}")

    numeric_cache_manifest = reward_numeric_cache / "a7reward1_numeric_cache_manifest.json"
    numeric_cache_started = time.perf_counter()
    numeric_cache_reused = numeric_cache_manifest.exists()
    if not numeric_cache_manifest.exists():
        log(log_path, "reward_numeric_cache_build_begin")
        subprocess.run(
            [
                args.python,
                "scripts/crypto_a7reward1_portfolio_reward_model.py",
                "--queue",
                str(reward_representative_queue_path),
                "--candidate-cap",
                "0",
                "--hours-per-split",
                "720",
                "--train-hours-per-split",
                "0",
                "--numeric-cache",
                str(reward_numeric_cache),
                "--build-numeric-cache-only",
                "--runtime",
                str(args.reward_run_root / "shared_numeric_cache_build_runtime"),
                "--report",
                str(args.reward_run_root / "shared_numeric_cache_build_runtime" / "report.md"),
            ],
            cwd=str(args.repo),
            check=True,
        )
        log(log_path, "reward_numeric_cache_build_done")
    else:
        log(log_path, "reward_numeric_cache_reuse_existing")
    numeric_cache_seconds = time.perf_counter() - numeric_cache_started

    env = os.environ.copy()
    env["A7V3S0_REWARD_PREQUEUE"] = str(reward_representative_queue_path)
    env["A7V3S0_REWARD_SHARD_RUNTIME"] = str(args.reward_run_root)
    env["A7V3S0_REWARD_ROWS_PER_SHARD"] = str(reward_rows_per_shard)
    log(log_path, "reward_shard_queue_begin")
    subprocess.run([args.python, "scripts/crypto_a7v3s0_reward_shard_queue.py"], cwd=str(args.repo), env=env, check=True)
    log(log_path, "reward_shard_queue_done")
    reward_plan = read_csv(args.reward_run_root / "a7v3s0_reward_shard_plan.csv")
    log(log_path, f"reward_shard_count={len(reward_plan)}")

    def reward_manifest(shard_id: str) -> Path:
        return args.reward_run_root / "shards" / shard_id / "reward_runtime" / "a7reward1_manifest.json"

    def reward_command(row: dict[str, Any]):
        shard_id = str(row["shard_id"])
        shard_root = args.reward_run_root / "shards" / shard_id
        runtime = shard_root / "reward_runtime"
        report = shard_root / f"CRYPTO_{shard_id}_A7SEARCH7_STRICT_VALIDATION_REWARD_SOURCE5_PY.md"
        cmd = [
            args.python,
            "scripts/crypto_a7reward1_portfolio_reward_model.py",
            "--queue",
            str(row["queue_path"]),
            "--candidate-cap",
            "0",
            "--hours-per-split",
            "720",
            "--cost-bps",
            "5",
            "--checkpoint-every",
            "4",
            "--source-lag-summary",
            str(args.source_aggregate_runtime / "a7source5_source_lag_summary.csv"),
            "--numeric-cache",
            str(reward_numeric_cache),
            "--runtime",
            str(runtime),
            "--report",
            str(report),
        ]
        return cmd, shard_root / "reward.out.log", shard_root / "reward.err.log"

    reward_stage_started = time.perf_counter()
    reward_status = run_parallel(
        reward_plan,
        args.max_parallel,
        reward_command,
        reward_manifest,
        log_path,
        "reward_source5",
        args.repo,
    )
    reward_stage_seconds = time.perf_counter() - reward_stage_started
    failed_reward = reward_status[reward_status["status"].eq("failed")] if not reward_status.empty else pd.DataFrame()
    if not failed_reward.empty:
        raise RuntimeError(f"reward shard failures: {failed_reward[['shard_id', 'exit_code']].to_dict('records')}")

    subprocess.run(
        [
            args.python,
            "scripts/crypto_a7v3s0_reward_sharded_aggregate.py",
            "--run-root",
            str(args.reward_run_root),
            "--runtime",
            str(args.reward_aggregate_runtime),
            "--report",
            str(args.reward_aggregate_report),
            "--alias-map",
            str(reward_alias_map_path),
            "--source-policy",
            str(args.repo / "runtime" / "a7source3_publication_semantics_research_20260703" / "a7source3_field_policy_recommendation.json"),
            "--source-lag-summary",
            str(args.source_aggregate_runtime / "a7source5_source_lag_summary.csv"),
        ],
        cwd=str(args.repo),
        check=True,
    )
    write_json(
        args.reward_aggregate_runtime / "a7source5_reward_flow_manifest.json",
        {
            "stage": "A7SOURCE5-SOURCE-LAG-REWARD-FLOW",
            "generated_at": now_utc(),
            "decision": "PASS_A7SOURCE5_REWARD_FLOW_COMPLETED",
            "validation_queue_rows": validation_queue_rows,
            "reward_input_rows": reward_input_rows,
            "reward_representative_rows": reward_representative_rows,
            "exact_signal_alias_rows_saved": exact_signal_alias_rows_saved,
            "semantic_reject_rows": int(len(semantic_rejections)),
            "semantic_rewrite_rows": int(len(semantic_rewrites)),
            "signal_similarity_review_rows": int(len(similarity_review)),
            "source_lag_rejected_before_reward_rows": source_lag_rejected_before_reward_rows,
            "total_rejected_before_reward_rows": total_rejected_before_reward_rows,
            "source_stage_seconds": round(source_stage_seconds, 3),
            "numeric_cache_seconds": round(numeric_cache_seconds, 3),
            "numeric_cache_reused": numeric_cache_reused,
            "reward_stage_seconds": round(reward_stage_seconds, 3),
            "total_flow_seconds": round(time.perf_counter() - flow_started, 3),
            "max_parallel": int(args.max_parallel),
            "reward_rows_per_shard": int(reward_rows_per_shard),
            "numeric_cache": str(reward_numeric_cache),
            "reward_identity_representative_feedback": str(args.reward_aggregate_runtime / "a7v3s0_reward_identity_representative_feedback.csv"),
            "authorizes_alpha_proof": False,
            "authorizes_shadow_paper_live": False,
        },
    )
    log(log_path, "A7SOURCE5 Python source-lag -> strict reward flow finished")


if __name__ == "__main__":
    main()
