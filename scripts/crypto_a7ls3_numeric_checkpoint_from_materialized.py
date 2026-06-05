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
NUMERIC_PROBE = REPO / "scripts" / "crypto_a7ff8_expanded_numeric_probe.py"
LS2 = REPO / "runtime" / "a7ls2_sharded_materialization_wave"
RUNTIME = REPO / "runtime" / "a7ls3_numeric_checkpoint_from_materialized"
REPORT = REPO / "reports" / "CRYPTO_A7LS3_NUMERIC_CHECKPOINT_FROM_MATERIALIZED_20260605.md"


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


def build_queue(metrics: pd.DataFrame, target: int) -> pd.DataFrame:
    ok = metrics[metrics["activity_ok"].astype(str).str.lower().isin({"true", "1"})].copy()
    if ok.empty:
        return ok
    ok["finite_share"] = pd.to_numeric(ok["finite_share"], errors="coerce").fillna(0)
    ok["nonzero_share"] = pd.to_numeric(ok["nonzero_share"], errors="coerce").fillna(0)
    ok["materialization_score"] = ok["finite_share"].clip(0, 1) * 0.6 + ok["nonzero_share"].clip(0, 1) * 0.4
    ok = ok.sort_values(["a7ls_arm", "materialization_score", "semantic_pair", "motif"], ascending=[True, False, True, True])

    per_arm = max(1, target // max(1, ok["a7ls_arm"].nunique()))
    selected_frames = []
    for arm, group in ok.groupby("a7ls_arm", sort=True):
        # Keep C if it is small; do not over-demand weak arm.
        take = min(per_arm, len(group))
        if arm == "A7LS_C":
            take = min(len(group), max(48, min(per_arm, len(group))))
        selected_frames.append(diversified_take(group, take))
    selected = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    if len(selected) < target:
        used = set(selected["blueprint_id"].astype(str)) if not selected.empty else set()
        extra = ok[~ok["blueprint_id"].astype(str).isin(used)].copy()
        selected = pd.concat([selected, diversified_take(extra, target - len(selected))], ignore_index=True)
    selected = selected.head(target).copy()
    selected["a7input_queue"] = "a7ls3_materialized_numeric_checkpoint"
    selected["core58_queue"] = "a7ls3_materialized_numeric_checkpoint"
    selected["company_shard"] = [f"a7ls3_numeric_s{i // 256:03d}" for i in range(len(selected))]
    return selected


def diversified_take(df: pd.DataFrame, limit: int) -> pd.DataFrame:
    if df.empty or limit <= 0:
        return df.head(0)
    selected = []
    seen_sem: dict[str, int] = {}
    seen_motif: dict[str, int] = {}
    seen_skel: dict[str, int] = {}
    sem_cap = max(8, int(limit * 0.25))
    motif_cap = max(8, int(limit * 0.25))
    skel_cap = max(3, int(limit * 0.08))
    for _, row in df.iterrows():
        sem = str(row.get("semantic_pair", ""))
        motif = str(row.get("motif", ""))
        skel = str(row.get("skeleton_key", ""))
        if seen_sem.get(sem, 0) >= sem_cap:
            continue
        if seen_motif.get(motif, 0) >= motif_cap:
            continue
        if seen_skel.get(skel, 0) >= skel_cap:
            continue
        selected.append(row)
        seen_sem[sem] = seen_sem.get(sem, 0) + 1
        seen_motif[motif] = seen_motif.get(motif, 0) + 1
        seen_skel[skel] = seen_skel.get(skel, 0) + 1
        if len(selected) >= limit:
            break
    if len(selected) < limit:
        used = {str(r.get("blueprint_id")) for r in selected}
        for _, row in df.iterrows():
            if str(row.get("blueprint_id")) in used:
                continue
            selected.append(row)
            used.add(str(row.get("blueprint_id")))
            if len(selected) >= limit:
                break
    return pd.DataFrame(selected)


def run_numeric(queue: pd.DataFrame) -> dict[str, Any]:
    runtime_dir = RUNTIME / "numeric_probe"
    queue_path = RUNTIME / "a7ls3_numeric_checkpoint_queue.csv"
    report_path = RUNTIME / "CRYPTO_A7LS3_NUMERIC_DETAIL_20260605.md"
    env = os.environ.copy()
    env.update(
        {
            "A7FF8_STAGE": "A7LS-3",
            "A7FF8_FILE_PREFIX": "a7ls3",
            "A7FF8_RUNTIME": str(runtime_dir),
            "A7FF8_REPORT": str(report_path),
            "A7FF8_QUEUE_PATH": str(queue_path),
            "A7FF8_AUTH_MANIFEST": str(LS2 / "a7ls2_manifest.json"),
            "A7FF8_AUTH_DECISION": "PASS_A7LS2_FIRST_CHECKPOINT_MATERIALIZATION_READY",
            "A7FF8_MATERIALIZE_CAP": str(len(queue)),
            "A7FF8_FAST_NUMERIC_CAP": str(len(queue)),
            "A7FF8_PORTFOLIO_CAP": "128",
            "A7FF8_QUEUE_LIMIT": str(len(queue)),
            "A7FF8_WRITE_CONTROL_DETAIL": "1",
        }
    )
    timeout_seconds = int(os.environ.get("A7LS3_TIMEOUT_SECONDS", "900"))
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
    (RUNTIME / "a7ls3_numeric_stdout.log").write_text(stdout, encoding="utf-8")
    manifest = read_json(runtime_dir / "a7ls3_manifest.json")
    if not manifest:
        manifest = {
            "decision": "HOLD_A7LS3_NUMERIC_PROBE_TIMEOUT_OR_NO_MANIFEST",
            "blockers": ["numeric_probe_timeout_or_no_manifest"],
            "materialized_activity_ok_count": 0,
            "label_response_rows": 0,
            "non_l7_numeric_clue_rows": 0,
            "rank_label_diagnostic_clue_rows": 0,
            "selected_portfolio_queue_count": 0,
        }
    manifest["returncode"] = returncode
    manifest["timed_out"] = timed_out
    manifest["timeout_seconds"] = timeout_seconds
    return manifest


def summarize_numeric() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    runtime_dir = RUNTIME / "numeric_probe"
    responses = read_csv(runtime_dir / "a7ls3_label_response_metrics.csv")
    selected = read_csv(runtime_dir / "a7ls3_selected_portfolio_queue.csv")
    material = read_csv(runtime_dir / "a7ls3_materialization_metrics.csv")
    if not responses.empty:
        response_summary = responses.groupby(["semantic_pair", "decision", "label_family"], dropna=False).size().reset_index(name="rows")
        response_summary.to_csv(RUNTIME / "a7ls3_response_summary.csv", index=False)
    else:
        response_summary = pd.DataFrame()
    if not selected.empty:
        selected_summary = selected.groupby(["semantic_pair", "label_family"], dropna=False).size().reset_index(name="rows")
        selected_summary.to_csv(RUNTIME / "a7ls3_selected_summary.csv", index=False)
    else:
        selected_summary = pd.DataFrame()
    if not material.empty:
        material_summary = material.groupby(["a7ls_arm", "semantic_pair"], dropna=False).agg(
            rows=("blueprint_id", "size"),
            activity_ok=("activity_ok", "sum"),
            median_finite_share=("finite_share", "median"),
            median_nonzero_share=("nonzero_share", "median"),
        ).reset_index()
        material_summary.to_csv(RUNTIME / "a7ls3_numeric_materialization_summary.csv", index=False)
    else:
        material_summary = pd.DataFrame()
    return response_summary, selected_summary, material_summary


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    ls2 = read_json(LS2 / "a7ls2_manifest.json")
    if not ls2.get("authorizes_a7ls3_numeric_wave"):
        raise SystemExit(f"A7LS-2 does not authorize A7LS-3: {ls2.get('decision')}")
    metrics = pd.read_csv(LS2 / "a7ls2_materialization_metrics_executed.csv")
    target = int(os.environ.get("A7LS3_QUEUE_ROWS", "512"))
    queue = build_queue(metrics, target)
    queue.to_csv(RUNTIME / "a7ls3_numeric_checkpoint_queue.csv", index=False)
    queue_summary = queue.groupby(["a7ls_arm", "semantic_pair"], dropna=False).size().reset_index(name="rows")
    queue_summary.to_csv(RUNTIME / "a7ls3_queue_summary.csv", index=False)
    numeric_manifest = run_numeric(queue)
    response_summary, selected_summary, material_summary = summarize_numeric()

    blockers: list[str] = []
    if numeric_manifest.get("returncode") != 0:
        blockers.append("numeric_probe_returncode_nonzero")
    if numeric_manifest.get("timed_out"):
        blockers.append("numeric_probe_timeout")
    non_l7 = int(numeric_manifest.get("non_l7_numeric_clue_rows", 0) or 0)
    selected_count = int(numeric_manifest.get("selected_portfolio_queue_count", 0) or 0)
    activity_ok = int(numeric_manifest.get("materialized_activity_ok_count", 0) or 0)
    if activity_ok < int(0.7 * len(queue)):
        blockers.append("numeric_materialization_activity_below_70pct")
    if non_l7 < 4:
        blockers.append("non_l7_numeric_clues_lt_4")
    if selected_count < 4:
        blockers.append("selected_portfolio_queue_lt_4")
    decision = "PASS_A7LS3_NUMERIC_CHECKPOINT_CLUES_FOUND" if not blockers else "HOLD_A7LS3_NUMERIC_CHECKPOINT_WEAK"
    manifest = {
        "stage": "A7LS-3",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7LS-2",
        "source_decision": ls2.get("decision"),
        "input_materialized_rows": int(len(metrics)),
        "numeric_checkpoint_queue_rows": int(len(queue)),
        "numeric_returncode": numeric_manifest.get("returncode"),
        "numeric_decision": numeric_manifest.get("decision"),
        "materialized_activity_ok_count": activity_ok,
        "label_response_rows": int(numeric_manifest.get("label_response_rows", 0) or 0),
        "non_l7_numeric_clue_rows": non_l7,
        "rank_label_diagnostic_clue_rows": int(numeric_manifest.get("rank_label_diagnostic_clue_rows", 0) or 0),
        "selected_portfolio_queue_count": selected_count,
        "executes_numeric_probe": True,
        "executes_search": False,
        "authorizes_a7ls4_checkpoint_triage": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls3_manifest.json", manifest)
    REPORT.write_text("\n".join([
        "# CRYPTO A7LS-3 NUMERIC CHECKPOINT FROM MATERIALIZED",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7LS-3 builds a memory-safe numeric checkpoint queue from A7LS-2 activity-ok materialized candidates and runs the existing numeric probe.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Queue Summary",
        "",
        md_table(queue_summary, 80),
        "",
        "## Response Summary",
        "",
        md_table(response_summary.sort_values("rows", ascending=False) if not response_summary.empty else response_summary, 80),
        "",
        "## Selected Summary",
        "",
        md_table(selected_summary, 40),
        "",
        "## Numeric Materialization Summary",
        "",
        md_table(material_summary, 80),
        "",
    ]), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
