from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.search_memory_enforcement import SearchMemoryEnforcer  # noqa: E402
from scripts.crypto_a7v3s0_next_large_search_contract import FIELD_SPECS, FORBIDDEN_FIELDS  # noqa: E402


STAGE = "A7SEARCH7"
DEFAULT_RUNTIME = Path(r"H:\AlphaFactory_CryptoData_archive\a7search7_family_diversified_proxy_65k_20260704")
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SEARCH7_FAMILY_DIVERSIFIED_QUEUE_20260704.md"
DEFAULT_MEMORY_PRIOR = REPO / "runtime" / "a7mem0_search_memory_registry_20260628" / "a7mem0_next_search_prior.json"
DEFAULT_SELECTED_PACKET = REPO / "runtime" / "a7shadow7_dedup_review_packet_20260704" / "a7shadow7_selected_review_packet.csv"
DEFAULT_OVERLAP_REJECTIONS = REPO / "runtime" / "a7shadow7_dedup_review_packet_20260704" / "a7shadow7_overlap_rejections.csv"

HORIZONS = [4, 8, 24]
WINDOWS_FAST = [4, 8, 12, 24, 48, 72, 96]
WINDOWS_SLOW = [168, 240, 336, 504]
LANE_TARGET_SHARES = {
    "shadow_positive_prior_light": 0.10,
    "taker_liquidity_mechanism": 0.24,
    "funding_basis_premium_mechanism": 0.22,
    "regime_conditioned_non_oi": 0.20,
    "raw_broad_non_oi": 0.24,
}
MIN_NON_OI_TOUCH_SHARE = 0.60
MAX_OI_TOUCH_SHARE = 0.42
MIN_SEMANTIC_PAIR_COUNT = 8
MIN_MOTIF_COUNT = 10


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short_hash(text: str, n: int = 16) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(frame: pd.DataFrame, max_rows: int = 80) -> str:
    if frame.empty:
        return "`<empty>`"
    view = frame.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def canonical_ast(expr: str) -> str:
    text = re.sub(r"\s+", "", expr)
    for field in sorted(FIELD_SPECS, key=len, reverse=True):
        text = text.replace(field, "FIELD")
    return re.sub(r"\b\d+\b", "W", text)


def available(field: str) -> bool:
    return field in FIELD_SPECS and field not in FORBIDDEN_FIELDS


def semantic(field: str) -> str:
    return str(FIELD_SPECS.get(field, {}).get("semantic", "unknown"))


def fields_by_semantic() -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    for field, spec in FIELD_SPECS.items():
        if available(field):
            out[str(spec.get("semantic", "unknown"))].append(field)
    return {key: sorted(value) for key, value in out.items()}


def transforms(field: str, rng: random.Random, *, rich: bool = True) -> list[tuple[str, str]]:
    windows = list(WINDOWS_FAST + (WINDOWS_SLOW if rich else []))
    rng.shuffle(windows)
    windows = windows[:9 if rich else 5]
    out = [
        (field, "level"),
        (f"CSRank({field})", "csrank"),
        (f"ZScore({field})", "zscore"),
        (f"Sign({field})", "sign"),
        (f"Abs({field})", "abs"),
    ]
    for window in windows:
        out.extend(
            [
                (f"Mean({field},{window})", f"mean_{window}"),
                (f"Delta({field},{window})", f"delta_{window}"),
                (f"ZScore(Mean({field},{window}))", f"zmean_{window}"),
                (f"TSRank({field},{window})", f"tsrank_{window}"),
                (f"Decay({field},{window})", f"decay_{window}"),
                (f"CSRank(Delta({field},{window}))", f"csdelta_{window}"),
            ]
        )
    return out


def pair_key(left: str, right: str) -> str:
    return "|".join(sorted([semantic(left), semantic(right)]))


def choose_lane(rng: random.Random, lane_counts: Counter[str], queue_rows: int) -> str:
    deficits: dict[str, float] = {}
    for lane, share in LANE_TARGET_SHARES.items():
        target = queue_rows * share
        deficits[lane] = max(0.0, target - lane_counts[lane])
    total = sum(deficits.values())
    if total <= 0:
        return rng.choice(list(LANE_TARGET_SHARES))
    mark = rng.random() * total
    running = 0.0
    for lane, deficit in deficits.items():
        running += deficit
        if running >= mark:
            return lane
    return next(iter(LANE_TARGET_SHARES))


def choose_fields(lane: str, by_sem: dict[str, list[str]], rng: random.Random) -> tuple[str, str]:
    oi = by_sem.get("open_interest", [])
    pos = by_sem.get("positioning", [])
    taker = by_sem.get("taker_flow", [])
    liq = by_sem.get("liquidity", [])
    basis = by_sem.get("basis", [])
    premium = by_sem.get("premium", [])
    funding = by_sem.get("funding_dense", []) + by_sem.get("funding_basis", [])
    regime = by_sem.get("regime", [])
    non_oi_signal = taker + liq + basis + premium + funding + pos
    if lane == "shadow_positive_prior_light":
        return rng.choice(oi or non_oi_signal), rng.choice((funding + premium + basis + pos) or non_oi_signal)
    if lane == "taker_liquidity_mechanism":
        return rng.choice(taker or non_oi_signal), rng.choice((liq + basis + premium + funding + pos) or non_oi_signal)
    if lane == "funding_basis_premium_mechanism":
        return rng.choice(funding or premium or basis or non_oi_signal), rng.choice((basis + premium + taker + liq + pos) or non_oi_signal)
    if lane == "regime_conditioned_non_oi":
        return rng.choice(non_oi_signal or regime), rng.choice(regime or funding or basis or premium or non_oi_signal)
    return rng.choice(non_oi_signal or oi), rng.choice(non_oi_signal or regime or oi)


def build_expression(lane: str, left_expr: str, right_expr: str, rng: random.Random) -> tuple[str, str]:
    if lane == "shadow_positive_prior_light":
        templates = [
            (f"SafeDiv({left_expr},Abs({right_expr}))", "positive_prior_safe_div_abs"),
            (f"SafeDiv({left_expr},CSRank({right_expr}))", "positive_prior_safe_div_rank"),
            (f"Mul(CSRank({left_expr}),Sign({right_expr}))", "positive_prior_signed_rank"),
        ]
    elif lane == "taker_liquidity_mechanism":
        templates = [
            (f"Mul(CSRank({left_expr}),CSRank({right_expr}))", "flow_liquidity_rank_mul"),
            (f"Sub(CSRank({left_expr}),CSRank({right_expr}))", "flow_liquidity_spread"),
            (f"Mul(Delta({left_expr},4),Sign({right_expr}))", "flow_shock_gate"),
            (f"SafeDiv(CSRank({left_expr}),Abs(CSRank({right_expr})))", "flow_liquidity_scaled"),
        ]
    elif lane == "funding_basis_premium_mechanism":
        templates = [
            (f"Sub(CSRank({left_expr}),CSRank({right_expr}))", "funding_basis_spread"),
            (f"Mul(CSRank({left_expr}),Sign({right_expr}))", "funding_basis_signed"),
            (f"SafeDiv(Delta({left_expr},8),Abs(CSRank({right_expr})))", "funding_basis_delta_scaled"),
            (f"Mul(ZScore({left_expr}),TSRank({right_expr},24))", "funding_basis_state_mul"),
        ]
    elif lane == "regime_conditioned_non_oi":
        templates = [
            (f"Mul(CSRank({left_expr}),Sign({right_expr}))", "regime_conditioned_sign"),
            (f"Mul(ZScore({left_expr}),CSRank({right_expr}))", "regime_conditioned_rank"),
            (f"SafeDiv({left_expr},Abs(CSRank({right_expr})))", "regime_conditioned_scaled"),
        ]
    else:
        templates = [
            (f"Add(CSRank({left_expr}),CSRank({right_expr}))", "raw_add_rank"),
            (f"Sub(CSRank({left_expr}),CSRank({right_expr}))", "raw_spread_rank"),
            (f"Mul(CSRank({left_expr}),CSRank({right_expr}))", "raw_rank_mul"),
            (f"SafeDiv({left_expr},Abs({right_expr}))", "raw_safe_div_abs"),
            (f"Mul({left_expr},Sign({right_expr}))", "raw_signed_gate"),
        ]
    return rng.choice(templates)


def read_existing_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def build_queue(
    *,
    queue_rows: int,
    rows_per_shard: int,
    seed: int,
    memory_prior: Path,
    selected_packet: Path,
    overlap_rejections: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    rng = random.Random(seed)
    enforcer = SearchMemoryEnforcer(prior_path=memory_prior)
    by_sem = fields_by_semantic()
    selected = read_existing_csv(selected_packet)
    rejections = read_existing_csv(overlap_rejections)
    rejected_expressions = set(rejections.get("expression", pd.Series(dtype=str)).dropna().astype(str))
    selected_expressions = selected.get("expression", pd.Series(dtype=str)).dropna().astype(str).tolist()

    rows: list[dict[str, Any]] = []
    trace_rows: list[dict[str, Any]] = []
    seen_expr: set[str] = set(rejected_expressions)
    lane_counts: Counter[str] = Counter()
    semantic_counts: Counter[str] = Counter()
    motif_counts: Counter[str] = Counter()
    skeleton_counts: Counter[str] = Counter()
    memory_action_counts: Counter[str] = Counter()
    memory_reject_counts: Counter[str] = Counter()
    memory_expression_counter: Counter[str] = Counter()
    memory_shard_counters: dict[int, dict[str, Counter[str]]] = defaultdict(lambda: {"skeleton_key": Counter(), "pair_motif": Counter()})
    attempts = 0
    max_attempts = queue_rows * 220
    skeleton_global_cap = max(64, int(queue_rows * 0.006))
    semantic_pair_cap = max(512, int(queue_rows * 0.16))
    oi_touch_cap = int(queue_rows * MAX_OI_TOUCH_SHARE)
    oi_touch_count = 0

    while len(rows) < queue_rows and attempts < max_attempts:
        attempts += 1
        lane = choose_lane(rng, lane_counts, queue_rows)
        if lane == "shadow_positive_prior_light" and selected_expressions and rng.random() < 0.20:
            base_expr = rng.choice(selected_expressions)
            expr, motif = rng.choice(
                [
                    (base_expr, "shadow_selected_exact_probe"),
                    (f"CSRank({base_expr})", "shadow_selected_rank_wrap"),
                    (f"Sign({base_expr})", "shadow_selected_sign_wrap"),
                ]
            )
            left_field, right_field = "open_interest_value_last", "funding_rate_delta_state_24h"
            semantic_pair = "funding_dense|open_interest"
            left_motif = "selected"
            right_motif = "selected"
        else:
            left_field, right_field = choose_fields(lane, by_sem, rng)
            if not available(left_field) or not available(right_field):
                continue
            semantic_pair = pair_key(left_field, right_field)
            left_expr, left_motif = rng.choice(transforms(left_field, rng, rich=True))
            right_expr, right_motif = rng.choice(transforms(right_field, rng, rich=True))
            expr, motif = build_expression(lane, left_expr, right_expr, rng)
        if expr in seen_expr:
            continue
        skeleton = canonical_ast(expr)
        if skeleton_counts[skeleton] >= skeleton_global_cap:
            continue
        if semantic_counts[semantic_pair] >= semantic_pair_cap:
            continue
        touches_oi = "open_interest" in semantic_pair
        if touches_oi and oi_touch_count >= oi_touch_cap:
            continue
        horizon = rng.choice(HORIZONS)
        row = {
            "blueprint_id": f"a7search7_{short_hash(str(len(rows)) + '|' + expr)}",
            "expression": expr,
            "semantic_pair": semantic_pair,
            "motif": motif,
            "horizon_h": horizon,
            "search_policy": lane,
            "search_core": "family_diversified_memory_surface",
            "ast_path": f"{lane}/{semantic_pair}/{motif}/{left_motif}/{right_motif}",
            "ast_skeleton": skeleton,
            "skeleton_key": skeleton,
            "primary_field": left_field,
            "secondary_field": right_field,
            "primary_semantic": semantic(left_field),
            "secondary_semantic": semantic(right_field),
            "left_transform_motif": left_motif,
            "right_transform_motif": right_motif,
            "candidate_origin": "a7shadow7_dedup_and_a7live1_source_lag_authorized",
            "reward_feedback_source": "a7shadow7_selected_positive_rejections_negative",
            "overlap_rejection_memory_applied": str(bool(rejected_expressions)),
            "authorizes": "proxy_only",
        }
        shard_bucket = len(rows) // max(1, rows_per_shard)
        counters = {
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
        semantic_counts[semantic_pair] += 1
        motif_counts[motif] += 1
        skeleton_counts[skeleton] += 1
        if touches_oi:
            oi_touch_count += 1

    queue = pd.DataFrame(rows)
    trace = pd.DataFrame(trace_rows)
    if queue.empty:
        non_oi_touch_share = 0.0
        oi_touch_share = 0.0
    else:
        oi_touch_share = float(queue["semantic_pair"].astype(str).str.contains("open_interest").mean())
        non_oi_touch_share = 1.0 - oi_touch_share
    blockers: list[str] = []
    if len(queue) != queue_rows:
        blockers.append("queue_underfilled")
    if oi_touch_share > MAX_OI_TOUCH_SHARE:
        blockers.append("oi_touch_share_above_cap")
    if non_oi_touch_share < MIN_NON_OI_TOUCH_SHARE:
        blockers.append("non_oi_touch_share_below_floor")
    if queue["semantic_pair"].nunique() < MIN_SEMANTIC_PAIR_COUNT:
        blockers.append("semantic_pair_count_below_floor")
    if queue["motif"].nunique() < MIN_MOTIF_COUNT:
        blockers.append("motif_count_below_floor")

    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": "PASS_A7SEARCH7_FAMILY_DIVERSIFIED_QUEUE_READY" if not blockers else "HOLD_A7SEARCH7_QUEUE_COVERAGE_BLOCKED",
        "queue_rows_requested": int(queue_rows),
        "queue_rows": int(len(queue)),
        "rows_per_shard": int(rows_per_shard),
        "attempts": int(attempts),
        "seed": int(seed),
        "lane_target_shares": LANE_TARGET_SHARES,
        "lane_counts": dict(lane_counts),
        "semantic_pair_count": int(queue["semantic_pair"].nunique()) if not queue.empty else 0,
        "motif_count": int(queue["motif"].nunique()) if not queue.empty else 0,
        "skeleton_count": int(queue["skeleton_key"].nunique()) if not queue.empty else 0,
        "oi_touch_share": oi_touch_share,
        "non_oi_touch_share": non_oi_touch_share,
        "blockers": blockers,
        "selected_packet": str(selected_packet),
        "overlap_rejections": str(overlap_rejections),
        "overlap_rejection_rows": int(rejections.shape[0]),
        "memory_prior": str(memory_prior),
        "memory_action_counts": dict(memory_action_counts),
        "memory_reject_counts": dict(memory_reject_counts),
        "authorizes_proxy_search": not blockers,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    return queue, trace, manifest


def write_supervisor(runtime: Path, max_parallel: int, min_free_gb: float) -> Path:
    path = runtime / "a7search7_proxy_supervisor.ps1"
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
$StatusPath = Join-Path $RunRoot "a7search7_proxy_supervisor_status.csv"
"shard_id,status,start_time,end_time,exit_code,notes" | Set-Content -Path $StatusPath -Encoding utf8

function FreeGb {{
  $os = Get-CimInstance Win32_OperatingSystem
  return [math]::Round($os.FreePhysicalMemory / 1024 / 1024, 2)
}}

Set-Location $Repo
$shards = Import-Csv (Join-Path $RunRoot "a7search7_proxy_shard_plan.csv")
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


def write_report(report: Path, runtime: Path, manifest: dict[str, Any], queue: pd.DataFrame) -> None:
    lane = queue.groupby("search_policy", dropna=False).size().reset_index(name="rows").sort_values("rows", ascending=False)
    pair = queue.groupby("semantic_pair", dropna=False).size().reset_index(name="rows").sort_values("rows", ascending=False)
    motif = queue.groupby("motif", dropna=False).size().reset_index(name="rows").sort_values("rows", ascending=False)
    sem_touch = (
        pd.concat(
            [
                queue[["primary_semantic"]].rename(columns={"primary_semantic": "semantic"}),
                queue[["secondary_semantic"]].rename(columns={"secondary_semantic": "semantic"}),
            ],
            ignore_index=True,
        )
        .groupby("semantic", dropna=False)
        .size()
        .reset_index(name="touches")
        .sort_values("touches", ascending=False)
    )
    lane.to_csv(runtime / "a7search7_lane_summary.csv", index=False)
    pair.to_csv(runtime / "a7search7_pair_summary.csv", index=False)
    motif.to_csv(runtime / "a7search7_motif_summary.csv", index=False)
    sem_touch.to_csv(runtime / "a7search7_semantic_touch_summary.csv", index=False)
    lines = [
        "# CRYPTO A7SEARCH7 Family Diversified Queue",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "A7SEARCH7 builds a checkpointable proxy queue after A7SHADOW-7 dedupe and A7LIVE-1 source-lag authorization. It is proxy-only and does not authorize alpha proof, shadow, paper, or live.",
        "",
        "## Counts",
        "",
        f"- queue_rows: `{manifest['queue_rows']}` / `{manifest['queue_rows_requested']}`",
        f"- semantic_pair_count: `{manifest['semantic_pair_count']}`",
        f"- motif_count: `{manifest['motif_count']}`",
        f"- skeleton_count: `{manifest['skeleton_count']}`",
        f"- oi_touch_share: `{manifest['oi_touch_share']}`",
        f"- non_oi_touch_share: `{manifest['non_oi_touch_share']}`",
        f"- blockers: `{';'.join(manifest['blockers']) or 'none'}`",
        "",
        "## Lane Summary",
        "",
        md_table(lane),
        "",
        "## Semantic Pair Summary",
        "",
        md_table(pair, 60),
        "",
        "## Motif Summary",
        "",
        md_table(motif, 60),
        "",
        "## Semantic Touch Summary",
        "",
        md_table(sem_touch),
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--queue-rows", type=int, default=65_536)
    parser.add_argument("--rows-per-shard", type=int, default=512)
    parser.add_argument("--seed", type=int, default=20260704)
    parser.add_argument("--memory-prior", type=Path, default=DEFAULT_MEMORY_PRIOR)
    parser.add_argument("--selected-packet", type=Path, default=DEFAULT_SELECTED_PACKET)
    parser.add_argument("--overlap-rejections", type=Path, default=DEFAULT_OVERLAP_REJECTIONS)
    parser.add_argument("--max-parallel", type=int, default=12)
    parser.add_argument("--min-free-gb", type=float, default=10.0)
    args = parser.parse_args()

    args.runtime.mkdir(parents=True, exist_ok=True)
    queue, trace, manifest = build_queue(
        queue_rows=args.queue_rows,
        rows_per_shard=args.rows_per_shard,
        seed=args.seed,
        memory_prior=args.memory_prior,
        selected_packet=args.selected_packet,
        overlap_rejections=args.overlap_rejections,
    )
    queue_path = args.runtime / "a7search7_proxy_queue.csv"
    queue.to_csv(queue_path, index=False)
    trace.to_csv(args.runtime / "a7search7_memory_enforcement_trace.csv", index=False)

    shard_root = args.runtime / "queue_shards"
    shard_root.mkdir(parents=True, exist_ok=True)
    shard_rows = []
    for idx, start in enumerate(range(0, len(queue), args.rows_per_shard)):
        shard_id = f"a7search7_proxy_s{idx:03d}"
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
    shard_plan.to_csv(args.runtime / "a7search7_proxy_shard_plan.csv", index=False)
    supervisor = write_supervisor(args.runtime, args.max_parallel, args.min_free_gb)
    manifest.update(
        {
            "runtime": str(args.runtime),
            "report": str(args.report),
            "queue": str(queue_path),
            "shard_count": int(len(shard_plan)),
            "shard_plan": str(args.runtime / "a7search7_proxy_shard_plan.csv"),
            "supervisor": str(supervisor),
            "max_parallel": int(args.max_parallel),
            "min_free_gb": float(args.min_free_gb),
        }
    )
    write_json(args.runtime / "a7search7_prepare_manifest.json", manifest)
    write_report(args.report, args.runtime, manifest, queue)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
