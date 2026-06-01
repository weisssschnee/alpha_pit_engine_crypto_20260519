from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore40_book_objective_replay_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE40_BOOK_OBJECTIVE_REPLAY_CONTRACT_20260602.md"
CORE39E = REPO / "runtime" / "a7ffcore39e_symbol_level_book_packet_audit" / "a7ffcore39e_manifest.json"
CORE39E_QUALITY = REPO / "runtime" / "a7ffcore39e_symbol_level_book_packet_audit" / "a7ffcore39e_packet_quality_audit.csv"


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
    source = read_json(CORE39E)
    if source.get("decision") != "PASS_A7FFCORE39E_SYMBOL_LEVEL_PACKET_SAMPLE_READY_FOR_CORE40_CONTRACT":
        raise SystemExit(f"CORE39E not ready for CORE40: {source.get('decision')}")
    quality = pd.read_csv(CORE39E_QUALITY)
    if not quality["pass"].astype(bool).all():
        raise SystemExit("CORE39E packet quality audit did not fully pass")

    book_objectives = pd.DataFrame(
        [
            {"book_objective": "B1_cross_sectional_rank_book", "label_column": "cs_relative_return", "primary": True},
            {"book_objective": "B2_market_beta_residual_book", "label_column": "market_beta_residual_return", "primary": True},
            {"book_objective": "B3_vol_adjusted_rank_book", "label_column": "vol_adjusted_return", "primary": True},
            {"book_objective": "B4_liquidity_cost_capped_book", "label_column": "cs_relative_return", "primary": True},
        ]
    )
    replay_gates = pd.DataFrame(
        [
            {"gate": "original_control_margin", "rule": "original book spread must beat stale and sign_flip controls", "hard_gate": True},
            {"gate": "split_balance", "rule": "validation/test/recent cannot be all negative after train positive", "hard_gate": True},
            {"gate": "family_diversity", "rule": "selected survivors must span >=2 families before any next expansion", "hard_gate": True},
            {"gate": "candidate_count", "rule": "selected survivors >=4 for any expansion contract", "hard_gate": True},
            {"gate": "cost_cap", "rule": "sample uses 5bps; full execution contract must include 2/5/10bps", "hard_gate": False},
            {"gate": "packet_reconciliation", "rule": "book replay must be reproducible from CORE39E packet path", "hard_gate": True},
        ]
    )
    execution_scope = pd.DataFrame(
        [
            {
                "stage": "A7FF-CORE40E",
                "input": source.get("packet_sample_path"),
                "action": "aggregate symbol-level weights and labels into bounded book-objective replay metrics",
                "executes_new_generation": False,
                "executes_search": False,
                "executes_alpha_proof": False,
            }
        ]
    )
    authorization = {
        "authorized": {"A7FF-CORE40E bounded book-objective replay execution": True},
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
            "new_generation": True,
        },
    }
    decision = "PASS_A7FFCORE40_BOOK_OBJECTIVE_REPLAY_CONTRACT_READY_FOR_CORE40E"
    manifest = {
        "stage": "A7FF-CORE40",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE39E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "packet_sample_rows": source.get("packet_sample_rows"),
        "packet_sample_path": source.get("packet_sample_path"),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core40e_execution": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE40E bounded book-objective replay execution",
    }
    quality.to_csv(RUNTIME / "a7ffcore40_source_packet_quality_snapshot.csv", index=False)
    book_objectives.to_csv(RUNTIME / "a7ffcore40_book_objectives.csv", index=False)
    replay_gates.to_csv(RUNTIME / "a7ffcore40_replay_gates.csv", index=False)
    execution_scope.to_csv(RUNTIME / "a7ffcore40_execution_scope.csv", index=False)
    write_json(RUNTIME / "a7ffcore40_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore40_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE40 BOOK OBJECTIVE REPLAY CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE40 authorizes bounded book-objective replay execution over the CORE39E symbol-level packet sample. It does not authorize new generation, formula search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Book Objectives",
        "",
        md_table(book_objectives),
        "",
        "## Replay Gates",
        "",
        md_table(replay_gates),
        "",
        "## Execution Scope",
        "",
        md_table(execution_scope),
        "",
        "## Source Packet Quality",
        "",
        md_table(quality),
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
