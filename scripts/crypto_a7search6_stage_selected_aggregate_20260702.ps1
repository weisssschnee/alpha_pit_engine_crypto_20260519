$ErrorActionPreference = "Stop"

$RunRoot = "H:\AlphaFactory_CryptoData_archive\a7search6_mechanism_memory_seed_proxy_65k_20260630"
$StageRoot = "D:\HermesWorker\runtime\a7search6_selected_aggregate_staging_20260702"
$Runtime = "D:\HermesWorker\runtime\a7search6_selected_aggregate_20260702"
$Report = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\reports\CRYPTO_A7SEARCH6_SELECTED_AGGREGATE_20260702.md"
$ExpectedShards = 128
$SelectTarget = 256
$PairCap = 24
$MotifCap = 96
$SkeletonCap = 2

function Write-Utf8($Path, $Text) {
  $dir = Split-Path -Parent $Path
  if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  [System.IO.File]::WriteAllText($Path, $Text, [System.Text.UTF8Encoding]::new($false))
}

function NumericValue($Value) {
  $out = 0.0
  if ([double]::TryParse([string]$Value, [ref]$out)) { return $out }
  return [double]::NegativeInfinity
}

function Add-RowMeta($Row, $ShardName, $SourceFile) {
  $ordered = [ordered]@{}
  foreach ($prop in $Row.PSObject.Properties) {
    $ordered[$prop.Name] = $prop.Value
  }
  $ordered["proxy_shard_id"] = $ShardName
  $ordered["source_file"] = $SourceFile
  return [PSCustomObject]$ordered
}

function Export-Rows($Path, $Rows) {
  $dir = Split-Path -Parent $Path
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  if ($Rows.Count -eq 0) {
    "" | Set-Content -Encoding UTF8 $Path
  } else {
    $Rows | Export-Csv -NoTypeInformation -Encoding UTF8 $Path
  }
}

function Group-Count($Rows, $Key) {
  $Rows |
    Group-Object -Property $Key |
    Sort-Object Count -Descending |
    ForEach-Object {
      [PSCustomObject]@{
        group_key = $_.Name
        count = $_.Count
      }
    }
}

Remove-Item -LiteralPath $StageRoot -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $Runtime -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $StageRoot, $Runtime | Out-Null

$manifestCount = 0
$selectedLocal = @()
$evalErrors = @()
$suspectShards = @()
$missingShards = @()

for ($i = 0; $i -lt $ExpectedShards; $i++) {
  $shardName = "a7search6_proxy_s{0:D3}" -f $i
  $sourceRuntime = Join-Path (Join-Path (Join-Path $RunRoot "shards") $shardName) "proxy_runtime"
  $stageShard = Join-Path (Join-Path $StageRoot "shards") $shardName
  New-Item -ItemType Directory -Force -Path $stageShard | Out-Null

  $manifest = Join-Path $sourceRuntime "a7v3s9_proxy_manifest.json"
  if (Test-Path $manifest) {
    $manifestCount += 1
    Copy-Item -LiteralPath $manifest -Destination (Join-Path $stageShard "a7v3s9_proxy_manifest.json") -Force
  } else {
    $missingShards += $shardName
  }

  $suspect = Join-Path (Join-Path (Join-Path $RunRoot "shards") $shardName) "DUPLICATE_WORKER_SUSPECT_20260701.txt"
  if (Test-Path $suspect) {
    $suspectShards += $shardName
    Copy-Item -LiteralPath $suspect -Destination (Join-Path $stageShard "DUPLICATE_WORKER_SUSPECT_20260701.txt") -Force
  }

  $selectedPath = Join-Path $sourceRuntime "a7v3s9_proxy_selected_for_reward.csv"
  if (Test-Path $selectedPath) {
    $stageSelected = Join-Path $stageShard "a7v3s9_proxy_selected_for_reward.csv"
    Copy-Item -LiteralPath $selectedPath -Destination $stageSelected -Force
    foreach ($row in (Import-Csv -LiteralPath $stageSelected)) {
      $selectedLocal += Add-RowMeta $row $shardName $stageSelected
    }
  }

  $errorPath = Join-Path $sourceRuntime "a7v3s9_proxy_eval_errors.csv"
  if (Test-Path $errorPath) {
    $stageErrors = Join-Path $stageShard "a7v3s9_proxy_eval_errors.csv"
    Copy-Item -LiteralPath $errorPath -Destination $stageErrors -Force
    if ((Get-Item -LiteralPath $stageErrors).Length -gt 2) {
      foreach ($row in (Import-Csv -LiteralPath $stageErrors)) {
        $evalErrors += Add-RowMeta $row $shardName $stageErrors
      }
    }
  }
}

$orderedCandidates = $selectedLocal | Sort-Object `
  @{ Expression = { NumericValue $_.proxy_score }; Descending = $true }, `
  @{ Expression = { NumericValue $_.min_oos_floor_sortino }; Descending = $true }, `
  @{ Expression = { NumericValue $_.recent_sortino }; Descending = $true }

$pairCounts = @{}
$motifCounts = @{}
$skeletonCounts = @{}
$selected = @()
foreach ($row in $orderedCandidates) {
  $pair = [string]$row.semantic_pair
  $motif = [string]$row.motif
  $skeleton = if ($row.PSObject.Properties.Name -contains "skeleton_key" -and $row.skeleton_key) { [string]$row.skeleton_key } else { [string]$row.expression }
  if (-not $pairCounts.ContainsKey($pair)) { $pairCounts[$pair] = 0 }
  if (-not $motifCounts.ContainsKey($motif)) { $motifCounts[$motif] = 0 }
  if (-not $skeletonCounts.ContainsKey($skeleton)) { $skeletonCounts[$skeleton] = 0 }
  if ($pairCounts[$pair] -ge $PairCap) { continue }
  if ($motifCounts[$motif] -ge $MotifCap) { continue }
  if ($skeletonCounts[$skeleton] -ge $SkeletonCap) { continue }
  $selected += $row
  $pairCounts[$pair] += 1
  $motifCounts[$motif] += 1
  $skeletonCounts[$skeleton] += 1
  if ($selected.Count -ge $SelectTarget) { break }
}

$pairSummary = @(Group-Count $selected "semantic_pair")
$motifSummary = @(Group-Count $selected "motif")
$uniqueBlueprints = @($selected | Where-Object { $_.blueprint_id } | Select-Object -ExpandProperty blueprint_id -Unique).Count

Export-Rows (Join-Path $Runtime "a7search6_proxy_selected_local_concat.csv") $selectedLocal
Export-Rows (Join-Path $Runtime "a7search6_proxy_selected_for_reward.csv") $selected
Export-Rows (Join-Path $Runtime "a7search6_proxy_eval_errors_all.csv") $evalErrors
Export-Rows (Join-Path $Runtime "a7search6_selected_pair_summary.csv") $pairSummary
Export-Rows (Join-Path $Runtime "a7search6_selected_motif_summary.csv") $motifSummary
Write-Utf8 (Join-Path $Runtime "a7search6_missing_shards.txt") (($missingShards -join "`n") + $(if ($missingShards.Count) { "`n" } else { "" }))
Write-Utf8 (Join-Path $Runtime "a7search6_suspect_shards.txt") (($suspectShards -join "`n") + $(if ($suspectShards.Count) { "`n" } else { "" }))

$decision = if ($manifestCount -eq $ExpectedShards -and $selected.Count -gt 0 -and $evalErrors.Count -eq 0 -and $suspectShards.Count -gt 0) {
  "PASS_A7SEARCH6_SELECTED_AGGREGATE_READY_WITH_SUSPECT_RECHECK"
} elseif ($manifestCount -eq $ExpectedShards -and $selected.Count -gt 0 -and $evalErrors.Count -eq 0) {
  "PASS_A7SEARCH6_SELECTED_AGGREGATE_READY"
} else {
  "HOLD_A7SEARCH6_SELECTED_AGGREGATE_INCOMPLETE_OR_ERRORS"
}

$manifest = [ordered]@{
  stage = "A7SEARCH6_SELECTED_AGGREGATE"
  generated_at = (Get-Date).ToString("o")
  decision = $decision
  run_root = $RunRoot
  stage_root = $StageRoot
  runtime = $Runtime
  report = $Report
  expected_shards = $ExpectedShards
  manifest_count = $manifestCount
  selected_local_rows = $selectedLocal.Count
  selected_rows = $selected.Count
  selected_unique_blueprints = $uniqueBlueprints
  eval_error_rows = $evalErrors.Count
  missing_shards = $missingShards
  suspect_shards = $suspectShards
  selected_queue = (Join-Path $Runtime "a7search6_proxy_selected_for_reward.csv")
  authorizes_bounded_full_reward = ($manifestCount -eq $ExpectedShards -and $selected.Count -gt 0 -and $evalErrors.Count -eq 0)
  authorizes_alpha_proof = $false
  authorizes_shadow_paper_live = $false
}
$manifestJson = $manifest | ConvertTo-Json -Depth 6
Write-Utf8 (Join-Path $Runtime "a7search6_selected_aggregate_manifest.json") $manifestJson

$nl = [System.Environment]::NewLine
$suspectText = if ($suspectShards.Count) { $suspectShards -join ", " } else { "<none>" }
$reportLines = @(
  "# CRYPTO A7SEARCH6 Selected Aggregate 20260702",
  "",
  "Decision: $decision",
  "",
  "Counts",
  "- manifest_count: $manifestCount / $ExpectedShards",
  "- selected_local_rows: $($selectedLocal.Count)",
  "- selected_rows: $($selected.Count)",
  "- selected_unique_blueprints: $uniqueBlueprints",
  "- eval_error_rows: $($evalErrors.Count)",
  "- suspect_shards: $suspectText",
  "",
  "Outputs",
  "- selected queue: $(Join-Path $Runtime 'a7search6_proxy_selected_for_reward.csv')",
  "- local selected concat: $(Join-Path $Runtime 'a7search6_proxy_selected_local_concat.csv')",
  "- pair summary: $(Join-Path $Runtime 'a7search6_selected_pair_summary.csv')",
  "- motif summary: $(Join-Path $Runtime 'a7search6_selected_motif_summary.csv')",
  "- suspect shards: $(Join-Path $Runtime 'a7search6_suspect_shards.txt')",
  "- manifest: $(Join-Path $Runtime 'a7search6_selected_aggregate_manifest.json')",
  "",
  "Boundary",
  "This aggregate authorizes bounded full reward queueing only. It does not authorize alpha proof, shadow, paper, or live."
)
$reportText = [string]::Join($nl, $reportLines)
Write-Utf8 $Report ($reportText + $nl)

$manifestJson
