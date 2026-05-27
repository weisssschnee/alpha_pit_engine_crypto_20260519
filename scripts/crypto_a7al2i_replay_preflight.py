from __future__ import annotations

import gc
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra


DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
BASE_DIR = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v2_20260527"
SPLIT_COVERAGE = REPO / "runtime" / "a7al0_top498_alpha_search_contract" / "a7al_split_coverage_by_symbol.csv"
SELECTED = REPO / "runtime" / "a7al2h_selector_repair" / "a7al2h_selected_control_gated_candidates.csv"
OUT_DIR = REPO / "runtime" / "a7al2i_replay_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7AL2I_REPLAY_PREFLIGHT_20260527.md"

PRIMARY_LABEL = "fwd_ret_24h"
MIN_ACTIVE_SYMBOLS = 30
SPLIT_ORDER = [
    "train_2024",
    "validation_2025H1",
    "test_2025H2",
    "recent_oos_2026JanApr",
    "known_may2026_stress",
]
SPLIT_END = {
    "train_2024": pd.Timestamp("2024-12-31 23:00:00+00:00"),
    "validation_2025H1": pd.Timestamp("2025-06-30 23:00:00+00:00"),
    "test_2025H2": pd.Timestamp("2025-12-31 23:00:00+00:00"),
    "recent_oos_2026JanApr": pd.Timestamp("2026-04-30 23:00:00+00:00"),
    "known_may2026_stress": pd.Timestamp("2026-05-26 00:00:00+00:00"),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def strict_symbols() -> list[str]:
    cov = pd.read_csv(SPLIT_COVERAGE)
    symbols = (
        cov.loc[cov["search_eligibility"].eq("strict_full_history"), "symbol"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .tolist()
    )
    return symbols


def fields_from_selected(selected: pd.DataFrame) -> set[str]:
    fields: set[str] = {"trade_close"}
    for text in selected["fields"].dropna().astype(str):
        fields.update(part for part in text.split("|") if part)
    return fields


def load_frame(symbols: list[str], fields: set[str]) -> pd.DataFrame:
    columns = ["timestamp"] + sorted(fields)
    frames: list[pd.DataFrame] = []
    for symbol in symbols:
        path = BASE_DIR / f"symbol={symbol}" / "part.parquet"
        if not path.exists():
            continue
        frame = pd.read_parquet(path, columns=[c for c in columns if c != "symbol"], engine="pyarrow")
        frame["symbol"] = symbol
        frames.append(frame)
    if not frames:
        raise RuntimeError("no strict symbols loaded from base v2")
    out = pd.concat(frames, ignore_index=True)
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out = out.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    out["split"] = np.select(
        [
            out["timestamp"].le(SPLIT_END["train_2024"]),
            out["timestamp"].le(SPLIT_END["validation_2025H1"]),
            out["timestamp"].le(SPLIT_END["test_2025H2"]),
            out["timestamp"].le(SPLIT_END["recent_oos_2026JanApr"]),
            out["timestamp"].le(SPLIT_END["known_may2026_stress"]),
        ],
        SPLIT_ORDER,
        default="out_of_scope",
    )
    close = pd.to_numeric(out["trade_close"], errors="coerce")
    log_close = np.log(close.where(close > 0))
    out[PRIMARY_LABEL] = log_close.groupby(out["symbol"], sort=False).shift(-24) - log_close
    label_end = out["timestamp"] + pd.Timedelta(hours=24)
    split_end = out["split"].map(SPLIT_END)
    out.loc[label_end > split_end, PRIMARY_LABEL] = np.nan
    return out


def tstat(values: pd.Series) -> float:
    x = pd.to_numeric(values, errors="coerce").dropna()
    if len(x) < 3:
        return np.nan
    std = x.std(ddof=1)
    if not np.isfinite(std) or std == 0:
        return np.nan
    return float(x.mean() / std * math.sqrt(len(x)))


def timestamp_spread(frame: pd.DataFrame, signal: pd.Series) -> tuple[pd.DataFrame, dict[str, Any]]:
    work = pd.DataFrame(
        {
            "timestamp": frame["timestamp"],
            "split": frame["split"],
            "symbol": frame["symbol"],
            "signal": pd.to_numeric(signal, errors="coerce"),
            "label": pd.to_numeric(frame[PRIMARY_LABEL], errors="coerce"),
        }
    ).replace([np.inf, -np.inf], np.nan)
    work = work.dropna(subset=["signal", "label"])
    valid_rows = int(len(work))
    if valid_rows == 0:
        return pd.DataFrame(), {"valid_rows": 0, "valid_row_share": 0.0}
    keys = ["split", "timestamp"]
    counts = work.groupby(keys, observed=True)["signal"].transform("count")
    work = work[counts >= MIN_ACTIVE_SYMBOLS].copy()
    if work.empty:
        return pd.DataFrame(), {"valid_rows": valid_rows, "valid_row_share": float(valid_rows / len(frame))}
    work["rank_pct"] = work.groupby(keys, observed=True)["signal"].rank(pct=True, method="average")
    top = work[work["rank_pct"] >= 0.9].groupby(keys, observed=True)["label"].mean()
    bottom = work[work["rank_pct"] <= 0.1].groupby(keys, observed=True)["label"].mean()
    nobs = work.groupby(keys, observed=True)["symbol"].count()
    out = pd.concat([top.rename("top_ret"), bottom.rename("bottom_ret"), nobs.rename("n_obs")], axis=1).dropna()
    out["spread"] = out["top_ret"] - out["bottom_ret"]
    return out.reset_index(), {"valid_rows": valid_rows, "valid_row_share": float(valid_rows / len(frame))}


def summarize(candidate_id: str, variant: str, ts: pd.DataFrame, coverage: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for split in SPLIT_ORDER:
        g = ts[ts["split"].eq(split)] if not ts.empty and "split" in ts.columns else pd.DataFrame()
        rows.append(
            {
                "candidate_id": candidate_id,
                "variant": variant,
                "split": split,
                "n_dates": int(g["timestamp"].nunique()) if not g.empty else 0,
                "avg_n_obs": float(g["n_obs"].mean()) if not g.empty else np.nan,
                "valid_rows": int(coverage.get("valid_rows", 0)),
                "valid_row_share": float(coverage.get("valid_row_share", 0.0)),
                "mean_spread_24h": float(g["spread"].mean()) if not g.empty else np.nan,
                "spread_tstat": tstat(g["spread"]) if not g.empty else np.nan,
                "positive_spread_rate": float((g["spread"] > 0).mean()) if not g.empty else np.nan,
            }
        )
    return rows


def used_fields(row: pd.Series) -> list[str]:
    return [part for part in str(row["fields"]).split("|") if part]


def eval_expression(frame: pd.DataFrame, expression: str, fields: list[str]) -> pd.Series:
    evaluator = CryptoFeatureAlgebra(frame[["symbol", "timestamp"] + sorted(set(fields))].copy(), set(fields))
    return evaluator.evaluate(expression).values


def shifted_frame(frame: pd.DataFrame, fields: list[str], periods: int) -> pd.DataFrame:
    out = frame[["symbol", "timestamp"] + sorted(set(fields))].copy()
    for field in sorted(set(fields)):
        out[field] = pd.to_numeric(out[field], errors="coerce").groupby(out["symbol"], sort=False).shift(periods)
    return out


def classify_candidate(metrics: pd.DataFrame, candidate_id: str) -> dict[str, Any]:
    pivot = metrics[metrics["candidate_id"].eq(candidate_id)].pivot_table(
        index="variant", columns="split", values="mean_spread_24h", aggfunc="first"
    )
    def v(variant: str, split: str) -> float:
        try:
            return float(pivot.loc[variant, split])
        except Exception:
            return np.nan

    original = [v("original", s) for s in ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]]
    finite_original = [x for x in original if np.isfinite(x) and abs(x) > 1e-8]
    sign_stable = len(finite_original) == 3 and len({np.sign(x) for x in finite_original}) == 1
    min_abs = min(abs(x) for x in finite_original) if finite_original else 0.0
    lag_recent = v("one_bar_lag", "recent_oos_2026JanApr")
    recent = v("original", "recent_oos_2026JanApr")
    lag_ok = np.isfinite(lag_recent) and np.isfinite(recent) and np.sign(lag_recent) == np.sign(recent) and abs(lag_recent) >= 0.35 * abs(recent)
    control_variants = ["wrong_lag_future_24h", "wrong_lag_stale_168h", "time_shuffle", "symbol_shuffle", "same_family_random"]
    control_ratios = []
    for split in ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]:
        control_max = np.nanmax([abs(v(c, split)) for c in control_variants])
        original_val = abs(v("original", split))
        if np.isfinite(control_max) and np.isfinite(original_val) and original_val > 0:
            control_ratios.append(float(control_max / original_val))
    control_dominance_ratio = max(control_ratios) if control_ratios else np.nan
    may = v("original", "known_may2026_stress")
    if not sign_stable:
        decision = "HOLD_A7AL2I_UNSTABLE_PRE_MAY"
    elif not lag_ok:
        decision = "HOLD_A7AL2I_ONE_BAR_LAG_FRAGILE"
    elif np.isfinite(control_dominance_ratio) and control_dominance_ratio >= 1.15:
        decision = "HOLD_A7AL2I_CONTROL_DOMINATED"
    elif min_abs < 0.0002:
        decision = "HOLD_A7AL2I_TOO_WEAK"
    else:
        decision = "A7AL2I_REPLAY_PREFLIGHT_CLUE"
    return {
        "candidate_id": candidate_id,
        "original_validation_spread": v("original", "validation_2025H1"),
        "original_test_spread": v("original", "test_2025H2"),
        "original_recent_spread": recent,
        "original_may_stress_spread": may,
        "one_bar_lag_recent_spread": lag_recent,
        "control_dominance_ratio_premay_max": control_dominance_ratio,
        "sign_stable_pre_may": sign_stable,
        "lag_ok": lag_ok,
        "min_abs_premay_spread": min_abs,
        "decision": decision,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    selected = pd.read_csv(SELECTED)
    ar4 = pd.read_csv(REPO / "runtime" / "a7ar4_selector_adapter_smoke" / "a7ar4_selection_trace.csv", usecols=["candidate_id", "expression"])
    selected = selected.merge(ar4, on="candidate_id", how="left")
    symbols = strict_symbols()
    if __import__("os").environ.get("A7AL2I_REUSE_METRICS") == "1" and (OUT_DIR / "a7al2i_candidate_variant_metrics.csv").exists():
        metrics = pd.read_csv(OUT_DIR / "a7al2i_candidate_variant_metrics.csv")
        frame_rows = int(metrics["valid_rows"].max()) if "valid_rows" in metrics else 0
        trace_rows: list[dict[str, Any]] = []
    else:
        fields = fields_from_selected(selected)
        frame = load_frame(symbols, fields)
        frame_rows = int(len(frame))
        rng = np.random.default_rng(20260527)

        metric_rows: list[dict[str, Any]] = []
        trace_rows = []
        for i, row in selected.iterrows():
            candidate_id = str(row["candidate_id"])
            expression = str(row["expression"]) if "expression" in row else ""
            if not expression or expression == "nan":
                raise RuntimeError(f"missing expression for {candidate_id}")
            fields_i = used_fields(row)
            print(f"[A7AL-2I] {i+1}/{len(selected)} {candidate_id}", flush=True)
            base_signal = eval_expression(frame, expression, fields_i)
            variants: dict[str, pd.Series] = {
                "original": base_signal,
                "one_bar_lag": base_signal.groupby(frame["symbol"], sort=False).shift(1),
                "time_shuffle": base_signal.sample(frac=1.0, random_state=20260527 + i).reset_index(drop=True).set_axis(base_signal.index),
                "symbol_shuffle": base_signal.groupby(frame["timestamp"], sort=False).transform(lambda s: pd.Series(rng.permutation(s.to_numpy()), index=s.index)),
                "same_family_random": pd.Series(rng.normal(size=len(frame)), index=frame.index),
            }
            for variant, periods in [("wrong_lag_future_24h", -24), ("wrong_lag_stale_168h", 168)]:
                ctrl_frame = shifted_frame(frame, fields_i, periods)
                variants[variant] = eval_expression(ctrl_frame, expression, fields_i)
                del ctrl_frame
                gc.collect()
            for variant, signal in variants.items():
                ts, coverage = timestamp_spread(frame, signal)
                metric_rows.extend(summarize(candidate_id, variant, ts, coverage))
                if variant in {"original", "one_bar_lag", "wrong_lag_future_24h", "wrong_lag_stale_168h"}:
                    for _, r in ts.head(120).iterrows():
                        trace_rows.append(
                            {
                                "candidate_id": candidate_id,
                                "variant": variant,
                                "split": r["split"],
                                "timestamp": r["timestamp"],
                                "spread": r["spread"],
                                "n_obs": r["n_obs"],
                            }
                        )
            del base_signal, variants
            gc.collect()

        metrics = pd.DataFrame(metric_rows)
    decisions = pd.DataFrame([classify_candidate(metrics, cid) for cid in selected["candidate_id"].astype(str)])
    decisions = decisions.merge(
        selected[["candidate_id", "family", "field_families", "fields", "operators", "windows", "a7al2g_policy"]],
        on="candidate_id",
        how="left",
    )
    decision_counts = decisions["decision"].value_counts().rename_axis("decision").reset_index(name="count")
    clue_count = int(decisions["decision"].eq("A7AL2I_REPLAY_PREFLIGHT_CLUE").sum())
    blockers = []
    if clue_count == 0:
        blockers.append("no_replay_preflight_clues")
    if int(decisions["decision"].eq("HOLD_A7AL2I_CONTROL_DOMINATED").sum()):
        blockers.append("control_dominated_candidates_present")

    decision = "PASS_A7AL2I_REPLAY_PREFLIGHT_CLUES_FOUND_EXECUTION_HOLD" if clue_count > 0 else "HOLD_A7AL2I_NO_CLUES"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_base": str(BASE_DIR),
        "strict_symbols": len(symbols),
        "rows": frame_rows,
        "candidates_replayed": int(len(selected)),
        "replay_preflight_clue_count": clue_count,
        "decision_counts": {str(r["decision"]): int(r["count"]) for _, r in decision_counts.iterrows()},
        "blockers": blockers,
        "controls": [
            "one_bar_lag",
            "wrong_lag_future_24h",
            "wrong_lag_stale_168h",
            "time_shuffle",
            "symbol_shuffle",
            "same_family_random",
        ],
        "executes_formula_generation": False,
        "executes_formula_search": False,
        "executes_alpha_proof": False,
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    metrics.to_csv(OUT_DIR / "a7al2i_candidate_variant_metrics.csv", index=False)
    decisions.to_csv(OUT_DIR / "a7al2i_candidate_decisions.csv", index=False)
    pd.DataFrame(trace_rows).to_csv(OUT_DIR / "a7al2i_timestamp_spread_trace_sample.csv", index=False)
    write_json(OUT_DIR / "a7al2i_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2I Replay Preflight

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This is a replay preflight on selected control-gated candidates. It does not execute new formula generation/search and does not authorize alpha proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Decision Counts

{md_table(decision_counts, 40)}

## Candidate Decisions

{md_table(decisions[["candidate_id", "family", "field_families", "decision", "original_validation_spread", "original_test_spread", "original_recent_spread", "original_may_stress_spread", "one_bar_lag_recent_spread", "control_dominance_ratio_premay_max"]], 80)}

## Boundary

```text
Allowed interpretation:
  A7AL2I_REPLAY_PREFLIGHT_CLUE means a derived/interacted structure deserves controlled follow-up.

Not authorized:
  alpha proof
  shadow / paper / live
  large formula search
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
