$ErrorActionPreference = "Stop"

$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe"
$InputRoot = "D:\HermesWorker\runtime\a7search7_family_diversified_proxy_65k_r2_20260704\a7search7_r2_quick_aggregate_20260706"
$Runtime = Join-Path $Repo "runtime\a7search7_strict_accepted_pack_20260706"
$Report = Join-Path $Repo "reports\CRYPTO_A7SEARCH7_STRICT_ACCEPTED_PACK_20260706.md"
$RewardRunRoot = "D:\HermesWorker\runtime\a7search7_strict_validation_reward_20260706"
$RewardAggregateRuntime = Join-Path $Repo "runtime\a7search7_strict_validation_reward_aggregate_20260706"
$RewardAggregateReport = Join-Path $Repo "reports\CRYPTO_A7SEARCH7_STRICT_VALIDATION_REWARD_AGGREGATE_20260706.md"
$Log = Join-Path $RewardRunRoot "a7search7_strict_validation_company.log"
$StatusPath = Join-Path $RewardRunRoot "a7search7_strict_validation_status.csv"

$RowsPerShard = 16
$MaxParallel = 8
if ($env:A7SEARCH7_VALIDATION_MAX_PARALLEL) {
  $MaxParallel = [int]$env:A7SEARCH7_VALIDATION_MAX_PARALLEL
}
$PollSeconds = 30
$MaxWaitHours = 10

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

Write-Log "A7SEARCH7 strict validation start"
Write-Log "repo=$Repo"
Write-Log "input_root=$InputRoot"
Write-Log "runtime=$Runtime"
Write-Log "reward_run_root=$RewardRunRoot"
Write-Log "max_parallel=$MaxParallel rows_per_shard=$RowsPerShard"

Write-Log "skip git pull; launcher is deployed by explicit upload/commit sync"

& $Python scripts\crypto_a7search7_strict_accepted_pack.py `
  --input-root $InputRoot `
  --runtime $Runtime `
  --report $Report `
  *> (Join-Path $Runtime "a7search7_strict_pack_build.log")
if ($LASTEXITCODE -ne 0) {
  throw "strict accepted pack build failed: $LASTEXITCODE"
}

$Queue = Join-Path $Runtime "a7search7_validation_ablation_queue.csv"
if (!(Test-Path $Queue)) {
  throw "validation queue missing: $Queue"
}

$queueRows = @(Import-Csv $Queue).Count
Write-Log "validation_queue_rows=$queueRows"
if ($queueRows -le 0) {
  throw "strict validation queue empty"
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
  $rewardReport = Join-Path $shardRoot ("CRYPTO_" + $sid + "_A7SEARCH7_STRICT_VALIDATION_REWARD.md")
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
    throw "timeout waiting for strict validation reward shards"
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

& $Python scripts\crypto_a7v3s0_reward_sharded_aggregate.py --run-root $RewardRunRoot --runtime $RewardAggregateRuntime --report $RewardAggregateReport *> (Join-Path $RewardRunRoot "reward_aggregate.log")
if ($LASTEXITCODE -ne 0) {
  throw "reward aggregate failed: $LASTEXITCODE"
}

Write-Log "A7SEARCH7 strict validation finished"
