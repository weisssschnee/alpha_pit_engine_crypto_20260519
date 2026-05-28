from __future__ import annotations

import importlib.util
import json
import math
import os
import re
import sys
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
GENERATOR_SCRIPT = REPO / "scripts" / "crypto_a7al2k_derived_generator_smoke.py"
A7AL2O_DECISIONS = REPO / "runtime" / "a7al2o_candidate_mini_replay" / "a7al2o_decision_record.csv"
A7AL2K_GENERATED = REPO / "runtime" / "a7al2k_derived_generator_smoke" / "a7al2k_generated_candidates.csv"
DATA_ROOT = Path(os.environ.get("ALPHAFACTORY_CRYPTO_DATA_ROOT", r"G:\AlphaFactory_CryptoData"))
LATENT_PANEL = Path(
    os.environ.get(
        "A7AL_LV1_PANEL",
        str(DATA_ROOT / "gold" / "features" / "binance_universe498_latent_state_features_v1_20260527.parquet"),
    )
)
OUT_DIR = REPO / "runtime" / "a7al2p0_pre_search_hardening_audit"
REPORT = REPO / "reports" / "CRYPTO_A7AL2P0_PRE_SEARCH_HARDENING_AUDIT_20260527.md"

PRE_MAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
AUDIT_SPLITS = PRE_MAY_SPLITS + ["known_may2026_stress"]
CONTROL_VARIANTS = ["wrong_lag_future_24h", "wrong_lag_stale_168h", "time_shuffle", "symbol_shuffle", "same_family_random"]
BLOCKED_OVERLAY_FIELDS = {
    "mark_basis_bps_okx_minus_binance",
    "index_spread_bps_okx_minus_binance",
    "okx_mark_close",
    "okx_index_close",
    "binance_mark_close",
    "binance_index_close",
    "binance_trade_close",
}
CANONICAL_OVERLAY_ALLOWLIST = {
    "funding_spread_okx_minus_binance",
    "okx_internal_mark_index_basis_bps",
    "binance_internal_mark_index_basis_bps",
    "oi_usd_spread_okx_minus_binance",
    "oi_usd_ratio_okx_over_binance",
    "oi_coin_ratio_okx_over_binance",
    "taker_ratio_spread_okx_minus_binance",
    "okx_contracts_taker_buy_share",
    "okx_contracts_taker_buy_sell_ratio",
    "oi_value_ratio_from_crowding_endpoint_okx_over_binance",
}


def load_fast_module() -> Any:
    spec = importlib.util.spec_from_file_location("a7al2l_fast", FAST_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {FAST_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fast = load_fast_module()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


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


def numeric(x: Any, default: float = np.nan) -> float:
    try:
        return float(x)
    except Exception:
        return default


def finite_tstat(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    if len(x) < 3:
        return np.nan
    std = np.nanstd(x, ddof=1)
    if not np.isfinite(std) or std <= 0:
        return np.nan
    return float(np.nanmean(x) / std * math.sqrt(len(x)))


def newey_west_tstat(x: np.ndarray, lag: int = 24) -> float:
    x = x[np.isfinite(x)]
    n = len(x)
    if n < lag + 5:
        return np.nan
    mu = float(np.mean(x))
    u = x - mu
    gamma0 = float(np.dot(u, u) / n)
    var = gamma0
    max_lag = min(lag, n - 2)
    for k in range(1, max_lag + 1):
        gamma = float(np.dot(u[k:], u[:-k]) / n)
        weight = 1.0 - k / (max_lag + 1)
        var += 2.0 * weight * gamma
    se = math.sqrt(var / n) if var > 0 else np.nan
    return float(mu / se) if np.isfinite(se) and se > 0 else np.nan


def block_bootstrap_tstat(x: np.ndarray, block: int = 24, reps: int = 300, seed: int = 20260527) -> float:
    x = x[np.isfinite(x)]
    n = len(x)
    if n < block * 4:
        return np.nan
    rng = np.random.default_rng(seed)
    means = []
    starts = np.arange(0, max(n - block + 1, 1))
    n_blocks = int(math.ceil(n / block))
    for _ in range(reps):
        chosen = rng.choice(starts, size=n_blocks, replace=True)
        sample = np.concatenate([x[s : s + block] for s in chosen])[:n]
        means.append(float(np.mean(sample)))
    std = float(np.std(means, ddof=1))
    return float(np.mean(x) / std) if std > 0 else np.nan


def label_matrix_entry_shift(trade_close: np.ndarray, timestamps: pd.DatetimeIndex, split: np.ndarray, entry_shift: int) -> np.ndarray:
    close = np.where(trade_close > 0, trade_close, np.nan)
    log_close = np.log(close)
    entry = fast.shift_matrix(log_close, -entry_shift)
    exit_ = fast.shift_matrix(log_close, -(entry_shift + 24))
    label = exit_ - entry
    label_end = timestamps + pd.Timedelta(hours=entry_shift + 24)
    for split_name in fast.SPLIT_ORDER:
        mask = (split == split_name) & (label_end > fast.SPLIT_END[split_name])
        label[:, mask] = np.nan
    label[:, split == "out_of_scope"] = np.nan
    return label


def portfolio_weights_and_spread(signal: np.ndarray, label: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
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
    return weights, spread


def split_metric_rows(candidate_id: str, variant: str, entry_label: str, spread: np.ndarray, split: np.ndarray, orientation: float) -> list[dict[str, Any]]:
    rows = []
    oriented = spread * orientation
    for split_name in fast.SPLIT_ORDER:
        mask = (split == split_name) & np.isfinite(oriented)
        x = oriented[mask]
        rows.append(
            {
                "candidate_id": candidate_id,
                "variant": variant,
                "entry_label": entry_label,
                "split": split_name,
                "n_dates": int(mask.sum()),
                "mean_oriented_spread": float(np.nanmean(x)) if len(x) else np.nan,
                "hourly_tstat_naive": finite_tstat(x),
                "positive_rate": float(np.nanmean(x > 0)) if len(x) else np.nan,
            }
        )
    return rows


def control_ratio_by_split(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (cid, entry_label, split_name), group in metrics.groupby(["candidate_id", "entry_label", "split"], dropna=False):
        try:
            original_abs = abs(float(group.loc[group["variant"].eq("original"), "mean_oriented_spread"].iloc[0]))
        except Exception:
            original_abs = np.nan
        controls = group[group["variant"].isin(CONTROL_VARIANTS)].copy()
        max_control_abs = float(controls["mean_oriented_spread"].abs().max()) if not controls.empty else np.nan
        ratio = max_control_abs / original_abs if np.isfinite(original_abs) and original_abs > 0 and np.isfinite(max_control_abs) else np.nan
        if np.isfinite(ratio) and ratio >= 1.0:
            gate = "HOLD_CONTROL_DOMINATED"
        elif np.isfinite(ratio) and ratio >= 0.8:
            gate = "WARN_CONTROL_CLOSE"
        else:
            gate = "ELIGIBLE_DIAGNOSTIC"
        rows.append(
            {
                "candidate_id": cid,
                "entry_label": entry_label,
                "split": split_name,
                "original_abs_spread": original_abs,
                "max_control_abs_spread": max_control_abs,
                "control_ratio": ratio,
                "gate": gate,
            }
        )
    return pd.DataFrame(rows)


def neutralize_timevarying_state(signal: np.ndarray, state_matrix: np.ndarray, min_group_symbols: int = 8) -> np.ndarray:
    out = np.full_like(signal, np.nan, dtype=np.float64)
    for col in range(signal.shape[1]):
        values = signal[:, col]
        states = state_matrix[:, col]
        finite = np.isfinite(values)
        if finite.sum() < fast.MIN_ACTIVE_SYMBOLS:
            continue
        for state in sorted(set(states[finite].astype(str))):
            if state in {"", "nan", "None", "__missing__"}:
                continue
            idx = np.where(finite & (states.astype(str) == state))[0]
            if len(idx) < min_group_symbols:
                continue
            sub = values[idx]
            std = float(np.nanstd(sub, ddof=1))
            if std > 0 and np.isfinite(std):
                out[idx, col] = (sub - float(np.nanmean(sub))) / std
    return out


def load_timevarying_latent_states(symbols: list[str], timestamps: pd.DatetimeIndex) -> tuple[np.ndarray, dict[str, Any]]:
    cols = ["symbol", "timestamp", "raw_latent_state_id", "state_seen_in_train"]
    frame = pd.read_parquet(LATENT_PANEL, columns=cols, engine="pyarrow")
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame[frame["symbol"].isin(symbols)]
    matrix = np.empty((len(symbols), len(timestamps)), dtype=object)
    matrix[:, :] = "__missing__"
    seen_matrix = np.zeros((len(symbols), len(timestamps)), dtype=bool)
    ts_index = pd.Index(timestamps)
    for i, symbol in enumerate(symbols):
        part = frame[frame["symbol"].eq(symbol)].sort_values("timestamp").drop_duplicates("timestamp")
        part = part.set_index("timestamp").reindex(ts_index)
        matrix[i, :] = part["raw_latent_state_id"].fillna("__missing__").astype(str).to_numpy()
        seen_matrix[i, :] = part["state_seen_in_train"].fillna(False).astype(bool).to_numpy()
    coverage = {
        "state_panel_path": str(LATENT_PANEL),
        "loaded_rows": int(len(frame)),
        "state_non_missing_share": float(np.mean(matrix != "__missing__")),
        "state_seen_in_train_share": float(seen_matrix.mean()),
    }
    return matrix, coverage


def nonoverlap_offset_rows(candidate_id: str, spread: np.ndarray, split: np.ndarray, orientation: float) -> list[dict[str, Any]]:
    rows = []
    oriented = spread * orientation
    for split_name in AUDIT_SPLITS:
        base_mask = (split == split_name) & np.isfinite(oriented)
        idx_all = np.where(base_mask)[0]
        for offset in range(24):
            idx = idx_all[(idx_all % 24) == offset]
            x = oriented[idx]
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "split": split_name,
                    "offset": offset,
                    "n_dates": int(len(x)),
                    "mean_spread": float(np.nanmean(x)) if len(x) else np.nan,
                    "tstat": finite_tstat(x),
                    "positive": bool(np.nanmean(x) > 0) if len(x) else False,
                }
            )
    return rows


def overlap_stat_rows(candidate_id: str, spread: np.ndarray, split: np.ndarray, orientation: float) -> list[dict[str, Any]]:
    rows = []
    oriented = spread * orientation
    for split_name in AUDIT_SPLITS:
        mask = (split == split_name) & np.isfinite(oriented)
        x = oriented[mask]
        rows.append(
            {
                "candidate_id": candidate_id,
                "split": split_name,
                "n_dates": int(len(x)),
                "mean_spread": float(np.nanmean(x)) if len(x) else np.nan,
                "hourly_tstat_naive": finite_tstat(x),
                "newey_west_tstat_lag24": newey_west_tstat(x, lag=24),
                "block_bootstrap_tstat_block24": block_bootstrap_tstat(x, block=24, reps=300),
            }
        )
    return rows


def expression_fields(expression: str) -> set[str]:
    ops = set(re.findall(r"\b([A-Z][A-Za-z0-9_]*)\s*\(", expression))
    tokens = set(re.findall(r"\b[a-z][a-z0-9_]*\b", expression))
    return tokens - {op.lower() for op in ops} - {"nan", "inf"}


def canonical_alias_audit() -> tuple[pd.DataFrame, pd.DataFrame]:
    script_text = GENERATOR_SCRIPT.read_text(encoding="utf-8")
    code_rows = []
    for field in sorted(BLOCKED_OVERLAY_FIELDS | CANONICAL_OVERLAY_ALLOWLIST):
        code_rows.append(
            {
                "field_name": field,
                "field_class": "blocked_direct_or_raw_price_comparison" if field in BLOCKED_OVERLAY_FIELDS else "canonical_allowed_overlay",
                "present_in_generator_code": field in script_text,
                "status": "FAIL" if field in BLOCKED_OVERLAY_FIELDS and field in script_text else "PASS",
            }
        )
    code_rows.append(
        {
            "field_name": "J5_silent_fallback_to_J0",
            "field_class": "silent_fallback",
            "present_in_generator_code": 'return self.expression_for_cell("J0_oi_derived_state")' in script_text,
            "status": "FAIL" if 'return self.expression_for_cell("J0_oi_derived_state")' in script_text else "PASS",
        }
    )
    artifact_rows = []
    if A7AL2K_GENERATED.exists():
        generated = pd.read_csv(A7AL2K_GENERATED)
        for _, row in generated.iterrows():
            fields = expression_fields(str(row.get("expression", "")))
            bad = sorted(fields & BLOCKED_OVERLAY_FIELDS)
            if bad:
                artifact_rows.append(
                    {
                        "candidate_id": row.get("candidate_id"),
                        "cell": row.get("cell"),
                        "expression": row.get("expression"),
                        "blocked_fields": "|".join(bad),
                        "selected_for_replay": row.get("selected_for_a7al2l_replay_preflight"),
                        "diagnostic_only": row.get("diagnostic_only"),
                    }
                )
    return pd.DataFrame(code_rows), pd.DataFrame(artifact_rows)


def selector_score_components(candidates: pd.DataFrame, label_metrics: pd.DataFrame, control_gate: pd.DataFrame, latent_metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in candidates.iterrows():
        cid = str(row["candidate_id"])
        original = label_metrics[
            label_metrics["candidate_id"].eq(cid)
            & label_metrics["variant"].eq("original")
            & label_metrics["entry_label"].eq("label_t1_to_t25")
            & label_metrics["split"].isin(PRE_MAY_SPLITS)
        ]
        orig_score = float(original["mean_oriented_spread"].mean()) if len(original) else np.nan
        onebar = label_metrics[
            label_metrics["candidate_id"].eq(cid)
            & label_metrics["variant"].eq("one_bar_lag")
            & label_metrics["entry_label"].eq("label_t1_to_t25")
            & label_metrics["split"].eq("recent_oos_2026JanApr")
        ]
        recent_orig = original[original["split"].eq("recent_oos_2026JanApr")]
        lag_survival = (
            float(onebar["mean_oriented_spread"].iloc[0] / recent_orig["mean_oriented_spread"].iloc[0])
            if not onebar.empty and not recent_orig.empty and numeric(recent_orig["mean_oriented_spread"].iloc[0]) != 0
            else np.nan
        )
        control_part = control_gate[
            control_gate["candidate_id"].eq(cid)
            & control_gate["entry_label"].eq("label_t1_to_t25")
            & control_gate["split"].isin(PRE_MAY_SPLITS)
        ]
        max_control_ratio = float(control_part["control_ratio"].max()) if len(control_part) else np.nan
        latent_part = latent_metrics[
            latent_metrics["candidate_id"].eq(cid)
            & latent_metrics["variant"].eq("timevarying_latent_state_neutral")
            & latent_metrics["entry_label"].eq("label_t1_to_t25")
            & latent_metrics["split"].isin(PRE_MAY_SPLITS)
        ]
        latent_survival = int(pd.to_numeric(latent_part["mean_oriented_spread"], errors="coerce").gt(0).sum()) if len(latent_part) else 0
        diversity_bonus = 1.0
        score = (
            np.nan_to_num(orig_score, nan=0.0)
            + 0.0005 * np.nan_to_num(lag_survival, nan=0.0)
            + 0.0002 * latent_survival
            + 0.0001 * diversity_bonus
            - 0.0007 * np.nan_to_num(max_control_ratio, nan=1.0)
        )
        rows.append(
            {
                "candidate_id": cid,
                "non_may_original_spread_score": orig_score,
                "entry_shift_aligned_label": "label_t1_to_t25",
                "one_bar_lag_survival_recent": lag_survival,
                "control_dominance_margin": 1.0 - max_control_ratio if np.isfinite(max_control_ratio) else np.nan,
                "timevarying_latent_positive_premay_splits": latent_survival,
                "family": row.get("family"),
                "cell": row.get("cell"),
                "field_families": row.get("field_families"),
                "replay_aware_selector_score_no_may": score,
                "uses_may": False,
            }
        )
    return pd.DataFrame(rows).sort_values("replay_aware_selector_score_no_may", ascending=False)


def replay_aware_selector_contract(selector_components: pd.DataFrame, blockers: list[str], warnings: list[str]) -> dict[str, Any]:
    top = selector_components.head(10)
    hard_gate_status = {
        "matched_control_dominance": "HOLD" if "matched_control_dominance_hard_gate_fail" in blockers else "PASS",
        "timevarying_latent_neutralization": "HOLD" if "timevarying_latent_neutralization_fragile" in blockers else "PASS",
        "canonical_field_alias_code": "HOLD" if "canonical_alias_code_fail" in blockers else "PASS",
        "candidate_eval": "HOLD" if "candidate_eval_errors" in blockers else "PASS",
    }
    return {
        "contract_name": "A7AR-5 replay-aware selector adapter",
        "generated_at": utc_now(),
        "status": "DRY_ADAPTER_ONLY",
        "decision": "HOLD_A7AR5_REPLAY_SELECTOR_NOT_AUTHORIZED" if blockers else "PASS_A7AR5_REPLAY_SELECTOR_DRY_CONTRACT_READY",
        "score_components_no_may": [
            "non_may_original_spread",
            "entry_shift_aligned_spread_label_t1_to_t25",
            "matched_control_dominance_margin_by_split",
            "one_bar_lag_survival_recent",
            "timevarying_latent_neutralization_survival",
            "cost_proxy_placeholder_from_replay_family",
            "family_skeleton_cell_diversity",
        ],
        "hard_gates": {
            "split_control_ratio_gte_1_00": "HOLD_CONTROL_DOMINATED",
            "split_control_ratio_0_80_to_1_00": "WARN_CONTROL_CLOSE",
            "canonical_contract_unit_fields_only": True,
            "j5_overlay_silent_fallback_forbidden": True,
            "timevarying_latent_state_neutralization_required": True,
            "label_entry_alignment_required": ["label_t_to_t24", "label_t1_to_t25", "label_t2_to_t26"],
            "overlap_robust_stats_required": ["newey_west_lag24", "block_bootstrap_block24", "nonoverlap_offset_tstats"],
        },
        "forbidden_inputs": [
            "May score",
            "May ranking",
            "May threshold tuning",
            "May weight selection",
            "May generator tuning",
            "May selector score",
            "shadow/paper/live promotion labels",
        ],
        "allowed_use": [
            "diagnostic candidate ordering",
            "pre-search selector implementation audit",
            "A7AL-2P contract drafting input after all hard blockers are cleared",
        ],
        "not_authorized": [
            "A7AL-2 formula search execution",
            "alpha proof",
            "shadow",
            "paper",
            "live",
        ],
        "blockers": blockers,
        "warnings": warnings,
        "hard_gate_status": hard_gate_status,
        "top_dry_selector_candidates": top[
            [
                "candidate_id",
                "replay_aware_selector_score_no_may",
                "non_may_original_spread_score",
                "control_dominance_margin",
                "one_bar_lag_survival_recent",
                "timevarying_latent_positive_premay_splits",
                "family",
                "cell",
            ]
        ].to_dict(orient="records"),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = pd.read_csv(A7AL2O_DECISIONS)
    candidates = candidates[candidates["mini_replay_label"].eq("A7AL2O_MINI_REPLAY_DIAGNOSTIC_PASS")].copy()
    if candidates.empty:
        raise SystemExit("A7AL-2O has no diagnostic pass candidates")

    # Preserve expression and orientation from A7AL-2N summary.
    a7al2n = pd.read_csv(REPO / "runtime" / "a7al2n_derived_deep_audit" / "a7al2n_deep_candidate_summary.csv")
    candidates = candidates.merge(
        a7al2n[["candidate_id", "expression", "fields", "orientation_from_premay"]],
        on="candidate_id",
        how="left",
    )

    fields = {"trade_close"}
    for text in candidates["fields"].dropna().astype(str):
        fields.update(part for part in text.split("|") if part)
    symbols = fast.strict_symbols()
    loaded_symbols, timestamps, matrices = fast.load_panel_matrices(symbols, fields)
    split = fast.split_for_timestamps(timestamps)
    evaluator = fast.MatrixFormulaEvaluator(matrices, field_shift=0)
    labels = {
        "label_t_to_t24": label_matrix_entry_shift(matrices["trade_close"], timestamps, split, 0),
        "label_t1_to_t25": label_matrix_entry_shift(matrices["trade_close"], timestamps, split, 1),
        "label_t2_to_t26": label_matrix_entry_shift(matrices["trade_close"], timestamps, split, 2),
    }
    rng = np.random.default_rng(20260527)
    state_matrix, latent_coverage = load_timevarying_latent_states(loaded_symbols, timestamps)

    label_rows: list[dict[str, Any]] = []
    overlap_rows: list[dict[str, Any]] = []
    nonoverlap_rows: list[dict[str, Any]] = []
    latent_rows: list[dict[str, Any]] = []
    eval_errors: list[dict[str, Any]] = []

    for _, row in candidates.iterrows():
        cid = str(row["candidate_id"])
        expression = str(row["expression"])
        orientation = numeric(row["orientation_from_premay"], 1.0)
        print(f"[A7AL-2P0] {cid}", flush=True)
        try:
            base_signal = evaluator.eval(expression)
            variants = {
                "original": base_signal,
                "one_bar_lag": fast.shift_matrix(base_signal, 1),
                "wrong_lag_future_24h": fast.MatrixFormulaEvaluator(matrices, field_shift=-24).eval(expression),
                "wrong_lag_stale_168h": fast.MatrixFormulaEvaluator(matrices, field_shift=168).eval(expression),
                "time_shuffle": base_signal.reshape(-1)[rng.permutation(base_signal.size)].reshape(base_signal.shape),
                "symbol_shuffle": np.take_along_axis(base_signal, rng.permutation(base_signal.shape[0])[:, None], axis=0),
                "same_family_random": rng.normal(size=base_signal.shape),
            }
            for entry_label, label in labels.items():
                for variant, signal in variants.items():
                    _, spread = portfolio_weights_and_spread(signal, label)
                    label_rows.extend(split_metric_rows(cid, variant, entry_label, spread, split, orientation))
                _, original_spread = portfolio_weights_and_spread(base_signal, label)
                if entry_label == "label_t1_to_t25":
                    overlap_rows.extend(overlap_stat_rows(cid, original_spread, split, orientation))
                    nonoverlap_rows.extend(nonoverlap_offset_rows(cid, original_spread, split, orientation))
                    latent_signal = neutralize_timevarying_state(base_signal, state_matrix)
                    _, latent_spread = portfolio_weights_and_spread(latent_signal, label)
                    latent_rows.extend(split_metric_rows(cid, "timevarying_latent_state_neutral", entry_label, latent_spread, split, orientation))
        except Exception as exc:
            eval_errors.append({"candidate_id": cid, "error": repr(exc)})

    label_metrics = pd.DataFrame(label_rows)
    control_gate = control_ratio_by_split(label_metrics)
    overlap_stats = pd.DataFrame(overlap_rows)
    nonoverlap_stats = pd.DataFrame(nonoverlap_rows)
    latent_metrics = pd.DataFrame(latent_rows)
    code_alias_audit, stale_alias_artifacts = canonical_alias_audit()
    selector_components = selector_score_components(candidates, label_metrics, control_gate, latent_metrics)

    control_block_rows = control_gate[
        control_gate["split"].isin(PRE_MAY_SPLITS)
        & control_gate["entry_label"].eq("label_t1_to_t25")
        & control_gate["gate"].eq("HOLD_CONTROL_DOMINATED")
    ].copy()
    label_alignment_summary = label_metrics[
        label_metrics["variant"].eq("original")
        & label_metrics["split"].isin(PRE_MAY_SPLITS)
    ].pivot_table(index=["candidate_id", "entry_label"], values="mean_oriented_spread", columns="split", aggfunc="first").reset_index()
    label_alignment_summary["premay_positive_splits"] = label_alignment_summary[PRE_MAY_SPLITS].gt(0).sum(axis=1)
    latent_recent = latent_metrics[latent_metrics["split"].eq("recent_oos_2026JanApr")]
    latent_block_rows = latent_recent[pd.to_numeric(latent_recent["mean_oriented_spread"], errors="coerce").le(0)].copy()
    overlap_recent = overlap_stats[overlap_stats["split"].eq("recent_oos_2026JanApr")]
    weak_overlap_rows = overlap_recent[pd.to_numeric(overlap_recent["newey_west_tstat_lag24"], errors="coerce").abs().lt(2.0)].copy()

    blockers: list[str] = []
    warnings: list[str] = []
    if eval_errors:
        blockers.append("candidate_eval_errors")
    if not code_alias_audit[code_alias_audit["status"].eq("FAIL")].empty:
        blockers.append("canonical_alias_code_fail")
    if not stale_alias_artifacts.empty:
        warnings.append("stale_a7al2k_artifacts_contain_blocked_overlay_aliases_rerun_required_before_j5_use")
    if not control_block_rows.empty:
        blockers.append("matched_control_dominance_hard_gate_fail")
    if not latent_block_rows.empty:
        blockers.append("timevarying_latent_neutralization_fragile")
    if not weak_overlap_rows.empty:
        warnings.append("overlap_adjusted_recent_tstat_below_2_for_some_candidates")

    decision = "PASS_A7AL2P0_PRE_SEARCH_IMPLEMENTATION_HARDENED" if not blockers else "HOLD_A7AL2P0_PRE_SEARCH_HARDENING_BLOCKERS"
    a7ar5_contract = replay_aware_selector_contract(selector_components, blockers, warnings)
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "candidate_count": int(len(candidates)),
        "blockers": blockers,
        "warnings": warnings,
        "eval_errors": len(eval_errors),
        "p0_1_label_alignment": "computed label_t_to_t24, label_t1_to_t25, label_t2_to_t26",
        "p0_2_canonical_alias": "generator code patched; stale generated artifacts audited separately",
        "p0_3_control_gate": "control_ratio >= 1.00 is HOLD by split",
        "p0_4_overlap_stats": "hourly naive, 24h non-overlap offset, Newey-West lag24, block bootstrap block24",
        "p0_5_timevarying_latent": latent_coverage,
        "p0_6_replay_selector": "A7AR-5 dry replay-aware selector contract and score generated without May",
        "a7ar5_contract_decision": a7ar5_contract["decision"],
        "authorizes_a7al2p_contract": not blockers,
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_training": False,
        "executes_search": False,
        "executes_alpha_proof": False,
    }

    label_metrics.to_csv(OUT_DIR / "a7al2p0_label_execution_alignment.csv", index=False)
    label_alignment_summary.to_csv(OUT_DIR / "a7al2p0_label_alignment_summary.csv", index=False)
    code_alias_audit.to_csv(OUT_DIR / "a7al2p0_canonical_field_alias_code_audit.csv", index=False)
    stale_alias_artifacts.to_csv(OUT_DIR / "a7al2p0_stale_artifact_alias_violations.csv", index=False)
    control_gate.to_csv(OUT_DIR / "a7al2p0_matched_control_gate_by_split.csv", index=False)
    overlap_stats.to_csv(OUT_DIR / "a7al2p0_overlap_robust_tstats.csv", index=False)
    nonoverlap_stats.to_csv(OUT_DIR / "a7al2p0_nonoverlap_offset_tstats.csv", index=False)
    latent_metrics.to_csv(OUT_DIR / "a7al2p0_timevarying_latent_neutralization.csv", index=False)
    selector_components.to_csv(OUT_DIR / "a7al2p0_replay_aware_selector_score_components.csv", index=False)
    selector_components.to_csv(OUT_DIR / "a7ar5_replay_aware_selector_score_components.csv", index=False)
    pd.DataFrame(eval_errors).to_csv(OUT_DIR / "a7al2p0_eval_errors.csv", index=False)
    write_json(OUT_DIR / "a7al2p0_manifest.json", manifest)
    write_json(OUT_DIR / "a7ar5_replay_aware_selector_contract.json", a7ar5_contract)

    report = f"""# CRYPTO A7AL-2P0 Pre-Search Implementation Hardening Audit

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This stage fixes/audits implementation risks before any A7AL-2 search contract. It executes no training, no generation, no search, and no alpha proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## P0-1 Label / Execution Alignment

{md_table(label_alignment_summary, 40)}

## P0-2 Canonical Field Alias Audit

{md_table(code_alias_audit, 40)}

Stale generated artifacts with blocked aliases:

{md_table(stale_alias_artifacts[["candidate_id", "cell", "blocked_fields", "selected_for_replay", "diagnostic_only"]] if not stale_alias_artifacts.empty else stale_alias_artifacts, 40)}

## P0-3 Matched-Control Hard Gate

{md_table(control_gate[control_gate["entry_label"].eq("label_t1_to_t25") & control_gate["split"].isin(PRE_MAY_SPLITS)], 80)}

## P0-4 Overlap-Robust Statistics

{md_table(overlap_stats, 40)}

## P0-5 Time-Varying Latent Neutralization

{md_table(latent_metrics[latent_metrics["split"].isin(PRE_MAY_SPLITS + ["known_may2026_stress"])], 60)}

## P0-6 Replay-Aware Selector Dry Components

{md_table(selector_components, 40)}

## A7AR-5 Replay-Aware Selector Contract

```json
{json.dumps(a7ar5_contract, indent=2, sort_keys=True)}
```

## Boundary

```text
Not authorized:
  A7AL-2 execution
  formula search execution
  alpha proof
  shadow / paper / live
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
