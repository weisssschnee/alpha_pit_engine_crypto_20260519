$ErrorActionPreference = 'Continue'
$root = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData'
$names = @(
  'metrics_daily_universe300',
  'metrics_daily_universe500_pruned_remaining_top500',
  'fundingRate_monthly_universe300',
  'markPriceKlines_monthly_universe300',
  'indexPriceKlines_monthly_universe300',
  'premiumIndexKlines_monthly_universe300'
)
foreach ($name in $names) {
  $path = Join-Path $root ("raw\binance_vision\$name")
  if (Test-Path $path) {
    $m = Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum
    [pscustomobject]@{ name=$name; exists=$true; files=$m.Count; gb=[math]::Round($m.Sum/1GB,3); path=$path }
  } else {
    [pscustomobject]@{ name=$name; exists=$false; files=0; gb=0; path=$path }
  }
}
