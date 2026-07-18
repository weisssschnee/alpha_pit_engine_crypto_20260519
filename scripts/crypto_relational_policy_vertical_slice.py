from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from alphafactory_crypto.relational_policy import run_vertical_slice_smoke


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the bounded development-only relational direct-weight smoke"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "config/crypto_relational_policy_vertical_slice_v1.json",
    )
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    print(json.dumps(run_vertical_slice_smoke(REPO_ROOT, config), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
