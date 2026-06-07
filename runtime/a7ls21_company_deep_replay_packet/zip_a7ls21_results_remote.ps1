$ErrorActionPreference = "Stop"

$Root = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls21_company_deep_replay_20260607"
$Zip = Join-Path $Root "a7ls21_results.zip"

if (Test-Path $Zip) {
  Remove-Item $Zip -Force
}

$Paths = @(
  (Join-Path $Root "shards"),
  (Join-Path $Root "a7ls21_remaining_summary.json")
)

Compress-Archive -Path $Paths -DestinationPath $Zip -Force
Get-Item $Zip | Select-Object FullName, Length, LastWriteTime | ConvertTo-Json -Depth 3
