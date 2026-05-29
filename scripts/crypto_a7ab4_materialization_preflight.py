from __future__ import annotations

import json
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

from scripts.crypto_a7al2x5_evaluator_preflight_smoke import (  # noqa: E402
    BASE_DIR,
    LATENT_PANEL,
    StateAwareEvaluator,
    load_base,
    load_latent_numeric,
    parquet_schema,
    parse_call,
    strict_symbols,
)


RUNTIME = REPO / "runtime" / "a7ab4_materialization_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7AB4_MATERIALIZATION_PREFLIGHT_20260529.md"

A7AB3_MANIFEST = REPO / "runtime" / "a7ab3_seed_constrained_dry_generation" / "a7ab3_manifest.json"
A7AB3_QUEUE = REPO / "runtime" / "a7ab3_seed_constrained_dry_generation" / "a7ab3_static_selected_queue.csv"

MIN_FINITE_SHARE = 0.20
MIN_NONZERO_SHARE = 0.01
TIMESTAMP_CAP = 4096


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
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


def split_pipe(value: Any) -> list[str]:
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]


def shift_matrix(values: np.ndarray, periods: int) -> np.ndarray:
    out = np.full_like(values, np.nan, dtype=np.float64)
    if periods == 0:
        return values.astype(np.float64, copy=True)
    if periods > 0:
        out[:, periods:] = values[:, :-periods]
    else:
        p = abs(periods)
        out[:, :-p] = values[:, p:]
    return out


def rolling_decay(values: np.ndarray, window: int) -> np.ndarray:
    w = max(1, int(window))
    min_periods = max(2, min(w, 24))
    numerator = np.zeros_like(values, dtype=np.float64)
    denom = np.zeros_like(values, dtype=np.float64)
    count = np.zeros_like(values, dtype=np.float64)
    for offset in range(w):
        weight = float(w - offset)
        shifted = shift_matrix(values, offset)
        valid = np.isfinite(shifted)
        numerator += np.where(valid, shifted * weight, 0.0)
        denom += np.where(valid, weight, 0.0)
        count += valid.astype(np.float64)
    out = np.full_like(values, np.nan, dtype=np.float64)
    np.divide(numerator, denom, out=out, where=(denom > 0) & (count >= min_periods))
    out[count < min_periods] = np.nan
    return out


def rolling_tsrank(values: np.ndarray, window: int) -> np.ndarray:
    w = max(1, int(window))
    min_periods = max(2, min(w, 24))
    out = np.full_like(values, np.nan, dtype=np.float64)
    for symbol_idx in range(values.shape[0]):
        series = pd.Series(values[symbol_idx])
        ranked = series.rolling(window=w, min_periods=min_periods).rank(pct=True)
        out[symbol_idx] = ranked.to_numpy(dtype=np.float64)
    return out


class A7AB4Evaluator(StateAwareEvaluator):
    def _eval(self, expression: str) -> np.ndarray:
        call = parse_call(expression)
        if call is not None:
            name, args = call
            if name == "TSRank":
                return rolling_tsrank(self.eval(args[0]), int(args[1]))
            if name == "Decay":
                return rolling_decay(self.eval(args[0]), int(args[1]))
        return super()._eval(expression)


def selected_fields(selected: pd.DataFrame) -> set[str]:
    fields: set[str] = set()
    for text in selected["source_fields"].dropna().astype(str):
        fields.update(split_pipe(text))
    return fields


def load_numeric_fields(
    fields: set[str],
    timestamp_cap: int | None = TIMESTAMP_CAP,
) -> tuple[list[str], pd.DatetimeIndex, dict[str, np.ndarray], list[str], int]:
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    base_fields = {field for field in fields if field in base_schema}
    latent_fields = {field for field in fields if field in latent_schema and field not in base_fields}
    missing = sorted(fields - base_fields - latent_fields)
    if missing:
        return [], pd.DatetimeIndex([]), {}, missing, 0
    symbols = strict_symbols()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_fields))
    full_timestamp_count = int(len(timestamps))
    if timestamp_cap and len(timestamps) > int(timestamp_cap):
        idx = np.arange(len(timestamps) - int(timestamp_cap), len(timestamps))
        timestamps = pd.DatetimeIndex(timestamps[idx])
        numeric = {key: value[:, idx] for key, value in numeric.items()}
    return loaded_symbols, timestamps, numeric, [], full_timestamp_count


def evaluate_candidate(evaluator: StateAwareEvaluator, row: dict[str, Any]) -> dict[str, Any]:
    expression = str(row["expression"])
    try:
        values = evaluator.eval(expression)
        finite = np.isfinite(values)
        finite_share = float(finite.mean()) if values.size else 0.0
        nonzero_share = float((np.abs(values[finite]) > 1e-12).mean()) if finite.any() else 0.0
        min_value = float(np.nanmin(values)) if finite.any() else np.nan
        max_value = float(np.nanmax(values)) if finite.any() else np.nan
        std_value = float(np.nanstd(values)) if finite.any() else np.nan
        eval_success = True
        error = ""
    except Exception as exc:  # noqa: BLE001 - materialization audit must record failures.
        finite_share = 0.0
        nonzero_share = 0.0
        min_value = np.nan
        max_value = np.nan
        std_value = np.nan
        eval_success = False
        error = repr(exc)
    activity_ok = eval_success and finite_share >= MIN_FINITE_SHARE and nonzero_share >= MIN_NONZERO_SHARE
    return {
        "candidate_id": row["candidate_id"],
        "family_id": row["family_id"],
        "primary_seed_field": row["primary_seed_field"],
        "source_fields": row["source_fields"],
        "skeleton_key": row["skeleton_key"],
        "production_key": row["production_key"],
        "motif": row["motif"],
        "expression": expression,
        "eval_success": eval_success,
        "finite_share": finite_share,
        "nonzero_share": nonzero_share,
        "activity_ok": activity_ok,
        "min_value": min_value,
        "max_value": max_value,
        "std_value": std_value,
        "error": error,
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ab3 = read_json(A7AB3_MANIFEST)
    if not a7ab3.get("authorizes_a7ab4_materialization_preflight"):
        raise SystemExit("A7AB-3 does not authorize A7AB-4")

    selected = pd.read_csv(A7AB3_QUEUE)
    fields = selected_fields(selected)
    loaded_symbols, timestamps, numeric, missing, full_timestamp_count = load_numeric_fields(fields)
    rows: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []

    if missing:
        for field in missing:
            blockers.append({"blocker": "missing_field", "candidate_id": "", "detail": field})
    else:
        evaluator = A7AB4Evaluator(numeric, {})
        for idx, row in enumerate(selected.to_dict("records"), start=1):
            result = evaluate_candidate(evaluator, row)
            rows.append(result)
            if not result["eval_success"]:
                blockers.append({"blocker": "eval_failure", "candidate_id": result["candidate_id"], "detail": result["error"]})
            elif not result["activity_ok"]:
                blockers.append(
                    {
                        "blocker": "activity_or_coverage_failure",
                        "candidate_id": result["candidate_id"],
                        "detail": f"finite={result['finite_share']:.6f};nonzero={result['nonzero_share']:.6f}",
                    }
                )
            if idx % 64 == 0:
                print(f"[A7AB-4] evaluated {idx}/{len(selected)}", flush=True)

    summary = pd.DataFrame(rows)
    blockers_df = pd.DataFrame(blockers)
    if summary.empty:
        summary = pd.DataFrame(
            columns=[
                "candidate_id",
                "family_id",
                "primary_seed_field",
                "source_fields",
                "skeleton_key",
                "production_key",
                "motif",
                "expression",
                "eval_success",
                "finite_share",
                "nonzero_share",
                "activity_ok",
                "min_value",
                "max_value",
                "std_value",
                "error",
            ]
        )

    family_summary = (
        summary.groupby("family_id", as_index=False).agg(
            evaluated_count=("candidate_id", "count"),
            eval_success_count=("eval_success", "sum"),
            activity_ok_count=("activity_ok", "sum"),
            median_finite_share=("finite_share", "median"),
            median_nonzero_share=("nonzero_share", "median"),
            skeleton_count=("skeleton_key", "nunique"),
            seed_field_count=("primary_seed_field", "nunique"),
        )
        if not summary.empty
        else pd.DataFrame()
    )
    motif_summary = (
        summary.groupby("motif", as_index=False).agg(
            evaluated_count=("candidate_id", "count"),
            activity_ok_count=("activity_ok", "sum"),
            median_finite_share=("finite_share", "median"),
            median_nonzero_share=("nonzero_share", "median"),
        )
        if not summary.empty
        else pd.DataFrame()
    )
    op_counts = Counter()
    for expr in selected["expression"].astype(str):
        # Simple lexical coverage; semantic eval is handled by StateAwareEvaluator.
        for token in ["Rank", "ZScore", "TSRank", "Delta", "Mean", "Decay", "Sub", "Mul", "Clip", "Winsor"]:
            if f"{token}(" in expr:
                op_counts[token] += 1
    operator_coverage = pd.DataFrame(
        [{"operator": key, "selected_candidate_count": value} for key, value in sorted(op_counts.items())]
    )

    eval_failure_count = int((~summary["eval_success"]).sum()) if not summary.empty else int(bool(missing))
    activity_failure_count = int((~summary["activity_ok"]).sum()) if not summary.empty else int(bool(missing))
    selected_count = int(len(selected))
    activity_ok_count = int(summary["activity_ok"].sum()) if not summary.empty else 0
    activity_ok_rate = float(activity_ok_count / selected_count) if selected_count else 0.0
    ok = (
        not missing
        and eval_failure_count == 0
        and activity_failure_count == 0
        and selected_count >= 512
        and int(summary["family_id"].nunique()) >= 4
        and int(summary["primary_seed_field"].nunique()) >= 5
        and int(summary["skeleton_key"].nunique()) >= 64
    )
    decision = (
        "PASS_A7AB4_MATERIALIZATION_PREFLIGHT_READY_FOR_A7AB5_NUMERIC_REPLAY_CONTRACT"
        if ok
        else "HOLD_A7AB4_MATERIALIZATION_OR_ACTIVITY_FAILURE"
    )

    manifest = {
        "stage": "A7AB-4",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_materialization_preflight": True,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may": False,
        "selected_candidates": selected_count,
        "evaluated_candidates": int(len(summary)),
        "activity_ok_count": activity_ok_count,
        "activity_ok_rate": activity_ok_rate,
        "eval_failure_count": eval_failure_count,
        "activity_failure_count": activity_failure_count,
        "missing_field_count": int(len(missing)),
        "missing_fields": missing,
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "full_timestamps_before_materialization_subset": int(full_timestamp_count),
        "timestamp_cap": int(TIMESTAMP_CAP),
        "numeric_field_count": int(len(numeric)),
        "family_count": int(summary["family_id"].nunique()) if not summary.empty else 0,
        "seed_field_count": int(summary["primary_seed_field"].nunique()) if not summary.empty else 0,
        "skeleton_count": int(summary["skeleton_key"].nunique()) if not summary.empty else 0,
        "authorizes_a7ab5_numeric_replay_contract": bool(ok),
        "authorizes_numeric_replay_execution": False,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    summary.to_csv(RUNTIME / "a7ab4_candidate_materialization_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ab4_family_materialization_summary.csv", index=False)
    motif_summary.to_csv(RUNTIME / "a7ab4_motif_materialization_summary.csv", index=False)
    operator_coverage.to_csv(RUNTIME / "a7ab4_operator_coverage.csv", index=False)
    blockers_df.to_csv(RUNTIME / "a7ab4_blocker_matrix.csv", index=False)
    write_json(RUNTIME / "a7ab4_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ab4_authorization_matrix.json",
        {
            "A7AB-4": {"status": decision},
            "A7AB-5_numeric_replay_contract": {"authorized": bool(ok)},
            "numeric_replay_execution": {"authorized": False},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AB-4 MATERIALIZATION PREFLIGHT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AB-4 evaluates static A7AB-3 expressions for materialization, finite coverage, and activity only. It does not compute returns, run replay, execute search, train, or authorize alpha proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Materialization Summary",
        "",
        md_table(family_summary),
        "",
        "## Motif Materialization Summary",
        "",
        md_table(motif_summary, 80),
        "",
        "## Operator Coverage",
        "",
        md_table(operator_coverage),
        "",
        "## Blockers",
        "",
        md_table(blockers_df) if not blockers_df.empty else "No blockers.",
        "",
        "## Candidate Summary Sample",
        "",
        md_table(
            summary[
                [
                    "candidate_id",
                    "family_id",
                    "primary_seed_field",
                    "motif",
                    "eval_success",
                    "finite_share",
                    "nonzero_share",
                    "activity_ok",
                ]
            ],
            max_rows=40,
        ),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
