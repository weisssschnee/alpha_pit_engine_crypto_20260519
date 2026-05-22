from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
PANEL_PATH = DATA_ROOT / "gold" / "features" / "binance_core39_all_features_metrics_v3_market_structure_v1.parquet"
A7AE1_AUTH = ROOT / "runtime" / "a7ae1_field_selection_contract" / "a7ae1_authorization_matrix.json"
A7AE1_FIELDS = ROOT / "runtime" / "a7ae1_field_selection_contract" / "a7ae1_selected_field_contract.csv"

OUT_DIR = ROOT / "runtime" / "a7af0_core39_selected_field_replay_contract"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AF0_CORE39_SELECTED_FIELD_REPLAY_CONTRACT_20260522.md"

SPLITS = [
    ("train_2024", "2024-01-01 00:00:00+00:00", "2024-12-31 23:00:00+00:00", "selection_training_only"),
    ("validation_2025H1", "2025-01-01 00:00:00+00:00", "2025-06-30 23:00:00+00:00", "ranking_allowed_non_may"),
    ("recent_2025H2_2026Apr", "2025-07-01 00:00:00+00:00", "2026-04-30 23:00:00+00:00", "ranking_allowed_non_may"),
    ("may_2026_stress", "2026-05-01 00:00:00+00:00", "2026-05-21 23:00:00+00:00", "post_selection_stress_only"),
]

BASE_FIELDS = ["symbol", "timestamp", "ret_1", "ret_24"]
FIRST_SMOKE_EXTRA_FIELDS = [
    "open_interest_change_24h",
    "open_interest_zscore_168h",
    "open_interest_value_zscore_168h",
    "global_long_short_account_ratio_zscore_168h",
    "top_long_short_account_ratio_zscore_168h",
    "top_long_short_position_ratio_zscore_168h",
    "taker_buy_sell_volume_ratio_zscore_168h",
    "mark_index_basis_change_24h",
    "mark_index_basis_zscore_168h",
    "premium_index_change_24h",
    "premium_index_bps",
    "funding_rate_bps",
    "funding_rate_change_3obs",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def split_manifest(df: pd.DataFrame, symbols: list[str]) -> pd.DataFrame:
    out = []
    for split, start_text, end_text, usage in SPLITS:
        start = pd.Timestamp(start_text)
        end = pd.Timestamp(end_text)
        part = df[df["timestamp"].between(start, end, inclusive="both")]
        expected_hours = int((end - start) / pd.Timedelta(hours=1)) + 1
        expected_rows = expected_hours * len(symbols)
        out.append(
            {
                "split": split,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "usage": usage,
                "rows": int(len(part)),
                "symbols": int(part["symbol"].nunique()),
                "expected_rows_if_full": int(expected_rows),
                "row_coverage": len(part) / expected_rows if expected_rows else None,
                "may_allowed_for_ranking": False if "may" in split else True,
                "feature_time_rule": "1h features available at timestamp + 1h",
                "execution_rule": "execution_time >= next 1h bar; lag stress required",
            }
        )
    return pd.DataFrame(out)


def field_availability(df: pd.DataFrame, fields: list[str]) -> pd.DataFrame:
    rows = []
    for field in fields:
        if field not in df.columns:
            rows.append({"field_name": field, "present": False, "non_null_rate": 0.0, "min_symbol_rate": 0.0, "median_symbol_rate": 0.0})
            continue
        rates = df.groupby("symbol", observed=True)[field].apply(lambda s: s.notna().mean())
        rows.append(
            {
                "field_name": field,
                "present": True,
                "non_null_rate": float(df[field].notna().mean()),
                "min_symbol_rate": float(rates.min()),
                "median_symbol_rate": float(rates.median()),
                "max_symbol_rate": float(rates.max()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    auth_prev = json.loads(A7AE1_AUTH.read_text(encoding="utf-8"))
    if not auth_prev.get("authorizes_a7af0_core39_selected_field_contract"):
        raise RuntimeError("A7AE1 does not authorize A7AF0")

    schema = pq.read_schema(PANEL_PATH)
    schema_names = set(schema.names)
    selected_contract = pd.read_csv(A7AE1_FIELDS)
    selected_core39 = selected_contract[selected_contract["scope"].eq("core39")].copy()
    selected_core39 = selected_core39[selected_core39["status"].isin(["allowed", "caution", "benchmark_only"])].copy()

    fields = sorted(set(BASE_FIELDS + selected_core39["field_name"].tolist() + FIRST_SMOKE_EXTRA_FIELDS))
    present_fields = [f for f in fields if f in schema_names]
    df = pd.read_parquet(PANEL_PATH, columns=present_fields, engine="pyarrow")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    symbols = sorted(df["symbol"].dropna().unique().tolist())
    duplicate_keys = int(df.duplicated(["symbol", "timestamp"]).sum())

    splits = split_manifest(df, symbols)
    availability = field_availability(df, fields)
    smoke_fields = pd.DataFrame({"field_name": FIRST_SMOKE_EXTRA_FIELDS})
    smoke_fields = smoke_fields.merge(availability, on="field_name", how="left")
    selected_contract = selected_contract.merge(availability[["field_name", "present", "non_null_rate", "min_symbol_rate", "median_symbol_rate"]], on="field_name", how="left")

    blockers: list[str] = []
    warnings: list[str] = []
    if duplicate_keys:
        blockers.append("duplicate_symbol_timestamp")
    if int(splits[splits["split"].ne("may_2026_stress")]["symbols"].min()) < 39:
        blockers.append("non_may_split_symbol_count_below_39")
    if not bool(availability[availability["field_name"].isin(BASE_FIELDS)]["present"].all()):
        blockers.append("base_fields_missing")
    missing_smoke = smoke_fields[~smoke_fields["present"].fillna(False)]
    if not missing_smoke.empty:
        blockers.append("first_smoke_required_fields_missing")
    low_smoke = smoke_fields[smoke_fields["min_symbol_rate"].fillna(0.0) < 0.70]
    if not low_smoke.empty:
        warnings.append("some_first_smoke_fields_have_low_min_symbol_coverage")
    warnings.append("ret_1_forward_proxy_replay_not_execution_grade_open_to_open")
    warnings.append("may_2026_is_stress_only_not_ranking_or_selection")

    decision = "PASS_A7AF0_CORE39_SELECTED_FIELD_REPLAY_CONTRACT_READY" if not blockers else "HOLD_A7AF0_CORE39_SELECTED_FIELD_REPLAY_CONTRACT_BLOCKED"
    auth = {
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "authorizes_a7af1_small_controlled_smoke": decision.startswith("PASS_"),
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_policy": "May 2026 stress-only; not ranking, generation, threshold, weight selection, or authorization",
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "panel": str(PANEL_PATH),
        "rows": int(len(df)),
        "columns_read": int(len(present_fields)),
        "symbols": int(len(symbols)),
        "timestamp_min": str(df["timestamp"].min()),
        "timestamp_max": str(df["timestamp"].max()),
        "duplicate_keys": duplicate_keys,
        "executes_replay": False,
        "executes_search": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }

    splits.to_csv(OUT_DIR / "a7af0_split_manifest.csv", index=False)
    availability.to_csv(OUT_DIR / "a7af0_selected_field_availability.csv", index=False)
    selected_contract.to_csv(OUT_DIR / "a7af0_selected_field_contract_with_availability.csv", index=False)
    smoke_fields.to_csv(OUT_DIR / "a7af0_first_smoke_field_list.csv", index=False)
    write_json(OUT_DIR / "a7af0_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7af0_manifest.json", manifest)

    report = f"""# CRYPTO A7AF-0 Core39 Selected-Field Replay Contract

Generated: {now}

## Decision

```text
{decision}
```

This stage reads the core39 selected-field data and prepares a small controlled replay smoke. It does not run replay and does not run search.

## Authorization

```json
{json.dumps(auth, indent=2, sort_keys=True)}
```

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Split Manifest

{md_table(splits)}

## First Smoke Field List

{md_table(smoke_fields)}

## Selected Field Contract With Availability

{md_table(selected_contract)}

## Boundary

- A7AF-1 may run only a small controlled replay smoke.
- `ret_1` forward proxy is acceptable for method smoke but not execution-grade proof.
- May 2026 is stress-only and cannot affect ranking or selection.
- Funding fields remain benchmark/control only.
- No formula search, large search, alpha proof, shadow, paper, or live is authorized.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
