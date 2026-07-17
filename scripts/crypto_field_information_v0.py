from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphafactory_crypto.broad_search.panel18m import RawPanelStore
from alphafactory_crypto.field_information import (
    FieldBatchProvider,
    build_core_pack,
    compile_token_catalog,
    cross_fitted_ridge_residual,
    information_census,
    payload_sha256,
    sha256_file,
)


def _git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _month_ids(timestamps: np.ndarray) -> np.ndarray:
    return pd.to_datetime(timestamps, utc=True).to_period("M").astype(str).to_numpy()


def _field_meta(catalog: pd.DataFrame) -> dict[str, dict[str, Any]]:
    return catalog.set_index("field_id", drop=False).to_dict("index")


def _broad_context(config: dict[str, Any], catalog: pd.DataFrame) -> pd.DataFrame:
    spec = config["contexts"]["BROAD_PANEL_BASELINE"]
    store = RawPanelStore.open(ROOT / config["inputs"]["broad_cache"])
    source_slice = store.block_slice(spec["start"], spec["end_exclusive"])
    provider = FieldBatchProvider.from_raw_panel(store, source_slice)
    registry = json.loads((ROOT / config["inputs"]["broad_registry"]).read_text(encoding="utf-8"))
    fields = [row["field_id"] for row in registry["fields"]]
    timestamps = np.asarray(store.timestamp_ns[source_slice], dtype=np.int64)
    target = np.asarray(store.target_return(spec["target_horizon_hours"])[..., source_slice], dtype=float)
    eligible = np.asarray(store.base_eligible()[..., source_slice], dtype=bool) & np.isfinite(target)
    known = provider.load(
        [f"FIELD:{field}" for field in spec["known_fields"]], slice(None), slice(0, provider.time_count)
    ).values
    residual = cross_fitted_ridge_residual(
        known, target, eligible, _month_ids(timestamps), config["statistics"]["ridge"]
    )
    fit_stop = int(
        np.searchsorted(timestamps, pd.Timestamp(spec["bin_fit_end_exclusive"]).value)
    )
    meta = _field_meta(catalog)
    for row in registry["fields"]:
        current = meta.setdefault(row["field_id"], {})
        current.update(
            family=row["field_family"],
            availability_scope="OBSERVED_ARCHIVE_ADAPTIVE_DEVELOPMENT",
            pit_source_status="DECLARED_1H_LAG_NOT_REVERIFIED_BY_CENSUS",
            runtime_loaded=bool(row.get("current_runtime_baseline", False)),
        )
    return information_census(
        context_id="BROAD_PANEL_BASELINE",
        provider=provider,
        field_ids=fields,
        field_meta=meta,
        target=target,
        residual_target=residual,
        eligible=eligible,
        timestamps=timestamps,
        bin_fit_slice=slice(0, fit_stop),
        bins=config["statistics"]["quantile_bins"],
        maximum_samples=config["statistics"]["maximum_samples_per_field"],
        null_shifts_hours=config["statistics"]["block_permutation_shifts_hours"],
    )


def _core3_context(config: dict[str, Any], catalog: pd.DataFrame) -> pd.DataFrame:
    spec = config["contexts"]["CORE3_MICROSTRUCTURE_PILOT"]
    base = pd.read_csv(ROOT / config["inputs"]["aggtrades_base"])
    fields = base["field_name"].tolist()
    columns = list(dict.fromkeys(
        ["symbol", "timestamp", "close", "agg_features_available", *fields, *spec["known_fields"]]
    ))
    frame = pd.read_parquet(config["inputs"]["core3_panel"], columns=columns)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame.loc[
        frame["symbol"].isin(spec["symbols"])
        & frame["timestamp"].ge(pd.Timestamp(spec["start"]))
        & frame["timestamp"].lt(pd.Timestamp(spec["end_exclusive"]))
        & frame["agg_features_available"].astype(bool)
    ].sort_values(["symbol", "timestamp"])
    groups = {symbol: group for symbol, group in frame.groupby("symbol", sort=False)}
    if set(groups) != set(spec["symbols"]):
        raise ValueError("core3 context is incomplete")
    timestamps = groups[spec["symbols"][0]]["timestamp"].to_numpy(dtype="datetime64[ns]")
    for symbol in spec["symbols"]:
        if not np.array_equal(groups[symbol]["timestamp"].to_numpy(dtype="datetime64[ns]"), timestamps):
            raise ValueError(f"core3 timestamp mismatch for {symbol}")
    cube = np.stack(
        [groups[symbol][fields].to_numpy(dtype=np.float32).T for symbol in spec["symbols"]]
    )
    known = np.stack(
        [groups[symbol][spec["known_fields"]].to_numpy(dtype=np.float32).T for symbol in spec["symbols"]]
    )
    close = np.stack([groups[symbol]["close"].to_numpy(dtype=float) for symbol in spec["symbols"]])
    target = np.full(close.shape, np.nan, dtype=float)
    target[:, :-6] = np.log(close[:, 6:] / close[:, 2:-4])
    eligible = np.isfinite(target) & np.all(np.isfinite(known), axis=1)
    timestamp_ns = timestamps.astype("datetime64[ns]").astype(np.int64)
    residual = cross_fitted_ridge_residual(
        known, target, eligible, _month_ids(timestamp_ns), config["statistics"]["ridge"]
    )
    provider = FieldBatchProvider.from_cube(fields, cube)
    fit_stop = int(
        np.searchsorted(timestamp_ns, pd.Timestamp(spec["bin_fit_end_exclusive"]).value)
    )
    meta = _field_meta(catalog)
    return information_census(
        context_id="CORE3_MICROSTRUCTURE_PILOT",
        provider=provider,
        field_ids=fields,
        field_meta=meta,
        target=target,
        residual_target=residual,
        eligible=eligible,
        timestamps=timestamp_ns,
        bin_fit_slice=slice(0, fit_stop),
        bins=config["statistics"]["quantile_bins"],
        maximum_samples=config["statistics"]["maximum_samples_per_field"],
        null_shifts_hours=config["statistics"]["block_permutation_shifts_hours"],
    )


def _report(census: pd.DataFrame, core_pack: list[dict[str, Any]], manifest: dict[str, Any]) -> str:
    lines = [
        "# Crypto Field Information V0",
        "",
        "Development-only field qualification; no OOS read, performance search, or promotion.",
        "",
        f"- Source SHA: `{manifest['source_sha']}`",
        f"- Token rows: {manifest['counts']['token_rows']}",
        f"- Census rows: {manifest['counts']['census_rows']}",
        f"- Core Pack tokens: {manifest['counts']['core_pack_tokens']}",
        f"- Unmaterialized derived specs: {manifest['counts']['unmaterialized_derived_specs']}",
        "",
    ]
    for context, group in census.groupby("context_id"):
        lines.extend([
            f"## {context}",
            "",
            f"- Fields audited: {len(group)}",
            f"- Median coverage: {group['coverage_ratio'].median():.6f}",
            f"- Missingness flags: {(group['missingness_flag'] != '').sum()}",
            f"- Redundancy clusters: {group['redundancy_cluster_id'].nunique()}",
            "",
            "Top residual-information fields:",
            "",
        ])
        for row in group.nlargest(10, "residual_mi_excess").itertuples():
            lines.append(
                f"- `{row.field_id}`: residual excess={row.residual_mi_excess:.6g}, "
                f"coverage={row.coverage_ratio:.4f}, block-positive={row.positive_block_ratio:.3f}"
            )
        lines.append("")
    lines.extend([
        "## Claim boundary",
        "",
        "The Core3 result is `CORE3_MICROSTRUCTURE_MECHANISM_EVIDENCE` only. "
        "The Core Pack is a context-bound proposed model surface, not an active runtime registry, alpha proof, OOS result, or promotion candidate.",
        "",
    ])
    return "\n".join(lines)


def run(config_path: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    runtime_root = ROOT / config["outputs"]["runtime_root"]
    report_path = ROOT / config["outputs"]["report"]
    runtime_root.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    catalog = compile_token_catalog(ROOT, config)
    broad = _broad_context(config, catalog)
    core3 = _core3_context(config, catalog)
    census = pd.concat([broad, core3], ignore_index=True)
    pack = build_core_pack(census, catalog, **{
        "minimum_size": config["core_pack"]["minimum_size"],
        "target_size": config["core_pack"]["target_size"],
        "maximum_size": config["core_pack"]["maximum_size"],
    })

    token_path = runtime_root / "token_catalog.parquet"
    census_path = runtime_root / "information_census.parquet"
    pack_path = runtime_root / "core_pack_manifest.json"
    manifest_path = runtime_root / "run_manifest.json"
    catalog.to_parquet(token_path, index=False)
    census.to_parquet(census_path, index=False)
    pack_payload = {
        "schema_version": 1,
        "status": "CONTEXT_BOUND_PROPOSED_MODEL_SURFACE",
        "tokens": pack,
        "boundaries": config["boundaries"],
    }
    pack_path.write_text(json.dumps(pack_payload, indent=2, sort_keys=True), encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "run_id": config["run_id"],
        "source_sha": _git_sha(),
        "config_sha256": sha256_file(config_path),
        "counts": {
            "token_rows": len(catalog),
            "base_or_registered_tokens": int((catalog["token_kind"] != "DERIVED").sum()),
            "derived_spec_tokens": int((catalog["token_kind"] == "DERIVED").sum()),
            "census_rows": len(census),
            "broad_fields_audited": len(broad),
            "core3_base_fields_audited": len(core3),
            "core_pack_tokens": len(pack),
            "unmaterialized_derived_specs": int((catalog["token_kind"] == "DERIVED").sum()),
        },
        "contexts": {
            "BROAD_PANEL_BASELINE": {"latest_timestamp_exclusive": "2024-07-01T00:00:00Z"},
            "CORE3_MICROSTRUCTURE_PILOT": {
                "symbols": config["contexts"]["CORE3_MICROSTRUCTURE_PILOT"]["symbols"],
                "latest_timestamp_exclusive": "2024-07-01T00:00:00Z",
                "claim_scope": "CORE3_MICROSTRUCTURE_MECHANISM_EVIDENCE",
            },
        },
        "boundaries": config["boundaries"],
        "files": {},
    }
    manifest["identity_sha256"] = payload_sha256({k: v for k, v in manifest.items() if k != "files"})
    report_path.write_text(_report(census, pack, manifest), encoding="utf-8")
    for path in [token_path, census_path, pack_path, report_path]:
        manifest["files"][str(path.relative_to(ROOT)).replace("\\", "/")] = sha256_file(path)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "config/crypto_field_information_v0.json")
    args = parser.parse_args()
    print(json.dumps(run(args.config), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
