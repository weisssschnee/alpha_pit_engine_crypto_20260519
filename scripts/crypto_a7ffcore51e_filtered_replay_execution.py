from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra
from crypto_a7ffcore49e_full_universe_null_vector_preflight_execution import (
    extract_fields,
    read_base_panel,
    overlay_latent_fields,
    vector_controls,
)


RUNTIME = REPO / "runtime" / "a7ffcore51e_filtered_replay_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE51E_FILTERED_REPLAY_EXECUTION_20260602.md"
CORE51 = REPO / "runtime" / "a7ffcore51_filtered_replay_contract" / "a7ffcore51_manifest.json"
FILTERED = REPO / "runtime" / "a7ffcore50_null_vector_preflight_arbitration" / "a7ffcore50_filtered_seed_preview.csv"
HORIZONS = [1, 4, 8, 24]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def select_balanced(filtered: pd.DataFrame, max_count: int) -> pd.DataFrame:
    data = filtered.copy()
    data["active_ratio_num"] = pd.to_numeric(data["active_ratio"], errors="coerce").fillna(0.0)
    data["group_key"] = (
        data["semantic_pair"].astype(str)
        + "|"
        + data["operator"].astype(str)
        + "|"
        + data.get("stale_risk_tier", pd.Series("unknown", index=data.index)).astype(str)
    )
    groups = [g.sort_values("active_ratio_num", ascending=False).reset_index(drop=True) for _, g in data.groupby("group_key", sort=True)]
    selected: list[pd.Series] = []
    seen: set[str] = set()
    positions = [0 for _ in groups]
    progressed = True
    while progressed and len(selected) < max_count:
        progressed = False
        for idx, group in enumerate(groups):
            while positions[idx] < len(group):
                row = group.iloc[positions[idx]]
                positions[idx] += 1
                seed_id = str(row["seed_id"])
                if seed_id in seen:
                    continue
                selected.append(row)
                seen.add(seed_id)
                progressed = True
                break
            if len(selected) >= max_count:
                break
    return pd.DataFrame(selected).drop(columns=["group_key"], errors="ignore").reset_index(drop=True)


def add_labels(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.sort_values(["symbol", "timestamp"]).reset_index(drop=True).copy()
    close = pd.to_numeric(frame["trade_close"], errors="coerce").astype("float64")
    for horizon in HORIZONS:
        fwd = close.groupby(frame["symbol"], sort=False).shift(-horizon) / close - 1.0
        frame[f"label_raw_{horizon}h"] = fwd.replace([np.inf, -np.inf], np.nan)
        mean = frame[f"label_raw_{horizon}h"].groupby(frame["timestamp"], sort=False).transform("mean")
        frame[f"label_xs_{horizon}h"] = frame[f"label_raw_{horizon}h"] - mean
    if "split" not in frame.columns:
        frame["split"] = "unknown"
    return frame


def spread_by_timestamp(frame: pd.DataFrame, signal: pd.Series, label: str) -> pd.Series:
    tmp = pd.DataFrame({"timestamp": frame["timestamp"], "signal": signal, "label": frame[label]})
    tmp = tmp.dropna()
    if tmp.empty:
        return pd.Series(dtype=float)
    rank = tmp["signal"].groupby(tmp["timestamp"], sort=False).rank(pct=True, method="average")
    top = tmp[rank >= 0.9].groupby("timestamp", sort=False)["label"].mean()
    bottom = tmp[rank <= 0.1].groupby("timestamp", sort=False)["label"].mean()
    return (top - bottom).dropna()


def replay_stats(frame: pd.DataFrame, signal: pd.Series, label: str) -> dict[str, float]:
    spreads = spread_by_timestamp(frame, signal, label)
    if spreads.empty:
        return {"spread_mean": np.nan, "spread_tstat": np.nan, "spread_obs": 0}
    std = float(spreads.std(skipna=True))
    mean = float(spreads.mean(skipna=True))
    tstat = mean / (std / np.sqrt(len(spreads))) if std > 0 and len(spreads) > 1 else np.nan
    return {"spread_mean": mean, "spread_tstat": float(tstat) if pd.notna(tstat) else np.nan, "spread_obs": int(len(spreads))}


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE51)
    if source.get("decision") != "PASS_A7FFCORE51_FILTERED_REPLAY_CONTRACT_READY_FOR_CORE51E":
        raise SystemExit(f"CORE51 not ready for CORE51E: {source.get('decision')}")
    filtered = pd.read_csv(FILTERED)
    max_replay = int(os.environ.get("A7FFCORE51E_MAX_CANDIDATES", "384"))
    selected = select_balanced(filtered, max_replay)
    required_fields = extract_fields(selected["expression"]) + ["trade_close", "split"]
    frame = read_base_panel(required_fields)
    frame = overlay_latent_fields(frame, required_fields)
    frame = add_labels(frame)
    allowed_fields = set(frame.columns) - {"symbol", "timestamp"}
    evaluator = CryptoFeatureAlgebra(frame[["symbol", "timestamp", *sorted(allowed_fields)]].copy(), set(allowed_fields))

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for _, seed in selected.iterrows():
        try:
            values = evaluator.evaluate(str(seed["expression"])).values
            controls = vector_controls(values, evaluator.frame)
        except Exception as exc:
            failures.append({"seed_id": seed["seed_id"], "expression": seed["expression"], "error": str(exc)})
            continue
        for horizon in HORIZONS:
            for label_family, label_col in [("L0_raw", f"label_raw_{horizon}h"), ("L1_xs", f"label_xs_{horizon}h")]:
                original = replay_stats(frame, values, label_col)
                stale = replay_stats(frame, controls["stale_signal"], label_col)
                time_shuffle = replay_stats(frame, controls["time_shuffle_signal"], label_col)
                symbol_shuffle = replay_stats(frame, controls["symbol_shuffle_signal"], label_col)
                sign_flip = replay_stats(frame, controls["sign_flip_signal"], label_col)
                control_max = np.nanmax(
                    [
                        abs(stale["spread_mean"]) if pd.notna(stale["spread_mean"]) else np.nan,
                        abs(time_shuffle["spread_mean"]) if pd.notna(time_shuffle["spread_mean"]) else np.nan,
                        abs(symbol_shuffle["spread_mean"]) if pd.notna(symbol_shuffle["spread_mean"]) else np.nan,
                        abs(sign_flip["spread_mean"]) if pd.notna(sign_flip["spread_mean"]) else np.nan,
                    ]
                )
                original_abs = abs(original["spread_mean"]) if pd.notna(original["spread_mean"]) else np.nan
                control_ratio = control_max / original_abs if pd.notna(original_abs) and original_abs > 1e-12 else np.nan
                rows.append(
                    {
                        "seed_id": seed["seed_id"],
                        "semantic_pair": seed["semantic_pair"],
                        "operator": seed["operator"],
                        "stale_risk_tier": seed.get("stale_risk_tier", ""),
                        "label_family": label_family,
                        "horizon": horizon,
                        "original_spread_mean": original["spread_mean"],
                        "original_tstat": original["spread_tstat"],
                        "original_obs": original["spread_obs"],
                        "stale_spread_mean": stale["spread_mean"],
                        "time_shuffle_spread_mean": time_shuffle["spread_mean"],
                        "symbol_shuffle_spread_mean": symbol_shuffle["spread_mean"],
                        "sign_flip_spread_mean": sign_flip["spread_mean"],
                        "control_ratio": control_ratio,
                        "decision": "control_clean_positive"
                        if pd.notna(control_ratio) and control_ratio < 1.0 and original["spread_mean"] > 0
                        else "not_control_clean_positive",
                    }
                )

    replay = pd.DataFrame(rows)
    failures_df = pd.DataFrame(failures)
    replay.to_csv(RUNTIME / "a7ffcore51e_replay_metrics.csv", index=False)
    selected.to_csv(RUNTIME / "a7ffcore51e_selected_queue.csv", index=False)
    failures_df.to_csv(RUNTIME / "a7ffcore51e_eval_failures.csv", index=False)
    summary = (
        replay.groupby(["label_family", "horizon"], as_index=False)
        .agg(
            row_count=("seed_id", "count"),
            control_clean_positive_count=("decision", lambda s: int((s == "control_clean_positive").sum())),
            median_control_ratio=("control_ratio", "median"),
            median_original_spread=("original_spread_mean", "median"),
        )
        .sort_values(["label_family", "horizon"])
    )
    summary.to_csv(RUNTIME / "a7ffcore51e_label_horizon_summary.csv", index=False)
    survivor = replay[replay["decision"].eq("control_clean_positive")].copy()
    survivor_summary = (
        survivor.groupby(["semantic_pair", "operator"], as_index=False)
        .agg(row_count=("seed_id", "count"), seed_count=("seed_id", "nunique"), median_control_ratio=("control_ratio", "median"))
        .sort_values(["seed_count", "row_count"], ascending=False)
    )
    survivor_summary.to_csv(RUNTIME / "a7ffcore51e_survivor_family_operator_summary.csv", index=False)

    selected_count = int(selected.shape[0])
    survivor_seed_count = int(survivor["seed_id"].nunique()) if not survivor.empty else 0
    non_l7_survivor_count = int(survivor.shape[0])
    decision = (
        "PASS_A7FFCORE51E_FILTERED_REPLAY_CLUES_READY_FOR_CORE52_ARBITRATION"
        if survivor_seed_count >= 4 and non_l7_survivor_count > 0 and failures_df.empty
        else "HOLD_A7FFCORE51E_FILTERED_REPLAY_NO_CONTROL_CLEAN_CLUES"
    )
    manifest = {
        "stage": "A7FF-CORE51E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE51",
        "source_decision": source.get("decision"),
        "decision": decision,
        "selected_count": selected_count,
        "frame_rows": int(len(frame)),
        "frame_symbols": int(frame["symbol"].nunique()),
        "eval_failure_count": int(len(failures_df)),
        "replay_metric_rows": int(replay.shape[0]),
        "control_clean_survivor_seed_count": survivor_seed_count,
        "executes_replay": True,
        "executes_search": False,
        "executes_generation": False,
        "authorizes_core52_arbitration": decision.startswith("PASS_"),
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE52 replay clue arbitration" if decision.startswith("PASS_") else "A7FF-CORE51R replay failure forensic",
    }
    authorization = {
        "authorized": {
            "A7FF-CORE52 replay clue arbitration": decision.startswith("PASS_"),
            "A7FF-CORE51R replay failure forensic": not decision.startswith("PASS_"),
        },
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    write_json(RUNTIME / "a7ffcore51e_manifest.json", manifest)
    write_json(RUNTIME / "a7ffcore51e_authorization_matrix.json", authorization)

    report = [
        "# CRYPTO A7FF-CORE51E FILTERED REPLAY EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE51E executes bounded filtered replay over the CORE50 vector-clean queue. It is not formula search, alpha proof, promotion, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label / Horizon Summary",
        "",
        md_table(summary, 80),
        "",
        "## Survivor Family / Operator Summary",
        "",
        md_table(survivor_summary, 80),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
