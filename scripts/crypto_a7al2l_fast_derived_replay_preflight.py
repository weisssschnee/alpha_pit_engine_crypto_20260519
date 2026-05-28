from __future__ import annotations

import json
import math
import os
import re
import sys
import time
import warnings
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.feature_algebra import parse_call


DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
BASE_DIR = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v2_20260527"
SPLIT_COVERAGE = REPO / "runtime" / "a7al0_top498_alpha_search_contract" / "a7al_split_coverage_by_symbol.csv"
A7AL2K_SELECTED = REPO / "runtime" / "a7al2k_derived_generator_smoke" / "a7al2k_selected_candidates.csv"
A7AL2K_MANIFEST = REPO / "runtime" / "a7al2k_derived_generator_smoke" / "a7al2k_manifest.json"
OUT_DIR = REPO / "runtime" / "a7al2l_fast_derived_replay_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7AL2L_FAST_DERIVED_REPLAY_PREFLIGHT_20260527.md"

PRIMARY_LABEL = "fwd_ret_24h"
MIN_ACTIVE_SYMBOLS = 30
DEFAULT_REPLAY_CAP = 192
SPLIT_ORDER = [
    "train_2024",
    "validation_2025H1",
    "test_2025H2",
    "recent_oos_2026JanApr",
    "known_may2026_stress",
]
SPLIT_END = {
    "train_2024": pd.Timestamp("2024-12-31 23:00:00+00:00"),
    "validation_2025H1": pd.Timestamp("2025-06-30 23:00:00+00:00"),
    "test_2025H2": pd.Timestamp("2025-12-31 23:00:00+00:00"),
    "recent_oos_2026JanApr": pd.Timestamp("2026-04-30 23:00:00+00:00"),
    "known_may2026_stress": pd.Timestamp("2026-05-26 00:00:00+00:00"),
}
CONTROL_VARIANTS = [
    "one_bar_lag",
    "wrong_lag_future_24h",
    "wrong_lag_stale_168h",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_random",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def strict_symbols() -> list[str]:
    cov = pd.read_csv(SPLIT_COVERAGE)
    return (
        cov.loc[cov["search_eligibility"].eq("strict_full_history"), "symbol"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .tolist()
    )


def select_replay_candidates(candidates: pd.DataFrame, cap: int) -> pd.DataFrame:
    selected = candidates[candidates["selected_for_a7al2l_replay_preflight"].astype(bool)].copy()
    buckets = {
        str(cell): group.sort_values(["skeleton_key", "candidate_id"]).reset_index(drop=True)
        for cell, group in selected.groupby("cell", sort=True)
    }
    cursors = {cell: 0 for cell in buckets}
    rows: list[pd.Series] = []
    skeleton_counts: Counter[str] = Counter()
    field_family_counts: Counter[str] = Counter()
    while len(rows) < cap:
        changed = False
        for cell in sorted(buckets):
            group = buckets[cell]
            while cursors[cell] < len(group):
                row = group.iloc[cursors[cell]]
                cursors[cell] += 1
                skeleton = str(row["skeleton_key"])
                families = [f for f in str(row["field_families"]).split("|") if f]
                if skeleton_counts[skeleton] >= 8:
                    continue
                if any(field_family_counts[f] >= int(cap * 0.35) for f in families):
                    continue
                rows.append(row)
                skeleton_counts[skeleton] += 1
                for family in families:
                    field_family_counts[family] += 1
                changed = True
                break
            if len(rows) >= cap:
                break
        if not changed:
            break
    return pd.DataFrame(rows).reset_index(drop=True) if rows else selected.head(0)


def fields_from_selected(selected: pd.DataFrame) -> set[str]:
    fields: set[str] = {"trade_close"}
    for text in selected["fields"].dropna().astype(str):
        fields.update(part for part in text.split("|") if part)
    return fields


def shift_matrix(values: np.ndarray, periods: int) -> np.ndarray:
    out = np.full_like(values, np.nan, dtype=np.float64)
    if periods == 0:
        return values.astype(np.float64, copy=True)
    if periods > 0:
        out[:, periods:] = values[:, :-periods]
    else:
        p = abs(periods)
        out[:, :-p] = values[:, p:]
    return out


def rolling_mean(values: np.ndarray, window: int) -> np.ndarray:
    w = max(1, int(window))
    min_periods = max(2, min(w, 24))
    valid = np.isfinite(values)
    x = np.where(valid, values, 0.0)
    csum = np.concatenate([np.zeros((x.shape[0], 1), dtype=np.float64), np.cumsum(x, axis=1)], axis=1)
    ccnt = np.concatenate([np.zeros((x.shape[0], 1), dtype=np.float64), np.cumsum(valid.astype(np.float64), axis=1)], axis=1)
    end = np.arange(1, x.shape[1] + 1)
    start = np.maximum(0, end - w)
    total = csum[:, end] - csum[:, start]
    count = ccnt[:, end] - ccnt[:, start]
    out = np.full_like(values, np.nan, dtype=np.float64)
    np.divide(total, count, out=out, where=count >= min_periods)
    out[count < min_periods] = np.nan
    return out


def cs_zscore(values: np.ndarray) -> np.ndarray:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        mean = np.nanmean(values, axis=0, keepdims=True)
        std = np.nanstd(values, axis=0, ddof=1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        out = (values - mean) / std
    out[~np.isfinite(out)] = np.nan
    return out


def cs_rank_pct(values: np.ndarray) -> np.ndarray:
    frame = pd.DataFrame(values)
    return frame.rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)


class MatrixFormulaEvaluator:
    def __init__(self, fields: dict[str, np.ndarray], field_shift: int = 0) -> None:
        self.fields = fields
        self.field_shift = int(field_shift)
        self.cache: dict[str, np.ndarray] = {}

    def eval(self, expression: str) -> np.ndarray:
        key = f"{self.field_shift}:{expression}"
        if key in self.cache:
            return self.cache[key]
        result = self._eval(expression.strip())
        self.cache[key] = result
        return result

    def _eval(self, expression: str) -> np.ndarray:
        call = parse_call(expression)
        if call is None:
            if expression not in self.fields:
                raise ValueError(f"unknown field: {expression}")
            return shift_matrix(self.fields[expression], self.field_shift)

        name, args = call
        if name == "Mean":
            return rolling_mean(self.eval(args[0]), int(args[1]))
        if name == "Delta":
            values = self.eval(args[0])
            return values - shift_matrix(values, int(args[1]))
        if name in {"Rank", "CSRank"}:
            return cs_rank_pct(self.eval(args[0]))
        if name == "ZScore":
            return cs_zscore(self.eval(args[0]))
        if name == "Mul":
            return self.eval(args[0]) * self.eval(args[1])
        if name == "Sub":
            return self.eval(args[0]) - self.eval(args[1])
        if name == "Add":
            return self.eval(args[0]) + self.eval(args[1])
        if name == "Neg":
            return -self.eval(args[0])
        if name == "Abs":
            return np.abs(self.eval(args[0]))
        if name == "Sign":
            return np.sign(self.eval(args[0]))
        raise ValueError(f"unsupported operator: {name}")


def load_panel_matrices(symbols: list[str], fields: set[str]) -> tuple[list[str], pd.DatetimeIndex, dict[str, np.ndarray]]:
    loaded_symbols: list[str] = []
    timestamps: pd.DatetimeIndex | None = None
    per_symbol: dict[str, pd.DataFrame] = {}
    cols = ["timestamp"] + sorted(fields)
    for symbol in symbols:
        path = BASE_DIR / f"symbol={symbol}" / "part.parquet"
        if not path.exists():
            continue
        frame = pd.read_parquet(path, columns=[c for c in cols if c != "symbol"], engine="pyarrow")
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        frame = frame.sort_values("timestamp").drop_duplicates("timestamp")
        if timestamps is None:
            timestamps = pd.DatetimeIndex(frame["timestamp"])
        frame = frame.set_index("timestamp").reindex(timestamps)
        per_symbol[symbol] = frame
        loaded_symbols.append(symbol)
    if timestamps is None or not loaded_symbols:
        raise RuntimeError("no symbols loaded")
    matrices: dict[str, np.ndarray] = {}
    for field in sorted(fields):
        matrices[field] = np.vstack(
            [pd.to_numeric(per_symbol[symbol][field], errors="coerce").to_numpy(dtype=np.float64) for symbol in loaded_symbols]
        )
    return loaded_symbols, timestamps, matrices


def split_for_timestamps(timestamps: pd.DatetimeIndex) -> np.ndarray:
    split = np.full(len(timestamps), "out_of_scope", dtype=object)
    ts = pd.Series(timestamps)
    split[ts.le(SPLIT_END["train_2024"]).to_numpy()] = "train_2024"
    split[(ts.gt(SPLIT_END["train_2024"]) & ts.le(SPLIT_END["validation_2025H1"])).to_numpy()] = "validation_2025H1"
    split[(ts.gt(SPLIT_END["validation_2025H1"]) & ts.le(SPLIT_END["test_2025H2"])).to_numpy()] = "test_2025H2"
    split[(ts.gt(SPLIT_END["test_2025H2"]) & ts.le(SPLIT_END["recent_oos_2026JanApr"])).to_numpy()] = "recent_oos_2026JanApr"
    split[(ts.gt(SPLIT_END["recent_oos_2026JanApr"]) & ts.le(SPLIT_END["known_may2026_stress"])).to_numpy()] = "known_may2026_stress"
    return split


def label_matrix(trade_close: np.ndarray, timestamps: pd.DatetimeIndex, split: np.ndarray) -> np.ndarray:
    close = np.where(trade_close > 0, trade_close, np.nan)
    log_close = np.log(close)
    label = shift_matrix(log_close, -24) - log_close
    label_end = timestamps + pd.Timedelta(hours=24)
    for split_name in SPLIT_ORDER:
        mask = (split == split_name) & (label_end > SPLIT_END[split_name])
        label[:, mask] = np.nan
    label[:, split == "out_of_scope"] = np.nan
    return label


def split_spread(signal: np.ndarray, label: np.ndarray, split: np.ndarray) -> tuple[pd.DataFrame, dict[str, Any]]:
    valid = np.isfinite(signal) & np.isfinite(label)
    valid_rows = int(valid.sum())
    if valid_rows == 0:
        return pd.DataFrame(), {"valid_rows": 0, "valid_row_share": 0.0}
    valid_counts = valid.sum(axis=0)
    enough = valid_counts >= MIN_ACTIVE_SYMBOLS
    if not enough.any():
        return pd.DataFrame(), {"valid_rows": valid_rows, "valid_row_share": float(valid_rows / valid.size)}

    sig = np.where(valid, signal, np.nan)
    q10 = np.full(sig.shape[1], np.nan)
    q90 = np.full(sig.shape[1], np.nan)
    cols = np.where(enough)[0]
    if len(cols):
        with np.errstate(all="ignore"):
            q10[cols] = np.nanpercentile(sig[:, cols], 10, axis=0)
            q90[cols] = np.nanpercentile(sig[:, cols], 90, axis=0)
    top_mask = valid & enough.reshape(1, -1) & (signal >= q90.reshape(1, -1))
    bottom_mask = valid & enough.reshape(1, -1) & (signal <= q10.reshape(1, -1))
    top_sum = np.where(top_mask, label, 0.0).sum(axis=0)
    bottom_sum = np.where(bottom_mask, label, 0.0).sum(axis=0)
    top_count = top_mask.sum(axis=0)
    bottom_count = bottom_mask.sum(axis=0)
    spread = np.full(signal.shape[1], np.nan)
    ok = (top_count > 0) & (bottom_count > 0)
    spread[ok] = (top_sum[ok] / top_count[ok]) - (bottom_sum[ok] / bottom_count[ok])
    rows: list[dict[str, Any]] = []
    for split_name in SPLIT_ORDER:
        mask = (split == split_name) & np.isfinite(spread)
        x = spread[mask]
        if len(x) == 0:
            rows.append(
                {
                    "split": split_name,
                    "n_dates": 0,
                    "avg_n_obs": np.nan,
                    "valid_rows": valid_rows,
                    "valid_row_share": float(valid_rows / valid.size),
                    "mean_spread_24h": np.nan,
                    "spread_tstat": np.nan,
                    "positive_spread_rate": np.nan,
                }
            )
            continue
        std = np.nanstd(x, ddof=1)
        tstat = float(np.nanmean(x) / std * math.sqrt(len(x))) if np.isfinite(std) and std > 0 and len(x) >= 3 else np.nan
        rows.append(
            {
                "split": split_name,
                "n_dates": int(mask.sum()),
                "avg_n_obs": float(np.nanmean(valid_counts[mask])),
                "valid_rows": valid_rows,
                "valid_row_share": float(valid_rows / valid.size),
                "mean_spread_24h": float(np.nanmean(x)),
                "spread_tstat": tstat,
                "positive_spread_rate": float(np.nanmean(x > 0)),
            }
        )
    return pd.DataFrame(rows), {"valid_rows": valid_rows, "valid_row_share": float(valid_rows / valid.size)}


def classify_candidate(metrics: pd.DataFrame, candidate_id: str) -> dict[str, Any]:
    pivot = metrics[metrics["candidate_id"].eq(candidate_id)].pivot_table(
        index="variant", columns="split", values="mean_spread_24h", aggfunc="first"
    )

    def v(variant: str, split: str) -> float:
        try:
            return float(pivot.loc[variant, split])
        except Exception:
            return np.nan

    original = [v("original", s) for s in ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]]
    finite_original = [x for x in original if np.isfinite(x) and abs(x) > 1e-10]
    sign_stable = len(finite_original) == 3 and len({np.sign(x) for x in finite_original}) == 1
    min_abs = min(abs(x) for x in finite_original) if finite_original else 0.0
    recent = v("original", "recent_oos_2026JanApr")
    lag_recent = v("one_bar_lag", "recent_oos_2026JanApr")
    lag_ok = np.isfinite(lag_recent) and np.isfinite(recent) and np.sign(lag_recent) == np.sign(recent) and abs(lag_recent) >= 0.25 * abs(recent)
    ratios = []
    for split_name in ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]:
        vals = [abs(v(c, split_name)) for c in CONTROL_VARIANTS if c != "one_bar_lag"]
        vals = [x for x in vals if np.isfinite(x)]
        original_abs = abs(v("original", split_name))
        if vals and np.isfinite(original_abs) and original_abs > 0:
            ratios.append(max(vals) / original_abs)
    control_dominance_ratio = max(ratios) if ratios else np.nan
    may = v("original", "known_may2026_stress")
    if not sign_stable:
        decision = "HOLD_A7AL2L_UNSTABLE_PRE_MAY"
    elif not lag_ok:
        decision = "HOLD_A7AL2L_ONE_BAR_LAG_FRAGILE"
    elif np.isfinite(control_dominance_ratio) and control_dominance_ratio >= 1.25:
        decision = "HOLD_A7AL2L_CONTROL_DOMINATED"
    elif min_abs < 0.00012:
        decision = "HOLD_A7AL2L_TOO_WEAK"
    else:
        decision = "A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE"
    return {
        "candidate_id": candidate_id,
        "original_validation_spread": v("original", "validation_2025H1"),
        "original_test_spread": v("original", "test_2025H2"),
        "original_recent_spread": recent,
        "original_may_stress_spread": may,
        "one_bar_lag_recent_spread": lag_recent,
        "control_dominance_ratio_premay_max": control_dominance_ratio,
        "sign_stable_pre_may": sign_stable,
        "lag_ok": lag_ok,
        "min_abs_premay_spread": min_abs,
        "decision": decision,
    }


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_k = read_json(A7AL2K_MANIFEST)
    if manifest_k.get("decision") != "PASS_A7AL2K_DERIVED_GENERATOR_SMOKE_READY_FOR_A7AL2L":
        raise SystemExit("A7AL-2K is not ready for A7AL-2L")
    cap = int(os.environ.get("A7AL2L_REPLAY_CAP", str(DEFAULT_REPLAY_CAP)))
    target_ids = [
        part.strip()
        for part in os.environ.get("A7AL2L_TARGET_IDS", "").split(",")
        if part.strip()
    ]
    all_selected = pd.read_csv(A7AL2K_SELECTED)
    if target_ids:
        selected = all_selected[all_selected["candidate_id"].astype(str).isin(target_ids)].copy()
        selected["_target_order"] = selected["candidate_id"].astype(str).map({cid: i for i, cid in enumerate(target_ids)})
        selected = selected.sort_values("_target_order").drop(columns=["_target_order"]).reset_index(drop=True)
        missing_targets = [cid for cid in target_ids if cid not in set(selected["candidate_id"].astype(str))]
        if missing_targets:
            raise SystemExit(f"A7AL2L_TARGET_IDS missing from A7AL-2K selected pool: {missing_targets}")
    else:
        selected = select_replay_candidates(all_selected, cap)
    symbols = strict_symbols()
    max_symbols = int(os.environ.get("A7AL2L_MAX_SYMBOLS", "0") or "0")
    if max_symbols > 0:
        symbols = symbols[:max_symbols]
    fields = set()
    for text in selected["fields"].dropna().astype(str):
        fields.update(part for part in text.split("|") if part)
    fields.add("trade_close")
    loaded_symbols, timestamps, matrices = load_panel_matrices(symbols, fields)
    split = split_for_timestamps(timestamps)
    label = label_matrix(matrices["trade_close"], timestamps, split)
    rng = np.random.default_rng(20260527)

    metric_rows: list[dict[str, Any]] = []
    error_rows: list[dict[str, Any]] = []
    for i, row in selected.iterrows():
        candidate_id = str(row["candidate_id"])
        expression = str(row["expression"])
        print(f"[A7AL-2L-fast] {i + 1}/{len(selected)} {candidate_id}", flush=True)
        try:
            evaluator = MatrixFormulaEvaluator(matrices, field_shift=0)
            base_signal = evaluator.eval(expression)
            variants: dict[str, np.ndarray] = {
                "original": base_signal,
                "one_bar_lag": shift_matrix(base_signal, 1),
                "time_shuffle": base_signal.reshape(-1)[rng.permutation(base_signal.size)].reshape(base_signal.shape),
                "symbol_shuffle": np.take_along_axis(base_signal, rng.permutation(base_signal.shape[0])[:, None], axis=0),
                "same_family_random": rng.normal(size=base_signal.shape),
                "wrong_lag_future_24h": MatrixFormulaEvaluator(matrices, field_shift=-24).eval(expression),
                "wrong_lag_stale_168h": MatrixFormulaEvaluator(matrices, field_shift=168).eval(expression),
            }
            for variant, signal in variants.items():
                summary, _coverage = split_spread(signal, label, split)
                for _, r in summary.iterrows():
                    row_out = r.to_dict()
                    row_out["candidate_id"] = candidate_id
                    row_out["variant"] = variant
                    metric_rows.append(row_out)
        except Exception as exc:
            error_rows.append({"candidate_id": candidate_id, "error": repr(exc)})

    metrics = pd.DataFrame(metric_rows)
    decisions = pd.DataFrame([classify_candidate(metrics, cid) for cid in selected["candidate_id"].astype(str)]) if not metrics.empty else pd.DataFrame()
    if not decisions.empty:
        decisions = decisions.merge(
            selected[["candidate_id", "cell", "family", "field_families", "fields", "operators", "windows", "feature_role"]],
            on="candidate_id",
            how="left",
        )
    decision_counts = decisions["decision"].value_counts().rename_axis("decision").reset_index(name="count") if not decisions.empty else pd.DataFrame(columns=["decision", "count"])
    clue_count = int(decisions["decision"].eq("A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE").sum()) if not decisions.empty else 0
    blockers = []
    warning_flags = []
    if error_rows:
        blockers.append("candidate_eval_errors")
    if clue_count == 0:
        blockers.append("no_derived_replay_preflight_clues")
    if not decisions.empty and int(decisions["decision"].eq("HOLD_A7AL2L_CONTROL_DOMINATED").sum()):
        warning_flags.append("control_dominated_candidates_rejected")

    decision = "PASS_A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUES_FOUND_EXECUTION_HOLD" if clue_count > 0 and not error_rows else "HOLD_A7AL2L_NO_CLEAN_CLUES"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_base": str(BASE_DIR),
        "strict_symbols": len(loaded_symbols),
        "max_symbols_env": max_symbols,
        "timestamps": int(len(timestamps)),
        "matrix_rows": int(len(loaded_symbols) * len(timestamps)),
        "selected_from_a7al2k": int(len(selected)),
        "replay_cap": cap,
        "target_ids": target_ids,
        "target_replay_mode": bool(target_ids),
        "candidate_eval_errors": len(error_rows),
        "derived_replay_preflight_clue_count": clue_count,
        "decision_counts": {str(r["decision"]): int(r["count"]) for _, r in decision_counts.iterrows()},
        "blockers": blockers,
        "warnings": warning_flags,
        "controls": ["one_bar_lag", "wrong_lag_future_24h", "wrong_lag_stale_168h", "time_shuffle", "symbol_shuffle", "same_family_random"],
        "runtime_seconds": round(time.time() - start, 3),
        "engine": "matrix_fast_preflight",
        "executes_formula_generation": False,
        "executes_replay_preflight": True,
        "executes_alpha_proof": False,
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    selected.to_csv(OUT_DIR / "a7al2l_fast_replayed_candidates.csv", index=False)
    metrics.to_csv(OUT_DIR / "a7al2l_fast_candidate_variant_metrics.csv", index=False)
    decisions.to_csv(OUT_DIR / "a7al2l_fast_candidate_decisions.csv", index=False)
    pd.DataFrame(error_rows).to_csv(OUT_DIR / "a7al2l_fast_eval_errors.csv", index=False)
    write_json(OUT_DIR / "a7al2l_fast_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2L Fast Derived Replay Preflight

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This is a matrix-level replay preflight on A7AL-2K derived-tolerant generated candidates. It does not authorize alpha proof, large search, shadow, paper, or live.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Decision Counts

{md_table(decision_counts, 40)}

## Candidate Decisions

{md_table(decisions[["candidate_id", "cell", "family", "field_families", "decision", "original_validation_spread", "original_test_spread", "original_recent_spread", "original_may_stress_spread", "one_bar_lag_recent_spread", "control_dominance_ratio_premay_max"]] if not decisions.empty else decisions, 80)}

## Boundary

```text
Allowed interpretation:
  A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE means a derived structure deserves controlled follow-up.

Not authorized:
  alpha proof
  shadow / paper / live
  large formula search
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
