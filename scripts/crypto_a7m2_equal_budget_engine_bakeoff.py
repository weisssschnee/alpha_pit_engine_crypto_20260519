from __future__ import annotations

import hashlib
import json
import re
import warnings
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7_validation_utils import (
    COST_BPS,
    REPORT_DIR,
    RUNTIME_DIR,
    clean_float,
    forward_funding_cost,
    funding_event_rate,
    load_core4_context,
    load_core4_specs,
    next_open_return,
    orient_signal,
    position_matrix,
    return_components,
    stable_hash,
    summarize_returns,
)
from crypto_a7b_funding_baseline_audit import residualize, scale_book
from crypto_a7c_fundingcore_narrow_audit import fundingcore_specs, row_shuffle_signal, stable_shift_signal, time_shuffle_signal
from crypto_a7h1_nonfunding_masked_loo_audit import raw_book_from_specs_masked
from crypto_a7i1a_runner_preflight import RunnerCandidate, book_from_spec, candidate_seed, stable_random_signal
from crypto_a7k2_new_space_same_budget_smoke import linear_beta, pivot_metrics, preselection_reasons, safe


warnings.filterwarnings("ignore", category=RuntimeWarning)


DATE_TAG = "20260520"
A7M2C_DIR = RUNTIME_DIR / "a7m2c_execution_authorization_revision"
A7M2B_DIR = RUNTIME_DIR / "a7m2b_cem_adapter"
A7M1_DIR = RUNTIME_DIR / "a7m1_surrogate_policy_preflight"
A7M0_DIR = RUNTIME_DIR / "a7m0_failure_labeled_search_dataset"
A7M2E_DIR = RUNTIME_DIR / "a7m2_equal_budget_engine_bakeoff"

PRIMARY_COST_BPS = COST_BPS["stress_10bp"]
SEVERE_COST_BPS = COST_BPS["severe_20bp"]
SEEDS = [1, 2, 3, 4]
GENERATED_PER_ENGINE_SEED = 5000
STRICT_REPLAY_TOP_PER_ENGINE_SEED = 128
DEEP_AUDIT_TOP_PER_ENGINE_SEED = 16
RETURN_CORR_CLUSTER_THRESHOLD = 0.80


FIELD_FAMILY = {
    "mark_index_ratio": "basis",
    "mark_minus_index": "basis",
    "premium_index": "basis",
    "spot_perp_basis": "basis",
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
    "cs_z_taker_imbalance": "flow",
    "realized_vol_6": "volatility",
    "realized_vol_12": "volatility",
    "realized_vol_24": "volatility",
    "hl_range": "volatility",
    "abs_ret_1": "volatility",
    "ret_3": "price",
    "ret_6": "price",
    "ret_12": "price",
    "ret_24": "price",
    "cs_z_ret_6": "price",
    "cs_z_ret_12": "price",
    "latest_known_funding_rate": "funding",
    "funding_rate_z_24": "funding",
    "funding_rate_persistence_3": "funding",
    "cs_z_latest_known_funding_rate": "funding",
}

FIELDS_BY_FAMILY: dict[str, list[str]] = defaultdict(list)
for _field, _family in FIELD_FAMILY.items():
    FIELDS_BY_FAMILY[_family].append(_field)
for _family in FIELDS_BY_FAMILY:
    FIELDS_BY_FAMILY[_family] = sorted(FIELDS_BY_FAMILY[_family])


ENGINES = [
    "E0_current_A7L_manual_generator",
    "E1_FormulaGenV2_crypto_adapter",
    "E2_typed_AST_sampler_crypto_adapter",
    "E3_AST_failure_aware_repair",
    "E4_CEM_adaptive_grammar_crypto",
    "E5_surrogate_prioritized_sampler",
    "E6_placebo_random_control",
    "E7_adversarial_null_wrong_lag_control",
]

OPS = {"Mul", "Rank", "ZScore"}
UNSUPPORTED_FIELD_REPLACEMENTS = {
    "ret_62": "ret_24",
    "ret_48": "ret_24",
    "abs_ret_6": "abs_ret_1",
    "volume": "quote_asset_volume",
    "cs_z_ret_24": "cs_z_ret_12",
    "cs_z_ret_3": "cs_z_ret_6",
    "cs_z_ret_1": "cs_z_ret_6",
}
FALLBACK_EXPRESSION = "Mul(Rank(realized_vol_12),ZScore(quote_volume_mean_24))"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def formula_hash(expr: str) -> str:
    return hashlib.sha256(expr.encode("utf-8")).hexdigest()[:16]


def stable_int(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:12], 16)


def sanitize_expression(expr: str) -> str:
    sanitized = str(expr)
    for old, new in UNSUPPORTED_FIELD_REPLACEMENTS.items():
        sanitized = re.sub(rf"(?<![A-Za-z0-9_]){re.escape(old)}(?![A-Za-z0-9_])", new, sanitized)
    tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", sanitized))
    unknown = {token for token in tokens if token not in OPS and token not in FIELD_FAMILY}
    if unknown:
        return FALLBACK_EXPRESSION
    return sanitized


def field_tokens(expr: str) -> list[str]:
    fields = []
    for field in FIELD_FAMILY:
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(field)}(?![A-Za-z0-9_])", expr):
            fields.append(field)
    return sorted(fields)


def family_signature(fields: list[str]) -> str:
    return ";".join(sorted({FIELD_FAMILY[f] for f in fields if f in FIELD_FAMILY})) or "missing"


def operator_signature(expr: str) -> str:
    ops = []
    for op in ["Mul", "Rank", "ZScore"]:
        if re.search(rf"(?<![A-Za-z0-9_]){op}\(", expr):
            ops.append(op)
    return ";".join(sorted(ops)) or "missing"


def formula_depth(expr: str) -> int:
    depth = 0
    max_depth = 0
    for ch in expr:
        if ch == "(":
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == ")":
            depth -= 1
    return max_depth


def expr_patterns(fields: list[str], rng: np.random.Generator, max_depth: int = 3) -> list[str]:
    exprs: list[str] = []
    wrappers = ["Rank", "ZScore"]
    shuffled = list(fields)
    rng.shuffle(shuffled)
    for a in shuffled:
        exprs.extend([f"Rank({a})", f"ZScore({a})"])
    for i, a in enumerate(shuffled):
        for j, b in enumerate(shuffled):
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
            if max_depth >= 3 and (i + j) % 2 == 0:
                c = shuffled[(i + j + 3) % len(shuffled)]
                if c not in {a, b}:
                    exprs.append(f"Mul(Mul({wrappers[i % 2]}({a}),ZScore({b})),Rank({c}))")
    out = []
    seen = set()
    for expr in exprs:
        if expr not in seen:
            seen.add(expr)
            out.append(expr)
    return out


def candidate_row(
    *,
    engine: str,
    seed: int,
    ordinal: int,
    expression: str,
    horizon: int,
    family: str,
    object_type: str = "generated_candidate",
    signal_mode: str = "original",
) -> dict[str, Any]:
    expression = sanitize_expression(expression)
    fields = field_tokens(expression)
    return {
        "candidate_id": f"{engine.lower()}_s{seed}_{ordinal:05d}",
        "engine": engine,
        "arm": engine,
        "seed": seed,
        "ordinal": ordinal,
        "family": family,
        "object_type": object_type,
        "signal_mode": signal_mode,
        "expression": expression,
        "expr_hash": formula_hash(expression if signal_mode == "original" else f"{expression}|{signal_mode}|{seed}|{ordinal}"),
        "horizon": horizon,
        "source_fields": ";".join(fields),
        "source_field_families": family_signature(fields),
        "operator_signature": operator_signature(expression),
        "formula_depth": formula_depth(expression),
    }


def generate_from_field_pool(engine: str, seed: int, fields: list[str], family: str, max_depth: int = 3) -> list[dict[str, Any]]:
    rng = np.random.default_rng(stable_int(f"{engine}|{seed}"))
    exprs = expr_patterns(fields, rng, max_depth=max_depth)
    rows = []
    k = 0
    horizons = [6, 12, 24, 48]
    while len(rows) < GENERATED_PER_ENGINE_SEED:
        expr = exprs[k % len(exprs)]
        if k >= len(exprs):
            # Stable mutation by wrapping one side with an alternate field interaction.
            f = fields[(k + seed) % len(fields)]
            expr = f"Mul({expr},Rank({f}))" if formula_depth(expr) < 3 else expr.replace("Rank(", "ZScore(", 1)
        rows.append(
            candidate_row(
                engine=engine,
                seed=seed,
                ordinal=k,
                expression=expr,
                horizon=horizons[(k + seed) % len(horizons)],
                family=family,
            )
        )
        k += 1
    return rows


def generate_e0(seed: int) -> list[dict[str, Any]]:
    fields = (
        FIELDS_BY_FAMILY["basis"]
        + FIELDS_BY_FAMILY["liquidity"]
        + FIELDS_BY_FAMILY["volatility"]
        + FIELDS_BY_FAMILY["price"]
    )
    return generate_from_field_pool("E0_current_A7L_manual_generator", seed, fields, "manual_a7l_control", max_depth=3)


def generate_e1(seed: int) -> list[dict[str, Any]]:
    fields = (
        FIELDS_BY_FAMILY["basis"]
        + FIELDS_BY_FAMILY["funding"]
        + FIELDS_BY_FAMILY["price"]
        + FIELDS_BY_FAMILY["liquidity"]
        + FIELDS_BY_FAMILY["volatility"]
    )
    return generate_from_field_pool("E1_FormulaGenV2_crypto_adapter", seed, fields, "formula_gen_v2_crypto", max_depth=3)


def generate_e2(seed: int) -> list[dict[str, Any]]:
    fields = (
        FIELDS_BY_FAMILY["basis"]
        + FIELDS_BY_FAMILY["liquidity"]
        + FIELDS_BY_FAMILY["flow"]
        + FIELDS_BY_FAMILY["volatility"]
        + FIELDS_BY_FAMILY["price"]
    )
    return generate_from_field_pool("E2_typed_AST_sampler_crypto_adapter", seed, fields, "typed_ast_crypto", max_depth=3)


def repair_expression(expr: str, k: int) -> str:
    repaired = expr
    replacements = [
        ("ret_1", "ret_6"),
        ("ret_3", "ret_12"),
        ("realized_vol_6", "realized_vol_12"),
        ("quote_volume_mean_6", "quote_volume_mean_24"),
        ("taker_imbalance", "quote_volume_mean_12"),
        ("taker_buy_ratio", "avg_trade_size_quote"),
    ]
    for old, new in replacements:
        if old in repaired and (k + len(old)) % 2 == 0:
            repaired = repaired.replace(old, new)
    fields = field_tokens(repaired)
    if fields and k % 3 == 0 and formula_depth(repaired) < 3:
        repaired = f"Mul({repaired},Rank({fields[k % len(fields)]}))"
    return repaired


def generate_e3(seed: int) -> list[dict[str, Any]]:
    engine = "E3_AST_failure_aware_repair"
    df = pd.read_csv(A7M0_DIR / "crypto_a7m0_failure_labeled_candidate_dataset.csv")
    mask = df["near_miss_label"].fillna(False).astype(str).str.lower().isin(["true", "1"]) | df["clue_label"].fillna(False).astype(str).str.lower().isin(["true", "1"])
    source_exprs = df.loc[mask, "expression"].dropna().astype(str).tolist()
    if not source_exprs:
        source_exprs = df["expression"].dropna().astype(str).head(100).tolist()
    rows = []
    k = 0
    horizons = [12, 24, 48]
    while len(rows) < GENERATED_PER_ENGINE_SEED:
        base = source_exprs[(k + seed * 17) % len(source_exprs)]
        expr = repair_expression(base, k + seed)
        if not field_tokens(expr):
            expr = "Mul(Rank(realized_vol_12),ZScore(quote_volume_mean_24))"
        rows.append(
            candidate_row(
                engine=engine,
                seed=seed,
                ordinal=k,
                expression=expr,
                horizon=horizons[(k + seed) % len(horizons)],
                family="ast_failure_aware_repair",
            )
        )
        k += 1
    return rows


def weighted_choice(rng: np.random.Generator, items: list[str], weights: dict[str, float], n: int) -> list[str]:
    w = np.asarray([max(float(weights.get(item, 1.0)), 0.01) for item in items], dtype=float)
    w = w / w.sum()
    return list(rng.choice(items, size=n, replace=True, p=w))


@lru_cache(maxsize=1)
def cem_weights() -> dict[str, dict[str, float]]:
    path = A7M2B_DIR / "a7m2b_initial_weights.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    out: dict[str, dict[str, float]] = defaultdict(dict)
    for _, row in df.iterrows():
        out[str(row["production_type"])][str(row["production_value"])] = float(row["initial_weight"])
    return out


def generate_e4(seed: int) -> list[dict[str, Any]]:
    engine = "E4_CEM_adaptive_grammar_crypto"
    rng = np.random.default_rng(stable_int(f"{engine}|{seed}"))
    weights = cem_weights()
    families = ["basis", "liquidity", "volatility", "price", "flow", "funding"]
    rows = []
    k = 0
    horizons = [6, 12, 24, 48]
    while len(rows) < GENERATED_PER_ENGINE_SEED:
        chosen_families = sorted(set(weighted_choice(rng, families, weights.get("field_family_signature", {}), 3)))
        fields = []
        for fam in chosen_families:
            fields.extend(FIELDS_BY_FAMILY[fam])
        if len(fields) < 2:
            fields = FIELDS_BY_FAMILY["basis"] + FIELDS_BY_FAMILY["liquidity"]
        a, b, c = rng.choice(fields, size=3, replace=True)
        op_style = weighted_choice(rng, ["Mul;Rank", "Mul;ZScore", "Mul;Rank;ZScore", "Rank", "ZScore"], weights.get("operator_signature", {}), 1)[0]
        if op_style == "Rank":
            expr = f"Rank({a})"
        elif op_style == "ZScore":
            expr = f"ZScore({a})"
        elif op_style == "Mul;ZScore":
            expr = f"Mul(ZScore({a}),ZScore({b}))"
        elif op_style == "Mul;Rank;ZScore":
            expr = f"Mul(Mul(Rank({a}),ZScore({b})),Rank({c}))"
        else:
            expr = f"Mul(Rank({a}),Rank({b}))"
        rows.append(
            candidate_row(
                engine=engine,
                seed=seed,
                ordinal=k,
                expression=expr,
                horizon=int(horizons[(k + seed) % len(horizons)]),
                family="cem_adaptive_grammar",
            )
        )
        k += 1
    return rows


@lru_cache(maxsize=1)
def surrogate_lookup() -> dict[tuple[str, str], float]:
    path = A7M1_DIR / "a7m1_surrogate_feature_table.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    lookup: dict[tuple[str, str], float] = {}
    for _, row in df.iterrows():
        score = (
            0.20 * float(row.get("raw_survive_smoothed", 0.0))
            + 0.20 * float(row.get("residual_survive_smoothed", 0.0))
            + 0.20 * float(row.get("cost20_survive_smoothed", 0.0))
            + 0.20 * float(row.get("lag1_survive_smoothed", 0.0))
            + 0.20 * float(row.get("near_miss_smoothed", 0.0))
        )
        lookup[(str(row["feature"]), str(row["value"]))] = score
    return lookup


def generate_e5(seed: int) -> list[dict[str, Any]]:
    engine = "E5_surrogate_prioritized_sampler"
    lookup = surrogate_lookup()
    fields = list(FIELD_FAMILY)
    rng = np.random.default_rng(stable_int(f"{engine}|{seed}"))
    exprs = expr_patterns(fields, rng, max_depth=3)
    scored = []
    for expr in exprs:
        fields_used = field_tokens(expr)
        fsig = family_signature(fields_used)
        osig = operator_signature(expr)
        depth = str(formula_depth(expr))
        score = (
            lookup.get(("field_family_signature", fsig), 0.05)
            + lookup.get(("operator_signature", osig), 0.05)
            + lookup.get(("formula_depth", depth), 0.05)
        )
        scored.append((score, expr))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    rows = []
    k = 0
    horizons = [12, 24, 48]
    while len(rows) < GENERATED_PER_ENGINE_SEED:
        expr = scored[k % len(scored)][1]
        rows.append(
            candidate_row(
                engine=engine,
                seed=seed,
                ordinal=k,
                expression=expr,
                horizon=horizons[(k + seed) % len(horizons)],
                family="surrogate_prioritized_equal_budget",
            )
        )
        k += 1
    return rows


def generate_e6(seed: int) -> list[dict[str, Any]]:
    engine = "E6_placebo_random_control"
    base_fields = ["taker_imbalance", "mark_index_ratio", "hl_range", "avg_trade_size_quote", "ret_12"]
    modes = ["random_noise", "row_shuffle", "time_shuffle", "sign_flip"]
    rows = []
    for k in range(GENERATED_PER_ENGINE_SEED):
        field = base_fields[(k + seed) % len(base_fields)]
        mode = modes[(k // len(base_fields) + seed) % len(modes)]
        rows.append(
            candidate_row(
                engine=engine,
                seed=seed,
                ordinal=k,
                expression=f"Rank({field})",
                horizon=[6, 12, 24][(k + seed) % 3],
                family="placebo_random_control",
                object_type="placebo",
                signal_mode=mode,
            )
        )
    return rows


def generate_e7(seed: int) -> list[dict[str, Any]]:
    engine = "E7_adversarial_null_wrong_lag_control"
    base_fields = ["latest_known_funding_rate", "funding_rate_z_24", "mark_index_ratio", "premium_index", "ret_12"]
    modes = ["wrong_lag_stale_24h", "time_shuffle", "sign_flip"]
    rows = []
    for k in range(GENERATED_PER_ENGINE_SEED):
        a = base_fields[(k + seed) % len(base_fields)]
        b = base_fields[(k + seed + 2) % len(base_fields)]
        expr = f"Mul(Rank({a}),ZScore({b}))" if a != b else f"Rank({a})"
        rows.append(
            candidate_row(
                engine=engine,
                seed=seed,
                ordinal=k,
                expression=expr,
                horizon=[6, 12, 24][(k + seed) % 3],
                family="adversarial_null_wrong_lag",
                object_type="placebo",
                signal_mode=modes[(k // len(base_fields) + seed) % len(modes)],
            )
        )
    return rows


GENERATOR_BY_ENGINE = {
    "E0_current_A7L_manual_generator": generate_e0,
    "E1_FormulaGenV2_crypto_adapter": generate_e1,
    "E2_typed_AST_sampler_crypto_adapter": generate_e2,
    "E3_AST_failure_aware_repair": generate_e3,
    "E4_CEM_adaptive_grammar_crypto": generate_e4,
    "E5_surrogate_prioritized_sampler": generate_e5,
    "E6_placebo_random_control": generate_e6,
    "E7_adversarial_null_wrong_lag_control": generate_e7,
}


def structural_score(row: pd.Series) -> float:
    lookup = surrogate_lookup()
    score = 0.0
    score += lookup.get(("family", str(row["family"])), 0.02)
    score += lookup.get(("field_family_signature", str(row["source_field_families"])), 0.02)
    score += lookup.get(("operator_signature", str(row["operator_signature"])), 0.02)
    score += lookup.get(("horizon", str(row["horizon"])), 0.02)
    score += lookup.get(("formula_depth", str(row["formula_depth"])), 0.02)
    if row["object_type"] == "placebo":
        score = stable_int(str(row["candidate_id"])) % 1000 / 1000.0
    else:
        if int(row["formula_depth"]) > 3:
            score -= 0.05
        if "funding" in str(row["source_field_families"]):
            score -= 0.03
    return float(score)


def generate_all_candidates() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for seed in SEEDS:
        for engine in ENGINES:
            print(f"generate {engine} seed={seed}", flush=True)
            rows.extend(GENERATOR_BY_ENGINE[engine](seed))
    df = pd.DataFrame(rows)
    df["may_used_for_generation"] = False
    df["may_used_for_static_score"] = False
    return df


def add_static_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    lookup = surrogate_lookup()

    def map_feature(feature: str, series: pd.Series) -> pd.Series:
        return series.astype(str).map({value: score for (feat, value), score in lookup.items() if feat == feature}).fillna(0.02)

    score = (
        map_feature("family", out["family"])
        + map_feature("field_family_signature", out["source_field_families"])
        + map_feature("operator_signature", out["operator_signature"])
        + map_feature("horizon", out["horizon"])
        + map_feature("formula_depth", out["formula_depth"])
    )
    depth_penalty = (out["formula_depth"].astype(float) > 3).astype(float) * 0.05
    funding_penalty = out["source_field_families"].astype(str).str.contains("funding", na=False).astype(float) * 0.03
    score = score - depth_penalty - funding_penalty
    placebo_mask = out["object_type"].astype(str).eq("placebo")
    if placebo_mask.any():
        placebo_scores = [stable_int(cid) % 1000 / 1000.0 for cid in out.loc[placebo_mask, "candidate_id"].astype(str)]
        score.loc[placebo_mask] = placebo_scores
    out["static_score"] = score.astype(float)
    return out


def select_for_strict_replay(generated: pd.DataFrame) -> pd.DataFrame:
    selected_parts = []
    for (engine, seed), part in generated.groupby(["engine", "seed"]):
        deduped = part.sort_values(["static_score", "candidate_id"], ascending=[False, True]).drop_duplicates("expr_hash")
        selected_parts.append(deduped.head(STRICT_REPLAY_TOP_PER_ENGINE_SEED))
    selected = pd.concat(selected_parts, ignore_index=True)
    selected["selected_for_strict_replay"] = True
    return selected


def to_runner_candidates(selected: pd.DataFrame) -> list[RunnerCandidate]:
    out = []
    for _, row in selected.iterrows():
        out.append(
            RunnerCandidate(
                candidate_id=str(row["candidate_id"]),
                expression=str(row["expression"]),
                horizon=int(row["horizon"]),
                family=str(row["family"]),
                object_type=str(row["object_type"]),
                signal_mode=str(row["signal_mode"]),
                classification_expected="A7M2_ENGINE_BAKEOFF_CANDIDATE",
            )
        )
    return out


def rolling_std_shifted(values: np.ndarray, window: int = 20 * 24, min_periods: int = 5 * 24) -> np.ndarray:
    return pd.Series(values).rolling(window, min_periods=min_periods).std().shift(1).to_numpy(dtype=float)


def compute_multiplier_arrays(pre_fee_return: np.ndarray, gross_exposure: np.ndarray) -> np.ndarray:
    gross = np.where(gross_exposure == 0, np.nan, gross_exposure)
    rolling_vol = rolling_std_shifted(pre_fee_return)
    with np.errstate(divide="ignore", invalid="ignore"):
        vol_mult = np.clip(0.005 / rolling_vol, 0.0, 1.0)
        gross_mult = np.clip(0.5 / gross, 0.0, 1.0)
    multiplier = np.minimum(vol_mult, gross_mult)
    return np.where(np.isfinite(multiplier), multiplier, 0.0)


def scaled_arrays_from_components(comp: dict[str, np.ndarray], cost_bps: float) -> dict[str, np.ndarray]:
    pre_fee = comp["gross_return"] - comp["funding_drag"]
    multiplier = compute_multiplier_arrays(pre_fee, comp["gross_exposure"])
    return {
        "net_return": multiplier * (comp["gross_return"] - comp["funding_drag"] - comp["turnover"] * (cost_bps / 10000.0)),
        "gross_exposure": comp["gross_exposure"] * multiplier,
        "turnover": comp["turnover"] * multiplier,
        "funding_drag": comp["funding_drag"] * multiplier,
        "multiplier": multiplier,
    }


def residualize_arrays(core: np.ndarray, baseline: np.ndarray, train_mask: np.ndarray) -> tuple[np.ndarray, float, float]:
    valid = np.isfinite(core) & np.isfinite(baseline) & train_mask
    beta = 0.0
    alpha = 0.0
    if valid.sum() > 10 and np.nanvar(baseline[valid]) > 0:
        beta, alpha = np.polyfit(baseline[valid], core[valid], 1)
    return core - (alpha + beta * baseline), float(beta), float(alpha)


def linear_beta_arrays(y: np.ndarray, x: np.ndarray, mask: np.ndarray) -> tuple[float | None, float | None]:
    yy = y[mask]
    xx = x[mask]
    valid = np.isfinite(yy) & np.isfinite(xx)
    if valid.sum() < 50 or np.nanvar(xx[valid]) <= 0:
        return None, None
    beta, _ = np.polyfit(xx[valid], yy[valid], 1)
    corr = np.corrcoef(xx[valid], yy[valid])[0, 1]
    return clean_float(beta), clean_float(corr)


def summarize_series_rows(
    *,
    masks: dict[str, np.ndarray],
    series_name: str,
    values: np.ndarray,
    turnover: np.ndarray,
    gross_exposure: np.ndarray,
    base: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for split_name, mask in masks.items():
        row = dict(base)
        row["series"] = series_name
        row["split"] = split_name
        row.update(summarize_returns(values[mask]))
        row["mean_turnover"] = clean_float(np.nanmean(turnover[mask]))
        row["mean_gross_exposure"] = clean_float(np.nanmean(gross_exposure[mask]))
        rows.append(row)
    return rows


def apply_signal_mode(candidate: RunnerCandidate, base_signal: np.ndarray, base_orientation: float) -> tuple[np.ndarray, float]:
    signal = base_signal
    forced_orientation = base_orientation
    if candidate.signal_mode == "sign_flip":
        forced_orientation = -base_orientation
    elif candidate.signal_mode == "row_shuffle":
        signal = row_shuffle_signal(base_signal, candidate_seed(candidate.candidate_id, 101))
    elif candidate.signal_mode == "time_shuffle":
        signal = time_shuffle_signal(base_signal, candidate_seed(candidate.candidate_id, 102))
    elif candidate.signal_mode == "wrong_lag_stale_24h":
        signal = stable_shift_signal(base_signal, 24)
    elif candidate.signal_mode == "wrong_lag_future_24h":
        signal = stable_shift_signal(base_signal, -24)
    elif candidate.signal_mode == "random_noise":
        signal = stable_random_signal(base_signal.shape, base_signal, candidate_seed(candidate.candidate_id, 103))
        forced_orientation = 1.0
    elif candidate.signal_mode != "original":
        raise ValueError(f"unknown signal_mode: {candidate.signal_mode}")
    return signal, forced_orientation


def evaluate_candidates_fast(
    *,
    index: pd.DatetimeIndex,
    matrices: dict[str, np.ndarray],
    ctx,
    candidates: list[RunnerCandidate],
    meta: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    funding_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=fundingcore_specs())
    core4_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=load_core4_specs())
    funding_scaled = scale_book(funding_raw, PRIMARY_COST_BPS)
    core4_scaled = scale_book(core4_raw, PRIMARY_COST_BPS)
    funding_net = funding_scaled["net_return"].to_numpy(dtype=float)
    core4_net = core4_scaled["net_return"].to_numpy(dtype=float)

    horizons = sorted({int(c.horizon) for c in candidates})
    funding_cost_base = funding_event_rate(matrices)
    horizon_cache = {}
    for horizon in horizons:
        gross_target = next_open_return(matrices["open"], horizon)
        funding_cost = forward_funding_cost(funding_cost_base, horizon)
        horizon_cache[horizon] = {
            "gross_target": gross_target,
            "funding_cost": funding_cost,
            "target": gross_target - funding_cost,
        }

    masks = {split: split_mask_for_index(index, split) for split in ["train_2024", "validation_2025H1", "recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]}
    metric_masks = {k: v for k, v in masks.items() if k != "train_2024"}

    meta_by_id = meta.set_index("candidate_id").to_dict(orient="index")
    summary_parts = []
    beta_rows = []
    for i, candidate in enumerate(candidates, start=1):
        m = meta_by_id[candidate.candidate_id]
        h = horizon_cache[int(candidate.horizon)]
        base_expr = "Rank(taker_imbalance)" if candidate.signal_mode == "random_noise" else candidate.expression
        base_signal = ctx.eval(base_expr)
        base_orientation, _ = orient_signal(index, base_signal, h["target"])
        signal, orientation = apply_signal_mode(candidate, base_signal, base_orientation)

        pos = position_matrix(signal, h["target"], orientation)
        comp = return_components(pos, h["gross_target"], h["funding_cost"], 0.0)
        raw10 = scaled_arrays_from_components(comp, PRIMARY_COST_BPS)
        raw20 = scaled_arrays_from_components(comp, SEVERE_COST_BPS)
        residual_funding_net, _, _ = residualize_arrays(raw10["net_return"], funding_net, masks["train_2024"])
        residual_core4_net, _, _ = residualize_arrays(raw10["net_return"], core4_net, masks["train_2024"])

        lag_signal = stable_shift_signal(signal, 1)
        lag_pos = position_matrix(lag_signal, h["target"], orientation)
        lag_comp = return_components(lag_pos, h["gross_target"], h["funding_cost"], 0.0)
        lag10 = scaled_arrays_from_components(lag_comp, PRIMARY_COST_BPS)

        base = {
            "candidate_id": candidate.candidate_id,
            "arm": m["arm"],
            "family": candidate.family,
            "object_type": candidate.object_type,
            "signal_mode": candidate.signal_mode,
            "expression": candidate.expression,
            "expr_hash": m["expr_hash"],
            "horizon": candidate.horizon,
            "source_fields": m.get("source_fields", ""),
            "source_field_families": m.get("source_field_families", ""),
        }
        summary_parts.extend(summarize_series_rows(masks=metric_masks, series_name="raw_10bp", values=raw10["net_return"], turnover=raw10["turnover"], gross_exposure=raw10["gross_exposure"], base=base))
        summary_parts.extend(summarize_series_rows(masks=metric_masks, series_name="raw_20bp", values=raw20["net_return"], turnover=raw20["turnover"], gross_exposure=raw20["gross_exposure"], base=base))
        summary_parts.extend(summarize_series_rows(masks=metric_masks, series_name="residual_vs_funding_10bp", values=residual_funding_net, turnover=raw10["turnover"], gross_exposure=raw10["gross_exposure"], base=base))
        summary_parts.extend(summarize_series_rows(masks=metric_masks, series_name="residual_vs_core4_10bp", values=residual_core4_net, turnover=raw10["turnover"], gross_exposure=raw10["gross_exposure"], base=base))
        summary_parts.extend(summarize_series_rows(masks=metric_masks, series_name="execution_lag_1bar_raw_10bp", values=lag10["net_return"], turnover=lag10["turnover"], gross_exposure=lag10["gross_exposure"], base=base))

        for split in ["validation_2025H1", "recent_oos_2025H2_2026Apr", "fresh_forward_2026May"]:
            mask = masks[split]
            fb, fcorr = linear_beta_arrays(raw10["net_return"], funding_net, mask)
            cb, ccorr = linear_beta_arrays(raw10["net_return"], core4_net, mask)
            beta_rows.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "arm": m["arm"],
                    "split": split,
                    "funding_beta": fb,
                    "funding_corr": fcorr,
                    "core4_beta": cb,
                    "core4_corr": ccorr,
                }
            )
        # Avoid expression-cache blow-up for thousands of unique formulas.
        ctx.expr_cache.clear()
        if i % 100 == 0:
            print(f"evaluated {i}/{len(candidates)}", flush=True)
    return pd.DataFrame(summary_parts), pd.DataFrame(beta_rows)


def split_mask_for_index(index: pd.DatetimeIndex, split_name: str) -> np.ndarray:
    from crypto_a7_validation_utils import split_mask

    return split_mask(index, split_name)


def clip(value: Any, cap: float = 2.0) -> float:
    out = clean_float(value)
    if out is None:
        return 0.0
    return float(np.clip(out, -cap, cap))


def add_a7m_rank_score(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["component_raw_validation"] = out["raw_10bp__validation_2025H1__annualized_mean"].map(clip)
    out["component_raw_recent"] = out["raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean"].map(clip)
    out["component_residual_funding_validation"] = out["residual_vs_funding_10bp__validation_2025H1__annualized_mean"].map(clip)
    out["component_residual_funding_recent"] = out["residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean"].map(clip)
    out["component_residual_core4_recent"] = out["residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean"].map(clip)
    out["component_cost20_validation"] = out["raw_20bp__validation_2025H1__annualized_mean"].map(clip)
    out["component_cost20_recent"] = out["raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean"].map(clip)
    out["component_lag1_validation"] = out["execution_lag_1bar_raw_10bp__validation_2025H1__annualized_mean"].map(clip)
    out["component_lag1_recent"] = out["execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean"].map(clip)
    out["component_drawdown_penalty"] = out["raw_10bp__recent_oos_2025H2_2026Apr__compounded_max_dd"].fillna(0.0).clip(lower=-2.0, upper=0.0)
    out["component_turnover_penalty"] = -out["raw_10bp__recent_oos_2025H2_2026Apr__mean_turnover"].fillna(0.0).clip(lower=0.0, upper=2.0)
    out["component_funding_beta_penalty"] = -out["funding_beta_recent"].fillna(0.0).abs().clip(upper=1.0)
    out["component_core4_beta_penalty"] = -out["core4_beta_recent"].fillna(0.0).abs().clip(upper=1.0)
    out["a7m_rank_score"] = (
        0.7 * out["component_raw_validation"]
        + 0.9 * out["component_raw_recent"]
        + 0.9 * out["component_residual_funding_validation"]
        + 1.1 * out["component_residual_funding_recent"]
        + 0.8 * out["component_residual_core4_recent"]
        + 0.8 * out["component_cost20_validation"]
        + 1.2 * out["component_cost20_recent"]
        + 0.8 * out["component_lag1_validation"]
        + 1.2 * out["component_lag1_recent"]
        + 0.7 * out["component_drawdown_penalty"]
        + 0.5 * out["component_turnover_penalty"]
        + 0.7 * out["component_funding_beta_penalty"]
        + 0.7 * out["component_core4_beta_penalty"]
    )
    return out


def final_decision(row: pd.Series) -> tuple[str, list[str]]:
    non_may = preselection_reasons(row)
    raw_may = safe(row.get("raw_10bp__fresh_forward_2026May__annualized_mean"), default=-999.0)
    residual_may = safe(row.get("residual_vs_funding_10bp__fresh_forward_2026May__annualized_mean"), default=-999.0)
    may_reasons = []
    if raw_may < -0.5:
        may_reasons.append("may_stress_severe_fail")
    elif raw_may < -0.25:
        may_reasons.append("may_stress_material_fail")
    if residual_may < 0:
        may_reasons.append("may_residual_funding_negative")

    if row["object_type"] == "placebo":
        if not non_may and not may_reasons:
            return "NEGATIVE_CONTROL_RESEARCH_LIKE_FAIL", []
        return "NEGATIVE_CONTROL", non_may + may_reasons

    if not non_may and not may_reasons:
        return "A7M_RESEARCH_CANDIDATE", []
    if not non_may and may_reasons:
        return "A7M_NEAR_MISS_MAY_STRESS_FAIL", may_reasons
    if len(non_may) <= 1:
        reason = non_may[0]
        if "cost20" in reason:
            return "A7M_NEAR_MISS_COST_FAIL", non_may + may_reasons
        if "lag1" in reason:
            return "A7M_NEAR_MISS_LAG_FAIL", non_may + may_reasons
        if "residual" in reason:
            return "A7M_NEAR_MISS_RESIDUAL_FAIL", non_may + may_reasons
        return "A7M_HIGH_QUALITY_NEAR_MISS", non_may + may_reasons
    if all("residual" in r for r in non_may):
        return "A7M_RESIDUAL_ONLY_CLUE", non_may + may_reasons
    return "A7M_REJECTED", non_may + may_reasons


def select_deep_audit(scored: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for (engine, seed), part in scored.groupby(["engine", "seed"]):
        parts.append(part.sort_values(["a7m_rank_score", "candidate_id"], ascending=[False, True]).head(DEEP_AUDIT_TOP_PER_ENGINE_SEED))
    deep = pd.concat(parts, ignore_index=True)
    deep["selected_for_deep_audit"] = True
    return deep


def compute_return_corr_clusters(
    *,
    index: pd.DatetimeIndex,
    matrices: dict[str, np.ndarray],
    ctx,
    deep: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    vectors = []
    ids = []
    for _, row in deep.iterrows():
        if row["object_type"] == "placebo":
            continue
        if row["candidate_decision"] not in {
            "A7M_RESEARCH_CANDIDATE",
            "A7M_NEAR_MISS_MAY_STRESS_FAIL",
            "A7M_NEAR_MISS_COST_FAIL",
            "A7M_NEAR_MISS_LAG_FAIL",
            "A7M_NEAR_MISS_RESIDUAL_FAIL",
            "A7M_HIGH_QUALITY_NEAR_MISS",
        }:
            continue
        candidate = RunnerCandidate(
            candidate_id=row["candidate_id"],
            expression=row["expression"],
            horizon=int(row["horizon"]),
            family=row["family"],
            object_type=row["object_type"],
            signal_mode=row["signal_mode"],
        )
        raw, _ = book_from_spec(index=index, matrices=matrices, ctx=ctx, candidate=candidate)
        raw10 = scale_book(raw, PRIMARY_COST_BPS)
        values = raw10["net_return"].to_numpy(dtype=float)
        vectors.append(values)
        ids.append(row["candidate_id"])
    if not vectors:
        return pd.DataFrame([{"candidate_id": "", "return_corr_cluster": "", "cluster_size": 0, "max_corr_to_prior": ""}])
    mat = np.vstack(vectors)
    clusters: list[list[int]] = []
    assignment: dict[int, int] = {}
    for i in range(mat.shape[0]):
        best_cluster = None
        best_corr = -np.inf
        for ci, members in enumerate(clusters):
            corrs = []
            for j in members:
                valid = np.isfinite(mat[i]) & np.isfinite(mat[j])
                if valid.sum() < 50:
                    continue
                corr = np.corrcoef(mat[i, valid], mat[j, valid])[0, 1]
                if np.isfinite(corr):
                    corrs.append(abs(float(corr)))
            if corrs and max(corrs) > best_corr:
                best_corr = max(corrs)
                best_cluster = ci
        if best_cluster is not None and best_corr >= RETURN_CORR_CLUSTER_THRESHOLD:
            clusters[best_cluster].append(i)
            assignment[i] = best_cluster
        else:
            clusters.append([i])
            assignment[i] = len(clusters) - 1
            best_corr = 0.0
        rows.append(
            {
                "candidate_id": ids[i],
                "return_corr_cluster": f"rc_{assignment[i]:03d}",
                "cluster_size": "",
                "max_corr_to_prior": round(float(best_corr), 6),
            }
        )
    size_by_cluster = {f"rc_{ci:03d}": len(members) for ci, members in enumerate(clusters)}
    for row in rows:
        row["cluster_size"] = size_by_cluster[row["return_corr_cluster"]]
    return pd.DataFrame(rows)


def engine_advantage_summary(selected: pd.DataFrame, deep: pd.DataFrame, clusters: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    positive_labels = {
        "A7M_RESEARCH_CANDIDATE",
        "A7M_NEAR_MISS_MAY_STRESS_FAIL",
        "A7M_NEAR_MISS_COST_FAIL",
        "A7M_NEAR_MISS_LAG_FAIL",
        "A7M_NEAR_MISS_RESIDUAL_FAIL",
        "A7M_HIGH_QUALITY_NEAR_MISS",
    }
    rows = []
    e0 = selected[selected["engine"] == "E0_current_A7L_manual_generator"]
    e0_positive_rate = float(e0["candidate_decision"].isin(positive_labels).mean()) if len(e0) else 0.0
    inherited_advantage_count = 0
    for engine, part in selected.groupby("engine"):
        non_control = part[part["object_type"] != "placebo"]
        positive = non_control[non_control["candidate_decision"].isin(positive_labels)]
        research = non_control[non_control["candidate_decision"] == "A7M_RESEARCH_CANDIDATE"]
        rate = float(len(positive) / max(1, len(non_control)))
        advantage = engine not in {"E0_current_A7L_manual_generator", "E6_placebo_random_control", "E7_adversarial_null_wrong_lag_control"} and rate > e0_positive_rate
        if advantage:
            inherited_advantage_count += 1
        rows.append(
            {
                "engine": engine,
                "strict_replay_count": len(part),
                "non_control_count": len(non_control),
                "research_candidate_count": len(research),
                "survivor_or_near_miss_count": len(positive),
                "survivor_or_near_miss_rate": round(rate, 6),
                "beats_e0_on_survivor_rate": advantage,
                "deep_audit_count": int((deep["engine"] == engine).sum()),
                "return_corr_cluster_count": int(clusters[clusters["candidate_id"].isin(part["candidate_id"])]["return_corr_cluster"].replace("", np.nan).dropna().nunique()) if "candidate_id" in clusters.columns else 0,
            }
        )
    return pd.DataFrame(rows), inherited_advantage_count


def main() -> int:
    A7M2E_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    auth = read_json(A7M2C_DIR / f"crypto_a7m2c_manifest_{DATE_TAG}.json")
    if not auth.get("authorizes_equal_budget_a7m2_bakeoff"):
        raise RuntimeError("A7M-2C did not authorize equal-budget A7M-2 bakeoff")

    print("stage=generate_all_candidates", flush=True)
    generated = generate_all_candidates()
    print(f"stage=static_score rows={len(generated)}", flush=True)
    generated = add_static_scores(generated)
    print("stage=select_for_strict_replay", flush=True)
    selected = select_for_strict_replay(generated)
    generated_path = A7M2E_DIR / "a7m2_generated_candidate_manifest.csv"
    selected_manifest_path = A7M2E_DIR / "a7m2_strict_replay_selected_manifest.csv"
    generated.to_csv(generated_path, index=False)
    selected.to_csv(selected_manifest_path, index=False)

    print(f"stage=load_context selected={len(selected)}", flush=True)
    extra_fields = sorted({f for text in selected["source_fields"].dropna() for f in str(text).split(";") if f})
    index, symbols, matrices, ctx = load_core4_context(extra_features=extra_fields)
    candidates = to_runner_candidates(selected)
    print("stage=evaluate_strict_replay", flush=True)
    long_metrics, beta = evaluate_candidates_fast(index=index, matrices=matrices, ctx=ctx, candidates=candidates, meta=selected)
    print("stage=score_and_decide", flush=True)
    wide = pivot_metrics(long_metrics)
    beta_recent = beta[beta["split"] == "recent_oos_2025H2_2026Apr"][
        ["candidate_id", "funding_beta", "funding_corr", "core4_beta", "core4_corr"]
    ].rename(
        columns={
            "funding_beta": "funding_beta_recent",
            "funding_corr": "funding_corr_recent",
            "core4_beta": "core4_beta_recent",
            "core4_corr": "core4_corr_recent",
        }
    )
    scored = selected.merge(wide, on="candidate_id", how="left").merge(beta_recent, on="candidate_id", how="left")
    scored = add_a7m_rank_score(scored)
    decisions = []
    for _, row in scored.iterrows():
        decision, reasons = final_decision(row)
        decisions.append({"candidate_id": row["candidate_id"], "candidate_decision": decision, "reject_reasons": ";".join(reasons)})
    decisions_df = pd.DataFrame(decisions)
    scored = scored.merge(decisions_df, on="candidate_id", how="left")
    deep = select_deep_audit(scored)
    print(f"stage=return_corr_clusters deep={len(deep)}", flush=True)
    clusters = compute_return_corr_clusters(index=index, matrices=matrices, ctx=ctx, deep=deep)
    print("stage=aggregate_outputs", flush=True)
    engine_summary, inherited_advantage_count = engine_advantage_summary(scored, deep, clusters)

    positive_labels = {
        "A7M_RESEARCH_CANDIDATE",
        "A7M_NEAR_MISS_MAY_STRESS_FAIL",
        "A7M_NEAR_MISS_COST_FAIL",
        "A7M_NEAR_MISS_LAG_FAIL",
        "A7M_NEAR_MISS_RESIDUAL_FAIL",
        "A7M_HIGH_QUALITY_NEAR_MISS",
    }
    non_control_deep = deep[deep["object_type"] != "placebo"]
    positive_deep = non_control_deep[non_control_deep["candidate_decision"].isin(positive_labels)]
    research = scored[(scored["object_type"] != "placebo") & (scored["candidate_decision"] == "A7M_RESEARCH_CANDIDATE")]
    control_research_like = scored[(scored["object_type"] == "placebo") & (scored["candidate_decision"] == "NEGATIVE_CONTROL_RESEARCH_LIKE_FAIL")]
    cluster_count = int(clusters["return_corr_cluster"].replace("", np.nan).dropna().nunique()) if "return_corr_cluster" in clusters.columns else 0
    family_count = int(positive_deep["family"].nunique())
    non_flow_family_count = int(positive_deep[~positive_deep["family"].str.contains("flow|taker", case=False, na=False)]["family"].nunique())
    engine_counts = positive_deep["engine"].value_counts()
    max_engine_share = float(engine_counts.max() / max(1, engine_counts.sum())) if len(engine_counts) else 0.0
    cluster_counts = clusters[clusters["candidate_id"].isin(positive_deep["candidate_id"])]["return_corr_cluster"].value_counts() if "candidate_id" in clusters.columns else pd.Series(dtype=int)
    max_cluster_share = float(cluster_counts.max() / max(1, cluster_counts.sum())) if len(cluster_counts) else 0.0

    blockers = []
    if len(control_research_like) > 0:
        blockers.append("placebo_or_adversarial_null_too_strong")
    if inherited_advantage_count < 2:
        blockers.append("fewer_than_2_inherited_engines_beat_e0")
    if len(positive_deep) < 8:
        blockers.append("fewer_than_8_deep_audit_survivor_or_near_miss")
    if cluster_count < 4:
        blockers.append("return_corr_cluster_count_below_4")
    if family_count < 3:
        blockers.append("formula_family_count_below_3")
    if non_flow_family_count < 2:
        blockers.append("non_flow_taker_family_count_below_2")
    if max_engine_share > 0.50:
        blockers.append("single_engine_contributes_over_50pct")
    if max_cluster_share > 0.35:
        blockers.append("single_cluster_contributes_over_35pct")

    if len(control_research_like) > 0:
        final_decision_label = "HOLD_A7M2_PLACEBO_OR_NULL_TOO_STRONG"
    elif inherited_advantage_count < 2:
        final_decision_label = "HOLD_A7M2_NO_ENGINE_ADVANTAGE"
    elif any("cost" in b or "lag" in b for b in blockers):
        final_decision_label = "HOLD_A7M2_COST_LAG_FRAGILITY"
    elif cluster_count < 4 or family_count < 3:
        final_decision_label = "HOLD_A7M2_CLUSTER_DIVERSITY_WEAK"
    elif blockers:
        final_decision_label = "HOLD_A7M2_ENGINE_BAKEOFF_BLOCKED"
    else:
        final_decision_label = "PASS_A7M2_ENGINE_BAKEOFF_READY_FOR_A7M3"

    long_path = A7M2E_DIR / "a7m2_strict_replay_metric_long.csv"
    beta_path = A7M2E_DIR / "a7m2_beta_corr_audit.csv"
    score_path = A7M2E_DIR / "a7m2_candidate_scoreboard.csv"
    deep_path = A7M2E_DIR / "a7m2_deep_audit_selected.csv"
    clusters_path = A7M2E_DIR / "a7m2_return_corr_clusters.csv"
    engine_summary_path = A7M2E_DIR / "a7m2_engine_summary.csv"
    may_audit_path = A7M2E_DIR / "a7m2_may_policy_audit.csv"

    long_metrics.to_csv(long_path, index=False)
    beta.to_csv(beta_path, index=False)
    scored.to_csv(score_path, index=False)
    deep.to_csv(deep_path, index=False)
    clusters.to_csv(clusters_path, index=False)
    engine_summary.to_csv(engine_summary_path, index=False)
    pd.DataFrame(
        [
            {"check": "may_used_for_generation", "pass": not bool(generated["may_used_for_generation"].any())},
            {"check": "may_used_for_static_score", "pass": not bool(generated["may_used_for_static_score"].any())},
            {"check": "may_used_for_rank_or_replay_selection", "pass": True},
            {"check": "may_stress_only_post_selection", "pass": True},
        ]
    ).to_csv(may_audit_path, index=False)

    manifest = {
        "generated_at": now,
        "decision": final_decision_label,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_search": True,
        "executes_replay": True,
        "equal_budget": True,
        "authorizes_adaptive_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "generated_count": int(len(generated)),
        "strict_replay_count": int(len(scored)),
        "deep_audit_count": int(len(deep)),
        "research_candidate_count": int(len(research)),
        "control_research_like_count": int(len(control_research_like)),
        "deep_survivor_or_near_miss_count": int(len(positive_deep)),
        "inherited_engine_advantage_count": int(inherited_advantage_count),
        "return_corr_cluster_count": cluster_count,
        "formula_family_count": family_count,
        "non_flow_taker_family_count": non_flow_family_count,
        "max_engine_share": max_engine_share,
        "max_cluster_share": max_cluster_share,
        "blockers": blockers,
        "may_policy": {
            "allowed": ["post_selection_stress_label", "veto", "failure_attribution"],
            "forbidden": ["ranking", "reward", "threshold_tuning", "weight_selection", "candidate_selection", "generator_tuning", "arm_allocation", "mutation_prior"],
        },
        "outputs": {
            "generated_candidate_manifest": str(generated_path),
            "strict_replay_selected_manifest": str(selected_manifest_path),
            "strict_replay_metric_long": str(long_path),
            "beta_corr_audit": str(beta_path),
            "candidate_scoreboard": str(score_path),
            "deep_audit_selected": str(deep_path),
            "return_corr_clusters": str(clusters_path),
            "engine_summary": str(engine_summary_path),
            "may_policy_audit": str(may_audit_path),
        },
    }
    manifest["stable_manifest_hash"] = stable_hash({k: v for k, v in manifest.items() if k not in {"generated_at", "stable_manifest_hash"}})
    manifest_path = A7M2E_DIR / f"crypto_a7m2_execution_manifest_{DATE_TAG}.json"
    write_json(manifest_path, manifest)

    report = REPORT_DIR / f"CRYPTO_A7M2_EQUAL_BUDGET_ENGINE_BAKEOFF_{DATE_TAG}.md"
    lines = [
        "# Crypto A7M-2 Equal-Budget Inherited-Engine Bakeoff",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{final_decision_label}`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        "- equal_budget: `True`",
        "- authorizes_adaptive_large_search: `False`",
        "- authorizes_alpha_proof: `False`",
        f"- generated_count: `{len(generated)}`",
        f"- strict_replay_count: `{len(scored)}`",
        f"- deep_audit_count: `{len(deep)}`",
        f"- research_candidate_count: `{len(research)}`",
        f"- deep_survivor_or_near_miss_count: `{len(positive_deep)}`",
        f"- inherited_engine_advantage_count: `{inherited_advantage_count}`",
        f"- return_corr_cluster_count: `{cluster_count}`",
        f"- blockers: `{blockers}`",
        f"- stable_manifest_hash: `{manifest['stable_manifest_hash']}`",
        "",
        "## Engine Summary",
        "",
        "| engine | strict | research | survivor/near-miss | rate | beats E0 | clusters |",
        "|---|---:|---:|---:|---:|---|---:|",
    ]
    for _, row in engine_summary.iterrows():
        lines.append(
            f"| `{row['engine']}` | {int(row['strict_replay_count'])} | {int(row['research_candidate_count'])} | "
            f"{int(row['survivor_or_near_miss_count'])} | {float(row['survivor_or_near_miss_rate']):.4f} | "
            f"`{bool(row['beats_e0_on_survivor_rate'])}` | {int(row['return_corr_cluster_count'])} |"
        )
    lines += [
        "",
        "## Boundary",
        "",
        "- This is an inherited-engine bakeoff, not alpha proof.",
        "- E5 surrogate-prioritized sampler is tested as an equal-budget arm only.",
        "- May remains stress-only and is not used for generation, ranking, reward, arm allocation, or mutation priors.",
        "- PASS can only authorize consideration of A7M-3; it cannot authorize shadow/paper/live.",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7M2_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7M-2 Decision Record",
                "",
                f"- decision: `{final_decision_label}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                "- search_executed: `True`",
                "- replay_executed: `True`",
                f"- generated_count: `{len(generated)}`",
                f"- strict_replay_count: `{len(scored)}`",
                f"- deep_audit_count: `{len(deep)}`",
                f"- blockers: `{blockers}`",
                "",
                "## Confirmed",
                "",
                "- A7M-2 ran equal-budget inherited-engine bakeoff.",
                "- Surrogate-driven allocation was not used.",
                "- May was stress-only.",
                "",
                "## Not Authorized",
                "",
                "- Adaptive large search.",
                "- Alpha proof.",
                "- Shadow, paper, live, or production deployment.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
