@echo off
set REMOTE_ROOT=D:\HermesWorker\GDrive\AlphaFactory_CryptoData
set ALPHAFACTORY_CRYPTO_DATA_ROOT=%REMOTE_ROOT%
set ALPHAFACTORY_CRYPTO_REPO_ROOT=%REMOTE_ROOT%
set A7AL_BASE_PANEL_ROOT=%REMOTE_ROOT%\gold\features\binance_universe498_replay_1h_v1_20260525
set A7AL_LV1_PANEL=%REMOTE_ROOT%\gold\features\binance_universe498_latent_state_features_v1_20260527.parquet
set A7AL_REGIME_PANEL=%REMOTE_ROOT%\gold\features\binance_universe498_upper_regime_state_v1_20260527.parquet
set A7AL_TAXONOMY=%REMOTE_ROOT%\runtime\a7ak_lv3r_contract_meme_taxonomy_audit\a7ak_lv3r_contract_meme_taxonomy.csv
set PY=%REMOTE_ROOT%\.venv_agg\Scripts\python.exe
set SCRIPT=%REMOTE_ROOT%\scripts\crypto_a7al1_field_family_neutralized_baseline.py
set OUT=%REMOTE_ROOT%\logs\a7al1_field_family_baseline_company_bat_20260527.out.log
set ERR=%REMOTE_ROOT%\logs\a7al1_field_family_baseline_company_bat_20260527.err.log
echo started %DATE% %TIME% > %OUT%
echo. > %ERR%
"%PY%" "%SCRIPT%" >> %OUT% 2>> %ERR%
echo exit_code=%ERRORLEVEL% >> %OUT%
