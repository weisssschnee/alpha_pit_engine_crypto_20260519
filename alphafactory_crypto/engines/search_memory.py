from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from alphafactory_crypto.engines.formula_gen_v2_adapter import extract_operators, extract_windows


CRYPTO_SEARCH_MEMORY_SCHEMA_VERSION = "crypto-search-memory-v1-2026-05-27"


def _digest(value: str, length: int = 16) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:length]


def canonicalize_expression_light(expression: str) -> str:
    text = re.sub(r"\s+", "", expression or "")
    return text


def expression_memory_key(expression: str) -> str:
    return f"expr-{_digest(canonicalize_expression_light(expression))}"


def skeleton_expression(expression: str) -> str:
    text = canonicalize_expression_light(expression)
    text = re.sub(r"\b[a-z][a-z0-9_]*\b", "FIELD", text)
    text = re.sub(r"\b\d+\b", "W", text)
    return text


def skeleton_memory_key(expression: str) -> str:
    return f"skeleton-{_digest(skeleton_expression(expression))}"


def production_rule_key(*, engine: str, family: str, field_families: str, horizon_signature: str) -> str:
    return "::".join([engine, family, field_families, horizon_signature])


@dataclass(slots=True)
class CryptoMemoryRecord:
    candidate_id: str
    expression: str
    family: str
    field_families: str
    expression_key: str
    skeleton_key: str
    production_key: str
    operator_signature: str
    horizon_signature: str


class CryptoSearchMemory:
    def __init__(
        self,
        *,
        namespace: str,
        inherited_paths: list[str] | None = None,
        expression_keys: set[str] | None = None,
        skeleton_keys: set[str] | None = None,
        records: list[CryptoMemoryRecord] | None = None,
        enforce_skeleton_unique: bool = False,
    ) -> None:
        self.namespace = namespace
        self.inherited_paths = inherited_paths or []
        self.expression_keys = expression_keys or set()
        self.skeleton_keys = skeleton_keys or set()
        self.records = records or []
        self.enforce_skeleton_unique = enforce_skeleton_unique
        self.duplicate_events: list[dict[str, Any]] = []
        self.skeleton_repeat_events: list[dict[str, Any]] = []

    @classmethod
    def fresh(cls, *, namespace: str) -> "CryptoSearchMemory":
        return cls(namespace=namespace)

    def add_candidate(self, row: dict[str, Any]) -> bool:
        expression = str(row["expression"])
        expression_key = expression_memory_key(expression)
        skeleton_key = skeleton_memory_key(expression)
        if expression_key in self.expression_keys:
            self.duplicate_events.append({"candidate_id": row.get("candidate_id"), "duplicate_type": "expression", "key": expression_key})
            return False
        if skeleton_key in self.skeleton_keys and self.enforce_skeleton_unique:
            self.duplicate_events.append({"candidate_id": row.get("candidate_id"), "duplicate_type": "skeleton", "key": skeleton_key})
            return False
        if skeleton_key in self.skeleton_keys:
            self.skeleton_repeat_events.append({"candidate_id": row.get("candidate_id"), "duplicate_type": "skeleton_repeat_soft", "key": skeleton_key})

        operators = "|".join(sorted(set(extract_operators(expression))))
        horizons = "|".join(str(value) for value in extract_windows(expression))
        field_families = str(row.get("field_families", ""))
        family = str(row.get("family", ""))
        record = CryptoMemoryRecord(
            candidate_id=str(row.get("candidate_id", "")),
            expression=expression,
            family=family,
            field_families=field_families,
            expression_key=expression_key,
            skeleton_key=skeleton_key,
            production_key=production_rule_key(
                engine="crypto_formula_gen_v2_adapter",
                family=family,
                field_families=field_families,
                horizon_signature=horizons,
            ),
            operator_signature=operators,
            horizon_signature=horizons,
        )
        self.expression_keys.add(expression_key)
        self.skeleton_keys.add(skeleton_key)
        self.records.append(record)
        return True

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema_version": CRYPTO_SEARCH_MEMORY_SCHEMA_VERSION,
            "namespace": self.namespace,
            "inherited_paths": self.inherited_paths,
            "expression_keys": sorted(self.expression_keys),
            "skeleton_keys": sorted(self.skeleton_keys),
            "records": [asdict(record) for record in self.records],
            "duplicate_events": self.duplicate_events,
            "skeleton_repeat_events": self.skeleton_repeat_events,
            "cn_memory_payload_inherited": False,
        }

    def write(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(self.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
