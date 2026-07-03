from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DEFAULT_RUNTIME = REPO / "runtime" / "a7mech1_oi_funding_mechanism_queue_20260703"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7MECH1_OI_FUNDING_MECHANISM_QUEUE_20260703.md"

BASE_FORMULA = "SafeDiv(TSRank(open_interest_value_last,336),CSRank(ZScore(Mean(funding_rate_delta_state_24h,72))))"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(frame: pd.DataFrame, max_rows: int = 80) -> str:
    if frame.empty:
        return "`<empty>`"
    view = frame.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```text\n" + view.to_string(index=False) + "\n```"


def clean_key(value: str) -> str:
    out = []
    for ch in value:
        out.append(ch if ch.isalnum() else "_")
    return "_".join("".join(out).strip("_").split("_"))[:96]


def add_row(rows: list[dict[str, Any]], seen: set[tuple[str, int]], formula: str, horizon: int, group: str, motif: str, note: str) -> None:
    key = (formula, horizon)
    if key in seen:
        return
    seen.add(key)
    idx = len(rows) + 1
    rows.append(
        {
            "source_blueprint_id": f"a7mech1_{idx:04d}",
            "blueprint_id": f"a7mech1_{idx:04d}_{clean_key(motif)}",
            "horizon_h": horizon,
            "expression": formula,
            "formula": formula,
            "candidate_role": "mechanism_ablation_or_controlled_expansion",
            "semantic_pair": "open_interest|funding_state",
            "motif": motif,
            "skeleton_key": clean_key(formula),
            "mechanism_group": group,
            "mechanism_note": note,
        }
    )


def build_rows() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    horizons = [4, 8, 24]
    oi_fields = ["open_interest_value_last", "open_interest_value_mean", "open_interest_last", "open_interest_mean"]
    oi_rank_windows = [168, 240, 336, 504]
    oi_mean_windows = [8, 12, 24, 48, 96]
    funding_windows = [24, 48, 72, 96, 168]

    # Base reproduction at the already strict-accepted horizon plus nearby horizons.
    for horizon in horizons:
        add_row(rows, seen, BASE_FORMULA, horizon, "base_reproduction", "base_safe_div_oi_funding", "base survivor formula")

    # Single-leg ablations: these test whether OI alone or funding alone carries the result.
    for horizon in horizons:
        for field in oi_fields:
            for window in [168, 336, 504]:
                add_row(rows, seen, f"TSRank({field},{window})", horizon, "single_leg_ablation", "oi_only_tsrank", "OI only")
                add_row(rows, seen, f"CSRank(TSRank({field},{window}))", horizon, "single_leg_ablation", "oi_only_cs_tsrank", "OI cross-sectional rank only")
        for window in funding_windows:
            add_row(rows, seen, f"CSRank(ZScore(Mean(funding_rate_delta_state_24h,{window})))", horizon, "single_leg_ablation", "funding_only_csrank_zmean", "funding state only")
            add_row(rows, seen, f"Sign(Mean(funding_rate_delta_state_24h,{window}))", horizon, "single_leg_ablation", "funding_only_sign", "funding sign only")

    # Controlled interaction expansion around the survivor mechanism.
    for horizon in horizons:
        for field in oi_fields:
            for oi_window in oi_rank_windows:
                oi_rank = f"TSRank({field},{oi_window})"
                oi_cs_rank = f"CSRank(TSRank({field},{oi_window}))"
                for funding_window in funding_windows:
                    funding_rank = f"CSRank(ZScore(Mean(funding_rate_delta_state_24h,{funding_window})))"
                    funding_abs = f"Abs(ZScore(Mean(funding_rate_delta_state_24h,{funding_window})))"
                    funding_sign = f"Sign(Mean(funding_rate_delta_state_24h,{funding_window}))"
                    add_row(rows, seen, f"SafeDiv({oi_rank},{funding_rank})", horizon, "interaction_expansion", "safe_div_rank_over_funding_rank", "base motif window/field expansion")
                    add_row(rows, seen, f"SafeDiv({oi_cs_rank},{funding_abs})", horizon, "interaction_expansion", "safe_div_cs_oi_over_abs_funding", "absolute funding denominator")
                    add_row(rows, seen, f"Mul({oi_cs_rank},{funding_sign})", horizon, "interaction_expansion", "oi_rank_times_funding_sign", "directional funding gate")
                    add_row(rows, seen, f"Sub({oi_cs_rank},{funding_rank})", horizon, "interaction_expansion", "oi_rank_minus_funding_rank", "rank spread")

    # OI level x basis sanity family: nearby mechanism from source-lag survivors.
    for horizon in horizons:
        for field in ["open_interest_last", "open_interest_mean"]:
            for oi_window in oi_mean_windows:
                for premium_window in [48, 168, 336, 504]:
                    add_row(
                        rows,
                        seen,
                        f"Mul(CSRank(Mean({field},{oi_window})),Sign(Mean(premium_close_bps,{premium_window})))",
                        horizon,
                        "nearby_survivor_family",
                        "oi_level_times_premium_sign",
                        "nearby OI x premium source-lag survivor family",
                    )

    frame = pd.DataFrame(rows)
    frame["mechanism_rank"] = range(1, len(frame) + 1)
    return frame


def build(runtime: Path, report: Path, max_rows: int) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    queue = build_rows().head(max_rows).copy()
    queue_path = runtime / "a7mech1_oi_funding_mechanism_queue.csv"
    queue.to_csv(queue_path, index=False)
    group_summary = queue.groupby("mechanism_group", dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)
    motif_summary = queue.groupby("motif", dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)
    group_summary.to_csv(runtime / "a7mech1_group_summary.csv", index=False)
    motif_summary.to_csv(runtime / "a7mech1_motif_summary.csv", index=False)
    manifest = {
        "stage": "A7MECH-1-OI-FUNDING-MECHANISM-QUEUE",
        "generated_at": now_utc(),
        "decision": "PASS_A7MECH1_MECHANISM_QUEUE_BUILT" if not queue.empty else "HOLD_A7MECH1_EMPTY_QUEUE",
        "runtime": str(runtime),
        "report": str(report),
        "queue_rows": int(queue.shape[0]),
        "output_queue": str(queue_path),
        "base_formula": BASE_FORMULA,
        "authorizes_source_lag_retest": bool(not queue.empty),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(runtime / "a7mech1_manifest.json", manifest)
    lines = [
        "# CRYPTO A7MECH-1 OI x Funding Mechanism Queue",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "This builds a controlled mechanism queue around the only strict A7REWARD-2 survivor. It is not alpha proof and does not authorize broad search.",
        "",
        "## Counts",
        "",
        f"- queue_rows: `{manifest['queue_rows']}`",
        "",
        "## Mechanism Groups",
        "",
        md_table(group_summary, 20),
        "",
        "## Motifs",
        "",
        md_table(motif_summary, 40),
        "",
        "## Queue Preview",
        "",
        md_table(queue[["blueprint_id", "horizon_h", "mechanism_group", "motif", "formula"]], 40),
        "",
        "## Next Required",
        "",
        "- Run source-lag retest before any strict reward evaluation.",
        "- Keep source publication proof gates active.",
        "",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--max-rows", type=int, default=180)
    args = parser.parse_args()
    manifest = build(args.runtime, args.report, args.max_rows)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
