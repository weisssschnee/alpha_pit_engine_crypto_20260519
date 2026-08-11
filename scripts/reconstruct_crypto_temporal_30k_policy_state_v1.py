from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from alphafactory_crypto.broad_search.temporal_prefix_reconstruction_v1 import (
    reconstruct_prefix_policy_state,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    result = reconstruct_prefix_policy_state(
        args.artifact_root,
        output_root=args.output_root,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PREFIX_POLICY_STATE_RECONSTRUCTION_PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
