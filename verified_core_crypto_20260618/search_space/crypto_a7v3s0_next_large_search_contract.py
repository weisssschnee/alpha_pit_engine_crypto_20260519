from __future__ import annotations

import hashlib
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATE = "20260613"
STAGE = "A7V3S-0"
RUNTIME = REPO / "runtime" / "a7v3s0_next_large_search_contract_20260613"
REPORT = REPO / "reports" / "CRYPTO_A7V3S0_NEXT_LARGE_SEARCH_CONTRACT_20260613.md"

V3_PANEL_ROOT = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v3_patch_age_20260613")
V3_SCHEMA = REPO / "runtime" / "a7data_recent_patch_merged_panel_20260613" / "a7data_recent_patch_merged_schema.csv"
V3_GUARD_MANIFEST = REPO / "runtime" / "a7guard0_presearch_v3_20260613" / "a7guard0_manifest.json"
V3_REGIME_MANIFEST = REPO / "runtime" / "a7regime2_v3_patch_age_20260613" / "a7regime2_manifest.json"
V3_REWARD_MANIFEST = REPO / "runtime" / "a7reward1_v3_patch_age_smoke_cap4_20260613" / "a7reward1_manifest.json"

TARGET_ROWS = 65_536
ROWS_PER_SHARD = 1_024
RNG_SEED = 20260613

WINDOWS_FAST = [3, 4, 6, 8, 12, 16, 24, 36, 48, 72]
WINDOWS_SLOW = [96, 120, 168, 240, 336, 504, 720]
WINDOWS_ALL = WINDOWS_FAST + WINDOWS_SLOW

FIELD_SPECS: dict[str, dict[str, str]] = {
    "mark_index_basis_bps": {"semantic": "basis", "role": "signal_candidate"},
    "mark_trade_basis_bps": {"semantic": "basis", "role": "signal_candidate"},
    "premium_close_bps": {"semantic": "premium", "role": "coverage_gated_signal"},
    "premium_abs_state": {"semantic": "premium", "role": "computed_derived"},
    "funding_rate": {"semantic": "funding_sparse", "role": "coverage_gated_signal"},
    "funding_rate_state_last_ffill_8h": {"semantic": "funding_dense", "role": "computed_dense_funding"},
    "funding_rate_update_age_hours": {"semantic": "funding_dense", "role": "computed_dense_funding"},
    "funding_rate_abs_state_168h_z": {"semantic": "funding_dense", "role": "computed_dense_funding"},
    "funding_rate_delta_state_24h": {"semantic": "funding_dense", "role": "computed_dense_funding"},
    "funding_state_x_basis_delta": {"semantic": "funding_basis", "role": "computed_dense_funding"},
    "open_interest_last": {"semantic": "open_interest", "role": "signal_candidate"},
    "open_interest_mean": {"semantic": "open_interest", "role": "signal_candidate"},
    "open_interest_value_last": {"semantic": "open_interest", "role": "signal_candidate"},
    "open_interest_value_mean": {"semantic": "open_interest", "role": "signal_candidate"},
    "open_interest_value_change_24h": {"semantic": "open_interest", "role": "computed_derived"},
    "top_long_short_account_ratio_last": {"semantic": "positioning", "role": "signal_candidate"},
    "top_long_short_position_ratio_last": {"semantic": "positioning", "role": "signal_candidate"},
    "global_long_short_account_ratio_last": {"semantic": "positioning", "role": "signal_candidate"},
    "account_position_divergence": {"semantic": "positioning", "role": "computed_derived"},
    "top_global_account_divergence": {"semantic": "positioning", "role": "computed_derived"},
    "taker_buy_sell_volume_ratio_last": {"semantic": "taker_flow", "role": "signal_candidate"},
    "taker_buy_sell_volume_ratio_mean": {"semantic": "taker_flow", "role": "signal_candidate"},
    "kline_taker_buy_quote_share": {"semantic": "taker_flow", "role": "signal_candidate"},
    "trade_quote_volume": {"semantic": "liquidity", "role": "risk_exposure_or_signal"},
    "quote_volume_z_168h": {"semantic": "liquidity", "role": "computed_derived"},
    "listing_age_days": {"semantic": "age", "role": "control_or_interaction"},
    "log1p_listing_age_days": {"semantic": "age", "role": "control_or_interaction"},
    "sqrt_listing_age_days": {"semantic": "age", "role": "control_or_interaction"},
    "age_percentile_active_universe": {"semantic": "age", "role": "control_or_interaction"},
    "active_universe_size": {"semantic": "universe_state", "role": "control_or_regime"},
    "market_breadth_state": {"semantic": "regime", "role": "upper_alias"},
    "liquidity_cycle_state": {"semantic": "regime", "role": "upper_alias"},
    "leverage_crowding_state": {"semantic": "regime", "role": "upper_alias"},
    "basis_dislocation_state": {"semantic": "regime", "role": "upper_alias"},
    "stress_proxy_state": {"semantic": "regime", "role": "upper_alias"},
}

FORBIDDEN_FIELDS = {
    "forward_trade_return_1h",
    "trade_return_1h",
    "return_4h",
    "return_24h",
    "timestamp",
    "feature_available_time",
    "execution_time",
    "first_observed_timestamp",
    "last_funding_time",
    "symbol",
}

LANE_TARGETS = {
    "mechanism_regime_conditioned": 16_384,
    "funding_basis_recent_robust": 16_384,
    "oi_flow_cross_mechanism": 16_384,
    "raw_broad_reserved": 16_384,
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
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


def short_hash(text: str, n: int = 16) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def available_fields() -> pd.DataFrame:
    schema = set(pd.read_csv(V3_SCHEMA)["column"].astype(str)) if V3_SCHEMA.exists() else set()
    rows: list[dict[str, Any]] = []
    for field, spec in FIELD_SPECS.items():
        computed = spec["role"].startswith("computed") or spec["role"] == "upper_alias"
        available = field in schema or computed
        rows.append(
            {
                "field": field,
                "semantic": spec["semantic"],
                "role": spec["role"],
                "available_in_v3_or_computed": bool(available),
                "forbidden": field in FORBIDDEN_FIELDS,
            }
        )
    df = pd.DataFrame(rows)
    return df[df["available_in_v3_or_computed"] & ~df["forbidden"]].copy()


def transforms(field: str, semantic: str, rng: random.Random) -> list[tuple[str, str]]:
    windows = rng.sample(WINDOWS_ALL, k=min(6, len(WINDOWS_ALL)))
    out: list[tuple[str, str]] = []
    for w in windows:
        if semantic in {"age", "regime", "universe_state"}:
            out.extend(
                [
                    (f"CSRank({field})", "state_csrank"),
                    (f"Sign(TSRank({field},{w}))", "state_tsrank_sign"),
                    (f"Decay({field},{w})", "state_decay"),
                ]
            )
        elif semantic in {"funding_sparse", "funding_dense", "funding_basis"}:
            out.extend(
                [
                    (f"ZScore(Mean({field},{w}))", "funding_zmean"),
                    (f"Delta({field},{w})", "funding_delta"),
                    (f"TSRank({field},{w})", "funding_tsrank"),
                    (f"Abs(ZScore(Mean({field},{w})))", "funding_abs_zmean"),
                ]
            )
        else:
            out.extend(
                [
                    (f"ZScore(Mean({field},{w}))", "zmean"),
                    (f"CSRank(Delta({field},{w}))", "cs_delta"),
                    (f"TSRank({field},{w})", "tsrank"),
                    (f"Decay({field},{w})", "decay"),
                    (f"Abs(ZScore(Mean({field},{w})))", "abs_zmean"),
                ]
            )
    return out


def semantic_pair(a: str, b: str) -> str:
    return "|".join(sorted([a, b]))


def lane_for(left_sem: str, right_sem: str, rng: random.Random) -> str:
    pair = {left_sem, right_sem}
    if pair & {"regime", "age", "universe_state"} and pair & {"basis", "premium", "open_interest", "positioning", "taker_flow", "funding_dense", "funding_basis"}:
        return "mechanism_regime_conditioned"
    if pair & {"funding_sparse", "funding_dense", "funding_basis"} and pair & {"basis", "premium", "open_interest"}:
        return "funding_basis_recent_robust"
    if pair & {"open_interest"} and pair & {"taker_flow", "positioning", "basis", "premium"}:
        return "oi_flow_cross_mechanism"
    return "raw_broad_reserved"


def pair_templates(left: tuple[str, str, str], right: tuple[str, str, str], lane: str, rng: random.Random) -> list[tuple[str, str]]:
    lf, ls, le = left
    rf, rs, re = right
    out = [
        (f"Sub(CSRank({le}),CSRank({re}))", "spread_rank"),
        (f"Mul(CSRank({le}),Sign({re}))", "signed_rank_gate"),
        (f"SafeDiv({le},Abs({re}))", "safe_div_abs"),
        (f"Mul({le},{re})", "smooth_mul"),
    ]
    if lane == "mechanism_regime_conditioned":
        out.extend(
            [
                (f"Mul({le},Sign({re}))", "state_conditioned_signed"),
                (f"Mul(CSRank({le}),CSRank({re}))", "state_conditioned_rank_mul"),
            ]
        )
    if lane == "funding_basis_recent_robust":
        out.extend(
            [
                (f"Sub(ZScore(Mean({lf},24)),ZScore(Mean({rf},24)))", "funding_basis_spread_24h"),
                (f"Mul(Delta({lf},24),Sign(Delta({rf},24)))", "funding_basis_delta_sign"),
            ]
        )
    if lane == "oi_flow_cross_mechanism":
        out.extend(
            [
                (f"Mul(CSRank(Delta({lf},24)),CSRank(Delta({rf},24)))", "oi_flow_delta_rank"),
                (f"SafeDiv(Sub(CSRank({le}),CSRank({re})),Abs({re}))", "oi_flow_scaled_spread"),
            ]
        )
    rng.shuffle(out)
    return out


def skeleton_key(expression: str, pair: str, motif: str) -> str:
    simplified = expression
    for field in sorted(FIELD_SPECS, key=len, reverse=True):
        simplified = simplified.replace(field, "F")
    for w in WINDOWS_ALL:
        simplified = simplified.replace(str(w), "W")
    return f"{pair}|{motif}|{short_hash(simplified, 12)}"


def build_queue() -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = random.Random(RNG_SEED)
    fields = available_fields()
    transform_rows: list[tuple[str, str, str, str]] = []
    for row in fields.to_dict("records"):
        for expr, motif in transforms(str(row["field"]), str(row["semantic"]), rng):
            transform_rows.append((str(row["field"]), str(row["semantic"]), expr, motif))

    lane_counts = {lane: 0 for lane in LANE_TARGETS}
    skeleton_counts: dict[str, int] = {}
    semantic_counts: dict[str, int] = {}
    field_counts: dict[str, int] = {}
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    attempts = 0
    max_attempts = TARGET_ROWS * 200
    lane_skeleton_cap = 96
    semantic_cap = 8192
    field_cap = 18_000

    while len(rows) < TARGET_ROWS and attempts < max_attempts:
        attempts += 1
        left = transform_rows[rng.randrange(len(transform_rows))]
        right = transform_rows[rng.randrange(len(transform_rows))]
        lf, ls, le, lm = left
        rf, rs, re, rm = right
        if lf == rf and lm == rm:
            continue
        lane = lane_for(ls, rs, rng)
        if lane_counts[lane] >= LANE_TARGETS[lane]:
            continue
        pair = semantic_pair(ls, rs)
        expr, motif = pair_templates((lf, ls, le), (rf, rs, re), lane, rng)[0]
        if expr in seen:
            continue
        skel = skeleton_key(expr, pair, motif)
        lane_skel = f"{lane}|{skel}"
        if skeleton_counts.get(lane_skel, 0) >= lane_skeleton_cap:
            continue
        if semantic_counts.get(f"{lane}|{pair}", 0) >= semantic_cap:
            continue
        if field_counts.get(lf, 0) >= field_cap or field_counts.get(rf, 0) >= field_cap:
            continue
        score = 0.0
        score += 18 if lane == "raw_broad_reserved" else 0
        score += 24 if lane == "funding_basis_recent_robust" else 0
        score += 22 if lane == "oi_flow_cross_mechanism" else 0
        score += 20 if lane == "mechanism_regime_conditioned" else 0
        score += 8 if "funding" in pair else 0
        score += 8 if "taker_flow" in pair else 0
        score += 6 if "age" in pair or "regime" in pair else 0
        score += {"safe_div_abs": 10, "spread_rank": 8, "signed_rank_gate": 7, "smooth_mul": 5}.get(motif, 0)
        rows.append(
            {
                "expression": expr,
                "a7v3s0_lane": lane,
                "semantic_pair": pair,
                "motif": motif,
                "left_field": lf,
                "right_field": rf,
                "left_semantic": ls,
                "right_semantic": rs,
                "left_transform": lm,
                "right_transform": rm,
                "skeleton_key": skel,
                "priority_score": score,
            }
        )
        seen.add(expr)
        lane_counts[lane] += 1
        skeleton_counts[lane_skel] = skeleton_counts.get(lane_skel, 0) + 1
        semantic_counts[f"{lane}|{pair}"] = semantic_counts.get(f"{lane}|{pair}", 0) + 1
        field_counts[lf] = field_counts.get(lf, 0) + 1
        field_counts[rf] = field_counts.get(rf, 0) + 1

    queue = pd.DataFrame(rows)
    if len(queue) < TARGET_ROWS:
        raise RuntimeError(f"queue too small: {len(queue)} after {attempts} attempts")
    queue["blueprint_id"] = ["a7v3s0_" + short_hash(f"{idx}|{expr}", 16) for idx, expr in enumerate(queue["expression"].astype(str))]
    queue["a7ls_lane"] = queue["a7v3s0_lane"]
    queue["lane_name"] = queue["a7v3s0_lane"]
    queue["search_role"] = "v3_native_large_space_numeric_probe"
    queue["level"] = "A7V3S0"
    queue["candidate_role"] = "numeric_probe_only"
    queue["generation_priority"] = queue["priority_score"]
    queue["primary_field"] = queue["left_field"]
    queue["secondary_field"] = queue["right_field"]
    queue["primary_semantic"] = queue["left_semantic"]
    queue["secondary_semantic"] = queue["right_semantic"]
    queue["primary_transform"] = queue["left_transform"]
    queue["secondary_transform"] = queue["right_transform"]
    queue["production_key"] = queue["skeleton_key"]
    queue["source_stage"] = STAGE
    queue["source_seed_id"] = "v3_schema_and_mechanism_state"
    queue["checkpoint_group"] = [f"a7v3s0_s{idx // ROWS_PER_SHARD:03d}" for idx in range(len(queue))]
    queue["authorizes_alpha_proof"] = False
    ordered = [
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
        "a7v3s0_lane",
        "left_field",
        "right_field",
        "left_transform",
        "right_transform",
        "authorizes_alpha_proof",
    ]
    return queue[ordered], fields


def write_company_launcher(queue_path: Path, shard_plan: pd.DataFrame) -> Path:
    path = RUNTIME / "run_a7v3s0_company_materialization.ps1"
    remote_repo = r"D:\HermesWorker\GDrive\Project_V7_Rotation\alpha_pit_engine_crypto_20260519_remote"
    remote_runtime = r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData\research_runtime\a7v3s0_v3_native_large_search_20260613"
    remote_queue = rf"{remote_runtime}\a7v3s0_large_search_queue.csv"
    lines = [
        '$ErrorActionPreference = "Stop"',
        '$Python = "D:\\HermesWorker\\workspace\\.venv\\Scripts\\python.exe"',
        f'$Repo = "{remote_repo}"',
        f'$Runtime = "{remote_runtime}"',
        f'$Queue = "{remote_queue}"',
        '$env:A7AL_BASE_PANEL_ROOT = "D:\\HermesWorker\\GDrive\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_replay_1h_v3_patch_age_20260613"',
        "Set-Location $Repo",
        "New-Item -ItemType Directory -Force -Path $Runtime | Out-Null",
        "$Concurrency = 4",
        "$SymbolCap = 192",
        "$TimestampCap = 4096",
        "$shards = @(",
    ]
    for i, row in enumerate(shard_plan.to_dict("records")):
        comma = "," if i < len(shard_plan) - 1 else ""
        lines.append(f'  @{{id="{row["shard_id"]}"; start={row["start_row"]}; end={row["end_row_exclusive"]}}}{comma}')
    lines.extend(
        [
            ")",
            "$active = @()",
            "foreach ($s in $shards) {",
            "  $manifest = Join-Path $Runtime (\"shards\\\" + $s.id + \"\\a7ls17_manifest.json\")",
            "  if (Test-Path $manifest) { Write-Host \"[A7V3S0] skip existing $($s.id)\"; continue }",
            "  while (($active | Where-Object { -not $_.HasExited }).Count -ge $Concurrency) { Start-Sleep -Seconds 20; $active = @($active | Where-Object { -not $_.HasExited }) }",
            "  $shardRoot = Join-Path $Runtime (\"shards\\\" + $s.id)",
            "  New-Item -ItemType Directory -Force -Path $shardRoot | Out-Null",
            "  $env:A7LS17_QUEUE_PATH = $Queue",
            "  $env:A7LS17_RUNTIME = $Runtime",
            "  $env:A7LS17_SHARD_ID = $s.id",
            "  $env:A7LS17_START_ROW = [string]$s.start",
            "  $env:A7LS17_END_ROW = [string]$s.end",
            "  $env:A7LS17_SYMBOL_CAP = [string]$SymbolCap",
            "  $env:A7LS17_TIMESTAMP_CAP = [string]$TimestampCap",
            "  $env:A7LS17_PROGRESS_EVERY = \"256\"",
            "  $outLog = Join-Path $shardRoot \"runner.out.log\"",
            "  $errLog = Join-Path $shardRoot \"runner.err.log\"",
            "  Write-Host \"[A7V3S0] start $($s.id) rows=$($s.start):$($s.end)\"",
            "  $p = Start-Process -FilePath $Python -ArgumentList @('scripts\\crypto_a7ls17_company_materialization_runner.py') -RedirectStandardOutput $outLog -RedirectStandardError $errLog -PassThru -WindowStyle Hidden",
            "  $active += $p",
            "}",
            "while (($active | Where-Object { -not $_.HasExited }).Count -gt 0) { Start-Sleep -Seconds 30; $active = @($active | Where-Object { -not $_.HasExited }) }",
            "$summary = @()",
            "foreach ($s in $shards) {",
            "  $manifest = Join-Path $Runtime (\"shards\\\" + $s.id + \"\\a7ls17_manifest.json\")",
            "  if (Test-Path $manifest) { $m = Get-Content $manifest -Raw | ConvertFrom-Json; $summary += [pscustomobject]@{shard_id=$s.id; decision=$m.decision; queue_rows=$m.queue_rows; eval_success_count=$m.eval_success_count; activity_ok_count=$m.activity_ok_count} }",
            "  else { $summary += [pscustomobject]@{shard_id=$s.id; decision='MISSING_MANIFEST'; queue_rows=0; eval_success_count=0; activity_ok_count=0} }",
            "}",
            "$summary | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $Runtime 'a7v3s0_materialization_summary.json')",
            "Write-Host \"[A7V3S0] materialization wave complete\"",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    queue, fields = build_queue()
    queue_path = RUNTIME / "a7v3s0_large_search_queue.csv"
    queue.to_csv(queue_path, index=False)
    fields.to_csv(RUNTIME / "a7v3s0_field_pool.csv", index=False)

    shard_rows = []
    for i, start in enumerate(range(0, len(queue), ROWS_PER_SHARD)):
        end = min(start + ROWS_PER_SHARD, len(queue))
        shard_rows.append({"shard_id": f"a7v3s0_s{i:03d}", "start_row": start, "end_row_exclusive": end, "rows": end - start})
    shard_plan = pd.DataFrame(shard_rows)
    shard_plan.to_csv(RUNTIME / "a7v3s0_shard_plan.csv", index=False)
    launcher = write_company_launcher(queue_path, shard_plan)

    lane_summary = queue.groupby("a7v3s0_lane", dropna=False).size().reset_index(name="rows")
    semantic_summary = queue.groupby(["a7v3s0_lane", "semantic_pair"], dropna=False).size().reset_index(name="rows").sort_values("rows", ascending=False)
    motif_summary = queue.groupby(["a7v3s0_lane", "motif"], dropna=False).size().reset_index(name="rows").sort_values("rows", ascending=False)
    field_usage = pd.concat(
        [
            queue[["primary_field"]].rename(columns={"primary_field": "field"}),
            queue[["secondary_field"]].rename(columns={"secondary_field": "field"}),
        ],
        ignore_index=True,
    ).groupby("field").size().reset_index(name="usage_rows").sort_values("usage_rows", ascending=False)
    lane_summary.to_csv(RUNTIME / "a7v3s0_lane_summary.csv", index=False)
    semantic_summary.to_csv(RUNTIME / "a7v3s0_semantic_pair_summary.csv", index=False)
    motif_summary.to_csv(RUNTIME / "a7v3s0_motif_summary.csv", index=False)
    field_usage.to_csv(RUNTIME / "a7v3s0_field_usage_summary.csv", index=False)

    guard = read_json(V3_GUARD_MANIFEST)
    regime = read_json(V3_REGIME_MANIFEST)
    reward = read_json(V3_REWARD_MANIFEST)
    decision = "PASS_A7V3S0_NEXT_LARGE_SEARCH_CONTRACT_READY_NOT_LAUNCHED"
    blockers = []
    if guard.get("decision") != "PASS_A7GUARD0_PRESEARCH_GUARD_READY":
        blockers.append("v3_guard_not_pass")
    if regime.get("decision") != "PASS_A7REGIME2_MECHANISM_REGIME_CANDIDATES_FOUND":
        blockers.append("v3_regime_not_pass")
    if reward.get("eval_error_rows", 1) != 0 or not reward.get("synthetic_smoke_pass", False):
        blockers.append("v3_reward_smoke_not_operational")
    if blockers:
        decision = "HOLD_A7V3S0_NEXT_LARGE_SEARCH_CONTRACT_BLOCKED"

    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "queue_rows": int(len(queue)),
        "rows_per_shard": ROWS_PER_SHARD,
        "shard_count": int(len(shard_plan)),
        "lane_targets": LANE_TARGETS,
        "v3_panel_root": str(V3_PANEL_ROOT),
        "guard_decision": guard.get("decision"),
        "regime_decision": regime.get("decision"),
        "reward_smoke_decision": reward.get("decision"),
        "reward_smoke_accepted_rows": reward.get("accepted_for_next_search_rows"),
        "old_queue_policy": "old accepted queue rejected by v3 reward smoke; use only as diagnostic negative control, not seed",
        "authorizes": ["company_materialization_numeric_probe_after_queue_upload", "reward_gate_followup"],
        "does_not_authorize": ["alpha_proof", "shadow_paper_live", "ungated_search_best_claim"],
        "outputs": {
            "queue": str(queue_path.relative_to(REPO)),
            "field_pool": str((RUNTIME / "a7v3s0_field_pool.csv").relative_to(REPO)),
            "shard_plan": str((RUNTIME / "a7v3s0_shard_plan.csv").relative_to(REPO)),
            "company_launcher": str(launcher.relative_to(REPO)),
            "report": str(REPORT.relative_to(REPO)),
        },
    }
    write_json(RUNTIME / "a7v3s0_manifest.json", manifest)
    REPORT.write_text(
        "\n".join(
            [
                "# CRYPTO A7V3S0 Next Large Search Contract 20260613",
                "",
                "## Decision",
                "",
                f"`{decision}`",
                "",
                "A7V3S0 defines the next large search as a v3-panel-native numeric probe. It does not reuse the old accepted queue as a seed because the v3 reward smoke rejected it. The queue is broad enough for system validation, but it remains gated: materialization first, then reward gate, then only accepted outputs may feed the next stage.",
                "",
                "## Counts",
                "",
                f"- queue_rows: `{len(queue)}`",
                f"- shard_count: `{len(shard_plan)}`",
                f"- rows_per_shard: `{ROWS_PER_SHARD}`",
                f"- v3_panel_root: `{V3_PANEL_ROOT}`",
                f"- guard_decision: `{manifest['guard_decision']}`",
                f"- regime_decision: `{manifest['regime_decision']}`",
                f"- reward_smoke_decision: `{manifest['reward_smoke_decision']}`",
                f"- reward_smoke_accepted_rows: `{manifest['reward_smoke_accepted_rows']}`",
                "",
                "## Lane Summary",
                "",
                md_table(lane_summary),
                "",
                "## Semantic Pair Summary",
                "",
                md_table(semantic_summary, 80),
                "",
                "## Motif Summary",
                "",
                md_table(motif_summary, 80),
                "",
                "## Field Usage Summary",
                "",
                md_table(field_usage, 80),
                "",
                "## Operating Rules",
                "",
                "- Use v3 panel only: `binance_universe498_replay_1h_v3_patch_age_20260613`.",
                "- Do not consume old accepted queue as seed; it is now a diagnostic negative control.",
                "- Do not claim best/alpha from materialization metrics; reward gate must write accepted/rejected queue.",
                "- Reject any candidate dominated by shuffle/wrong-lag/control or non-overlap floor failures.",
                "- Keep one lane as raw broad search, but keep semantic/skeleton/field caps active.",
                "- Final proof remains blocked until checksum/source trace audit.",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
