from __future__ import annotations

import csv
import unittest
from pathlib import Path

from alphafactory_crypto.input_roles import classify_input_role, validate_registry_rows


class InputRoleTests(unittest.TestCase):
    def test_precedence_blocks_future_fields(self) -> None:
        role, _ = classify_input_role({"field_name": "future_x", "uses_future": "True", "timing_ok": "True"})
        self.assertEqual(role, "blocked")

    def test_price_anchor_is_benchmark_only(self) -> None:
        role, _ = classify_input_role(
            {"field_name": "trade_close", "semantic_type_v3": "price_like", "timing_ok": "True", "allowed_roles_v3": "signal"}
        )
        self.assertEqual(role, "benchmark-only")

    def test_ordinary_alpha_role_is_primary_but_not_b0_enabled(self) -> None:
        role, _ = classify_input_role(
            {"field_name": "basis", "compiler_role_v3": "ordinary_alpha_seed", "timing_ok": "True", "allowed_roles_v3": "signal"}
        )
        self.assertEqual(role, "primary")

    def test_generated_registry_covers_ontology_and_enables_no_generator_fields(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        ontology_path = repo / "runtime" / "a7ffr1_field_ontology_v3" / "a7ffr1_field_ontology_v3.csv"
        registry_path = repo / "runtime" / "a7input0_v2_field_roles_20260711" / "a7input0_v2_field_role_registry.csv"
        with ontology_path.open("r", encoding="utf-8", newline="") as handle:
            ontology = list(csv.DictReader(handle))
        with registry_path.open("r", encoding="utf-8", newline="") as handle:
            registry = list(csv.DictReader(handle))
        validate_registry_rows(registry, {row["field_name"] for row in ontology})


if __name__ == "__main__":
    unittest.main()
