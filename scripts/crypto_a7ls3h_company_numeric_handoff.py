from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
LS2 = REPO / "runtime" / "a7ls2_sharded_materialization_wave"
LS3 = REPO / "runtime" / "a7ls3_numeric_checkpoint_from_materialized"
RUNTIME = REPO / "runtime" / "a7ls3h_company_numeric_handoff"
REPORT = REPO / "reports" / "CRYPTO_A7LS3H_COMPANY_NUMERIC_HANDOFF_20260605.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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
        if df[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```csv\n" + view.to_csv(index=False) + "```"


def diversified_take(df: pd.DataFrame, limit: int) -> pd.DataFrame:
    if df.empty or limit <= 0:
        return df.head(0)
    selected = []
    used: set[str] = set()
    sem_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    arm_counts: dict[str, int] = {}
    skel_counts: dict[str, int] = {}
    sem_cap = max(32, int(limit * 0.16))
    motif_cap = max(32, int(limit * 0.18))
    arm_cap = max(64, int(limit * 0.30))
    skel_cap = max(8, int(limit * 0.04))
    for _, row in df.iterrows():
        bid = str(row.get("blueprint_id"))
        if bid in used:
            continue
        sem = str(row.get("semantic_pair"))
        motif = str(row.get("motif"))
        arm = str(row.get("a7ls_arm"))
        skel = str(row.get("skeleton_key"))
        if sem_counts.get(sem, 0) >= sem_cap:
            continue
        if motif_counts.get(motif, 0) >= motif_cap:
            continue
        if arm_counts.get(arm, 0) >= arm_cap:
            continue
        if skel_counts.get(skel, 0) >= skel_cap:
            continue
        selected.append(row)
        used.add(bid)
        sem_counts[sem] = sem_counts.get(sem, 0) + 1
        motif_counts[motif] = motif_counts.get(motif, 0) + 1
        arm_counts[arm] = arm_counts.get(arm, 0) + 1
        skel_counts[skel] = skel_counts.get(skel, 0) + 1
        if len(selected) >= limit:
            break
    if len(selected) < limit:
        for _, row in df.iterrows():
            bid = str(row.get("blueprint_id"))
            if bid in used:
                continue
            selected.append(row)
            used.add(bid)
            if len(selected) >= limit:
                break
    return pd.DataFrame(selected)


def arm_balanced_handoff(ok: pd.DataFrame, target: int) -> pd.DataFrame:
    if ok.empty:
        return ok
    base_quota = max(1, target // 4)
    arm_order = ["A7LS_A", "A7LS_B", "A7LS_C", "A7LS_D"]
    selected_frames: list[pd.DataFrame] = []
    used: set[str] = set()
    for arm in arm_order:
        group = ok[ok["a7ls_arm"].eq(arm)].copy()
        take = min(base_quota, len(group))
        part = diversified_take(group, take)
        selected_frames.append(part)
        used.update(part["blueprint_id"].astype(str).tolist())
    selected = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    if len(selected) < target:
        # Raw multi-axis gets first claim on leftover budget, per user requirement.
        raw_extra = ok[ok["a7ls_arm"].eq("A7LS_B") & ~ok["blueprint_id"].astype(str).isin(used)].copy()
        extra = diversified_take(raw_extra, target - len(selected))
        selected = pd.concat([selected, extra], ignore_index=True)
        used.update(extra["blueprint_id"].astype(str).tolist())
    if len(selected) < target:
        remaining = ok[~ok["blueprint_id"].astype(str).isin(used)].copy()
        selected = pd.concat([selected, diversified_take(remaining, target - len(selected))], ignore_index=True)
    return selected.head(target).copy()


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    ls2 = read_json(LS2 / "a7ls2_manifest.json")
    ls3 = read_json(LS3 / "a7ls3_manifest.json")
    if not ls2.get("authorizes_a7ls3_numeric_wave"):
        raise SystemExit(f"A7LS-2 does not authorize A7LS-3 handoff: {ls2.get('decision')}")

    metrics = read_csv(LS2 / "a7ls2_materialization_metrics_executed.csv")
    if metrics.empty:
        raise SystemExit("A7LS3H requires A7LS-2 materialization metrics")
    ok = metrics[metrics["activity_ok"].astype(str).str.lower().isin({"true", "1"})].copy()
    ok["finite_share"] = pd.to_numeric(ok["finite_share"], errors="coerce").fillna(0)
    ok["nonzero_share"] = pd.to_numeric(ok["nonzero_share"], errors="coerce").fillna(0)
    ok["materialization_score"] = ok["finite_share"].clip(0, 1) * 0.6 + ok["nonzero_share"].clip(0, 1) * 0.4
    ok = ok.sort_values(["a7ls_arm", "materialization_score", "semantic_pair", "motif"], ascending=[True, False, True, True])

    target = int(min(1024, len(ok)))
    handoff = arm_balanced_handoff(ok, target)
    rows_per_shard = int(32)
    handoff = handoff.reset_index(drop=True)
    handoff["a7input_queue"] = "a7ls3h_company_numeric_checkpoint"
    handoff["core58_queue"] = "a7ls3h_company_numeric_checkpoint"
    handoff["company_numeric_shard"] = [f"a7ls3h_s{i // rows_per_shard:03d}" for i in range(len(handoff))]
    handoff["checkpoint_key"] = handoff["company_numeric_shard"] + "::" + handoff["blueprint_id"].astype(str)
    handoff.to_csv(RUNTIME / "a7ls3h_company_numeric_queue.csv", index=False)

    shard_plan = handoff.groupby(["company_numeric_shard", "a7ls_arm"], dropna=False).agg(
        rows=("blueprint_id", "size"),
        semantic_pair_count=("semantic_pair", "nunique"),
        motif_count=("motif", "nunique"),
        skeleton_count=("skeleton_key", "nunique"),
    ).reset_index()
    shard_plan.to_csv(RUNTIME / "a7ls3h_company_shard_plan.csv", index=False)

    queue_summary = handoff.groupby(["a7ls_arm", "semantic_pair"], dropna=False).agg(
        rows=("blueprint_id", "size"),
        motif_count=("motif", "nunique"),
        skeleton_count=("skeleton_key", "nunique"),
        median_materialization_score=("materialization_score", "median"),
    ).reset_index().sort_values(["a7ls_arm", "rows"], ascending=[True, False])
    queue_summary.to_csv(RUNTIME / "a7ls3h_queue_summary.csv", index=False)

    command_template = {
        "stage": "A7LS-3H",
        "runner": "scripts/crypto_a7ff8_expanded_numeric_probe.py",
        "per_shard_env": {
            "A7FF8_STAGE": "A7LS-3H-${SHARD}",
            "A7FF8_FILE_PREFIX": "a7ls3h_${SHARD}",
            "A7FF8_RUNTIME": "G:/AlphaFactory_CryptoData/research_runtime/a7ls3h_company_numeric/${SHARD}",
            "A7FF8_REPORT": "G:/AlphaFactory_CryptoData/research_runtime/a7ls3h_company_numeric/${SHARD}/A7LS3H_NUMERIC_DETAIL.md",
            "A7FF8_QUEUE_PATH": "G:/AlphaFactory_CryptoData/research_runtime/a7ls3h_company_numeric/${SHARD}/queue.csv",
            "A7FF8_AUTH_MANIFEST": str(LS2 / "a7ls2_manifest.json").replace("\\", "/"),
            "A7FF8_AUTH_DECISION": "PASS_A7LS2_FIRST_CHECKPOINT_MATERIALIZATION_READY",
            "A7FF8_MATERIALIZE_CAP": str(rows_per_shard),
            "A7FF8_FAST_NUMERIC_CAP": str(rows_per_shard),
            "A7FF8_PORTFOLIO_CAP": "64",
            "A7FF8_QUEUE_LIMIT": str(rows_per_shard),
            "A7FF8_WRITE_CONTROL_DETAIL": "1",
        },
        "checkpoint_policy": {
            "rows_per_shard": rows_per_shard,
            "shard_count": int(shard_plan["company_numeric_shard"].nunique()),
            "resume_rule": "skip shard if manifest exists and returncode==0",
            "timeout_seconds_per_shard": 3600,
            "parallelism_recommended": "4-8 shards depending on company-machine memory",
        },
    }
    write_json(RUNTIME / "a7ls3h_company_command_template.json", command_template)

    blockers: list[str] = []
    if ls3.get("decision") != "HOLD_A7LS3_NUMERIC_CHECKPOINT_WEAK":
        blockers.append("local_a7ls3_timeout_record_missing_or_unexpected")
    if len(handoff) < 512:
        blockers.append("handoff_queue_lt_512")
    if handoff["a7ls_arm"].nunique() < 4:
        blockers.append("handoff_not_all_arms")
    decision = "PASS_A7LS3H_COMPANY_NUMERIC_HANDOFF_READY" if not blockers else "HOLD_A7LS3H_HANDOFF_WEAK"
    manifest = {
        "stage": "A7LS-3H",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_a7ls2_decision": ls2.get("decision"),
        "source_local_a7ls3_decision": ls3.get("decision"),
        "local_a7ls3_timeout": "numeric_probe_timeout" in ls3.get("blockers", []),
        "input_activity_ok_rows": int(len(ok)),
        "handoff_queue_rows": int(len(handoff)),
        "shard_count": int(shard_plan["company_numeric_shard"].nunique()),
        "rows_per_shard": rows_per_shard,
        "arm_count": int(handoff["a7ls_arm"].nunique()),
        "executes_numeric_probe": False,
        "executes_search": False,
        "authorizes_company_numeric_async": decision.startswith("PASS_"),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls3h_manifest.json", manifest)
    write_json(RUNTIME / "a7ls3h_decision_record.json", manifest)

    REPORT.write_text("\n".join([
        "# CRYPTO A7LS-3H COMPANY NUMERIC HANDOFF",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7LS-3H converts the local A7LS-3 timeout into a company-machine async numeric handoff. It uses A7LS-2 activity-ok materialized rows, cuts 32-row shards, and records resume/checkpoint rules.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Queue Summary",
        "",
        md_table(queue_summary, 80),
        "",
        "## Shard Plan",
        "",
        md_table(shard_plan, 80),
        "",
        "## Command Template",
        "",
        "```json",
        json.dumps(command_template, indent=2, sort_keys=True),
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "handoff generated: true",
        "local numeric execution: not in this stage",
        "search/proof/shadow/live: false",
        "```",
    ]), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
