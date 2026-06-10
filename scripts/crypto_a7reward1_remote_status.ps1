$ErrorActionPreference = "Continue"
$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Runtime = "$Repo\runtime\a7reward1_portfolio_reward_model_20260610"
$External = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7reward1_portfolio_reward_model_20260610"

Write-Output "== python workers =="
Get-CimInstance Win32_Process -Filter "name='python.exe'" |
  Select-Object ProcessId, WorkingSetSize, CommandLine |
  Format-Table -AutoSize -Wrap

Write-Output "== local runtime =="
if (Test-Path $Runtime) {
  Get-ChildItem $Runtime | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
} else {
  Write-Output "missing $Runtime"
}

Write-Output "== external runtime =="
if (Test-Path $External) {
  Get-ChildItem $External | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
} else {
  Write-Output "missing $External"
}

Write-Output "== manifest =="
$Manifest = "$Runtime\a7reward1_manifest.json"
if (Test-Path $Manifest) {
  Get-Content $Manifest
} else {
  Write-Output "manifest not written"
}
