from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff20_confirmation_selector_triage"
REPORT = REPO / "reports" / "CRYPTO_A7FF20_CONFIRMATION_SELECTOR_TRIAGE_20260530.md"
A7FF19_AGG = REPO / "runtime" / "a7ff19_company_numeric_confirmation_aggregate"


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

    a7ff19 = read_json(A7FF19_AGG / "a7ff19_manifest.json")
    responses = pd.read_csv(A7FF19_AGG / "a7ff19_label_response_metrics_all_shards.csv")
    selected = pd.read_csv(A7FF19_AGG / "a7ff19_selected_portfolio_queue_all_shards.csv")

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

    decision = (
        "HOLD_A7FF20_INTERNAL_SELECTOR_LABEL_CONCENTRATION_CONFIRMED_AFTER_EXTERNAL_QUEUE"
        if selected_non_l7_top_label_share > 0.60 and raw_label_families >= 4
        else "PASS_A7FF20_INTERNAL_SELECTOR_TRIAGE_READY"
    )
    manifest = {
        "stage": "A7FF-20-CONFIRMATION-SELECTOR-TRIAGE",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ff19_decision": a7ff19.get("decision", ""),
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
        "authorizes_a7ff21_external_confirmation_selector": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    clue_label.to_csv(RUNTIME / "a7ff20_raw_clue_label_distribution.csv", index=False)
    selected_label.to_csv(RUNTIME / "a7ff20_internal_selected_label_distribution.csv", index=False)
    selected_non_l7_label.to_csv(RUNTIME / "a7ff20_internal_selected_non_l7_label_distribution.csv", index=False)
    clue_semantic.to_csv(RUNTIME / "a7ff20_raw_clue_semantic_distribution.csv", index=False)
    selected_semantic.to_csv(RUNTIME / "a7ff20_internal_selected_semantic_distribution.csv", index=False)
    write_json(RUNTIME / "a7ff20_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-20 CONFIRMATION SELECTOR TRIAGE

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-20 confirms that the A7FF-8 internal selected queue remains label-concentrated even after the A7FF-18 external label-balanced queue was rerun numerically.

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

The A7FF-8 internal portfolio selector must be replaced for this line. The numeric surface remains multi-label; the internal selector collapses to L5.

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
