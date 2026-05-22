from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
A7S3_DIR = ROOT / "runtime" / "a7s3_metrics_clue_forensic"
OUT_DIR = ROOT / "runtime" / "a7s4_crowding_robustness_audit"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7S4_CROWDING_ROBUSTNESS_AUDIT_20260522.md"

RECENT = "recent_oos_2025H2_2026Apr"
VALIDATION = "validation_2025H1"
MAY = "fresh_may_2026"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def clean_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def symbol_loo(symbol_df: pd.DataFrame, split_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, metric in split_df[split_df["split"].isin([VALIDATION, RECENT, MAY])].iterrows():
        horizon = int(metric["horizon"])
        split = metric["split"]
        total = float(metric["net10"])
        part = symbol_df[(symbol_df["horizon"].eq(horizon)) & (symbol_df["split"].eq(split))]
        for _, row in part.iterrows():
            loo = total - float(row["net10"])
            rows.append(
                {
                    "horizon": horizon,
                    "split": split,
                    "left_out_symbol": row["symbol"],
                    "full_net10": clean_float(total),
                    "symbol_net10": clean_float(row["net10"]),
                    "loo_net10": clean_float(loo),
                    "loo_positive": bool(loo > 0),
                }
            )
    return pd.DataFrame(rows)


def month_loo(month_df: pd.DataFrame, split_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, metric in split_df[split_df["split"].isin([RECENT, MAY])].iterrows():
        horizon = int(metric["horizon"])
        split = metric["split"]
        total = float(metric["net10"])
        if split == RECENT:
            months = month_df[(month_df["horizon"].eq(horizon)) & (month_df["month"] >= "2025-07") & (month_df["month"] <= "2026-04")]
        else:
            months = month_df[(month_df["horizon"].eq(horizon)) & (month_df["month"].eq("2026-05"))]
        for _, row in months.iterrows():
            loo = total - float(row["net10"])
            rows.append(
                {
                    "horizon": horizon,
                    "split": split,
                    "left_out_month": row["month"],
                    "full_net10": clean_float(total),
                    "month_net10": clean_float(row["net10"]),
                    "loo_net10": clean_float(loo),
                    "loo_positive": bool(loo > 0),
                }
            )
    return pd.DataFrame(rows)


def robustness_summary(split_df: pd.DataFrame, sym_loo: pd.DataFrame, mon_loo: pd.DataFrame, controls: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for horizon in sorted(split_df["horizon"].unique()):
        hsplit = split_df[split_df["horizon"].eq(horizon)].set_index("split")
        validation_net10 = float(hsplit.loc[VALIDATION, "net10"])
        validation_net20 = float(hsplit.loc[VALIDATION, "net20"])
        recent_net10 = float(hsplit.loc[RECENT, "net10"])
        recent_net20 = float(hsplit.loc[RECENT, "net20"])
        may_net10 = float(hsplit.loc[MAY, "net10"])
        lag1_recent = float(hsplit.loc[RECENT, "lag1_net10"])
        lag2_recent = float(hsplit.loc[RECENT, "lag2_net10"])
        lag3_recent = float(hsplit.loc[RECENT, "lag3_net10"])
        s_recent = sym_loo[(sym_loo["horizon"].eq(horizon)) & (sym_loo["split"].eq(RECENT))]
        s_may = sym_loo[(sym_loo["horizon"].eq(horizon)) & (sym_loo["split"].eq(MAY))]
        m_recent = mon_loo[(mon_loo["horizon"].eq(horizon)) & (mon_loo["split"].eq(RECENT))]
        recent_controls = controls[(controls["horizon"].eq(horizon)) & (controls["split"].eq(RECENT))]
        may_controls = controls[(controls["horizon"].eq(horizon)) & (controls["split"].eq(MAY))]
        rows.append(
            {
                "horizon": int(horizon),
                "validation_net10": clean_float(validation_net10),
                "validation_net20": clean_float(validation_net20),
                "recent_net10": clean_float(recent_net10),
                "recent_net20": clean_float(recent_net20),
                "may_net10": clean_float(may_net10),
                "lag1_recent_net10": clean_float(lag1_recent),
                "lag2_recent_net10": clean_float(lag2_recent),
                "lag3_recent_net10": clean_float(lag3_recent),
                "recent_symbol_loo_positive_rate": clean_float(s_recent["loo_positive"].mean()),
                "may_symbol_loo_positive_rate": clean_float(s_may["loo_positive"].mean()),
                "recent_month_loo_positive_rate": clean_float(m_recent["loo_positive"].mean()),
                "recent_min_symbol_loo_net10": clean_float(s_recent["loo_net10"].min()),
                "recent_min_month_loo_net10": clean_float(m_recent["loo_net10"].min()),
                "recent_control_positive_count": int((recent_controls["net10"] > 0).sum()),
                "may_control_positive_count": int((may_controls["net10"] > 0).sum()),
                "passes_validation_recent_10bps": bool(validation_net10 > 0 and recent_net10 > 0),
                "passes_validation_recent_20bps": bool(validation_net20 > 0 and recent_net20 > 0),
                "passes_lag_ladder_recent": bool(lag1_recent > 0 and lag2_recent > 0 and lag3_recent > 0),
                "passes_symbol_loo": bool(s_recent["loo_positive"].mean() >= 0.75 and s_recent["loo_net10"].min() > 0),
                "passes_month_loo": bool(m_recent["loo_positive"].mean() >= 0.70 and m_recent["loo_net10"].min() > 0),
                "passes_controls_recent": bool((recent_controls["net10"] > 0).sum() == 0),
                "passes_may_stress": bool(may_net10 > 0),
            }
        )
    return pd.DataFrame(rows)


def write_report(now: str, summary: pd.DataFrame, sym_loo: pd.DataFrame, mon_loo: pd.DataFrame, auth: dict[str, Any]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Crypto A7S-4 Crowding Robustness Audit",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{auth['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `robustness_from_a7s3_artifacts`",
        "- alpha proof / expanded replay / full search / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7S-4 tests whether the A7S-3 global-long-short crowding motif survives basic robustness gates. It uses A7S-3 artifacts and does not generate new formulas.",
        "",
        "## Robustness Summary",
        "",
        table(summary, max_rows=20),
        "",
        "## Recent Symbol Leave-One-Out",
        "",
        table(sym_loo[sym_loo["split"].eq(RECENT)].sort_values(["horizon", "loo_net10"]), max_rows=40),
        "",
        "## Recent Month Leave-One-Out",
        "",
        table(mon_loo[mon_loo["split"].eq(RECENT)].sort_values(["horizon", "loo_net10"]), max_rows=40),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(auth, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- Do not expand this crowding motif as an alpha candidate.",
        "- Keep global_long_short_account_ratio_zscore_168h as a candidate state/exposure feature.",
        "- If continuing metrics work, redesign around interaction/state use, not standalone crowding promotion.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    split_df = pd.read_csv(A7S3_DIR / "a7s3_clue_split_metrics.csv")
    symbol_df = pd.read_csv(A7S3_DIR / "a7s3_symbol_contribution.csv")
    month_df = pd.read_csv(A7S3_DIR / "a7s3_month_contribution.csv")
    controls = pd.read_csv(A7S3_DIR / "a7s3_control_detail.csv")
    sym_loo = symbol_loo(symbol_df, split_df)
    mon_loo = month_loo(month_df, split_df)
    summary = robustness_summary(split_df, sym_loo, mon_loo, controls)
    blockers: list[str] = []
    warnings: list[str] = ["single_formula_single_family"]
    if not bool(summary["passes_validation_recent_20bps"].all()):
        blockers.append("validation_recent_20bps_fail")
    if not bool(summary["passes_symbol_loo"].all()):
        blockers.append("symbol_loo_fail")
    if not bool(summary["passes_month_loo"].all()):
        blockers.append("month_loo_fail")
    if not bool(summary["passes_controls_recent"].all()):
        blockers.append("recent_control_positive")
    if int(summary["may_control_positive_count"].sum()) > 0:
        warnings.append("may_control_positive_stress_only")
    decision = "HOLD_A7S4_CROWDING_MOTIF_NOT_ROBUST"
    if not blockers:
        decision = "PASS_A7S4_CROWDING_MOTIF_ROBUSTNESS_FOR_STATE_USE_ONLY"
    auth = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "executes_search": False,
        "executes_replay": "robustness_from_a7s3_artifacts",
        "authorizes_state_feature_use": True,
        "authorizes_crowding_motif_expanded_replay": False,
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": [
            "Do not promote standalone global-long-short crowding motif",
            "Use metrics as state/exposure/interactions in later reset only",
            "No expanded replay from A7S-4",
        ],
    }
    summary.to_csv(OUT_DIR / "a7s4_robustness_summary.csv", index=False)
    sym_loo.to_csv(OUT_DIR / "a7s4_symbol_loo.csv", index=False)
    mon_loo.to_csv(OUT_DIR / "a7s4_month_loo.csv", index=False)
    write_json(OUT_DIR / "a7s4_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7s4_manifest.json", {"generated_at": now, "decision": decision, "output_dir": str(OUT_DIR), "report": str(REPORT_PATH)})
    write_report(now, summary, sym_loo, mon_loo, auth)
    print(json.dumps({"decision": decision, "blockers": blockers}, indent=2))


if __name__ == "__main__":
    main()
