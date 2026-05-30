from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

A7FF37_MANIFEST = REPO / "runtime" / "a7ff37_deep_replay_contract" / "a7ff37_manifest.json"
RUNTIME = REPO / "runtime" / "a7ff37a_bounded_deep_replay"
REPORT = REPO / "reports" / "CRYPTO_A7FF37A_BOUNDED_DEEP_REPLAY_20260530.md"
QUEUE = REPO / "runtime" / "a7ff37_deep_replay_contract" / "a7ff37_deep_replay_queue.csv"


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> None:
    manifest = read_json(A7FF37_MANIFEST)
    if not manifest.get("authorizes_a7ff37a_bounded_deep_replay"):
        raise SystemExit(f"A7FF-37 does not authorize A7FF-37A: {manifest.get('decision')}")

    os.environ["A7FF8_STAGE"] = "A7FF-37A"
    os.environ["A7FF8_FILE_PREFIX"] = "a7ff37a"
    os.environ["A7FF8_RUNTIME"] = str(RUNTIME)
    os.environ["A7FF8_REPORT"] = str(REPORT)
    os.environ["A7FF8_QUEUE_PATH"] = str(QUEUE)
    os.environ["A7FF8_MATERIALIZE_CAP"] = "4"
    os.environ["A7FF8_FAST_NUMERIC_CAP"] = "4"
    os.environ["A7FF8_PORTFOLIO_CAP"] = "4"
    os.environ["A7FF8_QUEUE_LIMIT"] = "4"

    z2r = importlib.import_module("scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair")
    z2r.SYMBOL_CAP = 181

    numeric_probe = importlib.import_module("scripts.crypto_a7ff8_expanded_numeric_probe")
    numeric_probe.main()


if __name__ == "__main__":
    main()
