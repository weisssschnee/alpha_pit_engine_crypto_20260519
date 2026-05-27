from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

A7AC0_DIR = ROOT / "runtime" / "a7ac0_universe_expansion_handoff_audit"
REGISTRY_PATH = A7AC0_DIR / "a7ac0_recommended_universe_registry.csv"
COVERAGE_PATH = A7AC0_DIR / "a7ac0_liquid80_source_coverage_matrix.csv"
AUTH0_PATH = A7AC0_DIR / "a7ac0_authorization_matrix.json"

OUT_DIR = ROOT / "runtime" / "a7ac1_expanded_universe_backfill_contract"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AC1_EXPANDED_UNIVERSE_BACKFILL_CONTRACT_20260522.md"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def table(df: pd.DataFrame, max_rows: int = 100) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    registry = pd.read_csv(REGISTRY_PATH)
    coverage = pd.read_csv(COVERAGE_PATH)
    auth0 = read_json(AUTH0_PATH)
    return registry, coverage, auth0


def build_track_registry(registry: pd.DataFrame, coverage: pd.DataFrame) -> pd.DataFrame:
    core12 = registry[registry["source"].eq("core12_existing")].copy()
    additions = registry[registry["source"].eq("liquid80_recommended_addition")].copy()
    coverage = coverage.copy()

    primary_symbols = set(registry["symbol"].tolist())
    eligible_pool = coverage[coverage["tier"].isin(["core48_candidate", "midcap_candidate"])].copy()
    eligible_pool = eligible_pool.sort_values(["score", "ready_source_checks", "symbol"], ascending=[False, False, True])

    rows = []
    for _, r in core12.iterrows():
        rows.append(
            {
                "track": "baseline_core12_existing",
                "symbol": r["symbol"],
                "tier": "core12_existing",
                "priority": "P0_existing_control",
                "probe_score": "",
                "included_in_primary_core48": True,
                "included_in_secondary_liquid80_pool": True,
                "required_before_experiment": "existing panel controls remain required",
                "historical_proof_status": "existing_core12_only",
            }
        )
    for _, r in additions.iterrows():
        rows.append(
            {
                "track": "primary_core48_top36_addition",
                "symbol": r["symbol"],
                "tier": r["tier"],
                "priority": "P0_backfill_contract",
                "probe_score": r["probe_score"],
                "included_in_primary_core48": True,
                "included_in_secondary_liquid80_pool": True,
                "required_before_experiment": "raw checksum/source trace + listing policy + gold panel build",
                "historical_proof_status": "not_authorized_until_a7ac2_a7ac3_pass",
            }
        )
    for _, r in eligible_pool.iterrows():
        if r["symbol"] in primary_symbols:
            continue
        rows.append(
            {
                "track": "secondary_liquid80_eligible_pool",
                "symbol": r["symbol"],
                "tier": r["tier"],
                "priority": "P1_secondary_contract",
                "probe_score": r["score"],
                "included_in_primary_core48": False,
                "included_in_secondary_liquid80_pool": True,
                "required_before_experiment": "secondary source trace + explicit missingness/listing policy",
                "historical_proof_status": "secondary_pool_not_main_proof",
            }
        )
    return pd.DataFrame(rows)


def build_source_requirements() -> pd.DataFrame:
    rows = [
        {
            "source_family": "futures_trade_klines_1m",
            "priority": "P0",
            "role": "base price/volume panel",
            "raw_source": "Binance Vision USD-M futures klines or equivalent existing collector",
            "target_granularity": "1m raw -> 1h gold",
            "required_for_primary_core48": True,
            "required_for_secondary_pool": True,
            "checksum_required": True,
            "pit_rule": "1h feature available after hour close; execution at next 1h bar or later",
            "acceptance_gate": "raw checksum ok; no duplicate symbol/timestamp; continuous from effective listing start; no inf",
        },
        {
            "source_family": "mark_price_klines_1m",
            "priority": "P0",
            "role": "mark price and mark/index basis",
            "raw_source": "Binance Vision USD-M markPriceKlines or equivalent existing collector",
            "target_granularity": "1m raw -> 1h gold",
            "required_for_primary_core48": True,
            "required_for_secondary_pool": True,
            "checksum_required": True,
            "pit_rule": "mark/index/basis only after bar close; no same-bar execution",
            "acceptance_gate": "raw checksum ok; mark/index ratio definition recorded; no negative/zero price anomalies",
        },
        {
            "source_family": "index_price_klines_1m",
            "priority": "P0",
            "role": "index price and basis denominator",
            "raw_source": "Binance Vision USD-M indexPriceKlines or equivalent existing collector",
            "target_granularity": "1m raw -> 1h gold",
            "required_for_primary_core48": True,
            "required_for_secondary_pool": True,
            "checksum_required": True,
            "pit_rule": "available after bar close; aligned to mark/trade timestamps",
            "acceptance_gate": "raw checksum ok; no duplicate symbol/timestamp; no zero index close",
        },
        {
            "source_family": "premium_index_klines_1m",
            "priority": "P0",
            "role": "premium/basis feature",
            "raw_source": "Binance Vision USD-M premiumIndexKlines or equivalent existing collector",
            "target_granularity": "1m raw -> 1h gold",
            "required_for_primary_core48": True,
            "required_for_secondary_pool": True,
            "checksum_required": True,
            "pit_rule": "available after bar close; never use future premium values",
            "acceptance_gate": "raw checksum ok or explicit hold reason; missing premium treated as blocker for primary symbols",
        },
        {
            "source_family": "funding_rate",
            "priority": "P0",
            "role": "funding state and funding cashflow",
            "raw_source": "Binance futures fundingRate history",
            "target_granularity": "funding event -> latest-known 1h state",
            "required_for_primary_core48": True,
            "required_for_secondary_pool": True,
            "checksum_required": False,
            "pit_rule": "signal can use latest-known observable funding only; future/settled-after-use rates forbidden",
            "acceptance_gate": "funding field contract complete; funding payment timing/sign convention recorded",
        },
        {
            "source_family": "binance_metrics_daily",
            "priority": "P0",
            "role": "open interest, long-short ratios, taker buy/sell ratio",
            "raw_source": "Binance Vision futures/um/daily/metrics",
            "target_granularity": "5m vendor rows -> 1h last observation",
            "required_for_primary_core48": True,
            "required_for_secondary_pool": True,
            "checksum_required": True,
            "pit_rule": "observable_time = raw timestamp + 5m; 1h feature available after hour close",
            "acceptance_gate": "all symbol-days ready or explicit listing/missingness policy; carry vendor jitter/gap caveat",
        },
        {
            "source_family": "aggtrades_enhanced",
            "priority": "P1",
            "role": "aggressor flow and large trade structure",
            "raw_source": "Binance Vision aggTrades",
            "target_granularity": "raw aggTrades -> 1h enhanced features",
            "required_for_primary_core48": False,
            "required_for_secondary_pool": False,
            "checksum_required": True,
            "pit_rule": "1h flow available after hour close; raw aggTrades retained on company machine",
            "acceptance_gate": "source trace complete per symbol-month; no corrupted zip; timestamp continuous by hour",
        },
        {
            "source_family": "cross_exchange_forward_snapshot",
            "priority": "FORWARD_ONLY",
            "role": "forward telemetry context",
            "raw_source": "Binance/OKX/Bybit REST snapshots",
            "target_granularity": "append-only snapshot",
            "required_for_primary_core48": False,
            "required_for_secondary_pool": False,
            "checksum_required": True,
            "pit_rule": "forward-only; cannot backfill historical proof",
            "acceptance_gate": "collector_version/schema_hash/observable_time present; never join to historical proof",
        },
    ]
    return pd.DataFrame(rows)


def build_download_job_plan(track_registry: pd.DataFrame, source_requirements: pd.DataFrame) -> pd.DataFrame:
    rows = []
    p0_sources = source_requirements[source_requirements["priority"].eq("P0")]
    p1_sources = source_requirements[source_requirements["priority"].eq("P1")]
    for _, sym in track_registry.iterrows():
        if sym["track"] == "baseline_core12_existing":
            continue
        sources = p0_sources if sym["track"] == "primary_core48_top36_addition" else p0_sources
        for _, src in sources.iterrows():
            rows.append(
                {
                    "job_group": sym["track"],
                    "symbol": sym["symbol"],
                    "source_family": src["source_family"],
                    "priority": src["priority"],
                    "date_start": "2024-01-01_or_listing_start_if_later",
                    "date_end": "2026-05-22_or_latest_available",
                    "raw_root": "G:/AlphaFactory_CryptoData/raw",
                    "checksum_root": "G:/AlphaFactory_CryptoData/metadata/checksums",
                    "gold_target": "G:/AlphaFactory_CryptoData/gold/panels/crypto_expanded_1h_v1.parquet",
                    "parallelization": "symbol x month shards; checkpoint every 64 symbol-months",
                    "must_not_do": "do not silently forward-fill missing pre-listing or missing source rows",
                }
            )
        if sym["track"] == "primary_core48_top36_addition":
            for _, src in p1_sources.iterrows():
                rows.append(
                    {
                        "job_group": "optional_p1_aggtrades_primary_subset",
                        "symbol": sym["symbol"],
                        "source_family": src["source_family"],
                        "priority": src["priority"],
                        "date_start": "2024-01-01_or_listing_start_if_later",
                        "date_end": "2026-05-22_or_latest_available",
                        "raw_root": "G:/AlphaFactory_CryptoData/raw",
                        "checksum_root": "G:/AlphaFactory_CryptoData/metadata/checksums",
                        "gold_target": "G:/AlphaFactory_CryptoData/gold/microstructure/aggtrades_1h_flow_enhanced_v1_expanded",
                        "parallelization": "symbol x month shards; treat corrupted zips as blocker until redownload",
                        "must_not_do": "do not make aggTrades P1 a blocker for P0 expanded market/metrics panel",
                    }
                )
    return pd.DataFrame(rows)


def build_acceptance_gates() -> pd.DataFrame:
    rows = [
        {
            "gate": "raw_source_trace",
            "required": True,
            "pass_condition": "100% required raw files have manifest rows and checksum status ok where checksum is available",
            "failure_decision": "HOLD_A7AC2_SOURCE_TRACE_INCOMPLETE",
        },
        {
            "gate": "symbol_listing_policy",
            "required": True,
            "pass_condition": "effective_start per symbol is recorded; pre-listing hours are excluded, not filled",
            "failure_decision": "HOLD_A7AC3_LISTING_POLICY_INCOMPLETE",
        },
        {
            "gate": "timestamp_alignment",
            "required": True,
            "pass_condition": "feature_time < execution_time <= label_start_time for all generated features",
            "failure_decision": "FAIL_A7AC_PIT_ALIGNMENT",
        },
        {
            "gate": "gold_panel_integrity",
            "required": True,
            "pass_condition": "no duplicate symbol/timestamp; no inf; numeric anomaly report clean or explained",
            "failure_decision": "HOLD_A7AC2_PANEL_INTEGRITY",
        },
        {
            "gate": "coverage_by_symbol",
            "required": True,
            "pass_condition": "primary_core48 P0 fields continuous from effective_start or missingness explicitly documented",
            "failure_decision": "HOLD_A7AC2_COVERAGE_GAP",
        },
        {
            "gate": "survivorship_bias_label",
            "required": True,
            "pass_condition": "expanded universe selected in 2026 is labeled as fixed research universe until dynamic listing universe is built",
            "failure_decision": "HOLD_A7AC3_SURVIVORSHIP_POLICY",
        },
        {
            "gate": "watchlist_exclusion",
            "required": True,
            "pass_condition": "watchlist/new-listing and reject/manual symbols are excluded from main historical proof",
            "failure_decision": "HOLD_A7AC_WATCHLIST_MIXED_INTO_MAIN_PROOF",
        },
    ]
    return pd.DataFrame(rows)


def build_authorization(track_registry: pd.DataFrame, job_plan: pd.DataFrame) -> dict[str, Any]:
    primary_additions = int(track_registry["track"].eq("primary_core48_top36_addition").sum())
    secondary_symbols = int(track_registry["track"].eq("secondary_liquid80_eligible_pool").sum())
    return {
        "decision": "PASS_A7AC1_BACKFILL_SOURCE_TRACE_CONTRACT_READY_EXECUTION_NOT_RUN",
        "generated_at": utc_stamp(),
        "executes_download": False,
        "executes_panel_build": False,
        "executes_search": False,
        "executes_replay": False,
        "primary_core48_additions": primary_additions,
        "secondary_liquid80_eligible_symbols": secondary_symbols,
        "planned_download_jobs": int(len(job_plan)),
        "authorizes_a7ac2_panel_build_after_data_line_execution": True,
        "authorizes_a7ac3_listing_survivorship_policy": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers_before_search": [
            "A7AC-2 expanded gold panel build audit not completed",
            "A7AC-3 listing/survivorship policy not completed",
            "P0 source trace for expanded symbols not closed",
            "Probe coverage is not equivalent to full historical panel validation",
        ],
        "required_next": [
            "Data line executes P0 downloads/builds for primary_core48 additions",
            "Run A7AC-2 expanded gold panel source trace and integrity audit",
            "Run A7AC-3 listing/survivorship policy audit",
            "Only after A7AC-2/3 pass can a small expanded-universe diagnostic be considered",
        ],
    }


def write_report(
    auth: dict[str, Any],
    track_registry: pd.DataFrame,
    source_requirements: pd.DataFrame,
    job_plan: pd.DataFrame,
    gates: pd.DataFrame,
    auth0: dict[str, Any],
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# CRYPTO A7AC-1 Expanded Universe Backfill Source-Trace Contract",
        "",
        f"Generated: {auth['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{auth['decision']}`",
        "",
        "A7AC-1 defines the data-line contract for expanding beyond core12. It does not download data, build panels, run replay, or authorize formula search.",
        "",
        "## Input Boundary",
        "",
        f"- Upstream A7AC-0 decision: `{auth0.get('decision', '<missing>')}`.",
        "- The upstream handoff is a universe coverage probe, not a new independent alpha field source.",
        "- Primary track is `core12 + liquid80 top36 additions`.",
        "- Secondary track is a larger eligible pool for later backfill triage, not main proof.",
        "",
        "## Track Registry",
        "",
        table(track_registry, max_rows=120),
        "",
        "## Source Requirements",
        "",
        table(source_requirements, max_rows=20),
        "",
        "## Download / Build Job Plan",
        "",
        table(job_plan, max_rows=140),
        "",
        "## Acceptance Gates",
        "",
        table(gates),
        "",
        "## Authorization",
        "",
        table(pd.DataFrame([auth])),
        "",
        "## Required Next Action",
        "",
        "1. Data line executes P0 backfill for primary_core48 additions first.",
        "2. Keep P1 aggTrades expansion separate; do not block the P0 market/funding/metrics panel on full aggTrades history.",
        "3. Run A7AC-2 panel/source-trace audit after files land.",
        "4. Run A7AC-3 listing/survivorship policy before any expanded-universe replay.",
        "5. Keep large search and alpha proof blocked.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    registry, coverage, auth0 = load_inputs()
    track_registry = build_track_registry(registry, coverage)
    source_requirements = build_source_requirements()
    job_plan = build_download_job_plan(track_registry, source_requirements)
    gates = build_acceptance_gates()
    auth = build_authorization(track_registry, job_plan)
    manifest = {
        "decision": auth["decision"],
        "generated_at": auth["generated_at"],
        "upstream_a7ac0": str(AUTH0_PATH),
        "executes_download": False,
        "executes_panel_build": False,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
    }

    track_registry.to_csv(OUT_DIR / "a7ac1_track_symbol_registry.csv", index=False)
    source_requirements.to_csv(OUT_DIR / "a7ac1_source_requirements.csv", index=False)
    job_plan.to_csv(OUT_DIR / "a7ac1_download_job_plan.csv", index=False)
    gates.to_csv(OUT_DIR / "a7ac1_acceptance_gates.csv", index=False)
    write_json(OUT_DIR / "a7ac1_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ac1_manifest.json", manifest)
    write_report(auth, track_registry, source_requirements, job_plan, gates, auth0)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
