@echo off
set REMOTE_ROOT=D:\HermesWorker\GDrive\AlphaFactory_CryptoData
set PY=%REMOTE_ROOT%\.venv_agg\Scripts\python.exe
set ALPHAFACTORY_CRYPTO_DATA_ROOT=%REMOTE_ROOT%
set ALPHAFACTORY_CRYPTO_REPO_ROOT=%REMOTE_ROOT%
set A7AL_BASE_PANEL_ROOT=%REMOTE_ROOT%\gold\features\binance_universe498_replay_1h_v2_20260527
set A7AL_LV1_PANEL=%REMOTE_ROOT%\gold\features\binance_universe498_latent_state_features_v1_20260527.parquet
set A7AL2Q_EXEC_REPLAY_CAP=128
set OUT=%REMOTE_ROOT%\logs\a7al2q2r_company_full_20260528.out.log
set ERR=%REMOTE_ROOT%\logs\a7al2q2r_company_full_20260528.err.log
if not exist "%REMOTE_ROOT%\logs" mkdir "%REMOTE_ROOT%\logs"
echo started %DATE% %TIME% > "%OUT%"
echo. > "%ERR%"
"%PY%" "%REMOTE_ROOT%\scripts\company_build_universe498_v2_if_missing.py" >> "%OUT%" 2>> "%ERR%"
echo build_v2_exit_code=%ERRORLEVEL% >> "%OUT%"
if not "%ERRORLEVEL%"=="0" exit /b %ERRORLEVEL%
"%PY%" "%REMOTE_ROOT%\scripts\crypto_a7al2q_local_oi_price_formula_search.py" >> "%OUT%" 2>> "%ERR%"
echo a7al2q_exit_code=%ERRORLEVEL% >> "%OUT%"
if not "%ERRORLEVEL%"=="0" exit /b %ERRORLEVEL%
"%PY%" "%REMOTE_ROOT%\scripts\crypto_a7al2r_local_forensic.py" >> "%OUT%" 2>> "%ERR%"
echo a7al2r_exit_code=%ERRORLEVEL% >> "%OUT%"
exit /b %ERRORLEVEL%
