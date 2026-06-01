from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore29e_independent_family_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE29E_INDEPENDENT_FAMILY_PREFLIGHT_20260602.md"
CORE29 = REPO / "runtime" / "a7ffcore29_independent_family_bounded_probe_contract" / "a7ffcore29_manifest.json"
CORE29_FAMILY = REPO / "runtime" / "a7ffcore29_independent_family_bounded_probe_contract" / "a7ffcore29_family_contract.csv"

TOP498 = Path("G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v2_20260527")
CORE12_AGG = Path(
    "G:/AlphaFactory_CryptoData/gold/features/binance_core12_all_features_metrics_market_structure_aggtrades_v1_20260524.parquet"
)


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
    return view.to_markdown(index=False)


def schema_names(path: Path) -> set[str]:
    if path.is_dir():
        return set(ds.dataset(str(path), format="parquet").schema.names)
    return set(pq.ParquetFile(str(path)).schema_arrow.names)


def build_blueprints() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    specs = [
        {
            "family_id": "F1a_aggtrades_flow_microstructure",
            "dataset": "core12_aggtrades_all_features",
            "fields": ["agg_signed_aggressor_notional", "agg_volume_imbalance", "agg_max_trade_notional", "agg_large_notional_ratio_100k_plus"],
            "partners": ["premium_index_bps", "funding_rate", "mark_index_basis_bps", "agg_price_range_bps"],
            "motifs": ["flow_reversal", "large_trade_shock", "flow_x_dislocation", "flow_x_low_turnover"],
        },
        {
            "family_id": "F1b_taker_flow_market_panel",
            "dataset": "top498_replay_v2",
            "fields": ["kline_taker_buy_quote_share", "taker_buy_quote_volume", "trade_quote_volume", "trade_volume"],
            "partners": ["mark_index_basis_bps", "premium_close_bps", "funding_rate", "trade_quote_volume"],
            "motifs": ["taker_flow_x_basis", "taker_flow_x_vol", "taker_flow_x_liquidity", "low_turnover_flow_state"],
        },
        {
            "family_id": "F2a_basis_funding_independent",
            "dataset": "top498_replay_v2",
            "fields": ["mark_index_basis_bps", "premium_close_bps", "funding_rate", "premium_close"],
            "partners": ["kline_taker_buy_quote_share", "trade_quote_volume", "taker_buy_quote_volume", "trade_volume"],
            "motifs": ["basis_delta_x_funding", "basis_x_flow", "funding_persistence_low_turnover", "H8_H24_dislocation"],
        },
    ]
    windows = [4, 8, 24, 72, 168]
    ops = ["Delta", "ZScore", "TSRank", "SpreadShortLong", "WinsorZ"]
    idx = 0
    for spec in specs:
        target = 160
        count = 0
        while count < target:
            field = spec["fields"][count % len(spec["fields"])]
            partner = spec["partners"][(count // len(spec["fields"])) % len(spec["partners"])]
            motif = spec["motifs"][(count // (len(spec["fields"]) * len(spec["partners"]))) % len(spec["motifs"])]
            w = windows[count % len(windows)]
            op = ops[(count // len(windows)) % len(ops)]
            if op == "SpreadShortLong":
                expr = f"Sub(ZScore(Mean({field},{w})),ZScore(Mean({partner},{min(336, w * 4)})))"
            elif op == "WinsorZ":
                expr = f"Clip(ZScore(Delta({field},{w})),-3,3)*Sign(Delta({partner},{w}))"
            else:
                expr = f"{op}({field},{w})*ZScore(Delta({partner},{w}))"
            rows.append(
                {
                    "candidate_id": f"a7ffcore29e_{idx:04d}",
                    "family_id": spec["family_id"],
                    "dataset": spec["dataset"],
                    "motif": motif,
                    "primary_field": field,
                    "partner_field": partner,
                    "window_h": w,
                    "operator": op,
                    "expression": expr,
                    "candidate_role": "preflight_blueprint_only",
                    "executes_numeric": False,
                }
            )
            idx += 1
            count += 1
    return pd.DataFrame(rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE29)
    if source.get("decision") != "PASS_A7FFCORE29_INDEPENDENT_FAMILY_BOUNDED_PROBE_CONTRACT_READY_FOR_CORE29E":
        raise SystemExit(f"CORE29 not ready for CORE29E: {source.get('decision')}")
    family_contract = pd.read_csv(CORE29_FAMILY)
    schemas = {
        "top498_replay_v2": schema_names(TOP498),
        "core12_aggtrades_all_features": schema_names(CORE12_AGG),
    }
    queue = build_blueprints()

    availability_rows = []
    for dataset, names in schemas.items():
        requested = sorted(set(queue.loc[queue["dataset"].eq(dataset), "primary_field"]).union(set(queue.loc[queue["dataset"].eq(dataset), "partner_field"])))
        for field in requested:
            availability_rows.append(
                {
                    "dataset": dataset,
                    "field": field,
                    "available": field in names,
                    "schema_field_count": len(names),
                }
            )
    availability = pd.DataFrame(availability_rows)
    queue["primary_field_available"] = queue.apply(lambda r: r["primary_field"] in schemas[r["dataset"]], axis=1)
    queue["partner_field_available"] = queue.apply(lambda r: r["partner_field"] in schemas[r["dataset"]], axis=1)
    queue["materialization_preflight_pass"] = queue["primary_field_available"] & queue["partner_field_available"]

    forbidden_tokens = [
        "open_interest_value_last,index_close",
        "RawOKXBinance",
        "SameBar",
        "future_return",
        "liquidation_",
        "depth_imbalance",
    ]
    forbidden_audit = pd.DataFrame(
        [
            {
                "pattern": token,
                "hit_count": int(queue["expression"].astype(str).str.contains(token, regex=False).sum()),
            }
            for token in forbidden_tokens
        ]
    )
    family_balance = (
        queue.groupby(["family_id", "dataset"], as_index=False)
        .agg(
            blueprint_count=("candidate_id", "count"),
            preflight_pass_count=("materialization_preflight_pass", "sum"),
            motif_count=("motif", "nunique"),
            operator_count=("operator", "nunique"),
        )
        .sort_values("family_id")
    )
    adapter_preflight = pd.DataFrame(
        [
            {
                "adapter": "aggtrades_enhanced_field_adapter",
                "dataset": "core12_aggtrades_all_features",
                "required_fields_available": bool(
                    availability.loc[availability["dataset"].eq("core12_aggtrades_all_features"), "available"].all()
                ),
                "status": "pass"
                if bool(availability.loc[availability["dataset"].eq("core12_aggtrades_all_features"), "available"].all())
                else "hold_missing_fields",
            },
            {
                "adapter": "existing_top498_panel_fields",
                "dataset": "top498_replay_v2",
                "required_fields_available": bool(availability.loc[availability["dataset"].eq("top498_replay_v2"), "available"].all()),
                "status": "pass"
                if bool(availability.loc[availability["dataset"].eq("top498_replay_v2"), "available"].all())
                else "hold_missing_fields",
            },
            {
                "adapter": "balanced_queue_policy",
                "dataset": "all",
                "required_fields_available": bool((family_balance["blueprint_count"] == 160).all()),
                "status": "pass" if bool((family_balance["blueprint_count"] == 160).all()) else "hold_unbalanced_queue",
            },
        ]
    )
    pass_count = int(queue["materialization_preflight_pass"].sum())
    missing_count = int((~queue["materialization_preflight_pass"]).sum())
    forbidden_hits = int(forbidden_audit["hit_count"].sum())
    decision = (
        "PASS_A7FFCORE29E_INDEPENDENT_FAMILY_PREFLIGHT_READY_FOR_CORE30_CONTRACT"
        if missing_count == 0 and forbidden_hits == 0 and bool(adapter_preflight["status"].eq("pass").all())
        else "HOLD_A7FFCORE29E_PREFLIGHT_BLOCKERS"
    )
    manifest = {
        "stage": "A7FF-CORE29E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE29",
        "source_decision": source.get("decision"),
        "decision": decision,
        "blueprint_count": int(queue.shape[0]),
        "preflight_pass_count": pass_count,
        "preflight_missing_count": missing_count,
        "family_count": int(queue["family_id"].nunique()),
        "forbidden_pattern_hit_count": forbidden_hits,
        "executes_generation": False,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core30_contract": decision.startswith("PASS_"),
        "authorizes_numeric_probe": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE30 independent family numeric probe contract"
        if decision.startswith("PASS_")
        else "CORE29E preflight blocker repair",
    }

    queue.to_csv(RUNTIME / "a7ffcore29e_blueprint_preflight_queue.csv", index=False)
    availability.to_csv(RUNTIME / "a7ffcore29e_schema_availability.csv", index=False)
    family_balance.to_csv(RUNTIME / "a7ffcore29e_family_balance.csv", index=False)
    forbidden_audit.to_csv(RUNTIME / "a7ffcore29e_forbidden_pattern_audit.csv", index=False)
    adapter_preflight.to_csv(RUNTIME / "a7ffcore29e_adapter_preflight.csv", index=False)
    family_contract.to_csv(RUNTIME / "a7ffcore29e_source_family_contract_snapshot.csv", index=False)
    write_json(RUNTIME / "a7ffcore29e_manifest.json", manifest)

    lines = [
        "# CRYPTO A7FF-CORE29E INDEPENDENT FAMILY PREFLIGHT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE29E builds a balanced blueprint preflight queue and validates field/schema availability. It does not execute numeric evaluation, replay, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Summary",
        "",
        f"- blueprint_count: `{manifest['blueprint_count']}`",
        f"- preflight_pass_count: `{pass_count}`",
        f"- preflight_missing_count: `{missing_count}`",
        f"- forbidden_pattern_hit_count: `{forbidden_hits}`",
        "",
        "## Adapter Preflight",
        "",
        md_table(adapter_preflight),
        "",
        "## Family Balance",
        "",
        md_table(family_balance),
        "",
        "## Schema Availability",
        "",
        md_table(availability, max_rows=120),
        "",
        "## Forbidden Pattern Audit",
        "",
        md_table(forbidden_audit),
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
