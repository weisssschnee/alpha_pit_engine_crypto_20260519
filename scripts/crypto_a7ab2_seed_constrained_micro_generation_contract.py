from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ab2_seed_constrained_micro_generation_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AB2_SEED_CONSTRAINED_MICRO_GENERATION_CONTRACT_20260529.md"

A7AB1_MANIFEST = REPO / "runtime" / "a7ab1_selector_rewrite_dryrun" / "a7ab1_manifest.json"
A7AB1_QUEUE = REPO / "runtime" / "a7ab1_selector_rewrite_dryrun" / "a7ab1_selector_queue.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ab1 = read_json(A7AB1_MANIFEST)
    if not a7ab1.get("authorizes_a7ab2_seed_constrained_micro_generation_contract"):
        raise SystemExit("A7AB-1 does not authorize A7AB-2")

    queue = pd.read_csv(A7AB1_QUEUE)
    if queue.empty:
        raise SystemExit("A7AB-1 selector queue is empty")

    seed_fields = sorted(queue["field_name"].astype(str).unique())
    seed_families = sorted(queue["field_family"].astype(str).unique())
    allowed_families = pd.DataFrame(
        [
            {
                "family_id": "G0_price_return_reversal",
                "required_seed_family": "price_return",
                "allowed_seed_fields": "trade_return_1h",
                "mechanism": "recent cross-sectional winners mean-revert over ranked future return labels",
                "allowed_transforms": "level|cs_rank|zscore|winsor|tsrank|decay",
                "allowed_interactions": "volatility_state|basis_premium_state",
            },
            {
                "family_id": "G1_volatility_state_reversal",
                "required_seed_family": "volatility",
                "allowed_seed_fields": "realized_vol_24h|realized_vol_168h",
                "mechanism": "high realized volatility state is tested as risk/reversal state, not standalone proof",
                "allowed_transforms": "level|cs_rank|zscore|winsor|tsrank|decay|horizon_spread",
                "allowed_interactions": "price_return_state|basis_premium_state",
            },
            {
                "family_id": "G2_basis_premium_dislocation",
                "required_seed_family": "basis_premium",
                "allowed_seed_fields": "premium_close_bps|mark_index_basis_bps",
                "mechanism": "basis/premium change is tested as dislocation/reversion state",
                "allowed_transforms": "delta_24h|cs_rank|zscore|winsor|tsrank|decay",
                "allowed_interactions": "price_return_state|volatility_state",
            },
            {
                "family_id": "G3_seed_pair_interaction",
                "required_seed_family": "price_return+volatility+basis_premium",
                "allowed_seed_fields": "|".join(seed_fields),
                "mechanism": "only pairwise seed interactions with clean primitive-response lineage",
                "allowed_transforms": "Mul|Sub|SafeDiv|Rank|ZScore|Clip|Winsor",
                "allowed_interactions": "price_x_vol|price_x_basis|basis_x_vol",
            },
        ]
    )
    transform_contract = pd.DataFrame(
        [
            {"operator": "Rank", "allowed": True, "constraint": "cross-sectional per timestamp only"},
            {"operator": "ZScore", "allowed": True, "constraint": "rolling or cross-sectional; no future fit"},
            {"operator": "TSRank", "allowed": True, "constraint": "lookback in 24|72|168 only"},
            {"operator": "Delta", "allowed": True, "constraint": "lookback in 1|4|24 only"},
            {"operator": "Mean", "allowed": True, "constraint": "lookback in 4|24|72|168 only"},
            {"operator": "Decay", "allowed": True, "constraint": "lookback in 4|12|24 only"},
            {"operator": "Sub", "allowed": True, "constraint": "seed fields only"},
            {"operator": "Mul", "allowed": True, "constraint": "max one interaction node"},
            {"operator": "SafeDiv", "allowed": True, "constraint": "bounded denominator; no raw price ratio overlay"},
            {"operator": "Clip", "allowed": True, "constraint": "fixed train-only or symmetric constants"},
            {"operator": "Winsor", "allowed": True, "constraint": "fixed train-only or symmetric constants"},
            {"operator": "SignedPower", "allowed": False, "constraint": "forbidden in A7AB-2"},
            {"operator": "deep_nested_conditionals", "allowed": False, "constraint": "forbidden in A7AB-2"},
        ]
    )
    forbidden = pd.DataFrame(
        [
            {"item": "full_open_grammar", "reason": "A7AB-2 is seed-constrained only"},
            {"item": "OI_or_positioning_reactivation", "reason": "A7AA response map did not classify OI/positioning as selector seed"},
            {"item": "A7V_activity_liquidity_self_reproduction", "reason": "previous family failed control/May attribution"},
            {"item": "liquidity_x_volatility_old_cluster", "reason": "previous cluster concentration failure"},
            {"item": "raw_OKX_Binance_direct_price_comparison", "reason": "canonical alias risk"},
            {"item": "stale_J5_overlay_aliases", "reason": "previous overlay alias risk"},
            {"item": "May_in_selector_generation_mutation", "reason": "May remains post-selection stress only"},
        ]
    )
    quota = {
        "generated_total_cap": 4096,
        "static_selected_cap": 512,
        "future_fast_replay_cap_if_later_authorized": 128,
        "future_deep_audit_cap_if_later_authorized": 16,
        "max_depth": 4,
        "max_interaction_nodes": 1,
        "max_per_family_share": 0.35,
        "max_per_seed_field_share": 0.25,
        "max_same_skeleton_share": 0.15,
        "min_family_count_static_queue": 3,
        "min_seed_field_count_static_queue": 5,
    }
    hard_gates = pd.DataFrame(
        [
            {"gate": "seed_lineage_required", "rule": "every expression must trace to an A7AB-1 selected seed"},
            {"gate": "primitive_response_role_required", "rule": "seed field must be predictive_signal_candidate in A7AA-2"},
            {"gate": "no_may", "rule": "May cannot enter generation, mutation, selector score, thresholds, or authorization"},
            {"gate": "negative_controls_attached", "rule": "wrong-lag/stale/shuffle/random controls must be generated with each family"},
            {"gate": "latency_native", "rule": "field-native latency only; no artificial +2h stress policy"},
            {"gate": "skeleton_diversity", "rule": "same skeleton share <= 15% in static queue"},
            {"gate": "field_family_diversity", "rule": "same family share <= 35% in static queue"},
        ]
    )

    decision = "PASS_A7AB2_SEED_CONSTRAINED_MICRO_GENERATION_CONTRACT_READY_FOR_A7AB3_DRY_GENERATION"
    manifest = {
        "stage": "A7AB-2",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_contract_only": True,
        "executes_formula_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may": False,
        "seed_field_count": int(len(seed_fields)),
        "seed_family_count": int(len(seed_families)),
        "seed_fields": seed_fields,
        "seed_families": seed_families,
        "quota": quota,
        "authorizes_a7ab3_seed_constrained_dry_generation": True,
        "authorizes_fast_replay": False,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    queue.to_csv(RUNTIME / "a7ab2_seed_queue_input.csv", index=False)
    allowed_families.to_csv(RUNTIME / "a7ab2_allowed_generation_families.csv", index=False)
    transform_contract.to_csv(RUNTIME / "a7ab2_transform_contract.csv", index=False)
    forbidden.to_csv(RUNTIME / "a7ab2_forbidden_families.csv", index=False)
    hard_gates.to_csv(RUNTIME / "a7ab2_hard_gates.csv", index=False)
    write_json(RUNTIME / "a7ab2_generation_quota.json", quota)
    write_json(RUNTIME / "a7ab2_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ab2_authorization_matrix.json",
        {
            "A7AB-2": {"status": decision},
            "A7AB-3_seed_constrained_dry_generation": {"authorized": True},
            "fast_replay": {"authorized": False},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AB-2 SEED-CONSTRAINED MICRO-GENERATION CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AB-2 is a contract only. It does not generate formulas, run replay, execute search, train a model, or authorize alpha proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Allowed Generation Families",
        "",
        md_table(allowed_families),
        "",
        "## Transform Contract",
        "",
        md_table(transform_contract),
        "",
        "## Hard Gates",
        "",
        md_table(hard_gates),
        "",
        "## Forbidden",
        "",
        md_table(forbidden),
        "",
        "## Seed Queue Input",
        "",
        md_table(
            queue[
                [
                    "selector_rank",
                    "field_name",
                    "field_family",
                    "transform",
                    "label_family",
                    "label_horizon_h",
                    "control_ratio_premay_max",
                    "blueprint",
                ]
            ],
            max_rows=20,
        ),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
