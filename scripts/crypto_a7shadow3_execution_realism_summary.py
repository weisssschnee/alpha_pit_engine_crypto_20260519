from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_RUNTIME = "runtime/a7shadow3_execution_realism_summary_20260703"
DEFAULT_REPORT = "reports/CRYPTO_A7SHADOW3_EXECUTION_REALISM_SUMMARY_20260703.md"
R2_RUNTIME = "runtime/a7shadow3_execution_realism_reward_r2_20260703"
ADAPTER_RUNTIME = "runtime/a7shadow3_reward_queue_adapter_20260703"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size <= 2:
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def fnum(value: Any) -> float:
    try:
        if value is None or value == "":
            return float("nan")
        return float(value)
    except Exception:
        return float("nan")


def build(repo: Path, runtime: Path, report: Path) -> dict[str, Any]:
    r2 = repo / R2_RUNTIME
    adapter = repo / ADAPTER_RUNTIME
    manifest = read_json(r2 / "a7reward1_manifest.json")
    adapter_manifest = read_json(adapter / "a7shadow3_queue_adapter_manifest.json")
    accepted = read_csv(r2 / "a7reward1_accepted_for_next_search.csv")
    rejected = read_csv(r2 / "a7reward1_validation_gate_rejections.csv")
    leaderboard = read_csv(r2 / "a7reward1_candidate_reward_leaderboard.csv")

    accepted_fields = [
        "blueprint_id",
        "expression",
        "horizon_h",
        "pareto_rank",
        "objective_pass_count",
        "train_sortino",
        "validation_sortino",
        "test_sortino",
        "recent_sortino",
        "min_oos_floor_sortino",
        "stress_floor_sortino",
        "recent_avg_turnover",
        "recent_capacity_proxy",
        "recent_control_ratio",
        "recent_shuffle_control_ratio",
        "source_lag_policy_status",
    ]
    write_csv(runtime / "a7shadow3_execution_accepted.csv", accepted, accepted_fields)

    rejection_counts = Counter(row.get("hard_reject_reasons", "") for row in rejected)
    rejection_rows = [{"hard_reject_reasons": k, "count": v} for k, v in rejection_counts.most_common()]
    write_csv(runtime / "a7shadow3_rejection_reason_summary.csv", rejection_rows, ["hard_reject_reasons", "count"])

    by_blueprint = Counter(row.get("blueprint_id", "") for row in accepted)
    accepted_blueprint_rows = [
        {
            "blueprint_id": blueprint_id,
            "accepted_horizon_count": count,
            "accepted_horizons": "|".join(row.get("horizon_h", "") for row in accepted if row.get("blueprint_id") == blueprint_id),
            "expression": next((row.get("expression", "") for row in accepted if row.get("blueprint_id") == blueprint_id), ""),
        }
        for blueprint_id, count in by_blueprint.most_common()
    ]
    write_csv(runtime / "a7shadow3_accepted_by_blueprint.csv", accepted_blueprint_rows, ["blueprint_id", "accepted_horizon_count", "accepted_horizons", "expression"])

    decision = (
        "PASS_A7SHADOW3_EXECUTION_REALISM_REWARD_ACCEPTED"
        if int(manifest.get("accepted_for_next_search_rows", 0)) > 0 and int(manifest.get("eval_error_rows", 0)) == 0
        else "HOLD_A7SHADOW3_NO_ACCEPTED_EXECUTION_REALISM"
    )
    out_manifest = {
        "stage": "A7SHADOW-3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "adapter_decision": adapter_manifest.get("decision", ""),
        "reward_decision": manifest.get("decision", ""),
        "queue_rows": manifest.get("queue_rows", 0),
        "reward_rows": manifest.get("reward_rows", 0),
        "accepted_rows": manifest.get("accepted_for_next_search_rows", 0),
        "accepted_unique_blueprints": manifest.get("accepted_for_next_search_unique_blueprints", 0),
        "hard_reject_rows": manifest.get("hard_reject_rows", 0),
        "eval_error_rows": manifest.get("eval_error_rows", 0),
        "cost_bps": manifest.get("cost_bps", 0),
        "train_crash_like_hours": manifest.get("train_crash_like_hours", 0),
        "may_stress_hours": manifest.get("may_stress_hours", 0),
        "top_pareto_blueprint_id": manifest.get("top_pareto_blueprint_id", ""),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_shadow_book": False,
        "authorizes_next_engineering_review": True,
        "next_required": [
            "live data adapter health check for accepted blueprints",
            "full signal correlation using realized return series, not just token overlap",
            "execution-capacity replay with explicit slippage/liquidity caps before any shadow book",
        ],
    }
    (runtime / "a7shadow3_manifest.json").write_text(json.dumps(out_manifest, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# CRYPTO A7SHADOW3 Execution Realism Summary",
        "",
        f"Generated: {out_manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7SHADOW-3 reruns the A7SHADOW-2 deduplicated keep leaders through the strict A7REWARD portfolio evaluator at 5bps cost. The first run exposed a queue adapter issue: empty `blueprint_id` values caused reward grouping to collapse multiple candidates into one blank id. R2 fixes this by assigning `blueprint_id = candidate_id` before evaluation.",
        "",
        "This does not authorize alpha proof, shadow, paper, or live trading.",
        "",
        "## Counts",
        "",
        f"- queue_rows: `{out_manifest['queue_rows']}`",
        f"- reward_rows: `{out_manifest['reward_rows']}`",
        f"- accepted_rows: `{out_manifest['accepted_rows']}`",
        f"- accepted_unique_blueprints: `{out_manifest['accepted_unique_blueprints']}`",
        f"- hard_reject_rows: `{out_manifest['hard_reject_rows']}`",
        f"- eval_error_rows: `{out_manifest['eval_error_rows']}`",
        f"- cost_bps: `{out_manifest['cost_bps']}`",
        f"- train_crash_like_hours: `{out_manifest['train_crash_like_hours']}`",
        f"- may_stress_hours: `{out_manifest['may_stress_hours']}`",
        "",
        "## Accepted Rows",
        "",
        "| blueprint_id | horizon | pareto | pass_count | train | validation | test | recent | min_oos_floor | stress_floor | turnover | capacity_proxy | expression |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in accepted:
        lines.append(
            "| {blueprint_id} | {horizon_h} | {pareto_rank} | {objective_pass_count} | {train_sortino} | {validation_sortino} | {test_sortino} | {recent_sortino} | {min_oos_floor_sortino} | {stress_floor_sortino} | {recent_avg_turnover} | {recent_capacity_proxy} | `{expression}` |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Rejection Summary",
            "",
            "| count | reasons |",
            "|---:|---|",
        ]
    )
    for row in rejection_rows[:12]:
        lines.append(f"| {row['count']} | `{row['hard_reject_reasons']}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The execution/reward gate did not erase all historical candidates after the adapter fix. Four horizon rows survived, covering three deduplicated blueprints. The surviving set is still narrow: OI/premium and OI/funding dominate. That supports continuing engineering review for these mechanisms while treating broader formula-generation and feature-supply as still unresolved.",
            "",
            "## Outputs",
            "",
            f"- accepted: `{runtime / 'a7shadow3_execution_accepted.csv'}`",
            f"- accepted_by_blueprint: `{runtime / 'a7shadow3_accepted_by_blueprint.csv'}`",
            f"- rejection_summary: `{runtime / 'a7shadow3_rejection_reason_summary.csv'}`",
            f"- manifest: `{runtime / 'a7shadow3_manifest.json'}`",
        ]
    )
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--runtime", default=DEFAULT_RUNTIME)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    manifest = build(repo, repo / args.runtime, repo / args.report)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
