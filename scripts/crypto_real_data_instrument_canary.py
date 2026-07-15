#!/usr/bin/env python3
"""CLI for the bounded existing-release real-data instrument canary."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
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
    PARTIAL,
    QUALIFIED,
    build_evidence,
    check_evidence,
    finalize_graph_qualification,
    run_cost_preflight,
    validate_frozen_canary_contract,
)


DEFAULT_CONFIG = REPO_ROOT / "config" / "crypto_real_data_instrument_canary_v1.json"
DEFAULT_GRAPH_SKILL_ROOT = (
    Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    / "skills"
    / "gsd-graphify-runtime-fidelity"
)


def _config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip().lower()


def _print(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))


def _load_runtime_trace(skill_root: Path):
    path = skill_root / "scripts" / "runtime_trace.py"
    if not path.is_file():
        raise FileNotFoundError(f"GraphSkill runtime tracer missing: {path}")
    spec = importlib.util.spec_from_file_location("graphskill_runtime_trace", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load runtime tracer: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


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
    parser.add_argument(
        "command",
        choices=("contract", "preflight", "build", "finalize-graph", "check", "replay"),
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--source-sha")
    parser.add_argument("--runtime-trace", type=Path)
    parser.add_argument("--graph-skill-root", type=Path, default=DEFAULT_GRAPH_SKILL_ROOT)
    args = parser.parse_args()
    config_path = args.config.resolve()
    if args.command == "contract":
        result = command_contract(config_path)
    elif args.command == "preflight":
        result = command_preflight(config_path, args.source_sha)
    elif args.command == "build":
        if args.runtime_trace is None:
            result = build_evidence(
                REPO_ROOT, config_path=config_path, source_sha=args.source_sha
            )
        else:
            source_sha = (args.source_sha or _sha()).lower()
            output_path = args.runtime_trace.resolve()
            tracer = _load_runtime_trace(args.graph_skill_root.resolve())
            with tracer.ExecutionTrace(
                project_root=REPO_ROOT,
                run_id=f"crypto-real-data-instrument-canary-20260715-{source_sha[:12]}",
                entrypoint="scripts/crypto_real_data_instrument_canary.py",
                profile_id="crypto-real-data-instrument-canary",
                output_path=output_path,
            ) as runtime_trace:
                tracer_path = Path(tracer.__file__).resolve()
                skill_path = (args.graph_skill_root.resolve() / "SKILL.md")
                runtime_trace.payload["tracer_authority"] = {
                    "runtime_trace_path": str(tracer_path),
                    "runtime_trace_sha256": _sha256(tracer_path),
                    "skill_path": str(skill_path),
                    "skill_sha256": _sha256(skill_path),
                }
                result = build_evidence(
                    REPO_ROOT,
                    config_path=config_path,
                    source_sha=source_sha,
                    runtime_trace=runtime_trace,
                )
    elif args.command == "finalize-graph":
        if args.runtime_trace is None:
            parser.error("finalize-graph requires --runtime-trace")
        result = finalize_graph_qualification(
            REPO_ROOT,
            config_path=config_path,
            trace_path=args.runtime_trace.resolve(),
        )
    else:
        # check includes hash verification and policy-only transcript replay;
        # replay is retained as a convenient explicit maintenance entry.
        result = check_evidence(REPO_ROOT, config_path=config_path)
    _print(result)
    if args.command == "build":
        return 0 if result.get("status") in {PARTIAL, QUALIFIED} else 1
    return 0 if result.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
