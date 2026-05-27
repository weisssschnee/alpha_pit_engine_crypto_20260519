from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

FAST_SCRIPT = REPO / "scripts" / "crypto_a7al2l_fast_derived_replay_preflight.py"
P0_SCRIPT = REPO / "scripts" / "crypto_a7al2p0_pre_search_hardening_audit.py"

A7AL2K_SELECTED = REPO / "runtime" / "a7al2k_derived_generator_smoke" / "a7al2k_selected_candidates.csv"
A7AL2L_DECISIONS = REPO / "runtime" / "a7al2l_fast_derived_replay_preflight" / "a7al2l_fast_candidate_decisions.csv"
A7AL2L_METRICS = REPO / "runtime" / "a7al2l_fast_derived_replay_preflight" / "a7al2l_fast_candidate_variant_metrics.csv"
A7AL0R_LINEAGE = REPO / "runtime" / "a7al0r_code_feature_regime_readiness_audit" / "a7al0r_feature_lineage_ledger.csv"

OUT_DIR = REPO / "runtime" / "a7al2p1_selector_feature_generation"
REPORT = REPO / "reports" / "CRYPTO_A7AL2P1_SELECTOR_FEATURE_GENERATION_20260528.md"

PRE_MAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
CONTROL_VARIANTS = ["wrong_lag_future_24h", "wrong_lag_stale_168h", "time_shuffle", "symbol_shuffle", "same_family_random"]


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fast = load_module("a7al2l_fast_for_p1", FAST_SCRIPT)
p0 = load_module("a7al2p0_for_p1", P0_SCRIPT)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if pd.api.types.is_object_dtype(view[col]) or pd.api.types.is_string_dtype(view[col]):
            view[col] = view[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```\n" + view.to_string(index=False) + "\n```"


def numeric(value: Any, default: float = np.nan) -> float:
    try:
        return float(value)
    except Exception:
        return default


def split_tokens(value: Any) -> list[str]:
    if pd.isna(value):
        return []
    return [part for part in str(value).split("|") if part]


def operator_depth(expression: str) -> int:
    depth = 0
    max_depth = 0
    for char in expression:
        if char == "(":
            depth += 1
            max_depth = max(max_depth, depth)
        elif char == ")":
            depth = max(0, depth - 1)
    return max_depth


def lineage_features(fields: list[str], lineage: pd.DataFrame) -> dict[str, Any]:
    indexed = lineage.set_index("field_name", drop=False)
    rows = [indexed.loc[field] for field in fields if field in indexed.index]
    classes = Counter(str(row.get("feature_class", "unknown")) for row in rows)
    source_families = Counter(str(row.get("source_family", "unknown")) for row in rows)
    allowed_search = sum(str(row.get("allowed_for_search", "")).lower() == "true" for row in rows)
    uses_future = sum(str(row.get("uses_future", "")).lower() == "true" for row in rows)
    uses_label = sum(str(row.get("uses_label", "")).lower() == "true" for row in rows)
    max_lookback = max([numeric(row.get("lookback_hours"), 0.0) for row in rows] or [0.0])
    derived_count = sum(count for key, count in classes.items() if key.startswith("derived"))
    return {
        "lineage_fields_resolved": len(rows),
        "lineage_fields_total": len(fields),
        "lineage_resolved_share": len(rows) / len(fields) if fields else 1.0,
        "lineage_allowed_search_count": allowed_search,
        "lineage_uses_future_count": uses_future,
        "lineage_uses_label_count": uses_label,
        "lineage_max_lookback_hours": max_lookback,
        "lineage_feature_classes": "|".join(f"{k}:{v}" for k, v in sorted(classes.items())),
        "lineage_source_families": "|".join(f"{k}:{v}" for k, v in sorted(source_families.items())),
        "lineage_derived_field_count": derived_count,
        "lineage_raw_source_count": classes.get("raw_source", 0),
    }


def premay_control_by_split(metrics: pd.DataFrame, candidate_id: str) -> tuple[pd.DataFrame, float, int]:
    rows = []
    for split_name in PRE_MAY_SPLITS:
        part = metrics[(metrics["candidate_id"].eq(candidate_id)) & (metrics["split"].eq(split_name))]
        original = part[part["variant"].eq("original")]
        original_abs = abs(numeric(original["mean_spread_24h"].iloc[0])) if not original.empty else np.nan
        controls = part[part["variant"].isin(CONTROL_VARIANTS)].copy()
        max_control_abs = float(pd.to_numeric(controls["mean_spread_24h"], errors="coerce").abs().max()) if not controls.empty else np.nan
        ratio = max_control_abs / original_abs if np.isfinite(original_abs) and original_abs > 0 and np.isfinite(max_control_abs) else np.nan
        if np.isfinite(ratio) and ratio >= 1.0:
            gate = "HOLD_CONTROL_DOMINATED"
        elif np.isfinite(ratio) and ratio >= 0.8:
            gate = "WARN_CONTROL_CLOSE"
        else:
            gate = "ELIGIBLE_DIAGNOSTIC"
        rows.append(
            {
                "candidate_id": candidate_id,
                "split": split_name,
                "original_abs_spread": original_abs,
                "max_control_abs_spread": max_control_abs,
                "control_ratio": ratio,
                "control_gate": gate,
            }
        )
    frame = pd.DataFrame(rows)
    max_ratio = float(frame["control_ratio"].max()) if not frame.empty else np.nan
    hard_holds = int(frame["control_gate"].eq("HOLD_CONTROL_DOMINATED").sum()) if not frame.empty else 0
    return frame, max_ratio, hard_holds


def oriented_label_t1_metrics(candidate: pd.Series, signal: np.ndarray, label: np.ndarray, split: np.ndarray) -> tuple[pd.DataFrame, np.ndarray]:
    premay_values = [
        numeric(candidate.get("original_validation_spread")),
        numeric(candidate.get("original_test_spread")),
        numeric(candidate.get("original_recent_spread")),
    ]
    orientation = 1.0 if np.nanmean([v for v in premay_values if np.isfinite(v)] or [1.0]) >= 0 else -1.0
    _, spread = p0.portfolio_weights_and_spread(signal, label)
    rows = p0.split_metric_rows(str(candidate["candidate_id"]), "timevarying_latent_state_neutral", "label_t1_to_t25", spread, split, orientation)
    return pd.DataFrame(rows), spread * orientation


def selector_score(row: dict[str, Any]) -> float:
    # No May inputs. This is a dry selector score, not a promotion metric.
    premay_strength = np.nanmean(
        [
            abs(numeric(row.get("original_validation_spread"))),
            abs(numeric(row.get("original_test_spread"))),
            abs(numeric(row.get("original_recent_spread"))),
        ]
    )
    control_margin = max(-1.0, min(1.0, numeric(row.get("control_margin_min"), 0.0)))
    lag_survival = max(0.0, min(2.0, numeric(row.get("one_bar_lag_survival_recent"), 0.0)))
    latent_count = numeric(row.get("latent_positive_premay_splits"), 0.0)
    cost_proxy = max(0.0, 1.0 - numeric(row.get("formula_turnover_proxy"), 1.0))
    derived_bonus = min(0.00015, 0.00005 * numeric(row.get("lineage_derived_field_count"), 0.0))
    interaction_bonus = 0.0001 if numeric(row.get("field_count"), 0.0) >= 2 else 0.0
    return float(
        np.nan_to_num(premay_strength, nan=0.0)
        + 0.00035 * control_margin
        + 0.00020 * lag_survival
        + 0.00020 * latent_count
        + 0.00015 * cost_proxy
        + derived_bonus
        + interaction_bonus
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    selected = pd.read_csv(A7AL2K_SELECTED)
    decisions = pd.read_csv(A7AL2L_DECISIONS)
    metrics = pd.read_csv(A7AL2L_METRICS)
    lineage = pd.read_csv(A7AL0R_LINEAGE)

    clues = decisions[decisions["decision"].eq("A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE")].copy()
    if clues.empty:
        raise SystemExit("A7AL-2L has no clue candidates for selector feature generation")
    clues = clues.merge(
        selected[
            [
                "candidate_id",
                "expression",
                "fields",
                "field_families",
                "operators",
                "windows",
                "feature_role",
                "cell",
                "family",
                "skeleton_key",
                "production_key",
                "expression_key",
            ]
        ],
        on=["candidate_id", "cell", "family", "field_families", "fields", "operators", "windows", "feature_role"],
        how="left",
    )

    fields = {"trade_close"}
    for text in clues["fields"].dropna().astype(str):
        fields.update(split_tokens(text))
    symbols = fast.strict_symbols()
    loaded_symbols, timestamps, matrices = fast.load_panel_matrices(symbols, fields)
    split = fast.split_for_timestamps(timestamps)
    label_t1 = p0.label_matrix_entry_shift(matrices["trade_close"], timestamps, split, 1)
    evaluator = fast.MatrixFormulaEvaluator(matrices, field_shift=0)
    state_matrix, latent_coverage = p0.load_timevarying_latent_states(loaded_symbols, timestamps)

    feature_rows: list[dict[str, Any]] = []
    control_rows_all: list[dict[str, Any]] = []
    latent_rows_all: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for _, candidate in clues.iterrows():
        cid = str(candidate["candidate_id"])
        expression = str(candidate["expression"])
        print(f"[A7AL-2P1] {cid}", flush=True)
        try:
            fields_i = split_tokens(candidate.get("fields"))
            operators = split_tokens(candidate.get("operators"))
            windows = [int(w) for w in split_tokens(candidate.get("windows")) if str(w).isdigit()]
            lineage_part = lineage_features(fields_i, lineage)
            control_split, max_control_ratio, control_holds = premay_control_by_split(metrics, cid)
            control_rows_all.extend(control_split.to_dict("records"))

            signal = evaluator.eval(expression)
            latent_signal = p0.neutralize_timevarying_state(signal, state_matrix)
            latent_metrics, _latent_spread = oriented_label_t1_metrics(candidate, latent_signal, label_t1, split)
            latent_rows_all.extend(latent_metrics.to_dict("records"))
            latent_premay = latent_metrics[latent_metrics["split"].isin(PRE_MAY_SPLITS)].copy()
            latent_positive_count = int(pd.to_numeric(latent_premay["mean_oriented_spread"], errors="coerce").gt(0).sum())
            latent_min_spread = float(pd.to_numeric(latent_premay["mean_oriented_spread"], errors="coerce").min()) if not latent_premay.empty else np.nan

            recent = numeric(candidate.get("original_recent_spread"))
            lag_recent = numeric(candidate.get("one_bar_lag_recent_spread"))
            lag_survival = abs(lag_recent) / abs(recent) if np.isfinite(recent) and abs(recent) > 0 and np.isfinite(lag_recent) else np.nan
            max_window = max(windows) if windows else 1
            delta_count = operators.count("Delta")
            mean_count = operators.count("Mean")
            formula_turnover_proxy = min(1.0, (delta_count + 0.5 * operators.count("Rank")) / max(math.log1p(max_window), 1.0))
            formula_smoothing_score = min(1.0, (mean_count + math.log1p(max_window) / 8.0) / 3.0)
            field_count = len(fields_i)

            row = {
                "candidate_id": cid,
                "cell": candidate.get("cell"),
                "family": candidate.get("family"),
                "field_families": candidate.get("field_families"),
                "feature_role": candidate.get("feature_role"),
                "expression": expression,
                "expression_key": candidate.get("expression_key"),
                "skeleton_key": candidate.get("skeleton_key"),
                "production_key": candidate.get("production_key"),
                "field_count": field_count,
                "operator_count": len(operators),
                "operator_depth": operator_depth(expression),
                "window_count": len(windows),
                "window_min": min(windows) if windows else np.nan,
                "window_max": max_window if windows else np.nan,
                "window_mean": float(np.mean(windows)) if windows else np.nan,
                "has_rank": "Rank" in operators or "CSRank" in operators,
                "has_zscore": "ZScore" in operators,
                "has_delta": "Delta" in operators,
                "has_mean": "Mean" in operators,
                "has_mul": "Mul" in operators,
                "has_abs_or_sign": "Abs" in operators or "Sign" in operators,
                "is_cross_source_interaction": len(set(split_tokens(candidate.get("field_families")))) >= 2,
                "formula_turnover_proxy": formula_turnover_proxy,
                "formula_smoothing_score": formula_smoothing_score,
                "original_validation_spread": candidate.get("original_validation_spread"),
                "original_test_spread": candidate.get("original_test_spread"),
                "original_recent_spread": candidate.get("original_recent_spread"),
                "one_bar_lag_recent_spread": lag_recent,
                "one_bar_lag_survival_recent": lag_survival,
                "control_ratio_premay_max_by_split": max_control_ratio,
                "control_margin_min": 1.0 - max_control_ratio if np.isfinite(max_control_ratio) else np.nan,
                "control_hard_hold_split_count": control_holds,
                "latent_positive_premay_splits": latent_positive_count,
                "latent_min_premay_spread": latent_min_spread,
                "latent_gate": "PASS" if latent_positive_count == 3 else "HOLD_TIMEVARYING_LATENT_FRAGILE",
                "matched_control_gate": "PASS" if control_holds == 0 else "HOLD_CONTROL_DOMINATED",
                "uses_may_in_selector": False,
                **lineage_part,
            }
            row["selector_feature_score_no_may"] = selector_score(row)
            if row["matched_control_gate"] != "PASS":
                row["selector_decision"] = row["matched_control_gate"]
            elif row["latent_gate"] != "PASS":
                row["selector_decision"] = row["latent_gate"]
            elif numeric(row["lineage_uses_future_count"]) > 0 or numeric(row["lineage_uses_label_count"]) > 0:
                row["selector_decision"] = "HOLD_LINEAGE_LEAKAGE"
            else:
                row["selector_decision"] = "A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE"
            feature_rows.append(row)
        except Exception as exc:
            errors.append({"candidate_id": cid, "error": repr(exc)})

    feature_matrix = pd.DataFrame(feature_rows).sort_values("selector_feature_score_no_may", ascending=False)
    control_by_split = pd.DataFrame(control_rows_all)
    latent_metrics = pd.DataFrame(latent_rows_all)
    error_frame = pd.DataFrame(errors)

    decision_counts = feature_matrix["selector_decision"].value_counts().rename_axis("selector_decision").reset_index(name="count") if not feature_matrix.empty else pd.DataFrame()
    eligible_count = int(feature_matrix["selector_decision"].eq("A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE").sum()) if not feature_matrix.empty else 0
    blockers: list[str] = []
    warnings: list[str] = []
    if errors:
        blockers.append("selector_feature_eval_errors")
    if eligible_count == 0:
        blockers.append("no_selector_candidate_survives_timevarying_latent_gate")
    if eligible_count < 2:
        warnings.append("selector_eligible_pool_below_2")
    if int(feature_matrix["lineage_resolved_share"].lt(1.0).sum()) if not feature_matrix.empty else 0:
        warnings.append("some_candidate_fields_missing_lineage")

    decision = "PASS_A7AL2P1_SELECTOR_FEATURES_READY_FOR_P0R_RETRY" if eligible_count > 0 and not errors else "HOLD_A7AL2P1_SELECTOR_FEATURES_BLOCKED"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "candidate_scope": "A7AL-2L replay-preflight clue candidates only",
        "candidate_count": int(len(feature_matrix)),
        "selector_eligible_count": eligible_count,
        "decision_counts": {str(r["selector_decision"]): int(r["count"]) for _, r in decision_counts.iterrows()},
        "blockers": blockers,
        "warnings": warnings,
        "latent_coverage": latent_coverage,
        "executes_training": False,
        "executes_search": False,
        "executes_alpha_proof": False,
        "uses_may_in_selector": False,
        "authorizes_a7al2p_contract": False,
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": "If eligible_count > 0, run a selector-reweighted mini replay/P0R retry; otherwise regenerate with time-varying latent survival in selector.",
    }

    feature_matrix.to_csv(OUT_DIR / "a7al2p1_selector_feature_matrix.csv", index=False)
    control_by_split.to_csv(OUT_DIR / "a7al2p1_control_dominance_by_split.csv", index=False)
    latent_metrics.to_csv(OUT_DIR / "a7al2p1_timevarying_latent_metrics.csv", index=False)
    error_frame.to_csv(OUT_DIR / "a7al2p1_eval_errors.csv", index=False)
    write_json(OUT_DIR / "a7al2p1_manifest.json", manifest)
    write_json(
        OUT_DIR / "a7al2p1_feature_generation_contract.json",
        {
            "generated_at": manifest["generated_at"],
            "contract": "A7AL-2P1 selector feature generation",
            "derived_feature_policy": {
                "derived_fields_are_allowed": True,
                "raw_source_independence_is_not_required_for_selector_features": True,
                "required": [
                    "field lineage resolved",
                    "PIT and label leakage clear",
                    "formula structure features",
                    "cross-source interaction tags",
                    "replay/control/lag features",
                    "time-varying latent neutral survival",
                    "cost/turnover proxy",
                    "family/skeleton/cell diversity keys",
                ],
                "forbidden": [
                    "May in selector score",
                    "May threshold tuning",
                    "label/future fields as features",
                    "promotion from replay-only clue",
                ],
            },
            "score_components_no_may": [
                "premay spread strength",
                "split-specific control dominance margin",
                "one-bar lag survival",
                "time-varying latent positive split count",
                "formula turnover proxy",
                "formula smoothing score",
                "derived/interaction feature bonus",
                "skeleton/production/family identity for diversity",
            ],
        },
    )

    report = f"""# CRYPTO A7AL-2P1 Selector Feature Generation

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This stage upgrades selector inputs. It does not train, does not search, and does not authorize A7AL-2 execution. Derived features are first-class selector features when lineage and PIT rules are clean.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Decision Counts

{md_table(decision_counts, 20)}

## Selector Feature Matrix

{md_table(feature_matrix[[
    "candidate_id",
    "cell",
    "family",
    "field_families",
    "selector_decision",
    "selector_feature_score_no_may",
    "control_ratio_premay_max_by_split",
    "control_hard_hold_split_count",
    "latent_positive_premay_splits",
    "latent_min_premay_spread",
    "one_bar_lag_survival_recent",
    "formula_turnover_proxy",
    "formula_smoothing_score",
    "lineage_feature_classes",
]], 80) if not feature_matrix.empty else "`<empty>`"}

## Split Control Gate

{md_table(control_by_split, 80)}

## Time-Varying Latent Neutralization

{md_table(latent_metrics[latent_metrics["split"].isin(PRE_MAY_SPLITS)] if not latent_metrics.empty else latent_metrics, 80)}

## Boundary

```text
Not authorized:
  A7AL-2P search contract
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
