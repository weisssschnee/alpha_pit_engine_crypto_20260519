from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CORE63 = REPO / "runtime" / "a7ffcore63_dice_execution_audit"
PANEL = Path("G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v2_20260527")

RUNTIME = REPO / "runtime" / "a7ffcore64_retest_and_funding_state_package"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE64_RETEST_AND_FUNDING_STATE_PACKAGE_20260605.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
        return "```csv\n" + view.to_csv(index=False) + "```"


def build_retest_package(selected: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    if selected.empty:
        return selected, pd.DataFrame(), {}

    q = selected.copy()
    q["retest_arm"] = "CORE64A_entry_lag_repair_retest"
    q["retest_reason"] = q["core61_reason"].fillna("near_miss")
    q["primary_label_family"] = q["label_family"]
    q["primary_label_horizon_h"] = pd.to_numeric(q["label_horizon_h"], errors="coerce").fillna(1).astype(int)
    q["entry_shift_set"] = "entry_t0,entry_t1,entry_t2"
    q["control_set"] = "matched_control,wrong_lag_stale,wrong_lag_future,row_shuffle,sign_flip"
    q["promotion_use"] = "diagnostic_retest_only"
    q["may_policy"] = "post_selection_veto_only"

    # Keep execution shards small and balanced by semantic pair.
    q = q.sort_values(["semantic_pair", "repair_score"], ascending=[True, False]).reset_index(drop=True)
    shard_count = 4
    q["core64_shard"] = [f"core64a_s{i % shard_count:02d}" for i in range(len(q))]
    q["checkpoint_key"] = q["core64_shard"] + "::" + q["blueprint_id"].astype(str)

    shard_plan = q.groupby("core64_shard", dropna=False).agg(
        rows=("blueprint_id", "size"),
        semantic_pair_count=("semantic_pair", "nunique"),
        motif_count=("motif", "nunique"),
        min_repair_score=("repair_score", "min"),
        max_repair_score=("repair_score", "max"),
    ).reset_index()
    config = {
        "stage": "A7FF-CORE64A",
        "retest_queue_rows": int(len(q)),
        "shard_count": int(shard_count),
        "entry_shift_set": ["entry_t0", "entry_t1", "entry_t2"],
        "label_translation_set": [
            "primary_original_label",
            "L0_raw_forward_return",
            "L1_cross_sectional_relative_return",
            "L5_vol_adjusted_return",
        ],
        "hard_reject": [
            "control_ratio >= 1.0 after retest",
            "all non-L7 translated labels fail",
            "entry_t1 and entry_t2 both fail",
            "same semantic pair dominates selected retest survivors",
        ],
        "checkpoint_required": True,
        "executes_search": False,
        "authorizes_search": False,
    }
    return q, shard_plan, config


def load_funding_panel(max_symbols: int | None = None) -> pd.DataFrame:
    paths = sorted(PANEL.glob("symbol=*/part.parquet"))
    if max_symbols:
        paths = paths[:max_symbols]
    cols = ["symbol", "timestamp", "funding_rate", "funding_interval_hours", "source_market_funding"]
    frames: list[pd.DataFrame] = []
    for path in paths:
        try:
            frame = pd.read_parquet(path, columns=cols)
        except Exception:
            continue
        frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=cols)


def build_funding_state_audit(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if panel.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    df = panel.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values(["symbol", "timestamp"])
    df["funding_event_flag"] = df["funding_rate"].notna()
    df["raw_event_available"] = df["funding_rate"].notna()

    # Event funding is sparse by construction. Candidate alpha features should use PIT last-known state.
    g = df.groupby("symbol", group_keys=False)
    df["funding_rate_last_known"] = g["funding_rate"].ffill()
    df["last_funding_timestamp"] = df["timestamp"].where(df["funding_event_flag"])
    df["last_funding_timestamp"] = g["last_funding_timestamp"].ffill()
    df["funding_event_age_hours"] = (df["timestamp"] - df["last_funding_timestamp"]).dt.total_seconds() / 3600.0
    df["funding_interval_hours_ffill"] = g["funding_interval_hours"].ffill().fillna(8.0)
    df["funding_state_valid_8h"] = df["funding_rate_last_known"].notna() & df["funding_event_age_hours"].between(0, 8, inclusive="both")
    df["funding_state_valid_24h"] = df["funding_rate_last_known"].notna() & df["funding_event_age_hours"].between(0, 24, inclusive="both")
    df["funding_rate_state_8h"] = df["funding_rate_last_known"].where(df["funding_state_valid_8h"])
    df["funding_rate_state_24h"] = df["funding_rate_last_known"].where(df["funding_state_valid_24h"])
    df["funding_abs_state_8h"] = df["funding_rate_state_8h"].abs()
    df["funding_abs_state_24h"] = df["funding_rate_state_24h"].abs()

    symbol_audit = df.groupby("symbol", dropna=False).agg(
        rows=("timestamp", "size"),
        raw_event_coverage=("raw_event_available", "mean"),
        state_8h_coverage=("funding_state_valid_8h", "mean"),
        state_24h_coverage=("funding_state_valid_24h", "mean"),
        first_timestamp=("timestamp", "min"),
        last_timestamp=("timestamp", "max"),
    ).reset_index()
    symbol_audit["state8_over_raw_lift"] = symbol_audit["state_8h_coverage"] / symbol_audit["raw_event_coverage"].replace(0, pd.NA)
    symbol_audit["state24_over_raw_lift"] = symbol_audit["state_24h_coverage"] / symbol_audit["raw_event_coverage"].replace(0, pd.NA)

    timestamp_audit = df.groupby("timestamp", dropna=False).agg(
        active_symbols=("symbol", "nunique"),
        raw_event_symbols=("raw_event_available", "sum"),
        state_8h_symbols=("funding_state_valid_8h", "sum"),
        state_24h_symbols=("funding_state_valid_24h", "sum"),
    ).reset_index()
    timestamp_audit["raw_event_cross_section_coverage"] = timestamp_audit["raw_event_symbols"] / timestamp_audit["active_symbols"].replace(0, pd.NA)
    timestamp_audit["state_8h_cross_section_coverage"] = timestamp_audit["state_8h_symbols"] / timestamp_audit["active_symbols"].replace(0, pd.NA)
    timestamp_audit["state_24h_cross_section_coverage"] = timestamp_audit["state_24h_symbols"] / timestamp_audit["active_symbols"].replace(0, pd.NA)

    field_contract = pd.DataFrame(
        [
            {
                "field_name": "funding_rate",
                "feature_class": "raw_event",
                "allowed_for_alpha": False,
                "allowed_for_diagnostic": True,
                "pit_rule": "event timestamp only; sparse raw source; do not use rolling operators directly for ordinary alpha",
                "materialization_status": "sparse_event_field",
            },
            {
                "field_name": "funding_rate_state_8h",
                "feature_class": "derived_pit_last_known_state",
                "allowed_for_alpha": True,
                "allowed_for_diagnostic": True,
                "pit_rule": "per-symbol last known funding_rate carried forward for <=8h after event; no backfill before first event",
                "materialization_status": "proposed_core64b_repair",
            },
            {
                "field_name": "funding_rate_state_24h",
                "feature_class": "derived_pit_last_known_state",
                "allowed_for_alpha": False,
                "allowed_for_diagnostic": True,
                "pit_rule": "diagnostic carry up to 24h; alpha use requires separate approval because stale carry may wash out event timing",
                "materialization_status": "diagnostic_only",
            },
            {
                "field_name": "funding_event_age_hours",
                "feature_class": "derived_state_age",
                "allowed_for_alpha": True,
                "allowed_for_diagnostic": True,
                "pit_rule": "hours since last observed funding event, computed forward-only per symbol",
                "materialization_status": "proposed_core64b_repair",
            },
            {
                "field_name": "funding_event_flag",
                "feature_class": "event_indicator",
                "allowed_for_alpha": False,
                "allowed_for_diagnostic": True,
                "pit_rule": "event-hour indicator only; do not use as standalone alpha",
                "materialization_status": "diagnostic_only",
            },
        ]
    )
    return symbol_audit, timestamp_audit, field_contract


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    selected = read_csv(CORE63 / "core63_selected_numeric_retest_queue.csv")
    material_diag = read_csv(CORE63 / "core63_materialization_pair_diagnosis.csv")
    if selected.empty:
        raise SystemExit("CORE64 requires CORE63 selected retest queue")

    retest_queue, shard_plan, retest_config = build_retest_package(selected)
    retest_queue.to_csv(RUNTIME / "core64a_numeric_retest_queue.csv", index=False)
    shard_plan.to_csv(RUNTIME / "core64a_retest_shard_plan.csv", index=False)
    write_json(RUNTIME / "core64a_retest_config.json", retest_config)

    funding_panel = load_funding_panel()
    symbol_audit, timestamp_audit, field_contract = build_funding_state_audit(funding_panel)
    symbol_audit.to_csv(RUNTIME / "core64b_funding_state_coverage_by_symbol.csv", index=False)
    timestamp_audit.to_csv(RUNTIME / "core64b_funding_state_coverage_by_timestamp.csv", index=False)
    field_contract.to_csv(RUNTIME / "core64b_funding_state_field_contract.csv", index=False)

    # Compact summary for reports / gating.
    funding_summary = {
        "panel_rows": int(len(funding_panel)),
        "panel_symbols": int(funding_panel["symbol"].nunique()) if not funding_panel.empty else 0,
        "raw_event_coverage_median": float(symbol_audit["raw_event_coverage"].median()) if not symbol_audit.empty else 0.0,
        "state_8h_coverage_median": float(symbol_audit["state_8h_coverage"].median()) if not symbol_audit.empty else 0.0,
        "state_24h_coverage_median": float(symbol_audit["state_24h_coverage"].median()) if not symbol_audit.empty else 0.0,
        "state8_over_raw_lift_median": float(symbol_audit["state8_over_raw_lift"].median()) if not symbol_audit.empty else 0.0,
        "state24_over_raw_lift_median": float(symbol_audit["state24_over_raw_lift"].median()) if not symbol_audit.empty else 0.0,
    }
    write_json(RUNTIME / "core64b_funding_state_summary.json", funding_summary)

    blockers: list[str] = []
    if len(retest_queue) < 24:
        blockers.append("retest_queue_lt_24")
    if retest_queue["semantic_pair"].nunique() < 4:
        blockers.append("retest_semantic_pair_count_lt_4")
    if funding_summary["state_8h_coverage_median"] < 0.75:
        blockers.append("funding_state_8h_coverage_lt_75pct")
    if not material_diag.empty and (material_diag["diagnosis"] == "funding_event_sparse_state_alignment").any():
        blockers.append("funding_pair_requires_state_field_retest")

    decision = "PASS_CORE64_PACKAGE_READY_FOR_COMPANY_RETEST" if not blockers else "HOLD_CORE64_PACKAGE_READY_WITH_FUNDING_REPAIR_REQUIRED"
    manifest = {
        "stage": "A7FF-CORE64",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "core64a_retest_queue_rows": int(len(retest_queue)),
        "core64a_shard_count": int(shard_plan["core64_shard"].nunique()) if not shard_plan.empty else 0,
        "core64a_semantic_pair_count": int(retest_queue["semantic_pair"].nunique()),
        "core64b_panel_rows": funding_summary["panel_rows"],
        "core64b_panel_symbols": funding_summary["panel_symbols"],
        "core64b_raw_event_coverage_median": funding_summary["raw_event_coverage_median"],
        "core64b_state_8h_coverage_median": funding_summary["state_8h_coverage_median"],
        "core64b_state8_over_raw_lift_median": funding_summary["state8_over_raw_lift_median"],
        "executes_search": False,
        "executes_replay": False,
        "authorizes_company_retest": len(retest_queue) >= 24,
        "authorizes_funding_state_patch": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    write_json(RUNTIME / "core64_manifest.json", manifest)
    write_json(RUNTIME / "core64_decision_record.json", manifest)

    REPORT.write_text("\n".join([
        "# CRYPTO A7FF-CORE64 RETEST AND FUNDING STATE PACKAGE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE64 packages the CORE63 dice output into a bounded retest queue and defines the funding sparse-event state repair. It does not execute formula search, replay promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## CORE64A Retest Shard Plan",
        "",
        md_table(shard_plan, 40),
        "",
        "## CORE64A Retest Queue Preview",
        "",
        md_table(retest_queue[[
            "blueprint_id", "core64_shard", "semantic_pair", "motif", "primary_label_family",
            "primary_label_horizon_h", "repair_score", "control_ratio", "cost10", "expression",
        ]], 80),
        "",
        "## CORE64B Funding State Coverage Summary",
        "",
        "```json",
        json.dumps(funding_summary, indent=2, sort_keys=True),
        "```",
        "",
        "## CORE64B Funding State Field Contract",
        "",
        md_table(field_contract, 20),
        "",
        "## CORE64B Symbol Coverage Preview",
        "",
        md_table(symbol_audit.sort_values("state_8h_coverage").head(30), 30),
        "",
    ]), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
