param(
  [string]$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote",
  [string]$Python = "D:\HermesWorker\venvs\phase3z33\Scripts\python.exe",
  [int]$ShardSize = 96,
  [int]$ShardCount = 4
)

$ErrorActionPreference = "Stop"
$RuntimeRoot = Join-Path $Repo "runtime"
$ReportRoot = Join-Path $Repo "reports"
$LogRoot = Join-Path $Repo "runtime\a7ff10_company_parallel"
New-Item -ItemType Directory -Force -Path $RuntimeRoot, $ReportRoot, $LogRoot | Out-Null

if (-not (Test-Path -LiteralPath $Python)) {
  throw "Python not found: $Python"
}
if (-not (Test-Path -LiteralPath (Join-Path $Repo "scripts\crypto_a7ff8_expanded_numeric_probe.py"))) {
  throw "A7FF numeric probe runner not found under repo: $Repo"
}

$rows = @()
for ($i = 0; $i -lt $ShardCount; $i++) {
  $offset = $i * $ShardSize
  $shard = "{0:D2}" -f $i
  $stage = "A7FF-10S$shard"
  $prefix = "a7ff10s$shard"
  $runtime = Join-Path $RuntimeRoot "a7ff10_company_numeric_probe_shard_$shard"
  $report = Join-Path $ReportRoot "CRYPTO_A7FF10S${shard}_COMPANY_NUMERIC_PROBE_20260530.md"
  $log = Join-Path $LogRoot "a7ff10s${shard}.log"
  New-Item -ItemType Directory -Force -Path $runtime | Out-Null

  $cmd = @"
`$env:A7FF8_STAGE='$stage'
`$env:A7FF8_FILE_PREFIX='$prefix'
`$env:A7FF8_RUNTIME='$runtime'
`$env:A7FF8_REPORT='$report'
`$env:ALPHAFACTORY_CRYPTO_DATA_ROOT='D:\HermesWorker\GDrive\AlphaFactory_CryptoData'
`$env:A7AL_BASE_PANEL_ROOT='D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527'
`$env:A7FF8_MATERIALIZE_CAP='384'
`$env:A7FF8_FAST_NUMERIC_CAP='0'
`$env:A7FF8_QUEUE_OFFSET='$offset'
`$env:A7FF8_QUEUE_LIMIT='$ShardSize'
`$env:A7FF8_PORTFOLIO_CAP='128'
Set-Location '$Repo'
& '$Python' 'scripts\crypto_a7ff8_expanded_numeric_probe.py' *> '$log'
"@
  $scriptPath = Join-Path $LogRoot "run_a7ff10s${shard}.ps1"
  Set-Content -LiteralPath $scriptPath -Value $cmd -Encoding UTF8
  $proc = Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $scriptPath) -WorkingDirectory $Repo -WindowStyle Hidden -PassThru
  $rows += [pscustomobject]@{
    stage = $stage
    shard = $shard
    offset = $offset
    limit = $ShardSize
    process_id = $proc.Id
    runtime = $runtime
    report = $report
    log = $log
    script = $scriptPath
    launched_at = (Get-Date).ToString("o")
  }
}

$manifest = Join-Path $LogRoot "a7ff10_company_parallel_launch_manifest.csv"
$rows | Export-Csv -LiteralPath $manifest -NoTypeInformation -Encoding UTF8
$rows | ConvertTo-Json -Depth 4
