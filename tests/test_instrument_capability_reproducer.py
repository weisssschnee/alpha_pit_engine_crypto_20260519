from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts.crypto_instrument_capability import _two_fixed_seed_reproduction_pass


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "crypto_instrument_capability.py"


class ReproducerIdentityTests(unittest.TestCase):
    def test_outer_qualification_gate_requires_two_distinct_seeds(self) -> None:
        cross_seed = {
            "family": {
                "canonical_mechanism_reproduction": True,
                "behavior_reproduction": True,
            }
        }
        duplicate_seed_payload = {
            "seeds": [123, 123],
            "distinct_seed_count": 1,
            "minimum_distinct_seed_count_met": False,
            "cross_seed_qualified": False,
            "cross_seed_reproduction": cross_seed,
        }
        self.assertFalse(_two_fixed_seed_reproduction_pass(duplicate_seed_payload))
        distinct_seed_payload = {
            **duplicate_seed_payload,
            "seeds": [123, 124],
            "distinct_seed_count": 2,
            "minimum_distinct_seed_count_met": True,
            "cross_seed_qualified": True,
        }
        self.assertTrue(_two_fixed_seed_reproduction_pass(distinct_seed_payload))

    def test_symbolic_and_abbreviated_source_refs_are_rejected(self) -> None:
        full_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=True,
        ).stdout.strip()
        for invalid in ("HEAD", full_sha[:12]):
            with self.subTest(invalid=invalid):
                completed = subprocess.run(
                    [sys.executable, str(SCRIPT), "build", "--source-sha", invalid],
                    cwd=REPO,
                    text=True,
                    encoding="utf-8",
                    capture_output=True,
                    check=False,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("full 40-character commit SHA", completed.stderr)


if __name__ == "__main__":
    unittest.main()
