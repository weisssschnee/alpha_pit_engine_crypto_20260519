param(
  [string]$Repo = 'D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote',
  [string]$Python = 'D:\HermesWorker\workspace\.venv\Scripts\python.exe',
  [string]$SourceRuntime = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls17_company_materialization_20260606_r3',
  [string]$AuthManifest = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls17_company_materialization_aggregate_20260606\a7ls17_manifest.json',
  [string]$External = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls18_company_numeric_20260606',
  [string]$LogDir = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\logs\a7ls18_company_numeric_20260606',
  [int]$RowsPerShard = 512,
  [int]$MaxRows = 100000,
  [string]$ShardRange = 'all',
  [int]$MaxParallel = 3
)

$ErrorActionPreference = 'Stop'

New-Item -ItemType Directory -Force -Path $External, $LogDir | Out-Null

if (!(Test-Path $Repo)) { throw "missing repo: $Repo" }
if (!(Test-Path $Python)) { throw "missing python: $Python" }
if (!(Test-Path $SourceRuntime)) { throw "missing source runtime: $SourceRuntime" }
if (!(Test-Path $AuthManifest)) { throw "missing auth manifest: $AuthManifest" }
if ($RowsPerShard -le 0) { throw 'RowsPerShard must be positive' }
if ($MaxParallel -le 0) { throw 'MaxParallel must be positive' }

$env:ALPHAFACTORY_CRYPTO_DATA_ROOT = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData'
$env:A7AL_BASE_PANEL_ROOT = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527'

$BuildQueues = @"
import json
from pathlib import Path

import pandas as pd

source = Path(r'$SourceRuntime')
external = Path(r'$External')
rows_per_shard = int($RowsPerShard)
max_rows = int($MaxRows)

files = sorted((source / 'shards').glob('a7ls17_s*/a7ls17_materialization_metrics.csv'))
if not files:
    raise SystemExit(f'no A7LS17 materialization metrics under {source}')

frames = []
for path in files:
    df = pd.read_csv(path)
    df['source_file'] = str(path)
    frames.append(df)

all_rows = pd.concat(frames, ignore_index=True)
mask = (
    all_rows['eval_success'].astype(str).str.lower().isin({'true', '1'})
    & all_rows['activity_ok'].astype(str).str.lower().isin({'true', '1'})
)
ok = all_rows.loc[mask].copy()
if ok.empty:
    raise SystemExit('no activity-ok A7LS17 rows for A7LS18')

ok['finite_share'] = pd.to_numeric(ok['finite_share'], errors='coerce').fillna(0.0)
ok['nonzero_share'] = pd.to_numeric(ok['nonzero_share'], errors='coerce').fillna(0.0)
ok['std_value'] = pd.to_numeric(ok['std_value'], errors='coerce').fillna(0.0)
ok['materialization_score'] = ok['finite_share'].clip(0, 1) * 0.55 + ok['nonzero_share'].clip(0, 1) * 0.35 + (ok['std_value'] > 0).astype(float) * 0.10

sort_cols = ['a7ls_lane', 'semantic_pair', 'motif', 'materialization_score', 'blueprint_id']
ok = ok.sort_values(sort_cols, ascending=[True, True, True, False, True]).drop_duplicates('blueprint_id')
if max_rows > 0:
    ok = ok.head(max_rows).copy()

external.mkdir(parents=True, exist_ok=True)
queue_path = external / 'a7ls18_company_numeric_queue.csv'
ok.to_csv(queue_path, index=False)

shard_records = []
for shard_index, start in enumerate(range(0, len(ok), rows_per_shard)):
    part = ok.iloc[start:start + rows_per_shard].copy()
    shard_id = f'a7ls18_s{shard_index:03d}'
    shard_dir = external / 'shards' / shard_id
    shard_dir.mkdir(parents=True, exist_ok=True)
    part['a7input_queue'] = 'a7ls18_company_numeric'
    part['core58_queue'] = 'a7ls18_company_numeric'
    part['company_numeric_shard'] = shard_id
    part.to_csv(shard_dir / f'{shard_id}_queue.csv', index=False)
    shard_records.append({
        'shard_index': shard_index,
        'shard_id': shard_id,
        'rows': int(len(part)),
        'lane_count': int(part['a7ls_lane'].nunique()) if 'a7ls_lane' in part.columns else 0,
        'semantic_pair_count': int(part['semantic_pair'].nunique()) if 'semantic_pair' in part.columns else 0,
        'motif_count': int(part['motif'].nunique()) if 'motif' in part.columns else 0,
        'skeleton_count': int(part['skeleton_key'].nunique()) if 'skeleton_key' in part.columns else 0,
    })

shards = pd.DataFrame(shard_records)
shards.to_csv(external / 'a7ls18_shard_plan.csv', index=False)

lane_summary = ok.groupby('a7ls_lane', dropna=False).agg(
    rows=('blueprint_id', 'size'),
    semantic_pair_count=('semantic_pair', 'nunique'),
    motif_count=('motif', 'nunique'),
    skeleton_count=('skeleton_key', 'nunique'),
    median_materialization_score=('materialization_score', 'median'),
).reset_index()
lane_summary.to_csv(external / 'a7ls18_queue_lane_summary.csv', index=False)

semantic_summary = ok.groupby(['a7ls_lane', 'semantic_pair'], dropna=False).size().reset_index(name='rows').sort_values('rows', ascending=False)
semantic_summary.to_csv(external / 'a7ls18_queue_semantic_summary.csv', index=False)

manifest = {
    'stage': 'A7LS-18',
    'source_runtime': str(source),
    'queue_rows': int(len(ok)),
    'rows_per_shard': rows_per_shard,
    'shard_count': int(len(shards)),
    'lane_count': int(ok['a7ls_lane'].nunique()) if 'a7ls_lane' in ok.columns else 0,
    'semantic_pair_count': int(ok['semantic_pair'].nunique()) if 'semantic_pair' in ok.columns else 0,
    'motif_count': int(ok['motif'].nunique()) if 'motif' in ok.columns else 0,
    'skeleton_count': int(ok['skeleton_key'].nunique()) if 'skeleton_key' in ok.columns else 0,
    'auth_manifest': r'$AuthManifest',
    'decision': 'A7LS18_QUEUE_BUILT_EXECUTION_IN_PROGRESS',
}
(external / 'a7ls18_queue_manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding='utf-8')
print(json.dumps(manifest, indent=2, sort_keys=True))
"@

$BuildQueuesPath = Join-Path $External 'build_a7ls18_numeric_queues.py'
$BuildQueues | Set-Content -Path $BuildQueuesPath -Encoding UTF8
& $Python $BuildQueuesPath

$ShardPlan = Import-Csv (Join-Path $External 'a7ls18_shard_plan.csv')
if ($ShardRange -ne 'all') {
  $Wanted = @{}
  foreach ($token in $ShardRange.Split(',')) {
    $t = $token.Trim().ToLower().Replace('a7ls18_s','').Replace('s','').Trim("'").Trim('"')
    if ($t.Length -gt 0) { $Wanted[[int]$t] = $true }
  }
  $ShardPlan = $ShardPlan | Where-Object { $Wanted.ContainsKey([int]$_.shard_index) }
}

if (($ShardPlan | Measure-Object).Count -eq 0) { throw 'no shards selected' }

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Launched = @()
$Jobs = @()

foreach ($Shard in $ShardPlan) {
  $ShardIndex = [int]$Shard.shard_index
  $ShardId = $Shard.shard_id
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
  $Report = Join-Path $ShardDir "CRYPTO_A7LS18_$ShardId`_NUMERIC_DETAIL_20260606.md"
  $Rows = [int]$Shard.rows

  $Script = @"
`$ErrorActionPreference='Continue'
Set-Location '$Repo'
`$env:ALPHAFACTORY_CRYPTO_DATA_ROOT='D:\HermesWorker\GDrive\AlphaFactory_CryptoData'
`$env:A7AL_BASE_PANEL_ROOT='D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527'
`$env:A7FF8_STAGE='A7LS-18-$ShardId'
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
& '$Python' scripts\crypto_a7ff8_expanded_numeric_probe.py *>> '$MainLog'
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

$LaunchCsv = Join-Path $External "a7ls18_launch_$Stamp.csv"
$Launched | Export-Csv -Path $LaunchCsv -NoTypeInformation -Encoding UTF8
Write-Output "launch_csv=$LaunchCsv"
$Launched | Format-Table -AutoSize | Out-String -Width 280

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

Write-Output 'A7LS18_COMPANY_NUMERIC_DONE'
Write-Output $LaunchCsv
