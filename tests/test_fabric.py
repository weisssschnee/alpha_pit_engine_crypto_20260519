from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from alphafactory_crypto.fabric import (
    FabricArtifactSpec,
    deterministic_cache_key,
    validate_cache,
    write_deterministic_array_cache,
)


def spec(**overrides: object) -> FabricArtifactSpec:
    values: dict[str, object] = {
        "artifact_id": "test:state:v1",
        "artifact_kind": "state",
        "data_role": "synthetic",
        "input_role": "state-only",
        "primitive_equivalence_id": "temporal-equivalence:test",
        "source_artifact_shas": ("A", "B"),
        "field_registry_sha": "REG",
        "contract_sha": "CONTRACT",
        "code_sha": "CODE",
        "universe_sha": "UNIVERSE",
        "timestamps_sha": "TIME",
        "dtype": "<f8",
        "shape": (2, 2),
        "endianness": "little",
        "nan_policy": "preserve",
        "observable_time_rule": "pit",
        "maturity_rule": "mature",
        "feedback_permission": "NO_REWARD_B0",
    }
    values.update(overrides)
    return FabricArtifactSpec(**values)


class FabricTests(unittest.TestCase):
    def test_cache_key_is_path_independent_and_source_order_independent(self) -> None:
        self.assertEqual(deterministic_cache_key(spec()), deterministic_cache_key(spec(source_artifact_shas=("B", "A"))))

    def test_contract_change_changes_cache_key(self) -> None:
        self.assertNotEqual(deterministic_cache_key(spec()), deterministic_cache_key(spec(contract_sha="OTHER")))
        self.assertNotEqual(deterministic_cache_key(spec()), deterministic_cache_key(spec(artifact_id="test:state:v2")))

    def test_dtype_endianness_disagreement_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                write_deterministic_array_cache(
                    Path(root), spec(dtype=">f8", endianness="little"), np.arange(4, dtype="<f8").reshape(2, 2)
                )

    def test_write_rebuild_and_tamper_detection(self) -> None:
        array = np.arange(4, dtype="<f8").reshape(2, 2)
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = write_deterministic_array_cache(Path(first_dir), spec(), array)
            second = write_deterministic_array_cache(Path(second_dir), spec(), array.copy())
            self.assertEqual(first["cache_key"], second["cache_key"])
            self.assertEqual(first["content_sha256"], second["content_sha256"])
            manifest = next(Path(first_dir).glob("*.manifest.json"))
            data = next(Path(first_dir).glob("*.bin"))
            data.write_bytes(data.read_bytes() + b"tamper")
            with self.assertRaises(ValueError):
                validate_cache(manifest)

    def test_state_reward_permission_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(PermissionError):
                write_deterministic_array_cache(
                    Path(root), spec(feedback_permission="REWARD"), np.arange(4, dtype="<f8").reshape(2, 2)
                )


if __name__ == "__main__":
    unittest.main()
