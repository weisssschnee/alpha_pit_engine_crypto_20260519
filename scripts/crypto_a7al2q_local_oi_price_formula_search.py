from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

FAST_SCRIPT = REPO / "scripts" / "crypto_a7al2l_fast_derived_replay_preflight.py"
P0_SCRIPT = REPO / "scripts" / "crypto_a7al2p0_pre_search_hardening_audit.py"

P2_MANIFEST = REPO / "runtime" / "a7al2p2_local_oi_price_search_contract" / "a7al2p2_manifest.json"
P2_SEEDS = REPO / "runtime" / "a7al2p2_local_oi_price_search_contract" / "a7al2p2_seed_candidates.csv"
OUT_DIR = REPO / "runtime" / "a7al2q_local_oi_price_formula_search"
REPORT = REPO / "reports" / "CRYPTO_A7AL2Q_LOCAL_OI_PRICE_FORMULA_SEARCH_20260528.md"

PRE_MAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
AUDIT_SPLITS = PRE_MAY_SPLITS + ["known_may2026_stress"]
GENERATED_TOTAL = 4000
SELECTED_FOR_FAST_REPLAY = 128
DEEP_AUDIT = 16
LATENT_AUDIT_CAP = 16
COST_BPS = [2.0, 5.0, 10.0]
WINDOWS = [4, 8, 12, 24, 48, 72, 96, 168, 336, 504, 720]
OI_FIELDS = [
    "open_interest_last",
    "open_interest_mean",
    "open_interest_value_last",
    "open_interest_value_mean",
]
PRICE_FIELDS = ["trade_close", "mark_close", "index_close"]
RANK_PATTERN_IDS = {
    "rank_level_spread",
    "rank_delta_spread",
    "oi_rank_x_neg_price_rank",
    "oi_rank_x_price_delta_sign",
    "oi_delta_rank_x_price_rank",
}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fast = load_module("a7al2l_fast_for_q", FAST_SCRIPT)
p0 = load_module("a7al2p0_for_q", P0_SCRIPT)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if pd.api.types.is_object_dtype(view[col]) or pd.api.types.is_string_dtype(view[col]):
            view[col] = view[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```\n" + view.to_string(index=False) + "\n```"


def sha16(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def finite_tstat(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    if len(x) < 3:
        return np.nan
    std = np.nanstd(x, ddof=1)
    if not np.isfinite(std) or std <= 0:
        return np.nan
    return float(np.nanmean(x) / std * math.sqrt(len(x)))


def expression_fields(expression: str) -> set[str]:
    ops = set(re.findall(r"\b([A-Z][A-Za-z0-9_]*)\s*\(", expression))
    tokens = set(re.findall(r"\b[a-z][a-z0-9_]*\b", expression))
    return tokens - {op.lower() for op in ops} - {"nan", "inf"}


def skeleton_for(pattern_id: str, expression: str) -> str:
    no_fields = expression
    for field in sorted(OI_FIELDS + PRICE_FIELDS, key=len, reverse=True):
        no_fields = no_fields.replace(field, "FIELD")
    no_windows = re.sub(r"\b\d+\b", "W", no_fields)
    return f"{pattern_id}::{no_windows}"


def formula_patterns(oi: str, price: str, w1: int, w2: int) -> list[tuple[str, str]]:
    oi_mean = f"Mean({oi},{w1})"
    px_mean = f"Mean({price},{w2})"
    oi_delta = f"Delta({oi},{w1})"
    px_delta = f"Delta({price},{w2})"
    oi_z = f"ZScore({oi_mean})"
    px_z = f"ZScore({px_mean})"
    oi_dz = f"ZScore({oi_delta})"
    px_dz = f"ZScore({px_delta})"
    oi_r = f"Rank({oi_mean})"
    px_r = f"Rank({px_mean})"
    oi_dr = f"Rank({oi_delta})"
    px_dr = f"Rank({px_delta})"
    return [
        ("abs_level_gap", f"Sub(Abs({oi_z}),Abs({px_z}))"),
        ("abs_delta_gap", f"Sub(Abs({oi_dz}),Abs({px_dz}))"),
        ("delta_spread", f"Sub({oi_dz},{px_dz})"),
        ("level_spread", f"Sub({oi_z},{px_z})"),
        ("rank_level_spread", f"Sub({oi_r},{px_r})"),
        ("rank_delta_spread", f"Sub({oi_dr},{px_dr})"),
        ("oi_delta_x_price_delta", f"Mul({oi_dz},{px_dz})"),
        ("oi_level_x_price_delta", f"Mul({oi_z},{px_dz})"),
        ("oi_delta_x_price_level", f"Mul({oi_dz},{px_z})"),
        ("oi_rank_x_neg_price_rank", f"Mul({oi_r},Neg({px_r}))"),
        ("oi_rank_x_price_delta_sign", f"Mul({oi_r},Sign({px_delta}))"),
        ("oi_delta_rank_x_price_rank", f"Mul({oi_dr},{px_r})"),
        ("oi_abs_x_price_abs_delta", f"Mul(Abs({oi_z}),Abs({px_dz}))"),
        ("oi_abs_delta_x_price_abs", f"Mul(Abs({oi_dz}),Abs({px_z}))"),
        ("oi_level_plus_neg_price_delta", f"Add({oi_z},Neg({px_dz}))"),
        ("oi_delta_plus_neg_price_level", f"Add({oi_dz},Neg({px_z}))"),
    ]


def generate_candidates(seeds: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    seen_expr: set[str] = set()
    seed_expr_map = {str(row["expression"]): str(row["candidate_id"]) for _, row in seeds.iterrows()}
    for oi in OI_FIELDS:
        for price in PRICE_FIELDS:
            for w1 in WINDOWS:
                for w2 in WINDOWS:
                    for pattern_id, expression in formula_patterns(oi, price, w1, w2):
                        if expression in seen_expr:
                            continue
                        seen_expr.add(expression)
                        rows.append(
                            {
                                "candidate_id": f"a7al2q_{sha16(expression)}",
                                "expression": expression,
                                "fields": "|".join(sorted(expression_fields(expression))),
                                "field_families": "open_interest|price",
                                "pattern_id": pattern_id,
                                "oi_field": oi,
                                "price_field": price,
                                "oi_window": w1,
                                "price_window": w2,
                                "windows": f"{w1}|{w2}",
                                "skeleton_key": f"skeleton-{sha16(skeleton_for(pattern_id, expression))}",
                                "production_key": f"a7al2q_local_oi_price::{pattern_id}::{oi}|{price}::{w1}|{w2}",
                                "parent_seed_id": seed_expr_map.get(expression, ""),
                                "source": "seed_exact" if expression in seed_expr_map else "local_mutation",
                                "deterministic_order_key": sha16(f"{pattern_id}|{oi}|{price}|{w1}|{w2}|{expression}"),
                            }
                        )
    frame = pd.DataFrame(rows).sort_values("deterministic_order_key").reset_index(drop=True)
    seed_rows = frame[frame["source"].eq("seed_exact")]
    non_seed_rows = frame[~frame["source"].eq("seed_exact")]
    selected = pd.concat([seed_rows, non_seed_rows], ignore_index=True).drop_duplicates("expression", keep="first")
    return selected.head(GENERATED_TOTAL).reset_index(drop=True)


def select_for_fast_replay(generated: pd.DataFrame, seeds: pd.DataFrame, cap: int = SELECTED_FOR_FAST_REPLAY) -> pd.DataFrame:
    rows: list[pd.Series] = []
    skeleton_counts: Counter[str] = Counter()
    production_prefix_counts: Counter[str] = Counter()
    pattern_counts: Counter[str] = Counter()
    field_pair_counts: Counter[str] = Counter()
    max_skeleton = max(1, int(math.floor(cap * 0.20)))
    max_pattern = max(1, int(math.floor(cap * 0.25)))
    max_field_pair = max(1, int(math.floor(cap * 0.35)))

    def accept(row: pd.Series, force: bool = False) -> bool:
        skeleton = str(row["skeleton_key"])
        pattern = str(row["pattern_id"])
        fields = str(row["fields"])
        prod_prefix = "::".join(str(row["production_key"]).split("::")[:3])
        if not force:
            if skeleton_counts[skeleton] >= max_skeleton:
                return False
            if pattern_counts[pattern] >= max_pattern:
                return False
            if field_pair_counts[fields] >= max_field_pair:
                return False
            if production_prefix_counts[prod_prefix] >= 16:
                return False
        rows.append(row)
        skeleton_counts[skeleton] += 1
        pattern_counts[pattern] += 1
        field_pair_counts[fields] += 1
        production_prefix_counts[prod_prefix] += 1
        return True

    seed_expressions = set(seeds["expression"].astype(str))
    for _, row in generated[generated["expression"].astype(str).isin(seed_expressions)].iterrows():
        accept(row, force=True)
    for _, row in generated.iterrows():
        if len(rows) >= cap:
            break
        if str(row["expression"]) in seed_expressions:
            continue
        if str(row["pattern_id"]) in RANK_PATTERN_IDS:
            continue
        accept(row)

    selected = pd.DataFrame(rows).drop_duplicates("candidate_id").head(cap).reset_index(drop=True)
    selected["selected_for_fast_replay"] = True
    return selected


def precompute_components(matrices: dict[str, np.ndarray], selected: pd.DataFrame) -> dict[tuple[str, str, int], np.ndarray]:
    components: dict[tuple[str, str, int], np.ndarray] = {}
    needs = selected[["oi_field", "price_field", "oi_window", "price_window"]].copy()
    selected_patterns = set(selected["pattern_id"].astype(str))
    needs_rank = bool(selected_patterns & RANK_PATTERN_IDS)
    pairs: set[tuple[str, int]] = set()
    for _, row in needs.iterrows():
        pairs.add((str(row["oi_field"]), int(row["oi_window"])))
        pairs.add((str(row["price_field"]), int(row["price_window"])))
    for field, window in sorted(pairs):
        raw = matrices[field]
        mean = fast.rolling_mean(raw, window)
        delta = raw - fast.shift_matrix(raw, window)
        components[("mean_z", field, window)] = fast.cs_zscore(mean)
        components[("delta_z", field, window)] = fast.cs_zscore(delta)
        if needs_rank:
            components[("mean_rank", field, window)] = fast.cs_rank_pct(mean)
            components[("delta_rank", field, window)] = fast.cs_rank_pct(delta)
        components[("delta_sign", field, window)] = np.sign(delta)
    return components


def eval_local_signal(candidate: pd.Series, components: dict[tuple[str, str, int], np.ndarray]) -> np.ndarray:
    pattern = str(candidate["pattern_id"])
    oi = str(candidate["oi_field"])
    price = str(candidate["price_field"])
    w1 = int(candidate["oi_window"])
    w2 = int(candidate["price_window"])
    oi_z = components[("mean_z", oi, w1)]
    px_z = components[("mean_z", price, w2)]
    oi_dz = components[("delta_z", oi, w1)]
    px_dz = components[("delta_z", price, w2)]
    px_delta_sign = components[("delta_sign", price, w2)]
    if pattern == "abs_level_gap":
        return np.abs(oi_z) - np.abs(px_z)
    if pattern == "abs_delta_gap":
        return np.abs(oi_dz) - np.abs(px_dz)
    if pattern == "delta_spread":
        return oi_dz - px_dz
    if pattern == "level_spread":
        return oi_z - px_z
    if pattern == "rank_level_spread":
        oi_r = components[("mean_rank", oi, w1)]
        px_r = components[("mean_rank", price, w2)]
        return oi_r - px_r
    if pattern == "rank_delta_spread":
        oi_dr = components[("delta_rank", oi, w1)]
        px_dr = components[("delta_rank", price, w2)]
        return oi_dr - px_dr
    if pattern == "oi_delta_x_price_delta":
        return oi_dz * px_dz
    if pattern == "oi_level_x_price_delta":
        return oi_z * px_dz
    if pattern == "oi_delta_x_price_level":
        return oi_dz * px_z
    if pattern == "oi_rank_x_neg_price_rank":
        oi_r = components[("mean_rank", oi, w1)]
        px_r = components[("mean_rank", price, w2)]
        return oi_r * (-px_r)
    if pattern == "oi_rank_x_price_delta_sign":
        oi_r = components[("mean_rank", oi, w1)]
        return oi_r * px_delta_sign
    if pattern == "oi_delta_rank_x_price_rank":
        oi_dr = components[("delta_rank", oi, w1)]
        px_r = components[("mean_rank", price, w2)]
        return oi_dr * px_r
    if pattern == "oi_abs_x_price_abs_delta":
        return np.abs(oi_z) * np.abs(px_dz)
    if pattern == "oi_abs_delta_x_price_abs":
        return np.abs(oi_dz) * np.abs(px_z)
    if pattern == "oi_level_plus_neg_price_delta":
        return oi_z - px_dz
    if pattern == "oi_delta_plus_neg_price_level":
        return oi_dz - px_z
    raise ValueError(f"unsupported local pattern: {pattern}")


def portfolio_weights_and_spread(signal: np.ndarray, label: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    valid = np.isfinite(signal) & np.isfinite(label)
    valid_counts = valid.sum(axis=0)
    enough = valid_counts >= fast.MIN_ACTIVE_SYMBOLS
    sig = np.where(valid, signal, np.nan)
    q10 = np.full(signal.shape[1], np.nan)
    q90 = np.full(signal.shape[1], np.nan)
    cols = np.where(enough)[0]
    if len(cols):
        with np.errstate(all="ignore"):
            q10[cols] = np.nanpercentile(sig[:, cols], 10, axis=0)
            q90[cols] = np.nanpercentile(sig[:, cols], 90, axis=0)
    top_mask = valid & enough.reshape(1, -1) & (signal >= q90.reshape(1, -1))
    bottom_mask = valid & enough.reshape(1, -1) & (signal <= q10.reshape(1, -1))
    top_count = top_mask.sum(axis=0)
    bottom_count = bottom_mask.sum(axis=0)
    ok = (top_count > 0) & (bottom_count > 0)
    weights = np.zeros(signal.shape, dtype=np.float64)
    if ok.any():
        cols_ok = np.where(ok)[0]
        weights[:, cols_ok] += top_mask[:, cols_ok] / top_count[cols_ok].reshape(1, -1)
        weights[:, cols_ok] -= bottom_mask[:, cols_ok] / bottom_count[cols_ok].reshape(1, -1)
    spread = np.full(signal.shape[1], np.nan)
    spread[ok] = np.nansum(weights[:, ok] * label[:, ok], axis=0)
    return weights, spread, top_count.astype(float), bottom_count.astype(float)


def turnover_series(weights: np.ndarray) -> np.ndarray:
    prev = np.zeros(weights.shape[0], dtype=np.float64)
    out = np.full(weights.shape[1], np.nan)
    for j in range(weights.shape[1]):
        w = weights[:, j]
        if np.isfinite(w).any() and np.abs(w).sum() > 0:
            out[j] = 0.5 * float(np.nansum(np.abs(w - prev)))
            prev = w.copy()
        else:
            out[j] = 0.0
            prev = np.zeros_like(prev)
    return out


def split_metric_rows(
    candidate_id: str,
    variant: str,
    entry_label: str,
    spread: np.ndarray,
    weights: np.ndarray,
    split: np.ndarray,
    orientation: float,
    top_count: np.ndarray,
    bottom_count: np.ndarray,
) -> list[dict[str, Any]]:
    oriented = spread * orientation
    turnover = turnover_series(weights)
    rows: list[dict[str, Any]] = []
    for split_name in fast.SPLIT_ORDER:
        mask = (split == split_name) & np.isfinite(oriented)
        x = oriented[mask]
        t = turnover[mask]
        row = {
            "candidate_id": candidate_id,
            "variant": variant,
            "entry_label": entry_label,
            "split": split_name,
            "n_dates": int(mask.sum()),
            "mean_oriented_spread": float(np.nanmean(x)) if len(x) else np.nan,
            "hourly_tstat_naive": finite_tstat(x),
            "positive_rate": float(np.nanmean(x > 0)) if len(x) else np.nan,
            "avg_one_way_turnover": float(np.nanmean(t)) if len(t) else np.nan,
            "avg_top_count": float(np.nanmean(top_count[mask])) if mask.any() else np.nan,
            "avg_bottom_count": float(np.nanmean(bottom_count[mask])) if mask.any() else np.nan,
        }
        for cost in COST_BPS:
            net = x - t * (cost / 10000.0)
            row[f"net_mean_spread_{int(cost)}bps"] = float(np.nanmean(net)) if len(net) else np.nan
        rows.append(row)
    return rows


def fit_train_orientation(signal: np.ndarray, label: np.ndarray, split: np.ndarray) -> tuple[float, float]:
    _weights, spread, _top, _bottom = portfolio_weights_and_spread(signal, label)
    mask = (split == "train_2024") & np.isfinite(spread)
    mean_train = float(np.nanmean(spread[mask])) if mask.any() else np.nan
    orientation = 1.0 if not np.isfinite(mean_train) or mean_train >= 0 else -1.0
    return orientation, mean_train


def control_ratio_by_split(metrics: pd.DataFrame) -> pd.DataFrame:
    return p0.control_ratio_by_split(metrics)


def pre_may_positive_count(metrics: pd.DataFrame, candidate_id: str, variant: str, entry_label: str, col: str) -> int:
    part = metrics[
        metrics["candidate_id"].eq(candidate_id)
        & metrics["variant"].eq(variant)
        & metrics["entry_label"].eq(entry_label)
        & metrics["split"].isin(PRE_MAY_SPLITS)
    ]
    if len(part) != 3:
        return 0
    return int(pd.to_numeric(part[col], errors="coerce").gt(0).sum())


def classify_candidates(
    selected: pd.DataFrame,
    metric_rows: pd.DataFrame,
    latent_rows: pd.DataFrame,
    control_gate: pd.DataFrame,
    overlap_rows: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, candidate in selected.iterrows():
        cid = str(candidate["candidate_id"])
        reasons: list[str] = []
        warnings_out: list[str] = []
        label_t1_pos = pre_may_positive_count(metric_rows, cid, "original", "label_t1_to_t25", "mean_oriented_spread")
        label_t2_pos = pre_may_positive_count(metric_rows, cid, "original", "label_t2_to_t26", "mean_oriented_spread")
        lag_pos = pre_may_positive_count(metric_rows, cid, "one_bar_lag", "label_t1_to_t25", "mean_oriented_spread")
        latent_part = latent_rows[latent_rows["candidate_id"].eq(cid)] if not latent_rows.empty else pd.DataFrame()
        latent_audited = not latent_part.empty
        latent_pos = (
            pre_may_positive_count(latent_rows, cid, "timevarying_latent_state_neutral", "label_t1_to_t25", "mean_oriented_spread")
            if latent_audited
            else np.nan
        )
        cost_2_pos = pre_may_positive_count(metric_rows, cid, "original", "label_t1_to_t25", "net_mean_spread_2bps")
        cost_5_pos = pre_may_positive_count(metric_rows, cid, "original", "label_t1_to_t25", "net_mean_spread_5bps")
        cost_10_pos = pre_may_positive_count(metric_rows, cid, "original", "label_t1_to_t25", "net_mean_spread_10bps")
        control_part = control_gate[
            control_gate["candidate_id"].eq(cid)
            & control_gate["entry_label"].eq("label_t1_to_t25")
            & control_gate["split"].isin(PRE_MAY_SPLITS)
        ]
        max_control_ratio = float(control_part["control_ratio"].max()) if len(control_part) else np.nan
        recent_cost = metric_rows[
            metric_rows["candidate_id"].eq(cid)
            & metric_rows["variant"].eq("original")
            & metric_rows["entry_label"].eq("label_t1_to_t25")
            & metric_rows["split"].eq("recent_oos_2026JanApr")
        ]
        recent_net_10 = float(recent_cost["net_mean_spread_10bps"].iloc[0]) if len(recent_cost) else np.nan
        recent_turnover = float(recent_cost["avg_one_way_turnover"].iloc[0]) if len(recent_cost) else np.nan
        if overlap_rows.empty or "candidate_id" not in overlap_rows.columns:
            overlap_recent = pd.DataFrame()
        else:
            overlap_recent = overlap_rows[
                overlap_rows["candidate_id"].eq(cid)
                & overlap_rows["split"].eq("recent_oos_2026JanApr")
            ]
        nw_recent = float(overlap_recent["newey_west_tstat_lag24"].iloc[0]) if len(overlap_recent) else np.nan
        if label_t1_pos < 3:
            reasons.append("label_t1_not_all_premay_positive")
        if label_t2_pos < 3:
            reasons.append("label_t2_not_all_premay_positive")
        if lag_pos < 3:
            reasons.append("one_bar_lag_fragile")
        if not latent_audited:
            warnings_out.append("timevarying_latent_deferred_to_a7al2r")
        elif latent_pos < 3:
            reasons.append("timevarying_latent_fragile")
        if np.isfinite(max_control_ratio) and max_control_ratio >= 1.0:
            reasons.append("control_dominated")
        elif np.isfinite(max_control_ratio) and max_control_ratio >= 0.8:
            warnings_out.append("control_close")
        if min(cost_2_pos, cost_5_pos, cost_10_pos) < 3:
            reasons.append("cost_proxy_fragile")
        if not np.isfinite(recent_net_10) or recent_net_10 <= 0:
            reasons.append("recent_10bps_negative")
        if not np.isfinite(nw_recent) or abs(nw_recent) < 1.0:
            warnings_out.append("overlap_adjusted_recent_tstat_weak")
        if not reasons:
            decision = "A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE"
        elif "control_dominated" in reasons:
            decision = "HOLD_A7AL2Q_CONTROL_DOMINATED"
        elif "one_bar_lag_fragile" in reasons or "cost_proxy_fragile" in reasons or "recent_10bps_negative" in reasons:
            decision = "HOLD_A7AL2Q_LATENCY_OR_COST_FRAGILE"
        elif "timevarying_latent_fragile" in reasons:
            decision = "HOLD_A7AL2Q_LATENT_FRAGILE"
        else:
            decision = "HOLD_A7AL2Q_WEAK_OR_INCONSISTENT"
        score = (
            label_t1_pos
            + label_t2_pos
            + lag_pos
            + np.nan_to_num(latent_pos, nan=1.0)
            + 0.5 * cost_10_pos
            + np.nan_to_num(1.0 - max_control_ratio, nan=0.0)
            + np.nan_to_num(recent_net_10 * 1000.0, nan=0.0)
        )
        rows.append(
            {
                "candidate_id": cid,
                "decision": decision,
                "reasons": "|".join(reasons),
                "warnings": "|".join(warnings_out),
                "label_t1_positive_premay_splits": label_t1_pos,
                "label_t2_positive_premay_splits": label_t2_pos,
                "one_bar_lag_positive_premay_splits": lag_pos,
                "timevarying_latent_positive_premay_splits": latent_pos,
                "timevarying_latent_audited": latent_audited,
                "net_2bps_positive_premay_splits": cost_2_pos,
                "net_5bps_positive_premay_splits": cost_5_pos,
                "net_10bps_positive_premay_splits": cost_10_pos,
                "control_ratio_premay_max_by_split": max_control_ratio,
                "recent_net_mean_spread_10bps": recent_net_10,
                "recent_turnover": recent_turnover,
                "recent_newey_west_tstat_lag24": nw_recent,
                "selector_score_no_may": score,
            }
        )
    return pd.DataFrame(rows).sort_values("selector_score_no_may", ascending=False)


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_p2 = read_json(P2_MANIFEST)
    if manifest_p2.get("decision") != "PASS_A7AL2P2_LOCAL_OI_PRICE_SEARCH_CONTRACT_READY_FOR_A7AL2Q":
        raise SystemExit("A7AL-2P2 contract is not ready for A7AL-2Q")
    if not manifest_p2.get("authorizes_a7al2q_local_execution"):
        raise SystemExit("A7AL-2P2 does not authorize A7AL-2Q local execution")

    seeds = pd.read_csv(P2_SEEDS)
    generated = generate_candidates(seeds)
    selected = select_for_fast_replay(generated, seeds)
    exec_replay_cap = int(os.environ.get("A7AL2Q_EXEC_REPLAY_CAP", str(len(selected))) or str(len(selected)))
    replay_selected = selected.head(max(1, min(exec_replay_cap, len(selected)))).copy()
    all_fields = {"trade_close"}
    for text in replay_selected["fields"].astype(str):
        all_fields.update(part for part in text.split("|") if part)

    symbols = fast.strict_symbols()
    loaded_symbols, timestamps, matrices = fast.load_panel_matrices(symbols, all_fields)
    split = fast.split_for_timestamps(timestamps)
    labels = {
        "label_t_to_t24": p0.label_matrix_entry_shift(matrices["trade_close"], timestamps, split, 0),
        "label_t1_to_t25": p0.label_matrix_entry_shift(matrices["trade_close"], timestamps, split, 1),
        "label_t2_to_t26": p0.label_matrix_entry_shift(matrices["trade_close"], timestamps, split, 2),
    }
    components = precompute_components(matrices, replay_selected)
    rng = np.random.default_rng(20260528)

    metric_rows: list[dict[str, Any]] = []
    latent_metric_rows: list[dict[str, Any]] = []
    overlap_rows: list[dict[str, Any]] = []
    nonoverlap_rows: list[dict[str, Any]] = []
    error_rows: list[dict[str, Any]] = []
    orientation_rows: list[dict[str, Any]] = []

    for i, candidate in replay_selected.iterrows():
        cid = str(candidate["candidate_id"])
        expression = str(candidate["expression"])
        print(f"[A7AL-2Q] replay {i + 1}/{len(replay_selected)} {cid}", flush=True)
        try:
            base_signal = eval_local_signal(candidate, components)
            orientation, train_mean = fit_train_orientation(base_signal, labels["label_t1_to_t25"], split)
            orientation_rows.append(
                {
                    "candidate_id": cid,
                    "orientation_fit_split": "train_2024",
                    "orientation_entry_label": "label_t1_to_t25",
                    "train_mean_spread": train_mean,
                    "orientation": orientation,
                    "uses_may": False,
                }
            )
            variants: dict[str, np.ndarray] = {
                "original": base_signal,
                "one_bar_lag": fast.shift_matrix(base_signal, 1),
                "wrong_lag_future_24h": fast.shift_matrix(base_signal, -24),
                "wrong_lag_stale_168h": fast.shift_matrix(base_signal, 168),
                "same_family_random": rng.normal(size=base_signal.shape),
            }
            for entry_label, label in labels.items():
                entry_variants = variants if entry_label == "label_t1_to_t25" else {
                    "original": variants["original"],
                    "one_bar_lag": variants["one_bar_lag"],
                }
                for variant, signal in entry_variants.items():
                    weights, spread, top_count, bottom_count = portfolio_weights_and_spread(signal, label)
                    metric_rows.extend(
                        split_metric_rows(cid, variant, entry_label, spread, weights, split, orientation, top_count, bottom_count)
                    )
                if entry_label == "label_t1_to_t25":
                    pass
        except Exception as exc:
            error_rows.append({"candidate_id": cid, "expression": expression, "error": repr(exc)})

    metric_frame = pd.DataFrame(metric_rows)
    overlap_frame = pd.DataFrame(overlap_rows)
    nonoverlap_frame = pd.DataFrame(nonoverlap_rows)
    orientation_frame = pd.DataFrame(orientation_rows)
    if metric_frame.empty:
        generated["selected_for_fast_replay"] = generated["candidate_id"].isin(set(selected["candidate_id"]))
        generated.to_csv(OUT_DIR / "a7al2q_generated_candidates.csv", index=False)
        selected.to_csv(OUT_DIR / "a7al2q_selected_for_fast_replay.csv", index=False)
        replay_selected.to_csv(OUT_DIR / "a7al2q_executed_fast_replay_candidates.csv", index=False)
        metric_frame.to_csv(OUT_DIR / "a7al2q_fast_replay_metrics.csv", index=False)
        pd.DataFrame(error_rows).to_csv(OUT_DIR / "a7al2q_eval_errors.csv", index=False)
        manifest = {
            "generated_at": utc_now(),
            "decision": "HOLD_A7AL2Q_EVAL_ERRORS",
            "generated_total": int(len(generated)),
            "selected_for_fast_replay": int(len(selected)),
            "executed_fast_replay": int(len(replay_selected)),
            "candidate_eval_errors": len(error_rows),
            "blockers": ["no_fast_replay_metric_rows"],
            "warnings": [],
            "runtime_seconds": round(time.time() - start, 3),
            "executes_local_search": True,
            "executes_training": False,
            "executes_alpha_proof": False,
            "authorizes_large_search": False,
            "authorizes_alpha_proof": False,
            "authorizes_shadow_paper_live": False,
        }
        write_json(OUT_DIR / "a7al2q_manifest.json", manifest)
        write_json(OUT_DIR / "a7al2q_decision_record.json", manifest)
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(
            "# CRYPTO A7AL-2Q Local OI Price Formula Search\n\n"
            f"Generated: {manifest['generated_at']}\n\n"
            "## Decision\n\n```text\nHOLD_A7AL2Q_EVAL_ERRORS\n```\n\n"
            "No fast replay metric rows were produced. See runtime/a7al2q_local_oi_price_formula_search/a7al2q_eval_errors.csv.\n",
            encoding="utf-8",
        )
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return
    control_gate = control_ratio_by_split(metric_frame) if not metric_frame.empty else pd.DataFrame()
    empty_latent = pd.DataFrame(
        columns=[
            "candidate_id",
            "variant",
            "entry_label",
            "split",
            "n_dates",
            "mean_oriented_spread",
            "hourly_tstat_naive",
            "positive_rate",
            "avg_one_way_turnover",
            "avg_top_count",
            "avg_bottom_count",
            "net_mean_spread_2bps",
            "net_mean_spread_5bps",
            "net_mean_spread_10bps",
        ]
    )
    latent_coverage = {"deferred_to": "A7AL-2R local deep forensic", "latent_audit_cap": LATENT_AUDIT_CAP}
    latent_frame = pd.DataFrame(latent_metric_rows)
    decisions = classify_candidates(replay_selected, metric_frame, latent_frame, control_gate, overlap_frame) if not metric_frame.empty else pd.DataFrame()
    scoreboard = replay_selected.merge(decisions, on="candidate_id", how="left")
    scoreboard = scoreboard.sort_values("selector_score_no_may", ascending=False)
    deep = scoreboard.head(DEEP_AUDIT).copy()

    decision_counts = decisions["decision"].value_counts().rename_axis("decision").reset_index(name="count") if not decisions.empty else pd.DataFrame(columns=["decision", "count"])
    candidate_count = int(decisions["decision"].eq("A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE").sum()) if not decisions.empty else 0
    control_dominated_count = int(decisions["decision"].eq("HOLD_A7AL2Q_CONTROL_DOMINATED").sum()) if not decisions.empty else 0
    skeleton_top_share = float(selected["skeleton_key"].value_counts(normalize=True).iloc[0]) if not selected.empty else np.nan
    selected_skeleton_count = int(selected["skeleton_key"].nunique()) if not selected.empty else 0
    blockers: list[str] = []
    warnings_out: list[str] = []
    if error_rows:
        blockers.append("candidate_eval_errors")
    if candidate_count == 0:
        blockers.append("no_local_oi_price_diagnostic_candidate")
    if control_dominated_count:
        warnings_out.append("control_dominated_candidates_rejected")
    if skeleton_top_share > 0.20:
        warnings_out.append("selected_top_skeleton_share_above_20pct")

    if error_rows:
        decision = "HOLD_A7AL2Q_EVAL_ERRORS"
    elif candidate_count > 0:
        decision = "PASS_A7AL2Q_LOCAL_OI_PRICE_CANDIDATES_FOUND_EXECUTION_HOLD"
    elif control_dominated_count:
        decision = "HOLD_A7AL2Q_CONTROL_DOMINATED"
    else:
        decision = "HOLD_A7AL2Q_NO_LOCAL_CANDIDATE"

    generated["selected_for_fast_replay"] = generated["candidate_id"].isin(set(selected["candidate_id"]))
    generated.to_csv(OUT_DIR / "a7al2q_generated_candidates.csv", index=False)
    selected.to_csv(OUT_DIR / "a7al2q_selected_for_fast_replay.csv", index=False)
    replay_selected.to_csv(OUT_DIR / "a7al2q_executed_fast_replay_candidates.csv", index=False)
    metric_frame.to_csv(OUT_DIR / "a7al2q_fast_replay_metrics.csv", index=False)
    control_gate.to_csv(OUT_DIR / "a7al2q_control_dominance.csv", index=False)
    orientation_frame.to_csv(OUT_DIR / "a7al2q_latency_label_alignment.csv", index=False)
    latent_frame.to_csv(OUT_DIR / "a7al2q_timevarying_latent_metrics.csv", index=False)
    overlap_frame.to_csv(OUT_DIR / "a7al2q_overlap_robust_tstats.csv", index=False)
    nonoverlap_frame.to_csv(OUT_DIR / "a7al2q_nonoverlap_offset_tstats.csv", index=False)
    metric_frame[
        [
            "candidate_id",
            "variant",
            "entry_label",
            "split",
            "avg_one_way_turnover",
            "net_mean_spread_2bps",
            "net_mean_spread_5bps",
            "net_mean_spread_10bps",
        ]
    ].to_csv(OUT_DIR / "a7al2q_cost_proxy.csv", index=False)
    scoreboard.to_csv(OUT_DIR / "a7al2q_candidate_scoreboard.csv", index=False)
    deep.to_csv(OUT_DIR / "a7al2q_deep_audit_scoreboard.csv", index=False)
    pd.DataFrame(error_rows).to_csv(OUT_DIR / "a7al2q_eval_errors.csv", index=False)
    reject_summary = decisions["decision"].value_counts().rename_axis("decision").reset_index(name="count") if not decisions.empty else decision_counts
    reject_summary.to_csv(OUT_DIR / "a7al2q_reject_reason_summary.csv", index=False)

    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_contract": str(P2_MANIFEST),
        "seed_candidates": seeds["candidate_id"].astype(str).tolist(),
        "generated_total": int(len(generated)),
        "selected_for_fast_replay": int(len(selected)),
        "executed_fast_replay": int(len(replay_selected)),
        "deep_audit": int(len(deep)),
        "diagnostic_candidate_count": candidate_count,
        "decision_counts": {str(r["decision"]): int(r["count"]) for _, r in decision_counts.iterrows()},
        "blockers": blockers,
        "warnings": warnings_out,
        "strict_symbols": len(loaded_symbols),
        "timestamps": int(len(timestamps)),
        "fields_loaded": sorted(all_fields),
        "latency_policy": "field-native; no blanket +2h stress; label_t1 and label_t2 are audit labels",
        "orientation_fit_split": "train_2024",
        "uses_may_for_selection": False,
        "uses_may_for_generation": False,
        "uses_may_for_ranking": False,
        "uses_may_for_mutation": False,
        "selected_skeleton_count": selected_skeleton_count,
        "selected_top_skeleton_share": skeleton_top_share,
        "controls": [
            "one_bar_lag",
            "wrong_lag_future_24h",
            "wrong_lag_stale_168h",
            "same_family_random",
        ],
        "controls_deferred_to_deep_forensic": ["time_shuffle", "symbol_shuffle"],
        "cost_bps": COST_BPS,
        "latent_coverage": latent_coverage,
        "runtime_seconds": round(time.time() - start, 3),
        "executes_local_search": True,
        "executes_training": False,
        "executes_alpha_proof": False,
        "authorizes_a7al2r_local_forensic": bool(candidate_count > 0 and not error_rows),
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(OUT_DIR / "a7al2q_manifest.json", manifest)
    write_json(
        OUT_DIR / "a7al2q_decision_record.json",
        {
            "decision": decision,
            "generated_at": manifest["generated_at"],
            "diagnostic_candidate_count": candidate_count,
            "blockers": blockers,
            "warnings": warnings_out,
            "authorizes_a7al2r_local_forensic": manifest["authorizes_a7al2r_local_forensic"],
            "authorizes_large_search": False,
            "authorizes_alpha_proof": False,
            "authorizes_shadow_paper_live": False,
        },
    )

    report = f"""# CRYPTO A7AL-2Q Local OI Price Formula Search

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This is a local OI-price search around the two A7AL-2P1S clean seeds. It executes no training, no large search, no alpha proof, and no shadow/paper/live authorization.

## Scope

```text
generated_total: {len(generated)}
selected_for_fast_replay: {len(selected)}
executed_fast_replay: {len(replay_selected)}
deep_audit: {len(deep)}
seed_count: {len(seeds)}
orientation_fit_split: train_2024
May usage: stress/reporting only; not used for generation, ranking, mutation, or selector score
```

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Decision Counts

{md_table(decision_counts, 40)}

## Deep Audit Scoreboard

{md_table(deep[["candidate_id", "expression", "pattern_id", "windows", "parent_seed_id", "decision", "reasons", "warnings", "selector_score_no_may", "control_ratio_premay_max_by_split", "recent_net_mean_spread_10bps", "recent_turnover"]] if not deep.empty else deep, 40)}

## Selector Diversity

```text
selected_skeleton_count: {selected_skeleton_count}
selected_top_skeleton_share: {skeleton_top_share:.6f}
```

## Boundary

```text
Allowed:
  local diagnostic candidate follow-up if decision is PASS_A7AL2Q_LOCAL_OI_PRICE_CANDIDATES_FOUND_EXECUTION_HOLD

Not authorized:
  large search
  alpha proof
  shadow / paper / live
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
