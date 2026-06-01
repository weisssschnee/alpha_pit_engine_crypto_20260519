from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore11e_small_dry_generation"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE11E_SMALL_DRY_GENERATION_20260601.md"
A7FFCORE11 = REPO / "runtime" / "a7ffcore11_small_expansion_contract" / "a7ffcore11_manifest.json"
SEEDS = REPO / "runtime" / "a7ffcore11_small_expansion_contract" / "a7ffcore11_seed_pool.csv"
FAMILY_BUDGET = REPO / "runtime" / "a7ffcore11_small_expansion_contract" / "a7ffcore11_family_budget.csv"

WINDOWS = [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 72, 96, 168, 240, 336]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def stable_id(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:18]


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def split_fields(raw_inputs: str) -> list[str]:
    return [x for x in str(raw_inputs).split(";") if x]


def candidate_exprs(seed_expr: str, fields: list[str], budget: int) -> list[tuple[str, str]]:
    exprs: list[tuple[str, str]] = []
    for field in fields:
        for w1 in WINDOWS[:12]:
            for w2 in WINDOWS[:12]:
                exprs.extend(
                    [
                        (f"Mul(ZScore(Mean({seed_expr},{w1})),Delta({field},{w2}))", "seed_field_mul_delta"),
                        (f"SafeDiv(Delta({seed_expr},{w1}),Abs(Delta({field},{w2})))", "seed_field_safe_div"),
                        (f"Sub(TSRank({seed_expr},{w1}),TSRank({field},{w2}))", "seed_field_rank_spread"),
                        (f"Add(ZScore(Mean({seed_expr},{w1})),ZScore(Mean({field},{w2})))", "seed_field_z_add"),
                        (f"Sub(ZScore(Mean({seed_expr},{w1})),ZScore(Mean({field},{w2})))", "seed_field_z_spread"),
                    ]
                )
    for w1 in WINDOWS[:12]:
        for w2 in WINDOWS[:12]:
            if w1 == w2:
                continue
            exprs.extend(
                [
                    (f"Sub(Mean({seed_expr},{w1}),Mean({seed_expr},{w2}))", "seed_term_spread"),
                    (f"SafeDiv(Delta({seed_expr},{w1}),Abs(Mean({seed_expr},{w2})))", "seed_self_safe_div"),
                ]
            )
    for field in fields:
        for w in WINDOWS:
            exprs.extend(
                [
                    (f"Mean({field},{w})", "single_mean"),
                    (f"Delta({field},{w})", "single_delta"),
                    (f"ZScore(Mean({field},{w}))", "single_zmean"),
                    (f"TSRank({field},{w})", "single_tsrank"),
                    (f"Rank({field})", "single_rank"),
                    (f"CSRank({field})", "single_csrank"),
                    (f"Abs(ZScore(Mean({field},{w})))", "single_abs_zmean"),
                    (f"Clip(ZScore(Delta({field},{w})),-5,5)", "single_clipped_delta"),
                    (f"Decay({field},{w})", "single_decay"),
                    (f"ZScore(Delta({field},{w}))", "single_zdelta"),
                ]
            )
        for w1 in WINDOWS[:10]:
            for w2 in WINDOWS[:10]:
                if w1 == w2:
                    continue
                exprs.extend(
                    [
                        (f"Mean(Delta({field},{w1}),{w2})", "single_delta_smooth"),
                        (f"Delta(Mean({field},{w1}),{w2})", "single_smooth_delta"),
                        (f"Sub(Mean({field},{w1}),Mean({field},{w2}))", "single_term_spread"),
                    ]
                )
    for a in fields:
        for b in fields:
            if a == b:
                continue
            for w1 in WINDOWS[:12]:
                for w2 in WINDOWS[:12]:
                    exprs.extend(
                        [
                            (f"Mul(ZScore(Mean({a},{w1})),Delta({b},{w2}))", "typed_mul_delta"),
                            (f"SafeDiv(Delta({a},{w1}),Abs(Delta({b},{w2})))", "typed_safe_div_delta"),
                            (f"Sub(TSRank({a},{w1}),TSRank({b},{w2}))", "typed_rank_spread"),
                            (f"Add(ZScore(Mean({a},{w1})),ZScore(Mean({b},{w2})))", "typed_z_add"),
                            (f"Sub(ZScore(Mean({a},{w1})),ZScore(Mean({b},{w2})))", "typed_z_spread"),
                            (f"Mul(Sign(Delta({a},{w1})),Abs(ZScore(Delta({b},{w2}))))", "typed_signed_abs"),
                        ]
                    )
    for w in WINDOWS:
        exprs.extend(
            [
                (f"Mean({seed_expr},{w})", "seed_smooth"),
                (f"Delta({seed_expr},{w})", "seed_delta"),
                (f"ZScore(Mean({seed_expr},{w}))", "seed_zmean"),
                (f"TSRank({seed_expr},{w})", "seed_tsrank"),
                (f"Decay({seed_expr},{w})", "seed_decay"),
                (f"Clip({seed_expr},-5,5)", "seed_clip"),
            ]
        )
    seen = set()
    out: list[tuple[str, str]] = []
    for expr, mode in exprs:
        key = expr.replace(" ", "")
        if key in seen:
            continue
        seen.add(key)
        out.append((expr, mode))
        if len(out) >= budget:
            break
    return out


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core11 = read_json(A7FFCORE11)
    if core11.get("decision") != "PASS_A7FFCORE11_SMALL_EXPANSION_CONTRACT_READY_FOR_CORE11E":
        raise SystemExit(f"A7FF-CORE11 is not ready: {core11.get('decision')}")
    seeds = pd.read_csv(SEEDS)
    family_budget = pd.read_csv(FAMILY_BUDGET)
    rows: list[dict[str, Any]] = []
    for fam in family_budget.to_dict("records"):
        semantic = fam["semantic_bucket"]
        motif = fam["motif_bucket"]
        budget = int(fam["generated_budget"])
        fam_seeds = seeds[(seeds["semantic_bucket"].eq(semantic)) & (seeds["motif_bucket"].eq(motif))]
        if fam_seeds.empty:
            continue
        per_seed = max(1, budget // len(fam_seeds))
        for seed in fam_seeds.to_dict("records"):
            fields = split_fields(seed.get("raw_inputs", ""))
            for expr, mode in candidate_exprs(str(seed["expression"]), fields, per_seed):
                cid = "a7ffcore11e_" + stable_id(f"{seed['candidate_id']}|{expr}|{mode}")
                rows.append(
                    {
                        "candidate_id": cid,
                        "parent_candidate_id": seed["candidate_id"],
                        "semantic_bucket": semantic,
                        "motif_bucket": motif,
                        "generation_mode": mode,
                        "expression": expr,
                        "raw_inputs": ";".join(fields),
                        "source_max_tstat": seed.get("max_tstat"),
                        "source_replay_min_control_ratio": seed.get("replay_min_control_ratio"),
                        "core_gate_status": "requires_core2_registration",
                        "authorizes_materialization": False,
                        "authorizes_numeric": False,
                        "authorizes_replay": False,
                        "authorizes_search": False,
                    }
                )
    pool = pd.DataFrame(rows).drop_duplicates(subset=["expression"]).reset_index(drop=True)
    pool = pool.head(4000).copy()
    family_summary = (
        pool.groupby(["semantic_bucket", "motif_bucket", "generation_mode"], dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"))
        .reset_index()
        .sort_values("candidate_count", ascending=False)
    )
    parent_summary = (
        pool.groupby("parent_candidate_id", dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), semantic_bucket=("semantic_bucket", "first"), motif_bucket=("motif_bucket", "first"))
        .reset_index()
        .sort_values("candidate_count", ascending=False)
    )
    pool.to_csv(RUNTIME / "a7ffcore11e_blueprint_pool.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore11e_family_generation_summary.csv", index=False)
    parent_summary.to_csv(RUNTIME / "a7ffcore11e_parent_generation_summary.csv", index=False)
    risk_flags = []
    if len(pool) < 3000:
        risk_flags.append("blueprint_count_below_3000")
    if int(pool["semantic_bucket"].nunique()) < 8:
        risk_flags.append("semantic_breadth_below_seed_pool")
    if int(pool["motif_bucket"].nunique()) < 6:
        risk_flags.append("motif_breadth_below_seed_pool")
    if pool["core_gate_status"].ne("requires_core2_registration").any():
        risk_flags.append("unexpected_gate_status")
    pd.DataFrame([{"risk_flag": r} for r in risk_flags]).to_csv(RUNTIME / "a7ffcore11e_risk_flags.csv", index=False)
    decision = "PASS_A7FFCORE11E_BLUEPRINTS_READY_FOR_CORE12_REGISTRATION" if not risk_flags else "HOLD_A7FFCORE11E_BLUEPRINT_GENERATION_WEAK"
    manifest = {
        "stage": "A7FF-CORE11E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE11",
        "source_decision": core11.get("decision"),
        "decision": decision,
        "blueprint_count": int(len(pool)),
        "parent_seed_count": int(pool["parent_candidate_id"].nunique()) if not pool.empty else 0,
        "semantic_bucket_count": int(pool["semantic_bucket"].nunique()) if not pool.empty else 0,
        "motif_bucket_count": int(pool["motif_bucket"].nunique()) if not pool.empty else 0,
        "risk_flags": risk_flags,
        "executes_materialization": False,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core12_registration": not risk_flags,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE12 blueprint subgraph registration / gate audit" if not risk_flags else "A7FF-CORE11R blueprint generation repair",
    }
    write_json(RUNTIME / "a7ffcore11e_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE11E SMALL DRY GENERATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE11E generates expansion blueprints from replay-clean seeds. New expressions are not materialization-ready until CORE12 registers/gates them.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Generation Summary",
        "",
        md_table(family_summary),
        "",
        "## Parent Seed Summary",
        "",
        md_table(parent_summary),
        "",
        "## Boundary",
        "",
        "```text",
        "blueprint generation: true",
        "materialization / numeric / replay execution: false",
        "formula search / large search: false",
        "CORE2 registration required before materialization.",
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
