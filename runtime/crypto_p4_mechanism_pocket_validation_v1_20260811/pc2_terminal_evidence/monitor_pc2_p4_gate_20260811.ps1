$ErrorActionPreference = "Stop"
$taskStatus = "D:\HermesWorker\runtime\jobs\job_20260811_010941_00029d.status.json"
$pipelineStatus = "C:\HermesWorker\runtime\crypto_p4_pocket_validation_20260811\status.json"
$oiRoot = "C:\HermesWorker\data\crypto_p4_pocket_validation_20260811\oi_mark_compact_20260801_20260809"
$aggRoot = "C:\HermesWorker\data\crypto_p4_pocket_validation_20260811\aggtrades_20260801_20260809"
$runtime = "C:\HermesWorker\workspace\crypto_p4_pocket_validation_5179bd28\runtime\crypto_p4_mechanism_pocket_validation_v1_20260811"
$task = if (Test-Path -LiteralPath $taskStatus) { Get-Content -LiteralPath $taskStatus -Raw | ConvertFrom-Json } else { $null }
$pipeline = if (Test-Path -LiteralPath $pipelineStatus) { Get-Content -LiteralPath $pipelineStatus -Raw | ConvertFrom-Json } else { $null }
$oi = if (Test-Path -LiteralPath (Join-Path $oiRoot "status.json")) { Get-Content -LiteralPath (Join-Path $oiRoot "status.json") -Raw | ConvertFrom-Json } else { $null }
$agg = if (Test-Path -LiteralPath (Join-Path $aggRoot "status.json")) { Get-Content -LiteralPath (Join-Path $aggRoot "status.json") -Raw | ConvertFrom-Json } else { $null }
$producer = if (Test-Path -LiteralPath (Join-Path $runtime "producer_status.json")) { Get-Content -LiteralPath (Join-Path $runtime "producer_status.json") -Raw | ConvertFrom-Json } else { $null }
$python = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*crypto_p4_pocket*' -or $_.CommandLine -like '*crypto_family_consensus_frozen_oi_acquire*' } | Select-Object ProcessId,ParentProcessId,CommandLine)
$os = Get-CimInstance Win32_OperatingSystem
[pscustomobject]@{
    task_state = if ($task) { $task.state } else { $null }
    task_exit_code = if ($task) { $task.exit_code } else { $null }
    pipeline_status = if ($pipeline) { $pipeline.status } else { $null }
    pipeline_phase = if ($pipeline) { $pipeline.phase } else { $null }
    pipeline_error = if ($pipeline) { $pipeline.error } else { $null }
    oi_status = if ($oi) { $oi.status } else { $null }
    oi_completed_days = if ($oi) { $oi.completed_days } else { $null }
    oi_total_days = if ($oi) { $oi.total_days } else { $null }
    oi_failure_count = if ($oi) { $oi.failure_count } else { $null }
    agg_status = if ($agg) { $agg.status } else { $null }
    agg_completed_symbols = if ($agg) { $agg.completed_symbols } else { $null }
    agg_failure_count = if ($agg) { $agg.failure_count } else { $null }
    producer_status = if ($producer) { $producer.status } else { $null }
    strict_evaluated_count = if ($producer) { $producer.strict_evaluated_count } else { $null }
    python_processes = $python
    c_free_gib = [math]::Round((Get-PSDrive C).Free / 1GB, 2)
    memory_free_gib = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
} | ConvertTo-Json -Depth 5 -Compress
