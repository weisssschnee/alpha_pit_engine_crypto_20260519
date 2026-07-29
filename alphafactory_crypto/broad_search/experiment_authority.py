"""Fail-closed authority resolution for real Search Engine experiments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_REAL_EXPERIMENT_ROLES = (
    "target",
    "optimizer_reward",
    "execution_price",
    "portfolio_mapping",
    "cost",
    "validation_role",
    "promotion_gate",
)

_INVALID_INTENT = {
    "",
    "n/a",
    "na",
    "none",
    "tbd",
    "todo",
    "unknown",
    "\u5f85\u5b9a",
    "\u672a\u77e5",
}


def _node_id(node: dict[str, Any]) -> str:
    return str(node.get("id") or node.get("node_id") or node.get("key") or "")


def _meaningful(value: str | None) -> bool:
    return str(value or "").strip().casefold() not in _INVALID_INTENT


def resolve_real_experiment_authorities(repo_root: Path) -> dict[str, Any]:
    current_path = repo_root / ".planning" / "graphs" / "current.json"
    if not current_path.is_file():
        raise RuntimeError(f"REAL_EXPERIMENT_AUTHORITY_BLOCKED: CURRENT missing: {current_path}")
    current = json.loads(current_path.read_text(encoding="utf-8-sig"))
    nodes = {
        _node_id(node): node
        for node in (current.get("nodes") or current.get("components") or [])
        if isinstance(node, dict) and _node_id(node)
    }
    bindings_by_role: dict[str, list[dict[str, Any]]] = {}
    for binding in current.get("semantic_authorities") or []:
        if isinstance(binding, dict):
            role = str(binding.get("semantic_role") or "")
            bindings_by_role.setdefault(role, []).append(binding)

    authority_refs: dict[str, dict[str, Any]] = {}
    blockers: list[str] = []
    non_formal: list[str] = []
    for role in REQUIRED_REAL_EXPERIMENT_ROLES:
        bindings = bindings_by_role.get(role, [])
        if not bindings:
            authority_refs[role] = {"status": "VACANT"}
            blockers.append(f"{role}:VACANT")
            continue
        if len(bindings) != 1:
            authority_refs[role] = {
                "status": "MULTIPLE_CONFLICTING_AUTHORITIES",
                "components": ",".join(
                    sorted(
                        str(item.get("authoritative_component") or "")
                        for item in bindings
                    )
                ),
            }
            blockers.append(f"{role}:MULTIPLE_CONFLICTING_AUTHORITIES")
            continue

        binding = bindings[0]
        component = str(binding.get("authoritative_component") or "")
        authority_class = str(binding.get("authority_class") or "UNCLASSIFIED").upper()
        node = nodes.get(component)
        lifecycle = str((node or {}).get("lifecycle") or (node or {}).get("status") or "")
        active_authority = (node or {}).get("active_authority")
        validation = (node or {}).get("validation")
        validation_result = (
            str(validation.get("result") or "").upper()
            if isinstance(validation, dict)
            else ""
        )
        if not node:
            status = "STALE"
        elif lifecycle.upper() in {"DEPRECATED", "REMOVED", "SUPERSEDED"}:
            status = "STALE"
        elif validation_result in {"FAIL", "FAILED", "ERROR", "STALE"}:
            status = "STALE"
        elif active_authority is not True:
            status = "INACTIVE_AUTHORITY"
        elif authority_class == "FORMAL":
            status = "RESOLVED"
        elif authority_class == "NON_FORMAL":
            status = "FOUND_BUT_UNQUALIFIED"
            non_formal.append(role)
        else:
            status = "FOUND_BUT_UNQUALIFIED"

        authority_refs[role] = {
            "status": status,
            "component": component,
            "authority_class": authority_class,
            "lifecycle": lifecycle,
            "active_authority": active_authority,
        }
        if (
            status in {"STALE", "INACTIVE_AUTHORITY"}
            or authority_class not in {"FORMAL", "NON_FORMAL"}
        ):
            blockers.append(f"{role}:{status}")

    return {
        "authority_refs": authority_refs,
        "blockers": blockers,
        "non_formal_roles": non_formal,
    }


def require_real_experiment_authority(
    repo_root: Path,
    *,
    evidence_to_add: str | None,
    decision_to_change: str | None,
) -> dict[str, Any]:
    resolution = resolve_real_experiment_authorities(repo_root)
    blockers = list(resolution["blockers"])
    if not _meaningful(evidence_to_add):
        blockers.append("evidence_to_add:MISSING")
    if not _meaningful(decision_to_change):
        blockers.append("decision_to_change:MISSING")
    if blockers:
        raise RuntimeError(
            "REAL_EXPERIMENT_AUTHORITY_BLOCKED: " + "; ".join(blockers)
        )
    return {
        "result": (
            "READY_WITH_NON_FORMAL_BOUNDARIES"
            if resolution["non_formal_roles"]
            else "READY"
        ),
        "authority_refs": resolution["authority_refs"],
        "evidence_to_add": str(evidence_to_add).strip(),
        "decision_to_change": str(decision_to_change).strip(),
        "formal_claims_authorized": not bool(resolution["non_formal_roles"]),
    }


__all__ = [
    "REQUIRED_REAL_EXPERIMENT_ROLES",
    "require_real_experiment_authority",
    "resolve_real_experiment_authorities",
]
