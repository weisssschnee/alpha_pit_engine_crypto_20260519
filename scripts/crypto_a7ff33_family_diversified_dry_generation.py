from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff33_family_diversified_dry_generation"
REPORT = REPO / "reports" / "CRYPTO_A7FF33_FAMILY_DIVERSIFIED_DRY_GENERATION_20260530.md"

A7FF32_MANIFEST = REPO / "runtime" / "a7ff32_family_diversification_contract" / "a7ff32_manifest.json"
A7FF32_SCALE = REPO / "runtime" / "a7ff32_family_diversification_contract" / "a7ff32_generation_scale_policy.json"
A7FF32_QUOTA = REPO / "runtime" / "a7ff32_family_diversification_contract" / "a7ff32_allowed_family_quota.csv"


FIELDS: dict[str, list[str]] = {
    "basis_premium_like": ["mark_index_basis_bps", "premium_close_bps", "index_close", "mark_close"],
    "open_interest_like": ["open_interest_last", "open_interest_value_last", "open_interest_change_24h", "oi_x_price_move_24h"],
    "positioning_like": [
        "global_long_short_account_ratio_last",
        "global_long_short_account_ratio_mean",
        "top_long_short_account_ratio_last",
        "top_long_short_position_ratio_last",
        "taker_buy_sell_volume_ratio_last",
    ],
    "taker_flow_like": ["taker_buy_sell_volume_ratio_last", "taker_buy_sell_volume_ratio_mean", "taker_buy_quote_volume", "taker_buy_volume"],
    "liquidity_like": ["trade_quote_volume", "trade_volume", "trade_count", "liquidity_rank_active_universe", "volume_volatility_ratio_168h"],
    "volatility_like": ["realized_vol_24h", "realized_vol_72h", "realized_vol_168h", "trade_return_24h"],
    "price_return_like": ["trade_return_1h", "trade_return_24h", "trade_close", "index_close", "mark_close"],
    "regime_state": ["rolling_coverage_168h", "raw_latent_state_id", "sqrt_listing_age_days", "age_x_liquidity"],
    "funding_like": ["funding_rate_state_last_ffill_8h", "funding_rate_delta_state_24h", "funding_rate_abs_state_168h_z", "funding_state_x_basis_delta"],
    "listing_age_like": ["sqrt_listing_age_days", "age_x_liquidity", "age_x_volatility"],
    "latent_state": ["raw_latent_state_id", "liquidity_rank_active_universe", "rolling_coverage_168h"],
}

FAMILY_CONFIGS = [
    ("D0_basis_premium_reference", "basis_premium_like", "basis_premium_like", 3600, "reference_family_only"),
    ("D1_open_interest_positioning", "open_interest_like", "positioning_like", 4800, "primary_diversification_target"),
    ("D2_taker_flow_leverage", "taker_flow_like", "open_interest_like", 3600, "primary_diversification_target"),
    ("D3_liquidity_volatility_state", "liquidity_like", "volatility_like", 3600, "primary_diversification_target"),
    ("D4_regime_relative_value", "regime_state", "price_return_like", 3000, "primary_diversification_target"),
    ("D5_funding_dense_state", "funding_like", "basis_premium_like", 3600, "dense_materializer_target"),
    ("D6_listing_latent_lifecycle", "listing_age_like", "latent_state", 1800, "diagnostic_to_signal_bridge"),
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_id(prefix: str, text: str) -> str:
    return f"{prefix}_{hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]}"


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


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


def skeleton(expr: str) -> str:
    import re

    text = re.sub(r"[A-Za-z_][A-Za-z0-9_]*", "TOK", str(expr))
    text = re.sub(r"\d+", "N", text)
    return stable_id("skel", text)


def transforms(field: str, semantic: str) -> list[tuple[str, str]]:
    windows = [1, 2, 4, 8, 12, 24, 48, 72, 168]
    out = [("level", field)]
    for window in windows:
        out.append((f"delta_{window}h", f"Delta({field},{window})"))
        out.append((f"mean_{window}h", f"Mean({field},{window})"))
        out.append((f"zmean_{window}h", f"ZScore(Mean({field},{window}))"))
    if semantic in {"basis_premium_like", "funding_like", "positioning_like", "open_interest_like", "volatility_like"}:
        for window in [8, 24, 72, 168]:
            out.append((f"abs_zmean_{window}h", f"Abs(ZScore(Mean({field},{window})))"))
            out.append((f"decay_{window}h", f"Decay({field},{window})"))
    out.extend(
        [
            ("csrank", f"CSRank({field})"),
            ("rank", f"Rank({field})"),
            ("sign_delta_24h", f"Sign(Delta({field},24))"),
            ("clip_zscore", f"Clip(ZScore({field}),-3,3)"),
        ]
    )
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
    if motif == "smooth_mul":
        return f"Mean(Mul({left},{right}),4)"
    if motif == "relative_shock":
        return f"Mul(Delta({left},4),ZScore({right}))"
    if motif == "signed_spread":
        return f"Mul(Sub(CSRank({left}),CSRank({right})),Sign({right}))"
    if motif == "mean_reversion_gate":
        return f"Mul(Neg(ZScore({left})),Sign({right}))"
    if motif == "safe_div_clip":
        return f"Clip(SafeDiv({left},Abs({right})),-5,5)"
    if motif == "zspread":
        return f"Sub(ZScore({left}),ZScore({right}))"
    return f"Mul({left},{right})"


def build_family(family_id: str, left_semantic: str, right_semantic: str, target: int, role: str) -> list[dict[str, Any]]:
    motifs = ["mul", "sub", "spread_rank", "gated_sign", "smooth_mul", "relative_shock", "signed_spread", "mean_reversion_gate", "safe_div_clip", "zspread"]
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    left_fields = FIELDS[left_semantic]
    right_fields = FIELDS[right_semantic]
    left_transforms = [(field, name, expr) for field in left_fields for name, expr in transforms(field, left_semantic)]
    right_transforms = [(field, name, expr) for field in right_fields for name, expr in transforms(field, right_semantic)]

    # Deterministic nested traversal. It is intentionally broad, not score-ranked.
    for lf, lt, le in left_transforms:
        for rf, rt, re in right_transforms:
            for motif in motifs:
                if len(rows) >= target:
                    return rows
                expr = interaction(le, re, motif)
                if expr in seen:
                    continue
                seen.add(expr)
                level = "L2_typed_two_field_interaction"
                if left_semantic in {"regime_state", "listing_age_like"} or right_semantic in {"regime_state", "latent_state"}:
                    level = "L3_state_conditioned_feature"
                if motif in {"safe_div_clip", "zspread", "mean_reversion_gate"}:
                    level = "L4_factor_candidate_probe"
                semantic_pair = f"{left_semantic}|{right_semantic}"
                production_key = stable_id("prod", f"{family_id}|{lf}|{rf}|{lt}|{rt}|{motif}")
                rows.append(
                    {
                        "level": level,
                        "family_id": family_id,
                        "root_family": semantic_pair,
                        "primary_field": lf,
                        "secondary_field": rf,
                        "primary_semantic": left_semantic,
                        "secondary_semantic": right_semantic,
                        "primary_route": role,
                        "secondary_route": role,
                        "primary_transform": lt,
                        "secondary_transform": rt,
                        "motif": motif,
                        "expression": expr,
                        "semantic_pair": semantic_pair,
                        "generation_priority": "P0" if "primary" in role else "P1",
                        "candidate_role": "ordinary_alpha_valid_family_diversification_probe",
                        "modifier_guard_required": role != "reference_family_only",
                        "skeleton_key": skeleton(expr),
                        "production_key": production_key,
                        "blueprint_id": stable_id("a7ff33", f"{family_id}|{expr}"),
                    }
                )
    return rows


def balanced_queue(pool: pd.DataFrame, target: int, family_order: list[str]) -> pd.DataFrame:
    parts = []
    remaining = target
    per_family = max(1, target // max(1, len(family_order)))
    for family_id in family_order:
        family_pool = pool[pool["family_id"].eq(family_id)].copy()
        motif_parts = []
        motifs = sorted(family_pool["motif"].dropna().unique().tolist())
        per_motif = max(1, per_family // max(1, len(motifs)))
        for motif in motifs:
            motif_parts.append(family_pool[family_pool["motif"].eq(motif)].head(per_motif).copy())
        part = pd.concat(motif_parts, ignore_index=True) if motif_parts else pd.DataFrame()
        if len(part) < per_family:
            extra = family_pool[~family_pool["blueprint_id"].isin(set(part["blueprint_id"]))].head(per_family - len(part))
            part = pd.concat([part, extra], ignore_index=True)
        part = part.head(per_family).copy()
        parts.append(part)
        remaining -= len(part)
    queue = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    if remaining > 0:
        extra = pool[~pool["blueprint_id"].isin(set(queue["blueprint_id"]))].head(remaining)
        queue = pd.concat([queue, extra], ignore_index=True)
    return queue.head(target).copy()


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    f32 = read_json(A7FF32_MANIFEST)
    if not f32.get("authorizes_a7ff33_family_diversified_dry_generation"):
        raise SystemExit(f"A7FF-32 does not authorize A7FF-33: {f32.get('decision')}")
    scale = read_json(A7FF32_SCALE)
    quota = pd.read_csv(A7FF32_QUOTA)

    rows: list[dict[str, Any]] = []
    for family_id, left, right, target, role in FAMILY_CONFIGS:
        rows.extend(build_family(family_id, left, right, target, role))
    pool = pd.DataFrame(rows).drop_duplicates("expression").reset_index(drop=True)
    target = int(scale.get("generated_blueprint_target", 24000))
    if len(pool) > target:
        pool = pool.head(target).copy()
    pool.to_csv(RUNTIME / "a7ff33_blueprint_pool.csv", index=False)

    family_order = [cfg[0] for cfg in FAMILY_CONFIGS]
    materialization = balanced_queue(pool, int(scale.get("materialization_queue_target", 6000)), family_order)
    company = balanced_queue(pool, int(scale.get("company_wave_queue_target", 3600)), family_order)
    shard_count = int(scale.get("company_shard_count", 18))
    company = company.copy()
    company["company_shard"] = [f"shard_{idx % shard_count:02d}" for idx in range(len(company))]
    materialization.to_csv(RUNTIME / "a7ff33_materialization_queue.csv", index=False)
    company.to_csv(RUNTIME / "a7ff33_company_numeric_wave_queue.csv", index=False)

    for shard, part in company.groupby("company_shard", sort=True):
        part.to_csv(RUNTIME / f"a7ff33_{shard}_queue.csv", index=False)

    family_summary = (
        pool.groupby(["family_id", "root_family", "level"], dropna=False)
        .agg(
            formula_count=("blueprint_id", "count"),
            skeleton_count=("skeleton_key", "nunique"),
            motif_count=("motif", "nunique"),
            primary_field_count=("primary_field", "nunique"),
            secondary_field_count=("secondary_field", "nunique"),
        )
        .reset_index()
        .sort_values(["family_id", "level"])
    )
    family_summary.to_csv(RUNTIME / "a7ff33_formula_family_summary.csv", index=False)

    queue_summary = (
        company.groupby(["family_id", "root_family"], dropna=False)
        .agg(company_wave_count=("blueprint_id", "count"), skeleton_count=("skeleton_key", "nunique"), motif_count=("motif", "nunique"))
        .reset_index()
        .sort_values("company_wave_count", ascending=False)
    )
    queue_summary.to_csv(RUNTIME / "a7ff33_company_queue_summary.csv", index=False)

    shard_plan = (
        company.groupby("company_shard", dropna=False)
        .agg(row_count=("blueprint_id", "count"), family_count=("family_id", "nunique"), motif_count=("motif", "nunique"), skeleton_count=("skeleton_key", "nunique"))
        .reset_index()
        .sort_values("company_shard")
    )
    shard_plan.to_csv(RUNTIME / "a7ff33_company_shard_plan.csv", index=False)

    root_counts = company["root_family"].value_counts(normalize=True)
    basis_share = float(root_counts.get("basis_premium_like|basis_premium_like", 0.0))
    non_basis_share = 1.0 - basis_share
    warnings: list[str] = []
    blockers: list[str] = []
    if len(pool) < target:
        warnings.append("generated_pool_below_target")
    if non_basis_share < float(scale.get("min_non_basis_company_wave_share", 0.65)):
        blockers.append("non_basis_company_wave_share_below_contract")
    if company["family_id"].nunique() < int(scale.get("min_root_family_count", 6)):
        blockers.append("family_count_below_contract")
    if company["motif"].nunique() < int(scale.get("min_motif_count", 10)):
        blockers.append("motif_count_below_contract")

    decision = "PASS_A7FF33_FAMILY_DIVERSIFIED_DRY_GENERATION_BUILT_NO_NUMERIC_NO_SEARCH_AUTH" if not blockers else "HOLD_A7FF33_DRY_GENERATION_CONTRACT_FAIL"
    manifest = {
        "stage": "A7FF-33",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "source_a7ff32_decision": f32.get("decision"),
        "blueprint_count": int(len(pool)),
        "materialization_queue_count": int(len(materialization)),
        "company_wave_queue_count": int(len(company)),
        "company_shard_count": shard_count,
        "family_count": int(company["family_id"].nunique()),
        "motif_count": int(company["motif"].nunique()),
        "company_wave_basis_root_share": basis_share,
        "company_wave_non_basis_share": non_basis_share,
        "executes_generation": True,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff34_queue_coverage_audit": not blockers,
        "authorizes_numeric_probe": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff33_manifest.json", manifest)
    write_json(RUNTIME / "a7ff33_decision_record.json", manifest)
    write_json(RUNTIME / "a7ff33_generation_policy.json", {"scale": scale, "quota": quota.to_dict("records")})

    report = f"""# CRYPTO A7FF-33 FAMILY-DIVERSIFIED DRY GENERATION

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-33 builds a larger family-diversified formula asset pool. It executes dry generation only; no numeric probe, replay, search, alpha proof, shadow, paper, or live execution is authorized.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Family Summary

{md_table(family_summary)}

## Company Queue Summary

{md_table(queue_summary)}

## Shard Plan

{md_table(shard_plan)}

## Boundary

```text
dry generation executed: true
numeric probe executed: false
replay executed: false
search executed: false
May used: false
next if PASS: A7FF-34 queue coverage audit
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
