from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7al2l_fast_derived_replay_preflight import SPLIT_END, SPLIT_ORDER, split_for_timestamps  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import BASE_DIR, load_base  # noqa: E402
from scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair import strict_symbols  # noqa: E402
from scripts.crypto_a7ff25r6_dense_funding_state_audit import dense_ffill_and_age, shift_matrix  # noqa: E402
from scripts.crypto_a7reward1_portfolio_reward_model import selected_column_indices  # noqa: E402


DATA_ROOT = Path(os.environ.get("ALPHAFACTORY_CRYPTO_DATA_ROOT", r"G:\AlphaFactory_CryptoData"))
DEFAULT_RECENT_PATCH = DATA_ROOT / "gold" / "features" / "binance_universe498_recent_patch_1h_v1_20260612"
DEFAULT_RUNTIME = REPO / "runtime" / "a7shadow5_stress_funding_coverage_audit_20260704"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SHADOW5_STRESS_FUNDING_COVERAGE_AUDIT_20260704.md"
FIELD_ALIASES = {
    "premium_close_bps": ["premium_close_bps", "premium_bps"],
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


def matrix_coverage(name: str, values: np.ndarray, timestamps: pd.DatetimeIndex, split: np.ndarray) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    finite = np.isfinite(values)
    nonzero = finite & (np.abs(values) > 1e-12)
    for split_name in SPLIT_ORDER:
        mask = split == split_name
        sub = values[:, mask]
        sub_finite = finite[:, mask]
        sub_nonzero = nonzero[:, mask]
        ts = timestamps[mask]
        rows.append(
            {
                "source": "base_panel",
                "field": name,
                "split": split_name,
                "timestamp_start": ts.min().isoformat() if len(ts) else "",
                "timestamp_end": ts.max().isoformat() if len(ts) else "",
                "hour_count": int(len(ts)),
                "cell_count": int(sub.size),
                "finite_cell_count": int(sub_finite.sum()),
                "finite_share": float(sub_finite.mean()) if sub_finite.size else np.nan,
                "nonzero_share": float(sub_nonzero.mean()) if sub_nonzero.size else np.nan,
                "symbol_with_any_finite": int(np.isfinite(sub).any(axis=1).sum()) if sub.size else 0,
            }
        )
    return rows


def read_symbol_panel(root: Path, symbol: str, fields: list[str]) -> pd.DataFrame:
    part_dir = root / f"symbol={symbol}"
    paths = sorted(part_dir.glob("*.parquet"))
    if not paths:
        return pd.DataFrame()
    # These files are small per symbol. Read all parquet parts so the audit is
    # not coupled to a single writer's file naming convention.
    frame = pd.concat((pd.read_parquet(path, engine="pyarrow") for path in paths), ignore_index=True)
    cols = ["timestamp"] + [field for field in fields if field in frame.columns]
    frame = frame[cols].copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame["symbol"] = symbol
    return frame


def patch_coverage(root: Path, symbols: list[str], fields: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if not root.exists():
        return pd.DataFrame(
            [
                {
                    "source": "recent_patch",
                    "field": field,
                    "status": "MISSING_ROOT",
                    "root": str(root),
                }
                for field in fields
            ]
        )
    for field in fields:
        aliases = FIELD_ALIASES.get(field, [field])
        all_values: list[pd.Series] = []
        timestamps_seen: list[pd.Series] = []
        symbols_seen = 0
        observed_field = ""
        for symbol in symbols:
            frame = read_symbol_panel(root, symbol, aliases)
            if frame.empty:
                continue
            symbol_field = next((alias for alias in aliases if alias in frame.columns), "")
            if not symbol_field:
                continue
            observed_field = observed_field or symbol_field
            symbols_seen += 1
            all_values.append(pd.to_numeric(frame[symbol_field], errors="coerce"))
            timestamps_seen.append(frame["timestamp"])
        if not all_values:
            rows.append(
                {
                    "source": "recent_patch",
                    "field": field,
                    "observed_field": "",
                    "status": "MISSING_FIELD",
                    "root": str(root),
                    "symbols_with_field": 0,
                    "timestamp_start": "",
                    "timestamp_end": "",
                    "cell_count": 0,
                    "finite_cell_count": 0,
                    "finite_share": np.nan,
                    "overlaps_may_stress_hours": 0,
                }
            )
            continue
        values = pd.concat(all_values, ignore_index=True)
        ts = pd.concat(timestamps_seen, ignore_index=True)
        stress_mask = (ts > SPLIT_END["recent_oos_2026JanApr"]) & (ts <= SPLIT_END["known_may2026_stress"])
        rows.append(
            {
                "source": "recent_patch",
                "field": field,
                "observed_field": observed_field,
                "status": "OK",
                "root": str(root),
                "symbols_with_field": symbols_seen,
                "timestamp_start": ts.min().isoformat(),
                "timestamp_end": ts.max().isoformat(),
                "cell_count": int(values.shape[0]),
                "finite_cell_count": int(np.isfinite(values.to_numpy(dtype=float)).sum()),
                "finite_share": float(np.isfinite(values.to_numpy(dtype=float)).mean()),
                "overlaps_may_stress_hours": int(ts[stress_mask].drop_duplicates().shape[0]),
                "stress_overlap_start": ts[stress_mask].min().isoformat() if stress_mask.any() else "",
                "stress_overlap_end": ts[stress_mask].max().isoformat() if stress_mask.any() else "",
            }
        )
    return pd.DataFrame(rows)


def missing_hour_table(timestamps: pd.DatetimeIndex, split: np.ndarray, values: np.ndarray, field: str) -> pd.DataFrame:
    stress = split == "known_may2026_stress"
    ts = timestamps[stress]
    mat = values[:, stress]
    finite_by_hour = np.isfinite(mat).mean(axis=0) if mat.size else np.array([])
    rows = []
    for timestamp, share in zip(ts, finite_by_hour):
        if not np.isfinite(share) or share < 0.95:
            rows.append({"field": field, "timestamp": timestamp.isoformat(), "finite_share": float(share)})
    return pd.DataFrame(rows)


def build(runtime: Path, report: Path, recent_patch: Path, hours_per_split: int, train_hours_per_split: int, symbol_cap: int) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    symbols = strict_symbols()[:symbol_cap]
    loaded_symbols, timestamps, numeric = load_base(symbols, {"funding_rate", "mark_index_basis_bps", "premium_close_bps", "open_interest_mean"})
    idx = selected_column_indices(timestamps, hours_per_split, train_hours_per_split)
    timestamps = pd.DatetimeIndex(timestamps[idx])
    numeric = {key: value[:, idx] for key, value in numeric.items()}
    split = split_for_timestamps(timestamps)

    raw = numeric["funding_rate"]
    dense8, age8 = dense_ffill_and_age(raw, 8)
    dense24, age24 = dense_ffill_and_age(raw, 24)
    dense72, age72 = dense_ffill_and_age(raw, 72)
    delta8 = dense8 - shift_matrix(dense8, 24)
    delta24 = dense24 - shift_matrix(dense24, 24)
    delta72 = dense72 - shift_matrix(dense72, 24)

    coverage_rows: list[dict[str, Any]] = []
    for name, values in [
        ("raw_funding_rate", raw),
        ("funding_rate_state_last_ffill_8h", dense8),
        ("funding_rate_delta_state_24h_ffill_8h", delta8),
        ("funding_rate_state_last_ffill_24h", dense24),
        ("funding_rate_delta_state_24h_ffill_24h", delta24),
        ("funding_rate_state_last_ffill_72h", dense72),
        ("funding_rate_delta_state_24h_ffill_72h", delta72),
        ("premium_close_bps", numeric["premium_close_bps"]),
        ("open_interest_mean", numeric["open_interest_mean"]),
    ]:
        coverage_rows.extend(matrix_coverage(name, values, timestamps, split))
    coverage = pd.DataFrame(coverage_rows)
    coverage.to_csv(runtime / "a7shadow5_base_dense_funding_coverage_by_split.csv", index=False)

    patch = patch_coverage(recent_patch, loaded_symbols, ["funding_rate", "funding_mark_price", "open_interest_mean", "premium_close_bps"])
    patch.to_csv(runtime / "a7shadow5_recent_patch_coverage.csv", index=False)

    missing = missing_hour_table(timestamps, split, delta8, "funding_rate_delta_state_24h_ffill_8h")
    missing.to_csv(runtime / "a7shadow5_stress_missing_hours_delta_ffill8.csv", index=False)

    split_hours = []
    for split_name in SPLIT_ORDER:
        mask = split == split_name
        ts = timestamps[mask]
        split_hours.append(
            {
                "split": split_name,
                "timestamp_start": ts.min().isoformat() if len(ts) else "",
                "timestamp_end": ts.max().isoformat() if len(ts) else "",
                "hour_count": int(len(ts)),
            }
        )
    split_hours_df = pd.DataFrame(split_hours)
    split_hours_df.to_csv(runtime / "a7shadow5_eval_split_hours.csv", index=False)

    stress_cov = coverage[(coverage["split"].eq("known_may2026_stress")) & (coverage["field"].str.contains("funding_rate_delta"))].copy()
    best_stress_share = float(stress_cov["finite_share"].max()) if not stress_cov.empty else np.nan
    base_delta8_stress_share = float(
        coverage[
            coverage["split"].eq("known_may2026_stress")
            & coverage["field"].eq("funding_rate_delta_state_24h_ffill_8h")
        ]["finite_share"].iloc[0]
    )
    premium_stress_share = float(
        coverage[
            coverage["split"].eq("known_may2026_stress")
            & coverage["field"].eq("premium_close_bps")
        ]["finite_share"].iloc[0]
    )
    oi_stress_share = float(
        coverage[
            coverage["split"].eq("known_may2026_stress")
            & coverage["field"].eq("open_interest_mean")
        ]["finite_share"].iloc[0]
    )
    patch_stress_hours = int(patch["overlaps_may_stress_hours"].max()) if "overlaps_may_stress_hours" in patch.columns and not patch.empty else 0
    stress_hours = int(split_hours_df.loc[split_hours_df["split"].eq("known_may2026_stress"), "hour_count"].iloc[0])
    missing_stress_hours = max(0, stress_hours - patch_stress_hours)

    blockers: list[str] = []
    if base_delta8_stress_share < 0.95:
        blockers.append("base_panel_funding_delta_stress_coverage_below_95pct")
    if base_delta8_stress_share < 0.95 and patch_stress_hours < stress_hours:
        blockers.append("recent_patch_does_not_cover_full_may_stress_window")

    decision = "HOLD_A7SHADOW5_STRESS_FUNDING_COVERAGE_GAP_CONFIRMED" if blockers else "PASS_A7SHADOW5_STRESS_FUNDING_COVERAGE_OK"
    required_repair = (
        [
            "Backfill Binance funding-rate data for 2026-05-01 00:00 through 2026-05-26 00:00 UTC for the strict universe, plus at least 24h lookback before May 1 for funding_delta.",
            "Merge the repair into the evaluator base panel or set A7AL_BASE_PANEL_ROOT to a merged panel before rerunning A7SHADOW-4.",
            "Base OI and premium coverage are not the May-stress blocker in this audit, but any rebuilt merged panel should still re-check OI/premium/mark-index source trace.",
            "If full funding backfill is unavailable, exclude funding_delta candidates from May-stress claims and rerun A7SHADOW-4 on OI/premium candidates only.",
        ]
        if blockers
        else [
            "No additional May-stress funding coverage repair is required for this evaluated base panel.",
            "Proceed to A7SHADOW-4 with A7AL_BASE_PANEL_ROOT set to the repaired panel.",
            "Keep source-trace/checksum audit as a final-proof prerequisite; this stage only validates evaluator coverage.",
        ]
    )
    manifest = {
        "stage": "A7SHADOW-5",
        "generated_at": now_utc(),
        "decision": decision,
        "symbol_count": len(loaded_symbols),
        "base_panel_root": str(BASE_DIR),
        "recent_patch_root": str(recent_patch),
        "hours_per_split": hours_per_split,
        "train_hours_per_split": train_hours_per_split,
        "stress_hours": stress_hours,
        "base_delta_ffill8_stress_finite_share": base_delta8_stress_share,
        "best_delta_stress_finite_share_across_ffill_limits": best_stress_share,
        "base_premium_stress_finite_share": premium_stress_share,
        "base_open_interest_stress_finite_share": oi_stress_share,
        "recent_patch_stress_overlap_hours": patch_stress_hours,
        "estimated_stress_hours_not_covered_by_recent_patch": missing_stress_hours,
        "blockers": blockers,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_shadow_book": False,
        "authorizes_a7shadow4_rerun": not blockers,
        "required_repair": required_repair,
    }
    write_json(runtime / "a7shadow5_manifest.json", manifest)

    lines = [
        "# CRYPTO A7SHADOW5 Stress Funding Coverage Audit",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This stage diagnoses why A7SHADOW-4 held on May-stress field coverage. It does not run search or promote any candidate.",
        "",
        "## Key Findings",
        "",
        f"- base_delta_ffill8_stress_finite_share: `{base_delta8_stress_share}`",
        f"- best_delta_stress_finite_share_across_ffill_limits: `{best_stress_share}`",
        f"- base_premium_stress_finite_share: `{premium_stress_share}`",
        f"- base_open_interest_stress_finite_share: `{oi_stress_share}`",
        f"- stress_hours: `{stress_hours}`",
        f"- recent_patch_stress_overlap_hours: `{patch_stress_hours}`",
        f"- estimated_stress_hours_not_covered_by_recent_patch: `{missing_stress_hours}`",
        "",
        "## Split Hours",
        "",
        md_table(split_hours_df, 20),
        "",
        "## Base Dense Funding Coverage",
        "",
        md_table(coverage, 80),
        "",
        "## Recent Patch Coverage",
        "",
        md_table(patch, 40),
        "",
        "## Required Repair / Next Step",
        "",
        *[f"- {item}" for item in required_repair],
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
    parser.add_argument("--recent-patch", default=str(DEFAULT_RECENT_PATCH))
    parser.add_argument("--hours-per-split", type=int, default=720)
    parser.add_argument("--train-hours-per-split", type=int, default=0)
    parser.add_argument("--symbol-cap", type=int, default=96)
    args = parser.parse_args()
    build(Path(args.runtime), Path(args.report), Path(args.recent_patch), args.hours_per_split, args.train_hours_per_split, args.symbol_cap)


if __name__ == "__main__":
    main()
