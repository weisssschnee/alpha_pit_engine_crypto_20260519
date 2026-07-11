from __future__ import annotations

import unittest

from scripts.crypto_architecture_control_plane import (
    REGISTRY_PATH,
    load_json,
    validate_outputs,
    validate_registry,
)


class ArchitectureControlPlaneTests(unittest.TestCase):
    def test_registry_and_generated_outputs_are_synchronized(self) -> None:
        registry = load_json(REGISTRY_PATH)
        validate_registry(registry)
        validate_outputs(registry)


if __name__ == "__main__":
    unittest.main()
