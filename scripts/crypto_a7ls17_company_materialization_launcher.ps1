param(
  [string]$Repo = 'D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote',
  [string]$Python = 'D:\HermesWorker\workspace\.venv\Scripts\python.exe',
  [string]$QueuePath = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls15_million_scale_blueprint_generation_20260606\a7ls15_materialization_queue_100k.csv',
  [string]$Runtime = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls17_company_materialization_20260606',
  [string]$LogDir = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\logs\a7ls17_company_materialization_20260606',
  [string]$Shards = '0-99',
  [int]$RowsPerShard = 1000,
  [int]$MaxParallel = 3,
  [int]$SymbolCap = 128,
  [int]$TimestampCap = 2048
)

$ErrorActionPreference = 'Stop'

New-Item -ItemType Directory -Force -Path $Runtime, $LogDir | Out-Null

if (!(Test-Path $Repo)) { throw "missing repo: $Repo" }
if (!(Test-Path $Python)) { throw "missing python: $Python" }
if (!(Test-Path $QueuePath)) { throw "missing queue: $QueuePath" }

Set-Location $Repo

$ShardIds = New-Object System.Collections.Generic.List[int]
foreach ($tokenRaw in $Shards.Split(',')) {
  $token = $tokenRaw.Trim().ToLower().Replace('shard_', '').Replace('s', '')
  if ($token.Length -eq 0) { continue }
  if ($token.Contains('-')) {
    $parts = $token.Split('-')
    $start = [int]$parts[0]
    $end = [int]$parts[1]
    for ($i = $start; $i -le $end; $i++) { $ShardIds.Add($i) }
  } else {
    $ShardIds.Add([int]$token)
  }
}

if ($ShardIds.Count -eq 0) { throw 'no shards requested' }
if ($RowsPerShard -le 0) { throw 'RowsPerShard must be positive' }
if ($MaxParallel -le 0) { throw 'MaxParallel must be positive' }

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$LaunchRows = @()
$Jobs = @()

foreach ($Shard in $ShardIds) {
  $S = '{0:D3}' -f $Shard
  $StartRow = $Shard * $RowsPerShard
  $EndRow = $StartRow + $RowsPerShard
  $ShardId = "a7ls17_s$S"
  $ShardDir = Join-Path $Runtime "shards\$ShardId"
  $Manifest = Join-Path $ShardDir 'a7ls17_manifest.json'

  if (Test-Path $Manifest) {
    Write-Output "skip existing $ShardId $Manifest"
    continue
  }

  while (($Jobs | Where-Object { -not $_.HasExited }).Count -ge $MaxParallel) {
    Start-Sleep -Seconds 20
  }

  New-Item -ItemType Directory -Force -Path $ShardDir | Out-Null
  $Runner = Join-Path $LogDir "$ShardId`_$Stamp.ps1"
  $Stdout = Join-Path $LogDir "$ShardId`_$Stamp.stdout.log"
  $Stderr = Join-Path $LogDir "$ShardId`_$Stamp.stderr.log"
  $MainLog = Join-Path $LogDir "$ShardId`_$Stamp.main.log"

  $Script = @"
`$ErrorActionPreference = 'Continue'
Set-Location '$Repo'
`$env:ALPHAFACTORY_CRYPTO_DATA_ROOT = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData'
`$env:A7AL_BASE_PANEL_ROOT = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527'
`$env:A7LS17_QUEUE_PATH = '$QueuePath'
`$env:A7LS17_RUNTIME = '$Runtime'
`$env:A7LS17_SHARD_ID = '$ShardId'
`$env:A7LS17_START_ROW = '$StartRow'
`$env:A7LS17_END_ROW = '$EndRow'
`$env:A7LS17_SYMBOL_CAP = '$SymbolCap'
`$env:A7LS17_TIMESTAMP_CAP = '$TimestampCap'
`$env:OMP_NUM_THREADS = '1'
`$env:MKL_NUM_THREADS = '1'
`$env:NUMEXPR_MAX_THREADS = '4'
"START `$((Get-Date).ToString('o')) shard=$ShardId rows=$RowsPerShard symbol_cap=$SymbolCap timestamp_cap=$TimestampCap" | Out-File -FilePath '$MainLog' -Encoding utf8
& '$Python' scripts\crypto_a7ls17_company_materialization_runner.py *>> '$MainLog'
"END `$((Get-Date).ToString('o')) exit=`$LASTEXITCODE" | Out-File -FilePath '$MainLog' -Append -Encoding utf8
exit `$LASTEXITCODE
"@

  Set-Content -LiteralPath $Runner -Encoding UTF8 -Value $Script
  $Proc = Start-Process powershell.exe -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $Runner) -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr -WindowStyle Hidden -PassThru
  $Jobs += $Proc
  $LaunchRows += [pscustomobject]@{
    shard_id = $ShardId
    start_row = $StartRow
    end_row = $EndRow
    process_id = $Proc.Id
    manifest = $Manifest
    runner = $Runner
    stdout = $Stdout
    stderr = $Stderr
    mainlog = $MainLog
    launched_at = (Get-Date).ToString('o')
  }
}

$LaunchCsv = Join-Path $Runtime "a7ls17_launch_$Stamp.csv"
$LaunchRows | Export-Csv -Path $LaunchCsv -NoTypeInformation -Encoding UTF8
Write-Output "launch_csv=$LaunchCsv"
Write-Output "launched_count=$($LaunchRows.Count)"
$LaunchRows | Format-Table -AutoSize | Out-String -Width 260

foreach ($Job in $Jobs) {
  if (Get-Process -Id $Job.Id -ErrorAction SilentlyContinue) {
    Wait-Process -Id $Job.Id
  }
}

$Missing = @()
foreach ($Row in $LaunchRows) {
  if (!(Test-Path $Row.manifest)) { $Missing += $Row.manifest }
}

if ($Missing.Count -gt 0) {
  Write-Output 'MISSING_MANIFESTS'
  $Missing | ForEach-Object { Write-Output $_ }
  exit 2
}

Write-Output 'A7LS17_COMPANY_MATERIALIZATION_DONE'
Write-Output $LaunchCsv
