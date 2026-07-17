from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphafactory_crypto.core_pack_consumption import (  # noqa: E402
    BROAD_CONTEXT,
    CORE3_CONTEXT,
    dense_consumption_probe,
    materialize_broad_context,
    materialize_core3_context,
    payload_sha256,
    qualify_consumption_rows,
    resolve_core_pack,
    sha256_file,
)


def _git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _report(manifest: dict[str, Any], contexts: dict[str, Any], rows: pd.DataFrame) -> str:
    failed = rows.loc[~rows["consumption_pass"]]
    lines = [
        "# Crypto 120-token Core Pack consumption qualification",
        "",
        "This is a development-only plumbing qualification. It is not model-quality, alpha, portfolio, economic, or OOS evidence.",
        "",
        f"- Source SHA: `{manifest['source_sha']}`",
        f"- Status: `{manifest['status']}`",
        f"- Core Pack identity: `{manifest['input_identities']['core_pack_sha256']}`",
        f"- Plumbing-connected tokens: {manifest['counts']['plumbing_pass_tokens']}/{manifest['counts']['tokens']}",
        f"- Nontrivially utilized tokens: {manifest['counts']['consumption_pass_tokens']}/{manifest['counts']['tokens']}",
        f"- Runtime seconds: {manifest['cost_time']['actual_wall_seconds']:.3f}",
        "",
        "## Context separation",
        "",
        "The pack remains two independent model surfaces. No synthetic 120-channel joint panel was created.",
        "",
    ]
    for context, summary in contexts.items():
        probe = summary["probe"]
        lines.extend(
            [
                f"### {context}",
                "",
                f"- Value channels: {probe['value_channels']}",
                f"- Probe samples: {probe['samples']}",
                f"- Gradient reachable: {probe['gradient_reachable_channels']}/{probe['value_channels']}",
                f"- First-layer parameters updated: {probe['updated_value_channels']}/{probe['value_channels']}",
                f"- Prediction-sensitive under zero ablation: {probe['ablation_sensitive_channels']}/{probe['value_channels']}",
                f"- Data range: {summary['materialization']['actual_start']} through {summary['materialization']['actual_end']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Derived execution contract",
            "",
            "Core3 lazy tokens are resolved before execution: TSMean is a trailing same-symbol mean; Delta is a trailing same-symbol difference; ZScore is the historical `ZScore(TSMean(field, window))` cross-sectional execution; Decay is bound to the current `CryptoFeatureAlgebra` linear-decay implementation. Registry availability lag is aligned before the probe, and same-hour execution remains forbidden.",
            "",
            "## Failures",
            "",
            "None." if failed.empty else failed[["context_id", "token_id"]].to_markdown(index=False),
            "",
            "## Claim boundary",
            "",
            "A passing token proves loadability, materialization, tensor exposure, gradient reachability, parameter update, and prediction sensitivity in this frozen probe. It does not prove unique information, stable learning value, portfolio increment, economic value, or OOS validity.",
            "",
        ]
    )
    return "\n".join(lines)


def run(config_path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output_root = ROOT / config["outputs"]["runtime_root"]
    report_path = ROOT / config["outputs"]["report"]
    output_root.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    core_pack_path = ROOT / config["inputs"]["core_pack"]
    base_path = ROOT / config["inputs"]["aggtrades_base"]
    derived_path = ROOT / config["inputs"]["aggtrades_derived"]
    pack = json.loads(core_pack_path.read_text(encoding="utf-8"))
    contracts = resolve_core_pack(
        pack,
        pd.read_csv(base_path),
        pd.read_csv(derived_path),
        expected_tokens=int(config["frozen_budget"]["tokens"]),
    )
    contract_payload = {
        "schema_version": 1,
        "status": "FROZEN_EXECUTABLE_CONTEXT_CONTRACT",
        "tokens": [row.to_dict() for row in contracts],
        "boundaries": config["boundaries"],
    }
    contract_payload["identity_sha256"] = payload_sha256(contract_payload)

    broad_values, broad_target, broad_stats, broad_materialization = materialize_broad_context(
        ROOT / config["inputs"]["broad_cache"],
        contracts,
        config["contexts"][BROAD_CONTEXT],
        probe_assets=int(config["contexts"][BROAD_CONTEXT]["probe_assets"]),
        probe_start=config["contexts"][BROAD_CONTEXT]["probe_start"],
    )
    core_values, core_target, core_stats, core_materialization = materialize_core3_context(
        Path(config["inputs"]["core3_panel"]),
        contracts,
        config["contexts"][CORE3_CONTEXT],
    )
    probe_config = config["consumer_probe"]
    probe_kwargs = {
        "seed": int(probe_config["seed"]),
        "maximum_samples": int(probe_config["maximum_samples_per_context"]),
        "epochs": int(probe_config["epochs"]),
        "hidden_width": int(probe_config["hidden_width"]),
        "learning_rate": float(probe_config["learning_rate"]),
        "ablation_samples": int(probe_config["ablation_samples"]),
    }
    broad_probe, broad_probe_rows = dense_consumption_probe(
        broad_values, broad_target, **probe_kwargs
    )
    core_probe, core_probe_rows = dense_consumption_probe(
        core_values, core_target, **probe_kwargs
    )
    broad_rows = qualify_consumption_rows(
        broad_stats,
        broad_probe_rows,
        minimum_finite_ratio=float(probe_config["minimum_finite_ratio"]),
    )
    core_rows = qualify_consumption_rows(
        core_stats,
        core_probe_rows,
        minimum_finite_ratio=float(probe_config["minimum_finite_ratio"]),
    )
    token_rows = pd.DataFrame([*broad_rows, *core_rows]).sort_values("ordinal")
    passed = int(token_rows["consumption_pass"].sum())
    status = (
        "CORE_PACK_CONTEXT_BOUND_CONSUMPTION_VERIFIED"
        if passed == len(token_rows) == int(config["frozen_budget"]["tokens"])
        else "CORE_PACK_CONSUMPTION_PARTIAL"
    )
    context_evidence = {
        BROAD_CONTEXT: {"materialization": broad_materialization, "probe": broad_probe},
        CORE3_CONTEXT: {"materialization": core_materialization, "probe": core_probe},
    }

    contract_path = output_root / "resolved_token_contract.json"
    token_path = output_root / "token_consumption_evidence.csv"
    context_path = output_root / "context_consumption_summary.json"
    manifest_path = output_root / "run_manifest.json"
    _write_json(contract_path, contract_payload)
    token_rows.to_csv(token_path, index=False, lineterminator="\n")
    _write_json(context_path, context_evidence)

    panel_path = Path(config["inputs"]["core3_panel"])
    cache_metadata = ROOT / config["inputs"]["broad_cache"] / "metadata.json"
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "objective": config["objective"],
        "status": status,
        "source_sha": _git_sha(),
        "created_at": _now(),
        "command": "python scripts/crypto_core_pack_consumption_v1.py",
        "parameters": {
            "contexts": config["contexts"],
            "consumer_probe": probe_config,
            "frozen_budget": config["frozen_budget"],
        },
        "input_identities": {
            "config_sha256": sha256_file(config_path),
            "core_pack_sha256": sha256_file(core_pack_path),
            "aggtrades_base_sha256": sha256_file(base_path),
            "aggtrades_derived_sha256": sha256_file(derived_path),
            "broad_registry_sha256": sha256_file(ROOT / config["inputs"]["broad_registry"]),
            "broad_cache_metadata_sha256": sha256_file(cache_metadata),
            "broad_cache_identity_sha256": json.loads(cache_metadata.read_text())["identity_sha256"],
            "core3_panel_sha256": sha256_file(panel_path),
            "core3_panel_bytes": panel_path.stat().st_size,
            "resolved_contract_identity_sha256": contract_payload["identity_sha256"],
        },
        "counts": {
            "tokens": int(len(token_rows)),
            "broad_tokens": int((token_rows["context_id"] == BROAD_CONTEXT).sum()),
            "core3_tokens": int((token_rows["context_id"] == CORE3_CONTEXT).sum()),
            "base_tokens": int((token_rows["token_kind"] == "BASE").sum()),
            "derived_tokens": int((token_rows["token_kind"] == "DERIVED").sum()),
            "consumption_pass_tokens": passed,
            "plumbing_pass_tokens": int(token_rows["plumbing_pass"].sum()),
        },
        "contexts": context_evidence,
        "cost_time": {
            "estimated_wall_minutes": config["frozen_budget"]["estimated_wall_minutes"],
            "estimated_peak_memory_gb": config["frozen_budget"]["estimated_peak_memory_gb"],
            "actual_wall_seconds": float(time.perf_counter() - started),
        },
        "reproducibility": {
            "reproducible": True,
            "fixed_seed": probe_config["seed"],
            "continuation": "Rerun the exact command at source_sha with the same content-hash-bound inputs; do not merge contexts or open economic evaluation.",
            "failure": None if passed == len(token_rows) else "See token_consumption_evidence.csv",
        },
        "decision": "N/A_CONSUMPTION_QUALIFICATION_ONLY",
        "boundaries": config["boundaries"],
        "files": {},
    }
    manifest["identity_sha256"] = payload_sha256(
        {key: value for key, value in manifest.items() if key != "files"}
    )
    report_path.write_text(
        _report(manifest, context_evidence, token_rows), encoding="utf-8", newline="\n"
    )
    for path in (contract_path, token_path, context_path, report_path):
        manifest["files"][path.relative_to(ROOT).as_posix()] = sha256_file(path)
    _write_json(manifest_path, manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "config/crypto_core_pack_consumption_v1.json",
    )
    args = parser.parse_args()
    print(json.dumps(run(args.config), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
