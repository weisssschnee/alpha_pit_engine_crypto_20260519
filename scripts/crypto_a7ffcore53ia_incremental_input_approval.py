from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CORE51PX = REPO / "runtime" / "a7ffcore51px_company_sharded_replay_runner_contract"
CORE53I = REPO / "runtime" / "a7ffcore53i_factor_input_information_audit"
COMPACT_FRAME = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore51px_company_sharded_replay_20260602/a7ffcore51px_compact_frame.parquet")
RUNTIME = REPO / "runtime" / "a7ffcore53ia_incremental_input_approval"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE53IA_INCREMENTAL_INPUT_APPROVAL_20260603.md"

KEY_OR_LABEL_PREFIXES = ("label_",)
BLOCKED_FIELDS = {"symbol", "timestamp", "execution_time", "split"}
SOURCE_FIELDS = {"source_market_funding", "source_metrics"}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def semantic_type(field: str) -> str:
    name = field.lower()
    if "basis" in name or "premium" in name:
        return "basis_premium_like"
    if "funding" in name:
        return "funding_like"
    if "open_interest" in name or "long_short" in name or "position" in name:
        return "positioning_like"
    if "taker" in name or "trade_count" in name or "volume" in name or "liquidity" in name or "coverage" in name or "gap" in name:
        return "liquidity_like"
    if "vol" in name:
        return "volatility_like"
    if "age" in name or "history_length" in name:
        return "state_or_taxonomy"
    if "close" in name or "open" in name or "high" in name or "low" in name or "return" in name or "price" in name or "mark_" in name or "index_" in name:
        return "price_like"
    return "generic_numeric"


def md5_stable_sample(df: pd.DataFrame, max_timestamps: int = 4096) -> pd.DataFrame:
    timestamps = pd.Series(sorted(df["timestamp"].dropna().unique()))
    if len(timestamps) <= max_timestamps:
        selected = set(timestamps)
    else:
        idx = np.linspace(0, len(timestamps) - 1, max_timestamps).round().astype(int)
        selected = set(timestamps.iloc[idx])
    return df.loc[df["timestamp"].isin(selected)].copy()


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE53I / "a7ffcore53i_manifest.json")
    if not source.get("authorizes_factor_input_repair"):
        raise SystemExit(f"CORE53IA not authorized by CORE53I: {source.get('decision')}")
    contract = pd.read_csv(CORE51PX / "a7ffcore51px_compact_frame_contract.csv")
    fields = contract["field_name"].dropna().astype(str).tolist()
    df = pd.read_parquet(COMPACT_FRAME, columns=[c for c in fields if c not in {"symbol"} and not c.startswith("label_")])
    sample = md5_stable_sample(df)
    numeric_cols = []
    for col in sample.columns:
        if col in BLOCKED_FIELDS or col in SOURCE_FIELDS or col.startswith(KEY_OR_LABEL_PREFIXES):
            continue
        converted = pd.to_numeric(sample[col], errors="coerce")
        if converted.notna().sum() > 0:
            sample[col] = converted.astype("float64")
            numeric_cols.append(col)

    stats_rows = []
    xs_std_rows = []
    grouped = sample[["timestamp", *numeric_cols]].groupby("timestamp", observed=True)
    for col in numeric_cols:
        series = sample[col]
        non_null = int(series.notna().sum())
        finite = np.isfinite(series.to_numpy(dtype="float64", na_value=np.nan))
        finite_count = int(finite.sum())
        unique_count = int(series.nunique(dropna=True))
        coverage = finite_count / max(1, len(series))
        xs_std = grouped[col].std().replace([np.inf, -np.inf], np.nan)
        median_xs_std = float(xs_std.median()) if xs_std.notna().any() else np.nan
        active_xs_share = float((xs_std > 1e-12).mean()) if len(xs_std) else 0.0
        stats_rows.append(
            {
                "field": col,
                "semantic_type": semantic_type(col),
                "source_panel": contract.loc[contract["field_name"].eq(col), "source_panel"].iloc[0],
                "coverage": coverage,
                "finite_count": finite_count,
                "non_null_count": non_null,
                "unique_count": unique_count,
                "unique_ratio": unique_count / max(1, finite_count),
                "median_xs_std": median_xs_std,
                "active_xs_share": active_xs_share,
            }
        )
        xs_std_rows.append({"field": col, "median_xs_std": median_xs_std, "active_xs_share": active_xs_share})
    stats = pd.DataFrame(stats_rows)

    matrix = sample[numeric_cols].replace([np.inf, -np.inf], np.nan)
    matrix = matrix.loc[:, matrix.notna().sum(axis=0) > 1000]
    corr = matrix.corr(method="pearson", min_periods=1000).fillna(0.0)
    pairs = []
    for i, left in enumerate(corr.columns):
        for right in corr.columns[i + 1 :]:
            value = float(corr.loc[left, right])
            if abs(value) >= 0.95:
                pairs.append(
                    {
                        "field_left": left,
                        "field_right": right,
                        "abs_corr": abs(value),
                        "corr": value,
                        "semantic_left": semantic_type(left),
                        "semantic_right": semantic_type(right),
                    }
                )
    pair_df = pd.DataFrame(pairs).sort_values("abs_corr", ascending=False) if pairs else pd.DataFrame()

    parent = {col: col for col in corr.columns}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for _, row in pair_df.iterrows():
        union(str(row["field_left"]), str(row["field_right"]))
    clusters = {}
    for col in corr.columns:
        clusters.setdefault(find(col), []).append(col)
    cluster_rows = []
    for idx, members in enumerate(sorted(clusters.values(), key=lambda xs: (-len(xs), xs[0]))):
        types = sorted({semantic_type(x) for x in members})
        cluster_rows.append(
            {
                "info_cluster_id": f"ic_{idx:03d}",
                "field_count": len(members),
                "fields": "|".join(sorted(members)),
                "semantic_types": "|".join(types),
                "dominant_semantic_type": types[0] if len(types) == 1 else "mixed",
            }
        )
    cluster_df = pd.DataFrame(cluster_rows)
    field_to_cluster = {}
    for _, row in cluster_df.iterrows():
        for field in str(row["fields"]).split("|"):
            field_to_cluster[field] = row["info_cluster_id"]

    stats["info_cluster_id"] = stats["field"].map(field_to_cluster).fillna("non_numeric_or_uncorrelated")
    stats["cluster_size"] = stats["info_cluster_id"].map(cluster_df.set_index("info_cluster_id")["field_count"]).fillna(1).astype(int)
    decisions = []
    for _, row in stats.iterrows():
        reasons = []
        decision = "approved_incremental_signal_input"
        if row["coverage"] < 0.70:
            decision = "blocked_low_coverage"
            reasons.append("coverage_below_70pct")
        if row["unique_count"] <= 3:
            decision = "blocked_low_information"
            reasons.append("unique_count_le_3")
        if not np.isfinite(row["median_xs_std"]) or row["median_xs_std"] <= 1e-12 or row["active_xs_share"] < 0.50:
            decision = "blocked_low_cross_sectional_variation"
            reasons.append("low_cross_sectional_variation")
        if row["semantic_type"] == "state_or_taxonomy":
            decision = "approved_condition_or_neutralizer_only"
            reasons.append("state_taxonomy_not_standalone_alpha")
        if row["cluster_size"] > 1 and decision == "approved_incremental_signal_input":
            decision = "approved_redundant_cluster_member_requires_cap"
            reasons.append("high_corr_cluster_member")
        decisions.append((decision, ";".join(reasons) if reasons else "incremental_enough"))
    stats["input_approval"] = [x[0] for x in decisions]
    stats["approval_reason"] = [x[1] for x in decisions]

    cluster_summary = (
        stats.groupby("info_cluster_id", as_index=False)
        .agg(
            field_count=("field", "count"),
            semantic_types=("semantic_type", lambda s: "|".join(sorted(set(s)))),
            approved_signal_count=("input_approval", lambda s: int(s.astype(str).str.startswith("approved_incremental").sum())),
            condition_only_count=("input_approval", lambda s: int((s == "approved_condition_or_neutralizer_only").sum())),
            blocked_count=("input_approval", lambda s: int(s.astype(str).str.startswith("blocked").sum())),
            fields=("field", lambda s: "|".join(sorted(s))),
        )
        .sort_values(["field_count", "approved_signal_count"], ascending=False)
    )
    approval_summary = (
        stats.groupby(["semantic_type", "input_approval"], as_index=False)
        .agg(field_count=("field", "count"))
        .sort_values(["semantic_type", "field_count"], ascending=[True, False])
    )
    approved_count = int(stats["input_approval"].isin(["approved_incremental_signal_input", "approved_redundant_cluster_member_requires_cap"]).sum())
    condition_only_count = int(stats["input_approval"].eq("approved_condition_or_neutralizer_only").sum())
    blocked_count = int(stats["input_approval"].astype(str).str.startswith("blocked").sum())
    large_cluster_count = int((cluster_summary["field_count"] > 1).sum())
    decision = "PASS_A7FFCORE53IA_INCREMENTAL_INPUT_APPROVAL_BUILT"
    manifest = {
        "stage": "A7FF-CORE53IA",
        "generated_at": now_utc(),
        "source_stage": source.get("stage"),
        "source_decision": source.get("decision"),
        "decision": decision,
        "sample_rows": int(sample.shape[0]),
        "sample_timestamps": int(sample["timestamp"].nunique()),
        "numeric_field_count": int(stats.shape[0]),
        "approved_signal_input_count": approved_count,
        "condition_only_input_count": condition_only_count,
        "blocked_input_count": blocked_count,
        "high_corr_pair_count_abs_ge_0_95": int(pair_df.shape[0]),
        "large_info_cluster_count": large_cluster_count,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core54_queue_builder": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    authorization = {
        "authorized": {
            "A7FF-CORE54 queue builder using input approval ledger": True,
        },
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    stats.to_csv(RUNTIME / "a7ffcore53ia_field_input_approval_ledger.csv", index=False)
    pair_df.to_csv(RUNTIME / "a7ffcore53ia_high_corr_field_pairs.csv", index=False)
    cluster_df.to_csv(RUNTIME / "a7ffcore53ia_information_clusters.csv", index=False)
    cluster_summary.to_csv(RUNTIME / "a7ffcore53ia_cluster_approval_summary.csv", index=False)
    approval_summary.to_csv(RUNTIME / "a7ffcore53ia_semantic_approval_summary.csv", index=False)
    write_json(RUNTIME / "a7ffcore53ia_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore53ia_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE53IA INCREMENTAL INPUT APPROVAL",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE53IA approves or blocks field inputs before queue construction. It audits incremental information directly at the field/factor-input layer; it does not execute replay, generation, search, proof, or promotion.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Approval Summary",
        "",
        md_table(approval_summary, 80),
        "",
        "## Field Approval Ledger",
        "",
        md_table(stats[["field", "semantic_type", "info_cluster_id", "cluster_size", "coverage", "unique_count", "median_xs_std", "active_xs_share", "input_approval", "approval_reason"]], 80),
        "",
        "## Information Clusters",
        "",
        md_table(cluster_summary, 80),
        "",
        "## High Correlation Field Pairs",
        "",
        md_table(pair_df, 80),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
