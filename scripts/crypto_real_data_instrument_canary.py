#!/usr/bin/env python3
"""CLI for the bounded existing-release real-data instrument canary."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import psutil

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from alphafactory_crypto.instrument_canary.grammar import FrozenGrammar
from alphafactory_crypto.instrument_canary.release import load_development_release
from alphafactory_crypto.instrument_canary.runner import (
    QUALIFIED,
    build_evidence,
    check_evidence,
    run_cost_preflight,
    validate_frozen_canary_contract,
)


DEFAULT_CONFIG = REPO_ROOT / "config" / "crypto_real_data_instrument_canary_v1.json"


def _config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip().lower()


def _print(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))


def command_contract(config_path: Path) -> dict:
    return validate_frozen_canary_contract(_config(config_path), FrozenGrammar.default())


def command_preflight(config_path: Path, source_sha: str | None) -> dict:
    config = _config(config_path)
    grammar = FrozenGrammar.default()
    validate_frozen_canary_contract(config, grammar)
    source_sha = (source_sha or _sha()).lower()
    if source_sha != _sha():
        raise ValueError("preflight source SHA must equal current HEAD")
    process = psutil.Process(os.getpid())
    rss_before = process.memory_info().rss
    started = time.perf_counter()
    panel = load_development_release(config)
    load_seconds = time.perf_counter() - started
    preflight = run_cost_preflight(
        panel,
        grammar=grammar,
        config=config,
        source_sha=source_sha,
        release_load_seconds=load_seconds,
        release_load_rss_delta_bytes=process.memory_info().rss - rss_before,
    )
    return {key: value for key, value in preflight.payload.items() if key != "rows"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("contract", "preflight", "build", "check", "replay"))
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--source-sha")
    args = parser.parse_args()
    config_path = args.config.resolve()
    if args.command == "contract":
        result = command_contract(config_path)
    elif args.command == "preflight":
        result = command_preflight(config_path, args.source_sha)
    elif args.command == "build":
        result = build_evidence(
            REPO_ROOT, config_path=config_path, source_sha=args.source_sha
        )
    else:
        # check includes hash verification and policy-only transcript replay;
        # replay is retained as a convenient explicit maintenance entry.
        result = check_evidence(REPO_ROOT, config_path=config_path)
    _print(result)
    if args.command == "build":
        return 0 if result.get("status") == QUALIFIED else 1
    return 0 if result.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
