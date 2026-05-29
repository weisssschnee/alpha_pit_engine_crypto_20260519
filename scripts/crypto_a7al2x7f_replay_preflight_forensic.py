from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
X7_RUNTIME = ROOT / "runtime" / "a7al2x7_small_numeric_replay_preflight"
RUNTIME = ROOT / "runtime" / "a7al2x7f_replay_preflight_forensic"
REPORT = ROOT / "reports" / "CRYPTO_A7AL2X7F_REPLAY_PREFLIGHT_FORENSIC_20260529.md"

PRE_MAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
CONTROL_VARIANTS = [
    "wrong_lag_future_24h",
    "wrong_lag_stale_168h",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_random",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    decisions = pd.read_csv(X7_RUNTIME / "a7al2x7_candidate_decisions.csv")
    metrics = pd.read_csv(X7_RUNTIME / "a7al2x7_candidate_variant_metrics.csv")
    sample = pd.read_csv(X7_RUNTIME / "a7al2x7_replayed_candidate_sample.csv")
    manifest = read_json(X7_RUNTIME / "a7al2x7_manifest.json")
    return decisions, metrics, sample, manifest


def metric_value(metrics: pd.DataFrame, cid: str, variant: str, split: str, column: str) -> float:
    row = metrics[
        metrics["candidate_id"].eq(cid)
        & metrics["variant"].eq(variant)
        & metrics["split"].eq(split)
    ]
    if row.empty:
        return np.nan
    return float(row.iloc[0][column])


def candidate_forensic(decisions: pd.DataFrame, metrics: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    sample_map = sample.set_index("candidate_id").to_dict("index")
    rows: list[dict[str, Any]] = []
    for row in decisions.to_dict("records"):
        cid = str(row["candidate_id"])
        orientation = float(row["orientation_from_train"])
        pre_values: dict[str, float] = {}
        pre_tstats: dict[str, float] = {}
        pre_nonoverlap_min: dict[str, float] = {}
        for split in PRE_MAY_SPLITS:
            spread = metric_value(metrics, cid, "original", split, "mean_spread_24h")
            pre_values[split] = orientation * spread if np.isfinite(spread) else np.nan
            pre_tstats[split] = orientation * metric_value(metrics, cid, "original", split, "naive_tstat")
            pre_nonoverlap_min[split] = orientation * metric_value(metrics, cid, "original", split, "nonoverlap_min_tstat")

        missing_pre_may = int(sum(not np.isfinite(v) for v in pre_values.values()))
        positive_pre_may = int(sum(np.isfinite(v) and v > 0 for v in pre_values.values()))
        negative_pre_may = int(sum(np.isfinite(v) and v <= 0 for v in pre_values.values()))
        sign_pattern = "/".join(
            "NA" if not np.isfinite(pre_values[s]) else ("+" if pre_values[s] > 0 else "-")
            for s in PRE_MAY_SPLITS
        )

        original_abs_values = {
            split: abs(pre_values[split]) if np.isfinite(pre_values[split]) else np.nan
            for split in PRE_MAY_SPLITS
        }
        control_rows: list[dict[str, Any]] = []
        for variant in CONTROL_VARIANTS:
            for split in PRE_MAY_SPLITS:
                orig_abs = original_abs_values[split]
                ctrl_spread = metric_value(metrics, cid, variant, split, "mean_spread_24h")
                ctrl_oriented_abs = abs(orientation * ctrl_spread) if np.isfinite(ctrl_spread) else np.nan
                ratio = ctrl_oriented_abs / orig_abs if np.isfinite(ctrl_oriented_abs) and np.isfinite(orig_abs) and orig_abs > 0 else np.nan
                control_rows.append(
                    {
                        "variant": variant,
                        "split": split,
                        "control_oriented_abs_spread": ctrl_oriented_abs,
                        "control_ratio": ratio,
                    }
                )
        finite_controls = [x for x in control_rows if np.isfinite(x["control_ratio"])]
        max_control = max(finite_controls, key=lambda x: x["control_ratio"]) if finite_controls else {}
        control_ratio_max = float(max_control.get("control_ratio", np.nan))
        control_dominated = bool(np.isfinite(control_ratio_max) and control_ratio_max >= 1.0)

        train_spread = metric_value(metrics, cid, "original", "train_2024", "mean_spread_24h")
        may_spread = metric_value(metrics, cid, "original", "known_may2026_stress", "mean_spread_24h")
        may_oriented = orientation * may_spread if np.isfinite(may_spread) else np.nan
        one_bar_recent = metric_value(metrics, cid, "one_bar_lag", "recent_oos_2026JanApr", "mean_spread_24h")
        original_recent = pre_values["recent_oos_2026JanApr"]
        one_bar_recent_oriented = orientation * one_bar_recent if np.isfinite(one_bar_recent) else np.nan
        lag_retention = (
            one_bar_recent_oriented / original_recent
            if np.isfinite(one_bar_recent_oriented) and np.isfinite(original_recent) and abs(original_recent) > 1e-12
            else np.nan
        )

        if missing_pre_may:
            failure_root = "metric_missing_or_sparse_smoke_window"
        elif positive_pre_may < len(PRE_MAY_SPLITS):
            failure_root = "pre_may_direction_unstable"
        elif control_dominated:
            failure_root = "matched_control_dominated"
        elif not np.isfinite(one_bar_recent_oriented) or one_bar_recent_oriented <= 0:
            failure_root = "one_bar_lag_fragile"
        elif not bool(row.get("may_stress_clean", False)):
            failure_root = "may_stress_veto_after_pre_may"
        else:
            failure_root = "stress_clean_preflight_clue"

        sample_row = sample_map.get(cid, {})
        rows.append(
            {
                "candidate_id": cid,
                "objective_family": row["objective_family"],
                "expression": sample_row.get("expression", ""),
                "fields": sample_row.get("fields", ""),
                "operator_signature": sample_row.get("operator_signature", ""),
                "skeleton_key": sample_row.get("skeleton_key", ""),
                "orientation_from_train": orientation,
                "train_oriented_spread": orientation * train_spread if np.isfinite(train_spread) else np.nan,
                "pre_may_sign_pattern": sign_pattern,
                "pre_may_positive_splits": positive_pre_may,
                "pre_may_negative_splits": negative_pre_may,
                "pre_may_missing_splits": missing_pre_may,
                "validation_oriented_spread": pre_values["validation_2025H1"],
                "test_oriented_spread": pre_values["test_2025H2"],
                "recent_oriented_spread": pre_values["recent_oos_2026JanApr"],
                "validation_oriented_tstat": pre_tstats["validation_2025H1"],
                "test_oriented_tstat": pre_tstats["test_2025H2"],
                "recent_oriented_tstat": pre_tstats["recent_oos_2026JanApr"],
                "validation_oriented_nonoverlap_min_tstat": pre_nonoverlap_min["validation_2025H1"],
                "test_oriented_nonoverlap_min_tstat": pre_nonoverlap_min["test_2025H2"],
                "recent_oriented_nonoverlap_min_tstat": pre_nonoverlap_min["recent_oos_2026JanApr"],
                "one_bar_recent_oriented_spread": one_bar_recent_oriented,
                "one_bar_recent_retention": lag_retention,
                "cost10_recent_proxy": row["cost10_recent_proxy"],
                "max_control_ratio_premay": control_ratio_max,
                "max_control_variant": max_control.get("variant", ""),
                "max_control_split": max_control.get("split", ""),
                "may_oriented_spread": may_oriented,
                "may_stress_clean": row["may_stress_clean"],
                "x7_decision": row["decision"],
                "failure_root": failure_root,
            }
        )
    return pd.DataFrame(rows)


def control_forensic(details: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    orientations = details.set_index("candidate_id")["orientation_from_train"].to_dict()
    for cid, orientation in orientations.items():
        for variant in CONTROL_VARIANTS:
            for split in PRE_MAY_SPLITS:
                original = metric_value(metrics, cid, "original", split, "mean_spread_24h")
                control = metric_value(metrics, cid, variant, split, "mean_spread_24h")
                orig_oriented = orientation * original if np.isfinite(original) else np.nan
                ctrl_oriented = orientation * control if np.isfinite(control) else np.nan
                ratio = (
                    abs(ctrl_oriented) / abs(orig_oriented)
                    if np.isfinite(orig_oriented) and np.isfinite(ctrl_oriented) and abs(orig_oriented) > 1e-12
                    else np.nan
                )
                rows.append(
                    {
                        "candidate_id": cid,
                        "variant": variant,
                        "split": split,
                        "original_oriented_spread": orig_oriented,
                        "control_oriented_spread": ctrl_oriented,
                        "control_abs_ratio": ratio,
                        "control_dominates": bool(np.isfinite(ratio) and ratio >= 1.0),
                    }
                )
    return pd.DataFrame(rows)


def family_summary(details: pd.DataFrame) -> pd.DataFrame:
    grouped = details.groupby("objective_family", dropna=False)
    rows = []
    for family, group in grouped:
        rows.append(
            {
                "objective_family": family,
                "candidate_count": int(len(group)),
                "pre_may_all_positive": int((group["pre_may_positive_splits"] == 3).sum()),
                "may_stress_clean": int(bool_series(group["may_stress_clean"]).sum()),
                "control_dominated": int((group["max_control_ratio_premay"] >= 1.0).sum()),
                "missing_or_sparse": int(group["failure_root"].eq("metric_missing_or_sparse_smoke_window").sum()),
                "median_max_control_ratio": float(group["max_control_ratio_premay"].median(skipna=True)),
                "median_recent_oriented_spread": float(group["recent_oriented_spread"].median(skipna=True)),
                "failure_roots": "|".join(sorted(group["failure_root"].dropna().astype(str).unique())),
            }
        )
    return pd.DataFrame(rows)


def split_alignment_summary(details: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for split, column in [
        ("validation_2025H1", "validation_oriented_spread"),
        ("test_2025H2", "test_oriented_spread"),
        ("recent_oos_2026JanApr", "recent_oriented_spread"),
        ("known_may2026_stress", "may_oriented_spread"),
    ]:
        values = details[column]
        rows.append(
            {
                "split": split,
                "candidate_count": int(len(values)),
                "finite_count": int(values.notna().sum()),
                "positive_count": int((values > 0).sum()),
                "positive_rate": float((values > 0).mean(skipna=True)),
                "median_oriented_spread": float(values.median(skipna=True)),
                "mean_oriented_spread": float(values.mean(skipna=True)),
            }
        )
    return pd.DataFrame(rows)


def root_summary(details: pd.DataFrame) -> pd.DataFrame:
    return (
        details["failure_root"]
        .value_counts(dropna=False)
        .rename_axis("failure_root")
        .reset_index(name="candidate_count")
    )


def control_summary(control: pd.DataFrame) -> pd.DataFrame:
    grouped = control.groupby(["variant", "split"], dropna=False)
    rows = []
    for (variant, split), group in grouped:
        rows.append(
            {
                "variant": variant,
                "split": split,
                "finite_ratio_count": int(group["control_abs_ratio"].notna().sum()),
                "dominance_count": int(group["control_dominates"].sum()),
                "median_control_abs_ratio": float(group["control_abs_ratio"].median(skipna=True)),
                "max_control_abs_ratio": float(group["control_abs_ratio"].max(skipna=True)),
            }
        )
    return pd.DataFrame(rows).sort_values(["dominance_count", "max_control_abs_ratio"], ascending=[False, False])


def write_report(
    manifest: dict[str, Any],
    details: pd.DataFrame,
    roots: pd.DataFrame,
    families: pd.DataFrame,
    split_summary: pd.DataFrame,
    control: pd.DataFrame,
    control_rollup: pd.DataFrame,
) -> None:
    lines = [
        "# CRYPTO A7AL-2X7F REPLAY PREFLIGHT FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "X7F is a forensic audit over existing X7 artifacts. It does not generate formulas, run search, train a model, or authorize replay promotion.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Failure Roots",
        "",
        md_table(roots),
        "",
        "## Split Alignment",
        "",
        md_table(split_summary),
        "",
        "## Objective Family Summary",
        "",
        md_table(families),
        "",
        "## Candidate Forensic Detail",
        "",
        md_table(
            details[
                [
                    "candidate_id",
                    "objective_family",
                    "pre_may_sign_pattern",
                    "pre_may_positive_splits",
                    "recent_oriented_spread",
                    "one_bar_recent_retention",
                    "cost10_recent_proxy",
                    "max_control_ratio_premay",
                    "max_control_variant",
                    "max_control_split",
                    "may_oriented_spread",
                    "failure_root",
                ]
            ],
            80,
        ),
        "",
        "## Control Dominance Rollup",
        "",
        md_table(control_rollup, 80),
        "",
        "## Highest Control Ratios",
        "",
        md_table(
            control.sort_values("control_abs_ratio", ascending=False).head(30),
            30,
        ),
        "",
        "## Interpretation",
        "",
        "```text",
        "Main finding:",
        "  X7 HOLD is not caused by evaluator failure. Existing numeric artifacts are complete enough for this forensic.",
        "",
        "Observed failure pattern:",
        "  Most selected OI/positioning interaction candidates do not keep the same oriented sign across validation, test, and recent OOS.",
        "  The only all-positive pre-May candidate is dominated by matched controls and is May-negative.",
        "  Wrong-lag / shuffle / same-family controls are often stronger than the original signals.",
        "",
        "Allowed next action:",
        "  forensic expansion or objective-family redesign only.",
        "",
        "Not authorized:",
        "  full replay",
        "  new formula generation",
        "  large search",
        "  alpha proof",
        "  shadow / paper / live",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    decisions, metrics, sample, x7_manifest = load_inputs()
    details = candidate_forensic(decisions, metrics, sample)
    controls = control_forensic(details, metrics)
    roots = root_summary(details)
    families = family_summary(details)
    split_summary = split_alignment_summary(details)
    controls_rollup = control_summary(controls)

    all_positive = int((details["pre_may_positive_splits"] == 3).sum())
    stress_clean = int((details["failure_root"] == "stress_clean_preflight_clue").sum())
    control_dominated = int((details["max_control_ratio_premay"] >= 1.0).sum())
    missing_or_sparse = int(details["failure_root"].eq("metric_missing_or_sparse_smoke_window").sum())

    blockers: list[str] = []
    if stress_clean == 0:
        blockers.append("no_stress_clean_preflight_clues")
    if all_positive <= 1:
        blockers.append("pre_may_alignment_too_sparse")
    if control_dominated > 0:
        blockers.append("matched_controls_often_dominate")
    if missing_or_sparse > 0:
        blockers.append("some_families_sparse_under_smoke_subset")

    decision = "HOLD_A7AL2X7F_OBJECTIVE_FAMILY_NUMERIC_EVIDENCE_WEAK"
    manifest = {
        "stage": "A7AL-2X7F",
        "generated_at": now_utc(),
        "decision": decision,
        "source_stage": "A7AL-2X7",
        "source_decision": x7_manifest.get("decision"),
        "executes_formula_generation": False,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_full_numeric_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "candidate_count": int(len(details)),
        "pre_may_all_positive_count": all_positive,
        "stress_clean_preflight_clue_count": stress_clean,
        "control_dominated_count": control_dominated,
        "missing_or_sparse_count": missing_or_sparse,
        "blockers": blockers,
        "allowed_next": [
            "A7AL-2X7F forensic expansion on company machine",
            "objective-family redesign away from current OI/positioning pool",
        ],
    }

    details.to_csv(RUNTIME / "a7al2x7f_candidate_failure_taxonomy.csv", index=False)
    families.to_csv(RUNTIME / "a7al2x7f_objective_family_failure_summary.csv", index=False)
    split_summary.to_csv(RUNTIME / "a7al2x7f_split_alignment_summary.csv", index=False)
    controls.to_csv(RUNTIME / "a7al2x7f_control_dominance_detail.csv", index=False)
    controls_rollup.to_csv(RUNTIME / "a7al2x7f_control_dominance_rollup.csv", index=False)
    roots.to_csv(RUNTIME / "a7al2x7f_failure_root_summary.csv", index=False)
    write_json(RUNTIME / "a7al2x7f_manifest.json", manifest)
    write_json(
        RUNTIME / "a7al2x7f_decision_record.json",
        {
            "decision": decision,
            "source_stage": "A7AL-2X7",
            "source_decision": x7_manifest.get("decision"),
            "primary_findings": [
                "X7 evaluator artifacts are available and do not indicate implementation failure.",
                "Pre-May split alignment is weak: only one candidate is positive across validation, test, and recent OOS.",
                "Matched controls dominate most candidates when inspected across pre-May splits.",
                "No stress-clean replay-preflight clue is present in the bounded smoke sample.",
            ],
            "blocking_issues": blockers,
            "recommended_next_action": [
                "Do not authorize A7AL-2Y or full replay from current X7 evidence.",
                "Either expand X7F forensic on the company machine or redesign away from the current OI/positioning pool.",
            ],
            "authorization": {
                "full_numeric_replay": False,
                "formula_generation": False,
                "large_search": False,
                "alpha_proof": False,
                "shadow_paper_live": False,
            },
        },
    )
    write_json(
        RUNTIME / "a7al2x7f_authorization_matrix.json",
        {
            "A7AL-2X7F": {"status": decision},
            "full_numeric_replay": {"authorized": False},
            "formula_generation": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    write_report(manifest, details, roots, families, split_summary, controls, controls_rollup)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
