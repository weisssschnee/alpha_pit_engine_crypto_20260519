from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7_validation_utils import (
    COST_BPS,
    REPORT_DIR,
    RUNTIME_DIR,
    SPLITS,
    clean_float,
    load_core4_context,
    split_mask,
    summarize_returns,
)
from crypto_a7b_funding_baseline_audit import residualize, scale_book
from crypto_a7c_fundingcore_narrow_audit import fundingcore_specs
from crypto_a7i1a_runner_preflight import (
    RunnerCandidate,
    book_from_spec,
    build_rank_components,
    metric_by_split,
)
from crypto_a7h1_nonfunding_masked_loo_audit import raw_book_from_specs_masked
from crypto_a7_validation_utils import load_core4_specs


A7I1B_DIR = RUNTIME_DIR / "a7i1b_matched_budget_smoke"
PRIMARY_COST_NAME = "stress_10bp"
PRIMARY_COST_BPS = COST_BPS[PRIMARY_COST_NAME]
SEVERE_COST_NAME = "severe_20bp"
SEVERE_COST_BPS = COST_BPS[SEVERE_COST_NAME]
GENERATED_PER_ARM = 250
REPLAY_PER_ARM = 64
MAX_SAME_FAMILY_SHORTLIST_SHARE = 0.25


FIELD_GROUPS = {
    "I0_basis_premium": [
        "mark_index_ratio",
        "mark_minus_index",
        "premium_index",
        "spot_perp_basis",
        "ret_1",
        "ret_3",
        "ret_6",
        "ret_12",
        "realized_vol_12",
        "hl_range",
    ],
    "I1_flow_liquidity": [
        "taker_imbalance",
        "taker_buy_ratio",
        "quote_asset_volume",
        "number_of_trades",
        "avg_trade_size_quote",
        "quote_volume_mean_6",
        "quote_volume_mean_12",
        "volume",
        "ret_1",
        "ret_6",
        "ret_12",
    ],
    "I2_microstructure_lite": [
        "hl_range",
        "abs_ret_1",
        "realized_vol_6",
        "realized_vol_12",
        "realized_vol_24",
        "ret_1",
        "ret_3",
        "ret_6",
        "ret_12",
        "quote_volume_mean_12",
    ],
}

ARM_FAMILY = {
    "I0_basis_premium": "basis_premium",
    "I1_flow_liquidity": "flow_liquidity",
    "I2_microstructure_lite": "microstructure_lite",
    "I3_placebo_random": "placebo_random",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def formula_hash(expr: str) -> str:
    return hashlib.sha256(expr.encode("utf-8")).hexdigest()[:16]


def make_exprs(fields: list[str]) -> list[str]:
    exprs: list[str] = []
    for f in fields:
        exprs.extend([f, f"Rank({f})", f"ZScore({f})"])
    wrappers = ["Rank", "ZScore"]
    for i, a in enumerate(fields):
        for j, b in enumerate(fields):
            if a == b:
                continue
            exprs.append(f"Mul(Rank({a}),Rank({b}))")
            exprs.append(f"Mul(ZScore({a}),ZScore({b}))")
            exprs.append(f"Mul(Rank({a}),ZScore({b}))")
            if (i + j) % 3 == 0:
                exprs.append(f"Mul({wrappers[(i + j) % 2]}({a}),Rank(ret_12))")
    # Stable unique order.
    out: list[str] = []
    seen = set()
    for expr in exprs:
        if expr not in seen:
            seen.add(expr)
            out.append(expr)
    return out


def generate_arm(arm: str) -> list[RunnerCandidate]:
    if arm == "I3_placebo_random":
        base = [
            "Rank(taker_imbalance)",
            "Rank(mark_index_ratio)",
            "Rank(hl_range)",
            "Rank(avg_trade_size_quote)",
            "Mul(Rank(mark_index_ratio),Rank(ret_12))",
        ]
        modes = ["random_noise", "row_shuffle", "time_shuffle", "sign_flip", "wrong_lag_stale_24h"]
        candidates = []
        k = 0
        while len(candidates) < GENERATED_PER_ARM:
            expr = base[k % len(base)]
            mode = modes[(k // len(base)) % len(modes)]
            candidates.append(
                RunnerCandidate(
                    candidate_id=f"{arm.lower()}_{k:03d}",
                    expression=expr if mode != "random_noise" else f"RandomNoise({k})",
                    horizon=6 if k % 2 == 0 else 12,
                    family=ARM_FAMILY[arm],
                    object_type="placebo",
                    signal_mode=mode,
                    classification_expected="NEGATIVE_CONTROL",
                )
            )
            k += 1
        return candidates

    exprs = make_exprs(FIELD_GROUPS[arm])
    candidates = []
    horizons = [6, 12]
    for k, expr in enumerate(exprs[:GENERATED_PER_ARM]):
        candidates.append(
            RunnerCandidate(
                candidate_id=f"{arm.lower()}_{k:03d}",
                expression=expr,
                horizon=horizons[k % len(horizons)],
                family=ARM_FAMILY[arm],
                object_type="generated_candidate",
                signal_mode="original",
                classification_expected="PREFLIGHT_TEST_CANDIDATE",
            )
        )
    if len(candidates) != GENERATED_PER_ARM:
        raise RuntimeError(f"{arm} generated {len(candidates)} candidates, expected {GENERATED_PER_ARM}")
    return candidates


def all_candidates() -> list[RunnerCandidate]:
    out = []
    for arm in ["I0_basis_premium", "I1_flow_liquidity", "I2_microstructure_lite", "I3_placebo_random"]:
        out.extend(generate_arm(arm))
    return out


def arm_from_id(candidate_id: str) -> str:
    for arm in ["i0_basis_premium", "i1_flow_liquidity", "i2_microstructure_lite", "i3_placebo_random"]:
        if candidate_id.startswith(arm):
            return arm.upper().replace("I0_", "I0_").replace("I1_", "I1_").replace("I2_", "I2_").replace("I3_", "I3_")
    return "UNKNOWN"


def arm_label(candidate_id: str) -> str:
    if candidate_id.startswith("i0_basis_premium"):
        return "I0_basis_premium"
    if candidate_id.startswith("i1_flow_liquidity"):
        return "I1_flow_liquidity"
    if candidate_id.startswith("i2_microstructure_lite"):
        return "I2_microstructure_lite"
    if candidate_id.startswith("i3_placebo_random"):
        return "I3_placebo_random"
    return "UNKNOWN"


def extract_fields_from_expr(expr: str, fields: set[str]) -> list[str]:
    return sorted([f for f in fields if f in expr])


def score_split(summary: pd.DataFrame, candidate_id: str, series: str, split: str, col: str) -> float | None:
    row = summary[(summary["candidate_id"] == candidate_id) & (summary["series"] == series) & (summary["split"] == split)]
    if row.empty or col not in row:
        return None
    return clean_float(row.iloc[0][col])


def linear_beta(y: pd.Series, x: pd.Series, mask: np.ndarray) -> tuple[float | None, float | None]:
    yy = y.to_numpy(dtype=float)[mask]
    xx = x.to_numpy(dtype=float)[mask]
    valid = np.isfinite(yy) & np.isfinite(xx)
    if valid.sum() < 50 or np.nanvar(xx[valid]) <= 0:
        return None, None
    beta, _ = np.polyfit(xx[valid], yy[valid], 1)
    corr = np.corrcoef(xx[valid], yy[valid])[0, 1]
    return clean_float(beta), clean_float(corr)


def evaluate_candidates(
    *,
    index: pd.DatetimeIndex,
    matrices: dict[str, np.ndarray],
    ctx,
    candidates: list[RunnerCandidate],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    funding_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=fundingcore_specs())
    core4_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=load_core4_specs())
    funding_scaled = scale_book(funding_raw, PRIMARY_COST_BPS)
    core4_scaled = scale_book(core4_raw, PRIMARY_COST_BPS)

    summary_parts = []
    beta_rows = []
    residual_rows = []
    lag_rows = []
    may_rows = []
    for i, candidate in enumerate(candidates, start=1):
        raw, _ = book_from_spec(index=index, matrices=matrices, ctx=ctx, candidate=candidate)
        raw10 = scale_book(raw, PRIMARY_COST_BPS)
        raw20 = scale_book(raw, SEVERE_COST_BPS)
        residual_funding = residualize(raw10, funding_scaled)
        residual_core4 = residualize(raw10, core4_scaled)
        lag_raw, _ = book_from_spec(index=index, matrices=matrices, ctx=ctx, candidate=candidate, signal_lag_bars=1)
        lag10 = scale_book(lag_raw, PRIMARY_COST_BPS)
        for series, frame in [
            ("raw_10bp", raw10),
            ("raw_20bp", raw20),
            ("residual_vs_funding_10bp", residual_funding),
            ("residual_vs_core4_10bp", residual_core4),
            ("execution_lag_1bar_raw_10bp", lag10),
        ]:
            summary_parts.append(
                metric_by_split(
                    frame,
                    "net_return",
                    {
                        "candidate_id": candidate.candidate_id,
                        "arm": arm_label(candidate.candidate_id),
                        "family": candidate.family,
                        "object_type": candidate.object_type,
                        "signal_mode": candidate.signal_mode,
                        "expression": candidate.expression,
                        "expr_hash": formula_hash(candidate.expression),
                        "horizon": candidate.horizon,
                        "series": series,
                    },
                )
            )
        ts = pd.DatetimeIndex(pd.to_datetime(raw10["timestamp"], utc=True))
        for split in ["validation_2025H1", "recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]:
            mask = split_mask(ts, split)
            fb, fcorr = linear_beta(raw10["net_return"], funding_scaled["net_return"], mask)
            cb, ccorr = linear_beta(raw10["net_return"], core4_scaled["net_return"], mask)
            beta_rows.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "arm": arm_label(candidate.candidate_id),
                    "split": split,
                    "funding_beta": fb,
                    "funding_corr": fcorr,
                    "core4_beta": cb,
                    "core4_corr": ccorr,
                }
            )
        residual_rows.extend(
            [
                {
                    "candidate_id": candidate.candidate_id,
                    "baseline": "FundingCore",
                    "beta_train": clean_float(residual_funding["residual_beta_train"].iloc[0]),
                    "alpha_train": clean_float(residual_funding["residual_alpha_train"].iloc[0]),
                    "uses_train_only": True,
                    "uses_may": False,
                },
                {
                    "candidate_id": candidate.candidate_id,
                    "baseline": "Core4",
                    "beta_train": clean_float(residual_core4["residual_beta_train"].iloc[0]),
                    "alpha_train": clean_float(residual_core4["residual_alpha_train"].iloc[0]),
                    "uses_train_only": True,
                    "uses_may": False,
                },
            ]
        )
        lag_rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "arm": arm_label(candidate.candidate_id),
                "lag_bars": 1,
                "lag_frame_rows": int(len(lag10)),
                "lag_output_exists": "net_return" in lag10.columns,
            }
        )
        may_mask = split_mask(ts, "fresh_forward_2026May")
        may_rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "arm": arm_label(candidate.candidate_id),
                "raw_may_10bp_ann_stress_only": summarize_returns(raw10.loc[may_mask, "net_return"].to_numpy(dtype=float)).get(
                    "annualized_mean"
                ),
                "residual_funding_may_ann_stress_only": summarize_returns(
                    residual_funding.loc[may_mask, "net_return"].to_numpy(dtype=float)
                ).get("annualized_mean"),
                "residual_core4_may_ann_stress_only": summarize_returns(
                    residual_core4.loc[may_mask, "net_return"].to_numpy(dtype=float)
                ).get("annualized_mean"),
                "may_used_for_rank": False,
                "may_used_for_selection": False,
            }
        )
        if i % 100 == 0:
            print(f"evaluated {i}/{len(candidates)}")
    return (
        pd.concat(summary_parts, ignore_index=True),
        pd.DataFrame(beta_rows),
        pd.DataFrame(residual_rows),
        pd.DataFrame(lag_rows),
        pd.DataFrame(may_rows),
    )


def duplicate_cluster_audit(candidates: list[RunnerCandidate], selected: pd.DataFrame) -> pd.DataFrame:
    rows = []
    family_counts = Counter(selected["family"].tolist())
    expr_counts = Counter(selected["expr_hash"].tolist())
    total = max(1, len(selected))
    for family, count in sorted(family_counts.items()):
        cap = 1.0 if total < 4 else MAX_SAME_FAMILY_SHORTLIST_SHARE
        rows.append(
            {
                "bucket_type": "family",
                "bucket": family,
                "selected_count": count,
                "selected_share": count / total,
                "cap": cap,
                "cap_pass": (count / total) <= cap,
                "cap_note": "too_few_shortlist_members_for_25pct_cap" if total < 4 else "standard_shortlist_family_cap",
            }
        )
    for expr_hash, count in sorted(expr_counts.items()):
        if count > 1:
            rows.append(
                {
                    "bucket_type": "formula_fingerprint",
                    "bucket": expr_hash,
                "selected_count": count,
                "selected_share": count / total,
                "cap": 1 / total,
                "cap_pass": count == 1,
                "cap_note": "formula_fingerprint_dedup",
            }
        )
    return pd.DataFrame(rows)


def symbol_month_loo_placeholder(selected: pd.DataFrame) -> pd.DataFrame:
    # Full masked symbol LOO is intentionally not run in A7I-1b smoke for all generated candidates.
    # The runner emits an explicit placeholder so promotion gates cannot mistake this for alpha proof.
    rows = []
    for _, row in selected.iterrows():
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "arm": row["arm"],
                "audit_type": "symbol_month_loo",
                "status": "not_run_in_a7i1b_smoke",
                "required_before_alpha_proof": True,
            }
        )
    return pd.DataFrame(rows)


def evaluate_research_candidate(row: pd.Series, beta: pd.DataFrame, may: pd.DataFrame) -> tuple[str, list[str]]:
    cid = row["candidate_id"]
    reasons: list[str] = []
    if row["object_type"] == "placebo":
        return "PLACEBO_NEGATIVE_CONTROL", ["placebo_arm"]
    def sv(series: str, split: str, col: str = "annualized_mean") -> float | None:
        return clean_float(row.get(f"{series}__{split}__{col}"))

    raw_val = sv("raw_10bp", "validation_2025H1")
    raw_recent = sv("raw_10bp", "recent_oos_2025H2_2026Apr")
    raw_may = clean_float(may.loc[may["candidate_id"] == cid, "raw_may_10bp_ann_stress_only"].iloc[0])
    rf_val = sv("residual_vs_funding_10bp", "validation_2025H1")
    rf_recent = sv("residual_vs_funding_10bp", "recent_oos_2025H2_2026Apr")
    rf_may = clean_float(may.loc[may["candidate_id"] == cid, "residual_funding_may_ann_stress_only"].iloc[0])
    rc_recent = sv("residual_vs_core4_10bp", "recent_oos_2025H2_2026Apr")
    raw20_recent = sv("raw_20bp", "recent_oos_2025H2_2026Apr")
    lag_recent = sv("execution_lag_1bar_raw_10bp", "recent_oos_2025H2_2026Apr")
    beta_recent = beta[(beta["candidate_id"] == cid) & (beta["split"] == "recent_oos_2025H2_2026Apr")]
    funding_beta = clean_float(beta_recent["funding_beta"].iloc[0]) if not beta_recent.empty else None
    core4_beta = clean_float(beta_recent["core4_beta"].iloc[0]) if not beta_recent.empty else None
    checks = [
        ("raw_validation_nonpositive", raw_val is None or raw_val <= 0),
        ("raw_recent_nonpositive", raw_recent is None or raw_recent <= 0),
        ("raw_may_severely_negative", raw_may is None or raw_may < -0.5),
        ("residual_funding_validation_nonpositive", rf_val is None or rf_val <= 0),
        ("residual_funding_recent_nonpositive", rf_recent is None or rf_recent <= 0),
        ("residual_funding_may_negative", rf_may is None or rf_may < 0),
        ("residual_core4_recent_nonpositive", rc_recent is None or rc_recent <= 0),
        ("cost20_recent_collapse", raw20_recent is None or raw20_recent < -1.0),
        ("execution_lag_recent_collapse", lag_recent is None or lag_recent < -1.0),
        ("funding_beta_too_high", funding_beta is not None and abs(funding_beta) > 0.5),
        ("core4_beta_too_high", core4_beta is not None and abs(core4_beta) > 0.5),
    ]
    for reason, failed in checks:
        if failed:
            reasons.append(reason)
    if not reasons:
        return "A7I_RESEARCH_CANDIDATE", []
    if any(r in reasons for r in ["residual_funding_validation_nonpositive", "residual_funding_recent_nonpositive", "residual_core4_recent_nonpositive"]):
        return "HOLD_A7I1_RESIDUAL_ONLY_OR_BASELINE_EXPLAINED", reasons
    if any(r in reasons for r in ["cost20_recent_collapse", "execution_lag_recent_collapse"]):
        return "HOLD_A7I1_COST_OR_LAG_FAIL", reasons
    if "raw_may_severely_negative" in reasons or "residual_funding_may_negative" in reasons:
        return "HOLD_A7I1_MAY_STRESS_FAIL", reasons
    return "HOLD_A7I1_NO_RESEARCH_CANDIDATE", reasons


def main() -> int:
    A7I1B_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    candidates = all_candidates()
    all_fields = sorted({f for fields in FIELD_GROUPS.values() for f in fields})
    index, symbols, matrices, ctx = load_core4_context(extra_features=all_fields)

    summary, beta, residual_audit, lag_audit, may_audit = evaluate_candidates(index=index, matrices=matrices, ctx=ctx, candidates=candidates)
    rank_components = build_rank_components(summary)
    rank_components["arm"] = rank_components["candidate_id"].map(arm_label)
    candidate_meta = pd.DataFrame(
        [
            {
                "candidate_id": c.candidate_id,
                "arm": arm_label(c.candidate_id),
                "family": c.family,
                "object_type": c.object_type,
                "signal_mode": c.signal_mode,
                "expression": c.expression,
                "expr_hash": formula_hash(c.expression),
                "horizon": c.horizon,
                "source_fields": ";".join(extract_fields_from_expr(c.expression, set(all_fields))),
            }
            for c in candidates
        ]
    )
    scoreboard = rank_components.merge(candidate_meta, on=["candidate_id", "arm", "family", "object_type", "signal_mode"], how="left")
    scoreboard["selected_for_replay"] = False
    for arm in ["I0_basis_premium", "I1_flow_liquidity", "I2_microstructure_lite", "I3_placebo_random"]:
        idx = scoreboard[scoreboard["arm"] == arm].sort_values(["rank_score", "candidate_id"], ascending=[False, True]).head(REPLAY_PER_ARM).index
        scoreboard.loc[idx, "selected_for_replay"] = True
    selected = scoreboard[scoreboard["selected_for_replay"]].copy()

    wide_parts = []
    for series in summary["series"].unique():
        part = summary[summary["series"] == series].pivot_table(index="candidate_id", columns="split", values="annualized_mean", aggfunc="first")
        part.columns = [f"{series}__{c}__annualized_mean" for c in part.columns]
        wide_parts.append(part)
        dd = summary[summary["series"] == series].pivot_table(index="candidate_id", columns="split", values="compounded_max_dd", aggfunc="first")
        dd.columns = [f"{series}__{c}__compounded_max_dd" for c in dd.columns]
        wide_parts.append(dd)
    wide = pd.concat(wide_parts, axis=1).reset_index()
    selected_eval = selected.merge(wide, on="candidate_id", how="left")
    decisions = []
    for _, row in selected_eval.iterrows():
        decision, reasons = evaluate_research_candidate(row, beta, may_audit)
        decisions.append({"candidate_id": row["candidate_id"], "candidate_decision": decision, "reject_reasons": ";".join(reasons)})
    decision_df = pd.DataFrame(decisions)
    selected_eval = selected_eval.merge(decision_df, on="candidate_id", how="left")
    shortlist = selected_eval[selected_eval["candidate_decision"] == "A7I_RESEARCH_CANDIDATE"].copy()
    rejected = selected_eval[selected_eval["candidate_decision"] != "A7I_RESEARCH_CANDIDATE"].copy()

    placebo = selected_eval[selected_eval["arm"] == "I3_placebo_random"].copy()
    placebo_comparison = pd.DataFrame(
        [
            {
                "metric": "placebo_selected_count",
                "value": int(len(placebo)),
            },
            {
                "metric": "placebo_research_candidate_count",
                "value": int((placebo["candidate_decision"] == "A7I_RESEARCH_CANDIDATE").sum()),
            },
            {
                "metric": "non_placebo_research_candidate_count",
                "value": int((selected_eval["candidate_decision"] == "A7I_RESEARCH_CANDIDATE").sum()),
            },
        ]
    )
    duplicate = duplicate_cluster_audit(candidates, shortlist)
    symbol_month_loo = symbol_month_loo_placeholder(selected)

    summary_path = A7I1B_DIR / "a7i1_candidate_scoreboard.csv"
    shortlist_path = A7I1B_DIR / "a7i1_research_candidate_shortlist.csv"
    rejected_path = A7I1B_DIR / "a7i1_rejected_candidate_reasons.csv"
    placebo_path = A7I1B_DIR / "a7i1_placebo_comparison.csv"
    residual_path = A7I1B_DIR / "a7i1_residual_vs_fundingcore_core4.csv"
    beta_path = A7I1B_DIR / "a7i1_beta_corr_audit.csv"
    may_path = A7I1B_DIR / "a7i1_may_stress_only_audit.csv"
    lag_path = A7I1B_DIR / "a7i1_execution_lag_1bar_stress.csv"
    loo_path = A7I1B_DIR / "a7i1_symbol_month_loo.csv"
    duplicate_path = A7I1B_DIR / "a7i1_duplicate_cluster_audit.csv"
    summary.to_csv(A7I1B_DIR / "a7i1_full_metric_long.csv", index=False)
    scoreboard.to_csv(summary_path, index=False)
    shortlist.to_csv(shortlist_path, index=False)
    rejected.to_csv(rejected_path, index=False)
    placebo_comparison.to_csv(placebo_path, index=False)
    residual_audit.to_csv(residual_path, index=False)
    beta.to_csv(beta_path, index=False)
    may_audit.to_csv(may_path, index=False)
    lag_audit.to_csv(lag_path, index=False)
    symbol_month_loo.to_csv(loo_path, index=False)
    duplicate.to_csv(duplicate_path, index=False)

    non_placebo_research = shortlist[shortlist["arm"] != "I3_placebo_random"]
    placebo_research = shortlist[shortlist["arm"] == "I3_placebo_random"]
    families = set(non_placebo_research["family"].tolist())
    blockers = []
    if len(non_placebo_research) < 2:
        blockers.append("fewer_than_2_non_placebo_research_candidates")
    if not placebo_research.empty:
        blockers.append("placebo_arm_produced_research_candidate")
    if families and families <= {"flow_liquidity"}:
        blockers.append("all_research_candidates_flow_related")
    if not duplicate.empty and not bool(duplicate["cap_pass"].all()):
        blockers.append("duplicate_or_family_cap_failed")

    if "placebo_arm_produced_research_candidate" in blockers:
        decision = "HOLD_A7I1_PLACEBO_TOO_STRONG"
    elif "fewer_than_2_non_placebo_research_candidates" in blockers:
        decision = "HOLD_A7I1_NO_RESEARCH_CANDIDATE"
    elif "duplicate_or_family_cap_failed" in blockers:
        decision = "HOLD_A7I1_FAMILY_CONCENTRATION"
    else:
        decision = "PASS_A7I1_METHOD_SMOKE"

    manifest = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "stage": "A7I-1b small matched-budget residual-aware generator smoke",
        "executes_search": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "generated_per_arm": GENERATED_PER_ARM,
        "replay_selected_per_arm": REPLAY_PER_ARM,
        "may_boundary": {
            "may_status": "known_adversarial_stress_set",
            "may_used_for_ranking": False,
            "may_used_for_selection": False,
        },
        "research_candidate_count": int(len(non_placebo_research)),
        "placebo_research_candidate_count": int(len(placebo_research)),
        "outputs": {
            "candidate_scoreboard": str(summary_path),
            "research_candidate_shortlist": str(shortlist_path),
            "rejected_candidate_reasons": str(rejected_path),
            "placebo_comparison": str(placebo_path),
            "residual_vs_fundingcore_core4": str(residual_path),
            "beta_corr_audit": str(beta_path),
            "may_stress_only_audit": str(may_path),
            "execution_lag_1bar_stress": str(lag_path),
            "symbol_month_loo": str(loo_path),
            "duplicate_cluster_audit": str(duplicate_path),
        },
    }
    manifest_path = A7I1B_DIR / "a7i1_manifest_20260519.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / "CRYPTO_A7I1B_MATCHED_BUDGET_SMOKE_20260519.md"
    lines = [
        "# Crypto A7I-1b Matched-Budget Smoke",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        f"- executes_search: `True`",
        f"- generated_per_arm: `{GENERATED_PER_ARM}`",
        f"- replay_selected_per_arm: `{REPLAY_PER_ARM}`",
        f"- authorizes_alpha_proof: `False`",
        f"- blockers: `{blockers}`",
        "",
        "## Arm Summary",
        "",
        "| arm | generated | selected | research candidates |",
        "|---|---:|---:|---:|",
    ]
    for arm in ["I0_basis_premium", "I1_flow_liquidity", "I2_microstructure_lite", "I3_placebo_random"]:
        lines.append(
            f"| `{arm}` | {int((scoreboard['arm'] == arm).sum())} | {int((selected_eval['arm'] == arm).sum())} | "
            f"{int(((selected_eval['arm'] == arm) & (selected_eval['candidate_decision'] == 'A7I_RESEARCH_CANDIDATE')).sum())} |"
        )
    lines += [
        "",
        "## Research Candidate Shortlist",
        "",
        "| candidate | arm | family | rank score | expression |",
        "|---|---|---|---:|---|",
    ]
    if shortlist.empty:
        lines.append("| n/a | n/a | n/a |  | n/a |")
    else:
        for _, row in shortlist.head(20).iterrows():
            lines.append(
                f"| `{row['candidate_id']}` | `{row['arm']}` | `{row['family']}` | {float(row['rank_score']):.6f} | `{row['expression']}` |"
            )
    lines += [
        "",
        "## Decision Boundary",
        "",
        "- PASS_A7I1_METHOD_SMOKE would only produce A7I_RESEARCH_CANDIDATE objects.",
        "- This report never authorizes alpha proof, shadow, paper, or live.",
        "- `symbol_month_loo` is an explicit placeholder in this smoke and must be run before alpha proof.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / "CRYPTO_A7I1B_DECISION_RECORD_20260519.md"
    decision_lines = [
        "# Crypto A7I-1b Decision Record",
        "",
        f"decision: {decision}",
        "stage: small matched-budget residual-aware generator smoke",
        "authorizes_alpha_proof: false",
        "authorizes_shadow_paper_live: false",
        f"generated_per_arm: {GENERATED_PER_ARM}",
        f"replay_selected_per_arm: {REPLAY_PER_ARM}",
        f"research_candidate_count: {int(len(non_placebo_research))}",
        f"placebo_research_candidate_count: {int(len(placebo_research))}",
        "",
        "not_confirmed:",
        "- alpha proof",
        "- true shadow readiness",
        "- paper/live readiness",
        "- symbol/month LOO promotion gate",
    ]
    decision_path.write_text("\n".join(decision_lines) + "\n", encoding="utf-8")

    print("A7I1B_REPORT=" + str(report_path))
    print("A7I1B_DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
