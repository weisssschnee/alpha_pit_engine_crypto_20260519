from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from crypto_a7ffcore30e_bounded_numeric_probe import build_signal, load_dataset


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore39e_symbol_level_book_packet_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE39E_SYMBOL_LEVEL_BOOK_PACKET_AUDIT_20260602.md"
CORE39 = REPO / "runtime" / "a7ffcore39_symbol_level_book_packet_contract" / "a7ffcore39_manifest.json"
CORE33_QUEUE = REPO / "runtime" / "a7ffcore33_bounded_replay_contract" / "a7ffcore33_replay_candidate_queue.csv"
PACKET_ROOT = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore39e_symbol_level_book_packet_20260602")

HORIZONS = [8, 24]
MAX_TIMESTAMPS_PER_DATASET = 48
CONTROL_VARIANTS = ["original", "stale", "sign_flip"]


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


def split_name(timestamp: pd.Series) -> pd.Series:
    ts = pd.to_datetime(timestamp, utc=True)
    out = pd.Series("recent_2026JanApr", index=timestamp.index, dtype=object)
    out.loc[ts.lt(pd.Timestamp("2025-01-01", tz="UTC"))] = "train_2024"
    out.loc[ts.ge(pd.Timestamp("2025-01-01", tz="UTC")) & ts.lt(pd.Timestamp("2025-07-01", tz="UTC"))] = "validation_2025H1"
    out.loc[ts.ge(pd.Timestamp("2025-07-01", tz="UTC")) & ts.lt(pd.Timestamp("2026-01-01", tz="UTC"))] = "test_2025H2"
    return out


def choose_timestamps(df: pd.DataFrame, max_timestamps: int) -> pd.Index:
    stamps = pd.Index(sorted(df["timestamp"].dropna().unique()))
    if len(stamps) <= max_timestamps:
        return stamps
    idx = np.linspace(0, len(stamps) - 1, max_timestamps).round().astype(int)
    return stamps[idx]


def attach_symbol_labels(df: pd.DataFrame, horizon: int, quote_col: str) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    future = df.groupby("symbol", sort=False)["__close"].shift(-horizon)
    ret = future / df["__close"] - 1.0
    out["forward_return"] = ret.astype("float32")
    out["cs_relative_return"] = (ret - ret.groupby(df["timestamp"]).transform("mean")).astype("float32")
    market = (
        df.loc[df["symbol"].isin(["BTCUSDT", "ETHUSDT"]), ["timestamp"]]
        .assign(market_leg=ret.loc[df["symbol"].isin(["BTCUSDT", "ETHUSDT"])].to_numpy())
        .groupby("timestamp")["market_leg"]
        .mean()
    )
    fallback_market = ret.groupby(df["timestamp"]).transform("mean")
    market_ret = df["timestamp"].map(market).fillna(fallback_market)
    out["market_beta_residual_return"] = (ret - market_ret).astype("float32")
    quote = pd.to_numeric(df[quote_col], errors="coerce")
    tier = quote.groupby(df["timestamp"]).rank(pct=True).mul(5).clip(0, 4).fillna(2).astype(int)
    tier_key = df["timestamp"].astype(str) + "|" + tier.astype(str)
    out["liquidity_tier_relative_return"] = (ret - ret.groupby(tier_key).transform("mean")).astype("float32")
    one_h = df.groupby("symbol", sort=False)["__close"].pct_change()
    realized_vol = (
        one_h.groupby(df["symbol"], sort=False)
        .rolling(24, min_periods=6)
        .std()
        .reset_index(level=0, drop=True)
        .reindex(df.index)
        .replace(0, np.nan)
    )
    out["vol_adjusted_return"] = (ret / realized_vol).clip(-20, 20).astype("float32")
    return out


def packet_for_candidate(
    df: pd.DataFrame,
    row: pd.Series,
    signal: pd.Series,
    sample_timestamps: pd.Index,
    *,
    quote_col: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    base = df.loc[df["timestamp"].isin(sample_timestamps), ["symbol", "timestamp", "__close", quote_col]].copy()
    base["candidate_score"] = signal.loc[base.index].astype("float32")
    base["candidate_rank"] = base["candidate_score"].groupby(base["timestamp"]).rank(pct=True, method="average")
    packets: list[pd.DataFrame] = []
    diagnostics: dict[str, Any] = {
        "candidate_id": row["replay_candidate_id"],
        "family_id": row["family_id"],
        "dataset": row["dataset"],
        "sample_rows": int(base.shape[0]),
        "score_non_null_ratio": float(base["candidate_score"].notna().mean()) if len(base) else 0.0,
        "score_std": float(base["candidate_score"].std(skipna=True)) if base["candidate_score"].notna().any() else np.nan,
    }
    label_cache = {h: attach_symbol_labels(df, h, quote_col).loc[base.index] for h in HORIZONS}
    stale_cache = {
        h: signal.groupby(df["symbol"], sort=False).shift(h).loc[base.index].astype("float32")
        for h in HORIZONS
    }
    for horizon in HORIZONS:
        labels = label_cache[horizon]
        for control_variant in CONTROL_VARIANTS:
            work = base.copy()
            if control_variant == "stale":
                work["candidate_score"] = stale_cache[horizon].to_numpy()
            elif control_variant == "sign_flip":
                work["candidate_score"] = -work["candidate_score"]
            work["candidate_rank"] = work["candidate_score"].groupby(work["timestamp"]).rank(pct=True, method="average")
            selected = work[work["candidate_rank"].ge(0.9) | work["candidate_rank"].le(0.1)].copy()
            if selected.empty:
                continue
            selected["side"] = np.where(selected["candidate_rank"].ge(0.9), "long", "short")
            selected["raw_side"] = np.where(selected["side"].eq("long"), 1.0, -1.0)
            count_by_side = selected.groupby(["timestamp", "side"])["symbol"].transform("count").replace(0, np.nan)
            selected["raw_weight"] = (selected["raw_side"] / count_by_side).astype("float32")
            selected["capped_weight"] = selected["raw_weight"].clip(-0.025, 0.025).astype("float32")
            selected["feature_available_time"] = selected["timestamp"] + pd.Timedelta(hours=1)
            selected["execution_time"] = selected["timestamp"] + pd.Timedelta(hours=1)
            selected["candidate_id"] = row["replay_candidate_id"]
            selected["family_id"] = row["family_id"]
            selected["cluster_key"] = row["cluster_key"]
            selected["split"] = split_name(selected["timestamp"]).to_numpy()
            selected["horizon_h"] = horizon
            selected["quote_volume"] = pd.to_numeric(selected[quote_col], errors="coerce").astype("float32")
            selected["turnover_proxy"] = selected["raw_weight"].abs().astype("float32")
            selected["cost_bps"] = 5
            selected["control_variant"] = control_variant
            for label_id, col in [
                ("L1_cross_sectional_relative_return", "cs_relative_return"),
                ("L2_market_beta_residual_return", "market_beta_residual_return"),
                ("L3_liquidity_tier_relative_return", "liquidity_tier_relative_return"),
                ("L5_vol_adjusted_return", "vol_adjusted_return"),
            ]:
                packet = selected.copy()
                packet["label_id"] = label_id
                packet["forward_return"] = labels.loc[packet.index, "forward_return"].to_numpy(dtype="float32")
                packet["cs_relative_return"] = labels.loc[packet.index, "cs_relative_return"].to_numpy(dtype="float32")
                packet["market_beta_residual_return"] = labels.loc[packet.index, "market_beta_residual_return"].to_numpy(dtype="float32")
                packet["liquidity_tier_relative_return"] = labels.loc[packet.index, "liquidity_tier_relative_return"].to_numpy(dtype="float32")
                packet["vol_adjusted_return"] = labels.loc[packet.index, "vol_adjusted_return"].to_numpy(dtype="float32")
                packets.append(packet)
    if not packets:
        return pd.DataFrame(), diagnostics
    columns = [
        "candidate_id",
        "timestamp",
        "feature_available_time",
        "execution_time",
        "symbol",
        "split",
        "family_id",
        "cluster_key",
        "label_id",
        "horizon_h",
        "candidate_score",
        "candidate_rank",
        "raw_weight",
        "capped_weight",
        "side",
        "forward_return",
        "cs_relative_return",
        "market_beta_residual_return",
        "liquidity_tier_relative_return",
        "vol_adjusted_return",
        "quote_volume",
        "turnover_proxy",
        "cost_bps",
        "control_variant",
    ]
    return pd.concat(packets, ignore_index=True)[columns], diagnostics


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    PACKET_ROOT.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE39)
    if source.get("decision") != "PASS_A7FFCORE39_SYMBOL_LEVEL_BOOK_PACKET_CONTRACT_READY_FOR_CORE39E":
        raise SystemExit(f"CORE39 not ready for CORE39E: {source.get('decision')}")

    queue = pd.read_csv(CORE33_QUEUE)
    packets: list[pd.DataFrame] = []
    diag_rows: list[dict[str, Any]] = []
    dataset_rows: list[dict[str, Any]] = []
    shard_rows: list[dict[str, Any]] = []
    for dataset_name, q in queue.groupby("dataset", sort=True):
        fields = set(q["primary_field"].astype(str)).union(set(q["partner_field"].astype(str)))
        quote_col = "trade_quote_volume" if dataset_name == "top498_replay_v2" else "agg_notional"
        fields.add(quote_col)
        df = load_dataset(dataset_name, fields)
        if quote_col not in df.columns:
            raise SystemExit(f"missing quote/liquidity column for {dataset_name}")
        sample_timestamps = choose_timestamps(df, MAX_TIMESTAMPS_PER_DATASET)
        cache: dict[tuple[str, str, int], pd.Series] = {}
        dataset_rows.append(
            {
                "dataset": dataset_name,
                "source_rows": int(df.shape[0]),
                "source_symbols": int(df["symbol"].nunique()),
                "source_timestamps": int(df["timestamp"].nunique()),
                "sample_timestamps": int(len(sample_timestamps)),
                "candidate_count": int(q.shape[0]),
                "quote_col": quote_col,
            }
        )
        for shard_id, (_, row) in enumerate(q.reset_index(drop=True).iterrows()):
            signal = build_signal(df, row, cache)
            packet, diag = packet_for_candidate(df, row, signal, sample_timestamps, quote_col=quote_col)
            diag_rows.append(diag)
            if not packet.empty:
                packets.append(packet)
            shard_rows.append(
                {
                    "dataset": dataset_name,
                    "shard_id": f"{dataset_name}_candidate_{shard_id:02d}",
                    "candidate_id": row["replay_candidate_id"],
                    "family_id": row["family_id"],
                    "estimated_full_source_rows": int(df.shape[0]),
                    "sample_packet_rows": int(packet.shape[0]),
                    "recommended_full_packet_output": str(PACKET_ROOT / f"candidate={row['replay_candidate_id']}.parquet").replace("\\", "/"),
                }
            )
    packet_sample = pd.concat(packets, ignore_index=True) if packets else pd.DataFrame()
    sample_path = PACKET_ROOT / "a7ffcore39e_symbol_level_packet_sample.parquet"
    if not packet_sample.empty:
        packet_sample.to_parquet(sample_path, index=False)

    dataset_summary = pd.DataFrame(dataset_rows)
    candidate_diag = pd.DataFrame(diag_rows)
    shard_plan = pd.DataFrame(shard_rows)
    quality = pd.DataFrame(
        [
            {
                "metric": "packet_sample_rows",
                "value": int(packet_sample.shape[0]),
                "pass": bool(packet_sample.shape[0] > 0),
            },
            {
                "metric": "candidate_count_in_sample",
                "value": int(packet_sample["candidate_id"].nunique()) if not packet_sample.empty else 0,
                "pass": bool(not packet_sample.empty and packet_sample["candidate_id"].nunique() == queue["replay_candidate_id"].nunique()),
            },
            {
                "metric": "label_count_in_sample",
                "value": int(packet_sample["label_id"].nunique()) if not packet_sample.empty else 0,
                "pass": bool(not packet_sample.empty and packet_sample["label_id"].nunique() == 4),
            },
            {
                "metric": "control_variant_count_in_sample",
                "value": int(packet_sample["control_variant"].nunique()) if not packet_sample.empty else 0,
                "pass": bool(not packet_sample.empty and packet_sample["control_variant"].nunique() == len(CONTROL_VARIANTS)),
            },
            {
                "metric": "required_field_count",
                "value": int(packet_sample.shape[1]) if not packet_sample.empty else 0,
                "pass": bool(not packet_sample.empty and packet_sample.shape[1] == 24),
            },
            {
                "metric": "missing_label_rate",
                "value": float(packet_sample[["forward_return", "cs_relative_return", "market_beta_residual_return", "liquidity_tier_relative_return", "vol_adjusted_return"]].isna().mean().mean()) if not packet_sample.empty else 1.0,
                "pass": bool(not packet_sample.empty and packet_sample[["forward_return", "cs_relative_return", "market_beta_residual_return", "liquidity_tier_relative_return", "vol_adjusted_return"]].isna().mean().mean() < 0.2),
            },
        ]
    )
    artifact_manifest = pd.DataFrame(
        [
            {
                "artifact": "symbol_level_packet_sample",
                "path": str(sample_path).replace("\\", "/"),
                "committed_to_git": False,
                "rows": int(packet_sample.shape[0]),
                "columns": int(packet_sample.shape[1]) if not packet_sample.empty else 0,
            }
        ]
    )
    pass_ready = bool(quality["pass"].all())
    decision = (
        "PASS_A7FFCORE39E_SYMBOL_LEVEL_PACKET_SAMPLE_READY_FOR_CORE40_CONTRACT"
        if pass_ready
        else "HOLD_A7FFCORE39E_SYMBOL_LEVEL_PACKET_SAMPLE_QUALITY_FAIL"
    )
    manifest = {
        "stage": "A7FF-CORE39E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE39",
        "source_decision": source.get("decision"),
        "decision": decision,
        "candidate_count": int(queue.shape[0]),
        "packet_sample_rows": int(packet_sample.shape[0]),
        "packet_sample_path": str(sample_path).replace("\\", "/"),
        "packet_sample_committed_to_git": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core40_contract": pass_ready,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE40 bounded book-objective replay contract" if pass_ready else "A7FF-CORE39E packet quality repair",
    }
    dataset_summary.to_csv(RUNTIME / "a7ffcore39e_dataset_summary.csv", index=False)
    candidate_diag.to_csv(RUNTIME / "a7ffcore39e_candidate_score_diagnostics.csv", index=False)
    shard_plan.to_csv(RUNTIME / "a7ffcore39e_shard_plan.csv", index=False)
    quality.to_csv(RUNTIME / "a7ffcore39e_packet_quality_audit.csv", index=False)
    artifact_manifest.to_csv(RUNTIME / "a7ffcore39e_packet_artifact_manifest.csv", index=False)
    write_json(RUNTIME / "a7ffcore39e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE39E SYMBOL-LEVEL BOOK PACKET AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE39E constructs a bounded symbol-level packet sample outside git and records quality/shard evidence in repo. It does not run book replay, formula search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Packet Sample",
        "",
        f"- path: `{manifest['packet_sample_path']}`",
        f"- rows: `{manifest['packet_sample_rows']}`",
        "- committed_to_git: `false`",
        "",
        "## Quality Audit",
        "",
        md_table(quality),
        "",
        "## Dataset Summary",
        "",
        md_table(dataset_summary),
        "",
        "## Candidate Score Diagnostics",
        "",
        md_table(candidate_diag),
        "",
        "## Shard Plan Preview",
        "",
        md_table(shard_plan),
        "",
        "## Artifact Manifest",
        "",
        md_table(artifact_manifest),
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
