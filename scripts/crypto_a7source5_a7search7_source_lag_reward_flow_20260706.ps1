$ErrorActionPreference = "Stop"

$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe"

$StrictPackRuntime = Join-Path $Repo "runtime\a7search7_strict_accepted_pack_20260706"
$ValidationQueue = Join-Path $StrictPackRuntime "a7search7_validation_ablation_queue.csv"

$SourceRunRoot = "D:\HermesWorker\runtime\a7source5_a7search7_source_lag_retest_20260706"
$SourceAggregateRuntime = Join-Path $Repo "runtime\a7source5_a7search7_source_lag_retest_aggregate_20260706"
$SourceAggregateReport = Join-Path $Repo "reports\CRYPTO_A7SOURCE5_A7SEARCH7_SOURCE_LAG_RETEST_AGGREGATE_20260706.md"

$RewardRunRoot = "D:\HermesWorker\runtime\a7search7_strict_validation_reward_source5_20260706"
$RewardAggregateRuntime = Join-Path $Repo "runtime\a7search7_strict_validation_reward_source5_aggregate_20260706"
$RewardAggregateReport = Join-Path $Repo "reports\CRYPTO_A7SEARCH7_STRICT_VALIDATION_REWARD_SOURCE5_AGGREGATE_20260706.md"

$Log = Join-Path $SourceRunRoot "a7source5_source_lag_reward_flow.log"
$SourceStatusPath = Join-Path $SourceRunRoot "a7source5_source_lag_status.csv"
$RewardStatusPath = Join-Path $RewardRunRoot "a7search7_strict_validation_reward_source5_status.csv"

$RowsPerShard = 16
$MaxParallel = 8
if ($env:A7SOURCE5_MAX_PARALLEL) {
  $MaxParallel = [int]$env:A7SOURCE5_MAX_PARALLEL
}
$PollSeconds = 20
$MaxWaitHours = 12

New-Item -ItemType Directory -Force -Path $SourceRunRoot, $SourceAggregateRuntime, $RewardRunRoot, $RewardAggregateRuntime | Out-Null
Set-Location $Repo

$LockPath = Join-Path $SourceRunRoot "a7source5_flow.lock"
try {
  New-Item -ItemType File -Path $LockPath -Value (Get-Date -Format o) -ErrorAction Stop | Out-Null
} catch {
  "[$(Get-Date -Format o)] lock exists; duplicate launch exits: $LockPath" | Out-File -Append -FilePath (Join-Path $SourceRunRoot "a7source5_duplicate_launch.log") -Encoding UTF8
  exit 0
}

$env:PYTHONWARNINGS = "ignore"
$env:NUMEXPR_MAX_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"

function Write-Log {
  param([string]$Message)
  "[$(Get-Date -Format o)] $Message" | Out-File -Append -FilePath $Log -Encoding UTF8
}

function Export-Shards {
  param(
    [string]$InputCsv,
    [string]$ShardDir,
    [string]$Prefix,
    [int]$RowsPerShard
  )
  New-Item -ItemType Directory -Force -Path $ShardDir | Out-Null
  $rows = @(Import-Csv $InputCsv)
  if ($rows.Count -le 0) {
    throw "empty input csv: $InputCsv"
  }
  $plan = New-Object System.Collections.Generic.List[object]
  $idx = 0
  for ($start = 0; $start -lt $rows.Count; $start += $RowsPerShard) {
    $sid = "{0}_s{1:D3}" -f $Prefix, $idx
    $path = Join-Path $ShardDir ($sid + ".csv")
    $end = [Math]::Min($start + $RowsPerShard - 1, $rows.Count - 1)
    $rows[$start..$end] | Export-Csv -NoTypeInformation -Path $path
    $plan.Add([pscustomobject]@{ shard_id=$sid; queue_path=$path; row_count=($end - $start + 1) })
    $idx += 1
  }
  return $plan.ToArray()
}

function Wait-ProcessPool {
  param(
    [System.Collections.ArrayList]$Running,
    [string]$StatusPath,
    [scriptblock]$ManifestFor,
    [string]$Kind
  )
  $statusRows = New-Object System.Collections.Generic.List[object]
  $deadline = (Get-Date).AddHours($MaxWaitHours)
  while ($Running.Count -gt 0) {
    if ((Get-Date) -gt $deadline) {
      throw "timeout waiting for $Kind shards"
    }
    Start-Sleep -Seconds $PollSeconds
    $nextRunning = New-Object System.Collections.ArrayList
    foreach ($entry in $Running) {
      $manifest = & $ManifestFor $entry.shard_id
      $entry.process.Refresh()
      if (Test-Path $manifest) {
        $statusRows.Add([pscustomobject]@{ shard_id=$entry.shard_id; status="done"; exit_code=$entry.process.ExitCode; started_at=$entry.started_at; ended_at=(Get-Date -Format o); queue_path=$entry.queue_path }) | Out-Null
        Write-Log "DONE $Kind $($entry.shard_id)"
      } elseif ($entry.process.HasExited) {
        $statusRows.Add([pscustomobject]@{ shard_id=$entry.shard_id; status="failed"; exit_code=$entry.process.ExitCode; started_at=$entry.started_at; ended_at=(Get-Date -Format o); queue_path=$entry.queue_path }) | Out-Null
        $statusRows | Export-Csv -NoTypeInformation -Path $StatusPath
        throw "$Kind shard exited without manifest: $($entry.shard_id) exit=$($entry.process.ExitCode)"
      } else {
        [void]$nextRunning.Add($entry)
      }
    }
    $Running = $nextRunning
    $statusRows | Export-Csv -NoTypeInformation -Path $StatusPath
  }
}

function Aggregate-Csv {
  param(
    [string]$Pattern,
    [string]$OutputPath
  )
  $frames = New-Object System.Collections.Generic.List[object]
  foreach ($path in Get-ChildItem -Path $Pattern -ErrorAction SilentlyContinue) {
    if ($path.Length -le 0) { continue }
    $rows = @(Import-Csv $path.FullName)
    foreach ($row in $rows) {
      $row | Add-Member -NotePropertyName source_file -NotePropertyValue $path.FullName -Force
      $frames.Add($row) | Out-Null
    }
  }
  if ($frames.Count -eq 0) {
    "" | Out-File -FilePath $OutputPath -Encoding UTF8
  } else {
    $frames | Export-Csv -NoTypeInformation -Path $OutputPath
  }
}

function SourceManifestFor {
  param([string]$ShardId)
  return (Join-Path $SourceRunRoot ("shards\" + $ShardId + "\runtime\a7source4_manifest.json"))
}

function RewardManifestFor {
  param([string]$ShardId)
  return (Join-Path $RewardRunRoot ("shards\" + $ShardId + "\reward_runtime\a7reward1_manifest.json"))
}

Write-Log "A7SOURCE5 source-lag -> strict reward flow start"
Write-Log "repo=$Repo"
Write-Log "validation_queue=$ValidationQueue"
Write-Log "max_parallel=$MaxParallel rows_per_shard=$RowsPerShard"

if (!(Test-Path $ValidationQueue)) {
  throw "missing validation queue: $ValidationQueue"
}

$sourcePlan = Export-Shards -InputCsv $ValidationQueue -ShardDir (Join-Path $SourceRunRoot "source_queue_shards") -Prefix "a7source5" -RowsPerShard $RowsPerShard
$sourcePlan | Export-Csv -NoTypeInformation -Path (Join-Path $SourceRunRoot "a7source5_source_lag_shard_plan.csv")
Write-Log "source_shard_count=$($sourcePlan.Count)"

$running = New-Object System.Collections.ArrayList
foreach ($row in $sourcePlan) {
  while ($running.Count -ge $MaxParallel) {
    Wait-ProcessPool -Running $running -StatusPath $SourceStatusPath -ManifestFor ${function:SourceManifestFor} -Kind "source_lag"
    $running = New-Object System.Collections.ArrayList
  }
  $sid = $row.shard_id
  $shardRoot = Join-Path $SourceRunRoot ("shards\" + $sid)
  $runtime = Join-Path $shardRoot "runtime"
  $report = Join-Path $shardRoot ("CRYPTO_" + $sid + "_SOURCE_LAG_RETEST.md")
  $out = Join-Path $shardRoot "source_lag.out.log"
  $err = Join-Path $shardRoot "source_lag.err.log"
  New-Item -ItemType Directory -Force -Path $runtime, $shardRoot | Out-Null
  if (Test-Path (SourceManifestFor $sid)) {
    continue
  }
  $args = @(
    "scripts\crypto_a7source4_batch_source_lag_retest.py",
    "--input", $row.queue_path,
    "--runtime", $runtime,
    "--report", $report,
    "--max-rows", "100000",
    "--cost-bps", "5"
  )
  Write-Log "START source_lag $sid"
  $proc = Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $Repo -RedirectStandardOutput $out -RedirectStandardError $err -PassThru -WindowStyle Hidden
  [void]$running.Add([pscustomobject]@{ process=$proc; shard_id=$sid; queue_path=$row.queue_path; started_at=(Get-Date -Format o) })
}
Wait-ProcessPool -Running $running -StatusPath $SourceStatusPath -ManifestFor ${function:SourceManifestFor} -Kind "source_lag"

Aggregate-Csv -Pattern (Join-Path $SourceRunRoot "shards\*\runtime\a7source4_source_lag_summary.csv") -OutputPath (Join-Path $SourceAggregateRuntime "a7source5_source_lag_summary.csv")
Aggregate-Csv -Pattern (Join-Path $SourceRunRoot "shards\*\runtime\a7source4_source_lag_metrics.csv") -OutputPath (Join-Path $SourceAggregateRuntime "a7source5_source_lag_metrics.csv")
Aggregate-Csv -Pattern (Join-Path $SourceRunRoot "shards\*\runtime\a7source4_eval_errors.csv") -OutputPath (Join-Path $SourceAggregateRuntime "a7source5_source_lag_eval_errors.csv")

$sourceSummary = Import-Csv (Join-Path $SourceAggregateRuntime "a7source5_source_lag_summary.csv")
$sourcePassCount = @($sourceSummary | Where-Object { $_.source_lag_gate -eq "PASS_SOURCE_LAG_1H_2H_DIAGNOSTIC" }).Count
$sourceManifestCount = @(Get-ChildItem -Path (Join-Path $SourceRunRoot "shards") -Filter "a7source4_manifest.json" -Recurse -ErrorAction SilentlyContinue).Count
$sourceManifest = [pscustomobject]@{
  stage="A7SOURCE5-A7SEARCH7-SOURCE-LAG-AGGREGATE"
  generated_at=(Get-Date -Format o)
  source_shards_expected=$sourcePlan.Count
  source_manifest_count=$sourceManifestCount
  source_lag_summary_rows=@($sourceSummary).Count
  source_lag_pass_count=$sourcePassCount
  source_lag_summary=(Join-Path $SourceAggregateRuntime "a7source5_source_lag_summary.csv")
  authorizes_alpha_proof=$false
  authorizes_shadow_paper_live=$false
}
$sourceManifest | ConvertTo-Json -Depth 6 | Out-File -FilePath (Join-Path $SourceAggregateRuntime "a7source5_manifest.json") -Encoding UTF8

$sourceDecision = if ($sourcePassCount -gt 0) { "PASS_A7SOURCE5_SOURCE_LAG_SURVIVORS_FOUND" } else { "HOLD_A7SOURCE5_SOURCE_LAG_NO_SURVIVORS" }
$sourcePlanCount = $sourcePlan.Count
$sourceSummaryRows = @($sourceSummary).Count
@(
  "# CRYPTO A7SOURCE5 A7SEARCH7 Source-Lag Retest Aggregate",
  "",
  "## Decision",
  "",
  $sourceDecision,
  "",
  "## Counts",
  "",
  ("- source_shards_expected: " + $sourcePlanCount),
  ("- source_manifest_count: " + $sourceManifestCount),
  ("- source_lag_summary_rows: " + $sourceSummaryRows),
  ("- source_lag_pass_count: " + $sourcePassCount),
  "",
  "This is a source-lag diagnostic and strict reward input, not alpha proof."
) | Out-File -FilePath $SourceAggregateReport -Encoding UTF8

Write-Log "source_lag aggregate pass_count=$sourcePassCount manifest_count=$sourceManifestCount expected=$($sourcePlan.Count)"

$env:A7V3S0_REWARD_PREQUEUE = $ValidationQueue
$env:A7V3S0_REWARD_SHARD_RUNTIME = $RewardRunRoot
$env:A7V3S0_REWARD_ROWS_PER_SHARD = "$RowsPerShard"
& $Python scripts\crypto_a7v3s0_reward_shard_queue.py *> (Join-Path $RewardRunRoot "reward_shard_queue.log")
if ($LASTEXITCODE -ne 0) {
  throw "reward shard queue failed: $LASTEXITCODE"
}

$rewardPlan = @(Import-Csv (Join-Path $RewardRunRoot "a7v3s0_reward_shard_plan.csv"))
Write-Log "reward_shard_count=$($rewardPlan.Count)"

$running = New-Object System.Collections.ArrayList
foreach ($row in $rewardPlan) {
  while ($running.Count -ge $MaxParallel) {
    Wait-ProcessPool -Running $running -StatusPath $RewardStatusPath -ManifestFor ${function:RewardManifestFor} -Kind "reward_source5"
    $running = New-Object System.Collections.ArrayList
  }
  $sid = $row.shard_id
  $shardRoot = Join-Path $RewardRunRoot ("shards\" + $sid)
  $rewardRuntime = Join-Path $shardRoot "reward_runtime"
  $rewardReport = Join-Path $shardRoot ("CRYPTO_" + $sid + "_A7SEARCH7_STRICT_VALIDATION_REWARD_SOURCE5.md")
  $out = Join-Path $shardRoot "reward.out.log"
  $err = Join-Path $shardRoot "reward.err.log"
  New-Item -ItemType Directory -Force -Path $rewardRuntime, $shardRoot | Out-Null
  if (Test-Path (RewardManifestFor $sid)) {
    continue
  }
  $args = @(
    "scripts\crypto_a7reward1_portfolio_reward_model.py",
    "--queue", $row.queue_path,
    "--candidate-cap", "0",
    "--hours-per-split", "720",
    "--cost-bps", "5",
    "--checkpoint-every", "4",
    "--source-lag-summary", (Join-Path $SourceAggregateRuntime "a7source5_source_lag_summary.csv"),
    "--runtime", $rewardRuntime,
    "--report", $rewardReport
  )
  Write-Log "START reward_source5 $sid"
  $proc = Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $Repo -RedirectStandardOutput $out -RedirectStandardError $err -PassThru -WindowStyle Hidden
  [void]$running.Add([pscustomobject]@{ process=$proc; shard_id=$sid; queue_path=$row.queue_path; started_at=(Get-Date -Format o) })
}
Wait-ProcessPool -Running $running -StatusPath $RewardStatusPath -ManifestFor ${function:RewardManifestFor} -Kind "reward_source5"

$rewardManifestCount = @(Get-ChildItem -Path (Join-Path $RewardRunRoot "shards") -Filter "a7reward1_manifest.json" -Recurse -ErrorAction SilentlyContinue).Count
Write-Log "reward manifest_count=$rewardManifestCount expected=$($rewardPlan.Count)"
if ($rewardManifestCount -ne $rewardPlan.Count) {
  throw "reward manifest count mismatch: $rewardManifestCount / $($rewardPlan.Count)"
}

& $Python scripts\crypto_a7v3s0_reward_sharded_aggregate.py --run-root $RewardRunRoot --runtime $RewardAggregateRuntime --report $RewardAggregateReport *> (Join-Path $RewardRunRoot "reward_aggregate.log")
if ($LASTEXITCODE -ne 0) {
  throw "reward aggregate failed: $LASTEXITCODE"
}

Write-Log "A7SOURCE5 source-lag -> strict reward flow finished"
