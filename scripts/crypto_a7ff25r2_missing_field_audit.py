from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7ff8_expanded_numeric_probe import expression_fields  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import BASE_DIR, LATENT_PANEL, parquet_schema  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ff25r2_one_shard_numeric_wave"
QUEUE = REPO / "runtime" / "a7ff24r_dry_generation_plan" / "a7ff24r_company_shard_00_queue.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def schema_safe(path: Path) -> tuple[set[str], str]:
    try:
        return set(parquet_schema(path)), ""
    except Exception as exc:  # noqa: BLE001
        return set(), repr(exc)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    queue = pd.read_csv(QUEUE)
    fields = {"trade_close", "realized_vol_168h"}
    for expr in queue["expression"].astype(str):
        fields.update(expression_fields(expr))

    base_schema, base_error = schema_safe(BASE_DIR)
    latent_schema, latent_error = schema_safe(LATENT_PANEL)
    missing = sorted(fields - base_schema - latent_schema)
    rows: list[dict[str, Any]] = []
    for _, row in queue.iterrows():
        expr_fields = expression_fields(str(row["expression"]))
        row_missing = sorted(expr_fields - base_schema - latent_schema)
        if row_missing:
            rows.append(
                {
                    "blueprint_id": row["blueprint_id"],
                    "level": row.get("level", ""),
                    "semantic_pair": row.get("semantic_pair", ""),
                    "motif": row.get("motif", ""),
                    "primary_field": row.get("primary_field", ""),
                    "secondary_field": row.get("secondary_field", ""),
                    "missing_fields": ";".join(row_missing),
                    "expression": row["expression"],
                }
            )
    audit = pd.DataFrame(rows)
    if audit.empty:
        audit = pd.DataFrame(
            columns=[
                "blueprint_id",
                "level",
                "semantic_pair",
                "motif",
                "primary_field",
                "secondary_field",
                "missing_fields",
                "expression",
            ]
        )
    field_table = pd.DataFrame(
        [
            {
                "field_name": field,
                "in_base_schema": field in base_schema,
                "in_latent_schema": field in latent_schema,
                "missing": field in missing,
            }
            for field in sorted(fields)
        ]
    )
    audit.to_csv(RUNTIME / "a7ff25r2_missing_field_audit.csv", index=False)
    field_table.to_csv(RUNTIME / "a7ff25r2_required_field_schema_audit.csv", index=False)
    manifest = {
        "stage": "A7FF-25R2-MISSING-FIELD-AUDIT",
        "generated_at": now_utc(),
        "queue_rows": int(len(queue)),
        "required_field_count": int(len(fields)),
        "base_dir": str(BASE_DIR),
        "base_dir_exists": BASE_DIR.exists(),
        "base_schema_field_count": int(len(base_schema)),
        "base_schema_error": base_error,
        "latent_panel": str(LATENT_PANEL),
        "latent_panel_exists": LATENT_PANEL.exists(),
        "latent_schema_field_count": int(len(latent_schema)),
        "latent_schema_error": latent_error,
        "missing_field_count": int(len(missing)),
        "missing_fields": missing,
        "rows_with_missing_fields": int(len(audit)),
    }
    write_json(RUNTIME / "a7ff25r2_missing_field_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
