from __future__ import annotations

import json
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


RUNTIME = REPO / "runtime" / "a7ffcore12e_materialization_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE12E_MATERIALIZATION_PREFLIGHT_20260601.md"
A7FFCORE12 = REPO / "runtime" / "a7ffcore12_blueprint_registration_audit" / "a7ffcore12_manifest.json"
APPROVED = REPO / "runtime" / "a7ffcore12_blueprint_registration_audit" / "a7ffcore12_approved_temp_subgraphs.csv"
BASE_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527")
LATENT_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_latent_state_features_v1_20260527.parquet")

PREFLIGHT_COUNT = 512
MAX_PER_SEMANTIC = 80
MAX_PER_MOTIF = 96


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
    return view.to_markdown(index=False)


def split_fields(series: pd.Series) -> set[str]:
    fields: set[str] = set()
    for value in series.fillna("").astype(str):
        fields.update(part for part in value.split(";") if part)
    return fields


def build_queue(df: pd.DataFrame) -> pd.DataFrame:
    ordered = df.sort_values(["semantic_bucket", "motif_bucket", "generation_mode", "candidate_id"]).copy()
    selected: list[dict[str, Any]] = []
    semantic_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    for row in ordered.to_dict("records"):
        semantic = str(row["semantic_bucket"])
        motif = str(row["motif_bucket"])
        if semantic_counts.get(semantic, 0) >= MAX_PER_SEMANTIC:
            continue
        if motif_counts.get(motif, 0) >= MAX_PER_MOTIF:
            continue
        row["preflight_rank"] = len(selected) + 1
        selected.append(row)
        semantic_counts[semantic] = semantic_counts.get(semantic, 0) + 1
        motif_counts[motif] = motif_counts.get(motif, 0) + 1
        if len(selected) >= PREFLIGHT_COUNT:
            break
    return pd.DataFrame(selected)


def load_panel(required_fields: set[str]) -> pd.DataFrame:
    base_schema = set(ds.dataset(str(BASE_PANEL), format="parquet").schema.names)
    latent_schema = set(ds.dataset(str(LATENT_PANEL), format="parquet").schema.names)
    key_cols = ["symbol", "timestamp"]
    base_cols = key_cols + sorted((required_fields & base_schema) - set(key_cols))
    latent_cols = key_cols + sorted((required_fields & latent_schema) - set(key_cols) - set(base_cols))
    base = ds.dataset(str(BASE_PANEL), format="parquet").to_table(columns=base_cols).to_pandas()
    base["timestamp"] = pd.to_datetime(base["timestamp"], utc=True).dt.tz_localize(None)
    if latent_cols == key_cols:
        panel = base
    else:
        latent = pd.read_parquet(LATENT_PANEL, columns=latent_cols)
        latent["timestamp"] = pd.to_datetime(latent["timestamp"], utc=True).dt.tz_localize(None)
        panel = base.merge(latent, on=key_cols, how="left", validate="one_to_one")
    return panel.sort_values(["symbol", "timestamp"]).reset_index(drop=True)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core12 = read_json(A7FFCORE12)
    if core12.get("decision") != "PASS_A7FFCORE12_TEMP_SUBGRAPH_REGISTRY_READY_FOR_CORE12E":
        raise SystemExit(f"A7FF-CORE12 is not ready: {core12.get('decision')}")
    approved = pd.read_csv(APPROVED)
    queue = build_queue(approved)
    required_fields = split_fields(queue["raw_inputs"])
    panel = load_panel(required_fields)
    evaluator = CachedCryptoFeatureAlgebra(panel, allowed_fields=required_fields)
    rows: list[dict[str, Any]] = []
    for cand in queue.to_dict("records"):
        try:
            series = evaluator.evaluate(str(cand["canonical_expression"])).values
            values = pd.to_numeric(series, errors="coerce")
            finite = np.isfinite(values.to_numpy(dtype=float, na_value=np.nan))
            non_null = int(values.notna().sum())
            active = int(values.diff().abs().fillna(0).gt(1e-12).sum())
            rows.append(
                {
                    "candidate_id": cand["candidate_id"],
                    "proposed_subgraph_id": cand["proposed_subgraph_id"],
                    "semantic_bucket": cand["semantic_bucket"],
                    "motif_bucket": cand["motif_bucket"],
                    "generation_mode": cand["generation_mode"],
                    "expression": cand["canonical_expression"],
                    "raw_inputs": cand["raw_inputs"],
                    "status": "ok",
                    "error": "",
                    "rows": int(len(values)),
                    "non_null_rows": non_null,
                    "finite_rows": int(finite.sum()),
                    "active_rows": active,
                    "non_null_ratio": non_null / max(1, len(values)),
                    "active_ratio": active / max(1, len(values)),
                    "std": float(values.std(skipna=True)) if non_null else float("nan"),
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "candidate_id": cand["candidate_id"],
                    "proposed_subgraph_id": cand["proposed_subgraph_id"],
                    "semantic_bucket": cand["semantic_bucket"],
                    "motif_bucket": cand["motif_bucket"],
                    "generation_mode": cand["generation_mode"],
                    "expression": cand["canonical_expression"],
                    "raw_inputs": cand["raw_inputs"],
                    "status": "eval_error",
                    "error": str(exc),
                    "rows": 0,
                    "non_null_rows": 0,
                    "finite_rows": 0,
                    "active_rows": 0,
                    "non_null_ratio": 0.0,
                    "active_ratio": 0.0,
                    "std": float("nan"),
                }
            )
    result = pd.DataFrame(rows)
    summary = (
        result.groupby(["semantic_bucket", "motif_bucket", "generation_mode"], dropna=False)
        .agg(
            candidate_count=("candidate_id", "nunique"),
            ok_count=("status", lambda s: int(s.eq("ok").sum())),
            eval_error_count=("status", lambda s: int(s.eq("eval_error").sum())),
            median_non_null_ratio=("non_null_ratio", "median"),
            median_active_ratio=("active_ratio", "median"),
        )
        .reset_index()
        .sort_values(["eval_error_count", "candidate_count"], ascending=[False, False])
    )
    result.to_csv(RUNTIME / "a7ffcore12e_materialization_rows.csv", index=False)
    queue.to_csv(RUNTIME / "a7ffcore12e_materialization_queue.csv", index=False)
    summary.to_csv(RUNTIME / "a7ffcore12e_materialization_summary.csv", index=False)
    error_summary = result[result["status"].eq("eval_error")].groupby("error", dropna=False).agg(count=("candidate_id", "size")).reset_index().sort_values("count", ascending=False)
    error_summary.to_csv(RUNTIME / "a7ffcore12e_error_summary.csv", index=False)
    eval_errors = int(result["status"].eq("eval_error").sum())
    ok_count = int(result["status"].eq("ok").sum())
    low_activity = int(result[result["status"].eq("ok")]["active_ratio"].lt(0.01).sum())
    decision = (
        "PASS_A7FFCORE12E_MATERIALIZATION_PREFLIGHT_READY_FOR_CORE13"
        if eval_errors == 0 and ok_count >= 384 and low_activity == 0
        else "HOLD_A7FFCORE12E_MATERIALIZATION_PREFLIGHT_REPAIR_REQUIRED"
    )
    blockers = []
    if eval_errors:
        blockers.append("eval_errors_present")
    if ok_count < 384:
        blockers.append("ok_count_below_384")
    if low_activity:
        blockers.append("low_activity_candidates_present")
    manifest = {
        "stage": "A7FF-CORE12E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE12",
        "source_decision": core12.get("decision"),
        "decision": decision,
        "queue_count": int(len(queue)),
        "ok_count": ok_count,
        "eval_error_count": eval_errors,
        "low_activity_count": low_activity,
        "blockers": blockers,
        "executes_materialization": True,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core13": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE13 numeric response contract" if decision.startswith("PASS_") else "A7FF-CORE12R evaluator/operator repair",
    }
    write_json(RUNTIME / "a7ffcore12e_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE12E MATERIALIZATION PREFLIGHT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE12E materializes a 512-row temp-subgraph sample. It does not run numeric response, replay, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Materialization Summary",
        "",
        md_table(summary),
        "",
        "## Error Summary",
        "",
        md_table(error_summary),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
