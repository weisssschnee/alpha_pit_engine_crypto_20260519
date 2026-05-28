from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

try:
    import pyarrow.dataset as ds
except Exception:  # pragma: no cover
    ds = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "a7al2x4_replay_readiness_audit"
REPORT = ROOT / "reports" / "CRYPTO_A7AL2X4_REPLAY_READINESS_AUDIT_20260529.md"

X3_LEDGER = ROOT / "runtime" / "a7al2x3_family_balanced_dry_generation" / "a7al2x3_shared_pool_ledger.csv"
X3_AUTH = ROOT / "runtime" / "a7al2x3_family_balanced_dry_generation" / "a7al2x3_authorization_matrix.json"
BASE_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527")
REGIME_CONTRACT = ROOT / "runtime" / "a7al0g_upper_regime_state_builder" / "a7al0g_regime_state_contract.csv"
LATENT_REGISTRY = ROOT / "runtime" / "a7ak_lv1_latent_state_feature_build" / "a7ak_lv1_raw_state_registry.csv"
LATENT_MERGE = ROOT / "runtime" / "a7ak_lv2_response_merge_audit" / "a7ak_lv2_state_merge_map.csv"


FAST_EVALUATOR_OPS = {"Mean", "Delta", "Rank", "CSRank", "ZScore", "Mul", "Sub", "Add", "Neg", "Abs", "Sign"}
IMPLEMENTABLE_LOCAL_OPS = {"Clip", "Winsor"}
REQUIRES_STATE_MATERIALIZATION_OPS = {"StateMask", "GroupNeutralize", "LatentNeutralRank"}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, limit: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(limit).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def schema_names(path: Path) -> set[str]:
    if ds is None or not path.exists():
        return set()
    try:
        return set(ds.dataset(str(path), format="parquet").schema.names)
    except Exception:
        return set()


def split_pipe(value: str) -> list[str]:
    return [part for part in str(value).split("|") if part]


def classify_field(field: str, base_schema: set[str]) -> tuple[str, str]:
    if field in base_schema:
        return "ready_in_base_panel", "base_panel"
    if field.startswith("R") and field.endswith("_state"):
        return "requires_upper_regime_materialization", "a7al0g_upper_regime"
    if field in {
        "merged_latent_state_id",
        "raw_latent_state_id",
        "liquidity_tier",
        "meme_flag",
        "multiplier_group",
        "major_flag",
    }:
        return "requires_latent_taxonomy_materialization", "a7ak_lv/a7ak_taxonomy"
    if field in {"funding_rate_abs_168h", "funding_rate_mean_168h"}:
        return "requires_derived_feature_materialization", "a7ak_lv1_derived"
    if field == "binance_internal_mark_index_basis_bps":
        return "requires_alias_or_drop", "canonical_basis_alias"
    return "unknown_missing_field", "unknown"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    generated_at = now_utc()

    ledger = pd.read_csv(X3_LEDGER)
    selected = ledger[ledger["selected_for_family_balanced_preflight"].astype(str).str.lower().eq("true")].copy()
    base_schema = schema_names(BASE_PANEL)

    field_rows = []
    for field in sorted({f for text in selected["fields"].astype(str) for f in split_pipe(text)}):
        status, source = classify_field(field, base_schema)
        field_rows.append(
            {
                "field_name": field,
                "status": status,
                "source": source,
                "in_base_panel_schema": field in base_schema,
                "blocking_for_current_fast_replay": status != "ready_in_base_panel",
            }
        )
    field_audit = pd.DataFrame(field_rows)

    op_rows = []
    for op in sorted({op for text in selected["operator_signature"].astype(str) for op in split_pipe(text)}):
        if op in FAST_EVALUATOR_OPS:
            status = "ready_in_existing_fast_evaluator"
            blocking = False
        elif op in IMPLEMENTABLE_LOCAL_OPS:
            status = "needs_small_evaluator_extension"
            blocking = True
        elif op in REQUIRES_STATE_MATERIALIZATION_OPS:
            status = "needs_state_aware_evaluator_extension"
            blocking = True
        else:
            status = "unknown_operator"
            blocking = True
        op_rows.append(
            {
                "operator": op,
                "status": status,
                "blocking_for_current_fast_replay": blocking,
            }
        )
    operator_audit = pd.DataFrame(op_rows)

    family_readiness = (
        selected.groupby("objective_family")
        .agg(
            selected_count=("candidate_id", "count"),
            unique_fields=("fields", lambda s: len({f for text in s.astype(str) for f in split_pipe(text)})),
            unique_ops=("operator_signature", lambda s: len({o for text in s.astype(str) for o in split_pipe(text)})),
        )
        .reset_index()
    )
    blocking_fields = set(field_audit.loc[field_audit["blocking_for_current_fast_replay"], "field_name"].astype(str))
    blocking_ops = set(operator_audit.loc[operator_audit["blocking_for_current_fast_replay"], "operator"].astype(str))

    def family_blocking_fields(family: str) -> str:
        sub = selected[selected["objective_family"].eq(family)]
        fields = sorted({f for text in sub["fields"].astype(str) for f in split_pipe(text)} & blocking_fields)
        return "|".join(fields)

    def family_blocking_ops(family: str) -> str:
        sub = selected[selected["objective_family"].eq(family)]
        ops = sorted({o for text in sub["operator_signature"].astype(str) for o in split_pipe(text)} & blocking_ops)
        return "|".join(ops)

    family_readiness["blocking_fields"] = family_readiness["objective_family"].map(family_blocking_fields)
    family_readiness["blocking_operators"] = family_readiness["objective_family"].map(family_blocking_ops)
    family_readiness["ready_for_current_fast_replay"] = family_readiness["blocking_fields"].eq("") & family_readiness[
        "blocking_operators"
    ].eq("")

    materialization_plan = pd.DataFrame(
        [
            {
                "step": "A7AL-2X4M0",
                "name": "operator extension",
                "action": "Add Clip/Winsor and state-aware StateMask/GroupNeutralize/LatentNeutralRank support to a crypto replay evaluator.",
                "executes_replay": False,
                "authorizes_alpha": False,
            },
            {
                "step": "A7AL-2X4M1",
                "name": "upper-regime materialization",
                "action": "Materialize A7AL-0G train-frozen regime states into a replay matrix aligned by timestamp.",
                "executes_replay": False,
                "authorizes_alpha": False,
            },
            {
                "step": "A7AL-2X4M2",
                "name": "latent/taxonomy materialization",
                "action": "Materialize A7AK LV1/LV2 latent state ids plus meme/multiplier/major/liquidity-tier taxonomy into symbol-time panel.",
                "executes_replay": False,
                "authorizes_alpha": False,
            },
            {
                "step": "A7AL-2X4M3",
                "name": "family-balanced replay authorization",
                "action": "Only after M0-M2 pass, authorize numeric replay preflight on the 176 selected candidates.",
                "executes_replay": False,
                "authorizes_alpha": False,
            },
        ]
    )

    blockers: list[str] = []
    if field_audit["blocking_for_current_fast_replay"].any():
        blockers.append("state_or_derived_fields_not_materialized_for_fast_replay")
    if operator_audit["blocking_for_current_fast_replay"].any():
        blockers.append("operators_not_supported_by_existing_fast_replay")
    if not REGIME_CONTRACT.exists():
        blockers.append("upper_regime_contract_missing")
    if not LATENT_REGISTRY.exists() or not LATENT_MERGE.exists():
        blockers.append("latent_state_artifacts_missing")

    decision = (
        "HOLD_A7AL2X4_REPLAY_PREFLIGHT_NOT_READY_MATERIALIZATION_REQUIRED"
        if blockers
        else "PASS_A7AL2X4_REPLAY_READINESS_READY_FOR_NUMERIC_PREFLIGHT"
    )
    manifest = {
        "decision": decision,
        "generated_at": generated_at,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "authorizes_numeric_replay_preflight": False,
        "authorizes_a7al2y_generation": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "selected_candidate_count": int(selected.shape[0]),
        "field_count": int(field_audit.shape[0]),
        "blocking_field_count": int(field_audit["blocking_for_current_fast_replay"].sum()),
        "operator_count": int(operator_audit.shape[0]),
        "blocking_operator_count": int(operator_audit["blocking_for_current_fast_replay"].sum()),
        "blockers": blockers,
    }
    authorization = {
        "decision": decision,
        "numeric_replay_preflight": "NOT_AUTHORIZED" if blockers else "READY_FOR_REVIEW_NOT_AUTHORIZED",
        "a7al2y_generation": "NOT_AUTHORIZED",
        "large_formula_search": "NOT_AUTHORIZED",
        "alpha_proof": "NOT_AUTHORIZED",
        "shadow_paper_live": "NOT_AUTHORIZED",
        "reason": "Current fast replay cannot honestly evaluate X3 family-balanced selected candidates until state fields and operators are materialized.",
    }

    field_audit.to_csv(RUNTIME / "a7al2x4_field_materialization_audit.csv", index=False)
    operator_audit.to_csv(RUNTIME / "a7al2x4_operator_support_audit.csv", index=False)
    family_readiness.to_csv(RUNTIME / "a7al2x4_family_readiness_audit.csv", index=False)
    materialization_plan.to_csv(RUNTIME / "a7al2x4_materialization_plan.csv", index=False)
    write_json(RUNTIME / "a7al2x4_manifest.json", manifest)
    write_json(RUNTIME / "a7al2x4_authorization_matrix.json", authorization)

    report = f"""# CRYPTO A7AL-2X4 Replay Readiness Audit

Generated: {generated_at}

## Decision

```text
{decision}
```

This stage audits whether the A7AL-2X3 family-balanced selected queue can be evaluated by the existing fast replay engine. It executes no numeric replay, no generation, no training, and no search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Family Readiness

{md_table(family_readiness)}

## Field Materialization Audit

{md_table(field_audit)}

## Operator Support Audit

{md_table(operator_audit)}

## Materialization Plan

{md_table(materialization_plan)}

## Authorization

```json
{json.dumps(authorization, indent=2, sort_keys=True)}
```

## Boundary

```text
No numeric replay executed.
No search.
No selector scoring.
No May in generation/ranking/selector/mutation.
No alpha proof / shadow / paper / live.
```
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
