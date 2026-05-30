from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff17_followup_selector_triage"
REPORT = REPO / "reports" / "CRYPTO_A7FF17_FOLLOWUP_SELECTOR_TRIAGE_20260530.md"
A7FF16_AGG = REPO / "runtime" / "a7ff16_company_numeric_followup_aggregate"


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
    safe = df.head(max_rows).copy()
    for col in safe.select_dtypes(include=["object"]).columns:
        safe[col] = safe[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return safe.to_markdown(index=False)
    except ImportError:
        return "```text\n" + safe.to_string(index=False) + "\n```"


def count_share(df: pd.DataFrame, col: str, name: str) -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return pd.DataFrame(columns=[name, "count", "share"])
    out = df.groupby(col, dropna=False).size().reset_index(name="count").rename(columns={col: name})
    total = float(out["count"].sum()) if not out.empty else 0.0
    out["share"] = out["count"] / total if total else 0.0
    return out.sort_values("count", ascending=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ff16 = read_json(A7FF16_AGG / "a7ff16_manifest.json")
    responses = pd.read_csv(A7FF16_AGG / "a7ff16_label_response_metrics_all_shards.csv")
    selected = pd.read_csv(A7FF16_AGG / "a7ff16_selected_portfolio_queue_all_shards.csv")

    clues = responses[responses["decision"].astype(str).str.contains("NUMERIC_CLUE", na=False)].copy()
    non_l7 = clues[~clues["label_family"].eq("L7_ranked_future_return")].copy()
    selected_non_l7 = selected[~selected["label_family"].eq("L7_ranked_future_return")].copy() if not selected.empty else pd.DataFrame()

    clue_label = count_share(non_l7, "label_family", "label_family")
    selected_label = count_share(selected, "label_family", "label_family")
    selected_non_l7_label = count_share(selected_non_l7, "label_family", "label_family")
    clue_semantic = count_share(non_l7, "semantic_pair", "semantic_pair")
    selected_semantic = count_share(selected, "semantic_pair", "semantic_pair")

    clue_top_label_share = float(clue_label["share"].max()) if not clue_label.empty else 0.0
    selected_top_label_share = float(selected_label["share"].max()) if not selected_label.empty else 0.0
    selected_non_l7_top_label_share = float(selected_non_l7_label["share"].max()) if not selected_non_l7_label.empty else 0.0
    raw_label_families = int(non_l7["label_family"].nunique()) if not non_l7.empty else 0
    selected_label_families = int(selected_non_l7["label_family"].nunique()) if not selected_non_l7.empty else 0

    concentration_persists = selected_non_l7_top_label_share > 0.60
    decision = (
        "HOLD_A7FF17_INTERNAL_SELECTOR_LABEL_CONCENTRATION_PERSISTS"
        if concentration_persists and raw_label_families >= 4
        else "PASS_A7FF17_SELECTOR_TRIAGE_READY"
    )
    manifest = {
        "stage": "A7FF-17-FOLLOWUP-SELECTOR-TRIAGE",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ff16_decision": a7ff16.get("decision", ""),
        "raw_non_l7_clue_rows": int(len(non_l7)),
        "raw_non_l7_label_families": raw_label_families,
        "raw_top_label_share": clue_top_label_share,
        "selected_rows": int(len(selected)),
        "selected_non_l7_rows": int(len(selected_non_l7)),
        "selected_non_l7_label_families": selected_label_families,
        "selected_top_label_share": selected_top_label_share,
        "selected_non_l7_top_label_share": selected_non_l7_top_label_share,
        "uses_may": False,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_a7ff18_external_label_balanced_selector": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    clue_label.to_csv(RUNTIME / "a7ff17_raw_clue_label_distribution.csv", index=False)
    selected_label.to_csv(RUNTIME / "a7ff17_internal_selected_label_distribution.csv", index=False)
    selected_non_l7_label.to_csv(RUNTIME / "a7ff17_internal_selected_non_l7_label_distribution.csv", index=False)
    clue_semantic.to_csv(RUNTIME / "a7ff17_raw_clue_semantic_distribution.csv", index=False)
    selected_semantic.to_csv(RUNTIME / "a7ff17_internal_selected_semantic_distribution.csv", index=False)
    write_json(RUNTIME / "a7ff17_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-17 FOLLOWUP SELECTOR TRIAGE

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-17 compares the A7FF-16 numeric clue surface with the A7FF-8 internal selected portfolio queue. The clue surface remains label-diverse, but the internal selector is still label-concentrated.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Raw Non-L7 Clue Label Distribution

{md_table(clue_label)}

## Internal Selected Label Distribution

{md_table(selected_label)}

## Internal Selected Non-L7 Label Distribution

{md_table(selected_non_l7_label)}

## Raw Non-L7 Semantic Distribution

{md_table(clue_semantic)}

## Internal Selected Semantic Distribution

{md_table(selected_semantic)}

## Interpretation

The numeric surface is not L5-only. The internal A7FF-8 portfolio selector remains L5-heavy and must not be used as the final selector target for the next expansion.

## Boundary

- Uses May: `false`
- Executes generation: `false`
- Executes replay: `false`
- Executes search: `false`
- Authorizes alpha proof / shadow / paper / live: `false`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
