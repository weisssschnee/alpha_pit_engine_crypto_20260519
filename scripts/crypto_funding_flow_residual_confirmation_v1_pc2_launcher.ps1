param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$Python,
    [Parameter(Mandatory = $true)][string]$PythonOverlay,
    [Parameter(Mandatory = $true)][string]$BaseWorkspace,
    [Parameter(Mandatory = $true)][string]$ProducerSourceSha,
    [Parameter(Mandatory = $true)][string]$RuntimeDate,
    [Parameter(Mandatory = $true)][string]$ReceiptRelativePath,
    [Parameter(Mandatory = $true)][string]$ReceiptBlobSha1,
    [Parameter(Mandatory = $true)][string]$LogRoot,
    [switch]$PreflightOnly
)

$ErrorActionPreference = 'Stop'
if (Test-Path variable:PSNativeCommandUseErrorActionPreference) {
    $PSNativeCommandUseErrorActionPreference = $false
}

function Invoke-PythonProcess {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$StdoutPath,
        [Parameter(Mandatory = $true)][string]$StderrPath
    )
    $nativeArguments = @($Arguments | ForEach-Object {
        $value = [string]$_
        if ($value -match '[\s"]') {
            return '"' + $value.Replace('"', '\"') + '"'
        }
        return $value
    })
    $process = Start-Process -FilePath $Python -ArgumentList $nativeArguments `
        -WorkingDirectory $RepoRoot -WindowStyle Hidden -Wait -PassThru `
        -RedirectStandardOutput $StdoutPath -RedirectStandardError $StderrPath
    return $process.ExitCode
}

$runtimeRoot = Join-Path $RepoRoot (
    "runtime\crypto_funding_flow_residual_nested_confirmation_v1_$RuntimeDate"
)
$receiptPath = Join-Path $RepoRoot $ReceiptRelativePath
foreach ($path in @($RepoRoot, $Python, $PythonOverlay, $BaseWorkspace, $receiptPath)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "REQUIRED_PATH_MISSING:$path" }
}
if (Test-Path -LiteralPath $runtimeRoot) { throw 'RUNTIME_ALREADY_EXISTS' }
if (Test-Path -LiteralPath $LogRoot) { throw 'LOG_ROOT_ALREADY_EXISTS' }

$head = (& git -C $RepoRoot rev-parse HEAD | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $head -ne $ProducerSourceSha) {
    throw 'SOURCE_SHA_MISMATCH'
}
if (@(& git -C $RepoRoot status --porcelain).Count -ne 0) {
    throw 'WORKTREE_NOT_CLEAN'
}
$observedBlob = (
    & git -C $RepoRoot rev-parse "HEAD:$ReceiptRelativePath" | Out-String
).Trim()
if ($LASTEXITCODE -ne 0 -or $observedBlob -ne $ReceiptBlobSha1) {
    throw 'RECEIPT_BLOB_MISMATCH'
}

$cache = Get-Item -LiteralPath (Join-Path $RepoRoot '.cache') -Force
if ($cache.LinkType -ne 'Junction') { throw 'CACHE_NOT_JUNCTION' }
$runtimeParent = Join-Path $RepoRoot 'runtime'
New-Item -ItemType Directory -Path $runtimeParent -Force | Out-Null
foreach ($name in @(
    'crypto_search_engine_v1_4_oi_flow_20260728',
    'crypto_search_replication_aware_gate_v1_20260806r3',
    'crypto_search_evidence_v1_1_validation_20260805r1'
)) {
    $source = Join-Path (Join-Path $BaseWorkspace 'runtime') $name
    $destination = Join-Path $runtimeParent $name
    if (-not (Test-Path -LiteralPath $source)) {
        throw "READ_ONLY_RUNTIME_SOURCE_MISSING:$name"
    }
    if (-not (Test-Path -LiteralPath $destination)) {
        New-Item -ItemType Junction -Path $destination -Target $source | Out-Null
    }
    $item = Get-Item -LiteralPath $destination -Force
    if ($item.LinkType -ne 'Junction' -or @($item.Target) -notcontains $source) {
        throw "READ_ONLY_RUNTIME_JUNCTION_MISMATCH:$name"
    }
}

$activePython = @(Get-Process -Name python -ErrorAction SilentlyContinue)
if ($activePython.Count -ne 0) { throw 'ANOTHER_PYTHON_WORKLOAD_IS_ACTIVE' }
$operatingSystem = Get-CimInstance Win32_OperatingSystem
$freeMemoryGiB = ($operatingSystem.FreePhysicalMemory * 1KB) / 1GB
if ($freeMemoryGiB -lt 12.0) { throw 'FREE_MEMORY_BELOW_12_GIB' }

$env:PYTHONPATH = "$RepoRoot;$PythonOverlay"
$probeRoot = Join-Path ([IO.Path]::GetTempPath()) (
    'crypto-funding-flow-confirmation-' + [Guid]::NewGuid().ToString('N')
)
New-Item -ItemType Directory -Path $probeRoot | Out-Null
try {
    $preflightStdout = Join-Path $probeRoot 'preflight.stdout.log'
    $preflightStderr = Join-Path $probeRoot 'preflight.stderr.log'
    $preflightArguments = @(
        '-m', 'alphafactory_crypto.broad_search.funding_flow_residual_confirmation_v1',
        'preflight', '--repo-root', $RepoRoot, '--receipt-path', $ReceiptRelativePath
    )
    $preflightExit = Invoke-PythonProcess `
        -Arguments $preflightArguments `
        -StdoutPath $preflightStdout `
        -StderrPath $preflightStderr
    if ($preflightExit -ne 0) { throw "PREFLIGHT_EXITED_NONZERO:$preflightExit" }
    $preflight = Get-Content -LiteralPath $preflightStdout -Raw | ConvertFrom-Json
    if (
        $preflight.status -ne 'PREFLIGHT_PASS_NO_MARKET_EVALUATION' -or
        $preflight.market_read_performed -ne $false -or
        $preflight.candidate_count -ne 162 -or
        $preflight.pair_count -ne 81 -or
        $preflight.holdout_read -ne $false -or
        $preflight.oos_read -ne $false
    ) { throw 'PREFLIGHT_CONTRACT_CHANGED' }
} finally {
    Remove-Item -LiteralPath $probeRoot -Recurse -Force
}

if ($PreflightOnly) {
    [ordered]@{
        status = 'LAUNCH_PREFLIGHT_ONLY_PASS'
        producer_sha = $head
        receipt_blob_sha1 = $observedBlob
        runtime_absent = -not (Test-Path -LiteralPath $runtimeRoot)
        active_python_count = $activePython.Count
        free_memory_gib = [math]::Round($freeMemoryGiB, 3)
        candidate_count = 162
        pair_count = 81
        workers_default = 10
        workers_memory_fallback = 8
        workers_12_forbidden = $true
        evidence_status = 'REUSED_DEVELOPMENT_VALIDATION_ADAPTIVE_DIAGNOSTIC_ONLY'
    } | ConvertTo-Json -Compress
    return
}

New-Item -ItemType Directory -Path $LogRoot | Out-Null
$env:NUMEXPR_MAX_THREADS = '4'
$env:OMP_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$runStdout = Join-Path $LogRoot 'producer.stdout.log'
$runStderr = Join-Path $LogRoot 'producer.stderr.log'
$checkStdout = Join-Path $LogRoot 'checker.stdout.log'
$checkStderr = Join-Path $LogRoot 'checker.stderr.log'
$runArguments = @(
    '-m', 'alphafactory_crypto.broad_search.funding_flow_residual_confirmation_v1',
    'run', '--repo-root', $RepoRoot, '--runtime-date', $RuntimeDate,
    '--source-sha', $ProducerSourceSha, '--receipt-path', $ReceiptRelativePath
)
[ordered]@{
    status = 'LAUNCH_FROZEN'
    started_utc = [DateTime]::UtcNow.ToString('o')
    workspace = $RepoRoot
    runtime = $runtimeRoot
    producer_sha = $ProducerSourceSha
    receipt_path = $ReceiptRelativePath
    receipt_blob_sha1 = $observedBlob
    candidate_count = 162
    pair_count = 81
    workers_default = 10
    workers_memory_fallback = 8
    wall_time_seconds_limit = 14400
    evidence_status = 'REUSED_DEVELOPMENT_VALIDATION_ADAPTIVE_DIAGNOSTIC_ONLY'
    validation_b_conditional = $true
    oos_holdout_forbidden = $true
    arguments = $runArguments
} | ConvertTo-Json -Depth 6 | Set-Content `
    -LiteralPath (Join-Path $LogRoot 'launch_manifest.json') -Encoding UTF8

$started = Get-Date
$runExit = Invoke-PythonProcess `
    -Arguments $runArguments `
    -StdoutPath $runStdout `
    -StderrPath $runStderr
if ($runExit -ne 0) { throw "PRODUCER_EXITED_NONZERO:$runExit" }
$checkArguments = @(
    '-m', 'alphafactory_crypto.broad_search.funding_flow_residual_confirmation_v1',
    'check', '--repo-root', $RepoRoot, '--runtime-date', $RuntimeDate,
    '--receipt-path', $ReceiptRelativePath
)
$checkExit = Invoke-PythonProcess `
    -Arguments $checkArguments `
    -StdoutPath $checkStdout `
    -StderrPath $checkStderr
if ($checkExit -ne 0) { throw "CHECKER_EXITED_NONZERO:$checkExit" }
$completed = Get-Date
$result = [ordered]@{
    schema_version = 1
    status = 'PROCESS_AND_CHECKER_COMPLETE'
    producer_exit_code = $runExit
    checker_exit_code = $checkExit
    started_at = $started.ToString('o')
    completed_at = $completed.ToString('o')
    wall_seconds = ($completed - $started).TotalSeconds
    producer_source_sha = $ProducerSourceSha
    runtime = $runtimeRoot
    final_decision_exists = Test-Path -LiteralPath (Join-Path $runtimeRoot 'final_decision.json')
    run_manifest_exists = Test-Path -LiteralPath (Join-Path $runtimeRoot 'run_manifest.json')
}
$result | ConvertTo-Json -Depth 5 | Set-Content `
    -LiteralPath (Join-Path $LogRoot 'wrapper_result.json') -Encoding UTF8
$result | ConvertTo-Json -Depth 5 | Set-Content `
    -LiteralPath (Join-Path $runtimeRoot 'pc2_wrapper_result.json') -Encoding UTF8
$result | ConvertTo-Json -Compress
