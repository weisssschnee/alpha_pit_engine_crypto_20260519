from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.temporal_proposal_dispatch_v1 import (
    build_train_only_historical_prior,
)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _retained_candidate_ids(path: Path | None) -> set[str]:
    if path is None:
        return set()
    payload = engine._read_json(path)
    policies = dict(payload.get("policies") or {})
    return {
        str(candidate_id)
        for policy in policies.values()
        for candidate_id in dict(
            (policy.get("realization_v2_state") or {}).get("descendants") or {}
        )
    }


def _campaign(value: str) -> dict[str, object]:
    parts = value.split("|", 2)
    if len(parts) not in {2, 3}:
        raise ValueError("campaign must be ID|LEDGER[|FINAL_STATE]")
    campaign_id, ledger_text = parts[:2]
    ledger_path = Path(ledger_text).resolve()
    state_path = Path(parts[2]).resolve() if len(parts) == 3 and parts[2] else None
    frame = pd.read_parquet(ledger_path)
    return {
        "campaign_id": campaign_id,
        "rows": frame.to_dict("records"),
        "retained_candidate_ids": sorted(_retained_candidate_ids(state_path)),
        "source": {
            "ledger_path": str(ledger_path),
            "ledger_rows": len(frame),
            "ledger_bytes": ledger_path.stat().st_size,
            "ledger_sha256": _file_sha256(ledger_path),
            "checkpoint_state_path": str(state_path) if state_path else None,
            "checkpoint_state_sha256": _file_sha256(state_path) if state_path else None,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    campaigns = [_campaign(value) for value in args.campaign]
    result = build_train_only_historical_prior(campaigns)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    engine._write_json(args.output, result)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
