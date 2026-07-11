from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.bz import create_benchmark_zero


INPUT_REGISTRY = REPO / "runtime" / "a7input0_v2_field_roles_20260711" / "a7input0_v2_field_role_registry.csv"
RUNTIME = REPO / "runtime" / "a7b0_bz_authority_20260711"
REPORT = REPO / "reports" / "CRYPTO_B0_BZ_BENCHMARK_ZERO_20260711.md"


def build() -> dict[str, object]:
    with INPUT_REGISTRY.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    benchmark_fields = sorted(row["field_name"] for row in rows if row["input_role"] == "benchmark-only")
    bz = create_benchmark_zero(benchmark_fields, ["benchmark-only"] * len(benchmark_fields))
    payload = bz.as_dict() | {
        "decision": "PASS_B0_BZ_BENCHMARK_ZERO_AUTHORITY",
        "legacy_undefined_bz_valid": False,
        "search_started": False,
        "forward_performance_read": False,
        "authorizes_promotion": False,
    }
    RUNTIME.mkdir(parents=True, exist_ok=True)
    (RUNTIME / "bz_authority_manifest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "\n".join(
            [
                "# Crypto B0 BZ Authority",
                "",
                "`BZ` uniquely means `Benchmark Zero`.",
                "",
                f"- authority: `{bz.authority_id}`",
                f"- entrypoint: `alphafactory_crypto.bz.create_benchmark_zero`",
                f"- benchmark-only fields: `{benchmark_fields}`",
                "- expected alpha: `0.0`",
                "- feedback permission: `NONE`",
                "- promotion authorization: `false`",
                "",
                "Any earlier undefined BZ mention is an invalid alias until explicitly migrated to this authority.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
