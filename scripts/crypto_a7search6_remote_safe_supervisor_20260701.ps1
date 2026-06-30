$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe"
$RunRoot = "H:\AlphaFactory_CryptoData_archive\a7search6_mechanism_memory_seed_proxy_65k_20260630"
$QueueDir = Join-Path $RunRoot "queue_shards"
$ShardDir = Join-Path $RunRoot "shards"
$LockDir = Join-Path $RunRoot "safe_locks_20260701"
$AuditDir = Join-Path $RunRoot "supervisor_audit"

$TargetActiveShards = 12
$MinFreeGb = 10.0
$SleepSeconds = 45
$MaxHours = 7

New-Item -ItemType Directory -Force -Path $ShardDir, $LockDir, $AuditDir | Out-Null
$env:PYTHONPATH = $Repo
$Started = @()
$StartTime = Get-Date
$LogPath = Join-Path $AuditDir ("a7search6_safe_supervisor_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")

function Write-Log($Message) {
  $line = "[$((Get-Date).ToString('o'))] $Message"
  $line | Tee-Object -FilePath $LogPath -Append
}

function Get-FreeGb {
  $os = Get-CimInstance Win32_OperatingSystem
  return [math]::Round($os.FreePhysicalMemory / 1024 / 1024, 2)
}

function Get-ActiveShardIds {
  $ids = @()
  Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | ForEach-Object {
    $cmd = $_.CommandLine
    if ($cmd -and $cmd -like "*a7search6_mechanism_memory_seed_proxy_65k_20260630*" -and $cmd -match "a7search6_proxy_s(\d{3})") {
      $ids += [int]$Matches[1]
    }
  }
  return @($ids | Sort-Object -Unique)
}

function Has-Manifest($ShardId) {
  $name = "a7search6_proxy_s{0:D3}" -f $ShardId
  return Test-Path (Join-Path (Join-Path $ShardDir $name) "proxy_runtime\a7v3s9_proxy_manifest.json")
}

function Has-SuspectMarker($ShardId) {
  $name = "a7search6_proxy_s{0:D3}" -f $ShardId
  return Test-Path (Join-Path (Join-Path $ShardDir $name) "DUPLICATE_WORKER_SUSPECT_20260701.txt")
}

function Start-Shard($ShardId) {
  $name = "a7search6_proxy_s{0:D3}" -f $ShardId
  $lock = Join-Path $LockDir "$name.lock"
  try {
    New-Item -ItemType Directory -Path $lock -ErrorAction Stop | Out-Null
  } catch {
    return $false
  }

  $runtime = Join-Path (Join-Path $ShardDir $name) "proxy_runtime"
  $report = Join-Path (Join-Path $ShardDir $name) "CRYPTO_${name}_PROXY.md"
  $queue = Join-Path $QueueDir "$name.csv"
  New-Item -ItemType Directory -Force -Path $runtime | Out-Null
  $stdout = Join-Path (Join-Path $ShardDir $name) "safe_supervisor.out.log"
  $stderr = Join-Path (Join-Path $ShardDir $name) "safe_supervisor.err.log"

  $args = @(
    "-W", "ignore",
    "-m", "scripts.crypto_a7v3s9_prereward_oos_control_proxy",
    "--queue", $queue,
    "--runtime", $runtime,
    "--report", $report,
    "--candidate-cap", "0",
    "--successive-halving",
    "--halving-keep-rows", "128",
    "--checkpoint-every", "64",
    "--select-target", "128",
    "--pair-cap", "24",
    "--motif-cap", "64",
    "--skeleton-cap", "3"
  )
  Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $Repo -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr | Out-Null
  $Started += $name
  Write-Log "START $name"
  return $true
}

Write-Log "safe supervisor start target_active=$TargetActiveShards min_free_gb=$MinFreeGb max_hours=$MaxHours"
while (((Get-Date) - $StartTime).TotalHours -lt $MaxHours) {
  $free = Get-FreeGb
  $active = @(Get-ActiveShardIds)
  $completed = 0
  for ($i = 0; $i -lt 128; $i++) {
    if (Has-Manifest $i) { $completed += 1 }
  }
  Write-Log "STATUS active=$($active.Count) completed=$completed free_gb=$free active_ids=$($active -join ',')"

  if ($completed -ge 128) {
    Write-Log "DONE all manifests present"
    break
  }
  if ($free -lt $MinFreeGb) {
    Start-Sleep -Seconds $SleepSeconds
    continue
  }

  while ($active.Count -lt $TargetActiveShards -and $free -ge $MinFreeGb) {
    $startedOne = $false
    for ($i = 0; $i -lt 128; $i++) {
      if ($active -contains $i) { continue }
      if (Has-Manifest $i) { continue }
      if (Has-SuspectMarker $i) { continue }
      if (Start-Shard $i) {
        $active = @(Get-ActiveShardIds)
        $free = Get-FreeGb
        $startedOne = $true
        break
      }
    }
    if (-not $startedOne) { break }
  }

  Start-Sleep -Seconds $SleepSeconds
}

$summary = [PSCustomObject]@{
  generated_at = (Get-Date).ToString("o")
  run_root = $RunRoot
  started_count = $Started.Count
  started_shards = ($Started -join ",")
  free_gb = Get-FreeGb
  decision = "PASS_A7SEARCH6_SAFE_SUPERVISOR_EXIT"
}
$summary | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $AuditDir "a7search6_safe_supervisor_summary_$(Get-Date -Format yyyyMMdd_HHmmss).json")
$summary | ConvertTo-Json -Depth 4
