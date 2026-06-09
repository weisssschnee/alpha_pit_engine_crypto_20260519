from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
DATE = "20260609"
STAGE = "A7LS-FIELD-GATE-0"

DEFAULT_QUEUE = Path(
    r"G:\AlphaFactory_CryptoData\research_runtime\a7ls28b_broader_targeted_space_queue_20260609\a7ls28b_targeted_blueprint_queue.csv"
)
QUEUE_PATH = Path(os.environ.get("A7LS_FIELD_GATE_QUEUE", str(DEFAULT_QUEUE)))
EXTENSION_REGISTRY = os.environ.get("A7LS_FIELD_GATE_EXTENSION_REGISTRY", "")
RUNTIME = Path(
    os.environ.get(
        "A7LS_FIELD_GATE_RUNTIME",
        str(REPO / "runtime" / "a7ls_field_gate_current_queue_20260609"),
    )
)
REPORT = Path(
    os.environ.get(
        "A7LS_FIELD_GATE_REPORT",
        str(REPO / "reports" / f"CRYPTO_A7LS_FIELD_GATE_CURRENT_QUEUE_{DATE}.md"),
    )
)

FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
OPERATORS = {
    "Mean",
    "Delta",
    "TSRank",
    "Decay",
    "Rank",
    "CSRank",
    "ZScore",
    "Mul",
    "Sub",
    "Add",
    "Neg",
    "Abs",
    "Sign",
    "SafeDiv",
    "Clip",
    "Winsor",
}
SYSTEM_FIELDS = {"trade_close", "realized_vol_168h"}
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
    "quote_volume_z_168h": {"trade_quote_volume"},
    "account_position_divergence": {
        "top_long_short_position_ratio_last",
        "top_long_short_account_ratio_last",
    },
    "top_global_account_divergence": {
        "top_long_short_account_ratio_last",
        "global_long_short_account_ratio_last",
    },
}
DERIVED_DEPS["basis_abs_168h"] = {"mark_index_basis_bps"}
DERIVED_DEPS["premium_abs_168h"] = {"premium_close_bps"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 40) -> str:
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


def expression_fields(expression: str) -> set[str]:
    out: set[str] = set()
    for token in FIELD_RE.findall(str(expression)):
        if token in OPERATORS or token.lower() in {"nan", "inf", "true", "false"}:
            continue
        out.add(token)
    return out


def parquet_schema(path: Path) -> set[str]:
    if not path.exists():
        return set()
    if path.is_dir():
        import pyarrow.dataset as ds

        return set(ds.dataset(str(path), format="parquet").schema.names)
    import pyarrow.parquet as pq

    return set(pq.ParquetFile(path).schema.names)


def load_f3_fields() -> set[str]:
    path = REPO / "runtime" / "a7aif3_materialization_evaluator_parity" / "a7aif3_field_materialization_matrix.csv"
    if not path.exists():
        return set()
    df = pd.read_csv(path)
    if "field_name" not in df.columns:
        return set()
    return set(df["field_name"].astype(str))


def classify_field(
    field: str,
    base_schema: set[str],
    latent_schema: set[str],
    upper_schema: set[str],
    f3_fields: set[str],
    extension_fields: set[str],
) -> dict[str, Any]:
    route = "unresolved"
    canonical = field
    deps: list[str] = []
    dependency_status = "not_applicable"

    if field in base_schema:
        route = "base_schema"
    elif field in latent_schema:
        route = "latent_schema"
    elif field in upper_schema:
        route = "upper_schema_direct"
    elif field in UPPER_ALIASES:
        canonical = UPPER_ALIASES[field]
        route = "upper_alias" if canonical in upper_schema else "upper_alias_missing_source"
    elif field in DENSE_FUNDING_FIELDS:
        route = "dense_funding_generated"
        deps = ["funding_rate"]
        if field == "funding_state_x_basis_delta":
            deps.append("mark_index_basis_bps")
    elif field in DERIVED_DEPS:
        route = "derived_dep_generated"
        deps = sorted(DERIVED_DEPS[field])
    else:
        route = "unresolved"

    if deps:
        missing_deps = sorted(d for d in deps if d not in base_schema and d not in latent_schema and d not in upper_schema)
        dependency_status = "deps_resolved" if not missing_deps else "deps_missing:" + ";".join(missing_deps)

    in_f3_contract = field in f3_fields
    in_extension_registry = field in extension_fields
    if route in {"upper_alias", "dense_funding_generated", "derived_dep_generated"} and not in_f3_contract:
        contract_status = "RESOLVED_BY_RUNNER_EXTENSION_NEEDS_REGISTRY_BACKFILL"
    elif route in {"upper_alias_missing_source", "unresolved"} or dependency_status.startswith("deps_missing"):
        contract_status = "BLOCK_UNRESOLVED_FIELD"
    elif in_f3_contract:
        contract_status = "OK_IN_A7AIF3_CONTRACT"
    else:
        contract_status = "OK_SCHEMA_DIRECT_NOT_IN_A7AIF3"
    if in_extension_registry and contract_status != "BLOCK_UNRESOLVED_FIELD":
        contract_status = "OK_BACKFILLED_BY_EXTENSION_REGISTRY"

    return {
        "field": field,
        "canonical_field": canonical,
        "route": route,
        "dependencies": ";".join(deps),
        "dependency_status": dependency_status,
        "in_a7aif3_field_matrix": in_f3_contract,
        "in_extension_registry": in_extension_registry,
        "contract_status": contract_status,
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    if not QUEUE_PATH.exists():
        raise FileNotFoundError(QUEUE_PATH)

    from scripts.crypto_a7al2x5_evaluator_preflight_smoke import BASE_DIR, LATENT_PANEL, UPPER_REGIME_PANEL

    queue = pd.read_csv(QUEUE_PATH)
    if "expression" not in queue.columns:
        raise ValueError(f"queue has no expression column: {QUEUE_PATH}")

    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    upper_schema = parquet_schema(UPPER_REGIME_PANEL)
    f3_fields = load_f3_fields()
    extension_fields: set[str] = set()
    extension_registry_path = ""
    if EXTENSION_REGISTRY:
        extension_registry_path = EXTENSION_REGISTRY
        extension_path = Path(EXTENSION_REGISTRY)
        if not extension_path.exists():
            raise FileNotFoundError(extension_path)
        extension = json.loads(extension_path.read_text(encoding="utf-8"))
        extension_fields = set(extension.get("field_roles", {}).keys())

    field_usage: Counter[str] = Counter()
    formula_rows: list[dict[str, Any]] = []
    field_examples: dict[str, str] = {}
    for row in queue.to_dict("records"):
        fields = sorted(expression_fields(str(row["expression"])))
        for field in fields:
            field_usage[field] += 1
            field_examples.setdefault(field, str(row["expression"]))
        formula_rows.append(
            {
                "blueprint_id": row.get("blueprint_id", ""),
                "semantic_pair": row.get("semantic_pair", ""),
                "motif": row.get("motif", ""),
                "mutation_kind": row.get("mutation_kind", row.get("mutation", "")),
                "field_count": len(fields),
                "fields": ";".join(fields),
                "expression": row.get("expression", ""),
            }
        )

    all_fields = set(field_usage) | SYSTEM_FIELDS
    field_map = pd.DataFrame(
        [
            {
                **classify_field(field, base_schema, latent_schema, upper_schema, f3_fields, extension_fields),
                "formula_usage_count": int(field_usage.get(field, 0)),
                "is_system_required": field in SYSTEM_FIELDS,
                "example_expression": field_examples.get(field, ""),
            }
            for field in sorted(all_fields)
        ]
    )
    drift_fields = field_map[
        field_map["contract_status"].isin(
            [
                "RESOLVED_BY_RUNNER_EXTENSION_NEEDS_REGISTRY_BACKFILL",
                "OK_SCHEMA_DIRECT_NOT_IN_A7AIF3",
            ]
        )
        & (~field_map["is_system_required"])
    ].copy()
    blocked_fields = field_map[field_map["contract_status"].eq("BLOCK_UNRESOLVED_FIELD")].copy()

    route_by_field = dict(zip(field_map["field"], field_map["route"]))
    status_by_field = dict(zip(field_map["field"], field_map["contract_status"]))
    formula_audit = pd.DataFrame(formula_rows)
    formula_audit["unresolved_fields"] = formula_audit["fields"].apply(
        lambda s: ";".join([f for f in str(s).split(";") if status_by_field.get(f) == "BLOCK_UNRESOLVED_FIELD"])
    )
    formula_audit["contract_drift_fields"] = formula_audit["fields"].apply(
        lambda s: ";".join(
            [
                f
                for f in str(s).split(";")
                if status_by_field.get(f)
                in {
                    "RESOLVED_BY_RUNNER_EXTENSION_NEEDS_REGISTRY_BACKFILL",
                    "OK_SCHEMA_DIRECT_NOT_IN_A7AIF3",
                }
            ]
        )
    )
    formula_audit["field_routes"] = formula_audit["fields"].apply(
        lambda s: ";".join([f"{f}:{route_by_field.get(f, 'unknown')}" for f in str(s).split(";") if f])
    )
    formula_audit["gate_decision"] = "PASS"
    formula_audit.loc[formula_audit["contract_drift_fields"].astype(str).str.len() > 0, "gate_decision"] = (
        "HOLD_CONTRACT_DRIFT_BACKFILL_REQUIRED"
    )
    formula_audit.loc[formula_audit["unresolved_fields"].astype(str).str.len() > 0, "gate_decision"] = (
        "BLOCK_UNRESOLVED_FIELD"
    )

    route_summary = (
        field_map.groupby(["route", "contract_status"], dropna=False)
        .agg(field_count=("field", "count"), formula_usage_count=("formula_usage_count", "sum"))
        .reset_index()
        .sort_values(["contract_status", "formula_usage_count"], ascending=[True, False])
    )
    formula_gate_summary = (
        formula_audit.groupby(["gate_decision", "semantic_pair"], dropna=False)
        .size()
        .reset_index(name="formula_count")
        .sort_values("formula_count", ascending=False)
    )
    drift_summary = (
        drift_fields.groupby(["contract_status", "route"], dropna=False)
        .agg(field_count=("field", "count"), formula_usage_count=("formula_usage_count", "sum"))
        .reset_index()
        .sort_values("formula_usage_count", ascending=False)
    )

    field_map.to_csv(RUNTIME / "a7ls_field_gate_field_route_map.csv", index=False)
    formula_audit.to_csv(RUNTIME / "a7ls_field_gate_formula_audit.csv", index=False)
    drift_fields.to_csv(RUNTIME / "a7ls_field_gate_contract_drift_fields.csv", index=False)
    blocked_fields.to_csv(RUNTIME / "a7ls_field_gate_blocked_fields.csv", index=False)
    route_summary.to_csv(RUNTIME / "a7ls_field_gate_route_summary.csv", index=False)
    formula_gate_summary.to_csv(RUNTIME / "a7ls_field_gate_formula_gate_summary.csv", index=False)
    drift_summary.to_csv(RUNTIME / "a7ls_field_gate_drift_summary.csv", index=False)

    unresolved_count = int(len(blocked_fields))
    drift_count = int(len(drift_fields))
    blocked_formula_count = int((formula_audit["gate_decision"] == "BLOCK_UNRESOLVED_FIELD").sum())
    drift_formula_count = int((formula_audit["gate_decision"] == "HOLD_CONTRACT_DRIFT_BACKFILL_REQUIRED").sum())
    if unresolved_count:
        decision = "BLOCK_A7LS_FIELD_GATE_UNRESOLVED_FIELDS"
        authorizes_next_search = False
    elif drift_count:
        decision = "HOLD_A7LS_FIELD_GATE_CONTRACT_DRIFT_BACKFILL_REQUIRED"
        authorizes_next_search = False
    else:
        decision = "PASS_A7LS_FIELD_GATE_CURRENT_QUEUE_CLEAN"
        authorizes_next_search = True

    manifest = {
        "stage": STAGE,
        "decision": decision,
        "generated_at": now_iso(),
        "queue_path": str(QUEUE_PATH),
        "queue_rows": int(len(queue)),
        "expression_field_count": int(len(field_usage)),
        "total_field_count_including_system": int(len(field_map)),
        "a7aif3_field_matrix_count": int(len(f3_fields)),
        "extension_registry_path": extension_registry_path,
        "extension_registry_field_count": int(len(extension_fields)),
        "unresolved_field_count": unresolved_count,
        "contract_drift_field_count": drift_count,
        "blocked_formula_count": blocked_formula_count,
        "contract_drift_formula_count": drift_formula_count,
        "authorizes_current_running_wave_to_continue": unresolved_count == 0,
        "authorizes_next_search_expansion": authorizes_next_search,
        "authorizes_alpha_proof": False,
        "executes_numeric_compute": False,
        "executes_replay": False,
    }
    write_json(RUNTIME / "a7ls_field_gate_manifest.json", manifest)

    report = f"""# CRYPTO A7LS Field Gate Current Queue {DATE}

## Decision

`{decision}`

This is a field ingress gate for the current A7LS28B queue. It does not run numeric compute, replay, search, or alpha proof.

## Counts

- queue_rows: {len(queue)}
- expression_field_count: {len(field_usage)}
- total_field_count_including_system: {len(field_map)}
- unresolved_field_count: {unresolved_count}
- contract_drift_field_count: {drift_count}
- blocked_formula_count: {blocked_formula_count}
- contract_drift_formula_count: {drift_formula_count}
- authorizes_current_running_wave_to_continue: {str(unresolved_count == 0).lower()}
- authorizes_next_search_expansion: {str(authorizes_next_search).lower()}

## Interpretation

Unresolved fields block execution. Fields resolved only through runner-local aliases or derived dependency code are not immediate execution blockers, but they are contract drift until they are backfilled into the shared field registry / A7AIF materialization matrix.

## Route Summary

{md_table(route_summary, 80)}

## Drift Fields

{md_table(drift_fields[["field", "route", "canonical_field", "dependencies", "formula_usage_count", "contract_status"]], 80)}

## Blocked Fields

{md_table(blocked_fields[["field", "route", "dependencies", "dependency_status", "formula_usage_count", "contract_status"]], 80)}

## Formula Gate Summary

{md_table(formula_gate_summary, 80)}

## Outputs

- `{RUNTIME / "a7ls_field_gate_manifest.json"}`
- `{RUNTIME / "a7ls_field_gate_field_route_map.csv"}`
- `{RUNTIME / "a7ls_field_gate_formula_audit.csv"}`
- `{RUNTIME / "a7ls_field_gate_contract_drift_fields.csv"}`
- `{RUNTIME / "a7ls_field_gate_blocked_fields.csv"}`
- `{RUNTIME / "a7ls_field_gate_route_summary.csv"}`
- `{RUNTIME / "a7ls_field_gate_formula_gate_summary.csv"}`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
