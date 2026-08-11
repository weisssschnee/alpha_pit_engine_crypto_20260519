param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$Python,
    [Parameter(Mandatory = $true)][string]$ProducerSourceSha,
    [Parameter(Mandatory = $true)][string]$RuntimeDate,
    [Parameter(Mandatory = $true)][string]$ReceiptRelativePath,
    [Parameter(Mandatory = $true)][string]$ReceiptBlobSha1,
    [Parameter(Mandatory = $true)][string]$ReceiptFileSha256,
    [Parameter(Mandatory = $true)][string]$DataRoot,
    [Parameter(Mandatory = $true)][string]$OiRoot,
    [Parameter(Mandatory = $true)][string]$PreviousExtended,
    [Parameter(Mandatory = $true)][string]$Classification,
    [Parameter(Mandatory = $true)][string]$AggBase,
    [Parameter(Mandatory = $true)][string]$BinanceProbe,
    [Parameter(Mandatory = $true)][string]$OpsRoot,
    [switch]$NativeInvocationSmokeOnly,
    [switch]$PreflightOnly
)

$ErrorActionPreference = 'Stop'
$runtime = Join-Path $RepoRoot "runtime\crypto_p4_mechanism_pocket_validation_v1_$RuntimeDate"
$statusPath = Join-Path $OpsRoot 'status.json'
$aggRoot = Join-Path $DataRoot 'aggtrades_20260801_20260809'
$top100Tar = Join-Path $aggRoot 'binance_aggtrades_top100_compact_1m_202608.tar'
$ranks101Tar = Join-Path $aggRoot 'binance_aggtrades_ranks101_200_compact_1m_202608.tar'
$started = [DateTimeOffset]::UtcNow

function Write-Status {
    param([string]$Status, [string]$Phase, [hashtable]$Extra = @{})
    $payload = [ordered]@{
        schema_version = 1
        status = $Status
        phase = $Phase
        producer_source_sha = $ProducerSourceSha
        runtime = $runtime
        data_root = $DataRoot
        updated_utc = [DateTimeOffset]::UtcNow.ToString('o')
        elapsed_seconds = ([DateTimeOffset]::UtcNow - $started).TotalSeconds
        reused_retained_oi_payload = $true
        oi_redownload_performed = $false
        candidate_generation_performed = $false
        optimizer_feedback_written = $false
        archive_written = $false
        oos_read_count = 0
        promotion_authorized = $false
        automatic_expansion = $false
    }
    foreach ($key in $Extra.Keys) { $payload[$key] = $Extra[$key] }
    $temporary = "$statusPath.tmp-$PID"
    [IO.File]::WriteAllText(
        $temporary,
        (($payload | ConvertTo-Json -Depth 10) + [Environment]::NewLine),
        [Text.UTF8Encoding]::new($false)
    )
    Move-Item -LiteralPath $temporary -Destination $statusPath -Force
}

function Convert-NativeArguments {
    param([string[]]$Arguments)
    return @($Arguments | ForEach-Object {
        $value = [string]$_
        if ($value -match '[\s"]') {
            return '"' + $value.Replace('"', '\"') + '"'
        }
        return $value
    })
}

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [int]$TimeoutSeconds = 0
    )
    $stdout = Join-Path $OpsRoot "$Name.stdout.log"
    $stderr = Join-Path $OpsRoot "$Name.stderr.log"
    $nativeArguments = Convert-NativeArguments -Arguments $Arguments
    $process = Start-Process -FilePath $Python -ArgumentList $nativeArguments `
        -WorkingDirectory $RepoRoot -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    if ($TimeoutSeconds -gt 0) {
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
            & taskkill.exe /PID $process.Id /T /F | Out-Null
            throw "$Name exceeded frozen wall limit $TimeoutSeconds"
        }
    } else {
        $process.WaitForExit()
    }
    # Complete the asynchronous redirected-stream drain before ExitCode access.
    $process.WaitForExit()
    if (-not $process.HasExited) { throw "$Name process did not reach terminal state" }
    try { $nativeExitCode = [int]$process.ExitCode }
    catch { throw "$Name native exit code unavailable after terminal wait" }
    if ($nativeExitCode -ne 0) {
        $tail = if (Test-Path -LiteralPath $stderr) {
            (Get-Content -LiteralPath $stderr -Tail 30) -join ' | '
        } else { 'stderr missing' }
        throw "$Name failed exit=$nativeExitCode`: $tail"
    }
    return $nativeExitCode
}

function Invoke-NativeSmoke {
    $smokeRoot = Join-Path $OpsRoot 'native_invocation_smoke'
    New-Item -ItemType Directory -Force -Path $smokeRoot | Out-Null
    $script = Join-Path $smokeRoot 'native_exit_smoke.py'
    [IO.File]::WriteAllText(
        $script,
        "import sys`nprint(sys.argv[1])`nprint('stderr-smoke', file=sys.stderr)`nsys.exit(int(sys.argv[2]))`n",
        [Text.UTF8Encoding]::new($false)
    )
    $zero = Invoke-Native 'native_zero_smoke' @($script, 'multi word argument', '0')
    $failureStdout = Join-Path $OpsRoot 'native_nonzero_smoke.stdout.log'
    $failureStderr = Join-Path $OpsRoot 'native_nonzero_smoke.stderr.log'
    $nativeArguments = Convert-NativeArguments -Arguments @($script, 'multi word argument', '7')
    $process = Start-Process -FilePath $Python -ArgumentList $nativeArguments `
        -WorkingDirectory $RepoRoot -WindowStyle Hidden -Wait -PassThru `
        -RedirectStandardOutput $failureStdout -RedirectStandardError $failureStderr
    $nonzero = [int]$process.ExitCode
    if ($zero -ne 0 -or $nonzero -ne 7) { throw 'NATIVE_EXIT_CODE_SMOKE_FAILED' }
    [ordered]@{ status='PASS'; zero_exit=$zero; nonzero_exit=$nonzero } | ConvertTo-Json `
        | Set-Content -LiteralPath (Join-Path $smokeRoot 'result.json') -Encoding UTF8
}

try {
    New-Item -ItemType Directory -Force -Path $OpsRoot | Out-Null
    Invoke-NativeSmoke
    if ($NativeInvocationSmokeOnly) { exit 0 }

    $required = @(
        $RepoRoot, $Python, $OiRoot, $PreviousExtended, $Classification,
        $AggBase, $BinanceProbe, (Join-Path $RepoRoot $ReceiptRelativePath)
    )
    $missing = @($required | Where-Object { -not (Test-Path -LiteralPath $_) })
    if ($missing.Count) { throw "required inputs missing: $($missing -join ',')" }
    $head = (& git -C $RepoRoot rev-parse HEAD | Out-String).Trim().ToLowerInvariant()
    if ($head -ne $ProducerSourceSha.ToLowerInvariant()) { throw 'producer SHA changed' }
    if (@(& git -C $RepoRoot status --porcelain).Count -ne 0) { throw 'producer worktree dirty' }
    $observedBlob = (& git -C $RepoRoot rev-parse "HEAD:$ReceiptRelativePath" | Out-String).Trim()
    if ($observedBlob -ne $ReceiptBlobSha1) { throw 'receipt blob changed' }
    if ((Get-FileHash -LiteralPath (Join-Path $RepoRoot $ReceiptRelativePath) -Algorithm SHA256).Hash -ne $ReceiptFileSha256) { throw 'receipt file hash changed' }
    if (Test-Path -LiteralPath $aggRoot) { throw 'aggTrades acquisition root already exists' }
    if (Test-Path -LiteralPath $runtime) { throw 'replacement runtime already exists' }
    if (@(Get-Process -Name python -ErrorAction SilentlyContinue).Count -ne 0) { throw 'another Python workload is active' }
    if ((Get-PSDrive C).Free -lt 100GB) { throw 'C drive free space below 100 GiB' }
    $probe = Get-Content -LiteralPath $BinanceProbe -Raw | ConvertFrom-Json
    if ($probe.status -ne 'PASS_SOURCE_METADATA_AVAILABILITY' -or [int]$probe.available_count -ne 27) { throw 'Binance source probe failed' }
    if ((Get-FileHash -LiteralPath $AggBase -Algorithm SHA256).Hash -ne '67355B7B5B8D34E6039733B4CA23116F1D9B6B4FBB6A69253F13B82DEF3A982F') { throw 'aggTrades base module changed' }
    if ((Get-FileHash -LiteralPath $Classification -Algorithm SHA256).Hash -ne 'B4BB2C7C8465AFA5B447554695DA7C036B5CF15B03420E47C6DDFF43D7A96BC6') { throw 'classification changed' }
    $env:PYTHONPATH = $RepoRoot
    Invoke-Native 'receipt_smoke' @('-c', "from pathlib import Path; from alphafactory_crypto.broad_search.p4_mechanism_pocket_validation_v1 import load_receipt; load_receipt(Path(r'$RepoRoot'), require_authorized=True, receipt_path=r'$ReceiptRelativePath'); print('RECEIPT_OK')")
    if ($PreflightOnly) {
        Write-Status 'PREFLIGHT_PASS' 'TERMINAL' @{ native_exit_smoke='PASS'; active_python_count=0 }
        exit 0
    }

    Write-Status 'RUNNING' 'AGGTRADES_ACQUISITION' @{ download_workers=3; network_concurrency_cap=3; oi_completed_days=27 }
    Invoke-Native 'aggtrades_acquisition' @(
        (Join-Path $RepoRoot 'scripts\acquire_binance_daily_aggtrades_compact_v1.py'),
        $AggBase, $Classification, $aggRoot,
        '--start', '2026-08-01', '--end-exclusive', '2026-08-10', '--workers', '3'
    )
    $agg = Get-Content -LiteralPath (Join-Path $aggRoot 'status.json') -Raw | ConvertFrom-Json
    if ($agg.status -ne 'complete' -or [int]$agg.failure_count -ne 0 -or [int]$agg.completed_symbols -ne 200 -or -not (Test-Path $top100Tar) -or -not (Test-Path $ranks101Tar)) { throw 'aggTrades acquisition failed' }

    Write-Status 'RUNNING' 'CARRIER_PREPARATION' @{ agg_completed_symbols=200; agg_failure_count=0 }
    Invoke-Native 'prepare_carrier' @(
        '-m', 'alphafactory_crypto.broad_search.p4_mechanism_pocket_validation_v1',
        'prepare-carrier', '--repo-root', $RepoRoot, '--runtime-date', $RuntimeDate,
        '--receipt-path', $ReceiptRelativePath, '--new-oi-source-root', $OiRoot,
        '--previous-extended-cache', $PreviousExtended, '--top100-tar', $top100Tar,
        '--ranks101-200-tar', $ranks101Tar
    )
    $carrier = Get-Content -LiteralPath (Join-Path $runtime 'aligned_carrier_manifest.json') -Raw | ConvertFrom-Json
    if ($carrier.status -ne 'P4_POCKET_CARRIER_READY' -or [int]$carrier.field_count -ne 115 -or $carrier.retained_oi_payload.status -ne 'RETAINED_OI_PAYLOAD_REVERIFIED') { throw 'carrier preparation failed' }

    Write-Status 'RUNNING' 'P4_POCKET_GATE' @{ candidate_count=80; workers=10; memory_fallback_workers=8; wall_limit_seconds=3600; carrier_identity_sha256=$carrier.extended_aligned_cache.identity_sha256; target_identity_sha256=$carrier.target_cache.identity_sha256 }
    Invoke-Native 'candidate_gate' @(
        '-m', 'alphafactory_crypto.broad_search.p4_mechanism_pocket_validation_v1',
        'run', '--repo-root', $RepoRoot, '--runtime-date', $RuntimeDate,
        '--receipt-path', $ReceiptRelativePath
    ) 3600
    Invoke-Native 'independent_checker' @(
        '-m', 'alphafactory_crypto.broad_search.p4_mechanism_pocket_validation_v1',
        'check', '--repo-root', $RepoRoot, '--runtime-date', $RuntimeDate,
        '--receipt-path', $ReceiptRelativePath
    )
    $manifest = Get-Content -LiteralPath (Join-Path $runtime 'run_manifest.json') -Raw | ConvertFrom-Json
    $checker = Get-Content -LiteralPath (Join-Path $runtime 'independent_checker.json') -Raw | ConvertFrom-Json
    if ($checker.status -ne 'PASS') { throw 'independent checker failed' }
    Write-Status 'COMPLETE' 'TERMINAL' @{ research_result=$manifest.research_result; strict_evaluated_count=[int]$manifest.strict_evaluated_count; candidate_local_failure_count=[int]$manifest.candidate_local_failure_count; pair_evaluated_per_hour=[double]$manifest.pair_evaluated_per_hour; independent_checker=$checker.status }
    exit 0
} catch {
    Write-Status 'FAILED' 'TERMINAL' @{ error=$_.Exception.Message; script_stack=$_.ScriptStackTrace; replacement_run_terminal=$true; no_second_replacement=$true }
    exit 1
}
