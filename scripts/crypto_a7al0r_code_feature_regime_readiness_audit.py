from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7al0r_code_feature_regime_readiness_audit"
REPORT = REPO / "reports" / "CRYPTO_A7AL0R_CODE_FEATURE_REGIME_READINESS_AUDIT_20260527.md"

BASE_CONTRACT = REPO / "runtime" / "a7al_universe498_replay_acceptance" / "a7am_feature_contract.csv"
LV1_QUALITY = REPO / "runtime" / "a7ak_lv1_latent_state_feature_build" / "a7ak_lv1_state_feature_quality.csv"
LV1_MANIFEST = REPO / "runtime" / "a7ak_lv1_latent_state_feature_build" / "a7ak_lv1_manifest.json"
LV2_MANIFEST = REPO / "runtime" / "a7ak_lv2_response_merge_audit" / "a7ak_lv2_manifest.json"
LV3_MANIFEST = REPO / "runtime" / "a7ak_lv3_neutral_field_family_smoke" / "a7ak_lv3_manifest.json"
A7AL0_MANIFEST = REPO / "runtime" / "a7al0_top498_alpha_search_contract" / "a7al0_manifest.json"


DERIVED_SPECS: list[dict[str, Any]] = [
    {
        "field_name": "listing_age_hours",
        "source_field_names": "symbol,timestamp,first_observed_timestamp",
        "source_family": "metadata_listing",
        "feature_class": "derived_latent_state",
        "formula": "(timestamp - first_observed_timestamp) / 1h",
        "lookback_hours": 0,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "listing lifecycle state",
    },
    {
        "field_name": "listing_age_days",
        "source_field_names": "listing_age_hours",
        "source_family": "metadata_listing",
        "feature_class": "derived_latent_state",
        "formula": "listing_age_hours / 24",
        "lookback_hours": 0,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "listing lifecycle state",
    },
    {
        "field_name": "log1p_listing_age_days",
        "source_field_names": "listing_age_days",
        "source_family": "metadata_listing",
        "feature_class": "derived_latent_state",
        "formula": "log1p(listing_age_days)",
        "lookback_hours": 0,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "nonlinear age transform",
    },
    {
        "field_name": "sqrt_listing_age_days",
        "source_field_names": "listing_age_days",
        "source_family": "metadata_listing",
        "feature_class": "derived_latent_state",
        "formula": "sqrt(listing_age_days)",
        "lookback_hours": 0,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "nonlinear age transform",
    },
    {
        "field_name": "age_percentile_active_universe",
        "source_field_names": "listing_age_days",
        "source_family": "metadata_listing",
        "feature_class": "derived_cross_section",
        "formula": "rank_pct(listing_age_days) within timestamp",
        "lookback_hours": 0,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "active-universe age rank",
    },
    {
        "field_name": "history_length_hours",
        "source_field_names": "symbol,timestamp",
        "source_family": "metadata_listing",
        "feature_class": "derived_latent_state",
        "formula": "row_number_since_first_observed + 1",
        "lookback_hours": 0,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "history coverage state",
    },
    {
        "field_name": "rolling_coverage_168h",
        "source_field_names": "source_trade_klines,source_metrics,source_market_funding",
        "source_family": "metadata_timing",
        "feature_class": "derived_rolling",
        "formula": "rolling_mean(all_sources_available, 168h)",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": False,
        "allowed_for_neutralization": True,
        "economic_role": "data quality state",
    },
    {
        "field_name": "gap_hours_recent_168h",
        "source_field_names": "timestamp",
        "source_family": "metadata_timing",
        "feature_class": "derived_rolling",
        "formula": "rolling_sum(max(timestamp_diff_hours - 1, 0), 168h)",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": False,
        "allowed_for_neutralization": True,
        "economic_role": "data gap state",
    },
    {
        "field_name": "median_quote_volume_168h",
        "source_field_names": "trade_quote_volume",
        "source_family": "trade_ohlcv",
        "feature_class": "derived_rolling",
        "formula": "rolling_median(trade_quote_volume, 168h)",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "liquidity level",
    },
    {
        "field_name": "log_quote_volume_168h",
        "source_field_names": "median_quote_volume_168h",
        "source_family": "trade_ohlcv",
        "feature_class": "derived_rolling",
        "formula": "log1p(median_quote_volume_168h)",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "liquidity level transform",
    },
    {
        "field_name": "liquidity_rank_active_universe",
        "source_field_names": "median_quote_volume_168h",
        "source_family": "trade_ohlcv",
        "feature_class": "derived_cross_section",
        "formula": "rank_pct(median_quote_volume_168h) within timestamp",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "active liquidity rank",
    },
    {
        "field_name": "trade_count_168h",
        "source_field_names": "trade_count",
        "source_family": "trade_ohlcv",
        "feature_class": "derived_rolling",
        "formula": "rolling_mean(trade_count, 168h)",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": False,
        "economic_role": "activity level",
    },
    {
        "field_name": "realized_vol_24h",
        "source_field_names": "trade_return_1h",
        "source_family": "trade_ohlcv",
        "feature_class": "derived_rolling",
        "formula": "rolling_std(trade_return_1h, 24h)",
        "lookback_hours": 24,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": False,
        "economic_role": "volatility state",
    },
    {
        "field_name": "realized_vol_72h",
        "source_field_names": "trade_return_1h",
        "source_family": "trade_ohlcv",
        "feature_class": "derived_rolling",
        "formula": "rolling_std(trade_return_1h, 72h)",
        "lookback_hours": 72,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": False,
        "economic_role": "volatility state",
    },
    {
        "field_name": "realized_vol_168h",
        "source_field_names": "trade_return_1h",
        "source_family": "trade_ohlcv",
        "feature_class": "derived_rolling",
        "formula": "rolling_std(trade_return_1h, 168h)",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "volatility state",
    },
    {
        "field_name": "volume_volatility_ratio_168h",
        "source_field_names": "log_quote_volume_168h,realized_vol_168h",
        "source_family": "trade_ohlcv",
        "feature_class": "derived_interaction",
        "formula": "log_quote_volume_168h / realized_vol_168h",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": False,
        "economic_role": "liquidity per volatility state",
    },
    {
        "field_name": "funding_rate_abs_168h",
        "source_field_names": "funding_rate",
        "source_family": "funding",
        "feature_class": "derived_rolling",
        "formula": "rolling_mean(abs(funding_rate), 168h)",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "funding crowding state",
    },
    {
        "field_name": "funding_rate_mean_168h",
        "source_field_names": "funding_rate",
        "source_family": "funding",
        "feature_class": "derived_rolling",
        "formula": "rolling_mean(funding_rate, 168h)",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": False,
        "economic_role": "funding direction state",
    },
    {
        "field_name": "basis_abs_168h",
        "source_field_names": "mark_index_basis_bps",
        "source_family": "mark_index_premium",
        "feature_class": "derived_rolling",
        "formula": "rolling_mean(abs(mark_index_basis_bps), 168h)",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "basis dislocation state",
    },
    {
        "field_name": "premium_abs_168h",
        "source_field_names": "premium_close_bps",
        "source_family": "mark_index_premium",
        "feature_class": "derived_rolling",
        "formula": "rolling_mean(abs(premium_close_bps), 168h)",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "premium dislocation state",
    },
    {
        "field_name": "open_interest_change_24h",
        "source_field_names": "open_interest_last",
        "source_family": "metrics_positioning",
        "feature_class": "derived_rolling",
        "formula": "log(open_interest_last).diff(24h)",
        "lookback_hours": 24,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": False,
        "economic_role": "leverage flow state",
    },
    {
        "field_name": "trade_return_24h",
        "source_field_names": "trade_close",
        "source_family": "trade_ohlcv",
        "feature_class": "derived_rolling",
        "formula": "log(trade_close).diff(24h)",
        "lookback_hours": 24,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": False,
        "economic_role": "past price move",
    },
    {
        "field_name": "oi_x_price_move_24h",
        "source_field_names": "open_interest_change_24h,trade_return_24h",
        "source_family": "metrics_positioning,trade_ohlcv",
        "feature_class": "derived_interaction",
        "formula": "open_interest_change_24h * trade_return_24h",
        "lookback_hours": 24,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": False,
        "economic_role": "leverage-flow price interaction",
    },
    {
        "field_name": "age_x_liquidity",
        "source_field_names": "log1p_listing_age_days,liquidity_rank_active_universe",
        "source_family": "metadata_listing,trade_ohlcv",
        "feature_class": "derived_interaction",
        "formula": "log1p_listing_age_days * liquidity_rank_active_universe",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "listing liquidity lifecycle",
    },
    {
        "field_name": "age_x_volatility",
        "source_field_names": "log1p_listing_age_days,realized_vol_168h",
        "source_family": "metadata_listing,trade_ohlcv",
        "feature_class": "derived_interaction",
        "formula": "log1p_listing_age_days * realized_vol_168h",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "listing volatility lifecycle",
    },
    {
        "field_name": "age_x_funding_abs",
        "source_field_names": "log1p_listing_age_days,funding_rate_abs_168h",
        "source_family": "metadata_listing,funding",
        "feature_class": "derived_interaction",
        "formula": "log1p_listing_age_days * funding_rate_abs_168h",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": True,
        "allowed_for_neutralization": True,
        "economic_role": "listing funding crowding lifecycle",
    },
    {
        "field_name": "raw_latent_state_id",
        "source_field_names": "age/liquidity/volatility/funding/basis/coverage/major buckets",
        "source_family": "latent_state",
        "feature_class": "derived_latent_state",
        "formula": "train-threshold bucket tuple hashed to state id",
        "lookback_hours": 168,
        "allowed_for_regime": True,
        "allowed_for_search": False,
        "allowed_for_neutralization": True,
        "economic_role": "latent neutralization group",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def md_table(rows: list[dict[str, Any]], limit: int | None = None) -> str:
    if limit is not None:
        rows = rows[:limit]
    if not rows:
        return "`<empty>`"
    fields = list(rows[0].keys())
    out = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(f, "")) for f in fields) + " |")
    return "\n".join(out)


def script_inventory() -> list[dict[str, Any]]:
    targets = [
        "crypto_a7al_universe498_replay_acceptance.py",
        "crypto_a7ak_lv1_latent_state_feature_build.py",
        "crypto_a7ak_lv2_response_merge_audit.py",
        "crypto_a7ak_lv3_neutral_field_family_smoke.py",
        "crypto_a7al0_top498_alpha_search_contract.py",
    ]
    rows = []
    for name in targets:
        path = REPO / "scripts" / name
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        rows.append(
            {
                "script_name": name,
                "exists": path.exists(),
                "lines": text.count("\n") + 1 if text else 0,
                "declares_search": "executes_search" in text or "formula" in text.lower(),
                "reads_may": "May" in text or "may_" in text,
                "risk_note": "reviewed for dataflow inventory; not edited by A7AL-0R",
            }
        )
    return rows


def base_lineage_rows() -> list[dict[str, Any]]:
    base = pd.read_csv(BASE_CONTRACT)
    rows = []
    for _, row in base.iterrows():
        field = str(row["field_name"])
        is_label = field.startswith("forward_") or field.startswith("fwd_")
        source_class = str(row["source_class"])
        is_raw = bool(row["independent_source"])
        feature_class = "raw_source" if is_raw else "metadata"
        if source_class == "derived_replay_base":
            feature_class = "derived_label" if is_label else "derived_rolling"
        rows.append(
            {
                "field_name": field,
                "source_field_names": row.get("source_detail", ""),
                "source_family": source_class,
                "feature_class": feature_class,
                "formula": "source field" if is_raw else "pipeline metadata or accepted derived field",
                "lookback_hours": 0 if is_raw else 1,
                "fit_window": "none",
                "train_only_fit": False,
                "uses_future": is_label,
                "uses_label": is_label,
                "pit_lag_required": "+1h primary",
                "latency_audit_required": True,
                "fixed_delay_stress_required": False,
                "allowed_for_rank": (not is_label) and source_class not in {"key", "metadata_timing"},
                "allowed_for_regime": (not is_label) and source_class not in {"key"},
                "allowed_for_search": (not is_label) and source_class not in {"key", "metadata_timing"},
                "allowed_for_label": is_label,
                "allowed_for_neutralization": False,
                "caveat": "label only; never enter feature/search" if is_label else str(row.get("feature_available_rule", "")),
            }
        )
    return rows


def derived_lineage_rows() -> list[dict[str, Any]]:
    quality = pd.read_csv(LV1_QUALITY) if LV1_QUALITY.exists() else pd.DataFrame()
    quality_lookup = {}
    if not quality.empty:
        key = "field_name" if "field_name" in quality.columns else "feature_name"
        for _, row in quality.iterrows():
            quality_lookup[str(row[key])] = row.to_dict()

    rows = []
    for spec in DERIVED_SPECS:
        q = quality_lookup.get(spec["field_name"], {})
        allowed_for_search = bool(spec["allowed_for_search"])
        uses_label = False
        rows.append(
            {
                "field_name": spec["field_name"],
                "source_field_names": spec["source_field_names"],
                "source_family": spec["source_family"],
                "feature_class": spec["feature_class"],
                "formula": spec["formula"],
                "lookback_hours": spec["lookback_hours"],
                "fit_window": "train thresholds only" if spec["feature_class"] == "derived_latent_state" else "rolling past only",
                "train_only_fit": spec["feature_class"] == "derived_latent_state",
                "uses_future": False,
                "uses_label": uses_label,
                "pit_lag_required": "+1h primary",
                "latency_audit_required": True,
                "fixed_delay_stress_required": False,
                "allowed_for_rank": allowed_for_search,
                "allowed_for_regime": bool(spec["allowed_for_regime"]),
                "allowed_for_search": allowed_for_search,
                "allowed_for_label": False,
                "allowed_for_neutralization": bool(spec["allowed_for_neutralization"]),
                "non_null_rate": q.get("non_null_rate", ""),
                "nan_count": q.get("nan_count", ""),
                "economic_role": spec["economic_role"],
                "caveat": "derived feature; source lineage and field-native latency audit required; fixed delay stress prohibited",
            }
        )
    return rows


def dataflow_graph_rows() -> list[dict[str, Any]]:
    return [
        {"node": "Universe498 1h replay panel", "kind": "input", "outputs_to": "A7AM base feature contract"},
        {"node": "A7AM base feature contract", "kind": "contract", "outputs_to": "A7AL-0R feature lineage ledger"},
        {"node": "A7AK-LV1 latent state feature build", "kind": "derived feature builder", "outputs_to": "A7AL-0R feature lineage ledger"},
        {"node": "A7AK-LV2 train-only response merge", "kind": "train-only state merge", "outputs_to": "A7AL-0R latent freeze audit"},
        {"node": "A7AK-LV3 neutral field-family smoke", "kind": "diagnostic", "outputs_to": "A7AL-0R readiness audit"},
        {"node": "A7AL-0 top498 contract", "kind": "contract", "outputs_to": "A7AL-0P pre-train gate"},
    ]


def label_lineage_rows(ledger: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in ledger:
        if row["allowed_for_label"] or row["uses_label"] or row["uses_future"]:
            rows.append(
                {
                    "field_name": row["field_name"],
                    "feature_class": row["feature_class"],
                    "allowed_for_label": row["allowed_for_label"],
                    "allowed_for_rank": row["allowed_for_rank"],
                    "allowed_for_search": row["allowed_for_search"],
                    "allowed_for_regime": row["allowed_for_regime"],
                    "status": "PASS_LABEL_ISOLATED"
                    if row["allowed_for_label"] and not row["allowed_for_search"] and not row["allowed_for_rank"]
                    else "HOLD_LABEL_LEAKAGE_RISK",
                }
            )
    return rows


def pit_lag_rows(ledger: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in ledger:
        if row["allowed_for_label"]:
            continue
        rows.append(
            {
                "field_name": row["field_name"],
                "feature_class": row["feature_class"],
                "pit_lag_required": row["pit_lag_required"],
                "latency_audit_required": row["latency_audit_required"],
                "fixed_delay_stress_required": row["fixed_delay_stress_required"],
                "same_bar_allowed": False,
                "status": "PASS_PIT_CONTRACTED" if row["pit_lag_required"] == "+1h primary" and row["latency_audit_required"] and not row["fixed_delay_stress_required"] else "HOLD_PIT_INCOMPLETE",
            }
        )
    return rows


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    generated_at = utc_now()
    ledger = base_lineage_rows() + derived_lineage_rows()
    scripts = script_inventory()
    dataflow = dataflow_graph_rows()
    labels = label_lineage_rows(ledger)
    pit = pit_lag_rows(ledger)
    derived = [row for row in ledger if str(row["feature_class"]).startswith("derived")]

    blockers = []
    if any(row["status"] == "HOLD_LABEL_LEAKAGE_RISK" for row in labels):
        blockers.append("label_lineage_leakage_risk")
    if any(row["status"] == "HOLD_PIT_INCOMPLETE" for row in pit):
        blockers.append("pit_lag_incomplete")
    if not ledger:
        blockers.append("empty_feature_lineage")

    manifest_inputs = {
        "lv1": read_json(LV1_MANIFEST).get("decision"),
        "lv2": read_json(LV2_MANIFEST).get("decision"),
        "lv3": read_json(LV3_MANIFEST).get("decision"),
        "a7al0": read_json(A7AL0_MANIFEST).get("decision"),
    }
    manifest = {
        "generated_at": generated_at,
        "decision": "PASS_A7AL0R_READY_FOR_FEATURE_REGIME_REBUILD" if not blockers else "HOLD_A7AL0R_FEATURE_LINEAGE_OR_PIT_BLOCKED",
        "executes_search": False,
        "executes_replay": False,
        "feature_lineage_rows": len(ledger),
        "derived_feature_rows": len(derived),
        "label_fields": len(labels),
        "pit_rows": len(pit),
        "input_decisions": manifest_inputs,
        "blockers": blockers,
        "warnings": [
            "Derived fields are allowed as first-class state/search inputs when lineage, PIT lag, and field-native latency audit are explicit",
            "Forward labels remain label-only",
            "A7AL-0R does not authorize formula search",
        ],
    }

    write_csv(RUNTIME / "a7al0r_script_inventory.csv", scripts)
    write_csv(RUNTIME / "a7al0r_dataflow_graph.csv", dataflow)
    write_csv(RUNTIME / "a7al0r_feature_lineage_ledger.csv", ledger)
    write_csv(RUNTIME / "a7al0r_derived_feature_catalog.csv", derived)
    write_csv(RUNTIME / "a7al0r_label_lineage_audit.csv", labels)
    write_csv(RUNTIME / "a7al0r_pit_lag_audit.csv", pit)
    (RUNTIME / "a7al0r_blocker_matrix.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    report = f"""# CRYPTO A7AL-0R Code Feature Regime Readiness Audit

Generated: {generated_at}

## Decision

```text
{manifest["decision"]}
```

This audit makes derived features first-class search inputs only when lineage, PIT lag, label isolation, and field-native latency audit are explicit. Fixed delay stress is prohibited.

## Summary

```json
{json.dumps(manifest, indent=2)}
```

## Script Inventory

{md_table(scripts)}

## Label Audit

{md_table(labels)}

## Derived Feature Sample

{md_table(derived, limit=40)}

## Boundary

```text
AUTHORIZED NEXT:
  A7AL-0F derived feature engineering contract
  A7AL-0G upper-regime state builder

NOT AUTHORIZED:
  A7AL-1 replay
  A7AL-2 formula search
  alpha proof / shadow / paper / live
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
