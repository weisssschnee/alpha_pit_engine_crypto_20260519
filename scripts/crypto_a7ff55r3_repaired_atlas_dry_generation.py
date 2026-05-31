from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff55r3_repaired_atlas_dry_generation"
REPORT = REPO / "reports" / "CRYPTO_A7FF55R3_REPAIRED_ATLAS_DRY_GENERATION_20260531.md"
A7FF55R2 = REPO / "runtime" / "a7ff55r2_atlas_field_family_generation_repair" / "a7ff55r2_manifest.json"
SEEDS = REPO / "runtime" / "a7ff55r2_atlas_field_family_generation_repair" / "a7ff55r2_repaired_seed_policy_preview.csv"
PAIR_PATCH = REPO / "runtime" / "a7ff55r2_atlas_field_family_generation_repair" / "a7ff55r2_required_pair_policy_patch.csv"


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
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def transforms(field: str, semantic: str) -> list[tuple[str, str]]:
    windows = [4, 8, 24, 72, 168]
    out: list[tuple[str, str]] = [("level", field)]
    for w in windows:
        out.append((f"delta_{w}h", f"Delta({field},{w})"))
        out.append((f"mean_{w}h", f"Mean({field},{w})"))
        out.append((f"zmean_{w}h", f"ZScore(Mean({field},{w}))"))
    if semantic in {"open_interest_like", "taker_flow_like", "liquidity_like", "positioning_like", "volatility_like", "basis_premium_like"}:
        for w in [24, 72, 168]:
            out.append((f"abs_zmean_{w}h", f"Abs(ZScore(Mean({field},{w})))"))
            out.append((f"decay_{w}h", f"Decay({field},{w})"))
            out.append((f"tsrank_{w}h", f"TSRank({field},{w})"))
    return list(dict(out).items())


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
    if motif == "delta_x_divergence":
        return f"Mul(Delta({left},24),Sub(CSRank({left}),CSRank({right})))"
    if motif == "flow_x_leverage":
        return f"Mul(ZScore({left}),Delta({right},24))"
    if motif == "liquidity_shock":
        return f"Mul(Delta({left},24),Abs(ZScore({right})))"
    return f"Mul({left},{right})"


def skeleton(expr: str) -> str:
    import re

    text = re.sub(r"[A-Za-z_][A-Za-z0-9_]*", "TOK", expr)
    text = re.sub(r"\d+", "N", text)
    return stable_id("skel", text)


def add_row(rows: list[dict[str, Any]], seen: set[str], row: dict[str, Any]) -> None:
    expr = str(row["expression"])
    if expr in seen:
        return
    row["skeleton_key"] = skeleton(expr)
    row["production_key"] = stable_id(
        "prod",
        f"{row['primary_field']}|{row['secondary_field']}|{row['primary_transform']}|{row['secondary_transform']}|{row['motif']}",
    )
    row["blueprint_id"] = stable_id("a7ff55r3", f"{row['level']}|{expr}")
    rows.append(row)
    seen.add(expr)


def build_pool(seeds: pd.DataFrame, pair_patch: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    active = seeds[seeds["a7ff23r_seed_route"].isin(["primary_signal_seed", "exploratory_signal_seed"])]
    interaction_seeds = seeds[
        seeds["a7ff23r_seed_route"].isin(["primary_signal_seed", "exploratory_signal_seed", "modifier_only_seed"])
    ]
    by_semantic = {key: group.copy() for key, group in interaction_seeds.groupby("semantic_type_v3")}

    for seed in active.itertuples(index=False):
        if seed.semantic_type_v3 not in {"open_interest_like", "taker_flow_like", "liquidity_like", "positioning_like", "volatility_like"}:
            continue
        for name, expr in transforms(seed.field_name, seed.semantic_type_v3)[:12]:
            add_row(
                rows,
                seen,
                {
                    "level": "L1_repaired_single_field_transform",
                    "candidate_role": "exploratory_signal_probe",
                    "generation_priority": "R3P0",
                    "semantic_pair": seed.semantic_type_v3,
                    "motif": "single",
                    "primary_field": seed.field_name,
                    "secondary_field": "",
                    "primary_semantic": seed.semantic_type_v3,
                    "secondary_semantic": "",
                    "primary_transform": name,
                    "secondary_transform": "",
                    "expression": expr,
                },
            )

    motif_map = {
        "open_interest_like|positioning_like": ["delta_x_divergence", "signed_spread", "smooth_mul", "spread_rank", "safe_div_abs"],
        "taker_flow_like|open_interest_like": ["flow_x_leverage", "relative_shock", "gated_sign", "smooth_mul", "safe_div_abs"],
        "liquidity_like|volatility_like": ["liquidity_shock", "smooth_mul", "spread_rank", "mean_reversion_gate", "safe_div_abs"],
        "open_interest_like|price_like": ["delta_x_divergence", "mean_reversion_gate", "smooth_mul", "spread_rank"],
        "taker_flow_like|basis_premium_like": ["relative_shock", "smooth_mul", "gated_sign", "safe_div_abs"],
    }
    for pair in pair_patch.itertuples(index=False):
        left_group = by_semantic.get(pair.left_semantic_type_v3, pd.DataFrame())
        right_group = by_semantic.get(pair.right_semantic_type_v3, pd.DataFrame())
        if left_group.empty or right_group.empty:
            continue
        motifs = motif_map.get(pair.semantic_pair, ["mul", "sub", "smooth_mul", "spread_rank"])
        pair_count = 0
        for left in left_group.itertuples(index=False):
            for right in right_group.itertuples(index=False):
                left_transforms = transforms(left.field_name, left.semantic_type_v3)[:10]
                right_transforms = transforms(right.field_name, right.semantic_type_v3)[:10]
                for lname, lexpr in left_transforms:
                    for rname, rexpr in right_transforms:
                        for motif in motifs:
                            expr = interaction(lexpr, rexpr, motif)
                            add_row(
                                rows,
                                seen,
                                {
                                    "level": "L2_repaired_typed_interaction",
                                    "candidate_role": "role_mixed_allowed",
                                    "generation_priority": "R3P0" if pair.a7ff55r2_pair_route == "generation_priority" else "R3P1",
                                    "semantic_pair": pair.semantic_pair,
                                    "motif": motif,
                                    "primary_field": left.field_name,
                                    "secondary_field": right.field_name,
                                    "primary_semantic": left.semantic_type_v3,
                                    "secondary_semantic": right.semantic_type_v3,
                                    "primary_transform": lname,
                                    "secondary_transform": rname,
                                    "expression": expr,
                                },
                            )
                            pair_count += 1
                            if pair_count >= 1800:
                                break
                        if pair_count >= 1800:
                            break
                    if pair_count >= 1800:
                        break
                if pair_count >= 1800:
                    break
            if pair_count >= 1800:
                break
    return pd.DataFrame(rows)


def select_balanced_queue(pool: pd.DataFrame, target: int = 2400) -> pd.DataFrame:
    selected: list[pd.Series] = []
    sem_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    skel_counts: dict[str, int] = {}
    for _, row in pool.sort_values(["generation_priority", "semantic_pair", "motif", "blueprint_id"]).iterrows():
        sem = str(row["semantic_pair"])
        motif = str(row["motif"])
        skel = str(row["skeleton_key"])
        if sem_counts.get(sem, 0) >= 600:
            continue
        if motif_counts.get(motif, 0) >= 500:
            continue
        if skel_counts.get(skel, 0) >= 80:
            continue
        selected.append(row)
        sem_counts[sem] = sem_counts.get(sem, 0) + 1
        motif_counts[motif] = motif_counts.get(motif, 0) + 1
        skel_counts[skel] = skel_counts.get(skel, 0) + 1
        if len(selected) >= target:
            break
    out = pd.DataFrame(selected)
    if out.empty:
        return out
    out["company_shard"] = [f"shard_{i // 200:02d}" for i in range(len(out))]
    return out


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    m55r2 = read_json(A7FF55R2)
    if m55r2.get("decision") != "PASS_A7FF55R2_ATLAS_FIELD_FAMILY_GENERATION_REPAIR_READY_NO_GENERATION_EXEC":
        raise SystemExit(f"A7FF-55R2 is not ready: {m55r2.get('decision')}")
    seeds = pd.read_csv(SEEDS)
    pair_patch = pd.read_csv(PAIR_PATCH)
    pool = build_pool(seeds, pair_patch)
    queue = select_balanced_queue(pool, target=2400)
    family_summary = (
        pool.groupby(["semantic_pair", "motif"], dropna=False)
        .size()
        .reset_index(name="formula_count")
        .sort_values("formula_count", ascending=False)
    )
    queue_summary = (
        queue.groupby(["semantic_pair", "motif"], dropna=False)
        .size()
        .reset_index(name="queue_count")
        .sort_values("queue_count", ascending=False)
        if not queue.empty
        else pd.DataFrame(columns=["semantic_pair", "motif", "queue_count"])
    )
    pool.to_csv(RUNTIME / "a7ff55r3_repaired_formula_index.csv", index=False)
    queue.to_csv(RUNTIME / "a7ff55r3_repaired_materialization_queue.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ff55r3_formula_family_summary.csv", index=False)
    queue_summary.to_csv(RUNTIME / "a7ff55r3_queue_summary.csv", index=False)

    required_pairs = {
        "open_interest_like|positioning_like",
        "taker_flow_like|open_interest_like",
        "liquidity_like|volatility_like",
    }
    present_pairs = set(queue["semantic_pair"].dropna().astype(str)) if not queue.empty else set()
    blockers = sorted([f"{pair}_missing_from_queue" for pair in required_pairs - present_pairs])
    decision = "PASS_A7FF55R3_REPAIRED_ATLAS_DRY_GENERATION_READY_FOR_COVERAGE_AUDIT" if not blockers else "HOLD_A7FF55R3_REPAIRED_ATLAS_DRY_GENERATION_INCOMPLETE"
    manifest = {
        "stage": "A7FF-55R3",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "formula_count": int(len(pool)),
        "queue_count": int(len(queue)),
        "queue_semantic_pair_count": int(queue["semantic_pair"].nunique()) if not queue.empty else 0,
        "queue_motif_count": int(queue["motif"].nunique()) if not queue.empty else 0,
        "required_pairs_present": sorted(required_pairs & present_pairs),
        "next_allowed": "A7FF-55R4 repaired atlas coverage audit" if not blockers else "A7FF-55R2 repair revision",
        "executes_generation": True,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_numeric": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff55r3_manifest.json", manifest)
    report = f"""# CRYPTO A7FF-55R3 REPAIRED ATLAS DRY GENERATION

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-55R3 executes dry generation only. It produces a repaired formula atlas and materialization queue, but does not run numeric evaluation, replay, or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Formula Family Summary

{md_table(family_summary, 80)}

## Queue Summary

{md_table(queue_summary, 80)}

## Boundary

```text
dry generation executed: true
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
