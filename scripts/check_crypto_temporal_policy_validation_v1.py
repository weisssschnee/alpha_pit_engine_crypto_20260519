"""Independent entry point for the Temporal Policy Validation V1 checker."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from alphafactory_crypto.broad_search.temporal_policy_validation_v1 import check_gate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-date", default="20260812")
    parser.add_argument(
        "--receipt-path",
        default="config/crypto_temporal_policy_validation_v1_authorization.json",
    )
    args = parser.parse_args()
    result = check_gate(
        args.repo_root,
        runtime_date=args.runtime_date,
        receipt_path=args.receipt_path,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
