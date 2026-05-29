from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff7e_expanded_derivation_probe_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF7E_EXPANDED_DERIVATION_PROBE_CONTRACT_20260530.md"

ROLE_MAP = REPO / "runtime" / "a7ff4_feature_role_promotion" / "a7ff4_feature_role_map_v2.csv"
PAIR_POLICY = REPO / "runtime" / "a7ff2_feature_pair_clustering" / "a7ff2_feature_pair_policy.csv"
A7FF6 = REPO / "runtime" / "a7ff6_portfolio_marginal_selector_dryrun" / "a7ff6_manifest.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_id(prefix: str, text: str) -> str:
    return f"{prefix}_{hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]}"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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
    return view.to_markdown(index=False)


def transform_expr(field: str, transform: str) -> str:
    if transform == "level":
        return field
    if transform == "delta_1h":
        return f"Delta({field},1)"
    if transform == "delta_4h":
        return f"Delta({field},4)"
    if transform == "delta_12h":
        return f"Delta({field},12)"
    if transform == "delta_24h":
        return f"Delta({field},24)"
    if transform == "delta_48h":
        return f"Delta({field},48)"
    if transform == "zscore":
        return f"ZScore({field})"
    if transform == "csrank":
        return f"CSRank({field})"
    if transform == "abs_zscore":
        return f"Abs(ZScore({field}))"
    if transform == "sign_delta_24h":
        return f"Sign(Delta({field},24))"
    if transform == "tsrank_24h":
        return f"TSRank({field},24)"
    if transform == "tsrank_168h":
        return f"TSRank({field},168)"
    if transform == "decay_8h":
        return f"Decay({field},8)"
    if transform == "decay_24h":
        return f"Decay({field},24)"
    if transform == "mean_4h":
        return f"Mean({field},4)"
    if transform == "mean_24h":
        return f"Mean({field},24)"
    if transform == "winsor_zscore":
        return f"Clip(ZScore({field}),-3,3)"
    return field


def transforms_for_semantic(semantic_type: str, role: str) -> list[str]:
    base = ["level", "delta_4h", "delta_24h", "zscore", "csrank", "winsor_zscore"]
    if semantic_type == "basis_premium_like":
        return base + ["delta_1h", "delta_12h", "delta_48h", "abs_zscore", "tsrank_24h", "decay_8h", "decay_24h", "mean_4h", "mean_24h"]
    if semantic_type == "positioning_like":
        return base + ["delta_1h", "delta_12h", "delta_48h", "sign_delta_24h", "tsrank_168h", "decay_24h", "mean_24h"]
    if semantic_type == "volatility_like":
        return base + ["abs_zscore", "tsrank_24h", "tsrank_168h", "decay_24h"]
    if semantic_type == "price_like":
        return ["delta_1h", "delta_4h", "delta_24h", "zscore", "csrank", "tsrank_24h", "decay_8h", "mean_24h"]
    if semantic_type == "rate_like":
        return ["level", "delta_24h", "zscore", "abs_zscore", "sign_delta_24h", "mean_24h"]
    return base


def interaction_expr(left: str, right: str, motif: str) -> str:
    if motif == "mul":
        return f"Mul({left},{right})"
    if motif == "sub":
        return f"Sub({left},{right})"
    if motif == "safe_div_abs":
        return f"SafeDiv({left},Abs({right}))"
    if motif == "spread_rank":
        return f"Sub(CSRank({left}),CSRank({right}))"
    if motif == "gated_sign":
        return f"Mul({left},Sign({right}))"
    if motif == "smooth_interaction":
        return f"Mean(Mul({left},{right}),4)"
    if motif == "relative_shock":
        return f"Mul(Delta({left},4),ZScore({right}))"
    return f"Mul({left},{right})"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    role_map = pd.read_csv(ROLE_MAP)
    pair_policy = pd.read_csv(PAIR_POLICY)
    a7ff6 = read_json(A7FF6)

    signal = role_map[role_map["new_factor_role"].eq("promote_to_signal_candidate")].copy()
    context = role_map[role_map["new_factor_role"].eq("promote_to_regime_or_interaction_input")].copy()
    if signal.empty:
        raise SystemExit("No promoted signal seed available for expanded derivation.")

    pair_lookup = {}
    for row in pair_policy.itertuples(index=False):
        pair_lookup[(row.left_field, row.right_field)] = (row.pair_policy, row.policy_reason, row.semantic_pair)
        pair_lookup[(row.right_field, row.left_field)] = (row.pair_policy, row.policy_reason, row.semantic_pair)

    blueprints: list[dict[str, Any]] = []
    for sig in signal.itertuples(index=False):
        sig_transforms = transforms_for_semantic(sig.semantic_type, sig.new_factor_role)
        for st in sig_transforms:
            sig_expr = transform_expr(sig.field_name, st)
            blueprints.append(
                {
                    "blueprint_id": stable_id("a7ff7e", f"F1|{sig.field_name}|{st}|{sig_expr}"),
                    "layer": "F1_single_field_expanded",
                    "primary_field": sig.field_name,
                    "secondary_field": "",
                    "primary_transform": st,
                    "secondary_transform": "",
                    "motif": "single",
                    "expression": sig_expr,
                    "semantic_pair": sig.semantic_type,
                    "pair_policy": "single_signal_seed",
                    "candidate_role": "ordinary_alpha_valid",
                    "requires_controls": True,
                    "numeric_probe_priority": "P0",
                }
            )
        for ctx in context.itertuples(index=False):
            pair = pair_lookup.get((sig.field_name, ctx.field_name), ("manual_anchor_interaction", "signal_seed_anchor", f"{sig.semantic_type}|{ctx.semantic_type}"))
            pair_policy_value, policy_reason, semantic_pair = pair
            ctx_transforms = transforms_for_semantic(ctx.semantic_type, ctx.new_factor_role)
            motifs = ["mul", "sub", "spread_rank", "gated_sign", "smooth_interaction", "relative_shock"]
            if ctx.semantic_type in {"positioning_like", "volatility_like", "basis_premium_like"}:
                motifs.append("safe_div_abs")
            for st in sig_transforms[:10]:
                left = transform_expr(sig.field_name, st)
                for ct in ctx_transforms[:10]:
                    right = transform_expr(ctx.field_name, ct)
                    for motif in motifs:
                        expr = interaction_expr(left, right, motif)
                        priority = "P1"
                        if pair_policy_value == "cross_cluster_high_prior_interaction":
                            priority = "P0"
                        if ctx.compiler_role == "risk_exposure_or_neutralizer":
                            priority = "P1"
                        blueprints.append(
                            {
                                "blueprint_id": stable_id("a7ff7e", f"F2|{sig.field_name}|{ctx.field_name}|{st}|{ct}|{motif}|{expr}"),
                                "layer": "F2_expanded_typed_interaction",
                                "primary_field": sig.field_name,
                                "secondary_field": ctx.field_name,
                                "primary_transform": st,
                                "secondary_transform": ct,
                                "motif": motif,
                                "expression": expr,
                                "semantic_pair": semantic_pair,
                                "pair_policy": pair_policy_value,
                                "pair_policy_reason": policy_reason,
                                "candidate_role": "role_mixed_allowed",
                                "requires_controls": True,
                                "numeric_probe_priority": priority,
                            }
                        )

    pool = pd.DataFrame(blueprints).drop_duplicates(subset=["expression"]).sort_values(
        ["numeric_probe_priority", "semantic_pair", "primary_field", "secondary_field", "motif", "blueprint_id"]
    )
    pool["skeleton_key"] = pool["expression"].str.replace(r"[A-Za-z_][A-Za-z0-9_]*", "TOK", regex=True).str.replace(r"\d+", "N", regex=True).map(lambda x: stable_id("skel", x))
    pool["production_key"] = pool.apply(lambda r: stable_id("prod", f"{r.primary_field}|{r.secondary_field}|{r.primary_transform}|{r.secondary_transform}|{r.motif}"), axis=1)
    pool["selected_for_a7ff8_numeric_probe"] = False

    # Larger but still bounded: prioritize P0, then fill by semantic/motif/skeleton diversity.
    selected_ids: set[str] = set()
    family_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    target = min(384, len(pool))
    for _, row in pool.iterrows():
        semantic = str(row["semantic_pair"])
        motif = str(row["motif"])
        skeleton = str(row["skeleton_key"])
        if family_counts.get(semantic, 0) >= 96:
            continue
        if motif_counts.get(motif, 0) >= 96:
            continue
        if skeleton_counts.get(skeleton, 0) >= 12:
            continue
        selected_ids.add(str(row["blueprint_id"]))
        family_counts[semantic] = family_counts.get(semantic, 0) + 1
        motif_counts[motif] = motif_counts.get(motif, 0) + 1
        skeleton_counts[skeleton] = skeleton_counts.get(skeleton, 0) + 1
        if len(selected_ids) >= target:
            break
    pool["selected_for_a7ff8_numeric_probe"] = pool["blueprint_id"].isin(selected_ids)

    family_summary = pool.groupby(["semantic_pair", "selected_for_a7ff8_numeric_probe"]).size().reset_index(name="count")
    motif_summary = pool.groupby(["motif", "selected_for_a7ff8_numeric_probe"]).size().reset_index(name="count")
    priority_summary = pool.groupby(["numeric_probe_priority", "selected_for_a7ff8_numeric_probe"]).size().reset_index(name="count")

    numeric_probe_plan = {
        "stage": "A7FF-8",
        "status": "contract_only_not_executed",
        "input_blueprint_source": "runtime/a7ff7e_expanded_derivation_probe_contract/a7ff7e_expanded_blueprint_pool.csv",
        "selected_blueprints": int(pool["selected_for_a7ff8_numeric_probe"].sum()),
        "materialize_cap": 384,
        "fast_numeric_probe_cap": 256,
        "control_probe_cap": 256,
        "portfolio_marginal_probe_cap": 128,
        "deep_audit_cap": 64,
        "labels": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return", "L7_ranked_future_return_diagnostic_only"],
        "horizons": ["1h", "4h", "8h", "24h"],
        "controls": ["wrong_lag_future", "wrong_lag_stale", "time_shuffle", "symbol_shuffle", "sign_flip", "same_family_placebo"],
        "required_outputs": [
            "a7ff8_materialization_metrics.csv",
            "a7ff8_label_response_metrics.csv",
            "a7ff8_control_dominance_metrics.csv",
            "a7ff8_nonoverlap_stats.csv",
            "a7ff8_portfolio_marginal_proxy.csv",
            "a7ff8_decision_record.json",
        ],
        "promotion_blockers": [
            "L7-only cannot promote",
            "control_ratio >= 1.0 blocks",
            "single semantic_pair > 35pct blocks",
            "single skeleton > 15pct blocks",
            "numeric replay required before any search authorization",
        ],
    }

    blockers: list[str] = []
    selected_count = int(pool["selected_for_a7ff8_numeric_probe"].sum())
    if selected_count < 128:
        blockers.append("selected_blueprints_lt_128")
    selected = pool[pool["selected_for_a7ff8_numeric_probe"]]
    if selected["semantic_pair"].nunique() < 4:
        blockers.append("semantic_pair_diversity_lt_4")
    if selected["motif"].nunique() < 5:
        blockers.append("motif_diversity_lt_5")
    decision = "PASS_A7FF7E_EXPANDED_DERIVATION_READY_FOR_A7FF8_NUMERIC_PROBE" if not blockers else "HOLD_A7FF7E_EXPANSION_INSUFFICIENT"

    manifest = {
        "stage": "A7FF-7E",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "previous_a7ff6_decision": a7ff6.get("decision"),
        "executes_generation": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "blueprint_count": int(len(pool)),
        "selected_for_numeric_probe": selected_count,
        "semantic_pair_count": int(pool["semantic_pair"].nunique()),
        "selected_semantic_pair_count": int(selected["semantic_pair"].nunique()) if selected_count else 0,
        "motif_count": int(pool["motif"].nunique()),
        "selected_motif_count": int(selected["motif"].nunique()) if selected_count else 0,
        "authorizes_a7ff8_numeric_probe_contract": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    pool.to_csv(RUNTIME / "a7ff7e_expanded_blueprint_pool.csv", index=False)
    selected.to_csv(RUNTIME / "a7ff7e_selected_numeric_probe_queue.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ff7e_semantic_pair_summary.csv", index=False)
    motif_summary.to_csv(RUNTIME / "a7ff7e_motif_summary.csv", index=False)
    priority_summary.to_csv(RUNTIME / "a7ff7e_priority_summary.csv", index=False)
    write_json(RUNTIME / "a7ff7e_numeric_probe_plan.json", numeric_probe_plan)
    write_json(RUNTIME / "a7ff7e_manifest.json", manifest)

    lines = [
        "# CRYPTO A7FF-7E EXPANDED DERIVATION PROBE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-7E deliberately expands derivation scale relative to A7FF-6. It creates a larger typed blueprint pool from one promoted signal seed plus regime/risk interaction inputs, but it still does not execute replay or search.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Numeric Probe Plan",
        "",
        "```json",
        json.dumps(numeric_probe_plan, indent=2, sort_keys=True),
        "```",
        "",
        "## Semantic Pair Summary",
        "",
        md_table(family_summary, 80),
        "",
        "## Motif Summary",
        "",
        md_table(motif_summary, 80),
        "",
        "## Selected Queue Sample",
        "",
        md_table(selected[["blueprint_id", "layer", "primary_field", "secondary_field", "primary_transform", "secondary_transform", "motif", "semantic_pair", "numeric_probe_priority"]], 80),
        "",
        "## Boundary",
        "",
        "```text",
        "This is a larger derivation and test contract, not alpha search.",
        "A7FF-8 numeric probe is required before any replay/search authorization.",
        "Risk-defense/regime fields are allowed as interaction inputs, not standalone alpha seeds.",
        "L7 ranked-return remains diagnostic-only for promotion.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
