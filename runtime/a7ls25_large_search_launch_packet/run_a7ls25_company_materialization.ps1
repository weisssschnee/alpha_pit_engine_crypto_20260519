$ErrorActionPreference = "Stop"
$Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe"
$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Runtime = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls25_large_search_materialization_20260607"
$Queue = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls25_large_search_materialization_20260607\a7ls25_materialization_queue_40k.csv"
$Concurrency = 2
Set-Location $Repo
New-Item -ItemType Directory -Force -Path $Runtime | Out-Null
$shards = @(
  @{id="a7ls25_mat_s000"; start=0; end=1000},
  @{id="a7ls25_mat_s001"; start=1000; end=2000},
  @{id="a7ls25_mat_s002"; start=2000; end=3000},
  @{id="a7ls25_mat_s003"; start=3000; end=4000},
  @{id="a7ls25_mat_s004"; start=4000; end=5000},
  @{id="a7ls25_mat_s005"; start=5000; end=6000},
  @{id="a7ls25_mat_s006"; start=6000; end=7000},
  @{id="a7ls25_mat_s007"; start=7000; end=8000},
  @{id="a7ls25_mat_s008"; start=8000; end=9000},
  @{id="a7ls25_mat_s009"; start=9000; end=10000},
  @{id="a7ls25_mat_s010"; start=10000; end=11000},
  @{id="a7ls25_mat_s011"; start=11000; end=12000},
  @{id="a7ls25_mat_s012"; start=12000; end=13000},
  @{id="a7ls25_mat_s013"; start=13000; end=14000},
  @{id="a7ls25_mat_s014"; start=14000; end=15000},
  @{id="a7ls25_mat_s015"; start=15000; end=16000},
  @{id="a7ls25_mat_s016"; start=16000; end=17000},
  @{id="a7ls25_mat_s017"; start=17000; end=18000},
  @{id="a7ls25_mat_s018"; start=18000; end=19000},
  @{id="a7ls25_mat_s019"; start=19000; end=20000},
  @{id="a7ls25_mat_s020"; start=20000; end=21000},
  @{id="a7ls25_mat_s021"; start=21000; end=22000},
  @{id="a7ls25_mat_s022"; start=22000; end=23000},
  @{id="a7ls25_mat_s023"; start=23000; end=24000},
  @{id="a7ls25_mat_s024"; start=24000; end=25000},
  @{id="a7ls25_mat_s025"; start=25000; end=26000},
  @{id="a7ls25_mat_s026"; start=26000; end=27000},
  @{id="a7ls25_mat_s027"; start=27000; end=28000},
  @{id="a7ls25_mat_s028"; start=28000; end=29000},
  @{id="a7ls25_mat_s029"; start=29000; end=30000},
  @{id="a7ls25_mat_s030"; start=30000; end=31000},
  @{id="a7ls25_mat_s031"; start=31000; end=32000},
  @{id="a7ls25_mat_s032"; start=32000; end=33000},
  @{id="a7ls25_mat_s033"; start=33000; end=34000},
  @{id="a7ls25_mat_s034"; start=34000; end=35000},
  @{id="a7ls25_mat_s035"; start=35000; end=36000},
  @{id="a7ls25_mat_s036"; start=36000; end=37000},
  @{id="a7ls25_mat_s037"; start=37000; end=38000},
  @{id="a7ls25_mat_s038"; start=38000; end=39000},
  @{id="a7ls25_mat_s039"; start=39000; end=40000}
)
$active = @()
foreach ($s in $shards) {
  $manifest = Join-Path $Runtime ("shards\" + $s.id + "\a7ls17_manifest.json")
  if (Test-Path $manifest) { Write-Host "[A7LS25] skip existing $($s.id)"; continue }
  while (($active | Where-Object { -not $_.HasExited }).Count -ge $Concurrency) { Start-Sleep -Seconds 10; $active = @($active | Where-Object { -not $_.HasExited }) }
  $shardRoot = Join-Path $Runtime ("shards\" + $s.id)
  New-Item -ItemType Directory -Force -Path $shardRoot | Out-Null
  $env:A7LS17_QUEUE_PATH = $Queue
  $env:A7LS17_RUNTIME = $Runtime
  $env:A7LS17_SHARD_ID = $s.id
  $env:A7LS17_START_ROW = [string]$s.start
  $env:A7LS17_END_ROW = [string]$s.end
  $env:A7LS17_SYMBOL_CAP = "192"
  $env:A7LS17_TIMESTAMP_CAP = "4096"
  $env:A7LS17_PROGRESS_EVERY = "250"
  $outLog = Join-Path $shardRoot "runner.out.log"
  $errLog = Join-Path $shardRoot "runner.err.log"
  Write-Host "[A7LS25] start $($s.id) rows=$($s.start):$($s.end)"
  $p = Start-Process -FilePath $Python -ArgumentList @('scripts\crypto_a7ls17_company_materialization_runner.py') -RedirectStandardOutput $outLog -RedirectStandardError $errLog -PassThru -WindowStyle Hidden
  $active += $p
}
while (($active | Where-Object { -not $_.HasExited }).Count -gt 0) { Start-Sleep -Seconds 15; $active = @($active | Where-Object { -not $_.HasExited }) }
$summary = @()
foreach ($s in $shards) {
  $manifest = Join-Path $Runtime ("shards\" + $s.id + "\a7ls17_manifest.json")
  if (Test-Path $manifest) { $m = Get-Content $manifest -Raw | ConvertFrom-Json; $summary += [pscustomobject]@{shard_id=$s.id; decision=$m.decision; queue_rows=$m.queue_rows; eval_success_count=$m.eval_success_count; activity_ok_count=$m.activity_ok_count} }
  else { $summary += [pscustomobject]@{shard_id=$s.id; decision='MISSING_MANIFEST'; queue_rows=0; eval_success_count=0; activity_ok_count=0} }
}
$summary | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $Runtime 'a7ls25_materialization_summary.json')
Write-Host "[A7LS25] materialization wave complete"