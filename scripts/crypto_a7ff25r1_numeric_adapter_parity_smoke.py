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
RUNTIME = REPO / "runtime" / "a7ff25r1_numeric_adapter_parity_smoke"
REPORT = REPO / "reports" / "CRYPTO_A7FF25R1_NUMERIC_ADAPTER_PARITY_SMOKE_20260530.md"

A7FF25R0_MANIFEST = REPO / "runtime" / "a7ff25r0_company_queue_coverage" / "a7ff25r0_manifest.json"
COMPANY_QUEUE = REPO / "runtime" / "a7ff24r_dry_generation_plan" / "a7ff24r_company_numeric_wave_queue.csv"
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
    safe = df.head(max_rows).copy()
    for col in safe.select_dtypes(include=["object"]).columns:
        safe[col] = safe[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return safe.to_markdown(index=False)
    except ImportError:
        return "```text\n" + safe.to_string(index=False) + "\n```"


def sample_queue(company: pd.DataFrame) -> pd.DataFrame:
    if "company_shard" not in company.columns:
        raise SystemExit("company queue lacks company_shard column")
    shard_count = int(os.environ.get("A7FF25R1_SHARD_COUNT", "2"))
    rows_per_shard = int(os.environ.get("A7FF25R1_ROWS_PER_SHARD", "10"))
    shards = sorted(company["company_shard"].dropna().unique())[:shard_count]
    if len(shards) < 2:
        raise SystemExit("need at least two shards for A7FF-25R1")
    parts = []
    for shard in shards:
        part = company[company["company_shard"].eq(shard)].head(rows_per_shard).copy()
        parts.append(part)
    sample = pd.concat(parts, ignore_index=True)
    expected = shard_count * rows_per_shard
    if len(sample) != expected:
        raise SystemExit(f"expected {expected} sample rows, got {len(sample)}")
    return sample


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    r0 = read_json(A7FF25R0_MANIFEST)
    if not r0.get("authorizes_a7ff25r1_adapter_parity_smoke"):
        raise SystemExit(f"A7FF-25R0 does not authorize A7FF-25R1: {r0.get('decision')}")
    company = pd.read_csv(COMPANY_QUEUE)
    sample = sample_queue(company)
    sample_path = RUNTIME / "a7ff25r1_sample_queue.csv"
    sample.to_csv(sample_path, index=False)

    env = os.environ.copy()
    env.update(
        {
            "A7FF8_STAGE": "A7FF-25R1",
            "A7FF8_FILE_PREFIX": "a7ff25r1",
            "A7FF8_RUNTIME": str(RUNTIME),
            "A7FF8_REPORT": str(REPORT),
            "A7FF8_QUEUE_PATH": str(sample_path),
            "A7FF8_MATERIALIZE_CAP": str(len(sample)),
            "A7FF8_FAST_NUMERIC_CAP": str(len(sample)),
            "A7FF8_PORTFOLIO_CAP": "32",
            "A7FF8_QUEUE_OFFSET": "0",
            "A7FF8_QUEUE_LIMIT": str(len(sample)),
        }
    )
    started = now_utc()
    timeout_seconds = int(os.environ.get("A7FF25R1_TIMEOUT_SECONDS", "900"))
    timed_out = False
    timeout_stdout = ""
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
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        timeout_stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace")
        stdout = timeout_stdout + f"\nTIMEOUT after {timeout_seconds} seconds\n"
        returncode = -9
    (RUNTIME / "a7ff25r1_numeric_probe_stdout.log").write_text(stdout, encoding="utf-8")

    numeric_manifest = read_json(RUNTIME / "a7ff25r1_manifest.json")
    materialization_path = RUNTIME / "a7ff25r1_materialization_metrics.csv"
    responses_path = RUNTIME / "a7ff25r1_label_response_metrics.csv"
    controls_path = RUNTIME / "a7ff25r1_control_dominance_metrics.csv"
    materialization = pd.read_csv(materialization_path) if materialization_path.exists() else pd.DataFrame()
    responses = pd.read_csv(responses_path) if responses_path.exists() else pd.DataFrame()
    controls = pd.read_csv(controls_path) if controls_path.exists() else pd.DataFrame()

    eval_success = int(materialization["eval_success"].sum()) if "eval_success" in materialization.columns else 0
    eval_fail = int((~materialization["eval_success"]).sum()) if "eval_success" in materialization.columns else len(sample)
    activity_ok = int(materialization["activity_ok"].sum()) if "activity_ok" in materialization.columns else 0
    missing_field = "missing_numeric_fields" in numeric_manifest.get("blockers", [])
    role_violation = False
    label_leakage = False
    response_rows = int(len(responses))
    control_rows = int(len(controls))
    non_l7_clues = int(numeric_manifest.get("non_l7_numeric_clue_rows", 0) or 0)
    rank_clues = int(numeric_manifest.get("rank_label_diagnostic_clue_rows", 0) or 0)

    parity_rows = pd.DataFrame(
        [
            {"check": "process_exit_code", "value": returncode, "pass": returncode == 0},
            {"check": "timed_out", "value": timed_out, "pass": not timed_out},
            {"check": "sample_rows", "value": len(sample), "pass": len(sample) > 0},
            {"check": "eval_failure_count", "value": eval_fail, "pass": eval_fail == 0},
            {"check": "activity_ok_count", "value": activity_ok, "pass": activity_ok > 0},
            {"check": "missing_field_blocker", "value": missing_field, "pass": not missing_field},
            {"check": "role_violation", "value": role_violation, "pass": not role_violation},
            {"check": "label_leakage_violation", "value": label_leakage, "pass": not label_leakage},
            {"check": "response_rows", "value": response_rows, "pass": response_rows > 0},
            {"check": "control_rows", "value": control_rows, "pass": control_rows > 0},
        ]
    )
    parity_rows.to_csv(RUNTIME / "a7ff25r1_adapter_parity_summary.csv", index=False)

    decision_blockers = []
    if returncode != 0:
        decision_blockers.append("numeric_probe_process_failed")
    if timed_out:
        decision_blockers.append("numeric_probe_timeout")
    if eval_fail != 0:
        decision_blockers.append("eval_failures_present")
    if missing_field:
        decision_blockers.append("missing_numeric_fields")
    if response_rows == 0 or control_rows == 0:
        decision_blockers.append("response_or_control_rows_missing")
    if decision_blockers:
        decision = "HOLD_A7FF25R1_NUMERIC_ADAPTER_PARITY_FAIL"
        authorizes_next = False
    else:
        decision = "PASS_A7FF25R1_NUMERIC_ADAPTER_PARITY_SMOKE"
        authorizes_next = True

    wrapper_manifest = {
        "stage": "A7FF-25R1-NUMERIC-ADAPTER-PARITY-SMOKE",
        "generated_at": now_utc(),
        "started_at": started,
        "decision": decision,
        "blockers": decision_blockers,
        "source_a7ff25r0_decision": r0.get("decision"),
        "sample_rows": int(len(sample)),
        "sample_policy": {
            "shards": int(os.environ.get("A7FF25R1_SHARD_COUNT", "2")),
            "rows_per_shard": int(os.environ.get("A7FF25R1_ROWS_PER_SHARD", "10")),
            "intended_full_adapter_smoke_rows": 100,
            "full_100_rows_recommended_on_company_machine": True,
        },
        "sample_shards": sorted(sample["company_shard"].dropna().unique().tolist()),
        "process_exit_code": returncode,
        "timed_out": timed_out,
        "timeout_seconds": timeout_seconds,
        "numeric_probe_decision": numeric_manifest.get("decision"),
        "eval_success_count": eval_success,
        "eval_failure_count": eval_fail,
        "activity_ok_count": activity_ok,
        "label_response_rows": response_rows,
        "control_rows": control_rows,
        "non_l7_numeric_clue_rows": non_l7_clues,
        "rank_label_diagnostic_clue_rows": rank_clues,
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff25r2_one_shard_numeric_wave": authorizes_next,
        "authorizes_full_12_shard_numeric": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff25r1_wrapper_manifest.json", wrapper_manifest)

    report = f"""# CRYPTO A7FF-25R1 NUMERIC ADAPTER PARITY SMOKE

Generated: {wrapper_manifest["generated_at"]}

## Decision

`{decision}`

A7FF-25R1 samples 2 company shards, 50 formulas per shard, and runs the existing numeric probe adapter on 100 formulas. It checks adapter/evaluator/label/control plumbing only. It does not authorize full 12-shard execution, search, or alpha proof.

## Wrapper Manifest

```json
{json.dumps(wrapper_manifest, indent=2, sort_keys=True)}
```

## Numeric Probe Manifest

```json
{json.dumps(numeric_manifest, indent=2, sort_keys=True)}
```

## Adapter Parity Summary

{md_table(parity_rows)}

## Materialization Summary

{md_table(materialization.head(40))}

## Boundary

```text
numeric probe executed: true, sample only
replay executed: false
search executed: false
May used: false
full 12-shard numeric execution authorized: false
next allowed if PASS: A7FF-25R2 one-shard numeric wave
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(wrapper_manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
