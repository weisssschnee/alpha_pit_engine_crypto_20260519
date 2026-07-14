from __future__ import annotations

import argparse
import csv
import functools
import hashlib
import io
import json
import subprocess
import sys
import types
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CLOSURE_REF = "crypto-frontier-provenance-closure-20260714"
EXPECTED_CLOSURE_SHA = "4726795f61052470d56e2d1475e4f6da9d262943"
MAIN_BASELINE_SHA = "09ac397c61b0b462497e9a8c0ea84981cc6a93f9"
OUT = REPO / "runtime/crypto_latest_evidence_independent_audit_20260714"
ALGORITHM_CSV = OUT / "CRYPTO_ALGORITHM_OBJECTIVE_LINEAGE.csv"
PRIMITIVE_CSV = OUT / "CRYPTO_PRIMITIVE_EQUIVALENCE_MATRIX.csv"
PROXY_REPORT = REPO / "reports/CRYPTO_PROXY_TO_FINAL_OBJECTIVE_AUDIT.md"
MAPPING_REPORT = REPO / "reports/CRYPTO_PORTFOLIO_MAPPING_AND_COST_ATTRIBUTION.md"

SOURCE_PATHS = {
    "temporal": "alphafactory_crypto/temporal_program.py",
    "b1s": "alphafactory_crypto/b1s_canary.py",
    "nextgen": "alphafactory_crypto/nextgen_epoch.py",
    "revision": "alphafactory_crypto/search_revision.py",
    "b1s_runner": "scripts/crypto_b1s_canary.py",
    "epoch0_runner": "scripts/crypto_nextgen_epoch0.py",
    "epoch1_runner": "scripts/crypto_nextgen_epoch1.py",
    "epoch1r_runner": "scripts/crypto_nextgen_epoch1r.py",
    "epoch2_runner": "scripts/crypto_epoch2.py",
    "b1s_config": "config/crypto_b1s_canary_v1.json",
    "epoch0_config": "config/crypto_nextgen_epoch0_v1.json",
    "epoch1_config": "config/crypto_nextgen_epoch1_v1.json",
    "epoch2_config": "config/crypto_epoch2_v1.json",
    "epoch2b_report": "runtime/epoch2b_audit_20260712/EPOCH2B_ECONOMIC_BOTTLENECK_REPORT.md",
    "epoch2b_decision": "runtime/epoch2b_audit_20260712/economic_bottleneck_decision.json",
}

PRIMITIVES = (
    "Delta",
    "Slope",
    "Acceleration",
    "Persistence",
    "Duration",
    "StateAge",
    "TimeSince",
    "FirstHit",
    "LastHit",
    "Transition",
    "PathShape",
    "EventWindow",
    "MultiScaleRelation",
)


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=REPO, text=True, encoding="utf-8", errors="strict",
        capture_output=True, check=True,
    )
    return result.stdout.strip()


def closure_sha() -> str:
    value = git("rev-parse", f"{CLOSURE_REF}^{{commit}}")
    if value != EXPECTED_CLOSURE_SHA:
        raise RuntimeError(f"closure ref drift: {value}")
    return value


@functools.lru_cache(maxsize=None)
def blob(path: str) -> str:
    return git("show", f"{CLOSURE_REF}:{path}") + "\n"


@functools.lru_cache(maxsize=None)
def blob_identity(path: str) -> str:
    object_id = git("rev-parse", f"{CLOSURE_REF}:{path}")
    digest = hashlib.sha256(blob(path).encode("utf-8")).hexdigest().upper()
    return f"git_blob={object_id};sha256={digest}"


def source_evidence(key: str, symbol: str) -> str:
    path = SOURCE_PATHS[key]
    return f"{CLOSURE_REF}:{path}#{symbol};{blob_identity(path)}"


@functools.lru_cache(maxsize=1)
def _install_runtime_modules() -> tuple[types.ModuleType, types.ModuleType, types.ModuleType]:
    """Load accepted-closure pure semantics without checking out or reading market data."""
    identity = types.ModuleType("alphafactory_crypto.identity_registry")
    identity.activation_identity = lambda *args, **kwargs: "synthetic-activation"
    behaviour = types.ModuleType("alphafactory_crypto.signal_behaviour")
    behaviour.canonical_weight_hash = lambda values: hashlib.sha256(
        np.asarray(values, dtype=float).tobytes()
    ).hexdigest()
    sys.modules[identity.__name__] = identity
    sys.modules[behaviour.__name__] = behaviour

    b1s = types.ModuleType("alphafactory_crypto.b1s_canary")
    b1s.__file__ = f"{CLOSURE_REF}:{SOURCE_PATHS['b1s']}"
    sys.modules[b1s.__name__] = b1s
    exec(compile(blob(SOURCE_PATHS["b1s"]), b1s.__file__, "exec"), b1s.__dict__)

    nextgen = types.ModuleType("alphafactory_crypto.nextgen_epoch")
    nextgen.__file__ = f"{CLOSURE_REF}:{SOURCE_PATHS['nextgen']}"
    sys.modules[nextgen.__name__] = nextgen
    exec(compile(blob(SOURCE_PATHS["nextgen"]), nextgen.__file__, "exec"), nextgen.__dict__)

    temporal = types.ModuleType("alphafactory_crypto.temporal_program")
    temporal.__file__ = f"{CLOSURE_REF}:{SOURCE_PATHS['temporal']}"
    sys.modules[temporal.__name__] = temporal
    exec(compile(blob(SOURCE_PATHS["temporal"]), temporal.__file__, "exec"), temporal.__dict__)
    return temporal, b1s, nextgen


def _synthetic_values() -> tuple[np.ndarray, pd.DatetimeIndex]:
    coordinates = np.arange(96, dtype=float)
    rows = []
    for asset in range(7):
        values = (
            0.18 * (asset + 1) * np.sin((coordinates + asset) / (3.0 + asset))
            + (asset - 3) * 0.006 * coordinates
            + 0.11 * ((coordinates.astype(int) // (5 + asset)) % 3)
            - 0.10
        )
        rows.append(values)
    return np.vstack(rows), pd.date_range("2020-01-01", periods=96, freq="h", tz="UTC")


def _temporal_matrix(
    module: types.ModuleType,
    primitive: str,
    values: np.ndarray,
    times: pd.DatetimeIndex,
    *,
    multiscale_short: int = 4,
    multiscale_long: int = 8,
) -> np.ndarray:
    params: dict[str, Any] = {"periods": 4, "threshold": 0.0}
    if primitive == "MultiScaleRelation":
        params = {
            "periods": 4,
            "short_periods": multiscale_short,
            "long_periods": multiscale_long,
            "threshold": 0.0,
        }
    output = []
    metadata = pd.Series(times, index=times)
    for row in values:
        observation = module.ObservationVector(pd.Series(row, index=times), metadata, metadata)
        program = module.TypedProgram(primitive, "synthetic:non_market", params)
        output.append(module.evaluate(program, observation).to_numpy(dtype=float))
    return np.vstack(output)


def _rank_array(values: np.ndarray) -> np.ndarray:
    return pd.DataFrame(values).rank(axis=0, method="average").to_numpy(dtype=float)


def _equal(left: np.ndarray, right: np.ndarray, *, mask_sensitive: bool = True) -> bool:
    left_finite, right_finite = np.isfinite(left), np.isfinite(right)
    if mask_sensitive and not np.array_equal(left_finite, right_finite):
        return False
    common = left_finite & right_finite
    return bool(common.any() and np.allclose(left[common], right[common], rtol=1e-10, atol=1e-12))


def _equivalence(
    left: np.ndarray,
    right: np.ndarray,
    b1s: types.ModuleType,
    timestamps: pd.DatetimeIndex,
) -> dict[str, str]:
    shared_equal = _equal(left, right, mask_sensitive=False)
    raw = "EQUIVALENT" if _equal(left, right) else ("EQUIVALENT_ON_SHARED_COORDINATES" if shared_equal else "NOT_EQUIVALENT")
    ranks_left, ranks_right = _rank_array(left), _rank_array(right)
    rank = "EQUIVALENT" if _equal(ranks_left, ranks_right) else ("EQUIVALENT_ON_SHARED_COORDINATES" if _equal(ranks_left, ranks_right, mask_sensitive=False) else "NOT_EQUIVALENT")
    weights_left, weights_right = b1s.rank_weights(left), b1s.rank_weights(right)
    weight = "EQUIVALENT" if np.allclose(weights_left, weights_right, rtol=1e-10, atol=1e-12) else "NOT_EQUIVALENT"
    active_left, active_right = np.abs(weights_left) > 1e-12, np.abs(weights_right) > 1e-12
    activation = "EQUIVALENT" if np.array_equal(active_left, active_right) else "NOT_EQUIVALENT"
    sign_left, sign_right = np.sign(weights_left), np.sign(weights_right)
    weight_sign = "EQUIVALENT" if np.array_equal(sign_left, sign_right) else "NOT_EQUIVALENT"
    left_cluster = b1s.behaviour_cluster_identity(weights_left, timestamps)
    right_cluster = b1s.behaviour_cluster_identity(weights_right, timestamps)
    actual_cluster = "EQUIVALENT" if left_cluster == right_cluster else "NOT_EQUIVALENT"
    return {
        "raw_numeric_equivalence": raw,
        "rank_equivalence": rank,
        "portfolio_weight_equivalence": weight,
        "activation_equivalence": activation,
        "weight_sign_equivalence": weight_sign,
        "actual_behaviour_cluster_equivalence": actual_cluster,
        "behaviour_equivalence": actual_cluster,
        "left_behaviour_cluster_id": left_cluster,
        "right_behaviour_cluster_id": right_cluster,
        "shared_finite_coordinates": str(int((np.isfinite(left) & np.isfinite(right)).sum())),
    }


def primitive_rows() -> list[dict[str, str]]:
    temporal, b1s, nextgen = _install_runtime_modules()
    values, times = _synthetic_values()
    rows: list[dict[str, str]] = []
    provenance = {
        "repo_ref": CLOSURE_REF,
        "commit_sha": EXPECTED_CLOSURE_SHA,
        "run_id": "NOT_APPLICABLE_STATIC_SEMANTIC_AUDIT",
        "data_release": "NO_MARKET_DATA_READ",
        "evidence_role": "STATIC_PRIMITIVE_SEMANTIC_QUALIFICATION",
        "superseded": "false",
        "authoritative_now": "true",
    }
    notes = {
        "Delta": "Both use x[t]-x[t-window].",
        "Slope": "temporal_program uses rolling OLS slope over window observations; nextgen/B1S use endpoint delta divided by window.",
        "Acceleration": "Both apply the same windowed difference twice.",
        "Persistence": "nextgen thresholds a rolling z-score; temporal/B1S threshold the raw level. B1S differs only in warm-up minimum periods from temporal.",
        "Duration": "nextgen duration is run length of a z-score state; temporal duration is run length of a raw-threshold state.",
        "StateAge": "temporal aliases StateAge to active-state duration; nextgen aliases it to age since the last rising transition, including inactive periods.",
        "TimeSince": "temporal is time since the last raw-threshold hit; nextgen is age since a z-score rising transition.",
        "FirstHit": "Both are rising transitions in form, but temporal uses raw threshold state and nextgen uses rolling-z state.",
        "LastHit": "temporal returns the absolute position of the last raw-threshold hit; nextgen returns age since a z-score rising transition.",
        "Transition": "temporal is raw-threshold rising transition; nextgen is z-score-state rising transition; B1S detects any numeric value change.",
        "PathShape": "temporal compares last-third and first-third path means; nextgen aliases PathShape to short-minus-long rolling means.",
        "EventWindow": "temporal counts raw-threshold-positive observations; nextgen averages z-score rising transitions; B1S averages any-value changes.",
        "MultiScaleRelation": "short-minus-long rolling means agree after full maturity; nextgen/B1S emit earlier because of half-window minimum periods.",
    }
    classifications = {
        "Delta": "NO_SEMANTIC_DRIFT_DETECTED",
        "Slope": "SEMANTIC_DRIFT_CONFIRMED",
        "Acceleration": "NO_SEMANTIC_DRIFT_DETECTED",
        "Persistence": "SEMANTIC_DRIFT_CONFIRMED",
        "Duration": "SEMANTIC_DRIFT_CONFIRMED",
        "StateAge": "SEMANTIC_DRIFT_CONFIRMED_AND_ALIAS_COLLAPSE",
        "TimeSince": "SEMANTIC_DRIFT_CONFIRMED_AND_ALIAS_COLLAPSE",
        "FirstHit": "SEMANTIC_DRIFT_CONFIRMED_AND_ALIAS_COLLAPSE",
        "LastHit": "SEMANTIC_DRIFT_CONFIRMED_AND_ALIAS_COLLAPSE",
        "Transition": "SEMANTIC_DRIFT_CONFIRMED_AND_ALIAS_COLLAPSE",
        "PathShape": "SEMANTIC_DRIFT_CONFIRMED_AND_PSEUDO_DIVERSITY",
        "EventWindow": "SEMANTIC_DRIFT_CONFIRMED",
        "MultiScaleRelation": "WARMUP_SEMANTIC_DRIFT_ONLY",
    }
    b1s_operators = {
        "Delta": ("delta", 4),
        "Slope": ("slope", 4),
        "Acceleration": ("acceleration", 4),
        "Persistence": ("persistence", 4),
        "StateAge": ("event_age", 4),
        "TimeSince": ("event_age", 4),
        "LastHit": ("event_age", 4),
        "Transition": ("transition", 4),
        "EventWindow": ("event_window", 4),
        "MultiScaleRelation": ("multiscale", 8),
    }
    b1s_event_age_notes = {
        "StateAge": "Cross-name comparison: B1S event_age is age since any numeric value change; temporal StateAge is active raw-threshold-state duration.",
        "TimeSince": "Cross-name comparison: B1S event_age is age since any numeric value change; temporal TimeSince is time since the last raw-threshold hit.",
        "LastHit": "Cross-name comparison: B1S event_age is age since any numeric value change; temporal LastHit is the absolute position of the last raw-threshold hit.",
    }
    temporal_aliases = {
        "Duration": "TEMPORAL_DURATION_STATEAGE",
        "StateAge": "TEMPORAL_DURATION_STATEAGE",
        "Transition": "TEMPORAL_TRANSITION_FIRSTHIT",
        "FirstHit": "TEMPORAL_TRANSITION_FIRSTHIT",
    }
    nextgen_aliases = {
        "StateAge": "NEXTGEN_STATEAGE_TIMESINCE_LASTHIT",
        "TimeSince": "NEXTGEN_STATEAGE_TIMESINCE_LASTHIT",
        "LastHit": "NEXTGEN_STATEAGE_TIMESINCE_LASTHIT",
        "Transition": "NEXTGEN_TRANSITION_FIRSTHIT",
        "FirstHit": "NEXTGEN_TRANSITION_FIRSTHIT",
        "PathShape": "NEXTGEN_PATHSHAPE_MULTISCALERELATION",
        "MultiScaleRelation": "NEXTGEN_PATHSHAPE_MULTISCALERELATION",
    }
    for primitive in PRIMITIVES:
        temporal_value = _temporal_matrix(temporal, primitive, values, times)
        nextgen_value = nextgen._primitive(values, primitive, 4, 8, 0.0)
        rows.append({
            **provenance,
            "comparison": "temporal_program_vs_nextgen_epoch",
            "primitive": primitive,
            "left_implementation_status": "IMPLEMENTED",
            "right_implementation_status": "IMPLEMENTED",
            "left_operator": primitive,
            "right_operator": primitive,
            "left_code_alias_group": temporal_aliases.get(primitive, "NONE"),
            "right_code_alias_group": nextgen_aliases.get(primitive, "NONE"),
            "code_semantic_relation": (
                "EXACT_IMPLEMENTATION_EQUIVALENCE"
                if classifications[primitive] == "NO_SEMANTIC_DRIFT_DETECTED"
                else "CONDITIONAL_MATURE_COORDINATE_EQUIVALENCE"
                if classifications[primitive] == "WARMUP_SEMANTIC_DRIFT_ONLY"
                else "CODE_SEMANTIC_MISMATCH"
            ),
            **_equivalence(temporal_value, nextgen_value, b1s, times),
            "classification": classifications[primitive],
            "synthetic_case_id": "DETERMINISTIC_NON_MARKET_PATH_V1",
            "evidence_paths": f"{source_evidence('temporal', 'evaluate')}|{source_evidence('nextgen', '_primitive')}",
            "notes": notes[primitive],
        })

        if primitive not in b1s_operators:
            nearest = {"FirstHit": "transition"}.get(primitive, "")
            rows.append({
                **provenance,
                "comparison": "temporal_program_vs_b1s_canary",
                "primitive": primitive,
                "left_implementation_status": "IMPLEMENTED",
                "right_implementation_status": "NOT_IMPLEMENTED",
                "left_operator": primitive,
                "right_operator": nearest,
                "left_code_alias_group": temporal_aliases.get(primitive, "NONE"),
                "right_code_alias_group": "NONE",
                "code_semantic_relation": "NOT_IMPLEMENTED",
                "raw_numeric_equivalence": "NOT_TESTED_NOT_IMPLEMENTED",
                "rank_equivalence": "NOT_TESTED_NOT_IMPLEMENTED",
                "portfolio_weight_equivalence": "NOT_TESTED_NOT_IMPLEMENTED",
                "activation_equivalence": "NOT_TESTED_NOT_IMPLEMENTED",
                "weight_sign_equivalence": "NOT_TESTED_NOT_IMPLEMENTED",
                "actual_behaviour_cluster_equivalence": "NOT_TESTED_NOT_IMPLEMENTED",
                "behaviour_equivalence": "NOT_TESTED_NOT_IMPLEMENTED",
                "left_behaviour_cluster_id": "NOT_TESTED_NOT_IMPLEMENTED",
                "right_behaviour_cluster_id": "NOT_TESTED_NOT_IMPLEMENTED",
                "shared_finite_coordinates": "0",
                "classification": "NOT_IMPLEMENTED",
                "synthetic_case_id": "DETERMINISTIC_NON_MARKET_PATH_V1",
                "evidence_paths": f"{source_evidence('temporal', 'evaluate')}|{source_evidence('b1s', 'LANE_RECIPES/materialize')}",
                "notes": f"No typed B1S operator implements {primitive}. Nearest name, if any, is {nearest or 'none'} and is not treated as recovery.",
            })
            continue
        operator, window = b1s_operators[primitive]
        temporal_b1s_value = temporal_value
        if primitive == "MultiScaleRelation":
            # B1S encodes short=max(2, window//4), while nextgen ProgramSpec carries
            # the explicit short `window`. Compare each implementation at matching parameters.
            temporal_b1s_value = _temporal_matrix(
                temporal, primitive, values, times, multiscale_short=2, multiscale_long=8
            )
        spec = b1s.CandidateSpec(
            "synthetic", "synthetic", "synthetic", 1, 1, "a", "b", operator, window, 1.0,
            "synthetic", "synthetic", "synthetic", "synthetic", "{}",
        )
        panel = b1s.FrozenPanel(
            "synthetic", tuple(f"A{i}" for i in range(values.shape[0])), times,
            {"a": values, "b": np.flipud(values), "funding": np.flipud(values)},
            np.zeros_like(values), "bucket_start_plus_1h", "bucket_close", "SYNTHETIC_ONLY",
        )
        b1s_value = b1s.materialize(spec, panel)
        eq = _equivalence(temporal_b1s_value, b1s_value, b1s, times)
        b1s_class = "NO_SEMANTIC_DRIFT_DETECTED"
        if primitive in {"Slope", "Transition", "EventWindow"}:
            b1s_class = "SEMANTIC_DRIFT_CONFIRMED"
        elif primitive in b1s_event_age_notes:
            b1s_class = "SEMANTIC_DRIFT_CONFIRMED_CROSS_NAME_EVENT_AGE"
        elif primitive in {"Persistence", "MultiScaleRelation"} and eq["raw_numeric_equivalence"] != "EQUIVALENT":
            b1s_class = "WARMUP_SEMANTIC_DRIFT_ONLY"
        rows.append({
            **provenance,
            "comparison": "temporal_program_vs_b1s_canary",
            "primitive": primitive,
            "left_implementation_status": "IMPLEMENTED",
            "right_implementation_status": (
                "IMPLEMENTED_CROSS_NAME_OPERATOR_NOT_TYPED_PRIMITIVE"
                if primitive in b1s_event_age_notes else "IMPLEMENTED"
            ),
            "left_operator": primitive,
            "right_operator": operator,
            "left_code_alias_group": temporal_aliases.get(primitive, "NONE"),
            "right_code_alias_group": "B1S_EVENT_AGE_CROSS_NAME" if primitive in b1s_event_age_notes else "NONE",
            "code_semantic_relation": (
                "EXACT_IMPLEMENTATION_EQUIVALENCE"
                if b1s_class == "NO_SEMANTIC_DRIFT_DETECTED"
                else "CONDITIONAL_MATURE_COORDINATE_EQUIVALENCE"
                if b1s_class == "WARMUP_SEMANTIC_DRIFT_ONLY"
                else "CODE_SEMANTIC_MISMATCH"
            ),
            **eq,
            "classification": b1s_class,
            "synthetic_case_id": "DETERMINISTIC_NON_MARKET_PATH_V1",
            "evidence_paths": f"{source_evidence('temporal', 'evaluate')}|{source_evidence('b1s', 'materialize')}",
            "notes": b1s_event_age_notes.get(primitive, notes[primitive]),
        })
    return rows


ALGORITHMS = ("typed_random", "typed_ast", "cem", "uct_mcts", "evolutionary", "surrogate", "llm_repair", "rx_ucb")


def _algorithm_default(stage: str, algorithm: str) -> dict[str, str]:
    return {
        "repo_ref": CLOSURE_REF,
        "commit_sha": EXPECTED_CLOSURE_SHA,
        "run_id": "",
        "data_release": "",
        "evidence_role": "HISTORICAL_SEARCH_INSTRUMENT_OBJECTIVE_QUALIFICATION",
        "superseded": "false",
        "authoritative_now": "true",
        "stage": stage,
        "algorithm": algorithm,
        "implementation_status": "NOT_IMPLEMENTED",
        "implementation_entrypoint": "",
        "feedback_function": "NONE",
        "feedback_coordinate": "NONE",
        "cost_in_feedback": "NO",
        "benchmark_increment_in_feedback": "NO",
        "uncertainty_in_feedback": "NO",
        "stability_in_feedback": "NO",
        "learnable_parameters": "NONE",
        "nonlearnable_parameters": "field identity;lookback window;target horizon;portfolio mapping",
        "field_identity_learnable": "NO",
        "target_horizon_learnable": "NO_FIXED_TARGET_LABEL",
        "lookback_window_learnable": "NO",
        "portfolio_mapping_learnable": "NO_FIXED_RANK_WEIGHTS",
        "matched_control": "NONE",
        "objective_mismatch_classification": "NOT_APPLICABLE_NOT_IMPLEMENTED",
        "conclusion_scope": "No implementation recovered in the audited closure scope.",
        "cannot_conclude": "Does not prove absence outside the accepted closure or repository.",
        "evidence_paths": "",
    }


def algorithm_rows() -> list[dict[str, str]]:
    stages = {
        "B1S": {
            "run_id": "20260711_b1s_canary_001",
            "data_release": "SHA256:35E1FDEDCE39DEB7A74A62FF84910114D7A10426DFEC2A49DE274B30F7E77AEF",
            "implementation_sha": "39dbd40e6ce7bde3fbaba0067da6a5bfbae797f8",
            "budget": "5120 proposals;64 adaptive feedback queries;635 logical strict evaluations",
            "artifact": "runtime/b1s_canary_20260711/b1s_canary_manifest.json",
        },
        "EPOCH0": {
            "run_id": "20260711_crypto_nextgen_search_epoch0_001",
            "data_release": "SHA256:68150BEACEBB4A92AA4C2C34A93D9E56F1538E2685BF683806FDBCB004B1E875",
            "implementation_sha": "3b608e08f3e95af45a00ea1b24694c600a268f9c",
            "budget": "32768 proposals;2048 adaptive feedback queries;1801 executed logical strict evaluations",
            "artifact": "runtime/nextgen_epoch0_20260711/epoch0_run_manifest.json",
        },
        "EPOCH1R": {
            "run_id": "20260712_crypto_nextgen_epoch1r_001",
            "data_release": "INHERITED_EPOCH0_PANEL_RELEASE_SHA256:68150BEACEBB4A92AA4C2C34A93D9E56F1538E2685BF683806FDBCB004B1E875",
            "implementation_sha": "90a80795d4978497a2a5810ea02a5cdfdd1fac2e",
            "budget": "32768 proposals;2052 strict assignments;unchanged Epoch1 search stream",
            "artifact": "runtime/nextgen_epoch1r_20260712/epoch1r_run_manifest.json",
        },
        "EPOCH2": {
            "run_id": "20260712_crypto_epoch2_001",
            "data_release": "INHERITED_EPOCH0_PANEL_RELEASE_SHA256:68150BEACEBB4A92AA4C2C34A93D9E56F1538E2685BF683806FDBCB004B1E875",
            "implementation_sha": "c31f3497ca18572f3add5cfefc8f33fa41e68632",
            "budget": "49152 proposals;2304 logical strict rows;768 per admission policy",
            "artifact": "runtime/epoch2_20260712/epoch2_run_manifest.json",
        },
    }
    rows: list[dict[str, str]] = []
    for stage, metadata in stages.items():
        for algorithm in ALGORITHMS:
            row = _algorithm_default(stage, algorithm)
            row.update({
                "repo_ref": CLOSURE_REF,
                "closure_commit_sha": EXPECTED_CLOSURE_SHA,
                "implementation_commit_sha": metadata["implementation_sha"],
                "run_id": metadata["run_id"],
                "data_release": metadata["data_release"],
                "data_scope": "FROZEN_DEVELOPMENT_ONLY_EXISTING_ARTIFACT;NO_DATA_READ_BY_THIS_AUDIT",
                "budget": metadata["budget"],
                "runtime_artifact": f"{CLOSURE_REF}:{metadata['artifact']}",
            })
            rows.append(row)

    index = {(row["stage"], row["algorithm"]): row for row in rows}
    b1s_common = {
        "implementation_status": "IMPLEMENTED_LABEL_SHARED_POLICY",
        "implementation_entrypoint": "scripts/crypto_b1s_canary.py#run;alphafactory_crypto/b1s_canary.py#generate_proposals",
        "feedback_function": "proxy_score",
        "feedback_coordinate": "subsampled development coordinates;gross rank-weight portfolio series",
        "learnable_parameters": "one preferred operator shared across algorithm labels",
        "nonlearnable_parameters": "algorithm-specific policy state;field identity;window;coefficient;portfolio mapping",
        "field_identity_learnable": "NO",
        "lookback_window_learnable": "NO_FIXED_BY_ENUMERATION",
        "matched_control": "global_top_k and stratified admission compare selectors, not adaptive algorithm labels",
        "objective_mismatch_classification": "CONFIRMED_PROXY_TO_STRICT_OBJECTIVE_MISMATCH_AND_ALGORITHM_LABEL_DEGENERACY",
        "conclusion_scope": "B1S adaptive labels do not identify separate CEM/UCT/evolutionary capabilities.",
        "cannot_conclude": "Cannot infer those algorithms are ineffective when independently implemented.",
        "evidence_paths": f"{source_evidence('b1s_runner', 'run')}|{source_evidence('b1s', 'proxy_score/strict_evaluate')}",
    }
    index[("B1S", "typed_ast")].update({
        "implementation_status": "IMPLEMENTED_DETERMINISTIC_TYPED_RECIPE_ENUMERATION",
        "implementation_entrypoint": "alphafactory_crypto/b1s_canary.py#generate_proposals",
        "feedback_function": "NONE_FOR_GENERATION;proxy_score_for_global_top_k",
        "feedback_coordinate": "fixed recipe/ordinal;selector uses gross proxy",
        "objective_mismatch_classification": "GENERATOR_NONADAPTIVE_SELECTOR_PROXY_MISMATCH",
        "conclusion_scope": "Typed recipes are reachable; no adaptive learning is implemented for this lane.",
        "cannot_conclude": "Does not qualify typed AST search quality.",
        "evidence_paths": source_evidence("b1s", "generate_proposals/global_top_k"),
    })
    for algorithm in ("cem", "uct_mcts", "evolutionary"):
        index[("B1S", algorithm)].update(b1s_common)

    epoch0_common = {
        "implementation_status": "IMPLEMENTED_ADAPTIVE_POLICY",
        "feedback_function": "signal_record.proxy_score",
        "feedback_coordinate": "subsampled development coordinates;gross rank-weight portfolio risk ratio",
        "cost_in_feedback": "NO",
        "benchmark_increment_in_feedback": "NO",
        "uncertainty_in_feedback": "NO_EXPLICIT_LCB",
        "stability_in_feedback": "NO",
        "portfolio_mapping_learnable": "NO_FIXED_RANK_WEIGHTS",
        "objective_mismatch_classification": "CONFIRMED_GROSS_PROXY_TO_STRICT_MULTI_OBJECTIVE_MISMATCH",
        "conclusion_scope": "Epoch0 can adapt sampling probabilities inside the fixed ProgramSpec grammar, but feedback omits strict cost/benchmark/stability/IC axes.",
        "cannot_conclude": "Cannot infer economic hypothesis learning or grammar exhaustion.",
        "evidence_paths": f"{source_evidence('epoch0_runner', '_generate_lane')}|{source_evidence('nextgen', 'signal_record/multiobjective_evaluate')}",
    }
    for algorithm in ("cem", "uct_mcts", "evolutionary", "surrogate"):
        index[("EPOCH0", algorithm)].update(epoch0_common)
    index[("EPOCH0", "cem")].update({"implementation_entrypoint": "nextgen_epoch.cem_preference", "learnable_parameters": "mechanism;primitive;interaction;lookback-window elite frequencies", "nonlearnable_parameters": "exact field slot;long lookback window;threshold;direction;target horizon;mapping", "field_identity_learnable": "INDIRECT_VIA_LEARNED_MECHANISM_FAMILY_EXACT_FIELD_SLOT_RANDOM", "lookback_window_learnable": "YES_SHORT_LOOKBACK_WINDOW_ONLY", "matched_control": "NONE_IN_EPOCH0"})
    index[("EPOCH0", "uct_mcts")].update({"implementation_entrypoint": "nextgen_epoch.UCTProgramPolicy", "learnable_parameters": "mechanism;primitive;interaction;lookback-window path values", "nonlearnable_parameters": "exact field slot;long lookback window;threshold;direction;target horizon;mapping", "field_identity_learnable": "INDIRECT_VIA_LEARNED_MECHANISM_FAMILY_EXACT_FIELD_SLOT_RANDOM", "lookback_window_learnable": "YES_SHORT_LOOKBACK_WINDOW_ONLY", "matched_control": "NONE_IN_EPOCH0"})
    index[("EPOCH0", "evolutionary")].update({"implementation_entrypoint": "nextgen_epoch.mutate_program;epoch0._generate_lane", "learnable_parameters": "reward-selected parent program including its fields/lookbacks;one random mutation slot", "nonlearnable_parameters": "target horizon;mapping;mutation distribution", "field_identity_learnable": "INDIRECT_VIA_REWARD_SELECTED_PARENT_PROGRAM", "lookback_window_learnable": "INDIRECT_VIA_REWARD_SELECTED_PARENT_PROGRAM_AND_RANDOM_MUTATION", "matched_control": "NONE_IN_EPOCH0"})
    index[("EPOCH0", "surrogate")].update({"implementation_entrypoint": "nextgen_epoch.surrogate_rank", "learnable_parameters": "ridge coefficients for mechanism/primitive/interaction/lookback windows/threshold/direction", "nonlearnable_parameters": "exact field slot;target horizon;portfolio mapping", "field_identity_learnable": "INDIRECT_VIA_LEARNED_MECHANISM_FAMILY_FIELD_SLOT_NOT_ENCODED", "lookback_window_learnable": "YES_SHORT_AND_LONG_LOOKBACK_WINDOWS", "matched_control": "NONE_IN_EPOCH0"})
    for algorithm in ("typed_random", "typed_ast"):
        index[("EPOCH0", algorithm)].update({
            "implementation_status": "IMPLEMENTED_SAME_CANONICAL_SAMPLER",
            "implementation_entrypoint": "nextgen_epoch.make_program",
            "feedback_function": "NONE",
            "feedback_coordinate": "deterministic hash choice by seed/ordinal/salt",
            "learnable_parameters": "NONE",
            "nonlearnable_parameters": "all ProgramSpec slots;mapping",
            "field_identity_learnable": "NO_RANDOM_SAMPLING_ONLY",
            "lookback_window_learnable": "NO_RANDOM_SAMPLING_ONLY",
            "objective_mismatch_classification": "TYPED_RANDOM_VS_TYPED_AST_CANONICAL_COMPARISON_DEGENERATE",
            "conclusion_scope": "Given equal seed/ordinal and family scope, lane labels do not enter _choice and canonical programs coincide.",
            "cannot_conclude": "Does not show typed grammars are useless; it shows this pair is not an independent algorithm comparison.",
            "evidence_paths": source_evidence("nextgen", "make_program/canonical_program"),
        })
    index[("EPOCH0", "llm_repair")].update({
        "implementation_status": "IMPLEMENTED_STATIC_TEMPLATE_LEGALITY_REPAIR_NO_MODEL_CALL",
        "implementation_entrypoint": "nextgen_epoch.make_program[lane_id=llm_proposal_repair]",
        "feedback_function": "NONE",
        "feedback_coordinate": "frozen template selection;self-difference and multiscale legality fixes",
        "learnable_parameters": "NONE",
        "nonlearnable_parameters": "all grammar slots;mechanism semantics;mapping",
        "field_identity_learnable": "NO",
        "lookback_window_learnable": "NO_STATIC_REPAIR_ONLY",
        "objective_mismatch_classification": "NOT_A_LEARNED_LLM_PROPOSAL_POLICY",
        "conclusion_scope": "Legality repair exists; novel mechanism generation is not evidenced.",
        "cannot_conclude": "Cannot qualify an external or live LLM search system.",
        "evidence_paths": source_evidence("nextgen", "make_program"),
    })

    epoch1_common = {
        "implementation_status": "IMPLEMENTED_INHERITED_UNCHANGED_FROM_EPOCH1",
        "feedback_function": "search_revision.development_feedback",
        "feedback_coordinate": "full development vector collapsed to limited_scalar/near-miss",
        "cost_in_feedback": "YES_FIXED_5BPS_ON_MAPPED_L1_TURNOVER",
        "benchmark_increment_in_feedback": "YES_LCB",
        "uncertainty_in_feedback": "YES_NAIVE_LCB_NO_DEPENDENCE_CORRECTION",
        "stability_in_feedback": "YES_MONTHLY_BLOCKS",
        "portfolio_mapping_learnable": "NO_FIXED_RANK_WEIGHTS",
        "objective_mismatch_classification": "PARTIAL_ALIGNMENT_WITH_RESIDUAL_STRICT_ONLY_AXES",
        "conclusion_scope": "Epoch1 materially changed feedback versus Epoch0; Epoch1R changed admission only and preserved that feedback.",
        "cannot_conclude": "IC/placebo strict gates and dependence-aware uncertainty were not learned, so full objective alignment is not established.",
        "evidence_paths": f"{source_evidence('revision', 'development_feedback')}|{source_evidence('epoch1r_runner', 'validate_unchanged_upstream')}",
    }
    for algorithm in ("cem", "uct_mcts", "evolutionary", "surrogate"):
        index[("EPOCH1R", algorithm)].update(epoch1_common)
    index[("EPOCH1R", "cem")].update({"implementation_entrypoint": "epoch1._generate_lane[cem]", "learnable_parameters": "early-gate eligible mechanism/primitive/interaction/lookback-window preferences", "nonlearnable_parameters": "exact field slot;threshold;direction;target horizon;mapping", "field_identity_learnable": "INDIRECT_VIA_LEARNED_MECHANISM_FAMILY_EXACT_FIELD_SLOT_RANDOM", "lookback_window_learnable": "YES_SHORT_LOOKBACK_WINDOW_ONLY", "matched_control": "cem_matched_control"})
    index[("EPOCH1R", "uct_mcts")].update({"implementation_entrypoint": "epoch1._generate_lane[uct_mcts]", "learnable_parameters": "mechanism/primitive/interaction/lookback-window UCT values minus crowding", "nonlearnable_parameters": "exact field slot;threshold;direction;target horizon;mapping", "field_identity_learnable": "INDIRECT_VIA_LEARNED_MECHANISM_FAMILY_EXACT_FIELD_SLOT_RANDOM", "lookback_window_learnable": "YES_SHORT_LOOKBACK_WINDOW_ONLY", "matched_control": "uct_matched_control"})
    index[("EPOCH1R", "evolutionary")].update({"implementation_entrypoint": "epoch1._generate_lane[evolutionary]", "learnable_parameters": "early-gate parent-program selection by near-miss then scalar", "nonlearnable_parameters": "target horizon;mutation distribution;mapping", "field_identity_learnable": "INDIRECT_VIA_REWARD_SELECTED_PARENT_PROGRAM", "lookback_window_learnable": "INDIRECT_VIA_REWARD_SELECTED_PARENT_PROGRAM_AND_RANDOM_MUTATION", "matched_control": "evolutionary_matched_control"})
    index[("EPOCH1R", "surrogate")].update({"implementation_entrypoint": "epoch1._generate_lane[surrogate];nextgen_epoch.surrogate_rank", "learnable_parameters": "ridge coefficients against near-miss + 0.1*limited_scalar including mechanism and lookback windows", "nonlearnable_parameters": "exact field slot;target horizon;mapping", "field_identity_learnable": "INDIRECT_VIA_LEARNED_MECHANISM_FAMILY_FIELD_SLOT_NOT_ENCODED", "lookback_window_learnable": "YES_SHORT_AND_LONG_LOOKBACK_WINDOWS", "matched_control": "surrogate_matched_control"})
    for algorithm in ("typed_random", "typed_ast"):
        index[("EPOCH1R", algorithm)].update({
            "implementation_status": "IMPLEMENTED_SAME_CANONICAL_SAMPLER",
            "implementation_entrypoint": "epoch1._program_for_lane;nextgen_epoch.make_program",
            "feedback_function": "NONE",
            "feedback_coordinate": "deterministic hash choice",
            "objective_mismatch_classification": "TYPED_RANDOM_VS_TYPED_AST_CANONICAL_COMPARISON_DEGENERATE",
            "conclusion_scope": "Same ProgramSpec sampler; labels do not create independent search logic.",
            "cannot_conclude": "No conclusion about typed grammar economic value.",
            "evidence_paths": f"{source_evidence('epoch1_runner', '_program_for_lane')}|{source_evidence('nextgen', 'make_program')}",
        })
    index[("EPOCH1R", "llm_repair")].update({
        "implementation_status": "IMPLEMENTED_STATIC_TEMPLATE_LEGALITY_REPAIR_NO_MODEL_CALL",
        "implementation_entrypoint": "nextgen_epoch.make_program[lane_id=llm_proposal_repair]",
        "feedback_function": "NONE",
        "feedback_coordinate": "frozen template legality repair",
        "objective_mismatch_classification": "NOT_A_LEARNED_LLM_PROPOSAL_POLICY",
        "conclusion_scope": "Same static repair semantics as Epoch0.",
        "cannot_conclude": "Cannot qualify model-driven mechanism generation.",
        "evidence_paths": source_evidence("nextgen", "make_program"),
    })

    epoch2_evolution = index[("EPOCH2", "evolutionary")]
    epoch2_evolution.update({
        "implementation_status": "IMPLEMENTED_FROZEN_PARENT_BLOCKER_REPAIR",
        "implementation_entrypoint": "scripts/crypto_epoch2.py#apply_repair/generate_spec",
        "feedback_function": "NONE_ONLINE_FOR_EVOLUTIONARY;parent pack frozen from Epoch1R",
        "feedback_coordinate": "blocker-specific window/interaction overwrite after one random mutation",
        "cost_in_feedback": "INDIRECT_PARENT_BLOCKER",
        "benchmark_increment_in_feedback": "INDIRECT_PARENT_BLOCKER",
        "uncertainty_in_feedback": "PARENT_LCB_ONLY",
        "stability_in_feedback": "INDIRECT_PARENT_BLOCKER",
        "learnable_parameters": "NONE_ONLINE;deterministic blocker action",
        "nonlearnable_parameters": "field identity;primitive;mapping;repair policy",
        "field_identity_learnable": "INHERITED_FROM_FROZEN_REWARD_SELECTED_PARENT_PACK_PLUS_RANDOM_MUTATION_NOT_LEARNED_ONLINE",
        "lookback_window_learnable": "BLOCKER_RULE_ONLY_NOT_LEARNED",
        "matched_control": "evolutionary_random_control",
        "objective_mismatch_classification": "BLOCKER_LOCAL_REPAIR_NOT_GLOBAL_OBJECTIVE_OPTIMIZATION",
        "conclusion_scope": "Tests a frozen repair heuristic against a matched random mutation control.",
        "cannot_conclude": "Does not qualify general evolutionary search capability or mechanism-space exhaustion.",
        "evidence_paths": source_evidence("epoch2_runner", "repair_action/apply_repair/generate_spec"),
    })
    index[("EPOCH2", "uct_mcts")].update({
        "implementation_status": "IMPLEMENTED_LOCAL_UCB_ACTION_SELECTOR_NOT_FULL_PROGRAM_MCTS",
        "implementation_entrypoint": "scripts/crypto_epoch2.py#select_local_mcts_action/update_local_mcts",
        "feedback_function": "near_miss_score + 1000*(net_lcb or benchmark_increment_lcb)",
        "feedback_coordinate": "blocker class and repair action index",
        "cost_in_feedback": "YES_VIA_NET_LCB",
        "benchmark_increment_in_feedback": "YES_FOR_BENCHMARK_BLOCKER",
        "uncertainty_in_feedback": "YES_INPUT_LCB_NO_POLICY_POSTERIOR",
        "stability_in_feedback": "NEAR_MISS_COMPONENT_ONLY",
        "learnable_parameters": "repair action index within blocker;window for COST_ONLY;interaction for selected blockers",
        "nonlearnable_parameters": "field identity;primitive;mapping;repair grammar",
        "field_identity_learnable": "NO",
        "lookback_window_learnable": "YES_ACTION_INDEX_ONLY_FOR_COST_ONLY_BLOCKER",
        "matched_control": "local_mcts_random_control",
        "objective_mismatch_classification": "BLOCKER_LOCAL_PROXY_TO_GLOBAL_STRICT_OBJECTIVE_MISMATCH",
        "conclusion_scope": "UCB learns among a tiny frozen repair action set, not over full ProgramSpec or economic hypotheses.",
        "cannot_conclude": "Does not establish full UCT/MCTS instrument capability.",
        "evidence_paths": source_evidence("epoch2_runner", "select_local_mcts_action/update_local_mcts"),
    })
    index[("EPOCH2", "llm_repair")].update({
        "implementation_status": "IMPLEMENTED_PROMPT_RECORD_PLUS_DETERMINISTIC_REPAIR_NO_MODEL_CALL",
        "implementation_entrypoint": "scripts/crypto_epoch2.py#generate_spec[llm_typed_repair]",
        "feedback_function": "NONE_ONLINE;frozen blocker row embedded in prompt",
        "feedback_coordinate": "deterministic ordinal repair_action;prompt is provenance only",
        "cost_in_feedback": "INDIRECT_PARENT_BLOCKER",
        "benchmark_increment_in_feedback": "INDIRECT_PARENT_BLOCKER",
        "uncertainty_in_feedback": "PARENT_LCB_ONLY",
        "stability_in_feedback": "INDIRECT_PARENT_BLOCKER",
        "learnable_parameters": "NONE",
        "nonlearnable_parameters": "all policy parameters;field identity;mapping",
        "field_identity_learnable": "NO",
        "lookback_window_learnable": "NO_DETERMINISTIC_RULE_ONLY",
        "matched_control": "llm_random_repair_control",
        "objective_mismatch_classification": "NOT_A_MODEL_DRIVEN_LLM_REPAIR_POLICY",
        "conclusion_scope": "The artifact qualifies typed deterministic repair, not an LLM's proposal capability.",
        "cannot_conclude": "Cannot infer LLM repair effectiveness.",
        "evidence_paths": source_evidence("epoch2_runner", "generate_spec"),
    })
    index[("EPOCH2", "cem")].update({
        "implementation_status": "DIAGNOSTIC_ONLY_NO_PROPOSAL_OR_SELECTION_USE",
        "implementation_entrypoint": "scripts/crypto_epoch2.py#cem_diagnostic",
        "feedback_function": "early-gate eligible elite descriptive summary",
        "feedback_coordinate": "post-proposal sketch rows",
        "cost_in_feedback": "YES_FILTER_USES_NET_AND_TURNOVER",
        "benchmark_increment_in_feedback": "NO",
        "uncertainty_in_feedback": "NO",
        "stability_in_feedback": "YES_POSITIVE_BLOCK_FILTER",
        "objective_mismatch_classification": "NOT_AN_EXECUTED_SEARCH_POLICY",
        "conclusion_scope": "CEM is report-only in Epoch2.",
        "cannot_conclude": "No Epoch2 CEM capability or failure conclusion is supported.",
        "evidence_paths": source_evidence("epoch2_runner", "cem_diagnostic"),
    })
    index[("EPOCH2", "surrogate")].update({
        "implementation_status": "DIAGNOSTIC_ONLY_POST_STRICT_CROSSFIT_NO_SELECTION_USE",
        "implementation_entrypoint": "scripts/crypto_epoch2.py#surrogate_crossfit",
        "feedback_function": "two-seed grouped cross-fit predictions",
        "feedback_coordinate": "post-strict mechanism_id x repair_action",
        "cost_in_feedback": "YES_TARGETS_USE_NET_LCB",
        "benchmark_increment_in_feedback": "YES_NEAR_DISTANCE",
        "uncertainty_in_feedback": "YES_REPORTED_NOT_USED",
        "stability_in_feedback": "YES_PARETO_FEASIBLE_TARGET",
        "objective_mismatch_classification": "NOT_AN_EXECUTED_SEARCH_POLICY",
        "conclusion_scope": "Surrogate is diagnostic and cannot affect proposal/admission/selection.",
        "cannot_conclude": "No Epoch2 surrogate search result exists.",
        "evidence_paths": source_evidence("epoch2_runner", "surrogate_crossfit"),
    })
    for algorithm in ("typed_random", "typed_ast"):
        index[("EPOCH2", algorithm)].update({
            "implementation_status": "IMPLEMENTED_SAME_CANONICAL_SAMPLER",
            "implementation_entrypoint": "scripts/crypto_epoch2.py#generate_spec;nextgen_epoch.make_program",
            "feedback_function": "NONE",
            "feedback_coordinate": "deterministic hash choice",
            "objective_mismatch_classification": "TYPED_RANDOM_VS_TYPED_AST_CANONICAL_COMPARISON_DEGENERATE",
            "conclusion_scope": "Fresh typed lanes differ by label/lineage, not canonical generation logic for equal seed/ordinal.",
            "cannot_conclude": "No typed search capability comparison is identified.",
            "evidence_paths": f"{source_evidence('epoch2_runner', 'generate_spec')}|{source_evidence('nextgen', 'make_program')}",
        })

    for stage in ("B1S", "EPOCH0", "EPOCH1R", "EPOCH2"):
        index[(stage, "rx_ucb")].update({
            "implementation_status": "NOT_RECOVERED",
            "implementation_entrypoint": "NONE_NAMED_RX_UCB",
            "feedback_function": "NONE",
            "feedback_coordinate": "NONE",
            "objective_mismatch_classification": "NOT_RECOVERED",
            "conclusion_scope": "No named RX-UCB implementation was recovered in accepted-closure alphafactory_crypto/scripts/config/reports; ordinary UCT/UCB implementations are recorded separately.",
            "cannot_conclude": "Does not prove RX-UCB is absent outside this ref or under an unrecognized name.",
            "evidence_paths": f"static_search_scope={CLOSURE_REF}:alphafactory_crypto|scripts|config|reports;positive_UCB={source_evidence('epoch2_runner', 'select_local_mcts_action')}",
        })
    return rows


def mapping_diagnostics() -> dict[str, Any]:
    _, b1s, _ = _install_runtime_modules()
    base = np.array([-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0])[:, None]
    shifted = np.hstack([base, base + 100.0])
    scaled = np.hstack([base, base * 10.0])
    confidence = np.hstack([base, np.sign(base) * np.square(np.abs(base))])
    rank_flip = np.array([
        [-3.0, -3.0], [-2.0, -2.0], [-1.0, 0.01], [0.0, -0.01], [1.0, 1.0], [2.0, 2.0], [3.0, 3.0],
    ])
    sparse = np.full((7, 1), np.nan); sparse[3, 0] = 5.0
    five = np.arange(5, dtype=float)[:, None]

    def mapped_turnover(signal: np.ndarray) -> float:
        weights = b1s.rank_weights(signal)
        return float(np.abs(weights[:, 1] - weights[:, 0]).sum()) if weights.shape[1] > 1 else 0.0

    return {
        "common_mode_raw_l1_change": float(np.abs(shifted[:, 1] - shifted[:, 0]).sum()),
        "common_mode_mapped_turnover": mapped_turnover(shifted),
        "scale_raw_l1_change": float(np.abs(scaled[:, 1] - scaled[:, 0]).sum()),
        "scale_mapped_turnover": mapped_turnover(scaled),
        "confidence_shape_mapped_turnover": mapped_turnover(confidence),
        "single_finite_event_mapped_gross": float(np.abs(b1s.rank_weights(sparse)).sum()),
        "small_rank_flip_raw_l1_change": float(np.abs(rank_flip[:, 1] - rank_flip[:, 0]).sum()),
        "small_rank_flip_mapped_turnover": mapped_turnover(rank_flip),
        "five_asset_final_max_abs_weight": float(np.max(np.abs(b1s.rank_weights(five)))),
        "five_asset_requested_cap": 0.20,
        "zero_net_max_abs": float(np.max(np.abs(b1s.rank_weights(shifted).sum(axis=0)))),
        "gross_exposure": [float(value) for value in np.abs(b1s.rank_weights(shifted)).sum(axis=0)],
    }


def _csv_text(rows: list[dict[str, str]]) -> str:
    if not rows:
        raise ValueError("empty audit table")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    return output.getvalue()


def render_proxy_report(rows: list[dict[str, str]]) -> str:
    by_stage = {stage: [row for row in rows if row["stage"] == stage] for stage in ("B1S", "EPOCH0", "EPOCH1R", "EPOCH2")}
    return f"""# Crypto Proxy-to-Final Objective Audit

Status: `CRYPTO_SEARCH_INSTRUMENT_MISMATCH_CONFIRMED` (bounded to the implementations below)

## Scope and provenance

- Current navigation baseline: `main@{MAIN_BASELINE_SHA}`.
- Accepted economic-evidence line and recovered source: `{CLOSURE_REF}@{EXPECTED_CLOSURE_SHA}`.
- This audit executed no market-return evaluation, opened no sealed block, integrated no data, changed no reward, and made no candidate promotion.
- All algorithm details are recorded row-by-row in `runtime/crypto_latest_evidence_independent_audit_20260714/CRYPTO_ALGORITHM_OBJECTIVE_LINEAGE.csv` with source blob identities and historical run IDs.

## Findings

### B1S

The adaptive challenger is not three independently implemented algorithms. `generate_proposals` rotates the labels `cem`, `uct_mcts`, and `evolutionary`; the runner aggregates all 64 pilot results by operator and applies one shared preferred operator to the remaining proposals. Its feedback is `proxy_score`: a gross, zero-cost risk ratio on subsampled development coordinates. Strict evaluation instead applies 5 bps to mapped L1 turnover and requires positive net mean and IC. Therefore the B1S adaptive comparison is both **algorithm-label degenerate** and **proxy-to-strict mismatched**. This says nothing about properly implemented CEM, UCT, or evolutionary search.

### Why the mismatch is not merely a reward-label difference

For B1S and Epoch-0, the adaptive scalar is

```text
P = mean(gross_return) / std(gross_return) * sqrt(observations)
```

and `gross_return` is produced with `cost_bps=0`. For `P` to be a sufficient statistic for strict selection, candidates with the same `P` would need to have the same strict decision/ranking, or at least an order preserved by `P`. The implementation does not have that property:

- **Cost and turnover:** the scalar does not retain the weight path. Different weight paths can produce the same aggregate gross-return scalar while having different `sum(abs(w[t]-w[t-1]))`; strict net then differs by `turnover * 5 / 10000` and can reverse order.
- **Cross-sectional IC:** aggregate portfolio return does not uniquely determine the cross-sectional rank correlation of weights and targets. IC and IC LCB can therefore differ at the same gross scalar.
- **Benchmark and stability:** a mean/std scalar is many-to-one over return paths. Paths with the same scalar can have different monthly/quarterly block order, worst block, positive-block fraction, and benchmark-increment LCB.
- **Controls:** placebo qualification, wrong-lag diagnostics, and adaptive-versus-matched-control deltas depend on coordinates or comparison arms absent from `P`; they can vary without changing the gross scalar.

Consequently equal—or higher—gross proxy does not uniquely imply equal—or higher—strict quality. The feedback cannot uniquely direct search toward the final strict surface; this is a functional-information mismatch, not a renamed reward.

The existing Epoch-2B cache provides limited corroboration without a new return run: among its rare positive gross-LCB-proxy rows, `98.4615%` were classified cost-killed. That figure is **not** an exact recomputed gross LCB. Epoch-2B defines the summary approximation as `gross_lcb_proxy = net_lcb + mean_cost_drag` because gross-series variance was not retained. It supports only the bounded claim that the cached cost axis frequently changes the sign/qualification after a positive gross summary; it does not estimate an exact gross LCB, prove causality for every candidate, or replace the sufficiency argument above. Evidence: `{source_evidence('epoch2b_report', 'cost-killed/gross-LCB caveat')}` and `{source_evidence('epoch2b_decision', 'cost_killed_share_of_positive_gross_lcb_proxy')}`.

### Epoch-0

CEM, UCT, evolutionary, and surrogate policies are real sampling policies, but all learn from `SignalRecord.proxy_score`, a costless gross rank-weight portfolio ratio. The strict vector adds cost, turnover, benchmark incremental LCB, time-block stability, IC LCB, concentration, a placebo hard gate and Pareto axes; wrong-lag is retained as a diagnostic, not a gate. The mismatch is substantive, not a naming issue. CEM/UCT/surrogate learn mechanism family and other encoded grammar slots, so they can indirectly change the field distribution, but none learns the exact field slot. Evolutionary selection can inherit exact fields through selected parents, while field mutation remains random. Portfolio mapping is fixed for every lane.

`typed_random_fresh` and `typed_ast` call the same `make_program` sampler. Lane/algorithm labels are excluded from `_choice` and canonical program identity, so equal seed/ordinal/family scope yields the same canonical program. This pair is not an independent algorithm comparison.

### Epoch-1 and Epoch-1R

Epoch-1 **did materially repair** the Epoch-0 feedback: `development_feedback` includes fixed-cost net LCB, benchmark increment LCB, monthly worst/positive blocks, stability, turnover and concentration. Epoch-1R explicitly preserves that search/reward implementation and changes admission only. It is incorrect to describe Epoch-1R as merely renaming the gross scalar, but it is also incorrect to claim full alignment: final strict evaluation still adds IC LCB, a placebo hard gate and a different multiobjective/Pareto surface. Wrong-lag is computed and retained only as a diagnostic. Naive LCB calculations do not correct temporal dependence.

### Epoch-2

Epoch-2 is blocker-local repair, not an unrestricted economic-hypothesis learner. Evolutionary repair applies a deterministic blocker action after a random mutation and has a matched random control. Local MCTS is a UCB selector over at most four blocker action indices; it does not search the full ProgramSpec, field identity, or portfolio mapping. Its reward is near-miss score plus a blocker-specific net/benchmark LCB term. CEM and surrogate are explicitly diagnostic-only and cannot affect proposal, admission, or selection. `llm_typed_repair` records a prompt but performs deterministic local code repair with no model call.

No named `RX-UCB` implementation was recovered in the accepted closure's `alphafactory_crypto/`, `scripts/`, `config/`, or `reports/`. That status is `NOT_RECOVERED`, not `NOT_IMPLEMENTED` and not evidence about code outside the audited ref.

## Exact mismatch boundary

| Stage | Feedback actually used | Final/strict surface omitted by feedback | Qualification |
|---|---|---|---|
| B1S | costless gross proxy on subsampled coordinates | cost, turnover, IC and strict survivor rule | `CONFIRMED_PROXY_TO_STRICT_OBJECTIVE_MISMATCH`; adaptive labels degenerate |
| Epoch-0 | costless gross proxy for every adaptive policy | cost, benchmark increment, stability, IC, placebo, concentration, Pareto vector | `CONFIRMED_GROSS_PROXY_TO_STRICT_MULTI_OBJECTIVE_MISMATCH` |
| Epoch-1R | net/benchmark/stability/turnover/concentration limited scalar and near-miss | IC, placebo hard gate and the complete strict Pareto surface; wrong-lag remains diagnostic-only | `PARTIAL_ALIGNMENT_WITH_RESIDUAL_STRICT_ONLY_AXES` |
| Epoch-2 | frozen blocker-local rule; UCB uses near-miss plus one target LCB | global strict vector and unsearched grammar/mapping slots | `BLOCKER_LOCAL_PROXY_TO_GLOBAL_STRICT_OBJECTIVE_MISMATCH` |

## Supported and unsupported conclusions

Supported: the current internal search instrument is **not fully qualified**. B1S and Epoch-0 have confirmed objective mismatch; Epoch-1 materially narrows it; Epoch-1R does not change it; Epoch-2 tests only a small repair action surface. Typed-random/typed-AST and B1S adaptive-label comparisons are degenerate at the generator/policy level.

Not supported: that the implemented grammar has no alpha, that the mechanism space is exhausted, that new data is the only possible next step, or that CEM/UCT/evolutionary/surrogate/LLM paradigms are economically ineffective. Existing negative economic evidence remains separate from this capability audit.
"""


def render_mapping_report(diagnostic: Mapping[str, Any]) -> str:
    return f"""# Crypto Portfolio Mapping and Cost Attribution

Status: `PORTFOLIO_MAPPING_CAUSAL_SHARE_NOT_IDENTIFIED`; synthetic collapse/amplification mechanisms are confirmed.

## Implemented mapping

The accepted closure uses one `rank_weights` mapping in B1S, Epoch-0, Epoch-1R and Epoch-2:

1. cross-sectionally rank every timestamp;
2. center ranks, forcing zero net exposure;
3. normalize by cross-sectional L1 magnitude;
4. clip at `max_abs_weight=0.20`;
5. renormalize to gross exposure 1.

Source: `{source_evidence('b1s', 'rank_weights')}`. The post-clip renormalization can undo the nominal cap: the deterministic five-asset case requests `0.20` but ends at max absolute weight `{diagnostic['five_asset_final_max_abs_weight']:.12g}`.

## Deterministic non-market diagnostics

| Case | Raw signal change | Mapped consequence |
|---|---:|---:|
| Common-mode shift | L1 `{diagnostic['common_mode_raw_l1_change']:.12g}` | weight turnover `{diagnostic['common_mode_mapped_turnover']:.12g}` |
| Positive scale change | L1 `{diagnostic['scale_raw_l1_change']:.12g}` | weight turnover `{diagnostic['scale_mapped_turnover']:.12g}` |
| Confidence-gap reshaping with ranks fixed | not a portfolio measure | weight turnover `{diagnostic['confidence_shape_mapped_turnover']:.12g}` |
| One finite sparse event | n/a | mapped gross `{diagnostic['single_finite_event_mapped_gross']:.12g}` |
| Small cross-sectional rank flip | L1 `{diagnostic['small_rank_flip_raw_l1_change']:.12g}` | weight turnover `{diagnostic['small_rank_flip_mapped_turnover']:.12g}` |

The mapping therefore:

- removes common-mode directional level and positive scale/confidence information;
- forces zero net and unit gross whenever the cross section has dispersion (`zero_net_max_abs={diagnostic['zero_net_max_abs']:.3g}`, gross={json.dumps(diagnostic['gross_exposure'])});
- collapses a single finite sparse event to zero weight;
- has no stateful holding rule; it reranks every coordinate;
- can suppress large raw moves when rank order is unchanged, or create material weight turnover from a small rank crossing.

These are mechanism demonstrations, not evidence that mapping caused the majority of historical turnover. The existing artifacts do not persist a counterfactual decomposition from raw signal change to mapped-weight change, so the question "did rank mapping create the main turnover?" remains `NOT_IDENTIFIED`.

## Cost decomposition

The executable formula is:

```text
gross[t] = sum_i(weight[i,t] * target_return[i,t])
mapped_L1_turnover[t] = sum_i(abs(weight[i,t] - weight[i,t-1]))
fixed_cost[t] = mapped_L1_turnover[t] * 5 / 10000
net[t] = gross[t] - fixed_cost[t]
```

The implementation initializes `previous` to zero and only fills `previous[:, 1:]` from prior weights. Therefore at `t=0`, `mapped_L1_turnover[0] = sum_i(abs(weight[i,0]))`: the initial build from cash/zero exposure is charged the same 5 bps fixed rate. With the usual unit-gross mapped book, that initial charge is 5 bps before any subsequent rebalance.

Source: `{source_evidence('b1s', '_portfolio_series')}` and `{source_evidence('nextgen', 'portfolio_series')}`.

Attribution must remain four-way:

| Layer | What is known | What is not known |
|---|---|---|
| Raw signal dynamics | Primitive output changes before mapping | No canonical raw-signal turnover unit or tradable counterfactual is persisted |
| Mapping-created turnover | Exact L1 turnover of final rank weights is charged | The portion caused specifically by reranking versus true signal state changes is not separately stored |
| Fixed cost | Exactly 5 bps per unit mapped L1 turnover | Calibration to venue/size/liquidity is not established here |
| Trading frictions | None beyond fixed rate | Spread, slippage, impact, fill probability and capacity are unmodeled |

The target contract already represents `trade_close[t+2]/trade_close[t+1]-1` for completed bucket `t`; `portfolio_series` multiplies the weight and this delayed label at the same stored coordinate. The mapping adds no separate execution-delay or stateful-hold model.

## Conclusion boundary

It is valid to say the rank mapping destroys absolute/common-mode confidence, forces zero-net/unit-gross exposure, collapses singleton events, and can add turnover through reranking. It is not valid to attribute cost-after-mapping failure wholly to raw information quality, nor to claim mapping is the dominant historical cause without a persisted counterfactual decomposition. Spread/slippage/impact remain outside the evaluator.
"""


def _render_all() -> dict[Path, str]:
    closure_sha()
    algorithms = algorithm_rows()
    primitives = primitive_rows()
    diagnostics = mapping_diagnostics()
    return {
        ALGORITHM_CSV: _csv_text(algorithms),
        PRIMITIVE_CSV: _csv_text(primitives),
        PROXY_REPORT: render_proxy_report(algorithms),
        MAPPING_REPORT: render_mapping_report(diagnostics),
    }


def build() -> None:
    rendered = _render_all()
    for path, content in rendered.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    print(json.dumps({"status": "CRYPTO_INSTRUMENT_SEMANTICS_AUDIT_BUILT", "outputs": [str(path.relative_to(REPO)).replace('\\', '/') for path in rendered]}, indent=2))


def check() -> None:
    sources = {key: blob(path) for key, path in SOURCE_PATHS.items()}
    guards = {
        "b1s_shared_algorithm_labels": 'algorithms = ("cem", "uct_mcts", "evolutionary")',
        "b1s_gross_proxy": "_portfolio_series(weights[:, coordinate_mask], target[:, coordinate_mask], 0.0)",
        "epoch0_proxy_feedback": "policy.update(ordinal, record.proxy_score)",
        "epoch1_limited_scalar": 'reward = float(feedback["limited_scalar"]) - crowding',
        "epoch1r_objective_guard": "reward/objective/adaptive logic changed outside narrow admission repair",
        "epoch2_ucb": "Frozen UCB rule with an exploration floor",
        "epoch2_llm_prompt_only": "prompt=f'current={canonical_program_json(parent)}",
        "rank_mapping": "ranks = pd.DataFrame(signal).rank(axis=0, pct=True, method=\"average\")",
        "epoch2b_cost_killed_cache": "Cost-killed share among the rare positive gross-LCB proxy rows: 98.4615%.",
        "epoch2b_gross_lcb_caveat": "gross-LCB value is a summary proxy (`net_lcb + mean_cost_drag`), not an exact recomputation",
    }
    locations = {
        "b1s_shared_algorithm_labels": "b1s",
        "b1s_gross_proxy": "b1s",
        "epoch0_proxy_feedback": "epoch0_runner",
        "epoch1_limited_scalar": "epoch1_runner",
        "epoch1r_objective_guard": "epoch1r_runner",
        "epoch2_ucb": "epoch2_runner",
        "epoch2_llm_prompt_only": "epoch2_runner",
        "rank_mapping": "b1s",
        "epoch2b_cost_killed_cache": "epoch2b_report",
        "epoch2b_gross_lcb_caveat": "epoch2b_report",
    }
    for name, needle in guards.items():
        if needle not in sources[locations[name]]:
            raise AssertionError(f"source guard failed: {name}")
    rendered = _render_all()
    for path, expected in rendered.items():
        if not path.exists():
            raise FileNotFoundError(path)
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            raise AssertionError(f"generated output drift: {path.relative_to(REPO)}")
    algorithms = pd.read_csv(ALGORITHM_CSV)
    primitives = pd.read_csv(PRIMITIVE_CSV)
    provenance_columns = {
        "repo_ref", "commit_sha", "run_id", "data_release", "evidence_role",
        "superseded", "authoritative_now",
    }
    for name, frame in (("algorithm", algorithms), ("primitive", primitives)):
        if not provenance_columns.issubset(frame.columns):
            raise AssertionError(f"{name} provenance columns missing")
        if frame[list(provenance_columns)].isna().any().any():
            raise AssertionError(f"{name} provenance contains nulls")
        if not frame["commit_sha"].astype(str).map(
            lambda value: len(value) == 40 and set(value.lower()) <= set("0123456789abcdef")
        ).all():
            raise AssertionError(f"{name} commit_sha is not a single valid SHA")
        if set(frame["superseded"].astype(str).str.lower()) != {"false"}:
            raise AssertionError(f"{name} supersession qualification drift")
        if set(frame["authoritative_now"].astype(str).str.lower()) != {"true"}:
            raise AssertionError(f"{name} authority qualification drift")
    if len(algorithms) != 32 or set(algorithms["stage"]) != {"B1S", "EPOCH0", "EPOCH1R", "EPOCH2"}:
        raise AssertionError("algorithm lineage coverage drift")
    if set(algorithms["evidence_role"]) != {"HISTORICAL_SEARCH_INSTRUMENT_OBJECTIVE_QUALIFICATION"}:
        raise AssertionError("algorithm evidence role drift")
    if "horizon_learnable" in algorithms.columns:
        raise AssertionError("ambiguous horizon learnability column returned")
    if "target_horizon_learnable" not in algorithms or "lookback_window_learnable" not in algorithms:
        raise AssertionError("target horizon and lookback window must be separate")
    if set(algorithms["target_horizon_learnable"]) != {"NO_FIXED_TARGET_LABEL"}:
        raise AssertionError("target horizon was incorrectly marked learnable")
    if set(PRIMITIVES) - set(primitives["primitive"]):
        raise AssertionError("primitive coverage drift")
    if set(primitives["run_id"]) != {"NOT_APPLICABLE_STATIC_SEMANTIC_AUDIT"}:
        raise AssertionError("primitive static run qualification drift")
    if set(primitives["data_release"]) != {"NO_MARKET_DATA_READ"}:
        raise AssertionError("primitive data-release qualification drift")
    if set(primitives["evidence_role"]) != {"STATIC_PRIMITIVE_SEMANTIC_QUALIFICATION"}:
        raise AssertionError("primitive evidence role drift")
    cross_name = primitives[
        (primitives["comparison"] == "temporal_program_vs_b1s_canary")
        & primitives["primitive"].isin(["StateAge", "TimeSince", "LastHit"])
    ]
    if len(cross_name) != 3 or not cross_name["right_implementation_status"].eq(
        "IMPLEMENTED_CROSS_NAME_OPERATOR_NOT_TYPED_PRIMITIVE"
    ).all():
        raise AssertionError("B1S event_age cross-name qualification drift")
    if not primitives["actual_behaviour_cluster_equivalence"].isin(
        ["EQUIVALENT", "NOT_EQUIVALENT", "NOT_TESTED_NOT_IMPLEMENTED"]
    ).all():
        raise AssertionError("actual behaviour-cluster comparison missing")
    if (algorithms.loc[algorithms.algorithm == "rx_ucb", "implementation_status"] != "NOT_RECOVERED").any():
        raise AssertionError("RX-UCB qualification drift")
    print("PASS_CRYPTO_INSTRUMENT_SEMANTICS_AUDIT")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("build", "check"))
    args = parser.parse_args()
    {"build": build, "check": check}[args.action]()


if __name__ == "__main__":
    main()
