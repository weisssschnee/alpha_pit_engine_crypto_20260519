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
RUNTIME = REPO / "runtime" / "a7ffcore32e_replay_preflight_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE32E_REPLAY_PREFLIGHT_EXECUTION_20260602.md"
CORE32 = REPO / "runtime" / "a7ffcore32_replay_preflight_contract" / "a7ffcore32_manifest.json"
QUEUE_PATH = REPO / "runtime" / "a7ffcore32_replay_preflight_contract" / "a7ffcore32_replay_preflight_queue.csv"

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
    df["__close"] = pd.to_numeric(df[close_col], errors="coerce")
    vol_col = "trade_quote_volume" if "trade_quote_volume" in df.columns else "agg_notional"
    df["__liquidity_proxy"] = pd.to_numeric(df[vol_col], errors="coerce")
    for col in fields:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def sample_frame(df: pd.DataFrame, max_timestamps: int = 1024) -> pd.DataFrame:
    stamps = pd.Index(sorted(df["timestamp"].dropna().unique()))
    if len(stamps) > max_timestamps:
        idx = np.linspace(0, len(stamps) - 1, max_timestamps).round().astype(int)
        stamps = stamps[idx]
    return df[df["timestamp"].isin(stamps)].copy()


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
        df[f"L7_h{h}"] = ret.groupby(df["timestamp"]).rank(pct=True).sub(0.5).astype("float32")
        liq_rank = df["__liquidity_proxy"].groupby(df["timestamp"]).rank(pct=True)
        tier = pd.cut(liq_rank, bins=[0, 0.33, 0.66, 1.0], labels=False, include_lowest=True)
        df[f"L3_h{h}"] = (ret - ret.groupby([df["timestamp"], tier]).transform("mean")).astype("float32")
        df[f"CONTROL_STALE_h{h}"] = past.astype("float32")
        df[f"CONTROL_FUTURE_WRONGLAG_h{h}"] = df.groupby("symbol", sort=False)[ret.name if hasattr(ret, "name") else "__close"].shift(-1) if False else ret.groupby(df["symbol"]).shift(-1)
    return df


def score(frame: pd.DataFrame, signal: pd.Series, label: str, control: str) -> dict[str, float]:
    tmp = frame[["timestamp", label, control]].copy()
    tmp["signal"] = signal.loc[frame.index].to_numpy(dtype="float32", copy=False)
    tmp = tmp.replace([np.inf, -np.inf], np.nan).dropna()
    if tmp.empty or tmp["signal"].nunique() < 10:
        return {"ic": np.nan, "spread": np.nan, "control_ic": np.nan, "control_ratio": np.nan, "n": 0}
    sig_rank = tmp["signal"].groupby(tmp["timestamp"]).rank(pct=True)
    lab_rank = tmp[label].groupby(tmp["timestamp"]).rank(pct=True)
    con_rank = tmp[control].groupby(tmp["timestamp"]).rank(pct=True)
    ic = float(sig_rank.corr(lab_rank))
    control_ic = float(sig_rank.corr(con_rank))
    top = tmp.loc[sig_rank >= 0.9, label].mean()
    bot = tmp.loc[sig_rank <= 0.1, label].mean()
    spread = float(top - bot)
    return {
        "ic": ic,
        "spread": spread,
        "control_ic": control_ic,
        "control_ratio": float(abs(control_ic) / (abs(ic) + 1e-9)) if np.isfinite(ic) else np.nan,
        "n": int(tmp.shape[0]),
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE32)
    if source.get("decision") != "PASS_A7FFCORE32_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE32E":
        raise SystemExit(f"CORE32 not ready for CORE32E: {source.get('decision')}")
    queue = pd.read_csv(QUEUE_PATH)
    horizons = [4, 8, 24]
    labels = ["L0", "L1", "L3", "L5", "L7"]
    rows: list[dict[str, Any]] = []
    dataset_summaries: list[dict[str, Any]] = []
    for dataset_name, q in queue.groupby("dataset", sort=True):
        fields = set(q["primary_field"].astype(str)).union(set(q["partner_field"].astype(str)))
        df = attach_labels(load_dataset(dataset_name, fields), horizons)
        sampled = sample_frame(df)
        cache: dict[tuple[str, str, int], pd.Series] = {}
        dataset_summaries.append(
            {
                "dataset": dataset_name,
                "rows": int(df.shape[0]),
                "sample_rows": int(sampled.shape[0]),
                "symbols": int(df["symbol"].nunique()),
                "sample_timestamps": int(sampled["timestamp"].nunique()),
            }
        )
        for _, candidate in q.iterrows():
            signal = build_signal(df, candidate, cache)
            flipped = -signal
            for h in horizons:
                for label_family in labels:
                    label = f"{label_family}_h{h}"
                    stale = score(sampled, signal, label, f"CONTROL_STALE_h{h}")
                    sign_flip = score(sampled, flipped, label, f"CONTROL_STALE_h{h}")
                    rows.append(
                        {
                            "preflight_candidate_id": candidate["preflight_candidate_id"],
                            "numeric_probe_id": candidate["numeric_probe_id"],
                            "family_id": candidate["family_id"],
                            "dataset": dataset_name,
                            "label_family": label_family,
                            "horizon_h": h,
                            "ic": stale["ic"],
                            "spread": stale["spread"],
                            "control_ratio_stale": stale["control_ratio"],
                            "sign_flip_abs_ic": abs(sign_flip["ic"]) if np.isfinite(sign_flip["ic"]) else np.nan,
                            "n": stale["n"],
                        }
                    )
    results = pd.DataFrame(rows)
    results["control_clean"] = results["control_ratio_stale"].lt(1.0)
    results["non_l7"] = results["label_family"].ne("L7")
    summary = (
        results.groupby(["preflight_candidate_id", "numeric_probe_id", "family_id"], as_index=False)
        .agg(
            max_abs_ic=("ic", lambda s: float(s.abs().max())),
            max_abs_spread=("spread", lambda s: float(s.abs().max())),
            min_control_ratio=("control_ratio_stale", "min"),
            non_l7_clean_rows=("control_clean", lambda s: int(s[results.loc[s.index, "non_l7"]].sum())),
            l7_clean_rows=("control_clean", lambda s: int(s[~results.loc[s.index, "non_l7"]].sum())),
            eval_rows=("n", "max"),
        )
        .sort_values(["non_l7_clean_rows", "max_abs_ic"], ascending=[False, False])
    )
    family_summary = (
        summary.groupby("family_id", as_index=False)
        .agg(
            candidate_count=("preflight_candidate_id", "count"),
            non_l7_clean_candidate_count=("non_l7_clean_rows", lambda s: int((s >= 4).sum())),
            median_control_ratio=("min_control_ratio", "median"),
            median_abs_ic=("max_abs_ic", "median"),
        )
        .sort_values("family_id")
    )
    selected = summary[summary["non_l7_clean_rows"].ge(4) & summary["min_control_ratio"].lt(1.0)].copy()
    selected_family_count = int(selected["family_id"].nunique()) if not selected.empty else 0
    decision = (
        "PASS_A7FFCORE32E_REPLAY_PREFLIGHT_READY_FOR_CORE33_CONTRACT"
        if selected.shape[0] >= 12 and selected_family_count >= 3
        else "HOLD_A7FFCORE32E_REPLAY_PREFLIGHT_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-CORE32E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE32",
        "source_decision": source.get("decision"),
        "decision": decision,
        "candidate_count": int(queue.shape[0]),
        "preflight_result_rows": int(results.shape[0]),
        "selected_preflight_candidate_count": int(selected.shape[0]),
        "selected_family_count": selected_family_count,
        "executes_replay_preflight": True,
        "executes_tradable_replay": False,
        "executes_search": False,
        "authorizes_core33_contract": decision.startswith("PASS_"),
        "authorizes_tradable_replay": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE33 bounded replay contract"
        if decision.startswith("PASS_")
        else "CORE32E preflight forensic / repair",
    }
    results.to_csv(RUNTIME / "a7ffcore32e_preflight_results.csv", index=False)
    summary.to_csv(RUNTIME / "a7ffcore32e_candidate_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore32e_family_summary.csv", index=False)
    selected.to_csv(RUNTIME / "a7ffcore32e_selected_preflight_candidates.csv", index=False)
    pd.DataFrame(dataset_summaries).to_csv(RUNTIME / "a7ffcore32e_dataset_summary.csv", index=False)
    write_json(RUNTIME / "a7ffcore32e_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE32E REPLAY PREFLIGHT EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE32E executes replay-preflight diagnostics only. It does not execute tradable replay, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Summary",
        "",
        f"- candidate_count: `{manifest['candidate_count']}`",
        f"- preflight_result_rows: `{manifest['preflight_result_rows']}`",
        f"- selected_preflight_candidate_count: `{manifest['selected_preflight_candidate_count']}`",
        f"- selected_family_count: `{selected_family_count}`",
        "",
        "## Dataset Summary",
        "",
        md_table(pd.DataFrame(dataset_summaries)),
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Selected Preflight Candidates",
        "",
        md_table(selected.head(40)),
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
