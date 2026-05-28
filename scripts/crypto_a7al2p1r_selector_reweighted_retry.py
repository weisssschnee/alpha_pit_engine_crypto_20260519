from __future__ import annotations

import importlib.util
import json
import math
import re
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

FAST_SCRIPT = REPO / "scripts" / "crypto_a7al2l_fast_derived_replay_preflight.py"
O_SCRIPT = REPO / "scripts" / "crypto_a7al2o_candidate_mini_replay.py"

A7AL2P1_FEATURES = REPO / "runtime" / "a7al2p1_selector_feature_generation" / "a7al2p1_selector_feature_matrix.csv"
TAXONOMY = REPO / "runtime" / "a7ak_lv3r_contract_meme_taxonomy_audit" / "a7ak_lv3r_contract_meme_taxonomy.csv"
LV1_SYMBOL_STATE = REPO / "runtime" / "a7ak_lv1_latent_state_feature_build" / "a7ak_lv1_symbol_state_coverage.csv"

OUT_DIR = REPO / "runtime" / "a7al2p1r_selector_reweighted_retry"
REPORT = REPO / "reports" / "CRYPTO_A7AL2P1R_SELECTOR_REWEIGHTED_RETRY_20260528.md"

PRE_MAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
COST_BPS = [2.0, 5.0, 10.0]


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fast = load_module("a7al2l_fast_for_p1r", FAST_SCRIPT)
o = load_module("a7al2o_for_p1r", O_SCRIPT)


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


def finite_tstat(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    if len(x) < 3:
        return np.nan
    std = np.nanstd(x, ddof=1)
    if not np.isfinite(std) or std <= 0:
        return np.nan
    return float(np.nanmean(x) / std * math.sqrt(len(x)))


def portfolio_weights_and_spread(signal: np.ndarray, label: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    return o.portfolio_weights_and_spread(signal, label)


def turnover_series(weights: np.ndarray) -> np.ndarray:
    return o.turnover_series(weights)


def split_rows(
    candidate_id: str,
    variant: str,
    oriented_spread: np.ndarray,
    oriented_weights: np.ndarray,
    split: np.ndarray,
    top_count: np.ndarray,
    bottom_count: np.ndarray,
) -> list[dict[str, Any]]:
    turnover = turnover_series(oriented_weights)
    rows: list[dict[str, Any]] = []
    for split_name in fast.SPLIT_ORDER:
        mask = (split == split_name) & np.isfinite(oriented_spread)
        x = oriented_spread[mask]
        t = turnover[mask]
        row = {
            "candidate_id": candidate_id,
            "variant": variant,
            "split": split_name,
            "n_dates": int(mask.sum()),
            "mean_spread_24h": float(np.nanmean(x)) if len(x) else np.nan,
            "spread_tstat": finite_tstat(x),
            "positive_spread_rate": float(np.nanmean(x > 0)) if len(x) else np.nan,
            "avg_one_way_turnover": float(np.nanmean(t)) if len(t) else np.nan,
            "avg_top_count": float(np.nanmean(top_count[mask])) if mask.any() else np.nan,
            "avg_bottom_count": float(np.nanmean(bottom_count[mask])) if mask.any() else np.nan,
        }
        for cost in COST_BPS:
            net = x - t * (cost / 10000.0)
            row[f"net_mean_spread_{int(cost)}bps"] = float(np.nanmean(net)) if len(net) else np.nan
        rows.append(row)
    return rows


def variant_positive_count(split_summary: pd.DataFrame, candidate_id: str, variant: str, col: str = "mean_spread_24h") -> int:
    part = split_summary[
        split_summary["candidate_id"].eq(candidate_id)
        & split_summary["variant"].eq(variant)
        & split_summary["split"].isin(PRE_MAY_SPLITS)
    ]
    if len(part) != 3:
        return 0
    return int(pd.to_numeric(part[col], errors="coerce").gt(0).sum())


def classify(candidate: pd.Series, split_summary: pd.DataFrame) -> dict[str, Any]:
    cid = str(candidate["candidate_id"])
    variants = [
        "original",
        "one_bar_lag",
        "neutral_liquidity_tier",
        "neutral_meme_contract_group",
        "neutral_multiplier_flag",
        "neutral_major_flag",
        "neutral_dominant_latent_state",
        "exclude_meme",
        "exclude_multiplier",
        "exclude_major",
    ]
    pass_variants = [v for v in variants if variant_positive_count(split_summary, cid, v) == 3]
    net_pass_variants = [v for v in variants if variant_positive_count(split_summary, cid, v, "net_mean_spread_2bps") == 3]
    neutral_pass_count = len([v for v in pass_variants if v.startswith("neutral_") or v.startswith("exclude_")])
    control_ratio = numeric(candidate.get("control_ratio_premay_max_by_split"))
    latent_count = int(numeric(candidate.get("latent_positive_premay_splits"), 0))
    recent_original = split_summary[
        split_summary["candidate_id"].eq(cid)
        & split_summary["variant"].eq("original")
        & split_summary["split"].eq("recent_oos_2026JanApr")
    ]
    recent_turnover = numeric(recent_original.iloc[0]["avg_one_way_turnover"]) if not recent_original.empty else np.nan
    reasons = []
    warnings_out = []
    if "original" not in pass_variants:
        reasons.append("original_not_all_premay_positive")
    if "one_bar_lag" not in pass_variants:
        reasons.append("one_bar_lag_not_all_premay_positive")
    if neutral_pass_count < 2:
        reasons.append("neutralization_survival_weak")
    if not net_pass_variants:
        reasons.append("cost_proxy_fragile")
    if np.isfinite(control_ratio) and control_ratio >= 1.0:
        reasons.append("control_dominated")
    elif np.isfinite(control_ratio) and control_ratio >= 0.8:
        warnings_out.append("control_close")
    if latent_count < 3:
        reasons.append("timevarying_latent_fragile")
    if np.isfinite(recent_turnover) and recent_turnover > 1.50:
        warnings_out.append("high_turnover_proxy")
    if not reasons:
        label = "A7AL2P1R_SELECTOR_REWEIGHTED_DIAGNOSTIC_PASS"
    elif "control_dominated" in reasons:
        label = "HOLD_A7AL2P1R_CONTROL_DOMINATED"
    elif "timevarying_latent_fragile" in reasons:
        label = "HOLD_A7AL2P1R_LATENT_FRAGILE"
    elif "neutralization_survival_weak" in reasons:
        label = "HOLD_A7AL2P1R_NEUTRALIZATION_FRAGILE"
    elif "cost_proxy_fragile" in reasons:
        label = "HOLD_A7AL2P1R_COST_FRAGILE"
    else:
        label = "HOLD_A7AL2P1R_RETRY_WEAK"
    return {
        "candidate_id": cid,
        "decision": label,
        "reasons": "|".join(reasons),
        "warnings": "|".join(warnings_out),
        "pass_variants": "|".join(pass_variants),
        "net_2bps_pass_variants": "|".join(net_pass_variants),
        "neutralized_pass_variant_count": neutral_pass_count,
        "recent_turnover": recent_turnover,
        "control_ratio_premay_max_by_split": control_ratio,
        "latent_positive_premay_splits": latent_count,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    features = pd.read_csv(A7AL2P1_FEATURES)
    candidates = features[features["selector_decision"].eq("A7AL2P1_SELECTOR_DIAGNOSTIC_ELIGIBLE")].copy()
    if candidates.empty:
        manifest = {
            "generated_at": utc_now(),
            "decision": "HOLD_A7AL2P1R_NO_SELECTOR_ELIGIBLE_CANDIDATES",
            "input": str(A7AL2P1_FEATURES),
            "candidate_count": 0,
            "diagnostic_pass_count": 0,
            "decision_counts": {},
            "blockers": ["no_selector_eligible_candidates"],
            "warnings": [],
            "executes_training": False,
            "executes_search": False,
            "executes_alpha_proof": False,
            "uses_may_for_selection": False,
            "authorizes_a7al2p_contract": False,
            "authorizes_formula_search_execution": False,
            "authorizes_alpha_proof": False,
            "authorizes_shadow_paper_live": False,
            "required_next": "regenerate or adjust non-May selector inputs; do not use stale P1R pass artifacts",
        }
        empty_decisions = pd.DataFrame(
            columns=[
                "candidate_id",
                "decision",
                "reasons",
                "warnings",
                "pass_variants",
                "net_2bps_pass_variants",
                "neutralized_pass_variant_count",
                "recent_turnover",
                "control_ratio_premay_max_by_split",
                "latent_positive_premay_splits",
            ]
        )
        empty_split = pd.DataFrame(
            columns=[
                "candidate_id",
                "variant",
                "split",
                "n_dates",
                "mean_spread_24h",
                "spread_tstat",
                "positive_spread_rate",
                "avg_one_way_turnover",
                "avg_top_count",
                "avg_bottom_count",
                "net_mean_spread_2bps",
                "net_mean_spread_5bps",
                "net_mean_spread_10bps",
            ]
        )
        empty_split.to_csv(OUT_DIR / "a7al2p1r_variant_split_summary.csv", index=False)
        empty_decisions.to_csv(OUT_DIR / "a7al2p1r_decision_record.csv", index=False)
        pd.DataFrame(columns=["candidate_id", "error"]).to_csv(OUT_DIR / "a7al2p1r_eval_errors.csv", index=False)
        write_json(OUT_DIR / "a7al2p1r_manifest.json", manifest)
        report = f"""# CRYPTO A7AL-2P1R Selector-Reweighted Retry

Generated: {manifest["generated_at"]}

## Decision

```text
{manifest["decision"]}
```

No A7AL-2P1 selector-eligible candidates were available. This file intentionally replaces any previous P1R pass artifacts so stale selector output cannot be used downstream.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Boundary

```text
Not authorized:
  A7AL-2P contract
  formula search execution
  alpha proof
  shadow / paper / live
```
"""
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(report, encoding="utf-8")
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return

    fields = {"trade_close"}
    for text in candidates["expression"].dropna().astype(str):
        for field in re.findall(r"\b[a-z][a-z0-9_]*\b", text):
            if field not in {"nan", "inf", "rank", "zscore", "mean", "delta", "mul", "sub", "add", "neg", "abs", "sign"}:
                fields.add(field)
    symbols = fast.strict_symbols()
    loaded_symbols, timestamps, matrices = fast.load_panel_matrices(symbols, fields)
    split = fast.split_for_timestamps(timestamps)
    label = fast.label_matrix(matrices["trade_close"], timestamps, split)
    evaluator = fast.MatrixFormulaEvaluator(matrices, field_shift=0)

    taxonomy = pd.read_csv(TAXONOMY).drop_duplicates("symbol").set_index("symbol").reindex(loaded_symbols)
    state_cov = pd.read_csv(LV1_SYMBOL_STATE).drop_duplicates("symbol").set_index("symbol").reindex(loaded_symbols)
    group_values = {
        "liquidity_tier": taxonomy["liquidity_tier"].fillna("unknown").tolist(),
        "meme_contract_group": taxonomy["meme_contract_group"].fillna("unknown").tolist(),
        "multiplier_flag": taxonomy["is_multiplier_contract"].fillna(False).astype(bool).astype(str).tolist(),
        "major_flag": taxonomy["is_major"].fillna(False).astype(bool).astype(str).tolist(),
        "dominant_latent_state": state_cov["dominant_state_id"].fillna("unknown").tolist(),
    }
    masks = {
        "exclude_meme": ~taxonomy["is_meme_token"].fillna(False).astype(bool).to_numpy(),
        "exclude_multiplier": ~taxonomy["is_multiplier_contract"].fillna(False).astype(bool).to_numpy(),
        "exclude_major": ~taxonomy["is_major"].fillna(False).astype(bool).to_numpy(),
    }

    split_rows_all: list[dict[str, Any]] = []
    decision_rows: list[dict[str, Any]] = []
    eval_errors: list[dict[str, Any]] = []
    for _, row in candidates.iterrows():
        cid = str(row["candidate_id"])
        expression = str(row["expression"])
        print(f"[A7AL-2P1R] {cid}", flush=True)
        try:
            signal = evaluator.eval(expression)
            orientation_values = [
                numeric(row.get("original_validation_spread")),
                numeric(row.get("original_test_spread")),
                numeric(row.get("original_recent_spread")),
            ]
            orientation = 1.0 if np.nanmean([v for v in orientation_values if np.isfinite(v)] or [1.0]) >= 0 else -1.0
            variants = {
                "original": signal,
                "one_bar_lag": fast.shift_matrix(signal, 1),
                "neutral_liquidity_tier": o.group_zscore(signal, group_values["liquidity_tier"]),
                "neutral_meme_contract_group": o.group_zscore(signal, group_values["meme_contract_group"]),
                "neutral_multiplier_flag": o.group_zscore(signal, group_values["multiplier_flag"]),
                "neutral_major_flag": o.group_zscore(signal, group_values["major_flag"]),
                "neutral_dominant_latent_state": o.group_zscore(signal, group_values["dominant_latent_state"], min_group_symbols=12),
                "exclude_meme": o.mask_symbols(signal, masks["exclude_meme"]),
                "exclude_multiplier": o.mask_symbols(signal, masks["exclude_multiplier"]),
                "exclude_major": o.mask_symbols(signal, masks["exclude_major"]),
            }
            for variant, values in variants.items():
                weights, spread, top_count, bottom_count = portfolio_weights_and_spread(values, label)
                split_rows_all.extend(split_rows(cid, variant, spread * orientation, weights * orientation, split, top_count, bottom_count))
        except Exception as exc:
            eval_errors.append({"candidate_id": cid, "error": repr(exc)})

    split_summary = pd.DataFrame(split_rows_all)
    if not split_summary.empty:
        for _, row in candidates.iterrows():
            decision_rows.append(classify(row, split_summary))
    decisions = pd.DataFrame(decision_rows)
    decision_counts = decisions["decision"].value_counts().rename_axis("decision").reset_index(name="count") if not decisions.empty else pd.DataFrame()
    pass_count = int(decisions["decision"].eq("A7AL2P1R_SELECTOR_REWEIGHTED_DIAGNOSTIC_PASS").sum()) if not decisions.empty else 0
    blockers: list[str] = []
    warnings: list[str] = []
    if eval_errors:
        blockers.append("candidate_eval_errors")
    if pass_count == 0:
        blockers.append("no_selector_reweighted_candidate_survives")
    if pass_count < 2:
        warnings.append("selector_reweighted_pool_below_2")

    decision = "PASS_A7AL2P1R_SELECTOR_REWEIGHTED_POOL_READY_FOR_P0R_RETRY" if pass_count > 0 and not eval_errors else "HOLD_A7AL2P1R_SELECTOR_REWEIGHTED_RETRY_BLOCKED"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input": str(A7AL2P1_FEATURES),
        "candidate_count": int(len(candidates)),
        "diagnostic_pass_count": pass_count,
        "decision_counts": {str(r["decision"]): int(r["count"]) for _, r in decision_counts.iterrows()},
        "blockers": blockers,
        "warnings": warnings,
        "executes_training": False,
        "executes_search": False,
        "executes_alpha_proof": False,
        "uses_may_for_selection": False,
        "authorizes_a7al2p_contract": False,
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": "freeze selector-reweighted diagnostic pool; do not execute A7AL-2 search without separate contract",
    }

    split_summary.to_csv(OUT_DIR / "a7al2p1r_variant_split_summary.csv", index=False)
    decisions.to_csv(OUT_DIR / "a7al2p1r_decision_record.csv", index=False)
    pd.DataFrame(eval_errors).to_csv(OUT_DIR / "a7al2p1r_eval_errors.csv", index=False)
    write_json(OUT_DIR / "a7al2p1r_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2P1R Selector-Reweighted Retry

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This stage reruns a mini replay only on A7AL-2P1 selector-eligible candidates. It uses no May inputs for selection and does not authorize formula-search execution.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Decision Counts

{md_table(decision_counts, 20)}

## Candidate Decisions

{md_table(decisions, 20)}

## Variant Split Summary

{md_table(split_summary[split_summary["split"].isin(PRE_MAY_SPLITS + ["known_may2026_stress"])], 80)}

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
