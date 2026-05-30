from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff24r_dry_generation_plan"
REPORT = REPO / "reports" / "CRYPTO_A7FF24R_DRY_GENERATION_PLAN_20260530.md"

A7FF23R_MANIFEST = REPO / "runtime" / "a7ff23r_derived_factor_expansion_contract" / "a7ff23r_manifest.json"
A7FF23R_SEEDS = REPO / "runtime" / "a7ff23r_derived_factor_expansion_contract" / "a7ff23r_seed_policy.csv"
A7FF23R_PAIRS = REPO / "runtime" / "a7ff23r_derived_factor_expansion_contract" / "a7ff23r_pair_policy.csv"
A7FF23R_BUDGET = REPO / "runtime" / "a7ff23r_derived_factor_expansion_contract" / "a7ff23r_generation_budget.json"
A7FF23R_SELECTOR = REPO / "runtime" / "a7ff23r_derived_factor_expansion_contract" / "a7ff23r_selector_policy.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_id(prefix: str, text: str) -> str:
    return f"{prefix}_{hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]}"


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


def transforms(field: str, semantic: str, route: str) -> list[tuple[str, str]]:
    windows = [1, 2, 4, 8, 12, 24, 48, 72, 168, 336]
    out: list[tuple[str, str]] = [("level", field)]
    for w in windows:
        out.extend(
            [
                (f"delta_{w}h", f"Delta({field},{w})"),
                (f"mean_{w}h", f"Mean({field},{w})"),
                (f"zmean_{w}h", f"ZScore(Mean({field},{w}))"),
            ]
        )
    if semantic in {"basis_premium_like", "funding_like", "positioning_like", "volatility_like"}:
        for w in [8, 24, 72, 168]:
            out.append((f"abs_zmean_{w}h", f"Abs(ZScore(Mean({field},{w})))"))
            out.append((f"decay_{w}h", f"Decay({field},{w})"))
    if route == "exploratory_signal_seed":
        out.extend(
            [
                ("csrank", f"CSRank({field})"),
                ("sign_delta_24h", f"Sign(Delta({field},24))"),
                ("clip_zscore", f"Clip(ZScore({field}),-3,3)"),
            ]
        )
    return list(dict(out).items())


def motifs_for_pair(left_semantic: str, right_semantic: str, route: str) -> list[str]:
    motifs = ["mul", "sub", "spread_rank", "gated_sign", "safe_div_abs", "smooth_mul"]
    if route == "exploratory_generation_priority":
        motifs.extend(["relative_shock", "signed_spread", "mean_reversion_gate"])
    if "state_or_taxonomy" in {left_semantic, right_semantic}:
        motifs = ["mul", "gated_sign", "smooth_mul", "signed_spread"]
    return motifs


def interaction(left: str, right: str, motif: str) -> str:
    if motif == "mul":
        return f"Mul({left},{right})"
    if motif == "sub":
        return f"Sub({left},{right})"
    if motif == "spread_rank":
        return f"Sub(CSRank({left}),CSRank({right}))"
    if motif == "gated_sign":
        return f"Mul({left},Sign({right}))"
    if motif == "safe_div_abs":
        return f"SafeDiv({left},Abs({right}))"
    if motif == "smooth_mul":
        return f"Mean(Mul({left},{right}),4)"
    if motif == "relative_shock":
        return f"Mul(Delta({left},4),ZScore({right}))"
    if motif == "signed_spread":
        return f"Mul(Sub(CSRank({left}),CSRank({right})),Sign({right}))"
    if motif == "mean_reversion_gate":
        return f"Mul(Neg(ZScore({left})),Sign({right}))"
    return f"Mul({left},{right})"


def skeleton(expr: str) -> str:
    import re

    text = re.sub(r"[A-Za-z_][A-Za-z0-9_]*", "TOK", expr)
    text = re.sub(r"\d+", "N", text)
    return stable_id("skel", text)


def build_pool(seeds: pd.DataFrame, pairs: pd.DataFrame, budget: dict[str, Any]) -> pd.DataFrame:
    target = int(budget["generated_blueprints_target"])
    seed_by_field = {row.field_name: row for row in seeds.itertuples(index=False)}
    rows: list[dict[str, Any]] = []
    seen_expr: set[str] = set()
    level_targets = {
        "L1_single_field_transform": 1200,
        "L2_typed_two_field_interaction": 14000,
        "L3_state_conditioned_feature": 7000,
        "L4_factor_candidate_probe": 1800,
    }
    level_counts = {key: 0 for key in level_targets}
    semantic_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}

    def try_add(row: dict[str, Any], *, strict_level_cap: bool = True) -> bool:
        if len(rows) >= target:
            return False
        level = str(row["level"])
        expr = str(row["expression"])
        if expr in seen_expr:
            return False
        if strict_level_cap and level_counts.get(level, 0) >= level_targets.get(level, target):
            return False
        sem = str(row["semantic_pair"])
        motif = str(row["motif"])
        skel = skeleton(expr)
        # These are pool-construction caps, not selector caps. They prevent one early
        # field pair from filling the entire dry-generation budget.
        if semantic_counts.get(sem, 0) >= max(6000, target // 4):
            return False
        if motif_counts.get(motif, 0) >= max(6000, target // 4):
            return False
        if skeleton_counts.get(skel, 0) >= 400:
            return False
        row["skeleton_key"] = skel
        row["production_key"] = stable_id(
            "prod",
            f"{row['primary_field']}|{row['secondary_field']}|{row['primary_transform']}|{row['secondary_transform']}|{row['motif']}",
        )
        row["blueprint_id"] = stable_id("a7ff24r", f"{level}|{expr}")
        rows.append(row)
        seen_expr.add(expr)
        level_counts[level] = level_counts.get(level, 0) + 1
        semantic_counts[sem] = semantic_counts.get(sem, 0) + 1
        motif_counts[motif] = motif_counts.get(motif, 0) + 1
        skeleton_counts[skel] = skeleton_counts.get(skel, 0) + 1
        return True

    signal_seeds = seeds[seeds["a7ff23r_seed_route"].isin(["primary_signal_seed", "exploratory_signal_seed"])]
    modifier_seeds = seeds[seeds["a7ff23r_seed_route"].eq("modifier_only_seed")]

    # L1: single-source transforms. This is intentionally a probe source, not a proof source.
    for seed in signal_seeds.itertuples(index=False):
        for transform_name, expr in transforms(seed.field_name, seed.semantic_type_v3, seed.a7ff23r_seed_route):
            try_add(
                {
                    "level": "L1_single_field_transform",
                    "primary_field": seed.field_name,
                    "secondary_field": "",
                    "primary_semantic": seed.semantic_type_v3,
                    "secondary_semantic": "",
                    "primary_route": seed.a7ff23r_seed_route,
                    "secondary_route": "",
                    "primary_transform": transform_name,
                    "secondary_transform": "",
                    "motif": "single",
                    "expression": expr,
                    "semantic_pair": seed.semantic_type_v3,
                    "generation_priority": "P0" if seed.a7ff23r_seed_route == "primary_signal_seed" else "P1",
                    "candidate_role": "ordinary_alpha_valid" if seed.a7ff23r_seed_route == "primary_signal_seed" else "exploratory_signal_probe",
                    "modifier_guard_required": False,
                }
            )

    # L2: typed interactions from the R3/R23R pair policy.
    for pair in pairs.itertuples(index=False):
        if level_counts["L2_typed_two_field_interaction"] >= level_targets["L2_typed_two_field_interaction"]:
            break
        left = seed_by_field.get(pair.left_field)
        right = seed_by_field.get(pair.right_field)
        if left is None or right is None:
            continue
        left_transforms = transforms(left.field_name, left.semantic_type_v3, left.a7ff23r_seed_route)
        right_transforms = transforms(right.field_name, right.semantic_type_v3, right.a7ff23r_seed_route)
        pair_motifs = motifs_for_pair(left.semantic_type_v3, right.semantic_type_v3, pair.a7ff23r_pair_route)
        for left_name, left_expr in left_transforms[:16]:
            for right_name, right_expr in right_transforms[:16]:
                for motif in pair_motifs:
                    expr = interaction(left_expr, right_expr, motif)
                    level = "L2_typed_two_field_interaction"
                    if bool(pair.requires_modifier_guard):
                        level = "L3_state_conditioned_feature"
                    try_add(
                        {
                            "level": level,
                            "primary_field": left.field_name,
                            "secondary_field": right.field_name,
                            "primary_semantic": left.semantic_type_v3,
                            "secondary_semantic": right.semantic_type_v3,
                            "primary_route": left.a7ff23r_seed_route,
                            "secondary_route": right.a7ff23r_seed_route,
                            "primary_transform": left_name,
                            "secondary_transform": right_name,
                            "motif": motif,
                            "expression": expr,
                            "semantic_pair": pair.semantic_pair,
                            "generation_priority": "P0" if pair.a7ff23r_pair_route == "generation_priority" else "P1",
                            "candidate_role": "role_mixed_allowed",
                            "modifier_guard_required": bool(pair.requires_modifier_guard),
                        }
                    )
                    if level_counts.get(level, 0) >= level_targets.get(level, target):
                        break
                if level_counts.get("L2_typed_two_field_interaction", 0) >= level_targets["L2_typed_two_field_interaction"]:
                    break
            if level_counts.get("L2_typed_two_field_interaction", 0) >= level_targets["L2_typed_two_field_interaction"]:
                break

    # L3: explicitly condition each signal seed on a bounded set of modifiers.
    for sig in signal_seeds.itertuples(index=False):
        if level_counts["L3_state_conditioned_feature"] >= level_targets["L3_state_conditioned_feature"]:
            break
        for mod in modifier_seeds.itertuples(index=False):
            if level_counts["L3_state_conditioned_feature"] >= level_targets["L3_state_conditioned_feature"]:
                break
            for sig_name, sig_expr in transforms(sig.field_name, sig.semantic_type_v3, sig.a7ff23r_seed_route)[:12]:
                for mod_name, mod_expr in transforms(mod.field_name, mod.semantic_type_v3, mod.a7ff23r_seed_route)[:8]:
                    expr = f"Mul({sig_expr},CSRank({mod_expr}))"
                    try_add(
                        {
                            "level": "L3_state_conditioned_feature",
                            "primary_field": sig.field_name,
                            "secondary_field": mod.field_name,
                            "primary_semantic": sig.semantic_type_v3,
                            "secondary_semantic": mod.semantic_type_v3,
                            "primary_route": sig.a7ff23r_seed_route,
                            "secondary_route": mod.a7ff23r_seed_route,
                            "primary_transform": sig_name,
                            "secondary_transform": mod_name,
                            "motif": "state_conditioned_csrank",
                            "expression": expr,
                            "semantic_pair": "|".join(sorted([sig.semantic_type_v3, mod.semantic_type_v3])),
                            "generation_priority": "P1",
                            "candidate_role": "role_mixed_allowed",
                            "modifier_guard_required": True,
                        }
                    )
                    if level_counts["L3_state_conditioned_feature"] >= level_targets["L3_state_conditioned_feature"]:
                        break
                if level_counts["L3_state_conditioned_feature"] >= level_targets["L3_state_conditioned_feature"]:
                    break

    # Fill any remaining budget with relaxed caps. This keeps the pool large enough
    # for a company-machine wave without making the first pass an open grammar.
    if len(rows) < target:
        for pair in pairs.itertuples(index=False):
            if len(rows) >= target:
                break
            left = seed_by_field.get(pair.left_field)
            right = seed_by_field.get(pair.right_field)
            if left is None or right is None:
                continue
            pair_motifs = motifs_for_pair(left.semantic_type_v3, right.semantic_type_v3, pair.a7ff23r_pair_route)
            for left_name, left_expr in transforms(left.field_name, left.semantic_type_v3, left.a7ff23r_seed_route)[:20]:
                for right_name, right_expr in transforms(right.field_name, right.semantic_type_v3, right.a7ff23r_seed_route)[:20]:
                    for motif in pair_motifs:
                        expr = interaction(left_expr, right_expr, motif)
                        try_add(
                            {
                                "level": "L4_factor_candidate_probe",
                                "primary_field": left.field_name,
                                "secondary_field": right.field_name,
                                "primary_semantic": left.semantic_type_v3,
                                "secondary_semantic": right.semantic_type_v3,
                                "primary_route": left.a7ff23r_seed_route,
                                "secondary_route": right.a7ff23r_seed_route,
                                "primary_transform": left_name,
                                "secondary_transform": right_name,
                                "motif": motif,
                                "expression": expr,
                                "semantic_pair": pair.semantic_pair,
                                "generation_priority": "P2",
                                "candidate_role": "role_mixed_allowed",
                                "modifier_guard_required": bool(pair.requires_modifier_guard),
                            },
                            strict_level_cap=False,
                        )
                        if len(rows) >= target:
                            break
                    if len(rows) >= target:
                        break
                if len(rows) >= target:
                    break

    pool = pd.DataFrame(rows).drop_duplicates(subset=["expression"])
    pool = pool.sort_values(
        ["generation_priority", "level", "semantic_pair", "motif", "skeleton_key", "blueprint_id"]
    ).head(target)
    return pool


def select_diverse_queue(pool: pd.DataFrame, target: int) -> pd.DataFrame:
    selected: list[pd.Series] = []
    semantic_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    level_counts: dict[str, int] = {}
    semantic_cap = max(500, target // 3)
    motif_cap = max(500, target // 3)
    skeleton_cap = 80
    level_cap = target
    for _, row in pool.iterrows():
        semantic = str(row["semantic_pair"])
        motif = str(row["motif"])
        skeleton_key = str(row["skeleton_key"])
        level = str(row["level"])
        if semantic_counts.get(semantic, 0) >= semantic_cap:
            continue
        if motif_counts.get(motif, 0) >= motif_cap:
            continue
        if skeleton_counts.get(skeleton_key, 0) >= skeleton_cap:
            continue
        if level_counts.get(level, 0) >= level_cap:
            continue
        selected.append(row)
        semantic_counts[semantic] = semantic_counts.get(semantic, 0) + 1
        motif_counts[motif] = motif_counts.get(motif, 0) + 1
        skeleton_counts[skeleton_key] = skeleton_counts.get(skeleton_key, 0) + 1
        level_counts[level] = level_counts.get(level, 0) + 1
        if len(selected) >= target:
            break
    selected_df = pd.DataFrame(selected)
    if len(selected_df) < target:
        used = set(selected_df["blueprint_id"]) if not selected_df.empty else set()
        extra = pool[~pool["blueprint_id"].isin(used)].head(target - len(selected_df))
        selected_df = pd.concat([selected_df, extra], ignore_index=True)
    return selected_df.head(target)


def shard_queue(queue: pd.DataFrame, shard_count: int, shard_size: int) -> pd.DataFrame:
    limited = queue.head(shard_count * shard_size).copy()
    limited["company_shard"] = [i // shard_size for i in range(len(limited))]
    limited["company_shard"] = limited["company_shard"].map(lambda x: f"shard_{int(x):02d}")
    plan = (
        limited.groupby("company_shard", dropna=False)
        .agg(
            row_count=("blueprint_id", "count"),
            semantic_pairs=("semantic_pair", "nunique"),
            motifs=("motif", "nunique"),
            skeletons=("skeleton_key", "nunique"),
        )
        .reset_index()
    )
    for shard, group in limited.groupby("company_shard"):
        group.to_csv(RUNTIME / f"a7ff24r_company_{shard}_queue.csv", index=False)
    limited.to_csv(RUNTIME / "a7ff24r_company_numeric_wave_queue.csv", index=False)
    return plan


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifest23 = read_json(A7FF23R_MANIFEST)
    if not bool(manifest23.get("authorizes_a7ff24r_company_execution_plan_contract")):
        raise SystemExit("A7FF-23R does not authorize A7FF-24R.")
    seeds = pd.read_csv(A7FF23R_SEEDS)
    pairs = pd.read_csv(A7FF23R_PAIRS)
    budget = read_json(A7FF23R_BUDGET)
    selector = read_json(A7FF23R_SELECTOR)

    pool = build_pool(seeds, pairs, budget)
    materialization_queue = select_diverse_queue(pool, int(budget["materialization_target"]))
    company_wave_queue = select_diverse_queue(pool, int(budget["company_numeric_wave_blueprints"]))
    shard_plan = shard_queue(
        company_wave_queue,
        int(budget["company_numeric_shards"]),
        int(budget["company_numeric_shard_size"]),
    )

    level_summary = pool.groupby(["level"], dropna=False).size().reset_index(name="count")
    semantic_summary = pool.groupby(["semantic_pair"], dropna=False).size().reset_index(name="count").sort_values(
        "count", ascending=False
    )
    queue_summary = materialization_queue.groupby(["level"], dropna=False).size().reset_index(name="materialization_count")
    blockers: list[str] = []
    # The blueprint target is an expansion envelope. The hard floor is lower so
    # we do not block a usable company-machine wave merely to manufacture more
    # near-duplicate expressions.
    if len(pool) < int(int(budget["generated_blueprints_target"]) * 0.85):
        blockers.append("generated_pool_below_hard_floor")
    if len(materialization_queue) < int(budget["materialization_target"]):
        blockers.append("materialization_queue_below_target")
    if len(company_wave_queue) < int(budget["company_numeric_wave_blueprints"]):
        blockers.append("company_wave_queue_below_target")
    if materialization_queue["semantic_pair"].nunique() < int(budget["minimum_selected_semantic_families"]):
        blockers.append("materialization_semantic_family_breadth_low")
    decision = "PASS_A7FF24R_DRY_GENERATION_PLAN_READY_FOR_COMPANY_NUMERIC" if not blockers else "HOLD_A7FF24R_DRY_GENERATION_PLAN_INSUFFICIENT"

    pool.to_csv(RUNTIME / "a7ff24r_blueprint_pool.csv", index=False)
    materialization_queue.to_csv(RUNTIME / "a7ff24r_materialization_queue.csv", index=False)
    level_summary.to_csv(RUNTIME / "a7ff24r_level_summary.csv", index=False)
    semantic_summary.to_csv(RUNTIME / "a7ff24r_semantic_summary.csv", index=False)
    queue_summary.to_csv(RUNTIME / "a7ff24r_materialization_queue_summary.csv", index=False)
    shard_plan.to_csv(RUNTIME / "a7ff24r_company_shard_plan.csv", index=False)

    remote_plan = {
        "remote_repo": "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote",
        "remote_python": "D:\\HermesWorker\\venvs\\phase3z33\\Scripts\\python.exe",
        "local_queue": str(RUNTIME / "a7ff24r_company_numeric_wave_queue.csv"),
        "company_shards": int(budget["company_numeric_shards"]),
        "company_shard_size": int(budget["company_numeric_shard_size"]),
        "max_parallel_company_shards": int(budget["max_parallel_company_shards"]),
        "execution_status": "not_started",
        "next_required_script": "A7FF25R company numeric runner implementation or adapter against crypto_a7ff8_expanded_numeric_probe.py",
    }
    write_json(RUNTIME / "a7ff24r_company_remote_plan.json", remote_plan)

    manifest = {
        "stage": "A7FF-24R-DRY-GENERATION-PLAN",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_a7ff23r_decision": manifest23.get("decision", ""),
        "blueprint_count": int(len(pool)),
        "materialization_queue_count": int(len(materialization_queue)),
        "company_wave_queue_count": int(len(company_wave_queue)),
        "company_shard_count": int(len(shard_plan)),
        "semantic_pair_count": int(pool["semantic_pair"].nunique()),
        "materialization_semantic_pair_count": int(materialization_queue["semantic_pair"].nunique()),
        "motif_count": int(pool["motif"].nunique()),
        "materialization_motif_count": int(materialization_queue["motif"].nunique()),
        "executes_blueprint_generation": True,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_company_numeric_execution": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "selector_policy": selector,
    }
    write_json(RUNTIME / "a7ff24r_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-24R DRY GENERATION PLAN

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-24R turns the A7FF-23R contract into a concrete blueprint pool and a company-machine numeric wave queue. It does not run numeric evaluation, replay, search, or alpha proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Level Summary

{md_table(level_summary)}

## Materialization Queue Summary

{md_table(queue_summary)}

## Top Semantic Pairs

{md_table(semantic_summary, 40)}

## Company Shard Plan

{md_table(shard_plan)}

## Remote Plan

```json
{json.dumps(remote_plan, indent=2, sort_keys=True)}
```

## Boundary

- Blueprint generation executed: `true`
- Numeric probe executed: `false`
- Replay/search executed: `false`
- Uses May: `false`
- Authorizes company numeric execution only after runner/adapter check: `{str(manifest["authorizes_company_numeric_execution"]).lower()}`
- Authorizes alpha proof / shadow / paper / live: `false`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
