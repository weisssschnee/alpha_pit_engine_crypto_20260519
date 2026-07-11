from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


FABRIC_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class FabricArtifactSpec:
    artifact_id: str
    artifact_kind: str
    data_role: str
    input_role: str
    primitive_equivalence_id: str
    source_artifact_shas: tuple[str, ...]
    field_registry_sha: str
    contract_sha: str
    code_sha: str
    universe_sha: str
    timestamps_sha: str
    dtype: str
    shape: tuple[int, ...]
    endianness: str
    nan_policy: str
    observable_time_rule: str
    maturity_rule: str
    feedback_permission: str


def _canonical_payload(spec: FabricArtifactSpec) -> dict[str, Any]:
    payload = asdict(spec)
    payload["schema_version"] = FABRIC_SCHEMA_VERSION
    payload["source_artifact_shas"] = sorted(spec.source_artifact_shas)
    payload["shape"] = list(spec.shape)
    return payload


def deterministic_cache_key(spec: FabricArtifactSpec) -> str:
    payload = json.dumps(_canonical_payload(spec), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "fabric:" + hashlib.sha256(payload).hexdigest()


def _content_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def validate_spec(spec: FabricArtifactSpec) -> None:
    if spec.artifact_kind not in {"feature", "state", "event_state", "benchmark"}:
        raise ValueError("invalid Fabric artifact kind")
    if spec.input_role == "blocked":
        raise PermissionError("blocked input cannot enter Fabric")
    if spec.artifact_kind in {"state", "event_state"} and spec.feedback_permission != "NO_REWARD_B0":
        raise PermissionError("state/event Fabric artifacts must be frozen from reward in B0")
    if not spec.shape or any(int(value) <= 0 for value in spec.shape):
        raise ValueError("Fabric shape must be positive")
    if spec.endianness not in {"little", "big", "not-applicable"}:
        raise ValueError("invalid endianness")
    dtype_marker = np.dtype(spec.dtype).str[0]
    if spec.endianness == "little" and dtype_marker == ">":
        raise ValueError("dtype and declared little endianness disagree")
    if spec.endianness == "big" and dtype_marker == "<":
        raise ValueError("dtype and declared big endianness disagree")
    if spec.endianness == "not-applicable" and dtype_marker != "|":
        raise ValueError("byte-order-sensitive dtype requires explicit endianness")


def _storage_dtype(spec: FabricArtifactSpec) -> np.dtype[Any]:
    order = {"little": "<", "big": ">", "not-applicable": "|"}[spec.endianness]
    return np.dtype(spec.dtype).newbyteorder(order)


def write_deterministic_array_cache(root: Path, spec: FabricArtifactSpec, array: np.ndarray) -> dict[str, Any]:
    validate_spec(spec)
    normalized = np.asarray(array, dtype=_storage_dtype(spec), order="C")
    if tuple(normalized.shape) != tuple(spec.shape):
        raise ValueError("array shape does not match Fabric spec")
    root.mkdir(parents=True, exist_ok=True)
    key = deterministic_cache_key(spec)
    stem = key.split(":", 1)[1]
    data_path = root / f"{stem}.bin"
    manifest_path = root / f"{stem}.manifest.json"
    temp_path = root / f".{stem}.tmp"
    temp_path.write_bytes(normalized.tobytes(order="C"))
    content_sha = _content_sha(temp_path)
    os.replace(temp_path, data_path)
    manifest = _canonical_payload(spec) | {
        "cache_key": key,
        "content_sha256": content_sha,
        "data_file": data_path.name,
        "write_mode": "atomic_replace",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validate_cache(manifest_path)
    return manifest


def validate_cache(manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    spec_fields = {field.name for field in FabricArtifactSpec.__dataclass_fields__.values()}
    spec_payload = {key: manifest[key] for key in spec_fields}
    spec_payload["source_artifact_shas"] = tuple(spec_payload["source_artifact_shas"])
    spec_payload["shape"] = tuple(spec_payload["shape"])
    spec = FabricArtifactSpec(**spec_payload)
    validate_spec(spec)
    if deterministic_cache_key(spec) != manifest["cache_key"]:
        raise ValueError("Fabric cache key mismatch")
    data_path = manifest_path.parent / manifest["data_file"]
    if _content_sha(data_path) != manifest["content_sha256"]:
        raise ValueError("Fabric content SHA mismatch")
    return manifest
