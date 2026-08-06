param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$Python,
    [Parameter(Mandatory = $true)][string]$PythonOverlay,
    [Parameter(Mandatory = $true)][string]$BaseWorkspace,
    [Parameter(Mandatory = $true)][string]$ProducerSourceSha,
    [Parameter(Mandatory = $true)][string]$RuntimeDate,
    [Parameter(Mandatory = $true)][string]$ReceiptRelativePath,
    [Parameter(Mandatory = $true)][string]$ReceiptBlobSha1,
    [Parameter(Mandatory = $true)][string]$ResolvedReceiptSha256,
    [Parameter(Mandatory = $true)][string]$LogRoot,
    [switch]$PreflightOnly,
    [switch]$NativeInvocationSmokeOnly
)

$ErrorActionPreference = 'Stop'
if (Test-Path variable:PSNativeCommandUseErrorActionPreference) {
    $PSNativeCommandUseErrorActionPreference = $false
}

function Invoke-PythonProcess {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][string]$StdoutPath,
        [Parameter(Mandatory = $true)][string]$StderrPath
    )

    $process = Start-Process -FilePath $Python -ArgumentList $Arguments `
        -WorkingDirectory $WorkingDirectory -WindowStyle Hidden -Wait -PassThru `
        -RedirectStandardOutput $StdoutPath -RedirectStandardError $StderrPath
    return $process.ExitCode
}

if ($NativeInvocationSmokeOnly) {
    if (Test-Path -LiteralPath $LogRoot) {
        throw 'NATIVE_SMOKE_LOG_ROOT_ALREADY_EXISTS'
    }
    New-Item -ItemType Directory -Path $LogRoot | Out-Null
    $smokeScript = Join-Path $LogRoot 'native_stderr_smoke.py'
    $smokeStdout = Join-Path $LogRoot 'native_stderr_smoke.stdout.log'
    $smokeStderr = Join-Path $LogRoot 'native_stderr_smoke.stderr.log'
    $smokeSource = @'
import warnings
warnings.warn("native-stderr-smoke", RuntimeWarning)
print("NATIVE_STDOUT_OK")
'@
    [IO.File]::WriteAllText(
        $smokeScript,
        $smokeSource,
        [Text.UTF8Encoding]::new($false)
    )
    $smokeExitCode = Invoke-PythonProcess `
        -Arguments @($smokeScript) `
        -WorkingDirectory $RepoRoot `
        -StdoutPath $smokeStdout `
        -StderrPath $smokeStderr
    if ($smokeExitCode -ne 0) { throw "NATIVE_SMOKE_EXITED_NONZERO:$smokeExitCode" }
    if ((Get-Content -LiteralPath $smokeStdout -Raw) -notmatch 'NATIVE_STDOUT_OK') {
        throw 'NATIVE_SMOKE_STDOUT_MISSING'
    }
    if ((Get-Content -LiteralPath $smokeStderr -Raw) -notmatch 'native-stderr-smoke') {
        throw 'NATIVE_SMOKE_STDERR_WARNING_MISSING'
    }
    [ordered]@{
        status = 'NATIVE_STDERR_SMOKE_PASS'
        exit_code = $smokeExitCode
        stderr_is_diagnostic_only = $true
        runtime_created = Test-Path -LiteralPath (
            Join-Path $RepoRoot "runtime\crypto_search_replication_aware_gate_v1_$RuntimeDate"
        )
        producer_source_sha = $ProducerSourceSha
    } | ConvertTo-Json -Compress | Set-Content `
        -LiteralPath (Join-Path $LogRoot 'native_stderr_smoke_result.json') `
        -Encoding UTF8
    Get-Content -LiteralPath (Join-Path $LogRoot 'native_stderr_smoke_result.json')
    return
}

$runtimeRoot = Join-Path $RepoRoot (
    "runtime\crypto_search_replication_aware_gate_v1_$RuntimeDate"
)
$receiptPath = Join-Path $RepoRoot $ReceiptRelativePath
$requiredPaths = @($RepoRoot, $Python, $PythonOverlay, $BaseWorkspace, $receiptPath)
foreach ($requiredPath in $requiredPaths) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "LAUNCH_REQUIRED_PATH_MISSING:$requiredPath"
    }
}
if (Test-Path -LiteralPath $LogRoot) { throw 'LAUNCH_LOG_ROOT_ALREADY_EXISTS' }
if (Test-Path -LiteralPath $runtimeRoot) { throw 'LAUNCH_RUNTIME_ALREADY_EXISTS' }

$head = (& git -C $RepoRoot rev-parse HEAD | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $head -ne $ProducerSourceSha) {
    throw 'LAUNCH_SOURCE_SHA_MISMATCH'
}
if (@(& git -C $RepoRoot status --porcelain).Count -ne 0) {
    throw 'LAUNCH_WORKTREE_NOT_CLEAN'
}
$observedReceiptBlobSha1 = (
    & git -C $RepoRoot rev-parse "HEAD:$ReceiptRelativePath" | Out-String
).Trim()
if ($LASTEXITCODE -ne 0 -or $observedReceiptBlobSha1 -ne $ReceiptBlobSha1) {
    throw 'LAUNCH_RECEIPT_BLOB_MISMATCH'
}

$cache = Get-Item -LiteralPath (Join-Path $RepoRoot '.cache') -Force
if ($cache.LinkType -ne 'Junction') { throw 'LAUNCH_CACHE_NOT_JUNCTION' }
$runtimeParent = Join-Path $RepoRoot 'runtime'
New-Item -ItemType Directory -Path $runtimeParent -Force | Out-Null
foreach ($name in @(
    'crypto_search_mechanism_v2_20260801',
    'crypto_search_engine_v1_4_oi_flow_20260728'
)) {
    $source = Join-Path (Join-Path $BaseWorkspace 'runtime') $name
    $destination = Join-Path $runtimeParent $name
    if (-not (Test-Path -LiteralPath $source)) {
        throw "LAUNCH_READ_ONLY_RUNTIME_SOURCE_MISSING:$name"
    }
    if (-not (Test-Path -LiteralPath $destination)) {
        New-Item -ItemType Junction -Path $destination -Target $source | Out-Null
    }
    $item = Get-Item -LiteralPath $destination -Force
    if ($item.LinkType -ne 'Junction' -or @($item.Target) -notcontains $source) {
        throw "LAUNCH_READ_ONLY_RUNTIME_JUNCTION_MISMATCH:$name"
    }
}

$env:PYTHONPATH = "$RepoRoot;$PythonOverlay"
$probeRoot = Join-Path ([IO.Path]::GetTempPath()) (
    'crypto-replication-r2-probe-' + [Guid]::NewGuid().ToString('N')
)
New-Item -ItemType Directory -Path $probeRoot | Out-Null
try {
    $probeScript = Join-Path $probeRoot 'receipt_probe.py'
    $probeStdout = Join-Path $probeRoot 'receipt_probe.stdout.log'
    $probeStderr = Join-Path $probeRoot 'receipt_probe.stderr.log'
    $probeSource = @"
from pathlib import Path
from alphafactory_crypto.broad_search.experiment_authority import resolve_search_economic_receipt
r = resolve_search_economic_receipt(Path.cwd(), '$ReceiptRelativePath')
assert r['result'] == 'RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT'
assert r['run_authorized'] is True
assert r['search_campaign']['runtime_date'] == '$RuntimeDate'
assert r['search_campaign']['strict_evaluated_target'] == 1536
assert r['validation']['role'] == 'NOT_AUTHORIZED'
assert r['holdout']['read_allowed'] is False
print(r['receipt_sha256'])
"@
    [IO.File]::WriteAllText(
        $probeScript,
        $probeSource,
        [Text.UTF8Encoding]::new($false)
    )
    $probeExitCode = Invoke-PythonProcess `
        -Arguments @($probeScript) `
        -WorkingDirectory $RepoRoot `
        -StdoutPath $probeStdout `
        -StderrPath $probeStderr
    $observedResolvedReceiptSha256 = (Get-Content -LiteralPath $probeStdout -Raw).Trim()
    if ($probeExitCode -ne 0 -or $observedResolvedReceiptSha256 -ne $ResolvedReceiptSha256) {
        throw 'LAUNCH_RESOLVED_RECEIPT_HASH_MISMATCH'
    }
} finally {
    Remove-Item -LiteralPath $probeRoot -Recurse -Force
}

$activePython = @(Get-Process -Name python -ErrorAction SilentlyContinue)
if ($activePython.Count -ne 0) { throw 'ANOTHER_PYTHON_WORKLOAD_IS_ACTIVE' }
$operatingSystem = Get-CimInstance Win32_OperatingSystem
$freeMemoryGiB = ($operatingSystem.FreePhysicalMemory * 1KB) / 1GB
if ($freeMemoryGiB -lt 12.0) { throw 'LAUNCH_FREE_MEMORY_BELOW_12_GIB' }

if ($PreflightOnly) {
    [ordered]@{
        status = 'LAUNCH_PREFLIGHT_ONLY_PASS'
        producer_sha = $head
        receipt_blob_sha1 = $observedReceiptBlobSha1
        resolved_receipt_sha256 = $observedResolvedReceiptSha256
        runtime_absent = -not (Test-Path -LiteralPath $runtimeRoot)
        log_root_absent = -not (Test-Path -LiteralPath $LogRoot)
        active_python_count = $activePython.Count
        free_memory_gib = [math]::Round($freeMemoryGiB, 3)
        workers_default = 10
        workers_memory_fallback = 8
        workers_12_forbidden = $true
    } | ConvertTo-Json -Compress
    return
}

New-Item -ItemType Directory -Path $LogRoot | Out-Null
$stdoutPath = Join-Path $LogRoot 'producer.stdout.log'
$stderrPath = Join-Path $LogRoot 'producer.stderr.log'
$resultPath = Join-Path $LogRoot 'wrapper_result.json'
$arguments = @(
    '-m', 'alphafactory_crypto.broad_search.search_engine_v1',
    'run-replication-aware-v1',
    '--runtime-date', $RuntimeDate,
    '--source-sha', $ProducerSourceSha,
    '--evidence-to-add',
    'equal-count development-block replication productivity and migration-ranking evidence',
    '--decision-to-change',
    'whether replication-aware Evolution replaces current development selection authority'
)
[ordered]@{
    status = 'LAUNCH_FROZEN'
    started_utc = [DateTime]::UtcNow.ToString('o')
    workspace = $RepoRoot
    runtime = $runtimeRoot
    producer_sha = $ProducerSourceSha
    receipt_path = $ReceiptRelativePath
    receipt_blob_sha1 = $observedReceiptBlobSha1
    resolved_receipt_sha256 = $observedResolvedReceiptSha256
    workers_default = 10
    workers_memory_fallback = 8
    workers_12_forbidden = $true
    strict_target = 1536
    raw_attempt_limit = 9600
    wall_time_seconds_limit = 10800
    required_pairs_per_hour = 512.0
    validation_oos_holdout_forbidden = $true
    arguments = $arguments
} | ConvertTo-Json -Depth 6 | Set-Content `
    -LiteralPath (Join-Path $LogRoot 'launch_manifest.json') -Encoding UTF8

$env:NUMEXPR_MAX_THREADS = '4'
$env:OMP_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$started = Get-Date
$exitCode = Invoke-PythonProcess `
    -Arguments $arguments `
    -WorkingDirectory $RepoRoot `
    -StdoutPath $stdoutPath `
    -StderrPath $stderrPath
$completed = Get-Date
$result = [ordered]@{
    schema_version = 1
    status = if ($exitCode -eq 0) { 'PROCESS_COMPLETE' } else { 'PROCESS_FAILED' }
    exit_code = $exitCode
    started_at = $started.ToString('o')
    completed_at = $completed.ToString('o')
    wall_seconds = ($completed - $started).TotalSeconds
    producer_source_sha = $ProducerSourceSha
    runtime = $runtimeRoot
    receipt_path = $ReceiptRelativePath
    stdout_path = $stdoutPath
    stderr_path = $stderrPath
    stderr_is_diagnostic_only = $true
    native_exit_code_is_terminal_authority = $true
    final_decision_exists = Test-Path -LiteralPath (Join-Path $runtimeRoot 'final_decision.json')
    run_manifest_exists = Test-Path -LiteralPath (Join-Path $runtimeRoot 'run_manifest.json')
}
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $resultPath -Encoding UTF8
if (Test-Path -LiteralPath $runtimeRoot) {
    $result | ConvertTo-Json -Depth 5 | Set-Content `
        -LiteralPath (Join-Path $runtimeRoot 'pc2_wrapper_result.json') -Encoding UTF8
}
if ($exitCode -ne 0) { throw "PRODUCER_EXITED_NONZERO:$exitCode" }
