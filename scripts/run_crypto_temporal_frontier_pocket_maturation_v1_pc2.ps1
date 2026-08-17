param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$RuntimeId,
    [Parameter(Mandatory = $true)][string]$PythonExe
)
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $RepoRoot
& $PythonExe scripts/run_crypto_temporal_frontier_pocket_maturation_v1.py --repo-root $RepoRoot --runtime-id $RuntimeId
exit $LASTEXITCODE
