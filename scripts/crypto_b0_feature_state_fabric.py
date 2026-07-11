from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.fabric import FabricArtifactSpec, write_deterministic_array_cache


RUNTIME = REPO / "runtime" / "a7b0_feature_state_fabric_20260711"
REPORT = REPO / "reports" / "CRYPTO_B0_FEATURE_STATE_FABRIC_20260711.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build() -> dict[str, object]:
    array = np.array([[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]], dtype="<f8")
    spec = FabricArtifactSpec(
        artifact_id="synthetic:event-age:v1",
        artifact_kind="event_state",
        data_role="synthetic_contract_fixture",
        input_role="state-only",
        primitive_equivalence_id="temporal-equivalence:synthetic-event-age",
        source_artifact_shas=("SYNTHETIC_SOURCE_SHA",),
        field_registry_sha=sha(REPO / "runtime" / "a7input0_v2_field_roles_20260711" / "a7input0_v2_field_role_registry.csv"),
        contract_sha=sha(REPO / "config" / "crypto_feature_state_fabric_v1.json"),
        code_sha=sha(REPO / "alphafactory_crypto" / "fabric.py"),
        universe_sha="SYNTHETIC_UNIVERSE_SHA",
        timestamps_sha="SYNTHETIC_TIMESTAMPS_SHA",
        dtype="<f8",
        shape=array.shape,
        endianness="little",
        nan_policy="preserve",
        observable_time_rule="usable_time_at_or_before_row_time",
        maturity_rule="event_state_matured",
        feedback_permission="NO_REWARD_B0",
    )
    cache_root = RUNTIME / "synthetic_cache"
    first = write_deterministic_array_cache(cache_root, spec, array)
    second = write_deterministic_array_cache(cache_root, spec, array.copy())
    if first["cache_key"] != second["cache_key"] or first["content_sha256"] != second["content_sha256"]:
        raise RuntimeError("Fabric cache is not deterministic")
    payload: dict[str, object] = {
        "decision": "PASS_B0_FEATURE_STATE_FABRIC_SCHEMA_AND_CACHE_CONTRACT",
        "synthetic_cache_key": first["cache_key"],
        "synthetic_content_sha256": first["content_sha256"],
        "deterministic_rebuild_match": True,
        "real_feature_or_state_built": False,
        "state_event_reward_allowed_b0": False,
        "generator_enabled_b0": False,
        "search_started": False,
        "forward_performance_read": False,
    }
    RUNTIME.mkdir(parents=True, exist_ok=True)
    (RUNTIME / "feature_state_fabric_manifest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "\n".join(
            [
                "# Crypto B0 Feature/State Fabric",
                "",
                f"Decision: `{payload['decision']}`",
                "",
                "- deterministic cache fixture rebuild match: `true`",
                "- real feature/state materialized: `false`",
                "- machine path in cache key: `false`",
                "- atomic write and content SHA verification: `true`",
                "- State/event to reward: `false`",
                "- generator enabled: `false`",
                "",
                "This is a schema and cache contract only. B1 remains frozen.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
