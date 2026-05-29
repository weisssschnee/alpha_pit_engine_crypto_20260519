from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ag1_static_blueprint_dryrun"
REPORT = REPO / "reports" / "CRYPTO_A7AG1_STATIC_BLUEPRINT_DRYRUN_20260529.md"

A7AG0_MANIFEST = REPO / "runtime" / "a7ag0_role_aware_generation_contract" / "a7ag0_manifest.json"
A7AG0_TRACKS = REPO / "runtime" / "a7ag0_role_aware_generation_contract" / "a7ag0_generation_tracks.csv"
A7AG0_RULES = REPO / "runtime" / "a7ag0_role_aware_generation_contract" / "a7ag0_generation_rules.csv"
A7AG0_QUEUE = REPO / "runtime" / "a7ag0_role_aware_generation_contract" / "a7ag0_source_selected_queue.csv"


TRACK_BY_TIER = {
    "T0_raw_relative_alpha": "G0_ordinary_alpha_basis_premium",
    "T1_beta_neutral_alpha_diagnostic": "G1_neutralized_alpha_diagnostic",
    "T2_downside_risk_defense": "G2_downside_risk_defense",
}

INTERACTION_FIELDS = {
    "G0_ordinary_alpha_basis_premium": [
        "realized_vol_24h",
        "realized_vol_168h",
        "liquidity_rank_active_universe",
        "trade_count",
    ],
    "G1_neutralized_alpha_diagnostic": [
        "liquidity_rank_active_universe",
        "premium_close_bps",
        "realized_vol_168h",
        "trade_return_1h",
    ],
    "G2_downside_risk_defense": [
        "realized_vol_24h",
        "open_interest_last",
        "oi_x_price_move_24h",
        "global_long_short_account_ratio_last",
        "top_long_short_account_ratio_last",
        "trade_count",
    ],
}


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


def key(text: str, n: int = 16) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:n]


def base_expr(field: str, transform: str) -> str:
    if transform == "delta_24h":
        return f"Delta({field},24)"
    if transform == "cs_rank":
        return f"CSRank({field})"
    if transform == "level":
        return field
    return f"{transform}({field})"


def transform_variants(expr: str) -> list[tuple[str, str]]:
    return [
        ("rank", f"CSRank({expr})"),
        ("zscore_168h", f"ZScore({expr},168)"),
        ("tsrank_168h", f"TSRank({expr},168)"),
        ("winsor_rank", f"Winsor(CSRank({expr}),0.01,0.99)"),
    ]


def interaction_variants(left: str, right_field: str) -> list[tuple[str, str]]:
    right_rank = f"CSRank({right_field})"
    right_delta = f"Delta({right_field},24)"
    return [
        ("mul_rank", f"Mul({left},{right_rank})"),
        ("sub_rank", f"Sub({left},{right_rank})"),
        ("div_rank", f"SafeDiv({left},Add(Abs({right_rank}),0.01))"),
        ("mul_delta", f"Mul({left},ZScore({right_delta},168))"),
    ]


def skeleton(expr: str) -> str:
    out = []
    token = ""
    for ch in expr:
        if ch.isalpha() or ch == "_":
            token += ch
        else:
            if token:
                out.append("FIELD" if token[0].islower() else token)
                token = ""
            if ch in "(),":
                out.append(ch)
    if token:
        out.append("FIELD" if token[0].islower() else token)
    return "".join(out)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ag0 = read_json(A7AG0_MANIFEST)
    if not a7ag0.get("authorizes_a7ag1_static_blueprint_dryrun"):
        raise SystemExit("A7AG-0 does not authorize A7AG-1")
    tracks = pd.read_csv(A7AG0_TRACKS)
    rules = pd.read_csv(A7AG0_RULES)
    queue = pd.read_csv(A7AG0_QUEUE)
    forbidden_by_track = {
        row["track_id"]: {part.strip() for part in str(row["forbidden"]).split("|") if part.strip()}
        for _, row in tracks.iterrows()
    }
    labels_by_track = {
        row["track_id"]: {part.strip() for part in str(row["allowed_labels"]).split("|") if part.strip()}
        for _, row in tracks.iterrows()
    }
    caps_by_track = {
        row["track_id"]: int(row["max_static_blueprints"])
        for _, row in tracks.iterrows()
    }

    rows: list[dict[str, Any]] = []
    per_track_count: dict[str, int] = {}
    for _, seed in queue.iterrows():
        tier = str(seed["selector_tier"])
        track = TRACK_BY_TIER.get(tier)
        if not track:
            continue
        if per_track_count.get(track, 0) >= caps_by_track.get(track, 0):
            continue
        seed_field = str(seed["field_name"])
        seed_expr = base_expr(seed_field, str(seed["transform"]))
        label = str(seed["label_family"])
        if label not in labels_by_track.get(track, set()):
            continue
        candidate_exprs: list[tuple[str, str, str, str]] = []
        for name, expr in transform_variants(seed_expr):
            candidate_exprs.append((name, "", expr, "single_seed_transform"))
        for other in INTERACTION_FIELDS.get(track, []):
            if other == seed_field:
                continue
            for name, expr in interaction_variants(seed_expr, other):
                candidate_exprs.append((name, other, expr, "seed_interaction"))
        for variant_name, interaction_field, expr, blueprint_family in candidate_exprs:
            if per_track_count.get(track, 0) >= caps_by_track.get(track, 0):
                break
            blocked = [term for term in forbidden_by_track.get(track, set()) if term in expr]
            May_used = "May" in expr or "2026May" in expr
            static_ok = not blocked and not May_used
            production_key = key(f"{track}|{blueprint_family}|{variant_name}|{seed_field}|{interaction_field}", 12)
            skel = skeleton(expr)
            blueprint_id = f"a7ag1_{key(track + '|' + expr + '|' + label, 18)}"
            rows.append(
                {
                    "blueprint_id": blueprint_id,
                    "source_candidate_id": seed["candidate_id"],
                    "track_id": track,
                    "selector_tier": tier,
                    "blueprint_family": blueprint_family,
                    "variant_name": variant_name,
                    "seed_field": seed_field,
                    "interaction_field": interaction_field,
                    "field_family": seed.get("field_family", ""),
                    "feature_role": seed.get("feature_role", ""),
                    "label_family": label,
                    "label_horizon_h": int(seed["label_horizon_h"]),
                    "expression": expr,
                    "skeleton": skel,
                    "skeleton_key": key(skel, 12),
                    "production_key": production_key,
                    "static_ok": static_ok,
                    "blocked_terms": "|".join(blocked),
                    "uses_may": May_used,
                    "authorizes_numeric_replay": False,
                    "authorizes_formula_search": False,
                }
            )
            per_track_count[track] = per_track_count.get(track, 0) + 1

    blueprints = pd.DataFrame(rows)
    if blueprints.empty:
        blueprints = pd.DataFrame(
            columns=[
                "blueprint_id",
                "source_candidate_id",
                "track_id",
                "selector_tier",
                "blueprint_family",
                "variant_name",
                "seed_field",
                "interaction_field",
                "field_family",
                "feature_role",
                "label_family",
                "label_horizon_h",
                "expression",
                "skeleton",
                "skeleton_key",
                "production_key",
                "static_ok",
                "blocked_terms",
                "uses_may",
                "authorizes_numeric_replay",
                "authorizes_formula_search",
            ]
        )
    ok = blueprints[blueprints["static_ok"].astype(bool)].copy()
    track_summary = (
        blueprints.groupby("track_id", dropna=False)
        .agg(
            blueprints=("blueprint_id", "count"),
            static_ok=("static_ok", "sum"),
            unique_seed_fields=("seed_field", "nunique"),
            unique_skeletons=("skeleton_key", "nunique"),
            unique_production_keys=("production_key", "nunique"),
        )
        .reset_index()
    )
    skeleton_summary = (
        ok.groupby(["track_id", "skeleton_key"], dropna=False)
        .agg(count=("blueprint_id", "count"))
        .reset_index()
        .sort_values(["track_id", "count"], ascending=[True, False])
    )
    decision = (
        "PASS_A7AG1_STATIC_BLUEPRINT_DRYRUN_READY_FOR_A7AG2_NUMERIC_REPLAY_CONTRACT"
        if len(ok) >= 64 and ok["track_id"].nunique() == 3 and ok["skeleton_key"].nunique() >= 12
        else "HOLD_A7AG1_STATIC_BLUEPRINT_DIVERSITY_WEAK"
    )
    manifest = {
        "stage": "A7AG-1",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ag0_decision": a7ag0.get("decision"),
        "executes_static_blueprint_generation": True,
        "executes_numeric_replay": False,
        "executes_formula_search": False,
        "executes_training": False,
        "authorizes_a7ag2_numeric_replay_contract": decision.startswith("PASS_"),
        "authorizes_numeric_replay_execution": False,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blueprint_count": int(len(blueprints)),
        "static_ok_count": int(len(ok)),
        "track_count": int(ok["track_id"].nunique()) if not ok.empty else 0,
        "skeleton_count": int(ok["skeleton_key"].nunique()) if not ok.empty else 0,
        "production_key_count": int(ok["production_key"].nunique()) if not ok.empty else 0,
        "uses_may_count": int(blueprints["uses_may"].sum()) if not blueprints.empty else 0,
    }
    blueprints.to_csv(RUNTIME / "a7ag1_static_blueprint_registry.csv", index=False)
    ok.to_csv(RUNTIME / "a7ag1_static_ok_blueprints.csv", index=False)
    track_summary.to_csv(RUNTIME / "a7ag1_track_summary.csv", index=False)
    skeleton_summary.to_csv(RUNTIME / "a7ag1_skeleton_summary.csv", index=False)
    rules.to_csv(RUNTIME / "a7ag1_inherited_generation_rules.csv", index=False)
    write_json(RUNTIME / "a7ag1_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ag1_authorization_matrix.json",
        {
            "A7AG-1": {"status": decision},
            "a7ag2_numeric_replay_contract": {"authorized": manifest["authorizes_a7ag2_numeric_replay_contract"]},
            "numeric_replay_execution": {"authorized": False},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AG-1 STATIC BLUEPRINT DRYRUN",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AG-1 generates static role-aware blueprints only. It does not run numeric replay, formula search execution, training, or proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Track Summary",
        "",
        md_table(track_summary, 80),
        "",
        "## Skeleton Summary",
        "",
        md_table(skeleton_summary, 120),
        "",
        "## Static OK Blueprints",
        "",
        md_table(ok.head(120), 120),
        "",
        "## Boundary",
        "",
        "```text",
        "A7AG-1 is static blueprint generation only.",
        "Numeric replay and formula search execution remain not authorized.",
        "May is not used.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
