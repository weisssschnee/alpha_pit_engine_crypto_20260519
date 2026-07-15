#!/usr/bin/env python3
"""Run or verify the bounded 18M compositional development search."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from alphafactory_crypto.broad_search.runner18m import build_evidence, check_evidence


DEFAULT_CONFIG = REPO_ROOT / "config" / "crypto_18m_compositional_broad_search_v1.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "check"))
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--source-sha")
    args = parser.parse_args()
    if args.command == "run":
        result = build_evidence(
            REPO_ROOT,
            config_path=args.config.resolve(),
            source_sha=args.source_sha,
        )
    else:
        result = check_evidence(REPO_ROOT, config_path=args.config.resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
