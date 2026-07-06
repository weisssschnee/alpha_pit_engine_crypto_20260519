$ErrorActionPreference = "Stop"

$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$RunRoot = "D:\HermesWorker\runtime\a7source6_incremental_validation_reward_20260706"
$Runner = Join-Path $Repo "scripts\crypto_a7source6_incremental_validation_company_20260706.ps1"
$Out = Join-Path $RunRoot "direct_launcher.out.log"
$Err = Join-Path $RunRoot "direct_launcher.err.log"
$Status = Join-Path $RunRoot "direct_launcher_status.json"

New-Item -ItemType Directory -Force -Path $RunRoot | Out-Null
Set-Location $Repo

$Child = Join-Path $RunRoot "direct_child_run.ps1"
@"
`$ErrorActionPreference = "Stop"
Set-Location "$Repo"
`$env:PYTHONWARNINGS = "ignore"
`$env:NUMEXPR_MAX_THREADS = "1"
`$env:OMP_NUM_THREADS = "1"
`$env:MKL_NUM_THREADS = "1"
`$env:A7SOURCE6_MAX_PARALLEL = "8"
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$Runner"
"@ | Out-File -FilePath $Child -Encoding UTF8

$CommandLine = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$Child`" 1> `"$Out`" 2> `"$Err`""
$created = ([wmiclass]"Win32_Process").Create($CommandLine, $Repo, $null)
if ($created.ReturnValue -ne 0) {
  throw "Win32_Process.Create failed: $($created.ReturnValue)"
}
@{
  stage = "A7SOURCE6_DIRECT_START"
  started_at = (Get-Date -Format o)
  pid = $created.ProcessId
  repo = $Repo
  run_root = $RunRoot
  runner = $Runner
  out = $Out
  err = $Err
} | ConvertTo-Json -Depth 4 | Out-File -FilePath $Status -Encoding UTF8

Write-Output "A7SOURCE6_DIRECT_STARTED pid=$($created.ProcessId) status=$Status"
