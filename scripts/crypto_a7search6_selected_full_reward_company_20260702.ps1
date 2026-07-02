$ErrorActionPreference = "Stop"

$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe"

$SelectedQueue = "D:\HermesWorker\runtime\a7search6_selected_aggregate_20260702\a7search6_proxy_selected_for_reward.csv"
$CleanRoot = "D:\HermesWorker\runtime\a7search6_selected_full_reward_clean_20260702"
$CleanQueue = Join-Path $CleanRoot "a7search6_selected_for_reward_clean.csv"
$SuspectQueue = Join-Path $CleanRoot "a7search6_selected_for_reward_suspect_excluded.csv"

$RewardRunRoot = "D:\HermesWorker\runtime\a7search6_selected_full_reward_r1_20260702"
$RewardAggregateRuntime = Join-Path $Repo "runtime\a7search6_selected_full_reward_r1_aggregate_20260702"
$RewardReport = Join-Path $Repo "reports\CRYPTO_A7SEARCH6_SELECTED_FULL_REWARD_R1_AGGREGATE_20260702.md"
$Log = Join-Path $RewardRunRoot "a7search6_selected_full_reward_r1.log"
$StatusPath = Join-Path $RewardRunRoot "a7search6_reward_status.csv"

$RowsPerShard = 16
$MaxParallel = 8
if ($env:A7SEARCH6_REWARD_MAX_PARALLEL) {
  $MaxParallel = [int]$env:A7SEARCH6_REWARD_MAX_PARALLEL
}
$ManifestWaitSeconds = 1800
$SuspectShardIds = @("a7search6_proxy_s019", "a7search6_proxy_s020", "a7search6_proxy_s022")

New-Item -ItemType Directory -Force -Path $CleanRoot, $RewardRunRoot, $RewardAggregateRuntime | Out-Null
Set-Location $Repo

$env:PYTHONWARNINGS = "ignore"
$env:NUMEXPR_MAX_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"

function Write-Log {
  param([string]$Message)
  "[$(Get-Date -Format o)] $Message" | Out-File -Append -FilePath $Log -Encoding UTF8
}

function Write-Json {
  param([string]$Path, [object]$Payload)
  $Payload | ConvertTo-Json -Depth 8 | Out-File -FilePath $Path -Encoding UTF8
}

if (!(Test-Path $SelectedQueue)) {
  throw "missing selected queue: $SelectedQueue"
}

Write-Log "A7SEARCH6 selected full reward start"
Write-Log "repo=$Repo"
Write-Log "selected_queue=$SelectedQueue"
Write-Log "reward_run_root=$RewardRunRoot"
Write-Log "max_parallel=$MaxParallel rows_per_shard=$RowsPerShard"

$Rows = @(Import-Csv $SelectedQueue)
if ($Rows.Count -eq 0) {
  throw "selected queue is empty: $SelectedQueue"
}

$HasShardColumn = $Rows[0].PSObject.Properties.Name -contains "proxy_shard_id"
if ($HasShardColumn) {
  $CleanRows = @($Rows | Where-Object { $SuspectShardIds -notcontains $_.proxy_shard_id })
  $SuspectRows = @($Rows | Where-Object { $SuspectShardIds -contains $_.proxy_shard_id })
} else {
  $CleanRows = $Rows
  $SuspectRows = @()
}

if ($CleanRows.Count -eq 0) {
  throw "suspect filtering removed all selected rows"
}

$CleanRows | Export-Csv -NoTypeInformation -Path $CleanQueue
if ($SuspectRows.Count -gt 0) {
  $SuspectRows | Export-Csv -NoTypeInformation -Path $SuspectQueue
}

$filterManifest = [ordered]@{
  stage = "A7SEARCH6-SELECTED-FULL-REWARD-CLEAN-FILTER"
  generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  decision = "PASS_A7SEARCH6_SELECTED_REWARD_QUEUE_CLEAN_READY"
  selected_queue = $SelectedQueue
  clean_queue = $CleanQueue
  suspect_queue = $SuspectQueue
  input_rows = [int]$Rows.Count
  clean_rows = [int]$CleanRows.Count
  suspect_excluded_rows = [int]$SuspectRows.Count
  suspect_shard_ids = $SuspectShardIds
  has_proxy_shard_id = [bool]$HasShardColumn
  authorizes_bounded_full_reward = $true
  authorizes_alpha_proof = $false
  authorizes_shadow_paper_live = $false
}
Write-Json -Path (Join-Path $CleanRoot "a7search6_selected_reward_clean_manifest.json") -Payload $filterManifest
Write-Log "clean_rows=$($CleanRows.Count) suspect_excluded_rows=$($SuspectRows.Count)"

$env:A7V3S0_REWARD_PREQUEUE = $CleanQueue
$env:A7V3S0_REWARD_SHARD_RUNTIME = $RewardRunRoot
$env:A7V3S0_REWARD_ROWS_PER_SHARD = "$RowsPerShard"

& $Python scripts\crypto_a7v3s0_reward_shard_queue.py *> (Join-Path $RewardRunRoot "reward_shard_queue.log")
if ($LASTEXITCODE -ne 0) {
  throw "reward shard queue failed: $LASTEXITCODE"
}

$RewardPlan = @(Import-Csv (Join-Path $RewardRunRoot "a7v3s0_reward_shard_plan.csv"))
Write-Log "reward_shard_count=$($RewardPlan.Count)"

$statusRows = New-Object System.Collections.Generic.List[object]
for ($start = 0; $start -lt $RewardPlan.Count; $start += $MaxParallel) {
  $end = [Math]::Min($start + $MaxParallel, $RewardPlan.Count)
  $procs = @()
  for ($i = $start; $i -lt $end; $i++) {
    $row = $RewardPlan[$i]
    $sid = $row.shard_id
    $shardRoot = Join-Path $RewardRunRoot ("shards\" + $sid)
    $runtime = Join-Path $shardRoot "reward_runtime"
    $report = Join-Path $shardRoot ("CRYPTO_" + $sid + "_A7SEARCH6_FULL_REWARD.md")
    $out = Join-Path $shardRoot "reward.out.log"
    $err = Join-Path $shardRoot "reward.err.log"
    $manifest = Join-Path $runtime "a7reward1_manifest.json"
    New-Item -ItemType Directory -Force -Path $runtime, $shardRoot | Out-Null
    if (Test-Path $manifest) {
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
      "--runtime", $runtime,
      "--report", $report
    )
    Write-Log "START reward $sid"
    $proc = Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $Repo -RedirectStandardOutput $out -RedirectStandardError $err -PassThru -WindowStyle Hidden
    $procs += [pscustomobject]@{ process=$proc; shard_id=$sid; queue_path=$row.queue_path; started_at=(Get-Date -Format o); manifest=$manifest }
  }
  foreach ($entry in $procs) {
    Wait-Process -Id $entry.process.Id
    $entry.process.Refresh()
    $exit = $entry.process.ExitCode
    $waitStart = Get-Date
    while (!(Test-Path $entry.manifest) -and (((Get-Date) - $waitStart).TotalSeconds -lt $ManifestWaitSeconds)) {
      Start-Sleep -Seconds 10
    }
    $status = if (Test-Path $entry.manifest) { "done" } else { "failed" }
    $statusRows.Add([pscustomobject]@{ shard_id=$entry.shard_id; status=$status; exit_code=$exit; started_at=$entry.started_at; ended_at=(Get-Date -Format o); queue_path=$entry.queue_path })
    Write-Log "END reward $($entry.shard_id) status=$status exit=$exit"
    $statusRows | Export-Csv -NoTypeInformation -Path $StatusPath
    if (!(Test-Path $entry.manifest)) {
      throw "reward shard missing manifest $($entry.shard_id) exit=$exit manifest=$($entry.manifest)"
    }
  }
  $statusRows | Export-Csv -NoTypeInformation -Path $StatusPath
}

& $Python scripts\crypto_a7v3s0_reward_sharded_aggregate.py --run-root $RewardRunRoot --runtime $RewardAggregateRuntime --report $RewardReport *> (Join-Path $RewardRunRoot "reward_aggregate.log")
if ($LASTEXITCODE -ne 0) {
  throw "reward aggregate failed: $LASTEXITCODE"
}

Write-Log "A7SEARCH6 selected full reward finished"
