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

New-Item -ItemType Directory -Force -Path $RunRoot | Out-Null
"[$(Get-Date -Format o)] launch python supervisor python=$Python script=$Script" | Out-File -FilePath (Join-Path $RunRoot "a7source10_py_supervisor_launcher.log") -Encoding UTF8

$proc = Start-Process -FilePath $Python `
  -ArgumentList @($Script) `
  -WorkingDirectory $Repo `
  -RedirectStandardOutput $Out `
  -RedirectStandardError $Err `
  -PassThru `
  -WindowStyle Hidden

"[$(Get-Date -Format o)] pid=$($proc.Id)" | Out-File -Append -FilePath (Join-Path $RunRoot "a7source10_py_supervisor_launcher.log") -Encoding UTF8
