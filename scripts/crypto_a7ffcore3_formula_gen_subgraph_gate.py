from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore3_formula_gen_subgraph_gate"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE3_FORMULAGEN_SUBGRAPH_GATE_20260601.md"
A7FFCORE2 = REPO / "runtime" / "a7ffcore2_feature_subgraph_registry" / "a7ffcore2_manifest.json"
SUBGRAPH_REGISTRY = REPO / "runtime" / "a7ffcore2_feature_subgraph_registry" / "a7ffcore2_subgraph_registry.csv"
REUSABLE_SUBGRAPHS = REPO / "runtime" / "a7ffcore2_feature_subgraph_registry" / "a7ffcore2_reusable_feature_subgraphs.csv"
FACTOR_ROOTS = REPO / "runtime" / "a7ffcore2_feature_subgraph_registry" / "a7ffcore2_factor_candidate_roots.csv"


GENERATION_SCRIPT_PATTERNS = (
    "generation",
    "generator",
    "dry_generation",
    "formula_search",
    "formula_engine",
)
DIRECT_EXPRESSION_PATTERNS = (
    r'"expression"\s*:',
    r"\bexpression\s*=",
    r"\bexpr\s*=",
    r"f\"[A-Za-z]+\(",
    r"f'[A-Za-z]+\(",
    r"\bproduction_key\b",
    r"\bskeleton_key\b",
)
CORE2_REFERENCE_PATTERNS = (
    "a7ffcore2",
    "subgraph_registry",
    "reusable_feature_subgraphs",
    "approved_subgraph",
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def generation_scripts() -> list[Path]:
    out: list[Path] = []
    for path in (REPO / "scripts").glob("*.py"):
        name = path.name.lower()
        if any(pattern in name for pattern in GENERATION_SCRIPT_PATTERNS):
            out.append(path)
    return sorted(out)


def audit_script(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    direct_hits: list[str] = []
    core2_hits: list[str] = []
    for lineno, line in enumerate(lines, start=1):
        for pattern in DIRECT_EXPRESSION_PATTERNS:
            if re.search(pattern, line):
                direct_hits.append(f"{lineno}:{line.strip()[:160]}")
                break
        if any(pattern in line for pattern in CORE2_REFERENCE_PATTERNS):
            core2_hits.append(f"{lineno}:{line.strip()[:160]}")
    executes_generation = any(
        marker in text
        for marker in (
            '"executes_formula_generation": True',
            '"executes_static_blueprint_generation": True',
            '"executes_generation": True',
        )
    )
    bypass_risk = "high" if direct_hits and not core2_hits else "medium" if direct_hits else "low"
    gate_status = "needs_core4_wiring" if bypass_risk in {"high", "medium"} else "no_obvious_generation_path"
    return {
        "script_path": str(path.relative_to(REPO)),
        "line_count": len(lines),
        "executes_generation_marker": executes_generation,
        "direct_expression_hit_count": len(direct_hits),
        "core2_reference_hit_count": len(core2_hits),
        "bypass_risk": bypass_risk,
        "gate_status": gate_status,
        "direct_expression_examples": " || ".join(direct_hits[:8]),
        "core2_reference_examples": " || ".join(core2_hits[:8]),
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core2 = read_json(A7FFCORE2)
    if core2.get("decision") != "PASS_A7FFCORE2_FEATURE_SUBGRAPH_REGISTRY_READY_FOR_CORE3":
        raise SystemExit(f"A7FF-CORE2 is not ready: {core2.get('decision')}")

    registry = pd.read_csv(SUBGRAPH_REGISTRY)
    reusable = pd.read_csv(REUSABLE_SUBGRAPHS)
    roots = pd.read_csv(FACTOR_ROOTS)

    approved_reusable = reusable[
        reusable["formula_gen_gate"].eq("feature_factory_reusable_subgraph")
        & reusable["feature_factory_allowed"].astype(bool)
    ].copy()
    approved_roots = roots[roots["formula_gen_gate"].eq("diagnostic_or_repair_root_only")].copy()
    blocked = registry[~registry["formula_gen_gate"].isin(["feature_factory_reusable_subgraph", "diagnostic_or_repair_root_only", "registry_only"])].copy()

    allowed_registry = approved_reusable[
        [
            "subgraph_id",
            "subgraph_kind",
            "expression",
            "raw_inputs",
            "candidate_roles",
            "semantic_pairs",
            "motifs",
            "formula_gen_gate",
            "pit_policy",
            "role_policy",
        ]
    ].copy()
    allowed_registry.to_csv(RUNTIME / "a7ffcore3_allowed_subgraph_registry.csv", index=False)

    root_registry = approved_roots[
        [
            "subgraph_id",
            "expression",
            "raw_inputs",
            "candidate_roles",
            "semantic_pairs",
            "motifs",
            "formula_gen_gate",
        ]
    ].copy()
    root_registry.to_csv(RUNTIME / "a7ffcore3_diagnostic_root_registry.csv", index=False)

    script_audit = pd.DataFrame([audit_script(path) for path in generation_scripts()])
    script_audit.to_csv(RUNTIME / "a7ffcore3_generation_script_bypass_audit.csv", index=False)

    gate_policy = {
        "policy_id": "a7ffcore3_formula_gen_subgraph_gate_v1",
        "source_stage": "A7FF-CORE2",
        "allowed_input_sources": [
            "runtime/a7ffcore2_feature_subgraph_registry/a7ffcore2_reusable_feature_subgraphs.csv",
            "runtime/a7ffcore2_feature_subgraph_registry/a7ffcore2_subgraph_registry.csv",
        ],
        "hard_rules": [
            {
                "rule": "subgraph_source_required",
                "detail": "FormulaGen must assemble candidates from approved_subgraph_id values, not ad hoc raw expression strings.",
            },
            {
                "rule": "raw_field_bypass_rejected",
                "detail": "Direct Field or raw expression creation is rejected unless it resolves to an approved CORE2 subgraph_id.",
            },
            {
                "rule": "root_candidate_not_alpha",
                "detail": "CORE2 factor_candidate_root nodes are diagnostic/repair roots only until response promotion and replay gates pass.",
            },
            {
                "rule": "label_and_future_forbidden",
                "detail": "label_only, future, timing-blocked, or missing-contract fields remain fail-closed.",
            },
            {
                "rule": "role_route_enforced",
                "detail": "diagnostic_only and risk_defense_only nodes cannot enter ordinary alpha queues.",
            },
            {
                "rule": "no_may_in_generation",
                "detail": "May labels, returns, pass/fail flags, or stress margins are forbidden in generation, mutation, ranking, or selector score.",
            },
        ],
        "allowed_formula_gen_modes": {
            "diagnostic_repair": {
                "allowed_subgraph_gate": ["feature_factory_reusable_subgraph", "diagnostic_or_repair_root_only"],
                "authorizes_numeric": False,
                "authorizes_replay": False,
                "authorizes_search": False,
            },
            "ordinary_alpha": {
                "allowed_subgraph_gate": ["feature_factory_reusable_subgraph"],
                "requires_response_promotion": True,
                "authorizes_numeric": False,
                "authorizes_replay": False,
                "authorizes_search": False,
            },
        },
    }
    write_json(RUNTIME / "a7ffcore3_formula_gen_gate_policy.json", gate_policy)

    gate_matrix = pd.DataFrame(
        [
            {
                "gate": "approved_reusable_subgraphs",
                "count": int(len(approved_reusable)),
                "status": "allowed_for_feature_factory",
                "authorizes_generation": False,
            },
            {
                "gate": "diagnostic_roots",
                "count": int(len(approved_roots)),
                "status": "diagnostic_or_repair_only",
                "authorizes_generation": False,
            },
            {
                "gate": "blocked_or_unknown_subgraphs",
                "count": int(len(blocked)),
                "status": "fail_closed",
                "authorizes_generation": False,
            },
        ]
    )
    gate_matrix.to_csv(RUNTIME / "a7ffcore3_gate_matrix.csv", index=False)

    bypass_summary = (
        script_audit.groupby(["bypass_risk", "gate_status"], dropna=False)
        .size()
        .reset_index(name="script_count")
        .sort_values("script_count", ascending=False)
    )
    bypass_summary.to_csv(RUNTIME / "a7ffcore3_bypass_summary.csv", index=False)

    blockers: list[str] = []
    if len(approved_reusable) == 0:
        blockers.append("no_approved_reusable_subgraphs")
    if len(script_audit[script_audit["bypass_risk"].eq("high")]) == 0:
        blockers.append("no_generation_scripts_detected_for_audit")
    decision = "PASS_A7FFCORE3_FORMULAGEN_SUBGRAPH_GATE_READY_FOR_CORE4"
    if blockers:
        decision = "HOLD_A7FFCORE3_FORMULAGEN_GATE_INCOMPLETE"

    manifest = {
        "stage": "A7FF-CORE3",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7FF-CORE2",
        "source_decision": core2.get("decision"),
        "registry_subgraph_count": int(len(registry)),
        "approved_reusable_subgraph_count": int(len(approved_reusable)),
        "diagnostic_root_count": int(len(approved_roots)),
        "blocked_or_unknown_subgraph_count": int(len(blocked)),
        "generation_script_count": int(len(script_audit)),
        "high_bypass_risk_script_count": int(script_audit["bypass_risk"].eq("high").sum()) if not script_audit.empty else 0,
        "medium_bypass_risk_script_count": int(script_audit["bypass_risk"].eq("medium").sum()) if not script_audit.empty else 0,
        "low_bypass_risk_script_count": int(script_audit["bypass_risk"].eq("low").sum()) if not script_audit.empty else 0,
        "executes_generation": False,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core4": decision.startswith("PASS_"),
        "authorizes_generation": False,
        "authorizes_numeric": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE4 FormulaGen gate implementation regression" if decision.startswith("PASS_") else "A7FF-CORE3 gate repair",
    }
    write_json(RUNTIME / "a7ffcore3_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-CORE3 FORMULAGEN SUBGRAPH GATE

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-CORE3 defines the FormulaGen subgraph gate from the CORE2 reusable subgraph registry and audits legacy generation scripts for bypass risk. It does not execute formula generation, numeric evaluation, replay, or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Gate Matrix

{md_table(gate_matrix, 20)}

## Bypass Summary

{md_table(bypass_summary, 40)}

## High-Risk Generation Scripts

{md_table(script_audit[script_audit["bypass_risk"].eq("high")][["script_path", "executes_generation_marker", "direct_expression_hit_count", "core2_reference_hit_count", "gate_status"]], 80)}

## Policy Boundary

```text
generation executed: false
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```

## Next

`A7FF-CORE4 FormulaGen gate implementation regression` should wire the gate into active generation entrypoints or explicitly quarantine legacy generation scripts. CORE3 itself only creates the source-of-truth policy and bypass audit.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
