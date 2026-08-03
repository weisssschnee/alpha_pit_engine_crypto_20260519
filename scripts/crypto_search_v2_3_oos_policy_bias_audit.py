from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


AUDIT_ID = "CRYPTO_SEARCH_V2_3_OOS_POLICY_BIAS_AUDIT_20260803"
OOS_RUNTIME = Path("runtime/crypto_search_v2_3_frozen_oos_20260803")
TRAIN_RUNTIME = Path("runtime/crypto_search_mechanism_v2_3_20260802")
METRICS = ("primary_net", "matched_increment", "control_net")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _mechanism_template(candidate_spec_json: str) -> str:
    payload = json.loads(candidate_spec_json)
    return str(payload["generation_genes"]["mechanism_spec"]["template_id"])


def _correlation_summary(frame: pd.DataFrame) -> dict[str, Any]:
    correlation = frame.corr().fillna(0.0).to_numpy(dtype=float)
    if correlation.size == 0:
        raise RuntimeError("AUDIT_EMPTY_CORRELATION_MATRIX")
    triangle = correlation[np.triu_indices_from(correlation, k=1)]
    eigenvalues = np.clip(np.linalg.eigvalsh(correlation), 0.0, None)
    eigenvalue_sum = float(np.sum(eigenvalues))
    effective_rank = (
        float(eigenvalue_sum**2 / float(eigenvalues @ eigenvalues))
        if float(eigenvalues @ eigenvalues) > 0.0
        else 0.0
    )
    return {
        "candidate_count": int(frame.shape[1]),
        "pair_count": int(triangle.size),
        "median_pair_correlation": float(np.nanmedian(triangle)),
        "p90_pair_correlation": float(np.nanquantile(triangle, 0.90)),
        "p95_pair_correlation": float(np.nanquantile(triangle, 0.95)),
        "pair_share_above_0_90": float(np.nanmean(triangle > 0.90)),
        "pair_share_above_0_95": float(np.nanmean(triangle > 0.95)),
        "correlation_participation_ratio_effective_rank": effective_rank,
        "top_eigenvalue_share": float(np.max(eigenvalues) / eigenvalue_sum),
    }


def _moving_block_bootstrap(
    values: np.ndarray,
    *,
    label: str,
    block_length: int = 7,
    replications: int = 4096,
) -> dict[str, Any]:
    series = np.asarray(values, dtype=float)
    series = series[np.isfinite(series)]
    if series.size < block_length:
        raise RuntimeError("AUDIT_DAILY_PATH_TOO_SHORT")
    seed = int.from_bytes(
        hashlib.sha256(f"{AUDIT_ID}|{label}".encode()).digest()[:4], "big"
    )
    rng = np.random.default_rng(seed)
    block_count = int(math.ceil(series.size / block_length))
    offsets = np.arange(block_length, dtype=int)
    sample_means = np.empty(replications, dtype=float)
    for ordinal in range(replications):
        starts = rng.integers(0, series.size, size=block_count)
        indexes = (starts[:, None] + offsets[None, :]) % series.size
        sample_means[ordinal] = float(
            np.mean(series[indexes.reshape(-1)[: series.size]])
        )
    return {
        "observed_mean": float(np.mean(series)),
        "probability_positive": float(np.mean(sample_means > 0.0)),
        "q05": float(np.quantile(sample_means, 0.05)),
        "q10": float(np.quantile(sample_means, 0.10)),
        "paired_day_count": int(series.size),
        "block_length_days": int(block_length),
        "replications": int(replications),
        "bootstrap_seed": int(seed),
    }


def _cohort_paths(paths: pd.DataFrame, cohort: str) -> pd.DataFrame:
    keys = ["seed", "horizon_hours", "day_ordinal", "utc_day"]
    return (
        paths.loc[paths["cohort"].eq(cohort)]
        .groupby(keys, as_index=False, sort=True)[list(METRICS)]
        .mean()
        .sort_values(keys, kind="stable")
    )


def _family_reweighted_paths(
    paths: pd.DataFrame,
    *,
    champion_ids: set[str] | None = None,
) -> pd.DataFrame:
    local = paths.loc[paths["cohort"].eq("evolution_train_top")].copy()
    if champion_ids is not None:
        local = local.loc[local["candidate_id"].isin(champion_ids)]
        return _cohort_paths(local, "evolution_train_top")
    family_keys = [
        "seed",
        "horizon_hours",
        "day_ordinal",
        "utc_day",
        "behavior_family_id",
    ]
    cohort_keys = ["seed", "horizon_hours", "day_ordinal", "utc_day"]
    return (
        local.groupby(family_keys, as_index=False, sort=True)[list(METRICS)]
        .mean()
        .groupby(cohort_keys, as_index=False, sort=True)[list(METRICS)]
        .mean()
        .sort_values(cohort_keys, kind="stable")
    )


def _policy_sensitivity(
    right: pd.DataFrame,
    left: pd.DataFrame,
    *,
    label: str,
) -> dict[str, Any]:
    cell_metrics: list[dict[str, Any]] = []
    deltas: dict[str, list[np.ndarray]] = {
        "primary_net": [],
        "matched_increment": [],
    }
    for (seed, horizon), right_cell in right.groupby(
        ["seed", "horizon_hours"], sort=True
    ):
        left_cell = left.loc[
            left["seed"].eq(seed) & left["horizon_hours"].eq(horizon)
        ].sort_values("day_ordinal")
        right_cell = right_cell.sort_values("day_ordinal")
        if not np.array_equal(
            left_cell["day_ordinal"].to_numpy(),
            right_cell["day_ordinal"].to_numpy(),
        ):
            raise RuntimeError("AUDIT_POLICY_DAY_ALIGNMENT_CHANGED")
        row: dict[str, Any] = {
            "seed": int(seed),
            "horizon_hours": int(horizon),
        }
        for metric in METRICS:
            row[f"right_{metric}_mean"] = float(right_cell[metric].mean())
        for metric in ("primary_net", "matched_increment"):
            deltas[metric].append(
                right_cell[metric].to_numpy(dtype=float)
                - left_cell[metric].to_numpy(dtype=float)
            )
        cell_metrics.append(row)
    pooled: dict[str, Any] = {}
    for metric, values in deltas.items():
        pooled_delta = np.mean(np.stack(values, axis=0), axis=0)
        pooled[metric] = _moving_block_bootstrap(
            pooled_delta,
            label=f"post_hoc_sensitivity|{label}|{metric}",
        )
    return {
        "role": "POST_HOC_WEIGHTING_SENSITIVITY_NOT_QUALIFICATION",
        "cells": cell_metrics,
        "total_policy_minus_original_random_train_top": pooled,
    }


def build_audit(project_root: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    oos_root = project_root / OOS_RUNTIME
    train_root = project_root / TRAIN_RUNTIME
    required = {
        "oos_contract": oos_root / "frozen_contract.json",
        "oos_checker": oos_root / "official_checker_result.json",
        "oos_ledger": oos_root / "oos_candidate_ledger.parquet",
        "oos_paths": oos_root / "oos_candidate_daily_paths.parquet",
        "oos_cohort_metrics": oos_root / "oos_cohort_metrics.parquet",
        "oos_effects": oos_root / "oos_effects.json",
        "train_ledger": train_root / "candidate_ledger.parquet",
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        raise RuntimeError(f"AUDIT_REQUIRED_ARTIFACT_MISSING:{','.join(missing)}")

    contract = json.loads(required["oos_contract"].read_text(encoding="utf-8"))
    checker = json.loads(required["oos_checker"].read_text(encoding="utf-8"))
    effects = json.loads(required["oos_effects"].read_text(encoding="utf-8"))
    selection = pd.read_parquet(required["oos_ledger"])
    paths = pd.read_parquet(required["oos_paths"])
    cohort_metrics = pd.read_parquet(required["oos_cohort_metrics"])
    train_columns = [
        "candidate_id",
        "exact_expression_id",
        "canonical_expression_id",
        "behavior_family_id",
        "candidate_spec_json",
        "search_reward",
    ]
    train = pd.read_parquet(required["train_ledger"], columns=train_columns)
    expected_train_hash = str(
        contract["receipt"]["source_v23"]["candidate_ledger_sha256"]
    ).upper()
    actual_train_hash = _sha256(required["train_ledger"])
    if actual_train_hash != expected_train_hash:
        raise RuntimeError("AUDIT_TRAIN_LEDGER_HASH_CHANGED")
    if selection["candidate_id"].duplicated().any():
        raise RuntimeError("AUDIT_OOS_CANDIDATE_ID_DUPLICATED")
    joined = selection.merge(train, on="candidate_id", how="left", validate="one_to_one")
    if joined["candidate_spec_json"].isna().any():
        raise RuntimeError("AUDIT_TRAIN_CANDIDATE_MISSING")
    joined["mechanism_template"] = joined["candidate_spec_json"].map(
        _mechanism_template
    )
    paths = paths.merge(
        joined[
            [
                "candidate_id",
                "behavior_family_id",
                "search_reward",
                "mechanism_template",
            ]
        ],
        on="candidate_id",
        how="left",
        validate="many_to_one",
    )
    if paths["mechanism_template"].isna().any():
        raise RuntimeError("AUDIT_OOS_PATH_CANDIDATE_MISSING")

    cohort_identity: dict[str, Any] = {}
    for cohort, local in joined.groupby("cohort", sort=True):
        mechanisms = local["mechanism_template"].value_counts().sort_index()
        cohort_identity[str(cohort)] = {
            "candidate_count": int(len(local)),
            "evaluated_count": int(local["oos_status"].eq("EVALUATED").sum()),
            "exact_expression_count": int(local["exact_expression_id"].nunique()),
            "canonical_expression_count": int(
                local["canonical_expression_id"].nunique()
            ),
            "behavior_family_count": int(local["behavior_family_id"].nunique()),
            "behavior_duplicate_rate": float(
                1.0 - local["behavior_family_id"].nunique() / len(local)
            ),
            "mechanism_counts": {
                str(key): int(value) for key, value in mechanisms.items()
            },
        }

    absolute_cohort_economics: dict[str, Any] = {}
    for cohort, local in cohort_metrics.groupby("cohort", sort=True):
        absolute_cohort_economics[str(cohort)] = {
            "equal_seed_horizon_primary_net_mean": float(
                local["oos_primary_net_mean"].mean()
            ),
            "equal_seed_horizon_matched_increment_mean": float(
                local["oos_matched_increment"].mean()
            ),
            "positive_primary_cells": int(
                local["oos_primary_net_mean"].gt(0.0).sum()
            ),
            "positive_matched_cells": int(
                local["oos_matched_increment"].gt(0.0).sum()
            ),
            "cell_count": int(len(local)),
        }

    evolution_top = joined.loc[joined["cohort"].eq("evolution_train_top")]
    evolution_paths = paths.loc[paths["cohort"].eq("evolution_train_top")]
    family_cells: list[dict[str, Any]] = []
    mechanism_cells: list[dict[str, Any]] = []
    for (seed, horizon), local in evolution_top.groupby(
        ["seed", "horizon_hours"], sort=True
    ):
        counts = local["behavior_family_id"].value_counts()
        family_cells.append(
            {
                "seed": int(seed),
                "horizon_hours": int(horizon),
                "candidate_count": int(len(local)),
                "behavior_family_count": int(len(counts)),
                "behavior_duplicate_rate": float(1.0 - len(counts) / len(local)),
                "largest_family_member_count": int(counts.max()),
                "repeated_family_count": int(counts.gt(1).sum()),
            }
        )
        mechanism_counts = local["mechanism_template"].value_counts().sort_index()
        mechanism_cells.append(
            {
                "seed": int(seed),
                "horizon_hours": int(horizon),
                "mechanism_counts": {
                    str(key): int(value) for key, value in mechanism_counts.items()
                },
            }
        )

    mechanism_attribution: dict[str, Any] = {}
    for mechanism, local in evolution_paths.groupby("mechanism_template", sort=True):
        cells: list[dict[str, Any]] = []
        for (seed, horizon), cell in local.groupby(
            ["seed", "horizon_hours"], sort=True
        ):
            cells.append(
                {
                    "seed": int(seed),
                    "horizon_hours": int(horizon),
                    "candidate_count": int(cell["candidate_id"].nunique()),
                    **{
                        f"{metric}_mean": float(cell[metric].mean())
                        for metric in METRICS
                    },
                }
            )
        daily = (
            local.groupby(
                ["seed", "horizon_hours", "utc_day"], as_index=False, sort=True
            )[list(METRICS)]
            .mean()
            .groupby("utc_day", as_index=False, sort=True)[list(METRICS)]
            .mean()
        )
        daily["month"] = pd.to_datetime(daily["utc_day"]).dt.to_period("M").astype(str)
        monthly = daily.groupby("month", sort=True)[list(METRICS)].mean()
        primary_matrix = local.pivot(
            index="utc_day", columns="candidate_id", values="primary_net"
        )
        matched_matrix = local.pivot(
            index="utc_day", columns="candidate_id", values="matched_increment"
        )
        mechanism_attribution[str(mechanism)] = {
            "role": "POST_HOC_MECHANISM_ATTRIBUTION_NOT_FRESH_CONFIRMATION",
            "candidate_count": int(local["candidate_id"].nunique()),
            "available_seed_horizon_cell_count": int(len(cells)),
            "cells": cells,
            "positive_primary_month_count": int(monthly["primary_net"].gt(0.0).sum()),
            "positive_matched_month_count": int(
                monthly["matched_increment"].gt(0.0).sum()
            ),
            "month_count": int(len(monthly)),
            "monthly_equal_available_cell_means": {
                str(month): {
                    metric: float(row[metric]) for metric in METRICS
                }
                for month, row in monthly.iterrows()
            },
            "primary_path_correlation": _correlation_summary(primary_matrix),
            "matched_path_correlation": _correlation_summary(matched_matrix),
        }

    primary_matrix = evolution_paths.pivot(
        index="utc_day", columns="candidate_id", values="primary_net"
    )
    matched_matrix = evolution_paths.pivot(
        index="utc_day", columns="candidate_id", values="matched_increment"
    )
    random_top_paths = _cohort_paths(paths, "random_train_top")
    original_top_paths = _cohort_paths(paths, "evolution_train_top")
    family_equal_paths = _family_reweighted_paths(paths)
    champion_rows = (
        evolution_top.sort_values(
            [
                "seed",
                "horizon_hours",
                "behavior_family_id",
                "search_reward",
                "candidate_id",
            ],
            ascending=[True, True, True, False, True],
            kind="stable",
        )
        .drop_duplicates(["seed", "horizon_hours", "behavior_family_id"])
    )
    champion_paths = _family_reweighted_paths(
        paths, champion_ids=set(champion_rows["candidate_id"].astype(str))
    )

    total = effects["pooled_effects"]["total_policy"]
    holdout = contract["holdout"]
    day_count = int(cohort_metrics["daily_path_row_count"].min())
    result = {
        "schema_version": 1,
        "audit_id": AUDIT_ID,
        "audit_role": "POST_HOC_READ_ONLY_EXISTING_LEDGER_NO_MARKET_EVALUATION",
        "authority_boundary": {
            "decision": "HOLD_RESEARCH",
            "policy_claim": "OOS_TOTAL_POLICY_DIRECTION_SUPPORTED",
            "alpha_claim": "NOT_ESTABLISHED",
            "optimizer_authority": "NON_FORMAL_UNCHANGED",
            "promotion": "FORBIDDEN_UNCHANGED",
            "new_search_or_holdout_read": "NOT_PERFORMED_AND_NOT_AUTHORIZED",
        },
        "input_integrity": {
            "source_sha": str(contract["source_sha"]),
            "selection_candidate_count": int(len(selection)),
            "evaluated_candidate_count": int(selection["oos_status"].eq("EVALUATED").sum()),
            "candidate_local_failure_count": int(
                selection["oos_status"].ne("EVALUATED").sum()
            ),
            "train_ledger_sha256": actual_train_hash,
            "oos_ledger_sha256": _sha256(required["oos_ledger"]),
            "oos_paths_sha256": _sha256(required["oos_paths"]),
            "official_checker_classification": str(checker["classification"]),
            "holdout": holdout,
        },
        "evidence_grade": {
            "paired_daily_observations": day_count,
            "grade": "WEAK",
            "rule": "fewer than 250 daily observations",
            "single_window": True,
            "window_start": str(holdout["start"]),
            "window_end_exclusive": str(holdout["end_exclusive"]),
        },
        "cohort_identity": cohort_identity,
        "absolute_cohort_economics": absolute_cohort_economics,
        "formal_total_policy_effect": {
            "primary_net": total["primary_net"],
            "matched_increment": total["matched_increment"],
        },
        "evolution_train_top_concentration": {
            "candidate_count": int(len(evolution_top)),
            "canonical_expression_count": int(
                evolution_top["canonical_expression_id"].nunique()
            ),
            "behavior_family_count": int(
                evolution_top["behavior_family_id"].nunique()
            ),
            "behavior_duplicate_rate": float(
                1.0
                - evolution_top["behavior_family_id"].nunique() / len(evolution_top)
            ),
            "mechanism_count": int(
                evolution_top["mechanism_template"].nunique()
            ),
            "mechanism_counts": {
                str(key): int(value)
                for key, value in evolution_top["mechanism_template"]
                .value_counts()
                .sort_index()
                .items()
            },
            "behavior_cells": family_cells,
            "mechanism_cells": mechanism_cells,
            "primary_path_correlation": _correlation_summary(primary_matrix),
            "matched_path_correlation": _correlation_summary(matched_matrix),
        },
        "mechanism_attribution": mechanism_attribution,
        "post_hoc_behavior_deduplication_sensitivity": {
            "original_candidate_weighting": _policy_sensitivity(
                original_top_paths, random_top_paths, label="original"
            ),
            "equal_behavior_family_weighting": _policy_sensitivity(
                family_equal_paths, random_top_paths, label="family_equal"
            ),
            "train_reward_champion_per_family": _policy_sensitivity(
                champion_paths, random_top_paths, label="train_champion"
            ),
        },
        "blocking_limitations": [
            "The 181-day single OOS window is WEAK under the audit rule and does not establish multi-regime stability.",
            "Evolution train-top contains 256 expressions but only 161 behavior families and a low correlation participation-ratio effective rank.",
            "FLOW_INTENSITY_CONVICTION appears only in seed 359914106, so its mechanism result is not seed replicated.",
            "The persisted OOS paths contain net, matched-increment, and control paths but no gross, turnover, cost-path, asset-weight, or venue-concentration paths; cost and concentration stress cannot be reconstructed without another market evaluation.",
            "The aligned observed-archive universe is dynamically eligible but not a survivorship-complete exchange universe.",
            "Mechanism and family reweighting results are post-hoc attribution only and cannot become a new qualification gate after the sealed read.",
        ],
        "required_next_action": "NO_NEW_SEARCH. Preserve policy-direction evidence and Alpha HOLD. Any future economic qualification requires separately authorized fresh data, preregistered family-deoverlap, absolute-zero benchmark, persisted OOS gross/turnover/cost/asset-weight paths, and multi-window evidence.",
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only V2.3 frozen-OOS policy attribution and bias audit."
    )
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build_audit(args.project_root)
    payload = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        output = args.output
        if not output.is_absolute():
            output = args.project_root / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
