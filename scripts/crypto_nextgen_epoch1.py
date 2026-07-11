from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from collections import Counter, defaultdict, deque
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import scripts.crypto_nextgen_epoch0 as epoch0
from alphafactory_crypto.b1s_canary import FrozenPanel, rank_weights
from alphafactory_crypto.nextgen_epoch import (
    ProgramSpec, SignalRecord, UCTProgramPolicy, candidate_identity, canonical_program_json,
    complexity, effective_count, make_program, materialize_program, multiobjective_evaluate,
    mutate_program, pareto_front, program_identity, signal_record, surrogate_rank,
)
from alphafactory_crypto.search_revision import (
    adaptive_verdict, admit_full_identity, concentration_metrics, development_feedback,
    epoch0_failure_matrix,
)


CONFIG = REPO / "config/crypto_nextgen_epoch1_v1.json"
MECHANISMS = REPO / "config/crypto_nextgen_mechanism_registry_v1.json"
MODULE = REPO / "alphafactory_crypto/search_revision.py"
RUNNER = Path(__file__)
OUTPUT_ROOT = REPO / "runtime/nextgen_epoch1_20260712"
EPOCH0_ROOT = REPO / "runtime/nextgen_epoch0_20260711"
DIAGNOSIS = OUTPUT_ROOT / "epoch0_failure_attribution_matrix.csv"
REPLAY = OUTPUT_ROOT / "epoch0_admission_offline_replay.csv"
SMOKE = OUTPUT_ROOT / "epoch1_throughput_smoke.json"
FROZEN = OUTPUT_ROOT / "epoch1_frozen_design_manifest.json"
RUN = OUTPUT_ROOT / "epoch1_run_manifest.json"
FAILURE = OUTPUT_ROOT / "epoch1_failure.json"
MAIN_LANES = (
    "typed_random", "typed_ast", "cem", "cem_matched_control", "uct_mcts", "uct_matched_control",
    "evolutionary", "evolutionary_matched_control", "surrogate", "surrogate_matched_control",
    "llm_proposal_repair", "orthogonal_exile",
)
BBO_LANES = ("bbo_typed_temporal",)
ADAPTIVE = ("cem", "uct_mcts", "evolutionary", "surrogate")
MATCHED = {
    "cem": "cem_matched_control", "uct_mcts": "uct_matched_control",
    "evolutionary": "evolutionary_matched_control", "surrogate": "surrogate_matched_control",
}
ALGORITHM = {
    "typed_random": "typed_random", "typed_ast": "typed_ast", "cem": "cem",
    "cem_matched_control": "typed_matched_control", "uct_mcts": "uct_mcts",
    "uct_matched_control": "typed_matched_control", "evolutionary": "evolutionary_search",
    "evolutionary_matched_control": "typed_matched_control", "surrogate": "surrogate",
    "surrogate_matched_control": "typed_matched_control", "llm_proposal_repair": "llm_proposal_repair",
    "orthogonal_exile": "orthogonal_search", "bbo_typed_temporal": "typed_ast",
}
BASE_LANE = {
    "cem_matched_control": "cem", "uct_matched_control": "uct_mcts",
    "evolutionary_matched_control": "evolutionary", "surrogate_matched_control": "surrogate",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_payload(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest().upper()


def git(*args: str, check: bool = True) -> str:
    return subprocess.run(["git", *args], cwd=REPO, text=True, capture_output=True, check=check).stdout.strip()


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def validate_config(config: Mapping[str, Any]) -> None:
    if tuple(config["main_lanes"]) != MAIN_LANES or tuple(config["bbo_lanes"]) != BBO_LANES:
        raise ValueError("Epoch-1 lanes drifted")
    if config["budget_range"] != {"proposals": [32768, 65536], "strict_per_arm": [1536, 2048]}:
        raise ValueError("Epoch-1 budget range drifted")
    if config["matched_controls"] != MATCHED:
        raise ValueError("matched controls drifted")
    if not config["admission_contract"]["full_identity_before_strict_assignment"]:
        raise PermissionError("full identity must precede strict assignment")


def diagnose_and_replay() -> dict[str, Any]:
    strict = pd.read_csv(EPOCH0_ROOT / "strict_evaluations.csv")
    matrix = epoch0_failure_matrix(strict)
    old_raw = pd.read_csv(EPOCH0_ROOT / "raw_proposals.csv", low_memory=False)
    old_admission = pd.read_csv(EPOCH0_ROOT / "admission_table.csv")
    bbo = old_raw[(old_raw["panel_id"] == "bbo_micro") & old_raw["legal"]].copy()
    replay_rows = []
    bbo_rows = []
    for _, row in bbo.sort_values(["ordinal", "proposal_id"]).iterrows():
        bbo_rows.append({
            "proposal_id": row["proposal_id"], "full_exact_identity": row["exact_identity"],
            "mechanism_id": row["mechanism_id"], "parent_identity": row["parent_identity"],
            "behaviour_cluster": row["behaviour_cluster"], "ordinal": int(row["ordinal"]),
        })
    replay = admit_full_identity(bbo_rows, 128)
    replay_rows.append({
        "panel_id": "bbo_micro", "lane_id": "bbo_typed_temporal", "historical_epoch0_admissions": 32,
        "offline_replay_admissions": len(replay.admitted_ids), "requested": 128,
        "identity_scope": "EPOCH0_EXISTING_SKETCH_IDENTITY_OFFLINE_REPLAY",
        "identity_capacity": replay.plan.identity_capacity, "legal_family_count": replay.plan.mechanism_family_count,
        "dynamic_family_cap": replay.plan.family_cap, "mechanical_waste_eliminated": len(replay.admitted_ids) == 128,
        "history_rewritten": False,
    })
    for (panel, lane), group in old_admission[old_admission["panel_id"] == "main"].groupby(["panel_id", "lane_id"]):
        replay_rows.append({
            "panel_id": panel, "lane_id": lane, "historical_epoch0_admissions": len(group),
            "offline_replay_admissions": len(group), "requested": 112,
            "identity_scope": "EPOCH0_EXISTING_ADMISSION_RECORD_NO_REEVALUATION",
            "identity_capacity": group["exact_identity"].nunique(), "legal_family_count": None,
            "dynamic_family_cap": None, "mechanical_waste_eliminated": True, "history_rewritten": False,
        })
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(DIAGNOSIS, index=False)
    pd.DataFrame(replay_rows).to_csv(REPLAY, index=False)
    result = {
        "status": "SEARCH_ENGINE_REVISION_DIAGNOSIS_COMPLETE", "matrix_rows": len(matrix),
        "bbo_old_admissions": 32, "bbo_replay_admissions": len(replay.admitted_ids),
        "epoch0_history_rewritten": False, "new_evaluation_block_read": False,
    }
    (OUTPUT_ROOT / "revision_diagnosis_manifest.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _program_for_lane(registry: Mapping[str, Any], lane: str, panel_id: str, seed: int, ordinal: int, **kwargs: Any) -> ProgramSpec:
    base = BASE_LANE.get(lane, lane)
    spec = make_program(registry, lane_id=base, panel_id=panel_id, algorithm=ALGORITHM[lane], seed=seed, ordinal=ordinal, **kwargs)
    if base != lane:
        spec = ProgramSpec(**({**asdict(spec), "lane_id": lane, "lineage_namespace": f"runtime_only/epoch1/{panel_id}/{lane}/seed_{seed}"}))
    return spec


def _evaluate(
    spec: ProgramSpec, panel: FrozenPanel, benchmark_net: np.ndarray,
    signal_cache: dict[tuple[str, str], tuple[SignalRecord, dict[str, Any]]],
) -> tuple[SignalRecord, dict[str, Any]]:
    key = (panel.panel_id, canonical_program_json(spec))
    if key not in signal_cache:
        try:
            signal = materialize_program(spec, panel)
            record, weights = signal_record(spec, signal, panel, np.ones(len(panel.timestamps), dtype=bool))
            feedback = development_feedback(weights, panel, benchmark_net)
            signal_cache[key] = (record, asdict(feedback))
        except Exception as exc:
            signal_cache[key] = (
                SignalRecord("", "", "", float("-inf"), False, f"{type(exc).__name__}:{exc}"),
                {"early_gate_pass": False, "gate_reasons": "MATERIALIZATION", "survivor_near_miss_score": 0.0, "limited_scalar": -999.0,
                 "net_lcb": float("nan"), "worst_block": float("nan"), "positive_block_fraction": 0.0,
                 "turnover_mean": float("inf"), "benchmark_increment_lcb": float("nan"), "concentration": float("inf")},
            )
    return signal_cache[key]


def _generate_lane(
    registry: Mapping[str, Any], lane: str, panel_id: str, seed: int, count: int,
    feedback_queries: int, panel: FrozenPanel, benchmark_net: np.ndarray,
    cache: dict[tuple[str, str], tuple[SignalRecord, dict[str, Any]]],
) -> tuple[list[ProgramSpec], list[tuple[SignalRecord, dict[str, Any]]], list[dict[str, Any]]]:
    queries = min(feedback_queries, count) if lane in ADAPTIVE else 0
    specs: list[ProgramSpec] = []; evaluations: list[tuple[SignalRecord, dict[str, Any]]] = []; query_rows = []
    if lane == "uct_mcts":
        policy = UCTProgramPolicy(registry, panel_id=panel_id, lane_id=lane, seed=seed, exploration=1.8)
        mechanism_seen: Counter[str] = Counter(); primitive_seen: Counter[str] = Counter()
        for ordinal in range(queries):
            spec = policy.propose(ordinal)
            record, feedback = _evaluate(spec, panel, benchmark_net, cache)
            crowding = 0.4 * mechanism_seen[spec.mechanism_id] / max(1, ordinal) + 0.3 * primitive_seen[spec.primitive] / max(1, ordinal)
            reward = float(feedback["limited_scalar"]) - crowding
            policy.update(ordinal, reward)
            mechanism_seen[spec.mechanism_id] += 1; primitive_seen[spec.primitive] += 1
            specs.append(spec); evaluations.append((record, feedback))
            query_rows.append({"lane_id": lane, "seed": seed, "query_ordinal": ordinal, "development_scalar": feedback["limited_scalar"], "near_miss_score": feedback["survivor_near_miss_score"], "persisted": False})
        preference = policy.frozen_preference()
        for ordinal in range(queries, count):
            # A 50% exploration floor is frozen to counter Epoch-0 UCT root concentration.
            pref = None if ordinal % 2 == 0 else preference
            spec = _program_for_lane(registry, lane, panel_id, seed, ordinal, preference=pref or {})
            specs.append(spec); evaluations.append(_evaluate(spec, panel, benchmark_net, cache))
        return specs, evaluations, query_rows
    initial = [_program_for_lane(registry, lane, panel_id, seed, ordinal, policy_feedback_used=ordinal < queries) for ordinal in range(queries)]
    initial_eval = [_evaluate(spec, panel, benchmark_net, cache) for spec in initial]
    for ordinal, (_, feedback) in enumerate(initial_eval):
        query_rows.append({"lane_id": lane, "seed": seed, "query_ordinal": ordinal, "development_scalar": feedback["limited_scalar"], "near_miss_score": feedback["survivor_near_miss_score"], "persisted": False})
    specs.extend(initial); evaluations.extend(initial_eval)
    remaining = count - len(specs)
    if lane == "cem":
        eligible = [(spec, feedback) for spec, (_, feedback) in zip(initial, initial_eval) if feedback["early_gate_pass"]]
        ranked = sorted(eligible, key=lambda item: item[1]["limited_scalar"], reverse=True)
        elite = [item[0] for item in ranked[: max(12, len(ranked) // 4)]] or initial
        pref: dict[str, tuple[Any, ...]] = {}
        for key in ("mechanism_id", "primitive", "interaction", "window"):
            counts = Counter(getattr(spec, key) for spec in elite)
            pref[key] = tuple(value for value, _ in counts.most_common(min(4, len(counts))))
        tail = [_program_for_lane(registry, lane, panel_id, seed, i + queries, preference=(pref if i % 4 else {})) for i in range(remaining)]
    elif lane == "evolutionary":
        ranked = sorted(zip(initial, initial_eval), key=lambda item: (item[1][1]["survivor_near_miss_score"], item[1][1]["limited_scalar"]), reverse=True)
        parents = [spec for spec, (_, feedback) in ranked if feedback["early_gate_pass"]][:32] or initial[:32]
        tail = [mutate_program(parents[i % len(parents)], registry, seed=seed, ordinal=i + queries) for i in range(remaining)]
    elif lane == "surrogate":
        pool = [_program_for_lane(registry, lane, panel_id, seed + 10000, i + queries) for i in range(max(remaining * 2, remaining + 128))]
        targets = [float(feedback["survivor_near_miss_score"]) + 0.1 * float(feedback["limited_scalar"]) for _, feedback in initial_eval]
        tail = surrogate_rank(initial, targets, pool, remaining)
        if len(tail) < remaining: tail += pool[: remaining - len(tail)]
    else:
        tail = [_program_for_lane(registry, lane, panel_id, seed, ordinal) for ordinal in range(count)]
        specs = []; evaluations = []
    for spec in tail:
        specs.append(spec); evaluations.append(_evaluate(spec, panel, benchmark_net, cache))
    if len(specs) != count: raise ValueError(f"proposal drift {lane}/{seed}: {len(specs)}")
    return specs, evaluations, query_rows


def smoke() -> dict[str, Any]:
    config = load_json(CONFIG); validate_config(config); registry = load_json(MECHANISMS)
    main = epoch0.load_main_panel(include_target=False); bbo = epoch0.load_bbo_panel(main, include_target=False)
    panels = {"main": epoch0.sketch_panel(main, 4), "bbo_micro": epoch0.sketch_panel(bbo, 2)}
    started = time.perf_counter(); hashes = []
    count = int(config["throughput_smoke"]["proposals_per_lane"])
    for panel_id, lanes in (("main", MAIN_LANES), ("bbo_micro", BBO_LANES)):
        for lane in lanes:
            for ordinal in range(count):
                spec = _program_for_lane(registry, lane, panel_id, 3601, ordinal)
                signal = materialize_program(spec, panels[panel_id])
                hashes.append(hashlib.sha256(np.nan_to_num(signal, nan=-999).astype("<f4").tobytes()).hexdigest())
    seconds = time.perf_counter() - started; proposals = count * (len(MAIN_LANES) + len(BBO_LANES))
    projected = seconds / proposals * 32768 + 2400
    payload = {"status": "COMPLETED_NO_PERFORMANCE_READ", "repo_sha": git("rev-parse", "HEAD"), "proposals": proposals,
               "runtime_seconds": seconds, "proposals_per_second": proposals / seconds, "projected_total_seconds": projected,
               "selected_proposals": 32768 if projected <= 5400 else None, "selected_strict_per_arm": 1536 if projected <= 5400 else None,
               "signal_hash": sha256_payload(hashes), "performance_read": False, "target_read": False, "forward_read": False}
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True); SMOKE.write_text(json.dumps(payload, indent=2, sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(payload, indent=2)); return payload


def freeze() -> dict[str, Any]:
    config = load_json(CONFIG); validate_config(config); smoke_result = load_json(SMOKE)
    if smoke_result["selected_proposals"] != 32768 or any(smoke_result[key] for key in ("performance_read", "target_read", "forward_read")):
        raise RuntimeError("Epoch-1 smoke did not qualify freeze")
    if subprocess.run(["git", "diff", "--quiet"], cwd=REPO).returncode: raise RuntimeError("freeze requires committed tracked implementation")
    input_paths = [epoch0.FEATURE_ROOT / f"symbol={symbol}" / "part.parquet" for symbol in epoch0.CORE12] + [epoch0.BBO_DATA]
    contracts = [CONFIG, MECHANISMS, MODULE, RUNNER, REPO / "alphafactory_crypto/nextgen_epoch.py", REPO / "scripts/crypto_nextgen_epoch0.py"]
    inputs = {relative(path): sha256_file(path) for path in input_paths}; contract_hashes = {relative(path): sha256_file(path) for path in contracts}
    proposals = {lane: 2560 for lane in MAIN_LANES} | {BBO_LANES[0]: 2048}
    strict = {lane: 120 for lane in MAIN_LANES} | {BBO_LANES[0]: 96}
    payload = {"experiment_id": "20260712_crypto_nextgen_epoch1_001", "status": "EPOCH1_DESIGN_FROZEN_NOT_STARTED",
               "objective": "test survivor-aligned adaptive search against matched controls under full-identity-first feasible admission",
               "implementation_subject_sha": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
               "input_files_sha256": inputs, "data_release_sha256": sha256_payload(inputs), "contracts_sha256": contract_hashes,
               "contract_bundle_sha256": sha256_payload(contract_hashes), "throughput_smoke_sha256": sha256_file(SMOKE),
               "budget": {"total_proposals": 32768, "proposals_by_lane": proposals, "fixed_seeds": [3701, 3709],
                          "strict_per_arm": 1536, "strict_by_lane": strict, "logical_strict_max": 3072,
                          "adaptive_feedback_queries_per_seed": 256, "refinement_pool_multiplier": 2, "extension_allowed": False},
               "reward_contract": config["objective_contract"], "admission_contract": config["admission_contract"],
               "survivor_contract": config["survivor_contract"], "lane_specs": config["main_lanes"] + config["bbo_lanes"],
               "matched_controls": config["matched_controls"], "capability_matrix": config["capability_matrix"],
               "benchmark_contract": "same frozen simple development benchmarks and 5bps cost as Epoch-0",
               "prohibited": config["prohibited"], "commands": {"run": "python scripts/crypto_nextgen_epoch1.py run", "check": "python scripts/crypto_nextgen_epoch1.py check"},
               "estimated_cost_time": f"{smoke_result['projected_total_seconds']:.1f} seconds", "reproducibility": "FROZEN_HASHES_BUDGET_SEEDS_CONTRACTS",
               "search_started": False, "forward_read": False, "candidate_promotion": False, "a7mem_updated": False}
    payload["frozen_manifest_sha256"] = sha256_payload(payload); FROZEN.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":payload["status"],"budget":payload["budget"],"manifest_sha256":payload["frozen_manifest_sha256"]},indent=2)); return payload


def verify_frozen() -> dict[str, Any]:
    frozen=load_json(FROZEN); recorded=frozen.pop("frozen_manifest_sha256")
    if sha256_payload(frozen)!=recorded: raise ValueError("Epoch-1 frozen hash drift")
    frozen["frozen_manifest_sha256"]=recorded
    if subprocess.run(["git","merge-base","--is-ancestor",frozen["implementation_subject_sha"],"HEAD"],cwd=REPO).returncode: raise ValueError("implementation subject not ancestor")
    for raw,expected in frozen["input_files_sha256"].items():
        path=Path(raw) if Path(raw).is_absolute() else REPO/raw
        if sha256_file(path)!=expected: raise ValueError(f"input drift: {raw}")
    for raw,expected in frozen["contracts_sha256"].items():
        if sha256_file(REPO/raw)!=expected: raise ValueError(f"contract drift: {raw}")
    return frozen


def _round_robin_pool(group: pd.DataFrame, count: int) -> list[str]:
    buckets={key:deque(values.sort_values(["early_gate_pass","survivor_near_miss_score","development_scalar","ordinal"],ascending=[False,False,False,True]).proposal_id.tolist()) for key,values in group.groupby("mechanism_id",sort=True)}
    result=[]; keys=sorted(buckets)
    while len(result)<count and any(buckets.values()):
        for key in keys:
            if buckets[key] and len(result)<count: result.append(buckets[key].popleft())
    return result


def run() -> dict[str, Any]:
    frozen=verify_frozen(); config=load_json(CONFIG); registry=load_json(MECHANISMS); started=time.perf_counter()
    main=epoch0.load_main_panel(); bbo=epoch0.load_bbo_panel(main); full_panels={"main":main,"bbo_micro":bbo}
    sketch_panels={"main":epoch0.sketch_panel(main,4),"bbo_micro":epoch0.sketch_panel(bbo,2)}
    benchmarks,best_full=epoch0._run_benchmarks(full_panels,5.0,5); best_sketch={"main":best_full["main"][::4],"bbo_micro":best_full["bbo_micro"][::2]}
    cache={}; candidate_rows=[]; spec_by_id={}; query_rows=[]; lane_runtime={}
    for panel_id,lanes in (("main",MAIN_LANES),("bbo_micro",BBO_LANES)):
        for lane in lanes:
            lane_start=time.perf_counter(); total=frozen["budget"]["proposals_by_lane"][lane]; per_seed=total//2; lane_ordinal=0
            for seed in frozen["budget"]["fixed_seeds"]:
                specs,evaluations,queries=_generate_lane(registry,lane,panel_id,int(seed),per_seed,256,sketch_panels[panel_id],best_sketch[panel_id],cache); query_rows+=queries
                for spec,(record,feedback) in zip(specs,evaluations):
                    pid=candidate_identity(spec); spec_by_id[pid]=spec
                    candidate_rows.append({"proposal_id":pid,"panel_id":panel_id,"lane_id":lane,"algorithm":spec.algorithm,"seed":spec.seed,"ordinal":spec.ordinal,"lane_ordinal":lane_ordinal,
                        "mechanism_id":spec.mechanism_id,"economic_hypothesis":spec.economic_hypothesis,"primitive":spec.primitive,"interaction":spec.interaction,"parent_identity":spec.parent_identity,
                        "modification_type":"single_slot_mutation" if lane=="evolutionary" and spec.parent_identity.startswith("typed-program:") else ("constraint_repair" if lane=="llm_proposal_repair" and spec.repaired else "root_proposal"),
                        "raw_template":spec.raw_template,"repaired":spec.repaired,
                        "canonical_expression":canonical_program_json(spec),"canonical_identity":program_identity(spec),"sketch_exact_identity":record.exact_identity,"activation_identity":record.activation_identity,
                        "behaviour_cluster":record.behaviour_cluster,"proxy_score_diagnostic_only":record.proxy_score,"legal":record.legal,"failure_reason":record.failure_reason,
                        "early_gate_pass":feedback["early_gate_pass"],"gate_reasons":feedback["gate_reasons"],"survivor_near_miss_score":feedback["survivor_near_miss_score"],"development_scalar":feedback["limited_scalar"],
                        "feedback_net_lcb":feedback["net_lcb"],"feedback_worst_block":feedback["worst_block"],"feedback_turnover":feedback["turnover_mean"],"feedback_benchmark_increment_lcb":feedback["benchmark_increment_lcb"],
                        "feedback_permission":"EPOCH1_RUNTIME_ONLY_NO_MEMORY_NO_PROMOTION"}); lane_ordinal+=1
            lane_runtime[(panel_id,lane)]=time.perf_counter()-lane_start
    candidates=pd.DataFrame(candidate_rows)
    behaviour_by_program = dict(zip(candidates.canonical_identity, candidates.behaviour_cluster))
    candidates["behaviour_distance_from_parent"] = [
        (float(record.behaviour_cluster != behaviour_by_program[parent]) if parent in behaviour_by_program else float("nan"))
        for parent, record in zip(candidates.parent_identity, candidates.itertuples())
    ]
    by_id=candidates.set_index("proposal_id",drop=False)
    if len(candidates)!=32768: raise ValueError("proposal budget drift")
    # Build deterministic 2x refinement pools, then compute full identities before final assignment.
    strat_pool=[]
    for (panel,lane),group in candidates[candidates.legal].groupby(["panel_id","lane_id"],sort=True):
        quota=frozen["budget"]["strict_by_lane"][lane]; strat_pool += [("STRATIFIED",pid) for pid in _round_robin_pool(group,quota*2)]
    global_pool=[]
    for panel,quota in (("main",1440),("bbo_micro",96)):
        group=candidates[(candidates.panel_id==panel)&candidates.legal].nlargest(quota*2,"development_scalar")
        global_pool += [("GLOBAL",pid) for pid in group.proposal_id]
    full_records={}
    for _,pid in strat_pool+global_pool:
        if pid in full_records: continue
        row=by_id.loc[pid]; spec=spec_by_id[pid]; panel=full_panels[row.panel_id]
        record,_=signal_record(spec,materialize_program(spec,panel),panel,np.ones(len(panel.timestamps),dtype=bool)); full_records[pid]=record
    admissions=[]; used=set(); feasibility=[]
    for (panel,lane),group in candidates.groupby(["panel_id","lane_id"],sort=True):
        quota=frozen["budget"]["strict_by_lane"][lane]; ids=[pid for arm,pid in strat_pool if arm=="STRATIFIED" and by_id.loc[pid].panel_id==panel and by_id.loc[pid].lane_id==lane]
        rows=[]
        for pid in ids:
            rec=full_records[pid]
            if (panel,rec.exact_identity) in used: continue
            base=by_id.loc[pid]
            rows.append({"proposal_id":pid,"full_exact_identity":rec.exact_identity,"mechanism_id":base.mechanism_id,"parent_identity":base.parent_identity,"behaviour_cluster":rec.behaviour_cluster,"ordinal":int(base.ordinal)})
        outcome=admit_full_identity(rows,quota)
        for rank,pid in enumerate(outcome.admitted_ids):
            rec=full_records[pid]; used.add((panel,rec.exact_identity)); admissions.append({"panel_id":panel,"lane_id":lane,"proposal_id":pid,"arm":"STRATIFIED_ADMISSION","rank":rank,"full_exact_identity":rec.exact_identity})
        feasibility.append({"panel_id":panel,"lane_id":lane,**asdict(outcome.plan),"executed":len(outcome.admitted_ids),"mechanical_underfill":len(outcome.admitted_ids)<outcome.plan.feasible_quota})
    global_ids=[]
    for panel,quota in (("main",1440),("bbo_micro",96)):
        group=[pid for arm,pid in global_pool if arm=="GLOBAL" and by_id.loc[pid].panel_id==panel]
        seen=set()
        for pid in group:
            exact=full_records[pid].exact_identity
            if exact and exact not in seen and len([x for x in global_ids if x[0]==panel])<quota:
                global_ids.append((panel,pid)); seen.add(exact)
    refs=[("STRATIFIED_ADMISSION",row["proposal_id"]) for row in admissions]+[("GLOBAL_TOP_K_CONTROL",pid) for _,pid in global_ids]
    preliminary=[]; seen_arm=set()
    for arm,pid in refs:
        base=by_id.loc[pid]; rec=full_records[pid]; key=(base.panel_id,arm,rec.exact_identity)
        if key in seen_arm: continue
        seen_arm.add(key); preliminary.append({"arm":arm,"proposal_id":pid,"panel_id":base.panel_id,"lane_id":base.lane_id,"exact_identity":rec.exact_identity,"activation_identity":rec.activation_identity,"behaviour_cluster":rec.behaviour_cluster,"economic_hypothesis":base.economic_hypothesis,"mechanism_id":base.mechanism_id,"algorithm":base.algorithm})
    prelim=pd.DataFrame(preliminary); counts=prelim.groupby(["panel_id","arm"])["behaviour_cluster"].transform("count"); same=prelim.groupby(["panel_id","arm","behaviour_cluster"])["behaviour_cluster"].transform("count"); novelty=np.log1p(counts/same)
    strict_rows=[]
    for record,nov in zip(preliminary,novelty):
        spec=spec_by_id[record["proposal_id"]]; panel=full_panels[record["panel_id"]]; weights=rank_weights(materialize_program(spec,panel))
        vector=asdict(multiobjective_evaluate(weights,panel,complexity=complexity(spec),behaviour_novelty=float(nov),benchmark_net=best_full[record["panel_id"]],cost_bps=5.0,minimum_assets=5))
        feedback=asdict(development_feedback(weights,panel,best_full[record["panel_id"]])); criteria=[vector["hard_gate_pass"],vector["ic_lcb"]>0,vector["net_lcb"]>0,vector["benchmark_incremental_lcb"]>0,vector["worst_horizon_net_mean"]>-0.001]
        strict_rows.append({**record,**vector,"development_scalar":feedback["limited_scalar"],"feedback_stability_lcb":feedback["stability_lcb"],"feedback_positive_block_fraction":feedback["positive_block_fraction"],"survivor_near_miss":sum(not x for x in criteria)==1,"development_survivor":all(criteria),"candidate_promotion":False,"feedback_persisted":False})
    strict=pd.DataFrame(strict_rows)
    pareto_rows=[]
    for (panel,arm),group in strict.groupby(["panel_id","arm"]):
        for pid in pareto_front(group.to_dict("records")): pareto_rows.append({"panel_id":panel,"arm":arm,"proposal_id":pid,"candidate_promotion":False})
    pareto=pd.DataFrame(pareto_rows); pack=strict[(strict.arm=="STRATIFIED_ADMISSION")&strict.proposal_id.isin(set(pareto.proposal_id if len(pareto) else []))].copy(); pack["pack_status"]="FROZEN_DEVELOPMENT_NO_PROMOTION"
    comparisons=[]
    for adaptive,control in MATCHED.items():
        ag=strict[(strict.arm=="STRATIFIED_ADMISSION")&(strict.lane_id==adaptive)]; cg=strict[(strict.arm=="STRATIFIED_ADMISSION")&(strict.lane_id==control)]
        ac=concentration_metrics(candidates[candidates.lane_id==adaptive]); cc=concentration_metrics(candidates[candidates.lane_id==control])
        am={"near_miss_per_strict":ag.survivor_near_miss.mean() if len(ag) else 0,"survivor_per_strict":ag.development_survivor.mean() if len(ag) else 0,"cluster_yield":ag.behaviour_cluster.nunique()/max(1,len(ag)),"top_concentration":max(ac["top_decile_mechanism_share"],ac["top_decile_primitive_share"]),"runtime_per_proposal":lane_runtime[("main",adaptive)]/2560,"benchmark_increment_median":ag.benchmark_incremental_lcb.median() if len(ag) else -999}
        cm={"near_miss_per_strict":cg.survivor_near_miss.mean() if len(cg) else 0,"survivor_per_strict":cg.development_survivor.mean() if len(cg) else 0,"cluster_yield":cg.behaviour_cluster.nunique()/max(1,len(cg)),"top_concentration":max(cc["top_decile_mechanism_share"],cc["top_decile_primitive_share"]),"runtime_per_proposal":lane_runtime[("main",control)]/2560,"benchmark_increment_median":cg.benchmark_incremental_lcb.median() if len(cg) else -999}
        comparisons.append({"adaptive_lane":adaptive,"control_lane":control,"verdict":adaptive_verdict(am,cm),**{f"adaptive_{k}":v for k,v in am.items()},**{f"control_{k}":v for k,v in cm.items()},**{f"adaptive_{k}":v for k,v in ac.items()},**{f"control_{k}":v for k,v in cc.items()}})
    adaptive_compare=pd.DataFrame(comparisons)
    lane_rows=[]
    for (panel,lane),group in candidates.groupby(["panel_id","lane_id"]):
        sg=strict[(strict.panel_id==panel)&(strict.lane_id==lane)&(strict.arm=="STRATIFIED_ADMISSION")]; vc=sg.behaviour_cluster.value_counts()
        lane_rows.append({"panel_id":panel,"lane_id":lane,"proposals":len(group),"legal_rate":group.legal.mean(),"exact_identities":group.loc[group.legal,"sketch_exact_identity"].nunique(),"strict":len(sg),"behaviour_clusters":sg.behaviour_cluster.nunique(),"n_eff":effective_count(sg.behaviour_cluster),"top_cluster_share":vc.iloc[0]/len(sg) if len(sg) else 0,"near_miss":int(sg.survivor_near_miss.sum()),"survivors":int(sg.development_survivor.sum()),"positive_net_lcb":int((sg.net_lcb>0).sum()),"runtime_seconds":lane_runtime[(panel,lane)],"failure_rate":1-group.legal.mean()})
    lane_summary=pd.DataFrame(lane_rows)
    arm_rows=[]
    for (panel,arm),group in strict.groupby(["panel_id","arm"]):
        vc=group.behaviour_cluster.value_counts(); arm_rows.append({"panel_id":panel,"arm":arm,"strict":len(group),"exact":group.exact_identity.nunique(),"clusters":group.behaviour_cluster.nunique(),"n_eff":effective_count(group.behaviour_cluster),"top1":vc.iloc[0]/len(group),"top3":vc.iloc[:3].sum()/len(group),"near_miss":int(group.survivor_near_miss.sum()),"survivors":int(group.development_survivor.sum()),"positive_net_lcb":int((group.net_lcb>0).sum()),"hypotheses":group.economic_hypothesis.nunique(),"cross_panel_ranked":False})
    arm_summary=pd.DataFrame(arm_rows)
    survivors=int(strict.development_survivor.sum()); near=int(strict.survivor_near_miss.sum()); positive_net=int((strict.net_lcb>0).sum()); adaptive_success=int((adaptive_compare.verdict=="ADAPTIVE_SUCCESS").sum()); mech_waste=bool(pd.DataFrame(feasibility).mechanical_underfill.any()); uct_row=adaptive_compare[adaptive_compare.adaptive_lane=="uct_mcts"].iloc[0]
    uct_conc=max(uct_row.adaptive_top_decile_mechanism_share,uct_row.adaptive_top_decile_primitive_share)
    if survivors>0 and positive_net>3 and adaptive_success>0 and not mech_waste:
        decision="FROZEN_DEVELOPMENT_EPOCH1_COMPLETED"; recommendation="PREPARE_ROTATING_CHALLENGE_EPOCH"
    elif near>17 or positive_net>3 or uct_conc<0.60:
        decision="FROZEN_DEVELOPMENT_EPOCH1_PARTIALLY_COMPLETED"; recommendation="REVISE_SURVIVOR_CONTRACT_WITHOUT_OOS_ACCESS" if adaptive_success>0 and positive_net>3 else "REVISE_SEARCH_ENGINE_AND_REPEAT_DEVELOPMENT_EPOCH"
    else:
        decision="FROZEN_DEVELOPMENT_EPOCH1_PARTIALLY_COMPLETED"; recommendation="REVISE_SEARCH_ENGINE_AND_REPEAT_DEVELOPMENT_EPOCH"
    tables={"raw_proposals.csv":candidates,"admission_table.csv":pd.DataFrame(admissions),"quota_feasibility.csv":pd.DataFrame(feasibility),"strict_evaluations.csv":strict,"pareto_archive.csv":pareto,"frozen_candidate_pack.csv":pack,"adaptive_vs_matched_controls.csv":adaptive_compare,"lane_summary.csv":lane_summary,"arm_summary.csv":arm_summary,"benchmark_results.csv":benchmarks,"adaptive_feedback_queries.csv":pd.DataFrame(query_rows)}
    OUTPUT_ROOT.mkdir(parents=True,exist_ok=True)
    for name,frame in tables.items(): frame.to_csv(OUTPUT_ROOT/name,index=False)
    lineage={"graph_id":"EPOCH1_LINEAGE","nodes":[{"id":row.proposal_id,"lane":row.lane_id,"modification_type":row.modification_type,"behaviour_distance_from_parent":None if pd.isna(row.behaviour_distance_from_parent) else row.behaviour_distance_from_parent} for row in candidates.itertuples()],"edges":[{"source":row.parent_identity,"target":row.proposal_id,"type":row.modification_type} for row in candidates.itertuples()],"candidate_promotion":False}; (OUTPUT_ROOT/"lineage_graph.json").write_text(json.dumps(lineage,separators=(",",":"))+"\n",encoding="utf-8")
    outputs=list(tables)+["lineage_graph.json"]
    runtime=time.perf_counter()-started
    manifest={"experiment_id":frozen["experiment_id"],"decision":decision,"recommendation":recommendation,"frozen_manifest_sha256":frozen["frozen_manifest_sha256"],"proposal_rows":len(candidates),"stratified_strict":int((strict.arm=="STRATIFIED_ADMISSION").sum()),"global_strict":int((strict.arm=="GLOBAL_TOP_K_CONTROL").sum()),"total_strict":len(strict),"development_survivors":survivors,"survivor_near_miss":near,"positive_net_lcb":positive_net,"adaptive_successes":adaptive_success,"mechanical_admission_underfill":mech_waste,"uct_top_concentration":float(uct_conc),"runtime_seconds":runtime,"outputs":[],"forward_status":"FORWARD_SEALED","candidate_promotion":False,"a7mem_updated":False,"cross_epoch_memory":False,"online_contract_changed":False,"additional_budget":False,"cross_panel_ranked":False,"oos_claim":False,"reproducibility":"FROZEN_HASHES_CONTRACTS_BUDGET_SEEDS"}
    for name in outputs: manifest["outputs"].append({"path":relative(OUTPUT_ROOT/name),"sha256":sha256_file(OUTPUT_ROOT/name)})
    RUN.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    report=["# Epoch-1 Compact Result","",f"Decision: `{decision}`",f"Recommendation: `{recommendation}`","",arm_summary.to_markdown(index=False),"",adaptive_compare.to_markdown(index=False),"","- `FORWARD_SEALED`","- `NO_CANDIDATE_PROMOTION`","- `NO_CROSS_EPOCH_ADAPTIVE_MEMORY`"]
    (OUTPUT_ROOT/"EPOCH1_COMPACT_RESULT.md").write_text("\n".join(report)+"\n",encoding="utf-8"); manifest["outputs"].append({"path":relative(OUTPUT_ROOT/"EPOCH1_COMPACT_RESULT.md"),"sha256":sha256_file(OUTPUT_ROOT/"EPOCH1_COMPACT_RESULT.md")}); RUN.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"decision":decision,"recommendation":recommendation,"proposals":len(candidates),"strict":len(strict),"survivors":survivors,"near_miss":near,"positive_net_lcb":positive_net,"adaptive_successes":adaptive_success,"runtime_seconds":runtime},indent=2)); return manifest


def check() -> None:
    frozen=verify_frozen(); run=load_json(RUN)
    if run["frozen_manifest_sha256"]!=frozen["frozen_manifest_sha256"]: raise ValueError("run/freeze mismatch")
    prohibited=("candidate_promotion","a7mem_updated","cross_epoch_memory","online_contract_changed","additional_budget","cross_panel_ranked","oos_claim")
    if any(run[key] for key in prohibited): raise PermissionError("prohibited activity")
    if run["proposal_rows"]!=32768 or run["stratified_strict"]>1536 or run["global_strict"]>1536: raise ValueError("budget mismatch")
    for item in run["outputs"]:
        if sha256_file(REPO/item["path"])!=item["sha256"]: raise ValueError(f"output drift {item['path']}")
    strict=pd.read_csv(OUTPUT_ROOT/"strict_evaluations.csv")
    if strict.groupby(["panel_id","arm"])["exact_identity"].apply(lambda x:x.duplicated().any()).any(): raise ValueError("duplicate full exact vote")
    feasible=pd.read_csv(OUTPUT_ROOT/"quota_feasibility.csv")
    bbo=feasible[feasible.panel_id=="bbo_micro"].iloc[0]
    if int(bbo.family_cap) < 96: raise ValueError("BBO dynamic family capacity regressed")
    if bbo.executed!=96 or bool(bbo.mechanical_underfill): raise ValueError("BBO mechanical underfill persists")
    print("PASS_FROZEN_DEVELOPMENT_EPOCH1_VALID")


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("action",choices=("diagnose-replay","smoke","freeze","run","check")); args=parser.parse_args()
    try:
        if args.action=="diagnose-replay": print(json.dumps(diagnose_and_replay(),indent=2))
        elif args.action=="smoke": smoke()
        elif args.action=="freeze": freeze()
        elif args.action=="run": run()
        else: check()
    except Exception as exc:
        OUTPUT_ROOT.mkdir(parents=True,exist_ok=True); FAILURE.write_text(json.dumps({"action":args.action,"status":"FAILED_VISIBLE_NOT_DELETED","error_type":type(exc).__name__,"error":str(exc),"repo_sha":git("rev-parse","HEAD",check=False),"forward_read":False,"candidate_promotion":False},indent=2)+"\n",encoding="utf-8"); raise


if __name__=="__main__": main()
