$ErrorActionPreference = "Stop"

$Root = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls26c_raw_diverse_numeric_wave_20260608"
$Script = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls25_large_search_materialization_20260607\run_a7ls26c_raw_diverse_numeric_wave_remote.ps1"
$OutLog = Join-Path $Root "a7ls26c_master.out.log"
$ErrLog = Join-Path $Root "a7ls26c_master.err.log"
$PidFile = Join-Path $Root "a7ls26c_master_pid.txt"

New-Item -ItemType Directory -Force -Path $Root | Out-Null
if (-not (Test-Path $Script)) { throw "missing script: $Script" }

$p = Start-Process -FilePath "powershell.exe" `
  -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $Script) `
  -RedirectStandardOutput $OutLog `
  -RedirectStandardError $ErrLog `
  -PassThru `
  -WindowStyle Hidden

$p.Id | Set-Content -Encoding ASCII $PidFile
[pscustomobject]@{ pid=$p.Id; out_log=$OutLog; err_log=$ErrLog; script=$Script } | ConvertTo-Json -Depth 3
