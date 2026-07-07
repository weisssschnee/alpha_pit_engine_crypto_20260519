from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DEFAULT_SEEDS = REPO / "runtime" / "a7source10_seed_triage_from_source9_20260708" / "a7source7_promoted_seed_queue.csv"
DEFAULT_RUNTIME = REPO / "runtime" / "a7source10_seed_expansion_queue_20260708"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SOURCE10_SEED_EXPANSION_QUEUE_20260708.md"

WINDOWS_FAST = [4, 8, 12, 24, 48, 72, 96]
WINDOWS_SLOW = [168, 240, 336, 504]
HORIZONS = [8, 24]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short_hash(text: str, n: int = 16) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(frame: pd.DataFrame, max_rows: int = 40) -> str:
    if frame.empty:
        return "`<empty>`"
    view = frame.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```text\n" + view.to_string(index=False) + "\n```"


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def canonical_skeleton(expr: str) -> str:
    text = re.sub(r"\s+", "", str(expr))
    text = re.sub(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", lambda m: m.group(0) if m.group(0) in {
        "Add", "Sub", "Mul", "SafeDiv", "CSRank", "TSRank", "ZScore", "Mean", "Delta", "Decay", "Abs", "Sign"
    } else "FIELD", text)
    text = re.sub(r"\b\d+\b", "W", text)
    return text


def fields_in_expr(expr: str) -> list[str]:
    ops = {"Add", "Sub", "Mul", "SafeDiv", "CSRank", "TSRank", "ZScore", "Mean", "Delta", "Decay", "Abs", "Sign"}
    tokens = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", str(expr))
    return sorted({tok for tok in tokens if tok not in ops})


def window_neighbors(expr: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    windows = sorted(set(int(x) for x in re.findall(r"\b\d+\b", str(expr))))
    replacements = sorted(set(WINDOWS_FAST + WINDOWS_SLOW))
    for old in windows:
        near = sorted(replacements, key=lambda x: (abs(x - old), x))[:5]
        for new in near:
            if new == old:
                continue
            out.append((re.sub(rf"\b{old}\b", str(new), str(expr), count=1), f"window_neighbor_{old}_to_{new}"))
    return out


def wrap_variants(expr: str) -> list[tuple[str, str]]:
    return [
        (expr, "identity_lock"),
        (f"CSRank({expr})", "rank_wrap"),
        (f"ZScore({expr})", "zscore_wrap"),
        (f"Sign({expr})", "sign_wrap"),
        (f"Abs({expr})", "abs_wrap"),
        (f"CSRank(CSRank({expr}))", "double_rank_wrap"),
    ]


def operator_neighbors(expr: str) -> list[tuple[str, str]]:
    swaps = [
        ("CSRank(", "ZScore(", "op_csrank_to_zscore"),
        ("ZScore(", "CSRank(", "op_zscore_to_csrank"),
        ("Mean(", "Decay(", "op_mean_to_decay"),
        ("Decay(", "Mean(", "op_decay_to_mean"),
        ("TSRank(", "CSRank(", "op_tsrank_to_csrank"),
    ]
    out: list[tuple[str, str]] = []
    for old, new, label in swaps:
        if old in expr:
            out.append((expr.replace(old, new, 1), label))
    return out


def single_leg_controls(expr: str) -> list[tuple[str, str]]:
    return [(f"CSRank({field})", f"single_leg_{field}") for field in fields_in_expr(expr)]


def transforms(field: str) -> list[tuple[str, str]]:
    out = [
        (field, "level"),
        (f"CSRank({field})", "csrank"),
        (f"ZScore({field})", "zscore"),
        (f"Abs({field})", "abs"),
        (f"Sign({field})", "sign"),
    ]
    for window in WINDOWS_FAST + WINDOWS_SLOW:
        out.extend(
            [
                (f"Mean({field},{window})", f"mean_{window}"),
                (f"Delta({field},{window})", f"delta_{window}"),
                (f"TSRank({field},{window})", f"tsrank_{window}"),
                (f"Decay({field},{window})", f"decay_{window}"),
                (f"ZScore(Mean({field},{window}))", f"zmean_{window}"),
                (f"CSRank(Delta({field},{window}))", f"csdelta_{window}"),
            ]
        )
    return out


def pair_controls(expr: str) -> list[tuple[str, str]]:
    fields = fields_in_expr(expr)
    out: list[tuple[str, str]] = []
    for left in fields:
        for right in fields:
            if left >= right:
                continue
            left_transforms = transforms(left)
            right_transforms = transforms(right)
            for left_expr, left_name in left_transforms:
                for right_expr, right_name in right_transforms:
                    out.extend(
                        [
                            (
                                f"SafeDiv({left_expr},Abs({right_expr}))",
                                f"field_pair_safe_div_{left}_{left_name}_{right}_{right_name}",
                            ),
                            (
                                f"Mul(CSRank({left_expr}),Sign({right_expr}))",
                                f"field_pair_signed_{left}_{left_name}_{right}_{right_name}",
                            ),
                            (
                                f"Sub(CSRank({left_expr}),CSRank({right_expr}))",
                                f"field_pair_spread_{left}_{left_name}_{right}_{right_name}",
                            ),
                            (
                                f"Mul(CSRank({left_expr}),CSRank({right_expr}))",
                                f"field_pair_rank_mul_{left}_{left_name}_{right}_{right_name}",
                            ),
                        ]
                    )
    return out


def expand_seed(seed: pd.Series, per_seed: int) -> list[dict]:
    expr = str(seed.get("expression") or seed.get("formula") or "")
    if not expr:
        return []
    base_pair = str(seed.get("semantic_pair", "unknown"))
    base_motif = str(seed.get("motif", "unknown"))
    source_id = str(seed.get("source_blueprint_id", seed.get("blueprint_id", "")))
    variants: list[tuple[str, str, str]] = []
    variants.extend((x, "formula_identity", m) for x, m in wrap_variants(expr))
    variants.extend((x, "window_neighbor", m) for x, m in window_neighbors(expr))
    variants.extend((x, "operator_neighbor", m) for x, m in operator_neighbors(expr))
    variants.extend((x, "single_leg_control", m) for x, m in single_leg_controls(expr))
    variants.extend((x, "field_pair_control", m) for x, m in pair_controls(expr))
    variants.extend((f"CSRank({x})", f"{lane}_ranked", m) for x, lane, m in list(variants))

    rows: list[dict] = []
    seen: set[str] = set()
    idx = 0
    while len(rows) < per_seed and idx < per_seed * 12:
        candidate_expr, lane, motif_suffix = variants[idx % len(variants)]
        horizon = HORIZONS[(idx // max(1, len(variants))) % len(HORIZONS)]
        idx += 1
        key = f"{candidate_expr}|{horizon}"
        if key in seen:
            continue
        seen.add(key)
        skeleton = canonical_skeleton(candidate_expr)
        rows.append(
            {
                "blueprint_id": f"a7source10_{short_hash(source_id + '|' + key)}",
                "source_blueprint_id": source_id,
                "source_rank": seed.get("seed_rank", ""),
                "expression": candidate_expr,
                "semantic_pair": base_pair,
                "motif": f"source9_{lane}_{motif_suffix}",
                "horizon_h": horizon,
                "search_policy": "source9_incremental_seed_expansion",
                "search_core": "source9_seed_local_mutation",
                "ast_path": f"source9/{base_pair}/{lane}/{motif_suffix}",
                "ast_skeleton": skeleton,
                "skeleton_key": skeleton,
                "candidate_origin": "a7source9_incremental_survivor_seed",
                "reward_feedback_source": "a7source9_strict_reward_and_incremental_validation",
                "authorizes": "proxy_only",
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=Path, default=DEFAULT_SEEDS)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--queue-rows", type=int, default=8192)
    parser.add_argument("--rows-per-shard", type=int, default=256)
    args = parser.parse_args()

    args.runtime.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    seeds = pd.read_csv(args.seeds, low_memory=False)
    per_seed = max(1, (args.queue_rows + max(1, len(seeds)) - 1) // max(1, len(seeds)))
    rows: list[dict] = []
    for _, seed in seeds.iterrows():
        rows.extend(expand_seed(seed, per_seed))
    queue = pd.DataFrame(rows).drop_duplicates(["expression", "horizon_h"]).head(args.queue_rows).reset_index(drop=True)
    queue["queue_rank"] = range(1, len(queue) + 1)
    queue_path = args.runtime / "a7source10_seed_expansion_proxy_queue.csv"
    queue.to_csv(queue_path, index=False)

    shard_rows = []
    for shard_id, start in enumerate(range(0, len(queue), args.rows_per_shard)):
        end = min(len(queue), start + args.rows_per_shard)
        shard = queue.iloc[start:end].copy()
        shard_path = args.runtime / "proxy_queue_shards" / f"a7source10_proxy_s{shard_id:03d}.csv"
        shard_path.parent.mkdir(parents=True, exist_ok=True)
        shard.to_csv(shard_path, index=False)
        shard_rows.append(
            {
                "shard_id": f"a7source10_proxy_s{shard_id:03d}",
                "path": str(shard_path),
                "path_relative": repo_relative(shard_path),
                "start_row": start,
                "end_row": end,
                "rows": len(shard),
            }
        )
    shard_plan = pd.DataFrame(shard_rows)
    shard_plan_path = args.runtime / "a7source10_proxy_shard_plan.csv"
    shard_plan.to_csv(shard_plan_path, index=False)

    group_cols = ["semantic_pair", "motif", "horizon_h"]
    summary = queue.groupby(group_cols, dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)
    summary_path = args.runtime / "a7source10_proxy_queue_summary.csv"
    summary.to_csv(summary_path, index=False)

    manifest = {
        "stage": "A7SOURCE10-SEED-EXPANSION-QUEUE",
        "generated_at": now_utc(),
        "decision": "PASS_A7SOURCE10_SEED_EXPANSION_QUEUE_BUILT" if len(queue) else "HOLD_A7SOURCE10_EMPTY_QUEUE",
        "seed_rows": int(len(seeds)),
        "queue_rows": int(len(queue)),
        "rows_per_shard": int(args.rows_per_shard),
        "shards": int(len(shard_plan)),
        "authorizes_proxy_search": bool(len(queue)),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "inputs": {"seeds": repo_relative(args.seeds)},
        "outputs": {
            "queue": repo_relative(queue_path),
            "shard_plan": repo_relative(shard_plan_path),
            "summary": repo_relative(summary_path),
            "runtime": repo_relative(args.runtime),
            "report": repo_relative(args.report),
        },
    }
    write_json(args.runtime / "a7source10_seed_expansion_manifest.json", manifest)

    lines = [
        "# CRYPTO A7SOURCE10 Seed Expansion Queue",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "Source10 expands only A7SOURCE9 incremental survivors into identity, rank-wrap, window-neighbor, operator-neighbor, single-leg-control, and field-pair-control probes.",
        "",
        "## Counts",
        "",
        f"- seed_rows: `{manifest['seed_rows']}`",
        f"- queue_rows: `{manifest['queue_rows']}`",
        f"- shards: `{manifest['shards']}`",
        f"- rows_per_shard: `{manifest['rows_per_shard']}`",
        "",
        "## Queue Summary",
        "",
        md_table(summary, 50),
        "",
        "## Boundary",
        "",
        "- Authorizes proxy search only.",
        "- Does not authorize alpha proof, shadow, paper, live, or deployment.",
    ]
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
