from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path("runtime/a7v3s1_accepted_candidate_validation_20260613")
DEFAULT_RUNTIME = Path("runtime/a7v3s2_control_variant_audit_20260613")
DEFAULT_REPORT = Path("reports/CRYPTO_A7V3S2_CONTROL_VARIANT_AUDIT_20260613.md")

OOS_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
STRESS_SPLIT = "known_may2026_stress"
CONTROL_VARIANTS = ["one_bar_lag", "stale_168h", "time_shuffle", "symbol_shuffle"]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def finite_float(value: object, default: float = math.nan) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def md_table(frame: pd.DataFrame, max_rows: int = 30) -> str:
    if frame.empty:
        return "_empty_"
    return frame.head(max_rows).to_markdown(index=False)


def get_metric(rows: pd.DataFrame, variant: str, split: str, metric: str) -> float:
    matched = rows[(rows["variant"] == variant) & (rows["split"] == split)]
    if matched.empty or metric not in matched:
        return math.nan
    return finite_float(matched.iloc[0][metric])


def audit_candidate(row: pd.Series, split_matrix: pd.DataFrame) -> dict[str, object]:
    blueprint_id = str(row["blueprint_id"])
    horizon_h = int(row["horizon_h"])
    rows = split_matrix[
        (split_matrix["blueprint_id"].astype(str) == blueprint_id)
        & (split_matrix["horizon_h"].astype(int) == horizon_h)
    ].copy()

    dominated_splits: list[str] = []
    shuffle_dominated_splits: list[str] = []
    lag_dominated_splits: list[str] = []
    oos_original_floor: list[float] = []
    oos_control_margin: list[float] = []
    sign_flip_positive_splits: list[str] = []

    for split in OOS_SPLITS:
        original_floor = get_metric(rows, "original", split, "nonoverlap_floor_sortino")
        oos_original_floor.append(original_floor)
        control_floors = {
            variant: get_metric(rows, variant, split, "nonoverlap_floor_sortino")
            for variant in CONTROL_VARIANTS
        }
        finite_controls = {k: v for k, v in control_floors.items() if math.isfinite(v)}
        max_control = max(finite_controls.values()) if finite_controls else math.nan
        if math.isfinite(original_floor) and math.isfinite(max_control):
            margin = original_floor - max_control
            oos_control_margin.append(margin)
            if max_control >= original_floor:
                dominated_splits.append(split)
        if math.isfinite(control_floors.get("time_shuffle", math.nan)) and control_floors["time_shuffle"] >= original_floor:
            shuffle_dominated_splits.append(split)
        if math.isfinite(control_floors.get("symbol_shuffle", math.nan)) and control_floors["symbol_shuffle"] >= original_floor:
            shuffle_dominated_splits.append(split)
        lag_max = max(
            [control_floors.get("one_bar_lag", math.nan), control_floors.get("stale_168h", math.nan)]
        )
        if math.isfinite(lag_max) and lag_max >= original_floor:
            lag_dominated_splits.append(split)
        sign_flip_sortino = get_metric(rows, "sign_flip", split, "sortino")
        if math.isfinite(sign_flip_sortino) and sign_flip_sortino > 0:
            sign_flip_positive_splits.append(split)

    stress_floor = get_metric(rows, "original", STRESS_SPLIT, "nonoverlap_floor_sortino")
    stress_sortino = get_metric(rows, "original", STRESS_SPLIT, "sortino")
    min_oos_original_floor = min([v for v in oos_original_floor if math.isfinite(v)], default=math.nan)
    median_oos_control_margin = (
        float(pd.Series(oos_control_margin).median()) if oos_control_margin else math.nan
    )

    flags: list[str] = []
    if not math.isfinite(min_oos_original_floor) or min_oos_original_floor <= 0:
        flags.append("original_oos_floor_not_positive")
    if len(dominated_splits) >= 2:
        flags.append("control_dominated_oos_majority")
    elif dominated_splits:
        flags.append("control_dominated_oos_partial")
    if shuffle_dominated_splits:
        flags.append("shuffle_dominated")
    if lag_dominated_splits:
        flags.append("lag_or_stale_dominated")
    if sign_flip_positive_splits:
        flags.append("sign_flip_positive")
    if not math.isfinite(stress_floor) or stress_floor <= 0:
        flags.append("stress_floor_not_positive")

    if "original_oos_floor_not_positive" in flags or "control_dominated_oos_majority" in flags:
        decision = "HOLD_CONTROL_DOMINATED"
    elif "stress_floor_not_positive" in flags:
        decision = "HOLD_STRESS_WEAK"
    elif "shuffle_dominated" in flags or "lag_or_stale_dominated" in flags:
        decision = "HOLD_CONTROL_REVIEW"
    else:
        decision = "ADVANCE_DEEP_REPLAY"

    return {
        "blueprint_id": blueprint_id,
        "semantic_pair": row.get("semantic_pair"),
        "motif": row.get("motif"),
        "horizon_h": horizon_h,
        "expression": row.get("expression"),
        "validation_decision_in": row.get("validation_decision"),
        "min_oos_original_floor_sortino": min_oos_original_floor,
        "median_oos_control_margin_floor_sortino": median_oos_control_margin,
        "stress_floor_sortino": stress_floor,
        "stress_sortino": stress_sortino,
        "dominated_oos_split_count": len(dominated_splits),
        "dominated_oos_splits": ";".join(dominated_splits),
        "shuffle_dominated_splits": ";".join(sorted(set(shuffle_dominated_splits))),
        "lag_dominated_splits": ";".join(sorted(set(lag_dominated_splits))),
        "sign_flip_positive_splits": ";".join(sign_flip_positive_splits),
        "control_audit_flags": ";".join(flags),
        "control_audit_decision": decision,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    args.runtime.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)

    queue = pd.read_csv(args.input / "a7v3s1_next_deep_validation_queue.csv")
    split_matrix = pd.read_csv(args.input / "a7v3s1_split_window_matrix.csv")
    audits = pd.DataFrame([audit_candidate(row, split_matrix) for _, row in queue.iterrows()])

    decision_summary = audits["control_audit_decision"].value_counts().rename_axis("decision").reset_index(name="count")
    flag_summary = (
        audits.assign(control_audit_flags=audits["control_audit_flags"].fillna("").str.split(";"))
        .explode("control_audit_flags")
        .query("control_audit_flags != ''")
        .groupby("control_audit_flags", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    pair_summary = (
        audits.groupby(["semantic_pair", "motif", "control_audit_decision"], dropna=False)
        .agg(
            candidates=("blueprint_id", "count"),
            median_control_margin=("median_oos_control_margin_floor_sortino", "median"),
            min_stress_floor=("stress_floor_sortino", "min"),
        )
        .reset_index()
        .sort_values(["candidates", "median_control_margin"], ascending=False)
    )
    next_queue = audits[audits["control_audit_decision"] == "ADVANCE_DEEP_REPLAY"].copy()

    outputs = {
        "control_audit": args.runtime / "a7v3s2_control_variant_audit.csv",
        "decision_summary": args.runtime / "a7v3s2_control_decision_summary.csv",
        "flag_summary": args.runtime / "a7v3s2_control_flag_summary.csv",
        "pair_summary": args.runtime / "a7v3s2_control_pair_summary.csv",
        "advance_queue": args.runtime / "a7v3s2_advance_deep_replay_queue.csv",
        "manifest": args.runtime / "a7v3s2_manifest.json",
    }
    audits.to_csv(outputs["control_audit"], index=False)
    decision_summary.to_csv(outputs["decision_summary"], index=False)
    flag_summary.to_csv(outputs["flag_summary"], index=False)
    pair_summary.to_csv(outputs["pair_summary"], index=False)
    next_queue.to_csv(outputs["advance_queue"], index=False)

    manifest = {
        "stage": "A7V3S2-CONTROL-VARIANT-AUDIT",
        "generated_at": now_utc(),
        "input": str(args.input),
        "runtime": str(args.runtime),
        "report": str(args.report),
        "candidate_count": int(len(audits)),
        "advance_deep_replay_count": int(len(next_queue)),
        "decision_counts": dict(zip(decision_summary["decision"], decision_summary["count"].astype(int))),
        "flag_counts": dict(zip(flag_summary["control_audit_flags"], flag_summary["count"].astype(int))) if not flag_summary.empty else {},
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_search_expansion": False,
        "outputs": {key: str(value) for key, value in outputs.items()},
    }
    outputs["manifest"].write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    report = [
        "# CRYPTO A7V3S2 Control Variant Audit",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        "`PASS_A7V3S2_CONTROL_VARIANT_AUDIT_BUILT`",
        "",
        "This audit checks whether reward-accepted numeric probes beat lag, stale, time-shuffle, symbol-shuffle, and sign-flip variants on OOS and stress windows.",
        "",
        "## Counts",
        "",
        f"- audited candidates: `{len(audits)}`",
        f"- advance deep replay: `{len(next_queue)}`",
        "",
        "## Control Decisions",
        "",
        md_table(decision_summary),
        "",
        "## Control Flags",
        "",
        md_table(flag_summary),
        "",
        "## Pair/Motif Summary",
        "",
        md_table(pair_summary),
        "",
        "## Candidate Audit",
        "",
        md_table(
            audits[
                [
                    "control_audit_decision",
                    "semantic_pair",
                    "motif",
                    "horizon_h",
                    "min_oos_original_floor_sortino",
                    "median_oos_control_margin_floor_sortino",
                    "stress_floor_sortino",
                    "dominated_oos_split_count",
                    "control_audit_flags",
                    "expression",
                ]
            ],
            max_rows=25,
        ),
        "",
        "## Interpretation",
        "",
        "- `ADVANCE_DEEP_REPLAY` requires positive OOS floor, no OOS majority control domination, and positive stress floor.",
        "- `HOLD_CONTROL_DOMINATED` means controls explain the candidate at least as well on most OOS windows or original OOS floor is non-positive.",
        "- `HOLD_STRESS_WEAK` means OOS may pass but May/stress floor fails.",
        "",
        "## Outputs",
        "",
    ]
    for key, value in outputs.items():
        report.append(f"- `{key}`: `{value}`")
    args.report.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
