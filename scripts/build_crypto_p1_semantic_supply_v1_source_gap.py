from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd
import pyarrow.parquet as pq


P1 = "P1_POSITION_STATE_CHANGE_TO_RESPONSE"
SAFE_COLUMNS = (
    "candidate_id",
    "candidate_spec_json",
    "program_family_id",
    "program_id",
    "matched_positive",
    "left_incremental_net_mean",
    "right_incremental_net_mean",
    "replicated_candidate",
    "search_reward",
    "targeted_economic_basin_id",
    "behavior_family_id",
    "evaluation_partition",
)


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest().upper()


def _as_bool(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes"}
    return bool(value)


def _program_spec(row: Mapping[str, Any]) -> dict[str, Any]:
    candidate = json.loads(str(row["candidate_spec_json"]))
    genes = dict(candidate["generation_genes"])
    spec = dict(genes["program_spec"])
    if (
        str(spec.get("family_id")) != P1
        or str(spec.get("program_id")) != str(row["program_id"])
    ):
        raise ValueError("P1 program identity changed in historical ledger")
    return spec


def _signature(spec: Mapping[str, Any]) -> tuple[str, ...]:
    return (
        str(spec["left_role"]),
        str(spec["right_role"]),
        str(spec["left_components"][0]),
        str(spec["right_components"][0]),
        str(spec["outer_operator"]),
    )


def build_source_gap(campaigns: Sequence[tuple[str, Path]]) -> dict[str, Any]:
    aggregates: dict[str, dict[str, Any]] = {}
    sources = []
    partitions = set()
    for campaign_id, path in campaigns:
        available = set(pq.ParquetFile(path).schema.names)
        required = set(SAFE_COLUMNS) - {"targeted_economic_basin_id"}
        if not required.issubset(available):
            raise ValueError(
                "historical P1 ledger is missing required columns: "
                + ",".join(sorted(required - available))
            )
        frame = pd.read_parquet(
            path, columns=[name for name in SAFE_COLUMNS if name in available]
        )
        if "targeted_economic_basin_id" not in frame:
            frame["targeted_economic_basin_id"] = None
        sources.append(
            {
                "campaign_id": campaign_id,
                "path": str(path),
                "rows": len(frame),
                "bytes": path.stat().st_size,
                "sha256": _sha_file(path),
            }
        )
        partitions.update(str(value) for value in frame["evaluation_partition"].dropna().unique())
        frame = frame.loc[frame["program_family_id"].astype(str) == P1]
        for row in frame.to_dict("records"):
            program_id = str(row["program_id"])
            spec = _program_spec(row)
            record = aggregates.setdefault(
                program_id,
                {
                    "program_id": program_id,
                    "program_spec": spec,
                    "attempts": 0,
                    "matched_positive": 0,
                    "dual_positive": 0,
                    "replicated": 0,
                    "positive_reward": 0,
                    "reward_sum": 0.0,
                    "reward_max": float("-inf"),
                    "campaigns": set(),
                    "basins": set(),
                    "behavior_families": set(),
                },
            )
            if record["program_spec"] != spec:
                raise ValueError("historical program spec drift")
            record["attempts"] += 1
            record["matched_positive"] += int(_as_bool(row["matched_positive"]))
            record["dual_positive"] += int(
                float(row["left_incremental_net_mean"] or 0.0) > 0.0
                and float(row["right_incremental_net_mean"] or 0.0) > 0.0
            )
            record["replicated"] += int(_as_bool(row["replicated_candidate"]))
            reward = float(row["search_reward"] or 0.0)
            record["positive_reward"] += int(reward > 0.0)
            record["reward_sum"] += reward
            record["reward_max"] = max(record["reward_max"], reward)
            record["campaigns"].add(campaign_id)
            basin = str(row.get("targeted_economic_basin_id") or "")
            if basin and basin.lower() != "nan":
                record["basins"].add(basin)
            record["behavior_families"].add(str(row["behavior_family_id"]))

    rows = []
    for record in aggregates.values():
        attempts = int(record["attempts"])
        matched = int(record["matched_positive"])
        evidence_score = (
            12.0 * matched
            + 3.0 * int(record["replicated"])
            + 1.5 * int(record["dual_positive"])
            + 0.25 * int(record["positive_reward"])
            + 4.0 * len(record["basins"])
            + 2.0 * len(record["campaigns"])
            + max(-2.0, min(4.0, float(record["reward_max"])))
        ) / max(12.0, attempts ** 0.5)
        rows.append(
            {
                **{key: value for key, value in record.items() if key not in {"campaigns", "basins", "behavior_families"}},
                "matched_density": matched / max(1, attempts),
                "campaign_count": len(record["campaigns"]),
                "campaigns": sorted(record["campaigns"]),
                "targeted_basin_count": len(record["basins"]),
                "behavior_family_count": len(record["behavior_families"]),
                "structural_signature": list(_signature(record["program_spec"])),
                "evidence_score": evidence_score,
            }
        )
    rows.sort(key=lambda row: (-float(row["evidence_score"]), str(row["program_id"])))

    selected: list[dict[str, Any]] = []
    covered: dict[str, set[str]] = defaultdict(set)
    dimensions = {
        "left_role": 0,
        "right_role": 1,
        "left_component": 2,
        "right_component": 3,
        "payload_operator": 4,
    }
    remaining = list(rows)
    while remaining and len(selected) < 24:
        def key(row: Mapping[str, Any]) -> tuple[Any, ...]:
            signature = list(row["structural_signature"])
            novelty = sum(signature[index] not in covered[name] for name, index in dimensions.items())
            economic = int(row["matched_positive"]) > 0 or int(row["dual_positive"]) > 0
            return (-int(economic), -novelty, -float(row["evidence_score"]), str(row["program_id"]))

        chosen = min(remaining, key=key)
        remaining.remove(chosen)
        selected.append(chosen)
        for name, index in dimensions.items():
            covered[name].add(str(chosen["structural_signature"][index]))

    core = {
        "schema_version": 1,
        "status": "P1_TRAIN_ONLY_SEMANTIC_SOURCE_GAP_READY",
        "family_id": P1,
        "selection_rule": "EVIDENCE_FIRST_GREEDY_STRUCTURAL_COVERAGE_24",
        "source_campaigns": sources,
        "source_partitions": sorted(partitions),
        "observed_p1_program_count": len(rows),
        "selected_parent_count": len(selected),
        "selected_parent_programs": selected,
        "unselected_program_count": len(rows) - len(selected),
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
    }
    return {**core, "source_gap_sha256": _sha(core)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", action="append", nargs=2, metavar=("ID", "LEDGER"), required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = build_source_gap([(campaign, Path(path)) for campaign, path in args.campaign])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "selected_parent_count": payload["selected_parent_count"], "source_gap_sha256": payload["source_gap_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
