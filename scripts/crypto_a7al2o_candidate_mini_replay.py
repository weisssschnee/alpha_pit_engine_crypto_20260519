from __future__ import annotations

import importlib.util
import json
import math
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
A7AL2N_SUMMARY = REPO / "runtime" / "a7al2n_derived_deep_audit" / "a7al2n_deep_candidate_summary.csv"
A7AL2L_VARIANT_METRICS = REPO / "runtime" / "a7al2l_fast_derived_replay_preflight" / "a7al2l_fast_candidate_variant_metrics.csv"
TAXONOMY = REPO / "runtime" / "a7ak_lv3r_contract_meme_taxonomy_audit" / "a7ak_lv3r_contract_meme_taxonomy.csv"
LV1_SYMBOL_STATE = REPO / "runtime" / "a7ak_lv1_latent_state_feature_build" / "a7ak_lv1_symbol_state_coverage.csv"

OUT_DIR = REPO / "runtime" / "a7al2o_candidate_mini_replay"
REPORT = REPO / "reports" / "CRYPTO_A7AL2O_CANDIDATE_MINI_REPLAY_20260527.md"

PRE_MAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
AUDIT_SPLITS = PRE_MAY_SPLITS + ["known_may2026_stress"]
COST_BPS = [2.0, 5.0, 10.0]
MIN_GROUP_SYMBOLS = 8


def load_fast_module() -> Any:
    spec = importlib.util.spec_from_file_location("a7al2l_fast", FAST_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {FAST_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fast = load_fast_module()


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


def numeric(x: Any, default: float = np.nan) -> float:
    try:
        return float(x)
    except Exception:
        return default


def finite_tstat(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    if len(x) < 3:
        return np.nan
    std = np.nanstd(x, ddof=1)
    if not np.isfinite(std) or std <= 0:
        return np.nan
    return float(np.nanmean(x) / std * math.sqrt(len(x)))


def portfolio_weights_and_spread(signal: np.ndarray, label: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    valid = np.isfinite(signal) & np.isfinite(label)
    valid_counts = valid.sum(axis=0)
    enough = valid_counts >= fast.MIN_ACTIVE_SYMBOLS
    sig = np.where(valid, signal, np.nan)
    q10 = np.full(signal.shape[1], np.nan)
    q90 = np.full(signal.shape[1], np.nan)
    cols = np.where(enough)[0]
    if len(cols):
        with np.errstate(all="ignore"):
            q10[cols] = np.nanpercentile(sig[:, cols], 10, axis=0)
            q90[cols] = np.nanpercentile(sig[:, cols], 90, axis=0)
    top_mask = valid & enough.reshape(1, -1) & (signal >= q90.reshape(1, -1))
    bottom_mask = valid & enough.reshape(1, -1) & (signal <= q10.reshape(1, -1))
    top_count = top_mask.sum(axis=0)
    bottom_count = bottom_mask.sum(axis=0)
    ok = (top_count > 0) & (bottom_count > 0)
    weights = np.zeros(signal.shape, dtype=np.float64)
    if ok.any():
        cols_ok = np.where(ok)[0]
        weights[:, cols_ok] += top_mask[:, cols_ok] / top_count[cols_ok].reshape(1, -1)
        weights[:, cols_ok] -= bottom_mask[:, cols_ok] / bottom_count[cols_ok].reshape(1, -1)
    spread = np.full(signal.shape[1], np.nan)
    spread[ok] = np.nansum(weights[:, ok] * label[:, ok], axis=0)
    return weights, spread, top_count.astype(float), bottom_count.astype(float)


def turnover_series(weights: np.ndarray) -> np.ndarray:
    prev = np.zeros(weights.shape[0], dtype=np.float64)
    out = np.full(weights.shape[1], np.nan)
    for j in range(weights.shape[1]):
        w = weights[:, j]
        if np.isfinite(w).any() and np.abs(w).sum() > 0:
            out[j] = 0.5 * float(np.nansum(np.abs(w - prev)))
            prev = w.copy()
        else:
            out[j] = 0.0
            prev = np.zeros_like(prev)
    return out


def group_zscore(signal: np.ndarray, group_values: list[Any], min_group_symbols: int = MIN_GROUP_SYMBOLS) -> np.ndarray:
    out = np.full_like(signal, np.nan, dtype=np.float64)
    groups = pd.Series(group_values).fillna("__missing__").astype(str).to_numpy()
    for group in sorted(set(groups)):
        idx = np.where(groups == group)[0]
        if len(idx) < min_group_symbols:
            continue
        sub = signal[idx, :]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            with np.errstate(invalid="ignore", divide="ignore"):
                mean = np.nanmean(sub, axis=0, keepdims=True)
                std = np.nanstd(sub, axis=0, ddof=1, keepdims=True)
                z = (sub - mean) / std
        z[~np.isfinite(z)] = np.nan
        out[idx, :] = z
    return out


def mask_symbols(signal: np.ndarray, include_mask: np.ndarray) -> np.ndarray:
    out = signal.astype(np.float64, copy=True)
    out[~include_mask, :] = np.nan
    return out


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


def alpha_rows(candidate_id: str, variant: str, spread: np.ndarray, split: np.ndarray, label: np.ndarray, symbols: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    benchmarks = []
    for sym in ["BTCUSDT", "ETHUSDT"]:
        if sym in symbols:
            benchmarks.append((sym, label[symbols.index(sym)]))
    for split_name in AUDIT_SPLITS:
        mask_split = split == split_name
        y = spread[mask_split]
        if len(benchmarks) >= 2:
            x1 = benchmarks[0][1][mask_split]
            x2 = benchmarks[1][1][mask_split]
            mask = np.isfinite(y) & np.isfinite(x1) & np.isfinite(x2)
            if mask.sum() >= 20:
                X = np.column_stack([np.ones(mask.sum()), x1[mask], x2[mask]])
                coef, *_ = np.linalg.lstsq(X, y[mask], rcond=None)
                resid = y[mask] - X @ coef
                dof = max(mask.sum() - X.shape[1], 1)
                sigma2 = float((resid @ resid) / dof)
                cov = sigma2 * np.linalg.pinv(X.T @ X)
                se_alpha = math.sqrt(float(cov[0, 0])) if cov[0, 0] > 0 else np.nan
                alpha = float(coef[0])
                alpha_t = float(alpha / se_alpha) if np.isfinite(se_alpha) and se_alpha > 0 else np.nan
                rows.append(
                    {
                        "candidate_id": candidate_id,
                        "variant": variant,
                        "split": split_name,
                        "n_dates": int(mask.sum()),
                        "btc_beta": float(coef[1]),
                        "eth_beta": float(coef[2]),
                        "beta_residual_alpha": alpha,
                        "beta_residual_alpha_tstat": alpha_t,
                        "raw_mean_spread": float(np.nanmean(y[mask])),
                    }
                )
    return rows


def variant_pass_count(split_summary: pd.DataFrame, candidate_id: str, variant: str, use_net: bool = False) -> int:
    part = split_summary[
        split_summary["candidate_id"].eq(candidate_id)
        & split_summary["variant"].eq(variant)
        & split_summary["split"].isin(PRE_MAY_SPLITS)
    ]
    if len(part) != 3:
        return 0
    col = "net_mean_spread_2bps" if use_net else "mean_spread_24h"
    return int(pd.to_numeric(part[col], errors="coerce").gt(0).sum())


def classify_candidates(candidate_meta: pd.DataFrame, split_summary: pd.DataFrame, alpha_summary: pd.DataFrame, control_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    key_variants = [
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
    for _, meta in candidate_meta.iterrows():
        cid = str(meta["candidate_id"])
        pass_variants = []
        net_pass_variants = []
        for variant in key_variants:
            if variant_pass_count(split_summary, cid, variant, use_net=False) >= 3:
                pass_variants.append(variant)
            if variant_pass_count(split_summary, cid, variant, use_net=True) >= 3:
                net_pass_variants.append(variant)
        recent_original = split_summary[
            split_summary["candidate_id"].eq(cid)
            & split_summary["variant"].eq("original")
            & split_summary["split"].eq("recent_oos_2026JanApr")
        ]
        recent_turnover = numeric(recent_original.iloc[0]["avg_one_way_turnover"]) if not recent_original.empty else np.nan
        alpha_recent = alpha_summary[
            alpha_summary["candidate_id"].eq(cid)
            & alpha_summary["variant"].eq("original")
            & alpha_summary["split"].eq("recent_oos_2026JanApr")
        ]
        beta_alpha_recent = numeric(alpha_recent.iloc[0]["beta_residual_alpha"]) if not alpha_recent.empty else np.nan
        control_row = control_summary[control_summary["candidate_id"].eq(cid)]
        control_ratio = numeric(control_row.iloc[0]["control_dominance_ratio_premay_max"]) if not control_row.empty else np.nan

        reasons = []
        if "original" not in pass_variants:
            reasons.append("original_not_all_premay_positive")
        if "one_bar_lag" not in pass_variants:
            reasons.append("one_bar_lag_not_all_premay_positive")
        neutral_count = len([v for v in pass_variants if v.startswith("neutral_") or v.startswith("exclude_")])
        if neutral_count < 3:
            reasons.append("neutralization_survival_weak")
        if len(net_pass_variants) < 2:
            reasons.append("cost_proxy_fragile")
        if np.isfinite(beta_alpha_recent) and beta_alpha_recent <= 0:
            reasons.append("beta_residual_recent_nonpositive")
        if np.isfinite(control_ratio) and control_ratio >= 1.15:
            reasons.append("control_margin_thin")
        if np.isfinite(recent_turnover) and recent_turnover > 1.50:
            reasons.append("high_turnover_proxy")

        warnings_out = []
        if "neutral_dominant_latent_state" not in pass_variants:
            warnings_out.append("dominant_latent_state_proxy_fragile")
        inherited_raw = meta.get("warnings", "")
        inherited_warning = str(inherited_raw) if pd.notna(inherited_raw) else ""
        if inherited_warning and inherited_warning.lower() != "nan":
            warnings_out.append(f"a7al2n:{inherited_warning}")

        if not reasons:
            label = "A7AL2O_MINI_REPLAY_DIAGNOSTIC_PASS"
        elif "control_margin_thin" in reasons:
            label = "HOLD_A7AL2O_CONTROL_MARGIN_THIN"
        elif "neutralization_survival_weak" in reasons:
            label = "HOLD_A7AL2O_NEUTRALIZATION_FRAGILE"
        elif "cost_proxy_fragile" in reasons or "high_turnover_proxy" in reasons:
            label = "HOLD_A7AL2O_COST_TURNOVER_FRAGILE"
        elif "beta_residual_recent_nonpositive" in reasons:
            label = "HOLD_A7AL2O_BETA_RESIDUAL_WEAK"
        else:
            label = "HOLD_A7AL2O_MINI_REPLAY_WEAK"

        rows.append(
            {
                "candidate_id": cid,
                "cell": meta.get("cell"),
                "family": meta.get("family"),
                "field_families": meta.get("field_families"),
                "mini_replay_label": label,
                "reasons": "|".join(reasons),
                "warnings": "|".join(warnings_out),
                "pass_variants": "|".join(pass_variants),
                "net_2bps_pass_variants": "|".join(net_pass_variants),
                "neutralized_pass_variant_count": neutral_count,
                "recent_original_turnover": recent_turnover,
                "recent_beta_residual_alpha": beta_alpha_recent,
                "control_dominance_ratio_premay_max": control_ratio,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = pd.read_csv(A7AL2N_SUMMARY)
    candidates = candidates[candidates["deep_audit_label"].eq("A7AL2N_DEEP_AUDIT_DIAGNOSTIC_PASS")].copy()
    if candidates.empty:
        raise SystemExit("no A7AL-2N diagnostic pass candidates")

    fields = {"trade_close"}
    for text in candidates["fields"].dropna().astype(str):
        fields.update(part for part in text.split("|") if part)
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
    alpha_rows_all: list[dict[str, Any]] = []
    variant_meta_rows: list[dict[str, Any]] = []
    eval_errors: list[dict[str, Any]] = []
    for _, row in candidates.iterrows():
        cid = str(row["candidate_id"])
        expression = str(row["expression"])
        orientation = numeric(row["orientation_from_premay"], -1.0)
        print(f"[A7AL-2O] {cid}", flush=True)
        try:
            base_signal = evaluator.eval(expression)
            variants: dict[str, np.ndarray] = {
                "original": base_signal,
                "one_bar_lag": fast.shift_matrix(base_signal, 1),
                "neutral_liquidity_tier": group_zscore(base_signal, group_values["liquidity_tier"]),
                "neutral_meme_contract_group": group_zscore(base_signal, group_values["meme_contract_group"]),
                "neutral_multiplier_flag": group_zscore(base_signal, group_values["multiplier_flag"]),
                "neutral_major_flag": group_zscore(base_signal, group_values["major_flag"]),
                "neutral_dominant_latent_state": group_zscore(base_signal, group_values["dominant_latent_state"], min_group_symbols=12),
                "exclude_meme": mask_symbols(base_signal, masks["exclude_meme"]),
                "exclude_multiplier": mask_symbols(base_signal, masks["exclude_multiplier"]),
                "exclude_major": mask_symbols(base_signal, masks["exclude_major"]),
            }
            for variant, signal in variants.items():
                weights, spread, top_count, bottom_count = portfolio_weights_and_spread(signal, label)
                oriented_weights = weights * orientation
                oriented_spread = spread * orientation
                split_rows_all.extend(split_rows(cid, variant, oriented_spread, oriented_weights, split, top_count, bottom_count))
                alpha_rows_all.extend(alpha_rows(cid, variant, oriented_spread, split, label, loaded_symbols))
                variant_meta_rows.append(
                    {
                        "candidate_id": cid,
                        "variant": variant,
                        "valid_signal_cells": int(np.isfinite(signal).sum()),
                        "valid_signal_share": float(np.isfinite(signal).mean()),
                    }
                )
        except Exception as exc:
            eval_errors.append({"candidate_id": cid, "error": repr(exc)})

    split_summary = pd.DataFrame(split_rows_all)
    alpha_summary = pd.DataFrame(alpha_rows_all)
    variant_meta = pd.DataFrame(variant_meta_rows)
    control_metrics = pd.read_csv(A7AL2L_VARIANT_METRICS)
    control_pivot = control_metrics[control_metrics["candidate_id"].isin(candidates["candidate_id"].astype(str))].pivot_table(
        index=["candidate_id", "variant"], columns="split", values="mean_spread_24h", aggfunc="first"
    )
    control_rows: list[dict[str, Any]] = []
    for cid in candidates["candidate_id"].astype(str):
        ratios = []
        for split_name in PRE_MAY_SPLITS:
            try:
                original_abs = abs(float(control_pivot.loc[(cid, "original"), split_name]))
            except Exception:
                original_abs = np.nan
            vals = []
            for variant in ["wrong_lag_future_24h", "wrong_lag_stale_168h", "time_shuffle", "symbol_shuffle", "same_family_random"]:
                try:
                    vals.append(abs(float(control_pivot.loc[(cid, variant), split_name])))
                except Exception:
                    pass
            if vals and np.isfinite(original_abs) and original_abs > 0:
                ratios.append(max(vals) / original_abs)
        control_rows.append({"candidate_id": cid, "control_dominance_ratio_premay_max": max(ratios) if ratios else np.nan})
    control_summary = pd.DataFrame(control_rows)
    decisions = classify_candidates(candidates, split_summary, alpha_summary, control_summary)
    decision_counts = decisions["mini_replay_label"].value_counts().rename_axis("mini_replay_label").reset_index(name="count")

    pass_count = int(decisions["mini_replay_label"].eq("A7AL2O_MINI_REPLAY_DIAGNOSTIC_PASS").sum())
    blockers = []
    if eval_errors:
        blockers.append("candidate_eval_errors")
    if pass_count == 0:
        blockers.append("no_candidate_survives_mini_replay")
    decision = "PASS_A7AL2O_MINI_REPLAY_CANDIDATES_READY_FOR_CONTRACT" if pass_count > 0 and not eval_errors else "HOLD_A7AL2O_NO_MINI_REPLAY_SURVIVOR"

    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input": str(A7AL2N_SUMMARY),
        "candidate_count": int(len(candidates)),
        "diagnostic_pass_count": pass_count,
        "decision_counts": {str(r["mini_replay_label"]): int(r["count"]) for _, r in decision_counts.iterrows()},
        "blockers": blockers,
        "eval_errors": len(eval_errors),
        "neutralization_variants": [
            "neutral_liquidity_tier",
            "neutral_meme_contract_group",
            "neutral_multiplier_flag",
            "neutral_major_flag",
            "neutral_dominant_latent_state",
            "exclude_meme",
            "exclude_multiplier",
            "exclude_major",
        ],
        "latent_state_neutralization_note": "dominant_latent_state is a symbol-level proxy because time-varying latent-state panel is not materialized in this audit",
        "cost_proxy_bps": COST_BPS,
        "decision_cost_proxy_bps": 2.0,
        "latency_policy": "field_native_one_bar_lag_no_blanket_plus2h",
        "may_usage": "stress_reporting_only_not_used_for_selection_or_orientation",
        "executes_formula_generation": False,
        "executes_mini_replay": True,
        "executes_alpha_proof": False,
        "authorizes_a7al2p_contract": pass_count > 0 and not eval_errors,
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    split_summary.to_csv(OUT_DIR / "a7al2o_variant_split_summary.csv", index=False)
    alpha_summary.to_csv(OUT_DIR / "a7al2o_beta_residual_alpha.csv", index=False)
    variant_meta.to_csv(OUT_DIR / "a7al2o_variant_validity.csv", index=False)
    control_summary.to_csv(OUT_DIR / "a7al2o_control_margin_recheck.csv", index=False)
    decisions.to_csv(OUT_DIR / "a7al2o_decision_record.csv", index=False)
    pd.DataFrame(eval_errors).to_csv(OUT_DIR / "a7al2o_eval_errors.csv", index=False)
    write_json(OUT_DIR / "a7al2o_manifest.json", manifest)

    key_cols = [
        "candidate_id",
        "cell",
        "family",
        "field_families",
        "mini_replay_label",
        "reasons",
        "warnings",
        "pass_variants",
        "net_2bps_pass_variants",
        "neutralized_pass_variant_count",
        "recent_original_turnover",
        "recent_beta_residual_alpha",
        "control_dominance_ratio_premay_max",
    ]
    display_splits = split_summary[
        split_summary["variant"].isin(["original", "one_bar_lag", "neutral_liquidity_tier", "neutral_dominant_latent_state"])
        & split_summary["split"].isin(PRE_MAY_SPLITS + ["known_may2026_stress"])
    ][
        ["candidate_id", "variant", "split", "mean_spread_24h", "net_mean_spread_2bps", "avg_one_way_turnover", "positive_spread_rate"]
    ]
    report = f"""# CRYPTO A7AL-2O Candidate Mini Replay / Neutralization Audit

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This is a small audit on the four A7AL-2N diagnostic candidates. It tests field-native one-bar lag, group neutralization, exclusion variants, BTC/ETH beta residual alpha, negative-control margin, and turnover/cost proxies. It does not authorize alpha proof, formula-search execution, shadow, paper, or live.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Decision Counts

{md_table(decision_counts, 20)}

## Candidate Decisions

{md_table(decisions[[c for c in key_cols if c in decisions.columns]], 20)}

## Selected Variant Split Metrics

{md_table(display_splits, 80)}

## Boundary

```text
Allowed next step if mini replay passes:
  A7AL-2P small formula-search contract / candidate pool definition.

Not authorized:
  formula search execution
  alpha proof
  shadow / paper / live
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
