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
RUNTIME = REPO / "runtime" / "a7al2z7_response_guided_dry_generation"
REPORT = REPO / "reports" / "CRYPTO_A7AL2Z7_RESPONSE_GUIDED_DRY_GENERATION_20260529.md"
Z6_MANIFEST = REPO / "runtime" / "a7al2z6_response_guided_mutation_contract" / "a7al2z6_manifest.json"
Z6_ALLOWED = REPO / "runtime" / "a7al2z6_response_guided_mutation_contract" / "a7al2z6_allowed_mutation_families.csv"

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
FORBIDDEN_FIELD_PREFIXES = ("open_interest", "global_long_short", "top_long_short")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest(text: str, length: int = 16) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:length]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


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
    text = re.sub(r"\bR\d+_[A-Za-z0-9_]+_state\b", "STATE", text)
    text = re.sub(r"\b[a-z][a-z0-9_]*\b", "FIELD", text)
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
        "candidate_id": f"a7al2z7_{digest(family + '|' + expr)}",
        "expression": expr,
        "objective_family": family,
        "source_stage": "a7al2z7_response_guided_dry_generation",
        "field_families": "|".join(families),
        "fields": "|".join(fields),
        "operator_signature": "|".join(ops),
        "window_signature": "|".join(map(str, windows)),
        "skeleton_key": f"skeleton-{digest(skeleton(expr))}",
        "production_key": f"a7al2z7::{family}::{'|'.join(fields)}::{'|'.join(ops)}::{'|'.join(map(str, windows))}",
        "historical_source_ok": True,
        "field_lineage_ok": True,
        "pit_policy_ok": True,
        "negative_control_attached": True,
        "selected_for_z8_materialization": False,
        "preflight_decision": "",
        "shared_pool_stage": "dry_generated_response_guided_non_oi",
        "control_modes": CONTROL_MODES,
    }


def build_specs() -> dict[str, list[str]]:
    w_short = [4, 8, 12, 24]
    w_med = [12, 24, 48, 72, 168]
    smooth = [4, 8, 12]
    basis = ["premium_close_bps", "mark_index_basis_bps", "mark_trade_basis_bps"]
    funding = ["funding_rate"]
    price = ["trade_close", "index_close", "mark_close"]
    taker = ["kline_taker_buy_quote_share", "taker_buy_sell_volume_ratio_last"]
    liq = ["trade_quote_volume", "trade_volume", "trade_count", "taker_buy_quote_volume"]
    range_pairs = [("trade_high", "trade_low"), ("mark_high", "mark_low")]
    regime = [
        "R0_market_trend_state",
        "R1_market_volatility_state",
        "R2_market_breadth_state",
        "R3_liquidity_cycle_state",
        "R5_basis_premium_dislocation_state",
        "R9_alt_vs_major_dispersion_state",
        "R10_stress_proxy_state",
    ]
    static_groups = ["liquidity_tier", "meme_contract_group", "is_major", "is_multiplier_contract"]
    specs: dict[str, list[str]] = {k: [] for k in [
        "M0_basis_funding_double_difference",
        "M1_price_range_smoothed_reversal",
        "M2_taker_liquidity_control_resistant",
        "M3_latent_meme_major_neutral",
        "M4_regime_relative_value",
        "M5_trend_breadth_interaction",
        "M6_low_turnover_funding_premium",
        "M7_multi_neutral_cross_family",
    ]}

    for b, f, w, s, g in product(basis, funding, [12, 24, 48, 72, 168], smooth, ["liquidity_tier", "R5_basis_premium_dislocation_state", "R10_stress_proxy_state"]):
        diff = f"Sub(Rank(Mean(Delta({b},{w}),{s})),Rank(Mean(Delta({f},{w}),{s})))"
        specs["M0_basis_funding_double_difference"].extend(
            [
                f"GroupNeutralize({diff},{g})",
                f"LatentNeutralRank({diff},{g})",
                f"GroupNeutralize(Mul(Winsor(ZScore(Mean(Delta({b},{w}),{s}))),Neg(Winsor(ZScore(Mean(Delta({f},{w}),{s}))))),{g})",
            ]
        )

    for (hi, lo), close, w, h, g in product(range_pairs, price, [12, 24, 48, 72], [4, 8, 12, 24], ["R1_market_volatility_state", "R0_market_trend_state", "liquidity_tier"]):
        range_expr = f"SafeDiv(Mean(Sub({hi},{lo}),{w}),Mean({close},{w}))"
        specs["M1_price_range_smoothed_reversal"].extend(
            [
                f"GroupNeutralize(Mul(Rank({range_expr}),Neg(Rank(Delta({close},{h})))),{g})",
                f"LatentNeutralRank(Sub(Rank({range_expr}),Rank(Delta({close},{h}))),{g})",
            ]
        )

    for t, l, w, s, g in product(taker, liq, w_short + [48], smooth, ["liquidity_tier", "R3_liquidity_cycle_state", "meme_contract_group"]):
        diff = f"Sub(Rank(Mean(Delta({t},{w}),{s})),Rank(Mean(Delta({l},{w}),{s})))"
        specs["M2_taker_liquidity_control_resistant"].extend(
            [
                f"GroupNeutralize({diff},{g})",
                f"LatentNeutralRank({diff},{g})",
                f"GroupNeutralize(Mul({diff},Neg(Rank(Delta(trade_close,{min(w,24)})))),{g})",
            ]
        )

    for f, g, w, s in product(["funding_rate", "premium_close_bps", "mark_index_basis_bps", "kline_taker_buy_quote_share", "trade_quote_volume"], static_groups, [12, 24, 48, 72, 168], smooth):
        signal = f"Sub(Rank(Mean(Delta({f},{w}),{s})),Rank(Mean(Delta(trade_close,{min(w,24)}),{s})))"
        specs["M3_latent_meme_major_neutral"].extend(
            [
                f"GroupNeutralize({signal},{g})",
                f"LatentNeutralRank({signal},{g})",
            ]
        )

    for a, b, g, w, s in product(["premium_close_bps", "mark_index_basis_bps", "funding_rate", "kline_taker_buy_quote_share"], ["trade_close", "index_close", "trade_quote_volume"], regime, [12, 24, 48, 72], smooth):
        signal = f"Sub(Rank(Mean(Delta({a},{w}),{s})),Rank(Mean(Delta({b},{min(w,24)}),{s})))"
        specs["M4_regime_relative_value"].extend(
            [
                f"GroupNeutralize({signal},{g})",
                f"LatentNeutralRank({signal},{g})",
            ]
        )

    for close, b, g, w, s in product(price, basis, ["R0_market_trend_state", "R2_market_breadth_state", "R9_alt_vs_major_dispersion_state", "R10_stress_proxy_state"], [12, 24, 48, 72], smooth):
        signal = f"Mul(Neg(Rank(Mean(Delta({close},{w}),{s}))),Rank(Mean(Delta({b},{w}),{s})))"
        specs["M5_trend_breadth_interaction"].extend(
            [
                f"GroupNeutralize({signal},{g})",
                f"LatentNeutralRank(Sub(Rank(Mean(Delta({b},{w}),{s})),Rank(Mean(Delta({close},{w}),{s}))),{g})",
            ]
        )

    for b, f, w, s, g in product(basis, funding, [48, 72, 168, 336], [12, 24, 48], ["R5_basis_premium_dislocation_state", "R10_stress_proxy_state", "liquidity_tier", "is_major"]):
        signal = f"Sub(Rank(Mean({b},{w})),Rank(Mean({f},{w})))"
        compress = f"Sub(Rank(Mean(Abs(Delta({b},{w})),{s})),Rank(Mean(Abs(Delta({f},{w})),{s})))"
        specs["M6_low_turnover_funding_premium"].extend(
            [
                f"GroupNeutralize({signal},{g})",
                f"GroupNeutralize({compress},{g})",
                f"LatentNeutralRank({signal},{g})",
                f"LatentNeutralRank({compress},{g})",
            ]
        )

    for a, b, c, g, w in product(["premium_close_bps", "funding_rate", "kline_taker_buy_quote_share"], ["trade_quote_volume", "trade_count", "trade_close"], ["R1_market_volatility_state", "R3_liquidity_cycle_state", "R10_stress_proxy_state"], static_groups, [12, 24, 48, 72]):
        signal = f"Sub(Sub(Rank(Delta({a},{w})),Rank(Delta({b},{w}))),Rank(Delta({c},{min(w,24)})))"
        specs["M7_multi_neutral_cross_family"].extend(
            [
                f"GroupNeutralize(GroupNeutralize({signal},{c}),{g})",
                f"LatentNeutralRank(GroupNeutralize({signal},{c}),{g})",
            ]
        )
    return specs


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    z6 = read_json(Z6_MANIFEST)
    if not z6.get("authorizes_a7al2z7_response_guided_generation"):
        raise SystemExit("A7AL-2Z6 does not authorize Z7 generation")
    allowed = pd.read_csv(Z6_ALLOWED)
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
    ledger["selected_for_z8_materialization"] = ledger["candidate_id"].isin(selected_ids)
    ledger.loc[ledger["selected_for_z8_materialization"], "shared_pool_stage"] = "selected_for_response_guided_materialization"
    family = (
        ledger.groupby("objective_family", dropna=False)
        .agg(
            generated_count=("candidate_id", "count"),
            static_valid_count=("static_valid", "sum"),
            selected_for_z8_count=("selected_for_z8_materialization", "sum"),
            unique_skeleton_count=("skeleton_key", "nunique"),
            unique_production_count=("production_key", "nunique"),
        )
        .reset_index()
        .merge(allowed[["family_id", "minimum_generated", "minimum_selected"]], left_on="objective_family", right_on="family_id", how="left")
    )
    family["quota_pass"] = (
        (family["generated_count"] >= family["minimum_generated"])
        & (family["selected_for_z8_count"] >= family["minimum_selected"])
    )
    blockers = pd.DataFrame(blocker_rows)
    selected = ledger[ledger["selected_for_z8_materialization"]].copy()
    unique_expr_ratio = float(ledger["expression"].nunique() / len(ledger)) if len(ledger) else 0.0
    selected_top_family_share = float(selected["objective_family"].value_counts(normalize=True).max()) if len(selected) else 0.0
    decision = (
        "PASS_A7AL2Z7_RESPONSE_GUIDED_DRY_GENERATION_READY_FOR_Z8"
        if blockers.empty and bool(family["quota_pass"].all()) and len(selected) >= 96
        else "HOLD_A7AL2Z7_RESPONSE_GUIDED_STATIC_GENERATION_FAIL"
    )
    manifest = {
        "stage": "A7AL-2Z7",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_static_generation": True,
        "executes_numeric_replay": False,
        "executes_training": False,
        "authorizes_a7al2z8_materialization_repair": decision.startswith("PASS"),
        "authorizes_numeric_replay": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "generated_total": int(len(ledger)),
        "static_valid_count": int(ledger["static_valid"].sum()),
        "selected_for_z8_count": int(ledger["selected_for_z8_materialization"].sum()),
        "unique_expr_ratio": unique_expr_ratio,
        "selected_top_family_share": selected_top_family_share,
        "family_count": int(ledger["objective_family"].nunique()),
        "blocker_count": int(len(blockers)),
        "uses_oi_or_positioning_core": False,
        "uses_may": False,
    }
    ledger.to_csv(RUNTIME / "a7al2z7_generated_candidate_ledger.csv", index=False)
    selected.to_csv(RUNTIME / "a7al2z7_selected_for_z8_materialization.csv", index=False)
    family.to_csv(RUNTIME / "a7al2z7_family_quota_audit.csv", index=False)
    blockers.to_csv(RUNTIME / "a7al2z7_static_blocker_matrix.csv", index=False)
    write_json(RUNTIME / "a7al2z7_manifest.json", manifest)
    write_json(
        RUNTIME / "a7al2z7_authorization_matrix.json",
        {
            "A7AL-2Z7": {"status": decision},
            "a7al2z8_materialization_repair": {"authorized": decision.startswith("PASS")},
            "numeric_replay": {"authorized": False},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AL-2Z7 RESPONSE-GUIDED DRY GENERATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "Z7 uses Z6 non-May failure directives to generate response-guided non-OI candidates. It does not replay, train, or authorize proof.",
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
