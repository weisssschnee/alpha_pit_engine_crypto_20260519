$ErrorActionPreference = "Stop"

$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Python = "D:\Python311\python.exe"
$AcceptedRoot = Join-Path $Repo "runtime\a7search7_strict_validation_reward_source5_py_aggregate_20260706"
$Runtime = Join-Path $Repo "runtime\a7source6_incremental_validation_pack_20260706"
$Report = Join-Path $Repo "reports\CRYPTO_A7SOURCE6_INCREMENTAL_VALIDATION_PACK_20260706.md"
$RewardRunRoot = "D:\HermesWorker\runtime\a7source6_incremental_validation_reward_20260706"
$RewardAggregateRuntime = Join-Path $Repo "runtime\a7source6_incremental_validation_reward_aggregate_20260706"
$RewardAggregateReport = Join-Path $Repo "reports\CRYPTO_A7SOURCE6_INCREMENTAL_VALIDATION_REWARD_AGGREGATE_20260706.md"
$Log = Join-Path $RewardRunRoot "a7source6_incremental_validation_company.log"
$StatusPath = Join-Path $RewardRunRoot "a7source6_incremental_validation_status.csv"

$RowsPerShard = 16
$MaxParallel = 8
if ($env:A7SOURCE6_MAX_PARALLEL) {
  $MaxParallel = [int]$env:A7SOURCE6_MAX_PARALLEL
}
$PollSeconds = 30
$MaxWaitHours = 8

New-Item -ItemType Directory -Force -Path $Runtime, $RewardRunRoot, $RewardAggregateRuntime | Out-Null
Set-Location $Repo

$env:PYTHONWARNINGS = "ignore"
$env:NUMEXPR_MAX_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"

function Write-Log {
  param([string]$Message)
  "[$(Get-Date -Format o)] $Message" | Out-File -Append -FilePath $Log -Encoding UTF8
}

function ManifestPathFor {
  param([string]$ShardId)
  return (Join-Path $RewardRunRoot ("shards\" + $ShardId + "\reward_runtime\a7reward1_manifest.json"))
}

Write-Log "A7SOURCE6 incremental validation start"
Write-Log "repo=$Repo"
Write-Log "accepted_root=$AcceptedRoot"
Write-Log "runtime=$Runtime"
Write-Log "reward_run_root=$RewardRunRoot"
Write-Log "max_parallel=$MaxParallel rows_per_shard=$RowsPerShard"

if (!(Test-Path $AcceptedRoot)) {
  throw "accepted root missing: $AcceptedRoot"
}

& $Python scripts\crypto_a7source6_incremental_validation_pack.py `
  --accepted-root $AcceptedRoot `
  --runtime $Runtime `
  --report $Report `
  --mode build `
  *> (Join-Path $Runtime "a7source6_build.log")
if ($LASTEXITCODE -ne 0) {
  throw "A7SOURCE6 queue build failed: $LASTEXITCODE"
}

$Queue = Join-Path $Runtime "a7source6_validation_ablation_queue.csv"
if (!(Test-Path $Queue)) {
  throw "A7SOURCE6 validation queue missing: $Queue"
}

$queueRows = @(Import-Csv $Queue).Count
Write-Log "validation_queue_rows=$queueRows"
if ($queueRows -le 0) {
  throw "A7SOURCE6 validation queue empty"
}

$env:A7V3S0_REWARD_PREQUEUE = $Queue
$env:A7V3S0_REWARD_SHARD_RUNTIME = $RewardRunRoot
$env:A7V3S0_REWARD_ROWS_PER_SHARD = "$RowsPerShard"
& $Python scripts\crypto_a7v3s0_reward_shard_queue.py *> (Join-Path $RewardRunRoot "reward_shard_queue.log")
if ($LASTEXITCODE -ne 0) {
  throw "reward shard queue failed: $LASTEXITCODE"
}

$Plan = @(Import-Csv (Join-Path $RewardRunRoot "a7v3s0_reward_shard_plan.csv"))
Write-Log "reward_shard_count=$($Plan.Count)"

$statusRows = New-Object System.Collections.Generic.List[object]
$running = @()
foreach ($row in $Plan) {
  while ($running.Count -ge $MaxParallel) {
    Start-Sleep -Seconds $PollSeconds
    $nextRunning = @()
    foreach ($entry in $running) {
      $manifest = ManifestPathFor $entry.shard_id
      $entry.process.Refresh()
      if (Test-Path $manifest) {
        $statusRows.Add([pscustomobject]@{ shard_id=$entry.shard_id; status="done"; exit_code=$entry.process.ExitCode; started_at=$entry.started_at; ended_at=(Get-Date -Format o); queue_path=$entry.queue_path })
        Write-Log "DONE reward $($entry.shard_id)"
      } elseif ($entry.process.HasExited) {
        $statusRows.Add([pscustomobject]@{ shard_id=$entry.shard_id; status="failed"; exit_code=$entry.process.ExitCode; started_at=$entry.started_at; ended_at=(Get-Date -Format o); queue_path=$entry.queue_path })
        $statusRows | Export-Csv -NoTypeInformation -Path $StatusPath
        throw "reward shard exited without manifest: $($entry.shard_id) exit=$($entry.process.ExitCode)"
      } else {
        $nextRunning += $entry
      }
    }
    $running = $nextRunning
    $statusRows | Export-Csv -NoTypeInformation -Path $StatusPath
  }

  $sid = $row.shard_id
  $shardRoot = Join-Path $RewardRunRoot ("shards\" + $sid)
  $rewardRuntime = Join-Path $shardRoot "reward_runtime"
  $rewardReport = Join-Path $shardRoot ("CRYPTO_" + $sid + "_A7SOURCE6_INCREMENTAL_VALIDATION_REWARD.md")
  $out = Join-Path $shardRoot "reward.out.log"
  $err = Join-Path $shardRoot "reward.err.log"
  New-Item -ItemType Directory -Force -Path $rewardRuntime, $shardRoot | Out-Null
  if (Test-Path (ManifestPathFor $sid)) {
    $statusRows.Add([pscustomobject]@{ shard_id=$sid; status="skip"; exit_code=0; started_at=""; ended_at=(Get-Date -Format o); queue_path=$row.queue_path })
    continue
  }
  $args = @(
    "scripts\crypto_a7reward1_portfolio_reward_model.py",
    "--queue", $row.queue_path,
    "--candidate-cap", "0",
    "--hours-per-split", "720",
    "--cost-bps", "5",
    "--checkpoint-every", "4",
    "--runtime", $rewardRuntime,
    "--report", $rewardReport
  )
  Write-Log "START reward $sid"
  $proc = Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $Repo -RedirectStandardOutput $out -RedirectStandardError $err -PassThru -WindowStyle Hidden
  $running += [pscustomobject]@{ process=$proc; shard_id=$sid; queue_path=$row.queue_path; started_at=(Get-Date -Format o) }
}

$deadline = (Get-Date).AddHours($MaxWaitHours)
while ($running.Count -gt 0) {
  if ((Get-Date) -gt $deadline) {
    throw "timeout waiting for A7SOURCE6 reward shards"
  }
  Start-Sleep -Seconds $PollSeconds
  $nextRunning = @()
  foreach ($entry in $running) {
    $manifest = ManifestPathFor $entry.shard_id
    $entry.process.Refresh()
    if (Test-Path $manifest) {
      $statusRows.Add([pscustomobject]@{ shard_id=$entry.shard_id; status="done"; exit_code=$entry.process.ExitCode; started_at=$entry.started_at; ended_at=(Get-Date -Format o); queue_path=$entry.queue_path })
      Write-Log "DONE reward $($entry.shard_id)"
    } elseif ($entry.process.HasExited) {
      $statusRows.Add([pscustomobject]@{ shard_id=$entry.shard_id; status="failed"; exit_code=$entry.process.ExitCode; started_at=$entry.started_at; ended_at=(Get-Date -Format o); queue_path=$entry.queue_path })
      $statusRows | Export-Csv -NoTypeInformation -Path $StatusPath
      throw "reward shard exited without manifest: $($entry.shard_id) exit=$($entry.process.ExitCode)"
    } else {
      $nextRunning += $entry
    }
  }
  $running = $nextRunning
  $statusRows | Export-Csv -NoTypeInformation -Path $StatusPath
}

$ManifestCount = @(Get-ChildItem -Path (Join-Path $RewardRunRoot "shards") -Filter "a7reward1_manifest.json" -Recurse -ErrorAction SilentlyContinue).Count
Write-Log "manifest_count=$ManifestCount expected=$($Plan.Count)"
if ($ManifestCount -ne $Plan.Count) {
  throw "manifest count mismatch: $ManifestCount / $($Plan.Count)"
}

& $Python scripts\crypto_a7v3s0_reward_sharded_aggregate.py `
  --run-root $RewardRunRoot `
  --runtime $RewardAggregateRuntime `
  --report $RewardAggregateReport `
  *> (Join-Path $RewardRunRoot "reward_aggregate.log")
if ($LASTEXITCODE -ne 0) {
  throw "reward aggregate failed: $LASTEXITCODE"
}

& $Python scripts\crypto_a7source6_incremental_validation_pack.py `
  --runtime $Runtime `
  --report $Report `
  --reward-aggregate-root $RewardAggregateRuntime `
  --mode summarize `
  *> (Join-Path $Runtime "a7source6_summarize.log")
if ($LASTEXITCODE -ne 0) {
  throw "A7SOURCE6 summarize failed: $LASTEXITCODE"
}

Write-Log "A7SOURCE6 incremental validation finished"
