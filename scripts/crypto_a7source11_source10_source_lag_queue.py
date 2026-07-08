from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = (
    REPO
    / "runtime"
    / "a7source10_seed_expansion_reward_aggregate_20260708"
    / "a7v3s0_reward_rejections_enriched.csv"
)
DEFAULT_RUNTIME = REPO / "runtime" / "a7source11_source10_source_lag_retest_queue_20260708"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SOURCE11_SOURCE10_SOURCE_LAG_RETEST_QUEUE_20260708.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(frame: pd.DataFrame, max_rows: int = 40) -> str:
    if frame.empty:
        return "`<empty>`"
    view = frame.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```text\n" + view.to_string(index=False) + "\n```"


def normalize_formula(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(r"\s+", "", text)
    return text


def reason_flags(reasons: str) -> tuple[bool, bool]:
    parts = [part for part in str(reasons or "").split(";") if part]
    has_source_lag = "source_lag_required_not_proven" in parts
    only_source_lag = has_source_lag and len(parts) == 1
    return has_source_lag, only_source_lag


def numeric(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = frame.copy()
    for col in columns:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def build(input_path: Path, runtime: Path, report: Path, max_rows: int) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    if not input_path.exists():
        raise FileNotFoundError(f"missing Source10 reward rejection input: {input_path}")
    rows = pd.read_csv(input_path, low_memory=False)
    rows = rows.copy()
    if "formula" not in rows.columns and "expression" in rows.columns:
        rows["formula"] = rows["expression"]
    if "expression" not in rows.columns:
        rows["expression"] = rows.get("formula", "")
    rows["formula_norm"] = rows["formula"].map(normalize_formula)
    flags = rows["hard_reject_reasons"].fillna("").map(reason_flags)
    rows["has_source_lag_reject"] = [item[0] for item in flags]
    rows["only_source_lag_reject"] = [item[1] for item in flags]
    source_lag = rows[rows["has_source_lag_reject"]].copy()

    score_cols = [
        "only_source_lag_reject",
        "overall_reward",
        "train_sortino",
        "validation_sortino",
        "test_sortino",
        "recent_sortino",
        "stress_sortino",
        "min_oos_floor_sortino",
    ]
    source_lag = numeric(source_lag, [col for col in score_cols if col != "only_source_lag_reject"])
    source_lag = source_lag.sort_values(
        [col for col in score_cols if col in source_lag.columns],
        ascending=[False] * len([col for col in score_cols if col in source_lag.columns]),
    )
    source_lag = source_lag.drop_duplicates(["formula_norm", "horizon_h"], keep="first").copy()
    selected = source_lag.head(max_rows).copy()

    if not selected.empty:
        selected["source_blueprint_id"] = selected.get("blueprint_id", "")
        selected["candidate_role"] = "source10_source_lag_retest_candidate"
        selected["motif"] = selected.get("motif", "a7source11_source10_source_lag_retest").astype(str)
        selected["skeleton_key"] = selected.get("skeleton_key", selected["formula"].astype(str).str.replace(r"\d+", "N", regex=True))
        selected["source_lag_retest_priority"] = range(1, len(selected) + 1)
        selected["expression"] = selected["formula"].astype(str)

    queue_cols = [
        col
        for col in [
            "source_blueprint_id",
            "blueprint_id",
            "horizon_h",
            "expression",
            "formula",
            "candidate_role",
            "semantic_pair",
            "motif",
            "skeleton_key",
            "source_lag_required_fields",
            "source_lag_required_families",
            "source_lag_gate",
            "hard_reject_reasons",
            "only_source_lag_reject",
            "overall_reward",
            "train_sortino",
            "validation_sortino",
            "test_sortino",
            "recent_sortino",
            "stress_sortino",
            "min_oos_floor_sortino",
            "recent_shuffle_control_ratio",
            "source_lag_retest_priority",
        ]
        if col in selected.columns
    ]
    queue = selected[queue_cols].copy() if not selected.empty else pd.DataFrame(columns=queue_cols)
    queue_path = runtime / "a7source11_source10_source_lag_retest_queue.csv"
    queue.to_csv(queue_path, index=False)

    reason_summary = (
        source_lag["hard_reject_reasons"].fillna("").value_counts().rename_axis("hard_reject_reasons").reset_index(name="count")
        if not source_lag.empty
        else pd.DataFrame(columns=["hard_reject_reasons", "count"])
    )
    pair_summary = (
        queue.groupby(["semantic_pair", "only_source_lag_reject"], dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)
        if not queue.empty and "semantic_pair" in queue.columns
        else pd.DataFrame(columns=["semantic_pair", "only_source_lag_reject", "count"])
    )
    reason_summary.to_csv(runtime / "a7source11_source_lag_rejection_reason_summary.csv", index=False)
    pair_summary.to_csv(runtime / "a7source11_source_lag_retest_pair_summary.csv", index=False)

    decision = "PASS_A7SOURCE11_SOURCE_LAG_RETEST_QUEUE_READY" if not queue.empty else "HOLD_A7SOURCE11_NO_SOURCE_LAG_REJECTS"
    manifest = {
        "stage": "A7SOURCE11-SOURCE10-SOURCE-LAG-QUEUE",
        "generated_at": now_utc(),
        "decision": decision,
        "input": str(input_path),
        "runtime": str(runtime),
        "report": str(report),
        "input_rows": int(rows.shape[0]),
        "source_lag_reject_rows": int(source_lag.shape[0]),
        "source_lag_unique_formula_horizon": int(source_lag[["formula_norm", "horizon_h"]].drop_duplicates().shape[0]) if not source_lag.empty else 0,
        "queue_rows": int(queue.shape[0]),
        "only_source_lag_queue_rows": int(queue["only_source_lag_reject"].sum()) if not queue.empty and "only_source_lag_reject" in queue.columns else 0,
        "queue": str(queue_path),
        "authorizes_source_lag_retest": bool(not queue.empty),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(runtime / "a7source11_manifest.json", manifest)

    lines = [
        "# CRYPTO A7SOURCE11 Source10 Source-Lag Retest Queue",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This packages Source10 reward hard rejects into a conservative source-lag retest queue. It does not relax the source-lag gate and does not authorize alpha proof.",
        "",
        "## Counts",
        "",
        f"- input_rows: `{manifest['input_rows']}`",
        f"- source_lag_reject_rows: `{manifest['source_lag_reject_rows']}`",
        f"- source_lag_unique_formula_horizon: `{manifest['source_lag_unique_formula_horizon']}`",
        f"- queue_rows: `{manifest['queue_rows']}`",
        f"- only_source_lag_queue_rows: `{manifest['only_source_lag_queue_rows']}`",
        "",
        "## Pair Summary",
        "",
        md_table(pair_summary, 30),
        "",
        "## Retest Queue",
        "",
        md_table(queue, 40),
        "",
        "## Rejection Reason Summary",
        "",
        md_table(reason_summary, 30),
        "",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--max-rows", type=int, default=96)
    args = parser.parse_args()
    manifest = build(args.input, args.runtime, args.report, args.max_rows)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
