#!/usr/bin/env python3
"""CLI for the bounded development-only CEM diversity A/B."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from alphafactory_crypto.instrument_canary.cem_diversity_runner import (
    INVALID,
    MIXED,
    NO_IMPROVEMENT,
    QUALIFIED,
    build_evidence,
    check_evidence,
    validate_experiment_contract,
)

DEFAULT_CONFIG = REPO_ROOT / "config" / "crypto_cem_diversity_ab_v1.json"
DEFAULT_GRAPH_SKILL_ROOT = (
    Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    / "skills"
    / "gsd-graphify-runtime-fidelity"
)


def _load_trace_module(skill_root: Path):
    path = skill_root / "scripts" / "runtime_trace.py"
    spec = importlib.util.spec_from_file_location("cem_diversity_runtime_trace", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load runtime tracer: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip().lower()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("contract", "build", "check", "replay"))
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--source-sha")
    parser.add_argument("--runtime-trace", type=Path)
    parser.add_argument("--graph-skill-root", type=Path, default=DEFAULT_GRAPH_SKILL_ROOT)
    args = parser.parse_args()
    config_path = args.config.resolve()
    if args.command == "contract":
        payload = validate_experiment_contract(
            REPO_ROOT, json.loads(config_path.read_text(encoding="utf-8"))
        )
        payload.pop("base_config", None)
    elif args.command in {"check", "replay"}:
        payload = check_evidence(REPO_ROOT, config_path=config_path)
    elif args.runtime_trace is None:
        payload = build_evidence(
            REPO_ROOT, config_path=config_path, source_sha=args.source_sha
        )
    else:
        source_sha = (args.source_sha or _sha()).lower()
        tracer = _load_trace_module(args.graph_skill_root.resolve())
        with tracer.ExecutionTrace(
            project_root=REPO_ROOT,
            run_id=f"crypto-cem-diversity-ab-20260715-{source_sha[:12]}",
            entrypoint="scripts/crypto_cem_diversity_ab.py",
            profile_id="crypto-cem-diversity-ab",
            output_path=args.runtime_trace.resolve(),
        ) as runtime_trace:
            tracer_path = Path(tracer.__file__).resolve()
            skill_path = args.graph_skill_root.resolve() / "SKILL.md"
            runtime_trace.payload["tracer_authority"] = {
                "runtime_trace_path": str(tracer_path),
                "runtime_trace_sha256": hashlib.sha256(tracer_path.read_bytes()).hexdigest().upper(),
                "skill_path": str(skill_path),
                "skill_sha256": hashlib.sha256(skill_path.read_bytes()).hexdigest().upper(),
            }
            payload = build_evidence(
                REPO_ROOT,
                config_path=config_path,
                source_sha=source_sha,
                runtime_trace=runtime_trace,
            )
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    if args.command == "build":
        return 0 if payload.get("status") in {QUALIFIED, MIXED, NO_IMPROVEMENT} else 1
    if args.command == "contract":
        return 0 if payload.get("result") == "PASS" else 1
    return 0 if payload.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
