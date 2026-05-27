from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR
from crypto_a7o_search_space_and_fold_replay import (
    A7O_DIR,
    DRY_GENERATED_PER_CELL,
    expression_from_motif,
    diversify_expression,
    field_family,
    horizon_value,
    select_field_pair,
    apply_cell_context,
)


DATE_TAG = "20260520"
A7O2C_DIR = RUNTIME_DIR / "a7o2c_semantic_uniqueness_authorization"

AUTHORIZED_MAX_WINDOW = 144
AUTHORIZED_P95_WINDOW = 96
MIN_EFFECTIVE_UNIQUE_RATIO = 0.85
MIN_SIMPLIFIED_EFFECTIVE_UNIQUE_RATIO = 0.75
MIN_ECONOMIC_CELL_UNIQUE_RATIO = 0.80
MAX_TOP_ECONOMIC_MOTIF_SHARE = 0.10
MAX_TOP_FEATURE_OPERATOR_HORIZON_TRIPLE_SHARE = 0.08
MIN_FOLD_EFFECTIVE_SAMPLE_RATE = 0.60


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


def bucket_window(value: int) -> str:
    if value <= 6:
        return "H6"
    if value <= 12:
        return "H12"
    if value <= 24:
        return "H24"
    if value <= 48:
        return "H48"
    if value <= 72:
        return "H72"
    if value <= 144:
        return "HGT72_LE144"
    return "HGT144"


INTEGER_RE = re.compile(r"(?<![\w.])-?\d+(?![\w.])")


def extract_windows(expr: str) -> list[int]:
    values: list[int] = []
    for match in INTEGER_RE.finditer(expr):
        try:
            value = int(match.group(0))
        except ValueError:
            continue
        if value >= 3:
            values.append(value)
    return values


def bucket_expression(expr: str) -> str:
    def repl(match: re.Match[str]) -> str:
        value = int(match.group(0))
        if value < 3:
            return match.group(0)
        return bucket_window(value)

    return INTEGER_RE.sub(repl, expr.replace(" ", ""))


def generate_cell_candidate_rows(cells: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in cells.iterrows():
        fields = str(row["fields"]).split(";") if "fields" in row.index else []
        if not fields:
            # Fall back to registry field names; this path should not normally run.
            fields = ["ret_6", "ret_12"]
        for j in range(DRY_GENERATED_PER_CELL):
            f1, f2 = select_field_pair(fields, j)
            h = horizon_value(str(row["temporal_horizon_class"]), j)
            expr = expression_from_motif(str(row["operator_motif"]), f1, f2, h, str(row["regime_fold_target"]), j)
            expr = diversify_expression(expr, f1, f2, j)
            if str(row["normalization_scope"]).startswith("cross_symbol") and not expr.startswith("CrossSymbol"):
                expr = f"{row['normalization_scope']}({expr})"
            if str(row["residualization_target"]) == "FundingCore" and not expr.startswith("ResidualizeVsFundingCore"):
                expr = f"ResidualizeVsFundingCore({expr})"
            elif str(row["residualization_target"]) == "Core4" and not expr.startswith("ResidualizeVsCore4"):
                expr = f"ResidualizeVsCore4({expr})"
            elif str(row["residualization_target"]) == "FundingCore_and_Core4":
                expr = f"ResidualizeVsCore4(ResidualizeVsFundingCore({expr}))"
            expr = apply_cell_context(expr, str(row["hypothesis_family"]), str(row["turnover_class"]), str(row["regime_fold_target"]), f1, f2, j)
            windows = extract_windows(expr)
            max_window = max(windows) if windows else 0
            fams = sorted({field_family(f1), field_family(f2)})
            rows.append(
                {
                    "cell_id": row["cell_id"],
                    "ordinal": j,
                    "hypothesis_family": row["hypothesis_family"],
                    "feature_family_set": row["feature_family_set"],
                    "operator_motif": row["operator_motif"],
                    "temporal_horizon_class": row["temporal_horizon_class"],
                    "normalization_scope": row["normalization_scope"],
                    "residualization_target": row["residualization_target"],
                    "turnover_class": row["turnover_class"],
                    "regime_fold_target": row["regime_fold_target"],
                    "field_family_pair": ";".join(fams),
                    "expression": expr,
                    "simplified_expression": expr.replace(" ", ""),
                    "bucketed_expression": bucket_expression(expr),
                    "window_count": len(windows),
                    "max_window": max_window,
                    "p95_source_window": np.nan,
                    "horizon_bucket": bucket_window(max_window) if max_window else "none",
                }
            )
    return pd.DataFrame(rows)


def load_cells_with_fields() -> pd.DataFrame:
    cells = pd.read_csv(A7O_DIR / "a7o_search_cell_registry.csv")
    feature_registry = pd.read_csv(A7O_DIR / "a7o_feature_family_registry.csv")
    return cells.merge(feature_registry[["feature_family_set", "fields"]], on="feature_family_set", how="left")


def semantic_uniqueness(candidates: pd.DataFrame) -> pd.DataFrame:
    total = len(candidates)
    return pd.DataFrame(
        [
            {
                "metric": "raw_unique_expr_ratio",
                "value": candidates["expression"].nunique() / total,
                "threshold": 0.90,
                "pass": candidates["expression"].nunique() / total >= 0.90,
            },
            {
                "metric": "effective_unique_ratio_after_horizon_bucketing",
                "value": candidates["bucketed_expression"].nunique() / total,
                "threshold": MIN_EFFECTIVE_UNIQUE_RATIO,
                "pass": candidates["bucketed_expression"].nunique() / total >= MIN_EFFECTIVE_UNIQUE_RATIO,
            },
            {
                "metric": "simplified_effective_unique_ratio_after_bucket",
                "value": candidates["bucketed_expression"].str.replace(" ", "", regex=False).nunique() / total,
                "threshold": MIN_SIMPLIFIED_EFFECTIVE_UNIQUE_RATIO,
                "pass": candidates["bucketed_expression"].str.replace(" ", "", regex=False).nunique() / total >= MIN_SIMPLIFIED_EFFECTIVE_UNIQUE_RATIO,
            },
        ]
    )


def horizon_distribution(candidates: pd.DataFrame) -> pd.DataFrame:
    windows = candidates["max_window"].astype(int)
    return pd.DataFrame(
        [
            {"metric": "max_window", "value": int(windows.max()), "threshold": AUTHORIZED_MAX_WINDOW, "pass": int(windows.max()) <= AUTHORIZED_MAX_WINDOW},
            {"metric": "p95_window", "value": float(np.quantile(windows, 0.95)), "threshold": AUTHORIZED_P95_WINDOW, "pass": float(np.quantile(windows, 0.95)) <= AUTHORIZED_P95_WINDOW},
            {"metric": "p50_window", "value": float(np.quantile(windows, 0.50)), "threshold": "", "pass": True},
            {"metric": "horizon_bucket_count", "value": int(candidates["horizon_bucket"].nunique()), "threshold": 6, "pass": int(candidates["horizon_bucket"].nunique()) >= 6},
            {
                "metric": "continuous_window_inflation_flag",
                "value": int(windows.nunique()),
                "threshold": AUTHORIZED_MAX_WINDOW,
                "pass": int(windows.nunique()) <= AUTHORIZED_MAX_WINDOW,
            },
        ]
    )


def economic_uniqueness(candidates: pd.DataFrame, cells: pd.DataFrame) -> pd.DataFrame:
    econ_cols = [
        "hypothesis_family",
        "feature_family_set",
        "operator_motif",
        "temporal_horizon_class",
        "normalization_scope",
        "residualization_target",
        "turnover_class",
        "regime_fold_target",
    ]
    cell_econ = cells[econ_cols].astype(str).agg("|".join, axis=1)
    motif = candidates[econ_cols].astype(str).agg("|".join, axis=1)
    triple = candidates[["feature_family_set", "operator_motif", "temporal_horizon_class"]].astype(str).agg("|".join, axis=1)
    cell_ratio = cell_econ.nunique() / len(cells)
    top_motif_share = motif.value_counts(normalize=True).iloc[0]
    top_triple_share = triple.value_counts(normalize=True).iloc[0]
    return pd.DataFrame(
        [
            {
                "metric": "economic_cell_unique_ratio",
                "value": cell_ratio,
                "threshold": MIN_ECONOMIC_CELL_UNIQUE_RATIO,
                "pass": cell_ratio >= MIN_ECONOMIC_CELL_UNIQUE_RATIO,
            },
            {
                "metric": "top_economic_motif_share",
                "value": top_motif_share,
                "threshold": MAX_TOP_ECONOMIC_MOTIF_SHARE,
                "pass": top_motif_share <= MAX_TOP_ECONOMIC_MOTIF_SHARE,
            },
            {
                "metric": "top_feature_family_operator_horizon_triple_share",
                "value": top_triple_share,
                "threshold": MAX_TOP_FEATURE_OPERATOR_HORIZON_TRIPLE_SHARE,
                "pass": top_triple_share <= MAX_TOP_FEATURE_OPERATOR_HORIZON_TRIPLE_SHARE,
            },
            {"metric": "feature_family_set_count", "value": int(candidates["feature_family_set"].nunique()), "threshold": 16, "pass": int(candidates["feature_family_set"].nunique()) >= 16},
            {"metric": "operator_motif_count", "value": int(candidates["operator_motif"].nunique()), "threshold": 24, "pass": int(candidates["operator_motif"].nunique()) >= 24},
            {"metric": "horizon_class_count", "value": int(candidates["temporal_horizon_class"].nunique()), "threshold": 10, "pass": int(candidates["temporal_horizon_class"].nunique()) >= 10},
        ]
    )


def fold_feasibility(candidates: pd.DataFrame) -> pd.DataFrame:
    folds = pd.read_csv(A7O_DIR / "a7o_fold_definition_audit.csv")
    max_windows = candidates["max_window"].astype(int).to_numpy()
    rows = []
    for _, row in folds.iterrows():
        n = int(row["n"])
        rates = np.maximum(0, n - max_windows) / max(1, n)
        rows.append(
            {
                "fold_id": row["fold_id"],
                "n": n,
                "min_effective_sample_rate": float(np.min(rates)),
                "p05_effective_sample_rate": float(np.quantile(rates, 0.05)),
                "median_effective_sample_rate": float(np.quantile(rates, 0.50)),
                "share_below_60pct": float(np.mean(rates < MIN_FOLD_EFFECTIVE_SAMPLE_RATE)),
                "pass": bool(np.quantile(rates, 0.05) >= MIN_FOLD_EFFECTIVE_SAMPLE_RATE),
            }
        )
    return pd.DataFrame(rows)


def write_markdown_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "(empty)\n"
    return df.head(max_rows).to_markdown(index=False) + "\n"


def main() -> int:
    A7O2C_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    cells = load_cells_with_fields()
    candidates = generate_cell_candidate_rows(cells)
    semantic = semantic_uniqueness(candidates)
    horizon = horizon_distribution(candidates)
    economic = economic_uniqueness(candidates, cells)
    folds = fold_feasibility(candidates)

    sample = candidates.sort_values(["cell_id", "ordinal"]).groupby("cell_id").head(2).copy()
    sample = sample[
        [
            "cell_id",
            "ordinal",
            "hypothesis_family",
            "feature_family_set",
            "operator_motif",
            "temporal_horizon_class",
            "normalization_scope",
            "residualization_target",
            "regime_fold_target",
            "expression",
            "bucketed_expression",
            "max_window",
            "horizon_bucket",
        ]
    ]

    gate_rows = []
    for group, frame in [("semantic", semantic), ("horizon", horizon), ("economic", economic)]:
        for _, row in frame.iterrows():
            gate_rows.append({"group": group, "gate": row["metric"], "pass": bool(row["pass"]), "value": row["value"], "threshold": row["threshold"]})
    for _, row in folds.iterrows():
        gate_rows.append({"group": "fold_feasibility", "gate": f"{row['fold_id']}_p05_effective_sample_rate", "pass": bool(row["pass"]), "value": row["p05_effective_sample_rate"], "threshold": MIN_FOLD_EFFECTIVE_SAMPLE_RATE})
    gate_df = pd.DataFrame(gate_rows)
    blockers = gate_df.loc[~gate_df["pass"], "gate"].astype(str).tolist()
    decision = "PASS_A7O2C_READY_FOR_L1_AUTHORIZATION_RECORD" if not blockers else "HOLD_A7O2C_SEMANTIC_OR_HORIZON_FEASIBILITY_FAIL"

    paths = {
        "candidate_sample": A7O2C_DIR / "a7o2c_sample_generated_semantic_keys.csv",
        "semantic_uniqueness": A7O2C_DIR / "a7o2c_effective_uniqueness.csv",
        "horizon_distribution": A7O2C_DIR / "a7o2c_horizon_parameter_distribution.csv",
        "economic_uniqueness": A7O2C_DIR / "a7o2c_economic_motif_uniqueness.csv",
        "fold_feasibility": A7O2C_DIR / "a7o2c_fold_coverage_feasibility.csv",
        "gate_summary": A7O2C_DIR / "a7o2c_gate_summary.csv",
        "manifest": A7O2C_DIR / "a7o2c_manifest.json",
    }
    sample.to_csv(paths["candidate_sample"], index=False)
    semantic.to_csv(paths["semantic_uniqueness"], index=False)
    horizon.to_csv(paths["horizon_distribution"], index=False)
    economic.to_csv(paths["economic_uniqueness"], index=False)
    folds.to_csv(paths["fold_feasibility"], index=False)
    gate_df.to_csv(paths["gate_summary"], index=False)

    manifest = {
        "generated_at": now,
        "decision": decision,
        "executes_search": False,
        "executes_replay": False,
        "executes_large_backtest": False,
        "authorizes_l1_execution": False,
        "authorizes_l2_execution": False,
        "authorizes_l3_execution": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "shadow_paper_live_status": "NOT_AUTHORIZED",
        "input": {
            "cell_registry": str(A7O_DIR / "a7o_search_cell_registry.csv"),
            "fold_definition_audit": str(A7O_DIR / "a7o_fold_definition_audit.csv"),
            "dry_generated_per_cell": DRY_GENERATED_PER_CELL,
        },
        "blockers": blockers,
        "semantic_summary": semantic.to_dict(orient="records"),
        "horizon_summary": horizon.to_dict(orient="records"),
        "economic_summary": economic.to_dict(orient="records"),
        "fold_feasibility_min_p05": float(folds["p05_effective_sample_rate"].min()),
        "may_policy": {
            "allowed": ["post_selection_stress_label", "post_selection_veto", "failure_attribution"],
            "forbidden": ["score", "ranking", "threshold", "generation", "allocation", "mutation", "surrogate_target"],
        },
        "outputs": {k: str(v) for k, v in paths.items() if k != "manifest"},
    }
    manifest["stable_manifest_hash"] = stable_file_hash([v for k, v in paths.items() if k != "manifest"])
    write_json(paths["manifest"], manifest)

    report = [
        "# Crypto A7O-2C Semantic Uniqueness Audit",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- executes_large_backtest: `False`",
        "- authorizes_l1_execution: `False`",
        f"- blockers: `{blockers}`",
        "",
        "## Effective Uniqueness",
        "",
        write_markdown_table(semantic),
        "## Horizon Parameter Distribution",
        "",
        write_markdown_table(horizon),
        "## Economic Motif Uniqueness",
        "",
        write_markdown_table(economic),
        "## Fold Coverage Feasibility",
        "",
        write_markdown_table(folds, 50),
        "## Decision",
        "",
        "A7O-L1 remains unauthorized unless A7O-2C passes and a separate A7O-2D authorization record is written.",
    ]
    report_path = REPORT_DIR / f"CRYPTO_A7O2C_SEMANTIC_UNIQUENESS_AUDIT_{DATE_TAG}.md"
    report_path.write_text("\n".join(report), encoding="utf-8")

    decision_record = [
        "# Crypto A7O-2C L1 Authorization Decision",
        "",
        f"- decision: `{decision}`",
        "- authorizes_l1_execution: `False`",
        "- authorizes_l2_execution: `False`",
        "- authorizes_l3_execution: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "A7O-2C audits whether A7O-2B uniqueness is semantic rather than only syntactic. It does not run L1 and does not authorize L1 by itself.",
    ]
    decision_path = REPORT_DIR / f"CRYPTO_A7O2C_L1_AUTHORIZATION_DECISION_{DATE_TAG}.md"
    decision_path.write_text("\n".join(decision_record), encoding="utf-8")

    print(
        json.dumps(
            {
                "decision": decision,
                "blockers": blockers,
                "authorizes_l1_execution": False,
                "manifest": str(paths["manifest"]),
                "report": str(report_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
