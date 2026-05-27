$ErrorActionPreference = 'Stop'

$RemoteRoot = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData'
$Python = Join-Path $RemoteRoot '.venv_agg\Scripts\python.exe'
$Script = Join-Path $RemoteRoot 'scripts\crypto_a7al1_field_family_neutralized_baseline.py'
$LogDir = Join-Path $RemoteRoot 'logs'
$RunStamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Stdout = Join-Path $LogDir "a7al1_field_family_baseline_company_$RunStamp.out.log"
$Stderr = Join-Path $LogDir "a7al1_field_family_baseline_company_$RunStamp.err.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$env:ALPHAFACTORY_CRYPTO_DATA_ROOT = $RemoteRoot
$env:ALPHAFACTORY_CRYPTO_REPO_ROOT = $RemoteRoot
$env:A7AL_BASE_PANEL_ROOT = Join-Path $RemoteRoot 'gold\features\binance_universe498_replay_1h_v1_20260525'
$env:A7AL_LV1_PANEL = Join-Path $RemoteRoot 'gold\features\binance_universe498_latent_state_features_v1_20260527.parquet'
$env:A7AL_REGIME_PANEL = Join-Path $RemoteRoot 'gold\features\binance_universe498_upper_regime_state_v1_20260527.parquet'
$env:A7AL_TAXONOMY = Join-Path $RemoteRoot 'runtime\a7ak_lv3r_contract_meme_taxonomy_audit\a7ak_lv3r_contract_meme_taxonomy.csv'

Write-Host "A7AL1 company run"
Write-Host "python=$Python"
Write-Host "script=$Script"
Write-Host "stdout=$Stdout"
Write-Host "stderr=$Stderr"

$Bat = Join-Path $RemoteRoot 'scripts\run_company_a7al1_field_family_baseline_20260527.bat'
$proc = Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c', $Bat) -WorkingDirectory $RemoteRoot -PassThru -WindowStyle Hidden
Write-Host "pid=$($proc.Id)"
