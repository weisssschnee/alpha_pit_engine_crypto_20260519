from __future__ import annotations

import json
import math
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
    CandidateSpec,
    clean_float,
    load_core4_context,
    load_core4_specs,
    split_mask,
    summarize_returns,
)
from crypto_a7b_funding_baseline_audit import object_raw_book, residualize, scale_book
from crypto_a7c_fundingcore_narrow_audit import fundingcore_specs, summarize_scaled
from crypto_a7d_funding_time_semantics_audit import variant_matrices
from crypto_a2_strict_replay import MatrixContext


A7H0_DIR = RUNTIME_DIR / "a7h0_nonfunding_residual_smoke"
PRIMARY_COST_NAME = "stress_10bp"
PRIMARY_COST_BPS = COST_BPS[PRIMARY_COST_NAME]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def a7h_candidates() -> list[CandidateSpec]:
    return [
        CandidateSpec("a7h_basis_rank_mark_ratio_h6", "a7h_basis_001", "Rank(mark_index_ratio)", 6, "basis_premium"),
        CandidateSpec("a7h_basis_z_mark_ratio_h12", "a7h_basis_002", "ZScore(mark_index_ratio)", 12, "basis_premium"),
        CandidateSpec("a7h_basis_rank_mark_minus_h6", "a7h_basis_003", "Rank(mark_minus_index)", 6, "basis_premium"),
        CandidateSpec("a7h_basis_rank_premium_h12", "a7h_basis_004", "Rank(premium_index)", 12, "basis_premium"),
        CandidateSpec("a7h_basis_ret_interaction_h6", "a7h_basis_005", "Mul(Rank(mark_index_ratio),Rank(ret_12))", 6, "basis_premium"),
        CandidateSpec("a7h_flow_rank_taker_imbalance_h6", "a7h_flow_001", "Rank(taker_imbalance)", 6, "flow_liquidity"),
        CandidateSpec("a7h_flow_z_taker_imbalance_h12", "a7h_flow_002", "ZScore(taker_imbalance)", 12, "flow_liquidity"),
        CandidateSpec("a7h_flow_rank_quote_volume_h6", "a7h_flow_003", "Rank(quote_asset_volume)", 6, "flow_liquidity"),
        CandidateSpec("a7h_flow_ret_interaction_h6", "a7h_flow_004", "Mul(Rank(taker_imbalance),Rank(ret_12))", 6, "flow_liquidity"),
        CandidateSpec("a7h_liquidity_size_h12", "a7h_flow_005", "Rank(avg_trade_size_quote)", 12, "flow_liquidity"),
        CandidateSpec("a7h_micro_rank_hl_range_h6", "a7h_micro_001", "Rank(hl_range)", 6, "microstructure_lite"),
        CandidateSpec("a7h_micro_rank_realized_vol_h12", "a7h_micro_002", "Rank(realized_vol_12)", 12, "microstructure_lite"),
        CandidateSpec("a7h_micro_rank_absret_h6", "a7h_micro_003", "Rank(abs_ret_1)", 6, "microstructure_lite"),
        CandidateSpec("a7h_micro_ret_vol_interaction_h6", "a7h_micro_004", "Mul(Rank(realized_vol_12),Rank(ret_12))", 6, "microstructure_lite"),
        CandidateSpec("a7h_micro_ret_range_interaction_h12", "a7h_micro_005", "Mul(Rank(hl_range),Rank(ret_12))", 12, "microstructure_lite"),
    ]


def candidate_features(specs: list[CandidateSpec]) -> list[str]:
    known = [
        "ret_12",
        "mark_index_ratio",
        "mark_minus_index",
        "premium_index",
        "taker_imbalance",
        "quote_asset_volume",
        "avg_trade_size_quote",
        "hl_range",
        "realized_vol_12",
        "abs_ret_1",
    ]
    return known


def linear_beta(y: pd.Series, x: pd.Series, mask: np.ndarray) -> tuple[float | None, float | None]:
    yy = y.to_numpy(dtype=float)[mask]
    xx = x.to_numpy(dtype=float)[mask]
    valid = np.isfinite(yy) & np.isfinite(xx)
    if valid.sum() < 50 or np.nanvar(xx[valid]) <= 0:
        return None, None
    beta, alpha = np.polyfit(xx[valid], yy[valid], 1)
    corr = np.corrcoef(xx[valid], yy[valid])[0, 1]
    return clean_float(beta), clean_float(corr)


def scaled_book_for_specs(index: pd.DatetimeIndex, matrices: dict[str, np.ndarray], ctx: MatrixContext, specs: list[CandidateSpec]) -> pd.DataFrame:
    raw, _ = object_raw_book(index, matrices, ctx, specs)
    return scale_book(raw, PRIMARY_COST_BPS)


def summarize_candidate(
    *,
    spec: CandidateSpec,
    scaled: pd.DataFrame,
    residual_funding: pd.DataFrame,
    residual_core4: pd.DataFrame,
    funding_scaled: pd.DataFrame,
    core4_scaled: pd.DataFrame,
    wrong_lag_scaled: pd.DataFrame,
) -> pd.DataFrame:
    ts = pd.DatetimeIndex(pd.to_datetime(scaled["timestamp"], utc=True))
    rows = []
    for split_name in SPLITS:
        mask = split_mask(ts, split_name)
        raw_st = summarize_returns(scaled.loc[mask, "net_return"].to_numpy(dtype=float))
        rf_st = summarize_returns(residual_funding.loc[mask, "net_return"].to_numpy(dtype=float))
        rc_st = summarize_returns(residual_core4.loc[mask, "net_return"].to_numpy(dtype=float))
        funding_beta, funding_corr = linear_beta(scaled["net_return"], funding_scaled["net_return"], mask)
        core4_beta, core4_corr = linear_beta(scaled["net_return"], core4_scaled["net_return"], mask)
        wrong_beta, wrong_corr = linear_beta(scaled["net_return"], wrong_lag_scaled["net_return"], mask)
        rows.append(
            {
                "candidate_id": spec.candidate_id,
                "cluster_id": spec.cluster_id,
                "family": spec.family,
                "expression": spec.expression,
                "horizon": spec.horizon,
                "cost_tier": PRIMARY_COST_NAME,
                "split": split_name,
                "raw_ann": raw_st.get("annualized_mean"),
                "raw_dd": raw_st.get("compounded_max_dd"),
                "raw_hit_rate": raw_st.get("hit_rate"),
                "residual_vs_funding_ann": rf_st.get("annualized_mean"),
                "residual_vs_funding_dd": rf_st.get("compounded_max_dd"),
                "residual_vs_core4_ann": rc_st.get("annualized_mean"),
                "residual_vs_core4_dd": rc_st.get("compounded_max_dd"),
                "funding_beta": funding_beta,
                "funding_corr": funding_corr,
                "core4_beta": core4_beta,
                "core4_corr": core4_corr,
                "wrong_lag_future_funding_beta": wrong_beta,
                "wrong_lag_future_funding_corr": wrong_corr,
                "mean_turnover": clean_float(scaled.loc[mask, "turnover"].mean()),
                "mean_gross_exposure": clean_float(scaled.loc[mask, "gross_exposure"].mean()),
            }
        )
    return pd.DataFrame(rows)


def symbol_loo_summary(
    *,
    symbols: list[str],
    spec: CandidateSpec,
) -> pd.DataFrame:
    rows = []
    for symbol in symbols:
        for split_name in ["recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]:
            rows.append(
                {
                    "candidate_id": spec.candidate_id,
                    "held_out_symbol": symbol,
                    "split": split_name,
                    "loo_mode": "placeholder_no_symbol_mask",
                    "annualized_mean": None,
                    "compounded_max_dd": None,
                }
            )
    return pd.DataFrame(rows)


def write_contract(path: Path, now: str) -> dict[str, Any]:
    contract = {
        "contract_id": "crypto_a7h0_nonfunding_residual_contract_v1",
        "created_at": now,
        "stage": "A7H-0 residualization contract + non-funding smoke",
        "scope": {
            "allowed_result": "PASS_A7H_METHOD_SMOKE_CANDIDATE or HOLD_A7H_NO_RESIDUAL_CANDIDATE",
            "forbidden_result": [
                "alpha_shadow_proof",
                "paper_ready",
                "live_ready",
                "production_ready",
                "generator_bakeoff_pass",
            ],
            "search_policy": "fixed small candidate set only; no formula tuning from May outcome",
        },
        "mandatory_reports_per_candidate": [
            "raw_performance",
            "residual_vs_FundingCore",
            "residual_vs_Core4",
            "funding_exposure_beta",
            "wrong_lag_future_funding_diagnostic",
            "fresh_May_behavior",
            "symbol_LOO_or_explicit_placeholder",
            "cost_stress_10bps_primary",
        ],
        "funding_baselines": {
            "FundingCore": "mandatory benchmark and residualization baseline",
            "Core4": "secondary residualization baseline",
            "wrong_lag_future_funding": "diagnostic only; cannot be used as signal",
        },
        "decision_boundary": {
            "pass_method_smoke": [
                "at least one non-funding candidate has positive validation and recent residual_vs_FundingCore",
                "fresh May is not a broad FundingCore-like collapse",
                "funding beta does not explain main return",
            ],
            "hold": [
                "no residual candidate",
                "candidate performance primarily explained by FundingCore/Core4",
                "fresh May resembles funding-family failure",
            ],
        },
    }
    write_json(path, contract)
    return contract


def main() -> int:
    A7H0_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    specs = a7h_candidates()
    index, symbols, matrices, ctx = load_core4_context(extra_features=candidate_features(specs))

    funding_scaled = scaled_book_for_specs(index, matrices, ctx, fundingcore_specs())
    core4_scaled = scaled_book_for_specs(index, matrices, ctx, load_core4_specs())
    wrong_lag_matrices = variant_matrices(matrices, "F7_wrong_lag_future_24h")
    wrong_lag_scaled = scaled_book_for_specs(index, wrong_lag_matrices, MatrixContext(wrong_lag_matrices), fundingcore_specs())

    all_rows = []
    all_loo = []
    raw_paths = {}
    for spec in specs:
        scaled = scaled_book_for_specs(index, matrices, ctx, [spec])
        residual_funding = residualize(scaled, funding_scaled)
        residual_core4 = residualize(scaled, core4_scaled)
        all_rows.append(
            summarize_candidate(
                spec=spec,
                scaled=scaled,
                residual_funding=residual_funding,
                residual_core4=residual_core4,
                funding_scaled=funding_scaled,
                core4_scaled=core4_scaled,
                wrong_lag_scaled=wrong_lag_scaled,
            )
        )
        all_loo.append(symbol_loo_summary(symbols=symbols, spec=spec))

    metrics = pd.concat(all_rows, ignore_index=True)
    loo = pd.concat(all_loo, ignore_index=True)
    contract_path = REPORT_DIR / "CRYPTO_A7H0_NONFUNDING_RESIDUAL_CONTRACT_20260519.json"
    contract = write_contract(contract_path, now)

    metrics_path = A7H0_DIR / "crypto_a7h0_nonfunding_residual_metrics_20260519.csv"
    loo_path = A7H0_DIR / "crypto_a7h0_symbol_loo_placeholder_20260519.csv"
    metrics.to_csv(metrics_path, index=False)
    loo.to_csv(loo_path, index=False)

    def split_metric(candidate_id: str, split: str, col: str) -> float | None:
        row = metrics[(metrics["candidate_id"] == candidate_id) & (metrics["split"] == split)]
        if row.empty:
            return None
        return clean_float(row.iloc[0][col])

    candidate_rows = []
    for spec in specs:
        val_res = split_metric(spec.candidate_id, "validation_2025H1", "residual_vs_funding_ann")
        recent_res = split_metric(spec.candidate_id, "recent_oos_2025H2_2026Apr", "residual_vs_funding_ann")
        may_raw = split_metric(spec.candidate_id, "fresh_forward_2026May", "raw_ann")
        may_res_funding = split_metric(spec.candidate_id, "fresh_forward_2026May", "residual_vs_funding_ann")
        may_res_core4 = split_metric(spec.candidate_id, "fresh_forward_2026May", "residual_vs_core4_ann")
        recent_beta = split_metric(spec.candidate_id, "recent_oos_2025H2_2026Apr", "funding_beta")
        recent_wrong_corr = split_metric(spec.candidate_id, "recent_oos_2025H2_2026Apr", "wrong_lag_future_funding_corr")
        pass_flag = (
            val_res is not None
            and recent_res is not None
            and may_res_funding is not None
            and may_res_core4 is not None
            and val_res > 0
            and recent_res > 0
            and may_res_funding >= 0
            and may_res_core4 >= 0
            and (recent_beta is None or abs(recent_beta) < 0.75)
            and (recent_wrong_corr is None or abs(recent_wrong_corr) < 0.70)
        )
        candidate_rows.append(
            {
                "candidate_id": spec.candidate_id,
                "family": spec.family,
                "expression": spec.expression,
                "validation_residual_vs_funding_ann": val_res,
                "recent_residual_vs_funding_ann": recent_res,
                "fresh_may_raw_ann": may_raw,
                "fresh_may_residual_vs_funding_ann": may_res_funding,
                "fresh_may_residual_vs_core4_ann": may_res_core4,
                "recent_funding_beta": recent_beta,
                "recent_wrong_lag_future_funding_corr": recent_wrong_corr,
                "method_smoke_pass": bool(pass_flag),
            }
        )
    candidate_summary = pd.DataFrame(candidate_rows).sort_values(
        ["method_smoke_pass", "recent_residual_vs_funding_ann"], ascending=[False, False]
    )
    candidate_summary_path = A7H0_DIR / "crypto_a7h0_candidate_summary_20260519.csv"
    candidate_summary.to_csv(candidate_summary_path, index=False)

    pass_count = int(candidate_summary["method_smoke_pass"].sum())
    decision = "PASS_A7H_METHOD_SMOKE_CANDIDATE" if pass_count > 0 else "HOLD_A7H_NO_RESIDUAL_CANDIDATE"
    warnings = [
        "symbol_loo_is_placeholder_until_masked_replay_path_is_added",
        "a7h0_is_method_smoke_not_generator_bakeoff",
        "fundingcore_and_core4_remain_mandatory_residual_baselines",
    ]
    if bool((candidate_summary["fresh_may_raw_ann"] < 0).all()):
        warnings.append("fresh_may_raw_negative_for_all_nonfunding_candidates")
    manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "pass_candidate_count": pass_count,
        "candidate_count": len(specs),
        "cost_tier": PRIMARY_COST_NAME,
        "purge_embargo_bars": PURGE_EMBARGO_BARS,
        "warnings": warnings,
        "outputs": {
            "contract": str(contract_path),
            "metrics": str(metrics_path),
            "candidate_summary": str(candidate_summary_path),
            "symbol_loo_placeholder": str(loo_path),
        },
    }
    manifest_path = A7H0_DIR / "crypto_a7h0_manifest_20260519.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / "CRYPTO_A7H0_NONFUNDING_RESIDUAL_SMOKE_20260519.md"
    lines = [
        "# Crypto A7H-0 Non-Funding Residual Smoke",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- evidence_level: `method_smoke_only_not_alpha_proof`",
        f"- pass_candidate_count: `{pass_count}`",
        f"- candidate_count: `{len(specs)}`",
        "",
        "## Contract Boundary",
        "",
        "- No search expansion, no formula tuning, no promotion.",
        "- Every candidate is measured raw, residual vs FundingCore, residual vs Core4, and against wrong-lag future funding diagnostic.",
        "- FundingCore/Core4 remain mandatory residual baselines.",
        "",
        "## Top Candidate Summary",
        "",
        "| candidate | family | val residual funding | recent residual funding | May raw | May residual funding | May residual Core4 | recent funding beta | wrong-lag corr | pass |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in candidate_summary.head(20).iterrows():
        lines.append(
            f"| `{row['candidate_id']}` | `{row['family']}` | "
            f"{row['validation_residual_vs_funding_ann'] if pd.notna(row['validation_residual_vs_funding_ann']) else 0:.4f} | "
            f"{row['recent_residual_vs_funding_ann'] if pd.notna(row['recent_residual_vs_funding_ann']) else 0:.4f} | "
            f"{row['fresh_may_raw_ann'] if pd.notna(row['fresh_may_raw_ann']) else 0:.4f} | "
            f"{row['fresh_may_residual_vs_funding_ann'] if pd.notna(row['fresh_may_residual_vs_funding_ann']) else 0:.4f} | "
            f"{row['fresh_may_residual_vs_core4_ann'] if pd.notna(row['fresh_may_residual_vs_core4_ann']) else 0:.4f} | "
            f"{row['recent_funding_beta'] if pd.notna(row['recent_funding_beta']) else 0:.4f} | "
            f"{row['recent_wrong_lag_future_funding_corr'] if pd.notna(row['recent_wrong_lag_future_funding_corr']) else 0:.4f} | "
            f"`{bool(row['method_smoke_pass'])}` |"
        )
    lines += [
        "",
        "## Decision",
        "",
        "- PASS here only means a non-funding residual candidate exists for further audit.",
        "- HOLD means this fixed non-funding smoke did not find a candidate independent enough from FundingCore/Core4.",
        "- This report does not authorize A7.3, shadow, paper, live, or production claims.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("A7H0_REPORT=" + str(report_path))
    print("A7H0_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
