from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.identity_registry import (
    canonical_identity,
    economic_hypothesis_assignment,
    exact_signal_identity,
    pnl_regime_diagnostic_identity,
    syntax_identity,
)


ACCEPTED = REPO / "runtime" / "a7eff2_git_release_20260711" / "a7eff2_accepted_train_validation_oos_log.csv"
RELEASE = REPO / "runtime" / "a7eff2_git_release_20260711" / "a7eff2_release_manifest.json"
BURN_LEDGER = REPO / "runtime" / "a7evalreset0_evaluation_governance_20260711" / "a7evalreset0_oos_burn_ledger.csv"
HYPOTHESES = REPO / "config" / "crypto_b0p_economic_hypothesis_registry_v1.json"
RUNTIME = REPO / "runtime" / "a7b0p_identity_qualification_20260711"
REPORT = REPO / "reports" / "CRYPTO_B0P_LAYERED_IDENTITY_QUALIFICATION_20260711.md"


METRIC_COLUMNS = {
    "validation": "validation_sortino",
    "test": "test_sortino",
    "recent": "recent_sortino",
    "stress": "stress_sortino",
}
BLOCK_TO_EPOCH_PREFIX = {
    "validation": "validation_",
    "test": "test_",
    "recent": "recent_",
    "stress": "known_may",
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build() -> dict[str, object]:
    accepted = _read_csv(ACCEPTED)
    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    burn_rows = _read_csv(BURN_LEDGER)
    hypothesis_config = json.loads(HYPOTHESES.read_text(encoding="utf-8"))
    definitions = {row["hypothesis_id"]: row for row in hypothesis_config["hypotheses"]}
    assignments = {row["signal_weight_exact_fingerprint"]: row["hypothesis_id"] for row in hypothesis_config["assignments"]}

    block_roles: dict[str, str] = {}
    for block, prefix in BLOCK_TO_EPOCH_PREFIX.items():
        matches = [row for row in burn_rows if row["epoch_id"].startswith(prefix)]
        if len(matches) != 1 or matches[0]["candidate_feedback_allowed"].lower() != "false":
            raise RuntimeError(f"spent diagnostic block is not uniquely governed: {block}")
        block_roles[block] = matches[0]["current_classification"]

    listed_paths = [str(row.get("path", "")) for row in release.get("canonical_sources", [])]
    listed_paths.extend(str(path) for path in release.get("outputs", {}))
    listed_paths.extend(str(row.get("path", "")) for row in release.get("source_evidence", []))
    activation_artifacts = [path for path in listed_paths if "activation" in path.lower() or "signal_mask" in path.lower()]
    activation_artifact_available = bool(activation_artifacts) and bool(release["boundaries"].get("contains_full_numeric_cache"))
    activation_status = (
        "ESTABLISHED_FROM_FROZEN_SIGNAL_BEHAVIOR"
        if activation_artifact_available
        else "NOT_QUALIFIED_MISSING_FROZEN_SIGNAL_BEHAVIOR_ARTIFACT"
    )

    registry_rows: list[dict[str, object]] = []
    for row in accepted:
        fingerprint = row["signal_weight_exact_fingerprint"]
        hypothesis_id = assignments.get(fingerprint)
        if not hypothesis_id or hypothesis_id not in definitions:
            raise RuntimeError(f"missing semantic hypothesis assignment for exact signal {fingerprint}")
        definition = definitions[hypothesis_id]
        hypothesis = economic_hypothesis_assignment(
            hypothesis_id,
            expression=row["expression"],
            required_fields=definition["required_fields"],
            required_operators=definition["required_operators"],
            mechanism=definition["mechanism"],
            provenance="config/crypto_b0p_economic_hypothesis_registry_v1.json",
        )
        pnl_regime = pnl_regime_diagnostic_identity(
            {block: float(row[column]) for block, column in METRIC_COLUMNS.items()}, block_roles
        )
        pnl_pattern = pnl_regime.provenance.rsplit(";", 1)[-1]
        registry_rows.append(
            {
                "blueprint_id": row["blueprint_id"],
                "syntax_identity": syntax_identity(row["expression"]),
                "canonical_identity": canonical_identity(row["expression"]),
                "exact_signal_identity": exact_signal_identity(fingerprint),
                "activation_identity": "",
                "activation_status": activation_status,
                "activation_cluster_identity": "",
                "activation_cluster_status": activation_status,
                "pnl_regime_identity": pnl_regime.identity_id,
                "pnl_regime_pattern": pnl_pattern,
                "pnl_regime_status": pnl_regime.status,
                "economic_hypothesis_identity": hypothesis.identity_id,
                "economic_hypothesis_label": definition["label"],
                "economic_hypothesis_status": hypothesis.status,
                "semantic_pair_observation": row["semantic_pair"],
                "feedback_permission": "DIAGNOSTIC_ONLY_NO_PROMOTION_MEMORY_SCHEDULER_OR_GENERATOR_FEEDBACK",
            }
        )

    pnl_counts = Counter(str(row["pnl_regime_identity"]) for row in registry_rows)
    pnl_rows = [
        {
            "pnl_regime_identity": identity,
            "pnl_regime_pattern": next(row["pnl_regime_pattern"] for row in registry_rows if row["pnl_regime_identity"] == identity),
            "accepted_rows": count,
            "feedback_permission": "DIAGNOSTIC_ONLY",
        }
        for identity, count in sorted(pnl_counts.items())
    ]
    hypothesis_rows = [
        {
            "hypothesis_id": definition["hypothesis_id"],
            "label": definition["label"],
            "required_fields": "|".join(definition["required_fields"]),
            "required_operators": "|".join(definition["required_operators"]),
            "mechanism": definition["mechanism"],
            "exact_signal_count": len({
                row["exact_signal_identity"]
                for row in registry_rows
                if row["economic_hypothesis_identity"] == definition["hypothesis_id"]
            }),
            "accepted_row_count": sum(
                row["economic_hypothesis_identity"] == definition["hypothesis_id"] for row in registry_rows
            ),
            "derivation_uses_performance": False,
        }
        for definition in hypothesis_config["hypotheses"]
    ]

    counts = {
        "alias_expanded_blueprints": int(release["split_execution"]["alias_expanded_blueprints"]),
        "numeric_identity_representatives": int(release["split_execution"]["numeric_identity_representatives"]),
        "accepted_rows": len(registry_rows),
        "canonical_identities": len({row["canonical_identity"] for row in registry_rows}),
        "exact_signal_identities": len({row["exact_signal_identity"] for row in registry_rows}),
        "activation_identities": 0,
        "activation_clusters": 0,
        "pnl_regime_diagnostic_identities": len(pnl_counts),
        "economic_hypotheses": len({row["economic_hypothesis_identity"] for row in registry_rows}),
    }
    payload: dict[str, object] = {
        "decision": "LAYERED_IDENTITY_PARTIALLY_QUALIFIED",
        **counts,
        "activation_status": activation_status,
        "activation_artifact_available": activation_artifact_available,
        "release_contains_full_numeric_cache": bool(release["boundaries"].get("contains_full_numeric_cache")),
        "pnl_regime_basis": "spent validation/test/recent/stress sign pattern only",
        "economic_hypothesis_basis": "field, structure, and mechanism semantics only",
        "first_independent_economic_information_collapse_identified": False,
        "search_started": False,
        "forward_performance_read": False,
        "candidate_selection_performed": False,
        "promotion_memory_scheduler_or_generator_feedback": False,
        "state_event_reward_connected": False,
        "cem_ucb_mcts_updated": False,
        "a7mem_updated": False,
        "b1_lane_integration": False,
        "large_search_authorized": False,
        "alpha_ready": False,
    }
    RUNTIME.mkdir(parents=True, exist_ok=True)
    _write_csv(RUNTIME / "layered_identity_registry.csv", registry_rows, list(registry_rows[0]))
    _write_csv(RUNTIME / "pnl_regime_diagnostic_registry.csv", pnl_rows, list(pnl_rows[0]))
    _write_csv(RUNTIME / "economic_hypothesis_registry.csv", hypothesis_rows, list(hypothesis_rows[0]))
    (RUNTIME / "activation_asset_audit.json").write_text(
        json.dumps(
            {
                "status": activation_status,
                "listed_activation_artifacts": activation_artifacts,
                "release_contains_full_numeric_cache": release["boundaries"].get("contains_full_numeric_cache"),
                "expression_or_performance_proxy_allowed": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (RUNTIME / "identity_qualification_manifest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "\n".join(
            [
                "# Crypto B0P Layered Identity Qualification",
                "",
                f"Decision: `{payload['decision']}`",
                "",
                f"- alias-expanded / numeric representatives / accepted rows: `{counts['alias_expanded_blueprints']}` / `{counts['numeric_identity_representatives']}` / `{counts['accepted_rows']}`",
                f"- canonical / exact signal: `{counts['canonical_identities']}` / `{counts['exact_signal_identities']}`",
                f"- activation identities / clusters: `0 / 0` — `{activation_status}`",
                f"- spent PnL/regime sign identities: `{counts['pnl_regime_diagnostic_identities']}` (diagnostic only)",
                f"- semantic economic hypotheses: `{counts['economic_hypotheses']}`",
                "",
                "The observed six exact signals share one coarse spent split-sign pattern, but this is post-selection diagnostic evidence and not an economic-independence claim.",
                "Activation collapse remains unresolved because the accepted release contains fingerprints but no frozen signal behavior matrix. Expression or performance proxies were deliberately rejected.",
                "Economic hypotheses are semantic registrations, not promotion evidence.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
