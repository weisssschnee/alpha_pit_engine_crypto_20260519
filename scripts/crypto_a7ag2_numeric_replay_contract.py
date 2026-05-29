from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ag2_numeric_replay_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AG2_NUMERIC_REPLAY_CONTRACT_20260529.md"

A7AG1_MANIFEST = REPO / "runtime" / "a7ag1_static_blueprint_dryrun" / "a7ag1_manifest.json"
A7AG1_BLUEPRINTS = REPO / "runtime" / "a7ag1_static_blueprint_dryrun" / "a7ag1_static_ok_blueprints.csv"


TRACK_QUOTAS = {
    "G0_ordinary_alpha_basis_premium": 24,
    "G1_neutralized_alpha_diagnostic": 32,
    "G2_downside_risk_defense": 40,
}
FIELD_TOKEN_RE = re.compile(r"\b[a-z][a-z0-9_]*\b")
FUNCTION_TOKENS = {"Add", "Abs", "CSRank", "Delta", "Mul", "SafeDiv", "Sub", "TSRank", "Winsor", "ZScore"}
LOWER_FUNCTION_TOKENS = {x.lower() for x in FUNCTION_TOKENS}


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
    view = df.head(max_rows).copy().astype(str)
    for col in view.columns:
        view[col] = view[col].str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False, disable_numparse=True)


def expression_fields(expr: str) -> str:
    tokens = sorted({x for x in FIELD_TOKEN_RE.findall(str(expr)) if x not in LOWER_FUNCTION_TOKENS})
    return "|".join(tokens)


def choose_diverse(pool: pd.DataFrame, quota: int) -> pd.DataFrame:
    if pool.empty or quota <= 0:
        return pool.head(0).copy()
    rows: list[dict[str, Any]] = []
    skeleton_counts: dict[str, int] = {}
    production_counts: dict[str, int] = {}
    seed_counts: dict[str, int] = {}
    family_counts: dict[str, int] = {}
    ordered = pool.sort_values(["blueprint_family", "variant_name", "seed_field", "interaction_field", "blueprint_id"])
    for rec in ordered.to_dict("records"):
        sk = str(rec["skeleton_key"])
        pk = str(rec["production_key"])
        seed = str(rec["seed_field"])
        fam = str(rec["field_family"])
        if skeleton_counts.get(sk, 0) >= 2:
            continue
        if production_counts.get(pk, 0) >= 1:
            continue
        if seed_counts.get(seed, 0) >= 8:
            continue
        if family_counts.get(fam, 0) >= max(8, quota // 2):
            continue
        rows.append(rec)
        skeleton_counts[sk] = skeleton_counts.get(sk, 0) + 1
        production_counts[pk] = production_counts.get(pk, 0) + 1
        seed_counts[seed] = seed_counts.get(seed, 0) + 1
        family_counts[fam] = family_counts.get(fam, 0) + 1
        if len(rows) >= quota:
            break
    if len(rows) < quota:
        chosen = {r["blueprint_id"] for r in rows}
        for rec in ordered.to_dict("records"):
            if rec["blueprint_id"] in chosen:
                continue
            rows.append(rec)
            if len(rows) >= quota:
                break
    return pd.DataFrame(rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ag1 = read_json(A7AG1_MANIFEST)
    if not a7ag1.get("authorizes_a7ag2_numeric_replay_contract"):
        raise SystemExit("A7AG-1 does not authorize A7AG-2")
    blueprints = pd.read_csv(A7AG1_BLUEPRINTS)
    blueprints = blueprints[blueprints["static_ok"].astype(str).str.lower().isin(["true", "1"])].copy()
    selected_parts: list[pd.DataFrame] = []
    for track, quota in TRACK_QUOTAS.items():
        selected_parts.append(choose_diverse(blueprints[blueprints["track_id"].eq(track)].copy(), quota))
    queue = pd.concat(selected_parts, ignore_index=True) if selected_parts else pd.DataFrame()
    queue.insert(0, "replay_rank", range(1, len(queue) + 1))
    queue["candidate_id"] = queue["blueprint_id"]
    queue["source_fields"] = queue["expression"].map(expression_fields)
    queue["control_variants_required"] = "one_bar_lag|wrong_lag_future_24h|wrong_lag_stale_168h|same_family_random"
    queue["numeric_replay_authorized"] = False
    queue["formula_search_authorized"] = False
    queue["ordinary_alpha_eligible_track"] = queue["track_id"].eq("G0_ordinary_alpha_basis_premium")
    queue["risk_defense_track"] = queue["track_id"].eq("G2_downside_risk_defense")

    track_summary = (
        queue.groupby("track_id", dropna=False)
        .agg(
            selected=("candidate_id", "count"),
            unique_seed_fields=("seed_field", "nunique"),
            unique_skeletons=("skeleton_key", "nunique"),
            unique_production_keys=("production_key", "nunique"),
            unique_blueprint_families=("blueprint_family", "nunique"),
        )
        .reset_index()
    )
    label_summary = (
        queue.groupby(["track_id", "label_family", "label_horizon_h"], dropna=False)
        .agg(selected=("candidate_id", "count"))
        .reset_index()
    )
    replay_contract = {
        "max_candidates": int(len(queue)),
        "universe": "strict_symbols bounded replay subset inherited from A7AA/A7AE diagnostics",
        "labels": sorted(queue["label_family"].dropna().astype(str).unique().tolist()),
        "horizons": sorted([int(x) for x in queue["label_horizon_h"].dropna().unique().tolist()]),
        "required_controls": [
            "one_bar_lag",
            "wrong_lag_future_24h",
            "wrong_lag_stale_168h",
            "same_family_random",
        ],
        "required_splits": ["train_2024", "validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"],
        "pass_gate": {
            "G0_ordinary_alpha_basis_premium": ">=2 control-clean nonrank candidates across pre-May splits",
            "G1_neutralized_alpha_diagnostic": ">=3 control-clean beta/neutralized candidates; cannot promote ordinary alpha without L0/L1 translation",
            "G2_downside_risk_defense": ">=4 control-clean downside candidates; cannot promote ordinary alpha",
        },
        "not_authorized": [
            "numeric_replay_execution_without_A7AG3",
            "formula_search_execution",
            "large_search",
            "alpha_proof",
            "shadow_paper_live",
        ],
    }
    decision = (
        "PASS_A7AG2_NUMERIC_REPLAY_CONTRACT_READY_FOR_A7AG3_PILOT"
        if len(queue) >= 72 and queue["track_id"].nunique() == 3
        else "HOLD_A7AG2_REPLAY_QUEUE_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7AG-2",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ag1_decision": a7ag1.get("decision"),
        "executes_contract_only": True,
        "executes_numeric_replay": False,
        "executes_formula_search": False,
        "executes_training": False,
        "authorizes_a7ag3_numeric_replay_pilot": decision.startswith("PASS_"),
        "authorizes_numeric_replay_execution": False,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "queue_count": int(len(queue)),
        "track_count": int(queue["track_id"].nunique()) if not queue.empty else 0,
        "skeleton_count": int(queue["skeleton_key"].nunique()) if not queue.empty else 0,
        "production_key_count": int(queue["production_key"].nunique()) if not queue.empty else 0,
        "uses_may": False,
    }
    queue.to_csv(RUNTIME / "a7ag2_numeric_replay_queue.csv", index=False)
    track_summary.to_csv(RUNTIME / "a7ag2_track_summary.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ag2_label_summary.csv", index=False)
    write_json(RUNTIME / "a7ag2_replay_contract.json", replay_contract)
    write_json(RUNTIME / "a7ag2_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ag2_authorization_matrix.json",
        {
            "A7AG-2": {"status": decision},
            "a7ag3_numeric_replay_pilot": {"authorized": manifest["authorizes_a7ag3_numeric_replay_pilot"]},
            "numeric_replay_execution": {"authorized": False},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AG-2 NUMERIC REPLAY CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AG-2 selects a role-aware replay queue and defines the numeric replay pilot contract. It does not execute numeric replay, formula search, training, or proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Replay Contract",
        "",
        "```json",
        json.dumps(replay_contract, indent=2, sort_keys=True),
        "```",
        "",
        "## Track Summary",
        "",
        md_table(track_summary),
        "",
        "## Label Summary",
        "",
        md_table(label_summary, 120),
        "",
        "## Replay Queue",
        "",
        md_table(queue.head(120), 120),
        "",
        "## Boundary",
        "",
        "```text",
        "A7AG-2 is contract-only.",
        "A7AG-3 must be a separate pilot execution record.",
        "Formula search, large search, alpha proof, shadow, paper, and live remain not authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
