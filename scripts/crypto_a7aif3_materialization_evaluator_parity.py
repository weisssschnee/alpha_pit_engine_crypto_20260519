from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra
from alphafactory_crypto.engines.formula_gen_v2_adapter import load_field_enforcement_csv


RUNTIME = REPO / "runtime" / "a7aif3_materialization_evaluator_parity"
REPORT = REPO / "reports" / "CRYPTO_A7AIF3_MATERIALIZATION_EVALUATOR_PARITY_20260529.md"
A7AIF2 = REPO / "runtime" / "a7aif2_field_enforcement_regression" / "a7aif2_manifest.json"
LEDGER_PATH = REPO / "runtime" / "a7aif0_field_contract_enforcement_ledger" / "a7aif0_semantic_field_enforcement_ledger.csv"

OPERATORS = {
    "Mean": "Mean(mark_index_basis_bps,4)",
    "Delta": "Delta(mark_index_basis_bps,4)",
    "ZScore": "ZScore(mark_index_basis_bps)",
    "Rank": "Rank(mark_index_basis_bps)",
    "CSRank": "CSRank(mark_index_basis_bps)",
    "Mul": "Mul(ZScore(mark_index_basis_bps),Rank(premium_close_bps))",
    "Sub": "Sub(ZScore(mark_index_basis_bps),ZScore(premium_close_bps))",
    "Add": "Add(ZScore(mark_index_basis_bps),ZScore(premium_close_bps))",
    "Neg": "Neg(ZScore(mark_index_basis_bps))",
    "Abs": "Abs(ZScore(mark_index_basis_bps))",
    "Sign": "Sign(Delta(mark_index_basis_bps,4))",
    "SafeDiv": "SafeDiv(ZScore(mark_index_basis_bps),Abs(ZScore(premium_close_bps)))",
    "Clip": "Clip(ZScore(mark_index_basis_bps),-2,2)",
    "TSRank": "TSRank(mark_index_basis_bps,24)",
    "Decay": "Decay(mark_index_basis_bps,24)",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def synthetic_frame(fields: list[str]) -> pd.DataFrame:
    timestamps = list(range(64))
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
    rows = []
    for si, symbol in enumerate(symbols):
        for ts in timestamps:
            row: dict[str, Any] = {"symbol": symbol, "timestamp": ts}
            for fi, field in enumerate(fields):
                row[field] = float(np.sin(ts / (3 + fi % 7)) + np.cos((si + 1) * (fi + 1) / 5) + 0.01 * ts + 0.1 * si)
            rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    f2 = read_json(A7AIF2)
    if not f2.get("authorizes_a7aif3"):
        raise SystemExit("A7AI-F2 does not authorize A7AI-F3")
    ledger = load_field_enforcement_csv(LEDGER_PATH)
    ledger_df = pd.DataFrame(ledger.values())
    allowed_fields = sorted(
        ledger_df.loc[
            ledger_df["generator_allowed_any_mode"].astype(str).str.lower().isin(["true", "1"]),
            "field_name",
        ].astype(str).tolist()
    )
    eval_fields = sorted(set(allowed_fields) | {"mark_index_basis_bps", "premium_close_bps"})
    frame = synthetic_frame(eval_fields)
    evaluator = CryptoFeatureAlgebra(frame[["symbol", "timestamp", *eval_fields]].copy(), set(eval_fields), field_contract=ledger)
    plain = CryptoFeatureAlgebra(frame[["symbol", "timestamp", *eval_fields]].copy(), set(eval_fields))

    field_rows = []
    for field in eval_fields:
        row = ledger.get(field, {})
        try:
            result = evaluator.evaluate(field)
            materialized = result.diagnostics["finite_rows"] > 0
            error = ""
        except Exception as exc:
            materialized = False
            error = str(exc)
        field_rows.append(
            {
                "field_name": field,
                "semantic_role": row.get("semantic_role", ""),
                "ordinary_alpha_allowed": row.get("ordinary_alpha_allowed", ""),
                "diagnostic_allowed": row.get("diagnostic_allowed", ""),
                "risk_defense_allowed": row.get("risk_defense_allowed", ""),
                "resolution": "resolved" if materialized else "unsupported",
                "error": error,
            }
        )

    operator_rows = []
    consistency_rows = []
    for op, expr in OPERATORS.items():
        try:
            result = evaluator.evaluate(expr)
            plain_result = plain.evaluate(expr)
            finite = int(result.diagnostics["finite_rows"])
            max_abs_diff = float((result.values - plain_result.values).abs().max(skipna=True))
            passed = finite > 0 and (np.isnan(max_abs_diff) or max_abs_diff < 1e-12)
            error = ""
        except Exception as exc:
            finite = 0
            max_abs_diff = np.nan
            passed = False
            error = str(exc)
        operator_rows.append(
            {
                "operator": op,
                "expression": expr,
                "supported": passed,
                "finite_rows": finite,
                "max_abs_diff_contract_vs_plain": max_abs_diff,
                "error": error,
                "resolution": "resolved" if passed else "forbidden_until_supported",
            }
        )
        consistency_rows.append(
            {
                "expression": expr,
                "operator": op,
                "consistent": passed,
                "max_abs_diff": max_abs_diff,
                "error": error,
            }
        )

    field_df = pd.DataFrame(field_rows)
    operator_df = pd.DataFrame(operator_rows)
    consistency_df = pd.DataFrame(consistency_rows)
    blocking_fields = field_df[field_df["resolution"].ne("resolved")].copy()
    blocking_ops = operator_df[~operator_df["supported"]].copy()
    blockers = []
    if not blocking_fields.empty:
        blockers.append("blocking_fields_remain")
    if not blocking_ops.empty:
        blockers.append("operator_parity_fail")
    decision = "PASS_A7AIF3_REPLAY_MATERIALIZATION_PARITY_READY" if not blockers else "HOLD_A7AIF3_MATERIALIZATION_PARITY_BLOCKERS"
    manifest = {
        "stage": "A7AI-F3",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "field_count": int(len(field_df)),
        "operator_count": int(len(operator_df)),
        "blocking_field_count": int(len(blocking_fields)),
        "blocking_operator_count": int(len(blocking_ops)),
        "authorizes_a7aa": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    field_df.to_csv(RUNTIME / "a7aif3_field_materialization_matrix.csv", index=False)
    blocking_fields.to_csv(RUNTIME / "a7aif3_blocking_field_resolution.csv", index=False)
    operator_df.to_csv(RUNTIME / "a7aif3_operator_parity_matrix.csv", index=False)
    blocking_ops.to_csv(RUNTIME / "a7aif3_blocking_operator_resolution.csv", index=False)
    consistency_df.to_csv(RUNTIME / "a7aif3_eval_consistency_sample.csv", index=False)
    write_json(RUNTIME / "a7aif3_manifest.json", manifest)
    if not blocking_ops.empty:
        blocking_ops[["operator", "resolution", "error"]].to_csv(RUNTIME / "a7aif3_forbidden_operator_registry.csv", index=False)
    else:
        pd.DataFrame(columns=["operator", "resolution", "error"]).to_csv(RUNTIME / "a7aif3_forbidden_operator_registry.csv", index=False)
    lines = [
        "# CRYPTO A7AI-F3 MATERIALIZATION EVALUATOR PARITY",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Field Materialization",
        "",
        md_table(field_df, 80),
        "",
        "## Operator Parity",
        "",
        md_table(operator_df, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "This is a synthetic materialization/evaluator parity sprint only.",
        "No formula search, full replay, alpha proof, shadow, paper, or live execution is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
