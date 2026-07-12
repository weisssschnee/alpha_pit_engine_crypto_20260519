from __future__ import annotations

import hashlib, json, math, subprocess, sys
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path: sys.path.insert(0, str(REPO))
import scripts.crypto_nextgen_epoch0 as epoch0
from alphafactory_crypto.b1s_canary import FrozenPanel, rank_weights
from alphafactory_crypto.nextgen_epoch import multiobjective_evaluate

ROOT = REPO / "runtime/epoch2_calibration_20260712"
ROWS = ROOT / "survivor_contract_calibration.csv"
MANIFEST = ROOT / "calibration_manifest.json"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def survivor(v: dict) -> tuple[bool, list[str]]:
    gates = {"hard_gate": bool(v["hard_gate_pass"]), "ic_lcb": v["ic_lcb"] > 0, "net_lcb": v["net_lcb"] > 0,
             "benchmark_increment": v["benchmark_incremental_lcb"] > 0, "worst_block": v["worst_horizon_net_mean"] > -0.001}
    return all(gates.values()), [key for key, value in gates.items() if not value]

def evaluate(control_id: str, category: str, weights: np.ndarray, panel: FrozenPanel, benchmark: np.ndarray, metadata: dict) -> dict:
    vector = asdict(multiobjective_evaluate(weights, panel, complexity=1, behaviour_novelty=0.0, benchmark_net=benchmark, cost_bps=5.0, minimum_assets=5))
    passed, failed = survivor(vector)
    thresholds = {"ic_lcb": 0.0, "net_lcb": 0.0, "benchmark_incremental_lcb": 0.0, "worst_horizon_net_mean": -0.001}
    return {"control_id": control_id, "category": category, **metadata, **vector, "survivor_pass": passed,
            "failed_gates": "|".join(failed), **{f"distance_{key}": vector[key]-value for key, value in thresholds.items()},
            "feedback_permission": "CALIBRATION_ONLY_NO_GENERATOR_MEMORY_CANDIDATE_OR_PROMOTION"}

def synthetic_panel(main: FrozenPanel, seed: int = 4202) -> tuple[FrozenPanel, np.ndarray]:
    rng = np.random.default_rng(seed); n, t = len(main.symbols), len(main.timestamps)
    latent = np.empty((n, t)); latent[:, 0] = rng.normal(size=n)
    for i in range(1, t): latent[:, i] = .97 * latent[:, i-1] + rng.normal(0, .25, n)
    cross = latent - latent.mean(axis=0, keepdims=True); cross /= np.maximum(cross.std(axis=0, keepdims=True), 1e-9)
    target = .0012 * cross + rng.normal(0, .0008, (n, t))
    panel = replace(main, panel_id="synthetic_calibration", fields={}, target_return=target, comparison_domain="CALIBRATION_ONLY")
    return panel, cross

def run() -> dict:
    ROOT.mkdir(parents=True, exist_ok=True); main = epoch0.load_main_panel(); synth, edge = synthetic_panel(main)
    rng = np.random.default_rng(4203); zero = np.zeros(len(main.timestamps)); records=[]
    planted = {
        "stable_weak_edge": edge, "cost_positive_portfolio": edge * 1.5,
        "cross_block_injected": edge + .15*np.sin(np.arange(edge.shape[1])/168)[None,:],
        "low_turnover": np.repeat(edge[:, ::24], 24, axis=1)[:, :edge.shape[1]],
        "moderate_concentration": edge + .25*np.eye(edge.shape[0])[:, [0]],
    }
    for name, signal in planted.items(): records.append(evaluate(name,"PLANTED_POSITIVE",rank_weights(signal),synth,zero,{"discovery_status":"synthetic_calibration"}))
    nulls = {
        "shuffled_signal": edge[:, rng.permutation(edge.shape[1])], "delayed_wrong_lag": np.roll(edge, 168, axis=1),
        "random_rank": rng.normal(size=edge.shape), "random_sparse_event": np.where(rng.random(edge.shape)<.05,rng.normal(size=edge.shape),np.nan),
        "sign_flipped": -edge,
    }
    for name, signal in nulls.items(): records.append(evaluate(name,"NULL_CONTROL",rank_weights(signal),synth,zero,{"discovery_status":"null_calibration"}))
    benchmark_signals = epoch0._benchmark_signals(main); _, best = epoch0._run_benchmarks({"main":main},5.0,5)
    for name in ("simple_funding","simple_basis","simple_oi","momentum","reversal","volatility","liquidity","session_time_of_day"):
        records.append(evaluate(name,"SIMPLE_REAL_BENCHMARK",rank_weights(benchmark_signals[name]),main,best["main"],{"discovery_status":"reproduction"}))
    frame=pd.DataFrame(records); frame.to_csv(ROWS,index=False)
    planted_pass=float(frame[frame.category=="PLANTED_POSITIVE"].survivor_pass.mean()); null_pass=float(frame[frame.category=="NULL_CONTROL"].survivor_pass.mean())
    decision="SURVIVOR_CONTRACT_CALIBRATED_REACHABLE" if planted_pass>=.8 and null_pass<=.2 else "SURVIVOR_CONTRACT_CALIBRATION_FAILED_STOP_SEARCH"
    manifest={"experiment_id":"20260712_epoch2_survivor_calibration_001","decision":decision,"repo_sha":subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO,text=True).strip(),
              "rows":len(frame),"planted_pass_rate":planted_pass,"null_pass_rate":null_pass,"table":str(ROWS.relative_to(REPO)).replace('\\','/'),"table_sha256":sha(ROWS),
              "data_access":"DEVELOPMENT_AND_SYNTHETIC_CALIBRATION_ONLY","oos_grade":"NONE","strict_search_started":False,"candidate_promotion":False,"memory_updated":False,"forward_read":False,
              "cost_bps":5.0,"reproducibility":"FIXED_SEEDS_AND_HASHED_OUTPUT","continuation":"proceed to frozen near-miss taxonomy only if decision is reachable"}
    MANIFEST.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8"); print(json.dumps(manifest,indent=2)); return manifest

if __name__=="__main__": run()
