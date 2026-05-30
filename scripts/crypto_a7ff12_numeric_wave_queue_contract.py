from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff12_numeric_wave_queue_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF12_NUMERIC_WAVE_QUEUE_CONTRACT_20260530.md"

FULL_POOL = REPO / "runtime" / "a7ff7e_expanded_derivation_probe_contract" / "a7ff7e_expanded_blueprint_pool.csv"
OLD_QUEUE = REPO / "runtime" / "a7ff7e_expanded_derivation_probe_contract" / "a7ff7e_selected_numeric_probe_queue.csv"
A7FF11_PRIORITY = REPO / "runtime" / "a7ff11_selected_queue_triage" / "a7ff11_priority_followup_queue.csv"
A7FF11_MANIFEST = REPO / "runtime" / "a7ff11_selected_queue_triage" / "a7ff11_manifest.json"
A7FF11R_MANIFEST = REPO / "runtime" / "a7ff11_company_runner_contract" / "a7ff11r_manifest.json"

TARGET_QUEUE_SIZE = 720
MAX_PER_SEMANTIC = {
    "basis_premium_like|positioning_like": 240,
    "basis_premium_like|volatility_like": 192,
    "basis_premium_like|basis_premium_like": 192,
    "basis_premium_like|price_like": 144,
    "basis_premium_like": 0,
}
MAX_PER_MOTIF = 128
MAX_PER_SKELETON = 8


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
    safe = df.head(max_rows).copy()
    for col in safe.select_dtypes(include=["object"]).columns:
        safe[col] = safe[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return safe.to_markdown(index=False)
    except ImportError:
        return "```text\n" + safe.to_string(index=False) + "\n```"


def bool_series(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s.fillna(False)
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def quota_select(candidates: pd.DataFrame) -> pd.DataFrame:
    selected_rows: list[dict[str, Any]] = []
    used_blueprints: set[str] = set()
    used_skeleton: set[str] = set()
    semantic_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}

    # Round-robin across semantic/motif groups to avoid selecting a contiguous transform block.
    ordered = candidates.sort_values(
        [
            "a7ff12_priority_score",
            "numeric_probe_priority",
            "semantic_pair",
            "motif",
            "primary_transform",
            "secondary_transform",
            "blueprint_id",
        ],
        ascending=[False, True, True, True, True, True, True],
    )
    groups = [
        group.copy()
        for _, group in ordered.groupby(["semantic_pair", "motif"], sort=False)
        if not group.empty
    ]
    group_positions = [0 for _ in groups]
    progress = True
    while progress and len(selected_rows) < TARGET_QUEUE_SIZE:
        progress = False
        for gi, group in enumerate(groups):
            while group_positions[gi] < len(group):
                row = group.iloc[group_positions[gi]].to_dict()
                group_positions[gi] += 1
                bp = str(row["blueprint_id"])
                skel = str(row["skeleton_key"])
                sem = str(row["semantic_pair"])
                motif = str(row["motif"])
                if bp in used_blueprints:
                    continue
                if MAX_PER_SKELETON and sum(1 for x in selected_rows if str(x.get("skeleton_key", "")) == skel) >= MAX_PER_SKELETON:
                    continue
                if semantic_counts.get(sem, 0) >= MAX_PER_SEMANTIC.get(sem, 0):
                    continue
                if motif_counts.get(motif, 0) >= MAX_PER_MOTIF:
                    continue
                selected_rows.append(row)
                used_blueprints.add(bp)
                used_skeleton.add(skel)
                semantic_counts[sem] = semantic_counts.get(sem, 0) + 1
                motif_counts[motif] = motif_counts.get(motif, 0) + 1
                progress = True
                break
            if len(selected_rows) >= TARGET_QUEUE_SIZE:
                break
    return pd.DataFrame(selected_rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    full = pd.read_csv(FULL_POOL)
    old = pd.read_csv(OLD_QUEUE)
    priority = pd.read_csv(A7FF11_PRIORITY) if A7FF11_PRIORITY.exists() else pd.DataFrame()
    a7ff11 = read_json(A7FF11_MANIFEST)
    a7ff11r = read_json(A7FF11R_MANIFEST)

    old_ids = set(old["blueprint_id"].astype(str))
    priority_semantics = set(priority.get("semantic_pair", pd.Series(dtype=str)).astype(str))
    priority_motifs = set(priority.get("motif", pd.Series(dtype=str)).astype(str))
    priority_primary_transforms = set(priority.get("expression", pd.Series(dtype=str)).astype(str))

    full["selected_for_a7ff8_numeric_probe"] = bool_series(full["selected_for_a7ff8_numeric_probe"])
    candidates = full[~full["blueprint_id"].astype(str).isin(old_ids)].copy()
    candidates = candidates[candidates["semantic_pair"].isin([k for k, v in MAX_PER_SEMANTIC.items() if v > 0])].copy()
    candidates["a7ff12_priority_score"] = 0.0
    candidates.loc[candidates["semantic_pair"].isin(priority_semantics), "a7ff12_priority_score"] += 2.0
    candidates.loc[candidates["motif"].isin(priority_motifs), "a7ff12_priority_score"] += 1.0
    candidates.loc[candidates["primary_transform"].isin(["delta_1h", "delta_4h", "delta_12h", "delta_24h", "zscore", "csrank", "winsor_zscore"]), "a7ff12_priority_score"] += 0.5
    candidates.loc[candidates["secondary_transform"].isin(["delta_1h", "delta_4h", "delta_12h", "delta_24h", "zscore", "csrank", "tsrank_24h", "winsor_zscore"]), "a7ff12_priority_score"] += 0.5
    candidates.loc[candidates["numeric_probe_priority"].eq("P0"), "a7ff12_priority_score"] += 0.25
    # Slightly diversify away from exact strings already seen in the priority queue.
    candidates.loc[candidates["expression"].astype(str).isin(priority_primary_transforms), "a7ff12_priority_score"] -= 5.0

    selected = quota_select(candidates)
    selected["selected_for_a7ff12_numeric_wave"] = True

    semantic_summary = (
        selected.groupby("semantic_pair", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    motif_summary = (
        selected.groupby("motif", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    transform_summary = (
        selected.groupby(["primary_transform", "secondary_transform"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    candidate_coverage = pd.DataFrame(
        [
            {"bucket": "full_pool", "count": len(full)},
            {"bucket": "old_a7ff7e_selected_queue", "count": len(old)},
            {"bucket": "unselected_candidate_pool", "count": len(candidates)},
            {"bucket": "a7ff12_selected_queue", "count": len(selected)},
        ]
    )

    decision = (
        "PASS_A7FF12_NUMERIC_WAVE_QUEUE_READY_FOR_COMPANY_EXECUTION"
        if len(selected) >= TARGET_QUEUE_SIZE
        else "HOLD_A7FF12_NUMERIC_WAVE_QUEUE_UNDERFILLED"
    )
    manifest = {
        "stage": "A7FF-12-NUMERIC-WAVE-QUEUE-CONTRACT",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ff11_decision": a7ff11.get("decision", ""),
        "source_a7ff11r_decision": a7ff11r.get("decision", ""),
        "target_queue_size": TARGET_QUEUE_SIZE,
        "selected_queue_size": int(len(selected)),
        "full_pool_rows": int(len(full)),
        "old_queue_rows": int(len(old)),
        "candidate_pool_rows": int(len(candidates)),
        "semantic_pair_count": int(selected["semantic_pair"].nunique()) if not selected.empty else 0,
        "motif_count": int(selected["motif"].nunique()) if not selected.empty else 0,
        "skeleton_count": int(selected["skeleton_key"].nunique()) if not selected.empty else 0,
        "max_per_semantic": MAX_PER_SEMANTIC,
        "max_per_motif": MAX_PER_MOTIF,
        "max_per_skeleton": MAX_PER_SKELETON,
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_company_numeric_probe": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    selected.to_csv(RUNTIME / "a7ff12_numeric_wave_queue.csv", index=False)
    candidates.to_csv(RUNTIME / "a7ff12_candidate_pool_after_exclusions.csv", index=False)
    semantic_summary.to_csv(RUNTIME / "a7ff12_semantic_quota_summary.csv", index=False)
    motif_summary.to_csv(RUNTIME / "a7ff12_motif_quota_summary.csv", index=False)
    transform_summary.to_csv(RUNTIME / "a7ff12_transform_summary.csv", index=False)
    candidate_coverage.to_csv(RUNTIME / "a7ff12_candidate_coverage.csv", index=False)
    write_json(RUNTIME / "a7ff12_manifest.json", manifest)

    lines = [
        "# CRYPTO A7FF-12 NUMERIC WAVE QUEUE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-12 builds a broader numeric-probe queue from the full A7FF-7E blueprint pool. It excludes the already-covered 384 queue and does not run generation, replay, search, alpha proof, shadow, paper, or live execution.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Candidate Coverage",
        "",
        md_table(candidate_coverage),
        "",
        "## Semantic Quotas",
        "",
        md_table(semantic_summary),
        "",
        "## Motif Quotas",
        "",
        md_table(motif_summary),
        "",
        "## Transform Summary",
        "",
        md_table(transform_summary, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "This is a queue contract only.",
        "No May is used.",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "A7FF-12 numeric execution must use company-machine preflight and manifest polling from A7FF-11R.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
