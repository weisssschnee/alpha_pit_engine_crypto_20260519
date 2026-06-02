from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from crypto_a7ffcore49e_full_universe_null_vector_preflight_execution import read_base_panel, overlay_latent_fields
from crypto_a7ffcore51e_filtered_replay_execution import add_labels


CONTRACT = REPO / "runtime" / "a7ffcore51px_company_sharded_replay_runner_contract"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="Output compact frame parquet path")
    parser.add_argument("--contract", default=str(CONTRACT), help="CORE51PX contract runtime directory")
    args = parser.parse_args()

    contract = Path(args.contract)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    field_contract = pd.read_csv(contract / "a7ffcore51px_compact_frame_contract.csv")
    fields = field_contract.loc[field_contract["status"].eq("present"), "field_name"].astype(str).tolist()
    read_fields = sorted(set(fields) - {"symbol", "timestamp"})
    frame = read_base_panel(read_fields)
    frame = overlay_latent_fields(frame, read_fields)
    frame = add_labels(frame)
    keep_cols = sorted(set(["symbol", "timestamp", *read_fields, *[c for c in frame.columns if c.startswith("label_")]]))
    frame = frame[[c for c in keep_cols if c in frame.columns]].copy()
    frame.to_parquet(out, index=False)
    manifest = {
        "stage": "A7FF-CORE51PX-COMPACT-FRAME",
        "generated_at": now_utc(),
        "output_path": str(out).replace("\\", "/"),
        "rows": int(frame.shape[0]),
        "columns": int(frame.shape[1]),
        "symbols": int(frame["symbol"].nunique()) if "symbol" in frame else 0,
        "timestamps": int(frame["timestamp"].nunique()) if "timestamp" in frame else 0,
        "executes_replay": False,
        "executes_search": False,
    }
    out.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
