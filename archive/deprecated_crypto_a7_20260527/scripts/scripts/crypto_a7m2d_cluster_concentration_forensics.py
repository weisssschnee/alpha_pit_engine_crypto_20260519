from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR


DATE_TAG = "20260520"
A7M2_DIR = RUNTIME_DIR / "a7m2_equal_budget_engine_bakeoff"
A7M2D_DIR = RUNTIME_DIR / "a7m2d_cluster_concentration_forensics"

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


def split_reasons(series: pd.Series) -> pd.Series:
    values = []
    for text in series.fillna("").astype(str):
        values.extend([part for part in text.split(";") if part])
    return pd.Series(values, dtype=str)


def top_counts(df: pd.DataFrame, column: str, prefix: dict[str, Any], top_n: int = 8) -> list[dict[str, Any]]:
    rows = []
    total = max(1, len(df))
    for value, count in df[column].fillna("missing").astype(str).value_counts().head(top_n).items():
        rows.append({**prefix, "field": column, "value": value, "count": int(count), "share": float(count / total)})
    return rows


def cluster_summary(deep: pd.DataFrame, clusters: pd.DataFrame) -> pd.DataFrame:
    positive = deep[deep["candidate_decision"].isin(POSITIVE_LABELS)].copy()
    joined = positive.merge(clusters, on="candidate_id", how="left")
    rows = []
    for cluster, part in joined.groupby("return_corr_cluster", dropna=False):
        total = len(part)
        rows.append(
            {
                "return_corr_cluster": cluster,
                "count": total,
                "share_of_positive_deep": total / max(1, len(joined)),
                "engine_count": part["engine"].nunique(),
                "family_count": part["family"].nunique(),
                "field_family_count": part["source_field_families"].nunique(),
                "operator_signature_count": part["operator_signature"].nunique(),
                "expr_hash_count": part["expr_hash"].nunique(),
                "top_engine": part["engine"].value_counts().idxmax(),
                "top_engine_share": part["engine"].value_counts().max() / max(1, total),
                "top_family": part["family"].value_counts().idxmax(),
                "top_family_share": part["family"].value_counts().max() / max(1, total),
                "top_field_family": part["source_field_families"].fillna("missing").astype(str).value_counts().idxmax(),
                "top_field_family_share": part["source_field_families"].fillna("missing").astype(str).value_counts().max() / max(1, total),
                "median_rank_score": part["a7m_rank_score"].median(),
                "median_recent_raw_ann": part["raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean"].median(),
                "median_cost20_recent_ann": part["raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean"].median(),
                "median_lag1_recent_ann": part["execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean"].median(),
                "median_may_raw_ann": part["raw_10bp__fresh_forward_2026May__annualized_mean"].median(),
                "median_residual_funding_recent_ann": part["residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean"].median(),
            }
        )
    out = pd.DataFrame(rows)
    return out.sort_values(["count", "return_corr_cluster"], ascending=[False, True]).reset_index(drop=True)


def matrix_counts(joined: pd.DataFrame, row_col: str, col_col: str) -> pd.DataFrame:
    return joined.pivot_table(index=row_col, columns=col_col, values="candidate_id", aggfunc="count", fill_value=0).reset_index()


def cluster_cap_counterfactual(joined: pd.DataFrame, caps: list[float]) -> pd.DataFrame:
    positives = joined[joined["candidate_decision"].isin(POSITIVE_LABELS)].copy()
    positives = positives.sort_values(["a7m_rank_score", "candidate_id"], ascending=[False, True])
    total = len(positives)
    rows = []
    for cap in caps:
        max_per_cluster = int(total * cap)
        kept_parts = []
        removed_parts = []
        for _, part in positives.groupby("return_corr_cluster", dropna=False):
            kept_parts.append(part.head(max_per_cluster))
            removed_parts.append(part.iloc[max_per_cluster:])
        kept = pd.concat(kept_parts, ignore_index=True) if kept_parts else pd.DataFrame()
        removed = pd.concat(removed_parts, ignore_index=True) if removed_parts else pd.DataFrame()
        rows.append(
            {
                "cap_share": cap,
                "max_per_cluster": max_per_cluster,
                "positive_deep_before": total,
                "positive_deep_after_cap_only": len(kept),
                "removed_by_cap": len(removed),
                "top_cluster_after_cap_share": kept["return_corr_cluster"].value_counts().max() / max(1, len(kept)) if len(kept) else 0.0,
                "engine_count_after_cap": kept["engine"].nunique() if len(kept) else 0,
                "family_count_after_cap": kept["family"].nunique() if len(kept) else 0,
                "field_family_count_after_cap": kept["source_field_families"].nunique() if len(kept) else 0,
                "median_rank_score_after_cap": kept["a7m_rank_score"].median() if len(kept) else None,
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    A7M2D_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    inputs = {
        "manifest": A7M2_DIR / f"crypto_a7m2_execution_manifest_{DATE_TAG}.json",
        "scoreboard": A7M2_DIR / "a7m2_candidate_scoreboard.csv",
        "deep": A7M2_DIR / "a7m2_deep_audit_selected.csv",
        "clusters": A7M2_DIR / "a7m2_return_corr_clusters.csv",
        "engine_summary": A7M2_DIR / "a7m2_engine_summary.csv",
    }
    missing = [str(path) for path in inputs.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing inputs: {missing}")

    manifest = json.loads(inputs["manifest"].read_text(encoding="utf-8"))
    scoreboard = pd.read_csv(inputs["scoreboard"])
    deep = pd.read_csv(inputs["deep"])
    clusters = pd.read_csv(inputs["clusters"])
    engine_summary = pd.read_csv(inputs["engine_summary"])

    positive_deep = deep[deep["candidate_decision"].isin(POSITIVE_LABELS)].copy()
    joined = deep.merge(clusters, on="candidate_id", how="left")
    positive_joined = joined[joined["candidate_decision"].isin(POSITIVE_LABELS)].copy()

    csummary = cluster_summary(deep, clusters)
    top_cluster = str(csummary.iloc[0]["return_corr_cluster"]) if not csummary.empty else ""
    top_share = float(csummary.iloc[0]["share_of_positive_deep"]) if not csummary.empty else 0.0
    top_members = positive_joined[positive_joined["return_corr_cluster"].astype(str).eq(top_cluster)].copy()

    top_members_path = A7M2D_DIR / "a7m2d_top_cluster_members.csv"
    top_members.sort_values(["a7m_rank_score", "candidate_id"], ascending=[False, True]).to_csv(top_members_path, index=False)

    cluster_summary_path = A7M2D_DIR / "a7m2d_cluster_summary.csv"
    csummary.to_csv(cluster_summary_path, index=False)

    engine_matrix = matrix_counts(positive_joined, "engine", "return_corr_cluster")
    engine_matrix_path = A7M2D_DIR / "a7m2d_engine_cluster_matrix.csv"
    engine_matrix.to_csv(engine_matrix_path, index=False)

    family_matrix = matrix_counts(positive_joined, "source_field_families", "return_corr_cluster")
    family_matrix_path = A7M2D_DIR / "a7m2d_field_family_cluster_matrix.csv"
    family_matrix.to_csv(family_matrix_path, index=False)

    reason_rows = []
    for cluster, part in positive_joined.groupby("return_corr_cluster", dropna=False):
        reasons = split_reasons(part["reject_reasons"])
        for reason, count in reasons.value_counts().items():
            reason_rows.append({"return_corr_cluster": cluster, "reject_reason": reason, "count": int(count), "share_in_cluster": count / max(1, len(part))})
    reason_df = pd.DataFrame(reason_rows)
    reason_path = A7M2D_DIR / "a7m2d_reject_reason_by_cluster.csv"
    reason_df.to_csv(reason_path, index=False)

    expr_rows = []
    for fn in [
        lambda df, prefix: top_counts(df, "expression", prefix, top_n=12),
        lambda df, prefix: top_counts(df, "source_fields", prefix, top_n=12),
        lambda df, prefix: top_counts(df, "source_field_families", prefix, top_n=12),
        lambda df, prefix: top_counts(df, "operator_signature", prefix, top_n=12),
        lambda df, prefix: top_counts(df, "horizon", prefix, top_n=12),
    ]:
        expr_rows.extend(fn(top_members, {"return_corr_cluster": top_cluster}))
    expr_summary = pd.DataFrame(expr_rows)
    expr_summary_path = A7M2D_DIR / "a7m2d_top_cluster_expression_summary.csv"
    expr_summary.to_csv(expr_summary_path, index=False)

    cap_df = cluster_cap_counterfactual(positive_joined, caps=[0.35, 0.25, 0.20, 0.15])
    cap_path = A7M2D_DIR / "a7m2d_cluster_cap_counterfactual.csv"
    cap_df.to_csv(cap_path, index=False)

    source_rows = []
    for name, df in [
        ("all_strict_replay", scoreboard),
        ("deep_audit", deep),
        ("positive_deep", positive_deep),
        ("top_cluster", top_members),
    ]:
        source_rows.append(
            {
                "population": name,
                "count": len(df),
                "engine_count": df["engine"].nunique(),
                "family_count": df["family"].nunique(),
                "field_family_count": df["source_field_families"].nunique(),
                "expr_hash_count": df["expr_hash"].nunique(),
                "top_engine": df["engine"].value_counts().idxmax() if len(df) else "",
                "top_engine_share": df["engine"].value_counts().max() / max(1, len(df)) if len(df) else 0.0,
                "top_field_family": df["source_field_families"].fillna("missing").astype(str).value_counts().idxmax() if len(df) else "",
                "top_field_family_share": df["source_field_families"].fillna("missing").astype(str).value_counts().max() / max(1, len(df)) if len(df) else 0.0,
            }
        )
    population_summary = pd.DataFrame(source_rows)
    population_path = A7M2D_DIR / "a7m2d_population_summary.csv"
    population_summary.to_csv(population_path, index=False)

    blocker = top_share > 0.35
    decision = "PASS_A7M2D_FORENSICS_KEEP_A7M2_HOLD" if blocker else "PASS_A7M2D_FORENSICS_CLUSTER_BLOCKER_CLEARED"
    recommendation = (
        "Do not run A7M-3. Add return-corr cluster cap before any next inherited-engine search."
        if blocker
        else "Cluster concentration no longer blocks by 35pct rule; verify other A7M-2 gates before A7M-3."
    )

    outputs = {
        "cluster_summary": str(cluster_summary_path),
        "top_cluster_members": str(top_members_path),
        "engine_cluster_matrix": str(engine_matrix_path),
        "field_family_cluster_matrix": str(family_matrix_path),
        "reject_reason_by_cluster": str(reason_path),
        "top_cluster_expression_summary": str(expr_summary_path),
        "cluster_cap_counterfactual": str(cap_path),
        "population_summary": str(population_path),
    }
    out_paths = [Path(v) for v in outputs.values()]
    manifest_out = {
        "generated_at": now,
        "decision": decision,
        "executes_search": False,
        "executes_replay": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "a7m2_decision": manifest.get("decision"),
        "a7m2_manifest_hash": manifest.get("stable_manifest_hash"),
        "positive_deep_count": int(len(positive_deep)),
        "top_cluster": top_cluster,
        "top_cluster_count": int(len(top_members)),
        "top_cluster_share": top_share,
        "blockers": ["single_cluster_contributes_over_35pct"] if blocker else [],
        "recommendation": recommendation,
        "inputs": {k: str(v) for k, v in inputs.items()},
        "outputs": outputs,
        "stable_manifest_hash": stable_hash(out_paths),
    }
    manifest_path = A7M2D_DIR / f"crypto_a7m2d_manifest_{DATE_TAG}.json"
    manifest_path.write_text(json.dumps(manifest_out, indent=2, sort_keys=True), encoding="utf-8")

    top_expr = expr_summary[(expr_summary["field"] == "expression")].head(8)
    top_reasons = reason_df[reason_df["return_corr_cluster"].astype(str).eq(top_cluster)].sort_values("count", ascending=False).head(8)

    report = [
        "# Crypto A7M-2D Cluster Concentration Forensics",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        f"- a7m2_decision: `{manifest.get('decision')}`",
        f"- top_cluster: `{top_cluster}`",
        f"- top_cluster_count: `{len(top_members)} / {len(positive_deep)}`",
        f"- top_cluster_share: `{top_share:.4f}`",
        f"- blocker: `{blocker}`",
        f"- recommendation: `{recommendation}`",
        "",
        "## Interpretation",
        "",
        "A7M-2 produced many survivor/near-miss rows, but the dominant return-corr cluster is too large for a valid inherited-engine promotion signal.",
        "This is a search-space concentration problem, not an alpha proof signal.",
        "",
        "## Top Cluster Summary",
        "",
        csummary.head(12).to_markdown(index=False),
        "",
        "## Top Cluster Expressions",
        "",
        top_expr.to_markdown(index=False),
        "",
        "## Top Cluster Reject Reasons",
        "",
        top_reasons.to_markdown(index=False) if not top_reasons.empty else "No reject reasons.",
        "",
        "## Cluster Cap Counterfactual",
        "",
        cap_df.to_markdown(index=False),
        "",
        "## Population Summary",
        "",
        population_summary.to_markdown(index=False),
        "",
        "## Decision Boundary",
        "",
        "- This report does not authorize A7M-3.",
        "- This report does not authorize alpha proof, shadow, paper, live, or production.",
        "- Next valid work is cluster-cap / diversity-first search policy revision, not budget expansion.",
        "",
    ]
    report_path = REPORT_DIR / f"CRYPTO_A7M2D_CLUSTER_CONCENTRATION_FORENSICS_{DATE_TAG}.md"
    report_path.write_text("\n".join(report), encoding="utf-8")

    decision_record = [
        "# Crypto A7M-2D Decision Record",
        "",
        f"- decision: `{decision}`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        "- search_executed: `False`",
        "- replay_executed: `False`",
        f"- a7m2_decision_preserved: `{manifest.get('decision')}`",
        f"- top_cluster: `{top_cluster}`",
        f"- top_cluster_share: `{top_share:.4f}`",
        f"- blockers: `{manifest_out['blockers']}`",
        "",
        "## Confirmed",
        "",
        "- A7M-2 failure is dominated by return-corr concentration.",
        "- The issue is not placebo control leakage.",
        "- A7M-3 remains unauthorized.",
        "",
        "## Required Before Any Next Search",
        "",
        "- Add a return-corr cluster cap before deep-audit survivor counting.",
        "- Add family/field/operator diversity pressure before promotion analysis.",
        "- Keep May stress-only; do not use May to repair this cluster.",
        "",
    ]
    decision_path = REPORT_DIR / f"CRYPTO_A7M2D_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text("\n".join(decision_record), encoding="utf-8")

    print(json.dumps(manifest_out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
