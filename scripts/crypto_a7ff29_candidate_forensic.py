from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff29_candidate_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FF29_CANDIDATE_FORENSIC_20260530.md"
A7FF28A = REPO / "runtime" / "a7ff28a_bounded_deep_replay"

PREMAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
NON_L7_DECISION = "A7FF28A_NUMERIC_CLUE"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def candidate_summary(queue: pd.DataFrame, responses: pd.DataFrame, materialized: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    non_l7 = responses[responses["decision"].eq(NON_L7_DECISION) & responses["label_family"].ne("L7_ranked_future_return")].copy()
    for _, q in queue.iterrows():
        cid = q["blueprint_id"]
        cand = non_l7[non_l7["blueprint_id"].eq(cid)].copy()
        mat = materialized[materialized["blueprint_id"].eq(cid)].head(1)
        best = cand.sort_values(["control_ratio_premay_max", "robust_median_tstat_floor"], ascending=[True, False]).head(1)
        if best.empty:
            best_row: dict[str, Any] = {}
        else:
            best_row = best.iloc[0].to_dict()
        control_max = float(numeric(cand["control_ratio_premay_max"]).max()) if not cand.empty else np.nan
        control_min = float(numeric(cand["control_ratio_premay_max"]).min()) if not cand.empty else np.nan
        robust_min_floor = float(numeric(cand["robust_min_tstat_floor"]).min()) if not cand.empty else np.nan
        labels = "|".join(sorted(cand["label_family"].dropna().astype(str).unique()))
        horizons = "|".join(str(int(x)) for x in sorted(pd.to_numeric(cand["label_horizon_h"], errors="coerce").dropna().unique()))
        warnings: list[str] = []
        if np.isfinite(control_max) and control_max >= 0.8:
            warnings.append("control_warning_ge_0_8")
        if str(q.get("semantic_pair", "")).count("basis_premium_like") >= 1:
            warnings.append("basis_premium_root")
        if "SafeDiv" in str(q.get("expression", "")):
            warnings.append("safe_div_outlier_risk")
        if not mat.empty:
            std_value = float(pd.to_numeric(mat["std_value"], errors="coerce").iloc[0])
            max_abs = max(
                abs(float(pd.to_numeric(mat["min_value"], errors="coerce").iloc[0])),
                abs(float(pd.to_numeric(mat["max_value"], errors="coerce").iloc[0])),
            )
            if np.isfinite(std_value) and std_value > 0 and max_abs / std_value > 100:
                warnings.append("extreme_value_to_std_ratio_gt_100")
        rows.append(
            {
                "blueprint_id": cid,
                "expression": q.get("expression", ""),
                "semantic_pair": q.get("semantic_pair", ""),
                "motif": q.get("motif", ""),
                "skeleton_key": q.get("skeleton_key", ""),
                "non_l7_clue_rows": int(len(cand)),
                "non_l7_label_families": labels,
                "non_l7_horizons": horizons,
                "best_label_family": best_row.get("label_family", ""),
                "best_label_horizon_h": best_row.get("label_horizon_h", ""),
                "min_control_ratio": control_min,
                "max_control_ratio": control_max,
                "min_robust_min_tstat_floor": robust_min_floor,
                "finite_share": float(pd.to_numeric(mat["finite_share"], errors="coerce").iloc[0]) if not mat.empty else np.nan,
                "nonzero_share": float(pd.to_numeric(mat["nonzero_share"], errors="coerce").iloc[0]) if not mat.empty else np.nan,
                "activity_ok": bool(mat["activity_ok"].astype(str).str.lower().isin(["true", "1"]).iloc[0]) if not mat.empty else False,
                "warning_flags": "|".join(warnings),
                "forensic_decision": "A7FF29_FORENSIC_QUEUE_KEEP" if len(cand) > 0 and (not np.isfinite(control_max) or control_max < 1.0) else "A7FF29_FORENSIC_REJECT",
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    prior = read_json(A7FF28A / "a7ff28a_summary_manifest.json")
    if not prior.get("authorizes_a7ff29_candidate_forensic_contract"):
        raise SystemExit("A7FF-28A summary does not authorize A7FF-29")

    queue = read_csv(A7FF28A / "a7ff28a_a7ff29_candidate_forensic_queue.csv")
    responses = read_csv(A7FF28A / "a7ff28a_label_response_metrics.csv")
    controls = read_csv(A7FF28A / "a7ff28a_control_dominance_metrics.csv")
    materialized = read_csv(A7FF28A / "a7ff28a_materialization_metrics.csv")

    summary = candidate_summary(queue, responses, materialized)
    summary.to_csv(RUNTIME / "a7ff29_candidate_forensic_summary.csv", index=False)

    non_l7_matrix = responses[
        responses["blueprint_id"].isin(set(queue["blueprint_id"]))
        & responses["label_family"].ne("L7_ranked_future_return")
    ].copy()
    non_l7_matrix.to_csv(RUNTIME / "a7ff29_label_horizon_response_matrix.csv", index=False)

    control_pre = controls[
        controls["blueprint_id"].isin(set(queue["blueprint_id"]))
        & controls["split"].isin(PREMAY_SPLITS)
        & ~controls["control"].isin(["one_bar_lag", "sign_flip"])
    ].copy()
    control_summary = (
        control_pre.groupby(["blueprint_id", "label_family", "label_horizon_h"], dropna=False)
        .agg(
            max_control_ratio=("control_ratio_to_original", "max"),
            median_control_ratio=("control_ratio_to_original", "median"),
            worst_control=("control", lambda x: "|".join(sorted(set(map(str, x))))),
        )
        .reset_index()
        if not control_pre.empty
        else pd.DataFrame()
    )
    control_summary.to_csv(RUNTIME / "a7ff29_control_summary_by_label.csv", index=False)

    concentration = pd.DataFrame(
        [
            {"axis": "semantic_pair", "value": k, "count": int(v)}
            for k, v in queue["semantic_pair"].value_counts(dropna=False).items()
        ]
        + [
            {"axis": "motif", "value": k, "count": int(v)}
            for k, v in queue["motif"].value_counts(dropna=False).items()
        ]
    )
    concentration.to_csv(RUNTIME / "a7ff29_concentration_audit.csv", index=False)

    kept = summary[summary["forensic_decision"].eq("A7FF29_FORENSIC_QUEUE_KEEP")].copy()
    a7ff30_queue = kept[
        [
            "blueprint_id",
            "expression",
            "semantic_pair",
            "motif",
            "skeleton_key",
            "best_label_family",
            "best_label_horizon_h",
            "min_control_ratio",
            "max_control_ratio",
            "finite_share",
            "nonzero_share",
            "warning_flags",
        ]
    ].copy()
    a7ff30_queue.insert(0, "a7ff30_queue_rank", range(1, len(a7ff30_queue) + 1))
    a7ff30_queue.to_csv(RUNTIME / "a7ff29_a7ff30_portfolio_replay_contract_queue.csv", index=False)

    candidate_count = int(len(queue))
    keep_count = int(len(kept))
    semantic_pair_count = int(queue["semantic_pair"].nunique()) if not queue.empty else 0
    max_control = float(summary["max_control_ratio"].max()) if not summary.empty else None
    concentration_warning = bool(
        queue["semantic_pair"].astype(str).str.contains("basis_premium_like", regex=False).all()
    ) if not queue.empty else False
    warnings: list[str] = []
    if concentration_warning:
        warnings.append("all_candidates_have_basis_premium_root")
    if "safe_div_outlier_risk" in "|".join(summary["warning_flags"].astype(str)):
        warnings.append("safe_div_outlier_risk_present")
    if semantic_pair_count < 3:
        warnings.append("semantic_pair_count_lt_3")
    if max_control is not None and max_control >= 0.8:
        warnings.append("control_warning_ge_0_8_present")

    decision = (
        "PASS_A7FF29_FORENSIC_READY_FOR_A7FF30_PORTFOLIO_REPLAY_CONTRACT_WITH_CONCENTRATION_WARNINGS_NO_SEARCH_AUTH"
        if keep_count >= 4 and semantic_pair_count >= 3 and (max_control is None or max_control < 1.0)
        else "HOLD_A7FF29_FORENSIC_QUEUE_NOT_READY"
    )
    manifest = {
        "stage": "A7FF-29",
        "generated_at": now_utc(),
        "decision": decision,
        "prior_stage": prior.get("stage", "A7FF-28A-SUMMARY"),
        "prior_decision": prior.get("decision", ""),
        "candidate_count": candidate_count,
        "kept_candidate_count": keep_count,
        "semantic_pair_count": semantic_pair_count,
        "max_control_ratio": max_control,
        "warnings": warnings,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_a7ff30_portfolio_replay_contract": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff29_manifest.json", manifest)
    write_json(RUNTIME / "a7ff29_decision_record.json", manifest)

    lines = [
        "# CRYPTO A7FF-29 CANDIDATE FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-29 audits the 6 non-L7 candidates from A7FF-28A. It does not generate formulas, execute search, or claim alpha.",
        "",
        "## Experiment Record",
        "",
        "```text",
        "experiment_id: 20260530_a7ff29_candidate_forensic",
        "objective: decide whether the 181-symbol non-L7 clue queue is clean enough for a portfolio replay contract",
        "inputs: runtime/a7ff28a_bounded_deep_replay/*",
        "parameters: no generation; no search; non-L7 only; control_ratio < 1 hard gate",
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Candidate Forensic Summary",
        "",
        md_table(summary, 20),
        "",
        "## A7FF-30 Contract Queue",
        "",
        md_table(a7ff30_queue, 20),
        "",
        "## Concentration Audit",
        "",
        md_table(concentration, 20),
        "",
        "## Control Summary",
        "",
        md_table(control_summary, 40),
        "",
        "## Boundary",
        "",
        "```text",
        "The queue is not an alpha proof. It remains concentrated in basis/premium-root candidates.",
        "A7FF-30 may only be a portfolio replay contract on this frozen queue.",
        "No formula search, large search, shadow, paper, or live execution is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
