from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7pm2_candidate_lifecycle"
REPORT = REPO / "reports" / "CRYPTO_A7PM2_CANDIDATE_LIFECYCLE_STATE_MACHINE_20260529.md"
A7PM1 = REPO / "runtime" / "a7pm1_asset_taxonomy" / "a7pm1_manifest.json"

STATES = [
    "generated",
    "materialized",
    "fast_replayed",
    "control_clean",
    "neutralization_clean",
    "latency_clean",
    "overlap_robust",
    "cluster_registered",
    "deep_audited",
    "diagnostic_clue",
    "research_candidate",
    "rejected",
    "superseded",
    "paper_candidate",
    "shadow_candidate",
    "live_candidate",
]

ALLOWED = [
    ("generated", "materialized", "static and field-contract valid"),
    ("materialized", "fast_replayed", "evaluator parity and PIT contract pass"),
    ("fast_replayed", "control_clean", "negative controls weaker"),
    ("control_clean", "neutralization_clean", "latent/liquidity/meme/beta neutral survival"),
    ("neutralization_clean", "latency_clean", "field-native latency pass"),
    ("latency_clean", "overlap_robust", "non-overlap or robust tstat pass"),
    ("overlap_robust", "cluster_registered", "signal-vector and formula cluster registered"),
    ("cluster_registered", "deep_audited", "deep audit selected under caps"),
    ("deep_audited", "diagnostic_clue", "diagnostic-only evidence"),
    ("deep_audited", "research_candidate", "all promotion gates pass"),
    ("diagnostic_clue", "generated", "only as weak prior for a new contract"),
    ("research_candidate", "paper_candidate", "explicit future authorization only"),
    ("paper_candidate", "shadow_candidate", "explicit future authorization only"),
    ("shadow_candidate", "live_candidate", "explicit future authorization only"),
    ("generated", "rejected", "static or role fail"),
    ("materialized", "rejected", "eval fail or low activity"),
    ("fast_replayed", "rejected", "control/latency/label fail"),
    ("diagnostic_clue", "superseded", "newer arbitration or failed translation"),
    ("research_candidate", "superseded", "newer arbitration or failed forward test"),
]

FORBIDDEN = [
    ("diagnostic_clue", "shadow_candidate", "diagnostic cannot skip research/paper gates"),
    ("diagnostic_clue", "live_candidate", "diagnostic cannot skip research/paper/shadow gates"),
    ("generated", "research_candidate", "must materialize/replay/audit first"),
    ("control_clean", "research_candidate", "must pass neutralization/latency/cluster/deep audit"),
    ("superseded", "generated", "superseded artifacts cannot be selector source-of-truth"),
    ("rejected", "research_candidate", "rejected candidates require fresh generation and full gate path"),
    ("deep_audited", "shadow_candidate", "deep audit is not trading authorization"),
    ("research_candidate", "live_candidate", "must pass paper/shadow gates"),
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    pm1 = read_json(A7PM1)
    if not pm1.get("authorizes_a7pm2"):
        raise SystemExit("A7PM-1 does not authorize A7PM-2")

    allowed_df = pd.DataFrame(ALLOWED, columns=["from_state", "to_state", "condition"])
    forbidden_df = pd.DataFrame(FORBIDDEN, columns=["from_state", "to_state", "reason"])
    labels = pd.DataFrame(
        [
            {"state": state, "definition": definition}
            for state, definition in {
                "generated": "formula/expression exists but has no evidence",
                "materialized": "expression evaluated into numeric signal",
                "fast_replayed": "candidate passed fast replay diagnostic",
                "control_clean": "matched controls are weaker",
                "neutralization_clean": "survives required neutralization",
                "latency_clean": "field-native timing and wrong-lag checks pass",
                "overlap_robust": "overlap-robust/non-overlap statistics pass",
                "cluster_registered": "signal-vector/formula cluster recorded",
                "deep_audited": "deep audit completed",
                "diagnostic_clue": "diagnostic evidence only; no promotion",
                "research_candidate": "research-stage candidate after all non-trading gates",
                "rejected": "blocked by any hard gate",
                "superseded": "replaced by newer source-of-truth arbitration",
                "paper_candidate": "future paper authorization only",
                "shadow_candidate": "future shadow authorization only",
                "live_candidate": "future live authorization only",
            }.items()
        ]
    )
    promotion = pd.DataFrame(
        [
            {"gate": "field_role_enforcement", "required_for": "materialized", "hard_fail_state": "rejected"},
            {"gate": "control_dominance", "required_for": "control_clean", "hard_fail_state": "rejected"},
            {"gate": "neutralization", "required_for": "neutralization_clean", "hard_fail_state": "diagnostic_clue_or_rejected"},
            {"gate": "latency_wrong_lag", "required_for": "latency_clean", "hard_fail_state": "rejected"},
            {"gate": "overlap_robust_stats", "required_for": "overlap_robust", "hard_fail_state": "diagnostic_clue_or_rejected"},
            {"gate": "cluster_diversity", "required_for": "cluster_registered", "hard_fail_state": "diagnostic_clue"},
            {"gate": "deep_audit", "required_for": "research_candidate", "hard_fail_state": "diagnostic_clue_or_rejected"},
            {"gate": "explicit_authorization", "required_for": "paper/shadow/live", "hard_fail_state": "not_authorized"},
        ]
    )
    machine = {"states": STATES, "allowed_transitions": [dict(zip(["from", "to", "condition"], row)) for row in ALLOWED]}
    manifest = {
        "stage": "A7PM-2",
        "generated_at": now_utc(),
        "decision": "PASS_A7PM2_CANDIDATE_LIFECYCLE_STATE_MACHINE_BUILT",
        "state_count": len(STATES),
        "allowed_transition_count": len(ALLOWED),
        "forbidden_transition_count": len(FORBIDDEN),
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_a7pm3": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7pm2_candidate_state_machine.json", machine)
    allowed_df.to_csv(RUNTIME / "a7pm2_allowed_transitions.csv", index=False)
    forbidden_df.to_csv(RUNTIME / "a7pm2_forbidden_transitions.csv", index=False)
    labels.to_csv(RUNTIME / "a7pm2_label_dictionary.csv", index=False)
    promotion.to_csv(RUNTIME / "a7pm2_promotion_gate_matrix.csv", index=False)
    write_json(RUNTIME / "a7pm2_manifest.json", manifest)
    lines = [
        "# CRYPTO A7PM-2 CANDIDATE LIFECYCLE STATE MACHINE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "## State Dictionary",
        "",
        md_table(labels),
        "",
        "## Forbidden Transitions",
        "",
        md_table(forbidden_df),
        "",
        "## Promotion Gates",
        "",
        md_table(promotion),
        "",
        "## Boundary",
        "",
        "```text",
        "diagnostic_clue cannot directly become shadow/live.",
        "control dominated candidates cannot become research_candidate.",
        "stress-vetoed or superseded artifacts cannot seed expansion unless a new contract explicitly reclassifies them.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
