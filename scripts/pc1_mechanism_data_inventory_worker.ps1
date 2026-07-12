param(
    [string]$JobId = "mechanism_inventory_20260712_1747",
    [string]$Python = "D:\HermesWorker\workspace\.venv\Scripts\python.exe",
    [string]$Scanner = "H:\CodexRuntime\crypto_mechanism_data_inventory.py",
    [string]$DataRoot = "D:\HermesWorker\GDrive\AlphaFactory_CryptoData",
    [string]$OutputRoot = "H:\CodexRuntime\mechanism_data_expansion0_inventory_20260712\pc1"
)

$ErrorActionPreference = "Stop"
$started = Get-Date
$runRoot = Split-Path -Parent $OutputRoot
$log = Join-Path $runRoot "pc1.log"
$status = Join-Path $runRoot "pc1.status.json"
$exitCode = 0

New-Item -ItemType Directory -Force -Path $OutputRoot | Out-Null

try {
    & $Python $Scanner --root $DataRoot --output $OutputRoot --metadata-samples-per-dataset 3 *>> $log
    $exitCode = $LASTEXITCODE
} catch {
    $_ | Out-String | Add-Content -Path $log
    $exitCode = 1
}

@{
    task_id = $JobId
    started_at = $started.ToString("s")
    ended_at = (Get-Date).ToString("s")
    exit_code = $exitCode
    log = $log
    output_root = $OutputRoot
    data_root = $DataRoot
} | ConvertTo-Json | Set-Content -Path $status -Encoding UTF8

exit $exitCode
