from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATE = "20260607"
STAGE = "A7LS-25"

FULL_INDEX = Path(
    r"G:\AlphaFactory_CryptoData\research_runtime\a7ls15_million_scale_blueprint_generation_20260606\a7ls15_full_blueprint_index.csv"
)
SEED_QUEUE = REPO / "runtime" / "a7ls24_label_transfer_deep_bias_replay" / "a7ls24_candidate_label_transfer_decisions.csv"
OUT_DIR = REPO / "runtime" / "a7ls25_large_search_launch_packet"
REPORT = REPO / "reports" / f"CRYPTO_A7LS25_LARGE_SEARCH_LAUNCH_PACKET_{DATE}.md"

TOTAL_TARGET = 80_000
MATERIALIZATION_TARGET = 40_000
ROWS_PER_SHARD = 1_000
COMPANY_CONCURRENCY = 2

AXIS_TARGETS = {
    "strong_positioning_basis": {
        "semantic_contains": ["positioning_like", "basis_premium_like"],
        "target": 22_000,
    },
    "oi_positioning": {
        "semantic_contains": ["open_interest_like", "positioning_like"],
        "target": 18_000,
    },
    "oi_taker_flow": {
        "semantic_contains": ["open_interest_like", "taker_flow_like"],
        "target": 18_000,
    },
    "raw_multi_axis_reserved": {
        "lane": "A7LS14_B",
        "target": 22_000,
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def axis_match(df: pd.DataFrame, spec: dict) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    if "lane" in spec:
        mask &= df["a7ls_lane"].astype(str).eq(spec["lane"])
    for token in spec.get("semantic_contains", []):
        token_mask = (
            df["semantic_pair"].astype(str).str.contains(token, regex=False, na=False)
            | df["primary_semantic"].astype(str).str.contains(token, regex=False, na=False)
            | df["secondary_semantic"].astype(str).str.contains(token, regex=False, na=False)
        )
        mask &= token_mask
    return mask


def balanced_take(df: pd.DataFrame, target: int) -> pd.DataFrame:
    if df.empty:
        return df
    parts = []
    per_lane = max(1, math.ceil(target / max(1, df["a7ls_lane"].nunique())))
    for _, lane_df in df.groupby("a7ls_lane", sort=True):
        per_semantic = max(1, math.ceil(per_lane / max(1, lane_df["semantic_pair"].nunique())))
        for _, sem_df in lane_df.groupby("semantic_pair", sort=True):
            per_motif = max(1, math.ceil(per_semantic / max(1, sem_df["motif"].nunique())))
            for _, motif_df in sem_df.groupby("motif", sort=True):
                parts.append(motif_df.head(per_motif))
    out = pd.concat(parts, ignore_index=True).drop_duplicates("blueprint_id") if parts else df.head(0)
    if len(out) < target:
        extra = df[~df["blueprint_id"].isin(set(out["blueprint_id"]))].head(target - len(out))
        out = pd.concat([out, extra], ignore_index=True)
    return out.head(target).copy()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    if not FULL_INDEX.exists():
        raise FileNotFoundError(FULL_INDEX)

    seeds = pd.read_csv(SEED_QUEUE)
    seed_transfer = seeds[seeds["role_in_a7ls25"].eq("label_transfer_seed")].copy()
    seed_transfer.to_csv(OUT_DIR / "a7ls25_seed_reference.csv", index=False)

    usecols = [
        "blueprint_id",
        "expression",
        "a7ls_lane",
        "lane_name",
        "search_role",
        "level",
        "candidate_role",
        "generation_priority",
        "semantic_pair",
        "motif",
        "primary_field",
        "secondary_field",
        "primary_semantic",
        "secondary_semantic",
        "primary_transform",
        "secondary_transform",
        "skeleton_key",
        "production_key",
        "source_stage",
        "source_seed_id",
        "checkpoint_group",
    ]

    buckets: dict[str, list[pd.DataFrame]] = {name: [] for name in AXIS_TARGETS}
    counts = {name: 0 for name in AXIS_TARGETS}
    for chunk in pd.read_csv(FULL_INDEX, usecols=usecols, chunksize=100_000, low_memory=False):
        for name, spec in AXIS_TARGETS.items():
            target = int(spec["target"])
            if counts[name] >= target * 3:
                continue
            hit = chunk[axis_match(chunk, spec)].copy()
            if not hit.empty:
                hit["a7ls25_axis"] = name
                buckets[name].append(hit)
                counts[name] += len(hit)

    selected_parts = []
    coverage_rows = []
    for name, spec in AXIS_TARGETS.items():
        df = pd.concat(buckets[name], ignore_index=True).drop_duplicates("blueprint_id") if buckets[name] else pd.DataFrame(columns=usecols)
        chosen = balanced_take(df, int(spec["target"]))
        chosen["a7ls25_axis"] = name
        selected_parts.append(chosen)
        coverage_rows.append(
            {
                "axis": name,
                "candidate_rows_seen": int(len(df)),
                "selected_rows": int(len(chosen)),
                "target_rows": int(spec["target"]),
                "semantic_pair_count": int(chosen["semantic_pair"].nunique()) if not chosen.empty else 0,
                "motif_count": int(chosen["motif"].nunique()) if not chosen.empty else 0,
                "skeleton_count": int(chosen["skeleton_key"].nunique()) if not chosen.empty else 0,
            }
        )

    queue = pd.concat(selected_parts, ignore_index=True).drop_duplicates("blueprint_id")
    queue = queue.head(TOTAL_TARGET).copy()
    queue["a7ls25_search_role"] = "label_transfer_scaled_large_search"
    queue["a7ls25_source"] = "a7ls15_full_blueprint_index_filtered_by_a7ls24_axes"
    queue.to_csv(OUT_DIR / "a7ls25_large_search_queue.csv", index=False)

    materialization = queue.head(MATERIALIZATION_TARGET).copy()
    materialization.to_csv(OUT_DIR / "a7ls25_materialization_queue_40k.csv", index=False)

    shard_rows = []
    for i, start in enumerate(range(0, len(materialization), ROWS_PER_SHARD)):
        end = min(start + ROWS_PER_SHARD, len(materialization))
        shard_rows.append(
            {
                "shard_id": f"a7ls25_mat_s{i:03d}",
                "start_row": start,
                "end_row_exclusive": end,
                "rows": end - start,
            }
        )
    shard_plan = pd.DataFrame(shard_rows)
    shard_plan.to_csv(OUT_DIR / "a7ls25_materialization_shard_plan.csv", index=False)

    coverage = pd.DataFrame(coverage_rows)
    coverage.to_csv(OUT_DIR / "a7ls25_axis_coverage.csv", index=False)

    family = (
        queue.groupby(["a7ls25_axis", "semantic_pair", "motif"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values("rows", ascending=False)
    )
    family.to_csv(OUT_DIR / "a7ls25_queue_family_summary.csv", index=False)

    run_ps1 = OUT_DIR / "run_a7ls25_company_materialization.ps1"
    runtime = r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7ls25_large_search_materialization_20260607"
    remote_repo = r"D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
    queue_path = rf"{runtime}\a7ls25_materialization_queue_40k.csv"
    lines = [
        '$ErrorActionPreference = "Stop"',
        f'$Python = "D:\\HermesWorker\\workspace\\.venv\\Scripts\\python.exe"',
        f'$Repo = "{remote_repo}"',
        f'$Runtime = "{runtime}"',
        f'$Queue = "{queue_path}"',
        f'$Concurrency = {COMPANY_CONCURRENCY}',
        "Set-Location $Repo",
        "New-Item -ItemType Directory -Force -Path $Runtime | Out-Null",
        "$shards = @(",
    ]
    for idx, row in enumerate(shard_rows):
        comma = "," if idx < len(shard_rows) - 1 else ""
        lines.append(
            f'  @{{id="{row["shard_id"]}"; start={row["start_row"]}; end={row["end_row_exclusive"]}}}{comma}'
        )
    lines.extend(
        [
            ")",
            "$active = @()",
            "foreach ($s in $shards) {",
            "  $manifest = Join-Path $Runtime (\"shards\\\" + $s.id + \"\\a7ls17_manifest.json\")",
            "  if (Test-Path $manifest) { Write-Host \"[A7LS25] skip existing $($s.id)\"; continue }",
            "  while (($active | Where-Object { -not $_.HasExited }).Count -ge $Concurrency) { Start-Sleep -Seconds 10; $active = @($active | Where-Object { -not $_.HasExited }) }",
            "  $shardRoot = Join-Path $Runtime (\"shards\\\" + $s.id)",
            "  New-Item -ItemType Directory -Force -Path $shardRoot | Out-Null",
            "  $env:A7LS17_QUEUE_PATH = $Queue",
            "  $env:A7LS17_RUNTIME = $Runtime",
            "  $env:A7LS17_SHARD_ID = $s.id",
            "  $env:A7LS17_START_ROW = [string]$s.start",
            "  $env:A7LS17_END_ROW = [string]$s.end",
            "  $env:A7LS17_SYMBOL_CAP = \"192\"",
            "  $env:A7LS17_TIMESTAMP_CAP = \"4096\"",
            "  $env:A7LS17_PROGRESS_EVERY = \"250\"",
            "  $outLog = Join-Path $shardRoot \"runner.out.log\"",
            "  $errLog = Join-Path $shardRoot \"runner.err.log\"",
            "  Write-Host \"[A7LS25] start $($s.id) rows=$($s.start):$($s.end)\"",
            "  $p = Start-Process -FilePath $Python -ArgumentList @('scripts\\crypto_a7ls17_company_materialization_runner.py') -RedirectStandardOutput $outLog -RedirectStandardError $errLog -PassThru -WindowStyle Hidden",
            "  $active += $p",
            "}",
            "while (($active | Where-Object { -not $_.HasExited }).Count -gt 0) { Start-Sleep -Seconds 15; $active = @($active | Where-Object { -not $_.HasExited }) }",
            "$summary = @()",
            "foreach ($s in $shards) {",
            "  $manifest = Join-Path $Runtime (\"shards\\\" + $s.id + \"\\a7ls17_manifest.json\")",
            "  if (Test-Path $manifest) { $m = Get-Content $manifest -Raw | ConvertFrom-Json; $summary += [pscustomobject]@{shard_id=$s.id; decision=$m.decision; queue_rows=$m.queue_rows; eval_success_count=$m.eval_success_count; activity_ok_count=$m.activity_ok_count} }",
            "  else { $summary += [pscustomobject]@{shard_id=$s.id; decision='MISSING_MANIFEST'; queue_rows=0; eval_success_count=0; activity_ok_count=0} }",
            "}",
            "$summary | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $Runtime 'a7ls25_materialization_summary.json')",
            "Write-Host \"[A7LS25] materialization wave complete\"",
        ]
    )
    run_ps1.write_text("\n".join(lines), encoding="utf-8")

    manifest = {
        "stage": STAGE,
        "decision": "PASS_A7LS25_LARGE_SEARCH_PACKET_READY_FOR_COMPANY_MATERIALIZATION",
        "generated_at": now_iso(),
        "full_index": str(FULL_INDEX),
        "total_queue_rows": int(len(queue)),
        "materialization_queue_rows": int(len(materialization)),
        "shard_count": int(len(shard_plan)),
        "rows_per_shard": ROWS_PER_SHARD,
        "company_concurrency": COMPANY_CONCURRENCY,
        "axis_targets": AXIS_TARGETS,
        "uses_may": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(OUT_DIR / "a7ls25_manifest.json", manifest)

    report = [
        f"# CRYPTO A7LS-25 Large Search Launch Packet ({DATE})",
        "",
        "## Decision",
        "",
        "`PASS_A7LS25_LARGE_SEARCH_PACKET_READY_FOR_COMPANY_MATERIALIZATION`",
        "",
        "## Scope",
        "",
        f"- total queue rows: {len(queue)}",
        f"- materialization queue rows: {len(materialization)}",
        f"- shards: {len(shard_plan)} x {ROWS_PER_SHARD}",
        f"- company concurrency: {COMPANY_CONCURRENCY}",
        "- source: A7LS15 full blueprint index filtered by A7LS24 label-transfer axes",
        "- no May usage",
        "- no alpha proof / shadow / paper / live",
        "",
        "## Axis Coverage",
        "",
        coverage.to_markdown(index=False),
        "",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
