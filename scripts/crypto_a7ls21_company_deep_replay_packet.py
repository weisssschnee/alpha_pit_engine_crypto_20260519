from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
A7LS20 = REPO / "runtime" / "a7ls20_checkpoint_deep_audit"
RUNTIME = REPO / "runtime" / "a7ls21_company_deep_replay_packet"
REPORT = REPO / "reports" / "CRYPTO_A7LS21_COMPANY_DEEP_REPLAY_PACKET_20260607.md"

QUEUE_IN = A7LS20 / "a7ls20_marginal_candidate_queue.csv"
MANIFEST_IN = A7LS20 / "a7ls20_manifest.json"

REMOTE_REPO = r"D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
REMOTE_RUN_ROOT = r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls21_company_deep_replay_20260607"
REMOTE_PYTHON = r"D:\HermesWorker\workspace\.venv\Scripts\python.exe"

ROWS_PER_SHARD = 12
HOURS_PER_SPLIT = 2160


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
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```csv\n" + view.to_csv(index=False) + "```"


def build_runner(shards: list[str]) -> str:
    shard_array = "@(" + ",".join(f'"{s}"' for s in shards) + ")"
    return rf'''$ErrorActionPreference = "Stop"
$Python = "{REMOTE_PYTHON}"
$RepoRoot = "{REMOTE_REPO}"
$RunRoot = "{REMOTE_RUN_ROOT}"
$Shards = {shard_array}

New-Item -ItemType Directory -Force -Path $RunRoot | Out-Null
Set-Location $RepoRoot
$env:PYTHONPATH = $RepoRoot
$env:NUMEXPR_MAX_THREADS = "4"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"

$summary = @()
foreach ($Shard in $Shards) {{
  $ShardRoot = Join-Path $RunRoot ("shards\" + $Shard)
  $Manifest = Join-Path $ShardRoot ("a7ls21_" + $Shard + "_manifest.json")
  if (Test-Path $Manifest) {{
    try {{
      $existing = Get-Content -Raw $Manifest | ConvertFrom-Json
      if ($existing.decision -like "PASS_*") {{
        Write-Output "[A7LS21] skip existing PASS shard $Shard"
        $summary += [pscustomobject]@{{ shard=$Shard; status="skip_existing_pass"; decision=$existing.decision }}
        continue
      }}
    }} catch {{}}
  }}

  Write-Output "[A7LS21] running shard $Shard"
  $env:A7FF8_STAGE = "A7LS-21-$Shard"
  $env:A7FF8_FILE_PREFIX = "a7ls21_$Shard"
  $env:A7FF8_RUNTIME = $ShardRoot
  $env:A7FF8_REPORT = (Join-Path $ShardRoot ("A7LS21_" + $Shard + "_REPORT.md"))
  $env:A7FF8_QUEUE_PATH = (Join-Path $ShardRoot "queue.csv")
  $env:A7FF8_AUTH_MANIFEST = (Join-Path $RunRoot "a7ls21_auth_manifest.json")
  $env:A7FF8_AUTH_DECISION = "PASS_A7LS20_MARGINAL_QUEUE_READY_FOR_A7LS21_DEEP_REPLAY_PACKET"
  $env:A7FF8_PLAN_PATH = (Join-Path $RunRoot "a7ls21_plan.json")
  $env:A7FF8_MATERIALIZE_CAP = "{ROWS_PER_SHARD}"
  $env:A7FF8_FAST_NUMERIC_CAP = "{ROWS_PER_SHARD}"
  $env:A7FF8_PORTFOLIO_CAP = "{ROWS_PER_SHARD}"
  $env:A7FF8_QUEUE_LIMIT = "{ROWS_PER_SHARD}"
  $env:A7FF8_HOURS_PER_SPLIT = "{HOURS_PER_SPLIT}"
  $env:A7FF8_WRITE_CONTROL_DETAIL = "1"

  $OldErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  & $Python scripts\crypto_a7ff8_expanded_numeric_probe.py > (Join-Path $ShardRoot "runner.log") 2>&1
  $code = $LASTEXITCODE
  $ErrorActionPreference = $OldErrorActionPreference
  if ($code -ne 0) {{
    Write-Output "[A7LS21] shard $Shard failed exit=$code"
    $summary += [pscustomobject]@{{ shard=$Shard; status="failed"; exit_code=$code; decision="" }}
  }} else {{
    $manifestPath = Join-Path $ShardRoot ("a7ls21_" + $Shard + "_manifest.json")
    $decision = ""
    if (Test-Path $manifestPath) {{
      try {{ $decision = (Get-Content -Raw $manifestPath | ConvertFrom-Json).decision }} catch {{}}
    }}
    Write-Output "[A7LS21] shard $Shard done decision=$decision"
    $summary += [pscustomobject]@{{ shard=$Shard; status="done"; exit_code=0; decision=$decision }}
  }}
}}

$summary | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $RunRoot "a7ls21_runner_summary.json")
Write-Output "[A7LS21] complete"
'''


def main() -> None:
    source_manifest = read_json(MANIFEST_IN)
    if source_manifest.get("decision") != "PASS_A7LS20_MARGINAL_QUEUE_READY_FOR_A7LS21_DEEP_REPLAY_PACKET":
        raise SystemExit(f"A7LS20 not ready: {source_manifest.get('decision')}")
    queue = pd.read_csv(QUEUE_IN)
    if queue.empty:
        raise SystemExit("empty A7LS20 marginal queue")

    RUNTIME.mkdir(parents=True, exist_ok=True)
    queue.to_csv(RUNTIME / "a7ls21_company_deep_replay_queue.csv", index=False)

    shard_rows: list[dict[str, Any]] = []
    shard_ids: list[str] = []
    for shard_idx, start in enumerate(range(0, len(queue), ROWS_PER_SHARD)):
        shard_id = f"s{shard_idx:03d}"
        shard_ids.append(shard_id)
        shard_dir = RUNTIME / "shards" / shard_id
        shard_dir.mkdir(parents=True, exist_ok=True)
        shard = queue.iloc[start : start + ROWS_PER_SHARD].copy()
        shard.to_csv(shard_dir / "queue.csv", index=False)
        shard_rows.append(
            {
                "shard_id": shard_id,
                "start_row": start,
                "end_row": start + len(shard),
                "rows": len(shard),
                "semantic_pair_count": int(shard["semantic_pair"].nunique()),
                "skeleton_count": int(shard["skeleton_key"].nunique()),
                "label_family_count": int(shard["label_family"].nunique()),
                "basis_premium_count": int(shard["contains_basis_premium"].sum()) if "contains_basis_premium" in shard else 0,
            }
        )

    shard_plan = pd.DataFrame(shard_rows)
    shard_plan.to_csv(RUNTIME / "a7ls21_shard_plan.csv", index=False)

    auth_manifest = {
        "stage": "A7LS-20",
        "decision": source_manifest["decision"],
        "source_manifest": str(MANIFEST_IN),
        "generated_for": "A7LS-21 company deep replay packet",
    }
    plan = {
        "stage": "A7LS-21",
        "remote_repo": REMOTE_REPO,
        "remote_run_root": REMOTE_RUN_ROOT,
        "rows_per_shard": ROWS_PER_SHARD,
        "shard_count": len(shard_ids),
        "hours_per_split": HOURS_PER_SPLIT,
        "labels": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return", "L7_ranked_future_return"],
        "uses_may": False,
        "executes_search": False,
        "authorizes_alpha_proof": False,
    }
    write_json(RUNTIME / "a7ls21_auth_manifest.json", auth_manifest)
    write_json(RUNTIME / "a7ls21_plan.json", plan)
    (RUNTIME / "run_a7ls21_company_deep_replay.ps1").write_text(build_runner(shard_ids), encoding="utf-8")

    manifest = {
        "stage": "A7LS-21-PACKET",
        "generated_at": now_utc(),
        "decision": "PASS_A7LS21_COMPANY_DEEP_REPLAY_PACKET_READY",
        "input_stage": "A7LS-20",
        "input_queue_count": int(len(queue)),
        "rows_per_shard": ROWS_PER_SHARD,
        "shard_count": len(shard_ids),
        "hours_per_split": HOURS_PER_SPLIT,
        "remote_repo": REMOTE_REPO,
        "remote_run_root": REMOTE_RUN_ROOT,
        "executes_search": False,
        "executes_numeric_probe": False,
        "uses_may": False,
        "authorizes_company_detached_execution": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls21_packet_manifest.json", manifest)
    write_json(RUNTIME / "a7ls21_decision_record.json", manifest)

    REPORT.write_text(
        "\n".join(
            [
                "# CRYPTO A7LS21 COMPANY DEEP REPLAY PACKET",
                "",
                f"Generated: {manifest['generated_at']}",
                "",
                "## Decision",
                "",
                "`PASS_A7LS21_COMPANY_DEEP_REPLAY_PACKET_READY`",
                "",
                "A7LS21 packages the A7LS20 48-row marginal queue into 4 company-machine numeric shards. This stage builds the packet only; detached company execution is separate.",
                "",
                "## Manifest",
                "",
                "```json",
                json.dumps(manifest, indent=2, sort_keys=True),
                "```",
                "",
                "## Shard Plan",
                "",
                md_table(shard_plan, 20),
                "",
                "## Boundary",
                "",
                "- New formula search: not authorized.",
                "- Alpha proof / shadow / paper / live: not authorized.",
                "- May is not used.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
