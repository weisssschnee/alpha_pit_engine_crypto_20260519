$ErrorActionPreference = "Stop"
$Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe"
$RepoRoot = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$RunRoot = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls21_company_deep_replay_20260607"
$Shards = @("s000","s001","s002","s003")

New-Item -ItemType Directory -Force -Path $RunRoot | Out-Null
Set-Location $RepoRoot
$env:PYTHONPATH = $RepoRoot
$env:NUMEXPR_MAX_THREADS = "4"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"

$summary = @()
foreach ($Shard in $Shards) {
  $ShardRoot = Join-Path $RunRoot ("shards\" + $Shard)
  $Manifest = Join-Path $ShardRoot ("a7ls21_" + $Shard + "_manifest.json")
  if (Test-Path $Manifest) {
    try {
      $existing = Get-Content -Raw $Manifest | ConvertFrom-Json
      if ($existing.decision -like "PASS_*") {
        Write-Output "[A7LS21] skip existing PASS shard $Shard"
        $summary += [pscustomobject]@{ shard=$Shard; status="skip_existing_pass"; decision=$existing.decision }
        continue
      }
    } catch {}
  }

  Write-Output "[A7LS21] running shard $Shard"
  $env:A7FF8_STAGE = "A7LS-21-$Shard"
  $env:A7FF8_FILE_PREFIX = "a7ls21_$Shard"
  $env:A7FF8_RUNTIME = $ShardRoot
  $env:A7FF8_REPORT = (Join-Path $ShardRoot ("A7LS21_" + $Shard + "_REPORT.md"))
  $env:A7FF8_QUEUE_PATH = (Join-Path $ShardRoot "queue.csv")
  $env:A7FF8_AUTH_MANIFEST = (Join-Path $RunRoot "a7ls21_auth_manifest.json")
  $env:A7FF8_AUTH_DECISION = "PASS_A7LS20_MARGINAL_QUEUE_READY_FOR_A7LS21_DEEP_REPLAY_PACKET"
  $env:A7FF8_PLAN_PATH = (Join-Path $RunRoot "a7ls21_plan.json")
  $env:A7FF8_MATERIALIZE_CAP = "12"
  $env:A7FF8_FAST_NUMERIC_CAP = "12"
  $env:A7FF8_PORTFOLIO_CAP = "12"
  $env:A7FF8_QUEUE_LIMIT = "12"
  $env:A7FF8_HOURS_PER_SPLIT = "2160"
  $env:A7FF8_WRITE_CONTROL_DETAIL = "1"

  $OldErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  & $Python scripts\crypto_a7ff8_expanded_numeric_probe.py > (Join-Path $ShardRoot "runner.log") 2>&1
  $code = $LASTEXITCODE
  $ErrorActionPreference = $OldErrorActionPreference
  if ($code -ne 0) {
    Write-Output "[A7LS21] shard $Shard failed exit=$code"
    $summary += [pscustomobject]@{ shard=$Shard; status="failed"; exit_code=$code; decision="" }
  } else {
    $manifestPath = Join-Path $ShardRoot ("a7ls21_" + $Shard + "_manifest.json")
    $decision = ""
    if (Test-Path $manifestPath) {
      try { $decision = (Get-Content -Raw $manifestPath | ConvertFrom-Json).decision } catch {}
    }
    Write-Output "[A7LS21] shard $Shard done decision=$decision"
    $summary += [pscustomobject]@{ shard=$Shard; status="done"; exit_code=0; decision=$decision }
  }
}

$summary | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $RunRoot "a7ls21_runner_summary.json")
Write-Output "[A7LS21] complete"
