from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff55r4_repaired_atlas_coverage_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FF55R4_REPAIRED_ATLAS_COVERAGE_AUDIT_20260531.md"
A7FF55R3 = REPO / "runtime" / "a7ff55r3_repaired_atlas_dry_generation" / "a7ff55r3_manifest.json"
QUEUE = REPO / "runtime" / "a7ff55r3_repaired_atlas_dry_generation" / "a7ff55r3_repaired_materialization_queue.csv"
FORMULAS = REPO / "runtime" / "a7ff55r3_repaired_atlas_dry_generation" / "a7ff55r3_repaired_formula_index.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def summary(df: pd.DataFrame, cols: list[str], name: str) -> pd.DataFrame:
    out = df.groupby(cols, dropna=False).size().reset_index(name=f"{name}_count").sort_values(f"{name}_count", ascending=False)
    out[f"{name}_share"] = out[f"{name}_count"] / max(1, len(df))
    return out


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    m55r3 = read_json(A7FF55R3)
    if m55r3.get("decision") != "PASS_A7FF55R3_REPAIRED_ATLAS_DRY_GENERATION_READY_FOR_COVERAGE_AUDIT":
        raise SystemExit(f"A7FF-55R3 is not ready: {m55r3.get('decision')}")
    queue = pd.read_csv(QUEUE)
    formulas = pd.read_csv(FORMULAS)
    by_pair = summary(queue, ["semantic_pair"], "queue")
    by_pair_motif = summary(queue, ["semantic_pair", "motif"], "queue")
    by_motif = summary(queue, ["motif"], "queue")
    by_primary = summary(queue, ["primary_semantic"], "queue")
    by_field = summary(queue, ["primary_field", "secondary_field"], "queue")
    by_shard = summary(queue, ["company_shard"], "queue")

    by_pair.to_csv(RUNTIME / "a7ff55r4_queue_by_semantic_pair.csv", index=False)
    by_pair_motif.to_csv(RUNTIME / "a7ff55r4_queue_by_pair_motif.csv", index=False)
    by_motif.to_csv(RUNTIME / "a7ff55r4_queue_by_motif.csv", index=False)
    by_primary.to_csv(RUNTIME / "a7ff55r4_queue_by_primary_semantic.csv", index=False)
    by_field.to_csv(RUNTIME / "a7ff55r4_queue_by_field_pair.csv", index=False)
    by_shard.to_csv(RUNTIME / "a7ff55r4_queue_by_shard.csv", index=False)

    required_pairs = {
        "open_interest_like|positioning_like",
        "taker_flow_like|open_interest_like",
        "liquidity_like|volatility_like",
    }
    present_pairs = set(queue["semantic_pair"].dropna().astype(str))
    top_pair_share = float(by_pair["queue_share"].max()) if not by_pair.empty else 0.0
    top_motif_share = float(by_motif["queue_share"].max()) if not by_motif.empty else 0.0
    top_pair_motif_share = float(by_pair_motif["queue_share"].max()) if not by_pair_motif.empty else 0.0
    blockers = []
    if len(queue) < 2000:
        blockers.append("queue_count_below_2000")
    if len(present_pairs) < 5:
        blockers.append("semantic_pair_count_below_5")
    if len(set(queue["motif"].dropna().astype(str))) < 6:
        blockers.append("motif_count_below_6")
    if top_pair_share > 0.30:
        blockers.append("top_semantic_pair_share_above_0p30")
    if top_motif_share > 0.30:
        blockers.append("top_motif_share_above_0p30")
    if top_pair_motif_share > 0.18:
        blockers.append("top_pair_motif_share_above_0p18")
    for pair in sorted(required_pairs - present_pairs):
        blockers.append(f"{pair}_missing")

    decision = "PASS_A7FF55R4_REPAIRED_ATLAS_COVERAGE_READY_FOR_NUMERIC_CONTRACT" if not blockers else "HOLD_A7FF55R4_REPAIRED_ATLAS_COVERAGE_FAIL"
    manifest = {
        "stage": "A7FF-55R4",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "formula_count": int(len(formulas)),
        "queue_count": int(len(queue)),
        "semantic_pair_count": int(queue["semantic_pair"].nunique()),
        "motif_count": int(queue["motif"].nunique()),
        "top_semantic_pair_share": top_pair_share,
        "top_motif_share": top_motif_share,
        "top_pair_motif_share": top_pair_motif_share,
        "required_pairs_present": sorted(required_pairs & present_pairs),
        "next_allowed": "A7FF-55R5 repaired atlas numeric contract" if not blockers else "A7FF-55R3 dry generation repair",
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_numeric_contract": not bool(blockers),
        "authorizes_numeric_execution": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff55r4_manifest.json", manifest)
    report = f"""# CRYPTO A7FF-55R4 REPAIRED ATLAS COVERAGE AUDIT

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-55R4 audits the repaired 2400-row atlas queue coverage. It does not run numeric evaluation, replay, or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Queue By Semantic Pair

{md_table(by_pair, 80)}

## Queue By Motif

{md_table(by_motif, 80)}

## Queue By Pair / Motif

{md_table(by_pair_motif, 80)}

## Queue By Shard

{md_table(by_shard, 40)}

## Boundary

```text
coverage audit executed: true
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
