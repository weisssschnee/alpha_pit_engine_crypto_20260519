$repo = 'G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519'
$out = 'G:/AlphaFactory_CryptoData/research_runtime/a7ffcore51px_company_sharded_replay_20260602'
New-Item -ItemType Directory -Force -Path $out | Out-Null
py (Join-Path $repo 'scripts/crypto_a7ffcore51pxe_company_sharded_replay_orchestrator.py') --out $out --jobs 8
