from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7ab6_small_numeric_replay_preflight import CONTROL_VARIANTS, PRE_MAY_SPLITS  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ac1_representative_forensic_execution"
REPORT = REPO / "reports" / "CRYPTO_A7AC1_REPRESENTATIVE_FORENSIC_EXECUTION_20260529.md"

A7AC0_MANIFEST = REPO / "runtime" / "a7ac0_representative_forensic_contract" / "a7ac0_manifest.json"
A7AC0_REPS = REPO / "runtime" / "a7ac0_representative_forensic_contract" / "a7ac0_representative_input_pool.csv"
A7AB8_METRICS = REPO / "runtime" / "a7ab8_clue_forensic_execution" / "a7ab8_full_window_variant_metrics.csv"
A7AB8_DECISIONS = REPO / "runtime" / "a7ab8_clue_forensic_execution" / "a7ab8_forensic_decisions.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
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


def metric_value(metrics: pd.DataFrame, candidate_id: str, label_family: str, horizon_h: int, variant: str, split: str, col: str) -> float:
    sub = metrics[
        metrics["candidate_id"].astype(str).eq(candidate_id)
        & metrics["label_family"].astype(str).eq(label_family)
        & metrics["horizon_h"].astype(int).eq(int(horizon_h))
        & metrics["variant"].astype(str).eq(variant)
        & metrics["split"].astype(str).eq(split)
    ]
    if sub.empty:
        return np.nan
    return float(sub.iloc[0][col])


def max_control_ratio_by_split(metrics: pd.DataFrame, candidate_id: str, label_family: str, horizon_h: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split in PRE_MAY_SPLITS:
        original = abs(metric_value(metrics, candidate_id, label_family, horizon_h, "original", split, "mean_spread"))
        best_variant = ""
        best_abs = np.nan
        ratio = np.nan
        for variant in CONTROL_VARIANTS:
            if variant in {"original", "one_bar_lag"}:
                continue
            value = abs(metric_value(metrics, candidate_id, label_family, horizon_h, variant, split, "mean_spread"))
            if np.isfinite(value) and (not np.isfinite(best_abs) or value > best_abs):
                best_abs = value
                best_variant = variant
        if np.isfinite(original) and original > 1e-12 and np.isfinite(best_abs):
            ratio = float(best_abs / original)
        rows.append(
            {
                "candidate_id": candidate_id,
                "label_family": label_family,
                "horizon_h": horizon_h,
                "split": split,
                "original_abs_spread": original,
                "strongest_control_variant": best_variant,
                "strongest_control_abs_spread": best_abs,
                "control_ratio": ratio,
                "control_hard_hold_ge_1": bool(np.isfinite(ratio) and ratio >= 1.0),
                "control_warning_ge_0_80": bool(np.isfinite(ratio) and 0.80 <= ratio < 1.0),
            }
        )
    return rows


def representative_audit(reps: pd.DataFrame, metrics: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    control_rows: list[dict[str, Any]] = []
    for _, rep in reps.iterrows():
        cid = str(rep["candidate_id"])
        label_family = str(rep["label_family"])
        horizon = int(rep["horizon_h"])
        orientation = float(rep["orientation_from_train"])
        expected = {
            "validation_2025H1": float(rep["oriented_validation_spread"]),
            "test_2025H2": float(rep["oriented_test_spread"]),
            "recent_oos_2026JanApr": float(rep["oriented_recent_spread"]),
        }
        reproduced: dict[str, float] = {}
        parity_diffs: list[float] = []
        oriented_tstats: list[float] = []
        oriented_nonoverlap_min_tstats: list[float] = []
        oriented_nonoverlap_median_tstats: list[float] = []
        for split, expected_value in expected.items():
            raw_value = metric_value(metrics, cid, label_family, horizon, "original", split, "mean_spread")
            spread_tstat = metric_value(metrics, cid, label_family, horizon, "original", split, "spread_tstat")
            no_min = metric_value(metrics, cid, label_family, horizon, "original", split, "nonoverlap_min_tstat")
            no_med = metric_value(metrics, cid, label_family, horizon, "original", split, "nonoverlap_median_tstat")
            reproduced_value = orientation * raw_value if np.isfinite(raw_value) else np.nan
            reproduced[split] = reproduced_value
            if np.isfinite(reproduced_value) and np.isfinite(expected_value):
                parity_diffs.append(abs(reproduced_value - expected_value))
            oriented_tstats.append(orientation * spread_tstat if np.isfinite(spread_tstat) else np.nan)
            oriented_nonoverlap_min_tstats.append(orientation * no_min if np.isfinite(no_min) else np.nan)
            oriented_nonoverlap_median_tstats.append(orientation * no_med if np.isfinite(no_med) else np.nan)

        lag_recent = orientation * metric_value(metrics, cid, label_family, horizon, "one_bar_lag", "recent_oos_2026JanApr", "mean_spread")
        recent = reproduced["recent_oos_2026JanApr"]
        turnover = float(rep["turnover_proxy"])
        cost2 = recent - (2.0 / 10000.0) * turnover if np.isfinite(recent) and np.isfinite(turnover) else np.nan
        cost5 = recent - (5.0 / 10000.0) * turnover if np.isfinite(recent) and np.isfinite(turnover) else np.nan
        cost10 = recent - (10.0 / 10000.0) * turnover if np.isfinite(recent) and np.isfinite(turnover) else np.nan
        cost20 = recent - (20.0 / 10000.0) * turnover if np.isfinite(recent) and np.isfinite(turnover) else np.nan

        controls = max_control_ratio_by_split(metrics, cid, label_family, horizon)
        control_rows.extend(controls)
        ratios = [row["control_ratio"] for row in controls if np.isfinite(row["control_ratio"])]
        max_control_ratio = max(ratios) if ratios else np.nan

        max_parity_diff = max(parity_diffs) if parity_diffs else np.nan
        parity_ok = bool(np.isfinite(max_parity_diff) and max_parity_diff <= 1e-10)
        premay_positive = all(np.isfinite(x) and x > 0 for x in reproduced.values())
        hard_control_clean = bool(np.isfinite(max_control_ratio) and max_control_ratio < 1.0)
        control_warning = bool(np.isfinite(max_control_ratio) and max_control_ratio >= 0.80)
        lag_ok = bool(np.isfinite(lag_recent) and lag_recent > 0 and abs(lag_recent) >= 0.25 * abs(recent))
        cost20_ok = bool(np.isfinite(cost20) and cost20 > 0)
        nonoverlap_positive = bool(
            all(np.isfinite(x) and x > 0 for x in oriented_nonoverlap_median_tstats)
            and all(np.isfinite(x) and x > 0 for x in oriented_nonoverlap_min_tstats)
        )
        concentration_ok = bool(
            float(rep["top_symbol_abs_contribution_share"]) <= 0.35
            and float(rep["top_month_abs_contribution_share"]) <= 0.35
        )

        blockers: list[str] = []
        warnings: list[str] = []
        if not parity_ok:
            blockers.append("metric_parity_fail")
        if not premay_positive:
            blockers.append("premay_spread_nonpositive")
        if not hard_control_clean:
            blockers.append("control_ratio_ge_1")
        if not lag_ok:
            blockers.append("one_bar_lag_fail")
        if not cost20_ok:
            blockers.append("cost20_fail")
        if not nonoverlap_positive:
            blockers.append("nonoverlap_tstat_not_positive")
        if not concentration_ok:
            blockers.append("concentration_fail")
        if control_warning and hard_control_clean:
            warnings.append("control_ratio_warning_ge_0_80")
        if label_family == "L7_ranked_future_return":
            warnings.append("ranked_return_label_only")

        if blockers:
            decision = "HOLD_A7AC1_REPRESENTATIVE_FORENSIC_BLOCKED"
        elif warnings:
            decision = "A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS"
        else:
            decision = "A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS"

        rows.append(
            {
                "representative_rank": int(rep["representative_rank"]),
                "candidate_id": cid,
                "label_family": label_family,
                "horizon_h": horizon,
                "return_corr_cluster": int(rep["return_corr_cluster"]),
                "max_metric_parity_diff": max_parity_diff,
                "oriented_validation_spread": reproduced["validation_2025H1"],
                "oriented_test_spread": reproduced["test_2025H2"],
                "oriented_recent_spread": recent,
                "one_bar_lag_recent_oriented": lag_recent,
                "cost2_recent_oriented": cost2,
                "cost5_recent_oriented": cost5,
                "cost10_recent_oriented": cost10,
                "cost20_recent_oriented": cost20,
                "max_control_ratio_by_split": max_control_ratio,
                "min_oriented_nonoverlap_median_tstat": float(np.nanmin(oriented_nonoverlap_median_tstats)),
                "min_oriented_nonoverlap_min_tstat": float(np.nanmin(oriented_nonoverlap_min_tstats)),
                "min_oriented_hourly_tstat": float(np.nanmin(oriented_tstats)),
                "top_symbol": rep["top_symbol"],
                "top_symbol_abs_contribution_share": float(rep["top_symbol_abs_contribution_share"]),
                "top_month": rep["top_month"],
                "top_month_abs_contribution_share": float(rep["top_month_abs_contribution_share"]),
                "decision": decision,
                "blockers": ";".join(blockers) if blockers else "none",
                "warnings": ";".join(warnings) if warnings else "none",
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(control_rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ac0 = read_json(A7AC0_MANIFEST)
    if not a7ac0.get("authorizes_a7ac1_representative_forensic_execution"):
        raise SystemExit("A7AC-0 does not authorize A7AC-1")

    reps = pd.read_csv(A7AC0_REPS)
    metrics = pd.read_csv(A7AB8_METRICS)
    decisions = pd.read_csv(A7AB8_DECISIONS)
    rep_audit, control_audit = representative_audit(reps, metrics)

    decision_counts = rep_audit["decision"].value_counts().rename_axis("decision").reset_index(name="count")
    blocking_rows = rep_audit[rep_audit["decision"].eq("HOLD_A7AC1_REPRESENTATIVE_FORENSIC_BLOCKED")]
    diagnostic_pass_rows = rep_audit[rep_audit["decision"].ne("HOLD_A7AC1_REPRESENTATIVE_FORENSIC_BLOCKED")]
    label_summary = (
        rep_audit.groupby(["label_family", "horizon_h"], as_index=False)
        .agg(
            representative_rows=("candidate_id", "count"),
            diagnostic_pass_rows=("decision", lambda x: int((x != "HOLD_A7AC1_REPRESENTATIVE_FORENSIC_BLOCKED").sum())),
            median_recent_spread=("oriented_recent_spread", "median"),
            median_control_ratio=("max_control_ratio_by_split", "median"),
            min_nonoverlap_min_tstat=("min_oriented_nonoverlap_min_tstat", "min"),
        )
        .sort_values(["diagnostic_pass_rows", "representative_rows"], ascending=[False, False])
    )
    cluster_summary = (
        rep_audit.groupby("return_corr_cluster", as_index=False)
        .agg(
            representative_rows=("candidate_id", "count"),
            diagnostic_pass_rows=("decision", lambda x: int((x != "HOLD_A7AC1_REPRESENTATIVE_FORENSIC_BLOCKED").sum())),
            median_recent_spread=("oriented_recent_spread", "median"),
            median_control_ratio=("max_control_ratio_by_split", "median"),
        )
        .sort_values(["diagnostic_pass_rows", "representative_rows"], ascending=[False, False])
    )

    pass_count = int(len(diagnostic_pass_rows))
    hard_block_count = int(len(blocking_rows))
    warning_pass_count = int(rep_audit["decision"].eq("A7AC1_REPRESENTATIVE_DIAGNOSTIC_PASS_WITH_WARNINGS").sum())
    unique_pass_candidates = int(diagnostic_pass_rows["candidate_id"].nunique()) if pass_count else 0
    unique_pass_clusters = int(diagnostic_pass_rows["return_corr_cluster"].nunique()) if pass_count else 0

    warnings: list[str] = []
    if warning_pass_count:
        warnings.append("diagnostic_pass_rows_have_warnings")
    if rep_audit["label_family"].nunique() == 1:
        warnings.append("single_label_family_only")
    if reps["candidate_id"].nunique() < len(reps):
        warnings.append("same_candidate_multi_horizon")

    authorizes_a7ac1r = bool(hard_block_count > 0 and pass_count >= 4)
    if pass_count >= 4 and hard_block_count == 0:
        decision = "PASS_A7AC1_REPRESENTATIVE_FORENSIC_DIAGNOSTIC_POOL_WITH_WARNINGS" if warnings else "PASS_A7AC1_REPRESENTATIVE_FORENSIC_DIAGNOSTIC_POOL"
        authorizes_a7ac2 = True
    elif pass_count > 0:
        decision = "HOLD_A7AC1_REPRESENTATIVE_FORENSIC_PARTIAL_BLOCKERS"
        authorizes_a7ac2 = False
    else:
        decision = "HOLD_A7AC1_NO_REPRESENTATIVE_FORENSIC_PASS"
        authorizes_a7ac2 = False

    experiment_record = {
        "date": "2026-05-29",
        "experiment_id": "20260529_a7ac1_representative_forensic_execution",
        "objective": "Execute artifact-level forensic checks on A7AB-9 representative survivors.",
        "status": "completed",
        "mode": "light_forensic",
        "inputs": {
            "a7ac0_manifest": str(A7AC0_MANIFEST),
            "representative_pool": str(A7AC0_REPS),
            "a7ab8_metrics": str(A7AB8_METRICS),
            "a7ab8_decisions": str(A7AB8_DECISIONS),
        },
        "parameters": {
            "new_formula_generation": False,
            "new_replay_execution": False,
            "metric_source": "A7AB-8 full-window metrics",
            "control_hard_gate": "control_ratio < 1.0",
            "control_warning_gate": "control_ratio >= 0.80",
            "cost_bps": [2, 5, 10, 20],
        },
        "outputs": {"runtime": str(RUNTIME), "report": str(REPORT)},
        "decision": decision,
        "next_action": (
            "A7AC-2 label-diversification and neutralization contract"
            if authorizes_a7ac2
            else "A7AC-1R representative quarantine contract"
            if authorizes_a7ac1r
            else "HOLD; inspect blockers"
        ),
    }
    manifest = {
        "stage": "A7AC-1",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_representative_forensic": True,
        "executes_new_replay": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may": False,
        "input_a7ac0_decision": a7ac0.get("decision"),
        "representative_rows": int(len(reps)),
        "diagnostic_pass_rows": pass_count,
        "hard_block_rows": hard_block_count,
        "warning_pass_rows": warning_pass_count,
        "diagnostic_pass_candidates": unique_pass_candidates,
        "diagnostic_pass_clusters": unique_pass_clusters,
        "decision_counts": {str(r["decision"]): int(r["count"]) for _, r in decision_counts.iterrows()},
        "warnings": warnings,
        "authorizes_a7ac1r_representative_quarantine_contract": authorizes_a7ac1r,
        "authorizes_a7ac2_label_diversification_contract": authorizes_a7ac2,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    rep_audit.to_csv(RUNTIME / "a7ac1_representative_forensic_audit.csv", index=False)
    control_audit.to_csv(RUNTIME / "a7ac1_control_dominance_by_split.csv", index=False)
    decision_counts.to_csv(RUNTIME / "a7ac1_decision_counts.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ac1_label_summary.csv", index=False)
    cluster_summary.to_csv(RUNTIME / "a7ac1_cluster_summary.csv", index=False)
    decisions.to_csv(RUNTIME / "a7ac1_source_a7ab8_decisions.csv", index=False)
    write_json(RUNTIME / "a7ac1_experiment_record.json", experiment_record)
    write_json(RUNTIME / "a7ac1_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ac1_authorization_matrix.json",
        {
            "A7AC-1": {"status": decision},
            "A7AC-1R_representative_quarantine_contract": {"authorized": authorizes_a7ac1r},
            "A7AC-2_label_diversification_and_neutralization_contract": {"authorized": authorizes_a7ac2},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AC-1 REPRESENTATIVE FORENSIC EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AC-1 audits A7AB-9 representatives using A7AB-8 full-window metrics. It does not generate formulas, run new replay, train, search, or authorize alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Decision Counts",
        "",
        md_table(decision_counts),
        "",
        "## Representative Forensic Audit",
        "",
        md_table(rep_audit, 80),
        "",
        "## Control Dominance By Split",
        "",
        md_table(control_audit, 120),
        "",
        "## Label Summary",
        "",
        md_table(label_summary),
        "",
        "## Cluster Summary",
        "",
        md_table(cluster_summary),
        "",
        "## Experiment Record",
        "",
        "```json",
        json.dumps(experiment_record, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
