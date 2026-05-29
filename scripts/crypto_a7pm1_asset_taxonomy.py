from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7pm1_asset_taxonomy"
REPORT = REPO / "reports" / "CRYPTO_A7PM1_ASSET_TAXONOMY_AND_MODULARIZATION_PLAN_20260529.md"
A7PM0 = REPO / "runtime" / "a7pm0_source_of_truth_registry" / "a7pm0_manifest.json"


TARGET_LAYOUT = {
    "alphafactory_crypto/data_contracts": "PIT/source/timing/source-of-truth contracts",
    "alphafactory_crypto/features": "typed FeatureFactory and derived feature contracts",
    "alphafactory_crypto/labels": "label construction and label adequacy",
    "alphafactory_crypto/regimes": "latent and upper-regime state builders",
    "alphafactory_crypto/generators": "formula and expression generators",
    "alphafactory_crypto/selectors": "role-aware and replay-aware selectors",
    "alphafactory_crypto/replay": "materialization, evaluator, replay, parity",
    "alphafactory_crypto/controls": "negative controls, wrong-lag, shuffle, placebo",
    "alphafactory_crypto/clustering": "signal-vector and formula-family clustering",
    "alphafactory_crypto/promotion": "candidate lifecycle and promotion gates",
    "alphafactory_crypto/experiments": "experiment board and stage registry integration",
    "alphafactory_crypto/governance": "source-of-truth registry and authorization matrix",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def classify(path: Path) -> tuple[str, str, int]:
    text = rel(path).lower()
    name = path.name.lower()
    if "cn_reference" in text:
        return "legacy_or_reference_only", "alphafactory_crypto/cn_reference", 90
    if "deprecated" in text or "superseded" in text:
        return "deprecated_or_superseded", "archive_or_runtime_only", 80
    if "a7pm" in text or "authorization" in name or "source_of_truth" in text:
        return "experiment_registry", "alphafactory_crypto/governance", 10
    if "contract" in name or "source_trace" in name or "field_contract" in name or "data" in name:
        return "data_contracts", "alphafactory_crypto/data_contracts", 20
    if "feature" in name or "algebra" in name or "derived" in name:
        return "feature_factory", "alphafactory_crypto/features", 20
    if "label" in name:
        return "label_factory", "alphafactory_crypto/labels", 20
    if "latent" in name or "regime" in name or "meme" in name or "listing" in name:
        return "regime_factory", "alphafactory_crypto/regimes", 30
    if "formula" in name or "generator" in name or "cem" in name or "ast" in name:
        return "formula_generator", "alphafactory_crypto/generators", 30
    if "selector" in name or "rerank" in name:
        return "selector", "alphafactory_crypto/selectors", 30
    if "replay" in name or "materialization" in name or "evaluator" in name or "parity" in name:
        return "replay_engine", "alphafactory_crypto/replay", 20
    if "control" in name or "shuffle" in name or "wrong" in name or "placebo" in name:
        return "controls", "alphafactory_crypto/controls", 30
    if "cluster" in name or "dedup" in name or "memory" in name:
        return "clustering", "alphafactory_crypto/clustering", 40
    if "promotion" in name or "candidate" in name or "lifecycle" in name:
        return "promotion", "alphafactory_crypto/promotion", 40
    if "experiment" in name or "board" in name:
        return "experiment_registry", "alphafactory_crypto/experiments", 30
    return "stage_entry_or_misc", "manual_review", 60


def file_inventory(root: Path, pattern: str, asset_kind: str) -> pd.DataFrame:
    rows = []
    if not root.exists():
        return pd.DataFrame()
    for path in sorted(root.rglob(pattern)):
        if not path.is_file():
            continue
        category, target, priority = classify(path)
        rows.append(
            {
                "path": rel(path),
                "asset_kind": asset_kind,
                "category": category,
                "target_module": target,
                "refactor_priority": priority,
                "bytes": path.stat().st_size,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    pm0 = read_json(A7PM0)
    if not pm0.get("authorizes_a7pm1"):
        raise SystemExit("A7PM-0 does not authorize A7PM-1")

    code = pd.concat(
        [
            file_inventory(REPO / "scripts", "*.py", "stage_entry_script"),
            file_inventory(REPO / "alphafactory_crypto", "*.py", "package_code"),
        ],
        ignore_index=True,
    )
    configs = file_inventory(REPO / "config", "*", "config")
    reports = file_inventory(REPO / "reports", "*.md", "report")
    runtime = file_inventory(REPO / "runtime", "*", "runtime_artifact")
    data_assets = pd.DataFrame(
        [
            {
                "path": "external_gold_and_silver_panels",
                "asset_kind": "data_asset",
                "category": "data_contracts",
                "target_module": "alphafactory_crypto/data_contracts",
                "refactor_priority": 20,
                "notes": "Large data stays outside git; registry should reference contracts/manifests only.",
            }
        ]
    )
    refactor_priority = (
        code.groupby(["category", "target_module"], dropna=False)
        .agg(asset_count=("path", "count"), min_priority=("refactor_priority", "min"))
        .reset_index()
        .sort_values(["min_priority", "asset_count"], ascending=[True, False])
    )
    manifest = {
        "stage": "A7PM-1",
        "generated_at": now_utc(),
        "decision": "PASS_A7PM1_ASSET_TAXONOMY_AND_MODULARIZATION_PLAN_BUILT",
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "code_asset_count": int(len(code)),
        "runtime_artifact_count": int(len(runtime)),
        "report_count": int(len(reports)),
        "config_count": int(len(configs)),
        "authorizes_a7pm2": True,
        "authorizes_a7pm3": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    code.to_csv(RUNTIME / "a7pm1_code_asset_inventory.csv", index=False)
    data_assets.to_csv(RUNTIME / "a7pm1_data_asset_inventory.csv", index=False)
    runtime.to_csv(RUNTIME / "a7pm1_runtime_artifact_inventory.csv", index=False)
    reports.to_csv(RUNTIME / "a7pm1_report_inventory.csv", index=False)
    configs.to_csv(RUNTIME / "a7pm1_config_inventory.csv", index=False)
    write_json(RUNTIME / "a7pm1_module_target_layout.json", TARGET_LAYOUT)
    refactor_priority.to_csv(RUNTIME / "a7pm1_refactor_priority.csv", index=False)
    write_json(RUNTIME / "a7pm1_manifest.json", manifest)
    lines = [
        "# CRYPTO A7PM-1 ASSET TAXONOMY AND MODULARIZATION PLAN",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "A7PM-1 classifies current code, reports, runtime artifacts, configs, and external data references. It does not move files or execute search.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Target Layout",
        "",
        "```json",
        json.dumps(TARGET_LAYOUT, indent=2, sort_keys=True),
        "```",
        "",
        "## Refactor Priority",
        "",
        md_table(refactor_priority, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "cn_reference is reference-only.",
        "scripts/crypto_a7*.py are stage-entry scripts, not long-term services.",
        "runtime artifacts must not be bypassed by future selectors or replay scripts.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
