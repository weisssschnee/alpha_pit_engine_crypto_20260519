#!/usr/bin/env python3
"""Qualify the completed policy canary without rewriting producer evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from alphafactory_crypto.broad_search.policy_upgrade_canary import check_canary
from alphafactory_crypto.instrument_canary.release import sha256_file

CONFIG = REPO_ROOT / "config" / "crypto_policy_upgrade_canary_v1.json"
ORIGINAL_ROOT = REPO_ROOT / "runtime" / "crypto_policy_upgrade_canary_v1_20260720"
OUTPUT_ROOT = (
    REPO_ROOT
    / "runtime"
    / "crypto_policy_upgrade_canary_v1_20260720_qualification_supersession_v1"
)
OUTPUT_JSON = OUTPUT_ROOT / "QUALIFICATION_SUPERSESSION.json"
OUTPUT_MANIFEST = OUTPUT_ROOT / "manifest.json"
OUTPUT_REPORT = REPO_ROOT / "reports" / "CRYPTO_POLICY_UPGRADE_CANARY_V1_QUALIFICATION_SUPERSESSION.md"
EXPECTED_DIAGNOSTICS = (
    "evolutionary:20260716:FAMILY_COVERAGE",
    "evolutionary:20260717:FAMILY_COVERAGE",
)
EXPECTED_POSITIVE = {"cem_distribution_v1": 4, "evolutionary_typed_v1": 3}


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _payload_sha(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest().upper()


def qualify_audit(audit: Mapping[str, Any], config: Mapping[str, Any]) -> dict[str, Any]:
    errors = tuple(audit.get("implementation_errors", ()))
    if errors != EXPECTED_DIAGNOSTICS:
        raise ValueError(f"unexpected implementation errors: {errors}")

    seeds = tuple(int(seed) for seed in config["budget"]["seeds"])
    expected_lane_errors = {
        ("evolutionary", 20260716): ("FAMILY_COVERAGE",),
        ("evolutionary", 20260717): ("FAMILY_COVERAGE",),
    }
    lanes = audit.get("lane_summaries", ())
    if len(lanes) != 20:
        raise ValueError("expected 20 completed lane summaries")
    if {(str(row["policy"]), int(row["seed"])) for row in lanes} != {
        (str(policy), seed) for policy in config["budget"]["policies"] for seed in seeds
    }:
        raise ValueError("lane identity mismatch")
    for lane in lanes:
        key = (str(lane["policy"]), int(lane["seed"]))
        observed = tuple(lane.get("implementation_errors", ()))
        if observed != expected_lane_errors.get(key, ()):
            raise ValueError(f"unexpected lane diagnostics: {key}={observed}")

    required = int(config["qualification"]["minimum_positive_seed_count"])
    comparisons = audit.get("matched_seed_comparisons", {})
    decisions: dict[str, Any] = {}
    for policy, expected_count in EXPECTED_POSITIVE.items():
        rows = comparisons.get(policy, ())
        if tuple(int(row["seed"]) for row in rows) != seeds:
            raise ValueError(f"matched seed identity mismatch: {policy}")
        positive = 0
        for row in rows:
            recomputed = all(
                float(row[key]) > 0.0
                for key in (
                    "mean_margin_vs_random", "top_mean_margin_vs_random",
                    "mean_margin_vs_lite", "top_mean_margin_vs_lite",
                )
            )
            if bool(row.get("jointly_positive")) != recomputed:
                raise ValueError(f"joint comparison flag mismatch: {policy}:{row['seed']}")
            positive += int(recomputed)
        if positive != expected_count:
            raise ValueError(f"unexpected positive seed count: {policy}={positive}")
        decisions[policy] = {
            "decision": (
                "KEEP_FOR_FUTURE_NEW_DATA_ARENA"
                if positive >= required
                else "EVICT_EXPERIMENTAL_UPGRADE"
            ),
            "implementation_valid": True,
            "matched_seed_count": len(rows),
            "positive_seed_count_vs_random_and_lite": positive,
            "required_positive_seed_count": required,
        }
    return decisions


def _qualification(source_sha: str, created_at: str) -> dict[str, Any]:
    config = _read(CONFIG)
    audit = _read(ORIGINAL_ROOT / "POLICY_UPGRADE_BEHAVIOR_AUDIT.json")
    original_decision = _read(ORIGINAL_ROOT / "POLICY_UPGRADE_DECISION.json")
    original_manifest = _read(ORIGINAL_ROOT / "manifest.json")
    if original_decision.get("main_status") != "POLICY_UPGRADE_CANARY_IMPLEMENTATION_FAILED":
        raise ValueError("original fail-closed decision changed")
    if any(
        value.get("invalidation_reason") != "GLOBAL_IMPLEMENTATION_OR_RESOURCE_GATE_FAILED"
        for value in original_decision.get("upgrade_decisions", {}).values()
    ):
        raise ValueError("original global invalidation identity changed")
    pair = next(
        row for row in original_manifest["artifacts"]
        if row["path"].endswith("POLICY_UPGRADE_PAIR_RESULTS.parquet")
    )
    return {
        "schema_version": 1,
        "status": "POLICY_UPGRADE_CANARY_QUALIFIED",
        "created_at": created_at,
        "qualifier_source_sha": source_sha,
        "supersession_reason": "LITE_CONTROL_FAMILY_COVERAGE_DIAGNOSTICS_WERE_INCORRECTLY_GLOBALIZED",
        "original_evidence": {
            "manifest_path": ORIGINAL_ROOT.relative_to(REPO_ROOT).as_posix() + "/manifest.json",
            "manifest_sha256": sha256_file(ORIGINAL_ROOT / "manifest.json"),
            "bundle_sha256": original_manifest["bundle_sha256"],
            "producer_source_sha": original_manifest["producer_source_sha"],
            "pair_artifact_sha256": pair["sha256"],
        },
        "nonblocking_control_diagnostics": list(EXPECTED_DIAGNOSTICS),
        "upgrade_decisions": qualify_audit(audit, config),
        "pair_evaluations_rerun": 0,
        "sealed_reads": 0,
        "report_only_reads": 0,
        "forward_reads": 0,
        "candidate_promotion": "FORBIDDEN",
        "cross_sprint_adaptive_memory": "FORBIDDEN",
        "claim_scope": "SPENT_DEVELOPMENT_POLICY_PRODUCTIVITY_DIRECTION_ONLY",
    }


def _report(value: Mapping[str, Any]) -> str:
    decisions = value["upgrade_decisions"]
    return "\n".join(
        [
            "# Crypto Policy Upgrade Qualification Supersession",
            "",
            f"Status: `{value['status']}`",
            "",
            "The completed 2,560-pair producer evidence is preserved unchanged. Two known",
            "`FAMILY_COVERAGE` diagnostics belong only to the lite evolutionary control and",
            "do not invalidate the reference or either real upgraded policy.",
            "",
            "## Qualified decisions",
            "",
            *[
                f"- `{name}`: `{row['decision']}` ({row['positive_seed_count_vs_random_and_lite']}/4 matched seeds)"
                for name, row in decisions.items()
            ],
            "",
            "No pair was rerun. This is spent-development policy-productivity evidence only;",
            "it does not establish alpha, OOS validity, forward authority, or promotion eligibility.",
            "",
        ]
    )


def _commit_exists(sha: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    ).returncode == 0


def build(source_sha: str | None = None) -> dict[str, Any]:
    original = check_canary(REPO_ROOT, config_path=CONFIG)
    if original.get("result") != "PASS":
        return {"result": "FAIL", "errors": ["original evidence: " + str(original)]}
    source_ref = source_sha or "HEAD"
    source_sha = subprocess.check_output(
        ["git", "rev-parse", f"{source_ref}^{{commit}}"], cwd=REPO_ROOT, text=True
    ).strip()
    if not _commit_exists(source_sha):
        return {"result": "FAIL", "errors": ["qualifier source commit missing"]}
    value = _qualification(source_sha, datetime.now(timezone.utc).isoformat())
    _write(OUTPUT_JSON, value)
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_REPORT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(_report(value))
    artifacts = [
        {"path": p.relative_to(REPO_ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha256_file(p)}
        for p in (OUTPUT_JSON, OUTPUT_REPORT)
    ]
    _write(OUTPUT_MANIFEST, {
        "schema_version": 1, "qualifier_source_sha": source_sha,
        "original_bundle_sha256": value["original_evidence"]["bundle_sha256"],
        "artifacts": artifacts, "bundle_sha256": _payload_sha(artifacts),
    })
    return check()


def check() -> dict[str, Any]:
    errors: list[str] = []
    original = check_canary(REPO_ROOT, config_path=CONFIG)
    if original.get("result") != "PASS":
        errors.append("original_evidence")
    try:
        manifest, value = _read(OUTPUT_MANIFEST), _read(OUTPUT_JSON)
        expected = _qualification(value["qualifier_source_sha"], value["created_at"])
        if value != expected:
            errors.append("qualification")
        if not _commit_exists(value["qualifier_source_sha"]):
            errors.append("qualifier_source_sha")
        paths = [OUTPUT_JSON, OUTPUT_REPORT]
        artifacts = [
            {"path": p.relative_to(REPO_ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha256_file(p)}
            for p in paths
        ]
        if manifest.get("artifacts") != artifacts or manifest.get("bundle_sha256") != _payload_sha(artifacts):
            errors.append("manifest")
        if OUTPUT_REPORT.read_text(encoding="utf-8") != _report(value):
            errors.append("report")
    except (KeyError, StopIteration, ValueError, OSError, json.JSONDecodeError) as exc:
        errors.append(type(exc).__name__ + ":" + str(exc))
    return {
        "result": "PASS" if not errors else "FAIL", "errors": errors,
        "status": None if errors else value["status"],
        "upgrade_decisions": {} if errors else value["upgrade_decisions"],
        "pair_evaluations_rerun": None if errors else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "check"))
    parser.add_argument("--source-sha")
    args = parser.parse_args()
    result = build(args.source_sha) if args.command == "build" else check()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
