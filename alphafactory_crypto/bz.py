from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


BZ_AUTHORITY_ID = "CRYPTO-BZ-BENCHMARK-ZERO-V1"


@dataclass(frozen=True)
class BenchmarkZero:
    authority_id: str
    object_id: str
    name: str
    input_fields: tuple[str, ...]
    input_roles: tuple[str, ...]
    expected_alpha: float
    feedback_permission: str
    allowed_uses: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def create_benchmark_zero(fields: Iterable[str], roles: Iterable[str]) -> BenchmarkZero:
    field_tuple = tuple(str(field) for field in fields)
    role_tuple = tuple(str(role) for role in roles)
    if not field_tuple or len(field_tuple) != len(role_tuple):
        raise ValueError("BZ requires aligned non-empty fields and roles")
    invalid = sorted({role for role in role_tuple if role != "benchmark-only"})
    if invalid:
        raise ValueError(f"BZ accepts benchmark-only inputs, got: {invalid}")
    return BenchmarkZero(
        authority_id=BZ_AUTHORITY_ID,
        object_id="bz:benchmark-zero:v1",
        name="Benchmark Zero",
        input_fields=field_tuple,
        input_roles=role_tuple,
        expected_alpha=0.0,
        feedback_permission="NONE",
        allowed_uses=("pipeline_sanity", "benchmark_delta", "diagnostic_report", "cache_parity_test"),
    )


def assert_bz_use_allowed(use: str) -> None:
    allowed = {"pipeline_sanity", "benchmark_delta", "diagnostic_report", "cache_parity_test"}
    if use not in allowed:
        raise PermissionError(f"BZ use is forbidden: {use}")
