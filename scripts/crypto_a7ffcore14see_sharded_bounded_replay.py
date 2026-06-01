from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import crypto_a7ffcore14e_bounded_replay_execution as core14e  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ffcore14see_sharded_bounded_replay"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE14SEE_SHARDED_BOUNDED_REPLAY_20260601.md"
CORE14SE = REPO / "runtime" / "a7ffcore14se_repaired_packet_construction" / "a7ffcore14se_manifest.json"
PACKET = REPO / "runtime" / "a7ffcore14se_repaired_packet_construction" / "a7ffcore14se_repaired_replay_packet.csv"


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


def normalize_packet(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "core14_rank" not in out.columns and "core14se_rank" in out.columns:
        out = out.rename(columns={"core14se_rank": "core14_rank"})
    return out


def run_shard(shard_id: int, shard_count: int) -> dict[str, Any]:
    source = read_json(CORE14SE)
    if source.get("decision") != "PASS_A7FFCORE14SE_REPAIRED_PACKET_READY_FOR_BOUNDED_REPLAY":
        raise SystemExit(f"A7FF-CORE14SE is not ready: {source.get('decision')}")
    if shard_id < 0 or shard_id >= shard_count:
        raise SystemExit(f"invalid shard_id={shard_id} shard_count={shard_count}")

    full = normalize_packet(pd.read_csv(PACKET))
    shard = full.iloc[shard_id::shard_count].copy().reset_index(drop=True)
    shard_dir = RUNTIME / f"shard_{shard_id:02d}_of_{shard_count:02d}"
    shard_dir.mkdir(parents=True, exist_ok=True)
    shard_packet = shard_dir / "a7ffcore14see_shard_packet.csv"
    shard_source = shard_dir / "a7ffcore14see_source_shim.json"
    shard_report = shard_dir / "a7ffcore14see_shard_report.md"
    shard.to_csv(shard_packet, index=False)
    write_json(
        shard_source,
        {
            "decision": "PASS_A7FFCORE14_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE14E",
            "source_stage": "A7FF-CORE14SE",
            "source_decision": source.get("decision"),
            "shard_id": shard_id,
            "shard_count": shard_count,
        },
    )

    core14e.RUNTIME = shard_dir
    core14e.REPORT = shard_report
    core14e.A7FFCORE14 = shard_source
    core14e.PACKET = shard_packet
    core14e.main()
    raw_manifest = read_json(shard_dir / "a7ffcore14e_manifest.json")
    manifest = dict(raw_manifest)
    raw_decision = str(raw_manifest.get("decision", ""))
    manifest.update(
        {
            "stage": "A7FF-CORE14SEE-SHARD",
            "shard_id": shard_id,
            "shard_count": shard_count,
            "source_stage": "A7FF-CORE14SE",
            "source_decision": source.get("decision"),
            "raw_core14e_decision": raw_decision,
            "decision": (
                "PASS_A7FFCORE14SEE_SHARD_REPLAY_COMPLETE"
                if raw_decision.startswith("PASS_") or raw_decision.startswith("HOLD_")
                else "HOLD_A7FFCORE14SEE_SHARD_REPLAY_FAILED"
            ),
            "executes_replay": True,
            "executes_search": False,
            "authorizes_search": False,
            "authorizes_alpha_proof": False,
            "authorizes_shadow_paper_live": False,
        }
    )
    write_json(shard_dir / "a7ffcore14see_shard_manifest.json", manifest)
    return manifest


def summarize(shard_count: int) -> dict[str, Any]:
    manifests = []
    candidate_frames = []
    family_frames = []
    row_frames = []
    for shard_id in range(shard_count):
        shard_dir = RUNTIME / f"shard_{shard_id:02d}_of_{shard_count:02d}"
        manifest = read_json(shard_dir / "a7ffcore14see_shard_manifest.json")
        if manifest:
            manifests.append(manifest)
        for name, target in [
            ("a7ffcore14e_candidate_summary.csv", candidate_frames),
            ("a7ffcore14e_family_summary.csv", family_frames),
            ("a7ffcore14e_replay_rows.csv", row_frames),
        ]:
            path = shard_dir / name
            if path.exists():
                df = pd.read_csv(path)
                df["shard_id"] = shard_id
                target.append(df)
    candidates = pd.concat(candidate_frames, ignore_index=True) if candidate_frames else pd.DataFrame()
    families = pd.concat(family_frames, ignore_index=True) if family_frames else pd.DataFrame()
    rows = pd.concat(row_frames, ignore_index=True) if row_frames else pd.DataFrame()
    completed = len({int(m["shard_id"]) for m in manifests if m.get("decision") == "PASS_A7FFCORE14SEE_SHARD_REPLAY_COMPLETE"})
    clean_candidates = candidates[candidates.get("replay_clean", pd.Series(dtype=bool)).astype(str).str.lower().eq("true")].copy() if not candidates.empty else pd.DataFrame()
    clean_count = int(clean_candidates["candidate_id"].nunique()) if not clean_candidates.empty else 0
    clean_semantic = int(clean_candidates["semantic_bucket"].nunique()) if not clean_candidates.empty else 0
    clean_motif = int(clean_candidates["motif_bucket"].nunique()) if not clean_candidates.empty else 0
    eval_errors = int(sum(int(m.get("eval_error_count", 0)) for m in manifests))
    if not candidates.empty:
        candidates.to_csv(RUNTIME / "a7ffcore14see_candidate_summary.csv", index=False)
    if not families.empty:
        families.to_csv(RUNTIME / "a7ffcore14see_family_summary_by_shard.csv", index=False)
    if not rows.empty:
        rows.to_csv(RUNTIME / "a7ffcore14see_replay_rows.csv", index=False)
    if not clean_candidates.empty:
        clean_candidates.to_csv(RUNTIME / "a7ffcore14see_replay_clean_candidates.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE14SEE",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE14SE",
        "source_decision": read_json(CORE14SE).get("decision"),
        "decision": (
            "PASS_A7FFCORE14SEE_REPAIRED_BOUNDED_REPLAY_READY_FOR_CORE15"
            if completed == shard_count and clean_count >= 24 and clean_semantic >= 4 and clean_motif >= 4 and eval_errors == 0
            else "HOLD_A7FFCORE14SEE_REPAIRED_BOUNDED_REPLAY_INSUFFICIENT_OR_INCOMPLETE"
        ),
        "shard_count": shard_count,
        "completed_shard_count": completed,
        "candidate_count": int(candidates["candidate_id"].nunique()) if not candidates.empty else 0,
        "eval_error_count": eval_errors,
        "replay_row_count": int(rows.shape[0]) if not rows.empty else 0,
        "replay_clean_candidate_count": clean_count,
        "replay_clean_semantic_bucket_count": clean_semantic,
        "replay_clean_motif_bucket_count": clean_motif,
        "executes_replay": True,
        "executes_search": False,
        "authorizes_core15_contract": completed == shard_count and clean_count >= 24 and clean_semantic >= 4 and clean_motif >= 4 and eval_errors == 0,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": (
            "A7FF-CORE15 replay-clean consolidation / search-readiness audit"
            if completed == shard_count and clean_count >= 24 and clean_semantic >= 4 and clean_motif >= 4 and eval_errors == 0
            else "continue A7FF-CORE14SEE shards or run CORE14SER forensic after full shard completion"
        ),
    }
    write_json(RUNTIME / "a7ffcore14see_manifest.json", manifest)
    pd.DataFrame(manifests).to_csv(RUNTIME / "a7ffcore14see_shard_manifest_summary.csv", index=False)
    report = [
        "# CRYPTO A7FF-CORE14SEE SHARDED BOUNDED REPLAY",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "A7FF-CORE14SEE executes repaired packet bounded replay as resumable shards. It does not execute formula search, large search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Clean Candidates",
        "",
        md_table(clean_candidates, max_rows=80),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-id", type=int, default=None)
    parser.add_argument("--shard-count", type=int, default=16)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    RUNTIME.mkdir(parents=True, exist_ok=True)
    if args.summary:
        print(json.dumps(summarize(args.shard_count), indent=2, sort_keys=True))
    elif args.shard_id is not None:
        print(json.dumps(run_shard(args.shard_id, args.shard_count), indent=2, sort_keys=True))
    else:
        raise SystemExit("pass --shard-id N or --summary")


if __name__ == "__main__":
    main()
