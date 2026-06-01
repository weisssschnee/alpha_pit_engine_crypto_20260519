from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore44e_orthogonal_score_packet_construction"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE44E_ORTHOGONAL_SCORE_PACKET_CONSTRUCTION_20260602.md"
CORE44 = REPO / "runtime" / "a7ffcore44_orthogonal_score_packet_contract" / "a7ffcore44_manifest.json"
ARTIFACT_ROOT = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore44e_orthogonal_score_packet_20260602")


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


def build_book_packet(vectors: pd.DataFrame) -> pd.DataFrame:
    work = vectors.copy()
    work["selected_score_variant"] = "residual_score_null_orthogonal"
    work["book_score"] = pd.to_numeric(work["residual_score_null_orthogonal"], errors="coerce").astype("float32")
    group_key = [work["candidate_id"], work["timestamp"]]
    work["book_rank"] = work["book_score"].groupby(group_key).rank(pct=True, method="average").astype("float32")
    selected_parts: list[pd.DataFrame] = []
    for _, group in work.dropna(subset=["book_score"]).groupby(["candidate_id", "timestamp"], sort=False):
        n = int(group.shape[0])
        if n < 2:
            continue
        k = max(1, int(np.floor(n * 0.10)))
        k = min(k, n // 2)
        bottom = group.nsmallest(k, "book_score").copy()
        bottom["book_side"] = "short"
        top = group.nlargest(k, "book_score").copy()
        top["book_side"] = "long"
        selected_parts.append(pd.concat([top, bottom], ignore_index=False))
    selected = pd.concat(selected_parts, ignore_index=False).copy() if selected_parts else pd.DataFrame(columns=[*work.columns, "book_side"])
    selected["raw_side"] = np.where(selected["book_side"].eq("long"), 1.0, -1.0)
    side_count = selected.groupby(["candidate_id", "timestamp", "book_side"])["symbol"].transform("count").replace(0, np.nan)
    selected["book_weight"] = (selected["raw_side"] / side_count).clip(-0.025, 0.025).astype("float32")
    selected["control_margin_metadata"] = (
        "orig_rank="
        + selected["candidate_score_original_rank"].round(6).astype(str)
        + ";stale_resid_rank="
        + selected["residual_score_stale_orthogonal_rank"].round(6).astype(str)
        + ";null_resid_rank="
        + selected["residual_score_null_orthogonal_rank"].round(6).astype(str)
    )
    keep = [
        "candidate_id",
        "dataset",
        "family_id",
        "cluster_key",
        "timestamp",
        "symbol",
        "split",
        "quote_volume",
        "candidate_score_original",
        "candidate_score_stale",
        "candidate_score_sign_flip",
        "candidate_score_shuffle_time",
        "candidate_score_shuffle_symbol",
        "residual_score_stale_orthogonal",
        "residual_score_null_orthogonal",
        "selected_score_variant",
        "book_score",
        "book_rank",
        "book_side",
        "book_weight",
        "control_margin_metadata",
    ]
    return selected[keep].reset_index(drop=True)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE44)
    if source.get("decision") != "PASS_A7FFCORE44_ORTHOGONAL_SCORE_PACKET_CONTRACT_READY_FOR_CORE44E":
        raise SystemExit(f"CORE44 not ready for CORE44E: {source.get('decision')}")
    vector_path = Path(str(source.get("source_external_sample_path", "")))
    if not vector_path.exists():
        raise SystemExit(f"CORE43E external vector sample missing: {vector_path}")

    vectors = pd.read_parquet(vector_path)
    packet = build_book_packet(vectors)
    packet_path = ARTIFACT_ROOT / "a7ffcore44e_orthogonal_book_input_packet.parquet"
    packet.to_parquet(packet_path, index=False)

    dataset_summary = (
        vectors.groupby("dataset", dropna=False)
        .agg(
            vector_rows=("candidate_id", "size"),
            candidate_count=("candidate_id", "nunique"),
            symbol_count=("symbol", "nunique"),
            timestamp_count=("timestamp", "nunique"),
        )
        .reset_index()
    )
    candidate_quality = (
        packet.groupby(["candidate_id", "dataset", "family_id"], dropna=False)
        .agg(
            packet_rows=("candidate_id", "size"),
            timestamp_count=("timestamp", "nunique"),
            symbol_count=("symbol", "nunique"),
            long_rows=("book_side", lambda s: int((s == "long").sum())),
            short_rows=("book_side", lambda s: int((s == "short").sum())),
            mean_abs_weight=("book_weight", lambda s: float(s.abs().mean())),
            max_abs_weight=("book_weight", lambda s: float(s.abs().max())),
        )
        .reset_index()
    )
    required_cols = [
        "candidate_id",
        "dataset",
        "family_id",
        "cluster_key",
        "timestamp",
        "symbol",
        "split",
        "quote_volume",
        "candidate_score_original",
        "candidate_score_stale",
        "candidate_score_sign_flip",
        "candidate_score_shuffle_time",
        "candidate_score_shuffle_symbol",
        "residual_score_stale_orthogonal",
        "residual_score_null_orthogonal",
        "selected_score_variant",
        "book_rank",
        "book_side",
        "book_weight",
        "control_margin_metadata",
    ]
    quality_gate = pd.DataFrame(
        [
            {"metric": "packet_rows", "value": int(packet.shape[0]), "pass": bool(packet.shape[0] > 0)},
            {
                "metric": "candidate_count",
                "value": int(packet["candidate_id"].nunique()) if not packet.empty else 0,
                "pass": bool(not packet.empty and packet["candidate_id"].nunique() == vectors["candidate_id"].nunique()),
            },
            {
                "metric": "required_packet_columns_present",
                "value": int(sum(col in packet.columns for col in required_cols)),
                "pass": bool(all(col in packet.columns for col in required_cols)),
            },
            {
                "metric": "missing_book_score_rate",
                "value": float(packet["book_score"].isna().mean()) if not packet.empty else 1.0,
                "pass": bool(not packet.empty and packet["book_score"].isna().mean() == 0.0),
            },
            {
                "metric": "max_abs_book_weight",
                "value": float(packet["book_weight"].abs().max()) if not packet.empty else np.nan,
                "pass": bool(not packet.empty and packet["book_weight"].abs().max() <= 0.0250001),
            },
            {
                "metric": "long_short_presence_all_candidates",
                "value": int(
                    candidate_quality[
                        candidate_quality["long_rows"].gt(0) & candidate_quality["short_rows"].gt(0)
                    ].shape[0]
                )
                if not candidate_quality.empty
                else 0,
                "pass": bool(
                    not candidate_quality.empty
                    and (
                        candidate_quality["long_rows"].gt(0) & candidate_quality["short_rows"].gt(0)
                    ).all()
                ),
            },
        ]
    )
    decision = (
        "PASS_A7FFCORE44E_ORTHOGONAL_SCORE_PACKET_READY_FOR_CORE45_CONTRACT"
        if bool(quality_gate["pass"].all())
        else "HOLD_A7FFCORE44E_ORTHOGONAL_SCORE_PACKET_INCOMPLETE"
    )
    artifact_manifest = pd.DataFrame(
        [
            {
                "artifact": "orthogonal_book_input_packet",
                "path": str(packet_path).replace("\\", "/"),
                "committed_to_git": False,
                "rows": int(packet.shape[0]),
                "columns": int(packet.shape[1]),
                "bytes": int(packet_path.stat().st_size) if packet_path.exists() else 0,
            }
        ]
    )
    authorization = {
        "authorized": {
            "A7FF-CORE45 bounded orthogonal book replay contract": decision.startswith("PASS")
        },
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "new_generation": True,
            "book_replay_execution": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
        },
    }
    manifest = {
        "stage": "A7FF-CORE44E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE44",
        "source_decision": source.get("decision"),
        "decision": decision,
        "source_vector_rows": int(vectors.shape[0]),
        "packet_rows": int(packet.shape[0]),
        "candidate_count": int(packet["candidate_id"].nunique()) if not packet.empty else 0,
        "external_packet_path": str(packet_path).replace("\\", "/"),
        "executes_new_generation": False,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_core45_contract": decision.startswith("PASS"),
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE45 bounded orthogonal book replay contract"
        if decision.startswith("PASS")
        else "A7FF-CORE44E repair / rerun only",
    }
    dataset_summary.to_csv(RUNTIME / "a7ffcore44e_dataset_summary.csv", index=False)
    candidate_quality.to_csv(RUNTIME / "a7ffcore44e_candidate_packet_quality.csv", index=False)
    quality_gate.to_csv(RUNTIME / "a7ffcore44e_packet_quality_gate.csv", index=False)
    artifact_manifest.to_csv(RUNTIME / "a7ffcore44e_packet_artifact_manifest.csv", index=False)
    write_json(RUNTIME / "a7ffcore44e_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore44e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE44E ORTHOGONAL SCORE PACKET CONSTRUCTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE44E constructs a bounded orthogonal book-input packet from CORE43E full-universe residual score vectors. It does not run book replay, generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Dataset Summary",
        "",
        md_table(dataset_summary),
        "",
        "## Packet Quality Gate",
        "",
        md_table(quality_gate),
        "",
        "## Candidate Packet Quality",
        "",
        md_table(candidate_quality),
        "",
        "## External Artifact",
        "",
        md_table(artifact_manifest),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
