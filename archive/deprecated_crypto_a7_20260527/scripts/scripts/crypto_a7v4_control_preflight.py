from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
A7V3_DIR = ROOT / "runtime" / "a7v3_agg_aware_candidate_dry_run"
OUT_DIR = ROOT / "runtime" / "a7v4_control_preflight"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7V4_CONTROL_PREFLIGHT_20260522.md"

REPLAY_CONTROL_MODES = ["row_shuffle", "time_shuffle", "wrong_lag", "sign_flip"]
BLOCKED_CONTROL_MODES = ["no_agg_mask", "zero_fill_core12_rank", "same_hour_execution_lag0"]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def stable_id(*parts: Any, length: int = 14) -> str:
    text = "|".join(str(part) for part in parts)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def read_candidates() -> pd.DataFrame:
    path = A7V3_DIR / "a7v3_candidates.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    return df[df["decision"].eq("A7V3_DRY_RUN_CANDIDATE")].copy()


def replay_control_variant(candidate: pd.Series, mode: str) -> dict[str, Any]:
    cid = str(candidate["candidate_id"])
    control_id = f"{cid}__ctrl_{mode}_{stable_id(cid, mode, length=8)}"
    expected = {
        "row_shuffle": "candidate edge should disappear versus original if signal depends on aligned features",
        "time_shuffle": "candidate edge should disappear if temporal order matters",
        "wrong_lag": "candidate must not improve versus original under stale/future timing displacement",
        "sign_flip": "return orientation should invert or materially degrade",
    }[mode]
    return {
        "control_id": control_id,
        "base_candidate_id": cid,
        "control_mode": mode,
        "control_class": "replay_negative_control",
        "expression": str(candidate["expression"]),
        "production_family": str(candidate["production_family"]),
        "horizon": int(candidate["horizon"]),
        "availability_mask": "agg_features_available",
        "uses_same_mask_as_candidate": True,
        "feature_available_lag_bars": int(candidate["feature_available_lag_bars"]),
        "promotable": False,
        "allowed_in_a7v5_replay": True,
        "expected_behavior": expected,
        "decision": "A7V4_REPLAY_CONTROL_READY",
    }


def blocked_control_variant(candidate: pd.Series, mode: str) -> dict[str, Any]:
    cid = str(candidate["candidate_id"])
    expression = str(candidate["expression"])
    if mode == "no_agg_mask":
        reason = "agg candidates must require agg_features_available"
        modified_expression = expression
        availability_mask = ""
        lag = int(candidate["feature_available_lag_bars"])
    elif mode == "zero_fill_core12_rank":
        reason = "missing agg rows cannot be converted into core12 zero-fill cross-sectional ranks"
        modified_expression = f"CrossSymbolRank(ZeroFill({expression}))"
        availability_mask = "agg_features_available"
        lag = int(candidate["feature_available_lag_bars"])
    else:
        reason = "same-hour close execution is forbidden for hourly aggTrades features"
        modified_expression = expression
        availability_mask = "agg_features_available"
        lag = 0
    return {
        "control_id": f"{cid}__blocked_{mode}_{stable_id(cid, mode, length=8)}",
        "base_candidate_id": cid,
        "control_mode": mode,
        "control_class": "blocked_before_replay",
        "expression": modified_expression,
        "production_family": str(candidate["production_family"]),
        "horizon": int(candidate["horizon"]),
        "availability_mask": availability_mask,
        "uses_same_mask_as_candidate": bool(availability_mask == "agg_features_available"),
        "feature_available_lag_bars": lag,
        "promotable": False,
        "allowed_in_a7v5_replay": False,
        "block_reason": reason,
        "decision": "A7V4_BLOCKED_EXPECTED_CONTROL",
    }


def build_controls(candidates: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    replay_rows = []
    blocked_rows = []
    for _, candidate in candidates.iterrows():
        for mode in REPLAY_CONTROL_MODES:
            replay_rows.append(replay_control_variant(candidate, mode))
        for mode in BLOCKED_CONTROL_MODES:
            blocked_rows.append(blocked_control_variant(candidate, mode))
    return pd.DataFrame(replay_rows), pd.DataFrame(blocked_rows)


def build_candidate_coverage(candidates: pd.DataFrame, replay_controls: pd.DataFrame, blocked_controls: pd.DataFrame) -> pd.DataFrame:
    replay_counts = replay_controls.groupby("base_candidate_id")["control_mode"].nunique().rename("replay_control_modes")
    blocked_counts = blocked_controls.groupby("base_candidate_id")["control_mode"].nunique().rename("blocked_control_modes")
    cov = candidates[["candidate_id", "production_family", "horizon", "source_fields", "availability_mask", "feature_available_lag_bars"]].copy()
    cov = cov.merge(replay_counts, left_on="candidate_id", right_index=True, how="left")
    cov = cov.merge(blocked_counts, left_on="candidate_id", right_index=True, how="left")
    cov["replay_control_modes"] = cov["replay_control_modes"].fillna(0).astype(int)
    cov["blocked_control_modes"] = cov["blocked_control_modes"].fillna(0).astype(int)
    cov["has_all_replay_controls"] = cov["replay_control_modes"].eq(len(REPLAY_CONTROL_MODES))
    cov["has_all_blocked_controls"] = cov["blocked_control_modes"].eq(len(BLOCKED_CONTROL_MODES))
    cov["decision"] = cov.apply(
        lambda row: "PASS" if row["has_all_replay_controls"] and row["has_all_blocked_controls"] else "HOLD_MISSING_CONTROL_COVERAGE",
        axis=1,
    )
    return cov


def build_policy_audit(candidates: pd.DataFrame, replay_controls: pd.DataFrame, blocked_controls: pd.DataFrame, coverage: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "gate": "candidate_count",
            "value": int(len(candidates)),
            "decision": "PASS" if len(candidates) > 0 else "HOLD",
        },
        {
            "gate": "all_candidates_have_replay_controls",
            "value": bool(coverage["has_all_replay_controls"].all()),
            "decision": "PASS" if coverage["has_all_replay_controls"].all() else "HOLD",
        },
        {
            "gate": "all_candidates_have_blocked_controls",
            "value": bool(coverage["has_all_blocked_controls"].all()),
            "decision": "PASS" if coverage["has_all_blocked_controls"].all() else "HOLD",
        },
        {
            "gate": "replay_controls_promotable",
            "value": bool(replay_controls["promotable"].any()),
            "decision": "PASS" if not replay_controls["promotable"].any() else "HOLD",
        },
        {
            "gate": "blocked_controls_allowed_in_replay",
            "value": bool(blocked_controls["allowed_in_a7v5_replay"].any()),
            "decision": "PASS" if not blocked_controls["allowed_in_a7v5_replay"].any() else "HOLD",
        },
        {
            "gate": "replay_controls_use_agg_mask",
            "value": bool(replay_controls["uses_same_mask_as_candidate"].all()),
            "decision": "PASS" if replay_controls["uses_same_mask_as_candidate"].all() else "HOLD",
        },
        {
            "gate": "blocked_no_mask_present",
            "value": int(blocked_controls["control_mode"].eq("no_agg_mask").sum()),
            "decision": "PASS" if int(blocked_controls["control_mode"].eq("no_agg_mask").sum()) == len(candidates) else "HOLD",
        },
        {
            "gate": "blocked_zero_fill_present",
            "value": int(blocked_controls["control_mode"].eq("zero_fill_core12_rank").sum()),
            "decision": "PASS" if int(blocked_controls["control_mode"].eq("zero_fill_core12_rank").sum()) == len(candidates) else "HOLD",
        },
        {
            "gate": "blocked_same_hour_present",
            "value": int(blocked_controls["control_mode"].eq("same_hour_execution_lag0").sum()),
            "decision": "PASS" if int(blocked_controls["control_mode"].eq("same_hour_execution_lag0").sum()) == len(candidates) else "HOLD",
        },
    ]
    return pd.DataFrame(rows)


def write_report(
    *,
    now: str,
    candidates: pd.DataFrame,
    replay_controls: pd.DataFrame,
    blocked_controls: pd.DataFrame,
    coverage: pd.DataFrame,
    policy_audit: pd.DataFrame,
    authorization: dict[str, Any],
) -> None:
    summary = (
        coverage.groupby("production_family")
        .agg(
            candidates=("candidate_id", "count"),
            replay_control_modes_min=("replay_control_modes", "min"),
            blocked_control_modes_min=("blocked_control_modes", "min"),
            all_pass=("decision", lambda s: bool((s == "PASS").all())),
        )
        .reset_index()
    )
    control_summary = (
        pd.concat([replay_controls[["control_mode", "control_class", "decision"]], blocked_controls[["control_mode", "control_class", "decision"]]], ignore_index=True)
        .groupby(["control_class", "control_mode", "decision"])
        .size()
        .reset_index(name="rows")
    )
    lines = [
        "# Crypto A7V-4 Control Preflight",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "A7V-4 creates the required control specifications for the A7V-3 agg-aware candidates. It does not evaluate returns. Replay controls are allowed only as non-promotable negative controls; no-mask, zero-fill, and same-hour controls are blocked before replay.",
        "",
        "## Candidate Control Coverage",
        "",
        table(summary, max_rows=40),
        "",
        "## Control Summary",
        "",
        table(control_summary, max_rows=80),
        "",
        "## Policy Audit",
        "",
        table(policy_audit, max_rows=80),
        "",
        "## Sample Replay Controls",
        "",
        table(replay_controls.head(20), max_rows=20),
        "",
        "## Sample Blocked Controls",
        "",
        table(blocked_controls.head(20), max_rows=20),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- A7V-5: small agg-aware replay smoke using a capped subset of A7V-3 candidates plus A7V-4 replay controls.",
        "- A7V-5 must keep controls non-promotable and must keep May stress-only.",
        "- Full search, alpha proof, shadow, paper, and live remain blocked.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    candidates = read_candidates()
    replay_controls, blocked_controls = build_controls(candidates)
    coverage = build_candidate_coverage(candidates, replay_controls, blocked_controls)
    policy_audit = build_policy_audit(candidates, replay_controls, blocked_controls, coverage)

    blockers = []
    if not policy_audit["decision"].eq("PASS").all():
        blockers.append("control_policy_audit_failed")
    if not coverage["decision"].eq("PASS").all():
        blockers.append("candidate_control_coverage_incomplete")
    if replay_controls["promotable"].any():
        blockers.append("replay_control_promotable")
    if blocked_controls["allowed_in_a7v5_replay"].any():
        blockers.append("blocked_control_allowed_in_replay")

    decision = "PASS_A7V4_CONTROL_PREFLIGHT" if not blockers else "HOLD_A7V4_CONTROL_PREFLIGHT"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "candidate_count": int(len(candidates)),
        "replay_control_count": int(len(replay_controls)),
        "blocked_control_count": int(len(blocked_controls)),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7v5_small_replay_smoke": decision.startswith("PASS"),
        "authorizes_full_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_control_promotion": False,
        "authorizes_no_mask_replay": False,
        "authorizes_zero_fill_replay": False,
        "authorizes_same_hour_execution": False,
        "required_next": [
            "A7V-5 small agg-aware replay smoke with capped candidates and non-promotable controls",
            "May remains stress-only and cannot enter ranking or candidate selection",
            "A7U-0R consolidated raw checksum trace before final alpha panel claims",
        ],
    }

    replay_controls.to_csv(OUT_DIR / "a7v4_replay_control_specs.csv", index=False)
    blocked_controls.to_csv(OUT_DIR / "a7v4_blocked_control_specs.csv", index=False)
    coverage.to_csv(OUT_DIR / "a7v4_candidate_control_coverage.csv", index=False)
    policy_audit.to_csv(OUT_DIR / "a7v4_control_policy_audit.csv", index=False)
    write_json(OUT_DIR / "a7v4_authorization_matrix.json", authorization)
    write_json(OUT_DIR / "a7v4_manifest.json", {"generated_at": now, "decision": decision, "output_dir": str(OUT_DIR)})
    write_report(
        now=now,
        candidates=candidates,
        replay_controls=replay_controls,
        blocked_controls=blocked_controls,
        coverage=coverage,
        policy_audit=policy_audit,
        authorization=authorization,
    )
    print(json.dumps({"decision": decision, "blockers": blockers, "replay_controls": len(replay_controls), "blocked_controls": len(blocked_controls)}, indent=2))


if __name__ == "__main__":
    main()
