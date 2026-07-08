$ErrorActionPreference = "Stop"

$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Python = "D:\Python311\python.exe"
if (!(Test-Path $Python)) {
  $Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe"
}
$RunRoot = "D:\HermesWorker\runtime\a7source10_seed_expansion_proxy_20260708"
$Script = Join-Path $Repo "scripts\crypto_a7source10_proxy_reward_flow_company_py_20260708.py"
$Out = Join-Path $RunRoot "a7source10_py_supervisor.out.log"
$Err = Join-Path $RunRoot "a7source10_py_supervisor.err.log"
$RunnerLog = Join-Path $RunRoot "a7source10_py_supervisor_runner.log"

New-Item -ItemType Directory -Force -Path $RunRoot | Out-Null
Set-Location $Repo

if (!$env:A7SOURCE10_MAX_PARALLEL) {
  $env:A7SOURCE10_MAX_PARALLEL = "8"
}

"[$(Get-Date -Format o)] runner start python=$Python script=$Script max_parallel=$env:A7SOURCE10_MAX_PARALLEL" | Out-File -FilePath $RunnerLog -Encoding UTF8
& $Python -u $Script > $Out 2> $Err
$ExitCode = $LASTEXITCODE
"[$(Get-Date -Format o)] runner exit=$ExitCode" | Out-File -Append -FilePath $RunnerLog -Encoding UTF8
exit $ExitCode
