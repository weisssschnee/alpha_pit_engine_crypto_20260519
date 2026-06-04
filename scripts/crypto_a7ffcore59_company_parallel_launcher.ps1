param(
  [string]$Repo = 'D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote',
  [string]$Python = 'D:\HermesWorker\venv_phase3z23\Scripts\python.exe',
  [string]$External = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ffcore59_numeric_repair_execution_20260604',
  [string]$LogDir = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\logs',
  [string]$Shards = '3,4,5',
  [int]$RowsPerShard = 200
)

$ErrorActionPreference = 'Continue'

New-Item -ItemType Directory -Force -Path $External, $LogDir | Out-Null
$QueuePath = Join-Path $Repo 'runtime\a7ffcore59_numeric_repair_execution\a7ffcore59_numeric_repair_queue.csv'
if (!(Test-Path $Repo)) { throw "missing repo: $Repo" }
if (!(Test-Path $Python)) { throw "missing python: $Python" }
if (!(Test-Path $QueuePath)) { throw "missing queue: $QueuePath" }

$ShardIds = @()
foreach ($token in $Shards.Split(',')) {
  $t = $token.Trim().ToLower().Replace('s','').Replace('shard_','')
  $t = $t.Trim("'").Trim('"')
  if ($t.Length -gt 0) { $ShardIds += [int]$t }
}

$MakeQueues = @"
import pandas as pd
from pathlib import Path
repo = Path(r'$Repo')
external = Path(r'$External')
queue = pd.read_csv(repo / 'runtime/a7ffcore59_numeric_repair_execution/a7ffcore59_numeric_repair_queue.csv')
rows_per_shard = $RowsPerShard
for shard in [$($ShardIds -join ',')]:
    part = queue.iloc[shard*rows_per_shard:(shard+1)*rows_per_shard].copy()
    part['a7input_queue'] = part.get('core58_queue', 'numeric_replay_repair')
    d = external / f'shard_{shard:02d}'
    d.mkdir(parents=True, exist_ok=True)
    part.to_csv(d / f'a7ffcore59_s{shard:02d}_queue.csv', index=False)
    print(f's{shard:02d} rows={len(part)}')
"@
$MakeQueuesPath = Join-Path $External 'make_parallel_shard_queues.py'
$MakeQueues | Set-Content -Path $MakeQueuesPath -Encoding UTF8
& $Python $MakeQueuesPath

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Launched = @()
foreach ($Shard in $ShardIds) {
  $S = '{0:D2}' -f $Shard
  $Manifest = Join-Path $External "shard_$S\a7ffcore59_s$S`_manifest.json"
  if (Test-Path $Manifest) {
    Write-Output "skip s$S existing manifest"
    continue
  }
  $ShardDir = Join-Path $External "shard_$S"
  $Ps1 = Join-Path $LogDir "a7ffcore59_parallel_s$S`_$Stamp.ps1"
  $Bat = Join-Path $LogDir "a7ffcore59_parallel_s$S`_$Stamp.bat"
  $Stdout = Join-Path $LogDir "a7ffcore59_parallel_s$S`_$Stamp.stdout.log"
  $Stderr = Join-Path $LogDir "a7ffcore59_parallel_s$S`_$Stamp.stderr.log"
  $MainLog = Join-Path $LogDir "a7ffcore59_parallel_s$S`_$Stamp.main.log"
  $Script = @"
`$ErrorActionPreference='Continue'
Set-Location '$Repo'
`$env:A7FF8_STAGE='A7FF-CORE59-S$S'
`$env:A7FF8_FILE_PREFIX='a7ffcore59_s$S'
`$env:A7FF8_RUNTIME='$ShardDir'
`$env:A7FF8_REPORT='$ShardDir\CRYPTO_A7FFCORE59_S$S`_NUMERIC_REPAIR_DETAIL_20260604.md'
`$env:A7FF8_QUEUE_PATH='$ShardDir\a7ffcore59_s$S`_queue.csv'
`$env:A7FF8_AUTH_MANIFEST='$Repo\runtime\a7ffcore58_failure_aware_queue_rebuild\a7ffcore58_manifest.json'
`$env:A7FF8_AUTH_DECISION='PASS_A7FFCORE58_FAILURE_AWARE_QUEUE_REBUILT_READY_FOR_CORE59'
`$env:A7FF8_MATERIALIZE_CAP='$RowsPerShard'
`$env:A7FF8_FAST_NUMERIC_CAP='$RowsPerShard'
`$env:A7FF8_PORTFOLIO_CAP='128'
`$env:A7FF8_QUEUE_OFFSET='0'
`$env:A7FF8_QUEUE_LIMIT='$RowsPerShard'
`$env:A7FF8_WRITE_CONTROL_DETAIL='1'
"START `$((Get-Date).ToString('o')) shard=s$S" | Out-File -FilePath '$MainLog' -Encoding utf8
& '$Python' scripts\crypto_a7ff8_expanded_numeric_probe.py *>> '$MainLog'
"END `$((Get-Date).ToString('o')) exit=`$LASTEXITCODE" | Out-File -FilePath '$MainLog' -Append -Encoding utf8
"@
  Set-Content -LiteralPath $Ps1 -Encoding UTF8 -Value $Script
  Set-Content -LiteralPath $Bat -Encoding ASCII -Value "@echo off`r`npowershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$Ps1`" > `"$Stdout`" 2> `"$Stderr`"`r`n"
  $TaskName = "A7FFCORE59_PARALLEL_S$S"
  cmd.exe /c "schtasks /Delete /TN $TaskName /F >NUL 2>NUL"
  schtasks.exe /Create /TN $TaskName /SC ONCE /ST 23:59 /TR $Bat /F | Out-Host
  schtasks.exe /Run /TN $TaskName | Out-Host
  $Launched += [pscustomobject]@{
    shard = "s$S"
    task = $TaskName
    ps1 = $Ps1
    bat = $Bat
    stdout = $Stdout
    stderr = $Stderr
    mainlog = $MainLog
  }
}

$LaunchCsv = Join-Path $External "a7ffcore59_parallel_launch_$Stamp.csv"
$Launched | Export-Csv -Path $LaunchCsv -NoTypeInformation -Encoding UTF8
Write-Output "launch_csv=$LaunchCsv"
$Launched | Format-Table -AutoSize | Out-String -Width 260
