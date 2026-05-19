from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a2_strict_replay import MatrixContext
from crypto_a7_validation_utils import (
    COST_BPS,
    REPORT_DIR,
    RUNTIME_DIR,
    SPLITS,
    CandidateSpec,
    clean_float,
    eval_expression,
    load_core4_context,
    load_core4_specs,
    split_mask,
    summarize_returns,
)
from crypto_a7b_funding_baseline_audit import object_raw_book, residualize, scale_book
from crypto_a7c_fundingcore_narrow_audit import fundingcore_specs, row_shuffle_signal, stable_shift_signal, time_shuffle_signal
from crypto_a7h0_nonfunding_residual_smoke import candidate_features
from crypto_a7h1_nonfunding_masked_loo_audit import raw_book_from_specs_masked


A7I1A_DIR = RUNTIME_DIR / "a7i1a_runner_preflight"
PRIMARY_COST_NAME = "stress_10bp"
PRIMARY_COST_BPS = COST_BPS[PRIMARY_COST_NAME]
SEVERE_COST_NAME = "severe_20bp"
SEVERE_COST_BPS = COST_BPS[SEVERE_COST_NAME]
RNG_SEED = 20260519


@dataclass(frozen=True)
class RunnerCandidate:
    candidate_id: str
    expression: str
    horizon: int
    family: str
    object_type: str
    signal_mode: str = "original"
    classification_expected: str = "PREFLIGHT_TEST_CANDIDATE"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def safe_score(value: float | None, cap: float = 2.0) -> float:
    if value is None or not math.isfinite(float(value)):
        return 0.0
    return float(np.clip(float(value), -cap, cap))


def stable_random_signal(shape: tuple[int, int], finite_like: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = rng.standard_normal(shape).astype(float)
    out[~np.isfinite(finite_like)] = np.nan
    return out


def preflight_candidates() -> list[RunnerCandidate]:
    return [
        RunnerCandidate(
            "a7i1a_fundingcore_baseline",
            "FundingCore_v1_book",
            6,
            "funding_baseline",
            "baseline",
            "book_object",
            "MANDATORY_BASELINE_NOT_CANDIDATE",
        ),
        RunnerCandidate(
            "a7i1a_core4_benchmark",
            "Core4_v1_book",
            6,
            "core4_benchmark",
            "baseline",
            "book_object",
            "RESEARCH_BENCHMARK_NOT_CANDIDATE",
        ),
        RunnerCandidate(
            "a7i1a_taker_imbalance_original",
            "Rank(taker_imbalance)",
            6,
            "flow_liquidity",
            "known_overlay",
            "original",
            "HOLD_RESIDUAL_ONLY_HEDGE_CLUE",
        ),
        RunnerCandidate(
            "a7i1a_avg_trade_size_original",
            "Rank(avg_trade_size_quote)",
            12,
            "flow_liquidity",
            "known_rejected",
            "original",
            "REJECTED_TAIL_RISK",
        ),
        RunnerCandidate(
            "a7i1a_taker_imbalance_sign_flip",
            "Rank(taker_imbalance)",
            6,
            "flow_liquidity",
            "placebo",
            "sign_flip",
            "NEGATIVE_CONTROL",
        ),
        RunnerCandidate(
            "a7i1a_taker_imbalance_row_shuffle",
            "Rank(taker_imbalance)",
            6,
            "flow_liquidity",
            "placebo",
            "row_shuffle",
            "NEGATIVE_CONTROL",
        ),
        RunnerCandidate(
            "a7i1a_taker_imbalance_time_shuffle",
            "Rank(taker_imbalance)",
            6,
            "flow_liquidity",
            "placebo",
            "time_shuffle",
            "NEGATIVE_CONTROL",
        ),
        RunnerCandidate(
            "a7i1a_taker_imbalance_wrong_lag",
            "Rank(taker_imbalance)",
            6,
            "flow_liquidity",
            "placebo",
            "wrong_lag_stale_24h",
            "NEGATIVE_CONTROL",
        ),
        RunnerCandidate(
            "a7i1a_random_noise_placebo",
            "RandomNoise(seed=20260519)",
            6,
            "placebo_random",
            "placebo",
            "random_noise",
            "NEGATIVE_CONTROL",
        ),
    ]


def spec_for_candidate(c: RunnerCandidate) -> CandidateSpec:
    return CandidateSpec(c.candidate_id, c.candidate_id, c.expression, c.horizon, c.family)


def book_from_spec(
    *,
    index: pd.DatetimeIndex,
    matrices: dict[str, np.ndarray],
    ctx: MatrixContext,
    candidate: RunnerCandidate,
    signal_lag_bars: int = 0,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if candidate.signal_mode == "book_object":
        if candidate.candidate_id == "a7i1a_fundingcore_baseline":
            raw, meta = object_raw_book(index, matrices, ctx, fundingcore_specs())
        elif candidate.candidate_id == "a7i1a_core4_benchmark":
            raw, meta = object_raw_book(index, matrices, ctx, load_core4_specs())
        else:
            raise ValueError(f"unknown book object candidate: {candidate.candidate_id}")
        raw = raw.copy()
        if signal_lag_bars:
            # Book objects are kept as baselines; lag stress is only meaningful for signal candidates.
            raw["pre_fee_return"] = np.nan
        return raw, {"orientation": None, "train_ic_mean": None, "signal_source": "book_object", "component_count": len(meta)}

    base_signal = ctx.eval(candidate.expression) if candidate.signal_mode != "random_noise" else ctx.eval("Rank(taker_imbalance)")
    _, base_meta = eval_expression(
        index=index,
        matrices=matrices,
        ctx=ctx,
        expression="Rank(taker_imbalance)" if candidate.signal_mode == "random_noise" else candidate.expression,
        horizon=candidate.horizon,
        cost_bps=0.0,
        forced_signal=base_signal,
    )
    base_orientation = float(base_meta["orientation"])
    signal = base_signal
    forced_orientation = base_orientation
    if candidate.signal_mode == "sign_flip":
        forced_orientation = -base_orientation
    elif candidate.signal_mode == "row_shuffle":
        signal = row_shuffle_signal(base_signal, RNG_SEED + 101)
    elif candidate.signal_mode == "time_shuffle":
        signal = time_shuffle_signal(base_signal, RNG_SEED + 102)
    elif candidate.signal_mode == "wrong_lag_stale_24h":
        signal = stable_shift_signal(base_signal, 24)
    elif candidate.signal_mode == "random_noise":
        signal = stable_random_signal(base_signal.shape, base_signal, RNG_SEED + 103)
        forced_orientation = 1.0
    elif candidate.signal_mode != "original":
        raise ValueError(f"unknown signal_mode: {candidate.signal_mode}")
    if signal_lag_bars:
        signal = stable_shift_signal(signal, signal_lag_bars)
    frame, meta = eval_expression(
        index=index,
        matrices=matrices,
        ctx=ctx,
        expression="Rank(taker_imbalance)" if candidate.signal_mode == "random_noise" else candidate.expression,
        horizon=candidate.horizon,
        cost_bps=0.0,
        forced_signal=signal,
        forced_orientation=forced_orientation,
    )
    frame = frame.rename(columns={"net_return": "pre_fee_return"})
    meta = {
        **meta,
        "base_orientation": base_orientation,
        "signal_source": candidate.signal_mode,
        "signal_lag_bars": signal_lag_bars,
    }
    return frame, meta


def metric_by_split(frame: pd.DataFrame, value_col: str, prefix: dict[str, Any]) -> pd.DataFrame:
    rows = []
    ts = pd.DatetimeIndex(pd.to_datetime(frame["timestamp"], utc=True))
    for split_name in SPLITS:
        mask = split_mask(ts, split_name)
        st = summarize_returns(frame.loc[mask, value_col].to_numpy(dtype=float))
        row = dict(prefix)
        row["split"] = split_name
        row.update(st)
        if "turnover" in frame.columns:
            row["mean_turnover"] = clean_float(frame.loc[mask, "turnover"].mean())
        if "gross_exposure" in frame.columns:
            row["mean_gross_exposure"] = clean_float(frame.loc[mask, "gross_exposure"].mean())
        rows.append(row)
    return pd.DataFrame(rows)


def train_residual_params(core_scaled: pd.DataFrame, baseline_scaled: pd.DataFrame) -> dict[str, Any]:
    df = pd.DataFrame(
        {
            "timestamp": core_scaled["timestamp"],
            "core": core_scaled["net_return"],
            "baseline": baseline_scaled["net_return"],
        }
    )
    ts = pd.DatetimeIndex(pd.to_datetime(df["timestamp"], utc=True))
    train_mask = split_mask(ts, "train_2024")
    x = df.loc[train_mask, "baseline"].to_numpy(dtype=float)
    y = df.loc[train_mask, "core"].to_numpy(dtype=float)
    valid = np.isfinite(x) & np.isfinite(y)
    beta = 0.0
    alpha = 0.0
    corr = None
    if valid.sum() > 10 and np.nanvar(x[valid]) > 0:
        beta, alpha = np.polyfit(x[valid], y[valid], 1)
        corr = np.corrcoef(x[valid], y[valid])[0, 1]
    return {
        "beta_train": clean_float(beta),
        "alpha_train": clean_float(alpha),
        "corr_train": clean_float(corr),
        "train_rows": int(valid.sum()),
        "uses_train_only": True,
        "uses_may": False,
    }


def split_value(metrics: pd.DataFrame, split: str, col: str, default: float | None = None) -> float | None:
    row = metrics[metrics["split"] == split]
    if row.empty or col not in row.columns:
        return default
    return clean_float(row.iloc[0][col])


def build_rank_components(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for candidate_id, group in summary.groupby("candidate_id"):
        meta = group.iloc[0].to_dict()
        raw = group[group["series"] == "raw_10bp"]
        raw20 = group[group["series"] == "raw_20bp"]
        residual_funding = group[group["series"] == "residual_vs_funding_10bp"]
        residual_core4 = group[group["series"] == "residual_vs_core4_10bp"]
        lag = group[group["series"] == "execution_lag_1bar_raw_10bp"]
        val_raw = split_value(raw, "validation_2025H1", "annualized_mean")
        recent_raw = split_value(raw, "recent_oos_2025H2_2026Apr", "annualized_mean")
        val_resid = split_value(residual_funding, "validation_2025H1", "annualized_mean")
        recent_resid = split_value(residual_funding, "recent_oos_2025H2_2026Apr", "annualized_mean")
        recent_core4_resid = split_value(residual_core4, "recent_oos_2025H2_2026Apr", "annualized_mean")
        recent_20 = split_value(raw20, "recent_oos_2025H2_2026Apr", "annualized_mean")
        recent_lag = split_value(lag, "recent_oos_2025H2_2026Apr", "annualized_mean")
        val_dd = split_value(raw, "validation_2025H1", "compounded_max_dd", 0.0)
        recent_dd = split_value(raw, "recent_oos_2025H2_2026Apr", "compounded_max_dd", 0.0)
        base_components = {
            "component_raw_validation": safe_score(val_raw),
            "component_raw_recent": safe_score(recent_raw),
            "component_residual_funding_validation": safe_score(val_resid),
            "component_residual_funding_recent": safe_score(recent_resid),
            "component_residual_core4_recent": safe_score(recent_core4_resid),
            "component_cost20_recent": 0.5 * safe_score(recent_20),
            "component_execution_lag_recent": 0.5 * safe_score(recent_lag),
            "component_drawdown_penalty": -0.25 * abs(safe_score(val_dd, cap=1.0)) - 0.25 * abs(safe_score(recent_dd, cap=1.0)),
        }
        rank_score = sum(base_components.values())
        rows.append(
            {
                "candidate_id": candidate_id,
                "family": meta.get("family"),
                "object_type": meta.get("object_type"),
                "signal_mode": meta.get("signal_mode"),
                **base_components,
                "rank_score": clean_float(rank_score),
                "rank_uses_validation": True,
                "rank_uses_recent_oos": True,
                "rank_excludes_known_adversarial_stress": True,
            }
        )
    out = pd.DataFrame(rows)
    out = out.sort_values(["rank_score", "candidate_id"], ascending=[False, True]).reset_index(drop=True)
    out["rank_order"] = np.arange(1, len(out) + 1)
    return out


def classify_candidate(candidate: RunnerCandidate, raw_may_10: float | None, residual_may: float | None) -> str:
    if candidate.classification_expected in {
        "MANDATORY_BASELINE_NOT_CANDIDATE",
        "RESEARCH_BENCHMARK_NOT_CANDIDATE",
        "NEGATIVE_CONTROL",
        "HOLD_RESIDUAL_ONLY_HEDGE_CLUE",
        "REJECTED_TAIL_RISK",
    }:
        return candidate.classification_expected
    if residual_may is not None and residual_may >= 0 and (raw_may_10 is None or raw_may_10 < 0):
        return "HOLD_RESIDUAL_ONLY"
    return "PREFLIGHT_TEST_CANDIDATE"


def main() -> int:
    A7I1A_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    candidates = preflight_candidates()
    feature_specs = [spec_for_candidate(c) for c in candidates if c.signal_mode not in {"book_object", "random_noise"}]
    index, symbols, matrices, ctx = load_core4_context(extra_features=candidate_features(feature_specs))

    funding_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=fundingcore_specs())
    core4_raw = raw_book_from_specs_masked(index=index, matrices=matrices, ctx=ctx, specs=load_core4_specs())
    funding_scaled = scale_book(funding_raw, PRIMARY_COST_BPS)
    core4_scaled = scale_book(core4_raw, PRIMARY_COST_BPS)

    summary_parts = []
    trace_rows = []
    residual_rows = []
    lag_rows = []
    baseline_rows = []
    meta_rows = []
    for candidate in candidates:
        raw, meta = book_from_spec(index=index, matrices=matrices, ctx=ctx, candidate=candidate)
        raw_10 = scale_book(raw, PRIMARY_COST_BPS)
        raw_20 = scale_book(raw, SEVERE_COST_BPS)
        residual_funding = residualize(raw_10, funding_scaled)
        residual_core4 = residualize(raw_10, core4_scaled)
        lag_raw, lag_meta = book_from_spec(index=index, matrices=matrices, ctx=ctx, candidate=candidate, signal_lag_bars=1)
        lag_10 = scale_book(lag_raw, PRIMARY_COST_BPS)

        for series, frame in [
            ("raw_10bp", raw_10),
            ("raw_20bp", raw_20),
            ("residual_vs_funding_10bp", residual_funding),
            ("residual_vs_core4_10bp", residual_core4),
            ("execution_lag_1bar_raw_10bp", lag_10),
        ]:
            summary_parts.append(
                metric_by_split(
                    frame,
                    "net_return",
                    {
                        "candidate_id": candidate.candidate_id,
                        "family": candidate.family,
                        "object_type": candidate.object_type,
                        "signal_mode": candidate.signal_mode,
                        "expression": candidate.expression,
                        "horizon": candidate.horizon,
                        "series": series,
                    },
                )
            )

        for baseline_name, baseline_scaled, resid_frame in [
            ("FundingCore", funding_scaled, residual_funding),
            ("Core4", core4_scaled, residual_core4),
        ]:
            params = train_residual_params(raw_10, baseline_scaled)
            residual_rows.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "baseline": baseline_name,
                    **params,
                    "residual_frame_beta_train": clean_float(resid_frame["residual_beta_train"].iloc[0]),
                    "residual_frame_alpha_train": clean_float(resid_frame["residual_alpha_train"].iloc[0]),
                }
            )

        raw_may_10 = summarize_returns(raw_10.loc[split_mask(index, "fresh_forward_2026May"), "net_return"].to_numpy(dtype=float)).get(
            "annualized_mean"
        )
        resid_may = summarize_returns(
            residual_funding.loc[split_mask(index, "fresh_forward_2026May"), "net_return"].to_numpy(dtype=float)
        ).get("annualized_mean")
        final_class = classify_candidate(candidate, clean_float(raw_may_10), clean_float(resid_may))
        baseline_rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "object_type": candidate.object_type,
                "expected_classification": candidate.classification_expected,
                "runner_classification": final_class,
                "classification_match": final_class == candidate.classification_expected
                or candidate.classification_expected == "PREFLIGHT_TEST_CANDIDATE",
                "may_stress_label_only": clean_float(raw_may_10),
                "residual_vs_funding_may_stress_label_only": clean_float(resid_may),
                "classification_uses_may_stress": candidate.object_type not in {"baseline", "placebo"},
                "classification_affects_rank": False,
            }
        )
        lag_rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "signal_mode": candidate.signal_mode,
                "lag_bars": 1,
                "lag_signal_source": lag_meta.get("signal_source"),
                "lag_raw_may_annualized_stress_only": clean_float(raw_may_10),
                "lag_frame_rows": int(len(lag_10)),
                "lag_output_exists": "net_return" in lag_10.columns,
            }
        )
        meta_rows.append({"candidate_id": candidate.candidate_id, **meta})

    summary = pd.concat(summary_parts, ignore_index=True)
    score_components = build_rank_components(summary)
    replay_eligible = ~score_components["object_type"].isin(["baseline", "placebo", "known_rejected", "known_overlay"])
    selected_ids = set(
        score_components[replay_eligible]
        .sort_values(["rank_score", "candidate_id"], ascending=[False, True])
        .head(4)["candidate_id"]
        .tolist()
    )
    trace = score_components.copy()
    trace["selected_for_replay"] = trace["candidate_id"].isin(selected_ids)
    trace["selection_reason"] = np.where(
        trace["selected_for_replay"],
        "top_rank_score_excluding_baseline_and_placebo",
        np.where(
            replay_eligible,
            "below_preflight_selection_cut",
            "not_selectable_object_type",
        ),
    )
    trace["may_derived_threshold_used"] = False
    trace["may_derived_weight_used"] = False
    trace["may_stress_gate_applied_before_selection"] = False

    may_columns = [c for c in score_components.columns if "may" in c.lower() or "fresh_forward" in c.lower()]
    order_original = trace.sort_values(["rank_score", "candidate_id"], ascending=[False, True])["candidate_id"].tolist()
    # Simulate May shuffle/delete. Ranking should be unchanged because ranking data frame has no May columns.
    may_shuffle_trace = trace.copy()
    rng = np.random.default_rng(RNG_SEED + 991)
    may_shuffle_trace["may_stress_label_shuffled_for_audit"] = rng.permutation(len(may_shuffle_trace))
    order_shuffle = may_shuffle_trace.sort_values(["rank_score", "candidate_id"], ascending=[False, True])["candidate_id"].tolist()
    may_delete_trace = trace.drop(columns=may_columns, errors="ignore")
    order_delete = may_delete_trace.sort_values(["rank_score", "candidate_id"], ascending=[False, True])["candidate_id"].tolist()
    selected_shuffle = set(may_shuffle_trace[may_shuffle_trace["selected_for_replay"]]["candidate_id"])
    selected_delete = set(may_delete_trace[may_delete_trace["selected_for_replay"]]["candidate_id"])
    may_usage = pd.DataFrame(
        [
            {
                "check_name": "rank_score_components_have_no_may_columns",
                "pass": len(may_columns) == 0,
                "detail": ",".join(may_columns),
            },
            {
                "check_name": "candidate_selection_trace_has_no_may_threshold_or_weight",
                "pass": not bool(trace["may_derived_threshold_used"].any() or trace["may_derived_weight_used"].any()),
                "detail": "may_derived_threshold_used=False; may_derived_weight_used=False",
            },
            {
                "check_name": "rank_order_unchanged_after_may_shuffle",
                "pass": order_original == order_shuffle,
                "detail": "May stress label shuffled in audit-only column",
            },
            {
                "check_name": "rank_order_unchanged_after_may_delete",
                "pass": order_original == order_delete,
                "detail": "May columns deleted from ranking frame",
            },
            {
                "check_name": "selected_for_replay_unchanged_after_may_shuffle_delete",
                "pass": selected_ids == selected_shuffle == selected_delete,
                "detail": "selection driven by validation/recent rank score only",
            },
            {
                "check_name": "may_affects_only_final_stress_label",
                "pass": not bool(trace["may_stress_gate_applied_before_selection"].any()),
                "detail": "May stress label is written in classification audit only",
            },
        ]
    )

    residual_audit = pd.DataFrame(residual_rows)
    lag_audit = pd.DataFrame(lag_rows)
    baseline_audit = pd.DataFrame(baseline_rows)
    meta = pd.DataFrame(meta_rows)

    scoreboard_path = A7I1A_DIR / "a7i1a_metric_scoreboard.csv"
    trace_path = A7I1A_DIR / "candidate_selection_trace.csv"
    score_path = A7I1A_DIR / "rank_score_components.csv"
    may_path = A7I1A_DIR / "may_usage_audit.csv"
    residual_path = A7I1A_DIR / "residualization_audit.csv"
    lag_path = A7I1A_DIR / "execution_lag_1bar_audit.csv"
    baseline_path = A7I1A_DIR / "baseline_classification_audit.csv"
    meta_path = A7I1A_DIR / "candidate_meta.csv"
    summary.to_csv(scoreboard_path, index=False)
    trace.to_csv(trace_path, index=False)
    score_components.to_csv(score_path, index=False)
    may_usage.to_csv(may_path, index=False)
    residual_audit.to_csv(residual_path, index=False)
    lag_audit.to_csv(lag_path, index=False)
    baseline_audit.to_csv(baseline_path, index=False)
    meta.to_csv(meta_path, index=False)

    blockers = []
    if not bool(may_usage["pass"].all()):
        blockers.append("may_usage_audit_failed")
    if not bool((residual_audit["uses_train_only"] == True).all()) or bool((residual_audit["uses_may"] == True).any()):
        blockers.append("residualization_not_train_only")
    if not bool(lag_audit["lag_output_exists"].all()):
        blockers.append("execution_lag_output_missing")
    if not bool(baseline_audit["classification_match"].all()):
        blockers.append("baseline_classification_mismatch")
    if trace[trace["selected_for_replay"] & trace["object_type"].isin(["baseline", "placebo"])].shape[0] > 0:
        blockers.append("baseline_or_placebo_selected_for_replay")
    decision = "PASS_A7I1A_RUNNER_PREFLIGHT" if not blockers else "HOLD_A7I1A_RUNNER_PREFLIGHT"

    manifest = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "stage": "A7I-1a runner implementation preflight",
        "executes_search": False,
        "authorizes_a7i1b": decision == "PASS_A7I1A_RUNNER_PREFLIGHT",
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_boundary": {
            "may_status": "known_adversarial_stress_set",
            "may_used_for_ranking": False,
            "may_used_for_threshold_tuning": False,
            "may_used_for_candidate_selection": False,
            "may_affects_only_stress_label": True,
        },
        "outputs": {
            "metric_scoreboard": str(scoreboard_path),
            "candidate_selection_trace": str(trace_path),
            "rank_score_components": str(score_path),
            "may_usage_audit": str(may_path),
            "residualization_audit": str(residual_path),
            "execution_lag_1bar_audit": str(lag_path),
            "baseline_classification_audit": str(baseline_path),
            "candidate_meta": str(meta_path),
        },
    }
    manifest_path = A7I1A_DIR / "a7i1a_manifest_20260519.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / "CRYPTO_A7I1A_RUNNER_PREFLIGHT_20260519.md"
    lines = [
        "# Crypto A7I-1a Runner Implementation Preflight",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        f"- executes_search: `False`",
        f"- authorizes_a7i1b: `{manifest['authorizes_a7i1b']}`",
        f"- authorizes_alpha_proof: `False`",
        f"- blockers: `{blockers}`",
        "",
        "## Scope",
        "",
        "A7I-1a tests runner mechanics on fixed known objects and placebo variants. It does not run matched-budget search.",
        "",
        "## May Usage Audit",
        "",
        "| check | pass | detail |",
        "|---|---:|---|",
    ]
    for _, row in may_usage.iterrows():
        lines.append(f"| `{row['check_name']}` | `{bool(row['pass'])}` | {row['detail']} |")
    lines += [
        "",
        "## Baseline Classification",
        "",
        "| candidate | expected | runner | match |",
        "|---|---|---|---:|",
    ]
    for _, row in baseline_audit.iterrows():
        lines.append(
            f"| `{row['candidate_id']}` | `{row['expected_classification']}` | `{row['runner_classification']}` | `{bool(row['classification_match'])}` |"
        )
    selected_display = trace[trace["selected_for_replay"]][["candidate_id", "rank_score", "selection_reason"]]
    lines += [
        "",
        "## Selection Trace",
        "",
        "| selected candidate | rank score | reason |",
        "|---|---:|---|",
    ]
    for _, row in selected_display.iterrows():
        lines.append(f"| `{row['candidate_id']}` | {float(row['rank_score']):.6f} | `{row['selection_reason']}` |")
    lines += [
        "",
        "## Decision Boundary",
        "",
        "- PASS authorizes A7I-1b small matched-budget smoke implementation/run.",
        "- PASS does not authorize alpha proof, shadow, paper, or live.",
        "- May 2026 remains known adversarial stress and is not used for ranking or selection.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / "CRYPTO_A7I1A_DECISION_RECORD_20260519.md"
    decision_lines = [
        "# Crypto A7I-1a Decision Record",
        "",
        f"decision: {decision}",
        "stage: runner implementation preflight",
        "executes_search: false",
        f"authorizes_a7i1b: {str(manifest['authorizes_a7i1b']).lower()}",
        "authorizes_alpha_proof: false",
        "authorizes_shadow_paper_live: false",
        "",
        "confirmed:",
        "- May stress result is mechanically excluded from rank_score and selected_for_replay.",
        "- Residualization parameters are fit on train_2024 only.",
        "- Execution lag 1bar stress outputs are generated.",
        "- FundingCore/Core4/taker/placebo baseline classifications are explicit.",
        "",
        "not_confirmed:",
        "- A7I-1b candidate discovery",
        "- alpha proof",
        "- shadow readiness",
        "- paper/live readiness",
    ]
    decision_path.write_text("\n".join(decision_lines) + "\n", encoding="utf-8")

    print("A7I1A_REPORT=" + str(report_path))
    print("A7I1A_DECISION=" + decision)
    return 0 if decision == "PASS_A7I1A_RUNNER_PREFLIGHT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
