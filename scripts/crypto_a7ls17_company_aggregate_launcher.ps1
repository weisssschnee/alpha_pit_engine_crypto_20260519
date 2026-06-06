param(
  [string]$Repo = 'D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote',
  [string]$Python = 'D:\HermesWorker\workspace\.venv\Scripts\python.exe',
  [string]$Runtime = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls17_company_materialization_20260606_r3',
  [string]$AggRuntime = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls17_company_materialization_aggregate_20260606',
  [string]$AggReport = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\reports\CRYPTO_A7LS17_COMPANY_MATERIALIZATION_AGGREGATE_20260606.md'
)

$ErrorActionPreference = 'Stop'

if (!(Test-Path $Repo)) { throw "missing repo: $Repo" }
if (!(Test-Path $Python)) { throw "missing python: $Python" }
if (!(Test-Path $Runtime)) { throw "missing runtime: $Runtime" }

Set-Location $Repo
$env:A7LS17_RUNTIME = $Runtime
$env:A7LS17_AGG_RUNTIME = $AggRuntime
$env:A7LS17_AGG_REPORT = $AggReport
$env:A7LS17_EXPECTED_SHARDS = '100'

& $Python scripts\crypto_a7ls17_company_result_aggregate.py
if ($LASTEXITCODE -ne 0) { throw "A7LS17 aggregate failed: $LASTEXITCODE" }
