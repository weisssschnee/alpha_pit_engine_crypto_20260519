from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7night_taskflow_20260531"
REPORT = REPO / "reports" / "CRYPTO_A7NIGHT_TASKFLOW_20260531.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 100) -> str:
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


def git_value(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def only_expected_dirty(status: str) -> tuple[bool, str]:
    if not status:
        return True, "clean"
    allowed = (
        "reports/CRYPTO_A7NIGHT_TASKFLOW_20260531.md",
        "runtime/a7night_taskflow_20260531/",
        "scripts/crypto_a7night_taskflow_20260531.py",
    )
    unexpected: list[str] = []
    for line in status.splitlines():
        path = line[3:] if len(line) > 3 else line
        if not any(path.startswith(prefix) for prefix in allowed):
            unexpected.append(line)
    return not unexpected, "\n".join(unexpected) if unexpected else "only A7NIGHT self artifacts are dirty"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    r11 = read_json(REPO / "runtime" / "a7ffr11_feature_label_objective_reset" / "a7ffr11_manifest.json")
    r3 = read_json(REPO / "runtime" / "a7ff24r3_dense_materializer_preflight" / "a7ff24r3_manifest.json")
    pm3_allowed = read_json(REPO / "runtime" / "a7pm3_experiment_board" / "a7pm3_allowed_next_tasks.json")
    head = git_value("rev-parse", "HEAD")
    origin = git_value("rev-parse", "origin/main")
    status = git_value("status", "--short")
    dirty_ok, dirty_detail = only_expected_dirty(status)

    contracts = {
        "A7FF-51": {
            "name": "compact non-L5-first derived generation contract",
            "status": "contract_ready",
            "source": "A7FF-R11",
            "execution_authorized": False,
            "search_authorized": False,
            "artifact_budget": {"max_new_reports": 1, "max_new_runtime_tables": 3, "required_manifest": True},
            "primary_labels": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return"],
            "hard_gates": {
                "reference_family_cannot_count_as_primary": True,
                "control_ratio_max": 0.80,
                "min_non_reference_rows_before_replay": 6,
                "min_non_reference_families_before_replay": 2,
            },
        },
        "A7FF-24R4": {
            "name": "repaired-queue numeric wave contract",
            "status": "contract_ready",
            "source": "A7FF-24R3",
            "execution_authorized": False,
            "search_authorized": False,
            "artifact_budget": {"max_new_reports": 1, "max_new_runtime_tables": 3, "required_manifest": True},
            "preconditions": {
                "dense_materializer_preflight_pass": r3.get("decision")
                == "PASS_A7FF24R3_DENSE_MATERIALIZER_PREFLIGHT_READY_FOR_REPAIRED_QUEUE_NUMERIC_WAVE_NO_SEARCH_AUTH",
                "eval_failure_count": r3.get("eval_failure_count"),
                "dense_tail_activity_ok_count": r3.get("dense_tail_activity_ok_count"),
                "raw_funding_rate_tail_rows": r3.get("raw_funding_rate_tail_rows"),
            },
            "hard_gates": {
                "before_full_wave": [
                    "queue coverage by shard and semantic pair",
                    "no missing numeric fields",
                    "no eval failures in preflight sample",
                    "raw funding rate must remain absent from dense tail",
                ]
            },
        },
    }
    write_json(RUNTIME / "a7night_contracts.json", contracts)

    checks = [
        {
            "check": "git_head_equals_origin_main_before_night_commit",
            "value": head == origin,
            "detail": f"head={head}; origin={origin}",
            "pass": head == origin,
        },
        {
            "check": "working_tree_has_only_expected_night_artifacts",
            "value": dirty_ok,
            "detail": dirty_detail,
            "pass": dirty_ok,
        },
        {
            "check": "a7ff51_contract_allowed_by_pm3",
            "value": "A7FF-51 contract" in pm3_allowed,
            "detail": str(pm3_allowed.get("A7FF-51 contract")),
            "pass": "A7FF-51 contract" in pm3_allowed,
        },
        {
            "check": "a7ff24r4_allowed_by_pm3",
            "value": "A7FF-24R4" in pm3_allowed,
            "detail": str(pm3_allowed.get("A7FF-24R4")),
            "pass": "A7FF-24R4" in pm3_allowed,
        },
        {
            "check": "a7ffr11_authorizes_contract_only",
            "value": r11.get("authorizes_a7ff51_contract") and not r11.get("authorizes_generation_execution"),
            "detail": str(r11.get("decision")),
            "pass": bool(r11.get("authorizes_a7ff51_contract") and not r11.get("authorizes_generation_execution")),
        },
        {
            "check": "a7ff24r3_authorizes_contract_only",
            "value": r3.get("authorizes_repaired_queue_numeric_wave_contract") and not r3.get("authorizes_full_12_shard_numeric"),
            "detail": str(r3.get("decision")),
            "pass": bool(r3.get("authorizes_repaired_queue_numeric_wave_contract") and not r3.get("authorizes_full_12_shard_numeric")),
        },
        {
            "check": "global_search_not_authorized",
            "value": not r11.get("authorizes_search") and not r3.get("authorizes_search"),
            "detail": "A7FF-R11 and A7FF-24R3 both deny search",
            "pass": bool(not r11.get("authorizes_search") and not r3.get("authorizes_search")),
        },
    ]
    check_df = pd.DataFrame(checks)
    check_df.to_csv(RUNTIME / "a7night_selfcheck.csv", index=False)

    blockers = check_df.loc[~check_df["pass"], "check"].tolist()
    manifest = {
        "stage": "A7NIGHT-20260531",
        "generated_at": now_utc(),
        "decision": "PASS_A7NIGHT_TASKFLOW_READY" if not blockers else "HOLD_A7NIGHT_TASKFLOW_SELF_CHECK_FAIL",
        "blockers": blockers,
        "contracts": list(contracts.keys()),
        "artifact_budget": {"reports": 1, "runtime_files": 3, "scripts": 1},
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7night_manifest.json", manifest)

    report = f"""# CRYPTO A7 NIGHT TASKFLOW 20260531

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

This night taskflow packages the currently authorized long-task direction without starting unauthorized generation or search. It keeps artifacts compact.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Contracts

```json
{json.dumps(contracts, indent=2, sort_keys=True)}
```

## Self Check

{md_table(check_df)}

## Execution Boundary

```text
generation executed: false
numeric probe executed: false
replay executed: false
search executed: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
