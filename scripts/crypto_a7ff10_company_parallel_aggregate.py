from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = Path(os.environ.get("A7FF10_AGG_RUNTIME", str(REPO / "runtime" / "a7ff10_company_parallel_aggregate")))
REPORT = Path(os.environ.get("A7FF10_AGG_REPORT", str(REPO / "reports" / "CRYPTO_A7FF10_COMPANY_PARALLEL_AGGREGATE_20260530.md")))
SHARD_ROOT = Path(os.environ.get("A7FF10_SHARD_ROOT", str(REPO / "runtime")))
SHARD_COUNT = int(os.environ.get("A7FF10_SHARD_COUNT", "4"))


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


def shard_dir(i: int) -> Path:
    return SHARD_ROOT / f"a7ff10_company_numeric_probe_shard_{i:02d}"


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    shard_rows: list[dict[str, Any]] = []
    response_frames: list[pd.DataFrame] = []
    selected_frames: list[pd.DataFrame] = []
    family_frames: list[pd.DataFrame] = []
    decision_frames: list[pd.DataFrame] = []
    missing: list[str] = []

    for i in range(SHARD_COUNT):
        sid = f"{i:02d}"
        prefix = f"a7ff10s{sid}"
        root = shard_dir(i)
        manifest_path = root / f"{prefix}_manifest.json"
        manifest = read_json(manifest_path)
        if not manifest:
            missing.append(str(manifest_path))
            continue
        shard_rows.append(
            {
                "shard": sid,
                "stage": manifest.get("stage", ""),
                "decision": manifest.get("decision", ""),
                "input_blueprint_count": manifest.get("input_blueprint_count", 0),
                "queue_offset": manifest.get("queue_offset", 0),
                "queue_limit": manifest.get("queue_limit", 0),
                "materialized_activity_ok_count": manifest.get("materialized_activity_ok_count", 0),
                "label_response_rows": manifest.get("label_response_rows", 0),
                "non_l7_numeric_clue_rows": manifest.get("non_l7_numeric_clue_rows", 0),
                "rank_label_diagnostic_clue_rows": manifest.get("rank_label_diagnostic_clue_rows", 0),
                "portfolio_queue_count": manifest.get("portfolio_queue_count", 0),
                "selected_portfolio_queue_count": manifest.get("selected_portfolio_queue_count", 0),
                "uses_may": manifest.get("uses_may", False),
                "authorizes_search": manifest.get("authorizes_search", False),
            }
        )
        for target, frames in [
            (root / f"{prefix}_label_response_metrics.csv", response_frames),
            (root / f"{prefix}_selected_portfolio_queue.csv", selected_frames),
            (root / f"{prefix}_family_decision_summary.csv", family_frames),
            (root / f"{prefix}_decision_counts.csv", decision_frames),
        ]:
            df = load_csv(target)
            if not df.empty:
                df.insert(0, "shard", sid)
                frames.append(df)

    shards = pd.DataFrame(shard_rows)
    responses = pd.concat(response_frames, ignore_index=True) if response_frames else pd.DataFrame()
    selected = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    family = pd.concat(family_frames, ignore_index=True) if family_frames else pd.DataFrame()
    decisions = pd.concat(decision_frames, ignore_index=True) if decision_frames else pd.DataFrame()

    clue_rows = responses[responses.get("decision", pd.Series(dtype=str)).astype(str).str.contains("NUMERIC_CLUE", na=False)].copy() if not responses.empty else pd.DataFrame()
    non_l7 = clue_rows[~clue_rows.get("label_family", pd.Series(dtype=str)).eq("L7_ranked_future_return")].copy() if not clue_rows.empty else pd.DataFrame()
    clue_summary = (
        non_l7.groupby(["semantic_pair", "label_family", "label_horizon_h"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        if not non_l7.empty
        else pd.DataFrame(columns=["semantic_pair", "label_family", "label_horizon_h", "count"])
    )

    complete = len(shard_rows) == SHARD_COUNT and not missing
    total_non_l7 = int(shards["non_l7_numeric_clue_rows"].sum()) if not shards.empty else 0
    total_selected = int(shards["selected_portfolio_queue_count"].sum()) if not shards.empty else 0
    decision = "PASS_A7FF10_COMPANY_PARALLEL_NUMERIC_AGGREGATE_BUILT" if complete and total_non_l7 > 0 and total_selected > 0 else "HOLD_A7FF10_COMPANY_PARALLEL_INCOMPLETE_OR_EMPTY"
    manifest = {
        "stage": "A7FF-10-COMPANY-PARALLEL-AGGREGATE",
        "generated_at": now_utc(),
        "decision": decision,
        "shard_count_expected": SHARD_COUNT,
        "shard_count_complete": len(shard_rows),
        "missing_manifests": missing,
        "total_input_blueprints": int(shards["input_blueprint_count"].sum()) if not shards.empty else 0,
        "total_materialized_activity_ok": int(shards["materialized_activity_ok_count"].sum()) if not shards.empty else 0,
        "total_label_response_rows": int(shards["label_response_rows"].sum()) if not shards.empty else 0,
        "total_non_l7_numeric_clue_rows": total_non_l7,
        "total_rank_label_diagnostic_clue_rows": int(shards["rank_label_diagnostic_clue_rows"].sum()) if not shards.empty else 0,
        "total_portfolio_queue_count": int(shards["portfolio_queue_count"].sum()) if not shards.empty else 0,
        "total_selected_portfolio_queue_count": total_selected,
        "uses_may": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    shards.to_csv(RUNTIME / "a7ff10_shard_summary.csv", index=False)
    clue_summary.to_csv(RUNTIME / "a7ff10_non_l7_clue_summary.csv", index=False)
    selected.to_csv(RUNTIME / "a7ff10_selected_portfolio_queue_all_shards.csv", index=False)
    decisions.to_csv(RUNTIME / "a7ff10_decision_counts_all_shards.csv", index=False)
    family.to_csv(RUNTIME / "a7ff10_family_decision_summary_all_shards.csv", index=False)
    write_json(RUNTIME / "a7ff10_manifest.json", manifest)

    lines = [
        "# CRYPTO A7FF-10 COMPANY PARALLEL NUMERIC AGGREGATE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-10 aggregates company-machine parallel numeric-probe shards. It is not generation, replay, search, alpha proof, shadow, paper, or live execution.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Shards",
        "",
        md_table(shards),
        "",
        "## Non-L7 Clue Summary",
        "",
        md_table(clue_summary, 120),
        "",
        "## Boundary",
        "",
        "```text",
        "No May/post-selection stress is used in scoring or authorization.",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "This stage only scales numeric probing across the A7FF-7E blueprint queue.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
