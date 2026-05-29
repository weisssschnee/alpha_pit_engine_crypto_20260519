from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7aa3_selector_rewrite_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AA3_SELECTOR_REWRITE_CONTRACT_20260529.md"
A7AA2_MANIFEST = REPO / "runtime" / "a7aa2_feature_role_classification" / "a7aa2_manifest.json"
A7AA2_SEEDS = REPO / "runtime" / "a7aa2_feature_role_classification" / "a7aa2_selector_seed_fields.csv"
A7AA2_POLICY = REPO / "runtime" / "a7aa2_feature_role_classification" / "a7aa2_selector_rewrite_seed_policy.json"


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

    a7aa2 = read_json(A7AA2_MANIFEST)
    if not a7aa2.get("authorizes_a7aa3_selector_rewrite_contract"):
        raise SystemExit("A7AA-2 does not authorize A7AA-3")
    seeds = pd.read_csv(A7AA2_SEEDS)
    policy = read_json(A7AA2_POLICY)
    selector_rules = {
        "selector_target": "primitive_response_first",
        "allowed_primary_seed_fields": seeds["field_name"].tolist(),
        "allowed_primary_families": sorted(seeds["field_family"].dropna().astype(str).unique().tolist()),
        "allowed_label_focus": policy.get("allowed_label_focus", []),
        "allowed_horizon_focus": policy.get("allowed_horizon_focus", []),
        "required_pre_generation_filters": [
            "seed_field_must_have_A7AA1_primitive_response_candidate",
            "label_family_must_match_seed_evidence",
            "horizon_must_match_seed_evidence_or_be_adjacent_short_horizon",
            "wrong_lag_and_random_controls_attached",
            "no_May_in_selector_generation_mutation",
        ],
        "allowed_next_stage": "A7AB0_selector_rewrite_dryrun_contract_only",
        "not_authorized": [
            "formula_search_execution",
            "large_search",
            "alpha_proof",
            "shadow_paper_live",
        ],
    }
    blocked = pd.DataFrame({"field_name": policy.get("blocked_until_response_evidence", [])})
    decision = "PASS_A7AA3_SELECTOR_REWRITE_CONTRACT_READY_FOR_A7AB0"
    manifest = {
        "stage": "A7AA-3",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_contract_only": True,
        "executes_search": False,
        "executes_training": False,
        "authorizes_a7ab0_selector_rewrite_dryrun_contract": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "seed_field_count": int(len(seeds)),
        "blocked_field_count": int(len(blocked)),
        "uses_may": False,
    }
    seeds.to_csv(RUNTIME / "a7aa3_allowed_selector_seed_fields.csv", index=False)
    blocked.to_csv(RUNTIME / "a7aa3_blocked_primary_fields_until_response_evidence.csv", index=False)
    write_json(RUNTIME / "a7aa3_selector_rewrite_contract.json", selector_rules)
    write_json(RUNTIME / "a7aa3_manifest.json", manifest)
    write_json(
        RUNTIME / "a7aa3_authorization_matrix.json",
        {
            "A7AA-3": {"status": decision},
            "a7ab0_selector_rewrite_dryrun_contract": {"authorized": True},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AA-3 SELECTOR REWRITE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AA-3 rewrites the selector target from expression-family-first to primitive-response-first. It does not authorize formula search.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Selector Rules",
        "",
        "```json",
        json.dumps(selector_rules, indent=2, sort_keys=True),
        "```",
        "",
        "## Allowed Seed Fields",
        "",
        md_table(seeds),
        "",
        "## Blocked Primary Fields",
        "",
        md_table(blocked, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "A7AA-3 only authorizes A7AB0 contract/dryrun design.",
        "Formula search execution remains not authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
