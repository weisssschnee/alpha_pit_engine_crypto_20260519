from __future__ import annotations

import os
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


os.environ.setdefault("A7AL2X7F_STAGE", "A7AL-2X7HF")
os.environ.setdefault("A7AL2X7F_SOURCE_STAGE", "A7AL-2X7H")
os.environ.setdefault("A7AL2X7F_SOURCE_PREFIX", "a7al2x7h")
os.environ.setdefault("A7AL2X7F_FILE_PREFIX", "a7al2x7hf")
os.environ.setdefault("A7AL2X7F_REPORT_TITLE", "CRYPTO A7AL-2X7HF HEAVY REPLAY PREFLIGHT FORENSIC")
os.environ.setdefault("A7AL2X7F_SOURCE_RUNTIME", r"runtime\a7al2x7h_heavy_numeric_replay_preflight")
os.environ.setdefault("A7AL2X7F_RUNTIME", r"runtime\a7al2x7hf_heavy_replay_preflight_forensic")
os.environ.setdefault("A7AL2X7F_REPORT", r"reports\CRYPTO_A7AL2X7HF_HEAVY_REPLAY_PREFLIGHT_FORENSIC_20260529.md")

from scripts.crypto_a7al2x7f_replay_preflight_forensic import main


if __name__ == "__main__":
    main()
