from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

BASE_PANEL_ROOT = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v1_20260525"
LV1_PANEL = DATA_ROOT / "gold" / "features" / "binance_universe498_latent_state_features_v1_20260527.parquet"
LV1_MANIFEST = ROOT / "runtime" / "a7ak_lv1_latent_state_feature_build" / "a7ak_lv1_manifest.json"

OUT_DIR = ROOT / "runtime" / "a7ak_lv2_response_merge_audit"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AK_LV2_RESPONSE_MERGE_AUDIT_20260527.md"

DATA_METADATA_DIR = DATA_ROOT / "gold" / "metadata"
DATA_MERGE_MAP = DATA_METADATA_DIR / "binance_universe498_latent_state_merge_map_v1_20260527.csv"
DATA_RESPONSE_VECTORS = DATA_METADATA_DIR / "binance_universe498_latent_state_response_vectors_v1_20260527.csv"

TRAIN_START = pd.Timestamp("2024-01-01 00:00:00+00:00")
TRAIN_END = pd.Timestamp("2024-12-31 23:00:00+00:00")

LV1_COLUMNS = [
    "symbol",
    "timestamp",
    "split",
    "search_eligibility",
    "liquidity_tier_static",
    "history_tier_static",
    "is_core12",
    "is_major",
    "listing_age_days",
    "age_percentile_active_universe",
    "rolling_coverage_168h",
    "gap_hours_recent_168h",
    "log_quote_volume_168h",
    "liquidity_rank_active_universe",
    "realized_vol_168h",
    "funding_rate_abs_168h",
    "basis_abs_168h",
    "premium_abs_168h",
    "open_interest_change_24h",
    "trade_return_24h",
    "oi_x_price_move_24h",
    "age_x_liquidity",
    "age_x_volatility",
    "age_x_funding_abs",
    "age_bucket_dynamic",
    "liquidity_state",
    "volatility_state",
    "funding_abs_state",
    "basis_abs_state",
    "coverage_state",
    "major_state",
    "raw_latent_state_label",
    "raw_latent_state_id",
    "state_seen_in_train",
]

BASE_COLUMNS = ["symbol", "timestamp", "trade_close"]

SIGNAL_COLUMNS = [
    "trade_return_24h",
    "liquidity_rank_active_universe",
    "realized_vol_168h",
    "funding_rate_abs_168h",
    "basis_abs_168h",
    "open_interest_change_24h",
    "oi_x_price_move_24h",
    "age_x_liquidity",
    "age_x_volatility",
]

RESPONSE_COLUMNS = [
    "fwd_ret_1h_mean",
    "fwd_ret_4h_mean",
    "fwd_ret_24h_mean",
    "fwd_ret_24h_pos_rate",
    "fwd_ret_24h_std",
    "fwd_ret_24h_max_drawdown_proxy",
    "fwd_ret_24h_lag1_mean",
    "btc_fwd_ret_24h_corr",
    "resp_momentum_24h",
    "resp_liquidity_rank",
    "resp_realized_vol",
    "resp_funding_abs",
    "resp_basis_abs",
    "resp_oi_change",
    "resp_oi_x_price",
    "resp_age_x_liquidity",
    "resp_age_x_volatility",
    "avg_log_quote_volume_168h",
    "avg_realized_vol_168h",
    "avg_funding_abs_168h",
    "avg_basis_abs_168h",
    "avg_listing_age_days",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def stable_merge_id(seed: str, index: int) -> str:
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:8]
    return f"mg_{index:04d}_{digest}"


def symbol_dirs() -> list[Path]:
    return sorted(p for p in BASE_PANEL_ROOT.glob("symbol=*") if (p / "part.parquet").exists())


def load_forward_labels() -> pd.DataFrame:
    parts = []
    for sym_dir in symbol_dirs():
        part = pd.read_parquet(sym_dir / "part.parquet", columns=BASE_COLUMNS, engine="pyarrow")
        part["timestamp"] = pd.to_datetime(part["timestamp"], utc=True)
        part = part.sort_values("timestamp").reset_index(drop=True)
        close = pd.to_numeric(part["trade_close"], errors="coerce")
        log_close = np.log(close.where(close > 0))
        for horizon in [1, 4, 24]:
            label = log_close.shift(-horizon) - log_close
            label_end = part["timestamp"] + pd.Timedelta(hours=horizon)
            label = label.where(label_end <= TRAIN_END)
            part[f"fwd_ret_{horizon}h"] = label
        lag1 = log_close.shift(-25) - log_close.shift(-1)
        lag1_end = part["timestamp"] + pd.Timedelta(hours=25)
        part["fwd_ret_24h_lag1"] = lag1.where(lag1_end <= TRAIN_END)
        parts.append(part[["symbol", "timestamp", "fwd_ret_1h", "fwd_ret_4h", "fwd_ret_24h", "fwd_ret_24h_lag1"]])
    return pd.concat(parts, ignore_index=True)


def cs_zscore(frame: pd.DataFrame, column: str) -> pd.Series:
    value = pd.to_numeric(frame[column], errors="coerce").replace([np.inf, -np.inf], np.nan)
    mean = value.groupby(frame["timestamp"]).transform("mean")
    std = value.groupby(frame["timestamp"]).transform("std").replace(0, np.nan)
    z = ((value - mean) / std).clip(-5, 5)
    return z


def max_drawdown_by_state(train: pd.DataFrame) -> pd.DataFrame:
    state_ts = (
        train.dropna(subset=["fwd_ret_24h"])
        .groupby(["raw_latent_state_id", "timestamp"], observed=True)["fwd_ret_24h"]
        .mean()
        .reset_index()
        .sort_values(["raw_latent_state_id", "timestamp"])
    )
    if state_ts.empty:
        return pd.DataFrame(columns=["raw_latent_state_id", "fwd_ret_24h_max_drawdown_proxy"])
    state_ts["cum_ret_proxy"] = state_ts.groupby("raw_latent_state_id")["fwd_ret_24h"].cumsum()
    state_ts["peak_proxy"] = state_ts.groupby("raw_latent_state_id")["cum_ret_proxy"].cummax()
    state_ts["drawdown_proxy"] = state_ts["cum_ret_proxy"] - state_ts["peak_proxy"]
    return (
        state_ts.groupby("raw_latent_state_id", observed=True)["drawdown_proxy"]
        .min()
        .rename("fwd_ret_24h_max_drawdown_proxy")
        .reset_index()
    )


def build_response_vectors(panel: pd.DataFrame) -> pd.DataFrame:
    train = panel[(panel["split"] == "train_2024") & panel["state_seen_in_train"].astype(bool)].copy()
    train = train[(train["timestamp"] >= TRAIN_START) & (train["timestamp"] <= TRAIN_END)].copy()
    btc = train.loc[train["symbol"] == "BTCUSDT", ["timestamp", "fwd_ret_24h"]].rename(columns={"fwd_ret_24h": "btc_fwd_ret_24h"})
    train = train.merge(btc, on="timestamp", how="left")

    signal_map = {
        "trade_return_24h": "resp_momentum_24h",
        "liquidity_rank_active_universe": "resp_liquidity_rank",
        "realized_vol_168h": "resp_realized_vol",
        "funding_rate_abs_168h": "resp_funding_abs",
        "basis_abs_168h": "resp_basis_abs",
        "open_interest_change_24h": "resp_oi_change",
        "oi_x_price_move_24h": "resp_oi_x_price",
        "age_x_liquidity": "resp_age_x_liquidity",
        "age_x_volatility": "resp_age_x_volatility",
    }
    for source_col, response_col in signal_map.items():
        train[f"z_{source_col}"] = cs_zscore(train, source_col)
        train[response_col] = train[f"z_{source_col}"] * train["fwd_ret_24h"]

    agg_spec: dict[str, Any] = {
        "train_rows": ("symbol", "size"),
        "train_symbols": ("symbol", "nunique"),
        "label_rows_1h": ("fwd_ret_1h", "count"),
        "label_rows_4h": ("fwd_ret_4h", "count"),
        "label_rows_24h": ("fwd_ret_24h", "count"),
        "fwd_ret_1h_mean": ("fwd_ret_1h", "mean"),
        "fwd_ret_4h_mean": ("fwd_ret_4h", "mean"),
        "fwd_ret_24h_mean": ("fwd_ret_24h", "mean"),
        "fwd_ret_24h_std": ("fwd_ret_24h", "std"),
        "fwd_ret_24h_lag1_mean": ("fwd_ret_24h_lag1", "mean"),
        "avg_log_quote_volume_168h": ("log_quote_volume_168h", "mean"),
        "avg_realized_vol_168h": ("realized_vol_168h", "mean"),
        "avg_funding_abs_168h": ("funding_rate_abs_168h", "mean"),
        "avg_basis_abs_168h": ("basis_abs_168h", "mean"),
        "avg_listing_age_days": ("listing_age_days", "mean"),
        "avg_rolling_coverage_168h": ("rolling_coverage_168h", "mean"),
        "age_lt30_rows_train": ("age_bucket_dynamic", lambda s: int((s == "age_lt30d").sum())),
        "major_rows_train": ("is_major", lambda s: int(pd.Series(s).astype(bool).sum())),
    }
    for response_col in signal_map.values():
        agg_spec[response_col] = (response_col, "mean")
        agg_spec[f"{response_col}_valid_rows"] = (response_col, "count")

    state = train.groupby(["raw_latent_state_id", "raw_latent_state_label"], observed=True).agg(**agg_spec).reset_index()
    pos_rate = (
        train.assign(fwd_ret_24h_positive=(train["fwd_ret_24h"] > 0).where(train["fwd_ret_24h"].notna()))
        .groupby("raw_latent_state_id", observed=True)["fwd_ret_24h_positive"]
        .mean()
        .rename("fwd_ret_24h_pos_rate")
        .reset_index()
    )
    dd = max_drawdown_by_state(train)

    btc_stats = train.dropna(subset=["fwd_ret_24h", "btc_fwd_ret_24h"]).copy()
    btc_stats["ret_x_btc"] = btc_stats["fwd_ret_24h"] * btc_stats["btc_fwd_ret_24h"]
    btc_stats["ret_sq"] = btc_stats["fwd_ret_24h"] ** 2
    btc_stats["btc_sq"] = btc_stats["btc_fwd_ret_24h"] ** 2
    btc = (
        btc_stats.groupby("raw_latent_state_id", observed=True)
        .agg(
            btc_pair_rows=("fwd_ret_24h", "size"),
            ret_mean=("fwd_ret_24h", "mean"),
            btc_mean=("btc_fwd_ret_24h", "mean"),
            ret_x_btc_mean=("ret_x_btc", "mean"),
            ret_sq_mean=("ret_sq", "mean"),
            btc_sq_mean=("btc_sq", "mean"),
        )
        .reset_index()
    )
    btc_cov = btc["ret_x_btc_mean"] - btc["ret_mean"] * btc["btc_mean"]
    btc_ret_var = btc["ret_sq_mean"] - btc["ret_mean"] ** 2
    btc_btc_var = btc["btc_sq_mean"] - btc["btc_mean"] ** 2
    btc["btc_fwd_ret_24h_corr"] = btc_cov / np.sqrt(btc_ret_var.clip(lower=0) * btc_btc_var.clip(lower=0))
    btc = btc[["raw_latent_state_id", "btc_pair_rows", "btc_fwd_ret_24h_corr"]]

    state = state.merge(pos_rate, on="raw_latent_state_id", how="left")
    state = state.merge(dd, on="raw_latent_state_id", how="left")
    state = state.merge(btc, on="raw_latent_state_id", how="left")
    state["age_lt30_train_share"] = state["age_lt30_rows_train"] / state["train_rows"].replace(0, np.nan)
    state["major_train_share"] = state["major_rows_train"] / state["train_rows"].replace(0, np.nan)
    return state


def robust_standardize(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for col in cols:
        values = pd.to_numeric(df[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
        median = values.median()
        q25 = values.quantile(0.25)
        q75 = values.quantile(0.75)
        scale = q75 - q25
        if not np.isfinite(scale) or scale <= 0:
            scale = values.std()
        if not np.isfinite(scale) or scale <= 0:
            scale = 1.0
        out[col] = ((values.fillna(median) - median) / scale).clip(-6, 6)
    return out


def cosine_similarity_matrix(vectors: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vectors, axis=1)
    norm[norm == 0] = 1.0
    unit = vectors / norm[:, None]
    return unit @ unit.T


def build_merge_audit(response: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = response.copy()
    df["merge_eligible"] = (df["train_rows"] >= 5000) & (df["train_symbols"] >= 5) & (df["label_rows_24h"] >= 1000)
    eligible = df[df["merge_eligible"]].copy().sort_values(["train_rows", "raw_latent_state_id"], ascending=[False, True]).reset_index(drop=True)
    hold = df[~df["merge_eligible"]].copy()

    if eligible.empty:
        merge_map = df[["raw_latent_state_id", "raw_latent_state_label", "train_rows", "train_symbols", "merge_eligible"]].copy()
        merge_map["merged_latent_state_id"] = np.nan
        merge_map["merge_action"] = "insufficient_train_support"
        return merge_map, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    z = robust_standardize(eligible, RESPONSE_COLUMNS).to_numpy(dtype=float)
    sim = cosine_similarity_matrix(z)
    ids = eligible["raw_latent_state_id"].tolist()

    edges = []
    for i, state_id in enumerate(ids):
        neighbors = np.argsort(sim[i])[::-1]
        emitted = 0
        for j in neighbors:
            if i == j:
                continue
            edges.append(
                {
                    "raw_latent_state_id": state_id,
                    "neighbor_state_id": ids[j],
                    "response_cosine_similarity": float(sim[i, j]),
                    "same_age_bucket": bool(eligible.loc[i, "raw_latent_state_label"].split("|")[0] == eligible.loc[j, "raw_latent_state_label"].split("|")[0]),
                    "same_liquidity_state": bool(eligible.loc[i, "raw_latent_state_label"].split("|")[1] == eligible.loc[j, "raw_latent_state_label"].split("|")[1]),
                    "same_volatility_state": bool(eligible.loc[i, "raw_latent_state_label"].split("|")[2] == eligible.loc[j, "raw_latent_state_label"].split("|")[2]),
                }
            )
            emitted += 1
            if emitted >= 5:
                break
    edge_df = pd.DataFrame(edges)

    assigned: dict[str, str] = {}
    rows = []
    group_index = 1
    for i, seed_id in enumerate(ids):
        if seed_id in assigned:
            continue
        group_id = stable_merge_id(seed_id, group_index)
        group_index += 1
        assigned[seed_id] = group_id
        rows.append({"raw_latent_state_id": seed_id, "merged_latent_state_id": group_id, "merge_action": "seed"})
        candidate_idx = np.where(sim[i] >= 0.93)[0]
        candidate_idx = [j for j in candidate_idx if j != i]
        for j in candidate_idx:
            candidate_id = ids[j]
            if candidate_id in assigned:
                continue
            mean_diff = abs(float(eligible.loc[i, "fwd_ret_24h_mean"]) - float(eligible.loc[j, "fwd_ret_24h_mean"]))
            vol_i = float(eligible.loc[i, "fwd_ret_24h_std"]) if pd.notna(eligible.loc[i, "fwd_ret_24h_std"]) else np.nan
            vol_j = float(eligible.loc[j, "fwd_ret_24h_std"]) if pd.notna(eligible.loc[j, "fwd_ret_24h_std"]) else np.nan
            vol_ratio = max(vol_i, vol_j) / max(min(vol_i, vol_j), 1e-12) if np.isfinite(vol_i) and np.isfinite(vol_j) else 1.0
            btc_i = float(eligible.loc[i, "btc_fwd_ret_24h_corr"]) if pd.notna(eligible.loc[i, "btc_fwd_ret_24h_corr"]) else 0.0
            btc_j = float(eligible.loc[j, "btc_fwd_ret_24h_corr"]) if pd.notna(eligible.loc[j, "btc_fwd_ret_24h_corr"]) else 0.0
            if mean_diff <= 0.003 and vol_ratio <= 2.0 and abs(btc_i - btc_j) <= 0.35:
                assigned[candidate_id] = group_id
                rows.append(
                    {
                        "raw_latent_state_id": candidate_id,
                        "merged_latent_state_id": group_id,
                        "merge_action": "response_similar",
                    }
                )
    assigned_df = pd.DataFrame(rows)

    eligible_map = eligible.merge(assigned_df, on="raw_latent_state_id", how="left")
    eligible_map["merge_action"] = eligible_map["merge_action"].fillna("self")
    eligible_map["merged_latent_state_id"] = eligible_map["merged_latent_state_id"].fillna(
        eligible_map["raw_latent_state_id"].map(lambda x: stable_merge_id(str(x), 9999))
    )
    hold_map = hold.copy()
    hold_map["merged_latent_state_id"] = np.nan
    hold_map["merge_action"] = "insufficient_train_support"
    merge_map = pd.concat([eligible_map, hold_map], ignore_index=True, sort=False)

    registry = (
        merge_map[merge_map["merged_latent_state_id"].notna()]
        .groupby("merged_latent_state_id", observed=True)
        .agg(
            raw_state_count=("raw_latent_state_id", "nunique"),
            train_rows=("train_rows", "sum"),
            train_symbols_max=("train_symbols", "max"),
            age_lt30_train_share=("age_lt30_train_share", "mean"),
            avg_response_similarity_seed_members=("raw_latent_state_id", "size"),
            mean_fwd_ret_24h=("fwd_ret_24h_mean", "mean"),
            mean_lag1_ret_24h=("fwd_ret_24h_lag1_mean", "mean"),
            mean_btc_corr=("btc_fwd_ret_24h_corr", "mean"),
        )
        .reset_index()
        .sort_values(["train_rows", "raw_state_count"], ascending=[False, False])
    )
    registry["merge_group_rank"] = np.arange(1, len(registry) + 1)
    return merge_map, registry, edge_df, eligible


def unseen_state_policy(all_states: pd.DataFrame, response: pd.DataFrame) -> pd.DataFrame:
    train_seen = set(response["raw_latent_state_id"].dropna())
    out = all_states[~all_states["raw_latent_state_id"].isin(train_seen)].copy()
    if out.empty:
        return pd.DataFrame(columns=["raw_latent_state_id", "raw_latent_state_label", "rows", "symbols", "policy"])
    out["policy"] = "unseen_in_train_hold_until_lv3_mapping"
    return out[["raw_latent_state_id", "raw_latent_state_label", "rows", "symbols", "policy"]].sort_values("rows", ascending=False)


def build_bias_audit(summary: dict[str, Any]) -> pd.DataFrame:
    rows = [
        {
            "check": "response_fit_window",
            "status": "PASS",
            "detail": "response vectors and merge groups are computed from train_2024 rows only",
        },
        {
            "check": "validation_recent_usage",
            "status": "PASS",
            "detail": "validation/recent rows are not used for response-vector fitting or merge assignment",
        },
        {
            "check": "may_usage",
            "status": "PASS",
            "detail": "May rows are unavailable and not used",
        },
        {
            "check": "label_boundary",
            "status": "PASS",
            "detail": "forward labels are nulled when label_end would cross beyond train_2024",
        },
        {
            "check": "replay_boundary",
            "status": "PASS",
            "detail": "LV2 is a response/merge audit, not a trading replay or promotion test",
        },
        {
            "check": "short_history_policy",
            "status": "PASS",
            "detail": "age_lt30 states are kept for modeling diagnostics but not promoted to proof",
        },
    ]
    if summary.get("unseen_train_hold_states", 0) > 0:
        rows.append(
            {
                "check": "unseen_state_policy",
                "status": "WARN",
                "detail": "states unseen in train are held for LV3 mapping and not force-merged",
            }
        )
    return pd.DataFrame(rows)


def relaxed_merge_suggestions(edges: pd.DataFrame) -> pd.DataFrame:
    if edges.empty:
        return pd.DataFrame(
            columns=[
                "state_a",
                "state_b",
                "response_cosine_similarity",
                "same_age_bucket",
                "same_liquidity_state",
                "same_volatility_state",
                "suggestion_status",
            ]
        )
    rows = []
    seen = set()
    for _, row in edges[edges["response_cosine_similarity"] >= 0.88].iterrows():
        a = str(row["raw_latent_state_id"])
        b = str(row["neighbor_state_id"])
        key = tuple(sorted([a, b]))
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "state_a": key[0],
                "state_b": key[1],
                "response_cosine_similarity": float(row["response_cosine_similarity"]),
                "same_age_bucket": bool(row["same_age_bucket"]),
                "same_liquidity_state": bool(row["same_liquidity_state"]),
                "same_volatility_state": bool(row["same_volatility_state"]),
                "suggestion_status": "candidate_for_review_not_applied",
            }
        )
    return pd.DataFrame(rows).sort_values("response_cosine_similarity", ascending=False) if rows else pd.DataFrame(rows)


def build_report(
    summary: dict[str, Any],
    response: pd.DataFrame,
    merge_map: pd.DataFrame,
    registry: pd.DataFrame,
    edges: pd.DataFrame,
    relaxed: pd.DataFrame,
    unseen: pd.DataFrame,
    bias: pd.DataFrame,
) -> None:
    largest_groups = registry.sort_values("train_rows", ascending=False).head(25) if not registry.empty else registry
    action_counts = merge_map["merge_action"].value_counts(dropna=False).rename_axis("merge_action").reset_index(name="states")
    report = f"""# CRYPTO A7AK-LV2 Response Merge Audit

Generated: {summary["generated_at"]}

## Decision

```text
{summary["decision"]}
```

LV2 computes train-only response vectors for A7AK raw latent states and proposes response-similar merge groups. It does not run search, replay, or promotion.

## Summary

```json
{json.dumps(summary, indent=2, sort_keys=True)}
```

## Merge Action Counts

{md_table(action_counts)}

## Largest Merge Groups

{md_table(largest_groups, max_rows=25)}

## Top Response States

{md_table(response.sort_values("train_rows", ascending=False).head(30), max_rows=30)}

## Top Similarity Edges

{md_table(edges.sort_values("response_cosine_similarity", ascending=False).head(30), max_rows=30)}

## Relaxed Candidate Merge Suggestions

These are not applied to the merge map. They are review candidates only.

{md_table(relaxed.head(30), max_rows=30)}

## Largest Unseen Train-Hold States

{md_table(unseen.head(30), max_rows=30)}

## Bias Boundary Audit

{md_table(bias)}

## Boundary

```text
AUTHORIZED NEXT:
  A7AK-LV3 global vs age-neutral vs latent-neutral field-family smoke design

NOT AUTHORIZED:
  alpha search
  replay promotion
  alpha proof
  shadow / paper / live

LEAKAGE RULE:
  response vectors are fit on train_2024 only
  validation/recent are not used for merge assignment
  May is unavailable and not used
```
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lv1_manifest = read_json(LV1_MANIFEST)

    lv1 = pd.read_parquet(LV1_PANEL, columns=LV1_COLUMNS, engine="pyarrow")
    lv1["timestamp"] = pd.to_datetime(lv1["timestamp"], utc=True)
    labels = load_forward_labels()
    panel = lv1.merge(labels, on=["symbol", "timestamp"], how="left")

    response = build_response_vectors(panel)
    merge_map, registry, edges, eligible = build_merge_audit(response)
    all_states = pd.read_csv(ROOT / "runtime" / "a7ak_lv1_latent_state_feature_build" / "a7ak_lv1_raw_state_registry.csv")
    unseen = unseen_state_policy(all_states, response)
    relaxed = relaxed_merge_suggestions(edges)

    blockers: list[str] = []
    if lv1_manifest.get("decision") != "PASS_A7AK_LV1_LATENT_STATE_FEATURES_READY":
        blockers.append("lv1_not_passed")
    if response.empty:
        blockers.append("empty_train_response_vectors")
    if int(response["label_rows_24h"].sum()) == 0:
        blockers.append("empty_train_forward_labels")

    summary = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AK_LV2_RESPONSE_MERGE_AUDIT_READY",
        "input_lv1_panel": str(LV1_PANEL),
        "input_base_panel_root": str(BASE_PANEL_ROOT),
        "train_window": "2024-01-01 00:00 UTC .. 2024-12-31 23:00 UTC",
        "raw_states_total_lv1": int(all_states["raw_latent_state_id"].nunique()),
        "train_response_states": int(response["raw_latent_state_id"].nunique()),
        "merge_eligible_states": int(merge_map["merge_eligible"].fillna(False).sum()) if not merge_map.empty else 0,
        "merged_groups": int(registry["merged_latent_state_id"].nunique()) if not registry.empty else 0,
        "multi_state_merge_groups": int((registry["raw_state_count"] > 1).sum()) if not registry.empty else 0,
        "states_in_multi_state_groups": int(registry.loc[registry["raw_state_count"] > 1, "raw_state_count"].sum()) if not registry.empty else 0,
        "relaxed_candidate_merge_pairs_ge_0_88": int(len(relaxed)),
        "insufficient_train_support_states": int((merge_map["merge_action"] == "insufficient_train_support").sum()) if not merge_map.empty else 0,
        "unseen_train_hold_states": int(len(unseen)),
        "age_lt30_states_with_train_response": int(response.loc[response["age_lt30_train_share"] > 0, "raw_latent_state_id"].nunique()),
        "executes_response_merge_audit": True,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_lv3_neutral_smoke_design": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": blockers,
        "warnings": [
            "Forward labels are used only inside train_2024 to estimate state response vectors",
            "LV2 response vectors are diagnostics and not trading replay evidence",
            "States unseen in train are held for LV3 mapping rather than force-merged",
            "Cost/lag fields in LV2 are response proxies, not executable book-level cost proof",
        ],
    }
    if blockers:
        summary["decision"] = "HOLD_A7AK_LV2_RESPONSE_MERGE_AUDIT_BLOCKED"
        summary["authorizes_lv3_neutral_smoke_design"] = False

    bias = build_bias_audit(summary)

    write_json(OUT_DIR / "a7ak_lv2_manifest.json", summary)
    response.to_csv(OUT_DIR / "a7ak_lv2_state_response_vectors.csv", index=False)
    merge_map.to_csv(OUT_DIR / "a7ak_lv2_state_merge_map.csv", index=False)
    registry.to_csv(OUT_DIR / "a7ak_lv2_merge_group_registry.csv", index=False)
    edges.to_csv(OUT_DIR / "a7ak_lv2_response_similarity_edges.csv", index=False)
    relaxed.to_csv(OUT_DIR / "a7ak_lv2_relaxed_merge_suggestions.csv", index=False)
    unseen.to_csv(OUT_DIR / "a7ak_lv2_unseen_state_policy.csv", index=False)
    bias.to_csv(OUT_DIR / "a7ak_lv2_bias_boundary_audit.csv", index=False)

    DATA_METADATA_DIR.mkdir(parents=True, exist_ok=True)
    merge_map.to_csv(DATA_MERGE_MAP, index=False)
    response.to_csv(DATA_RESPONSE_VECTORS, index=False)

    build_report(summary, response, merge_map, registry, edges, relaxed, unseen, bias)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
