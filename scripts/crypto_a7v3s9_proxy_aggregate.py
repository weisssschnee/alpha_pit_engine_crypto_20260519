from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.evaluation_access import (
    EvaluationAccessViolation,
    assert_candidate_feedback_columns_allowed,
)
from scripts.crypto_a7v3s9_prereward_oos_control_proxy import bounded_select, group_summary, md_table, reason_summary


DEFAULT_RUN_ROOT = Path(
    r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s9_prereward_oos_control_proxy_20260614"
)
DEFAULT_RUNTIME = Path(
    r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s9_prereward_oos_control_proxy_aggregate_20260614"
)
DEFAULT_REPORT = Path(
    r"D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\reports\CRYPTO_A7V3S9_PREREWARD_OOS_CONTROL_PROXY_AGGREGATE_20260614.md"
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception:
        return pd.DataFrame()


def collect(run_root: Path, filename: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in sorted(run_root.glob(f"shards/*/proxy_runtime/{filename}")):
        frame = read_csv(path)
        if frame.empty:
            continue
        shard_id = path.parts[-3]
        frame.insert(0, "proxy_shard_id", shard_id)
        frame.insert(1, "source_file", str(path))
        frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def collect_manifests(run_root: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in sorted(run_root.glob("shards/*/proxy_runtime/a7v3s9_proxy_manifest.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["proxy_shard_id"] = path.parts[-3]
        payload["source_file"] = str(path)
        rows.append(payload)
    return pd.DataFrame(rows)


def expected_shard_count(run_root: Path, manifest_count: int) -> int:
    shard_plan = run_root / "a7v3s9_proxy_shard_plan.csv"
    if shard_plan.exists():
        return int(len(pd.read_csv(shard_plan)))
    for prepare_manifest in sorted(run_root.glob("*prepare_manifest.json")):
        try:
            payload = json.loads(prepare_manifest.read_text(encoding="utf-8"))
        except Exception:
            continue
        if "shard_count" in payload:
            return int(payload["shard_count"])
    status_path = run_root / "a7fast2_status.csv"
    if status_path.exists():
        status = read_csv(status_path)
        if not status.empty and "shard_id" in status.columns:
            return int(status["shard_id"].nunique())
    return int(manifest_count)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--select-target", type=int, default=256)
    parser.add_argument("--pair-cap", type=int, default=24)
    parser.add_argument("--motif-cap", type=int, default=96)
    parser.add_argument("--skeleton-cap", type=int, default=2)
    args = parser.parse_args()

    runtime = args.runtime
    runtime.mkdir(parents=True, exist_ok=True)
    manifests = collect_manifests(args.run_root)
    leaderboard = collect(args.run_root, "a7v3s9_proxy_leaderboard.csv")
    errors = collect(args.run_root, "a7v3s9_proxy_eval_errors.csv")
    selected_local = collect(args.run_root, "a7v3s9_proxy_selected_for_reward.csv")

    selectable = leaderboard[leaderboard.get("proxy_selectable", pd.Series(dtype=bool)).astype(str).str.lower().isin(["true", "1"])].copy()
    for column in ["proxy_score", "min_oos_floor_sortino", "recent_sortino"]:
        if column in selectable.columns:
            selectable[column] = pd.to_numeric(selectable[column], errors="coerce")
    selected = bounded_select(selectable, args.select_target, args.pair_cap, args.motif_cap, args.skeleton_cap)
    feedback_guard: dict[str, Any] = {}
    try:
        assert_candidate_feedback_columns_allowed(
            selected.columns,
            context="a7v3s9.aggregate_selected_for_reward",
        )
    except EvaluationAccessViolation as exc:
        feedback_guard = exc.as_dict()
        selected = selected.head(0).copy()

    leaderboard.to_csv(runtime / "a7v3s9_proxy_leaderboard_all.csv", index=False)
    selected_local.to_csv(runtime / "a7v3s9_proxy_selected_local_concat.csv", index=False)
    selected.to_csv(runtime / "a7v3s9_proxy_selected_for_reward.csv", index=False)
    errors.to_csv(runtime / "a7v3s9_proxy_eval_errors_all.csv", index=False)
    manifests.to_csv(runtime / "a7v3s9_proxy_manifest_summary.csv", index=False)
    reason_summary(leaderboard).to_csv(runtime / "a7v3s9_proxy_rejection_reason_summary.csv", index=False)
    group_summary(leaderboard, ["proxy_bucket"]).to_csv(runtime / "a7v3s9_proxy_bucket_summary.csv", index=False)
    group_summary(selected, ["semantic_pair"]).to_csv(runtime / "a7v3s9_selected_pair_summary.csv", index=False)
    group_summary(selected, ["motif"]).to_csv(runtime / "a7v3s9_selected_motif_summary.csv", index=False)

    expected_shards = expected_shard_count(args.run_root, manifests.shape[0])
    strict_pass_rows = int(leaderboard.get("proxy_strict_pass", pd.Series(dtype=bool)).astype(str).str.lower().isin(["true", "1"]).sum()) if not leaderboard.empty else 0
    near_miss_rows = int(leaderboard.get("proxy_near_miss", pd.Series(dtype=bool)).astype(str).str.lower().isin(["true", "1"]).sum()) if not leaderboard.empty else 0
    if feedback_guard:
        decision = "HOLD_EVALRESET_SPENT_EVALUATION_FEEDBACK_BLOCKED"
    elif manifests.shape[0] == expected_shards and selected.shape[0] > 0 and errors.empty:
        decision = "PASS_A7V3S9_PROXY_AGGREGATE_SELECTED"
    else:
        decision = "HOLD_A7V3S9_PROXY_AGGREGATE_NO_SELECTED_OR_INCOMPLETE"
    manifest = {
        "stage": "A7V3S9_PROXY_AGGREGATE",
        "generated_at": now_utc(),
        "decision": decision,
        "run_root": str(args.run_root),
        "runtime": str(runtime),
        "report": str(args.report),
        "expected_shards": int(expected_shards),
        "manifest_count": int(manifests.shape[0]),
        "leaderboard_rows": int(leaderboard.shape[0]),
        "eval_error_rows": int(errors.shape[0]),
        "strict_pass_rows": strict_pass_rows,
        "near_miss_rows": near_miss_rows,
        "selected_rows": int(selected.shape[0]),
        "selected_unique_blueprints": int(selected["blueprint_id"].nunique()) if not selected.empty and "blueprint_id" in selected else 0,
        "candidate_feedback_guard": feedback_guard or {"status": "PASS"},
        "selected_queue": str(runtime / "a7v3s9_proxy_selected_for_reward.csv"),
        "authorizes_bounded_full_reward": bool(manifests.shape[0] == expected_shards and selected.shape[0] > 0 and errors.empty and not feedback_guard),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(runtime / "a7v3s9_proxy_aggregate_manifest.json", manifest)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        "\n".join(
            [
                "# CRYPTO A7V3S9 Pre-Reward OOS/Control Proxy Aggregate 20260614",
                "",
                f"Decision: `{decision}`",
                "",
                "## Counts",
                "",
                f"- expected_shards: `{manifest['expected_shards']}`",
                f"- manifest_count: `{manifest['manifest_count']}`",
                f"- leaderboard_rows: `{manifest['leaderboard_rows']}`",
                f"- eval_error_rows: `{manifest['eval_error_rows']}`",
                f"- strict_pass_rows: `{manifest['strict_pass_rows']}`",
                f"- near_miss_rows: `{manifest['near_miss_rows']}`",
                f"- selected_rows: `{manifest['selected_rows']}`",
                "",
                "## Bucket Summary",
                "",
                md_table(pd.read_csv(runtime / "a7v3s9_proxy_bucket_summary.csv"), 20),
                "",
                "## Selected Pairs",
                "",
                md_table(pd.read_csv(runtime / "a7v3s9_selected_pair_summary.csv"), 30),
                "",
                "## Selected Motifs",
                "",
                md_table(pd.read_csv(runtime / "a7v3s9_selected_motif_summary.csv"), 30),
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
                "This aggregate can authorize only bounded full reward on the selected proxy queue. It does not authorize alpha proof, shadow, paper, or live.",
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
