import json
import pandas as pd
import pytest
import scripts.crypto_epoch2 as e
def test_budget_and_admission_contracts():
 c=json.loads(e.CONFIG.read_text());e.validate_config(c);assert sum(e.LANES.values())==49152;assert 3*768==2304;assert sum(e.PANEL_STRICT_BUDGETS.values())==768
def test_repair_actions_are_blocker_directed():
 assert e.repair_action('COST_ONLY',0)[0]=='reduce_turnover';assert e.repair_action('NET_LCB_NEAR_ZERO',0)[0]=='improve_net_lcb';assert e.repair_action('BENCHMARK_INCREMENT_ONLY',0)[0]=='orthogonalize_benchmark'
def test_matched_repair_lanes_have_equal_budgets():
 assert e.LANES['local_mcts_repair']==e.LANES['local_mcts_random_control'];assert abs(e.LANES['evolutionary_repair']-e.LANES['evolutionary_random_control'])<=1;assert abs(e.LANES['llm_typed_repair']-e.LANES['llm_random_repair_control'])<=1

def test_survivor_flags_use_frozen_contract():
 row={'hard_gate_pass':True,'ic_lcb':.01,'net_lcb':.001,'benchmark_incremental_lcb':.0001,'worst_horizon_net_mean':-.0009}
 gates,survivor,near=e.survivor_flags(row)
 assert survivor and not near and all(gates.values())
 row['net_lcb']=-1e-9
 gates,survivor,near=e.survivor_flags(row)
 assert not survivor and near and not gates['NET_LCB']

def test_blocker_distance_is_signed_and_gate_specific():
 row={'hard_gate_pass':True,'ic_lcb':.01,'net_lcb':-.0002,'benchmark_incremental_lcb':.0003,'worst_horizon_net_mean':-.0008,'max_weight_mean':.20}
 assert e.blocker_distance(row,'COST_ONLY')==-.0002
 assert e.blocker_distance(row,'BENCHMARK_INCREMENT_ONLY')==.0003
 assert e.blocker_distance(row,'STABILITY_ONLY')==pytest.approx(.0002)
 assert e.blocker_distance(row,'CONCENTRATION_ONLY')==pytest.approx(.05)

def test_cem_diagnostic_requires_early_gate_eligibility_and_never_selects():
 rows=[]
 for ordinal in range(4):
  rows.append({'proposal_id':str(ordinal),'lane_id':'lane','seed':e.SEEDS[ordinal%2],'legal':True,'early_gate_pass':ordinal!=0,'sketch_net_lcb':0.,'sketch_positive_block_fraction':.5,'sketch_turnover_mean':1.,'near_score':ordinal,'quality':ordinal,'mechanism_id':'m','primitive':f'p{ordinal}','repair_action':'a'})
 result=e.cem_diagnostic(pd.DataFrame(rows))
 assert result.early_gate_eligible_rows.sum()==3
 assert not result.selection_used.any() and not result.separate_budget.any()

def test_surrogate_diagnostic_is_seed_cross_fit_and_not_selection():
 rows=[]
 for seed in e.SEEDS:
  for ordinal in range(2):
   rows.append({'proposal_id':f'{seed}-{ordinal}','admission_policy':'P','seed':seed,'mechanism_id':'m','repair_action':'a','hard_gate_pass':True,'net_lcb':.1 if ordinal else -.1,'ic_lcb':.1,'benchmark_incremental_lcb':.1,'worst_horizon_net_mean':0.})
 result=e.surrogate_crossfit(pd.DataFrame(rows))
 assert len(result)==4 and set(result.test_seed)==set(e.SEEDS)
 assert not result.selection_used.any()

def test_local_mcts_ucb_has_exploration_floor_and_no_majority_action():
 state={};feedback={'survivor_near_miss_score':1.,'net_lcb':0.,'benchmark_increment_lcb':0.}
 for _ in range(60):
  action=e.select_local_mcts_action(state,'NET_LCB_NEAR_ZERO')
  e.update_local_mcts(state,'NET_LCB_NEAR_ZERO',action,feedback)
 visits=state['NET_LCB_NEAR_ZERO']['visits']
 assert min(visits)>0 and max(visits)/sum(visits)<.50
