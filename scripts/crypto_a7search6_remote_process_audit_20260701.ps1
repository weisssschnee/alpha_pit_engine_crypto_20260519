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
      process_id = $_.ProcessId
      parent_process_id = $_.ParentProcessId
      working_set_mb = [math]::Round($_.WorkingSetSize / 1MB, 1)
      shard = $shard
      command_line = $cmd
    }
  }
}

$Os = Get-CimInstance Win32_OperatingSystem
$Mem = [PSCustomObject]@{
  free_gb = [math]::Round($Os.FreePhysicalMemory / 1024 / 1024, 2)
  total_gb = [math]::Round($Os.TotalVisibleMemorySize / 1024 / 1024, 2)
}

$Completed = @()
Get-ChildItem (Join-Path $RunRoot "shards") -Directory -ErrorAction SilentlyContinue | ForEach-Object {
  $manifest = Join-Path $_.FullName "proxy_runtime\a7v3s9_proxy_manifest.json"
  if (Test-Path $manifest) {
    $Completed += $_.Name
  }
}

$DuplicateShards = $Rows |
  Where-Object { $_.shard } |
  Group-Object shard |
  Where-Object { $_.Count -gt 2 } |
  ForEach-Object {
    [PSCustomObject]@{
      shard = $_.Name
      process_count = $_.Count
      process_ids = ($_.Group | ForEach-Object { $_.process_id }) -join ";"
      parent_process_ids = ($_.Group | ForEach-Object { $_.parent_process_id } | Sort-Object -Unique) -join ";"
    }
  }

$Summary = [PSCustomObject]@{
  generated_at = (Get-Date).ToString("o")
  run_root = $RunRoot
  active_process_rows = $Rows.Count
  active_shards = (($Rows | Where-Object { $_.shard } | Select-Object -ExpandProperty shard -Unique | Sort-Object) -join ",")
  duplicate_shards = (($DuplicateShards | Select-Object -ExpandProperty shard) -join ",")
  completed_manifest_count = $Completed.Count
  free_gb = $Mem.free_gb
  total_gb = $Mem.total_gb
  decision = $(if ($Rows.Count -gt 0) { "RUNNING_A7SEARCH6_PROXY_WORKERS_PRESENT" } else { "HOLD_A7SEARCH6_NO_ACTIVE_WORKERS" })
}

$Rows | Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $OutDir "a7search6_active_processes_$Stamp.csv")
$DuplicateShards | Export-Csv -NoTypeInformation -Encoding UTF8 (Join-Path $OutDir "a7search6_duplicate_shards_$Stamp.csv")
$Completed | Set-Content -Encoding UTF8 (Join-Path $OutDir "a7search6_completed_manifests_$Stamp.txt")
$Summary | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $OutDir "a7search6_process_audit_$Stamp.json")
$Summary | ConvertTo-Json -Depth 4
