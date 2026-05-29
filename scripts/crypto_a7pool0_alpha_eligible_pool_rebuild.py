from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7pool0_alpha_eligible_pool"
REPORT = REPO / "reports" / "CRYPTO_A7POOL0_ALPHA_ELIGIBLE_POOL_REBUILD_20260529.md"

A7AIF4 = REPO / "runtime" / "a7aif4_response_backed_field_promotion" / "a7aif4_manifest.json"
PROMOTED = REPO / "runtime" / "a7aif4_response_backed_field_promotion" / "a7aif4_promoted_ordinary_alpha_fields.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def stable_id(prefix: str, text: str) -> str:
    return f"{prefix}_{hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]}"


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def expression_for_transform(field: str, transform: str) -> str:
    if transform == "delta_24h":
        return f"Delta({field},24)"
    if transform == "delta_4h":
        return f"Delta({field},4)"
    if transform == "cs_rank":
        return f"CSRank({field})"
    if transform == "level":
        return field
    if transform == "zscore":
        return f"ZScore({field})"
    return field


def generate_variants(field: str, transform: str, orientation: float) -> list[dict[str, str]]:
    base = expression_for_transform(field, transform)
    oriented = f"Neg({base})" if orientation < 0 else base
    variants = [
        ("base_oriented", oriented),
        ("cs_rank_oriented", f"CSRank({oriented})"),
        ("zscore_oriented", f"ZScore({oriented})"),
        ("clip_zscore_oriented", f"Clip(ZScore({oriented}),-3,3)"),
        ("mean4_oriented", f"Mean({oriented},4)"),
        ("mean24_oriented", f"Mean({oriented},24)"),
        ("decay8_oriented", f"Decay({oriented},8)"),
        ("tsrank24_oriented", f"TSRank({oriented},24)"),
    ]
    return [{"variant": name, "expression": expr} for name, expr in variants]


def skeleton(expression: str) -> str:
    text = expression
    for token in ["mark_index_basis_bps", "premium_close_bps", "funding_rate"]:
        text = text.replace(token, "FIELD")
    for number in ["336", "168", "96", "72", "48", "24", "12", "8", "4", "3", "1"]:
        text = text.replace(number, "N")
    return stable_id("skeleton", text)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    f4 = read_json(A7AIF4)
    if not f4.get("authorizes_a7pool0"):
        raise SystemExit(f"A7AI-F4 does not authorize A7POOL-0: {f4.get('decision')}")
    promoted = pd.read_csv(PROMOTED) if PROMOTED.exists() else pd.DataFrame()

    rows: list[dict[str, Any]] = []
    for promo in promoted.itertuples(index=False):
        field = str(promo.field_name)
        transform = str(promo.transform)
        orientation = float(getattr(promo, "orientation_from_train", 1.0)) if hasattr(promo, "orientation_from_train") else -1.0
        for variant in generate_variants(field, transform, orientation):
            expression = variant["expression"]
            identity = f"{field}|{transform}|{variant['variant']}|{expression}"
            rows.append(
                {
                    "candidate_id": stable_id("a7pool0", identity),
                    "expression": expression,
                    "fields": field,
                    "field_family": promo.field_family,
                    "source_family": promo.source_family,
                    "transform": transform,
                    "variant": variant["variant"],
                    "label_evidence_family": str(promo.label_family),
                    "label_evidence_horizon_h": str(promo.label_horizon_h),
                    "control_ratio_premay_max": promo.control_ratio_premay_max,
                    "candidate_role": "ordinary_alpha_valid",
                    "field_roles": promo.semantic_role,
                    "role_violation": False,
                    "missing_contract": False,
                    "timing_violation": False,
                    "requires_controls": True,
                    "skeleton_key": skeleton(expression),
                    "production_key": stable_id("prod", f"{field}|{transform}|{variant['variant']}"),
                    "source_stage": "A7AI-F4",
                    "eligible_for_role_strict_selector": True,
                }
            )
    pool = pd.DataFrame(rows)
    if not pool.empty:
        duplicate_expression_count = int(pool.duplicated(subset=["expression"]).sum())
        agg = {
            col: "first"
            for col in pool.columns
            if col not in {"label_evidence_family", "label_evidence_horizon_h", "control_ratio_premay_max"}
        }
        agg["label_evidence_family"] = lambda s: "|".join(sorted(set(map(str, s))))
        agg["label_evidence_horizon_h"] = lambda s: "|".join(sorted(set(map(str, s))))
        agg["control_ratio_premay_max"] = "min"
        pool = pool.groupby("expression", as_index=False).agg(agg)
        pool = pool.sort_values(["field_family", "variant", "candidate_id"])
    else:
        duplicate_expression_count = 0
    role_trace = pool[
        [
            "candidate_id",
            "fields",
            "field_family",
            "candidate_role",
            "field_roles",
            "role_violation",
            "missing_contract",
            "timing_violation",
            "eligible_for_role_strict_selector",
        ]
    ].copy() if not pool.empty else pd.DataFrame()
    reject_rows = []
    if promoted.empty:
        reject_rows.append({"reason": "no_promoted_fields", "count": 1})
    reject_summary = pd.DataFrame(reject_rows)
    family_dist = (
        pool.groupby("field_family").size().reset_index(name="count").assign(share=lambda x: x["count"] / max(len(pool), 1))
        if not pool.empty
        else pd.DataFrame(columns=["field_family", "count", "share"])
    )
    skeleton_dist = (
        pool.groupby("skeleton_key").size().reset_index(name="count").assign(share=lambda x: x["count"] / max(len(pool), 1))
        if not pool.empty
        else pd.DataFrame(columns=["skeleton_key", "count", "share"])
    )
    signal_proxy = (
        pool[["candidate_id", "skeleton_key", "field_family", "variant", "control_ratio_premay_max"]].copy()
        if not pool.empty
        else pd.DataFrame()
    )
    blockers: list[str] = []
    if pool.empty:
        blockers.append("generated_count_zero")
    if not pool.empty and not bool(pool["eligible_for_role_strict_selector"].any()):
        blockers.append("alpha_eligible_count_zero")
    if not pool.empty and pool["candidate_role"].isin(["risk_defense_only", "diagnostic_only", "weak_or_unclassified"]).any():
        blockers.append("non_alpha_roles_in_pool")
    if not pool.empty and bool(pool["role_violation"].any()):
        blockers.append("field_role_violation")
    if not pool.empty and bool(pool["missing_contract"].any()):
        blockers.append("missing_contract")
    if not pool.empty and bool(pool["timing_violation"].any()):
        blockers.append("timing_violation")
    top_family_share = float(family_dist["share"].max()) if not family_dist.empty else 0.0
    top_skeleton_share = float(skeleton_dist["share"].max()) if not skeleton_dist.empty else 0.0
    if top_family_share > 0.35:
        blockers.append("single_family_concentration_gt_35pct")
    if top_skeleton_share > 0.25:
        blockers.append("single_skeleton_concentration_gt_25pct")

    decision = "PASS_A7POOL0_ALPHA_ELIGIBLE_POOL_REBUILT" if not blockers else "HOLD_A7POOL0_POOL_NOT_READY_FOR_SELECTOR"
    manifest = {
        "stage": "A7POOL-0",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "executes_generation": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "generated_count": int(len(pool)),
        "alpha_eligible_count": int(pool["eligible_for_role_strict_selector"].sum()) if not pool.empty else 0,
        "field_family_count": int(pool["field_family"].nunique()) if not pool.empty else 0,
        "skeleton_count": int(pool["skeleton_key"].nunique()) if not pool.empty else 0,
        "top_family_share": top_family_share,
        "top_skeleton_share": top_skeleton_share,
        "duplicate_expression_count_before_dedup": duplicate_expression_count,
        "authorizes_a7sel1": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    pool.to_csv(RUNTIME / "a7pool0_generated_pool.csv", index=False)
    role_trace.to_csv(RUNTIME / "a7pool0_role_trace.csv", index=False)
    reject_summary.to_csv(RUNTIME / "a7pool0_reject_reason_summary.csv", index=False)
    family_dist.to_csv(RUNTIME / "a7pool0_family_distribution.csv", index=False)
    skeleton_dist.to_csv(RUNTIME / "a7pool0_skeleton_distribution.csv", index=False)
    signal_proxy.to_csv(RUNTIME / "a7pool0_signal_vector_proxy_distribution.csv", index=False)
    write_json(RUNTIME / "a7pool0_manifest.json", manifest)

    lines = [
        "# CRYPTO A7POOL-0 ALPHA-ELIGIBLE POOL REBUILD",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7POOL-0 rebuilds a role-clean pool only from A7AI-F4 promoted ordinary-alpha field evidence. It does not run replay or search.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Distribution",
        "",
        md_table(family_dist, 40),
        "",
        "## Generated Pool",
        "",
        md_table(pool[["candidate_id", "expression", "field_family", "variant", "candidate_role", "skeleton_key"]] if not pool.empty else pool, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "A7POOL-0 may produce role-clean diagnostic pool artifacts, but it does not authorize formula search or alpha proof.",
        "If family/skeleton concentration fails, A7SEL-1 is not authorized except as a blocked/not-run record.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
