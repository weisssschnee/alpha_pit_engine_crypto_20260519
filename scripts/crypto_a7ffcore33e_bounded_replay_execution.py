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
RUNTIME = REPO / "runtime" / "a7ffcore33e_bounded_replay_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE33E_BOUNDED_REPLAY_EXECUTION_20260602.md"
CORE33 = REPO / "runtime" / "a7ffcore33_bounded_replay_contract" / "a7ffcore33_manifest.json"
QUEUE_PATH = REPO / "runtime" / "a7ffcore33_bounded_replay_contract" / "a7ffcore33_replay_candidate_queue.csv"

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


def split_name(ts: pd.Series) -> pd.Series:
    out = pd.Series("holdout_or_unmapped", index=ts.index, dtype="object")
    out[(ts >= "2024-01-01") & (ts < "2025-01-01")] = "train_2024"
    out[(ts >= "2025-01-01") & (ts < "2025-07-01")] = "validation_2025H1"
    out[(ts >= "2025-07-01") & (ts < "2026-01-01")] = "test_2025H2"
    out[(ts >= "2026-01-01") & (ts < "2026-05-01")] = "recent_2026JanApr"
    return out


def load_dataset(dataset_name: str, fields: set[str]) -> pd.DataFrame:
    if dataset_name == "top498_replay_v2":
        cols = sorted({"symbol", "timestamp", "trade_close", "trade_quote_volume", *fields})
        table = ds.dataset(str(TOP498), format="parquet").to_table(columns=cols)
    elif dataset_name == "core12_aggtrades_all_features":
        cols = sorted({"symbol", "timestamp", "mark_price_close", "agg_notional", *fields})
        table = pq.read_table(str(CORE12_AGG), columns=cols)
    else:
        raise ValueError(dataset_name)
    df = table.to_pandas()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    close_col = "trade_close" if "trade_close" in df.columns else "mark_price_close"
    vol_col = "trade_quote_volume" if "trade_quote_volume" in df.columns else "agg_notional"
    df["__close"] = pd.to_numeric(df[close_col], errors="coerce")
    df["__liquidity_proxy"] = pd.to_numeric(df[vol_col], errors="coerce")
    df["split"] = split_name(df["timestamp"])
    for col in fields:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[df["split"].ne("holdout_or_unmapped")].copy()


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


def replay_metric(df: pd.DataFrame, signal: pd.Series, label: str, control: str, split: str, cost_bps: float) -> dict[str, Any]:
    frame = df.loc[df["split"].eq(split), ["timestamp", "symbol", label, control]].copy()
    frame["signal"] = signal.loc[frame.index].to_numpy(dtype="float32", copy=False)
    frame = frame.replace([np.inf, -np.inf], np.nan).dropna()
    if frame.empty or frame["timestamp"].nunique() < 100:
        return {"split": split, "spread": np.nan, "net_spread": np.nan, "control_ratio": np.nan, "turnover": np.nan, "tstat": np.nan, "n": 0}
    rank = frame["signal"].groupby(frame["timestamp"]).rank(pct=True)
    pos = pd.Series(0.0, index=frame.index)
    pos[rank >= 0.9] = 1.0
    pos[rank <= 0.1] = -1.0
    frame["position"] = pos
    frame["pnl"] = frame["position"] * frame[label]
    frame["control_pnl"] = frame["position"] * frame[control]
    by_ts = frame.groupby("timestamp", sort=False).agg(pnl=("pnl", "mean"), control_pnl=("control_pnl", "mean"))
    wide = frame.pivot_table(index="timestamp", columns="symbol", values="position", fill_value=0.0)
    turnover = float(wide.diff().abs().mean(axis=1).mean()) if wide.shape[0] > 1 else np.nan
    spread = float(by_ts["pnl"].mean())
    control_spread = float(by_ts["control_pnl"].mean())
    net = spread - (turnover * cost_bps / 10000.0 if np.isfinite(turnover) else 0.0)
    tstat = float(by_ts["pnl"].mean() / (by_ts["pnl"].std(ddof=1) / np.sqrt(by_ts.shape[0]))) if by_ts["pnl"].std(ddof=1) else np.nan
    return {
        "split": split,
        "spread": spread,
        "net_spread": net,
        "control_ratio": abs(control_spread) / (abs(spread) + 1e-9),
        "turnover": turnover,
        "tstat": tstat,
        "n": int(frame.shape[0]),
        "timestamp_count": int(by_ts.shape[0]),
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE33)
    if source.get("decision") != "PASS_A7FFCORE33_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE33E":
        raise SystemExit(f"CORE33 not ready for CORE33E: {source.get('decision')}")
    queue = pd.read_csv(QUEUE_PATH)
    horizons = [4, 8, 24]
    labels = ["L0", "L1", "L5"]
    splits = ["train_2024", "validation_2025H1", "test_2025H2", "recent_2026JanApr"]
    rows: list[dict[str, Any]] = []
    dataset_rows: list[dict[str, Any]] = []
    for dataset_name, q in queue.groupby("dataset", sort=True):
        fields = set(q["primary_field"].astype(str)).union(set(q["partner_field"].astype(str)))
        df = attach_labels(load_dataset(dataset_name, fields), horizons)
        dataset_rows.append(
            {
                "dataset": dataset_name,
                "rows": int(df.shape[0]),
                "symbols": int(df["symbol"].nunique()),
                "timestamp_min": str(df["timestamp"].min()),
                "timestamp_max": str(df["timestamp"].max()),
            }
        )
        cache: dict[tuple[str, str, int], pd.Series] = {}
        for _, candidate in q.iterrows():
            sig = build_signal(df, candidate, cache)
            for h in horizons:
                for label_family in labels:
                    for split in splits:
                        m = replay_metric(df, sig, f"{label_family}_h{h}", f"CONTROL_STALE_h{h}", split, cost_bps=5.0)
                        rows.append(
                            {
                                "replay_candidate_id": candidate["replay_candidate_id"],
                                "family_id": candidate["family_id"],
                                "dataset": dataset_name,
                                "motif": candidate["motif"],
                                "operator": candidate["operator"],
                                "label_family": label_family,
                                "horizon_h": h,
                                **m,
                            }
                        )
    results = pd.DataFrame(rows)
    results["positive_net"] = results["net_spread"].gt(0)
    results["control_clean"] = results["control_ratio"].lt(1.0)
    summary = (
        results.groupby(["replay_candidate_id", "family_id"], as_index=False)
        .agg(
            positive_net_count=("positive_net", "sum"),
            control_clean_count=("control_clean", "sum"),
            median_control_ratio=("control_ratio", "median"),
            median_net_spread=("net_spread", "median"),
            max_tstat=("tstat", "max"),
            eval_rows=("n", "max"),
        )
        .sort_values(["positive_net_count", "control_clean_count", "max_tstat"], ascending=[False, False, False])
    )
    survivors = summary[
        summary["positive_net_count"].ge(18)
        & summary["control_clean_count"].ge(18)
        & summary["median_control_ratio"].lt(1.0)
    ].copy()
    family_summary = (
        summary.groupby("family_id", as_index=False)
        .agg(
            candidate_count=("replay_candidate_id", "count"),
            survivor_count=("positive_net_count", lambda s: int((s >= 18).sum())),
            median_control_ratio=("median_control_ratio", "median"),
            median_net_spread=("median_net_spread", "median"),
        )
        .sort_values("family_id")
    )
    survivor_family_count = int(survivors["family_id"].nunique()) if not survivors.empty else 0
    decision = (
        "PASS_A7FFCORE33E_BOUNDED_REPLAY_SURVIVORS_READY_FOR_CORE34_ARBITRATION"
        if survivors.shape[0] >= 6 and survivor_family_count >= 2
        else "HOLD_A7FFCORE33E_BOUNDED_REPLAY_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-CORE33E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE33",
        "source_decision": source.get("decision"),
        "decision": decision,
        "candidate_count": int(queue.shape[0]),
        "replay_result_rows": int(results.shape[0]),
        "survivor_count": int(survivors.shape[0]),
        "survivor_family_count": survivor_family_count,
        "executes_bounded_replay": True,
        "executes_search": False,
        "authorizes_core34_arbitration": decision.startswith("PASS_"),
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE34 search-readiness arbitration" if decision.startswith("PASS_") else "CORE33E replay forensic / repair",
    }
    results.to_csv(RUNTIME / "a7ffcore33e_replay_results.csv", index=False)
    summary.to_csv(RUNTIME / "a7ffcore33e_candidate_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore33e_family_summary.csv", index=False)
    survivors.to_csv(RUNTIME / "a7ffcore33e_survivors.csv", index=False)
    pd.DataFrame(dataset_rows).to_csv(RUNTIME / "a7ffcore33e_dataset_summary.csv", index=False)
    write_json(RUNTIME / "a7ffcore33e_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE33E BOUNDED REPLAY EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE33E executes bounded replay diagnostics only. It does not execute formula search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Summary",
        "",
        f"- candidate_count: `{manifest['candidate_count']}`",
        f"- replay_result_rows: `{manifest['replay_result_rows']}`",
        f"- survivor_count: `{manifest['survivor_count']}`",
        f"- survivor_family_count: `{survivor_family_count}`",
        "",
        "## Dataset Summary",
        "",
        md_table(pd.DataFrame(dataset_rows)),
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Survivors",
        "",
        md_table(survivors),
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
