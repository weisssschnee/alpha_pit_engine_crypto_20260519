from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alphafactory_crypto.broad_search.temporal_representation_analysis_v1 import (
    build_final_analysis,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--decision", required=True)
    parser.add_argument("--rationale", action="append", default=[])
    args = parser.parse_args()
    result = build_final_analysis(
        args.repo_root,
        args.runtime_root,
        decision=args.decision,
        rationale=args.rationale,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
