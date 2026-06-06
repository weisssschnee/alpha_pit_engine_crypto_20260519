from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7al2x5_evaluator_preflight_smoke import (  # noqa: E402
    BASE_DIR,
    LATENT_PANEL,
    UPPER_REGIME_PANEL,
    load_base,
    load_latent_numeric,
    parquet_schema,
    rolling_mean,
    strict_symbols,
)
from scripts.crypto_a7ff25r6_dense_funding_state_audit import (  # noqa: E402
    dense_ffill_and_age,
    rolling_mean_std_z,
    shift_matrix as dense_shift_matrix,
)
from scripts.crypto_a7ls2_sharded_materialization_wave import A7AB4Evaluator, expression_fields  # noqa: E402
from alphafactory_crypto.engines.feature_algebra import parse_call  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ls16_local_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7LS16_LOCAL_PREFLIGHT_20260606.md"
A7LS15 = REPO / "runtime" / "a7ls15_million_scale_blueprint_generation" / "a7ls15_manifest.json"

FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
OPERATORS = {
    "Mean", "Delta", "TSRank", "Decay", "Rank", "CSRank", "ZScore",
    "Mul", "Sub", "Add", "Neg", "Abs", "Sign", "SafeDiv", "Clip", "Winsor",
}
MIN_FINITE_SHARE = 0.20
MIN_NONZERO_SHARE = 0.01
SAMPLE_ROWS = 256
SYMBOL_CAP = 96
TIMESTAMP_CAP = 1024
DENSE_FUNDING_FIELDS = {
    "funding_rate_state_last_ffill_8h",
    "funding_rate_update_age_hours",
    "funding_rate_abs_state_168h_z",
    "funding_rate_delta_state_24h",
    "funding_state_x_basis_delta",
}

UPPER_ALIASES = {
    "market_breadth_state": "R2_market_breadth_state",
    "liquidity_cycle_state": "R3_liquidity_cycle_state",
    "leverage_crowding_state": "R4_leverage_crowding_state",
    "basis_dislocation_state": "R5_basis_premium_dislocation_state",
    "stress_proxy_state": "R10_stress_proxy_state",
}

DERIVED_DEPS = {
    "open_interest_value_change_24h": {"open_interest_value_last"},
    "funding_rate_persistence_24h": {"funding_rate"},
    "premium_abs_state": {"premium_close_bps"},
    "account_position_divergence": {"top_long_short_position_ratio_last", "top_long_short_account_ratio_last"},
    "top_global_account_divergence": {"top_long_short_account_ratio_last", "global_long_short_account_ratio_last"},
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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
    return view.to_markdown(index=False)


def balanced_sample(queue: pd.DataFrame, target: int) -> pd.DataFrame:
    pieces: list[pd.DataFrame] = []
    per_lane = max(1, target // max(1, queue["a7ls_lane"].nunique()))
    for _, lane_df in queue.groupby("a7ls_lane", sort=True):
        sems = sorted(lane_df["semantic_pair"].dropna().astype(str).unique().tolist())
        per_sem = max(1, per_lane // max(1, len(sems)))
        lane_parts: list[pd.DataFrame] = []
        for sem in sems:
            part = lane_df[lane_df["semantic_pair"].astype(str).eq(sem)].head(per_sem)
            lane_parts.append(part)
        lane_sample = pd.concat(lane_parts, ignore_index=True) if lane_parts else lane_df.head(0)
        if len(lane_sample) < per_lane:
            extra = lane_df[~lane_df["blueprint_id"].isin(set(lane_sample["blueprint_id"]))].head(per_lane - len(lane_sample))
            lane_sample = pd.concat([lane_sample, extra], ignore_index=True)
        pieces.append(lane_sample.head(per_lane))
    out = pd.concat(pieces, ignore_index=True).drop_duplicates("blueprint_id") if pieces else queue.head(0)
    if len(out) < target:
        extra = queue[~queue["blueprint_id"].isin(set(out["blueprint_id"]))].head(target - len(out))
        out = pd.concat([out, extra], ignore_index=True)
    return out.head(target).copy()


def requested_fields(queue: pd.DataFrame) -> set[str]:
    fields: set[str] = set()
    for expr in queue["expression"].astype(str):
        fields.update(expression_fields(expr))
    return fields


def expression_operators(expression: str) -> set[str]:
    return {match.group(1) for match in re.finditer(r"([A-Za-z][A-Za-z0-9_]*)\(", str(expression))}


def schema_field_status(fields: set[str]) -> dict[str, str]:
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    upper_schema = parquet_schema(UPPER_REGIME_PANEL)
    status: dict[str, str] = {}
    for field in sorted(fields):
        if field in base_schema:
            status[field] = "base"
        elif field in latent_schema:
            status[field] = "latent"
        elif field in upper_schema:
            status[field] = "upper_regime"
        elif field in DENSE_FUNDING_FIELDS:
            status[field] = "computed_dense_funding"
        elif field in UPPER_ALIASES and UPPER_ALIASES[field] in upper_schema:
            status[field] = f"upper_regime_alias:{UPPER_ALIASES[field]}"
        elif field in DERIVED_DEPS:
            deps = DERIVED_DEPS[field]
            missing_deps = [
                dep for dep in deps
                if dep not in base_schema and dep not in latent_schema and dep not in upper_schema
            ]
            status[field] = "computed_derived" if not missing_deps else "missing_dependency:" + ";".join(missing_deps)
        else:
            status[field] = "missing"
    return status


def categorical_or_numeric(values: pd.Series, mapping: dict[Any, float]) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.notna().any():
        return numeric
    return values.map(mapping).astype("float64")


def load_upper_numeric(symbols: list[str], timestamps: pd.DatetimeIndex, fields: set[str]) -> dict[str, np.ndarray]:
    if not fields:
        return {}
    frame = pd.read_parquet(UPPER_REGIME_PANEL, columns=["timestamp", *sorted(fields)], engine="pyarrow")
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame.sort_values("timestamp").drop_duplicates("timestamp").set_index("timestamp")
    out: dict[str, np.ndarray] = {}
    for field in fields:
        unique_values = sorted(frame[field].dropna().astype(str).unique().tolist())
        mapping = {value: float(idx - (len(unique_values) - 1) / 2.0) for idx, value in enumerate(unique_values)}
        series = categorical_or_numeric(frame[field], mapping).reindex(timestamps)
        out[field] = np.tile(series.to_numpy(dtype=np.float64), (len(symbols), 1))
    return out


def load_numeric(fields: set[str]) -> tuple[dict[str, np.ndarray], dict[str, str], list[str], pd.DatetimeIndex]:
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    upper_schema = parquet_schema(UPPER_REGIME_PANEL)
    requested = set(fields)
    alias_upper_fields = {UPPER_ALIASES[field] for field in requested if field in UPPER_ALIASES}
    derived_fields = set(requested) & set(DERIVED_DEPS)
    derived_deps = set().union(*(DERIVED_DEPS[field] for field in derived_fields)) if derived_fields else set()
    fields = (requested - set(UPPER_ALIASES) - derived_fields) | alias_upper_fields | derived_deps
    dense = fields & DENSE_FUNDING_FIELDS
    base_fields = {field for field in fields if field in base_schema}
    latent_fields = {field for field in fields if field in latent_schema and field not in base_fields}
    upper_fields = {field for field in fields if field in upper_schema and field not in base_fields and field not in latent_fields}
    if dense:
        base_fields.add("funding_rate")
        if "funding_state_x_basis_delta" in dense:
            base_fields.add("mark_index_basis_bps")
    missing = sorted(fields - base_fields - latent_fields - upper_fields - dense)
    field_status = {field: "base" for field in base_fields}
    field_status.update({field: "latent" for field in latent_fields})
    field_status.update({field: "upper_regime" for field in upper_fields})
    field_status.update({field: "computed_dense_funding" for field in dense})
    field_status.update({field: "missing" for field in missing})
    for alias, source in UPPER_ALIASES.items():
        if alias in requested:
            field_status[alias] = f"upper_regime_alias:{source}"
    for field in derived_fields:
        field_status[field] = "computed_derived"
    symbols = strict_symbols()[:SYMBOL_CAP]
    loaded_symbols, timestamps, numeric = load_base(symbols, base_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_fields))
    numeric.update(load_upper_numeric(loaded_symbols, timestamps, upper_fields))
    for alias, source in UPPER_ALIASES.items():
        if alias in requested and source in numeric:
            numeric[alias] = numeric[source]
    if dense:
        raw_funding = numeric["funding_rate"]
        dense_funding, funding_age = dense_ffill_and_age(raw_funding, 8)
        numeric["funding_rate_state_last_ffill_8h"] = dense_funding
        numeric["funding_rate_update_age_hours"] = funding_age
        if "funding_rate_abs_state_168h_z" in dense:
            numeric["funding_rate_abs_state_168h_z"] = rolling_mean_std_z(np.abs(dense_funding), 168, 48)
        if "funding_rate_delta_state_24h" in dense or "funding_state_x_basis_delta" in dense:
            funding_delta_24h = dense_funding - dense_shift_matrix(dense_funding, 24)
            numeric["funding_rate_delta_state_24h"] = funding_delta_24h
        if "funding_state_x_basis_delta" in dense:
            basis = numeric["mark_index_basis_bps"]
            numeric["funding_state_x_basis_delta"] = funding_delta_24h * (basis - dense_shift_matrix(basis, 24))
    if "open_interest_value_change_24h" in derived_fields:
        values = numeric["open_interest_value_last"]
        numeric["open_interest_value_change_24h"] = values - dense_shift_matrix(values, 24)
    if "funding_rate_persistence_24h" in derived_fields:
        numeric["funding_rate_persistence_24h"] = rolling_mean(numeric["funding_rate"], 24)
    if "premium_abs_state" in derived_fields:
        numeric["premium_abs_state"] = np.abs(numeric["premium_close_bps"])
    if "account_position_divergence" in derived_fields:
        numeric["account_position_divergence"] = numeric["top_long_short_position_ratio_last"] - numeric["top_long_short_account_ratio_last"]
    if "top_global_account_divergence" in derived_fields:
        numeric["top_global_account_divergence"] = numeric["top_long_short_account_ratio_last"] - numeric["global_long_short_account_ratio_last"]
    if len(timestamps) > TIMESTAMP_CAP:
        idx = np.linspace(0, len(timestamps) - 1, TIMESTAMP_CAP).round().astype(int)
        timestamps = timestamps[idx]
        numeric = {field: values[:, idx] for field, values in numeric.items()}
    return numeric, field_status, loaded_symbols, timestamps


def rolling_tsrank_safe(values: np.ndarray, window: int) -> np.ndarray:
    w = max(1, int(window))
    min_periods = max(1, min(w, 24))
    out = np.full_like(values, np.nan, dtype=np.float64)
    for symbol_idx in range(values.shape[0]):
        series = pd.Series(values[symbol_idx])
        out[symbol_idx] = series.rolling(window=w, min_periods=min_periods).rank(pct=True).to_numpy(dtype=np.float64)
    return out


class A7LS16Evaluator(A7AB4Evaluator):
    def _eval(self, expression: str) -> np.ndarray:
        call = parse_call(expression)
        if call is not None:
            name, args = call
            if name == "TSRank":
                return rolling_tsrank_safe(self.eval(args[0]), int(args[1]))
        return super()._eval(expression)


def build() -> dict[str, Any]:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    manifest15 = read_json(A7LS15)
    if manifest15.get("decision") != "PASS_A7LS15_MILLION_SCALE_BLUEPRINT_GENERATION_READY_FOR_A7LS16":
        raise SystemExit(f"A7LS15 not ready: {manifest15.get('decision')}")

    queue_path = Path(manifest15["materialization_queue_path"])
    queue = pd.read_csv(queue_path, low_memory=False)
    sample = balanced_sample(queue, SAMPLE_ROWS)
    sample.to_csv(RUNTIME / "a7ls16_preflight_sample.csv", index=False)

    fields = requested_fields(sample)
    operators = sorted({op for expr in sample["expression"].astype(str) for op in expression_operators(expr)})
    unsupported_operators = [op for op in operators if op not in OPERATORS]
    run_numeric_smoke = os.environ.get("A7LS16_RUN_NUMERIC_SMOKE", "0").strip().lower() in {"1", "true", "yes"}

    if not run_numeric_smoke:
        field_status = schema_field_status(fields)
        field_audit = pd.DataFrame([{"field": field, "status": status} for field, status in sorted(field_status.items())])
        field_audit.to_csv(RUNTIME / "a7ls16_field_schema_audit.csv", index=False)
        operator_audit = pd.DataFrame(
            [{"operator": op, "status": "supported" if op in OPERATORS else "unsupported"} for op in operators]
        )
        operator_audit.to_csv(RUNTIME / "a7ls16_operator_audit.csv", index=False)
        metrics = sample[["blueprint_id", "a7ls_lane", "semantic_pair", "motif"]].copy()
        metrics["eval_success"] = pd.NA
        metrics["finite_share"] = pd.NA
        metrics["nonzero_share"] = pd.NA
        metrics["activity_ok"] = pd.NA
        metrics["std_value"] = pd.NA
        metrics["error"] = "numeric_smoke_not_run_local_schema_preflight_only"
        metrics.to_csv(RUNTIME / "a7ls16_materialization_smoke_metrics.csv", index=False)
        lane_summary = (
            sample.groupby("a7ls_lane", dropna=False)
            .agg(
                rows=("blueprint_id", "count"),
                semantic_pairs=("semantic_pair", "nunique"),
                motifs=("motif", "nunique"),
                skeletons=("skeleton_key", "nunique"),
            )
            .reset_index()
        )
        lane_summary.to_csv(RUNTIME / "a7ls16_lane_preflight_summary.csv", index=False)
        missing_count = int(field_audit["status"].astype(str).str.startswith("missing").sum())
        unsupported_operator_count = int(operator_audit["status"].eq("unsupported").sum())
        blockers: list[str] = []
        if missing_count:
            blockers.append("missing_fields")
        if unsupported_operator_count:
            blockers.append("unsupported_operators")
        decision = "PASS_A7LS16_LOCAL_SCHEMA_PREFLIGHT_READY_FOR_A7LS17_COMPANY_MATERIALIZATION" if not blockers else "HOLD_A7LS16_LOCAL_PREFLIGHT_REPAIR_REQUIRED"
        manifest = {
            "stage": "A7LS-16",
            "generated_at": now_iso(),
            "decision": decision,
            "blockers": blockers,
            "input_stage": "A7LS-15",
            "preflight_mode": "local_schema_queue_preflight",
            "sample_rows": int(len(sample)),
            "requested_field_count": int(len(fields)),
            "missing_field_count": missing_count,
            "operator_count": int(len(operators)),
            "unsupported_operator_count": unsupported_operator_count,
            "lane_count": int(sample["a7ls_lane"].nunique()),
            "authorizes_a7ls17_company_materialization": decision.startswith("PASS_"),
            "authorizes_a7ls18_company_numeric": False,
            "authorizes_alpha_proof": False,
            "authorizes_shadow_paper_live": False,
            "uses_may": False,
        }
        write_json(RUNTIME / "a7ls16_manifest.json", manifest)
        REPORT.write_text(
            "\n".join(
                [
                    "# CRYPTO A7LS-16 LOCAL PREFLIGHT",
                    "",
                    f"Generated: {manifest['generated_at']}",
                    "",
                    "## Decision",
                    "",
                    f"`{decision}`",
                    "",
                    "## Mode",
                    "",
                    "Local schema/queue preflight only. Numeric materialization smoke is intentionally not run on the local machine by default; A7LS17 handles company-machine materialization.",
                    "",
                    "## Summary",
                    "",
                    f"- sample_rows: {len(sample)}",
                    f"- requested_field_count: {len(fields)}",
                    f"- missing_field_count: {missing_count}",
                    f"- operator_count: {len(operators)}",
                    f"- unsupported_operator_count: {unsupported_operator_count}",
                    "",
                    "## Lane Summary",
                    "",
                    md_table(lane_summary),
                    "",
                    "## Field Status",
                    "",
                    md_table(field_audit.groupby('status').size().reset_index(name='fields')),
                    "",
                    "## Operator Status",
                    "",
                    md_table(operator_audit),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return manifest

    numeric, field_status, symbols, timestamps = load_numeric(fields)
    field_rows = [{"field": field, "status": status} for field, status in sorted(field_status.items())]
    field_audit = pd.DataFrame(field_rows)
    field_audit.to_csv(RUNTIME / "a7ls16_field_schema_audit.csv", index=False)

    evaluator = A7LS16Evaluator(numeric, {})
    rows: list[dict[str, Any]] = []
    for row in sample.to_dict("records"):
        expr = str(row["expression"])
        expr_fields = expression_fields(expr)
        missing = sorted(field for field in expr_fields if field_status.get(field) == "missing")
        try:
            if missing:
                raise ValueError("missing_fields:" + ";".join(missing))
            values = evaluator.eval(expr)
            finite = np.isfinite(values)
            finite_share = float(finite.mean()) if values.size else 0.0
            nonzero_share = float((np.abs(values[finite]) > 1e-12).mean()) if finite.any() else 0.0
            eval_success = True
            error = ""
            std_value = float(np.nanstd(values)) if finite.any() else np.nan
        except Exception as exc:  # noqa: BLE001
            finite_share = 0.0
            nonzero_share = 0.0
            eval_success = False
            error = repr(exc)
            std_value = np.nan
        rows.append(
            {
                "blueprint_id": row["blueprint_id"],
                "a7ls_lane": row["a7ls_lane"],
                "semantic_pair": row["semantic_pair"],
                "motif": row["motif"],
                "eval_success": eval_success,
                "finite_share": finite_share,
                "nonzero_share": nonzero_share,
                "activity_ok": bool(eval_success and finite_share >= MIN_FINITE_SHARE and nonzero_share >= MIN_NONZERO_SHARE),
                "std_value": std_value,
                "error": error,
            }
        )
    metrics = pd.DataFrame(rows)
    metrics.to_csv(RUNTIME / "a7ls16_materialization_smoke_metrics.csv", index=False)

    lane_summary = (
        metrics.groupby("a7ls_lane", dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            eval_success_rows=("eval_success", "sum"),
            activity_ok_rows=("activity_ok", "sum"),
            median_finite_share=("finite_share", "median"),
            median_nonzero_share=("nonzero_share", "median"),
        )
        .reset_index()
    )
    lane_summary["eval_success_rate"] = lane_summary["eval_success_rows"] / lane_summary["rows"]
    lane_summary["activity_ok_rate"] = lane_summary["activity_ok_rows"] / lane_summary["rows"]
    lane_summary.to_csv(RUNTIME / "a7ls16_lane_preflight_summary.csv", index=False)

    error_summary = (
        metrics.loc[~metrics["eval_success"]]
        .groupby("error", dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values("rows", ascending=False)
    )
    error_summary.to_csv(RUNTIME / "a7ls16_error_summary.csv", index=False)

    blockers: list[str] = []
    missing_count = int(field_audit["status"].eq("missing").sum())
    eval_failure_count = int((~metrics["eval_success"]).sum())
    activity_ok_rate = float(metrics["activity_ok"].mean()) if len(metrics) else 0.0
    if missing_count:
        blockers.append("missing_fields")
    if eval_failure_count:
        blockers.append("eval_failure_count_nonzero")
    if activity_ok_rate < 0.60:
        blockers.append("activity_ok_rate_below_0p60")
    if int(lane_summary["activity_ok_rows"].gt(0).sum()) < 3:
        blockers.append("active_lane_count_lt_3")
    decision = "PASS_A7LS16_LOCAL_PREFLIGHT_READY_FOR_A7LS17_COMPANY_MATERIALIZATION" if not blockers else "HOLD_A7LS16_LOCAL_PREFLIGHT_REPAIR_REQUIRED"

    manifest = {
        "stage": "A7LS-16",
        "generated_at": now_iso(),
        "decision": decision,
        "blockers": blockers,
        "input_stage": "A7LS-15",
        "sample_rows": int(len(sample)),
        "requested_field_count": int(len(fields)),
        "missing_field_count": missing_count,
        "eval_failure_count": eval_failure_count,
        "activity_ok_rate": activity_ok_rate,
        "loaded_symbol_count": int(len(symbols)),
        "timestamp_count": int(len(timestamps)),
        "authorizes_a7ls17_company_materialization": decision.startswith("PASS_"),
        "authorizes_a7ls18_company_numeric": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may": False,
    }
    write_json(RUNTIME / "a7ls16_manifest.json", manifest)

    REPORT.write_text(
        "\n".join(
            [
                "# CRYPTO A7LS-16 LOCAL PREFLIGHT",
                "",
                f"Generated: {manifest['generated_at']}",
                "",
                "## Decision",
                "",
                f"`{decision}`",
                "",
                "## Summary",
                "",
                f"- sample_rows: {len(sample)}",
                f"- requested_field_count: {len(fields)}",
                f"- missing_field_count: {missing_count}",
                f"- eval_failure_count: {eval_failure_count}",
                f"- activity_ok_rate: {activity_ok_rate:.4f}",
                "",
                "## Lane Summary",
                "",
                md_table(lane_summary),
                "",
                "## Field Status",
                "",
                md_table(field_audit.groupby('status').size().reset_index(name='fields')),
                "",
                "## Error Summary",
                "",
                md_table(error_summary),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
