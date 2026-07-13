from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from alphafactory_crypto.frontier_arena import (
    behaviour_summary,
    build_alpha158_features,
    build_dmn_features,
    canonical_sha256,
    cross_sectional_unit_gross,
    daily_ic,
    evaluate_weights,
    fit_dmn_ensemble,
    fit_lgbm_ensemble,
    load_daily_panel,
    sha256_file,
    topk_dropout_weights,
    tsmom_weights,
    validate_external_data_contract,
    validate_frontier_config,
)


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "config/crypto_external_frontier_assimilation_v1.json"
RUN_ROOT = REPO / "runtime/crypto_external_frontier_assimilation_20260713"
PREP_MANIFEST = RUN_ROOT / "preparation_manifest.json"
FROZEN_MANIFEST = RUN_ROOT / "frozen_experiment_manifest.json"
SUMMARY = RUN_ROOT / "frontier_assimilation_summary.json"


def repo_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()


def package_versions() -> dict[str, str]:
    import lightgbm
    import sklearn
    import torch

    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "lightgbm": lightgbm.__version__,
        "scikit_learn": sklearn.__version__,
        "torch": torch.__version__,
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def artifact_record(path: Path, role: str, producer: str) -> dict[str, Any]:
    return {
        "artifact": path.relative_to(REPO).as_posix(),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "role": role,
        "producer": producer,
    }


def prepare() -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    validate_frontier_config(config)
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    daily = load_daily_panel(REPO, config)
    alpha, alpha_features = build_alpha158_features(daily, config["qlib_reproduction"]["rolling_windows"])
    dmn, dmn_features = build_dmn_features(daily, config["dmn_reproduction"])
    daily.to_parquet(RUN_ROOT / "daily_observation_panel.parquet", index=False)
    alpha.to_parquet(RUN_ROOT / "alpha158_daily_panel.parquet", index=False)
    dmn.to_parquet(RUN_ROOT / "dmn_daily_panel.parquet", index=False)
    pd.DataFrame(config["frontier_map"]).to_csv(RUN_ROOT / "external_frontier_map.csv", index=False, lineterminator="\n")
    ingress = []
    for contract in config["external_data_contracts"]:
        ingress.append({
            "family": contract["family"],
            "required_schema": "|".join(contract["required_schema"]),
            "compatible_paradigms": "|".join(contract["compatible_paradigms"]),
            "release_status": "AWAITING_EXTERNAL_RELEASE",
            "direct_entrypoint": "python scripts/crypto_external_frontier_assimilation.py ingress-preflight --family FAMILY --schema-json FILE",
        })
    pd.DataFrame(ingress).to_csv(RUN_ROOT / "external_data_ingress_registry.csv", index=False, lineterminator="\n")
    source_paths = sorted({str(path) for path in Path(json.loads((REPO / config["release"]["config"]).read_text())["release_root"]).rglob("part.parquet")})
    manifest = {
        "status": "FRONTIER_ASSIMILATION_INPUTS_PREPARED",
        "experiment_id": "20260713_crypto_frontier_assimilation_001",
        "objective": config["research_objective"],
        "repo_sha_at_preparation": repo_sha(),
        "config_sha256": sha256_file(CONFIG),
        "release_id": config["release"]["release_id"],
        "release_content_sha256": config["release"]["content_sha256"],
        "source_release_files": len(source_paths),
        "daily_rows": int(len(daily)),
        "daily_symbols": int(daily.symbol.nunique()),
        "daily_dates": int(daily.date.nunique()),
        "role_rows": daily.groupby("data_role").size().astype(int).to_dict(),
        "role_dates": daily.groupby("data_role").date.nunique().astype(int).to_dict(),
        "date_range": [str(daily.date.min()), str(daily.date.max())],
        "alpha158_features": alpha_features,
        "dmn_features": dmn_features,
        "performance_started": False,
        "forward_read": False,
        "spent_evaluation_read": False,
        "candidate_promotion": False,
        "cross_sprint_memory_update": False,
        "runtime_seconds": time.perf_counter() - started,
    }
    input_artifacts = [
        artifact_record(RUN_ROOT / "daily_observation_panel.parquet", "PIT_DAILY_OBSERVATION", "prepare"),
        artifact_record(RUN_ROOT / "alpha158_daily_panel.parquet", "QLIB_NATIVE_REPRESENTATION", "prepare"),
        artifact_record(RUN_ROOT / "dmn_daily_panel.parquet", "DMN_NATIVE_REPRESENTATION", "prepare"),
        artifact_record(RUN_ROOT / "external_frontier_map.csv", "EXTERNAL_REFERENCE_MAP", "prepare"),
        artifact_record(RUN_ROOT / "external_data_ingress_registry.csv", "NEW_DATA_DIRECT_ENTRY", "prepare"),
    ]
    manifest["input_artifacts"] = input_artifacts
    manifest["input_bundle_sha256"] = canonical_sha256(input_artifacts)
    write_json(PREP_MANIFEST, manifest)
    return manifest


def freeze() -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    validate_frontier_config(config)
    if not PREP_MANIFEST.exists():
        raise FileNotFoundError("run prepare before freeze")
    prep = json.loads(PREP_MANIFEST.read_text(encoding="utf-8"))
    for artifact in prep["input_artifacts"]:
        path = REPO / artifact["artifact"]
        if sha256_file(path) != artifact["sha256"]:
            raise ValueError(f"prepared input drift: {path}")
    payload = {
        "status": "CRYPTO_EXTERNAL_FRONTIER_ASSIMILATION_DESIGN_FROZEN",
        "experiment_id": prep["experiment_id"],
        "objective": config["research_objective"],
        "repo_sha": repo_sha(),
        "config_sha256": sha256_file(CONFIG),
        "implementation_hashes": {
            "arena_module": sha256_file(REPO / "alphafactory_crypto/frontier_arena.py"),
            "runner": sha256_file(Path(__file__)),
            "tests": sha256_file(REPO / "tests/test_external_frontier_assimilation.py"),
        },
        "input_bundle_sha256": prep["input_bundle_sha256"],
        "input_artifacts": prep["input_artifacts"],
        "release_id": config["release"]["release_id"],
        "release_content_sha256": config["release"]["content_sha256"],
        "roles": config["arena"]["roles"],
        "external_reproductions": [item["source_id"] for item in config["external_sources"]],
        "arena_systems": config["arena"]["systems"],
        "fixed_budget": config["fixed_budget"],
        "qlib_contract": config["qlib_reproduction"],
        "dmn_contract": config["dmn_reproduction"],
        "evaluation_contract": config["arena"],
        "dataset_contract": config["dataset"],
        "package_versions": package_versions(),
        "commands": {
            "prepare": "python scripts/crypto_external_frontier_assimilation.py prepare",
            "freeze": "python scripts/crypto_external_frontier_assimilation.py freeze",
            "run": "python scripts/crypto_external_frontier_assimilation.py run",
            "check": "python scripts/crypto_external_frontier_assimilation.py check",
        },
        "estimated_cost_time": "CPU-only, eight fixed fits, expected under 20 minutes; no paid service",
        "performance_started": False,
        "online_adjustment": False,
        "additional_budget": False,
        "forward_read": False,
        "spent_evaluation_read": False,
        "candidate_promotion": False,
        "cross_sprint_memory_update": False,
    }
    payload["frozen_manifest_sha256"] = canonical_sha256(payload)
    write_json(FROZEN_MANIFEST, payload)
    return payload


def validate_frozen() -> tuple[dict[str, Any], dict[str, Any]]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    validate_frontier_config(config)
    payload = json.loads(FROZEN_MANIFEST.read_text(encoding="utf-8"))
    recorded = payload.pop("frozen_manifest_sha256")
    if canonical_sha256(payload) != recorded:
        raise ValueError("frozen manifest hash drift")
    payload["frozen_manifest_sha256"] = recorded
    if payload["config_sha256"] != sha256_file(CONFIG):
        raise ValueError("frozen config drift")
    for name, path in {
        "arena_module": REPO / "alphafactory_crypto/frontier_arena.py",
        "runner": Path(__file__),
        "tests": REPO / "tests/test_external_frontier_assimilation.py",
    }.items():
        if payload["implementation_hashes"][name] != sha256_file(path):
            raise ValueError(f"frozen implementation drift: {name}")
    for artifact in payload["input_artifacts"]:
        if sha256_file(REPO / artifact["artifact"]) != artifact["sha256"]:
            raise ValueError(f"frozen input drift: {artifact['artifact']}")
    if subprocess.run(["git", "merge-base", "--is-ancestor", payload["repo_sha"], "HEAD"], cwd=REPO).returncode:
        raise ValueError("frozen implementation SHA is not an ancestor of HEAD")
    for flag in ("online_adjustment", "additional_budget", "forward_read", "spent_evaluation_read", "candidate_promotion", "cross_sprint_memory_update"):
        if payload[flag]:
            raise PermissionError(f"frozen manifest records prohibited activity: {flag}")
    return config, payload


def _monthly_stability(paths: pd.DataFrame) -> pd.DataFrame:
    if paths.empty:
        return pd.DataFrame()
    work = paths.copy()
    work["month"] = pd.to_datetime(work.date, utc=True).dt.strftime("%Y-%m")
    result = work.groupby(["system_id", "data_role", "evaluation", "month"], as_index=False).agg(
        net_mean=("net_return", "mean"),
        gross_mean=("gross_return", "mean"),
        turnover_mean=("turnover", "mean"),
        observations=("net_return", "size"),
    )
    return result


def _migration_decisions(
    results: pd.DataFrame,
    behaviour: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    gate = config["arena"]["migration_gate"]
    pairs = [
        ("QLIB_ALPHA158_LIGHTGBM", "QLIB_PRICE_KBAR_CONTROL", "ALPHA158_REPRESENTATION_AND_CS_TARGET"),
        ("DEEP_MOMENTUM_LSTM", "DEEP_MOMENTUM_NO_TURNOVER_CONTROL", "TURNOVER_AWARE_PORTFOLIO_FIRST_OBJECTIVE"),
    ]
    rows = []
    common = results[results.evaluation.eq("COMMON")]
    for challenger, control, component in pairs:
        by_role: dict[str, Any] = {}
        for role in config["arena"]["roles"]:
            left = common[(common.system_id == challenger) & (common.data_role == role)].iloc[0]
            right = common[(common.system_id == control) & (common.data_role == role)].iloc[0]
            by_role[role] = {
                "challenger_net_mean": float(left.net_mean),
                "control_net_mean": float(right.net_mean),
                "net_mean_increment": float(left.net_mean - right.net_mean),
                "challenger_net_lcb": float(left.net_lcb),
                "positive_month_fraction": float(left.positive_month_fraction),
            }
        challenge = by_role["CHALLENGE"]
        correlation = float(behaviour.loc[challenger, "INTERNAL_FORMULA_20D_CS_MOMENTUM"])
        passed = bool(
            challenge["challenger_net_lcb"] > 0
            and challenge["positive_month_fraction"] >= gate["challenge_positive_month_fraction_min"]
            and all(by_role[role]["net_mean_increment"] > 0 for role in config["arena"]["roles"])
            and abs(correlation) <= gate["max_abs_behaviour_correlation_to_internal"]
        )
        rows.append({
            "component": component,
            "challenger": challenger,
            "matched_control": control,
            "development_net_mean_increment": by_role["DEVELOPMENT"]["net_mean_increment"],
            "challenge_net_mean_increment": challenge["net_mean_increment"],
            "challenge_net_lcb": challenge["challenger_net_lcb"],
            "challenge_positive_month_fraction": challenge["positive_month_fraction"],
            "behaviour_correlation_to_internal": correlation,
            "migration_gate_passed": passed,
            "decision": "MIGRATE_AS_INTERNAL_CHALLENGER" if passed else "HOLD_NO_STABLE_DEVELOPMENT_INCREMENT",
        })
    return pd.DataFrame(rows)


def run() -> dict[str, Any]:
    config, frozen = validate_frozen()
    started = time.perf_counter()
    alpha = pd.read_parquet(RUN_ROOT / "alpha158_daily_panel.parquet")
    dmn = pd.read_parquet(RUN_ROOT / "dmn_daily_panel.parquet")
    alpha["date"] = pd.to_datetime(alpha.date, utc=True)
    dmn["date"] = pd.to_datetime(dmn.date, utc=True)
    alpha_features = json.loads(PREP_MANIFEST.read_text(encoding="utf-8"))["alpha158_features"]
    dmn_features = json.loads(PREP_MANIFEST.read_text(encoding="utf-8"))["dmn_features"]

    fit_records: list[dict[str, Any]] = []
    full_scores, records = fit_lgbm_ensemble(alpha, alpha_features, config["qlib_reproduction"], config["qlib_reproduction"]["model_seeds"])
    fit_records.extend({"system_id": "QLIB_ALPHA158_LIGHTGBM", **item} for item in records)
    control_features = list(alpha_features[:13])
    control_scores, records = fit_lgbm_ensemble(alpha, control_features, config["qlib_reproduction"], config["qlib_reproduction"]["model_seeds"])
    fit_records.extend({"system_id": "QLIB_PRICE_KBAR_CONTROL", **item} for item in records)
    dmn_fit = fit_dmn_ensemble(
        dmn, dmn_features, config["dmn_reproduction"], config["dmn_reproduction"]["seeds"],
        float(config["dmn_reproduction"]["turnover_penalty"]),
    )
    fit_records.extend({"system_id": "DEEP_MOMENTUM_LSTM", **item} for item in dmn_fit.records)
    dmn_control = fit_dmn_ensemble(
        dmn, dmn_features, config["dmn_reproduction"], config["dmn_reproduction"]["seeds"], 0.0,
    )
    fit_records.extend({"system_id": "DEEP_MOMENTUM_NO_TURNOVER_CONTROL", **item} for item in dmn_control.records)
    if len(fit_records) != config["fixed_budget"]["model_fits"]:
        raise ValueError("executed model-fit count drift")

    internal_score = alpha.groupby("symbol", sort=False).close.pct_change(20, fill_method=None)
    common_weights = {
        "INTERNAL_FORMULA_20D_CS_MOMENTUM": cross_sectional_unit_gross(internal_score, alpha),
        "SIMPLE_ECONOMIC_20D_TSMOM": tsmom_weights(alpha, 20),
        "QLIB_ALPHA158_LIGHTGBM": cross_sectional_unit_gross(full_scores, alpha),
        "QLIB_PRICE_KBAR_CONTROL": cross_sectional_unit_gross(control_scores, alpha),
        "DEEP_MOMENTUM_LSTM": dmn_fit.positions.groupby(dmn.date, sort=False).transform(lambda s: s / s.abs().sum() if s.abs().sum() else 0.0),
        "DEEP_MOMENTUM_NO_TURNOVER_CONTROL": dmn_control.positions.groupby(dmn.date, sort=False).transform(lambda s: s / s.abs().sum() if s.abs().sum() else 0.0),
    }
    native_weights = {
        "QLIB_ALPHA158_LIGHTGBM": topk_dropout_weights(full_scores, alpha, config["qlib_reproduction"]["native_topk"], config["qlib_reproduction"]["native_drop"]),
        "QLIB_PRICE_KBAR_CONTROL": topk_dropout_weights(control_scores, alpha, config["qlib_reproduction"]["native_topk"], config["qlib_reproduction"]["native_drop"]),
        "DEEP_MOMENTUM_LSTM": dmn_fit.positions / dmn.groupby("date").symbol.transform("count"),
        "DEEP_MOMENTUM_NO_TURNOVER_CONTROL": dmn_control.positions / dmn.groupby("date").symbol.transform("count"),
    }
    runtime_by_system = pd.DataFrame(fit_records).groupby("system_id").runtime_seconds.sum().to_dict()
    complexity = {
        "INTERNAL_FORMULA_20D_CS_MOMENTUM": 1.0,
        "SIMPLE_ECONOMIC_20D_TSMOM": 2.0,
        "QLIB_ALPHA158_LIGHTGBM": 158.0,
        "QLIB_PRICE_KBAR_CONTROL": 13.0,
        "DEEP_MOMENTUM_LSTM": float(len(dmn_features) * config["dmn_reproduction"]["hidden_size"]),
        "DEEP_MOMENTUM_NO_TURNOVER_CONTROL": float(len(dmn_features) * config["dmn_reproduction"]["hidden_size"]),
    }
    results: list[dict[str, Any]] = []
    paths: list[pd.DataFrame] = []
    for system, weights in common_weights.items():
        frame = dmn if system.startswith("DEEP_MOMENTUM") else alpha
        for role in config["arena"]["roles"]:
            record, path = evaluate_weights(
                frame, weights, role, config["dataset"]["common_cost_bps_per_unit_turnover"], system,
                runtime_by_system.get(system, 0.0), complexity[system], "COMMON",
            )
            results.append(record)
            paths.append(path)
    qlib_native_cost = (config["qlib_reproduction"]["native_open_cost_bps"] + config["qlib_reproduction"]["native_close_cost_bps"]) / 2.0
    for system, weights in native_weights.items():
        frame = dmn if system.startswith("DEEP_MOMENTUM") else alpha
        cost = config["dmn_reproduction"]["native_cost_bps_per_unit_turnover"] if system.startswith("DEEP_MOMENTUM") else qlib_native_cost
        for role in config["arena"]["roles"]:
            record, path = evaluate_weights(frame, weights, role, cost, system, runtime_by_system.get(system, 0.0), complexity[system], "NATIVE")
            results.append(record)
            paths.append(path)
    result_frame = pd.DataFrame(results)
    path_frame = pd.concat(paths, ignore_index=True)
    if len(result_frame[result_frame.evaluation.eq("COMMON")]) != len(config["arena"]["systems"]) * len(config["arena"]["roles"]):
        raise ValueError("common arena result matrix incomplete")

    native_forecasts = []
    for system, scores in (("QLIB_ALPHA158_LIGHTGBM", full_scores), ("QLIB_PRICE_KBAR_CONTROL", control_scores)):
        for role in config["arena"]["roles"]:
            native_forecasts.append({"system_id": system, "data_role": role, **daily_ic(alpha, scores, role)})
    native_forecast_frame = pd.DataFrame(native_forecasts)

    behaviour_matrix, behaviour = behaviour_summary(alpha, {
        key: value if not key.startswith("DEEP_MOMENTUM") else pd.Series(value.to_numpy(), index=alpha.index)
        for key, value in common_weights.items()
    })
    result_frame["behaviour_overlap"] = result_frame.system_id.map(
        lambda value: float(behaviour_matrix.loc[value, "INTERNAL_FORMULA_20D_CS_MOMENTUM"])
    )
    migration = _migration_decisions(result_frame, behaviour_matrix, config)
    migrated = migration[migration.migration_gate_passed]
    common = result_frame[result_frame.evaluation.eq("COMMON")]
    challenge = common[common.data_role.eq("CHALLENGE")]
    qlib_ic = native_forecast_frame[(native_forecast_frame.system_id.eq("QLIB_ALPHA158_LIGHTGBM")) & native_forecast_frame.data_role.eq("CHALLENGE")].iloc[0]
    dmn_challenge = challenge[challenge.system_id.eq("DEEP_MOMENTUM_LSTM")].iloc[0]
    reproducible_advantage = bool(not migrated.empty)
    if reproducible_advantage:
        recommendation = "HYBRIDIZE_EXTERNAL_COMPONENTS_WITH_INTERNAL_SYSTEM"
        weakest_layer = "CURRENT_SIGNAL_FIRST_PORTFOLIO_AND_REPRESENTATION_BOUNDARY"
        next_architecture = "HYBRID_MULTI_PARADIGM_ARENA_WITH_MIGRATED_COMPONENT"
    else:
        recommendation = "WAIT_FOR_EXTERNAL_DATA_WITH_ARENA_READY"
        weakest_layer = "APPROVED_DATA_REPRESENTATION_AND_HISTORY_DEPTH"
        next_architecture = "ARENA_FIRST_EXTERNAL_DATA_ADAPTERS_WITH_FORMULA_SEARCH_FROZEN"
    gap_analysis = {
        "representation": {
            "qlib_alpha158_challenge_ic": float(qlib_ic.ic),
            "qlib_alpha158_challenge_rank_ic": float(qlib_ic.rank_ic),
            "full_minus_price_control_challenge_net_mean": float(migration.loc[migration.challenger.eq("QLIB_ALPHA158_LIGHTGBM"), "challenge_net_mean_increment"].iloc[0]),
            "conclusion": "SUPERIOR" if migration.loc[migration.challenger.eq("QLIB_ALPHA158_LIGHTGBM"), "migration_gate_passed"].iloc[0] else "NO_STABLE_INCREMENT",
        },
        "target_horizon": {
            "qlib_target": config["dataset"]["label"],
            "dmn_target": "direct next-day portfolio return",
            "conclusion": "INSUFFICIENT_EVIDENCE_TO_REDEFINE" if not reproducible_advantage else "EXTERNAL_TARGET_COMPONENT_SUPPORTED",
        },
        "model_expression": {
            "dmn_challenge_net_lcb": float(dmn_challenge.net_lcb),
            "conclusion": "NO_STABLE_INCREMENT" if not migration.loc[migration.challenger.eq("DEEP_MOMENTUM_LSTM"), "migration_gate_passed"].iloc[0] else "TURNOVER_AWARE_DMN_SUPPORTED",
        },
        "search_training": {
            "fixed_model_fits": len(fit_records),
            "online_tuning": False,
            "conclusion": "EXTERNAL_FIXED_TRAINING_DID_NOT_REMOVE_DATA_BOTTLENECK" if not reproducible_advantage else "EXTERNAL_FIXED_TRAINING_ADDS_INCREMENT",
        },
        "portfolio_mapping": {
            "native_and_common_both_reported": True,
            "conclusion": "PORTFOLIO_MAPPING_NOT_ALLOWED_TO_HIDE_FORECAST_FAILURE",
        },
        "cost_model": {
            "common_cost_bps": config["dataset"]["common_cost_bps_per_unit_turnover"],
            "qlib_native_cost_bps_average": qlib_native_cost,
            "dmn_native_cost_bps": config["dmn_reproduction"]["native_cost_bps_per_unit_turnover"],
            "conclusion": "COST_AWARE_ALL_COMMON_DECISIONS_NET",
        },
        "regime_state": {
            "time_blocks": int(_monthly_stability(path_frame).month.nunique()),
            "conclusion": "NATIVE_LONG_REGIME_HISTORY_UNAVAILABLE",
        },
        "evaluator": {
            "native_and_common_separated": True,
            "conclusion": "MULTI_PARADIGM_BRIDGE_IMPLEMENTED",
        },
        "weakest_layer": weakest_layer,
        "directly_transplantable_components": migrated.component.tolist(),
        "unadaptable_paradigms": [
            "DEEPLOB_DIGITAL_ASSET_WITHOUT_MULTI_LEVEL_L2",
            "FULL_MOMENTUM_TRANSFORMER_WITHOUT_ONE_YEAR_TRAINING_HISTORY",
            "G_RESEARCH_NATIVE_15MIN_WITHOUT_QUALIFIED_MINUTE_RELEASE",
            "DEEPM_WITHOUT_LONG_MULTI_REGIME_CROSS_ASSET_HISTORY",
        ],
        "architecture_assumptions_to_overturn": [
            "one_formula_signal_identity is the universal research object",
            "all paradigms must share one target and portfolio mapper",
            "search-engine repair can compensate for missing mechanism data",
        ],
        "next_generation_architecture": next_architecture,
    }

    result_frame.to_csv(RUN_ROOT / "arena_comparison.csv", index=False, lineterminator="\n")
    native_forecast_frame.to_csv(RUN_ROOT / "native_forecast_metrics.csv", index=False, lineterminator="\n")
    path_frame.to_parquet(RUN_ROOT / "arena_daily_paths.parquet", index=False)
    _monthly_stability(path_frame).to_csv(RUN_ROOT / "time_block_stability.csv", index=False, lineterminator="\n")
    behaviour_matrix.to_csv(RUN_ROOT / "behaviour_overlap_matrix.csv", lineterminator="\n")
    write_json(RUN_ROOT / "behaviour_summary.json", behaviour)
    migration.to_csv(RUN_ROOT / "component_migration_decisions.csv", index=False, lineterminator="\n")
    pd.DataFrame(fit_records).to_csv(RUN_ROOT / "model_fit_ledger.csv", index=False, lineterminator="\n")
    pd.concat([dmn_fit.training_curve.assign(system_id="DEEP_MOMENTUM_LSTM"), dmn_control.training_curve.assign(system_id="DEEP_MOMENTUM_NO_TURNOVER_CONTROL")], ignore_index=True).to_csv(
        RUN_ROOT / "dmn_training_curve.csv", index=False, lineterminator="\n"
    )
    prediction_table = alpha[["date", "symbol", "data_role", "label"]].copy()
    prediction_table["qlib_score"] = full_scores
    prediction_table["qlib_control_score"] = control_scores
    for system, weights in common_weights.items():
        prediction_table[f"weight__{system}"] = weights.to_numpy()
    prediction_table.to_parquet(RUN_ROOT / "arena_predictions_and_weights.parquet", index=False)
    write_json(RUN_ROOT / "layer_gap_analysis.json", gap_analysis)

    bias_audit = {
        "factor": "multi-paradigm frontier reproductions",
        "run_experiment_id": frozen["experiment_id"],
        "data_source_and_universe": f"{config['release']['release_id']} qualified core12 coordinates only",
        "frequency_and_horizon": "daily; one-day execution delay; next-day return",
        "in_sample_window": "2024-01 through 2024-06",
        "development_challenge_window": "2024-07 through 2024-10; previously opened pre-forward release role",
        "oos_window": "NONE; sealed forward not accessed",
        "oos_sample_grade": "NONE",
        "cost_model": "common 5bp per unit turnover; native Qlib and DMN costs reported separately",
        "turnover": "reported from actual portfolio weights",
        "benchmark": "internal 20d formula momentum and simple 20d TSMOM",
        "discovery_status": "REPRODUCTION",
        "findings": {
            "look_ahead": "PASS_PIT_FEATURES_AND_ONE_DAY_EXECUTION_DELAY",
            "survivorship": "SCOPED_FIXED_CORE12_RELEASE_NOT_A_DYNAMIC_UNIVERSE",
            "date_alignment": "PASS_LABEL_START_T_PLUS_1_TO_T_PLUS_2",
            "label_horizon": "PASS_NON_OVERLAPPING_DAILY_DECISION_RETURN",
            "costs": "PASS_NATIVE_AND_COMMON_COSTS_EXPLICIT",
            "turnover": "PASS_ACTUAL_WEIGHT_TURNOVER",
            "multi_window_stability": "DEVELOPMENT_AND_CHALLENGE_MONTHS_REPORTED",
            "replay_vs_discovery": "REPRODUCTION_NOT_NEW_ALPHA_DISCOVERY",
        },
        "blocking_issues": [
            "no untouched OOS is available or accessed",
            "fixed core12 universe carries scoped survivorship limitations",
            "DMN native 252-day and one-year sequence features are not reproducible in ten months",
        ],
        "decision": "HOLD_RESEARCH",
        "required_next_action": "ingest approved external mechanism data through the frozen Arena contract before any new performance program",
    }
    write_json(RUN_ROOT / "bias_audit.json", bias_audit)

    total_runtime = time.perf_counter() - started
    summary = {
        "status": "CRYPTO_FRONTIER_ASSIMILATION_COMPLETED",
        "main_recommendation": recommendation,
        "outcome_class": "A_EXTERNAL_COMPONENT_MIGRATED" if reproducible_advantage else "B_DATA_BOTTLENECK_WITH_ARENA_READY",
        "external_frontier_entries": len(config["frontier_map"]),
        "real_end_to_end_reproductions": 2,
        "matched_controls": 2,
        "fixed_model_fits": len(fit_records),
        "arena_systems": len(config["arena"]["systems"]),
        "arena_common_results": int(len(result_frame[result_frame.evaluation.eq("COMMON")])),
        "arena_native_results": int(len(result_frame[result_frame.evaluation.eq("NATIVE")])),
        "migrated_components": migrated.component.tolist(),
        "data_hard_blockers": gap_analysis["unadaptable_paradigms"],
        "weakest_layer": weakest_layer,
        "behaviour_neff": behaviour["behaviour_neff"],
        "behaviour_clusters": behaviour["behaviour_clusters"],
        "top_cluster_share": behaviour["top_cluster_share"],
        "runtime_seconds": total_runtime,
        "reproducibility": "DETERMINISTIC_SEEDS_HASHED_INPUTS_FIXED_BUDGET_SINGLE_EXECUTION",
        "performance_scope": "QUALIFIED_DEVELOPMENT_AND_PREVIOUSLY_OPENED_PRE_FORWARD_CHALLENGE_ONLY",
        "new_performance_search_frozen": True,
        "forward_read": False,
        "spent_evaluation_read": False,
        "candidate_promotion": False,
        "cross_sprint_adaptive_memory": False,
        "additional_budget": False,
        "frozen_manifest_sha256": frozen["frozen_manifest_sha256"],
    }
    write_json(SUMMARY, summary)
    _write_report(summary, gap_analysis, result_frame, native_forecast_frame, migration, bias_audit)
    _write_artifact_index()
    return summary


def _write_report(
    summary: dict[str, Any],
    gaps: dict[str, Any],
    results: pd.DataFrame,
    native: pd.DataFrame,
    migration: pd.DataFrame,
    audit: dict[str, Any],
) -> None:
    common_challenge = results[(results.evaluation.eq("COMMON")) & results.data_role.eq("CHALLENGE")]
    table = common_challenge[["system_id", "net_mean", "net_lcb", "annualized_sharpe", "positive_month_fraction", "turnover_mean", "behaviour_overlap"]].to_markdown(index=False)
    native_table = native.to_markdown(index=False)
    migration_table = migration.to_markdown(index=False)
    report = f"""# Crypto External Frontier Assimilation Sprint

Status: `{summary['status']}`
Main recommendation: `{summary['main_recommendation']}`
Outcome: `{summary['outcome_class']}`

## Result

- Reproduced end to end: Qlib Alpha158/LightGBM/TopKDropout and scoped Deep Momentum LSTM/direct-Sharpe.
- Arena: `{summary['arena_systems']}` systems, `{summary['arena_common_results']}` common bridge results and `{summary['arena_native_results']}` native portfolio results.
- Weakest layer: `{summary['weakest_layer']}`.
- Behaviour: N_eff `{summary['behaviour_neff']:.4f}`, clusters `{summary['behaviour_clusters']}`, top share `{summary['top_cluster_share']:.4f}`.
- Migrated components: `{summary['migrated_components'] or 'none'}`.

## Common challenge comparison

{table}

## Native forecast evaluation

{native_table}

## Matched component decisions

{migration_table}

## Layer attribution

- Data representation: `{gaps['representation']['conclusion']}`.
- Target/horizon: `{gaps['target_horizon']['conclusion']}`.
- Model expression: `{gaps['model_expression']['conclusion']}`.
- Search/training: `{gaps['search_training']['conclusion']}`.
- Portfolio mapping: `{gaps['portfolio_mapping']['conclusion']}`.
- Regime/state: `{gaps['regime_state']['conclusion']}`.
- Evaluator: `{gaps['evaluator']['conclusion']}`.

The system cannot honestly infer that DeepLOB, full Momentum Transformer, native G-Research minute forecasting, or DeePM is ineffective. Those paradigms are data-incompatible with the currently qualified release. The result supports an Arena-first architecture and a direct external-data entry contract, while keeping formula search frozen.

## Scope and non-claims

- No validation, test, recent, May stress, sealed forward, promotion, or cross-sprint memory was accessed.
- The Jul-Oct role is the already-opened pre-forward challenge block from the qualified native aggTrades release; it is not untouched OOS.
- Bias audit: `{audit['decision']}` because OOS grade is `{audit['oos_sample_grade']}`.
- These are reproductions and architecture evidence, not alpha-ready or deployable candidates.

## External references

- Qlib Alpha158/LightGBM workflow: https://github.com/microsoft/qlib/blob/main/examples/benchmarks/LightGBM/workflow_config_lightgbm_Alpha158.yaml
- Deep Momentum Networks: https://arxiv.org/abs/1904.04912v3
- Momentum Transformer companion code: https://github.com/kieranjwood/trading-momentum-transformer
- G-Research Crypto Forecasting: https://www.gresearch.com/news/wrapping-up-the-g-research-crypto-forecasting-competition/
- DeepLOB: https://github.com/zcakhaa/DeepLOB-Deep-Convolutional-Neural-Networks-for-Limit-Order-Books
- Digital-asset order-book model: https://arxiv.org/abs/2010.01241
- DeepDow: https://deepdow.readthedocs.io/
- FinRL: https://github.com/AI4Finance-Foundation/FinRL
- AlphaGen: https://github.com/ICT-FinD-Lab/alphagen
"""
    (RUN_ROOT / "CRYPTO_FRONTIER_ASSIMILATION_REPORT.md").write_text(report, encoding="utf-8")


def _write_artifact_index() -> None:
    excluded = {"frontier_artifact_index.csv"}
    rows = []
    for path in sorted(RUN_ROOT.iterdir()):
        if not path.is_file() or path.name in excluded:
            continue
        rows.append(artifact_record(path, "FRONTIER_ASSIMILATION_EVIDENCE", "crypto_external_frontier_assimilation.py"))
    pd.DataFrame(rows).to_csv(RUN_ROOT / "frontier_artifact_index.csv", index=False, lineterminator="\n")


def ingress_preflight(family: str, schema_json: Path) -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    contract = next((item for item in config["external_data_contracts"] if item["family"] == family), None)
    if contract is None:
        raise KeyError(f"unknown external data family: {family}")
    payload = json.loads(schema_json.read_text(encoding="utf-8"))
    columns = payload["columns"] if isinstance(payload, dict) else payload
    result = validate_external_data_contract(contract, columns)
    result.update({
        "source_schema_path": str(schema_json),
        "performance_started": False,
        "forward_read": False,
        "next_command_if_ready": "register release manifest, freeze adapter hash, then run one bounded mechanism/competitor experiment",
    })
    write_json(RUN_ROOT / f"ingress_preflight__{family}.json", result)
    return result


def check() -> dict[str, Any]:
    config, frozen = validate_frozen()
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    results = pd.read_csv(RUN_ROOT / "arena_comparison.csv")
    fits = pd.read_csv(RUN_ROOT / "model_fit_ledger.csv")
    index = pd.read_csv(RUN_ROOT / "frontier_artifact_index.csv")
    if len(fits) != config["fixed_budget"]["model_fits"]:
        raise ValueError("model fit budget mismatch")
    if len(results[results.evaluation.eq("COMMON")]) != len(config["arena"]["systems"]) * len(config["arena"]["roles"]):
        raise ValueError("arena result matrix mismatch")
    if summary["frozen_manifest_sha256"] != frozen["frozen_manifest_sha256"]:
        raise ValueError("summary/freeze identity mismatch")
    for flag in ("forward_read", "spent_evaluation_read", "candidate_promotion", "cross_sprint_adaptive_memory", "additional_budget"):
        if summary[flag]:
            raise PermissionError(f"summary records prohibited activity: {flag}")
    for row in index.itertuples():
        path = REPO / row.artifact
        if sha256_file(path) != row.sha256:
            raise ValueError(f"artifact drift: {row.artifact}")
    return {
        "status": "PASS_CRYPTO_FRONTIER_ASSIMILATION_CHECK",
        "experiment_id": frozen["experiment_id"],
        "model_fits": len(fits),
        "common_results": int(len(results[results.evaluation.eq("COMMON")])),
        "recommendation": summary["main_recommendation"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "freeze", "run", "check", "ingress-preflight"])
    parser.add_argument("--family")
    parser.add_argument("--schema-json", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare()
    elif args.command == "freeze":
        result = freeze()
    elif args.command == "run":
        result = run()
    elif args.command == "check":
        result = check()
    else:
        if not args.family or not args.schema_json:
            parser.error("ingress-preflight requires --family and --schema-json")
        result = ingress_preflight(args.family, args.schema_json)
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
