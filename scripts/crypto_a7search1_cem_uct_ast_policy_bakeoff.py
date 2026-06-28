from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(REPO))

from scripts.crypto_a7v3s0_next_large_search_contract import FIELD_SPECS, FORBIDDEN_FIELDS, WINDOWS_ALL  # noqa: E402
from alphafactory_crypto.engines.search_memory_enforcement import SearchMemoryEnforcer  # noqa: E402


STAGE = "A7SEARCH1"
DEFAULT_RUNTIME = REPO / "runtime" / "a7search1_cem_uct_ast_policy_bakeoff_20260618"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SEARCH1_CEM_UCT_AST_POLICY_BAKEOFF_20260618.md"
DEFAULT_PRIORS = [
    REPO / "runtime" / "a7v3s9_selected_full_reward_aggregate_20260614" / "a7v3s0_reward_accepted_enriched.csv",
    REPO / "runtime" / "a7v3s0_reward_sharded_720h_r2_aggregate_20260613" / "a7v3s0_reward_accepted_enriched.csv",
    REPO / "runtime" / "a7reward1_portfolio_reward_model_20260610" / "a7reward1_accepted_for_next_search.csv",
]

TRANSFORM_OPS = ["Mean", "Delta", "TSRank", "Decay", "ZScore", "CSRank", "Abs", "Sign"]
INTERACTION_OPS = ["SafeDiv", "Sub", "Mul", "Add"]
HORIZONS = [4, 8, 24]

POLICY_TARGET_SHARE = {
    "cem_ast_prior": 0.34,
    "uct_ast_tree": 0.34,
    "raw_ast_explore": 0.20,
    "map_elites_diversity": 0.12,
}

SEMANTIC_COMPATIBILITY = {
    ("basis", "funding_dense"),
    ("basis", "funding_sparse"),
    ("basis", "open_interest"),
    ("basis", "positioning"),
    ("basis", "taker_flow"),
    ("basis", "regime"),
    ("premium", "funding_dense"),
    ("premium", "open_interest"),
    ("premium", "positioning"),
    ("premium", "taker_flow"),
    ("funding_dense", "open_interest"),
    ("funding_dense", "positioning"),
    ("funding_dense", "taker_flow"),
    ("open_interest", "positioning"),
    ("open_interest", "taker_flow"),
    ("open_interest", "regime"),
    ("positioning", "taker_flow"),
    ("positioning", "regime"),
    ("taker_flow", "regime"),
    ("liquidity", "basis"),
    ("liquidity", "funding_dense"),
    ("liquidity", "open_interest"),
    ("liquidity", "positioning"),
    ("liquidity", "taker_flow"),
    ("age", "open_interest"),
    ("age", "positioning"),
    ("age", "taker_flow"),
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short_hash(text: str, n: int = 16) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```text\n" + view.to_string(index=False) + "\n```"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception:
        return pd.DataFrame()


def expression_tokens(expression: str) -> tuple[list[str], list[int]]:
    ops = re.findall(r"\b([A-Z][A-Za-z0-9_]*)\s*\(", expression or "")
    windows = [int(x) for x in re.findall(r",\s*(\d+)\s*\)", expression or "")]
    return ops, windows


def semantic_pair(a: str, b: str) -> str:
    return "|".join(sorted([a, b]))


def canonical_ast(expr: str) -> str:
    text = re.sub(r"\s+", "", expr)
    for field in sorted(FIELD_SPECS, key=len, reverse=True):
        text = text.replace(field, "FIELD")
    text = re.sub(r"\b\d+\b", "W", text)
    return text


def weighted_choice(rng: random.Random, weights: dict[str, float]) -> str:
    items = [(key, max(0.0, float(value))) for key, value in weights.items()]
    total = sum(value for _, value in items)
    if total <= 0:
        return sorted(weights)[rng.randrange(len(weights))]
    mark = rng.random() * total
    running = 0.0
    for key, value in sorted(items):
        running += value
        if running >= mark:
            return key
    return items[-1][0]


def available_field_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for field, spec in FIELD_SPECS.items():
        if field in FORBIDDEN_FIELDS:
            continue
        semantic = str(spec.get("semantic", "unknown"))
        role = str(spec.get("role", "unknown"))
        if semantic in {"universe_state"}:
            continue
        rows.append({"field": field, "semantic": semantic, "role": role})
    return rows


def load_priors(paths: list[Path]) -> tuple[pd.DataFrame, dict[str, Counter]]:
    frames = []
    for path in paths:
        frame = read_csv(path)
        if not frame.empty:
            frame["prior_source"] = str(path)
            frames.append(frame)
    priors = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    counters: dict[str, Counter] = {
        "semantic_pair": Counter(),
        "motif": Counter(),
        "operator": Counter(),
        "window": Counter(),
        "horizon": Counter(),
    }
    if priors.empty:
        return priors, counters
    for row in priors.to_dict("records"):
        pair = str(row.get("semantic_pair", "") or "")
        motif = str(row.get("motif", "") or "")
        horizon = str(row.get("horizon_h", "") or "")
        if pair:
            counters["semantic_pair"][pair] += 1
        if motif:
            counters["motif"][motif] += 1
        if horizon:
            counters["horizon"][horizon] += 1
        ops, windows = expression_tokens(str(row.get("expression", "") or ""))
        counters["operator"].update(ops)
        counters["window"].update(map(str, windows))
    return priors, counters


def prior_weights(values: list[str], counter: Counter, floor: float = 1.0, boost: float = 7.0) -> dict[str, float]:
    return {value: floor + boost * math.log1p(counter.get(value, 0)) for value in values}


def transform_ast(field: str, semantic: str, rng: random.Random, counters: dict[str, Counter], policy: str) -> tuple[dict[str, Any], str, str]:
    op_weights = prior_weights(TRANSFORM_OPS, counters["operator"], floor=1.0, boost=3.0)
    if policy in {"raw_ast_explore", "map_elites_diversity"}:
        op_weights = {op: 1.0 for op in TRANSFORM_OPS}
    if semantic in {"age", "regime"}:
        allowed = ["CSRank", "TSRank", "Decay", "Sign"]
    elif semantic in {"funding_sparse", "funding_dense", "funding_basis"}:
        allowed = ["Mean", "Delta", "TSRank", "Decay", "ZScore", "Abs"]
    else:
        allowed = TRANSFORM_OPS
    op = weighted_choice(rng, {k: v for k, v in op_weights.items() if k in allowed})
    window_weights = prior_weights([str(w) for w in WINDOWS_ALL], counters["window"], floor=1.0, boost=2.0)
    window = int(weighted_choice(rng, window_weights))
    leaf = {"node_type": "Field", "field_name": field}
    if op == "Mean":
        ast = {"node_type": "Transform", "operator": "Mean", "args": [leaf, {"node_type": "Const", "value": window}]}
        motif = "mean"
    elif op == "Delta":
        ast = {"node_type": "Transform", "operator": "Delta", "args": [leaf, {"node_type": "Const", "value": window}]}
        motif = "delta"
    elif op == "TSRank":
        ast = {"node_type": "Transform", "operator": "TSRank", "args": [leaf, {"node_type": "Const", "value": window}]}
        motif = "tsrank"
    elif op == "Decay":
        ast = {"node_type": "Transform", "operator": "Decay", "args": [leaf, {"node_type": "Const", "value": window}]}
        motif = "decay"
    elif op == "ZScore":
        ast = {"node_type": "Transform", "operator": "ZScore", "args": [leaf]}
        motif = "zscore"
    elif op == "CSRank":
        ast = {"node_type": "Transform", "operator": "CSRank", "args": [leaf]}
        motif = "csrank"
    elif op == "Abs":
        inner = {"node_type": "Transform", "operator": "ZScore", "args": [leaf]}
        ast = {"node_type": "Transform", "operator": "Abs", "args": [inner]}
        motif = "abs_zscore"
    else:
        inner = {"node_type": "Transform", "operator": "Delta", "args": [leaf, {"node_type": "Const", "value": window}]}
        ast = {"node_type": "Transform", "operator": "Sign", "args": [inner]}
        motif = "sign_delta"
    return ast, motif, str(window)


def render_ast(ast: dict[str, Any]) -> str:
    node_type = ast.get("node_type")
    if node_type == "Field":
        return str(ast["field_name"])
    if node_type == "Const":
        return str(ast["value"])
    op = str(ast["operator"])
    args = ",".join(render_ast(arg) for arg in ast.get("args", []))
    return f"{op}({args})"


def interaction_ast(left: dict[str, Any], right: dict[str, Any], rng: random.Random, counters: dict[str, Counter], policy: str) -> tuple[dict[str, Any], str]:
    op_weights = prior_weights(INTERACTION_OPS, counters["operator"], floor=1.0, boost=4.0)
    if policy == "raw_ast_explore":
        op_weights = {op: 1.0 for op in INTERACTION_OPS}
    op = weighted_choice(rng, op_weights)
    if op == "SafeDiv":
        denom = {"node_type": "Transform", "operator": "Abs", "args": [right]}
        return {"node_type": "Interaction", "operator": "SafeDiv", "args": [left, denom]}, "safe_div_abs"
    if op == "Sub":
        return {"node_type": "Interaction", "operator": "Sub", "args": [left, right]}, "spread"
    if op == "Mul":
        return {"node_type": "Interaction", "operator": "Mul", "args": [left, right]}, "smooth_mul"
    return {"node_type": "Interaction", "operator": "Add", "args": [left, right]}, "additive_composite"


def uct_score(total_visits: int, wins: float, visits: int, c: float = 1.7) -> float:
    if visits <= 0:
        return float("inf")
    return wins / visits + c * math.sqrt(math.log(max(2, total_visits)) / visits)


def choose_pair(
    rng: random.Random,
    fields: list[dict[str, str]],
    counters: dict[str, Counter],
    policy: str,
    path_stats: dict[str, dict[str, float]],
) -> tuple[dict[str, str], dict[str, str], str]:
    semantic_values = sorted({row["semantic"] for row in fields})
    all_pairs = [semantic_pair(a, b) for a in semantic_values for b in semantic_values if a <= b]
    compatible = set(semantic_pair(a, b) for a, b in SEMANTIC_COMPATIBILITY)
    compatible |= {semantic_pair(a, a) for a in semantic_values if a not in {"age", "regime"}}
    pair_candidates = [pair for pair in all_pairs if pair in compatible]
    if policy == "cem_ast_prior":
        pair = weighted_choice(rng, prior_weights(pair_candidates, counters["semantic_pair"], floor=1.0, boost=8.0))
    elif policy == "uct_ast_tree":
        total = sum(int(v.get("visits", 0)) for v in path_stats.values()) + 1
        scored = []
        for pair_value in pair_candidates:
            stats = path_stats.get(pair_value, {"wins": float(counters["semantic_pair"].get(pair_value, 0)), "visits": float(counters["semantic_pair"].get(pair_value, 0))})
            scored.append((uct_score(total, float(stats.get("wins", 0.0)), int(stats.get("visits", 0))), pair_value))
        scored.sort(reverse=True)
        top = scored[: max(8, min(64, len(scored)))]
        pair = rng.choice([x[1] for x in top])
    elif policy == "map_elites_diversity":
        counts = counters["semantic_pair"]
        least = sorted(pair_candidates, key=lambda x: counts.get(x, 0))[: max(16, min(96, len(pair_candidates)))]
        pair = rng.choice(least)
    else:
        pair = rng.choice(pair_candidates)
    left_sem, right_sem = pair.split("|")
    left_pool = [row for row in fields if row["semantic"] == left_sem]
    right_pool = [row for row in fields if row["semantic"] == right_sem]
    return rng.choice(left_pool), rng.choice(right_pool), pair


def build_queue(
    *,
    stage_label: str,
    queue_rows: int,
    seed: int,
    prior_paths: list[Path],
    entropy_floor: float,
    skeleton_cap: int,
    max_pair_share: float,
    max_field_share: float,
    memory_prior_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame, pd.DataFrame]:
    rng = random.Random(seed)
    fields = available_field_rows()
    priors, counters = load_priors(prior_paths)
    path_stats: dict[str, dict[str, float]] = {}
    for pair, count in counters["semantic_pair"].items():
        path_stats[pair] = {"wins": float(count), "visits": float(max(1, count))}

    target_counts = {policy: int(queue_rows * share) for policy, share in POLICY_TARGET_SHARE.items()}
    while sum(target_counts.values()) < queue_rows:
        target_counts["raw_ast_explore"] += 1

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    policy_counts = Counter()
    pair_counts = Counter()
    skeleton_counts = Counter()
    field_counts = Counter()
    memory_enforcer = SearchMemoryEnforcer(prior_path=memory_prior_path) if memory_prior_path else None
    memory_counters: dict[str, Counter[str]] = {
        "expression_key": Counter(),
        "skeleton_key": Counter(),
        "pair_motif": Counter(),
    }
    memory_trace_rows: list[dict[str, Any]] = []
    memory_reject_counts: Counter[str] = Counter()
    memory_action_counts: Counter[str] = Counter()
    max_skeleton_count = int(skeleton_cap)
    attempts = 0
    max_attempts = queue_rows * 80

    policies = list(target_counts)
    while len(rows) < queue_rows and attempts < max_attempts:
        attempts += 1
        available_policies = [p for p in policies if policy_counts[p] < target_counts[p]]
        if not available_policies:
            break
        policy = rng.choice(available_policies)
        left, right, pair = choose_pair(rng, fields, counters, policy, path_stats)
        left_ast, left_motif, left_window = transform_ast(left["field"], left["semantic"], rng, counters, policy)
        right_ast, right_motif, right_window = transform_ast(right["field"], right["semantic"], rng, counters, policy)
        ast, interaction_motif = interaction_ast(left_ast, right_ast, rng, counters, policy)
        if rng.random() < 0.22 and policy in {"uct_ast_tree", "cem_ast_prior"}:
            gate_field = rng.choice([row for row in fields if row["semantic"] in {"regime", "age", "liquidity"}])
            gate_ast, gate_motif, gate_window = transform_ast(gate_field["field"], gate_field["semantic"], rng, counters, policy)
            ast = {"node_type": "Interaction", "operator": "Mul", "args": [ast, {"node_type": "Transform", "operator": "Sign", "args": [gate_ast]}]}
            interaction_motif = f"{interaction_motif}_gated"
        expr = render_ast(ast)
        if expr in seen:
            continue
        skeleton = canonical_ast(expr)
        if skeleton_counts[skeleton] >= max_skeleton_count:
            continue
        if pair_counts[pair] >= int(queue_rows * max_pair_share):
            continue
        if field_counts[left["field"]] >= int(queue_rows * max_field_share):
            continue
        if field_counts[right["field"]] >= int(queue_rows * max_field_share):
            continue
        path = f"{policy}/{pair}/{interaction_motif}/{left_motif}:{left_window}/{right_motif}:{right_window}"
        horizon = int(weighted_choice(rng, prior_weights([str(h) for h in HORIZONS], counters["horizon"], floor=entropy_floor, boost=3.0)))
        candidate = {
            "blueprint_id": f"a7search1_{short_hash(str(len(rows)) + '|' + expr, 16)}",
            "expression": expr,
            "semantic_pair": pair,
            "motif": interaction_motif,
            "horizon_h": horizon,
            "search_policy": policy,
            "search_core": "cem_uct_policy_over_typed_ast",
            "ast_path": path,
            "ast_skeleton": skeleton,
            "primary_field": left["field"],
            "secondary_field": right["field"],
            "primary_semantic": left["semantic"],
            "secondary_semantic": right["semantic"],
            "left_transform_motif": left_motif,
            "right_transform_motif": right_motif,
            "left_window": left_window,
            "right_window": right_window,
            "candidate_origin": "generated_search_policy",
            "reward_feedback_source": "strict_accepted_prior" if policy == "cem_ast_prior" else "policy_exploration",
            "authorizes": "proxy_only",
        }
        if memory_enforcer is not None:
            decision = memory_enforcer.decide(candidate, memory_counters)
            memory_trace_rows.append({"attempt": attempts, **candidate, **decision.as_row()})
            memory_action_counts[decision.action] += 1
            memory_reject_counts[decision.reason] += 1
            if not decision.allowed:
                continue
            candidate.update(decision.as_row())
            memory_counters["expression_key"][decision.expression_key] += 1
            memory_counters["skeleton_key"][decision.skeleton_key] += 1
            memory_counters["pair_motif"][decision.pair_motif] += 1
        policy_counts[policy] += 1
        pair_counts[pair] += 1
        skeleton_counts[skeleton] += 1
        field_counts[left["field"]] += 1
        field_counts[right["field"]] += 1
        seen.add(expr)
        rows.append(candidate)

    queue = pd.DataFrame(rows)
    prior_summary = pd.DataFrame(
        [
            {"counter": name, "key": key, "count": value}
            for name, counter in counters.items()
            for key, value in counter.most_common(100)
        ]
    )
    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": "PASS_A7SEARCH1_CEM_UCT_AST_QUEUE_READY_FOR_PROXY",
        "queue_rows_requested": int(queue_rows),
        "queue_rows": int(len(queue)),
        "seed": int(seed),
        "policy_target_share": POLICY_TARGET_SHARE,
        "policy_counts": dict(policy_counts),
        "semantic_pair_count": int(queue["semantic_pair"].nunique()) if not queue.empty else 0,
        "motif_count": int(queue["motif"].nunique()) if not queue.empty else 0,
        "skeleton_count": int(queue["ast_skeleton"].nunique()) if not queue.empty else 0,
        "prior_rows": int(len(priors)),
        "prior_paths": [str(path) for path in prior_paths],
        "entropy_floor": float(entropy_floor),
        "skeleton_cap": int(skeleton_cap),
        "max_pair_share": float(max_pair_share),
        "max_field_share": float(max_field_share),
        "does_not_authorize": ["alpha_proof", "shadow_paper_live", "strict_acceptance_without_reward"],
        "memory_enforcement": {
            "enabled": memory_enforcer is not None,
            "prior_path": str(memory_prior_path) if memory_prior_path else "",
            "trace_rows": len(memory_trace_rows),
            "action_counts": dict(memory_action_counts),
            "reason_counts": dict(memory_reject_counts),
        },
    }
    manifest["stage"] = stage_label
    if len(queue) < queue_rows:
        manifest["decision"] = "HOLD_A7SEARCH1_QUEUE_UNDERFILLED"
        manifest["blocker"] = "caps_or_attempt_budget_exhausted"
    memory_trace = pd.DataFrame(memory_trace_rows)
    return queue, manifest, prior_summary, memory_trace


def write_launcher(runtime: Path, shard_plan: pd.DataFrame, max_parallel: int) -> Path:
    launcher = runtime / "a7search1_proxy_launcher.ps1"
    lines = [
        "$ErrorActionPreference = 'Stop'",
        "$Repo = 'D:\\HermesWorker\\GDrive\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519_remote'",
        "$Python = 'D:\\HermesWorker\\workspace\\.venv\\Scripts\\python.exe'",
        f"$RunRoot = '{runtime}'",
        f"$MaxParallel = {max_parallel}",
        "$StatusPath = Join-Path $RunRoot 'a7search1_proxy_status.csv'",
        "\"shard_id,status,start_time,end_time,exit_code\" | Set-Content -Path $StatusPath -Encoding utf8",
        "Set-Location $Repo",
        "$jobs = @()",
        f"$ShardIds = @({','.join([repr(str(x)) for x in shard_plan['shard_id'].tolist()])})",
        "foreach ($ShardId in $ShardIds) {",
        "  while (($jobs | Where-Object { $_.HasExited -eq $false }).Count -ge $MaxParallel) { Start-Sleep -Seconds 20 }",
        "  $Queue = Join-Path $RunRoot \"queue_shards\\$ShardId.csv\"",
        "  $ShardRoot = Join-Path $RunRoot \"shards\\$ShardId\"",
        "  New-Item -ItemType Directory -Force -Path $ShardRoot | Out-Null",
        "  $Runtime = Join-Path $ShardRoot 'proxy_runtime'",
        "  $Report = Join-Path $ShardRoot \"CRYPTO_${ShardId}_PROXY.md\"",
        "  Add-Content -Path $StatusPath -Value \"$ShardId,running,$((Get-Date).ToString('s')),,\"",
        "  $Args = @('scripts\\crypto_a7v3s9_prereward_oos_control_proxy.py','--queue',$Queue,'--runtime',$Runtime,'--report',$Report,'--candidate-cap','0','--successive-halving','--halving-keep-rows','128','--checkpoint-every','64','--select-target','128','--pair-cap','24','--motif-cap','64','--skeleton-cap','3')",
        "  $Out = Join-Path $ShardRoot 'runner.out.log'",
        "  $Err = Join-Path $ShardRoot 'runner.err.log'",
        "  $p = Start-Process -FilePath $Python -ArgumentList $Args -WorkingDirectory $Repo -RedirectStandardOutput $Out -RedirectStandardError $Err -PassThru -WindowStyle Hidden",
        "  $p | Add-Member -NotePropertyName ShardId -NotePropertyValue $ShardId",
        "  $jobs += $p",
        "}",
        "foreach ($j in $jobs) {",
        "  $j.WaitForExit()",
        "  Add-Content -Path $StatusPath -Value \"$($j.ShardId),finished,,$((Get-Date).ToString('s')),$($j.ExitCode)\"",
        "}",
    ]
    launcher.write_text("\n".join(lines), encoding="utf-8")
    return launcher


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", default=str(DEFAULT_RUNTIME))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--stage-label", default=STAGE)
    parser.add_argument("--queue-rows", type=int, default=131_072)
    parser.add_argument("--rows-per-shard", type=int, default=512)
    parser.add_argument("--seed", type=int, default=20260618)
    parser.add_argument("--max-parallel", type=int, default=8)
    parser.add_argument("--entropy-floor", type=float, default=1.0)
    parser.add_argument("--skeleton-cap", type=int, default=512)
    parser.add_argument("--max-pair-share", type=float, default=0.16)
    parser.add_argument("--max-field-share", type=float, default=0.22)
    parser.add_argument("--prior", action="append", default=[])
    parser.add_argument(
        "--memory-prior",
        default=str(REPO / "runtime" / "a7mem0_search_memory_registry_20260628" / "a7mem0_next_search_prior.json"),
        help="A7MEM next-search prior. Use --no-memory-enforcement only for legacy reproduction.",
    )
    parser.add_argument("--no-memory-enforcement", action="store_true")
    args = parser.parse_args()

    runtime = Path(args.runtime)
    report = Path(args.report)
    runtime.mkdir(parents=True, exist_ok=True)
    prior_paths = [Path(p) for p in args.prior] if args.prior else DEFAULT_PRIORS
    memory_prior_path = None if args.no_memory_enforcement else Path(args.memory_prior)
    queue, manifest, prior_summary, memory_trace = build_queue(
        queue_rows=args.queue_rows,
        stage_label=args.stage_label,
        seed=args.seed,
        prior_paths=prior_paths,
        entropy_floor=args.entropy_floor,
        skeleton_cap=args.skeleton_cap,
        max_pair_share=args.max_pair_share,
        max_field_share=args.max_field_share,
        memory_prior_path=memory_prior_path,
    )
    queue_path = runtime / "a7search1_cem_uct_ast_queue.csv"
    queue.to_csv(queue_path, index=False)
    prior_summary.to_csv(runtime / "a7search1_prior_summary.csv", index=False)
    if not memory_trace.empty:
        memory_trace.to_csv(runtime / "a7search1_memory_enforcement_trace.csv", index=False)
    policy_summary = queue.groupby("search_policy", dropna=False).size().reset_index(name="rows")
    pair_summary = queue.groupby(["search_policy", "semantic_pair"], dropna=False).size().reset_index(name="rows").sort_values("rows", ascending=False)
    motif_summary = queue.groupby(["search_policy", "motif"], dropna=False).size().reset_index(name="rows").sort_values("rows", ascending=False)
    policy_summary.to_csv(runtime / "a7search1_policy_summary.csv", index=False)
    pair_summary.to_csv(runtime / "a7search1_pair_summary.csv", index=False)
    motif_summary.to_csv(runtime / "a7search1_motif_summary.csv", index=False)

    queue_shards = runtime / "queue_shards"
    queue_shards.mkdir(parents=True, exist_ok=True)
    shard_rows = []
    for idx, start in enumerate(range(0, len(queue), args.rows_per_shard)):
        shard_id = f"a7search1_proxy_s{idx:03d}"
        shard = queue.iloc[start : start + args.rows_per_shard].copy()
        shard.to_csv(queue_shards / f"{shard_id}.csv", index=False)
        shard_rows.append({"shard_id": shard_id, "start_row": start, "end_row_exclusive": start + len(shard), "rows": len(shard)})
    shard_plan = pd.DataFrame(shard_rows)
    shard_plan.to_csv(runtime / "a7search1_proxy_shard_plan.csv", index=False)
    launcher = write_launcher(runtime, shard_plan, args.max_parallel)

    manifest.update(
        {
            "rows_per_shard": int(args.rows_per_shard),
            "shard_count": int(len(shard_plan)),
            "max_parallel": int(args.max_parallel),
            "outputs": {
                "queue": str(queue_path),
                "shard_plan": str(runtime / "a7search1_proxy_shard_plan.csv"),
                "launcher": str(launcher),
                "policy_summary": str(runtime / "a7search1_policy_summary.csv"),
                "pair_summary": str(runtime / "a7search1_pair_summary.csv"),
                "motif_summary": str(runtime / "a7search1_motif_summary.csv"),
            },
        }
    )
    write_json(runtime / "a7search1_manifest.json", manifest)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        "\n".join(
            [
                "# CRYPTO A7SEARCH1 CEM UCT Typed-AST Policy Bakeoff 20260618",
                "",
                "## Decision",
                "",
                f"`{manifest['decision']}`",
                "",
                "This stage tests search policy over a shared typed-AST formula space. AST is the expression/state representation; CEM and UCT are the search policies. The output authorizes proxy evaluation only.",
                "",
                "## Counts",
                "",
                f"- queue_rows: `{manifest['queue_rows']}`",
                f"- shard_count: `{manifest['shard_count']}`",
                f"- rows_per_shard: `{manifest['rows_per_shard']}`",
                f"- max_parallel: `{manifest['max_parallel']}`",
                f"- prior_rows: `{manifest['prior_rows']}`",
                f"- semantic_pair_count: `{manifest['semantic_pair_count']}`",
                f"- motif_count: `{manifest['motif_count']}`",
                f"- skeleton_count: `{manifest['skeleton_count']}`",
                f"- memory_enforcement_enabled: `{manifest['memory_enforcement']['enabled']}`",
                f"- memory_trace_rows: `{manifest['memory_enforcement']['trace_rows']}`",
                "",
                "## Policy Summary",
                "",
                md_table(policy_summary, 20),
                "",
                "## Pair Summary",
                "",
                md_table(pair_summary, 60),
                "",
                "## Motif Summary",
                "",
                md_table(motif_summary, 60),
                "",
                "## Guardrails",
                "",
                "- Search policies generate candidates only.",
                "- Proxy evaluation is not promotion.",
                "- Strict reward remains the only accepted-for-next-search gate.",
                "- Every candidate records search_policy, AST path, semantic pair, motif, fields, windows, and origin.",
                "- A7MEM prior is fail-closed by default; use --no-memory-enforcement only for legacy reproduction.",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
