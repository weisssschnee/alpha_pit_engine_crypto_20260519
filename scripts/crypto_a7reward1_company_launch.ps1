$ErrorActionPreference = "Stop"

$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe"
$RunRoot = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7reward1_portfolio_reward_model_20260610"
$LocalRuntime = Join-Path $Repo "runtime\a7reward1_portfolio_reward_model_20260610"
$LocalReport = Join-Path $Repo "reports\CRYPTO_A7REWARD1_PORTFOLIO_REWARD_MODEL_20260610.md"
$Queue = Join-Path $Repo "runtime\a7ls30_productive_numeric_acceptance_20260610\a7ls30_selected_top240.csv"

New-Item -ItemType Directory -Force -Path $RunRoot | Out-Null
Set-Location $Repo

$env:A7REWARD_CANDIDATE_CAP = "80"
$env:A7REWARD_HOURS_PER_SPLIT = "720"
$env:A7REWARD_COST_BPS = "5"
$env:A7REWARD_CHECKPOINT_EVERY = "4"

& $Python scripts\crypto_a7reward1_portfolio_reward_model.py `
  --queue $Queue `
  --candidate-cap 80 `
  --hours-per-split 720 `
  --cost-bps 5 `
  --checkpoint-every 4 `
  --runtime $LocalRuntime `
  --report $LocalReport

Copy-Item -Recurse -Force $LocalRuntime $RunRoot
Copy-Item -Force $LocalReport $RunRoot
