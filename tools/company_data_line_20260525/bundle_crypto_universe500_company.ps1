$ErrorActionPreference = 'Stop'
$root = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData'
$out = Join-Path $root 'transfer\crypto_universe500_20260525'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$items = @(
  @{name='metadata_universe'; paths=@('metadata/universe')},
  @{name='manifests_reports'; paths=@(
    'manifests/universe300_raw_metrics_universe300_20260524.csv',
    'manifests/universe300_vision_monthly_funding_20260524_072444.csv',
    'manifests/universe300_vision_monthly_market_20260524_072444.csv',
    'manifests/metrics_daily_universe500_pruned_remaining_top500_remaining_top500_20260524.csv',
    'manifests/metrics_daily_universe500_pruned_remaining_top500_remaining_top500_20260524_plan.csv',
    'manifests/metrics_daily_universe500_pruned_remaining_top500_remaining_top500_20260524_invalid_symbols.json',
    'reports/universe300_raw_metrics_universe300_20260524.json',
    'reports/universe300_vision_monthly_funding_20260524_072444.json',
    'reports/universe300_vision_monthly_market_universe300_20260524.json',
    'reports/universe300_vision_monthly_market_20260524_072444.json',
    'reports/metrics_daily_universe500_pruned_remaining_top500_remaining_top500_20260524.json'
  )},
  @{name='raw_metrics_top300'; paths=@('raw/binance_vision/metrics_daily_universe300')},
  @{name='raw_metrics_remaining_top500'; paths=@('raw/binance_vision/metrics_daily_universe500_pruned_remaining_top500')},
  @{name='raw_monthly_funding_market_top300'; paths=@(
    'raw/binance_vision/fundingRate_monthly_universe300',
    'raw/binance_vision/markPriceKlines_monthly_universe300',
    'raw/binance_vision/indexPriceKlines_monthly_universe300',
    'raw/binance_vision/premiumIndexKlines_monthly_universe300'
  )}
)
foreach ($item in $items) {
  $tar = Join-Path $out ($item.name + '.tar')
  if (Test-Path $tar) { Remove-Item -LiteralPath $tar -Force }
  Push-Location $root
  try {
    tar -cf $tar @($item.paths)
  } finally {
    Pop-Location
  }
  $f = Get-Item $tar
  [pscustomobject]@{tar=$tar; gb=[math]::Round($f.Length/1GB,3); bytes=$f.Length}
}
