from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff40_control_strict_followup"
REPORT = REPO / "reports" / "CRYPTO_A7FF40_CONTROL_STRICT_FOLLOWUP_20260530.md"

A7FF39_MANIFEST = REPO / "runtime" / "a7ff39_focused_taskflow_forensic" / "a7ff39_manifest.json"
A7FF38_METRICS = REPO / "runtime" / "a7ff38_focused_replay_taskflow" / "a7ff38_label_response_metrics.csv"
A7FF38_SELECTED = REPO / "runtime" / "a7ff39_focused_taskflow_forensic" / "a7ff39_selected_forensic.csv"
A7FF33_COMPANY = REPO / "runtime" / "a7ff33_family_diversified_dry_generation" / "a7ff33_company_numeric_wave_queue.csv"
NUMERIC_PROBE = REPO / "scripts" / "crypto_a7ff8_expanded_numeric_probe.py"

CONTROL_STRICT_THRESHOLD = 0.80
DEFAULT_NUMERIC_ROWS = 480


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


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


def numeric(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series([float("nan")] * len(df), index=df.index)
    return pd.to_numeric(df[col], errors="coerce")


def balanced_take_by_skeleton(frame: pd.DataFrame, target: int) -> pd.DataFrame:
    if frame.empty or target <= 0:
        return pd.DataFrame(columns=frame.columns)
    pieces: list[pd.DataFrame] = []
    for _, group in frame.groupby("motif", sort=True):
        # Keep multiple skeletons per motif so the queue does not collapse into one expression shape.
        per_motif = max(1, target // max(1, frame["motif"].nunique()))
        subpieces = []
        for _, skel_group in group.groupby("skeleton_key", sort=True):
            subpieces.append(skel_group.head(1))
        candidate = pd.concat(subpieces, ignore_index=True) if subpieces else group.head(0)
        if len(candidate) < per_motif:
            extra = group[~group["blueprint_id"].isin(set(candidate["blueprint_id"]))].head(per_motif - len(candidate))
            candidate = pd.concat([candidate, extra], ignore_index=True)
        pieces.append(candidate.head(per_motif))
    out = pd.concat(pieces, ignore_index=True) if pieces else frame.head(0)
    if len(out) < target:
        extra = frame[~frame["blueprint_id"].isin(set(out["blueprint_id"]))].head(target - len(out))
        out = pd.concat([out, extra], ignore_index=True)
    return out.drop_duplicates("blueprint_id").head(target).copy()


def build_policy(metrics: pd.DataFrame, selected: pd.DataFrame, company: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    metrics = metrics.copy()
    metrics["control_ratio_premay_max"] = numeric(metrics, "control_ratio_premay_max")
    # Full label-response metrics do not carry the selector score. Use a deterministic
    # response proxy for policy ranking; selected-score remains audited separately.
    metrics["response_proxy_score"] = (
        numeric(metrics, "recent_oos_2026JanApr_tstat").abs().fillna(0.0)
        + numeric(metrics, "validation_2025H1_tstat").abs().fillna(0.0)
        + numeric(metrics, "test_2025H2_tstat").abs().fillna(0.0)
    )
    metrics["is_non_l7"] = ~metrics["label_family"].astype(str).eq("L7_ranked_future_return")
    metrics["is_numeric_clue"] = metrics["decision"].astype(str).str.contains("NUMERIC_CLUE", regex=False)
    strict = metrics[
        metrics["is_non_l7"]
        & metrics["is_numeric_clue"]
        & metrics["control_ratio_premay_max"].lt(CONTROL_STRICT_THRESHOLD)
    ].copy()
    strict = strict.merge(
        company[["blueprint_id", "primary_field", "secondary_field", "primary_transform", "secondary_transform", "skeleton_key", "production_key"]],
        on="blueprint_id",
        how="left",
        suffixes=("", "_company"),
    )
    strict.to_csv(RUNTIME / "a7ff40_strict_seed_evidence.csv", index=False)

    pattern = (
        strict.groupby(["semantic_pair", "motif"], dropna=False)
        .agg(
            seed_rows=("blueprint_id", "count"),
            seed_blueprints=("blueprint_id", "nunique"),
            label_count=("label_family", "nunique"),
            min_control_ratio=("control_ratio_premay_max", "min"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            max_response_proxy_score=("response_proxy_score", "max"),
            primary_field_count=("primary_field", "nunique"),
            secondary_field_count=("secondary_field", "nunique"),
        )
        .reset_index()
        .sort_values(["seed_rows", "max_response_proxy_score"], ascending=[False, False])
    )
    pattern["a7ff40_policy"] = "expand_control_strict"
    pattern.loc[pattern["semantic_pair"].eq("basis_premium_like|basis_premium_like"), "a7ff40_policy"] = "small_reference_only"
    pattern.loc[pattern["semantic_pair"].eq("regime_state|price_return_like"), "a7ff40_policy"] = "diagnostic_control_repair"
    pattern.to_csv(RUNTIME / "a7ff40_seed_pattern_policy.csv", index=False)
    return strict, pattern


def build_followup_queue(company: pd.DataFrame, pattern: pd.DataFrame) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    # Larger than the previous selected set, but still bounded and policy-driven.
    target_by_policy = {
        "expand_control_strict": 360,
        "diagnostic_control_repair": 180,
        "small_reference_only": 80,
    }
    for _, row in pattern.iterrows():
        semantic_pair = str(row["semantic_pair"])
        motif = str(row["motif"])
        policy = str(row["a7ff40_policy"])
        source = company[company["semantic_pair"].eq(semantic_pair) & company["motif"].eq(motif)].copy()
        if source.empty:
            continue
        # Allocate per pattern, capped to avoid single motif dominance.
        target = min(int(target_by_policy.get(policy, 80) / max(1, (pattern["a7ff40_policy"].eq(policy)).sum())), 160)
        source["a7ff40_policy"] = policy
        source["a7ff40_seed_semantic_pair"] = semantic_pair
        source["a7ff40_seed_motif"] = motif
        parts.append(balanced_take_by_skeleton(source, max(20, target)))

    queue = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=company.columns)
    queue = queue.drop_duplicates("blueprint_id")

    # Add hard contrast rows only if the strict queue is too narrow. These rows are diagnostic,
    # not promotion candidates.
    contrast_specs = [
        ("open_interest_like|positioning_like", "contrast_no_promotion", 80),
        ("taker_flow_like|open_interest_like", "contrast_no_promotion", 80),
        ("liquidity_like|volatility_like", "contrast_no_promotion", 80),
    ]
    for semantic_pair, policy, target in contrast_specs:
        if len(queue) >= 720:
            break
        source = company[company["semantic_pair"].eq(semantic_pair)].copy()
        if source.empty:
            continue
        source["a7ff40_policy"] = policy
        source["a7ff40_seed_semantic_pair"] = semantic_pair
        source["a7ff40_seed_motif"] = "*"
        add = balanced_take_by_skeleton(source, target)
        queue = pd.concat([queue, add], ignore_index=True).drop_duplicates("blueprint_id")

    queue["a7ff40_queue_role"] = queue["a7ff40_policy"].map(
        {
            "expand_control_strict": "strict_followup_candidate",
            "diagnostic_control_repair": "control_repair_diagnostic",
            "small_reference_only": "basis_reference_diagnostic",
            "contrast_no_promotion": "contrast_diagnostic",
        }
    ).fillna("unknown")
    return queue.head(720).copy()


def sample_for_numeric(queue: pd.DataFrame) -> pd.DataFrame:
    max_rows = int(os.environ.get("A7FF40_NUMERIC_SAMPLE_ROWS", str(DEFAULT_NUMERIC_ROWS)))
    if queue.empty:
        return queue
    pieces: list[pd.DataFrame] = []
    for _, group in queue.groupby(["a7ff40_policy", "semantic_pair", "motif"], sort=True):
        pieces.append(group.head(3))
    sample = pd.concat(pieces, ignore_index=True).drop_duplicates("blueprint_id") if pieces else queue.head(0)
    if len(sample) < max_rows:
        extra = queue[~queue["blueprint_id"].isin(set(sample["blueprint_id"]))].head(max_rows - len(sample))
        sample = pd.concat([sample, extra], ignore_index=True)
    return sample.head(max_rows).copy()


def run_numeric(sample: pd.DataFrame) -> tuple[int, bool, str]:
    sample_path = RUNTIME / "a7ff40_numeric_wave_sample_queue.csv"
    sample.to_csv(sample_path, index=False)
    env = os.environ.copy()
    env.update(
        {
            "A7FF8_STAGE": "A7FF-40",
            "A7FF8_FILE_PREFIX": "a7ff40",
            "A7FF8_RUNTIME": str(RUNTIME),
            "A7FF8_REPORT": str(REPORT),
            "A7FF8_QUEUE_PATH": str(sample_path),
            "A7FF8_MATERIALIZE_CAP": str(len(sample)),
            "A7FF8_FAST_NUMERIC_CAP": str(len(sample)),
            "A7FF8_PORTFOLIO_CAP": "160",
            "A7FF8_QUEUE_OFFSET": "0",
            "A7FF8_QUEUE_LIMIT": str(len(sample)),
        }
    )
    timeout_seconds = int(os.environ.get("A7FF40_TIMEOUT_SECONDS", "7200"))
    try:
        proc = subprocess.run(
            [sys.executable, str(NUMERIC_PROBE)],
            cwd=REPO,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout_seconds,
        )
        stdout = proc.stdout
        returncode = proc.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace"))
        stdout += f"\nTIMEOUT after {timeout_seconds} seconds\n"
        returncode = -9
        timed_out = True
    (RUNTIME / "a7ff40_numeric_probe_stdout.log").write_text(stdout, encoding="utf-8")
    return returncode, timed_out, stdout


def post_numeric_forensic() -> dict[str, Any]:
    label_metrics = read_csv(RUNTIME / "a7ff40_label_response_metrics.csv")
    materialization = read_csv(RUNTIME / "a7ff40_materialization_metrics.csv")
    selected = read_csv(RUNTIME / "a7ff40_selected_portfolio_queue.csv")
    family_summary = read_csv(RUNTIME / "a7ff40_family_decision_summary.csv")
    decision_counts = read_csv(RUNTIME / "a7ff40_decision_counts.csv")

    if not label_metrics.empty:
        label_metrics["control_ratio_premay_max"] = numeric(label_metrics, "control_ratio_premay_max")
        label_metrics["response_proxy_score"] = (
            numeric(label_metrics, "recent_oos_2026JanApr_tstat").abs().fillna(0.0)
            + numeric(label_metrics, "validation_2025H1_tstat").abs().fillna(0.0)
            + numeric(label_metrics, "test_2025H2_tstat").abs().fillna(0.0)
        )
        label_metrics["is_non_l7"] = ~label_metrics["label_family"].astype(str).eq("L7_ranked_future_return")
        label_metrics["is_numeric_clue"] = label_metrics["decision"].astype(str).str.contains("NUMERIC_CLUE", regex=False)
        strict = label_metrics[
            label_metrics["is_non_l7"]
            & label_metrics["is_numeric_clue"]
            & label_metrics["control_ratio_premay_max"].lt(CONTROL_STRICT_THRESHOLD)
        ].copy()
    else:
        strict = pd.DataFrame()
    strict.to_csv(RUNTIME / "a7ff40_control_strict_numeric_clues.csv", index=False)

    if not selected.empty:
        selected["control_ratio_premay_max"] = numeric(selected, "control_ratio_premay_max")
        selected["is_non_l7"] = ~selected["label_family"].astype(str).eq("L7_ranked_future_return")
        selected["is_control_strict"] = selected["control_ratio_premay_max"].lt(CONTROL_STRICT_THRESHOLD)
        selected["a7ff40_forensic_role"] = "selected_but_not_control_strict"
        selected.loc[selected["is_non_l7"] & selected["is_control_strict"], "a7ff40_forensic_role"] = "control_strict_non_l7_selected"
        selected.loc[~selected["is_non_l7"], "a7ff40_forensic_role"] = "rank_label_diagnostic_selected"
    selected.to_csv(RUNTIME / "a7ff40_selected_forensic.csv", index=False)

    strict_summary = (
        strict.groupby(["semantic_pair", "motif", "label_family"], dropna=False)
        .agg(
            clue_rows=("blueprint_id", "count"),
            blueprints=("blueprint_id", "nunique"),
            min_control_ratio=("control_ratio_premay_max", "min"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            max_response_proxy_score=("response_proxy_score", "max"),
        )
        .reset_index()
        .sort_values(["blueprints", "max_response_proxy_score"], ascending=[False, False])
        if not strict.empty
        else pd.DataFrame()
    )
    strict_summary.to_csv(RUNTIME / "a7ff40_control_strict_summary.csv", index=False)

    selected_strict = selected[selected.get("a7ff40_forensic_role", pd.Series(dtype=str)).eq("control_strict_non_l7_selected")].copy() if not selected.empty else pd.DataFrame()
    eval_success_count = int(materialization["eval_success"].sum()) if "eval_success" in materialization.columns else 0
    eval_failure_count = int((~materialization["eval_success"]).sum()) if "eval_success" in materialization.columns else 0
    activity_ok_count = int(materialization["activity_ok"].sum()) if "activity_ok" in materialization.columns else 0

    return {
        "label_metrics": label_metrics,
        "materialization": materialization,
        "selected": selected,
        "strict": strict,
        "strict_summary": strict_summary,
        "selected_strict": selected_strict,
        "family_summary": family_summary,
        "decision_counts": decision_counts,
        "eval_success_count": eval_success_count,
        "eval_failure_count": eval_failure_count,
        "activity_ok_count": activity_ok_count,
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    f39 = read_json(A7FF39_MANIFEST)
    if not f39.get("authorizes_a7ff40_control_strict_followup"):
        raise SystemExit(f"A7FF-39 does not authorize A7FF-40: {f39.get('decision')}")

    metrics = read_csv(A7FF38_METRICS)
    selected = read_csv(A7FF38_SELECTED)
    company = read_csv(A7FF33_COMPANY)
    strict_seed, pattern = build_policy(metrics, selected, company)
    queue = build_followup_queue(company, pattern)
    sample = sample_for_numeric(queue)
    queue.to_csv(RUNTIME / "a7ff40_control_strict_followup_queue.csv", index=False)

    queue_summary = (
        queue.groupby(["a7ff40_queue_role", "semantic_pair", "motif"], dropna=False)
        .agg(queue_count=("blueprint_id", "count"), skeleton_count=("skeleton_key", "nunique"))
        .reset_index()
        .sort_values("queue_count", ascending=False)
    )
    queue_summary.to_csv(RUNTIME / "a7ff40_queue_summary.csv", index=False)

    started = now_utc()
    returncode, timed_out, _stdout = run_numeric(sample)
    numeric_manifest = read_json(RUNTIME / "a7ff40_manifest.json")
    forensic = post_numeric_forensic()

    blockers: list[str] = []
    warnings: list[str] = []
    if returncode != 0:
        blockers.append("numeric_probe_process_failed")
    if timed_out:
        blockers.append("numeric_probe_timeout")
    if forensic["eval_failure_count"] != 0:
        blockers.append("eval_failures_present")
    strict = forensic["strict"]
    selected_strict = forensic["selected_strict"]
    strict_family_count = int(strict["semantic_pair"].nunique()) if not strict.empty else 0
    selected_strict_family_count = int(selected_strict["semantic_pair"].nunique()) if not selected_strict.empty else 0
    if len(strict) == 0:
        blockers.append("no_control_strict_non_l7_numeric_clues")
    if strict_family_count < 2:
        warnings.append("control_strict_non_l7_clues_below_2_families")
    if len(selected_strict) < 2:
        warnings.append("selected_control_strict_non_l7_below_2")
    if selected_strict_family_count < 2:
        warnings.append("selected_control_strict_non_l7_single_family")

    if blockers:
        decision = "HOLD_A7FF40_CONTROL_STRICT_FOLLOWUP_NO_CLEAN_CLUES"
        authorizes_a7ff41 = False
    elif selected_strict_family_count >= 2 and len(selected_strict) >= 4:
        decision = "PASS_A7FF40_CONTROL_STRICT_MULTIFAMILY_READY_FOR_A7FF41_NO_SEARCH_AUTH"
        authorizes_a7ff41 = True
    else:
        decision = "HOLD_A7FF40_CONTROL_STRICT_SINGLE_FAMILY_OR_SELECTED_TOO_THIN"
        authorizes_a7ff41 = False

    manifest = {
        "stage": "A7FF-40",
        "generated_at": now_utc(),
        "started_at": started,
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "source_a7ff39_decision": f39.get("decision"),
        "focused_queue_count": int(len(queue)),
        "numeric_sample_count": int(len(sample)),
        "strict_seed_rows": int(len(strict_seed)),
        "strict_seed_family_count": int(strict_seed["semantic_pair"].nunique()) if not strict_seed.empty else 0,
        "strict_seed_motif_count": int(strict_seed["motif"].nunique()) if not strict_seed.empty else 0,
        "eval_success_count": forensic["eval_success_count"],
        "eval_failure_count": forensic["eval_failure_count"],
        "activity_ok_count": forensic["activity_ok_count"],
        "control_strict_non_l7_clue_rows": int(len(strict)),
        "control_strict_non_l7_family_count": strict_family_count,
        "selected_count": int(len(forensic["selected"])),
        "selected_control_strict_non_l7_count": int(len(selected_strict)),
        "selected_control_strict_non_l7_family_count": selected_strict_family_count,
        "process_exit_code": int(returncode),
        "timed_out": bool(timed_out),
        "executes_generation": False,
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff41_control_strict_expansion": authorizes_a7ff41,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "numeric_probe_decision": numeric_manifest.get("decision"),
    }
    write_json(RUNTIME / "a7ff40_manifest.json", manifest)
    write_json(RUNTIME / "a7ff40_decision_record.json", manifest)

    next_actions = pd.DataFrame(
        [
            {
                "route": "A7FF-41_control_strict_expansion",
                "status": "authorized" if authorizes_a7ff41 else "not_authorized",
                "reason": "requires >=4 selected control-strict non-L7 rows across >=2 semantic families",
            },
            {
                "route": "A7FF-R_operator_pair_repair",
                "status": "recommended_if_hold",
                "reason": "single-family clean evidence means feature-pair policy, not selector size, is the binding constraint",
            },
            {
                "route": "formula_search",
                "status": "blocked",
                "reason": "A7FF-40 is numeric/forensic only and never authorizes search",
            },
        ]
    )
    next_actions.to_csv(RUNTIME / "a7ff40_next_actions.csv", index=False)

    report = f"""# CRYPTO A7FF-40 CONTROL-STRICT FOLLOW-UP

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-40 expands the A7FF-39 control-clean non-L7 evidence into a larger but control-strict focused numeric taskflow. It excludes rank-label-only rows from promotion logic and treats control warning rows as diagnostic only.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Seed Pattern Policy

{md_table(pattern)}

## Queue Summary

{md_table(queue_summary)}

## Control-Strict Numeric Summary

{md_table(forensic["strict_summary"])}

## Selected Forensic

{md_table(forensic["selected"])}

## Decision Counts

{md_table(forensic["decision_counts"])}

## Family Summary

{md_table(forensic["family_summary"])}

## Next Actions

{md_table(next_actions)}

## Boundary

```text
numeric probe executed: true
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
