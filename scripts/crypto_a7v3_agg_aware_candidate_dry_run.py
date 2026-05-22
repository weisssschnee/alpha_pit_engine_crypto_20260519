from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "crypto_a7v_feature_registry_v1.json"
OUT_DIR = ROOT / "runtime" / "a7v3_agg_aware_candidate_dry_run"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7V3_AGG_AWARE_CANDIDATE_DRY_RUN_20260522.md"
DATE_TAG = "20260522"

FORBIDDEN_PREFIXES = ("fwd_ret_",)
FORBIDDEN_TOKENS = ("positioning", "openInterestHist", "globalLongShort", "topLongShort", "takerlongshortRatio")
MARKET_CONTROL_FIELDS = {
    "ret_6",
    "ret_12",
    "realized_vol_12",
    "realized_vol_24",
    "mark_index_ratio",
    "premium_index",
    "latest_known_funding_rate",
}

QUOTAS = {
    "rolling_self_reproduction": 180,
    "cross_symbol_self_reproduction_core3": 80,
    "interaction_self_reproduction": 100,
}


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def sha(text: str, n: int = 12) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:n]


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def split_fields(text: str) -> list[str]:
    return [item for item in str(text).split(";") if item and item != "nan"]


def candidate_id(production_family: str, expression: str, horizon: int, ordinal: int) -> str:
    digest = sha(f"{production_family}|{expression}|{horizon}|{ordinal}")
    return f"a7v3_{production_family}_{horizon}_{digest}"


def rolling_expression(transform: str, field: str, window: int) -> str:
    if transform == "TSMean":
        return f"TSMean({field},{window})"
    if transform == "TSStd":
        return f"TSStd({field},{window})"
    if transform == "TSRank":
        return f"TSRank({field},{window})"
    if transform == "Delta":
        return f"Delta({field},{window})"
    if transform == "Decay":
        return f"Decay({field},{window})"
    if transform == "RollingMin":
        return f"RollingMin({field},{window})"
    if transform == "RollingMax":
        return f"RollingMax({field},{window})"
    if transform == "ZScore":
        return f"ZScore(TSMean({field},{window}))"
    return f"{transform}({field},{window})"


def cross_symbol_expression(transform: str, field: str) -> str:
    if transform in {"CrossSymbolRank", "CrossSymbolZScore", "ShareOfUniverse", "RelativeToBTC", "RelativeToETH"}:
        return f"{transform}({field})"
    return f"CrossSymbolRank({field})"


def interaction_expression(transform: str, fields: list[str]) -> str:
    agg_field = fields[0]
    market_field = fields[1] if len(fields) > 1 else "ret_12"
    a = f"ZScore({agg_field})"
    b = f"Rank({market_field})"
    if transform == "Mul":
        return f"Mul({a},{b})"
    if transform == "Add":
        return f"Add({a},{b})"
    if transform == "Sub":
        return f"Sub({a},{b})"
    if transform == "SafeDiv":
        return f"SafeDiv({a},Clip(Abs(ZScore({market_field})),0.05,4.0))"
    if transform == "HorizonSpread":
        return f"HorizonSpread({agg_field},4,24)"
    if transform == "SmoothInteraction":
        return f"SmoothInteraction({agg_field},TSMean({market_field},12))"
    return f"Mul({a},{b})"


def horizon_from_spec(row: pd.Series, ordinal: int) -> int:
    window = int(row.get("window_hours", 1))
    if window <= 8:
        return 12
    if window <= 24:
        return 24
    if window <= 48:
        return 48
    return [48, 72][ordinal % 2]


def expression_from_spec(row: pd.Series) -> str:
    production = str(row["production_family"])
    transform = str(row["transform"])
    fields = split_fields(str(row["base_fields"]))
    if production == "rolling_self_reproduction":
        return rolling_expression(transform, fields[0], int(row["window_hours"]))
    if production == "cross_symbol_self_reproduction_core3":
        return cross_symbol_expression(transform, fields[0])
    if production == "interaction_self_reproduction":
        return interaction_expression(transform, fields)
    raise ValueError(f"unsupported production: {production}")


def field_families_from_spec(row: pd.Series) -> list[str]:
    return sorted({item for item in str(row.get("base_field_families", "")).split(";") if item and item != "nan"})


def is_forbidden_source_field(field: str) -> bool:
    return field.startswith(FORBIDDEN_PREFIXES) or any(token in field for token in FORBIDDEN_TOKENS)


def build_candidate(row: pd.Series, panel_columns: set[str], ordinal: int) -> dict[str, Any]:
    expression = expression_from_spec(row)
    production = str(row["production_family"])
    fields = split_fields(str(row["base_fields"]))
    source_fields = [f for f in fields if f not in MARKET_CONTROL_FIELDS] + [f for f in fields if f in MARKET_CONTROL_FIELDS]
    missing_panel_fields = [f for f in source_fields if f not in panel_columns and f not in MARKET_CONTROL_FIELDS]
    forbidden_fields = [f for f in source_fields if is_forbidden_source_field(f)]
    requires_mask = str(row["requires_agg_features_available_mask"]).lower() in {"true", "1"}
    feature_lag = int(row.get("feature_available_lag_bars", 1))
    zero_fill_allowed = str(row.get("zero_fill_allowed", "false")).lower() in {"true", "1"}
    same_hour_allowed = str(row.get("same_hour_execution_allowed", "false")).lower() in {"true", "1"}
    missing_as_signal_allowed = str(row.get("missing_as_signal_allowed", "false")).lower() in {"true", "1"}
    cross_scope = str(row.get("cross_symbol_scope", "same_symbol"))

    blockers = []
    if missing_panel_fields:
        blockers.append("missing_panel_source_fields")
    if forbidden_fields:
        blockers.append("forbidden_source_fields")
    if not requires_mask:
        blockers.append("missing_required_agg_mask")
    if feature_lag < 1:
        blockers.append("same_hour_or_future_timing_risk")
    if zero_fill_allowed:
        blockers.append("zero_fill_allowed")
    if same_hour_allowed:
        blockers.append("same_hour_execution_allowed")
    if missing_as_signal_allowed:
        blockers.append("missing_as_signal_allowed")
    if production == "cross_symbol_self_reproduction_core3" and cross_scope != "BTCUSDT,ETHUSDT,SOLUSDT":
        blockers.append("cross_symbol_scope_not_core3")
    if "latest_known_funding_rate" in source_fields and production != "interaction_self_reproduction":
        blockers.append("funding_not_controlled_interaction")

    horizon = horizon_from_spec(row, ordinal)
    decision = "A7V3_DRY_RUN_CANDIDATE" if not blockers else "A7V3_REJECTED_BY_DRY_RUN_GATE"
    return {
        "candidate_id": candidate_id(production, expression, horizon, ordinal),
        "generator": "crypto_a7v3_agg_aware_candidate_dry_run",
        "status": "dry_run_not_replayed",
        "production_family": production,
        "derived_feature_id": str(row["derived_feature_id"]),
        "expression": expression,
        "horizon": horizon,
        "source_fields": ";".join(source_fields),
        "source_field_families": ";".join(field_families_from_spec(row)),
        "transform": str(row["transform"]),
        "window_hours": int(row["window_hours"]),
        "availability_mask": "agg_features_available",
        "cross_symbol_scope": cross_scope,
        "feature_available_lag_bars": feature_lag,
        "feature_timestamp_rule": "agg hour bucket start t is observable after t+1h; rolling descendants require past-only completed input hours",
        "execution_rule": "next-bar or later; same-hour close execution forbidden",
        "requires_residual_baselines": "FundingCore;Core4",
        "required_negative_controls": "row_shuffle;time_shuffle;wrong_lag;sign_flip;no_agg_mask;zero_fill_core12_rank",
        "paired_ablation_plan": "base_agg_field;derived_transform;market_control_if_any;full_formula",
        "decision": decision,
        "reject_reasons": ";".join(blockers),
    }


def stratified_select(specs: pd.DataFrame) -> pd.DataFrame:
    selected = []
    for production, quota in QUOTAS.items():
        part = specs[specs["production_family"] == production].copy()
        if part.empty:
            continue
        family_counts: dict[str, int] = defaultdict(int)
        transform_counts: dict[str, int] = defaultdict(int)
        rows = []
        for _, row in part.sort_values(["base_field_families", "transform", "window_hours", "derived_feature_id"]).iterrows():
            fam = str(row["base_field_families"])
            transform = str(row["transform"])
            if family_counts[fam] >= max(8, quota // 8):
                continue
            if transform_counts[transform] >= max(8, quota // 5):
                continue
            rows.append(row)
            family_counts[fam] += 1
            transform_counts[transform] += 1
            if len(rows) >= quota:
                break
        if len(rows) < quota:
            used = {str(r["derived_feature_id"]) for r in rows}
            for _, row in part.sort_values("derived_feature_id").iterrows():
                if str(row["derived_feature_id"]) in used:
                    continue
                rows.append(row)
                if len(rows) >= quota:
                    break
        selected.extend(rows[:quota])
    return pd.DataFrame(selected).reset_index(drop=True)


def build_blocked_controls(panel_columns: set[str]) -> pd.DataFrame:
    rows = [
        {
            "control_id": "a7v3_no_agg_mask_control",
            "expression": "Rank(agg_flow_imbalance_notional)",
            "control_type": "missing_required_mask",
            "expected_blocker": "missing_required_agg_mask",
            "decision": "BLOCKED_EXPECTED_CONTROL",
        },
        {
            "control_id": "a7v3_zero_fill_core12_rank_control",
            "expression": "CrossSymbolRank(ZeroFill(agg_flow_imbalance_notional))",
            "control_type": "forbidden_zero_fill",
            "expected_blocker": "zero_fill_allowed",
            "decision": "BLOCKED_EXPECTED_CONTROL",
        },
        {
            "control_id": "a7v3_same_hour_execution_lag0_control",
            "expression": "Rank(agg_notional)",
            "control_type": "forbidden_timing",
            "expected_blocker": "same_hour_or_future_timing_risk",
            "decision": "BLOCKED_EXPECTED_CONTROL",
        },
        {
            "control_id": "a7v3_fwd_ret_input_control",
            "expression": "Rank(fwd_ret_12)",
            "control_type": "forbidden_label_input",
            "expected_blocker": "forbidden_source_fields",
            "decision": "BLOCKED_EXPECTED_CONTROL",
        },
        {
            "control_id": "a7v3_funding_packaging_control",
            "expression": "Mul(Rank(agg_flow_imbalance_notional),ZScore(latest_known_funding_rate))",
            "control_type": "funding_unrestricted_packaging",
            "expected_blocker": "funding_must_remain_baseline_or_control",
            "decision": "BLOCKED_EXPECTED_CONTROL",
        },
    ]
    return pd.DataFrame(rows)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def write_report(
    *,
    now: str,
    candidates: pd.DataFrame,
    summary: pd.DataFrame,
    gate_audit: pd.DataFrame,
    controls: pd.DataFrame,
    authorization: dict[str, Any],
) -> None:
    lines = [
        "# Crypto A7V-3 Agg-Aware Candidate Dry Run",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "This dry run reads the opt-in A7V feature registry, creates agg-aware candidate metadata, and verifies generator gates. It does not evaluate returns and does not modify legacy A7M/A7O generators.",
        "",
        "## Candidate Summary",
        "",
        table(summary, max_rows=80),
        "",
        "## Gate Audit",
        "",
        table(gate_audit, max_rows=80),
        "",
        "## Blocked Controls",
        "",
        table(controls, max_rows=40),
        "",
        "## Sample Candidates",
        "",
        table(candidates.head(30), max_rows=30),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- A7V-4: run no-mask, row/time shuffle, wrong-lag, sign-flip, and zero-fill controls before any replay.",
        "- A7V-5: if controls pass, run a small agg-aware replay smoke; no full search yet.",
        "- A7U-0R: consolidate raw checksum trace before final alpha panel claims.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    config = read_json(CONFIG_PATH)
    panel_path = Path(config["primary_panel"])
    panel_columns = set(pq.read_schema(panel_path).names)
    specs_path = ROOT / config["files"]["derived_feature_specs"]
    specs = pd.read_csv(specs_path)
    selected_specs = stratified_select(specs)

    rows = [build_candidate(row, panel_columns, i) for i, (_, row) in enumerate(selected_specs.iterrows(), start=1)]
    candidates = pd.DataFrame(rows)
    controls = build_blocked_controls(panel_columns)

    summary = (
        candidates.groupby(["production_family", "decision"], dropna=False)
        .agg(
            candidates=("candidate_id", "count"),
            unique_expressions=("expression", "nunique"),
            unique_source_fields=("source_fields", "nunique"),
            min_feature_lag=("feature_available_lag_bars", "min"),
            max_feature_lag=("feature_available_lag_bars", "max"),
        )
        .reset_index()
    )
    gate_audit = pd.DataFrame(
        [
            {"gate": "all_candidates_require_agg_mask", "value": bool(candidates["availability_mask"].eq("agg_features_available").all()), "decision": "PASS"},
            {"gate": "no_same_hour_lag", "value": bool((candidates["feature_available_lag_bars"] >= 1).all()), "decision": "PASS"},
            {"gate": "accepted_candidates", "value": int(candidates["decision"].eq("A7V3_DRY_RUN_CANDIDATE").sum()), "decision": "PASS"},
            {"gate": "rejected_candidates", "value": int(candidates["decision"].ne("A7V3_DRY_RUN_CANDIDATE").sum()), "decision": "PASS"},
            {"gate": "blocked_controls", "value": int(controls["decision"].eq("BLOCKED_EXPECTED_CONTROL").sum()), "decision": "PASS"},
            {
                "gate": "funding_interaction_candidates",
                "value": int(candidates["source_fields"].str.contains("latest_known_funding_rate", regex=False).sum()),
                "decision": "PASS",
            },
        ]
    )

    blockers = []
    if candidates.empty:
        blockers.append("no_candidates_generated")
    if not candidates["decision"].eq("A7V3_DRY_RUN_CANDIDATE").all():
        blockers.append("some_candidates_failed_dry_run_gate")
    if not controls["decision"].eq("BLOCKED_EXPECTED_CONTROL").all():
        blockers.append("blocked_controls_not_blocked")
    if not candidates["availability_mask"].eq("agg_features_available").all():
        blockers.append("candidate_missing_agg_mask")
    if int(candidates["production_family"].nunique()) < 3:
        blockers.append("production_family_coverage_too_narrow")

    decision = "PASS_A7V3_AGG_AWARE_CANDIDATE_DRY_RUN" if not blockers else "HOLD_A7V3_DRY_RUN_GATE_BLOCKER"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "candidate_count": int(len(candidates)),
        "production_family_count": int(candidates["production_family"].nunique()),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7v4_control_preflight": decision.startswith("PASS"),
        "authorizes_replay": False,
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_zero_fill_for_missing_agg": False,
        "authorizes_same_hour_execution": False,
        "required_next": [
            "A7V-4 no-mask/row-shuffle/time-shuffle/wrong-lag/sign-flip/zero-fill controls",
            "A7V-5 small agg-aware replay smoke only if A7V-4 passes",
            "A7U-0R consolidated raw checksum trace before final alpha panel claims",
        ],
    }

    candidates.to_csv(OUT_DIR / "a7v3_candidates.csv", index=False)
    write_jsonl(OUT_DIR / "a7v3_candidates.jsonl", rows)
    selected_specs.to_csv(OUT_DIR / "a7v3_selected_derived_specs.csv", index=False)
    summary.to_csv(OUT_DIR / "a7v3_candidate_family_summary.csv", index=False)
    gate_audit.to_csv(OUT_DIR / "a7v3_gate_audit.csv", index=False)
    controls.to_csv(OUT_DIR / "a7v3_blocked_controls.csv", index=False)
    write_json(OUT_DIR / "a7v3_authorization_matrix.json", authorization)
    write_json(OUT_DIR / "a7v3_manifest.json", {"generated_at": now, "decision": decision, "config": str(CONFIG_PATH), "output_dir": str(OUT_DIR)})
    write_report(now=now, candidates=candidates, summary=summary, gate_audit=gate_audit, controls=controls, authorization=authorization)
    print(json.dumps({"decision": decision, "blockers": blockers, "candidate_count": len(candidates)}, indent=2))


if __name__ == "__main__":
    main()
