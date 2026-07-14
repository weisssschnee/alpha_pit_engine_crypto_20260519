from __future__ import annotations

import hashlib
import json
import math
import os
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .arena import (
    evaluate_common_bridge,
    long_only_topk_momentum_weights,
    one_over_n_weights,
    paired_increment,
)
from .deepdow_v023 import (
    _activate_dependency_path,
    _build_tensors,
    _native_metrics,
    _split_indices,
    verify_upstream as verify_deepdow_upstream,
)
from .qlib_v097 import _extract_position_weights, verify_upstream as verify_qlib_upstream
from .release import canonical_sha256, preflight_external_release, sha256_file


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def frame_identity(frame: pd.DataFrame) -> str:
    ordered = frame.sort_index().sort_index(axis=1)
    payload = pd.util.hash_pandas_object(ordered, index=True).to_numpy(dtype=np.uint64).tobytes()
    columns = json.dumps([str(column) for column in ordered.columns], separators=(",", ":")).encode()
    return hashlib.sha256(columns + payload).hexdigest().upper()


def _feature_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if isinstance(frame.columns, pd.MultiIndex):
        result = frame.xs("feature", axis=1, level=0, drop_level=True)
    else:
        result = frame.copy()
    result.columns = result.columns.astype(str)
    return result


def _label_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if isinstance(frame.columns, pd.MultiIndex):
        return frame.xs("label", axis=1, level=0, drop_level=True)
    return frame.loc[:, [column for column in frame.columns if "label" in str(column).lower()]]


def qlib_input_diagnostics(
    base_root: Path,
    splits: dict[str, Any],
) -> tuple[dict[str, Any], pd.DataFrame]:
    from qlib.data.dataset.handler import DataHandlerLP

    full_path = base_root / "qlib_handler_full_alpha158.pkl"
    control_path = base_root / "qlib_handler_first_13_control.pkl"
    full = DataHandlerLP.load(full_path)
    control = DataHandlerLP.load(control_path)
    full_raw = _feature_frame(full._data)
    full_infer = _feature_frame(full._infer)
    full_learn = _feature_frame(full._learn)
    control_raw = _feature_frame(control._data)
    control_learn = _feature_frame(control._learn)
    full_only = [column for column in full_raw.columns if column not in control_raw.columns]

    raw_non_null = full_raw.notna().mean()
    infer_non_null = full_infer.notna().mean()
    learn_non_null = full_learn.notna().mean()
    raw_variance = full_raw.var(ddof=0)
    learn_variance = full_learn.var(ddof=0)
    time_variance = full_raw.groupby(level="instrument", sort=False).var(ddof=0).mean(axis=0)
    cross_sectional_time_fraction = (
        full_raw.groupby(level="datetime", sort=False).var(ddof=0).gt(1e-15).mean(axis=0)
    )
    feature_rows = []
    for feature in full_raw.columns:
        feature_rows.append(
            {
                "feature": feature,
                "full_only": feature in full_only,
                "raw_non_null_rate": float(raw_non_null[feature]),
                "infer_non_null_rate": float(infer_non_null[feature]),
                "learn_non_null_rate": float(learn_non_null[feature]),
                "raw_variance": float(raw_variance[feature]),
                "learn_variance": float(learn_variance[feature]),
                "mean_within_symbol_time_variance": float(time_variance[feature]),
                "fraction_dates_with_cross_sectional_variance": float(
                    cross_sectional_time_fraction[feature]
                ),
                "raw_unique_values": int(full_raw[feature].nunique(dropna=True)),
            }
        )
    feature_stats = pd.DataFrame(feature_rows)

    label_rows = []
    for variant, handler in (("FULL_ALPHA158", full), ("FIRST_13_CONTROL", control)):
        for stage, frame in (("raw", handler._data), ("infer", handler._infer), ("learn", handler._learn)):
            label = _label_frame(frame).iloc[:, 0]
            dates = label.index.get_level_values("datetime")
            for split, split_range in splits.items():
                if split not in {"train", "valid", "development_holdout"}:
                    continue
                start, end = split_range
                mask = (dates >= pd.Timestamp(start)) & (dates <= pd.Timestamp(end))
                values = label.loc[mask]
                label_rows.append(
                    {
                        "variant": variant,
                        "stage": stage,
                        "split": split,
                        "rows": int(len(values)),
                        "valid_rows": int(values.notna().sum()),
                        "support": float(values.notna().mean()) if len(values) else float("nan"),
                        "variance": float(values.var(ddof=0)),
                        "unique_values": int(values.nunique(dropna=True)),
                    }
                )
    label_stats = pd.DataFrame(label_rows)
    full_only_stats = feature_stats[feature_stats.full_only]
    summary = {
        "full_schema_count": int(full_raw.shape[1]),
        "control_schema_count": int(control_raw.shape[1]),
        "full_only_feature_count": len(full_only),
        "full_only_all_positive_raw_variance": bool((full_only_stats.raw_variance > 0).all()),
        "full_only_all_time_varying": bool(
            (full_only_stats.mean_within_symbol_time_variance > 0).all()
        ),
        "full_only_min_raw_non_null_rate": float(full_only_stats.raw_non_null_rate.min()),
        "full_handler_sha256": sha256_file(full_path),
        "control_handler_sha256": sha256_file(control_path),
        "handler_artifact_identity_reused": sha256_file(full_path) == sha256_file(control_path),
        "full_raw_matrix_sha256": frame_identity(full_raw),
        "control_raw_matrix_sha256": frame_identity(control_raw),
        "full_learn_matrix_sha256": frame_identity(full_learn),
        "control_learn_matrix_sha256": frame_identity(control_learn),
        "raw_matrix_identical": full_raw.equals(control_raw),
        "processor_retention": {
            "full": {
                "raw_features": int(_feature_frame(full._data).shape[1]),
                "infer_features": int(_feature_frame(full._infer).shape[1]),
                "learn_features": int(_feature_frame(full._learn).shape[1]),
                "raw_rows": int(len(full._data)),
                "infer_rows": int(len(full._infer)),
                "learn_rows": int(len(full._learn)),
                "learn_processors": [type(item).__name__ for item in full.learn_processors],
            },
            "control": {
                "raw_features": int(_feature_frame(control._data).shape[1]),
                "infer_features": int(_feature_frame(control._infer).shape[1]),
                "learn_features": int(_feature_frame(control._learn).shape[1]),
                "raw_rows": int(len(control._data)),
                "infer_rows": int(len(control._infer)),
                "learn_rows": int(len(control._learn)),
                "learn_processors": [type(item).__name__ for item in control.learn_processors],
            },
        },
        "label_stats": label_stats.to_dict(orient="records"),
    }
    return summary, feature_stats


def _prediction_comparison(predictions: pd.DataFrame) -> dict[str, Any]:
    pivot = predictions.pivot(index=["datetime", "instrument"], columns="variant", values="score")
    full = pivot["FULL_ALPHA158"]
    control = pivot["FIRST_13_CONTROL"]
    difference = full - control
    exact = np.array_equal(full.to_numpy(), control.to_numpy(), equal_nan=True)
    per_date = predictions.groupby(["variant", "datetime"], sort=True).score.nunique(dropna=False)
    unique_summary: dict[str, Any] = {}
    for variant in predictions.variant.unique():
        values = per_date.loc[variant]
        unique_summary[str(variant)] = {
            "min": int(values.min()),
            "median": float(values.median()),
            "max": int(values.max()),
        }
    return {
        "rows": int(len(pivot)),
        "exact_equality": bool(exact),
        "exact_equal_rows": int((difference == 0).sum()),
        "max_absolute_difference": float(difference.abs().max()),
        "mean_absolute_difference": float(difference.abs().mean()),
        "value_correlation": float(full.corr(control)) if full.nunique() > 1 and control.nunique() > 1 else None,
        "rank_correlation": float(full.corr(control, method="spearman"))
        if full.nunique() > 1 and control.nunique() > 1
        else None,
        "cross_sectional_unique_counts": unique_summary,
        "full_value_variance": float(full.var(ddof=0)),
        "control_value_variance": float(control.var(ddof=0)),
        "difference_is_only_report_rounding": bool(not exact and difference.abs().max() < 5e-13),
    }


def _weight_comparison(full: pd.DataFrame, control: pd.DataFrame) -> dict[str, Any]:
    dates = full.index.intersection(control.index)
    columns = full.columns.union(control.columns)
    left = full.reindex(index=dates, columns=columns, fill_value=0.0)
    right = control.reindex(index=dates, columns=columns, fill_value=0.0)
    absolute = (left - right).abs()
    daily_l1 = absolute.sum(axis=1)
    return {
        "dates": int(len(dates)),
        "exact_equality": bool(np.array_equal(left.to_numpy(), right.to_numpy(), equal_nan=True)),
        "exact_equal_dates": int((daily_l1 == 0).sum()),
        "mean_daily_l1_difference": float(daily_l1.mean()),
        "max_daily_l1_difference": float(daily_l1.max()),
        "mean_absolute_cell_difference": float(absolute.to_numpy().mean()),
        "full_matrix_sha256": frame_identity(left),
        "control_matrix_sha256": frame_identity(right),
    }


def _fit_qlib_variant(
    handler_path: Path,
    variant: str,
    qlib_config: dict[str, Any],
    splits: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any], pd.DataFrame]:
    from qlib.contrib.eva.alpha import calc_ic
    from qlib.contrib.evaluate import backtest_daily, risk_analysis
    from qlib.contrib.model.gbdt import LGBModel
    from qlib.contrib.strategy import TopkDropoutStrategy
    from qlib.data.dataset import DatasetH
    from qlib.data.dataset.handler import DataHandlerLP
    from qlib.workflow import R

    handler = DataHandlerLP.load(handler_path)
    dataset = DatasetH(
        handler=handler,
        segments={
            "train": tuple(splits["train"]),
            "valid": tuple(splits["valid"]),
            "test": tuple(splits["development_holdout"]),
        },
    )
    model_kwargs = dict(qlib_config["model"])
    num_boost_round = int(model_kwargs.pop("num_boost_round"))
    early_stopping_rounds = int(model_kwargs.pop("early_stopping_rounds"))
    model = LGBModel(
        num_boost_round=num_boost_round,
        early_stopping_rounds=early_stopping_rounds,
        **model_kwargs,
    )
    evals_result: dict[str, Any] = {}
    started = time.perf_counter()
    with R.start(
        experiment_name="crypto_frontier_evidence_qualification",
        recorder_name=variant.lower(),
    ):
        model.fit(dataset, evals_result=evals_result, verbose_eval=0)
        prediction = model.predict(dataset, segment="test")
    runtime = time.perf_counter() - started
    prediction.name = "score"
    raw_label = dataset.prepare("test", col_set="label", data_key=DataHandlerLP.DK_R).iloc[:, 0]
    ic, ric = calc_ic(prediction, raw_label)
    strategy = TopkDropoutStrategy(
        signal=prediction,
        topk=int(qlib_config["topk"]),
        n_drop=int(qlib_config["n_drop"]),
    )
    test_start, test_end = splits["development_holdout"]
    report, positions = backtest_daily(
        start_time=test_start,
        end_time=test_end,
        strategy=strategy,
        account=float(qlib_config["account"]),
        benchmark=qlib_config["benchmark"],
        exchange_kwargs={
            "freq": "day",
            "limit_threshold": None,
            "deal_price": "close",
            "open_cost": float(qlib_config["open_cost"]),
            "close_cost": float(qlib_config["close_cost"]),
            "min_cost": float(qlib_config["min_cost"]),
            "trade_unit": 1,
        },
    )
    symbols = sorted(prediction.index.get_level_values("instrument").str.upper().unique())
    position_weights = _extract_position_weights(positions, symbols)
    decision_weights = position_weights.copy()
    decision_weights.index = decision_weights.index - pd.Timedelta(days=1)
    prediction_dates = pd.DatetimeIndex(prediction.index.get_level_values("datetime").unique()).tz_localize("UTC")
    decision_weights = decision_weights.loc[decision_weights.index.intersection(prediction_dates)]
    pred_frame = prediction.rename("score").reset_index()
    pred_frame["instrument"] = pred_frame.instrument.str.upper()
    pred_frame["variant"] = variant

    booster = model.model
    feature_columns = _feature_frame(
        dataset.prepare("train", col_set="feature", data_key=DataHandlerLP.DK_I)
    ).columns.tolist()
    split_importance = booster.feature_importance(importance_type="split")
    gain_importance = booster.feature_importance(importance_type="gain")
    importance = pd.DataFrame(
        {
            "variant": variant,
            "feature": feature_columns,
            "split_importance": split_importance,
            "gain_importance": gain_importance,
        }
    )
    train_losses = list(evals_result.get("train", {}).get("l2", []))
    valid_losses = list(evals_result.get("valid", {}).get("l2", []))
    native_net_excess = report["return"] - report["bench"] - report["cost"]
    native_risk = risk_analysis(native_net_excess, freq="day")
    diagnostics = {
        "variant": variant,
        "fit_runtime_seconds": runtime,
        "best_iteration": int(booster.best_iteration),
        "num_trees": int(booster.num_trees()),
        "train_rows": int(len(dataset.prepare("train", col_set="feature", data_key=DataHandlerLP.DK_I))),
        "valid_rows": int(len(dataset.prepare("valid", col_set="feature", data_key=DataHandlerLP.DK_I))),
        "development_holdout_rows": int(len(prediction)),
        "train_loss_first": float(train_losses[0]) if train_losses else None,
        "train_loss_last": float(train_losses[-1]) if train_losses else None,
        "train_loss_min": float(min(train_losses)) if train_losses else None,
        "valid_loss_first": float(valid_losses[0]) if valid_losses else None,
        "valid_loss_last": float(valid_losses[-1]) if valid_losses else None,
        "valid_loss_min": float(min(valid_losses)) if valid_losses else None,
        "loss_changed": bool(train_losses and max(train_losses) - min(train_losses) > 1e-12),
        "nonzero_split_importance_features": int((split_importance > 0).sum()),
        "nonzero_gain_importance_features": int((gain_importance > 0).sum()),
        "total_split_nodes": int(split_importance.sum()),
        "model_string_sha256": hashlib.sha256(booster.model_to_string().encode()).hexdigest().upper(),
        "evals_result": evals_result,
        "native_metrics": {
            "IC": float(ic.mean()),
            "ICIR": float(ic.mean() / ic.std(ddof=1)),
            "Rank_IC": float(ric.mean()),
            "Rank_ICIR": float(ric.mean() / ric.std(ddof=1)),
            **{f"net_excess_{key}": float(value) for key, value in native_risk.risk.items()},
        },
    }
    return decision_weights, pred_frame, diagnostics, importance


def run_qlib_qualification(
    daily: pd.DataFrame,
    base_config: dict[str, Any],
    qualification_config: dict[str, Any],
    base_root: Path,
    output_root: Path,
) -> dict[str, Any]:
    import qlib
    from qlib.config import REG_US

    input_summary, feature_stats = qlib_input_diagnostics(base_root, base_config["splits"])
    original_predictions = pd.read_parquet(base_root / "qlib_v097" / "native_predictions.parquet")
    original_weights = pd.read_parquet(base_root / "qlib_v097" / "native_position_weights.parquet")
    if {"date", "symbol", "weight", "system_id"}.issubset(original_weights.columns):
        original_weights["date"] = pd.to_datetime(original_weights.date, utc=True)
        original_full_weights = original_weights[
            original_weights.system_id.eq("QLIB_V097_NATIVE_FULL")
        ].pivot(index="date", columns="symbol", values="weight")
        original_control_weights = original_weights[
            original_weights.system_id.eq("QLIB_V097_NATIVE_13_FEATURE_CONTROL")
        ].pivot(index="date", columns="symbol", values="weight")
    else:
        raise ValueError("unexpected original Qlib weight artifact schema")
    original_prediction_comparison = _prediction_comparison(original_predictions)
    original_weight_comparison = _weight_comparison(original_full_weights, original_control_weights)
    original_ledger = pd.read_csv(base_root / "qlib_v097" / "training_ledger.csv")
    original_model_fit_degenerate = bool(
        (original_ledger.best_iteration <= 1).all()
        and all(
            max(json.loads(row.evals_result)["train"]["l2"])
            - min(json.loads(row.evals_result)["train"]["l2"])
            <= 1e-12
            for row in original_ledger.itertuples()
        )
    )
    original_classification = (
        "COMPETITOR_COMPARISON_DEGENERATE"
        if input_summary["raw_matrix_identical"]
        else "MODEL_FIT_DEGENERATE"
        if original_model_fit_degenerate
        else "PORTFOLIO_MAPPING_COLLAPSE"
        if original_prediction_comparison["exact_equality"] or original_weight_comparison["exact_equality"]
        else "UNQUALIFIED"
    )

    repaired_config = json.loads(json.dumps(base_config["qlib"]))
    repaired_config["model"].update(qualification_config["qlib_one_shot_repair"]["model_overrides"])
    verify_qlib_upstream(repaired_config)
    qlib.init(
        provider_uri=str(base_root / "qlib_provider"),
        region=REG_US,
        kernels=int(repaired_config["provider_workers"]),
        joblib_backend=str(repaired_config["joblib_backend"]),
    )
    results: dict[str, Any] = {}
    importance_frames = []
    prediction_frames = []
    for variant, handler_name in (
        ("FULL_ALPHA158", "qlib_handler_full_alpha158.pkl"),
        ("FIRST_13_CONTROL", "qlib_handler_first_13_control.pkl"),
    ):
        weights, predictions, diagnostics, importance = _fit_qlib_variant(
            base_root / handler_name,
            variant,
            repaired_config,
            base_config["splits"],
        )
        results[variant] = {"weights": weights, "diagnostics": diagnostics}
        prediction_frames.append(predictions)
        importance_frames.append(importance)
    repaired_predictions = pd.concat(prediction_frames, ignore_index=True)
    repaired_importance = pd.concat(importance_frames, ignore_index=True)
    repaired_prediction_comparison = _prediction_comparison(repaired_predictions)
    repaired_weight_comparison = _weight_comparison(
        results["FULL_ALPHA158"]["weights"], results["FIRST_13_CONTROL"]["weights"]
    )
    repaired_model_fit_degenerate = any(
        not item["diagnostics"]["loss_changed"]
        or item["diagnostics"]["nonzero_split_importance_features"] == 0
        for item in results.values()
    ) or any(
        repaired_prediction_comparison[f"{name}_value_variance"] <= 1e-15
        for name in ("full", "control")
    )
    repaired_mapping_collapse = bool(
        not repaired_prediction_comparison["exact_equality"] and repaired_weight_comparison["exact_equality"]
    )
    repaired_status_before_adequacy = (
        "MODEL_FIT_DEGENERATE"
        if repaired_model_fit_degenerate
        else "PORTFOLIO_MAPPING_COLLAPSE"
        if repaired_mapping_collapse
        else "EFFECTIVE_DIFFERENCE_PRESENT"
    )

    qlib_dir = output_root / "qlib"
    qlib_dir.mkdir(parents=True, exist_ok=True)
    feature_stats.to_csv(qlib_dir / "full_feature_qualification.csv", index=False, lineterminator="\n")
    repaired_predictions.to_csv(qlib_dir / "repaired_predictions.csv", index=False, lineterminator="\n")
    repaired_importance.to_csv(qlib_dir / "repaired_feature_importance.csv", index=False, lineterminator="\n")
    weight_frames = []
    for variant, item in results.items():
        long = item["weights"].stack().rename("weight").reset_index()
        long.columns = ["date", "symbol", "weight"]
        long["variant"] = variant
        weight_frames.append(long)
    repaired_weights_long = pd.concat(weight_frames, ignore_index=True)
    repaired_weights_long.to_csv(qlib_dir / "repaired_position_weights.csv", index=False, lineterminator="\n")
    qualification = {
        "original_classification": original_classification,
        "original_input": input_summary,
        "original_predictions": original_prediction_comparison,
        "original_weights": original_weight_comparison,
        "original_model_fit_degenerate": original_model_fit_degenerate,
        "repair": qualification_config["qlib_one_shot_repair"],
        "repaired_model_diagnostics": {
            variant: item["diagnostics"] for variant, item in results.items()
        },
        "repaired_predictions": repaired_prediction_comparison,
        "repaired_weights": repaired_weight_comparison,
        "repaired_status_before_data_adequacy": repaired_status_before_adequacy,
        "artifact_identity_reused": False,
        "same_frozen_fit_count": len(results) == int(qualification_config["qlib_one_shot_repair"]["fixed_fits"]),
        "parameter_search_performed": False,
        "scope": "development-only fixed core10; no OOS or promotion conclusion",
    }
    write_json(qlib_dir / "qualification.json", qualification)
    return {
        "qualification": qualification,
        "full_weights": results["FULL_ALPHA158"]["weights"],
        "control_weights": results["FIRST_13_CONTROL"]["weights"],
        "feature_stats": feature_stats,
    }


def _parameter_vector(network: Any) -> np.ndarray:
    import torch

    tensors = [parameter.detach().cpu().reshape(-1) for parameter in network.parameters()]
    return torch.cat(tensors).numpy() if tensors else np.array([], dtype=float)


def _deepdow_fit_one(
    X: np.ndarray,
    y: np.ndarray,
    decision_dates: pd.DatetimeIndex,
    symbols: list[str],
    split_indices: dict[str, list[int]],
    config: dict[str, Any],
    *,
    seed: int,
    variant: str,
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, float], pd.DataFrame, pd.DataFrame]:
    import torch
    from deepdow.benchmarks import InverseVolatility, OneOverN
    from deepdow.callbacks import Callback
    from deepdow.data import InRAMDataset, RigidDataLoader, Scale, prepare_standard_scaler
    from deepdow.experiments import Run
    from deepdow.losses import MaximumDrawdown, MeanReturns, SharpeRatio, SquaredWeights
    from deepdow.nn import KeynesNet

    class EvidenceCallback(Callback):
        def __init__(self) -> None:
            self.rows: list[dict[str, Any]] = []
            self.initial_parameters: np.ndarray | None = None

        def on_train_begin(self, metadata: dict[str, Any]) -> None:
            self.initial_parameters = _parameter_vector(self.run.network)

        def on_batch_end(self, metadata: dict[str, Any]) -> None:
            gradients = [
                parameter.grad.detach().cpu().reshape(-1)
                for parameter in self.run.network.parameters()
                if parameter.grad is not None
            ]
            grad_norm = float(torch.linalg.vector_norm(torch.cat(gradients)).item()) if gradients else 0.0
            weights = metadata["weights"].detach().cpu()
            self.rows.append(
                {
                    "epoch": int(metadata["epoch"]),
                    "batch": int(metadata["batch"]),
                    "batch_loss": float(metadata["batch_loss"]),
                    "gradient_l2_norm": grad_norm,
                    "batch_weight_variance": float(weights.var(unbiased=False).item()),
                    "batch_weight_min": float(weights.min().item()),
                    "batch_weight_max": float(weights.max().item()),
                }
            )

    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.set_num_threads(1)
    means, stds = prepare_standard_scaler(X, indices=split_indices["train"])
    dataset = InRAMDataset(
        X,
        y,
        timestamps=decision_dates,
        asset_names=symbols,
        transform=Scale(means, stds),
    )
    batch_size = int(config["training"]["batch_size"])
    train_loader = RigidDataLoader(dataset, indices=split_indices["train"], batch_size=batch_size)
    valid_loader = RigidDataLoader(dataset, indices=split_indices["valid"], batch_size=batch_size)
    network = KeynesNet(
        n_input_channels=X.shape[1],
        hidden_size=int(config["network"]["hidden_size"]),
        transform_type=config["network"]["transform_type"],
        n_groups=int(config["network"]["n_groups"]),
    )
    loss = SharpeRatio(input_type="simple", eps=float(config["loss"]["eps"])) + float(
        config["loss"]["squared_weight_coefficient"]
    ) * SquaredWeights()
    optimizer = torch.optim.Adam(
        network.parameters(),
        lr=float(config["training"]["learning_rate"]),
        amsgrad=bool(config["training"]["amsgrad"]),
    )
    evidence_callback = EvidenceCallback()
    run = Run(
        network,
        loss,
        train_loader,
        val_dataloaders={"valid": valid_loader},
        metrics={
            "native_sharpe": SharpeRatio(input_type="simple", eps=float(config["loss"]["eps"])),
            "native_mean_return": MeanReturns(input_type="simple"),
            "native_max_drawdown": MaximumDrawdown(input_type="simple"),
        },
        benchmarks={"one_over_n": OneOverN(), "inverse_volatility": InverseVolatility()},
        optimizer=optimizer,
        device=torch.device("cpu"),
        dtype=torch.float32,
        callbacks=[evidence_callback],
    )
    started = time.perf_counter()
    history = run.launch(int(config["training"]["epochs"]))
    runtime = time.perf_counter() - started
    final_parameters = _parameter_vector(network)
    initial_parameters = evidence_callback.initial_parameters
    if initial_parameters is None:
        raise RuntimeError("DeepDow initial parameters were not captured")
    eval_ix = split_indices["development_holdout"]
    X_eval = (X[eval_ix] - means[None, :, None, None]) / stds[None, :, None, None]
    network.eval()
    with torch.no_grad():
        weights = network(torch.as_tensor(X_eval, dtype=torch.float32)).cpu().numpy()
    weights_frame = pd.DataFrame(weights, index=decision_dates[eval_ix], columns=symbols)
    native = _native_metrics(weights, y[eval_ix])
    batch_frame = pd.DataFrame(evidence_callback.rows)
    batch_frame["variant"] = variant
    batch_frame["seed"] = seed
    history_frame = history.metrics.reset_index()
    history_frame["variant"] = variant
    history_frame["seed"] = seed
    ledger = {
        "variant": variant,
        "seed": seed,
        "fit_runtime_seconds": runtime,
        "epochs": int(config["training"]["epochs"]),
        "train_samples": len(split_indices["train"]),
        "valid_samples": len(split_indices["valid"]),
        "development_holdout_samples": len(eval_ix),
        "parameter_count": int(len(final_parameters)),
        "parameter_l2_change": float(np.linalg.norm(final_parameters - initial_parameters)),
        "initial_parameter_sha256": hashlib.sha256(initial_parameters.tobytes()).hexdigest().upper(),
        "final_parameter_sha256": hashlib.sha256(final_parameters.tobytes()).hexdigest().upper(),
        "mean_gradient_l2_norm": float(batch_frame.gradient_l2_norm.mean()),
        "min_gradient_l2_norm": float(batch_frame.gradient_l2_norm.min()),
        "max_gradient_l2_norm": float(batch_frame.gradient_l2_norm.max()),
        "first_batch_loss": float(batch_frame.batch_loss.iloc[0]),
        "last_batch_loss": float(batch_frame.batch_loss.iloc[-1]),
        "min_batch_loss": float(batch_frame.batch_loss.min()),
        "eval_weight_variance": float(np.var(weights)),
        "eval_cross_asset_weight_std_mean": float(np.std(weights, axis=1).mean()),
        "eval_max_weight": float(weights.max()),
        "eval_min_weight": float(weights.min()),
    }
    return weights_frame, ledger, native, batch_frame, history_frame


def _effective_sample_size(values: np.ndarray, max_lag: int) -> float:
    clean = np.asarray(values, dtype=float)
    clean = clean[np.isfinite(clean)]
    n = len(clean)
    if n < 3 or np.var(clean) == 0:
        return float(n)
    centered = clean - clean.mean()
    variance = float(np.dot(centered, centered) / n)
    autocorrelations = []
    for lag in range(1, min(max_lag, n - 1) + 1):
        rho = float(np.dot(centered[:-lag], centered[lag:]) / ((n - lag) * variance))
        if rho <= 0:
            break
        autocorrelations.append((1.0 - lag / n) * rho)
    denominator = 1.0 + 2.0 * sum(autocorrelations)
    return float(max(1.0, min(n, n / denominator)))


def _interval_statistics(
    decision_dates: pd.DatetimeIndex,
    split_indices: dict[str, list[int]],
    gap_days: int,
    horizon_days: int,
) -> dict[str, Any]:
    intervals = []
    for index, decision in enumerate(decision_dates):
        start = decision + pd.Timedelta(days=gap_days + 1)
        end = start + pd.Timedelta(days=horizon_days - 1)
        intervals.append((index, start, end))
    split_stats: dict[str, Any] = {}
    split_intervals: dict[str, list[tuple[int, pd.Timestamp, pd.Timestamp]]] = {}
    for split, indices in split_indices.items():
        selected = [intervals[index] for index in indices]
        split_intervals[split] = selected
        independent = 0
        last_end: pd.Timestamp | None = None
        for _, start, end in selected:
            if last_end is None or start > last_end:
                independent += 1
                last_end = end
        adjacent_overlap = sum(
            1 for left, right in zip(selected, selected[1:]) if right[1] <= left[2]
        )
        split_stats[split] = {
            "windows": len(selected),
            "max_nonoverlapping_target_windows": independent,
            "adjacent_overlapping_target_pairs": adjacent_overlap,
            "first_target_start": str(selected[0][1]),
            "last_target_end": str(selected[-1][2]),
        }
    cross_split_overlap = 0
    ordered = ["train", "valid", "development_holdout"]
    for left_name, right_name in zip(ordered, ordered[1:]):
        left = split_intervals[left_name]
        right = split_intervals[right_name]
        cross_split_overlap += sum(
            1 for _, left_start, left_end in left for _, right_start, right_end in right
            if left_start <= right_end and right_start <= left_end
        )
    return {"splits": split_stats, "cross_split_target_overlap_pairs": cross_split_overlap}


def _allocation_summary(weights: pd.DataFrame) -> dict[str, Any]:
    values = weights.to_numpy(dtype=float)
    equal = np.full_like(values, 1.0 / values.shape[1])
    entropy = -(np.clip(values, 1e-15, None) * np.log(np.clip(values, 1e-15, None))).sum(axis=1)
    return {
        "cross_asset_std_mean": float(values.std(axis=1).mean()),
        "mean_daily_l1_from_one_over_n": float(np.abs(values - equal).sum(axis=1).mean()),
        "max_daily_l1_from_one_over_n": float(np.abs(values - equal).sum(axis=1).max()),
        "normalized_entropy_mean": float((entropy / math.log(values.shape[1])).mean()),
        "hhi_mean": float(np.square(values).sum(axis=1).mean()),
        "max_weight": float(values.max()),
        "min_weight": float(values.min()),
        "top_asset_by_average_weight": str(weights.mean().idxmax()),
        "top_asset_average_weight": float(weights.mean().max()),
        "most_concentrated_date": str(weights.apply(lambda row: np.square(row).sum(), axis=1).idxmax()),
    }


def run_deepdow_qualification(
    daily: pd.DataFrame,
    base_config: dict[str, Any],
    output_root: Path,
) -> dict[str, Any]:
    config = base_config["deepdow"]
    verify_deepdow_upstream(config)
    _activate_dependency_path(config)
    full_X, y, decision_dates, symbols = _build_tensors(daily, config, rotate_flow_assets=False)
    control_X, control_y, control_dates, control_symbols = _build_tensors(
        daily, config, rotate_flow_assets=True
    )
    if not np.array_equal(y, control_y) or not decision_dates.equals(control_dates) or symbols != control_symbols:
        raise RuntimeError("DeepDow qualification control identity drift")
    split_indices = _split_indices(decision_dates, base_config["splits"])
    per_variant: dict[str, list[pd.DataFrame]] = {"CHALLENGER": [], "ASSET_ROTATED_CONTROL": []}
    ledger_rows: list[dict[str, Any]] = []
    native_rows: list[dict[str, Any]] = []
    batch_frames = []
    history_frames = []
    per_seed_frames = []
    for variant, X in (("CHALLENGER", full_X), ("ASSET_ROTATED_CONTROL", control_X)):
        for seed in config["training"]["seeds"]:
            weights, ledger, native, batches, history = _deepdow_fit_one(
                X,
                y,
                decision_dates,
                symbols,
                split_indices,
                config,
                seed=int(seed),
                variant=variant,
            )
            per_variant[variant].append(weights)
            ledger_rows.append(ledger)
            native_rows.append({"variant": variant, "seed": int(seed), **native})
            batch_frames.append(batches)
            history_frames.append(history)
            long = weights.stack().rename("weight").reset_index()
            long.columns = ["date", "symbol", "weight"]
            long["variant"] = variant
            long["seed"] = int(seed)
            per_seed_frames.append(long)
    challenger = sum(per_variant["CHALLENGER"]) / len(per_variant["CHALLENGER"])
    control = sum(per_variant["ASSET_ROTATED_CONTROL"]) / len(per_variant["ASSET_ROTATED_CONTROL"])
    same_seed_comparisons = []
    for ordinal, seed in enumerate(config["training"]["seeds"]):
        comparison = _weight_comparison(
            per_variant["CHALLENGER"][ordinal], per_variant["ASSET_ROTATED_CONTROL"][ordinal]
        )
        same_seed_comparisons.append({"seed": int(seed), **comparison})
    cross_seed_comparisons = []
    for variant in per_variant:
        comparison = _weight_comparison(per_variant[variant][0], per_variant[variant][1])
        cross_seed_comparisons.append({"variant": variant, **comparison})

    interval_stats = _interval_statistics(
        decision_dates,
        split_indices,
        int(config["execution_gap_days"]),
        int(config["horizon_days"]),
    )
    label_signal = y[:, 0].mean(axis=(1, 2))
    tensor_stats = {
        "windows": int(len(full_X)),
        "input_shape": list(full_X.shape),
        "target_shape": list(y.shape),
        "input_non_null_rate": float(np.isfinite(full_X).mean()),
        "target_non_null_rate": float(np.isfinite(y[:, 0]).mean()),
        "input_channel_variance": [float(np.var(full_X[:, index])) for index in range(full_X.shape[1])],
        "target_return_variance": float(np.var(y[:, 0])),
        "control_input_exactly_equal": bool(np.array_equal(full_X, control_X)),
        "return_channel_exactly_equal": bool(np.array_equal(full_X[:, 0], control_X[:, 0])),
        "flow_channels_exactly_equal": bool(np.array_equal(full_X[:, 1:], control_X[:, 1:])),
        "label_autocorrelation_effective_sample_size": _effective_sample_size(
            label_signal, int(config["horizon_days"])
        ),
        "intervals": interval_stats,
    }
    ledger = pd.DataFrame(ledger_rows)
    model_fit_degenerate = bool(
        (ledger.parameter_l2_change <= 1e-12).any()
        or (ledger.mean_gradient_l2_norm <= 1e-12).any()
        or (ledger.eval_weight_variance <= 1e-15).any()
    )
    weight_comparison = _weight_comparison(challenger, control)
    mapping_collapse = bool(weight_comparison["max_daily_l1_difference"] <= 1e-6)
    status_before_adequacy = (
        "MODEL_FIT_DEGENERATE"
        if model_fit_degenerate
        else "PORTFOLIO_MAPPING_COLLAPSE"
        if mapping_collapse
        else "EFFECTIVE_DIFFERENCE_PRESENT"
    )
    deepdow_dir = output_root / "deepdow"
    deepdow_dir.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(deepdow_dir / "model_training_diagnostics.csv", index=False, lineterminator="\n")
    pd.DataFrame(native_rows).to_csv(deepdow_dir / "native_metrics.csv", index=False, lineterminator="\n")
    pd.concat(batch_frames, ignore_index=True).to_csv(
        deepdow_dir / "batch_gradient_and_loss.csv", index=False, lineterminator="\n"
    )
    pd.concat(history_frames, ignore_index=True).to_csv(
        deepdow_dir / "upstream_history_metrics.csv", index=False, lineterminator="\n"
    )
    pd.concat(per_seed_frames, ignore_index=True).to_csv(
        deepdow_dir / "per_seed_position_weights.csv", index=False, lineterminator="\n"
    )
    qualification = {
        "tensor_and_sample_evidence": tensor_stats,
        "training_diagnostics": ledger.to_dict(orient="records"),
        "same_seed_challenger_control_weights": same_seed_comparisons,
        "cross_seed_weights": cross_seed_comparisons,
        "ensemble_challenger_control_weights": weight_comparison,
        "challenger_allocation": _allocation_summary(challenger),
        "control_allocation": _allocation_summary(control),
        "model_fit_degenerate": model_fit_degenerate,
        "portfolio_mapping_collapse": mapping_collapse,
        "status_before_data_adequacy": status_before_adequacy,
        "same_frozen_fit_count": len(ledger) == int(config["fixed_fits"]),
        "parameter_search_performed": False,
        "scope": "development-only fixed core10; overlapping five-day targets disclosed",
    }
    write_json(deepdow_dir / "qualification.json", qualification)
    return {
        "qualification": qualification,
        "challenger_weights": challenger,
        "control_weights": control,
        "tensor_stats": tensor_stats,
    }


def evaluate_data_adequacy(
    gate_config: dict[str, Any],
    actuals: dict[str, dict[str, float]],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows = []
    summaries: dict[str, Any] = {}
    mapping = {
        "development_dates": "min_development_dates",
        "training_samples": "min_training_samples",
        "cross_sectional_assets": "min_cross_sectional_assets",
        "feature_non_null_rate": "min_feature_non_null_rate",
        "positive_variance_feature_fraction": "min_positive_variance_feature_fraction",
        "history_days": "min_history_days",
        "label_support": "min_label_support",
        "turnover_observations": "min_turnover_observations",
        "independent_evaluation_blocks": "min_independent_evaluation_blocks",
    }
    for paradigm, thresholds in gate_config.items():
        actual = actuals[paradigm]
        failures = []
        for field, threshold_field in mapping.items():
            observed = float(actual[field])
            required = float(thresholds[threshold_field])
            passed = observed >= required
            if not passed:
                failures.append(field)
            rows.append(
                {
                    "paradigm": paradigm,
                    "condition": field,
                    "observed": observed,
                    "required_minimum": required,
                    "passed": passed,
                }
            )
        summaries[paradigm] = {
            "status": "PASS" if not failures else "DATA_ADEQUACY_UNDERPOWERED",
            "failed_conditions": failures,
            "actual": actual,
            "thresholds": thresholds,
        }
    return pd.DataFrame(rows), summaries


def run_corrected_arena(
    daily: pd.DataFrame,
    qlib_result: dict[str, Any],
    deepdow_result: dict[str, Any],
    base_config: dict[str, Any],
    output_root: Path,
) -> dict[str, Any]:
    common_dates = qlib_result["full_weights"].index.intersection(
        deepdow_result["challenger_weights"].index
    )
    systems = {
        "INTERNAL_LONG_ONLY_20D_MOMENTUM": long_only_topk_momentum_weights(daily, common_dates),
        "QLIB_V097_REPAIRED_FULL": qlib_result["full_weights"].loc[common_dates],
        "QLIB_V097_REPAIRED_13_FEATURE_CONTROL": qlib_result["control_weights"].loc[common_dates],
        "DEEPDOW_V023_KEYNESNET_FLOW": deepdow_result["challenger_weights"].loc[common_dates],
        "DEEPDOW_V023_ASSET_ROTATED_FLOW_CONTROL": deepdow_result["control_weights"].loc[common_dates],
        "ONE_OVER_N": one_over_n_weights(daily, common_dates),
    }
    arena_cfg = base_config["arena"]
    metric_rows = []
    path_frames = []
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
            bootstrap_seed=20260714 + ordinal,
        )
        metric_rows.append(asdict(metrics))
        path["system_id"] = system_id
        path_frames.append(path)
        paths[system_id] = path
    paired = pd.DataFrame(
        [
            paired_increment(
                paths["QLIB_V097_REPAIRED_FULL"],
                paths["QLIB_V097_REPAIRED_13_FEATURE_CONTROL"],
                challenger_id="QLIB_V097_REPAIRED_FULL",
                control_id="QLIB_V097_REPAIRED_13_FEATURE_CONTROL",
                block_days=arena_cfg["paired_block_bootstrap_days"],
                bootstrap_samples=arena_cfg["paired_bootstrap_samples"],
                seed=20260714,
            ),
            paired_increment(
                paths["DEEPDOW_V023_KEYNESNET_FLOW"],
                paths["DEEPDOW_V023_ASSET_ROTATED_FLOW_CONTROL"],
                challenger_id="DEEPDOW_V023_KEYNESNET_FLOW",
                control_id="DEEPDOW_V023_ASSET_ROTATED_FLOW_CONTROL",
                block_days=arena_cfg["paired_block_bootstrap_days"],
                bootstrap_samples=arena_cfg["paired_bootstrap_samples"],
                seed=20260715,
            ),
        ]
    )
    metrics = pd.DataFrame(metric_rows)
    paths_frame = pd.concat(path_frames, ignore_index=True)
    metrics.to_csv(output_root / "corrected_arena_metrics.csv", index=False, lineterminator="\n")
    paths_frame.to_csv(output_root / "corrected_arena_paths.csv", index=False, lineterminator="\n")
    paired.to_csv(output_root / "corrected_paired_comparisons.csv", index=False, lineterminator="\n")
    return {"systems": list(systems), "metrics": metrics, "paths": paths_frame, "paired": paired}


def base_bundle_attestation(repo: Path, base_root: Path) -> dict[str, Any]:
    index_path = base_root / "artifact_index.csv"
    index = pd.read_csv(index_path)
    records = index.to_dict(orient="records")
    computed_bundle = canonical_sha256(records)
    missing = []
    drift = []
    for row in index.itertuples():
        path = repo / row.artifact
        if not path.is_file():
            missing.append(row.artifact)
        elif sha256_file(path) != str(row.sha256).upper() or path.stat().st_size != int(row.size_bytes):
            drift.append(row.artifact)
    return {
        "artifact_index": index_path.relative_to(repo).as_posix(),
        "artifact_index_sha256": sha256_file(index_path),
        "artifact_count": int(len(index)),
        "bundle_sha256": computed_bundle,
        "content_verification": {
            "missing": missing,
            "drift": drift,
            "verified_count": int(len(index) - len(missing) - len(drift)),
        },
        "commit_policy": {
            "content_hash_manifest_committed": True,
            "evidence_artifacts_committed": True,
            "regenerable_provider_handler_and_tracking_caches_ignored": True,
        },
    }


def build_artifact_index(repo: Path, output_root: Path) -> dict[str, Any]:
    index_path = output_root / "artifact_index.csv"
    records = []
    for path in sorted(output_root.rglob("*")):
        if (
            not path.is_file()
            or path == index_path
            or path.name.startswith("runner.")
            or path.name in {"seal_result.json", "check_result.json"}
        ):
            continue
        records.append(
            {
                "artifact": path.relative_to(repo).as_posix(),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    pd.DataFrame(records).to_csv(index_path, index=False, lineterminator="\n")
    return {
        "artifact_count": len(records),
        "bundle_sha256": canonical_sha256(records),
        "artifact_index_sha256": sha256_file(index_path),
    }


def plan_new_release_activation(
    manifest_path: Path,
    base_config: dict[str, Any],
    qualification_config: dict[str, Any],
) -> dict[str, Any]:
    preflight = preflight_external_release(
        manifest_path,
        base_config["external_release_entry"],
    )
    if not preflight["ready"]:
        return {
            "status": "INGRESS_PREFLIGHT_FAILED",
            "run_authorized": False,
            "preflight": preflight,
        }
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    profiles = manifest.get("adequacy_profiles", {})
    gate_rows = []
    eligible = []
    for paradigm, thresholds in qualification_config["data_adequacy_gate"].items():
        if paradigm == "INTERNAL_LONG_ONLY_DAILY" or paradigm not in profiles:
            continue
        profile = profiles[paradigm]
        rows, summary = evaluate_data_adequacy({paradigm: thresholds}, {paradigm: profile})
        gate_rows.extend(rows.to_dict(orient="records"))
        if summary[paradigm]["status"] == "PASS":
            eligible.append(
                {
                    "paradigm": paradigm,
                    "information_match_score": float(profile.get("information_match_score", 0.0)),
                }
            )
    eligible = sorted(eligible, key=lambda item: (-item["information_match_score"], item["paradigm"]))
    selected = eligible[: int(qualification_config["new_release_activation"]["maximum_external_paradigms"])]
    ready = len(selected) == int(qualification_config["new_release_activation"]["maximum_external_paradigms"])
    return {
        "status": "READY_FOR_NEW_DATA_ARENA" if ready else "DATA_ADEQUACY_UNDERPOWERED",
        "run_authorized": ready,
        "preflight": preflight,
        "data_adequacy_checks": gate_rows,
        "selected_external_paradigms": selected,
        "include_internal_baseline": True,
        "budget_action": "FREEZE_FIXED_DEVELOPMENT_ONLY_BUDGET" if ready else "NO_LARGE_EXPERIMENT",
        "boundaries": qualification_config["new_release_activation"],
    }
