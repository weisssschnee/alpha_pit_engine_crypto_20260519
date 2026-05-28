$ErrorActionPreference = 'Stop'
$root = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData'
$out = Join-Path $root 'transfer\crypto_universe500_silver_20260525'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$tar = Join-Path $out 'crypto_universe500_silver_20260525.tar'
if (Test-Path $tar) { Remove-Item -LiteralPath $tar -Force }
Push-Location $root
try {
  tar -cf $tar `
    silver/binance_vision/metrics_1h_universe500_v1 `
    silver/binance_vision/monthly_market_funding_1h_top300_v1 `
    manifests/metrics_1h_universe500_v1_20260525_aggregate_v1.csv `
    manifests/monthly_market_funding_1h_top300_v1_20260525_aggregate_v1.csv `
    reports/metrics_1h_universe500_v1_20260525_aggregate_v1.json `
    reports/monthly_market_funding_1h_top300_v1_20260525_aggregate_v1.json `
    manifests/universe300_raw_metrics_universe300_20260524.csv `
    manifests/metrics_daily_universe500_pruned_remaining_top500_remaining_top500_20260524.csv `
    manifests/universe300_vision_monthly_funding_20260524_072444.csv `
    manifests/universe300_vision_monthly_market_20260524_072444.csv `
    reports/universe300_raw_metrics_universe300_20260524.json `
    reports/metrics_daily_universe500_pruned_remaining_top500_remaining_top500_20260524.json `
    reports/universe300_vision_monthly_funding_20260524_072444.json `
    reports/universe300_vision_monthly_market_20260524_072444.json
} finally {
  Pop-Location
}
Get-Item $tar | Select-Object FullName,Length,LastWriteTime
