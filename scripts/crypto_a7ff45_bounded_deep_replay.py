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
RUNTIME = REPO / "runtime" / "a7ff45_bounded_deep_replay"
REPORT = REPO / "reports" / "CRYPTO_A7FF45_BOUNDED_DEEP_REPLAY_20260531.md"

A7FFR9_MANIFEST = REPO / "runtime" / "a7ffr9_reference_regime_repair" / "a7ffr9_manifest.json"
A7FFR9_QUEUE = REPO / "runtime" / "a7ffr9_reference_regime_repair" / "a7ffr9_repaired_candidate_queue.csv"
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


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def md_table(df: pd.DataFrame, max_rows: int = 100) -> str:
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


def normalize_key(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["blueprint_id"] = out["blueprint_id"].astype(str)
    out["label_family"] = out["label_family"].astype(str)
    out["label_horizon_h"] = num(out, "label_horizon_h").astype("Int64").astype(str)
    return out


def run_numeric(queue: pd.DataFrame) -> tuple[int, bool]:
    queue_path = RUNTIME / "a7ff45_bounded_deep_replay_queue.csv"
    queue.to_csv(queue_path, index=False)
    env = os.environ.copy()
    env.update(
        {
            "A7FF8_STAGE": "A7FF-45",
            "A7FF8_FILE_PREFIX": "a7ff45",
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
    timeout_seconds = int(os.environ.get("A7FF45_TIMEOUT_SECONDS", "3600"))
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
    (RUNTIME / "a7ff45_numeric_probe_stdout.log").write_text(stdout, encoding="utf-8")
    return returncode, timed_out


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    r9 = read_json(A7FFR9_MANIFEST)
    if not r9.get("authorizes_a7ff45_bounded_deep_replay"):
        raise SystemExit(f"A7FF-R9 does not authorize A7FF-45: {r9.get('decision')}")

    target = normalize_key(read_csv(A7FFR9_QUEUE))
    if target.empty:
        raise SystemExit("A7FF-R9 repaired queue is empty")
    formula_queue = target.drop_duplicates("blueprint_id").copy()
    formula_queue.to_csv(RUNTIME / "a7ff45_unique_formula_queue.csv", index=False)

    started = now_utc()
    returncode, timed_out = run_numeric(formula_queue)
    numeric_manifest = read_json(RUNTIME / "a7ff45_manifest.json")
    metrics = normalize_key(read_csv(RUNTIME / "a7ff45_label_response_metrics.csv"))
    materialization = read_csv(RUNTIME / "a7ff45_materialization_metrics.csv")
    selected = read_csv(RUNTIME / "a7ff45_selected_portfolio_queue.csv")

    key_cols = ["blueprint_id", "label_family", "label_horizon_h"]
    confirmed = target.merge(
        metrics,
        on=key_cols,
        how="left",
        suffixes=("_r9", "_confirmed"),
        indicator=True,
    )
    confirmed["semantic_pair"] = confirmed.get("semantic_pair_r9", confirmed.get("semantic_pair_confirmed", ""))
    confirmed["motif"] = confirmed.get("motif_r9", confirmed.get("motif_confirmed", ""))
    confirmed["confirmed_row_found"] = confirmed["_merge"].eq("both")
    confirmed["confirmed_decision"] = confirmed["decision"].astype(str)
    confirmed["confirmed_control_ratio"] = num(confirmed, "control_ratio_premay_max_confirmed")
    confirmed["confirmed_non_l7"] = ~confirmed["label_family"].astype(str).eq("L7_ranked_future_return")
    confirmed["confirmed_control_strict"] = confirmed["confirmed_control_ratio"].lt(0.80)
    confirmed["confirmed_numeric_clue"] = confirmed["confirmed_decision"].str.contains("NUMERIC_CLUE", regex=False)
    confirmed["confirmed_cost10_positive"] = num(confirmed, "cost10_recent_oriented_confirmed").gt(0)
    confirmed["confirmed_lag_positive"] = num(confirmed, "one_bar_lag_recent_oriented_confirmed").gt(0)
    confirmed["confirmed_robust_positive"] = num(confirmed, "robust_min_tstat_floor_confirmed").gt(0)
    confirmed["confirmed_ok"] = (
        confirmed["confirmed_row_found"]
        & confirmed["confirmed_non_l7"]
        & confirmed["confirmed_control_strict"]
        & confirmed["confirmed_numeric_clue"]
        & confirmed["confirmed_cost10_positive"]
        & confirmed["confirmed_lag_positive"]
        & confirmed["confirmed_robust_positive"]
    )
    confirmed.to_csv(RUNTIME / "a7ff45_confirmed_bounded_rows.csv", index=False)

    ok = confirmed.loc[confirmed["confirmed_ok"]].copy()
    family_confirmation = (
        confirmed.groupby("semantic_pair", dropna=False)
        .agg(
            target_rows=("blueprint_id", "count"),
            confirmed_rows=("confirmed_ok", "sum"),
            found_rows=("confirmed_row_found", "sum"),
            motifs=("motif", "nunique"),
            labels=("label_family", "nunique"),
            max_control_ratio=("confirmed_control_ratio", "max"),
            median_control_ratio=("confirmed_control_ratio", "median"),
            min_cost10=("cost10_recent_oriented_confirmed", "min"),
            min_robust_floor=("robust_min_tstat_floor_confirmed", "min"),
        )
        .reset_index()
        .sort_values("confirmed_rows", ascending=False)
    )
    family_confirmation.to_csv(RUNTIME / "a7ff45_family_confirmation.csv", index=False)

    if not selected.empty:
        selected["control_ratio_premay_max"] = num(selected, "control_ratio_premay_max")
        selected["is_non_l7"] = ~selected["label_family"].astype(str).eq("L7_ranked_future_return")
        selected["is_control_strict"] = selected["control_ratio_premay_max"].lt(0.80)
        selected["a7ff45_probe_role"] = "probe_selected_other"
        selected.loc[selected["is_non_l7"] & selected["is_control_strict"], "a7ff45_probe_role"] = "probe_selected_control_strict_non_l7"
    selected.to_csv(RUNTIME / "a7ff45_probe_selected_forensic.csv", index=False)

    eval_success_count = int(materialization["eval_success"].sum()) if "eval_success" in materialization.columns else 0
    eval_failure_count = int((~materialization["eval_success"]).sum()) if "eval_success" in materialization.columns else 0
    activity_ok_count = int(materialization["activity_ok"].sum()) if "activity_ok" in materialization.columns else 0
    ok_family_count = int(ok["semantic_pair"].nunique()) if not ok.empty else 0
    ok_top_share = float(ok["semantic_pair"].value_counts(normalize=True).iloc[0]) if len(ok) else 0.0
    ok_max_control = float(ok["confirmed_control_ratio"].max()) if len(ok) else None
    ok_median_control = float(ok["confirmed_control_ratio"].median()) if len(ok) else None

    blockers: list[str] = []
    warnings: list[str] = []
    if returncode != 0:
        blockers.append("numeric_probe_process_failed")
    if timed_out:
        blockers.append("numeric_probe_timeout")
    if eval_failure_count != 0:
        blockers.append("eval_failures_present")
    if len(ok) < 6:
        blockers.append("confirmed_bounded_rows_below_6")
    if ok_family_count < 2:
        blockers.append("confirmed_family_count_below_2")
    if ok_top_share > 0.75:
        blockers.append("confirmed_top_family_share_above_0p75")
    if ok_max_control is not None and ok_max_control >= 0.80:
        blockers.append("confirmed_control_ratio_max_ge_0p80")
    if ok_top_share > 0.60:
        warnings.append("confirmed_top_family_share_above_0p60")

    decision = (
        "PASS_A7FF45_BOUNDED_DEEP_REPLAY_CONFIRMED_READY_FOR_A7FF46_NO_SEARCH_AUTH"
        if not blockers
        else "HOLD_A7FF45_BOUNDED_DEEP_REPLAY_FAILED"
    )
    manifest = {
        "stage": "A7FF-45",
        "generated_at": now_utc(),
        "started_at": started,
        "decision": decision,
        "source_a7ffr9_decision": r9.get("decision"),
        "blockers": blockers,
        "warnings": warnings,
        "target_rows": int(len(target)),
        "unique_formula_count": int(len(formula_queue)),
        "eval_success_count": eval_success_count,
        "eval_failure_count": eval_failure_count,
        "activity_ok_count": activity_ok_count,
        "confirmed_bounded_rows": int(len(ok)),
        "confirmed_family_count": ok_family_count,
        "confirmed_top_family_share": ok_top_share,
        "confirmed_control_ratio_max": ok_max_control,
        "confirmed_control_ratio_median": ok_median_control,
        "numeric_probe_decision": numeric_manifest.get("decision"),
        "process_exit_code": int(returncode),
        "timed_out": bool(timed_out),
        "executes_generation": False,
        "executes_numeric_probe": True,
        "executes_replay": True,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff46_candidate_freeze": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff45_manifest.json", manifest)
    write_json(RUNTIME / "a7ff45_decision_record.json", manifest)

    next_actions = pd.DataFrame(
        [
            {
                "route": "A7FF-46_candidate_freeze",
                "status": "authorized" if not blockers else "not_authorized",
                "reason": "requires bounded replay to keep at least 6 rows, 2 families, control strict, cost/lag/robust positive",
            },
            {
                "route": "formula_search",
                "status": "blocked",
                "reason": "A7FF-45 is bounded replay only and does not authorize generation or search",
            },
        ]
    )
    next_actions.to_csv(RUNTIME / "a7ff45_next_actions.csv", index=False)

    report = f"""# CRYPTO A7FF-45 BOUNDED DEEP REPLAY

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-45 replays only the 7-row A7FF-R9 repaired queue through the numeric adapter. It does not generate formulas or run search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Family Confirmation

{md_table(family_confirmation)}

## Confirmed Bounded Rows

{md_table(confirmed)}

## Probe Selected Forensic

{md_table(selected)}

## Next Actions

{md_table(next_actions)}

## Boundary

```text
generation executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
