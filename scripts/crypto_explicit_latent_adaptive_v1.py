from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from alphafactory_crypto.latent_adaptive import run_experiment


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="config/crypto_explicit_latent_adaptive_v1.json",
    )
    parser.add_argument("--stage", choices=("stage0", "all"), default="all")
    args = parser.parse_args()
    repo_root = REPO_ROOT
    decision = run_experiment(
        repo_root,
        repo_root / args.config,
        stage=args.stage,
    )
    print(decision["status"])


if __name__ == "__main__":
    main()
