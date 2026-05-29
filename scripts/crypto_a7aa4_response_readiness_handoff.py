from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7aa4_response_readiness_handoff"
REPORT = REPO / "reports" / "CRYPTO_A7AA4_RESPONSE_READINESS_HANDOFF_20260529.md"

MANIFESTS = {
    "A7AA-0": REPO / "runtime" / "a7aa0_label_feature_response_contract" / "a7aa0_manifest.json",
    "A7AA-1": REPO / "runtime" / "a7aa1_primitive_response_map" / "a7aa1_manifest.json",
    "A7AA-2": REPO / "runtime" / "a7aa2_feature_role_classification" / "a7aa2_manifest.json",
    "A7AA-3": REPO / "runtime" / "a7aa3_selector_rewrite_contract" / "a7aa3_manifest.json",
    "A7AI-F3": REPO / "runtime" / "a7aif3_materialization_evaluator_parity" / "a7aif3_manifest.json",
}
LABEL_CONTRACT = REPO / "runtime" / "a7aa0_label_feature_response_contract" / "a7aa0_label_family_contract.csv"
ROLE_LEDGER = REPO / "runtime" / "a7aa2_feature_role_classification" / "a7aa2_feature_role_ledger.csv"


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
    rows = []
    blockers = []
    for stage, path in MANIFESTS.items():
        payload = read_json(path)
        decision = str(payload.get("decision", "MISSING"))
        pass_like = decision.startswith("PASS_")
        if not pass_like:
            blockers.append(f"{stage}_not_pass")
        rows.append(
            {
                "stage": stage,
                "manifest_path": str(path.relative_to(REPO)).replace("\\", "/"),
                "decision": decision,
                "pass_like": pass_like,
                "executes_search": payload.get("executes_search", False),
                "authorizes_search": payload.get("authorizes_search", payload.get("authorizes_formula_search", False)),
                "authorizes_alpha_proof": payload.get("authorizes_alpha_proof", False),
            }
        )
    label_df = pd.read_csv(LABEL_CONTRACT)
    role_df = pd.read_csv(ROLE_LEDGER)
    label_rows = label_df.copy()
    active_labels = sorted(label_df.loc[label_df["allowed_in_a7aa1"].astype(str).str.lower().isin(["true", "1"]), "label_family"].astype(str).tolist())
    expected = {
        "L0_raw_forward_return",
        "L1_cross_sectional_relative_return",
        "L2_BTC_ETH_beta_residual_return",
        "L3_liquidity_tier_relative_return",
        "L4_latent_state_relative_return",
        "L5_vol_adjusted_return",
        "L6_downside_avoidance",
        "L7_ranked_future_return",
    }
    present = set(label_df["label_family"].astype(str))
    deferred_or_missing = sorted(expected - present)
    signal_candidates = int((role_df["feature_role"] == "predictive_signal_candidate").sum())
    decision = "PASS_A7AA4_RESPONSE_LABEL_READINESS_HANDOFF_FOR_A7SEL0" if not blockers and signal_candidates > 0 else "HOLD_A7AA4_RESPONSE_READINESS_INCOMPLETE"
    manifest = {
        "stage": "A7AA-4",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "reuses_existing_a7aa0_to_a7aa3": True,
        "active_label_families": active_labels,
        "deferred_or_missing_label_families": deferred_or_missing,
        "signal_candidate_field_count": signal_candidates,
        "authorizes_a7sel0": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    summary = pd.DataFrame(rows)
    summary.to_csv(RUNTIME / "a7aa4_reused_stage_summary.csv", index=False)
    label_rows.to_csv(RUNTIME / "a7aa4_label_contract_reuse_audit.csv", index=False)
    role_df.to_csv(RUNTIME / "a7aa4_feature_role_reuse_audit.csv", index=False)
    write_json(RUNTIME / "a7aa4_manifest.json", manifest)
    lines = [
        "# CRYPTO A7AA-4 RESPONSE READINESS HANDOFF",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AA-4 reuses the already executed A7AA-0/1/2/3 response and label adequacy chain. It does not rerun primitive response maps and does not run search.",
        "",
        "## Reused Stages",
        "",
        md_table(summary, 20),
        "",
        "## Label Contract",
        "",
        md_table(label_rows, 20),
        "",
        "## Boundary",
        "",
        "```text",
        "A7AA-4 authorizes only A7SEL-0 dry selector counterfactual.",
        "L7 ranked-return evidence remains diagnostic unless translated to non-L7/raw/relative/portfolio evidence.",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
