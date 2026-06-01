from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore30e_bounded_numeric_probe"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE30E_BOUNDED_NUMERIC_PROBE_20260602.md"
CORE30 = REPO / "runtime" / "a7ffcore30_independent_family_numeric_probe_contract" / "a7ffcore30_manifest.json"
QUEUE_PATH = REPO / "runtime" / "a7ffcore30_independent_family_numeric_probe_contract" / "a7ffcore30_numeric_probe_queue.csv"

TOP498 = Path("G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v2_20260527")
CORE12_AGG = Path(
    "G:/AlphaFactory_CryptoData/gold/features/binance_core12_all_features_metrics_market_structure_aggtrades_v1_20260524.parquet"
)


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


def load_dataset(dataset_name: str, fields: set[str]) -> pd.DataFrame:
    if dataset_name == "top498_replay_v2":
        cols = sorted({"symbol", "timestamp", "trade_close", *fields})
        table = ds.dataset(str(TOP498), format="parquet").to_table(columns=cols)
    elif dataset_name == "core12_aggtrades_all_features":
        # Core12 panel uses mark_price_close as the clean close proxy.
        cols = sorted({"symbol", "timestamp", "mark_price_close", *fields})
        table = pq.read_table(str(CORE12_AGG), columns=cols)
    else:
        raise ValueError(dataset_name)
    df = table.to_pandas()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    close_col = "trade_close" if "trade_close" in df.columns else "mark_price_close"
    df["__close"] = pd.to_numeric(df[close_col], errors="coerce")
    for col in fields:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def cs_zscore(s: pd.Series, ts: pd.Series) -> pd.Series:
    mean = s.groupby(ts).transform("mean")
    std = s.groupby(ts).transform("std").replace(0, np.nan)
    return (s - mean) / std


def cs_rank(s: pd.Series, ts: pd.Series) -> pd.Series:
    return s.groupby(ts).rank(pct=True) - 0.5


def delta(df: pd.DataFrame, field: str, window: int) -> pd.Series:
    return df.groupby("symbol", sort=False)[field].diff(window)


def build_signal(df: pd.DataFrame, row: pd.Series, cache: dict[tuple[str, str, int], pd.Series]) -> pd.Series:
    primary = str(row["primary_field"])
    partner = str(row["partner_field"])
    window = int(row["window_h"])
    op = str(row["operator"])
    ts = df["timestamp"]

    def cached(kind: str, field: str, w: int) -> pd.Series:
        key = (kind, field, w)
        if key in cache:
            return cache[key]
        if kind == "delta":
            out = delta(df, field, w)
        elif kind == "cs_z_delta":
            out = cs_zscore(delta(df, field, w), ts)
        elif kind == "cs_z_level":
            out = cs_zscore(df[field], ts)
        elif kind == "cs_rank_level":
            out = cs_rank(df[field], ts)
        else:
            raise ValueError(kind)
        cache[key] = out.astype("float32")
        return cache[key]

    partner_z = cached("cs_z_delta", partner, window)
    if op == "Delta":
        sig = cached("delta", primary, window) * partner_z
    elif op == "ZScore":
        sig = cached("cs_z_level", primary, window) * partner_z
    elif op == "TSRank":
        sig = cached("cs_rank_level", primary, window) * partner_z
    elif op == "SpreadShortLong":
        sig = cached("cs_z_delta", primary, window) - cached("cs_z_delta", partner, min(336, window * 4))
    elif op == "WinsorZ":
        sig = cached("cs_z_delta", primary, window).clip(-3, 3) * np.sign(cached("delta", partner, window))
    else:
        sig = cached("cs_z_delta", primary, window) * partner_z
    return pd.Series(sig, index=df.index, dtype="float32")


def attach_labels(df: pd.DataFrame, horizons: list[int]) -> pd.DataFrame:
    for h in horizons:
        future = df.groupby("symbol", sort=False)["__close"].shift(-h)
        ret = future / df["__close"] - 1.0
        past = df["__close"] / df.groupby("symbol", sort=False)["__close"].shift(h) - 1.0
        df[f"L0_h{h}"] = ret.astype("float32")
        df[f"L1_h{h}"] = (ret - ret.groupby(df["timestamp"]).transform("mean")).astype("float32")
        vol = past.abs().groupby(df["timestamp"]).transform("median").replace(0, np.nan)
        df[f"L5_h{h}"] = (ret / vol).clip(-20, 20).astype("float32")
        df[f"CONTROL_STALE_h{h}"] = past.astype("float32")
    return df


def score_signal(frame: pd.DataFrame, signal: pd.Series, label: str, control: str) -> dict[str, float]:
    tmp = frame[["timestamp", label, control]].copy()
    tmp["signal"] = signal.loc[frame.index].to_numpy(dtype="float32", copy=False)
    tmp = tmp.replace([np.inf, -np.inf], np.nan).dropna()
    if tmp.empty or tmp["signal"].nunique() < 10:
        return {"ic": np.nan, "spread": np.nan, "control_ic": np.nan, "control_ratio": np.nan, "n": 0}
    sig_rank = tmp["signal"].groupby(tmp["timestamp"]).rank(pct=True)
    label_rank = tmp[label].groupby(tmp["timestamp"]).rank(pct=True)
    control_rank = tmp[control].groupby(tmp["timestamp"]).rank(pct=True)
    ic = float(sig_rank.corr(label_rank))
    control_ic = float(sig_rank.corr(control_rank))
    top = tmp.loc[sig_rank >= 0.9, label].mean()
    bot = tmp.loc[sig_rank <= 0.1, label].mean()
    spread = float(top - bot)
    control_ratio = abs(control_ic) / (abs(ic) + 1e-9) if np.isfinite(ic) else np.nan
    return {"ic": ic, "spread": spread, "control_ic": control_ic, "control_ratio": float(control_ratio), "n": int(tmp.shape[0])}


def sample_frame(df: pd.DataFrame, max_timestamps: int = 768) -> pd.DataFrame:
    stamps = pd.Index(sorted(df["timestamp"].dropna().unique()))
    if len(stamps) > max_timestamps:
        idx = np.linspace(0, len(stamps) - 1, max_timestamps).round().astype(int)
        stamps = stamps[idx]
    return df[df["timestamp"].isin(stamps)].copy()


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE30)
    if source.get("decision") != "PASS_A7FFCORE30_NUMERIC_PROBE_CONTRACT_READY_FOR_CORE30E":
        raise SystemExit(f"CORE30 not ready for CORE30E: {source.get('decision')}")
    queue = pd.read_csv(QUEUE_PATH)
    horizons = [4, 8, 24]
    result_rows: list[dict[str, Any]] = []
    dataset_summaries: list[dict[str, Any]] = []

    for dataset_name, q in queue.groupby("dataset", sort=True):
        fields = set(q["primary_field"].astype(str)).union(set(q["partner_field"].astype(str)))
        df = load_dataset(dataset_name, fields)
        df = attach_labels(df, horizons)
        sampled = sample_frame(df)
        cache: dict[tuple[str, str, int], pd.Series] = {}
        dataset_summaries.append(
            {
                "dataset": dataset_name,
                "rows": int(df.shape[0]),
                "sample_rows": int(sampled.shape[0]),
                "symbols": int(df["symbol"].nunique()),
                "sample_timestamps": int(sampled["timestamp"].nunique()),
                "field_count": len(fields),
            }
        )
        for _, row in q.iterrows():
            signal = build_signal(df, row, cache)
            for h in horizons:
                for label_family in ["L0", "L1", "L5"]:
                    label = f"{label_family}_h{h}"
                    metrics = score_signal(sampled, signal, label, f"CONTROL_STALE_h{h}")
                    result_rows.append(
                        {
                            "numeric_probe_id": row["numeric_probe_id"],
                            "candidate_id": row["candidate_id"],
                            "family_id": row["family_id"],
                            "dataset": dataset_name,
                            "motif": row["motif"],
                            "operator": row["operator"],
                            "label_family": label_family,
                            "horizon_h": h,
                            **metrics,
                        }
                    )
    results = pd.DataFrame(result_rows)
    results["oriented_ic"] = results["ic"].abs()
    results["oriented_spread"] = results["spread"].abs()
    results["control_clean"] = results["control_ratio"].lt(1.0)
    results["non_l7_label"] = True
    candidate_summary = (
        results.groupby(["numeric_probe_id", "family_id"], as_index=False)
        .agg(
            max_oriented_ic=("oriented_ic", "max"),
            max_oriented_spread=("oriented_spread", "max"),
            min_control_ratio=("control_ratio", "min"),
            clean_label_count=("control_clean", "sum"),
            eval_rows=("n", "max"),
        )
        .sort_values(["clean_label_count", "max_oriented_ic"], ascending=[False, False])
    )
    family_summary = (
        candidate_summary.groupby("family_id", as_index=False)
        .agg(
            candidate_count=("numeric_probe_id", "count"),
            clean_candidate_count=("clean_label_count", lambda s: int((s >= 2).sum())),
            median_control_ratio=("min_control_ratio", "median"),
            median_max_ic=("max_oriented_ic", "median"),
        )
        .sort_values("family_id")
    )
    selected = candidate_summary[
        candidate_summary["clean_label_count"].ge(2)
        & candidate_summary["min_control_ratio"].lt(1.0)
        & candidate_summary["max_oriented_ic"].ge(0.005)
    ].copy()
    clean_count = int(selected.shape[0])
    clean_family_count = int(selected["family_id"].nunique()) if not selected.empty else 0
    decision = (
        "PASS_A7FFCORE30E_NUMERIC_PROBE_CLUES_READY_FOR_CORE31_CONTRACT"
        if clean_count >= 6 and clean_family_count >= 2
        else "HOLD_A7FFCORE30E_NUMERIC_PROBE_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-CORE30E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE30",
        "source_decision": source.get("decision"),
        "decision": decision,
        "candidate_count": int(queue.shape[0]),
        "numeric_result_rows": int(results.shape[0]),
        "clean_candidate_count": clean_count,
        "clean_family_count": clean_family_count,
        "executes_numeric": True,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core31_contract": decision.startswith("PASS_"),
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE31 independent family clue consolidation contract"
        if decision.startswith("PASS_")
        else "CORE30E numeric forensic / independent-family repair",
    }
    results.to_csv(RUNTIME / "a7ffcore30e_numeric_results.csv", index=False)
    candidate_summary.to_csv(RUNTIME / "a7ffcore30e_candidate_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore30e_family_summary.csv", index=False)
    selected.to_csv(RUNTIME / "a7ffcore30e_selected_numeric_clues.csv", index=False)
    pd.DataFrame(dataset_summaries).to_csv(RUNTIME / "a7ffcore30e_dataset_summary.csv", index=False)
    write_json(RUNTIME / "a7ffcore30e_manifest.json", manifest)

    lines = [
        "# CRYPTO A7FF-CORE30E BOUNDED NUMERIC PROBE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE30E executes a bounded numeric probe only. It does not execute replay, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Summary",
        "",
        f"- candidate_count: `{manifest['candidate_count']}`",
        f"- numeric_result_rows: `{manifest['numeric_result_rows']}`",
        f"- clean_candidate_count: `{clean_count}`",
        f"- clean_family_count: `{clean_family_count}`",
        "",
        "## Dataset Summary",
        "",
        md_table(pd.DataFrame(dataset_summaries)),
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Selected Numeric Clues",
        "",
        md_table(selected.head(40)),
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
