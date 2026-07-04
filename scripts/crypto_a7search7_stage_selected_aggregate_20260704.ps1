param(
  [string]$RunRoot = "D:\HermesWorker\runtime\a7search7_family_diversified_proxy_65k_r2_20260704",
  [string]$StageRoot = "D:\HermesWorker\runtime\a7search7_selected_aggregate_staging_r2_20260704",
  [string]$Runtime = "D:\HermesWorker\runtime\a7search7_selected_aggregate_r2_20260704",
  [string]$Report = "D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote\reports\CRYPTO_A7SEARCH7_SELECTED_AGGREGATE_R2_20260704.md",
  [int]$ExpectedShards = 128,
  [int]$SelectTarget = 384,
  [int]$PairCap = 24,
  [int]$MotifCap = 96,
  [int]$SkeletonCap = 2
)

$ErrorActionPreference = "Stop"

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
$missingShards = @()
$manifestFailures = @()

for ($i = 0; $i -lt $ExpectedShards; $i++) {
  $shardName = "a7search7_proxy_s{0:D3}" -f $i
  $sourceRuntime = Join-Path (Join-Path (Join-Path $RunRoot "shards") $shardName) "proxy_runtime"
  $stageShard = Join-Path (Join-Path $StageRoot "shards") $shardName
  New-Item -ItemType Directory -Force -Path $stageShard | Out-Null

  $manifest = Join-Path $sourceRuntime "a7v3s9_proxy_manifest.json"
  if (Test-Path $manifest) {
    try {
      Copy-Item -LiteralPath $manifest -Destination (Join-Path $stageShard "a7v3s9_proxy_manifest.json") -Force
      $manifestCount += 1
    } catch {
      $manifestFailures += "$shardName manifest_copy_failed $($_.Exception.Message)"
    }
  } else {
    $missingShards += $shardName
  }

  $selectedPath = Join-Path $sourceRuntime "a7v3s9_proxy_selected_for_reward.csv"
  if (Test-Path $selectedPath) {
    try {
      $stageSelected = Join-Path $stageShard "a7v3s9_proxy_selected_for_reward.csv"
      Copy-Item -LiteralPath $selectedPath -Destination $stageSelected -Force
      foreach ($row in (Import-Csv -LiteralPath $stageSelected)) {
        $selectedLocal += Add-RowMeta $row $shardName $stageSelected
      }
    } catch {
      $manifestFailures += "$shardName selected_copy_or_import_failed $($_.Exception.Message)"
    }
  }

  $errorPath = Join-Path $sourceRuntime "a7v3s9_proxy_eval_errors.csv"
  if (Test-Path $errorPath) {
    try {
      $stageErrors = Join-Path $stageShard "a7v3s9_proxy_eval_errors.csv"
      Copy-Item -LiteralPath $errorPath -Destination $stageErrors -Force
      if ((Get-Item -LiteralPath $stageErrors).Length -gt 2) {
        foreach ($row in (Import-Csv -LiteralPath $stageErrors)) {
          $evalErrors += Add-RowMeta $row $shardName $stageErrors
        }
      }
    } catch {
      $manifestFailures += "$shardName errors_copy_or_import_failed $($_.Exception.Message)"
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
$policySummary = @(Group-Count $selected "search_policy")
$uniqueBlueprints = @($selected | Where-Object { $_.blueprint_id } | Select-Object -ExpandProperty blueprint_id -Unique).Count

Export-Rows (Join-Path $Runtime "a7search7_proxy_selected_local_concat.csv") $selectedLocal
Export-Rows (Join-Path $Runtime "a7search7_proxy_selected_for_reward.csv") $selected
Export-Rows (Join-Path $Runtime "a7search7_proxy_eval_errors_all.csv") $evalErrors
Export-Rows (Join-Path $Runtime "a7search7_selected_pair_summary.csv") $pairSummary
Export-Rows (Join-Path $Runtime "a7search7_selected_motif_summary.csv") $motifSummary
Export-Rows (Join-Path $Runtime "a7search7_selected_policy_summary.csv") $policySummary
Write-Utf8 (Join-Path $Runtime "a7search7_missing_shards.txt") (($missingShards -join "`n") + $(if ($missingShards.Count) { "`n" } else { "" }))
Write-Utf8 (Join-Path $Runtime "a7search7_manifest_failures.txt") (($manifestFailures -join "`n") + $(if ($manifestFailures.Count) { "`n" } else { "" }))

$decision = if ($manifestCount -eq $ExpectedShards -and $selected.Count -gt 0 -and $evalErrors.Count -eq 0 -and $manifestFailures.Count -eq 0) {
  "PASS_A7SEARCH7_SELECTED_AGGREGATE_READY"
} elseif ($manifestCount -eq $ExpectedShards -and $selected.Count -gt 0 -and $evalErrors.Count -eq 0) {
  "PASS_A7SEARCH7_SELECTED_AGGREGATE_READY_WITH_COPY_WARNINGS"
} else {
  "HOLD_A7SEARCH7_SELECTED_AGGREGATE_INCOMPLETE_OR_ERRORS"
}

$manifest = [ordered]@{
  stage = "A7SEARCH7_SELECTED_AGGREGATE"
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
  manifest_failures = $manifestFailures
  selected_queue = (Join-Path $Runtime "a7search7_proxy_selected_for_reward.csv")
  authorizes_bounded_full_reward = ($manifestCount -eq $ExpectedShards -and $selected.Count -gt 0 -and $evalErrors.Count -eq 0)
  authorizes_alpha_proof = $false
  authorizes_shadow_paper_live = $false
}
$manifestJson = $manifest | ConvertTo-Json -Depth 6
Write-Utf8 (Join-Path $Runtime "a7search7_selected_aggregate_manifest.json") $manifestJson

$nl = [System.Environment]::NewLine
$reportLines = @(
  "# CRYPTO A7SEARCH7 Selected Aggregate 20260704",
  "",
  "Decision: $decision",
  "",
  "Counts",
  "- manifest_count: $manifestCount / $ExpectedShards",
  "- selected_local_rows: $($selectedLocal.Count)",
  "- selected_rows: $($selected.Count)",
  "- selected_unique_blueprints: $uniqueBlueprints",
  "- eval_error_rows: $($evalErrors.Count)",
  "- manifest_failures: $($manifestFailures.Count)",
  "",
  "Outputs",
  "- selected queue: $(Join-Path $Runtime 'a7search7_proxy_selected_for_reward.csv')",
  "- local selected concat: $(Join-Path $Runtime 'a7search7_proxy_selected_local_concat.csv')",
  "- pair summary: $(Join-Path $Runtime 'a7search7_selected_pair_summary.csv')",
  "- motif summary: $(Join-Path $Runtime 'a7search7_selected_motif_summary.csv')",
  "- policy summary: $(Join-Path $Runtime 'a7search7_selected_policy_summary.csv')",
  "- missing shards: $(Join-Path $Runtime 'a7search7_missing_shards.txt')",
  "- manifest failures: $(Join-Path $Runtime 'a7search7_manifest_failures.txt')",
  "- manifest: $(Join-Path $Runtime 'a7search7_selected_aggregate_manifest.json')",
  "",
  "Boundary",
  "This aggregate authorizes bounded full reward queueing only. It does not authorize alpha proof, shadow, paper, or live."
)
Write-Utf8 $Report ([string]::Join($nl, $reportLines) + $nl)

$manifestJson
