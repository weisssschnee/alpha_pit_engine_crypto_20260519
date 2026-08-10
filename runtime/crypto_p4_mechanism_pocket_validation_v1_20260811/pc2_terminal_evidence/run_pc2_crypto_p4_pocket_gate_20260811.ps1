$ErrorActionPreference = "Stop"
$Workspace = "C:\HermesWorker\workspace\crypto_p4_pocket_validation_5179bd28"
$Python = "D:\HermesWorker\workspace\crypto_line\.venv_b251733\Scripts\python.exe"
$ProducerSha = "5179bd2875d4bad56c02919bf774ddc7483ee984"
$Runtime = Join-Path $Workspace "runtime\crypto_p4_mechanism_pocket_validation_v1_20260811"
$OpsRoot = "C:\HermesWorker\runtime\crypto_p4_pocket_validation_20260811"
$StatusPath = Join-Path $OpsRoot "status.json"
$DataRoot = "C:\HermesWorker\data\crypto_p4_pocket_validation_20260811"
$OiRoot = Join-Path $DataRoot "oi_mark_compact_20260801_20260809"
$AggRoot = Join-Path $DataRoot "aggtrades_20260801_20260809"
$Top100Tar = Join-Path $AggRoot "binance_aggtrades_top100_compact_1m_202608.tar"
$Ranks101Tar = Join-Path $AggRoot "binance_aggtrades_ranks101_200_compact_1m_202608.tar"
$PreviousExtended = "C:\HermesWorker\workspace\crypto_family_consensus_d3dd6184\.cache\crypto_search_family_consensus_dev_v1\aligned_extended_to_20260801"
$FrozenOiAcquire = "C:\HermesWorker\runtime\crypto_family_consensus_frozen_oi_acquire_20260805.py"
$OiDownloader = "D:\HermesWorker\runtime\cryptohft_crossvenue_oi_mark_compact_ranks51_200_pc2_20260720.py"
$KeyPath = "D:\HermesWorker\runtime\secrets\cryptohftdata_api_key.txt"
$Classification = "D:\HermesWorker\runtime\binance_universe498_symbol_classification_20260526.csv"
$FrozenMap = "C:\HermesWorker\runtime\crypto_family_consensus_frozen_symbol_map_20260805.json"
$AggBase = "D:\HermesWorker\runtime\binance_vision_aggtrades_top100_compact_1m_pc2_20260721.py"
$OiProbe = "C:\HermesWorker\runtime\crypto_p4_pocket_oi_source_probe_20260811.json"
$BinanceProbe = "C:\HermesWorker\runtime\crypto_p4_pocket_binance_source_probe_20260811.json"
$Started = [DateTimeOffset]::UtcNow

New-Item -ItemType Directory -Force -Path $OpsRoot | Out-Null

function Write-Status {
    param([string]$Status, [string]$Phase, [hashtable]$Extra = @{})
    $payload = [ordered]@{
        schema_version = 1
        status = $Status
        phase = $Phase
        producer_source_sha = $ProducerSha
        workspace = $Workspace
        runtime = $Runtime
        data_root = $DataRoot
        updated_utc = [DateTimeOffset]::UtcNow.ToString("o")
        elapsed_seconds = ([DateTimeOffset]::UtcNow - $Started).TotalSeconds
        candidate_generation_performed = $false
        optimizer_feedback_written = $false
        archive_written = $false
        oos_read_count = 0
        promotion_authorized = $false
        automatic_expansion = $false
    }
    foreach ($key in $Extra.Keys) { $payload[$key] = $Extra[$key] }
    $temporary = "$StatusPath.tmp-$PID"
    [IO.File]::WriteAllText($temporary, (($payload | ConvertTo-Json -Depth 10) + [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporary -Destination $StatusPath -Force
}

function Invoke-Native {
    param([string]$Name, [string[]]$Arguments, [int]$TimeoutSeconds = 0)
    $stdout = Join-Path $OpsRoot "$Name.stdout.log"
    $stderr = Join-Path $OpsRoot "$Name.stderr.log"
    $process = Start-Process -FilePath $Python -ArgumentList $Arguments -WorkingDirectory $Workspace -WindowStyle Hidden -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    if ($TimeoutSeconds -gt 0) {
        try { Wait-Process -Id $process.Id -Timeout $TimeoutSeconds -ErrorAction Stop }
        catch {
            & taskkill.exe /PID $process.Id /T /F | Out-Null
            throw "$Name exceeded frozen wall limit $TimeoutSeconds"
        }
    } else { $process.WaitForExit() }
    $process.Refresh()
    if ($process.ExitCode -ne 0) {
        $tail = if (Test-Path -LiteralPath $stderr) { (Get-Content -LiteralPath $stderr -Tail 30) -join " | " } else { "stderr missing" }
        throw "$Name failed exit=$($process.ExitCode): $tail"
    }
}

try {
    $required = @($Workspace,$Python,$Runtime,$PreviousExtended,$FrozenOiAcquire,$OiDownloader,$KeyPath,$Classification,$FrozenMap,$AggBase,$OiProbe,$BinanceProbe)
    $missing = @($required | Where-Object { -not (Test-Path -LiteralPath $_) })
    if ($missing.Count) { throw "required inputs missing: $($missing -join ',')" }
    if ((git -C $Workspace rev-parse HEAD).Trim() -ne $ProducerSha) { throw "producer SHA changed" }
    if (@(git -C $Workspace status --porcelain).Count -ne 0) { throw "producer worktree dirty" }
    if (Test-Path -LiteralPath $DataRoot) { throw "fresh data root already exists" }
    if (Test-Path -LiteralPath (Join-Path $Runtime "run_manifest.json")) { throw "gate already terminal" }
    $oiProbePayload = Get-Content -LiteralPath $OiProbe -Raw | ConvertFrom-Json
    $binanceProbePayload = Get-Content -LiteralPath $BinanceProbe -Raw | ConvertFrom-Json
    if ($oiProbePayload.status -ne "PASS_SOURCE_METADATA_COVERAGE" -or [int]$oiProbePayload.minimum_hourly_common_base_support -lt 68) { throw "OI source probe failed" }
    if ($binanceProbePayload.status -ne "PASS_SOURCE_METADATA_AVAILABILITY" -or [int]$binanceProbePayload.available_count -ne 27) { throw "Binance source probe failed" }
    if ((Get-FileHash -LiteralPath $AggBase -Algorithm SHA256).Hash -ne "67355B7B5B8D34E6039733B4CA23116F1D9B6B4FBB6A69253F13B82DEF3A982F") { throw "aggTrades base module changed" }
    if ((Get-FileHash -LiteralPath $Classification -Algorithm SHA256).Hash -ne "B4BB2C7C8465AFA5B447554695DA7C036B5CF15B03420E47C6DDFF43D7A96BC6") { throw "classification changed" }
    $cFree = (Get-PSDrive C).Free
    $memoryFree = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory * 1KB
    if ($cFree -lt 120GB -or $memoryFree -lt 8GB) { throw "resource preflight failed" }

    New-Item -ItemType Directory -Force -Path $DataRoot | Out-Null
    Write-Status "RUNNING" "OI_MARK_ACQUISITION" @{ c_free_gib=[math]::Round($cFree/1GB,2); memory_free_gib=[math]::Round($memoryFree/1GB,2); day_workers=3; object_workers=12 }
    $env:CRYPTOHFT_COMPACT_START_DATE = "2026-08-01"
    $env:CRYPTOHFT_COMPACT_END_DATE = "2026-08-09"
    $env:CRYPTOHFT_COMPACT_DAY_WORKERS = "3"
    $env:CRYPTOHFT_COMPACT_OBJECT_WORKERS = "12"
    Invoke-Native "oi_acquisition" @($FrozenOiAcquire,$OiDownloader,$KeyPath,$Classification,$FrozenMap,$OiRoot)
    $oi = Get-Content -LiteralPath (Join-Path $OiRoot "status.json") -Raw | ConvertFrom-Json
    $mapProof = Get-Content -LiteralPath (Join-Path $OiRoot "frozen_symbol_map_proof.json") -Raw | ConvertFrom-Json
    if ($oi.status -ne "complete" -or [int]$oi.failure_count -ne 0 -or [int]$oi.total_days -ne 27 -or [int]$oi.completed_days -ne 27 -or $mapProof.mapping_exact_match -ne $true) { throw "OI acquisition failed" }

    Write-Status "RUNNING" "AGGTRADES_ACQUISITION" @{ oi_completed_days=27; download_workers=3; network_concurrency_cap=3 }
    Invoke-Native "aggtrades_acquisition" @((Join-Path $Workspace "scripts\acquire_binance_daily_aggtrades_compact_v1.py"),$AggBase,$Classification,$AggRoot,"--start","2026-08-01","--end-exclusive","2026-08-10","--workers","3")
    $agg = Get-Content -LiteralPath (Join-Path $AggRoot "status.json") -Raw | ConvertFrom-Json
    if ($agg.status -ne "complete" -or [int]$agg.failure_count -ne 0 -or [int]$agg.completed_symbols -ne 200 -or -not (Test-Path -LiteralPath $Top100Tar) -or -not (Test-Path -LiteralPath $Ranks101Tar)) { throw "aggTrades acquisition failed" }

    Write-Status "RUNNING" "CARRIER_PREPARATION" @{ oi_completed_days=27; agg_completed_symbols=200; agg_failure_count=0 }
    Invoke-Native "prepare_carrier" @("-m","alphafactory_crypto.broad_search.p4_mechanism_pocket_validation_v1","prepare-carrier","--repo-root",$Workspace,"--runtime-date","20260811","--new-oi-source-root",$OiRoot,"--previous-extended-cache",$PreviousExtended,"--top100-tar",$Top100Tar,"--ranks101-200-tar",$Ranks101Tar)
    $carrier = Get-Content -LiteralPath (Join-Path $Runtime "aligned_carrier_manifest.json") -Raw | ConvertFrom-Json
    if ($carrier.status -ne "P4_POCKET_CARRIER_READY" -or [int]$carrier.field_count -ne 115) { throw "carrier preparation failed" }

    $memoryFree = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory * 1KB
    if ($memoryFree -lt 8GB) { throw "pre-gate memory floor failed" }
    Write-Status "RUNNING" "P4_POCKET_GATE" @{ candidate_count=80; workers=10; memory_fallback_workers=8; wall_limit_seconds=3600; carrier_identity_sha256=$carrier.extended_aligned_cache.identity_sha256; target_identity_sha256=$carrier.target_cache.identity_sha256 }
    Invoke-Native "candidate_gate" @("-m","alphafactory_crypto.broad_search.p4_mechanism_pocket_validation_v1","run","--repo-root",$Workspace,"--runtime-date","20260811") 3600
    Invoke-Native "independent_checker" @("-m","alphafactory_crypto.broad_search.p4_mechanism_pocket_validation_v1","check","--repo-root",$Workspace,"--runtime-date","20260811")
    $manifest = Get-Content -LiteralPath (Join-Path $Runtime "run_manifest.json") -Raw | ConvertFrom-Json
    $checker = Get-Content -LiteralPath (Join-Path $Runtime "independent_checker.json") -Raw | ConvertFrom-Json
    if ($checker.status -ne "PASS") { throw "independent checker failed" }
    Write-Status "COMPLETE" "TERMINAL" @{ research_result=$manifest.research_result; strict_evaluated_count=[int]$manifest.strict_evaluated_count; candidate_local_failure_count=[int]$manifest.candidate_local_failure_count; pair_evaluated_per_hour=[double]$manifest.pair_evaluated_per_hour; workers=[int]$manifest.workers; independent_checker=$checker.status }
    exit 0
} catch {
    Write-Status "FAILED" "TERMINAL" @{ error=$_.Exception.Message; script_stack=$_.ScriptStackTrace; no_second_run=$true }
    exit 1
}
