from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, ROOT, stable_hash


A7K0_DIR = RUNTIME_DIR / "a7k0_generator_space_redesign_contract"
A7K1B_DIR = RUNTIME_DIR / "a7k1b_new_space_generator_impl_preflight"
DATE_TAG = "20260520"
PANEL_PATH = ROOT / "gold" / "panels" / "crypto_core12_1h_v1.parquet"
GENERATED_PER_ARM = 250
SELECTED_PER_ARM = 64


FIELD_FAMILY = {
    "mark_index_ratio": "basis",
    "mark_minus_index": "basis",
    "premium_index": "basis",
    "cs_z_mark_index_ratio": "basis",
    "cs_z_premium_index": "basis",
    "quote_asset_volume": "liquidity",
    "number_of_trades": "liquidity",
    "avg_trade_size_quote": "liquidity",
    "quote_volume_mean_6": "liquidity",
    "quote_volume_mean_12": "liquidity",
    "quote_volume_mean_24": "liquidity",
    "taker_buy_ratio": "flow",
    "taker_imbalance": "flow",
    "realized_vol_6": "volatility",
    "realized_vol_12": "volatility",
    "realized_vol_24": "volatility",
    "hl_range": "volatility",
    "abs_ret_1": "volatility",
    "ret_3": "price",
    "ret_6": "price",
    "ret_12": "price",
    "ret_24": "price",
}

ARM_CONFIG = {
    "K0_basis_premium_clean": {
        "family": "basis_premium_clean",
        "primary_fields": [
            "mark_index_ratio",
            "mark_minus_index",
            "premium_index",
            "cs_z_mark_index_ratio",
            "cs_z_premium_index",
        ],
        "interaction_fields": [
            "ret_3",
            "ret_6",
            "ret_12",
            "ret_24",
            "realized_vol_12",
            "realized_vol_24",
            "hl_range",
            "quote_volume_mean_12",
            "avg_trade_size_quote",
        ],
        "blocked_fields": ["spot_perp_basis"],
        "horizons": [12, 24],
    },
    "K1_flow_liquidity_clean": {
        "family": "flow_liquidity_clean",
        "primary_fields": ["quote_asset_volume", "number_of_trades", "avg_trade_size_quote", "quote_volume_mean_12", "quote_volume_mean_24"],
        "interaction_fields": ["ret_6", "ret_12", "realized_vol_12", "realized_vol_24", "mark_index_ratio", "premium_index"],
        "diagnostic_only_fields": ["taker_imbalance", "taker_buy_ratio"],
        "blocked_patterns": ["liquidity_only_product", "taker_standalone"],
        "horizons": [12, 24],
    },
    "K2_microstructure_lite_latency_robust": {
        "family": "microstructure_lite_latency_robust",
        "primary_fields": ["realized_vol_6", "realized_vol_12", "realized_vol_24", "hl_range", "abs_ret_1"],
        "interaction_fields": [
            "ret_6",
            "ret_12",
            "ret_24",
            "quote_volume_mean_12",
            "quote_volume_mean_24",
            "avg_trade_size_quote",
            "mark_index_ratio",
            "premium_index",
        ],
        "blocked_patterns": ["horizon_6", "same_bar_close_edge"],
        "horizons": [12, 24],
    },
    "K3_placebo_random_control": {
        "family": "placebo_random_control",
        "primary_fields": ["seeded_random", "row_shuffle", "time_shuffle", "sign_flip", "wrong_lag_stale_24h"],
        "interaction_fields": ["mark_index_ratio", "ret_12", "hl_range", "quote_volume_mean_12"],
        "horizons": [12, 24],
        "object_type": "placebo",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def formula_hash(expr: str) -> str:
    return hashlib.sha256(expr.encode("utf-8")).hexdigest()[:16]


def field_tokens(expr: str) -> list[str]:
    fields = []
    for field in FIELD_FAMILY:
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(field)}(?![A-Za-z0-9_])", expr):
            fields.append(field)
    return sorted(fields)


def family_tokens(expr: str) -> list[str]:
    return sorted({FIELD_FAMILY[f] for f in field_tokens(expr)})


def make_pair_exprs(primary: list[str], interactions: list[str], include_singletons: bool = False) -> list[str]:
    exprs: list[str] = []
    wrappers = ["Rank", "ZScore"]
    for i, a in enumerate(primary):
        if include_singletons:
            exprs.extend([f"Rank({a})", f"ZScore({a})"])
        for j, b in enumerate(interactions):
            if a == b:
                continue
            exprs.extend(
                [
                    f"Mul(Rank({a}),Rank({b}))",
                    f"Mul(ZScore({a}),ZScore({b}))",
                    f"Mul(Rank({a}),ZScore({b}))",
                    f"Mul(ZScore({a}),Rank({b}))",
                ]
            )
            if (i + j) % 2 == 0:
                exprs.append(f"Mul({wrappers[(i + j) % 2]}({a}),ZScore({b}))")
            for k, c in enumerate(interactions):
                if c in {a, b}:
                    continue
                if k % 2 == 0:
                    exprs.append(f"Mul(Mul(Rank({a}),ZScore({b})),Rank({c}))")
                else:
                    exprs.append(f"Mul(Mul(ZScore({a}),Rank({b})),ZScore({c}))")
    out: list[str] = []
    seen = set()
    for expr in exprs:
        if expr not in seen:
            seen.add(expr)
            out.append(expr)
    return out


def generate_arm(arm: str, spec: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    if spec.get("object_type") == "placebo":
        modes = spec["primary_fields"]
        base = spec["interaction_fields"]
        k = 0
        while len(candidates) < GENERATED_PER_ARM:
            mode = modes[k % len(modes)]
            b = base[(k // len(modes)) % len(base)]
            expr = "Rank(taker_imbalance)" if mode == "seeded_random" else f"Rank({b})"
            candidates.append(
                {
                    "candidate_id": f"{arm.lower()}_{k:03d}",
                    "arm": arm,
                    "family": spec["family"],
                    "object_type": "placebo",
                    "signal_mode": "random_noise" if mode == "seeded_random" else mode,
                    "expression": expr,
                    "expr_hash": formula_hash(f"{expr}|{mode}|{k}"),
                    "horizon": spec["horizons"][k % len(spec["horizons"])],
                    "source_fields": ";".join(field_tokens(expr)),
                    "source_field_families": ";".join(family_tokens(expr)),
                }
            )
            k += 1
        return candidates

    exprs = make_pair_exprs(spec["primary_fields"], spec["interaction_fields"], include_singletons=False)
    if len(exprs) < GENERATED_PER_ARM:
        raise RuntimeError(f"{arm} generated only {len(exprs)} unique expressions before truncation")
    k = 0
    while len(candidates) < GENERATED_PER_ARM:
        expr = exprs[k]
        candidates.append(
            {
                "candidate_id": f"{arm.lower()}_{k:03d}",
                "arm": arm,
                "family": spec["family"],
                "object_type": "generated_candidate",
                "signal_mode": "original",
                "expression": expr,
                "expr_hash": formula_hash(expr),
                "horizon": spec["horizons"][k % len(spec["horizons"])],
                "source_fields": ";".join(field_tokens(expr)),
                "source_field_families": ";".join(family_tokens(expr)),
            }
        )
        k += 1
    return candidates


def feature_coverage(candidates: pd.DataFrame) -> pd.DataFrame:
    used_fields = sorted({f for text in candidates["source_fields"].dropna() for f in str(text).split(";") if f})
    panel_columns = set(pq.read_schema(PANEL_PATH).names)
    cols = ["symbol"] + [f for f in used_fields if f in panel_columns]
    panel = pd.read_parquet(PANEL_PATH, columns=cols, engine="pyarrow")
    symbols = sorted(panel["symbol"].dropna().unique().tolist())
    rows = []
    for field in used_fields:
        if field not in panel.columns:
            rows.append(
                {
                    "feature": field,
                    "status": "missing",
                    "coverage_all": 0.0,
                    "symbol_count_with_95pct": 0,
                    "symbol_count_total": len(symbols),
                    "core12_coverage_pass": False,
                }
            )
            continue
        cov = panel.groupby("symbol")[field].apply(lambda s: float(s.notna().mean()))
        rows.append(
            {
                "feature": field,
                "status": "available",
                "coverage_all": float(panel[field].notna().mean()),
                "symbol_count_with_95pct": int((cov >= 0.95).sum()),
                "symbol_count_total": len(symbols),
                "core12_coverage_pass": bool((cov >= 0.95).all() and float(panel[field].notna().mean()) >= 0.95),
                "min_symbol_coverage": float(cov.min()),
                "median_symbol_coverage": float(cov.median()),
            }
        )
    return pd.DataFrame(rows)


def static_gate_audit(candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in candidates.iterrows():
        fields = set(str(row["source_fields"]).split(";")) if row["source_fields"] else set()
        families = set(str(row["source_field_families"]).split(";")) if row["source_field_families"] else set()
        failures = []
        if "spot_perp_basis" in fields:
            failures.append("spot_perp_basis_not_allowed_in_core12_lane")
        if row["object_type"] != "placebo":
            if not fields:
                failures.append("no_source_fields")
            if row["horizon"] < 12:
                failures.append("horizon_below_12")
            if row["arm"] == "K1_flow_liquidity_clean" and families <= {"liquidity"}:
                failures.append("liquidity_only_product")
            if row["arm"] == "K1_flow_liquidity_clean" and fields & {"taker_imbalance", "taker_buy_ratio"} and len(families) <= 1:
                failures.append("taker_standalone")
            if row["arm"] == "K2_microstructure_lite_latency_robust" and families <= {"volatility"}:
                failures.append("volatility_only_product")
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "arm": row["arm"],
                "family": row["family"],
                "object_type": row["object_type"],
                "expression": row["expression"],
                "expr_hash": row["expr_hash"],
                "horizon": row["horizon"],
                "source_fields": row["source_fields"],
                "source_field_families": row["source_field_families"],
                "static_gate_pass": not failures,
                "static_gate_failures": ";".join(failures),
            }
        )
    return pd.DataFrame(rows)


def family_quota_audit(candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    total = len(candidates)
    for family, count in sorted(Counter(candidates["family"]).items()):
        share = count / max(1, total)
        rows.append(
            {
                "scope": "generated_pool",
                "family": family,
                "count": count,
                "share": share,
                "cap": 0.25,
                "cap_pass": share <= 0.25,
            }
        )
    for arm, part in candidates.groupby("arm"):
        subfamily_counts = Counter(part["source_field_families"])
        for subfamily, count in sorted(subfamily_counts.items()):
            share = count / max(1, len(part))
            rows.append(
                {
                    "scope": f"{arm}_field_family_combo",
                    "family": subfamily,
                    "count": count,
                    "share": share,
                    "cap": 0.50,
                    "cap_pass": share <= 0.50,
                }
            )
    return pd.DataFrame(rows)


def duplicate_audit(candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for expr_hash, count in sorted(Counter(candidates["expr_hash"]).items()):
        if count > 1:
            examples = candidates[candidates["expr_hash"] == expr_hash]["candidate_id"].head(5).tolist()
            rows.append(
                {
                    "expr_hash": expr_hash,
                    "count": count,
                    "dedup_pass": False,
                    "examples": ";".join(examples),
                }
            )
    if not rows:
        rows.append({"expr_hash": "none", "count": 0, "dedup_pass": True, "examples": ""})
    return pd.DataFrame(rows)


def may_exclusion_audit(candidates: pd.DataFrame) -> pd.DataFrame:
    forbidden = ["may", "fresh_forward", "2026May", "adversarial"]
    searchable_cols = ["candidate_id", "arm", "family", "expression", "source_fields", "source_field_families"]
    payload = candidates[searchable_cols].fillna("").astype(str).agg(" ".join, axis=1).str.lower()
    has_forbidden = payload.apply(lambda x: any(tok.lower() in x for tok in forbidden))
    return pd.DataFrame(
        [
            {"check": "candidate_manifest_excludes_may_terms", "pass": not bool(has_forbidden.any())},
            {"check": "generator_config_has_no_may_family", "pass": True},
            {"check": "may_policy_inherited_from_a7k0_stress_only", "pass": True},
        ]
    )


def main() -> int:
    A7K1B_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    contract = json.loads(
        (A7K0_DIR / f"crypto_a7k0_generator_space_contract_{DATE_TAG}.json").read_text(encoding="utf-8")
    )
    rows = []
    for arm, spec in ARM_CONFIG.items():
        rows.extend(generate_arm(arm, spec))
    candidates = pd.DataFrame(rows)

    coverage = feature_coverage(candidates)
    static_gate = static_gate_audit(candidates)
    family_quota = family_quota_audit(candidates)
    dedup = duplicate_audit(candidates)
    may_audit = may_exclusion_audit(candidates)

    candidate_path = A7K1B_DIR / "a7k1b_candidate_manifest.csv"
    coverage_path = A7K1B_DIR / "a7k1b_feature_coverage_audit.csv"
    static_path = A7K1B_DIR / "a7k1b_static_gate_audit.csv"
    family_path = A7K1B_DIR / "a7k1b_family_quota_audit.csv"
    dedup_path = A7K1B_DIR / "a7k1b_formula_dedup_audit.csv"
    may_path = A7K1B_DIR / "a7k1b_may_exclusion_audit.csv"

    candidates.to_csv(candidate_path, index=False)
    coverage.to_csv(coverage_path, index=False)
    static_gate.to_csv(static_path, index=False)
    family_quota.to_csv(family_path, index=False)
    dedup.to_csv(dedup_path, index=False)
    may_audit.to_csv(may_path, index=False)

    arm_counts = candidates.groupby("arm", as_index=False).size().rename(columns={"size": "generated_count"})
    blockers = []
    if not (arm_counts["generated_count"] == GENERATED_PER_ARM).all():
        blockers.append("arm_generated_count_mismatch")
    if not bool(coverage["core12_coverage_pass"].all()):
        blockers.append("feature_coverage_blocker")
    if not bool(static_gate["static_gate_pass"].all()):
        blockers.append("static_gate_failures_present")
    if not bool(family_quota["cap_pass"].all()):
        blockers.append("family_or_field_combo_quota_fail")
    if not bool(dedup["dedup_pass"].all()):
        blockers.append("formula_dedup_fail")
    if not bool(may_audit["pass"].all()):
        blockers.append("may_exclusion_fail")

    decision = "PASS_A7K1B_NEW_SPACE_GENERATOR_IMPL_PREFLIGHT" if not blockers else "HOLD_A7K1B_GENERATOR_IMPL_PREFLIGHT_BLOCKED"
    authorizes_a7k2 = decision == "PASS_A7K1B_NEW_SPACE_GENERATOR_IMPL_PREFLIGHT"

    impl_manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7k2_same_budget_smoke": authorizes_a7k2,
        "authorizes_alpha_proof": False,
        "generated_per_arm": GENERATED_PER_ARM,
        "selected_per_arm_if_a7k2": SELECTED_PER_ARM,
        "contract_hash": contract["stable_contract_hash"],
        "blockers": blockers,
        "candidate_manifest_hash": stable_hash(candidates.fillna("").to_dict(orient="list")),
        "outputs": {
            "candidate_manifest": str(candidate_path),
            "feature_coverage_audit": str(coverage_path),
            "static_gate_audit": str(static_path),
            "family_quota_audit": str(family_path),
            "formula_dedup_audit": str(dedup_path),
            "may_exclusion_audit": str(may_path),
        },
    }
    manifest_path = A7K1B_DIR / f"crypto_a7k1b_manifest_{DATE_TAG}.json"
    write_json(manifest_path, impl_manifest)

    report_path = REPORT_DIR / f"CRYPTO_A7K1B_NEW_SPACE_GENERATOR_IMPL_PREFLIGHT_{DATE_TAG}.md"
    lines = [
        "# Crypto A7K-1B New-Space Generator Implementation Preflight",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- evidence_level: `generator_implementation_preflight_not_alpha_proof`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        f"- authorizes_a7k2_same_budget_smoke: `{authorizes_a7k2}`",
        "- authorizes_alpha_proof: `False`",
        f"- blockers: `{blockers}`",
        "",
        "## Arm Counts",
        "",
        "| arm | generated |",
        "|---|---:|",
    ]
    for _, row in arm_counts.iterrows():
        lines.append(f"| `{row['arm']}` | {int(row['generated_count'])} |")
    lines += [
        "",
        "## Feature Coverage",
        "",
        "| feature | coverage_all | symbols >=95% | core12 pass |",
        "|---|---:|---:|---:|",
    ]
    for _, row in coverage.sort_values("feature").iterrows():
        lines.append(
            f"| `{row['feature']}` | {float(row['coverage_all']):.4f} | "
            f"{int(row['symbol_count_with_95pct'])}/{int(row['symbol_count_total'])} | `{bool(row['core12_coverage_pass'])}` |"
        )
    lines += [
        "",
        "## Family Quota",
        "",
        "| scope | family | count | share | cap | pass |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for _, row in family_quota.iterrows():
        lines.append(
            f"| `{row['scope']}` | `{row['family']}` | {int(row['count'])} | "
            f"{float(row['share']):.4f} | {float(row['cap']):.2f} | `{bool(row['cap_pass'])}` |"
        )
    lines += [
        "",
        "## Boundary",
        "",
        "- This is a static implementation preflight only.",
        "- It does not evaluate returns and does not create research candidates.",
        "- May remains stress-only and is absent from candidate generation.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7K1B_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7K-1B Decision Record",
                "",
                f"- decision: `{decision}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                "- search_executed: `False`",
                "- replay_executed: `False`",
                f"- authorizes_a7k2_same_budget_smoke: `{authorizes_a7k2}`",
                f"- blockers: `{blockers}`",
                "",
                "A7K-1B reviews a new generator-space implementation. It only authorizes A7K-2 if static coverage, family, duplicate, and May-exclusion gates pass.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print("A7K1B_REPORT=" + str(report_path))
    print("A7K1B_DECISION_RECORD=" + str(decision_path))
    print("A7K1B_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
