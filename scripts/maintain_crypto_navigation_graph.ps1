[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("build", "maintain", "check", "query")]
    [string]$Command = "check",

    [string]$Question,

    [ValidateRange(100, 10000)]
    [int]$Budget = 1200,

    [string]$GraphifyExecutable
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$GraphDir = Join-Path $RepoRoot ".planning\graphs"
$GraphJson = Join-Path $GraphDir "graph.json"
$GraphReport = Join-Path $GraphDir "GRAPH_REPORT.md"
$GraphHtml = Join-Path $GraphDir "graph.html"
$CurrentJson = Join-Path $GraphDir "current.json"
$CurrentHtml = Join-Path $GraphDir "current.html"
$CurrentOverlay = Join-Path $RepoRoot "config\architecture_overlay.json"
$GeneratedRelativePaths = @(
    ".planning/graphs/graph.json",
    ".planning/graphs/GRAPH_REPORT.md",
    ".planning/graphs/graph.html",
    ".planning/graphs/current.json",
    ".planning/graphs/current.html"
)
$RawFreshnessNeutralExact = @(
    $GeneratedRelativePaths
    ".planning/config.json"
    "config/architecture_overlay.json"
    "reports/CRYPTO_REAL_DATA_INSTRUMENT_CANARY_REPORT.md"
    "reports/CRYPTO_CEM_DIVERSITY_AB_REPORT.md"
)
$RawFreshnessNeutralPrefixes = @(
    ".planning/graphs/execution_traces/",
    "config/architecture_profiles/",
    "profiles/",
    "runtime/crypto_real_data_instrument_canary_",
    "runtime/crypto_cem_diversity_ab_"
)

function Test-RawFreshnessNeutral([string]$Path) {
    $normalized = $Path.Replace("\", "/").TrimStart("/")
    if ($RawFreshnessNeutralExact -contains $normalized) {
        return $true
    }
    return @($RawFreshnessNeutralPrefixes | Where-Object { $normalized.StartsWith($_, [StringComparison]::OrdinalIgnoreCase) }).Count -gt 0
}

function Resolve-GraphifyExecutable {
    if ($GraphifyExecutable) {
        if (-not (Test-Path -LiteralPath $GraphifyExecutable -PathType Leaf)) {
            throw "Graphify executable not found: $GraphifyExecutable"
        }
        return (Resolve-Path -LiteralPath $GraphifyExecutable).Path
    }

    $fromPath = Get-Command graphify -ErrorAction SilentlyContinue
    if ($fromPath) {
        return $fromPath.Source
    }

    $workspaceRuntime = "G:\PythonProject\.venv\Scripts\graphify.exe"
    if (Test-Path -LiteralPath $workspaceRuntime -PathType Leaf) {
        return $workspaceRuntime
    }

    throw "graphify is unavailable. Set -GraphifyExecutable or install the compatible graphifyy runtime separately."
}

function Assert-CompatibleGraphify([string]$Executable) {
    $versionText = (& $Executable --version 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $versionText -notmatch "(?<version>\d+\.\d+\.\d+)") {
        throw "Unable to read graphify version from: $Executable"
    }

    $version = [version]$Matches.version
    if ($version -lt [version]"0.4.0" -or $version -ge [version]"1.0.0") {
        throw "Unsupported graphify version $version; expected >=0.4.0,<1.0."
    }

    Write-Host "graphify $version"
}

function Get-ChangedPaths([string]$BuiltCommit, [string]$HeadCommit) {
    $paths = @()
    if ($BuiltCommit -ne $HeadCommit) {
        $paths += @(git -C $RepoRoot diff --name-only "$BuiltCommit..$HeadCommit" -- .)
        if ($LASTEXITCODE -ne 0) {
            throw "Unable to compare graph build commit $BuiltCommit with HEAD $HeadCommit."
        }
    }

    $porcelain = @(git -C $RepoRoot status --porcelain=v1 --untracked-files=all)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read Git worktree status."
    }
    foreach ($line in $porcelain) {
        if ($line.Length -ge 4) {
            $paths += $line.Substring(3).Replace("\", "/")
        }
    }
    return @($paths | Where-Object { $_ } | Sort-Object -Unique)
}

function Invoke-GraphCheck {
    foreach ($required in @($GraphJson, $GraphReport)) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
            throw "Required raw graph artifact is missing: $required"
        }
    }

    $graph = Get-Content -LiteralPath $GraphJson -Raw -Encoding UTF8 | ConvertFrom-Json
    $builtCommit = [string]$graph.built_at_commit
    if (-not $builtCommit) {
        throw "graph.json has no built_at_commit identity."
    }

    git -C $RepoRoot cat-file -e "$builtCommit^{commit}" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "graph.json references unknown commit: $builtCommit"
    }

    $headCommit = (git -C $RepoRoot rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to resolve repository HEAD."
    }

    $changedPaths = @(Get-ChangedPaths -BuiltCommit $builtCommit -HeadCommit $headCommit)
    $nonGeneratedChanges = @($changedPaths | Where-Object { -not (Test-RawFreshnessNeutral -Path $_) })
    if ($nonGeneratedChanges.Count -gt 0) {
        throw "Raw graph is stale or the worktree has non-Graph changes: $($nonGeneratedChanges -join ', ')"
    }

    $selfIndexed = @(
        $graph.nodes | Where-Object {
            $source = [string]$_.source_file
            $GeneratedRelativePaths -contains $source
        }
    )
    if ($selfIndexed.Count -gt 0) {
        throw "Raw graph indexed its own generated products. Check .graphifyignore."
    }

    $edgeCount = if ($null -ne $graph.links) { @($graph.links).Count } else { @($graph.edges).Count }
    $currentFresh = Test-CurrentFreshness
    [pscustomobject]@{
        status = "RAW_NAVIGATION_GRAPH_FRESH"
        built_at_commit = $builtCommit
        head_commit = $headCommit
        nodes = @($graph.nodes).Count
        edges = $edgeCount
        html_present = Test-Path -LiteralPath $GraphHtml -PathType Leaf
        current_view = ".planning/graphs/current.json"
        current_view_is_generated = $true
        current_present = $true
        current_fresh = $currentFresh
    } | ConvertTo-Json -Depth 3
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Test-CurrentFreshness {
    foreach ($required in @($CurrentJson, $CurrentHtml, $CurrentOverlay)) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
            throw "Required CURRENT architecture artifact is missing: $required"
        }
    }

    $current = Get-Content -LiteralPath $CurrentJson -Raw -Encoding UTF8 | ConvertFrom-Json
    if ([string]$current.raw.sha256 -ne (Get-Sha256 -Path $GraphJson)) {
        throw "CURRENT is stale against RAW graph.json. Run maintain."
    }
    if ([string]$current.overlay.sha256 -ne (Get-Sha256 -Path $CurrentOverlay)) {
        throw "CURRENT is stale against config/architecture_overlay.json. Run maintain."
    }
    foreach ($profile in @($current.profiles)) {
        $profilePath = Join-Path $RepoRoot ([string]$profile.path)
        if (-not (Test-Path -LiteralPath $profilePath -PathType Leaf)) {
            throw "CURRENT profile is missing: $($profile.path)"
        }
        if ([string]$profile.sha256 -ne (Get-Sha256 -Path $profilePath)) {
            throw "CURRENT is stale against profile: $($profile.path). Run maintain."
        }
    }
    return $true
}

function Invoke-CurrentArchitectureProjection {
    $python = 'G:\PythonProject\.venv\Scripts\python.exe'
    $syncScript = 'G:\CodexData\.codex\skills\gsd-graphify-runtime-fidelity\scripts\architecture_sync.py'

    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        throw "CURRENT projection Python runtime not found: $python"
    }
    if (-not (Test-Path -LiteralPath $syncScript -PathType Leaf)) {
        throw "CURRENT projection renderer not found: $syncScript"
    }

    & $python $syncScript `
        --project-root $RepoRoot `
        --overlay $CurrentOverlay `
        --raw-graph $GraphJson `
        --out-dir $GraphDir
    if ($LASTEXITCODE -ne 0) {
        throw "CURRENT architecture projection failed with exit code $LASTEXITCODE"
    }
}

function Invoke-GraphBuild([string]$Executable) {
    $tempRoot = Join-Path ([IO.Path]::GetTempPath()) ("crypto-graphify-" + [guid]::NewGuid().ToString("N"))
    $tempFullPath = [IO.Path]::GetFullPath($tempRoot)
    $systemTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    New-Item -ItemType Directory -Path $tempFullPath -Force | Out-Null

    $previousOut = $env:GRAPHIFY_OUT
    try {
        $env:GRAPHIFY_OUT = $tempFullPath
        & $Executable update $RepoRoot --force
        if ($LASTEXITCODE -ne 0) {
            throw "graphify update failed with exit code $LASTEXITCODE."
        }

        $builtGraph = Join-Path $tempFullPath "graph.json"
        $builtReport = Join-Path $tempFullPath "GRAPH_REPORT.md"
        $builtHtml = Join-Path $tempFullPath "graph.html"
        foreach ($required in @($builtGraph, $builtReport)) {
            if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
                throw "graphify did not produce required artifact: $required"
            }
        }

        New-Item -ItemType Directory -Path $GraphDir -Force | Out-Null
        Copy-Item -LiteralPath $builtGraph -Destination $GraphJson -Force
        Copy-Item -LiteralPath $builtReport -Destination $GraphReport -Force
        if (Test-Path -LiteralPath $builtHtml -PathType Leaf) {
            Copy-Item -LiteralPath $builtHtml -Destination $GraphHtml -Force
        }
        elseif (Test-Path -LiteralPath $GraphHtml -PathType Leaf) {
            Remove-Item -LiteralPath $GraphHtml -Force
        }
    }
    finally {
        $env:GRAPHIFY_OUT = $previousOut
        $safeTemp = $tempFullPath.StartsWith($systemTemp, [StringComparison]::OrdinalIgnoreCase) -and
            ((Split-Path -Leaf $tempFullPath) -like "crypto-graphify-*")
        if ($safeTemp -and (Test-Path -LiteralPath $tempFullPath)) {
            Remove-Item -LiteralPath $tempFullPath -Recurse -Force
        }
    }

    Invoke-CurrentArchitectureProjection
    Invoke-GraphCheck
}

$graphify = Resolve-GraphifyExecutable
Assert-CompatibleGraphify -Executable $graphify

switch ($Command) {
    "build" {
        Invoke-GraphBuild -Executable $graphify
    }
    "maintain" {
        Invoke-CurrentArchitectureProjection
        Invoke-GraphCheck
    }
    "check" {
        Invoke-GraphCheck
    }
    "query" {
        if (-not $Question) {
            throw "query requires -Question."
        }
        if (-not (Test-Path -LiteralPath $GraphJson -PathType Leaf)) {
            throw "Raw graph is missing: $GraphJson"
        }
        & $graphify query $Question --budget $Budget --graph $GraphJson
        if ($LASTEXITCODE -ne 0) {
            throw "graphify query failed with exit code $LASTEXITCODE."
        }
    }
}
