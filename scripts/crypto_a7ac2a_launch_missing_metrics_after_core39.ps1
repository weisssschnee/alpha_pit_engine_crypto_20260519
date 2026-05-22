param(
  [string]$RepoRoot = 'G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519',
  [string]$DataRoot = 'G:\AlphaFactory_CryptoData',
  [string]$CurrentCore39Status = 'G:\AlphaFactory_CryptoData\reports\core39_metrics_expansion_status_20260522_181951.json',
  [string]$Tag = ('a7ac_primary_missing_' + (Get-Date -Format 'yyyyMMdd_HHmmss')),
  [int]$MaxConcurrent = 6,
  [int]$PollSeconds = 60
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$Python = 'G:\PythonProject\.venv\Scripts\python.exe'
$Runner = Join-Path $DataRoot 'scripts\run_binance_metrics_core39_expansion.py'
$Registry = Join-Path $RepoRoot 'runtime\a7ac1_expanded_universe_backfill_contract\a7ac1_track_symbol_registry.csv'
$LogDir = Join-Path $DataRoot 'logs\a7ac_primary_metrics_missing_launcher'
$ReportDir = Join-Path $DataRoot 'reports'
New-Item -ItemType Directory -Force -Path $LogDir,$ReportDir | Out-Null

$statusPath = Join-Path $ReportDir "$Tag`_launcher_status.json"
$outLog = Join-Path $LogDir "$Tag.out.log"
$errLog = Join-Path $LogDir "$Tag.err.log"

function Write-Status([hashtable]$State) {
  $State.generated_at = (Get-Date).ToUniversalTime().ToString('s') + 'Z'
  $tmp = "$statusPath.tmp"
  $State | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $tmp -Encoding UTF8
  Move-Item -LiteralPath $tmp -Destination $statusPath -Force
}

function Current-Core39-Active {
  if (!(Test-Path -LiteralPath $CurrentCore39Status)) { return $false }
  try {
    $s = Get-Content -LiteralPath $CurrentCore39Status -Raw | ConvertFrom-Json
    return (($s.counts.pending -gt 0) -or ($s.counts.running -gt 0))
  } catch {
    return $true
  }
}

$primary = Import-Csv -LiteralPath $Registry | Where-Object { $_.track -eq 'primary_core48_top36_addition' } | Select-Object -ExpandProperty symbol
$core39 = @(
  'DOTUSDT','TRXUSDT','UNIUSDT','AAVEUSDT','APTUSDT','ARBUSDT',
  'OPUSDT','NEARUSDT','ATOMUSDT','FILUSDT','INJUSDT','SEIUSDT',
  'TIAUSDT','ETCUSDT','XLMUSDT','HBARUSDT','ICPUSDT','ORDIUSDT',
  'ARUSDT','GALAUSDT','SANDUSDT','MANAUSDT','ALGOUSDT','IMXUSDT',
  'STXUSDT','WLDUSDT','JTOUSDT'
)
$missing = @($primary | Where-Object { $core39 -notcontains $_ } | Sort-Object)

Write-Status @{
  decision = 'A7AC2A_WAITING_FOR_CORE39_THEN_LAUNCH_MISSING_METRICS'
  tag = $Tag
  current_core39_status = $CurrentCore39Status
  missing_symbols = $missing
  missing_count = $missing.Count
  max_concurrent = $MaxConcurrent
  status = 'waiting'
  executes_download = $true
  executes_search = $false
  authorizes_alpha_proof = $false
}

while (Current-Core39-Active) {
  Write-Status @{
    decision = 'A7AC2A_WAITING_FOR_CORE39_THEN_LAUNCH_MISSING_METRICS'
    tag = $Tag
    current_core39_status = $CurrentCore39Status
    missing_symbols = $missing
    missing_count = $missing.Count
    max_concurrent = $MaxConcurrent
    status = 'waiting_for_core39'
    executes_download = $true
    executes_search = $false
    authorizes_alpha_proof = $false
  }
  Start-Sleep -Seconds $PollSeconds
}

if ($missing.Count -eq 0) {
  Write-Status @{
    decision = 'PASS_A7AC2A_NO_MISSING_METRICS_SYMBOLS'
    tag = $Tag
    current_core39_status = $CurrentCore39Status
    missing_symbols = $missing
    missing_count = 0
    status = 'completed_noop'
    executes_download = $false
    executes_search = $false
    authorizes_alpha_proof = $false
  }
  exit 0
}

$args = @(
  '-u', $Runner,
  '--symbols'
) + $missing + @(
  '--start', '2024-01-01',
  '--end', '2026-05-21',
  '--max-concurrent', [string]$MaxConcurrent,
  '--sleep', '0.01',
  '--tag', $Tag
)

Write-Status @{
  decision = 'A7AC2A_RUNNING_MISSING_METRICS'
  tag = $Tag
  missing_symbols = $missing
  missing_count = $missing.Count
  command = $Python + ' ' + ($args -join ' ')
  out_log = $outLog
  err_log = $errLog
  status = 'running'
  executes_download = $true
  executes_search = $false
  authorizes_alpha_proof = $false
}

$proc = Start-Process -FilePath $Python -ArgumentList $args -RedirectStandardOutput $outLog -RedirectStandardError $errLog -WindowStyle Hidden -PassThru -Wait

Write-Status @{
  decision = $(if ($proc.ExitCode -eq 0) { 'PASS_A7AC2A_MISSING_METRICS_RUN_COMPLETED' } else { 'HOLD_A7AC2A_MISSING_METRICS_RUN_FAILED' })
  tag = $Tag
  missing_symbols = $missing
  missing_count = $missing.Count
  exit_code = $proc.ExitCode
  out_log = $outLog
  err_log = $errLog
  status = 'finished'
  executes_download = $true
  executes_search = $false
  authorizes_alpha_proof = $false
}

exit $proc.ExitCode
