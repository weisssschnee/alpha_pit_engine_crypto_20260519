param(
  [string]$Repo = 'G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519',
  [string]$Python = 'py',
  [string]$External = 'G:\AlphaFactory_CryptoData\research_runtime\a7ls18_local_numeric_20260606_r2',
  [string]$QueuePath = 'G:\AlphaFactory_CryptoData\research_runtime\a7ls18_local_numeric_20260606_r2\a7ls18_company_numeric_queue.csv',
  [string]$LogDir = 'G:\AlphaFactory_CryptoData\logs\a7ls18_local_numeric_20260606_r2',
  [int]$RowsPerShard = 512,
  [string]$ShardRange = '96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147',
  [int]$MaxParallel = 2
)

$ErrorActionPreference = 'Stop'

New-Item -ItemType Directory -Force -Path $External, $LogDir | Out-Null
if (!(Test-Path $Repo)) { throw "missing repo: $Repo" }
if (!(Test-Path $QueuePath)) { throw "missing queue: $QueuePath" }
if ($RowsPerShard -le 0) { throw 'RowsPerShard must be positive' }
if ($MaxParallel -le 0) { throw 'MaxParallel must be positive' }

$AuthManifest = Join-Path $Repo 'runtime\a7ls17_company_materialization_aggregate\a7ls17_manifest.json'
if (!(Test-Path $AuthManifest)) { throw "missing auth manifest: $AuthManifest" }

$MakeQueues = @"
from pathlib import Path
import pandas as pd

queue = pd.read_csv(r'$QueuePath')
external = Path(r'$External')
rows_per_shard = int($RowsPerShard)
shards = [$($ShardRange)]
for shard in shards:
    part = queue.iloc[shard * rows_per_shard:(shard + 1) * rows_per_shard].copy()
    if part.empty:
        print(f'skip a7ls18_s{shard:03d} empty')
        continue
    shard_id = f'a7ls18_s{shard:03d}'
    shard_dir = external / 'shards' / shard_id
    shard_dir.mkdir(parents=True, exist_ok=True)
    part['a7input_queue'] = 'a7ls18_local_numeric'
    part['core58_queue'] = 'a7ls18_local_numeric'
    part['company_numeric_shard'] = shard_id
    part.to_csv(shard_dir / f'{shard_id}_queue.csv', index=False)
    print(f'{shard_id} rows={len(part)}')
"@

$MakeQueuesPath = Join-Path $External 'make_a7ls18_local_shard_queues.py'
$MakeQueues | Set-Content -Path $MakeQueuesPath -Encoding UTF8
& $Python $MakeQueuesPath

$ShardIds = @()
foreach ($token in $ShardRange.Split(',')) {
  $t = $token.Trim().ToLower().Replace('a7ls18_s','').Replace('s','').Trim("'").Trim('"')
  if ($t.Length -gt 0) { $ShardIds += [int]$t }
}

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Launched = @()
$Jobs = @()

foreach ($Shard in $ShardIds) {
  $ShardId = 'a7ls18_s{0:D3}' -f $Shard
  $ShardDir = Join-Path (Join-Path $External 'shards') $ShardId
  $Queue = Join-Path $ShardDir "$ShardId`_queue.csv"
  $Manifest = Join-Path $ShardDir "$ShardId`_manifest.json"
  if (!(Test-Path $Queue)) {
    Write-Output "skip $ShardId missing queue"
    continue
  }
  if (Test-Path $Manifest) {
    Write-Output "skip $ShardId existing manifest"
    continue
  }

  while (($Jobs | Where-Object { -not $_.HasExited }).Count -ge $MaxParallel) {
    Start-Sleep -Seconds 20
  }

  $Runner = Join-Path $LogDir "$ShardId`_$Stamp.ps1"
  $Stdout = Join-Path $LogDir "$ShardId`_$Stamp.stdout.log"
  $Stderr = Join-Path $LogDir "$ShardId`_$Stamp.stderr.log"
  $MainLog = Join-Path $LogDir "$ShardId`_$Stamp.main.log"
  $Report = Join-Path $ShardDir "CRYPTO_A7LS18_LOCAL_$ShardId`_NUMERIC_DETAIL_20260606.md"
  $Rows = (Import-Csv $Queue | Measure-Object).Count

  $Script = @"
`$ErrorActionPreference='Continue'
Set-Location '$Repo'
`$env:ALPHAFACTORY_CRYPTO_DATA_ROOT='G:\AlphaFactory_CryptoData'
`$env:A7AL_BASE_PANEL_ROOT='G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527'
`$env:A7FF8_STAGE='A7LS-18-LOCAL-$ShardId'
`$env:A7FF8_FILE_PREFIX='$ShardId'
`$env:A7FF8_RUNTIME='$ShardDir'
`$env:A7FF8_REPORT='$Report'
`$env:A7FF8_QUEUE_PATH='$Queue'
`$env:A7FF8_AUTH_MANIFEST='$AuthManifest'
`$env:A7FF8_AUTH_DECISION='PASS_A7LS17_COMPANY_MATERIALIZATION_AGGREGATE_READY_FOR_A7LS18'
`$env:A7FF8_MATERIALIZE_CAP='$Rows'
`$env:A7FF8_FAST_NUMERIC_CAP='$Rows'
`$env:A7FF8_PORTFOLIO_CAP='192'
`$env:A7FF8_QUEUE_OFFSET='0'
`$env:A7FF8_QUEUE_LIMIT='$Rows'
`$env:A7FF8_WRITE_CONTROL_DETAIL='1'
"START `$((Get-Date).ToString('o')) shard=$ShardId rows=$Rows" | Out-File -FilePath '$MainLog' -Encoding utf8
& $Python scripts\crypto_a7ff8_expanded_numeric_probe.py *>> '$MainLog'
"END `$((Get-Date).ToString('o')) exit=`$LASTEXITCODE" | Out-File -FilePath '$MainLog' -Append -Encoding utf8
exit `$LASTEXITCODE
"@

  Set-Content -LiteralPath $Runner -Encoding UTF8 -Value $Script
  $Proc = Start-Process powershell.exe -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $Runner) -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr -WindowStyle Hidden -PassThru
  $Jobs += $Proc
  $Launched += [pscustomobject]@{
    shard = $ShardId
    process_id = $Proc.Id
    rows = $Rows
    runtime = $ShardDir
    queue = $Queue
    manifest = $Manifest
    report = $Report
    runner = $Runner
    stdout = $Stdout
    stderr = $Stderr
    mainlog = $MainLog
    launched_at = (Get-Date).ToString('o')
  }
}

$LaunchCsv = Join-Path $External "a7ls18_local_launch_$Stamp.csv"
$Launched | Export-Csv -Path $LaunchCsv -NoTypeInformation -Encoding UTF8
Write-Output "launch_csv=$LaunchCsv"
$Launched | Format-Table -AutoSize | Out-String -Width 280

foreach ($Job in $Jobs) {
  if (Get-Process -Id $Job.Id -ErrorAction SilentlyContinue) {
    Wait-Process -Id $Job.Id
  }
}

Write-Output 'A7LS18_LOCAL_NUMERIC_DONE_OR_PARTIAL'
Write-Output $LaunchCsv
