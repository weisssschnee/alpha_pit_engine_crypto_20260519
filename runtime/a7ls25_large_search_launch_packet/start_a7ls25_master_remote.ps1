$ErrorActionPreference = "Stop"

$Root = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls25_large_search_materialization_20260607"
$Runner = Join-Path $Root "run_a7ls25_company_materialization.ps1"
$OutLog = Join-Path $Root "a7ls25_master.out.log"
$ErrLog = Join-Path $Root "a7ls25_master.err.log"
$PidFile = Join-Path $Root "a7ls25_master_pid.txt"

if (-not (Test-Path $Runner)) {
  throw "missing runner: $Runner"
}

$p = Start-Process -FilePath "powershell.exe" `
  -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $Runner) `
  -RedirectStandardOutput $OutLog `
  -RedirectStandardError $ErrLog `
  -PassThru `
  -WindowStyle Hidden

$p.Id | Set-Content -Encoding ASCII $PidFile
[pscustomobject]@{
  pid = $p.Id
  out_log = $OutLog
  err_log = $ErrLog
  runner = $Runner
} | ConvertTo-Json -Depth 3
