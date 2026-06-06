param(
  [string]$Repo = 'D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote',
  [string]$Python = 'D:\HermesWorker\workspace\.venv\Scripts\python.exe',
  [string]$External = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls18_company_numeric_20260606_r2',
  [string]$Report = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\reports\CRYPTO_A7LS18_COMPANY_NUMERIC_AGGREGATE_20260606.md'
)

$ErrorActionPreference = 'Stop'

if (!(Test-Path $Repo)) { throw "missing repo: $Repo" }
if (!(Test-Path $Python)) { throw "missing python: $Python" }
if (!(Test-Path $External)) { throw "missing external: $External" }

Set-Location $Repo
$env:A7LS18_EXTERNAL = $External
$env:A7LS18_REPORT = $Report
& $Python scripts\crypto_a7ls18_company_result_aggregate.py
exit $LASTEXITCODE
