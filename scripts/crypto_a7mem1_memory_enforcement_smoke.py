from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.search_memory_enforcement import SearchMemoryEnforcer  # noqa: E402


DATE_TAG = "20260628"
RUNTIME = REPO / "runtime" / "a7mem1_memory_enforcement_smoke_20260628"
REPORT = REPO / "reports" / "CRYPTO_A7MEM1_MEMORY_ENFORCEMENT_SMOKE_20260628.md"
PRIOR = REPO / "runtime" / "a7mem0_search_memory_registry_20260628" / "a7mem0_next_search_prior.json"
CANDIDATE_MEMORY = REPO / "runtime" / "a7mem0_search_memory_registry_20260628" / "a7mem0_candidate_memory.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def make_rows() -> list[dict[str, Any]]:
    memory_rows = read_csv(CANDIDATE_MEMORY)
    duplicate_expression = next(row["expression"] for row in memory_rows if row.get("expression"))
    return [
        {
            "blueprint_id": "a7mem1_exact_duplicate",
            "expression": duplicate_expression,
            "semantic_pair": "basis|positioning",
            "motif": "safe_div_abs_gated",
            "horizon_h": 24,
        },
        {
            "blueprint_id": "a7mem1_promote_skeleton_1",
            "expression": "Add(Mean(open_interest_value_last,24),Mean(taker_buy_sell_volume_ratio,24))",
            "semantic_pair": "open_interest|taker_flow",
            "motif": "additive_composite",
            "horizon_h": 24,
        },
        {
            "blueprint_id": "a7mem1_promote_skeleton_2",
            "expression": "Add(Mean(open_interest_value_mean,48),Mean(taker_buy_sell_volume_ratio_mean,48))",
            "semantic_pair": "open_interest|taker_flow",
            "motif": "additive_composite",
            "horizon_h": 24,
        },
        {
            "blueprint_id": "a7mem1_promote_skeleton_3_reject",
            "expression": "Add(Mean(open_interest_value_last,96),Mean(taker_buy_sell_volume_ratio,96))",
            "semantic_pair": "open_interest|taker_flow",
            "motif": "additive_composite",
            "horizon_h": 24,
        },
        {
            "blueprint_id": "a7mem1_downweight_pair_motif",
            "expression": "Mul(SafeDiv(Decay(listing_age_hours,24),Abs(Decay(account_position_divergence,48))),Sign(Decay(trade_quote_volume,96)))",
            "semantic_pair": "age|positioning",
            "motif": "safe_div_abs_gated",
            "horizon_h": 8,
        },
    ]


def make_report(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# CRYPTO A7MEM-1 Memory Enforcement Smoke 20260628",
            "",
            "## Decision",
            "",
            f"`{summary['decision']}`",
            "",
            "Boundary: memory enforcement smoke only. This does not run proxy evaluation, replay, alpha proof, shadow, paper, or live.",
            "",
            "## Checks",
            "",
            f"- fail_closed_missing_prior: `{summary['fail_closed_missing_prior']}`",
            f"- duplicate_expression_rejected: `{summary['duplicate_expression_rejected']}`",
            f"- skeleton_cap_rejected: `{summary['skeleton_cap_rejected']}`",
            f"- promoted_rows: `{summary['promoted_rows']}`",
            f"- downweighted_rows: `{summary['downweighted_rows']}`",
            f"- accepted_rows: `{summary['accepted_rows']}`",
            f"- rejected_rows: `{summary['rejected_rows']}`",
            "",
            "## Next Gate",
            "",
            "A7SEARCH queues must run with A7MEM prior loaded by default. `--no-memory-enforcement` is for legacy reproduction only.",
        ]
    ) + "\n"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    fail_closed = False
    try:
        SearchMemoryEnforcer(prior_path=RUNTIME / "missing_prior.json")
    except FileNotFoundError:
        fail_closed = True

    enforcer = SearchMemoryEnforcer(prior_path=PRIOR)
    input_rows = make_rows()
    accepted, trace, manifest = enforcer.filter_rows(input_rows)
    write_csv(
        RUNTIME / "a7mem1_smoke_input_rows.csv",
        input_rows,
        ["blueprint_id", "semantic_pair", "motif", "horizon_h", "expression"],
    )
    write_csv(
        RUNTIME / "a7mem1_smoke_trace.csv",
        trace,
        [
            "row_index",
            "blueprint_id",
            "semantic_pair",
            "motif",
            "horizon_h",
            "memory_allowed",
            "memory_action",
            "memory_reason",
            "memory_pair_motif",
            "memory_search_weight",
            "expression",
        ],
    )
    write_csv(
        RUNTIME / "a7mem1_smoke_accepted_rows.csv",
        accepted,
        [
            "blueprint_id",
            "semantic_pair",
            "motif",
            "horizon_h",
            "memory_action",
            "memory_reason",
            "memory_search_weight",
            "expression",
        ],
    )

    duplicate_rejected = any(row["blueprint_id"] == "a7mem1_exact_duplicate" and row["memory_allowed"] == "False" for row in trace)
    skeleton_rejected = any(row["blueprint_id"] == "a7mem1_promote_skeleton_3_reject" and row["memory_reason"] == "skeleton_key_cap" for row in trace)
    promoted_rows = sum(1 for row in trace if row["memory_action"] == "promote" and row["memory_allowed"] == "True")
    downweighted_rows = sum(1 for row in trace if row["memory_action"] == "downweight" and row["memory_allowed"] == "True")
    passed = fail_closed and duplicate_rejected and skeleton_rejected and promoted_rows >= 2 and downweighted_rows >= 1
    summary = {
        "object_id": "crypto_a7mem1_memory_enforcement_smoke",
        "decision": "PASS_A7MEM1_MEMORY_ENFORCEMENT_CONNECTED" if passed else "HOLD_A7MEM1_MEMORY_ENFORCEMENT_GAP",
        "prior": str(PRIOR),
        "fail_closed_missing_prior": fail_closed,
        "duplicate_expression_rejected": duplicate_rejected,
        "skeleton_cap_rejected": skeleton_rejected,
        "promoted_rows": promoted_rows,
        "downweighted_rows": downweighted_rows,
        "accepted_rows": len(accepted),
        "rejected_rows": len(input_rows) - len(accepted),
        "enforcer_manifest": manifest,
        "outputs": {
            "input_rows": str(RUNTIME / "a7mem1_smoke_input_rows.csv"),
            "trace": str(RUNTIME / "a7mem1_smoke_trace.csv"),
            "accepted_rows": str(RUNTIME / "a7mem1_smoke_accepted_rows.csv"),
            "report": str(REPORT),
        },
    }
    write_json(RUNTIME / "a7mem1_manifest.json", summary)
    REPORT.write_text(make_report(summary), encoding="utf-8")
    print(summary["decision"])


if __name__ == "__main__":
    main()
