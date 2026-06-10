from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7aa1_primitive_response_map import horizon_label  # noqa: E402
from scripts.crypto_a7ab4_materialization_preflight import A7AB4Evaluator  # noqa: E402
from scripts.crypto_a7al2l_fast_derived_replay_preflight import SPLIT_END, SPLIT_ORDER, split_for_timestamps  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import (  # noqa: E402
    BASE_DIR,
    LATENT_PANEL,
    UPPER_REGIME_PANEL,
    load_base,
    load_group_fields,
    load_latent_numeric,
    parquet_schema,
)
from scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair import strict_symbols  # noqa: E402
from scripts.crypto_a7ff25r6_dense_funding_state_audit import (  # noqa: E402
    dense_ffill_and_age,
    rolling_mean_std_z,
    shift_matrix as dense_shift_matrix,
)
from scripts.crypto_a7ff8_expanded_numeric_probe import (  # noqa: E402
    DENSE_FUNDING_FIELDS,
    DERIVED_DEPS,
    OPERATORS,
    UPPER_ALIASES,
    expression_fields,
    load_upper_numeric,
)


DEFAULT_QUEUE = REPO / "runtime" / "a7ls30_productive_numeric_acceptance_20260610" / "a7ls30_selected_top240.csv"
RUNTIME = REPO / "runtime" / "a7reward1_portfolio_reward_model_20260610"
REPORT = REPO / "reports" / "CRYPTO_A7REWARD1_PORTFOLIO_REWARD_MODEL_20260610.md"

FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
HORIZONS = [1, 4, 8, 24]
PREMAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
ALL_EVAL_SPLITS = ["train_2024", *PREMAY_SPLITS, "known_may2026_stress"]
CONTROL_VARIANTS = ["one_bar_lag", "stale_168h", "sign_flip", "time_shuffle", "symbol_shuffle"]
PARETO_OBJECTIVES = [
    "obj_recent_sortino",
    "obj_min_oos_sortino",
    "obj_min_oos_floor_sortino",
    "obj_recent_sharpe",
    "obj_recent_rankic",
    "obj_stress_sortino",
    "obj_neg_recent_drawdown",
    "obj_neg_recent_turnover",
    "obj_neg_shuffle_control_ratio",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def md_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def add_pareto_columns(rewards: pd.DataFrame) -> pd.DataFrame:
    if rewards.empty:
        return rewards
    out = rewards.copy()
    out["min_oos_sortino"] = out[["validation_sortino", "test_sortino", "recent_sortino"]].min(axis=1)
    if {"validation_floor_sortino", "test_floor_sortino", "recent_floor_sortino"}.issubset(out.columns):
        out["min_oos_floor_sortino"] = out[["validation_floor_sortino", "test_floor_sortino", "recent_floor_sortino"]].min(axis=1)
    else:
        out["min_oos_floor_sortino"] = np.nan
    out["obj_recent_sortino"] = pd.to_numeric(out["recent_sortino"], errors="coerce")
    out["obj_min_oos_sortino"] = pd.to_numeric(out["min_oos_sortino"], errors="coerce")
    out["obj_min_oos_floor_sortino"] = pd.to_numeric(out["min_oos_floor_sortino"], errors="coerce")
    out["obj_recent_sharpe"] = pd.to_numeric(out["recent_sharpe"], errors="coerce")
    out["obj_recent_rankic"] = pd.to_numeric(out["recent_rankic"], errors="coerce")
    out["obj_stress_sortino"] = pd.to_numeric(out["stress_sortino"], errors="coerce").fillna(-1e9)
    out["obj_neg_recent_drawdown"] = -pd.to_numeric(out["recent_max_drawdown"], errors="coerce").abs()
    out["obj_neg_recent_turnover"] = -pd.to_numeric(out["recent_avg_turnover"], errors="coerce")
    out["obj_neg_shuffle_control_ratio"] = -pd.to_numeric(out["recent_shuffle_control_ratio"], errors="coerce")

    objective_passes = pd.DataFrame(
        {
            "recent_sortino_positive": out["recent_sortino"] > 0,
            "min_oos_sortino_positive": out["min_oos_sortino"] > 0,
            "min_oos_floor_sortino_positive": out["min_oos_floor_sortino"] > 0,
            "recent_sharpe_positive": out["recent_sharpe"] > 0,
            "recent_rankic_positive": out["recent_rankic"] > 0,
            "stress_sortino_positive": out["stress_sortino"] > 0,
            "shuffle_control_not_dominant": out["recent_shuffle_control_ratio"] < 1.0,
            "net_mean_oos_all_positive": out["oos_positive_split_count"] >= 3,
        }
    )
    out["objective_pass_count"] = objective_passes.sum(axis=1).astype(int)
    out["gate_pass"] = (
        (~out["hard_reject"])
        & (out["min_oos_sortino"] > 0)
        & (out["min_oos_floor_sortino"] > 0)
        & (out["recent_shuffle_control_ratio"] < 1.0)
    )

    values = out[PARETO_OBJECTIVES].replace([np.inf, -np.inf], np.nan).fillna(-1e9).to_numpy(dtype=float)
    n = values.shape[0]
    dominance_count = np.zeros(n, dtype=int)
    dominates_count = np.zeros(n, dtype=int)
    pareto_rank = np.ones(n, dtype=int)
    remaining = set(range(n))
    rank = 1
    while remaining:
        front = []
        for i in remaining:
            dominated = False
            for j in remaining:
                if i == j:
                    continue
                if np.all(values[j] >= values[i]) and np.any(values[j] > values[i]):
                    dominated = True
                    break
            if not dominated:
                front.append(i)
        if not front:
            break
        for i in front:
            pareto_rank[i] = rank
            remaining.remove(i)
        rank += 1
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if np.all(values[j] >= values[i]) and np.any(values[j] > values[i]):
                dominance_count[i] += 1
            if np.all(values[i] >= values[j]) and np.any(values[i] > values[j]):
                dominates_count[i] += 1
    out["pareto_rank"] = pareto_rank
    out["pareto_front"] = out["pareto_rank"].eq(1)
    out["dominance_count"] = dominance_count
    out["dominates_count"] = dominates_count
    return out


def selected_column_indices(timestamps: pd.DatetimeIndex, hours_per_split: int) -> np.ndarray:
    split = split_for_timestamps(timestamps)
    if hours_per_split <= 0:
        return np.arange(len(timestamps), dtype=int)
    selected: list[int] = []
    for split_name in SPLIT_ORDER:
        idx = np.where(split == split_name)[0]
        if len(idx):
            selected.extend(idx[-hours_per_split:].tolist())
    return np.array(sorted(set(selected)), dtype=int)


def contract_payload() -> dict[str, Any]:
    return {
        "stage": "A7REWARD-1",
        "reward_model": "cost_adjusted_portfolio_reward_v1",
        "mature_references_used": [
            "FinRL portfolio allocation reward: portfolio value/return with trading environment separation",
            "TensorTrade risk-adjusted reward schemes: Sharpe and Sortino style objective choices",
            "AlphaGen/AlphaForge style set-level reward: marginal contribution and alpha collection performance",
            "Crypto RL/backtest practice: transaction costs, drawdown, turnover and tail-risk penalties",
        ],
        "primary_reward": "OOS cost-adjusted Sortino on dollar-neutral cross-sectional portfolio returns",
        "secondary_rewards": [
            "OOS Sharpe",
            "OOS IC and RankIC",
            "May/stress Sortino",
            "max drawdown",
            "turnover",
            "capacity proxy from quote volume weighted by absolute portfolio weights",
            "control dominance penalty",
            "split stability",
            "family and skeleton diversity retained outside this per-candidate evaluator",
        ],
        "hard_rejects": [
            "non-finite or missing reward metrics",
            "recent_oos Sortino <= 0",
            "validation/test/recent OOS not all positive on net mean return",
            "control_ratio_recent >= 1.0",
            "ranked-label-only evidence without raw tradable PnL support",
            "missing transaction cost model",
            "turnover excessive relative to reward",
            "same-bar/future/leakage field violations upstream",
        ],
        "portfolio_construction": {
            "signal_to_weight": "cross-sectional percentile rank, demeaned to dollar neutral, normalized to gross 1 per timestamp",
            "orientation": "chosen on train_2024 net mean return only, then frozen for OOS/stress",
            "return_label": "raw forward log return for tradable PnL; other label families remain diagnostics",
            "rebalance": "hourly signal timestamps; non-overlap reward uses horizon-stride offsets",
            "transaction_cost": "one-way turnover * cost_bps / 10000",
        },
        "ranking_policy": "multi-objective gates and Pareto ranking define the primary leaderboard; the fixed-weight score is diagnostic only",
        "pareto_objectives": PARETO_OBJECTIVES,
        "diagnostic_composite_formula": {
            "recent_sortino": 0.35,
            "min_validation_test_recent_sortino": 0.20,
            "recent_sharpe": 0.15,
            "recent_rankic_times_20": 0.15,
            "may_stress_sortino": 0.05,
            "capacity_score": 0.05,
            "max_drawdown_penalty": -0.15,
            "turnover_penalty": -0.05,
            "control_penalty": -0.25,
        },
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }


def finite_corr(x: np.ndarray, y: np.ndarray) -> float:
    mask = np.isfinite(x) & np.isfinite(y)
    if int(mask.sum()) < 8:
        return np.nan
    xx = x[mask].astype(np.float64)
    yy = y[mask].astype(np.float64)
    sx = float(np.nanstd(xx))
    sy = float(np.nanstd(yy))
    if sx <= 1e-12 or sy <= 1e-12:
        return np.nan
    return float(np.corrcoef(xx, yy)[0, 1])


def rank_pct(values: np.ndarray) -> np.ndarray:
    return pd.DataFrame(values).rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)


def signal_to_weights(signal: np.ndarray, gross: float = 1.0, max_abs_weight: float = 0.03) -> np.ndarray:
    ranks = rank_pct(signal)
    centered = ranks - np.nanmean(ranks, axis=0, keepdims=True)
    centered[~np.isfinite(centered)] = 0.0
    denom = np.nansum(np.abs(centered), axis=0, keepdims=True)
    weights = np.divide(centered, denom, out=np.zeros_like(centered), where=denom > 1e-12) * gross
    weights = np.clip(weights, -max_abs_weight, max_abs_weight)
    denom2 = np.nansum(np.abs(weights), axis=0, keepdims=True)
    return np.divide(weights, denom2, out=np.zeros_like(weights), where=denom2 > 1e-12) * gross


def turnover_cost(weights: np.ndarray, cost_bps: float) -> np.ndarray:
    prev = np.zeros((weights.shape[0], 1), dtype=np.float64)
    delta = np.diff(np.concatenate([prev, weights], axis=1), axis=1)
    one_way_turnover = np.nansum(np.abs(delta), axis=0) / 2.0
    return one_way_turnover * cost_bps / 10000.0


def drawdown(returns: np.ndarray) -> float:
    x = returns[np.isfinite(returns)]
    if len(x) == 0:
        return np.nan
    equity = np.cumprod(1.0 + np.clip(x, -0.95, 10.0))
    peak = np.maximum.accumulate(equity)
    dd = equity / np.where(peak > 0, peak, np.nan) - 1.0
    return float(np.nanmin(dd)) if len(dd) else np.nan


def sharpe(returns: np.ndarray, periods_per_year: float) -> float:
    x = returns[np.isfinite(returns)]
    if len(x) < 8:
        return np.nan
    sd = float(np.nanstd(x, ddof=1))
    if sd <= 1e-12:
        return np.nan
    return float(np.nanmean(x) / sd * math.sqrt(periods_per_year))


def sortino(returns: np.ndarray, periods_per_year: float) -> float:
    x = returns[np.isfinite(returns)]
    if len(x) < 8:
        return np.nan
    downside = np.minimum(x, 0.0)
    ds = float(np.sqrt(np.nanmean(downside * downside)))
    if ds <= 1e-12:
        if float(np.nanmean(x)) > 0:
            return 50.0
        return np.nan
    return float(np.nanmean(x) / ds * math.sqrt(periods_per_year))


def nonoverlap_metric(values: np.ndarray, horizon: int, func) -> tuple[float, float]:
    stats: list[float] = []
    step = max(1, int(horizon))
    for offset in range(step):
        sub = values[offset::step]
        stat = func(sub)
        if np.isfinite(stat):
            stats.append(float(stat))
    if not stats:
        return np.nan, np.nan
    return float(np.nanmedian(stats)), float(np.nanmin(stats))


def split_metrics(
    candidate: dict[str, Any],
    horizon: int,
    variant: str,
    signal: np.ndarray,
    raw_label: np.ndarray,
    split: np.ndarray,
    quote_volume: np.ndarray,
    cost_bps: float,
    orientation: float,
) -> list[dict[str, Any]]:
    weights = signal_to_weights(signal * orientation)
    gross_forward = np.nansum(weights * raw_label, axis=0)
    cost = turnover_cost(weights, cost_bps)
    net = gross_forward - cost
    periods_per_year = 24.0 * 365.0 / max(1, horizon)
    rank_signal = rank_pct(signal * orientation)
    rank_label = rank_pct(raw_label)
    capacity_series = np.nansum(np.abs(weights) * quote_volume, axis=0)
    rows: list[dict[str, Any]] = []
    for split_name in ALL_EVAL_SPLITS:
        mask = split == split_name
        if not np.any(mask):
            continue
        ret = net[mask]
        cap = capacity_series[mask]
        sig_sub = rank_signal[:, mask]
        lab_sub = raw_label[:, mask]
        rank_lab_sub = rank_label[:, mask]
        ic_values = [finite_corr(sig_sub[:, i], lab_sub[:, i]) for i in range(sig_sub.shape[1])]
        rankic_values = [finite_corr(sig_sub[:, i], rank_lab_sub[:, i]) for i in range(sig_sub.shape[1])]
        no_sortino_median, no_sortino_floor = nonoverlap_metric(ret, horizon, lambda x: sortino(x, periods_per_year))
        no_sharpe_median, no_sharpe_floor = nonoverlap_metric(ret, horizon, lambda x: sharpe(x, periods_per_year))
        rows.append(
            {
                "blueprint_id": candidate.get("blueprint_id", ""),
                "semantic_pair": candidate.get("semantic_pair", ""),
                "motif": candidate.get("motif", ""),
                "skeleton_key": candidate.get("skeleton_key", ""),
                "expression": candidate.get("expression", ""),
                "horizon_h": horizon,
                "variant": variant,
                "split": split_name,
                "n_obs": int(np.isfinite(ret).sum()),
                "net_mean": float(np.nanmean(ret)) if np.isfinite(ret).any() else np.nan,
                "net_median": float(np.nanmedian(ret)) if np.isfinite(ret).any() else np.nan,
                "net_std": float(np.nanstd(ret, ddof=1)) if int(np.isfinite(ret).sum()) > 1 else np.nan,
                "sharpe": sharpe(ret, periods_per_year),
                "sortino": sortino(ret, periods_per_year),
                "nonoverlap_median_sortino": no_sortino_median,
                "nonoverlap_floor_sortino": no_sortino_floor,
                "nonoverlap_median_sharpe": no_sharpe_median,
                "nonoverlap_floor_sharpe": no_sharpe_floor,
                "max_drawdown": drawdown(ret),
                "positive_rate": float(np.nanmean(ret > 0)) if np.isfinite(ret).any() else np.nan,
                "avg_cost": float(np.nanmean(cost[mask])) if np.isfinite(cost[mask]).any() else np.nan,
                "avg_turnover": float(np.nanmean(cost[mask]) / (cost_bps / 10000.0)) if cost_bps > 0 and np.isfinite(cost[mask]).any() else np.nan,
                "ic_mean": float(np.nanmean(ic_values)) if np.isfinite(ic_values).any() else np.nan,
                "rankic_mean": float(np.nanmean(rankic_values)) if np.isfinite(rankic_values).any() else np.nan,
                "capacity_proxy_median_quote_volume": float(np.nanmedian(cap)) if np.isfinite(cap).any() else np.nan,
            }
        )
    return rows


def control_signal(signal: np.ndarray, variant: str, rng: np.random.Generator) -> np.ndarray:
    if variant == "one_bar_lag":
        return dense_shift_matrix(signal, 1)
    if variant == "stale_168h":
        return dense_shift_matrix(signal, 168)
    if variant == "sign_flip":
        return -signal
    if variant == "time_shuffle":
        return signal[:, rng.permutation(signal.shape[1])]
    if variant == "symbol_shuffle":
        return signal[rng.permutation(signal.shape[0]), :]
    raise ValueError(f"unknown control variant: {variant}")


def load_numeric_for_queue(queue: pd.DataFrame, hours_per_split: int) -> tuple[pd.DatetimeIndex, np.ndarray, dict[str, np.ndarray], dict[str, np.ndarray]]:
    requested = {"trade_close", "trade_quote_volume"}
    for expression in queue["expression"].dropna().astype(str):
        requested.update(expression_fields(expression))
    alias_upper_fields = {UPPER_ALIASES[field] for field in requested if field in UPPER_ALIASES}
    derived_fields = requested & set(DERIVED_DEPS)
    derived_deps = set().union(*(DERIVED_DEPS[field] for field in derived_fields)) if derived_fields else set()
    fields = (requested - set(UPPER_ALIASES) - derived_fields) | alias_upper_fields | derived_deps
    requested_dense_funding = fields & DENSE_FUNDING_FIELDS

    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    upper_schema = parquet_schema(UPPER_REGIME_PANEL)
    base_fields = {field for field in fields if field in base_schema}
    if requested_dense_funding:
        base_fields.add("funding_rate")
        if "funding_state_x_basis_delta" in requested_dense_funding:
            base_fields.add("mark_index_basis_bps")
    latent_fields = {field for field in fields if field in latent_schema and field not in base_fields}
    upper_fields = {field for field in fields if field in upper_schema and field not in base_fields and field not in latent_fields}
    missing = sorted(fields - base_fields - latent_fields - upper_fields - requested_dense_funding)
    if missing:
        raise RuntimeError(f"missing numeric fields for reward model: {missing[:20]}")

    symbols = strict_symbols()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_fields))
    numeric.update(load_upper_numeric(loaded_symbols, timestamps, upper_fields))
    for alias, source in UPPER_ALIASES.items():
        if alias in requested and source in numeric:
            numeric[alias] = numeric[source]
    if requested_dense_funding:
        raw_funding = numeric["funding_rate"]
        dense_funding, funding_age = dense_ffill_and_age(raw_funding, 8)
        numeric["funding_rate_state_last_ffill_8h"] = dense_funding
        numeric["funding_rate_update_age_hours"] = funding_age
        if "funding_rate_abs_state_168h_z" in requested_dense_funding:
            numeric["funding_rate_abs_state_168h_z"] = rolling_mean_std_z(np.abs(dense_funding), 168, 48)
        if "funding_rate_delta_state_24h" in requested_dense_funding or "funding_state_x_basis_delta" in requested_dense_funding:
            funding_delta_24h = dense_funding - dense_shift_matrix(dense_funding, 24)
            numeric["funding_rate_delta_state_24h"] = funding_delta_24h
        if "funding_state_x_basis_delta" in requested_dense_funding:
            basis = numeric["mark_index_basis_bps"]
            numeric["funding_state_x_basis_delta"] = funding_delta_24h * (basis - dense_shift_matrix(basis, 24))
    if "open_interest_value_change_24h" in derived_fields:
        numeric["open_interest_value_change_24h"] = numeric["open_interest_value_last"] - dense_shift_matrix(numeric["open_interest_value_last"], 24)
    if "funding_rate_persistence_24h" in derived_fields:
        from scripts.crypto_a7al2x5_evaluator_preflight_smoke import rolling_mean  # noqa: E402

        numeric["funding_rate_persistence_24h"] = rolling_mean(numeric["funding_rate"], 24)
    if "premium_abs_state" in derived_fields:
        numeric["premium_abs_state"] = np.abs(numeric["premium_close_bps"])
    if "quote_volume_z_168h" in derived_fields:
        numeric["quote_volume_z_168h"] = rolling_mean_std_z(numeric["trade_quote_volume"], 168, 48)
    if "account_position_divergence" in derived_fields:
        numeric["account_position_divergence"] = numeric["top_long_short_position_ratio_last"] - numeric["top_long_short_account_ratio_last"]
    if "top_global_account_divergence" in derived_fields:
        numeric["top_global_account_divergence"] = numeric["top_long_short_account_ratio_last"] - numeric["global_long_short_account_ratio_last"]

    groups = load_group_fields(loaded_symbols, timestamps, {"liquidity_tier"})
    idx = selected_column_indices(timestamps, hours_per_split)
    timestamps = pd.DatetimeIndex(timestamps[idx])
    numeric = {key: value[:, idx] for key, value in numeric.items()}
    groups = {key: value[:, idx] for key, value in groups.items()}
    split = split_for_timestamps(timestamps)
    return timestamps, split, numeric, groups


def evaluate_queue(
    queue: pd.DataFrame,
    hours_per_split: int,
    cost_bps: float,
    candidate_cap: int,
    checkpoint_dir: Path | None = None,
    checkpoint_every: int = 0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if candidate_cap > 0:
        queue = queue.head(candidate_cap).copy()
    timestamps, split, numeric, groups = load_numeric_for_queue(queue, hours_per_split)
    evaluator = A7AB4Evaluator(numeric, groups)
    raw_labels = {h: horizon_label(numeric["trade_close"], timestamps, split, h) for h in HORIZONS}
    quote_volume = numeric["trade_quote_volume"]
    rng = np.random.default_rng(20260610)
    metric_rows: list[dict[str, Any]] = []
    error_rows: list[dict[str, Any]] = []
    total_rows = len(queue)
    for idx_row, row in enumerate(queue.to_dict("records"), start=1):
        cid = str(row.get("blueprint_id", f"row_{idx_row}"))
        print(f"[A7REWARD1] evaluating {idx_row}/{total_rows} {cid}", flush=True)
        try:
            signal = evaluator.eval(str(row["expression"]))
            # Orientation is chosen on train only for each horizon, then frozen.
            for horizon in HORIZONS:
                train_rows_pos = split_metrics(row, horizon, "orientation_probe", signal, raw_labels[horizon], split, quote_volume, cost_bps, 1.0)
                train_pos = next((x for x in train_rows_pos if x["split"] == "train_2024"), {})
                train_rows_neg = split_metrics(row, horizon, "orientation_probe", signal, raw_labels[horizon], split, quote_volume, cost_bps, -1.0)
                train_neg = next((x for x in train_rows_neg if x["split"] == "train_2024"), {})
                orientation = 1.0 if float(train_pos.get("net_mean", np.nan)) >= float(train_neg.get("net_mean", np.nan)) else -1.0
                metric_rows.extend(split_metrics(row, horizon, "original", signal, raw_labels[horizon], split, quote_volume, cost_bps, orientation))
                for variant in CONTROL_VARIANTS:
                    ctrl = control_signal(signal, variant, rng)
                    metric_rows.extend(split_metrics(row, horizon, variant, ctrl, raw_labels[horizon], split, quote_volume, cost_bps, orientation))
        except Exception as exc:  # keep the reward audit fail-open as data, not as silent loss
            error_rows.append({"blueprint_id": cid, "error": repr(exc), "expression": row.get("expression", "")})
        if checkpoint_dir is not None and checkpoint_every > 0 and (idx_row % checkpoint_every == 0 or idx_row == total_rows):
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            partial_metrics = pd.DataFrame(metric_rows)
            partial_errors = pd.DataFrame(error_rows)
            partial_rewards = aggregate_rewards(partial_metrics)
            partial_metrics.to_csv(checkpoint_dir / "a7reward1_checkpoint_split_reward_metrics.csv", index=False)
            partial_errors.to_csv(checkpoint_dir / "a7reward1_checkpoint_eval_errors.csv", index=False)
            partial_rewards.to_csv(checkpoint_dir / "a7reward1_checkpoint_candidate_reward_leaderboard.csv", index=False)
            write_json(
                checkpoint_dir / "a7reward1_checkpoint_status.json",
                {
                    "generated_at": now_utc(),
                    "completed_candidates": int(idx_row),
                    "total_candidates": int(total_rows),
                    "metric_rows": int(partial_metrics.shape[0]),
                    "reward_rows": int(partial_rewards.shape[0]),
                    "error_rows": int(partial_errors.shape[0]),
                    "top_gate_blueprint_id": str(partial_rewards.iloc[0]["blueprint_id"]) if not partial_rewards.empty else "",
                    "top_diagnostic_composite_score": float(partial_rewards.iloc[0]["diagnostic_composite_score"]) if not partial_rewards.empty else np.nan,
                    "ranking_policy": "gate_pass_then_pareto_rank; diagnostic_composite_score_is_tiebreaker_only",
                },
            )
    return pd.DataFrame(metric_rows), pd.DataFrame(error_rows)


def aggregate_rewards(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return pd.DataFrame()
    original = metrics[metrics["variant"].eq("original")].copy()
    controls = (
        metrics[~metrics["variant"].eq("original")]
        .groupby(["blueprint_id", "horizon_h", "split"], as_index=False)
        .agg(max_abs_control_net_mean=("net_mean", lambda s: float(np.nanmax(np.abs(s))) if len(s) else np.nan))
    )
    shuffle_controls = (
        metrics[metrics["variant"].isin(["time_shuffle", "symbol_shuffle"])]
        .groupby(["blueprint_id", "horizon_h", "split"], as_index=False)
        .agg(max_abs_shuffle_control_net_mean=("net_mean", lambda s: float(np.nanmax(np.abs(s))) if len(s) else np.nan))
    )
    original = original.merge(controls, on=["blueprint_id", "horizon_h", "split"], how="left")
    original = original.merge(shuffle_controls, on=["blueprint_id", "horizon_h", "split"], how="left")
    original["control_ratio"] = original["max_abs_control_net_mean"].abs() / (original["net_mean"].abs() + 1e-12)
    original["shuffle_control_ratio"] = original["max_abs_shuffle_control_net_mean"].abs() / (original["net_mean"].abs() + 1e-12)
    rows: list[dict[str, Any]] = []
    for (cid, horizon), group in original.groupby(["blueprint_id", "horizon_h"], sort=False):
        by_split = {str(r["split"]): r for r in group.to_dict("records")}
        train = by_split.get("train_2024", {})
        validation = by_split.get("validation_2025H1", {})
        test = by_split.get("test_2025H2", {})
        recent = by_split.get("recent_oos_2026JanApr", {})
        stress = by_split.get("known_may2026_stress", {})
        sortinos = [
            float(validation.get("nonoverlap_median_sortino", np.nan)),
            float(test.get("nonoverlap_median_sortino", np.nan)),
            float(recent.get("nonoverlap_median_sortino", np.nan)),
        ]
        floor_sortinos = [
            float(validation.get("nonoverlap_floor_sortino", np.nan)),
            float(test.get("nonoverlap_floor_sortino", np.nan)),
            float(recent.get("nonoverlap_floor_sortino", np.nan)),
        ]
        oos_positive = [
            float(validation.get("net_mean", np.nan)) > 0,
            float(test.get("net_mean", np.nan)) > 0,
            float(recent.get("net_mean", np.nan)) > 0,
        ]
        recent_control = float(recent.get("control_ratio", np.nan))
        recent_shuffle_control = float(recent.get("shuffle_control_ratio", np.nan))
        capacity = float(recent.get("capacity_proxy_median_quote_volume", np.nan))
        capacity_score = math.log10(max(capacity, 1.0)) / 10.0 if np.isfinite(capacity) else 0.0
        turnover_penalty = max(0.0, float(recent.get("avg_turnover", 0.0)) - 0.75)
        dd_penalty = abs(min(float(recent.get("max_drawdown", 0.0)), 0.0))
        control_penalty = max(0.0, recent_shuffle_control - 0.8) if np.isfinite(recent_shuffle_control) else 1.0
        diagnostic_composite = (
            0.35 * float(recent.get("nonoverlap_median_sortino", np.nan))
            + 0.20 * float(np.nanmin(sortinos))
            + 0.15 * float(recent.get("nonoverlap_median_sharpe", np.nan))
            + 0.15 * float(recent.get("rankic_mean", np.nan)) * 20.0
            + 0.05 * float(stress.get("nonoverlap_median_sortino", 0.0) if np.isfinite(float(stress.get("nonoverlap_median_sortino", np.nan))) else 0.0)
            + 0.05 * capacity_score
            - 0.15 * dd_penalty
            - 0.05 * turnover_penalty
            - 0.25 * control_penalty
        )
        sample = group.iloc[0].to_dict()
        hard_reject_reasons = []
        if not np.isfinite(diagnostic_composite):
            hard_reject_reasons.append("non_finite_diagnostic_composite")
        if not (float(recent.get("nonoverlap_median_sortino", np.nan)) > 0):
            hard_reject_reasons.append("recent_sortino_non_positive")
        if not (float(train.get("net_mean", np.nan)) > 0):
            hard_reject_reasons.append("train_orientation_no_positive_edge")
        if not all(np.isfinite(value) and value > 0 for value in floor_sortinos):
            hard_reject_reasons.append("oos_nonoverlap_floor_not_positive")
        if not all(oos_positive):
            hard_reject_reasons.append("oos_net_mean_not_all_positive")
        if not np.isfinite(recent_shuffle_control):
            hard_reject_reasons.append("missing_shuffle_control_metrics")
        elif recent_shuffle_control >= 1.0:
            hard_reject_reasons.append("shuffle_control_dominated_recent")
        if float(recent.get("n_obs", 0)) < 100:
            hard_reject_reasons.append("recent_sample_too_small")
        rows.append(
            {
                "blueprint_id": cid,
                "semantic_pair": sample.get("semantic_pair", ""),
                "motif": sample.get("motif", ""),
                "skeleton_key": sample.get("skeleton_key", ""),
                "expression": sample.get("expression", ""),
                "horizon_h": int(horizon),
                "diagnostic_composite_score": diagnostic_composite,
                "overall_reward": diagnostic_composite,
                "train_sortino": train.get("nonoverlap_median_sortino", np.nan),
                "validation_sortino": validation.get("nonoverlap_median_sortino", np.nan),
                "test_sortino": test.get("nonoverlap_median_sortino", np.nan),
                "recent_sortino": recent.get("nonoverlap_median_sortino", np.nan),
                "validation_floor_sortino": validation.get("nonoverlap_floor_sortino", np.nan),
                "test_floor_sortino": test.get("nonoverlap_floor_sortino", np.nan),
                "recent_floor_sortino": recent.get("nonoverlap_floor_sortino", np.nan),
                "stress_sortino": stress.get("nonoverlap_median_sortino", np.nan),
                "stress_floor_sortino": stress.get("nonoverlap_floor_sortino", np.nan),
                "recent_sharpe": recent.get("nonoverlap_median_sharpe", np.nan),
                "recent_ic": recent.get("ic_mean", np.nan),
                "recent_rankic": recent.get("rankic_mean", np.nan),
                "recent_net_mean": recent.get("net_mean", np.nan),
                "recent_max_drawdown": recent.get("max_drawdown", np.nan),
                "recent_avg_turnover": recent.get("avg_turnover", np.nan),
                "recent_capacity_proxy": recent.get("capacity_proxy_median_quote_volume", np.nan),
                "recent_control_ratio": recent_control,
                "recent_shuffle_control_ratio": recent_shuffle_control,
                "oos_positive_split_count": int(sum(oos_positive)),
                "hard_reject": bool(hard_reject_reasons),
                "hard_reject_reasons": ";".join(hard_reject_reasons),
            }
        )
    out = pd.DataFrame(rows)
    out = add_pareto_columns(out)
    return out.sort_values(
        [
            "gate_pass",
            "pareto_rank",
            "objective_pass_count",
            "recent_sortino",
            "min_oos_sortino",
            "recent_shuffle_control_ratio",
            "diagnostic_composite_score",
        ],
        ascending=[False, True, False, False, False, True, False],
    )


def run_synthetic_smoke() -> pd.DataFrame:
    rng = np.random.default_rng(20260610)
    n_assets, n_times = 64, 1200
    split = np.array(["train_2024"] * 300 + ["validation_2025H1"] * 300 + ["test_2025H2"] * 300 + ["recent_oos_2026JanApr"] * 240 + ["known_may2026_stress"] * 60, dtype=object)
    true_signal = rng.normal(size=(n_assets, n_times))
    label = 0.002 * true_signal + rng.normal(scale=0.01, size=(n_assets, n_times))
    quote_volume = np.exp(rng.normal(12.0, 0.8, size=(n_assets, n_times)))
    train_mask = split == "train_2024"
    validation_mask = split == "validation_2025H1"
    test_mask = split == "test_2025H2"
    recent_mask = split == "recent_oos_2026JanApr"
    train_only_overfit = rng.normal(size=(n_assets, n_times))
    train_only_overfit[:, train_mask] = true_signal[:, train_mask]
    train_only_overfit[:, validation_mask | test_mask | recent_mask] = -true_signal[:, validation_mask | test_mask | recent_mask]
    recent_only_overfit = rng.normal(size=(n_assets, n_times))
    recent_only_overfit[:, recent_mask] = true_signal[:, recent_mask]
    recent_only_overfit[:, validation_mask | test_mask] = -true_signal[:, validation_mask | test_mask]
    fast_flip = true_signal * np.where(np.arange(n_times) % 2 == 0, 1.0, -1.0)
    candidates = [
        ("synthetic_true_positive", true_signal, True, "stable_signal"),
        ("synthetic_orientation_equivalent", -true_signal, True, "orientation_equivalent"),
        ("synthetic_train_only_overfit", train_only_overfit, False, "train_only_overfit"),
        ("synthetic_recent_only_overfit", recent_only_overfit, False, "recent_only_overfit"),
        ("synthetic_high_turnover_trap", fast_flip, False, "cost_turnover_trap"),
        ("synthetic_shuffle_noise", rng.normal(size=(n_assets, n_times)), False, "shuffle_noise"),
    ]
    rows = []
    expectations: dict[str, tuple[bool, str]] = {}
    for cid, signal, expected_gate_pass, adversarial_case in candidates:
        expectations[cid] = (expected_gate_pass, adversarial_case)
        candidate = {
            "blueprint_id": cid,
            "semantic_pair": "synthetic",
            "motif": "smoke",
            "skeleton_key": cid,
            "expression": cid,
        }
        train_pos = split_metrics(candidate, 24, "orientation_probe", signal, label, split, quote_volume, 5.0, 1.0)
        train_neg = split_metrics(candidate, 24, "orientation_probe", signal, label, split, quote_volume, 5.0, -1.0)
        orientation = 1.0 if train_pos[0]["net_mean"] >= train_neg[0]["net_mean"] else -1.0
        rows.extend(split_metrics(candidate, 24, "original", signal, label, split, quote_volume, 5.0, orientation))
        for variant in CONTROL_VARIANTS:
            rows.extend(
                split_metrics(
                    candidate,
                    24,
                    variant,
                    control_signal(signal, variant, rng),
                    label,
                    split,
                    quote_volume,
                    5.0,
                    orientation,
                )
            )
    metrics = pd.DataFrame(rows)
    rewards = aggregate_rewards(metrics)
    rewards["smoke_expected_gate_pass"] = rewards["blueprint_id"].map(lambda value: expectations.get(value, (False, ""))[0])
    rewards["smoke_adversarial_case"] = rewards["blueprint_id"].map(lambda value: expectations.get(value, (False, ""))[1])
    rewards["smoke_case_pass"] = np.where(
        rewards["smoke_expected_gate_pass"],
        rewards["gate_pass"] & ~rewards["hard_reject"],
        ~rewards["gate_pass"] & rewards["hard_reject"],
    )
    return rewards


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE))
    parser.add_argument("--candidate-cap", type=int, default=int(os.environ.get("A7REWARD_CANDIDATE_CAP", "80")))
    parser.add_argument("--hours-per-split", type=int, default=int(os.environ.get("A7REWARD_HOURS_PER_SPLIT", "720")))
    parser.add_argument("--cost-bps", type=float, default=float(os.environ.get("A7REWARD_COST_BPS", "5.0")))
    parser.add_argument("--smoke-only", action="store_true")
    parser.add_argument("--runtime", default=str(RUNTIME))
    parser.add_argument("--report", default=str(REPORT))
    parser.add_argument("--checkpoint-every", type=int, default=int(os.environ.get("A7REWARD_CHECKPOINT_EVERY", "8")))
    args = parser.parse_args()

    runtime = Path(args.runtime)
    report_path = Path(args.report)
    runtime.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    contract = contract_payload()
    write_json(runtime / "a7reward1_reward_contract.json", contract)

    smoke = run_synthetic_smoke()
    smoke.to_csv(runtime / "a7reward1_synthetic_smoke_leaderboard.csv", index=False)
    smoke_pass = (
        not smoke.empty
        and bool(smoke["smoke_case_pass"].all())
        and smoke[smoke["blueprint_id"].eq("synthetic_true_positive")]["gate_pass"].eq(True).all()
        and smoke[smoke["blueprint_id"].eq("synthetic_shuffle_noise")]["hard_reject"].eq(True).all()
    )
    if args.smoke_only:
        decision = "PASS_A7REWARD1_SYNTHETIC_SMOKE" if smoke_pass else "HOLD_A7REWARD1_SYNTHETIC_SMOKE_FAIL"
        manifest = {
            "stage": "A7REWARD-1-SMOKE",
            "generated_at": now_utc(),
            "decision": decision,
            "synthetic_smoke_pass": bool(smoke_pass),
            "authorizes_alpha_proof": False,
            "authorizes_shadow_paper_live": False,
        }
        write_json(runtime / "a7reward1_manifest.json", manifest)
        report_path.write_text(
            "\n".join(
                [
                    "# CRYPTO A7REWARD1 Synthetic Reward Smoke",
                    "",
                    f"Generated: {manifest['generated_at']}",
                    "",
                    "## Decision",
                    "",
                    f"`{decision}`",
                    "",
                    "## Synthetic Smoke Leaderboard",
                    "",
                    md_table(smoke, 20),
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return

    queue_path = Path(args.queue)
    queue = read_csv(queue_path)
    if queue.empty:
        raise SystemExit(f"empty reward queue: {queue_path}")
    metrics, errors = evaluate_queue(
        queue,
        args.hours_per_split,
        args.cost_bps,
        args.candidate_cap,
        checkpoint_dir=runtime,
        checkpoint_every=args.checkpoint_every,
    )
    rewards = aggregate_rewards(metrics)
    metrics.to_csv(runtime / "a7reward1_split_reward_metrics.csv", index=False)
    errors.to_csv(runtime / "a7reward1_eval_errors.csv", index=False)
    rewards.to_csv(runtime / "a7reward1_candidate_reward_leaderboard.csv", index=False)

    best_by_pareto = rewards.sort_values(["gate_pass", "pareto_rank", "objective_pass_count"], ascending=[False, True, False]).head(80)
    best_by_sortino = rewards.sort_values(["hard_reject", "recent_sortino"], ascending=[True, False]).head(40)
    best_by_sharpe = rewards.sort_values(["hard_reject", "recent_sharpe"], ascending=[True, False]).head(40)
    best_by_ic = rewards.sort_values(["hard_reject", "recent_rankic"], ascending=[True, False]).head(40)
    diagnostic_composite = rewards.sort_values(["hard_reject", "diagnostic_composite_score"], ascending=[True, False]).head(80)
    top_queue = best_by_pareto
    best_overall = diagnostic_composite
    best_by_pareto.to_csv(runtime / "a7reward1_pareto_leaderboard.csv", index=False)
    best_by_sortino.to_csv(runtime / "a7reward1_best_by_sortino.csv", index=False)
    best_by_sharpe.to_csv(runtime / "a7reward1_best_by_sharpe.csv", index=False)
    best_by_ic.to_csv(runtime / "a7reward1_best_by_rankic.csv", index=False)
    diagnostic_composite.to_csv(runtime / "a7reward1_diagnostic_composite_leaderboard.csv", index=False)

    valid = rewards[~rewards["hard_reject"]].copy()
    decision = (
        "PASS_A7REWARD1_PORTFOLIO_REWARD_LEADERBOARD_BUILT"
        if smoke_pass and not valid.empty
        else "HOLD_A7REWARD1_REWARD_MODEL_OR_QUEUE_FAILED"
    )
    manifest = {
        "stage": "A7REWARD-1",
        "generated_at": now_utc(),
        "decision": decision,
        "queue_path": str(queue_path),
        "queue_rows": int(queue.shape[0]),
        "candidate_cap": int(args.candidate_cap),
        "hours_per_split": int(args.hours_per_split),
        "cost_bps": float(args.cost_bps),
        "split_metric_rows": int(metrics.shape[0]),
        "reward_rows": int(rewards.shape[0]),
        "hard_reject_rows": int(rewards["hard_reject"].sum()) if not rewards.empty else 0,
        "valid_reward_rows": int((~rewards["hard_reject"]).sum()) if not rewards.empty else 0,
        "eval_error_rows": int(errors.shape[0]),
        "synthetic_smoke_pass": bool(smoke_pass),
        "top_pareto_blueprint_id": str(top_queue.iloc[0]["blueprint_id"]) if not top_queue.empty else "",
        "top_pareto_rank": int(top_queue.iloc[0]["pareto_rank"]) if not top_queue.empty else 0,
        "top_pareto_objective_pass_count": int(top_queue.iloc[0]["objective_pass_count"]) if not top_queue.empty else 0,
        "top_diagnostic_composite_blueprint_id": str(diagnostic_composite.iloc[0]["blueprint_id"]) if not diagnostic_composite.empty else "",
        "top_diagnostic_composite_score": float(diagnostic_composite.iloc[0]["diagnostic_composite_score"]) if not diagnostic_composite.empty else np.nan,
        "ranking_policy": "multi_objective_gate_and_pareto; diagnostic_composite_score_is_not_a_search_reward",
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_required": [
            "run full A7REWARD on company machine for selected queues",
            "wire A7REWARD leaderboard into A7RAW/A7LS shard outputs",
            "replace numeric-proxy best with multi-objective Pareto reward views in source-of-truth registry",
        ],
    }
    write_json(runtime / "a7reward1_manifest.json", manifest)

    report = [
        "# CRYPTO A7REWARD1 Portfolio Reward Model",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7REWARD1 establishes portfolio-level evaluation for crypto alpha search. Numeric clue scores remain diagnostic. Candidate acceptance is now gated by OOS/stress/control metrics and Pareto rank; the fixed diagnostic composite is not a search reward.",
        "",
        "## Reward Contract",
        "",
        "Primary ranking uses multi-objective gates and Pareto rank over OOS cost-adjusted Sortino, OOS stability, Sharpe, IC/RankIC, drawdown, turnover, stress survival, and control dominance. The fixed diagnostic composite is retained only as a compatibility/tie-breaker column.",
        "",
        "## Counts",
        "",
        f"- queue_rows: `{manifest['queue_rows']}`",
        f"- candidate_cap: `{manifest['candidate_cap']}`",
        f"- hours_per_split: `{manifest['hours_per_split']}`",
        f"- cost_bps: `{manifest['cost_bps']}`",
        f"- reward_rows: `{manifest['reward_rows']}`",
        f"- valid_reward_rows: `{manifest['valid_reward_rows']}`",
        f"- hard_reject_rows: `{manifest['hard_reject_rows']}`",
        f"- eval_error_rows: `{manifest['eval_error_rows']}`",
        f"- synthetic_smoke_pass: `{manifest['synthetic_smoke_pass']}`",
        "",
        "## Synthetic Smoke Leaderboard",
        "",
        md_table(smoke, 20),
        "",
        "## Pareto Leaderboard",
        "",
        md_table(best_by_pareto, 40),
        "",
        "## Diagnostic Composite Leaderboard",
        "",
        md_table(diagnostic_composite, 30),
        "",
        "## Best By Sortino",
        "",
        md_table(best_by_sortino, 30),
        "",
        "## Boundary",
        "",
        "This is a research reward layer, not alpha proof. It does not authorize shadow, paper, or live execution.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
