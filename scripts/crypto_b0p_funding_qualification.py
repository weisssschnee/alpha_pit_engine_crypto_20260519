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
from alphafactory_crypto.funding_qualification import (
    DETECTOR_QUALIFICATION_COLUMNS,
    TRUTH_QUALIFICATION_COLUMNS,
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


def sha256_normalized_text_file(path: Path) -> str:
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest().upper()


def _write_csv(frame: pd.DataFrame, name: str) -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    frame.to_csv(RUNTIME / name, index=False)


def build() -> dict[str, object]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    manifest_path = Path(config["truth_manifest"])
    truth_set_path = REPO / config["approved_truth_set"]
    panel_path = Path(config["detector_panel"])
    if sha256_file(manifest_path) != config["truth_manifest_sha256"]:
        raise RuntimeError("funding truth manifest SHA mismatch")
    if sha256_file(panel_path) != config["detector_panel_sha256"]:
        raise RuntimeError("pre-forward detector panel SHA mismatch")
    truth_set_sha = sha256_normalized_text_file(truth_set_path)
    if truth_set_sha != config["approved_truth_set_normalized_sha256"]:
        raise RuntimeError("approved pre-cutoff funding truth-set SHA mismatch")

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

    expected_symbols = set(config["expected_symbols"])
    cutoff = pd.Timestamp(config["qualification_cutoff_utc"])
    qualification_start = pd.Timestamp(config["qualification_start_utc"])
    required_last_event = pd.Timestamp(config["required_last_event_not_before_utc"])
    truth_raw = pd.read_csv(truth_set_path, usecols=truth_columns)
    truth_raw["funding_time_utc"] = pd.to_datetime(truth_raw["funding_time_utc"], utc=True, format="mixed")
    truth_raw["observable_time_utc"] = pd.to_datetime(
        truth_raw["observable_time_utc"], utc=True, format="mixed"
    )
    truth_columns_verified = set(truth_raw.columns) == set(TRUTH_QUALIFICATION_COLUMNS)
    truth_symbols_verified = set(truth_raw["instrument"].astype(str)) == expected_symbols
    truth_rows_verified = len(truth_raw) == int(config["expected_qualified_events"])
    truth_time_coverage_verified = bool(
        truth_raw["funding_time_utc"].min() <= qualification_start
        and truth_raw["funding_time_utc"].max() >= required_last_event
        and truth_raw["funding_time_utc"].max() <= cutoff
    )
    source_verification = pd.DataFrame(
        [
            {
                "source_role": "APPROVED_PHYSICAL_PRE_CUTOFF_EVENT_TRUTH_SET",
                "source_path": config["approved_truth_set"],
                "expected_normalized_sha256": config["approved_truth_set_normalized_sha256"],
                "actual_sha256": truth_set_sha,
                "sha_verified": truth_set_sha == config["approved_truth_set_normalized_sha256"],
                "columns_verified": truth_columns_verified,
                "rows_verified": truth_rows_verified,
                "symbols_verified": truth_symbols_verified,
                "time_coverage_verified": truth_time_coverage_verified,
                "first_event_utc": truth_raw["funding_time_utc"].min(),
                "last_event_utc": truth_raw["funding_time_utc"].max(),
                "upstream_manifest": config["truth_manifest"],
                "upstream_manifest_sha256": config["truth_manifest_sha256"],
            }
        ]
    )
    source_integrity_verified = bool(
        source_verification[["sha_verified", "columns_verified", "rows_verified", "symbols_verified", "time_coverage_verified"]].all(axis=None)
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

    truth_source_duplicate_rows = int(
        truth_raw.duplicated(["venue", "instrument", "funding_time_utc"], keep=False).sum()
    )
    truth = canonicalize_funding_events(
        truth_raw,
        instrument_col="instrument",
        event_time_col="funding_time_utc",
        rate_col="funding_rate",
        observable_time_col="observable_time_utc",
        source_record_col="source_record_id",
        venue=config["venue"],
    )
    truth_event_id_verified = set(truth["event_id"].astype(str)) == set(truth_raw["event_id"].astype(str))
    source_integrity_verified = source_integrity_verified and truth_event_id_verified
    source_verification.loc[0, "event_id_verified"] = truth_event_id_verified
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
        "approved_truth_set_normalized_sha256": config["approved_truth_set_normalized_sha256"],
        "detector_panel_sha256": config["detector_panel_sha256"],
        "truth_columns_read": truth_columns,
        "detector_columns_read": panel_columns,
        "truth_independence": "APPROVED_PHYSICAL_PRE_CUTOFF_EVENT_TRUTH_SET_SEPARATE_FROM_DERIVED_HOURLY_DETECTOR_PANEL",
        "truth_and_detector_artifact_same_path": truth_set_path.resolve() == panel_path.resolve(),
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
