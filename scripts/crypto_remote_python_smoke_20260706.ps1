$ErrorActionPreference = "Stop"

$Repo = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
$Log = "D:\HermesWorker\runtime\a7source5_python_smoke_20260706.log"
Set-Location $Repo

@("D:\HermesWorker\workspace\.venv\Scripts\python.exe", "D:\Python311\python.exe") | ForEach-Object {
  $Python = $_
  "PYTHON=$Python" | Out-File -Append -FilePath $Log -Encoding UTF8
  & $Python -c "import sys, pandas as pd; print(sys.executable); print(pd.__version__)" *>> $Log
  "EXIT=$LASTEXITCODE" | Out-File -Append -FilePath $Log -Encoding UTF8
}

Get-Content $Log
