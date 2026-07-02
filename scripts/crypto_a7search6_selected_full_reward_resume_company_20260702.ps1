$ErrorActionPreference = "Stop"

$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe"
$RunRoot = "D:\HermesWorker\runtime\a7search6_selected_full_reward_r1_20260702"
$AggregateRuntime = Join-Path $Repo "runtime\a7search6_selected_full_reward_r1_aggregate_20260702"
$AggregateReport = Join-Path $Repo "reports\CRYPTO_A7SEARCH6_SELECTED_FULL_REWARD_R1_AGGREGATE_20260702.md"
$PlanPath = Join-Path $RunRoot "a7v3s0_reward_shard_plan.csv"
$Log = Join-Path $RunRoot "a7search6_selected_full_reward_r1_resume.log"
$StatusPath = Join-Path $RunRoot "a7search6_reward_resume_status.csv"
$MaxParallel = 4
$PollSeconds = 30
$MaxWaitHours = 6

New-Item -ItemType Directory -Force -Path $RunRoot, $AggregateRuntime | Out-Null
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
  return (Join-Path $RunRoot ("shards\" + $ShardId + "\reward_runtime\a7reward1_manifest.json"))
}

if (!(Test-Path $PlanPath)) {
  throw "missing shard plan: $PlanPath"
}

$Plan = @(Import-Csv $PlanPath)
$Remaining = @()
foreach ($row in $Plan) {
  if (!(Test-Path (ManifestPathFor $row.shard_id))) {
    $Remaining += $row
  }
}

Write-Log "resume start plan_count=$($Plan.Count) remaining=$($Remaining.Count)"

$statusRows = New-Object System.Collections.Generic.List[object]
$running = @()
foreach ($row in $Remaining) {
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
  $shardRoot = Join-Path $RunRoot ("shards\" + $sid)
  $runtime = Join-Path $shardRoot "reward_runtime"
  $report = Join-Path $shardRoot ("CRYPTO_" + $sid + "_A7SEARCH6_FULL_REWARD.md")
  $out = Join-Path $shardRoot "reward.resume.out.log"
  $err = Join-Path $shardRoot "reward.resume.err.log"
  New-Item -ItemType Directory -Force -Path $runtime, $shardRoot | Out-Null
  $args = @(
    "scripts\crypto_a7reward1_portfolio_reward_model.py",
    "--queue", $row.queue_path,
    "--candidate-cap", "0",
    "--hours-per-split", "720",
    "--cost-bps", "5",
    "--checkpoint-every", "4",
    "--runtime", $runtime,
    "--report", $report
  )
  Write-Log "START reward $sid"
  $proc = Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $Repo -RedirectStandardOutput $out -RedirectStandardError $err -PassThru -WindowStyle Hidden
  $running += [pscustomobject]@{ process=$proc; shard_id=$sid; queue_path=$row.queue_path; started_at=(Get-Date -Format o) }
}

$deadline = (Get-Date).AddHours($MaxWaitHours)
while ($running.Count -gt 0) {
  if ((Get-Date) -gt $deadline) {
    throw "timeout waiting for remaining reward shards"
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

$ManifestCount = @(Get-ChildItem -Path (Join-Path $RunRoot "shards") -Filter "a7reward1_manifest.json" -Recurse -ErrorAction SilentlyContinue).Count
Write-Log "manifest_count=$ManifestCount expected=$($Plan.Count)"
if ($ManifestCount -ne $Plan.Count) {
  throw "manifest count mismatch: $ManifestCount / $($Plan.Count)"
}

& $Python scripts\crypto_a7v3s0_reward_sharded_aggregate.py --run-root $RunRoot --runtime $AggregateRuntime --report $AggregateReport *> (Join-Path $RunRoot "reward_aggregate.resume.log")
if ($LASTEXITCODE -ne 0) {
  throw "reward aggregate failed: $LASTEXITCODE"
}
Write-Log "resume finished and aggregate completed"
