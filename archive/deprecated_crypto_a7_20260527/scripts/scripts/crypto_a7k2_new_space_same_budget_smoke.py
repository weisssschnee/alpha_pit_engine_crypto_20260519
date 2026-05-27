from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7_validation_utils import COST_BPS, REPORT_DIR, RUNTIME_DIR, clean_float, load_core4_context, split_mask
from crypto_a7b_funding_baseline_audit import residualize, scale_book
from crypto_a7c_fundingcore_narrow_audit import fundingcore_specs
from crypto_a7h1_nonfunding_masked_loo_audit import raw_book_from_specs_masked
from crypto_a7i1a_runner_preflight import RunnerCandidate, book_from_spec, metric_by_split
from crypto_a7_validation_utils import load_core4_specs


A7K1B_DIR = RUNTIME_DIR / "a7k1b_new_space_generator_impl_preflight"
A7K2_DIR = RUNTIME_DIR / "a7k2_new_space_same_budget_smoke"
DATE_TAG = "20260520"
PRIMARY_COST_BPS = COST_BPS["stress_10bp"]
SEVERE_COST_BPS = COST_BPS["severe_20bp"]
SELECTED_PER_ARM = 64
ARMS = [
    "K0_basis_premium_clean",
    "K1_flow_liquidity_clean",
    "K2_microstructure_lite_latency_robust",
    "K3_placebo_random_control",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def safe(value: Any, default: float = 0.0) -> float:
    out = clean_float(value)
    return default if out is None else out


def clip(value: Any, cap: float = 2.0) -> float:
    return float(np.clip(safe(value), -cap, cap))


def linear_beta(y: pd.Series, x: pd.Series, mask: np.ndarray) -> tuple[float | None, float | None]:
    yy = y.to_numpy(dtype=float)[mask]
    xx = x.to_numpy(dtype=float)[mask]
    valid = np.isfinite(yy) & np.isfinite(xx)
    if valid.sum() < 50 or np.nanvar(xx[valid]) <= 0:
        return None, None
    beta, _ = np.polyfit(xx[valid], yy[valid], 1)
    corr = np.corrcoef(xx[valid], yy[valid])[0, 1]
    return clean_float(beta), clean_float(corr)


def candidates_from_manifest(path: Path) -> tuple[list[RunnerCandidate], pd.DataFrame]:
    manifest = pd.read_csv(path)
    candidates = []
    for _, row in manifest.iterrows():
        candidates.append(
            RunnerCandidate(
                candidate_id=row["candidate_id"],
                expression=row["expression"],
                horizon=int(row["horizon"]),
                family=row["family"],
                object_type=row["object_type"],
                signal_mode=row.get("signal_mode", "original"),
                classification_expected="A7K2_SMOKE_CANDIDATE",
            )
        )
    return candidates, manifest


def evaluate_candidates(
    *,
    index: pd.DatetimeIndex,
    matrices: dict[str, np.ndarray],
    ctx,
    candidates: list[RunnerCandidate],
    meta: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    funding_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=fundingcore_specs())
    core4_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=load_core4_specs())
    funding_scaled = scale_book(funding_raw, PRIMARY_COST_BPS)
    core4_scaled = scale_book(core4_raw, PRIMARY_COST_BPS)

    meta_by_id = meta.set_index("candidate_id").to_dict(orient="index")
    summary_parts = []
    beta_rows = []
    for i, candidate in enumerate(candidates, start=1):
        m = meta_by_id[candidate.candidate_id]
        raw, _ = book_from_spec(index=index, matrices=matrices, ctx=ctx, candidate=candidate)
        raw10 = scale_book(raw, PRIMARY_COST_BPS)
        raw20 = scale_book(raw, SEVERE_COST_BPS)
        lag_raw, _ = book_from_spec(index=index, matrices=matrices, ctx=ctx, candidate=candidate, signal_lag_bars=1)
        lag10 = scale_book(lag_raw, PRIMARY_COST_BPS)
        residual_funding = residualize(raw10, funding_scaled)
        residual_core4 = residualize(raw10, core4_scaled)

        base = {
            "candidate_id": candidate.candidate_id,
            "arm": m["arm"],
            "family": candidate.family,
            "object_type": candidate.object_type,
            "signal_mode": candidate.signal_mode,
            "expression": candidate.expression,
            "expr_hash": m["expr_hash"],
            "horizon": candidate.horizon,
            "source_fields": m.get("source_fields", ""),
            "source_field_families": m.get("source_field_families", ""),
        }
        for series, frame in [
            ("raw_10bp", raw10),
            ("raw_20bp", raw20),
            ("residual_vs_funding_10bp", residual_funding),
            ("residual_vs_core4_10bp", residual_core4),
            ("execution_lag_1bar_raw_10bp", lag10),
        ]:
            summary_parts.append(metric_by_split(frame, "net_return", {**base, "series": series}))

        ts = pd.DatetimeIndex(pd.to_datetime(raw10["timestamp"], utc=True))
        for split in ["validation_2025H1", "recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]:
            mask = split_mask(ts, split)
            fb, fcorr = linear_beta(raw10["net_return"], funding_scaled["net_return"], mask)
            cb, ccorr = linear_beta(raw10["net_return"], core4_scaled["net_return"], mask)
            beta_rows.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "arm": m["arm"],
                    "split": split,
                    "funding_beta": fb,
                    "funding_corr": fcorr,
                    "core4_beta": cb,
                    "core4_corr": ccorr,
                }
            )
        if i % 100 == 0:
            print(f"evaluated {i}/{len(candidates)}")
    return pd.concat(summary_parts, ignore_index=True), pd.DataFrame(beta_rows)


def pivot_metrics(long_df: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for value_col in ["n", "annualized_mean", "compounded_max_dd", "mean_turnover", "mean_gross_exposure"]:
        p = long_df.pivot_table(index="candidate_id", columns=["series", "split"], values=value_col, aggfunc="first")
        p.columns = [f"{series}__{split}__{value_col}" for series, split in p.columns]
        parts.append(p)
    return pd.concat(parts, axis=1).reset_index()


def add_rank_score(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["component_raw_validation"] = out["raw_10bp__validation_2025H1__annualized_mean"].map(clip)
    out["component_raw_recent"] = out["raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean"].map(clip)
    out["component_residual_funding_validation"] = out[
        "residual_vs_funding_10bp__validation_2025H1__annualized_mean"
    ].map(clip)
    out["component_residual_funding_recent"] = out[
        "residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean"
    ].map(clip)
    out["component_residual_core4_recent"] = out[
        "residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean"
    ].map(clip)
    out["component_cost20_validation"] = out["raw_20bp__validation_2025H1__annualized_mean"].map(clip)
    out["component_cost20_recent"] = out["raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean"].map(clip)
    out["component_lag1_validation"] = out[
        "execution_lag_1bar_raw_10bp__validation_2025H1__annualized_mean"
    ].map(clip)
    out["component_lag1_recent"] = out[
        "execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean"
    ].map(clip)
    out["component_drawdown_penalty"] = out[
        "raw_10bp__recent_oos_2025H2_2026Apr__compounded_max_dd"
    ].fillna(0.0).clip(lower=-2.0, upper=0.0)
    out["component_turnover_penalty"] = -out[
        "raw_10bp__recent_oos_2025H2_2026Apr__mean_turnover"
    ].fillna(0.0).clip(lower=0.0, upper=2.0)
    out["component_funding_beta_penalty"] = -out["funding_beta_recent"].fillna(0.0).abs().clip(upper=1.0)
    out["component_core4_beta_penalty"] = -out["core4_beta_recent"].fillna(0.0).abs().clip(upper=1.0)
    out["a7k_rank_score"] = (
        0.7 * out["component_raw_validation"]
        + 0.9 * out["component_raw_recent"]
        + 0.9 * out["component_residual_funding_validation"]
        + 1.1 * out["component_residual_funding_recent"]
        + 0.8 * out["component_residual_core4_recent"]
        + 0.8 * out["component_cost20_validation"]
        + 1.2 * out["component_cost20_recent"]
        + 0.8 * out["component_lag1_validation"]
        + 1.2 * out["component_lag1_recent"]
        + 0.7 * out["component_drawdown_penalty"]
        + 0.5 * out["component_turnover_penalty"]
        + 0.7 * out["component_funding_beta_penalty"]
        + 0.7 * out["component_core4_beta_penalty"]
    )
    return out


def preselection_reasons(row: pd.Series) -> list[str]:
    checks = [
        ("raw_10bp__validation_2025H1__n", 250, ">=", "raw_validation_insufficient_n"),
        ("raw_10bp__recent_oos_2025H2_2026Apr__n", 250, ">=", "raw_recent_insufficient_n"),
        ("raw_10bp__validation_2025H1__mean_gross_exposure", 0.10, ">=", "raw_validation_insufficient_gross_exposure"),
        ("raw_10bp__recent_oos_2025H2_2026Apr__mean_gross_exposure", 0.10, ">=", "raw_recent_insufficient_gross_exposure"),
        ("raw_10bp__validation_2025H1__annualized_mean", 0.0, ">", "raw_validation_nonpositive"),
        ("raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean", 0.0, ">", "raw_recent_nonpositive"),
        ("raw_20bp__validation_2025H1__annualized_mean", 0.0, ">=", "cost20_validation_negative"),
        ("raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean", 0.0, ">=", "cost20_recent_negative"),
        (
            "execution_lag_1bar_raw_10bp__validation_2025H1__annualized_mean",
            0.0,
            ">=",
            "lag1_validation_negative",
        ),
        (
            "execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
            0.0,
            ">=",
            "lag1_recent_negative",
        ),
        (
            "residual_vs_funding_10bp__validation_2025H1__annualized_mean",
            0.0,
            ">",
            "residual_funding_validation_nonpositive",
        ),
        (
            "residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
            0.0,
            ">",
            "residual_funding_recent_nonpositive",
        ),
        (
            "residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
            0.0,
            ">",
            "residual_core4_recent_nonpositive",
        ),
    ]
    reasons = []
    for col, threshold, op, reason in checks:
        value = safe(row.get(col), default=np.nan)
        if not np.isfinite(value):
            reasons.append(reason)
        elif op == ">=" and value < threshold:
            reasons.append(reason)
        elif op == ">" and value <= threshold:
            reasons.append(reason)
    if abs(safe(row.get("funding_beta_recent"), 99.0)) >= 0.50:
        reasons.append("funding_beta_too_high")
    if abs(safe(row.get("core4_beta_recent"), 99.0)) >= 0.50:
        reasons.append("core4_beta_too_high")
    if row["object_type"] == "placebo":
        reasons.append("placebo_arm")
    return reasons


def final_candidate_decision(row: pd.Series) -> tuple[str, list[str]]:
    reasons = preselection_reasons(row)
    raw_may = safe(row.get("raw_10bp__fresh_forward_2026May__annualized_mean"), default=-999.0)
    residual_may = safe(row.get("residual_vs_funding_10bp__fresh_forward_2026May__annualized_mean"), default=-999.0)
    if raw_may < -0.5:
        reasons.append("may_stress_severe_fail")
    elif raw_may < -0.25:
        reasons.append("may_stress_material_fail")
    if residual_may < 0:
        reasons.append("may_residual_funding_negative")
    if not reasons:
        return "A7K_RESEARCH_CANDIDATE", []
    if any(r in reasons for r in ["cost20_recent_negative", "lag1_recent_negative", "may_stress_severe_fail", "may_stress_material_fail"]):
        return "A7K_CLUE_ONLY", reasons
    if row["object_type"] == "placebo":
        return "NEGATIVE_CONTROL", reasons
    return "REJECT_A7K_GATE_FAIL", reasons


def duplicate_family_audit(shortlist: pd.DataFrame) -> pd.DataFrame:
    if shortlist.empty:
        return pd.DataFrame([{"bucket_type": "none", "bucket": "none", "count": 0, "share": 0.0, "cap": 0.25, "cap_pass": True}])
    total = len(shortlist)
    rows = []
    for family, count in Counter(shortlist["family"]).items():
        share = count / total
        rows.append({"bucket_type": "family", "bucket": family, "count": count, "share": share, "cap": 0.25, "cap_pass": share <= 0.25})
    for expr_hash, count in Counter(shortlist["expr_hash"]).items():
        if count > 1:
            rows.append({"bucket_type": "expr_hash", "bucket": expr_hash, "count": count, "share": count / total, "cap": 1 / total, "cap_pass": False})
    return pd.DataFrame(rows)


def main() -> int:
    A7K2_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    preflight = json.loads((A7K1B_DIR / f"crypto_a7k1b_manifest_{DATE_TAG}.json").read_text(encoding="utf-8"))
    if not preflight.get("authorizes_a7k2_same_budget_smoke"):
        raise RuntimeError("A7K-1B did not authorize A7K-2")

    candidates, meta = candidates_from_manifest(A7K1B_DIR / "a7k1b_candidate_manifest.csv")
    extra_fields = sorted({f for text in meta["source_fields"].dropna() for f in str(text).split(";") if f})
    index, symbols, matrices, ctx = load_core4_context(extra_features=extra_fields)
    long_metrics, beta = evaluate_candidates(index=index, matrices=matrices, ctx=ctx, candidates=candidates, meta=meta)
    wide = pivot_metrics(long_metrics)
    beta_recent = beta[beta["split"] == "recent_oos_2025H2_2026Apr"][
        ["candidate_id", "funding_beta", "funding_corr", "core4_beta", "core4_corr"]
    ].rename(
        columns={
            "funding_beta": "funding_beta_recent",
            "funding_corr": "funding_corr_recent",
            "core4_beta": "core4_beta_recent",
            "core4_corr": "core4_corr_recent",
        }
    )
    scored = meta.merge(wide, on="candidate_id", how="left").merge(beta_recent, on="candidate_id", how="left")
    scored = add_rank_score(scored)
    scored["preselection_reasons"] = scored.apply(lambda r: ";".join(preselection_reasons(r)), axis=1)
    scored["a7k_preselection_pass"] = scored["preselection_reasons"].eq("")
    scored["selected_for_replay"] = False
    arm_shortfalls = {}
    for arm in ARMS:
        part = scored[(scored["arm"] == arm) & (scored["a7k_preselection_pass"])]
        idx = part.sort_values(["a7k_rank_score", "candidate_id"], ascending=[False, True]).head(SELECTED_PER_ARM).index
        scored.loc[idx, "selected_for_replay"] = True
        arm_shortfalls[arm] = max(0, SELECTED_PER_ARM - len(idx))
    selected = scored[scored["selected_for_replay"]].copy()

    decisions = []
    for _, row in selected.iterrows():
        decision, reasons = final_candidate_decision(row)
        decisions.append({"candidate_id": row["candidate_id"], "candidate_decision": decision, "reject_reasons": ";".join(reasons)})
    decision_df = pd.DataFrame(decisions)
    selected_eval = selected.merge(decision_df, on="candidate_id", how="left")
    shortlist = selected_eval[selected_eval["candidate_decision"] == "A7K_RESEARCH_CANDIDATE"].copy()
    rejected = selected_eval[selected_eval["candidate_decision"] != "A7K_RESEARCH_CANDIDATE"].copy()
    duplicate = duplicate_family_audit(shortlist)

    long_path = A7K2_DIR / "a7k2_full_metric_long.csv"
    beta_path = A7K2_DIR / "a7k2_beta_corr_audit.csv"
    score_path = A7K2_DIR / "a7k2_candidate_scoreboard.csv"
    selected_path = A7K2_DIR / "a7k2_selected_candidates.csv"
    shortlist_path = A7K2_DIR / "a7k2_research_candidate_shortlist.csv"
    rejected_path = A7K2_DIR / "a7k2_rejected_candidate_reasons.csv"
    duplicate_path = A7K2_DIR / "a7k2_duplicate_family_audit.csv"
    may_path = A7K2_DIR / "a7k2_may_stress_label_audit.csv"
    long_metrics.to_csv(long_path, index=False)
    beta.to_csv(beta_path, index=False)
    scored.to_csv(score_path, index=False)
    selected_eval.to_csv(selected_path, index=False)
    shortlist.to_csv(shortlist_path, index=False)
    rejected.to_csv(rejected_path, index=False)
    duplicate.to_csv(duplicate_path, index=False)
    selected_eval[
        [
            "candidate_id",
            "arm",
            "candidate_decision",
            "raw_10bp__fresh_forward_2026May__annualized_mean",
            "residual_vs_funding_10bp__fresh_forward_2026May__annualized_mean",
            "reject_reasons",
        ]
    ].assign(may_used_for_ranking=False, may_used_for_selection=False).to_csv(may_path, index=False)

    arm_summary = (
        scored.groupby("arm", as_index=False)
        .agg(
            generated_count=("candidate_id", "size"),
            preselection_pass_count=("a7k_preselection_pass", "sum"),
        )
        .merge(
            selected_eval.groupby("arm", as_index=False).agg(
                selected_count=("candidate_id", "size"),
                research_candidate_count=("candidate_decision", lambda x: int((x == "A7K_RESEARCH_CANDIDATE").sum())),
                clue_only_count=("candidate_decision", lambda x: int((x == "A7K_CLUE_ONLY").sum())),
            ),
            on="arm",
            how="left",
        )
        .fillna(0)
    )
    arm_summary["selection_shortfall"] = arm_summary["arm"].map(arm_shortfalls)
    arm_summary_path = A7K2_DIR / "a7k2_arm_summary.csv"
    arm_summary.to_csv(arm_summary_path, index=False)

    non_placebo = shortlist[shortlist["object_type"] != "placebo"]
    placebo = shortlist[shortlist["object_type"] == "placebo"]
    non_flow = non_placebo[~non_placebo["family"].str.contains("flow", case=False, na=False)]
    blockers = []
    if len(non_placebo) < 2:
        blockers.append("fewer_than_2_non_placebo_research_candidates")
    if len(placebo) > 0:
        blockers.append("placebo_research_candidate_nonzero")
    if len(non_flow) < 1:
        blockers.append("no_non_flow_non_taker_research_candidate")
    if not bool(duplicate["cap_pass"].all()):
        blockers.append("duplicate_or_family_cap_failed")
    if any(v > 0 for v in arm_shortfalls.values()):
        blockers.append("arm_preselection_shortfall")

    if "placebo_research_candidate_nonzero" in blockers:
        decision = "HOLD_A7K2_PLACEBO_TOO_STRONG"
    elif "fewer_than_2_non_placebo_research_candidates" in blockers:
        decision = "HOLD_A7K2_INSUFFICIENT_RESEARCH_CANDIDATES"
    elif blockers:
        decision = "HOLD_A7K2_METHOD_SMOKE_BLOCKED"
    else:
        decision = "PASS_A7K2_METHOD_SMOKE"

    manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_search": True,
        "executes_replay": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "candidate_pool_source": "A7K-1B new-space generator manifest",
        "generated_count": int(len(scored)),
        "selected_count": int(len(selected_eval)),
        "research_candidate_count": int(len(non_placebo)),
        "placebo_research_candidate_count": int(len(placebo)),
        "non_flow_research_candidate_count": int(len(non_flow)),
        "blockers": blockers,
        "arm_shortfalls": arm_shortfalls,
        "may_boundary": {"may_used_for_ranking": False, "may_used_for_selection": False, "may_stress_only": True},
        "outputs": {
            "full_metric_long": str(long_path),
            "beta_corr_audit": str(beta_path),
            "candidate_scoreboard": str(score_path),
            "selected_candidates": str(selected_path),
            "research_candidate_shortlist": str(shortlist_path),
            "rejected_candidate_reasons": str(rejected_path),
            "duplicate_family_audit": str(duplicate_path),
            "may_stress_label_audit": str(may_path),
            "arm_summary": str(arm_summary_path),
        },
    }
    manifest_path = A7K2_DIR / f"crypto_a7k2_manifest_{DATE_TAG}.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / f"CRYPTO_A7K2_NEW_SPACE_SAME_BUDGET_SMOKE_{DATE_TAG}.md"
    lines = [
        "# Crypto A7K-2 New-Space Same-Budget Smoke",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- evidence_level: `method_smoke_not_alpha_proof`",
        "- candidate_pool_source: `A7K-1B new-space generator manifest`",
        "- generated_count: `1000`",
        f"- selected_count: `{len(selected_eval)}`",
        "- may_used_for_ranking: `False`",
        "- may_used_for_selection: `False`",
        "- authorizes_alpha_proof: `False`",
        f"- blockers: `{blockers}`",
        "",
        "## Arm Summary",
        "",
        "| arm | generated | preselection pass | selected | research | clue_only | shortfall |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in arm_summary.iterrows():
        lines.append(
            f"| `{row['arm']}` | {int(row['generated_count'])} | {int(row['preselection_pass_count'])} | "
            f"{int(row['selected_count'])} | {int(row['research_candidate_count'])} | "
            f"{int(row['clue_only_count'])} | {int(row['selection_shortfall'])} |"
        )
    lines += ["", "## Research Candidate Shortlist", ""]
    if shortlist.empty:
        lines.append("- none")
    else:
        lines += ["| candidate | arm | family | expression | raw recent | cost20 recent | lag1 recent | May raw |", "|---|---|---|---|---:|---:|---:|---:|"]
        for _, row in shortlist.iterrows():
            lines.append(
                f"| `{row['candidate_id']}` | `{row['arm']}` | `{row['family']}` | `{row['expression']}` | "
                f"{safe(row['raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean']):.4f} | "
                f"{safe(row['raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean']):.4f} | "
                f"{safe(row['execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean']):.4f} | "
                f"{safe(row['raw_10bp__fresh_forward_2026May__annualized_mean']):.4f} |"
            )
    lines += [
        "",
        "## Boundary",
        "",
        "- A7K-2 is a method smoke only.",
        "- May is a stress/veto label only, not a ranking or generator input.",
        "- PASS would not authorize alpha proof, shadow, paper, live, or production.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7K2_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7K-2 Decision Record",
                "",
                f"- decision: `{decision}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                f"- research_candidate_count: `{int(len(non_placebo))}`",
                f"- placebo_research_candidate_count: `{int(len(placebo))}`",
                f"- blockers: `{blockers}`",
                "",
                "A7K-2 evaluates the A7K-1B new-space candidate manifest under the same 1000/256 budget. It does not authorize alpha proof or trading.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print("A7K2_REPORT=" + str(report_path))
    print("A7K2_DECISION_RECORD=" + str(decision_path))
    print("A7K2_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
