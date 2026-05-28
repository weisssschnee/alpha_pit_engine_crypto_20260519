from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "runtime" / "a7al2x0_authorization_arbitration"
REPORT = REPO / "reports" / "CRYPTO_A7AL2X0_AUTHORIZATION_ARBITRATION_20260528.md"

ARTIFACTS = [
    {
        "record_id": "A7AL-2P2",
        "stage": "local_oi_price_contract",
        "manifest": REPO / "runtime" / "a7al2p2_local_oi_price_search_contract" / "a7al2p2_manifest.json",
        "report": REPO / "reports" / "CRYPTO_A7AL2P2_LOCAL_OI_PRICE_SEARCH_CONTRACT_20260528.md",
        "nominal_commit": "40620fe",
        "precedence": 10,
    },
    {
        "record_id": "A7AL-2Q",
        "stage": "company_local_oi_price_execution",
        "manifest": REPO / "runtime" / "company_a7al2q2r_full_20260528" / "runtime" / "a7al2q_local_oi_price_formula_search" / "a7al2q_manifest.json",
        "report": REPO / "runtime" / "company_a7al2q2r_full_20260528" / "reports" / "CRYPTO_A7AL2Q_LOCAL_OI_PRICE_FORMULA_SEARCH_20260528.md",
        "nominal_commit": "f2f8c3b",
        "precedence": 20,
    },
    {
        "record_id": "A7AL-2R",
        "stage": "company_local_forensic",
        "manifest": REPO / "runtime" / "company_a7al2q2r_full_20260528" / "runtime" / "a7al2r_local_forensic" / "a7al2r_manifest.json",
        "report": REPO / "runtime" / "company_a7al2q2r_full_20260528" / "reports" / "CRYPTO_A7AL2R_LOCAL_FORENSIC_20260528.md",
        "nominal_commit": "f2f8c3b",
        "precedence": 30,
    },
    {
        "record_id": "A7AL-2S",
        "stage": "company_full_followup_contract",
        "manifest": REPO / "runtime" / "a7al2s_company_full_followup_contract" / "a7al2s_manifest.json",
        "report": REPO / "reports" / "CRYPTO_A7AL2S_COMPANY_FULL_FOLLOWUP_CONTRACT_20260528.md",
        "nominal_commit": "2d1efd3",
        "precedence": 40,
    },
    {
        "record_id": "A7AL-2T",
        "stage": "company_may_stress_attribution",
        "manifest": REPO / "runtime" / "a7al2t_company_may_stress_failure_attribution" / "a7al2t_manifest.json",
        "report": REPO / "reports" / "CRYPTO_A7AL2T_COMPANY_MAY_STRESS_FAILURE_ATTRIBUTION_20260528.md",
        "nominal_commit": "c8cb2ae",
        "precedence": 50,
    },
    {
        "record_id": "A7AL-2U",
        "stage": "objective_selector_repair_contract",
        "manifest": REPO / "runtime" / "a7al2u_objective_selector_repair_contract" / "a7al2u_manifest.json",
        "report": REPO / "reports" / "CRYPTO_A7AL2U_OBJECTIVE_SELECTOR_REPAIR_CONTRACT_20260528.md",
        "nominal_commit": "7e34b48",
        "precedence": 60,
    },
    {
        "record_id": "A7AR-7",
        "stage": "shared_candidate_pool",
        "manifest": REPO / "runtime" / "a7ar7_shared_candidate_pool" / "a7ar7_manifest.json",
        "report": REPO / "reports" / "CRYPTO_A7AR7_SHARED_CANDIDATE_POOL_20260528.md",
        "nominal_commit": "52b6e46",
        "precedence": 70,
    },
    {
        "record_id": "A7AL-2V",
        "stage": "replay_aware_selector_dryrun",
        "manifest": REPO / "runtime" / "a7al2v_replay_aware_selector_dryrun" / "a7al2v_manifest.json",
        "report": REPO / "reports" / "CRYPTO_A7AL2V_REPLAY_AWARE_SELECTOR_DRYRUN_20260528.md",
        "nominal_commit": "52b6e46",
        "precedence": 80,
    },
    {
        "record_id": "A7AR-8",
        "stage": "signal_vector_cluster_registry",
        "manifest": REPO / "runtime" / "a7ar8_signal_vector_cluster_registry" / "a7ar8_manifest.json",
        "report": REPO / "reports" / "CRYPTO_A7AR8_SIGNAL_VECTOR_CLUSTER_REGISTRY_20260528.md",
        "nominal_commit": "55f40b9",
        "precedence": 90,
    },
    {
        "record_id": "A7AL-2W",
        "stage": "signal_vector_selector_repair",
        "manifest": REPO / "runtime" / "a7al2w_signal_vector_selector_repair" / "a7al2w_manifest.json",
        "report": REPO / "reports" / "CRYPTO_A7AL2W_SIGNAL_VECTOR_SELECTOR_REPAIR_20260528.md",
        "nominal_commit": "9394520",
        "precedence": 100,
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO, text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as exc:
        return exc.output.strip()


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


def truthy(payload: dict[str, Any], key: str) -> bool:
    value = payload.get(key)
    return bool(value) if value is not None else False


def artifact_inventory() -> pd.DataFrame:
    rows = []
    for item in ARTIFACTS:
        manifest = read_json(item["manifest"])
        rows.append(
            {
                "record_id": item["record_id"],
                "nominal_commit": item["nominal_commit"],
                "stage": item["stage"],
                "manifest_exists": item["manifest"].exists(),
                "report_exists": item["report"].exists(),
                "decision": manifest.get("decision", ""),
                "generated_at": manifest.get("generated_at", ""),
                "authorizes_execution": (
                    truthy(manifest, "authorizes_a7al2q_local_execution")
                    or truthy(manifest, "authorizes_formula_search_execution")
                    or truthy(manifest, "authorizes_large_search")
                ),
                "authorizes_contract": (
                    truthy(manifest, "authorizes_a7al2v_selector_dryrun")
                    or truthy(manifest, "authorizes_a7al2x_objective_family_reset_contract")
                    or truthy(manifest, "authorizes_a7ar7_shared_candidate_pool_builder")
                ),
                "selected_count": manifest.get("selected_count", manifest.get("selected_candidates", "")),
                "selected_stress_clean_count": manifest.get("selected_stress_clean_candidates", ""),
                "stress_clean_count": manifest.get("stress_clean_count", ""),
                "blockers": "|".join(map(str, manifest.get("blockers", []))) if isinstance(manifest.get("blockers"), list) else manifest.get("blockers", ""),
                "precedence": item["precedence"],
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inventory = artifact_inventory()

    local_head = git(["rev-parse", "--short", "HEAD"])
    origin_main = git(["rev-parse", "--short", "origin/main"])
    ahead_behind = git(["rev-list", "--left-right", "--count", "origin/main...HEAD"])
    branch_vv = git(["branch", "-vv"])

    # Later stress and selector evidence supersedes the earlier P2 local-execution
    # authorization. This is an authorization decision only, not a replay result.
    precedence_rows = [
        {
            "record_id": "A7AL-2P2",
            "decision": "PASS_A7AL2P2_LOCAL_OI_PRICE_SEARCH_CONTRACT_READY_FOR_A7AL2Q",
            "superseded_by": "A7AL-2T|A7AL-2U|A7AL-2V|A7AR-8|A7AL-2W",
            "final_status": "SUPERSEDED_DIAGNOSTIC_CONTRACT",
            "reason": "Later company execution, stress attribution, replay-aware selector, signal-vector registry, and selector repair show zero stress-clean selected candidates.",
        },
        {
            "record_id": "A7AL-2Q",
            "decision": "previously_authorized_by_A7AL-2P2",
            "superseded_by": "A7AL-2X0",
            "final_status": "NOT_AUTHORIZED",
            "reason": "Same objective direct OI x price path is stress-vetoed after later evidence.",
        },
        {
            "record_id": "A7AL-2X",
            "decision": "objective_family_reset_contract",
            "superseded_by": "",
            "final_status": "AUTHORIZED_CONTRACT_ONLY",
            "reason": "Move from direct OI x price weak prior to broader OI/positioning interaction contract; no search execution.",
        },
    ]
    decision_precedence = pd.DataFrame(precedence_rows)

    superseded = pd.DataFrame(
        [
            {
                "superseded_record": "A7AL-2P2",
                "superseded_authorization": "authorizes_a7al2q_local_execution",
                "new_status": "suspended_not_authorized",
                "superseding_record": "A7AL-2X0",
                "evidence": "A7AL-2V selected_stress_clean=0; A7AR-8 selected_queue stress veto; A7AL-2W repaired diversity but selected_stress_clean=0",
            }
        ]
    )

    authorization = {
        "decision": "PASS_A7AL2X0_AUTHORIZATION_ARBITRATION_COMPLETE",
        "source_of_truth": "local_main_after_commit_pending_remote_push",
        "local_head_before_a7al2x0_commit": local_head,
        "origin_main_before_a7al2x0_commit": origin_main,
        "origin_main_ahead_behind_before_a7al2x0_commit": ahead_behind,
        "a7al2p2_final_status": "SUPERSEDED_DIAGNOSTIC_CONTRACT",
        "a7al2q_local_execution": "NOT_AUTHORIZED",
        "same_objective_rerun": "NOT_AUTHORIZED",
        "direct_oi_price_expansion": "NOT_AUTHORIZED",
        "large_formula_search": "NOT_AUTHORIZED",
        "a7al2x_objective_family_reset_contract": "AUTHORIZED_CONTRACT_ONLY",
        "a7al2x1_dry_rerank": "AUTHORIZED_AFTER_A7AL2X_CONTRACT",
        "alpha_proof": "NOT_AUTHORIZED",
        "shadow_paper_live": "NOT_AUTHORIZED",
        "may_policy": {
            "may_allowed_for_veto_or_attribution": True,
            "may_allowed_for_selector": False,
            "may_allowed_for_ranking": False,
            "may_allowed_for_generation": False,
            "may_allowed_for_mutation": False,
            "may_allowed_for_weight_update": False,
        },
    }

    required_next = {
        "next_stage": "A7AL-2X objective family reset contract",
        "must_not_do": [
            "execute A7AL-2Q under superseded P2 authorization",
            "rerun same direct OI x price objective",
            "start large formula search",
            "authorize alpha proof/shadow/paper/live",
        ],
        "a7al2x_scope": [
            "direct OI x price becomes stress-vetoed weak prior",
            "allow OI/positioning interaction families only",
            "require shared candidate pool as source of truth",
            "require signal-vector cluster cap",
            "May remains post-selection veto/attribution only",
        ],
    }

    manifest = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AL2X0_AUTHORIZATION_ARBITRATION_COMPLETE",
        "local_head_before_commit": local_head,
        "origin_main_before_commit": origin_main,
        "origin_main_ahead_behind_before_commit": ahead_behind,
        "branch_vv": branch_vv,
        "artifact_records": int(inventory.shape[0]),
        "a7al2p2_superseded": True,
        "authorizes_a7al2q_local_execution": False,
        "authorizes_same_objective_rerun": False,
        "authorizes_direct_oi_price_expansion": False,
        "authorizes_large_search": False,
        "authorizes_a7al2x_contract": True,
        "authorizes_a7al2x1_dry_rerank_after_contract": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "uses_may_for_authorization": "veto_or_attribution_only",
    }

    inventory.to_csv(OUT_DIR / "a7al2x0_artifact_inventory.csv", index=False)
    decision_precedence.to_csv(OUT_DIR / "a7al2x0_decision_precedence.csv", index=False)
    superseded.to_csv(OUT_DIR / "a7al2x0_superseded_records.csv", index=False)
    write_json(OUT_DIR / "a7al2x0_authorization_matrix.json", authorization)
    write_json(OUT_DIR / "a7al2x0_required_next.json", required_next)
    write_json(OUT_DIR / "a7al2x0_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2X0 Authorization Arbitration

Generated: {manifest["generated_at"]}

## Decision

```text
{manifest["decision"]}
```

This stage resolves the authorization conflict between A7AL-2P2 and later A7AL-2Q/2R/2S/2T/2U/2V/AR8/2W evidence. It executes no search, no replay, no training, and no proof.

## Git Source-of-Truth Status

```text
local_head_before_commit: {local_head}
origin_main_before_commit: {origin_main}
origin_main...HEAD before commit: {ahead_behind}
```

Interpretation:

```text
Local main contains later evidence that origin/main does not yet show.
After this arbitration is committed, pushing local main is required for GitHub main to become the source of truth.
```

## Final Authorization

```json
{json.dumps(authorization, indent=2, sort_keys=True)}
```

## Artifact Inventory

{md_table(inventory, 80)}

## Decision Precedence

{md_table(decision_precedence)}

## Superseded Records

{md_table(superseded)}

## Required Next

```json
{json.dumps(required_next, indent=2, sort_keys=True)}
```

## Boundary

```text
Superseded:
  A7AL-2P2 authorization to execute A7AL-2Q local direct OI x price search

Authorized:
  A7AL-2X objective family reset contract only
  A7AL-2X1 dry rerank only after A7AL-2X contract passes

Not authorized:
  A7AL-2Q execution under P2
  same-objective rerun
  direct OI x price expansion
  large formula search
  alpha proof
  shadow / paper / live
```
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
