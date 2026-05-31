from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore1_ast_schema_adapter"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE1_AST_SCHEMA_ADAPTER_20260601.md"
A7FFCORE0 = REPO / "runtime" / "a7ffcore0_typed_ast_governance" / "a7ffcore0_manifest.json"
CORE0_SCHEMA = REPO / "runtime" / "a7ffcore0_typed_ast_governance" / "a7ffcore0_expression_node_schema.json"
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
        next_token = self.peek()
        if next_token == "(":
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
            if operator not in ALL_OPS:
                node_type = "Transform"
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


def canonical(expr: str) -> str:
    return re.sub(r"\s+", "", str(expr))


def ast_stats(ast: dict[str, Any]) -> dict[str, Any]:
    fields: set[str] = set()
    ops: list[str] = []
    node_count = 0
    max_depth = 0

    def walk(node: dict[str, Any], depth: int) -> None:
        nonlocal node_count, max_depth
        node_count += 1
        max_depth = max(max_depth, depth)
        if node.get("node_type") == "Field":
            fields.add(str(node.get("field_name")))
        if "operator" in node:
            ops.append(str(node.get("operator")))
        for arg in node.get("args", []):
            walk(arg, depth + 1)

    walk(ast, 1)
    return {
        "node_count": node_count,
        "max_depth": max_depth,
        "field_count": len(fields),
        "operator_count": len(ops),
        "raw_inputs": ";".join(sorted(fields)),
        "operator_path": ">".join(ops),
    }


def attach_metadata(ast: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    out = dict(ast)
    out["schema_version"] = "a7ff_core_ast_v0"
    out["blueprint_id"] = row.get("blueprint_id")
    out["semantic_pair"] = row.get("semantic_pair")
    out["motif"] = row.get("motif")
    out["candidate_role"] = row.get("candidate_role")
    out["generation_priority"] = row.get("generation_priority")
    out["primary_field"] = row.get("primary_field")
    out["secondary_field"] = row.get("secondary_field")
    out["primary_semantic"] = row.get("primary_semantic")
    out["secondary_semantic"] = row.get("secondary_semantic")
    out["pit_policy"] = "inherit_from_field_contract"
    out["latency_policy"] = "inherit_from_field_contract"
    out["role_policy"] = "role_enforced_no_label_feature"
    return out


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core0 = read_json(A7FFCORE0)
    if core0.get("decision") != "PASS_A7FFCORE0_TYPED_AST_GOVERNANCE_READY_FOR_CORE1":
        raise SystemExit(f"A7FF-CORE0 is not ready: {core0.get('decision')}")
    schema = read_json(CORE0_SCHEMA)
    formula_index = pd.read_csv(REPAIRED_INDEX)

    audit_rows: list[dict[str, Any]] = []
    node_rows: list[dict[str, Any]] = []
    sample_ast: list[dict[str, Any]] = []
    for row in formula_index.to_dict("records"):
        expr = str(row["expression"])
        record: dict[str, Any] = {
            "blueprint_id": row.get("blueprint_id"),
            "expression": expr,
            "semantic_pair": row.get("semantic_pair"),
            "motif": row.get("motif"),
        }
        try:
            ast = parse_expression(expr)
            rendered = render(ast)
            stats = ast_stats(ast)
            ok = canonical(expr) == canonical(rendered)
            typed_ast = attach_metadata(ast, row)
            if len(sample_ast) < 100:
                sample_ast.append(typed_ast)
            record.update(
                {
                    "parse_ok": True,
                    "roundtrip_ok": ok,
                    "rendered_expression": rendered,
                    "error": "",
                    **stats,
                }
            )
            for field in stats["raw_inputs"].split(";") if stats["raw_inputs"] else []:
                node_rows.append(
                    {
                        "blueprint_id": row.get("blueprint_id"),
                        "node_type": "Field",
                        "node_value": field,
                        "semantic_pair": row.get("semantic_pair"),
                        "motif": row.get("motif"),
                    }
                )
            for op in stats["operator_path"].split(">") if stats["operator_path"] else []:
                node_rows.append(
                    {
                        "blueprint_id": row.get("blueprint_id"),
                        "node_type": "Operator",
                        "node_value": op,
                        "semantic_pair": row.get("semantic_pair"),
                        "motif": row.get("motif"),
                    }
                )
        except Exception as exc:
            record.update(
                {
                    "parse_ok": False,
                    "roundtrip_ok": False,
                    "rendered_expression": "",
                    "error": str(exc),
                    "node_count": 0,
                    "max_depth": 0,
                    "field_count": 0,
                    "operator_count": 0,
                    "raw_inputs": "",
                    "operator_path": "",
                }
            )
        audit_rows.append(record)

    audit = pd.DataFrame(audit_rows)
    node_inventory = pd.DataFrame(node_rows)
    family_summary = (
        audit.groupby(["semantic_pair", "motif"], dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            parse_ok=("parse_ok", "sum"),
            roundtrip_ok=("roundtrip_ok", "sum"),
            median_nodes=("node_count", "median"),
            max_depth=("max_depth", "max"),
            field_count=("field_count", "median"),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    operator_summary = (
        node_inventory[node_inventory["node_type"].eq("Operator")]
        .groupby("node_value", dropna=False)
        .size()
        .reset_index(name="operator_node_count")
        .sort_values("operator_node_count", ascending=False)
        if not node_inventory.empty
        else pd.DataFrame(columns=["node_value", "operator_node_count"])
    )
    field_summary = (
        node_inventory[node_inventory["node_type"].eq("Field")]
        .groupby("node_value", dropna=False)
        .size()
        .reset_index(name="field_node_count")
        .sort_values("field_node_count", ascending=False)
        if not node_inventory.empty
        else pd.DataFrame(columns=["node_value", "field_node_count"])
    )

    audit.to_csv(RUNTIME / "a7ffcore1_ast_roundtrip_audit.csv", index=False)
    node_inventory.to_csv(RUNTIME / "a7ffcore1_node_inventory.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore1_family_roundtrip_summary.csv", index=False)
    operator_summary.to_csv(RUNTIME / "a7ffcore1_operator_inventory.csv", index=False)
    field_summary.to_csv(RUNTIME / "a7ffcore1_field_inventory.csv", index=False)
    (RUNTIME / "a7ffcore1_sample_typed_ast.jsonl").write_text(
        "\n".join(json.dumps(x, sort_keys=True) for x in sample_ast) + "\n",
        encoding="utf-8",
    )

    parse_failures = int((~audit["parse_ok"]).sum())
    roundtrip_failures = int((~audit["roundtrip_ok"]).sum())
    blockers: list[str] = []
    if parse_failures:
        blockers.append("parse_failures_present")
    if roundtrip_failures:
        blockers.append("roundtrip_failures_present")
    if audit["raw_inputs"].eq("").any():
        blockers.append("empty_raw_inputs_present")
    decision = "PASS_A7FFCORE1_AST_SCHEMA_ADAPTER_READY_FOR_CORE2" if not blockers else "HOLD_A7FFCORE1_AST_SCHEMA_ADAPTER_FAIL"
    manifest = {
        "stage": "A7FF-CORE1",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7FF-CORE0",
        "source_decision": core0.get("decision"),
        "schema_version": schema.get("schema_version", "a7ff_core_ast_v0"),
        "input_formula_rows": int(len(formula_index)),
        "parse_ok_rows": int(audit["parse_ok"].sum()),
        "roundtrip_ok_rows": int(audit["roundtrip_ok"].sum()),
        "parse_failure_rows": parse_failures,
        "roundtrip_failure_rows": roundtrip_failures,
        "operator_types": int(operator_summary["node_value"].nunique()) if not operator_summary.empty else 0,
        "field_types": int(field_summary["node_value"].nunique()) if not field_summary.empty else 0,
        "max_ast_depth": int(audit["max_depth"].max()) if not audit.empty else 0,
        "executes_generation": False,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core2": not bool(blockers),
        "authorizes_generation": False,
        "authorizes_numeric": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE2 FeatureFactory subgraph registry" if not blockers else "A7FF-CORE1 parser repair",
    }
    write_json(RUNTIME / "a7ffcore1_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-CORE1 AST SCHEMA ADAPTER

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-CORE1 validates a typed AST adapter over the repaired A7FF-55R3 formula atlas. It parses expression strings, renders them back, and audits node inventories. It does not execute generation, numeric evaluation, replay, or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Family Roundtrip Summary

{md_table(family_summary, 80)}

## Operator Inventory

{md_table(operator_summary, 40)}

## Field Inventory

{md_table(field_summary, 60)}

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
