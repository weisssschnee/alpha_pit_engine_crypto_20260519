from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7ffcore_gate import FormulaGenSubgraphGate


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore5_gate_native_generation_dryrun"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE5_GATE_NATIVE_GENERATION_DRYRUN_20260601.md"
A7FFCORE4 = REPO / "runtime" / "a7ffcore4_gate_implementation_regression" / "a7ffcore4_manifest.json"
ROOT_REGISTRY = REPO / "runtime" / "a7ffcore3_formula_gen_subgraph_gate" / "a7ffcore3_diagnostic_root_registry.csv"
REUSABLE_REGISTRY = REPO / "runtime" / "a7ffcore3_formula_gen_subgraph_gate" / "a7ffcore3_allowed_subgraph_registry.csv"


QUEUE_TARGET = 2048
MAX_PER_SEMANTIC_PAIR = 192
MAX_PER_MOTIF = 256


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


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{hashlib.sha1(value.encode('utf-8')).hexdigest()[:18]}"


def first_token(value: Any) -> str:
    text = "" if pd.isna(value) else str(value)
    return text.split(";")[0] if text else ""


def select_balanced_roots(roots: pd.DataFrame) -> pd.DataFrame:
    work = roots.copy()
    work["semantic_bucket"] = work["semantic_pairs"].map(first_token)
    work["motif_bucket"] = work["motifs"].map(first_token)
    work["raw_input_count"] = work["raw_inputs"].fillna("").astype(str).map(lambda x: len([p for p in x.split(";") if p]))
    work["expr_len"] = work["expression"].astype(str).str.len()
    work = work.sort_values(["semantic_bucket", "motif_bucket", "raw_input_count", "expr_len", "subgraph_id"])

    selected: list[dict[str, Any]] = []
    pair_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    for _, row in work.iterrows():
        pair = str(row["semantic_bucket"])
        motif = str(row["motif_bucket"])
        if pair_counts.get(pair, 0) >= MAX_PER_SEMANTIC_PAIR:
            continue
        if motif_counts.get(motif, 0) >= MAX_PER_MOTIF:
            continue
        selected.append(row.to_dict())
        pair_counts[pair] = pair_counts.get(pair, 0) + 1
        motif_counts[motif] = motif_counts.get(motif, 0) + 1
        if len(selected) >= QUEUE_TARGET:
            break

    if len(selected) < QUEUE_TARGET:
        seen = {row["subgraph_id"] for row in selected}
        for _, row in work.iterrows():
            if row["subgraph_id"] in seen:
                continue
            selected.append(row.to_dict())
            seen.add(row["subgraph_id"])
            if len(selected) >= QUEUE_TARGET:
                break
    return pd.DataFrame(selected)


def build_queue(selected: pd.DataFrame, gate: FormulaGenSubgraphGate) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for idx, row in enumerate(selected.to_dict("records")):
        result = gate.validate(subgraph_id=str(row["subgraph_id"]), mode="diagnostic_repair")
        ordinary_result = gate.validate(subgraph_id=str(row["subgraph_id"]), mode="ordinary_alpha")
        rows.append(
            {
                "candidate_id": stable_id("a7ffcore5", f"{idx}|{row['subgraph_id']}|{row['expression']}"),
                "queue_index": idx,
                "root_subgraph_id": row["subgraph_id"],
                "expression": row["expression"],
                "raw_inputs": row["raw_inputs"],
                "candidate_roles": row["candidate_roles"],
                "semantic_pairs": row["semantic_pairs"],
                "motifs": row["motifs"],
                "semantic_bucket": row["semantic_bucket"],
                "motif_bucket": row["motif_bucket"],
                "formula_gen_gate": row["formula_gen_gate"],
                "gate_mode": "diagnostic_repair",
                "gate_allowed": bool(result["allowed"]),
                "gate_reason": result["reason"],
                "ordinary_alpha_allowed": bool(ordinary_result["allowed"]),
                "ordinary_alpha_reject_reason": ordinary_result["reason"] if not ordinary_result["allowed"] else "",
                "uses_raw_expression_construction": False,
                "uses_may": False,
                "authorizes_numeric": False,
                "authorizes_replay": False,
                "authorizes_search": False,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core4 = read_json(A7FFCORE4)
    if core4.get("decision") != "PASS_A7FFCORE4_GATE_IMPLEMENTATION_REGRESSION_READY_FOR_CORE5":
        raise SystemExit(f"A7FF-CORE4 is not ready: {core4.get('decision')}")

    roots = pd.read_csv(ROOT_REGISTRY)
    reusable = pd.read_csv(REUSABLE_REGISTRY)
    gate = FormulaGenSubgraphGate()
    selected = select_balanced_roots(roots)
    queue = build_queue(selected, gate)

    queue.to_csv(RUNTIME / "a7ffcore5_gate_native_candidate_queue.csv", index=False)
    selected.to_csv(RUNTIME / "a7ffcore5_selected_root_subgraphs.csv", index=False)

    family_summary = (
        queue.groupby(["semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            candidates=("candidate_id", "count"),
            raw_field_count=("raw_inputs", lambda s: len(set(";".join(s.astype(str)).split(";")) - {""})),
            gate_pass=("gate_allowed", "sum"),
        )
        .reset_index()
        .sort_values("candidates", ascending=False)
    )
    family_summary.to_csv(RUNTIME / "a7ffcore5_queue_family_summary.csv", index=False)

    gate_summary = (
        queue.groupby(["gate_allowed", "gate_reason", "ordinary_alpha_allowed", "ordinary_alpha_reject_reason"], dropna=False)
        .size()
        .reset_index(name="candidates")
        .sort_values("candidates", ascending=False)
    )
    gate_summary.to_csv(RUNTIME / "a7ffcore5_gate_summary.csv", index=False)

    coverage = pd.DataFrame(
        [
            {"metric": "queue_rows", "value": len(queue)},
            {"metric": "root_registry_rows", "value": len(roots)},
            {"metric": "reusable_subgraph_rows", "value": len(reusable)},
            {"metric": "semantic_bucket_count", "value": queue["semantic_bucket"].nunique()},
            {"metric": "motif_bucket_count", "value": queue["motif_bucket"].nunique()},
            {"metric": "raw_field_count", "value": len(set(";".join(queue["raw_inputs"].astype(str)).split(";")) - {""})},
            {"metric": "gate_pass_count", "value": int(queue["gate_allowed"].sum())},
            {"metric": "ordinary_alpha_allowed_count", "value": int(queue["ordinary_alpha_allowed"].sum())},
        ]
    )
    coverage.to_csv(RUNTIME / "a7ffcore5_queue_coverage.csv", index=False)

    blockers: list[str] = []
    if len(queue) < min(QUEUE_TARGET, len(roots)):
        blockers.append("queue_below_target")
    if int(queue["gate_allowed"].sum()) != len(queue):
        blockers.append("gate_failures_present")
    if int(queue["ordinary_alpha_allowed"].sum()) != 0:
        blockers.append("diagnostic_roots_leak_into_ordinary_alpha")
    if queue["semantic_bucket"].nunique() < 5:
        blockers.append("semantic_coverage_too_narrow")
    if queue["motif_bucket"].nunique() < 6:
        blockers.append("motif_coverage_too_narrow")

    decision = "PASS_A7FFCORE5_GATE_NATIVE_DRYRUN_READY_FOR_CORE6" if not blockers else "HOLD_A7FFCORE5_GATE_NATIVE_DRYRUN_FAIL"
    manifest = {
        "stage": "A7FF-CORE5",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7FF-CORE4",
        "source_decision": core4.get("decision"),
        "root_registry_rows": int(len(roots)),
        "reusable_subgraph_rows": int(len(reusable)),
        "queue_target": QUEUE_TARGET,
        "queue_rows": int(len(queue)),
        "semantic_bucket_count": int(queue["semantic_bucket"].nunique()),
        "motif_bucket_count": int(queue["motif_bucket"].nunique()),
        "gate_pass_count": int(queue["gate_allowed"].sum()),
        "ordinary_alpha_allowed_count": int(queue["ordinary_alpha_allowed"].sum()),
        "uses_raw_expression_construction": False,
        "executes_gate_native_dryrun": True,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core6": not bool(blockers),
        "authorizes_numeric": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE6 gate-native materialization preflight contract" if not blockers else "A7FF-CORE5 queue repair",
    }
    write_json(RUNTIME / "a7ffcore5_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-CORE5 GATE-NATIVE GENERATION DRYRUN

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-CORE5 builds a gate-native diagnostic queue from CORE2/CORE3 registered root subgraphs. It emits root subgraph references and gate metadata only; it does not create ad hoc raw expressions and does not execute numeric evaluation, replay, search, or promotion.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Queue Coverage

{md_table(coverage, 40)}

## Gate Summary

{md_table(gate_summary, 40)}

## Family Summary

{md_table(family_summary, 80)}

## Boundary

```text
gate-native dryrun: true
raw expression construction: false
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
