from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

BASE_PROBE_JSON = DATA_ROOT / "reports" / "crypto_universe_expansion_probe_20260522_candidates.json"
BASE_PROBE_CSV = DATA_ROOT / "raw" / "source_probes" / "universe_expansion_20260522_candidates" / "universe_expansion_probe.csv"

LIQUID80_JSON = DATA_ROOT / "reports" / "crypto_universe_expansion_probe_20260522_liquid80_candidates.json"
LIQUID80_CSV = DATA_ROOT / "raw" / "source_probes" / "universe_expansion_20260522_liquid80_candidates" / "universe_expansion_probe.csv"

OUT_DIR = ROOT / "runtime" / "a7ac0_universe_expansion_handoff_audit"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AC0_UNIVERSE_EXPANSION_HANDOFF_AUDIT_20260522.md"

CORE12 = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "LINKUSDT",
    "AVAXUSDT",
    "LTCUSDT",
    "BCHUSDT",
    "SUIUSDT",
]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_probe(name: str, json_path: Path, csv_path: Path) -> tuple[dict[str, Any], pd.DataFrame]:
    meta = read_json(json_path)
    if csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        df = pd.DataFrame()
    if not df.empty:
        df.insert(0, "probe_name", name)
    return meta, df


def is_ok(value: Any) -> bool:
    return str(value).lower() == "ok"


def table(df: pd.DataFrame, max_rows: int = 100) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def summarize_probe(name: str, meta: dict[str, Any], df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            [
                {
                    "probe_name": name,
                    "exists": False,
                    "candidate_count": int(meta.get("candidate_count", 0) or 0),
                    "csv_rows": 0,
                    "core48_candidate": 0,
                    "midcap_candidate": 0,
                    "watchlist_or_new_listing": 0,
                    "reject_or_manual_review": 0,
                    "recommended_additions": len(meta.get("recommended_additions_top36", [])),
                    "decision": "HOLD_MISSING_PROBE_CSV",
                }
            ]
        )
    tier_counts = df["tier"].value_counts().to_dict() if "tier" in df.columns else {}
    return pd.DataFrame(
        [
            {
                "probe_name": name,
                "exists": True,
                "candidate_count": int(meta.get("candidate_count", len(df)) or len(df)),
                "csv_rows": int(len(df)),
                "core48_candidate": int(tier_counts.get("core48_candidate", 0)),
                "midcap_candidate": int(tier_counts.get("midcap_candidate", 0)),
                "watchlist_or_new_listing": int(tier_counts.get("watchlist_or_new_listing", 0)),
                "reject_or_manual_review": int(tier_counts.get("reject_or_manual_review", 0)),
                "recommended_additions": len(meta.get("recommended_additions_top36", [])),
                "decision": "PASS_PROBE_READABLE",
            }
        ]
    )


def tier_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    rows = []
    for tier, g in df.groupby("tier", dropna=False):
        rows.append(
            {
                "tier": tier,
                "symbols": int(g["symbol"].nunique()),
                "mean_score": round(float(pd.to_numeric(g["score"], errors="coerce").mean()), 4),
                "metrics_2024_ok": int(g["metrics_2024_01"].map(is_ok).sum()) if "metrics_2024_01" in g else 0,
                "metrics_2025_ok": int(g["metrics_2025_01"].map(is_ok).sum()) if "metrics_2025_01" in g else 0,
                "metrics_2026_ok": int(g["metrics_2026_01"].map(is_ok).sum()) if "metrics_2026_01" in g else 0,
                "binance_klines_ok": int(g["binance_klines"].map(is_ok).sum()) if "binance_klines" in g else 0,
                "binance_premium_ok": int(g["binance_premium"].map(is_ok).sum()) if "binance_premium" in g else 0,
                "okx_oi_ok": int(g["okx_oi"].map(is_ok).sum()) if "okx_oi" in g else 0,
                "okx_orderbook_ok": int(g["okx_orderbook"].map(is_ok).sum()) if "okx_orderbook" in g else 0,
                "bybit_ticker_ok": int(g["bybit_ticker"].map(is_ok).sum()) if "bybit_ticker" in g else 0,
                "bybit_orderbook_ok": int(g["bybit_orderbook"].map(is_ok).sum()) if "bybit_orderbook" in g else 0,
            }
        )
    return pd.DataFrame(rows).sort_values("tier")


def source_coverage_matrix(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    rows = []
    checks = [
        "metrics_2024_01",
        "metrics_2025_01",
        "metrics_2026_01",
        "binance_klines",
        "binance_premium",
        "okx_oi",
        "okx_orderbook",
        "bybit_ticker",
        "bybit_orderbook",
    ]
    for _, r in df.iterrows():
        row = {
            "symbol": r.get("symbol", ""),
            "tier": r.get("tier", ""),
            "score": int(pd.to_numeric(r.get("score", 0), errors="coerce") or 0),
        }
        ready_count = 0
        hold_count = 0
        for c in checks:
            value = r.get(c, "")
            row[c] = value
            if is_ok(value):
                ready_count += 1
            else:
                hold_count += 1
        row["ready_source_checks"] = ready_count
        row["non_ok_source_checks"] = hold_count
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["tier", "score", "symbol"], ascending=[True, False, True])


def recommended_universe(meta: dict[str, Any], df: pd.DataFrame) -> pd.DataFrame:
    symbols = list(meta.get("recommended_universe_if_added_to_core12", []))
    if not symbols:
        symbols = CORE12 + list(meta.get("recommended_additions_top36", []))
    registry = []
    tiers = df.set_index("symbol")["tier"].to_dict() if not df.empty and "symbol" in df else {}
    scores = df.set_index("symbol")["score"].to_dict() if not df.empty and "symbol" in df else {}
    for i, symbol in enumerate(symbols, start=1):
        tier = "core12_existing" if symbol in CORE12 else tiers.get(symbol, "<missing>")
        registry.append(
            {
                "rank": i,
                "symbol": symbol,
                "source": "core12_existing" if symbol in CORE12 else "liquid80_recommended_addition",
                "tier": tier,
                "probe_score": "" if symbol in CORE12 else scores.get(symbol, ""),
                "eligible_for_backfill_contract": bool(symbol in CORE12 or tier in {"core48_candidate", "midcap_candidate"}),
                "main_historical_proof_status": "existing_core12_controls_only" if symbol in CORE12 else "not_authorized_until_full_source_trace",
                "required_before_use": "existing panel controls" if symbol in CORE12 else "full source trace + listing/survivorship policy + gold panel build",
            }
        )
    return pd.DataFrame(registry)


def compare_recommendations(base_meta: dict[str, Any], liquid_meta: dict[str, Any]) -> pd.DataFrame:
    base = set(base_meta.get("recommended_additions_top36", []))
    liquid = set(liquid_meta.get("recommended_additions_top36", []))
    rows = []
    for label, symbols in [
        ("overlap", sorted(base & liquid)),
        ("added_by_liquid80", sorted(liquid - base)),
        ("dropped_from_base_top36", sorted(base - liquid)),
    ]:
        rows.append({"comparison": label, "count": len(symbols), "symbols": ",".join(symbols)})
    return pd.DataFrame(rows)


def build_authorization(liquid_summary: pd.DataFrame, liquid_df: pd.DataFrame) -> dict[str, Any]:
    liquid_ready = bool(not liquid_summary.empty and bool(liquid_summary.iloc[0].get("exists")))
    tiers = liquid_df["tier"].value_counts().to_dict() if not liquid_df.empty and "tier" in liquid_df else {}
    return {
        "decision": "PASS_A7AC0_UNIVERSE_EXPANSION_HANDOFF_READY_FOR_BACKFILL_CONTRACT",
        "generated_at": utc_stamp(),
        "executes_search": False,
        "executes_replay": False,
        "input_is_new_independent_field_source": False,
        "input_is_universe_expansion_probe": True,
        "liquid80_probe_ready": liquid_ready,
        "candidate_count": int(len(liquid_df)),
        "core48_candidates": int(tiers.get("core48_candidate", 0)),
        "midcap_candidates": int(tiers.get("midcap_candidate", 0)),
        "watchlist_or_new_listing": int(tiers.get("watchlist_or_new_listing", 0)),
        "reject_or_manual_review": int(tiers.get("reject_or_manual_review", 0)),
        "authorizes_core48_data_backfill_contract": True,
        "authorizes_midcap_secondary_backfill_contract": True,
        "authorizes_watchlist_main_historical_proof": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers_before_search": [
            "expanded symbols do not yet have full raw checksum/source trace in repo proof pack",
            "listing date and survivorship policy for expanded universe is not written",
            "probe checks are endpoint/month samples, not full 2024-2026 panel validation",
            "watchlist/new-listing symbols require separate treatment",
            "universe expansion is not a substitute for independent liquidation/orderbook historical sources",
        ],
        "required_next": [
            "A7AC-1 core48/core80 data backfill and source-trace contract",
            "A7AC-2 expanded universe gold panel build audit",
            "A7AC-3 listing/survivorship policy before any expanded-universe replay",
            "Keep alpha proof/shadow/paper/live blocked",
        ],
    }


def write_report(
    base_summary: pd.DataFrame,
    liquid_summary: pd.DataFrame,
    liquid_tiers: pd.DataFrame,
    coverage: pd.DataFrame,
    registry: pd.DataFrame,
    comparison: pd.DataFrame,
    auth: dict[str, Any],
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# CRYPTO A7AC-0 Universe Expansion Handoff Audit",
        "",
        f"Generated: {auth['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{auth['decision']}`",
        "",
        "A7AC-0 accepts the new handoff as a universe-expansion coverage probe. It is not a new independent alpha field source, does not run search/replay, and does not authorize alpha proof.",
        "",
        "## What Arrived",
        "",
        "- Latest handoff: `crypto_universe_expansion_probe_20260522_liquid80_candidates.json`.",
        "- Candidate symbols: 124.",
        "- Main value: broader cross-section coverage for future data backfill and robustness testing.",
        "- Not value: it does not add a new PIT feature field by itself.",
        "",
        "## Probe Summaries",
        "",
        table(pd.concat([base_summary, liquid_summary], ignore_index=True)),
        "",
        "## Liquid80 Tier Summary",
        "",
        table(liquid_tiers),
        "",
        "## Recommended Core12 + Top36 Registry",
        "",
        table(registry, max_rows=60),
        "",
        "## Recommendation Drift vs Previous Probe",
        "",
        table(comparison),
        "",
        "## Source Coverage Matrix",
        "",
        table(coverage, max_rows=140),
        "",
        "## Authorization Matrix",
        "",
        table(pd.DataFrame([auth])),
        "",
        "## Required Next Action",
        "",
        "1. Start A7AC-1 as a data-line backfill/source-trace contract for the expanded universe.",
        "2. Do not use watchlist/new-listing symbols in main historical proof without a separate listing policy.",
        "3. Build and audit expanded gold panels before any formula search uses the new universe.",
        "4. Keep large search, alpha proof, shadow, paper, and live blocked.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base_meta, base_df = read_probe("base_candidates", BASE_PROBE_JSON, BASE_PROBE_CSV)
    liquid_meta, liquid_df = read_probe("liquid80_candidates", LIQUID80_JSON, LIQUID80_CSV)
    base_summary = summarize_probe("base_candidates", base_meta, base_df)
    liquid_summary = summarize_probe("liquid80_candidates", liquid_meta, liquid_df)
    liquid_tiers = tier_summary(liquid_df)
    coverage = source_coverage_matrix(liquid_df)
    registry = recommended_universe(liquid_meta, liquid_df)
    comparison = compare_recommendations(base_meta, liquid_meta)
    auth = build_authorization(liquid_summary, liquid_df)
    manifest = {
        "decision": auth["decision"],
        "generated_at": auth["generated_at"],
        "base_probe_json": str(BASE_PROBE_JSON),
        "base_probe_csv": str(BASE_PROBE_CSV),
        "liquid80_probe_json": str(LIQUID80_JSON),
        "liquid80_probe_csv": str(LIQUID80_CSV),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
    }

    pd.concat([base_summary, liquid_summary], ignore_index=True).to_csv(OUT_DIR / "a7ac0_probe_summary.csv", index=False)
    liquid_tiers.to_csv(OUT_DIR / "a7ac0_liquid80_tier_summary.csv", index=False)
    coverage.to_csv(OUT_DIR / "a7ac0_liquid80_source_coverage_matrix.csv", index=False)
    registry.to_csv(OUT_DIR / "a7ac0_recommended_universe_registry.csv", index=False)
    comparison.to_csv(OUT_DIR / "a7ac0_recommendation_drift_vs_base_probe.csv", index=False)
    write_json(OUT_DIR / "a7ac0_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ac0_manifest.json", manifest)
    write_report(base_summary, liquid_summary, liquid_tiers, coverage, registry, comparison, auth)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
