from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from alphafactory_crypto.engines.search_memory_enforcement import SearchMemoryEnforcer
from scripts.crypto_a7v3s0_next_large_search_contract import FIELD_SPECS, FORBIDDEN_FIELDS, WINDOWS_ALL


REPO = Path(__file__).resolve().parents[1]
STAGE = "A7SEARCH6"
DEFAULT_RUNTIME = Path(r"H:\AlphaFactory_CryptoData_archive\a7search6_mechanism_memory_seed_proxy_65k_20260630")
DEFAULT_REPORT = (
    REPO / "reports" / "CRYPTO_A7SEARCH6_MECHANISM_MEMORY_SEED_PROXY_CONTRACT_20260630.md"
)
DEFAULT_MEMORY_PRIOR = REPO / "runtime" / "a7mem0_search_memory_registry_20260628" / "a7mem0_next_search_prior.json"
DEFAULT_VALIDATION_MANIFEST = REPO / "runtime" / "a7search5_validation_pack_manifest_20260630.json"

OI_FIELDS = [
    "open_interest_value_last",
    "open_interest_value_mean",
    "open_interest_last",
    "open_interest_mean",
    "open_interest_value_change_24h",
]
POSITIONING_FIELDS = [
    "top_long_short_account_ratio_last",
    "top_long_short_position_ratio_last",
    "global_long_short_account_ratio_last",
    "account_position_divergence",
    "top_global_account_divergence",
]
ADJACENT_FIELDS = [
    "taker_buy_sell_volume_ratio_last",
    "taker_buy_sell_volume_ratio_mean",
    "kline_taker_buy_quote_share",
    "funding_rate_state_last_ffill_8h",
    "funding_rate_abs_state_168h_z",
    "funding_rate_delta_state_24h",
    "mark_index_basis_bps",
    "premium_close_bps",
    "quote_volume_z_168h",
    "leverage_crowding_state",
    "basis_dislocation_state",
    "stress_proxy_state",
    "liquidity_cycle_state",
]
HORIZONS = [4, 8, 24]
LANE_WEIGHTS = {
    "validated_oi_positioning_scale": 0.58,
    "operator_ablation_surface": 0.18,
    "adjacent_mechanism_cross": 0.16,
    "regime_conditioned_mechanism": 0.08,
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short_hash(text: str, n: int = 16) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(frame: pd.DataFrame, max_rows: int = 60) -> str:
    if frame.empty:
        return "`<empty>`"
    view = frame.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def canonical_ast(expr: str) -> str:
    text = re.sub(r"\s+", "", expr)
    for field in sorted(FIELD_SPECS, key=len, reverse=True):
        text = text.replace(field, "FIELD")
    text = re.sub(r"\b\d+\b", "W", text)
    return text


def field_semantic(field: str) -> str:
    return str(FIELD_SPECS.get(field, {}).get("semantic", "unknown"))


def available(field: str) -> bool:
    return field in FIELD_SPECS and field not in FORBIDDEN_FIELDS


def transform_pool(field: str, rng: random.Random, *, rich: bool = True) -> list[tuple[str, str]]:
    windows = [4, 8, 12, 24, 48, 72, 96, 168, 336, 504]
    rng.shuffle(windows)
    windows = windows[:8] if rich else windows[:4]
    out = [
        (field, "level"),
        (f"ZScore({field})", "zscore"),
        (f"CSRank({field})", "csrank"),
        (f"Abs(CSRank({field}))", "abs_csrank"),
    ]
    for w in windows:
        out.extend(
            [
                (f"Mean({field},{w})", f"mean_{w}"),
                (f"ZScore(Mean({field},{w}))", f"zmean_{w}"),
                (f"Delta({field},{w})", f"delta_{w}"),
                (f"CSRank(Delta({field},{w}))", f"cs_delta_{w}"),
                (f"TSRank({field},{w})", f"tsrank_{w}"),
                (f"Decay({field},{w})", f"decay_{w}"),
            ]
        )
    return out


def pick_weighted(rng: random.Random, weights: dict[str, float]) -> str:
    total = sum(max(0.0, float(v)) for v in weights.values())
    mark = rng.random() * total
    running = 0.0
    for key, value in weights.items():
        running += max(0.0, float(value))
        if running >= mark:
            return key
    return next(iter(weights))


def lane_fields(lane: str, rng: random.Random) -> tuple[str, str, str]:
    oi = [field for field in OI_FIELDS if available(field)]
    pos = [field for field in POSITIONING_FIELDS if available(field)]
    adj = [field for field in ADJACENT_FIELDS if available(field)]
    if lane in {"validated_oi_positioning_scale", "operator_ablation_surface"}:
        return rng.choice(oi), rng.choice(pos), "open_interest|positioning"
    if lane == "adjacent_mechanism_cross":
        left = rng.choice(oi + pos)
        right = rng.choice(adj)
        pair = "|".join(sorted([field_semantic(left), field_semantic(right)]))
        return left, right, pair
    left = rng.choice(oi + pos)
    regimes = [f for f in adj if field_semantic(f) == "regime"]
    right = rng.choice(regimes or adj)
    pair = "|".join(sorted([field_semantic(left), field_semantic(right)]))
    return left, right, pair


def interaction_expr(lane: str, left: str, right: str, rng: random.Random) -> tuple[str, str]:
    if lane == "validated_oi_positioning_scale":
        templates = [
            (f"SafeDiv({left},CSRank({right}))", "safe_div_csrank"),
            (f"SafeDiv({left},Abs(CSRank({right})))", "safe_div_abs_csrank"),
            (f"SafeDiv({left},Abs({right}))", "safe_div_abs"),
            (f"SafeDiv(CSRank({left}),CSRank({right}))", "rank_safe_div"),
            (f"SafeDiv(ZScore({left}),CSRank({right}))", "z_safe_div_csrank"),
            (f"SafeDiv(ZScore({left}),Abs(CSRank({right})))", "z_safe_div_abs_csrank"),
        ]
    elif lane == "operator_ablation_surface":
        templates = [
            (f"Sub(CSRank({left}),CSRank({right}))", "spread_rank"),
            (f"Mul(CSRank({left}),CSRank({right}))", "rank_mul"),
            (f"Mul(CSRank({left}),Sign({right}))", "signed_rank_gate"),
            (f"SafeDiv(Sub(CSRank({left}),CSRank({right})),CSRank({right}))", "scaled_spread_no_abs"),
            (f"SafeDiv(Sub(CSRank({left}),CSRank({right})),Abs(CSRank({right})))", "scaled_spread_abs"),
        ]
    elif lane == "regime_conditioned_mechanism":
        templates = [
            (f"Mul({left},Sign({right}))", "regime_signed"),
            (f"Mul(CSRank({left}),CSRank({right}))", "regime_rank_mul"),
            (f"SafeDiv({left},Abs(CSRank({right})))", "regime_scaled"),
        ]
    else:
        templates = [
            (f"SafeDiv({left},Abs({right}))", "adjacent_safe_div_abs"),
            (f"SafeDiv({left},CSRank({right}))", "adjacent_safe_div_csrank"),
            (f"Sub(CSRank({left}),CSRank({right}))", "adjacent_spread_rank"),
            (f"Mul(CSRank({left}),Sign({right}))", "adjacent_signed_rank"),
            (f"Mul({left},{right})", "adjacent_mul"),
        ]
    return rng.choice(templates)


def build_queue(
    *,
    queue_rows: int,
    seed: int,
    memory_prior: Path,
    rows_per_shard: int,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    rng = random.Random(seed)
    enforcer = SearchMemoryEnforcer(prior_path=memory_prior)
    rows: list[dict[str, Any]] = []
    trace_rows: list[dict[str, Any]] = []
    seen_expr: set[str] = set()
    lane_counts = Counter()
    field_counts = Counter()
    skeleton_counts = Counter()
    memory_expression_counter: Counter[str] = Counter()
    memory_shard_counters: dict[int, dict[str, Counter[str]]] = defaultdict(
        lambda: {"skeleton_key": Counter(), "pair_motif": Counter()}
    )
    memory_action_counts = Counter()
    memory_reject_counts = Counter()
    attempts = 0
    max_attempts = queue_rows * 160
    field_cap = max(1024, int(queue_rows * 0.36))
    skeleton_cap = 192

    while len(rows) < queue_rows and attempts < max_attempts:
        attempts += 1
        lane = pick_weighted(rng, LANE_WEIGHTS)
        left_field, right_field, semantic_pair = lane_fields(lane, rng)
        left_expr, left_motif = rng.choice(transform_pool(left_field, rng, rich=True))
        right_expr, right_motif = rng.choice(transform_pool(right_field, rng, rich=True))
        expr, motif = interaction_expr(lane, left_expr, right_expr, rng)
        if expr in seen_expr:
            continue
        skeleton = canonical_ast(expr)
        if skeleton_counts[skeleton] >= skeleton_cap:
            continue
        if field_counts[left_field] >= field_cap or field_counts[right_field] >= field_cap:
            continue
        horizon = rng.choice(HORIZONS)
        row = {
            "blueprint_id": f"a7search6_{short_hash(str(len(rows)) + '|' + expr)}",
            "expression": expr,
            "semantic_pair": semantic_pair,
            "motif": motif,
            "horizon_h": horizon,
            "search_policy": lane,
            "search_core": "memory_seeded_mechanism_surface",
            "ast_path": f"{lane}/{semantic_pair}/{motif}/{left_motif}/{right_motif}",
            "ast_skeleton": skeleton,
            "skeleton_key": skeleton,
            "primary_field": left_field,
            "secondary_field": right_field,
            "primary_semantic": field_semantic(left_field),
            "secondary_semantic": field_semantic(right_field),
            "left_transform_motif": left_motif,
            "right_transform_motif": right_motif,
            "candidate_origin": "a7search5_validation_seed_expansion",
            "reward_feedback_source": "a7search5_validation_pack_hold_non_unique_increment",
            "authorizes": "proxy_only",
        }
        shard_bucket = len(rows) // max(1, rows_per_shard)
        counters: dict[str, Counter[str]] = {
            "expression_key": memory_expression_counter,
            "skeleton_key": memory_shard_counters[shard_bucket]["skeleton_key"],
            "pair_motif": memory_shard_counters[shard_bucket]["pair_motif"],
        }
        decision = enforcer.decide(row, counters)
        trace_rows.append({"attempt": attempts, **row, **decision.as_row()})
        memory_action_counts[decision.action] += 1
        memory_reject_counts[decision.reason] += 1
        if not decision.allowed:
            continue
        row.update(decision.as_row())
        memory_expression_counter[decision.expression_key] += 1
        memory_shard_counters[shard_bucket]["skeleton_key"][decision.skeleton_key] += 1
        memory_shard_counters[shard_bucket]["pair_motif"][decision.pair_motif] += 1
        rows.append(row)
        seen_expr.add(expr)
        lane_counts[lane] += 1
        field_counts[left_field] += 1
        field_counts[right_field] += 1
        skeleton_counts[skeleton] += 1

    queue = pd.DataFrame(rows)
    trace = pd.DataFrame(trace_rows)
    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": "PASS_A7SEARCH6_MECHANISM_QUEUE_READY" if len(queue) == queue_rows else "HOLD_A7SEARCH6_QUEUE_UNDERFILLED",
        "queue_rows_requested": int(queue_rows),
        "queue_rows": int(len(queue)),
        "attempts": int(attempts),
        "seed": int(seed),
        "rows_per_shard": int(rows_per_shard),
        "lane_weights": LANE_WEIGHTS,
        "lane_counts": dict(lane_counts),
        "semantic_pair_count": int(queue["semantic_pair"].nunique()) if not queue.empty else 0,
        "motif_count": int(queue["motif"].nunique()) if not queue.empty else 0,
        "skeleton_count": int(queue["skeleton_key"].nunique()) if not queue.empty else 0,
        "memory_prior": str(memory_prior),
        "memory_action_counts": dict(memory_action_counts),
        "memory_reject_counts": dict(memory_reject_counts),
        "authorizes_proxy_search": bool(len(queue) > 0),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    return queue, trace, manifest


def write_supervisor(runtime: Path, max_parallel: int, min_free_gb: float) -> Path:
    path = runtime / "a7search6_proxy_supervisor.ps1"
    content = f'''
$ErrorActionPreference = "Continue"
$Repo = "D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote"
$Python = "D:\\HermesWorker\\workspace\\.venv\\Scripts\\python.exe"
$RunRoot = "{runtime}"
$MaxParallel = {max_parallel}
$MinFreeGb = {min_free_gb}
$env:PYTHONPATH = $Repo
$env:PYTHONWARNINGS = "ignore"
$env:NUMEXPR_MAX_THREADS = "4"
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$StatusPath = Join-Path $RunRoot "a7search6_proxy_supervisor_status.csv"
"shard_id,status,start_time,end_time,exit_code,notes" | Set-Content -Path $StatusPath -Encoding utf8

function FreeGb {{
  $os = Get-CimInstance Win32_OperatingSystem
  return [math]::Round($os.FreePhysicalMemory / 1024 / 1024, 2)
}}

Set-Location $Repo
$shards = Import-Csv (Join-Path $RunRoot "a7search6_proxy_shard_plan.csv")
$jobs = @()
foreach ($row in $shards) {{
  $ShardId = $row.shard_id
  $Manifest = Join-Path $RunRoot ("shards\\" + $ShardId + "\\proxy_runtime\\a7v3s9_proxy_manifest.json")
  if (Test-Path $Manifest) {{
    Add-Content -Path $StatusPath -Value "$ShardId,skip_existing,,,$(0),manifest_exists"
    continue
  }}
  while (($jobs | Where-Object {{ $_.HasExited -eq $false }}).Count -ge $MaxParallel -or (FreeGb) -lt $MinFreeGb) {{
    Start-Sleep -Seconds 20
    $jobs = @($jobs | Where-Object {{ $_.HasExited -eq $false }})
  }}
  $Queue = Join-Path $RunRoot ("queue_shards\\" + $ShardId + ".csv")
  $ShardRoot = Join-Path $RunRoot ("shards\\" + $ShardId)
  New-Item -ItemType Directory -Force -Path $ShardRoot | Out-Null
  $Runtime = Join-Path $ShardRoot "proxy_runtime"
  $Report = Join-Path $ShardRoot ("CRYPTO_" + $ShardId + "_PROXY.md")
  $Out = Join-Path $ShardRoot "runner.out.log"
  $Err = Join-Path $ShardRoot "runner.err.log"
  Add-Content -Path $StatusPath -Value "$ShardId,running,$((Get-Date).ToString('s')),,,free_gb=$(FreeGb)"
  $Args = @("-W","ignore","-m","scripts.crypto_a7v3s9_prereward_oos_control_proxy","--queue",$Queue,"--runtime",$Runtime,"--report",$Report,"--candidate-cap","0","--successive-halving","--halving-keep-rows","128","--checkpoint-every","64","--select-target","128","--pair-cap","24","--motif-cap","64","--skeleton-cap","3")
  $p = Start-Process -FilePath $Python -ArgumentList $Args -WorkingDirectory $Repo -RedirectStandardOutput $Out -RedirectStandardError $Err -PassThru -WindowStyle Hidden
  $p | Add-Member -NotePropertyName ShardId -NotePropertyValue $ShardId
  $jobs += $p
}}
foreach ($j in $jobs) {{
  $j.WaitForExit()
  Add-Content -Path $StatusPath -Value "$($j.ShardId),finished,,$((Get-Date).ToString('s')),$($j.ExitCode),free_gb=$(FreeGb)"
}}
'''
    path.write_text(content.strip() + "\n", encoding="utf-8")
    return path


def write_report(report: Path, manifest: dict[str, Any], queue: pd.DataFrame, runtime: Path) -> None:
    lane = queue.groupby("search_policy", dropna=False).size().reset_index(name="rows").sort_values("rows", ascending=False)
    pair = queue.groupby("semantic_pair", dropna=False).size().reset_index(name="rows").sort_values("rows", ascending=False)
    motif = queue.groupby("motif", dropna=False).size().reset_index(name="rows").sort_values("rows", ascending=False)
    lane.to_csv(runtime / "a7search6_lane_summary.csv", index=False)
    pair.to_csv(runtime / "a7search6_pair_summary.csv", index=False)
    motif.to_csv(runtime / "a7search6_motif_summary.csv", index=False)
    lines = [
        "# CRYPTO A7SEARCH6 Mechanism Memory Seed Proxy Contract 20260630",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "A7SEARCH6 expands the A7SEARCH5 validation result into a bounded OI/positioning mechanism surface. It is proxy-only and does not authorize alpha proof, shadow, paper, or live.",
        "",
        "## Counts",
        "",
        f"- queue_rows: `{manifest['queue_rows']}`",
        f"- semantic_pair_count: `{manifest['semantic_pair_count']}`",
        f"- motif_count: `{manifest['motif_count']}`",
        f"- skeleton_count: `{manifest['skeleton_count']}`",
        "",
        "## Lane Summary",
        "",
        md_table(lane),
        "",
        "## Pair Summary",
        "",
        md_table(pair, 40),
        "",
        "## Motif Summary",
        "",
        md_table(motif, 40),
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--queue-rows", type=int, default=65_536)
    parser.add_argument("--rows-per-shard", type=int, default=512)
    parser.add_argument("--seed", type=int, default=20260630)
    parser.add_argument("--memory-prior", type=Path, default=DEFAULT_MEMORY_PRIOR)
    parser.add_argument("--max-parallel", type=int, default=12)
    parser.add_argument("--min-free-gb", type=float, default=16.0)
    args = parser.parse_args()

    args.runtime.mkdir(parents=True, exist_ok=True)
    queue, trace, manifest = build_queue(
        queue_rows=args.queue_rows,
        seed=args.seed,
        memory_prior=args.memory_prior,
        rows_per_shard=args.rows_per_shard,
    )
    queue_path = args.runtime / "a7search6_proxy_queue.csv"
    queue.to_csv(queue_path, index=False)
    trace.to_csv(args.runtime / "a7search6_memory_enforcement_trace.csv", index=False)

    shard_root = args.runtime / "queue_shards"
    shard_root.mkdir(parents=True, exist_ok=True)
    shard_rows = []
    for idx, start in enumerate(range(0, len(queue), args.rows_per_shard)):
        shard_id = f"a7search6_proxy_s{idx:03d}"
        shard = queue.iloc[start : start + args.rows_per_shard].copy()
        shard.to_csv(shard_root / f"{shard_id}.csv", index=False)
        shard_rows.append(
            {
                "shard_id": shard_id,
                "start_row": start,
                "end_row_exclusive": start + len(shard),
                "rows": len(shard),
            }
        )
    shard_plan = pd.DataFrame(shard_rows)
    shard_plan.to_csv(args.runtime / "a7search6_proxy_shard_plan.csv", index=False)
    supervisor = write_supervisor(args.runtime, args.max_parallel, args.min_free_gb)

    manifest.update(
        {
            "runtime": str(args.runtime),
            "report": str(args.report),
            "queue": str(queue_path),
            "shard_count": int(len(shard_plan)),
            "shard_plan": str(args.runtime / "a7search6_proxy_shard_plan.csv"),
            "supervisor": str(supervisor),
            "max_parallel": int(args.max_parallel),
            "min_free_gb": float(args.min_free_gb),
        }
    )
    write_json(args.runtime / "a7search6_prepare_manifest.json", manifest)
    write_report(args.report, manifest, queue, args.runtime)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
