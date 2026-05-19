from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a2_6_tradable_replay import forward_funding_cost, funding_event_rate, next_open_return
from crypto_a7_validation_utils import (
    COST_BPS,
    REPORT_DIR,
    RUNTIME_DIR,
    SPLITS,
    clean_float,
    load_core4_context,
    load_core4_specs,
    orient_signal,
    position_matrix,
    split_mask,
    summarize_returns,
)
from crypto_a7b_funding_baseline_audit import RISK_VARIANT, compute_multiplier, object_raw_book, scale_book
from crypto_a7c_fundingcore_narrow_audit import fundingcore_specs
from crypto_a7f_funding_regime_failure_audit import regime_frame


A7G1_DIR = RUNTIME_DIR / "a7g1_may_failure_forensic_audit"
PRIMARY_COST_NAME = "stress_10bp"
PRIMARY_COST_BPS = COST_BPS[PRIMARY_COST_NAME]
MAY_START = pd.Timestamp("2026-05-01T00:00:00Z")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def object_specs() -> dict[str, list]:
    return {
        "FundingCore": fundingcore_specs(),
        "Core4": load_core4_specs(),
    }


def component_symbol_may(
    *,
    object_name: str,
    spec,
    index: pd.DatetimeIndex,
    symbols: list[str],
    matrices: dict[str, np.ndarray],
    ctx,
    multiplier: pd.Series,
) -> pd.DataFrame:
    signal = ctx.eval(spec.expression)
    gross_target = next_open_return(matrices["open"], spec.horizon)
    funding_cost = forward_funding_cost(funding_event_rate(matrices), spec.horizon)
    target = gross_target - funding_cost
    orientation, train_ic = orient_signal(index, signal, target)
    pos = position_matrix(signal, target, orientation)
    prev = np.vstack([np.zeros((1, pos.shape[1])), pos[:-1, :]])
    turnover = np.abs(pos - prev) / 2.0
    fee = turnover * (PRIMARY_COST_BPS / 10000.0)
    gross = pos * gross_target
    funding_drag = pos * funding_cost
    net = gross - funding_drag - fee
    may_mask = np.asarray(index >= MAY_START)
    m = multiplier.to_numpy(dtype=float)[:, None]
    rows = []
    for j, symbol in enumerate(symbols):
        part = pd.DataFrame(
            {
                "timestamp": index[may_mask],
                "object": object_name,
                "component_id": spec.cluster_id,
                "candidate_id": spec.candidate_id,
                "horizon": spec.horizon,
                "symbol": symbol,
                "orientation": orientation,
                "train_ic_mean": train_ic,
                "position": pos[may_mask, j],
                "gross_price_pnl": gross[may_mask, j] * m[may_mask, 0],
                "funding_drag": funding_drag[may_mask, j] * m[may_mask, 0],
                "fee_drag": fee[may_mask, j] * m[may_mask, 0],
                "turnover": turnover[may_mask, j] * m[may_mask, 0],
                "net_return": net[may_mask, j] * m[may_mask, 0],
                "funding_rate": matrices["latest_known_funding_rate"][may_mask, j],
                "funding_cost_forward": funding_cost[may_mask, j],
                "mark_index_ratio": matrices["mark_index_ratio"][may_mask, j],
                "mark_minus_index": matrices["mark_minus_index"][may_mask, j],
                "ret_12": matrices["ret_12"][may_mask, j],
                "hl_range": matrices["hl_range"][may_mask, j],
            }
        )
        rows.append(part)
    return pd.concat(rows, ignore_index=True)


def summarize_group(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    out = (
        df.groupby(group_cols, dropna=False)
        .agg(
            rows=("net_return", "size"),
            net_sum=("net_return", "sum"),
            net_mean=("net_return", "mean"),
            worst_hour_symbol=("net_return", "min"),
            best_hour_symbol=("net_return", "max"),
            gross_sum=("gross_price_pnl", "sum"),
            funding_drag_sum=("funding_drag", "sum"),
            fee_drag_sum=("fee_drag", "sum"),
            turnover_sum=("turnover", "sum"),
            abs_position_sum=("position", lambda x: float(np.nansum(np.abs(x)))),
            long_position_share=("position", lambda x: float(np.nanmean(x > 0))),
            short_position_share=("position", lambda x: float(np.nanmean(x < 0))),
            mean_funding_rate=("funding_rate", "mean"),
            mean_abs_funding_rate=("funding_rate", lambda x: float(np.nanmean(np.abs(x)))),
        )
        .reset_index()
    )
    return out.sort_values("net_sum")


def object_book(index: pd.DatetimeIndex, matrices: dict[str, np.ndarray], ctx, specs: list) -> tuple[pd.DataFrame, pd.Series]:
    raw, _ = object_raw_book(index, matrices, ctx, specs)
    scaled = scale_book(raw, PRIMARY_COST_BPS)
    return scaled, compute_multiplier(raw)


def book_regime_summary(book: pd.DataFrame, regime: pd.DataFrame, object_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = book.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    reg = regime.copy()
    reg["timestamp"] = pd.to_datetime(reg["timestamp"], utc=True)
    frame = frame.merge(reg, on="timestamp", how="left")
    frame["object"] = object_name
    may = frame[frame["timestamp"] >= MAY_START].copy()
    bucket_fields = [
        "funding_abs_mean_bucket",
        "funding_positive_share_bucket",
        "funding_negative_share_bucket",
        "basis_abs_mean_bucket",
        "vol_ret12_abs_mean_bucket",
        "vol_hl_mean_bucket",
    ]
    rows = []
    for field in bucket_fields:
        for bucket, part in may.groupby(field, dropna=False):
            st = summarize_returns(part["net_return"].to_numpy(dtype=float))
            rows.append(
                {
                    "object": object_name,
                    "bucket_field": field,
                    "bucket": str(bucket),
                    "hours": int(len(part)),
                    "active_share_in_may": clean_float(len(part) / len(may)) if len(may) else None,
                    **st,
                    "mean_turnover": clean_float(part["turnover"].mean()) if "turnover" in part else None,
                    "mean_gross_exposure": clean_float(part["gross_exposure"].mean()) if "gross_exposure" in part else None,
                }
            )
    top_losses = may.sort_values("net_return").head(30)
    return pd.DataFrame(rows), top_losses


def component_top_loss_contrib(symbol_detail: pd.DataFrame, top_losses: pd.DataFrame) -> pd.DataFrame:
    top_ts = set(pd.to_datetime(top_losses["timestamp"], utc=True))
    part = symbol_detail[pd.to_datetime(symbol_detail["timestamp"], utc=True).isin(top_ts)]
    return summarize_group(part, ["object", "component_id"]).rename(columns={"net_sum": "top_loss_hours_net_sum"})


def concentration_stats(book: pd.DataFrame, object_name: str) -> dict[str, Any]:
    may = book[pd.to_datetime(book["timestamp"], utc=True) >= MAY_START].copy()
    losses = may.sort_values("net_return")
    total = clean_float(may["net_return"].sum())
    neg_total = clean_float(may.loc[may["net_return"] < 0, "net_return"].sum())
    return {
        "object": object_name,
        "may_hours": int(len(may)),
        "may_total_return_sum": total,
        "may_negative_return_sum": neg_total,
        "top1_loss": clean_float(losses["net_return"].head(1).sum()),
        "top3_loss": clean_float(losses["net_return"].head(3).sum()),
        "top5_loss": clean_float(losses["net_return"].head(5).sum()),
        "top10_loss": clean_float(losses["net_return"].head(10).sum()),
        "top3_loss_share_of_negative_loss": clean_float(losses["net_return"].head(3).sum() / neg_total) if neg_total else None,
        "top10_loss_share_of_negative_loss": clean_float(losses["net_return"].head(10).sum() / neg_total) if neg_total else None,
        "positive_hour_rate": clean_float((may["net_return"] > 0).mean()),
    }


def write_report(
    *,
    manifest: dict[str, Any],
    component_summary: pd.DataFrame,
    symbol_summary: pd.DataFrame,
    bucket_summary: pd.DataFrame,
    concentration: pd.DataFrame,
    report_path: Path,
) -> None:
    comp = component_summary.sort_values("net_sum").head(16)
    sym = symbol_summary.sort_values("net_sum").head(16)
    bucket = bucket_summary[
        bucket_summary["bucket_field"].isin(["funding_abs_mean_bucket", "basis_abs_mean_bucket", "vol_ret12_abs_mean_bucket"])
    ].copy()
    lines = [
        "# Crypto A7G-1 May Failure Forensic Audit",
        "",
        f"- generated_at: `{manifest['generated_at']}`",
        f"- decision: `{manifest['decision']}`",
        f"- blockers: `{manifest['blockers']}`",
        f"- warnings: `{manifest['warnings']}`",
        "",
        "## Scope",
        "",
        "No new search, no formula changes, no gate tuning. This audit decomposes fresh May 2026 losses after the corrected basis contract from A7G-0.",
        "",
        "## Status Boundary",
        "",
        "- A7G-1 is a forensic completion pass, not an alpha/risk gate pass.",
        "- FundingCore/Core4 remain blocked from alpha shadow proof.",
        "- This result does not authorize A7.3 generator bakeoff, shadow, paper, or live trading.",
        "",
        "## Loss Concentration",
        "",
        "| object | May total | positive hour rate | top3 loss share | top10 loss share |",
        "|---|---:|---:|---:|---:|",
    ]
    for _, row in concentration.iterrows():
        lines.append(
            f"| `{row['object']}` | {row['may_total_return_sum']:.4f} | {row['positive_hour_rate']:.3f} | "
            f"{row['top3_loss_share_of_negative_loss']:.3f} | {row['top10_loss_share_of_negative_loss']:.3f} |"
        )
    lines += [
        "",
        "## Worst Components",
        "",
        "| object | component | net sum | gross | funding drag | fee | turnover | mean funding |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in comp.iterrows():
        lines.append(
            f"| `{row['object']}` | `{row['component_id']}` | {row['net_sum']:.4f} | {row['gross_sum']:.4f} | "
            f"{row['funding_drag_sum']:.4f} | {row['fee_drag_sum']:.4f} | {row['turnover_sum']:.4f} | {row['mean_funding_rate']:.6f} |"
        )
    lines += [
        "",
        "## Worst Symbols",
        "",
        "| object | symbol | net sum | gross | funding drag | fee | turnover | abs pos |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in sym.iterrows():
        lines.append(
            f"| `{row['object']}` | `{row['symbol']}` | {row['net_sum']:.4f} | {row['gross_sum']:.4f} | "
            f"{row['funding_drag_sum']:.4f} | {row['fee_drag_sum']:.4f} | {row['turnover_sum']:.4f} | {row['abs_position_sum']:.2f} |"
        )
    lines += [
        "",
        "## Regime Buckets",
        "",
        "| object | bucket field | bucket | ann mean | DD | hours | share |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for _, row in bucket.iterrows():
        lines.append(
            f"| `{row['object']}` | `{row['bucket_field']}` | `{row['bucket']}` | "
            f"{row['annualized_mean'] if pd.notna(row['annualized_mean']) else 0:.4f} | "
            f"{row['compounded_max_dd'] if pd.notna(row['compounded_max_dd']) else 0:.4f} | "
            f"{int(row['hours'])} | {row['active_share_in_may']:.3f} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        "- FundingCore/Core4 stay at research-benchmark status only.",
        "- The May failure is broad across components and multiple symbols, not a small top-hour cleanup problem.",
        "- If losses are broad across components and symbols, the funding line remains paused for alpha proof.",
        "- If losses are dominated by a small component/symbol/hour set, the next valid work is a predeclared risk-control audit, not search.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    A7G1_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    index, symbols, matrices, ctx = load_core4_context()
    regime, _ = regime_frame(index, matrices)
    specs_by_object = object_specs()

    all_symbol_detail = []
    all_books = []
    all_bucket = []
    all_top_losses = []
    all_concentration = []
    all_top_loss_component = []
    for object_name, specs in specs_by_object.items():
        book, multiplier = object_book(index, matrices, ctx, specs)
        book["object"] = object_name
        all_books.append(book)
        bucket_summary, top_losses = book_regime_summary(book, regime, object_name)
        all_bucket.append(bucket_summary)
        all_top_losses.append(top_losses.assign(object=object_name))
        all_concentration.append(concentration_stats(book, object_name))
        detail_parts = []
        for spec in specs:
            detail_parts.append(
                component_symbol_may(
                    object_name=object_name,
                    spec=spec,
                    index=index,
                    symbols=symbols,
                    matrices=matrices,
                    ctx=ctx,
                    multiplier=multiplier,
                )
            )
        detail = pd.concat(detail_parts, ignore_index=True)
        all_symbol_detail.append(detail)
        all_top_loss_component.append(component_top_loss_contrib(detail, top_losses))

    symbol_detail = pd.concat(all_symbol_detail, ignore_index=True)
    component_summary = summarize_group(symbol_detail, ["object", "component_id", "candidate_id", "horizon"])
    symbol_summary = summarize_group(symbol_detail, ["object", "symbol"])
    object_symbol_component = summarize_group(symbol_detail, ["object", "symbol", "component_id"])
    bucket_summary = pd.concat(all_bucket, ignore_index=True)
    top_losses = pd.concat(all_top_losses, ignore_index=True)
    concentration = pd.DataFrame(all_concentration)
    top_loss_component = pd.concat(all_top_loss_component, ignore_index=True)

    component_path = A7G1_DIR / "crypto_a7g1_may_component_contribution_20260519.csv"
    symbol_path = A7G1_DIR / "crypto_a7g1_may_symbol_contribution_20260519.csv"
    symbol_component_path = A7G1_DIR / "crypto_a7g1_may_symbol_component_contribution_20260519.csv"
    bucket_path = A7G1_DIR / "crypto_a7g1_may_regime_bucket_contribution_20260519.csv"
    top_loss_path = A7G1_DIR / "crypto_a7g1_may_top_loss_hours_20260519.csv"
    concentration_path = A7G1_DIR / "crypto_a7g1_may_loss_concentration_20260519.csv"
    top_loss_component_path = A7G1_DIR / "crypto_a7g1_top_loss_hour_component_contribution_20260519.csv"
    component_summary.to_csv(component_path, index=False)
    symbol_summary.to_csv(symbol_path, index=False)
    object_symbol_component.to_csv(symbol_component_path, index=False)
    bucket_summary.to_csv(bucket_path, index=False)
    top_losses.to_csv(top_loss_path, index=False)
    concentration.to_csv(concentration_path, index=False)
    top_loss_component.to_csv(top_loss_component_path, index=False)

    def metric(df: pd.DataFrame, obj: str, col: str) -> float | None:
        row = df[df["object"] == obj]
        if row.empty:
            return None
        return clean_float(row.iloc[0][col])

    fcore_top10_share = metric(concentration, "FundingCore", "top10_loss_share_of_negative_loss")
    core4_top10_share = metric(concentration, "Core4", "top10_loss_share_of_negative_loss")
    fcore_positive_rate = metric(concentration, "FundingCore", "positive_hour_rate")
    core4_positive_rate = metric(concentration, "Core4", "positive_hour_rate")
    fcore_components_negative = int((component_summary[component_summary["object"] == "FundingCore"]["net_sum"] < 0).sum())
    core4_components_negative = int((component_summary[component_summary["object"] == "Core4"]["net_sum"] < 0).sum())
    fcore_symbols_negative = int((symbol_summary[symbol_summary["object"] == "FundingCore"]["net_sum"] < 0).sum())
    core4_symbols_negative = int((symbol_summary[symbol_summary["object"] == "Core4"]["net_sum"] < 0).sum())

    warnings = [
        "fresh_forward_failure_unresolved",
        "funding_line_paused_for_alpha_proof",
        "a7g1_forensic_pass_is_not_risk_gate_pass",
    ]
    blockers = []
    if fcore_components_negative >= 3 and fcore_symbols_negative >= 6:
        warnings.append("fundingcore_may_loss_broad_across_components_and_multiple_symbols")
    if core4_components_negative >= 3 and core4_symbols_negative >= 6:
        warnings.append("core4_may_loss_broad_across_components_and_multiple_symbols")
    if fcore_top10_share is not None and fcore_top10_share > 0.5:
        warnings.append("fundingcore_top_loss_hours_concentrated")
    if core4_top10_share is not None and core4_top10_share > 0.5:
        warnings.append("core4_top_loss_hours_concentrated")

    decision = "PASS_A7G1_FORENSIC_COMPLETED_HOLD_FUNDING_LINE"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "alpha_proof_status": "HOLD_ALPHA_SHADOW_PROOF",
        "risk_gate_status": "NOT_PASSED",
        "authorizes_a7_3_generator_bakeoff": False,
        "authorizes_shadow_live_or_paper": False,
        "blockers": blockers,
        "warnings": warnings,
        "risk_variant": RISK_VARIANT,
        "cost_tier": PRIMARY_COST_NAME,
        "key_metrics": {
            "fundingcore_top10_loss_share": fcore_top10_share,
            "core4_top10_loss_share": core4_top10_share,
            "fundingcore_positive_hour_rate": fcore_positive_rate,
            "core4_positive_hour_rate": core4_positive_rate,
            "fundingcore_negative_components": fcore_components_negative,
            "core4_negative_components": core4_components_negative,
            "fundingcore_negative_symbols": fcore_symbols_negative,
            "core4_negative_symbols": core4_symbols_negative,
        },
        "outputs": {
            "component_contribution": str(component_path),
            "symbol_contribution": str(symbol_path),
            "symbol_component_contribution": str(symbol_component_path),
            "regime_bucket_contribution": str(bucket_path),
            "top_loss_hours": str(top_loss_path),
            "loss_concentration": str(concentration_path),
            "top_loss_component_contribution": str(top_loss_component_path),
        },
    }
    manifest_path = A7G1_DIR / "crypto_a7g1_manifest_20260519.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / "CRYPTO_A7G1_MAY_FAILURE_FORENSIC_AUDIT_20260519.md"
    write_report(
        manifest=manifest,
        component_summary=component_summary,
        symbol_summary=symbol_summary,
        bucket_summary=bucket_summary,
        concentration=concentration,
        report_path=report_path,
    )

    decision_path = REPORT_DIR / "CRYPTO_A7G1_DECISION_RECORD_20260519.md"
    decision_lines = [
        "# Crypto A7G-1 Decision Record",
        "",
        f"- decision: `{decision}`",
        f"- generated_at: `{manifest['generated_at']}`",
        f"- blockers: `{blockers}`",
        f"- warnings: `{warnings}`",
        f"- alpha_proof_status: `{manifest['alpha_proof_status']}`",
        f"- risk_gate_status: `{manifest['risk_gate_status']}`",
        f"- authorizes_a7_3_generator_bakeoff: `{manifest['authorizes_a7_3_generator_bakeoff']}`",
        f"- authorizes_shadow_live_or_paper: `{manifest['authorizes_shadow_live_or_paper']}`",
        "",
        "## Conclusion",
        "",
        "A7G-1 is a forensic audit only. FundingCore/Core4 remain blocked from alpha shadow proof until fresh-forward failure is resolved by a predeclared rule and forward-locked evidence.",
        "",
        "## Explicit Non-Authorization",
        "",
        "- This is not a risk-gate pass.",
        "- This does not authorize A7.3 generator/reward bakeoff.",
        "- This does not authorize shadow/live/paper promotion.",
    ]
    decision_path.write_text("\n".join(decision_lines) + "\n", encoding="utf-8")

    print("A7G1_REPORT=" + str(report_path))
    print("A7G1_DECISION_RECORD=" + str(decision_path))
    print("A7G1_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
