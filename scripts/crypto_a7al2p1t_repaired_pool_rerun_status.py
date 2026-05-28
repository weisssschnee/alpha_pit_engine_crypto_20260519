from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "runtime" / "a7al2p1t_repaired_pool_rerun_status"
REPORT = REPO / "reports" / "CRYPTO_A7AL2P1T_REPAIRED_POOL_RERUN_STATUS_20260528.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except EmptyDataError:
        return pd.DataFrame()


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


def stage_row(stage: str, manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    return {
        "stage": stage,
        "decision": manifest.get("decision", ""),
        "generated_at": manifest.get("generated_at", ""),
        "generated_candidates": manifest.get("generated_candidates", ""),
        "selected_or_replayed_candidates": manifest.get("selected_for_a7al2l_replay_preflight", manifest.get("selected_from_a7al2k", "")),
        "candidate_count": manifest.get("candidate_count", ""),
        "clue_count": manifest.get("derived_replay_preflight_clue_count", ""),
        "selector_eligible_count": manifest.get("selector_eligible_count", ""),
        "diagnostic_pass_count": manifest.get("diagnostic_pass_count", ""),
        "blockers": "|".join(manifest.get("blockers", []) or []),
        "warnings": "|".join(manifest.get("warnings", []) or []),
        "authorizes_formula_search_execution": manifest.get("authorizes_formula_search_execution", False),
        "authorizes_alpha_proof": manifest.get("authorizes_alpha_proof", False),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    paths = {
        "k_manifest": REPO / "runtime" / "a7al2k_derived_generator_smoke" / "a7al2k_manifest.json",
        "l_manifest": REPO / "runtime" / "a7al2l_fast_derived_replay_preflight" / "a7al2l_fast_manifest.json",
        "p1_manifest": REPO / "runtime" / "a7al2p1_selector_feature_generation" / "a7al2p1_manifest.json",
        "p1r_manifest": REPO / "runtime" / "a7al2p1r_selector_reweighted_retry" / "a7al2p1r_manifest.json",
    }
    manifests = {key: read_json(path) for key, path in paths.items()}

    stage_summary = pd.DataFrame(
        [
            stage_row("A7AL-2K repaired current generated pool", paths["k_manifest"]),
            stage_row("A7AL-2L repaired current 64-cap replay preflight", paths["l_manifest"]),
            stage_row("A7AL-2P1 selector feature generation on repaired pool", paths["p1_manifest"]),
            stage_row("A7AL-2P1R selector-reweighted retry", paths["p1r_manifest"]),
        ]
    )

    l_decisions = read_csv(REPO / "runtime" / "a7al2l_fast_derived_replay_preflight" / "a7al2l_fast_candidate_decisions.csv")
    p1_features = read_csv(REPO / "runtime" / "a7al2p1_selector_feature_generation" / "a7al2p1_selector_feature_matrix.csv")
    p1r_decisions = read_csv(REPO / "runtime" / "a7al2p1r_selector_reweighted_retry" / "a7al2p1r_decision_record.csv")

    clue_pool = l_decisions[l_decisions["decision"].eq("A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE")].copy() if not l_decisions.empty else pd.DataFrame()
    selector_decisions = p1_features[
        [
            "candidate_id",
            "selector_decision",
            "latent_gate",
            "matched_control_gate",
            "control_ratio_premay_max_by_split",
            "latent_positive_premay_splits",
            "field_families",
            "expression",
        ]
    ].copy() if not p1_features.empty else pd.DataFrame()

    clue_pool.to_csv(OUT_DIR / "a7al2p1t_repaired_clue_pool.csv", index=False)
    selector_decisions.to_csv(OUT_DIR / "a7al2p1t_selector_decisions.csv", index=False)
    p1r_decisions.to_csv(OUT_DIR / "a7al2p1t_p1r_decision_record.csv", index=False)
    stage_summary.to_csv(OUT_DIR / "a7al2p1t_stage_summary.csv", index=False)

    p1 = manifests["p1_manifest"]
    p1r = manifests["p1r_manifest"]
    selector_eligible = int(p1.get("selector_eligible_count", 0) or 0)
    p1r_pass = int(p1r.get("diagnostic_pass_count", 0) or 0)
    if selector_eligible == 0:
        decision = "HOLD_A7AL2P1T_REPAIRED_POOL_NO_SELECTOR_ELIGIBLE_CANDIDATES"
        blockers = ["no_selector_eligible_candidates_after_repaired_pool_rerun"]
        required_next = "regenerate or adjust non-May selector/generator with time-varying latent survival and control dominance earlier in selection; do not draft A7AL-2P2 from the old P1/P1R pool"
    elif p1r_pass == 0:
        decision = "HOLD_A7AL2P1T_REPAIRED_POOL_NO_P1R_PASS"
        blockers = ["no_selector_reweighted_pass_after_repaired_pool_rerun"]
        required_next = "repair selector-reweighted retry before provenance audit; do not draft A7AL-2P2"
    else:
        decision = "PASS_A7AL2P1T_REPAIRED_POOL_READY_FOR_PROVENANCE_AUDIT"
        blockers = []
        required_next = "run or rely on A7AL-2P1S provenance audit before drafting A7AL-2P2"

    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "blockers": blockers,
        "a7al2k_generated_at": manifests["k_manifest"].get("generated_at", ""),
        "a7al2k_generated_candidates": manifests["k_manifest"].get("generated_candidates", 0),
        "a7al2k_selected_for_replay": manifests["k_manifest"].get("selected_for_a7al2l_replay_preflight", 0),
        "a7al2l_generated_at": manifests["l_manifest"].get("generated_at", ""),
        "a7al2l_replay_cap": manifests["l_manifest"].get("replay_cap", 0),
        "a7al2l_clue_count": manifests["l_manifest"].get("derived_replay_preflight_clue_count", 0),
        "a7al2p1_generated_at": p1.get("generated_at", ""),
        "a7al2p1_candidate_count": p1.get("candidate_count", 0),
        "a7al2p1_selector_eligible_count": selector_eligible,
        "a7al2p1_decision_counts": p1.get("decision_counts", {}),
        "a7al2p1r_generated_at": p1r.get("generated_at", ""),
        "a7al2p1r_decision": p1r.get("decision", ""),
        "a7al2p1r_diagnostic_pass_count": p1r_pass,
        "executes_training": False,
        "executes_search": False,
        "executes_alpha_proof": False,
        "authorizes_a7al2p2": False,
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": required_next,
    }
    write_json(OUT_DIR / "a7al2p1t_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2P1T Repaired Pool Rerun Status

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This status record freezes the repaired current A7AL-2K/L/P1/P1R rerun. It supersedes the stale two-candidate P1/P1R selector pool for downstream authorization.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Stage Summary

{md_table(stage_summary, 20)}

## Repaired A7AL-2L Clue Pool

{md_table(clue_pool[["candidate_id", "decision", "cell", "family", "field_families", "fields", "control_dominance_ratio_premay_max", "one_bar_lag_recent_spread"]], 20) if not clue_pool.empty else "`<empty>`"}

## P1 Selector Decisions

{md_table(selector_decisions, 20)}

## Boundary

```text
Authorized:
  none

Not authorized:
  A7AL-2P2 local search contract
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
