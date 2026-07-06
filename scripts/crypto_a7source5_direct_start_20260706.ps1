$ErrorActionPreference = "Stop"

$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Python = "D:\Python311\python.exe"
$RunRoot = "D:\HermesWorker\runtime\a7source5_a7search7_source_lag_retest_py_20260706"
$RewardRunRoot = "D:\HermesWorker\runtime\a7search7_strict_validation_reward_source5_py_20260706"
$Out = Join-Path $RunRoot "direct_launcher.out.log"
$Err = Join-Path $RunRoot "direct_launcher.err.log"
$Status = Join-Path $RunRoot "direct_launcher_status.json"

New-Item -ItemType Directory -Force -Path $RunRoot, $RewardRunRoot | Out-Null
Set-Location $Repo

$env:PYTHONWARNINGS = "ignore"
$env:NUMEXPR_MAX_THREADS = "1"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"

$FlowScript = Join-Path $Repo "scripts\crypto_a7source5_a7search7_source_lag_reward_flow.py"
$Child = Join-Path $RunRoot "direct_child_run.ps1"
@"
`$ErrorActionPreference = "Stop"
Set-Location "$Repo"
`$env:PYTHONWARNINGS = "ignore"
`$env:NUMEXPR_MAX_THREADS = "1"
`$env:OMP_NUM_THREADS = "1"
`$env:MKL_NUM_THREADS = "1"
& "$Python" -u "$FlowScript" --python "$Python" --max-parallel 8 --rows-per-shard 16
"@ | Out-File -FilePath $Child -Encoding UTF8

$CommandLine = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$Child`" 1> `"$Out`" 2> `"$Err`""
$created = ([wmiclass]"Win32_Process").Create($CommandLine, $Repo, $null)
if ($created.ReturnValue -ne 0) {
  throw "Win32_Process.Create failed: $($created.ReturnValue)"
}
@{
  stage = "A7SOURCE5_DIRECT_START"
  started_at = (Get-Date -Format o)
  pid = $created.ProcessId
  repo = $Repo
  python = $Python
  run_root = $RunRoot
  reward_run_root = $RewardRunRoot
  out = $Out
  err = $Err
} | ConvertTo-Json -Depth 4 | Out-File -FilePath $Status -Encoding UTF8

Write-Output "A7SOURCE5_DIRECT_STARTED pid=$($created.ProcessId) status=$Status"
