from __future__ import annotations

import importlib.metadata
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .release import sha256_file


@dataclass
class DeepDowResult:
    challenger_weights: pd.DataFrame
    control_weights: pd.DataFrame
    per_seed_weights: pd.DataFrame
    native_metrics: pd.DataFrame
    training_ledger: pd.DataFrame
    manifest: dict[str, Any]


def _activate_dependency_path(config: dict[str, Any]) -> None:
    dependency_path = str(Path(config["dependency_path"]).resolve())
    if dependency_path not in sys.path:
        sys.path.insert(0, dependency_path)


def verify_upstream(config: dict[str, Any]) -> dict[str, Any]:
    _activate_dependency_path(config)
    import deepdow

    observed_version = deepdow.__version__
    if observed_version != config["version"]:
        raise RuntimeError(f"DeepDow version mismatch: {observed_version}")
    wheel_path = Path(config["wheel_path"])
    if not wheel_path.exists():
        raise FileNotFoundError(wheel_path)
    wheel_sha = sha256_file(wheel_path)
    if wheel_sha != config["wheel_sha256"]:
        raise RuntimeError("DeepDow wheel hash mismatch")
    source_root = Path(config["source_root"])
    source_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=source_root, text=True
    ).strip()
    if source_commit != config["git_commit"]:
        raise RuntimeError("DeepDow source commit mismatch")
    return {
        "package_version": observed_version,
        "package_path": str(Path(deepdow.__file__).resolve()),
        "wheel_sha256": wheel_sha,
        "source_commit": source_commit,
        "source_clean": not bool(
            subprocess.check_output(["git", "status", "--porcelain"], cwd=source_root, text=True).strip()
        ),
        "torch_version": importlib.metadata.version("torch"),
    }


def _build_tensors(
    daily: pd.DataFrame,
    config: dict[str, Any],
    *,
    rotate_flow_assets: bool,
) -> tuple[np.ndarray, np.ndarray, pd.DatetimeIndex, list[str]]:
    symbols = sorted(daily.symbol.unique())
    dates = pd.DatetimeIndex(sorted(pd.to_datetime(daily.date, utc=True).unique()))
    close = daily.pivot(index="date", columns="symbol", values="close").reindex(index=dates, columns=symbols)
    flow = daily.pivot(index="date", columns="symbol", values="flow_imbalance").reindex(index=dates, columns=symbols)
    notional = daily.pivot(index="date", columns="symbol", values="notional").reindex(index=dates, columns=symbols)
    trades = daily.pivot(index="date", columns="symbol", values="trade_count").reindex(index=dates, columns=symbols)
    if any(frame.isna().any().any() for frame in (close, flow, notional, trades)):
        raise ValueError("DeepDow fixed-axis tensors require complete inputs")
    log_returns = np.log(close / close.shift(1))
    simple_returns = close.pct_change(fill_method=None)
    channels = np.stack(
        [
            log_returns.to_numpy(),
            flow.to_numpy(),
            np.log1p(notional.to_numpy()),
            np.log1p(trades.to_numpy()),
        ],
        axis=1,
    )
    if rotate_flow_assets:
        channels[:, 1:, :] = np.roll(channels[:, 1:, :], shift=1, axis=2)

    lookback = int(config["lookback_days"])
    gap = int(config["execution_gap_days"])
    horizon = int(config["horizon_days"])
    X_rows: list[np.ndarray] = []
    y_rows: list[np.ndarray] = []
    decision_dates: list[pd.Timestamp] = []
    for cursor in range(lookback + 1, len(dates) - gap - horizon + 1):
        X = channels[cursor - lookback : cursor].transpose(1, 0, 2)
        future = simple_returns.iloc[cursor + gap : cursor + gap + horizon].to_numpy()
        if not np.isfinite(X).all() or not np.isfinite(future).all():
            continue
        y = np.zeros((channels.shape[1], horizon, len(symbols)), dtype=np.float64)
        y[0] = future
        X_rows.append(X.astype(np.float64))
        y_rows.append(y)
        decision_dates.append(dates[cursor - 1])
    return np.stack(X_rows), np.stack(y_rows), pd.DatetimeIndex(decision_dates), symbols


def _split_indices(decision_dates: pd.DatetimeIndex, splits: dict[str, Any]) -> dict[str, list[int]]:
    result: dict[str, list[int]] = {}
    mapping = {
        "train": splits["train"],
        "valid": splits["valid"],
        "development_holdout": splits["development_holdout"],
    }
    for name, (start, end) in mapping.items():
        mask = (decision_dates >= pd.Timestamp(start, tz="UTC")) & (decision_dates <= pd.Timestamp(end, tz="UTC"))
        result[name] = np.flatnonzero(mask).tolist()
        if not result[name]:
            raise ValueError(f"DeepDow split is empty: {name}")
    if max(result["train"]) >= min(result["valid"]) or max(result["valid"]) >= min(result["development_holdout"]):
        raise ValueError("DeepDow chronological split ordering violated")
    return result


def _native_metrics(weights: np.ndarray, y: np.ndarray) -> dict[str, float]:
    import torch
    from deepdow.losses import MaximumDrawdown, MeanReturns, SharpeRatio, portfolio_returns

    weights_t = torch.as_tensor(weights, dtype=torch.float32)
    y_t = torch.as_tensor(y, dtype=torch.float32)
    sharpe_loss = SharpeRatio(input_type="simple", eps=1e-4)(weights_t, y_t)
    mean_return_loss = MeanReturns(input_type="simple")(weights_t, y_t)
    max_drawdown_loss = MaximumDrawdown(input_type="simple")(weights_t, y_t)
    paths = portfolio_returns(weights_t, y_t[:, 0], input_type="simple", output_type="simple", rebalance=False)
    return {
        "native_negative_sharpe_loss_mean": float(sharpe_loss.mean().item()),
        "native_mean_return_loss_mean": float(mean_return_loss.mean().item()),
        "native_max_drawdown_loss_mean": float(max_drawdown_loss.mean().item()),
        "native_buy_hold_path_return_mean": float(paths.mean().item()),
    }


def _fit_one(
    X: np.ndarray,
    y: np.ndarray,
    decision_dates: pd.DatetimeIndex,
    symbols: list[str],
    split_indices: dict[str, list[int]],
    config: dict[str, Any],
    *,
    seed: int,
    variant: str,
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, float]]:
    import torch
    from deepdow.benchmarks import InverseVolatility, OneOverN
    from deepdow.data import InRAMDataset, RigidDataLoader, Scale, prepare_standard_scaler
    from deepdow.experiments import Run
    from deepdow.losses import MaximumDrawdown, MeanReturns, SharpeRatio, SquaredWeights
    from deepdow.nn import KeynesNet

    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.set_num_threads(1)
    means, stds = prepare_standard_scaler(X, indices=split_indices["train"])
    if not np.isfinite(means).all() or not np.isfinite(stds).all() or (stds <= 0).any():
        raise ValueError("invalid train-only DeepDow scaler")
    dataset = InRAMDataset(
        X,
        y,
        timestamps=decision_dates,
        asset_names=symbols,
        transform=Scale(means, stds),
    )
    batch_size = int(config["training"]["batch_size"])
    train_loader = RigidDataLoader(
        dataset,
        indices=split_indices["train"],
        batch_size=batch_size,
    )
    valid_loader = RigidDataLoader(
        dataset,
        indices=split_indices["valid"],
        batch_size=batch_size,
    )
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
    started = time.perf_counter()
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
    )
    run.launch(int(config["training"]["epochs"]))
    runtime_seconds = time.perf_counter() - started

    eval_ix = split_indices["development_holdout"]
    X_eval = (X[eval_ix] - means[None, :, None, None]) / stds[None, :, None, None]
    network.eval()
    with torch.no_grad():
        weights = network(torch.as_tensor(X_eval, dtype=torch.float32)).cpu().numpy()
    if not np.isfinite(weights).all() or (weights < -1e-7).any() or not np.allclose(weights.sum(axis=1), 1.0, atol=1e-6):
        raise ValueError("DeepDow KeynesNet allocation contract violated")
    weights_frame = pd.DataFrame(weights, index=decision_dates[eval_ix], columns=symbols)
    native = _native_metrics(weights, y[eval_ix])
    ledger = {
        "variant": variant,
        "seed": seed,
        "fit_runtime_seconds": runtime_seconds,
        "epochs": int(config["training"]["epochs"]),
        "train_samples": len(split_indices["train"]),
        "valid_samples": len(split_indices["valid"]),
        "development_holdout_samples": len(eval_ix),
        "train_scaler_means": json.dumps(means.tolist()),
        "train_scaler_stds": json.dumps(stds.tolist()),
    }
    return weights_frame, ledger, native


def run_deepdow_native(
    daily: pd.DataFrame,
    config: dict[str, Any],
    splits: dict[str, Any],
) -> DeepDowResult:
    verification = verify_upstream(config)
    _activate_dependency_path(config)
    import torch
    from deepdow.losses import portfolio_returns

    example_returns = torch.tensor([[[0.1, 0.2], [0.05, 0.02]]], dtype=torch.float32)
    example_weights = torch.tensor([[0.4, 0.6]], dtype=torch.float32)
    example_result = portfolio_returns(
        example_weights,
        example_returns,
        input_type="simple",
        output_type="simple",
    )
    if not torch.allclose(example_result, torch.tensor([[0.16, 0.0314]]), atol=1e-4):
        raise RuntimeError("DeepDow upstream portfolio_returns parity canary failed")

    full_X, y, decision_dates, symbols = _build_tensors(daily, config, rotate_flow_assets=False)
    control_X, control_y, control_dates, control_symbols = _build_tensors(
        daily, config, rotate_flow_assets=True
    )
    if not np.array_equal(y, control_y) or not decision_dates.equals(control_dates) or symbols != control_symbols:
        raise RuntimeError("DeepDow matched-control target or index drift")
    if not np.array_equal(full_X[:, 0], control_X[:, 0]):
        raise RuntimeError("DeepDow matched control changed return channel")
    split_indices = _split_indices(decision_dates, splits)

    per_seed: list[pd.DataFrame] = []
    native_rows: list[dict[str, Any]] = []
    ledgers: list[dict[str, Any]] = []
    variant_weights: dict[str, list[pd.DataFrame]] = {"CHALLENGER": [], "ASSET_ROTATED_CONTROL": []}
    for variant, X in (("CHALLENGER", full_X), ("ASSET_ROTATED_CONTROL", control_X)):
        for seed in config["training"]["seeds"]:
            weights, ledger, native = _fit_one(
                X,
                y,
                decision_dates,
                symbols,
                split_indices,
                config,
                seed=int(seed),
                variant=variant,
            )
            variant_weights[variant].append(weights)
            long = weights.stack().rename("weight").reset_index()
            long.columns = ["date", "symbol", "weight"]
            long["variant"] = variant
            long["seed"] = int(seed)
            per_seed.append(long)
            native_rows.append({"variant": variant, "seed": int(seed), **native})
            ledgers.append(ledger)
    challenger = sum(variant_weights["CHALLENGER"]) / len(variant_weights["CHALLENGER"])
    control = sum(variant_weights["ASSET_ROTATED_CONTROL"]) / len(variant_weights["ASSET_ROTATED_CONTROL"])
    manifest = {
        "status": "NATIVE_CODE_REPRODUCED_WITH_CRYPTO_ADAPTATIONS",
        "reproduction_id": config["source_id"],
        "classification": "NATIVE_REPRODUCED",
        "upstream_verification": verification,
        "native_contract": {
            "input_shape": list(full_X.shape),
            "target_shape": list(y.shape),
            "lookback_days": config["lookback_days"],
            "execution_gap_days": config["execution_gap_days"],
            "horizon_days": config["horizon_days"],
            "portfolio_mapping": "KeynesNet SoftmaxAllocator long-only fully-invested weights",
            "native_evaluator": "DeepDow per-sample multi-step buy-and-hold losses, rebalance=False",
        },
        "matched_control": config["matched_control"],
        "symbols": symbols,
        "decision_date_range": [str(decision_dates.min()), str(decision_dates.max())],
        "split_sample_counts": {key: len(value) for key, value in split_indices.items()},
        "upstream_parity": {
            "portfolio_returns_example": example_result.detach().cpu().numpy().tolist(),
            "weights_nonnegative_and_sum_one": True,
            "upstream_Run_used": True,
            "upstream_KeynesNet_used": True,
            "upstream_losses_used": True,
        },
        "scope_limit": "framework workflow reproduced on fixed complete crypto core10; no claim of reproducing a published DeepDow market benchmark",
        "forward_read": False,
        "challenge_read": False,
        "candidate_promotion": False,
    }
    return DeepDowResult(
        challenger_weights=challenger,
        control_weights=control,
        per_seed_weights=pd.concat(per_seed, ignore_index=True),
        native_metrics=pd.DataFrame(native_rows),
        training_ledger=pd.DataFrame(ledgers),
        manifest=manifest,
    )
