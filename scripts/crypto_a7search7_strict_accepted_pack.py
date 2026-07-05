from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DATE = "20260706"
STAGE = "A7SEARCH7-STRICT-ACCEPTED-PACK"
DEFAULT_RUNTIME = Path("runtime/a7search7_strict_accepted_pack_20260706")
DEFAULT_REPORT = Path("reports/CRYPTO_A7SEARCH7_STRICT_ACCEPTED_PACK_20260706.md")
FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
OPS = {
    "Abs",
    "Add",
    "CSRank",
    "Clip",
    "Decay",
    "Delta",
    "Mean",
    "Mul",
    "Neg",
    "Rank",
    "SafeDiv",
    "Sign",
    "Sub",
    "TSRank",
    "ZScore",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def num(value: object, default: float = math.nan) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def md_table(frame: pd.DataFrame, max_rows: int = 30) -> str:
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


def expression_fields(expr: str) -> list[str]:
    out: list[str] = []
    for token in FIELD_RE.findall(str(expr)):
        if token in OPS:
            continue
        if token not in out:
            out.append(token)
    return out


def add_validation_row(rows: list[dict[str, Any]], src: dict[str, Any], suffix: str, expr: str, group: str, note: str) -> None:
    sid = str(src["blueprint_id"])
    rows.append(
        {
            "blueprint_id": f"a7search7_vp_{sid}_{src.get('horizon_h')}_{suffix}",
            "production_key": f"a7search7_vp_{sid}_{src.get('horizon_h')}_{suffix}",
            "source_blueprint_id": sid,
            "source_expression": src.get("expression", ""),
            "source_horizon_h": src.get("horizon_h", ""),
            "source_semantic_pair": src.get("semantic_pair", ""),
            "source_motif": src.get("motif", ""),
            "source_proxy_score": src.get("proxy_score", ""),
            "source_overall_reward": src.get("overall_reward", ""),
            "semantic_pair": src.get("semantic_pair", ""),
            "motif": f"{src.get('motif', '')}_strict_validation",
            "skeleton_key": suffix,
            "expression": expr,
            "validation_group": group,
            "validation_note": note,
            "candidate_role": "strict_validation_ablation",
        }
    )


def validation_queue(strict: pd.DataFrame, max_fields: int = 3) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for src in strict.to_dict("records"):
        expr = str(src.get("expression", ""))
        fields = expression_fields(expr)[:max_fields]
        add_validation_row(rows, src, "canonical", expr, "canonical", "strict accepted formula rerun")
        for field in fields:
            safe = re.sub(r"[^A-Za-z0-9_]+", "_", field)
            add_validation_row(rows, src, f"single_csrank_{safe}", f"CSRank({field})", "single_leg", f"{field} CSRank only")
            add_validation_row(rows, src, f"single_zscore_{safe}", f"ZScore({field})", "single_leg", f"{field} ZScore only")
            add_validation_row(rows, src, f"single_tsrank_{safe}", f"TSRank({field},336)", "single_leg", f"{field} TSRank336 only")
            add_validation_row(rows, src, f"single_mean72_{safe}", f"Mean({field},72)", "single_leg", f"{field} Mean72 only")
        if len(fields) >= 2:
            left, right = fields[0], fields[1]
            add_validation_row(rows, src, "pair_spread_rank", f"Sub(CSRank({left}),CSRank({right}))", "operator_neighbor", "rank spread")
            add_validation_row(rows, src, "pair_mul_rank", f"Mul(CSRank({left}),CSRank({right}))", "operator_neighbor", "rank product")
            add_validation_row(rows, src, "pair_safe_div_rank", f"SafeDiv(CSRank({left}),Abs(CSRank({right})))", "operator_neighbor", "safe-div same direction")
            add_validation_row(rows, src, "pair_safe_div_rank_swapped", f"SafeDiv(CSRank({right}),Abs(CSRank({left})))", "operator_neighbor", "safe-div swapped")
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).drop_duplicates("blueprint_id", keep="first")


def strict_filter(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    out = frame.copy()
    for col in [
        "overall_reward",
        "proxy_score",
        "train_sortino",
        "validation_sortino",
        "test_sortino",
        "recent_sortino",
        "min_oos_sortino",
        "min_oos_floor_sortino",
        "stress_sortino",
        "stress_floor_sortino",
        "recent_control_ratio",
        "recent_shuffle_control_ratio",
        "oos_control_dominated_count",
        "oos_lag_stale_dominated_count",
        "oos_shuffle_dominated_count",
        "recent_avg_turnover",
    ]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    mask = (
        ~out.get("hard_reject", pd.Series(False, index=out.index)).map(truthy)
        & out.get("gate_pass", pd.Series(False, index=out.index)).map(truthy)
        & out.get("proxy_strict_pass", pd.Series(False, index=out.index)).map(truthy)
        & (out["min_oos_sortino"] > 0)
        & (out["min_oos_floor_sortino"] > 0)
        & (out["stress_floor_sortino"] > 0)
        & (out["recent_shuffle_control_ratio"] < 1)
        & (out["recent_control_ratio"] < 1)
        & (out["oos_control_dominated_count"].fillna(0) <= 0)
        & (out["oos_lag_stale_dominated_count"].fillna(0) <= 0)
        & (out["oos_shuffle_dominated_count"].fillna(0) <= 0)
    )
    strict = out[mask].copy()
    if strict.empty:
        return strict
    strict["strict_pack_score"] = (
        strict["min_oos_floor_sortino"]
        + 0.35 * strict["recent_sortino"]
        + 0.20 * strict["stress_floor_sortino"]
        - 0.25 * strict["recent_shuffle_control_ratio"]
        - 0.10 * strict["recent_avg_turnover"].fillna(0)
    )
    strict = strict.sort_values(["strict_pack_score", "min_oos_floor_sortino", "recent_sortino"], ascending=False)
    strict = strict.drop_duplicates(["expression", "horizon_h"], keep="first")
    strict = strict.drop_duplicates(["semantic_pair", "motif", "skeleton_key"], keep="first")
    return strict


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True, help="A7SEARCH7 quick aggregate directory")
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--max-fields-per-formula", type=int, default=3)
    args = parser.parse_args()

    args.runtime.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)

    selected = read_csv(args.input_root / "a7search7_r2_all_selected_for_reward.csv")
    rewards = read_csv(args.input_root / "a7search7_r2_all_reward_leaderboard.csv")
    coverage = read_csv(args.input_root / "a7search7_r2_shard_file_coverage.csv")
    if selected.empty:
        raise RuntimeError(f"missing selected input under {args.input_root}")

    strict = strict_filter(selected)
    queue = validation_queue(strict, max_fields=args.max_fields_per_formula)

    selected.to_csv(args.runtime / "a7search7_r2_selected_for_reward_all.csv", index=False)
    strict.to_csv(args.runtime / "a7search7_strict_accepted_candidates.csv", index=False)
    queue.to_csv(args.runtime / "a7search7_validation_ablation_queue.csv", index=False)

    family = (
        strict.groupby(["semantic_pair", "motif"], dropna=False)
        .agg(
            candidates=("blueprint_id", "count"),
            median_min_oos_floor=("min_oos_floor_sortino", "median"),
            median_recent_sortino=("recent_sortino", "median"),
            median_stress_floor=("stress_floor_sortino", "median"),
            max_score=("strict_pack_score", "max"),
        )
        .reset_index()
        .sort_values(["candidates", "max_score"], ascending=False)
        if not strict.empty
        else pd.DataFrame()
    )
    queue_summary = (
        queue.groupby("validation_group", dropna=False)
        .agg(rows=("blueprint_id", "count"), source_blueprints=("source_blueprint_id", "nunique"))
        .reset_index()
        if not queue.empty
        else pd.DataFrame()
    )
    family.to_csv(args.runtime / "a7search7_strict_family_summary.csv", index=False)
    queue_summary.to_csv(args.runtime / "a7search7_validation_queue_summary.csv", index=False)

    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": "PASS_A7SEARCH7_STRICT_ACCEPTED_PACK_BUILT" if len(strict) > 0 else "HOLD_A7SEARCH7_NO_STRICT_ACCEPTED_CANDIDATES",
        "input_root": str(args.input_root),
        "runtime": str(args.runtime),
        "selected_rows": int(len(selected)),
        "reward_rows": int(len(rewards)),
        "shard_coverage_rows": int(len(coverage)),
        "strict_accepted_rows": int(len(strict)),
        "strict_unique_blueprints": int(strict["blueprint_id"].nunique()) if not strict.empty else 0,
        "validation_queue_rows": int(len(queue)),
        "authorizes_validation_reward": int(len(queue)) > 0,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "outputs": {
            "selected_all": str(args.runtime / "a7search7_r2_selected_for_reward_all.csv"),
            "strict_accepted": str(args.runtime / "a7search7_strict_accepted_candidates.csv"),
            "validation_queue": str(args.runtime / "a7search7_validation_ablation_queue.csv"),
            "family_summary": str(args.runtime / "a7search7_strict_family_summary.csv"),
            "queue_summary": str(args.runtime / "a7search7_validation_queue_summary.csv"),
        },
    }
    write_json(args.runtime / "a7search7_strict_accepted_pack_manifest.json", manifest)

    top_cols = [
        "blueprint_id",
        "semantic_pair",
        "motif",
        "horizon_h",
        "strict_pack_score",
        "train_sortino",
        "validation_sortino",
        "test_sortino",
        "recent_sortino",
        "min_oos_floor_sortino",
        "stress_floor_sortino",
        "recent_control_ratio",
        "recent_shuffle_control_ratio",
        "expression",
    ]
    top = strict[[c for c in top_cols if c in strict.columns]].head(30) if not strict.empty else pd.DataFrame()
    report = [
        "# CRYPTO A7SEARCH7 Strict Accepted Pack 20260706",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "This packages A7SEARCH7 R2 candidates that passed strict reward/proxy gates. It is not alpha proof and does not authorize shadow, paper, or live trading.",
        "",
        "## Counts",
        "",
        f"- selected_rows: `{manifest['selected_rows']}`",
        f"- reward_rows: `{manifest['reward_rows']}`",
        f"- strict_accepted_rows: `{manifest['strict_accepted_rows']}`",
        f"- validation_queue_rows: `{manifest['validation_queue_rows']}`",
        "",
        "## Family Summary",
        "",
        md_table(family, 30),
        "",
        "## Validation Queue Summary",
        "",
        md_table(queue_summary, 20),
        "",
        "## Top Strict Accepted",
        "",
        md_table(top, 30),
        "",
        "## Gate Definition",
        "",
        "- `hard_reject == false`",
        "- `gate_pass == true`",
        "- `proxy_strict_pass == true`",
        "- `min_oos_sortino > 0` and `min_oos_floor_sortino > 0`",
        "- `stress_floor_sortino > 0`",
        "- recent matched/shuffle control ratios below 1",
        "- no OOS control, lag/stale, or shuffle dominance counts",
        "- one representative per `(expression, horizon)` and per `(semantic_pair, motif, skeleton_key)`",
        "",
        "## Outputs",
        "",
    ]
    for key, value in manifest["outputs"].items():
        report.append(f"- `{key}`: `{value}`")
    args.report.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
