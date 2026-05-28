$ErrorActionPreference = 'Continue'
$root = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData'
$logDir = Join-Path $root 'logs\aggregate_crypto_20260525'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
& 'D:\Python311\python.exe' (Join-Path $root 'scripts\aggregate_crypto_universe500_stdlib.py') --mode all --tag 20260525_aggregate_v1 *> (Join-Path $logDir 'aggregate_crypto_universe500_20260525.out.log')
