from __future__ import annotations

import hashlib
import csv
import json
import sys
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.funding_events import canonicalize_funding_events, funding_event_flags_from_last_time
from alphafactory_crypto.funding_qualification import (
    DETECTOR_QUALIFICATION_COLUMNS,
    TRUTH_QUALIFICATION_COLUMNS,
    hourly_bar_close_observable_time,
    qualify_production_funding,
    validate_observation_columns,
)


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


def _read_truth_prefix(source_path: Path, *, symbol: str, cutoff_ms: int) -> tuple[pd.DataFrame, dict[str, object]]:
    rows: list[dict[str, object]] = []
    prefix_digest = hashlib.sha256()
    previous_time = -1
    with source_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not set(TRUTH_QUALIFICATION_COLUMNS).issubset(reader.fieldnames or []):
            raise RuntimeError(f"truth source missing approved columns: {source_path}")
        for source_index, row in enumerate(reader):
            event_time_ms = int(row["fundingTime"])
            if event_time_ms < previous_time:
                raise RuntimeError(f"truth source is not time ordered: {source_path}")
            previous_time = event_time_ms
            if event_time_ms > cutoff_ms:
                break
            selected = {
                "symbol": row["symbol"],
                "fundingTime": event_time_ms,
                "fundingRate": row["fundingRate"],
                "source_record_id": f"{source_path.name}:{source_index}",
            }
            if selected["symbol"] != symbol:
                raise RuntimeError(f"truth source symbol mismatch: {source_path}")
            prefix_digest.update(
                f"{selected['symbol']}|{selected['fundingTime']}|{selected['fundingRate']}\n".encode("utf-8")
            )
            rows.append(selected)
    frame = pd.DataFrame(rows)
    metadata = {
        "qualified_prefix_sha256": prefix_digest.hexdigest().upper(),
        "qualified_rows": len(frame),
        "first_event_utc": pd.to_datetime(frame["fundingTime"].min(), unit="ms", utc=True),
        "last_event_utc": pd.to_datetime(frame["fundingTime"].max(), unit="ms", utc=True),
    }
    return frame, metadata


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
    validate_observation_columns(truth_columns, set(TRUTH_QUALIFICATION_COLUMNS))
    validate_observation_columns(panel_columns, set(DETECTOR_QUALIFICATION_COLUMNS))
    if set(truth_columns) != set(TRUTH_QUALIFICATION_COLUMNS):
        raise RuntimeError("funding truth qualification columns must match the code-owned allowlist")
    if set(panel_columns) != set(DETECTOR_QUALIFICATION_COLUMNS):
        raise RuntimeError("detector qualification columns must match the code-owned allowlist")
    if config.get("price_or_return_columns_allowed") is not False:
        raise RuntimeError("price or return columns must remain prohibited")
    if config.get("alpha_reward_allowed") is not False or config.get("candidate_feedback_permission") != "NONE":
        raise RuntimeError("reward and candidate feedback must remain prohibited")

    manifest = pd.read_csv(manifest_path)
    expected_symbols = set(config["expected_symbols"])
    manifest = manifest[manifest["symbol"].astype(str).isin(expected_symbols)].copy()
    cutoff = pd.Timestamp(config["qualification_cutoff_utc"])
    cutoff_ms = int(cutoff.timestamp() * 1000)
    qualification_start = pd.Timestamp(config["qualification_start_utc"])
    required_last_event = pd.Timestamp(config["required_last_event_not_before_utc"])
    source_rows: list[dict[str, object]] = []
    truth_parts: list[pd.DataFrame] = []
    for row in manifest.sort_values("symbol").itertuples(index=False):
        source_path = Path(str(row.local_path))
        raw, prefix = _read_truth_prefix(source_path, symbol=str(row.symbol), cutoff_ms=cutoff_ms)
        file_size_verified = source_path.stat().st_size == int(row.file_size)
        qualified_rows_verified = len(raw) == int(config["expected_qualified_rows_per_symbol"])
        time_coverage_verified = (
            prefix["first_event_utc"] <= qualification_start and prefix["last_event_utc"] >= required_last_event
        )
        truth_parts.append(raw)
        source_rows.append(
            {
                "symbol": row.symbol,
                "source_path": source_path.as_posix(),
                "manifest_declared_full_source_sha256": str(row.sha256).upper(),
                "full_source_sha_recomputed": False,
                "qualified_prefix_sha256": prefix["qualified_prefix_sha256"],
                "manifest_file_size": int(row.file_size),
                "actual_file_size": source_path.stat().st_size,
                "file_size_verified": file_size_verified,
                "qualified_rows": prefix["qualified_rows"],
                "qualified_rows_verified": qualified_rows_verified,
                "first_event_utc": prefix["first_event_utc"],
                "last_event_utc": prefix["last_event_utc"],
                "time_coverage_verified": time_coverage_verified,
                "symbol_verified": True,
                "manifest_status": row.status,
                "declared_interval": row.interval,
            }
        )
    source_verification = pd.DataFrame(source_rows)
    source_integrity_verified = bool(
        len(source_verification) == len(expected_symbols)
        and set(source_verification["symbol"].astype(str)) == expected_symbols
        and source_verification[
            ["file_size_verified", "qualified_rows_verified", "time_coverage_verified", "symbol_verified"]
        ].all(axis=None)
        and source_verification["manifest_status"].astype(str).eq("downloaded").all()
        and source_verification["declared_interval"].astype(str).eq("8h").all()
    )

    panel = pd.read_parquet(panel_path, columns=panel_columns)
    panel["timestamp"] = pd.to_datetime(panel["timestamp"], utc=True)
    panel_time_boundary_verified = bool(
        panel["timestamp"].min() <= qualification_start and panel["timestamp"].max() == cutoff
    )
    source_integrity_verified = source_integrity_verified and panel_time_boundary_verified
    panel = panel[panel["timestamp"] <= cutoff].copy()
    panel = panel.rename(
        columns={"fundingTime_ms": "last_funding_time", "latest_known_funding_rate": "last_funding_rate"}
    )
    flags = funding_event_flags_from_last_time(panel, last_funding_time_col="last_funding_time")
    detected_raw = panel.loc[flags].copy()
    detector_source_duplicate_rows = int(
        detected_raw.duplicated(["symbol", "last_funding_time"], keep=False).sum()
    )
    detected = canonicalize_funding_events(
        detected_raw,
        event_time_col="last_funding_time",
        rate_col="last_funding_rate",
        observable_time_col="bar_close_timestamp",
        venue=config["venue"],
    )

    truth_raw = pd.concat(truth_parts, ignore_index=True)
    truth_source_duplicate_rows = int(truth_raw.duplicated(["symbol", "fundingTime"], keep=False).sum())
    truth_event_times = pd.to_datetime(truth_raw["fundingTime"], unit="ms", utc=True)
    truth_raw["expected_observable_time"] = hourly_bar_close_observable_time(truth_event_times)
    truth = canonicalize_funding_events(
        truth_raw,
        event_time_col="fundingTime",
        rate_col="fundingRate",
        observable_time_col="expected_observable_time",
        source_record_col="source_record_id",
        venue=config["venue"],
    )
    qualification = qualify_production_funding(
        truth,
        detected,
        source_integrity_verified=source_integrity_verified,
        truth_source_duplicate_rows=truth_source_duplicate_rows,
        detector_source_duplicate_rows=detector_source_duplicate_rows,
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
        "truth_independence": "UPSTREAM_RAW_EVENT_LOG_SEPARATE_FROM_DERIVED_HOURLY_DETECTOR_PANEL",
        "truth_and_detector_artifact_same_path": manifest_path.resolve() == panel_path.resolve(),
        "panel_time_boundary_verified": panel_time_boundary_verified,
        "truth_rows_match_contract": len(truth) == int(config["expected_qualified_events"]),
        "search_started": False,
        "forward_performance_read": False,
        "state_event_reward_connected": False,
        "memory_or_scheduler_updated": False,
        "cem_ucb_mcts_updated": False,
        "a7mem_updated": False,
        "candidate_selection_performed": False,
        "b1_lane_integration": False,
        "large_search_authorized": False,
        "alpha_ready": False,
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
                f"- maximum observable-time error: `{summary['observable_time_error_abs_seconds_max']} seconds`",
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
