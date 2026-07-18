from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import Ridge

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphafactory_crypto.broad_information_arena import (  # noqa: E402
    CONTROL_SURFACE,
    DIRECT_DELTA_MAPPING,
    FULL_SURFACE,
    HORIZON_MEAN_DELTA_MAPPING,
    MLP_MODEL,
    RIDGE_MODEL,
    TURNOVER_AWARE_STICKY_MAPPING,
    FixedMLP,
    apply_linear_return_calibration,
    arena_decision,
    array_sha256,
    data_adequacy,
    deterministic_coordinates,
    economic_metrics,
    fit_normalization,
    fit_nonnegative_linear_return_calibration,
    information_evidence,
    incremental_signal_mapping,
    load_broad_arena_data,
    model_matrix,
    mapping_repair_decision,
    paired_increment,
    paired_surface_diagnostics,
    payload_sha256,
    predict_split,
    prediction_metrics,
    sticky_mapping_decision,
    turnover_aware_sticky_mapping,
)
from alphafactory_crypto.core_pack_consumption import sha256_file  # noqa: E402
from alphafactory_crypto.instrument_capability.mapping import (  # noqa: E402
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    map_portfolio,
    mapping_contract_sha256,
)


def _git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, values: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True, default=str) + "\n" for row in values), encoding="utf-8", newline="\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _report(manifest: dict[str, Any], decision: dict[str, Any], adequacy: dict[str, Any], information: pd.DataFrame) -> str:
    added = information.loc[information["surface_role"] == "ADDED"]
    control = information.loc[information["surface_role"] == "CONTROL"]
    return "\n".join(
        [
            "# Broad Core Pack purged model-fit / calibration development Arena",
            "",
            "This is a frozen development-only comparison. It is not performance search, OOS evidence, or promotion authority.",
            "",
            f"- Source SHA: `{manifest['source_sha']}`",
            f"- Status: `{decision['status']}`",
            f"- Data adequacy: `{adequacy['status']}`",
            f"- Added fields with stable residual information: {int(added['stable_residual_information'].sum())}/{len(added)}",
            f"- Control fields with stable residual information: {int(control['stable_residual_information'].sum())}/{len(control)}",
            f"- Information gate: {decision['information_gate_pass']}",
            f"- Economic increment gate: {decision['economic_increment_gate_pass']}",
            f"- Cost-killed under frozen mapping: {decision['cost_killed_under_frozen_mapping']}",
            f"- Degenerate prediction/mapping pairs: {decision['degenerate_pairs']}",
            f"- Mapping repair: `{decision['mapping_repair']['status']}`",
            f"- Turnover-aware sticky mapping: `{decision['turnover_aware_mapping']['status']}`",
            f"- Train-only calibrated sticky mapping: `{decision['train_only_calibrated_sticky']['status']}`",
            f"- Calibration-fit degenerate arms: {decision['train_only_calibrated_sticky']['calibration_fit_degenerate_arms']}",
            f"- Bias audit: `{decision['bias_audit']['decision']}`",
            "",
            "## Why entropy is not used alone",
            "",
            "Quantile-binned H(X) is an adequacy check and approaches its maximum for nearly every non-degenerate field. The decision therefore uses block-matched mutual-information excess, residual information over the current 10-field Ridge, redundancy evidence, and fixed-model matched increments.",
            "",
            "## Split increment summary",
            "",
            pd.DataFrame(decision["split_increment_summary"]).to_markdown(index=False),
            "",
            "## Mapping repair summary",
            "",
            pd.DataFrame(decision["mapping_repair"]["summary"]).to_markdown(index=False),
            "",
            "## Turnover-aware sticky mapping summary",
            "",
            pd.DataFrame(decision["turnover_aware_mapping"]["summary"]).to_markdown(index=False),
            "",
            "## Train-only calibrated sticky summary",
            "",
            pd.DataFrame(decision["train_only_calibrated_sticky"]["summary"]).to_markdown(index=False),
            "",
            "## Boundary repair",
            "",
            "The former train role is split once into model-fit (2023-07 through 2023-12) and held-out calibration (2024-01 through 2024-02). Every model-fit, calibration, selection, and stability block purges its final 6 hours, equal to the 2h execution delay plus 4h target horizon. Prior unpurged prediction identities are retained only as superseded evidence.",
            "",
            "Ridge plus three MLP seeds are robustness arms, not independent samples. Selection and stability are already-spent development evidence; hourly LCBs are descriptive because 4h labels overlap and returns are serially dependent.",
            "",
            "## Boundaries",
            "",
            "No validation/test/recent/May-stress/forward/challenge role was read. No hyperparameter search or candidate promotion occurred.",
            "",
        ]
    )


def run(config_path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output_root = ROOT / config["outputs"]["runtime_root"]
    report_path = ROOT / config["outputs"]["report"]
    output_root.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    data = load_broad_arena_data(ROOT, config)
    reference_rows = _read_jsonl(ROOT / config["inputs"]["reference_model_evidence"])
    reference_by_key = {
        (row["model_family"], int(row["seed"]), row["split"], row["surface"]): row
        for row in reference_rows
    }
    adequacy = data_adequacy(data, config)
    _write_json(output_root / "data_adequacy.json", adequacy)
    if adequacy["status"] != "DATA_ADEQUACY_PASS":
        raise RuntimeError("Broad information Arena failed its pre-registered Data Adequacy Gate")

    purge_hours = int(config["label_boundary_contract"]["purge_hours"])
    split_boundary_evidence: dict[str, Any] = {
        "label_definition": "log(close[t+2+4]/close[t+2])",
        "execution_delay_hours": int(
            config["label_boundary_contract"]["execution_delay_hours"]
        ),
        "target_horizon_hours": int(config["target_horizon_hours"]),
        "purge_hours": purge_hours,
        "roles": {},
    }
    for role, block in data.slices.items():
        declared_end = pd.Timestamp(config["splits"][role]["end_exclusive"])
        last_signal = pd.Timestamp(int(data.timestamps[block.stop - 1]), tz="UTC")
        label_end = last_signal + pd.Timedelta(hours=purge_hours)
        local_mask = data.eligibility[:, block] & np.isfinite(data.target[:, block])
        split_boundary_evidence["roles"][role] = {
            "declared_start": config["splits"][role]["start"],
            "declared_end_exclusive": config["splits"][role]["end_exclusive"],
            "effective_last_signal_timestamp": str(last_signal),
            "last_label_end_timestamp": str(label_end),
            "last_label_end_before_declared_end": bool(label_end < declared_end),
            "eligible_label_samples": int(local_mask.sum()),
            "eligible_mask_sha256": array_sha256(local_mask.astype(np.float64)),
            "target_block_sha256": array_sha256(data.target[:, block]),
        }
    _write_json(output_root / "split_boundary_evidence.json", split_boundary_evidence)

    model_fit = data.slices["model_fit"]
    train_mask = data.eligibility[:, model_fit] & np.isfinite(data.target[:, model_fit])
    train_assets, train_times = deterministic_coordinates(train_mask, int(config["models"]["train_samples"]))
    train_absolute = train_times + model_fit.start
    median, scale = fit_normalization(data, train_assets, train_absolute)
    full_indices = np.arange(len(data.fields))
    control_indices = np.asarray([data.fields.index(field) for field in data.control_fields])
    train_target = data.target[train_assets, train_absolute].astype(np.float32)
    target_mean = float(np.mean(train_target))
    target_scale = float(max(np.std(train_target), 1e-8))
    train_scaled = (train_target - target_mean) / target_scale
    raw_full = data.values[train_assets[:, None], full_indices[None, :], train_absolute[:, None]]
    model_fit_identity = {
        "role": "model_fit",
        "sample_count": int(len(train_assets)),
        "asset_coordinates_sha256": array_sha256(train_assets.astype(np.float64)),
        "time_coordinates_sha256": array_sha256(train_absolute.astype(np.float64)),
        "sampled_target_sha256": array_sha256(train_target),
    }

    models: list[tuple[str, str, int, Any, dict[str, Any], np.ndarray]] = []
    for surface, indices in ((CONTROL_SURFACE, control_indices), (FULL_SURFACE, full_indices)):
        x = model_matrix(raw_full[:, indices], median[indices], scale[indices])
        ridge = Ridge(alpha=float(config["models"]["ridge_alpha"]))
        fit_started = time.perf_counter()
        ridge.fit(x, train_scaled)
        models.append((RIDGE_MODEL, surface, 0, ridge, {"fit_seconds": time.perf_counter() - fit_started, "training_score": float(ridge.score(x, train_scaled))}, indices))
        for seed in config["models"]["mlp_seeds"]:
            model = FixedMLP(x.shape[1], config["models"]["mlp_hidden"], int(seed))
            diagnostic = model.fit(
                x,
                train_scaled,
                seed=int(seed),
                epochs=int(config["models"]["mlp_epochs"]),
                batch_size=int(config["models"]["mlp_batch_size"]),
                learning_rate=float(config["models"]["mlp_learning_rate"]),
                weight_decay=float(config["models"]["mlp_weight_decay"]),
                torch_threads=int(config["models"]["torch_threads"]),
            )
            models.append((MLP_MODEL, surface, int(seed), model, diagnostic, indices))

    baseline_ridge = next(model for family, surface, _, model, _, _ in models if family == RIDGE_MODEL and surface == CONTROL_SURFACE)
    prior_census = pd.read_parquet(ROOT / config["inputs"]["prior_information_census"])
    information = information_evidence(
        data,
        baseline_ridge=baseline_ridge,
        median=median,
        scale=scale,
        target_mean=target_mean,
        target_scale=target_scale,
        config=config,
        prior_census=prior_census,
    )
    information_path = output_root / "information_evidence.csv"
    information.to_csv(information_path, index=False, lineterminator="\n")

    calibration_block = data.slices["calibration"]
    calibration_rows: list[dict[str, Any]] = []
    calibration_by_model: dict[tuple[str, int, str], dict[str, Any]] = {}
    for family, surface, seed, model, _, indices in models:
        calibration_prediction = predict_split(
            model,
            model_family=family,
            data=data,
            block=calibration_block,
            field_indices=indices,
            median=median,
            scale=scale,
            target_mean=target_mean,
            target_scale=target_scale,
        )
        calibration = fit_nonnegative_linear_return_calibration(
            calibration_prediction, data.target[:, calibration_block]
        )
        calibration.update(
            {
                "model_family": family,
                "surface": surface,
                "seed": int(seed),
                "parent_role": config["train_only_calibration"]["parent_role"],
                "model_fit_role": config["train_only_calibration"]["model_fit_role"],
                "fit_role": config["train_only_calibration"]["fit_role"],
                "fit_independence": config["train_only_calibration"]["fit_independence"],
                "model_fit_identity": model_fit_identity,
                "fit_start": config["splits"]["calibration"]["start"],
                "declared_fit_end_exclusive": config["splits"]["calibration"]["end_exclusive"],
                "purge_hours": purge_hours,
                "last_fitted_signal_timestamp": str(
                    pd.Timestamp(int(data.timestamps[calibration_block.stop - 1]), tz="UTC")
                ),
            }
        )
        calibration_rows.append(calibration)
        calibration_by_model[(family, int(seed), surface)] = calibration

    model_rows: list[dict[str, Any]] = []
    prediction_identity_rows: list[dict[str, Any]] = []
    weights: dict[tuple[str, int, str, str], np.ndarray] = {}
    predictions: dict[tuple[str, int, str, str], np.ndarray] = {}
    base_economic_by_key: dict[tuple[str, int, str, str], dict[str, Any]] = {}
    reference_policy = str(config["reference_prediction_policy"])
    for family, surface, seed, model, diagnostic, indices in models:
        for split in ("selection", "stability"):
            block = data.slices[split]
            prediction = predict_split(
                model,
                model_family=family,
                data=data,
                block=block,
                field_indices=indices,
                median=median,
                scale=scale,
                target_mean=target_mean,
                target_scale=target_scale,
            )
            predictive = prediction_metrics(prediction, data.target[:, block], int(config["models"]["rank_metric_samples"]))
            identity_key = (family, int(seed), split, surface)
            if identity_key not in reference_by_key:
                raise ValueError(f"REFERENCE_PREDICTION_KEY_MISSING:{identity_key}")
            expected_prediction_sha256 = reference_by_key[identity_key]["predictive"]["prediction_sha256"]
            prediction_identity_match = predictive["prediction_sha256"] == expected_prediction_sha256
            prediction_identity_rows.append(
                {
                    "model_family": family,
                    "surface": surface,
                    "seed": int(seed),
                    "split": split,
                    "expected_prediction_sha256": expected_prediction_sha256,
                    "observed_prediction_sha256": predictive["prediction_sha256"],
                    "match": prediction_identity_match,
                    "policy": reference_policy,
                    "supersession_reason": (
                        "PRIOR_REFERENCE_DID_NOT_PURGE_EXECUTION_DELAY_PLUS_HORIZON"
                        if reference_policy == "SUPERSEDE_UNPURGED_REFERENCE"
                        else None
                    ),
                }
            )
            if reference_policy == "REQUIRE_EXACT" and not prediction_identity_match:
                raise ValueError(f"REFERENCE_PREDICTION_IDENTITY_MISMATCH:{identity_key}")
            if reference_policy not in {"REQUIRE_EXACT", "SUPERSEDE_UNPURGED_REFERENCE"}:
                raise ValueError(f"UNKNOWN_REFERENCE_PREDICTION_POLICY:{reference_policy}")
            economic, local_weights = economic_metrics(prediction, data, block)
            weights[(family, seed, split, surface)] = local_weights
            predictions[(family, seed, split, surface)] = prediction
            base_economic_by_key[(family, seed, split, surface)] = economic
            model_rows.append({
                "model_family": family,
                "surface": surface,
                "seed": seed,
                "split": split,
                "field_count": int(len(indices)),
                "fit": diagnostic,
                "predictive": predictive,
                "economic": economic,
            })
    increment_rows: list[dict[str, Any]] = []
    for family, seed in ((RIDGE_MODEL, 0), *[(MLP_MODEL, int(seed)) for seed in config["models"]["mlp_seeds"]]):
        for split in ("selection", "stability"):
            full_prediction = predictions[(family, seed, split, FULL_SURFACE)]
            control_prediction = predictions[(family, seed, split, CONTROL_SURFACE)]
            full_weights = weights[(family, seed, split, FULL_SURFACE)]
            control_weights = weights[(family, seed, split, CONTROL_SURFACE)]
            increment_rows.append({
                "model_family": family,
                "seed": seed,
                "split": split,
                "full_surface": FULL_SURFACE,
                "control_surface": CONTROL_SURFACE,
                "metrics": paired_increment(
                    full_weights,
                    control_weights,
                    data,
                    data.slices[split],
                ),
                "comparison": paired_surface_diagnostics(
                    full_prediction,
                    control_prediction,
                    full_weights,
                    control_weights,
                    maximum_rank_samples=int(config["models"]["rank_metric_samples"]),
                ),
            })
    decision = arena_decision(information, increment_rows, config)
    fit_degenerate = [
        {"model_family": family, "surface": surface, "seed": seed}
        for family, surface, seed, _, diagnostic, _ in models
        if (family == MLP_MODEL and not diagnostic["training_loss_decreased"])
        or (family == RIDGE_MODEL and diagnostic["training_score"] <= 0.0)
    ]
    decision["model_fit_degenerate_runs"] = fit_degenerate
    if fit_degenerate:
        decision["status"] = "BROAD_CORE_PACK_MODEL_FIT_DEGENERATE"
    mapping_rows: list[dict[str, Any]] = []
    for family, seed in ((RIDGE_MODEL, 0), *[(MLP_MODEL, int(seed)) for seed in config["models"]["mlp_seeds"]]):
        for split in ("selection", "stability"):
            full_prediction = predictions[(family, seed, split, FULL_SURFACE)]
            control_prediction = predictions[(family, seed, split, CONTROL_SURFACE)]
            for variant, window in (
                (DIRECT_DELTA_MAPPING, 1),
                (
                    HORIZON_MEAN_DELTA_MAPPING,
                    int(config["mapping_repair"]["horizon_smoothing_hours"]),
                ),
            ):
                metrics, variant_weights, signal = incremental_signal_mapping(
                    full_prediction,
                    control_prediction,
                    data,
                    data.slices[split],
                    smoothing_window=window,
                )
                mapping_rows.append(
                    {
                        "variant": variant,
                        "model_family": family,
                        "seed": seed,
                        "split": split,
                        "smoothing_window_hours": window,
                        "metrics": metrics,
                        "signal_sha256": array_sha256(signal),
                        "weight_sha256": array_sha256(variant_weights),
                    }
                )
    decision["mapping_repair"] = mapping_repair_decision(
        mapping_rows, float(config["decision"]["minimum_positive_run_ratio"])
    )
    if decision["mapping_repair"]["passed_variants"]:
        decision["status"] = "BROAD_CORE_PACK_PORTFOLIO_MAPPING_DEVELOPMENT_INCREMENT_OBSERVED"
    sticky = config["turnover_aware_mapping"]
    sticky_surface_rows: list[dict[str, Any]] = []
    sticky_surface_by_key: dict[tuple[str, int, str, str], dict[str, Any]] = {}
    sticky_weights: dict[tuple[str, int, str, str], np.ndarray] = {}
    for key, prediction in predictions.items():
        family, seed, split, surface = key
        metrics, local_weights, diagnostics = turnover_aware_sticky_mapping(
            prediction,
            data,
            data.slices[split],
            horizon=int(sticky["horizon_hours"]),
            cost_bps=float(sticky["cost_bps"]),
            round_trip_multiplier=float(sticky["round_trip_multiplier"]),
        )
        reference_economic = base_economic_by_key[key]
        reference_turnover = float(reference_economic["turnover_mean"])
        row = {
            "mapping_id": TURNOVER_AWARE_STICKY_MAPPING,
            "model_family": family,
            "surface": surface,
            "seed": int(seed),
            "split": split,
            "metrics": metrics,
            "diagnostics": diagnostics,
            "reference_prediction_sha256": array_sha256(prediction),
            "reference_weight_sha256": reference_economic["weight_sha256"],
            "net_improvement_vs_reference": float(metrics["net_mean"] - reference_economic["net_mean"]),
            "turnover_reduction_ratio": float(
                1.0 - metrics["turnover_mean"] / reference_turnover
                if reference_turnover > 0.0
                else 0.0
            ),
        }
        sticky_surface_rows.append(row)
        sticky_surface_by_key[key] = row
        sticky_weights[key] = local_weights
    sticky_pair_rows: list[dict[str, Any]] = []
    for family, seed in ((RIDGE_MODEL, 0), *[(MLP_MODEL, int(seed)) for seed in config["models"]["mlp_seeds"]]):
        for split in ("selection", "stability"):
            full_key = (family, seed, split, FULL_SURFACE)
            control_key = (family, seed, split, CONTROL_SURFACE)
            full = sticky_surface_by_key[full_key]
            control = sticky_surface_by_key[control_key]
            full_metrics = full["metrics"]
            control_metrics = control["metrics"]
            sticky_pair_rows.append(
                {
                    "mapping_id": TURNOVER_AWARE_STICKY_MAPPING,
                    "model_family": family,
                    "seed": int(seed),
                    "split": split,
                    "full": full,
                    "control": control,
                    "matched_surface_difference": {
                        "gross_mean": float(full_metrics["gross_mean"] - control_metrics["gross_mean"]),
                        "cost_mean": float(full_metrics["cost_mean"] - control_metrics["cost_mean"]),
                        "net_mean": float(full_metrics["net_mean"] - control_metrics["net_mean"]),
                    },
                    "delta_sleeve_metrics": paired_increment(
                        sticky_weights[full_key],
                        sticky_weights[control_key],
                        data,
                        data.slices[split],
                    ),
                    "comparison": paired_surface_diagnostics(
                        predictions[full_key],
                        predictions[control_key],
                        sticky_weights[full_key],
                        sticky_weights[control_key],
                        maximum_rank_samples=int(config["models"]["rank_metric_samples"]),
                    ),
                }
            )
    decision["turnover_aware_mapping"] = sticky_mapping_decision(
        sticky_pair_rows, float(config["decision"]["minimum_positive_run_ratio"])
    )
    if decision["turnover_aware_mapping"]["development_increment_observed"]:
        decision["status"] = "BROAD_CORE_PACK_TURNOVER_AWARE_MAPPING_DEVELOPMENT_INCREMENT_OBSERVED"

    calibrated_predictions: dict[tuple[str, int, str, str], np.ndarray] = {}
    calibrated_weights: dict[tuple[str, int, str, str], np.ndarray] = {}
    calibrated_surface_rows: list[dict[str, Any]] = []
    calibrated_surface_by_key: dict[tuple[str, int, str, str], dict[str, Any]] = {}
    for key, prediction in predictions.items():
        family, seed, split, surface = key
        calibration = calibration_by_model[(family, int(seed), surface)]
        calibrated_prediction = apply_linear_return_calibration(
            prediction,
            slope=float(calibration["slope"]),
            intercept=float(calibration["intercept"]),
        )
        no_intercept_prediction = apply_linear_return_calibration(
            prediction,
            slope=float(calibration["slope"]),
            intercept=0.0,
        )
        metrics, local_weights, diagnostics = turnover_aware_sticky_mapping(
            calibrated_prediction,
            data,
            data.slices[split],
            horizon=int(sticky["horizon_hours"]),
            cost_bps=float(sticky["cost_bps"]),
            round_trip_multiplier=float(sticky["round_trip_multiplier"]),
        )
        _, no_intercept_weights, no_intercept_diagnostics = turnover_aware_sticky_mapping(
            no_intercept_prediction,
            data,
            data.slices[split],
            horizon=int(sticky["horizon_hours"]),
            cost_bps=float(sticky["cost_bps"]),
            round_trip_multiplier=float(sticky["round_trip_multiplier"]),
        )
        raw_candidate_weights = np.asarray(
            map_portfolio(
                prediction, DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]
            ).weights,
            dtype=float,
        )
        calibrated_candidate_weights = np.asarray(
            map_portfolio(
                calibrated_prediction,
                DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET],
            ).weights,
            dtype=float,
        )
        candidate_max_abs_difference = float(
            np.max(np.abs(raw_candidate_weights - calibrated_candidate_weights))
        )
        intercept_max_abs_difference = float(
            np.max(np.abs(local_weights - no_intercept_weights))
        )
        candidate_weight_invariant = bool(
            np.allclose(
                raw_candidate_weights,
                calibrated_candidate_weights,
                rtol=0.0,
                atol=1e-12,
            )
        )
        intercept_sticky_weight_invariant = bool(
            np.allclose(local_weights, no_intercept_weights, rtol=0.0, atol=1e-12)
        )
        uncalibrated = sticky_surface_by_key[key]
        reference_turnover = float(uncalibrated["metrics"]["turnover_mean"])
        row = {
            "mapping_id": f"TRAIN_ONLY_CALIBRATED_{TURNOVER_AWARE_STICKY_MAPPING}",
            "model_family": family,
            "surface": surface,
            "seed": int(seed),
            "split": split,
            "metrics": metrics,
            "diagnostics": diagnostics,
            "calibration": calibration,
            "raw_prediction_sha256": array_sha256(prediction),
            "calibrated_prediction_sha256": array_sha256(calibrated_prediction),
            "raw_candidate_weight_sha256": array_sha256(raw_candidate_weights),
            "calibrated_candidate_weight_sha256": array_sha256(
                calibrated_candidate_weights
            ),
            "candidate_weight_invariant_under_positive_affine_calibration": candidate_weight_invariant,
            "candidate_weight_max_abs_difference": candidate_max_abs_difference,
            "intercept_free_sticky_weight_sha256": array_sha256(no_intercept_weights),
            "intercept_free_sticky_diagnostics": no_intercept_diagnostics,
            "intercept_sticky_weight_invariant": intercept_sticky_weight_invariant,
            "intercept_sticky_weight_max_abs_difference": intercept_max_abs_difference,
            "reference_weight_sha256": uncalibrated["metrics"]["weight_sha256"],
            "net_improvement_vs_reference": float(
                metrics["net_mean"] - uncalibrated["metrics"]["net_mean"]
            ),
            "turnover_reduction_ratio": float(
                1.0 - metrics["turnover_mean"] / reference_turnover
                if reference_turnover > 0.0
                else 0.0
            ),
        }
        calibrated_surface_rows.append(row)
        calibrated_surface_by_key[key] = row
        calibrated_predictions[key] = calibrated_prediction
        calibrated_weights[key] = local_weights

    calibrated_pair_rows: list[dict[str, Any]] = []
    for family, seed in ((RIDGE_MODEL, 0), *[(MLP_MODEL, int(seed)) for seed in config["models"]["mlp_seeds"]]):
        for split in ("selection", "stability"):
            full_key = (family, seed, split, FULL_SURFACE)
            control_key = (family, seed, split, CONTROL_SURFACE)
            full = calibrated_surface_by_key[full_key]
            control = calibrated_surface_by_key[control_key]
            full_metrics = full["metrics"]
            control_metrics = control["metrics"]
            calibrated_pair_rows.append(
                {
                    "mapping_id": f"TRAIN_ONLY_CALIBRATED_{TURNOVER_AWARE_STICKY_MAPPING}",
                    "model_family": family,
                    "seed": int(seed),
                    "split": split,
                    "full": full,
                    "control": control,
                    "matched_surface_difference": {
                        "gross_mean": float(full_metrics["gross_mean"] - control_metrics["gross_mean"]),
                        "cost_mean": float(full_metrics["cost_mean"] - control_metrics["cost_mean"]),
                        "net_mean": float(full_metrics["net_mean"] - control_metrics["net_mean"]),
                    },
                    "delta_sleeve_metrics": paired_increment(
                        calibrated_weights[full_key],
                        calibrated_weights[control_key],
                        data,
                        data.slices[split],
                    ),
                    "comparison": paired_surface_diagnostics(
                        calibrated_predictions[full_key],
                        calibrated_predictions[control_key],
                        calibrated_weights[full_key],
                        calibrated_weights[control_key],
                        maximum_rank_samples=int(config["models"]["rank_metric_samples"]),
                    ),
                    "gate_degenerate": bool(
                        full["calibration"]["fit_degenerate"]
                        or control["calibration"]["fit_degenerate"]
                        or not full[
                            "candidate_weight_invariant_under_positive_affine_calibration"
                        ]
                        or not control[
                            "candidate_weight_invariant_under_positive_affine_calibration"
                        ]
                        or not full["intercept_sticky_weight_invariant"]
                        or not control["intercept_sticky_weight_invariant"]
                    ),
                }
            )
    decision["train_only_calibrated_sticky"] = sticky_mapping_decision(
        calibrated_pair_rows, float(config["decision"]["minimum_positive_run_ratio"])
    )
    decision["train_only_calibrated_sticky"].update(
        {
            "calibration_fit_degenerate_arms": int(
                sum(bool(row["fit_degenerate"]) for row in calibration_rows)
            ),
            "arm_interpretation": "Ridge plus three MLP seeds are model-robustness arms, not independent statistical samples.",
            "evidence_scope": "SPENT_DEVELOPMENT_SELECTION_AND_STABILITY_ONLY",
        }
    )

    bias_checks = {
        "purge_equals_execution_delay_plus_horizon": purge_hours
        == int(config["label_boundary_contract"]["execution_delay_hours"])
        + int(config["target_horizon_hours"]),
        "boundary_horizon_matches_target": int(
            config["label_boundary_contract"]["target_horizon_hours"]
        )
        == int(config["target_horizon_hours"]),
        "all_calibrations_use_dedicated_calibration_role": all(
            row["fit_role"] == "calibration" for row in calibration_rows
        ),
        "calibration_is_held_out_from_model_fit": all(
            row["fit_independence"]
            == "HELD_OUT_FROM_MODEL_FIT_WITHIN_DEVELOPMENT_TRAIN"
            for row in calibration_rows
        )
        and data.slices["model_fit"].stop <= data.slices["calibration"].start,
        "nonnegative_slopes_preserve_direction": all(float(row["slope"]) >= 0.0 for row in calibration_rows),
        "no_calibration_fit_degenerate_arms": not any(
            bool(row["fit_degenerate"]) for row in calibration_rows
        ),
        "raw_and_calibrated_candidate_weights_invariant": all(
            bool(row["candidate_weight_invariant_under_positive_affine_calibration"])
            for row in calibrated_surface_rows
        ),
        "intercept_does_not_change_sticky_weights": all(
            bool(row["intercept_sticky_weight_invariant"])
            for row in calibrated_surface_rows
        ),
        "selection_stability_not_used_for_fit": not bool(
            config["train_only_calibration"]["selection_or_stability_fit_allowed"]
        ),
        "all_development_blocks_purged": all(
            data.slices[name].stop
            == data.store.block_slice(
                config["splits"][name]["start"], config["splits"][name]["end_exclusive"]
            ).stop
            - purge_hours
            for name in ("model_fit", "calibration", "selection", "stability")
        ),
        "all_last_labels_end_before_role_boundary": all(
            bool(row["last_label_end_before_declared_end"])
            for row in split_boundary_evidence["roles"].values()
        ),
    }
    decision["reference_supersession"] = {
        "status": "PRIOR_UNPURGED_REFERENCE_SUPERSEDED",
        "policy": reference_policy,
        "mismatched_prediction_identities": int(
            sum(not row["match"] for row in prediction_identity_rows)
        ),
        "total_prediction_identities": int(len(prediction_identity_rows)),
        "reason": "The prior run neither purged the final execution-delay-plus-horizon coordinates nor separated model fitting from calibration.",
    }
    decision["bias_audit"] = {
        "decision": "PASS" if all(bias_checks.values()) else "HOLD_RESEARCH",
        "requested_stage": "development-only matched replay",
        "discovery_status": "predeclared repair reproduction",
        "OOS_sample_grade": "NONE_SPENT_DEVELOPMENT_EVIDENCE",
        "checks": bias_checks,
        "feature_date": "signal timestamp",
        "execution_date": "signal timestamp plus 2h",
        "label_horizon": "4h after execution",
        "cost_model": "full-L1 5 bps with initial establishment and terminal liquidation",
        "cannot_infer": [
            "OOS qualification",
            "candidate promotion",
            "future performance",
            "independent statistical power from four model arms",
            "survivorship-complete observed archive",
        ],
    }
    if decision["bias_audit"]["decision"] != "PASS":
        decision["status"] = "BROAD_CALIBRATED_STICKY_BIAS_AUDIT_HOLD"
    elif decision["train_only_calibrated_sticky"]["development_increment_observed"]:
        decision["status"] = "POST_HOC_DEVELOPMENT_CALIBRATION_INCREMENT_OBSERVED"
    else:
        decision["status"] = "BROAD_PURGED_CALIBRATED_STICKY_INCREMENT_NOT_ESTABLISHED"

    _write_jsonl(output_root / "model_evidence.jsonl", model_rows)
    _write_jsonl(output_root / "train_calibration_evidence.jsonl", calibration_rows)
    _write_jsonl(output_root / "prediction_identity_evidence.jsonl", prediction_identity_rows)
    _write_jsonl(output_root / "paired_increment_evidence.jsonl", increment_rows)
    _write_jsonl(output_root / "mapping_repair_evidence.jsonl", mapping_rows)
    _write_jsonl(output_root / "sticky_surface_evidence.jsonl", sticky_surface_rows)
    _write_jsonl(output_root / "sticky_pair_evidence.jsonl", sticky_pair_rows)
    _write_jsonl(output_root / "calibrated_sticky_surface_evidence.jsonl", calibrated_surface_rows)
    _write_jsonl(output_root / "calibrated_sticky_pair_evidence.jsonl", calibrated_pair_rows)
    _write_json(output_root / "decision.json", decision)

    input_paths = {
        name: ROOT / value for name, value in config["inputs"].items() if name != "broad_cache"
    }
    cache_metadata = ROOT / config["inputs"]["broad_cache"] / "metadata.json"
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "objective": config["objective"],
        "status": decision["status"],
        "source_sha": _git_sha(),
        "created_at": _now(),
        "command": "python scripts/crypto_broad_core_pack_information_arena_v1.py",
        "parameters": {
            key: config[key]
            for key in (
                "splits",
                "label_boundary_contract",
                "information",
                "models",
                "data_adequacy",
                "mapping_repair",
                "turnover_aware_mapping",
                "reference_prediction_policy",
                "train_only_calibration",
                "frozen_budget",
                "economic_contract",
            )
        },
        "input_identities": {
            **{f"{name}_sha256": sha256_file(path) for name, path in input_paths.items()},
            "broad_cache_metadata_sha256": sha256_file(cache_metadata),
            "broad_cache_identity_sha256": json.loads(cache_metadata.read_text())["identity_sha256"],
        },
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "sklearn": sklearn.__version__,
        },
        "data_adequacy": adequacy,
        "model_fit_identity": model_fit_identity,
        "split_boundary_evidence": split_boundary_evidence,
        "decision": decision,
        "economic_mapping_sha256": mapping_contract_sha256(DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]),
        "cost_time": {
            "estimated_wall_minutes": config["frozen_budget"]["estimated_wall_minutes"],
            "estimated_peak_memory_gb": config["frozen_budget"]["estimated_peak_memory_gb"],
            "actual_wall_seconds": float(time.perf_counter() - started),
        },
        "boundaries": config["boundaries"],
        "reproducibility": {
            "reproducible": True,
            "continuation": "Rerun the exact command at source_sha with the same content-hash-bound inputs; do not tune models or open sealed roles.",
            "failure": None,
        },
        "files": {},
    }
    manifest["identity_sha256"] = payload_sha256({key: value for key, value in manifest.items() if key != "files"})
    report_path.write_text(_report(manifest, decision, adequacy, information), encoding="utf-8", newline="\n")
    for path in (
        output_root / "data_adequacy.json",
        output_root / "split_boundary_evidence.json",
        information_path,
        output_root / "model_evidence.jsonl",
        output_root / "train_calibration_evidence.jsonl",
        output_root / "prediction_identity_evidence.jsonl",
        output_root / "paired_increment_evidence.jsonl",
        output_root / "mapping_repair_evidence.jsonl",
        output_root / "sticky_surface_evidence.jsonl",
        output_root / "sticky_pair_evidence.jsonl",
        output_root / "calibrated_sticky_surface_evidence.jsonl",
        output_root / "calibrated_sticky_pair_evidence.jsonl",
        output_root / "decision.json",
        report_path,
    ):
        manifest["files"][path.relative_to(ROOT).as_posix()] = sha256_file(path)
    _write_json(output_root / "run_manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "config/crypto_broad_core_pack_information_arena_v1.json")
    args = parser.parse_args()
    print(json.dumps(run(args.config), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
