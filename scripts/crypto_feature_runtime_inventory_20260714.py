from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runtime" / "crypto_feature_runtime_inventory_20260714"
REPORT = ROOT / "reports" / "CRYPTO_FEATURE_RUNTIME_INVENTORY_20260714.md"

ARCHIVE_COMMIT = "1ed5acd"
ARCHIVE_BASE = (
    "archive/deprecated_crypto_a7_20260527/runtime/runtime/"
    "a7v1_feature_registry_smoke/a7v1_base_feature_registry.csv"
)
ARCHIVE_DERIVED = (
    "archive/deprecated_crypto_a7_20260527/runtime/runtime/"
    "a7v1_feature_registry_smoke/a7v1_derived_feature_specs.csv"
)
ARCHIVE_GENERATOR = (
    "archive/deprecated_crypto_a7_20260527/scripts/scripts/"
    "crypto_a7v1_feature_registry_and_smoke.py"
)

ACTIVE_SOURCE = ROOT / "runtime/a7eff2_git_release_20260711/a7eff2_active_field_registry.csv"
APPROVAL_SOURCE = ROOT / "runtime/a7input0_input_approval_package/a7input0_input_approval_registry.csv"
ONTOLOGY_SOURCE = ROOT / "runtime/a7ffr1_field_ontology_v3/a7ffr1_field_ontology_v3.csv"
LINEAGE_SOURCE = ROOT / "runtime/a7al0r_code_feature_regime_readiness_audit/a7al0r_feature_lineage_ledger.csv"
GRAPH_SOURCE = ROOT / ".planning/graphs/graph.json"

RUNTIME_ENTRYPOINT = "scripts/crypto_a7source5_a7search7_source_lag_reward_flow.py"
REWARD_GENERATOR = "scripts/crypto_a7reward1_portfolio_reward_model.py"
FORMULA_GENERATOR = "alphafactory_crypto/engines/formula_gen_v2_adapter.py"

INVENTORY_COLUMNS = [
    "field_id",
    "source_field",
    "representation_id",
    "feature_family",
    "frequency",
    "PIT/source_lag",
    "registry_status",
    "search_allowed",
    "runtime_loaded",
    "runtime_entrypoint",
    "consumer_lane",
    "primitive_eligible",
    "portfolio_mapping",
    "notes",
]


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def git_bytes(spec: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(ROOT), "show", spec])


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_csv_bytes(payload: bytes) -> list[dict[str, str]]:
    text = payload.decode("utf-8-sig").splitlines()
    return list(csv.DictReader(text))


def write_csv(path: Path, rows: Iterable[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def bool_text(value: object) -> str:
    return "true" if str(value).strip().lower() in {"1", "true", "yes"} else "false"


def first_nonempty(*values: object) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    source_head = git("rev-parse", "HEAD")

    graph = json.loads(GRAPH_SOURCE.read_text(encoding="utf-8"))
    graph_built_sha = str(graph.get("built_at_commit", ""))
    graph_file_commit = git("log", "-1", "--format=%H", "--", str(GRAPH_SOURCE.relative_to(ROOT)))

    base_all = read_csv_bytes(git_bytes(f"{ARCHIVE_COMMIT}:{ARCHIVE_BASE}"))
    base_rows = [row for row in base_all if row.get("role") == "feature"]
    derived_rows = read_csv_bytes(git_bytes(f"{ARCHIVE_COMMIT}:{ARCHIVE_DERIVED}"))
    active_rows = read_csv(ACTIVE_SOURCE)
    approval_rows = read_csv(APPROVAL_SOURCE)
    ontology_rows = read_csv(ONTOLOGY_SOURCE)
    lineage_rows = read_csv(LINEAGE_SOURCE)

    if len(base_rows) != 94:
        raise RuntimeError(f"Expected 94 aggTrades base features, found {len(base_rows)}")
    if len(derived_rows) != 5211:
        raise RuntimeError(f"Expected 5,211 derived specs, found {len(derived_rows)}")
    if len(active_rows) != 10:
        raise RuntimeError(f"Expected 10 A7EFF2 active fields, found {len(active_rows)}")
    if len(approval_rows) != 36:
        raise RuntimeError(f"Expected 36 A7INPUT0 approval rows, found {len(approval_rows)}")

    base_out = OUT / "aggtrades_base_feature_registry_94.csv"
    derived_out = OUT / "aggtrades_derived_feature_specs_5211.csv"
    active_out = OUT / "latest_active_field_registry.csv"
    approval_out = OUT / "latest_input_approval_registry.csv"
    lineage_out = OUT / "feature_lineage_ledger.csv"
    epoch_out = OUT / "current_epoch_runtime_fields.csv"
    static_out = OUT / "field_representation_lane_generator_map.csv"
    inventory_out = OUT / "CRYPTO_FEATURE_RUNTIME_INVENTORY.csv"

    write_csv(base_out, base_rows, list(base_rows[0]))
    write_csv(derived_out, derived_rows, list(derived_rows[0]))
    shutil.copyfile(ACTIVE_SOURCE, active_out)
    shutil.copyfile(APPROVAL_SOURCE, approval_out)

    active_by_field = {row["field_name"]: row for row in active_rows}
    approval_by_field = {row["field"]: row for row in approval_rows}
    ontology_by_field = {row["field_name"]: row for row in ontology_rows}
    lineage_by_field = {row["field_name"]: row for row in lineage_rows}

    inventory: dict[str, dict[str, str]] = {}
    lineage: list[dict[str, str]] = []

    for row in base_rows:
        field = row["field_name"]
        inventory[field] = {
            "field_id": field,
            "source_field": f"aggtrades_enhanced_v1::{field}",
            "representation_id": f"agg_base::{field}",
            "feature_family": row["field_family"],
            "frequency": "1h",
            "PIT/source_lag": "+1h; available_after_hour_close_plus_join_lag",
            "registry_status": "A7V1_BASE_REGISTERED_ARCHIVED_SOURCE",
            "search_allowed": "false",
            "runtime_loaded": "false",
            "runtime_entrypoint": f"git:{ARCHIVE_COMMIT}:{ARCHIVE_GENERATOR}",
            "consumer_lane": "A7V_AGG_AWARE_OPT_IN_DRYRUN",
            "primitive_eligible": bool_text(row["generator_enabled"]),
            "portfolio_mapping": "not_mapped_current_epoch",
            "notes": "Registered base feature; historical config forbids full search and same-hour execution.",
        }
        lineage.append(
            {
                "field_id": field,
                "lineage_kind": "aggtrades_hourly_base",
                "source_fields": "Binance Futures aggTrades hourly enhanced panel",
                "transform": "registered hourly aggregation; exact data-builder formula not stored in A7V1 registry",
                "window_hours": "1",
                "PIT/source_lag": "+1h",
                "source_path": f"git:{ARCHIVE_COMMIT}:{ARCHIVE_BASE}",
                "lineage_status": "REGISTRY_RECOVERED_FORMULA_DETAIL_EXTERNAL",
            }
        )

    for row in derived_rows:
        field = row["derived_feature_id"]
        lag = row["feature_available_lag_bars"]
        inventory[field] = {
            "field_id": field,
            "source_field": row["base_fields"],
            "representation_id": f"agg_derived::{row['production_family']}::{row['transform']}",
            "feature_family": row["base_field_families"],
            "frequency": "1h",
            "PIT/source_lag": f"+{lag}h specification lag",
            "registry_status": "A7V1_DERIVED_SPEC_ARCHIVED_SOURCE",
            "search_allowed": "false",
            "runtime_loaded": "false",
            "runtime_entrypoint": f"git:{ARCHIVE_COMMIT}:{ARCHIVE_GENERATOR}",
            "consumer_lane": "A7V_AGG_AWARE_OPT_IN_DRYRUN",
            "primitive_eligible": "false",
            "portfolio_mapping": "not_mapped_current_epoch",
            "notes": "Static spec only; historical A7V1 authorization did not permit full search.",
        }
        lineage.append(
            {
                "field_id": field,
                "lineage_kind": row["production_family"],
                "source_fields": row["base_fields"],
                "transform": row["transform"],
                "window_hours": row["window_hours"],
                "PIT/source_lag": f"+{lag}h specification lag",
                "source_path": f"git:{ARCHIVE_COMMIT}:{ARCHIVE_DERIVED}",
                "lineage_status": "SPEC_RECOVERED_NOT_CURRENTLY_MATERIALIZED",
            }
        )

    for field, row in ontology_by_field.items():
        lin = lineage_by_field.get(field, {})
        approval = approval_by_field.get(field, {})
        active = active_by_field.get(field, {})
        route = active.get("route", "")
        is_active = bool(active)
        if route == "derived_dep_generated":
            generator = REWARD_GENERATOR
        elif bool_text(row.get("generator_allowed_any_mode")) == "true":
            generator = FORMULA_GENERATOR
        else:
            generator = "none_static_contract_only"
        current = inventory.get(field, {})
        status = row.get("enforcement_status", "ONTOLOGY_V3")
        if approval:
            status += f"|{approval.get('source_input_approval', '')}"
        if is_active:
            status = f"A7EFF2_ACTIVE|{status}"
        inventory[field] = {
            "field_id": field,
            "source_field": first_nonempty(active.get("dependencies"), lin.get("source_field_names"), current.get("source_field")),
            "representation_id": f"field::{row.get('feature_class', 'unknown')}::{field}",
            "feature_family": first_nonempty(row.get("semantic_type_v3"), row.get("motif_field_family"), current.get("feature_family")),
            "frequency": "1h",
            "PIT/source_lag": first_nonempty(active.get("pit_lag_required"), row.get("pit_lag_required"), current.get("PIT/source_lag")),
            "registry_status": status,
            "search_allowed": bool_text(active.get("allowed_for_search") if is_active else row.get("allowed_for_search")),
            "runtime_loaded": "true" if is_active else "false",
            "runtime_entrypoint": RUNTIME_ENTRYPOINT if is_active else generator,
            "consumer_lane": "A7EFF2_SOURCE_LAG_REWARD" if is_active else first_nonempty(approval.get("input_route"), "ONTOLOGY_GOVERNED_POOL"),
            "primitive_eligible": bool_text(row.get("generator_allowed_any_mode")),
            "portfolio_mapping": "expression->exact_signal_identity->portfolio_weight_vector" if is_active else "candidate_expression_only",
            "notes": first_nonempty(active.get("memory_credit_input_status"), row.get("caveat"), current.get("notes")),
        }
        lineage.append(
            {
                "field_id": field,
                "lineage_kind": "current_ontology_field",
                "source_fields": first_nonempty(active.get("dependencies"), lin.get("source_field_names")),
                "transform": first_nonempty(lin.get("formula"), row.get("feature_class")),
                "window_hours": first_nonempty(lin.get("lookback_hours"), "1"),
                "PIT/source_lag": first_nonempty(active.get("pit_lag_required"), row.get("pit_lag_required")),
                "source_path": str(ONTOLOGY_SOURCE.relative_to(ROOT)).replace("\\", "/"),
                "lineage_status": "A7EFF2_RUNTIME_LOADED" if is_active else "ONTOLOGY_REGISTERED_NOT_CURRENT_EPOCH",
            }
        )

    for field, active in active_by_field.items():
        if field in ontology_by_field:
            continue
        approval = approval_by_field.get(field, {})
        inventory[field] = {
            "field_id": field,
            "source_field": active.get("dependencies", ""),
            "representation_id": f"field::derived_dep_generated::{field}",
            "feature_family": first_nonempty(active.get("semantic_type_v3"), active.get("source_family")),
            "frequency": "1h",
            "PIT/source_lag": active.get("pit_lag_required", ""),
            "registry_status": f"A7EFF2_ACTIVE|{active.get('enforcement_status', '')}",
            "search_allowed": bool_text(active.get("allowed_for_search")),
            "runtime_loaded": "true",
            "runtime_entrypoint": RUNTIME_ENTRYPOINT,
            "consumer_lane": "A7EFF2_SOURCE_LAG_REWARD",
            "primitive_eligible": "false",
            "portfolio_mapping": "expression->exact_signal_identity->portfolio_weight_vector",
            "notes": first_nonempty(active.get("memory_credit_input_status"), approval.get("route_reason")),
        }
        lineage.append(
            {
                "field_id": field,
                "lineage_kind": "current_runtime_derived_dependency",
                "source_fields": active.get("dependencies", ""),
                "transform": "runtime derived dependency",
                "window_hours": "1",
                "PIT/source_lag": active.get("pit_lag_required", ""),
                "source_path": str(ACTIVE_SOURCE.relative_to(ROOT)).replace("\\", "/"),
                "lineage_status": "A7EFF2_RUNTIME_LOADED_OUTSIDE_ONTOLOGY_V3",
            }
        )

    for field, approval in approval_by_field.items():
        if field in inventory:
            continue
        inventory[field] = {
            "field_id": field,
            "source_field": field,
            "representation_id": f"approval_only::{field}",
            "feature_family": approval.get("semantic_type", ""),
            "frequency": "1h",
            "PIT/source_lag": "inherit_from_field_contract",
            "registry_status": f"A7INPUT0|{approval.get('source_input_approval', '')}",
            "search_allowed": bool_text(approval.get("system_input_role") in {"signal_primary", "signal_redundant_cap"}),
            "runtime_loaded": "false",
            "runtime_entrypoint": "none_approval_contract_only",
            "consumer_lane": approval.get("input_route", ""),
            "primitive_eligible": "false",
            "portfolio_mapping": "approval_only_not_current_epoch",
            "notes": approval.get("route_reason", ""),
        }

    inventory_rows = sorted(inventory.values(), key=lambda row: row["field_id"])
    write_csv(inventory_out, inventory_rows, INVENTORY_COLUMNS)

    lineage_columns = [
        "field_id",
        "lineage_kind",
        "source_fields",
        "transform",
        "window_hours",
        "PIT/source_lag",
        "source_path",
        "lineage_status",
    ]
    write_csv(lineage_out, lineage, lineage_columns)

    epoch_columns = list(active_rows[0]) + ["runtime_loaded", "runtime_entrypoint", "consumer_lane", "epoch_id"]
    epoch_rows = [
        {
            **row,
            "runtime_loaded": "true",
            "runtime_entrypoint": RUNTIME_ENTRYPOINT,
            "consumer_lane": "A7EFF2_SOURCE_LAG_REWARD",
            "epoch_id": "A7EFF2_GIT_RELEASE_20260711",
        }
        for row in active_rows
    ]
    write_csv(epoch_out, epoch_rows, epoch_columns)

    static_columns = [
        "field_id",
        "representation_id",
        "consumer_lane",
        "generator",
        "runtime_entrypoint",
        "runtime_loaded",
        "mapping_status",
    ]
    static_rows = []
    for row in inventory_rows:
        if row["consumer_lane"] == "A7EFF2_SOURCE_LAG_REWARD":
            generator = REWARD_GENERATOR if "derived" in row["representation_id"] else "source_panel_column"
        elif row["consumer_lane"] == "A7V_AGG_AWARE_OPT_IN_DRYRUN":
            generator = f"git:{ARCHIVE_COMMIT}:{ARCHIVE_GENERATOR}"
        else:
            generator = row["runtime_entrypoint"]
        static_rows.append(
            {
                "field_id": row["field_id"],
                "representation_id": row["representation_id"],
                "consumer_lane": row["consumer_lane"],
                "generator": generator,
                "runtime_entrypoint": row["runtime_entrypoint"],
                "runtime_loaded": row["runtime_loaded"],
                "mapping_status": "CURRENT_EPOCH" if row["runtime_loaded"] == "true" else "STATIC_ONLY",
            }
        )
    write_csv(static_out, static_rows, static_columns)

    content_files = [base_out, derived_out, active_out, approval_out, lineage_out, epoch_out, static_out, inventory_out]
    source_paths = {
        base_out.name: f"git:{ARCHIVE_COMMIT}:{ARCHIVE_BASE}",
        derived_out.name: f"git:{ARCHIVE_COMMIT}:{ARCHIVE_DERIVED}",
        active_out.name: str(ACTIVE_SOURCE.relative_to(ROOT)).replace("\\", "/"),
        approval_out.name: str(APPROVAL_SOURCE.relative_to(ROOT)).replace("\\", "/"),
        lineage_out.name: ";".join(
            [
                f"git:{ARCHIVE_COMMIT}:{ARCHIVE_BASE}",
                f"git:{ARCHIVE_COMMIT}:{ARCHIVE_DERIVED}",
                str(ONTOLOGY_SOURCE.relative_to(ROOT)).replace("\\", "/"),
                str(LINEAGE_SOURCE.relative_to(ROOT)).replace("\\", "/"),
                str(ACTIVE_SOURCE.relative_to(ROOT)).replace("\\", "/"),
            ]
        ),
        epoch_out.name: str(ACTIVE_SOURCE.relative_to(ROOT)).replace("\\", "/"),
        static_out.name: "generated from CRYPTO_FEATURE_RUNTIME_INVENTORY.csv",
        inventory_out.name: "union of A7V1 registry/specs, ontology v3, A7INPUT0, and A7EFF2 active registry",
    }
    manifest_rows = [
        {
            "file": path.name,
            "rows": sum(1 for _ in path.open("r", encoding="utf-8")) - 1,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "source_path": source_paths[path.name],
        }
        for path in content_files
    ]
    manifest_csv = OUT / "asset_manifest.csv"
    write_csv(manifest_csv, manifest_rows, ["file", "rows", "bytes", "sha256", "source_path"])

    manifest = {
        "stage": "CRYPTO_FEATURE_RUNTIME_INVENTORY",
        "generated_at": generated_at,
        "source_head": source_head,
        "graph": {
            "built_at_commit": graph_built_sha,
            "graph_file_commit": graph_file_commit,
            "graph_sha256": sha256(GRAPH_SOURCE),
            "source_path": str(GRAPH_SOURCE.relative_to(ROOT)).replace("\\", "/"),
        },
        "epoch_interpretation": "Latest verifiable runtime epoch is A7EFF2_GIT_RELEASE_20260711.",
        "counts": {
            "aggtrades_base_features": len(base_rows),
            "aggtrades_derived_specs": len(derived_rows),
            "active_fields": len(active_rows),
            "input_approval_rows": len(approval_rows),
            "ontology_rows": len(ontology_rows),
            "inventory_rows": len(inventory_rows),
            "lineage_rows": len(lineage),
            "runtime_loaded_rows": sum(row["runtime_loaded"] == "true" for row in inventory_rows),
        },
        "boundaries": {
            "a7v1_assets_recovered_from_git_history": True,
            "a7v1_authorizes_full_search": False,
            "a7v1_current_epoch_loaded": False,
            "inventory_is_static_metadata_not_numeric_proof": True,
        },
        "files": manifest_rows,
    }
    manifest_json = OUT / "manifest.json"
    manifest_json.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    sums_rows = [
        {
            "file": path.name,
            "sha256": sha256(path),
            "source_path": source_paths.get(path.name, "generated manifest"),
        }
        for path in [*content_files, manifest_csv, manifest_json]
    ]
    write_csv(OUT / "SHA256SUMS.csv", sums_rows, ["file", "sha256", "source_path"])

    report = f"""# CRYPTO Feature Runtime Inventory 20260714

## Decision

`PASS_CRYPTO_FEATURE_RUNTIME_INVENTORY_BUILT`

This package is a metadata and lineage inventory. It does not authorize search, replay, alpha proof, or forward use.

## Scope

| Asset | Rows | Status |
|---|---:|---|
| aggTrades base feature registry | {len(base_rows)} | recovered exactly from Git history `{ARCHIVE_COMMIT}`; two non-feature schema/mask rows excluded |
| aggTrades derived feature specs | {len(derived_rows):,} | recovered exactly from Git history `{ARCHIVE_COMMIT}` |
| Latest active field registry | {len(active_rows)} | A7EFF2 release |
| Latest input approval registry | {len(approval_rows)} | A7INPUT0 |
| Unified runtime inventory | {len(inventory_rows):,} | static union with field-level deduplication |
| Feature lineage ledger | {len(lineage):,} | base, derived-spec, and ontology lineage rows |
| Current Epoch runtime-loaded fields | {len(active_rows)} | A7EFF2 only |

## Runtime Meaning

The repository does not define a standalone `Epoch` object. For this inventory, current Epoch means the latest verifiable release runtime, `A7EFF2_GIT_RELEASE_20260711`. Only its ten active fields are marked `runtime_loaded=true`.

The 94 base features and 5,211 derived specs are real A7V1 registry assets, but their original runtime directory was later removed. They were recovered from Git commit `{ARCHIVE_COMMIT}`. Historical A7V1 explicitly authorized an agg-aware dry run, not full search. They are therefore marked static/not loaded in the current Epoch.

## Identity

```text
source HEAD:       {source_head}
graph built SHA:   {graph_built_sha}
graph file commit: {graph_file_commit}
graph SHA256:      {sha256(GRAPH_SOURCE)}
updated UTC:       {generated_at}
```

## Files

`runtime/crypto_feature_runtime_inventory_20260714/asset_manifest.csv` records the SHA256 and source path for every content asset. `SHA256SUMS.csv` additionally hashes the manifest files; it intentionally omits its own self-hash.

## Known Boundary

The A7V1 base registry records field family, mask, scope, and lag but not the exact raw aggregation formula for every base feature. Those rows are marked `REGISTRY_RECOVERED_FORMULA_DETAIL_EXTERNAL` in the lineage ledger rather than being assigned invented lineage.
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
