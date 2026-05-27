from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, stable_hash
from crypto_a7o2c_semantic_uniqueness_audit import write_json, write_markdown_table


DATE_TAG = os.environ.get("A7O_DATE_TAG", "20260521")
WAVE_ID = os.environ.get("A7O_L1_WAVE_ID", "w1")
MAX_PARALLEL = int(os.environ.get("A7O_L1W_MAX_PARALLEL", "4"))
CHECKPOINTS = [
    {"checkpoint_id": "03", "cell_start": 128},
    {"checkpoint_id": "04", "cell_start": 192},
    {"checkpoint_id": "05", "cell_start": 256},
    {"checkpoint_id": "06", "cell_start": 320},
]
CELL_COUNT = 64
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
WAVE_DIR = RUNTIME_DIR / "a7o_l1_waves"
WAVE_RUNTIME_DIR = WAVE_DIR / f"a7o_l1{WAVE_ID}"
LOG_DIR = WAVE_RUNTIME_DIR / "logs"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_checkpoint_jobs() -> list[dict[str, Any]]:
    WAVE_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    queue = list(CHECKPOINTS)
    running: list[dict[str, Any]] = []
    finished: list[dict[str, Any]] = []
    while queue or running:
        while queue and len(running) < MAX_PARALLEL:
            job = queue.pop(0)
            env = os.environ.copy()
            env.update(
                {
                    "A7O_DATE_TAG": DATE_TAG,
                    "A7O_L1_CHECKPOINT_ID": job["checkpoint_id"],
                    "A7O_L1_CELL_START": str(job["cell_start"]),
                    "A7O_L1_CELL_COUNT": str(CELL_COUNT),
                    "A7O_L1_SKIP_CUMULATIVE_UPDATE": "1",
                }
            )
            log_path = LOG_DIR / f"checkpoint_{job['checkpoint_id']}.log"
            log_file = log_path.open("w", encoding="utf-8")
            proc = subprocess.Popen(
                [sys.executable, str(SCRIPT_DIR / "crypto_a7o_l1_pilot_shard.py")],
                cwd=str(REPO_ROOT),
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True,
            )
            running.append({**job, "process": proc, "log_file": log_file, "log_path": log_path, "started_at": utc_now()})
            print(f"started checkpoint_{job['checkpoint_id']} cell_start={job['cell_start']} pid={proc.pid}", flush=True)
        still_running = []
        for job in running:
            rc = job["process"].poll()
            if rc is None:
                still_running.append(job)
                continue
            job["finished_at"] = utc_now()
            job["returncode"] = int(rc)
            job["log_file"].close()
            finished.append({k: v for k, v in job.items() if k not in {"process", "log_file"}})
            print(f"finished checkpoint_{job['checkpoint_id']} returncode={rc}", flush=True)
        running = still_running
        if running and not queue:
            time.sleep(5)
        elif running:
            time.sleep(2)
    return finished


def checkpoint_paths(checkpoint_id: str) -> dict[str, Path]:
    prefix = f"a7o_l1_checkpoint_{checkpoint_id}"
    base = RUNTIME_DIR / prefix
    return {
        "base": base,
        "prefix": Path(prefix),
        "manifest": base / f"{prefix}_manifest.json",
        "decision": base / f"{prefix}_checkpoint_decision.json",
        "deep": base / f"{prefix}_deep_audit_scoreboard.csv",
        "post_may": base / f"{prefix}_post_may_eligible_pool.csv",
        "clusters": base / f"{prefix}_return_corr_clusters.csv",
        "cell_failure": base / f"{prefix}_cell_failure_map.csv",
        "placebo": base / f"{prefix}_placebo_null_comparison.csv",
        "may": base / f"{prefix}_may_stress_only_audit.csv",
    }


def load_checkpoint_records(jobs: list[dict[str, Any]]) -> dict[str, Any]:
    decisions = []
    manifests = []
    deep_frames = []
    post_may_frames = []
    cluster_frames = []
    cell_failure_frames = []
    placebo_frames = []
    may_frames = []
    for job in sorted(jobs, key=lambda x: x["checkpoint_id"]):
        checkpoint_id = job["checkpoint_id"]
        paths = checkpoint_paths(checkpoint_id)
        if job.get("returncode") != 0:
            decisions.append(
                {
                    "checkpoint_id": checkpoint_id,
                    "cell_start": job["cell_start"],
                    "cell_end": job["cell_start"] + CELL_COUNT - 1,
                    "decision": "PROCESS_FAILED",
                    "blockers": "process_returncode",
                    "returncode": job.get("returncode"),
                    "log_path": str(job["log_path"]),
                }
            )
            continue
        decision = json.loads(paths["decision"].read_text(encoding="utf-8"))
        manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
        decisions.append(
            {
                "checkpoint_id": checkpoint_id,
                "cell_start": decision["cell_start"],
                "cell_end": decision["cell_end"],
                "decision": decision["decision"],
                "blockers": ";".join(decision["blockers"]),
                "returncode": job.get("returncode"),
                "log_path": str(job["log_path"]),
                **decision["metrics"],
                "manifest_hash": manifest.get("stable_manifest_hash", ""),
            }
        )
        manifests.append({"checkpoint_id": checkpoint_id, **manifest})
        for key, frames, path_key in [
            ("deep", deep_frames, "deep"),
            ("post_may", post_may_frames, "post_may"),
            ("clusters", cluster_frames, "clusters"),
            ("cell_failure", cell_failure_frames, "cell_failure"),
            ("placebo", placebo_frames, "placebo"),
            ("may", may_frames, "may"),
        ]:
            df = pd.read_csv(paths[path_key])
            df.insert(0, "checkpoint_id", checkpoint_id)
            frames.append(df)
    return {
        "checkpoint_summary": pd.DataFrame(decisions),
        "manifests": manifests,
        "deep": pd.concat(deep_frames, ignore_index=True) if deep_frames else pd.DataFrame(),
        "post_may": pd.concat(post_may_frames, ignore_index=True) if post_may_frames else pd.DataFrame(),
        "clusters": pd.concat(cluster_frames, ignore_index=True) if cluster_frames else pd.DataFrame(),
        "cell_failure": pd.concat(cell_failure_frames, ignore_index=True) if cell_failure_frames else pd.DataFrame(),
        "placebo": pd.concat(placebo_frames, ignore_index=True) if placebo_frames else pd.DataFrame(),
        "may": pd.concat(may_frames, ignore_index=True) if may_frames else pd.DataFrame(),
    }


def concentration_audit(deep: pd.DataFrame, clusters: pd.DataFrame, post_may: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if deep.empty:
        return pd.DataFrame(columns=["metric", "value", "threshold", "pass"])
    liqvol = deep["source_field_families"].astype(str).apply(lambda x: {"liquidity", "volatility"}.issubset(set(x.split(";"))))
    cluster_key = clusters["checkpoint_id"].astype(str) + ":" + clusters["return_corr_cluster"].astype(str) if not clusters.empty else pd.Series(dtype=str)
    motif = deep["feature_family_set"].astype(str) + "|" + deep["operator_motif"].astype(str) + "|" + deep["temporal_horizon_class"].astype(str)
    metrics = {
        "wave_liquidity_volatility_deep_share": (float(liqvol.mean()), 0.15, "<="),
        "wave_single_return_corr_cluster_share": (float(cluster_key.value_counts(normalize=True).iloc[0]) if len(cluster_key) else 0.0, 0.20, "<="),
        "wave_single_horizon_deep_share": (float(deep["temporal_horizon_class"].value_counts(normalize=True).iloc[0]), 0.30, "<="),
        "wave_single_hypothesis_family_share": (float(deep["hypothesis_family"].value_counts(normalize=True).iloc[0]), 0.30, "<="),
        "wave_single_feature_operator_horizon_motif_share": (float(motif.value_counts(normalize=True).iloc[0]), 0.20, "<="),
        "wave_field_families": (int(deep["source_field_families"].nunique()), 6, ">="),
        "wave_hypothesis_families": (int(deep["hypothesis_family"].nunique()), 6, ">="),
        "wave_post_may_eligible_deep_survivors": (int(len(post_may)), 120, ">="),
        "wave_post_may_eligible_rate": (float(len(post_may) / len(deep)) if len(deep) else 0.0, 0.15, ">="),
        "wave_return_corr_clusters_proxy": (int(cluster_key.nunique()) if len(cluster_key) else 0, 12, ">="),
    }
    for metric, (value, threshold, op) in metrics.items():
        passed = value <= threshold if op == "<=" else value >= threshold
        rows.append({"metric": metric, "value": value, "threshold": threshold, "operator": op, "pass": bool(passed)})
    return pd.DataFrame(rows)


def write_wave_outputs(records: dict[str, Any], jobs: list[dict[str, Any]]) -> dict[str, Any]:
    WAVE_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint_summary = records["checkpoint_summary"]
    deep = records["deep"]
    post_may = records["post_may"]
    clusters = records["clusters"]
    cell_failure = records["cell_failure"]
    placebo = records["placebo"]
    may = records["may"]
    audit = concentration_audit(deep, clusters, post_may)
    all_checkpoints_pass = bool((checkpoint_summary["decision"] == "PASS_A7O_L1_PILOT_CHECKPOINT_READY_FOR_NEXT_64_CELLS").all()) if not checkpoint_summary.empty else False
    placebo_research = int(pd.to_numeric(placebo.get("research_candidate_count", pd.Series(dtype=int)), errors="coerce").fillna(0).sum()) if not placebo.empty else 0
    may_violations = int(pd.to_numeric(may.get("count", pd.Series(dtype=int)), errors="coerce").fillna(0).sum()) if not may.empty else 0
    blockers = []
    if not all_checkpoints_pass:
        blockers.append("one_or_more_checkpoints_not_pass")
    if placebo_research != 0:
        blockers.append("placebo_or_null_research_candidates")
    if may_violations != 0:
        blockers.append("may_leakage_violations")
    for _, row in audit.iterrows():
        if not bool(row["pass"]):
            blockers.append(str(row["metric"]))
    decision = "PASS_A7O_L1W1_READY_FOR_W2" if not blockers else "HOLD_A7O_L1W1"
    paths = {
        "manifest": WAVE_RUNTIME_DIR / f"a7o_l1{WAVE_ID}_manifest.json",
        "checkpoint_summary": WAVE_RUNTIME_DIR / f"a7o_l1{WAVE_ID}_checkpoint_summary.csv",
        "cumulative_summary": WAVE_RUNTIME_DIR / f"a7o_l1{WAVE_ID}_cumulative_summary.csv",
        "post_may_pool": WAVE_RUNTIME_DIR / f"a7o_l1{WAVE_ID}_post_may_eligible_pool.csv",
        "return_corr_clusters": WAVE_RUNTIME_DIR / f"a7o_l1{WAVE_ID}_return_corr_clusters.csv",
        "cell_failure_map": WAVE_RUNTIME_DIR / f"a7o_l1{WAVE_ID}_cell_failure_map.csv",
        "concentration_audit": WAVE_RUNTIME_DIR / f"a7o_l1{WAVE_ID}_concentration_audit.csv",
        "placebo_null_comparison": WAVE_RUNTIME_DIR / f"a7o_l1{WAVE_ID}_placebo_null_comparison.csv",
        "may_stress_only_audit": WAVE_RUNTIME_DIR / f"a7o_l1{WAVE_ID}_may_stress_only_audit.csv",
        "decision_record": WAVE_RUNTIME_DIR / f"a7o_l1{WAVE_ID}_decision_record.json",
    }
    checkpoint_summary.to_csv(paths["checkpoint_summary"], index=False)
    post_may.to_csv(paths["post_may_pool"], index=False)
    clusters.to_csv(paths["return_corr_clusters"], index=False)
    cell_failure.to_csv(paths["cell_failure_map"], index=False)
    audit.to_csv(paths["concentration_audit"], index=False)
    placebo.to_csv(paths["placebo_null_comparison"], index=False)
    may.to_csv(paths["may_stress_only_audit"], index=False)

    base_summary = RUNTIME_DIR / "a7o_l1_cumulative_checkpoint_summary.csv"
    existing = pd.read_csv(base_summary, dtype={"checkpoint_id": str}) if base_summary.exists() else pd.DataFrame()
    wave_rows = checkpoint_summary.copy()
    if not wave_rows.empty:
        wave_rows["post_may_eligible_rate"] = wave_rows["post_may_eligible_deep_survivors"] / wave_rows["deep_audit_selected"]
        wave_rows["may_leakage_violations"] = 0
        wave_rows["runtime_dir"] = wave_rows["checkpoint_id"].apply(lambda c: str(RUNTIME_DIR / f"a7o_l1_checkpoint_{str(c).zfill(2)}"))
        wave_rows["report"] = wave_rows["checkpoint_id"].apply(lambda c: str(REPORT_DIR / f"CRYPTO_A7O_L1_CHECKPOINT_{str(c).zfill(2)}_{DATE_TAG}.md"))
        keep_cols = [
            "checkpoint_id",
            "cell_start",
            "cell_end",
            "generated",
            "strict_replay_selected",
            "deep_audit_selected",
            "post_may_eligible_deep_survivors",
            "post_may_eligible_rate",
            "liquidity_volatility_deep_share",
            "single_return_corr_cluster_share",
            "single_horizon_deep_share",
            "active_cells_with_valid_deep_audit",
            "placebo_or_null_research_candidates",
            "may_leakage_violations",
            "decision",
            "blockers",
            "manifest_hash",
            "runtime_dir",
            "report",
        ]
        wave_rows = wave_rows[keep_cols]
    if not existing.empty and "checkpoint_id" in existing.columns:
        existing = existing[~existing["checkpoint_id"].astype(str).str.zfill(2).isin(wave_rows["checkpoint_id"].astype(str).str.zfill(2))]
    cumulative = pd.concat([existing, wave_rows], ignore_index=True)
    cumulative["checkpoint_id"] = cumulative["checkpoint_id"].astype(str).str.zfill(2)
    cumulative["cell_start"] = pd.to_numeric(cumulative["cell_start"], errors="coerce")
    cumulative = cumulative.sort_values(["cell_start", "checkpoint_id"], kind="stable")
    cumulative.to_csv(paths["cumulative_summary"], index=False)
    cumulative.to_csv(base_summary, index=False)

    decision_record = {
        "generated_at": utc_now(),
        "wave_id": WAVE_ID,
        "decision": decision,
        "authorizes_w2": decision == "PASS_A7O_L1W1_READY_FOR_W2",
        "authorizes_full_l1_without_checkpoint": False,
        "authorizes_l2_or_l3": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "shadow_paper_live_status": "NOT_AUTHORIZED",
        "blockers": blockers,
        "max_parallel": MAX_PARALLEL,
        "jobs": [{k: str(v) for k, v in job.items()} for job in jobs],
        "wave_metrics": {row["metric"]: row["value"] for _, row in audit.iterrows()},
        "checkpoint_count": int(len(checkpoint_summary)),
        "wave_generated": int(pd.to_numeric(checkpoint_summary.get("generated", pd.Series(dtype=int)), errors="coerce").fillna(0).sum()) if not checkpoint_summary.empty else 0,
        "wave_strict_replay": int(pd.to_numeric(checkpoint_summary.get("strict_replay_selected", pd.Series(dtype=int)), errors="coerce").fillna(0).sum()) if not checkpoint_summary.empty else 0,
        "wave_deep_audit": int(pd.to_numeric(checkpoint_summary.get("deep_audit_selected", pd.Series(dtype=int)), errors="coerce").fillna(0).sum()) if not checkpoint_summary.empty else 0,
        "outputs": {k: str(v) for k, v in paths.items()},
    }
    decision_record["stable_decision_hash"] = stable_hash({k: v for k, v in decision_record.items() if k != "stable_decision_hash"})
    write_json(paths["decision_record"], decision_record)

    manifest = {
        "generated_at": utc_now(),
        "wave_id": WAVE_ID,
        "decision": decision,
        "executes_search": True,
        "executes_replay": True,
        "parallel_checkpoint_wave": True,
        "checkpoint_ids": [job["checkpoint_id"] for job in CHECKPOINTS],
        "max_parallel": MAX_PARALLEL,
        "authorizes_w2": decision == "PASS_A7O_L1W1_READY_FOR_W2",
        "authorizes_full_l1_without_checkpoint": False,
        "authorizes_l2_execution": False,
        "authorizes_l3_execution": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "shadow_paper_live_status": "NOT_AUTHORIZED",
        "blockers": blockers,
        "outputs": {k: str(v) for k, v in paths.items()},
        "may_policy": {
            "allowed": ["post_selection_stress_label", "post_selection_veto", "failure_attribution"],
            "forbidden": ["score", "ranking", "threshold", "generation", "allocation", "mutation", "surrogate_target"],
        },
    }
    report_path = REPORT_DIR / f"CRYPTO_A7O_L1{WAVE_ID.upper()}_PARALLEL_CHECKPOINT_WAVE_{DATE_TAG}.md"
    manifest["outputs"]["report"] = str(report_path)
    manifest["stable_manifest_hash"] = stable_hash({k: v for k, v in manifest.items() if k not in {"generated_at", "stable_manifest_hash"}})
    write_json(paths["manifest"], manifest)

    report = [
        f"# Crypto A7O-L1{WAVE_ID.upper()} Parallel Checkpoint Wave",
        "",
        f"- generated_at: `{manifest['generated_at']}`",
        f"- decision: `{decision}`",
        f"- checkpoint_ids: `{', '.join(manifest['checkpoint_ids'])}`",
        f"- max_parallel: `{MAX_PARALLEL}`",
        f"- authorizes_w2: `{manifest['authorizes_w2']}`",
        "- authorizes_full_l1_without_checkpoint: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        f"- blockers: `{blockers}`",
        "",
        "## Wave Concentration Audit",
        "",
        write_markdown_table(audit, 40),
        "## Checkpoint Summary",
        "",
        write_markdown_table(checkpoint_summary, 40),
        "## Cumulative Summary",
        "",
        write_markdown_table(cumulative, 40),
        "## Boundary",
        "",
        "This wave can only authorize the next checkpoint wave. It cannot authorize full L1 without checkpoints, L2, L3, alpha proof, shadow, paper, or live.",
    ]
    report_path.write_text("\n".join(report), encoding="utf-8")
    write_json(paths["manifest"], manifest)
    return {"decision_record": decision_record, "manifest": manifest, "paths": paths}


def sync_outputs_to_repo() -> None:
    repo_runtime = REPO_ROOT / "runtime"
    repo_reports = REPO_ROOT / "reports"
    repo_runtime.mkdir(exist_ok=True)
    repo_reports.mkdir(exist_ok=True)
    for job in CHECKPOINTS:
        src = RUNTIME_DIR / f"a7o_l1_checkpoint_{job['checkpoint_id']}"
        dst = repo_runtime / src.name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        report_name = f"CRYPTO_A7O_L1_CHECKPOINT_{job['checkpoint_id']}_{DATE_TAG}.md"
        shutil.copy2(REPORT_DIR / report_name, repo_reports / report_name)
    src_wave = WAVE_DIR
    dst_wave = repo_runtime / "a7o_l1_waves"
    if dst_wave.exists():
        shutil.rmtree(dst_wave)
    shutil.copytree(src_wave, dst_wave)
    shutil.copy2(RUNTIME_DIR / "a7o_l1_cumulative_checkpoint_summary.csv", repo_runtime / "a7o_l1_cumulative_checkpoint_summary.csv")
    wave_report = REPORT_DIR / f"CRYPTO_A7O_L1{WAVE_ID.upper()}_PARALLEL_CHECKPOINT_WAVE_{DATE_TAG}.md"
    shutil.copy2(wave_report, repo_reports / wave_report.name)


def main() -> int:
    started = utc_now()
    jobs = run_checkpoint_jobs()
    records = load_checkpoint_records(jobs)
    output = write_wave_outputs(records, jobs)
    sync_outputs_to_repo()
    print(json.dumps({"started_at": started, "finished_at": utc_now(), **output["decision_record"]}, indent=2, sort_keys=True))
    return 0 if output["decision_record"]["decision"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
