from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from itertools import cycle, product
from pathlib import Path
from typing import Any

import pandas as pd

try:
    import pyarrow.dataset as ds
except Exception:  # pragma: no cover
    ds = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "a7al2x3_family_balanced_dry_generation"
REPORT = ROOT / "reports" / "CRYPTO_A7AL2X3_FAMILY_BALANCED_DRY_GENERATION_SMOKE_20260529.md"

CONTRACT_DIR = ROOT / "runtime" / "a7al2x2r_family_balanced_repair_contract"
QUOTA = CONTRACT_DIR / "a7al2x2r_family_min_quota_policy.csv"
FIELD_CONTRACT = CONTRACT_DIR / "a7al2x2r_historical_field_source_contract.csv"
TEMPLATE_REQ = CONTRACT_DIR / "a7al2x2r_generator_template_requirements.csv"
FORBIDDEN = CONTRACT_DIR / "a7al2x2r_forbidden_fallbacks.csv"
BASE_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527")


CONTROL_MODES = [
    "one_bar_lag",
    "wrong_lag_future_24h",
    "wrong_lag_stale_168h",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_random",
]

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

STATE_CONSTANTS = {
    "alt_lag",
    "alt_lead",
    "alt_mid",
    "basis_high",
    "basis_low",
    "basis_mid",
    "breadth_mid",
    "breadth_strong",
    "breadth_weak",
    "false",
    "high",
    "lev_high",
    "lev_low",
    "lev_mid",
    "liq_contracting",
    "liq_expanding",
    "liq_mid",
    "low",
    "meme_multiplier_contract",
    "meme_plain_contract",
    "mid",
    "non_meme_multiplier_contract",
    "non_meme_plain_contract",
    "pos_high",
    "pos_low",
    "pos_mid",
    "stress_high",
    "stress_low",
    "stress_mid",
    "tail",
    "top100",
    "top20",
    "top200",
    "top50",
    "trend_up",
    "trend_down",
    "trend_mid",
    "true",
    "vol_high",
    "vol_low",
    "vol_mid",
    "risk_on",
    "risk_off",
    "major",
    "nonmajor",
    "meme",
    "nonmeme",
    "multiplier_1000",
    "regular",
    "young",
    "mature",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest(value: str, length: int = 16) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:length]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, limit: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(limit).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def canonical(expression: str) -> str:
    return re.sub(r"\s+", "", expression)


def skeleton(expression: str) -> str:
    text = canonical(expression)
    text = re.sub(r"\b[a-z][a-z0-9_]*\b", "FIELD", text)
    text = re.sub(r"\b\d+\b", "W", text)
    return text


def extract_operators(expression: str) -> tuple[str, ...]:
    return tuple(re.findall(r"\b([A-Z][A-Za-z0-9_]*)\s*\(", expression))


def extract_windows(expression: str) -> tuple[int, ...]:
    return tuple(sorted({int(match) for match in re.findall(r",\s*(\d+)\s*(?:,|\))", expression)}))


def extract_fields(expression: str) -> tuple[str, ...]:
    tokens = set(re.findall(r"\b[a-z][a-z0-9_]*\b", expression))
    operators = {op.lower() for op in extract_operators(expression)}
    return tuple(sorted(tokens - operators - STATE_CONSTANTS - {"nan", "inf"}))


def schema_names(path: Path) -> set[str]:
    if ds is None or not path.exists():
        return set()
    try:
        return set(ds.dataset(str(path), format="parquet").schema.names)
    except Exception:
        return set()


def split_contract_fields(value: str) -> list[str]:
    fields: list[str] = []
    for part in str(value).split("|"):
        part = part.strip()
        if part:
            fields.append(part)
    return fields


def field_family(field: str) -> str:
    name = field.lower()
    if "open_interest" in name:
        return "open_interest"
    if "funding" in name:
        return "funding"
    if "basis" in name or "premium" in name:
        return "basis"
    if "long_short" in name or "position" in name or "taker_buy_sell" in name:
        return "positioning"
    if "taker" in name:
        return "taker_flow"
    if name.startswith("r") and "_state" in name:
        return "upper_regime"
    if (
        "latent" in name
        or "listing_age" in name
        or "liquidity_tier" in name
        or "meme" in name
        or "multiplier" in name
        or name == "is_major"
    ):
        return "latent_state"
    if any(token in name for token in ["close", "price", "return"]):
        return "price"
    return "misc"


def source_map(field_contract: pd.DataFrame) -> dict[str, dict[str, Any]]:
    mapping: dict[str, dict[str, Any]] = {}
    for row in field_contract.to_dict("records"):
        for field in split_contract_fields(row["field_or_group"]):
            mapping[field] = {
                "family_id": row["family_id"],
                "source_contract": row["source_contract"],
                "field_class": row["field_class"],
                "pit_policy": row["pit_policy"],
                "allowed_for_historical_dry_generation": str(row["allowed_for_historical_dry_generation"]).lower()
                == "true",
            }
    return mapping


def rows_from_specs(family_id: str, target: int, specs: list[str], fields_by_expr: dict[str, list[str]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[str] = set()
    ordered_specs = sorted(specs, key=lambda expr: digest(f"{family_id}|{expr}", 24))
    for expression in ordered_specs:
        expr_key = f"expr-{digest(canonical(expression))}"
        if expr_key in seen:
            continue
        seen.add(expr_key)
        fields = fields_by_expr[expression]
        operators = sorted(set(extract_operators(expression)))
        windows = sorted(set(extract_windows(expression)))
        families = sorted({field_family(f) for f in fields})
        sk = f"skeleton-{digest(skeleton(expression))}"
        prod = f"a7al2x3::{family_id}::{'|'.join(fields)}::{'|'.join(operators)}::{'|'.join(map(str, windows))}"
        candidates.append(
            {
                "candidate_id": f"a7al2x3_{digest(family_id + '|' + expression)}",
                "expression": expression,
                "objective_family": family_id,
                "source_stage": "a7al2x3_family_balanced_dry_generation",
                "field_families": "|".join(families),
                "fields": "|".join(fields),
                "operator_signature": "|".join(operators),
                "window_signature": "|".join(map(str, windows)),
                "skeleton_key": sk,
                "production_key": prod,
                "historical_source_ok": True,
                "field_lineage_ok": True,
                "pit_policy_ok": True,
                "negative_control_attached": True,
                "selected_for_family_balanced_preflight": False,
                "preflight_decision": "",
                "shared_pool_stage": "dry_generated",
                "control_modes": "|".join(CONTROL_MODES),
            }
        )

    by_skeleton: dict[str, list[dict[str, Any]]] = {}
    for row in candidates:
        by_skeleton.setdefault(row["skeleton_key"], []).append(row)
    for group in by_skeleton.values():
        group.sort(key=lambda row: (row["production_key"], row["candidate_id"]))

    rows: list[dict[str, Any]] = []
    max_per_skeleton = max(1, target // 4)
    skeleton_keys = sorted(by_skeleton)
    while len(rows) < target:
        progressed = False
        for sk in skeleton_keys:
            if len(rows) >= target:
                break
            current_count = sum(1 for row in rows if row["skeleton_key"] == sk)
            if current_count >= max_per_skeleton:
                continue
            group = by_skeleton[sk]
            if current_count < len(group):
                rows.append(group[current_count])
                progressed = True
        if not progressed:
            break
    if len(rows) < target:
        used = {row["candidate_id"] for row in rows}
        for row in candidates:
            if row["candidate_id"] not in used:
                rows.append(row)
                used.add(row["candidate_id"])
            if len(rows) >= target:
                break
    return rows[:target]


def build_specs() -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    oi_fields = ["open_interest_last", "open_interest_mean", "open_interest_value_last", "open_interest_value_mean"]
    price_fields = ["trade_close", "mark_close", "index_close"]
    basis_fields = ["premium_close", "premium_close_bps", "mark_index_basis_bps", "mark_trade_basis_bps"]
    funding_fields = ["funding_rate_abs_168h", "funding_rate_mean_168h"]
    global_fields = ["global_long_short_account_ratio_last", "global_long_short_account_ratio_mean"]
    account_fields = ["top_long_short_account_ratio_last", "top_long_short_account_ratio_mean"]
    position_fields = ["top_long_short_position_ratio_last", "top_long_short_position_ratio_mean"]
    taker_fields = [
        "taker_buy_sell_volume_ratio_last",
        "taker_buy_sell_volume_ratio_mean",
        "taker_buy_quote_volume",
        "kline_taker_buy_quote_share",
    ]
    regime_state_values = {
        "R0_market_trend_state": ["trend_up", "trend_down"],
        "R2_market_breadth_state": ["breadth_strong", "breadth_weak"],
        "R3_liquidity_cycle_state": ["liq_expanding", "liq_contracting"],
        "R4_leverage_crowding_state": ["lev_high", "lev_low"],
        "R5_basis_premium_dislocation_state": ["basis_high", "basis_low"],
        "R6_positioning_crowding_state": ["pos_high", "pos_low"],
        "R9_alt_vs_major_dispersion_state": ["alt_lead", "alt_lag"],
        "R10_stress_proxy_state": ["stress_high", "stress_low"],
    }
    latent_fields = ["raw_latent_state_id", "liquidity_tier", "meme_contract_group", "is_multiplier_contract", "is_major"]
    latent_state_values = {
        "liquidity_tier": ["top20", "top50", "top100", "top200", "tail"],
        "meme_contract_group": [
            "meme_multiplier_contract",
            "meme_plain_contract",
            "non_meme_multiplier_contract",
            "non_meme_plain_contract",
        ],
        "is_multiplier_contract": ["True", "False"],
        "is_major": ["True", "False"],
    }
    windows = [4, 8, 12, 24, 48, 72, 96, 168, 336]
    slow_windows = [24, 48, 72, 96, 168, 336]

    specs: list[dict[str, Any]] = []
    fields_by_expr: dict[str, list[str]] = {}

    def add(family: str, expression: str, fields: list[str]) -> None:
        specs.append({"family_id": family, "expression": expression})
        fields_by_expr[expression] = fields

    for oi, price, w1, w2 in product(oi_fields, price_fields, windows, windows):
        add("F0_OI_delta_price_interaction", f"Mul(Sign(Delta({oi},{w1})),Rank(Delta({price},{w2})))", [oi, price])
        add("F0_OI_delta_price_interaction", f"Sub(ZScore(Delta({oi},{w1})),ZScore(Delta({price},{w2})))", [oi, price])
        add("F0_OI_delta_price_interaction", f"Mul(Winsor(ZScore(Delta({oi},{w1}))),Winsor(ZScore(Delta({price},{w2}))))", [oi, price])
        add("F0_OI_delta_price_interaction", f"Add(ZScore(Delta({oi},{w1})),Neg(ZScore(Delta({price},{w2}))))", [oi, price])
        add("F0_OI_delta_price_interaction", f"Sub(Rank(Mean(Delta({oi},{w1}),{max(w1,w2)})),Rank(Mean(Delta({price},{w2}),{max(w1,w2)})))", [oi, price])
        add("F0_OI_delta_price_interaction", f"Mul(Clip(ZScore(Delta({oi},{w1}))),Sign(Delta({price},{w2})))", [oi, price])
        add("F0_OI_delta_price_interaction", f"Sub(Abs(ZScore(Delta({oi},{w1}))),Abs(ZScore(Delta({price},{w2}))))", [oi, price])

    for oi, basis, w1, w2 in product(oi_fields, basis_fields, slow_windows, slow_windows):
        add("F1_OI_basis_premium_interaction", f"Mul(Sign(Delta({oi},{w1})),Rank(Mean({basis},{w2})))", [oi, basis])
        add("F1_OI_basis_premium_interaction", f"Sub(ZScore(Delta({oi},{w1})),ZScore(Mean({basis},{w2})))", [oi, basis])
        add("F1_OI_basis_premium_interaction", f"Add(ZScore(Delta({oi},{w1})),Neg(Rank(Mean({basis},{w2}))))", [oi, basis])
        add("F1_OI_basis_premium_interaction", f"Mul(Rank(Delta({oi},{w1})),Abs(ZScore(Mean({basis},{w2}))))", [oi, basis])
        add("F1_OI_basis_premium_interaction", f"Sub(Rank(Mean(Delta({oi},{w1}),{w2})),Rank(Mean({basis},{w2})))", [oi, basis])
        add("F1_OI_basis_premium_interaction", f"Mul(Clip(ZScore(Mean({basis},{w2}))),Sign(Delta({oi},{w1})))", [oi, basis])

    for oi, fund, w1, w2 in product(oi_fields, funding_fields, slow_windows, slow_windows):
        add("F2_OI_funding_crowding_interaction", f"Mul(Sign(Delta({oi},{w1})),Rank(Mean({fund},{w2})))", [oi, fund])
        add("F2_OI_funding_crowding_interaction", f"Add(ZScore(Delta({oi},{w1})),Neg(ZScore(Mean({fund},{w2}))))", [oi, fund])
        add("F2_OI_funding_crowding_interaction", f"Sub(Rank(Mean(Delta({oi},{w1}),{w2})),Rank(Mean({fund},{w2})))", [oi, fund])
        add("F2_OI_funding_crowding_interaction", f"Mul(Rank(Delta({oi},{w1})),Abs(ZScore(Mean({fund},{w2}))))", [oi, fund])
        add("F2_OI_funding_crowding_interaction", f"Mul(Clip(ZScore(Mean({fund},{w2}))),Sign(Delta({oi},{w1})))", [oi, fund])
        add("F2_OI_funding_crowding_interaction", f"Sub(Abs(ZScore(Delta({oi},{w1}))),Abs(ZScore(Mean({fund},{w2}))))", [oi, fund])

    for top, base, price, w1, w2 in product(position_fields + account_fields, global_fields, price_fields, slow_windows, [12, 24, 48, 72, 96]):
        add("F3_positioning_divergence", f"Sub(Rank(Mean({top},{w1})),Rank(Mean({base},{w1})))", [top, base])
        add("F3_positioning_divergence", f"Mul(Sub(Rank(Mean({top},{w1})),Rank(Mean({base},{w1}))),Sign(Delta({price},{w2})))", [top, base, price])
        add("F3_positioning_divergence", f"Add(ZScore(Delta({top},{w1})),Neg(ZScore(Delta({base},{w1}))))", [top, base])
        add("F3_positioning_divergence", f"Sub(ZScore(Mean({top},{w1})),ZScore(Mean({base},{w2})))", [top, base])
        add("F3_positioning_divergence", f"Mul(Sign(Delta({top},{w1})),Rank(Delta({price},{w2})))", [top, price])
        add("F3_positioning_divergence", f"Mul(Abs(ZScore(Delta({top},{w1}))),Neg(ZScore(Delta({base},{w2}))))", [top, base])
        add("F3_positioning_divergence", f"Sub(Rank(Delta({top},{w1})),Rank(Delta({base},{w2})))", [top, base])

    for oi, taker, w1, w2 in product(oi_fields, taker_fields, windows, windows):
        add("F4_OI_taker_flow_interaction", f"Mul(Sign(Delta({oi},{w1})),Rank(Delta({taker},{w2})))", [oi, taker])
        add("F4_OI_taker_flow_interaction", f"Sub(ZScore(Delta({oi},{w1})),ZScore(Mean({taker},{w2})))", [oi, taker])
        add("F4_OI_taker_flow_interaction", f"Add(ZScore(Delta({oi},{w1})),Neg(Rank(Delta({taker},{w2}))))", [oi, taker])
        add("F4_OI_taker_flow_interaction", f"Mul(Rank(Mean(Delta({oi},{w1}),{max(w1,w2)})),Sign(Delta({taker},{w2})))", [oi, taker])
        add("F4_OI_taker_flow_interaction", f"Sub(Abs(ZScore(Delta({oi},{w1}))),Abs(ZScore(Delta({taker},{w2}))))", [oi, taker])
        add("F4_OI_taker_flow_interaction", f"Mul(Clip(ZScore(Mean({taker},{w2}))),Sign(Delta({oi},{w1})))", [oi, taker])

    for oi, regime, w1 in product(oi_fields, regime_state_values, slow_windows):
        for state in regime_state_values[regime]:
            add("F5_OI_upper_regime_interaction", f"Mul(Rank(Delta({oi},{w1})),StateMask({regime},{state}))", [oi, regime])
        add("F5_OI_upper_regime_interaction", f"GroupNeutralize(Rank(Delta({oi},{w1})),{regime})", [oi, regime])

    for oi, latent, w1 in product(oi_fields, latent_fields, slow_windows):
        add("F6_OI_latent_state_interaction", f"LatentNeutralRank(Delta({oi},{w1}),{latent})", [oi, latent])
        add("F6_OI_latent_state_interaction", f"GroupNeutralize(Rank(Delta({oi},{w1})),{latent})", [oi, latent])
        add("F6_OI_latent_state_interaction", f"GroupNeutralize(ZScore(Mean({oi},{w1})),{latent})", [oi, latent])
        add("F6_OI_latent_state_interaction", f"Sub(Rank(Delta({oi},{w1})),GroupNeutralize(Rank(Delta({oi},{w1})),{latent}))", [oi, latent])
        for state in latent_state_values.get(latent, []):
            add("F6_OI_latent_state_interaction", f"Mul(Rank(Delta({oi},{w1})),StateMask({latent},{state}))", [oi, latent])
            add("F6_OI_latent_state_interaction", f"Mul(Sign(Delta({oi},{w1})),StateMask({latent},{state}))", [oi, latent])

    return specs, fields_by_expr


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    generated_at = now_utc()
    quota = pd.read_csv(QUOTA)
    field_contract = pd.read_csv(FIELD_CONTRACT)
    template_req = pd.read_csv(TEMPLATE_REQ)
    forbidden = pd.read_csv(FORBIDDEN)
    schema = schema_names(BASE_PANEL)
    field_meta = source_map(field_contract)

    specs, fields_by_expr = build_specs()
    spec_df = pd.DataFrame(specs)

    rows: list[dict[str, Any]] = []
    for q in quota.to_dict("records"):
        family_id = q["family_id"]
        target = int(q["dry_generation_min_candidates"])
        family_exprs = spec_df.loc[spec_df["family_id"] == family_id, "expression"].tolist()
        rows.extend(rows_from_specs(family_id, target, family_exprs, fields_by_expr))

    ledger = pd.DataFrame(rows)

    def validate_row(row: pd.Series) -> pd.Series:
        fields = split_contract_fields(row["fields"])
        operators = split_contract_fields(row["operator_signature"])
        missing_contract = [f for f in fields if f not in field_meta]
        missing_panel = [
            f
            for f in fields
            if f in field_meta
            and field_meta[f]["source_contract"].startswith("binance")
            and field_meta[f]["field_class"] == "raw_source"
            and f not in schema
        ]
        forbidden_terms = [
            term
            for term in ["okx", "okx_minus_binance", "cross_exchange", "funding_spread_okx", "direct_oi_price_level_gap"]
            if term in str(row["expression"]).lower() or term in str(row["fields"]).lower()
        ]
        unsupported_ops = [op for op in operators if op not in ALLOWED_OPERATORS]
        return pd.Series(
            {
                "candidate_id": row["candidate_id"],
                "objective_family": row["objective_family"],
                "missing_contract_fields": "|".join(missing_contract),
                "missing_panel_raw_fields": "|".join(missing_panel),
                "forbidden_terms": "|".join(forbidden_terms),
                "unsupported_operators": "|".join(unsupported_ops),
                "static_valid": not missing_contract and not missing_panel and not forbidden_terms and not unsupported_ops,
            }
        )

    static_audit = ledger.apply(validate_row, axis=1)
    valid_map = static_audit.set_index("candidate_id")["static_valid"].to_dict()
    ledger["historical_source_ok"] = ledger["candidate_id"].map(valid_map).fillna(False)
    ledger["field_lineage_ok"] = ledger["candidate_id"].map(valid_map).fillna(False)
    ledger["pit_policy_ok"] = ledger["candidate_id"].map(valid_map).fillna(False)

    selected_ids: set[str] = set()
    for q in quota.to_dict("records"):
        family = q["family_id"]
        n = int(q["preflight_min_candidates"])
        sub = ledger[(ledger["objective_family"] == family) & (ledger["historical_source_ok"])].copy()
        sub = sub.sort_values(["skeleton_key", "production_key", "candidate_id"])
        max_per_skeleton = max(1, int((n + 3) // 4))
        picks: list[str] = []
        for _, group in sub.groupby("skeleton_key", sort=True):
            for candidate_id in group.drop_duplicates("production_key").head(max_per_skeleton)["candidate_id"].tolist():
                if len(picks) < n:
                    picks.append(candidate_id)
        if len(picks) < n:
            for candidate_id in sub["candidate_id"].tolist():
                if candidate_id not in picks:
                    picks.append(candidate_id)
                if len(picks) >= n:
                    break
        selected_ids.update(picks[:n])
    ledger["selected_for_family_balanced_preflight"] = ledger["candidate_id"].isin(selected_ids)
    ledger["shared_pool_stage"] = ledger["selected_for_family_balanced_preflight"].map(
        {True: "selected_for_future_family_balanced_preflight", False: "dry_generated"}
    )

    family_quota = (
        ledger.groupby("objective_family")
        .agg(
            generated_count=("candidate_id", "count"),
            static_valid_count=("historical_source_ok", "sum"),
            selected_for_preflight_count=("selected_for_family_balanced_preflight", "sum"),
            unique_skeleton_count=("skeleton_key", "nunique"),
            unique_production_count=("production_key", "nunique"),
        )
        .reset_index()
        .merge(
            quota[["family_id", "dry_generation_min_candidates", "dry_generation_max_share", "preflight_min_candidates"]],
            left_on="objective_family",
            right_on="family_id",
            how="left",
        )
    )
    total = max(1, int(ledger.shape[0]))
    family_quota["generated_share"] = family_quota["generated_count"] / total
    family_quota["quota_pass"] = (
        (family_quota["generated_count"] >= family_quota["dry_generation_min_candidates"])
        & (family_quota["generated_share"] <= family_quota["dry_generation_max_share"] + 1e-12)
        & (family_quota["selected_for_preflight_count"] >= family_quota["preflight_min_candidates"])
    )

    skeleton_audit = (
        ledger.groupby("objective_family")
        .agg(
            candidate_count=("candidate_id", "count"),
            skeleton_count=("skeleton_key", "nunique"),
            production_count=("production_key", "nunique"),
            top_skeleton_count=("skeleton_key", lambda s: int(s.value_counts().iloc[0])),
            top_production_count=("production_key", lambda s: int(s.value_counts().iloc[0])),
        )
        .reset_index()
    )
    skeleton_audit["top_skeleton_share"] = skeleton_audit["top_skeleton_count"] / skeleton_audit["candidate_count"]
    skeleton_audit["top_production_share"] = skeleton_audit["top_production_count"] / skeleton_audit["candidate_count"]
    skeleton_audit["diversity_pass"] = (skeleton_audit["top_skeleton_share"] <= 0.25) & (
        skeleton_audit["top_production_share"] <= 0.20
    )

    field_source_rows = []
    for field, meta in sorted(field_meta.items()):
        field_source_rows.append(
            {
                "field_name": field,
                "source_contract": meta["source_contract"],
                "field_class": meta["field_class"],
                "pit_policy": meta["pit_policy"],
                "in_base_panel_schema": field in schema,
                "allowed_for_historical_dry_generation": meta["allowed_for_historical_dry_generation"],
            }
        )
    field_source_audit = pd.DataFrame(field_source_rows)

    forbidden_audit = pd.DataFrame(
        [
            {
                "forbidden_item": row["item"],
                "policy": row["policy"],
                "candidate_hit_count": int(
                    ledger["expression"].astype(str).str.lower().str.contains(str(row["item"]).lower(), regex=False).sum()
                ),
            }
            for row in forbidden.to_dict("records")
        ]
    )

    all_quota_pass = bool(family_quota["quota_pass"].all())
    all_static_pass = bool(static_audit["static_valid"].all())
    all_diversity_pass = bool(skeleton_audit["diversity_pass"].all())
    blockers: list[str] = []
    if not all_quota_pass:
        blockers.append("family_quota_fail")
    if not all_static_pass:
        blockers.append("static_validity_fail")
    if not all_diversity_pass:
        blockers.append("skeleton_or_production_diversity_fail")

    decision = (
        "PASS_A7AL2X3_FAMILY_BALANCED_DRY_GENERATION_LEDGER_READY_FOR_PREFLIGHT_REVIEW"
        if not blockers
        else "HOLD_A7AL2X3_FAMILY_BALANCED_DRY_GENERATION_STATIC_BLOCKERS"
    )
    manifest = {
        "decision": decision,
        "generated_at": generated_at,
        "executes_generation": True,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "authorizes_replay": False,
        "authorizes_a7al2y_generation": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "generated_count": int(ledger.shape[0]),
        "family_count": int(ledger["objective_family"].nunique()),
        "selected_for_future_preflight_count": int(ledger["selected_for_family_balanced_preflight"].sum()),
        "static_valid_count": int(static_audit["static_valid"].sum()),
        "blockers": blockers,
        "base_panel_schema_fields": int(len(schema)),
    }
    authorization = {
        "decision": decision,
        "a7al2x4_family_balanced_replay_preflight": "READY_FOR_REVIEW_NOT_AUTHORIZED",
        "a7al2y_generation": "NOT_AUTHORIZED",
        "large_formula_search": "NOT_AUTHORIZED",
        "alpha_proof": "NOT_AUTHORIZED",
        "shadow_paper_live": "NOT_AUTHORIZED",
        "reason": "A7AL-2X3 is dry generation and ledger construction only; replay/preflight requires a separate authorization record.",
    }

    ledger.to_csv(RUNTIME / "a7al2x3_generated_candidate_ledger.csv", index=False)
    ledger.to_csv(RUNTIME / "a7al2x3_shared_pool_ledger.csv", index=False)
    family_quota.to_csv(RUNTIME / "a7al2x3_family_quota_audit.csv", index=False)
    static_audit.to_csv(RUNTIME / "a7al2x3_static_validity_audit.csv", index=False)
    field_source_audit.to_csv(RUNTIME / "a7al2x3_field_source_audit.csv", index=False)
    skeleton_audit.to_csv(RUNTIME / "a7al2x3_skeleton_diversity_audit.csv", index=False)
    forbidden_audit.to_csv(RUNTIME / "a7al2x3_forbidden_fallback_audit.csv", index=False)
    pd.DataFrame(CONTROL_MODES, columns=["control_mode"]).to_csv(RUNTIME / "a7al2x3_negative_control_plan.csv", index=False)
    write_json(RUNTIME / "a7al2x3_manifest.json", manifest)
    write_json(RUNTIME / "a7al2x3_authorization_matrix.json", authorization)

    report = f"""# CRYPTO A7AL-2X3 Family-Balanced Dry Generation Smoke

Generated: {generated_at}

## Decision

```text
{decision}
```

This stage executes dry candidate generation and shared-ledger construction only. It performs no replay, no selector scoring, no training, and no alpha proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Family Quota Audit

{md_table(family_quota)}

## Skeleton Diversity Audit

{md_table(skeleton_audit)}

## Field Source Audit

{md_table(field_source_audit)}

## Forbidden Fallback Audit

{md_table(forbidden_audit)}

## Authorization

```json
{json.dumps(authorization, indent=2, sort_keys=True)}
```

## Boundary

```text
No replay.
No search execution.
No May in generation / ranking / selector / mutation.
No alpha proof / shadow / paper / live.

A7AL-2X4 family-balanced replay preflight requires a separate authorization record.
```
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
