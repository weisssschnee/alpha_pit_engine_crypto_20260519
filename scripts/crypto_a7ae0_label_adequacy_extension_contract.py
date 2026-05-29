from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ae0_label_adequacy_extension_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AE0_LABEL_ADEQUACY_EXTENSION_CONTRACT_20260529.md"

A7AD1_MANIFEST = REPO / "runtime" / "a7ad1_ranked_label_translation_audit" / "a7ad1_manifest.json"
A7AA0_FIELDS = REPO / "runtime" / "a7aa0_label_feature_response_contract" / "a7aa0_candidate_primitive_fields.csv"
A7AA2_SEEDS = REPO / "runtime" / "a7aa2_feature_role_classification" / "a7aa2_selector_seed_fields.csv"


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

    a7ad1 = read_json(A7AD1_MANIFEST)
    if not a7ad1:
        raise SystemExit("A7AD-1 manifest is required before A7AE-0")

    labels = pd.DataFrame(
        [
            {
                "label_family": "L0_raw_forward_return",
                "definition": "log(close_t+h)-log(close_t)",
                "role": "baseline tradable raw return proxy",
                "enabled_in_a7ae1": True,
            },
            {
                "label_family": "L1_cross_sectional_relative_return",
                "definition": "raw forward return minus timestamp cross-sectional mean",
                "role": "market-mode reduced relative return",
                "enabled_in_a7ae1": True,
            },
            {
                "label_family": "L2_BTC_ETH_beta_residual_return",
                "definition": "train-fit per-symbol residual versus BTC and ETH forward-return factors",
                "role": "major-beta residual return",
                "enabled_in_a7ae1": True,
            },
            {
                "label_family": "L3_liquidity_tier_relative_return",
                "definition": "raw forward return demeaned within liquidity_tier at timestamp",
                "role": "liquidity-tier relative return",
                "enabled_in_a7ae1": True,
            },
            {
                "label_family": "L5_vol_adjusted_return",
                "definition": "raw forward return divided by contemporaneous realized_vol_168h",
                "role": "volatility-normalized return",
                "enabled_in_a7ae1": True,
            },
            {
                "label_family": "L6_downside_avoidance",
                "definition": "min(raw forward return, 0); higher spread means top bucket loses less in downside states",
                "role": "downside-avoidance diagnostic",
                "enabled_in_a7ae1": True,
            },
            {
                "label_family": "L7_ranked_future_return",
                "definition": "timestamp cross-sectional rank percentile of raw forward return minus 0.5",
                "role": "rank-label diagnostic only",
                "enabled_in_a7ae1": True,
            },
        ]
    )
    transforms = pd.DataFrame(
        [
            {"transform": "level", "description": "raw feature value", "enabled_in_a7ae1": True},
            {"transform": "delta_24h", "description": "feature_t - feature_t-24", "enabled_in_a7ae1": True},
            {"transform": "cs_rank", "description": "timestamp cross-sectional rank percentile", "enabled_in_a7ae1": True},
        ]
    )
    controls = pd.DataFrame(
        [
            {"control": "one_bar_lag", "purpose": "entry latency survival"},
            {"control": "wrong_lag_future_24h", "purpose": "lookahead contamination check"},
            {"control": "wrong_lag_stale_168h", "purpose": "stale signal placebo"},
            {"control": "same_family_random", "purpose": "random signal placebo"},
        ]
    )

    fields = pd.read_csv(A7AA0_FIELDS).head(24)
    seeds = pd.read_csv(A7AA2_SEEDS) if A7AA2_SEEDS.exists() else pd.DataFrame()
    if not seeds.empty:
        fields["a7aa2_seed_field"] = fields["field_name"].isin(seeds["field_name"].astype(str))
    else:
        fields["a7aa2_seed_field"] = False

    decision = "PASS_A7AE0_LABEL_ADEQUACY_EXTENSION_CONTRACT_READY_FOR_A7AE1"
    manifest = {
        "stage": "A7AE-0",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ad1_decision": a7ad1.get("decision"),
        "source_a7ad1_translated_candidates": a7ad1.get("translated_candidates"),
        "executes_contract_only": True,
        "executes_response_map": False,
        "executes_search": False,
        "executes_training": False,
        "authorizes_a7ae1_label_adequacy_response_map": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "feature_count": int(len(fields)),
        "label_family_count": int(labels["enabled_in_a7ae1"].sum()),
        "transform_count": int(transforms["enabled_in_a7ae1"].sum()),
        "uses_may": False,
    }

    fields.to_csv(RUNTIME / "a7ae0_field_universe.csv", index=False)
    labels.to_csv(RUNTIME / "a7ae0_label_family_contract.csv", index=False)
    transforms.to_csv(RUNTIME / "a7ae0_transform_contract.csv", index=False)
    controls.to_csv(RUNTIME / "a7ae0_negative_control_contract.csv", index=False)
    write_json(RUNTIME / "a7ae0_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ae0_authorization_matrix.json",
        {
            "A7AE-0": {"status": decision},
            "a7ae1_label_adequacy_response_map": {"authorized": True},
            "formula_search": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AE-0 LABEL ADEQUACY EXTENSION CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AE-0 extends A7AA/A7AD from rank-label diagnostics into a broader label adequacy audit. It does not generate formulas, search, train, or authorize proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label Families",
        "",
        md_table(labels),
        "",
        "## Primitive Field Universe",
        "",
        md_table(fields, 80),
        "",
        "## Transforms",
        "",
        md_table(transforms),
        "",
        "## Negative Controls",
        "",
        md_table(controls),
        "",
        "## Boundary",
        "",
        "```text",
        "A7AE-1 is diagnostic only.",
        "No formula search, large search, alpha proof, shadow, paper, or live authorization.",
        "May is not used.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
