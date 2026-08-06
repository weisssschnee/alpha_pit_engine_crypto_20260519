param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$RuntimeDate,
    [Parameter(Mandatory = $true)]
    [string]$SourceSha,
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $RepoRoot

$branch = (git branch --show-current).Trim()
$head = (git rev-parse HEAD).Trim().ToLowerInvariant()
$autocrlf = (git config --get core.autocrlf).Trim().ToLowerInvariant()
if ($branch -ne "experiment/crypto-search-evidence-v1-1-20260805") {
    throw "Unexpected branch: $branch"
}
if ($head -ne $SourceSha.ToLowerInvariant()) {
    throw "Source SHA mismatch: $head"
}
if ($autocrlf -ne "false") {
    throw "core.autocrlf must be false"
}
if (git status --porcelain --untracked-files=all) {
    throw "Producer worktree must be clean"
}

$smokeRoot = Join-Path $env:TEMP "crypto_search_temporal_activation_v1_smoke_$RuntimeDate\process_evidence"
& $PythonExe -m alphafactory_crypto.broad_search.temporal_activation_v1 source-smoke `
    --repo-root $RepoRoot `
    --smoke-evidence-root $smokeRoot
if ($LASTEXITCODE -ne 0) {
    throw "No-market source/process smoke failed"
}

& $PythonExe -m alphafactory_crypto.broad_search.temporal_activation_v1 run `
    --repo-root $RepoRoot `
    --runtime-date $RuntimeDate `
    --source-sha $SourceSha
if ($LASTEXITCODE -ne 0) {
    throw "Temporal activation producer failed"
}

& $PythonExe -m alphafactory_crypto.broad_search.temporal_activation_v1 check `
    --repo-root $RepoRoot `
    --runtime-date $RuntimeDate
if ($LASTEXITCODE -ne 0) {
    throw "Temporal activation independent checker failed"
}
