from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7al0l_fixed_delay_stress_abolition"
REPORT = REPO / "reports" / "CRYPTO_A7AL0L_FIXED_DELAY_STRESS_ABOLITION_20260527.md"

SCAN_DIRS = ["scripts", "config", "alphafactory_crypto"]
FORBIDDEN = ["+2h", "2h stress", "plus2", "two_bar", "timestamp + 2h", "feature_available_time_conservative"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def scan() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for root_name in SCAN_DIRS:
        root = REPO / root_name
        if not root.exists():
            continue
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            if path == Path(__file__).resolve():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for term in FORBIDDEN:
                if term in text:
                    rows.append(
                        {
                            "path": str(path.relative_to(REPO)),
                            "forbidden_term": term,
                            "occurrences": text.count(term),
                        }
                    )
    return rows


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    generated_at = utc_now()
    violations = scan()
    manifest = {
        "generated_at": generated_at,
        "decision": "PASS_A7AL0L_FIXED_DELAY_STRESS_ABOLISHED" if not violations else "HOLD_A7AL0L_FIXED_DELAY_STRESS_REFERENCES_REMAIN",
        "scope": SCAN_DIRS,
        "forbidden_terms": FORBIDDEN,
        "violation_count": len(violations),
        "violations": violations,
        "policy": {
            "fixed_delay_stress": "prohibited",
            "primary_execution": "timestamp + 1h / next 1h bar open for 1h bar-close features",
            "required_audit": "field-native latency contract plus wrong-lag controls",
            "fast_microstructure": "must use native 5m/15m/tick/aggTrades timing, not fixed bar delay",
        },
        "authorizes_a7al1_field_family_baseline": not violations,
        "authorizes_a7al2_formula_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    (RUNTIME / "a7al0l_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (RUNTIME / "a7al0l_active_code_forbidden_term_scan.json").write_text(json.dumps(violations, indent=2), encoding="utf-8")

    report = f"""# CRYPTO A7AL-0L Fixed Delay Stress Abolition

Generated: {generated_at}

## Decision

```text
{manifest["decision"]}
```

## Policy

```text
fixed delay stress:
  prohibited

primary 1h bar-close execution:
  timestamp + 1h / next 1h bar open

required timing audit:
  field-native latency contract
  wrong-lag future / stale controls
  no same-bar execution

fast microstructure:
  use native 5m / 15m / tick / aggTrades timing
  do not impose fixed bar delay
```

## Active Code Scan

```json
{json.dumps({"violation_count": len(violations), "violations": violations}, indent=2)}
```

## Authorization

```text
AUTHORIZED:
  A7AL-1 field-family baseline under field-native latency policy

NOT AUTHORIZED:
  fixed delay stress as a promotion gate
  A7AL-2 formula search
  alpha proof
  shadow / paper / live
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
