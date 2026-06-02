$repo = 'G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519'
$runtime = Join-Path $repo 'runtime/a7ffcore51px_company_sharded_replay_runner_contract'
$out = 'G:/AlphaFactory_CryptoData/research_runtime/a7ffcore51px_company_sharded_replay_20260602'
$compact = Join-Path $out 'a7ffcore51px_compact_frame.parquet'
New-Item -ItemType Directory -Force -Path $out | Out-Null
py (Join-Path $repo 'scripts/crypto_a7ffcore51px_company_compact_frame_builder.py') --out $compact --contract $runtime
Get-ChildItem (Join-Path $runtime 'candidate_shards') -Filter '*.csv' | ForEach-Object {
  py (Join-Path $repo 'scripts/crypto_a7ffcore51px_company_shard_worker.py') --shard $_.FullName --compact-frame $compact --out $out
}
