from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import scripts.crypto_a7reward1_portfolio_reward_model as reward  # noqa: E402


DEFAULT_QUEUE = REPO / "runtime" / "a7v3s7_candidate_construction_redesign_20260614" / "a7v3s7_redesigned_reward_prequeue.csv"
DEFAULT_RUNTIME = REPO / "runtime" / "a7v3s9_prereward_oos_control_proxy_20260614"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7V3S9_PREREWARD_OOS_CONTROL_PROXY_20260614.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(frame: pd.DataFrame, max_rows: int = 30) -> str:
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


def num(frame: pd.DataFrame, column: str, default: float = np.nan) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(default, index=frame.index, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce")


def contains(frame: pd.DataFrame, column: str, needle: str) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(False, index=frame.index)
    return frame[column].fillna("").astype(str).str.contains(needle, regex=False)


def add_proxy_columns(rewards: pd.DataFrame) -> pd.DataFrame:
    if rewards.empty:
        return rewards.copy()
    out = rewards.copy()
    for column in [
        "train_sortino",
        "validation_sortino",
        "test_sortino",
        "recent_sortino",
        "median_oos_sortino",
        "train_oos_sortino_gap",
        "min_oos_sortino",
        "min_oos_floor_sortino",
        "stress_floor_sortino",
        "recent_shuffle_control_ratio",
        "oos_control_dominated_count",
        "oos_lag_stale_dominated_count",
        "oos_shuffle_dominated_count",
        "objective_pass_count",
    ]:
        out[column] = num(out, column)
    if "median_oos_sortino" not in rewards.columns:
        out["median_oos_sortino"] = pd.concat(
            [out["validation_sortino"], out["test_sortino"], out["recent_sortino"]],
            axis=1,
        ).median(axis=1)
    if "train_oos_sortino_gap" not in rewards.columns:
        out["train_oos_sortino_gap"] = (out["train_sortino"] - out["median_oos_sortino"]).abs()
    out["train_oos_overfit_gap"] = np.maximum(0.0, out["train_sortino"] - out["median_oos_sortino"] - 6.0)

    stress_obs = num(out, "stress_n_obs", 0).fillna(0) > 0
    stress_clean = (~stress_obs) | (out["stress_floor_sortino"] > 0)
    out["proxy_strict_pass"] = (
        (~out["hard_reject"].astype(bool))
        & (out["train_sortino"] > 0)
        & (out["recent_sortino"] > 0)
        & (out["train_oos_overfit_gap"] <= 0.0)
        & (out["min_oos_sortino"] > 0)
        & (out["min_oos_floor_sortino"] > 0)
        & stress_clean
        & out["oos_control_dominated_count"].fillna(99).eq(0)
        & out["oos_lag_stale_dominated_count"].fillna(99).eq(0)
        & (out["recent_shuffle_control_ratio"] < 1)
    )
    out["proxy_near_miss"] = (
        (~contains(out, "hard_reject_reasons", "non_finite_diagnostic_composite"))
        & (~contains(out, "hard_reject_reasons", "train_orientation_no_positive_edge"))
        & (~contains(out, "hard_reject_reasons", "train_sortino_non_positive"))
        & (out["train_sortino"] > 0)
        & (out["recent_sortino"] > 0)
        & (out["train_oos_overfit_gap"] <= 3.0)
        & (out["min_oos_sortino"] > -0.25)
        & (out["min_oos_floor_sortino"] > -0.75)
        & ((~stress_obs) | (out["stress_floor_sortino"] > -0.75))
        & (out["oos_control_dominated_count"].fillna(99) <= 1)
        & (out["oos_lag_stale_dominated_count"].fillna(99) <= 1)
        & (out["oos_shuffle_dominated_count"].fillna(99) <= 1)
        & (out["recent_shuffle_control_ratio"] < 1.0)
    )
    out["proxy_selectable"] = out["proxy_strict_pass"] | out["proxy_near_miss"]

    out["proxy_score"] = (
        1.25 * out["train_sortino"].fillna(-10).clip(-10, 10)
        + 2.00 * out["min_oos_floor_sortino"].fillna(-10).clip(-10, 10)
        + 1.25 * out["min_oos_sortino"].fillna(-10).clip(-10, 10)
        + 0.35 * out["recent_sortino"].fillna(-10).clip(-10, 10)
        + 1.00 * out["stress_floor_sortino"].fillna(0).clip(-10, 10)
        + 0.25 * out["objective_pass_count"].fillna(0)
        - 1.50 * out["oos_control_dominated_count"].fillna(4)
        - 1.50 * out["oos_lag_stale_dominated_count"].fillna(4)
        - 1.00 * out["oos_shuffle_dominated_count"].fillna(4)
        - 1.00 * np.maximum(0.0, out["recent_shuffle_control_ratio"].fillna(9) - 0.7)
        - 0.25 * out["train_oos_sortino_gap"].fillna(12).clip(0, 12)
        - 1.25 * out["train_oos_overfit_gap"].fillna(12).clip(0, 12)
    )
    out["proxy_bucket"] = np.select(
        [out["proxy_strict_pass"], out["proxy_near_miss"]],
        ["proxy_pass", "proxy_near_miss"],
        default="proxy_reject",
    )
    return out.sort_values(
        ["proxy_selectable", "proxy_strict_pass", "proxy_score", "min_oos_floor_sortino", "train_sortino", "recent_sortino"],
        ascending=[False, False, False, False, False, False],
    )


def bounded_select(frame: pd.DataFrame, target: int, pair_cap: int, motif_cap: int, skeleton_cap: int) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    selected: list[pd.Series] = []
    pair_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    for _, row in frame.sort_values(
        ["proxy_strict_pass", "proxy_score", "min_oos_floor_sortino", "train_sortino", "recent_sortino"],
        ascending=[False, False, False, False, False],
    ).iterrows():
        pair = str(row.get("semantic_pair", ""))
        motif = str(row.get("motif", ""))
        skeleton = str(row.get("skeleton_key", ""))
        if pair_counts.get(pair, 0) >= pair_cap:
            continue
        if motif_counts.get(motif, 0) >= motif_cap:
            continue
        if skeleton_counts.get(skeleton, 0) >= skeleton_cap:
            continue
        selected.append(row)
        pair_counts[pair] = pair_counts.get(pair, 0) + 1
        motif_counts[motif] = motif_counts.get(motif, 0) + 1
        skeleton_counts[skeleton] = skeleton_counts.get(skeleton, 0) + 1
        if len(selected) >= target:
            break
    return pd.DataFrame(selected)


def reason_summary(rewards: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for reasons in rewards.get("hard_reject_reasons", pd.Series(dtype=str)).fillna("").astype(str):
        for reason in [part for part in reasons.split(";") if part]:
            rows.append(reason)
    if not rows:
        return pd.DataFrame(columns=["hard_reject_reason", "count"])
    return (
        pd.Series(rows)
        .value_counts()
        .rename_axis("hard_reject_reason")
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )


def group_summary(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=columns + ["count"])
    return frame.groupby(columns, dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)


def apply_proxy_runtime(full_proxy: bool) -> None:
    if full_proxy:
        reward.HORIZONS = [8, 24]
        reward.CONTROL_VARIANTS = ["one_bar_lag", "stale_168h", "time_shuffle"]
        reward.CONTROL_DOMINANCE_VARIANTS = ["one_bar_lag", "stale_168h", "time_shuffle"]
        reward.LAG_STALE_VARIANTS = ["one_bar_lag", "stale_168h"]
        reward.SHUFFLE_VARIANTS = ["time_shuffle"]
    else:
        reward.HORIZONS = [24]
        reward.CONTROL_VARIANTS = ["time_shuffle"]
        reward.CONTROL_DOMINANCE_VARIANTS = ["time_shuffle"]
        reward.LAG_STALE_VARIANTS = []
        reward.SHUFFLE_VARIANTS = ["time_shuffle"]


def halving_keep_queue(queue: pd.DataFrame, stage1_rewards: pd.DataFrame, keep_rows: int) -> pd.DataFrame:
    if stage1_rewards.empty or keep_rows <= 0 or keep_rows >= len(queue):
        return queue.copy()
    ranked = stage1_rewards.copy()
    if "hard_reject" in ranked.columns:
        hard = ranked["hard_reject"].astype(bool)
        soft = ranked[~hard].copy()
        if soft.shape[0] >= max(1, keep_rows // 4):
            ranked = soft
    ranked = ranked.sort_values(
        ["proxy_selectable", "proxy_strict_pass", "proxy_score", "min_oos_floor_sortino", "recent_sortino"],
        ascending=[False, False, False, False, False],
    )
    keep_ids = ranked["blueprint_id"].dropna().astype(str).head(keep_rows).tolist()
    if not keep_ids:
        keep_ids = stage1_rewards["blueprint_id"].dropna().astype(str).head(keep_rows).tolist()
    keep_set = set(keep_ids)
    return queue[queue["blueprint_id"].astype(str).isin(keep_set)].copy()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE))
    parser.add_argument("--runtime", default=str(DEFAULT_RUNTIME))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--candidate-cap", type=int, default=0)
    parser.add_argument("--hours-per-split", type=int, default=720)
    parser.add_argument("--train-hours-per-split", type=int, default=0)
    parser.add_argument("--orientation-extension-hours", type=int, default=0)
    parser.add_argument("--cost-bps", type=float, default=5.0)
    parser.add_argument("--checkpoint-every", type=int, default=16)
    parser.add_argument("--select-target", type=int, default=256)
    parser.add_argument("--pair-cap", type=int, default=24)
    parser.add_argument("--motif-cap", type=int, default=96)
    parser.add_argument("--skeleton-cap", type=int, default=2)
    parser.add_argument("--successive-halving", action="store_true")
    parser.add_argument("--halving-keep-rows", type=int, default=0)
    args = parser.parse_args()

    queue_path = Path(args.queue)
    runtime = Path(args.runtime)
    report_path = Path(args.report)
    runtime.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    queue = pd.read_csv(queue_path, low_memory=False)
    candidate_cap = args.candidate_cap if args.candidate_cap and args.candidate_cap > 0 else len(queue)
    if candidate_cap > 0:
        queue = queue.head(candidate_cap).copy()
    stage1_manifest: dict[str, Any] = {}
    if args.successive_halving and args.halving_keep_rows > 0 and args.halving_keep_rows < len(queue):
        stage1_runtime = runtime / "stage1_halving"
        apply_proxy_runtime(full_proxy=False)
        stage1_metrics, stage1_errors = reward.evaluate_queue(
            queue,
            args.hours_per_split,
            args.train_hours_per_split,
            args.cost_bps,
            len(queue),
            args.orientation_extension_hours,
            checkpoint_dir=stage1_runtime,
            checkpoint_every=max(args.checkpoint_every, 64),
        )
        stage1_rewards = add_proxy_columns(reward.aggregate_rewards(stage1_metrics))
        kept_queue = halving_keep_queue(queue, stage1_rewards, args.halving_keep_rows)
        stage1_metrics.to_csv(stage1_runtime / "a7v3s9_stage1_split_metrics.csv", index=False)
        stage1_errors.to_csv(stage1_runtime / "a7v3s9_stage1_eval_errors.csv", index=False)
        stage1_rewards.to_csv(stage1_runtime / "a7v3s9_stage1_leaderboard.csv", index=False)
        kept_queue.to_csv(stage1_runtime / "a7v3s9_stage1_kept_queue.csv", index=False)
        stage1_manifest = {
            "enabled": True,
            "stage1_runtime": str(stage1_runtime),
            "stage1_horizons": reward.HORIZONS,
            "stage1_control_variants": reward.CONTROL_VARIANTS,
            "stage1_input_rows": int(queue.shape[0]),
            "stage1_metric_rows": int(stage1_metrics.shape[0]),
            "stage1_reward_rows": int(stage1_rewards.shape[0]),
            "stage1_eval_error_rows": int(stage1_errors.shape[0]),
            "halving_keep_rows_requested": int(args.halving_keep_rows),
            "halving_kept_rows": int(kept_queue.shape[0]),
        }
        write_json(stage1_runtime / "a7v3s9_stage1_halving_manifest.json", stage1_manifest)
        queue = kept_queue
        candidate_cap = len(queue)
    else:
        stage1_manifest = {"enabled": False}

    # Patch the imported reward module for a cheap pre-reward proxy. This keeps the same
    # numeric loader, formula evaluator, label alignment, split logic, and metric code.
    apply_proxy_runtime(full_proxy=True)

    metrics, errors = reward.evaluate_queue(
        queue,
        args.hours_per_split,
        args.train_hours_per_split,
        args.cost_bps,
        candidate_cap,
        args.orientation_extension_hours,
        checkpoint_dir=runtime,
        checkpoint_every=args.checkpoint_every,
    )
    rewards = add_proxy_columns(reward.aggregate_rewards(metrics))
    selected = bounded_select(
        rewards[rewards["proxy_selectable"].astype(bool)].copy(),
        args.select_target,
        args.pair_cap,
        args.motif_cap,
        args.skeleton_cap,
    )

    metrics.to_csv(runtime / "a7v3s9_proxy_split_metrics.csv", index=False)
    errors.to_csv(runtime / "a7v3s9_proxy_eval_errors.csv", index=False)
    rewards.to_csv(runtime / "a7v3s9_proxy_leaderboard.csv", index=False)
    selected.to_csv(runtime / "a7v3s9_proxy_selected_for_reward.csv", index=False)
    reason_summary(rewards).to_csv(runtime / "a7v3s9_proxy_rejection_reason_summary.csv", index=False)
    group_summary(rewards, ["proxy_bucket"]).to_csv(runtime / "a7v3s9_proxy_bucket_summary.csv", index=False)
    group_summary(selected, ["semantic_pair"]).to_csv(runtime / "a7v3s9_selected_pair_summary.csv", index=False)
    group_summary(selected, ["motif"]).to_csv(runtime / "a7v3s9_selected_motif_summary.csv", index=False)

    decision = (
        "PASS_A7V3S9_PREREWARD_PROXY_SELECTED"
        if selected.shape[0] > 0 and errors.empty
        else "HOLD_A7V3S9_PREREWARD_PROXY_NO_SELECTABLE"
    )
    manifest = {
        "stage": "A7V3S9_PREREWARD_OOS_CONTROL_PROXY",
        "generated_at": now_utc(),
        "decision": decision,
        "queue": str(queue_path),
        "runtime": str(runtime),
        "queue_rows": int(queue.shape[0]),
        "candidate_cap": int(candidate_cap),
        "successive_halving": stage1_manifest,
        "hours_per_split": int(args.hours_per_split),
        "proxy_horizons": reward.HORIZONS,
        "proxy_control_variants": reward.CONTROL_VARIANTS,
        "metric_rows": int(metrics.shape[0]),
        "reward_rows": int(rewards.shape[0]),
        "eval_error_rows": int(errors.shape[0]),
        "strict_pass_rows": int(rewards["proxy_strict_pass"].sum()) if not rewards.empty else 0,
        "near_miss_rows": int(rewards["proxy_near_miss"].sum()) if not rewards.empty else 0,
        "selected_rows": int(selected.shape[0]),
        "selected_unique_blueprints": int(selected["blueprint_id"].nunique()) if not selected.empty else 0,
        "selected_semantic_pair_count": int(selected["semantic_pair"].nunique()) if not selected.empty else 0,
        "selected_motif_count": int(selected["motif"].nunique()) if not selected.empty else 0,
        "output_selected_queue": str(runtime / "a7v3s9_proxy_selected_for_reward.csv"),
        "authorizes_bounded_reward_smoke": bool(selected.shape[0] > 0 and errors.empty),
        "authorizes_full_reward_wave": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(runtime / "a7v3s9_proxy_manifest.json", manifest)

    report_path.write_text(
        "\n".join(
            [
                "# CRYPTO A7V3S9 Pre-Reward OOS/Control Proxy 20260614",
                "",
                f"Decision: `{decision}`",
                "",
                "A7V3S9 is a cheap pre-reward gate. It reuses the reward numeric loader, evaluator, label alignment, split logic, and metrics, but only evaluates horizons 8h/24h and control variants one_bar_lag/stale_168h/time_shuffle.",
                "",
                "It is not alpha proof and does not authorize shadow, paper, live, or full reward continuation.",
                "",
                "## Counts",
                "",
                f"- queue_rows: `{manifest['queue_rows']}`",
                f"- candidate_cap: `{manifest['candidate_cap']}`",
                f"- metric_rows: `{manifest['metric_rows']}`",
                f"- reward_rows: `{manifest['reward_rows']}`",
                f"- eval_error_rows: `{manifest['eval_error_rows']}`",
                f"- strict_pass_rows: `{manifest['strict_pass_rows']}`",
                f"- near_miss_rows: `{manifest['near_miss_rows']}`",
                f"- selected_rows: `{manifest['selected_rows']}`",
                f"- selected_semantic_pair_count: `{manifest['selected_semantic_pair_count']}`",
                f"- selected_motif_count: `{manifest['selected_motif_count']}`",
                "",
                "## Bucket Summary",
                "",
                md_table(pd.read_csv(runtime / "a7v3s9_proxy_bucket_summary.csv"), 20),
                "",
                "## Selected Pair Summary",
                "",
                md_table(pd.read_csv(runtime / "a7v3s9_selected_pair_summary.csv"), 30),
                "",
                "## Selected Motif Summary",
                "",
                md_table(pd.read_csv(runtime / "a7v3s9_selected_motif_summary.csv"), 30),
                "",
                "## Rejection Reasons",
                "",
                md_table(pd.read_csv(runtime / "a7v3s9_proxy_rejection_reason_summary.csv"), 30),
                "",
                "## Top Selected",
                "",
                md_table(
                    selected[
                        [
                            col
                            for col in [
                                "blueprint_id",
                                "semantic_pair",
                                "motif",
                                "horizon_h",
                                "proxy_bucket",
                                "proxy_score",
                                "recent_sortino",
                                "min_oos_floor_sortino",
                                "stress_floor_sortino",
                                "recent_shuffle_control_ratio",
                                "oos_control_dominated_count",
                                "oos_lag_stale_dominated_count",
                                "expression",
                            ]
                            if col in selected.columns
                        ]
                    ],
                    30,
                ),
                "",
                "## Boundary",
                "",
                "Only `proxy_pass` and bounded `proxy_near_miss` rows may enter the expensive reward gate. Full continuation of unfiltered A7V3S8-style queues remains blocked.",
                "",
                "## Manifest",
                "",
                "```json",
                json.dumps(manifest, indent=2, sort_keys=True),
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
