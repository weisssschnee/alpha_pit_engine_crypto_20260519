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
A7INPUT2 = REPO / "runtime" / "a7input2_tag_aware_queue_builder"
A7INPUT3 = REPO / "runtime" / "a7input3_tag_aware_numeric_preflight"
NUMERIC_PROBE = REPO / "scripts" / "crypto_a7ff8_expanded_numeric_probe.py"

RUNTIME = REPO / "runtime" / "a7ffcore54e_tag_aware_numeric_execution"
EXTERNAL = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore54e_tag_aware_numeric_execution_20260604")
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE54E_TAG_AWARE_NUMERIC_EXECUTION_20260604.md"
DETAIL_REPORT = EXTERNAL / "CRYPTO_A7FFCORE54E_NUMERIC_PROBE_DETAIL_20260604.md"


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
    return pd.read_csv(path)


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def build_main_queue() -> pd.DataFrame:
    ordinary = read_csv(A7INPUT2 / "a7input2_ordinary_alpha_queue.csv").copy()
    interaction = read_csv(A7INPUT2 / "a7input2_interaction_queue.csv").copy()
    ordinary["a7input_queue"] = "ordinary_alpha"
    interaction["a7input_queue"] = "interaction_alpha"
    used = set(ordinary["blueprint_id"].astype(str))
    interaction = interaction[~interaction["blueprint_id"].astype(str).isin(used)].copy()
    queue = pd.concat([ordinary, interaction], ignore_index=True)
    queue = queue.drop_duplicates("blueprint_id").reset_index(drop=True)
    if queue.empty:
        raise SystemExit("CORE54E main queue is empty")
    return queue


def compact_summary(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[*group_cols, "row_count"])
    return df.groupby(group_cols, dropna=False).size().reset_index(name="row_count").sort_values("row_count", ascending=False)


def shard_queue(queue: pd.DataFrame, rows_per_shard: int) -> list[tuple[int, pd.DataFrame]]:
    shards: list[tuple[int, pd.DataFrame]] = []
    for shard_index, start in enumerate(range(0, len(queue), rows_per_shard)):
        shards.append((shard_index, queue.iloc[start : start + rows_per_shard].copy()))
    return shards


def run_numeric_probe_for_shard(shard_index: int, shard: pd.DataFrame, source_decision: str, timeout_seconds: int) -> dict[str, Any]:
    shard_dir = EXTERNAL / f"shard_{shard_index:02d}"
    shard_dir.mkdir(parents=True, exist_ok=True)
    shard_queue_path = shard_dir / f"a7ffcore54e_s{shard_index:02d}_queue.csv"
    shard.to_csv(shard_queue_path, index=False)
    file_prefix = f"a7ffcore54e_s{shard_index:02d}"
    detail_report = shard_dir / f"CRYPTO_A7FFCORE54E_S{shard_index:02d}_NUMERIC_PROBE_DETAIL_20260604.md"
    existing_manifest = shard_dir / f"{file_prefix}_manifest.json"
    if existing_manifest.exists() and os.environ.get("A7FFCORE54E_FORCE_RERUN", "0").lower() not in {"1", "true", "yes"}:
        manifest = read_json(existing_manifest)
        return {
            "shard": f"s{shard_index:02d}",
            "started_at": "",
            "finished_at": now_utc(),
            "returncode": 0 if manifest else -1,
            "timed_out": False,
            "runtime_dir": str(shard_dir).replace("\\", "/"),
            "queue_rows": int(len(shard)),
            "ordinary_rows": int((shard["a7input_queue"] == "ordinary_alpha").sum()),
            "interaction_rows": int((shard["a7input_queue"] == "interaction_alpha").sum()),
            "decision": manifest.get("decision", "NO_MANIFEST"),
            "blockers": ";".join(manifest.get("blockers", [])) if manifest else "no_manifest",
            "materialized_activity_ok_count": int(manifest.get("materialized_activity_ok_count", 0) or 0),
            "label_response_rows": int(manifest.get("label_response_rows", 0) or 0),
            "non_l7_numeric_clue_rows": int(manifest.get("non_l7_numeric_clue_rows", 0) or 0),
            "rank_label_diagnostic_clue_rows": int(manifest.get("rank_label_diagnostic_clue_rows", 0) or 0),
            "selected_portfolio_queue_count": int(manifest.get("selected_portfolio_queue_count", 0) or 0),
            "reused_existing": True,
        }
    env = os.environ.copy()
    env.update(
        {
            "A7FF8_STAGE": f"A7FF-CORE54E-S{shard_index:02d}",
            "A7FF8_FILE_PREFIX": file_prefix,
            "A7FF8_RUNTIME": str(shard_dir),
            "A7FF8_REPORT": str(detail_report),
            "A7FF8_QUEUE_PATH": str(shard_queue_path),
            "A7FF8_AUTH_MANIFEST": str(A7INPUT3 / "a7input3_manifest.json"),
            "A7FF8_AUTH_DECISION": source_decision,
            "A7FF8_MATERIALIZE_CAP": str(len(shard)),
            "A7FF8_FAST_NUMERIC_CAP": str(len(shard)),
            "A7FF8_PORTFOLIO_CAP": "128",
            "A7FF8_QUEUE_OFFSET": "0",
            "A7FF8_QUEUE_LIMIT": str(len(shard)),
            "A7FF8_WRITE_CONTROL_DETAIL": "1",
        }
    )
    started = now_utc()
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
        "started_at": started,
        "finished_at": now_utc(),
        "returncode": returncode,
        "timed_out": timed_out,
        "runtime_dir": str(shard_dir).replace("\\", "/"),
        "queue_rows": int(len(shard)),
        "ordinary_rows": int((shard["a7input_queue"] == "ordinary_alpha").sum()),
        "interaction_rows": int((shard["a7input_queue"] == "interaction_alpha").sum()),
        "decision": manifest.get("decision", "NO_MANIFEST"),
        "blockers": ";".join(manifest.get("blockers", [])) if manifest else "no_manifest",
        "materialized_activity_ok_count": int(manifest.get("materialized_activity_ok_count", 0) or 0),
        "label_response_rows": int(manifest.get("label_response_rows", 0) or 0),
        "non_l7_numeric_clue_rows": int(manifest.get("non_l7_numeric_clue_rows", 0) or 0),
        "rank_label_diagnostic_clue_rows": int(manifest.get("rank_label_diagnostic_clue_rows", 0) or 0),
        "selected_portfolio_queue_count": int(manifest.get("selected_portfolio_queue_count", 0) or 0),
        "reused_existing": False,
    }


def collect_shard_csv(name: str, shard_count: int) -> pd.DataFrame:
    frames = []
    for shard_index in range(shard_count):
        path = EXTERNAL / f"shard_{shard_index:02d}" / f"a7ffcore54e_s{shard_index:02d}_{name}"
        frame = read_csv(path)
        if not frame.empty:
            frame["core54e_shard"] = f"s{shard_index:02d}"
            frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    EXTERNAL.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7input2 = read_json(A7INPUT2 / "a7input2_queue_manifest.json")
    a7input3 = read_json(A7INPUT3 / "a7input3_manifest.json")
    if not a7input2.get("authorizes_core54_queue_builder_contract"):
        raise SystemExit(f"A7INPUT-2 not ready: {a7input2.get('decision')}")
    if not a7input3.get("authorizes_core54e_tag_aware_numeric_execution"):
        raise SystemExit(f"A7INPUT-3 not ready: {a7input3.get('decision')}")

    queue = build_main_queue()
    queue_path = RUNTIME / "a7ffcore54e_main_numeric_queue.csv"
    queue.to_csv(queue_path, index=False)
    queue.to_csv(EXTERNAL / "a7ffcore54e_main_numeric_queue.csv", index=False)

    started = now_utc()
    timeout_seconds = int(os.environ.get("A7FFCORE54E_TIMEOUT_SECONDS", "28800"))
    shard_rows = int(os.environ.get("A7FFCORE54E_ROWS_PER_SHARD", "256"))
    shards = shard_queue(queue, shard_rows)
    shard_results = []
    for shard_index, shard in shards:
        print(f"[A7FF-CORE54E] running shard {shard_index + 1}/{len(shards)} rows={len(shard)}", flush=True)
        shard_results.append(run_numeric_probe_for_shard(shard_index, shard, str(a7input3.get("decision")), timeout_seconds))
    shard_summary = pd.DataFrame(shard_results)
    shard_summary.to_csv(RUNTIME / "a7ffcore54e_shard_summary.csv", index=False)

    materialization = collect_shard_csv("materialization_metrics.csv", len(shards))
    responses = collect_shard_csv("label_response_metrics.csv", len(shards))
    selected = collect_shard_csv("selected_portfolio_queue.csv", len(shards))

    if not materialization.empty:
        materialization = materialization.merge(
            queue[["blueprint_id", "a7input_queue", "input_tags", "input_clusters", "input_semantic_types"]],
            on="blueprint_id",
            how="left",
        )
    if not responses.empty:
        responses = responses.merge(
            queue[["blueprint_id", "a7input_queue", "input_tags", "input_clusters", "input_semantic_types"]],
            on="blueprint_id",
            how="left",
        )
    if not selected.empty and "blueprint_id" in selected.columns:
        selected = selected.merge(
            queue[["blueprint_id", "a7input_queue", "input_tags", "input_clusters", "input_semantic_types"]],
            on="blueprint_id",
            how="left",
        )

    mat_by_queue = (
        materialization.groupby("a7input_queue", dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            eval_success=("eval_success", "sum"),
            activity_ok=("activity_ok", "sum"),
            median_finite_share=("finite_share", "median"),
            median_nonzero_share=("nonzero_share", "median"),
        )
        .reset_index()
        if not materialization.empty
        else pd.DataFrame()
    )
    decision_by_queue = (
        responses.groupby(["a7input_queue", "decision", "label_family"], dropna=False)
        .size()
        .reset_index(name="row_count")
        .sort_values("row_count", ascending=False)
        if not responses.empty
        else pd.DataFrame()
    )
    clue_rows = (
        responses[responses["decision"].astype(str).str.contains("NUMERIC_CLUE|RANK_LABEL_DIAGNOSTIC_CLUE", na=False)]
        if not responses.empty
        else pd.DataFrame()
    )
    semantic_response = compact_summary(clue_rows, ["a7input_queue", "semantic_pair", "decision", "label_family"])
    selected_summary = compact_summary(selected, ["a7input_queue", "semantic_pair", "label_family"]) if not selected.empty else pd.DataFrame()

    mat_by_queue.to_csv(RUNTIME / "a7ffcore54e_materialization_by_queue.csv", index=False)
    decision_by_queue.to_csv(RUNTIME / "a7ffcore54e_decision_by_queue.csv", index=False)
    semantic_response.to_csv(RUNTIME / "a7ffcore54e_semantic_response_summary.csv", index=False)
    selected_summary.to_csv(RUNTIME / "a7ffcore54e_selected_summary.csv", index=False)

    eval_fail = int((~materialization["eval_success"].astype(bool)).sum()) if "eval_success" in materialization else len(queue)
    activity_ok = int(materialization["activity_ok"].sum()) if "activity_ok" in materialization else 0
    non_l7_clues = int(shard_summary["non_l7_numeric_clue_rows"].sum()) if not shard_summary.empty else 0
    selected_count = int(shard_summary["selected_portfolio_queue_count"].sum()) if not shard_summary.empty else 0
    failed_shards = int((shard_summary["returncode"] != 0).sum()) if not shard_summary.empty else len(shards)
    timed_out_shards = int(shard_summary["timed_out"].astype(bool).sum()) if not shard_summary.empty and "timed_out" in shard_summary else 0
    blockers = []
    if failed_shards:
        blockers.append("numeric_probe_process_failed_shards")
    if timed_out_shards:
        blockers.append("numeric_probe_timeout_shards")
    if eval_fail > 0:
        blockers.append("eval_failures_present")
    if activity_ok < max(128, int(len(queue) * 0.20)):
        blockers.append("activity_ok_too_low")
    if non_l7_clues <= 0:
        blockers.append("no_non_l7_numeric_clues")
    if selected_count < 16:
        blockers.append("selected_portfolio_queue_too_small")

    decision = "PASS_A7FFCORE54E_TAG_AWARE_NUMERIC_EXECUTION_READY_FOR_CORE55" if not blockers else "HOLD_A7FFCORE54E_TAG_AWARE_NUMERIC_EXECUTION"
    manifest = {
        "stage": "A7FF-CORE54E",
        "generated_at": now_utc(),
        "started_at": started,
        "decision": decision,
        "blockers": blockers,
        "source_stages": ["A7INPUT-2", "A7INPUT-3"],
        "source_decisions": [a7input2.get("decision"), a7input3.get("decision")],
        "external_runtime_dir": str(EXTERNAL).replace("\\", "/"),
        "process_exit_code": 0 if failed_shards == 0 else -1,
        "timed_out": bool(timed_out_shards),
        "timeout_seconds": timeout_seconds,
        "input_queue_rows": int(len(queue)),
        "ordinary_rows": int((queue["a7input_queue"] == "ordinary_alpha").sum()),
        "interaction_rows": int((queue["a7input_queue"] == "interaction_alpha").sum()),
        "shard_count": int(len(shards)),
        "failed_shard_count": failed_shards,
        "timed_out_shard_count": timed_out_shards,
        "eval_failure_count": eval_fail,
        "materialized_activity_ok_count": activity_ok,
        "label_response_rows": int(len(responses)),
        "non_l7_numeric_clue_rows": non_l7_clues,
        "rank_label_diagnostic_clue_rows": int(shard_summary["rank_label_diagnostic_clue_rows"].sum()) if not shard_summary.empty else 0,
        "portfolio_queue_count": 0,
        "selected_portfolio_queue_count": selected_count,
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core55_numeric_forensic": decision.startswith("PASS_"),
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffcore54e_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ffcore54e_authorization_matrix.json",
        {
            "authorized": {
                "A7FF-CORE55 numeric clue forensic": decision.startswith("PASS_"),
            },
            "not_authorized": {
                "replay": True,
                "large_search": True,
                "alpha_proof": True,
                "shadow_paper_live": True,
            },
        },
    )
    write_json(
        RUNTIME / "a7ffcore54e_external_artifact_manifest.json",
        {
            "external_runtime_dir": str(EXTERNAL).replace("\\", "/"),
            "repo_keeps": [
                "manifest",
                "authorization",
                "materialization_by_queue",
                "decision_by_queue",
                "semantic_response_summary",
                "selected_summary",
                "compact selected/portfolio/materialization files",
            ],
            "external_keeps": [
                "full label_response_metrics",
                "full control_dominance_metrics",
                "full nonoverlap_stats",
                "stdout detail",
                "numeric probe detail report",
            ],
        },
    )

    report = [
        "# CRYPTO A7FF-CORE54E TAG-AWARE NUMERIC EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE54E runs the existing numeric probe over the full A7INPUT-2 main queue: ordinary-alpha plus interaction-alpha, excluding rescue lane from the main path. It is numeric execution, not replay/search/proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Materialization By Queue",
        "",
        md_table(mat_by_queue, 20),
        "",
        "## Shard Summary",
        "",
        md_table(shard_summary, 40),
        "",
        "## Decision By Queue",
        "",
        md_table(decision_by_queue, 80),
        "",
        "## Semantic Response Summary",
        "",
        md_table(semantic_response, 80),
        "",
        "## Selected Summary",
        "",
        md_table(selected_summary, 80),
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
