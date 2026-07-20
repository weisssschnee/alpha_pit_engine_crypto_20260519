#!/usr/bin/env python3
"""Run or verify the bounded policy acceleration canary."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from alphafactory_crypto.broad_search.acceleration_canary import check_canary, run_canary


DEFAULT_CONFIG = REPO_ROOT / "config" / "crypto_policy_acceleration_canary_v1.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "check"))
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--source-sha")
    args = parser.parse_args()
    if args.command == "run" and not args.source_sha:
        parser.error("run requires --source-sha")
    result = (
        run_canary(REPO_ROOT, config_path=args.config.resolve(), source_sha=args.source_sha)
        if args.command == "run"
        else check_canary(REPO_ROOT, config_path=args.config.resolve())
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
