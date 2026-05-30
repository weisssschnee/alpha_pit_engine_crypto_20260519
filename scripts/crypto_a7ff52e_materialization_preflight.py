from __future__ import annotations

import json
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
    load_group_fields,
    load_latent_numeric,
    parquet_schema,
)
from scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair import strict_symbols  # noqa: E402
from scripts.crypto_a7al2z4_broader_non_oi_numeric_replay_preflight import smoke_column_indices  # noqa: E402
from scripts.crypto_a7ff25r6_dense_funding_state_audit import (  # noqa: E402
    dense_ffill_and_age,
    rolling_mean_std_z,
    shift_matrix as dense_shift_matrix,
)
from scripts.crypto_a7ff8_expanded_numeric_probe import DENSE_FUNDING_FIELDS, expression_fields, md_table  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ff52e_materialization_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7FF52E_MATERIALIZATION_PREFLIGHT_20260531.md"
A7FF52_MANIFEST = REPO / "runtime" / "a7ff52_materialization_preflight_contract" / "a7ff52_manifest.json"
A7FF51E_QUEUE = REPO / "runtime" / "a7ff51e_non_l5_heavy_generation" / "a7ff51e_blueprint_queue.csv"

MIN_FINITE_SHARE = 0.20
MIN_NONZERO_SHARE = 0.01


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def balanced_sample(queue: pd.DataFrame, target_rows: int = 1200, min_per_family: int = 100) -> pd.DataFrame:
    pieces: list[pd.DataFrame] = []
    families = sorted(queue["semantic_pair"].dropna().unique().tolist())
    per_family = max(min_per_family, target_rows // max(1, len(families)))
    for family in families:
        group = queue[queue["semantic_pair"].eq(family)].copy()
        motifs = sorted(group["motif"].dropna().unique().tolist())
        motif_parts = []
        per_motif = max(1, per_family // max(1, len(motifs)))
        for motif in motifs:
            motif_parts.append(group[group["motif"].eq(motif)].head(per_motif))
        part = pd.concat(motif_parts, ignore_index=True) if motif_parts else group.head(0)
        if len(part) < per_family:
            extra = group[~group["blueprint_id"].isin(set(part["blueprint_id"]))].head(per_family - len(part))
            part = pd.concat([part, extra], ignore_index=True)
        pieces.append(part.head(per_family))
    out = pd.concat(pieces, ignore_index=True).drop_duplicates("blueprint_id") if pieces else queue.head(0)
    if len(out) < target_rows:
        extra = queue[~queue["blueprint_id"].isin(set(out["blueprint_id"]))].head(target_rows - len(out))
        out = pd.concat([out, extra], ignore_index=True)
    return out.head(target_rows).copy()


def requested_fields(queue: pd.DataFrame) -> tuple[set[str], set[str], set[str], set[str]]:
    fields = set()
    for expr in queue["expression"].astype(str):
        fields.update(expression_fields(expr))
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    dense = fields & DENSE_FUNDING_FIELDS
    base_fields = {field for field in fields if field in base_schema}
    if dense:
        base_fields.add("funding_rate")
        if "funding_state_x_basis_delta" in dense:
            base_fields.add("mark_index_basis_bps")
    latent_fields = {field for field in fields if field in latent_schema and field not in base_fields}
    missing = fields - base_fields - latent_fields - dense
    return base_fields, latent_fields, dense, missing


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    contract = read_json(A7FF52_MANIFEST)
    if contract.get("decision") != "PASS_A7FF52_MATERIALIZATION_PREFLIGHT_CONTRACT_READY_NO_EXECUTION_AUTH":
        raise SystemExit(f"A7FF-52 contract not ready: {contract.get('decision')}")

    queue = pd.read_csv(A7FF51E_QUEUE)
    sample = balanced_sample(queue, 1200, 100)
    base_fields, latent_fields, dense_fields, missing = requested_fields(sample)

    material_rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    if missing:
        blockers.append("missing_fields")
    else:
        symbols = strict_symbols()
        loaded_symbols, timestamps, numeric = load_base(symbols, base_fields)
        numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_fields))
        if dense_fields:
            raw_funding = numeric["funding_rate"]
            dense_funding, funding_age = dense_ffill_and_age(raw_funding, 8)
            numeric["funding_rate_state_last_ffill_8h"] = dense_funding
            numeric["funding_rate_update_age_hours"] = funding_age
            if "funding_rate_abs_state_168h_z" in dense_fields:
                numeric["funding_rate_abs_state_168h_z"] = rolling_mean_std_z(np.abs(dense_funding), 168, 48)
            if "funding_rate_delta_state_24h" in dense_fields or "funding_state_x_basis_delta" in dense_fields:
                funding_delta_24h = dense_funding - dense_shift_matrix(dense_funding, 24)
                numeric["funding_rate_delta_state_24h"] = funding_delta_24h
            if "funding_state_x_basis_delta" in dense_fields:
                basis = numeric["mark_index_basis_bps"]
                numeric["funding_state_x_basis_delta"] = funding_delta_24h * (basis - dense_shift_matrix(basis, 24))
        groups = load_group_fields(loaded_symbols, timestamps, {"liquidity_tier"})
        idx = smoke_column_indices(timestamps)
        numeric = {key: value[:, idx] for key, value in numeric.items()}
        groups = {key: value[:, idx] for key, value in groups.items()}
        evaluator = A7AB4Evaluator(numeric, groups)

        for n, row in enumerate(sample.to_dict("records"), start=1):
            expr = str(row["expression"])
            try:
                signal = evaluator.eval(expr)
                finite = np.isfinite(signal)
                finite_share = float(finite.mean()) if signal.size else 0.0
                nonzero_share = float((np.abs(signal[finite]) > 1e-12).mean()) if finite.any() else 0.0
                eval_success = True
                error = ""
                std_value = float(np.nanstd(signal)) if finite.any() else np.nan
            except Exception as exc:  # noqa: BLE001
                finite_share = 0.0
                nonzero_share = 0.0
                eval_success = False
                error = repr(exc)
                std_value = np.nan
            activity_ok = eval_success and finite_share >= MIN_FINITE_SHARE and nonzero_share >= MIN_NONZERO_SHARE
            material_rows.append(
                {
                    "blueprint_id": row["blueprint_id"],
                    "semantic_pair": row["semantic_pair"],
                    "motif": row["motif"],
                    "target_label_family": row["target_label_family"],
                    "eval_success": eval_success,
                    "finite_share": finite_share,
                    "nonzero_share": nonzero_share,
                    "activity_ok": activity_ok,
                    "std_value": std_value,
                    "error": error,
                }
            )
            if n % 100 == 0:
                print(f"[A7FF-52E] materialized {n}/{len(sample)}", flush=True)

    material = pd.DataFrame(material_rows)
    material.to_csv(RUNTIME / "a7ff52e_materialization_metrics.csv", index=False)

    if material.empty:
        summary = pd.DataFrame()
        eval_failure_count = len(sample) if not missing else 0
        activity_ok_rate = 0.0
        retained_families = 0
    else:
        eval_failure_count = int((~material["eval_success"]).sum())
        activity_ok_rate = float(material["activity_ok"].mean())
        retained_families = int(material.loc[material["activity_ok"], "semantic_pair"].nunique())
        summary = (
            material.groupby("semantic_pair", dropna=False)
            .agg(
                rows=("blueprint_id", "count"),
                eval_success_rows=("eval_success", "sum"),
                activity_ok_rows=("activity_ok", "sum"),
                median_finite_share=("finite_share", "median"),
                median_nonzero_share=("nonzero_share", "median"),
                median_std=("std_value", "median"),
            )
            .reset_index()
        )
    low_activity_families = (
        summary.loc[summary["activity_ok_rows"] == 0, "semantic_pair"].astype(str).sort_values().tolist()
        if not summary.empty
        else []
    )
    summary.to_csv(RUNTIME / "a7ff52e_summary.csv", index=False)

    if eval_failure_count != 0:
        blockers.append("eval_failure_count_nonzero")
    if len(missing) != 0:
        blockers.append("missing_field_count_nonzero")
    if retained_families < 6:
        blockers.append("families_retained_below_6")
    if activity_ok_rate < 0.60:
        blockers.append("activity_ok_rate_below_0p60")

    manifest = {
        "stage": "A7FF-52E",
        "generated_at": now_utc(),
        "decision": "PASS_A7FF52E_MATERIALIZATION_PREFLIGHT_READY_FOR_NUMERIC_CONTRACT"
        if not blockers
        else "HOLD_A7FF52E_MATERIALIZATION_PREFLIGHT_FAIL",
        "blockers": sorted(set(blockers)),
        "sample_rows": int(len(sample)),
        "sample_family_count": int(sample["semantic_pair"].nunique()),
        "base_field_count": int(len(base_fields)),
        "latent_field_count": int(len(latent_fields)),
        "dense_field_count": int(len(dense_fields)),
        "missing_fields": sorted(missing),
        "low_activity_families": low_activity_families,
        "eval_failure_count": int(eval_failure_count),
        "activity_ok_rate": activity_ok_rate,
        "families_retained": int(retained_families),
        "execution_authorization_source": "latest_user_continue_request_after_A7FF52_contract",
        "executes_materialization": True,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_numeric_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff52e_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-52E MATERIALIZATION PREFLIGHT

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-52E evaluates a 1,200-row family-balanced materialization sample from A7FF51E. It does not compute labels, numeric replay, or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Family Summary

{md_table(summary)}

## Boundary

```text
materialization executed: true
numeric replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
