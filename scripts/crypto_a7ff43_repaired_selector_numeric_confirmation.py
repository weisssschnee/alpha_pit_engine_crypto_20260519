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
RUNTIME = REPO / "runtime" / "a7ff43_repaired_selector_numeric_confirmation"
REPORT = REPO / "reports" / "CRYPTO_A7FF43_REPAIRED_SELECTOR_NUMERIC_CONFIRMATION_20260531.md"

A7FFR8_MANIFEST = REPO / "runtime" / "a7ffr8_selector_objective_rewrite" / "a7ffr8_manifest.json"
A7FFR8_REPAIRED = REPO / "runtime" / "a7ffr8_selector_objective_rewrite" / "a7ffr8c_repaired_selected_queue.csv"
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


def num(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series([float("nan")] * len(df), index=df.index)
    return pd.to_numeric(df[col], errors="coerce")


def run_numeric(queue: pd.DataFrame) -> tuple[int, bool]:
    queue_path = RUNTIME / "a7ff43_repaired_selector_numeric_queue.csv"
    queue.to_csv(queue_path, index=False)
    env = os.environ.copy()
    env.update(
        {
            "A7FF8_STAGE": "A7FF-43",
            "A7FF8_FILE_PREFIX": "a7ff43",
            "A7FF8_RUNTIME": str(RUNTIME),
            "A7FF8_REPORT": str(REPORT),
            "A7FF8_QUEUE_PATH": str(queue_path),
            "A7FF8_MATERIALIZE_CAP": str(len(queue)),
            "A7FF8_FAST_NUMERIC_CAP": str(len(queue)),
            "A7FF8_PORTFOLIO_CAP": str(max(32, len(queue) * 5)),
            "A7FF8_QUEUE_OFFSET": "0",
            "A7FF8_QUEUE_LIMIT": str(len(queue)),
        }
    )
    timeout_seconds = int(os.environ.get("A7FF43_TIMEOUT_SECONDS", "3600"))
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
    (RUNTIME / "a7ff43_numeric_probe_stdout.log").write_text(stdout, encoding="utf-8")
    return returncode, timed_out


def normalize_key(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["label_horizon_h"] = num(out, "label_horizon_h").astype("Int64").astype(str)
    out["blueprint_id"] = out["blueprint_id"].astype(str)
    out["label_family"] = out["label_family"].astype(str)
    return out


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    r8 = read_json(A7FFR8_MANIFEST)
    if not r8.get("authorizes_a7ff43_numeric_confirmation"):
        raise SystemExit(f"A7FF-R8 does not authorize A7FF-43: {r8.get('decision')}")

    repaired = read_csv(A7FFR8_REPAIRED)
    if repaired.empty:
        raise SystemExit("R8 repaired selected queue is empty")
    target = normalize_key(repaired)
    formula_queue = repaired.drop_duplicates("blueprint_id").copy()
    formula_queue.to_csv(RUNTIME / "a7ff43_unique_formula_queue.csv", index=False)

    started = now_utc()
    returncode, timed_out = run_numeric(formula_queue)
    numeric_manifest = read_json(RUNTIME / "a7ff43_manifest.json")
    metrics = normalize_key(read_csv(RUNTIME / "a7ff43_label_response_metrics.csv"))
    materialization = read_csv(RUNTIME / "a7ff43_materialization_metrics.csv")
    probe_selected = read_csv(RUNTIME / "a7ff43_selected_portfolio_queue.csv")

    key_cols = ["blueprint_id", "label_family", "label_horizon_h"]
    confirmed = target.merge(
        metrics,
        on=key_cols,
        how="left",
        suffixes=("_r8", "_confirmed"),
        indicator=True,
    )
    confirmed["confirmed_row_found"] = confirmed["_merge"].eq("both")
    confirmed["confirmed_decision"] = confirmed["decision_confirmed"].astype(str)
    confirmed["confirmed_control_ratio"] = num(confirmed, "control_ratio_premay_max_confirmed")
    confirmed["confirmed_non_l7"] = ~confirmed["label_family"].astype(str).eq("L7_ranked_future_return")
    confirmed["confirmed_control_strict"] = confirmed["confirmed_control_ratio"].lt(0.80)
    confirmed["confirmed_numeric_clue"] = confirmed["confirmed_decision"].str.contains("NUMERIC_CLUE", regex=False)
    confirmed["confirmed_ok"] = (
        confirmed["confirmed_row_found"]
        & confirmed["confirmed_non_l7"]
        & confirmed["confirmed_control_strict"]
        & confirmed["confirmed_numeric_clue"]
    )
    confirmed.to_csv(RUNTIME / "a7ff43_confirmed_repaired_rows.csv", index=False)

    confirmed_ok = confirmed[confirmed["confirmed_ok"]].copy()
    family_confirmation = (
        confirmed.groupby("semantic_pair_r8", dropna=False)
        .agg(
            target_rows=("blueprint_id", "count"),
            confirmed_rows=("confirmed_ok", "sum"),
            found_rows=("confirmed_row_found", "sum"),
            max_confirmed_control_ratio=("confirmed_control_ratio", "max"),
            median_confirmed_control_ratio=("confirmed_control_ratio", "median"),
            target_motifs=("motif_r8", "nunique"),
        )
        .reset_index()
        .rename(columns={"semantic_pair_r8": "semantic_pair"})
        .sort_values("confirmed_rows", ascending=False)
    )
    family_confirmation.to_csv(RUNTIME / "a7ff43_family_confirmation.csv", index=False)

    if not probe_selected.empty:
        probe_selected["control_ratio_premay_max"] = num(probe_selected, "control_ratio_premay_max")
        probe_selected["is_non_l7"] = ~probe_selected["label_family"].astype(str).eq("L7_ranked_future_return")
        probe_selected["is_control_strict"] = probe_selected["control_ratio_premay_max"].lt(0.80)
        probe_selected["a7ff43_probe_role"] = "probe_selected_other"
        probe_selected.loc[probe_selected["is_non_l7"] & probe_selected["is_control_strict"], "a7ff43_probe_role"] = "probe_selected_control_strict_non_l7"
    probe_selected.to_csv(RUNTIME / "a7ff43_probe_selected_forensic.csv", index=False)

    eval_success_count = int(materialization["eval_success"].sum()) if "eval_success" in materialization.columns else 0
    eval_failure_count = int((~materialization["eval_success"]).sum()) if "eval_success" in materialization.columns else 0
    activity_ok_count = int(materialization["activity_ok"].sum()) if "activity_ok" in materialization.columns else 0
    confirmed_family_count = int(confirmed_ok["semantic_pair_r8"].nunique()) if not confirmed_ok.empty else 0
    confirmed_top_share = (
        float(confirmed_ok["semantic_pair_r8"].value_counts().iloc[0] / len(confirmed_ok)) if not confirmed_ok.empty else 0.0
    )
    confirmed_max_control = float(confirmed_ok["confirmed_control_ratio"].max()) if not confirmed_ok.empty else None
    confirmed_median_control = float(confirmed_ok["confirmed_control_ratio"].median()) if not confirmed_ok.empty else None

    blockers: list[str] = []
    warnings: list[str] = []
    if returncode != 0:
        blockers.append("numeric_probe_process_failed")
    if timed_out:
        blockers.append("numeric_probe_timeout")
    if eval_failure_count != 0:
        blockers.append("eval_failures_present")
    if len(confirmed_ok) < 6:
        blockers.append("confirmed_control_strict_non_l7_rows_below_6")
    if confirmed_family_count < 2:
        blockers.append("confirmed_family_count_below_2")
    if confirmed_max_control is not None and confirmed_max_control >= 0.80:
        blockers.append("confirmed_control_ratio_max_ge_0p80")
    if confirmed_top_share > 0.60:
        warnings.append("confirmed_top_family_share_above_0p60")
    if confirmed_family_count >= 3:
        warnings.append("confirmed_retains_3_families")

    decision = (
        "PASS_A7FF43_REPAIRED_SELECTOR_NUMERIC_CONFIRMED_READY_FOR_DEEP_FORENSIC_NO_SEARCH_AUTH"
        if not blockers
        else "HOLD_A7FF43_REPAIRED_SELECTOR_NUMERIC_CONFIRMATION_FAILED"
    )
    manifest = {
        "stage": "A7FF-43",
        "generated_at": now_utc(),
        "started_at": started,
        "decision": decision,
        "source_a7ffr8_decision": r8.get("decision"),
        "blockers": blockers,
        "warnings": warnings,
        "target_rows": int(len(target)),
        "unique_formula_count": int(len(formula_queue)),
        "eval_success_count": eval_success_count,
        "eval_failure_count": eval_failure_count,
        "activity_ok_count": activity_ok_count,
        "confirmed_control_strict_non_l7_rows": int(len(confirmed_ok)),
        "confirmed_family_count": confirmed_family_count,
        "confirmed_top_family_share": confirmed_top_share,
        "confirmed_control_ratio_max": confirmed_max_control,
        "confirmed_control_ratio_median": confirmed_median_control,
        "probe_selected_count": int(len(probe_selected)),
        "probe_selected_control_strict_non_l7_count": int((probe_selected.get("a7ff43_probe_role", pd.Series(dtype=str)) == "probe_selected_control_strict_non_l7").sum()) if not probe_selected.empty else 0,
        "process_exit_code": int(returncode),
        "timed_out": bool(timed_out),
        "numeric_probe_decision": numeric_manifest.get("decision"),
        "executes_generation": False,
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff44_deep_forensic": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff43_manifest.json", manifest)
    write_json(RUNTIME / "a7ff43_decision_record.json", manifest)

    next_actions = pd.DataFrame(
        [
            {
                "route": "A7FF-44_deep_forensic",
                "status": "authorized" if not blockers else "not_authorized",
                "reason": "requires repaired selector rows to remain numeric-confirmed, non-L7, control-strict, and multi-family",
            },
            {
                "route": "A7FF-R9_selector_repair_failure_audit",
                "status": "not_needed_if_pass" if not blockers else "recommended_if_hold",
                "reason": "use only if repaired rows fail numeric confirmation",
            },
            {"route": "formula_search", "status": "blocked", "reason": "A7FF-43 is numeric confirmation only"},
        ]
    )
    next_actions.to_csv(RUNTIME / "a7ff43_next_actions.csv", index=False)

    report = f"""# CRYPTO A7FF-43 REPAIRED SELECTOR NUMERIC CONFIRMATION

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-43 re-runs numeric confirmation for the A7FF-R8 repaired selector queue. It validates the exact repaired rows by blueprint, label family, and horizon. It does not execute search or alpha proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Family Confirmation

{md_table(family_confirmation)}

## Confirmed Repaired Rows

{md_table(confirmed)}

## Probe Selected Forensic

{md_table(probe_selected)}

## Next Actions

{md_table(next_actions)}

## Boundary

```text
numeric probe executed: true
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
