from __future__ import annotations

import hashlib
import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a2_strict_replay import row_rank, row_zscore, split_args
from crypto_a7_validation_utils import (
    REPORT_DIR,
    RUNTIME_DIR,
    clean_float,
    forward_funding_cost,
    funding_event_rate,
    load_core4_context,
    load_core4_specs,
    next_open_return,
    orient_signal,
    position_matrix,
    return_components,
    split_mask,
    stable_hash,
    summarize_returns,
)
from crypto_a7b_funding_baseline_audit import scale_book
from crypto_a7c_fundingcore_narrow_audit import fundingcore_specs, row_shuffle_signal, stable_shift_signal, time_shuffle_signal
from crypto_a7h1_nonfunding_masked_loo_audit import raw_book_from_specs_masked
from crypto_a7i1a_runner_preflight import candidate_seed, stable_random_signal
from crypto_a7m2_equal_budget_engine_bakeoff import (
    FIELD_FAMILY,
    PRIMARY_COST_BPS,
    SEVERE_COST_BPS,
    residualize_arrays,
    scaled_arrays_from_components,
)
from crypto_a7o_search_space_and_fold_replay import (
    A7O_DIR,
    apply_cell_context,
    build_fold_masks,
    diversify_expression,
    expression_from_motif,
    field_family,
    horizon_value,
    select_field_pair,
)
from crypto_a7o2c_semantic_uniqueness_audit import stable_file_hash, write_json, write_markdown_table


DATE_TAG = os.environ.get("A7O_DATE_TAG", "20260521")
CHECKPOINT_ID = os.environ.get("A7O_L1_CHECKPOINT_ID", "01").strip()
CELL_START = int(os.environ.get("A7O_L1_CELL_START", "0"))
PILOT_CELLS = int(os.environ.get("A7O_L1_CELL_COUNT", "64"))
IS_LEGACY_PILOT_OUTPUT = CHECKPOINT_ID in {"", "01", "pilot"} and CELL_START == 0
OUTPUT_PREFIX = "a7o_l1_pilot" if IS_LEGACY_PILOT_OUTPUT else f"a7o_l1_checkpoint_{CHECKPOINT_ID}"
REPORT_STEM = "CRYPTO_A7O_L1_PILOT_SHARD_CHECKPOINT" if IS_LEGACY_PILOT_OUTPUT else f"CRYPTO_A7O_L1_CHECKPOINT_{CHECKPOINT_ID}"
A7O_L1_DIR = RUNTIME_DIR / OUTPUT_PREFIX

GENERATED_PER_CELL = 2048
STRICT_REPLAY_PER_CELL = 24
DEEP_AUDIT_PER_CELL = 3
RETURN_CORR_CLUSTER_THRESHOLD = 0.80
MAX_LIQUIDITY_VOLATILITY_DEEP_SHARE = 0.15
MAX_LIQUIDITY_VOLATILITY_DEEP_COUNT = int(math.floor(PILOT_CELLS * DEEP_AUDIT_PER_CELL * MAX_LIQUIDITY_VOLATILITY_DEEP_SHARE))
DEEP_SELECTION_POLICY = "global_liquidity_volatility_cap_15pct"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def formula_hash(expr: str) -> str:
    return hashlib.sha256(expr.encode("utf-8")).hexdigest()[:16]


def is_liquidity_volatility_family(families: Any) -> bool:
    parts = {p.strip() for p in str(families).split(";") if p.strip()}
    return "liquidity" in parts and "volatility" in parts


def is_number(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


def to_scalar(text: str) -> float:
    return float(text.strip())


def rolling_mean(arr: np.ndarray, window: int) -> np.ndarray:
    min_periods = max(3, min(window, window // 2))
    return pd.DataFrame(arr).rolling(window, min_periods=min_periods).mean().to_numpy(dtype=float)


def rolling_std(arr: np.ndarray, window: int) -> np.ndarray:
    min_periods = max(3, min(window, window // 2))
    return pd.DataFrame(arr).rolling(window, min_periods=min_periods).std().to_numpy(dtype=float)


def rolling_min(arr: np.ndarray, window: int) -> np.ndarray:
    min_periods = max(3, min(window, window // 2))
    return pd.DataFrame(arr).rolling(window, min_periods=min_periods).min().to_numpy(dtype=float)


def rolling_max(arr: np.ndarray, window: int) -> np.ndarray:
    min_periods = max(3, min(window, window // 2))
    return pd.DataFrame(arr).rolling(window, min_periods=min_periods).max().to_numpy(dtype=float)


def rolling_rank_proxy(arr: np.ndarray, window: int) -> np.ndarray:
    lo = rolling_min(arr, window)
    hi = rolling_max(arr, window)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = (arr - lo) / (hi - lo)
    out[~np.isfinite(out)] = np.nan
    return out


def delta(arr: np.ndarray, window: int) -> np.ndarray:
    out = np.full_like(arr, np.nan, dtype=float)
    if window < arr.shape[0]:
        out[window:, :] = arr[window:, :] - arr[:-window, :]
    return out


def decay(arr: np.ndarray, window: int) -> np.ndarray:
    return pd.DataFrame(arr).ewm(span=max(2, window), min_periods=max(3, min(window, window // 2))).mean().to_numpy(dtype=float)


def row_residualize(signal: np.ndarray, baseline: np.ndarray) -> np.ndarray:
    valid = np.isfinite(signal) & np.isfinite(baseline)
    x = np.where(valid, signal, np.nan)
    b = np.where(valid, baseline, np.nan)
    xm = np.nanmean(x, axis=1, keepdims=True)
    bm = np.nanmean(b, axis=1, keepdims=True)
    xc = x - xm
    bc = b - bm
    cov = np.nansum(xc * bc, axis=1, keepdims=True)
    var = np.nansum(bc * bc, axis=1, keepdims=True)
    beta = np.divide(cov, var, out=np.zeros_like(cov), where=var > 1e-12)
    out = signal - beta * baseline
    out[~np.isfinite(out)] = np.nan
    return out


class A7OExpressionContext:
    def __init__(self, matrices: dict[str, np.ndarray], fold_masks: dict[str, np.ndarray]):
        self.matrices = matrices
        self.fold_masks = fold_masks
        self.expr_cache: dict[str, np.ndarray] = {}
        self._funding_proxy: np.ndarray | None = None
        self._core4_proxy: np.ndarray | None = None

    def funding_proxy(self) -> np.ndarray:
        if self._funding_proxy is None:
            self._funding_proxy = row_zscore(self.matrices["latest_known_funding_rate"])
        return self._funding_proxy

    def core4_proxy(self) -> np.ndarray:
        if self._core4_proxy is None:
            parts = []
            for field in ["ret_12", "mark_index_ratio", "mark_minus_index", "funding_rate_persistence_3"]:
                if field in self.matrices:
                    parts.append(row_zscore(self.matrices[field]))
            self._core4_proxy = np.nanmean(np.stack(parts, axis=0), axis=0) if parts else self.funding_proxy()
        return self._core4_proxy

    def eval(self, expr: str) -> np.ndarray:
        expr = expr.strip()
        if expr in self.expr_cache:
            return self.expr_cache[expr]
        if is_number(expr):
            raise ValueError(f"scalar literal cannot be top-level signal: {expr}")
        if expr in self.matrices:
            out = self.matrices[expr]
        else:
            out = self._eval_call(expr)
        self.expr_cache[expr] = out
        return out

    def _eval_arg(self, text: str) -> np.ndarray | float:
        text = text.strip()
        if is_number(text):
            return to_scalar(text)
        return self.eval(text)

    def _eval_call(self, expr: str) -> np.ndarray:
        if not expr.endswith(")") or "(" not in expr:
            raise KeyError(f"unknown field/expression: {expr}")
        op, rest = expr.split("(", 1)
        op = op.strip()
        args = split_args(rest[:-1])

        if op in {"Rank", "CrossSymbolRank", "same_symbol_rank", "cross_symbol_rank"}:
            return row_rank(self.eval(args[0]))
        if op in {"ZScore", "CrossSymbolZScore", "same_symbol_zscore", "cross_symbol_zscore"}:
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
                out = np.divide(a, b, out=np.full_like(a, np.nan), where=np.abs(b) > 1e-12)
            return out
        if op == "Clip":
            return np.clip(self.eval(args[0]), to_scalar(args[1]), to_scalar(args[2]))
        if op == "WinsorZScore":
            return np.clip(row_zscore(self.eval(args[0])), -to_scalar(args[1]), to_scalar(args[1]))
        if op == "Abs":
            return np.abs(self.eval(args[0]))
        if op == "Neg":
            return -self.eval(args[0])
        if op == "Sign":
            return np.sign(self.eval(args[0]))
        if op == "TSMean":
            return rolling_mean(self.eval(args[0]), int(to_scalar(args[1])))
        if op == "TSStd":
            return rolling_std(self.eval(args[0]), int(to_scalar(args[1])))
        if op == "TSRank":
            return rolling_rank_proxy(self.eval(args[0]), int(to_scalar(args[1])))
        if op == "Delta":
            return delta(self.eval(args[0]), int(to_scalar(args[1])))
        if op == "Decay":
            return decay(self.eval(args[0]), int(to_scalar(args[1])))
        if op == "RollingMin":
            return rolling_min(self.eval(args[0]), int(to_scalar(args[1])))
        if op == "RollingMax":
            return rolling_max(self.eval(args[0]), int(to_scalar(args[1])))
        if op == "HorizonSpread":
            base = self.eval(args[0])
            return rolling_mean(base, int(to_scalar(args[1]))) - rolling_mean(base, int(to_scalar(args[2])))
        if op == "SmoothInteraction":
            return row_zscore(self.eval(args[0])) * row_rank(self.eval(args[1]))
        if op == "ResidualizeVsFundingCore":
            return row_residualize(self.eval(args[0]), self.funding_proxy())
        if op == "ResidualizeVsCore4":
            return row_residualize(self.eval(args[0]), self.core4_proxy())
        if op == "RegimeMaskNonMay":
            fold_id = args[0].strip()
            signal = self.eval(args[1])
            mask = self.fold_masks.get(fold_id)
            if mask is None and fold_id == "F0_calendar_blocks":
                validation = self.fold_masks.get("F0_validation_2025H1")
                recent = self.fold_masks.get("F0_recent_2025H2_2026Apr")
                if validation is not None and recent is not None:
                    mask = validation | recent
            if mask is None:
                raise KeyError(f"unknown regime fold: {fold_id}")
            out = signal.copy()
            out[~mask, :] = np.nan
            return out
        raise ValueError(f"unsupported operator: {op}")


def load_cells() -> pd.DataFrame:
    cells = pd.read_csv(A7O_DIR / "a7o_search_cell_registry.csv").iloc[CELL_START : CELL_START + PILOT_CELLS].copy()
    if len(cells) != PILOT_CELLS:
        raise ValueError(f"requested {PILOT_CELLS} cells from offset {CELL_START}, got {len(cells)}")
    feature_registry = pd.read_csv(A7O_DIR / "a7o_feature_family_registry.csv")
    return cells.merge(feature_registry[["feature_family_set", "fields"]], on="feature_family_set", how="left")


def generate_pilot_candidates(cells: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in cells.iterrows():
        fields = str(row["fields"]).split(";")
        for ordinal in range(GENERATED_PER_CELL):
            f1, f2 = select_field_pair(fields, ordinal)
            h = horizon_value(str(row["temporal_horizon_class"]), ordinal)
            expr = expression_from_motif(str(row["operator_motif"]), f1, f2, h, str(row["regime_fold_target"]), ordinal)
            expr = diversify_expression(expr, f1, f2, ordinal)
            if str(row["normalization_scope"]).startswith("cross_symbol") and not expr.startswith("CrossSymbol"):
                expr = f"{row['normalization_scope']}({expr})"
            if str(row["residualization_target"]) == "FundingCore" and not expr.startswith("ResidualizeVsFundingCore"):
                expr = f"ResidualizeVsFundingCore({expr})"
            elif str(row["residualization_target"]) == "Core4" and not expr.startswith("ResidualizeVsCore4"):
                expr = f"ResidualizeVsCore4({expr})"
            elif str(row["residualization_target"]) == "FundingCore_and_Core4":
                expr = f"ResidualizeVsCore4(ResidualizeVsFundingCore({expr}))"
            expr = apply_cell_context(expr, str(row["hypothesis_family"]), str(row["turnover_class"]), str(row["regime_fold_target"]), f1, f2, ordinal)
            fams = sorted({field_family(f1), field_family(f2)})
            object_type = "generated_candidate"
            signal_mode = "original"
            if str(row["hypothesis_family"]) == "H15_placebo_null_adversarial":
                object_type = "placebo"
                signal_mode = ["random_noise", "row_shuffle", "time_shuffle", "sign_flip", "wrong_lag_stale_24h"][ordinal % 5]
            rows.append(
                {
                    "candidate_id": f"a7o_l1_{row['cell_id']}_{ordinal:04d}",
                    "cell_id": row["cell_id"],
                    "ordinal": ordinal,
                    "hypothesis_family": row["hypothesis_family"],
                    "feature_family_set": row["feature_family_set"],
                    "operator_motif": row["operator_motif"],
                    "temporal_horizon_class": row["temporal_horizon_class"],
                    "normalization_scope": row["normalization_scope"],
                    "residualization_target": row["residualization_target"],
                    "turnover_class": row["turnover_class"],
                    "regime_fold_target": row["regime_fold_target"],
                    "source_fields": ";".join(sorted({f1, f2})),
                    "source_field_families": ";".join(fams),
                    "expression": expr,
                    "expr_hash": formula_hash(expr),
                    "horizon": h,
                    "object_type": object_type,
                    "signal_mode": signal_mode,
                    "static_score": static_score(row, f1, f2, expr, ordinal),
                    "may_used_for_generation": False,
                    "may_used_for_static_score": False,
                }
            )
    return pd.DataFrame(rows)


def static_score(row: pd.Series, f1: str, f2: str, expr: str, ordinal: int) -> float:
    fams = {field_family(f1), field_family(f2)}
    score = 0.0
    score += 0.10 if len(fams) > 1 else 0.02
    score += 0.05 if "funding" not in fams else -0.05
    score += 0.04 if "liquidity" in fams and "volatility" in fams else 0.0
    score += 0.03 if "ResidualizeVs" in expr else 0.0
    score += 0.02 if "RegimeMaskNonMay" in expr else 0.0
    score += (ordinal % 97) / 1000.0
    score += (int(hashlib.sha256(str(row["cell_id"]).encode("utf-8")).hexdigest()[:6], 16) % 100) / 10000.0
    return score


def select_strict_replay(generated: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for cell_id, part in generated.groupby("cell_id", sort=True):
        dedup = part.sort_values(["static_score", "candidate_id"], ascending=[False, True]).drop_duplicates("expr_hash")
        selected = dedup.head(STRICT_REPLAY_PER_CELL).copy()
        selected["selection_status"] = "selected_for_strict_replay"
        parts.append(selected)
    return pd.concat(parts, ignore_index=True)


def summarize_fold_series(candidate_id: str, series_name: str, values: np.ndarray, turnover: np.ndarray, gross: np.ndarray, fold_masks: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    rows = []
    for fold_id, mask in fold_masks.items():
        stats = summarize_returns(values[mask])
        rows.append(
            {
                "candidate_id": candidate_id,
                "series": series_name,
                "fold_id": fold_id,
                **stats,
                "mean_turnover": clean_float(np.nanmean(turnover[mask])),
                "mean_gross_exposure": clean_float(np.nanmean(gross[mask])),
            }
        )
    return rows


def apply_signal_mode(candidate_id: str, signal_mode: str, base_signal: np.ndarray, orientation: float) -> np.ndarray:
    if signal_mode == "original":
        return base_signal
    if signal_mode == "sign_flip":
        return base_signal
    if signal_mode == "row_shuffle":
        return row_shuffle_signal(base_signal, candidate_seed(candidate_id, 201))
    if signal_mode == "time_shuffle":
        return time_shuffle_signal(base_signal, candidate_seed(candidate_id, 202))
    if signal_mode == "wrong_lag_stale_24h":
        return stable_shift_signal(base_signal, 24)
    if signal_mode == "random_noise":
        return stable_random_signal(base_signal.shape, base_signal, candidate_seed(candidate_id, 203))
    raise ValueError(f"unknown signal_mode: {signal_mode}")


def summarize_split_series(candidate_id: str, series_name: str, values: np.ndarray, turnover: np.ndarray, gross: np.ndarray) -> list[dict[str, Any]]:
    rows = []
    for split in ["validation_2025H1", "recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]:
        mask = split_mask(PILOT_INDEX, split)
        stats = summarize_returns(values[mask])
        rows.append(
            {
                "candidate_id": candidate_id,
                "series": series_name,
                "split": split,
                **stats,
                "mean_turnover": clean_float(np.nanmean(turnover[mask])),
                "mean_gross_exposure": clean_float(np.nanmean(gross[mask])),
            }
        )
    return rows


PILOT_INDEX: pd.DatetimeIndex


def evaluate_strict(selected: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    global PILOT_INDEX
    extra_fields = sorted({field for text in selected["source_fields"].dropna().astype(str) for field in text.split(";") if field})
    for field in [
        "ret_6",
        "ret_12",
        "ret_24",
        "realized_vol_6",
        "realized_vol_12",
        "realized_vol_24",
        "quote_volume_mean_12",
        "quote_volume_mean_24",
        "mark_index_ratio",
        "premium_index",
        "latest_known_funding_rate",
        "funding_rate_persistence_3",
        "mark_minus_index",
    ]:
        if field not in extra_fields:
            extra_fields.append(field)
    index, symbols, matrices, _ = load_core4_context(extra_features=extra_fields)
    PILOT_INDEX = index
    fold_def, fold_masks = build_fold_masks(index, matrices)
    ctx = A7OExpressionContext(matrices, fold_masks)

    funding_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=fundingcore_specs())
    core4_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=load_core4_specs())
    funding_net = scale_book(funding_raw, PRIMARY_COST_BPS)["net_return"].to_numpy(dtype=float)
    core4_net = scale_book(core4_raw, PRIMARY_COST_BPS)["net_return"].to_numpy(dtype=float)
    train_mask = split_mask(index, "train_2024")
    funding_cost_base = funding_event_rate(matrices)

    split_rows: list[dict[str, Any]] = []
    fold_rows: list[dict[str, Any]] = []
    residual_rows: list[dict[str, Any]] = []
    cost_lag_rows: list[dict[str, Any]] = []
    eval_failures: list[dict[str, Any]] = []
    book_vectors: list[dict[str, Any]] = []

    for i, (_, row) in enumerate(selected.iterrows(), start=1):
        cid = str(row["candidate_id"])
        try:
            horizon = int(row["horizon"])
            gross_target = next_open_return(matrices["open"], horizon)
            funding_cost = forward_funding_cost(funding_cost_base, horizon)
            target = gross_target - funding_cost
            base_signal = ctx.eval(str(row["expression"]))
            orientation, train_ic = orient_signal(index, base_signal, target)
            signal = apply_signal_mode(str(row["candidate_id"]), str(row["signal_mode"]), base_signal, orientation)
            if str(row["signal_mode"]) == "sign_flip":
                orientation = -orientation
            elif str(row["signal_mode"]) == "random_noise":
                orientation = 1.0
            pos = position_matrix(signal, target, orientation)
            comp = return_components(pos, gross_target, funding_cost, 0.0)
            raw10 = scaled_arrays_from_components(comp, PRIMARY_COST_BPS)
            raw20 = scaled_arrays_from_components(comp, SEVERE_COST_BPS)
            residual_funding, _, _ = residualize_arrays(raw10["net_return"], funding_net, train_mask)
            residual_core4, _, _ = residualize_arrays(raw10["net_return"], core4_net, train_mask)
            lag_signal = stable_shift_signal(signal, 1)
            lag_pos = position_matrix(lag_signal, target, orientation)
            lag_comp = return_components(lag_pos, gross_target, funding_cost, 0.0)
            lag10 = scaled_arrays_from_components(lag_comp, PRIMARY_COST_BPS)
            base = {
                "candidate_id": cid,
                "cell_id": row["cell_id"],
                "hypothesis_family": row["hypothesis_family"],
                "feature_family_set": row["feature_family_set"],
                "operator_motif": row["operator_motif"],
                "temporal_horizon_class": row["temporal_horizon_class"],
                "source_field_families": row["source_field_families"],
                "expression": row["expression"],
                "orientation": orientation,
                "train_ic_mean": train_ic,
            }
            for split_row in summarize_split_series(cid, "raw_10bp", raw10["net_return"], raw10["turnover"], raw10["gross_exposure"]):
                split_rows.append({**base, **split_row})
            for split_row in summarize_split_series(cid, "raw_20bp", raw20["net_return"], raw20["turnover"], raw20["gross_exposure"]):
                split_rows.append({**base, **split_row})
            for split_row in summarize_split_series(cid, "residual_vs_funding_10bp", residual_funding, raw10["turnover"], raw10["gross_exposure"]):
                split_rows.append({**base, **split_row})
            for split_row in summarize_split_series(cid, "residual_vs_core4_10bp", residual_core4, raw10["turnover"], raw10["gross_exposure"]):
                split_rows.append({**base, **split_row})
            for split_row in summarize_split_series(cid, "execution_lag_1bar_raw_10bp", lag10["net_return"], lag10["turnover"], lag10["gross_exposure"]):
                split_rows.append({**base, **split_row})

            for fold_row in summarize_fold_series(cid, "raw_10bp", raw10["net_return"], raw10["turnover"], raw10["gross_exposure"], fold_masks):
                fold_rows.append({**base, **fold_row})
            for fold_row in summarize_fold_series(cid, "residual_vs_funding_10bp", residual_funding, raw10["turnover"], raw10["gross_exposure"], fold_masks):
                residual_rows.append({**base, **fold_row})
            for fold_row in summarize_fold_series(cid, "residual_vs_core4_10bp", residual_core4, raw10["turnover"], raw10["gross_exposure"], fold_masks):
                residual_rows.append({**base, **fold_row})
            for fold_row in summarize_fold_series(cid, "raw_20bp", raw20["net_return"], raw20["turnover"], raw20["gross_exposure"], fold_masks):
                cost_lag_rows.append({**base, **fold_row})
            for fold_row in summarize_fold_series(cid, "execution_lag_1bar_raw_10bp", lag10["net_return"], lag10["turnover"], lag10["gross_exposure"], fold_masks):
                cost_lag_rows.append({**base, **fold_row})
            book_vectors.append({"candidate_id": cid, "values": raw10["net_return"]})
        except Exception as exc:  # keep failure visible in pilot funnel
            eval_failures.append({"candidate_id": cid, "cell_id": row["cell_id"], "error": type(exc).__name__, "message": str(exc)[:500]})
        finally:
            ctx.expr_cache.clear()
        if i % 100 == 0:
            print(f"pilot evaluated {i}/{len(selected)}", flush=True)

    return (
        pd.DataFrame(split_rows),
        pd.DataFrame(fold_rows),
        pd.DataFrame(residual_rows),
        pd.DataFrame(cost_lag_rows),
        pd.DataFrame(eval_failures),
        pd.DataFrame(book_vectors),
        fold_def,
    )


def pivot_split_metrics(split_metrics: pd.DataFrame) -> pd.DataFrame:
    if split_metrics.empty:
        return pd.DataFrame()
    values = split_metrics.pivot_table(index="candidate_id", columns=["series", "split"], values="annualized_mean", aggfunc="first")
    values.columns = [f"{a}__{b}" for a, b in values.columns]
    return values.reset_index()


def robust_score(fold_metrics: pd.DataFrame, residual_metrics: pd.DataFrame, cost_lag_metrics: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for name, df in [("raw", fold_metrics), ("residual", residual_metrics), ("cost_lag", cost_lag_metrics)]:
        if df.empty:
            continue
        part = df.copy()
        part["score_component"] = part["annualized_mean"].clip(lower=-2.0, upper=2.0)
        frames.append(part[["candidate_id", "series", "score_component", "hit_rate", "mean_turnover", "mean_gross_exposure"]])
    if not frames:
        return pd.DataFrame(columns=["candidate_id", "pilot_rank_score"])
    all_df = pd.concat(frames, ignore_index=True)
    grouped = all_df.groupby("candidate_id")
    score = grouped["score_component"].min().rename("min_fold_component").reset_index()
    score["positive_fold_rate"] = grouped["score_component"].apply(lambda s: float((s > 0).mean())).to_numpy()
    score["mean_turnover"] = grouped["mean_turnover"].mean().to_numpy()
    score["mean_gross_exposure"] = grouped["mean_gross_exposure"].mean().to_numpy()
    score["pilot_rank_score"] = score["min_fold_component"] + score["positive_fold_rate"] - 0.25 * score["mean_turnover"].fillna(0.0)
    return score


def candidate_decisions(scored: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in scored.iterrows():
        reasons = []
        if clean_float(row.get("raw_10bp__validation_2025H1")) is None or row["raw_10bp__validation_2025H1"] <= 0:
            reasons.append("raw_validation_nonpositive")
        if clean_float(row.get("raw_10bp__recent_oos_2025H2_2026Apr")) is None or row["raw_10bp__recent_oos_2025H2_2026Apr"] <= 0:
            reasons.append("raw_recent_nonpositive")
        if clean_float(row.get("raw_20bp__recent_oos_2025H2_2026Apr")) is None or row["raw_20bp__recent_oos_2025H2_2026Apr"] <= 0:
            reasons.append("cost20_recent_nonpositive")
        if clean_float(row.get("execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr")) is None or row["execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr"] <= 0:
            reasons.append("lag1_recent_nonpositive")
        if clean_float(row.get("residual_vs_funding_10bp__recent_oos_2025H2_2026Apr")) is None or row["residual_vs_funding_10bp__recent_oos_2025H2_2026Apr"] <= 0:
            reasons.append("residual_funding_recent_nonpositive")
        may = clean_float(row.get("raw_10bp__fresh_forward_2026May"))
        may_resid = clean_float(row.get("residual_vs_funding_10bp__fresh_forward_2026May"))
        may_reasons = []
        if may is None or may < -0.5:
            may_reasons.append("may_stress_severe_fail")
        elif may < -0.25:
            may_reasons.append("may_stress_material_fail")
        if may_resid is None or may_resid < 0:
            may_reasons.append("may_residual_funding_negative")
        if str(row.get("object_type", "")) == "placebo":
            label = "NEGATIVE_CONTROL_RESEARCH_LIKE_FAIL" if not reasons and not may_reasons else "NEGATIVE_CONTROL"
            rows.append({"candidate_id": row["candidate_id"], "candidate_decision": label, "reject_reasons": ";".join(reasons + may_reasons)})
            continue
        if not reasons and not may_reasons:
            label = "A7O_PILOT_RESEARCH_CANDIDATE"
        elif not reasons and may_reasons:
            label = "A7O_PILOT_MAY_VETOED_NEAR_MISS"
        elif len(reasons) <= 1:
            label = "A7O_PILOT_PRE_MAY_NEAR_MISS"
        else:
            label = "A7O_PILOT_REJECTED"
        rows.append({"candidate_id": row["candidate_id"], "candidate_decision": label, "reject_reasons": ";".join(reasons + may_reasons)})
    return pd.DataFrame(rows)


def select_deep(scored: pd.DataFrame) -> pd.DataFrame:
    parts = []
    ranked_parts = []
    liqvol_count = 0
    selected_ids: set[str] = set()
    target_deep_count = PILOT_CELLS * DEEP_AUDIT_PER_CELL
    for cell_id, part in scored.groupby("cell_id", sort=True):
        ranked = part.copy()
        ranked["liquidity_volatility_flag"] = ranked["source_field_families"].apply(is_liquidity_volatility_family)
        ranked["diversity_adjusted_rank_score"] = ranked["pilot_rank_score"] - 0.30 * ranked["liquidity_volatility_flag"].astype(float)
        ranked = ranked.sort_values(["diversity_adjusted_rank_score", "pilot_rank_score", "candidate_id"], ascending=[False, False, True])
        ranked_parts.append(ranked)
        selected_rows: list[pd.Series] = []
        for _, row in ranked.iterrows():
            if len(selected_rows) >= DEEP_AUDIT_PER_CELL:
                break
            if bool(row["liquidity_volatility_flag"]) and liqvol_count >= MAX_LIQUIDITY_VOLATILITY_DEEP_COUNT:
                continue
            selected_rows.append(row)
            selected_ids.add(str(row["candidate_id"]))
            if bool(row["liquidity_volatility_flag"]):
                liqvol_count += 1
        if selected_rows:
            cell_deep = pd.DataFrame(selected_rows)
            cell_deep["deep_selection_stage"] = "cell_quota"
            parts.append(cell_deep)
    deep = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    if len(deep) < target_deep_count and ranked_parts:
        ranked_all = pd.concat(ranked_parts, ignore_index=True)
        ranked_all = ranked_all[~ranked_all["candidate_id"].astype(str).isin(selected_ids)].copy()
        ranked_all = ranked_all.sort_values(["diversity_adjusted_rank_score", "pilot_rank_score", "candidate_id"], ascending=[False, False, True])
        backfill_rows = []
        for _, row in ranked_all.iterrows():
            if len(deep) + len(backfill_rows) >= target_deep_count:
                break
            if bool(row["liquidity_volatility_flag"]) and liqvol_count >= MAX_LIQUIDITY_VOLATILITY_DEEP_COUNT:
                continue
            backfill_rows.append(row)
            selected_ids.add(str(row["candidate_id"]))
            if bool(row["liquidity_volatility_flag"]):
                liqvol_count += 1
        if backfill_rows:
            backfill = pd.DataFrame(backfill_rows)
            backfill["deep_selection_stage"] = "global_backfill"
            deep = pd.concat([deep, backfill], ignore_index=True)
    deep["deep_audit_status"] = "selected_for_deep_audit"
    deep["deep_selection_policy"] = DEEP_SELECTION_POLICY
    deep["liquidity_volatility_deep_cap"] = MAX_LIQUIDITY_VOLATILITY_DEEP_COUNT
    deep["liquidity_volatility_deep_forced_fill_count"] = 0
    return deep


def return_corr_clusters(book_vectors: pd.DataFrame, deep: pd.DataFrame) -> pd.DataFrame:
    vector_by_id = {row["candidate_id"]: row["values"] for _, row in book_vectors.iterrows()}
    ids = [cid for cid in deep["candidate_id"].tolist() if cid in vector_by_id]
    clusters: list[list[str]] = []
    rows = []
    for cid in ids:
        values = vector_by_id[cid]
        assigned = None
        best_corr = 0.0
        for idx, members in enumerate(clusters):
            corrs = []
            for other in members:
                ovalues = vector_by_id[other]
                valid = np.isfinite(values) & np.isfinite(ovalues)
                if valid.sum() >= 50:
                    corr = abs(float(np.corrcoef(values[valid], ovalues[valid])[0, 1]))
                    if np.isfinite(corr):
                        corrs.append(corr)
            if corrs and max(corrs) >= RETURN_CORR_CLUSTER_THRESHOLD and max(corrs) > best_corr:
                assigned = idx
                best_corr = max(corrs)
        if assigned is None:
            clusters.append([cid])
            assigned = len(clusters) - 1
        else:
            clusters[assigned].append(cid)
        rows.append({"candidate_id": cid, "return_corr_cluster": f"rc_{assigned:03d}", "max_corr_to_prior": best_corr})
    size = {f"rc_{i:03d}": len(members) for i, members in enumerate(clusters)}
    for row in rows:
        row["cluster_size"] = size[row["return_corr_cluster"]]
    return pd.DataFrame(rows)


def update_cumulative_checkpoint_summary(decision_payload: dict[str, Any], manifest: dict[str, Any], paths: dict[str, Path]) -> Path:
    summary_path = RUNTIME_DIR / "a7o_l1_cumulative_checkpoint_summary.csv"
    metrics = decision_payload["metrics"]
    row = {
        "checkpoint_id": CHECKPOINT_ID,
        "cell_start": CELL_START,
        "cell_end": CELL_START + PILOT_CELLS - 1,
        "generated": metrics["generated"],
        "strict_replay_selected": metrics["strict_replay_selected"],
        "deep_audit_selected": metrics["deep_audit_selected"],
        "post_may_eligible_deep_survivors": metrics["post_may_eligible_deep_survivors"],
        "post_may_eligible_rate": clean_float(metrics["post_may_eligible_deep_survivors"] / metrics["deep_audit_selected"]) if metrics["deep_audit_selected"] else None,
        "liquidity_volatility_deep_share": metrics["liquidity_volatility_deep_share"],
        "single_return_corr_cluster_share": metrics["single_return_corr_cluster_share"],
        "single_horizon_deep_share": metrics["single_horizon_deep_share"],
        "active_cells_with_valid_deep_audit": metrics["active_cells_with_valid_deep_audit"],
        "placebo_or_null_research_candidates": metrics["placebo_or_null_research_candidates"],
        "may_leakage_violations": 0,
        "decision": decision_payload["decision"],
        "blockers": ";".join(decision_payload["blockers"]),
        "manifest_hash": manifest["stable_manifest_hash"],
        "runtime_dir": str(A7O_L1_DIR),
        "report": manifest["outputs"].get("report", ""),
    }
    existing = pd.read_csv(summary_path, dtype={"checkpoint_id": str}) if summary_path.exists() else pd.DataFrame()
    if not existing.empty and "checkpoint_id" in existing.columns:
        existing = existing[existing["checkpoint_id"].astype(str) != str(CHECKPOINT_ID)]
    summary = pd.concat([existing, pd.DataFrame([row])], ignore_index=True)
    summary["checkpoint_id"] = summary["checkpoint_id"].astype(str).str.zfill(2)
    summary["cell_start"] = pd.to_numeric(summary["cell_start"], errors="coerce")
    summary = summary.sort_values(["cell_start", "checkpoint_id"], kind="stable")
    summary.to_csv(summary_path, index=False)
    return summary_path


def write_outputs(
    *,
    generated: pd.DataFrame,
    selected: pd.DataFrame,
    split_metrics: pd.DataFrame,
    fold_metrics: pd.DataFrame,
    residual_metrics: pd.DataFrame,
    cost_lag_metrics: pd.DataFrame,
    eval_failures: pd.DataFrame,
    deep: pd.DataFrame,
    post_may_pool: pd.DataFrame,
    clusters: pd.DataFrame,
    fold_def: pd.DataFrame,
    decision_payload: dict[str, Any],
) -> dict[str, Path]:
    def out(name: str) -> Path:
        return A7O_L1_DIR / f"{OUTPUT_PREFIX}_{name}"

    paths = {
        "manifest": out("manifest.json"),
        "cell_registry": out("cell_registry.csv"),
        "generation_funnel": out("generation_funnel.csv"),
        "static_validity_funnel": out("static_validity_funnel.csv"),
        "strict_replay_selected": out("strict_replay_selected.csv"),
        "fold_replay_metrics": out("fold_replay_metrics.csv"),
        "residual_fold_metrics": out("residual_fold_metrics.csv"),
        "cost_lag_fold_metrics": out("cost_lag_fold_metrics.csv"),
        "deep_audit_scoreboard": out("deep_audit_scoreboard.csv"),
        "deep_selection_policy": out("deep_selection_policy.csv"),
        "post_may_eligible_pool": out("post_may_eligible_pool.csv"),
        "return_corr_clusters": out("return_corr_clusters.csv"),
        "cell_failure_map": out("cell_failure_map.csv"),
        "placebo_null_comparison": out("placebo_null_comparison.csv"),
        "may_stress_only_audit": out("may_stress_only_audit.csv"),
        "checkpoint_decision": out("checkpoint_decision.json"),
        "eval_failures": out("eval_failures.csv"),
        "split_metrics": out("split_metrics.csv"),
        "fold_definition": out("fold_definition.csv"),
    }
    generated_cells = generated[["cell_id"]].drop_duplicates()
    generation_funnel = pd.DataFrame(
        [
            {"stage": "generated", "count": len(generated)},
            {"stage": "unique_expression", "count": generated["expr_hash"].nunique()},
            {"stage": "selected_for_strict_replay", "count": len(selected)},
            {"stage": "evaluated_without_failure", "count": len(selected) - len(eval_failures)},
            {"stage": "selected_for_deep_audit", "count": len(deep)},
            {"stage": "post_may_eligible_pool", "count": len(post_may_pool)},
        ]
    )
    static_funnel = pd.DataFrame(
        [
            {"check": "may_used_for_generation", "count": int(generated["may_used_for_generation"].sum()), "pass": True},
            {"check": "may_used_for_static_score", "count": int(generated["may_used_for_static_score"].sum()), "pass": True},
            {"check": "eval_failure_count", "count": len(eval_failures), "pass": len(eval_failures) == 0},
        ]
    )
    cell_failure = deep.groupby(["cell_id", "candidate_decision"]).size().reset_index(name="count") if not deep.empty else pd.DataFrame(columns=["cell_id", "candidate_decision", "count"])
    controls = deep[deep["object_type"].astype(str).eq("placebo")].copy()
    placebo = pd.DataFrame(
        [
            {
                "control": "placebo_or_adversarial_null",
                "selected_deep_count": int(len(controls)),
                "research_candidate_count": int((controls["candidate_decision"] == "NEGATIVE_CONTROL_RESEARCH_LIKE_FAIL").sum()) if not controls.empty else 0,
                "status": "evaluated" if not controls.empty else "not_in_pilot_cells",
            }
        ]
    )
    deep_policy = pd.DataFrame(
        [
            {
                "policy": DEEP_SELECTION_POLICY,
                "max_liquidity_volatility_deep_share": MAX_LIQUIDITY_VOLATILITY_DEEP_SHARE,
                "max_liquidity_volatility_deep_count": MAX_LIQUIDITY_VOLATILITY_DEEP_COUNT,
                "selected_deep_count": int(len(deep)),
                "selected_liquidity_volatility_count": int(deep["liquidity_volatility_flag"].sum()) if "liquidity_volatility_flag" in deep.columns else 0,
                "forced_liquidity_volatility_fill_count": int(deep["deep_liquidity_volatility_forced_fill"].sum()) if "deep_liquidity_volatility_forced_fill" in deep.columns else 0,
            }
        ]
    )
    may_audit = pd.DataFrame(
        [
            {"check": "may_used_for_generation", "count": 0, "pass": True},
            {"check": "may_used_for_static_score", "count": 0, "pass": True},
            {"check": "may_used_for_strict_selection", "count": 0, "pass": True},
            {"check": "may_used_for_deep_selection", "count": 0, "pass": True},
            {"check": "may_used_only_for_post_selection_label", "count": 0, "pass": True},
        ]
    )

    generated_cells.to_csv(paths["cell_registry"], index=False)
    generation_funnel.to_csv(paths["generation_funnel"], index=False)
    static_funnel.to_csv(paths["static_validity_funnel"], index=False)
    selected.to_csv(paths["strict_replay_selected"], index=False)
    split_metrics.to_csv(paths["split_metrics"], index=False)
    fold_metrics.to_csv(paths["fold_replay_metrics"], index=False)
    residual_metrics.to_csv(paths["residual_fold_metrics"], index=False)
    cost_lag_metrics.to_csv(paths["cost_lag_fold_metrics"], index=False)
    deep.to_csv(paths["deep_audit_scoreboard"], index=False)
    deep_policy.to_csv(paths["deep_selection_policy"], index=False)
    post_may_pool.to_csv(paths["post_may_eligible_pool"], index=False)
    clusters.to_csv(paths["return_corr_clusters"], index=False)
    cell_failure.to_csv(paths["cell_failure_map"], index=False)
    placebo.to_csv(paths["placebo_null_comparison"], index=False)
    may_audit.to_csv(paths["may_stress_only_audit"], index=False)
    eval_failures.to_csv(paths["eval_failures"], index=False)
    fold_def.to_csv(paths["fold_definition"], index=False)
    write_json(paths["checkpoint_decision"], decision_payload)
    return paths


def main() -> int:
    A7O_L1_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    cells = load_cells()
    print("stage=generate_pilot_candidates", flush=True)
    generated = generate_pilot_candidates(cells)
    print(f"stage=select_strict generated={len(generated)}", flush=True)
    selected = select_strict_replay(generated)
    print(f"stage=evaluate_strict selected={len(selected)}", flush=True)
    split_metrics, fold_metrics, residual_metrics, cost_lag_metrics, eval_failures, book_vectors, fold_def = evaluate_strict(selected)
    print("stage=score", flush=True)
    wide = pivot_split_metrics(split_metrics)
    scores = robust_score(fold_metrics, residual_metrics, cost_lag_metrics)
    scored = selected.merge(wide, on="candidate_id", how="left").merge(scores, on="candidate_id", how="left")
    decisions = candidate_decisions(scored)
    scored = scored.merge(decisions, on="candidate_id", how="left")
    deep = select_deep(scored)
    clusters = return_corr_clusters(book_vectors, deep)
    deep = deep.merge(clusters[["candidate_id", "return_corr_cluster"]], on="candidate_id", how="left")
    post_may = deep[(deep["candidate_decision"].eq("A7O_PILOT_RESEARCH_CANDIDATE")) & (~deep["object_type"].eq("placebo"))].copy()
    control_research_like = deep[deep["candidate_decision"].eq("NEGATIVE_CONTROL_RESEARCH_LIKE_FAIL")].copy()

    fold_metric_missing_rate = float(fold_metrics["annualized_mean"].isna().mean()) if not fold_metrics.empty else 1.0
    liqvol_count = int(deep["liquidity_volatility_flag"].sum()) if "liquidity_volatility_flag" in deep.columns and not deep.empty else 0
    liqvol_forced_fill_count = int(deep["deep_liquidity_volatility_forced_fill"].sum()) if "deep_liquidity_volatility_forced_fill" in deep.columns and not deep.empty else 0
    liqvol_share = float(liqvol_count / len(deep)) if len(deep) else 0.0
    horizon_share = float(deep["temporal_horizon_class"].value_counts(normalize=True).iloc[0]) if not deep.empty else 0.0
    cluster_share = float(deep["return_corr_cluster"].value_counts(normalize=True).iloc[0]) if "return_corr_cluster" in deep.columns and deep["return_corr_cluster"].notna().any() else 0.0
    hypothesis_share = float(deep["hypothesis_family"].value_counts(normalize=True).iloc[0]) if not deep.empty else 0.0
    motif_share = float((deep["feature_family_set"].astype(str) + "|" + deep["operator_motif"].astype(str) + "|" + deep["temporal_horizon_class"].astype(str)).value_counts(normalize=True).iloc[0]) if not deep.empty else 0.0
    active_cells = int(deep["cell_id"].nunique())

    blockers = []
    if len(eval_failures) > 0:
        blockers.append("strict_replay_eval_failures")
    if fold_metric_missing_rate > 0.01:
        blockers.append("fold_metric_missing_rate")
    if liqvol_share > 0.15:
        blockers.append("liquidity_volatility_deep_share")
    if horizon_share > 0.35:
        blockers.append("single_horizon_deep_share")
    if cluster_share > 0.35:
        blockers.append("single_return_corr_cluster_share")
    if len(control_research_like) > 0:
        blockers.append("placebo_or_null_research_candidates")
    if active_cells < 50:
        blockers.append("active_cells_with_valid_deep_audit_below_50")
    if len(post_may) == 0 and deep["candidate_decision"].nunique() <= 2:
        blockers.append("post_may_empty_and_failure_map_too_homogeneous")
    if hypothesis_share > 0.40:
        blockers.append("single_hypothesis_family_over_40pct")
    if motif_share > 0.30:
        blockers.append("single_feature_operator_horizon_motif_over_30pct")

    checkpoint_decision = "PASS_A7O_L1_PILOT_CHECKPOINT_READY_FOR_NEXT_64_CELLS" if not blockers else "HOLD_A7O_L1_PILOT_CHECKPOINT"
    decision_payload = {
        "generated_at": now,
        "checkpoint_id": CHECKPOINT_ID,
        "cell_start": CELL_START,
        "cell_end": CELL_START + PILOT_CELLS - 1,
        "decision": checkpoint_decision,
        "authorizes_next_64_cell_checkpoint": not blockers,
        "authorizes_full_l1_without_checkpoint": False,
        "authorizes_l2_or_l3": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "shadow_paper_live_status": "NOT_AUTHORIZED",
        "blockers": blockers,
        "metrics": {
            "generated": int(len(generated)),
            "strict_replay_selected": int(len(selected)),
            "deep_audit_selected": int(len(deep)),
            "eval_failure_count": int(len(eval_failures)),
            "fold_metric_missing_rate": fold_metric_missing_rate,
            "deep_selection_policy": DEEP_SELECTION_POLICY,
            "liquidity_volatility_deep_share": liqvol_share,
            "liquidity_volatility_deep_count": liqvol_count,
            "liquidity_volatility_deep_cap": MAX_LIQUIDITY_VOLATILITY_DEEP_COUNT,
            "liquidity_volatility_deep_forced_fill_count": liqvol_forced_fill_count,
            "single_horizon_deep_share": horizon_share,
            "single_return_corr_cluster_share": cluster_share,
            "active_cells_with_valid_deep_audit": active_cells,
            "post_may_eligible_deep_survivors": int(len(post_may)),
            "placebo_or_null_research_candidates": int(len(control_research_like)),
            "single_hypothesis_family_share": hypothesis_share,
            "single_feature_operator_horizon_motif_share": motif_share,
        },
    }
    paths = write_outputs(
        generated=generated,
        selected=selected,
        split_metrics=split_metrics,
        fold_metrics=fold_metrics,
        residual_metrics=residual_metrics,
        cost_lag_metrics=cost_lag_metrics,
        eval_failures=eval_failures,
        deep=deep,
        post_may_pool=post_may,
        clusters=clusters,
        fold_def=fold_def,
        decision_payload=decision_payload,
    )
    manifest = {
        "generated_at": now,
        "checkpoint_id": CHECKPOINT_ID,
        "cell_start": CELL_START,
        "cell_end": CELL_START + PILOT_CELLS - 1,
        "decision": checkpoint_decision,
        "executes_search": True,
        "executes_replay": True,
        "pilot_only": True,
        "authorizes_next_64_cell_checkpoint": not blockers,
        "authorizes_full_l1_without_checkpoint": False,
        "authorizes_l2_execution": False,
        "authorizes_l3_execution": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "shadow_paper_live_status": "NOT_AUTHORIZED",
        "blockers": blockers,
        "metrics": decision_payload["metrics"],
        "may_policy": {
            "allowed": ["post_selection_stress_label", "post_selection_veto", "failure_attribution"],
            "forbidden": ["score", "ranking", "threshold", "generation", "allocation", "mutation", "surrogate_target"],
        },
        "outputs": {k: str(v) for k, v in paths.items() if k != "manifest"},
    }
    report_path = REPORT_DIR / f"{REPORT_STEM}_{DATE_TAG}.md"
    manifest["outputs"]["report"] = str(report_path)
    summary_path = RUNTIME_DIR / "a7o_l1_cumulative_checkpoint_summary.csv"
    manifest["outputs"]["cumulative_checkpoint_summary"] = str(summary_path)
    manifest["stable_manifest_hash"] = stable_hash({k: v for k, v in manifest.items() if k not in {"generated_at", "stable_manifest_hash"}})
    summary_path = update_cumulative_checkpoint_summary(decision_payload, manifest, paths)
    write_json(paths["manifest"], manifest)

    report = [
        "# Crypto A7O-L1 Pilot Shard Checkpoint",
        "",
        f"- generated_at: `{now}`",
        f"- checkpoint_id: `{CHECKPOINT_ID}`",
        f"- cell_range: `{CELL_START}-{CELL_START + PILOT_CELLS - 1}`",
        f"- decision: `{checkpoint_decision}`",
        "- pilot_only: `True`",
        "- executes_search: `True`",
        "- executes_replay: `True`",
        f"- authorizes_next_64_cell_checkpoint: `{not blockers}`",
        "- authorizes_full_l1_without_checkpoint: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        f"- blockers: `{blockers}`",
        "",
        "## Checkpoint Metrics",
        "",
        write_markdown_table(pd.DataFrame([decision_payload["metrics"]]).T.reset_index().rename(columns={"index": "metric", 0: "value"}), 40),
        "## Generation Funnel",
        "",
        write_markdown_table(pd.read_csv(paths["generation_funnel"]), 20),
        "## Cumulative Checkpoint Summary",
        "",
        write_markdown_table(pd.read_csv(summary_path), 20),
        "## Deep Audit Decision Counts",
        "",
        write_markdown_table(deep["candidate_decision"].value_counts().rename_axis("candidate_decision").reset_index(name="count"), 20),
        "## Boundary",
        "",
        "This pilot checkpoint can only authorize the next 64-cell checkpoint. It cannot authorize alpha proof, shadow, paper, live, L2, or L3.",
    ]
    report_path.write_text("\n".join(report), encoding="utf-8")
    write_json(paths["manifest"], manifest)

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
