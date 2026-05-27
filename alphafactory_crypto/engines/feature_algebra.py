from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True, slots=True)
class EvalResult:
    values: pd.Series
    diagnostics: dict[str, Any]


def split_args(body: str) -> list[str]:
    args: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(body):
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            args.append(body[start:index].strip())
            start = index + 1
    args.append(body[start:].strip())
    return args


def parse_call(expression: str) -> tuple[str, list[str]] | None:
    text = expression.strip()
    match = re.match(r"^([A-Za-z][A-Za-z0-9_]*)\((.*)\)$", text)
    if not match:
        return None
    return match.group(1), split_args(match.group(2))


def _group_symbol(values: pd.Series, frame: pd.DataFrame) -> pd.core.groupby.SeriesGroupBy:
    return values.groupby(frame["symbol"], sort=False)


def _rolling_mean(values: pd.Series, frame: pd.DataFrame, window: int) -> pd.Series:
    return (
        _group_symbol(values, frame)
        .rolling(window=max(1, int(window)), min_periods=max(2, min(int(window), 24)))
        .mean()
        .reset_index(level=0, drop=True)
        .reindex(values.index)
    )


def _delta(values: pd.Series, frame: pd.DataFrame, window: int) -> pd.Series:
    return _group_symbol(values, frame).diff(max(1, int(window))).reindex(values.index)


def _cross_sectional_rank(values: pd.Series, frame: pd.DataFrame) -> pd.Series:
    return values.groupby(frame["timestamp"], sort=False).rank(pct=True, method="average")


def _cross_sectional_zscore(values: pd.Series, frame: pd.DataFrame) -> pd.Series:
    grouped = values.groupby(frame["timestamp"], sort=False)
    mean = grouped.transform("mean")
    std = grouped.transform("std").replace(0.0, np.nan)
    return (values - mean) / std


def _to_numeric(values: pd.Series) -> pd.Series:
    return pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan)


class CryptoFeatureAlgebra:
    """Small crypto-safe evaluator for CN-style formula smoke tests.

    Semantics are deliberately explicit:
    - Mean/Delta are trailing per-symbol operators.
    - Rank/ZScore are cross-sectional by timestamp.
    - No same-bar execution is implied by this evaluator; timing is audited by
      the caller through feature_available_time/execution_time shifts.
    """

    def __init__(self, frame: pd.DataFrame, allowed_fields: set[str]) -> None:
        required = {"symbol", "timestamp"}
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"frame missing required columns: {sorted(missing)}")
        self.frame = frame.sort_values(["symbol", "timestamp"]).reset_index(drop=True).copy()
        self.allowed_fields = allowed_fields

    def evaluate(self, expression: str) -> EvalResult:
        values = self._eval(expression.strip())
        values = _to_numeric(values)
        diagnostics = self.diagnostics(values)
        return EvalResult(values=values, diagnostics=diagnostics)

    def diagnostics(self, values: pd.Series) -> dict[str, Any]:
        finite = np.isfinite(values.to_numpy(dtype=float, na_value=np.nan))
        non_null = values.notna()
        active = non_null & (values.abs() > 1e-12)
        return {
            "rows": int(len(values)),
            "non_null_rows": int(non_null.sum()),
            "finite_rows": int(finite.sum()),
            "nan_rows": int(values.isna().sum()),
            "inf_rows": int(np.isinf(values.to_numpy(dtype=float, na_value=np.nan)).sum()),
            "active_rows": int(active.sum()),
            "non_null_ratio": round(float(non_null.mean()), 6) if len(values) else 0.0,
            "active_ratio": round(float(active.mean()), 6) if len(values) else 0.0,
            "std": round(float(values.std(skipna=True)), 10) if non_null.any() else math.nan,
        }

    def _eval(self, expression: str) -> pd.Series:
        call = parse_call(expression)
        if call is None:
            if expression not in self.allowed_fields:
                raise ValueError(f"unknown field: {expression}")
            if expression not in self.frame.columns:
                raise ValueError(f"field not present in frame: {expression}")
            return _to_numeric(self.frame[expression])

        name, args = call
        if name == "Mean":
            if len(args) != 2:
                raise ValueError(f"Mean expects 2 args: {expression}")
            return _rolling_mean(self._eval(args[0]), self.frame, int(args[1]))
        if name == "Delta":
            if len(args) != 2:
                raise ValueError(f"Delta expects 2 args: {expression}")
            return _delta(self._eval(args[0]), self.frame, int(args[1]))
        if name in {"Rank", "CSRank"}:
            if len(args) != 1:
                raise ValueError(f"{name} expects 1 arg: {expression}")
            return _cross_sectional_rank(self._eval(args[0]), self.frame)
        if name == "ZScore":
            if len(args) != 1:
                raise ValueError(f"ZScore expects 1 arg: {expression}")
            return _cross_sectional_zscore(self._eval(args[0]), self.frame)
        if name == "Mul":
            if len(args) != 2:
                raise ValueError(f"Mul expects 2 args: {expression}")
            return self._eval(args[0]) * self._eval(args[1])
        if name == "Sub":
            if len(args) != 2:
                raise ValueError(f"Sub expects 2 args: {expression}")
            return self._eval(args[0]) - self._eval(args[1])
        if name == "Add":
            if len(args) != 2:
                raise ValueError(f"Add expects 2 args: {expression}")
            return self._eval(args[0]) + self._eval(args[1])
        if name == "Neg":
            if len(args) != 1:
                raise ValueError(f"Neg expects 1 arg: {expression}")
            return -self._eval(args[0])
        if name == "Abs":
            if len(args) != 1:
                raise ValueError(f"Abs expects 1 arg: {expression}")
            return self._eval(args[0]).abs()
        if name == "Sign":
            if len(args) != 1:
                raise ValueError(f"Sign expects 1 arg: {expression}")
            return np.sign(self._eval(args[0]))
        raise ValueError(f"unsupported operator: {name}")
