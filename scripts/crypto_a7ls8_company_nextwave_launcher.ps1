param(
  [string]$Repo = 'D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote',
  [string]$Python = 'D:\HermesWorker\workspace\.venv\Scripts\python.exe',
  [string]$External = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls8_company_numeric',
  [string]$LogDir = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\logs',
  [string]$Shards = '0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15',
  [int]$RowsPerShard = 64,
  [int]$MaxParallel = 4,
  [int]$HoursPerSplit = 2160
)

$ErrorActionPreference = 'Stop'

New-Item -ItemType Directory -Force -Path $External, $LogDir | Out-Null

if (!(Test-Path $Repo)) { throw "missing repo: $Repo" }
if (!(Test-Path $Python)) { throw "missing python: $Python" }

$QueuePath = Join-Path $Repo 'runtime\a7ls7_clue_mechanism_queue_contract\a7ls7_next_company_numeric_queue.csv'
$AuthManifest = Join-Path $Repo 'runtime\a7ls7_clue_mechanism_queue_contract\a7ls7_manifest.json'
if (!(Test-Path $QueuePath)) { throw "missing queue: $QueuePath" }
if (!(Test-Path $AuthManifest)) { throw "missing auth manifest: $AuthManifest" }

$env:ALPHAFACTORY_CRYPTO_DATA_ROOT = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData'
$env:A7AL_BASE_PANEL_ROOT = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527'

$ShardIds = @()
foreach ($token in $Shards.Split(',')) {
  $t = $token.Trim().ToLower().Replace('s','').Replace('shard_','').Trim("'").Trim('"')
  if ($t.Length -gt 0) { $ShardIds += [int]$t }
}

if ($ShardIds.Count -eq 0) { throw 'no shards requested' }
if ($RowsPerShard -le 0) { throw 'RowsPerShard must be positive' }
if ($MaxParallel -le 0) { throw 'MaxParallel must be positive' }

$MakeQueues = @"
import pandas as pd
from pathlib import Path

repo = Path(r'$Repo')
external = Path(r'$External')
queue = pd.read_csv(repo / 'runtime/a7ls7_clue_mechanism_queue_contract/a7ls7_next_company_numeric_queue.csv')

for shard in [$($ShardIds -join ',')]:
    shard_name = f'a7ls8_s{shard:03d}'
    part = queue.loc[queue['company_numeric_shard'].astype(str).eq(shard_name)].copy()
    if part.empty:
        print(f'{shard_name} rows=0 skipped_empty')
        continue
    part['a7input_queue'] = shard_name
    shard_dir = external / f'shard_{shard:03d}'
    shard_dir.mkdir(parents=True, exist_ok=True)
    part.to_csv(shard_dir / f'a7ls8_s{shard:03d}_queue.csv', index=False)
    print(f'{shard_name} rows={len(part)}')
"@

$MakeQueuesPath = Join-Path $External 'make_a7ls8_shard_queues.py'
$MakeQueues | Set-Content -Path $MakeQueuesPath -Encoding UTF8
& $Python $MakeQueuesPath

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Launched = @()
$Jobs = @()

foreach ($Shard in $ShardIds) {
  $S = '{0:D3}' -f $Shard
  $ShardDir = Join-Path $External "shard_$S"
  $Queue = Join-Path $ShardDir "a7ls8_s$S`_queue.csv"
  $Manifest = Join-Path $ShardDir "a7ls8_s$S`_manifest.json"
  if (!(Test-Path $Queue)) {
    Write-Output "skip s$S missing queue"
    continue
  }
  if (Test-Path $Manifest) {
    Write-Output "skip s$S existing manifest"
    continue
  }

  while (($Jobs | Where-Object { -not $_.HasExited }).Count -ge $MaxParallel) {
    Start-Sleep -Seconds 15
  }

  $Runner = Join-Path $LogDir "a7ls8_s$S`_$Stamp.ps1"
  $Stdout = Join-Path $LogDir "a7ls8_s$S`_$Stamp.stdout.log"
  $Stderr = Join-Path $LogDir "a7ls8_s$S`_$Stamp.stderr.log"
  $MainLog = Join-Path $LogDir "a7ls8_s$S`_$Stamp.main.log"
  $Report = Join-Path $ShardDir "CRYPTO_A7LS8_S$S`_NUMERIC_DETAIL_20260605.md"

  $Script = @"
`$ErrorActionPreference='Continue'
Set-Location '$Repo'
`$env:ALPHAFACTORY_CRYPTO_DATA_ROOT='D:\HermesWorker\GDrive\AlphaFactory_CryptoData'
`$env:A7AL_BASE_PANEL_ROOT='D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527'
`$env:A7FF8_STAGE='A7LS-8-S$S'
`$env:A7FF8_FILE_PREFIX='a7ls8_s$S'
`$env:A7FF8_RUNTIME='$ShardDir'
`$env:A7FF8_REPORT='$Report'
`$env:A7FF8_QUEUE_PATH='$Queue'
`$env:A7FF8_AUTH_MANIFEST='$AuthManifest'
`$env:A7FF8_AUTH_DECISION='PASS_A7LS7_MECHANISM_QUEUE_READY_FOR_A7LS8_COMPANY_NUMERIC_NO_SEARCH_AUTH'
`$env:A7FF8_MATERIALIZE_CAP='$RowsPerShard'
`$env:A7FF8_FAST_NUMERIC_CAP='$RowsPerShard'
`$env:A7FF8_PORTFOLIO_CAP='160'
`$env:A7FF8_QUEUE_OFFSET='0'
`$env:A7FF8_QUEUE_LIMIT='$RowsPerShard'
`$env:A7FF8_WRITE_CONTROL_DETAIL='1'
`$env:A7FF8_HOURS_PER_SPLIT='$HoursPerSplit'
"START `$((Get-Date).ToString('o')) shard=s$S rows=$RowsPerShard hours_per_split=$HoursPerSplit" | Out-File -FilePath '$MainLog' -Encoding utf8
& '$Python' scripts\crypto_a7ff8_expanded_numeric_probe.py *>> '$MainLog'
"END `$((Get-Date).ToString('o')) exit=`$LASTEXITCODE" | Out-File -FilePath '$MainLog' -Append -Encoding utf8
exit `$LASTEXITCODE
"@

  Set-Content -LiteralPath $Runner -Encoding UTF8 -Value $Script
  $Proc = Start-Process powershell.exe -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $Runner) -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr -WindowStyle Hidden -PassThru
  $Jobs += $Proc
  $Launched += [pscustomobject]@{
    shard = "s$S"
    process_id = $Proc.Id
    rows_per_shard = $RowsPerShard
    hours_per_split = $HoursPerSplit
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

$LaunchCsv = Join-Path $External "a7ls8_launch_$Stamp.csv"
$Launched | Export-Csv -Path $LaunchCsv -NoTypeInformation -Encoding UTF8
Write-Output "launch_csv=$LaunchCsv"
$Launched | Format-Table -AutoSize | Out-String -Width 260

foreach ($Job in $Jobs) {
  if (Get-Process -Id $Job.Id -ErrorAction SilentlyContinue) {
    Wait-Process -Id $Job.Id
  }
}

$Missing = @()
foreach ($Row in $Launched) {
  if (!(Test-Path $Row.manifest)) { $Missing += $Row.manifest }
}

if ($Missing.Count -gt 0) {
  Write-Output 'MISSING_MANIFESTS'
  $Missing | ForEach-Object { Write-Output $_ }
  exit 2
}

Write-Output 'A7LS8_COMPANY_NUMERIC_DONE'
Write-Output $LaunchCsv
