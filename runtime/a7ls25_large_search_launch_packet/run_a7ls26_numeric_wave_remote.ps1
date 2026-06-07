$ErrorActionPreference = "Stop"

$Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe"
$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$MatRoot = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls25_large_search_materialization_20260607"
$Runtime = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls26_numeric_wave_20260608"
$Queue = Join-Path $Runtime "a7ls26_numeric_queue_4096.csv"
$Concurrency = 2
$RowsPerShard = 64
$TargetRows = 4096

Set-Location $Repo
New-Item -ItemType Directory -Force -Path $Runtime | Out-Null

$AggregateScript = Join-Path $Runtime "build_a7ls26_numeric_queue.py"
@'
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

mat_root = Path(r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls25_large_search_materialization_20260607")
runtime = Path(r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls26_numeric_wave_20260608")
target_rows = 4096

source_queue = pd.read_csv(mat_root / "a7ls25_materialization_queue_40k.csv", low_memory=False)
metrics_parts = []
for p in sorted((mat_root / "shards").glob("*/a7ls17_materialization_metrics.csv")):
    df = pd.read_csv(p, low_memory=False)
    df["source_shard"] = p.parent.name
    metrics_parts.append(df)

if not metrics_parts:
    raise SystemExit("no materialization metrics found")

metrics = pd.concat(metrics_parts, ignore_index=True)
ok = metrics[metrics["activity_ok"].astype(bool)].copy()
merged = ok.merge(
    source_queue[
        [
            "blueprint_id",
            "a7ls25_axis",
            "a7ls25_search_role",
            "a7ls25_source",
            "level",
            "candidate_role",
            "generation_priority",
            "primary_semantic",
            "secondary_semantic",
            "primary_transform",
            "secondary_transform",
            "checkpoint_group",
        ]
    ],
    on="blueprint_id",
    how="left",
    suffixes=("", "_src"),
)
merged["activity_score"] = (
    merged["finite_share"].fillna(0).clip(0, 1)
    * merged["nonzero_share"].fillna(0).clip(0, 1)
    * merged["std_value"].abs().fillna(0).clip(upper=10)
)

parts = []
axis_target = max(1, target_rows // max(1, merged["a7ls25_axis"].nunique()))
for _, axis_df in merged.sort_values("activity_score", ascending=False).groupby("a7ls25_axis", dropna=False):
    sem_target = max(1, axis_target // max(1, axis_df["semantic_pair"].nunique()))
    for _, sem_df in axis_df.groupby("semantic_pair", dropna=False):
        motif_target = max(1, sem_target // max(1, sem_df["motif"].nunique()))
        for _, motif_df in sem_df.groupby("motif", dropna=False):
            parts.append(motif_df.sort_values("activity_score", ascending=False).head(motif_target))

queue = pd.concat(parts, ignore_index=True).drop_duplicates("blueprint_id") if parts else merged.head(0)
if len(queue) < target_rows:
    extra = merged[~merged["blueprint_id"].isin(set(queue["blueprint_id"]))].sort_values("activity_score", ascending=False).head(target_rows - len(queue))
    queue = pd.concat([queue, extra], ignore_index=True)
queue = queue.head(target_rows).copy()

runtime.mkdir(parents=True, exist_ok=True)
queue.to_csv(runtime / "a7ls26_numeric_queue_4096.csv", index=False)

summary = {
    "stage": "A7LS-26",
    "decision": "PASS_A7LS26_NUMERIC_QUEUE_BUILT",
    "materialized_activity_ok_input_rows": int(len(merged)),
    "numeric_queue_rows": int(len(queue)),
    "axis_count": int(queue["a7ls25_axis"].nunique()),
    "semantic_pair_count": int(queue["semantic_pair"].nunique()),
    "motif_count": int(queue["motif"].nunique()),
    "skeleton_count": int(queue["skeleton_key"].nunique()),
}
(runtime / "a7ls26_numeric_queue_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
queue.groupby(["a7ls25_axis", "semantic_pair", "motif"], dropna=False).size().reset_index(name="rows").sort_values("rows", ascending=False).to_csv(runtime / "a7ls26_numeric_queue_family_summary.csv", index=False)
print(json.dumps(summary, indent=2, sort_keys=True))
'@ | Set-Content -Encoding UTF8 $AggregateScript

& $Python $AggregateScript
if ($LASTEXITCODE -ne 0) {
  throw "A7LS26 queue build failed with exit code $LASTEXITCODE"
}

$shards = @()
for ($start = 0; $start -lt $TargetRows; $start += $RowsPerShard) {
  $end = [Math]::Min($start + $RowsPerShard, $TargetRows)
  $sid = "a7ls26_num_s{0:D3}" -f ($start / $RowsPerShard)
  $shards += [pscustomobject]@{ id = $sid; start = $start; end = $end }
}

$active = @()
foreach ($s in $shards) {
  $manifest = Join-Path $Runtime ("shards\" + $s.id + "\a7ls26_" + $s.id + "_manifest.json")
  if (Test-Path $manifest) {
    Write-Host "[A7LS26] skip existing $($s.id)"
    continue
  }
  while (($active | Where-Object { -not $_.HasExited }).Count -ge $Concurrency) {
    Start-Sleep -Seconds 15
    $active = @($active | Where-Object { -not $_.HasExited })
  }

  $shardRoot = Join-Path $Runtime ("shards\" + $s.id)
  New-Item -ItemType Directory -Force -Path $shardRoot | Out-Null

  $env:A7FF8_STAGE = "A7LS-26-" + $s.id
  $env:A7FF8_FILE_PREFIX = "a7ls26_" + $s.id
  $env:A7FF8_RUNTIME = $shardRoot
  $env:A7FF8_REPORT = Join-Path $shardRoot ("A7LS26_" + $s.id + "_REPORT.md")
  $env:A7FF8_QUEUE_PATH = $Queue
  $env:A7FF8_QUEUE_OFFSET = [string]$s.start
  $env:A7FF8_QUEUE_LIMIT = [string]($s.end - $s.start)
  $env:A7FF8_MATERIALIZE_CAP = "64"
  $env:A7FF8_FAST_NUMERIC_CAP = "64"
  $env:A7FF8_PORTFOLIO_CAP = "32"
  $env:A7FF8_HOURS_PER_SPLIT = "2160"
  $env:A7FF8_WRITE_CONTROL_DETAIL = "0"

  $outLog = Join-Path $shardRoot "runner.out.log"
  $errLog = Join-Path $shardRoot "runner.err.log"
  Write-Host "[A7LS26] start $($s.id) rows=$($s.start):$($s.end)"
  $p = Start-Process -FilePath $Python -ArgumentList @("scripts\crypto_a7ff8_expanded_numeric_probe.py") -RedirectStandardOutput $outLog -RedirectStandardError $errLog -PassThru -WindowStyle Hidden
  $active += $p
}

while (($active | Where-Object { -not $_.HasExited }).Count -gt 0) {
  Start-Sleep -Seconds 30
  $active = @($active | Where-Object { -not $_.HasExited })
}

$summary = @()
foreach ($s in $shards) {
  $manifest = Join-Path $Runtime ("shards\" + $s.id + "\a7ls26_" + $s.id + "_manifest.json")
  if (Test-Path $manifest) {
    $m = Get-Content $manifest -Raw | ConvertFrom-Json
    $summary += [pscustomobject]@{
      shard_id = $s.id
      decision = $m.decision
      queue_total_rows = $m.queue_total_rows
      materialized_activity_ok_count = $m.materialized_activity_ok_count
      non_l7_numeric_clue_rows = $m.non_l7_numeric_clue_rows
      rank_label_diagnostic_clue_rows = $m.rank_label_diagnostic_clue_rows
      selected_portfolio_queue_count = $m.selected_portfolio_queue_count
    }
  } else {
    $summary += [pscustomobject]@{ shard_id=$s.id; decision="MISSING_MANIFEST" }
  }
}
$summary | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $Runtime "a7ls26_numeric_wave_summary.json")
Write-Host "[A7LS26] numeric wave complete"
