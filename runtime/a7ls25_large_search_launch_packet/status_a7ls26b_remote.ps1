$ErrorActionPreference = "Continue"

$Root = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls26b_numeric_wave_20260608"

Write-Host "== PROCESSES =="
Get-Process python, powershell -ErrorAction SilentlyContinue |
  Select-Object ProcessName, Id, CPU, WorkingSet, StartTime |
  Sort-Object StartTime -Descending |
  Select-Object -First 20 |
  Format-Table -AutoSize

Write-Host "== QUEUE SUMMARY =="
$queueSummary = Join-Path $Root "a7ls26b_numeric_queue_summary.json"
if (Test-Path $queueSummary) { Get-Content $queueSummary -Raw } else { Write-Host "queue summary not ready" }

Write-Host "== SHARDS =="
if (Test-Path (Join-Path $Root "shards")) {
  Get-ChildItem (Join-Path $Root "shards") -Directory |
    ForEach-Object {
      $sid = $_.Name
      $manifest = Join-Path $_.FullName ("a7ls26b_" + $sid + "_manifest.json")
      $outLog = Join-Path $_.FullName "runner.out.log"
      $errLog = Join-Path $_.FullName "runner.err.log"
      [pscustomobject]@{
        shard = $sid
        manifest = Test-Path $manifest
        out_log = Test-Path $outLog
        err_log = Test-Path $errLog
        out_size = if (Test-Path $outLog) { (Get-Item $outLog).Length } else { 0 }
        err_size = if (Test-Path $errLog) { (Get-Item $errLog).Length } else { 0 }
        updated = if (Test-Path $outLog) { (Get-Item $outLog).LastWriteTime } else { $_.LastWriteTime }
      }
    } |
    Sort-Object shard |
    Format-Table -AutoSize
} else {
  Write-Host "no shards directory"
}

Write-Host "== MASTER OUT =="
$masterOut = Join-Path $Root "a7ls26b_master.out.log"
if (Test-Path $masterOut) { Get-Content $masterOut -Tail 80 } else { Write-Host "master out missing" }

Write-Host "== MASTER ERR =="
$masterErr = Join-Path $Root "a7ls26b_master.err.log"
if (Test-Path $masterErr) { Get-Content $masterErr -Tail 80 } else { Write-Host "master err missing" }

Write-Host "== ACTIVE SHARD LOG TAILS =="
if (Test-Path (Join-Path $Root "shards")) {
  Get-ChildItem (Join-Path $Root "shards") -Directory |
    Where-Object { -not (Test-Path (Join-Path $_.FullName ("a7ls26b_" + $_.Name + "_manifest.json"))) } |
    Select-Object -First 4 |
    ForEach-Object {
      Write-Host ("-- " + $_.Name + " OUT --")
      $outLog = Join-Path $_.FullName "runner.out.log"
      if (Test-Path $outLog) { Get-Content $outLog -Tail 20 } else { Write-Host "missing out" }
      Write-Host ("-- " + $_.Name + " ERR --")
      $errLog = Join-Path $_.FullName "runner.err.log"
      if (Test-Path $errLog) { Get-Content $errLog -Tail 20 } else { Write-Host "missing err" }
    }
}

Write-Host "== SUMMARY =="
$summary = Join-Path $Root "a7ls26b_numeric_wave_summary.json"
if (Test-Path $summary) { Get-Content $summary -Raw } else { Write-Host "numeric wave summary not ready" }
