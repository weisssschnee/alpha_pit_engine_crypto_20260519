from __future__ import annotations

import csv
import hashlib
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "crypto_formula_gen_v2_motif_pack_v1.json"

FIELD_MODE_COLUMN = {
    "ordinary_alpha": "ordinary_alpha_allowed",
    "diagnostic": "diagnostic_allowed",
    "risk_defense": "risk_defense_allowed",
}


@dataclass(frozen=True, slots=True)
class CryptoFormulaCandidate:
    candidate_id: str
    expression: str
    family: str
    field_families: tuple[str, ...]
    fields: tuple[str, ...]
    operators: tuple[str, ...]
    windows: tuple[int, ...]
    metadata: dict[str, Any]


def stable_hash(value: str, length: int = 16) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:length]


def extract_operators(expression: str) -> tuple[str, ...]:
    return tuple(re.findall(r"\b([A-Z][A-Za-z0-9_]*)\s*\(", expression))


def extract_windows(expression: str) -> tuple[int, ...]:
    values = [int(match) for match in re.findall(r",\s*(\d+)\s*\)", expression)]
    return tuple(sorted(set(values)))


def tree_depth(expression: str) -> int:
    depth = 0
    max_depth = 0
    for char in expression:
        if char == "(":
            depth += 1
            max_depth = max(max_depth, depth)
        elif char == ")":
            depth = max(0, depth - 1)
    return max_depth


def _choice(rng: random.Random, values: list[Any]) -> Any:
    if not values:
        raise ValueError("cannot sample from an empty list")
    return values[rng.randrange(len(values))]


def _weighted_choice(rng: random.Random, weights: dict[str, float]) -> str:
    items = [(key, max(0.0, float(value))) for key, value in weights.items()]
    total = sum(value for _, value in items)
    if total <= 0:
        return sorted(weights)[0]
    mark = rng.random() * total
    running = 0.0
    for key, value in sorted(items):
        running += value
        if running >= mark:
            return key
    return sorted(weights)[-1]


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def load_field_enforcement_csv(path: str | Path) -> dict[str, dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return {str(row["field_name"]): dict(row) for row in csv.DictReader(handle)}


class CryptoFormulaGenV2Adapter:
    """CN FormulaGenV2-style generator adapted to crypto field contracts.

    This is intentionally a fresh crypto adapter. It reuses the CN role/motif
    design pattern, but it does not import CN memory, CN stock fields, or CN
    reward outcomes.
    """

    def __init__(
        self,
        config: dict[str, Any],
        *,
        seed: str = "crypto_formula_gen_v2",
        field_enforcement: dict[str, dict[str, Any]] | None = None,
        field_mode: str = "syntax",
    ) -> None:
        self.config = config
        self.rng = random.Random(stable_hash(seed, 12))
        self.seed = seed
        self.field_enforcement = field_enforcement or {}
        self.field_mode = field_mode

    @classmethod
    def from_path(
        cls,
        path: str | Path = DEFAULT_CONFIG,
        *,
        seed: str = "crypto_formula_gen_v2",
        field_enforcement_path: str | Path | None = None,
        field_mode: str = "syntax",
    ) -> "CryptoFormulaGenV2Adapter":
        import json

        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        enforcement = load_field_enforcement_csv(field_enforcement_path) if field_enforcement_path else None
        return cls(payload, seed=seed, field_enforcement=enforcement, field_mode=field_mode)

    def _field_allowed_for_mode(self, field: str) -> bool:
        if self.field_mode == "syntax" or not self.field_enforcement:
            return True
        row = self.field_enforcement.get(field)
        if not row:
            return False
        if str(row.get("enforcement_status", "")).startswith("FORBID"):
            return False
        if str(row.get("enforcement_status", "")).startswith("HOLD_CONTRACT") or str(row.get("enforcement_status", "")).startswith("HOLD_TIMING"):
            return False
        mode_column = FIELD_MODE_COLUMN.get(self.field_mode)
        if not mode_column:
            raise ValueError(f"unknown field_mode: {self.field_mode}")
        return _truthy(row.get(mode_column))

    @property
    def field_registry(self) -> dict[str, list[str]]:
        registry: dict[str, list[str]] = {}
        for key, values in (self.config.get("field_families") or {}).items():
            registry[key] = [str(field) for field in values if self._field_allowed_for_mode(str(field))]
        return registry

    @property
    def allowed_fields(self) -> set[str]:
        values: set[str] = set()
        for fields in self.field_registry.values():
            values.update(str(field) for field in fields)
        return values

    def _sample_field(self, family: str) -> str:
        return str(_choice(self.rng, self.field_registry[family]))

    def _sample_window(self, class_name: str | None = None) -> int:
        buckets = self.config.get("windows") or {}
        if class_name and class_name in buckets:
            return int(_choice(self.rng, list(buckets[class_name])))
        flattened: list[int] = []
        for values in buckets.values():
            flattened.extend(int(value) for value in values)
        return int(_choice(self.rng, sorted(set(flattened)) or [4, 8, 24, 48, 168]))

    def _format(self, template: str, required_families: list[str]) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
        slots: dict[str, str] = {}
        used_fields: list[str] = []
        used_families: list[str] = []
        for family in required_families:
            field = self._sample_field(family)
            slots[family] = field
            used_fields.append(field)
            used_families.append(family)
        for index in range(1, 5):
            slots[f"w{index}"] = str(self._sample_window())
        return template.format(**slots), tuple(sorted(set(used_families))), tuple(sorted(set(used_fields)))

    def generate(self, *, index: int = 0) -> CryptoFormulaCandidate:
        families = self.config.get("motif_families") or {}
        weights = {key: float(value.get("weight", 1.0)) for key, value in families.items()}
        for _attempt in range(128):
            family = _weighted_choice(self.rng, weights)
            spec = families[family]
            template = str(_choice(self.rng, list(spec.get("templates") or [])))
            required_families = list(spec.get("field_families") or [])
            expression, field_families, used_fields = self._format(template, required_families)
            validation = validate_expression(
                expression,
                self.allowed_fields,
                self.config,
                field_enforcement=self.field_enforcement,
                field_mode=self.field_mode,
            )
            if validation["passed"]:
                candidate_id = f"crypto_fg2_{stable_hash(expression + str(index), 16)}"
                return CryptoFormulaCandidate(
                    candidate_id=candidate_id,
                    expression=expression,
                    family=family,
                    field_families=field_families,
                    fields=used_fields,
                    operators=extract_operators(expression),
                    windows=extract_windows(expression),
                    metadata={
                        "engine": "CryptoFormulaGenV2Adapter",
                        "cn_engine_structure_inherited": True,
                        "cn_memory_payload_inherited": False,
                        "cn_reward_payload_inherited": False,
                        "source_config": str(DEFAULT_CONFIG),
                        "field_mode": self.field_mode,
                        "semantic_field_enforcement_applied": bool(self.field_enforcement),
                    },
                )
        raise RuntimeError("failed to generate a valid crypto expression after 128 attempts")


def validate_expression(
    expression: str,
    allowed_fields: set[str],
    config: dict[str, Any],
    *,
    field_enforcement: dict[str, dict[str, Any]] | None = None,
    field_mode: str = "syntax",
) -> dict[str, Any]:
    reasons: list[str] = []
    max_tree_depth = int((config.get("constraints") or {}).get("max_tree_depth", 8))
    if tree_depth(expression) > max_tree_depth:
        reasons.append("tree_depth_exceeded")
    banned_tokens = set((config.get("constraints") or {}).get("banned_cn_stock_tokens") or [])
    lowered = expression.lower()
    for token in banned_tokens:
        if str(token).lower() in lowered:
            reasons.append(f"banned_cn_token:{token}")
    fields = set(re.findall(r"\b[a-z][a-z0-9_]*\b", expression))
    function_names = {name.lower() for name in extract_operators(expression)}
    numeric_words = {"nan", "inf"}
    candidate_fields = fields - function_names - numeric_words
    unknown = sorted(field for field in candidate_fields if field not in allowed_fields)
    if unknown:
        reasons.append("unknown_field:" + "|".join(unknown[:8]))
    if field_mode != "syntax" and field_enforcement:
        mode_column = FIELD_MODE_COLUMN.get(field_mode)
        if not mode_column:
            reasons.append(f"unknown_field_mode:{field_mode}")
        for field in sorted(candidate_fields):
            row = field_enforcement.get(field)
            if not row:
                reasons.append(f"field_contract_missing:{field}")
                continue
            status = str(row.get("enforcement_status", ""))
            if status == "FORBID" or status.startswith("HOLD_CONTRACT") or status.startswith("HOLD_TIMING"):
                reasons.append(f"field_enforcement_block:{field}:{status}")
            if mode_column and not _truthy(row.get(mode_column)):
                reasons.append(f"field_mode_not_allowed:{field}:{field_mode}")
    if "Mul(" in expression:
        mul_args = re.findall(r"Mul\((.*)\)", expression)
        unsafe = [arg for arg in mul_args if not any(prefix in arg for prefix in ("ZScore(", "Rank(", "Sign(", "Clip(", "Abs("))]
        if unsafe:
            reasons.append("unsafe_mul_input")
    return {"passed": not reasons, "reasons": reasons}
