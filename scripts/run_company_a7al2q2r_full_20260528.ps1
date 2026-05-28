$ErrorActionPreference = 'Stop'
$RemoteRoot = 'D:\HermesWorker\GDrive\AlphaFactory_CryptoData'
$Bat = Join-Path $RemoteRoot 'scripts\run_company_a7al2q2r_full_20260528.bat'
$LogDir = Join-Path $RemoteRoot 'logs'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
Write-Host "A7AL-2Q/2R company full run"
Write-Host "remote_root=$RemoteRoot"
Write-Host "bat=$Bat"
$proc = Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c', $Bat) -WorkingDirectory $RemoteRoot -PassThru -WindowStyle Hidden
Write-Host "pid=$($proc.Id)"
Write-Host "stdout=$LogDir\a7al2q2r_company_full_20260528.out.log"
Write-Host "stderr=$LogDir\a7al2q2r_company_full_20260528.err.log"
