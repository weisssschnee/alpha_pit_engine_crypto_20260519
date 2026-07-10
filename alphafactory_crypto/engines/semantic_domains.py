from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

from alphafactory_crypto.engines.feature_algebra import parse_call


REPO = Path(__file__).resolve().parents[2]
DEFAULT_RULES = REPO / "config" / "crypto_field_value_domain_rules_v1.json"


class ValueDomain(str, Enum):
    STRICT_POSITIVE = "STRICT_POSITIVE"
    NON_NEGATIVE = "NON_NEGATIVE"
    SIGNED = "SIGNED"
    UNIT_INTERVAL = "UNIT_INTERVAL"
    BOOLEAN = "BOOLEAN"
    STRICT_NEGATIVE = "STRICT_NEGATIVE"
    NON_POSITIVE = "NON_POSITIVE"
    ZERO = "ZERO"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class FieldDomainRegistry:
    domains: dict[str, ValueDomain]
    known_fields: frozenset[str]
    regex_domains: tuple[tuple[re.Pattern[str], ValueDomain], ...]
    semantic_defaults: dict[str, ValueDomain]
    semantic_types: dict[str, str]

    @classmethod
    def from_rules(cls, rules_path: str | Path = DEFAULT_RULES) -> "FieldDomainRegistry":
        path = Path(rules_path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        domains: dict[str, ValueDomain] = {}
        for domain_name, fields in dict(payload.get("exact_domains") or {}).items():
            domain = ValueDomain(domain_name)
            for field in fields:
                domains[str(field)] = domain

        ontology_path = REPO / str(payload.get("ontology_csv") or "")
        semantic_types: dict[str, str] = {}
        if ontology_path.exists():
            with ontology_path.open("r", encoding="utf-8", newline="") as handle:
                for row in csv.DictReader(handle):
                    field = str(row.get("field_name") or "")
                    if field:
                        semantic_types[field] = str(row.get("semantic_type_v3") or "")

        regex_domains = tuple(
            (re.compile(str(item["pattern"]), re.IGNORECASE), ValueDomain(str(item["domain"])))
            for item in payload.get("regex_domains", [])
        )
        semantic_defaults = {
            str(key): ValueDomain(str(value))
            for key, value in dict(payload.get("semantic_type_defaults") or {}).items()
        }
        return cls(
            domains=domains,
            known_fields=frozenset(semantic_types),
            regex_domains=regex_domains,
            semantic_defaults=semantic_defaults,
            semantic_types=semantic_types,
        )

    def field_domain(self, field: str) -> ValueDomain:
        if field in self.domains:
            return self.domains[field]
        for pattern, domain in self.regex_domains:
            if pattern.search(field):
                return domain
        return self.semantic_defaults.get(self.semantic_types.get(field, ""), ValueDomain.UNKNOWN)


@lru_cache(maxsize=1)
def default_domain_registry() -> FieldDomainRegistry:
    return FieldDomainRegistry.from_rules()


def _number_domain(text: str) -> ValueDomain | None:
    try:
        value = float(text)
    except ValueError:
        return None
    if value > 0:
        return ValueDomain.STRICT_POSITIVE
    if value < 0:
        return ValueDomain.STRICT_NEGATIVE
    return ValueDomain.ZERO


def _negate(domain: ValueDomain) -> ValueDomain:
    return {
        ValueDomain.STRICT_POSITIVE: ValueDomain.STRICT_NEGATIVE,
        ValueDomain.STRICT_NEGATIVE: ValueDomain.STRICT_POSITIVE,
        ValueDomain.NON_NEGATIVE: ValueDomain.NON_POSITIVE,
        ValueDomain.NON_POSITIVE: ValueDomain.NON_NEGATIVE,
    }.get(domain, domain)


def _mul_domain(left: ValueDomain, right: ValueDomain) -> ValueDomain:
    if ValueDomain.ZERO in {left, right}:
        return ValueDomain.ZERO
    positive = {ValueDomain.STRICT_POSITIVE, ValueDomain.UNIT_INTERVAL}
    if left in positive and right in positive:
        return ValueDomain.STRICT_POSITIVE
    if left in positive and right == ValueDomain.NON_NEGATIVE:
        return ValueDomain.NON_NEGATIVE
    if right in positive and left == ValueDomain.NON_NEGATIVE:
        return ValueDomain.NON_NEGATIVE
    if left in positive and right == ValueDomain.STRICT_NEGATIVE:
        return ValueDomain.STRICT_NEGATIVE
    if right in positive and left == ValueDomain.STRICT_NEGATIVE:
        return ValueDomain.STRICT_NEGATIVE
    return ValueDomain.SIGNED if ValueDomain.UNKNOWN not in {left, right} else ValueDomain.UNKNOWN


def _operator_domain(name: str, args: list[str], child: list[ValueDomain]) -> ValueDomain:
    if name in {"Rank", "CSRank", "TSRank", "LatentNeutralRank"}:
        return ValueDomain.UNIT_INTERVAL
    if name in {"Mean", "Decay", "Winsor"} and child:
        if child[0] == ValueDomain.UNIT_INTERVAL:
            return ValueDomain.STRICT_POSITIVE
        return child[0]
    if name == "Abs":
        return ValueDomain.STRICT_POSITIVE if child and child[0] in {ValueDomain.STRICT_POSITIVE, ValueDomain.STRICT_NEGATIVE, ValueDomain.UNIT_INTERVAL} else ValueDomain.NON_NEGATIVE
    if name == "Sign":
        if child and child[0] in {ValueDomain.STRICT_POSITIVE, ValueDomain.UNIT_INTERVAL}:
            return ValueDomain.STRICT_POSITIVE
        if child and child[0] == ValueDomain.STRICT_NEGATIVE:
            return ValueDomain.STRICT_NEGATIVE
        if child and child[0] == ValueDomain.ZERO:
            return ValueDomain.ZERO
        return ValueDomain.SIGNED
    if name in {"Delta", "Sub", "ZScore", "GroupNeutralize"}:
        return ValueDomain.SIGNED
    if name == "Neg" and child:
        return _negate(child[0])
    if name in {"Mul", "SafeDiv"} and len(child) >= 2:
        return _mul_domain(child[0], child[1])
    if name == "Add" and len(child) >= 2:
        if all(value in {ValueDomain.STRICT_POSITIVE, ValueDomain.UNIT_INTERVAL} for value in child[:2]):
            return ValueDomain.STRICT_POSITIVE
        if all(value in {ValueDomain.STRICT_POSITIVE, ValueDomain.UNIT_INTERVAL, ValueDomain.NON_NEGATIVE, ValueDomain.ZERO} for value in child[:2]):
            return ValueDomain.NON_NEGATIVE
        return ValueDomain.SIGNED if ValueDomain.UNKNOWN not in set(child[:2]) else ValueDomain.UNKNOWN
    if name == "Clip" and len(args) == 3:
        try:
            lower, upper = float(args[1]), float(args[2])
        except ValueError:
            return ValueDomain.UNKNOWN
        if lower > 0:
            return ValueDomain.STRICT_POSITIVE
        if lower >= 0:
            return ValueDomain.NON_NEGATIVE
        if upper < 0:
            return ValueDomain.STRICT_NEGATIVE
        if upper <= 0:
            return ValueDomain.NON_POSITIVE
        return ValueDomain.SIGNED
    if name == "StateMask":
        return ValueDomain.BOOLEAN
    return ValueDomain.UNKNOWN


def infer_value_domain(expression: str, registry: FieldDomainRegistry | None = None) -> ValueDomain:
    registry = registry or default_domain_registry()
    text = expression.strip()
    call = parse_call(text)
    if call is None:
        return _number_domain(text) or registry.field_domain(text)
    name, args = call
    return _operator_domain(name, args, [infer_value_domain(arg, registry) for arg in args])


def semantic_degeneracy_reasons(expression: str, registry: FieldDomainRegistry | None = None) -> list[str]:
    if "Sign" not in expression and "Abs" not in expression:
        return []
    registry = registry or default_domain_registry()
    def analyze(text: str) -> tuple[ValueDomain, list[str]]:
        call = parse_call(text.strip())
        if call is None:
            return _number_domain(text.strip()) or registry.field_domain(text.strip()), []
        name, args = call
        child_results = [analyze(arg) for arg in args]
        child_domains = [result[0] for result in child_results]
        reasons = [reason for _, child_reasons in child_results for reason in child_reasons]
        if name == "Sign" and args:
            domain = child_domains[0]
            if domain in {ValueDomain.STRICT_POSITIVE, ValueDomain.UNIT_INTERVAL}:
                reasons.append("constant_sign_of_strictly_positive_subtree")
            elif domain == ValueDomain.STRICT_NEGATIVE:
                reasons.append("constant_sign_of_strictly_negative_subtree")
        if name == "Abs" and args:
            domain = child_domains[0]
            if domain in {ValueDomain.STRICT_POSITIVE, ValueDomain.NON_NEGATIVE, ValueDomain.UNIT_INTERVAL}:
                reasons.append("redundant_abs_of_nonnegative_subtree")
        return _operator_domain(name, args, child_domains), reasons

    _, reasons = analyze(expression)
    return list(dict.fromkeys(reasons))


def canonicalize_semantic_expression(
    expression: str,
    registry: FieldDomainRegistry | None = None,
) -> tuple[str, list[str]]:
    registry = registry or default_domain_registry()

    def simplify(text: str) -> tuple[str, ValueDomain, list[str]]:
        stripped = text.strip()
        call = parse_call(stripped)
        if call is None:
            return stripped, _number_domain(stripped) or registry.field_domain(stripped), []
        name, args = call
        child_results = [simplify(arg) for arg in args]
        simplified_args = [result[0] for result in child_results]
        child_domains = [result[1] for result in child_results]
        reasons = [reason for _, _, child_reasons in child_results for reason in child_reasons]
        domain = _operator_domain(name, args, child_domains)

        if name == "Sign" and child_domains:
            if child_domains[0] in {ValueDomain.STRICT_POSITIVE, ValueDomain.UNIT_INTERVAL}:
                reasons.append("constant_sign_of_strictly_positive_subtree")
                return "1", ValueDomain.STRICT_POSITIVE, reasons
            if child_domains[0] == ValueDomain.STRICT_NEGATIVE:
                reasons.append("constant_sign_of_strictly_negative_subtree")
                return "-1", ValueDomain.STRICT_NEGATIVE, reasons
            if child_domains[0] == ValueDomain.ZERO:
                return "0", ValueDomain.ZERO, reasons
        if name == "Abs" and child_domains and child_domains[0] in {
            ValueDomain.STRICT_POSITIVE,
            ValueDomain.NON_NEGATIVE,
            ValueDomain.UNIT_INTERVAL,
        }:
            reasons.append("redundant_abs_of_nonnegative_subtree")
            return simplified_args[0], child_domains[0], reasons
        if name == "Mul" and len(simplified_args) == 2:
            left, right = simplified_args
            if "0" in {left, right}:
                return "0", ValueDomain.ZERO, reasons
            if left == "1":
                return right, child_domains[1], reasons
            if right == "1":
                return left, child_domains[0], reasons
            if left == "-1":
                return f"Neg({right})", _negate(child_domains[1]), reasons
            if right == "-1":
                return f"Neg({left})", _negate(child_domains[0]), reasons
        if name == "Add" and len(simplified_args) == 2:
            if simplified_args[0] == "0":
                return simplified_args[1], child_domains[1], reasons
            if simplified_args[1] == "0":
                return simplified_args[0], child_domains[0], reasons
        if name == "Sub" and len(simplified_args) == 2 and simplified_args[1] == "0":
            return simplified_args[0], child_domains[0], reasons
        if name == "Neg" and simplified_args:
            if simplified_args[0] == "0":
                return "0", ValueDomain.ZERO, reasons
            if simplified_args[0] == "1":
                return "-1", ValueDomain.STRICT_NEGATIVE, reasons
            if simplified_args[0] == "-1":
                return "1", ValueDomain.STRICT_POSITIVE, reasons
        return f"{name}({','.join(simplified_args)})", domain, reasons

    canonical, _, reasons = simplify(expression)
    return canonical, list(dict.fromkeys(reasons))


def is_numeric_constant_expression(expression: str) -> bool:
    return _number_domain(expression.strip()) is not None


def collect_operator_calls(expression: str, operator: str) -> list[tuple[str, list[str]]]:
    calls: list[tuple[str, list[str]]] = []

    def visit(text: str) -> None:
        call = parse_call(text.strip())
        if call is None:
            return
        name, args = call
        if name == operator:
            calls.append((text.strip(), args))
        for arg in args:
            visit(arg)

    visit(expression)
    return calls
