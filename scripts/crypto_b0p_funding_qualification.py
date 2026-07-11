from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.funding_events import canonicalize_funding_events, funding_event_flags_from_last_time
from alphafactory_crypto.funding_qualification import qualify_production_funding, validate_observation_columns


CONFIG_PATH = REPO / "config" / "crypto_b0p_funding_qualification_v1.json"
RUNTIME = REPO / "runtime" / "a7b0p_funding_qualification_20260711"
REPORT = REPO / "reports" / "CRYPTO_B0P_FUNDING_PRODUCTION_QUALIFICATION_20260711.md"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _write_csv(frame: pd.DataFrame, name: str) -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    frame.to_csv(RUNTIME / name, index=False)


def build() -> dict[str, object]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    manifest_path = Path(config["truth_manifest"])
    panel_path = Path(config["detector_panel"])
    if sha256_file(manifest_path) != config["truth_manifest_sha256"]:
        raise RuntimeError("funding truth manifest SHA mismatch")
    if sha256_file(panel_path) != config["detector_panel_sha256"]:
        raise RuntimeError("pre-forward detector panel SHA mismatch")

    truth_columns = list(config["truth_allowed_columns"])
    panel_columns = list(config["detector_allowed_columns"])
    validate_observation_columns(truth_columns, set(truth_columns))
    validate_observation_columns(panel_columns, set(panel_columns))

    manifest = pd.read_csv(manifest_path)
    expected_symbols = set(config["expected_symbols"])
    manifest = manifest[manifest["symbol"].astype(str).isin(expected_symbols)].copy()
    source_rows: list[dict[str, object]] = []
    truth_parts: list[pd.DataFrame] = []
    for row in manifest.sort_values("symbol").itertuples(index=False):
        source_path = Path(str(row.local_path))
        actual_sha = sha256_file(source_path)
        sha_ok = actual_sha.lower() == str(row.sha256).lower()
        raw = pd.read_csv(source_path, usecols=truth_columns)
        row_count_ok = len(raw) == int(row.row_count)
        symbol_ok = set(raw["symbol"].astype(str)) == {str(row.symbol)}
        raw["source_record_id"] = [f"{source_path.name}:{index}" for index in range(len(raw))]
        truth_parts.append(raw)
        source_rows.append(
            {
                "symbol": row.symbol,
                "source_path": source_path.as_posix(),
                "expected_sha256": str(row.sha256).upper(),
                "actual_sha256": actual_sha,
                "sha_verified": sha_ok,
                "expected_rows": int(row.row_count),
                "actual_rows": len(raw),
                "row_count_verified": row_count_ok,
                "symbol_verified": symbol_ok,
                "manifest_status": row.status,
                "declared_interval": row.interval,
            }
        )
    source_verification = pd.DataFrame(source_rows)
    source_integrity_verified = bool(
        len(source_verification) == len(expected_symbols)
        and set(source_verification["symbol"].astype(str)) == expected_symbols
        and source_verification[["sha_verified", "row_count_verified", "symbol_verified"]].all(axis=None)
    )

    panel = pd.read_parquet(panel_path, columns=panel_columns)
    cutoff = pd.Timestamp(config["qualification_cutoff_utc"])
    panel["timestamp"] = pd.to_datetime(panel["timestamp"], utc=True)
    panel = panel[panel["timestamp"] <= cutoff].copy()
    panel = panel.rename(
        columns={"fundingTime_ms": "last_funding_time", "latest_known_funding_rate": "last_funding_rate"}
    )
    flags = funding_event_flags_from_last_time(panel, last_funding_time_col="last_funding_time")
    detected_raw = panel.loc[flags].copy()
    detected = canonicalize_funding_events(
        detected_raw,
        event_time_col="last_funding_time",
        rate_col="last_funding_rate",
        observable_time_col="bar_close_timestamp",
        venue=config["venue"],
    )

    truth_raw = pd.concat(truth_parts, ignore_index=True)
    truth_times = pd.to_datetime(truth_raw["fundingTime"], unit="ms", utc=True)
    truth_raw = truth_raw.loc[truth_times <= cutoff].copy()
    truth = canonicalize_funding_events(
        truth_raw,
        event_time_col="fundingTime",
        rate_col="fundingRate",
        source_record_col="source_record_id",
        venue=config["venue"],
    )
    qualification = qualify_production_funding(
        truth,
        detected,
        source_integrity_verified=source_integrity_verified,
        tolerance=config["matching_tolerance"],
    )
    summary: dict[str, object] = {
        **qualification.summary,
        "qualification_id": config["qualification_id"],
        "qualification_cutoff_utc": config["qualification_cutoff_utc"],
        "truth_manifest_sha256": config["truth_manifest_sha256"],
        "detector_panel_sha256": config["detector_panel_sha256"],
        "truth_columns_read": truth_columns,
        "detector_columns_read": panel_columns,
        "search_started": False,
        "forward_performance_read": False,
        "state_event_reward_connected": False,
        "memory_or_scheduler_updated": False,
    }

    RUNTIME.mkdir(parents=True, exist_ok=True)
    for obsolete in ("detected_funding_events.csv", "funding_event_matches.csv"):
        (RUNTIME / obsolete).unlink(missing_ok=True)
    (RUNTIME / "funding_qualification_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    _write_csv(source_verification, "funding_source_verification.csv")
    _write_csv(
        truth[["event_id", "venue", "instrument", "funding_time_utc", "observable_time_utc", "funding_rate", "payer_side", "receiver_side", "source_record_id"]],
        "approved_funding_truth_set.csv",
    )
    match_sample = qualification.matches.copy()
    if not match_sample.empty:
        match_sample["month_utc"] = match_sample["expected_time_utc"].dt.strftime("%Y-%m")
        match_sample = match_sample.groupby(["venue", "instrument", "month_utc"], as_index=False).head(1)
    _write_csv(match_sample, "funding_event_match_audit_sample.csv")
    _write_csv(qualification.misses, "funding_event_misses.csv")
    _write_csv(qualification.false_positives, "funding_event_false_positives.csv")
    _write_csv(qualification.symbol_month_coverage, "funding_symbol_month_coverage.csv")
    _write_csv(qualification.schedule_intervals, "funding_schedule_intervals.csv")
    REPORT.write_text(
        "\n".join(
            [
                "# Crypto B0P Funding Production Qualification",
                "",
                f"Decision: `{summary['decision']}`",
                "",
                f"- truth/detected/matched: `{summary['expected_events']}` / `{summary['detected_events']}` / `{summary['matched_events']}`",
                f"- recall / precision: `{summary['recall']}` / `{summary['precision']}`",
                f"- misses / false positives / duplicates: `{summary['missed_events']}` / `{summary['false_positive_events']}` / `{summary['detected_duplicate_rows']}`",
                f"- maximum timestamp error: `{summary['timing_error_abs_seconds_max']} seconds`",
                f"- symbol coverage: `{summary['fully_covered_symbols']}/{summary['truth_symbols']}`",
                f"- symbol-month coverage: `{summary['fully_covered_symbol_month_groups']}/{summary['symbol_month_groups']}`",
                f"- funding-rate mismatches: `{summary['rate_mismatch_events']}`",
                f"- cash-flow sign semantics: `{summary['cashflow_semantics_pass']}`",
                f"- non-8h schedule transitions: `{summary['non_8h_schedule_transitions']}`",
                "",
                "Only event identity, event time, funding rate, and observation time were read. Price returns and Alpha reward were not read or computed.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
