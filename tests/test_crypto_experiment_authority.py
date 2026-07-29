from __future__ import annotations

import json
from pathlib import Path

import pytest

from alphafactory_crypto.broad_search.experiment_authority import (
    REQUIRED_REAL_EXPERIMENT_ROLES,
    require_real_experiment_authority,
    resolve_real_experiment_authorities,
)


def _write_current(
    repo_root: Path,
    *,
    inactive_roles: tuple[str, ...] = (),
    non_formal_roles: tuple[str, ...] = (),
) -> None:
    graph_root = repo_root / ".planning" / "graphs"
    graph_root.mkdir(parents=True)
    nodes = []
    bindings = []
    for role in REQUIRED_REAL_EXPERIMENT_ROLES:
        component = f"{role}_component"
        nodes.append(
            {
                "id": component,
                "lifecycle": "ACTIVE",
                "active_authority": role not in inactive_roles,
                "validation": {"result": "PASS"},
            }
        )
        bindings.append(
            {
                "semantic_role": role,
                "authoritative_component": component,
                "authority_class": (
                    "NON_FORMAL" if role in non_formal_roles else "FORMAL"
                ),
            }
        )
    (graph_root / "current.json").write_text(
        json.dumps({"nodes": nodes, "semantic_authorities": bindings}),
        encoding="utf-8",
    )


def test_active_non_formal_authority_is_visible_but_not_formal(tmp_path: Path) -> None:
    _write_current(tmp_path, non_formal_roles=("optimizer_reward",))

    result = require_real_experiment_authority(
        tmp_path,
        evidence_to_add="compare a frozen development mechanism",
        decision_to_change="keep or close that mechanism",
    )

    assert result["result"] == "READY_WITH_NON_FORMAL_BOUNDARIES"
    assert result["formal_claims_authorized"] is False
    assert (
        result["authority_refs"]["optimizer_reward"]["status"]
        == "FOUND_BUT_UNQUALIFIED"
    )


def test_inactive_bound_component_fails_closed(tmp_path: Path) -> None:
    _write_current(tmp_path, inactive_roles=("target",))

    with pytest.raises(
        RuntimeError,
        match="REAL_EXPERIMENT_AUTHORITY_BLOCKED: target:INACTIVE_AUTHORITY",
    ):
        require_real_experiment_authority(
            tmp_path,
            evidence_to_add="compare a frozen development mechanism",
            decision_to_change="keep or close that mechanism",
        )


def test_missing_information_intent_fails_closed(tmp_path: Path) -> None:
    _write_current(tmp_path)

    with pytest.raises(RuntimeError, match="evidence_to_add:MISSING"):
        require_real_experiment_authority(
            tmp_path,
            evidence_to_add="TBD",
            decision_to_change="keep or close that mechanism",
        )


def test_committed_current_blocks_inactive_search_economic_roles() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    resolution = resolve_real_experiment_authorities(repo_root)

    assert set(resolution["blockers"]) == {
        "target:INACTIVE_AUTHORITY",
        "optimizer_reward:INACTIVE_AUTHORITY",
        "execution_price:INACTIVE_AUTHORITY",
        "cost:INACTIVE_AUTHORITY",
    }
    current = json.loads(
        (repo_root / ".planning" / "graphs" / "current.json").read_text(
            encoding="utf-8-sig"
        )
    )
    semantic_roles = {
        str(binding.get("semantic_role"))
        for binding in current.get("semantic_authorities", [])
    }
    assert "adaptive_feedback_authority" not in semantic_roles
    assert "capability_strict_feedback_authority" in semantic_roles
