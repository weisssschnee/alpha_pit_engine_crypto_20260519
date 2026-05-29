from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any

import pandas as pd

try:
    import pyarrow.dataset as ds
    import pyarrow.parquet as pq
except Exception:  # pragma: no cover
    ds = None  # type: ignore[assignment]
    pq = None  # type: ignore[assignment]


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7al2z1_broader_non_oi_dry_generation"
REPORT = REPO / "reports" / "CRYPTO_A7AL2Z1_BROADER_NON_OI_DRY_GENERATION_20260529.md"

Z0_MANIFEST = REPO / "runtime" / "a7al2z0_broader_non_oi_objective_contract" / "a7al2z0_manifest.json"
Z0_ALLOWED = REPO / "runtime" / "a7al2z0_broader_non_oi_objective_contract" / "a7al2z0_allowed_objective_families.csv"

DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
BASE_PANEL = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v2_20260527"
LATENT_PANEL = DATA_ROOT / "gold" / "features" / "binance_universe498_latent_state_features_v1_20260527.parquet"
UPPER_REGIME_PANEL = DATA_ROOT / "gold" / "features" / "binance_universe498_upper_regime_state_v1_20260527.parquet"

CONTROL_MODES = "one_bar_lag|wrong_lag_future_24h|wrong_lag_stale_168h|time_shuffle|symbol_shuffle|same_family_random"
ALLOWED_OPERATORS = {
    "Abs",
    "Add",
    "Clip",
    "Delta",
    "GroupNeutralize",
    "LatentNeutralRank",
    "Mean",
    "Mul",
    "Neg",
    "Rank",
    "SafeDiv",
    "Sign",
    "StateMask",
    "Sub",
    "Winsor",
    "ZScore",
}
STATE_FIELDS = {
    "R0_market_trend_state",
    "R1_market_volatility_state",
    "R2_market_breadth_state",
    "R3_liquidity_cycle_state",
    "R5_basis_premium_dislocation_state",
    "R9_alt_vs_major_dispersion_state",
    "R10_stress_proxy_state",
    "liquidity_tier",
    "meme_contract_group",
    "is_multiplier_contract",
    "is_major",
}
FORBIDDEN_FIELD_PREFIXES = (
    "open_interest",
    "global_long_short",
    "top_long_short",
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest(text: str, length: int = 16) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:length]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def schema_names(path: Path) -> set[str]:
    if not path.exists():
        return set()
    if path.is_dir():
        if ds is None:
            return set()
        return set(ds.dataset(str(path), format="parquet").schema.names)
    if pq is None:
        return set()
    return set(pq.ParquetFile(path).schema.names)


def canonical(expr: str) -> str:
    return re.sub(r"\s+", "", expr)


def skeleton(expr: str) -> str:
    text = canonical(expr)
    text = re.sub(r"\b[a-z][a-z0-9_]*\b", "FIELD", text)
    text = re.sub(r"\bR\d+_[a-z0-9_]+_state\b", "STATE", text)
    text = re.sub(r"\b\d+\b", "W", text)
    return text


def extract_operators(expr: str) -> tuple[str, ...]:
    return tuple(re.findall(r"\b([A-Z][A-Za-z0-9_]*)\s*\(", expr))


def extract_windows(expr: str) -> tuple[int, ...]:
    return tuple(sorted({int(x) for x in re.findall(r",\s*(\d+)\s*(?:,|\))", expr)}))


def extract_fields(expr: str) -> tuple[str, ...]:
    operators = {x.lower() for x in extract_operators(expr)}
    tokens = set(re.findall(r"\b[a-z][a-z0-9_]*\b", expr))
    tokens.update(re.findall(r"\bR\d+_[A-Za-z0-9_]+_state\b", expr))
    state_values = {"true", "false", "major", "nonmajor", "meme", "nonmeme"}
    return tuple(sorted(tokens - operators - state_values))


def field_family(field: str) -> str:
    if field in STATE_FIELDS:
        return "state"
    name = field.lower()
    if "funding" in name:
        return "funding"
    if "basis" in name or "premium" in name:
        return "basis_premium"
    if "taker" in name:
        return "taker_flow"
    if "volume" in name or "trade_count" in name:
        return "liquidity"
    if "high" in name or "low" in name:
        return "range"
    if "close" in name or "return" in name:
        return "price"
    return "misc"


def forbidden_field(field: str) -> bool:
    return field.startswith(FORBIDDEN_FIELD_PREFIXES)


def expr_row(family: str, expr: str) -> dict[str, Any]:
    fields = list(extract_fields(expr))
    ops = sorted(set(extract_operators(expr)))
    windows = sorted(set(extract_windows(expr)))
    families = sorted({field_family(f) for f in fields})
    return {
        "candidate_id": f"a7al2z1_{digest(family + '|' + expr)}",
        "expression": expr,
        "objective_family": family,
        "source_stage": "a7al2z1_broader_non_oi_dry_generation",
        "field_families": "|".join(families),
        "fields": "|".join(fields),
        "operator_signature": "|".join(ops),
        "window_signature": "|".join(map(str, windows)),
        "skeleton_key": f"skeleton-{digest(skeleton(expr))}",
        "production_key": f"a7al2z1::{family}::{'|'.join(fields)}::{'|'.join(ops)}::{'|'.join(map(str, windows))}",
        "historical_source_ok": True,
        "field_lineage_ok": True,
        "pit_policy_ok": True,
        "negative_control_attached": True,
        "selected_for_z2_materialization": False,
        "preflight_decision": "",
        "shared_pool_stage": "dry_generated_non_oi",
        "control_modes": CONTROL_MODES,
    }


def build_specs() -> dict[str, list[str]]:
    w_short = [6, 12, 24, 48]
    w_med = [12, 24, 48, 72, 168, 336]
    basis = ["premium_close_bps", "mark_index_basis_bps", "mark_trade_basis_bps"]
    price = ["trade_close", "index_close", "mark_close"]
    liquidity = ["trade_quote_volume", "trade_volume", "trade_count", "taker_buy_quote_volume"]
    taker = ["kline_taker_buy_quote_share", "taker_buy_sell_volume_ratio_last"]
    regime = [
        "R0_market_trend_state",
        "R1_market_volatility_state",
        "R2_market_breadth_state",
        "R3_liquidity_cycle_state",
        "R5_basis_premium_dislocation_state",
        "R10_stress_proxy_state",
    ]
    static_groups = ["liquidity_tier", "meme_contract_group", "is_major", "is_multiplier_contract"]

    specs: dict[str, list[str]] = {}
    specs["Z0_funding_basis_premium_dislocation"] = []
    for b, w in product(basis, w_med):
        specs["Z0_funding_basis_premium_dislocation"].extend(
            [
                f"Sub(Rank(Mean({b},{w})),Rank(Mean(funding_rate,{w})))",
                f"Sub(Rank(Delta({b},{w})),Rank(Delta(funding_rate,{w})))",
                f"Mul(Winsor(ZScore(Mean({b},{w}))),Winsor(ZScore(Mean(funding_rate,{w}))))",
                f"Mul(Winsor(ZScore(Delta({b},{w}))),Winsor(ZScore(Delta(funding_rate,{w}))))",
                f"Rank(Abs(ZScore(Mean({b},{w}))))",
                f"Rank(Abs(ZScore(Delta({b},{w}))))",
                f"GroupNeutralize(Rank(Delta({b},{w})),R5_basis_premium_dislocation_state)",
            ]
        )

    specs["Z1_price_range_volatility_structure"] = []
    for close, w in product(price, w_med):
        specs["Z1_price_range_volatility_structure"].extend(
            [
                f"Rank(Delta({close},{w}))",
                f"Neg(Rank(Delta({close},{w})))",
                f"Rank(Abs(ZScore(Delta({close},{w}))))",
            ]
        )
    for left, right, w in product(price, price, w_med):
        if left == right:
            continue
        specs["Z1_price_range_volatility_structure"].extend(
            [
                f"Sub(Rank(Delta({left},{w})),Rank(Delta({right},{w})))",
                f"Sub(Rank(Mean({left},{w})),Rank(Mean({right},{w})))",
                f"Mul(Winsor(ZScore(Delta({left},{w}))),Neg(Winsor(ZScore(Delta({right},{w})))))",
            ]
        )
    for high, low, w in [
        ("trade_high", "trade_low", 24),
        ("trade_high", "trade_low", 72),
        ("mark_high", "mark_low", 24),
        ("mark_high", "mark_low", 72),
    ]:
        specs["Z1_price_range_volatility_structure"].extend(
            [
                f"Rank(Mean(Sub({high},{low}),{w}))",
                f"Rank(Delta(Sub({high},{low}),{w}))",
                f"SafeDiv(Mean(Sub({high},{low}),{w}),Mean(trade_close,{w}))",
                f"Mul(Rank(Mean(Sub({high},{low}),{w})),Neg(Rank(Delta(trade_close,{w}))))",
                f"GroupNeutralize(Rank(Mean(Sub({high},{low}),{w})),R1_market_volatility_state)",
            ]
        )

    specs["Z2_liquidity_taker_microstructure_lite"] = []
    for f, w in product(liquidity + taker, w_short + [48, 168]):
        specs["Z2_liquidity_taker_microstructure_lite"].extend(
            [
                f"Rank(Delta({f},{w}))",
                f"Rank(Mean({f},{w}))",
                f"Rank(Abs(ZScore(Delta({f},{w}))))",
                f"Sub(Rank(Delta({f},{w})),Rank(Delta(trade_close,{min(w,24)})))",
                f"Mul(Winsor(ZScore(Delta({f},{w}))),Neg(Winsor(ZScore(Delta(trade_close,{min(w,24)})))))",
                f"GroupNeutralize(Rank(Delta({f},{w})),R3_liquidity_cycle_state)",
            ]
        )
    specs["Z2_liquidity_taker_microstructure_lite"].extend(
        [
            "SafeDiv(taker_buy_quote_volume,trade_quote_volume)",
            "Sub(Rank(kline_taker_buy_quote_share),Rank(taker_buy_sell_volume_ratio_last))",
        ]
    )

    specs["Z3_basis_price_trend_reversal"] = []
    for b, c, w in product(basis, ["trade_close", "index_close"], [12, 24, 48, 168]):
        specs["Z3_basis_price_trend_reversal"].extend(
            [
                f"Mul(Rank(Delta({b},{w})),Neg(Rank(Delta({c},{w}))))",
                f"Mul(Winsor(ZScore(Delta({b},{w}))),Neg(Winsor(ZScore(Delta({c},{w})))))",
                f"Sub(Rank(Mean({b},{w})),Rank(Delta({c},{w})))",
                f"Sub(Rank(Delta({b},{w})),Rank(Delta({c},{w})))",
                f"GroupNeutralize(Rank(Delta({b},{w})),R0_market_trend_state)",
            ]
        )

    specs["Z4_upper_regime_relative_value"] = []
    for f, g, w in product(["funding_rate", "premium_close_bps", "mark_index_basis_bps", "trade_quote_volume"], regime, [24, 72, 168]):
        specs["Z4_upper_regime_relative_value"].extend(
            [
                f"GroupNeutralize(Rank(Delta({f},{w})),{g})",
                f"LatentNeutralRank(Delta({f},{w}),{g})",
                f"GroupNeutralize(Rank(Mean({f},{w})),{g})",
            ]
        )

    specs["Z5_latent_listing_meme_neutral_structure"] = []
    for f, g, w in product(["trade_return_1h", "premium_close_bps", "funding_rate", "kline_taker_buy_quote_share", "trade_quote_volume"], static_groups, [24, 72, 168]):
        specs["Z5_latent_listing_meme_neutral_structure"].extend(
            [
                f"GroupNeutralize(Rank(Delta({f},{w})),{g})",
                f"LatentNeutralRank(Delta({f},{w}),{g})",
                f"GroupNeutralize(Rank(Mean({f},{w})),{g})",
            ]
        )
    specs["Z5_latent_listing_meme_neutral_structure"].extend(
        [
            "Mul(Rank(Delta(trade_close,24)),StateMask(is_major,True))",
            "Mul(Rank(Delta(trade_close,24)),StateMask(is_major,False))",
        ]
    )

    specs["Z6_cross_sectional_relative_flow_value"] = []
    for a, b, w in product(["premium_close_bps", "funding_rate", "kline_taker_buy_quote_share"], ["trade_quote_volume", "trade_count"], [12, 24, 72, 168]):
        specs["Z6_cross_sectional_relative_flow_value"].extend(
            [
                f"Sub(Rank(Delta({a},{w})),Rank(Delta({b},{w})))",
                f"Sub(Rank(Mean({a},{w})),Rank(Mean({b},{w})))",
                f"Mul(Winsor(ZScore(Delta({a},{w}))),Winsor(ZScore(Delta({b},{w}))))",
                f"Mul(Winsor(ZScore(Mean({a},{w}))),Winsor(ZScore(Mean({b},{w}))))",
            ]
        )

    specs["Z7_market_regime_price_breadth"] = []
    for f, g, w in product(["trade_close", "index_close", "trade_return_1h", "premium_close_bps"], ["R0_market_trend_state", "R1_market_volatility_state", "R2_market_breadth_state", "R9_alt_vs_major_dispersion_state", "R10_stress_proxy_state"], [24, 72, 168]):
        specs["Z7_market_regime_price_breadth"].extend(
            [
                f"GroupNeutralize(Rank(Delta({f},{w})),{g})",
                f"LatentNeutralRank(Delta({f},{w}),{g})",
                f"GroupNeutralize(Rank(Mean({f},{w})),{g})",
            ]
        )
    return specs


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    z0 = read_json(Z0_MANIFEST)
    if not z0.get("authorizes_a7al2z1_static_dry_generation"):
        raise SystemExit("A7AL-2Z0 does not authorize Z1 static dry generation")

    allowed = pd.read_csv(Z0_ALLOWED)
    base_schema = schema_names(BASE_PANEL)
    latent_schema = schema_names(LATENT_PANEL)
    regime_schema = schema_names(UPPER_REGIME_PANEL)
    known_fields = base_schema | latent_schema | regime_schema | STATE_FIELDS

    specs = build_specs()
    rows: list[dict[str, Any]] = []
    blocker_rows: list[dict[str, Any]] = []
    for family in allowed["family_id"]:
        for expr in sorted(set(specs.get(family, [])), key=lambda e: digest(f"{family}|{e}", 24)):
            row = expr_row(family, expr)
            fields = row["fields"].split("|") if row["fields"] else []
            operators = set(row["operator_signature"].split("|")) if row["operator_signature"] else set()
            missing = sorted(f for f in fields if f not in known_fields)
            forbidden = sorted(f for f in fields if forbidden_field(f))
            unsupported = sorted(operators - ALLOWED_OPERATORS)
            row["historical_source_ok"] = not missing
            row["field_lineage_ok"] = not forbidden
            row["pit_policy_ok"] = not missing and not forbidden
            row["static_valid"] = not missing and not forbidden and not unsupported
            if missing:
                blocker_rows.append({"candidate_id": row["candidate_id"], "blocker": "missing_field", "detail": "|".join(missing)})
            if forbidden:
                blocker_rows.append({"candidate_id": row["candidate_id"], "blocker": "forbidden_oi_or_positioning_field", "detail": "|".join(forbidden)})
            if unsupported:
                blocker_rows.append({"candidate_id": row["candidate_id"], "blocker": "unsupported_operator", "detail": "|".join(unsupported)})
            rows.append(row)

    ledger = pd.DataFrame(rows).drop_duplicates("candidate_id").reset_index(drop=True)
    valid = ledger[ledger["static_valid"].astype(bool)].copy()
    selected_parts = []
    for family, group in valid.groupby("objective_family", sort=True):
        selected = group.drop_duplicates("skeleton_key").head(16)
        if len(selected) < 16:
            extra = group[~group["candidate_id"].isin(set(selected["candidate_id"]))].head(16 - len(selected))
            selected = pd.concat([selected, extra], ignore_index=True)
        selected_parts.append(selected.head(16))
    selected_ids = set(pd.concat(selected_parts, ignore_index=True)["candidate_id"]) if selected_parts else set()
    ledger["selected_for_z2_materialization"] = ledger["candidate_id"].isin(selected_ids)
    ledger.loc[ledger["selected_for_z2_materialization"], "shared_pool_stage"] = "selected_for_future_non_oi_materialization"

    family = (
        ledger.groupby("objective_family", dropna=False)
        .agg(
            generated_count=("candidate_id", "count"),
            static_valid_count=("static_valid", "sum"),
            selected_for_z2_count=("selected_for_z2_materialization", "sum"),
            unique_skeleton_count=("skeleton_key", "nunique"),
            unique_production_count=("production_key", "nunique"),
        )
        .reset_index()
        .merge(allowed[["family_id", "minimum_generated", "minimum_selected_for_preflight"]], left_on="objective_family", right_on="family_id", how="left")
    )
    family["quota_pass"] = (
        (family["generated_count"] >= family["minimum_generated"])
        & (family["selected_for_z2_count"] >= family["minimum_selected_for_preflight"])
    )

    blockers = pd.DataFrame(blocker_rows)
    unique_expr_ratio = float(ledger["expression"].nunique() / len(ledger)) if len(ledger) else 0.0
    selected = ledger[ledger["selected_for_z2_materialization"]].copy()
    selected_top_family_share = float(selected["objective_family"].value_counts(normalize=True).max()) if len(selected) else 0.0
    decision = (
        "PASS_A7AL2Z1_BROADER_NON_OI_DRY_GENERATION_READY_FOR_MATERIALIZATION_AUDIT"
        if blockers.empty and bool(family["quota_pass"].all()) and len(selected) >= 96
        else "HOLD_A7AL2Z1_STATIC_GENERATION_CONTRACT_FAIL"
    )
    manifest = {
        "stage": "A7AL-2Z1",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_static_generation": True,
        "executes_numeric_replay": False,
        "executes_training": False,
        "authorizes_a7al2z2_materialization_audit": decision.startswith("PASS"),
        "authorizes_numeric_replay": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "generated_total": int(len(ledger)),
        "static_valid_count": int(ledger["static_valid"].sum()),
        "selected_for_z2_count": int(ledger["selected_for_z2_materialization"].sum()),
        "unique_expr_ratio": unique_expr_ratio,
        "selected_top_family_share": selected_top_family_share,
        "family_count": int(ledger["objective_family"].nunique()),
        "blocker_count": int(len(blockers)),
        "uses_oi_or_positioning_core": False,
        "uses_may": False,
    }

    ledger.to_csv(RUNTIME / "a7al2z1_generated_candidate_ledger.csv", index=False)
    selected.to_csv(RUNTIME / "a7al2z1_selected_for_z2_materialization.csv", index=False)
    family.to_csv(RUNTIME / "a7al2z1_family_quota_audit.csv", index=False)
    blockers.to_csv(RUNTIME / "a7al2z1_static_blocker_matrix.csv", index=False)
    write_json(RUNTIME / "a7al2z1_manifest.json", manifest)
    write_json(
        RUNTIME / "a7al2z1_authorization_matrix.json",
        {
            "A7AL-2Z1": {"status": decision},
            "a7al2z2_materialization_audit": {"authorized": decision.startswith("PASS")},
            "numeric_replay": {"authorized": False},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AL-2Z1 BROADER NON-OI DRY GENERATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "Z1 is static dry generation only. It does not run replay, train a model, or authorize alpha proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Quota Audit",
        "",
        md_table(family),
        "",
        "## Selected Preview",
        "",
        md_table(selected[["candidate_id", "objective_family", "expression", "field_families", "operator_signature", "skeleton_key"]], 40),
        "",
        "## Blockers",
        "",
        md_table(blockers) if not blockers.empty else "No blockers.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
