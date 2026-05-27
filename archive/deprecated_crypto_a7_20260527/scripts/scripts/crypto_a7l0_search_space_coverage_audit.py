from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, stable_hash


A7L0_DIR = RUNTIME_DIR / "a7l0_search_space_coverage_audit"
DATE_TAG = "20260520"

INPUTS = {
    "A7I1B_original_generator": {
        "scoreboard": RUNTIME_DIR / "a7i1b_matched_budget_smoke" / "a7i1_candidate_scoreboard.csv",
        "selected": RUNTIME_DIR / "a7i1b_matched_budget_smoke" / "a7i1_rejected_candidate_reasons.csv",
        "manifest": RUNTIME_DIR / "a7i1b_matched_budget_smoke" / "a7i1_manifest_20260519.json",
    },
    "A7J2_reranked_original_pool": {
        "scoreboard": RUNTIME_DIR / "a7j2_same_budget_redesigned_smoke" / "a7j2_candidate_scoreboard.csv",
        "selected": RUNTIME_DIR / "a7j2_same_budget_redesigned_smoke" / "a7j2_selected_candidates.csv",
        "manifest": RUNTIME_DIR / "a7j2_same_budget_redesigned_smoke" / "crypto_a7j2_manifest_20260520.json",
    },
    "A7K2_new_space": {
        "scoreboard": RUNTIME_DIR / "a7k2_new_space_same_budget_smoke" / "a7k2_candidate_scoreboard.csv",
        "selected": RUNTIME_DIR / "a7k2_new_space_same_budget_smoke" / "a7k2_selected_candidates.csv",
        "manifest": RUNTIME_DIR / "a7k2_new_space_same_budget_smoke" / "crypto_a7k2_manifest_20260520.json",
    },
}

FIELD_FAMILY = {
    "ret_1": "price",
    "ret_3": "price",
    "ret_6": "price",
    "ret_12": "price",
    "ret_24": "price",
    "log_ret_1": "price",
    "fwd_ret_1": "future_label",
    "fwd_ret_3": "future_label",
    "fwd_ret_6": "future_label",
    "fwd_ret_12": "future_label",
    "fwd_ret_24": "future_label",
    "hl_range": "volatility",
    "abs_ret_1": "volatility",
    "realized_vol_6": "volatility",
    "realized_vol_12": "volatility",
    "realized_vol_24": "volatility",
    "volume": "liquidity",
    "quote_asset_volume": "liquidity",
    "number_of_trades": "liquidity",
    "avg_trade_size_quote": "liquidity",
    "quote_volume_mean_6": "liquidity",
    "quote_volume_mean_12": "liquidity",
    "quote_volume_mean_24": "liquidity",
    "taker_buy_ratio": "flow",
    "taker_imbalance": "flow",
    "taker_buy_base_asset_volume": "flow",
    "taker_buy_quote_asset_volume": "flow",
    "mark_index_ratio": "basis",
    "mark_minus_index": "basis",
    "premium_index": "basis",
    "spot_perp_basis": "basis",
    "cs_z_mark_index_ratio": "basis",
    "cs_z_premium_index": "basis",
    "latest_known_funding_rate": "funding",
    "funding_rate_z_24": "funding",
    "funding_rate_persistence_3": "funding",
    "cs_z_latest_known_funding_rate": "funding",
}

OPERATOR_PATTERNS = {
    "Rank": r"Rank\(",
    "ZScore": r"ZScore\(",
    "Mul": r"Mul\(",
    "RandomNoise": r"RandomNoise|seeded_random",
    "row_shuffle": r"row_shuffle",
    "time_shuffle": r"time_shuffle",
    "sign_flip": r"sign_flip",
    "wrong_lag": r"wrong_lag",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if pd.notna(out) else default


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def field_tokens(expr: str) -> list[str]:
    out = []
    for field in FIELD_FAMILY:
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(field)}(?![A-Za-z0-9_])", str(expr)):
            out.append(field)
    return sorted(out)


def formula_depth(expr: str) -> int:
    depth = 0
    max_depth = 0
    for ch in str(expr):
        if ch == "(":
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == ")":
            depth = max(0, depth - 1)
    return max_depth


def operators(expr: str, signal_mode: str = "") -> list[str]:
    text = f"{expr} {signal_mode}"
    return sorted([op for op, pattern in OPERATOR_PATTERNS.items() if re.search(pattern, text)])


def candidate_enrich(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    out = df.copy()
    out["source_run"] = source_name
    if "source_fields" not in out.columns:
        out["source_fields"] = out["expression"].map(lambda x: ";".join(field_tokens(str(x))))
    out["field_list"] = out.apply(
        lambda r: [f for f in str(r.get("source_fields", "")).split(";") if f] or field_tokens(str(r.get("expression", ""))),
        axis=1,
    )
    out["field_family_list"] = out["field_list"].map(lambda xs: sorted({FIELD_FAMILY.get(x, "unknown") for x in xs}))
    out["field_family_combo"] = out["field_family_list"].map(lambda xs: ";".join(xs))
    out["operator_list"] = out.apply(lambda r: operators(str(r.get("expression", "")), str(r.get("signal_mode", ""))), axis=1)
    out["operator_combo"] = out["operator_list"].map(lambda xs: ";".join(xs))
    out["formula_depth"] = out["expression"].map(formula_depth)
    if "horizon" not in out.columns:
        out["horizon"] = None
    if "expr_hash" not in out.columns:
        out["expr_hash"] = out["expression"].map(lambda x: stable_hash({"expr": str(x)})[:16])
    if "a7k_preselection_pass" not in out.columns:
        pre = compute_a7k_style_preselection(out)
        out["a7k_preselection_pass"] = pre["pass"]
        out["a7k_preselection_available"] = pre["available"]
    else:
        out["a7k_preselection_available"] = True
    if "selected_for_replay" not in out.columns:
        if "a7j_selected_for_replay" in out.columns:
            out["selected_for_replay"] = out["a7j_selected_for_replay"]
        else:
            out["selected_for_replay"] = False
    return out


def compute_a7k_style_preselection(df: pd.DataFrame) -> dict[str, pd.Series]:
    required = [
        "raw_10bp__validation_2025H1__n",
        "raw_10bp__recent_oos_2025H2_2026Apr__n",
        "raw_10bp__validation_2025H1__mean_gross_exposure",
        "raw_10bp__recent_oos_2025H2_2026Apr__mean_gross_exposure",
        "raw_10bp__validation_2025H1__annualized_mean",
        "raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
        "raw_20bp__validation_2025H1__annualized_mean",
        "raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean",
        "execution_lag_1bar_raw_10bp__validation_2025H1__annualized_mean",
        "execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
        "residual_vs_funding_10bp__validation_2025H1__annualized_mean",
        "residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
        "residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
        "funding_beta_recent",
        "core4_beta_recent",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        return {
            "available": pd.Series(False, index=df.index),
            "pass": pd.Series(False, index=df.index),
        }

    out = (
        df["raw_10bp__validation_2025H1__n"].map(lambda x: safe_float(x, -999) >= 250)
        & df["raw_10bp__recent_oos_2025H2_2026Apr__n"].map(lambda x: safe_float(x, -999) >= 250)
        & df["raw_10bp__validation_2025H1__mean_gross_exposure"].map(lambda x: safe_float(x, -999) >= 0.10)
        & df["raw_10bp__recent_oos_2025H2_2026Apr__mean_gross_exposure"].map(lambda x: safe_float(x, -999) >= 0.10)
        & df["raw_10bp__validation_2025H1__annualized_mean"].map(lambda x: safe_float(x, -999) > 0)
        & df["raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean"].map(lambda x: safe_float(x, -999) > 0)
        & df["raw_20bp__validation_2025H1__annualized_mean"].map(lambda x: safe_float(x, -999) >= 0)
        & df["raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean"].map(lambda x: safe_float(x, -999) >= 0)
        & df["execution_lag_1bar_raw_10bp__validation_2025H1__annualized_mean"].map(lambda x: safe_float(x, -999) >= 0)
        & df["execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean"].map(lambda x: safe_float(x, -999) >= 0)
        & df["residual_vs_funding_10bp__validation_2025H1__annualized_mean"].map(lambda x: safe_float(x, -999) > 0)
        & df["residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean"].map(lambda x: safe_float(x, -999) > 0)
        & df["residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean"].map(lambda x: safe_float(x, -999) > 0)
        & df["funding_beta_recent"].map(lambda x: abs(safe_float(x, 999)) < 0.50)
        & df["core4_beta_recent"].map(lambda x: abs(safe_float(x, 999)) < 0.50)
    )
    return {
        "available": pd.Series(True, index=df.index),
        "pass": out,
    }


def coverage_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for source, part in df.groupby("source_run"):
        generated = len(part)
        unique_expr = part["expr_hash"].nunique()
        selected = int(part["selected_for_replay"].astype(str).str.lower().isin(["true", "1"]).sum())
        if "a7k_preselection_available" in part.columns and not bool(part["a7k_preselection_available"].any()):
            preselection = None
            preselection_rate = None
        else:
            preselection = int(part["a7k_preselection_pass"].astype(str).str.lower().isin(["true", "1"]).sum())
            preselection_rate = preselection / max(1, generated)
        rows.append(
            {
                "source_run": source,
                "generated": generated,
                "unique_expr_hash": unique_expr,
                "unique_expr_ratio": unique_expr / max(1, generated),
                "arm_count": part["arm"].nunique() if "arm" in part.columns else None,
                "family_count": part["family"].nunique() if "family" in part.columns else None,
                "field_family_combo_count": part["field_family_combo"].nunique(),
                "operator_combo_count": part["operator_combo"].nunique(),
                "horizon_count": part["horizon"].nunique(),
                "preselection_pass_count": preselection,
                "preselection_pass_rate": preselection_rate,
                "selected_count": selected,
                "selected_rate": selected / max(1, generated),
                "top_family_share": part["family"].value_counts(normalize=True).max() if "family" in part.columns else None,
                "top_field_family_combo_share": part["field_family_combo"].value_counts(normalize=True).max(),
                "top_operator_combo_share": part["operator_combo"].value_counts(normalize=True).max(),
                "max_formula_depth": int(part["formula_depth"].max()),
                "median_formula_depth": float(part["formula_depth"].median()),
            }
        )
    return pd.DataFrame(rows)


def distribution_table(df: pd.DataFrame, column: str) -> pd.DataFrame:
    rows = []
    for source, part in df.groupby("source_run"):
        total = len(part)
        for value, count in part[column].fillna("NA").astype(str).value_counts().items():
            rows.append({"source_run": source, "dimension": column, "value": value, "count": int(count), "share": count / max(1, total)})
    return pd.DataFrame(rows)


def gate_attrition(scoreboards: dict[str, pd.DataFrame], manifests: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for source, df in scoreboards.items():
        generated = len(df)
        selected = int(df.get("selected_for_replay", pd.Series(False, index=df.index)).astype(str).str.lower().isin(["true", "1"]).sum())
        if "a7k_preselection_available" in df.columns and not bool(df["a7k_preselection_available"].any()):
            preselection = None
            preselection_rate = None
        else:
            preselection = int(df.get("a7k_preselection_pass", pd.Series(False, index=df.index)).astype(str).str.lower().isin(["true", "1"]).sum())
            preselection_rate = preselection / max(1, generated)
        manifest = manifests.get(source, {})
        research = int(manifest.get("research_candidate_count", 0))
        placebo = int(manifest.get("placebo_research_candidate_count", 0))
        non_flow = int(manifest.get("non_flow_research_candidate_count", 0))
        rows += [
            {"source_run": source, "stage": "generated", "count": generated, "rate_vs_generated": 1.0},
            {"source_run": source, "stage": "non_may_preselection_pass", "count": preselection, "rate_vs_generated": preselection_rate},
            {"source_run": source, "stage": "selected", "count": selected, "rate_vs_generated": selected / max(1, generated)},
            {"source_run": source, "stage": "research_candidate", "count": research, "rate_vs_generated": research / max(1, generated)},
            {"source_run": source, "stage": "placebo_research_candidate", "count": placebo, "rate_vs_generated": placebo / max(1, generated)},
            {"source_run": source, "stage": "non_flow_research_candidate", "count": non_flow, "rate_vs_generated": non_flow / max(1, generated)},
        ]
    return pd.DataFrame(rows)


def rejection_summary(selected_paths: dict[str, Path]) -> pd.DataFrame:
    rows = []
    for source, path in selected_paths.items():
        if not path.exists():
            continue
        df = pd.read_csv(path)
        reason_col = "reject_reasons"
        if reason_col not in df.columns:
            continue
        total = len(df)
        counts: Counter[str] = Counter()
        for reasons in df[reason_col].fillna(""):
            for reason in str(reasons).split(";"):
                if reason:
                    counts[reason] += 1
        for reason, count in counts.most_common():
            rows.append({"source_run": source, "reason": reason, "count": int(count), "share_of_selected": count / max(1, total)})
    return pd.DataFrame(rows)


def near_miss_audit(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for source, part in df.groupby("source_run"):
        cols = [
            "raw_10bp__validation_2025H1__annualized_mean",
            "raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
            "raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean",
            "execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
            "residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
            "residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
        ]
        present = [c for c in cols if c in part.columns]
        if not present:
            continue
        work = part.copy()
        for col in present:
            work[f"pass_{col}"] = work[col].map(lambda x: safe_float(x, -999) > 0)
        pass_cols = [f"pass_{c}" for c in present]
        work["near_miss_gate_pass_count"] = work[pass_cols].sum(axis=1)
        top = work.sort_values(["near_miss_gate_pass_count", "candidate_id"], ascending=[False, True]).head(20)
        for _, row in top.iterrows():
            rows.append(
                {
                    "source_run": source,
                    "candidate_id": row.get("candidate_id"),
                    "arm": row.get("arm"),
                    "family": row.get("family"),
                    "expression": row.get("expression"),
                    "near_miss_gate_pass_count": int(row["near_miss_gate_pass_count"]),
                    "gate_count": len(pass_cols),
                    "raw_recent": safe_float(row.get("raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean"), None),
                    "cost20_recent": safe_float(row.get("raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean"), None),
                    "lag1_recent": safe_float(row.get("execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean"), None),
                    "residual_funding_recent": safe_float(row.get("residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean"), None),
                    "residual_core4_recent": safe_float(row.get("residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean"), None),
                }
            )
    return pd.DataFrame(rows)


def main() -> int:
    A7L0_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    enriched = []
    scoreboards: dict[str, pd.DataFrame] = {}
    manifests: dict[str, dict[str, Any]] = {}
    selected_paths: dict[str, Path] = {}
    for name, paths in INPUTS.items():
        df = pd.read_csv(paths["scoreboard"])
        enriched_df = candidate_enrich(df, name)
        enriched.append(enriched_df)
        scoreboards[name] = enriched_df
        manifests[name] = load_manifest(paths["manifest"])
        selected_paths[name] = paths["selected"]
    all_df = pd.concat(enriched, ignore_index=True)

    coverage = coverage_summary(all_df)
    dims = pd.concat(
        [
            distribution_table(all_df, "family"),
            distribution_table(all_df, "field_family_combo"),
            distribution_table(all_df, "operator_combo"),
            distribution_table(all_df, "horizon"),
        ],
        ignore_index=True,
    )
    attrition = gate_attrition(scoreboards, manifests)
    rejects = rejection_summary(selected_paths)
    near_miss = near_miss_audit(all_df)

    coverage_path = A7L0_DIR / "a7l0_search_space_coverage_summary.csv"
    dims_path = A7L0_DIR / "a7l0_distribution_by_dimension.csv"
    attrition_path = A7L0_DIR / "a7l0_gate_attrition.csv"
    rejects_path = A7L0_DIR / "a7l0_rejection_reason_summary.csv"
    near_miss_path = A7L0_DIR / "a7l0_near_miss_audit.csv"
    all_path = A7L0_DIR / "a7l0_unified_candidate_coverage_table.csv"
    coverage.to_csv(coverage_path, index=False)
    dims.to_csv(dims_path, index=False)
    attrition.to_csv(attrition_path, index=False)
    rejects.to_csv(rejects_path, index=False)
    near_miss.to_csv(near_miss_path, index=False)
    all_df.to_csv(all_path, index=False)

    # Budget ladder authorization is intentionally conservative.
    blockers = []
    a7k = coverage[coverage["source_run"] == "A7K2_new_space"].iloc[0]
    if a7k["preselection_pass_rate"] < 0.10:
        blockers.append("a7k_preselection_pass_rate_below_10pct")
    if int(manifests["A7K2_new_space"].get("research_candidate_count", 0)) == 0:
        blockers.append("a7k_zero_research_candidates")
    if "A7K2_new_space" in rejects["source_run"].unique():
        k_rejects = rejects[rejects["source_run"] == "A7K2_new_space"]
        may_share = float(k_rejects[k_rejects["reason"].str.contains("may_", na=False)]["share_of_selected"].max() or 0)
        if may_share >= 0.75:
            blockers.append("a7k_selected_candidates_may_failure_too_homogeneous")
    if a7k["field_family_combo_count"] < 8:
        blockers.append("a7k_field_family_combo_coverage_too_narrow")

    decision = "HOLD_A7L0_BUDGET_LADDER_NOT_AUTHORIZED" if blockers else "PASS_A7L0_AUTHORIZE_BUDGET_LADDER_LEVEL1"

    manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_budget_ladder_level1": decision == "PASS_A7L0_AUTHORIZE_BUDGET_LADDER_LEVEL1",
        "authorizes_alpha_proof": False,
        "inputs": {name: {k: str(v) for k, v in paths.items()} for name, paths in INPUTS.items()},
        "blockers": blockers,
        "outputs": {
            "coverage_summary": str(coverage_path),
            "distribution_by_dimension": str(dims_path),
            "gate_attrition": str(attrition_path),
            "rejection_reason_summary": str(rejects_path),
            "near_miss_audit": str(near_miss_path),
            "unified_candidate_coverage_table": str(all_path),
        },
    }
    manifest_path = A7L0_DIR / f"crypto_a7l0_manifest_{DATE_TAG}.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / f"CRYPTO_A7L0_SEARCH_SPACE_COVERAGE_AUDIT_{DATE_TAG}.md"
    lines = [
        "# Crypto A7L-0 Search-Space Coverage Audit",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- evidence_level: `coverage_audit_not_alpha_proof`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        f"- authorizes_budget_ladder_level1: `{manifest['authorizes_budget_ladder_level1']}`",
        "- authorizes_alpha_proof: `False`",
        f"- blockers: `{blockers}`",
        "",
        "## Coverage Summary",
        "",
        "| source | generated | unique expr ratio | field combos | op combos | horizons | preselect pass | research |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in coverage.iterrows():
        research = int(manifests[row["source_run"]].get("research_candidate_count", 0))
        preselect_rate = "NA" if pd.isna(row["preselection_pass_rate"]) else f"{float(row['preselection_pass_rate']):.3f}"
        lines.append(
            f"| `{row['source_run']}` | {int(row['generated'])} | {float(row['unique_expr_ratio']):.3f} | "
            f"{int(row['field_family_combo_count'])} | {int(row['operator_combo_count'])} | {int(row['horizon_count'])} | "
            f"{preselect_rate} | {research} |"
        )
    lines += [
        "",
        "## Gate Attrition",
        "",
        "| source | stage | count | rate vs generated |",
        "|---|---|---:|---:|",
    ]
    for _, row in attrition.iterrows():
        count = "NA" if pd.isna(row["count"]) else str(int(row["count"]))
        rate = "NA" if pd.isna(row["rate_vs_generated"]) else f"{float(row['rate_vs_generated']):.4f}"
        lines.append(f"| `{row['source_run']}` | `{row['stage']}` | {count} | {rate} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- A7K is a narrow negative result, not a falsification of broader crypto formula search.",
        "- A7L-0 checks whether the observed search distributions justify a budget ladder.",
        "- If budget ladder is not authorized, the next valid work is search-space redesign or data/feature-layer rethink, not blind larger search.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7L0_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7L-0 Decision Record",
                "",
                f"- decision: `{decision}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                "- search_executed: `False`",
                "- replay_executed: `False`",
                f"- authorizes_budget_ladder_level1: `{manifest['authorizes_budget_ladder_level1']}`",
                f"- blockers: `{blockers}`",
                "",
                "A7L-0 measures coverage and attrition across A7I/A7J/A7K. It does not generate or promote candidates.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print("A7L0_REPORT=" + str(report_path))
    print("A7L0_DECISION_RECORD=" + str(decision_path))
    print("A7L0_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
