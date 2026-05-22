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
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
PANEL_PATH = DATA_ROOT / "gold" / "panels" / "crypto_core12_1h_with_aggtrades_features_v1.parquet"
A7V3_DIR = ROOT / "runtime" / "a7v3_agg_aware_candidate_dry_run"
A7V4_DIR = ROOT / "runtime" / "a7v4_control_preflight"
OUT_DIR = ROOT / "runtime" / "a7v5_small_replay_smoke"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7V5_SMALL_REPLAY_SMOKE_20260522.md"

CORE3 = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
SPLITS = {
    "train_2024": ("2024-01-01T00:00:00Z", "2024-12-31T23:00:00Z"),
    "validation_2025H1": ("2025-01-01T00:00:00Z", "2025-06-30T23:00:00Z"),
    "recent_oos_2025H2_2026Apr": ("2025-07-01T00:00:00Z", "2026-04-30T23:00:00Z"),
    "fresh_may_2026": ("2026-05-01T00:00:00Z", None),
}
PRIMARY_COST_BPS = 10.0
SEVERE_COST_BPS = 20.0


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


def rolling_std(arr: np.ndarray, window: int) -> np.ndarray:
    return pd.DataFrame(arr).rolling(window, min_periods=window).std(ddof=0).to_numpy(dtype=float)


def rolling_min(arr: np.ndarray, window: int) -> np.ndarray:
    return pd.DataFrame(arr).rolling(window, min_periods=window).min().to_numpy(dtype=float)


def rolling_max(arr: np.ndarray, window: int) -> np.ndarray:
    return pd.DataFrame(arr).rolling(window, min_periods=window).max().to_numpy(dtype=float)


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
    return pd.DataFrame(arr).ewm(span=max(2, window), min_periods=window).mean().to_numpy(dtype=float)


def relative_to_symbol(arr: np.ndarray, symbols: list[str], symbol: str) -> np.ndarray:
    if symbol not in symbols:
        return np.full_like(arr, np.nan)
    base = arr[:, [symbols.index(symbol)]]
    return arr - base


def share_of_universe(arr: np.ndarray) -> np.ndarray:
    denom = np.nansum(np.abs(arr), axis=1, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.divide(arr, denom, out=np.full_like(arr, np.nan), where=denom > 1e-12)
    return out


class ExprContext:
    def __init__(self, matrices: dict[str, np.ndarray], symbols: list[str]):
        self.matrices = matrices
        self.symbols = symbols
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
        if op == "ShareOfUniverse":
            return share_of_universe(self.eval(args[0]))
        if op == "RelativeToBTC":
            return relative_to_symbol(self.eval(args[0]), self.symbols, "BTCUSDT")
        if op == "RelativeToETH":
            return relative_to_symbol(self.eval(args[0]), self.symbols, "ETHUSDT")
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
        if op == "Clip":
            return np.clip(self.eval(args[0]), to_scalar(args[1]), to_scalar(args[2]))
        if op == "Abs":
            return np.abs(self.eval(args[0]))
        if op == "Neg":
            return -self.eval(args[0])
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
        raise ValueError(f"unsupported operator: {op}")


def choose_candidates() -> pd.DataFrame:
    candidates = pd.read_csv(A7V3_DIR / "a7v3_candidates.csv")
    accepted = candidates[candidates["decision"].eq("A7V3_DRY_RUN_CANDIDATE")].copy()
    selected = []
    for family, quota in {
        "rolling_self_reproduction": 12,
        "cross_symbol_self_reproduction_core3": 12,
        "interaction_self_reproduction": 12,
    }.items():
        part = accepted[accepted["production_family"].eq(family)].copy()
        part = part.sort_values(["source_field_families", "transform", "window_hours", "candidate_id"])
        selected.append(part.head(quota))
    out = pd.concat(selected, ignore_index=True)
    return out


def load_replay_controls(selected_candidates: pd.DataFrame) -> pd.DataFrame:
    controls = pd.read_csv(A7V4_DIR / "a7v4_replay_control_specs.csv")
    return controls[controls["base_candidate_id"].isin(set(selected_candidates["candidate_id"]))].copy()


def required_columns(selected: pd.DataFrame) -> list[str]:
    fields = {"symbol", "timestamp", "open", "close", "agg_features_available"}
    for text in selected["source_fields"].dropna().astype(str):
        for item in text.split(";"):
            if item:
                fields.add(item)
    for field in ["mark_index_ratio", "premium_index", "latest_known_funding_rate", "realized_vol_12", "realized_vol_24", "ret_6", "ret_12"]:
        fields.add(field)
    return sorted(fields)


def load_panel(selected: pd.DataFrame) -> tuple[pd.DatetimeIndex, list[str], dict[str, np.ndarray]]:
    cols = required_columns(selected)
    df = pd.read_parquet(PANEL_PATH, columns=cols)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df[df["symbol"].isin(CORE3)].sort_values(["timestamp", "symbol"]).copy()
    index = pd.DatetimeIndex(sorted(df["timestamp"].unique()))
    symbols = CORE3
    matrices: dict[str, np.ndarray] = {}
    for col in cols:
        if col in {"symbol", "timestamp"}:
            continue
        pivot = df.pivot(index="timestamp", columns="symbol", values=col).reindex(index=index, columns=symbols)
        matrices[col] = pivot.to_numpy(dtype=float)
    matrices["agg_available_float"] = np.asarray(matrices["agg_features_available"], dtype=float)
    return index, symbols, matrices


def forward_open_return(open_mat: np.ndarray, horizon: int) -> np.ndarray:
    out = np.full_like(open_mat, np.nan, dtype=float)
    start = 1
    end = 1 + int(horizon)
    if end < open_mat.shape[0]:
        out[:-end, :] = open_mat[end:, :] / open_mat[start : open_mat.shape[0] - int(horizon), :] - 1.0
    return out


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
    out[(n < 3) | ~np.isfinite(out)] = np.nan
    return out


def top_bottom_book(signal: np.ndarray, target: np.ndarray, orientation: float, cost_bps: float) -> dict[str, np.ndarray]:
    oriented = signal * orientation
    valid = np.isfinite(oriented) & np.isfinite(target)
    pos = np.zeros_like(target, dtype=float)
    for i in range(target.shape[0]):
        idx = np.where(valid[i])[0]
        if len(idx) < 3:
            continue
        order = idx[np.argsort(oriented[i, idx])]
        short_idx = order[0]
        long_idx = order[-1]
        pos[i, long_idx] = 0.5
        pos[i, short_idx] = -0.5
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


def summarize_series(index: pd.DatetimeIndex, split: str, signal: np.ndarray, target: np.ndarray, book: dict[str, np.ndarray]) -> dict[str, Any]:
    mask = split_mask(index, split)
    ic = row_ic(signal[mask], target[mask])
    net = book["net"][mask]
    gross_exp = book["gross_exposure"][mask]
    return {
        "split": split,
        "rows": int(mask.sum()),
        "active_hours": int(np.sum(np.isfinite(net) & (gross_exp > 0))),
        "mean_ic": clean_float(np.nanmean(ic)),
        "net_sum_10bps": clean_float(np.nansum(net)),
        "net_mean_10bps": clean_float(np.nanmean(net)),
        "turnover_mean": clean_float(np.nanmean(book["turnover"][mask])),
        "gross_exposure_mean": clean_float(np.nanmean(gross_exp)),
    }


def evaluate_row(index: pd.DatetimeIndex, matrices: dict[str, np.ndarray], ctx: ExprContext, row: pd.Series, object_type: str, control_mode: str = "original") -> tuple[list[dict[str, Any]], dict[str, Any]]:
    expr = str(row["expression"])
    horizon = int(row["horizon"])
    agg_mask = matrices["agg_features_available"].astype(bool)
    base_signal = np.where(agg_mask, ctx.eval(expr), np.nan)
    target = forward_open_return(matrices["open"], horizon)
    train_mask = split_mask(index, "train_2024")
    base_train_ic = np.nanmean(row_ic(base_signal[train_mask], target[train_mask]))
    orientation = 1.0 if not np.isfinite(base_train_ic) or base_train_ic >= 0 else -1.0

    signal = base_signal
    if control_mode != "original":
        signal = apply_control(signal, control_mode, str(row.get("control_id", row.get("candidate_id", ""))))
        # Controls may permute or lag valid values into rows where agg data is
        # unavailable. Re-apply the PIT availability mask after every control
        # transform so null windows cannot become synthetic stress evidence.
        signal = np.where(agg_mask, signal, np.nan)
    train_ic = np.nanmean(row_ic(signal[train_mask], target[train_mask]))
    book10 = top_bottom_book(signal, target, orientation, PRIMARY_COST_BPS)
    book20 = top_bottom_book(signal, target, orientation, SEVERE_COST_BPS)

    metric_rows = []
    for split in SPLITS:
        m = summarize_series(index, split, signal, target, book10)
        m.update(
            {
                "candidate_id": str(row.get("candidate_id", row.get("control_id"))),
                "base_candidate_id": str(row.get("base_candidate_id", row.get("candidate_id", ""))),
                "object_type": object_type,
                "control_mode": control_mode,
                "production_family": str(row["production_family"]),
                "expression": expr,
                "horizon": horizon,
                "orientation": orientation,
                "base_train_ic_for_orientation": clean_float(base_train_ic),
                "variant_train_ic": clean_float(train_ic),
                "net_sum_20bps": clean_float(np.nansum(book20["net"][split_mask(index, split)])),
            }
        )
        metric_rows.append(m)
    meta = {
        "candidate_id": str(row.get("candidate_id", row.get("control_id"))),
        "object_type": object_type,
        "control_mode": control_mode,
        "eval_error": "",
    }
    return metric_rows, meta


def label_candidates(metrics: pd.DataFrame) -> pd.DataFrame:
    pivot = metrics.pivot_table(index=["candidate_id", "object_type", "control_mode", "production_family"], columns="split", values=["net_sum_10bps", "mean_ic", "active_hours"], aggfunc="first")
    pivot.columns = [f"{a}__{b}" for a, b in pivot.columns]
    pivot = pivot.reset_index()
    fresh_active = pivot.get("active_hours__fresh_may_2026", pd.Series(0, index=pivot.index)).fillna(0)
    pivot["fresh_may_status"] = np.where(fresh_active.gt(0), "HAS_MAY_AGG_DATA_STRESS_ONLY", "UNAVAILABLE_BY_DATA_COVERAGE")
    pivot["validation_positive"] = pivot.get("net_sum_10bps__validation_2025H1", 0).fillna(0).gt(0)
    pivot["recent_positive"] = pivot.get("net_sum_10bps__recent_oos_2025H2_2026Apr", 0).fillna(0).gt(0)
    pivot["control_non_promotable"] = pivot["object_type"].ne("candidate")
    pivot["smoke_label"] = np.where(
        pivot["object_type"].eq("candidate") & pivot["validation_positive"] & pivot["recent_positive"],
        "A7V5_SIGNAL_SMOKE_POSITIVE_NOT_PROOF",
        np.where(pivot["object_type"].eq("candidate"), "A7V5_SIGNAL_SMOKE_WEAK_OR_NEGATIVE", "A7V5_CONTROL_NON_PROMOTABLE"),
    )
    return pivot


def write_report(now: str, metrics: pd.DataFrame, labels: pd.DataFrame, controls: pd.DataFrame, eval_failures: pd.DataFrame, authorization: dict[str, Any]) -> None:
    split_summary = (
        metrics.groupby(["object_type", "control_mode", "split"])
        .agg(rows=("candidate_id", "count"), mean_net_sum_10bps=("net_sum_10bps", "mean"), median_ic=("mean_ic", "median"), mean_active_hours=("active_hours", "mean"))
        .reset_index()
    )
    label_summary = labels.groupby(["object_type", "control_mode", "smoke_label", "fresh_may_status"]).size().reset_index(name="rows")
    lines = [
        "# Crypto A7V-5 Small Agg-Aware Replay Smoke",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `small_smoke_only`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7V-5 evaluates a capped subset of A7V-3 candidates and A7V-4 replay controls on the unified core12 panel, restricted to core3 rows where agg features are available. It uses a core3 top1/bottom1 smoke book, not the legacy core12 top3/bottom3 book.",
        "",
        "Fresh May is reported strictly as post-selection stress when agg rows are present. It is not used for candidate selection, orientation, ranking, or authorization.",
        "",
        "## Label Summary",
        "",
        table(label_summary, max_rows=80),
        "",
        "## Split Summary",
        "",
        table(split_summary, max_rows=120),
        "",
        "## Candidate Labels",
        "",
        table(labels[labels["object_type"].eq("candidate")].head(80), max_rows=80),
        "",
        "## Eval Failures",
        "",
        table(eval_failures, max_rows=40),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- A7V-6: inspect positive smoke candidates against control dominance and family concentration before any larger replay.",
        "- Do not use A7V-5 to claim May robustness; May remains stress-only and this is a capped smoke.",
        "- Do not start full search until A7V-6 control-dominance and concentration forensics pass.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    selected = choose_candidates()
    controls = load_replay_controls(selected)
    index, symbols, matrices = load_panel(selected)
    ctx = ExprContext(matrices, symbols)

    metric_rows: list[dict[str, Any]] = []
    eval_failures: list[dict[str, Any]] = []
    for _, row in selected.iterrows():
        try:
            rows, meta = evaluate_row(index, matrices, ctx, row, "candidate", "original")
            metric_rows.extend(rows)
            if meta["eval_error"]:
                eval_failures.append(meta)
        except Exception as exc:  # noqa: BLE001
            eval_failures.append({"candidate_id": row["candidate_id"], "object_type": "candidate", "control_mode": "original", "eval_error": f"{type(exc).__name__}: {exc}"})
    for _, row in controls.iterrows():
        try:
            rows, meta = evaluate_row(index, matrices, ctx, row, "control", str(row["control_mode"]))
            metric_rows.extend(rows)
            if meta["eval_error"]:
                eval_failures.append(meta)
        except Exception as exc:  # noqa: BLE001
            eval_failures.append({"candidate_id": row["control_id"], "object_type": "control", "control_mode": row["control_mode"], "eval_error": f"{type(exc).__name__}: {exc}"})

    metrics = pd.DataFrame(metric_rows)
    failures = pd.DataFrame(eval_failures)
    labels = label_candidates(metrics) if not metrics.empty else pd.DataFrame()
    control_promotable = bool((labels.get("object_type", pd.Series(dtype=str)).eq("control") & labels.get("smoke_label", pd.Series(dtype=str)).ne("A7V5_CONTROL_NON_PROMOTABLE")).any()) if not labels.empty else False
    blockers = []
    if not failures.empty:
        blockers.append("eval_failures_present")
    if control_promotable:
        blockers.append("control_promotable_label")
    if metrics.empty:
        blockers.append("no_metrics")

    decision = "PASS_A7V5_SMALL_REPLAY_SMOKE_METHOD_ONLY" if not blockers else "HOLD_A7V5_REPLAY_SMOKE_BLOCKER"
    may_status = "HAS_MAY_AGG_DATA_STRESS_ONLY" if not labels.empty and labels["fresh_may_status"].eq("HAS_MAY_AGG_DATA_STRESS_ONLY").any() else "UNAVAILABLE_BY_DATA_COVERAGE_FOR_AGGTRADES"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "candidate_count": int(len(selected)),
        "control_count": int(len(controls)),
        "executes_search": False,
        "executes_replay": "small_smoke_only",
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_may_robustness_claim": False,
        "authorizes_a7v6_candidate_forensic": decision.startswith("PASS"),
        "may_status": may_status,
        "required_next": [
            "A7V-6 candidate/control dominance forensic on A7V-5 positives",
            "Do not claim May robustness from this capped smoke; May remains stress-only",
            "A7U-0R consolidated raw checksum trace before final alpha panel claims",
        ],
    }

    metrics.to_csv(OUT_DIR / "a7v5_smoke_split_metrics.csv", index=False)
    labels.to_csv(OUT_DIR / "a7v5_smoke_candidate_labels.csv", index=False)
    selected.to_csv(OUT_DIR / "a7v5_selected_candidates.csv", index=False)
    controls.to_csv(OUT_DIR / "a7v5_selected_controls.csv", index=False)
    failures.to_csv(OUT_DIR / "a7v5_eval_failures.csv", index=False)
    write_json(OUT_DIR / "a7v5_authorization_matrix.json", authorization)
    write_json(OUT_DIR / "a7v5_manifest.json", {"generated_at": now, "decision": decision, "output_dir": str(OUT_DIR), "panel": str(PANEL_PATH)})
    write_report(now, metrics, labels, controls, failures, authorization)
    print(json.dumps({"decision": decision, "blockers": blockers, "candidates": len(selected), "controls": len(controls), "metric_rows": len(metrics)}, indent=2))


if __name__ == "__main__":
    main()
