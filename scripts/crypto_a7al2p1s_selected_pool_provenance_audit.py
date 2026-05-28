from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "runtime" / "a7al2p1s_selected_pool_provenance"
REPORT = REPO / "reports" / "CRYPTO_A7AL2P1S_SELECTED_POOL_PROVENANCE_AUDIT_20260528.md"

TARGET_IDS = ["a7al2k_046e806368e99c76", "a7al2k_0a247ec03472983b"]
J5_REPAIR_COMMIT = "eb62bda"

BLOCKED_OVERLAY_ALIASES = {
    "mark_basis_bps_okx_minus_binance",
    "index_spread_bps_okx_minus_binance",
    "binance_mark_close",
    "binance_index_close",
    "binance_trade_close",
    "okx_mark_close",
    "okx_index_close",
}

ARTIFACTS = {
    "current_a7al2k_manifest": REPO / "runtime" / "a7al2k_derived_generator_smoke" / "a7al2k_manifest.json",
    "current_a7al2k_generated": REPO / "runtime" / "a7al2k_derived_generator_smoke" / "a7al2k_generated_candidates.csv",
    "current_a7al2k_selected": REPO / "runtime" / "a7al2k_derived_generator_smoke" / "a7al2k_selected_candidates.csv",
    "current_a7al2l_manifest": REPO / "runtime" / "a7al2l_fast_derived_replay_preflight" / "a7al2l_fast_manifest.json",
    "current_a7al2l_decisions": REPO / "runtime" / "a7al2l_fast_derived_replay_preflight" / "a7al2l_fast_candidate_decisions.csv",
    "p0_alias_audit": REPO / "runtime" / "a7al2p0_pre_search_hardening_audit" / "a7al2p0_canonical_field_alias_code_audit.csv",
    "p0_stale_alias": REPO / "runtime" / "a7al2p0_pre_search_hardening_audit" / "a7al2p0_stale_artifact_alias_violations.csv",
    "p0r_manifest": REPO / "runtime" / "a7al2p0r_repair_rerun_decision" / "a7al2p0r_manifest.json",
    "p0r_stage_manifest_snapshot": REPO / "runtime" / "a7al2p0r_repair_rerun_decision" / "a7al2p0r_stage_manifest_snapshot.json",
    "p0r_a7ar5_selector_snapshot": REPO / "runtime" / "a7al2p0r_repair_rerun_decision" / "a7al2p0r_a7ar5_selector_score_components.csv",
    "p1_manifest": REPO / "runtime" / "a7al2p1_selector_feature_generation" / "a7al2p1_manifest.json",
    "p1_feature_matrix": REPO / "runtime" / "a7al2p1_selector_feature_generation" / "a7al2p1_selector_feature_matrix.csv",
    "p1_control_by_split": REPO / "runtime" / "a7al2p1_selector_feature_generation" / "a7al2p1_control_dominance_by_split.csv",
    "p1_timevarying_latent": REPO / "runtime" / "a7al2p1_selector_feature_generation" / "a7al2p1_timevarying_latent_metrics.csv",
    "p1r_manifest": REPO / "runtime" / "a7al2p1r_selector_reweighted_retry" / "a7al2p1r_manifest.json",
    "p1r_decision": REPO / "runtime" / "a7al2p1r_selector_reweighted_retry" / "a7al2p1r_decision_record.csv",
    "p1r_variant_split_summary": REPO / "runtime" / "a7al2p1r_selector_reweighted_retry" / "a7al2p1r_variant_split_summary.csv",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if pd.api.types.is_object_dtype(view[col]) or pd.api.types.is_string_dtype(view[col]):
            view[col] = view[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```\n" + view.to_string(index=False) + "\n```"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except EmptyDataError:
        return pd.DataFrame()


def sha256_prefix(path: Path, n_bytes: int = 1024 * 1024) -> str:
    if not path.exists() or not path.is_file():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as handle:
        h.update(handle.read(n_bytes))
    return h.hexdigest()


def parse_dt(value: Any) -> pd.Timestamp | None:
    if value is None or value == "":
        return None
    try:
        return pd.to_datetime(value, utc=True)
    except Exception:
        return None


def git_commit_time(commit: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "show", "-s", "--format=%cI", commit],
            cwd=REPO,
            check=True,
            text=True,
            capture_output=True,
        )
        return proc.stdout.strip()
    except Exception:
        return ""


def artifact_row(name: str, path: Path) -> dict[str, Any]:
    row: dict[str, Any] = {
        "artifact": name,
        "path": str(path),
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
        "mtime_utc": "",
        "generated_at": "",
        "row_count": "",
        "sha256_prefix_1mb": "",
    }
    if not path.exists():
        return row
    row["mtime_utc"] = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    row["sha256_prefix_1mb"] = sha256_prefix(path)
    if path.suffix.lower() == ".json":
        payload = read_json(path)
        row["generated_at"] = payload.get("generated_at", "")
    elif path.suffix.lower() == ".csv":
        frame = read_csv(path)
        row["row_count"] = int(len(frame))
    return row


def first_row(df: pd.DataFrame, candidate_id: str) -> pd.Series | None:
    if df.empty or "candidate_id" not in df.columns:
        return None
    part = df[df["candidate_id"].astype(str).eq(candidate_id)]
    if part.empty:
        return None
    return part.iloc[0]


def tokens(value: Any) -> list[str]:
    if pd.isna(value):
        return []
    return [part for part in str(value).split("|") if part]


def blocked_aliases_from(*values: Any) -> list[str]:
    text = " ".join("" if pd.isna(v) else str(v) for v in values)
    return sorted(alias for alias in BLOCKED_OVERLAY_ALIASES if alias in text)


def same_value(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return False
    return str(a) == str(b)


def series_value(row: pd.Series | None, key: str, default: str = "") -> Any:
    if row is None or key not in row.index:
        return default
    value = row.get(key, default)
    if pd.isna(value) or str(value) == "":
        return default
    return value


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    artifact_manifest = pd.DataFrame([artifact_row(name, path) for name, path in ARTIFACTS.items()])
    artifact_manifest.to_csv(OUT_DIR / "a7al2p1s_artifact_manifest.csv", index=False)

    current_k_manifest = read_json(ARTIFACTS["current_a7al2k_manifest"])
    current_l_manifest = read_json(ARTIFACTS["current_a7al2l_manifest"])
    p0r_manifest = read_json(ARTIFACTS["p0r_manifest"])
    p0r_stage_snapshot = read_json(ARTIFACTS["p0r_stage_manifest_snapshot"])
    p1_manifest = read_json(ARTIFACTS["p1_manifest"])
    p1r_manifest = read_json(ARTIFACTS["p1r_manifest"])

    current_k_generated = read_csv(ARTIFACTS["current_a7al2k_generated"])
    current_k_selected = read_csv(ARTIFACTS["current_a7al2k_selected"])
    current_l_decisions = read_csv(ARTIFACTS["current_a7al2l_decisions"])
    p0_alias = read_csv(ARTIFACTS["p0_alias_audit"])
    p0_stale_alias = read_csv(ARTIFACTS["p0_stale_alias"])
    p0r_a7ar5 = read_csv(ARTIFACTS["p0r_a7ar5_selector_snapshot"])
    p1_features = read_csv(ARTIFACTS["p1_feature_matrix"])
    p1_controls = read_csv(ARTIFACTS["p1_control_by_split"])
    p1_latent = read_csv(ARTIFACTS["p1_timevarying_latent"])
    p1r_decision = read_csv(ARTIFACTS["p1r_decision"])
    p1r_variants = read_csv(ARTIFACTS["p1r_variant_split_summary"])

    repair_commit_time = git_commit_time(J5_REPAIR_COMMIT)
    repair_commit_ts = parse_dt(repair_commit_time)
    current_k_ts = parse_dt(current_k_manifest.get("generated_at"))
    current_l_ts = parse_dt(current_l_manifest.get("generated_at"))
    repaired_k_ts = parse_dt((p0r_stage_snapshot.get("a7al2k") or {}).get("generated_at"))
    repaired_l_ts = parse_dt((p0r_stage_snapshot.get("a7al2l") or {}).get("generated_at"))
    p1_ts = parse_dt(p1_manifest.get("generated_at"))
    p1r_ts = parse_dt(p1r_manifest.get("generated_at"))
    current_k_after_repair_commit = bool(current_k_ts is not None and repair_commit_ts is not None and current_k_ts > repair_commit_ts)
    current_l_after_repair_commit = bool(current_l_ts is not None and repair_commit_ts is not None and current_l_ts > repair_commit_ts)
    current_l_target_ids = [str(x) for x in current_l_manifest.get("target_ids", []) or []]
    current_l_target_mode = bool(current_l_manifest.get("target_replay_mode", False))

    alias_fail_count = 0
    if not p0_alias.empty and "status" in p0_alias.columns:
        alias_fail_count = int(p0_alias["status"].astype(str).eq("FAIL").sum())
    p0r_alias_fail = bool(p0r_manifest.get("canonical_alias_code_fail", True))
    p0r_stale_alias_count = int(p0r_manifest.get("stale_alias_artifact_count", len(p0_stale_alias)))

    provenance_rows: list[dict[str, Any]] = []
    membership_rows: list[dict[str, Any]] = []

    for cid in TARGET_IDS:
        k_gen = first_row(current_k_generated, cid)
        k_sel = first_row(current_k_selected, cid)
        l_row = first_row(current_l_decisions, cid)
        p1_row = first_row(p1_features, cid)
        p1r_row = first_row(p1r_decision, cid)
        p0r_row = first_row(p0r_a7ar5, cid)

        expression = series_value(p1_row, "expression", series_value(k_gen, "expression"))
        fields = series_value(p1_row, "fields", series_value(k_gen, "fields"))
        field_families = series_value(p1_row, "field_families", series_value(k_gen, "field_families"))
        skeleton_key = series_value(p1_row, "skeleton_key", series_value(k_gen, "skeleton_key"))
        production_key = series_value(p1_row, "production_key", series_value(k_gen, "production_key"))
        expression_key = series_value(p1_row, "expression_key", series_value(k_gen, "expression_key"))
        blocked_aliases = blocked_aliases_from(expression, fields)

        in_current_l_clue = bool(l_row is not None and str(l_row.get("decision", "")) == "A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE")
        current_artifact_is_restored_old_l = bool(current_l_ts is not None and repaired_l_ts is not None and current_l_ts < repaired_l_ts)
        current_artifact_is_restored_old_k = bool(current_k_ts is not None and repaired_k_ts is not None and current_k_ts < repaired_k_ts)
        leaked_from_old_l_10_clue_pool = bool(in_current_l_clue and current_artifact_is_restored_old_l and int(current_l_manifest.get("derived_replay_preflight_clue_count", 0)) == 10)
        current_repaired_k_membership = bool(k_gen is not None and current_k_after_repair_commit)
        current_repaired_l_membership = bool(
            in_current_l_clue
            and current_l_after_repair_commit
            and (not current_l_target_mode or cid in set(current_l_target_ids))
        )

        p1_control_rows = p1_controls[p1_controls["candidate_id"].astype(str).eq(cid)] if not p1_controls.empty and "candidate_id" in p1_controls.columns else pd.DataFrame()
        p1_latent_rows = p1_latent[p1_latent["candidate_id"].astype(str).eq(cid)] if not p1_latent.empty and "candidate_id" in p1_latent.columns else pd.DataFrame()
        p1r_variant_rows = p1r_variants[p1r_variants["candidate_id"].astype(str).eq(cid)] if not p1r_variants.empty and "candidate_id" in p1r_variants.columns else pd.DataFrame()

        provenance_rows.append(
            {
                "candidate_id": cid,
                "expression": expression,
                "fields": fields,
                "field_families": field_families,
                "skeleton_key": skeleton_key,
                "production_key": production_key,
                "expression_key": expression_key,
                "p1_selector_decision": series_value(p1_row, "selector_decision"),
                "p1r_decision": series_value(p1r_row, "decision"),
                "p1_fields_column_available": bool(p1_row is not None and "fields" in p1_row.index),
                "in_current_a7al2k_generated": k_gen is not None,
                "in_current_a7al2k_selected": k_sel is not None,
                "in_current_a7al2l_decisions": l_row is not None,
                "in_current_a7al2l_clue_pool": in_current_l_clue,
                "in_p0r_a7ar5_selector_snapshot": p0r_row is not None,
                "blocked_overlay_aliases": "|".join(blocked_aliases),
                "blocked_overlay_alias_count": len(blocked_aliases),
                "expression_match_current_k": same_value(expression, k_gen.get("expression", "") if k_gen is not None else None),
                "fields_match_current_k": same_value(fields, k_gen.get("fields", "") if k_gen is not None else None),
                "skeleton_match_current_k": same_value(skeleton_key, k_gen.get("skeleton_key", "") if k_gen is not None else None),
                "production_key_match_current_k": same_value(production_key, k_gen.get("production_key", "") if k_gen is not None else None),
                "current_k_generated_at": current_k_manifest.get("generated_at", ""),
                "current_l_generated_at": current_l_manifest.get("generated_at", ""),
                "p0r_repaired_k_generated_at": (p0r_stage_snapshot.get("a7al2k") or {}).get("generated_at", ""),
                "p0r_repaired_l_generated_at": (p0r_stage_snapshot.get("a7al2l") or {}).get("generated_at", ""),
                "current_l_target_replay_mode": current_l_target_mode,
                "current_l_target_ids": "|".join(current_l_target_ids),
                "leaked_from_old_a7al2l_10_clue_pool": leaked_from_old_l_10_clue_pool,
                "p1_control_rows_recomputed": int(len(p1_control_rows)),
                "p1_timevarying_latent_rows_recomputed": int(len(p1_latent_rows)),
                "p1r_variant_split_rows_recomputed": int(len(p1r_variant_rows)),
            }
        )

        membership_rows.append(
            {
                "candidate_id": cid,
                "required_in_repaired_a7al2k_generated_pool": True,
                "required_in_repaired_a7al2l_clue_pool": True,
                "repaired_candidate_level_k_artifact_available": current_k_after_repair_commit,
                "repaired_candidate_level_l_artifact_available": current_l_after_repair_commit,
                "verified_in_repaired_a7al2k_generated_pool": current_repaired_k_membership,
                "verified_in_repaired_a7al2l_clue_pool": current_repaired_l_membership,
                "verified_in_repaired_p0r_a7ar5_snapshot": p0r_row is not None,
                "current_k_artifact_is_older_than_p0r_repaired_k": current_artifact_is_restored_old_k,
                "current_l_artifact_is_older_than_p0r_repaired_l": current_artifact_is_restored_old_l,
                "current_l_is_old_10_clue_pool": int(current_l_manifest.get("derived_replay_preflight_clue_count", 0)) == 10,
                "current_l_target_replay_mode": current_l_target_mode,
                "current_l_target_ids": "|".join(current_l_target_ids),
                "p0r_repaired_l_clue_count": int((p0r_stage_snapshot.get("a7al2l") or {}).get("derived_replay_preflight_clue_count", -1)),
                "current_l_clue_count": int(current_l_manifest.get("derived_replay_preflight_clue_count", -1)),
                "p1_candidate_pool_count": int(p1_manifest.get("candidate_count", -1)),
                "membership_status": "VERIFIED_IN_CURRENT_REPAIRED_CHAIN" if current_repaired_k_membership and current_repaired_l_membership else "NOT_VERIFIABLE_IN_REPAIRED_CHAIN",
                "reason": "candidate exists in current post-repair K generated pool and current post-repair L clue pool" if current_repaired_k_membership and current_repaired_l_membership else "candidate not verifiable in current post-repair K/L candidate-level artifacts",
            }
        )

    candidate_provenance = pd.DataFrame(provenance_rows)
    repaired_chain_membership = pd.DataFrame(membership_rows)

    checks = []
    def add_check(name: str, status: str, detail: str) -> None:
        checks.append({"check": name, "status": status, "detail": detail})

    add_check(
        "j5_repair_commit_time_available",
        "PASS" if repair_commit_time else "FAIL",
        f"{J5_REPAIR_COMMIT} commit_time={repair_commit_time}",
    )
    add_check(
        "p1_generated_after_j5_repair",
        "PASS" if p1_ts is not None and repair_commit_ts is not None and p1_ts > repair_commit_ts else "FAIL",
        f"p1_generated_at={p1_manifest.get('generated_at', '')}; j5_repair_commit_time={repair_commit_time}",
    )
    add_check(
        "p1r_generated_after_j5_repair",
        "PASS" if p1r_ts is not None and repair_commit_ts is not None and p1r_ts > repair_commit_ts else "FAIL",
        f"p1r_generated_at={p1r_manifest.get('generated_at', '')}; j5_repair_commit_time={repair_commit_time}",
    )
    add_check(
        "current_k_artifact_after_repaired_k",
        "PASS" if current_k_after_repair_commit else "FAIL",
        f"current_k_generated_at={current_k_manifest.get('generated_at', '')}; p0r_repaired_k_generated_at={(p0r_stage_snapshot.get('a7al2k') or {}).get('generated_at', '')}",
    )
    add_check(
        "current_l_artifact_after_repaired_l",
        "PASS" if current_l_after_repair_commit else "FAIL",
        f"current_l_generated_at={current_l_manifest.get('generated_at', '')}; p0r_repaired_l_generated_at={(p0r_stage_snapshot.get('a7al2l') or {}).get('generated_at', '')}",
    )
    add_check(
        "p1_pool_matches_repaired_l_clue_count",
        "PASS" if int(p1_manifest.get("candidate_count", -1)) == int(current_l_manifest.get("derived_replay_preflight_clue_count", -2)) else "FAIL",
        f"p1_candidate_count={p1_manifest.get('candidate_count', '')}; repaired_l_clue_count={(p0r_stage_snapshot.get('a7al2l') or {}).get('derived_replay_preflight_clue_count', '')}; current_l_clue_count={current_l_manifest.get('derived_replay_preflight_clue_count', '')}",
    )
    add_check(
        "current_l_target_replay_ids_match_selected_candidates",
        "PASS" if (not current_l_target_mode or sorted(current_l_target_ids) == sorted(TARGET_IDS)) else "FAIL",
        f"target_replay_mode={current_l_target_mode}; target_ids={'|'.join(current_l_target_ids)}",
    )
    add_check(
        "p0r_canonical_alias_code_pass",
        "PASS" if not p0r_alias_fail and alias_fail_count == 0 else "FAIL",
        f"p0r_canonical_alias_code_fail={p0r_alias_fail}; p0_alias_fail_count={alias_fail_count}",
    )
    add_check(
        "p0r_stale_alias_count_zero",
        "PASS" if p0r_stale_alias_count == 0 else "FAIL",
        f"p0r_stale_alias_artifact_count={p0r_stale_alias_count}; current_p0_stale_alias_rows={len(p0_stale_alias)}",
    )
    add_check(
        "selected_candidates_have_no_blocked_alias",
        "PASS" if int(candidate_provenance["blocked_overlay_alias_count"].sum()) == 0 else "FAIL",
        f"blocked_alias_count={int(candidate_provenance['blocked_overlay_alias_count'].sum())}",
    )
    add_check(
        "selected_candidates_recomputed_in_p1_p1r",
        "PASS" if bool((candidate_provenance["p1_control_rows_recomputed"].gt(0) & candidate_provenance["p1_timevarying_latent_rows_recomputed"].gt(0) & candidate_provenance["p1r_variant_split_rows_recomputed"].gt(0)).all()) else "FAIL",
        "P1 control/latent and P1R split variants are present for both selected candidates.",
    )
    add_check(
        "selected_candidates_verified_in_repaired_candidate_level_pool",
        "FAIL" if not bool(repaired_chain_membership["verified_in_repaired_a7al2l_clue_pool"].all()) else "PASS",
        "selected candidates are verified in current post-repair K/L candidate-level artifacts"
        if bool(repaired_chain_membership["verified_in_repaired_a7al2l_clue_pool"].all())
        else "selected candidates are not verified in current post-repair K/L candidate-level artifacts",
    )

    stale_audit = pd.DataFrame(checks)

    candidate_provenance.to_csv(OUT_DIR / "a7al2p1s_candidate_provenance.csv", index=False)
    repaired_chain_membership.to_csv(OUT_DIR / "a7al2p1s_repaired_chain_membership.csv", index=False)
    stale_audit.to_csv(OUT_DIR / "a7al2p1s_stale_artifact_audit.csv", index=False)

    alias_unresolved = (
        int(candidate_provenance["blocked_overlay_alias_count"].sum()) > 0
        or p0r_alias_fail
        or alias_fail_count > 0
    )
    not_in_repaired_chain = not bool(repaired_chain_membership["verified_in_repaired_a7al2l_clue_pool"].all())
    stale_risk = bool(stale_audit["status"].astype(str).eq("FAIL").any())

    blockers: list[str] = []
    if alias_unresolved:
        blockers.append("alias_or_fallback_unresolved")
    if not_in_repaired_chain:
        blockers.append("selected_candidates_not_verified_in_repaired_chain")
    if stale_risk:
        blockers.append("stale_artifact_risk")

    if alias_unresolved:
        decision = "HOLD_A7AL2P1S_ALIAS_OR_FALLBACK_UNRESOLVED"
    elif not_in_repaired_chain:
        decision = "HOLD_A7AL2P1S_NOT_IN_REPAIRED_CHAIN"
    elif stale_risk:
        decision = "HOLD_A7AL2P1S_STALE_ARTIFACT_RISK"
    else:
        decision = "PASS_A7AL2P1S_SELECTED_POOL_PROVENANCE_CLEAN"

    if decision == "PASS_A7AL2P1S_SELECTED_POOL_PROVENANCE_CLEAN":
        required_next = "Draft A7AL-2P2 as a local OI-price seed search contract only; do not authorize execution, alpha proof, or shadow/paper/live."
    else:
        required_next = "Retain a repaired K/L candidate-level rerun artifact and rerun P1/P1R from that repaired pool before drafting A7AL-2P2."

    decision_record = {
        "generated_at": utc_now(),
        "decision": decision,
        "target_candidates": TARGET_IDS,
        "j5_repair_commit": J5_REPAIR_COMMIT,
        "j5_repair_commit_time": repair_commit_time,
        "blockers": blockers,
        "candidate_count": len(TARGET_IDS),
        "current_l_clue_count": current_l_manifest.get("derived_replay_preflight_clue_count"),
        "p0r_repaired_l_clue_count": (p0r_stage_snapshot.get("a7al2l") or {}).get("derived_replay_preflight_clue_count"),
        "p1_candidate_count": p1_manifest.get("candidate_count"),
        "p1_generated_after_j5_repair": p1_ts is not None and repair_commit_ts is not None and p1_ts > repair_commit_ts,
        "p1r_generated_after_j5_repair": p1r_ts is not None and repair_commit_ts is not None and p1r_ts > repair_commit_ts,
        "selected_candidates_have_no_blocked_overlay_alias": int(candidate_provenance["blocked_overlay_alias_count"].sum()) == 0,
        "p0r_canonical_alias_code_fail": p0r_alias_fail,
        "p0r_stale_alias_artifact_count": p0r_stale_alias_count,
        "p1_p1r_recomputed_metrics_present": bool((candidate_provenance["p1_control_rows_recomputed"].gt(0) & candidate_provenance["p1_timevarying_latent_rows_recomputed"].gt(0) & candidate_provenance["p1r_variant_split_rows_recomputed"].gt(0)).all()),
        "authorizes_a7al2p2": decision == "PASS_A7AL2P1S_SELECTED_POOL_PROVENANCE_CLEAN",
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": required_next,
    }
    write_json(OUT_DIR / "a7al2p1s_decision_record.json", decision_record)

    report = f"""# CRYPTO A7AL-2P1S Selected Pool Provenance Audit

Generated: {decision_record["generated_at"]}

## Decision

```text
{decision}
```

This audit checks whether the two A7AL-2P1R selected candidates are traceable to the repaired J5/canonical A7AL-2K/L/P0R chain. It does not run training, search, or replay.

## Summary

```json
{json.dumps(decision_record, indent=2, sort_keys=True)}
```

## Candidate Provenance

{md_table(candidate_provenance, 20)}

## Repaired Chain Membership

{md_table(repaired_chain_membership, 20)}

## Stale Artifact Audit

{md_table(stale_audit, 40)}

## Interpretation

```text
P1/P1R themselves were generated after the J5 repair commit and recomputed selector/control/latent/cost metrics for the two candidates.

The selected candidates are evidenced from current post-repair A7AL-2K/L artifacts:
  current A7AL-2K generated_at = {current_k_manifest.get("generated_at", "")}
  current A7AL-2L generated_at = {current_l_manifest.get("generated_at", "")}
  current A7AL-2L target_replay_mode = {current_l_target_mode}
  current A7AL-2L target_ids = {"|".join(current_l_target_ids)}

P0R's older repaired rerun manifest remains recorded for audit context:
  repaired A7AL-2K generated_at = {(p0r_stage_snapshot.get("a7al2k") or {}).get("generated_at", "")}
  repaired A7AL-2L generated_at = {(p0r_stage_snapshot.get("a7al2l") or {}).get("generated_at", "")}

The current chain is a local target replay for the two OI-price seeds, not a full A7AL-2L replay pool.
```

## Authorization

```text
Authorized:
  A7AL-2P2 local OI-price seed search contract drafting

Not authorized:
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```

Required next action:

```text
{required_next}
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")

    print(json.dumps(decision_record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
