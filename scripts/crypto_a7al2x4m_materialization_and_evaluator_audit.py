from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "a7al2x4m_materialization_and_evaluator_audit"
REPORT = ROOT / "reports" / "CRYPTO_A7AL2X4M_MATERIALIZATION_AND_EVALUATOR_AUDIT_20260529.md"

X3_LEDGER = ROOT / "runtime" / "a7al2x3_family_balanced_dry_generation" / "a7al2x3_generated_candidate_ledger.csv"
X4_MANIFEST = ROOT / "runtime" / "a7al2x4_replay_readiness_audit" / "a7al2x4_manifest.json"

BASE_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527")
UPPER_REGIME_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_upper_regime_state_v1_20260527.parquet")
LATENT_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_latent_state_features_v1_20260527.parquet")
TAXONOMY = Path(r"G:\AlphaFactory_CryptoData\gold\metadata\binance_universe498_contract_meme_taxonomy_v1_20260527.csv")

STATE_MASK_RE = re.compile(r"StateMask\(([^,]+),([^)]+)\)")


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def schema_names(path: Path) -> set[str]:
    if not path.exists():
        return set()
    if path.is_dir():
        return set(ds.dataset(str(path), format="parquet").schema.names)
    if path.suffix.lower() == ".parquet":
        return set(pq.ParquetFile(path).schema.names)
    if path.suffix.lower() == ".csv":
        return set(pd.read_csv(path, nrows=0).columns)
    return set()


def selected_rows() -> pd.DataFrame:
    ledger = pd.read_csv(X3_LEDGER)
    selected = ledger[
        ledger["selected_for_family_balanced_preflight"].astype(str).str.lower().isin(["true", "1"])
    ].copy()
    return selected


def split_pipe(value: Any) -> list[str]:
    if pd.isna(value):
        return []
    return [x for x in str(value).split("|") if x]


def actual_values(path: Path, column: str) -> list[str]:
    if not path.exists() or column not in schema_names(path):
        return []
    df = pd.read_parquet(path, columns=[column])
    return sorted(df[column].dropna().astype(str).unique().tolist())


def build_field_sources(selected: pd.DataFrame) -> pd.DataFrame:
    base_schema = schema_names(BASE_PANEL)
    upper_schema = schema_names(UPPER_REGIME_PANEL)
    latent_schema = schema_names(LATENT_PANEL)
    taxonomy_schema = schema_names(TAXONOMY)

    rows: list[dict[str, Any]] = []
    fields = sorted({field for value in selected["fields"].tolist() for field in split_pipe(value)})
    for field in fields:
        source = ""
        source_path = ""
        materialized_field = field
        join_key = ""
        status = "missing"
        caveat = ""
        if field in base_schema:
            source = "base_replay_panel_v2"
            source_path = str(BASE_PANEL)
            join_key = "symbol,timestamp"
            status = "resolved"
        elif field in upper_schema:
            source = "a7al0g_upper_regime_panel_v1"
            source_path = str(UPPER_REGIME_PANEL)
            join_key = "timestamp"
            status = "resolved"
            caveat = "upper regime was built from v1 panel; requires timestamp alignment audit before numeric replay"
        elif field in latent_schema:
            source = "a7ak_lv1_latent_state_panel_v1"
            source_path = str(LATENT_PANEL)
            join_key = "symbol,timestamp"
            status = "resolved"
            caveat = "latent panel was built from v1 panel; requires symbol/timestamp alignment audit before numeric replay"
        elif field in taxonomy_schema:
            source = "a7ak_static_contract_meme_taxonomy"
            source_path = str(TAXONOMY)
            join_key = "symbol"
            status = "resolved"
        elif field == "liquidity_tier" and "liquidity_tier_static" in latent_schema:
            source = "a7ak_lv1_latent_state_panel_v1"
            source_path = str(LATENT_PANEL)
            materialized_field = "liquidity_tier_static"
            join_key = "symbol,timestamp"
            status = "resolved_with_alias"
            caveat = "liquidity_tier maps to liquidity_tier_static in LV1 panel; static taxonomy also has exact liquidity_tier"

        rows.append(
            {
                "field_name": field,
                "status": status,
                "source": source,
                "source_path": source_path,
                "materialized_field": materialized_field,
                "join_key": join_key,
                "caveat": caveat,
            }
        )
    return pd.DataFrame(rows)


def build_state_domains() -> dict[str, list[str]]:
    domains: dict[str, list[str]] = {}
    upper_schema = schema_names(UPPER_REGIME_PANEL)
    latent_schema = schema_names(LATENT_PANEL)
    taxonomy_schema = schema_names(TAXONOMY)
    for col in sorted([c for c in upper_schema if c.startswith("R") and c.endswith("_state")]):
        domains[col] = actual_values(UPPER_REGIME_PANEL, col)
    for col in ["liquidity_tier_static", "liquidity_state", "raw_latent_state_id", "raw_latent_state_label"]:
        if col in latent_schema:
            vals = actual_values(LATENT_PANEL, col)
            domains[col] = vals[:200]
    for col in ["liquidity_tier", "meme_contract_group", "is_multiplier_contract", "is_major"]:
        if col in taxonomy_schema:
            vals = pd.read_csv(TAXONOMY, usecols=[col])[col].dropna().astype(str).unique().tolist()
            domains[col] = sorted(vals)
    return domains


def build_statemask_audit(selected: pd.DataFrame, field_sources: pd.DataFrame) -> pd.DataFrame:
    domains = build_state_domains()
    source_status = field_sources.set_index("field_name").to_dict("index")
    rows: list[dict[str, Any]] = []
    for row in selected.to_dict("records"):
        expression = str(row["expression"])
        for match in STATE_MASK_RE.finditer(expression):
            field = match.group(1).strip()
            requested_label = match.group(2).strip()
            materialized_field = source_status.get(field, {}).get("materialized_field", field)
            actual = domains.get(field) or domains.get(materialized_field) or []
            rows.append(
                {
                    "candidate_id": row["candidate_id"],
                    "objective_family": row["objective_family"],
                    "expression": expression,
                    "state_field": field,
                    "materialized_field": materialized_field,
                    "requested_label": requested_label,
                    "actual_values": "|".join(actual[:60]),
                    "label_valid": requested_label in set(actual),
                }
            )
    return pd.DataFrame(rows)


def build_operator_semantics(selected: pd.DataFrame, statemask_audit: pd.DataFrame) -> pd.DataFrame:
    ops = sorted({op for value in selected["operator_signature"].tolist() for op in split_pipe(value)})
    invalid_masks = 0 if statemask_audit.empty else int((~statemask_audit["label_valid"]).sum())
    rows: list[dict[str, Any]] = []
    for op in ops:
        status = "already_supported"
        semantics = "existing fast replay operator"
        blocker = False
        if op == "Clip":
            status = "local_extension_contract_ready"
            semantics = "fixed symmetric clipping after scalar transform; proposed default [-5,5], no May fit"
        elif op == "Winsor":
            status = "local_extension_contract_ready"
            semantics = "fixed symmetric winsorization after scalar transform; proposed default [-5,5], no May fit"
        elif op == "GroupNeutralize":
            status = "requires_state_aware_evaluator_extension"
            semantics = "demean or zscore within timestamp and materialized group field; needs min-group fallback policy"
        elif op == "StateMask":
            status = "blocked_until_state_label_repair" if invalid_masks else "requires_state_aware_evaluator_extension"
            semantics = "indicator for materialized state field equals requested label"
            blocker = invalid_masks > 0
        elif op == "LatentNeutralRank":
            status = "requires_state_aware_evaluator_extension"
            semantics = "rank signal within materialized latent group with min-group fallback"
        rows.append({"operator": op, "status": status, "semantics": semantics, "is_blocker": blocker})
    return pd.DataFrame(rows)


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def write_report(
    manifest: dict[str, Any],
    field_sources: pd.DataFrame,
    statemask_audit: pd.DataFrame,
    operator_semantics: pd.DataFrame,
    blockers: pd.DataFrame,
) -> None:
    lines = [
        "# CRYPTO A7AL-2X4M MATERIALIZATION AND EVALUATOR AUDIT",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "This audit does not execute numeric replay, search, training, or proof. It checks whether A7AL-2X3 selected candidates can be materialized and interpreted by a replay evaluator.",
        "",
        "## Summary",
        "",
        f"- selected candidates: {manifest['selected_candidates']}",
        f"- resolved selected fields: {manifest['resolved_fields']} / {manifest['selected_field_count']}",
        f"- invalid StateMask labels: {manifest['invalid_statemask_labels']}",
        f"- blocking operators: {manifest['blocking_operator_count']}",
        "",
        "## Field Materialization",
        "",
        md_table(field_sources),
        "",
        "## StateMask Label Audit",
        "",
        md_table(statemask_audit) if not statemask_audit.empty else "No selected StateMask expressions.",
        "",
        "## Operator Semantics",
        "",
        md_table(operator_semantics),
        "",
        "## Blockers",
        "",
        md_table(blockers) if not blockers.empty else "No blockers.",
        "",
        "## Authorization",
        "",
        "- numeric replay: not authorized",
        "- A7AL-2Y generation: not authorized",
        "- large search: not authorized",
        "- alpha proof / shadow / paper / live: not authorized",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    selected = selected_rows()
    field_sources = build_field_sources(selected)
    statemask_audit = build_statemask_audit(selected, field_sources)
    operator_semantics = build_operator_semantics(selected, statemask_audit)

    unresolved = field_sources.loc[~field_sources["status"].isin(["resolved", "resolved_with_alias"])].copy()
    invalid_masks = statemask_audit.loc[~statemask_audit["label_valid"]].copy() if not statemask_audit.empty else pd.DataFrame()
    blocking_ops = operator_semantics.loc[operator_semantics["is_blocker"]].copy()

    blocker_rows: list[dict[str, Any]] = []
    for row in unresolved.to_dict("records"):
        blocker_rows.append({"blocker": "missing_field_materialization", "detail": row["field_name"], "action": "resolve field source before replay"})
    for row in invalid_masks.to_dict("records"):
        blocker_rows.append(
            {
                "blocker": "invalid_statemask_label",
                "detail": f"{row['state_field']}={row['requested_label']} for {row['candidate_id']}",
                "action": "repair A7AL-2X3 generator to use materialized state labels, then regenerate X3/X4",
            }
        )
    for row in blocking_ops.to_dict("records"):
        blocker_rows.append({"blocker": "operator_blocked", "detail": row["operator"], "action": row["semantics"]})
    blockers = pd.DataFrame(blocker_rows)

    if not invalid_masks.empty:
        decision = "HOLD_A7AL2X4M_STATE_MASK_LABEL_MISMATCH_REQUIRES_GENERATOR_REPAIR"
    elif not unresolved.empty:
        decision = "HOLD_A7AL2X4M_FIELD_MATERIALIZATION_UNRESOLVED"
    elif not blocking_ops.empty:
        decision = "HOLD_A7AL2X4M_EVALUATOR_EXTENSION_REQUIRED"
    else:
        decision = "PASS_A7AL2X4M_READY_FOR_NUMERIC_REPLAY_PREFLIGHT_IMPLEMENTATION"

    manifest = {
        "stage": "A7AL-2X4M",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_numeric_replay": False,
        "authorizes_a7al2y_generation": False,
        "selected_candidates": int(len(selected)),
        "selected_field_count": int(len(field_sources)),
        "resolved_fields": int(field_sources["status"].isin(["resolved", "resolved_with_alias"]).sum()),
        "invalid_statemask_labels": int(len(invalid_masks)),
        "blocking_operator_count": int(len(blocking_ops)),
        "blockers": blockers["blocker"].drop_duplicates().tolist() if not blockers.empty else [],
    }

    field_sources.to_csv(RUNTIME / "a7al2x4m_field_materialization_sources.csv", index=False)
    statemask_audit.to_csv(RUNTIME / "a7al2x4m_statemask_label_audit.csv", index=False)
    operator_semantics.to_csv(RUNTIME / "a7al2x4m_operator_semantics.csv", index=False)
    blockers.to_csv(RUNTIME / "a7al2x4m_blocker_matrix.csv", index=False)
    with (RUNTIME / "a7al2x4m_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    auth = {
        "A7AL-2X4M": {"status": decision},
        "numeric_replay": {"authorized": False, "reason": "materialization/evaluator audit only"},
        "A7AL-2Y_generation": {"authorized": False},
        "large_search": {"authorized": False},
        "alpha_proof": {"authorized": False},
        "shadow_paper_live": {"authorized": False},
    }
    with (RUNTIME / "a7al2x4m_authorization_matrix.json").open("w", encoding="utf-8") as f:
        json.dump(auth, f, indent=2)

    write_report(manifest, field_sources, statemask_audit, operator_semantics, blockers)


if __name__ == "__main__":
    main()
