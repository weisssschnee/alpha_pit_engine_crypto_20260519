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
RUNTIME = REPO / "runtime" / "a7input3_tag_aware_numeric_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7INPUT3_TAG_AWARE_NUMERIC_PREFLIGHT_20260603.md"
DETAIL_REPORT = REPO / "reports" / "CRYPTO_A7INPUT3_NUMERIC_PROBE_DETAIL_20260603.md"

A7INPUT2 = REPO / "runtime" / "a7input2_tag_aware_queue_builder"
A7INPUT2_MANIFEST = A7INPUT2 / "a7input2_queue_manifest.json"
NUMERIC_PROBE = REPO / "scripts" / "crypto_a7ff8_expanded_numeric_probe.py"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
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


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def sample_queue() -> pd.DataFrame:
    ordinary_n = int(os.environ.get("A7INPUT3_ORDINARY_ROWS", "512"))
    interaction_n = int(os.environ.get("A7INPUT3_INTERACTION_ROWS", "512"))
    rescue_n = int(os.environ.get("A7INPUT3_RESCUE_ROWS", "192"))
    ordinary_all = read_csv(A7INPUT2 / "a7input2_ordinary_alpha_queue.csv")
    interaction_all = read_csv(A7INPUT2 / "a7input2_interaction_queue.csv")
    rescue_all = read_csv(A7INPUT2 / "a7input2_rescue_queue.csv")
    ordinary = ordinary_all.head(ordinary_n).copy()
    used = set(ordinary["blueprint_id"].astype(str))
    interaction = interaction_all[~interaction_all["blueprint_id"].astype(str).isin(used)].head(interaction_n).copy()
    used.update(interaction["blueprint_id"].astype(str))
    rescue = rescue_all[~rescue_all["blueprint_id"].astype(str).isin(used)].head(rescue_n).copy()
    ordinary["a7input_queue"] = "ordinary_alpha"
    interaction["a7input_queue"] = "interaction_alpha"
    rescue["a7input_queue"] = "rescue_lane"
    queue = pd.concat([ordinary, interaction, rescue], ignore_index=True)
    if queue.empty:
        raise SystemExit("A7INPUT-3 queue is empty")
    return queue


def compact_summary(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[*group_cols, "row_count"])
    return df.groupby(group_cols, dropna=False).size().reset_index(name="row_count").sort_values("row_count", ascending=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(A7INPUT2_MANIFEST)
    if not source.get("authorizes_core54_queue_builder_contract"):
        raise SystemExit(f"A7INPUT-2 does not authorize numeric preflight input: {source.get('decision')}")

    queue = sample_queue()
    queue_path = RUNTIME / "a7input3_numeric_preflight_queue.csv"
    queue.to_csv(queue_path, index=False)

    started = now_utc()
    env = os.environ.copy()
    env.update(
        {
            "A7FF8_STAGE": "A7INPUT-3",
            "A7FF8_FILE_PREFIX": "a7input3",
            "A7FF8_RUNTIME": str(RUNTIME),
            "A7FF8_REPORT": str(DETAIL_REPORT),
            "A7FF8_QUEUE_PATH": str(queue_path),
            "A7FF8_AUTH_MANIFEST": str(A7INPUT2_MANIFEST),
            "A7FF8_AUTH_DECISION": str(source.get("decision")),
            "A7FF8_MATERIALIZE_CAP": str(len(queue)),
            "A7FF8_FAST_NUMERIC_CAP": str(len(queue)),
            "A7FF8_PORTFOLIO_CAP": "192",
            "A7FF8_QUEUE_OFFSET": "0",
            "A7FF8_QUEUE_LIMIT": str(len(queue)),
            "A7FF8_WRITE_CONTROL_DETAIL": "1",
        }
    )
    timeout_seconds = int(os.environ.get("A7INPUT3_TIMEOUT_SECONDS", "7200"))
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
    (RUNTIME / "a7input3_numeric_probe_stdout.log").write_text(stdout, encoding="utf-8")

    numeric_manifest = read_json(RUNTIME / "a7input3_manifest.json")
    materialization = read_csv(RUNTIME / "a7input3_materialization_metrics.csv")
    responses = read_csv(RUNTIME / "a7input3_label_response_metrics.csv")
    controls = read_csv(RUNTIME / "a7input3_control_dominance_metrics.csv")
    selected = read_csv(RUNTIME / "a7input3_selected_portfolio_queue.csv")

    materialization = materialization.merge(
        queue[["blueprint_id", "a7input_queue", "input_tags", "input_clusters", "input_semantic_types"]],
        on="blueprint_id",
        how="left",
    ) if not materialization.empty else materialization
    responses = responses.merge(
        queue[["blueprint_id", "a7input_queue", "input_tags", "input_clusters", "input_semantic_types"]],
        on="blueprint_id",
        how="left",
    ) if not responses.empty else responses
    selected = selected.merge(
        queue[["blueprint_id", "a7input_queue", "input_tags", "input_clusters", "input_semantic_types"]],
        on="blueprint_id",
        how="left",
    ) if not selected.empty and "blueprint_id" in selected.columns else selected

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
    semantic_response = compact_summary(
        responses[responses["decision"].astype(str).str.contains("NUMERIC_CLUE|RANK_LABEL_DIAGNOSTIC_CLUE", na=False)]
        if not responses.empty
        else pd.DataFrame(),
        ["a7input_queue", "semantic_pair", "decision", "label_family"],
    )
    selected_summary = compact_summary(selected, ["a7input_queue", "semantic_pair", "label_family"]) if not selected.empty else pd.DataFrame()

    mat_by_queue.to_csv(RUNTIME / "a7input3_materialization_by_queue.csv", index=False)
    decision_by_queue.to_csv(RUNTIME / "a7input3_decision_by_queue.csv", index=False)
    semantic_response.to_csv(RUNTIME / "a7input3_semantic_response_summary.csv", index=False)
    selected_summary.to_csv(RUNTIME / "a7input3_selected_summary.csv", index=False)

    eval_fail = int((~materialization["eval_success"].astype(bool)).sum()) if "eval_success" in materialization else len(queue)
    activity_ok = int(materialization["activity_ok"].sum()) if "activity_ok" in materialization else 0
    non_l7_clues = int(numeric_manifest.get("non_l7_numeric_clue_rows", 0) or 0)
    selected_count = int(numeric_manifest.get("selected_portfolio_queue_count", 0) or 0)
    blockers = []
    if returncode != 0:
        blockers.append("numeric_probe_process_failed")
    if timed_out:
        blockers.append("numeric_probe_timeout")
    if eval_fail > 0:
        blockers.append("eval_failures_present")
    if activity_ok < max(32, int(len(queue) * 0.20)):
        blockers.append("activity_ok_too_low")
    if non_l7_clues <= 0:
        blockers.append("no_non_l7_numeric_clues")
    if selected_count < 8:
        blockers.append("selected_portfolio_queue_too_small")

    decision = "PASS_A7INPUT3_TAG_AWARE_NUMERIC_PREFLIGHT_READY_FOR_CORE54E" if not blockers else "HOLD_A7INPUT3_TAG_AWARE_NUMERIC_PREFLIGHT"
    manifest = {
        "stage": "A7INPUT-3",
        "generated_at": now_utc(),
        "started_at": started,
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7INPUT-2",
        "source_decision": source.get("decision"),
        "process_exit_code": returncode,
        "timed_out": timed_out,
        "timeout_seconds": timeout_seconds,
        "input_queue_rows": int(len(queue)),
        "ordinary_rows": int((queue["a7input_queue"] == "ordinary_alpha").sum()),
        "interaction_rows": int((queue["a7input_queue"] == "interaction_alpha").sum()),
        "rescue_rows": int((queue["a7input_queue"] == "rescue_lane").sum()),
        "numeric_probe_decision": numeric_manifest.get("decision"),
        "eval_failure_count": eval_fail,
        "materialized_activity_ok_count": activity_ok,
        "label_response_rows": int(len(responses)),
        "control_rows": int(len(controls)),
        "non_l7_numeric_clue_rows": non_l7_clues,
        "rank_label_diagnostic_clue_rows": int(numeric_manifest.get("rank_label_diagnostic_clue_rows", 0) or 0),
        "portfolio_queue_count": int(numeric_manifest.get("portfolio_queue_count", 0) or 0),
        "selected_portfolio_queue_count": selected_count,
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core54e_tag_aware_numeric_execution": decision.startswith("PASS_"),
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7input3_manifest.json", manifest)
    write_json(
        RUNTIME / "a7input3_authorization_matrix.json",
        {
            "authorized": {
                "A7FF-CORE54E tag-aware numeric execution": decision.startswith("PASS_"),
            },
            "not_authorized": {
                "large_search": True,
                "alpha_proof": True,
                "shadow_paper_live": True,
            },
        },
    )

    report = [
        "# CRYPTO A7INPUT-3 TAG-AWARE NUMERIC PREFLIGHT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7INPUT-3 runs the existing numeric probe over a substantial tag-aware queue sample. This is execution progress, not another approval-only contract. It still does not run full replay, formula search, alpha proof, shadow, paper, or live.",
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
