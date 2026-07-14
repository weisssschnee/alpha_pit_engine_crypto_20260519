from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "crypto_instrument_capability.py"


class ReproducerIdentityTests(unittest.TestCase):
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
