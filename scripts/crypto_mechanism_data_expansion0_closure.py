from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "runtime" / "mechanism_data_expansion0_20260712"
INVENTORY = ROOT / "inventory_decision.json"
RELEASE = ROOT / "native_aggtrades_release_v1" / "release_manifest.json"
BENCHMARK = ROOT / "native_aggtrades_benchmark_v1" / "benchmark_summary.json"
BENCHMARK_RESULTS = ROOT / "native_aggtrades_benchmark_v1" / "benchmark_results.csv"
BBO_CAPACITY = ROOT / "bbo_full_year_acquisition" / "bbo_acquisition_capacity_summary.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validate_boundaries(inventory: dict[str, Any], release: dict[str, Any], benchmark: dict[str, Any], bbo: dict[str, Any]) -> None:
    if inventory["new_performance_queries"] != 0 or inventory["forward_read"] or inventory["selection_used_performance"]:
        raise PermissionError("inventory boundary violated")
    prohibited_release = ("performance_queries", "performance_values_read", "return_labels_read", "forward_read", "candidate_promotion", "memory_updated")
    if any(release.get(flag) for flag in prohibited_release) or not release.get("reproducible") or release.get("interpolation_used"):
        raise PermissionError("release boundary violated")
    prohibited_benchmark = ("forward_read", "spent_evaluation_read", "candidate_promotion", "memory_update", "complex_search_participation", "additional_budget")
    if any(benchmark.get(flag) for flag in prohibited_benchmark) or benchmark["fixed_evaluations"] != 164:
        raise PermissionError("benchmark boundary or fixed budget violated")
    if bbo["performance_queries"] != 0 or bbo["forward_read"] or bbo["accepted_identity_used"]:
        raise PermissionError("BBO capacity plan boundary violated")


def run() -> dict[str, Any]:
    inventory, release, benchmark, bbo = map(load_json, (INVENTORY, RELEASE, BENCHMARK, BBO_CAPACITY))
    validate_boundaries(inventory, release, benchmark, bbo)
    results = pd.read_csv(BENCHMARK_RESULTS)
    bases = results[results.variant.eq("BASE")]
    decisions = pd.DataFrame([
        {"mechanism": "cross_venue_price_discovery", "decision": "UNAVAILABLE_NO_SOURCE", "evidence": "only recent/May short probes; no verified longitudinal source"},
        {"mechanism": "native_aggtrades_trade_flow", "decision": "REJECT_NO_EDGE", "evidence": "qualified 97.5% scoped release; 164 fixed evaluations; zero admitted benchmark-horizons; every base net LCB negative"},
        {"mechanism": "native_bbo_full_year", "decision": "HOLD_FOR_MORE_DATA", "evidence": f"official monthly source only {bbo['available_coordinates']}/{bbo['source_coordinates']} symbol-months ({bbo['source_availability_ratio']:.2%}); May-Dec HTTP 404"},
        {"mechanism": "multi_level_order_book_depth", "decision": "UNAVAILABLE_NO_SOURCE", "evidence": "no verified historical snapshots/deltas; BBO not relabelled as depth"},
        {"mechanism": "forced_flow_liquidation", "decision": "UNAVAILABLE_NO_SOURCE", "evidence": "no verified historical force-order/liquidation source; proxy substitution prohibited"},
        {"mechanism": "options_expectation_state", "decision": "UNAVAILABLE_NO_SOURCE", "evidence": "no options historical source found on local or PC1"},
    ])
    decisions.to_csv(ROOT / "mechanism_final_decisions.csv", index=False, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    positive_gross_lcb = int((bases.gross_lcb > 0).sum())
    positive_net_lcb = int((bases.net_lcb > 0).sum())
    closure = {
        "status": "MECHANISM_DATA_EXPANSION0_PARTIALLY_COMPLETED",
        "recommendation": "STOP_CRYPTO_ALPHA_DISCOVERY_PENDING_EXTERNAL_DATA",
        "inventory_file_observations": inventory["total_file_observations"],
        "qualified_release": release["release_id"], "release_coverage_ratio": release["coverage_ratio"],
        "benchmark_fixed_evaluations": benchmark["fixed_evaluations"],
        "benchmark_base_rows": len(bases), "benchmark_positive_gross_lcb_rows": positive_gross_lcb,
        "benchmark_positive_net_lcb_rows": positive_net_lcb,
        "benchmark_admitted_horizons": benchmark["admitted_benchmark_horizons"],
        "benchmark_behaviour_neff": benchmark["behaviour_neff"],
        "bbo_official_source_coordinates": bbo["available_coordinates"],
        "bbo_required_coordinates": bbo["source_coordinates"],
        "bbo_source_availability_ratio": bbo["source_availability_ratio"],
        "bbo_available_compressed_gib": bbo["compressed_gib_total"],
        "performance_queries_outside_fixed_canary": 0, "forward_read": False, "spent_evaluation_read": False,
        "candidate_promotion": False, "cross_epoch_memory": False, "formal_search_unlocked": False,
        "per_mechanism_decisions": decisions.to_dict("records"),
    }
    manifest_path = ROOT / "stage_closure_manifest.json"
    manifest_path.write_text(json.dumps(closure, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    bias = {
        "decision": "HOLD_RESEARCH_EXTERNAL_DATA_REQUIRED",
        "discovery_vs_evaluation": "simple hypotheses and horizons frozen before the new physical development/challenge release was evaluated",
        "oos_grade": "NEW_SCOPED_CHALLENGE_ONLY_NOT_FORWARD_OOS",
        "multiple_testing": "eight fixed simple benchmarks, two fixed horizons and five fixed variants; no online selection or budget extension",
        "costs": "5 bps per unit turnover applied to every benchmark and control",
        "leakage_controls": ["one-hour execution delay", "observable-time bucket close", "wrong-lag", "shuffled timing", "matched random", "sign flip"],
        "limitations": ["challenge contains four months", "three checksum-lineage coordinates excluded before performance", "no external cross-venue, forced-flow, full-year BBO or options history"],
        "promotion_allowed": False,
    }
    bias_path = ROOT / "mechanism_data_expansion0_bias_audit.json"
    bias_path.write_text(json.dumps(bias, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# CRYPTO MECHANISM/DATA EXPANSION-0 closure

Status: `{closure['status']}`  
Recommendation: `{closure['recommendation']}`

## What completed

- Inventoried `{inventory['total_file_observations']}` local/PC1 file observations without row-data or performance access.
- Qualified native aggTrades release `{release['release_id']}` at `{release['coverage_ratio']:.2%}` symbol-month coverage with physical development/challenge separation and deterministic content hash `{release['content_sha256']}`.
- Executed exactly `{benchmark['fixed_evaluations']}` frozen simple benchmark/control evaluations. `{positive_gross_lcb}` base rows had positive gross LCB, `0` had positive net LCB, and `0` benchmark-horizons passed future-search admission.
- Measured native-flow behaviour N_eff `{benchmark['behaviour_neff']:.4f}`; this diversity did not produce a cost-surviving mechanism.
- Verified official Binance UM monthly bookTicker source only for `{bbo['available_coordinates']}/{bbo['source_coordinates']}` full-year coordinates (`{bbo['source_availability_ratio']:.2%}`). May-Dec return HTTP 404, so downloading the available `{bbo['compressed_gib_total']:.2f}` GiB cannot satisfy the 95% full-year gate.

## Mechanism decisions

{decisions.to_markdown(index=False)}

Formal search remains frozen. No candidate was promoted, no spent/forward block was read, and no cross-epoch memory was updated. A future crypto-alpha stage requires an independently verified external historical source (cross-venue, full-year BBO, forced-flow or options); expanding the rejected existing formula space is not authorized.
"""
    report_path = ROOT / "MECHANISM_DATA_EXPANSION0_CLOSURE_REPORT.md"
    report_path.write_text(report, encoding="utf-8")
    artifact_paths = [ROOT / "mechanism_final_decisions.csv", manifest_path, bias_path, report_path, BBO_CAPACITY,
                      ROOT / "bbo_full_year_acquisition" / "bbo_source_capacity.csv",
                      ROOT / "native_aggtrades_benchmark_v1" / "benchmark_summary.json",
                      ROOT / "native_aggtrades_benchmark_v1" / "benchmark_results.csv",
                      ROOT / "native_aggtrades_benchmark_v1" / "benchmark_decisions.csv"]
    index = pd.DataFrame([{"artifact": str(path.relative_to(REPO)).replace("\\", "/"), "sha256": sha256_file(path), "role": "MECHANISM_DATA_EXPANSION0_CLOSURE"} for path in artifact_paths])
    index.to_csv(ROOT / "stage_artifact_index.csv", index=False, lineterminator="\n")
    return closure


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
