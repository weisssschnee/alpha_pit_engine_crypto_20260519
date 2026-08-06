$ErrorActionPreference = 'Stop'
$log = 'D:\HermesWorker\runtime\jobs\job_20260806_140152_2eabe8.log'
$stdout = 'D:\HermesWorker\runtime\jobs\job_20260806_140152_2eabe8.stdout.log'
$stderr = 'D:\HermesWorker\runtime\jobs\job_20260806_140152_2eabe8.stderr.log'
$status = 'D:\HermesWorker\runtime\jobs\job_20260806_140152_2eabe8.status.json'
$startLock = 'D:\HermesWorker\runtime\jobs\job_20260806_140152_2eabe8.start.lock'
function Write-AtomicStatus([hashtable]$payload) {
  $temporary = "$status.tmp-$PID"
  $payload | ConvertTo-Json -Depth 4 | Set-Content -Path $temporary -Encoding UTF8
  Move-Item -LiteralPath $temporary -Destination $status -Force
}
try {
  $lockStream = [System.IO.File]::Open(
    $startLock,
    [System.IO.FileMode]::CreateNew,
    [System.IO.FileAccess]::Write,
    [System.IO.FileShare]::None
  )
  $lockWriter = [System.IO.StreamWriter]::new($lockStream)
  $lockWriter.WriteLine("launcher_pid=$PID")
  $lockWriter.Dispose()
} catch [System.IO.IOException] {
  "DUPLICATE_START_BLOCKED $((Get-Date).ToString('s')) launcher_pid=$PID" |
    Out-File -FilePath $log -Append -Encoding utf8
  exit 0
}
$start = Get-Date
"BEGIN $($start.ToString('s'))" | Out-File -FilePath $log -Append -Encoding utf8
$exitCode = 0
$childPid = $null
try {
  $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
  $startInfo.FileName = 'cmd.exe'
  $startInfo.Arguments = "/d /s /c powershell.exe -NoProfile -ExecutionPolicy Bypass -EncodedCommand cABvAHcAZQByAHMAaABlAGwAbAAuAGUAeABlACAALQBOAG8AUAByAG8AZgBpAGwAZQAgAC0ARQB4AGUAYwB1AHQAaQBvAG4AUABvAGwAaQBjAHkAIABCAHkAcABhAHMAcwAgAC0ARgBpAGwAZQAgAEMAOgBcAEgAZQByAG0AZQBzAFcAbwByAGsAZQByAFwAdwBvAHIAawBzAHAAYQBjAGUAXABjAHIAeQBwAHQAbwBfAHIAZQBwAGwAaQBjAGEAdABpAG8AbgBfAGcAYQB0AGUAXwByADIAXwBjADgAZABkAGYAZQBkADgAXABzAGMAcgBpAHAAdABzAFwAYwByAHkAcAB0AG8AXwByAGUAcABsAGkAYwBhAHQAaQBvAG4AXwBhAHcAYQByAGUAXwBnAGEAdABlAF8AdgAxAF8AcABjADIAXwBsAGEAdQBuAGMAaABlAHIALgBwAHMAMQAgAC0AUgBlAHAAbwBSAG8AbwB0ACAAQwA6AFwASABlAHIAbQBlAHMAVwBvAHIAawBlAHIAXAB3AG8AcgBrAHMAcABhAGMAZQBcAGMAcgB5AHAAdABvAF8AcgBlAHAAbABpAGMAYQB0AGkAbwBuAF8AZwBhAHQAZQBfAHIAMgBfAGMAOABkAGQAZgBlAGQAOAAgAC0AUAB5AHQAaABvAG4AIABEADoAXABIAGUAcgBtAGUAcwBXAG8AcgBrAGUAcgBcAHAAeQB0AGgAbwBuADMAMQAxAFwAcAB5AHQAaABvAG4ALgBlAHgAZQAgAC0AUAB5AHQAaABvAG4ATwB2AGUAcgBsAGEAeQAgAEQAOgBcAEgAZQByAG0AZQBzAFcAbwByAGsAZQByAFwAcgB1AG4AdABpAG0AZQBcAGMAcgB5AHAAdABvAF8AcwBlAGEAcgBjAGgAXwBwAHkAMwAxADEAXwBvAHYAZQByAGwAYQB5AF8AOQA0AGIAMAAxADYAZgBhAFwAcwBpAHQAZQAtAHAAYQBjAGsAYQBnAGUAcwAgAC0AQgBhAHMAZQBXAG8AcgBrAHMAcABhAGMAZQAgAEMAOgBcAEgAZQByAG0AZQBzAFcAbwByAGsAZQByAFwAdwBvAHIAawBzAHAAYQBjAGUAXABjAHIAeQBwAHQAbwBfAHMAZQBhAHIAYwBoAF8AZQB2AGkAZABlAG4AYwBlAF8AdgAxAF8AMQBfADYANwA3ADAAMQBiAGEANwAgAC0AUAByAG8AZAB1AGMAZQByAFMAbwB1AHIAYwBlAFMAaABhACAAYwA4AGQAZABmAGUAZAA4ADQAZQBkADAANgAxADAAMQBjAGQANgA5AGIAMwBhAGUANQBkADYAYgA2ADMANAA1ADEAZQA1AGIAZQA2ADkAOAAgAC0AUgB1AG4AdABpAG0AZQBEAGEAdABlACAAMgAwADIANgAwADgAMAA2AHIAMgAgAC0AUgBlAGMAZQBpAHAAdABSAGUAbABhAHQAaQB2AGUAUABhAHQAaAAgAGMAbwBuAGYAaQBnAC8AYwByAHkAcAB0AG8AXwBzAGUAYQByAGMAaABfAHIAZQBwAGwAaQBjAGEAdABpAG8AbgBfAGEAdwBhAHIAZQBfAGcAYQB0AGUAXwB2ADEAXwByADIAXwByAGUAYwBlAGkAcAB0AC4AagBzAG8AbgAgAC0AUgBlAGMAZQBpAHAAdABCAGwAbwBiAFMAaABhADEAIAAzADkAZgA2AGIAYgA1ADgANgAzAGIAYgA3ADQAMABjADIANwBmAGQAZgBlAGQAZQBiADEAYgBmAGQAOQAxADAAMgA2ADEAMgA0ADMAYwBkACAALQBSAGUAcwBvAGwAdgBlAGQAUgBlAGMAZQBpAHAAdABTAGgAYQAyADUANgAgADIAOABGAEMAQwBBADMANAA3AEEAMwA4ADAAQQA2ADMANgA4ADYARgA1ADYARgAwADkAOAA0AEYAMwBDADkAOQBFADIAQwBFAEIAMABDAEUARAAzADcANgAwADYAQQAzADMAQwA2AEQAMABGADkAOQAyAEUARABBADkARQA3ADcAIAAtAEwAbwBnAFIAbwBvAHQAIABDADoAXABIAGUAcgBtAGUAcwBXAG8AcgBrAGUAcgBcAHIAdQBuAHQAaQBtAGUAXABjAHIAeQBwAHQAbwBfAHIAZQBwAGwAaQBjAGEAdABpAG8AbgBfAGcAYQB0AGUAXwByADIAXwBjADgAZABkAGYAZQBkADgA 1>$stdout 2>$stderr"
  $startInfo.UseShellExecute = $false
  $startInfo.CreateNoWindow = $true
  $process = [System.Diagnostics.Process]::new()
  $process.StartInfo = $startInfo
  [void]$process.Start()
  $childPid = $process.Id
  Write-AtomicStatus @{
    schema_version = 2
    state = 'RUNNING'
    task_id = 'job_20260806_140152_2eabe8'
    task_name = 'HermesRemote_job_20260806_140152_2eabe8'
    launcher_pid = $PID
    child_pid = $childPid
    started_at = $start.ToString('s')
    ended_at = $null
    exit_code = $null
    log = 'D:\HermesWorker\runtime\jobs\job_20260806_140152_2eabe8.log'
    stdout_log = 'D:\HermesWorker\runtime\jobs\job_20260806_140152_2eabe8.stdout.log'
    stderr_log = 'D:\HermesWorker\runtime\jobs\job_20260806_140152_2eabe8.stderr.log'
    start_lock = 'D:\HermesWorker\runtime\jobs\job_20260806_140152_2eabe8.start.lock'
  }
  "CHILD_PID $childPid" | Out-File -FilePath $log -Append -Encoding utf8
  $process.WaitForExit()
  $process.Refresh()
  $exitCode = [int]$process.ExitCode
} catch {
  $exitCode = 1
  "EXCEPTION: $($_.Exception.Message)" | Out-File -FilePath $log -Append -Encoding utf8
}
$end = Get-Date
$terminalState = if ($exitCode -eq 0) { 'COMPLETED' } else { 'FAILED' }
Write-AtomicStatus @{
  schema_version = 2
  state = $terminalState
  task_id = 'job_20260806_140152_2eabe8'
  task_name = 'HermesRemote_job_20260806_140152_2eabe8'
  launcher_pid = $PID
  child_pid = $childPid
  started_at = $start.ToString('s')
  ended_at = $end.ToString('s')
  exit_code = $exitCode
  log = 'D:\HermesWorker\runtime\jobs\job_20260806_140152_2eabe8.log'
  stdout_log = 'D:\HermesWorker\runtime\jobs\job_20260806_140152_2eabe8.stdout.log'
  stderr_log = 'D:\HermesWorker\runtime\jobs\job_20260806_140152_2eabe8.stderr.log'
  start_lock = 'D:\HermesWorker\runtime\jobs\job_20260806_140152_2eabe8.start.lock'
}
if ($exitCode -eq 0) {
  "END OK $($end.ToString('s'))" | Out-File -FilePath $log -Append -Encoding utf8
} else {
  "END FAIL $($end.ToString('s')) code=$exitCode" | Out-File -FilePath $log -Append -Encoding utf8
}
exit $exitCode
