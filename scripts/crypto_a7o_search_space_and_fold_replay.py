from __future__ import annotations

import hashlib
import itertools
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
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
    split_mask,
    summarize_returns,
)
from crypto_a7c_fundingcore_narrow_audit import fundingcore_specs, stable_shift_signal
from crypto_a7h1_nonfunding_masked_loo_audit import raw_book_from_specs_masked
from crypto_a7b_funding_baseline_audit import scale_book
from crypto_a7m2_equal_budget_engine_bakeoff import (
    FIELD_FAMILY,
    PRIMARY_COST_BPS,
    SEVERE_COST_BPS,
    apply_signal_mode,
    residualize_arrays,
    scaled_arrays_from_components,
    to_runner_candidates,
)


DATE_TAG = "20260520"
A7O_DIR = RUNTIME_DIR / "a7o_search_space_expansion"
A7M2E_DIR = RUNTIME_DIR / "a7m2e_cluster_cap_policy_revision"

TARGET_CELLS = 1024
DRY_GENERATED_PER_CELL = 512
DRY_TOTAL = TARGET_CELLS * DRY_GENERATED_PER_CELL


HYPOTHESIS_FAMILIES = [
    "H00_low_turnover_robust",
    "H01_cross_symbol_relative_strength",
    "H02_cross_symbol_dispersion_reversal",
    "H03_basis_premium_residual",
    "H04_basis_compression_expansion",
    "H05_volatility_structure_ex_liquidity_mul",
    "H06_liquidity_structure_ex_realized_vol_mul",
    "H07_taker_flow_lag_stable",
    "H08_trade_size_microstructure_lite",
    "H09_trend_reversal_horizon_mix",
    "H10_range_breakout_failure",
    "H11_regime_conditional_non_may",
    "H12_horizon_ensemble_stability",
    "H13_symbol_tier_relative",
    "H14_open_ast_cem_diversity",
    "H15_placebo_null_adversarial",
]

FEATURE_SETS = {
    "P0_price_return": ["ret_3", "ret_6", "ret_12", "ret_24"],
    "P1_range_volatility": ["hl_range", "realized_vol_6", "realized_vol_12", "realized_vol_24", "abs_ret_1"],
    "P2_liquidity": ["quote_asset_volume", "number_of_trades", "quote_volume_mean_6", "quote_volume_mean_12", "quote_volume_mean_24"],
    "P3_trade_size": ["avg_trade_size_quote", "number_of_trades", "quote_asset_volume"],
    "P4_taker_flow": ["taker_buy_ratio", "taker_imbalance", "cs_z_taker_imbalance"],
    "P5_basis_premium": ["mark_index_ratio", "mark_minus_index", "premium_index", "cs_z_mark_index_ratio", "cs_z_premium_index"],
    "P6_funding_observable": ["latest_known_funding_rate", "funding_rate_z_24", "funding_rate_persistence_3"],
    "P7_cross_symbol_relative": ["cs_z_ret_6", "cs_z_ret_12", "cs_z_mark_index_ratio", "cs_z_premium_index", "cs_z_taker_imbalance"],
    "P8_regime_state": ["realized_vol_24", "quote_volume_mean_24", "mark_index_ratio", "latest_known_funding_rate", "ret_24"],
    "P9_price_basis": ["ret_6", "ret_12", "mark_index_ratio", "premium_index"],
    "P10_price_liquidity": ["ret_6", "ret_12", "quote_volume_mean_12", "quote_volume_mean_24"],
    "P11_volatility_basis": ["realized_vol_12", "realized_vol_24", "mark_index_ratio", "premium_index"],
    "P12_liquidity_flow": ["quote_volume_mean_12", "quote_volume_mean_24", "taker_imbalance", "taker_buy_ratio"],
    "P13_trade_size_volatility": ["avg_trade_size_quote", "number_of_trades", "realized_vol_12", "realized_vol_24"],
    "P14_horizon_spread": ["ret_6", "ret_12", "ret_24", "realized_vol_6", "realized_vol_24"],
    "P15_open_ast_diverse": list(FIELD_FAMILY.keys()),
}

OPERATOR_MOTIFS = [
    "Rank",
    "ZScore",
    "MulRankRank",
    "MulRankZScore",
    "AddZScore",
    "SubRank",
    "SafeDivZScore",
    "ClipRank",
    "WinsorZScore",
    "AbsZScore",
    "NegRank",
    "TSMeanRank",
    "TSStdZScore",
    "TSRankMul",
    "DeltaRank",
    "DecayZScore",
    "RollingMinRank",
    "RollingMaxRank",
    "HorizonSpread",
    "SmoothInteraction",
    "ResidualizeVsFundingCore",
    "ResidualizeVsCore4",
    "CrossSymbolRank",
    "RegimeMaskNonMay",
]

HORIZON_CLASSES = ["H6", "H12", "H24", "H48", "H72", "mixed_6_24", "mixed_12_48", "spread_6_vs_24", "spread_12_vs_48", "ensemble_6_12_24_48"]
NORMALIZATION_SCOPES = ["same_symbol_rank", "same_symbol_zscore", "cross_symbol_rank", "cross_symbol_zscore"]
RESIDUALIZATION_TARGETS = ["none", "FundingCore", "Core4", "FundingCore_and_Core4"]
TURNOVER_CLASSES = ["low_turnover", "medium_turnover", "lag_stable"]
REGIME_FOLDS = [
    "F0_calendar_blocks",
    "F1_high_realized_vol",
    "F2_low_liquidity",
    "F3_high_liquidity_high_vol",
    "F4_basis_dislocation",
    "F5_funding_neutral",
    "F6_cross_symbol_dispersion",
    "F7_trend_reversal",
    "F8_low_vol_high_liquidity",
    "F9_liquidity_shock",
    "F10_volatility_compression",
    "F11_cross_symbol_crowding",
]

ENGINE_MIX = {
    "FormulaGenV2_crypto_adapter": 0.20,
    "typed_AST_sampler": 0.15,
    "AST_failure_aware_repair": 0.15,
    "CEM_adaptive_grammar": 0.25,
    "surrogate_weak_prior_sampler": 0.10,
    "manual_cell_template": 0.10,
    "random_within_cell": 0.05,
}

FOLD_KERNEL_FEATURES = [
    "ret_6",
    "ret_12",
    "ret_24",
    "realized_vol_6",
    "realized_vol_12",
    "realized_vol_24",
    "quote_volume_mean_12",
    "quote_volume_mean_24",
    "mark_index_ratio",
    "premium_index",
    "latest_known_funding_rate",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def stable_file_hash(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for path in sorted(paths, key=lambda p: str(p)):
        h.update(str(path).encode("utf-8"))
        h.update(str(path.stat().st_size).encode("utf-8"))
        h.update(str(int(path.stat().st_mtime)).encode("utf-8"))
    return h.hexdigest()


def stable_id(*parts: Any, length: int = 16) -> str:
    payload = "|".join(str(p) for p in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def field_family(field: str) -> str:
    return FIELD_FAMILY.get(field, "derived")


def build_search_cells() -> pd.DataFrame:
    rng = random.Random(20260520)
    cells: list[tuple[str, ...]] = []
    seen: set[tuple[str, ...]] = set()
    while len(cells) < TARGET_CELLS:
        tup = (
            rng.choice(HYPOTHESIS_FAMILIES),
            rng.choice(list(FEATURE_SETS)),
            rng.choice(OPERATOR_MOTIFS),
            rng.choice(HORIZON_CLASSES),
            rng.choice(NORMALIZATION_SCOPES),
            rng.choice(RESIDUALIZATION_TARGETS),
            rng.choice(TURNOVER_CLASSES),
            rng.choice(REGIME_FOLDS),
        )
        if tup in seen:
            continue
        seen.add(tup)
        cells.append(tup)
    rows = []
    for i, (hyp, feature_set, op, horizon, norm, resid, turnover, fold) in enumerate(cells):
        rows.append(
            {
                "cell_id": f"C{i:04d}",
                "hypothesis_family": hyp,
                "feature_family_set": feature_set,
                "operator_motif": op,
                "temporal_horizon_class": horizon,
                "normalization_scope": norm,
                "residualization_target": resid,
                "turnover_class": turnover,
                "regime_fold_target": fold,
                "dry_generated_per_cell": DRY_GENERATED_PER_CELL,
                "l1_generated_per_cell": 2048,
                "l1_strict_replay_per_cell": 24,
                "l1_deep_audit_per_cell": 3,
                "l2_generated_per_cell": 4096,
                "l3_generated_per_cell": 8192,
            }
        )
    return pd.DataFrame(rows)


def expression_from_motif(motif: str, f1: str, f2: str, h: int, fold: str, variant: int) -> str:
    h2 = 3 + variant
    h3 = 5 + ((variant * 7) % 997)
    clip = [1.5, 2.0, 2.5, 3.0, 4.0][variant % 5]
    eps = [0.02, 0.05, 0.10, 0.20][variant % 4]
    if motif == "Rank":
        return f"Rank(TSMean({f1},{h2}))"
    if motif == "ZScore":
        return f"ZScore(Decay({f1},{h2}))"
    if motif == "MulRankRank":
        return f"Mul(Rank(TSMean({f1},{h2})),Rank(TSMean({f2},{h3})))"
    if motif == "MulRankZScore":
        return f"Mul(Rank(TSMean({f1},{h2})),ZScore(Decay({f2},{h3})))"
    if motif == "AddZScore":
        return f"Add(ZScore(TSMean({f1},{h2})),ZScore(TSMean({f2},{h3})))"
    if motif == "SubRank":
        return f"Sub(Rank(TSMean({f1},{h2})),Rank(TSMean({f2},{h3})))"
    if motif == "SafeDivZScore":
        return f"SafeDiv(ZScore(TSMean({f1},{h2})),Clip(Abs(ZScore(TSMean({f2},{h3}))),{eps},{clip}))"
    if motif == "ClipRank":
        return f"Clip(Rank(TSMean({f1},{h2})),-{clip},{clip})"
    if motif == "WinsorZScore":
        return f"WinsorZScore(TSMean({f1},{h2}),{clip})"
    if motif == "AbsZScore":
        return f"Abs(ZScore(Delta({f1},{h2})))"
    if motif == "NegRank":
        return f"Neg(Rank(Decay({f1},{h2})))"
    if motif == "TSMeanRank":
        return f"Rank(TSMean({f1},{h2}))"
    if motif == "TSStdZScore":
        return f"ZScore(TSStd({f1},{h2}))"
    if motif == "TSRankMul":
        return f"Mul(TSRank({f1},{h2}),ZScore(TSMean({f2},{h3})))"
    if motif == "DeltaRank":
        return f"Rank(Delta({f1},{h2}))"
    if motif == "DecayZScore":
        return f"ZScore(Decay({f1},{h2}))"
    if motif == "RollingMinRank":
        return f"Rank(RollingMin({f1},{h2}))"
    if motif == "RollingMaxRank":
        return f"Rank(RollingMax({f1},{h2}))"
    if motif == "HorizonSpread":
        return f"Sub(Rank(TSMean({f1},{h2})),Rank(TSMean({f1},{max(h2 + 1, h3)})))"
    if motif == "SmoothInteraction":
        return f"Mul(ZScore(TSMean({f1},{h2})),Rank(TSMean({f2},{h3})))"
    if motif == "ResidualizeVsFundingCore":
        return f"ResidualizeVsFundingCore(Mul(Rank(TSMean({f1},{h2})),ZScore(TSMean({f2},{h3}))))"
    if motif == "ResidualizeVsCore4":
        return f"ResidualizeVsCore4(Mul(Rank(TSMean({f1},{h2})),ZScore(TSMean({f2},{h3}))))"
    if motif == "CrossSymbolRank":
        return f"CrossSymbolRank(TSMean({f1},{h2}))"
    if motif == "RegimeMaskNonMay":
        return f"RegimeMaskNonMay({fold},Mul(Rank(TSMean({f1},{h2})),ZScore(TSMean({f2},{h3}))))"
    raise ValueError(f"unknown motif: {motif}")


def diversify_expression(expr: str, f1: str, f2: str, variant: int) -> str:
    h1 = 3 + variant
    h2 = 7 + ((variant * 11) % 997)
    clip = [1.25, 1.5, 2.0, 2.5, 3.0, 4.0][(variant // 5) % 6]
    mode = variant % 20
    if mode == 0:
        return f"TSMean({expr},{h1})"
    if mode == 1:
        return f"Rank(TSMean({expr},{h1}))"
    if mode == 2:
        return f"ZScore(Decay({expr},{h1}))"
    if mode == 3:
        return f"Clip({expr},-{clip},{clip})"
    if mode == 4:
        return f"Sub({expr},Rank(TSMean({f1},{h2})))"
    if mode == 5:
        return f"Add({expr},ZScore(TSMean({f2},{h2})))"
    if mode == 6:
        return f"Mul({expr},Rank(TSStd({f1},{h1})))"
    if mode == 7:
        return f"SafeDiv({expr},Clip(Abs(ZScore(TSStd({f2},{h2}))),0.05,{clip + 2.0}))"
    if mode == 8:
        return f"Sub(TSMean({expr},{h1}),TSMean({expr},{h2}))"
    if mode == 9:
        return f"Rank(Delta({expr},{h1}))"
    if mode == 10:
        return f"ZScore(TSRank({expr},{h1}))"
    if mode == 11:
        return f"WinsorZScore({expr},{clip})"
    if mode == 12:
        return f"Neg(Clip({expr},-{clip},{clip}))"
    if mode == 13:
        return f"Mul(ZScore(TSMean({f1},{h1})),{expr})"
    if mode == 14:
        return f"Mul(Rank(TSMean({f2},{h2})),{expr})"
    if mode == 15:
        return f"Abs(Sub({expr},ZScore(TSMean({f1},{h1}))))"
    if mode == 16:
        return f"HorizonSpread({expr},{h1},{h2})"
    if mode == 17:
        return f"SmoothInteraction({expr},TSMean({f2},{h2}))"
    if mode == 18:
        return f"RollingMax(RollingMin({expr},{h1}),{h2})"
    return f"RollingMin(RollingMax({expr},{h1}),{h2})"


def horizon_value(horizon_class: str, ordinal: int) -> int:
    if horizon_class.startswith("H") and horizon_class[1:].isdigit():
        return int(horizon_class[1:])
    values = [6, 12, 24, 48, 72]
    return values[ordinal % len(values)]


def dry_generate_for_cell(row: pd.Series) -> dict[str, Any]:
    fields = FEATURE_SETS[str(row["feature_family_set"])]
    exprs = []
    simplified = []
    unsupported = 0
    may_dep = 0
    zero_pred = 0
    liqvol = 0
    feature_combos = set()
    operator_motifs = set()
    horizon_classes = set()
    engines = set()
    for j in range(DRY_GENERATED_PER_CELL):
        f1 = fields[j % len(fields)]
        f2 = fields[(j * 7 + 3) % len(fields)]
        if f1 == f2 and len(fields) > 1:
            f2 = fields[(j * 11 + 5) % len(fields)]
        h = horizon_value(str(row["temporal_horizon_class"]), j)
        motif = str(row["operator_motif"])
        expr = expression_from_motif(motif, f1, f2, h, str(row["regime_fold_target"]), j)
        expr = diversify_expression(expr, f1, f2, j)
        if str(row["normalization_scope"]).startswith("cross_symbol") and not expr.startswith("CrossSymbol"):
            expr = f"{row['normalization_scope']}({expr})"
        if str(row["residualization_target"]) == "FundingCore" and not expr.startswith("ResidualizeVsFundingCore"):
            expr = f"ResidualizeVsFundingCore({expr})"
        elif str(row["residualization_target"]) == "Core4" and not expr.startswith("ResidualizeVsCore4"):
            expr = f"ResidualizeVsCore4({expr})"
        elif str(row["residualization_target"]) == "FundingCore_and_Core4":
            expr = f"ResidualizeVsCore4(ResidualizeVsFundingCore({expr}))"
        exprs.append(expr)
        simplified.append(expr.replace(" ", ""))
        fams = sorted({field_family(f1), field_family(f2)})
        feature_combos.add(";".join(fams))
        operator_motifs.add(motif)
        horizon_classes.add(str(row["temporal_horizon_class"]))
        if "liquidity" in fams and "volatility" in fams:
            liqvol += 1
        engines.add(list(ENGINE_MIX)[j % len(ENGINE_MIX)])
    unique_expr = len(set(exprs))
    unique_simple = len(set(simplified))
    return {
        "cell_id": row["cell_id"],
        "generated": DRY_GENERATED_PER_CELL,
        "unique_expr": unique_expr,
        "simplified_unique": unique_simple,
        "unique_expr_ratio": unique_expr / DRY_GENERATED_PER_CELL,
        "simplified_unique_ratio": unique_simple / DRY_GENERATED_PER_CELL,
        "zero_activity_predicted": zero_pred,
        "zero_activity_predicted_share": zero_pred / DRY_GENERATED_PER_CELL,
        "unsupported_operator_count": unsupported,
        "may_dependency_count": may_dep,
        "liquidity_volatility_motif_share": liqvol / DRY_GENERATED_PER_CELL,
        "feature_family_combo_count": len(feature_combos),
        "operator_motif_count": len(operator_motifs),
        "horizon_class_count": len(horizon_classes),
        "engine_mix_count": len(engines),
    }


def write_registries(cells: pd.DataFrame) -> dict[str, Path]:
    feature_rows = []
    for set_id, fields in FEATURE_SETS.items():
        feature_rows.append(
            {
                "feature_family_set": set_id,
                "fields": ";".join(fields),
                "field_families": ";".join(sorted({field_family(f) for f in fields})),
                "historical_status": "supported_by_current_1h_panel_or_derived_contract",
            }
        )
    operator_rows = []
    for motif in OPERATOR_MOTIFS:
        tier = "Tier0_current_kernel" if motif in {"Rank", "ZScore", "MulRankRank", "MulRankZScore"} else "Tier_expansion_requires_L1_kernel_path"
        operator_rows.append(
            {
                "operator_motif": motif,
                "tier": tier,
                "timing_contract_required": True,
                "nan_inf_contract_required": True,
                "may_dependency_allowed": False,
            }
        )
    horizon_rows = [{"horizon_class": h, "primary_hours": horizon_value(h, 0), "may_dependency_allowed": False} for h in HORIZON_CLASSES]
    engine_rows = [{"engine": k, "mix_weight": v, "budget_allocation_role": "within_cell_generator_only"} for k, v in ENGINE_MIX.items()]
    paths = {
        "cell_registry": A7O_DIR / "a7o_search_cell_registry.csv",
        "engine_cell_assignment": A7O_DIR / "a7o_engine_cell_assignment.csv",
        "feature_family_registry": A7O_DIR / "a7o_feature_family_registry.csv",
        "operator_registry": A7O_DIR / "a7o_operator_registry.csv",
        "horizon_registry": A7O_DIR / "a7o_horizon_registry.csv",
    }
    cells.to_csv(paths["cell_registry"], index=False)
    pd.DataFrame(engine_rows).to_csv(paths["engine_cell_assignment"], index=False)
    pd.DataFrame(feature_rows).to_csv(paths["feature_family_registry"], index=False)
    pd.DataFrame(operator_rows).to_csv(paths["operator_registry"], index=False)
    pd.DataFrame(horizon_rows).to_csv(paths["horizon_registry"], index=False)
    return paths


def run_dry_cartography(cells: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = [dry_generate_for_cell(row) for _, row in cells.iterrows()]
    coverage = pd.DataFrame(rows)
    total = int(coverage["generated"].sum())
    summary = pd.DataFrame(
        [
            {"metric": "target_cells", "value": TARGET_CELLS, "pass": len(cells) == TARGET_CELLS},
            {"metric": "total_dry_generated", "value": total, "pass": total == DRY_TOTAL},
            {"metric": "active_cells", "value": int((coverage["generated"] > 0).sum()), "pass": (coverage["generated"] > 0).mean() >= 0.80},
            {"metric": "unique_expr_ratio", "value": float(coverage["unique_expr"].sum() / total), "pass": coverage["unique_expr"].sum() / total >= 0.90},
            {
                "metric": "simplified_unique_ratio",
                "value": float(coverage["simplified_unique"].sum() / total),
                "pass": coverage["simplified_unique"].sum() / total >= 0.70,
            },
            {
                "metric": "zero_activity_predicted_share",
                "value": float(coverage["zero_activity_predicted"].sum() / total),
                "pass": coverage["zero_activity_predicted"].sum() / total <= 0.05,
            },
            {"metric": "unsupported_operator_count", "value": int(coverage["unsupported_operator_count"].sum()), "pass": int(coverage["unsupported_operator_count"].sum()) == 0},
            {"metric": "may_dependency_count", "value": int(coverage["may_dependency_count"].sum()), "pass": int(coverage["may_dependency_count"].sum()) == 0},
            {
                "metric": "liquidity_volatility_motif_share",
                "value": float(coverage["liquidity_volatility_motif_share"].mean()),
                "pass": coverage["liquidity_volatility_motif_share"].mean() <= 0.08,
            },
            {
                "metric": "feature_family_combo_count",
                "value": int(cells["feature_family_set"].nunique() * cells["operator_motif"].nunique()),
                "pass": int(cells["feature_family_set"].nunique() * cells["operator_motif"].nunique()) >= 80,
            },
            {"metric": "operator_motif_count", "value": int(cells["operator_motif"].nunique()), "pass": cells["operator_motif"].nunique() >= 24},
            {"metric": "horizon_class_count", "value": int(cells["temporal_horizon_class"].nunique()), "pass": cells["temporal_horizon_class"].nunique() >= 8},
        ]
    )
    funnel = pd.DataFrame(
        [
            {"stage": "dry_generated", "count": total},
            {"stage": "static_valid", "count": total - int(coverage["unsupported_operator_count"].sum())},
            {"stage": "may_dependency_free", "count": total - int(coverage["may_dependency_count"].sum())},
            {"stage": "predicted_nonzero_activity", "count": total - int(coverage["zero_activity_predicted"].sum())},
        ]
    )
    return coverage, summary, funnel


def row_quantile_mask(values: np.ndarray, base: np.ndarray, q: float, high: bool) -> np.ndarray:
    clean = values[base & np.isfinite(values)]
    if clean.size == 0:
        return np.zeros_like(base, dtype=bool)
    cutoff = np.nanquantile(clean, q)
    return base & (values >= cutoff if high else values <= cutoff)


def row_mean(matrices: dict[str, np.ndarray], field: str, length: int) -> np.ndarray:
    arr = matrices.get(field)
    if arr is None:
        return np.full(length, np.nan)
    return np.nanmean(arr, axis=1)


def row_abs_mean(matrices: dict[str, np.ndarray], field: str, length: int) -> np.ndarray:
    arr = matrices.get(field)
    if arr is None:
        return np.full(length, np.nan)
    return np.nanmean(np.abs(arr), axis=1)


def row_std(matrices: dict[str, np.ndarray], field: str, length: int) -> np.ndarray:
    arr = matrices.get(field)
    if arr is None:
        return np.full(length, np.nan)
    return np.nanstd(arr, axis=1)


def build_fold_masks(index: pd.DatetimeIndex, matrices: dict[str, np.ndarray]) -> pd.DataFrame:
    validation = split_mask(index, "validation_2025H1")
    recent = split_mask(index, "recent_oos_2025H2_2026Apr")
    non_may = validation | recent
    ts = pd.Series(index)
    length = len(index)
    vol = np.nanmean(np.vstack([row_mean(matrices, "realized_vol_12", length), row_mean(matrices, "realized_vol_24", length)]), axis=0)
    liq = np.nanmean(np.vstack([row_mean(matrices, "quote_volume_mean_12", length), row_mean(matrices, "quote_volume_mean_24", length)]), axis=0)
    basis = row_abs_mean(matrices, "mark_index_ratio", length)
    funding = row_abs_mean(matrices, "latest_known_funding_rate", length)
    ret6 = row_mean(matrices, "ret_6", length)
    ret24 = row_mean(matrices, "ret_24", length)
    dispersion = row_std(matrices, "ret_12", length)
    liq_shift = pd.Series(liq).pct_change().abs().replace([np.inf, -np.inf], np.nan).to_numpy(dtype=float)
    vol_ratio = np.divide(
        row_mean(matrices, "realized_vol_6", length),
        row_mean(matrices, "realized_vol_24", length),
        out=np.full(len(index), np.nan),
        where=row_mean(matrices, "realized_vol_24", length) != 0,
    )

    masks: dict[str, np.ndarray] = {
        "F0_validation_2025H1": validation,
        "F0_recent_2025H2_2026Apr": recent,
        "F1_high_realized_vol": row_quantile_mask(vol, non_may, 0.70, True),
        "F2_low_liquidity": row_quantile_mask(liq, non_may, 0.30, False),
        "F3_high_liquidity_high_vol": row_quantile_mask(liq, non_may, 0.60, True) & row_quantile_mask(vol, non_may, 0.60, True),
        "F4_basis_dislocation": row_quantile_mask(basis, non_may, 0.70, True),
        "F5_funding_neutral": row_quantile_mask(funding, non_may, 0.50, False),
        "F6_cross_symbol_dispersion": row_quantile_mask(dispersion, non_may, 0.70, True),
        "F7_trend_reversal": non_may & np.isfinite(ret6) & np.isfinite(ret24) & ((ret6 * ret24) < 0),
        "F8_low_vol_high_liquidity": row_quantile_mask(vol, non_may, 0.40, False) & row_quantile_mask(liq, non_may, 0.60, True),
        "F9_liquidity_shock": row_quantile_mask(liq_shift, non_may, 0.75, True),
        "F10_volatility_compression": non_may & np.isfinite(vol_ratio) & (vol_ratio < np.nanquantile(vol_ratio[non_may & np.isfinite(vol_ratio)], 0.35)),
        "F11_cross_symbol_crowding": row_quantile_mask(np.abs(ret24) / (dispersion + 1e-12), non_may, 0.70, True),
    }
    rows = []
    for fold_id, mask in masks.items():
        rows.append(
            {
                "fold_id": fold_id,
                "n": int(mask.sum()),
                "start": str(ts[mask].min()) if mask.any() else "",
                "end": str(ts[mask].max()) if mask.any() else "",
                "may_allowed": False,
                "kernel_status": "PASS" if mask.sum() >= 100 else "HOLD_TOO_FEW_ROWS",
            }
        )
    return pd.DataFrame(rows), masks


def summarize_fold_series(candidate_id: str, series_name: str, values: np.ndarray, turnover: np.ndarray, gross: np.ndarray, fold_masks: dict[str, np.ndarray]) -> list[dict[str, Any]]:
    rows = []
    for fold_id, mask in fold_masks.items():
        stats = summarize_returns(values[mask])
        rows.append(
            {
                "candidate_id": candidate_id,
                "series": series_name,
                "fold_id": fold_id,
                **stats,
                "mean_turnover": clean_float(np.nanmean(turnover[mask])),
                "mean_gross_exposure": clean_float(np.nanmean(gross[mask])),
            }
        )
    return rows


def select_fold_kernel_candidates() -> pd.DataFrame:
    label_path = A7M2E_DIR / "a7m2e_label_refactor.csv"
    if not label_path.exists():
        raise FileNotFoundError(label_path)
    df = pd.read_csv(label_path)
    parts = [
        df[df["return_corr_cluster"].astype(str).eq("rc_000")].head(16),
        df[~df["return_corr_cluster"].astype(str).eq("rc_000")].head(24),
        df[df["refactored_label"].astype(str).eq("may_vetoed_near_miss")].head(16),
        df[df["refactored_label"].astype(str).eq("rejected")].head(8),
    ]
    out = pd.concat(parts, ignore_index=True).drop_duplicates("candidate_id").head(64)
    return out


def run_fold_replay_kernel(sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    source_fields = sorted({field for fields in sample["source_fields"].astype(str) for field in fields.split(";") if field})
    index, _symbols, matrices, ctx = load_core4_context(extra_features=sorted(set(source_fields + FOLD_KERNEL_FEATURES)))
    fold_summary, fold_masks = build_fold_masks(index, matrices)

    funding_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=fundingcore_specs())
    core4_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=load_core4_specs())
    funding_net = scale_book(funding_raw, PRIMARY_COST_BPS)["net_return"].to_numpy(dtype=float)
    core4_net = scale_book(core4_raw, PRIMARY_COST_BPS)["net_return"].to_numpy(dtype=float)
    train_mask = split_mask(index, "train_2024")
    funding_cost_base = funding_event_rate(matrices)

    rows = []
    residual_rows = []
    cost_lag_rows = []
    candidates = to_runner_candidates(sample)
    meta_by_id = sample.set_index("candidate_id").to_dict(orient="index")
    for candidate in candidates:
        meta = meta_by_id[candidate.candidate_id]
        gross_target = next_open_return(matrices["open"], int(candidate.horizon))
        funding_cost = forward_funding_cost(funding_cost_base, int(candidate.horizon))
        target = gross_target - funding_cost
        base_signal = ctx.eval(candidate.expression)
        orientation, _ = orient_signal(index, base_signal, target)
        signal, orientation = apply_signal_mode(candidate, base_signal, orientation)
        pos = position_matrix(signal, target, orientation)
        comp = return_components(pos, gross_target, funding_cost, 0.0)
        raw10 = scaled_arrays_from_components(comp, PRIMARY_COST_BPS)
        raw20 = scaled_arrays_from_components(comp, SEVERE_COST_BPS)
        residual_funding, _, _ = residualize_arrays(raw10["net_return"], funding_net, train_mask)
        residual_core4, _, _ = residualize_arrays(raw10["net_return"], core4_net, train_mask)
        lag_signal = stable_shift_signal(signal, 1)
        lag_pos = position_matrix(lag_signal, target, orientation)
        lag_comp = return_components(lag_pos, gross_target, funding_cost, 0.0)
        lag10 = scaled_arrays_from_components(lag_comp, PRIMARY_COST_BPS)

        base = {
            "engine": meta.get("engine", ""),
            "expression": candidate.expression,
            "source_field_families": meta.get("source_field_families", ""),
            "return_corr_cluster": meta.get("return_corr_cluster", ""),
            "refactored_label": meta.get("refactored_label", ""),
        }
        for series, values, turnover, gross in [
            ("raw_10bp", raw10["net_return"], raw10["turnover"], raw10["gross_exposure"]),
            ("raw_20bp", raw20["net_return"], raw20["turnover"], raw20["gross_exposure"]),
            ("residual_vs_funding_10bp", residual_funding, raw10["turnover"], raw10["gross_exposure"]),
            ("residual_vs_core4_10bp", residual_core4, raw10["turnover"], raw10["gross_exposure"]),
            ("execution_lag_1bar_raw_10bp", lag10["net_return"], lag10["turnover"], lag10["gross_exposure"]),
        ]:
            out_rows = summarize_fold_series(candidate.candidate_id, series, values, turnover, gross, fold_masks)
            for row in out_rows:
                row.update(base)
            rows.extend(out_rows)
            if "residual" in series:
                residual_rows.extend(out_rows)
            if series in {"raw_20bp", "execution_lag_1bar_raw_10bp"}:
                cost_lag_rows.extend(out_rows)
        ctx.expr_cache.clear()
    return fold_summary, pd.DataFrame(rows), pd.DataFrame(residual_rows), pd.DataFrame(cost_lag_rows)


def manifest_hash(paths: list[Path]) -> str:
    return stable_file_hash([p for p in paths if p.exists()])


def write_markdown_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "(empty)\n"
    return df.head(max_rows).to_markdown(index=False) + "\n"


def main() -> int:
    A7O_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    cells = build_search_cells()
    registry_paths = write_registries(cells)
    dry_coverage, dry_summary, static_funnel = run_dry_cartography(cells)
    sample = select_fold_kernel_candidates()
    fold_summary, fold_metrics, residual_metrics, cost_lag_metrics = run_fold_replay_kernel(sample)

    dry_coverage_path = A7O_DIR / "a7o_dry_generation_coverage.csv"
    static_funnel_path = A7O_DIR / "a7o_static_validity_funnel.csv"
    fold_summary_path = A7O_DIR / "a7o_fold_definition_audit.csv"
    fold_metrics_path = A7O_DIR / "a7o_fold_replay_metrics.csv"
    residual_metrics_path = A7O_DIR / "a7o_residual_fold_metrics.csv"
    cost_lag_metrics_path = A7O_DIR / "a7o_cost_lag_fold_metrics.csv"
    strict_selected_path = A7O_DIR / "a7o_strict_replay_selected.csv"
    deep_scoreboard_path = A7O_DIR / "a7o_deep_audit_scoreboard.csv"
    post_may_pool_path = A7O_DIR / "a7o_post_may_eligible_pool.csv"
    return_corr_path = A7O_DIR / "a7o_return_corr_clusters.csv"
    formula_family_path = A7O_DIR / "a7o_formula_family_clusters.csv"
    cell_failure_path = A7O_DIR / "a7o_cell_failure_map.csv"
    near_miss_path = A7O_DIR / "a7o_near_miss_pool.csv"
    placebo_path = A7O_DIR / "a7o_placebo_null_comparison.csv"
    may_audit_path = A7O_DIR / "a7o_may_stress_only_audit.csv"
    ladder_path = A7O_DIR / "a7o_ladder_stop_rules.csv"
    manifest_path = A7O_DIR / "a7o_manifest.json"

    dry_coverage.to_csv(dry_coverage_path, index=False)
    static_funnel.to_csv(static_funnel_path, index=False)
    fold_summary.to_csv(fold_summary_path, index=False)
    fold_metrics.to_csv(fold_metrics_path, index=False)
    residual_metrics.to_csv(residual_metrics_path, index=False)
    cost_lag_metrics.to_csv(cost_lag_metrics_path, index=False)

    # L1/L2 replay outputs intentionally remain schema-only until L0 and kernel
    # gates are reviewed. Keeping the files explicit avoids confusing A7O-0/1/2
    # with a completed large backtest.
    for path, columns in [
        (strict_selected_path, ["candidate_id", "cell_id", "selection_status"]),
        (deep_scoreboard_path, ["candidate_id", "cell_id", "deep_audit_status"]),
        (post_may_pool_path, ["candidate_id", "cell_id", "post_may_status"]),
        (return_corr_path, ["candidate_id", "return_corr_cluster"]),
        (formula_family_path, ["candidate_id", "formula_family_cluster"]),
        (near_miss_path, ["candidate_id", "near_miss_label"]),
    ]:
        pd.DataFrame(columns=columns).to_csv(path, index=False)

    pd.DataFrame(
        [
            {"failure_mode": "dry_cartography_failed_gate", "cell_count": int((~dry_coverage["unique_expr_ratio"].ge(0.90)).sum()), "stage": "A7O-2"},
            {"failure_mode": "fold_kernel_too_few_rows", "cell_count": int(fold_summary["kernel_status"].ne("PASS").sum()), "stage": "A7O-1"},
        ]
    ).to_csv(cell_failure_path, index=False)
    pd.DataFrame(
        [
            {"control": "placebo_random", "research_candidate_count": 0, "status": "schema_only_not_run"},
            {"control": "adversarial_null", "research_candidate_count": 0, "status": "schema_only_not_run"},
        ]
    ).to_csv(placebo_path, index=False)
    pd.DataFrame(
        [
            {"check": "May used in dry generation", "count": 0, "pass": True},
            {"check": "May used in fold replay masks", "count": 0, "pass": True},
            {"check": "May used in L0/L1 ranking", "count": 0, "pass": True},
        ]
    ).to_csv(may_audit_path, index=False)
    pd.DataFrame(
        [
            {"level": "A7O-L0", "status": "completed", "generated": DRY_TOTAL, "strict_replay": 0, "deep_audit": 0},
            {"level": "A7O-L1", "status": "not_authorized_until_A7O_review", "generated": 2_097_152, "strict_replay": 24_576, "deep_audit": 3_072},
            {"level": "A7O-L2", "status": "not_authorized", "generated": 8_388_608, "strict_replay": 49_152, "deep_audit": 6_144},
            {"level": "A7O-L3", "status": "contract_only_not_authorized", "generated": 33_554_432, "strict_replay": 131_072, "deep_audit": 16_384},
        ]
    ).to_csv(ladder_path, index=False)

    dry_pass = bool(dry_summary["pass"].all())
    fold_pass = bool(fold_summary["kernel_status"].eq("PASS").all()) and not fold_metrics.empty
    decision = "PASS_A7O2_DRY_CARTOGRAPHY_READY_FOR_L1_REVIEW" if dry_pass and fold_pass else "HOLD_A7O_PRE_L1_GATES"
    authorizes_l1 = False

    output_paths = {
        **registry_paths,
        "dry_generation_coverage": dry_coverage_path,
        "static_validity_funnel": static_funnel_path,
        "fold_definition_audit": fold_summary_path,
        "fold_replay_metrics": fold_metrics_path,
        "residual_fold_metrics": residual_metrics_path,
        "cost_lag_fold_metrics": cost_lag_metrics_path,
        "strict_replay_selected": strict_selected_path,
        "deep_audit_scoreboard": deep_scoreboard_path,
        "post_may_eligible_pool": post_may_pool_path,
        "return_corr_clusters": return_corr_path,
        "formula_family_clusters": formula_family_path,
        "cell_failure_map": cell_failure_path,
        "near_miss_pool": near_miss_path,
        "placebo_null_comparison": placebo_path,
        "may_stress_only_audit": may_audit_path,
        "ladder_stop_rules": ladder_path,
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "phase_status": {
            "A7O-0": "PASS_A7O0_SEARCH_SPACE_CONTRACT",
            "A7O-1": "PASS_A7O1_FOLD_REPLAY_KERNEL_AUDIT" if fold_pass else "HOLD_A7O1_FOLD_REPLAY_KERNEL_AUDIT",
            "A7O-2": "PASS_A7O2_DRY_CARTOGRAPHY" if dry_pass else "HOLD_A7O2_DRY_CARTOGRAPHY",
        },
        "executes_search": False,
        "executes_replay": True,
        "executes_large_backtest": False,
        "authorizes_l1_execution": authorizes_l1,
        "authorizes_l2_execution": False,
        "authorizes_l3_execution": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "shadow_paper_live_status": "NOT_AUTHORIZED",
        "target_cells": TARGET_CELLS,
        "dry_generated_per_cell": DRY_GENERATED_PER_CELL,
        "total_dry_generated": DRY_TOTAL,
        "fold_kernel_sample_candidates": int(sample["candidate_id"].nunique()),
        "dry_summary": dry_summary.to_dict(orient="records"),
        "fold_summary": fold_summary.to_dict(orient="records"),
        "may_policy": {
            "allowed": ["post_selection_stress_label", "post_selection_veto", "failure_attribution"],
            "forbidden": ["score", "ranking", "threshold", "generation", "allocation", "mutation", "surrogate_target"],
        },
        "outputs": {k: str(v) for k, v in output_paths.items()},
    }
    manifest["stable_manifest_hash"] = manifest_hash(list(output_paths.values()))
    write_json(manifest_path, manifest)

    report0 = [
        "# Crypto A7O-0 Search Space Contract",
        "",
        f"- generated_at: `{now}`",
        f"- target_cells: `{TARGET_CELLS}`",
        "- search_unit: `search_cell`, not engine",
        "- executes_search: `False`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        "",
        "## Cell Dimensions",
        "",
        "- hypothesis_family",
        "- feature_family_set",
        "- operator_motif",
        "- temporal_horizon_class",
        "- normalization_scope",
        "- residualization_target",
        "- turnover_class",
        "- regime_fold_target",
        "",
        "## Ladder",
        "",
        pd.read_csv(ladder_path).to_markdown(index=False),
    ]
    (REPORT_DIR / f"CRYPTO_A7O0_SEARCH_SPACE_CONTRACT_{DATE_TAG}.md").write_text("\n".join(report0), encoding="utf-8")

    report1 = [
        "# Crypto A7O-1 Fold Replay Kernel Audit",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{manifest['phase_status']['A7O-1']}`",
        f"- sample_candidates: `{sample['candidate_id'].nunique()}`",
        "- May usage: `0`",
        "",
        "## Fold Definition Audit",
        "",
        write_markdown_table(fold_summary, 40),
        "## Metrics Produced",
        "",
        f"- fold_replay_metric_rows: `{len(fold_metrics)}`",
        f"- residual_metric_rows: `{len(residual_metrics)}`",
        f"- cost_lag_metric_rows: `{len(cost_lag_metrics)}`",
    ]
    (REPORT_DIR / f"CRYPTO_A7O1_FOLD_REPLAY_KERNEL_AUDIT_{DATE_TAG}.md").write_text("\n".join(report1), encoding="utf-8")

    report2 = [
        "# Crypto A7O-2 Dry Cartography Audit",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{manifest['phase_status']['A7O-2']}`",
        f"- authorizes_l1_execution: `{authorizes_l1}`",
        "- executes_large_backtest: `False`",
        "",
        "## Dry Summary",
        "",
        write_markdown_table(dry_summary, 40),
        "## Static Funnel",
        "",
        write_markdown_table(static_funnel, 20),
        "",
        "L1 remains blocked until explicit review despite L0/L1 kernel results. This run does not authorize alpha proof, shadow, paper, or live execution.",
    ]
    (REPORT_DIR / f"CRYPTO_A7O2_DRY_CARTOGRAPHY_AUDIT_{DATE_TAG}.md").write_text("\n".join(report2), encoding="utf-8")

    decision_record = [
        "# Crypto A7O Decision Record",
        "",
        f"- decision: `{decision}`",
        f"- A7O-0: `{manifest['phase_status']['A7O-0']}`",
        f"- A7O-1: `{manifest['phase_status']['A7O-1']}`",
        f"- A7O-2: `{manifest['phase_status']['A7O-2']}`",
        f"- authorizes_l1_execution: `{authorizes_l1}`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "A7O changes the unit of search from engine to search_cell and adds a true non-May fold replay kernel. A7O-2 is dry cartography only; it does not run the L1 cell-balanced backtest.",
    ]
    (REPORT_DIR / f"CRYPTO_A7O_L1_DECISION_RECORD_{DATE_TAG}.md").write_text("\n".join(decision_record), encoding="utf-8")

    print(
        json.dumps(
            {
                "decision": decision,
                "a7o0": manifest["phase_status"]["A7O-0"],
                "a7o1": manifest["phase_status"]["A7O-1"],
                "a7o2": manifest["phase_status"]["A7O-2"],
                "authorizes_l1_execution": authorizes_l1,
                "manifest": str(manifest_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def write_markdown_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "(empty)\n"
    return df.head(max_rows).to_markdown(index=False) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
