"""Deterministic mapping evidence derived only from synthetic inputs.

The functions in this module are pure: they do not read market data, inspect
sealed roles, or write artifacts.  Callers may serialize their return values
into the capability evidence bundle.
"""

from __future__ import annotations

import hashlib
from typing import Any, Iterable

import numpy as np

from .harness import FAMILY_IDS, build_synthetic_case
from .mapping import (
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    SPARSE_EVENT_OR_CARRY,
    TIME_SERIES_DIRECTIONAL_STATEFUL,
    MappingResult,
    map_portfolio,
    portfolio_series,
    turnover_decomposition,
)


FIXED_EVIDENCE_SEED = 20260715
FIXED_COST_BPS = 5.0
_TOLERANCE = 1e-12


def _hash_array(values: np.ndarray) -> str:
    source = np.asarray(values, dtype=np.float64)
    digest = hashlib.sha256()
    digest.update(str(source.shape).encode("ascii"))
    digest.update(np.isfinite(source).tobytes())
    digest.update(np.nan_to_num(source, nan=0.0, posinf=0.0, neginf=0.0).tobytes())
    return digest.hexdigest().upper()


def _json_array(values: np.ndarray) -> list[Any]:
    source = np.asarray(values)

    def convert(value: Any) -> Any:
        if isinstance(value, np.ndarray):
            return [convert(item) for item in value]
        number = float(value)
        return number if np.isfinite(number) else None

    return convert(source)


def _reason_count(mapped: MappingResult, reason: str) -> int:
    return sum(reason in coordinate for coordinate in mapped.transition_reasons)


def _assert_close(left: float, right: float, label: str) -> None:
    if not math_isclose(left, right):
        raise AssertionError(f"{label}: {left} != {right}")


def math_isclose(left: float, right: float) -> bool:
    return bool(np.isclose(float(left), float(right), rtol=1e-10, atol=_TOLERANCE))


def mapping_synthetic_behavior_payload() -> dict[str, Any]:
    """Return focused non-market invariants for the three explicit mappings."""

    cs_contract = DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]
    ts_contract = DEFAULT_MAPPING_CONTRACTS[TIME_SERIES_DIRECTIONAL_STATEFUL]
    sparse_contract = DEFAULT_MAPPING_CONTRACTS[SPARSE_EVENT_OR_CARRY]

    # Exercise every mapping with deliberately extreme signals.  The evidence
    # is computed from final weights, after all normalization/scaling, because
    # an intermediate clip is not sufficient proof of a portfolio-level cap.
    cap_signals = {
        # Five assets cannot sustain unit gross with two names on each side at
        # a 20% cap.  The mapping must reduce gross rather than breach the cap.
        CROSS_SECTIONAL_ZERO_NET: np.asarray(
            [[-1e12], [-1e6], [0.0], [1e6], [1e12]], dtype=float
        ),
        # Eight simultaneous, extreme entries force gross-cap scaling.
        TIME_SERIES_DIRECTIONAL_STATEFUL: np.asarray(
            [
                [1e12, -1e12, 1e12],
                [-1e12, 1e12, -1e12],
            ]
            * 4,
            dtype=float,
        ),
        # Ten simultaneous signed events also force gross-cap scaling, then
        # remain subject to the same caps throughout their fixed hold.
        SPARSE_EVENT_OR_CARRY: np.vstack(
            [
                np.asarray(
                    [1e12 if asset % 2 == 0 else -1e12] + [0.0] * 5,
                    dtype=float,
                )
                for asset in range(10)
            ]
        ),
    }
    cap_results: dict[str, MappingResult] = {}
    cap_cases: dict[str, dict[str, Any]] = {}
    cap_checks: dict[str, bool] = {}
    for mapping_id, signal in cap_signals.items():
        contract = DEFAULT_MAPPING_CONTRACTS[mapping_id]
        mapped = map_portfolio(signal, contract)
        cap_results[mapping_id] = mapped
        if mapping_id == CROSS_SECTIONAL_ZERO_NET:
            declared_position_cap = float(contract.parameters["position_cap"])
            declared_gross_cap = float(contract.parameters["gross_target"])
        else:
            declared_position_cap = float(contract.parameters["maximum_position"])
            declared_gross_cap = float(contract.parameters["gross_cap"])
        gross_path = np.abs(mapped.weights).sum(axis=0)
        final_max = float(np.max(np.abs(mapped.weights)))
        final_max_gross = float(np.max(gross_path))
        position_cap_holds = final_max <= declared_position_cap + _TOLERANCE
        gross_cap_holds = final_max_gross <= declared_gross_cap + _TOLERANCE
        cap_checks[mapping_id] = position_cap_holds and gross_cap_holds
        cap_cases[mapping_id] = {
            "mapping_id": mapping_id,
            "contract_sha256": mapped.contract_sha256,
            "declared_position_cap": declared_position_cap,
            "declared_gross_cap": declared_gross_cap,
            "final_max_abs_weight": final_max,
            "final_max_gross": final_max_gross,
            "position_cap_holds": position_cap_holds,
            "gross_cap_holds": gross_cap_holds,
            "signal_sha256": _hash_array(signal),
            "weights_sha256": _hash_array(mapped.weights),
            "transition_reasons": [list(item) for item in mapped.transition_reasons],
        }

    cap_result = cap_results[CROSS_SECTIONAL_ZERO_NET]
    declared_cap = float(cs_contract.parameters["position_cap"])
    final_max = float(np.max(np.abs(cap_result.weights)))
    cap_holds = cap_checks[CROSS_SECTIONAL_ZERO_NET]
    all_mapping_caps_hold = all(cap_checks.values())
    gross_reduced = float(np.abs(cap_result.weights).sum()) < float(
        cs_contract.parameters["gross_target"]
    ) - _TOLERANCE

    relative = np.linspace(-1.0, 1.0, 6)[:, None]
    common_mode_pair = np.hstack([relative, relative + 100.0])
    cs_common = map_portfolio(common_mode_pair, cs_contract)
    cs_common_deleted = bool(
        np.allclose(
            cs_common.weights[:, 0],
            cs_common.weights[:, 1],
            rtol=0.0,
            atol=_TOLERANCE,
        )
    )
    directional_common_signal = np.full((6, 3), 0.95, dtype=float)
    ts_common = map_portfolio(directional_common_signal, ts_contract)
    ts_common_preserved = bool(
        np.all(ts_common.weights.sum(axis=0) > _ACTIVE_WEIGHT_EPSILON)
    )

    singleton_signal = np.full((6, 8), np.nan, dtype=float)
    singleton_signal[2, 1] = 1.0
    singleton_result = map_portfolio(singleton_signal, sparse_contract)
    singleton_counts = (np.abs(singleton_result.weights) > _ACTIVE_WEIGHT_EPSILON).sum(
        axis=0
    )
    singleton_preserved = bool(np.any(singleton_counts == 1))

    hysteresis_signal = np.asarray([[0.0, 0.80, 0.40, np.nan, 0.10]], dtype=float)
    hysteresis_result = map_portfolio(hysteresis_signal, ts_contract)
    hysteresis_weights = hysteresis_result.weights[0]
    hysteresis_holds = bool(
        hysteresis_weights[1] > 0
        and math_isclose(hysteresis_weights[1], hysteresis_weights[2])
        and math_isclose(hysteresis_weights[2], hysteresis_weights[3])
        and math_isclose(hysteresis_weights[4], 0.0)
    )

    event_signal = np.zeros((1, 7), dtype=float)
    event_signal[0, 1] = 1.0
    event_signal[0, 2] = np.nan
    event_result = map_portfolio(event_signal, sparse_contract)
    event_weights = event_result.weights[0]
    hold_period = int(sparse_contract.parameters["fixed_holding_period"])
    expected_active = list(range(1, 1 + hold_period))
    observed_active = np.flatnonzero(np.abs(event_weights) > _ACTIVE_WEIGHT_EPSILON).tolist()
    event_hold_and_exit = bool(
        observed_active == expected_active
        and math_isclose(event_weights[1 + hold_period], 0.0)
    )
    sparse_missing_held = _reason_count(event_result, "MISSING_SIGNAL_HELD") > 0

    cs_missing_signal = np.asarray(
        [[-1.0], [-0.5], [np.nan], [0.5], [1.0], [1.5]], dtype=float
    )
    cs_missing_result = map_portfolio(cs_missing_signal, cs_contract)
    cs_missing_excluded = bool(
        math_isclose(cs_missing_result.weights[2, 0], 0.0)
        and cs_missing_result.feasible[0]
    )
    explicit_no_trade = map_portfolio(np.zeros((2, 6), dtype=float), sparse_contract)
    explicit_no_trade_stays_flat = bool(
        np.allclose(explicit_no_trade.weights, 0.0, rtol=0.0, atol=_TOLERANCE)
    )

    checks = {
        "final_position_cap_holds": cap_holds,
        "final_position_cap_holds_all_mappings": all_mapping_caps_hold,
        "infeasible_unit_gross_is_explicitly_reduced": gross_reduced,
        "cross_sectional_common_mode_deleted": cs_common_deleted,
        "directional_common_mode_preserved": ts_common_preserved,
        "singleton_sparse_event_preserved": singleton_preserved,
        "directional_hysteresis_holds_then_exits": hysteresis_holds,
        "sparse_event_holds_then_explicitly_exits": event_hold_and_exit,
        "directional_missing_observation_holds_state": _reason_count(
            hysteresis_result, "MISSING_SIGNAL_HELD"
        )
        > 0,
        "sparse_missing_observation_holds_state": sparse_missing_held,
        "cross_sectional_missing_asset_excluded": cs_missing_excluded,
        "explicit_no_trade_stays_flat": explicit_no_trade_stays_flat,
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"mapping synthetic behavior regression: {failed}")

    all_checks_pass = all(checks.values())
    return {
        "schema_version": 1,
        "scope": "deterministic synthetic mapping behavior; no market or sealed data",
        "checks": checks,
        "all_checks_pass": all_checks_pass,
        "cases": {
            "position_cap": {
                "all_mappings_pass": all_mapping_caps_hold,
                "mappings": cap_cases,
                # Compatibility summary for consumers of the original
                # cross-sectional-only evidence shape.
                "mapping_id": CROSS_SECTIONAL_ZERO_NET,
                "contract_sha256": cap_result.contract_sha256,
                "declared_cap": declared_cap,
                "requested_gross": float(cs_contract.parameters["gross_target"]),
                "realized_gross": float(np.abs(cap_result.weights).sum()),
                "final_max_abs_weight": final_max,
                "transition_reasons": [list(item) for item in cap_result.transition_reasons],
            },
            "common_mode": {
                "cross_sectional_weights": _json_array(cs_common.weights),
                "cross_sectional_weight_turnover": float(
                    np.abs(cs_common.weights[:, 1] - cs_common.weights[:, 0]).sum()
                ),
                "directional_weights": _json_array(ts_common.weights),
                "directional_net_exposure": ts_common.weights.sum(axis=0).tolist(),
            },
            "singleton_sparse_event": {
                "contract_sha256": singleton_result.contract_sha256,
                "active_assets_by_coordinate": singleton_counts.astype(int).tolist(),
                "weights": _json_array(singleton_result.weights),
            },
            "directional_hysteresis": {
                "signal": _json_array(hysteresis_signal),
                "weights": hysteresis_weights.tolist(),
                "transition_reasons": [
                    list(item) for item in hysteresis_result.transition_reasons
                ],
            },
            "event_hold_exit_and_missing": {
                "signal": _json_array(event_signal),
                "weights": event_weights.tolist(),
                "expected_active_coordinates": expected_active,
                "observed_active_coordinates": observed_active,
                "transition_reasons": [list(item) for item in event_result.transition_reasons],
            },
            "cross_sectional_missing": {
                "signal": _json_array(cs_missing_signal),
                "weights": _json_array(cs_missing_result.weights),
            },
        },
    }


_ACTIVE_WEIGHT_EPSILON = 1e-12


def _sum(values: Iterable[float]) -> float:
    return float(np.sum(np.asarray(list(values), dtype=float)))


def mapping_turnover_rows() -> list[dict[str, Any]]:
    """Aggregate exact turnover identities for all seven positive families."""

    rows: list[dict[str, Any]] = []
    for family_id in FAMILY_IDS:
        case = build_synthetic_case(family_id, FIXED_EVIDENCE_SEED)
        mapped = case.positive_mapping
        decomposition = turnover_decomposition(
            case.signals["positive"], mapped.weights, FIXED_COST_BPS
        )
        raw_movement = _sum(decomposition["raw_signal_movement_l1_native_units"])
        entry = _sum(decomposition["entry_portfolio_establishment_l1"])
        rebalance = _sum(decomposition["rebalance_turnover_l1"])
        exit_ = _sum(decomposition["exit_turnover_l1"])
        full_l1 = _sum(decomposition["mapped_full_l1_turnover"])
        direct = _sum(
            decomposition["direct_clipped_signal_counterfactual_turnover"]
        )
        excess = _sum(decomposition["mapping_excess_vs_direct_counterfactual_l1"])
        fixed_cost = _sum(decomposition["fixed_cost"])
        component_residual = full_l1 - (entry + rebalance + exit_)
        counterfactual_residual = excess - (full_l1 - direct)
        cost_residual = fixed_cost - full_l1 * FIXED_COST_BPS / 10_000.0
        checks = {
            "components_sum_to_full_l1": math_isclose(component_residual, 0.0),
            "excess_matches_declared_direct_counterfactual": math_isclose(
                counterfactual_residual, 0.0
            ),
            "fixed_cost_matches_full_l1_rate": math_isclose(cost_residual, 0.0),
        }
        if not all(checks.values()):
            raise AssertionError(f"turnover identity failed for {family_id}: {checks}")
        rows.append(
            {
                "family_id": family_id,
                "seed": FIXED_EVIDENCE_SEED,
                "portfolio_mapping_id": mapped.portfolio_mapping_id,
                "mapping_contract_sha256": mapped.contract_sha256,
                "coordinates": int(mapped.weights.shape[1]),
                "raw_signal_movement_l1_native_units": raw_movement,
                "entry_portfolio_establishment_l1": entry,
                "rebalance_turnover_l1": rebalance,
                "exit_turnover_l1": exit_,
                "mapped_full_l1_turnover": full_l1,
                "direct_clipped_signal_counterfactual_turnover": direct,
                "mapping_excess_vs_direct_counterfactual_l1": excess,
                "fixed_cost_bps": FIXED_COST_BPS,
                "fixed_cost": fixed_cost,
                "component_identity_residual": component_residual,
                "counterfactual_identity_residual": counterfactual_residual,
                "cost_identity_residual": cost_residual,
                "identity_checks": checks,
                "all_identities_hold": True,
            }
        )
    return rows


def _counterfactual_signal() -> np.ndarray:
    assets, periods = 6, 32
    time = np.arange(periods, dtype=float)
    relative = np.linspace(-0.75, 0.75, assets)[:, None]
    common = np.select(
        [time < 5, time < 11, time < 16, time < 22, time < 27],
        [0.0, 0.90, 0.35, -0.90, -0.35],
        default=0.0,
    )
    modulation = 0.75 + 0.25 * np.cos(time / 4.0)
    return common[None, :] + relative * modulation[None, :]


def mapping_cost_counterfactual_payload() -> dict[str, Any]:
    """Map one raw signal three ways and report bounded cost consequences."""

    signal = _counterfactual_signal()
    target = 0.001 * np.tanh(signal) + 0.00002 * np.sin(
        (np.arange(signal.shape[0])[:, None] + 1.0)
        * (np.arange(signal.shape[1])[None, :] + 1.0)
        / 7.0
    )
    systems: list[dict[str, Any]] = []
    weight_hashes: set[str] = set()
    for mapping_id in (
        CROSS_SECTIONAL_ZERO_NET,
        TIME_SERIES_DIRECTIONAL_STATEFUL,
        SPARSE_EVENT_OR_CARRY,
    ):
        mapped = map_portfolio(signal, DEFAULT_MAPPING_CONTRACTS[mapping_id])
        path = portfolio_series(mapped.weights, target, FIXED_COST_BPS)
        weight_sha256 = _hash_array(mapped.weights)
        weight_hashes.add(weight_sha256)
        full_l1 = float(np.sum(path["turnover"]))
        cost = float(np.sum(path["cost"]))
        _assert_close(
            cost,
            full_l1 * FIXED_COST_BPS / 10_000.0,
            f"counterfactual cost identity {mapping_id}",
        )
        systems.append(
            {
                "portfolio_mapping_id": mapping_id,
                "mapping_contract_sha256": mapped.contract_sha256,
                "weights_sha256": weight_sha256,
                "shape": list(mapped.weights.shape),
                "feasible_coordinates": int(np.count_nonzero(mapped.feasible)),
                "max_abs_weight": float(np.max(np.abs(mapped.weights))),
                "mean_gross_exposure": float(
                    np.mean(np.abs(mapped.weights).sum(axis=0))
                ),
                "mean_net_exposure": float(np.mean(mapped.weights.sum(axis=0))),
                "gross_return": {
                    "mean": float(np.mean(path["gross"])),
                    "sum": float(np.sum(path["gross"])),
                    "path": path["gross"].tolist(),
                },
                "turnover": {
                    "mean": float(np.mean(path["turnover"])),
                    "sum": full_l1,
                    "path": path["turnover"].tolist(),
                    "convention": "full_L1_no_divide_by_two",
                },
                "cost": {
                    "bps_per_full_l1": FIXED_COST_BPS,
                    "mean": float(np.mean(path["cost"])),
                    "sum": cost,
                    "path": path["cost"].tolist(),
                },
                "net_return": {
                    "mean": float(np.mean(path["net"])),
                    "sum": float(np.sum(path["net"])),
                    "path": path["net"].tolist(),
                },
            }
        )
    if len(weight_hashes) != 3:
        raise AssertionError("three explicit mappings unexpectedly produced identical weights")
    return {
        "schema_version": 1,
        "scope": "same deterministic raw signal and synthetic target; no market or sealed data",
        "raw_signal_sha256": _hash_array(signal),
        "synthetic_target_sha256": _hash_array(target),
        "coordinates": {"assets": signal.shape[0], "periods": signal.shape[1]},
        "systems": systems,
        "all_weight_paths_distinct": True,
        "conclusion_boundary": {
            "supported": [
                "the declared mapping alone changes weights, full-L1 turnover, fixed-rate cost, and synthetic gross/net paths for identical inputs",
                "contract hashes and weight hashes identify each deterministic counterfactual",
            ],
            "not_supported": [
                "mapping caused the majority of historical turnover or cost-killed candidates",
                "one mapping is economically superior on real data",
                "the fixed 5 bps rate represents spread, slippage, impact, fill probability, or capacity",
                "raw-signal movement and mapped turnover are directly subtractable economic units",
            ],
        },
    }


__all__ = [
    "FIXED_EVIDENCE_SEED",
    "mapping_cost_counterfactual_payload",
    "mapping_synthetic_behavior_payload",
    "mapping_turnover_rows",
]
