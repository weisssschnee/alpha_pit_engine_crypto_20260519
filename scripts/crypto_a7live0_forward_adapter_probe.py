from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra  # noqa: E402
from scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair import strict_symbols  # noqa: E402


DATA_ROOT = Path(os.environ.get("ALPHAFACTORY_CRYPTO_DATA_ROOT", r"G:\AlphaFactory_CryptoData"))
DEFAULT_PATCH_ROOT = DATA_ROOT / "gold" / "features" / "binance_universe498_recent_patch_1h_v1_20260612"
DEFAULT_PACKET = REPO / "runtime" / "a7shadow7_dedup_review_packet_20260704" / "a7shadow7_selected_review_packet.csv"
DEFAULT_RUNTIME = REPO / "runtime" / "a7live0_forward_adapter_probe_20260704"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7LIVE0_FORWARD_ADAPTER_PROBE_20260704.md"
FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
OPERATORS = {
    "Abs",
    "Add",
    "CSRank",
    "Decay",
    "Delta",
    "Mean",
    "Mul",
    "Neg",
    "Rank",
    "SafeDiv",
    "Sign",
    "Sub",
    "TSRank",
    "ZScore",
}
PATCH_RENAMES = {
    "open": "trade_open",
    "high": "trade_high",
    "low": "trade_low",
    "close": "trade_close",
    "volume": "trade_volume",
    "quote_volume": "trade_quote_volume",
    "premium_bps": "premium_close_bps",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def expression_fields(expression: str) -> set[str]:
    return {
        token
        for token in FIELD_RE.findall(str(expression))
        if token not in OPERATORS and token.lower() not in {"nan", "inf"}
    }


def read_symbol_patch(root: Path, symbol: str) -> pd.DataFrame:
    part_dir = root / f"symbol={symbol}"
    paths = sorted(part_dir.glob("*.parquet"))
    if not paths:
        return pd.DataFrame()
    frame = pd.concat((pd.read_parquet(path, engine="pyarrow") for path in paths), ignore_index=True, sort=False)
    frame = frame.rename(columns={k: v for k, v in PATCH_RENAMES.items() if k in frame.columns})
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True).dt.tz_localize(None)
    if "symbol" not in frame.columns:
        frame["symbol"] = symbol
    return frame.sort_values(["symbol", "timestamp"]).drop_duplicates(["symbol", "timestamp"], keep="last")


def dense_funding_delta(frame: pd.DataFrame) -> pd.Series:
    funding = pd.to_numeric(frame["funding_rate"], errors="coerce")
    dense = funding.groupby(frame["symbol"], sort=False).ffill(limit=8)
    return dense - dense.groupby(frame["symbol"], sort=False).shift(24)


def build_frame(root: Path, symbols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    frames: list[pd.DataFrame] = []
    symbol_rows: list[dict[str, Any]] = []
    for symbol in symbols:
        frame = read_symbol_patch(root, symbol)
        if frame.empty:
            symbol_rows.append({"symbol": symbol, "status": "missing_patch_part", "rows": 0})
            continue
        frames.append(frame)
        symbol_rows.append(
            {
                "symbol": symbol,
                "status": "ok",
                "rows": int(frame.shape[0]),
                "timestamp_start": frame["timestamp"].min().isoformat(),
                "timestamp_end": frame["timestamp"].max().isoformat(),
            }
        )
    if not frames:
        return pd.DataFrame(), pd.DataFrame(symbol_rows)
    panel = pd.concat(frames, ignore_index=True, sort=False)
    panel = panel.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    if "funding_rate" in panel.columns:
        panel["funding_rate_delta_state_24h"] = dense_funding_delta(panel)
    return panel, pd.DataFrame(symbol_rows)


def field_health(panel: pd.DataFrame, fields: set[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for field in sorted(fields):
        if field not in panel.columns:
            rows.append({"field": field, "status": "MISSING", "finite_share": np.nan, "active_share": np.nan})
            continue
        values = pd.to_numeric(panel[field], errors="coerce").to_numpy(dtype=float)
        finite = np.isfinite(values)
        active = finite & (np.abs(values) > 1e-12)
        rows.append(
            {
                "field": field,
                "status": "OK",
                "finite_share": float(finite.mean()) if values.size else np.nan,
                "active_share": float(active.mean()) if values.size else np.nan,
            }
        )
    return pd.DataFrame(rows)


def evaluate_packet(panel: pd.DataFrame, packet: pd.DataFrame) -> pd.DataFrame:
    fields = set().union(*(expression_fields(expr) for expr in packet["expression"].astype(str)))
    evaluator = CryptoFeatureAlgebra(panel, allowed_fields=fields)
    rows: list[dict[str, Any]] = []
    for row in packet.to_dict("records"):
        expression = str(row["expression"])
        try:
            result = evaluator.evaluate(expression)
            diag = result.diagnostics
            rows.append(
                {
                    "candidate_key": row.get("candidate_key", f"{row['blueprint_id']}|h{int(row['horizon_h'])}"),
                    "blueprint_id": row["blueprint_id"],
                    "horizon_h": int(row["horizon_h"]),
                    "expression": expression,
                    "eval_success": True,
                    "error": "",
                    **diag,
                }
            )
        except Exception as exc:  # noqa: BLE001
            rows.append(
                {
                    "candidate_key": row.get("candidate_key", f"{row['blueprint_id']}|h{int(row['horizon_h'])}"),
                    "blueprint_id": row["blueprint_id"],
                    "horizon_h": int(row["horizon_h"]),
                    "expression": expression,
                    "eval_success": False,
                    "error": repr(exc),
                    "rows": int(panel.shape[0]),
                    "finite_rows": 0,
                    "finite_ratio": 0.0,
                    "active_ratio": 0.0,
                }
            )
    return pd.DataFrame(rows)


def build(runtime: Path, report: Path, patch_root: Path, packet_path: Path, symbol_cap: int) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    packet = pd.read_csv(packet_path)
    symbols = strict_symbols()[:symbol_cap]
    panel, symbol_coverage = build_frame(patch_root, symbols)
    if panel.empty:
        raise SystemExit(f"no patch panel loaded from {patch_root}")
    fields = set().union(*(expression_fields(expr) for expr in packet["expression"].astype(str)))
    health = field_health(panel, fields)
    evals = evaluate_packet(panel, packet)

    symbol_coverage.to_csv(runtime / "a7live0_symbol_patch_coverage.csv", index=False)
    health.to_csv(runtime / "a7live0_field_health.csv", index=False)
    evals.to_csv(runtime / "a7live0_formula_materialization.csv", index=False)

    eval_errors = int((~evals["eval_success"].astype(bool)).sum())
    min_field_finite = float(health["finite_share"].min()) if not health.empty else np.nan
    min_formula_finite = float(evals["non_null_ratio"].min()) if "non_null_ratio" in evals.columns and not evals.empty else np.nan
    min_formula_active = float(evals["active_ratio"].min()) if "active_ratio" in evals.columns and not evals.empty else np.nan
    missing_fields = health.loc[health["status"].ne("OK"), "field"].astype(str).tolist()
    blockers: list[str] = []
    warnings: list[str] = []
    if missing_fields:
        blockers.append("missing_forward_fields")
    if eval_errors:
        blockers.append("formula_eval_errors")
    if np.isfinite(min_field_finite) and min_field_finite < 0.90:
        blockers.append("forward_field_finite_share_below_90pct")
    if np.isfinite(min_formula_finite) and min_formula_finite < 0.20:
        blockers.append("formula_materialization_finite_share_below_20pct")
    if np.isfinite(min_formula_active) and min_formula_active < 0.01:
        blockers.append("formula_materialization_active_share_below_1pct")
    if panel["timestamp"].nunique() < 168:
        warnings.append("forward_window_lt_168h")

    decision = "PASS_A7LIVE0_FORWARD_ADAPTER_PROBE_READY" if not blockers else "HOLD_A7LIVE0_FORWARD_ADAPTER_PROBE_BLOCKED"
    manifest = {
        "stage": "A7LIVE-0",
        "generated_at": now_utc(),
        "decision": decision,
        "patch_root": str(patch_root),
        "packet_path": str(packet_path),
        "symbol_count": len(symbols),
        "loaded_symbol_count": int(symbol_coverage["status"].eq("ok").sum()),
        "row_count": int(panel.shape[0]),
        "timestamp_start": panel["timestamp"].min().isoformat(),
        "timestamp_end": panel["timestamp"].max().isoformat(),
        "timestamp_count": int(panel["timestamp"].nunique()),
        "candidate_count": int(packet.shape[0]),
        "eval_error_count": eval_errors,
        "missing_fields": missing_fields,
        "min_field_finite_share": min_field_finite,
        "min_formula_non_null_ratio": min_formula_finite,
        "min_formula_active_ratio": min_formula_active,
        "blockers": blockers,
        "warnings": warnings,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_book": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_live_adapter_probe_only": decision.startswith("PASS"),
        "next_required": [
            "Build a source-lag and checksum audit for the forward patch before any proof claim.",
            "Keep this as adapter/materialization evidence only; it is not a live-trading authorization.",
            "Feed selected A7SHADOW-7 packet and overlap rejections into the next family-diversified search memory.",
        ],
    }
    write_json(runtime / "a7live0_manifest.json", manifest)

    lines = [
        "# CRYPTO A7LIVE0 Forward Adapter Probe",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7LIVE-0 validates that the A7SHADOW-7 review packet can be materialized from the forward-only recent patch field path. It does not run backtest, alpha proof, shadow, paper, or live trading.",
        "",
        "## Counts",
        "",
        f"- loaded_symbol_count: `{manifest['loaded_symbol_count']}` / `{manifest['symbol_count']}`",
        f"- timestamp_start: `{manifest['timestamp_start']}`",
        f"- timestamp_end: `{manifest['timestamp_end']}`",
        f"- timestamp_count: `{manifest['timestamp_count']}`",
        f"- candidate_count: `{manifest['candidate_count']}`",
        f"- eval_error_count: `{manifest['eval_error_count']}`",
        f"- min_field_finite_share: `{manifest['min_field_finite_share']}`",
        f"- min_formula_non_null_ratio: `{manifest['min_formula_non_null_ratio']}`",
        f"- min_formula_active_ratio: `{manifest['min_formula_active_ratio']}`",
        "",
        "## Field Health",
        "",
        md_table(health, 40),
        "",
        "## Formula Materialization",
        "",
        md_table(evals, 40),
        "",
        "## Interpretation",
        "",
        "This is a forward adapter/materialization smoke, not a trading validation. Passing it means the selected formulas can be computed on the recent patch path with past-only derived funding delta; it does not validate execution, slippage, or future live behavior.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", default=str(DEFAULT_RUNTIME))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--patch-root", default=str(DEFAULT_PATCH_ROOT))
    parser.add_argument("--packet", default=str(DEFAULT_PACKET))
    parser.add_argument("--symbol-cap", type=int, default=96)
    args = parser.parse_args()
    build(Path(args.runtime), Path(args.report), Path(args.patch_root), Path(args.packet), args.symbol_cap)


if __name__ == "__main__":
    main()
