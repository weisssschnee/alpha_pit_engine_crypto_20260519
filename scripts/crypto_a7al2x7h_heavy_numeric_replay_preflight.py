from __future__ import annotations

import os
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


os.environ.setdefault("A7AL2X7_STAGE", "A7AL-2X7H")
os.environ.setdefault("A7AL2X7_FILE_PREFIX", "a7al2x7h")
os.environ.setdefault("A7AL2X7_REPORT_TITLE", "CRYPTO A7AL-2X7H HEAVY NUMERIC REPLAY PREFLIGHT")
os.environ.setdefault("A7AL2X7_RUNTIME", r"runtime\a7al2x7h_heavy_numeric_replay_preflight")
os.environ.setdefault("A7AL2X7_REPORT", r"reports\CRYPTO_A7AL2X7H_HEAVY_NUMERIC_REPLAY_PREFLIGHT_20260529.md")

os.environ.setdefault("A7AL2X7_CANDIDATE_CAP", "56")
os.environ.setdefault("A7AL2X7_PER_FAMILY_CAP", "8")
os.environ.setdefault("A7AL2X7_SYMBOL_CAP", "96")
os.environ.setdefault("A7AL2X7_MIN_ACTIVE_SYMBOLS", "60")
os.environ.setdefault("A7AL2X7_HOURS_PER_SPLIT", "720")

from scripts.crypto_a7al2x7_small_numeric_replay_preflight import main


if __name__ == "__main__":
    main()
