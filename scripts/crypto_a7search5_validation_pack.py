from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DEFAULT_ACCEPTED_ROOT = Path(
    r"H:\AlphaFactory_CryptoData_archive\a7search5_selected_full_reward_r3_aggregate_20260630"
)
DEFAULT_RUNTIME = Path(r"H:\AlphaFactory_CryptoData_archive\a7search5_validation_pack_20260630")
DEFAULT_REPORT = Path(
    r"D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
    r"\reports\CRYPTO_A7SEARCH5_VALIDATION_PACK_20260630.md"
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(frame: pd.DataFrame, max_rows: int = 30) -> str:
    if frame.empty:
        return "`<empty>`"
    view = frame.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size <= 2:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def variant_rows() -> list[dict[str, Any]]:
    right = "top_long_short_account_ratio_last"
    denom = f"Abs(CSRank({right}))"
    rows: list[dict[str, Any]] = []

    def add(name: str, expr: str, group: str, note: str) -> None:
        rows.append(
            {
                "blueprint_id": f"a7search5_vp_{name}",
                "production_key": f"a7search5_vp_{name}",
                "semantic_pair": "open_interest|positioning",
                "motif": "safe_div_abs_validation",
                "skeleton_key": name,
                "expression": expr,
                "primary_field": "open_interest_value_last"
                if "open_interest_value_last" in expr
                else "open_interest_value_mean"
                if "open_interest_value_mean" in expr
                else right,
                "secondary_field": right if right in expr and "open_interest_value" in expr else "",
                "validation_group": group,
                "validation_note": note,
                "candidate_role": "validation_ablation",
            }
        )

    for field in ["open_interest_value_last", "open_interest_value_mean"]:
        suffix = "last" if field.endswith("_last") else "mean"
        z = f"ZScore({field})"
        rank = f"CSRank({field})"
        add(
            f"canonical_{suffix}",
            f"SafeDiv({z},{denom})",
            "canonical",
            "accepted structure rerun",
        )
        add(f"numerator_z_{suffix}", z, "single_leg", "OI value z-score only")
        add(f"numerator_rank_{suffix}", rank, "single_leg", "OI value cross-sectional rank only")
        add(
            f"no_abs_denom_{suffix}",
            f"SafeDiv({z},CSRank({right}))",
            "operator_ablation",
            "remove Abs from denominator",
        )
        add(
            f"spread_rank_{suffix}",
            f"Sub({rank},CSRank({right}))",
            "operator_ablation",
            "replace division with rank spread",
        )
        add(
            f"rank_mul_{suffix}",
            f"Mul({rank},CSRank({right}))",
            "operator_ablation",
            "replace division with rank multiplication",
        )
        add(
            f"smooth_168_{suffix}",
            f"SafeDiv(ZScore(Mean({field},168)),{denom})",
            "robustness_variant",
            "smooth OI value before canonical denominator",
        )

    add(
        "denominator_csrank_only",
        f"CSRank({right})",
        "single_leg",
        "top-account positioning rank only",
    )
    add(
        "denominator_abs_csrank_only",
        denom,
        "single_leg",
        "absolute top-account positioning rank only",
    )
    return rows


def build_queue(runtime: Path) -> Path:
    runtime.mkdir(parents=True, exist_ok=True)
    queue = pd.DataFrame(variant_rows())
    queue_path = runtime / "a7search5_validation_ablation_queue.csv"
    queue.to_csv(queue_path, index=False)
    return queue_path


def run_reward(queue_path: Path, runtime: Path, report: Path, python_exe: str) -> int:
    reward_runtime = runtime / "reward_runtime"
    reward_report = runtime / "CRYPTO_A7SEARCH5_VALIDATION_REWARD_MODEL_20260630.md"
    cmd = [
        python_exe,
        "-W",
        "ignore",
        "-m",
        "scripts.crypto_a7reward1_portfolio_reward_model",
        "--queue",
        str(queue_path),
        "--candidate-cap",
        "0",
        "--hours-per-split",
        "720",
        "--train-hours-per-split",
        "0",
        "--orientation-extension-hours",
        "0",
        "--cost-bps",
        "5.0",
        "--checkpoint-every",
        "4",
        "--runtime",
        str(reward_runtime),
        "--report",
        str(reward_report),
    ]
    log_path = runtime / "a7search5_validation_reward_stdout.log"
    err_path = runtime / "a7search5_validation_reward_stderr.log"
    with log_path.open("w", encoding="utf-8") as stdout, err_path.open("w", encoding="utf-8") as stderr:
        completed = subprocess.run(cmd, cwd=REPO, stdout=stdout, stderr=stderr, check=False)
    return int(completed.returncode)


def summarize(runtime: Path, accepted_root: Path, report: Path, reward_returncode: int) -> dict[str, Any]:
    queue = pd.read_csv(runtime / "a7search5_validation_ablation_queue.csv")
    reward_runtime = runtime / "reward_runtime"
    leaderboard_path = reward_runtime / "a7reward1_candidate_reward_leaderboard.csv"
    accepted_path = reward_runtime / "a7reward1_accepted_for_next_search.csv"
    rejections_path = reward_runtime / "a7reward1_validation_gate_rejections.csv"
    errors_path = reward_runtime / "a7reward1_eval_errors.csv"
    metrics_path = reward_runtime / "a7reward1_split_reward_metrics.csv"

    leaderboard = read_csv_or_empty(leaderboard_path)
    accepted = read_csv_or_empty(accepted_path)
    rejections = read_csv_or_empty(rejections_path)
    errors = read_csv_or_empty(errors_path)
    metrics = read_csv_or_empty(metrics_path)

    group_map = queue[["blueprint_id", "validation_group", "validation_note"]].drop_duplicates()
    if not leaderboard.empty:
        leaderboard = leaderboard.merge(group_map, on="blueprint_id", how="left")
    if not accepted.empty:
        accepted = accepted.merge(group_map, on="blueprint_id", how="left")
    if not rejections.empty:
        rejections = rejections.merge(group_map, on="blueprint_id", how="left")

    accepted_summary = (
        accepted.groupby(["validation_group", "blueprint_id", "horizon_h"], dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            train_sortino=("train_sortino", "max"),
            validation_sortino=("validation_sortino", "max"),
            test_sortino=("test_sortino", "max"),
            recent_sortino=("recent_sortino", "max"),
            min_oos_floor_sortino=("min_oos_floor_sortino", "max"),
            stress_floor_sortino=("stress_floor_sortino", "max"),
            recent_shuffle_control_ratio=("recent_shuffle_control_ratio", "min"),
        )
        .reset_index()
        .sort_values(["min_oos_floor_sortino", "recent_sortino"], ascending=False)
        if not accepted.empty
        else pd.DataFrame()
    )
    group_summary = (
        leaderboard.groupby("validation_group", dropna=False)
        .agg(
            candidates=("blueprint_id", "nunique"),
            accepted_rows=("gate_pass", lambda s: int(s.astype(bool).sum())),
            max_recent_sortino=("recent_sortino", "max"),
            max_min_oos_floor_sortino=("min_oos_floor_sortino", "max"),
        )
        .reset_index()
        .sort_values(["accepted_rows", "max_min_oos_floor_sortino"], ascending=False)
        if not leaderboard.empty
        else pd.DataFrame()
    )

    canonical_accept = int(
        accepted["validation_group"].eq("canonical").sum()
        if not accepted.empty and "validation_group" in accepted
        else 0
    )
    single_leg_accept = int(
        accepted["validation_group"].eq("single_leg").sum()
        if not accepted.empty and "validation_group" in accepted
        else 0
    )
    operator_ablation_accept = int(
        accepted["validation_group"].eq("operator_ablation").sum()
        if not accepted.empty and "validation_group" in accepted
        else 0
    )
    if reward_returncode != 0 or not errors.empty:
        decision = "HOLD_A7SEARCH5_VALIDATION_EVAL_ERROR"
    elif canonical_accept > 0 and single_leg_accept == 0 and operator_ablation_accept == 0:
        decision = "PASS_A7SEARCH5_CANONICAL_INCREMENTAL_EVIDENCE"
    elif canonical_accept > 0:
        decision = "HOLD_A7SEARCH5_CANONICAL_NOT_UNIQUE_INCREMENT"
    else:
        decision = "HOLD_A7SEARCH5_CANONICAL_FAILED_ABLATION_GATE"

    outputs = {
        "queue": runtime / "a7search5_validation_ablation_queue.csv",
        "leaderboard": leaderboard_path,
        "accepted": accepted_path,
        "rejections": rejections_path,
        "errors": errors_path,
        "metrics": metrics_path,
        "accepted_summary": runtime / "a7search5_validation_accepted_summary.csv",
        "group_summary": runtime / "a7search5_validation_group_summary.csv",
        "manifest": runtime / "a7search5_validation_manifest.json",
    }
    accepted_summary.to_csv(outputs["accepted_summary"], index=False)
    group_summary.to_csv(outputs["group_summary"], index=False)

    manifest = {
        "stage": "A7SEARCH5-VALIDATION-PACK",
        "generated_at": now_utc(),
        "decision": decision,
        "accepted_root": str(accepted_root),
        "runtime": str(runtime),
        "report": str(report),
        "reward_returncode": reward_returncode,
        "queue_rows": int(queue.shape[0]),
        "leaderboard_rows": int(leaderboard.shape[0]),
        "accepted_rows": int(accepted.shape[0]),
        "accepted_unique_blueprints": int(accepted["blueprint_id"].nunique()) if not accepted.empty else 0,
        "eval_error_rows": int(errors.shape[0]),
        "split_metric_rows": int(metrics.shape[0]),
        "canonical_accepted_rows": canonical_accept,
        "single_leg_accepted_rows": single_leg_accept,
        "operator_ablation_accepted_rows": operator_ablation_accept,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_next_search_memory_seed": decision.startswith("PASS_"),
        "outputs": {key: str(value) for key, value in outputs.items()},
    }
    write_json(outputs["manifest"], manifest)

    lines = [
        "# CRYPTO A7SEARCH5 Validation Pack 20260630",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This validates whether the A7SEARCH5 accepted OI/positioning structure has incremental evidence over single-leg and operator-ablation baselines. It is not alpha proof and does not authorize shadow, paper, or live trading.",
        "",
        "## Counts",
        "",
        f"- queue_rows: `{manifest['queue_rows']}`",
        f"- leaderboard_rows: `{manifest['leaderboard_rows']}`",
        f"- accepted_rows: `{manifest['accepted_rows']}`",
        f"- accepted_unique_blueprints: `{manifest['accepted_unique_blueprints']}`",
        f"- eval_error_rows: `{manifest['eval_error_rows']}`",
        f"- canonical_accepted_rows: `{canonical_accept}`",
        f"- single_leg_accepted_rows: `{single_leg_accept}`",
        f"- operator_ablation_accepted_rows: `{operator_ablation_accept}`",
        "",
        "## Group Summary",
        "",
        md_table(group_summary),
        "",
        "## Accepted Summary",
        "",
        md_table(accepted_summary, 40),
        "",
        "## Interpretation",
        "",
    ]
    if decision == "PASS_A7SEARCH5_CANONICAL_INCREMENTAL_EVIDENCE":
        lines.append("- Canonical SafeDiv structure passed while single-leg and operator-ablation baselines did not pass. This supports incremental interaction evidence.")
    elif decision == "HOLD_A7SEARCH5_CANONICAL_NOT_UNIQUE_INCREMENT":
        lines.append("- Canonical structure passed, but at least one single-leg or operator-ablation baseline also passed. Treat this as non-unique information until deduped or neutralized.")
    elif decision == "HOLD_A7SEARCH5_CANONICAL_FAILED_ABLATION_GATE":
        lines.append("- Canonical structure did not pass this ablation validation. Do not seed next search from it.")
    else:
        lines.append("- Evaluation errors occurred. Inspect error rows before using this validation pack.")
    lines.extend(["", "## Outputs", ""])
    for key, value in outputs.items():
        lines.append(f"- `{key}`: `{value}`")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accepted-root", type=Path, default=DEFAULT_ACCEPTED_ROOT)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--skip-reward", action="store_true")
    args = parser.parse_args()

    args.runtime.mkdir(parents=True, exist_ok=True)
    queue_path = build_queue(args.runtime)
    if args.skip_reward:
        reward_returncode = 0
    else:
        reward_returncode = run_reward(queue_path, args.runtime, args.report, args.python)
    manifest = summarize(args.runtime, args.accepted_root, args.report, reward_returncode)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
