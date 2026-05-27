from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import crypto_a7s2m_metrics_registry_diagnostic as a7s2m


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path("G:/AlphaFactory_CryptoData")
PANEL_PATH = DATA_ROOT / "gold" / "panels" / "crypto_core12_1h_with_aggtrades_metrics_features_v1.parquet"
A7Y0_AUTH = ROOT / "runtime" / "a7y0_unified_state_panel" / "a7y0_authorization_matrix.json"

OUT_DIR = ROOT / "runtime" / "a7y1_interaction_diagnostic"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7Y1_INTERACTION_DIAGNOSTIC_20260522.md"

CORE12 = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "AVAXUSDT",
    "LINKUSDT",
    "BCHUSDT",
    "LTCUSDT",
    "SUIUSDT",
]
CORE3 = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

VALIDATION = "validation_2025H1"
RECENT = "recent_oos_2025H2_2026Apr"
MAY = "fresh_may_2026"
PRIMARY_COST_BPS = 10.0
SEVERE_COST_BPS = 20.0
GENERATED_CAP = 320
STRICT_REPLAY_CAP = 96
DEEP_AUDIT_CAP = 48


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def clean_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def stable_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def stable_int(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:12], 16)


def candidate_row(lane: str, family: str, expr: str, horizon: int, fields: list[str], motif: str) -> dict[str, Any]:
    cid = f"a7y1_{lane}_{family}_{horizon}_{stable_id(expr + str(horizon))}"
    return {
        "candidate_id": cid,
        "lane": lane,
        "production_family": family,
        "derived_feature_id": motif,
        "expression": expr,
        "horizon": horizon,
        "source_fields": ";".join(sorted(set(fields))),
        "feature_available_lag_bars": 1,
        "feature_timestamp_rule": "unified 1h features available at hour timestamp + 1h",
        "execution_rule": "next 1h bar or later; May stress post-selection only",
    }


def generate_candidates() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    crowd_states = [
        "global_long_short_account_ratio_zscore_168h",
        "top_long_short_position_ratio_zscore_168h",
        "top_long_short_account_ratio_zscore_168h",
    ]
    oi_states = [
        "open_interest_zscore_168h",
        "open_interest_change_24h",
        "open_interest_value_zscore_168h",
    ]
    contexts = ["mark_index_ratio", "premium_index", "latest_known_funding_rate", "ret_24", "realized_vol_24"]
    for crowd in crowd_states:
        for ctx in contexts:
            for horizon in [24, 48]:
                expr = f"Mul(Neg(ZScore({crowd})),Rank({ctx}))"
                rows.append(candidate_row("core12_metrics", "F0_metrics_crowding_state_interaction", expr, horizon, [crowd, ctx], "crowding_x_state"))
    for oi in oi_states:
        for ctx in ["mark_index_ratio", "premium_index", "ret_24", "realized_vol_24"]:
            for horizon in [24, 48]:
                expr = f"Mul(ZScore({oi}),Rank({ctx}))"
                rows.append(candidate_row("core12_metrics", "F1_oi_state_interaction", expr, horizon, [oi, ctx], "oi_x_state"))
    for crowd in crowd_states:
        for oi in oi_states:
            for horizon in [24, 48]:
                expr = f"Mul(Neg(ZScore({crowd})),Rank({oi}))"
                rows.append(candidate_row("core12_metrics", "F2_crowding_oi_interaction", expr, horizon, [crowd, oi], "crowding_x_oi"))

    agg_fields = [
        "agg_flow_imbalance_notional_24h",
        "agg_signed_flow_z_24h",
        "agg_large_notional_share_24h",
        "agg_cross_symbol_signed_flow_share",
        "agg_notional_accel_4h_vs_24h",
        "agg_flow_accel_4h_vs_24h",
    ]
    for crowd in crowd_states[:2]:
        for agg in agg_fields:
            for horizon in [24, 48]:
                expr = f"Mul(Neg(ZScore({crowd})),Rank({agg}))"
                rows.append(candidate_row("core3_agg_metrics", "F3_metrics_crowding_x_aggflow", expr, horizon, [crowd, agg], "crowding_x_aggflow"))
    for oi in oi_states:
        for agg in agg_fields[:4]:
            for horizon in [24, 48]:
                expr = f"Mul(ZScore({oi}),Rank({agg}))"
                rows.append(candidate_row("core3_agg_metrics", "F4_oi_x_aggflow", expr, horizon, [oi, agg], "oi_x_aggflow"))
    out = pd.DataFrame(rows).drop_duplicates("candidate_id").head(GENERATED_CAP).copy()
    return out


def choose_strict_replay(generated: pd.DataFrame) -> pd.DataFrame:
    selected = []
    quota = max(1, STRICT_REPLAY_CAP // max(1, generated["production_family"].nunique()))
    for family in sorted(generated["production_family"].unique()):
        part = generated[generated["production_family"].eq(family)].sort_values(["lane", "derived_feature_id", "expression", "horizon"])
        selected.append(part.head(quota))
    return pd.concat(selected, ignore_index=True).head(STRICT_REPLAY_CAP)


def build_controls(selected: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in selected.iterrows():
        for mode in ["row_shuffle", "time_shuffle", "wrong_lag", "sign_flip"]:
            rec = row.to_dict()
            rec.update(
                {
                    "control_id": f"{row['candidate_id']}__ctrl_{mode}_{stable_id(str(row['candidate_id']) + mode)}",
                    "base_candidate_id": row["candidate_id"],
                    "control_mode": mode,
                    "object_type": "control",
                    "promotable": False,
                }
            )
            rec.pop("candidate_id", None)
            rows.append(rec)
    return pd.DataFrame(rows)


def required_columns(selected: pd.DataFrame) -> list[str]:
    fields = {"symbol", "timestamp", "open", "metrics_features_available", "agg_features_available"}
    for text in selected["source_fields"].dropna().astype(str):
        for item in text.split(";"):
            if item:
                fields.add(item)
    return sorted(fields)


def load_matrices(selected: pd.DataFrame, lane: str) -> tuple[pd.DatetimeIndex, list[str], dict[str, np.ndarray]]:
    cols = required_columns(selected)
    df = pd.read_parquet(PANEL_PATH, columns=cols)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    symbols = CORE12 if lane == "core12_metrics" else CORE3
    df = df[df["symbol"].isin(symbols)].sort_values(["timestamp", "symbol"]).copy()
    index = pd.DatetimeIndex(sorted(df["timestamp"].unique()))
    matrices: dict[str, np.ndarray] = {}
    for col in cols:
        if col in {"symbol", "timestamp"} or df[col].dtype == "object":
            continue
        pivot = df.pivot(index="timestamp", columns="symbol", values=col).reindex(index=index, columns=symbols)
        matrices[col] = pivot.to_numpy(dtype=float)
    if lane == "core12_metrics":
        matrices["lane_features_available"] = matrices["metrics_features_available"].astype(bool).astype(float)
    else:
        matrices["lane_features_available"] = (matrices["metrics_features_available"].astype(bool) & matrices["agg_features_available"].astype(bool)).astype(float)
    return index, symbols, matrices


def top_bottom_book(signal: np.ndarray, target: np.ndarray, orientation: float, cost_bps: float, k: int) -> dict[str, np.ndarray]:
    oriented = signal * orientation
    valid = np.isfinite(oriented) & np.isfinite(target)
    valid_rows = valid.sum(axis=1) >= (2 * k)
    pos = np.zeros_like(target, dtype=float)
    if np.any(valid_rows):
        high = np.where(valid, oriented, -np.inf)
        low = np.where(valid, oriented, np.inf)
        rows = np.where(valid_rows)[0]
        long_idx = np.argpartition(high[valid_rows], -k, axis=1)[:, -k:]
        short_idx = np.argpartition(low[valid_rows], k - 1, axis=1)[:, :k]
        weight = 0.5 / k
        for r_pos, r in enumerate(rows):
            pos[r, long_idx[r_pos]] = weight
            pos[r, short_idx[r_pos]] = -weight
    gross = np.nansum(pos * target, axis=1)
    prev = np.vstack([np.zeros((1, pos.shape[1])), pos[:-1, :]])
    turnover = np.nansum(np.abs(pos - prev), axis=1) / 2.0
    fee = turnover * (cost_bps / 10000.0)
    return {"net": gross - fee, "turnover": turnover, "gross_exposure": np.nansum(np.abs(pos), axis=1)}


def summarize(index: pd.DatetimeIndex, split: str, signal: np.ndarray, target: np.ndarray, book10: dict[str, np.ndarray], book20: dict[str, np.ndarray], lag1: dict[str, np.ndarray]) -> dict[str, Any]:
    mask = a7s2m.split_mask(index, split)
    return {
        "split": split,
        "rows": int(mask.sum()),
        "active_hours": int(np.sum(np.isfinite(book10["net"][mask]) & (book10["gross_exposure"][mask] > 0))),
        "mean_ic": clean_float(np.nanmean(a7s2m.row_ic(signal[mask], target[mask]))),
        "net_sum_10bps": clean_float(np.nansum(book10["net"][mask])),
        "net_sum_20bps": clean_float(np.nansum(book20["net"][mask])),
        "lag1_net_sum_10bps": clean_float(np.nansum(lag1["net"][mask])),
        "turnover_mean": clean_float(np.nanmean(book10["turnover"][mask])),
        "gross_exposure_mean": clean_float(np.nanmean(book10["gross_exposure"][mask])),
    }


def evaluate_lane(selected: pd.DataFrame, controls: pd.DataFrame, lane: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    lane_selected = selected[selected["lane"].eq(lane)].copy()
    lane_controls = controls[controls["base_candidate_id"].isin(set(lane_selected["candidate_id"]))].copy()
    index, symbols, matrices = load_matrices(lane_selected, lane)
    ctx = a7s2m.ExprContext(matrices)
    k = 3 if lane == "core12_metrics" else 1
    train = a7s2m.split_mask(index, "train_2024")
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    cache: dict[str, tuple[np.ndarray, float]] = {}
    for _, row in lane_selected.iterrows():
        cid = str(row["candidate_id"])
        try:
            signal = np.where(matrices["lane_features_available"].astype(bool), ctx.eval(str(row["expression"])), np.nan)
            target = a7s2m.forward_open_return(matrices["open"], int(row["horizon"]))
            train_ic = np.nanmean(a7s2m.row_ic(signal[train], target[train]))
            orientation = 1.0 if not np.isfinite(train_ic) or train_ic >= 0 else -1.0
            cache[cid] = (signal, orientation)
            book10 = top_bottom_book(signal, target, orientation, PRIMARY_COST_BPS, k)
            book20 = top_bottom_book(signal, target, orientation, SEVERE_COST_BPS, k)
            lag_signal = np.where(matrices["lane_features_available"].astype(bool), a7s2m.apply_control(signal, "lag1_stress", cid), np.nan)
            lag1 = top_bottom_book(lag_signal, target, orientation, PRIMARY_COST_BPS, k)
            for split in a7s2m.SPLITS:
                rec = summarize(index, split, signal, target, book10, book20, lag1)
                rec.update({"candidate_id": cid, "base_candidate_id": cid, "object_type": "candidate", "control_mode": "original", "lane": lane, "production_family": row["production_family"], "expression": row["expression"], "horizon": int(row["horizon"]), "orientation": orientation, "base_train_ic": clean_float(train_ic)})
                rows.append(rec)
        except Exception as exc:  # noqa: BLE001
            failures.append({"candidate_id": cid, "object_type": "candidate", "control_mode": "original", "eval_error": f"{type(exc).__name__}: {exc}"})
    for _, row in lane_controls.iterrows():
        control_id = str(row["control_id"])
        base_id = str(row["base_candidate_id"])
        try:
            signal, orientation = cache[base_id]
            target = a7s2m.forward_open_return(matrices["open"], int(row["horizon"]))
            ctrl = a7s2m.apply_control(signal, str(row["control_mode"]), control_id)
            ctrl = np.where(matrices["lane_features_available"].astype(bool), ctrl, np.nan)
            book10 = top_bottom_book(ctrl, target, orientation, PRIMARY_COST_BPS, k)
            book20 = top_bottom_book(ctrl, target, orientation, SEVERE_COST_BPS, k)
            lag_ctrl = a7s2m.apply_control(ctrl, "lag1_stress", control_id + "_lag1")
            lag1 = top_bottom_book(lag_ctrl, target, orientation, PRIMARY_COST_BPS, k)
            for split in a7s2m.SPLITS:
                rec = summarize(index, split, ctrl, target, book10, book20, lag1)
                rec.update({"candidate_id": control_id, "base_candidate_id": base_id, "object_type": "control", "control_mode": row["control_mode"], "lane": lane, "production_family": row["production_family"], "expression": row["expression"], "horizon": int(row["horizon"]), "orientation": orientation, "base_train_ic": np.nan})
                rows.append(rec)
        except Exception as exc:  # noqa: BLE001
            failures.append({"candidate_id": control_id, "base_candidate_id": base_id, "object_type": "control", "control_mode": row.get("control_mode", ""), "eval_error": f"{type(exc).__name__}: {exc}"})
    return pd.DataFrame(rows), pd.DataFrame(failures)


def wide_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    idx = ["candidate_id", "base_candidate_id", "object_type", "control_mode", "lane", "production_family", "expression", "horizon"]
    values = ["active_hours", "mean_ic", "net_sum_10bps", "net_sum_20bps", "lag1_net_sum_10bps", "turnover_mean", "gross_exposure_mean"]
    wide = metrics.pivot_table(index=idx, columns="split", values=values, aggfunc="first")
    wide.columns = [f"{a}__{b}" for a, b in wide.columns]
    return wide.reset_index()


def label_candidates(wide: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    candidates = wide[wide["object_type"].eq("candidate")].copy()
    controls = wide[wide["object_type"].eq("control")].copy()
    rows = []
    for _, cand in candidates.iterrows():
        cid = str(cand["candidate_id"])
        matched = controls[controls["base_candidate_id"].eq(cid)]
        val = float(cand.get(f"net_sum_10bps__{VALIDATION}", np.nan))
        recent = float(cand.get(f"net_sum_10bps__{RECENT}", np.nan))
        recent20 = float(cand.get(f"net_sum_20bps__{RECENT}", np.nan))
        lag1_recent = float(cand.get(f"lag1_net_sum_10bps__{RECENT}", np.nan))
        may = float(cand.get(f"net_sum_10bps__{MAY}", np.nan))
        may_active = float(cand.get(f"active_hours__{MAY}", np.nan))
        ctrl_recent_pos = int(
            (
                (pd.to_numeric(matched.get(f"net_sum_10bps__{VALIDATION}", pd.Series(dtype=float)), errors="coerce") > 0)
                & (pd.to_numeric(matched.get(f"net_sum_10bps__{RECENT}", pd.Series(dtype=float)), errors="coerce") > 0)
            ).sum()
        )
        if ctrl_recent_pos:
            label = "A7Y1_HOLD_CONTROL_CONTAMINATED"
        elif not (val > 0 and recent > 0):
            label = "A7Y1_HOLD_RAW_VAL_RECENT_FAIL"
        elif not recent20 > 0:
            label = "A7Y1_HOLD_COST20_FAIL"
        elif not lag1_recent > 0:
            label = "A7Y1_HOLD_LAG1_FAIL"
        elif not (may_active > 0 and may > 0):
            label = "A7Y1_NEAR_MISS_MAY_STRESS_FAIL"
        else:
            label = "A7Y1_INTERACTION_RESEARCH_CLUE_FOR_FORENSIC"
        rows.append(
            {
                "candidate_id": cid,
                "lane": cand["lane"],
                "production_family": cand["production_family"],
                "expression": cand["expression"],
                "horizon": int(cand["horizon"]),
                "validation_net10": clean_float(val),
                "recent_net10": clean_float(recent),
                "recent_net20": clean_float(recent20),
                "lag1_recent_net10": clean_float(lag1_recent),
                "may_net10_stress_only": clean_float(may),
                "may_active_hours": clean_float(may_active),
                "control_val_recent_positive_count": ctrl_recent_pos,
                "a7y1_label": label,
            }
        )
    labels = pd.DataFrame(rows)
    return labels.merge(selected[["candidate_id", "source_fields", "derived_feature_id"]], on="candidate_id", how="left")


def select_deep(labels: pd.DataFrame) -> pd.DataFrame:
    order = {
        "A7Y1_INTERACTION_RESEARCH_CLUE_FOR_FORENSIC": 0,
        "A7Y1_NEAR_MISS_MAY_STRESS_FAIL": 1,
        "A7Y1_HOLD_LAG1_FAIL": 2,
        "A7Y1_HOLD_COST20_FAIL": 3,
        "A7Y1_HOLD_CONTROL_CONTAMINATED": 4,
        "A7Y1_HOLD_RAW_VAL_RECENT_FAIL": 5,
    }
    labels = labels.copy()
    labels["label_order"] = labels["a7y1_label"].map(order).fillna(99)
    selected = []
    quota = max(1, DEEP_AUDIT_CAP // max(1, labels["production_family"].nunique()))
    for family in sorted(labels["production_family"].unique()):
        part = labels[labels["production_family"].eq(family)].sort_values(["label_order", "recent_net20", "lag1_recent_net10"], ascending=[True, False, False])
        selected.append(part.head(quota))
    return pd.concat(selected, ignore_index=True).head(DEEP_AUDIT_CAP)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_report(now: str, generated: pd.DataFrame, selected: pd.DataFrame, controls: pd.DataFrame, labels: pd.DataFrame, deep: pd.DataFrame, failures: pd.DataFrame, auth: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    label_summary = labels.groupby(["lane", "production_family", "a7y1_label"]).size().reset_index(name="rows") if not labels.empty else pd.DataFrame()
    lines = [
        "# Crypto A7Y-1 Interaction Diagnostic",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{auth['decision']}`",
        "- executes_search: `small_structural_generation`",
        "- executes_replay: `small_controlled_diagnostic`",
        "- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7Y-1 tests state-interaction use of accepted aggTrades and Binance metrics features. It has two lanes: core12 metrics-only and core3 aggTrades x metrics. It does not promote standalone crowding or standalone activity/liquidity.",
        "",
        "May is post-selection stress-only and is not used for generation, orientation, ranking, thresholds, or allocation.",
        "",
        "## Funnel",
        "",
        f"- generated: `{len(generated)}` / cap `{GENERATED_CAP}`",
        f"- strict replay candidates: `{len(selected)}` / cap `{STRICT_REPLAY_CAP}`",
        f"- controls: `{len(controls)}`",
        f"- deep audit selected: `{len(deep)}` / cap `{DEEP_AUDIT_CAP}`",
        "",
        "## Label Summary",
        "",
        table(label_summary, max_rows=100),
        "",
        "## Deep Audit Pool",
        "",
        table(deep.sort_values(["a7y1_label", "recent_net20"], ascending=[True, False]), max_rows=80),
        "",
        "## Eval Failures",
        "",
        table(failures, max_rows=40),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(auth, indent=2, sort_keys=True),
        "```",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    a7y0_auth = json.loads(A7Y0_AUTH.read_text(encoding="utf-8")) if A7Y0_AUTH.exists() else {}
    generated = generate_candidates()
    selected = choose_strict_replay(generated)
    controls = build_controls(selected)
    metric_parts = []
    failure_parts = []
    for lane in sorted(selected["lane"].unique()):
        m, f = evaluate_lane(selected, controls, lane)
        metric_parts.append(m)
        failure_parts.append(f)
    metrics = pd.concat(metric_parts, ignore_index=True) if metric_parts else pd.DataFrame()
    non_empty_failures = [f for f in failure_parts if not f.empty]
    failures = pd.concat(non_empty_failures, ignore_index=True) if non_empty_failures else pd.DataFrame()
    wide = wide_metrics(metrics) if not metrics.empty else pd.DataFrame()
    labels = label_candidates(wide, selected) if not wide.empty else pd.DataFrame()
    deep = select_deep(labels) if not labels.empty else pd.DataFrame()
    clue_count = int(labels["a7y1_label"].eq("A7Y1_INTERACTION_RESEARCH_CLUE_FOR_FORENSIC").sum()) if not labels.empty else 0
    control_contaminated = int(labels["a7y1_label"].eq("A7Y1_HOLD_CONTROL_CONTAMINATED").sum()) if not labels.empty else 0
    blockers: list[str] = []
    warnings: list[str] = []
    if not str(a7y0_auth.get("decision", "")).startswith("PASS"):
        blockers.append("a7y0_not_pass")
    if not failures.empty:
        blockers.append("eval_failures_present")
    if control_contaminated > 0:
        warnings.append("control_contamination_present_in_non_clue_pool")
    if clue_count == 0:
        blockers.append("no_clean_interaction_research_clue")
    decision = "PASS_A7Y1_INTERACTION_CLUE_POOL_FOR_FORENSIC" if clue_count > 0 and failures.empty and "a7y0_not_pass" not in blockers else "HOLD_A7Y1_NO_CLEAN_INTERACTION_CLUE"
    if not failures.empty:
        decision = "HOLD_A7Y1_EVAL_FAILURE"
    auth = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "generated_count": int(len(generated)),
        "strict_replay_candidate_count": int(len(selected)),
        "control_count": int(len(controls)),
        "metric_rows": int(len(metrics)),
        "deep_audit_count": int(len(deep)),
        "interaction_research_clue_count": clue_count,
        "control_contaminated_candidate_count": control_contaminated,
        "executes_search": "small_structural_generation",
        "executes_replay": "small_controlled_diagnostic",
        "may_policy": "stress_only_not_generation_orientation_ranking_threshold_or_allocation",
        "authorizes_a7y2_forensic": clue_count > 0 and failures.empty,
        "authorizes_expanded_replay": False,
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": [
            "A7Y-2 forensic if interaction clues exist",
            "No expanded replay or alpha proof from A7Y-1",
            "Preserve lane separation between core12 metrics and core3 agg-metrics",
        ],
    }
    generated.to_csv(OUT_DIR / "a7y1_generated_candidates.csv", index=False)
    selected.to_csv(OUT_DIR / "a7y1_selected_candidates.csv", index=False)
    controls.to_csv(OUT_DIR / "a7y1_controls.csv", index=False)
    metrics.to_csv(OUT_DIR / "a7y1_split_metrics.csv", index=False)
    wide.to_csv(OUT_DIR / "a7y1_wide_metrics.csv", index=False)
    labels.to_csv(OUT_DIR / "a7y1_candidate_labels.csv", index=False)
    deep.to_csv(OUT_DIR / "a7y1_deep_audit_pool.csv", index=False)
    failures.to_csv(OUT_DIR / "a7y1_eval_failures.csv", index=False)
    write_json(OUT_DIR / "a7y1_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7y1_manifest.json", {"generated_at": now, "decision": decision, "output_dir": str(OUT_DIR), "report": str(REPORT_PATH), "panel": str(PANEL_PATH)})
    write_report(now, generated, selected, controls, labels, deep, failures, auth)
    print(json.dumps({"decision": decision, "blockers": blockers, "warnings": warnings, "clues": clue_count, "selected": len(selected)}, indent=2))


if __name__ == "__main__":
    main()
