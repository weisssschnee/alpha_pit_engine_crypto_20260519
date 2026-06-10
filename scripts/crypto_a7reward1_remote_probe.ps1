$ErrorActionPreference = "Continue"
$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
Write-Output "== identity =="
whoami
Write-Output "== python =="
& "D:\HermesWorker\workspace\.venv\Scripts\python.exe" --version
Write-Output "== reward script =="
Get-Item "$Repo\scripts\crypto_a7reward1_portfolio_reward_model.py" | Select-Object FullName, Length, LastWriteTime
Write-Output "== launch script =="
Get-Item "$Repo\scripts\crypto_a7reward1_company_launch.ps1" | Select-Object FullName, Length, LastWriteTime
Write-Output "== queue =="
Get-Item "$Repo\runtime\a7ls30_productive_numeric_acceptance_20260610\a7ls30_selected_top240.csv" | Select-Object FullName, Length, LastWriteTime
Write-Output "== active python =="
Get-CimInstance Win32_Process -Filter "name='python.exe'" | Select-Object ProcessId, WorkingSetSize, CommandLine
