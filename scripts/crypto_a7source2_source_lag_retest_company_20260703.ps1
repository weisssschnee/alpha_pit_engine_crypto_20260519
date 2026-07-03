$ErrorActionPreference = "Stop"

$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe"
$Panel = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v3_patch_age_20260613"

Set-Location $Repo
$env:A7SEARCH6_JUNE_PANEL_ROOT = $Panel
$env:A7AL_BASE_PANEL_ROOT = $Panel
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:NUMEXPR_MAX_THREADS = "4"

& $Python scripts\crypto_a7source2_source_lag_retest.py
if ($LASTEXITCODE -ne 0) {
  throw "A7SOURCE-2 source-lag retest failed with exit code $LASTEXITCODE"
}
