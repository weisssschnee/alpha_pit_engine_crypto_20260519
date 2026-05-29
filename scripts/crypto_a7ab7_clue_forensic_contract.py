from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ab7_clue_forensic_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AB7_CLUE_FORENSIC_CONTRACT_20260529.md"

A7AB6_MANIFEST = REPO / "runtime" / "a7ab6_small_numeric_replay_preflight" / "a7ab6_manifest.json"
A7AB6_CLUES = REPO / "runtime" / "a7ab6_small_numeric_replay_preflight" / "a7ab6_clue_queue.csv"
A7AB5_QUEUE = REPO / "runtime" / "a7ab5_numeric_replay_contract" / "a7ab5_replay_contract_queue.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
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

    a7ab6 = read_json(A7AB6_MANIFEST)
    if not a7ab6.get("authorizes_a7ab7_forensic_contract"):
        raise SystemExit("A7AB-6 does not authorize A7AB-7")
    clues = pd.read_csv(A7AB6_CLUES)
    queue = pd.read_csv(A7AB5_QUEUE)
    clue_candidates = sorted(clues["candidate_id"].astype(str).unique())
    clue_detail = queue.merge(clues, on="candidate_id", how="inner", suffixes=("_candidate", "_clue"))

    forensic_tests = pd.DataFrame(
        [
            {"test": "full_window_replay", "purpose": "rerun clue candidates on full available timestamps, not split-balanced subset"},
            {"test": "nonoverlap_stats", "purpose": "report horizon-aware non-overlap tstats; naive hourly tstats cannot promote"},
            {"test": "control_dominance_by_split", "purpose": "wrong-lag/stale/shuffle/random controls must remain weaker in each pre-May split"},
            {"test": "field_native_latency", "purpose": "one-bar lag survival; no artificial +2h stress policy"},
            {"test": "cost_proxy", "purpose": "2bps/5bps/10bps proxy sensitivity"},
            {"test": "symbol_concentration", "purpose": "no single symbol or symbol tier explains the clue"},
            {"test": "month_concentration", "purpose": "no single month explains the clue"},
            {"test": "return_corr_cluster", "purpose": "cluster clue return streams and cap single cluster"},
            {"test": "skeleton_and_family_diversity", "purpose": "check whether clues are repeated variants of one skeleton/family"},
            {"test": "May_stress_label_only_if_available", "purpose": "May can only be post-selection stress/veto/failure attribution"},
        ]
    )
    pass_gates = pd.DataFrame(
        [
            {"gate": "pre_may_full_window_positive", "rule": "validation/test/recent oriented spread positive in full-window replay"},
            {"gate": "control_ratio_lt_0_80", "rule": "control ratio < 0.80 preferred; >=1.00 hard HOLD"},
            {"gate": "lag_survival", "rule": "one-bar lag remains positive and >=25% of original recent spread"},
            {"gate": "cost_survival", "rule": "2/5/10bps proxy does not erase all pre-May evidence"},
            {"gate": "cluster_diversity", "rule": "no single return-corr cluster >35% of forensic survivors"},
            {"gate": "family_diversity", "rule": "no single generation family >50% of forensic survivors"},
            {"gate": "no_may_leakage", "rule": "May not used in ranking, threshold, selector, generation, or mutation"},
        ]
    )
    clue_family_summary = (
        clue_detail.groupby("family_id", as_index=False)
        .agg(
            clue_rows=("candidate_id", "count"),
            clue_candidates=("candidate_id", "nunique"),
            seed_fields=("primary_seed_field", "nunique"),
            skeletons=("skeleton_key", "nunique"),
        )
        .sort_values(["clue_candidates", "clue_rows"], ascending=[False, False])
    )
    clue_label_summary = (
        clues.groupby(["label_family", "horizon_h"], as_index=False)
        .agg(
            clue_rows=("candidate_id", "count"),
            clue_candidates=("candidate_id", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            max_control_ratio=("control_ratio_premay_max", "max"),
        )
        .sort_values(["clue_rows"], ascending=False)
    )

    decision = "PASS_A7AB7_CLUE_FORENSIC_CONTRACT_READY_FOR_A7AB8"
    manifest = {
        "stage": "A7AB-7",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_contract_only": True,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may": False,
        "input_a7ab6_decision": a7ab6.get("decision"),
        "clue_rows": int(len(clues)),
        "clue_candidate_count": int(len(clue_candidates)),
        "clue_family_count": int(clue_detail["family_id"].nunique()),
        "clue_skeleton_count": int(clue_detail["skeleton_key"].nunique()),
        "authorizes_a7ab8_clue_forensic_execution": True,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    clues.to_csv(RUNTIME / "a7ab7_clue_queue_input.csv", index=False)
    clue_detail.to_csv(RUNTIME / "a7ab7_clue_candidate_detail.csv", index=False)
    clue_family_summary.to_csv(RUNTIME / "a7ab7_clue_family_summary.csv", index=False)
    clue_label_summary.to_csv(RUNTIME / "a7ab7_clue_label_summary.csv", index=False)
    forensic_tests.to_csv(RUNTIME / "a7ab7_required_forensic_tests.csv", index=False)
    pass_gates.to_csv(RUNTIME / "a7ab7_pass_gates.csv", index=False)
    write_json(RUNTIME / "a7ab7_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ab7_authorization_matrix.json",
        {
            "A7AB-7": {"status": decision},
            "A7AB-8_clue_forensic_execution": {"authorized": True},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AB-7 CLUE FORENSIC CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AB-7 is a contract for forensic review of A7AB-6 clues. It does not authorize formula search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Clue Label Summary",
        "",
        md_table(clue_label_summary),
        "",
        "## Clue Family Summary",
        "",
        md_table(clue_family_summary),
        "",
        "## Required Forensic Tests",
        "",
        md_table(forensic_tests),
        "",
        "## Pass Gates",
        "",
        md_table(pass_gates),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
