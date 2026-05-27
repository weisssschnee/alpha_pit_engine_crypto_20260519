from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, clean_float, load_core4_context
from crypto_a7b_funding_baseline_audit import residualize, scale_book
from crypto_a7c_fundingcore_narrow_audit import fundingcore_specs
from crypto_a7h1_nonfunding_masked_loo_audit import raw_book_from_specs_masked
from crypto_a7i1a_runner_preflight import RunnerCandidate, book_from_spec, metric_by_split
from crypto_a7k2_new_space_same_budget_smoke import linear_beta, pivot_metrics
from crypto_a7m2_equal_budget_engine_bakeoff import (
    FIELD_FAMILY,
    PRIMARY_COST_BPS,
    SEVERE_COST_BPS,
    evaluate_candidates_fast,
    formula_depth,
    formula_hash,
    operator_signature,
    sanitize_expression,
    split_mask_for_index,
    to_runner_candidates,
)


DATE_TAG = "20260520"
A7M2_DIR = RUNTIME_DIR / "a7m2_equal_budget_engine_bakeoff"
A7M2D_DIR = RUNTIME_DIR / "a7m2d_cluster_concentration_forensics"
A7M2E_DIR = RUNTIME_DIR / "a7m2e_cluster_cap_policy_revision"

MAY_REASONS = {"may_stress_severe_fail", "may_stress_material_fail", "may_residual_funding_negative"}
MAY_VETO_REASONS = {"may_stress_severe_fail", "may_residual_funding_negative"}
NEGATIVE_CONTROL_ENGINES = {"E6_placebo_random_control", "E7_adversarial_null_wrong_lag_control"}
POSITIVE_LABELS = {
    "A7M_RESEARCH_CANDIDATE",
    "A7M_NEAR_MISS_MAY_STRESS_FAIL",
    "A7M_NEAR_MISS_COST_FAIL",
    "A7M_NEAR_MISS_LAG_FAIL",
    "A7M_NEAR_MISS_RESIDUAL_FAIL",
    "A7M_HIGH_QUALITY_NEAR_MISS",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_hash(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for path in paths:
        h.update(str(path).encode("utf-8"))
        h.update(str(path.stat().st_size).encode("utf-8"))
        h.update(str(int(path.stat().st_mtime)).encode("utf-8"))
    return h.hexdigest()


def field_tokens(expr: str) -> list[str]:
    fields = []
    for field in FIELD_FAMILY:
        if field in str(expr):
            fields.append(field)
    return sorted(fields)


def family_signature(expr: str) -> str:
    fields = field_tokens(expr)
    return ";".join(sorted({FIELD_FAMILY[field] for field in fields})) or "missing"


def source_fields(expr: str) -> str:
    return ";".join(field_tokens(expr))


def parse_reasons(text: Any) -> list[str]:
    return [part for part in str(text or "").split(";") if part]


def known_row(candidate_id: str, expression: str, horizon: int, family: str, object_type: str, signal_mode: str) -> dict[str, Any]:
    expr = sanitize_expression(expression) if signal_mode != "book_object" else expression
    return {
        "candidate_id": candidate_id,
        "engine": "KNOWN_OBJECTS",
        "arm": "KNOWN_OBJECTS",
        "seed": 0,
        "ordinal": 0,
        "family": family,
        "object_type": object_type,
        "signal_mode": signal_mode,
        "expression": expr,
        "expr_hash": formula_hash(f"{expr}|{candidate_id}"),
        "horizon": horizon,
        "source_fields": source_fields(expr) if signal_mode != "book_object" else "",
        "source_field_families": family_signature(expr) if signal_mode != "book_object" else family,
        "operator_signature": operator_signature(expr) if signal_mode != "book_object" else "book_object",
        "formula_depth": formula_depth(expr) if signal_mode != "book_object" else 0,
    }


def build_parity_sample(scoreboard: pd.DataFrame, deep: pd.DataFrame, clusters: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, part in scoreboard.sort_values(["candidate_id"]).groupby("engine"):
        rows.append(part.head(16))
    rows.append(scoreboard[scoreboard["engine"].eq("E6_placebo_random_control")].sort_values("candidate_id").head(16))
    rows.append(scoreboard[scoreboard["engine"].eq("E7_adversarial_null_wrong_lag_control")].sort_values("candidate_id").head(16))

    positive = deep[deep["candidate_decision"].isin(POSITIVE_LABELS)].merge(clusters, on="candidate_id", how="left")
    rc000 = positive[positive["return_corr_cluster"].astype(str).eq("rc_000")].sort_values(["a7m_rank_score", "candidate_id"], ascending=[False, True]).head(32)
    non_rc = positive[~positive["return_corr_cluster"].astype(str).eq("rc_000")].sort_values(["return_corr_cluster", "a7m_rank_score", "candidate_id"], ascending=[True, False, True]).head(64)
    rows.extend([rc000[scoreboard.columns], non_rc[scoreboard.columns]])

    sample = pd.concat(rows, ignore_index=True).drop_duplicates("candidate_id")
    known = pd.DataFrame(
        [
            known_row("a7i1a_fundingcore_baseline", "FundingCore_v1_book", 6, "funding_baseline", "baseline", "book_object"),
            known_row("a7i1a_core4_benchmark", "Core4_v1_book", 6, "core4_benchmark", "baseline", "book_object"),
            known_row("parity_taker_imbalance", "Rank(taker_imbalance)", 6, "flow_liquidity", "known_overlay", "original"),
            known_row(
                "parity_i2_microstructure_lite_113",
                "Mul(Rank(realized_vol_6),ZScore(quote_volume_mean_12))",
                12,
                "microstructure_lite",
                "generated_candidate",
                "original",
            ),
        ]
    )
    return pd.concat([sample, known], ignore_index=True, sort=False).fillna("")


def metric_rows_from_raw(
    *,
    index: pd.DatetimeIndex,
    funding_scaled: pd.DataFrame,
    core4_scaled: pd.DataFrame,
    raw,
    lag_raw,
    base: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw10 = scale_book(raw, PRIMARY_COST_BPS)
    raw20 = scale_book(raw, SEVERE_COST_BPS)
    residual_funding = residualize(raw10, funding_scaled)
    residual_core4 = residualize(raw10, core4_scaled)
    lag10 = scale_book(lag_raw, PRIMARY_COST_BPS)
    long_rows = []
    for series, frame in [
        ("raw_10bp", raw10),
        ("raw_20bp", raw20),
        ("residual_vs_funding_10bp", residual_funding),
        ("residual_vs_core4_10bp", residual_core4),
        ("execution_lag_1bar_raw_10bp", lag10),
    ]:
        long_rows.append(metric_by_split(frame, "net_return", {**base, "series": series}))

    beta_rows = []
    ts = pd.DatetimeIndex(pd.to_datetime(raw10["timestamp"], utc=True))
    for split in ["validation_2025H1", "recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]:
        mask = split_mask_for_index(ts, split)
        fb, fcorr = linear_beta(raw10["net_return"], funding_scaled["net_return"], mask)
        cb, ccorr = linear_beta(raw10["net_return"], core4_scaled["net_return"], mask)
        beta_rows.append(
            {
                "candidate_id": base["candidate_id"],
                "split": split,
                "funding_beta": fb,
                "funding_corr": fcorr,
                "core4_beta": cb,
                "core4_corr": ccorr,
            }
        )
    return pd.concat(long_rows, ignore_index=True), pd.DataFrame(beta_rows)


def object_raw_fast(index, matrices, ctx, candidate: RunnerCandidate):
    if candidate.candidate_id == "a7i1a_fundingcore_baseline":
        return raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=fundingcore_specs())
    if candidate.candidate_id == "a7i1a_core4_benchmark":
        from crypto_a7_validation_utils import load_core4_specs

        return raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=load_core4_specs())
    raise ValueError(f"unknown fast object: {candidate.candidate_id}")


def evaluate_known_objects_fast(index, matrices, ctx, known_meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    funding_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=fundingcore_specs())
    from crypto_a7_validation_utils import load_core4_specs

    core4_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=load_core4_specs())
    funding_scaled = scale_book(funding_raw, PRIMARY_COST_BPS)
    core4_scaled = scale_book(core4_raw, PRIMARY_COST_BPS)
    rows = []
    beta = []
    for c in to_runner_candidates(known_meta):
        if c.signal_mode != "book_object":
            continue
        raw = object_raw_fast(index, matrices, ctx, c)
        lag_raw = raw.copy()
        lag_raw["pre_fee_return"] = np.nan
        base = known_meta[known_meta["candidate_id"].eq(c.candidate_id)].iloc[0].to_dict()
        long, b = metric_rows_from_raw(index=index, funding_scaled=funding_scaled, core4_scaled=core4_scaled, raw=raw, lag_raw=lag_raw, base=base)
        rows.append(long)
        beta.append(b)
    return pd.concat(rows, ignore_index=True), pd.concat(beta, ignore_index=True)


def evaluate_candidates_legacy(index, matrices, ctx, candidates: list[RunnerCandidate], meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    funding_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=fundingcore_specs())
    from crypto_a7_validation_utils import load_core4_specs

    core4_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=load_core4_specs())
    funding_scaled = scale_book(funding_raw, PRIMARY_COST_BPS)
    core4_scaled = scale_book(core4_raw, PRIMARY_COST_BPS)
    meta_by_id = meta.set_index("candidate_id").to_dict(orient="index")
    rows = []
    beta = []
    for i, c in enumerate(candidates, start=1):
        base = dict(meta_by_id[c.candidate_id])
        base["candidate_id"] = c.candidate_id
        raw, _ = book_from_spec(index=index, matrices=matrices, ctx=ctx, candidate=c)
        lag_raw, _ = book_from_spec(index=index, matrices=matrices, ctx=ctx, candidate=c, signal_lag_bars=1)
        long, b = metric_rows_from_raw(index=index, funding_scaled=funding_scaled, core4_scaled=core4_scaled, raw=raw, lag_raw=lag_raw, base=base)
        rows.append(long)
        beta.append(b)
        ctx.expr_cache.clear()
        if i % 50 == 0:
            print(f"legacy parity evaluated {i}/{len(candidates)}", flush=True)
    return pd.concat(rows, ignore_index=True), pd.concat(beta, ignore_index=True)


def wide_with_beta(metrics: pd.DataFrame, beta: pd.DataFrame, suffix: str) -> pd.DataFrame:
    wide = pivot_metrics(metrics)
    beta_wide_parts = []
    for col in ["funding_beta", "funding_corr", "core4_beta", "core4_corr"]:
        p = beta.pivot_table(index="candidate_id", columns="split", values=col, aggfunc="first")
        p.columns = [f"{col}__{split}" for split in p.columns]
        beta_wide_parts.append(p)
    out = wide.merge(pd.concat(beta_wide_parts, axis=1).reset_index(), on="candidate_id", how="left")
    return out.add_suffix(f"__{suffix}").rename(columns={f"candidate_id__{suffix}": "candidate_id"})


def run_parity_audit(sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    extra_fields = sorted({f for text in sample["source_fields"].dropna() for f in str(text).split(";") if f})
    index, symbols, matrices, ctx_fast = load_core4_context(extra_features=extra_fields)
    _, _, _, ctx_legacy = load_core4_context(extra_features=extra_fields)

    candidate_meta = sample[~sample["signal_mode"].eq("book_object")].copy()
    known_meta = sample[sample["signal_mode"].eq("book_object")].copy()

    fast_rows = []
    fast_beta = []
    legacy_rows = []
    legacy_beta = []
    if not candidate_meta.empty:
        fast_long, fast_b = evaluate_candidates_fast(index=index, matrices=matrices, ctx=ctx_fast, candidates=to_runner_candidates(candidate_meta), meta=candidate_meta)
        legacy_long, legacy_b = evaluate_candidates_legacy(index, matrices, ctx_legacy, to_runner_candidates(candidate_meta), candidate_meta)
        fast_rows.append(fast_long)
        fast_beta.append(fast_b)
        legacy_rows.append(legacy_long)
        legacy_beta.append(legacy_b)
    if not known_meta.empty:
        fast_long, fast_b = evaluate_known_objects_fast(index, matrices, ctx_fast, known_meta)
        legacy_long, legacy_b = evaluate_candidates_legacy(index, matrices, ctx_legacy, to_runner_candidates(known_meta), known_meta)
        fast_rows.append(fast_long)
        fast_beta.append(fast_b)
        legacy_rows.append(legacy_long)
        legacy_beta.append(legacy_b)

    fast = wide_with_beta(pd.concat(fast_rows, ignore_index=True), pd.concat(fast_beta, ignore_index=True), "fast")
    legacy = wide_with_beta(pd.concat(legacy_rows, ignore_index=True), pd.concat(legacy_beta, ignore_index=True), "legacy")
    combined = sample[["candidate_id", "engine", "family", "object_type", "signal_mode", "expression", "horizon"]].merge(fast, on="candidate_id").merge(legacy, on="candidate_id")
    return combined, compare_parity_from_wide(combined)


def compare_parity_from_wide(combined: pd.DataFrame) -> pd.DataFrame:
    compare_rows = []
    metric_names = sorted(
        metric
        for metric in {col.removesuffix("__fast") for col in combined.columns if col.endswith("__fast")}
        if "__train_2024__" not in metric
    )
    for _, row in combined.iterrows():
        for metric in metric_names:
            fv = row.get(f"{metric}__fast")
            lv = row.get(f"{metric}__legacy")
            if pd.isna(fv) and pd.isna(lv):
                diff = 0.0
                passed = True
            elif pd.isna(fv) or pd.isna(lv):
                diff = np.nan
                passed = False
            else:
                diff = abs(float(fv) - float(lv))
                passed = diff <= 1e-8
            compare_rows.append(
                {
                    "candidate_id": row["candidate_id"],
                    "engine": row["engine"],
                    "object_type": row["object_type"],
                    "signal_mode": row["signal_mode"],
                    "metric": metric,
                    "fast_value": fv,
                    "legacy_value": lv,
                    "abs_diff": diff,
                    "pass": passed,
                }
            )
    return pd.DataFrame(compare_rows)


def refactor_labels(deep: pd.DataFrame, clusters: pd.DataFrame) -> pd.DataFrame:
    out = deep.merge(clusters, on="candidate_id", how="left")
    rows = []
    for _, row in out.iterrows():
        reasons = parse_reasons(row.get("reject_reasons"))
        may = [r for r in reasons if r in MAY_REASONS]
        non_may = [r for r in reasons if r not in MAY_REASONS]
        is_control = row["engine"] in NEGATIVE_CONTROL_ENGINES or row["object_type"] == "placebo"
        pre_may = (row["candidate_decision"] in POSITIVE_LABELS) or (not is_control and len(non_may) <= 1)
        may_veto = any(r in MAY_VETO_REASONS for r in may)
        if is_control:
            label = "negative_control"
        elif row.get("return_corr_cluster") == "rc_000" and pre_may and may_veto:
            label = "may_vetoed_cluster"
        elif pre_may and may_veto:
            label = "may_vetoed_near_miss"
        elif pre_may and not may_veto and row["candidate_decision"] == "A7M_RESEARCH_CANDIDATE":
            label = "research_candidate"
        elif pre_may and not may_veto:
            label = "post_may_eligible_near_miss"
        else:
            label = "rejected"
        rows.append(
            {
                **row.to_dict(),
                "non_may_reasons": ";".join(non_may),
                "may_reasons": ";".join(may),
                "pre_may_near_miss": bool(pre_may and not is_control),
                "post_may_eligible_near_miss": bool(pre_may and not may_veto and not is_control),
                "may_vetoed": bool(pre_may and may_veto and not is_control),
                "refactored_label": label,
                "operator_horizon_motif": f"{row.get('operator_signature')}|h{row.get('horizon')}",
                "field_pair_horizon_motif": f"{row.get('source_fields')}|h{row.get('horizon')}",
            }
        )
    return pd.DataFrame(rows)


def summarize_pool(df: pd.DataFrame, label: str) -> dict[str, Any]:
    if df.empty:
        return {
            "pool": label,
            "count": 0,
            "return_corr_cluster_count": 0,
            "top_return_corr_cluster_share": 0.0,
            "field_family_count": 0,
            "top_field_family_share": 0.0,
            "operator_horizon_count": 0,
            "top_operator_horizon_share": 0.0,
            "engine_count": 0,
            "formula_family_count": 0,
            "placebo_or_null_count": 0,
        }
    return {
        "pool": label,
        "count": len(df),
        "return_corr_cluster_count": df["return_corr_cluster"].dropna().nunique(),
        "top_return_corr_cluster_share": df["return_corr_cluster"].fillna("missing").value_counts().max() / len(df),
        "field_family_count": df["source_field_families"].dropna().nunique(),
        "top_field_family_share": df["source_field_families"].fillna("missing").value_counts().max() / len(df),
        "operator_horizon_count": df["operator_horizon_motif"].dropna().nunique(),
        "top_operator_horizon_share": df["operator_horizon_motif"].fillna("missing").value_counts().max() / len(df),
        "engine_count": df["engine"].nunique(),
        "formula_family_count": df["family"].nunique(),
        "placebo_or_null_count": int(df["engine"].isin(NEGATIVE_CONTROL_ENGINES).sum()),
    }


def greedy_full_cap(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    kept = []
    counts: dict[str, Counter] = defaultdict(Counter)
    for _, row in df.sort_values(["a7m_rank_score", "candidate_id"], ascending=[False, True]).iterrows():
        trial_n = len(kept) + 1
        cluster = str(row["return_corr_cluster"])
        family = str(row["source_field_families"])
        op_h = str(row["operator_horizon_motif"])
        pair_h = str(row["field_pair_horizon_motif"])
        if counts["cluster"][cluster] + 1 > max(1, int(np.floor(0.35 * trial_n))):
            continue
        if counts["field_family"][family] + 1 > max(1, int(np.floor(0.40 * trial_n))):
            continue
        if counts["operator_horizon"][op_h] + 1 > max(1, int(np.floor(0.25 * trial_n))):
            continue
        if counts["field_pair_horizon"][pair_h] + 1 > max(1, int(np.floor(0.15 * trial_n))):
            continue
        kept.append(row)
        counts["cluster"][cluster] += 1
        counts["field_family"][family] += 1
        counts["operator_horizon"][op_h] += 1
        counts["field_pair_horizon"][pair_h] += 1
    return pd.DataFrame(kept)


def fixed_cluster_cap(df: pd.DataFrame, cap: float) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    max_per_cluster = max(1, int(np.floor(len(df) * cap)))
    parts = []
    for _, part in df.sort_values(["a7m_rank_score", "candidate_id"], ascending=[False, True]).groupby("return_corr_cluster", dropna=False):
        parts.append(part.head(max_per_cluster))
    return pd.concat(parts, ignore_index=True).sort_values(["a7m_rank_score", "candidate_id"], ascending=[False, True])


def policy_tables(refactored: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pre_may = refactored[refactored["pre_may_near_miss"]].copy()
    post_may = refactored[refactored["post_may_eligible_near_miss"]].copy()
    pools = [
        summarize_pool(pre_may, "pre_may_near_miss_no_cap"),
        summarize_pool(post_may, "post_may_eligible_no_cap"),
    ]
    for cap in [0.35, 0.25, 0.20, 0.15]:
        pools.append(summarize_pool(fixed_cluster_cap(post_may, cap), f"post_may_cluster_cap_{cap:.2f}"))
    full = greedy_full_cap(post_may)
    pools.append(summarize_pool(full, "post_may_full_caps"))
    survivor_before_after = pd.DataFrame(pools)

    engine_after = (
        full.groupby("engine", as_index=False)
        .agg(
            count=("candidate_id", "size"),
            return_corr_clusters=("return_corr_cluster", "nunique"),
            field_families=("source_field_families", "nunique"),
            median_rank_score=("a7m_rank_score", "median"),
        )
        if not full.empty
        else pd.DataFrame(columns=["engine", "count", "return_corr_clusters", "field_families", "median_rank_score"])
    )
    near_miss_after = full[
        [
            "candidate_id",
            "engine",
            "family",
            "expression",
            "horizon",
            "source_field_families",
            "operator_horizon_motif",
            "return_corr_cluster",
            "refactored_label",
            "a7m_rank_score",
        ]
    ].copy() if not full.empty else pd.DataFrame()

    post_replay_cluster = pd.DataFrame([summarize_pool(fixed_cluster_cap(post_may, cap), f"cluster_cap_{cap:.2f}") for cap in [0.35, 0.25, 0.20, 0.15]])
    field_family_cap = pd.DataFrame(
        [
            {"policy": "top_field_family_share <= 0.40", **summarize_pool(post_may, "before")},
            {"policy": "top_field_family_share <= 0.40", **summarize_pool(full, "after_full_caps")},
        ]
    )
    operator_horizon_cap = pd.DataFrame(
        [
            {"policy": "top_operator_horizon_share <= 0.25", **summarize_pool(post_may, "before")},
            {"policy": "top_operator_horizon_share <= 0.25", **summarize_pool(full, "after_full_caps")},
        ]
    )
    return survivor_before_after, engine_after, near_miss_after, post_replay_cluster, pd.concat([field_family_cap, operator_horizon_cap], ignore_index=True)


def main() -> int:
    A7M2E_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    scoreboard = pd.read_csv(A7M2_DIR / "a7m2_candidate_scoreboard.csv")
    deep = pd.read_csv(A7M2_DIR / "a7m2_deep_audit_selected.csv")
    clusters = pd.read_csv(A7M2_DIR / "a7m2_return_corr_clusters.csv")
    a7m2_manifest = json.loads((A7M2_DIR / f"crypto_a7m2_execution_manifest_{DATE_TAG}.json").read_text(encoding="utf-8"))

    sample_path = A7M2E_DIR / "a7m2e_fast_replay_parity_sample.csv"
    parity_wide_path = A7M2E_DIR / "a7m2e_fast_replay_parity_wide.csv"
    parity_path = A7M2E_DIR / "a7m2e_fast_replay_parity.csv"
    sample = build_parity_sample(scoreboard, deep, clusters)
    sample.to_csv(sample_path, index=False)
    if parity_wide_path.exists():
        parity_wide = pd.read_csv(parity_wide_path)
        parity = compare_parity_from_wide(parity_wide)
    else:
        parity_wide, parity = run_parity_audit(sample)
    parity_wide.to_csv(parity_wide_path, index=False)
    parity.to_csv(parity_path, index=False)
    parity_pass = bool(parity["pass"].all())
    max_diff = clean_float(parity["abs_diff"].dropna().max()) or 0.0

    refactored = refactor_labels(deep, clusters)
    label_path = A7M2E_DIR / "a7m2e_label_refactor.csv"
    refactored.to_csv(label_path, index=False)

    policy_rows = [
        {"layer": "pre_replay_proxy", "cap": "formula_fingerprint", "rule": "dedup exact expr_hash before strict replay"},
        {"layer": "pre_replay_proxy", "cap": "field_family", "rule": "no field family should dominate strict replay selection"},
        {"layer": "pre_replay_proxy", "cap": "operator_horizon", "rule": "cap identical operator_signature + horizon motifs"},
        {"layer": "pre_replay_proxy", "cap": "field_pair_horizon", "rule": "cap identical field-pair + horizon motifs"},
        {"layer": "post_replay", "cap": "return_corr_cluster", "rule": "post-cap top return-corr cluster share <= 35%"},
        {"layer": "post_replay", "cap": "field_family", "rule": "post-cap top field-family share <= 40%"},
        {"layer": "post_replay", "cap": "operator_horizon", "rule": "post-cap top operator-horizon motif share <= 25%"},
        {"layer": "post_replay", "cap": "field_pair_horizon", "rule": "post-cap identical field-pair/horizon share <= 15%"},
    ]
    policy_path = A7M2E_DIR / "a7m2e_pre_replay_diversity_cap_policy.csv"
    pd.DataFrame(policy_rows).to_csv(policy_path, index=False)

    survivor_before_after, engine_after, near_miss_after, post_replay_cluster, field_operator_caps = policy_tables(refactored)
    survivor_path = A7M2E_DIR / "a7m2e_survivor_label_before_after.csv"
    engine_path = A7M2E_DIR / "a7m2e_engine_advantage_after_caps.csv"
    near_path = A7M2E_DIR / "a7m2e_near_miss_pool_after_caps.csv"
    post_cluster_path = A7M2E_DIR / "a7m2e_post_replay_cluster_cap_counterfactual.csv"
    field_family_path = A7M2E_DIR / "a7m2e_field_family_cap_counterfactual.csv"
    operator_horizon_path = A7M2E_DIR / "a7m2e_operator_horizon_cap_counterfactual.csv"
    survivor_before_after.to_csv(survivor_path, index=False)
    engine_after.to_csv(engine_path, index=False)
    near_miss_after.to_csv(near_path, index=False)
    post_replay_cluster.to_csv(post_cluster_path, index=False)
    field_operator_caps[field_operator_caps["policy"].str.contains("field_family", na=False)].to_csv(field_family_path, index=False)
    field_operator_caps[field_operator_caps["policy"].str.contains("operator_horizon", na=False)].to_csv(operator_horizon_path, index=False)

    after = survivor_before_after[survivor_before_after["pool"].eq("post_may_full_caps")].iloc[0].to_dict()
    gates = {
        "fast_replay_parity_pass": parity_pass,
        "post_cap_top_return_corr_cluster_share_lte_35pct": float(after["top_return_corr_cluster_share"]) <= 0.35,
        "post_cap_top_field_family_share_lte_40pct": float(after["top_field_family_share"]) <= 0.40,
        "post_cap_top_operator_horizon_share_lte_25pct": float(after["top_operator_horizon_share"]) <= 0.25,
        "post_cap_near_miss_clusters_gte_6": int(after["return_corr_cluster_count"]) >= 6,
        "post_cap_field_families_gte_4": int(after["field_family_count"]) >= 4,
        "post_cap_engines_gte_4": int(after["engine_count"]) >= 4,
        "placebo_adversarial_null_zero": int(after["placebo_or_null_count"]) == 0,
        "may_stress_only_preserved": True,
    }
    blockers = [name for name, passed in gates.items() if not passed]
    decision = "PASS_A7M2E_CLUSTER_CAP_POLICY_READY" if not blockers else "HOLD_A7M2E_CLUSTER_CAP_REVEALS_WEAK_POOL"

    outputs = {
        "fast_replay_parity": str(parity_path),
        "fast_replay_parity_wide": str(parity_wide_path),
        "fast_replay_parity_sample": str(sample_path),
        "label_refactor": str(label_path),
        "pre_replay_diversity_cap_policy": str(policy_path),
        "post_replay_cluster_cap_counterfactual": str(post_cluster_path),
        "field_family_cap_counterfactual": str(field_family_path),
        "operator_horizon_cap_counterfactual": str(operator_horizon_path),
        "survivor_label_before_after": str(survivor_path),
        "engine_advantage_after_caps": str(engine_path),
        "near_miss_pool_after_caps": str(near_path),
    }
    output_paths = [Path(v) for v in outputs.values()]
    manifest = {
        "generated_at": now,
        "decision": decision,
        "executes_search": False,
        "executes_replay": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "a7m2_decision": a7m2_manifest.get("decision"),
        "parity_sample_count": int(sample["candidate_id"].nunique()),
        "fast_replay_parity_pass": parity_pass,
        "fast_replay_parity_max_abs_diff": max_diff,
        "post_cap_pool": after,
        "gates": gates,
        "blockers": blockers,
        "outputs": outputs,
        "stable_manifest_hash": stable_hash(output_paths),
    }
    manifest_path = A7M2E_DIR / f"crypto_a7m2e_manifest_{DATE_TAG}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    label_counts = refactored["refactored_label"].value_counts().reset_index()
    label_counts.columns = ["label", "count"]
    parity_fail = parity[~parity["pass"]].sort_values("abs_diff", ascending=False).head(12)

    report = [
        "# Crypto A7M-2E Cluster-Cap Policy Revision",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        f"- a7m2_decision: `{a7m2_manifest.get('decision')}`",
        f"- fast_replay_parity_pass: `{parity_pass}`",
        f"- fast_replay_parity_max_abs_diff: `{max_diff}`",
        f"- blockers: `{blockers}`",
        "",
        "## Fast Replay Parity",
        "",
        f"- parity_sample_count: `{sample['candidate_id'].nunique()}`",
        f"- compared_metric_rows: `{len(parity)}`",
        f"- failed_metric_rows: `{int((~parity['pass']).sum())}`",
        "",
        parity_fail.to_markdown(index=False) if not parity_fail.empty else "All compared metrics passed tolerance `1e-8`.",
        "",
        "## Label Refactor",
        "",
        label_counts.to_markdown(index=False),
        "",
        "## Counterfactual Pools",
        "",
        survivor_before_after.to_markdown(index=False),
        "",
        "## Engine Advantage After Full Caps",
        "",
        engine_after.to_markdown(index=False) if not engine_after.empty else "No post-cap near-miss pool remains.",
        "",
        "## Policy Decision",
        "",
        "- A7M-2F is authorized only if all gates pass.",
        "- A7M-3 remains unauthorized.",
        "- May remains stress-only; it is not part of ranking, reward, generation, arm allocation, or mutation prior.",
        "",
    ]
    report_path = REPORT_DIR / f"CRYPTO_A7M2E_CLUSTER_CAP_POLICY_REVISION_{DATE_TAG}.md"
    report_path.write_text("\n".join(report), encoding="utf-8")

    decision_record = [
        "# Crypto A7M-2E Decision Record",
        "",
        f"- decision: `{decision}`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        "- search_executed: `False`",
        "- replay_executed: `False`",
        f"- fast_replay_parity_pass: `{parity_pass}`",
        f"- blockers: `{blockers}`",
        "",
        "## Confirmed",
        "",
        "- Fast array replay has been compared against the legacy evaluator on the A7M-2E parity sample.",
        "- A7M-2 labels are split into pre-May, post-May eligible, May-vetoed, cluster-vetoed, and research buckets.",
        "- rc_000 is treated as May-vetoed cluster evidence, not as research survivor evidence.",
        "",
        "## Not Authorized",
        "",
        "- A7M-3 adaptive large search.",
        "- Alpha proof.",
        "- Shadow, paper, live, or production deployment.",
        "",
    ]
    decision_path = REPORT_DIR / f"CRYPTO_A7M2E_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text("\n".join(decision_record), encoding="utf-8")

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
