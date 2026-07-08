$ErrorActionPreference = "Stop"

$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Python = "D:\Python311\python.exe"
if (!(Test-Path $Python)) {
  $Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe"
}
$RunRoot = "D:\HermesWorker\runtime\a7source10_seed_expansion_proxy_20260708"
$Runner = Join-Path $Repo "scripts\crypto_a7source10_run_py_supervisor_company_20260708.ps1"

New-Item -ItemType Directory -Force -Path $RunRoot | Out-Null
"[$(Get-Date -Format o)] launch python supervisor runner=$Runner" | Out-File -FilePath (Join-Path $RunRoot "a7source10_py_supervisor_launcher.log") -Encoding UTF8

$proc = Start-Process -FilePath "powershell.exe" `
  -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $Runner) `
  -WorkingDirectory $Repo `
  -PassThru `
  -WindowStyle Hidden

"[$(Get-Date -Format o)] pid=$($proc.Id)" | Out-File -Append -FilePath (Join-Path $RunRoot "a7source10_py_supervisor_launcher.log") -Encoding UTF8
