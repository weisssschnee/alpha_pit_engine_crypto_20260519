$ErrorActionPreference = "Stop"
$Run = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls21_company_deep_replay_20260607"
$Script = Join-Path $Run "run_a7ls21_company_deep_replay.ps1"
$Out = Join-Path $Run "detached.out.log"
$Err = Join-Path $Run "detached.err.log"
$PidFile = Join-Path $Run "detached_process.json"

if (-not (Test-Path $Script)) {
  throw "missing runner: $Script"
}

$p = Start-Process -WindowStyle Hidden `
  -FilePath "powershell" `
  -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $Script) `
  -RedirectStandardOutput $Out `
  -RedirectStandardError $Err `
  -PassThru

[pscustomobject]@{
  id = $p.Id
  process_name = $p.ProcessName
  start_time = $p.StartTime
  run_root = $Run
  script = $Script
} | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 $PidFile

Get-Content -Raw $PidFile
