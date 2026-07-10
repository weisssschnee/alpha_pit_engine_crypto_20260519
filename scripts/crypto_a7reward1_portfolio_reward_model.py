from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import gc
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    import bottleneck as bn
except Exception:  # pragma: no cover - optional acceleration dependency.
    bn = None


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
from alphafactory_crypto.engines.semantic_domains import collect_operator_calls  # noqa: E402


DEFAULT_QUEUE = REPO / "runtime" / "a7ls30_productive_numeric_acceptance_20260610" / "a7ls30_selected_top240.csv"
RUNTIME = REPO / "runtime" / "a7reward1_portfolio_reward_model_20260610"
REPORT = REPO / "reports" / "CRYPTO_A7REWARD1_PORTFOLIO_REWARD_MODEL_20260610.md"
DEFAULT_SOURCE_POLICY = (
    REPO
    / "runtime"
    / "a7source3_publication_semantics_research_20260703"
    / "a7source3_field_policy_recommendation.json"
)
DEFAULT_SOURCE_LAG_SUMMARY = (
    REPO
    / "runtime"
    / "a7source4_batch_source_lag_retest_20260703"
    / "a7source4_source_lag_summary.csv"
)

FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
HORIZONS = [1, 4, 8, 24]
PREMAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
ALL_EVAL_SPLITS = ["train_2024", *PREMAY_SPLITS, "known_may2026_stress"]
ORIENTATION_SPLIT = "orientation_contiguous_extension_train"
CONTROL_VARIANTS = ["one_bar_lag", "stale_168h", "sign_flip", "time_shuffle", "symbol_shuffle"]
CONTROL_DOMINANCE_VARIANTS = ["one_bar_lag", "stale_168h", "time_shuffle", "symbol_shuffle"]
LAG_STALE_VARIANTS = ["one_bar_lag", "stale_168h"]
SHUFFLE_VARIANTS = ["time_shuffle", "symbol_shuffle"]
PARETO_OBJECTIVES = [
    "obj_train_sortino",
    "obj_train_oos_consistency",
    "obj_recent_sortino",
    "obj_min_oos_sortino",
    "obj_min_oos_floor_sortino",
    "obj_recent_sharpe",
    "obj_recent_rankic",
    "obj_stress_sortino",
    "obj_neg_recent_drawdown",
    "obj_neg_recent_turnover",
    "obj_neg_shuffle_control_ratio",
    "obj_neg_oos_control_dominated_count",
    "obj_neg_oos_lag_stale_dominated_count",
]
COMPUTED_UNIVERSE_STATE_FIELDS = {"active_universe_size"}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


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
    oos_sortino_frame = out[["validation_sortino", "test_sortino", "recent_sortino"]].apply(pd.to_numeric, errors="coerce")
    out["median_oos_sortino"] = oos_sortino_frame.median(axis=1)
    out["train_oos_sortino_gap"] = (
        pd.to_numeric(out["train_sortino"], errors="coerce") - out["median_oos_sortino"]
    ).abs()
    out["train_oos_consistency_score"] = -out["train_oos_sortino_gap"]
    if {"validation_floor_sortino", "test_floor_sortino", "recent_floor_sortino"}.issubset(out.columns):
        out["min_oos_floor_sortino"] = out[["validation_floor_sortino", "test_floor_sortino", "recent_floor_sortino"]].min(axis=1)
    else:
        out["min_oos_floor_sortino"] = np.nan
    out["obj_train_sortino"] = pd.to_numeric(out["train_sortino"], errors="coerce")
    out["obj_train_oos_consistency"] = pd.to_numeric(out["train_oos_consistency_score"], errors="coerce")
    out["obj_recent_sortino"] = pd.to_numeric(out["recent_sortino"], errors="coerce")
    out["obj_min_oos_sortino"] = pd.to_numeric(out["min_oos_sortino"], errors="coerce")
    out["obj_min_oos_floor_sortino"] = pd.to_numeric(out["min_oos_floor_sortino"], errors="coerce")
    out["obj_recent_sharpe"] = pd.to_numeric(out["recent_sharpe"], errors="coerce")
    out["obj_recent_rankic"] = pd.to_numeric(out["recent_rankic"], errors="coerce")
    out["obj_stress_sortino"] = pd.to_numeric(out["stress_sortino"], errors="coerce").fillna(-1e9)
    out["obj_neg_recent_drawdown"] = -pd.to_numeric(out["recent_max_drawdown"], errors="coerce").abs()
    out["obj_neg_recent_turnover"] = -pd.to_numeric(out["recent_avg_turnover"], errors="coerce")
    out["obj_neg_shuffle_control_ratio"] = -pd.to_numeric(out["recent_shuffle_control_ratio"], errors="coerce")
    out["obj_neg_oos_control_dominated_count"] = -pd.to_numeric(
        out.get("oos_control_dominated_count", 99), errors="coerce"
    )
    out["obj_neg_oos_lag_stale_dominated_count"] = -pd.to_numeric(
        out.get("oos_lag_stale_dominated_count", 99), errors="coerce"
    )
    stress_obs = pd.to_numeric(out.get("stress_n_obs", pd.Series(0, index=out.index)), errors="coerce").fillna(0) > 0
    stress_floor = pd.to_numeric(out.get("stress_floor_sortino", pd.Series(np.nan, index=out.index)), errors="coerce")
    stress_floor_clean = (~stress_obs) | (stress_floor > 0)

    objective_passes = pd.DataFrame(
        {
            "recent_sortino_positive": out["recent_sortino"] > 0,
            "train_sortino_positive": out["train_sortino"] > 0,
            "train_oos_consistency_reasonable": out["train_oos_sortino_gap"] <= 6.0,
            "min_oos_sortino_positive": out["min_oos_sortino"] > 0,
            "min_oos_floor_sortino_positive": out["min_oos_floor_sortino"] > 0,
            "recent_sharpe_positive": out["recent_sharpe"] > 0,
            "recent_rankic_positive": out["recent_rankic"] > 0,
            "stress_sortino_positive": out["stress_sortino"] > 0,
            "stress_floor_clean": stress_floor_clean,
            "shuffle_control_not_dominant": out["recent_shuffle_control_ratio"] < 1.0,
            "oos_control_not_dominant": out.get("oos_control_dominated_count", pd.Series(99, index=out.index)).eq(0),
            "oos_lag_stale_not_dominant": out.get("oos_lag_stale_dominated_count", pd.Series(99, index=out.index)).eq(0),
            "net_mean_oos_all_positive": out["oos_positive_split_count"] >= 3,
        }
    )
    out["objective_pass_count"] = objective_passes.sum(axis=1).astype(int)
    out["gate_pass"] = (
        (~out["hard_reject"])
        & (out["min_oos_sortino"] > 0)
        & (out["min_oos_floor_sortino"] > 0)
        & stress_floor_clean
        & (out["recent_shuffle_control_ratio"] < 1.0)
        & out.get("oos_control_dominated_count", pd.Series(99, index=out.index)).eq(0)
        & out.get("oos_lag_stale_dominated_count", pd.Series(99, index=out.index)).eq(0)
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


def accepted_for_next_search(rewards: pd.DataFrame) -> pd.DataFrame:
    if rewards.empty:
        return rewards.copy()
    accepted = rewards[(rewards["gate_pass"].astype(bool)) & (~rewards["hard_reject"].astype(bool))].copy()
    if accepted.empty:
        return accepted
    return accepted.sort_values(
        [
            "pareto_rank",
            "objective_pass_count",
            "min_oos_floor_sortino",
            "min_oos_sortino",
            "oos_control_dominated_count",
            "oos_lag_stale_dominated_count",
            "recent_shuffle_control_ratio",
            "recent_sortino",
        ],
        ascending=[True, False, False, False, True, True, True, False],
    )


def compact_expr(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or ""))


def load_source_policy(path: Path) -> dict[str, dict[str, Any]]:
    payload = read_json(path)
    policy: dict[str, dict[str, Any]] = {}
    for family, spec in payload.get("field_family_policy", {}).items():
        status = str(spec.get("status", ""))
        for field in spec.get("fields", []):
            policy[str(field)] = {
                "field_family": family,
                "status": status,
                "required_gate": str(spec.get("required_gate", "")),
            }
    return policy


def load_source_lag_passes(path: Path) -> tuple[set[str], set[str]]:
    summary = read_csv(path)
    if summary.empty or "source_lag_gate" not in summary:
        return set(), set()
    passed = summary[summary["source_lag_gate"].astype(str).eq("PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC")].copy()
    ids: set[str] = set()
    formulas: set[str] = set()
    for _, row in passed.iterrows():
        horizon = str(row.get("horizon_h", "") or "")
        for col in ["source_blueprint_id", "blueprint_id"]:
            value = str(row.get(col, "") or "")
            if value:
                ids.add(f"{value}|{horizon}")
        formulas.add(f"{compact_expr(row.get('formula', ''))}|{horizon}")
    return ids, formulas


def source_policy_for_field(field: str, source_policy: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    if field in source_policy:
        return source_policy[field]
    if "open_interest" in field:
        return {
            "field_family": "open_interest",
            "status": "SOURCE_LAG_REQUIRED",
            "required_gate": "source_lag_1h_and_2h_survival_or_publication_time_proof",
        }
    if "funding" in field:
        return {
            "field_family": "funding_state",
            "status": "EVENT_PUBLICATION_REQUIRED_OR_SOURCE_LAG_REQUIRED",
            "required_gate": "funding_event_publication_time_or_source_lag_survival",
        }
    if "long_short" in field or "position" in field:
        return {
            "field_family": "positioning",
            "status": "SOURCE_LAG_REQUIRED",
            "required_gate": "source_lag_1h_and_2h_survival",
        }
    if "stress_proxy" in field or "regime" in field:
        return {
            "field_family": "regime_state",
            "status": "THRESHOLD_LINEAGE_REQUIRED",
            "required_gate": "threshold_lineage_and_non_empty_response",
        }
    return None


def append_reject_reason(existing: Any, reason: str) -> str:
    parts = [part for part in str(existing or "").split(";") if part]
    if reason not in parts:
        parts.append(reason)
    return ";".join(parts)


def apply_source_lag_policy(rewards: pd.DataFrame, source_policy: dict[str, dict[str, Any]], source_lag_pass_ids: set[str], source_lag_pass_formulas: set[str]) -> pd.DataFrame:
    if rewards.empty or not source_policy:
        return rewards.copy()
    out = rewards.copy()
    source_statuses: list[str] = []
    required_fields_values: list[str] = []
    required_family_values: list[str] = []
    source_lag_gates: list[str] = []
    rejects: list[bool] = []

    for idx, row in out.iterrows():
        formula = str(row.get("expression", "") or "")
        fields = expression_fields(formula)
        required_fields: list[str] = []
        required_families: list[str] = []
        fragile_fields: list[str] = []
        for field in fields:
            spec = source_policy_for_field(field, source_policy)
            if not spec:
                continue
            status = str(spec.get("status", ""))
            family = str(spec.get("field_family", ""))
            if "SOURCE_LAG_REQUIRED" in status or "EVENT_PUBLICATION_REQUIRED" in status:
                required_fields.append(field)
                required_families.append(family)
            if "FRAGILE" in status:
                fragile_fields.append(field)

        blueprint_id = str(row.get("blueprint_id", "") or "")
        horizon = str(row.get("horizon_h", "") or "")
        formula_key = compact_expr(formula)
        has_pass = f"{blueprint_id}|{horizon}" in source_lag_pass_ids or f"{formula_key}|{horizon}" in source_lag_pass_formulas
        reject = bool(required_fields) and not has_pass
        if fragile_fields and not has_pass:
            reject = True

        if required_fields and has_pass:
            gate = "PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC"
            status_value = "SOURCE_LAG_REQUIRED_PASS"
        elif required_fields:
            gate = "HOLD_SOURCE_LAG_REQUIRED_NOT_PROVEN"
            status_value = "SOURCE_LAG_REQUIRED_FAIL_CLOSED"
        else:
            gate = "NOT_REQUIRED"
            status_value = "NO_SOURCE_LAG_REQUIRED"

        if fragile_fields and not has_pass:
            gate = "HOLD_SOURCE_LAG_FRAGILE_OR_NOT_PROVEN"
            status_value = "SOURCE_LAG_FRAGILE_FAIL_CLOSED"

        source_statuses.append(status_value)
        required_fields_values.append("|".join(sorted(set(required_fields))))
        required_family_values.append("|".join(sorted(set(required_families))))
        source_lag_gates.append(gate)
        rejects.append(reject)

        if reject:
            out.at[idx, "hard_reject"] = True
            out.at[idx, "gate_pass"] = False
            out.at[idx, "hard_reject_reasons"] = append_reject_reason(
                row.get("hard_reject_reasons", ""),
                "source_lag_required_not_proven",
            )

    out["source_lag_policy_status"] = source_statuses
    out["source_lag_required_fields"] = required_fields_values
    out["source_lag_required_families"] = required_family_values
    out["source_lag_gate"] = source_lag_gates
    out["source_lag_policy_reject"] = rejects
    return out


def selected_column_indices(timestamps: pd.DatetimeIndex, hours_per_split: int, train_hours_per_split: int) -> np.ndarray:
    split = split_for_timestamps(timestamps)
    if hours_per_split <= 0 and train_hours_per_split <= 0:
        return np.arange(len(timestamps), dtype=int)
    selected: list[int] = []
    for split_name in SPLIT_ORDER:
        idx = np.where(split == split_name)[0]
        if len(idx):
            limit = train_hours_per_split if split_name == "train_2024" else hours_per_split
            if limit <= 0:
                selected.extend(idx.tolist())
            else:
                selected.extend(idx[-limit:].tolist())
    return np.array(sorted(set(selected)), dtype=int)


def split_csv(value: str) -> list[str]:
    return [part.strip() for part in str(value).split(",") if part.strip()]


def nan_rolling_mean(values: np.ndarray, window: int, min_periods: int | None = None) -> np.ndarray:
    return pd.Series(values).rolling(window, min_periods=min_periods or max(8, window // 4)).mean().to_numpy()


def nan_rolling_std(values: np.ndarray, window: int, min_periods: int | None = None) -> np.ndarray:
    return pd.Series(values).rolling(window, min_periods=min_periods or max(8, window // 4)).std().to_numpy()


def regime_crash_like_mask(numeric: dict[str, np.ndarray], split: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    close = numeric["trade_close"].astype(float)
    log_close = np.log(np.where(close > 0, close, np.nan))
    ret1 = log_close - np.roll(log_close, 1, axis=1)
    ret1[:, 0] = np.nan
    market_ret = np.nanmedian(ret1, axis=0)
    neg_share = np.nanmean(ret1 < 0, axis=0)
    dispersion = np.nanpercentile(ret1, 90, axis=0) - np.nanpercentile(ret1, 10, axis=0)
    vol_24h = nan_rolling_std(market_ret, 24)
    vol_168h = nan_rolling_std(market_ret, 168)
    ret_24h = pd.Series(market_ret).rolling(24, min_periods=8).sum().to_numpy()
    ret_168h = pd.Series(market_ret).rolling(168, min_periods=42).sum().to_numpy()
    index = np.nanmedian(log_close, axis=0)
    peak = pd.Series(index).rolling(24 * 30, min_periods=24).max().to_numpy()
    drawdown = index - peak
    volume = numeric.get("trade_quote_volume")
    if volume is not None:
        volume_med = np.nanmedian(np.log1p(volume.astype(float)), axis=0)
        volume_z = (volume_med - nan_rolling_mean(volume_med, 168, 48)) / (nan_rolling_std(volume_med, 168, 48) + 1e-12)
    else:
        volume_z = np.full(len(split), np.nan)
    features = pd.DataFrame(
        {
            "market_ret_24h": ret_24h,
            "market_ret_168h": ret_168h,
            "neg_asset_share_1h": neg_share,
            "cs_dispersion_1h": dispersion,
            "vol_24h": vol_24h,
            "vol_168h": vol_168h,
            "drawdown_30d_log": drawdown,
            "volume_z_168h": volume_z,
        }
    ).replace([np.inf, -np.inf], np.nan)
    train = split == "train_2024"
    may = split == "known_may2026_stress"
    mu = features.loc[train].mean(skipna=True)
    sd = features.loc[train].std(skipna=True).replace(0, np.nan)
    z = (features - mu) / (sd + 1e-12)
    components = pd.DataFrame(
        {
            "neg_ret_24h_z": -z["market_ret_24h"],
            "neg_ret_168h_z": -z["market_ret_168h"],
            "neg_share_z": z["neg_asset_share_1h"],
            "dispersion_z": z["cs_dispersion_1h"],
            "vol24_z": z["vol_24h"],
            "vol168_z": z["vol_168h"],
            "drawdown_z": -z["drawdown_30d_log"],
            "low_volume_z": -z["volume_z_168h"],
        }
    )
    stress_score = components.mean(axis=1, skipna=True)
    may_vec = z.loc[may].mean(skipna=True)
    valid = [col for col in z.columns if np.isfinite(may_vec.get(col, np.nan))]
    distance = ((z[valid] - may_vec[valid]) ** 2).mean(axis=1).pow(0.5) if valid else pd.Series(np.nan, index=z.index)
    may_distance_q75 = float(distance.loc[may].quantile(0.75)) if np.any(may) else np.nan
    may_stress_q25 = float(stress_score.loc[may].quantile(0.25)) if np.any(may) else np.nan
    crash_like = (distance <= may_distance_q75) & (stress_score >= may_stress_q25)
    return crash_like.to_numpy(dtype=bool), {
        "may_distance_q75": may_distance_q75,
        "may_stress_score_q25": may_stress_q25,
        "train_crash_like_hours": int(np.nansum(crash_like.to_numpy(dtype=bool) & train)),
        "may_stress_hours": int(np.nansum(may)),
    }


def contiguous_orientation_extension_mask(
    split: np.ndarray,
    extension_hours: int,
) -> np.ndarray:
    mask = np.zeros(len(split), dtype=bool)
    if extension_hours <= 0:
        return mask
    train_idx = np.where(split == "train_2024")[0]
    if len(train_idx) == 0:
        return mask
    start = int(train_idx[-1]) + 1
    end = min(len(split), start + int(extension_hours))
    if start < end:
        mask[start:end] = True
    return mask


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
            "stress floor Sortino <= 0",
            "OOS lag/stale/control variant dominates original",
            "ranked-label-only evidence without raw tradable PnL support",
            "missing transaction cost model",
            "turnover excessive relative to reward",
            "same-bar/future/leakage field violations upstream",
        ],
        "portfolio_construction": {
            "signal_to_weight": "cross-sectional percentile rank, demeaned to dollar neutral, normalized to gross 1 per timestamp",
            "orientation": "chosen on full train_2024 plus optional contiguous post-train extension; extension rows are relabeled out of OOS evaluation",
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


def finite_corr_columns(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Vectorized equivalent of finite_corr for asset-by-time matrices."""
    xx = np.asarray(x, dtype=np.float64)
    yy = np.asarray(y, dtype=np.float64)
    if xx.shape != yy.shape or xx.ndim != 2:
        raise ValueError(f"finite_corr_columns shape mismatch: {xx.shape} vs {yy.shape}")
    mask = np.isfinite(xx) & np.isfinite(yy)
    counts = mask.sum(axis=0).astype(np.float64, copy=False)
    x0 = np.where(mask, xx, 0.0)
    y0 = np.where(mask, yy, 0.0)
    sum_x = x0.sum(axis=0)
    sum_y = y0.sum(axis=0)
    safe_counts = np.where(counts > 0, counts, 1.0)
    x0 -= sum_x.reshape(1, -1) / safe_counts.reshape(1, -1)
    y0 -= sum_y.reshape(1, -1) / safe_counts.reshape(1, -1)
    x0[~mask] = 0.0
    y0[~mask] = 0.0
    cov_sum = np.einsum("ij,ij->j", x0, y0)
    var_x = np.einsum("ij,ij->j", x0, x0)
    var_y = np.einsum("ij,ij->j", y0, y0)
    denom = np.sqrt(var_x * var_y)
    valid = (counts >= 8) & (var_x > counts * 1e-24) & (var_y > counts * 1e-24)
    out = np.divide(cov_sum, denom, out=np.full_like(cov_sum, np.nan), where=valid)
    return out


def rank_pct(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    if bn is not None:
        counts = np.isfinite(arr).sum(axis=0).astype(np.float64, copy=False)
        ranks = bn.nanrankdata(arr, axis=0).astype(np.float64, copy=False)
        out = np.divide(ranks, counts.reshape(1, -1), out=np.full_like(ranks, np.nan), where=counts.reshape(1, -1) > 0)
        out[~np.isfinite(arr)] = np.nan
        return out
    return pd.DataFrame(arr).rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)


def ranked_signal_to_weights(ranks: np.ndarray, gross: float = 1.0, max_abs_weight: float = 0.03) -> np.ndarray:
    finite_counts = np.isfinite(ranks).sum(axis=0, keepdims=True)
    rank_means = np.divide(
        np.nansum(ranks, axis=0, keepdims=True),
        finite_counts,
        out=np.zeros((1, ranks.shape[1]), dtype=np.float64),
        where=finite_counts > 0,
    )
    centered = ranks - rank_means
    centered[~np.isfinite(centered)] = 0.0
    denom = np.nansum(np.abs(centered), axis=0, keepdims=True)
    weights = np.divide(centered, denom, out=np.zeros_like(centered), where=denom > 1e-12) * gross
    weights = np.clip(weights, -max_abs_weight, max_abs_weight)
    denom2 = np.nansum(np.abs(weights), axis=0, keepdims=True)
    return np.divide(weights, denom2, out=np.zeros_like(weights), where=denom2 > 1e-12) * gross


def signal_to_weights(signal: np.ndarray, gross: float = 1.0, max_abs_weight: float = 0.03) -> np.ndarray:
    return ranked_signal_to_weights(rank_pct(signal), gross, max_abs_weight)


def _bounded_flat_sample(values: np.ndarray, max_values: int = 250_000) -> np.ndarray:
    flat = np.asarray(values, dtype=np.float64).ravel(order="C")
    if flat.size > max_values:
        flat = flat[:: max(1, math.ceil(flat.size / max_values))]
    return flat[np.isfinite(flat)]


def _rank_1d(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=np.float64)
    ranks[order] = np.arange(len(values), dtype=np.float64)
    return ranks


def compute_safediv_diagnostics(
    evaluator: A7AB4Evaluator,
    expression: str,
    signal: np.ndarray,
) -> dict[str, Any]:
    calls = collect_operator_calls(expression, "SafeDiv")
    if not calls:
        return {
            "safediv_node_count": 0,
            "safediv_denominator_min_abs_q01": np.nan,
            "safediv_denominator_min_abs_q05": np.nan,
            "safediv_denominator_min_q01_to_median": np.nan,
            "safediv_denominator_max_near_zero_ratio": 0.0,
            "safediv_local_rank_stability_min": np.nan,
            "signal_abs_p99_to_median": np.nan,
            "signal_top1pct_abs_mass_share": np.nan,
            "safediv_review_flag": False,
            "safediv_review_reasons": "",
        }
    signal_abs = np.abs(_bounded_flat_sample(signal))
    signal_median = float(np.nanmedian(signal_abs)) if signal_abs.size else np.nan
    signal_p99 = float(np.nanquantile(signal_abs, 0.99)) if signal_abs.size else np.nan
    signal_tail_ratio = (
        signal_p99 / max(signal_median, 1e-12)
        if np.isfinite(signal_p99) and np.isfinite(signal_median)
        else np.nan
    )
    if signal_abs.size and float(np.nansum(signal_abs)) > 0:
        threshold = float(np.nanquantile(signal_abs, 0.99))
        top_mass_share = float(np.nansum(signal_abs[signal_abs >= threshold]) / np.nansum(signal_abs))
    else:
        top_mass_share = np.nan

    q01_values: list[float] = []
    q05_values: list[float] = []
    q01_median_ratios: list[float] = []
    near_zero_ratios: list[float] = []
    rank_stabilities: list[float] = []
    for _, args in calls:
        if len(args) != 2:
            continue
        numerator = np.asarray(evaluator.eval(args[0]), dtype=np.float64).ravel(order="C")
        denominator = np.asarray(evaluator.eval(args[1]), dtype=np.float64).ravel(order="C")
        step = max(1, math.ceil(len(denominator) / 250_000))
        numerator = numerator[::step]
        denominator = denominator[::step]
        valid_denominator = np.isfinite(denominator)
        denominator_abs = np.abs(denominator[valid_denominator])
        if not denominator_abs.size:
            continue
        median_abs = float(np.nanmedian(denominator_abs))
        q01 = float(np.nanquantile(denominator_abs, 0.01))
        q05 = float(np.nanquantile(denominator_abs, 0.05))
        adaptive_floor = max(1e-12, median_abs * 1e-3)
        q01_values.append(q01)
        q05_values.append(q05)
        q01_median_ratios.append(q01 / max(median_abs, 1e-12))
        near_zero_ratios.append(float(np.mean(denominator_abs <= adaptive_floor)))

        valid = np.isfinite(numerator) & np.isfinite(denominator) & (np.abs(denominator) > 1e-12)
        if int(valid.sum()) >= 32:
            raw_ratio = numerator[valid] / denominator[valid]
            stable_denominator = np.copysign(np.maximum(np.abs(denominator[valid]), adaptive_floor), denominator[valid])
            stable_ratio = numerator[valid] / stable_denominator
            finite = np.isfinite(raw_ratio) & np.isfinite(stable_ratio)
            if int(finite.sum()) >= 32:
                raw_rank = _rank_1d(raw_ratio[finite])
                stable_rank = _rank_1d(stable_ratio[finite])
                rank_stabilities.append(float(np.corrcoef(raw_rank, stable_rank)[0, 1]))

    min_q01_median_ratio = min(q01_median_ratios) if q01_median_ratios else np.nan
    max_near_zero_ratio = max(near_zero_ratios) if near_zero_ratios else 0.0
    min_rank_stability = min(rank_stabilities) if rank_stabilities else np.nan
    review_reasons: list[str] = []
    if np.isfinite(min_q01_median_ratio) and min_q01_median_ratio < 0.03:
        review_reasons.append("denominator_q01_below_3pct_median")
    if calls and max_near_zero_ratio > 0.005:
        review_reasons.append("denominator_near_zero_share_above_0p5pct")
    if calls and np.isfinite(min_rank_stability) and min_rank_stability < 0.98:
        review_reasons.append("denominator_floor_changes_local_rank")
    if calls and np.isfinite(signal_tail_ratio) and signal_tail_ratio > 100.0:
        review_reasons.append("signal_p99_to_median_above_100")
    if calls and np.isfinite(top_mass_share) and top_mass_share > 0.25:
        review_reasons.append("signal_top1pct_abs_mass_above_25pct")
    return {
        "safediv_node_count": int(len(calls)),
        "safediv_denominator_min_abs_q01": min(q01_values) if q01_values else np.nan,
        "safediv_denominator_min_abs_q05": min(q05_values) if q05_values else np.nan,
        "safediv_denominator_min_q01_to_median": min_q01_median_ratio,
        "safediv_denominator_max_near_zero_ratio": max_near_zero_ratio,
        "safediv_local_rank_stability_min": min_rank_stability,
        "signal_abs_p99_to_median": signal_tail_ratio,
        "signal_top1pct_abs_mass_share": top_mass_share,
        "safediv_review_flag": bool(review_reasons),
        "safediv_review_reasons": ";".join(review_reasons),
    }


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
    raw_label_rank: np.ndarray | None = None,
    prepared_signal: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray] | None = None,
) -> list[dict[str, Any]]:
    if prepared_signal is None:
        rank_signal = rank_pct(signal * orientation)
        weights = ranked_signal_to_weights(rank_signal)
        cost = turnover_cost(weights, cost_bps)
        capacity_series = np.nansum(np.abs(weights) * quote_volume, axis=0)
    else:
        weights, cost, rank_signal, capacity_series = prepared_signal
    gross_forward = np.nansum(weights * raw_label, axis=0)
    net = gross_forward - cost
    periods_per_year = 24.0 * 365.0 / max(1, horizon)
    rank_label = raw_label_rank if raw_label_rank is not None else rank_pct(raw_label)
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
        ic_values = finite_corr_columns(sig_sub, lab_sub)
        rankic_values = finite_corr_columns(sig_sub, rank_lab_sub)
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


def prepare_signal_arrays(
    signal: np.ndarray,
    quote_volume: np.ndarray,
    cost_bps: float,
    orientation: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rank_signal = rank_pct(signal * orientation)
    weights = ranked_signal_to_weights(rank_signal)
    cost = turnover_cost(weights, cost_bps)
    capacity_series = np.nansum(np.abs(weights) * quote_volume, axis=0)
    return weights, cost, rank_signal, capacity_series


def transform_prepared_control(
    prepared_signal: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    variant: str,
    rng: np.random.Generator,
    quote_volume: np.ndarray,
    cost_bps: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    weights, _, rank_signal, _ = prepared_signal
    if variant == "one_bar_lag":
        transformed_rank = dense_shift_matrix(rank_signal, 1)
        transformed_weights = np.nan_to_num(dense_shift_matrix(weights, 1), nan=0.0)
    elif variant == "stale_168h":
        transformed_rank = dense_shift_matrix(rank_signal, 168)
        transformed_weights = np.nan_to_num(dense_shift_matrix(weights, 168), nan=0.0)
    elif variant == "time_shuffle":
        permutation = rng.permutation(rank_signal.shape[1])
        transformed_rank = rank_signal[:, permutation]
        transformed_weights = weights[:, permutation]
    elif variant == "symbol_shuffle":
        permutation = rng.permutation(rank_signal.shape[0])
        transformed_rank = rank_signal[permutation, :]
        transformed_weights = weights[permutation, :]
    else:
        raise ValueError(f"prepared control does not support variant: {variant}")
    cost = turnover_cost(transformed_weights, cost_bps)
    capacity_series = np.nansum(np.abs(transformed_weights) * quote_volume, axis=0)
    return transformed_weights, cost, transformed_rank, capacity_series


def select_train_orientation(
    positive: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    negative: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    raw_label: np.ndarray,
    orientation_mask: np.ndarray,
) -> float:
    positive_weights, positive_cost, _, _ = positive
    negative_weights, negative_cost, _, _ = negative
    positive_net = np.nansum(positive_weights * raw_label, axis=0) - positive_cost
    negative_net = np.nansum(negative_weights * raw_label, axis=0) - negative_cost
    positive_mean = float(np.nanmean(positive_net[orientation_mask]))
    negative_mean = float(np.nanmean(negative_net[orientation_mask]))
    return 1.0 if positive_mean >= negative_mean else -1.0


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


def deterministic_control_rng(expression: str, horizon: int, variant: str) -> np.random.Generator:
    # Common random numbers make control comparisons invariant to candidate ID,
    # formula spelling, shard assignment, and evaluation order.
    del expression
    payload = f"a7reward1-control-v2|{int(horizon)}|{variant}".encode("utf-8")
    seed = int.from_bytes(hashlib.sha256(payload).digest()[:8], "little", signed=False)
    return np.random.default_rng(seed)


def load_numeric_for_queue(
    queue: pd.DataFrame,
    hours_per_split: int,
    train_hours_per_split: int,
    numeric_cache: Path | None = None,
) -> tuple[pd.DatetimeIndex, np.ndarray, dict[str, np.ndarray], dict[str, np.ndarray]]:
    if numeric_cache is not None:
        return load_numeric_cache(numeric_cache, queue, hours_per_split, train_hours_per_split)
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
    requested_universe_state = fields & COMPUTED_UNIVERSE_STATE_FIELDS
    missing = sorted(
        fields
        - base_fields
        - latent_fields
        - upper_fields
        - requested_dense_funding
        - requested_universe_state
    )
    if missing:
        raise RuntimeError(f"missing numeric fields for reward model: {missing[:20]}")

    symbols = strict_symbols()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_fields))
    numeric.update(load_upper_numeric(loaded_symbols, timestamps, upper_fields))
    if "active_universe_size" in requested_universe_state:
        active_count = np.isfinite(numeric["trade_close"].astype(float)).sum(axis=0).astype(float)
        numeric["active_universe_size"] = np.broadcast_to(active_count, numeric["trade_close"].shape).copy()
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
    idx = selected_column_indices(timestamps, hours_per_split, train_hours_per_split)
    timestamps = pd.DatetimeIndex(timestamps[idx])
    numeric = {key: value[:, idx] for key, value in numeric.items()}
    groups = {key: value[:, idx] for key, value in groups.items()}
    split = split_for_timestamps(timestamps)
    return timestamps, split, numeric, groups


def _cache_array_name(kind: str, key: str) -> str:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
    return f"{kind}_{digest}.npy"


def _queue_expression_fingerprint(queue: pd.DataFrame) -> str:
    expressions = sorted(queue.get("expression", pd.Series(dtype=str)).dropna().astype(str))
    return hashlib.sha256("\n".join(expressions).encode("utf-8")).hexdigest()


def build_numeric_cache(
    cache_dir: Path,
    queue: pd.DataFrame,
    hours_per_split: int,
    train_hours_per_split: int,
) -> dict[str, Any]:
    timestamps, split, numeric, groups = load_numeric_for_queue(
        queue,
        hours_per_split,
        train_hours_per_split,
        numeric_cache=None,
    )
    cache_dir.mkdir(parents=True, exist_ok=True)
    numeric_files: dict[str, str] = {}
    group_files: dict[str, str] = {}
    for key, values in sorted(numeric.items()):
        filename = _cache_array_name("numeric", key)
        np.save(cache_dir / filename, np.asarray(values), allow_pickle=False)
        numeric_files[key] = filename
    for key, values in sorted(groups.items()):
        filename = _cache_array_name("group", key)
        array = np.asarray(values)
        if array.dtype == object:
            array = array.astype(str)
        np.save(cache_dir / filename, array, allow_pickle=False)
        group_files[key] = filename
    timestamp_file = "timestamps_ns.npy"
    split_file = "split.npy"
    np.save(cache_dir / timestamp_file, timestamps.asi8, allow_pickle=False)
    np.save(cache_dir / split_file, np.asarray(split, dtype=str), allow_pickle=False)
    manifest = {
        "stage": "A7REWARD-1-SHARED-NUMERIC-CACHE",
        "version": 1,
        "generated_at": now_utc(),
        "decision": "PASS_A7REWARD1_SHARED_NUMERIC_CACHE_READY",
        "queue_rows": int(len(queue)),
        "queue_expression_fingerprint": _queue_expression_fingerprint(queue),
        "hours_per_split": int(hours_per_split),
        "train_hours_per_split": int(train_hours_per_split),
        "timestamp_count": int(len(timestamps)),
        "timestamp_timezone": str(timestamps.tz) if timestamps.tz is not None else "",
        "timestamp_file": timestamp_file,
        "split_file": split_file,
        "numeric_files": numeric_files,
        "group_files": group_files,
        "numeric_shapes": {key: list(np.asarray(values).shape) for key, values in sorted(numeric.items())},
        "numeric_dtypes": {key: str(np.asarray(values).dtype) for key, values in sorted(numeric.items())},
        "base_panel_root": str(BASE_DIR),
        "latent_panel": str(LATENT_PANEL),
        "upper_regime_panel": str(UPPER_REGIME_PANEL),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(cache_dir / "a7reward1_numeric_cache_manifest.json", manifest)
    return manifest


def load_numeric_cache(
    cache_dir: Path,
    queue: pd.DataFrame,
    hours_per_split: int,
    train_hours_per_split: int,
) -> tuple[pd.DatetimeIndex, np.ndarray, dict[str, np.ndarray], dict[str, np.ndarray]]:
    manifest_path = cache_dir / "a7reward1_numeric_cache_manifest.json"
    manifest = read_json(manifest_path)
    if manifest.get("decision") != "PASS_A7REWARD1_SHARED_NUMERIC_CACHE_READY":
        raise RuntimeError(f"numeric cache is incomplete: {manifest_path}")
    if int(manifest.get("version", -1)) != 1:
        raise RuntimeError(f"numeric cache version mismatch: {manifest.get('version')}")
    if int(manifest.get("hours_per_split", -1)) != int(hours_per_split):
        raise RuntimeError("numeric cache hours_per_split mismatch")
    if int(manifest.get("train_hours_per_split", -1)) != int(train_hours_per_split):
        raise RuntimeError("numeric cache train_hours_per_split mismatch")
    expected_sources = {
        "base_panel_root": BASE_DIR,
        "latent_panel": LATENT_PANEL,
        "upper_regime_panel": UPPER_REGIME_PANEL,
    }
    for manifest_key, current_path in expected_sources.items():
        cached_path = str(manifest.get(manifest_key) or "")
        current_normalized = os.path.normcase(os.path.abspath(str(current_path)))
        cached_normalized = os.path.normcase(os.path.abspath(cached_path)) if cached_path else ""
        if cached_normalized != current_normalized:
            raise RuntimeError(
                f"numeric cache source mismatch for {manifest_key}: {cached_path!r} != {str(current_path)!r}"
            )
    numeric_files = dict(manifest.get("numeric_files") or {})
    required = {"trade_close", "trade_quote_volume"}
    for expression in queue.get("expression", pd.Series(dtype=str)).dropna().astype(str):
        required.update(expression_fields(expression))
    missing = sorted(required - set(numeric_files))
    if missing:
        raise RuntimeError(f"numeric cache missing queue fields: {missing[:20]}")
    numeric = {
        key: np.load(cache_dir / filename, mmap_mode="r", allow_pickle=False)
        for key, filename in numeric_files.items()
    }
    groups = {
        key: np.load(cache_dir / filename, mmap_mode="r", allow_pickle=False)
        for key, filename in dict(manifest.get("group_files") or {}).items()
    }
    timestamp_ns = np.load(cache_dir / str(manifest["timestamp_file"]), mmap_mode="r", allow_pickle=False)
    timezone_name = str(manifest.get("timestamp_timezone") or "")
    if timezone_name:
        timestamps = pd.DatetimeIndex(pd.to_datetime(timestamp_ns, utc=True)).tz_convert(timezone_name)
    else:
        timestamps = pd.DatetimeIndex(pd.to_datetime(timestamp_ns))
    split = np.load(cache_dir / str(manifest["split_file"]), mmap_mode="r", allow_pickle=False).astype(object)
    expected_count = int(manifest.get("timestamp_count", -1))
    if len(timestamps) != expected_count or any(values.shape[1] != expected_count for values in numeric.values()):
        raise RuntimeError("numeric cache shape mismatch")
    return timestamps, split, numeric, groups


def evaluate_queue(
    queue: pd.DataFrame,
    hours_per_split: int,
    train_hours_per_split: int,
    cost_bps: float,
    candidate_cap: int,
    orientation_extension_hours: int,
    checkpoint_dir: Path | None = None,
    checkpoint_every: int = 0,
    numeric_cache: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if candidate_cap > 0:
        queue = queue.head(candidate_cap).copy()
    timestamps, split, numeric, groups = load_numeric_for_queue(
        queue,
        hours_per_split,
        train_hours_per_split,
        numeric_cache=numeric_cache,
    )
    crash_like, regime_payload = regime_crash_like_mask(numeric, split)
    eval_split = split.copy()
    orientation_extension_mask = contiguous_orientation_extension_mask(
        split,
        orientation_extension_hours,
    )
    if np.any(orientation_extension_mask):
        eval_split[orientation_extension_mask] = ORIENTATION_SPLIT
    orientation_mask = (split == "train_2024") | orientation_extension_mask
    evaluator = A7AB4Evaluator(numeric, groups)
    raw_labels = {h: horizon_label(numeric["trade_close"], timestamps, split, h) for h in HORIZONS}
    raw_label_ranks = {h: rank_pct(raw_labels[h]) for h in HORIZONS}
    quote_volume = numeric["trade_quote_volume"]
    metric_rows: list[dict[str, Any]] = []
    error_rows: list[dict[str, Any]] = []
    total_rows = len(queue)
    for idx_row, row in enumerate(queue.to_dict("records"), start=1):
        cid = str(row.get("blueprint_id", f"row_{idx_row}"))
        print(f"[A7REWARD1] evaluating {idx_row}/{total_rows} {cid}", flush=True)
        try:
            signal = evaluator.eval(str(row["expression"]))
            candidate_metric_start = len(metric_rows)
            safediv_diagnostics = compute_safediv_diagnostics(evaluator, str(row["expression"]), signal)
            prepared_by_orientation = {
                orientation: prepare_signal_arrays(signal, quote_volume, cost_bps, orientation)
                for orientation in (1.0, -1.0)
            }
            # Orientation is chosen on train only for each horizon, then frozen.
            for horizon in HORIZONS:
                orientation = select_train_orientation(
                    prepared_by_orientation[1.0],
                    prepared_by_orientation[-1.0],
                    raw_labels[horizon],
                    orientation_mask,
                )
                metric_rows.extend(
                    split_metrics(
                        row,
                        horizon,
                        "original",
                        signal,
                        raw_labels[horizon],
                        eval_split,
                        quote_volume,
                        cost_bps,
                        orientation,
                        raw_label_ranks[horizon],
                        prepared_by_orientation[orientation],
                    )
                )
                for variant in CONTROL_VARIANTS:
                    if variant == "sign_flip":
                        prepared_control = prepared_by_orientation[-orientation]
                    else:
                        prepared_control = transform_prepared_control(
                            prepared_by_orientation[orientation],
                            variant,
                            deterministic_control_rng(str(row["expression"]), horizon, variant),
                            quote_volume,
                            cost_bps,
                        )
                    metric_rows.extend(
                        split_metrics(
                            row,
                            horizon,
                            variant,
                            signal,
                            raw_labels[horizon],
                            eval_split,
                            quote_volume,
                            cost_bps,
                            orientation,
                            raw_label_ranks[horizon],
                            prepared_control,
                        )
                    )
            for metric in metric_rows[candidate_metric_start:]:
                metric.update(safediv_diagnostics)
        except Exception as exc:  # keep the reward audit fail-open as data, not as silent loss
            error_rows.append({"blueprint_id": cid, "error": repr(exc), "expression": row.get("expression", "")})
        finally:
            # Candidate expressions materialize large asset x time matrices. Keeping the
            # whole expression cache for a 1k-row shard can dominate memory and kill
            # otherwise healthy workers; clear between candidates while preserving
            # intra-expression caching during a single eval call.
            evaluator.cache.clear()
            if idx_row % max(1, checkpoint_every or 64) == 0:
                gc.collect()
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
                    "orientation_train_hours": int(np.nansum(orientation_mask)),
                    "orientation_extension_hours": int(np.nansum(orientation_extension_mask)),
                    "orientation_extension_crash_like_hours": int(np.nansum(orientation_extension_mask & crash_like)),
                    "train_crash_like_hours": int(regime_payload["train_crash_like_hours"]),
                },
            )
    metrics = pd.DataFrame(metric_rows)
    if not metrics.empty:
        metrics["orientation_train_hours"] = int(np.nansum(orientation_mask))
        metrics["orientation_extension_hours"] = int(np.nansum(orientation_extension_mask))
        metrics["orientation_extension_crash_like_hours"] = int(np.nansum(orientation_extension_mask & crash_like))
        metrics["train_crash_like_hours"] = int(regime_payload["train_crash_like_hours"])
        metrics["may_stress_hours"] = int(regime_payload["may_stress_hours"])
        metrics["orientation_extension_requested_hours"] = int(orientation_extension_hours)
    return metrics, pd.DataFrame(error_rows)


def aggregate_rewards(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return pd.DataFrame()
    original = metrics[metrics["variant"].eq("original")].copy()
    controls = (
        metrics[metrics["variant"].isin(CONTROL_DOMINANCE_VARIANTS)]
        .groupby(["blueprint_id", "horizon_h", "split"], as_index=False)
        .agg(
            max_abs_control_net_mean=("net_mean", lambda s: float(np.nanmax(np.abs(s))) if len(s) else np.nan),
            max_control_floor_sortino=("nonoverlap_floor_sortino", lambda s: float(np.nanmax(s)) if len(s) else np.nan),
        )
    )
    shuffle_controls = (
        metrics[metrics["variant"].isin(SHUFFLE_VARIANTS)]
        .groupby(["blueprint_id", "horizon_h", "split"], as_index=False)
        .agg(
            max_abs_shuffle_control_net_mean=("net_mean", lambda s: float(np.nanmax(np.abs(s))) if len(s) else np.nan),
            max_shuffle_floor_sortino=("nonoverlap_floor_sortino", lambda s: float(np.nanmax(s)) if len(s) else np.nan),
        )
    )
    lag_stale_controls = (
        metrics[metrics["variant"].isin(LAG_STALE_VARIANTS)]
        .groupby(["blueprint_id", "horizon_h", "split"], as_index=False)
        .agg(max_lag_stale_floor_sortino=("nonoverlap_floor_sortino", lambda s: float(np.nanmax(s)) if len(s) else np.nan))
    )
    original = original.merge(controls, on=["blueprint_id", "horizon_h", "split"], how="left")
    original = original.merge(shuffle_controls, on=["blueprint_id", "horizon_h", "split"], how="left")
    original = original.merge(lag_stale_controls, on=["blueprint_id", "horizon_h", "split"], how="left")
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
        train_sortino = float(train.get("nonoverlap_median_sortino", np.nan))
        validation_sortino = float(validation.get("nonoverlap_median_sortino", np.nan))
        test_sortino = float(test.get("nonoverlap_median_sortino", np.nan))
        recent_sortino = float(recent.get("nonoverlap_median_sortino", np.nan))
        sortinos = [
            validation_sortino,
            test_sortino,
            recent_sortino,
        ]
        median_oos_sortino = float(np.nanmedian(sortinos)) if np.isfinite(np.nanmedian(sortinos)) else np.nan
        train_oos_sortino_gap = abs(train_sortino - median_oos_sortino) if np.isfinite(train_sortino) and np.isfinite(median_oos_sortino) else np.nan
        train_oos_consistency_penalty = min(train_oos_sortino_gap / 4.0, 3.0) if np.isfinite(train_oos_sortino_gap) else 3.0
        train_overfit_penalty = max(0.0, train_sortino - median_oos_sortino - 3.0) / 2.0 if np.isfinite(train_sortino) and np.isfinite(median_oos_sortino) else 1.5
        floor_sortinos = [
            float(validation.get("nonoverlap_floor_sortino", np.nan)),
            float(test.get("nonoverlap_floor_sortino", np.nan)),
            float(recent.get("nonoverlap_floor_sortino", np.nan)),
        ]
        control_floor_sortinos = [
            float(validation.get("max_control_floor_sortino", np.nan)),
            float(test.get("max_control_floor_sortino", np.nan)),
            float(recent.get("max_control_floor_sortino", np.nan)),
        ]
        lag_stale_floor_sortinos = [
            float(validation.get("max_lag_stale_floor_sortino", np.nan)),
            float(test.get("max_lag_stale_floor_sortino", np.nan)),
            float(recent.get("max_lag_stale_floor_sortino", np.nan)),
        ]
        shuffle_floor_sortinos = [
            float(validation.get("max_shuffle_floor_sortino", np.nan)),
            float(test.get("max_shuffle_floor_sortino", np.nan)),
            float(recent.get("max_shuffle_floor_sortino", np.nan)),
        ]
        oos_control_dominated = [
            np.isfinite(control) and np.isfinite(original_floor) and control >= original_floor
            for control, original_floor in zip(control_floor_sortinos, floor_sortinos)
        ]
        oos_lag_stale_dominated = [
            np.isfinite(control) and np.isfinite(original_floor) and control >= original_floor
            for control, original_floor in zip(lag_stale_floor_sortinos, floor_sortinos)
        ]
        oos_shuffle_dominated = [
            np.isfinite(control) and np.isfinite(original_floor) and control >= original_floor
            for control, original_floor in zip(shuffle_floor_sortinos, floor_sortinos)
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
            0.24 * train_sortino
            + 0.18 * validation_sortino
            + 0.18 * test_sortino
            + 0.14 * recent_sortino
            + 0.12 * float(np.nanmin(sortinos))
            + 0.08 * float(np.nanmin(floor_sortinos))
            + 0.08 * float(recent.get("nonoverlap_median_sharpe", np.nan))
            + 0.08 * float(recent.get("rankic_mean", np.nan)) * 20.0
            + 0.05 * float(stress.get("nonoverlap_median_sortino", 0.0) if np.isfinite(float(stress.get("nonoverlap_median_sortino", np.nan))) else 0.0)
            + 0.05 * capacity_score
            - 0.15 * dd_penalty
            - 0.05 * turnover_penalty
            - 0.25 * control_penalty
            - 0.30 * train_oos_consistency_penalty
            - 0.20 * train_overfit_penalty
        )
        sample = group.iloc[0].to_dict()
        hard_reject_reasons = []
        if not np.isfinite(diagnostic_composite):
            hard_reject_reasons.append("non_finite_diagnostic_composite")
        if not (float(recent.get("nonoverlap_median_sortino", np.nan)) > 0):
            hard_reject_reasons.append("recent_sortino_non_positive")
        if not (train_sortino > 0):
            hard_reject_reasons.append("train_sortino_non_positive")
        if not np.isfinite(train_oos_sortino_gap):
            hard_reject_reasons.append("missing_train_oos_consistency")
        if np.isfinite(train_sortino) and np.isfinite(median_oos_sortino) and train_sortino > median_oos_sortino + 6.0:
            hard_reject_reasons.append("train_sortino_overfit_gap")
        if not (float(train.get("net_mean", np.nan)) > 0):
            hard_reject_reasons.append("train_orientation_no_positive_edge")
        if float(train.get("n_obs", 0)) < 250:
            hard_reject_reasons.append("orientation_sample_too_small")
        if not all(np.isfinite(value) and value > 0 for value in floor_sortinos):
            hard_reject_reasons.append("oos_nonoverlap_floor_not_positive")
        stress_n_obs = float(stress.get("n_obs", 0) or 0)
        if stress_n_obs > 0 and not (float(stress.get("nonoverlap_floor_sortino", np.nan)) > 0):
            hard_reject_reasons.append("stress_floor_not_positive")
        if sum(oos_control_dominated) > 0:
            hard_reject_reasons.append("oos_control_dominated")
        if sum(oos_lag_stale_dominated) > 0:
            hard_reject_reasons.append("oos_lag_stale_dominated")
        if sum(oos_shuffle_dominated) > 0:
            hard_reject_reasons.append("oos_shuffle_dominated")
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
                "train_sortino": train_sortino,
                "validation_sortino": validation_sortino,
                "test_sortino": test_sortino,
                "recent_sortino": recent_sortino,
                "median_oos_sortino": median_oos_sortino,
                "train_oos_sortino_gap": train_oos_sortino_gap,
                "train_oos_consistency_penalty": train_oos_consistency_penalty,
                "train_overfit_penalty": train_overfit_penalty,
                "validation_floor_sortino": validation.get("nonoverlap_floor_sortino", np.nan),
                "test_floor_sortino": test.get("nonoverlap_floor_sortino", np.nan),
                "recent_floor_sortino": recent.get("nonoverlap_floor_sortino", np.nan),
                "stress_sortino": stress.get("nonoverlap_median_sortino", np.nan),
                "stress_floor_sortino": stress.get("nonoverlap_floor_sortino", np.nan),
                "stress_n_obs": stress_n_obs,
                "recent_sharpe": recent.get("nonoverlap_median_sharpe", np.nan),
                "recent_ic": recent.get("ic_mean", np.nan),
                "recent_rankic": recent.get("rankic_mean", np.nan),
                "recent_net_mean": recent.get("net_mean", np.nan),
                "recent_max_drawdown": recent.get("max_drawdown", np.nan),
                "recent_avg_turnover": recent.get("avg_turnover", np.nan),
                "recent_capacity_proxy": recent.get("capacity_proxy_median_quote_volume", np.nan),
                "recent_control_ratio": recent_control,
                "recent_shuffle_control_ratio": recent_shuffle_control,
                "oos_control_dominated_count": int(sum(oos_control_dominated)),
                "oos_lag_stale_dominated_count": int(sum(oos_lag_stale_dominated)),
                "oos_shuffle_dominated_count": int(sum(oos_shuffle_dominated)),
                "oos_positive_split_count": int(sum(oos_positive)),
                "orientation_train_hours": sample.get("orientation_train_hours", np.nan),
                "orientation_extension_hours": sample.get("orientation_extension_hours", np.nan),
                "orientation_extension_crash_like_hours": sample.get("orientation_extension_crash_like_hours", np.nan),
                "orientation_extension_requested_hours": sample.get("orientation_extension_requested_hours", np.nan),
                "train_crash_like_hours": sample.get("train_crash_like_hours", np.nan),
                "may_stress_hours": sample.get("may_stress_hours", np.nan),
                "safediv_node_count": sample.get("safediv_node_count", 0),
                "safediv_denominator_min_abs_q01": sample.get("safediv_denominator_min_abs_q01", np.nan),
                "safediv_denominator_min_abs_q05": sample.get("safediv_denominator_min_abs_q05", np.nan),
                "safediv_denominator_min_q01_to_median": sample.get("safediv_denominator_min_q01_to_median", np.nan),
                "safediv_denominator_max_near_zero_ratio": sample.get("safediv_denominator_max_near_zero_ratio", 0.0),
                "safediv_local_rank_stability_min": sample.get("safediv_local_rank_stability_min", np.nan),
                "signal_abs_p99_to_median": sample.get("signal_abs_p99_to_median", np.nan),
                "signal_top1pct_abs_mass_share": sample.get("signal_top1pct_abs_mass_share", np.nan),
                "safediv_review_flag": truthy(sample.get("safediv_review_flag", False)),
                "safediv_review_reasons": sample.get("safediv_review_reasons", ""),
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
    n_assets, n_times = 64, 1440
    split = np.array(["train_2024"] * 300 + ["validation_2025H1"] * 300 + ["test_2025H2"] * 300 + ["recent_oos_2026JanApr"] * 240 + ["known_may2026_stress"] * 300, dtype=object)
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
    parser.add_argument("--train-hours-per-split", type=int, default=int(os.environ.get("A7REWARD_TRAIN_HOURS_PER_SPLIT", "0")))
    parser.add_argument("--orientation-extension-hours", type=int, default=int(os.environ.get("A7REWARD_ORIENTATION_EXTENSION_HOURS", "0")))
    parser.add_argument("--cost-bps", type=float, default=float(os.environ.get("A7REWARD_COST_BPS", "5.0")))
    parser.add_argument("--smoke-only", action="store_true")
    parser.add_argument("--runtime", default=str(RUNTIME))
    parser.add_argument("--report", default=str(REPORT))
    parser.add_argument("--checkpoint-every", type=int, default=int(os.environ.get("A7REWARD_CHECKPOINT_EVERY", "8")))
    parser.add_argument("--source-policy", default=os.environ.get("A7REWARD_SOURCE_POLICY", str(DEFAULT_SOURCE_POLICY)))
    parser.add_argument("--source-lag-summary", default=os.environ.get("A7REWARD_SOURCE_LAG_SUMMARY", str(DEFAULT_SOURCE_LAG_SUMMARY)))
    parser.add_argument("--numeric-cache", default=os.environ.get("A7REWARD_NUMERIC_CACHE", ""))
    parser.add_argument("--build-numeric-cache-only", action="store_true")
    args = parser.parse_args()

    runtime = Path(args.runtime)
    report_path = Path(args.report)
    runtime.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    contract = contract_payload()
    write_json(runtime / "a7reward1_reward_contract.json", contract)

    if args.build_numeric_cache_only:
        if not args.numeric_cache:
            raise SystemExit("--build-numeric-cache-only requires --numeric-cache")
        queue_path = Path(args.queue)
        queue = read_csv(queue_path)
        if queue.empty:
            raise SystemExit(f"empty reward queue: {queue_path}")
        if args.candidate_cap > 0:
            queue = queue.head(args.candidate_cap).copy()
        manifest = build_numeric_cache(
            Path(args.numeric_cache),
            queue,
            args.hours_per_split,
            args.train_hours_per_split,
        )
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return

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
        args.train_hours_per_split,
        args.cost_bps,
        args.candidate_cap,
        args.orientation_extension_hours,
        checkpoint_dir=runtime,
        checkpoint_every=args.checkpoint_every,
        numeric_cache=Path(args.numeric_cache) if args.numeric_cache else None,
    )
    rewards = aggregate_rewards(metrics)
    source_policy_path = Path(args.source_policy)
    source_lag_summary_path = Path(args.source_lag_summary)
    source_policy = load_source_policy(source_policy_path)
    source_lag_pass_ids, source_lag_pass_formulas = load_source_lag_passes(source_lag_summary_path)
    rewards = apply_source_lag_policy(rewards, source_policy, source_lag_pass_ids, source_lag_pass_formulas)
    metrics.to_csv(runtime / "a7reward1_split_reward_metrics.csv", index=False)
    errors.to_csv(runtime / "a7reward1_eval_errors.csv", index=False)
    rewards.to_csv(runtime / "a7reward1_candidate_reward_leaderboard.csv", index=False)
    accepted = accepted_for_next_search(rewards)
    rejected = rewards[~rewards.index.isin(accepted.index)].copy() if not rewards.empty else rewards.copy()
    accepted.to_csv(runtime / "a7reward1_accepted_for_next_search.csv", index=False)
    rejected.to_csv(runtime / "a7reward1_validation_gate_rejections.csv", index=False)

    best_by_pareto = rewards.sort_values(["gate_pass", "pareto_rank", "objective_pass_count"], ascending=[False, True, False]).head(80)
    best_by_sortino = rewards.sort_values(["hard_reject", "recent_sortino"], ascending=[True, False]).head(40)
    best_by_train_aligned_reward = rewards.sort_values(
        ["hard_reject", "gate_pass", "overall_reward", "train_sortino", "min_oos_floor_sortino"],
        ascending=[True, False, False, False, False],
    ).head(80)
    best_by_sharpe = rewards.sort_values(["hard_reject", "recent_sharpe"], ascending=[True, False]).head(40)
    best_by_ic = rewards.sort_values(["hard_reject", "recent_rankic"], ascending=[True, False]).head(40)
    diagnostic_composite = rewards.sort_values(["hard_reject", "diagnostic_composite_score"], ascending=[True, False]).head(80)
    top_queue = accepted if not accepted.empty else best_by_pareto
    best_overall = diagnostic_composite
    best_by_pareto.to_csv(runtime / "a7reward1_pareto_leaderboard.csv", index=False)
    best_by_sortino.to_csv(runtime / "a7reward1_best_by_sortino.csv", index=False)
    best_by_train_aligned_reward.to_csv(runtime / "a7reward1_best_by_train_aligned_reward.csv", index=False)
    best_by_sharpe.to_csv(runtime / "a7reward1_best_by_sharpe.csv", index=False)
    best_by_ic.to_csv(runtime / "a7reward1_best_by_rankic.csv", index=False)
    diagnostic_composite.to_csv(runtime / "a7reward1_diagnostic_composite_leaderboard.csv", index=False)

    decision = (
        "PASS_A7REWARD1_PORTFOLIO_REWARD_LEADERBOARD_BUILT"
        if smoke_pass and not accepted.empty
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
        "train_hours_per_split": int(args.train_hours_per_split),
        "numeric_cache": str(Path(args.numeric_cache)) if args.numeric_cache else "",
        "numeric_cache_used": bool(args.numeric_cache),
        "orientation_extension_hours_requested": int(args.orientation_extension_hours),
        "orientation_train_hours": int(metrics["orientation_train_hours"].max()) if "orientation_train_hours" in metrics else 0,
        "orientation_extension_hours": int(metrics["orientation_extension_hours"].max()) if "orientation_extension_hours" in metrics else 0,
        "orientation_extension_crash_like_hours": int(metrics["orientation_extension_crash_like_hours"].max()) if "orientation_extension_crash_like_hours" in metrics else 0,
        "train_crash_like_hours": int(metrics["train_crash_like_hours"].max()) if "train_crash_like_hours" in metrics else 0,
        "may_stress_hours": int(metrics["may_stress_hours"].max()) if "may_stress_hours" in metrics else 0,
        "cost_bps": float(args.cost_bps),
        "split_metric_rows": int(metrics.shape[0]),
        "reward_rows": int(rewards.shape[0]),
        "hard_reject_rows": int(rewards["hard_reject"].sum()) if not rewards.empty else 0,
        "valid_reward_rows": int((~rewards["hard_reject"]).sum()) if not rewards.empty else 0,
        "accepted_for_next_search_rows": int(accepted.shape[0]),
        "accepted_for_next_search_unique_blueprints": int(accepted["blueprint_id"].nunique()) if not accepted.empty else 0,
        "eval_error_rows": int(errors.shape[0]),
        "synthetic_smoke_pass": bool(smoke_pass),
        "source_policy_path": str(source_policy_path),
        "source_lag_summary_path": str(source_lag_summary_path),
        "source_policy_fields": int(len(source_policy)),
        "source_lag_pass_ids": int(len(source_lag_pass_ids)),
        "source_lag_policy_reject_rows": int(rewards["source_lag_policy_reject"].sum()) if "source_lag_policy_reject" in rewards else 0,
        "safediv_review_rows": int(rewards["safediv_review_flag"].fillna(False).astype(bool).sum()) if "safediv_review_flag" in rewards else 0,
        "top_pareto_blueprint_id": str(top_queue.iloc[0]["blueprint_id"]) if not top_queue.empty else "",
        "top_pareto_rank": int(top_queue.iloc[0]["pareto_rank"]) if not top_queue.empty else 0,
        "top_pareto_objective_pass_count": int(top_queue.iloc[0]["objective_pass_count"]) if not top_queue.empty else 0,
        "top_diagnostic_composite_blueprint_id": str(diagnostic_composite.iloc[0]["blueprint_id"]) if not diagnostic_composite.empty else "",
        "top_diagnostic_composite_score": float(diagnostic_composite.iloc[0]["diagnostic_composite_score"]) if not diagnostic_composite.empty else np.nan,
        "ranking_policy": "multi_objective_gate_and_pareto; diagnostic_composite_score_is_not_a_search_reward",
        "reward_alignment": {
            "primary_train_component": "train_sortino",
            "oos_components": ["validation_sortino", "test_sortino", "recent_sortino", "min_oos_floor_sortino"],
            "consistency_penalty": "penalize train_oos_sortino_gap; hard reject only when train_sortino materially exceeds OOS median",
            "recent_sortino_role": "one OOS component, no longer dominant standalone reward",
        },
        "automatic_validation_gate": {
            "output": str(runtime / "a7reward1_accepted_for_next_search.csv"),
            "reject_output": str(runtime / "a7reward1_validation_gate_rejections.csv"),
            "required": [
                "train_sortino > 0",
                "train_sortino_overfit_gap not present",
                "train_orientation_no_positive_edge not present",
                "oos_nonoverlap_floor_not_positive not present",
                "min_oos_sortino > 0",
                "min_oos_floor_sortino > 0",
                "stress_floor_sortino > 0 when stress_n_obs > 0",
                "oos_control_dominated_count == 0",
                "oos_lag_stale_dominated_count == 0",
                "recent_shuffle_control_ratio < 1",
                "orientation_sample_too_small not present",
                "hard_reject == false",
                "gate_pass == true",
                "source_lag_policy_reject == false",
            ],
        },
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
        "A7REWARD1 establishes portfolio-level evaluation for crypto alpha search. Numeric clue scores remain diagnostic. Candidate acceptance is now gated by train/OOS/stress/control metrics and Pareto rank; the fixed diagnostic composite is not a standalone search reward.",
        "",
        "## Reward Contract",
        "",
        "Primary ranking uses multi-objective gates and Pareto rank over train Sortino, validation/test/recent OOS Sortino, OOS floor stability, Sharpe, IC/RankIC, drawdown, turnover, stress survival, and control dominance. The train/OOS consistency penalty reduces train-only overfit; recent Sortino is one OOS component, not the dominant reward.",
        "",
        "## Counts",
        "",
        f"- queue_rows: `{manifest['queue_rows']}`",
        f"- candidate_cap: `{manifest['candidate_cap']}`",
        f"- hours_per_split: `{manifest['hours_per_split']}`",
        f"- train_hours_per_split: `{manifest['train_hours_per_split']}`",
        f"- orientation_extension_hours_requested: `{manifest['orientation_extension_hours_requested']}`",
        f"- orientation_train_hours: `{manifest['orientation_train_hours']}`",
        f"- orientation_extension_hours: `{manifest['orientation_extension_hours']}`",
        f"- orientation_extension_crash_like_hours: `{manifest['orientation_extension_crash_like_hours']}`",
        f"- train_crash_like_hours: `{manifest['train_crash_like_hours']}`",
        f"- cost_bps: `{manifest['cost_bps']}`",
        f"- reward_rows: `{manifest['reward_rows']}`",
        f"- valid_reward_rows: `{manifest['valid_reward_rows']}`",
        f"- accepted_for_next_search_rows: `{manifest['accepted_for_next_search_rows']}`",
        f"- accepted_for_next_search_unique_blueprints: `{manifest['accepted_for_next_search_unique_blueprints']}`",
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
        "## Accepted For Next Search",
        "",
        md_table(accepted, 40),
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
