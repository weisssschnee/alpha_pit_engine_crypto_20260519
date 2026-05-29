from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7ab4_materialization_preflight import (  # noqa: E402
    A7AB4Evaluator,
    load_numeric_fields,
    shift_matrix,
)
from scripts.crypto_a7al2l_fast_derived_replay_preflight import (  # noqa: E402
    SPLIT_END,
    SPLIT_ORDER,
    split_for_timestamps,
)


RUNTIME = REPO / "runtime" / "a7ab6_small_numeric_replay_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7AB6_SMALL_NUMERIC_REPLAY_PREFLIGHT_20260529.md"

A7AB5_MANIFEST = REPO / "runtime" / "a7ab5_numeric_replay_contract" / "a7ab5_manifest.json"
A7AB5_QUEUE = REPO / "runtime" / "a7ab5_numeric_replay_contract" / "a7ab5_replay_contract_queue.csv"

HOURS_PER_SPLIT = 720
MIN_ACTIVE_SYMBOLS = 30
PRE_MAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
LABELS = ["L7_ranked_future_return", "L1_cross_sectional_relative_return", "L0_raw_forward_return"]
HORIZONS = [1, 4]
CONTROL_VARIANTS = [
    "one_bar_lag",
    "wrong_lag_future_1h",
    "wrong_lag_stale_24h",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_random",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def split_pipe(value: Any) -> list[str]:
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]


def selected_fields(selected: pd.DataFrame) -> set[str]:
    fields = {"trade_close"}
    for text in selected["source_fields"].dropna().astype(str):
        fields.update(split_pipe(text))
    return fields


def subset_indices_by_split(timestamps: pd.DatetimeIndex) -> np.ndarray:
    split = split_for_timestamps(timestamps)
    selected: list[int] = []
    for split_name in SPLIT_ORDER:
        idx = np.where(split == split_name)[0]
        if len(idx):
            selected.extend(idx[-HOURS_PER_SPLIT:].tolist())
    return np.array(sorted(set(selected)), dtype=int)


def subset_columns(
    timestamps: pd.DatetimeIndex,
    numeric: dict[str, np.ndarray],
) -> tuple[pd.DatetimeIndex, dict[str, np.ndarray], np.ndarray, int]:
    idx = subset_indices_by_split(timestamps)
    split = split_for_timestamps(timestamps[idx])
    return pd.DatetimeIndex(timestamps[idx]), {key: value[:, idx] for key, value in numeric.items()}, split, int(len(timestamps))


def forward_return_label(trade_close: np.ndarray, timestamps: pd.DatetimeIndex, split: np.ndarray, horizon: int) -> np.ndarray:
    close = np.where(trade_close > 0, trade_close, np.nan)
    log_close = np.log(close)
    label = shift_matrix(log_close, -int(horizon)) - log_close
    label_end = timestamps + pd.Timedelta(hours=int(horizon))
    for split_name in SPLIT_ORDER:
        if split_name not in SPLIT_END:
            continue
        mask = (split == split_name) & (label_end > SPLIT_END[split_name])
        label[:, mask] = np.nan
    label[:, split == "out_of_scope"] = np.nan
    return label


def cs_rank_pct(values: np.ndarray) -> np.ndarray:
    return pd.DataFrame(values).rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)


def label_matrix(label_family: str, horizon: int, trade_close: np.ndarray, timestamps: pd.DatetimeIndex, split: np.ndarray) -> np.ndarray:
    raw = forward_return_label(trade_close, timestamps, split, horizon)
    if label_family == "L0_raw_forward_return":
        return raw
    if label_family == "L1_cross_sectional_relative_return":
        with np.errstate(invalid="ignore"):
            mean = np.nanmean(raw, axis=0, keepdims=True)
        return raw - mean
    if label_family == "L7_ranked_future_return":
        return cs_rank_pct(raw) - 0.5
    raise ValueError(f"unsupported label family: {label_family}")


def spread_series(signal: np.ndarray, label: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    valid = np.isfinite(signal) & np.isfinite(label)
    valid_counts = valid.sum(axis=0)
    enough = valid_counts >= MIN_ACTIVE_SYMBOLS
    sig = np.where(valid, signal, np.nan)
    ranks = pd.DataFrame(sig).rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)
    top = valid & enough.reshape(1, -1) & (ranks >= 0.90)
    bottom = valid & enough.reshape(1, -1) & (ranks <= 0.10)
    top_count = top.sum(axis=0)
    bottom_count = bottom.sum(axis=0)
    spread = np.full(signal.shape[1], np.nan)
    ok = (top_count > 0) & (bottom_count > 0)
    spread[ok] = (
        np.where(top, label, 0.0).sum(axis=0)[ok] / top_count[ok]
        - np.where(bottom, label, 0.0).sum(axis=0)[ok] / bottom_count[ok]
    )
    return spread, valid_counts


def tstat(values: np.ndarray) -> float:
    x = values[np.isfinite(values)]
    if len(x) < 3:
        return np.nan
    std = np.nanstd(x, ddof=1)
    if not np.isfinite(std) or std <= 0:
        return np.nan
    return float(np.nanmean(x) / std * math.sqrt(len(x)))


def nonoverlap_tstats(values: np.ndarray, mask: np.ndarray, horizon: int) -> tuple[float, float]:
    stats: list[float] = []
    step = max(1, int(horizon))
    idx = np.where(mask & np.isfinite(values))[0]
    for offset in range(step):
        sub = idx[idx % step == offset]
        if len(sub) >= 3:
            stats.append(tstat(values[sub]))
    finite = [x for x in stats if np.isfinite(x)]
    if not finite:
        return np.nan, np.nan
    return float(np.nanmedian(finite)), float(np.nanmin(finite))


def variant_signals(base_signal: np.ndarray, rng: np.random.Generator) -> dict[str, np.ndarray]:
    return {
        "original": base_signal,
        "one_bar_lag": shift_matrix(base_signal, 1),
        "wrong_lag_future_1h": shift_matrix(base_signal, -1),
        "wrong_lag_stale_24h": shift_matrix(base_signal, 24),
        "time_shuffle": base_signal.reshape(-1)[rng.permutation(base_signal.size)].reshape(base_signal.shape),
        "symbol_shuffle": base_signal[rng.permutation(base_signal.shape[0]), :],
        "same_family_random": rng.normal(size=base_signal.shape),
    }


def summarize_variant(
    candidate_id: str,
    family_id: str,
    label_family: str,
    horizon: int,
    variant: str,
    signal: np.ndarray,
    label: np.ndarray,
    split: np.ndarray,
) -> list[dict[str, Any]]:
    spread, valid_counts = spread_series(signal, label)
    rows: list[dict[str, Any]] = []
    for split_name in SPLIT_ORDER:
        mask = (split == split_name) & np.isfinite(spread)
        x = spread[mask]
        median_nonoverlap, min_nonoverlap = nonoverlap_tstats(spread, split == split_name, horizon=horizon)
        rows.append(
            {
                "candidate_id": candidate_id,
                "family_id": family_id,
                "label_family": label_family,
                "horizon_h": horizon,
                "variant": variant,
                "split": split_name,
                "n_dates": int(mask.sum()),
                "avg_n_obs": float(np.nanmean(valid_counts[mask])) if mask.any() else np.nan,
                "mean_spread": float(np.nanmean(x)) if len(x) else np.nan,
                "spread_tstat": tstat(x) if len(x) else np.nan,
                "nonoverlap_median_tstat": median_nonoverlap,
                "nonoverlap_min_tstat": min_nonoverlap,
                "positive_rate": float(np.nanmean(x > 0)) if len(x) else np.nan,
            }
        )
    return rows


def classify(metrics: pd.DataFrame, candidate_id: str, label_family: str, horizon: int) -> dict[str, Any]:
    sub = metrics[
        metrics["candidate_id"].eq(candidate_id)
        & metrics["label_family"].eq(label_family)
        & metrics["horizon_h"].eq(horizon)
    ]
    pivot = sub.pivot_table(index="variant", columns="split", values="mean_spread", aggfunc="first")

    def v(variant: str, split_name: str) -> float:
        try:
            return float(pivot.loc[variant, split_name])
        except Exception:
            return np.nan

    train = v("original", "train_2024")
    orientation = 1.0 if not np.isfinite(train) or train >= 0 else -1.0
    premay = [orientation * v("original", split_name) for split_name in PRE_MAY_SPLITS]
    premay_ok = all(np.isfinite(x) and x > 0 for x in premay)
    recent = orientation * v("original", "recent_oos_2026JanApr")
    lag_recent = orientation * v("one_bar_lag", "recent_oos_2026JanApr")
    lag_ok = np.isfinite(recent) and np.isfinite(lag_recent) and lag_recent > 0 and abs(lag_recent) >= 0.25 * abs(recent)
    ratios: list[float] = []
    for split_name in PRE_MAY_SPLITS:
        original_abs = abs(v("original", split_name))
        vals = [abs(v(control, split_name)) for control in CONTROL_VARIANTS if control != "one_bar_lag"]
        vals = [x for x in vals if np.isfinite(x)]
        if vals and np.isfinite(original_abs) and original_abs > 1e-12:
            ratios.append(max(vals) / original_abs)
    control_ratio = max(ratios) if ratios else np.nan
    control_clean = np.isfinite(control_ratio) and control_ratio < 1.0
    if not premay_ok:
        decision = "HOLD_A7AB6_PREMAY_UNSTABLE"
    elif not lag_ok:
        decision = "HOLD_A7AB6_ONE_BAR_LAG_FRAGILE"
    elif not control_clean:
        decision = "HOLD_A7AB6_CONTROL_DOMINATED"
    else:
        decision = "A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE"
    return {
        "candidate_id": candidate_id,
        "label_family": label_family,
        "horizon_h": horizon,
        "orientation_from_train": orientation,
        "premay_all_positive": premay_ok,
        "one_bar_lag_ok": lag_ok,
        "control_ratio_premay_max": control_ratio,
        "oriented_validation_spread": premay[0],
        "oriented_test_spread": premay[1],
        "oriented_recent_spread": premay[2],
        "decision": decision,
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ab5 = read_json(A7AB5_MANIFEST)
    if not a7ab5.get("authorizes_a7ab6_small_numeric_replay_preflight"):
        raise SystemExit("A7AB-5 does not authorize A7AB-6")
    queue = pd.read_csv(A7AB5_QUEUE)
    fields = selected_fields(queue)
    loaded_symbols, timestamps, numeric, missing, full_timestamp_count = load_numeric_fields(fields, timestamp_cap=None)
    if missing:
        raise SystemExit(f"missing fields: {missing}")
    timestamps, numeric, split, _ = subset_columns(timestamps, numeric)
    evaluator = A7AB4Evaluator(numeric, {})
    labels = {
        (label_family, horizon): label_matrix(label_family, horizon, numeric["trade_close"], timestamps, split)
        for label_family in LABELS
        for horizon in HORIZONS
    }
    rng = np.random.default_rng(20260529)
    metric_rows: list[dict[str, Any]] = []
    eval_errors: list[dict[str, Any]] = []
    for idx, row in enumerate(queue.to_dict("records"), start=1):
        candidate_id = str(row["candidate_id"])
        family_id = str(row["family_id"])
        expression = str(row["expression"])
        try:
            base_signal = evaluator.eval(expression)
            variants = variant_signals(base_signal, rng)
            for label_key, label in labels.items():
                label_family, horizon = label_key
                for variant, signal in variants.items():
                    metric_rows.extend(summarize_variant(candidate_id, family_id, label_family, horizon, variant, signal, label, split))
        except Exception as exc:  # noqa: BLE001
            eval_errors.append({"candidate_id": candidate_id, "error": repr(exc)})
        if idx % 16 == 0:
            print(f"[A7AB-6] replayed {idx}/{len(queue)}", flush=True)

    metrics = pd.DataFrame(metric_rows)
    decision_rows: list[dict[str, Any]] = []
    for row in queue.to_dict("records"):
        cid = str(row["candidate_id"])
        for label_family in LABELS:
            for horizon in HORIZONS:
                decision_rows.append(classify(metrics, cid, label_family, horizon))
    decisions = pd.DataFrame(decision_rows)
    best = decisions.sort_values(
        ["decision", "control_ratio_premay_max", "oriented_recent_spread"],
        ascending=[True, True, False],
    )
    clue = decisions[decisions["decision"].eq("A7AB6_SMALL_REPLAY_PREFLIGHT_CLUE")].copy()
    decision_counts = decisions["decision"].value_counts().rename_axis("decision").reset_index(name="count")
    clue_count = int(len(clue))
    clue_candidate_count = int(clue["candidate_id"].nunique()) if clue_count else 0
    if eval_errors:
        decision = "HOLD_A7AB6_EVAL_ERRORS"
    elif clue_count > 0:
        decision = "PASS_A7AB6_SMALL_NUMERIC_REPLAY_PREFLIGHT_CLUES_FOUND_EXECUTION_HOLD"
    else:
        decision = "HOLD_A7AB6_NO_CONTROL_CLEAN_CLUES"

    manifest = {
        "stage": "A7AB-6",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_small_numeric_replay_preflight": True,
        "executes_formula_generation": False,
        "executes_large_search": False,
        "executes_training": False,
        "uses_may": False,
        "input_queue_count": int(len(queue)),
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "full_timestamps_before_subset": int(full_timestamp_count),
        "hours_per_split": int(HOURS_PER_SPLIT),
        "labels": LABELS,
        "horizons": HORIZONS,
        "metric_rows": int(len(metrics)),
        "eval_error_count": int(len(eval_errors)),
        "decision_counts": {str(r["decision"]): int(r["count"]) for _, r in decision_counts.iterrows()},
        "clue_count": clue_count,
        "clue_candidate_count": clue_candidate_count,
        "authorizes_a7ab7_forensic_contract": bool(clue_count > 0 and not eval_errors),
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    metrics.to_csv(RUNTIME / "a7ab6_candidate_variant_metrics.csv", index=False)
    decisions.to_csv(RUNTIME / "a7ab6_candidate_label_decisions.csv", index=False)
    best.to_csv(RUNTIME / "a7ab6_ranked_decision_queue.csv", index=False)
    clue.to_csv(RUNTIME / "a7ab6_clue_queue.csv", index=False)
    pd.DataFrame(eval_errors).to_csv(RUNTIME / "a7ab6_eval_errors.csv", index=False)
    decision_counts.to_csv(RUNTIME / "a7ab6_decision_counts.csv", index=False)
    write_json(RUNTIME / "a7ab6_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ab6_authorization_matrix.json",
        {
            "A7AB-6": {"status": decision},
            "A7AB-7_forensic_contract": {"authorized": bool(clue_count > 0 and not eval_errors)},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AB-6 SMALL NUMERIC REPLAY PREFLIGHT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AB-6 is a bounded numeric replay preflight on A7AB-5 queue. It does not authorize formula search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Decision Counts",
        "",
        md_table(decision_counts),
        "",
        "## Clue Queue",
        "",
        md_table(clue.head(80)),
        "",
        "## Ranked Decision Queue Sample",
        "",
        md_table(best.head(80)),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
