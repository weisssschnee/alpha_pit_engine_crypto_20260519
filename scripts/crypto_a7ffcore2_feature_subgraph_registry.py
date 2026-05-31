from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore2_feature_subgraph_registry"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE2_FEATURE_SUBGRAPH_REGISTRY_20260601.md"
A7FFCORE1 = REPO / "runtime" / "a7ffcore1_ast_schema_adapter" / "a7ffcore1_manifest.json"
REPAIRED_INDEX = REPO / "runtime" / "a7ff55r3_repaired_atlas_dry_generation" / "a7ff55r3_repaired_formula_index.csv"


TRANSFORM_OPS = {"Delta", "Mean", "ZScore", "TSRank", "Decay", "Rank", "CSRank", "Abs", "Sign", "Clip", "Neg", "Winsor"}
INTERACTION_OPS = {"Mul", "Sub", "Add", "SafeDiv"}
ALL_OPS = TRANSFORM_OPS | INTERACTION_OPS
TOKEN_RE = re.compile(r"\s*([A-Za-z_][A-Za-z0-9_]*|-?\d+(?:\.\d+)?|[,()])\s*")


@dataclass
class Parser:
    tokens: list[str]
    pos: int = 0

    def peek(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def take(self) -> str:
        if self.pos >= len(self.tokens):
            raise ValueError("unexpected_end")
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def expect(self, token: str) -> None:
        got = self.take()
        if got != token:
            raise ValueError(f"expected_{token}_got_{got}")

    def parse_expr(self) -> dict[str, Any]:
        token = self.take()
        if self.peek() == "(":
            operator = token
            self.expect("(")
            args: list[dict[str, Any]] = []
            if self.peek() != ")":
                while True:
                    args.append(self.parse_expr())
                    if self.peek() == ",":
                        self.take()
                        continue
                    break
            self.expect(")")
            node_type = "Interaction" if operator in INTERACTION_OPS else "Transform"
            return {"node_type": node_type, "operator": operator, "args": args}
        if re.fullmatch(r"-?\d+(?:\.\d+)?", token):
            value: int | float = float(token) if "." in token else int(token)
            return {"node_type": "Const", "value": value}
        return {"node_type": "Field", "field_name": token}


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


def clean(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    return str(value)


def tokenize(expression: str) -> list[str]:
    tokens: list[str] = []
    idx = 0
    while idx < len(expression):
        match = TOKEN_RE.match(expression, idx)
        if not match:
            raise ValueError(f"bad_token_at_{idx}")
        tokens.append(match.group(1))
        idx = match.end()
    return tokens


def parse_expression(expression: str) -> dict[str, Any]:
    parser = Parser(tokenize(expression))
    ast = parser.parse_expr()
    if parser.peek() is not None:
        raise ValueError(f"trailing_token_{parser.peek()}")
    return ast


def render(ast: dict[str, Any]) -> str:
    node_type = ast.get("node_type")
    if node_type == "Field":
        return str(ast["field_name"])
    if node_type == "Const":
        value = ast["value"]
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
    operator = str(ast["operator"])
    return f"{operator}({','.join(render(arg) for arg in ast.get('args', []))})"


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{hashlib.sha1(value.encode('utf-8')).hexdigest()[:16]}"


def raw_fields(ast: dict[str, Any]) -> set[str]:
    fields: set[str] = set()

    def walk(node: dict[str, Any]) -> None:
        if node.get("node_type") == "Field":
            fields.add(str(node.get("field_name")))
        for arg in node.get("args", []):
            walk(arg)

    walk(ast)
    return fields


def operators(ast: dict[str, Any]) -> list[str]:
    ops: list[str] = []

    def walk(node: dict[str, Any]) -> None:
        if "operator" in node:
            ops.append(str(node.get("operator")))
        for arg in node.get("args", []):
            walk(arg)

    walk(ast)
    return ops


def max_depth(ast: dict[str, Any]) -> int:
    def walk(node: dict[str, Any], depth: int) -> int:
        children = node.get("args", [])
        if not children:
            return depth
        return max(walk(child, depth + 1) for child in children)

    return walk(ast, 1)


def subgraph_kind(ast: dict[str, Any], is_root: bool) -> str:
    node_type = ast.get("node_type")
    if is_root:
        return "factor_candidate_root"
    if node_type == "Field":
        return "field_node"
    if node_type == "Transform":
        return "typed_transform_subgraph"
    if node_type == "Interaction":
        return "typed_interaction_subgraph"
    return "const_node"


def formula_gen_gate(candidate_roles: set[str], is_root: bool, node_type: str) -> str:
    if "label_only" in candidate_roles:
        return "reject_label_only"
    if "risk_defense_only" in candidate_roles:
        return "risk_defense_route_only"
    if "diagnostic_only" in candidate_roles:
        return "diagnostic_route_only"
    if is_root:
        return "diagnostic_or_repair_root_only"
    if node_type in {"typed_transform_subgraph", "typed_interaction_subgraph", "field_node"}:
        return "feature_factory_reusable_subgraph"
    return "registry_only"


def collect_nodes(
    ast: dict[str, Any],
    row: dict[str, Any],
    rows: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    parent_id: str = "",
    depth: int = 1,
    arg_index: int = 0,
    is_root: bool = False,
) -> str:
    expression = render(ast)
    subgraph_id = stable_id("sg", expression)
    kind = subgraph_kind(ast, is_root)
    node_type = str(ast.get("node_type", ""))
    op = clean(ast.get("operator"))
    fields = sorted(raw_fields(ast))
    ops = operators(ast)
    rows.append(
        {
            "blueprint_id": clean(row.get("blueprint_id")),
            "subgraph_id": subgraph_id,
            "parent_subgraph_id": parent_id,
            "arg_index": arg_index,
            "is_root": bool(is_root),
            "subgraph_kind": kind,
            "node_type": node_type,
            "operator": op,
            "expression": expression,
            "depth_from_root": depth,
            "subgraph_depth": max_depth(ast),
            "raw_inputs": ";".join(fields),
            "raw_input_count": len(fields),
            "operator_path": ">".join(ops),
            "operator_count": len(ops),
            "level": clean(row.get("level")),
            "candidate_role": clean(row.get("candidate_role")),
            "generation_priority": clean(row.get("generation_priority")),
            "semantic_pair": clean(row.get("semantic_pair")),
            "motif": clean(row.get("motif")),
            "primary_field": clean(row.get("primary_field")),
            "secondary_field": clean(row.get("secondary_field")),
            "primary_semantic": clean(row.get("primary_semantic")),
            "secondary_semantic": clean(row.get("secondary_semantic")),
            "skeleton_key": clean(row.get("skeleton_key")),
            "production_key": clean(row.get("production_key")),
        }
    )
    if parent_id:
        edges.append(
            {
                "blueprint_id": clean(row.get("blueprint_id")),
                "parent_subgraph_id": parent_id,
                "child_subgraph_id": subgraph_id,
                "arg_index": arg_index,
                "parent_expression": "",
                "child_expression": expression,
            }
        )
    for idx, child in enumerate(ast.get("args", [])):
        collect_nodes(child, row, rows, edges, subgraph_id, depth + 1, idx, False)
    return subgraph_id


def join_unique(values: pd.Series) -> str:
    items = sorted({clean(x) for x in values if clean(x)})
    return ";".join(items)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core1 = read_json(A7FFCORE1)
    if core1.get("decision") != "PASS_A7FFCORE1_AST_SCHEMA_ADAPTER_READY_FOR_CORE2":
        raise SystemExit(f"A7FF-CORE1 is not ready: {core1.get('decision')}")

    formula_index = pd.read_csv(REPAIRED_INDEX)
    node_rows: list[dict[str, Any]] = []
    edge_rows: list[dict[str, Any]] = []
    blueprint_rows: list[dict[str, Any]] = []
    parse_failures: list[dict[str, Any]] = []
    for row in formula_index.to_dict("records"):
        try:
            ast = parse_expression(str(row["expression"]))
            root_id = collect_nodes(ast, row, node_rows, edge_rows, is_root=True)
            blueprint_rows.append(
                {
                    "blueprint_id": clean(row.get("blueprint_id")),
                    "root_subgraph_id": root_id,
                    "expression": str(row["expression"]),
                    "level": clean(row.get("level")),
                    "candidate_role": clean(row.get("candidate_role")),
                    "semantic_pair": clean(row.get("semantic_pair")),
                    "motif": clean(row.get("motif")),
                    "skeleton_key": clean(row.get("skeleton_key")),
                    "production_key": clean(row.get("production_key")),
                }
            )
        except Exception as exc:
            parse_failures.append({"blueprint_id": clean(row.get("blueprint_id")), "expression": str(row.get("expression")), "error": str(exc)})

    nodes = pd.DataFrame(node_rows)
    edges = pd.DataFrame(edge_rows)
    blueprint_map = pd.DataFrame(blueprint_rows)
    if edges.empty:
        edges = pd.DataFrame(columns=["blueprint_id", "parent_subgraph_id", "child_subgraph_id", "arg_index", "parent_expression", "child_expression"])

    unique_rows: list[dict[str, Any]] = []
    for subgraph_id, group in nodes.groupby("subgraph_id", dropna=False):
        candidate_roles = {clean(x) for x in group["candidate_role"] if clean(x)}
        root_count = int(group["is_root"].sum())
        kind_counts = group["subgraph_kind"].value_counts().to_dict()
        preferred_kind = "factor_candidate_root" if root_count else str(group["subgraph_kind"].iloc[0])
        gate = formula_gen_gate(candidate_roles, bool(root_count), preferred_kind)
        unique_rows.append(
            {
                "subgraph_id": subgraph_id,
                "expression": str(group["expression"].iloc[0]),
                "subgraph_kind": preferred_kind,
                "node_type": str(group["node_type"].iloc[0]),
                "operator": join_unique(group["operator"]),
                "blueprint_ref_count": int(group["blueprint_id"].nunique()),
                "node_occurrence_count": int(len(group)),
                "root_ref_count": root_count,
                "nonroot_ref_count": int(len(group) - root_count),
                "raw_inputs": join_unique(group["raw_inputs"]),
                "raw_input_count": int(max(group["raw_input_count"])),
                "operator_path": join_unique(group["operator_path"]),
                "operator_count_max": int(max(group["operator_count"])),
                "max_subgraph_depth": int(max(group["subgraph_depth"])),
                "levels": join_unique(group["level"]),
                "candidate_roles": ";".join(sorted(candidate_roles)),
                "semantic_pairs": join_unique(group["semantic_pair"]),
                "motifs": join_unique(group["motif"]),
                "primary_semantics": join_unique(group["primary_semantic"]),
                "secondary_semantics": join_unique(group["secondary_semantic"]),
                "formula_gen_gate": gate,
                "feature_factory_allowed": gate in {"feature_factory_reusable_subgraph", "diagnostic_or_repair_root_only"},
                "ordinary_alpha_eligible": False,
                "requires_response_promotion": True,
                "pit_policy": "inherit_from_field_contract",
                "role_policy": "role_enforced_no_label_feature",
                "kind_counts": json.dumps(kind_counts, sort_keys=True),
            }
        )

    registry = pd.DataFrame(unique_rows).sort_values(["blueprint_ref_count", "node_occurrence_count"], ascending=False)

    lineage_rows: list[dict[str, Any]] = []
    for row in registry.to_dict("records"):
        for field in str(row["raw_inputs"]).split(";") if row["raw_inputs"] else []:
            lineage_rows.append(
                {
                    "subgraph_id": row["subgraph_id"],
                    "expression": row["expression"],
                    "raw_field": field,
                    "raw_input_count": row["raw_input_count"],
                    "subgraph_kind": row["subgraph_kind"],
                    "semantic_pairs": row["semantic_pairs"],
                    "pit_policy": row["pit_policy"],
                    "role_policy": row["role_policy"],
                }
            )
    lineage = pd.DataFrame(lineage_rows)

    reusable = registry[
        registry["feature_factory_allowed"].eq(True)
        & registry["subgraph_kind"].isin(["field_node", "typed_transform_subgraph", "typed_interaction_subgraph"])
    ].copy()
    root_registry = registry[registry["root_ref_count"].gt(0)].copy()

    summary = (
        registry.groupby(["subgraph_kind", "formula_gen_gate"], dropna=False)
        .agg(
            subgraphs=("subgraph_id", "count"),
            blueprint_refs=("blueprint_ref_count", "sum"),
            max_ref_count=("blueprint_ref_count", "max"),
        )
        .reset_index()
        .sort_values(["subgraphs", "blueprint_refs"], ascending=False)
    )
    family_summary = (
        registry.groupby(["semantic_pairs", "motifs"], dropna=False)
        .agg(
            subgraphs=("subgraph_id", "count"),
            blueprint_refs=("blueprint_ref_count", "sum"),
            reusable_subgraphs=("feature_factory_allowed", "sum"),
        )
        .reset_index()
        .sort_values("blueprint_refs", ascending=False)
    )

    role_gate_summary = (
        registry.groupby(["candidate_roles", "formula_gen_gate"], dropna=False)
        .size()
        .reset_index(name="subgraphs")
        .sort_values("subgraphs", ascending=False)
    )

    registry.to_csv(RUNTIME / "a7ffcore2_subgraph_registry.csv", index=False)
    reusable.to_csv(RUNTIME / "a7ffcore2_reusable_feature_subgraphs.csv", index=False)
    root_registry.to_csv(RUNTIME / "a7ffcore2_factor_candidate_roots.csv", index=False)
    blueprint_map.to_csv(RUNTIME / "a7ffcore2_blueprint_subgraph_map.csv", index=False)
    nodes.to_csv(RUNTIME / "a7ffcore2_node_occurrence_trace.csv", index=False)
    edges.to_csv(RUNTIME / "a7ffcore2_subgraph_edge_list.csv", index=False)
    lineage.to_csv(RUNTIME / "a7ffcore2_field_lineage.csv", index=False)
    summary.to_csv(RUNTIME / "a7ffcore2_subgraph_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore2_family_subgraph_summary.csv", index=False)
    role_gate_summary.to_csv(RUNTIME / "a7ffcore2_formula_gen_gate_matrix.csv", index=False)
    pd.DataFrame(parse_failures).to_csv(RUNTIME / "a7ffcore2_parse_failures.csv", index=False)

    blockers: list[str] = []
    if parse_failures:
        blockers.append("parse_failures_present")
    if len(registry) == 0:
        blockers.append("empty_subgraph_registry")
    if int(reusable["subgraph_id"].nunique()) == 0:
        blockers.append("no_reusable_feature_subgraphs")
    if "reject_label_only" in set(registry["formula_gen_gate"]):
        blockers.append("label_only_subgraph_present")

    decision = "PASS_A7FFCORE2_FEATURE_SUBGRAPH_REGISTRY_READY_FOR_CORE3" if not blockers else "HOLD_A7FFCORE2_SUBGRAPH_REGISTRY_FAIL"
    manifest = {
        "stage": "A7FF-CORE2",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7FF-CORE1",
        "source_decision": core1.get("decision"),
        "input_formula_rows": int(len(formula_index)),
        "blueprint_map_rows": int(len(blueprint_map)),
        "node_occurrence_rows": int(len(nodes)),
        "unique_subgraph_count": int(len(registry)),
        "reusable_feature_subgraph_count": int(reusable["subgraph_id"].nunique()) if not reusable.empty else 0,
        "factor_candidate_root_count": int(root_registry["subgraph_id"].nunique()) if not root_registry.empty else 0,
        "field_lineage_rows": int(len(lineage)),
        "edge_rows": int(len(edges)),
        "parse_failure_rows": int(len(parse_failures)),
        "top_reusable_subgraph_ref_count": int(reusable["blueprint_ref_count"].max()) if not reusable.empty else 0,
        "executes_generation": False,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core3": not bool(blockers),
        "authorizes_generation": False,
        "authorizes_numeric": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE3 FormulaGen subgraph gate" if not blockers else "A7FF-CORE2 registry repair",
    }
    write_json(RUNTIME / "a7ffcore2_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-CORE2 FEATURE SUBGRAPH REGISTRY

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-CORE2 converts the parsed A7FF typed AST atlas into a reusable FeatureFactory subgraph registry. It assigns stable subgraph IDs, records blueprint-to-root mappings, parent/child edges, raw-field lineage, role/PIT policy, and FormulaGen gates. It does not execute generation, numeric evaluation, replay, or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Subgraph Summary

{md_table(summary, 80)}

## FormulaGen Gate Matrix

{md_table(role_gate_summary, 80)}

## Family Subgraph Summary

{md_table(family_summary, 80)}

## Top Reusable Feature Subgraphs

{md_table(reusable[["subgraph_id", "subgraph_kind", "expression", "blueprint_ref_count", "raw_inputs", "semantic_pairs", "motifs", "formula_gen_gate"]].head(40), 40)}

## Boundary

```text
generation executed: false
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
