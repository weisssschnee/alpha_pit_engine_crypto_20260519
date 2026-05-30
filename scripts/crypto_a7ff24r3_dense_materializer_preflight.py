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
RUNTIME = REPO / "runtime" / "a7ff24r3_dense_materializer_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7FF24R3_DENSE_MATERIALIZER_PREFLIGHT_20260530.md"

A7FF24R2_MANIFEST = REPO / "runtime" / "a7ff24r2_repaired_company_queue" / "a7ff24r2_manifest.json"
REPAIRED_QUEUE = REPO / "runtime" / "a7ff24r2_repaired_company_queue" / "a7ff24r2_company_numeric_wave_queue.csv"
NUMERIC_PROBE = REPO / "scripts" / "crypto_a7ff8_expanded_numeric_probe.py"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


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


def sample_dense_tail(queue: pd.DataFrame) -> pd.DataFrame:
    required = {"company_shard", "expression", "blueprint_id"}
    missing = sorted(required - set(queue.columns))
    if missing:
        raise SystemExit(f"repaired queue missing required columns: {missing}")
    shards = [x.strip() for x in os.environ.get("A7FF24R3_TAIL_SHARDS", "shard_08,shard_09,shard_10,shard_11").split(",") if x.strip()]
    rows_per_shard = int(os.environ.get("A7FF24R3_ROWS_PER_SHARD", "25"))
    dense = queue[
        queue["company_shard"].isin(shards)
        & queue["expression"].astype(str).str.contains("funding_rate_state_last_ffill_8h", regex=False)
    ].copy()
    parts = []
    for shard in shards:
        part = dense[dense["company_shard"].eq(shard)].head(rows_per_shard).copy()
        if len(part) != rows_per_shard:
            raise SystemExit(f"expected {rows_per_shard} dense rows for {shard}, got {len(part)}")
        parts.append(part)
    sample = pd.concat(parts, ignore_index=True)
    if sample["blueprint_id"].duplicated().any():
        raise SystemExit("dense tail sample has duplicate blueprint_id")
    return sample


def audit_repaired_queue(queue: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    expr = queue["expression"].astype(str)
    raw_global = expr.str.contains(r"\bfunding_rate\b", regex=True) & ~expr.str.contains("funding_rate_state", regex=False)
    dense_global = expr.str.contains("funding_rate_state_last_ffill_8h", regex=False)
    shard_audit = (
        queue.assign(raw_funding_rate_global=raw_global, dense_funding_state=dense_global)
        .groupby("company_shard", dropna=False)
        .agg(
            row_count=("blueprint_id", "count"),
            raw_funding_rate_rows=("raw_funding_rate_global", "sum"),
            dense_funding_rows=("dense_funding_state", "sum"),
            semantic_pairs=("semantic_pair", "nunique"),
            motifs=("motif", "nunique"),
        )
        .reset_index()
        .sort_values("company_shard")
    )
    summary = {
        "queue_rows": int(len(queue)),
        "raw_funding_rate_global_rows": int(raw_global.sum()),
        "dense_funding_state_rows": int(dense_global.sum()),
        "dense_tail_rows": int((dense_global & queue["company_shard"].isin(["shard_08", "shard_09", "shard_10", "shard_11"])).sum()),
        "raw_funding_rate_tail_rows": int((raw_global & queue["company_shard"].isin(["shard_08", "shard_09", "shard_10", "shard_11"])).sum()),
    }
    return shard_audit, summary


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    r2 = read_json(A7FF24R2_MANIFEST)
    if not r2.get("authorizes_dense_materializer_preflight"):
        raise SystemExit(f"A7FF-24R2 does not authorize A7FF-24R3: {r2.get('decision')}")

    queue = pd.read_csv(REPAIRED_QUEUE)
    shard_audit, queue_summary = audit_repaired_queue(queue)
    sample = sample_dense_tail(queue)
    sample_path = RUNTIME / "a7ff24r3_dense_tail_sample_queue.csv"
    sample.to_csv(sample_path, index=False)
    shard_audit.to_csv(RUNTIME / "a7ff24r3_repaired_queue_shard_audit.csv", index=False)

    env = os.environ.copy()
    env.update(
        {
            "A7FF8_STAGE": "A7FF-24R3",
            "A7FF8_FILE_PREFIX": "a7ff24r3",
            "A7FF8_RUNTIME": str(RUNTIME),
            "A7FF8_REPORT": str(REPORT),
            "A7FF8_QUEUE_PATH": str(sample_path),
            "A7FF8_MATERIALIZE_CAP": str(len(sample)),
            "A7FF8_FAST_NUMERIC_CAP": str(len(sample)),
            "A7FF8_PORTFOLIO_CAP": "64",
            "A7FF8_QUEUE_OFFSET": "0",
            "A7FF8_QUEUE_LIMIT": str(len(sample)),
        }
    )

    started = now_utc()
    timeout_seconds = int(os.environ.get("A7FF24R3_TIMEOUT_SECONDS", "1800"))
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
    (RUNTIME / "a7ff24r3_numeric_probe_stdout.log").write_text(stdout, encoding="utf-8")

    numeric_manifest = read_json(RUNTIME / "a7ff24r3_manifest.json")
    materialization_path = RUNTIME / "a7ff24r3_materialization_metrics.csv"
    responses_path = RUNTIME / "a7ff24r3_label_response_metrics.csv"
    controls_path = RUNTIME / "a7ff24r3_control_dominance_metrics.csv"
    materialization = pd.read_csv(materialization_path) if materialization_path.exists() else pd.DataFrame()
    responses = pd.read_csv(responses_path) if responses_path.exists() else pd.DataFrame()
    controls = pd.read_csv(controls_path) if controls_path.exists() else pd.DataFrame()

    eval_fail = int((~materialization["eval_success"]).sum()) if "eval_success" in materialization.columns else len(sample)
    eval_success = int(materialization["eval_success"].sum()) if "eval_success" in materialization.columns else 0
    activity_ok = int(materialization["activity_ok"].sum()) if "activity_ok" in materialization.columns else 0
    sample_ids = set(sample["blueprint_id"].astype(str))
    tail_materialization = materialization[materialization["blueprint_id"].astype(str).isin(sample_ids)].copy() if "blueprint_id" in materialization.columns else pd.DataFrame()
    tail_activity_ok = int(tail_materialization["activity_ok"].sum()) if "activity_ok" in tail_materialization.columns else 0
    missing_field = "missing_numeric_fields" in numeric_manifest.get("blockers", [])
    response_rows = int(len(responses))
    control_rows = int(len(controls))

    blockers: list[str] = []
    if returncode != 0:
        blockers.append("numeric_probe_process_failed")
    if timed_out:
        blockers.append("numeric_probe_timeout")
    if eval_fail != 0:
        blockers.append("eval_failures_present")
    if missing_field:
        blockers.append("missing_numeric_fields")
    if tail_activity_ok == 0:
        blockers.append("dense_tail_no_activity")
    if response_rows == 0 or control_rows == 0:
        blockers.append("response_or_control_rows_missing")
    if queue_summary["raw_funding_rate_tail_rows"] != 0:
        blockers.append("tail_raw_funding_rate_still_present")

    warnings: list[str] = []
    if queue_summary["raw_funding_rate_global_rows"] > 0:
        warnings.append("preserved_healthy_queue_still_has_raw_funding_rate_rows")

    decision = (
        "PASS_A7FF24R3_DENSE_MATERIALIZER_PREFLIGHT_READY_FOR_REPAIRED_QUEUE_NUMERIC_WAVE_NO_SEARCH_AUTH"
        if not blockers
        else "HOLD_A7FF24R3_DENSE_MATERIALIZER_PREFLIGHT_FAIL"
    )
    parity = pd.DataFrame(
        [
            {"check": "process_exit_code", "value": returncode, "pass": returncode == 0},
            {"check": "timed_out", "value": timed_out, "pass": not timed_out},
            {"check": "sample_rows", "value": len(sample), "pass": len(sample) > 0},
            {"check": "eval_failure_count", "value": eval_fail, "pass": eval_fail == 0},
            {"check": "activity_ok_count", "value": activity_ok, "pass": activity_ok > 0},
            {"check": "dense_tail_activity_ok_count", "value": tail_activity_ok, "pass": tail_activity_ok > 0},
            {"check": "missing_field_blocker", "value": missing_field, "pass": not missing_field},
            {"check": "response_rows", "value": response_rows, "pass": response_rows > 0},
            {"check": "control_rows", "value": control_rows, "pass": control_rows > 0},
            {"check": "tail_raw_funding_rate_rows", "value": queue_summary["raw_funding_rate_tail_rows"], "pass": queue_summary["raw_funding_rate_tail_rows"] == 0},
            {"check": "global_raw_funding_rate_rows", "value": queue_summary["raw_funding_rate_global_rows"], "pass": queue_summary["raw_funding_rate_global_rows"] == 0},
        ]
    )
    parity.to_csv(RUNTIME / "a7ff24r3_dense_materializer_parity_summary.csv", index=False)
    tail_materialization.to_csv(RUNTIME / "a7ff24r3_dense_tail_materialization_metrics.csv", index=False)
    pd.DataFrame([queue_summary]).to_csv(RUNTIME / "a7ff24r3_repaired_queue_summary.csv", index=False)

    manifest = {
        "stage": "A7FF-24R3",
        "generated_at": now_utc(),
        "started_at": started,
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "source_a7ff24r2_decision": r2.get("decision"),
        "sample_rows": int(len(sample)),
        "sample_policy": {
            "tail_shards": sorted(sample["company_shard"].dropna().unique().tolist()),
            "rows_per_tail_shard": int(os.environ.get("A7FF24R3_ROWS_PER_SHARD", "25")),
        },
        "process_exit_code": returncode,
        "timed_out": timed_out,
        "timeout_seconds": timeout_seconds,
        "numeric_probe_decision": numeric_manifest.get("decision"),
        "eval_success_count": eval_success,
        "eval_failure_count": eval_fail,
        "activity_ok_count": activity_ok,
        "dense_tail_activity_ok_count": tail_activity_ok,
        "label_response_rows": response_rows,
        "control_rows": control_rows,
        "non_l7_numeric_clue_rows": int(numeric_manifest.get("non_l7_numeric_clue_rows", 0) or 0),
        "rank_label_diagnostic_clue_rows": int(numeric_manifest.get("rank_label_diagnostic_clue_rows", 0) or 0),
        **queue_summary,
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_repaired_queue_numeric_wave_contract": not blockers,
        "authorizes_full_12_shard_numeric": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff24r3_manifest.json", manifest)
    write_json(RUNTIME / "a7ff24r3_decision_record.json", manifest)

    report = f"""# CRYPTO A7FF-24R3 DENSE MATERIALIZER PREFLIGHT

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-24R3 samples repaired dense funding tail rows from A7FF-24R2 and runs the existing numeric probe adapter. It validates materialization/activity/label-control plumbing only. It does not execute formula search, alpha proof, shadow, paper, or live.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Dense Materializer Parity Summary

{md_table(parity)}

## Repaired Queue Shard Audit

{md_table(shard_audit)}

## Dense Tail Materialization Sample

{md_table(tail_materialization.head(40))}

## Boundary

```text
numeric probe executed: true, bounded dense-tail sample only
replay executed: false
search executed: false
May used: false
full 12-shard numeric execution authorized: false
next if PASS: repaired-queue numeric wave contract / A7FF-32 family diversification contract
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
