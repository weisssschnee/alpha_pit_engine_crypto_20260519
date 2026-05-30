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
RUNTIME = REPO / "runtime" / "a7ff42_family_balanced_numeric"
REPORT = REPO / "reports" / "CRYPTO_A7FF42_FAMILY_BALANCED_NUMERIC_20260530.md"

A7FFR7_MANIFEST = REPO / "runtime" / "a7ffr7_operator_pair_repair" / "a7ffr7_manifest.json"
A7FFR7_POLICY = REPO / "runtime" / "a7ffr7_operator_pair_repair" / "a7ffr7_operator_pair_policy.csv"
A7FF33_COMPANY = REPO / "runtime" / "a7ff33_family_diversified_dry_generation" / "a7ff33_company_numeric_wave_queue.csv"
NUMERIC_PROBE = REPO / "scripts" / "crypto_a7ff8_expanded_numeric_probe.py"

TARGET_BY_FAMILY = {
    "funding_like|basis_premium_like": 360,
    "regime_state|price_return_like": 360,
    "basis_premium_like|basis_premium_like": 120,
}
DEFAULT_NUMERIC_ROWS = 600


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


def balanced_take(frame: pd.DataFrame, target: int) -> pd.DataFrame:
    if frame.empty or target <= 0:
        return pd.DataFrame(columns=frame.columns)
    pieces: list[pd.DataFrame] = []
    motifs = sorted(frame["motif"].dropna().unique().tolist())
    per_motif = max(1, target // max(1, len(motifs)))
    for motif in motifs:
        group = frame[frame["motif"].eq(motif)].copy()
        skel_parts = []
        for _, skel_group in group.groupby("skeleton_key", sort=True):
            skel_parts.append(skel_group.head(1))
        candidate = pd.concat(skel_parts, ignore_index=True) if skel_parts else group.head(0)
        if len(candidate) < per_motif:
            extra = group[~group["blueprint_id"].isin(set(candidate["blueprint_id"]))].head(per_motif - len(candidate))
            candidate = pd.concat([candidate, extra], ignore_index=True)
        pieces.append(candidate.head(per_motif))
    out = pd.concat(pieces, ignore_index=True) if pieces else frame.head(0)
    if len(out) < target:
        extra = frame[~frame["blueprint_id"].isin(set(out["blueprint_id"]))].head(target - len(out))
        out = pd.concat([out, extra], ignore_index=True)
    return out.drop_duplicates("blueprint_id").head(target).copy()


def build_queue(company: pd.DataFrame, policy: pd.DataFrame) -> pd.DataFrame:
    allowed = policy[policy["promotion_boundary"].astype(str).ne("diagnostic_reference_only_until_non_self_pair_confirms")].copy()
    # Keep the capped basis reference as diagnostic, not as promotion.
    reference = policy[policy["semantic_pair"].eq("basis_premium_like|basis_premium_like")].copy()
    rows: list[pd.DataFrame] = []
    for semantic_pair, target in TARGET_BY_FAMILY.items():
        source = company[company["semantic_pair"].eq(semantic_pair)].copy()
        if semantic_pair != "basis_premium_like|basis_premium_like":
            motifs = set(allowed[allowed["semantic_pair"].eq(semantic_pair)]["motif"].astype(str))
            source = source[source["motif"].astype(str).isin(motifs)]
            role = "family_balanced_candidate"
        else:
            motifs = set(reference["motif"].astype(str))
            source = source[source["motif"].astype(str).isin(motifs)]
            role = "capped_reference_diagnostic"
        if source.empty:
            continue
        source["a7ff42_queue_role"] = role
        rows.append(balanced_take(source, target))
    queue = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=company.columns)
    queue = queue.drop_duplicates("blueprint_id")
    return queue


def sample_queue(queue: pd.DataFrame) -> pd.DataFrame:
    max_rows = int(os.environ.get("A7FF42_NUMERIC_SAMPLE_ROWS", str(DEFAULT_NUMERIC_ROWS)))
    pieces: list[pd.DataFrame] = []
    for _, group in queue.groupby(["semantic_pair", "motif"], sort=True):
        pieces.append(group.head(4))
    sample = pd.concat(pieces, ignore_index=True).drop_duplicates("blueprint_id") if pieces else queue.head(0)
    if len(sample) < max_rows:
        extra = queue[~queue["blueprint_id"].isin(set(sample["blueprint_id"]))].head(max_rows - len(sample))
        sample = pd.concat([sample, extra], ignore_index=True)
    return sample.head(max_rows).copy()


def run_numeric(sample: pd.DataFrame) -> tuple[int, bool]:
    sample_path = RUNTIME / "a7ff42_numeric_wave_sample_queue.csv"
    sample.to_csv(sample_path, index=False)
    env = os.environ.copy()
    env.update(
        {
            "A7FF8_STAGE": "A7FF-42",
            "A7FF8_FILE_PREFIX": "a7ff42",
            "A7FF8_RUNTIME": str(RUNTIME),
            "A7FF8_REPORT": str(REPORT),
            "A7FF8_QUEUE_PATH": str(sample_path),
            "A7FF8_MATERIALIZE_CAP": str(len(sample)),
            "A7FF8_FAST_NUMERIC_CAP": str(len(sample)),
            "A7FF8_PORTFOLIO_CAP": "180",
            "A7FF8_QUEUE_OFFSET": "0",
            "A7FF8_QUEUE_LIMIT": str(len(sample)),
        }
    )
    timeout_seconds = int(os.environ.get("A7FF42_TIMEOUT_SECONDS", "9000"))
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
    (RUNTIME / "a7ff42_numeric_probe_stdout.log").write_text(stdout, encoding="utf-8")
    return returncode, timed_out


def post_forensic() -> dict[str, Any]:
    labels = read_csv(RUNTIME / "a7ff42_label_response_metrics.csv")
    materialization = read_csv(RUNTIME / "a7ff42_materialization_metrics.csv")
    selected = read_csv(RUNTIME / "a7ff42_selected_portfolio_queue.csv")
    decisions = read_csv(RUNTIME / "a7ff42_decision_counts.csv")
    family = read_csv(RUNTIME / "a7ff42_family_decision_summary.csv")
    if not labels.empty:
        labels["control_ratio_premay_max"] = numeric(labels, "control_ratio_premay_max")
        labels["is_non_l7"] = ~labels["label_family"].astype(str).eq("L7_ranked_future_return")
        labels["is_numeric_clue"] = labels["decision"].astype(str).str.contains("NUMERIC_CLUE", regex=False)
        strict = labels[labels["is_non_l7"] & labels["is_numeric_clue"] & labels["control_ratio_premay_max"].lt(0.80)].copy()
    else:
        strict = pd.DataFrame()
    strict.to_csv(RUNTIME / "a7ff42_control_strict_non_l7_clues.csv", index=False)

    if not selected.empty:
        selected["control_ratio_premay_max"] = numeric(selected, "control_ratio_premay_max")
        selected["is_non_l7"] = ~selected["label_family"].astype(str).eq("L7_ranked_future_return")
        selected["is_control_strict"] = selected["control_ratio_premay_max"].lt(0.80)
        selected["a7ff42_role"] = "selected_other"
        selected.loc[selected["is_non_l7"] & selected["is_control_strict"], "a7ff42_role"] = "selected_control_strict_non_l7"
        selected.loc[~selected["is_non_l7"], "a7ff42_role"] = "selected_rank_label_diagnostic"
    selected.to_csv(RUNTIME / "a7ff42_selected_forensic.csv", index=False)

    strict_summary = (
        strict.groupby(["semantic_pair", "motif", "label_family"], dropna=False)
        .agg(
            clue_rows=("blueprint_id", "count"),
            blueprints=("blueprint_id", "nunique"),
            min_control_ratio=("control_ratio_premay_max", "min"),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        .sort_values(["blueprints", "clue_rows"], ascending=[False, False])
        if not strict.empty
        else pd.DataFrame()
    )
    strict_summary.to_csv(RUNTIME / "a7ff42_control_strict_summary.csv", index=False)
    selected_strict = selected[selected.get("a7ff42_role", pd.Series(dtype=str)).eq("selected_control_strict_non_l7")].copy() if not selected.empty else pd.DataFrame()
    return {
        "labels": labels,
        "materialization": materialization,
        "selected": selected,
        "selected_strict": selected_strict,
        "strict": strict,
        "strict_summary": strict_summary,
        "decisions": decisions,
        "family": family,
        "eval_success_count": int(materialization["eval_success"].sum()) if "eval_success" in materialization.columns else 0,
        "eval_failure_count": int((~materialization["eval_success"]).sum()) if "eval_success" in materialization.columns else 0,
        "activity_ok_count": int(materialization["activity_ok"].sum()) if "activity_ok" in materialization.columns else 0,
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    r7 = read_json(A7FFR7_MANIFEST)
    if not r7.get("authorizes_a7ff42_family_balanced_numeric"):
        raise SystemExit(f"A7FF-R7 does not authorize A7FF-42: {r7.get('decision')}")
    policy = read_csv(A7FFR7_POLICY)
    company = read_csv(A7FF33_COMPANY)
    queue = build_queue(company, policy)
    sample = sample_queue(queue)
    queue.to_csv(RUNTIME / "a7ff42_family_balanced_queue.csv", index=False)
    sample.to_csv(RUNTIME / "a7ff42_numeric_wave_sample_queue.csv", index=False)
    queue_summary = (
        queue.groupby(["a7ff42_queue_role", "semantic_pair", "motif"], dropna=False)
        .agg(queue_count=("blueprint_id", "count"), skeleton_count=("skeleton_key", "nunique"))
        .reset_index()
        .sort_values("queue_count", ascending=False)
    )
    queue_summary.to_csv(RUNTIME / "a7ff42_queue_summary.csv", index=False)

    started = now_utc()
    returncode, timed_out = run_numeric(sample)
    numeric_manifest = read_json(RUNTIME / "a7ff42_manifest.json")
    forensic = post_forensic()
    selected_strict = forensic["selected_strict"]
    strict = forensic["strict"]

    selected_strict_family_count = int(selected_strict["semantic_pair"].nunique()) if not selected_strict.empty else 0
    strict_family_count = int(strict["semantic_pair"].nunique()) if not strict.empty else 0
    blockers: list[str] = []
    warnings: list[str] = []
    if returncode != 0:
        blockers.append("numeric_probe_process_failed")
    if timed_out:
        blockers.append("numeric_probe_timeout")
    if forensic["eval_failure_count"] != 0:
        blockers.append("eval_failures_present")
    if len(strict) == 0:
        blockers.append("no_control_strict_non_l7_clues")
    if strict_family_count < 2:
        blockers.append("control_strict_non_l7_clue_family_count_below_2")
    if len(selected_strict) < 4:
        warnings.append("selected_control_strict_non_l7_below_4")
    if selected_strict_family_count < 2:
        warnings.append("selected_control_strict_non_l7_family_count_below_2")

    if blockers:
        decision = "HOLD_A7FF42_FAMILY_BALANCED_NUMERIC_BLOCKED"
        authorizes = False
    elif len(selected_strict) >= 4 and selected_strict_family_count >= 2:
        decision = "PASS_A7FF42_FAMILY_BALANCED_SELECTED_MULTIFAMILY_READY_FOR_DEEP_FORENSIC_NO_SEARCH_AUTH"
        authorizes = True
    else:
        decision = "HOLD_A7FF42_FAMILY_BALANCED_NUMERIC_SELECTED_TOO_THIN"
        authorizes = False

    manifest = {
        "stage": "A7FF-42",
        "generated_at": now_utc(),
        "started_at": started,
        "decision": decision,
        "source_a7ffr7_decision": r7.get("decision"),
        "blockers": blockers,
        "warnings": warnings,
        "queue_count": int(len(queue)),
        "numeric_sample_count": int(len(sample)),
        "eval_success_count": forensic["eval_success_count"],
        "eval_failure_count": forensic["eval_failure_count"],
        "activity_ok_count": forensic["activity_ok_count"],
        "control_strict_non_l7_clue_rows": int(len(strict)),
        "control_strict_non_l7_clue_family_count": strict_family_count,
        "selected_count": int(len(forensic["selected"])),
        "selected_control_strict_non_l7_count": int(len(selected_strict)),
        "selected_control_strict_non_l7_family_count": selected_strict_family_count,
        "process_exit_code": int(returncode),
        "timed_out": bool(timed_out),
        "numeric_probe_decision": numeric_manifest.get("decision"),
        "executes_generation": False,
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff43_deep_forensic": authorizes,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff42_manifest.json", manifest)
    write_json(RUNTIME / "a7ff42_decision_record.json", manifest)

    next_actions = pd.DataFrame(
        [
            {
                "route": "A7FF-43_deep_forensic",
                "status": "authorized" if authorizes else "not_authorized",
                "reason": "requires selected control-strict non-L7 evidence across at least 2 families",
            },
            {
                "route": "A7FF-R8_selector_objective_rewrite",
                "status": "recommended_if_hold",
                "reason": "family-balanced input still cannot produce selected multifamily evidence",
            },
            {"route": "formula_search", "status": "blocked", "reason": "A7FF-42 is numeric only and never authorizes search"},
        ]
    )
    next_actions.to_csv(RUNTIME / "a7ff42_next_actions.csv", index=False)

    report = f"""# CRYPTO A7FF-42 FAMILY-BALANCED CONTROL-STRICT NUMERIC

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-42 runs a family-balanced numeric follow-up from the A7FF-R7 repaired operator-pair policy. It is numeric-only: no formula search, no replay promotion, and no alpha proof authorization.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Queue Summary

{md_table(queue_summary)}

## Control-Strict Summary

{md_table(forensic["strict_summary"])}

## Selected Forensic

{md_table(forensic["selected"])}

## Decision Counts

{md_table(forensic["decisions"])}

## Family Summary

{md_table(forensic["family"])}

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
