from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphafactory_crypto.unified_field_management import build_management_view


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-sha", required=True)
    args = parser.parse_args()
    config = json.loads(
        (ROOT / "config/crypto_unified_field_management_v1.json").read_text(
            encoding="utf-8"
        )
    )
    manifest = build_management_view(ROOT, config, source_sha=args.source_sha)
    print(json.dumps(manifest["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
