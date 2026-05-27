from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR


DATE_TAG = "20260520"
A7M2_DIR = RUNTIME_DIR / "a7m2_equal_budget_engine_bakeoff"
A7M2E_DIR = RUNTIME_DIR / "a7m2e_cluster_cap_policy_revision"
A7N_DIR = RUNTIME_DIR / "a7n_regime_invariant_counterfactual"

NEGATIVE_CONTROL_ENGINES = {"E6_placebo_random_control", "E7_adversarial_null_wrong_lag_control"}

NON_MAY_TERMS = {
    "raw_validation": "raw_10bp__validation_2025H1__annualized_mean",
    "raw_recent": "raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
    "residual_funding_validation": "residual_vs_funding_10bp__validation_2025H1__annualized_mean",
    "residual_funding_recent": "residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
    "residual_core4_validation": "residual_vs_core4_10bp__validation_2025H1__annualized_mean",
    "residual_core4_recent": "residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
    "cost20_validation": "raw_20bp__validation_2025H1__annualized_mean",
    "cost20_recent": "raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean",
    "lag1_validation": "execution_lag_1bar_raw_10bp__validation_2025H1__annualized_mean",
    "lag1_recent": "execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def stable_file_hash(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for path in sorted(paths, key=lambda p: str(p)):
        h.update(str(path).encode("utf-8"))
        h.update(str(path.stat().st_size).encode("utf-8"))
        h.update(str(int(path.stat().st_mtime)).encode("utf-8"))
    return h.hexdigest()


def num(df: pd.DataFrame, col: str, default: float = np.nan) -> pd.Series:
    if col not in df.columns:
        return pd.Series(default, index=df.index, dtype="float64")
    return pd.to_numeric(df[col], errors="coerce")


def normalized_motif(df: pd.DataFrame) -> pd.Series:
    op = df.get("operator_signature", pd.Series("", index=df.index)).astype(str)
    horizon = pd.to_numeric(df.get("horizon", pd.Series(0, index=df.index)), errors="coerce").fillna(0).astype(int)
    return op + "|h" + horizon.astype(str)


def has_liquidity_volatility(df: pd.DataFrame) -> pd.Series:
    fam = df.get("source_field_families", pd.Series("", index=df.index)).astype(str)
    return fam.str.contains("liquidity", regex=False) & fam.str.contains("volatility", regex=False)


def objective_contract(now: str) -> dict[str, Any]:
    return {
        "contract_id": "CRYPTO_A7N_REGIME_INVARIANT_OBJECTIVE_V1",
        "generated_at": now,
        "phase": "A7N-0",
        "decision": "PASS_A7N0_OBJECTIVE_CONTRACT",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7n3": False,
        "objective": {
            "primary": [
                "min_non_may_raw_validation_recent",
                "min_non_may_residual_vs_fundingcore",
                "min_non_may_residual_vs_core4",
                "min_non_may_cost20",
                "min_non_may_lag1",
                "positive_non_may_term_rate",
                "diversity_adjusted_selection",
            ],
            "penalties": [
                "non_may_term_dispersion",
                "funding_beta_abs",
                "core4_beta_abs",
                "turnover_proxy",
                "drawdown_proxy",
                "field_family_concentration",
                "operator_horizon_concentration",
                "formula_family_concentration",
            ],
            "not_used": [
                "May annualized returns",
                "May residual returns",
                "May severe-fail margin",
                "May symbol LOO",
                "May-derived thresholds",
            ],
        },
        "may_policy": {
            "allowed": ["post_selection_stress_label", "post_selection_veto", "failure_attribution"],
            "forbidden": [
                "ranking",
                "reward",
                "threshold_tuning",
                "weight_selection",
                "candidate_selection",
                "generator_tuning",
                "arm_allocation",
                "mutation_prior",
                "surrogate_target",
            ],
        },
        "a7n3_required_before_execution": [
            "A7N-2 counterfactual top-decile must suppress rc_000/liquidity-volatility without May",
            "post-May eligible near-miss pool target must be explicit",
            "pre-replay diversity caps must be active",
            "post-replay return-corr caps must be active",
        ],
    }


def regime_fold_library(now: str) -> pd.DataFrame:
    rows = [
        {
            "fold_id": "F0_calendar_block_folds",
            "feature_source": "timestamp",
            "definition": "validation/recent monthly or biweekly calendar blocks",
            "purpose": "avoid one block supporting candidate ranking",
            "may_allowed": False,
            "status": "contract_only_not_replayed",
        },
        {
            "fold_id": "F1_high_realized_vol_fold",
            "feature_source": "realized_vol_6/12/24",
            "definition": "top non-May realized volatility quantile inside validation/recent",
            "purpose": "stress volatility-regime dependence",
            "may_allowed": False,
            "status": "contract_only_not_replayed",
        },
        {
            "fold_id": "F2_low_liquidity_fold",
            "feature_source": "quote_volume/trade_count/activity",
            "definition": "bottom non-May liquidity/activity quantile inside validation/recent",
            "purpose": "stress liquidity fragility",
            "may_allowed": False,
            "status": "contract_only_not_replayed",
        },
        {
            "fold_id": "F3_high_liquidity_high_vol_fold",
            "feature_source": "quote volume x realized volatility",
            "definition": "intersection of high liquidity and high volatility inside validation/recent",
            "purpose": "constrain liquidity-volatility collapse without May labels",
            "may_allowed": False,
            "status": "contract_only_not_replayed",
        },
        {
            "fold_id": "F4_basis_dislocation_fold",
            "feature_source": "mark_index_ratio/premium_index/mark_minus_index",
            "definition": "large absolute basis or premium dislocation inside validation/recent",
            "purpose": "stress basis-regime dependence",
            "may_allowed": False,
            "status": "contract_only_not_replayed",
        },
        {
            "fold_id": "F5_funding_neutral_fold",
            "feature_source": "latest_known_funding_rate/funding persistence",
            "definition": "non-extreme funding state inside validation/recent",
            "purpose": "detect hidden funding-family wrappers",
            "may_allowed": False,
            "status": "contract_only_not_replayed",
        },
        {
            "fold_id": "F6_cross_symbol_dispersion_fold",
            "feature_source": "cross-symbol returns/vol/basis dispersion",
            "definition": "high cross-symbol dispersion inside validation/recent",
            "purpose": "stress cross-sectional stability",
            "may_allowed": False,
            "status": "contract_only_not_replayed",
        },
        {
            "fold_id": "F7_trend_reversal_fold",
            "feature_source": "non-May trend/reversal state",
            "definition": "trend to reversal or reverse-shock blocks inside validation/recent",
            "purpose": "avoid one-direction trend-only alpha wrappers",
            "may_allowed": False,
            "status": "contract_only_not_replayed",
        },
    ]
    out = pd.DataFrame(rows)
    out.insert(1, "generated_at", now)
    return out


def add_a7n_scores(df: pd.DataFrame, population_name: str) -> pd.DataFrame:
    out = df.copy()
    terms = pd.DataFrame({name: num(out, col) for name, col in NON_MAY_TERMS.items()}, index=out.index)
    clipped = terms.clip(lower=-2.0, upper=2.0)
    out["a7n_min_non_may_raw"] = clipped[["raw_validation", "raw_recent"]].min(axis=1)
    out["a7n_min_non_may_residual_funding"] = clipped[["residual_funding_validation", "residual_funding_recent"]].min(axis=1)
    out["a7n_min_non_may_residual_core4"] = clipped[["residual_core4_validation", "residual_core4_recent"]].min(axis=1)
    out["a7n_min_non_may_cost20"] = clipped[["cost20_validation", "cost20_recent"]].min(axis=1)
    out["a7n_min_non_may_lag1"] = clipped[["lag1_validation", "lag1_recent"]].min(axis=1)
    out["a7n_positive_non_may_term_rate"] = (terms > 0).mean(axis=1)
    out["a7n_non_may_dispersion"] = clipped.std(axis=1)

    dd_cols = [
        "raw_10bp__validation_2025H1__compounded_max_dd",
        "raw_10bp__recent_oos_2025H2_2026Apr__compounded_max_dd",
        "raw_20bp__validation_2025H1__compounded_max_dd",
        "raw_20bp__recent_oos_2025H2_2026Apr__compounded_max_dd",
        "execution_lag_1bar_raw_10bp__validation_2025H1__compounded_max_dd",
        "execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__compounded_max_dd",
    ]
    dd = pd.concat([num(out, c) for c in dd_cols], axis=1).min(axis=1).abs().fillna(0.0)
    turnover = pd.concat(
        [
            num(out, "raw_10bp__validation_2025H1__mean_turnover"),
            num(out, "raw_10bp__recent_oos_2025H2_2026Apr__mean_turnover"),
        ],
        axis=1,
    ).mean(axis=1).fillna(0.0)
    beta = num(out, "funding_beta_recent").abs().clip(0.0, 2.0).fillna(0.0) + num(out, "core4_beta_recent").abs().clip(0.0, 2.0).fillna(0.0)

    out["operator_horizon_motif"] = normalized_motif(out)
    out["field_pair_horizon_motif"] = out.get("source_fields", pd.Series("", index=out.index)).astype(str) + "|h" + pd.to_numeric(
        out.get("horizon", pd.Series(0, index=out.index)), errors="coerce"
    ).fillna(0).astype(int).astype(str)
    out["formula_family_motif"] = (
        out.get("source_field_families", pd.Series("", index=out.index)).astype(str)
        + "|"
        + out.get("operator_signature", pd.Series("", index=out.index)).astype(str)
        + "|h"
        + pd.to_numeric(out.get("horizon", pd.Series(0, index=out.index)), errors="coerce").fillna(0).astype(int).astype(str)
    )

    def share_penalty(series: pd.Series) -> pd.Series:
        counts = series.value_counts(dropna=False)
        return series.map(counts).astype(float).fillna(0.0) / max(1, len(series))

    out["a7n_field_family_concentration"] = share_penalty(out.get("source_field_families", pd.Series("", index=out.index)).astype(str))
    out["a7n_operator_horizon_concentration"] = share_penalty(out["operator_horizon_motif"])
    out["a7n_formula_family_concentration"] = share_penalty(out["formula_family_motif"])
    out["a7n_is_liquidity_volatility"] = has_liquidity_volatility(out)
    out["a7n_negative_control"] = out.get("engine", pd.Series("", index=out.index)).isin(NEGATIVE_CONTROL_ENGINES)

    out["a7n_regime_invariant_score"] = (
        1.4 * out["a7n_min_non_may_raw"]
        + 1.2 * out["a7n_min_non_may_residual_funding"]
        + 1.0 * out["a7n_min_non_may_residual_core4"]
        + 0.9 * out["a7n_min_non_may_cost20"]
        + 0.9 * out["a7n_min_non_may_lag1"]
        + 1.0 * out["a7n_positive_non_may_term_rate"]
        - 0.45 * out["a7n_non_may_dispersion"]
        - 0.30 * dd
        - 0.35 * turnover
        - 0.30 * beta
        - 1.20 * out["a7n_field_family_concentration"]
        - 0.80 * out["a7n_operator_horizon_concentration"]
        - 0.50 * out["a7n_formula_family_concentration"]
        - 5.00 * out["a7n_negative_control"].astype(float)
    )
    out["a7n_score_population"] = population_name
    return out


def top_summary(df: pd.DataFrame, score_col: str, label: str, top_n: int | None = None) -> dict[str, Any]:
    if top_n is None:
        top_n = max(1, int(len(df) * 0.10))
    top = df.sort_values(score_col, ascending=False).head(top_n).copy()
    return summarize_pool(top, label, score_col)


def summarize_pool(pool: pd.DataFrame, label: str, score_col: str) -> dict[str, Any]:
    if pool.empty:
        return {
            "pool": label,
            "score_col": score_col,
            "count": 0,
            "return_corr_cluster_count": 0,
            "top_return_corr_cluster_share": 0.0,
            "rc_000_share": 0.0,
            "field_family_count": 0,
            "top_field_family_share": 0.0,
            "liquidity_volatility_share": 0.0,
            "engine_count": 0,
            "placebo_or_null_count": 0,
            "operator_horizon_count": 0,
            "top_operator_horizon_share": 0.0,
        }
    cluster = pool.get("return_corr_cluster", pd.Series("", index=pool.index)).astype(str)
    family = pool.get("source_field_families", pd.Series("", index=pool.index)).astype(str)
    engine = pool.get("engine", pd.Series("", index=pool.index)).astype(str)
    motif = pool.get("operator_horizon_motif", normalized_motif(pool)).astype(str)
    cluster_counts = Counter(cluster[cluster.ne("")])
    family_counts = Counter(family[family.ne("")])
    motif_counts = Counter(motif[motif.ne("")])
    return {
        "pool": label,
        "score_col": score_col,
        "count": int(len(pool)),
        "return_corr_cluster_count": int(cluster[cluster.ne("")].nunique()),
        "top_return_corr_cluster_share": float(max(cluster_counts.values()) / len(pool)) if cluster_counts else 0.0,
        "rc_000_share": float(cluster.eq("rc_000").mean()) if len(pool) else 0.0,
        "field_family_count": int(family[family.ne("")].nunique()),
        "top_field_family_share": float(max(family_counts.values()) / len(pool)) if family_counts else 0.0,
        "liquidity_volatility_share": float(has_liquidity_volatility(pool).mean()),
        "engine_count": int(engine[engine.ne("")].nunique()),
        "placebo_or_null_count": int(engine.isin(NEGATIVE_CONTROL_ENGINES).sum()),
        "operator_horizon_count": int(motif[motif.ne("")].nunique()),
        "top_operator_horizon_share": float(max(motif_counts.values()) / len(pool)) if motif_counts else 0.0,
    }


def diversity_capped_selection(df: pd.DataFrame, score_col: str, top_n: int) -> pd.DataFrame:
    selected: list[int] = []
    field_counts: Counter[str] = Counter()
    engine_counts: Counter[str] = Counter()
    motif_counts: Counter[str] = Counter()
    liqvol_count = 0
    for idx, row in df.sort_values(score_col, ascending=False).iterrows():
        if len(selected) >= top_n:
            break
        engine = str(row.get("engine", ""))
        if engine in NEGATIVE_CONTROL_ENGINES:
            continue
        field = str(row.get("source_field_families", ""))
        motif = str(row.get("operator_horizon_motif", ""))
        liqvol = bool(row.get("a7n_is_liquidity_volatility", False))
        if liqvol and liqvol_count + 1 > max(1, int(0.30 * top_n)):
            continue
        if field_counts[field] + 1 > max(1, int(0.40 * top_n)):
            continue
        if motif_counts[motif] + 1 > max(1, int(0.25 * top_n)):
            continue
        if engine_counts[engine] + 1 > max(1, int(0.35 * top_n)):
            continue
        selected.append(idx)
        field_counts[field] += 1
        engine_counts[engine] += 1
        motif_counts[motif] += 1
        liqvol_count += int(liqvol)
    return df.loc[selected].copy()


def write_markdown_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "(empty)\n"
    return df.head(max_rows).to_markdown(index=False) + "\n"


def main() -> int:
    A7N_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    scoreboard_path = A7M2_DIR / "a7m2_candidate_scoreboard.csv"
    label_path = A7M2E_DIR / "a7m2e_label_refactor.csv"
    if not scoreboard_path.exists() or not label_path.exists():
        missing = [str(p) for p in [scoreboard_path, label_path] if not p.exists()]
        raise FileNotFoundError(f"missing A7M2/A7M2E input files: {missing}")

    objective = objective_contract(now)
    folds = regime_fold_library(now)
    strict = add_a7n_scores(pd.read_csv(scoreboard_path), "strict_4096")
    deep = add_a7n_scores(pd.read_csv(label_path), "deep_512")

    strict_top_n = max(1, int(len(strict) * 0.10))
    deep_top_n = max(1, int(len(deep) * 0.10))
    strict_capped = diversity_capped_selection(strict, "a7n_regime_invariant_score", strict_top_n)
    deep_capped = diversity_capped_selection(deep, "a7n_regime_invariant_score", deep_top_n)

    summary_rows = [
        top_summary(strict, "a7m_rank_score", "strict_old_a7m_top_decile", strict_top_n),
        top_summary(strict, "a7n_regime_invariant_score", "strict_a7n_raw_top_decile", strict_top_n),
        summarize_pool(strict_capped, "strict_a7n_diversity_capped_top_decile", "a7n_regime_invariant_score"),
        top_summary(deep, "a7m_rank_score", "deep_old_a7m_top_decile", deep_top_n),
        top_summary(deep, "a7n_regime_invariant_score", "deep_a7n_raw_top_decile", deep_top_n),
        summarize_pool(deep_capped, "deep_a7n_diversity_capped_top_decile", "a7n_regime_invariant_score"),
    ]
    summary = pd.DataFrame(summary_rows)

    strict_pass_row = summary[summary["pool"].eq("strict_a7n_diversity_capped_top_decile")].iloc[0].to_dict()
    deep_pass_row = summary[summary["pool"].eq("deep_a7n_diversity_capped_top_decile")].iloc[0].to_dict()
    gates = {
        "may_excluded_from_score_components": True,
        "strict_liquidity_volatility_share_lte_30pct": strict_pass_row["liquidity_volatility_share"] <= 0.30,
        "strict_field_families_gte_4": strict_pass_row["field_family_count"] >= 4,
        "strict_engines_gte_4": strict_pass_row["engine_count"] >= 4,
        "strict_placebo_null_zero": strict_pass_row["placebo_or_null_count"] == 0,
        "deep_rc000_share_lte_35pct": deep_pass_row["rc_000_share"] <= 0.35,
        "deep_return_corr_clusters_gte_6": deep_pass_row["return_corr_cluster_count"] >= 6,
        "deep_field_families_gte_4": deep_pass_row["field_family_count"] >= 4,
        "deep_engines_gte_4": deep_pass_row["engine_count"] >= 4,
        "deep_placebo_null_zero": deep_pass_row["placebo_or_null_count"] == 0,
    }
    blockers = [name for name, ok in gates.items() if not ok]
    decision = "PASS_A7N2_OBJECTIVE_READY_FOR_A7N3" if not blockers else "HOLD_A7N2_OBJECTIVE_STILL_COLLAPSES"

    strict_cols = [
        "candidate_id",
        "engine",
        "source_field_families",
        "operator_signature",
        "horizon",
        "expression",
        "a7m_rank_score",
        "a7n_regime_invariant_score",
        "a7n_min_non_may_raw",
        "a7n_min_non_may_residual_funding",
        "a7n_min_non_may_cost20",
        "a7n_min_non_may_lag1",
        "candidate_decision",
        "reject_reasons",
    ]
    deep_cols = strict_cols + [
        "return_corr_cluster",
        "refactored_label",
        "may_vetoed",
        "pre_may_near_miss",
        "post_may_eligible_near_miss",
    ]

    objective_path = A7N_DIR / f"crypto_a7n0_objective_contract_{DATE_TAG}.json"
    folds_path = A7N_DIR / "a7n1_non_may_regime_fold_library.csv"
    strict_scores_path = A7N_DIR / "a7n2_strict_counterfactual_scores.csv"
    deep_scores_path = A7N_DIR / "a7n2_deep_counterfactual_scores.csv"
    summary_path = A7N_DIR / "a7n2_top_decile_counterfactual_summary.csv"
    strict_top_path = A7N_DIR / "a7n2_strict_diversity_capped_top_decile.csv"
    deep_top_path = A7N_DIR / "a7n2_deep_diversity_capped_top_decile.csv"
    may_audit_path = A7N_DIR / "a7n2_may_exclusion_audit.csv"
    gates_path = A7N_DIR / "a7n2_gate_summary.csv"
    manifest_path = A7N_DIR / f"crypto_a7n_manifest_{DATE_TAG}.json"

    write_json(objective_path, objective)
    folds.to_csv(folds_path, index=False)
    strict[strict_cols].to_csv(strict_scores_path, index=False)
    deep[[c for c in deep_cols if c in deep.columns]].to_csv(deep_scores_path, index=False)
    summary.to_csv(summary_path, index=False)
    strict_capped[strict_cols].to_csv(strict_top_path, index=False)
    deep_capped[[c for c in deep_cols if c in deep_capped.columns]].to_csv(deep_top_path, index=False)
    may_audit = pd.DataFrame(
        [
            {"check": "May columns used in A7N score", "status": "PASS", "detail": "No fresh_forward_2026May columns are referenced by score construction."},
            {"check": "May reject reasons used in score", "status": "PASS", "detail": "reject_reasons and refactored labels are evaluation outputs only."},
            {"check": "May used for generator/arm allocation", "status": "PASS", "detail": "A7N-2 executes no generation and no allocation."},
            {"check": "A7N-1 fold source", "status": "PASS", "detail": "Fold library is validation/recent contract-only; May is forbidden."},
        ]
    )
    may_audit.to_csv(may_audit_path, index=False)
    gate_df = pd.DataFrame([{"gate": k, "pass": bool(v)} for k, v in gates.items()])
    gate_df.to_csv(gates_path, index=False)

    manifest = {
        "generated_at": now,
        "decision": decision,
        "phase_status": {
            "A7N-0": "PASS_A7N0_OBJECTIVE_CONTRACT",
            "A7N-1": "PASS_A7N1_FOLD_LIBRARY_CONTRACT_ONLY",
            "A7N-2": decision,
        },
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "authorizes_a7n3": decision == "PASS_A7N2_OBJECTIVE_READY_FOR_A7N3",
        "authorizes_a7m3": False,
        "may_policy": objective["may_policy"],
        "counterfactual_scope": "A7M-2 strict/deep existing candidate tables only; no new formula generation and no new replay.",
        "fold_replay_status": "not_executed_contract_only",
        "gates": gates,
        "summary": summary_rows,
        "outputs": {
            "objective_contract": str(objective_path),
            "fold_library": str(folds_path),
            "strict_counterfactual_scores": str(strict_scores_path),
            "deep_counterfactual_scores": str(deep_scores_path),
            "top_decile_summary": str(summary_path),
            "strict_diversity_capped_top_decile": str(strict_top_path),
            "deep_diversity_capped_top_decile": str(deep_top_path),
            "may_exclusion_audit": str(may_audit_path),
            "gate_summary": str(gates_path),
        },
    }
    manifest["stable_manifest_hash"] = stable_file_hash(
        [objective_path, folds_path, strict_scores_path, deep_scores_path, summary_path, strict_top_path, deep_top_path, may_audit_path, gates_path]
    )
    write_json(manifest_path, manifest)

    report = [
        "# Crypto A7N Regime-Invariant Counterfactual",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        f"- authorizes_a7n3: `{manifest['authorizes_a7n3']}`",
        f"- blockers: `{blockers}`",
        "",
        "## A7N-0 Objective Contract",
        "",
        "The objective replaces mean validation/recent strength with non-May worst-case survival terms:",
        "",
        "- min raw validation/recent",
        "- min residual vs FundingCore/Core4 validation/recent",
        "- min cost20 validation/recent",
        "- min 1bar-lag validation/recent",
        "- positive non-May term rate",
        "- field/operator/formula concentration penalties",
        "",
        "May is stress-only and is not used in score construction, ranking, generation, arm allocation, or mutation.",
        "",
        "## A7N-1 Non-May Fold Library",
        "",
        write_markdown_table(folds),
        "These are fold contracts only. Existing A7M-2 artifacts do not contain per-regime-fold replay metrics, so A7N-2 uses split-level non-May metrics plus structural diversity proxies.",
        "",
        "## A7N-2 Counterfactual Summary",
        "",
        write_markdown_table(summary),
        "## Gate Summary",
        "",
        write_markdown_table(gate_df),
        "## Decision",
        "",
        "- A7N-3 is authorized only if A7N-2 gates pass.",
        "- A7M-3 remains unauthorized.",
        "- No alpha proof, shadow, paper, or live deployment is authorized.",
    ]
    report_path = REPORT_DIR / f"CRYPTO_A7N_REGIME_INVARIANT_COUNTERFACTUAL_{DATE_TAG}.md"
    report_path.write_text("\n".join(report), encoding="utf-8")

    decision_record = [
        "# Crypto A7N Decision Record",
        "",
        f"- decision: `{decision}`",
        "- A7N-0: `PASS_A7N0_OBJECTIVE_CONTRACT`",
        "- A7N-1: `PASS_A7N1_FOLD_LIBRARY_CONTRACT_ONLY`",
        f"- A7N-2: `{decision}`",
        f"- authorizes_a7n3: `{manifest['authorizes_a7n3']}`",
        "- authorizes_a7m3: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "A7N-2 did not run new formula search or replay. It tested whether a non-May regime-invariant, diversity-first objective can suppress the A7M-2 failure mode on existing candidates.",
        "",
        "May remains post-selection stress/veto only. It is not a score, threshold, generation, allocation, or mutation input.",
    ]
    decision_path = REPORT_DIR / f"CRYPTO_A7N_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text("\n".join(decision_record), encoding="utf-8")

    print(
        json.dumps(
            {
                "decision": decision,
                "blockers": blockers,
                "authorizes_a7n3": manifest["authorizes_a7n3"],
                "manifest": str(manifest_path),
                "report": str(report_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
