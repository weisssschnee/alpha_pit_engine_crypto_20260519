from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.dataset as ds


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ffcore6e_materialization_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE6E_MATERIALIZATION_PREFLIGHT_EXECUTION_20260601.md"
A7FFCORE6 = REPO / "runtime" / "a7ffcore6_materialization_preflight_contract" / "a7ffcore6_manifest.json"
CONTRACT = REPO / "runtime" / "a7ffcore6_materialization_preflight_contract" / "a7ffcore6e_execution_contract.json"
QUEUE = REPO / "runtime" / "a7ffcore5_gate_native_generation_dryrun" / "a7ffcore5_gate_native_candidate_queue.csv"
SHARD_PLAN = REPO / "runtime" / "a7ffcore6_materialization_preflight_contract" / "a7ffcore6_shard_plan.csv"
BASE_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527")
LATENT_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_latent_state_features_v1_20260527.parquet")


class CachedCryptoFeatureAlgebra(CryptoFeatureAlgebra):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._cache: dict[str, pd.Series] = {}

    def _eval(self, expression: str) -> pd.Series:
        key = expression.strip()
        if key in self._cache:
            return self._cache[key]
        values = super()._eval(key)
        self._cache[key] = values
        return values


def now_utc() -> str:
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
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def split_fields(series: pd.Series) -> set[str]:
    fields: set[str] = set()
    for value in series.fillna("").astype(str):
        fields.update(part for part in value.split(";") if part)
    return fields


def load_panel(required_fields: set[str]) -> tuple[pd.DataFrame, list[str], list[str]]:
    base_schema = ds.dataset(str(BASE_PANEL), format="parquet").schema.names
    latent_schema = pd.read_parquet(LATENT_PANEL, columns=["symbol", "timestamp"]).columns.tolist()
    # Use pyarrow schema for latent without reading all columns twice.
    latent_schema = ds.dataset(str(LATENT_PANEL), format="parquet").schema.names

    key_cols = ["symbol", "timestamp"]
    base_fields = sorted((required_fields & set(base_schema)) - set(key_cols))
    latent_fields = sorted((required_fields & set(latent_schema)) - set(key_cols) - set(base_fields))
    missing_fields = sorted(required_fields - set(base_fields) - set(latent_fields) - set(key_cols))

    base = ds.dataset(str(BASE_PANEL), format="parquet").to_table(columns=key_cols + base_fields).to_pandas()
    base["timestamp"] = pd.to_datetime(base["timestamp"], utc=True).dt.tz_localize(None)
    if latent_fields:
        latent = pd.read_parquet(LATENT_PANEL, columns=key_cols + latent_fields)
        latent["timestamp"] = pd.to_datetime(latent["timestamp"], utc=True).dt.tz_localize(None)
        panel = base.merge(latent, on=key_cols, how="left", validate="one_to_one")
    else:
        panel = base
    return panel.sort_values(["symbol", "timestamp"]).reset_index(drop=True), missing_fields, base_fields + latent_fields


def evaluate_shard(shard: pd.DataFrame, panel: pd.DataFrame, allowed_fields: set[str]) -> pd.DataFrame:
    evaluator = CachedCryptoFeatureAlgebra(panel, allowed_fields=allowed_fields)
    rows: list[dict[str, Any]] = []
    forbidden_tokens = ("forward_", "label", "May", "may_", "stress_pass", "pass_fail")
    for row in shard.to_dict("records"):
        expr = str(row["expression"])
        raw_inputs = [x for x in str(row["raw_inputs"]).split(";") if x]
        missing = sorted(set(raw_inputs) - set(panel.columns))
        token_violation = any(token in expr for token in forbidden_tokens)
        status = "ok"
        error = ""
        diagnostics: dict[str, Any] = {
            "rows": len(panel),
            "non_null_rows": 0,
            "finite_rows": 0,
            "nan_rows": len(panel),
            "inf_rows": 0,
            "active_rows": 0,
            "non_null_ratio": 0.0,
            "active_ratio": 0.0,
            "std": math.nan,
        }
        if missing:
            status = "missing_field"
            error = ";".join(missing)
        elif token_violation:
            status = "label_or_may_token"
            error = "forbidden_token"
        else:
            try:
                result = evaluator.evaluate(expr)
                diagnostics = result.diagnostics
                if int(diagnostics.get("inf_rows", 0)) > 0:
                    status = "inf_present"
            except Exception as exc:
                status = "eval_error"
                error = str(exc)
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "root_subgraph_id": row["root_subgraph_id"],
                "expression": expr,
                "semantic_bucket": row["semantic_bucket"],
                "motif_bucket": row["motif_bucket"],
                "raw_inputs": row["raw_inputs"],
                "status": status,
                "error": error,
                "missing_field_count": len(missing),
                "label_or_may_token": token_violation,
                **diagnostics,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core6 = read_json(A7FFCORE6)
    if core6.get("decision") != "PASS_A7FFCORE6_MATERIALIZATION_PREFLIGHT_CONTRACT_READY_FOR_CORE6E":
        raise SystemExit(f"A7FF-CORE6 is not ready: {core6.get('decision')}")
    contract = read_json(CONTRACT)
    queue = pd.read_csv(QUEUE)
    shard_plan = pd.read_csv(SHARD_PLAN)
    required_fields = split_fields(queue["raw_inputs"])
    panel, missing_panel_fields, loaded_fields = load_panel(required_fields)

    shard_manifests: list[dict[str, Any]] = []
    all_results: list[pd.DataFrame] = []
    for shard in shard_plan.to_dict("records"):
        shard_id = str(shard["shard_id"])
        start = int(shard["start_index"])
        end = int(shard["end_index_exclusive"])
        out_path = RUNTIME / f"a7ffcore6e_{shard_id}_materialization.csv"
        manifest_path = RUNTIME / f"a7ffcore6e_{shard_id}_manifest.json"
        if out_path.exists() and manifest_path.exists():
            result = pd.read_csv(out_path)
            shard_manifests.append(read_json(manifest_path))
            all_results.append(result)
            continue
        shard_queue = queue.iloc[start:end].copy()
        result = evaluate_shard(shard_queue, panel, set(loaded_fields))
        result.to_csv(out_path, index=False)
        manifest = {
            "shard_id": shard_id,
            "candidate_count": int(len(result)),
            "ok_count": int(result["status"].eq("ok").sum()),
            "eval_error_count": int(result["status"].eq("eval_error").sum()),
            "missing_field_count": int(result["status"].eq("missing_field").sum()),
            "label_or_may_token_count": int(result["label_or_may_token"].sum()),
            "mean_non_null_ratio": float(result["non_null_ratio"].mean()) if not result.empty else 0.0,
            "mean_active_ratio": float(result["active_ratio"].mean()) if not result.empty else 0.0,
            "output": str(out_path.relative_to(REPO)),
        }
        write_json(manifest_path, manifest)
        shard_manifests.append(manifest)
        all_results.append(result)

    combined = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()
    combined.to_csv(RUNTIME / "a7ffcore6e_materialization_summary_rows.csv", index=False)
    shard_summary = pd.DataFrame(shard_manifests)
    shard_summary.to_csv(RUNTIME / "a7ffcore6e_shard_summary.csv", index=False)

    status_summary = (
        combined.groupby("status", dropna=False)
        .agg(
            candidates=("candidate_id", "count"),
            mean_non_null_ratio=("non_null_ratio", "mean"),
            mean_active_ratio=("active_ratio", "mean"),
        )
        .reset_index()
        .sort_values("candidates", ascending=False)
    )
    status_summary.to_csv(RUNTIME / "a7ffcore6e_status_summary.csv", index=False)

    family_summary = (
        combined.groupby(["semantic_bucket", "motif_bucket", "status"], dropna=False)
        .agg(
            candidates=("candidate_id", "count"),
            mean_non_null_ratio=("non_null_ratio", "mean"),
            mean_active_ratio=("active_ratio", "mean"),
        )
        .reset_index()
        .sort_values("candidates", ascending=False)
    )
    family_summary.to_csv(RUNTIME / "a7ffcore6e_family_status_summary.csv", index=False)

    field_summary = pd.DataFrame(
        [
            {"field": field, "present": field in panel.columns, "source": "loaded" if field in loaded_fields else "missing"}
            for field in sorted(required_fields)
        ]
    )
    field_summary.to_csv(RUNTIME / "a7ffcore6e_field_presence_summary.csv", index=False)

    eval_errors = int(combined["status"].eq("eval_error").sum()) if not combined.empty else 0
    missing_rows = int(combined["status"].eq("missing_field").sum()) if not combined.empty else 0
    label_or_may = int(combined["label_or_may_token"].sum()) if not combined.empty else 0
    total = int(len(combined))
    eval_failure_rate = eval_errors / total if total else 1.0
    missing_field_rate = missing_rows / total if total else 1.0
    pass_conditions = contract.get("pass_conditions", {})
    blockers: list[str] = []
    if missing_panel_fields:
        blockers.append("required_panel_fields_missing")
    if eval_failure_rate > float(pass_conditions.get("eval_failure_rate_max", 0.02)):
        blockers.append("eval_failure_rate_above_limit")
    if missing_field_rate > float(pass_conditions.get("missing_field_rate_max", 0.01)):
        blockers.append("missing_field_rate_above_limit")
    if label_or_may:
        blockers.append("label_or_may_token_present")

    decision = "PASS_A7FFCORE6E_MATERIALIZATION_PREFLIGHT_READY_FOR_CORE7" if not blockers else "HOLD_A7FFCORE6E_MATERIALIZATION_PREFLIGHT_FAIL"
    manifest = {
        "stage": "A7FF-CORE6E",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7FF-CORE6",
        "source_decision": core6.get("decision"),
        "panel_path": str(BASE_PANEL),
        "latent_panel_path": str(LATENT_PANEL),
        "panel_rows": int(len(panel)),
        "panel_symbols": int(panel["symbol"].nunique()),
        "queue_rows": total,
        "shard_count": int(len(shard_summary)),
        "ok_count": int(combined["status"].eq("ok").sum()) if total else 0,
        "eval_error_count": eval_errors,
        "missing_field_candidate_count": missing_rows,
        "missing_panel_fields": missing_panel_fields,
        "label_or_may_token_count": label_or_may,
        "eval_failure_rate": eval_failure_rate,
        "missing_field_rate": missing_field_rate,
        "mean_non_null_ratio": float(combined["non_null_ratio"].mean()) if total else 0.0,
        "mean_active_ratio": float(combined["active_ratio"].mean()) if total else 0.0,
        "executes_materialization": True,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core7": not bool(blockers),
        "authorizes_numeric": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE7 gate-native numeric-response contract" if not blockers else "A7FF-CORE6E materialization repair",
    }
    write_json(RUNTIME / "a7ffcore6e_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-CORE6E MATERIALIZATION PREFLIGHT EXECUTION

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-CORE6E materializes the CORE5 gate-native queue for finite/activity diagnostics only. It does not compute labels, returns, IC, spread, PnL, replay metrics, selector scores, search, or promotion.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Status Summary

{md_table(status_summary, 40)}

## Shard Summary

{md_table(shard_summary, 40)}

## Field Presence

{md_table(field_summary, 80)}

## Family Status Summary

{md_table(family_summary, 80)}

## Boundary

```text
materialization executed: true
numeric response: false
labels/returns/IC/spread/PnL: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
