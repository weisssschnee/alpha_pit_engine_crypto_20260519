from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a2_strict_replay import split_args


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path("G:/AlphaFactory_CryptoData")
METRICS_PATH = DATA_ROOT / "gold" / "features" / "binance_metrics_1h_features_v1.parquet"
BASE_PANEL_PATH = DATA_ROOT / "gold" / "panels" / "crypto_core12_1h_with_aggtrades_features_v1.parquet"
A7S1_ACCEPTANCE = ROOT / "runtime" / "a7s1_metrics_acceptance_audit" / "a7s1_acceptance_authorization_matrix.json"
A7S1_SOURCE_DIR = DATA_ROOT / "alphafactory_crypto" / "runtime" / "a7s1_metrics_source_trace"

OUT_DIR = ROOT / "runtime" / "a7s2m_metrics_registry_diagnostic"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7S2M_METRICS_REGISTRY_DIAGNOSTIC_20260522.md"

CORE12 = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "AVAXUSDT",
    "LINKUSDT",
    "BCHUSDT",
    "LTCUSDT",
    "SUIUSDT",
]

SPLITS = {
    "train_2024": ("2024-01-01T00:00:00Z", "2024-12-31T23:00:00Z"),
    "validation_2025H1": ("2025-01-01T00:00:00Z", "2025-06-30T23:00:00Z"),
    "recent_oos_2025H2_2026Apr": ("2025-07-01T00:00:00Z", "2026-04-30T23:00:00Z"),
    "fresh_may_2026": ("2026-05-01T00:00:00Z", None),
}

VALIDATION = "validation_2025H1"
RECENT = "recent_oos_2025H2_2026Apr"
MAY = "fresh_may_2026"

PRIMARY_COST_BPS = 10.0
SEVERE_COST_BPS = 20.0
GENERATED_CAP = 500
STRICT_REPLAY_CAP = 96
DEEP_AUDIT_CAP = 48

INDEPENDENT_FIELDS = [
    "open_interest",
    "open_interest_value",
    "global_long_short_account_ratio",
    "top_long_short_account_ratio",
    "top_long_short_position_ratio",
    "taker_buy_sell_volume_ratio",
]

DERIVED_METRICS_FIELDS = [
    "open_interest_change_1h",
    "open_interest_change_4h",
    "open_interest_change_24h",
    "open_interest_zscore_168h",
    "open_interest_value_change_1h",
    "open_interest_value_change_4h",
    "open_interest_value_change_24h",
    "open_interest_value_zscore_168h",
    "global_long_short_account_ratio_change_1h",
    "global_long_short_account_ratio_change_4h",
    "global_long_short_account_ratio_change_24h",
    "global_long_short_account_ratio_zscore_168h",
    "top_long_short_account_ratio_change_1h",
    "top_long_short_account_ratio_change_4h",
    "top_long_short_account_ratio_change_24h",
    "top_long_short_account_ratio_zscore_168h",
    "top_long_short_position_ratio_change_1h",
    "top_long_short_position_ratio_change_4h",
    "top_long_short_position_ratio_change_24h",
    "top_long_short_position_ratio_zscore_168h",
    "taker_buy_sell_volume_ratio_change_1h",
    "taker_buy_sell_volume_ratio_change_4h",
    "taker_buy_sell_volume_ratio_change_24h",
    "taker_buy_sell_volume_ratio_zscore_168h",
    "open_interest_x_price_move_1h",
    "open_interest_x_taker_imbalance",
]

BASE_CONTEXT_FIELDS = [
    "open",
    "close",
    "ret_1",
    "ret_6",
    "ret_12",
    "ret_24",
    "realized_vol_12",
    "realized_vol_24",
    "mark_index_ratio",
    "premium_index",
    "latest_known_funding_rate",
    "taker_imbalance",
    "quote_asset_volume",
    "number_of_trades",
]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def clean_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def stable_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def stable_int(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:12], 16)


def is_number(text: str) -> bool:
    try:
        float(str(text).strip())
        return True
    except ValueError:
        return False


def to_scalar(text: str) -> float:
    return float(str(text).strip())


def row_rank(mat: np.ndarray) -> np.ndarray:
    return pd.DataFrame(mat).rank(axis=1, pct=True).to_numpy(dtype=float)


def row_zscore(mat: np.ndarray) -> np.ndarray:
    mean = np.nanmean(mat, axis=1, keepdims=True)
    std = np.nanstd(mat, axis=1, keepdims=True)
    std[std == 0] = np.nan
    return (mat - mean) / std


def rolling_mean(arr: np.ndarray, window: int) -> np.ndarray:
    return pd.DataFrame(arr).rolling(window, min_periods=window).mean().to_numpy(dtype=float)


def delta(arr: np.ndarray, window: int) -> np.ndarray:
    out = np.full_like(arr, np.nan, dtype=float)
    if window < arr.shape[0]:
        out[window:, :] = arr[window:, :] - arr[:-window, :]
    return out


def decay(arr: np.ndarray, window: int) -> np.ndarray:
    return pd.DataFrame(arr).ewm(span=max(2, window), min_periods=window).mean().to_numpy(dtype=float)


class ExprContext:
    def __init__(self, matrices: dict[str, np.ndarray]):
        self.matrices = matrices
        self.cache: dict[str, np.ndarray] = {}

    def eval(self, expr: str) -> np.ndarray:
        expr = str(expr).strip()
        if expr in self.cache:
            return self.cache[expr]
        if expr in self.matrices:
            out = self.matrices[expr]
        else:
            out = self._eval_call(expr)
        self.cache[expr] = out
        return out

    def _eval_arg(self, text: str) -> np.ndarray | float:
        text = text.strip()
        return to_scalar(text) if is_number(text) else self.eval(text)

    def _eval_call(self, expr: str) -> np.ndarray:
        if not expr.endswith(")") or "(" not in expr:
            raise KeyError(f"unknown expression: {expr}")
        op, rest = expr.split("(", 1)
        args = split_args(rest[:-1])
        if op in {"Rank", "CrossSymbolRank"}:
            return row_rank(self.eval(args[0]))
        if op in {"ZScore", "CrossSymbolZScore"}:
            return row_zscore(self.eval(args[0]))
        if op == "Mul":
            return self.eval(args[0]) * self.eval(args[1])
        if op == "Add":
            return self.eval(args[0]) + self.eval(args[1])
        if op == "Sub":
            return self.eval(args[0]) - self.eval(args[1])
        if op == "SafeDiv":
            a = self.eval(args[0])
            b = self._eval_arg(args[1])
            with np.errstate(divide="ignore", invalid="ignore"):
                return np.divide(a, b, out=np.full_like(a, np.nan), where=np.abs(b) > 1e-12)
        if op == "Abs":
            return np.abs(self.eval(args[0]))
        if op == "Neg":
            return -self.eval(args[0])
        if op == "TSMean":
            return rolling_mean(self.eval(args[0]), int(to_scalar(args[1])))
        if op == "Delta":
            return delta(self.eval(args[0]), int(to_scalar(args[1])))
        if op == "Decay":
            return decay(self.eval(args[0]), int(to_scalar(args[1])))
        if op == "HorizonSpread":
            base = self.eval(args[0])
            return rolling_mean(base, int(to_scalar(args[1]))) - rolling_mean(base, int(to_scalar(args[2])))
        raise ValueError(f"unsupported operator: {op}")


def split_mask(index: pd.DatetimeIndex, name: str) -> np.ndarray:
    start, end = SPLITS[name]
    mask = np.asarray(index >= pd.Timestamp(start))
    if end is not None:
        mask &= np.asarray(index <= pd.Timestamp(end))
    return mask


def row_ic(signal: np.ndarray, target: np.ndarray) -> np.ndarray:
    s = row_rank(signal)
    t = row_rank(target)
    valid = np.isfinite(s) & np.isfinite(t)
    n = valid.sum(axis=1).astype(float)
    x = np.where(valid, s, 0.0)
    y = np.where(valid, t, 0.0)
    sx = x.sum(axis=1)
    sy = y.sum(axis=1)
    sxy = (x * y).sum(axis=1)
    sx2 = (x * x).sum(axis=1)
    sy2 = (y * y).sum(axis=1)
    den = np.sqrt((n * sx2 - sx * sx) * (n * sy2 - sy * sy))
    with np.errstate(divide="ignore", invalid="ignore"):
        out = (n * sxy - sx * sy) / den
    out[(n < 6) | ~np.isfinite(out)] = np.nan
    return out


def forward_open_return(open_mat: np.ndarray, horizon: int) -> np.ndarray:
    out = np.full_like(open_mat, np.nan, dtype=float)
    start = 1
    end = 1 + int(horizon)
    if end < open_mat.shape[0]:
        out[:-end, :] = open_mat[end:, :] / open_mat[start : open_mat.shape[0] - int(horizon), :] - 1.0
    return out


def top_bottom_book(signal: np.ndarray, target: np.ndarray, orientation: float, cost_bps: float, k: int = 3) -> dict[str, np.ndarray]:
    oriented = signal * orientation
    valid = np.isfinite(oriented) & np.isfinite(target)
    valid_rows = valid.sum(axis=1) >= (2 * k)
    pos = np.zeros_like(target, dtype=float)
    if np.any(valid_rows):
        high = np.where(valid, oriented, -np.inf)
        low = np.where(valid, oriented, np.inf)
        rows = np.where(valid_rows)[0]
        long_idx = np.argpartition(high[valid_rows], -k, axis=1)[:, -k:]
        short_idx = np.argpartition(low[valid_rows], k - 1, axis=1)[:, :k]
        weight = 0.5 / k
        for r_pos, r in enumerate(rows):
            pos[r, long_idx[r_pos]] = weight
            pos[r, short_idx[r_pos]] = -weight
    gross = np.nansum(pos * target, axis=1)
    prev = np.vstack([np.zeros((1, pos.shape[1])), pos[:-1, :]])
    turnover = np.nansum(np.abs(pos - prev), axis=1) / 2.0
    fee = turnover * (cost_bps / 10000.0)
    return {
        "net": gross - fee,
        "gross": gross,
        "turnover": turnover,
        "gross_exposure": np.nansum(np.abs(pos), axis=1),
    }


def apply_control(signal: np.ndarray, mode: str, seed_key: str) -> np.ndarray:
    if mode == "sign_flip":
        return -signal
    if mode == "wrong_lag":
        out = np.full_like(signal, np.nan)
        out[24:, :] = signal[:-24, :]
        return out
    if mode == "lag1_stress":
        out = np.full_like(signal, np.nan)
        out[1:, :] = signal[:-1, :]
        return out
    if mode == "time_shuffle":
        rng = np.random.default_rng(stable_int(seed_key))
        order = np.arange(signal.shape[0])
        rng.shuffle(order)
        return signal[order, :]
    if mode == "row_shuffle":
        out = signal.copy()
        rng = np.random.default_rng(stable_int(seed_key))
        for i in range(out.shape[0]):
            rng.shuffle(out[i])
        return out
    return signal


def summarize_series(index: pd.DatetimeIndex, split: str, signal: np.ndarray, target: np.ndarray, book10: dict[str, np.ndarray], book20: dict[str, np.ndarray]) -> dict[str, Any]:
    mask = split_mask(index, split)
    ic = row_ic(signal[mask], target[mask])
    net10 = book10["net"][mask]
    net20 = book20["net"][mask]
    gross_exp = book10["gross_exposure"][mask]
    return {
        "split": split,
        "rows": int(mask.sum()),
        "active_hours": int(np.sum(np.isfinite(net10) & (gross_exp > 0))),
        "mean_ic": clean_float(np.nanmean(ic)),
        "net_sum_10bps": clean_float(np.nansum(net10)),
        "net_sum_20bps": clean_float(np.nansum(net20)),
        "turnover_mean": clean_float(np.nanmean(book10["turnover"][mask])),
        "gross_exposure_mean": clean_float(np.nanmean(gross_exp)),
    }


def feature_registry() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for field in INDEPENDENT_FIELDS:
        rows.append(
            {
                "field_name": field,
                "field_role": "independent_source",
                "raw_source": "Binance Vision futures/um/daily/metrics",
                "is_independent_source": True,
                "is_derived": False,
                "observable_rule": "raw observable_time = 5m timestamp + 5min; 1h feature_available_time = hour + 1h",
                "execution_rule": "execution_time >= next 1h bar",
                "vendor_warning_caveat_required": True,
            }
        )
    for field in DERIVED_METRICS_FIELDS:
        rows.append(
            {
                "field_name": field,
                "field_role": "derived_metrics_feature",
                "raw_source": "derived from accepted Binance metrics and base panel context",
                "is_independent_source": False,
                "is_derived": True,
                "observable_rule": "derived using past-only transforms after 1h metrics availability",
                "execution_rule": "execution_time >= next 1h bar",
                "vendor_warning_caveat_required": True,
            }
        )
    for field in BASE_CONTEXT_FIELDS:
        rows.append(
            {
                "field_name": field,
                "field_role": "existing_market_context",
                "raw_source": "existing crypto_core12_1h_with_aggtrades_features_v1 panel",
                "is_independent_source": False,
                "is_derived": False,
                "observable_rule": "existing A7 panel contract",
                "execution_rule": "execution_time >= next 1h bar",
                "vendor_warning_caveat_required": False,
            }
        )
    return pd.DataFrame(rows)


def candidate_row(family: str, expr: str, horizon: int, fields: list[str], motif: str) -> dict[str, Any]:
    cid = f"a7s2m_{family}_{horizon}_{stable_id(expr + str(horizon))}"
    return {
        "candidate_id": cid,
        "generator": "crypto_a7s2m_metrics_registry_diagnostic",
        "production_family": family,
        "derived_feature_id": motif,
        "expression": expr,
        "horizon": horizon,
        "source_fields": ";".join(sorted(set(fields))),
        "source_field_families": "metrics_positioning",
        "feature_available_lag_bars": 1,
        "feature_timestamp_rule": "metrics 1h feature available at hour timestamp + 1h",
        "execution_rule": "next 1h bar or later; May stress post-selection only",
        "required_negative_controls": "row_shuffle;time_shuffle;wrong_lag;sign_flip",
        "decision": "A7S2M_GENERATED_CANDIDATE",
    }


def generate_candidates() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    oi_fields = [
        "open_interest_change_4h",
        "open_interest_change_24h",
        "open_interest_zscore_168h",
        "open_interest_value_change_24h",
        "open_interest_value_zscore_168h",
    ]
    crowd_fields = [
        "global_long_short_account_ratio_change_24h",
        "global_long_short_account_ratio_zscore_168h",
        "top_long_short_account_ratio_change_24h",
        "top_long_short_account_ratio_zscore_168h",
        "top_long_short_position_ratio_change_24h",
        "top_long_short_position_ratio_zscore_168h",
    ]
    taker_fields = [
        "taker_buy_sell_volume_ratio_change_4h",
        "taker_buy_sell_volume_ratio_change_24h",
        "taker_buy_sell_volume_ratio_zscore_168h",
    ]
    market_states = ["ret_24", "mark_index_ratio", "premium_index", "latest_known_funding_rate", "taker_imbalance"]

    for field in oi_fields:
        for horizon in [12, 24, 48]:
            rows.append(candidate_row("F0_open_interest_slow", f"Rank({field})", horizon, [field], "oi_rank"))
            rows.append(candidate_row("F0_open_interest_slow", f"ZScore({field})", horizon, [field], "oi_zscore"))
            rows.append(candidate_row("F0_open_interest_slow", f"Decay({field},12)", horizon, [field], "oi_decay12"))
            rows.append(candidate_row("F0_open_interest_slow", f"HorizonSpread({field},12,48)", horizon, [field], "oi_horizon_spread"))

    for field in oi_fields:
        for state in market_states:
            for horizon in [24, 48]:
                rows.append(candidate_row("F1_oi_market_interaction", f"Mul(ZScore({field}),Rank({state}))", horizon, [field, state], "oi_x_market"))

    for field in crowd_fields:
        for horizon in [12, 24, 48]:
            rows.append(candidate_row("F2_crowding_positioning", f"Rank({field})", horizon, [field], "crowding_rank"))
            rows.append(candidate_row("F2_crowding_positioning", f"Neg(ZScore({field}))", horizon, [field], "crowding_contrarian"))
            rows.append(candidate_row("F2_crowding_positioning", f"HorizonSpread({field},12,48)", horizon, [field], "crowding_horizon_spread"))

    for field in taker_fields + ["open_interest_x_taker_imbalance"]:
        for state in ["taker_imbalance", "ret_12", "ret_24"]:
            for horizon in [12, 24, 48]:
                rows.append(candidate_row("F3_metrics_taker_divergence", f"Mul(ZScore({field}),Rank({state}))", horizon, [field, state], "metrics_taker_x_state"))

    for field in oi_fields + crowd_fields + taker_fields:
        for state in ["mark_index_ratio", "premium_index", "latest_known_funding_rate"]:
            rows.append(candidate_row("F4_metrics_basis_funding_interaction", f"Mul(Rank({field}),ZScore({state}))", 24, [field, state], "metrics_x_basis_funding"))

    out = pd.DataFrame(rows).drop_duplicates("candidate_id").head(GENERATED_CAP).copy()
    return out


def choose_strict_replay(generated: pd.DataFrame) -> pd.DataFrame:
    selected = []
    families = sorted(generated["production_family"].unique())
    quota = max(1, STRICT_REPLAY_CAP // max(1, len(families)))
    for family in families:
        part = generated[generated["production_family"].eq(family)].sort_values(["derived_feature_id", "expression", "horizon", "candidate_id"])
        selected.append(part.head(quota))
    return pd.concat(selected, ignore_index=True).head(STRICT_REPLAY_CAP)


def build_controls(selected: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in selected.iterrows():
        for mode in ["row_shuffle", "time_shuffle", "wrong_lag", "sign_flip"]:
            rec = row.to_dict()
            rec.update(
                {
                    "control_id": f"{row['candidate_id']}__ctrl_{mode}_{stable_id(str(row['candidate_id']) + mode)}",
                    "base_candidate_id": row["candidate_id"],
                    "control_mode": mode,
                    "object_type": "control",
                    "promotable": False,
                }
            )
            rec.pop("candidate_id", None)
            rows.append(rec)
    return pd.DataFrame(rows)


def required_columns(selected: pd.DataFrame) -> tuple[list[str], list[str]]:
    metric_cols = {"symbol", "timestamp"}
    base_cols = {"symbol", "timestamp", "open"}
    registry = set(INDEPENDENT_FIELDS) | set(DERIVED_METRICS_FIELDS)
    base_registry = set(BASE_CONTEXT_FIELDS)
    for text in selected["source_fields"].dropna().astype(str):
        for item in text.split(";"):
            if not item:
                continue
            if item in registry:
                metric_cols.add(item)
            if item in base_registry:
                base_cols.add(item)
    for field in ["ret_1", "ret_6", "ret_12", "ret_24", "mark_index_ratio", "premium_index", "latest_known_funding_rate", "taker_imbalance", "realized_vol_12", "realized_vol_24"]:
        base_cols.add(field)
    for field in INDEPENDENT_FIELDS + DERIVED_METRICS_FIELDS:
        metric_cols.add(field)
    return sorted(metric_cols), sorted(base_cols)


def load_panel(selected: pd.DataFrame) -> tuple[pd.DatetimeIndex, list[str], dict[str, np.ndarray], pd.DataFrame]:
    metric_cols, base_cols = required_columns(selected)
    metrics = pd.read_parquet(METRICS_PATH, columns=metric_cols)
    base = pd.read_parquet(BASE_PANEL_PATH, columns=base_cols)
    metrics["timestamp"] = pd.to_datetime(metrics["timestamp"], utc=True)
    base["timestamp"] = pd.to_datetime(base["timestamp"], utc=True)
    df = base.merge(metrics, on=["symbol", "timestamp"], how="inner", suffixes=("", "_metric"))
    df = df[df["symbol"].isin(CORE12)].sort_values(["timestamp", "symbol"]).copy()
    index = pd.DatetimeIndex(sorted(df["timestamp"].unique()))
    matrices: dict[str, np.ndarray] = {}
    for col in sorted(set(df.columns) - {"symbol", "timestamp", "interval"}):
        if col.endswith("_metric") or df[col].dtype == "object":
            continue
        pivot = df.pivot(index="timestamp", columns="symbol", values=col).reindex(index=index, columns=CORE12)
        matrices[col] = pivot.to_numpy(dtype=float)
    available = np.ones((len(index), len(CORE12)), dtype=bool)
    for field in INDEPENDENT_FIELDS:
        available &= np.isfinite(matrices[field])
    matrices["metrics_features_available"] = available.astype(float)
    return index, CORE12, matrices, df


def evaluate_signal(
    index: pd.DatetimeIndex,
    matrices: dict[str, np.ndarray],
    base_signal: np.ndarray,
    horizon: int,
    orientation: float,
    control_mode: str,
    seed_key: str,
) -> list[dict[str, Any]]:
    availability = matrices["metrics_features_available"].astype(bool)
    target = forward_open_return(matrices["open"], horizon)
    signal = np.where(availability, base_signal, np.nan)
    if control_mode != "original":
        signal = apply_control(signal, control_mode, seed_key)
        signal = np.where(availability, signal, np.nan)
    book10 = top_bottom_book(signal, target, orientation, PRIMARY_COST_BPS)
    book20 = top_bottom_book(signal, target, orientation, SEVERE_COST_BPS)
    lag1 = apply_control(signal, "lag1_stress", seed_key + "_lag1")
    lag_book10 = top_bottom_book(lag1, target, orientation, PRIMARY_COST_BPS)
    lag_book20 = top_bottom_book(lag1, target, orientation, SEVERE_COST_BPS)
    rows = []
    for split in SPLITS:
        m = summarize_series(index, split, signal, target, book10, book20)
        mask = split_mask(index, split)
        m.update(
            {
                "lag1_net_sum_10bps": clean_float(np.nansum(lag_book10["net"][mask])),
                "lag1_net_sum_20bps": clean_float(np.nansum(lag_book20["net"][mask])),
                "lag1_active_hours": int(np.sum(np.isfinite(lag_book10["net"][mask]) & (lag_book10["gross_exposure"][mask] > 0))),
            }
        )
        rows.append(m)
    return rows


def run_replay(selected: pd.DataFrame, controls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    index, symbols, matrices, merged = load_panel(selected)
    ctx = ExprContext(matrices)
    train_mask = split_mask(index, "train_2024")
    metric_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    signal_cache: dict[str, tuple[np.ndarray, float, float]] = {}

    for _, row in selected.iterrows():
        cid = str(row["candidate_id"])
        try:
            expr = str(row["expression"])
            horizon = int(row["horizon"])
            signal = np.where(matrices["metrics_features_available"].astype(bool), ctx.eval(expr), np.nan)
            target = forward_open_return(matrices["open"], horizon)
            base_train_ic = np.nanmean(row_ic(signal[train_mask], target[train_mask]))
            orientation = 1.0 if not np.isfinite(base_train_ic) or base_train_ic >= 0 else -1.0
            signal_cache[cid] = (signal, orientation, clean_float(base_train_ic) or 0.0)
            rows = evaluate_signal(index, matrices, signal, horizon, orientation, "original", cid)
            for m in rows:
                m.update(
                    {
                        "candidate_id": cid,
                        "base_candidate_id": cid,
                        "object_type": "candidate",
                        "control_mode": "original",
                        "production_family": row["production_family"],
                        "expression": expr,
                        "horizon": horizon,
                        "orientation": orientation,
                        "base_train_ic_for_orientation": clean_float(base_train_ic),
                    }
                )
                metric_rows.append(m)
        except Exception as exc:  # noqa: BLE001
            failures.append({"candidate_id": cid, "object_type": "candidate", "control_mode": "original", "eval_error": f"{type(exc).__name__}: {exc}"})

    for _, row in controls.iterrows():
        control_id = str(row["control_id"])
        base_id = str(row["base_candidate_id"])
        try:
            if base_id not in signal_cache:
                raise KeyError(f"base signal missing for {base_id}")
            signal, orientation, base_train_ic = signal_cache[base_id]
            horizon = int(row["horizon"])
            rows = evaluate_signal(index, matrices, signal, horizon, orientation, str(row["control_mode"]), control_id)
            for m in rows:
                m.update(
                    {
                        "candidate_id": control_id,
                        "base_candidate_id": base_id,
                        "object_type": "control",
                        "control_mode": row["control_mode"],
                        "production_family": row["production_family"],
                        "expression": row["expression"],
                        "horizon": horizon,
                        "orientation": orientation,
                        "base_train_ic_for_orientation": base_train_ic,
                    }
                )
                metric_rows.append(m)
        except Exception as exc:  # noqa: BLE001
            failures.append({"candidate_id": control_id, "base_candidate_id": base_id, "object_type": "control", "control_mode": row.get("control_mode", ""), "eval_error": f"{type(exc).__name__}: {exc}"})

    coverage = pd.DataFrame(
        [
            {
                "symbol": symbol,
                "rows": int(len(index)),
                "metrics_available_hours": int(np.sum(matrices["metrics_features_available"][:, i] > 0)),
                "metrics_available_rate": clean_float(np.mean(matrices["metrics_features_available"][:, i] > 0)),
                "timestamp_min": str(index.min()),
                "timestamp_max": str(index.max()),
            }
            for i, symbol in enumerate(symbols)
        ]
    )
    return pd.DataFrame(metric_rows), pd.DataFrame(failures), coverage, merged


def wide_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    idx = ["candidate_id", "base_candidate_id", "object_type", "control_mode", "production_family", "expression", "horizon"]
    values = [
        "active_hours",
        "mean_ic",
        "net_sum_10bps",
        "net_sum_20bps",
        "lag1_net_sum_10bps",
        "lag1_net_sum_20bps",
        "turnover_mean",
        "gross_exposure_mean",
    ]
    wide = metrics.pivot_table(index=idx, columns="split", values=values, aggfunc="first")
    wide.columns = [f"{a}__{b}" for a, b in wide.columns]
    return wide.reset_index()


def label_candidates(wide: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    candidates = wide[wide["object_type"].eq("candidate")].copy()
    controls = wide[wide["object_type"].eq("control")].copy()
    rows: list[dict[str, Any]] = []
    for _, cand in candidates.iterrows():
        cid = str(cand["candidate_id"])
        matched = controls[controls["base_candidate_id"].eq(cid)]
        val = float(cand.get(f"net_sum_10bps__{VALIDATION}", np.nan))
        recent = float(cand.get(f"net_sum_10bps__{RECENT}", np.nan))
        recent20 = float(cand.get(f"net_sum_20bps__{RECENT}", np.nan))
        lag1_recent = float(cand.get(f"lag1_net_sum_10bps__{RECENT}", np.nan))
        may = float(cand.get(f"net_sum_10bps__{MAY}", np.nan))
        may_active = float(cand.get(f"active_hours__{MAY}", np.nan))
        max_control_val = pd.to_numeric(matched.get(f"net_sum_10bps__{VALIDATION}", pd.Series(dtype=float)), errors="coerce").max()
        max_control_recent = pd.to_numeric(matched.get(f"net_sum_10bps__{RECENT}", pd.Series(dtype=float)), errors="coerce").max()
        control_val_recent_positive = int(
            (
                (pd.to_numeric(matched.get(f"net_sum_10bps__{VALIDATION}", pd.Series(dtype=float)), errors="coerce") > 0)
                & (pd.to_numeric(matched.get(f"net_sum_10bps__{RECENT}", pd.Series(dtype=float)), errors="coerce") > 0)
            ).sum()
        )
        dominates_controls = bool(val > max_control_val and recent > max_control_recent) if np.isfinite(max_control_val) and np.isfinite(max_control_recent) else True
        if control_val_recent_positive:
            label = "A7S2M_HOLD_CONTROL_CONTAMINATED"
        elif not (val > 0 and recent > 0):
            label = "A7S2M_HOLD_RAW_VAL_RECENT_FAIL"
        elif not dominates_controls:
            label = "A7S2M_HOLD_DOES_NOT_DOMINATE_CONTROLS"
        elif not recent20 > 0:
            label = "A7S2M_HOLD_COST20_FAIL"
        elif not lag1_recent > 0:
            label = "A7S2M_HOLD_LAG1_FAIL"
        elif not (may_active > 0 and may > 0):
            label = "A7S2M_NEAR_MISS_MAY_STRESS_FAIL"
        else:
            label = "A7S2M_RESEARCH_CLUE_FOR_FORENSIC"
        rows.append(
            {
                "candidate_id": cid,
                "production_family": cand["production_family"],
                "expression": cand["expression"],
                "horizon": int(cand["horizon"]),
                "validation_net10": clean_float(val),
                "recent_net10": clean_float(recent),
                "recent_net20": clean_float(recent20),
                "lag1_recent_net10": clean_float(lag1_recent),
                "may_net10_stress_only": clean_float(may),
                "may_active_hours": clean_float(may_active),
                "max_control_validation_net10": clean_float(max_control_val),
                "max_control_recent_net10": clean_float(max_control_recent),
                "dominates_controls": int(dominates_controls),
                "control_val_recent_positive_count": control_val_recent_positive,
                "a7s2m_label": label,
            }
        )
    labels = pd.DataFrame(rows)
    lineage_cols = ["candidate_id", "derived_feature_id", "source_fields", "required_negative_controls"]
    return labels.merge(selected[[c for c in lineage_cols if c in selected.columns]], on="candidate_id", how="left")


def select_deep_audit(labels: pd.DataFrame) -> pd.DataFrame:
    label_order = {
        "A7S2M_RESEARCH_CLUE_FOR_FORENSIC": 0,
        "A7S2M_NEAR_MISS_MAY_STRESS_FAIL": 1,
        "A7S2M_HOLD_LAG1_FAIL": 2,
        "A7S2M_HOLD_COST20_FAIL": 3,
        "A7S2M_HOLD_DOES_NOT_DOMINATE_CONTROLS": 4,
        "A7S2M_HOLD_CONTROL_CONTAMINATED": 5,
        "A7S2M_HOLD_RAW_VAL_RECENT_FAIL": 6,
    }
    labels = labels.copy()
    labels["label_order"] = labels["a7s2m_label"].map(label_order).fillna(99)
    selected = []
    quota = max(1, DEEP_AUDIT_CAP // max(1, labels["production_family"].nunique()))
    for family in sorted(labels["production_family"].unique()):
        part = labels[labels["production_family"].eq(family)].sort_values(
            ["label_order", "recent_net20", "lag1_recent_net10", "recent_net10"],
            ascending=[True, False, False, False],
        )
        selected.append(part.head(quota))
    return pd.concat(selected, ignore_index=True).head(DEEP_AUDIT_CAP)


def write_report(
    now: str,
    registry: pd.DataFrame,
    generated: pd.DataFrame,
    selected: pd.DataFrame,
    controls: pd.DataFrame,
    labels: pd.DataFrame,
    deep: pd.DataFrame,
    coverage: pd.DataFrame,
    failures: pd.DataFrame,
    authorization: dict[str, Any],
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    label_summary = labels.groupby(["production_family", "a7s2m_label"]).size().reset_index(name="rows") if not labels.empty else pd.DataFrame()
    registry_summary = registry.groupby(["field_role", "is_independent_source", "is_derived"]).size().reset_index(name="fields")
    lines = [
        "# Crypto A7S-2M Metrics Registry Diagnostic",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `small_structural_generation`",
        "- executes_replay: `small_controlled_diagnostic`",
        "- alpha proof / full search / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7S-2M supersedes the old pre-backfill A7S-2 feasibility stage for Binance metrics. It registers the accepted metrics source fields and runs a small controlled diagnostic on core12. It does not authorize alpha proof.",
        "",
        "May remains post-selection stress-only. It is not used for generation, orientation, threshold setting, ranking, or allocation.",
        "",
        "Vendor 5m bucket duplicate/gap/NaN caveats from A7S-1 are carried downstream.",
        "",
        "## Funnel",
        "",
        f"- generated: `{len(generated)}` / cap `{GENERATED_CAP}`",
        f"- strict replay candidates: `{len(selected)}` / cap `{STRICT_REPLAY_CAP}`",
        f"- controls: `{len(controls)}`",
        f"- deep audit selected: `{len(deep)}` / cap `{DEEP_AUDIT_CAP}`",
        "",
        "## Feature Registry Summary",
        "",
        table(registry_summary, max_rows=20),
        "",
        "## Coverage",
        "",
        table(coverage, max_rows=20),
        "",
        "## Label Summary",
        "",
        table(label_summary, max_rows=80),
        "",
        "## Deep Audit Pool",
        "",
        table(deep.sort_values(["a7s2m_label", "recent_net20"], ascending=[True, False]), max_rows=80),
        "",
        "## Eval Failures",
        "",
        table(failures, max_rows=40),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- If clean research clues exist, run A7S-3 forensic before any expanded replay.",
        "- If clues are control-contaminated or May-failed, keep metrics as state/exposure features and redesign objective before search.",
        "- Do not classify change/zscore/interaction columns as independent data sources.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    a7s1_auth = json.loads(A7S1_ACCEPTANCE.read_text(encoding="utf-8")) if A7S1_ACCEPTANCE.exists() else {}
    registry = feature_registry()
    generated = generate_candidates()
    selected = choose_strict_replay(generated)
    controls = build_controls(selected)
    metrics, failures, coverage, merged = run_replay(selected, controls)
    wide = wide_metrics(metrics) if not metrics.empty else pd.DataFrame()
    labels = label_candidates(wide, selected) if not wide.empty else pd.DataFrame()
    deep = select_deep_audit(labels) if not labels.empty else pd.DataFrame()

    research_clues = int(labels["a7s2m_label"].eq("A7S2M_RESEARCH_CLUE_FOR_FORENSIC").sum()) if not labels.empty else 0
    near_miss_may = int(labels["a7s2m_label"].eq("A7S2M_NEAR_MISS_MAY_STRESS_FAIL").sum()) if not labels.empty else 0
    control_contaminated = int(labels["a7s2m_label"].eq("A7S2M_HOLD_CONTROL_CONTAMINATED").sum()) if not labels.empty else 0
    blockers: list[str] = []
    diagnostic_warnings = list(a7s1_auth.get("warnings", []))
    if a7s1_auth.get("decision") != "PASS_A7S1_ACCEPTED_WITH_VENDOR_5M_WARNINGS":
        blockers.append("a7s1_acceptance_not_pass")
    if not failures.empty:
        blockers.append("eval_failures_present")
    if metrics.empty:
        blockers.append("no_metrics")
    if control_contaminated > 0:
        diagnostic_warnings.append("control_contamination_present_in_non_clue_pool")
    if research_clues == 0:
        diagnostic_warnings.append("no_clean_metrics_research_clue")

    if not failures.empty or metrics.empty:
        decision = "HOLD_A7S2M_EVALUATION_BLOCKER"
    elif research_clues > 0 and control_contaminated == 0:
        decision = "PASS_A7S2M_METRICS_CLUE_POOL_FOR_FORENSIC"
    elif research_clues > 0:
        decision = "PASS_A7S2M_CLEAN_CLUES_FOR_FORENSIC_HOLD_EXPANDED_REPLAY"
    else:
        decision = "HOLD_A7S2M_METRICS_DIAGNOSTIC_NO_CLEAN_CLUE"

    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "warnings": diagnostic_warnings,
        "generated_count": int(len(generated)),
        "strict_replay_candidate_count": int(len(selected)),
        "control_count": int(len(controls)),
        "metric_rows": int(len(metrics)),
        "deep_audit_count": int(len(deep)),
        "research_clue_count": research_clues,
        "near_miss_may_stress_fail_count": near_miss_may,
        "control_contaminated_candidate_count": control_contaminated,
        "executes_search": "small_structural_generation",
        "executes_replay": "small_controlled_diagnostic",
        "independent_source_fields": INDEPENDENT_FIELDS,
        "derived_fields_are_not_independent_sources": True,
        "may_policy": "stress_only_not_generation_ranking_threshold_orientation_or_allocation",
        "feature_available_time_rule": "1h metrics feature available at hour timestamp + 1h; execute next 1h bar or later",
        "vendor_5m_warning_caveat_required": True,
        "authorizes_a7s3_forensic": research_clues > 0 and failures.empty,
        "authorizes_expanded_replay": False,
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": [
            "A7S-3 forensic if clean clues exist; otherwise keep metrics as state/exposure features",
            "Do not expand metrics search from A7S-2M alone",
            "Carry A7S-1 vendor 5m warnings downstream",
        ],
    }

    registry.to_csv(OUT_DIR / "a7s2m_feature_registry.csv", index=False)
    generated.to_csv(OUT_DIR / "a7s2m_generated_candidates.csv", index=False)
    selected.to_csv(OUT_DIR / "a7s2m_selected_candidates.csv", index=False)
    controls.to_csv(OUT_DIR / "a7s2m_controls.csv", index=False)
    metrics.to_csv(OUT_DIR / "a7s2m_split_metrics.csv", index=False)
    wide.to_csv(OUT_DIR / "a7s2m_wide_metrics.csv", index=False)
    labels.to_csv(OUT_DIR / "a7s2m_candidate_labels.csv", index=False)
    deep.to_csv(OUT_DIR / "a7s2m_deep_audit_pool.csv", index=False)
    failures.to_csv(OUT_DIR / "a7s2m_eval_failures.csv", index=False)
    coverage.to_csv(OUT_DIR / "a7s2m_panel_coverage.csv", index=False)
    write_json(OUT_DIR / "a7s2m_authorization_matrix.json", authorization)
    write_json(
        OUT_DIR / "a7s2m_manifest.json",
        {
            "generated_at": now,
            "decision": decision,
            "output_dir": str(OUT_DIR),
            "report": str(REPORT_PATH),
            "metrics_panel": str(METRICS_PATH),
            "base_panel": str(BASE_PANEL_PATH),
            "source_trace_dir": str(A7S1_SOURCE_DIR),
            "merged_rows": int(len(merged)),
        },
    )
    write_report(now, registry, generated, selected, controls, labels, deep, coverage, failures, authorization)
    print(json.dumps({"decision": decision, "blockers": blockers, "research_clues": research_clues, "selected": len(selected), "controls": len(controls)}, indent=2))


if __name__ == "__main__":
    main()
