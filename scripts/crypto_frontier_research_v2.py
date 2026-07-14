from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_IMPORT_ROOT = Path(__file__).resolve().parents[1]
if str(_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_IMPORT_ROOT))

from alphafactory_crypto.frontier_v2.arena import (
    evaluate_common_bridge,
    long_only_topk_momentum_weights,
    one_over_n_weights,
    paired_increment,
)
from alphafactory_crypto.frontier_v2.deepdow_v023 import run_deepdow_native
from alphafactory_crypto.frontier_v2.qlib_v097 import run_qlib_native
from alphafactory_crypto.frontier_v2.release import (
    canonical_sha256,
    load_development_daily_panel,
    preflight_external_release,
    sha256_file,
)


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "config/crypto_frontier_research_v2.json"
RUN_ROOT = REPO / "runtime/crypto_frontier_research_v2_20260713"
PREPARED_PANEL = RUN_ROOT / "development_daily_panel.parquet"
SUMMARY = RUN_ROOT / "frontier_research_summary.json"
ARTIFACT_INDEX = RUN_ROOT / "artifact_index.csv"
FROZEN_MANIFEST = RUN_ROOT / "frozen_experiment_manifest.json"
EXECUTION_IDENTITY = RUN_ROOT / "execution_identity_supersession.json"


def _repo_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value) if math.isfinite(float(value)) else None
    if isinstance(value, (pd.Timestamp, Path)):
        return str(value)
    return value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_json_safe(value), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _weights_long(weights: pd.DataFrame, system_id: str) -> pd.DataFrame:
    frame = weights.stack().rename("weight").reset_index()
    frame.columns = ["date", "symbol", "weight"]
    frame["system_id"] = system_id
    return frame


def _frontier_map() -> list[dict[str, Any]]:
    return [
        {
            "system_id": "MICROSOFT_QLIB_V097_ALPHA158",
            "paradigm": "supervised cross-sectional forecasting to stateful TopK portfolio",
            "native_input": "daily OHLCV/VWAP",
            "target_horizon": "cross-sectionally normalized close[t+2]/close[t+1]-1",
            "model_search": "fixed Qlib LGBModel; train/valid early stopping",
            "portfolio": "TopkDropoutStrategy orders, cash and retained holdings",
            "native_evaluator": "IC/RankIC plus benchmark-excess order backtest",
            "bridge": "native position weights, delayed one-day return, 5bp L1 turnover",
            "version": "v0.9.7@da920b7f954f48ab1bb64117c976710de198373e",
            "status_before": "NOT_REPRODUCED",
            "v2_disposition": "REPRODUCE_NATIVE_WITH_CRYPTO_ADAPTATIONS",
        },
        {
            "system_id": "DEEPDOW_V023_KEYNESNET",
            "paradigm": "direct differentiable multi-asset portfolio learning",
            "native_input": "channels x lookback x fixed assets tensor",
            "target_horizon": "future five-day return tensor after one-day execution gap",
            "model_search": "fixed KeynesNet and upstream Run; no HPO",
            "portfolio": "SoftmaxAllocator long-only fully-invested weights",
            "native_evaluator": "per-sample five-day buy-and-hold portfolio losses",
            "bridge": "native weights, delayed first-day return, 5bp L1 turnover",
            "version": "v0.2.3@384e18acc17c982ac5a4362187b348bdbdb07b98",
            "status_before": "NOT_REPRODUCED",
            "v2_disposition": "REPRODUCE_NATIVE_FRAMEWORK_RUN",
        },
        {
            "system_id": "DEEP_MOMENTUM_NETWORK_2019",
            "paradigm": "shared temporal position model and direct Sharpe",
            "native_input": "1/20/63/126/252-day features and long sequences",
            "target_horizon": "next-day volatility-scaled strategy return",
            "model_search": "validation, early stopping and 50-run random search",
            "portfolio": "volatility-scaled long-short positions",
            "native_evaluator": "cost-adjusted portfolio Sharpe",
            "bridge": "not opened in v2",
            "version": "arXiv:1904.04912v3",
            "status_before": "SCOPED_REIMPLEMENTATION",
            "v2_disposition": "DATA_INCOMPATIBLE_NATIVE_252D_HISTORY",
        },
        {
            "system_id": "G_RESEARCH_CRYPTO_FORECASTING",
            "paradigm": "short-horizon residualized supervised forecasting",
            "native_input": "minute crypto bars across assets",
            "target_horizon": "15-minute market-residualized return",
            "model_search": "fixed competition-style supervised learners",
            "portfolio": "no native execution portfolio",
            "native_evaluator": "asset-weighted forecast correlation",
            "bridge": "requires qualified minute release",
            "version": "G-Research Crypto Forecasting competition contract",
            "status_before": "MAP_ONLY",
            "v2_disposition": "DATA_INCOMPATIBLE_NATIVE_MINUTE_RELEASE",
        },
        {
            "system_id": "DEEPLOB",
            "paradigm": "event-time multi-level order-book representation",
            "native_input": "multi-level L2 states",
            "target_horizon": "future mid-price movement by events",
            "model_search": "CNN/Inception plus recurrent temporal model",
            "portfolio": "requires execution bridge",
            "native_evaluator": "classification plus execution simulation",
            "bridge": "not expressible with top-of-book coverage",
            "version": "official DeepLOB research line",
            "status_before": "DATA_INCOMPATIBLE",
            "v2_disposition": "DATA_INCOMPATIBLE_MULTI_LEVEL_L2",
        },
    ]


def prepare() -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if not all(config["boundaries"].values()):
        raise PermissionError("frontier v2 boundary drift")
    started = time.perf_counter()
    daily, evidence = load_development_daily_panel(REPO, config)
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    daily.to_parquet(PREPARED_PANEL, index=False)
    _write_json(RUN_ROOT / "release_evidence.json", evidence.to_dict())
    pd.DataFrame(_frontier_map()).to_csv(RUN_ROOT / "external_frontier_map.csv", index=False, lineterminator="\n")
    supersession = {
        "decision_id": "CRYPTO_FRONTIER_V2_SUPERSESSION_20260713",
        "supersedes_research_id": config["supersedes"]["research_id"],
        "historical_assets_immutable": True,
        "changes": [
            {
                "old_claim": "real_end_to_end_reproductions=2",
                "new_status": "0_AT_START_OF_V2",
                "reason": "prior Qlib and DMN paths were scoped manual reimplementations without upstream parity",
            },
            {
                "old_claim": "data is the weakest or unique bottleneck",
                "new_status": "INSUFFICIENT_EVIDENCE",
                "reason": "no matched data control and no direct-allocation paradigm had been run",
            },
            {
                "old_claim": "native evaluators reproduced",
                "new_status": "COMMON_BRIDGE_ONLY_SCOPED",
                "reason": "prior native rows reused the internal generic evaluator",
            },
        ],
        "preserved_narrow_findings": [
            "formula/rank-weight hourly Main has rare reliable gross edge in the audited cached search rows",
            "blocker-directed repair did not beat matched random controls in Epoch-2B",
            "simple fixed native aggTrades benchmarks produced no admitted net row",
            "DeepLOB remains data-incompatible without multi-level L2",
        ],
    }
    _write_json(RUN_ROOT / "supersession_decision.json", supersession)
    frozen = {
        "status": "CRYPTO_FRONTIER_V2_DESIGN_FROZEN",
        "research_id": config["research_id"],
        "repo_sha": _repo_sha(),
        "config_sha256": sha256_file(CONFIG),
        "release_evidence_sha256": sha256_file(RUN_ROOT / "release_evidence.json"),
        "development_panel_sha256": sha256_file(PREPARED_PANEL),
        "implementation_hashes": {
            "release": sha256_file(REPO / "alphafactory_crypto/frontier_v2/release.py"),
            "arena": sha256_file(REPO / "alphafactory_crypto/frontier_v2/arena.py"),
            "qlib": sha256_file(REPO / "alphafactory_crypto/frontier_v2/qlib_v097.py"),
            "deepdow": sha256_file(REPO / "alphafactory_crypto/frontier_v2/deepdow_v023.py"),
            "runner": sha256_file(Path(__file__)),
        },
        "budget": config["budget"],
        "boundaries": config["boundaries"],
        "performance_started": False,
        "challenge_read": False,
        "forward_read": False,
        "candidate_promotion": False,
        "runtime_seconds": time.perf_counter() - started,
    }
    _write_json(RUN_ROOT / "frozen_experiment_manifest.json", frozen)
    return frozen


def _persist_native_results(qlib_result: Any, deepdow_result: Any) -> None:
    qlib_root = RUN_ROOT / "qlib_v097"
    qlib_root.mkdir(parents=True, exist_ok=True)
    _write_json(qlib_root / "reproduction_manifest.json", qlib_result.manifest)
    qlib_result.predictions.to_parquet(qlib_root / "native_predictions.parquet", index=False)
    pd.concat(
        [
            _weights_long(qlib_result.challenger_weights, "QLIB_V097_NATIVE_FULL"),
            _weights_long(qlib_result.control_weights, "QLIB_V097_NATIVE_13_FEATURE_CONTROL"),
        ],
        ignore_index=True,
    ).to_parquet(qlib_root / "native_position_weights.parquet", index=False)
    qlib_result.native_metrics.to_csv(qlib_root / "native_metrics.csv", index=False, lineterminator="\n")
    qlib_result.native_reports.to_parquet(qlib_root / "native_backtest_report.parquet", index=False)
    qlib_result.training_ledger.to_csv(qlib_root / "training_ledger.csv", index=False, lineterminator="\n")

    deepdow_root = RUN_ROOT / "deepdow_v023"
    deepdow_root.mkdir(parents=True, exist_ok=True)
    _write_json(deepdow_root / "reproduction_manifest.json", deepdow_result.manifest)
    pd.concat(
        [
            _weights_long(deepdow_result.challenger_weights, "DEEPDOW_V023_KEYNESNET_FLOW"),
            _weights_long(deepdow_result.control_weights, "DEEPDOW_V023_ASSET_ROTATED_FLOW_CONTROL"),
        ],
        ignore_index=True,
    ).to_parquet(deepdow_root / "native_position_weights.parquet", index=False)
    deepdow_result.per_seed_weights.to_parquet(deepdow_root / "per_seed_weights.parquet", index=False)
    deepdow_result.native_metrics.to_csv(deepdow_root / "native_metrics.csv", index=False, lineterminator="\n")
    deepdow_result.training_ledger.to_csv(deepdow_root / "training_ledger.csv", index=False, lineterminator="\n")


def run() -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if not PREPARED_PANEL.exists():
        prepare()
    daily = pd.read_parquet(PREPARED_PANEL)
    daily["date"] = pd.to_datetime(daily.date, utc=True)
    if set(daily.data_role.unique()) != {"DEVELOPMENT"}:
        raise PermissionError("prepared panel role drift")
    started = time.perf_counter()
    qlib_result = run_qlib_native(daily, config["qlib"], config["splits"], RUN_ROOT)
    deepdow_result = run_deepdow_native(daily, config["deepdow"], config["splits"])
    _persist_native_results(qlib_result, deepdow_result)

    common_dates = qlib_result.challenger_weights.index.intersection(deepdow_result.challenger_weights.index)
    systems = {
        "INTERNAL_LONG_ONLY_20D_MOMENTUM": long_only_topk_momentum_weights(daily, common_dates),
        "QLIB_V097_NATIVE_FULL": qlib_result.challenger_weights.loc[common_dates],
        "QLIB_V097_NATIVE_13_FEATURE_CONTROL": qlib_result.control_weights.loc[common_dates],
        "DEEPDOW_V023_KEYNESNET_FLOW": deepdow_result.challenger_weights.loc[common_dates],
        "DEEPDOW_V023_ASSET_ROTATED_FLOW_CONTROL": deepdow_result.control_weights.loc[common_dates],
        "ONE_OVER_N": one_over_n_weights(daily, common_dates),
    }
    arena_cfg = config["arena"]
    metrics_rows: list[dict[str, Any]] = []
    path_frames: list[pd.DataFrame] = []
    paths: dict[str, pd.DataFrame] = {}
    for ordinal, (system_id, weights) in enumerate(systems.items()):
        metrics, path = evaluate_common_bridge(
            daily,
            weights,
            system_id=system_id,
            cost_bps_per_unit_turnover=arena_cfg["common_cost_bps_per_unit_turnover"],
            annualization=arena_cfg["annualization"],
            block_days=arena_cfg["paired_block_bootstrap_days"],
            bootstrap_samples=arena_cfg["paired_bootstrap_samples"],
            bootstrap_seed=20260713 + ordinal,
        )
        metrics_rows.append(metrics.to_dict())
        path["system_id"] = system_id
        path_frames.append(path)
        paths[system_id] = path
    metrics_frame = pd.DataFrame(metrics_rows)
    paths_frame = pd.concat(path_frames, ignore_index=True)
    paired = pd.DataFrame(
        [
            paired_increment(
                paths["QLIB_V097_NATIVE_FULL"],
                paths["QLIB_V097_NATIVE_13_FEATURE_CONTROL"],
                challenger_id="QLIB_V097_NATIVE_FULL",
                control_id="QLIB_V097_NATIVE_13_FEATURE_CONTROL",
                block_days=arena_cfg["paired_block_bootstrap_days"],
                bootstrap_samples=arena_cfg["paired_bootstrap_samples"],
            ),
            paired_increment(
                paths["DEEPDOW_V023_KEYNESNET_FLOW"],
                paths["DEEPDOW_V023_ASSET_ROTATED_FLOW_CONTROL"],
                challenger_id="DEEPDOW_V023_KEYNESNET_FLOW",
                control_id="DEEPDOW_V023_ASSET_ROTATED_FLOW_CONTROL",
                block_days=arena_cfg["paired_block_bootstrap_days"],
                bootstrap_samples=arena_cfg["paired_bootstrap_samples"],
                seed=20260714,
            ),
        ]
    )
    metrics_frame.to_csv(RUN_ROOT / "arena_common_metrics.csv", index=False, lineterminator="\n")
    paths_frame.to_parquet(RUN_ROOT / "arena_common_paths.parquet", index=False)
    paired.to_csv(RUN_ROOT / "paired_component_comparisons.csv", index=False, lineterminator="\n")
    returns = paths_frame.pivot(index="date", columns="system_id", values="net_return")
    returns.corr().to_csv(RUN_ROOT / "arena_behaviour_correlation.csv", lineterminator="\n")

    gate_rows = []
    for row in paired.to_dict(orient="records"):
        passed = bool(row["paired_net_increment_lcb_95"] > 0)
        gate_rows.append(
            {
                **row,
                "economic_migration_gate": "PASS" if passed else "HOLD",
                "candidate_promotion": False,
                "conclusion": "DEVELOPMENT_INCREMENT_SUPPORTED" if passed else "INSUFFICIENT_EVIDENCE",
            }
        )
    pd.DataFrame(gate_rows).to_csv(RUN_ROOT / "component_migration_decisions.csv", index=False, lineterminator="\n")

    layer_gap = [
        {
            "layer": "data_representation",
            "old_capability": "hourly Main plus scoped daily aggregation",
            "v2_capability": "hash-verified development-only fixed core10 daily tensor with release lineage",
            "remaining_gap": "core12 fixed axis missing BTC March and AVAX April; multi-level L2 and qualified minute data absent",
            "attribution": "NARROW_DATA_BLOCKERS_ONLY",
        },
        {
            "layer": "target_and_horizon",
            "old_capability": "single delayed one-day label",
            "v2_capability": "coexisting Qlib one-day normalized label and DeepDow five-day future return tensor",
            "remaining_gap": "no generic target registry for event-time or residualized minute labels",
            "attribution": "EXPRESSIVITY_GAP_CLOSED_FOR_MULTI_STEP_DAILY",
        },
        {
            "layer": "model_and_search",
            "old_capability": "formula/program search plus scoped manual ML canaries",
            "v2_capability": "pinned upstream supervised and direct-allocation adapters with separate fit ledgers",
            "remaining_gap": "no long-history transformer or event-time LOB model",
            "attribution": "MODEL_MONOCULTURE_REJECTED",
        },
        {
            "layer": "portfolio_mapping",
            "old_capability": "mostly cross-sectional rank weights",
            "v2_capability": "native stateful TopK holdings and direct neural long-only weights retained into bridge",
            "remaining_gap": "execution-aware shorting and inventory state remain absent",
            "attribution": "DIRECT_PORTFOLIO_CONTRACT_MIGRATED",
        },
        {
            "layer": "evaluator",
            "old_capability": "native label applied to a generic evaluator",
            "v2_capability": "native evaluator artifacts kept distinct from a one-day common economic bridge",
            "remaining_gap": "holdout is one development month and cannot support promotion",
            "attribution": "NATIVE_BRIDGE_SEPARATION_MIGRATED",
        },
    ]
    pd.DataFrame(layer_gap).to_csv(RUN_ROOT / "layer_gap_attribution.csv", index=False, lineterminator="\n")

    architecture_decision = {
        "decision_id": "ADR_CRYPTO_FRONTIER_MULTI_PARADIGM_ARENA_V2",
        "status": "ACCEPTED_DEVELOPMENT_ONLY",
        "decision": "replace the single formula-score pipeline assumption with adapter-neutral ForecastArtifact and PortfolioArtifact contracts, retain each native evaluator, and compare only through an explicit common bridge",
        "migrated_components": [
            "multi-step future-return tensor target contract",
            "direct portfolio weight artifact",
            "stateful native portfolio position artifact",
            "native-versus-bridge evaluator separation",
            "hash-verified development-only external release entry",
        ],
        "economic_selection": "NO_CHALLENGER_PROMOTED",
        "reason": "architecture result B is achieved by making a previously inexpressible direct-allocation paradigm runnable; economic increments remain subject to paired development evidence",
        "forbidden_conclusions": [
            "Qlib is ineffective",
            "DeepDow is ineffective",
            "data is the unique remaining bottleneck",
            "development holdout is OOS promotion evidence",
        ],
    }
    _write_json(RUN_ROOT / "architecture_decision.json", architecture_decision)

    summary = {
        "status": "CRYPTO_FRONTIER_RESEARCH_COMPLETED",
        "research_id": config["research_id"],
        "completion_route": "B",
        "real_native_reproductions": 2,
        "native_reproduction_ids": [config["qlib"]["source_id"], config["deepdow"]["source_id"]],
        "multi_paradigm_arena_systems": list(systems),
        "matched_controls": 2,
        "architecture_components_migrated": len(architecture_decision["migrated_components"]),
        "economic_components_promoted": 0,
        "data_only_bottleneck_status": "INSUFFICIENT_EVIDENCE",
        "narrow_data_blockers": [
            "DeepLOB native input requires multi-level L2",
            "full 2019 DMN/long-history transformer requires unavailable 252-day history",
            "G-Research native target requires a qualified minute release",
            "exact fixed core12 direct-allocation tensor is unavailable without filling two missing symbol-months",
        ],
        "release_entry_status": "IMPLEMENTED_HASH_AND_PIT_GATED",
        "development_only": True,
        "challenge_read": False,
        "forward_read": False,
        "candidate_promotion": False,
        "cross_sprint_adaptive_memory": False,
        "repo_sha_at_run": _repo_sha(),
        "config_sha256": sha256_file(CONFIG),
        "paired_component_results": gate_rows,
        "runtime_seconds": time.perf_counter() - started,
    }
    _write_json(SUMMARY, summary)
    _build_artifact_index()
    return summary


def _is_volatile_execution_evidence(path: Path) -> bool:
    relative = path.relative_to(RUN_ROOT)
    return (
        relative.name.startswith("runner.")
        or relative.name in {"check_result.json", "seal_result.json"}
        or relative.parts[0] in {"mlruns", "tensorboard"}
    )


def _build_artifact_index() -> dict[str, Any]:
    records = []
    for path in sorted(RUN_ROOT.rglob("*")):
        if not path.is_file() or path == ARTIFACT_INDEX or _is_volatile_execution_evidence(path):
            continue
        records.append(
            {
                "artifact": path.relative_to(REPO).as_posix(),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    pd.DataFrame(records).to_csv(ARTIFACT_INDEX, index=False, lineterminator="\n")
    return {"artifacts_sealed": len(records), "bundle_sha256": canonical_sha256(records)}


def check() -> dict[str, Any]:
    if not SUMMARY.exists() or not ARTIFACT_INDEX.exists() or not EXECUTION_IDENTITY.exists():
        raise FileNotFoundError("run frontier v2 before check")
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if summary["status"] != "CRYPTO_FRONTIER_RESEARCH_COMPLETED":
        raise RuntimeError("frontier status is not complete")
    if summary["real_native_reproductions"] < 2 or len(summary["multi_paradigm_arena_systems"]) < 6:
        raise RuntimeError("frontier result responsibility not met")
    for flag in ("challenge_read", "forward_read", "candidate_promotion", "cross_sprint_adaptive_memory"):
        if summary[flag]:
            raise PermissionError(f"frozen boundary violated: {flag}")
    frozen = json.loads(FROZEN_MANIFEST.read_text(encoding="utf-8"))
    identity = json.loads(EXECUTION_IDENTITY.read_text(encoding="utf-8"))
    if identity["status"] != "ACCEPTED_PRE_RUN_OPERATIONAL_SUPERSESSION":
        raise RuntimeError("execution identity supersession is not accepted")
    if identity["research_semantics_changed"]:
        raise RuntimeError("execution identity reports a semantic experiment change")
    original = identity["original_frozen_manifest"]
    actual = identity["actual_run_identity"]
    if sha256_file(FROZEN_MANIFEST) != original["sha256"]:
        raise RuntimeError("original frozen manifest drift")
    if frozen["config_sha256"] != original["config_sha256"]:
        raise RuntimeError("original frozen config identity drift")
    current_config_sha = sha256_file(CONFIG)
    if summary["config_sha256"] != current_config_sha or actual["config_sha256"] != current_config_sha:
        raise RuntimeError("run summary/current config/execution identity mismatch")
    implementation_paths = {
        "arena": REPO / "alphafactory_crypto/frontier_v2/arena.py",
        "deepdow": REPO / "alphafactory_crypto/frontier_v2/deepdow_v023.py",
        "qlib": REPO / "alphafactory_crypto/frontier_v2/qlib_v097.py",
        "release": REPO / "alphafactory_crypto/frontier_v2/release.py",
    }
    for name, path in implementation_paths.items():
        if sha256_file(path) != actual["implementation_hashes"][name]:
            raise RuntimeError(f"actual run implementation drift: {name}")
    if actual["implementation_hashes"]["runner"] != frozen["implementation_hashes"]["runner"]:
        raise RuntimeError("actual run runner is not chained to the original frozen runner")
    post_run = identity["post_run_verification_code"]
    if sha256_file(Path(__file__)) != post_run["runner_sha256"]:
        raise RuntimeError("post-run verification runner drift")
    if sha256_file(REPO / "scripts/run_crypto_frontier_research_v2.ps1") != post_run["wrapper_sha256"]:
        raise RuntimeError("post-run verification wrapper drift")
    if datetime.fromisoformat(actual["config_last_write_time"]) >= datetime.fromisoformat(actual["run_started_at"]):
        raise RuntimeError("config operational supersession was not fixed before run")
    if datetime.fromisoformat(actual["qlib_last_write_time"]) >= datetime.fromisoformat(actual["run_started_at"]):
        raise RuntimeError("Qlib operational supersession was not fixed before run")
    for flag in ("candidate_promotion", "forward_read", "cross_sprint_adaptive_memory"):
        if identity[flag]:
            raise PermissionError(f"execution identity boundary violated: {flag}")
    index = pd.read_csv(ARTIFACT_INDEX)
    mismatches = []
    for row in index.itertuples():
        path = REPO / row.artifact
        if not path.exists() or sha256_file(path) != row.sha256:
            mismatches.append(row.artifact)
    if mismatches:
        raise RuntimeError(f"artifact drift: {mismatches}")
    for reproduction in ("qlib_v097", "deepdow_v023"):
        manifest = json.loads((RUN_ROOT / reproduction / "reproduction_manifest.json").read_text(encoding="utf-8"))
        if manifest["classification"] != "NATIVE_REPRODUCED":
            raise RuntimeError(f"native reproduction check failed: {reproduction}")
    result = {
        "status": "CRYPTO_FRONTIER_RESEARCH_CHECK_PASSED",
        "artifacts_verified": len(index),
        "native_reproductions": summary["real_native_reproductions"],
        "arena_systems": len(summary["multi_paradigm_arena_systems"]),
        "frozen_boundaries_intact": True,
        "execution_identity_verified": True,
    }
    _write_json(RUN_ROOT / "check_result.json", result)
    return result


def ingress_preflight(manifest_path: Path) -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    return preflight_external_release(manifest_path, config["external_release_entry"])


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("prepare")
    subparsers.add_parser("run")
    subparsers.add_parser("seal")
    subparsers.add_parser("check")
    ingress = subparsers.add_parser("ingress-preflight")
    ingress.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare()
    elif args.command == "run":
        result = run()
    elif args.command == "seal":
        result = _build_artifact_index()
    elif args.command == "check":
        result = check()
    else:
        result = ingress_preflight(args.manifest)
    print(json.dumps(_json_safe(result), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
