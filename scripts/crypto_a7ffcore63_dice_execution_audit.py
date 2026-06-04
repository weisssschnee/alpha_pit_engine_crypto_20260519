from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
EXTERNAL = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore59_numeric_repair_execution_20260604")

CORE62 = REPO / "runtime" / "a7ffcore62_dice_batch_dryrun"
RUNTIME = REPO / "runtime" / "a7ffcore63_dice_execution_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE63_DICE_EXECUTION_AUDIT_20260605.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 60) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```csv\n" + view.to_csv(index=False) + "```"


def collect_external(name: str, shard_count: int = 6) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for shard in range(shard_count):
        path = EXTERNAL / f"shard_{shard:02d}" / f"a7ffcore59_s{shard:02d}_{name}.csv"
        frame = read_csv(path)
        if not frame.empty:
            frame["core59_shard"] = f"s{shard:02d}"
            frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def finite_num(series: pd.Series, default: float = 0.0) -> pd.Series:
    out = pd.to_numeric(series, errors="coerce")
    return out.replace([math.inf, -math.inf], pd.NA).fillna(default)


def build_core62b_score(dice: pd.DataFrame) -> pd.DataFrame:
    b = dice[dice["dice_arm"].eq("CORE62B_target_near_miss_repair")].copy()
    if b.empty:
        return b

    b["premay_positive_split_count"] = finite_num(b["premay_positive_split_count"])
    b["control_ratio"] = finite_num(b["control_ratio"], 999.0)
    b["cost10"] = finite_num(b["cost10"], -999.0)
    b["control_margin"] = (1.0 - b["control_ratio"]).clip(lower=-2, upper=1)
    b["cost10_positive"] = b["cost10"].gt(0)
    b["lag_fragile"] = b["core61_reason"].astype(str).str.contains("lag_fragile", case=False, na=False)
    b["control_clean"] = b["control_ratio"].lt(1.0)

    # Score is intentionally simple and inspectable. It ranks repair dice, not alpha candidates.
    b["repair_score"] = (
        0.40 * (b["premay_positive_split_count"].clip(0, 3) / 3.0)
        + 0.30 * b["control_margin"].clip(0, 1)
        + 0.20 * b["cost10"].clip(0, 0.20) / 0.20
        + 0.10 * b["lag_fragile"].astype(float)
    )
    b["core63_action"] = "hold"
    b.loc[b["control_clean"] & b["cost10_positive"] & b["lag_fragile"], "core63_action"] = "entry_lag_repair_numeric_retest"
    b.loc[b["control_clean"] & b["cost10_positive"] & ~b["lag_fragile"], "core63_action"] = "target_gate_retest"
    b.loc[~b["control_clean"], "core63_action"] = "reject_control_not_clean"
    b.loc[~b["cost10_positive"], "core63_action"] = "reject_cost10_not_positive"

    b = b.sort_values(
        ["core63_action", "repair_score", "control_ratio", "cost10"],
        ascending=[True, False, True, False],
    )
    b["core63_selected_for_retest"] = False
    eligible = b[b["core63_action"].isin(["entry_lag_repair_numeric_retest", "target_gate_retest"])].copy()
    # Keep a bounded but non-trivial dice throw: diverse semantic pairs first, then best remaining.
    selected_idx: list[int] = []
    seen_pairs: set[str] = set()
    for idx, row in eligible.iterrows():
        pair = str(row.get("semantic_pair"))
        if pair in seen_pairs:
            continue
        selected_idx.append(idx)
        seen_pairs.add(pair)
        if len(selected_idx) >= 12:
            break
    for idx, _ in eligible.iterrows():
        if idx in selected_idx:
            continue
        selected_idx.append(idx)
        if len(selected_idx) >= 24:
            break
    b.loc[selected_idx, "core63_selected_for_retest"] = True
    return b


def build_core62c_audit(material: pd.DataFrame, dice: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    c_tasks = dice[dice["dice_arm"].eq("CORE62C_materialization_repair")].copy()
    if c_tasks.empty or material.empty:
        return c_tasks, pd.DataFrame()

    mat = material[material["semantic_pair"].isin(c_tasks["semantic_pair"].dropna().astype(str))].copy()
    for col in ["finite_share", "nonzero_share", "std_value"]:
        mat[col] = finite_num(mat[col])
    mat["eval_success_bool"] = mat["eval_success"].fillna(False).astype(bool)
    mat["activity_ok_bool"] = mat["activity_ok"].fillna(False).astype(bool)
    mat["zero_finite"] = mat["finite_share"].le(0)
    mat["low_finite"] = mat["finite_share"].lt(0.05)
    mat["uses_funding_rate"] = mat["expression"].astype(str).str.contains("funding_rate", na=False)
    mat["uses_positioning"] = mat["expression"].astype(str).str.contains("long_short|position", case=False, regex=True, na=False)

    pair_audit = mat.groupby("semantic_pair", dropna=False).agg(
        formulas=("blueprint_id", "nunique"),
        rows=("blueprint_id", "size"),
        eval_success_rate=("eval_success_bool", "mean"),
        activity_ok_rows=("activity_ok_bool", "sum"),
        median_finite_share=("finite_share", "median"),
        median_nonzero_share=("nonzero_share", "median"),
        zero_finite_rate=("zero_finite", "mean"),
        low_finite_rate=("low_finite", "mean"),
        uses_funding_rate=("uses_funding_rate", "mean"),
        uses_positioning=("uses_positioning", "mean"),
    ).reset_index()

    def diagnose(row: pd.Series) -> str:
        if row["eval_success_rate"] < 1.0:
            return "eval_error_first"
        if row["median_finite_share"] < 0.01 and row["uses_funding_rate"] > 0:
            return "funding_event_sparse_state_alignment"
        if row["median_finite_share"] < 0.05:
            return "low_finite_share_transform_or_panel_alignment"
        if row["activity_ok_rows"] <= 0:
            return "activity_threshold_too_strict_or_low_variance"
        return "materialization_ok"

    pair_audit["diagnosis"] = pair_audit.apply(diagnose, axis=1)
    pair_audit["core63_repair"] = pair_audit["diagnosis"].map(
        {
            "funding_event_sparse_state_alignment": "build PIT funding_state carry contract and retest funding interactions",
            "low_finite_share_transform_or_panel_alignment": "audit field availability and min_period/window transform policy",
            "eval_error_first": "fix evaluator/operator error before any retest",
            "activity_threshold_too_strict_or_low_variance": "separate true zero activity from overly strict activity gate",
            "materialization_ok": "release pair from materialization hold",
        }
    )
    sample_cols = [
        "blueprint_id", "semantic_pair", "motif", "expression", "finite_share",
        "nonzero_share", "std_value", "activity_ok", "error",
    ]
    sample = mat.sort_values(["semantic_pair", "finite_share"], ascending=[True, False])[
        [c for c in sample_cols if c in mat.columns]
    ].head(80)
    return pair_audit, sample


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    dice = read_csv(CORE62 / "core62_dice_batch_queue.csv")
    if dice.empty:
        raise SystemExit("CORE63 requires CORE62 dice batch queue")
    material = collect_external("materialization_metrics")

    core62b = build_core62b_score(dice)
    core62c_pair, core62c_sample = build_core62c_audit(material, dice)

    core62b.to_csv(RUNTIME / "core63_target_near_miss_repair_score.csv", index=False)
    core62b[core62b.get("core63_selected_for_retest", False).eq(True)].to_csv(
        RUNTIME / "core63_selected_numeric_retest_queue.csv", index=False
    )
    core62c_pair.to_csv(RUNTIME / "core63_materialization_pair_diagnosis.csv", index=False)
    core62c_sample.to_csv(RUNTIME / "core63_materialization_formula_samples.csv", index=False)

    selected = core62b[core62b.get("core63_selected_for_retest", False).eq(True)].copy()
    b_summary = core62b.groupby(["semantic_pair", "core63_action"], dropna=False).agg(
        rows=("blueprint_id", "size"),
        selected=("core63_selected_for_retest", "sum"),
        median_repair_score=("repair_score", "median"),
        median_control_ratio=("control_ratio", "median"),
        min_cost10=("cost10", "min"),
        max_cost10=("cost10", "max"),
    ).reset_index().sort_values(["selected", "rows"], ascending=False)
    b_summary.to_csv(RUNTIME / "core63_target_near_miss_summary.csv", index=False)

    blockers: list[str] = []
    selected_count = int(len(selected))
    selected_pair_count = int(selected["semantic_pair"].nunique()) if selected_count else 0
    material_repair_count = int((core62c_pair["diagnosis"] != "materialization_ok").sum()) if not core62c_pair.empty else 0
    funding_sparse_count = int(core62c_pair["diagnosis"].eq("funding_event_sparse_state_alignment").sum()) if not core62c_pair.empty else 0

    if selected_count < 12:
        blockers.append("selected_retest_queue_lt_12")
    if selected_pair_count < 3:
        blockers.append("selected_semantic_pair_count_lt_3")
    if material_repair_count > 0:
        blockers.append("materialization_repairs_required")

    decision = "PASS_CORE63_DICE_EXECUTION_READY_FOR_RETEST_PACKAGE" if not blockers else "HOLD_CORE63_DICE_EXECUTION_REPAIRS_REQUIRED"
    manifest = {
        "stage": "A7FF-CORE63",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "input_dice_rows": int(len(dice)),
        "core62b_rows": int(len(core62b)),
        "selected_numeric_retest_rows": selected_count,
        "selected_semantic_pair_count": selected_pair_count,
        "core62c_pair_diagnosis_rows": int(len(core62c_pair)),
        "materialization_repair_pair_count": material_repair_count,
        "funding_sparse_state_alignment_pair_count": funding_sparse_count,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_core64_retest_package": selected_count >= 12,
        "authorizes_core64_materialization_fix": material_repair_count > 0,
    }
    write_json(RUNTIME / "core63_manifest.json", manifest)
    write_json(RUNTIME / "core63_decision_record.json", manifest)

    REPORT.write_text("\n".join([
        "# CRYPTO A7FF-CORE63 DICE EXECUTION AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE63 executes the CORE62 dice batch as an audit: it scores target near-miss rows and diagnoses materialization blockers. It does not run formula search, replay promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Target Near-Miss Summary",
        "",
        md_table(b_summary, 80),
        "",
        "## Selected Retest Queue",
        "",
        md_table(selected[[
            "blueprint_id", "semantic_pair", "motif", "label_family", "label_horizon_h",
            "core61_reason", "repair_score", "control_ratio", "cost10", "expression",
        ]] if not selected.empty else selected, 80),
        "",
        "## Materialization Pair Diagnosis",
        "",
        md_table(core62c_pair, 40),
        "",
        "## Materialization Formula Samples",
        "",
        md_table(core62c_sample, 40),
        "",
    ]), encoding="utf-8")

    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
