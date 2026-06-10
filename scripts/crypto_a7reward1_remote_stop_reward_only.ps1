$ErrorActionPreference = "Continue"
Write-Output "== stopping A7REWARD1 only =="
$procs = Get-CimInstance Win32_Process -Filter "name='python.exe'" |
  Where-Object { $_.CommandLine -match "crypto_a7reward1_portfolio_reward_model.py" }
foreach ($p in $procs) {
  Write-Output "stop pid=$($p.ProcessId) cmd=$($p.CommandLine)"
  Stop-Process -Id $p.ProcessId -Force -ErrorAction Continue
}
Write-Output "== remaining python =="
Get-CimInstance Win32_Process -Filter "name='python.exe'" |
  Select-Object ProcessId, WorkingSetSize, CommandLine |
  Format-Table -AutoSize -Wrap
