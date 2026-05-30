param(
  [string]$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote",
  [string]$Python = "D:\HermesWorker\venvs\phase3z33\Scripts\python.exe",
  [int]$ShardCount = 4,
  [int]$ShardSize = 90,
  [int]$StartShard = 0,
  [int]$MaxParallel = 2
)

$ErrorActionPreference = "Stop"

$runtimeRoot = Join-Path $Repo "runtime\a7ff12_company_parallel"
$queuePath = Join-Path $Repo "runtime\a7ff12_numeric_wave_queue_contract\a7ff12_numeric_wave_queue.csv"
New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null

$env:ALPHAFACTORY_CRYPTO_DATA_ROOT = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData"
$env:A7AL_BASE_PANEL_ROOT = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527"

if (-not (Test-Path $Python)) {
  throw "Python not found: $Python"
}
if (-not (Test-Path $queuePath)) {
  throw "A7FF-12 queue not found: $queuePath"
}

$jobs = @()
$manifestRows = @()

for ($i = $StartShard; $i -lt ($StartShard + $ShardCount); $i++) {
  $sid = "{0:D2}" -f $i
  $offset = $i * $ShardSize
  $stage = "A7FF-12S$sid"
  $filePrefix = "a7ff12s$sid"
  $runtime = Join-Path $Repo "runtime\a7ff12_company_numeric_probe_shard_$sid"
  $report = Join-Path $Repo "reports\CRYPTO_A7FF12S$sid`_COMPANY_NUMERIC_PROBE_20260530.md"
  $outLog = Join-Path $runtimeRoot "a7ff12s$sid.out.log"
  $errLog = Join-Path $runtimeRoot "a7ff12s$sid.err.log"
  $runner = Join-Path $runtimeRoot "run_a7ff12s$sid.ps1"
  New-Item -ItemType Directory -Force -Path $runtime | Out-Null

  $script = @"
`$ErrorActionPreference = "Stop"
Set-Location "$Repo"
`$env:ALPHAFACTORY_CRYPTO_DATA_ROOT = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData"
`$env:A7AL_BASE_PANEL_ROOT = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527"
`$env:A7FF8_STAGE = "$stage"
`$env:A7FF8_FILE_PREFIX = "$filePrefix"
`$env:A7FF8_RUNTIME = "$runtime"
`$env:A7FF8_REPORT = "$report"
`$env:A7FF8_QUEUE_PATH = "$queuePath"
`$env:A7FF8_QUEUE_OFFSET = "$offset"
`$env:A7FF8_QUEUE_LIMIT = "$ShardSize"
`$env:A7FF8_MATERIALIZE_CAP = "$ShardSize"
`$env:A7FF8_FAST_NUMERIC_CAP = "$ShardSize"
`$env:A7FF8_PORTFOLIO_CAP = "128"
& "$Python" "scripts\crypto_a7ff8_expanded_numeric_probe.py"
"@
  Set-Content -Path $runner -Value $script -Encoding UTF8

  while (($jobs | Where-Object { -not $_.HasExited }).Count -ge $MaxParallel) {
    Start-Sleep -Seconds 10
  }

  $proc = Start-Process powershell.exe -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $runner) -RedirectStandardOutput $outLog -RedirectStandardError $errLog -WindowStyle Hidden -PassThru
  $jobs += $proc
  $manifestRows += [pscustomobject]@{
    stage = $stage
    shard = $sid
    offset = $offset
    limit = $ShardSize
    process_id = $proc.Id
    runtime = $runtime
    report = $report
    out_log = $outLog
    err_log = $errLog
    script = $runner
    launched_at = (Get-Date).ToString("o")
  }
}

foreach ($job in $jobs) {
  if (Get-Process -Id $job.Id -ErrorAction SilentlyContinue) {
    Wait-Process -Id $job.Id
  }
}

$manifestPath = Join-Path $runtimeRoot "a7ff12_company_wave_launch_manifest.csv"
$manifestRows | Export-Csv -NoTypeInformation -Path $manifestPath

$missing = @()
foreach ($row in $manifestRows) {
  $manifest = Join-Path $row.runtime ("a7ff12s" + $row.shard + "_manifest.json")
  if (-not (Test-Path $manifest)) {
    $missing += $manifest
  }
}
if ($missing.Count -gt 0) {
  Write-Output "MISSING_MANIFESTS"
  $missing | ForEach-Object { Write-Output $_ }
  exit 2
}

Write-Output "A7FF12_COMPANY_WAVE_DONE"
Write-Output $manifestPath
