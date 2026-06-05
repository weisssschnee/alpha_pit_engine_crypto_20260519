from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
NUMERIC_PROBE = REPO / "scripts" / "crypto_a7ff8_expanded_numeric_probe.py"
CORE64 = REPO / "runtime" / "a7ffcore64_retest_and_funding_state_package"
CORE59 = REPO / "runtime" / "a7ffcore59_numeric_repair_execution"

RUNTIME = REPO / "runtime" / "a7ffcore65b_funding_state_retest_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE65B_FUNDING_STATE_RETEST_EXECUTION_20260605.md"

FUNDING_PAIRS = {"basis_premium_like|funding_like", "funding_like|positioning_like"}
RAW_FUNDING_TOKEN = re.compile(r"\bfunding_rate\b")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


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
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```csv\n" + view.to_csv(index=False) + "```"


def build_patched_queue(limit: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    source = read_csv(CORE59 / "a7ffcore59_numeric_repair_queue.csv")
    if source.empty:
        raise SystemExit("CORE65B requires CORE59 numeric repair queue")
    q = source[source["semantic_pair"].isin(FUNDING_PAIRS)].copy()
    if q.empty:
        raise SystemExit("CORE65B found no funding semantic-pair rows")

    q["core65b_original_blueprint_id"] = q["blueprint_id"]
    q["core65b_original_expression"] = q["expression"]
    q["expression"] = q["expression"].map(lambda x: RAW_FUNDING_TOKEN.sub("funding_rate_state_last_ffill_8h", str(x)))
    q["blueprint_id"] = q["blueprint_id"].astype(str) + "_funding_state8h"
    q["semantic_pair"] = q["semantic_pair"].map(
        {
            "basis_premium_like|funding_like": "basis_premium_like|funding_state_like",
            "funding_like|positioning_like": "funding_state_like|positioning_like",
        }
    ).fillna(q["semantic_pair"])
    q["primary_field"] = q.get("primary_field", "").replace({"funding_rate": "funding_rate_state_last_ffill_8h"})
    q["secondary_field"] = q.get("secondary_field", "").replace({"funding_rate": "funding_rate_state_last_ffill_8h"})
    q["core65b_patch"] = "funding_rate_to_pit_last_known_state_8h"
    q["a7input_queue"] = "funding_state_materialization_repair"

    q = q.sort_values(["semantic_pair", "motif", "blueprint_id"]).reset_index(drop=True)
    full_queue = q.copy()
    if limit and len(q) > limit:
        rows = []
        # Diverse first by semantic pair and motif.
        for _, group in q.groupby(["semantic_pair", "motif"], sort=False):
            rows.append(group.head(max(1, limit // max(1, q[["semantic_pair", "motif"]].drop_duplicates().shape[0]))))
        sampled = pd.concat(rows, ignore_index=True).drop_duplicates("blueprint_id")
        if len(sampled) < limit:
            extra = q[~q["blueprint_id"].isin(set(sampled["blueprint_id"]))].head(limit - len(sampled))
            sampled = pd.concat([sampled, extra], ignore_index=True)
        q = sampled.head(limit).copy()

    full_queue.to_csv(RUNTIME / "core65b_full_patched_funding_state_queue.csv", index=False)
    q.to_csv(RUNTIME / "core65b_patched_funding_state_retest_queue.csv", index=False)
    return q, full_queue


def run_numeric(queue: pd.DataFrame) -> dict[str, Any]:
    queue_path = RUNTIME / "core65b_patched_funding_state_retest_queue.csv"
    runtime_dir = RUNTIME / "numeric_probe"
    report_path = RUNTIME / "CRYPTO_A7FFCORE65B_NUMERIC_DETAIL_20260605.md"
    env = os.environ.copy()
    env.update(
        {
            "A7FF8_STAGE": "A7FF-CORE65B",
            "A7FF8_FILE_PREFIX": "a7ffcore65b",
            "A7FF8_RUNTIME": str(runtime_dir),
            "A7FF8_REPORT": str(report_path),
            "A7FF8_QUEUE_PATH": str(queue_path),
            "A7FF8_AUTH_MANIFEST": str(CORE64 / "core64_manifest.json"),
            "A7FF8_AUTH_DECISION": "HOLD_CORE64_PACKAGE_READY_WITH_FUNDING_REPAIR_REQUIRED",
            "A7FF8_MATERIALIZE_CAP": str(len(queue)),
            "A7FF8_FAST_NUMERIC_CAP": str(len(queue)),
            "A7FF8_PORTFOLIO_CAP": "64",
            "A7FF8_QUEUE_LIMIT": str(len(queue)),
            "A7FF8_WRITE_CONTROL_DETAIL": "1",
        }
    )
    proc = subprocess.run(
        [sys.executable, str(NUMERIC_PROBE)],
        cwd=REPO,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=int(os.environ.get("A7FFCORE65B_TIMEOUT_SECONDS", "1800")),
    )
    (RUNTIME / "core65b_numeric_probe_stdout.log").write_text(proc.stdout, encoding="utf-8")
    manifest = read_json(runtime_dir / "a7ffcore65b_manifest.json")
    manifest["returncode"] = proc.returncode
    return manifest


def summarize_numeric() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    runtime_dir = RUNTIME / "numeric_probe"
    material = read_csv(runtime_dir / "a7ffcore65b_materialization_metrics.csv")
    responses = read_csv(runtime_dir / "a7ffcore65b_label_response_metrics.csv")
    selected = read_csv(runtime_dir / "a7ffcore65b_selected_portfolio_queue.csv")
    material_summary = (
        material.groupby(["semantic_pair"], dropna=False).agg(
            rows=("blueprint_id", "size"),
            eval_success=("eval_success", "sum"),
            activity_ok=("activity_ok", "sum"),
            median_finite_share=("finite_share", "median"),
            median_nonzero_share=("nonzero_share", "median"),
        ).reset_index()
        if not material.empty
        else pd.DataFrame()
    )
    response_summary = (
        responses.groupby(["semantic_pair", "decision", "label_family"], dropna=False).size().reset_index(name="rows")
        if not responses.empty
        else pd.DataFrame()
    )
    selected_summary = (
        selected.groupby(["semantic_pair", "label_family"], dropna=False).size().reset_index(name="rows")
        if not selected.empty
        else pd.DataFrame()
    )
    material_summary.to_csv(RUNTIME / "core65b_materialization_summary.csv", index=False)
    response_summary.to_csv(RUNTIME / "core65b_response_summary.csv", index=False)
    selected_summary.to_csv(RUNTIME / "core65b_selected_summary.csv", index=False)
    return material_summary, response_summary, selected_summary


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    limit = int(os.environ.get("A7FFCORE65B_QUEUE_LIMIT", "128"))
    queue, full_queue = build_patched_queue(limit)
    numeric_manifest = run_numeric(queue)
    material_summary, response_summary, selected_summary = summarize_numeric()

    materialized_activity_ok = int(numeric_manifest.get("materialized_activity_ok_count", 0) or 0)
    non_l7_clues = int(numeric_manifest.get("non_l7_numeric_clue_rows", 0) or 0)
    selected_count = int(numeric_manifest.get("selected_portfolio_queue_count", 0) or 0)
    blockers: list[str] = []
    if numeric_manifest.get("returncode") != 0:
        blockers.append("numeric_probe_returncode_nonzero")
    if materialized_activity_ok < max(16, int(0.5 * len(queue))):
        blockers.append("funding_state_materialization_activity_still_weak")
    if non_l7_clues < 4:
        blockers.append("funding_state_non_l7_clues_lt_4")
    if selected_count < 4:
        blockers.append("funding_state_selected_queue_lt_4")

    decision = "PASS_CORE65B_FUNDING_STATE_REPAIR_NUMERIC_CLUES_FOUND" if not blockers else "HOLD_CORE65B_FUNDING_STATE_REPAIR_STILL_WEAK"
    manifest = {
        "stage": "A7FF-CORE65B",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "full_patched_queue_rows": int(len(full_queue)),
        "executed_queue_rows": int(len(queue)),
        "numeric_decision": numeric_manifest.get("decision"),
        "numeric_returncode": numeric_manifest.get("returncode"),
        "materialized_activity_ok_count": materialized_activity_ok,
        "label_response_rows": int(numeric_manifest.get("label_response_rows", 0) or 0),
        "non_l7_numeric_clue_rows": non_l7_clues,
        "rank_label_diagnostic_clue_rows": int(numeric_manifest.get("rank_label_diagnostic_clue_rows", 0) or 0),
        "selected_portfolio_queue_count": selected_count,
        "executes_generation": False,
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    write_json(RUNTIME / "core65b_manifest.json", manifest)
    write_json(RUNTIME / "core65b_decision_record.json", manifest)

    REPORT.write_text("\n".join([
        "# CRYPTO A7FF-CORE65B FUNDING STATE RETEST EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE65B rewrites raw `funding_rate` formulas to PIT dense `funding_rate_state_last_ffill_8h` formulas and executes a bounded numeric retest. It does not run formula search, replay promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Materialization Summary",
        "",
        md_table(material_summary, 80),
        "",
        "## Response Summary",
        "",
        md_table(response_summary, 80),
        "",
        "## Selected Summary",
        "",
        md_table(selected_summary, 80),
        "",
    ]), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
