from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class BenchmarkSpec:
    benchmark_id: str
    version: int
    kind: str
    input_fields: tuple[str, ...]
    input_roles: tuple[str, ...]
    evaluation_space: str
    description: str
    feedback_permission: str = "REPORT_ONLY"

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkObservation:
    benchmark_id: str
    metric_name: str
    value: float
    epoch_id: str
    epoch_classification: str
    feedback_permission: str = "REPORT_ONLY"


class BenchmarkRegistry:
    def __init__(self) -> None:
        self._specs: dict[str, BenchmarkSpec] = {}

    def register(self, spec: BenchmarkSpec) -> None:
        if spec.benchmark_id in self._specs:
            raise ValueError(f"duplicate benchmark id: {spec.benchmark_id}")
        if spec.version <= 0 or not spec.input_fields or len(spec.input_fields) != len(spec.input_roles):
            raise ValueError("benchmark requires versioned aligned inputs")
        invalid = sorted({role for role in spec.input_roles if role != "benchmark-only"})
        if invalid:
            raise ValueError(f"benchmark accepts benchmark-only inputs, got: {invalid}")
        if spec.feedback_permission != "REPORT_ONLY":
            raise ValueError("benchmark feedback must be REPORT_ONLY")
        self._specs[spec.benchmark_id] = spec

    def get(self, benchmark_id: str) -> BenchmarkSpec:
        return self._specs[benchmark_id]

    def values(self) -> tuple[BenchmarkSpec, ...]:
        return tuple(self._specs[key] for key in sorted(self._specs))


def make_spec(payload: dict[str, object]) -> BenchmarkSpec:
    return BenchmarkSpec(
        benchmark_id=str(payload["benchmark_id"]),
        version=int(payload["version"]),
        kind=str(payload["kind"]),
        input_fields=tuple(str(value) for value in payload["input_fields"]),
        input_roles=tuple(str(value) for value in payload["input_roles"]),
        evaluation_space=str(payload["evaluation_space"]),
        description=str(payload["description"]),
    )


def assert_benchmark_observations_not_memory(observations: Iterable[BenchmarkObservation]) -> None:
    for observation in observations:
        if observation.feedback_permission != "REPORT_ONLY":
            raise PermissionError("benchmark observation cannot enter candidate feedback or memory")
