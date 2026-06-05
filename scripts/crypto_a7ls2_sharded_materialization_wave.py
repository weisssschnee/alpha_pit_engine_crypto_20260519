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

from scripts.crypto_a7ab4_materialization_preflight import A7AB4Evaluator  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import (  # noqa: E402
    BASE_DIR,
    LATENT_PANEL,
    load_base,
    load_latent_numeric,
    parquet_schema,
)
from scripts.crypto_a7ff25r6_dense_funding_state_audit import (  # noqa: E402
    dense_ffill_and_age,
    rolling_mean_std_z,
    shift_matrix as dense_shift_matrix,
)
from scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair import strict_symbols  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ls2_sharded_materialization_wave"
REPORT = REPO / "reports" / "CRYPTO_A7LS2_SHARDED_MATERIALIZATION_WAVE_20260605.md"
LS1 = REPO / "runtime" / "a7ls1_multi_arm_blueprint_generation"
QUEUE = LS1 / "a7ls1_materialization_wave_queue.csv"
LS1_MANIFEST = LS1 / "a7ls1_manifest.json"

FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
OPERATORS = {
    "Mean", "Delta", "TSRank", "Decay", "Rank", "CSRank", "ZScore",
    "Mul", "Sub", "Add", "Neg", "Abs", "Sign", "SafeDiv", "Clip", "Winsor",
}
DENSE_FUNDING_FIELDS = {
    "funding_rate_state_last_ffill_8h",
    "funding_rate_update_age_hours",
    "funding_rate_abs_state_168h_z",
    "funding_rate_delta_state_24h",
    "funding_state_x_basis_delta",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


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


def expression_fields(expression: str) -> set[str]:
    fields: set[str] = set()
    for token in FIELD_RE.findall(str(expression)):
        if token in OPERATORS or token in {"nan", "inf"}:
            continue
        fields.add(token)
    return fields


def requested_fields(queue: pd.DataFrame) -> set[str]:
    out: set[str] = set()
    for expr in queue["expression"].astype(str):
        out.update(expression_fields(expr))
    return out


def select_shards(queue: pd.DataFrame) -> list[str]:
    raw = os.environ.get("A7LS2_SHARDS", "").strip()
    if raw:
        return [token.strip() for token in raw.replace(";", ",").split(",") if token.strip()]
    mode = os.environ.get("A7LS2_TRANCHE", "first_per_arm").strip().lower()
    if mode == "all":
        return sorted(queue["materialization_shard"].dropna().unique().tolist())
    if mode == "first_per_arm":
        shards = []
        for _, group in queue.sort_values("materialization_shard").groupby("a7ls_arm", sort=True):
            shards.append(str(group["materialization_shard"].iloc[0]))
        return shards
    max_shards = int(os.environ.get("A7LS2_MAX_SHARDS", "4"))
    return sorted(queue["materialization_shard"].dropna().unique().tolist())[:max_shards]


def load_numeric(fields: set[str]) -> tuple[list[str], pd.DatetimeIndex, dict[str, np.ndarray], list[str]]:
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    dense = fields & DENSE_FUNDING_FIELDS
    base_fields = {field for field in fields if field in base_schema}
    latent_fields = {field for field in fields if field in latent_schema and field not in base_fields}
    if dense:
        base_fields.add("funding_rate")
        if "funding_state_x_basis_delta" in dense:
            base_fields.add("mark_index_basis_bps")
    missing = sorted(fields - base_fields - latent_fields - dense)
    if missing:
        return [], pd.DatetimeIndex([]), {}, missing
    symbols = strict_symbols()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_fields))
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
    return loaded_symbols, timestamps, numeric, []


def evaluate_shard(shard_name: str, shard: pd.DataFrame) -> dict[str, Any]:
    shard_dir = RUNTIME / "shards" / shard_name
    shard_dir.mkdir(parents=True, exist_ok=True)
    shard.to_csv(shard_dir / "queue.csv", index=False)
    fields = requested_fields(shard)
    loaded_symbols, timestamps, numeric, missing = load_numeric(fields)
    rows: list[dict[str, Any]] = []
    if missing:
        for row in shard.to_dict("records"):
            rows.append(
                {
                    "blueprint_id": row.get("blueprint_id"),
                    "a7ls_arm": row.get("a7ls_arm"),
                    "semantic_pair": row.get("semantic_pair"),
                    "motif": row.get("motif"),
                    "expression": row.get("expression"),
                    "eval_success": False,
                    "finite_share": 0.0,
                    "nonzero_share": 0.0,
                    "activity_ok": False,
                    "min_value": np.nan,
                    "max_value": np.nan,
                    "std_value": np.nan,
                    "error": "missing_fields:" + ";".join(missing),
                }
            )
    else:
        evaluator = A7AB4Evaluator(numeric, {})
        for idx, row in enumerate(shard.to_dict("records"), start=1):
            expr = str(row["expression"])
            try:
                values = evaluator.eval(expr)
                finite = np.isfinite(values)
                finite_share = float(finite.mean()) if values.size else 0.0
                nonzero_share = float((np.abs(values[finite]) > 1e-12).mean()) if finite.any() else 0.0
                eval_success = True
                error = ""
                min_value = float(np.nanmin(values)) if finite.any() else np.nan
                max_value = float(np.nanmax(values)) if finite.any() else np.nan
                std_value = float(np.nanstd(values)) if finite.any() else np.nan
            except Exception as exc:  # noqa: BLE001
                finite_share = 0.0
                nonzero_share = 0.0
                eval_success = False
                error = repr(exc)
                min_value = max_value = std_value = np.nan
            activity_ok = eval_success and finite_share >= 0.20 and nonzero_share >= 0.01
            rows.append(
                {
                    "blueprint_id": row.get("blueprint_id"),
                    "a7ls_arm": row.get("a7ls_arm"),
                    "semantic_pair": row.get("semantic_pair"),
                    "motif": row.get("motif"),
                    "skeleton_key": row.get("skeleton_key"),
                    "production_key": row.get("production_key"),
                    "expression": expr,
                    "eval_success": eval_success,
                    "finite_share": finite_share,
                    "nonzero_share": nonzero_share,
                    "activity_ok": activity_ok,
                    "min_value": min_value,
                    "max_value": max_value,
                    "std_value": std_value,
                    "error": error,
                }
            )
            if idx % 100 == 0:
                print(f"[A7LS-2] {shard_name} evaluated {idx}/{len(shard)}", flush=True)
    result = pd.DataFrame(rows)
    result.to_csv(shard_dir / "materialization_metrics.csv", index=False)
    manifest = {
        "shard": shard_name,
        "generated_at": now_utc(),
        "queue_rows": int(len(shard)),
        "a7ls_arm": str(shard["a7ls_arm"].iloc[0]) if not shard.empty else "",
        "field_count": int(len(fields)),
        "missing_field_count": int(len(missing)),
        "missing_fields": missing,
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps_loaded": int(len(timestamps)),
        "eval_success_count": int(result["eval_success"].sum()) if not result.empty else 0,
        "eval_failure_count": int((~result["eval_success"].astype(bool)).sum()) if not result.empty else int(len(shard)),
        "activity_ok_count": int(result["activity_ok"].sum()) if not result.empty else 0,
        "activity_ok_rate": float(result["activity_ok"].mean()) if not result.empty else 0.0,
    }
    write_json(shard_dir / "manifest.json", manifest)
    return manifest


def summarize(shard_manifests: list[dict[str, Any]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    checkpoint = pd.DataFrame(shard_manifests)
    all_metrics = []
    for shard_name in checkpoint["shard"].astype(str).tolist() if not checkpoint.empty else []:
        path = RUNTIME / "shards" / shard_name / "materialization_metrics.csv"
        frame = read_csv(path)
        if not frame.empty:
            frame["materialization_shard"] = shard_name
            all_metrics.append(frame)
    metrics = pd.concat(all_metrics, ignore_index=True) if all_metrics else pd.DataFrame()
    metrics.to_csv(RUNTIME / "a7ls2_materialization_metrics_executed.csv", index=False)
    if metrics.empty:
        summary = pd.DataFrame()
    else:
        summary = metrics.groupby(["a7ls_arm", "semantic_pair"], dropna=False).agg(
            rows=("blueprint_id", "size"),
            eval_success=("eval_success", "sum"),
            activity_ok=("activity_ok", "sum"),
            median_finite_share=("finite_share", "median"),
            median_nonzero_share=("nonzero_share", "median"),
            skeleton_count=("skeleton_key", "nunique"),
        ).reset_index()
        summary["activity_ok_rate"] = summary["activity_ok"] / summary["rows"].replace(0, pd.NA)
    summary.to_csv(RUNTIME / "a7ls2_materialization_summary_by_semantic.csv", index=False)
    checkpoint.to_csv(RUNTIME / "a7ls2_checkpoint_status.csv", index=False)
    return checkpoint, summary


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    ls1 = read_json(LS1_MANIFEST)
    if not ls1.get("authorizes_a7ls2_materialization_wave"):
        raise SystemExit(f"A7LS-1 does not authorize A7LS-2: {ls1.get('decision')}")
    queue = pd.read_csv(QUEUE)
    shards = select_shards(queue)
    manifests = []
    for shard_name in shards:
        shard = queue[queue["materialization_shard"].eq(shard_name)].copy()
        if shard.empty:
            continue
        print(f"[A7LS-2] running {shard_name} rows={len(shard)} arm={shard['a7ls_arm'].iloc[0]}", flush=True)
        manifests.append(evaluate_shard(shard_name, shard))
    checkpoint, summary = summarize(manifests)
    total_rows = int(checkpoint["queue_rows"].sum()) if not checkpoint.empty else 0
    eval_fail = int(checkpoint["eval_failure_count"].sum()) if not checkpoint.empty else 0
    activity_ok = int(checkpoint["activity_ok_count"].sum()) if not checkpoint.empty else 0
    activity_rate = float(activity_ok / total_rows) if total_rows else 0.0
    executed_arms = int(checkpoint["a7ls_arm"].nunique()) if not checkpoint.empty else 0
    blockers: list[str] = []
    if executed_arms < 4 and os.environ.get("A7LS2_TRANCHE", "first_per_arm").lower() == "first_per_arm":
        blockers.append("not_all_arms_executed")
    if eval_fail:
        blockers.append("eval_failures_present")
    if activity_rate < 0.50:
        blockers.append("activity_ok_rate_lt_0_50")
    decision = "PASS_A7LS2_FIRST_CHECKPOINT_MATERIALIZATION_READY" if not blockers else "HOLD_A7LS2_MATERIALIZATION_CHECKPOINT_WEAK"
    manifest = {
        "stage": "A7LS-2",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7LS-1",
        "source_decision": ls1.get("decision"),
        "executed_shard_count": int(len(checkpoint)),
        "executed_arm_count": executed_arms,
        "executed_rows": total_rows,
        "eval_failure_count": eval_fail,
        "activity_ok_count": activity_ok,
        "activity_ok_rate": activity_rate,
        "executes_materialization": True,
        "executes_numeric_probe": False,
        "executes_search": False,
        "authorizes_a7ls2_continue_materialization": activity_rate >= 0.50 and eval_fail == 0,
        "authorizes_a7ls3_numeric_wave": decision.startswith("PASS_"),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls2_manifest.json", manifest)
    REPORT.write_text("\n".join([
        "# CRYPTO A7LS-2 SHARDED MATERIALIZATION WAVE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7LS-2 executes the materialization wave in memory-safe shards. This run defaults to first checkpoint tranche: one 500-row shard per arm.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Checkpoint Status",
        "",
        md_table(checkpoint, 40),
        "",
        "## Semantic Summary",
        "",
        md_table(summary, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "materialization executed: true",
        "numeric probe executed: false",
        "search/proof/shadow/live: false",
        "```",
    ]), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
