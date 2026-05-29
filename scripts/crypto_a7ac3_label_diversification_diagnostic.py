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

from scripts.crypto_a7ab4_materialization_preflight import A7AB4Evaluator, load_numeric_fields, shift_matrix  # noqa: E402
from scripts.crypto_a7ab6_small_numeric_replay_preflight import (  # noqa: E402
    CONTROL_VARIANTS,
    PRE_MAY_SPLITS,
    cs_rank_pct,
    forward_return_label,
    nonoverlap_tstats,
    split_for_timestamps,
    tstat,
    variant_signals,
)
from scripts.crypto_a7al2l_fast_derived_replay_preflight import SPLIT_ORDER  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ac3_label_diversification_diagnostic"
REPORT = REPO / "reports" / "CRYPTO_A7AC3_LABEL_DIVERSIFICATION_DIAGNOSTIC_20260529.md"

A7AC2_MANIFEST = REPO / "runtime" / "a7ac2_label_diversification_contract" / "a7ac2_manifest.json"
A7AC2_SUBSET = REPO / "runtime" / "a7ac2_label_diversification_contract" / "a7ac2_diagnostic_subset_input.csv"
A7AB8_CLUE_AUG = REPO / "runtime" / "a7ab8_clue_forensic_execution" / "a7ab8_clue_augmented.csv"
A7AB3_SELECTED = REPO / "runtime" / "a7ab3_seed_constrained_dry_generation" / "a7ab3_static_selected_queue.csv"
SYMBOL_CLASSIFICATION = REPO / "runtime" / "a7al_universe498_replay_acceptance" / "a7am_symbol_classification.csv"
MEME_TAXONOMY = REPO / "runtime" / "a7ak_lv3r_contract_meme_taxonomy_audit" / "a7ak_lv3r_contract_meme_taxonomy.csv"
LATENT_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_latent_state_features_v1_20260527.parquet")

LABELS = ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L7_ranked_future_return"]
HORIZONS = [1, 4]
MODES = ["global_rank", "liquidity_tier_neutral", "meme_multiplier_neutral"]
MIN_ACTIVE_SYMBOLS = 30
MIN_GROUP_SYMBOLS = 8


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 100) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def split_pipe(value: Any) -> list[str]:
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]


def selected_fields(detail: pd.DataFrame) -> set[str]:
    fields = {"trade_close"}
    for text in detail["source_fields"].dropna().astype(str):
        fields.update(split_pipe(text))
    return fields


def label_matrix(label_family: str, horizon: int, trade_close: np.ndarray, timestamps: pd.DatetimeIndex, split: np.ndarray) -> np.ndarray:
    raw = forward_return_label(trade_close, timestamps, split, horizon)
    if label_family == "L0_raw_forward_return":
        return raw
    if label_family == "L1_cross_sectional_relative_return":
        with np.errstate(invalid="ignore"):
            mean = np.nanmean(raw, axis=0, keepdims=True)
        return raw - mean
    if label_family == "L7_ranked_future_return":
        return cs_rank_pct(raw) - 0.5
    raise ValueError(f"unsupported label family: {label_family}")


def spread_global(signal: np.ndarray, label: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    valid = np.isfinite(signal) & np.isfinite(label)
    counts = valid.sum(axis=0)
    enough = counts >= MIN_ACTIVE_SYMBOLS
    sig = np.where(valid, signal, np.nan)
    ranks = pd.DataFrame(sig).rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)
    top = valid & enough.reshape(1, -1) & (ranks >= 0.90)
    bottom = valid & enough.reshape(1, -1) & (ranks <= 0.10)
    spread = np.full(signal.shape[1], np.nan)
    top_count = top.sum(axis=0)
    bottom_count = bottom.sum(axis=0)
    ok = (top_count > 0) & (bottom_count > 0)
    spread[ok] = (
        np.where(top, label, 0.0).sum(axis=0)[ok] / top_count[ok]
        - np.where(bottom, label, 0.0).sum(axis=0)[ok] / bottom_count[ok]
    )
    return spread, counts


def spread_static_group_neutral(signal: np.ndarray, label: np.ndarray, group: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n_times = signal.shape[1]
    spread_sum = np.zeros(n_times, dtype=np.float64)
    weight_sum = np.zeros(n_times, dtype=np.float64)
    for group_value in pd.unique(pd.Series(group).astype(str)):
        idx = group.astype(str) == str(group_value)
        if int(idx.sum()) < MIN_GROUP_SYMBOLS:
            continue
        sig = signal[idx, :]
        lab = label[idx, :]
        valid = np.isfinite(sig) & np.isfinite(lab)
        counts = valid.sum(axis=0)
        enough = counts >= MIN_GROUP_SYMBOLS
        ranks = pd.DataFrame(np.where(valid, sig, np.nan)).rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)
        top = valid & enough.reshape(1, -1) & (ranks >= 0.80)
        bottom = valid & enough.reshape(1, -1) & (ranks <= 0.20)
        top_count = top.sum(axis=0)
        bottom_count = bottom.sum(axis=0)
        ok = (top_count > 0) & (bottom_count > 0)
        group_spread = np.full(n_times, np.nan)
        group_spread[ok] = (
            np.where(top, lab, 0.0).sum(axis=0)[ok] / top_count[ok]
            - np.where(bottom, lab, 0.0).sum(axis=0)[ok] / bottom_count[ok]
        )
        weights = counts.astype(np.float64)
        finite = np.isfinite(group_spread)
        spread_sum[finite] += group_spread[finite] * weights[finite]
        weight_sum[finite] += weights[finite]
    spread = np.full(n_times, np.nan)
    ok = weight_sum > 0
    spread[ok] = spread_sum[ok] / weight_sum[ok]
    return spread, weight_sum


def spread_group_neutral(signal: np.ndarray, label: np.ndarray, group: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if group.ndim == 1:
        return spread_static_group_neutral(signal, label, group)
    n_symbols, n_times = signal.shape
    spread = np.full(n_times, np.nan)
    counts = np.zeros(n_times, dtype=np.float64)
    for t in range(n_times):
        sig_t = signal[:, t]
        lab_t = label[:, t]
        grp_t = group[:, t] if group.ndim == 2 else group
        valid = np.isfinite(sig_t) & np.isfinite(lab_t) & pd.notna(grp_t)
        if int(valid.sum()) < MIN_ACTIVE_SYMBOLS:
            continue
        group_spreads: list[float] = []
        group_weights: list[int] = []
        for g in pd.unique(pd.Series(grp_t[valid]).astype(str)):
            idx = valid & (grp_t.astype(str) == g)
            if int(idx.sum()) < MIN_GROUP_SYMBOLS:
                continue
            ranks = pd.Series(sig_t[idx]).rank(pct=True, method="average").to_numpy(dtype=np.float64)
            top = ranks >= 0.80
            bottom = ranks <= 0.20
            if not top.any() or not bottom.any():
                continue
            values = lab_t[idx]
            group_spreads.append(float(np.nanmean(values[top]) - np.nanmean(values[bottom])))
            group_weights.append(int(idx.sum()))
        if group_spreads:
            weights = np.asarray(group_weights, dtype=np.float64)
            spread[t] = float(np.average(np.asarray(group_spreads, dtype=np.float64), weights=weights))
            counts[t] = float(np.sum(weights))
    return spread, counts


def summarize_spread(
    candidate_id: str,
    label_family: str,
    horizon: int,
    mode: str,
    variant: str,
    spread: np.ndarray,
    counts: np.ndarray,
    split: np.ndarray,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split_name in SPLIT_ORDER:
        mask = (split == split_name) & np.isfinite(spread)
        x = spread[mask]
        med_t, min_t = nonoverlap_tstats(spread, split == split_name, horizon=horizon)
        rows.append(
            {
                "candidate_id": candidate_id,
                "label_family": label_family,
                "horizon_h": horizon,
                "neutralization_mode": mode,
                "variant": variant,
                "split": split_name,
                "n_dates": int(mask.sum()),
                "avg_n_obs": float(np.nanmean(counts[mask])) if mask.any() else np.nan,
                "mean_spread": float(np.nanmean(x)) if len(x) else np.nan,
                "spread_tstat": tstat(x) if len(x) else np.nan,
                "nonoverlap_median_tstat": med_t,
                "nonoverlap_min_tstat": min_t,
                "positive_rate": float(np.nanmean(x > 0)) if len(x) else np.nan,
            }
        )
    return rows


def static_group_matrix(symbols: list[str], source: pd.DataFrame, column: str, default: str = "missing") -> np.ndarray:
    mapping = source.set_index("symbol")[column].astype(str).to_dict()
    values = np.asarray([mapping.get(symbol, default) for symbol in symbols], dtype=object)
    return values


def latent_group_matrix(symbols: list[str], timestamps: pd.DatetimeIndex) -> tuple[np.ndarray | None, str]:
    if not LATENT_PANEL.exists():
        return None, "missing_latent_panel"
    latent = pd.read_parquet(LATENT_PANEL, columns=["symbol", "timestamp", "raw_latent_state_id"])
    latent["timestamp"] = pd.to_datetime(latent["timestamp"], utc=True)
    need = pd.MultiIndex.from_product([symbols, timestamps], names=["symbol", "timestamp"]).to_frame(index=False)
    merged = need.merge(latent, on=["symbol", "timestamp"], how="left")
    arr = merged["raw_latent_state_id"].fillna("latent_missing").astype(str).to_numpy(dtype=object)
    return arr.reshape(len(symbols), len(timestamps)), "loaded"


def classify(metrics: pd.DataFrame, candidate_id: str, label_family: str, horizon: int, mode: str) -> dict[str, Any]:
    sub = metrics[
        metrics["candidate_id"].astype(str).eq(candidate_id)
        & metrics["label_family"].astype(str).eq(label_family)
        & metrics["horizon_h"].astype(int).eq(int(horizon))
        & metrics["neutralization_mode"].astype(str).eq(mode)
    ]
    pivot = sub.pivot_table(index="variant", columns="split", values="mean_spread", aggfunc="first")
    tstats = sub.pivot_table(index="variant", columns="split", values="nonoverlap_min_tstat", aggfunc="first")

    def v(variant: str, split_name: str) -> float:
        try:
            return float(pivot.loc[variant, split_name])
        except Exception:
            return np.nan

    def no_t(variant: str, split_name: str) -> float:
        try:
            return float(tstats.loc[variant, split_name])
        except Exception:
            return np.nan

    train = v("original", "train_2024")
    orientation = 1.0 if not np.isfinite(train) or train >= 0 else -1.0
    oriented = {split_name: orientation * v("original", split_name) for split_name in PRE_MAY_SPLITS}
    no_min = {split_name: orientation * no_t("original", split_name) for split_name in PRE_MAY_SPLITS}
    premay_positive = all(np.isfinite(value) and value > 0 for value in oriented.values())
    nonoverlap_positive = all(np.isfinite(value) and value > 0 for value in no_min.values())
    recent = oriented["recent_oos_2026JanApr"]
    lag_recent = orientation * v("one_bar_lag", "recent_oos_2026JanApr")
    lag_ok = bool(np.isfinite(recent) and np.isfinite(lag_recent) and lag_recent > 0 and abs(lag_recent) >= 0.25 * abs(recent))
    ratios: list[float] = []
    for split_name in PRE_MAY_SPLITS:
        original_abs = abs(v("original", split_name))
        vals = [abs(v(control, split_name)) for control in CONTROL_VARIANTS if control != "one_bar_lag"]
        vals = [value for value in vals if np.isfinite(value)]
        if vals and np.isfinite(original_abs) and original_abs > 1e-12:
            ratios.append(max(vals) / original_abs)
    control_ratio = max(ratios) if ratios else np.nan
    control_clean = bool(np.isfinite(control_ratio) and control_ratio < 1.0)

    blockers: list[str] = []
    warnings: list[str] = []
    if not premay_positive:
        blockers.append("premay_spread_nonpositive")
    if not nonoverlap_positive:
        blockers.append("nonoverlap_tstat_not_positive")
    if not control_clean:
        blockers.append("control_ratio_ge_1")
    elif control_ratio >= 0.80:
        warnings.append("control_ratio_warning_ge_0_80")
    if not lag_ok:
        blockers.append("one_bar_lag_fail")
    if label_family == "L7_ranked_future_return":
        warnings.append("ranked_return_label")
    if mode != "global_rank":
        warnings.append("neutralized_mode")
    if blockers:
        decision = "HOLD_A7AC3_LABEL_OR_NEUTRALIZATION_BLOCKED"
    elif warnings:
        decision = "A7AC3_LABEL_NEUTRALIZATION_PASS_WITH_WARNINGS"
    else:
        decision = "A7AC3_LABEL_NEUTRALIZATION_PASS"
    return {
        "candidate_id": candidate_id,
        "label_family": label_family,
        "horizon_h": int(horizon),
        "neutralization_mode": mode,
        "orientation_from_train": orientation,
        "oriented_validation_spread": oriented["validation_2025H1"],
        "oriented_test_spread": oriented["test_2025H2"],
        "oriented_recent_spread": recent,
        "one_bar_lag_recent_oriented": lag_recent,
        "control_ratio_premay_max": control_ratio,
        "min_oriented_nonoverlap_min_tstat": min(no_min.values()) if no_min else np.nan,
        "decision": decision,
        "blockers": ";".join(blockers) if blockers else "none",
        "warnings": ";".join(warnings) if warnings else "none",
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ac2 = read_json(A7AC2_MANIFEST)
    if not a7ac2.get("authorizes_a7ac3_label_diversification_diagnostic"):
        raise SystemExit("A7AC-2 does not authorize A7AC-3")

    subset = pd.read_csv(A7AC2_SUBSET)
    clue_aug = pd.read_csv(A7AB8_CLUE_AUG).drop_duplicates("candidate_id")
    selected = pd.read_csv(A7AB3_SELECTED).drop_duplicates("candidate_id")
    details = subset[["candidate_id"]].drop_duplicates().merge(clue_aug, on="candidate_id", how="left")
    details = details.merge(
        selected[["candidate_id", "source_fields", "production_key", "motif"]],
        on="candidate_id",
        how="left",
    )
    if details["expression"].isna().any():
        missing = details.loc[details["expression"].isna(), "candidate_id"].tolist()
        raise SystemExit(f"missing expressions for candidates: {missing}")
    fields = selected_fields(details)
    symbols, timestamps, numeric, missing_fields, full_timestamp_count = load_numeric_fields(fields, timestamp_cap=None)
    if missing_fields:
        raise SystemExit(f"missing numeric fields: {missing_fields}")
    split = split_for_timestamps(timestamps)
    evaluator = A7AB4Evaluator(numeric, {})
    rng = np.random.default_rng(20260529)

    classification = pd.read_csv(SYMBOL_CLASSIFICATION)
    meme = pd.read_csv(MEME_TAXONOMY)
    liquidity_group = static_group_matrix(symbols, classification, "liquidity_tier")
    meme_group = static_group_matrix(symbols, meme, "meme_contract_group")
    latent_group = None
    latent_status = "deferred_dynamic_latent_neutralization_not_run_in_A7AC3"
    group_inputs: dict[str, np.ndarray | None] = {
        "global_rank": None,
        "liquidity_tier_neutral": liquidity_group,
        "meme_multiplier_neutral": meme_group,
    }

    labels = {
        (label_family, horizon): label_matrix(label_family, horizon, numeric["trade_close"], timestamps, split)
        for label_family in LABELS
        for horizon in HORIZONS
    }
    metric_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(details.to_dict("records"), start=1):
        cid = str(row["candidate_id"])
        signal = evaluator.eval(str(row["expression"]))
        variants = variant_signals(signal, rng)
        for (label_family, horizon), label in labels.items():
            for mode in MODES:
                group = group_inputs.get(mode)
                if mode != "global_rank" and group is None:
                    continue
                for variant, variant_signal in variants.items():
                    if mode == "global_rank":
                        spread, counts = spread_global(variant_signal, label)
                    else:
                        spread, counts = spread_group_neutral(variant_signal, label, group)  # type: ignore[arg-type]
                    metric_rows.extend(summarize_spread(cid, label_family, horizon, mode, variant, spread, counts, split))
        print(f"[A7AC-3] evaluated {idx}/{len(details)}", flush=True)

    metrics = pd.DataFrame(metric_rows)
    decision_rows: list[dict[str, Any]] = []
    for cid in details["candidate_id"].astype(str).tolist():
        for label_family in LABELS:
            for horizon in HORIZONS:
                for mode in MODES:
                    if mode == "latent_state_neutral" and latent_group is None:
                        continue
                    decision_rows.append(classify(metrics, cid, label_family, horizon, mode))
    decisions = pd.DataFrame(decision_rows)
    pass_rows = decisions[decisions["decision"].ne("HOLD_A7AC3_LABEL_OR_NEUTRALIZATION_BLOCKED")].copy()
    non_rank_pass = pass_rows[pass_rows["label_family"].ne("L7_ranked_future_return")]
    neutral_pass = pass_rows[pass_rows["neutralization_mode"].ne("global_rank")]
    decision_counts = decisions["decision"].value_counts().rename_axis("decision").reset_index(name="count")
    label_mode_summary = (
        decisions.groupby(["label_family", "neutralization_mode"], as_index=False)
        .agg(
            rows=("candidate_id", "count"),
            pass_rows=("decision", lambda x: int((x != "HOLD_A7AC3_LABEL_OR_NEUTRALIZATION_BLOCKED").sum())),
            candidates=("candidate_id", "nunique"),
            pass_candidates=("candidate_id", lambda x: int(decisions.loc[x.index][decisions.loc[x.index, "decision"].ne("HOLD_A7AC3_LABEL_OR_NEUTRALIZATION_BLOCKED")]["candidate_id"].nunique())),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .sort_values(["pass_rows", "rows"], ascending=[False, False])
    )
    candidate_summary = (
        pass_rows.groupby("candidate_id", as_index=False)
        .agg(
            pass_rows=("decision", "count"),
            label_families=("label_family", "nunique"),
            neutralization_modes=("neutralization_mode", "nunique"),
            non_rank_pass_rows=("label_family", lambda x: int((x != "L7_ranked_future_return").sum())),
        )
        .sort_values(["non_rank_pass_rows", "pass_rows"], ascending=[False, False])
        if not pass_rows.empty
        else pd.DataFrame()
    )

    non_rank_candidates = int(non_rank_pass["candidate_id"].nunique()) if not non_rank_pass.empty else 0
    neutral_candidates = int(neutral_pass["candidate_id"].nunique()) if not neutral_pass.empty else 0
    if non_rank_candidates >= 2 and neutral_candidates >= 2:
        decision = "PASS_A7AC3_LABEL_DIVERSIFICATION_DIAGNOSTIC_READY_FOR_A7AC4"
        authorizes_a7ac4 = True
    elif non_rank_candidates > 0 or neutral_candidates > 0:
        decision = "HOLD_A7AC3_PARTIAL_LABEL_DIVERSIFICATION"
        authorizes_a7ac4 = False
    else:
        decision = "HOLD_A7AC3_L7_ONLY_LABEL_ARTIFACT_RISK"
        authorizes_a7ac4 = False

    manifest = {
        "stage": "A7AC-3",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_label_diagnostic": True,
        "executes_formula_generation": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may": False,
        "input_a7ac2_decision": a7ac2.get("decision"),
        "candidate_count": int(details["candidate_id"].nunique()),
        "symbols_loaded": int(len(symbols)),
        "timestamps": int(len(timestamps)),
        "full_timestamps_before_subset": int(full_timestamp_count),
        "labels": LABELS,
        "horizons": HORIZONS,
        "neutralization_modes": MODES,
        "latent_group_status": latent_status,
        "metric_rows": int(len(metrics)),
        "decision_counts": {str(r["decision"]): int(r["count"]) for _, r in decision_counts.iterrows()},
        "pass_rows": int(len(pass_rows)),
        "non_rank_pass_candidates": non_rank_candidates,
        "neutralized_pass_candidates": neutral_candidates,
        "authorizes_a7ac4_neutralized_representative_contract": authorizes_a7ac4,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    experiment_record = {
        "date": "2026-05-29",
        "experiment_id": "20260529_a7ac3_label_diversification_diagnostic",
        "objective": "Test whether A7AC-1R representatives survive non-ranked labels and neutralization modes.",
        "status": "completed",
        "mode": "light_diagnostic",
        "inputs": {
            "a7ac2_manifest": str(A7AC2_MANIFEST),
            "a7ac2_subset": str(A7AC2_SUBSET),
            "a7ab8_clue_augmented": str(A7AB8_CLUE_AUG),
            "symbol_classification": str(SYMBOL_CLASSIFICATION),
            "meme_taxonomy": str(MEME_TAXONOMY),
            "latent_panel": str(LATENT_PANEL),
        },
        "parameters": {
            "labels": LABELS,
            "horizons": HORIZONS,
            "neutralization_modes": MODES,
            "min_active_symbols": MIN_ACTIVE_SYMBOLS,
            "min_group_symbols": MIN_GROUP_SYMBOLS,
            "May_usage": "not used",
        },
        "outputs": {"runtime": str(RUNTIME), "report": str(REPORT)},
        "decision": decision,
        "next_action": "A7AC-4 neutralized representative contract" if authorizes_a7ac4 else "HOLD; do not expand formula search",
    }

    metrics.to_csv(RUNTIME / "a7ac3_label_neutralization_metrics.csv", index=False)
    decisions.to_csv(RUNTIME / "a7ac3_label_neutralization_decisions.csv", index=False)
    pass_rows.to_csv(RUNTIME / "a7ac3_pass_rows.csv", index=False)
    non_rank_pass.to_csv(RUNTIME / "a7ac3_non_rank_pass_rows.csv", index=False)
    neutral_pass.to_csv(RUNTIME / "a7ac3_neutralized_pass_rows.csv", index=False)
    label_mode_summary.to_csv(RUNTIME / "a7ac3_label_mode_summary.csv", index=False)
    candidate_summary.to_csv(RUNTIME / "a7ac3_candidate_summary.csv", index=False)
    decision_counts.to_csv(RUNTIME / "a7ac3_decision_counts.csv", index=False)
    write_json(RUNTIME / "a7ac3_manifest.json", manifest)
    write_json(RUNTIME / "a7ac3_experiment_record.json", experiment_record)
    write_json(
        RUNTIME / "a7ac3_authorization_matrix.json",
        {
            "A7AC-3": {"status": decision},
            "A7AC-4_neutralized_representative_contract": {"authorized": authorizes_a7ac4},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AC-3 LABEL DIVERSIFICATION DIAGNOSTIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AC-3 evaluates A7AC-1R representatives across required labels and neutralization modes. It does not generate formulas, train, search, or authorize alpha proof, shadow, paper, or live.",
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
        "## Label / Neutralization Summary",
        "",
        md_table(label_mode_summary, 100),
        "",
        "## Candidate Summary",
        "",
        md_table(candidate_summary, 80),
        "",
        "## Non-Ranked Pass Rows",
        "",
        md_table(non_rank_pass, 80),
        "",
        "## Neutralized Pass Rows",
        "",
        md_table(neutral_pass, 80),
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
