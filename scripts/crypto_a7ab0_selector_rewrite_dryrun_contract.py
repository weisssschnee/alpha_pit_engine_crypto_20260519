from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ab0_selector_rewrite_dryrun_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AB0_SELECTOR_REWRITE_DRYRUN_CONTRACT_20260529.md"
A7AA3_MANIFEST = REPO / "runtime" / "a7aa3_selector_rewrite_contract" / "a7aa3_manifest.json"
A7AA3_CONTRACT = REPO / "runtime" / "a7aa3_selector_rewrite_contract" / "a7aa3_selector_rewrite_contract.json"
A7AA3_SEEDS = REPO / "runtime" / "a7aa3_selector_rewrite_contract" / "a7aa3_allowed_selector_seed_fields.csv"


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

    a7aa3 = read_json(A7AA3_MANIFEST)
    if not a7aa3.get("authorizes_a7ab0_selector_rewrite_dryrun_contract"):
        raise SystemExit("A7AA-3 does not authorize A7AB-0")
    contract = read_json(A7AA3_CONTRACT)
    seeds = pd.read_csv(A7AA3_SEEDS)
    selector_features = pd.DataFrame(
        [
            {"feature": "premay_split_consistency", "source": "A7AA1 primitive response map", "weight": 0.30},
            {"feature": "control_margin", "source": "1 - max wrong-lag/stale/random control ratio", "weight": 0.25},
            {"feature": "one_bar_lag_survival", "source": "A7AA1 one_bar_lag_recent_oriented", "weight": 0.20},
            {"feature": "nonoverlap_robust_tstat", "source": "minimum oriented pre-May non-overlap statistic", "weight": 0.15},
            {"feature": "seed_family_diversity", "source": "field family cap", "weight": 0.10},
        ]
    )
    hard_gates = pd.DataFrame(
        [
            {"gate": "primary_field_must_be_a7aa2_seed", "rule": "field in A7AA2 predictive_signal_candidate set"},
            {"gate": "control_ratio_lt_1", "rule": "control_ratio_premay_max < 1.0"},
            {"gate": "premay_all_positive", "rule": "validation/test/recent all oriented positive"},
            {"gate": "lag_ok", "rule": "one_bar_lag_recent_oriented positive and >= 25pct of recent"},
            {"gate": "label_and_horizon_focus", "rule": "label/horizon must be supported by A7AA1 evidence"},
            {"gate": "no_may", "rule": "May not used in selector score, generation, mutation, or threshold"},
        ]
    )
    decision = "PASS_A7AB0_SELECTOR_REWRITE_DRYRUN_CONTRACT_READY_FOR_A7AB1"
    manifest = {
        "stage": "A7AB-0",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_contract_only": True,
        "executes_selector_dryrun": False,
        "executes_formula_generation": False,
        "executes_search": False,
        "executes_training": False,
        "authorizes_a7ab1_selector_rewrite_dryrun": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "seed_field_count": int(len(seeds)),
        "allowed_primary_seed_fields": contract.get("allowed_primary_seed_fields", []),
        "allowed_label_focus": contract.get("allowed_label_focus", []),
        "allowed_horizon_focus": contract.get("allowed_horizon_focus", []),
        "uses_may": False,
    }
    seeds.to_csv(RUNTIME / "a7ab0_allowed_seed_fields.csv", index=False)
    selector_features.to_csv(RUNTIME / "a7ab0_selector_score_features.csv", index=False)
    hard_gates.to_csv(RUNTIME / "a7ab0_selector_hard_gates.csv", index=False)
    write_json(RUNTIME / "a7ab0_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ab0_authorization_matrix.json",
        {
            "A7AB-0": {"status": decision},
            "a7ab1_selector_rewrite_dryrun": {"authorized": True},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AB-0 SELECTOR REWRITE DRYRUN CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AB-0 defines the selector rewrite dryrun. It does not generate formulas or run search.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Selector Score Features",
        "",
        md_table(selector_features),
        "",
        "## Hard Gates",
        "",
        md_table(hard_gates),
        "",
        "## Allowed Seed Fields",
        "",
        md_table(seeds),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
