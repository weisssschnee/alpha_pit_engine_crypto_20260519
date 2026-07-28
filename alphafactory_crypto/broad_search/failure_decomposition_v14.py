"""Existing-ledger-only failure decomposition for Crypto Search Engine V1.4.

This module is deliberately not an evaluator.  It reads the committed V1.4
ledger, archive, contracts, and aligned-carrier mark-availability metadata.  It
does not materialize candidate expressions, read reward labels, or call
``evaluate_pair``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from .panel18m import RawPanelStore


AUDIT_ID = "CRYPTO_SEARCH_ENGINE_V1_4_EXISTING_LEDGER_FAILURE_DECOMPOSITION"
DEFAULT_DATE = "20260728"
SOURCE_RUNTIME = "runtime/crypto_search_engine_v1_4_oi_flow_20260728"
SOURCE_REPORT = "reports/CRYPTO_SEARCH_ENGINE_V1_4_OI_FLOW_20260728.md"
OUTPUT_RUNTIME_PREFIX = (
    "runtime/crypto_search_engine_v1_4_failure_decomposition_"
)
OUTPUT_REPORT_PREFIX = (
    "reports/CRYPTO_SEARCH_ENGINE_V1_4_FAILURE_DECOMPOSITION_"
)

NEAR_MISS_DISTANCE = -1.0
NEAR_MISS_MINIMUM_RATE = 0.01
SECONDARY_NEAR_MISS_DISTANCE = -2.0
CHECKPOINT_MINIMUM_LEVEL_COUNT = 5
CHECKPOINT_MINIMUM_COMPARISONS = 2
STABLE_RANK_CORRELATION_MINIMUM = 0.60
COST_KILL_DOMINANCE_MINIMUM = 0.50

AXIS_ORDER = ("AB_MINUS_A", "AB_MINUS_B", "ABC_MINUS_AB")
AXIS_COLUMNS = {
    "AB_MINUS_A": "interaction_left_distance",
    "AB_MINUS_B": "interaction_right_distance",
    "ABC_MINUS_AB": "conditional_distance",
}


def _json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=_json_default,
    ).encode("utf-8")


def _json_default(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if pd.isna(value):
        return None
    raise TypeError(f"not JSON serializable: {type(value)!r}")


def _payload_sha(value: Any) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest().upper()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            default=_json_default,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_parquet(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(list(rows)).to_parquet(path, index=False)


def _git_sha(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        text=True,
    ).strip().lower()


def _finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _joined(values: Iterable[str]) -> str:
    return "|".join(sorted(set(value for value in values if value)))


def _oi_metric_statistic(field_id: str) -> str:
    if "__" not in field_id:
        return ""
    tail = field_id.split("__", 1)[1]
    for suffix in ("_last", "_mean", "_min", "_max"):
        if tail.endswith(suffix):
            return f"{tail[: -len(suffix)]}:{suffix[1:]}"
    return tail


def _augment_ledger(
    ledger: pd.DataFrame, archive: pd.DataFrame
) -> pd.DataFrame:
    required = {
        "candidate_id",
        "stage",
        "checkpoint_index",
        "pair_reward",
        "hierarchical_three_axis",
        "candidate_spec_json",
        "semantic_tuple",
        "net_mean",
        "cost_mean",
        "turnover_mean",
        "support",
    }
    missing = sorted(required - set(ledger.columns))
    if missing:
        raise ValueError(f"V1.4 ledger columns missing: {missing}")
    if ledger["candidate_id"].nunique() != len(ledger):
        raise ValueError("V1.4 ledger is not exact-unique")
    annotations = archive[
        ["exact_expression_id", "gross_mean_annotation"]
    ].rename(columns={"exact_expression_id": "candidate_id"})
    output = ledger.merge(
        annotations,
        on="candidate_id",
        how="left",
        validate="one_to_one",
    )
    if output["gross_mean_annotation"].isna().any():
        raise ValueError("gross annotations are incomplete")
    specs = output["candidate_spec_json"].map(json.loads)
    genes = specs.map(lambda item: dict(item["generation_genes"]))
    output["candidate_class"] = np.where(
        output["hierarchical_three_axis"].fillna(False).astype(bool),
        "HIERARCHICAL",
        "BINARY",
    )
    output["semantic_tuple_label"] = output["semantic_tuple"].fillna(
        "BINARY_BASELINE"
    )
    output["horizon_hours"] = specs.map(
        lambda item: int(item["horizon_hours"])
    )
    for name in (
        "left_field",
        "right_field",
        "condition_field",
        "auxiliary_field",
        "left_window",
        "right_window",
        "condition_window",
        "left_normalizer",
        "right_normalizer",
        "condition_normalizer",
    ):
        output[name] = genes.map(lambda item, key=name: item.get(key))
    raw_fields = output["raw_fields_json"].map(json.loads)
    output["venue"] = raw_fields.map(
        lambda values: _joined(
            value.split("__", 1)[0] for value in values if "__" in value
        )
        or "NO_OI_VENUE"
    )
    output["oi_metric_statistic"] = raw_fields.map(
        lambda values: _joined(
            _oi_metric_statistic(value)
            for value in values
            if "__" in value
        )
        or "NO_OI_METRIC"
    )
    output["flow_field"] = raw_fields.map(
        lambda values: _joined(value for value in values if "__" not in value)
        or "NO_AGGTRADES_FIELD"
    )
    return output


def _constraint_bottleneck_rows(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    stage_b = frame.loc[frame["stage"].eq("STAGE_B")].copy()
    group_columns = (
        "candidate_class",
        "semantic_tuple_label",
        "horizon_hours",
    )
    for keys, group in stage_b.groupby(list(group_columns), dropna=False):
        candidate_class, semantic_tuple, horizon = keys
        base = {
            "scope": "STAGE_B",
            "candidate_class": str(candidate_class),
            "semantic_tuple": str(semantic_tuple),
            "horizon_hours": int(horizon),
            "candidate_count": int(len(group)),
        }
        if candidate_class == "BINARY":
            for sleeve in ("A", "B"):
                rows.append(
                    {
                        **base,
                        "sleeve_or_increment": sleeve,
                        "availability": "NOT_PERSISTED",
                        "distance_count": 0,
                        "distance_mean": None,
                        "distance_median": None,
                        "distance_max": None,
                        "deterministic_bottleneck_count": None,
                        "deterministic_bottleneck_rate": None,
                        "tied_minimum_count": None,
                        "net_lcb": "NOT_PERSISTED",
                        "worst_month": "NOT_PERSISTED",
                        "positive_month_fraction": "NOT_PERSISTED",
                        "turnover_constraint": "NOT_PERSISTED",
                        "cost_constraint": "NOT_PERSISTED",
                        "concentration": "NOT_PERSISTED",
                        "support_constraint": "NOT_PERSISTED",
                        "evidence_note": (
                            "Binary pair_reward persists only min(A-axis,"
                            " B-axis); axis attribution was not written."
                        ),
                    }
                )
            rows.append(
                {
                    **base,
                    "sleeve_or_increment": "PAIR_MIN_A_OR_B",
                    "availability": "PERSISTED_PAIR_MIN_ONLY",
                    "distance_count": int(len(group)),
                    "distance_mean": float(group["pair_reward"].mean()),
                    "distance_median": float(group["pair_reward"].median()),
                    "distance_max": float(group["pair_reward"].max()),
                    "deterministic_bottleneck_count": None,
                    "deterministic_bottleneck_rate": None,
                    "tied_minimum_count": None,
                    "net_lcb": "NOT_PERSISTED",
                    "worst_month": "NOT_PERSISTED",
                    "positive_month_fraction": "NOT_PERSISTED",
                    "turnover_constraint": "NOT_PERSISTED",
                    "cost_constraint": "NOT_PERSISTED",
                    "concentration": "NOT_PERSISTED",
                    "support_constraint": "NOT_PERSISTED",
                    "evidence_note": "The binding strict constraint name is absent.",
                }
            )
            continue

        distances = group[[AXIS_COLUMNS[value] for value in AXIS_ORDER]]
        values = distances.to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise ValueError("hierarchical distance waterfall is incomplete")
        minimum = np.min(values, axis=1)
        deterministic = np.argmin(values, axis=1)
        ties = (values == minimum[:, None]).sum(axis=1) > 1
        for axis_index, axis in enumerate(AXIS_ORDER):
            series = group[AXIS_COLUMNS[axis]].astype(float)
            rows.append(
                {
                    **base,
                    "sleeve_or_increment": axis,
                    "availability": "PERSISTED_DISTANCE_ONLY",
                    "distance_count": int(series.notna().sum()),
                    "distance_mean": float(series.mean()),
                    "distance_median": float(series.median()),
                    "distance_max": float(series.max()),
                    "deterministic_bottleneck_count": int(
                        (deterministic == axis_index).sum()
                    ),
                    "deterministic_bottleneck_rate": float(
                        (deterministic == axis_index).mean()
                    ),
                    "tied_minimum_count": int(ties.sum()),
                    "net_lcb": "NOT_PERSISTED",
                    "worst_month": "NOT_PERSISTED",
                    "positive_month_fraction": "NOT_PERSISTED",
                    "turnover_constraint": "NOT_PERSISTED",
                    "cost_constraint": "NOT_PERSISTED",
                    "concentration": "NOT_PERSISTED",
                    "support_constraint": "NOT_PERSISTED",
                    "evidence_note": (
                        "Axis distance persisted; the seven component margins"
                        " and first failing constraint did not."
                    ),
                }
            )
        for sleeve in ("A", "B", "AB", "ABC"):
            rows.append(
                {
                    **base,
                    "sleeve_or_increment": sleeve,
                    "availability": "NOT_PERSISTED_STANDALONE",
                    "distance_count": 0,
                    "distance_mean": None,
                    "distance_median": None,
                    "distance_max": None,
                    "deterministic_bottleneck_count": None,
                    "deterministic_bottleneck_rate": None,
                    "tied_minimum_count": None,
                    "net_lcb": "NOT_PERSISTED",
                    "worst_month": "NOT_PERSISTED",
                    "positive_month_fraction": "NOT_PERSISTED",
                    "turnover_constraint": "NOT_PERSISTED",
                    "cost_constraint": "NOT_PERSISTED",
                    "concentration": "NOT_PERSISTED",
                    "support_constraint": "NOT_PERSISTED",
                    "evidence_note": (
                        "Evaluator computed this sleeve in memory but V1.4"
                        " ledger did not persist its metrics."
                    ),
                }
            )
    return rows


def _waterfall_summary(
    group: pd.DataFrame,
    *,
    base: Mapping[str, Any],
    sleeve: str,
    availability: str,
) -> dict[str, Any]:
    if availability != "PERSISTED_FINAL_INCREMENT_ANNOTATIONS":
        return {
            **base,
            "sleeve_or_increment": sleeve,
            "availability": availability,
            "candidate_count": int(len(group)),
            "gross_positive_count": None,
            "gross_positive_rate": None,
            "net_positive_count": None,
            "net_positive_rate": None,
            "net_lcb_positive_count": None,
            "cost_sign_killed_count": None,
            "cost_sign_killed_rate": None,
            "monthly_instability_count": None,
            "gross_mean": None,
            "net_mean": None,
            "cost_mean": None,
            "turnover_mean": None,
            "support_mean": None,
            "evidence_note": "Required economic or monthly metrics were not persisted.",
        }
    gross_positive = group["gross_mean_annotation"].gt(0.0)
    net_positive = group["net_mean"].gt(0.0)
    cost_killed = gross_positive & ~net_positive
    return {
        **base,
        "sleeve_or_increment": sleeve,
        "availability": availability,
        "candidate_count": int(len(group)),
        "gross_positive_count": int(gross_positive.sum()),
        "gross_positive_rate": float(gross_positive.mean()),
        "net_positive_count": int(net_positive.sum()),
        "net_positive_rate": float(net_positive.mean()),
        "net_lcb_positive_count": None,
        "cost_sign_killed_count": int(cost_killed.sum()),
        "cost_sign_killed_rate": float(cost_killed.mean()),
        "monthly_instability_count": None,
        "gross_mean": float(group["gross_mean_annotation"].mean()),
        "net_mean": float(group["net_mean"].mean()),
        "cost_mean": float(group["cost_mean"].mean()),
        "turnover_mean": float(group["turnover_mean"].mean()),
        "support_mean": float(group["support"].mean()),
        "evidence_note": (
            "Gross/net/cost/turnover/support are final incremental annotations;"
            " net LCB and monthly waterfall are absent."
        ),
    }


def _economic_waterfall_rows(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    stage_b = frame.loc[frame["stage"].eq("STAGE_B")]
    for keys, group in stage_b.groupby(
        ["candidate_class", "semantic_tuple_label", "horizon_hours"],
        dropna=False,
    ):
        candidate_class, semantic_tuple, horizon = keys
        base = {
            "scope": "STAGE_B",
            "candidate_class": str(candidate_class),
            "semantic_tuple": str(semantic_tuple),
            "horizon_hours": int(horizon),
        }
        if candidate_class == "HIERARCHICAL":
            for sleeve in ("A", "B", "AB", "AB_MINUS_A", "AB_MINUS_B"):
                rows.append(
                    _waterfall_summary(
                        group,
                        base=base,
                        sleeve=sleeve,
                        availability="NOT_PERSISTED",
                    )
                )
            rows.append(
                _waterfall_summary(
                    group,
                    base=base,
                    sleeve="ABC_MINUS_AB",
                    availability="PERSISTED_FINAL_INCREMENT_ANNOTATIONS",
                )
            )
            rows.append(
                _waterfall_summary(
                    group,
                    base=base,
                    sleeve="ABC",
                    availability="NOT_PERSISTED",
                )
            )
        else:
            for sleeve in ("A", "B", "PRIMARY"):
                rows.append(
                    _waterfall_summary(
                        group,
                        base=base,
                        sleeve=sleeve,
                        availability="NOT_PERSISTED",
                    )
                )
            rows.append(
                _waterfall_summary(
                    group,
                    base=base,
                    sleeve="PRIMARY_MINUS_LEFT_CONTROL",
                    availability="PERSISTED_FINAL_INCREMENT_ANNOTATIONS",
                )
            )
    return rows


def _checkpoint_rank_correlations(
    frame: pd.DataFrame, dimension: str
) -> list[float]:
    grouped = (
        frame.groupby(["checkpoint_index", dimension], dropna=False)[
            "pair_reward"
        ]
        .agg(["mean", "count"])
        .reset_index()
    )
    checkpoints = sorted(grouped["checkpoint_index"].unique().tolist())
    correlations: list[float] = []
    for left_index, left in enumerate(checkpoints):
        for right in checkpoints[left_index + 1 :]:
            first = grouped.loc[grouped["checkpoint_index"].eq(left)]
            second = grouped.loc[grouped["checkpoint_index"].eq(right)]
            joined = first.merge(
                second,
                on=dimension,
                suffixes=("_left", "_right"),
            )
            joined = joined.loc[
                joined["count_left"].ge(CHECKPOINT_MINIMUM_LEVEL_COUNT)
                & joined["count_right"].ge(CHECKPOINT_MINIMUM_LEVEL_COUNT)
            ]
            if len(joined) < 2:
                continue
            value = joined["mean_left"].corr(
                joined["mean_right"], method="spearman"
            )
            if pd.notna(value):
                correlations.append(float(value))
    return correlations


def _learnability_rows(frame: pd.DataFrame) -> list[dict[str, Any]]:
    stage_b = frame.loc[frame["stage"].eq("STAGE_B")].copy()
    top_count = max(1, int(math.ceil(len(stage_b) * 0.10)))
    top_ids = set(
        stage_b.nlargest(top_count, "pair_reward")["candidate_id"].astype(str)
    )
    dimensions = (
        "semantic_tuple_label",
        "venue",
        "oi_metric_statistic",
        "flow_field",
        "left_field",
        "right_field",
        "condition_field",
        "left_window",
        "right_window",
        "condition_window",
        "left_normalizer",
        "right_normalizer",
        "condition_normalizer",
        "horizon_hours",
    )
    rows: list[dict[str, Any]] = []
    for dimension in dimensions:
        correlations = _checkpoint_rank_correlations(stage_b, dimension)
        dimension_correlation = (
            float(np.median(correlations)) if correlations else None
        )
        for level, group in stage_b.groupby(dimension, dropna=False):
            effects: list[float] = []
            effect_signs: list[int] = []
            for checkpoint, local in group.groupby("checkpoint_index"):
                comparison = stage_b.loc[
                    stage_b["checkpoint_index"].eq(checkpoint)
                ]
                if (
                    len(local) < CHECKPOINT_MINIMUM_LEVEL_COUNT
                    or comparison.empty
                ):
                    continue
                effect = float(
                    local["pair_reward"].mean()
                    - comparison["pair_reward"].mean()
                )
                effects.append(effect)
                effect_signs.append(1 if effect > 0 else (-1 if effect < 0 else 0))
            nonzero = [value for value in effect_signs if value != 0]
            consistency = (
                max(Counter(nonzero).values()) / len(nonzero)
                if len(nonzero) >= CHECKPOINT_MINIMUM_COMPARISONS
                else None
            )
            top_members = group["candidate_id"].astype(str).isin(top_ids)
            rows.append(
                {
                    "dimension": dimension,
                    "level": "<NA>" if pd.isna(level) else str(level),
                    "candidate_count": int(len(group)),
                    "mean_pair_reward": float(group["pair_reward"].mean()),
                    "median_pair_reward": float(group["pair_reward"].median()),
                    "maximum_pair_reward": float(group["pair_reward"].max()),
                    "top_decile_member_count": int(top_members.sum()),
                    "top_decile_share": float(top_members.sum() / top_count),
                    "near_miss_count": int(
                        group["pair_reward"].ge(NEAR_MISS_DISTANCE).sum()
                    ),
                    "near_miss_rate": float(
                        group["pair_reward"].ge(NEAR_MISS_DISTANCE).mean()
                    ),
                    "secondary_near_miss_count": int(
                        group["pair_reward"]
                        .ge(SECONDARY_NEAR_MISS_DISTANCE)
                        .sum()
                    ),
                    "checkpoint_effect_count": int(len(effects)),
                    "checkpoint_effect_median": (
                        float(np.median(effects)) if effects else None
                    ),
                    "checkpoint_direction_consistency": consistency,
                    "dimension_checkpoint_rank_correlation_median": (
                        dimension_correlation
                    ),
                    "time_block_stability": "NOT_RECONSTRUCTIBLE",
                    "evidence_note": (
                        "Checkpoint consistency compares proposal batches, not"
                        " market time blocks; per-time-block rewards were absent."
                    ),
                }
            )
    rows.append(
        {
            "dimension": "market_time_block",
            "level": "early|middle|late",
            "candidate_count": int(len(stage_b)),
            "mean_pair_reward": None,
            "median_pair_reward": None,
            "maximum_pair_reward": None,
            "top_decile_member_count": None,
            "top_decile_share": None,
            "near_miss_count": None,
            "near_miss_rate": None,
            "secondary_near_miss_count": None,
            "checkpoint_effect_count": 0,
            "checkpoint_effect_median": None,
            "checkpoint_direction_consistency": None,
            "dimension_checkpoint_rank_correlation_median": None,
            "time_block_stability": "NOT_RECONSTRUCTIBLE",
            "evidence_note": (
                "The ledger contains one full-window reward per candidate and"
                " no early/middle/late economic metrics."
            ),
        }
    )
    return rows


def _target_execution_rows(
    *,
    repo_root: Path,
    source_runtime: Path,
    frame: pd.DataFrame,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    manifest = _read_json(source_runtime / "aligned_carrier_manifest.json")
    qualification = _read_json(
        source_runtime / "stage_a_carrier_qualification.json"
    )
    store = RawPanelStore.open(repo_root / str(manifest["cache_root"]))
    oi_fields = manifest["field_origins"][
        "OI_MARK_RANKS51_200_DELIVERED"
    ]
    mark_fields = sorted(
        value for value in oi_fields if "__mark_price_last" in value
    )
    if not mark_fields:
        raise ValueError("V1.4 carrier has no mark-price target fields")
    window = qualification["qualified_continuous_window"]
    block = store.block_slice(window["start"], window["end_exclusive"])
    base = np.asarray(store.base_eligible()[:, block], dtype=bool)
    finite = np.stack(
        [
            np.isfinite(np.asarray(store.field(value)[:, block], dtype=float))
            for value in mark_fields
        ]
    )
    choice = np.full(base.shape, -1, dtype=np.int16)
    # The source builder iterates sorted venues and fills only empty reference
    # coordinates.  Reverse assignment reproduces that first-finite rule
    # without reading or recomputing target returns.
    for index in range(len(mark_fields) - 1, -1, -1):
        choice[finite[index]] = index
    coordinate_count = int(base.sum())
    venue_counts = {
        field_id.split("__", 1)[0]: int(
            ((choice == index) & base).sum()
        )
        for index, field_id in enumerate(mark_fields)
    }
    assets_multi_priority = int(
        sum(
            len(set(choice[index][base[index]].tolist())) > 1
            for index in range(base.shape[0])
            if base[index].any()
        )
    )
    switch_metrics: dict[str, dict[str, Any]] = {}
    for horizon in (1, 4):
        width = 2 + horizon
        valid = (
            base[:, : -width]
            & (choice[:, 2 : -horizon] >= 0)
            & (choice[:, width:] >= 0)
        )
        switched = valid & (
            choice[:, 2 : -horizon] != choice[:, width:]
        )
        switch_metrics[str(horizon)] = {
            "valid_target_coordinates": int(valid.sum()),
            "cross_venue_endpoint_switches": int(switched.sum()),
            "cross_venue_endpoint_switch_rate": float(
                switched.sum() / max(1, valid.sum())
            ),
        }
    stage_b = frame.loc[frame["stage"].eq("STAGE_B")].copy()
    horizon_rows = {}
    for horizon, group in stage_b.groupby("horizon_hours"):
        gross_positive = group["gross_mean_annotation"].gt(0.0)
        net_positive = group["net_mean"].gt(0.0)
        horizon_rows[str(int(horizon))] = {
            "candidate_count": int(len(group)),
            "mean_pair_reward": float(group["pair_reward"].mean()),
            "gross_positive_rate": float(gross_positive.mean()),
            "net_positive_rate": float(net_positive.mean()),
            "cost_sign_killed_rate": float(
                (gross_positive & ~net_positive).mean()
            ),
            "turnover_mean": float(group["turnover_mean"].mean()),
        }
    rows: list[dict[str, Any]] = [
        {
            "check": "order_flow_source",
            "status": "OBSERVED",
            "value": "BINANCE_AGGTRADES_TOP200",
            "evidence": "V1.4 aligned carrier field origin",
            "implication": "Signal venue is Binance.",
        },
        {
            "check": "target_price_source",
            "status": "UNQUALIFIED_EXECUTION_SURFACE",
            "value": "FIRST_FINITE_SORTED_OI_VENUE_MARK",
            "evidence": (
                "build_oi_mark_search_carrier fills reference_price once while"
                " iterating sorted venues"
            ),
            "implication": (
                "Target is a mark-price label, not a frozen tradable execution"
                " venue or Binance price."
            ),
        },
        {
            "check": "priority_venue_rule",
            "status": "DETERMINISTIC_BUT_NOT_ECONOMICALLY_AUTHORIZED",
            "value": "|".join(mark_fields),
            "evidence": "Lexicographic first-finite field order",
            "implication": "Priority varies when earlier venue support is missing.",
        },
    ]
    for venue, count in venue_counts.items():
        rows.append(
            {
                "check": f"target_venue_share:{venue}",
                "status": "OBSERVED",
                "value": f"{count / max(1, coordinate_count):.12f}",
                "evidence": f"{count}/{coordinate_count} eligible coordinates",
                "implication": (
                    "Binance flow is evaluated against a non-Binance mark target."
                ),
            }
        )
    rows.extend(
        [
            {
                "check": "assets_with_multiple_priority_venues",
                "status": "OBSERVED",
                "value": f"{assets_multi_priority}/{int(base.any(axis=1).sum())}",
                "evidence": "Existing aligned-carrier mark availability",
                "implication": "The target venue is not asset-stationary.",
            },
            {
                "check": "target_endpoint_venue_switch_1h",
                "status": "OBSERVED",
                "value": str(
                    switch_metrics["1"]["cross_venue_endpoint_switch_rate"]
                ),
                "evidence": json.dumps(
                    switch_metrics["1"], sort_keys=True
                ),
                "implication": "Some log returns join marks from different venues.",
            },
            {
                "check": "target_endpoint_venue_switch_4h",
                "status": "OBSERVED",
                "value": str(
                    switch_metrics["4"]["cross_venue_endpoint_switch_rate"]
                ),
                "evidence": json.dumps(
                    switch_metrics["4"], sort_keys=True
                ),
                "implication": "Cross-venue endpoint mixing rises with horizon.",
            },
            {
                "check": "cost_execution_consistency",
                "status": "UNQUALIFIED",
                "value": "FIXED_5_BPS_FULL_L1",
                "evidence": "pair18m.FIXED_COST_BPS and CROSS_SECTIONAL_ZERO_NET",
                "implication": (
                    "No venue fee, mark-to-trade basis, slippage, or executable"
                    " instrument bridge is persisted."
                ),
            },
            {
                "check": "horizon_comparison",
                "status": "OBSERVED_FULL_WINDOW_ONLY",
                "value": json.dumps(horizon_rows, sort_keys=True),
                "evidence": "Existing Stage-B ledger annotations",
                "implication": (
                    "4h has lower turnover and less-negative reward than 1h;"
                    " 5m/15m was not tested and cannot be inferred."
                ),
            },
            {
                "check": "date_alignment",
                "status": "ENGINEERING_PASS_EXECUTION_HOLD",
                "value": "signal_t; label log(mark[t+2+h]/mark[t+2])",
                "evidence": "Committed target formula and pair contract",
                "implication": (
                    "Lag is explicit, but t+2 mark is not a qualified first"
                    " tradable execution price."
                ),
            },
        ]
    )
    facts = {
        "mark_fields_in_priority_order": mark_fields,
        "eligible_coordinates": coordinate_count,
        "venue_counts": venue_counts,
        "venue_shares": {
            key: value / max(1, coordinate_count)
            for key, value in venue_counts.items()
        },
        "assets_ever_eligible": int(base.any(axis=1).sum()),
        "assets_with_multiple_priority_venues": assets_multi_priority,
        "switch_metrics": switch_metrics,
        "horizon_ledger_metrics": horizon_rows,
        "target_return_arrays_read": False,
        "candidate_evaluator_called": False,
    }
    return rows, facts


def _decision_rows(
    *,
    frame: pd.DataFrame,
    learnability_rows: Sequence[Mapping[str, Any]],
    target_facts: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    stage_b = frame.loc[frame["stage"].eq("STAGE_B")]
    gross_positive = stage_b["gross_mean_annotation"].gt(0.0)
    net_positive = stage_b["net_mean"].gt(0.0)
    cost_killed = gross_positive & ~net_positive
    near_miss_rate = float(
        stage_b["pair_reward"].ge(NEAR_MISS_DISTANCE).mean()
    )
    cost_kill_share_of_gross_positive = float(
        cost_killed.sum() / max(1, gross_positive.sum())
    )
    horizon_rows = [
        row
        for row in learnability_rows
        if row["dimension"] == "horizon_hours"
    ]
    horizon_rank_correlation = next(
        (
            _finite_float(
                row["dimension_checkpoint_rank_correlation_median"]
            )
            for row in horizon_rows
            if _finite_float(
                row["dimension_checkpoint_rank_correlation_median"]
            )
            is not None
        ),
        None,
    )
    target_execution_qualified = False
    branches = [
        {
            "priority": 1,
            "branch": "TARGET_EXECUTION_CONTRACT_REPAIR",
            "condition": (
                "Signal and target execution venue must be aligned and 5 bps"
                " must correspond to a tradable execution surface."
            ),
            "observed": (
                f"target venues={target_facts['venue_shares']}; "
                f"multi-priority assets="
                f"{target_facts['assets_with_multiple_priority_venues']}; "
                "generic 5 bps only"
            ),
            "triggered": not target_execution_qualified,
            "next_action": (
                "Freeze a tradable venue-specific target/execution contract;"
                " do not rerun candidates in this audit."
            ),
        },
        {
            "priority": 2,
            "branch": "MAPPING_HOLDING_TURNOVER_REPAIR",
            "condition": (
                "Gross-positive candidates exist but at least half are"
                " sign-killed after cost."
            ),
            "observed": (
                f"gross_positive={int(gross_positive.sum())}/{len(stage_b)}; "
                f"net_positive={int(net_positive.sum())}/{len(stage_b)}; "
                f"cost_sign_killed={int(cost_killed.sum())}/{len(stage_b)}; "
                f"cost_kill_share_of_gross_positive="
                f"{cost_kill_share_of_gross_positive:.6f}"
            ),
            "triggered": (
                bool(gross_positive.any())
                and cost_kill_share_of_gross_positive
                >= COST_KILL_DOMINANCE_MINIMUM
            ),
            "next_action": (
                "Audit mapping, holding period, and turnover before expanding"
                " fields or operator count."
            ),
        },
        {
            "priority": 3,
            "branch": "SMALL_ADAPTIVE_V1_4B",
            "condition": (
                f"near-miss rate at reward>={NEAR_MISS_DISTANCE} must be at"
                f" least {NEAR_MISS_MINIMUM_RATE}; target execution qualified;"
                " stable gene ranking required."
            ),
            "observed": (
                f"near_miss_rate={near_miss_rate:.6f}; "
                f"horizon_rank_correlation={horizon_rank_correlation}; "
                f"target_execution_qualified={target_execution_qualified}"
            ),
            "triggered": bool(
                near_miss_rate >= NEAR_MISS_MINIMUM_RATE
                and target_execution_qualified
                and horizon_rank_correlation is not None
                and horizon_rank_correlation
                >= STABLE_RANK_CORRELATION_MINIMUM
            ),
            "next_action": "Not authorized by current evidence.",
        },
        {
            "priority": 4,
            "branch": "OPERATOR_BASIS_EXPANSION",
            "condition": (
                "Requires reconstructed evidence that A/B or AB is effective"
                " while multiplication or StateModulation is the failing layer."
            ),
            "observed": (
                "A/B/AB/ABC standalone economics and component constraints"
                " were not persisted."
            ),
            "triggered": False,
            "next_action": (
                "Residual, divergence, ConditionGate, or regime routing is a"
                " hypothesis only; do not authorize from V1.4 ledger."
            ),
        },
    ]
    primary = [
        row["branch"]
        for row in branches
        if row["triggered"] and row["priority"] <= 2
    ]
    decision = {
        "schema_version": 1,
        "audit_id": AUDIT_ID,
        "status": "PASS_LEDGER_FAILURE_DECOMPOSITION_WITH_PERSISTENCE_GAPS",
        "decision": (
            "HOLD_ADAPTIVE_TARGET_EXECUTION_AND_TURNOVER_REPAIR_FIRST"
        ),
        "triggered_primary_branches": primary,
        "adaptive_v1_4b_authorized": False,
        "operator_basis_expansion_authorized": False,
        "new_market_candidate_evaluations": 0,
        "alpha_claim": False,
        "oos": False,
        "promotion": False,
        "sealed_reads": 0,
        "research_decision": "HOLD_RESEARCH",
        "evidence_limits": [
            "standalone A/B/AB/ABC economics not persisted",
            "component constraint margins and violation names not persisted",
            "monthly waterfall not persisted",
            "market time-block reward stability not reconstructible",
        ],
    }
    return branches, decision


def _input_records(
    repo_root: Path, source_runtime: Path
) -> list[dict[str, Any]]:
    relative_paths = [
        f"{SOURCE_RUNTIME}/candidate_ledger.parquet",
        f"{SOURCE_RUNTIME}/behavior_archive.parquet",
        f"{SOURCE_RUNTIME}/frozen_contract.json",
        f"{SOURCE_RUNTIME}/aligned_carrier_manifest.json",
        f"{SOURCE_RUNTIME}/stage_a_carrier_qualification.json",
        f"{SOURCE_RUNTIME}/stage_b_semantic_gate.json",
        f"{SOURCE_RUNTIME}/final_decision.json",
        f"{SOURCE_RUNTIME}/run_manifest.json",
        SOURCE_REPORT,
        "alphafactory_crypto/broad_search/pair18m.py",
        "alphafactory_crypto/data_admission_v1.py",
        "config/crypto_search_engine_v1_4_oi_flow.json",
    ]
    rows = []
    for relative in relative_paths:
        path = repo_root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    cache_manifest = _read_json(
        source_runtime / "aligned_carrier_manifest.json"
    )
    rows.append(
        {
            "path": str(cache_manifest["cache_root"]),
            "bytes": int(cache_manifest["directory_bundle"]["bytes"]),
            "sha256": str(
                cache_manifest["directory_bundle"]["bundle_sha256"]
            ),
            "identity_role": "EXISTING_ALIGNED_CACHE_DIRECTORY_BUNDLE",
        }
    )
    return rows


def _manifest_records(
    repo_root: Path, runtime_root: Path, report_path: Path
) -> list[dict[str, Any]]:
    paths = [
        value
        for value in runtime_root.iterdir()
        if value.is_file() and value.name != "run_manifest.json"
    ]
    paths.append(report_path)
    return [
        {
            "path": path.relative_to(repo_root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
        for path in sorted(paths)
    ]


def _report_text(
    *,
    source_sha: str,
    decision: Mapping[str, Any],
    frame: pd.DataFrame,
    target_facts: Mapping[str, Any],
) -> str:
    stage_b = frame.loc[frame["stage"].eq("STAGE_B")]
    gross_positive = stage_b["gross_mean_annotation"].gt(0.0)
    net_positive = stage_b["net_mean"].gt(0.0)
    cost_killed = gross_positive & ~net_positive
    hierarchical = stage_b.loc[
        stage_b["candidate_class"].eq("HIERARCHICAL")
    ]
    axis_values = hierarchical[
        [AXIS_COLUMNS[value] for value in AXIS_ORDER]
    ].to_numpy(dtype=float)
    deterministic = np.argmin(axis_values, axis=1)
    bottlenecks = {
        axis: int((deterministic == index).sum())
        for index, axis in enumerate(AXIS_ORDER)
    }
    return "\n".join(
        [
            "# Crypto Search Engine V1.4 Failure Decomposition",
            "",
            f"- Audit source: `{source_sha}`.",
            "- Scope: committed V1.4 ledger/archive and aligned-carrier target metadata only; candidate evaluations: `0`.",
            f"- Stage-B rows: `{len(stage_b)}`; near misses at reward >= `{NEAR_MISS_DISTANCE}`: `{int(stage_b['pair_reward'].ge(NEAR_MISS_DISTANCE).sum())}`.",
            f"- Persisted hierarchical worst-axis attribution: `{bottlenecks}`.",
            f"- Final-increment gross positive: `{int(gross_positive.sum())}/{len(stage_b)}`; net positive: `{int(net_positive.sum())}/{len(stage_b)}`; cost sign-killed: `{int(cost_killed.sum())}/{len(stage_b)}`.",
            f"- Target venue shares: `{target_facts['venue_shares']}`; `{target_facts['assets_with_multiple_priority_venues']}/{target_facts['assets_ever_eligible']}` assets use multiple priority venues.",
            "- Target/execution finding: Binance aggTrades is evaluated against a lexicographic first-finite Bybit/Hyperliquid/OKX mark target, with no qualified unified tradable venue or venue-specific 5 bps bridge.",
            "- Persistence finding: V1.4 did not write standalone A/B/AB/ABC economics, component constraint margins, monthly waterfalls, or time-block rewards. These are `NOT_RECONSTRUCTIBLE` without market reevaluation.",
            f"- Decision: `{decision['decision']}`. Adaptive V1.4b and operator-basis expansion remain unauthorized.",
            "- Bias audit: `HOLD_RESEARCH`; OOS grade `NONE`; no Alpha, promotion, challenge, forward, or sealed-read claim.",
            "",
        ]
    )


def run_audit(
    repo_root: Path,
    *,
    runtime_date: str = DEFAULT_DATE,
    source_sha: str | None = None,
) -> dict[str, Any]:
    if runtime_date != DEFAULT_DATE:
        raise ValueError("V1.4 failure-decomposition date changed")
    source_sha = str(source_sha or _git_sha(repo_root)).lower()
    if source_sha != _git_sha(repo_root):
        raise ValueError("audit source SHA must equal checkout HEAD")
    source_runtime = repo_root / SOURCE_RUNTIME
    runtime_root = repo_root / f"{OUTPUT_RUNTIME_PREFIX}{runtime_date}"
    report_path = repo_root / f"{OUTPUT_REPORT_PREFIX}{runtime_date}.md"
    if runtime_root.exists() or report_path.exists():
        raise FileExistsError("audit output already exists")
    ledger = pd.read_parquet(source_runtime / "candidate_ledger.parquet")
    archive = pd.read_parquet(source_runtime / "behavior_archive.parquet")
    if len(ledger) != 1264 or len(archive) != 1264:
        raise ValueError("V1.4 source row count changed")
    frame = _augment_ledger(ledger, archive)
    input_records = _input_records(repo_root, source_runtime)
    input_hash_before = _payload_sha(input_records)

    constraint_rows = _constraint_bottleneck_rows(frame)
    waterfall_rows = _economic_waterfall_rows(frame)
    learnability_rows = _learnability_rows(frame)
    target_rows, target_facts = _target_execution_rows(
        repo_root=repo_root,
        source_runtime=source_runtime,
        frame=frame,
    )
    decision_rows, decision = _decision_rows(
        frame=frame,
        learnability_rows=learnability_rows,
        target_facts=target_facts,
    )
    runtime_root.mkdir(parents=True, exist_ok=False)
    contract = {
        "schema_version": 1,
        "audit_id": AUDIT_ID,
        "source_sha": source_sha,
        "source_v14_producer_sha": _read_json(
            source_runtime / "run_manifest.json"
        )["producer_source_sha"],
        "source_artifact_bundle_sha256": _read_json(
            source_runtime / "run_manifest.json"
        )["artifact_bundle_sha256"],
        "input_records": input_records,
        "input_bundle_sha256": input_hash_before,
        "rules": {
            "near_miss_distance": NEAR_MISS_DISTANCE,
            "near_miss_minimum_rate": NEAR_MISS_MINIMUM_RATE,
            "secondary_near_miss_distance": SECONDARY_NEAR_MISS_DISTANCE,
            "checkpoint_minimum_level_count": CHECKPOINT_MINIMUM_LEVEL_COUNT,
            "checkpoint_minimum_comparisons": (
                CHECKPOINT_MINIMUM_COMPARISONS
            ),
            "stable_rank_correlation_minimum": (
                STABLE_RANK_CORRELATION_MINIMUM
            ),
            "cost_kill_dominance_minimum": COST_KILL_DOMINANCE_MINIMUM,
        },
        "boundaries": {
            "candidate_evaluations": 0,
            "candidate_materializations": 0,
            "target_return_arrays_read": False,
            "mark_availability_read_for_target_provenance": True,
            "market_budget_consumed": 0,
            "sealed_reads": 0,
            "oos": False,
            "promotion": False,
        },
    }
    contract["contract_sha256"] = _payload_sha(contract)
    _write_json(runtime_root / "frozen_audit_contract.json", contract)
    _write_parquet(
        runtime_root / "constraint_bottleneck_matrix.parquet",
        constraint_rows,
    )
    _write_parquet(
        runtime_root / "economic_waterfall.parquet",
        waterfall_rows,
    )
    _write_parquet(
        runtime_root / "search_learnability.parquet",
        learnability_rows,
    )
    _write_parquet(
        runtime_root / "target_execution_semantics.parquet",
        target_rows,
    )
    _write_parquet(
        runtime_root / "automatic_branch_decision.parquet",
        decision_rows,
    )
    _write_json(runtime_root / "target_execution_facts.json", target_facts)
    _write_json(runtime_root / "final_decision.json", decision)
    report_path.write_text(
        _report_text(
            source_sha=source_sha,
            decision=decision,
            frame=frame,
            target_facts=target_facts,
        ),
        encoding="utf-8",
        newline="\n",
    )
    input_records_after = _input_records(repo_root, source_runtime)
    if _payload_sha(input_records_after) != input_hash_before:
        raise RuntimeError("V1.4 inputs changed during read-only audit")
    artifacts = _manifest_records(repo_root, runtime_root, report_path)
    manifest = {
        "schema_version": 1,
        "audit_id": AUDIT_ID,
        "producer_source_sha": source_sha,
        "input_bundle_sha256": input_hash_before,
        "artifact_bundle_sha256": _payload_sha(artifacts),
        "artifacts": artifacts,
        "source_inputs_unchanged": True,
        "candidate_evaluations": 0,
        "market_budget_consumed": 0,
        "sealed_reads": 0,
        "reproducible": True,
        "continuation": (
            "python -m "
            "alphafactory_crypto.broad_search.failure_decomposition_v14 "
            "check"
        ),
    }
    _write_json(runtime_root / "run_manifest.json", manifest)
    return {
        "result": "PASS",
        **decision,
        "artifact_bundle_sha256": manifest["artifact_bundle_sha256"],
        "input_bundle_sha256": input_hash_before,
    }


def check_audit(
    repo_root: Path, *, runtime_date: str = DEFAULT_DATE
) -> dict[str, Any]:
    runtime_root = repo_root / f"{OUTPUT_RUNTIME_PREFIX}{runtime_date}"
    report_path = repo_root / f"{OUTPUT_REPORT_PREFIX}{runtime_date}.md"
    required = (
        "frozen_audit_contract.json",
        "constraint_bottleneck_matrix.parquet",
        "economic_waterfall.parquet",
        "search_learnability.parquet",
        "target_execution_semantics.parquet",
        "automatic_branch_decision.parquet",
        "target_execution_facts.json",
        "final_decision.json",
        "run_manifest.json",
    )
    errors = [
        f"missing:{name}"
        for name in required
        if not (runtime_root / name).is_file()
    ]
    if not report_path.is_file():
        errors.append("missing:report")
    if errors:
        return {"result": "FAIL", "errors": errors}
    contract = _read_json(runtime_root / "frozen_audit_contract.json")
    decision = _read_json(runtime_root / "final_decision.json")
    manifest = _read_json(runtime_root / "run_manifest.json")
    contract_hash = _payload_sha(
        {
            key: value
            for key, value in contract.items()
            if key != "contract_sha256"
        }
    )
    if contract_hash != contract.get("contract_sha256"):
        errors.append("contract_sha256")
    current_inputs = _input_records(repo_root, repo_root / SOURCE_RUNTIME)
    if _payload_sha(current_inputs) != contract.get("input_bundle_sha256"):
        errors.append("input_bundle_changed")
    artifacts = manifest.get("artifacts", [])
    if _payload_sha(artifacts) != manifest.get("artifact_bundle_sha256"):
        errors.append("artifact_bundle")
    for record in artifacts:
        path = repo_root / str(record["path"])
        if (
            not path.is_file()
            or path.stat().st_size != int(record["bytes"])
            or _sha256_file(path) != str(record["sha256"])
        ):
            errors.append(f"artifact:{record['path']}")
    constraint = pd.read_parquet(
        runtime_root / "constraint_bottleneck_matrix.parquet"
    )
    waterfall = pd.read_parquet(
        runtime_root / "economic_waterfall.parquet"
    )
    learnability = pd.read_parquet(
        runtime_root / "search_learnability.parquet"
    )
    target = pd.read_parquet(
        runtime_root / "target_execution_semantics.parquet"
    )
    branches = pd.read_parquet(
        runtime_root / "automatic_branch_decision.parquet"
    )
    if not {
        "AB_MINUS_A",
        "AB_MINUS_B",
        "ABC_MINUS_AB",
    }.issubset(set(constraint["sleeve_or_increment"])):
        errors.append("hierarchical_axis_rows")
    if "ABC_MINUS_AB" not in set(waterfall["sleeve_or_increment"]):
        errors.append("waterfall_final_increment")
    if "market_time_block" not in set(learnability["dimension"]):
        errors.append("time_block_gap")
    if "cost_execution_consistency" not in set(target["check"]):
        errors.append("target_execution_contract")
    if not {
        "TARGET_EXECUTION_CONTRACT_REPAIR",
        "MAPPING_HOLDING_TURNOVER_REPAIR",
    }.issubset(set(branches.loc[branches["triggered"], "branch"])):
        errors.append("automatic_branch_decision")
    for key in (
        "candidate_evaluations",
        "market_budget_consumed",
        "sealed_reads",
    ):
        if int(manifest.get(key, -1)) != 0:
            errors.append(f"boundary:{key}")
    if decision.get("adaptive_v1_4b_authorized") is not False:
        errors.append("adaptive_authority")
    result = "PASS" if not errors else "FAIL"
    return {
        "result": result,
        "errors": errors,
        "producer_source_sha": manifest.get("producer_source_sha"),
        "input_bundle_sha256": manifest.get("input_bundle_sha256"),
        "artifact_bundle_sha256": manifest.get(
            "artifact_bundle_sha256"
        ),
        "candidate_evaluations": manifest.get("candidate_evaluations"),
        "market_budget_consumed": manifest.get("market_budget_consumed"),
        "decision": decision.get("decision"),
        "adaptive_v1_4b_authorized": decision.get(
            "adaptive_v1_4b_authorized"
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("run", "check"):
        local = subparsers.add_parser(command)
        local.add_argument("--runtime-date", default=DEFAULT_DATE)
        local.add_argument("--repo-root", type=Path, default=Path.cwd())
    arguments = parser.parse_args(argv)
    repo_root = arguments.repo_root.resolve()
    if arguments.command == "run":
        result = run_audit(
            repo_root,
            runtime_date=arguments.runtime_date,
        )
    else:
        result = check_audit(
            repo_root,
            runtime_date=arguments.runtime_date,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
