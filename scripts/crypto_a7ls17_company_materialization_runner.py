from __future__ import annotations

import json
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

import scripts.crypto_a7ls16_local_preflight as a7ls16  # noqa: E402


DEFAULT_QUEUE = Path(
    os.environ.get(
        "A7LS17_QUEUE_PATH",
        "G:/AlphaFactory_CryptoData/research_runtime/a7ls15_million_scale_blueprint_generation_20260606/a7ls15_materialization_queue_100k.csv",
    )
)
DEFAULT_RUNTIME = Path(
    os.environ.get(
        "A7LS17_RUNTIME",
        "G:/AlphaFactory_CryptoData/research_runtime/a7ls17_company_materialization_20260606",
    )
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    return int(raw)


def read_queue_slice(queue_path: Path, start_row: int, end_row: int) -> pd.DataFrame:
    if not queue_path.exists():
        raise FileNotFoundError(f"missing queue: {queue_path}")
    if start_row < 0 or end_row <= start_row:
        raise ValueError(f"invalid row range: {start_row}:{end_row}")
    queue = pd.read_csv(queue_path, low_memory=False)
    return queue.iloc[start_row:end_row].copy()


def evaluate(queue: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str], list[str], int, int]:
    fields = a7ls16.requested_fields(queue)
    operators = sorted({op for expr in queue["expression"].astype(str) for op in a7ls16.expression_operators(expr)})
    unsupported = [op for op in operators if op not in a7ls16.OPERATORS]
    if unsupported:
        rows = []
        for row in queue.to_dict("records"):
            rows.append(
                {
                    "blueprint_id": row.get("blueprint_id"),
                    "a7ls_lane": row.get("a7ls_lane"),
                    "semantic_pair": row.get("semantic_pair"),
                    "motif": row.get("motif"),
                    "expression": row.get("expression"),
                    "eval_success": False,
                    "finite_share": 0.0,
                    "nonzero_share": 0.0,
                    "std_value": np.nan,
                    "activity_ok": False,
                    "error": "unsupported_operators:" + ";".join(unsupported),
                }
            )
        return pd.DataFrame(rows), {}, unsupported, len(fields), len(operators)

    numeric, field_status, symbols, timestamps = a7ls16.load_numeric(fields)
    missing = sorted(field for field in fields if str(field_status.get(field, "")).startswith("missing"))
    if missing:
        rows = []
        for row in queue.to_dict("records"):
            rows.append(
                {
                    "blueprint_id": row.get("blueprint_id"),
                    "a7ls_lane": row.get("a7ls_lane"),
                    "semantic_pair": row.get("semantic_pair"),
                    "motif": row.get("motif"),
                    "expression": row.get("expression"),
                    "eval_success": False,
                    "finite_share": 0.0,
                    "nonzero_share": 0.0,
                    "std_value": np.nan,
                    "activity_ok": False,
                    "error": "missing_fields:" + ";".join(missing),
                }
            )
        return pd.DataFrame(rows), field_status, missing, len(fields), len(operators)

    evaluator = a7ls16.A7LS16Evaluator(numeric, {})
    rows: list[dict[str, Any]] = []
    progress_every = env_int("A7LS17_PROGRESS_EVERY", 100)
    total = len(queue)
    for idx, row in enumerate(queue.to_dict("records"), start=1):
        expr = str(row["expression"])
        try:
            values = evaluator.eval(expr)
            finite = np.isfinite(values)
            finite_share = float(finite.mean()) if values.size else 0.0
            nonzero_share = float((np.abs(values[finite]) > 1e-12).mean()) if finite.any() else 0.0
            std_value = float(np.nanstd(values)) if finite.any() else np.nan
            min_value = float(np.nanmin(values)) if finite.any() else np.nan
            max_value = float(np.nanmax(values)) if finite.any() else np.nan
            eval_success = True
            error = ""
        except Exception as exc:  # noqa: BLE001
            finite_share = 0.0
            nonzero_share = 0.0
            std_value = np.nan
            min_value = np.nan
            max_value = np.nan
            eval_success = False
            error = repr(exc)
        activity_ok = bool(eval_success and finite_share >= a7ls16.MIN_FINITE_SHARE and nonzero_share >= a7ls16.MIN_NONZERO_SHARE and (not np.isfinite(std_value) or std_value > 1e-12))
        rows.append(
            {
                "blueprint_id": row.get("blueprint_id"),
                "a7ls_lane": row.get("a7ls_lane"),
                "lane_name": row.get("lane_name"),
                "search_role": row.get("search_role"),
                "level": row.get("level"),
                "candidate_role": row.get("candidate_role"),
                "semantic_pair": row.get("semantic_pair"),
                "motif": row.get("motif"),
                "primary_field": row.get("primary_field"),
                "secondary_field": row.get("secondary_field"),
                "skeleton_key": row.get("skeleton_key"),
                "production_key": row.get("production_key"),
                "expression": expr,
                "eval_success": eval_success,
                "finite_share": finite_share,
                "nonzero_share": nonzero_share,
                "std_value": std_value,
                "min_value": min_value,
                "max_value": max_value,
                "activity_ok": activity_ok,
                "error": error,
            }
        )
        if progress_every > 0 and idx % progress_every == 0:
            print(f"[A7LS17] evaluated {idx}/{total}", flush=True)
    return pd.DataFrame(rows), field_status, [], len(fields), len(operators)


def summarize(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return pd.DataFrame()
    return (
        metrics.groupby(["a7ls_lane", "semantic_pair", "motif"], dropna=False)
        .agg(
            rows=("blueprint_id", "size"),
            eval_success=("eval_success", "sum"),
            activity_ok=("activity_ok", "sum"),
            finite_share_median=("finite_share", "median"),
            nonzero_share_median=("nonzero_share", "median"),
        )
        .reset_index()
        .sort_values(["activity_ok", "eval_success", "rows"], ascending=False)
    )


def main() -> dict[str, Any]:
    started = time.time()
    queue_path = Path(os.environ.get("A7LS17_QUEUE_PATH", str(DEFAULT_QUEUE)))
    runtime = Path(os.environ.get("A7LS17_RUNTIME", str(DEFAULT_RUNTIME)))
    shard_id = os.environ.get("A7LS17_SHARD_ID", "a7ls17_s000").strip()
    start_row = env_int("A7LS17_START_ROW", 0)
    end_row = env_int("A7LS17_END_ROW", start_row + env_int("A7LS17_ROWS", 1000))
    symbol_cap = env_int("A7LS17_SYMBOL_CAP", 128)
    timestamp_cap = env_int("A7LS17_TIMESTAMP_CAP", 2048)

    a7ls16.SYMBOL_CAP = symbol_cap
    a7ls16.TIMESTAMP_CAP = timestamp_cap

    shard_dir = runtime / "shards" / shard_id
    shard_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = shard_dir / "a7ls17_manifest.json"
    if manifest_path.exists() and os.environ.get("A7LS17_OVERWRITE", "0").strip() not in {"1", "true", "yes"}:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        print(json.dumps({"status": "skip_existing_manifest", **manifest}, indent=2, sort_keys=True))
        return manifest

    queue = read_queue_slice(queue_path, start_row, end_row)
    queue.to_csv(shard_dir / "a7ls17_queue_slice.csv", index=False)
    metrics, field_status, blockers, field_count, operator_count = evaluate(queue)
    metrics.to_csv(shard_dir / "a7ls17_materialization_metrics.csv", index=False)
    summarize(metrics).to_csv(shard_dir / "a7ls17_family_activity_summary.csv", index=False)
    pd.DataFrame(
        [{"field": field, "status": status} for field, status in sorted(field_status.items())]
    ).to_csv(shard_dir / "a7ls17_field_status.csv", index=False)

    eval_success_count = int(metrics["eval_success"].sum()) if not metrics.empty else 0
    activity_ok_count = int(metrics["activity_ok"].sum()) if not metrics.empty else 0
    manifest = {
        "stage": "A7LS-17",
        "decision": "PASS_A7LS17_SHARD_MATERIALIZATION_COMPLETE" if not blockers else "HOLD_A7LS17_SHARD_BLOCKED",
        "generated_at": now_iso(),
        "shard_id": shard_id,
        "queue_path": str(queue_path),
        "runtime": str(runtime),
        "start_row": start_row,
        "end_row": end_row,
        "queue_rows": int(len(queue)),
        "field_count": int(field_count),
        "operator_count": int(operator_count),
        "symbol_cap": int(symbol_cap),
        "timestamp_cap": int(timestamp_cap),
        "eval_success_count": eval_success_count,
        "eval_failure_count": int(len(metrics) - eval_success_count),
        "activity_ok_count": activity_ok_count,
        "activity_ok_rate": float(activity_ok_count / len(metrics)) if len(metrics) else 0.0,
        "lane_count": int(queue["a7ls_lane"].nunique()) if "a7ls_lane" in queue else 0,
        "semantic_pair_count": int(queue["semantic_pair"].nunique()) if "semantic_pair" in queue else 0,
        "blockers": blockers,
        "elapsed_seconds": round(time.time() - started, 3),
        "uses_may": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(manifest_path, manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


if __name__ == "__main__":
    main()
