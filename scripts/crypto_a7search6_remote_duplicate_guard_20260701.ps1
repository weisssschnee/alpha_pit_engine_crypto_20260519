$RunRoot = "H:\AlphaFactory_CryptoData_archive\a7search6_mechanism_memory_seed_proxy_65k_20260630"
$OutDir = Join-Path $RunRoot "supervisor_audit"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"

$Rows = @()
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | ForEach-Object {
  $cmd = $_.CommandLine
  if ($cmd -and $cmd -like "*a7search6_mechanism_memory_seed_proxy_65k_20260630*") {
    $shard = ""
    if ($cmd -match "a7search6_proxy_s(\d{3})") {
      $shard = "s$($Matches[1])"
    }
    $Rows += [PSCustomObject]@{
      process_id = [int]$_.ProcessId
      parent_process_id = [int]$_.ParentProcessId
      working_set = [int64]$_.WorkingSetSize
      working_set_mb = [math]::Round($_.WorkingSetSize / 1MB, 1)
      shard = $shard
      command_line = $cmd
    }
  }
}

$WrapperRows = $Rows | Where-Object { $_.command_line -like "*workspace\.venv\Scripts\python.exe*" }
$ChildRows = $Rows | Where-Object { $_.command_line -like "*D:\Python311\python.exe*" }

$Pairs = @()
foreach ($wrapper in $WrapperRows) {
  $child = $ChildRows | Where-Object { $_.parent_process_id -eq $wrapper.process_id } | Select-Object -First 1
  $Pairs += [PSCustomObject]@{
    shard = $wrapper.shard
    supervisor_pid = $wrapper.parent_process_id
    wrapper_pid = $wrapper.process_id
    child_pid = $(if ($child) { [int]$child.process_id } else { 0 })
    child_working_set = $(if ($child) { [int64]$child.working_set } else { 0 })
    child_working_set_mb = $(if ($child) { [math]::Round($child.working_set / 1MB, 1) } else { 0 })
  }
}

$DuplicateGroups = $Pairs |
  Where-Object { $_.shard } |
  Group-Object shard |
  Where-Object { $_.Count -gt 1 }

$UniqueGroups = $Pairs |
  Where-Object { $_.shard } |
  Group-Object shard |
  Where-Object { $_.Count -eq 1 }

$ParentScores = @{}
foreach ($group in $UniqueGroups) {
  $supervisorPidKey = [string]$group.Group[0].supervisor_pid
  if (-not $ParentScores.ContainsKey($supervisorPidKey)) { $ParentScores[$supervisorPidKey] = 0 }
  $ParentScores[$supervisorPidKey] += 1
}
$PreserveSupervisor = $null
if ($ParentScores.Count -gt 0) {
  $PreserveSupervisor = ($ParentScores.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Key
}

$Killed = @()
$Suspect = @()
foreach ($group in $DuplicateGroups) {
  $keep = $group.Group | Sort-Object child_working_set -Descending | Select-Object -First 1
  foreach ($pair in $group.Group) {
    if ($pair.wrapper_pid -ne $keep.wrapper_pid) {
      foreach ($processIdToStop in @($pair.child_pid, $pair.wrapper_pid)) {
        if ($processIdToStop -gt 0) {
          Stop-Process -Id $processIdToStop -Force -ErrorAction SilentlyContinue
        }
      }
      $Killed += [PSCustomObject]@{
        shard = $pair.shard
        killed_wrapper_pid = $pair.wrapper_pid
        killed_child_pid = $pair.child_pid
        kept_wrapper_pid = $keep.wrapper_pid
        kept_child_pid = $keep.child_pid
        reason = "duplicate_shard_pair"
      }
    }
  }
  $ShardDir = Join-Path (Join-Path $RunRoot "shards") "a7search6_proxy_$($group.Name)"
  New-Item -ItemType Directory -Force -Path $ShardDir | Out-Null
  "duplicate worker detected and trimmed at $((Get-Date).ToString('o'))" |
    Set-Content -Encoding UTF8 (Join-Path $ShardDir "DUPLICATE_WORKER_SUSPECT_20260701.txt")
  $Suspect += $group.Name
}

$StoppedSupervisors = @()
$DuplicateSupervisorPids = $DuplicateGroups.Group |
  Select-Object -ExpandProperty supervisor_pid -Unique |
  Where-Object { $_ -and ([string]$_) -ne ([string]$PreserveSupervisor) }
foreach ($supervisorProcessId in $DuplicateSupervisorPids) {
  Stop-Process -Id $supervisorProcessId -Force -ErrorAction SilentlyContinue
  $StoppedSupervisors += [int]$supervisorProcessId
}

Start-Sleep -Seconds 2

$RemainingRows = @()
Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" | ForEach-Object {
  $cmd = $_.CommandLine
  if ($cmd -and $cmd -like "*a7search6_mechanism_memory_seed_proxy_65k_20260630*") {
    $shard = ""
    if ($cmd -match "a7search6_proxy_s(\d{3})") {
      $shard = "s$($Matches[1])"
    }
    $RemainingRows += [PSCustomObject]@{
      process_id = [int]$_.ProcessId
      parent_process_id = [int]$_.ParentProcessId
      shard = $shard
      command_line = $cmd
    }
  }
}

$RemainingDuplicateShards = $RemainingRows |
  Where-Object { $_.shard } |
  Group-Object shard |
  Where-Object { $_.Count -gt 2 } |
  Select-Object -ExpandProperty Name

$Os = Get-CimInstance Win32_OperatingSystem
$Summary = [PSCustomObject]@{
  generated_at = (Get-Date).ToString("o")
  run_root = $RunRoot
  preserve_supervisor_pid = $PreserveSupervisor
  stopped_supervisor_pids = ($StoppedSupervisors -join ",")
  killed_worker_pairs = $Killed.Count
  suspect_shards = ($Suspect -join ",")
  remaining_active_process_rows = $RemainingRows.Count
  remaining_duplicate_shards = ($RemainingDuplicateShards -join ",")
  free_gb = [math]::Round($Os.FreePhysicalMemory / 1024 / 1024, 2)
  decision = $(if ($RemainingDuplicateShards.Count -eq 0) { "PASS_A7SEARCH6_DUPLICATE_WORKERS_TRIMMED" } else { "HOLD_A7SEARCH6_DUPLICATE_WORKERS_REMAIN" })
}

$Killed | Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $OutDir "a7search6_duplicate_guard_killed_$Stamp.csv")
$Summary | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $OutDir "a7search6_duplicate_guard_summary_$Stamp.json")
$Summary | ConvertTo-Json -Depth 4
