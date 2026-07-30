"""Fail-closed authority resolution for real Search Engine experiments."""

from __future__ import annotations

import ast
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from alphafactory_crypto.instrument_capability.mapping import (
    DEFAULT_MAPPING_CONTRACTS,
)
from alphafactory_crypto.instrument_canary.grammar import MECHANISM_MAPPING


REQUIRED_REAL_EXPERIMENT_ROLES = (
    "target",
    "optimizer_reward",
    "execution_price",
    "portfolio_mapping",
    "cost",
    "validation_role",
    "promotion_gate",
)
DEFAULT_SEARCH_ECONOMIC_RECEIPT_PATH = (
    "config/crypto_search_economic_receipt_v1.json"
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


def _canonical_sha256(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest().upper()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _symbol_is_declared(source_path: Path, dotted_symbol: str) -> bool:
    symbol = str(dotted_symbol).rsplit(".", 1)[-1]
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == symbol:
                return True
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == symbol for target in targets):
                return True
    return False


def _parse_utc(value: Any, field: str, blockers: list[str]) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        blockers.append(field)
        return None
    if parsed.utcoffset() is None:
        blockers.append(field)
        return None
    return parsed


def evaluate_search_validation_kill_line(
    metrics: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply the frozen development-validation stop rule without reading data.

    The caller owns metric production and checkpoint persistence.  This gate
    consumes one already-evaluated validation row, returns a deterministic
    decision, and has no optimizer, archive, proposal, or holdout side effect.
    """

    required = {
        "validation_net_mean_positive": bool(
            float(metrics.get("validation_net_mean", float("nan"))) > 0.0
        ),
        "validation_nonoverlap_floor_sortino_positive": bool(
            float(
                metrics.get(
                    "validation_nonoverlap_floor_sortino",
                    float("nan"),
                )
            )
            > 0.0
        ),
        "validation_matched_increment_positive": bool(
            float(
                metrics.get(
                    "validation_matched_increment",
                    float("nan"),
                )
            )
            > 0.0
        ),
        "validation_control_not_dominant": (
            metrics.get("validation_control_not_dominant") is True
        ),
    }
    passed = all(required.values())
    return {
        "result": (
            "PASS_CONTINUE_FROZEN_ARM"
            if passed
            else "FAIL_STOP_ARM_AND_WRITE_CHECKPOINT"
        ),
        "passed": passed,
        "conditions": required,
        "optimizer_feedback_written": False,
        "policy_memory_written": False,
        "candidate_generation_performed": False,
        "holdout_read": False,
    }


def _validate_search_economic_receipt(
    repo_root: Path,
    receipt: Mapping[str, Any],
    *,
    receipt_path_label: str,
) -> dict[str, Any]:
    """Validate one receipt payload; it never grants run authority."""

    receipt = dict(receipt)
    blockers: list[str] = []

    if receipt.get("schema_version") != 1:
        blockers.append("schema_version")
    if receipt.get("receipt_id") != "CRYPTO_SEARCH_ECONOMIC_RECEIPT_V1":
        blockers.append("receipt_id")
    if receipt.get("status") != "SOURCE_QUALIFIED_NOT_RUN_AUTHORIZED":
        blockers.append("status")
    if receipt.get("run_authorized") is not False:
        blockers.append("run_authorized")
    market = dict(receipt.get("market") or {})
    if market != {"asset_class": "CRYPTO", "calendar": "CONTINUOUS_UTC"}:
        blockers.append("market")

    mechanism = dict(receipt.get("mechanism") or {})
    direction = dict(receipt.get("direction") or {})
    portfolio = dict(receipt.get("portfolio") or {})
    execution = dict(receipt.get("execution") or {})
    cost = dict(receipt.get("cost") or {})
    optimizer_reward = dict(receipt.get("optimizer_reward") or {})
    partitions = dict(receipt.get("evidence_partition") or {})
    validation = dict(partitions.get("validation") or {})
    holdout = dict(partitions.get("holdout") or {})
    kill_line = dict(receipt.get("validation_kill_line") or {})
    boundaries = dict(receipt.get("boundaries") or {})
    component_sources = dict(receipt.get("component_sources") or {})

    expected_mechanism = (
        "alphafactory_crypto.broad_search.compositional18m.skeleton_registry"
    )
    expected_mapping = (
        "alphafactory_crypto.instrument_canary.grammar.MECHANISM_MAPPING"
    )
    expected_direction = (
        "scripts.crypto_a7reward1_portfolio_reward_model.select_train_orientation"
    )
    expected_validation = (
        "alphafactory_crypto.broad_search.experiment_authority."
        "evaluate_search_validation_kill_line"
    )
    expected_target_store = (
        "alphafactory_crypto.broad_search.replay_v14_binance_target."
        "BinanceTargetStore"
    )
    expected_reward = (
        "alphafactory_crypto.broad_search.pair18m.SEARCH_REWARD_AUTHORITY"
    )
    if mechanism.get("registry_symbol") != expected_mechanism:
        blockers.append("mechanism.registry_symbol")
    if mechanism.get("economic_hypothesis_field") != "financial_hypothesis":
        blockers.append("mechanism.economic_hypothesis_field")
    if mechanism.get("mapping_authority_symbol") != expected_mapping:
        blockers.append("mechanism.mapping_authority_symbol")
    if mechanism.get("mapping_class") != "CROSS_SECTIONAL_RELATIVE":
        blockers.append("mechanism.mapping_class")
    elif (
        MECHANISM_MAPPING.get(str(mechanism.get("mapping_class")))
        != portfolio.get("mapping_id")
    ):
        blockers.append("mechanism.mapping_resolution")
    if direction.get("rule") != "TRAIN_FROZEN_SIGN_ORIENTATION":
        blockers.append("direction.rule")
    if direction.get("authority_symbol") != expected_direction:
        blockers.append("direction.authority_symbol")
    if direction.get("fit_role") != "FRESH_DEVELOPMENT_TRAIN_ONLY":
        blockers.append("direction.fit_role")
    if direction.get("allowed_values") != [-1, 1]:
        blockers.append("direction.allowed_values")
    if direction.get("persist_in_candidate_ledger") is not True:
        blockers.append("direction.persist_in_candidate_ledger")
    if portfolio.get("mapping_authority_component") != "explicit_portfolio_mapping":
        blockers.append("portfolio.mapping_authority_component")
    mapping_id = str(portfolio.get("mapping_id") or "")
    mapping_contract = DEFAULT_MAPPING_CONTRACTS.get(mapping_id)
    if mapping_contract is None:
        blockers.append("portfolio.mapping_id")
    if portfolio.get("shared_support_execution_horizon_cost") is not True:
        blockers.append("portfolio.shared_support_execution_horizon_cost")

    target_config_path = repo_root / str(execution.get("authority_config") or "")
    target_config: dict[str, Any] = {}
    if not target_config_path.is_file():
        blockers.append("execution.authority_config")
    else:
        target_config = json.loads(
            target_config_path.read_text(encoding="utf-8-sig")
        )
    target = dict(target_config.get("target") or {})
    target_fields = (
        "venue",
        "source",
        "price_field",
        "formula",
        "execution_delay_hours",
        "horizons_hours",
        "positive_price_required",
        "missing_value_fill",
    )
    for field in target_fields:
        if execution.get(field) != target.get(field):
            blockers.append(f"execution.{field}")
    if execution.get("target_store_symbol") != expected_target_store:
        blockers.append("execution.target_store_symbol")
    if execution.get("venue") != "BINANCE_USD_M":
        blockers.append("execution.venue")
    if execution.get("instrument_type") != "LINEAR_PERPETUAL":
        blockers.append("execution.instrument_type")

    if mapping_contract is not None:
        mapping_cost = dict(mapping_contract.cost_model)
        expected_cost = {
            "model_id": mapping_cost.get("id"),
            "cost_bps": float(mapping_cost.get("cost_bps")),
            "initial_establishment_charged": mapping_cost.get(
                "initial_establishment_charged"
            ),
        }
        observed_cost = {
            "model_id": cost.get("model_id"),
            "cost_bps": float(cost.get("cost_bps", float("nan"))),
            "initial_establishment_charged": cost.get(
                "initial_establishment_charged"
            ),
        }
        if observed_cost != expected_cost:
            blockers.append("cost.mapping_contract")
    else:
        observed_cost = {}
    if cost.get("authority_component") != "real_data_mapping_cost_evaluator":
        blockers.append("cost.authority_component")
    if cost.get("mapping_id") != mapping_id:
        blockers.append("cost.mapping_id")
    if cost.get("venue") != execution.get("venue"):
        blockers.append("cost.venue")
    if cost.get("instrument_type") != execution.get("instrument_type"):
        blockers.append("cost.instrument_type")
    if cost.get("qualification") != "FROZEN_VENUE_ASSUMPTION_NON_FORMAL":
        blockers.append("cost.qualification")

    from alphafactory_crypto.broad_search.pair18m import SEARCH_REWARD_AUTHORITY

    if optimizer_reward.get("authority_symbol") != expected_reward:
        blockers.append("optimizer_reward.authority_symbol")
    if optimizer_reward.get("authority_id") != SEARCH_REWARD_AUTHORITY:
        blockers.append("optimizer_reward.authority_id")
    if optimizer_reward.get("feedback_role") != "FRESH_DEVELOPMENT_TRAIN_ONLY":
        blockers.append("optimizer_reward.feedback_role")
    if (
        optimizer_reward.get("pair_reward_role")
        != "MATCHED_ATTRIBUTION_DIAGNOSTIC_ONLY"
    ):
        blockers.append("optimizer_reward.pair_reward_role")

    train = dict(partitions.get("train") or {})
    train_start = _parse_utc(
        train.get("start"), "evidence_partition.train.start", blockers
    )
    train_end = _parse_utc(
        train.get("end_exclusive"),
        "evidence_partition.train.end_exclusive",
        blockers,
    )
    validation_start = _parse_utc(
        validation.get("start"),
        "evidence_partition.validation.start",
        blockers,
    )
    validation_end = _parse_utc(
        validation.get("end_exclusive"),
        "evidence_partition.validation.end_exclusive",
        blockers,
    )
    holdout_start = _parse_utc(
        holdout.get("start"), "evidence_partition.holdout.start", blockers
    )
    holdout_end = _parse_utc(
        holdout.get("end_exclusive"),
        "evidence_partition.holdout.end_exclusive",
        blockers,
    )
    if all(
        value is not None
        for value in (
            train_start,
            train_end,
            validation_start,
            validation_end,
            holdout_start,
            holdout_end,
        )
    ) and not (
        train_start
        < train_end
        == validation_start
        < validation_end
        == holdout_start
        < holdout_end
    ):
        blockers.append("evidence_partition.order")
    if train.get("optimizer_feedback_allowed") is not True:
        blockers.append("evidence_partition.train.optimizer_feedback_allowed")
    for field in (
        "optimizer_feedback_allowed",
        "policy_memory_write_allowed",
        "candidate_generation_allowed",
    ):
        if validation.get(field) is not False:
            blockers.append(f"evidence_partition.validation.{field}")
    for field in (
        "read_allowed",
        "optimizer_feedback_allowed",
        "policy_memory_write_allowed",
    ):
        if holdout.get(field) is not False:
            blockers.append(f"evidence_partition.holdout.{field}")
    if kill_line.get("authority_symbol") != expected_validation:
        blockers.append("validation_kill_line.authority_symbol")
    if kill_line.get("equal_matched_evaluated_count") is not True:
        blockers.append("validation_kill_line.equal_matched_evaluated_count")
    if kill_line.get("threshold_tuning_allowed") is not False:
        blockers.append("validation_kill_line.threshold_tuning_allowed")
    if kill_line.get("failure_action") != "STOP_ARM_AND_WRITE_CHECKPOINT":
        blockers.append("validation_kill_line.failure_action")

    for field in (
        "oos",
        "challenge",
        "recent",
        "may_stress",
        "forward",
        "promotion",
        "cross_sprint_adaptive_memory",
        "a_share_constraints_applied",
    ):
        if boundaries.get(field) is not False:
            blockers.append(f"boundaries.{field}")
    if boundaries.get("development_only") is not True:
        blockers.append("boundaries.development_only")
    if boundaries.get("sealed_reads") != 0:
        blockers.append("boundaries.sealed_reads")

    source_symbols = {
        "mechanism": mechanism.get("registry_symbol"),
        "mechanism_mapping": mechanism.get("mapping_authority_symbol"),
        "direction": direction.get("authority_symbol"),
        "validation_kill_line": kill_line.get("authority_symbol"),
        "target_execution": execution.get("target_store_symbol"),
        "optimizer_reward_and_matched_attribution": optimizer_reward.get(
            "authority_symbol"
        ),
    }
    component_sha256: dict[str, str] = {}
    for component, source_binding in component_sources.items():
        if not isinstance(source_binding, Mapping):
            blockers.append(f"component_sources.{component}")
            continue
        source_path = repo_root / str(source_binding.get("path") or "")
        expected_sha256 = str(source_binding.get("sha256") or "").upper()
        if not source_path.is_file():
            blockers.append(f"component_sources.{component}")
            continue
        observed_sha256 = _file_sha256(source_path)
        component_sha256[str(component)] = observed_sha256
        if observed_sha256 != expected_sha256:
            blockers.append(f"component_hash.{component}")
        symbol = source_symbols.get(str(component))
        if symbol and not _symbol_is_declared(source_path, str(symbol)):
            blockers.append(f"component_symbol.{component}")

    if blockers:
        raise RuntimeError(
            "SEARCH_ECONOMIC_RECEIPT_BLOCKED: "
            + "; ".join(sorted(set(blockers)))
        )
    return {
        "result": str(receipt["status"]),
        "receipt_path": receipt_path_label,
        "receipt_sha256": _canonical_sha256(receipt),
        "component_sha256": component_sha256,
        "market": market,
        "mechanism": mechanism,
        "direction": direction,
        "portfolio": portfolio,
        "execution": execution,
        "cost": observed_cost,
        "optimizer_reward": optimizer_reward,
        "train": train,
        "validation": validation,
        "holdout": holdout,
        "validation_kill_line": kill_line,
        "run_authorized": False,
        "formal_claims_authorized": False,
    }


def resolve_search_economic_receipt(
    repo_root: Path,
) -> dict[str, Any]:
    """Verify the thin crypto campaign binding without reimplementing its authorities."""

    relative_receipt = DEFAULT_SEARCH_ECONOMIC_RECEIPT_PATH
    path = repo_root / relative_receipt
    if not path.is_file():
        raise RuntimeError(
            f"SEARCH_ECONOMIC_RECEIPT_BLOCKED: receipt:MISSING:{path}"
        )
    receipt = json.loads(path.read_text(encoding="utf-8-sig"))
    return _validate_search_economic_receipt(
        repo_root,
        receipt,
        receipt_path_label=relative_receipt,
    )


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
    economic_receipt_required: bool = True,
) -> dict[str, Any]:
    resolution = resolve_real_experiment_authorities(repo_root)
    blockers = list(resolution["blockers"])
    economic_receipt = None
    if economic_receipt_required:
        economic_receipt = resolve_search_economic_receipt(repo_root)
        if economic_receipt["run_authorized"] is not True:
            blockers.append("economic_receipt:RUN_NOT_AUTHORIZED")
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
        "economic_receipt": economic_receipt,
    }


__all__ = [
    "DEFAULT_SEARCH_ECONOMIC_RECEIPT_PATH",
    "REQUIRED_REAL_EXPERIMENT_ROLES",
    "evaluate_search_validation_kill_line",
    "require_real_experiment_authority",
    "resolve_real_experiment_authorities",
    "resolve_search_economic_receipt",
]
