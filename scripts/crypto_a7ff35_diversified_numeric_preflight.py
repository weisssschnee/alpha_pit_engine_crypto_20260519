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
RUNTIME = REPO / "runtime" / "a7ff35_diversified_numeric_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7FF35_DIVERSIFIED_NUMERIC_PREFLIGHT_20260530.md"

A7FF34_MANIFEST = REPO / "runtime" / "a7ff34_family_queue_coverage_audit" / "a7ff34_manifest.json"
A7FF33_COMPANY = REPO / "runtime" / "a7ff33_family_diversified_dry_generation" / "a7ff33_company_numeric_wave_queue.csv"
NUMERIC_PROBE = REPO / "scripts" / "crypto_a7ff8_expanded_numeric_probe.py"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


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
        return "```text\n" + view.to_string(index=False) + "\n```"


def sample_diversified_queue(company: pd.DataFrame) -> pd.DataFrame:
    rows_per_bucket = int(os.environ.get("A7FF35_ROWS_PER_FAMILY_MOTIF", "2"))
    max_rows = int(os.environ.get("A7FF35_MAX_ROWS", "140"))
    parts = []
    for _, group in company.groupby(["family_id", "motif"], sort=True):
        parts.append(group.head(rows_per_bucket).copy())
    sample = pd.concat(parts, ignore_index=True).drop_duplicates("blueprint_id") if parts else pd.DataFrame()
    if len(sample) < max_rows:
        extra = company[~company["blueprint_id"].isin(set(sample["blueprint_id"]))].head(max_rows - len(sample))
        sample = pd.concat([sample, extra], ignore_index=True)
    return sample.head(max_rows).copy()


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    f34 = read_json(A7FF34_MANIFEST)
    if not f34.get("authorizes_a7ff35_numeric_prefight"):
        raise SystemExit(f"A7FF-34 does not authorize A7FF-35: {f34.get('decision')}")

    company = pd.read_csv(A7FF33_COMPANY)
    sample = sample_diversified_queue(company)
    sample_path = RUNTIME / "a7ff35_diversified_sample_queue.csv"
    sample.to_csv(sample_path, index=False)

    sample_coverage = (
        sample.groupby(["family_id", "motif"], dropna=False).size().reset_index(name="sample_count").sort_values(["family_id", "motif"])
    )
    sample_coverage.to_csv(RUNTIME / "a7ff35_sample_coverage.csv", index=False)

    env = os.environ.copy()
    env.update(
        {
            "A7FF8_STAGE": "A7FF-35",
            "A7FF8_FILE_PREFIX": "a7ff35",
            "A7FF8_RUNTIME": str(RUNTIME),
            "A7FF8_REPORT": str(REPORT),
            "A7FF8_QUEUE_PATH": str(sample_path),
            "A7FF8_MATERIALIZE_CAP": str(len(sample)),
            "A7FF8_FAST_NUMERIC_CAP": str(len(sample)),
            "A7FF8_PORTFOLIO_CAP": "96",
            "A7FF8_QUEUE_OFFSET": "0",
            "A7FF8_QUEUE_LIMIT": str(len(sample)),
        }
    )
    started = now_utc()
    timeout_seconds = int(os.environ.get("A7FF35_TIMEOUT_SECONDS", "2400"))
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
        stdout = (exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace"))
        stdout += f"\nTIMEOUT after {timeout_seconds} seconds\n"
        returncode = -9
        timed_out = True
    (RUNTIME / "a7ff35_numeric_probe_stdout.log").write_text(stdout, encoding="utf-8")

    numeric_manifest = read_json(RUNTIME / "a7ff35_manifest.json")
    materialization = read_csv(RUNTIME / "a7ff35_materialization_metrics.csv")
    responses = read_csv(RUNTIME / "a7ff35_label_response_metrics.csv")
    controls = read_csv(RUNTIME / "a7ff35_control_dominance_metrics.csv")
    selected = read_csv(RUNTIME / "a7ff35_selected_portfolio_queue.csv")

    eval_fail = int((~materialization["eval_success"]).sum()) if "eval_success" in materialization.columns else len(sample)
    eval_success = int(materialization["eval_success"].sum()) if "eval_success" in materialization.columns else 0
    activity_ok = int(materialization["activity_ok"].sum()) if "activity_ok" in materialization.columns else 0
    response_rows = int(len(responses))
    control_rows = int(len(controls))
    selected_rows = int(len(selected))
    missing_field = "missing_numeric_fields" in numeric_manifest.get("blockers", [])

    blockers: list[str] = []
    if returncode != 0:
        blockers.append("numeric_probe_process_failed")
    if timed_out:
        blockers.append("numeric_probe_timeout")
    if missing_field:
        blockers.append("missing_numeric_fields")
    if eval_fail != 0:
        blockers.append("eval_failures_present")
    if activity_ok == 0:
        blockers.append("no_activity")
    if response_rows == 0 or control_rows == 0:
        blockers.append("response_or_control_rows_missing")

    family_activity = (
        materialization.merge(sample[["blueprint_id", "family_id", "motif", "root_family"]], on="blueprint_id", how="left")
        .groupby(["family_id", "root_family"], dropna=False)
        .agg(rows=("blueprint_id", "count"), eval_success=("eval_success", "sum"), activity_ok=("activity_ok", "sum"), finite_share_median=("finite_share", "median"), nonzero_share_median=("nonzero_share", "median"))
        .reset_index()
        if not materialization.empty and "blueprint_id" in materialization.columns
        else pd.DataFrame()
    )
    family_activity.to_csv(RUNTIME / "a7ff35_family_materialization_summary.csv", index=False)

    decision = "PASS_A7FF35_DIVERSIFIED_NUMERIC_PREFLIGHT_COMPLETED_NO_SEARCH_AUTH" if not blockers else "HOLD_A7FF35_DIVERSIFIED_NUMERIC_PREFLIGHT_FAIL"
    manifest = {
        "stage": "A7FF-35",
        "generated_at": now_utc(),
        "started_at": started,
        "decision": decision,
        "blockers": blockers,
        "source_a7ff34_decision": f34.get("decision"),
        "sample_rows": int(len(sample)),
        "sample_family_count": int(sample["family_id"].nunique()),
        "sample_motif_count": int(sample["motif"].nunique()),
        "process_exit_code": returncode,
        "timed_out": timed_out,
        "timeout_seconds": timeout_seconds,
        "numeric_probe_decision": numeric_manifest.get("decision"),
        "eval_success_count": eval_success,
        "eval_failure_count": eval_fail,
        "activity_ok_count": activity_ok,
        "label_response_rows": response_rows,
        "control_rows": control_rows,
        "selected_portfolio_queue_count": selected_rows,
        "non_l7_numeric_clue_rows": int(numeric_manifest.get("non_l7_numeric_clue_rows", 0) or 0),
        "rank_label_diagnostic_clue_rows": int(numeric_manifest.get("rank_label_diagnostic_clue_rows", 0) or 0),
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_a7ff36_forensic_or_repair": not blockers,
    }
    write_json(RUNTIME / "a7ff35_manifest.json", manifest)
    write_json(RUNTIME / "a7ff35_decision_record.json", manifest)

    report = f"""# CRYPTO A7FF-35 DIVERSIFIED NUMERIC PREFLIGHT

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-35 samples the A7FF-33 family-diversified queue and runs the existing numeric probe adapter. It is a bounded numeric preflight only: no replay, no search, no alpha proof, no shadow/paper/live.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Sample Coverage

{md_table(sample_coverage, 120)}

## Family Materialization Summary

{md_table(family_activity)}

## Selected Portfolio Queue

{md_table(selected)}

## Boundary

```text
numeric probe executed: true, bounded sample only
replay executed: false
search executed: false
May used: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
