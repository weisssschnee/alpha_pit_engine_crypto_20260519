from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore38_portfolio_label_objective_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE38_PORTFOLIO_LABEL_OBJECTIVE_CONTRACT_20260602.md"
CORE37X = REPO / "runtime" / "a7ffcore37x_route_arbitration" / "a7ffcore37x_manifest.json"


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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE37X)
    if source.get("decision") != "PASS_A7FFCORE37X_ROUTE_ARBITRATION_READY_FOR_CORE38_CONTRACT":
        raise SystemExit(f"CORE37X not ready for CORE38: {source.get('decision')}")

    objective_book = pd.DataFrame(
        [
            {
                "objective_id": "B0_legacy_net_spread",
                "role": "reference_only",
                "description": "existing per-candidate net spread proxy used in CORE33/34/36",
                "allowed_as_primary": False,
                "reason": "failed train-to-OOS executable survivor translation",
            },
            {
                "objective_id": "B1_cross_sectional_rank_book",
                "role": "primary_candidate",
                "description": "top/bottom cross-sectional rank book with equal-weight and liquidity-capped variants",
                "allowed_as_primary": True,
                "reason": "tests whether numeric rank response converts into book spread without relying on raw return label only",
            },
            {
                "objective_id": "B2_market_beta_residual_book",
                "role": "primary_candidate",
                "description": "BTC/ETH/market beta residualized return book before spread and control gates",
                "allowed_as_primary": True,
                "reason": "separates market beta from symbol-specific cross-section structure",
            },
            {
                "objective_id": "B3_vol_adjusted_rank_book",
                "role": "diagnostic_primary",
                "description": "vol-adjusted rank return and downside-normalized book proxy",
                "allowed_as_primary": True,
                "reason": "prevents high-vol small symbols from dominating raw spread",
            },
            {
                "objective_id": "B4_liquidity_cost_capped_book",
                "role": "primary_candidate",
                "description": "book proxy with turnover, quote-volume, and cost bucket caps",
                "allowed_as_primary": True,
                "reason": "aligns replay objective to executable capacity and cost before selector scoring",
            },
            {
                "objective_id": "B5_family_role_book",
                "role": "diagnostic_only",
                "description": "family-specific book roles: F1a may be hedge/regime-like; F1b/F2a require control-first directional evidence",
                "allowed_as_primary": False,
                "reason": "CORE36ER showed family-specific failure modes, not one universal objective",
            },
        ]
    )
    label_contract = pd.DataFrame(
        [
            {"label_id": "L0_raw_forward_return", "status": "allowed_reference", "primary": False, "note": "cannot be sole proof label"},
            {"label_id": "L1_cross_sectional_relative_return", "status": "allowed_primary", "primary": True, "note": "preferred for cross-sectional book"},
            {"label_id": "L2_market_beta_residual_return", "status": "required_primary", "primary": True, "note": "must be tested before search authorization"},
            {"label_id": "L3_liquidity_tier_relative_return", "status": "allowed_primary", "primary": True, "note": "controls liquidity-tier distortions"},
            {"label_id": "L5_vol_adjusted_return", "status": "allowed_primary", "primary": True, "note": "controls high-vol dominance"},
            {"label_id": "L7_ranked_future_return", "status": "diagnostic_only", "primary": False, "note": "rank labels cannot alone authorize alpha/search"},
        ]
    )
    book_constraints = pd.DataFrame(
        [
            {"constraint": "max_symbol_weight", "value": "2.5% or lower in top498 book", "hard_gate": True},
            {"constraint": "max_family_weight", "value": "35% selected queue cap", "hard_gate": True},
            {"constraint": "max_cluster_weight", "value": "25% signal-vector/cluster cap", "hard_gate": True},
            {"constraint": "liquidity_cap", "value": "quote-volume tier cap before spread scoring", "hard_gate": True},
            {"constraint": "cost_buckets", "value": "2bps/5bps/10bps variants; primary must survive 5bps", "hard_gate": True},
            {"constraint": "controls", "value": "wrong-lag, stale, shuffle, sign-flip weaker than original", "hard_gate": True},
            {"constraint": "oos_balance", "value": "validation/test/recent cannot be dominated by one split", "hard_gate": True},
        ]
    )
    core38e_plan = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE38E",
                "action": "recompute book-objective adequacy over existing CORE33E/36E artifacts where possible",
                "executes_new_generation": False,
                "executes_search": False,
                "executes_new_replay": False,
            },
            {
                "stage": "A7FF-CORE39",
                "action": "only if CORE38E identifies book-objective survivors, write bounded book-replay contract",
                "executes_new_generation": False,
                "executes_search": False,
                "executes_new_replay": False,
            },
        ]
    )
    authorization = {
        "authorized": {"A7FF-CORE38E executable portfolio-label objective adequacy audit": True},
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
            "same_CORE33_34_36_queue_rerun": True,
        },
    }
    decision = "PASS_A7FFCORE38_PORTFOLIO_LABEL_OBJECTIVE_CONTRACT_READY_FOR_CORE38E"
    manifest = {
        "stage": "A7FF-CORE38",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE37X",
        "source_decision": source.get("decision"),
        "decision": decision,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core38e_audit": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE38E executable portfolio-label objective adequacy audit",
    }
    objective_book.to_csv(RUNTIME / "a7ffcore38_objective_book_contract.csv", index=False)
    label_contract.to_csv(RUNTIME / "a7ffcore38_label_contract.csv", index=False)
    book_constraints.to_csv(RUNTIME / "a7ffcore38_book_constraints.csv", index=False)
    core38e_plan.to_csv(RUNTIME / "a7ffcore38_execution_plan.csv", index=False)
    write_json(RUNTIME / "a7ffcore38_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore38_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE38 PORTFOLIO-LABEL OBJECTIVE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE38 defines the executable portfolio-label objective required after CORE37X rejected same-queue rerun and large formula search. It does not execute replay, generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Objective Book Contract",
        "",
        md_table(objective_book),
        "",
        "## Label Contract",
        "",
        md_table(label_contract),
        "",
        "## Book Constraints",
        "",
        md_table(book_constraints),
        "",
        "## Execution Plan",
        "",
        md_table(core38e_plan),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
