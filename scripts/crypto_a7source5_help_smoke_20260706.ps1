$ErrorActionPreference = "Stop"

$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Python = "D:\Python311\python.exe"
$FlowScript = Join-Path $Repo "scripts\crypto_a7source5_a7search7_source_lag_reward_flow.py"
$Log = "D:\HermesWorker\runtime\a7source5_help_smoke_20260706.log"
Set-Location $Repo
& $Python -u $FlowScript --help *> $Log
Get-Content $Log
