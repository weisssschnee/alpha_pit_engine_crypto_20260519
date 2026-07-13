from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


ALPHA158_ROLLING_FAMILIES = (
    "ROC", "MA", "STD", "BETA", "RSQR", "RESI", "MAX", "MIN", "QTLU", "QTLD",
    "RANK", "RSV", "IMAX", "IMIN", "IMXD", "CORR", "CORD", "CNTP", "CNTN", "CNTD",
    "SUMP", "SUMN", "SUMD", "VMA", "VSTD", "WVMA", "VSUMP", "VSUMN", "VSUMD",
)
ALPHA158_KBAR_FEATURES = ("KMID", "KLEN", "KMID2", "KUP", "KUP2", "KLOW", "KLOW2", "KSFT", "KSFT2")
ALPHA158_PRICE_FEATURES = ("OPEN0", "HIGH0", "LOW0", "VWAP0")
REQUIRED_DAILY_COLUMNS = {
    "date", "symbol", "data_role", "open", "high", "low", "close", "vwap", "volume",
    "notional", "signed_flow", "flow_imbalance", "observable_time", "maturity",
}


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def validate_frontier_config(config: dict[str, Any]) -> None:
    if config["fixed_budget"]["external_reproductions"] < 2:
        raise ValueError("frontier sprint requires at least two external reproductions")
    if len(config["frontier_map"]) < 4:
        raise ValueError("external frontier map is too narrow")
    dispositions = {item["competitor_id"]: item["sprint_disposition"] for item in config["frontier_map"]}
    for required in ("QLIB_ALPHA158_LIGHTGBM", "DEEP_MOMENTUM_LSTM", "DEEPLOB_DIGITAL_ASSET"):
        if required not in dispositions:
            raise ValueError(f"missing required frontier reference: {required}")
    for flag, enabled in config["prohibitions"].items():
        if not enabled:
            raise PermissionError(f"prohibition disabled: {flag}")
    if config["release"]["forward_access"] or config["release"]["spent_evaluation_access"]:
        raise PermissionError("frontier sprint cannot open spent or sealed evaluation data")
    systems = config["arena"]["systems"]
    if len(systems) != len(set(systems)) or len(systems) < 6:
        raise ValueError("arena systems must be unique and multi-paradigm")
    expected_fits = (
        len(config["qlib_reproduction"]["model_seeds"]) * 2
        + len(config["dmn_reproduction"]["seeds"]) * 2
    )
    if expected_fits != config["fixed_budget"]["model_fits"]:
        raise ValueError("fixed model-fit budget drift")


def validate_external_data_contract(contract: dict[str, Any], columns: Iterable[str]) -> dict[str, Any]:
    observed = set(columns)
    required = set(contract["required_schema"])
    missing = sorted(required - observed)
    return {
        "family": contract["family"],
        "compatible_paradigms": contract["compatible_paradigms"],
        "required_columns": sorted(required),
        "missing_columns": missing,
        "ready": not missing,
    }


def load_daily_panel(repo: Path, config: dict[str, Any]) -> pd.DataFrame:
    release_cfg = json.loads((repo / config["release"]["config"]).read_text(encoding="utf-8"))
    release_root = Path(release_cfg["release_root"])
    coverage = pd.read_csv(repo / "runtime/mechanism_data_expansion0_20260712/native_aggtrades_release_v1/coverage_ledger.csv")
    allowed_months = set(config["release"]["development_months"] + config["release"]["challenge_months"])
    qualified = coverage[coverage.status.eq("QUALIFIED") & coverage.month.isin(allowed_months)].copy()
    frames: list[pd.DataFrame] = []
    source_columns = ["timestamp", "open_price", "high_price", "low_price", "close_price"]
    feature_columns = [
        "timestamp", "symbol", "month", "quantity", "notional", "signed_aggressor_notional",
        "volume_imbalance", "vwap", "trade_count", "missing_any", "observable_time", "maturity",
    ]
    for row in qualified.sort_values(["data_role", "symbol", "month"], kind="mergesort").itertuples():
        path = release_root / row.data_role.lower() / f"symbol={row.symbol}" / f"month={row.month}" / "part.parquet"
        feature = pd.read_parquet(path, columns=feature_columns)
        source = pd.read_parquet(Path(row.source_path), columns=source_columns)
        feature["timestamp"] = pd.to_datetime(feature["timestamp"], utc=True)
        source["timestamp"] = pd.to_datetime(source["timestamp"], utc=True)
        merged = feature.merge(source, on="timestamp", how="left", validate="one_to_one")
        if merged[source_columns[1:]].isna().any().any():
            raise ValueError(f"source OHLC missing for {row.symbol} {row.month}")
        merged["data_role"] = row.data_role
        frames.append(merged)
    hourly = pd.concat(frames, ignore_index=True)
    hourly = hourly[~hourly.missing_any].sort_values(["symbol", "timestamp"], kind="mergesort")
    hourly["date"] = hourly.timestamp.dt.floor("D")
    daily_rows: list[dict[str, Any]] = []
    for (role, symbol, date), block in hourly.groupby(["data_role", "symbol", "date"], sort=True):
        block = block.sort_values("timestamp", kind="mergesort")
        quantity = float(block.quantity.sum())
        notional = float(block.notional.sum())
        daily_rows.append({
            "date": date,
            "symbol": symbol,
            "data_role": role,
            "month": str(date)[:7],
            "open": float(block.open_price.iloc[0]),
            "high": float(block.high_price.max()),
            "low": float(block.low_price.min()),
            "close": float(block.close_price.iloc[-1]),
            "vwap": notional / quantity if quantity > 0 else float("nan"),
            "volume": quantity,
            "notional": notional,
            "trade_count": int(block.trade_count.sum()),
            "signed_flow": float(block.signed_aggressor_notional.sum()),
            "flow_imbalance": float(block.signed_aggressor_notional.sum() / notional) if notional > 0 else float("nan"),
            "observable_time": date + pd.Timedelta(days=1),
            "maturity": date + pd.Timedelta(days=1),
            "source_lag_seconds": 0,
            "hour_coverage": int(len(block)),
        })
    daily = pd.DataFrame(daily_rows).sort_values(["symbol", "date"], kind="mergesort").reset_index(drop=True)
    if not REQUIRED_DAILY_COLUMNS.issubset(daily.columns):
        raise ValueError("daily panel schema incomplete")
    if (daily.observable_time <= daily.date).any() or (daily.maturity < daily.observable_time).any():
        raise ValueError("daily observable-time or maturity contract violated")
    counts = daily.groupby("date").symbol.nunique()
    valid_dates = set(counts[counts >= config["dataset"]["minimum_symbols_per_day"]].index)
    daily = daily[daily.date.isin(valid_dates)].copy().reset_index(drop=True)
    history_group = daily.groupby("symbol", sort=False)
    label_group = daily.groupby(["symbol", "data_role"], sort=False)
    daily["return_1d"] = history_group.close.pct_change(fill_method=None)
    daily["label"] = label_group.close.shift(-2) / label_group.close.shift(-1) - 1.0
    daily["label_observable_time"] = daily.date + pd.Timedelta(days=3)
    return daily


def _rolling_slope(values: np.ndarray) -> float:
    if np.isnan(values).any() or len(values) < 2:
        return float("nan")
    x = np.arange(len(values), dtype=float)
    return float(np.polyfit(x, values, 1)[0])


def _rolling_rsquared(values: np.ndarray) -> float:
    if np.isnan(values).any() or len(values) < 2 or np.std(values) == 0:
        return float("nan")
    x = np.arange(len(values), dtype=float)
    corr = np.corrcoef(x, values)[0, 1]
    return float(corr * corr)


def _rolling_residual(values: np.ndarray) -> float:
    if np.isnan(values).any() or len(values) < 2:
        return float("nan")
    x = np.arange(len(values), dtype=float)
    fit = np.polyfit(x, values, 1)
    return float(values[-1] - (fit[0] * x[-1] + fit[1]))


def _last_rank(values: np.ndarray) -> float:
    if np.isnan(values).any() or not len(values):
        return float("nan")
    return float((np.sum(values < values[-1]) + 0.5 * np.sum(values == values[-1])) / len(values))


def _argmax_fraction(values: np.ndarray) -> float:
    return float(np.argmax(values) / max(1, len(values) - 1)) if not np.isnan(values).any() else float("nan")


def _argmin_fraction(values: np.ndarray) -> float:
    return float(np.argmin(values) / max(1, len(values) - 1)) if not np.isnan(values).any() else float("nan")


def build_alpha158_features(daily: pd.DataFrame, windows: Iterable[int]) -> tuple[pd.DataFrame, list[str]]:
    frame = daily.sort_values(["symbol", "date"], kind="mergesort").copy()
    eps = 1e-12
    close = frame.close.replace(0, np.nan)
    frame["KMID"] = (frame.close - frame.open) / frame.open.replace(0, np.nan)
    frame["KLEN"] = (frame.high - frame.low) / frame.open.replace(0, np.nan)
    frame["KMID2"] = (frame.close - frame.open) / (frame.high - frame.low).replace(0, np.nan)
    frame["KUP"] = (frame.high - np.maximum(frame.open, frame.close)) / frame.open.replace(0, np.nan)
    frame["KUP2"] = (frame.high - np.maximum(frame.open, frame.close)) / (frame.high - frame.low).replace(0, np.nan)
    frame["KLOW"] = (np.minimum(frame.open, frame.close) - frame.low) / frame.open.replace(0, np.nan)
    frame["KLOW2"] = (np.minimum(frame.open, frame.close) - frame.low) / (frame.high - frame.low).replace(0, np.nan)
    frame["KSFT"] = (2 * frame.close - frame.high - frame.low) / frame.open.replace(0, np.nan)
    frame["KSFT2"] = (2 * frame.close - frame.high - frame.low) / (frame.high - frame.low).replace(0, np.nan)
    frame["OPEN0"] = frame.open / close
    frame["HIGH0"] = frame.high / close
    frame["LOW0"] = frame.low / close
    frame["VWAP0"] = frame.vwap / close
    feature_names = list(ALPHA158_KBAR_FEATURES + ALPHA158_PRICE_FEATURES)
    for window in windows:
        feature_names.extend(f"{family}{window}" for family in ALPHA158_ROLLING_FAMILIES)

    parts: list[pd.DataFrame] = []
    for _, block in frame.groupby("symbol", sort=False):
        block = block.copy()
        derived: dict[str, pd.Series] = {}
        c, h, l, v = block.close, block.high, block.low, block.volume
        delta_c = c.diff()
        delta_v = v.diff()
        abs_delta_c = delta_c.abs()
        log_v = np.log1p(v.clip(lower=0))
        ret_abs_volume = c.pct_change(fill_method=None).abs() * v
        for w in windows:
            roll_c = c.rolling(w, min_periods=w)
            roll_h = h.rolling(w, min_periods=w)
            roll_l = l.rolling(w, min_periods=w)
            roll_v = v.rolling(w, min_periods=w)
            positive = delta_c.clip(lower=0).rolling(w, min_periods=w).sum()
            negative = (-delta_c.clip(upper=0)).rolling(w, min_periods=w).sum()
            total_move = abs_delta_c.rolling(w, min_periods=w).sum().replace(0, np.nan)
            positive_v = delta_v.clip(lower=0).rolling(w, min_periods=w).sum()
            negative_v = (-delta_v.clip(upper=0)).rolling(w, min_periods=w).sum()
            total_v_move = delta_v.abs().rolling(w, min_periods=w).sum().replace(0, np.nan)
            derived[f"ROC{w}"] = c.shift(w) / c
            derived[f"MA{w}"] = roll_c.mean() / c
            derived[f"STD{w}"] = roll_c.std(ddof=0) / c
            derived[f"BETA{w}"] = roll_c.apply(_rolling_slope, raw=True) / c
            derived[f"RSQR{w}"] = roll_c.apply(_rolling_rsquared, raw=True)
            derived[f"RESI{w}"] = roll_c.apply(_rolling_residual, raw=True) / c
            derived[f"MAX{w}"] = roll_h.max() / c
            derived[f"MIN{w}"] = roll_l.min() / c
            derived[f"QTLU{w}"] = roll_h.quantile(0.8) / c
            derived[f"QTLD{w}"] = roll_l.quantile(0.2) / c
            derived[f"RANK{w}"] = roll_c.apply(_last_rank, raw=True)
            derived[f"RSV{w}"] = (c - roll_l.min()) / (roll_h.max() - roll_l.min()).replace(0, np.nan)
            derived[f"IMAX{w}"] = roll_h.apply(_argmax_fraction, raw=True)
            derived[f"IMIN{w}"] = roll_l.apply(_argmin_fraction, raw=True)
            derived[f"IMXD{w}"] = derived[f"IMAX{w}"] - derived[f"IMIN{w}"]
            derived[f"CORR{w}"] = c.rolling(w, min_periods=w).corr(log_v)
            derived[f"CORD{w}"] = delta_c.rolling(w, min_periods=w).corr(log_v.diff())
            derived[f"CNTP{w}"] = (delta_c > 0).astype(float).rolling(w, min_periods=w).mean()
            derived[f"CNTN{w}"] = (delta_c < 0).astype(float).rolling(w, min_periods=w).mean()
            derived[f"CNTD{w}"] = derived[f"CNTP{w}"] - derived[f"CNTN{w}"]
            derived[f"SUMP{w}"] = positive / total_move
            derived[f"SUMN{w}"] = negative / total_move
            derived[f"SUMD{w}"] = (positive - negative) / total_move
            derived[f"VMA{w}"] = roll_v.mean() / v.replace(0, np.nan)
            derived[f"VSTD{w}"] = roll_v.std(ddof=0) / v.replace(0, np.nan)
            derived[f"WVMA{w}"] = ret_abs_volume.rolling(w, min_periods=w).std(ddof=0) / (ret_abs_volume.rolling(w, min_periods=w).mean() + eps)
            derived[f"VSUMP{w}"] = positive_v / total_v_move
            derived[f"VSUMN{w}"] = negative_v / total_v_move
            derived[f"VSUMD{w}"] = (positive_v - negative_v) / total_v_move
        parts.append(pd.concat([block, pd.DataFrame(derived, index=block.index)], axis=1))
    output = pd.concat(parts, ignore_index=True).sort_values(["symbol", "date"], kind="mergesort").reset_index(drop=True)
    if len(feature_names) != 158 or len(set(feature_names)) != 158:
        raise ValueError(f"Alpha158 feature contract drift: {len(feature_names)}")
    output[feature_names] = output[feature_names].replace([np.inf, -np.inf], np.nan)
    return output, feature_names


def build_dmn_features(daily: pd.DataFrame, config: dict[str, Any]) -> tuple[pd.DataFrame, list[str]]:
    frame = daily.sort_values(["symbol", "date"], kind="mergesort").copy()
    feature_names: list[str] = []
    pieces: list[pd.DataFrame] = []
    span = int(config["volatility_span_days"])
    for _, block in frame.groupby("symbol", sort=False):
        block = block.copy()
        returns = block.close.pct_change(fill_method=None)
        vol = returns.ewm(span=span, adjust=False, min_periods=max(10, span // 3)).std(bias=False)
        annual_vol = vol * math.sqrt(365.0)
        block["dmn_ex_ante_vol"] = annual_vol
        local_names: list[str] = []
        for horizon in config["feature_horizons_days"]:
            name = f"dmn_norm_ret_{horizon}d"
            block[name] = block.close.pct_change(horizon, fill_method=None) / (vol * math.sqrt(horizon)).replace(0, np.nan)
            local_names.append(name)
        for short, long in config["macd_pairs_days"]:
            name = f"dmn_macd_{short}_{long}"
            fast = block.close.ewm(span=short, adjust=False, min_periods=short).mean()
            slow = block.close.ewm(span=long, adjust=False, min_periods=long).mean()
            block[name] = (fast - slow) / (block.close * vol).replace(0, np.nan)
            local_names.append(name)
        block[local_names] = block[local_names].clip(-10, 10)
        feature_names = local_names
        pieces.append(block)
    output = pd.concat(pieces, ignore_index=True).sort_values(["symbol", "date"], kind="mergesort").reset_index(drop=True)
    return output, feature_names


def cross_sectional_unit_gross(values: pd.Series, frame: pd.DataFrame) -> pd.Series:
    temp = frame[["date"]].assign(value=pd.to_numeric(values, errors="coerce"))
    rank = temp.groupby("date", sort=False).value.rank(pct=True, method="average") - 0.5
    gross = rank.abs().groupby(temp.date, sort=False).transform("sum").replace(0, np.nan)
    return (rank / gross).fillna(0.0)


def topk_dropout_weights(scores: pd.Series, frame: pd.DataFrame, topk: int, n_drop: int) -> pd.Series:
    output = pd.Series(0.0, index=frame.index)
    previous: set[str] = set()
    for _, indices in frame.groupby("date", sort=True).groups.items():
        block = pd.DataFrame({"symbol": frame.loc[indices, "symbol"], "score": scores.loc[indices]}).dropna()
        block = block.sort_values(["score", "symbol"], ascending=[False, True], kind="mergesort")
        ranked = block.symbol.tolist()
        eligible = set(ranked[: topk + n_drop])
        kept = [symbol for symbol in ranked if symbol in previous and symbol in eligible][: max(0, topk - n_drop)]
        selected = kept + [symbol for symbol in ranked if symbol not in kept][: topk - len(kept)]
        if selected:
            mapping = {symbol: 1.0 / len(selected) for symbol in selected}
            output.loc[indices] = frame.loc[indices, "symbol"].map(mapping).fillna(0.0)
        previous = set(selected)
    return output


def tsmom_weights(frame: pd.DataFrame, lookback: int = 20) -> pd.Series:
    score = frame.groupby("symbol", sort=False).close.pct_change(lookback, fill_method=None)
    vol = frame.groupby("symbol", sort=False).return_1d.transform(lambda s: s.ewm(span=60, adjust=False, min_periods=20).std())
    raw = np.sign(score) / vol.replace(0, np.nan)
    gross = raw.abs().groupby(frame.date, sort=False).transform("sum").replace(0, np.nan)
    return (raw / gross).fillna(0.0)


def evaluate_weights(
    frame: pd.DataFrame,
    weights: pd.Series,
    role: str,
    cost_bps: float,
    system_id: str,
    runtime_seconds: float,
    complexity: float,
    native_or_common: str = "COMMON",
) -> tuple[dict[str, Any], pd.DataFrame]:
    block = frame[frame.data_role.eq(role)].copy()
    block["weight"] = weights.loc[block.index].to_numpy()
    block = block[block.label.notna() & block.weight.notna()].copy()
    if block.empty:
        return ({"system_id": system_id, "data_role": role, "evaluation": native_or_common, "failure_mode": "NO_VALID_OBSERVATIONS"}, pd.DataFrame())
    wide = block.pivot(index="date", columns="symbol", values="weight").fillna(0.0).sort_index()
    label_wide = block.pivot(index="date", columns="symbol", values="label").reindex(index=wide.index, columns=wide.columns)
    valid = label_wide.notna()
    effective_weights = wide.where(valid, 0.0)
    gross_exposure = effective_weights.abs().sum(axis=1).replace(0, np.nan)
    if native_or_common == "COMMON":
        effective_weights = effective_weights.div(gross_exposure, axis=0).fillna(0.0)
    gross = (effective_weights * label_wide.fillna(0.0)).sum(axis=1)
    turnover = effective_weights.diff().abs().sum(axis=1)
    if len(turnover):
        turnover.iloc[0] = effective_weights.iloc[0].abs().sum()
    net = gross - turnover * cost_bps / 10_000.0
    monthly = net.groupby(net.index.strftime("%Y-%m")).mean()
    mean = float(net.mean())
    std = float(net.std(ddof=1))
    sharpe = mean / std * math.sqrt(365.0) if std > 0 else float("nan")
    monthly_se = float(monthly.std(ddof=1) / math.sqrt(len(monthly))) if len(monthly) > 1 else float("inf")
    lcb = float(monthly.mean() - 1.645 * monthly_se) if len(monthly) else float("nan")
    wealth = (1.0 + net).cumprod()
    drawdown = wealth / wealth.cummax() - 1.0
    result = {
        "system_id": system_id,
        "data_role": role,
        "evaluation": native_or_common,
        "observations": int(len(net)),
        "months": int(len(monthly)),
        "gross_mean": float(gross.mean()),
        "net_mean": mean,
        "net_lcb": lcb,
        "annualized_sharpe": sharpe,
        "max_drawdown": float(drawdown.min()),
        "positive_month_fraction": float((monthly > 0).mean()) if len(monthly) else float("nan"),
        "turnover_mean": float(turnover.mean()),
        "coverage": float((valid.sum(axis=1) >= 2).mean()),
        "runtime_seconds": float(runtime_seconds),
        "complexity": float(complexity),
        "failure_mode": "NONE",
    }
    path = pd.DataFrame({"date": net.index, "gross_return": gross.values, "turnover": turnover.values, "net_return": net.values})
    path["system_id"] = system_id
    path["data_role"] = role
    path["evaluation"] = native_or_common
    return result, path


def daily_ic(frame: pd.DataFrame, scores: pd.Series, role: str) -> dict[str, float]:
    block = frame[frame.data_role.eq(role)].copy()
    block["score"] = scores.loc[block.index]
    pearson: list[float] = []
    spearman: list[float] = []
    for _, day in block.groupby("date", sort=True):
        valid = day[["score", "label"]].dropna()
        if len(valid) >= 4 and valid.score.nunique() > 1 and valid.label.nunique() > 1:
            pearson.append(float(valid.score.corr(valid.label, method="pearson")))
            spearman.append(float(valid.score.corr(valid.label, method="spearman")))
    p = pd.Series(pearson, dtype=float)
    s = pd.Series(spearman, dtype=float)
    return {
        "ic": float(p.mean()) if len(p) else float("nan"),
        "icir": float(p.mean() / p.std(ddof=1)) if len(p) > 1 and p.std(ddof=1) > 0 else float("nan"),
        "rank_ic": float(s.mean()) if len(s) else float("nan"),
        "rank_icir": float(s.mean() / s.std(ddof=1)) if len(s) > 1 and s.std(ddof=1) > 0 else float("nan"),
        "ic_days": int(len(p)),
    }


def fit_lgbm_ensemble(
    frame: pd.DataFrame,
    feature_names: list[str],
    config: dict[str, Any],
    seeds: Iterable[int],
) -> tuple[pd.Series, list[dict[str, Any]]]:
    from lightgbm import LGBMRegressor

    train = frame.data_role.eq("DEVELOPMENT") & frame.label.notna()
    cross_mean = frame.groupby("date", sort=False).label.transform("mean")
    cross_std = frame.groupby("date", sort=False).label.transform("std").replace(0, np.nan)
    target = (frame.label - cross_mean) / cross_std
    train &= target.notna()
    medians = frame.loc[train, feature_names].median()
    x_all = frame[feature_names].replace([np.inf, -np.inf], np.nan).fillna(medians).fillna(0.0)
    predictions: list[np.ndarray] = []
    records: list[dict[str, Any]] = []
    for seed in seeds:
        params = dict(config["model"])
        params.update({"random_state": seed, "deterministic": True, "verbosity": -1})
        started = time.perf_counter()
        model = LGBMRegressor(objective="regression", **params)
        model.fit(x_all.loc[train], target.loc[train])
        predictions.append(model.predict(x_all))
        records.append({
            "seed": seed,
            "fit_rows": int(train.sum()),
            "features": len(feature_names),
            "trees": int(config["model"]["n_estimators"]),
            "runtime_seconds": time.perf_counter() - started,
        })
    return pd.Series(np.mean(predictions, axis=0), index=frame.index), records


@dataclass
class DmnFitResult:
    positions: pd.Series
    records: list[dict[str, Any]]
    training_curve: pd.DataFrame


def fit_dmn_ensemble(
    frame: pd.DataFrame,
    feature_names: list[str],
    config: dict[str, Any],
    seeds: Iterable[int],
    turnover_penalty: float,
) -> DmnFitResult:
    import torch
    from torch import nn

    torch.set_num_threads(1)
    dates = sorted(frame.date.unique())
    symbols = sorted(frame.symbol.unique())
    date_index = {value: idx for idx, value in enumerate(dates)}
    symbol_index = {value: idx for idx, value in enumerate(symbols)}
    feature_array = np.full((len(dates), len(symbols), len(feature_names)), np.nan, dtype=np.float32)
    label_array = np.full((len(dates), len(symbols)), np.nan, dtype=np.float32)
    vol_array = np.full((len(dates), len(symbols)), np.nan, dtype=np.float32)
    role_by_date: dict[Any, str] = {}
    for row in frame.itertuples():
        i, j = date_index[row.date], symbol_index[row.symbol]
        feature_array[i, j] = np.asarray([getattr(row, name) for name in feature_names], dtype=np.float32)
        label_array[i, j] = np.float32(row.label)
        vol_array[i, j] = np.float32(row.dmn_ex_ante_vol)
        role_by_date[row.date] = row.data_role
    train_dates = np.asarray([role_by_date[value] == "DEVELOPMENT" for value in dates])
    feature_train = feature_array[train_dates]
    means = np.nanmean(feature_train, axis=(0, 1))
    stds = np.nanstd(feature_train, axis=(0, 1))
    stds = np.where(stds > 1e-8, stds, 1.0)
    normalized = (feature_array - means) / stds
    normalized = np.nan_to_num(normalized, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
    seq_len = int(config["sequence_length_days"])
    sequences = np.zeros((len(dates), len(symbols), seq_len, len(feature_names)), dtype=np.float32)
    sequence_valid = np.zeros((len(dates), len(symbols)), dtype=bool)
    raw_feature_valid = np.isfinite(feature_array).all(axis=2)
    for idx in range(seq_len - 1, len(dates)):
        sequences[idx] = normalized[idx - seq_len + 1 : idx + 1].transpose(1, 0, 2)
        sequence_valid[idx] = raw_feature_valid[idx - seq_len + 1 : idx + 1].all(axis=0)
    labels = torch.tensor(np.nan_to_num(label_array, nan=0.0), dtype=torch.float32)
    vols = torch.tensor(np.nan_to_num(vol_array, nan=1.0), dtype=torch.float32).clamp_min(1e-4)
    valid = torch.tensor(sequence_valid & np.isfinite(label_array), dtype=torch.bool)
    train_mask = torch.tensor(train_dates[:, None], dtype=torch.bool) & valid
    x_tensor = torch.tensor(sequences, dtype=torch.float32)

    class PositionLstm(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.lstm = nn.LSTM(len(feature_names), int(config["hidden_size"]), batch_first=True)
            self.head = nn.Linear(int(config["hidden_size"]), 1)

        def forward(self, values: torch.Tensor) -> torch.Tensor:
            flat = values.reshape(-1, seq_len, len(feature_names))
            encoded, _ = self.lstm(flat)
            return torch.tanh(self.head(encoded[:, -1]).squeeze(-1)).reshape(len(dates), len(symbols))

    all_positions: list[np.ndarray] = []
    records: list[dict[str, Any]] = []
    curves: list[dict[str, Any]] = []
    for seed in seeds:
        torch.manual_seed(seed)
        np.random.seed(seed)
        model = PositionLstm()
        optimizer = torch.optim.Adam(model.parameters(), lr=float(config["learning_rate"]), weight_decay=float(config["weight_decay"]))
        started = time.perf_counter()
        for epoch in range(int(config["epochs"])):
            optimizer.zero_grad()
            positions = model(x_tensor)
            scale = (float(config["volatility_target_annual"]) / vols).clamp(max=4.0)
            scaled = positions * scale
            effective = torch.where(train_mask, scaled, torch.zeros_like(scaled))
            counts = train_mask.sum(dim=1).clamp_min(1)
            gross = (effective * labels).sum(dim=1) / counts
            active_dates = train_mask.any(dim=1)
            gross = gross[active_dates]
            eff_active = effective[active_dates]
            turnover = torch.abs(eff_active[1:] - eff_active[:-1]).sum(dim=1) / counts[active_dates][1:]
            padded_turnover = torch.cat([torch.zeros(1), turnover])
            net = gross - padded_turnover * float(config["native_cost_bps_per_unit_turnover"]) / 10_000.0
            sharpe = net.mean() / net.std(unbiased=False).clamp_min(1e-8) * math.sqrt(365.0)
            loss = -sharpe + turnover_penalty * padded_turnover.mean()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            if epoch in {0, int(config["epochs"]) - 1} or (epoch + 1) % 20 == 0:
                curves.append({"seed": seed, "epoch": epoch + 1, "loss": float(loss.detach()), "train_sharpe": float(sharpe.detach()), "turnover_penalty": turnover_penalty})
        with torch.no_grad():
            positions = model(x_tensor)
            scale = (float(config["volatility_target_annual"]) / vols).clamp(max=4.0)
            all_positions.append((positions * scale).numpy())
        records.append({
            "seed": seed,
            "fit_dates": int(train_dates.sum()),
            "features": len(feature_names),
            "sequence_length": seq_len,
            "epochs": int(config["epochs"]),
            "turnover_penalty": turnover_penalty,
            "runtime_seconds": time.perf_counter() - started,
        })
    ensemble = np.mean(all_positions, axis=0)
    values = []
    for row in frame.itertuples():
        values.append(float(ensemble[date_index[row.date], symbol_index[row.symbol]]))
    return DmnFitResult(pd.Series(values, index=frame.index), records, pd.DataFrame(curves))


def behaviour_summary(frame: pd.DataFrame, weights: dict[str, pd.Series], role: str = "CHALLENGE") -> tuple[pd.DataFrame, dict[str, Any]]:
    role_frame = frame[frame.data_role.eq(role)]
    flattened: dict[str, pd.Series] = {}
    for system, values in weights.items():
        block = role_frame[["date", "symbol"]].copy()
        block["weight"] = values.loc[role_frame.index].to_numpy()
        flattened[system] = block.pivot(index="date", columns="symbol", values="weight").fillna(0.0).stack()
    matrix = pd.DataFrame(flattened).corr(method="spearman").fillna(0.0)
    systems = list(matrix.columns)
    parent = {name: name for name in systems}

    def find(name: str) -> str:
        while parent[name] != name:
            parent[name] = parent[parent[name]]
            name = parent[name]
        return name

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    for i, left in enumerate(systems):
        for right in systems[i + 1 :]:
            if abs(float(matrix.loc[left, right])) >= 0.90:
                union(left, right)
    clusters = {name: find(name) for name in systems}
    counts = pd.Series(list(clusters.values())).value_counts()
    eigenvalues = np.linalg.eigvalsh(matrix.to_numpy()) if len(matrix) else np.array([])
    neff = float(eigenvalues.sum() ** 2 / np.square(eigenvalues).sum()) if len(eigenvalues) and np.square(eigenvalues).sum() else 0.0
    summary = {
        "systems": len(systems),
        "behaviour_clusters": int(len(counts)),
        "behaviour_neff": neff,
        "top_cluster_share": float(counts.max() / len(systems)) if len(systems) else 0.0,
        "cluster_assignment": clusters,
    }
    return matrix, summary
