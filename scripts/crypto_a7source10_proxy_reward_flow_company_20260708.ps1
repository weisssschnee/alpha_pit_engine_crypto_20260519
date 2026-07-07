$ErrorActionPreference = "Stop"

$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Python = "D:\Python311\python.exe"
if (!(Test-Path $Python)) {
  $Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe"
}

$RunRoot = "D:\HermesWorker\runtime\a7source10_seed_expansion_proxy_20260708"
$AggregateRuntime = Join-Path $Repo "runtime\a7source10_seed_expansion_proxy_aggregate_20260708"
$RewardRunRoot = "D:\HermesWorker\runtime\a7source10_seed_expansion_reward_20260708"
$RewardAggregateRuntime = Join-Path $Repo "runtime\a7source10_seed_expansion_reward_aggregate_20260708"
$Queue = Join-Path $Repo "runtime\a7source10_seed_expansion_queue_20260708\a7source10_seed_expansion_proxy_queue.csv"
$ProxyReport = Join-Path $Repo "reports\CRYPTO_A7SOURCE10_SEED_EXPANSION_PROXY_AGGREGATE_20260708.md"
$RewardReport = Join-Path $Repo "reports\CRYPTO_A7SOURCE10_SEED_EXPANSION_REWARD_AGGREGATE_20260708.md"

$ProxyRowsPerShard = 64
$RewardRowsPerShard = 16
$MaxParallel = 8
if ($env:A7SOURCE10_MAX_PARALLEL) {
  $MaxParallel = [int]$env:A7SOURCE10_MAX_PARALLEL
}
$ManifestWaitSeconds = 1800

New-Item -ItemType Directory -Force -Path $RunRoot, $AggregateRuntime, $RewardRunRoot, $RewardAggregateRuntime | Out-Null
Set-Location $Repo

$env:NUMEXPR_MAX_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"

$Log = Join-Path $RunRoot "a7source10_proxy_reward_flow.log"
"[$(Get-Date -Format o)] A7SOURCE10 proxy -> reward flow start" | Out-File -FilePath $Log -Encoding UTF8
"repo=$Repo" | Out-File -Append -FilePath $Log -Encoding UTF8
"python=$Python" | Out-File -Append -FilePath $Log -Encoding UTF8

"[$(Get-Date -Format o)] asset_mode=uploaded_files source_commit=8c9e35a" | Out-File -Append -FilePath $Log

if (!(Test-Path $Queue)) {
  throw "missing A7SOURCE10 queue: $Queue"
}

function Start-ShardBatch {
  param(
    [array]$Rows,
    [string]$Stage,
    [string]$RuntimeName,
    [string]$ReportSuffix,
    [int]$CheckpointEvery,
    [string]$StatusPath
  )
  $statusRows = New-Object System.Collections.Generic.List[object]
  for ($start = 0; $start -lt $Rows.Count; $start += $MaxParallel) {
    $end = [Math]::Min($start + $MaxParallel, $Rows.Count)
    $procs = @()
    for ($i = $start; $i -lt $end; $i++) {
      $row = $Rows[$i]
      $sid = $row.shard_id
      $shardRoot = Join-Path (Split-Path $StatusPath -Parent) ("shards\" + $sid)
      $runtime = Join-Path $shardRoot $RuntimeName
      $report = Join-Path $shardRoot ("CRYPTO_" + $sid + $ReportSuffix)
      $out = Join-Path $shardRoot ($Stage + ".out.log")
      $err = Join-Path $shardRoot ($Stage + ".err.log")
      New-Item -ItemType Directory -Force -Path $runtime, $shardRoot | Out-Null
      $manifest = if ($Stage -eq "proxy") { Join-Path $runtime "a7v3s9_proxy_manifest.json" } else { Join-Path $runtime "a7reward1_manifest.json" }
      if (Test-Path $manifest) {
        $statusRows.Add([pscustomobject]@{ shard_id=$sid; status="skip"; exit_code=0; started_at=""; ended_at=(Get-Date -Format o); queue_path=$row.queue_path })
        continue
      }
      if ($Stage -eq "proxy") {
        $args = @(
          "scripts\crypto_a7v3s9_prereward_oos_control_proxy.py",
          "--queue", $row.queue_path,
          "--runtime", $runtime,
          "--report", $report,
          "--candidate-cap", "0",
          "--select-target", "48",
          "--pair-cap", "16",
          "--motif-cap", "24",
          "--skeleton-cap", "2",
          "--checkpoint-every", "$CheckpointEvery"
        )
      } else {
        $args = @(
          "scripts\crypto_a7reward1_portfolio_reward_model.py",
          "--queue", $row.queue_path,
          "--candidate-cap", "0",
          "--hours-per-split", "720",
          "--cost-bps", "5",
          "--checkpoint-every", "$CheckpointEvery",
          "--runtime", $runtime,
          "--report", $report
        )
      }
      "[$(Get-Date -Format o)] START $Stage $sid" | Out-File -Append -FilePath $Log
      $proc = Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $Repo -RedirectStandardOutput $out -RedirectStandardError $err -PassThru -WindowStyle Hidden
      $procs += [pscustomobject]@{ process=$proc; shard_id=$sid; queue_path=$row.queue_path; started_at=(Get-Date -Format o) }
    }
    foreach ($entry in $procs) {
      Wait-Process -Id $entry.process.Id
      $entry.process.Refresh()
      $exit = $entry.process.ExitCode
      $runtimeName = if ($Stage -eq "proxy") { "proxy_runtime" } else { "reward_runtime" }
      $manifestName = if ($Stage -eq "proxy") { "a7v3s9_proxy_manifest.json" } else { "a7reward1_manifest.json" }
      $manifestPath = Join-Path (Join-Path (Join-Path (Split-Path $StatusPath -Parent) ("shards\" + $entry.shard_id)) $runtimeName) $manifestName
      $waitStart = Get-Date
      while (!(Test-Path $manifestPath) -and (((Get-Date) - $waitStart).TotalSeconds -lt $ManifestWaitSeconds)) {
        Start-Sleep -Seconds 10
      }
      $status = if (Test-Path $manifestPath) { "done" } else { "failed" }
      $statusRows.Add([pscustomobject]@{ shard_id=$entry.shard_id; status=$status; exit_code=$exit; started_at=$entry.started_at; ended_at=(Get-Date -Format o); queue_path=$entry.queue_path })
      "[$(Get-Date -Format o)] END $Stage $($entry.shard_id) exit=$exit status=$status" | Out-File -Append -FilePath $Log
      if (!(Test-Path $manifestPath)) {
        $statusRows | Export-Csv -NoTypeInformation -Path $StatusPath
        throw "$Stage shard missing manifest $($entry.shard_id) exit=$exit manifest=$manifestPath"
      }
    }
    $statusRows | Export-Csv -NoTypeInformation -Path $StatusPath
  }
}

$ProxyShardRoot = Join-Path $RunRoot "queue_shards"
New-Item -ItemType Directory -Force -Path $ProxyShardRoot | Out-Null
$Rows = Import-Csv $Queue
$PlanRows = New-Object System.Collections.Generic.List[object]
for ($start = 0; $start -lt $Rows.Count; $start += $ProxyRowsPerShard) {
  $end = [Math]::Min($start + $ProxyRowsPerShard, $Rows.Count)
  $idx = [int]($start / $ProxyRowsPerShard)
  $sid = "a7source10_proxy_s{0:D3}" -f $idx
  $path = Join-Path $ProxyShardRoot "$sid.csv"
  $Rows[$start..($end - 1)] | Export-Csv -NoTypeInformation -Path $path
  $PlanRows.Add([pscustomobject]@{ shard_id=$sid; start_row=$start; end_row=$end; rows=($end-$start); queue_path=$path })
}
$ProxyPlan = Join-Path $RunRoot "a7source10_proxy_shard_plan.csv"
$PlanRows | Export-Csv -NoTypeInformation -Path $ProxyPlan
"[$(Get-Date -Format o)] proxy shard_count=$($PlanRows.Count) max_parallel=$MaxParallel" | Out-File -Append -FilePath $Log

Start-ShardBatch -Rows $PlanRows.ToArray() -Stage "proxy" -RuntimeName "proxy_runtime" -ReportSuffix "_PROXY.md" -CheckpointEvery 16 -StatusPath (Join-Path $RunRoot "a7source10_proxy_status.csv")

& $Python scripts\crypto_a7v3s9_proxy_aggregate.py --run-root $RunRoot --runtime $AggregateRuntime --report $ProxyReport --select-target 384
if ($LASTEXITCODE -ne 0) { throw "proxy aggregate failed: $LASTEXITCODE" }

$ProxyManifest = Get-Content (Join-Path $AggregateRuntime "a7v3s9_proxy_aggregate_manifest.json") | ConvertFrom-Json
"[$(Get-Date -Format o)] proxy aggregate selected=$($ProxyManifest.selected_rows) errors=$($ProxyManifest.eval_error_rows)" | Out-File -Append -FilePath $Log
if (($ProxyManifest.selected_rows -le 0) -or ($ProxyManifest.eval_error_rows -gt 0)) {
  "[$(Get-Date -Format o)] no reward continuation" | Out-File -Append -FilePath $Log
  exit 0
}

$SelectedQueue = Join-Path $AggregateRuntime "a7v3s9_proxy_selected_for_reward.csv"
$env:A7V3S0_REWARD_PREQUEUE = $SelectedQueue
$env:A7V3S0_REWARD_SHARD_RUNTIME = $RewardRunRoot
$env:A7V3S0_REWARD_ROWS_PER_SHARD = "$RewardRowsPerShard"
& $Python scripts\crypto_a7v3s0_reward_shard_queue.py
if ($LASTEXITCODE -ne 0) { throw "reward shard queue failed: $LASTEXITCODE" }

$RewardPlan = Import-Csv (Join-Path $RewardRunRoot "a7v3s0_reward_shard_plan.csv")
"[$(Get-Date -Format o)] reward shard_count=$($RewardPlan.Count) max_parallel=$MaxParallel" | Out-File -Append -FilePath $Log
Start-ShardBatch -Rows $RewardPlan -Stage "reward" -RuntimeName "reward_runtime" -ReportSuffix "_FULL_REWARD.md" -CheckpointEvery 4 -StatusPath (Join-Path $RewardRunRoot "a7source10_reward_status.csv")

& $Python scripts\crypto_a7v3s0_reward_sharded_aggregate.py --run-root $RewardRunRoot --runtime $RewardAggregateRuntime --report $RewardReport
if ($LASTEXITCODE -ne 0) { throw "reward aggregate failed: $LASTEXITCODE" }
"[$(Get-Date -Format o)] A7SOURCE10 flow finished" | Out-File -Append -FilePath $Log
