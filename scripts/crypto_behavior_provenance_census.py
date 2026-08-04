from __future__ import annotations

import argparse
import json
from pathlib import Path

from alphafactory_crypto.broad_search.behavior_provenance_census import (
    write_behavior_provenance_census,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consume persisted behavior provenance without market replay."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    result = write_behavior_provenance_census(
        args.repo_root.resolve(),
        ledger_path=args.ledger.resolve(),
        output_root=args.output_root.resolve(),
    )
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
