from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7_validation_utils import (
    COST_BPS,
    PURGE_EMBARGO_BARS,
    REPORT_DIR,
    RUNTIME_DIR,
    SPLITS,
    clean_float,
    load_core4_context,
    load_core4_specs,
    monthly_pass_rate,
    split_mask,
    summarize_returns,
)
from crypto_a7b_funding_baseline_audit import (
    RISK_VARIANT,
    object_specs,
    object_raw_book,
    scale_book,
    summarize_object,
)
from crypto_a7c_fundingcore_narrow_audit import fundingcore_specs


A7F_DIR = RUNTIME_DIR / "a7f_funding_regime_failure_audit"
RNG_SEED = 20260519
PRIMARY_COST_NAME = "stress_10bp"
PRIMARY_COST_BPS = COST_BPS[PRIMARY_COST_NAME]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def train_quantiles(index: pd.DatetimeIndex, values: np.ndarray, qs: list[float]) -> dict[float, float]:
    mask = split_mask(index, "train_2024")
    clean = values[mask]
    clean = clean[np.isfinite(clean)]
    if clean.size == 0:
        return {q: np.nan for q in qs}
    return {q: float(np.quantile(clean, q)) for q in qs}


def bucket_from_edges(values: np.ndarray, low: float, high: float) -> np.ndarray:
    out = np.full(values.shape, "missing", dtype=object)
    finite = np.isfinite(values)
    out[finite & (values <= low)] = "low"
    out[finite & (values > low) & (values < high)] = "mid"
    out[finite & (values >= high)] = "high"
    return out


def regime_frame(index: pd.DatetimeIndex, matrices: dict[str, np.ndarray]) -> tuple[pd.DataFrame, dict[str, Any]]:
    funding = matrices["latest_known_funding_rate"]
    persistence = matrices["funding_rate_persistence_3"]
    ret_12 = matrices["ret_12"]
    hl_range = matrices["hl_range"]
    mark_index_ratio = matrices["mark_index_ratio"]
    mark_minus_index = matrices["mark_minus_index"]

    metrics = pd.DataFrame(
        {
            "timestamp": index,
            "funding_abs_mean": np.nanmean(np.abs(funding), axis=1),
            "funding_mean": np.nanmean(funding, axis=1),
            "funding_dispersion": np.nanstd(funding, axis=1),
            "funding_positive_share": np.nanmean(funding > 0, axis=1),
            "funding_negative_share": np.nanmean(funding < 0, axis=1),
            "funding_persistence_abs_mean": np.nanmean(np.abs(persistence), axis=1),
            "basis_abs_mean": np.nanmean(np.abs(mark_index_ratio), axis=1),
            "basis_minus_abs_mean": np.nanmean(np.abs(mark_minus_index), axis=1),
            "vol_ret12_abs_mean": np.nanmean(np.abs(ret_12), axis=1),
            "vol_hl_mean": np.nanmean(hl_range, axis=1),
        }
    )

    threshold_fields = [
        "funding_abs_mean",
        "funding_dispersion",
        "funding_positive_share",
        "funding_negative_share",
        "funding_persistence_abs_mean",
        "basis_abs_mean",
        "basis_minus_abs_mean",
        "vol_ret12_abs_mean",
        "vol_hl_mean",
    ]
    thresholds: dict[str, Any] = {}
    for field in threshold_fields:
        q = train_quantiles(index, metrics[field].to_numpy(dtype=float), [0.25, 0.33, 0.50, 0.67, 0.75])
        thresholds[field] = {str(k): clean_float(v) for k, v in q.items()}
        metrics[f"{field}_bucket"] = bucket_from_edges(
            metrics[field].to_numpy(dtype=float),
            q[0.33],
            q[0.67],
        )

    return metrics, thresholds


def merge_book_with_regime(book: pd.DataFrame, regime: pd.DataFrame, object_name: str) -> pd.DataFrame:
    out = book.copy()
    if "fee_drag" not in out.columns and "turnover" in out.columns:
        out["fee_drag"] = out["turnover"] * (PRIMARY_COST_BPS / 10000.0)
    if "gross_return" not in out.columns and {"net_return", "funding_drag", "fee_drag"}.issubset(out.columns):
        out["gross_return"] = out["net_return"] + out["funding_drag"] + out["fee_drag"]
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    reg = regime.copy()
    reg["timestamp"] = pd.to_datetime(reg["timestamp"], utc=True)
    out = out.merge(reg, on="timestamp", how="left")
    out["object"] = object_name
    return out


def summarize_bucket(frame: pd.DataFrame, value_col: str, bucket_col: str) -> pd.DataFrame:
    rows = []
    ts = pd.DatetimeIndex(pd.to_datetime(frame["timestamp"], utc=True))
    for split_name in SPLITS:
        split = frame.loc[split_mask(ts, split_name)].copy()
        for bucket, part in split.groupby(bucket_col, dropna=False):
            st = summarize_returns(part[value_col].to_numpy(dtype=float))
            rows.append(
                {
                    "object": frame["object"].iloc[0] if "object" in frame and not frame.empty else None,
                    "split": split_name,
                    "bucket_field": bucket_col,
                    "bucket": str(bucket),
                    "active_ratio_within_split": clean_float(len(part) / len(split)) if len(split) else None,
                    **st,
                    "mean_turnover": clean_float(part["turnover"].mean()) if "turnover" in part else None,
                    "mean_gross_exposure": clean_float(part["gross_exposure"].mean()) if "gross_exposure" in part else None,
                }
            )
    return pd.DataFrame(rows)


def gate_definitions(regime: pd.DataFrame) -> dict[str, pd.Series]:
    # All gates are predeclared using train-derived regime buckets. Gate returns
    # are full-calendar with cash return of zero while inactive.
    return {
        "G0_no_gate": pd.Series(True, index=regime.index),
        "G1_avoid_high_funding_abs": regime["funding_abs_mean_bucket"] != "high",
        "G2_funding_abs_low_only": regime["funding_abs_mean_bucket"] == "low",
        "G3_funding_positive_share_low_or_mid": regime["funding_positive_share_bucket"].isin(["low", "mid"]),
        "G4_basis_abs_low_or_mid": regime["basis_abs_mean_bucket"].isin(["low", "mid"]),
        "G5_vol_ret12_low_or_mid": regime["vol_ret12_abs_mean_bucket"].isin(["low", "mid"]),
        "G6_all_low_risk_intersection": (
            (regime["funding_abs_mean_bucket"] != "high")
            & (regime["basis_abs_mean_bucket"] != "high")
            & (regime["vol_ret12_abs_mean_bucket"] != "high")
        ),
        "G7_inverted_avoid_high_funding_abs": regime["funding_abs_mean_bucket"] == "high",
    }


def summarize_gate(frame: pd.DataFrame, gates: dict[str, pd.Series], value_col: str = "net_return") -> pd.DataFrame:
    rows = []
    ts = pd.DatetimeIndex(pd.to_datetime(frame["timestamp"], utc=True))
    for gate_name, gate in gates.items():
        gate_values = gate.reset_index(drop=True).to_numpy(dtype=bool)
        gated = frame.copy()
        gated["gate_active"] = gate_values[: len(gated)]
        gated["gated_return"] = np.where(gated["gate_active"], gated[value_col], 0.0)
        for split_name in SPLITS:
            mask = split_mask(ts, split_name)
            part = gated.loc[mask]
            st = summarize_returns(part["gated_return"].to_numpy(dtype=float))
            active = part[part["gate_active"]]
            inactive = part[~part["gate_active"]]
            mon = monthly_pass_rate(part.rename(columns={"gated_return": "tmp"}), "tmp", split_name)
            rows.append(
                {
                    "object": frame["object"].iloc[0],
                    "gate": gate_name,
                    "split": split_name,
                    "active_ratio": clean_float(part["gate_active"].mean()) if len(part) else None,
                    "active_hours": int(part["gate_active"].sum()),
                    "inactive_hours": int((~part["gate_active"]).sum()),
                    "active_mean_return": clean_float(active[value_col].mean()) if not active.empty else None,
                    "inactive_missed_mean_return": clean_float(inactive[value_col].mean()) if not inactive.empty else None,
                    "active_total_return_sum": clean_float(active[value_col].sum()) if not active.empty else None,
                    "inactive_missed_return_sum": clean_float(inactive[value_col].sum()) if not inactive.empty else None,
                    **st,
                    **mon,
                    "mean_turnover_active": clean_float(active["turnover"].mean()) if "turnover" in active else None,
                }
            )
    return pd.DataFrame(rows)


def random_gate_placebo(frame: pd.DataFrame, reference_gate: pd.Series, iterations: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(RNG_SEED)
    active_count = int(reference_gate.sum())
    n = len(reference_gate)
    ts = pd.DatetimeIndex(pd.to_datetime(frame["timestamp"], utc=True))
    rows = []
    if active_count <= 0 or active_count >= n:
        return pd.DataFrame(rows)
    for i in range(iterations):
        active_idx = rng.choice(n, size=active_count, replace=False)
        gate = np.zeros(n, dtype=bool)
        gate[active_idx] = True
        ret = np.where(gate, frame["net_return"].to_numpy(dtype=float), 0.0)
        for split_name in ["recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]:
            mask = split_mask(ts, split_name)
            st = summarize_returns(ret[mask])
            rows.append({"iteration": i, "split": split_name, **st})
    return pd.DataFrame(rows)


def top_loss_hours(frame: pd.DataFrame, n: int = 30) -> pd.DataFrame:
    cols = [
        "timestamp",
        "object",
        "net_return",
        "gross_return",
        "funding_drag",
        "fee_drag",
        "turnover",
        "gross_exposure",
        "funding_abs_mean",
        "funding_mean",
        "funding_dispersion",
        "funding_positive_share",
        "basis_abs_mean",
        "vol_ret12_abs_mean",
        "funding_abs_mean_bucket",
        "basis_abs_mean_bucket",
        "vol_ret12_abs_mean_bucket",
    ]
    may = frame[pd.to_datetime(frame["timestamp"], utc=True) >= pd.Timestamp("2026-05-01T00:00:00Z")]
    return may.sort_values("net_return").head(n)[cols]


def write_report(
    *,
    manifest: dict[str, Any],
    gate_summary: pd.DataFrame,
    bucket_summary: pd.DataFrame,
    placebo_summary: pd.DataFrame,
    report_path: Path,
) -> None:
    gate_display = gate_summary[
        (gate_summary["object"].isin(["FundingCore", "Core4"]))
        & (gate_summary["split"].isin(["validation_2025H1", "recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]))
    ].copy()
    gate_display = gate_display[gate_display["gate"].isin(["G0_no_gate", "G1_avoid_high_funding_abs", "G6_all_low_risk_intersection", "G7_inverted_avoid_high_funding_abs"])]
    bucket_display = bucket_summary[
        (bucket_summary["object"] == "FundingCore")
        & (bucket_summary["split"].isin(["recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]))
        & (bucket_summary["bucket_field"].isin(["funding_abs_mean_bucket", "basis_abs_mean_bucket", "vol_ret12_abs_mean_bucket"]))
    ].copy()

    lines = [
        "# Crypto A7F Funding Regime / Risk Failure Audit",
        "",
        f"- generated_at: `{manifest['generated_at']}`",
        f"- decision: `{manifest['decision']}`",
        f"- blockers: `{manifest['blockers']}`",
        f"- warnings: `{manifest['warnings']}`",
        f"- risk_variant: `{manifest['risk_variant']}`",
        f"- cost_tier: `{manifest['cost_tier']}`",
        "",
        "## Scope",
        "",
        "No new search, no formula changes, no gate promotion. This audit explains FundingCore/Core4 fresh May failure and tests only predeclared train-threshold gates.",
        "",
        "Regime basis proxy uses corrected `basis_abs_mean = abs(mark_index_ratio)`. `mark_index_ratio` is already centered as `mark_close / index_close - 1.0`.",
        "",
        "## Gate Replay",
        "",
        "| object | gate | split | ann mean | DD | active ratio | active mean | inactive missed mean | month pass |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in gate_display.iterrows():
        lines.append(
            f"| `{row['object']}` | `{row['gate']}` | `{row['split']}` | "
            f"{row['annualized_mean'] if pd.notna(row['annualized_mean']) else 0:.4f} | "
            f"{row['compounded_max_dd'] if pd.notna(row['compounded_max_dd']) else 0:.4f} | "
            f"{row['active_ratio'] if pd.notna(row['active_ratio']) else 0:.3f} | "
            f"{row['active_mean_return'] if pd.notna(row['active_mean_return']) else 0:.6f} | "
            f"{row['inactive_missed_mean_return'] if pd.notna(row['inactive_missed_mean_return']) else 0:.6f} | "
            f"{row['positive_month_rate'] if pd.notna(row['positive_month_rate']) else 0:.3f} |"
        )
    lines += [
        "",
        "## FundingCore Bucket Replay",
        "",
        "| bucket field | bucket | split | ann mean | DD | active ratio | turnover |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for _, row in bucket_display.iterrows():
        lines.append(
            f"| `{row['bucket_field']}` | `{row['bucket']}` | `{row['split']}` | "
            f"{row['annualized_mean'] if pd.notna(row['annualized_mean']) else 0:.4f} | "
            f"{row['compounded_max_dd'] if pd.notna(row['compounded_max_dd']) else 0:.4f} | "
            f"{row['active_ratio_within_split'] if pd.notna(row['active_ratio_within_split']) else 0:.3f} | "
            f"{row['mean_turnover'] if pd.notna(row['mean_turnover']) else 0:.4f} |"
        )
    if not placebo_summary.empty:
        lines += [
            "",
            "## Random Active-Hour Placebo",
            "",
            "| split | reference gate | iterations | mean ann | p95 ann |",
            "|---|---|---:|---:|---:|",
        ]
        for _, row in placebo_summary.iterrows():
            lines.append(
                f"| `{row['split']}` | `{row['reference_gate']}` | {int(row['iterations'])} | "
                f"{row['mean_annualized']:.4f} | {row['p95_annualized']:.4f} |"
            )
    lines += [
        "",
        "## Decision",
        "",
        "- Passing A7F would only justify further regime/risk research.",
        "- It does not promote FundingCore/Core4 to shadow proof.",
        "- Generator bakeoff remains blocked while fresh-forward failure and drawdown remain unresolved.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    A7F_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    index, symbols, matrices, ctx = load_core4_context()
    regime, thresholds = regime_frame(index, matrices)

    core4_raw, _ = object_raw_book(index, matrices, ctx, object_specs()["B0_Core4"])
    funding_raw, _ = object_raw_book(index, matrices, ctx, fundingcore_specs())
    core4 = scale_book(core4_raw, PRIMARY_COST_BPS)
    funding = scale_book(funding_raw, PRIMARY_COST_BPS)
    core4 = merge_book_with_regime(core4, regime, "Core4")
    funding = merge_book_with_regime(funding, regime, "FundingCore")

    bucket_fields = [
        "funding_abs_mean_bucket",
        "funding_dispersion_bucket",
        "funding_positive_share_bucket",
        "funding_negative_share_bucket",
        "basis_abs_mean_bucket",
        "basis_minus_abs_mean_bucket",
        "vol_ret12_abs_mean_bucket",
        "vol_hl_mean_bucket",
    ]
    bucket_summary = pd.concat(
        [summarize_bucket(frame, "net_return", field) for frame in [funding, core4] for field in bucket_fields],
        ignore_index=True,
    )

    gates = gate_definitions(regime)
    gate_summary = pd.concat(
        [summarize_gate(frame, gates, "net_return") for frame in [funding, core4]],
        ignore_index=True,
    )

    reference_gate = gates["G1_avoid_high_funding_abs"]
    placebo = random_gate_placebo(funding, reference_gate)
    if not placebo.empty:
        placebo_summary = (
            placebo.groupby("split")
            .agg(
                mean_annualized=("annualized_mean", "mean"),
                p95_annualized=("annualized_mean", lambda x: float(np.quantile(x, 0.95))),
                iterations=("iteration", "nunique"),
            )
            .reset_index()
        )
        placebo_summary["reference_gate"] = "G1_avoid_high_funding_abs"
    else:
        placebo_summary = pd.DataFrame()

    losses = pd.concat([top_loss_hours(funding), top_loss_hours(core4)], ignore_index=True)

    regime_path = A7F_DIR / "crypto_a7f_regime_state_20260519.csv"
    threshold_path = A7F_DIR / "crypto_a7f_train_thresholds_20260519.json"
    bucket_path = A7F_DIR / "crypto_a7f_bucket_summary_20260519.csv"
    gate_path = A7F_DIR / "crypto_a7f_gate_summary_20260519.csv"
    placebo_path = A7F_DIR / "crypto_a7f_gate_random_placebo_20260519.csv"
    loss_path = A7F_DIR / "crypto_a7f_may_top_loss_hours_20260519.csv"
    regime.to_csv(regime_path, index=False)
    write_json(threshold_path, thresholds)
    bucket_summary.to_csv(bucket_path, index=False)
    gate_summary.to_csv(gate_path, index=False)
    placebo_summary.to_csv(placebo_path, index=False)
    losses.to_csv(loss_path, index=False)

    def gate_metric(obj: str, gate: str, split: str, col: str) -> float | None:
        row = gate_summary[(gate_summary["object"] == obj) & (gate_summary["gate"] == gate) & (gate_summary["split"] == split)]
        if row.empty:
            return None
        return clean_float(row.iloc[0][col])

    fcore_no_gate_may = gate_metric("FundingCore", "G0_no_gate", "fresh_forward_2026May", "annualized_mean")
    fcore_g1_may = gate_metric("FundingCore", "G1_avoid_high_funding_abs", "fresh_forward_2026May", "annualized_mean")
    fcore_g1_recent = gate_metric("FundingCore", "G1_avoid_high_funding_abs", "recent_oos_2025H2_2026Apr", "annualized_mean")
    fcore_g1_active_may = gate_metric("FundingCore", "G1_avoid_high_funding_abs", "fresh_forward_2026May", "active_ratio")
    fcore_g6_may = gate_metric("FundingCore", "G6_all_low_risk_intersection", "fresh_forward_2026May", "annualized_mean")
    fcore_g6_recent = gate_metric("FundingCore", "G6_all_low_risk_intersection", "recent_oos_2025H2_2026Apr", "annualized_mean")
    fcore_g6_active_may = gate_metric("FundingCore", "G6_all_low_risk_intersection", "fresh_forward_2026May", "active_ratio")
    core4_g1_may = gate_metric("Core4", "G1_avoid_high_funding_abs", "fresh_forward_2026May", "annualized_mean")
    core4_g6_may = gate_metric("Core4", "G6_all_low_risk_intersection", "fresh_forward_2026May", "annualized_mean")

    blockers = []
    warnings = []
    if fcore_g1_may is None or fcore_g1_may <= 0:
        blockers.append("predeclared_funding_gate_does_not_clear_fresh_may_failure")
    if fcore_g1_recent is not None and fcore_g1_recent <= 0:
        warnings.append("predeclared_funding_gate_not_positive_in_recent_oos")
    if fcore_g1_active_may is not None and fcore_g1_active_may < 0.15:
        warnings.append("predeclared_gate_active_ratio_too_low")
    if core4_g1_may is not None and core4_g1_may <= 0:
        warnings.append("core4_still_negative_under_predeclared_funding_gate")

    decision = "PASS_A7F_REGIME_GATE_RESEARCH_CANDIDATE" if not blockers else "HOLD_A7F_FUNDING_REGIME_FAILURE_UNRESOLVED"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "risk_variant": RISK_VARIANT,
        "cost_tier": PRIMARY_COST_NAME,
        "purge_embargo_bars": PURGE_EMBARGO_BARS,
        "key_metrics": {
            "fundingcore_no_gate_fresh_may_ann": fcore_no_gate_may,
            "fundingcore_g1_fresh_may_ann": fcore_g1_may,
            "fundingcore_g1_recent_oos_ann": fcore_g1_recent,
            "fundingcore_g1_fresh_may_active_ratio": fcore_g1_active_may,
            "fundingcore_g6_fresh_may_ann": fcore_g6_may,
            "fundingcore_g6_recent_oos_ann": fcore_g6_recent,
            "fundingcore_g6_fresh_may_active_ratio": fcore_g6_active_may,
            "core4_g1_fresh_may_ann": core4_g1_may,
            "core4_g6_fresh_may_ann": core4_g6_may,
        },
        "regime_feature_contract": {
            "basis_abs_mean": "abs(mark_index_ratio)",
            "basis_abs_mean_note": "mark_index_ratio is already centered as mark_close / index_close - 1.0",
            "legacy_invalid_basis_abs_mean": "abs(mark_index_ratio - 1.0)",
        },
        "outputs": {
            "regime_state": str(regime_path),
            "train_thresholds": str(threshold_path),
            "bucket_summary": str(bucket_path),
            "gate_summary": str(gate_path),
            "gate_random_placebo": str(placebo_path),
            "may_top_loss_hours": str(loss_path),
        },
    }
    manifest_path = A7F_DIR / "crypto_a7f_manifest_20260519.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / "CRYPTO_A7F_FUNDING_REGIME_FAILURE_AUDIT_20260519.md"
    write_report(
        manifest=manifest,
        gate_summary=gate_summary,
        bucket_summary=bucket_summary,
        placebo_summary=placebo_summary,
        report_path=report_path,
    )

    decision_path = REPORT_DIR / "CRYPTO_A7F_DECISION_RECORD_20260519.md"
    decision_lines = [
        "# Crypto A7F Decision Record",
        "",
        f"- decision: `{decision}`",
        f"- generated_at: `{manifest['generated_at']}`",
        f"- blockers: `{blockers}`",
        f"- warnings: `{warnings}`",
        "",
        "## Conclusion",
        "",
        "A7F fixes no formulas and performs no search. It tests whether train-threshold funding/basis/volatility regimes can explain or reduce the fresh May failure.",
        "",
        "## Current State",
        "",
        "- Funding semantics are clean enough for research after A7E.",
        "- FundingCore/Core4 remain blocked from alpha shadow proof unless fresh-forward and drawdown risks are cleared.",
        "- Any gate found here is a research candidate only and must be forward-locked before evidence upgrade.",
    ]
    decision_path.write_text("\n".join(decision_lines) + "\n", encoding="utf-8")

    print("A7F_REPORT=" + str(report_path))
    print("A7F_DECISION_RECORD=" + str(decision_path))
    print("A7F_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
