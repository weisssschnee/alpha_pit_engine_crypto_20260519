from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CORE58 = REPO / "runtime" / "a7ffcore58_failure_aware_queue_rebuild"
NUMERIC_PROBE = REPO / "scripts" / "crypto_a7ff8_expanded_numeric_probe.py"
RUNTIME = REPO / "runtime" / "a7ffcore59_numeric_repair_execution"
EXTERNAL = Path(
    os.environ.get(
        "A7FFCORE59_EXTERNAL",
        "G:/AlphaFactory_CryptoData/research_runtime/a7ffcore59_numeric_repair_execution_20260604",
    )
)
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE59_NUMERIC_REPAIR_EXECUTION_20260604.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```csv\n" + view.to_csv(index=False) + "```"


def shard_queue(queue: pd.DataFrame, rows_per_shard: int) -> list[tuple[int, pd.DataFrame]]:
    return [(i, queue.iloc[start : start + rows_per_shard].copy()) for i, start in enumerate(range(0, len(queue), rows_per_shard))]


def parse_shard_filter() -> set[int] | None:
    raw = os.environ.get("A7FFCORE59_SHARDS", "").strip()
    if not raw:
        return None
    out: set[int] = set()
    for token in raw.replace(";", ",").split(","):
        token = token.strip().lower().removeprefix("s").removeprefix("shard_")
        if token:
            out.add(int(token))
    return out


def checkpoint_rows(shard_results: list[dict[str, Any]], shards: list[tuple[int, pd.DataFrame]]) -> pd.DataFrame:
    done = {str(row.get("shard")): row for row in shard_results}
    rows = []
    for shard_index, shard in shards:
        shard_name = f"s{shard_index:02d}"
        external_dir = EXTERNAL / f"shard_{shard_index:02d}"
        manifest = external_dir / f"a7ffcore59_s{shard_index:02d}_manifest.json"
        queue_path = external_dir / f"a7ffcore59_s{shard_index:02d}_queue.csv"
        if shard_name in done:
            base = dict(done[shard_name])
            base["checkpoint_status"] = "complete" if int(base.get("returncode", -1)) == 0 and manifest.exists() else "failed_or_partial"
        else:
            manifest_payload = read_json(manifest)
            base = {
                "shard": shard_name,
                "returncode": 0 if manifest_payload else "",
                "timed_out": False if manifest_payload else "",
                "reused_existing": bool(manifest_payload),
                "runtime_dir": str(external_dir).replace("\\", "/"),
                "queue_rows": int(len(shard)),
                "decision": manifest_payload.get("decision", ""),
                "blockers": ";".join(manifest_payload.get("blockers", [])) if manifest_payload else "",
                "materialized_activity_ok_count": manifest_payload.get("materialized_activity_ok_count", ""),
                "label_response_rows": manifest_payload.get("label_response_rows", ""),
                "non_l7_numeric_clue_rows": manifest_payload.get("non_l7_numeric_clue_rows", ""),
                "rank_label_diagnostic_clue_rows": manifest_payload.get("rank_label_diagnostic_clue_rows", ""),
                "selected_portfolio_queue_count": manifest_payload.get("selected_portfolio_queue_count", ""),
                "checkpoint_status": "complete_existing" if manifest.exists() else ("queued_partial" if queue_path.exists() else "not_started"),
            }
        base["manifest_exists"] = manifest.exists()
        base["queue_exists"] = queue_path.exists()
        rows.append(base)
    return pd.DataFrame(rows)


def write_checkpoint(shard_results: list[dict[str, Any]], shards: list[tuple[int, pd.DataFrame]]) -> None:
    frame = checkpoint_rows(shard_results, shards)
    frame.to_csv(RUNTIME / "a7ffcore59_checkpoint_status.csv", index=False)
    frame.to_csv(EXTERNAL / "a7ffcore59_checkpoint_status.csv", index=False)
    write_json(
        RUNTIME / "a7ffcore59_checkpoint_manifest.json",
        {
            "stage": "A7FF-CORE59",
            "generated_at": now_utc(),
            "external_runtime_dir": str(EXTERNAL).replace("\\", "/"),
            "total_shards": int(len(shards)),
            "complete_or_existing_shards": int(frame["checkpoint_status"].astype(str).str.contains("complete").sum()),
            "failed_or_partial_shards": int(frame["checkpoint_status"].astype(str).str.contains("failed|partial").sum()),
            "not_started_shards": int(frame["checkpoint_status"].eq("not_started").sum()),
        },
    )


def run_shard(shard_index: int, shard: pd.DataFrame, source_decision: str, timeout_seconds: int) -> dict[str, Any]:
    shard_dir = EXTERNAL / f"shard_{shard_index:02d}"
    shard_dir.mkdir(parents=True, exist_ok=True)
    file_prefix = f"a7ffcore59_s{shard_index:02d}"
    shard_queue_path = shard_dir / f"{file_prefix}_queue.csv"
    shard = shard.copy()
    shard["a7input_queue"] = shard.get("core58_queue", "numeric_replay_repair")
    shard.to_csv(shard_queue_path, index=False)
    existing_manifest = shard_dir / f"{file_prefix}_manifest.json"
    if existing_manifest.exists() and os.environ.get("A7FFCORE59_FORCE_RERUN", "0").lower() not in {"1", "true", "yes"}:
        manifest = read_json(existing_manifest)
        return {
            "shard": f"s{shard_index:02d}",
            "returncode": 0 if manifest else -1,
            "timed_out": False,
            "reused_existing": True,
            "runtime_dir": str(shard_dir).replace("\\", "/"),
            "queue_rows": int(len(shard)),
            "decision": manifest.get("decision", "NO_MANIFEST"),
            "blockers": ";".join(manifest.get("blockers", [])) if manifest else "no_manifest",
            "materialized_activity_ok_count": int(manifest.get("materialized_activity_ok_count", 0) or 0),
            "label_response_rows": int(manifest.get("label_response_rows", 0) or 0),
            "non_l7_numeric_clue_rows": int(manifest.get("non_l7_numeric_clue_rows", 0) or 0),
            "rank_label_diagnostic_clue_rows": int(manifest.get("rank_label_diagnostic_clue_rows", 0) or 0),
            "selected_portfolio_queue_count": int(manifest.get("selected_portfolio_queue_count", 0) or 0),
        }
    env = os.environ.copy()
    env.update(
        {
            "A7FF8_STAGE": f"A7FF-CORE59-S{shard_index:02d}",
            "A7FF8_FILE_PREFIX": file_prefix,
            "A7FF8_RUNTIME": str(shard_dir),
            "A7FF8_REPORT": str(shard_dir / f"CRYPTO_A7FFCORE59_S{shard_index:02d}_NUMERIC_REPAIR_DETAIL_20260604.md"),
            "A7FF8_QUEUE_PATH": str(shard_queue_path),
            "A7FF8_AUTH_MANIFEST": str(CORE58 / "a7ffcore58_manifest.json"),
            "A7FF8_AUTH_DECISION": source_decision,
            "A7FF8_MATERIALIZE_CAP": str(len(shard)),
            "A7FF8_FAST_NUMERIC_CAP": str(len(shard)),
            "A7FF8_PORTFOLIO_CAP": "128",
            "A7FF8_QUEUE_OFFSET": "0",
            "A7FF8_QUEUE_LIMIT": str(len(shard)),
            "A7FF8_WRITE_CONTROL_DETAIL": "1",
        }
    )
    try:
        proc = subprocess.run(
            [sys.executable, str(NUMERIC_PROBE)],
            cwd=REPO,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_seconds,
        )
        stdout = proc.stdout
        returncode = proc.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace")
        stdout += f"\nTIMEOUT after {timeout_seconds} seconds\n"
        returncode = -9
        timed_out = True
    (shard_dir / f"{file_prefix}_numeric_probe_stdout.log").write_text(stdout, encoding="utf-8")
    manifest = read_json(shard_dir / f"{file_prefix}_manifest.json")
    return {
        "shard": f"s{shard_index:02d}",
        "returncode": returncode,
        "timed_out": timed_out,
        "reused_existing": False,
        "runtime_dir": str(shard_dir).replace("\\", "/"),
        "queue_rows": int(len(shard)),
        "decision": manifest.get("decision", "NO_MANIFEST"),
        "blockers": ";".join(manifest.get("blockers", [])) if manifest else "no_manifest",
        "materialized_activity_ok_count": int(manifest.get("materialized_activity_ok_count", 0) or 0),
        "label_response_rows": int(manifest.get("label_response_rows", 0) or 0),
        "non_l7_numeric_clue_rows": int(manifest.get("non_l7_numeric_clue_rows", 0) or 0),
        "rank_label_diagnostic_clue_rows": int(manifest.get("rank_label_diagnostic_clue_rows", 0) or 0),
        "selected_portfolio_queue_count": int(manifest.get("selected_portfolio_queue_count", 0) or 0),
    }


def collect_shard_csv(name: str, shard_count: int) -> pd.DataFrame:
    frames = []
    for shard_index in range(shard_count):
        path = EXTERNAL / f"shard_{shard_index:02d}" / f"a7ffcore59_s{shard_index:02d}_{name}"
        frame = read_csv(path)
        if not frame.empty:
            frame["core59_shard"] = f"s{shard_index:02d}"
            frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def compact_summary(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    return df.groupby(cols, dropna=False).size().reset_index(name="row_count").sort_values("row_count", ascending=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    EXTERNAL.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE58 / "a7ffcore58_manifest.json")
    if not source.get("authorizes_core59_numeric_repair_execution"):
        raise SystemExit(f"CORE58 does not authorize CORE59: {source.get('decision')}")
    queue = read_csv(CORE58 / "a7ffcore58_numeric_replay_repair_queue.csv")
    if queue.empty:
        raise SystemExit("CORE59 numeric queue is empty")
    queue.to_csv(RUNTIME / "a7ffcore59_numeric_repair_queue.csv", index=False)
    queue.to_csv(EXTERNAL / "a7ffcore59_numeric_repair_queue.csv", index=False)

    rows_per_shard = int(os.environ.get("A7FFCORE59_ROWS_PER_SHARD", "200"))
    timeout_seconds = int(os.environ.get("A7FFCORE59_TIMEOUT_SECONDS", "21600"))
    shards = shard_queue(queue, rows_per_shard)
    if os.environ.get("A7FFCORE59_CHECKPOINT_ONLY", "0").lower() in {"1", "true", "yes"}:
        write_checkpoint([], shards)
        print(json.dumps(read_json(RUNTIME / "a7ffcore59_checkpoint_manifest.json"), indent=2, sort_keys=True))
        return
    shard_filter = parse_shard_filter()
    shard_rows = []
    for shard_index, shard in shards:
        existing_manifest = EXTERNAL / f"shard_{shard_index:02d}" / f"a7ffcore59_s{shard_index:02d}_manifest.json"
        if shard_filter is not None and shard_index not in shard_filter and not existing_manifest.exists():
            continue
        write_checkpoint(shard_rows, shards)
        print(f"[A7FF-CORE59] running shard {shard_index + 1}/{len(shards)} rows={len(shard)}", flush=True)
        shard_rows.append(run_shard(shard_index, shard, str(source.get("decision")), timeout_seconds))
        write_checkpoint(shard_rows, shards)
    shard_summary = pd.DataFrame(shard_rows)
    shard_summary.to_csv(RUNTIME / "a7ffcore59_shard_summary.csv", index=False)

    materialization = collect_shard_csv("materialization_metrics.csv", len(shards))
    responses = collect_shard_csv("label_response_metrics.csv", len(shards))
    selected = collect_shard_csv("selected_portfolio_queue.csv", len(shards))
    if not materialization.empty:
        materialization = materialization.merge(
            queue[["blueprint_id", "core58_queue", "core58_score", "core58_failed_semantic_pair", "core58_failed_motif"]],
            on="blueprint_id",
            how="left",
        )
    if not responses.empty:
        responses = responses.merge(
            queue[["blueprint_id", "core58_queue", "core58_score", "core58_failed_semantic_pair", "core58_failed_motif"]],
            on="blueprint_id",
            how="left",
        )
    if not selected.empty and "blueprint_id" in selected.columns:
        selected = selected.merge(
            queue[["blueprint_id", "core58_queue", "core58_score", "core58_failed_semantic_pair", "core58_failed_motif"]],
            on="blueprint_id",
            how="left",
        )

    materialization_by_semantic = (
        materialization.groupby(["semantic_pair"], as_index=False, dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            eval_success=("eval_success", "sum"),
            activity_ok=("activity_ok", "sum"),
            median_finite_share=("finite_share", "median"),
            median_nonzero_share=("nonzero_share", "median"),
        )
        .sort_values("activity_ok", ascending=False)
        if not materialization.empty
        else pd.DataFrame()
    )
    decision_by_semantic = (
        responses.groupby(["semantic_pair", "decision", "label_family"], as_index=False, dropna=False)
        .size()
        .rename(columns={"size": "row_count"})
        .sort_values("row_count", ascending=False)
        if not responses.empty
        else pd.DataFrame()
    )
    clue_rows = (
        responses[responses["decision"].astype(str).str.contains("NUMERIC_CLUE|RANK_LABEL_DIAGNOSTIC_CLUE", na=False)].copy()
        if not responses.empty
        else pd.DataFrame()
    )
    non_l7_clues = clue_rows[clue_rows["label_family"].ne("L7_ranked_future_return")].copy() if not clue_rows.empty else pd.DataFrame()
    clue_summary = compact_summary(clue_rows, ["semantic_pair", "decision", "label_family"])
    non_l7_summary = compact_summary(non_l7_clues, ["semantic_pair", "decision", "label_family"])
    selected_summary = compact_summary(selected, ["semantic_pair", "label_family"]) if not selected.empty else pd.DataFrame()

    materialization_by_semantic.to_csv(RUNTIME / "a7ffcore59_materialization_by_semantic.csv", index=False)
    decision_by_semantic.to_csv(RUNTIME / "a7ffcore59_decision_by_semantic.csv", index=False)
    clue_summary.to_csv(RUNTIME / "a7ffcore59_clue_summary.csv", index=False)
    non_l7_summary.to_csv(RUNTIME / "a7ffcore59_non_l7_clue_summary.csv", index=False)
    selected_summary.to_csv(RUNTIME / "a7ffcore59_selected_summary.csv", index=False)

    failed_shards = int((shard_summary["returncode"] != 0).sum()) if not shard_summary.empty else len(shards)
    timed_out_shards = int(shard_summary["timed_out"].astype(bool).sum()) if not shard_summary.empty else 0
    eval_fail = int((~materialization["eval_success"].astype(bool)).sum()) if "eval_success" in materialization else len(queue)
    activity_ok = int(materialization["activity_ok"].sum()) if "activity_ok" in materialization else 0
    non_l7_clue_rows = int(len(non_l7_clues))
    non_l7_candidate_count = int(non_l7_clues["blueprint_id"].nunique()) if not non_l7_clues.empty else 0
    non_l7_semantic_count = int(non_l7_clues["semantic_pair"].nunique()) if not non_l7_clues.empty else 0
    selected_count = int(len(selected))
    blockers = []
    if failed_shards:
        blockers.append("numeric_probe_failed_shards")
    if timed_out_shards:
        blockers.append("numeric_probe_timeout_shards")
    if eval_fail:
        blockers.append("eval_failures_present")
    if activity_ok < 512:
        blockers.append("activity_ok_lt_512")
    if non_l7_candidate_count < 24:
        blockers.append("non_l7_candidate_count_lt_24")
    if non_l7_semantic_count < 4:
        blockers.append("non_l7_semantic_count_lt_4")
    if selected_count < 16:
        blockers.append("selected_queue_lt_16")
    decision = "PASS_A7FFCORE59_NUMERIC_REPAIR_EXECUTION_READY_FOR_CORE60" if not blockers else "HOLD_A7FFCORE59_NUMERIC_REPAIR_EXECUTION"
    manifest = {
        "stage": "A7FF-CORE59",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE58",
        "source_decision": source.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "external_runtime_dir": str(EXTERNAL).replace("\\", "/"),
        "input_queue_rows": int(len(queue)),
        "shard_count": int(len(shards)),
        "failed_shard_count": failed_shards,
        "timed_out_shard_count": timed_out_shards,
        "eval_failure_count": eval_fail,
        "materialized_activity_ok_count": activity_ok,
        "label_response_rows": int(len(responses)),
        "non_l7_numeric_clue_rows": non_l7_clue_rows,
        "non_l7_candidate_count": non_l7_candidate_count,
        "non_l7_semantic_pair_count": non_l7_semantic_count,
        "rank_label_diagnostic_clue_rows": int(shard_summary["rank_label_diagnostic_clue_rows"].sum()) if not shard_summary.empty else 0,
        "selected_portfolio_queue_count": selected_count,
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core60_numeric_forensic": decision.startswith("PASS_"),
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffcore59_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ffcore59_authorization_matrix.json",
        {
            "authorized": {"A7FF-CORE60 numeric repair forensic": decision.startswith("PASS_")},
            "not_authorized": {"large_search": True, "alpha_proof": True, "shadow_paper_live": True},
        },
    )
    write_json(
        RUNTIME / "a7ffcore59_external_artifact_manifest.json",
        {
            "external_runtime_dir": str(EXTERNAL).replace("\\", "/"),
            "repo_keeps": [
                "manifest",
                "authorization",
                "materialization_by_semantic",
                "decision_by_semantic",
                "clue summaries",
                "selected summary",
            ],
            "external_keeps": ["full shard label/control/nonoverlap/materialization outputs and logs"],
        },
    )

    report = [
        "# CRYPTO A7FF-CORE59 NUMERIC REPAIR EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE59 executes the numeric probe over the CORE58 failure-aware numeric queue. It is numeric execution, not replay/search/proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Shard Summary",
        "",
        md_table(shard_summary),
        "",
        "## Materialization By Semantic",
        "",
        md_table(materialization_by_semantic),
        "",
        "## Decision By Semantic",
        "",
        md_table(decision_by_semantic),
        "",
        "## Non-L7 Clue Summary",
        "",
        md_table(non_l7_summary),
        "",
        "## Selected Summary",
        "",
        md_table(selected_summary),
        "",
        "## External Detail Artifacts",
        "",
        "```text",
        str(EXTERNAL).replace("\\", "/"),
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "numeric probe executed: true",
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
