from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CONTRACT = REPO / "runtime" / "a7ffcore51px_company_sharded_replay_runner_contract"
DEFAULT_OUT = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore51px_company_sharded_replay_20260602")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_command(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(args, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def run_shard(shard: Path, compact: Path, out: Path, force: bool) -> dict[str, object]:
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "crypto_a7ffcore51px_company_shard_worker.py"),
        "--shard",
        str(shard),
        "--compact-frame",
        str(compact),
        "--out",
        str(out),
    ]
    if force:
        cmd.append("--force")
    code, stdout, stderr = run_command(cmd)
    manifest_path = out / f"{shard.stem}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    return {
        "shard_id": shard.stem,
        "return_code": code,
        "stdout_tail": stdout[-1000:],
        "stderr_tail": stderr[-1000:],
        "decision": manifest.get("decision", "MISSING_MANIFEST"),
        "metric_rows": manifest.get("metric_rows", 0),
        "eval_failure_count": manifest.get("eval_failure_count", None),
        "control_clean_positive_rows": manifest.get("control_clean_positive_rows", 0),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--contract", default=str(CONTRACT))
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    contract = Path(args.contract)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    compact = out / "a7ffcore51px_compact_frame.parquet"
    if args.force or not compact.exists():
        compact_cmd = [
            sys.executable,
            str(REPO / "scripts" / "crypto_a7ffcore51px_company_compact_frame_builder.py"),
            "--out",
            str(compact),
            "--contract",
            str(contract),
        ]
        code, stdout, stderr = run_command(compact_cmd)
        if code != 0:
            raise SystemExit(f"compact frame build failed: {stderr[-2000:]}")

    shards = sorted((contract / "candidate_shards").glob("*.csv"))
    rows = []
    with ThreadPoolExecutor(max_workers=max(1, int(args.jobs))) as executor:
        futures = [executor.submit(run_shard, shard, compact, out, args.force) for shard in shards]
        for future in as_completed(futures):
            rows.append(future.result())
    summary = pd.DataFrame(rows).sort_values("shard_id")
    summary_path = out / "a7ffcore51pxe_shard_execution_summary.csv"
    summary.to_csv(summary_path, index=False)
    pass_count = int(summary["decision"].astype(str).str.startswith("PASS_").sum()) if not summary.empty else 0
    manifest = {
        "stage": "A7FF-CORE51PXE",
        "generated_at": now_utc(),
        "contract_runtime": str(contract).replace("\\", "/"),
        "output_dir": str(out).replace("\\", "/"),
        "compact_frame": str(compact).replace("\\", "/"),
        "jobs": int(args.jobs),
        "shard_count": int(len(shards)),
        "completed_shard_count": pass_count,
        "metric_rows": int(pd.to_numeric(summary.get("metric_rows", pd.Series(dtype=int)), errors="coerce").fillna(0).sum()),
        "eval_failure_count": int(pd.to_numeric(summary.get("eval_failure_count", pd.Series(dtype=int)), errors="coerce").fillna(0).sum()),
        "control_clean_positive_rows": int(pd.to_numeric(summary.get("control_clean_positive_rows", pd.Series(dtype=int)), errors="coerce").fillna(0).sum()),
        "decision": "PASS_A7FFCORE51PXE_COMPANY_SHARDED_REPLAY_COMPLETE" if pass_count == len(shards) and len(shards) > 0 else "HOLD_A7FFCORE51PXE_COMPANY_SHARDED_REPLAY_INCOMPLETE",
        "executes_replay": True,
        "executes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    (out / "a7ffcore51pxe_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
