from __future__ import annotations

import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.feature_algebra import parse_call


DATA_ROOT = Path(os.environ.get("ALPHAFACTORY_CRYPTO_DATA_ROOT", r"G:\AlphaFactory_CryptoData"))
BASE_DIR = Path(os.environ.get("A7AL_BASE_PANEL_ROOT", str(DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v2_20260527")))
UPPER_REGIME_PANEL = DATA_ROOT / "gold" / "features" / "binance_universe498_upper_regime_state_v1_20260527.parquet"
LATENT_PANEL = DATA_ROOT / "gold" / "features" / "binance_universe498_latent_state_features_v1_20260527.parquet"
TAXONOMY = DATA_ROOT / "gold" / "metadata" / "binance_universe498_contract_meme_taxonomy_v1_20260527.csv"

SPLIT_COVERAGE = REPO / "runtime" / "a7al0_top498_alpha_search_contract" / "a7al_split_coverage_by_symbol.csv"
X3_LEDGER = REPO / "runtime" / "a7al2x3_family_balanced_dry_generation" / "a7al2x3_generated_candidate_ledger.csv"
X4M_MANIFEST = REPO / "runtime" / "a7al2x4m_materialization_and_evaluator_audit" / "a7al2x4m_manifest.json"

OUT_DIR = REPO / "runtime" / "a7al2x5_evaluator_preflight_smoke"
REPORT = REPO / "reports" / "CRYPTO_A7AL2X5_EVALUATOR_PREFLIGHT_SMOKE_20260529.md"

SYMBOL_CAP = int(os.environ.get("A7AL2X5_SYMBOL_CAP", "96"))
MIN_FINITE_SHARE = float(os.environ.get("A7AL2X5_MIN_FINITE_SHARE", "0.20"))
MIN_NONZERO_SHARE = float(os.environ.get("A7AL2X5_MIN_NONZERO_SHARE", "0.01"))


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def split_pipe(value: Any) -> list[str]:
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]


def strict_symbols() -> list[str]:
    cov = pd.read_csv(SPLIT_COVERAGE)
    symbols = (
        cov.loc[cov["search_eligibility"].eq("strict_full_history"), "symbol"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .tolist()
    )
    return sorted(symbols)[:SYMBOL_CAP]


def selected_candidates() -> pd.DataFrame:
    ledger = pd.read_csv(X3_LEDGER)
    return ledger[
        ledger["selected_for_family_balanced_preflight"].astype(str).str.lower().isin(["true", "1"])
    ].copy()


def selected_fields(selected: pd.DataFrame) -> set[str]:
    fields = {"trade_close"}
    for text in selected["fields"].dropna().astype(str):
        fields.update(split_pipe(text))
    return fields


def load_base(symbols: list[str], numeric_fields: set[str]) -> tuple[list[str], pd.DatetimeIndex, dict[str, np.ndarray]]:
    loaded_symbols: list[str] = []
    timestamps: pd.DatetimeIndex | None = None
    frames: dict[str, pd.DataFrame] = {}
    cols = ["timestamp"] + sorted(numeric_fields)
    for symbol in symbols:
        path = BASE_DIR / f"symbol={symbol}" / "part.parquet"
        if not path.exists():
            continue
        available = pd.read_parquet(path, columns=["timestamp"], engine="pyarrow").columns.tolist()
        # The first read is intentionally small; pyarrow raises on missing columns otherwise.
        frame = pd.read_parquet(path, columns=cols, engine="pyarrow")
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        frame = frame.sort_values("timestamp").drop_duplicates("timestamp")
        if timestamps is None:
            timestamps = pd.DatetimeIndex(frame["timestamp"])
        frame = frame.set_index("timestamp").reindex(timestamps)
        frames[symbol] = frame
        loaded_symbols.append(symbol)
    if timestamps is None or not loaded_symbols:
        raise RuntimeError("no base panel symbols loaded")
    matrices: dict[str, np.ndarray] = {}
    for field in sorted(numeric_fields):
        matrices[field] = np.vstack(
            [pd.to_numeric(frames[symbol][field], errors="coerce").to_numpy(dtype=np.float64) for symbol in loaded_symbols]
        )
    return loaded_symbols, timestamps, matrices


def parquet_schema(path: Path) -> set[str]:
    if not path.exists():
        return set()
    if path.is_dir():
        import pyarrow.dataset as ds

        return set(ds.dataset(str(path), format="parquet").schema.names)
    import pyarrow.parquet as pq

    return set(pq.ParquetFile(path).schema.names)


def load_latent_numeric(symbols: list[str], timestamps: pd.DatetimeIndex, numeric_fields: set[str]) -> dict[str, np.ndarray]:
    if not numeric_fields:
        return {}
    cols = ["symbol", "timestamp"] + sorted(numeric_fields)
    frame = pd.read_parquet(LATENT_PANEL, columns=cols)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame[frame["symbol"].isin(symbols)].sort_values(["symbol", "timestamp"])
    matrices: dict[str, np.ndarray] = {}
    for field in sorted(numeric_fields):
        rows = []
        for symbol in symbols:
            sub = frame.loc[frame["symbol"].eq(symbol), ["timestamp", field]].drop_duplicates("timestamp")
            sub = sub.set_index("timestamp").reindex(timestamps)
            rows.append(pd.to_numeric(sub[field], errors="coerce").to_numpy(dtype=np.float64))
        matrices[field] = np.vstack(rows)
    return matrices


def load_group_fields(symbols: list[str], timestamps: pd.DatetimeIndex, group_fields: set[str]) -> dict[str, np.ndarray]:
    groups: dict[str, np.ndarray] = {}
    if group_fields & {
        "R0_market_trend_state",
        "R1_market_volatility_state",
        "R2_market_breadth_state",
        "R3_liquidity_cycle_state",
        "R4_leverage_crowding_state",
        "R5_basis_premium_dislocation_state",
        "R6_positioning_crowding_state",
        "R7_meme_risk_on_state",
        "R8_listing_cycle_pressure_state",
        "R9_alt_vs_major_dispersion_state",
        "R10_stress_proxy_state",
    }:
        regime_cols = ["timestamp"] + sorted(
            c
            for c in group_fields
            if c.startswith("R") and c.endswith("_state")
        )
        regime = pd.read_parquet(UPPER_REGIME_PANEL, columns=regime_cols)
        regime["timestamp"] = pd.to_datetime(regime["timestamp"], utc=True)
        regime = regime.sort_values("timestamp").drop_duplicates("timestamp").set_index("timestamp").reindex(timestamps)
        for col in regime_cols:
            if col == "timestamp":
                continue
            values = regime[col].astype(object).to_numpy()
            groups[col] = np.tile(values.reshape(1, -1), (len(symbols), 1))

    static_cols = ["symbol"] + sorted(
        c for c in group_fields if c in {"liquidity_tier", "meme_contract_group", "is_multiplier_contract", "is_major"}
    )
    if len(static_cols) > 1:
        taxonomy = pd.read_csv(TAXONOMY, usecols=static_cols).set_index("symbol")
        for col in static_cols:
            if col == "symbol":
                continue
            per_symbol = taxonomy.reindex(symbols)[col].astype(str).fillna("missing").to_numpy(dtype=object)
            groups[col] = np.tile(per_symbol.reshape(-1, 1), (1, len(timestamps)))
    return groups


def shift_matrix(values: np.ndarray, periods: int) -> np.ndarray:
    out = np.full_like(values, np.nan, dtype=np.float64)
    if periods == 0:
        return values.astype(np.float64, copy=True)
    if periods > 0:
        out[:, periods:] = values[:, :-periods]
    else:
        p = abs(periods)
        out[:, :-p] = values[:, p:]
    return out


def rolling_mean(values: np.ndarray, window: int) -> np.ndarray:
    w = max(1, int(window))
    min_periods = max(2, min(w, 24))
    valid = np.isfinite(values)
    x = np.where(valid, values, 0.0)
    csum = np.concatenate([np.zeros((x.shape[0], 1), dtype=np.float64), np.cumsum(x, axis=1)], axis=1)
    ccnt = np.concatenate([np.zeros((x.shape[0], 1), dtype=np.float64), np.cumsum(valid.astype(np.float64), axis=1)], axis=1)
    end = np.arange(1, x.shape[1] + 1)
    start = np.maximum(0, end - w)
    total = csum[:, end] - csum[:, start]
    count = ccnt[:, end] - ccnt[:, start]
    out = np.full_like(values, np.nan, dtype=np.float64)
    np.divide(total, count, out=out, where=count >= min_periods)
    out[count < min_periods] = np.nan
    return out


def cs_zscore(values: np.ndarray) -> np.ndarray:
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = np.nanmean(values, axis=0, keepdims=True)
        std = np.nanstd(values, axis=0, ddof=1, keepdims=True)
        out = (values - mean) / std
    out[~np.isfinite(out)] = np.nan
    return out


def cs_rank_pct(values: np.ndarray) -> np.ndarray:
    return pd.DataFrame(values).rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)


def group_demean(values: np.ndarray, groups: np.ndarray, min_group: int = 3) -> np.ndarray:
    out = np.full_like(values, np.nan, dtype=np.float64)
    for t in range(values.shape[1]):
        col = values[:, t]
        grp = groups[:, t].astype(str)
        valid = np.isfinite(col) & pd.notna(grp)
        if not valid.any():
            continue
        for g in np.unique(grp[valid]):
            idx = valid & (grp == g)
            if idx.sum() < min_group:
                continue
            out[idx, t] = col[idx] - np.nanmean(col[idx])
    return out


def group_rank(values: np.ndarray, groups: np.ndarray, min_group: int = 3) -> np.ndarray:
    out = np.full_like(values, np.nan, dtype=np.float64)
    for t in range(values.shape[1]):
        col = values[:, t]
        grp = groups[:, t].astype(str)
        valid = np.isfinite(col) & pd.notna(grp)
        for g in np.unique(grp[valid]):
            idx = valid & (grp == g)
            if idx.sum() < min_group:
                continue
            out[idx, t] = pd.Series(col[idx]).rank(pct=True, method="average").to_numpy(dtype=np.float64)
    return out


class StateAwareEvaluator:
    def __init__(self, numeric_fields: dict[str, np.ndarray], group_fields: dict[str, np.ndarray]) -> None:
        self.numeric_fields = numeric_fields
        self.group_fields = group_fields
        self.cache: dict[str, np.ndarray] = {}

    def eval(self, expression: str) -> np.ndarray:
        expression = expression.strip()
        if expression in self.cache:
            return self.cache[expression]
        result = self._eval(expression)
        self.cache[expression] = result
        return result

    def group(self, name: str) -> np.ndarray:
        if name not in self.group_fields:
            raise ValueError(f"unknown group field: {name}")
        return self.group_fields[name]

    def _eval(self, expression: str) -> np.ndarray:
        call = parse_call(expression)
        if call is None:
            if expression not in self.numeric_fields:
                raise ValueError(f"unknown numeric field: {expression}")
            return self.numeric_fields[expression].astype(np.float64, copy=False)

        name, args = call
        if name == "Mean":
            return rolling_mean(self.eval(args[0]), int(args[1]))
        if name == "Delta":
            values = self.eval(args[0])
            return values - shift_matrix(values, int(args[1]))
        if name in {"Rank", "CSRank"}:
            return cs_rank_pct(self.eval(args[0]))
        if name == "ZScore":
            return cs_zscore(self.eval(args[0]))
        if name == "Mul":
            return self.eval(args[0]) * self.eval(args[1])
        if name == "Sub":
            return self.eval(args[0]) - self.eval(args[1])
        if name == "Add":
            return self.eval(args[0]) + self.eval(args[1])
        if name == "Neg":
            return -self.eval(args[0])
        if name == "Abs":
            return np.abs(self.eval(args[0]))
        if name == "Sign":
            return np.sign(self.eval(args[0]))
        if name == "SafeDiv":
            denom = self.eval(args[1])
            out = np.full_like(denom, np.nan, dtype=np.float64)
            np.divide(self.eval(args[0]), denom, out=out, where=np.abs(denom) > 1e-12)
            return out
        if name in {"Clip", "Winsor"}:
            return np.clip(self.eval(args[0]), -5.0, 5.0)
        if name == "StateMask":
            groups = self.group(args[0])
            return (groups.astype(str) == str(args[1])).astype(np.float64)
        if name == "GroupNeutralize":
            return group_demean(self.eval(args[0]), self.group(args[1]))
        if name == "LatentNeutralRank":
            return group_rank(self.eval(args[0]), self.group(args[1]))
        raise ValueError(f"unsupported operator: {name}")


def write_report(manifest: dict[str, Any], summary: pd.DataFrame, op: pd.DataFrame, groups: pd.DataFrame, blockers: pd.DataFrame) -> None:
    lines = [
        "# CRYPTO A7AL-2X5 EVALUATOR PREFLIGHT SMOKE",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "This stage evaluates A7AL-2X3 selected expressions on a bounded strict-universe sample. It does not compute returns, replay, candidate promotion, search, or proof.",
        "",
        "## Summary",
        "",
        f"- selected candidates evaluated: {manifest['evaluated_candidates']}",
        f"- eval failures: {manifest['eval_failure_count']}",
        f"- activity failures: {manifest['activity_failure_count']}",
        f"- symbols loaded: {manifest['symbols_loaded']}",
        f"- timestamps: {manifest['timestamps']}",
        "",
        "## Candidate Evaluation Summary",
        "",
        md_table(summary, 80),
        "",
        "## Operator Coverage",
        "",
        md_table(op),
        "",
        "## Group Field Coverage",
        "",
        md_table(groups),
        "",
        "## Blockers",
        "",
        md_table(blockers) if not blockers.empty else "No blockers.",
        "",
        "## Authorization",
        "",
        "- numeric replay: not authorized",
        "- formula generation/search: not authorized",
        "- alpha proof / shadow / paper / live: not authorized",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    selected = selected_candidates()
    fields = selected_fields(selected)
    group_field_names = {
        f
        for f in fields
        if (f.startswith("R") and f.endswith("_state"))
        or f in {"liquidity_tier", "meme_contract_group", "is_multiplier_contract", "is_major"}
    }
    numeric_field_names = fields - group_field_names
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    base_numeric_fields = {field for field in numeric_field_names if field in base_schema}
    latent_numeric_fields = {field for field in numeric_field_names if field in latent_schema and field not in base_numeric_fields}
    missing_numeric_fields = sorted(numeric_field_names - base_numeric_fields - latent_numeric_fields)

    symbols = strict_symbols()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_numeric_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_numeric_fields))
    groups = load_group_fields(loaded_symbols, timestamps, group_field_names)

    if missing_numeric_fields:
        raise RuntimeError(f"missing numeric fields for X5 materialization: {missing_numeric_fields}")

    evaluator = StateAwareEvaluator(numeric, groups)
    rows: list[dict[str, Any]] = []
    op_counter: Counter[str] = Counter()
    blockers: list[dict[str, Any]] = []

    for row in selected.to_dict("records"):
        expression = str(row["expression"])
        for op in split_pipe(row["operator_signature"]):
            op_counter[op] += 1
        try:
            values = evaluator.eval(expression)
            finite = np.isfinite(values)
            finite_share = float(finite.mean()) if values.size else 0.0
            nonzero_share = float((np.abs(values[finite]) > 1e-12).mean()) if finite.any() else 0.0
            min_value = float(np.nanmin(values)) if finite.any() else np.nan
            max_value = float(np.nanmax(values)) if finite.any() else np.nan
            eval_success = True
            error = ""
        except Exception as exc:  # noqa: BLE001 - audit should record all evaluator failures.
            finite_share = 0.0
            nonzero_share = 0.0
            min_value = np.nan
            max_value = np.nan
            eval_success = False
            error = repr(exc)
        activity_ok = eval_success and finite_share >= MIN_FINITE_SHARE and nonzero_share >= MIN_NONZERO_SHARE
        if not eval_success:
            blockers.append({"blocker": "eval_failure", "candidate_id": row["candidate_id"], "detail": error})
        elif not activity_ok:
            blockers.append(
                {
                    "blocker": "activity_or_coverage_failure",
                    "candidate_id": row["candidate_id"],
                    "detail": f"finite={finite_share:.4f};nonzero={nonzero_share:.4f}",
                }
            )
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "objective_family": row["objective_family"],
                "expression": expression,
                "operator_signature": row["operator_signature"],
                "eval_success": eval_success,
                "finite_share": finite_share,
                "nonzero_share": nonzero_share,
                "activity_ok": activity_ok,
                "min_value": min_value,
                "max_value": max_value,
                "error": error,
            }
        )

    summary = pd.DataFrame(rows)
    op = pd.DataFrame([{"operator": key, "selected_candidate_count": value} for key, value in sorted(op_counter.items())])
    group_rows = []
    for field, matrix in groups.items():
        vals = sorted(pd.Series(matrix.reshape(-1)).dropna().astype(str).unique().tolist())
        group_rows.append({"group_field": field, "unique_values": len(vals), "values": "|".join(vals[:80])})
    groups_df = pd.DataFrame(group_rows)
    blockers_df = pd.DataFrame(blockers)

    eval_failure_count = int((~summary["eval_success"]).sum())
    activity_failure_count = int((~summary["activity_ok"]).sum())
    decision = (
        "PASS_A7AL2X5_EVALUATOR_PREFLIGHT_SMOKE_READY_FOR_SMALL_REPLAY_CONTRACT"
        if eval_failure_count == 0 and activity_failure_count == 0
        else "HOLD_A7AL2X5_EVALUATOR_OR_ACTIVITY_FAILURE"
    )

    manifest = {
        "stage": "A7AL-2X5",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_numeric_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "input_x4m_decision": json.loads(X4M_MANIFEST.read_text(encoding="utf-8")).get("decision") if X4M_MANIFEST.exists() else "",
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "evaluated_candidates": int(len(summary)),
        "eval_failure_count": eval_failure_count,
        "activity_failure_count": activity_failure_count,
        "group_field_count": int(len(groups)),
        "numeric_field_count": int(len(numeric)),
        "base_numeric_field_count": int(len(base_numeric_fields)),
        "latent_numeric_field_count": int(len(latent_numeric_fields)),
        "blockers": blockers_df["blocker"].drop_duplicates().tolist() if not blockers_df.empty else [],
    }

    summary.to_csv(OUT_DIR / "a7al2x5_candidate_eval_summary.csv", index=False)
    op.to_csv(OUT_DIR / "a7al2x5_operator_coverage.csv", index=False)
    groups_df.to_csv(OUT_DIR / "a7al2x5_group_field_coverage.csv", index=False)
    blockers_df.to_csv(OUT_DIR / "a7al2x5_blocker_matrix.csv", index=False)
    write_json(OUT_DIR / "a7al2x5_manifest.json", manifest)
    write_json(
        OUT_DIR / "a7al2x5_authorization_matrix.json",
        {
            "A7AL-2X5": {"status": decision},
            "small_numeric_replay_contract": {"authorized": decision.startswith("PASS"), "note": "contract only; execution still requires explicit next stage"},
            "numeric_replay_execution": {"authorized": False},
            "formula_generation": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    write_report(manifest, summary, op, groups_df, blockers_df)


if __name__ == "__main__":
    main()
