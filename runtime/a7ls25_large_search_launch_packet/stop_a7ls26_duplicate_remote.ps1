$ErrorActionPreference = "Continue"

$Ids = @(31204, 21532, 31300, 26456, 12796, 25940, 25776)
foreach ($id in $Ids) {
  Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
}

"stopped duplicate A7LS26 worker ids: " + ($Ids -join ",")
