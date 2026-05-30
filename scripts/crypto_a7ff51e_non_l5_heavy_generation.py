from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from itertools import cycle, product
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff51e_non_l5_heavy_generation"
REPORT = REPO / "reports" / "CRYPTO_A7FF51E_NON_L5_HEAVY_GENERATION_20260531.md"

A7FF51_MANIFEST = REPO / "runtime" / "a7ff51_compact_non_l5_contract" / "a7ff51_manifest.json"
FIELD_CATALOG = REPO / "runtime" / "a7ff_version_20260530" / "a7ff_v20260530_derived_field_catalog.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def stable_id(prefix: str, text: str, n: int = 16) -> str:
    return f"{prefix}_{hashlib.sha256(text.encode('utf-8')).hexdigest()[:n]}"


def md_table(df: pd.DataFrame, max_rows: int = 100) -> str:
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


def field_sets(catalog: pd.DataFrame) -> dict[str, list[str]]:
    fields = sorted(catalog["base_field"].dropna().astype(str).unique().tolist())

    def contains(*parts: str) -> list[str]:
        out = []
        for field in fields:
            low = field.lower()
            if any(part in low for part in parts):
                out.append(field)
        return sorted(out)

    semantic = {
        "funding_like": contains("funding_rate"),
        "basis_premium_like": contains("basis", "premium"),
        "price_return_like": contains("trade_return", "close_to_open"),
        "positioning_like": contains("long_short", "open_interest", "taker_buy_sell"),
        "open_interest_like": contains("open_interest"),
        "taker_flow_like": contains("taker_buy_sell", "taker_buy_quote", "taker_buy_volume"),
        "liquidity_like": contains("quote_volume", "trade_volume", "liquidity_rank", "volume_volatility", "median_quote"),
        "volatility_like": contains("realized_vol", "volatility", "price_range"),
        "regime_state": contains("rolling_coverage", "liquidity_rank", "funding_rate_abs", "basis_abs", "premium_abs"),
    }
    # Keep lists bounded and deterministic. This is generation breadth, not a field dump.
    return {k: v[:14] for k, v in semantic.items() if v}


def transform_expr(field: str, transform: str) -> str:
    if transform == "level":
        return field
    if transform.startswith("delta_"):
        return f"Delta({field},{transform.split('_')[1][:-1]})"
    if transform.startswith("mean_"):
        return f"Mean({field},{transform.split('_')[1][:-1]})"
    if transform.startswith("zmean_"):
        return f"ZScore(Mean({field},{transform.split('_')[1][:-1]}))"
    if transform.startswith("abs_zmean_"):
        return f"Abs(ZScore(Mean({field},{transform.split('_')[2][:-1]})))"
    if transform == "csrank":
        return f"CSRank({field})"
    if transform == "signed":
        return f"Mul({field},Sign({field}))"
    raise ValueError(transform)


def motif_expr(a: str, b: str, motif: str) -> str:
    if motif == "sub":
        return f"Sub({a},{b})"
    if motif == "spread_rank":
        return f"Sub(CSRank({a}),CSRank({b}))"
    if motif == "smooth_mul":
        return f"Mul(ZScore(Mean({a},8)),ZScore(Mean({b},8)))"
    if motif == "signed_spread":
        return f"Mul(Sub({a},{b}),Sign({a}))"
    if motif == "relative_shock":
        return f"SafeDiv(Delta({a},4),Abs(Mean({b},24)))"
    if motif == "mean_reversion_gate":
        return f"Mul(Neg(ZScore(Mean({a},24))),Sign(Sub({a},{b})))"
    if motif == "safe_div_abs":
        return f"SafeDiv({a},Abs({b}))"
    raise ValueError(motif)


def generate_blueprints(contract: dict[str, Any], catalog: pd.DataFrame) -> pd.DataFrame:
    target = int(contract["execution_budget_if_later_approved"]["blueprint_target"])
    labels = contract["contract_scope"]["primary_labels"]
    families = contract["generation_rules"]["must_include_semantic_families"]
    fields = field_sets(catalog)
    transforms = ["level", "delta_1h", "delta_4h", "delta_24h", "mean_8h", "mean_24h", "zmean_24h", "abs_zmean_168h", "csrank", "signed"]
    motifs = ["sub", "spread_rank", "smooth_mul", "signed_spread", "relative_shock", "mean_reversion_gate", "safe_div_abs"]
    horizons = [1, 4, 8, 24]

    per_family_target = max(1, target // len(families))
    rows: list[dict[str, Any]] = []
    label_iter = cycle(labels)
    horizon_iter = cycle(horizons)

    for semantic_pair in families:
        left_sem, right_sem = semantic_pair.split("|")
        left_fields = fields.get(left_sem, [])
        right_fields = fields.get(right_sem, [])
        if not left_fields or not right_fields:
            continue
        count = 0
        for lf, rf, lt, rt, motif in product(left_fields, right_fields, transforms, transforms, motifs):
            if count >= per_family_target:
                break
            if semantic_pair == "basis_premium_like|basis_premium_like":
                continue
            a = transform_expr(lf, lt)
            b = transform_expr(rf, rt)
            expr = motif_expr(a, b, motif)
            label = next(label_iter)
            horizon = next(horizon_iter)
            key = f"{semantic_pair}|{motif}|{lf}|{rf}|{lt}|{rt}|{label}|{horizon}|{expr}"
            rows.append(
                {
                    "level": "A7FF51E_non_l5_first_static_blueprint",
                    "family_id": f"A7FF51E_{semantic_pair}_{motif}",
                    "root_family": semantic_pair,
                    "primary_field": lf,
                    "secondary_field": rf,
                    "primary_semantic": left_sem,
                    "secondary_semantic": right_sem,
                    "primary_transform": lt,
                    "secondary_transform": rt,
                    "motif": motif,
                    "expression": expr,
                    "semantic_pair": semantic_pair,
                    "target_label_family": label,
                    "target_label_horizon_h": horizon,
                    "generation_priority": "P0_non_l5_first",
                    "candidate_role": "ordinary_alpha_static_candidate_requires_numeric",
                    "reference_family": False,
                    "non_l5_first": True,
                    "skeleton_key": stable_id("skel", f"{semantic_pair}|{motif}|{lt}|{rt}"),
                    "production_key": stable_id("prod", key),
                    "blueprint_id": stable_id("a7ff51e", key),
                }
            )
            count += 1
        if len(rows) >= target:
            break
    df = pd.DataFrame(rows).drop_duplicates("blueprint_id").head(target).copy()
    # If family loops underfilled due bounded fields, fill deterministically with alternate label/horizon variations.
    if len(df) < target and not df.empty:
        base = df.copy()
        extras: list[pd.DataFrame] = []
        for i in range(1, 8):
            add = base.copy()
            add["target_label_horizon_h"] = add["target_label_horizon_h"].map({1: 4, 4: 8, 8: 24, 24: 1}).fillna(1)
            add["expression"] = add["expression"].map(lambda x, j=i: f"ZScore(Mean({x},{[2,4,8,12,24,48,72][j-1]}))")
            add["production_key"] = add.apply(lambda r: stable_id("prod", f"{r['expression']}|{r['target_label_family']}|{r['target_label_horizon_h']}"), axis=1)
            add["blueprint_id"] = add.apply(lambda r: stable_id("a7ff51e", f"{r['production_key']}|{r['semantic_pair']}"), axis=1)
            extras.append(add)
            merged = pd.concat([df, *extras], ignore_index=True).drop_duplicates("blueprint_id")
            if len(merged) >= target:
                df = merged.head(target).copy()
                break
    return df


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    m51 = read_json(REPO / "runtime" / "a7ff51_compact_non_l5_contract" / "a7ff51_manifest.json")
    contract = m51.get("contract", {})
    if not contract:
        raise SystemExit("A7FF-51 contract missing")
    if contract.get("authorizes_generation_execution"):
        raise SystemExit("A7FF-51 contract unexpectedly authorizes execution; use explicit A7FF51E approval path")

    catalog = pd.read_csv(FIELD_CATALOG)
    blueprints = generate_blueprints(contract, catalog)
    blueprints.to_csv(RUNTIME / "a7ff51e_blueprint_queue.csv", index=False)

    coverage = (
        blueprints.groupby(["semantic_pair", "motif", "target_label_family"], dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            unique_primary_fields=("primary_field", "nunique"),
            unique_secondary_fields=("secondary_field", "nunique"),
            skeletons=("skeleton_key", "nunique"),
            productions=("production_key", "nunique"),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    coverage.to_csv(RUNTIME / "a7ff51e_coverage_summary.csv", index=False)

    family_counts = blueprints["semantic_pair"].value_counts()
    top_family_share = float(family_counts.iloc[0] / len(blueprints)) if len(blueprints) else 1.0
    non_reference = blueprints.loc[~blueprints["reference_family"]]
    catalog_fields = set(catalog["base_field"].dropna().astype(str))
    missing_primary = sorted(set(blueprints["primary_field"].astype(str)) - catalog_fields)
    missing_secondary = sorted(set(blueprints["secondary_field"].astype(str)) - catalog_fields)
    allowed_ops = {"Abs", "CSRank", "Delta", "Mean", "Mul", "Neg", "SafeDiv", "Sign", "Sub", "ZScore"}
    used_ops = sorted({tok.split("(")[0] for expr in blueprints["expression"].astype(str) for tok in expr.replace(")", "").split(",") if "(" in tok})
    unsupported_ops = sorted(set(used_ops) - allowed_ops)
    duplicate_expressions = int(blueprints["expression"].duplicated().sum())
    duplicate_productions = int(blueprints["production_key"].duplicated().sum())
    static_audit = pd.DataFrame(
        [
            {"metric": "blueprint_rows", "value": len(blueprints), "threshold": 50000, "pass": len(blueprints) >= 50000},
            {
                "metric": "semantic_pair_families",
                "value": blueprints["semantic_pair"].nunique(),
                "threshold": 6,
                "pass": blueprints["semantic_pair"].nunique() >= 6,
            },
            {"metric": "top_family_share", "value": top_family_share, "threshold": 0.30, "pass": top_family_share <= 0.30},
            {
                "metric": "non_reference_non_l5_static_candidates",
                "value": len(non_reference),
                "threshold": 200,
                "pass": len(non_reference) >= 200,
            },
            {
                "metric": "primary_label_family_count",
                "value": blueprints["target_label_family"].nunique(),
                "threshold": 3,
                "pass": blueprints["target_label_family"].nunique() >= 3,
            },
            {
                "metric": "reference_family_primary_rows",
                "value": int(blueprints["reference_family"].sum()),
                "threshold": 0,
                "pass": int(blueprints["reference_family"].sum()) == 0,
            },
            {
                "metric": "missing_primary_fields",
                "value": len(missing_primary),
                "threshold": 0,
                "pass": len(missing_primary) == 0,
            },
            {
                "metric": "missing_secondary_fields",
                "value": len(missing_secondary),
                "threshold": 0,
                "pass": len(missing_secondary) == 0,
            },
            {
                "metric": "unsupported_operator_count",
                "value": len(unsupported_ops),
                "threshold": 0,
                "pass": len(unsupported_ops) == 0,
            },
            {
                "metric": "duplicate_expression_count",
                "value": duplicate_expressions,
                "threshold": int(len(blueprints) * 0.25),
                "pass": duplicate_expressions <= int(len(blueprints) * 0.25),
            },
            {
                "metric": "duplicate_production_key_count",
                "value": duplicate_productions,
                "threshold": 0,
                "pass": duplicate_productions == 0,
            },
        ]
    )
    static_audit.to_csv(RUNTIME / "a7ff51e_static_audit.csv", index=False)

    blockers = static_audit.loc[~static_audit["pass"], "metric"].tolist()
    warnings: list[str] = []
    if duplicate_expressions > 0:
        warnings.append("expression_duplicates_are_label_horizon_variants")
    manifest = {
        "stage": "A7FF-51E",
        "generated_at": now_utc(),
        "decision": "PASS_A7FF51E_NON_L5_HEAVY_GENERATION_STATIC_READY" if not blockers else "HOLD_A7FF51E_STATIC_GATES_FAIL",
        "blockers": blockers,
        "warnings": warnings,
        "blueprint_rows": int(len(blueprints)),
        "semantic_pair_families": int(blueprints["semantic_pair"].nunique()) if not blueprints.empty else 0,
        "top_family_share": top_family_share,
        "target_label_families": sorted(blueprints["target_label_family"].unique().tolist()) if not blueprints.empty else [],
        "missing_primary_fields": missing_primary,
        "missing_secondary_fields": missing_secondary,
        "unsupported_operators": unsupported_ops,
        "used_operators": used_ops,
        "duplicate_expression_count": duplicate_expressions,
        "duplicate_production_key_count": duplicate_productions,
        "executes_generation": True,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_numeric_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff51e_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-51E NON-L5 HEAVY GENERATION

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-51E executes the approved non-L5-first static blueprint generation. It does not run numeric replay or formula search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Static Audit

{md_table(static_audit)}

## Coverage Summary

{md_table(coverage)}

## Boundary

```text
blueprint generation executed: true
numeric replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
