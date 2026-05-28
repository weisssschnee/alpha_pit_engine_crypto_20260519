from __future__ import annotations

import importlib.util
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

Q_SCRIPT = REPO / "scripts" / "crypto_a7al2q_local_oi_price_formula_search.py"
P0_SCRIPT = REPO / "scripts" / "crypto_a7al2p0_pre_search_hardening_audit.py"
Q_MANIFEST = REPO / "runtime" / "a7al2q_local_oi_price_formula_search" / "a7al2q_manifest.json"
Q_SCOREBOARD = REPO / "runtime" / "a7al2q_local_oi_price_formula_search" / "a7al2q_deep_audit_scoreboard.csv"
OUT_DIR = REPO / "runtime" / "a7al2r_local_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7AL2R_LOCAL_FORENSIC_20260528.md"

PRE_MAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
AUDIT_SPLITS = PRE_MAY_SPLITS + ["known_may2026_stress"]
CONTROL_VARIANTS = [
    "wrong_lag_future_24h",
    "wrong_lag_stale_168h",
    "same_family_random",
    "time_shuffle",
    "symbol_shuffle",
]
COST_BPS = [2.0, 5.0, 10.0]


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


q = load_module("a7al2q_for_r", Q_SCRIPT)
p0 = load_module("a7al2p0_for_r", P0_SCRIPT)
fast = q.fast


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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


def finite_tstat(x: np.ndarray) -> float:
    return q.finite_tstat(x)


def split_metric_rows(
    candidate_id: str,
    variant: str,
    entry_label: str,
    spread: np.ndarray,
    weights: np.ndarray,
    split: np.ndarray,
    orientation: float,
    top_count: np.ndarray,
    bottom_count: np.ndarray,
) -> list[dict[str, Any]]:
    return q.split_metric_rows(candidate_id, variant, entry_label, spread, weights, split, orientation, top_count, bottom_count)


def contribution_tables(
    candidate_id: str,
    weights: np.ndarray,
    label: np.ndarray,
    split: np.ndarray,
    timestamps: pd.DatetimeIndex,
    symbols: list[str],
    state_matrix: np.ndarray,
    orientation: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    pnl = weights * label * orientation
    symbol_rows: list[dict[str, Any]] = []
    month_rows: list[dict[str, Any]] = []
    latent_rows: list[dict[str, Any]] = []
    hour_rows: list[dict[str, Any]] = []
    months = pd.Series(timestamps).dt.strftime("%Y-%m").to_numpy()
    for split_name in AUDIT_SPLITS:
        mask = (split == split_name) & np.isfinite(np.nansum(pnl, axis=0))
        if not mask.any():
            continue
        sym_abs = np.nansum(np.abs(pnl[:, mask]), axis=1)
        total_abs = float(np.nansum(sym_abs))
        if total_abs > 0:
            order = np.argsort(-sym_abs)[:10]
            for rank, idx in enumerate(order, start=1):
                symbol_rows.append(
                    {
                        "candidate_id": candidate_id,
                        "split": split_name,
                        "rank": rank,
                        "symbol": symbols[idx],
                        "abs_contribution": float(sym_abs[idx]),
                        "abs_contribution_share": float(sym_abs[idx] / total_abs),
                    }
                )
        month_values = []
        for month in sorted(set(months[mask])):
            m = mask & (months == month)
            month_values.append((month, float(np.nansum(np.abs(np.nansum(pnl[:, m], axis=0))))))
        month_total = sum(v for _, v in month_values)
        for rank, (month, value) in enumerate(sorted(month_values, key=lambda x: -x[1])[:12], start=1):
            month_rows.append(
                {
                    "candidate_id": candidate_id,
                    "split": split_name,
                    "rank": rank,
                    "month": month,
                    "abs_spread_contribution": value,
                    "abs_contribution_share": float(value / month_total) if month_total > 0 else np.nan,
                }
            )
        state_contrib: dict[str, float] = {}
        cols = np.where(mask)[0]
        for col in cols:
            states = state_matrix[:, col].astype(str)
            vals = np.abs(pnl[:, col])
            finite = np.isfinite(vals)
            for state in set(states[finite]):
                state_contrib[state] = state_contrib.get(state, 0.0) + float(np.nansum(vals[finite & (states == state)]))
        state_total = sum(state_contrib.values())
        for rank, (state, value) in enumerate(sorted(state_contrib.items(), key=lambda x: -x[1])[:12], start=1):
            latent_rows.append(
                {
                    "candidate_id": candidate_id,
                    "split": split_name,
                    "rank": rank,
                    "raw_latent_state_id": state,
                    "abs_contribution": value,
                    "abs_contribution_share": float(value / state_total) if state_total > 0 else np.nan,
                }
            )
        spread = np.nansum(pnl, axis=0)
        valid_idx = np.where(mask & np.isfinite(spread))[0]
        if len(valid_idx):
            worst = valid_idx[np.argsort(spread[valid_idx])[:10]]
            best = valid_idx[np.argsort(-spread[valid_idx])[:10]]
            for rank, col in enumerate(worst, start=1):
                hour_rows.append(
                    {
                        "candidate_id": candidate_id,
                        "split": split_name,
                        "side": "loss",
                        "rank": rank,
                        "timestamp": timestamps[col].isoformat(),
                        "spread": float(spread[col]),
                    }
                )
            for rank, col in enumerate(best, start=1):
                hour_rows.append(
                    {
                        "candidate_id": candidate_id,
                        "split": split_name,
                        "side": "gain",
                        "rank": rank,
                        "timestamp": timestamps[col].isoformat(),
                        "spread": float(spread[col]),
                    }
                )
    return symbol_rows, month_rows, latent_rows, hour_rows


def control_ratio_by_split(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (cid, entry_label, split_name), group in metrics.groupby(["candidate_id", "entry_label", "split"], dropna=False):
        try:
            original_abs = abs(float(group.loc[group["variant"].eq("original"), "mean_oriented_spread"].iloc[0]))
        except Exception:
            original_abs = np.nan
        controls = group[group["variant"].isin(CONTROL_VARIANTS)].copy()
        max_control_abs = float(controls["mean_oriented_spread"].abs().max()) if not controls.empty else np.nan
        ratio = max_control_abs / original_abs if np.isfinite(original_abs) and original_abs > 0 and np.isfinite(max_control_abs) else np.nan
        if np.isfinite(ratio) and ratio >= 1.0:
            gate = "HOLD_CONTROL_DOMINATED"
        elif np.isfinite(ratio) and ratio >= 0.8:
            gate = "WARN_CONTROL_CLOSE"
        else:
            gate = "ELIGIBLE_DIAGNOSTIC"
        rows.append(
            {
                "candidate_id": cid,
                "entry_label": entry_label,
                "split": split_name,
                "original_abs_spread": original_abs,
                "max_control_abs_spread": max_control_abs,
                "control_ratio": ratio,
                "gate": gate,
            }
        )
    return pd.DataFrame(rows)


def positive_count(metrics: pd.DataFrame, candidate_id: str, variant: str, entry_label: str, col: str = "mean_oriented_spread") -> int:
    part = metrics[
        metrics["candidate_id"].eq(candidate_id)
        & metrics["variant"].eq(variant)
        & metrics["entry_label"].eq(entry_label)
        & metrics["split"].isin(PRE_MAY_SPLITS)
    ]
    if len(part) != 3:
        return 0
    return int(pd.to_numeric(part[col], errors="coerce").gt(0).sum())


def classify(
    candidates: pd.DataFrame,
    metrics: pd.DataFrame,
    control_gate: pd.DataFrame,
    latent_metrics: pd.DataFrame,
    symbol_contrib: pd.DataFrame,
    month_contrib: pd.DataFrame,
    latent_contrib: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for _, row in candidates.iterrows():
        cid = str(row["candidate_id"])
        reasons: list[str] = []
        warnings_out: list[str] = []
        label_t1_pos = positive_count(metrics, cid, "original", "label_t1_to_t25")
        label_t2_pos = positive_count(metrics, cid, "original", "label_t2_to_t26")
        lag_pos = positive_count(metrics, cid, "one_bar_lag", "label_t1_to_t25")
        latent_pos = positive_count(latent_metrics, cid, "timevarying_latent_state_neutral", "label_t1_to_t25")
        cost10_pos = positive_count(metrics, cid, "original", "label_t1_to_t25", "net_mean_spread_10bps")
        cpart = control_gate[
            control_gate["candidate_id"].eq(cid)
            & control_gate["entry_label"].eq("label_t1_to_t25")
            & control_gate["split"].isin(PRE_MAY_SPLITS)
        ]
        max_control_ratio = float(cpart["control_ratio"].max()) if len(cpart) else np.nan
        pre_symbol = symbol_contrib[symbol_contrib["candidate_id"].eq(cid) & symbol_contrib["split"].isin(PRE_MAY_SPLITS)] if not symbol_contrib.empty else pd.DataFrame()
        pre_month = month_contrib[month_contrib["candidate_id"].eq(cid) & month_contrib["split"].isin(PRE_MAY_SPLITS)] if not month_contrib.empty else pd.DataFrame()
        pre_latent = latent_contrib[latent_contrib["candidate_id"].eq(cid) & latent_contrib["split"].isin(PRE_MAY_SPLITS)] if not latent_contrib.empty else pd.DataFrame()
        top_symbol_share = float(pre_symbol["abs_contribution_share"].max()) if not pre_symbol.empty else np.nan
        top_month_share = float(pre_month["abs_contribution_share"].max()) if not pre_month.empty else np.nan
        top_latent_share = float(pre_latent["abs_contribution_share"].max()) if not pre_latent.empty else np.nan
        if label_t1_pos < 3:
            reasons.append("label_t1_not_all_premay_positive")
        if label_t2_pos < 3:
            reasons.append("label_t2_not_all_premay_positive")
        if lag_pos < 3:
            reasons.append("one_bar_lag_fragile")
        if latent_pos < 3:
            reasons.append("timevarying_latent_fragile")
        if cost10_pos < 3:
            reasons.append("cost10_fragile")
        if np.isfinite(max_control_ratio) and max_control_ratio >= 1.0:
            reasons.append("control_dominated")
        elif np.isfinite(max_control_ratio) and max_control_ratio >= 0.8:
            warnings_out.append("control_close")
        if np.isfinite(top_symbol_share) and top_symbol_share > 0.35:
            reasons.append("symbol_concentration")
        if np.isfinite(top_month_share) and top_month_share > 0.40:
            reasons.append("month_concentration")
        if np.isfinite(top_latent_share) and top_latent_share > 0.35:
            reasons.append("latent_concentration")
        if not reasons:
            decision = "A7AL2R_LOCAL_FORENSIC_PASS"
        elif "control_dominated" in reasons:
            decision = "HOLD_A7AL2R_CONTROL_DOMINATED"
        elif "timevarying_latent_fragile" in reasons:
            decision = "HOLD_A7AL2R_LATENT_FRAGILE"
        elif any(x in reasons for x in ["symbol_concentration", "month_concentration", "latent_concentration"]):
            decision = "HOLD_A7AL2R_CONCENTRATION_FAIL"
        elif any(x in reasons for x in ["one_bar_lag_fragile", "cost10_fragile"]):
            decision = "HOLD_A7AL2R_LATENCY_OR_COST_FAIL"
        else:
            decision = "HOLD_A7AL2R_WEAK_OR_INCONSISTENT"
        rows.append(
            {
                "candidate_id": cid,
                "decision": decision,
                "reasons": "|".join(reasons),
                "warnings": "|".join(warnings_out),
                "label_t1_positive_premay_splits": label_t1_pos,
                "label_t2_positive_premay_splits": label_t2_pos,
                "one_bar_lag_positive_premay_splits": lag_pos,
                "latent_positive_premay_splits": latent_pos,
                "net_10bps_positive_premay_splits": cost10_pos,
                "control_ratio_premay_max": max_control_ratio,
                "top_symbol_abs_contribution_share": top_symbol_share,
                "top_month_abs_contribution_share": top_month_share,
                "top_latent_abs_contribution_share": top_latent_share,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    q_manifest = read_json(Q_MANIFEST)
    if not q_manifest.get("authorizes_a7al2r_local_forensic"):
        raise SystemExit("A7AL-2Q does not authorize A7AL-2R local forensic")
    scoreboard = pd.read_csv(Q_SCOREBOARD)
    candidates = scoreboard[scoreboard["decision"].eq("A7AL2Q_LOCAL_OI_PRICE_DIAGNOSTIC_CANDIDATE")].copy()
    ids_env = [x.strip() for x in os.environ.get("A7AL2R_CANDIDATE_IDS", "").split(",") if x.strip()]
    if ids_env:
        candidates = candidates[candidates["candidate_id"].astype(str).isin(ids_env)].copy()
    cap = int(os.environ.get("A7AL2R_CANDIDATE_CAP", str(len(candidates))) or str(len(candidates)))
    candidates = candidates.head(max(1, min(cap, len(candidates)))).reset_index(drop=True)
    if candidates.empty:
        raise SystemExit("No A7AL-2Q diagnostic candidates available for A7AL-2R")

    fields = {"trade_close"}
    for text in candidates["fields"].astype(str):
        fields.update(part for part in text.split("|") if part)
    symbols = fast.strict_symbols()
    loaded_symbols, timestamps, matrices = fast.load_panel_matrices(symbols, fields)
    split = fast.split_for_timestamps(timestamps)
    labels = {
        "label_t1_to_t25": p0.label_matrix_entry_shift(matrices["trade_close"], timestamps, split, 1),
        "label_t2_to_t26": p0.label_matrix_entry_shift(matrices["trade_close"], timestamps, split, 2),
    }
    components = q.precompute_components(matrices, candidates)
    state_matrix, latent_coverage = p0.load_timevarying_latent_states(loaded_symbols, timestamps)
    rng = np.random.default_rng(20260528)

    metric_rows: list[dict[str, Any]] = []
    latent_metric_rows: list[dict[str, Any]] = []
    overlap_rows: list[dict[str, Any]] = []
    nonoverlap_rows: list[dict[str, Any]] = []
    symbol_rows: list[dict[str, Any]] = []
    month_rows: list[dict[str, Any]] = []
    latent_contrib_rows: list[dict[str, Any]] = []
    top_hour_rows: list[dict[str, Any]] = []
    orientation_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for idx, row in candidates.iterrows():
        cid = str(row["candidate_id"])
        print(f"[A7AL-2R] {idx + 1}/{len(candidates)} {cid}", flush=True)
        try:
            base_signal = q.eval_local_signal(row, components)
            orientation, train_mean = q.fit_train_orientation(base_signal, labels["label_t1_to_t25"], split)
            orientation_rows.append(
                {
                    "candidate_id": cid,
                    "orientation_fit_split": "train_2024",
                    "orientation_entry_label": "label_t1_to_t25",
                    "train_mean_spread": train_mean,
                    "orientation": orientation,
                    "uses_may": False,
                }
            )
            variants = {
                "original": base_signal,
                "one_bar_lag": fast.shift_matrix(base_signal, 1),
                "wrong_lag_future_24h": fast.shift_matrix(base_signal, -24),
                "wrong_lag_stale_168h": fast.shift_matrix(base_signal, 168),
                "same_family_random": rng.normal(size=base_signal.shape),
                "time_shuffle": base_signal.reshape(-1)[rng.permutation(base_signal.size)].reshape(base_signal.shape),
                "symbol_shuffle": np.take_along_axis(base_signal, rng.permutation(base_signal.shape[0])[:, None], axis=0),
            }
            for entry_label, label in labels.items():
                for variant, signal in variants.items():
                    weights, spread, top_count, bottom_count = q.portfolio_weights_and_spread(signal, label)
                    metric_rows.extend(split_metric_rows(cid, variant, entry_label, spread, weights, split, orientation, top_count, bottom_count))
                if entry_label == "label_t1_to_t25":
                    weights, spread, top_count, bottom_count = q.portfolio_weights_and_spread(base_signal, label)
                    overlap_rows.extend(p0.overlap_stat_rows(cid, spread, split, orientation))
                    nonoverlap_rows.extend(p0.nonoverlap_offset_rows(cid, spread, split, orientation))
                    s, m, l, h = contribution_tables(cid, weights, label, split, timestamps, loaded_symbols, state_matrix, orientation)
                    symbol_rows.extend(s)
                    month_rows.extend(m)
                    latent_contrib_rows.extend(l)
                    top_hour_rows.extend(h)
                    latent_signal = p0.neutralize_timevarying_state(base_signal, state_matrix)
                    l_weights, l_spread, l_top, l_bottom = q.portfolio_weights_and_spread(latent_signal, label)
                    latent_metric_rows.extend(
                        split_metric_rows(
                            cid,
                            "timevarying_latent_state_neutral",
                            entry_label,
                            l_spread,
                            l_weights,
                            split,
                            orientation,
                            l_top,
                            l_bottom,
                        )
                    )
        except Exception as exc:
            errors.append({"candidate_id": cid, "error": repr(exc)})

    metrics = pd.DataFrame(metric_rows)
    latent_metrics = pd.DataFrame(latent_metric_rows)
    control_gate = control_ratio_by_split(metrics) if not metrics.empty else pd.DataFrame()
    overlap_stats = pd.DataFrame(overlap_rows)
    nonoverlap_stats = pd.DataFrame(nonoverlap_rows)
    symbol_contrib = pd.DataFrame(symbol_rows)
    month_contrib = pd.DataFrame(month_rows)
    latent_contrib = pd.DataFrame(latent_contrib_rows)
    top_hours = pd.DataFrame(top_hour_rows)
    orientation_frame = pd.DataFrame(orientation_rows)
    decisions = classify(candidates, metrics, control_gate, latent_metrics, symbol_contrib, month_contrib, latent_contrib) if not metrics.empty else pd.DataFrame()
    decision_counts = decisions["decision"].value_counts().rename_axis("decision").reset_index(name="count") if not decisions.empty else pd.DataFrame(columns=["decision", "count"])
    pass_count = int(decisions["decision"].eq("A7AL2R_LOCAL_FORENSIC_PASS").sum()) if not decisions.empty else 0
    blockers: list[str] = []
    warnings_out: list[str] = []
    if errors:
        blockers.append("candidate_eval_errors")
    if pass_count == 0:
        blockers.append("no_local_forensic_pass")
    if not decisions.empty and decisions["decision"].astype(str).str.contains("CONTROL_DOMINATED").any():
        warnings_out.append("control_dominated_candidates_rejected")
    decision = "PASS_A7AL2R_LOCAL_FORENSIC_CANDIDATES_READY_FOR_A7AL2S_CONTRACT" if pass_count > 0 and not errors else "HOLD_A7AL2R_LOCAL_FORENSIC_NO_CLEAN_PASS"

    candidates.to_csv(OUT_DIR / "a7al2r_input_candidates.csv", index=False)
    metrics.to_csv(OUT_DIR / "a7al2r_variant_metrics.csv", index=False)
    control_gate.to_csv(OUT_DIR / "a7al2r_control_dominance.csv", index=False)
    latent_metrics.to_csv(OUT_DIR / "a7al2r_timevarying_latent_metrics.csv", index=False)
    overlap_stats.to_csv(OUT_DIR / "a7al2r_overlap_robust_tstats.csv", index=False)
    nonoverlap_stats.to_csv(OUT_DIR / "a7al2r_nonoverlap_offset_tstats.csv", index=False)
    symbol_contrib.to_csv(OUT_DIR / "a7al2r_symbol_contribution.csv", index=False)
    month_contrib.to_csv(OUT_DIR / "a7al2r_month_contribution.csv", index=False)
    latent_contrib.to_csv(OUT_DIR / "a7al2r_latent_state_contribution.csv", index=False)
    top_hours.to_csv(OUT_DIR / "a7al2r_top_gain_loss_hours.csv", index=False)
    orientation_frame.to_csv(OUT_DIR / "a7al2r_orientation_audit.csv", index=False)
    decisions.to_csv(OUT_DIR / "a7al2r_decision_record.csv", index=False)
    pd.DataFrame(errors).to_csv(OUT_DIR / "a7al2r_eval_errors.csv", index=False)

    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_q_manifest": str(Q_MANIFEST),
        "candidate_count": int(len(candidates)),
        "forensic_pass_count": pass_count,
        "decision_counts": {str(r["decision"]): int(r["count"]) for _, r in decision_counts.iterrows()},
        "blockers": blockers,
        "warnings": warnings_out,
        "strict_symbols": len(loaded_symbols),
        "timestamps": int(len(timestamps)),
        "fields_loaded": sorted(fields),
        "controls": CONTROL_VARIANTS,
        "entry_labels": list(labels.keys()),
        "cost_bps": COST_BPS,
        "latent_coverage": latent_coverage,
        "runtime_seconds": round(time.time() - start, 3),
        "uses_may_for_selection": False,
        "uses_may_for_generation": False,
        "uses_may_for_ranking": False,
        "uses_may_for_mutation": False,
        "executes_search": False,
        "executes_training": False,
        "executes_alpha_proof": False,
        "authorizes_a7al2s_contract": bool(pass_count > 0 and not errors),
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(OUT_DIR / "a7al2r_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2R Local Forensic

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This stage deep-audits A7AL-2Q local OI-price diagnostic candidates. It does not generate formulas, does not train, does not authorize large search, and does not authorize alpha proof or shadow/paper/live.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Decision Counts

{md_table(decision_counts, 40)}

## Candidate Decisions

{md_table(decisions, 40)}

## Control Gate

{md_table(control_gate[control_gate["entry_label"].eq("label_t1_to_t25") & control_gate["split"].isin(PRE_MAY_SPLITS)] if not control_gate.empty else control_gate, 80)}

## Top Symbol Contribution

{md_table(symbol_contrib, 40)}

## Boundary

```text
Allowed if PASS:
  draft A7AL-2S local follow-up contract.

Not authorized:
  alpha proof
  large search
  shadow / paper / live
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
