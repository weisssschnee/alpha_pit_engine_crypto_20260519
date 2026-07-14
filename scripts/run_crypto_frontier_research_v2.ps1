param(
    [ValidateSet("prepare", "run", "seal", "check")]
    [string]$Command = "run"
)

$ErrorActionPreference = "Continue"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$RunRoot = Join-Path $RepoRoot "runtime\crypto_frontier_research_v2_20260713"
$Python = "G:\PythonProject\.venv\Scripts\python.exe"
$Prefix = if ($Command -eq "run") { "runner" } else { "runner.$Command" }
$Stdout = Join-Path $RunRoot "$Prefix.stdout.log"
$Stderr = Join-Path $RunRoot "$Prefix.stderr.log"
$Status = Join-Path $RunRoot "$Prefix.status.json"
$Started = Get-Date

New-Item -ItemType Directory -Force -Path $RunRoot | Out-Null
$env:PYTHONUTF8 = "1"
$env:MLFLOW_TRACKING_URI = "file:///G:/Chengbo/alpha_pit_engine_crypto_20260519/runtime/crypto_frontier_research_v2_20260713/mlruns"
$env:TENSORBOARD_LOG_DIR = Join-Path $RunRoot "tensorboard"

Set-Location $RepoRoot
$ExitCode = 1
[ordered]@{
    command = $Command
    state = "RUNNING"
    started_at = $Started.ToString("o")
    finished_at = $null
    exit_code = $null
    stdout = $Stdout
    stderr = $Stderr
} | ConvertTo-Json | Set-Content -LiteralPath $Status -Encoding utf8
try {
    & $Python -u "scripts\crypto_frontier_research_v2.py" $Command 1> $Stdout 2> $Stderr
    $ExitCode = $LASTEXITCODE
}
catch {
    $_ | Out-String | Add-Content -LiteralPath $Stderr -Encoding utf8
    $ExitCode = 1
}
finally {
    [ordered]@{
        command = $Command
        state = "FINISHED"
        started_at = $Started.ToString("o")
        finished_at = (Get-Date).ToString("o")
        exit_code = $ExitCode
        stdout = $Stdout
        stderr = $Stderr
    } | ConvertTo-Json | Set-Content -LiteralPath $Status -Encoding utf8
}

exit $ExitCode
