from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore51px_company_sharded_replay_runner_contract"
SHARDS = RUNTIME / "candidate_shards"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE51PX_COMPANY_SHARDED_REPLAY_RUNNER_CONTRACT_20260602.md"
CORE51PR = REPO / "runtime" / "a7ffcore51pr_local_runner_blocker_forensic" / "a7ffcore51pr_manifest.json"
FILTERED = REPO / "runtime" / "a7ffcore50_null_vector_preflight_arbitration" / "a7ffcore50_filtered_seed_preview.csv"
BASE_PANEL = Path("G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v2_20260527")
LATENT_PANEL = Path("G:/AlphaFactory_CryptoData/gold/features/binance_universe498_latent_state_features_v1_20260527.parquet")

OPS = {
    "Mean",
    "Delta",
    "TSRank",
    "Decay",
    "Rank",
    "CSRank",
    "ZScore",
    "Mul",
    "Sub",
    "SafeDiv",
    "Add",
    "Neg",
    "Abs",
    "Sign",
    "Clip",
}
MAX_CANDIDATES = 384
SHARD_SIZE = 24


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def extract_fields(expressions: pd.Series) -> list[str]:
    tokens: set[str] = set()
    for expression in expressions.astype(str):
        tokens.update(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", expression))
    return sorted(token for token in tokens if token not in OPS)


def select_balanced(filtered: pd.DataFrame, max_count: int) -> pd.DataFrame:
    data = filtered.copy()
    data["active_ratio_num"] = pd.to_numeric(data["active_ratio"], errors="coerce").fillna(0.0)
    data["group_key"] = (
        data["semantic_pair"].astype(str)
        + "|"
        + data["operator"].astype(str)
        + "|"
        + data.get("stale_risk_tier", pd.Series("unknown", index=data.index)).astype(str)
    )
    groups = [g.sort_values("active_ratio_num", ascending=False).reset_index(drop=True) for _, g in data.groupby("group_key", sort=True)]
    selected: list[pd.Series] = []
    seen: set[str] = set()
    positions = [0 for _ in groups]
    progressed = True
    while progressed and len(selected) < max_count:
        progressed = False
        for index, group in enumerate(groups):
            while positions[index] < len(group):
                row = group.iloc[positions[index]]
                positions[index] += 1
                seed_id = str(row["seed_id"])
                if seed_id in seen:
                    continue
                selected.append(row)
                seen.add(seed_id)
                progressed = True
                break
            if len(selected) >= max_count:
                break
    return pd.DataFrame(selected).drop(columns=["group_key"], errors="ignore").reset_index(drop=True)


def panel_columns() -> tuple[set[str], set[str]]:
    part_files = sorted(BASE_PANEL.glob("symbol=*/part.parquet"))
    base_cols = set(pd.read_parquet(part_files[0]).columns) if part_files else set()
    latent_cols = set(pq.ParquetFile(LATENT_PANEL).schema_arrow.names) if LATENT_PANEL.exists() else set()
    return base_cols, latent_cols


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    SHARDS.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE51PR)
    if source.get("decision") != "HOLD_A7FFCORE51PR_LOCAL_REPLAY_RUNNER_INSUFFICIENT_USE_COMPANY_SHARDS":
        raise SystemExit(f"CORE51PR not ready for CORE51PX: {source.get('decision')}")

    filtered = pd.read_csv(FILTERED)
    selected = select_balanced(filtered, MAX_CANDIDATES)
    fields = sorted(set(extract_fields(selected["expression"]) + ["symbol", "timestamp", "trade_close", "split"]))
    base_cols, latent_cols = panel_columns()
    field_rows = []
    for field in fields:
        if field in {"symbol", "timestamp"}:
            source_panel = "key"
            status = "present"
        elif field in base_cols:
            source_panel = "base_universe498_v2"
            status = "present"
        elif field in latent_cols:
            source_panel = "latent_state_v1"
            status = "present"
        else:
            source_panel = "missing"
            status = "missing"
        field_rows.append({"field_name": field, "source_panel": source_panel, "status": status})
    compact_frame_contract = pd.DataFrame(field_rows)

    shard_rows = []
    for shard_index, start in enumerate(range(0, len(selected), SHARD_SIZE)):
        shard = selected.iloc[start : start + SHARD_SIZE].copy()
        shard_id = f"core51px_shard_{shard_index:02d}"
        shard_path = SHARDS / f"{shard_id}.csv"
        shard.to_csv(shard_path, index=False)
        shard_rows.append(
            {
                "shard_id": shard_id,
                "candidate_count": int(shard.shape[0]),
                "candidate_start": int(start),
                "candidate_end_exclusive": int(start + shard.shape[0]),
                "relative_path": str(shard_path.relative_to(REPO)).replace("\\", "/"),
                "max_runtime_minutes": 90,
                "resume_safe": True,
            }
        )
    shard_plan = pd.DataFrame(shard_rows)

    input_sources = pd.DataFrame(
        [
            {
                "input_id": "I0_selected_candidate_queue",
                "path": "runtime/a7ffcore51px_company_sharded_replay_runner_contract/a7ffcore51px_selected_candidate_queue.csv",
                "role": "balanced 384-candidate replay queue",
                "required": True,
            },
            {
                "input_id": "I1_candidate_shards",
                "path": "runtime/a7ffcore51px_company_sharded_replay_runner_contract/candidate_shards/",
                "role": "16 x 24-candidate shard CSVs",
                "required": True,
            },
            {
                "input_id": "I2_compact_frame_contract",
                "path": "runtime/a7ffcore51px_company_sharded_replay_runner_contract/a7ffcore51px_compact_frame_contract.csv",
                "role": "required columns and source panel routing",
                "required": True,
            },
            {
                "input_id": "I3_base_panel",
                "path": str(BASE_PANEL).replace("\\", "/"),
                "role": "base universe498 replay panel",
                "required": True,
            },
            {
                "input_id": "I4_latent_panel",
                "path": str(LATENT_PANEL).replace("\\", "/"),
                "role": "latent/listing/liquidity overlay",
                "required": True,
            },
        ]
    )
    output_schema = pd.DataFrame(
        [
            {"field": "shard_id", "required": True},
            {"field": "seed_id", "required": True},
            {"field": "label_family", "required": True},
            {"field": "horizon", "required": True},
            {"field": "original_spread_mean", "required": True},
            {"field": "original_tstat", "required": True},
            {"field": "control_ratio", "required": True},
            {"field": "stale_spread_mean", "required": True},
            {"field": "time_shuffle_spread_mean", "required": True},
            {"field": "symbol_shuffle_spread_mean", "required": True},
            {"field": "sign_flip_spread_mean", "required": True},
            {"field": "decision", "required": True},
        ]
    )
    deployment_policy = pd.DataFrame(
        [
            {"policy_id": "P0_no_local_retry", "policy": "do not rerun local pandas replay runner"},
            {"policy_id": "P1_company_shards", "policy": "run candidate shards independently on company machine"},
            {"policy_id": "P2_compact_frame", "policy": "build compact frame with only required columns before shard replay"},
            {"policy_id": "P3_incremental_outputs", "policy": "write one metrics CSV and one manifest JSON per shard"},
            {"policy_id": "P4_resume_safe", "policy": "skip completed shards with PASS manifest unless force flag is set"},
            {"policy_id": "P5_no_search", "policy": "no formula generation/search/proof/promotion/shadow/paper/live"},
        ]
    )
    commands = [
        "$repo = 'G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519'",
        "$out = 'G:/AlphaFactory_CryptoData/research_runtime/a7ffcore51px_company_sharded_replay_20260602'",
        "New-Item -ItemType Directory -Force -Path $out | Out-Null",
        "py (Join-Path $repo 'scripts/crypto_a7ffcore51pxe_company_sharded_replay_orchestrator.py') --out $out --jobs 8",
    ]
    command_text = "\n".join(commands) + "\n"
    (RUNTIME / "a7ffcore51px_company_execution_commands.ps1").write_text(command_text, encoding="utf-8")

    selected.to_csv(RUNTIME / "a7ffcore51px_selected_candidate_queue.csv", index=False)
    shard_plan.to_csv(RUNTIME / "a7ffcore51px_candidate_shard_plan.csv", index=False)
    compact_frame_contract.to_csv(RUNTIME / "a7ffcore51px_compact_frame_contract.csv", index=False)
    input_sources.to_csv(RUNTIME / "a7ffcore51px_input_sources.csv", index=False)
    output_schema.to_csv(RUNTIME / "a7ffcore51px_worker_output_schema.csv", index=False)
    deployment_policy.to_csv(RUNTIME / "a7ffcore51px_deployment_policy.csv", index=False)

    missing_count = int(compact_frame_contract["status"].eq("missing").sum())
    decision = (
        "PASS_A7FFCORE51PX_COMPANY_SHARDED_REPLAY_CONTRACT_READY_FOR_COMPANY_EXECUTION"
        if selected.shape[0] == MAX_CANDIDATES and shard_plan.shape[0] == 16 and missing_count == 0
        else "HOLD_A7FFCORE51PX_COMPANY_SHARDED_REPLAY_CONTRACT_INCOMPLETE"
    )
    authorization = {
        "authorized": {
            "A7FF-CORE51PXE company-machine sharded replay execution": decision.startswith("PASS_")
        },
        "not_authorized": {
            "local_runner_retry": True,
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    manifest = {
        "stage": "A7FF-CORE51PX",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE51PR",
        "source_decision": source.get("decision"),
        "decision": decision,
        "selected_candidate_count": int(selected.shape[0]),
        "candidate_shard_count": int(shard_plan.shape[0]),
        "shard_size": SHARD_SIZE,
        "semantic_pair_count": int(selected["semantic_pair"].nunique()),
        "operator_count": int(selected["operator"].nunique()),
        "required_field_count": int(compact_frame_contract.shape[0]),
        "missing_field_count": missing_count,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_company_sharded_replay_execution": decision.startswith("PASS_"),
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE51PXE company-machine sharded replay execution" if decision.startswith("PASS_") else "A7FF-CORE51PX repair",
    }
    write_json(RUNTIME / "a7ffcore51px_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore51px_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE51PX COMPANY-MACHINE SHARDED REPLAY RUNNER CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE51PX packages the filtered replay queue for company-machine sharded execution. It does not execute replay locally and does not authorize formula search, large search, proof, promotion, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Input Sources",
        "",
        md_table(input_sources),
        "",
        "## Candidate Shard Plan",
        "",
        md_table(shard_plan, 80),
        "",
        "## Compact Frame Contract",
        "",
        md_table(compact_frame_contract, 80),
        "",
        "## Deployment Policy",
        "",
        md_table(deployment_policy),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
