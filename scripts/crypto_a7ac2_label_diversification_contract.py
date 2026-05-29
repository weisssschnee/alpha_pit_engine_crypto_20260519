from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ac2_label_diversification_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AC2_LABEL_DIVERSIFICATION_CONTRACT_20260529.md"

A7AC1R_MANIFEST = REPO / "runtime" / "a7ac1r_representative_quarantine_contract" / "a7ac1r_manifest.json"
A7AC1R_SUBSET = REPO / "runtime" / "a7ac1r_representative_quarantine_contract" / "a7ac1r_diagnostic_representative_subset.csv"
A7AC1R_QUARANTINED = REPO / "runtime" / "a7ac1r_representative_quarantine_contract" / "a7ac1r_quarantined_representatives.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 100) -> str:
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

    a7ac1r = read_json(A7AC1R_MANIFEST)
    if not a7ac1r.get("authorizes_a7ac2_label_diversification_contract"):
        raise SystemExit("A7AC-1R does not authorize A7AC-2")

    subset = pd.read_csv(A7AC1R_SUBSET)
    quarantined = pd.read_csv(A7AC1R_QUARANTINED)

    label_family_contract = pd.DataFrame(
        [
            {
                "label_family": "L0_raw_forward_return",
                "role": "raw return sanity check",
                "horizons": "1|4",
                "required": True,
                "promotion_role": "diagnostic_only_unless_neutral_survives",
            },
            {
                "label_family": "L1_cross_sectional_relative_return",
                "role": "market-mean relative return",
                "horizons": "1|4",
                "required": True,
                "promotion_role": "minimum non-ranked diversification target",
            },
            {
                "label_family": "L7_ranked_future_return",
                "role": "current survivor label; must not be sole evidence",
                "horizons": "1|4",
                "required": True,
                "promotion_role": "cannot promote alone",
            },
            {
                "label_family": "L2_btc_eth_residual_return",
                "role": "BTC/ETH beta residual label",
                "horizons": "1|4",
                "required": False,
                "promotion_role": "secondary if local implementation available",
            },
            {
                "label_family": "L3_liquidity_tier_relative_return",
                "role": "liquidity-tier relative label",
                "horizons": "1|4",
                "required": False,
                "promotion_role": "secondary if local implementation available",
            },
            {
                "label_family": "L4_latent_state_relative_return",
                "role": "time-varying latent-state relative label",
                "horizons": "1|4",
                "required": False,
                "promotion_role": "secondary if local implementation available",
            },
        ]
    )
    neutralization_contract = pd.DataFrame(
        [
            {
                "neutralization_mode": "global_rank",
                "required": True,
                "minimum_group_symbols": 30,
                "fallback": "none",
                "purpose": "baseline cross-sectional top/bottom construction",
            },
            {
                "neutralization_mode": "liquidity_tier_neutral",
                "required": True,
                "minimum_group_symbols": 8,
                "fallback": "global_rank",
                "purpose": "separate signal from liquidity tier bias",
            },
            {
                "neutralization_mode": "latent_state_neutral",
                "required": True,
                "minimum_group_symbols": 8,
                "fallback": "liquidity_tier_neutral",
                "purpose": "separate signal from listing-age latent-state bias",
            },
            {
                "neutralization_mode": "meme_multiplier_neutral",
                "required": True,
                "minimum_group_symbols": 8,
                "fallback": "liquidity_tier_neutral",
                "purpose": "separate signal from meme and contract-multiplier effects",
            },
            {
                "neutralization_mode": "btc_eth_beta_residual",
                "required": False,
                "minimum_group_symbols": 30,
                "fallback": "global_rank",
                "purpose": "secondary beta residual check where implementation is available",
            },
        ]
    )
    execution_plan = pd.DataFrame(
        [
            {
                "step": "load_diagnostic_subset",
                "description": "use only A7AC-1R diagnostic representative subset; quarantined representatives remain excluded",
                "executes_search": False,
            },
            {
                "step": "recompute_candidate_signals",
                "description": "re-evaluate the 7 diagnostic expressions on full timestamps for label/neutralization variants only",
                "executes_search": False,
            },
            {
                "step": "evaluate_label_matrix",
                "description": "evaluate required labels L0/L1/L7 at 1h/4h; optional L2/L3/L4 if local inputs are available",
                "executes_search": False,
            },
            {
                "step": "evaluate_neutralization_modes",
                "description": "global, liquidity-tier, latent-state, meme/multiplier neutral where grouping inputs are available",
                "executes_search": False,
            },
            {
                "step": "control_and_lag_audit",
                "description": "wrong-lag/stale/shuffle/sign/random controls plus one-bar execution and 2/5/10/20bps cost proxy",
                "executes_search": False,
            },
            {
                "step": "decide_label_artifact_vs_real_structure",
                "description": "if evidence exists only in L7 ranked-return, freeze as label artifact and stop",
                "executes_search": False,
            },
        ]
    )
    pass_gates = pd.DataFrame(
        [
            {"gate": "quarantine_respected", "rule": "no A7AC-1 blocked representatives in A7AC-3 input"},
            {"gate": "non_ranked_label_support", "rule": "at least 2 diagnostic candidates survive either L0 or L1 in pre-May splits"},
            {"gate": "neutralization_support", "rule": "at least 2 diagnostic candidates survive one required neutralization mode beyond global rank"},
            {"gate": "control_hard_gate", "rule": "control_ratio must remain <1.0 by split and control type"},
            {"gate": "control_warning_disclosure", "rule": "0.80 <= control_ratio < 1.0 remains diagnostic-only warning"},
            {"gate": "nonoverlap_positive", "rule": "nonoverlap min/median tstats must remain positive in validation/test/recent"},
            {"gate": "lag_cost_positive", "rule": "one-bar lag and 20bps proxy must remain positive"},
            {"gate": "label_concentration_resolution", "rule": "if survivors remain L7-only, do not authorize formula search or replay expansion"},
            {"gate": "no_may_leakage", "rule": "May is unavailable to selector/ranking/generation/thresholds and remains stress-only if later observed"},
        ]
    )
    forbidden = pd.DataFrame(
        [
            {"item": "use_quarantined_representative", "reason": "blocked by A7AC-1 nonoverlap tstat"},
            {"item": "formula_search_execution", "reason": "A7AC-2 is contract-only"},
            {"item": "large_search", "reason": "no label diversification evidence yet"},
            {"item": "alpha_proof_shadow_paper_live", "reason": "diagnostic lineage only"},
            {"item": "May_in_selector_or_threshold", "reason": "May must remain stress-only"},
            {"item": "L7_only_promotion", "reason": "current evidence is single label family dominated"},
        ]
    )
    source_summary = pd.DataFrame(
        [
            {
                "source": "A7AC-1R diagnostic subset",
                "path": str(A7AC1R_SUBSET),
                "rows": int(len(subset)),
                "candidates": int(subset["candidate_id"].nunique()),
                "clusters": int(subset["return_corr_cluster"].nunique()),
                "label_families": int(subset["label_family"].nunique()),
            },
            {
                "source": "A7AC-1R quarantined representatives",
                "path": str(A7AC1R_QUARANTINED),
                "rows": int(len(quarantined)),
                "candidates": int(quarantined["candidate_id"].nunique()) if not quarantined.empty else 0,
                "clusters": int(quarantined["return_corr_cluster"].nunique()) if not quarantined.empty else 0,
                "label_families": int(quarantined["label_family"].nunique()) if not quarantined.empty else 0,
            },
        ]
    )
    experiment_record = {
        "date": "2026-05-29",
        "experiment_id": "20260529_a7ac2_label_diversification_contract",
        "objective": "Define a bounded label-diversification and neutralization diagnostic for A7AC-1R representatives.",
        "status": "completed",
        "mode": "light_contract",
        "inputs": {
            "a7ac1r_manifest": str(A7AC1R_MANIFEST),
            "diagnostic_subset": str(A7AC1R_SUBSET),
            "quarantined": str(A7AC1R_QUARANTINED),
        },
        "parameters": {
            "required_labels": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L7_ranked_future_return"],
            "required_horizons": [1, 4],
            "minimum_non_ranked_candidates": 2,
            "minimum_neutralized_candidates": 2,
            "May_usage": "not used",
        },
        "outputs": {"runtime": str(RUNTIME), "report": str(REPORT)},
        "decision": "contract_only",
        "next_action": "A7AC-3 label diversification and neutralization diagnostic",
    }

    decision = "PASS_A7AC2_LABEL_DIVERSIFICATION_CONTRACT_READY_FOR_A7AC3"
    manifest = {
        "stage": "A7AC-2",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_contract_only": True,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may": False,
        "input_a7ac1r_decision": a7ac1r.get("decision"),
        "diagnostic_rows": int(len(subset)),
        "diagnostic_candidates": int(subset["candidate_id"].nunique()),
        "diagnostic_clusters": int(subset["return_corr_cluster"].nunique()),
        "diagnostic_label_families": int(subset["label_family"].nunique()),
        "quarantined_rows": int(len(quarantined)),
        "required_label_count": int(label_family_contract["required"].sum()),
        "required_neutralization_count": int(neutralization_contract["required"].sum()),
        "authorizes_a7ac3_label_diversification_diagnostic": True,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    source_summary.to_csv(RUNTIME / "a7ac2_source_summary.csv", index=False)
    label_family_contract.to_csv(RUNTIME / "a7ac2_label_family_contract.csv", index=False)
    neutralization_contract.to_csv(RUNTIME / "a7ac2_neutralization_contract.csv", index=False)
    execution_plan.to_csv(RUNTIME / "a7ac2_execution_plan.csv", index=False)
    pass_gates.to_csv(RUNTIME / "a7ac2_pass_gates.csv", index=False)
    forbidden.to_csv(RUNTIME / "a7ac2_forbidden_actions.csv", index=False)
    subset.to_csv(RUNTIME / "a7ac2_diagnostic_subset_input.csv", index=False)
    quarantined.to_csv(RUNTIME / "a7ac2_quarantined_input.csv", index=False)
    write_json(RUNTIME / "a7ac2_experiment_record.json", experiment_record)
    write_json(RUNTIME / "a7ac2_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ac2_authorization_matrix.json",
        {
            "A7AC-2": {"status": decision},
            "A7AC-3_label_diversification_and_neutralization_diagnostic": {"authorized": True},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AC-2 LABEL DIVERSIFICATION CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AC-2 defines a bounded label-diversification and neutralization diagnostic for A7AC-1R representatives. It does not execute replay, train, search, or authorize alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Source Summary",
        "",
        md_table(source_summary),
        "",
        "## Label Family Contract",
        "",
        md_table(label_family_contract),
        "",
        "## Neutralization Contract",
        "",
        md_table(neutralization_contract),
        "",
        "## Execution Plan",
        "",
        md_table(execution_plan),
        "",
        "## Pass Gates",
        "",
        md_table(pass_gates),
        "",
        "## Forbidden Actions",
        "",
        md_table(forbidden),
        "",
        "## Experiment Record",
        "",
        "```json",
        json.dumps(experiment_record, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
