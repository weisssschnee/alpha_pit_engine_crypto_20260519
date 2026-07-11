from __future__ import annotations

import unittest

from alphafactory_crypto.benchmarks import (
    BenchmarkObservation,
    BenchmarkRegistry,
    BenchmarkSpec,
    assert_benchmark_observations_not_memory,
)


class BenchmarkRegistryTests(unittest.TestCase):
    def test_registry_requires_benchmark_only_inputs(self) -> None:
        registry = BenchmarkRegistry()
        with self.assertRaises(ValueError):
            registry.register(BenchmarkSpec("bad", 1, "market", ("x",), ("primary",), "return", "bad"))

    def test_duplicate_benchmark_id_fails(self) -> None:
        registry = BenchmarkRegistry()
        spec = BenchmarkSpec("benchmark:x:v1", 1, "market", ("trade_close",), ("benchmark-only",), "return", "x")
        registry.register(spec)
        with self.assertRaises(ValueError):
            registry.register(spec)

    def test_observation_is_report_only(self) -> None:
        observation = BenchmarkObservation("benchmark:x:v1", "return", 0.1, "train_2024", "DISCOVERY_TRAIN")
        assert_benchmark_observations_not_memory([observation])
        invalid = BenchmarkObservation("benchmark:x:v1", "return", 0.1, "train_2024", "DISCOVERY_TRAIN", "POSITIVE_MEMORY")
        with self.assertRaises(PermissionError):
            assert_benchmark_observations_not_memory([invalid])


if __name__ == "__main__":
    unittest.main()
