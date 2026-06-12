$ErrorActionPreference = "Stop"
$Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe"
$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Runtime = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_v3_native_large_search_20260613"
$Queue = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_v3_native_large_search_20260613\a7v3s0_large_search_queue.csv"
$env:A7AL_BASE_PANEL_ROOT = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v3_patch_age_20260613"
Set-Location $Repo
New-Item -ItemType Directory -Force -Path $Runtime | Out-Null
$Concurrency = 4
$SymbolCap = 192
$TimestampCap = 4096
$shards = @(
  @{id="a7v3s0_s000"; start=0; end=1024},
  @{id="a7v3s0_s001"; start=1024; end=2048},
  @{id="a7v3s0_s002"; start=2048; end=3072},
  @{id="a7v3s0_s003"; start=3072; end=4096},
  @{id="a7v3s0_s004"; start=4096; end=5120},
  @{id="a7v3s0_s005"; start=5120; end=6144},
  @{id="a7v3s0_s006"; start=6144; end=7168},
  @{id="a7v3s0_s007"; start=7168; end=8192},
  @{id="a7v3s0_s008"; start=8192; end=9216},
  @{id="a7v3s0_s009"; start=9216; end=10240},
  @{id="a7v3s0_s010"; start=10240; end=11264},
  @{id="a7v3s0_s011"; start=11264; end=12288},
  @{id="a7v3s0_s012"; start=12288; end=13312},
  @{id="a7v3s0_s013"; start=13312; end=14336},
  @{id="a7v3s0_s014"; start=14336; end=15360},
  @{id="a7v3s0_s015"; start=15360; end=16384},
  @{id="a7v3s0_s016"; start=16384; end=17408},
  @{id="a7v3s0_s017"; start=17408; end=18432},
  @{id="a7v3s0_s018"; start=18432; end=19456},
  @{id="a7v3s0_s019"; start=19456; end=20480},
  @{id="a7v3s0_s020"; start=20480; end=21504},
  @{id="a7v3s0_s021"; start=21504; end=22528},
  @{id="a7v3s0_s022"; start=22528; end=23552},
  @{id="a7v3s0_s023"; start=23552; end=24576},
  @{id="a7v3s0_s024"; start=24576; end=25600},
  @{id="a7v3s0_s025"; start=25600; end=26624},
  @{id="a7v3s0_s026"; start=26624; end=27648},
  @{id="a7v3s0_s027"; start=27648; end=28672},
  @{id="a7v3s0_s028"; start=28672; end=29696},
  @{id="a7v3s0_s029"; start=29696; end=30720},
  @{id="a7v3s0_s030"; start=30720; end=31744},
  @{id="a7v3s0_s031"; start=31744; end=32768},
  @{id="a7v3s0_s032"; start=32768; end=33792},
  @{id="a7v3s0_s033"; start=33792; end=34816},
  @{id="a7v3s0_s034"; start=34816; end=35840},
  @{id="a7v3s0_s035"; start=35840; end=36864},
  @{id="a7v3s0_s036"; start=36864; end=37888},
  @{id="a7v3s0_s037"; start=37888; end=38912},
  @{id="a7v3s0_s038"; start=38912; end=39936},
  @{id="a7v3s0_s039"; start=39936; end=40960},
  @{id="a7v3s0_s040"; start=40960; end=41984},
  @{id="a7v3s0_s041"; start=41984; end=43008},
  @{id="a7v3s0_s042"; start=43008; end=44032},
  @{id="a7v3s0_s043"; start=44032; end=45056},
  @{id="a7v3s0_s044"; start=45056; end=46080},
  @{id="a7v3s0_s045"; start=46080; end=47104},
  @{id="a7v3s0_s046"; start=47104; end=48128},
  @{id="a7v3s0_s047"; start=48128; end=49152},
  @{id="a7v3s0_s048"; start=49152; end=50176},
  @{id="a7v3s0_s049"; start=50176; end=51200},
  @{id="a7v3s0_s050"; start=51200; end=52224},
  @{id="a7v3s0_s051"; start=52224; end=53248},
  @{id="a7v3s0_s052"; start=53248; end=54272},
  @{id="a7v3s0_s053"; start=54272; end=55296},
  @{id="a7v3s0_s054"; start=55296; end=56320},
  @{id="a7v3s0_s055"; start=56320; end=57344},
  @{id="a7v3s0_s056"; start=57344; end=58368},
  @{id="a7v3s0_s057"; start=58368; end=59392},
  @{id="a7v3s0_s058"; start=59392; end=60416},
  @{id="a7v3s0_s059"; start=60416; end=61440},
  @{id="a7v3s0_s060"; start=61440; end=62464},
  @{id="a7v3s0_s061"; start=62464; end=63488},
  @{id="a7v3s0_s062"; start=63488; end=64512},
  @{id="a7v3s0_s063"; start=64512; end=65536}
)
$active = @()
foreach ($s in $shards) {
  $manifest = Join-Path $Runtime ("shards\" + $s.id + "\a7ls17_manifest.json")
  if (Test-Path $manifest) { Write-Host "[A7V3S0] skip existing $($s.id)"; continue }
  while (($active | Where-Object { -not $_.HasExited }).Count -ge $Concurrency) { Start-Sleep -Seconds 20; $active = @($active | Where-Object { -not $_.HasExited }) }
  $shardRoot = Join-Path $Runtime ("shards\" + $s.id)
  New-Item -ItemType Directory -Force -Path $shardRoot | Out-Null
  $env:A7LS17_QUEUE_PATH = $Queue
  $env:A7LS17_RUNTIME = $Runtime
  $env:A7LS17_SHARD_ID = $s.id
  $env:A7LS17_START_ROW = [string]$s.start
  $env:A7LS17_END_ROW = [string]$s.end
  $env:A7LS17_SYMBOL_CAP = [string]$SymbolCap
  $env:A7LS17_TIMESTAMP_CAP = [string]$TimestampCap
  $env:A7LS17_PROGRESS_EVERY = "256"
  $outLog = Join-Path $shardRoot "runner.out.log"
  $errLog = Join-Path $shardRoot "runner.err.log"
  Write-Host "[A7V3S0] start $($s.id) rows=$($s.start):$($s.end)"
  $p = Start-Process -FilePath $Python -ArgumentList @('scripts\crypto_a7ls17_company_materialization_runner.py') -RedirectStandardOutput $outLog -RedirectStandardError $errLog -PassThru -WindowStyle Hidden
  $active += $p
}
while (($active | Where-Object { -not $_.HasExited }).Count -gt 0) { Start-Sleep -Seconds 30; $active = @($active | Where-Object { -not $_.HasExited }) }
$summary = @()
foreach ($s in $shards) {
  $manifest = Join-Path $Runtime ("shards\" + $s.id + "\a7ls17_manifest.json")
  if (Test-Path $manifest) { $m = Get-Content $manifest -Raw | ConvertFrom-Json; $summary += [pscustomobject]@{shard_id=$s.id; decision=$m.decision; queue_rows=$m.queue_rows; eval_success_count=$m.eval_success_count; activity_ok_count=$m.activity_ok_count} }
  else { $summary += [pscustomobject]@{shard_id=$s.id; decision='MISSING_MANIFEST'; queue_rows=0; eval_success_count=0; activity_ok_count=0} }
}
$summary | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $Runtime 'a7v3s0_materialization_summary.json')
Write-Host "[A7V3S0] materialization wave complete"
