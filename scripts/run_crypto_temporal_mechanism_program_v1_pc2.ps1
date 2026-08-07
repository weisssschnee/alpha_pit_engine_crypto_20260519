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

function Invoke-PythonChecked {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,
        [Parameter(Mandatory = $true)]
        [string]$FailureMessage
    )

    # Windows PowerShell turns native stderr into ErrorRecord objects.  A
    # harmless RuntimeWarning must remain visible without becoming a terminating
    # PowerShell error; the native process exit code is the sole authority.
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $PythonExe @Arguments 2>&1 | ForEach-Object { Write-Output $_ }
        $nativeExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($nativeExitCode -ne 0) {
        throw "$FailureMessage (exit code $nativeExitCode)"
    }
}

$branch = (git branch --show-current).Trim()
$head = (git rev-parse HEAD).Trim().ToLowerInvariant()
$autocrlf = (git config --get core.autocrlf).Trim().ToLowerInvariant()
if ($branch -ne "experiment/crypto-temporal-program-search-v1-20260807") {
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

Invoke-PythonChecked -Arguments @(
    "-m", "alphafactory_crypto.broad_search.temporal_program_search_v1",
    "source-smoke", "--repo-root", $RepoRoot
) -FailureMessage "Temporal program no-market source smoke failed"

Invoke-PythonChecked -Arguments @(
    "-m", "alphafactory_crypto.broad_search.temporal_program_search_v1",
    "run", "--repo-root", $RepoRoot, "--runtime-date", $RuntimeDate,
    "--source-sha", $SourceSha
) -FailureMessage "Temporal program producer failed"

Invoke-PythonChecked -Arguments @(
    "-m", "alphafactory_crypto.broad_search.temporal_program_search_v1",
    "check", "--repo-root", $RepoRoot, "--runtime-date", $RuntimeDate
) -FailureMessage "Temporal program independent checker failed"
