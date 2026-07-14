from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BridgeMetrics:
    system_id: str
    observations: int
    gross_mean: float
    net_mean: float
    net_mean_lcb_95: float
    annualized_sharpe: float
    max_drawdown: float
    turnover_mean: float
    positive_day_fraction: float
    positive_month_fraction: float
    average_gross_exposure: float
    average_net_exposure: float
    first_date: str
    last_date: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _moving_block_bootstrap_mean_lcb(
    values: np.ndarray,
    *,
    block_days: int,
    samples: int,
    seed: int,
) -> float:
    clean = np.asarray(values, dtype=float)
    clean = clean[np.isfinite(clean)]
    if clean.size < 2:
        return float("nan")
    block_days = min(max(1, int(block_days)), clean.size)
    starts = np.arange(clean.size - block_days + 1)
    rng = np.random.default_rng(seed)
    draws: list[float] = []
    blocks_needed = math.ceil(clean.size / block_days)
    for _ in range(int(samples)):
        selected = rng.choice(starts, size=blocks_needed, replace=True)
        sample = np.concatenate([clean[start : start + block_days] for start in selected])[: clean.size]
        draws.append(float(sample.mean()))
    return float(np.quantile(draws, 0.025))


def _maximum_drawdown(returns: pd.Series) -> float:
    wealth = (1.0 + returns.fillna(0.0)).cumprod()
    drawdown = wealth / wealth.cummax() - 1.0
    return float(drawdown.min()) if len(drawdown) else float("nan")


def evaluate_common_bridge(
    daily: pd.DataFrame,
    weights: pd.DataFrame,
    *,
    system_id: str,
    cost_bps_per_unit_turnover: float,
    annualization: int,
    block_days: int,
    bootstrap_samples: int,
    bootstrap_seed: int = 20260713,
) -> tuple[BridgeMetrics, pd.DataFrame]:
    labels = daily.pivot(index="date", columns="symbol", values="label_1d_delayed").sort_index()
    labels.index = pd.to_datetime(labels.index, utc=True)
    aligned_weights = weights.copy()
    aligned_weights.index = pd.to_datetime(aligned_weights.index, utc=True)
    aligned_weights = aligned_weights.reindex(columns=labels.columns).sort_index()
    common_dates = aligned_weights.index.intersection(labels.dropna().index)
    aligned_weights = aligned_weights.loc[common_dates]
    aligned_labels = labels.loc[common_dates]
    if aligned_weights.empty:
        raise ValueError(f"no common bridge observations for {system_id}")
    if aligned_weights.isna().any().any() or aligned_labels.isna().any().any():
        raise ValueError(f"missing common bridge values for {system_id}")
    if not np.isfinite(aligned_weights.to_numpy()).all():
        raise ValueError(f"non-finite weights for {system_id}")

    gross_return = (aligned_weights * aligned_labels).sum(axis=1)
    previous = aligned_weights.shift(1).fillna(0.0)
    turnover = (aligned_weights - previous).abs().sum(axis=1)
    cost = turnover * float(cost_bps_per_unit_turnover) / 10000.0
    net_return = gross_return - cost
    monthly = net_return.groupby(net_return.index.to_period("M")).sum()
    std = float(net_return.std(ddof=1))
    sharpe = float(net_return.mean() / std * math.sqrt(annualization)) if std > 0 else float("nan")
    metrics = BridgeMetrics(
        system_id=system_id,
        observations=len(net_return),
        gross_mean=float(gross_return.mean()),
        net_mean=float(net_return.mean()),
        net_mean_lcb_95=_moving_block_bootstrap_mean_lcb(
            net_return.to_numpy(),
            block_days=block_days,
            samples=bootstrap_samples,
            seed=bootstrap_seed,
        ),
        annualized_sharpe=sharpe,
        max_drawdown=_maximum_drawdown(net_return),
        turnover_mean=float(turnover.mean()),
        positive_day_fraction=float((net_return > 0).mean()),
        positive_month_fraction=float((monthly > 0).mean()),
        average_gross_exposure=float(aligned_weights.abs().sum(axis=1).mean()),
        average_net_exposure=float(aligned_weights.sum(axis=1).mean()),
        first_date=str(common_dates.min()),
        last_date=str(common_dates.max()),
    )
    path = pd.DataFrame(
        {
            "date": common_dates,
            "gross_return": gross_return.to_numpy(),
            "turnover": turnover.to_numpy(),
            "cost": cost.to_numpy(),
            "net_return": net_return.to_numpy(),
        }
    )
    return metrics, path


def paired_increment(
    challenger_path: pd.DataFrame,
    control_path: pd.DataFrame,
    *,
    challenger_id: str,
    control_id: str,
    block_days: int,
    bootstrap_samples: int,
    seed: int = 20260713,
) -> dict[str, Any]:
    merged = challenger_path[["date", "net_return"]].merge(
        control_path[["date", "net_return"]],
        on="date",
        how="inner",
        validate="one_to_one",
        suffixes=("_challenger", "_control"),
    )
    if merged.empty:
        raise ValueError("paired comparison has no common dates")
    difference = merged.net_return_challenger - merged.net_return_control
    return {
        "challenger_id": challenger_id,
        "control_id": control_id,
        "observations": len(difference),
        "paired_net_increment_mean": float(difference.mean()),
        "paired_net_increment_lcb_95": _moving_block_bootstrap_mean_lcb(
            difference.to_numpy(),
            block_days=block_days,
            samples=bootstrap_samples,
            seed=seed,
        ),
        "positive_day_fraction": float((difference > 0).mean()),
        "first_date": str(merged.date.min()),
        "last_date": str(merged.date.max()),
    }


def long_only_topk_momentum_weights(
    daily: pd.DataFrame,
    decision_dates: pd.DatetimeIndex,
    *,
    lookback_days: int = 20,
    topk: int = 3,
) -> pd.DataFrame:
    close = daily.pivot(index="date", columns="symbol", values="close").sort_index()
    score = close / close.shift(lookback_days) - 1.0
    rows: list[pd.Series] = []
    for date in pd.to_datetime(decision_dates, utc=True):
        values = score.loc[date].dropna().sort_values(ascending=False, kind="mergesort")
        selected = values.head(topk).index
        row = pd.Series(0.0, index=close.columns, name=date)
        if len(selected):
            row.loc[selected] = 1.0 / len(selected)
        rows.append(row)
    return pd.DataFrame(rows)


def one_over_n_weights(daily: pd.DataFrame, decision_dates: pd.DatetimeIndex) -> pd.DataFrame:
    symbols = sorted(daily.symbol.unique())
    return pd.DataFrame(
        np.full((len(decision_dates), len(symbols)), 1.0 / len(symbols)),
        index=pd.to_datetime(decision_dates, utc=True),
        columns=symbols,
    )
