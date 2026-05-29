from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7ag3_numeric_replay_pilot import A7AG3Evaluator, classify_candidate, selected_fields, subset_columns  # noqa: E402
from scripts.crypto_a7ae1_label_adequacy_response_map import PRE_MAY_SPLITS, horizon_label, label_family_matrix  # noqa: E402
from scripts.crypto_a7al2l_fast_derived_replay_preflight import split_for_timestamps  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import (  # noqa: E402
    BASE_DIR,
    LATENT_PANEL,
    load_base,
    load_latent_numeric,
    parquet_schema,
    strict_symbols,
)


RUNTIME = REPO / "runtime" / "a7ag5_clue_forensic_audit"
REPORT = REPO / "reports" / "CRYPTO_A7AG5_CLUE_FORENSIC_AUDIT_20260529.md"

A7AG4_MANIFEST = REPO / "runtime" / "a7ag4_clue_forensic_contract" / "a7ag4_manifest.json"
A7AG4_CLUES = REPO / "runtime" / "a7ag4_clue_forensic_contract" / "a7ag4_role_classified_clues.csv"

TRANSLATION_LABELS = [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L2_BTC_ETH_beta_residual_return",
    "L5_vol_adjusted_return",
    "L6_downside_avoidance",
]
CONCENTRATION_GROUPS = ["symbol", "month", "raw_latent_state_id", "age_bucket_dynamic", "liquidity_state"]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
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


def load_latent_groups(symbols: list[str], timestamps: pd.DatetimeIndex, group_cols: list[str]) -> dict[str, np.ndarray]:
    cols = ["symbol", "timestamp"] + group_cols
    frame = pd.read_parquet(LATENT_PANEL, columns=cols)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame[frame["symbol"].isin(symbols)].sort_values(["symbol", "timestamp"])
    out: dict[str, np.ndarray] = {}
    for col in group_cols:
        rows = []
        for symbol in symbols:
            sub = frame.loc[frame["symbol"].eq(symbol), ["timestamp", col]].drop_duplicates("timestamp")
            sub = sub.set_index("timestamp").reindex(timestamps)
            rows.append(sub[col].astype(object).to_numpy())
        out[col] = np.vstack(rows)
    return out


def contribution_matrix(signal: np.ndarray, label: np.ndarray, orientation: float) -> np.ndarray:
    valid = np.isfinite(signal) & np.isfinite(label)
    valid_counts = valid.sum(axis=0)
    enough = valid_counts >= 30
    ranks = pd.DataFrame(np.where(valid, signal, np.nan)).rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)
    top = valid & enough.reshape(1, -1) & (ranks >= 0.90)
    bottom = valid & enough.reshape(1, -1) & (ranks <= 0.10)
    top_count = top.sum(axis=0)
    bottom_count = bottom.sum(axis=0)
    contrib = np.zeros_like(signal, dtype=np.float64)
    ok_top = top & (top_count.reshape(1, -1) > 0)
    ok_bottom = bottom & (bottom_count.reshape(1, -1) > 0)
    top_denom = np.tile(top_count.reshape(1, -1), (signal.shape[0], 1))
    bottom_denom = np.tile(bottom_count.reshape(1, -1), (signal.shape[0], 1))
    contrib[ok_top] = label[ok_top] / top_denom[ok_top]
    contrib[ok_bottom] = -label[ok_bottom] / bottom_denom[ok_bottom]
    contrib *= float(orientation)
    contrib[~np.isfinite(contrib)] = 0.0
    return contrib


def top_abs_share_by_key(values: np.ndarray, keys: np.ndarray, mask: np.ndarray) -> tuple[str, float]:
    x = np.abs(values[mask])
    k = keys[mask].astype(str)
    total = float(np.nansum(x))
    if total <= 0 or len(x) == 0:
        return "", np.nan
    frame = pd.DataFrame({"key": k, "abs_contrib": x})
    agg = frame.groupby("key", dropna=False)["abs_contrib"].sum().sort_values(ascending=False)
    return str(agg.index[0]), float(agg.iloc[0] / total)


def concentration_for_candidate(
    row: dict[str, Any],
    signal: np.ndarray,
    label: np.ndarray,
    timestamps: pd.DatetimeIndex,
    split: np.ndarray,
    symbols: list[str],
    latent_groups: dict[str, np.ndarray],
) -> dict[str, Any]:
    orientation = float(row.get("orientation_from_train", 1.0))
    contrib = contribution_matrix(signal, label, orientation)
    mask = np.isin(split, PRE_MAY_SPLITS)
    mask2d = np.tile(mask.reshape(1, -1), (len(symbols), 1)) & (np.abs(contrib) > 0)
    symbol_keys = np.tile(np.array(symbols, dtype=object).reshape(-1, 1), (1, len(timestamps)))
    month_keys = np.tile(np.array([ts.strftime("%Y-%m") for ts in timestamps], dtype=object).reshape(1, -1), (len(symbols), 1))
    out = {"candidate_id": row["candidate_id"]}
    for axis, keys in [("symbol", symbol_keys), ("month", month_keys), *[(name, matrix) for name, matrix in latent_groups.items()]]:
        key, share = top_abs_share_by_key(contrib, keys, mask2d)
        out[f"top_{axis}"] = key
        out[f"top_{axis}_abs_contrib_share"] = share
    out["concentration_blocker"] = bool(
        (np.isfinite(out.get("top_symbol_abs_contrib_share", np.nan)) and out["top_symbol_abs_contrib_share"] > 0.35)
        or (np.isfinite(out.get("top_month_abs_contrib_share", np.nan)) and out["top_month_abs_contrib_share"] > 0.50)
        or (np.isfinite(out.get("top_raw_latent_state_id_abs_contrib_share", np.nan)) and out["top_raw_latent_state_id_abs_contrib_share"] > 0.50)
    )
    return out


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ag4 = read_json(A7AG4_MANIFEST)
    if not a7ag4.get("authorizes_a7ag5_clue_forensic_audit"):
        raise SystemExit("A7AG-4 does not authorize A7AG-5")

    clues = pd.read_csv(A7AG4_CLUES)
    fields = selected_fields(clues)
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    base_fields = {field for field in fields if field in base_schema}
    latent_fields = {field for field in fields if field in latent_schema and field not in base_fields}
    missing = sorted(fields - base_fields - latent_fields)

    symbols = strict_symbols()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_fields))
    timestamps, numeric, _, full_timestamp_count = subset_columns(timestamps, numeric, {})
    split = split_for_timestamps(timestamps)
    latent_groups = load_latent_groups(loaded_symbols, timestamps, ["raw_latent_state_id", "age_bucket_dynamic", "liquidity_state"])
    evaluator = A7AG3Evaluator(numeric, {})

    horizons = sorted({int(x) for x in clues["label_horizon_h"].dropna().astype(int).tolist()} | {1, 24})
    raw_labels = {h: horizon_label(numeric["trade_close"], timestamps, split, h) for h in horizons}
    vol = numeric.get("realized_vol_168h", np.full_like(numeric["trade_close"], np.nan))
    liquidity_tier = latent_groups["liquidity_state"]

    label_cache: dict[tuple[str, int], np.ndarray] = {}
    for horizon in horizons:
        for label_family in TRANSLATION_LABELS:
            label_cache[(label_family, horizon)], _ = label_family_matrix(
                raw_labels[horizon],
                label_family,
                loaded_symbols,
                split,
                vol,
                liquidity_tier,
            )

    rng = np.random.default_rng(20260529)
    translation_rows: list[dict[str, Any]] = []
    concentration_rows: list[dict[str, Any]] = []
    for index, row in enumerate(clues.to_dict("records"), start=1):
        signal = evaluator.eval(str(row["expression"]))
        original_key = (str(row["label_family"]), int(row["label_horizon_h"]))
        original_label = label_cache[original_key]
        concentration_rows.append(
            {
                **{
                    "candidate_id": row["candidate_id"],
                    "track_id": row["track_id"],
                    "clue_role": row["clue_role"],
                    "seed_field": row["seed_field"],
                    "interaction_field": row["interaction_field"],
                },
                **concentration_for_candidate(row, signal, original_label, timestamps, split, loaded_symbols, latent_groups),
            }
        )
        for label_family in TRANSLATION_LABELS:
            key = (label_family, int(row["label_horizon_h"]))
            result = classify_candidate(row, signal, label_cache[key], split, rng)
            translation_rows.append(
                {
                    "candidate_id": row["candidate_id"],
                    "track_id": row["track_id"],
                    "clue_role": row["clue_role"],
                    "original_label_family": row["label_family"],
                    "translation_label_family": label_family,
                    "label_horizon_h": int(row["label_horizon_h"]),
                    "decision": result["decision"],
                    "control_ratio_premay_max": result["control_ratio_premay_max"],
                    "cost5_recent_oriented": result["cost5_recent_oriented"],
                    "cost10_recent_oriented": result["cost10_recent_oriented"],
                    "cost20_recent_oriented": result["cost20_recent_oriented"],
                    "robust_median_tstat_floor": result["robust_median_tstat_floor"],
                    "premay_all_positive": result["premay_all_positive"],
                    "lag_ok": result["lag_ok"],
                }
            )
        if index % 8 == 0:
            print(f"[A7AG-5] audited {index}/{len(clues)} clues", flush=True)

    translation = pd.DataFrame(translation_rows)
    concentration = pd.DataFrame(concentration_rows)
    translation_summary = (
        translation.groupby(["clue_role", "translation_label_family"], dropna=False)
        .agg(
            rows=("candidate_id", "count"),
            replay_clues=("decision", lambda s: int((s == "A7AG3_NUMERIC_REPLAY_CLUE").sum())),
            median_control_ratio=("control_ratio_premay_max", "median"),
            cost20_survivors=("cost20_recent_oriented", lambda s: int((pd.to_numeric(s, errors="coerce") > 0).sum())),
        )
        .reset_index()
    )
    concentration_summary = (
        concentration.groupby(["clue_role"], dropna=False)
        .agg(
            candidates=("candidate_id", "count"),
            concentration_blockers=("concentration_blocker", "sum"),
            max_symbol_share=("top_symbol_abs_contrib_share", "max"),
            max_month_share=("top_month_abs_contrib_share", "max"),
            max_raw_latent_state_share=("top_raw_latent_state_id_abs_contrib_share", "max"),
        )
        .reset_index()
    )
    ordinary_translation_candidates = translation[
        translation["translation_label_family"].isin(["L0_raw_forward_return", "L1_cross_sectional_relative_return"])
        & translation["decision"].eq("A7AG3_NUMERIC_REPLAY_CLUE")
    ]
    cost20_original_survivors = int((pd.to_numeric(clues["cost20_recent_oriented"], errors="coerce") > 0).sum())
    concentration_blockers = int(concentration["concentration_blocker"].sum()) if not concentration.empty else 0

    decision = (
        "PASS_A7AG5_FORENSIC_AUDIT_READY_FOR_A7AG6_CONTRACT"
        if len(ordinary_translation_candidates) > 0 and concentration_blockers < len(concentration)
        else "HOLD_A7AG5_NO_ORDINARY_LABEL_TRANSLATION"
    )
    manifest = {
        "stage": "A7AG-5",
        "generated_at": now_utc(),
        "decision": decision,
        "input_a7ag4_decision": a7ag4.get("decision"),
        "executes_forensic_audit": True,
        "executes_formula_generation": False,
        "executes_search": False,
        "executes_training": False,
        "authorizes_a7ag6_contract": decision.startswith("PASS_"),
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may": False,
        "input_clue_count": int(len(clues)),
        "translation_rows": int(len(translation)),
        "ordinary_label_translation_clue_count": int(len(ordinary_translation_candidates)),
        "cost20_original_survivor_count": cost20_original_survivors,
        "concentration_blocker_count": concentration_blockers,
        "missing_fields": missing,
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "full_timestamps_before_subset": full_timestamp_count,
    }

    translation.to_csv(RUNTIME / "a7ag5_label_translation_audit.csv", index=False)
    translation_summary.to_csv(RUNTIME / "a7ag5_label_translation_summary.csv", index=False)
    concentration.to_csv(RUNTIME / "a7ag5_concentration_audit.csv", index=False)
    concentration_summary.to_csv(RUNTIME / "a7ag5_concentration_summary.csv", index=False)
    ordinary_translation_candidates.to_csv(RUNTIME / "a7ag5_ordinary_label_translation_candidates.csv", index=False)
    write_json(RUNTIME / "a7ag5_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ag5_authorization_matrix.json",
        {
            "A7AG-5": {"status": decision},
            "a7ag6_contract": {"authorized": bool(manifest["authorizes_a7ag6_contract"])},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AG-5 CLUE FORENSIC AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AG-5 checks whether A7AG-3/4 clues translate into ordinary labels and whether they are concentration-dominated. It does not generate formulas, search, train, or authorize proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label Translation Summary",
        "",
        md_table(translation_summary, 120),
        "",
        "## Concentration Summary",
        "",
        md_table(concentration_summary, 80),
        "",
        "## Ordinary Label Translation Candidates",
        "",
        md_table(ordinary_translation_candidates, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "A7AG-5 is forensic only.",
        "May is not used.",
        "No formula search, large search, alpha proof, shadow, paper, or live is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
