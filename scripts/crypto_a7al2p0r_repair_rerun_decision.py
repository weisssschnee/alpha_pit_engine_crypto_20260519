from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "runtime" / "a7al2p0r_repair_rerun_decision"
REPORT = REPO / "reports" / "CRYPTO_A7AL2P0R_REPAIR_RERUN_DECISION_20260528.md"


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


def csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except EmptyDataError:
        return pd.DataFrame()


def stage_row(stage: str, manifest_path: Path, decision_key: str = "decision") -> dict[str, Any]:
    manifest = read_json(manifest_path)
    return {
        "stage": stage,
        "decision": manifest.get(decision_key, ""),
        "generated_at": manifest.get("generated_at", ""),
        "blockers": "|".join(manifest.get("blockers", []) or []),
        "warnings": "|".join(manifest.get("warnings", []) or []),
        "authorizes_formula_search_execution": manifest.get("authorizes_formula_search_execution", False),
        "authorizes_alpha_proof": manifest.get("authorizes_alpha_proof", False),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    paths = {
        "a7al2k": REPO / "runtime" / "a7al2k_derived_generator_smoke" / "a7al2k_manifest.json",
        "a7al2l": REPO / "runtime" / "a7al2l_fast_derived_replay_preflight" / "a7al2l_fast_manifest.json",
        "a7al2m": REPO / "runtime" / "a7al2m_derived_clue_forensic" / "a7al2m_manifest.json",
        "a7al2n": REPO / "runtime" / "a7al2n_derived_deep_audit" / "a7al2n_manifest.json",
        "a7al2o": REPO / "runtime" / "a7al2o_candidate_mini_replay" / "a7al2o_manifest.json",
        "a7al2p0": REPO / "runtime" / "a7al2p0_pre_search_hardening_audit" / "a7al2p0_manifest.json",
    }
    manifests = {name: read_json(path) for name, path in paths.items()}

    stage_summary = pd.DataFrame(
        [
            stage_row("A7AL-2K repaired generator smoke", paths["a7al2k"]),
            stage_row("A7AL-2L fast replay preflight rerun", paths["a7al2l"]),
            stage_row("A7AL-2M clue forensic rerun", paths["a7al2m"]),
            stage_row("A7AL-2N deep audit rerun", paths["a7al2n"]),
            stage_row("A7AL-2O mini replay rerun", paths["a7al2o"]),
            stage_row("A7AL-2P0 hardening audit rerun", paths["a7al2p0"]),
        ]
    )

    alias_audit = csv_or_empty(REPO / "runtime" / "a7al2p0_pre_search_hardening_audit" / "a7al2p0_canonical_field_alias_code_audit.csv")
    stale_alias = csv_or_empty(REPO / "runtime" / "a7al2p0_pre_search_hardening_audit" / "a7al2p0_stale_artifact_alias_violations.csv")
    control_gate = csv_or_empty(REPO / "runtime" / "a7al2p0_pre_search_hardening_audit" / "a7al2p0_matched_control_gate_by_split.csv")
    latent = csv_or_empty(REPO / "runtime" / "a7al2p0_pre_search_hardening_audit" / "a7al2p0_timevarying_latent_neutralization.csv")
    selector = csv_or_empty(REPO / "runtime" / "a7al2p0_pre_search_hardening_audit" / "a7ar5_replay_aware_selector_score_components.csv")
    a7ar5_contract = read_json(REPO / "runtime" / "a7al2p0_pre_search_hardening_audit" / "a7ar5_replay_aware_selector_contract.json")

    code_alias_fail = not alias_audit[alias_audit.get("status", pd.Series(dtype=str)).eq("FAIL")].empty if not alias_audit.empty else True
    stale_alias_count = int(len(stale_alias))
    control_hold = control_gate[control_gate.get("gate", pd.Series(dtype=str)).eq("HOLD_CONTROL_DOMINATED")].copy() if not control_gate.empty else pd.DataFrame()
    premay_control_hold = (
        control_hold[control_hold.get("split", pd.Series(dtype=str)).isin(["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"])]
        if not control_hold.empty
        else pd.DataFrame()
    )
    latent_premay = (
        latent[latent.get("split", pd.Series(dtype=str)).isin(["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"])]
        if not latent.empty
        else pd.DataFrame()
    )
    latent_negative = (
        latent_premay[pd.to_numeric(latent_premay.get("mean_oriented_spread", pd.Series(dtype=float)), errors="coerce").le(0)]
        if not latent_premay.empty
        else pd.DataFrame()
    )

    p0_manifest = manifests["a7al2p0"]
    blockers = list(p0_manifest.get("blockers", []) or [])
    warnings = list(p0_manifest.get("warnings", []) or [])
    if code_alias_fail:
        blockers.append("canonical_alias_code_fail_after_repair")
    if stale_alias_count:
        warnings.append("stale_alias_artifacts_remain_after_repair")

    decision = "PASS_A7AL2P0R_REPAIR_RERUN_READY_FOR_A7AL2P_DRAFT" if not blockers else "HOLD_A7AL2P0R_REPAIR_RERUN_BLOCKED"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "rerun_scope": "A7AL-2K/L/M/N/O/P0 repaired chain",
        "executes_training": False,
        "executes_search": False,
        "executes_alpha_proof": False,
        "a7al2l_replay_cap": manifests["a7al2l"].get("replay_cap"),
        "a7al2k_generated_candidates": manifests["a7al2k"].get("generated_candidates"),
        "a7al2k_selected_for_replay": manifests["a7al2k"].get("selected_for_a7al2l_replay_preflight"),
        "a7al2l_clue_count": manifests["a7al2l"].get("derived_replay_preflight_clue_count"),
        "a7al2m_deep_audit_candidate_count": manifests["a7al2m"].get("deep_audit_candidate_count"),
        "a7al2n_diagnostic_pass_count": manifests["a7al2n"].get("diagnostic_pass_count"),
        "a7al2o_diagnostic_pass_count": manifests["a7al2o"].get("diagnostic_pass_count"),
        "a7al2p0_decision": p0_manifest.get("decision"),
        "a7ar5_contract_decision": a7ar5_contract.get("decision"),
        "blockers": blockers,
        "warnings": warnings,
        "canonical_alias_code_fail": code_alias_fail,
        "stale_alias_artifact_count": stale_alias_count,
        "premay_control_hold_count": int(len(premay_control_hold)),
        "timevarying_latent_negative_premay_rows": int(len(latent_negative)),
        "authorizes_a7al2p_contract": False,
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": "repair selector/neutralization or regenerate candidate pool; do not run A7AL-2 formula search",
    }

    stage_summary.to_csv(OUT_DIR / "a7al2p0r_stage_summary.csv", index=False)
    premay_control_hold.to_csv(OUT_DIR / "a7al2p0r_premay_control_hold_rows.csv", index=False)
    latent_negative.to_csv(OUT_DIR / "a7al2p0r_timevarying_latent_negative_rows.csv", index=False)
    selector.to_csv(OUT_DIR / "a7al2p0r_a7ar5_selector_score_components.csv", index=False)
    write_json(OUT_DIR / "a7al2p0r_stage_manifest_snapshot.json", manifests)
    write_json(OUT_DIR / "a7al2p0r_a7ar5_contract_snapshot.json", a7ar5_contract)
    write_json(OUT_DIR / "a7al2p0r_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2P0R Repair Rerun Decision

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This stage reruns the repaired A7AL-2K/L/M/N/O/P0 chain after the J5 canonical overlay and silent-fallback fix. It is a repair rerun only: no training, no search execution, no alpha proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Stage Summary

{md_table(stage_summary, 20)}

## Canonical Alias Result

{md_table(alias_audit, 40)}

Stale blocked-alias artifacts after rerun:

```text
{stale_alias_count}
```

## Matched-Control Hard Gate

Premay HOLD rows:

{md_table(premay_control_hold, 40)}

## Time-Varying Latent Neutralization

Premay negative/zero rows:

{md_table(latent_negative, 40)}

## A7AR-5 Replay-Aware Selector

```json
{json.dumps(a7ar5_contract, indent=2, sort_keys=True)}
```

## Boundary

```text
Not authorized:
  A7AL-2P search contract
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
