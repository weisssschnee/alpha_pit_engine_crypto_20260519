param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$Python,
    [Parameter(Mandatory = $true)][string]$PythonOverlay,
    [Parameter(Mandatory = $true)][string]$ProducerSourceSha,
    [Parameter(Mandatory = $true)][string]$RuntimeDate,
    [Parameter(Mandatory = $true)][string]$ReceiptPath,
    [Parameter(Mandatory = $true)][string]$LogRoot
)

$ErrorActionPreference = 'Stop'
$runtimeRoot = Join-Path $RepoRoot "runtime\crypto_search_evidence_v1_1_validation_$RuntimeDate"
if (Test-Path -LiteralPath $runtimeRoot) {
    throw 'EVIDENCE_VALIDATION_REPLACEMENT_RUNTIME_ALREADY_EXISTS'
}
New-Item -ItemType Directory -Path $LogRoot -Force | Out-Null
$stdoutPath = Join-Path $LogRoot 'producer.stdout.log'
$stderrPath = Join-Path $LogRoot 'producer.stderr.log'
$resultPath = Join-Path $LogRoot 'wrapper_result.json'

$env:PYTHONPATH = "$RepoRoot;$PythonOverlay"
$arguments = @(
    '-m',
    'alphafactory_crypto.broad_search.search_evidence_validation_v1',
    'run',
    '--repo-root', $RepoRoot,
    '--runtime-date', $RuntimeDate,
    '--producer-source-sha', $ProducerSourceSha,
    '--receipt-path', $ReceiptPath
)
$started = Get-Date
$process = Start-Process -FilePath $Python -ArgumentList $arguments `
    -WorkingDirectory $RepoRoot -WindowStyle Hidden -Wait -PassThru `
    -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
$completed = Get-Date
$result = [ordered]@{
    schema_version = 1
    status = if ($process.ExitCode -eq 0) { 'PROCESS_COMPLETE' } else { 'PROCESS_FAILED' }
    exit_code = $process.ExitCode
    started_at = $started.ToString('o')
    completed_at = $completed.ToString('o')
    wall_seconds = ($completed - $started).TotalSeconds
    producer_source_sha = $ProducerSourceSha
    runtime = $runtimeRoot
    receipt_path = $ReceiptPath
    stdout_path = $stdoutPath
    stderr_path = $stderrPath
    stderr_is_diagnostic_only = $true
    native_exit_code_is_terminal_authority = $true
    final_decision_exists = Test-Path -LiteralPath (Join-Path $runtimeRoot 'final_decision.json')
    run_manifest_exists = Test-Path -LiteralPath (Join-Path $runtimeRoot 'run_manifest.json')
}
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $resultPath -Encoding UTF8
if (Test-Path -LiteralPath $runtimeRoot) {
    $result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $runtimeRoot 'pc2_wrapper_result.json') -Encoding UTF8
}
exit $process.ExitCode
