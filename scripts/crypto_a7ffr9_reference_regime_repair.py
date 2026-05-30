from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffr9_reference_regime_repair"
REPORT = REPO / "reports" / "CRYPTO_A7FFR9_REFERENCE_REGIME_REPAIR_20260531.md"

A7FF44_MANIFEST = REPO / "runtime" / "a7ff44_deep_forensic" / "a7ff44_manifest.json"
A7FF44_QUEUE = REPO / "runtime" / "a7ff44_deep_forensic" / "a7ff44_bounded_deep_replay_queue.csv"
A7FF44_ROWS = REPO / "runtime" / "a7ff44_deep_forensic" / "a7ff44_row_forensic.csv"
A7FF42_STRICT = REPO / "runtime" / "a7ff42_family_balanced_numeric" / "a7ff42_control_strict_non_l7_clues.csv"

REFERENCE_FAMILY = "basis_premium_like|basis_premium_like"
REGIME_FAMILY = "regime_state|price_return_like"
FUNDING_BASIS_FAMILY = "funding_like|basis_premium_like"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def num(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series([float("nan")] * len(df), index=df.index)
    return pd.to_numeric(df[col], errors="coerce")


def normalize_queue(queue: pd.DataFrame) -> pd.DataFrame:
    if queue.empty:
        return queue
    out = queue.copy()
    if "semantic_pair" not in out.columns:
        out["semantic_pair"] = out.get("semantic_pair_confirmed", out.get("semantic_pair_r8", ""))
    if "motif" not in out.columns:
        out["motif"] = out.get("motif_confirmed", out.get("motif_r8", ""))
    for src, dst in [
        ("expression_confirmed", "expression"),
        ("control_ratio_premay_max_confirmed", "control_ratio_premay_max"),
        ("cost10_recent_oriented_confirmed", "cost10_recent_oriented"),
        ("one_bar_lag_recent_oriented_confirmed", "one_bar_lag_recent_oriented"),
        ("robust_min_tstat_floor_confirmed", "robust_min_tstat_floor"),
        ("robust_median_tstat_floor_confirmed", "robust_median_tstat_floor"),
    ]:
        if dst not in out.columns and src in out.columns:
            out[dst] = out[src]
    out["repair_source"] = "a7ff44_bounded_queue"
    return out


def regime_repair_candidates(strict_rows: pd.DataFrame) -> pd.DataFrame:
    if strict_rows.empty:
        return strict_rows
    reg = strict_rows.loc[strict_rows["semantic_pair"].astype(str).eq(REGIME_FAMILY)].copy()
    if reg.empty:
        return reg
    reg["control_ratio_premay_max"] = num(reg, "control_ratio_premay_max")
    reg["cost10_recent_oriented"] = num(reg, "cost10_recent_oriented")
    reg["one_bar_lag_recent_oriented"] = num(reg, "one_bar_lag_recent_oriented")
    reg["robust_min_tstat_floor"] = num(reg, "robust_min_tstat_floor")
    reg["robust_median_tstat_floor"] = num(reg, "robust_median_tstat_floor")
    reg["is_strict_regime_repair"] = (
        reg["control_ratio_premay_max"].lt(0.80)
        & reg["cost10_recent_oriented"].gt(0)
        & reg["one_bar_lag_recent_oriented"].gt(0)
        & reg["robust_min_tstat_floor"].gt(0)
        & reg["is_non_l7"].astype(str).str.lower().eq("true")
        & reg["is_numeric_clue"].astype(str).str.lower().eq("true")
    )
    reg["repair_class"] = "regime_hold"
    reg.loc[reg["is_strict_regime_repair"], "repair_class"] = "strict_regime_repair_candidate"
    reg.loc[
        reg["cost10_recent_oriented"].gt(0) & ~reg["is_strict_regime_repair"],
        "repair_class",
    ] = "diagnostic_cost_positive_but_not_strict"
    return reg.sort_values(
        ["is_strict_regime_repair", "cost10_recent_oriented", "robust_min_tstat_floor", "control_ratio_premay_max"],
        ascending=[False, False, False, True],
    )


def reference_policy(rows44: pd.DataFrame) -> pd.DataFrame:
    if rows44.empty:
        return pd.DataFrame()
    ref = rows44.loc[rows44["semantic_pair"].astype(str).eq(REFERENCE_FAMILY)].copy()
    if ref.empty:
        return pd.DataFrame(
            [
                {
                    "semantic_pair": REFERENCE_FAMILY,
                    "rows": 0,
                    "policy": "reference_cap_not_triggered",
                    "counts_as_replay_family": False,
                    "max_share_in_bounded_replay": 0.0,
                }
            ]
        )
    return pd.DataFrame(
        [
            {
                "semantic_pair": REFERENCE_FAMILY,
                "rows": int(len(ref)),
                "policy": "reference_only_capped_diagnostic",
                "counts_as_replay_family": False,
                "max_share_in_bounded_replay": 0.0,
                "reason": "basis self-pair confirms reference response but cannot be used as a non-reference replay family",
            }
        ]
    )


def select_repaired_queue(queue44: pd.DataFrame, reg_repair: pd.DataFrame) -> pd.DataFrame:
    funding = normalize_queue(queue44)
    funding = funding.loc[funding["semantic_pair"].astype(str).eq(FUNDING_BASIS_FAMILY)].copy()
    funding["r9_role"] = "carry_forward_funding_basis_candidate"

    regime = reg_repair.loc[reg_repair.get("is_strict_regime_repair", False).astype(bool)].copy()
    if not regime.empty:
        regime["r9_role"] = "repaired_regime_candidate"
        regime["repair_source"] = "a7ff42_strict_non_l7_regime_pool"
    keep_cols = [
        "blueprint_id",
        "expression",
        "semantic_pair",
        "motif",
        "label_family",
        "label_horizon_h",
        "control_ratio_premay_max",
        "cost10_recent_oriented",
        "one_bar_lag_recent_oriented",
        "robust_min_tstat_floor",
        "robust_median_tstat_floor",
        "repair_source",
        "r9_role",
    ]
    parts = []
    for part in [funding, regime]:
        if part.empty:
            continue
        for col in keep_cols:
            if col not in part.columns:
                part[col] = pd.NA
        parts.append(part[keep_cols])
    if not parts:
        return pd.DataFrame(columns=keep_cols)
    out = pd.concat(parts, ignore_index=True)
    out = out.drop_duplicates(subset=["blueprint_id", "label_family", "label_horizon_h", "semantic_pair", "motif"])
    out["control_ratio_premay_max"] = num(out, "control_ratio_premay_max")
    out["cost10_recent_oriented"] = num(out, "cost10_recent_oriented")
    out["robust_min_tstat_floor"] = num(out, "robust_min_tstat_floor")
    out = out.sort_values(
        ["semantic_pair", "cost10_recent_oriented", "robust_min_tstat_floor", "control_ratio_premay_max"],
        ascending=[True, False, False, True],
    )
    return out


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    f44 = read_json(A7FF44_MANIFEST)
    if f44.get("decision") != "HOLD_A7FF44_DEEP_FORENSIC_CONCENTRATION_OR_BREADTH_FAIL":
        raise SystemExit(f"A7FF-44 state does not require R9 repair: {f44.get('decision')}")

    rows44 = read_csv(A7FF44_ROWS)
    queue44 = read_csv(A7FF44_QUEUE)
    strict42 = read_csv(A7FF42_STRICT)
    reg = regime_repair_candidates(strict42)
    ref_policy = reference_policy(rows44)
    repaired_queue = select_repaired_queue(queue44, reg)

    family_summary = (
        repaired_queue.groupby("semantic_pair", dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            blueprints=("blueprint_id", "nunique"),
            motifs=("motif", "nunique"),
            labels=("label_family", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            max_control_ratio=("control_ratio_premay_max", "max"),
            min_cost10=("cost10_recent_oriented", "min"),
            min_robust_floor=("robust_min_tstat_floor", "min"),
        )
        .reset_index()
        if not repaired_queue.empty
        else pd.DataFrame()
    )

    reg_summary = pd.DataFrame(
        [
            {
                "metric": "regime_total_strict_pool_rows",
                "value": int(len(reg)),
            },
            {
                "metric": "regime_strict_repair_rows",
                "value": int(reg.get("is_strict_regime_repair", pd.Series(dtype=bool)).sum()) if not reg.empty else 0,
            },
            {
                "metric": "regime_strict_repair_blueprints",
                "value": int(reg.loc[reg.get("is_strict_regime_repair", False).astype(bool), "blueprint_id"].nunique())
                if not reg.empty
                else 0,
            },
        ]
    )

    ref_policy.to_csv(RUNTIME / "a7ffr9_reference_cap_policy.csv", index=False)
    reg.to_csv(RUNTIME / "a7ffr9_regime_repair_candidates.csv", index=False)
    repaired_queue.to_csv(RUNTIME / "a7ffr9_repaired_candidate_queue.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffr9_repaired_queue_family_summary.csv", index=False)
    reg_summary.to_csv(RUNTIME / "a7ffr9_regime_repair_summary.csv", index=False)

    family_count = int(repaired_queue["semantic_pair"].nunique()) if not repaired_queue.empty else 0
    queue_count = int(len(repaired_queue))
    regime_rows = int(reg.get("is_strict_regime_repair", pd.Series(dtype=bool)).sum()) if not reg.empty else 0
    regime_blueprints = (
        int(reg.loc[reg.get("is_strict_regime_repair", False).astype(bool), "blueprint_id"].nunique()) if not reg.empty else 0
    )
    top_share = float(repaired_queue["semantic_pair"].value_counts(normalize=True).iloc[0]) if queue_count else 1.0

    blockers: list[str] = []
    warnings: list[str] = []
    if queue_count < 6:
        blockers.append("repaired_queue_count_below_6")
    if family_count < 2:
        blockers.append("repaired_queue_family_count_below_2")
    if regime_rows < 2 or regime_blueprints < 2:
        blockers.append("regime_repair_breadth_below_2")
    if top_share > 0.75:
        blockers.append("top_family_share_above_0p75")
    if top_share > 0.60:
        warnings.append("top_family_share_above_0p60")

    decision = (
        "PASS_A7FFR9_REFERENCE_REGIME_REPAIR_READY_FOR_A7FF45_BOUNDED_DEEP_REPLAY_NO_SEARCH_AUTH"
        if not blockers
        else "HOLD_A7FFR9_REFERENCE_REGIME_REPAIR_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-R9",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ff44_decision": f44.get("decision"),
        "blockers": blockers,
        "warnings": warnings,
        "reference_policy": "basis self-pair capped as reference-only diagnostic",
        "regime_repair_rows": regime_rows,
        "regime_repair_blueprints": regime_blueprints,
        "repaired_queue_count": queue_count,
        "repaired_queue_family_count": family_count,
        "repaired_queue_top_family_share": top_share,
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff45_bounded_deep_replay": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffr9_manifest.json", manifest)
    write_json(RUNTIME / "a7ffr9_decision_record.json", manifest)

    lines = [
        "# CRYPTO A7FF-R9 REFERENCE / REGIME REPAIR",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-R9 does not generate formulas, run numeric probes, or run replay. It repairs the A7FF-44 bounded queue by capping the basis self-pair reference family and restoring strict regime/price candidates from the A7FF-42 strict non-L7 pool.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Reference Cap Policy",
        "",
        md_table(ref_policy),
        "",
        "## Regime Repair Summary",
        "",
        md_table(reg_summary),
        "",
        "## Repaired Queue Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Repaired Candidate Queue",
        "",
        md_table(repaired_queue),
        "",
        "## Regime Repair Candidates",
        "",
        md_table(
            reg[
                [
                    "blueprint_id",
                    "expression",
                    "motif",
                    "label_family",
                    "label_horizon_h",
                    "control_ratio_premay_max",
                    "cost10_recent_oriented",
                    "one_bar_lag_recent_oriented",
                    "robust_min_tstat_floor",
                    "repair_class",
                ]
            ]
            if not reg.empty
            else reg
        ),
        "",
        "## Boundary",
        "",
        "```text",
        "numeric probe executed: false",
        "replay executed: false",
        "search executed: false",
        "May used: false",
        "alpha proof / shadow / paper / live: false",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
