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
RUNTIME = REPO / "runtime" / "a7ff38_focused_replay_taskflow"
REPORT = REPO / "reports" / "CRYPTO_A7FF38_FOCUSED_REPLAY_TASKFLOW_20260530.md"

A7FF37B_MANIFEST = REPO / "runtime" / "a7ff37b_deep_replay_forensic" / "a7ff37b_manifest.json"
A7FF33_COMPANY = REPO / "runtime" / "a7ff33_family_diversified_dry_generation" / "a7ff33_company_numeric_wave_queue.csv"
NUMERIC_PROBE = REPO / "scripts" / "crypto_a7ff8_expanded_numeric_probe.py"

QUEUE_TARGETS = {
    "funding_like|basis_premium_like": 300,
    "regime_state|price_return_like": 180,
    "basis_premium_like|basis_premium_like": 60,
    "open_interest_like|positioning_like": 60,
    "taker_flow_like|open_interest_like": 60,
    "liquidity_like|volatility_like": 60,
}


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


def balanced_take(frame: pd.DataFrame, target: int) -> pd.DataFrame:
    if frame.empty:
        return frame
    motifs = sorted(frame["motif"].dropna().unique().tolist())
    per_motif = max(1, target // max(1, len(motifs)))
    parts = []
    for motif in motifs:
        parts.append(frame[frame["motif"].eq(motif)].head(per_motif).copy())
    out = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    if len(out) < target:
        extra = frame[~frame["blueprint_id"].isin(set(out["blueprint_id"]))].head(target - len(out))
        out = pd.concat([out, extra], ignore_index=True)
    return out.head(target).copy()


def build_focused_queue(company: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for semantic_pair, target in QUEUE_TARGETS.items():
        source = company[company["semantic_pair"].eq(semantic_pair)].copy()
        if semantic_pair == "basis_premium_like|basis_premium_like":
            # Basis root is diagnostic/reference only; keep it small and broad.
            source = source[source["motif"].isin(["safe_div_clip", "zspread", "spread_rank", "sub", "smooth_mul"])]
        parts.append(balanced_take(source, target))
    queue = pd.concat(parts, ignore_index=True).drop_duplicates("blueprint_id")
    queue["a7ff38_role"] = queue["semantic_pair"].map(
        {
            "funding_like|basis_premium_like": "primary_focus_funding_dense",
            "regime_state|price_return_like": "control_warning_focus_regime",
            "basis_premium_like|basis_premium_like": "diagnostic_reference_basis",
            "open_interest_like|positioning_like": "contrast_oi_positioning",
            "taker_flow_like|open_interest_like": "contrast_taker_leverage",
            "liquidity_like|volatility_like": "contrast_liquidity_volatility",
        }
    )
    return queue


def sample_numeric_wave(queue: pd.DataFrame) -> pd.DataFrame:
    max_rows = int(os.environ.get("A7FF38_NUMERIC_SAMPLE_ROWS", "360"))
    parts = []
    for _, group in queue.groupby(["semantic_pair", "motif"], sort=True):
        parts.append(group.head(2).copy())
    sample = pd.concat(parts, ignore_index=True).drop_duplicates("blueprint_id") if parts else pd.DataFrame()
    if len(sample) < max_rows:
        extra = queue[~queue["blueprint_id"].isin(set(sample["blueprint_id"]))].head(max_rows - len(sample))
        sample = pd.concat([sample, extra], ignore_index=True)
    return sample.head(max_rows).copy()


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    f37b = read_json(A7FF37B_MANIFEST)
    if not f37b.get("authorizes_a7ff38_focused_replay_contract"):
        raise SystemExit(f"A7FF-37B does not authorize A7FF-38: {f37b.get('decision')}")

    company = pd.read_csv(A7FF33_COMPANY)
    queue = build_focused_queue(company)
    queue.to_csv(RUNTIME / "a7ff38_focused_replay_queue.csv", index=False)
    sample = sample_numeric_wave(queue)
    sample.to_csv(RUNTIME / "a7ff38_numeric_wave_sample_queue.csv", index=False)

    queue_summary = (
        queue.groupby(["semantic_pair", "a7ff38_role"], dropna=False)
        .agg(
            queue_count=("blueprint_id", "count"),
            motif_count=("motif", "nunique"),
            skeleton_count=("skeleton_key", "nunique"),
            primary_field_count=("primary_field", "nunique"),
            secondary_field_count=("secondary_field", "nunique"),
        )
        .reset_index()
        .sort_values("queue_count", ascending=False)
    )
    queue_summary.to_csv(RUNTIME / "a7ff38_queue_summary.csv", index=False)
    sample_summary = (
        sample.groupby(["semantic_pair", "a7ff38_role"], dropna=False)
        .agg(sample_count=("blueprint_id", "count"), motif_count=("motif", "nunique"), skeleton_count=("skeleton_key", "nunique"))
        .reset_index()
        .sort_values("sample_count", ascending=False)
    )
    sample_summary.to_csv(RUNTIME / "a7ff38_sample_summary.csv", index=False)

    env = os.environ.copy()
    env.update(
        {
            "A7FF8_STAGE": "A7FF-38",
            "A7FF8_FILE_PREFIX": "a7ff38",
            "A7FF8_RUNTIME": str(RUNTIME),
            "A7FF8_REPORT": str(REPORT),
            "A7FF8_QUEUE_PATH": str(sample_path := (RUNTIME / "a7ff38_numeric_wave_sample_queue.csv")),
            "A7FF8_MATERIALIZE_CAP": str(len(sample)),
            "A7FF8_FAST_NUMERIC_CAP": str(len(sample)),
            "A7FF8_PORTFOLIO_CAP": "128",
            "A7FF8_QUEUE_OFFSET": "0",
            "A7FF8_QUEUE_LIMIT": str(len(sample)),
        }
    )
    started = now_utc()
    timeout_seconds = int(os.environ.get("A7FF38_TIMEOUT_SECONDS", "4200"))
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
    (RUNTIME / "a7ff38_numeric_probe_stdout.log").write_text(stdout, encoding="utf-8")

    numeric_manifest = read_json(RUNTIME / "a7ff38_manifest.json")
    materialization = read_csv(RUNTIME / "a7ff38_materialization_metrics.csv")
    selected = read_csv(RUNTIME / "a7ff38_selected_portfolio_queue.csv")
    decisions = read_csv(RUNTIME / "a7ff38_decision_counts.csv")
    family_decisions = read_csv(RUNTIME / "a7ff38_family_decision_summary.csv")
    controls = read_csv(RUNTIME / "a7ff38_control_dominance_metrics.csv")

    eval_fail = int((~materialization["eval_success"]).sum()) if "eval_success" in materialization.columns else len(sample)
    eval_success = int(materialization["eval_success"].sum()) if "eval_success" in materialization.columns else 0
    activity_ok = int(materialization["activity_ok"].sum()) if "activity_ok" in materialization.columns else 0
    non_l7 = int(numeric_manifest.get("non_l7_numeric_clue_rows", 0) or 0)
    rank_l7 = int(numeric_manifest.get("rank_label_diagnostic_clue_rows", 0) or 0)
    selected_count = int(len(selected))
    selected_non_l7 = int(selected["label_family"].ne("L7_ranked_future_return").sum()) if "label_family" in selected.columns else 0
    selected_family_count = int(selected.loc[selected.get("label_family", pd.Series(dtype=str)).ne("L7_ranked_future_return"), "semantic_pair"].nunique()) if not selected.empty and {"label_family", "semantic_pair"}.issubset(selected.columns) else 0

    blockers: list[str] = []
    warnings: list[str] = []
    if returncode != 0:
        blockers.append("numeric_probe_process_failed")
    if timed_out:
        blockers.append("numeric_probe_timeout")
    if eval_fail != 0:
        blockers.append("eval_failures_present")
    if activity_ok == 0:
        blockers.append("no_activity")
    if non_l7 == 0:
        blockers.append("no_non_l7_numeric_clues")
    if selected_non_l7 < 4:
        warnings.append("selected_non_l7_below_4")
    if selected_family_count < 3:
        warnings.append("selected_non_l7_family_count_below_3")
    if rank_l7 > non_l7:
        warnings.append("rank_label_rows_exceed_non_l7_rows")

    decision = "PASS_A7FF38_FOCUSED_REPLAY_TASKFLOW_COMPLETED_NO_SEARCH_AUTH" if not blockers else "HOLD_A7FF38_FOCUSED_REPLAY_TASKFLOW_FAIL"
    manifest = {
        "stage": "A7FF-38",
        "generated_at": now_utc(),
        "started_at": started,
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "source_a7ff37b_decision": f37b.get("decision"),
        "focused_queue_count": int(len(queue)),
        "numeric_sample_count": int(len(sample)),
        "numeric_sample_family_count": int(sample["semantic_pair"].nunique()),
        "numeric_sample_motif_count": int(sample["motif"].nunique()),
        "process_exit_code": returncode,
        "timed_out": timed_out,
        "timeout_seconds": timeout_seconds,
        "numeric_probe_decision": numeric_manifest.get("decision"),
        "eval_success_count": eval_success,
        "eval_failure_count": eval_fail,
        "activity_ok_count": activity_ok,
        "non_l7_numeric_clue_rows": non_l7,
        "rank_label_diagnostic_clue_rows": rank_l7,
        "selected_portfolio_queue_count": selected_count,
        "selected_non_l7_count": selected_non_l7,
        "selected_non_l7_family_count": selected_family_count,
        "executes_generation": False,
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff39_focused_forensic": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff38_manifest.json", manifest)
    write_json(RUNTIME / "a7ff38_decision_record.json", manifest)

    report = f"""# CRYPTO A7FF-38 FOCUSED REPLAY TASKFLOW

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-38 builds a 720-row focused replay queue and runs a 360-row numeric wave sample. It expands the funding-dense and regime follow-up while preserving OI/taker/liquidity contrast families. It is not formula search or alpha proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Focused Queue Summary

{md_table(queue_summary)}

## Numeric Sample Summary

{md_table(sample_summary)}

## Selected Portfolio Queue

{md_table(selected)}

## Decision Counts

{md_table(decisions)}

## Family Decisions

{md_table(family_decisions)}

## Control Metrics Sample

{md_table(controls)}

## Boundary

```text
focused queue built: true
numeric probe executed: true
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
