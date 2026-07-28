from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphafactory_crypto.unified_field_management import build_management_view


def main() -> None:
    config = json.loads(
        (ROOT / "config/crypto_unified_field_management_v1.json").read_text(
            encoding="utf-8"
        )
    )
    manifest = build_management_view(ROOT, config)
    print(json.dumps(manifest["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
