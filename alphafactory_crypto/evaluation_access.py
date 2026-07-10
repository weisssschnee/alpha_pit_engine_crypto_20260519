from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


REPO = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = REPO / "config" / "crypto_evaluation_access_policy_v1.json"


class EvaluationAccessViolation(RuntimeError):
    """Raised when sealed or spent evaluation data would influence candidate feedback."""

    def __init__(self, context: str, blocked_columns: Sequence[str], policy_id: str) -> None:
        self.context = context
        self.blocked_columns = tuple(sorted(set(blocked_columns)))
        self.policy_id = policy_id
        columns = ", ".join(self.blocked_columns)
        super().__init__(f"{policy_id} blocked candidate feedback at {context}: {columns}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": "BLOCKED_EVALRESET_CANDIDATE_FEEDBACK",
            "policy_id": self.policy_id,
            "context": self.context,
            "blocked_columns": list(self.blocked_columns),
        }


@dataclass(frozen=True)
class EpochAccess:
    epoch_id: str
    classification: str
    candidate_feedback_allowed: bool
    reason: str


def load_evaluation_access_policy(path: Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    policy = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "policy_id",
        "default_epoch_classification",
        "allowed_candidate_feedback_classifications",
        "epochs",
        "sealed_epoch_rules",
    }
    missing = sorted(required.difference(policy))
    if missing:
        raise ValueError(f"evaluation access policy missing keys: {missing}")
    return policy


def epoch_access(epoch_id: str, policy: Mapping[str, Any] | None = None) -> EpochAccess:
    active = dict(policy or load_evaluation_access_policy())
    for row in active.get("epochs", []):
        if str(row.get("epoch_id")) == epoch_id:
            return EpochAccess(
                epoch_id=epoch_id,
                classification=str(row.get("classification", "")),
                candidate_feedback_allowed=bool(row.get("candidate_feedback_allowed", False)),
                reason=str(row.get("reason", "")),
            )
    return EpochAccess(
        epoch_id=epoch_id,
        classification=str(active["default_epoch_classification"]),
        candidate_feedback_allowed=False,
        reason="Unknown epochs are sealed by default.",
    )


def assert_epoch_candidate_feedback_allowed(
    epoch_ids: Iterable[str],
    *,
    context: str,
    policy: Mapping[str, Any] | None = None,
) -> None:
    active = dict(policy or load_evaluation_access_policy())
    blocked = [epoch_id for epoch_id in epoch_ids if not epoch_access(epoch_id, active).candidate_feedback_allowed]
    if blocked:
        raise EvaluationAccessViolation(context, blocked, str(active["policy_id"]))


def blocked_candidate_feedback_columns(
    columns: Iterable[str], policy: Mapping[str, Any] | None = None
) -> list[str]:
    active = dict(policy or load_evaluation_access_policy())
    patterns = [
        re.compile(str(pattern), flags=re.IGNORECASE)
        for pattern in active.get("candidate_feedback_blocked_column_patterns", [])
    ]
    derived = {
        str(column).strip().lower()
        for column in active.get("candidate_feedback_blocked_derived_columns", [])
    }
    blocked: list[str] = []
    for raw_column in columns:
        column = str(raw_column).strip()
        lowered = column.lower()
        if lowered in derived or any(pattern.search(lowered) for pattern in patterns):
            blocked.append(column)
    return sorted(set(blocked))


def assert_candidate_feedback_columns_allowed(
    columns: Iterable[str],
    *,
    context: str,
    policy: Mapping[str, Any] | None = None,
) -> None:
    active = dict(policy or load_evaluation_access_policy())
    blocked = blocked_candidate_feedback_columns(columns, active)
    if blocked:
        raise EvaluationAccessViolation(context, blocked, str(active["policy_id"]))


def assert_candidate_feedback_records_allowed(
    records: Sequence[Mapping[str, Any]],
    *,
    context: str,
    policy: Mapping[str, Any] | None = None,
) -> None:
    columns: set[str] = set()
    for record in records:
        columns.update(str(key) for key in record)
    assert_candidate_feedback_columns_allowed(columns, context=context, policy=policy)
