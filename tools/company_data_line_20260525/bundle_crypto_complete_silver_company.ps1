$ErrorActionPreference='Stop'
$root='D:\HermesWorker\GDrive\AlphaFactory_CryptoData'
$out=Join-Path $root 'transfer\crypto_universe500_complete_silver_20260525'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$tar=Join-Path $out 'crypto_universe500_complete_silver_20260525.tar'
if (Test-Path $tar) { Remove-Item -LiteralPath $tar -Force }
Push-Location $root
try {
  tar -cf $tar `
    silver/binance_vision/klines_1h_universe500_v1 `
    silver/binance_vision/metrics_1h_universe500_v1 `
    silver/binance_vision/monthly_market_funding_1h_top300_v1 `
    silver/binance_vision/monthly_market_funding_1h_universe500_remaining_v1 `
    manifests/klines_1h_universe500_v1_20260525_v1.csv `
    manifests/metrics_1h_universe500_v1_20260525_aggregate_v1.csv `
    manifests/monthly_market_funding_1h_top300_v1_20260525_aggregate_v1.csv `
    manifests/monthly_market_funding_1h_universe500_remaining_v1_20260525_remaining_top500_v1.csv `
    reports/klines_1h_universe500_v1_20260525_v1.json `
    reports/metrics_1h_universe500_v1_20260525_aggregate_v1.json `
    reports/monthly_market_funding_1h_top300_v1_20260525_aggregate_v1.json `
    reports/monthly_market_funding_1h_universe500_remaining_v1_20260525_remaining_top500_v1.json
} finally { Pop-Location }
Get-Item $tar | Select-Object FullName,Length,LastWriteTime
