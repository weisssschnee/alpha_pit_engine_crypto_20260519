from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import scripts.crypto_native_aggtrades_release as release


CONFIG = REPO / "config" / "crypto_native_aggtrades_benchmark_canary_v1.json"
RUN_ROOT = REPO / "runtime" / "mechanism_data_expansion0_20260712" / "native_aggtrades_benchmark_v1"
FROZEN = RUN_ROOT / "benchmark_frozen_manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_payload(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest().upper()


def repo_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()


def transform(frame: pd.DataFrame, spec: dict[str, Any]) -> pd.Series:
    group = frame.groupby(["symbol", "month"], sort=False, group_keys=False)
    field = spec["field"]
    operator = spec["operator"]
    value = pd.to_numeric(frame[field], errors="coerce")
    if operator == "LEVEL":
        return value
    if operator == "DELTA_1H":
        return group[field].diff()
    if operator == "ZSCORE_24H":
        mean = group[field].transform(lambda values: values.rolling(24, min_periods=12).mean())
        std = group[field].transform(lambda values: values.rolling(24, min_periods=12).std(ddof=0)).replace(0, np.nan)
        return (value - mean) / std
    if operator == "PERSISTENCE_4H":
        return group[field].transform(lambda values: np.sign(values).rolling(4, min_periods=4).mean())
    if operator == "TRANSITION":
        sign = np.sign(value)
        previous = group[field].shift(1)
        return sign.where(sign.ne(np.sign(previous)), 0.0)
    if operator == "DIVERGENCE":
        secondary = pd.to_numeric(frame[spec["secondary_field"]], errors="coerce")
        by_time = frame.assign(_a=value, _b=secondary).groupby("timestamp", sort=False)
        za = by_time["_a"].rank(pct=True) - 0.5
        zb = by_time["_b"].rank(pct=True) - 0.5
        return za - zb
    raise ValueError(f"unknown benchmark operator: {operator}")


def variant_values(base: pd.Series, frame: pd.DataFrame, variant: str, seed: int) -> pd.Series:
    if variant == "BASE":
        return base
    if variant == "SIGN_FLIP":
        return -base
    if variant == "WRONG_LAG_24H":
        temp = frame.assign(_value=base)
        return temp.groupby(["symbol", "month"], sort=False)["_value"].shift(24)
    if variant == "SHUFFLED_WITHIN_SYMBOL_MONTH":
        output = pd.Series(np.nan, index=frame.index, dtype=float)
        rng = np.random.default_rng(seed)
        for _, indices in frame.groupby(["symbol", "month"], sort=True).groups.items():
            values = base.loc[indices].to_numpy(copy=True)
            output.loc[indices] = values[rng.permutation(len(values))]
        return output
    if variant == "MATCHED_RANDOM":
        rng = np.random.default_rng(seed)
        output = pd.Series(rng.standard_normal(len(base)), index=base.index)
        return output.where(base.notna())
    raise ValueError(f"unknown variant: {variant}")


def cross_sectional_weights(values: pd.Series, frame: pd.DataFrame) -> pd.Series:
    temp = frame[["timestamp", "month"]].assign(_value=values)
    ranks = temp.groupby("timestamp", sort=False)["_value"].rank(pct=True, method="average") - 0.5
    denominator = ranks.abs().groupby(temp["timestamp"], sort=False).transform("sum").replace(0, np.nan)
    return (ranks / denominator).fillna(0.0)


def future_label(frame: pd.DataFrame, horizon: int, delay: int) -> pd.Series:
    output = pd.Series(np.nan, index=frame.index, dtype=float)
    for _, indices in frame.groupby(["symbol", "data_role"], sort=False).groups.items():
        block = frame.loc[indices, ["timestamp", "close_price"]].sort_values("timestamp", kind="mergesort")
        lookup = block.set_index("timestamp")["close_price"]
        start = lookup.reindex(block["timestamp"] + pd.Timedelta(hours=delay)).to_numpy()
        end = lookup.reindex(block["timestamp"] + pd.Timedelta(hours=delay + horizon)).to_numpy()
        values = np.log(end / start)
        output.loc[block.index] = values
    return output


def monthly_lcb(series: pd.Series, months: pd.Series) -> tuple[float, float, float, int]:
    monthly = series.groupby(months).mean().dropna()
    if monthly.empty:
        return float("nan"), float("nan"), float("nan"), 0
    mean = float(monthly.mean())
    se = float(monthly.std(ddof=1) / math.sqrt(len(monthly))) if len(monthly) > 1 else float("inf")
    lcb = mean - 1.645 * se
    return mean, lcb, float((monthly > 0).mean()), len(monthly)


def evaluate(weights: pd.Series, labels: pd.Series, frame: pd.DataFrame, cost_bps: float) -> dict[str, Any]:
    valid = labels.notna() & weights.notna()
    work = frame.loc[valid, ["timestamp", "month", "symbol"]].copy()
    work["weight"] = weights.loc[valid].to_numpy()
    work["label"] = labels.loc[valid].to_numpy()
    gross = work.assign(_gross=work.weight * work.label).groupby("timestamp", sort=True)["_gross"].sum()
    wide = work.pivot(index="timestamp", columns="symbol", values="weight").fillna(0.0).sort_index()
    month_by_time = work.drop_duplicates("timestamp").set_index("timestamp")["month"].reindex(wide.index)
    previous = wide.groupby(month_by_time, sort=False).shift(1).fillna(0.0)
    turnover = (wide - previous).abs().sum(axis=1)
    net = gross.reindex(wide.index).fillna(0.0) - turnover * cost_bps / 10_000.0
    gross_mean, gross_lcb, gross_positive, blocks = monthly_lcb(gross, month_by_time.reindex(gross.index))
    net_mean, net_lcb, net_positive, _ = monthly_lcb(net, month_by_time)
    return {
        "observations": int(len(net)), "months": blocks, "gross_mean": gross_mean, "gross_lcb": gross_lcb,
        "net_mean": net_mean, "net_lcb": net_lcb, "gross_positive_month_fraction": gross_positive,
        "net_positive_month_fraction": net_positive, "turnover_mean": float(turnover.mean()),
        "cost_drag_mean": float((turnover * cost_bps / 10_000.0).mean()),
    }


def load_panel(config: dict[str, Any]) -> pd.DataFrame:
    release_config = json.loads(release.CONFIG.read_text(encoding="utf-8"))
    release_root = Path(release_config["release_root"])
    coverage = pd.read_csv(release.RUN_ROOT / "coverage_ledger.csv")
    qualified = coverage[coverage.status.eq("QUALIFIED")]
    frames = []
    for row in qualified.sort_values(["data_role", "symbol", "month"], kind="mergesort").itertuples():
        feature_path = release_root / row.data_role.lower() / f"symbol={row.symbol}" / f"month={row.month}" / "part.parquet"
        feature = pd.read_parquet(feature_path)
        source = pd.read_parquet(row.source_path, columns=["timestamp", "close_price"])
        source["timestamp"] = pd.to_datetime(source["timestamp"], utc=True)
        merged = feature.merge(source, on="timestamp", how="left", validate="one_to_one")
        merged["data_role"] = row.data_role
        frames.append(merged)
    panel = pd.concat(frames, ignore_index=True).sort_values(["data_role", "symbol", "timestamp"], kind="mergesort").reset_index(drop=True)
    if panel.close_price.isna().any():
        raise ValueError("benchmark label price source missing")
    return panel


def freeze() -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    release_check = release.check()
    if release_check["content_sha256"] != config["release_content_sha256"]:
        raise ValueError("benchmark/release identity mismatch")
    expected = len(config["benchmarks"]) * len(config["variants"]) * len(config["horizons_hours"]) * len(config["roles"]) + len(config["horizons_hours"]) * len(config["roles"])
    if expected != config["fixed_evaluation_count"]:
        raise ValueError("fixed evaluation budget mismatch")
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "NATIVE_AGGTRADES_BENCHMARK_CANARY_DESIGN_FROZEN",
        "repo_sha": repo_sha(), "config_sha256": sha256_file(CONFIG),
        "release_content_sha256": release_check["content_sha256"], "release_output_files": release_check["output_files"],
        "fixed_evaluation_count": expected, "horizons_hours": config["horizons_hours"], "roles": config["roles"],
        "benchmarks": config["benchmarks"], "variants": config["variants"], "incumbent": config["incumbent"],
        "fixed_seed": config["fixed_seed"], "execution_delay_hours": config["execution_delay_hours"],
        "cost_bps_per_unit_turnover": config["cost_bps_per_unit_turnover"], "future_search_admission": config["future_search_admission"],
        "performance_started": False, "forward_read": False, "candidate_promotion": False, "memory_update": False,
        "complex_search_participation": False, "online_adjustment": False, "additional_budget": False,
    }
    payload["frozen_manifest_sha256"] = sha256_payload(payload)
    FROZEN.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def validate_frozen(config: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(FROZEN.read_text(encoding="utf-8"))
    recorded = payload.pop("frozen_manifest_sha256")
    if sha256_payload(payload) != recorded or payload["config_sha256"] != sha256_file(CONFIG):
        raise ValueError("benchmark frozen manifest drift")
    if payload["performance_started"] or payload["forward_read"] or payload["complex_search_participation"]:
        raise PermissionError("benchmark freeze records prohibited activity")
    if subprocess.run(["git", "merge-base", "--is-ancestor", payload["repo_sha"], "HEAD"], cwd=REPO).returncode:
        raise ValueError("benchmark implementation SHA is not an ancestor")
    payload["frozen_manifest_sha256"] = recorded
    return payload


def run() -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    frozen = validate_frozen(config)
    panel = load_panel(config)
    rows: list[dict[str, Any]] = []
    weight_sketches: dict[tuple[str, str], pd.Series] = {}
    all_specs = config["benchmarks"]
    incumbent = config["incumbent"]
    for role in config["roles"]:
        role_frame = panel[panel.data_role.eq(role)].copy().reset_index(drop=True)
        for horizon in config["horizons_hours"]:
            labels = future_label(role_frame, horizon, config["execution_delay_hours"])
            incumbent_base = transform(role_frame, incumbent)
            incumbent_weights = cross_sectional_weights(incumbent_base, role_frame)
            incumbent_metrics = evaluate(incumbent_weights, labels, role_frame, config["cost_bps_per_unit_turnover"])
            rows.append({"data_role": role, "benchmark_id": incumbent["benchmark_id"], "variant": "INCUMBENT", "horizon_hours": horizon, **incumbent_metrics})
            for ordinal, spec in enumerate(all_specs):
                base = transform(role_frame, spec)
                for variant in config["variants"]:
                    values = variant_values(base, role_frame, variant, config["fixed_seed"] + ordinal * 101 + horizon)
                    weights = cross_sectional_weights(values, role_frame)
                    metrics = evaluate(weights, labels, role_frame, config["cost_bps_per_unit_turnover"])
                    aligned = pd.concat([weights.rename("a"), incumbent_weights.rename("b")], axis=1).dropna()
                    correlation = float(aligned.corr(method="spearman").iloc[0, 1]) if len(aligned) > 2 else float("nan")
                    rows.append({"data_role": role, "benchmark_id": spec["benchmark_id"], "variant": variant, "horizon_hours": horizon,
                                 "operator": spec["operator"], "hypothesis": spec["hypothesis"], "weight_correlation_to_incumbent": correlation, **metrics})
                    if variant == "BASE":
                        weight_sketches[(role, f"{spec['benchmark_id']}__h{horizon}")] = weights
    results = pd.DataFrame(rows)
    if len(results) != config["fixed_evaluation_count"]:
        raise ValueError(f"evaluation count drift: {len(results)}")
    results.to_csv(RUN_ROOT / "benchmark_results.csv", index=False, lineterminator="\n")

    bases = results[results.variant.eq("BASE")].copy()
    controls = results[results.variant.isin(["WRONG_LAG_24H", "SHUFFLED_WITHIN_SYMBOL_MONTH", "MATCHED_RANDOM"])]
    decisions = []
    for spec in all_specs:
        benchmark_id = spec["benchmark_id"]
        for horizon in config["horizons_hours"]:
            dev = bases[(bases.benchmark_id.eq(benchmark_id)) & (bases.horizon_hours.eq(horizon)) & bases.data_role.eq("DEVELOPMENT")].iloc[0]
            challenge = bases[(bases.benchmark_id.eq(benchmark_id)) & (bases.horizon_hours.eq(horizon)) & bases.data_role.eq("CHALLENGE")].iloc[0]
            incumbent_dev = results[(results.benchmark_id.eq(incumbent["benchmark_id"])) & (results.horizon_hours.eq(horizon)) & results.data_role.eq("DEVELOPMENT")].iloc[0]
            incumbent_challenge = results[(results.benchmark_id.eq(incumbent["benchmark_id"])) & (results.horizon_hours.eq(horizon)) & results.data_role.eq("CHALLENGE")].iloc[0]
            relevant_controls = controls[(controls.benchmark_id.eq(benchmark_id)) & (controls.horizon_hours.eq(horizon))]
            controls_match = bool(np.isclose(relevant_controls.net_mean, dev.net_mean, rtol=0, atol=1e-12).any())
            increment_lcb = min(float(dev.net_lcb - incumbent_dev.net_lcb), float(challenge.net_lcb - incumbent_challenge.net_lcb))
            admit = bool(dev.gross_lcb > 0 and dev.net_lcb > 0 and challenge.net_lcb > 0 and increment_lcb > 0
                         and dev.net_positive_month_fraction >= config["future_search_admission"]["positive_month_fraction_min"]
                         and challenge.net_positive_month_fraction >= config["future_search_admission"]["positive_month_fraction_min"]
                         and not controls_match and abs(float(dev.weight_correlation_to_incumbent)) <= config["future_search_admission"]["max_abs_weight_correlation_to_incumbent"])
            decisions.append({"benchmark_id": benchmark_id, "horizon_hours": horizon, "development_gross_lcb": dev.gross_lcb,
                              "development_net_lcb": dev.net_lcb, "challenge_net_lcb": challenge.net_lcb,
                              "benchmark_increment_lcb": increment_lcb, "development_positive_month_fraction": dev.net_positive_month_fraction,
                              "challenge_positive_month_fraction": challenge.net_positive_month_fraction,
                              "weight_correlation_to_incumbent": dev.weight_correlation_to_incumbent,
                              "negative_controls_match_base": controls_match, "admit_for_future_search": admit})
    decision_frame = pd.DataFrame(decisions)
    decision_frame.to_csv(RUN_ROOT / "benchmark_decisions.csv", index=False, lineterminator="\n")

    weight_matrix = pd.DataFrame({name: series.reset_index(drop=True) for (_, name), series in weight_sketches.items() if _ == "DEVELOPMENT"})
    corr = weight_matrix.corr(method="spearman").fillna(0.0) if not weight_matrix.empty else pd.DataFrame()
    corr.to_csv(RUN_ROOT / "development_weight_correlations.csv", lineterminator="\n")
    eigenvalues = np.linalg.eigvalsh(corr.to_numpy()) if len(corr) else np.array([])
    neff = float((eigenvalues.sum() ** 2) / np.square(eigenvalues).sum()) if len(eigenvalues) and np.square(eigenvalues).sum() else 0.0
    admitted = decision_frame[decision_frame.admit_for_future_search]
    recommendation = "AUTHORIZE_NEW_MECHANISM_SEARCH_CANARY" if not admitted.empty else "PIVOT_TO_DIFFERENT_DATA_FAMILY"
    summary = {
        "status": "NATIVE_AGGTRADES_SIMPLE_BENCHMARK_CANARY_COMPLETED",
        "fixed_evaluations": len(results), "admitted_benchmark_horizons": len(admitted),
        "admitted": admitted[["benchmark_id", "horizon_hours"]].to_dict("records"),
        "behaviour_neff": neff, "recommendation": recommendation,
        "performance_scope": "NEW_PHYSICALLY_ISOLATED_DEVELOPMENT_AND_CHALLENGE_ONLY",
        "forward_read": False, "spent_evaluation_read": False, "candidate_promotion": False,
        "memory_update": False, "complex_search_participation": False, "additional_budget": False,
        "frozen_manifest_sha256": frozen["frozen_manifest_sha256"],
    }
    (RUN_ROOT / "benchmark_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Native aggTrades simple benchmark CANARY

Status: `{summary['status']}`

- Fixed evaluations: `{len(results)}`; online adjustment/additional budget: `false`.
- Admitted benchmark-horizons: `{len(admitted)}`.
- Behaviour N_eff across development base weight sketches: `{neff:.4f}`.
- Recommendation: `{recommendation}`.
- Only the new physically isolated development/challenge release was evaluated. No spent block, forward block, complex generator, promotion or memory participated.
"""
    (RUN_ROOT / "NATIVE_AGGTRADES_BENCHMARK_REPORT.md").write_text(report, encoding="utf-8")
    artifact_names = ["benchmark_frozen_manifest.json", "benchmark_results.csv", "benchmark_decisions.csv", "development_weight_correlations.csv", "benchmark_summary.json", "NATIVE_AGGTRADES_BENCHMARK_REPORT.md"]
    artifacts = [{"artifact": f"runtime/mechanism_data_expansion0_20260712/native_aggtrades_benchmark_v1/{name}", "sha256": sha256_file(RUN_ROOT / name), "role": "FIXED_SIMPLE_BENCHMARK_CANARY"} for name in artifact_names]
    pd.DataFrame(artifacts).to_csv(RUN_ROOT / "benchmark_artifact_index.csv", index=False, lineterminator="\n")
    return summary


def check() -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    frozen = validate_frozen(config)
    summary = json.loads((RUN_ROOT / "benchmark_summary.json").read_text(encoding="utf-8"))
    results = pd.read_csv(RUN_ROOT / "benchmark_results.csv")
    if len(results) != frozen["fixed_evaluation_count"] or summary["fixed_evaluations"] != len(results):
        raise ValueError("benchmark fixed budget drift")
    for flag in ("forward_read", "spent_evaluation_read", "candidate_promotion", "memory_update", "complex_search_participation", "additional_budget"):
        if summary.get(flag):
            raise PermissionError(f"benchmark records prohibited activity: {flag}")
    index = pd.read_csv(RUN_ROOT / "benchmark_artifact_index.csv")
    for row in index.itertuples():
        path = REPO / row.artifact
        if sha256_file(path) != row.sha256:
            raise ValueError(f"benchmark artifact drift: {row.artifact}")
    return {"status": "PASS_NATIVE_AGGTRADES_BENCHMARK_CHECK", "evaluations": len(results), "recommendation": summary["recommendation"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["freeze", "run", "check"])
    args = parser.parse_args()
    result = freeze() if args.command == "freeze" else run() if args.command == "run" else check()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
