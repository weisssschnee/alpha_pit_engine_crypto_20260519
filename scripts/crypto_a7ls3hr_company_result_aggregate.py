from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ls3hr_company_result_aggregate"
REPORT = REPO / "reports" / "CRYPTO_A7LS3HR_COMPANY_RESULT_AGGREGATE_20260605.md"
DEFAULT_EXTERNAL = Path(
    "G:/AlphaFactory_CryptoData/research_runtime/a7ls3hr_company_numeric"
)
HANDOFF_MANIFEST = (
    REPO / "runtime" / "a7ls3hr_company_handoff_resize" / "a7ls3hr_manifest.json"
)
HANDOFF_PLAN = (
    REPO
    / "runtime"
    / "a7ls3hr_company_handoff_resize"
    / "a7ls3hr_company_shard_plan_64.csv"
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def find_manifest(shard_dir: Path, shard: str) -> Path | None:
    direct = shard_dir / f"a7ls3hr_{shard}_manifest.json"
    if direct.exists():
        return direct
    matches = sorted(shard_dir.glob("*manifest.json"))
    return matches[0] if matches else None


def collect_csv(shard_dir: Path, patterns: list[str]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for pattern in patterns:
        for path in sorted(shard_dir.glob(pattern)):
            try:
                frame = pd.read_csv(path)
            except Exception:
                continue
            frame["source_file"] = str(path)
            frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--external", default=str(DEFAULT_EXTERNAL))
    args = parser.parse_args()

    external = Path(args.external)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    handoff = read_json(HANDOFF_MANIFEST)
    expected_shards = int(handoff.get("primary_shard_count", 16))
    plan = pd.read_csv(HANDOFF_PLAN) if HANDOFF_PLAN.exists() else pd.DataFrame()

    manifest_rows: list[dict[str, Any]] = []
    missing_rows: list[dict[str, Any]] = []
    clue_frames: list[pd.DataFrame] = []
    response_frames: list[pd.DataFrame] = []
    portfolio_frames: list[pd.DataFrame] = []

    for i in range(expected_shards):
        shard = f"s{i:03d}"
        shard_dir = external / f"shard_{i:03d}"
        manifest_path = find_manifest(shard_dir, shard) if shard_dir.exists() else None
        if manifest_path is None:
            missing_rows.append(
                {
                    "shard": shard,
                    "shard_dir": str(shard_dir),
                    "missing_reason": "missing_manifest_or_shard_dir",
                }
            )
            continue
        manifest = read_json(manifest_path)
        manifest_rows.append(
            {
                "shard": shard,
                "manifest_path": str(manifest_path),
                "decision": manifest.get("decision", ""),
                "blockers": ";".join(map(str, manifest.get("blockers", []))),
                "label_response_rows": manifest.get("label_response_rows", ""),
                "clue_count": manifest.get("clue_count", manifest.get("numeric_clue_count", "")),
                "portfolio_candidate_count": manifest.get("portfolio_candidate_count", ""),
                "materialized_activity_ok_count": manifest.get("materialized_activity_ok_count", ""),
                "eval_failure_count": manifest.get("eval_failure_count", ""),
                "generated_at": manifest.get("generated_at", ""),
            }
        )
        clues = collect_csv(shard_dir, ["*clue*.csv", "*selected*.csv"])
        if not clues.empty:
            clues["shard"] = shard
            clue_frames.append(clues)
        responses = collect_csv(shard_dir, ["*label*response*.csv", "*response*.csv"])
        if not responses.empty:
            responses["shard"] = shard
            response_frames.append(responses)
        portfolios = collect_csv(shard_dir, ["*portfolio*.csv"])
        if not portfolios.empty:
            portfolios["shard"] = shard
            portfolio_frames.append(portfolios)

    manifest_df = pd.DataFrame(manifest_rows)
    missing_df = pd.DataFrame(missing_rows)
    clue_df = pd.concat(clue_frames, ignore_index=True) if clue_frames else pd.DataFrame()
    response_df = pd.concat(response_frames, ignore_index=True) if response_frames else pd.DataFrame()
    portfolio_df = pd.concat(portfolio_frames, ignore_index=True) if portfolio_frames else pd.DataFrame()

    manifest_df.to_csv(RUNTIME / "a7ls3hr_shard_manifest_summary.csv", index=False)
    missing_df.to_csv(RUNTIME / "a7ls3hr_missing_shards.csv", index=False)
    if not clue_df.empty:
        clue_df.to_csv(RUNTIME / "a7ls3hr_combined_clues.csv", index=False)
    if not response_df.empty:
        response_df.to_csv(RUNTIME / "a7ls3hr_combined_responses.csv", index=False)
    if not portfolio_df.empty:
        portfolio_df.to_csv(RUNTIME / "a7ls3hr_combined_portfolio_candidates.csv", index=False)

    decision_counts = (
        manifest_df["decision"].value_counts().rename_axis("decision").reset_index(name="count")
        if not manifest_df.empty and "decision" in manifest_df
        else pd.DataFrame(columns=["decision", "count"])
    )
    decision_counts.to_csv(RUNTIME / "a7ls3hr_decision_counts.csv", index=False)

    completed = int(len(manifest_df))
    missing = int(len(missing_df))
    clue_count = int(len(clue_df))
    portfolio_count = int(len(portfolio_df))
    response_rows = int(len(response_df))
    ready = completed == expected_shards and missing == 0
    stress_clean = 0
    if not clue_df.empty:
        for col in ["stress_clean", "may_stress_clean", "selected_stress_clean"]:
            if col in clue_df.columns:
                stress_clean = int(clue_df[col].astype(str).str.lower().isin(["true", "1", "yes"]).sum())
                break

    blockers: list[str] = []
    if missing:
        blockers.append("missing_shard_manifests")
    if completed == 0:
        blockers.append("no_company_results_found")
    if ready and clue_count == 0:
        blockers.append("no_combined_clue_rows")

    decision = (
        "PASS_A7LS3HR_COMPANY_RESULTS_AGGREGATED_READY_FOR_FORENSIC"
        if ready and clue_count > 0
        else "HOLD_A7LS3HR_COMPANY_RESULTS_INCOMPLETE_OR_NO_CLUES"
    )

    manifest = {
        "stage": "A7LS-3HR-AGG",
        "generated_at": now_utc(),
        "external": str(external),
        "expected_shards": expected_shards,
        "completed_shards": completed,
        "missing_shards": missing,
        "combined_clue_rows": clue_count,
        "combined_response_rows": response_rows,
        "combined_portfolio_rows": portfolio_count,
        "stress_clean_clue_count_observed": stress_clean,
        "decision": decision,
        "blockers": blockers,
        "executes_numeric_probe": False,
        "executes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls3hr_aggregate_manifest.json", manifest)

    plan_note = ""
    if not plan.empty:
        plan_note = f"\nExpected primary shards from handoff plan: {len(plan)} rows in shard plan.\n"

    report = [
        "# CRYPTO A7LS-3HR COMPANY RESULT AGGREGATE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Summary",
        "",
        f"- external: `{external}`",
        f"- expected_shards: {expected_shards}",
        f"- completed_shards: {completed}",
        f"- missing_shards: {missing}",
        f"- combined_clue_rows: {clue_count}",
        f"- combined_response_rows: {response_rows}",
        f"- combined_portfolio_rows: {portfolio_count}",
        f"- stress_clean_clue_count_observed: {stress_clean}",
        plan_note,
        "## Decision Counts",
        "",
        decision_counts.to_markdown(index=False) if not decision_counts.empty else "_none_",
        "",
        "## Missing Shards",
        "",
        missing_df.to_markdown(index=False) if not missing_df.empty else "_none_",
        "",
        "## Authorization",
        "",
        "- Aggregation only.",
        "- Does not execute numeric probe, search, alpha proof, shadow, paper, or live.",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
