"""Deterministic management view over existing crypto field authorities.

The compiled tables in this module are navigation and consistency artifacts.
They do not replace the inventory, ontology, approval, lineage, carrier,
typed-compiler, or materializer authorities from which they are built.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

from alphafactory_crypto.broad_search.compositional18m import field_role_surface
from alphafactory_crypto.broad_search.expression import FieldContract
from alphafactory_crypto.field_information import compile_token_catalog, sha256_file


def _payload_sha(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def _git_sha(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def _first(*values: Any) -> str:
    return next((text for value in values if (text := _text(value))), "")


def _venue(field_id: str) -> str:
    return field_id.split("__", 1)[0].upper() if "__" in field_id else ""


def _statistic(field_id: str) -> str:
    for suffix in (
        "_last",
        "_mean",
        "_min",
        "_max",
        "_std",
        "_sum",
        "_count",
        "_ratio",
        "_vwap",
    ):
        if field_id.endswith(suffix):
            return suffix.removeprefix("_").upper()
    return "DERIVED" if "__" in field_id and not _venue(field_id) else "LEVEL"


def _grain(frequency: Any, carrier_id: str = "") -> str:
    text = _text(frequency).lower()
    if "hour" in text or text in {"1h", "hourly"} or carrier_id:
        return "1H"
    return _text(frequency).upper() or "UNRESOLVED_FROM_CURRENT_AUTHORITIES"


def _unique_nonempty(rows: list[dict[str, Any]], key: str) -> set[str]:
    return {_text(row.get(key)) for row in rows if _text(row.get(key))}


def compile_management_tables(
    repo_root: Path, config: Mapping[str, Any]
) -> dict[str, pd.DataFrame]:
    """Compile one canonical record per discovered identity, fail closed on drift."""

    inputs = config["inputs"]
    field_config = _read_json(repo_root / inputs["field_information_config"])
    token_catalog = compile_token_catalog(repo_root, field_config)
    inventory = pd.read_csv(repo_root / field_config["inputs"]["inventory"])
    lineage = pd.read_csv(repo_root / field_config["inputs"]["lineage"])
    ontology = pd.read_csv(repo_root / inputs["ontology"])
    approval = pd.read_csv(repo_root / inputs["approval"])
    carrier_contracts = _read_json(repo_root / inputs["carrier_contracts"])
    reachability = pd.read_parquet(repo_root / inputs["field_reachability"])

    inventory_by_id = inventory.set_index("field_id", drop=False).to_dict("index")
    lineage_rows: dict[str, list[dict[str, Any]]] = {}
    ontology_rows: dict[str, list[dict[str, Any]]] = {}
    approval_rows: dict[str, list[dict[str, Any]]] = {}
    for row in lineage.to_dict("records"):
        lineage_rows.setdefault(str(row["field_id"]), []).append(row)
    for row in ontology.to_dict("records"):
        ontology_rows.setdefault(str(row["field_name"]), []).append(row)
    for row in approval.to_dict("records"):
        approval_rows.setdefault(str(row["field"]), []).append(row)

    inventory_ids = set(inventory["field_id"].astype(str))
    conflicts: list[dict[str, Any]] = []
    for authority, values in (
        ("ontology", set(ontology["field_name"].astype(str))),
        ("approval", set(approval["field"].astype(str))),
        ("lineage", set(lineage["field_id"].astype(str))),
    ):
        for field_id in sorted(values - inventory_ids):
            conflicts.append(
                {
                    "conflict_type": "ORPHAN_AUTHORITY_IDENTITY",
                    "canonical_field_id": f"FIELD:{field_id}",
                    "field_id": field_id,
                    "authorities": authority,
                    "detail": "identity is absent from the inventory authority",
                    "fatal": True,
                }
            )

    for field_id in sorted(inventory_ids):
        checks = (
            ("LINEAGE_DIVERGENCE", lineage_rows.get(field_id, []), "lineage_status"),
            (
                "APPROVAL_DIVERGENCE",
                approval_rows.get(field_id, []),
                "source_input_approval",
            ),
            (
                "ONTOLOGY_SEMANTIC_TYPE_DIVERGENCE",
                ontology_rows.get(field_id, []),
                "semantic_type_v3",
            ),
        )
        for conflict_type, rows, key in checks:
            values = _unique_nonempty(rows, key)
            if len(values) > 1:
                conflicts.append(
                    {
                        "conflict_type": conflict_type,
                        "canonical_field_id": f"FIELD:{field_id}",
                        "field_id": field_id,
                        "authorities": key,
                        "detail": json.dumps(sorted(values)),
                        "fatal": True,
                    }
                )

    catalog_rows: dict[str, dict[str, Any]] = {}
    canonical_by_field: dict[str, str] = {}
    alias_rows: list[dict[str, Any]] = []
    derived_rows: list[dict[str, Any]] = []
    for row in token_catalog.to_dict("records"):
        field_id = str(row["field_id"])
        canonical = str(row["token_id"])
        canonical_by_field[field_id] = canonical
        kind = str(row["token_kind"])
        inventory_row = inventory_by_id.get(field_id, {})
        lineage_row = (lineage_rows.get(field_id) or [{}])[0]
        ontology_row = (ontology_rows.get(field_id) or [{}])[0]
        approval_row = (approval_rows.get(field_id) or [{}])[0]
        registry_status = _text(inventory_row.get("registry_status"))
        is_deprecated = any(
            marker in registry_status.upper()
            for marker in ("DEPRECATED", "SUPERSEDED", "RETIRED")
        )
        catalog_rows[canonical] = {
            "canonical_field_id": canonical,
            "field_id": field_id,
            "record_kind": "DERIVED_VIEW" if kind == "DERIVED" else "BASE_FIELD",
            "family": str(row.get("family") or "unknown"),
            "source": str(row.get("source") or ""),
            "value_type": "UNRESOLVED_FROM_CURRENT_AUTHORITIES",
            "unit": "UNRESOLVED_FROM_CURRENT_AUTHORITIES",
            "observable_lag_hours": _first(
                row.get("observable_lag"), inventory_row.get("PIT/source_lag")
            ),
            "pit_authority": (
                f"LINEAGE_LEDGER:{_text(lineage_row.get('lineage_status'))}"
                if _text(lineage_row.get("lineage_status"))
                else "UNRESOLVED_FROM_CURRENT_AUTHORITIES"
            ),
            "lineage_status": _text(lineage_row.get("lineage_status")),
            "lineage_source_fields": _text(lineage_row.get("source_fields")),
            "approval_status": _first(
                approval_row.get("source_input_approval"), registry_status
            ),
            "ontology_semantic_type": _text(
                ontology_row.get("semantic_type_v3")
            )
            or "UNRESOLVED_FROM_CURRENT_AUTHORITIES",
            "grain": _grain(inventory_row.get("frequency")),
            "venue": _venue(field_id) or "MULTI_VENUE_OR_UNSPECIFIED",
            "statistic": _statistic(field_id),
            "deprecation_status": (
                registry_status if is_deprecated else "CURRENT_OR_UNSPECIFIED"
            ),
            "materialization_status": (
                "LAZY_EXISTING_RECIPE"
                if kind == "DERIVED"
                else (
                    "CURRENT_RUNTIME_MATERIALIZED"
                    if _as_bool(row.get("current_runtime_member"))
                    else "REGISTERED_NOT_CURRENTLY_MATERIALIZED"
                )
            ),
            "authority_ref": str(row.get("authority_ref") or inputs["inventory"]),
            "current_runtime_member": _as_bool(row.get("current_runtime_member")),
            "search_allowed": _as_bool(row.get("search_allowed")),
            "provenance_only": False,
        }
        alias_rows.append(
            {
                "authority_scope": "FIELD_INVENTORY",
                "source_field_id": field_id,
                "canonical_field_id": canonical,
                "alias_type": "CANONICAL_IDENTITY",
                "authority_ref": inputs["inventory"],
            }
        )
        if kind == "DERIVED":
            derived_rows.append(
                {
                    "canonical_field_id": canonical,
                    "field_id": field_id,
                    "dependencies": str(row["base_dependencies"]),
                    "transform": str(row["transform"]),
                    "window_hours": row.get("window_hours"),
                    "materialization": "LAZY_EXISTING_RECIPE",
                    "authority_ref": str(row.get("authority_ref") or ""),
                    "recipe_identity_sha256": _payload_sha(
                        {
                            "dependencies": str(row["base_dependencies"]),
                            "transform": str(row["transform"]),
                            "window_hours": row.get("window_hours"),
                            "scope": str(row.get("scope") or ""),
                        }
                    ),
                }
            )

    provenance_only = set(config.get("provenance_only_fields", ()))
    known_alias_canonicals = {row["canonical_field_id"] for row in alias_rows}
    carrier_rows: list[dict[str, Any]] = []
    search_rows: list[dict[str, Any]] = []
    contracts_by_field: dict[str, list[tuple[str, tuple[Any, ...]]]] = {}
    for carrier_id in sorted(carrier_contracts):
        contracts = tuple(
            FieldContract(
                str(row["field_id"]),
                str(row["value_type"]),
                str(row["unit"]),
                int(row["observable_lag_hours"]),
                str(row["pit_authority"]),
            )
            for row in carrier_contracts[carrier_id]
        )
        surface = field_role_surface(contracts)
        roles_by_field: dict[str, list[str]] = {
            contract.field_id: [] for contract in contracts
        }
        for role, fields in surface["roles"].items():
            for field_id in fields:
                roles_by_field[field_id].append(role)
        for contract in contracts:
            canonical = canonical_by_field.get(
                contract.field_id, f"FIELD:{contract.field_id}"
            )
            if canonical not in catalog_rows:
                catalog_rows[canonical] = {
                    "canonical_field_id": canonical,
                    "field_id": contract.field_id,
                    "record_kind": "BASE_FIELD",
                    "family": "carrier_registered",
                    "source": carrier_id,
                    "value_type": contract.value_type,
                    "unit": contract.unit,
                    "observable_lag_hours": contract.observable_lag_hours,
                    "pit_authority": contract.pit_authority,
                    "lineage_status": "CARRIER_CONTRACT_BOUND",
                    "lineage_source_fields": contract.field_id,
                    "approval_status": "ENGINEERING_CARRIER_ONLY",
                    "ontology_semantic_type": "UNRESOLVED_FROM_CURRENT_AUTHORITIES",
                    "grain": _grain("", carrier_id),
                    "venue": _venue(contract.field_id)
                    or "MULTI_VENUE_OR_UNSPECIFIED",
                    "statistic": _statistic(contract.field_id),
                    "deprecation_status": "CURRENT_OR_UNSPECIFIED",
                    "materialization_status": "CURRENT_RUNTIME_MATERIALIZED",
                    "authority_ref": inputs["carrier_contracts"],
                    "current_runtime_member": True,
                    "search_allowed": contract.field_id not in provenance_only,
                    "provenance_only": contract.field_id in provenance_only,
                }
            else:
                managed = catalog_rows[canonical]
                for key, value in (
                    ("value_type", contract.value_type),
                    ("unit", contract.unit),
                    ("observable_lag_hours", contract.observable_lag_hours),
                    ("pit_authority", contract.pit_authority),
                ):
                    if _text(managed.get(key)) in {
                        "",
                        "UNRESOLVED_FROM_CURRENT_AUTHORITIES",
                    } or (
                        key == "pit_authority"
                        and _text(managed.get(key)).startswith("LINEAGE_LEDGER:")
                    ):
                        managed[key] = value
                managed["grain"] = _grain(managed.get("grain"), carrier_id)
                if managed["materialization_status"] != "LAZY_EXISTING_RECIPE":
                    managed["materialization_status"] = "CURRENT_RUNTIME_MATERIALIZED"
            if contract.field_id in provenance_only:
                catalog_rows[canonical]["provenance_only"] = True
                catalog_rows[canonical]["search_allowed"] = False
            alias_rows.append(
                {
                    "authority_scope": carrier_id,
                    "source_field_id": contract.field_id,
                    "canonical_field_id": canonical,
                    "alias_type": (
                        "SAME_CANONICAL_IDENTITY"
                        if canonical in known_alias_canonicals
                        else "CANONICAL_IDENTITY"
                    ),
                    "authority_ref": inputs["carrier_contracts"],
                }
            )
            known_alias_canonicals.add(canonical)
            carrier_rows.append(
                {
                    "carrier_id": carrier_id,
                    "canonical_field_id": canonical,
                    "field_id": contract.field_id,
                    "value_type": contract.value_type,
                    "unit": contract.unit,
                    "observable_lag_hours": contract.observable_lag_hours,
                    "pit_authority": contract.pit_authority,
                    "runtime_active": True,
                    "boundary": "INDEPENDENT_DATA_PLANE",
                }
            )
            signature = (
                contract.value_type,
                contract.unit,
                contract.observable_lag_hours,
                contract.pit_authority,
            )
            contracts_by_field.setdefault(contract.field_id, []).append(
                (carrier_id, signature)
            )
            if contract.field_id not in provenance_only:
                for role in sorted(roles_by_field[contract.field_id]):
                    search_rows.append(
                        {
                            "carrier_id": carrier_id,
                            "canonical_field_id": canonical,
                            "field_id": contract.field_id,
                            "typed_role": role,
                            "binding_authority": "EXISTING_FIELD_ROLE_SURFACE",
                        }
                    )

    for field_id, bindings in sorted(contracts_by_field.items()):
        for index, label in enumerate(
            ("TYPE", "UNIT", "LAG", "PIT_AUTHORITY")
        ):
            values = {signature[index] for _, signature in bindings}
            if len(values) > 1:
                scoped = label == "PIT_AUTHORITY"
                conflicts.append(
                    {
                        "conflict_type": (
                            "CARRIER_PIT_AUTHORITY_SCOPED_DIFFERENCE"
                            if scoped
                            else f"CARRIER_{label}_DIVERGENCE"
                        ),
                        "canonical_field_id": canonical_by_field.get(
                            field_id, f"FIELD:{field_id}"
                        ),
                        "field_id": field_id,
                        "authorities": ",".join(
                            carrier for carrier, _ in bindings
                        ),
                        "detail": json.dumps(
                            sorted(str(value) for value in values)
                        ),
                        "fatal": not scoped,
                    }
                )

    reachability_rows: list[dict[str, Any]] = []
    for row in reachability.to_dict("records"):
        field_id = str(row["field_id"])
        canonical = canonical_by_field.get(field_id, f"FIELD:{field_id}")
        materialized = _as_bool(row.get("runtime_materialized")) or _as_bool(
            row.get("materialized")
        )
        contracted = _as_bool(row.get("field_contract_registered"))
        role_reachable = _as_bool(row.get("typed_role_reachable"))
        compiler_valid = _as_bool(row.get("compiler_valid"))
        matched_valid = _as_bool(row.get("matched_control_constructible"))
        research_admitted = _as_bool(row.get("research_admitted"))
        declared_reason = _text(row.get("block_reason"))
        if declared_reason:
            first_breakpoint = declared_reason
        elif not materialized:
            first_breakpoint = "MATERIALIZATION_NOT_VERIFIED"
        elif not contracted:
            first_breakpoint = "FIELD_CONTRACT_NOT_REGISTERED"
        elif not role_reachable:
            first_breakpoint = "TYPED_ROLE_NOT_REACHABLE"
        elif not compiler_valid:
            first_breakpoint = "COMPILER_VALIDATION_NOT_VERIFIED"
        elif not matched_valid:
            first_breakpoint = "MATCHED_CONTROL_NOT_CONSTRUCTIBLE"
        elif not research_admitted:
            first_breakpoint = "RESEARCH_ADMISSION_NOT_GRANTED"
        else:
            first_breakpoint = "NONE"
        reachability_rows.append(
            {
                "carrier_id": str(row["surface_id"]),
                "canonical_field_id": canonical,
                "field_id": field_id,
                "schema_observed": _as_bool(row.get("schema_observed")),
                "materialized": materialized,
                "field_contract_registered": contracted,
                "typed_role_reachable": role_reachable,
                "compiler_valid": compiler_valid,
                "matched_control_constructible": matched_valid,
                "deterministic_replay": _as_bool(
                    row.get("deterministic_replay")
                ),
                "research_admitted": research_admitted,
                "first_breakpoint": first_breakpoint,
                "source_block_reason": declared_reason,
            }
        )
    reached_canonicals = {
        row["canonical_field_id"] for row in reachability_rows
    }
    for canonical, managed in catalog_rows.items():
        if canonical in reached_canonicals:
            continue
        reachability_rows.append(
            {
                "carrier_id": "",
                "canonical_field_id": canonical,
                "field_id": managed["field_id"],
                "schema_observed": False,
                "materialized": managed["materialization_status"]
                in {"CURRENT_RUNTIME_MATERIALIZED", "LAZY_EXISTING_RECIPE"},
                "field_contract_registered": False,
                "typed_role_reachable": False,
                "compiler_valid": False,
                "matched_control_constructible": False,
                "deterministic_replay": False,
                "research_admitted": False,
                "first_breakpoint": "NO_CURRENT_CARRIER_BINDING",
                "source_block_reason": "",
            }
        )

    catalog = pd.DataFrame(catalog_rows.values()).sort_values(
        ["record_kind", "canonical_field_id"], kind="stable"
    )
    catalog["observable_lag_hours"] = catalog["observable_lag_hours"].map(_text)
    aliases = pd.DataFrame(alias_rows).drop_duplicates().sort_values(
        ["canonical_field_id", "authority_scope"], kind="stable"
    )
    derived = pd.DataFrame(derived_rows).sort_values(
        "canonical_field_id", kind="stable"
    )
    carrier = pd.DataFrame(carrier_rows).sort_values(
        ["carrier_id", "field_id"], kind="stable"
    )
    search = pd.DataFrame(search_rows).sort_values(
        ["carrier_id", "field_id", "typed_role"], kind="stable"
    )
    reachability_frame = pd.DataFrame(reachability_rows).sort_values(
        ["canonical_field_id", "carrier_id"], kind="stable"
    )
    conflict_frame = pd.DataFrame(
        conflicts,
        columns=[
            "conflict_type",
            "canonical_field_id",
            "field_id",
            "authorities",
            "detail",
            "fatal",
        ],
    )
    if catalog["canonical_field_id"].duplicated().any():
        raise ValueError("canonical field identities are not unique")
    if not conflict_frame.empty and conflict_frame["fatal"].any():
        raise ValueError(
            "conflicting field authorities: "
            + ",".join(conflict_frame["field_id"].astype(str))
        )
    return {
        "unified_field_catalog": catalog.reset_index(drop=True),
        "field_alias_map": aliases.reset_index(drop=True),
        "derived_view_catalog": derived.reset_index(drop=True),
        "carrier_field_matrix": carrier.reset_index(drop=True),
        "search_role_binding": search.reset_index(drop=True),
        "field_reachability_matrix": reachability_frame.reset_index(drop=True),
        "field_authority_conflicts": conflict_frame.reset_index(drop=True),
    }


def build_management_view(
    repo_root: Path,
    config: Mapping[str, Any],
    *,
    source_sha: str | None = None,
) -> dict[str, Any]:
    """Write the compiled management view and a content-bound run manifest."""

    output_root = repo_root / config["outputs"]["runtime_root"]
    output_root.mkdir(parents=True, exist_ok=True)
    actual_sha = _git_sha(repo_root)
    if source_sha is not None and source_sha != actual_sha:
        raise ValueError(
            f"source SHA mismatch: requested {source_sha}, current {actual_sha}"
        )
    tables = compile_management_tables(repo_root, config)
    output_files: dict[str, str] = {}
    for name, frame in tables.items():
        path = output_root / f"{name}.parquet"
        frame.to_parquet(path, index=False)
        output_files[path.name] = sha256_file(path)

    summary = {
        "schema_version": 1,
        "status": "PASS_COMPILED_VIEW_NOT_AUTHORITY",
        "canonical_field_count": len(tables["unified_field_catalog"]),
        "base_field_count": int(
            (tables["unified_field_catalog"]["record_kind"] == "BASE_FIELD").sum()
        ),
        "derived_view_count": len(tables["derived_view_catalog"]),
        "carrier_binding_count": len(tables["carrier_field_matrix"]),
        "carrier_counts": tables["carrier_field_matrix"]
        .groupby("carrier_id")
        .size()
        .sort_index()
        .to_dict(),
        "search_role_binding_count": len(tables["search_role_binding"]),
        "provenance_only_count": int(
            tables["unified_field_catalog"]["provenance_only"].sum()
        ),
        "authority_conflict_count": len(tables["field_authority_conflicts"]),
        "reachability_row_count": len(tables["field_reachability_matrix"]),
        "first_breakpoint_counts": tables["field_reachability_matrix"]
        .groupby("first_breakpoint")
        .size()
        .sort_index()
        .to_dict(),
        "contexts_merged": False,
        "creates_ontology": False,
        "creates_approval_authority": False,
        "changes_candidate_identity": False,
        "market_search_executed": False,
    }
    summary_path = output_root / "field_management_summary.json"
    _write_json(summary_path, summary)
    output_files[summary_path.name] = sha256_file(summary_path)

    input_files = {
        key: sha256_file(repo_root / value)
        for key, value in config["inputs"].items()
        if key != "field_information_config"
    }
    input_files["field_information_config"] = sha256_file(
        repo_root / config["inputs"]["field_information_config"]
    )
    production_files = {
        path: sha256_file(repo_root / path)
        for path in config["production_paths"]
    }
    manifest = {
        "schema_version": 1,
        "source_sha": actual_sha,
        "production_code_sha256": dict(sorted(production_files.items())),
        "production_code_bundle_sha256": _payload_sha(production_files),
        "config_identity_sha256": _payload_sha(config),
        "input_sha256": dict(sorted(input_files.items())),
        "output_sha256": dict(sorted(output_files.items())),
        "summary": summary,
        "boundaries": config["boundaries"],
    }
    manifest_path = output_root / "run_manifest.json"
    _write_json(manifest_path, manifest)
    return manifest


__all__ = [
    "build_management_view",
    "compile_management_tables",
]
