param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$RuntimeId,
    [string]$Python = "D:\HermesWorker\workspace\crypto_line\.venv_b251733\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $RepoRoot
& $Python scripts/run_crypto_temporal_representation_successor_v1.py `
    --repo-root $RepoRoot `
    --runtime-id $RuntimeId
exit $LASTEXITCODE
