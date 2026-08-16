param(
    [Parameter(Mandatory=$true)][string]$RepoRoot,
    [Parameter(Mandatory=$true)][string]$RuntimeId,
    [switch]$PreflightOnly
)
$ErrorActionPreference = 'Stop'
$python = 'G:\PythonProject\.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { $python = 'python' }
$arguments = @('scripts/run_crypto_temporal_hypothesis_frontier_v1.py', '--repo-root', $RepoRoot, '--runtime-id', $RuntimeId)
if ($PreflightOnly) { $arguments += '--preflight-only' }
& $python @arguments
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
