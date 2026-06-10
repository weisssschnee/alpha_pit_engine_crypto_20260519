$ErrorActionPreference = "Continue"
$Runtime = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\runtime\a7reward1_portfolio_reward_model_20260610"
Write-Output "== checkpoint status =="
Get-Content "$Runtime\a7reward1_checkpoint_status.json"
Write-Output "== checkpoint top =="
Import-Csv "$Runtime\a7reward1_checkpoint_candidate_reward_leaderboard.csv" |
  Select-Object -First 12 blueprint_id,horizon_h,overall_reward,recent_sortino,recent_sharpe,recent_rankic,recent_shuffle_control_ratio,hard_reject,hard_reject_reasons,expression |
  Format-List
