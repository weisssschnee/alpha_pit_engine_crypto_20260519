from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a2_strict_replay import MatrixContext
from crypto_a7_validation_utils import (
    COST_BPS,
    PURGE_EMBARGO_BARS,
    REPORT_DIR,
    RUNTIME_DIR,
    SPLITS,
    CandidateSpec,
    clean_float,
    eval_expression,
    load_core4_context,
    load_core4_specs,
    split_mask,
    summarize_returns,
)
from crypto_a7b_funding_baseline_audit import residualize, scale_book
from crypto_a7c_fundingcore_narrow_audit import fundingcore_specs
from crypto_a7h0_nonfunding_residual_smoke import a7h_candidates, candidate_features


A7H1_DIR = RUNTIME_DIR / "a7h1_nonfunding_masked_loo_audit"
PRIMARY_COST_NAME = "stress_10bp"
PRIMARY_COST_BPS = COST_BPS[PRIMARY_COST_NAME]
PASS_IDS = {"a7h_liquidity_size_h12", "a7h_flow_rank_taker_imbalance_h6"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def selected_specs() -> list[CandidateSpec]:
    return [s for s in a7h_candidates() if s.candidate_id in PASS_IDS]


def raw_book_from_specs_masked(
    *,
    index: pd.DatetimeIndex,
    matrices: dict[str, np.ndarray],
    ctx: MatrixContext,
    specs: list[CandidateSpec],
    symbols_to_keep: np.ndarray | None = None,
) -> pd.DataFrame:
    frames = []
    for spec in specs:
        frame, _ = eval_expression(
            index=index,
            matrices=matrices,
            ctx=ctx,
            expression=spec.expression,
            horizon=spec.horizon,
            cost_bps=0.0,
            symbols_to_keep=symbols_to_keep,
        )
        frame = frame.copy()
        frame["component_id"] = spec.cluster_id
        frames.append(frame)
    comp = pd.concat(frames, ignore_index=True)
    book = pd.DataFrame({"timestamp": index})
    for col in ["gross_return", "funding_drag", "turnover", "fee_drag", "net_return", "gross_exposure", "net_exposure"]:
        pivot = comp.pivot(index="timestamp", columns="component_id", values=col)
        book[col] = pivot.mean(axis=1, skipna=True).to_numpy(dtype=float)
    return book.rename(columns={"net_return": "pre_fee_return"})


def summarize_scaled_object(object_name: str, scaled: pd.DataFrame, cost_name: str) -> pd.DataFrame:
    ts = pd.DatetimeIndex(pd.to_datetime(scaled["timestamp"], utc=True))
    rows = []
    for split_name in SPLITS:
        mask = split_mask(ts, split_name)
        st = summarize_returns(scaled.loc[mask, "net_return"].to_numpy(dtype=float))
        rows.append(
            {
                "object": object_name,
                "cost_tier": cost_name,
                "split": split_name,
                **st,
                "mean_turnover": clean_float(scaled.loc[mask, "turnover"].mean()),
                "mean_gross_exposure": clean_float(scaled.loc[mask, "gross_exposure"].mean()),
            }
        )
    return pd.DataFrame(rows)


def monthly_summary(candidate_id: str, frame: pd.DataFrame, value_col: str, label: str) -> pd.DataFrame:
    part = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(frame["timestamp"], utc=True),
            "value": frame[value_col].to_numpy(dtype=float),
        }
    )
    part = part[np.isfinite(part["value"])].copy()
    if part.empty:
        return pd.DataFrame()
    part["month"] = part["timestamp"].dt.strftime("%Y-%m")
    out = (
        part.groupby("month", as_index=False)
        .agg(
            hour_count=("value", "size"),
            month_sum=("value", "sum"),
            mean_hour=("value", "mean"),
            hit_rate=("value", lambda x: float((x > 0).mean())),
            worst_hour=("value", "min"),
        )
        .assign(candidate_id=candidate_id, series=label)
    )
    return out[["candidate_id", "series", "month", "hour_count", "month_sum", "mean_hour", "hit_rate", "worst_hour"]]


def top_loss_hours(candidate_id: str, scaled: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    part = scaled.copy()
    part["timestamp"] = pd.to_datetime(part["timestamp"], utc=True)
    part = part.sort_values("net_return").head(n)
    return part.assign(candidate_id=candidate_id)[
        ["candidate_id", "timestamp", "net_return", "gross_exposure", "turnover", "funding_drag"]
    ]


def split_metric(frame: pd.DataFrame, split: str, col: str) -> float | None:
    row = frame[frame["split"] == split]
    if row.empty or col not in row.columns:
        return None
    return clean_float(row.iloc[0][col])


def evaluate_candidate(
    *,
    spec: CandidateSpec,
    index: pd.DatetimeIndex,
    symbols: list[str],
    matrices: dict[str, np.ndarray],
    ctx: MatrixContext,
    funding_specs: list[CandidateSpec],
    core4_specs: list[CandidateSpec],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    candidate_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=[spec])
    funding_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=funding_specs)
    core4_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=core4_specs)

    metric_rows = []
    cost_rows = []
    month_rows = []
    top_loss_rows = []
    for cost_name, cost_bps in COST_BPS.items():
        candidate_scaled = scale_book(candidate_raw, cost_bps)
        funding_scaled = scale_book(funding_raw, cost_bps)
        core4_scaled = scale_book(core4_raw, cost_bps)
        residual_funding = residualize(candidate_scaled, funding_scaled)
        residual_core4 = residualize(candidate_scaled, core4_scaled)
        raw_summary = summarize_scaled_object("raw", candidate_scaled, cost_name)
        rf_summary = summarize_scaled_object("residual_vs_funding", residual_funding, cost_name)
        rc_summary = summarize_scaled_object("residual_vs_core4", residual_core4, cost_name)
        for frame, series in [(raw_summary, "raw"), (rf_summary, "residual_vs_funding"), (rc_summary, "residual_vs_core4")]:
            part = frame.copy()
            part.insert(0, "candidate_id", spec.candidate_id)
            part.insert(1, "series", series)
            cost_rows.append(part)
        if cost_name == PRIMARY_COST_NAME:
            raw_summary = raw_summary.rename(columns={"annualized_mean": "raw_ann", "compounded_max_dd": "raw_dd"})
            rf_summary = rf_summary.rename(
                columns={"annualized_mean": "residual_vs_funding_ann", "compounded_max_dd": "residual_vs_funding_dd"}
            )
            rc_summary = rc_summary.rename(
                columns={"annualized_mean": "residual_vs_core4_ann", "compounded_max_dd": "residual_vs_core4_dd"}
            )
            merged = raw_summary[["split", "raw_ann", "raw_dd", "hit_rate", "mean_turnover", "mean_gross_exposure"]].merge(
                rf_summary[["split", "residual_vs_funding_ann", "residual_vs_funding_dd"]],
                on="split",
                how="left",
            )
            merged = merged.merge(
                rc_summary[["split", "residual_vs_core4_ann", "residual_vs_core4_dd"]],
                on="split",
                how="left",
            )
            merged.insert(0, "candidate_id", spec.candidate_id)
            merged.insert(1, "family", spec.family)
            merged.insert(2, "expression", spec.expression)
            merged.insert(3, "horizon", spec.horizon)
            metric_rows.append(merged)
            month_rows.append(monthly_summary(spec.candidate_id, candidate_scaled, "net_return", "raw"))
            month_rows.append(monthly_summary(spec.candidate_id, residual_funding, "net_return", "residual_vs_funding"))
            month_rows.append(monthly_summary(spec.candidate_id, residual_core4, "net_return", "residual_vs_core4"))
            top_loss_rows.append(top_loss_hours(spec.candidate_id, candidate_scaled))

    loo_rows = []
    for held_out in symbols:
        keep = np.asarray([s != held_out for s in symbols])
        candidate_raw_loo = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=[spec], symbols_to_keep=keep)
        funding_raw_loo = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=funding_specs, symbols_to_keep=keep)
        core4_raw_loo = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=core4_specs, symbols_to_keep=keep)
        candidate_scaled_loo = scale_book(candidate_raw_loo, PRIMARY_COST_BPS)
        funding_scaled_loo = scale_book(funding_raw_loo, PRIMARY_COST_BPS)
        core4_scaled_loo = scale_book(core4_raw_loo, PRIMARY_COST_BPS)
        residual_funding_loo = residualize(candidate_scaled_loo, funding_scaled_loo)
        residual_core4_loo = residualize(candidate_scaled_loo, core4_scaled_loo)
        ts = pd.DatetimeIndex(pd.to_datetime(candidate_scaled_loo["timestamp"], utc=True))
        for split_name in ["validation_2025H1", "recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]:
            mask = split_mask(ts, split_name)
            raw_st = summarize_returns(candidate_scaled_loo.loc[mask, "net_return"].to_numpy(dtype=float))
            rf_st = summarize_returns(residual_funding_loo.loc[mask, "net_return"].to_numpy(dtype=float))
            rc_st = summarize_returns(residual_core4_loo.loc[mask, "net_return"].to_numpy(dtype=float))
            loo_rows.append(
                {
                    "candidate_id": spec.candidate_id,
                    "held_out_symbol": held_out,
                    "split": split_name,
                    "raw_ann": raw_st.get("annualized_mean"),
                    "raw_dd": raw_st.get("compounded_max_dd"),
                    "residual_vs_funding_ann": rf_st.get("annualized_mean"),
                    "residual_vs_funding_dd": rf_st.get("compounded_max_dd"),
                    "residual_vs_core4_ann": rc_st.get("annualized_mean"),
                    "residual_vs_core4_dd": rc_st.get("compounded_max_dd"),
                }
            )

    return (
        pd.concat(metric_rows, ignore_index=True),
        pd.concat(cost_rows, ignore_index=True),
        pd.DataFrame(loo_rows),
        pd.concat(month_rows, ignore_index=True),
        pd.concat(top_loss_rows, ignore_index=True),
    )


def main() -> int:
    A7H1_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    specs = selected_specs()
    index, symbols, matrices, ctx = load_core4_context(extra_features=candidate_features(specs))
    funding_specs = fundingcore_specs()
    core4_specs = load_core4_specs()

    metrics_parts = []
    cost_parts = []
    loo_parts = []
    month_parts = []
    top_loss_parts = []
    for spec in specs:
        metrics, cost_stress, loo, months, top_losses = evaluate_candidate(
            spec=spec,
            index=index,
            symbols=symbols,
            matrices=matrices,
            ctx=ctx,
            funding_specs=funding_specs,
            core4_specs=core4_specs,
        )
        metrics_parts.append(metrics)
        cost_parts.append(cost_stress)
        loo_parts.append(loo)
        month_parts.append(months)
        top_loss_parts.append(top_losses)

    metrics = pd.concat(metrics_parts, ignore_index=True)
    cost_stress = pd.concat(cost_parts, ignore_index=True)
    loo = pd.concat(loo_parts, ignore_index=True)
    months = pd.concat(month_parts, ignore_index=True)
    top_losses = pd.concat(top_loss_parts, ignore_index=True)

    metrics_path = A7H1_DIR / "crypto_a7h1_candidate_metrics_20260519.csv"
    cost_path = A7H1_DIR / "crypto_a7h1_cost_stress_20260519.csv"
    loo_path = A7H1_DIR / "crypto_a7h1_masked_symbol_loo_20260519.csv"
    month_path = A7H1_DIR / "crypto_a7h1_monthly_series_20260519.csv"
    top_loss_path = A7H1_DIR / "crypto_a7h1_top_loss_hours_20260519.csv"
    metrics.to_csv(metrics_path, index=False)
    cost_stress.to_csv(cost_path, index=False)
    loo.to_csv(loo_path, index=False)
    months.to_csv(month_path, index=False)
    top_losses.to_csv(top_loss_path, index=False)

    summary_rows = []
    for spec in specs:
        cand = metrics[metrics["candidate_id"] == spec.candidate_id]
        loo_cand = loo[loo["candidate_id"] == spec.candidate_id]
        recent_loo = loo_cand[loo_cand["split"] == "recent_oos_2025H2_2026Apr"]
        may_loo = loo_cand[loo_cand["split"] == "fresh_forward_2026May"]
        def m(split: str, col: str) -> float | None:
            row = cand[cand["split"] == split]
            if row.empty:
                return None
            return clean_float(row.iloc[0][col])
        val_rf_dd = m("validation_2025H1", "residual_vs_funding_dd")
        recent_rf_dd = m("recent_oos_2025H2_2026Apr", "residual_vs_funding_dd")
        may_rf_dd = m("fresh_forward_2026May", "residual_vs_funding_dd")
        summary_rows.append(
            {
                "candidate_id": spec.candidate_id,
                "family": spec.family,
                "expression": spec.expression,
                "validation_residual_vs_funding_ann": m("validation_2025H1", "residual_vs_funding_ann"),
                "validation_residual_vs_funding_dd": val_rf_dd,
                "recent_residual_vs_funding_ann": m("recent_oos_2025H2_2026Apr", "residual_vs_funding_ann"),
                "recent_residual_vs_funding_dd": recent_rf_dd,
                "fresh_may_residual_vs_funding_ann": m("fresh_forward_2026May", "residual_vs_funding_ann"),
                "fresh_may_residual_vs_funding_dd": may_rf_dd,
                "fresh_may_residual_vs_core4_ann": m("fresh_forward_2026May", "residual_vs_core4_ann"),
                "fresh_may_raw_ann": m("fresh_forward_2026May", "raw_ann"),
                "recent_loo_residual_vs_funding_positive_rate": clean_float(
                    (recent_loo["residual_vs_funding_ann"] > 0).mean()
                ),
                "may_loo_residual_vs_funding_positive_rate": clean_float(
                    (may_loo["residual_vs_funding_ann"] > 0).mean()
                ),
                "recent_loo_residual_vs_funding_min_ann": clean_float(recent_loo["residual_vs_funding_ann"].min()),
                "may_loo_residual_vs_funding_min_ann": clean_float(may_loo["residual_vs_funding_ann"].min()),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary["a7h1_audit_pass"] = (
        (summary["validation_residual_vs_funding_ann"] > 0)
        & (summary["recent_residual_vs_funding_ann"] > 0)
        & (summary["fresh_may_residual_vs_funding_ann"] >= 0)
        & (summary["fresh_may_residual_vs_core4_ann"] >= 0)
        & (summary["validation_residual_vs_funding_dd"] >= -0.35)
        & (summary["recent_residual_vs_funding_dd"] >= -0.35)
        & (summary["fresh_may_residual_vs_funding_dd"] >= -0.12)
        & (summary["recent_loo_residual_vs_funding_positive_rate"] >= 0.75)
        & (summary["may_loo_residual_vs_funding_positive_rate"] >= 0.50)
        & (summary["may_loo_residual_vs_funding_min_ann"] >= -1.0)
    )
    summary_path = A7H1_DIR / "crypto_a7h1_candidate_summary_20260519.csv"
    summary.to_csv(summary_path, index=False)

    pass_count = int(summary["a7h1_audit_pass"].sum())
    decision = "PASS_A7H1_RESIDUAL_CANDIDATE_AUDIT" if pass_count > 0 else "HOLD_A7H1_NO_ROBUST_RESIDUAL_CANDIDATE"
    warnings = [
        "a7h1_is_not_alpha_shadow_proof",
        "a7h1_does_not_authorize_generator_bakeoff",
        "candidate_raw_may_can_remain_negative_even_when_residual_is_positive",
    ]
    manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "pass_count": pass_count,
        "candidate_count": len(specs),
        "cost_tier": PRIMARY_COST_NAME,
        "purge_embargo_bars": PURGE_EMBARGO_BARS,
        "warnings": warnings,
        "outputs": {
            "candidate_metrics": str(metrics_path),
            "cost_stress": str(cost_path),
            "masked_symbol_loo": str(loo_path),
            "monthly_series": str(month_path),
            "top_loss_hours": str(top_loss_path),
            "candidate_summary": str(summary_path),
        },
    }
    manifest_path = A7H1_DIR / "crypto_a7h1_manifest_20260519.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / "CRYPTO_A7H1_NONFUNDING_MASKED_LOO_AUDIT_20260519.md"
    lines = [
        "# Crypto A7H-1 Non-Funding Masked LOO Audit",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- evidence_level: `candidate_audit_only_not_alpha_proof`",
        f"- pass_count: `{pass_count}`",
        f"- candidate_count: `{len(specs)}`",
        "",
        "## Scope",
        "",
        "- Only A7H-0 pass candidates are audited.",
        "- No search expansion, no formula tuning, no shadow promotion.",
        "- Masked symbol LOO is computed by excluding each held-out symbol from candidate, FundingCore, and Core4 replay before residualization.",
        "",
        "## Candidate Summary",
        "",
        "| candidate | val residual funding | recent residual funding | May residual funding | May residual Core4 | May raw | recent LOO+ | May LOO+ | pass |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| `{row['candidate_id']}` | "
            f"{row['validation_residual_vs_funding_ann']:.4f} | "
            f"{row['recent_residual_vs_funding_ann']:.4f} | "
            f"{row['fresh_may_residual_vs_funding_ann']:.4f} | "
            f"{row['fresh_may_residual_vs_core4_ann']:.4f} | "
            f"{row['fresh_may_raw_ann']:.4f} | "
            f"{row['recent_loo_residual_vs_funding_positive_rate']:.3f} | "
            f"{row['may_loo_residual_vs_funding_positive_rate']:.3f} | "
            f"`{bool(row['a7h1_audit_pass'])}` |"
        )
    lines += [
        "",
        "## Decision Boundary",
        "",
        "- PASS only means a non-funding residual candidate is robust enough for deeper A7H-2 audit.",
        "- This does not authorize A7.3 generator bakeoff, dry-shadow evidence, paper, live, or production claims.",
        "- If no candidate passes masked LOO, non-funding residual line remains research-only.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / "CRYPTO_A7H1_DECISION_RECORD_20260519.md"
    decision_lines = [
        "# Crypto A7H-1 Decision Record",
        "",
        f"- decision: `{decision}`",
        f"- alpha_proof_status: `{manifest['alpha_proof_status']}`",
        f"- pass_count: `{pass_count}`",
        f"- warnings: `{warnings}`",
        "",
        "## Conclusion",
        "",
        "A7H-1 audits the two A7H-0 residual candidates with masked symbol LOO and cost-consistent residualization. It is not alpha proof.",
    ]
    decision_path.write_text("\n".join(decision_lines) + "\n", encoding="utf-8")

    print("A7H1_REPORT=" + str(report_path))
    print("A7H1_DECISION_RECORD=" + str(decision_path))
    print("A7H1_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
