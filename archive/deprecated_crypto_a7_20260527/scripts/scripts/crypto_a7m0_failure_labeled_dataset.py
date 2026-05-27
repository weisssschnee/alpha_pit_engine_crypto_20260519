from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, stable_hash


DATE_TAG = "20260520"
A7M0_DIR = RUNTIME_DIR / "a7m0_failure_labeled_search_dataset"

SOURCES = {
    "A7I1B_original_generator": {
        "scoreboard": RUNTIME_DIR / "a7i1b_matched_budget_smoke" / "a7i1_candidate_scoreboard.csv",
        "selected_or_rejected": RUNTIME_DIR / "a7i1b_matched_budget_smoke" / "a7i1_rejected_candidate_reasons.csv",
        "research_shortlist": RUNTIME_DIR / "a7i1b_matched_budget_smoke" / "a7i1_research_candidate_shortlist.csv",
        "stage": "small_matched_budget_smoke",
    },
    "A7J2_reranked_original_pool": {
        "scoreboard": RUNTIME_DIR / "a7j2_same_budget_redesigned_smoke" / "a7j2_candidate_scoreboard.csv",
        "selected_or_rejected": RUNTIME_DIR / "a7j2_same_budget_redesigned_smoke" / "a7j2_rejected_candidate_reasons.csv",
        "research_shortlist": RUNTIME_DIR / "a7j2_same_budget_redesigned_smoke" / "a7j2_research_candidate_shortlist.csv",
        "selected": RUNTIME_DIR / "a7j2_same_budget_redesigned_smoke" / "a7j2_selected_candidates.csv",
        "stage": "same_pool_reward_rerank",
    },
    "A7K2_new_space": {
        "scoreboard": RUNTIME_DIR / "a7k2_new_space_same_budget_smoke" / "a7k2_candidate_scoreboard.csv",
        "selected_or_rejected": RUNTIME_DIR / "a7k2_new_space_same_budget_smoke" / "a7k2_rejected_candidate_reasons.csv",
        "research_shortlist": RUNTIME_DIR / "a7k2_new_space_same_budget_smoke" / "a7k2_research_candidate_shortlist.csv",
        "selected": RUNTIME_DIR / "a7k2_new_space_same_budget_smoke" / "a7k2_selected_candidates.csv",
        "stage": "new_space_same_budget_smoke",
    },
    "A7L1B_dry_preflight": {
        "scoreboard": RUNTIME_DIR / "a7l1b_implementation_preflight" / "a7l1b_dry_candidate_manifest.csv",
        "stage": "implementation_preflight_static_only",
    },
}

FIELD_FAMILY = {
    "ret_1": "price",
    "ret_3": "price",
    "ret_6": "price",
    "ret_12": "price",
    "ret_24": "price",
    "cs_z_ret_6": "cross_symbol",
    "cs_z_ret_12": "cross_symbol",
    "cs_z_ret_24": "cross_symbol",
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
    "cs_z_taker_imbalance": "cross_symbol",
    "mark_index_ratio": "basis",
    "mark_minus_index": "basis",
    "premium_index": "basis",
    "spot_perp_basis": "basis",
    "cs_z_mark_index_ratio": "cross_symbol",
    "cs_z_premium_index": "cross_symbol",
    "latest_known_funding_rate": "funding",
    "funding_rate_z_24": "funding",
    "funding_rate_persistence_3": "funding",
    "cs_z_latest_known_funding_rate": "cross_symbol",
}

OPERATORS = [
    "Rank",
    "ZScore",
    "Mul",
    "PLACEBO",
    "RandomNoise",
    "row_shuffle",
    "time_shuffle",
    "symbol_shuffle",
    "sign_flip",
    "wrong_lag",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def safe_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(out):
        return None
    return out


def boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def get(row: pd.Series, *cols: str) -> Any:
    for col in cols:
        if col in row.index and pd.notna(row[col]):
            return row[col]
    return None


def field_tokens(expr: str, source_fields: str | None = None) -> list[str]:
    out: list[str] = []
    if source_fields:
        out.extend([x for x in str(source_fields).split(";") if x and x != "nan"])
    for field in FIELD_FAMILY:
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(field)}(?![A-Za-z0-9_])", str(expr)):
            out.append(field)
    return sorted(set(out))


def operator_tokens(expr: str, signal_mode: str | None = None) -> list[str]:
    text = f"{expr} {signal_mode or ''}"
    out = []
    for op in OPERATORS:
        if op == "PLACEBO":
            if "PLACEBO(" in text:
                out.append(op)
        elif re.search(rf"\b{re.escape(op)}\b|\b{re.escape(op)}\(", text):
            out.append(op)
    return sorted(set(out))


def formula_depth(expr: str) -> int:
    depth = 0
    max_depth = 0
    for ch in str(expr):
        if ch == "(":
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == ")":
            depth = max(depth - 1, 0)
    return max_depth


def load_source(source_name: str, spec: dict[str, Any]) -> pd.DataFrame:
    scoreboard_path = Path(spec["scoreboard"])
    if not scoreboard_path.exists():
        return pd.DataFrame()
    df = pd.read_csv(scoreboard_path)
    df["source_run"] = source_name
    df["source_stage"] = spec["stage"]

    for extra_key in ["selected_or_rejected", "selected", "research_shortlist"]:
        path = spec.get(extra_key)
        if not path or not Path(path).exists():
            continue
        extra = pd.read_csv(path)
        cols = [
            c
            for c in extra.columns
            if c in {"candidate_id", "candidate_decision", "reject_reasons", "selected_for_replay", "a7k_preselection_pass", "a7j_selected_for_replay"}
            or c.startswith("raw_")
            or c.startswith("residual_")
            or c.startswith("execution_lag_")
            or c in {"funding_beta_recent", "core4_beta_recent"}
        ]
        extra = extra[cols].drop_duplicates("candidate_id")
        suffix = f"_{extra_key}"
        df = df.merge(extra, on="candidate_id", how="left", suffixes=("", suffix))
        for base in ["candidate_decision", "reject_reasons", "selected_for_replay", "a7k_preselection_pass"]:
            alt = f"{base}{suffix}"
            if alt in df.columns:
                if base in df.columns:
                    df[base] = df[base].where(df[base].notna(), df[alt])
                else:
                    df[base] = df[alt]
        if extra_key == "research_shortlist" and "candidate_id" in extra.columns:
            df["in_research_shortlist"] = df["candidate_id"].isin(set(extra["candidate_id"].astype(str)))
    return df


def derive_row(row: pd.Series) -> dict[str, Any]:
    expr = str(get(row, "expression") or "")
    source_fields = get(row, "source_fields", "field_list")
    fields = field_tokens(expr, str(source_fields) if source_fields is not None else None)
    families = sorted({FIELD_FAMILY.get(f, "unknown") for f in fields}) or [str(get(row, "field_family_combo") or "unknown")]
    ops = operator_tokens(expr, str(get(row, "signal_mode") or ""))
    reject_reasons = str(get(row, "reject_reasons") or "")
    candidate_decision = str(get(row, "candidate_decision") or "")

    raw_val = safe_float(get(row, "raw_10bp__validation_2025H1__annualized_mean", "component_raw_validation"))
    raw_recent = safe_float(get(row, "raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean", "component_raw_recent"))
    cost20_val = safe_float(get(row, "raw_20bp__validation_2025H1__annualized_mean", "component_cost20_validation"))
    cost20_recent = safe_float(get(row, "raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean", "component_cost20_recent"))
    lag_val = safe_float(get(row, "execution_lag_1bar_raw_10bp__validation_2025H1__annualized_mean", "component_lag1_validation"))
    lag_recent = safe_float(get(row, "execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean", "component_execution_lag_recent", "component_lag1_recent"))
    res_fund_val = safe_float(get(row, "residual_vs_funding_10bp__validation_2025H1__annualized_mean", "component_residual_funding_validation"))
    res_fund_recent = safe_float(get(row, "residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean", "component_residual_funding_recent"))
    res_core_recent = safe_float(get(row, "residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean", "component_residual_core4_recent"))
    raw_may = safe_float(get(row, "raw_10bp__fresh_forward_2026May__annualized_mean"))
    res_fund_may = safe_float(get(row, "residual_vs_funding_10bp__fresh_forward_2026May__annualized_mean"))

    n_val = safe_float(get(row, "raw_10bp__validation_2025H1__n"))
    n_recent = safe_float(get(row, "raw_10bp__recent_oos_2025H2_2026Apr__n"))
    gross_val = safe_float(get(row, "raw_10bp__validation_2025H1__mean_gross_exposure"))
    gross_recent = safe_float(get(row, "raw_10bp__recent_oos_2025H2_2026Apr__mean_gross_exposure"))
    funding_beta = safe_float(get(row, "funding_beta_recent"))
    core4_beta = safe_float(get(row, "core4_beta_recent"))

    selected = boolish(get(row, "selected_for_replay", "a7j_selected_for_replay"))
    preselection_pass = boolish(get(row, "a7k_preselection_pass")) if get(row, "a7k_preselection_pass") is not None else None
    research_candidate = (
        "RESEARCH_CANDIDATE" in candidate_decision
        or candidate_decision.endswith("RESEARCH_CANDIDATE")
        or boolish(get(row, "in_research_shortlist"))
    )
    clue = "CLUE" in candidate_decision
    placebo_like = str(get(row, "object_type") or "").lower() == "placebo" or str(get(row, "family") or "").lower().find("placebo") >= 0

    labels = {
        "coverage_fail": (n_val is not None and n_val < 250) or (n_recent is not None and n_recent < 250),
        "activity_fail": (gross_val is not None and gross_val < 0.10) or (gross_recent is not None and gross_recent < 0.10),
        "raw_validation_fail": raw_val is not None and raw_val <= 0,
        "raw_recent_fail": raw_recent is not None and raw_recent <= 0,
        "residual_funding_validation_fail": res_fund_val is not None and res_fund_val <= 0,
        "residual_funding_recent_fail": res_fund_recent is not None and res_fund_recent <= 0,
        "residual_core4_recent_fail": res_core_recent is not None and res_core_recent <= 0,
        "cost20_validation_fail": cost20_val is not None and cost20_val < 0,
        "cost20_recent_fail": cost20_recent is not None and cost20_recent < 0,
        "lag1_validation_fail": lag_val is not None and lag_val < 0,
        "lag1_recent_fail": lag_recent is not None and lag_recent < 0,
        "funding_beta_fail": funding_beta is not None and abs(funding_beta) >= 0.50,
        "core4_beta_fail": core4_beta is not None and abs(core4_beta) >= 0.50,
    }
    may_labels = {
        "may_raw_severe_fail_stress_only": (raw_may is not None and raw_may < -0.50) or "raw_may_severely_negative" in reject_reasons,
        "may_residual_funding_negative_stress_only": (res_fund_may is not None and res_fund_may < 0) or "residual_funding_may_negative" in reject_reasons,
    }
    non_may_fail_count = sum(1 for v in labels.values() if v)
    near_miss = (not research_candidate) and selected and non_may_fail_count <= 1 and not placebo_like

    return {
        "source_run": get(row, "source_run"),
        "source_stage": get(row, "source_stage"),
        "candidate_id": get(row, "candidate_id"),
        "arm": get(row, "arm"),
        "family": get(row, "family"),
        "object_type": get(row, "object_type"),
        "signal_mode": get(row, "signal_mode"),
        "expression": expr,
        "expr_hash": get(row, "expr_hash") or stable_hash({"expr": expr})[:16],
        "horizon": get(row, "horizon"),
        "operator_signature": ";".join(ops),
        "field_signature": ";".join(fields),
        "field_family_signature": ";".join(families),
        "formula_depth": formula_depth(expr),
        "selected_for_replay": selected,
        "preselection_pass": preselection_pass,
        "candidate_decision": candidate_decision,
        "reject_reasons": reject_reasons,
        "research_candidate_label": research_candidate,
        "near_miss_label": near_miss,
        "clue_label": clue,
        "placebo_like": placebo_like,
        "policy_training_eligible": not placebo_like,
        "raw_validation": raw_val,
        "raw_recent": raw_recent,
        "residual_funding_validation": res_fund_val,
        "residual_funding_recent": res_fund_recent,
        "residual_core4_recent": res_core_recent,
        "cost20_validation": cost20_val,
        "cost20_recent": cost20_recent,
        "lag1_validation": lag_val,
        "lag1_recent": lag_recent,
        "n_validation": n_val,
        "n_recent": n_recent,
        "gross_exposure_validation": gross_val,
        "gross_exposure_recent": gross_recent,
        "funding_beta_recent": funding_beta,
        "core4_beta_recent": core4_beta,
        **labels,
        **may_labels,
        "may_policy_training_allowed": False,
        "non_may_fail_count": non_may_fail_count,
    }


def main() -> int:
    A7M0_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    frames = []
    source_counts: list[dict[str, Any]] = []
    for name, spec in SOURCES.items():
        df = load_source(name, spec)
        if df.empty:
            source_counts.append({"source_run": name, "rows": 0, "status": "missing_or_empty"})
            continue
        frames.append(df)
        source_counts.append({"source_run": name, "rows": len(df), "status": "loaded"})
    raw = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    rows = [derive_row(row) for _idx, row in raw.iterrows()]
    dataset = pd.DataFrame(rows)

    dataset_path = A7M0_DIR / "crypto_a7m0_failure_labeled_candidate_dataset.csv"
    dataset.to_csv(dataset_path, index=False, encoding="utf-8")

    label_cols = [
        "coverage_fail",
        "activity_fail",
        "raw_validation_fail",
        "raw_recent_fail",
        "residual_funding_validation_fail",
        "residual_funding_recent_fail",
        "residual_core4_recent_fail",
        "cost20_validation_fail",
        "cost20_recent_fail",
        "lag1_validation_fail",
        "lag1_recent_fail",
        "funding_beta_fail",
        "core4_beta_fail",
        "may_raw_severe_fail_stress_only",
        "may_residual_funding_negative_stress_only",
        "near_miss_label",
        "research_candidate_label",
        "clue_label",
        "placebo_like",
    ]
    label_summary_rows = []
    for label in label_cols:
        count = int(dataset[label].fillna(False).astype(bool).sum()) if label in dataset.columns else 0
        label_summary_rows.append(
            {
                "label": label,
                "count": count,
                "rate": round(count / len(dataset), 6) if len(dataset) else 0.0,
                "policy_training_allowed": not label.startswith("may_"),
            }
        )

    source_summary = []
    for source, part in dataset.groupby("source_run"):
        source_summary.append(
            {
                "source_run": source,
                "rows": len(part),
                "selected_for_replay": int(part["selected_for_replay"].fillna(False).astype(bool).sum()),
                "research_candidates": int(part["research_candidate_label"].fillna(False).astype(bool).sum()),
                "near_miss": int(part["near_miss_label"].fillna(False).astype(bool).sum()),
                "clue": int(part["clue_label"].fillna(False).astype(bool).sum()),
                "may_stress_fail": int(
                    (
                        part["may_raw_severe_fail_stress_only"].fillna(False).astype(bool)
                        | part["may_residual_funding_negative_stress_only"].fillna(False).astype(bool)
                    ).sum()
                ),
                "policy_training_eligible": int(part["policy_training_eligible"].fillna(False).astype(bool).sum()),
            }
        )

    family_summary = []
    for family, part in dataset.groupby("family", dropna=False):
        family_summary.append(
            {
                "family": family,
                "rows": len(part),
                "research_candidates": int(part["research_candidate_label"].fillna(False).astype(bool).sum()),
                "near_miss": int(part["near_miss_label"].fillna(False).astype(bool).sum()),
                "raw_recent_fail": int(part["raw_recent_fail"].fillna(False).astype(bool).sum()),
                "cost20_recent_fail": int(part["cost20_recent_fail"].fillna(False).astype(bool).sum()),
                "lag1_recent_fail": int(part["lag1_recent_fail"].fillna(False).astype(bool).sum()),
                "may_stress_fail": int(
                    (
                        part["may_raw_severe_fail_stress_only"].fillna(False).astype(bool)
                        | part["may_residual_funding_negative_stress_only"].fillna(False).astype(bool)
                    ).sum()
                ),
            }
        )

    label_taxonomy = [
        {"label": "raw_validation_fail", "kind": "selection_failure", "policy_training_allowed": True},
        {"label": "raw_recent_fail", "kind": "selection_failure", "policy_training_allowed": True},
        {"label": "residual_funding_validation_fail", "kind": "selection_failure", "policy_training_allowed": True},
        {"label": "residual_funding_recent_fail", "kind": "selection_failure", "policy_training_allowed": True},
        {"label": "residual_core4_recent_fail", "kind": "selection_failure", "policy_training_allowed": True},
        {"label": "cost20_recent_fail", "kind": "selection_failure", "policy_training_allowed": True},
        {"label": "lag1_recent_fail", "kind": "selection_failure", "policy_training_allowed": True},
        {"label": "near_miss_label", "kind": "policy_target_preferred", "policy_training_allowed": True},
        {"label": "research_candidate_label", "kind": "rare_policy_target", "policy_training_allowed": True},
        {"label": "may_raw_severe_fail_stress_only", "kind": "stress_label_only", "policy_training_allowed": False},
        {"label": "may_residual_funding_negative_stress_only", "kind": "stress_label_only", "policy_training_allowed": False},
    ]

    write_csv(A7M0_DIR / "a7m0_label_summary.csv", label_summary_rows, ["label", "count", "rate", "policy_training_allowed"])
    write_csv(A7M0_DIR / "a7m0_source_summary.csv", source_summary, ["source_run", "rows", "selected_for_replay", "research_candidates", "near_miss", "clue", "may_stress_fail", "policy_training_eligible"])
    write_csv(A7M0_DIR / "a7m0_family_failure_summary.csv", family_summary, ["family", "rows", "research_candidates", "near_miss", "raw_recent_fail", "cost20_recent_fail", "lag1_recent_fail", "may_stress_fail"])
    write_csv(A7M0_DIR / "a7m0_label_taxonomy.csv", label_taxonomy, ["label", "kind", "policy_training_allowed"])

    manifest = {
        "generated_at": now,
        "decision": "PASS_A7M0_FAILURE_LABELED_DATASET_BUILD",
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_search": False,
        "executes_replay": False,
        "trains_surrogate": False,
        "authorizes_a7m1_surrogate_preflight": True,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "may_policy": {
            "may_labels_included": True,
            "may_policy_training_allowed": False,
            "may_allowed_use": "stress_label_and_failure_attribution_only",
        },
        "inputs": {name: {k: str(v) for k, v in spec.items() if isinstance(v, Path)} for name, spec in SOURCES.items()},
        "source_counts": source_counts,
        "outputs": {
            "dataset": str(dataset_path),
            "label_summary": str(A7M0_DIR / "a7m0_label_summary.csv"),
            "source_summary": str(A7M0_DIR / "a7m0_source_summary.csv"),
            "family_failure_summary": str(A7M0_DIR / "a7m0_family_failure_summary.csv"),
            "label_taxonomy": str(A7M0_DIR / "a7m0_label_taxonomy.csv"),
        },
        "row_count": int(len(dataset)),
        "unique_candidate_keys": int(dataset[["source_run", "candidate_id"]].drop_duplicates().shape[0]) if not dataset.empty else 0,
    }
    manifest["stable_manifest_hash"] = stable_hash({k: v for k, v in manifest.items() if k not in {"generated_at", "stable_manifest_hash"}})
    write_json(A7M0_DIR / f"crypto_a7m0_manifest_{DATE_TAG}.json", manifest)

    report_path = REPORT_DIR / f"CRYPTO_A7M0_FAILURE_LABELED_DATASET_{DATE_TAG}.md"
    report_lines = [
        "# Crypto A7M-0 Failure-Labeled Search Dataset",
        "",
        f"- generated_at: `{now}`",
        "- decision: `PASS_A7M0_FAILURE_LABELED_DATASET_BUILD`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- trains_surrogate: `False`",
        "- authorizes_a7m1_surrogate_preflight: `True`",
        "- authorizes_large_search: `False`",
        f"- row_count: `{len(dataset)}`",
        "",
        "## Purpose",
        "",
        "A7M-0 converts A7I/A7J/A7K/A7L negative evidence into a structured multi-label dataset for future active search policy work. It does not promote any candidate.",
        "",
        "## May Policy",
        "",
        "- May 2026 labels are included only as stress/failure attribution labels.",
        "- May labels are explicitly marked `policy_training_allowed = False`.",
        "- A7M-1 may not train ranking, reward, arm allocation, generator tuning, or mutation priors on May labels.",
        "",
        "## Source Summary",
        "",
        "| source_run | rows | selected | research | near_miss | clue | may_stress_fail |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in source_summary:
        report_lines.append(
            f"| `{row['source_run']}` | {row['rows']} | {row['selected_for_replay']} | {row['research_candidates']} | {row['near_miss']} | {row['clue']} | {row['may_stress_fail']} |"
        )
    report_lines += [
        "",
        "## Label Summary",
        "",
        "| label | count | rate | policy_training_allowed |",
        "|---|---:|---:|---|",
    ]
    for row in label_summary_rows:
        report_lines.append(f"| `{row['label']}` | {row['count']} | {row['rate']} | `{row['policy_training_allowed']}` |")
    report_lines += [
        "",
        "## Decision",
        "",
        "A7M-0 passes as a dataset build. It authorizes A7M-1 surrogate/policy preflight only. It does not authorize adaptive large search or alpha proof.",
    ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7M0_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7M-0 Decision Record",
                "",
                "- decision: `PASS_A7M0_FAILURE_LABELED_DATASET_BUILD`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                "- search_executed: `False`",
                "- replay_executed: `False`",
                "- trains_surrogate: `False`",
                "- authorizes_a7m1_surrogate_preflight: `True`",
                "- authorizes_large_search: `False`",
                "",
                "## Confirmed",
                "",
                "- Historical A7I/A7J/A7K/A7L candidates are converted into structured failure labels.",
                "- May stress labels are separated from policy-training labels.",
                "- Negative examples are retained as first-class search-policy data.",
                "",
                "## Not Confirmed",
                "",
                "- No search policy is trained yet.",
                "- No adaptive search is authorized.",
                "- No research candidate, alpha proof, shadow, paper, live, or production readiness.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
