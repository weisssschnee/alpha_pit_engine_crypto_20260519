from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE4 = REPO / "runtime" / "a7source4_batch_source_lag_retest_20260703" / "a7source4_source_lag_summary.csv"
DEFAULT_RUNTIME = REPO / "runtime" / "a7source5_source_lag_survivor_queue_20260703"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SOURCE5_SOURCE_LAG_SURVIVOR_QUEUE_20260703.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(frame: pd.DataFrame, max_rows: int = 80) -> str:
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


def family_from_formula(formula: str) -> str:
    text = str(formula)
    families: list[str] = []
    if "open_interest" in text:
        families.append("open_interest")
    if "funding" in text:
        families.append("funding_state")
    if "premium" in text or "basis" in text or "mark_index" in text:
        families.append("basis_premium")
    if "long_short" in text or "position" in text:
        families.append("positioning")
    if "volume" in text or "liquidity" in text:
        families.append("liquidity")
    return "|".join(families) if families else "other"


def build(source4: Path, runtime: Path, report: Path) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    summary = pd.read_csv(source4, low_memory=False)
    survivors = summary[summary["source_lag_gate"].astype(str).eq("PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC")].copy()
    if survivors.empty:
        queue = pd.DataFrame()
    else:
        survivors["expression"] = survivors["formula"].astype(str)
        survivors["candidate_role"] = "source_lag_survivor_research_candidate"
        survivors["semantic_pair"] = survivors["formula"].map(family_from_formula)
        survivors["motif"] = "a7source5_source_lag_survivor"
        survivors["skeleton_key"] = survivors["formula"].astype(str).str.replace(r"\d+", "N", regex=True)
        survivors["source_lag_survivor_rank"] = survivors["nonoverlap_floor_sortino_source_lag_2h"].rank(
            ascending=False,
            method="first",
        ).astype(int)
        queue_cols = [
            "source_blueprint_id",
            "blueprint_id",
            "horizon_h",
            "expression",
            "formula",
            "candidate_role",
            "semantic_pair",
            "motif",
            "skeleton_key",
            "source_lag_gate",
            "sortino_source_lag_1h",
            "sortino_source_lag_2h",
            "sortino_source_lag_4h",
            "nonoverlap_floor_sortino_source_lag_1h",
            "nonoverlap_floor_sortino_source_lag_2h",
            "nonoverlap_floor_sortino_source_lag_4h",
            "rankic_mean_source_lag_2h",
            "floor_retention_source_lag_2h",
            "source_lag_survivor_rank",
        ]
        queue = survivors[queue_cols].sort_values("source_lag_survivor_rank").copy()

    queue_path = runtime / "a7source5_source_lag_survivor_reward_queue.csv"
    queue.to_csv(queue_path, index=False)
    family_summary = (
        queue.groupby("semantic_pair", dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)
        if not queue.empty
        else pd.DataFrame(columns=["semantic_pair", "count"])
    )
    family_summary.to_csv(runtime / "a7source5_survivor_family_summary.csv", index=False)
    manifest = {
        "stage": "A7SOURCE-5-SOURCE-LAG-SURVIVOR-QUEUE",
        "generated_at": now_utc(),
        "decision": "PASS_A7SOURCE5_SURVIVOR_REWARD_QUEUE_BUILT" if not queue.empty else "HOLD_A7SOURCE5_NO_SURVIVORS",
        "source4_summary": str(source4),
        "runtime": str(runtime),
        "report": str(report),
        "queue_rows": int(queue.shape[0]),
        "unique_source_blueprints": int(queue["source_blueprint_id"].nunique()) if not queue.empty else 0,
        "output_queue": str(queue_path),
        "authorizes_reward2": bool(not queue.empty),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(runtime / "a7source5_manifest.json", manifest)
    lines = [
        "# CRYPTO A7SOURCE-5 Source-Lag Survivor Reward Queue",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "This packages A7SOURCE-4 source-lag survivors into a strict reward queue. It is not alpha proof.",
        "",
        "## Counts",
        "",
        f"- queue_rows: `{manifest['queue_rows']}`",
        f"- unique_source_blueprints: `{manifest['unique_source_blueprints']}`",
        "",
        "## Survivor Queue",
        "",
        md_table(queue, 20),
        "",
        "## Family Summary",
        "",
        md_table(family_summary, 20),
        "",
        "## Next Required",
        "",
        "- Run A7REWARD-2 strict reward on this queue.",
        "- Keep source-lag and source-publication proof gates active.",
        "",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source4", type=Path, default=DEFAULT_SOURCE4)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    manifest = build(args.source4, args.runtime, args.report)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
