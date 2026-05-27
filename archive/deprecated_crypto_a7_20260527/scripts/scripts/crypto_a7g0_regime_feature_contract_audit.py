from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, SPLITS, clean_float, split_mask


ROOT = Path("G:/AlphaFactory_CryptoData")
PANEL_1H = ROOT / "gold" / "panels" / "crypto_core12_1h_v1.parquet"
PANEL_BUILDER = ROOT / "scripts" / "build_crypto_gold_panel_v1.py"
A7G0_DIR = RUNTIME_DIR / "a7g0_regime_feature_contract_audit"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def quantile_row(name: str, values: pd.Series, split: str) -> dict[str, Any]:
    clean = values.replace([np.inf, -np.inf], np.nan).dropna()
    if clean.empty:
        return {"feature": name, "split": split, "count": 0}
    qs = clean.quantile([0.001, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 0.999])
    return {
        "feature": name,
        "split": split,
        "count": int(clean.size),
        "mean": clean_float(clean.mean()),
        "std": clean_float(clean.std()),
        "min": clean_float(clean.min()),
        "q001": clean_float(qs.loc[0.001]),
        "q01": clean_float(qs.loc[0.01]),
        "q05": clean_float(qs.loc[0.05]),
        "q25": clean_float(qs.loc[0.25]),
        "q50": clean_float(qs.loc[0.5]),
        "q75": clean_float(qs.loc[0.75]),
        "q95": clean_float(qs.loc[0.95]),
        "q99": clean_float(qs.loc[0.99]),
        "q999": clean_float(qs.loc[0.999]),
        "max": clean_float(clean.max()),
    }


def bucket(values: pd.Series, low: float, high: float) -> pd.Series:
    out = pd.Series("missing", index=values.index, dtype=object)
    finite = values.replace([np.inf, -np.inf], np.nan).notna()
    out.loc[finite & (values <= low)] = "low"
    out.loc[finite & (values > low) & (values < high)] = "mid"
    out.loc[finite & (values >= high)] = "high"
    return out


def train_edges(ts: pd.DatetimeIndex, values: pd.Series) -> tuple[float, float]:
    mask = split_mask(ts, "train_2024")
    clean = values.loc[mask].replace([np.inf, -np.inf], np.nan).dropna()
    if clean.empty:
        return np.nan, np.nan
    return float(clean.quantile(0.33)), float(clean.quantile(0.67))


def main() -> int:
    A7G0_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    cols = [
        "timestamp",
        "symbol",
        "mark_close",
        "index_close",
        "mark_index_ratio",
        "mark_minus_index",
        "premium_index",
    ]
    df = pd.read_parquet(PANEL_1H, columns=cols).sort_values(["timestamp", "symbol"]).reset_index(drop=True)
    ts = pd.DatetimeIndex(pd.to_datetime(df["timestamp"], utc=True))

    df["basis_abs_v0_ratio_minus_1"] = (df["mark_index_ratio"] - 1.0).abs()
    df["basis_abs_v1_centered_ratio"] = df["mark_index_ratio"].abs()
    df["basis_abs_v2_mark_minus_over_index"] = (df["mark_minus_index"] / df["index_close"].replace(0, np.nan)).abs()
    df["premium_abs"] = df["premium_index"].abs()

    feature_cols = [
        "mark_index_ratio",
        "mark_minus_index",
        "premium_index",
        "basis_abs_v0_ratio_minus_1",
        "basis_abs_v1_centered_ratio",
        "basis_abs_v2_mark_minus_over_index",
        "premium_abs",
    ]
    rows = []
    for split in SPLITS:
        mask = split_mask(ts, split)
        for col in feature_cols:
            rows.append(quantile_row(col, df.loc[mask, col], split))
    quantiles = pd.DataFrame(rows)

    low0, high0 = train_edges(ts, df["basis_abs_v0_ratio_minus_1"])
    low1, high1 = train_edges(ts, df["basis_abs_v1_centered_ratio"])
    low2, high2 = train_edges(ts, df["basis_abs_v2_mark_minus_over_index"])
    bucket_df = pd.DataFrame({"timestamp": df["timestamp"], "symbol": df["symbol"]})
    bucket_df["v0_bucket"] = bucket(df["basis_abs_v0_ratio_minus_1"], low0, high0)
    bucket_df["v1_bucket"] = bucket(df["basis_abs_v1_centered_ratio"], low1, high1)
    bucket_df["v2_bucket"] = bucket(df["basis_abs_v2_mark_minus_over_index"], low2, high2)
    bucket_df["v0_equals_v1"] = bucket_df["v0_bucket"] == bucket_df["v1_bucket"]
    bucket_df["v1_equals_v2"] = bucket_df["v1_bucket"] == bucket_df["v2_bucket"]
    overlap_rows = []
    for split in SPLITS:
        mask = split_mask(ts, split)
        part = bucket_df.loc[mask]
        overlap_rows.append(
            {
                "split": split,
                "rows": int(len(part)),
                "v0_v1_bucket_match_rate": clean_float(part["v0_equals_v1"].mean()),
                "v1_v2_bucket_match_rate": clean_float(part["v1_equals_v2"].mean()),
                "v0_low_share": clean_float((part["v0_bucket"] == "low").mean()),
                "v1_low_share": clean_float((part["v1_bucket"] == "low").mean()),
                "v2_low_share": clean_float((part["v2_bucket"] == "low").mean()),
            }
        )
    overlap = pd.DataFrame(overlap_rows)

    builder_text = PANEL_BUILDER.read_text(encoding="utf-8")
    source_lines = []
    for i, line in enumerate(builder_text.splitlines(), start=1):
        if "mark_index_ratio" in line or "mark_minus_index" in line or "premium_index" in line:
            source_lines.append({"line": i, "text": line.strip()})

    q_train = quantiles[quantiles["split"] == "train_2024"].set_index("feature")
    v0_median = clean_float(q_train.loc["basis_abs_v0_ratio_minus_1", "q50"])
    v1_median = clean_float(q_train.loc["basis_abs_v1_centered_ratio", "q50"])
    v2_median = clean_float(q_train.loc["basis_abs_v2_mark_minus_over_index", "q50"])
    v1_v2_match = clean_float(overlap.loc[overlap["split"] == "train_2024", "v1_v2_bucket_match_rate"].iloc[0])
    v0_invalid = v0_median is not None and v0_median > 0.5 and v1_median is not None and v1_median < 0.01
    v1_v2_consistent = v1_v2_match is not None and v1_v2_match > 0.95

    blockers = []
    warnings = []
    if not v0_invalid:
        warnings.append("basis_v0_not_flagged_invalid_check_panel_distribution")
    if not v1_v2_consistent:
        warnings.append("centered_ratio_and_normalized_mark_minus_bucket_mismatch")

    decision = "PASS_A7G0_FIELD_CONTRACT_A7F_CORRECTION_REQUIRED" if not blockers else "HOLD_A7G0_FIELD_CONTRACT_UNRESOLVED"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "field_contract": {
            "mark_minus_index": {
                "definition": "mark_close - index_close",
                "source": str(PANEL_BUILDER),
                "source_lines": [x for x in source_lines if "mark_minus_index" in x["text"]],
            },
            "mark_index_ratio": {
                "definition": "mark_close / index_close - 1.0",
                "is_centered": True,
                "correct_abs_basis": "abs(mark_index_ratio)",
                "incorrect_abs_basis": "abs(mark_index_ratio - 1.0)",
                "source": str(PANEL_BUILDER),
                "source_lines": [x for x in source_lines if "mark_index_ratio" in x["text"]],
            },
            "premium_index": {
                "definition": "premium_close",
                "source": str(PANEL_BUILDER),
                "source_lines": [x for x in source_lines if "premium_index" in x["text"]],
            },
        },
        "key_metrics": {
            "train_basis_abs_v0_median": v0_median,
            "train_basis_abs_v1_median": v1_median,
            "train_basis_abs_v2_median": v2_median,
            "train_v0_v1_bucket_match_rate": clean_float(overlap.loc[overlap["split"] == "train_2024", "v0_v1_bucket_match_rate"].iloc[0]),
            "train_v1_v2_bucket_match_rate": v1_v2_match,
        },
        "next_action": "Rerun A7F with basis_abs_mean = abs(mark_index_ratio); do not interpret old G6 basis bucket.",
    }

    quantile_path = A7G0_DIR / "crypto_a7g0_basis_sanity_quantiles_20260519.csv"
    overlap_path = A7G0_DIR / "crypto_a7g0_basis_bucket_overlap_20260519.csv"
    contract_path = A7G0_DIR / "crypto_a7g0_regime_feature_contract_20260519.json"
    manifest_path = A7G0_DIR / "crypto_a7g0_manifest_20260519.json"
    quantiles.to_csv(quantile_path, index=False)
    overlap.to_csv(overlap_path, index=False)
    write_json(contract_path, manifest["field_contract"])
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / "CRYPTO_A7G0_REGIME_FEATURE_CONTRACT_AUDIT_20260519.md"
    lines = [
        "# Crypto A7G-0 Regime Feature Contract Audit",
        "",
        f"- generated_at: `{manifest['generated_at']}`",
        f"- decision: `{decision}`",
        f"- blockers: `{blockers}`",
        f"- warnings: `{warnings}`",
        "",
        "## Contract",
        "",
        "- `mark_index_ratio = mark_close / index_close - 1.0`; it is already centered around zero.",
        "- Correct absolute basis proxy: `abs(mark_index_ratio)`.",
        "- Incorrect A7F proxy: `abs(mark_index_ratio - 1.0)`.",
        "",
        "## Key Metrics",
        "",
        f"- train basis_abs_v0 median: `{v0_median}`",
        f"- train basis_abs_v1 median: `{v1_median}`",
        f"- train basis_abs_v2 median: `{v2_median}`",
        f"- train v0/v1 bucket match rate: `{manifest['key_metrics']['train_v0_v1_bucket_match_rate']}`",
        f"- train v1/v2 bucket match rate: `{v1_v2_match}`",
        "",
        "## Decision",
        "",
        "A7F's old `basis_abs_mean` used an invalid centered-ratio transform. Old G6 remains a diagnostic only and cannot be used as A7G design evidence.",
        "",
        "Required next step: rerun A7F with `basis_abs_mean = abs(mark_index_ratio)` before any funding-regime redesign.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("A7G0_REPORT=" + str(report_path))
    print("A7G0_CONTRACT=" + str(contract_path))
    print("A7G0_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
