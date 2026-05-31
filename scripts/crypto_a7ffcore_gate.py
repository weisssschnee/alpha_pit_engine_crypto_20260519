from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CORE2_RUNTIME = REPO / "runtime" / "a7ffcore2_feature_subgraph_registry"
CORE3_RUNTIME = REPO / "runtime" / "a7ffcore3_formula_gen_subgraph_gate"

TOKEN_RE = re.compile(r"\s+")


def canonical_expression(expression: str) -> str:
    return TOKEN_RE.sub("", str(expression))


class FormulaGenSubgraphGate:
    """Fail-closed gate for FormulaGen candidates.

    The gate is intentionally simple: a candidate must resolve to a CORE2
    approved subgraph id or to an expression already present in the approved
    CORE2 registry. New raw-expression construction remains disallowed until a
    future CORE stage explicitly wires a gate-native generator.
    """

    def __init__(
        self,
        reusable_path: Path | None = None,
        roots_path: Path | None = None,
        policy_path: Path | None = None,
    ) -> None:
        reusable_path = reusable_path or CORE2_RUNTIME / "a7ffcore2_reusable_feature_subgraphs.csv"
        roots_path = roots_path or CORE2_RUNTIME / "a7ffcore2_factor_candidate_roots.csv"
        policy_path = policy_path or CORE3_RUNTIME / "a7ffcore3_formula_gen_gate_policy.json"
        self.reusable = pd.read_csv(reusable_path)
        self.roots = pd.read_csv(roots_path)
        self.policy = json.loads(policy_path.read_text(encoding="utf-8")) if policy_path.exists() else {}

        approved_reusable = self.reusable[
            self.reusable["formula_gen_gate"].eq("feature_factory_reusable_subgraph")
            & self.reusable["feature_factory_allowed"].astype(bool)
        ].copy()
        diagnostic_roots = self.roots[self.roots["formula_gen_gate"].eq("diagnostic_or_repair_root_only")].copy()

        self.reusable_ids = set(approved_reusable["subgraph_id"].astype(str))
        self.reusable_expr = {
            canonical_expression(expr): subgraph_id
            for subgraph_id, expr in zip(approved_reusable["subgraph_id"].astype(str), approved_reusable["expression"].astype(str))
        }
        self.root_ids = set(diagnostic_roots["subgraph_id"].astype(str))
        self.root_expr = {
            canonical_expression(expr): subgraph_id
            for subgraph_id, expr in zip(diagnostic_roots["subgraph_id"].astype(str), diagnostic_roots["expression"].astype(str))
        }

    def validate(
        self,
        *,
        expression: str | None = None,
        subgraph_id: str | None = None,
        mode: str = "ordinary_alpha",
    ) -> dict[str, Any]:
        if mode not in {"ordinary_alpha", "diagnostic_repair"}:
            return self._reject("unknown_mode", expression, subgraph_id, mode)

        if subgraph_id:
            sid = str(subgraph_id)
            if sid in self.reusable_ids:
                return self._accept("approved_reusable_subgraph_id", sid, expression, mode)
            if mode == "diagnostic_repair" and sid in self.root_ids:
                return self._accept("approved_diagnostic_root_id", sid, expression, mode)
            return self._reject("subgraph_id_not_allowed_for_mode", expression, sid, mode)

        if expression is None or str(expression).strip() == "":
            return self._reject("missing_expression_or_subgraph_id", expression, subgraph_id, mode)

        canonical = canonical_expression(expression)
        if canonical in self.reusable_expr:
            return self._accept("approved_reusable_expression", self.reusable_expr[canonical], expression, mode)
        if mode == "diagnostic_repair" and canonical in self.root_expr:
            return self._accept("approved_diagnostic_root_expression", self.root_expr[canonical], expression, mode)
        return self._reject("expression_not_in_core2_registry", expression, subgraph_id, mode)

    @staticmethod
    def _accept(reason: str, subgraph_id: str, expression: str | None, mode: str) -> dict[str, Any]:
        return {
            "allowed": True,
            "reason": reason,
            "mode": mode,
            "resolved_subgraph_id": subgraph_id,
            "expression": expression or "",
        }

    @staticmethod
    def _reject(reason: str, expression: str | None, subgraph_id: str | None, mode: str) -> dict[str, Any]:
        return {
            "allowed": False,
            "reason": reason,
            "mode": mode,
            "resolved_subgraph_id": "",
            "expression": expression or "",
            "subgraph_id": subgraph_id or "",
        }
