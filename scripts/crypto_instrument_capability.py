from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import math
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphafactory_crypto.instrument_capability.evidence_feedback import (  # noqa: E402
    capability_matrix_rows,
    planted_result_rows,
    proxy_strict_alignment_payload,
)
from alphafactory_crypto.instrument_capability.evidence_mapping import (  # noqa: E402
    mapping_cost_counterfactual_payload,
    mapping_synthetic_behavior_payload,
    mapping_turnover_rows,
)
from alphafactory_crypto.instrument_capability.evidence_primitives import (  # noqa: E402
    implementation_authority_rows,
    legacy_compatibility_rows,
    primitive_synthetic_parity_payload,
)
from alphafactory_crypto.instrument_capability.feedback import (  # noqa: E402
    feedback_contract_payload,
)
from alphafactory_crypto.instrument_capability.harness import (  # noqa: E402
    FAMILY_IDS,
    run_qualification,
)
from alphafactory_crypto.instrument_capability.legacy import (  # noqa: E402
    CLOSURE_TAG,
    EXPECTED_CLOSURE_SHA,
)
from alphafactory_crypto.instrument_capability.mapping import (  # noqa: E402
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    SPARSE_EVENT_OR_CARRY,
    TIME_SERIES_DIRECTIONAL_STATEFUL,
    mapping_contract_payload,
)
from alphafactory_crypto.instrument_capability.primitives import (  # noqa: E402
    CANONICAL_PRIMITIVES,
    primitive_contract_payload,
)
from alphafactory_crypto.instrument_capability.search import (  # noqa: E402
    B1S_LABELS_DEGENERATE,
    POLICY_BEHAVIOR,
    SUPPORTED_ALGORITHMS,
)


OUT = ROOT / "runtime" / "crypto_instrument_capability_20260715"
REPORT = ROOT / "reports" / "CRYPTO_INSTRUMENT_CAPABILITY_REPORT.md"
MANIFEST = OUT / "manifest.json"
SEEDS = (20260715, 20260716)
SEARCH_BUDGET = 27
REPAIR_BRANCH = "repair/crypto-instrument-capability-20260715"
FINAL_STATUS_QUALIFIED = "CRYPTO_INTERNAL_SEARCH_INSTRUMENT_CAPABILITY_QUALIFIED"
FINAL_STATUS_PARTIAL = "CRYPTO_INTERNAL_SEARCH_INSTRUMENT_PARTIALLY_QUALIFIED"

SOURCE_PATHS = (
    "alphafactory_crypto/instrument_capability/__init__.py",
    "alphafactory_crypto/instrument_capability/primitives.py",
    "alphafactory_crypto/instrument_capability/mapping.py",
    "alphafactory_crypto/instrument_capability/feedback.py",
    "alphafactory_crypto/instrument_capability/evaluator.py",
    "alphafactory_crypto/instrument_capability/legacy.py",
    "alphafactory_crypto/instrument_capability/search.py",
    "alphafactory_crypto/instrument_capability/harness.py",
    "alphafactory_crypto/instrument_capability/evidence_primitives.py",
    "alphafactory_crypto/instrument_capability/evidence_mapping.py",
    "alphafactory_crypto/instrument_capability/evidence_feedback.py",
    "scripts/crypto_instrument_capability.py",
    "tests/test_instrument_capability_primitives_mapping.py",
    "tests/test_instrument_capability_harness.py",
    "tests/test_instrument_capability_reproducer.py",
    "docs/adr/0002-capability-only-search-instrument-authority.md",
)

CAPABILITY_EXECUTION_PATHS = (
    "alphafactory_crypto/instrument_capability/primitives.py",
    "alphafactory_crypto/instrument_capability/mapping.py",
    "alphafactory_crypto/instrument_capability/feedback.py",
    "alphafactory_crypto/instrument_capability/evaluator.py",
    "alphafactory_crypto/instrument_capability/search.py",
    "alphafactory_crypto/instrument_capability/harness.py",
)

FORBIDDEN_EXECUTION_IMPORT_ROOTS = {
    "boto3",
    "duckdb",
    "fsspec",
    "os",
    "pandas",
    "pathlib",
    "polars",
    "pyarrow",
    "requests",
    "socket",
    "sqlalchemy",
    "subprocess",
    "urllib",
}
FORBIDDEN_EXECUTION_CALLS = {
    "__import__",
    "compile",
    "eval",
    "exec",
    "fetch",
    "load",
    "open",
    "read_bytes",
    "read_csv",
    "read_json",
    "read_parquet",
    "read_text",
    "urlopen",
}

BOUNDARIES: Mapping[str, bool] = {
    "new_performance_search_run": False,
    "sealed_data_read": False,
    "forward_opened": False,
    "challenge_opened": False,
    "recent_opened": False,
    "may_stress_opened": False,
    "new_data_integrated": False,
    "candidate_promoted": False,
    "cross_sprint_adaptive_memory_written": False,
    "historical_frontier_closure_rewritten": False,
}

ARTIFACT_NAMES = (
    "CRYPTO_CANONICAL_PRIMITIVE_CONTRACT.json",
    "CRYPTO_PRIMITIVE_IMPLEMENTATION_AUTHORITY.csv",
    "CRYPTO_PRIMITIVE_SYNTHETIC_PARITY.json",
    "CRYPTO_PORTFOLIO_MAPPING_CONTRACT.json",
    "CRYPTO_MAPPING_SYNTHETIC_BEHAVIOR.json",
    "CRYPTO_MAPPING_TURNOVER_DECOMPOSITION.csv",
    "CRYPTO_MAPPING_COST_COUNTERFACTUAL.json",
    "CRYPTO_ADAPTIVE_FEEDBACK_CONTRACT.json",
    "CRYPTO_PROXY_STRICT_ALIGNMENT_SYNTHETIC.json",
    "CRYPTO_INSTRUMENT_CAPABILITY_MATRIX.csv",
    "CRYPTO_PLANTED_MECHANISM_RESULTS.csv",
    "CRYPTO_INSTRUMENT_CAPABILITY_QUALIFICATION.json",
    "CRYPTO_LEGACY_SEMANTIC_COMPATIBILITY.csv",
)


def _git(*args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=not binary,
        encoding=None if binary else "utf-8",
        errors=None if binary else "strict",
    )
    if binary:
        return result.stdout
    return str(result.stdout).strip()


def _require_full_source_sha(value: str) -> str:
    source_sha = str(value).strip().lower()
    if re.fullmatch(r"[0-9a-f]{40}", source_sha) is None:
        raise ValueError(
            "--source-sha must be an explicit full 40-character commit SHA; "
            "symbolic and abbreviated refs are forbidden"
        )
    resolved = _git("rev-parse", f"{source_sha}^{{commit}}")
    if resolved != source_sha:
        raise RuntimeError(f"source commit identity drift: {resolved} != {source_sha}")
    return source_sha


def _verify_source_branch(source_sha: str) -> None:
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if branch != REPAIR_BRANCH:
        raise RuntimeError(f"expected branch {REPAIR_BRANCH}, observed {branch}")
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", source_sha, "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"source commit {source_sha} is not an ancestor of current {REPAIR_BRANCH} HEAD"
        )


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def _clean(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(item) for item in value]
    if hasattr(value, "tolist"):
        return _clean(value.tolist())
    if hasattr(value, "item"):
        return _clean(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _json_bytes(value: Any) -> bytes:
    text = json.dumps(
        _clean(value),
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    )
    return (text + "\n").encode("utf-8")


def _csv_cell(value: Any) -> Any:
    value = _clean(value)
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    return value


def _csv_bytes(rows: Sequence[Mapping[str, Any]]) -> bytes:
    if not rows:
        raise ValueError("CSV evidence cannot be empty")
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(str(key))
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: _csv_cell(row.get(key)) for key in fieldnames})
    return buffer.getvalue().encode("utf-8")


def _provenance(source_sha: str) -> dict[str, Any]:
    return {
        "repo_ref": f"{REPAIR_BRANCH}@{source_sha}",
        "verified_branch": REPAIR_BRANCH,
        "source_commit_sha": source_sha,
        "accepted_closure_tag": CLOSURE_TAG,
        "accepted_closure_sha": EXPECTED_CLOSURE_SHA,
        "evidence_scope": "DETERMINISTIC_SYNTHETIC_CAPABILITY_ONLY",
        "market_data_read": False,
        "sealed_data_read": False,
        "economic_increment_claimed": False,
    }


def _with_provenance(payload: Mapping[str, Any], source_sha: str) -> dict[str, Any]:
    result = dict(payload)
    result["provenance"] = _provenance(source_sha)
    return result


def _rows_with_provenance(
    rows: Sequence[Mapping[str, Any]], source_sha: str
) -> list[dict[str, Any]]:
    provenance = _provenance(source_sha)
    return [{**row, **provenance} for row in rows]


def _source_inventory(source_sha: str) -> list[dict[str, Any]]:
    if _git("cat-file", "-t", source_sha) != "commit":
        raise RuntimeError(f"source SHA is not a commit: {source_sha}")
    inventory: list[dict[str, Any]] = []
    for relative in SOURCE_PATHS:
        current = (ROOT / relative).read_bytes()
        committed = _git("show", f"{source_sha}:{relative}", binary=True)
        assert isinstance(committed, bytes)
        if current != committed:
            raise RuntimeError(
                f"source file differs from bound commit {source_sha}: {relative}"
            )
        inventory.append(
            {
                "path": relative,
                "git_blob": _git("rev-parse", f"{source_sha}:{relative}"),
                "sha256": _sha256(current),
                "bytes": len(current),
            }
        )
    return inventory


def _execution_boundary_receipt(
    source_sha: str, harness: Mapping[str, Any]
) -> dict[str, Any]:
    """Statically close the capability runner's input surface.

    This is intentionally not presented as a formal runtime trace.  It proves
    that the executed qualification path has no filesystem, network, process,
    database, or market-data import/call surface and that the observed payload
    is the fixed synthetic grammar run.
    """

    files: list[dict[str, Any]] = []
    allowed_local_modules = {Path(path).stem for path in CAPABILITY_EXECUTION_PATHS}
    all_forbidden_imports: list[str] = []
    all_forbidden_calls: list[str] = []
    for relative in CAPABILITY_EXECUTION_PATHS:
        payload = (ROOT / relative).read_bytes()
        committed = _git("show", f"{source_sha}:{relative}", binary=True)
        assert isinstance(committed, bytes)
        if payload != committed:
            raise RuntimeError(
                f"capability execution file differs from bound commit: {relative}"
            )
        tree = ast.parse(payload.decode("utf-8"), filename=relative)
        imports: set[str] = set()
        calls: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(item.name.split(".", 1)[0] for item in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".", 1)[0]
                if node.level == 0:
                    imports.add(root)
                elif root not in allowed_local_modules:
                    imports.add(f"FORBIDDEN_LOCAL:{root}")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.add(node.func.attr)
        forbidden_imports = sorted(
            (imports & FORBIDDEN_EXECUTION_IMPORT_ROOTS)
            | {name for name in imports if name.startswith("FORBIDDEN_LOCAL:")}
        )
        forbidden_calls = sorted(calls & FORBIDDEN_EXECUTION_CALLS)
        all_forbidden_imports.extend(f"{relative}:{name}" for name in forbidden_imports)
        all_forbidden_calls.extend(f"{relative}:{name}" for name in forbidden_calls)
        files.append(
            {
                "path": relative,
                "sha256": _sha256(payload),
                "imports": sorted(imports),
                "forbidden_imports": forbidden_imports,
                "forbidden_calls": forbidden_calls,
            }
        )

    observed_families = set(harness.get("families", []))
    observed_algorithms = set(harness.get("algorithms", []))
    observed_seeds = tuple(harness.get("seeds", []))
    runs = list(harness.get("runs", []))
    candidate_records = [
        candidate
        for run in runs
        for candidate in run.get("candidates", {}).values()
    ]
    candidate_contract_pass = bool(
        candidate_records
        and all(
            str(candidate.get("candidate_id", "")).startswith("proposal-grammar:")
            and candidate.get("candidate_id")
            == candidate.get("proposal_receipt", {}).get("grammar_identity")
            and candidate.get("admission_receipt", {}).get("grammar", {}).get("result")
            == "PASS"
            for candidate in candidate_records
        )
    )
    synthetic_run_shape_pass = bool(
        "synthetic" in str(harness.get("scope", "")).lower()
        and observed_families == set(FAMILY_IDS)
        and observed_algorithms == set(SUPPORTED_ALGORITHMS)
        and observed_seeds == SEEDS
        and len(runs) == len(FAMILY_IDS) * len(SEEDS)
        and candidate_contract_pass
    )
    closed_input_surface_pass = not all_forbidden_imports and not all_forbidden_calls
    return {
        "schema_version": 1,
        "assurance_level": "STATIC_VERIFIED_CLOSED_INPUT_SURFACE",
        "formal_runtime_trace_supplied": False,
        "source_commit_sha": source_sha,
        "execution_files": files,
        "forbidden_import_roots": sorted(FORBIDDEN_EXECUTION_IMPORT_ROOTS),
        "forbidden_call_names": sorted(FORBIDDEN_EXECUTION_CALLS),
        "forbidden_import_findings": all_forbidden_imports,
        "forbidden_call_findings": all_forbidden_calls,
        "closed_input_surface_result": "PASS"
        if closed_input_surface_pass
        else "FAIL",
        "synthetic_run_shape_result": "PASS" if synthetic_run_shape_pass else "FAIL",
        "sealed_data_read_result": "PASS"
        if closed_input_surface_pass and synthetic_run_shape_pass
        else "FAIL",
        "real_performance_search_result": "PASS"
        if closed_input_surface_pass and synthetic_run_shape_pass
        else "FAIL",
        "observed_run_kind": "FIXED_SYNTHETIC_FINITE_GRAMMAR_CAPABILITY",
        "allowed_infrastructure_reads_outside_execution_path": [
            "current committed source files for content identity",
            "three exact accepted-closure Python blobs for legacy semantic parity",
        ],
        "conclusion_boundary": "Static closed-input assurance; not a formal GraphSkill runtime trace and not economic evidence",
    }


def _two_fixed_seed_reproduction_pass(harness: Mapping[str, Any]) -> bool:
    cross_seed = harness.get("cross_seed_reproduction", {})
    return bool(
        harness.get("minimum_distinct_seed_count_met")
        and int(harness.get("distinct_seed_count", 0)) >= 2
        and harness.get("cross_seed_qualified")
        and cross_seed
        and all(
            bool(row.get("canonical_mechanism_reproduction"))
            and bool(row.get("behavior_reproduction"))
            for row in cross_seed.values()
        )
    )


def _qualification_criteria(
    primitive_parity: Mapping[str, Any],
    mapping_behavior: Mapping[str, Any],
    alignment: Mapping[str, Any],
    harness: Mapping[str, Any],
    boundary_receipt: Mapping[str, Any],
) -> list[dict[str, Any]]:
    run_checks = [row["qualification_checks"] for row in harness["runs"]]
    cross_seed = harness["cross_seed_reproduction"]
    primitive_rows = list(primitive_parity.get("primitives", []))
    observed_primitive_ids = [str(row.get("primitive_id", "")) for row in primitive_rows]
    observed_behavior_ids = [str(row.get("behavior_identity", "")) for row in primitive_rows]
    mapping_ids = {
        row["family_contract"]["portfolio_mapping_id"] for row in harness["runs"]
    }
    expected_mapping_ids = {
        CROSS_SECTIONAL_ZERO_NET,
        TIME_SERIES_DIRECTIONAL_STATEFUL,
        SPARSE_EVENT_OR_CARRY,
    }
    required_decoys = (
        "positive_candidate_ranks_above_matched_null",
        "wrong_lag_rejected_before_strict",
        "high_cost_decoy_rejected_or_downgraded",
        "high_concentration_decoy_rejected_or_downgraded",
        "single_time_block_decoy_rejected_or_downgraded",
        "negative_benchmark_increment_decoy_rejected_or_downgraded",
        "mapping_mismatch_rejected_or_downgraded",
        "primitive_alias_rejected_before_strict",
    )
    grammar_discovery_and_retention = all(
        bool(row.get("proposal_generated_from_frozen_grammar"))
        and bool(row.get("positive_candidate_reachable"))
        and bool(row.get("mapping_preserves_intended_information"))
        and bool(row.get("positive_candidate_survives"))
        and bool(row.get("survivor_selected_only_from_visited_feedback"))
        for row in run_checks
    )
    distinct_search_behavior = all(
        len(
            {
                search.get("behavior_hash")
                for search in run.get("searches", {}).values()
            }
        )
        == len(SUPPORTED_ALGORITHMS)
        and all(
            bool(search.get("independent_behavior"))
            for search in run.get("searches", {}).values()
        )
        for run in harness.get("runs", [])
    )
    checks = [
        (
            "UNIQUE_CANONICAL_SEMANTICS",
            set(observed_primitive_ids) == set(CANONICAL_PRIMITIVES)
            and len(observed_primitive_ids) == 13
            and len(set(observed_behavior_ids)) == 13
            and all(observed_behavior_ids),
            "CRYPTO_PRIMITIVE_SYNTHETIC_PARITY.json",
        ),
        (
            "PRIMITIVE_SYNTHETIC_TESTS_PASS",
            primitive_parity.get("primitive_count") == 13
            and primitive_parity.get("overall_result") == "PASS",
            "CRYPTO_PRIMITIVE_SYNTHETIC_PARITY.json",
        ),
        (
            "THREE_EXPLICIT_MAPPINGS_PASS",
            mapping_ids == expected_mapping_ids
            and bool(mapping_behavior.get("all_checks_pass")),
            "CRYPTO_MAPPING_SYNTHETIC_BEHAVIOR.json",
        ),
        (
            "FINAL_POSITION_CAP_HOLDS",
            bool(
                mapping_behavior.get("checks", {}).get(
                    "final_position_cap_holds_all_mappings"
                )
            ),
            "CRYPTO_MAPPING_SYNTHETIC_BEHAVIOR.json",
        ),
        (
            "ALIGNED_FEEDBACK_REJECTS_MAJOR_DECOYS",
            not alignment.get("aggregate", {}).get(
                "decoys_still_fooling_aligned_feedback", ["MISSING"]
            ),
            "CRYPTO_PROXY_STRICT_ALIGNMENT_SYNTHETIC.json",
        ),
        (
            "SEVEN_PLANTED_FAMILIES_DISCOVERED_MAPPED_RETAINED",
            set(harness.get("families", [])) == set(FAMILY_IDS)
            and len(FAMILY_IDS) == 7
            and bool(harness.get("all_runs_qualified"))
            and grammar_discovery_and_retention
            and distinct_search_behavior,
            "CRYPTO_INSTRUMENT_CAPABILITY_MATRIX.csv",
        ),
        (
            "NULL_WRONG_LAG_MAPPING_MISMATCH_HIGH_COST_HANDLED",
            all(all(bool(row.get(key)) for key in required_decoys) for row in run_checks),
            "CRYPTO_PLANTED_MECHANISM_RESULTS.csv",
        ),
        (
            "TWO_FIXED_SEEDS_REPRODUCE_CANONICAL_MECHANISM",
            _two_fixed_seed_reproduction_pass(harness),
            "CRYPTO_INSTRUMENT_CAPABILITY_QUALIFICATION.json",
        ),
        (
            "NO_SEALED_DATA_READ",
            boundary_receipt.get("sealed_data_read_result") == "PASS",
            "CRYPTO_INSTRUMENT_CAPABILITY_QUALIFICATION.json",
        ),
        (
            "NO_REAL_PERFORMANCE_SEARCH",
            boundary_receipt.get("real_performance_search_result") == "PASS",
            "CRYPTO_INSTRUMENT_CAPABILITY_QUALIFICATION.json",
        ),
    ]
    return [
        {
            "criterion_id": criterion_id,
            "result": "PASS" if passed else "FAIL",
            "evidence_ref": evidence_ref,
        }
        for criterion_id, passed, evidence_ref in checks
    ]


def _compatibility_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for row in rows:
        if row.get("comparison_kind") != "PRIMITIVE":
            continue
        result.setdefault(str(row["classification"]), []).append(str(row["primitive"]))
    return {key: sorted(values) for key, values in sorted(result.items())}


def _fmt(value: Any) -> str:
    if value is None:
        return "N/A"
    return f"{100.0 * float(value):.1f}%"


def _render_report(
    *,
    source_sha: str,
    status: str,
    criteria: Sequence[Mapping[str, Any]],
    compatibility: Sequence[Mapping[str, Any]],
    mapping_behavior: Mapping[str, Any],
    alignment: Mapping[str, Any],
    harness: Mapping[str, Any],
    boundary_receipt: Mapping[str, Any],
) -> bytes:
    classes = _compatibility_summary(compatibility)
    aggregate = alignment["aggregate"]
    capability_qualified = status == FINAL_STATUS_QUALIFIED
    family_lines = []
    for family_id in FAMILY_IDS:
        reproduction = harness["cross_seed_reproduction"][family_id]
        family_runs = [
            row
            for row in harness["runs"]
            if row["family_contract"]["family_id"] == family_id
        ]
        discovered = all(
            bool(row["qualification_checks"].get("proposal_generated_from_frozen_grammar"))
            and bool(row["qualification_checks"].get("positive_candidate_reachable"))
            for row in family_runs
        )
        mapped = all(
            bool(row["qualification_checks"].get("mapping_preserves_intended_information"))
            for row in family_runs
        )
        survived = all(
            bool(row["qualification_checks"].get("positive_candidate_survives"))
            for row in family_runs
        )
        family_lines.append(
            "| "
            + family_id
            + " | "
            + ("PASS" if discovered else "FAIL")
            + " | "
            + ("PASS" if mapped else "FAIL")
            + " | "
            + ("PASS" if survived else "FAIL")
            + " | "
            + ("PASS" if reproduction["canonical_mechanism_reproduction"] else "FAIL")
            + " | "
            + ("PASS" if reproduction["behavior_reproduction"] else "FAIL")
            + " |"
        )
    criterion_lines = [
        f"| {row['criterion_id']} | {row['result']} | `{row['evidence_ref']}` |"
        for row in criteria
    ]
    primitive_list = ", ".join(f"`{name}`" for name in CANONICAL_PRIMITIVES)
    old_fooling = ", ".join(
        f"`{name}`"
        for name in aggregate["decoys_still_fooling_legacy_feedback"]
    ) or "无"
    new_fooling = ", ".join(
        f"`{name}`"
        for name in aggregate["decoys_still_fooling_aligned_feedback"]
    ) or "无"
    algorithm_list = ", ".join(f"`{name}`" for name in SUPPORTED_ALGORITHMS)
    lines = [
        "# Crypto Internal Search Instrument Capability Report",
        "",
        f"**Final status:** `{status}`  ",
        f"**Source commit:** `{source_sha}`  ",
        f"**Accepted closure:** `{CLOSURE_TAG}` → `{EXPECTED_CLOSURE_SHA}`  ",
        "**Scope:** deterministic synthetic capability only; no market alpha or economic increment claim.",
        "",
        "## 结论",
        "",
        (
            "内部搜索仪器已经通过固定有限 grammar 内的表达、发现、保留、显式持仓映射、full-L1 换手/固定 5 bps 成本和 decoy 排序能力门槛。"
            if capability_qualified
            else "内部搜索仪器尚未通过全部固定有限 grammar capability 门槛；失败项以 qualification gate 为准。"
        )
        + "该结论不改变 `CURRENT_DATA_UNDERPOWERED`、`FINANCIAL_GATE_HOLD_RESEARCH` 或任何 sealed/frozen 边界。",
        "",
        "## 十个必答问题",
        "",
        "### 1. Canonical primitive authority",
        "",
        primitive_list + "。每个 active ID 只绑定 `alphafactory_crypto.instrument_capability.primitives.evaluate_primitive` 中的一种数学语义。",
        "",
        "### 2. Deprecated 旧实现",
        "",
        "Closure tag 中 `temporal_program`、`nextgen_epoch` 与 `b1s_canary` 的同名差异实现仅保留为 source-qualified legacy adapter/parity source；它们不能以旧同名重新取得 active authority。35 条显式 alias 记录见 implementation authority CSV。",
        "",
        "### 3. 已确认的历史语义漂移",
        "",
        f"- `EXACT_PARITY`: {', '.join(classes.get('EXACT_PARITY', [])) or '无'}",
        f"- `CONDITIONAL_PARITY`: {', '.join(classes.get('CONDITIONAL_PARITY', [])) or '无'}",
        f"- `EXPECTED_SEMANTIC_CHANGE`: {', '.join(classes.get('EXPECTED_SEMANTIC_CHANGE', [])) or '无'}",
        f"- `LEGACY_BEHAVIOR_DEPRECATED`: {', '.join(classes.get('LEGACY_BEHAVIOR_DEPRECATED', [])) or '无'}",
        "",
        "### 4. 三种 mapping 保留/删除的信息",
        "",
        "- `CROSS_SECTIONAL_ZERO_NET` 保留同一时点资产间相对次序；显式删除 common mode 与绝对置信度。singleton/inadequate cross-section 为 infeasible no-trade。",
        "- `TIME_SERIES_DIRECTIONAL_STATEFUL` 保留符号、绝对置信度、common mode、entry/exit hysteresis 与持有状态；不 demean。",
        "- `SPARSE_EVENT_OR_CARRY` 保留 singleton event、少量 active assets、settlement cadence、fixed hold 与 explicit exit/no-trade；不强制横截面归零。",
        "",
        "### 5. Turnover attribution",
        "",
        "`raw signal movement` 与权重变化使用不同单位，不能直接作历史因果分解。证据分别报告 raw movement、entry establishment、rebalance、exit、mapped full-L1 turnover，以及同一 raw signal 的 direct clipped-signal counterfactual。固定 5 bps 只覆盖线性 cost；spread/slippage/impact/fill/capacity 未建模。",
        "",
        "### 6. Aligned feedback 是否优于旧 gross proxy",
        "",
        f"在固定 synthetic comparable set 上，aligned decoy rejection 为 {_fmt(aggregate['mean_decoy_rejection_rate_aligned'])}，旧 proxy 为 {_fmt(aggregate['mean_decoy_rejection_rate_legacy'])}；aligned top-3 strict-feasible rate 为 {_fmt(aggregate['mean_top_k_strict_feasibility_rate_aligned'])}，旧 proxy 为 {_fmt(aggregate['mean_top_k_strict_feasibility_rate_legacy'])}。这是 instrument alignment 增量，不是经济收益增量。",
        "",
        "### 7. 仍能欺骗 feedback 的 decoy",
        "",
        f"旧 zero-cost gross proxy：{old_fooling}。新 aligned feedback：{new_fooling}。",
        "",
        "### 8. 七类 planted mechanism",
        "",
        "| Family | discover | explicit mapping | survivor | canonical cross-seed | behavior cross-seed |",
        "|---|---:|---:|---:|---:|---:|",
        *family_lines,
        "",
        "### 9. 实际独立搜索行为",
        "",
        f"Capability harness 中实际运行且 behavior hash 区分的策略为 {algorithm_list}。`typed_random`/`typed_ast` 不被伪装成两个算法；历史 B1S 标签 `{', '.join(B1S_LABELS_DEGENERATE['labels'])}` 继续标记为 `{B1S_LABELS_DEGENERATE['classification']}`。策略定义："
        + "; ".join(f"`{key}`={value}" for key, value in POLICY_BEHAVIOR.items())
        + "。结构 proposal identity 与 evolutionary mutation 均排除 role_id 和 evidence label；mutation receipt 绑定 parent、child 与精确 changed genes；资格门槛要求至少两个不同的固定 seed"
        + "。这里的 discovery 是固定小型 proposal grammar 的可达、评价与保留；每个策略先覆盖 grammar，再执行各自 adaptive update，不等于宽泛真实市场 generator search。",
        "",
        "### 10. 是否可启动小型 development-only canary",
        "",
        (
            "技术上的固定有限 grammar capability-only 先决条件已满足；执行授权仍为 **NO**。"
            if capability_qualified
            else "技术上的 capability-only 先决条件尚未全部满足；执行授权同样为 **NO**。"
        )
        + "`NEW_PERFORMANCE_SEARCH_FROZEN` 与 financial HOLD 未改变，因此本结果不自动启动真实 development search、接入新数据、打开 challenge/forward/recent/May stress、promotion 或跨 sprint memory。",
        "",
        "## Qualification gate",
        "",
        "| Criterion | Result | Evidence |",
        "|---|---:|---|",
        *criterion_lines,
        "",
        "## 仍存 mismatch / 不能推出的结论",
        "",
        "- 未做真实市场或 OOS 经济资格化，不能推出存在 alpha、可交易性或 external component increment。",
        "- 5 bps 固定成本不含 spread、slippage、impact、fill 与 capacity。",
        "- 普通标准误 LCB 未做时间依赖修正，只用于 deterministic planted gate。",
        "- 历史 B1S/Epoch runner 保持冻结；本任务没有迁移或恢复真实 performance search。",
        "- 发现资格只覆盖固定 finite proposal grammar，不证明完整历史 generator 或开放式表达空间的召回率。",
        "- Legacy parity 的语义变化是显式兼容分类，不通过调参强求旧行为。",
        "",
        "## Boundary record",
        "",
        f"- closed input surface: `{boundary_receipt['closed_input_surface_result']}` (`{boundary_receipt['assurance_level']}`)",
        f"- synthetic run shape: `{boundary_receipt['synthetic_run_shape_result']}`",
        "- formal GraphSkill runtime trace supplied: `false`; this is static closed-input assurance.",
        *[f"- `{key}`: `{str(value).lower()}`" for key, value in BOUNDARIES.items()],
    ]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _render_bundle(source_sha: str) -> tuple[dict[str, bytes], dict[str, Any]]:
    source_sha = _require_full_source_sha(source_sha)
    _verify_source_branch(source_sha)
    source_inventory = _source_inventory(source_sha)
    closure_sha = _git("rev-parse", f"{CLOSURE_TAG}^{{commit}}")
    if closure_sha != EXPECTED_CLOSURE_SHA:
        raise RuntimeError(
            f"accepted closure tag drift: {closure_sha} != {EXPECTED_CLOSURE_SHA}"
        )

    primitive_contract = primitive_contract_payload()
    primitive_authority = implementation_authority_rows()
    primitive_parity = primitive_synthetic_parity_payload()
    mapping_contract = mapping_contract_payload()
    mapping_behavior = mapping_synthetic_behavior_payload()
    turnover_rows = mapping_turnover_rows()
    cost_counterfactual = mapping_cost_counterfactual_payload()
    feedback_contract = feedback_contract_payload()
    harness = run_qualification(SEEDS, SEARCH_BUDGET)
    boundary_receipt = _execution_boundary_receipt(source_sha, harness)
    alignment = proxy_strict_alignment_payload(harness)
    matrix_rows = capability_matrix_rows(harness)
    planted_rows = planted_result_rows(harness)
    compatibility_rows = legacy_compatibility_rows(ROOT)
    criteria = _qualification_criteria(
        primitive_parity, mapping_behavior, alignment, harness, boundary_receipt
    )
    qualified = all(row["result"] == "PASS" for row in criteria)
    status = FINAL_STATUS_QUALIFIED if qualified else FINAL_STATUS_PARTIAL
    qualification = {
        "schema_version": 1,
        "final_status": status,
        "scope": "DETERMINISTIC_SYNTHETIC_CAPABILITY_ONLY",
        "economic_research_conclusion": "NOT_EVALUATED",
        "qualification_criteria": criteria,
        "boundaries": dict(BOUNDARIES),
        "execution_boundary_receipt": boundary_receipt,
        "input_roles": {
            "synthetic_observables": True,
            "synthetic_targets": True,
            "accepted_closure_code_for_fixed_parity": True,
            "market_numeric_data": False,
            "validation": False,
            "holdout": False,
            "challenge": False,
            "recent": False,
            "forward": False,
            "may_stress": False,
        },
        "harness": harness,
        "provenance": _provenance(source_sha),
    }

    rendered: dict[str, bytes] = {
        str((OUT / ARTIFACT_NAMES[0]).relative_to(ROOT)).replace("\\", "/"): _json_bytes(
            _with_provenance(primitive_contract, source_sha)
        ),
        str((OUT / ARTIFACT_NAMES[1]).relative_to(ROOT)).replace("\\", "/"): _csv_bytes(
            _rows_with_provenance(primitive_authority, source_sha)
        ),
        str((OUT / ARTIFACT_NAMES[2]).relative_to(ROOT)).replace("\\", "/"): _json_bytes(
            _with_provenance(primitive_parity, source_sha)
        ),
        str((OUT / ARTIFACT_NAMES[3]).relative_to(ROOT)).replace("\\", "/"): _json_bytes(
            _with_provenance(mapping_contract, source_sha)
        ),
        str((OUT / ARTIFACT_NAMES[4]).relative_to(ROOT)).replace("\\", "/"): _json_bytes(
            _with_provenance(mapping_behavior, source_sha)
        ),
        str((OUT / ARTIFACT_NAMES[5]).relative_to(ROOT)).replace("\\", "/"): _csv_bytes(
            _rows_with_provenance(turnover_rows, source_sha)
        ),
        str((OUT / ARTIFACT_NAMES[6]).relative_to(ROOT)).replace("\\", "/"): _json_bytes(
            _with_provenance(cost_counterfactual, source_sha)
        ),
        str((OUT / ARTIFACT_NAMES[7]).relative_to(ROOT)).replace("\\", "/"): _json_bytes(
            _with_provenance(feedback_contract, source_sha)
        ),
        str((OUT / ARTIFACT_NAMES[8]).relative_to(ROOT)).replace("\\", "/"): _json_bytes(
            _with_provenance(alignment, source_sha)
        ),
        str((OUT / ARTIFACT_NAMES[9]).relative_to(ROOT)).replace("\\", "/"): _csv_bytes(
            _rows_with_provenance(matrix_rows, source_sha)
        ),
        str((OUT / ARTIFACT_NAMES[10]).relative_to(ROOT)).replace("\\", "/"): _csv_bytes(
            _rows_with_provenance(planted_rows, source_sha)
        ),
        str((OUT / ARTIFACT_NAMES[11]).relative_to(ROOT)).replace("\\", "/"): _json_bytes(
            qualification
        ),
        str((OUT / ARTIFACT_NAMES[12]).relative_to(ROOT)).replace("\\", "/"): _csv_bytes(
            _rows_with_provenance(compatibility_rows, source_sha)
        ),
        str(REPORT.relative_to(ROOT)).replace("\\", "/"): _render_report(
            source_sha=source_sha,
            status=status,
            criteria=criteria,
            compatibility=compatibility_rows,
            mapping_behavior=mapping_behavior,
            alignment=alignment,
            harness=harness,
            boundary_receipt=boundary_receipt,
        ),
    }
    artifacts = [
        {"path": path, "sha256": _sha256(payload), "bytes": len(payload)}
        for path, payload in sorted(rendered.items())
    ]
    bundle_identity = "\n".join(
        f"{row['path']}\0{row['sha256']}\0{row['bytes']}" for row in artifacts
    ).encode("utf-8")
    manifest = {
        "schema_version": 1,
        "bundle_id": "crypto-instrument-capability-20260715",
        "verified_branch": REPAIR_BRANCH,
        "source_commit_sha": source_sha,
        "accepted_closure_tag": CLOSURE_TAG,
        "accepted_closure_sha": EXPECTED_CLOSURE_SHA,
        "final_status": status,
        "fixed_seeds": list(SEEDS),
        "search_budget_per_family_algorithm_seed": SEARCH_BUDGET,
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
        "bundle_hash_sha256": _sha256(bundle_identity),
        "source_files": source_inventory,
        "boundaries": dict(BOUNDARIES),
        "execution_boundary_receipt": boundary_receipt,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "reproducer": {
            "build": "python scripts/crypto_instrument_capability.py build --source-sha <sha>",
            "check": "python scripts/crypto_instrument_capability.py check",
        },
    }
    return rendered, manifest


def build(source_sha: str) -> None:
    source_sha = _require_full_source_sha(source_sha)
    _verify_source_branch(source_sha)
    rendered, manifest = _render_bundle(source_sha)
    for relative, payload in rendered.items():
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_bytes(_json_bytes(manifest))
    print(
        json.dumps(
            {
                "status": "BUILT",
                "final_status": manifest["final_status"],
                "source_commit_sha": source_sha,
                "artifact_count": manifest["artifact_count"],
                "bundle_hash_sha256": manifest["bundle_hash_sha256"],
            },
            sort_keys=True,
        )
    )


def check() -> None:
    if not MANIFEST.is_file():
        raise RuntimeError(f"manifest missing: {MANIFEST.relative_to(ROOT)}")
    observed_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_sha = _require_full_source_sha(str(observed_manifest["source_commit_sha"]))
    _verify_source_branch(source_sha)
    rendered, expected_manifest = _render_bundle(source_sha)
    expected_manifest_bytes = _json_bytes(expected_manifest)
    if MANIFEST.read_bytes() != expected_manifest_bytes:
        raise RuntimeError("manifest differs from deterministic reconstruction")
    mismatches: list[str] = []
    for relative, expected in rendered.items():
        path = ROOT / relative
        if not path.is_file():
            mismatches.append(f"MISSING:{relative}")
        elif path.read_bytes() != expected:
            mismatches.append(f"CONTENT_MISMATCH:{relative}")
    expected_output_files = {
        str((OUT / name).resolve()) for name in ARTIFACT_NAMES
    } | {str(MANIFEST.resolve())}
    observed_output_files = {
        str(path.resolve()) for path in OUT.iterdir() if path.is_file()
    }
    for unexpected in sorted(observed_output_files - expected_output_files):
        mismatches.append(f"UNEXPECTED:{Path(unexpected).relative_to(ROOT)}")
    if mismatches:
        raise RuntimeError(";".join(mismatches))
    print(
        json.dumps(
            {
                "status": "PASS",
                "final_status": expected_manifest["final_status"],
                "source_commit_sha": source_sha,
                "artifact_count": expected_manifest["artifact_count"],
                "bundle_hash_sha256": expected_manifest["bundle_hash_sha256"],
            },
            sort_keys=True,
        )
    )


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Build/check deterministic crypto search-instrument capability evidence."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--source-sha", required=True)
    subparsers.add_parser("check")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command == "build":
        build(str(args.source_sha))
    else:
        check()


if __name__ == "__main__":
    main()
