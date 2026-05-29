from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ab3_seed_constrained_dry_generation"
REPORT = REPO / "reports" / "CRYPTO_A7AB3_SEED_CONSTRAINED_DRY_GENERATION_20260529.md"

A7AB2_MANIFEST = REPO / "runtime" / "a7ab2_seed_constrained_micro_generation_contract" / "a7ab2_manifest.json"
A7AB2_QUOTA = REPO / "runtime" / "a7ab2_seed_constrained_micro_generation_contract" / "a7ab2_generation_quota.json"
A7AB2_FAMILIES = REPO / "runtime" / "a7ab2_seed_constrained_micro_generation_contract" / "a7ab2_allowed_generation_families.csv"
A7AB2_QUEUE = REPO / "runtime" / "a7ab2_seed_constrained_micro_generation_contract" / "a7ab2_seed_queue_input.csv"


DELTA_LB = [1, 4, 24]
MEAN_LB = [4, 24, 72, 168]
TS_LB = [24, 72, 168]
DECAY_LB = [4, 12, 24]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def stable_id(prefix: str, text: str) -> str:
    return f"{prefix}_{hashlib.sha1(text.encode('utf-8')).hexdigest()[:16]}"


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def next_distinct(values: list[int], value: int) -> int:
    if len(values) <= 1:
        return value
    idx = values.index(value)
    return values[(idx + 1) % len(values)]


SELF_SPREAD_PATTERNS = [
    re.compile(r"Sub\(Mean\(([^,]+),(\d+)\),Mean\(\1,\2\)\)"),
    re.compile(r"Sub\(Decay\(([^,]+),(\d+)\),Decay\(\1,\2\)\)"),
    re.compile(r"Sub\(TSRank\(([^,]+),(\d+)\),TSRank\(\1,\2\)\)"),
    re.compile(r"Sub\(ZScore\(Delta\(([^,]+),(\d+)\)\),ZScore\(Delta\(\1,\2\)\)\)"),
]


def obvious_self_spread_count(expressions: pd.Series) -> int:
    count = 0
    for expr in expressions.astype(str):
        if any(pattern.search(expr) for pattern in SELF_SPREAD_PATTERNS):
            count += 1
    return count


def atom(field: str, variant: int) -> tuple[str, str]:
    d = DELTA_LB[variant % len(DELTA_LB)]
    d2 = DELTA_LB[((variant // 5) + 1) % len(DELTA_LB)]
    m = MEAN_LB[(variant // 3) % len(MEAN_LB)]
    m2 = MEAN_LB[((variant // 7) + 1) % len(MEAN_LB)]
    t = TS_LB[(variant // 11) % len(TS_LB)]
    t2 = TS_LB[((variant // 13) + 1) % len(TS_LB)]
    e = DECAY_LB[(variant // 17) % len(DECAY_LB)]
    e2 = DECAY_LB[((variant // 19) + 1) % len(DECAY_LB)]
    if d2 == d:
        d2 = next_distinct(DELTA_LB, d)
    if m2 == m:
        m2 = next_distinct(MEAN_LB, m)
    if t2 == t:
        t2 = next_distinct(TS_LB, t)
    if e2 == e:
        e2 = next_distinct(DECAY_LB, e)
    k = variant % 48
    if k == 0:
        return f"Rank({field})", "rank"
    if k == 1:
        return f"ZScore({field})", "zscore"
    if k == 2:
        return f"TSRank({field},{t})", "tsrank"
    if k == 3:
        return f"Delta({field},{d})", "delta"
    if k == 4:
        return f"Mean({field},{m})", "mean"
    if k == 5:
        return f"Decay({field},{e})", "decay"
    if k == 6:
        return f"Clip(ZScore({field}),-3,3)", "clip_zscore"
    if k == 7:
        return f"Winsor(ZScore({field}),3)", "winsor_zscore"
    if k == 8:
        return f"Rank(Delta({field},{d}))", "rank_delta"
    if k == 9:
        return f"ZScore(Mean({field},{m}))", "zscore_mean"
    if k == 10:
        return f"TSRank(Delta({field},{d}),{t})", "tsrank_delta"
    if k == 11:
        return f"Decay(ZScore({field}),{e})", "decay_zscore"
    if k == 12:
        return f"Sub(TSRank({field},{t}),Rank({field}))", "tsrank_minus_rank"
    if k == 13:
        return f"Sub(ZScore(Mean({field},{m})),ZScore({field}))", "mean_minus_spot"
    if k == 14:
        return f"Mul(Rank({field}),ZScore(Delta({field},{d})))", "rank_x_delta"
    if k == 15:
        return f"Sub(Mean({field},{m}),Decay({field},{e}))", "mean_minus_decay"
    if k == 16:
        return f"Sub(Mean({field},{m}),Mean({field},{m2}))", "mean_spread"
    if k == 17:
        return f"Sub(TSRank({field},{t}),TSRank({field},{t2}))", "tsrank_spread"
    if k == 18:
        return f"Sub(Decay({field},{e}),Decay({field},{e2}))", "decay_spread"
    if k == 19:
        return f"Mean(Delta({field},{d}),{m})", "mean_delta"
    if k == 20:
        return f"Decay(Delta({field},{d}),{e})", "decay_delta"
    if k == 21:
        return f"TSRank(Mean({field},{m}),{t})", "tsrank_mean"
    if k == 22:
        return f"ZScore(Delta(Mean({field},{m}),{d}))", "zscore_delta_mean"
    if k == 23:
        return f"Rank(Sub(Mean({field},{m}),Mean({field},{m2})))", "rank_mean_spread"
    if k == 24:
        return f"ZScore(Sub(Decay({field},{e}),Decay({field},{e2})))", "zscore_decay_spread"
    if k == 25:
        return f"Clip(Delta({field},{d}),-3,3)", "clip_delta"
    if k == 26:
        return f"Winsor(Delta({field},{d}),3)", "winsor_delta"
    if k == 27:
        return f"Clip(Mean({field},{m}),-3,3)", "clip_mean"
    if k == 28:
        return f"Winsor(Mean({field},{m}),3)", "winsor_mean"
    if k == 29:
        return f"Rank(Mean(Delta({field},{d}),{m}))", "rank_mean_delta"
    if k == 30:
        return f"ZScore(Decay(Delta({field},{d}),{e}))", "zscore_decay_delta"
    if k == 31:
        return f"Sub(TSRank(Delta({field},{d}),{t}),Rank(Delta({field},{d2})))", "tsrank_delta_spread"
    if k == 32:
        return f"Mul(Rank(Mean({field},{m})),ZScore(Delta({field},{d})))", "rank_mean_x_delta"
    if k == 33:
        return f"Mul(TSRank({field},{t}),ZScore(Mean({field},{m})))", "tsrank_x_mean"
    if k == 34:
        return f"Mul(Decay({field},{e}),ZScore(Delta({field},{d})))", "decay_x_delta"
    if k == 35:
        return f"Sub(ZScore(Mean({field},{m})),ZScore(Mean({field},{m2})))", "zscore_mean_spread"
    if k == 36:
        return f"Sub(ZScore(Delta({field},{d})),ZScore(Delta({field},{d2})))", "zscore_delta_spread"
    if k == 37:
        return f"Sub(Rank(Decay({field},{e})),Rank(Decay({field},{e2})))", "rank_decay_spread"
    if k == 38:
        return f"TSRank(Sub(Mean({field},{m}),Mean({field},{m2})),{t})", "tsrank_mean_spread"
    if k == 39:
        return f"Decay(Sub(Mean({field},{m}),Mean({field},{m2})),{e})", "decay_mean_spread"
    if k == 40:
        return f"Clip(Sub(Mean({field},{m}),Decay({field},{e})),-3,3)", "clip_mean_decay_spread"
    if k == 41:
        return f"Winsor(Sub(Mean({field},{m}),Decay({field},{e})),3)", "winsor_mean_decay_spread"
    if k == 42:
        return f"Rank(Clip(ZScore({field}),-3,3))", "rank_clip_zscore"
    if k == 43:
        return f"Rank(Winsor(ZScore({field}),3))", "rank_winsor_zscore"
    if k == 44:
        return f"ZScore(Clip(Delta({field},{d}),-3,3))", "zscore_clip_delta"
    if k == 45:
        return f"ZScore(Winsor(Delta({field},{d}),3))", "zscore_winsor_delta"
    if k == 46:
        return f"Sub(Decay(Mean({field},{m}),{e}),Mean(Decay({field},{e2}),{m2}))", "decay_mean_minus_mean_decay"
    return f"Mul(Rank(Delta({field},{d})),TSRank(Mean({field},{m}),{t}))", "rank_delta_x_tsrank_mean"


def single_expression(field: str, variant: int) -> tuple[str, str, str]:
    a, ak = atom(field, variant)
    b, bk = atom(field, variant * 7 + 3)
    wrapper = variant % 12
    if wrapper == 0:
        return a, ak, "single_atom"
    if wrapper == 1:
        return f"Rank({a})", f"rank_{ak}", "rank_atom"
    if wrapper == 2:
        return f"ZScore({a})", f"zscore_{ak}", "zscore_atom"
    if wrapper == 3:
        return f"Sub({a},{b})", f"sub_{ak}_{bk}", "horizon_spread"
    if wrapper == 4:
        return f"Mul({a},{b})", f"mul_{ak}_{bk}", "self_interaction"
    if wrapper == 5:
        return f"Clip({a},-3,3)", f"clip_{ak}", "clip_atom"
    if wrapper == 6:
        return f"Winsor({a},3)", f"winsor_{ak}", "winsor_atom"
    if wrapper == 7:
        return f"Decay({a},{DECAY_LB[variant % len(DECAY_LB)]})", f"decay_{ak}", "decay_atom"
    if wrapper == 8:
        return f"Rank(Sub({a},{b}))", f"rank_sub_{ak}_{bk}", "rank_horizon_spread"
    if wrapper == 9:
        return f"ZScore(Mul({a},{b}))", f"zscore_mul_{ak}_{bk}", "zscore_self_interaction"
    if wrapper == 10:
        return f"Clip(Sub({a},{b}),-3,3)", f"clip_sub_{ak}_{bk}", "clip_horizon_spread"
    return f"Winsor(Mul({a},{b}),3)", f"winsor_mul_{ak}_{bk}", "winsor_self_interaction"


def pair_expression(field_a: str, field_b: str, variant: int) -> tuple[str, str, str]:
    a, ak = atom(field_a, variant)
    b, bk = atom(field_b, variant * 5 + 1)
    wrapper = variant % 6
    if wrapper == 0:
        return f"Mul({a},{b})", f"pair_mul_{ak}_{bk}", "pair_mul"
    if wrapper == 1:
        return f"Sub({a},{b})", f"pair_sub_{ak}_{bk}", "pair_sub"
    if wrapper == 2:
        return f"Rank(Mul({a},{b}))", f"pair_rank_mul_{ak}_{bk}", "pair_rank_mul"
    if wrapper == 3:
        return f"ZScore(Sub({a},{b}))", f"pair_zscore_sub_{ak}_{bk}", "pair_zscore_sub"
    if wrapper == 4:
        return f"Clip(Mul({a},{b}),-3,3)", f"pair_clip_mul_{ak}_{bk}", "pair_clip_mul"
    return f"Winsor(Sub({a},{b}),3)", f"pair_winsor_sub_{ak}_{bk}", "pair_winsor_sub"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifest2 = read_json(A7AB2_MANIFEST)
    if not manifest2.get("authorizes_a7ab3_seed_constrained_dry_generation"):
        raise SystemExit("A7AB-2 does not authorize A7AB-3")

    quota = read_json(A7AB2_QUOTA)
    families = pd.read_csv(A7AB2_FAMILIES)
    seed_queue = pd.read_csv(A7AB2_QUEUE)

    generated_total_cap = int(quota.get("generated_total_cap", 4096))
    static_selected_cap = int(quota.get("static_selected_cap", 512))

    fields_by_family = {
        fam: sorted(seed_queue.loc[seed_queue["field_family"].astype(str) == fam, "field_name"].astype(str).unique())
        for fam in sorted(seed_queue["field_family"].astype(str).unique())
    }
    all_fields = sorted(seed_queue["field_name"].astype(str).unique())

    family_ids = families["family_id"].astype(str).tolist()
    target_per_family = generated_total_cap // len(family_ids)
    extra = generated_total_cap % len(family_ids)

    records: list[dict[str, Any]] = []
    seen_expr: set[str] = set()
    for family_idx, family_id in enumerate(family_ids):
        target = target_per_family + (1 if family_idx < extra else 0)
        attempts = 0
        made = 0
        while made < target and attempts < target * 80:
            attempts += 1
            variant = attempts + family_idx * 100003
            if family_id == "G0_price_return_reversal":
                primary = "trade_return_1h"
                expr, skeleton_key, motif = single_expression(primary, variant)
                source_fields = primary
            elif family_id == "G1_volatility_state_reversal":
                choices = fields_by_family.get("volatility", [])
                primary = choices[variant % len(choices)]
                expr, skeleton_key, motif = single_expression(primary, variant)
                source_fields = primary
            elif family_id == "G2_basis_premium_dislocation":
                choices = fields_by_family.get("basis_premium", [])
                primary = choices[variant % len(choices)]
                expr, skeleton_key, motif = single_expression(primary, variant)
                source_fields = primary
            else:
                primary = all_fields[variant % len(all_fields)]
                other_choices = [f for f in all_fields if f != primary]
                secondary = other_choices[(variant // 7) % len(other_choices)]
                expr, skeleton_key, motif = pair_expression(primary, secondary, variant)
                source_fields = f"{primary}|{secondary}"
            if expr in seen_expr:
                continue
            seen_expr.add(expr)
            candidate_id = stable_id("a7ab3", expr)
            records.append(
                {
                    "candidate_id": candidate_id,
                    "family_id": family_id,
                    "primary_seed_field": primary,
                    "source_fields": source_fields,
                    "expression": expr,
                    "skeleton_key": stable_id("skeleton", skeleton_key),
                    "production_key": stable_id("prod", f"{family_id}:{motif}:{skeleton_key}"),
                    "motif": motif,
                    "static_valid": True,
                    "uses_may": False,
                    "allowed_next_use": "A7AB4_materialization_preflight_only",
                }
            )
            made += 1

    generated = pd.DataFrame(records)
    # generated_total_cap is a maximum budget, not a minimum. The pass gate is
    # whether the static queue can be filled under diversity constraints.
    if len(generated) < static_selected_cap:
        decision = "HOLD_A7AB3_DRY_GENERATION_UNDERFILLED"
    else:
        decision = "PASS_A7AB3_SEED_CONSTRAINED_DRY_GENERATION_READY_FOR_A7AB4_MATERIALIZATION_PREFLIGHT"

    # Static selection applies diversity caps before any numeric evaluation.
    max_per_family = max(1, int(static_selected_cap * float(quota.get("max_per_family_share", 0.35))))
    max_per_field = max(1, int(static_selected_cap * float(quota.get("max_per_seed_field_share", 0.25))))
    max_per_skeleton = max(1, int(static_selected_cap * float(quota.get("max_same_skeleton_share", 0.15))))
    selected_rows: list[dict[str, Any]] = []
    family_counts: dict[str, int] = {}
    field_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    for row in generated.to_dict("records"):
        family = str(row["family_id"])
        field = str(row["primary_seed_field"])
        skeleton = str(row["skeleton_key"])
        if family_counts.get(family, 0) >= max_per_family:
            continue
        if field_counts.get(field, 0) >= max_per_field:
            continue
        if skeleton_counts.get(skeleton, 0) >= max_per_skeleton:
            continue
        selected_rows.append(row)
        family_counts[family] = family_counts.get(family, 0) + 1
        field_counts[field] = field_counts.get(field, 0) + 1
        skeleton_counts[skeleton] = skeleton_counts.get(skeleton, 0) + 1
        if len(selected_rows) >= static_selected_cap:
            break

    selected = pd.DataFrame(selected_rows)
    if selected.empty:
        selected = pd.DataFrame(columns=generated.columns)
    selected.insert(0, "static_selector_rank", range(1, len(selected) + 1))

    quota_summary = {
        "generated_total": int(len(generated)),
        "unique_expression_ratio": float(generated["expression"].nunique() / max(1, len(generated))),
        "family_count": int(generated["family_id"].nunique()) if not generated.empty else 0,
        "primary_seed_field_count": int(generated["primary_seed_field"].nunique()) if not generated.empty else 0,
        "skeleton_count": int(generated["skeleton_key"].nunique()) if not generated.empty else 0,
        "static_selected_count": int(len(selected)),
        "static_selected_family_count": int(selected["family_id"].nunique()) if not selected.empty else 0,
        "static_selected_seed_field_count": int(selected["primary_seed_field"].nunique()) if not selected.empty else 0,
        "static_selected_skeleton_count": int(selected["skeleton_key"].nunique()) if not selected.empty else 0,
        "static_top_family_share": float(selected["family_id"].value_counts(normalize=True).iloc[0]) if not selected.empty else None,
        "static_top_seed_field_share": float(selected["primary_seed_field"].value_counts(normalize=True).iloc[0]) if not selected.empty else None,
        "static_top_skeleton_share": float(selected["skeleton_key"].value_counts(normalize=True).iloc[0]) if not selected.empty else None,
    }
    static_validity = {
        "generated_obvious_self_spread_count": obvious_self_spread_count(generated["expression"]),
        "selected_obvious_self_spread_count": obvious_self_spread_count(selected["expression"]) if not selected.empty else 0,
        "generated_uses_may_count": int(generated["uses_may"].sum()) if not generated.empty else 0,
        "selected_uses_may_count": int(selected["uses_may"].sum()) if not selected.empty else 0,
    }
    if decision.startswith("PASS"):
        if quota_summary["static_selected_count"] < static_selected_cap:
            decision = "HOLD_A7AB3_STATIC_SELECTION_UNDERFILLED"
        elif quota_summary["static_selected_family_count"] < int(quota.get("min_family_count_static_queue", 3)):
            decision = "HOLD_A7AB3_STATIC_FAMILY_DIVERSITY_WEAK"
        elif quota_summary["static_selected_seed_field_count"] < int(quota.get("min_seed_field_count_static_queue", 5)):
            decision = "HOLD_A7AB3_STATIC_SEED_FIELD_DIVERSITY_WEAK"
        elif static_validity["selected_obvious_self_spread_count"] > 0:
            decision = "HOLD_A7AB3_STATIC_SELF_SPREAD_RISK"

    family_summary = generated.groupby("family_id", as_index=False).agg(
        generated_count=("candidate_id", "count"),
        seed_field_count=("primary_seed_field", "nunique"),
        skeleton_count=("skeleton_key", "nunique"),
    )
    selected_family_summary = selected.groupby("family_id", as_index=False).agg(
        selected_count=("candidate_id", "count"),
        seed_field_count=("primary_seed_field", "nunique"),
        skeleton_count=("skeleton_key", "nunique"),
    )

    manifest = {
        "stage": "A7AB-3",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_formula_generation": True,
        "executes_static_dry_generation_only": True,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may": False,
        "authorizes_a7ab4_materialization_preflight": decision.startswith("PASS"),
        "authorizes_fast_replay": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "quota_summary": quota_summary,
        "static_validity": static_validity,
        "generation_contract": quota,
    }

    generated.to_csv(RUNTIME / "a7ab3_generated_pool.csv", index=False)
    selected.to_csv(RUNTIME / "a7ab3_static_selected_queue.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ab3_generation_family_summary.csv", index=False)
    selected_family_summary.to_csv(RUNTIME / "a7ab3_static_selected_family_summary.csv", index=False)
    write_json(RUNTIME / "a7ab3_manifest.json", manifest)
    write_json(RUNTIME / "a7ab3_static_validity_audit.json", static_validity)
    write_json(
        RUNTIME / "a7ab3_authorization_matrix.json",
        {
            "A7AB-3": {"status": decision},
            "A7AB-4_materialization_preflight": {"authorized": bool(decision.startswith("PASS"))},
            "fast_replay": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AB-3 SEED-CONSTRAINED DRY GENERATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AB-3 generates a static formula pool from A7AB-1 primitive-response seeds. It does not run replay, search execution, training, or alpha proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Generation Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Static Selected Family Summary",
        "",
        md_table(selected_family_summary),
        "",
        "## Static Validity Audit",
        "",
        "```json",
        json.dumps(static_validity, indent=2, sort_keys=True),
        "```",
        "",
        "## Static Selected Queue Sample",
        "",
        md_table(
            selected[
                [
                    "static_selector_rank",
                    "candidate_id",
                    "family_id",
                    "primary_seed_field",
                    "source_fields",
                    "skeleton_key",
                    "production_key",
                    "motif",
                    "expression",
                ]
            ],
            max_rows=40,
        ),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
