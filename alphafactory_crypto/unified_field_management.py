"""Deterministic management view over existing crypto field authorities.

The compiled tables in this module are navigation and consistency artifacts.
They do not replace the inventory, ontology, approval, lineage, carrier,
typed-compiler, or materializer authorities from which they are built.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from alphafactory_crypto.broad_search.compositional18m import field_role_surface
from alphafactory_crypto.broad_search.expression import FieldContract
from alphafactory_crypto.field_information import compile_token_catalog, sha256_file


@dataclass(frozen=True, slots=True)
class CarrierSpec:
    carrier_id: str
    authority_ref: str
    boundary: str = "INDEPENDENT_DATA_PLANE"


@dataclass(frozen=True, slots=True)
class BaseFieldSpec:
    canonical_field_id: str
    field_id: str
    authority_ref: str


@dataclass(frozen=True, slots=True)
class DerivedViewSpec:
    canonical_field_id: str
    field_id: str
    dependencies: str
    transform: str
    window_hours: int | None
    authority_ref: str


@dataclass(frozen=True, slots=True)
class SearchRoleBinding:
    carrier_id: str
    canonical_field_id: str
    field_id: str
    typed_role: str


@dataclass(frozen=True, slots=True)
class ProvenanceOnlySpec:
    canonical_field_id: str
    field_id: str
    reason: str


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

    catalog_rows: dict[str, dict[str, Any]] = {}
    canonical_by_field: dict[str, str] = {}
    alias_rows: list[dict[str, Any]] = []
    derived_rows: list[dict[str, Any]] = []
    for row in token_catalog.to_dict("records"):
        field_id = str(row["field_id"])
        canonical = str(row["token_id"])
        canonical_by_field[field_id] = canonical
        kind = str(row["token_kind"])
        catalog_rows[canonical] = {
            "canonical_field_id": canonical,
            "field_id": field_id,
            "record_kind": "DERIVED_VIEW" if kind == "DERIVED" else "BASE_FIELD",
            "family": str(row.get("family") or "unknown"),
            "source": str(row.get("source") or ""),
            "observable_lag": str(row.get("observable_lag") or ""),
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
                    "observable_lag": str(contract.observable_lag_hours),
                    "authority_ref": inputs["carrier_contracts"],
                    "current_runtime_member": True,
                    "search_allowed": contract.field_id not in provenance_only,
                    "provenance_only": contract.field_id in provenance_only,
                }
            elif contract.field_id in provenance_only:
                catalog_rows[canonical]["provenance_only"] = True
                catalog_rows[canonical]["search_allowed"] = False
            alias_rows.append(
                {
                    "authority_scope": carrier_id,
                    "source_field_id": contract.field_id,
                    "canonical_field_id": canonical,
                    "alias_type": (
                        "EXACT_EQUIVALENT"
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
        signatures = {signature for _, signature in bindings}
        if len(signatures) > 1:
            conflicts.append(
                {
                    "conflict_type": "CARRIER_CONTRACT_DIVERGENCE",
                    "canonical_field_id": f"FIELD:{field_id}",
                    "field_id": field_id,
                    "authorities": ",".join(carrier for carrier, _ in bindings),
                    "detail": json.dumps(bindings, sort_keys=True),
                    "fatal": True,
                }
            )

    catalog = pd.DataFrame(catalog_rows.values()).sort_values(
        ["record_kind", "canonical_field_id"], kind="stable"
    )
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
        "field_authority_conflicts": conflict_frame.reset_index(drop=True),
    }


def build_management_view(
    repo_root: Path, config: Mapping[str, Any]
) -> dict[str, Any]:
    """Write the compiled management view and a content-bound run manifest."""

    output_root = repo_root / config["outputs"]["runtime_root"]
    output_root.mkdir(parents=True, exist_ok=True)
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
    manifest = {
        "schema_version": 1,
        "source_sha": _git_sha(repo_root),
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
    "BaseFieldSpec",
    "CarrierSpec",
    "DerivedViewSpec",
    "ProvenanceOnlySpec",
    "SearchRoleBinding",
    "build_management_view",
    "compile_management_tables",
]
