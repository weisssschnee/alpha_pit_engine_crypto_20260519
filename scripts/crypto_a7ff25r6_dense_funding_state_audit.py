from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7al2l_fast_derived_replay_preflight import SPLIT_ORDER, split_for_timestamps  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import BASE_DIR, load_base  # noqa: E402
from scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair import strict_symbols  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ff25r6_dense_funding_state_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FF25R6_DENSE_FUNDING_STATE_AUDIT_20260530.md"
A7FF25R5 = REPO / "runtime" / "a7ff25r5_funding_tail_repair_contract"

MAX_SYMBOLS = 96
FFILL_LIMIT_HOURS = 8
MIN_FINITE_SHARE = 0.20
MIN_NONZERO_SHARE = 0.01


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
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


def dense_ffill_and_age(raw: np.ndarray, limit: int) -> tuple[np.ndarray, np.ndarray]:
    dense = np.full_like(raw, np.nan, dtype=np.float64)
    age = np.full_like(raw, np.nan, dtype=np.float64)
    for i in range(raw.shape[0]):
        last = np.nan
        last_t = -10**9
        for j in range(raw.shape[1]):
            value = raw[i, j]
            if np.isfinite(value):
                last = value
                last_t = j
            current_age = j - last_t
            if np.isfinite(last) and current_age <= limit:
                dense[i, j] = last
                age[i, j] = current_age
    return dense, age


def rolling_mean_std_z(values: np.ndarray, window: int, min_periods: int) -> np.ndarray:
    out = np.full_like(values, np.nan, dtype=np.float64)
    frame = pd.DataFrame(values.T)
    mean = frame.rolling(window=window, min_periods=min_periods).mean()
    std = frame.rolling(window=window, min_periods=min_periods).std(ddof=0)
    z = (frame - mean) / std.replace(0, np.nan)
    out[:, :] = z.to_numpy(dtype=np.float64).T
    return out


def shift_matrix(values: np.ndarray, periods: int) -> np.ndarray:
    out = np.full_like(values, np.nan, dtype=np.float64)
    if periods > 0:
        out[:, periods:] = values[:, :-periods]
    elif periods < 0:
        out[:, :periods] = values[:, -periods:]
    else:
        out[:, :] = values
    return out


def field_metrics(name: str, matrix: np.ndarray, splits: np.ndarray) -> dict[str, Any]:
    finite = np.isfinite(matrix)
    nonzero = finite & (np.abs(matrix) > 1e-12)
    payload: dict[str, Any] = {
        "field_name": name,
        "finite_share": float(finite.mean()) if finite.size else np.nan,
        "nonzero_share": float(nonzero.mean()) if finite.size else np.nan,
        "mean_abs": float(np.nanmean(np.abs(matrix))) if finite.any() else np.nan,
        "max_abs": float(np.nanmax(np.abs(matrix))) if finite.any() else np.nan,
        "activity_ok": bool((float(finite.mean()) if finite.size else 0.0) >= MIN_FINITE_SHARE and (float(nonzero.mean()) if finite.size else 0.0) >= MIN_NONZERO_SHARE),
    }
    for split_name in SPLIT_ORDER:
        mask = splits == split_name
        sub = matrix[:, mask]
        sub_finite = np.isfinite(sub)
        sub_nonzero = sub_finite & (np.abs(sub) > 1e-12)
        payload[f"{split_name}_finite_share"] = float(sub_finite.mean()) if sub_finite.size else np.nan
        payload[f"{split_name}_nonzero_share"] = float(sub_nonzero.mean()) if sub_finite.size else np.nan
    return payload


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    prior = read_json(A7FF25R5 / "a7ff25r5_manifest.json")
    contract = read_csv(A7FF25R5 / "a7ff25r5_dense_funding_state_field_contract.csv")
    symbols = strict_symbols()[:MAX_SYMBOLS]
    loaded_symbols, timestamps, numeric = load_base(symbols, {"funding_rate", "mark_index_basis_bps"})
    raw = numeric["funding_rate"]
    basis = numeric["mark_index_basis_bps"]

    dense, age = dense_ffill_and_age(raw, FFILL_LIMIT_HOURS)
    abs_state_z = rolling_mean_std_z(np.abs(dense), 168, 48)
    delta_state_24h = dense - shift_matrix(dense, 24)
    basis_delta_24h = basis - shift_matrix(basis, 24)
    interaction = delta_state_24h * basis_delta_24h

    fields = {
        "raw_funding_rate": raw,
        "funding_rate_state_last_ffill_8h": dense,
        "funding_rate_update_age_hours": age,
        "funding_rate_abs_state_168h_z": abs_state_z,
        "funding_rate_delta_state_24h": delta_state_24h,
        "funding_state_x_basis_delta": interaction,
    }
    splits = split_for_timestamps(timestamps)
    metrics = pd.DataFrame([field_metrics(name, matrix, splits) for name, matrix in fields.items()])
    metrics.to_csv(RUNTIME / "a7ff25r6_dense_funding_state_activity_metrics.csv", index=False)

    split_metrics = metrics[
        ["field_name"]
        + [f"{split_name}_{suffix}" for split_name in SPLIT_ORDER for suffix in ["finite_share", "nonzero_share"]]
    ].copy()
    split_metrics.to_csv(RUNTIME / "a7ff25r6_split_activity_metrics.csv", index=False)

    repair_comparison = metrics.loc[
        metrics["field_name"].isin(["raw_funding_rate", "funding_rate_state_last_ffill_8h", "funding_rate_delta_state_24h", "funding_state_x_basis_delta"])
    ].copy()
    repair_comparison["finite_share_gain_vs_raw"] = repair_comparison["finite_share"] - float(metrics.loc[metrics["field_name"].eq("raw_funding_rate"), "finite_share"].iloc[0])
    repair_comparison.to_csv(RUNTIME / "a7ff25r6_repair_comparison.csv", index=False)

    sample_rows: list[dict[str, Any]] = []
    for symbol_idx, symbol in enumerate(loaded_symbols[:4]):
        for t_idx in range(0, min(len(timestamps), 96), 8):
            sample_rows.append(
                {
                    "symbol": symbol,
                    "timestamp": timestamps[t_idx].isoformat(),
                    "raw_funding_rate": raw[symbol_idx, t_idx],
                    "funding_rate_state_last_ffill_8h": dense[symbol_idx, t_idx],
                    "funding_rate_update_age_hours": age[symbol_idx, t_idx],
                    "funding_rate_delta_state_24h": delta_state_24h[symbol_idx, t_idx],
                    "funding_state_x_basis_delta": interaction[symbol_idx, t_idx],
                }
            )
    pd.DataFrame(sample_rows).to_csv(RUNTIME / "a7ff25r6_dense_funding_state_sample.csv", index=False)

    dense_ok = bool(metrics.loc[metrics["field_name"].eq("funding_rate_state_last_ffill_8h"), "activity_ok"].iloc[0])
    delta_ok = bool(metrics.loc[metrics["field_name"].eq("funding_rate_delta_state_24h"), "activity_ok"].iloc[0])
    interaction_ok = bool(metrics.loc[metrics["field_name"].eq("funding_state_x_basis_delta"), "activity_ok"].iloc[0])
    blockers: list[str] = []
    if not dense_ok:
        blockers.append("dense_state_activity_fail")
    if not delta_ok:
        blockers.append("delta_state_activity_fail")
    if not interaction_ok:
        blockers.append("interaction_activity_fail")

    decision = (
        "PASS_A7FF25R6_DENSE_FUNDING_STATE_MATERIALIZATION_READY_FOR_QUEUE_REPAIR_NO_SEARCH_AUTH"
        if not blockers
        else "HOLD_A7FF25R6_DENSE_FUNDING_STATE_ACTIVITY_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-25R6",
        "generated_at": now_utc(),
        "decision": decision,
        "prior_stage": prior.get("stage", "A7FF-25R5"),
        "prior_decision": prior.get("decision", ""),
        "symbol_count": len(loaded_symbols),
        "timestamp_count": len(timestamps),
        "field_count": len(fields),
        "ffill_limit_hours": FFILL_LIMIT_HOURS,
        "min_finite_share": MIN_FINITE_SHARE,
        "min_nonzero_share": MIN_NONZERO_SHARE,
        "blockers": blockers,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_queue_repair_contract": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff25r6_manifest.json", manifest)
    write_json(RUNTIME / "a7ff25r6_decision_record.json", manifest)

    lines = [
        "# CRYPTO A7FF-25R6 DENSE FUNDING-STATE AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-25R6 materializes the dense funding-state contract from A7FF-25R5 and checks whether the repaired fields clear basic activity gates. It does not generate formulas, run replay, execute search, or prove alpha.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## A7FF-25R5 Contract",
        "",
        md_table(contract, 20),
        "",
        "## Activity Metrics",
        "",
        md_table(metrics, 20),
        "",
        "## Repair Comparison",
        "",
        md_table(repair_comparison, 20),
        "",
        "## Sample",
        "",
        md_table(pd.DataFrame(sample_rows), 20),
        "",
        "## Boundary",
        "",
        "```text",
        "Dense funding-state materialization can repair no-activity tail queue inputs.",
        "It does not authorize formula generation, large search, alpha proof, shadow, paper, or live execution.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
