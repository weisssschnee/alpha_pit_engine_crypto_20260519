#!/usr/bin/env python3
"""Build, check, or inspect the train-only 18-month Crypto surface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from alphafactory_crypto.train_surface import (  # noqa: E402
    build_qualification,
    check_qualification,
    load_symbol_train,
)


DEFAULT_CONFIG = REPO_ROOT / "config" / "crypto_train_surface_18m_v1.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "check", "inspect-symbol"))
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--skip-source-hashes", action="store_true")
    args = parser.parse_args()
    config_path = args.config.resolve()
    if args.command == "build":
        result = build_qualification(
            REPO_ROOT,
            config_path=config_path,
            hash_source_files=not args.skip_source_hashes,
        )
    elif args.command == "check":
        result = check_qualification(REPO_ROOT, config_path=config_path)
    else:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        frame = load_symbol_train(config, args.symbol)
        result = {
            "result": "PASS" if not frame.empty else "FAIL",
            "symbol": args.symbol,
            "rows": int(frame.shape[0]),
            "timestamp_min": str(frame["timestamp"].min()) if not frame.empty else None,
            "timestamp_max": str(frame["timestamp"].max()) if not frame.empty else None,
            "columns": frame.columns.tolist(),
            "source_segments": sorted(frame["source_segment"].unique().tolist())
            if not frame.empty
            else [],
        }
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True))
    return 0 if result.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
