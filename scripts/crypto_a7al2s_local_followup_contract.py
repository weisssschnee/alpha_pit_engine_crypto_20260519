from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CONTEXT = os.environ.get("A7AL2S_CONTEXT", "local").strip() or "local"
OUT_DIR = Path(os.environ.get("A7AL2S_OUT_DIR", str(REPO / "runtime" / "a7al2s_local_followup_contract")))
REPORT = Path(
    os.environ.get(
        "A7AL2S_REPORT",
        str(REPO / "reports" / "CRYPTO_A7AL2S_LOCAL_FOLLOWUP_CONTRACT_20260528.md"),
    )
)

A7AL2R_BASE = Path(os.environ.get("A7AL2R_BASE_DIR", str(REPO / "runtime" / "a7al2r_local_forensic")))
A7AL2R_MANIFEST = A7AL2R_BASE / "a7al2r_manifest.json"
A7AL2R_DECISIONS = A7AL2R_BASE / "a7al2r_decision_record.csv"
A7AL2R_CONTROL = A7AL2R_BASE / "a7al2r_control_dominance.csv"
A7AL2R_VARIANTS = A7AL2R_BASE / "a7al2r_variant_metrics.csv"


def utc_now() -> str:
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
        if pd.api.types.is_object_dtype(view[col]) or pd.api.types.is_string_dtype(view[col]):
            view[col] = view[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```\n" + view.to_string(index=False) + "\n```"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    r_manifest = read_json(A7AL2R_MANIFEST)
    if r_manifest.get("decision") != "PASS_A7AL2R_LOCAL_FORENSIC_CANDIDATES_READY_FOR_A7AL2S_CONTRACT":
        raise SystemExit("A7AL-2R is not ready for A7AL-2S")

    decisions = pd.read_csv(A7AL2R_DECISIONS)
    control = pd.read_csv(A7AL2R_CONTROL)
    variants = pd.read_csv(A7AL2R_VARIANTS)

    may_control = control[control["split"].eq("known_may2026_stress")].copy()
    may_summary = (
        may_control.groupby("candidate_id", as_index=False)
        .agg(
            may_control_ratio_max=("control_ratio", "max"),
            may_gate_max=("gate", lambda s: ";".join(sorted(set(map(str, s))))),
        )
    )
    pre_may_control = control[~control["split"].eq("known_may2026_stress")].copy()
    pre_may_summary = (
        pre_may_control.groupby("candidate_id", as_index=False)
        .agg(
            pre_may_control_ratio_max=("control_ratio", "max"),
            pre_may_control_gates=("gate", lambda s: ";".join(sorted(set(map(str, s))))),
        )
    )
    variant_summary = (
        variants[
            variants["entry_label"].eq("label_t1_to_t25")
            & variants["variant"].eq("original")
            & ~variants["split"].eq("known_may2026_stress")
        ]
        .groupby("candidate_id", as_index=False)
        .agg(
            premay_positive_split_count=("mean_oriented_spread", lambda s: int((s > 0).sum())),
            min_split_mean_spread=("mean_oriented_spread", "min"),
            max_split_mean_spread=("mean_oriented_spread", "max"),
        )
    )

    tiers = decisions.merge(pre_may_summary, on="candidate_id", how="left")
    tiers = tiers.merge(may_summary, on="candidate_id", how="left")
    tiers = tiers.merge(variant_summary, on="candidate_id", how="left")
    tiers["warnings"] = tiers["warnings"].fillna("")
    tiers["reasons"] = tiers["reasons"].fillna("")

    def tier(row: pd.Series) -> str:
        decision_value = str(row.get("decision", "") or "")
        reasons = str(row.get("reasons", "") or "")
        warnings = str(row.get("warnings", "") or "")
        may_gate = str(row.get("may_gate_max", "") or "")
        if "HOLD_CONTROL_DOMINATED" in may_gate:
            stress = "may_control_dominated"
        else:
            stress = "may_stress_not_clean"
        if decision_value != "A7AL2R_LOCAL_FORENSIC_PASS":
            hold_reason = reasons.strip() or decision_value or "forensic_hold"
            hold_reason = hold_reason.lower().replace("hold_a7al2r_", "").replace(" ", "_")
            return f"hold_{hold_reason}__{stress}"
        if warnings.strip():
            return f"watchlist_control_close__{stress}"
        return f"primary_clean_premay__{stress}"

    tiers["a7al2s_tier"] = tiers.apply(tier, axis=1)
    tiers["allowed_as_seed_for_large_search"] = False
    tiers["allowed_as_seed_for_company_full_qr_comparison"] = CONTEXT != "company_full"
    tiers["allowed_for_may_stress_failure_attribution"] = True
    tiers["allowed_for_local_expansion_before_full_pool"] = False

    if CONTEXT == "company_full":
        action_matrix = pd.DataFrame(
            [
                {
                    "action": "a7al2t_company_may_stress_attribution",
                    "status": "AUTHORIZED",
                    "reason": "company full run produced a 14-candidate forensic pool; classify stress behavior before any expansion",
                },
                {
                    "action": "a7al2u_objective_or_selector_repair_contract",
                    "status": "AUTHORIZED_FOR_CONTRACT_ONLY",
                    "reason": "control dominance remains high in fast replay and must feed selector/objective repair, not direct expansion",
                },
                {
                    "action": "local_narrow_mutation_expansion",
                    "status": "NOT_AUTHORIZED",
                    "reason": "company full results supersede local pilot and still require stress attribution",
                },
                {
                    "action": "large_formula_search",
                    "status": "NOT_AUTHORIZED",
                    "reason": "company full run is diagnostic and not a proof object",
                },
                {
                    "action": "alpha_proof_shadow_paper_live",
                    "status": "NOT_AUTHORIZED",
                    "reason": "no append-only proof and stress attribution remains pending",
                },
            ]
        )
    else:
        action_matrix = pd.DataFrame(
            [
                {
                    "action": "company_full_a7al2q2r",
                    "status": "AUTHORIZED_IF_COMPANY_PATH_AVAILABLE",
                    "reason": "local pilot executed only 16 replay candidates; full 128 replay/deep pass should be checked off local memory path",
                },
                {
                    "action": "a7al2t_may_stress_failure_attribution",
                    "status": "AUTHORIZED",
                    "reason": "all four local forensic candidates are pre-May positive but May/control dominated; classify failure without using May for selection",
                },
                {
                    "action": "local_narrow_mutation_expansion",
                    "status": "HOLD_UNTIL_FULL_QR_OR_A7AL2T",
                    "reason": "avoid amplifying a four-candidate local pilot before full-pool confirmation",
                },
                {
                    "action": "large_formula_search",
                    "status": "NOT_AUTHORIZED",
                    "reason": "current evidence is local diagnostic only",
                },
                {
                    "action": "alpha_proof_shadow_paper_live",
                    "status": "NOT_AUTHORIZED",
                    "reason": "May stress remains negative/control dominated and no append-only proof exists",
                },
            ]
        )
    gates = pd.DataFrame(
        [
            {"gate": "full_pool_required", "requirement": "A7AL-2Q/2R full 128 replay on company resources before expansion"},
            {"gate": "may_stress_only", "requirement": "May can be failure attribution/veto only, never selector/ranking/mutation"},
            {"gate": "control_close_handling", "requirement": "control_close candidates stay watchlist unless full-pool controls improve"},
            {"gate": "primary_seed_handling", "requirement": "no-warning candidates are diagnostic primary clues, not proof objects"},
            {"gate": "negative_controls", "requirement": "wrong-lag, shuffle, same-family controls remain attached"},
            {"gate": "artifact_chain", "requirement": "use committed A7AL-2Q and A7AL-2R artifacts only"},
        ]
    )

    clean_count = int(tiers["a7al2s_tier"].str.startswith("primary_clean_premay").sum())
    watch_count = int(tiers["a7al2s_tier"].str.startswith("watchlist_control_close").sum())
    decision = "PASS_A7AL2S_COMPANY_FULL_FOLLOWUP_CONTRACT_READY" if CONTEXT == "company_full" else "PASS_A7AL2S_LOCAL_FOLLOWUP_CONTRACT_READY"
    manifest = {
        "generated_at": utc_now(),
        "context": CONTEXT,
        "decision": decision,
        "input_a7al2r_decision": r_manifest.get("decision"),
        "input_a7al2r_base_dir": str(A7AL2R_BASE),
        "candidate_count": int(len(tiers)),
        "primary_clean_premay_count": clean_count,
        "watchlist_control_close_count": watch_count,
        "authorizes_company_full_a7al2q2r": CONTEXT != "company_full",
        "authorizes_a7al2t_may_stress_failure_attribution": True,
        "authorizes_local_expansion_before_full_pool": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may_for_selection": False,
        "uses_may_for_ranking": False,
        "uses_may_for_mutation": False,
        "blockers": [],
        "required_next": "Run A7AL-2T stress attribution on this company full pool; do not start expansion or large search."
        if CONTEXT == "company_full"
        else "Run company full A7AL-2Q/2R when company data path is mounted, or run A7AL-2T May stress failure attribution; do not start large search.",
    }

    tiers.to_csv(OUT_DIR / "a7al2s_candidate_tiers.csv", index=False)
    action_matrix.to_csv(OUT_DIR / "a7al2s_action_authorization_matrix.csv", index=False)
    gates.to_csv(OUT_DIR / "a7al2s_followup_gates.csv", index=False)
    write_json(OUT_DIR / "a7al2s_manifest.json", manifest)

    title = "CRYPTO A7AL-2S Company Full Follow-Up Contract" if CONTEXT == "company_full" else "CRYPTO A7AL-2S Local Follow-Up Contract"
    report = f"""# {title}

Generated: {manifest["generated_at"]}

## Decision

```text
{manifest["decision"]}
```

This is a contract only. It executes no search, no training, no replay, and no proof. It converts the A7AL-2R forensic result into explicit next-step authorization.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Candidate Tiers

{md_table(tiers, 20)}

## Action Authorization

{md_table(action_matrix, 20)}

## Follow-Up Gates

{md_table(gates, 20)}

## Boundary

```text
Authorized:
  A7AL-2T May-stress failure attribution
  company full A7AL-2Q/2R run when company path is available only for local context

Not authorized:
  local expansion before full-pool confirmation
  large formula search
  alpha proof
  shadow / paper / live
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
