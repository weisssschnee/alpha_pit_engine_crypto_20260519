from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.identity_registry import canonical_identity, exact_signal_identity, syntax_identity


ACCEPTED = REPO / "runtime" / "a7eff2_git_release_20260711" / "a7eff2_accepted_train_validation_oos_log.csv"
RUNTIME = REPO / "runtime" / "a7b0_identity_registry_20260711"
REGISTRY = RUNTIME / "layered_identity_registry.csv"
MANIFEST = RUNTIME / "identity_registry_manifest.json"
REPORT = REPO / "reports" / "CRYPTO_B0_LAYERED_IDENTITY_REGISTRY_20260711.md"


def build() -> dict[str, object]:
    with ACCEPTED.open("r", encoding="utf-8", newline="") as handle:
        accepted = list(csv.DictReader(handle))
    rows = []
    for row in accepted:
        expression = row["expression"]
        rows.append(
            {
                "blueprint_id": row["blueprint_id"],
                "syntax_identity": syntax_identity(expression),
                "syntax_status": "ESTABLISHED_FROM_RELEASE",
                "canonical_identity": canonical_identity(expression),
                "canonical_status": "ESTABLISHED_FROM_RELEASE",
                "exact_signal_identity": exact_signal_identity(row["signal_weight_exact_fingerprint"]),
                "exact_signal_status": "ESTABLISHED_FROM_RELEASE",
                "activation_identity": "",
                "activation_status": "UNRESOLVED_NO_ARTIFACT",
                "pnl_regime_identity": "",
                "pnl_regime_status": "UNRESOLVED_NO_ARTIFACT",
                "economic_hypothesis_identity": "",
                "economic_hypothesis_status": "UNRESOLVED_NO_ARTIFACT",
                "semantic_pair_observation": row.get("semantic_pair", ""),
                "feedback_permission": "REPORT_ONLY_B0",
            }
        )
    counts = {
        "accepted_rows": len(rows),
        "syntax_identities": len({row["syntax_identity"] for row in rows}),
        "canonical_identities": len({row["canonical_identity"] for row in rows}),
        "exact_signal_identities": len({row["exact_signal_identity"] for row in rows}),
        "activation_identities": 0,
        "pnl_regime_identities": 0,
        "economic_hypothesis_identities": 0,
    }
    payload: dict[str, object] = {
        "decision": "PASS_B0_LAYERED_IDENTITY_REGISTRY_WITH_UPPER_LAYERS_UNRESOLVED",
        **counts,
        "first_independent_economic_information_collapse_identified": False,
        "search_started": False,
        "forward_performance_read": False,
        "authorizes_candidate_feedback": False,
    }
    RUNTIME.mkdir(parents=True, exist_ok=True)
    with REGISTRY.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "\n".join(
            [
                "# Crypto B0 Layered Identity Registry",
                "",
                f"Decision: `{payload['decision']}`",
                "",
                f"- accepted rows: `{counts['accepted_rows']}`",
                f"- syntax identities: `{counts['syntax_identities']}`",
                f"- canonical identities: `{counts['canonical_identities']}`",
                f"- exact signal identities: `{counts['exact_signal_identities']}`",
                "- activation identities: `0 / unresolved`",
                "- PnL/regime identities: `0 / unresolved`",
                "- economic hypotheses: `0 / unresolved`",
                "",
                "Semantic pairs are retained only as observations. They are not promoted to economic-hypothesis identities.",
                "",
                "The first collapse of independent economic information remains unidentified.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
