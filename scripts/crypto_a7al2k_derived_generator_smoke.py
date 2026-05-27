from __future__ import annotations

import csv
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

try:
    import pyarrow.dataset as ds
except Exception:  # pragma: no cover - optional import guard for report-only environments
    ds = None  # type: ignore[assignment]


REPO = Path(__file__).resolve().parents[1]
DATE_TAG = "20260527"
OUT_DIR = REPO / "runtime" / "a7al2k_derived_generator_smoke"
REPORT = REPO / "reports" / f"CRYPTO_A7AL2K_DERIVED_GENERATOR_SMOKE_{DATE_TAG}.md"

A7AL2J = REPO / "runtime" / "a7al2j_derived_tolerant_search_reset" / "a7al2j_manifest.json"
A7AL2J_CELLS = REPO / "runtime" / "a7al2j_derived_tolerant_search_reset" / "a7al2j_generator_cells.csv"
A7AL2J_POLICY = REPO / "runtime" / "a7al2j_derived_tolerant_search_reset" / "a7al2j_relaxed_selector_policy.csv"
A7AS0 = REPO / "runtime" / "a7as0_v2_data_acceptance" / "a7as0_manifest.json"
A7AL0R_LINEAGE = REPO / "runtime" / "a7al0r_code_feature_regime_readiness_audit" / "a7al0r_feature_lineage_ledger.csv"


SUPPORTED_OPERATORS = {"Mean", "Delta", "Rank", "CSRank", "ZScore", "Mul", "Sub", "Add", "Neg", "Abs", "Sign"}
CONTROL_MODES = [
    "one_bar_lag",
    "wrong_lag_future_24h",
    "wrong_lag_stale_168h",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_random",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def md_table(df: pd.DataFrame, limit: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(limit).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(limit).to_string(index=False) + "\n```"


def digest(value: str, length: int = 16) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:length]


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
    return tuple(sorted({int(match) for match in re.findall(r",\s*(\d+)\s*\)", expression)}))


def extract_fields(expression: str) -> tuple[str, ...]:
    tokens = set(re.findall(r"\b[a-z][a-z0-9_]*\b", expression))
    op_lower = {op.lower() for op in extract_operators(expression)}
    return tuple(sorted(tokens - op_lower - {"nan", "inf"}))


def schema_names(path: str | Path) -> set[str]:
    if not path or ds is None:
        return set()
    try:
        return set(ds.dataset(str(path), format="parquet").schema.names)
    except Exception:
        return set()


def field_family(field: str) -> str:
    name = field.lower()
    if name in {"trade_close", "mark_close", "index_close", "trade_return_1h", "mark_trade_basis_bps"}:
        return "price"
    if any(token in name for token in ["high", "low", "realized_vol", "range", "volatility"]):
        return "volatility"
    if any(token in name for token in ["quote_volume", "trade_volume", "trade_count", "liquidity", "taker_buy_quote"]):
        return "liquidity"
    if "open_interest" in name or name.startswith("oi_"):
        return "open_interest"
    if "long_short" in name or "position" in name or "taker_buy_sell" in name:
        return "positioning"
    if "funding" in name:
        return "funding"
    if "basis" in name or "premium" in name:
        return "basis"
    if "age" in name or "listing" in name or "history_length" in name:
        return "listing_age"
    if name.startswith("okx_") or "spread_okx" in name or "okx_minus_binance" in name:
        return "cross_exchange"
    return "misc"


@dataclass(frozen=True)
class CandidateSpec:
    cell: str
    family: str
    expression: str
    feature_role: str
    diagnostic_only: bool = False


class DerivedCandidateGenerator:
    def __init__(self, seed: str, base_fields: set[str], overlay_fields: set[str]) -> None:
        self.rng = random.Random(int(digest(seed, 12), 16))
        self.base_fields = base_fields
        self.overlay_fields = overlay_fields
        self.windows = [4, 8, 12, 24, 48, 72, 96, 168, 336, 504, 720]
        self.pools = {
            "price": [f for f in ["trade_close", "mark_close", "index_close"] if f in base_fields],
            "high": [f for f in ["trade_high", "mark_high", "index_high"] if f in base_fields],
            "low": [f for f in ["trade_low", "mark_low", "index_low"] if f in base_fields],
            "liquidity": [f for f in ["trade_quote_volume", "trade_volume", "trade_count", "taker_buy_quote_volume", "kline_taker_buy_quote_share"] if f in base_fields],
            "oi": [f for f in ["open_interest_last", "open_interest_mean", "open_interest_value_last", "open_interest_value_mean"] if f in base_fields],
            "positioning": [
                f
                for f in [
                    "global_long_short_account_ratio_last",
                    "global_long_short_account_ratio_mean",
                    "top_long_short_account_ratio_last",
                    "top_long_short_account_ratio_mean",
                    "top_long_short_position_ratio_last",
                    "top_long_short_position_ratio_mean",
                    "taker_buy_sell_volume_ratio_last",
                    "taker_buy_sell_volume_ratio_mean",
                ]
                if f in base_fields
            ],
            "basis": [f for f in ["premium_close", "premium_close_bps", "mark_index_basis_bps", "mark_trade_basis_bps"] if f in base_fields],
            "funding": [f for f in ["funding_rate"] if f in base_fields],
            "overlay": [
                f
                for f in [
                    "funding_spread_okx_minus_binance",
                    "okx_internal_mark_index_basis_bps",
                    "binance_internal_mark_index_basis_bps",
                    "oi_usd_spread_okx_minus_binance",
                    "oi_usd_ratio_okx_over_binance",
                    "oi_coin_ratio_okx_over_binance",
                    "taker_ratio_spread_okx_minus_binance",
                    "okx_contracts_taker_buy_share",
                    "okx_contracts_taker_buy_sell_ratio",
                    "oi_value_ratio_from_crowding_endpoint_okx_over_binance",
                ]
                if f in overlay_fields
            ],
        }

    def choice(self, key: str) -> str:
        values = self.pools[key]
        if not values:
            raise ValueError(f"empty field pool: {key}")
        return values[self.rng.randrange(len(values))]

    def w(self, *, min_value: int = 4) -> int:
        choices = [window for window in self.windows if window >= min_value]
        return choices[self.rng.randrange(len(choices))]

    def expression_for_cell(self, cell: str) -> CandidateSpec:
        if cell == "J0_oi_derived_state":
            oi = self.choice("oi")
            price = self.choice("price")
            w1, w2, w3 = self.w(), self.w(), self.w(min_value=24)
            w4 = self.w(min_value=48)
            templates = [
                f"Mul(ZScore(Delta({oi},{w1})),ZScore(Delta({price},{w2})))",
                f"Sub(ZScore(Delta({oi},{w1})),Rank(Delta({price},{w2})))",
                f"Mul(Rank(Mean(Delta({oi},{w1}),{w3})),Sign(Delta({price},{w2})))",
                f"Add(ZScore(Delta({oi},{w1})),Neg(ZScore(Delta({price},{w2}))))",
                f"Sub(ZScore(Mean({oi},{w3})),ZScore(Mean({oi},{w4})))",
                f"Sub(Rank(Delta({oi},{w1})),Rank(Delta({oi},{w2})))",
                f"Mul(Abs(ZScore(Delta({oi},{w1}))),Neg(ZScore(Delta({price},{w2}))))",
                f"Add(Rank(Mean({oi},{w3})),Neg(Rank(Mean({price},{w2}))))",
                f"Mul(Sign(Delta({oi},{w1})),Abs(ZScore(Delta({price},{w2}))))",
                f"Sub(Abs(ZScore(Mean({oi},{w3}))),Abs(ZScore(Mean({price},{w2}))))",
                f"Rank(Delta({oi},{w1}))",
                f"ZScore(Mean(Delta({oi},{w1}),{w3}))",
                f"Mul(Rank(Mean({oi},{w3})),Sign(Delta({oi},{w1})))",
                f"Add(ZScore(Mean({oi},{w3})),Neg(ZScore(Mean({oi},{w4}))))",
            ]
            return CandidateSpec(cell, "derived_oi_price_state", self.rng.choice(templates), "derived_interaction")
        if cell == "J1_vol_range_structure":
            high = self.choice("high")
            low = self.choice("low")
            price = self.choice("price")
            w1, w2, w3 = self.w(), self.w(), self.w(min_value=24)
            w4 = self.w(min_value=48)
            templates = [
                f"Sub(Rank(Mean(Sub({high},{low}),{w1})),Rank(Mean(Abs(Delta({price},{w2})),{w3})))",
                f"Mul(ZScore(Mean(Sub({high},{low}),{w1})),Neg(ZScore(Delta({price},{w2}))))",
                f"Add(Rank(Delta({price},{w2})),Neg(Rank(Mean(Sub({high},{low}),{w1}))))",
                f"Mul(Sign(Delta({price},{w2})),Abs(ZScore(Mean(Sub({high},{low}),{w1}))))",
                f"Sub(ZScore(Mean(Sub({high},{low}),{w1})),ZScore(Mean(Sub({high},{low}),{w4})))",
                f"Rank(Mean(Sub({high},{low}),{w3}))",
                f"ZScore(Delta(Sub({high},{low}),{w1}))",
                f"Mul(Rank(Mean(Sub({high},{low}),{w1})),Sign(Delta(Sub({high},{low}),{w2})))",
                f"Sub(Abs(ZScore(Delta({price},{w2}))),Abs(ZScore(Delta(Sub({high},{low}),{w1}))))",
                f"Add(ZScore(Mean(Sub({high},{low}),{w3})),Neg(Rank(Delta(Sub({high},{low}),{w1}))))",
                f"Mul(Abs(ZScore(Mean(Sub({high},{low}),{w3}))),Rank(Delta({price},{w2})))",
                f"Sub(Rank(Delta(Sub({high},{low}),{w1})),Rank(Mean(Sub({high},{low}),{w4})))",
                f"Mul(Sign(Delta(Sub({high},{low}),{w1})),ZScore(Mean(Sub({high},{low}),{w3})))",
                f"Add(Rank(Mean(Abs(Delta({price},{w2})),{w3})),Neg(ZScore(Mean(Sub({high},{low}),{w1}))))",
            ]
            return CandidateSpec(cell, "derived_vol_range_state", self.rng.choice(templates), "derived_rolling")
        if cell == "J2_liquidity_lifecycle":
            liq = self.choice("liquidity")
            price = self.choice("price")
            w1, w2, w3 = self.w(), self.w(), self.w(min_value=48)
            w4 = self.w(min_value=168)
            templates = [
                f"Mul(Rank(Mean({liq},{w1})),ZScore(Delta({price},{w2})))",
                f"Sub(Rank(Mean({liq},{w3})),Rank(Mean({liq},{w1})))",
                f"Mul(ZScore(Delta({liq},{w1})),Sign(Delta({price},{w2})))",
                f"Add(Rank(Mean({liq},{w1})),Neg(Rank(Delta({price},{w2}))))",
                f"ZScore(Mean(Delta({liq},{w1}),{w3}))",
                f"Rank(Delta({liq},{w1}))",
                f"Sub(ZScore(Mean({liq},{w1})),ZScore(Mean({liq},{w4})))",
                f"Mul(Abs(ZScore(Delta({liq},{w1}))),Rank(Mean({liq},{w3})))",
                f"Add(ZScore(Delta({liq},{w1})),Neg(ZScore(Mean({liq},{w3}))))",
                f"Sub(Rank(Delta({liq},{w1})),Rank(Mean({price},{w2})))",
                f"Mul(Sign(Delta({liq},{w1})),Abs(ZScore(Mean({liq},{w3}))))",
                f"Add(Rank(Mean({liq},{w3})),Neg(ZScore(Delta({price},{w2}))))",
                f"Mul(Rank(Mean({liq},{w1})),Sign(Delta({liq},{w2})))",
                f"Sub(Abs(ZScore(Mean({liq},{w1}))),Abs(ZScore(Mean({liq},{w4}))))",
            ]
            return CandidateSpec(cell, "derived_liquidity_lifecycle", self.rng.choice(templates), "derived_rolling")
        if cell == "J3_basis_funding_derived":
            basis = self.choice("basis")
            funding = self.choice("funding")
            w1, w2 = self.w(), self.w()
            w3 = self.w(min_value=48)
            templates = [
                f"Sub(Abs(ZScore(Mean({basis},{w1}))),Abs(ZScore(Mean({funding},{w2}))))",
                f"Mul(Sign(Delta({basis},{w1})),ZScore(Mean({funding},{w2})))",
                f"Add(Rank(Delta({basis},{w1})),Neg(ZScore(Mean({funding},{w2}))))",
                f"Mul(Rank(Mean({basis},{w1})),Sign(Delta({funding},{w2})))",
                f"Sub(ZScore(Mean({basis},{w1})),ZScore(Mean({basis},{w3})))",
                f"Sub(ZScore(Mean({funding},{w1})),ZScore(Mean({funding},{w3})))",
                f"Rank(Delta({basis},{w1}))",
                f"ZScore(Mean(Delta({funding},{w1}),{w3}))",
                f"Mul(Abs(ZScore(Mean({basis},{w1}))),Sign(Delta({funding},{w2})))",
                f"Mul(Abs(ZScore(Mean({funding},{w1}))),Sign(Delta({basis},{w2})))",
                f"Add(Rank(Mean({basis},{w1})),Neg(Rank(Mean({funding},{w2}))))",
                f"Sub(Rank(Delta({basis},{w1})),Rank(Delta({funding},{w2})))",
                f"Mul(Rank(Mean({basis},{w3})),Rank(Mean({funding},{w1})))",
                f"Add(ZScore(Delta({basis},{w1})),Neg(ZScore(Delta({funding},{w2}))))",
            ]
            return CandidateSpec(cell, "derived_basis_funding_state", self.rng.choice(templates), "derived_interaction")
        if cell == "J4_upper_regime_interaction":
            liq = self.choice("liquidity")
            oi = self.choice("oi")
            funding = self.choice("funding")
            price = self.choice("price")
            basis = self.choice("basis")
            w1, w2, w3 = self.w(min_value=24), self.w(min_value=48), self.w(min_value=24)
            templates = [
                f"Mul(Rank(Mean({liq},{w1})),Rank(Mean({oi},{w2})))",
                f"Mul(Abs(ZScore(Mean({funding},{w1}))),Neg(ZScore(Delta({price},{w3}))))",
                f"Mul(Abs(ZScore(Mean({basis},{w1}))),Rank(Mean({liq},{w2})))",
                f"Add(ZScore(Delta({oi},{w1})),Neg(ZScore(Mean({funding},{w2}))))",
                f"Sub(Rank(Mean({liq},{w2})),Rank(Mean({oi},{w1})))",
                f"Sub(Abs(ZScore(Mean({basis},{w1}))),Abs(ZScore(Mean({funding},{w2}))))",
                f"Mul(Sign(Delta({oi},{w1})),Rank(Mean({liq},{w2})))",
                f"Mul(Sign(Delta({basis},{w1})),Abs(ZScore(Mean({funding},{w2}))))",
                f"Add(Rank(Mean({liq},{w1})),Neg(Rank(Mean({funding},{w2}))))",
                f"Sub(ZScore(Delta({oi},{w1})),ZScore(Delta({price},{w3})))",
                f"Mul(Rank(Mean({basis},{w1})),Rank(Mean({oi},{w2})))",
                f"Add(ZScore(Mean({funding},{w1})),Neg(ZScore(Delta({price},{w3}))))",
                f"Mul(Abs(ZScore(Delta({liq},{w1}))),Sign(Delta({oi},{w2})))",
                f"Sub(Rank(Delta({basis},{w1})),Rank(Delta({price},{w3})))",
            ]
            return CandidateSpec(cell, "derived_upper_regime_proxy", self.rng.choice(templates), "upper_regime_proxy")
        if cell == "J5_cross_exchange_overlay_diagnostic":
            if not self.pools["overlay"]:
                raise ValueError("J5_cross_exchange_overlay_diagnostic requires canonical overlay fields; silent fallback is forbidden")
            overlay = self.choice("overlay")
            price = self.choice("price")
            w1, w2 = self.w(), self.w()
            templates = [
                f"Mul(ZScore(Mean({overlay},{w1})),ZScore(Delta({price},{w2})))",
                f"Sub(Rank(Mean({overlay},{w1})),Rank(Delta({price},{w2})))",
                f"Mul(Sign(Delta({overlay},{w1})),Rank(Mean({price},{w2})))",
            ]
            return CandidateSpec(cell, "cross_exchange_overlay_diagnostic", self.rng.choice(templates), "cross_exchange_30d_overlay", diagnostic_only=True)
        raise ValueError(f"unsupported cell: {cell}")


def validate_expression(expression: str, base_fields: set[str], overlay_fields: set[str]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    operators = set(extract_operators(expression))
    unknown_ops = sorted(operators - SUPPORTED_OPERATORS)
    if unknown_ops:
        reasons.append("unsupported_operator:" + "|".join(unknown_ops))
    fields = set(extract_fields(expression))
    allowed = base_fields | overlay_fields
    unknown = sorted(fields - allowed)
    if unknown:
        reasons.append("unknown_field:" + "|".join(unknown[:8]))
    forbidden = sorted(field for field in fields if field.startswith("forward_") or field.startswith("fwd_") or "future" in field)
    if forbidden:
        reasons.append("label_or_future_field:" + "|".join(forbidden))
    if "Mul(" in expression:
        # Keep products normalized or sign/rank guarded. This does not reject
        # derived fields; it rejects unbounded raw products.
        mul_bodies = re.findall(r"Mul\((.*)\)", expression)
        if any(not any(prefix in body for prefix in ("ZScore(", "Rank(", "Sign(", "Abs(")) for body in mul_bodies):
            reasons.append("unsafe_mul_input")
    return not reasons, reasons


def selected_diversity_cap(candidates: pd.DataFrame, target: int) -> pd.DataFrame:
    eligible = candidates[(candidates["static_valid"]) & (~candidates["diagnostic_only"])].copy()
    eligible = eligible.sort_values(["cell", "candidate_id"]).copy()

    selected_ids: set[str] = set()
    skeleton_counts: Counter[str] = Counter()
    field_family_counts: Counter[str] = Counter()
    cell_counts: Counter[str] = Counter()

    # Pass 1: one candidate per skeleton where possible.
    for _, row in eligible.iterrows():
        skeleton_key = str(row["skeleton_key"])
        if skeleton_counts[skeleton_key] > 0:
            continue
        selected_ids.add(str(row["candidate_id"]))
        skeleton_counts[skeleton_key] += 1
        cell_counts[str(row["cell"])] += 1
        for family in str(row["field_families"]).split("|"):
            if family:
                field_family_counts[family] += 1
        if len(selected_ids) >= target:
            break

    # Pass 2: fill with loose caps using cell round-robin. A simple sorted pass
    # lets early cells consume shared skeleton capacity and starves later cells.
    # The round-robin is still static and deterministic, but it measures the
    # generator instead of the CSV sort order.
    grouped = {
        str(cell): group.reset_index(drop=True)
        for cell, group in eligible.groupby("cell", sort=True)
    }
    cursors = {cell: 0 for cell in grouped}
    changed = True
    while len(selected_ids) < target and changed:
        changed = False
        for cell in sorted(grouped):
            group = grouped[cell]
            while cursors[cell] < len(group):
                row = group.iloc[cursors[cell]]
                cursors[cell] += 1
                candidate_id = str(row["candidate_id"])
                if candidate_id in selected_ids:
                    continue
                skeleton_key = str(row["skeleton_key"])
                families = [f for f in str(row["field_families"]).split("|") if f]
                if skeleton_counts[skeleton_key] >= 24:
                    continue
                if cell_counts[cell] >= max(48, target // 4):
                    continue
                if any(field_family_counts[f] >= int(target * 0.30) for f in families):
                    continue
                selected_ids.add(candidate_id)
                skeleton_counts[skeleton_key] += 1
                cell_counts[cell] += 1
                for family in families:
                    field_family_counts[family] += 1
                changed = True
                break
            if len(selected_ids) >= target:
                break

    result = candidates.copy()
    result["selected_for_a7al2l_replay_preflight"] = result["candidate_id"].astype(str).isin(selected_ids)
    result["selector_reason"] = "not_selected"
    result.loc[result["diagnostic_only"], "selector_reason"] = "diagnostic_overlay_not_historical_replay"
    result.loc[~result["static_valid"], "selector_reason"] = "static_validation_failed"
    result.loc[result["selected_for_a7al2l_replay_preflight"], "selector_reason"] = "selected_diversity_capped"
    result.loc[
        (result["static_valid"]) & (~result["diagnostic_only"]) & (~result["selected_for_a7al2l_replay_preflight"]),
        "selector_reason",
    ] = "eligible_not_selected_by_budget_or_caps"
    return result


def top_share(series: pd.Series) -> tuple[str, int, float]:
    if series.empty:
        return "", 0, 0.0
    counts = series.astype(str).value_counts()
    return str(counts.index[0]), int(counts.iloc[0]), float(counts.iloc[0] / len(series))


def token_top_share(series: pd.Series) -> tuple[str, int, float]:
    tokens: list[str] = []
    for value in series.astype(str):
        tokens.extend([part for part in value.split("|") if part])
    if not tokens:
        return "", 0, 0.0
    counts = Counter(tokens)
    key, count = counts.most_common(1)[0]
    return key, int(count), float(count / len(tokens))


def make_control_rows(selected: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for _, row in selected.iterrows():
        for mode in CONTROL_MODES:
            rows.append(
                {
                    "candidate_id": row["candidate_id"],
                    "control_id": f"{row['candidate_id']}__{mode}",
                    "control_mode": mode,
                    "matched_cell": row["cell"],
                    "matched_family": row["family"],
                    "required_for_replay_preflight": True,
                }
            )
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    a7al2j = read_json(A7AL2J)
    a7as0 = read_json(A7AS0)
    if a7al2j.get("decision") != "PASS_A7AL2J_DERIVED_TOLERANT_RESET_READY_FOR_A7AL2K":
        raise SystemExit("A7AL-2J is not ready for A7AL-2K")

    base_path = ((a7as0.get("base_summary") or {}).get("path") or "")
    overlay_path = ((a7as0.get("overlay_summary") or {}).get("path") or "")
    base_fields = schema_names(base_path)
    overlay_fields = schema_names(overlay_path)
    lineage = pd.read_csv(A7AL0R_LINEAGE)
    allowed_lineage = lineage[
        (lineage["allowed_for_search"].astype(str) == "True")
        & (lineage["uses_future"].astype(str) != "True")
        & (lineage["uses_label"].astype(str) != "True")
    ].copy()

    cell_rows = pd.read_csv(A7AL2J_CELLS)
    policy_rows = pd.read_csv(A7AL2J_POLICY)
    policy = {str(row["rule"]): str(row["value"]) for _, row in policy_rows.iterrows()}
    generation_cap = int(policy.get("generation_cap", "8000"))
    selector_cap = int(policy.get("selector_cap", "768"))

    generator = DerivedCandidateGenerator("a7al2k_derived_generator_smoke", base_fields, overlay_fields)
    non_control_cells = [cell for cell in cell_rows["cell"].astype(str).tolist() if cell != "J6_controls_placebo"]
    budget_by_cell: dict[str, int] = {}
    allocated = 0
    for _, row in cell_rows.iterrows():
        cell = str(row["cell"])
        if cell == "J6_controls_placebo":
            continue
        count = int(round(float(row["budget_share"]) * generation_cap))
        budget_by_cell[cell] = count
        allocated += count
    if allocated < generation_cap:
        budget_by_cell[non_control_cells[0]] += generation_cap - allocated
    elif allocated > generation_cap:
        budget_by_cell[non_control_cells[0]] = max(0, budget_by_cell[non_control_cells[0]] - (allocated - generation_cap))

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    max_attempts = generation_cap * 80
    attempts = 0
    for cell, target in budget_by_cell.items():
        produced = 0
        while produced < target and attempts < max_attempts:
            attempts += 1
            spec = generator.expression_for_cell(cell)
            expr = canonical(spec.expression)
            if expr in seen:
                continue
            seen.add(expr)
            fields = extract_fields(expr)
            families = sorted({field_family(field) for field in fields})
            operators = extract_operators(expr)
            windows = extract_windows(expr)
            static_valid, reasons = validate_expression(expr, base_fields, overlay_fields)
            candidate_id = f"a7al2k_{digest(cell + expr, 16)}"
            row = {
                "candidate_id": candidate_id,
                "cell": cell,
                "family": spec.family,
                "expression": expr,
                "fields": "|".join(fields),
                "field_families": "|".join(families),
                "operators": "|".join(sorted(set(operators))),
                "windows": "|".join(str(w) for w in windows),
                "feature_role": spec.feature_role,
                "diagnostic_only": spec.diagnostic_only,
                "static_valid": static_valid,
                "static_reject_reasons": "|".join(reasons),
                "expression_key": f"expr-{digest(expr)}",
                "skeleton_key": f"skeleton-{digest(skeleton(expr))}",
                "production_key": "::".join(["a7al2k_derived_generator", spec.family, "|".join(families), "|".join(str(w) for w in windows)]),
                "label_or_future_field_count": sum(1 for field in fields if field.startswith("forward_") or field.startswith("fwd_") or "future" in field),
                "lineage_allowed_fields": sum(1 for field in fields if field in set(allowed_lineage["field_name"].astype(str))),
                "base_field_count": sum(1 for field in fields if field in base_fields),
                "overlay_field_count": sum(1 for field in fields if field in overlay_fields),
            }
            rows.append(row)
            produced += 1

    candidates = pd.DataFrame(rows)
    candidates = selected_diversity_cap(candidates, selector_cap)
    selected = candidates[candidates["selected_for_a7al2l_replay_preflight"]].copy()
    control_rows = make_control_rows(selected)

    quota_summary = candidates.groupby("cell", dropna=False).agg(
        generated=("candidate_id", "count"),
        static_valid=("static_valid", "sum"),
        selected=("selected_for_a7al2l_replay_preflight", "sum"),
        diagnostic_only=("diagnostic_only", "sum"),
    ).reset_index()
    reject_summary = candidates.groupby("selector_reason", dropna=False).size().reset_index(name="count")
    feature_lineage_audit = pd.DataFrame(
        [
            {
                "check": "a7al2j_ready",
                "status": "PASS" if a7al2j.get("decision") == "PASS_A7AL2J_DERIVED_TOLERANT_RESET_READY_FOR_A7AL2K" else "FAIL",
                "detail": str(a7al2j.get("decision")),
            },
            {
                "check": "base_schema_available",
                "status": "PASS" if base_fields else "FAIL",
                "detail": str(len(base_fields)),
            },
            {
                "check": "overlay_schema_available",
                "status": "PASS" if overlay_fields else "WARN",
                "detail": str(len(overlay_fields)),
            },
            {
                "check": "label_future_field_block",
                "status": "PASS" if int(candidates["label_or_future_field_count"].sum()) == 0 else "FAIL",
                "detail": str(int(candidates["label_or_future_field_count"].sum())),
            },
            {
                "check": "diagnostic_overlay_excluded_from_historical_selection",
                "status": "PASS" if int(selected["diagnostic_only"].sum()) == 0 else "FAIL",
                "detail": str(int(selected["diagnostic_only"].sum())),
            },
        ]
    )
    diversity_rows = []
    for name, value, cap in [
        ("top_skeleton_share", selected["skeleton_key"], 0.15),
        ("top_production_key_share", selected["production_key"], 0.20),
        ("top_cell_share", selected["cell"], 0.30),
    ]:
        top, count, share = top_share(value)
        diversity_rows.append({"metric": name, "top_value": top, "top_count": count, "share": share, "cap": cap, "pass": share <= cap})
    top_ff, top_ff_count, top_ff_share = token_top_share(selected["field_families"])
    diversity_rows.append({"metric": "top_field_family_token_share", "top_value": top_ff, "top_count": top_ff_count, "share": top_ff_share, "cap": 0.30, "pass": top_ff_share <= 0.30})
    diversity = pd.DataFrame(diversity_rows)

    control_audit = pd.DataFrame(
        [
            {"check": "selected_candidates", "status": "PASS" if len(selected) == selector_cap else "FAIL", "detail": str(len(selected))},
            {"check": "matched_control_rows", "status": "PASS" if len(control_rows) == len(selected) * len(CONTROL_MODES) else "FAIL", "detail": str(len(control_rows))},
            {"check": "one_bar_lag_attached", "status": "PASS" if any(row["control_mode"] == "one_bar_lag" for row in control_rows) else "FAIL", "detail": "one_bar_lag"},
            {"check": "wrong_lag_future_attached", "status": "PASS" if any(row["control_mode"] == "wrong_lag_future_24h" for row in control_rows) else "FAIL", "detail": "wrong_lag_future_24h"},
            {"check": "same_family_random_attached", "status": "PASS" if any(row["control_mode"] == "same_family_random" for row in control_rows) else "FAIL", "detail": "same_family_random"},
        ]
    )

    blockers: list[str] = []
    if len(candidates) != generation_cap:
        blockers.append("generation_cap_not_met")
    if len(selected) != selector_cap:
        blockers.append("selector_cap_not_met")
    if selected["skeleton_key"].nunique() < 40:
        blockers.append("selected_skeleton_count_below_40")
    if top_ff_share > 0.30:
        blockers.append("top_field_family_share_above_30pct")
    if not bool(diversity["pass"].all()):
        blockers.append("diversity_cap_failed")
    if int(candidates["label_or_future_field_count"].sum()) > 0:
        blockers.append("label_or_future_field_generated")
    if int(selected["diagnostic_only"].sum()) > 0:
        blockers.append("diagnostic_overlay_selected_for_historical_replay")
    if not bool((control_audit["status"] == "PASS").all()):
        blockers.append("control_attachment_failed")

    decision = "PASS_A7AL2K_DERIVED_GENERATOR_SMOKE_READY_FOR_A7AL2L" if not blockers else "HOLD_A7AL2K_DERIVED_GENERATOR_SMOKE"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "generated_candidates": int(len(candidates)),
        "selector_cap": selector_cap,
        "selected_for_a7al2l_replay_preflight": int(len(selected)),
        "selected_skeleton_count": int(selected["skeleton_key"].nunique()),
        "selected_cell_count": int(selected["cell"].nunique()),
        "selected_field_family_count": int(len(set("|".join(selected["field_families"]).split("|")) - {""})),
        "control_rows": int(len(control_rows)),
        "blockers": blockers,
        "executes_formula_generation": True,
        "executes_replay": False,
        "authorizes_a7al2l_replay_preflight": not blockers,
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "policy": "derived formulas are allowed broadly; label/PIT/control requirements are not relaxed",
    }

    candidates.to_csv(OUT_DIR / "a7al2k_generated_candidates.csv", index=False)
    selected.to_csv(OUT_DIR / "a7al2k_selected_candidates.csv", index=False)
    pd.DataFrame(control_rows).to_csv(OUT_DIR / "a7al2k_control_attachment_audit.csv", index=False)
    quota_summary.to_csv(OUT_DIR / "a7al2k_cell_quota_summary.csv", index=False)
    reject_summary.to_csv(OUT_DIR / "a7al2k_selector_trace_summary.csv", index=False)
    feature_lineage_audit.to_csv(OUT_DIR / "a7al2k_feature_lineage_audit.csv", index=False)
    diversity.to_csv(OUT_DIR / "a7al2k_diversity_summary.csv", index=False)
    write_json(OUT_DIR / "a7al2k_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2K Derived Generator Smoke

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

## Summary

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Cell Quotas

{md_table(quota_summary)}

## Selector Trace

{md_table(reject_summary)}

## Diversity

{md_table(diversity)}

## Feature Lineage Audit

{md_table(feature_lineage_audit)}

## Control Attachment

{md_table(control_audit)}

## Boundary

```text
This stage executes formula generation only.
It does not execute replay, alpha proof, shadow, paper, or live.

Derived-field tolerance is intentionally high:
  rolling / interaction / cross-sectional / upper-regime proxy formulas are allowed.

Not relaxed:
  no forward labels as features
  matched controls required
  one-bar-lag control required
  30d cross-exchange overlay excluded from historical replay selection
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
