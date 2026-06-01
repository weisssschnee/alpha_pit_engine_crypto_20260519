from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore48r_dry_seed_generation_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE48R_DRY_SEED_GENERATION_FORENSIC_20260602.md"
CORE48E = REPO / "runtime" / "a7ffcore48e_null_first_dry_seed_generation" / "a7ffcore48e_manifest.json"
QUALITY = REPO / "runtime" / "a7ffcore48e_null_first_dry_seed_generation" / "a7ffcore48e_quality_gate.csv"
FAMILY_OPERATOR = REPO / "runtime" / "a7ffcore48e_null_first_dry_seed_generation" / "a7ffcore48e_family_operator_summary.csv"
ELIGIBLE = REPO / "runtime" / "a7ffcore48e_null_first_dry_seed_generation" / "a7ffcore48e_eligible_seed_queue.csv"


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
    source = read_json(CORE48E)
    if source.get("decision") != "HOLD_A7FFCORE48E_NULL_FIRST_DRY_SEEDS_INSUFFICIENT":
        raise SystemExit(f"CORE48E not ready for CORE48R: {source.get('decision')}")
    quality = pd.read_csv(QUALITY)
    family_operator = pd.read_csv(FAMILY_OPERATOR)
    eligible = pd.read_csv(ELIGIBLE)

    gate_forensic = quality.copy()
    gate_forensic["forensic_class"] = gate_forensic.apply(
        lambda r: "pass" if str(r["pass"]).lower() == "true" else (
            "operator_breadth_fail" if r["metric"] == "operator_count" else
            "motif_concentration_fail" if r["metric"] == "motif_cap_violation_count" else
            "other_fail"
        ),
        axis=1,
    )
    operator_forensic = (
        eligible.groupby("operator", as_index=False)
        .agg(seed_count=("seed_id", "count"), semantic_family_count=("semantic_pair", "nunique"))
        .sort_values("seed_count", ascending=False)
    )
    operator_forensic["seed_share"] = operator_forensic["seed_count"] / max(int(eligible.shape[0]), 1)
    family_forensic = (
        eligible.groupby("semantic_pair", as_index=False)
        .agg(seed_count=("seed_id", "count"), operator_count=("operator", "nunique"))
        .sort_values("seed_count", ascending=False)
    )
    family_forensic["seed_share"] = family_forensic["seed_count"] / max(int(eligible.shape[0]), 1)
    route_options = pd.DataFrame(
        [
            {
                "route_id": "R0_relax_operator_gate",
                "decision": "REJECT",
                "reason": "would admit unprobed operators into eligible null-first queue",
            },
            {
                "route_id": "R1_proceed_to_core49",
                "decision": "REJECT",
                "reason": "eligible seed queue has only three native operators and motif caps fail",
            },
            {
                "route_id": "R2_operator_null_coverage_repair_contract",
                "decision": "SELECT",
                "reason": "field/family breadth is adequate; repair missing native null-aware operator coverage before vector preflight",
            },
        ]
    )
    decision = "PASS_A7FFCORE48R_DRY_SEED_FORENSIC_READY_FOR_CORE48S_OPERATOR_REPAIR"
    manifest = {
        "stage": "A7FF-CORE48R",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE48E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "dominant_failure": "operator_breadth_and_motif_concentration_after_successful_seed_supply",
        "eligible_seed_count": source.get("eligible_seed_count"),
        "eligible_semantic_family_count": source.get("eligible_semantic_family_count"),
        "eligible_operator_count": source.get("eligible_operator_count"),
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core48s_operator_repair_contract": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE48S operator-null coverage repair contract",
    }
    gate_forensic.to_csv(RUNTIME / "a7ffcore48r_gate_forensic.csv", index=False)
    operator_forensic.to_csv(RUNTIME / "a7ffcore48r_operator_forensic.csv", index=False)
    family_forensic.to_csv(RUNTIME / "a7ffcore48r_family_forensic.csv", index=False)
    route_options.to_csv(RUNTIME / "a7ffcore48r_route_options.csv", index=False)
    family_operator.to_csv(RUNTIME / "a7ffcore48r_family_operator_source_summary.csv", index=False)
    write_json(RUNTIME / "a7ffcore48r_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE48R DRY SEED GENERATION FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE48R classifies CORE48E as a supply-width improvement with an operator/motif coverage failure, not a field-family failure. It does not authorize replay, formula search, large search, proof, shadow, paper, live, or promotion.",
        "",
        "## Gate Forensic",
        "",
        md_table(gate_forensic),
        "",
        "## Operator Forensic",
        "",
        md_table(operator_forensic),
        "",
        "## Family Forensic",
        "",
        md_table(family_forensic),
        "",
        "## Route Options",
        "",
        md_table(route_options),
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
