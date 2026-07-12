from __future__ import annotations
import argparse,gzip,hashlib,io,json,math,subprocess,sys,time
from collections import Counter,defaultdict,deque
from dataclasses import asdict,replace
from pathlib import Path
from typing import Any,Iterable,Mapping
import numpy as np,pandas as pd
REPO=Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:sys.path.insert(0,str(REPO))
import scripts.crypto_nextgen_epoch0 as epoch0
import scripts.crypto_nextgen_epoch1 as epoch1
import scripts.crypto_nextgen_epoch1r as epoch1r
from alphafactory_crypto.b1s_canary import rank_weights
from alphafactory_crypto.nextgen_epoch import ProgramSpec,candidate_identity,canonical_program_json,complexity,effective_count,make_program,materialize_program,multiobjective_evaluate,mutate_program,pareto_front,program_identity,signal_record
from alphafactory_crypto.search_revision import development_feedback,normalized_entropy
CONFIG=REPO/'config/crypto_epoch2_v1.json'; CAL=REPO/'runtime/epoch2_calibration_20260712/calibration_manifest.json'; TAX=REPO/'runtime/epoch2_calibration_20260712/taxonomy_manifest.json'; PARENTS=REPO/'runtime/epoch2_calibration_20260712/frozen_near_miss_parent_pack.csv'
ROOT=REPO/'runtime/epoch2_20260712'; FROZEN=ROOT/'epoch2_frozen_manifest.json'; RUN=ROOT/'epoch2_run_manifest.json'; FAILURE=ROOT/'epoch2_failure.json'; PACK=ROOT/'proposal_pack.jsonl.gz'; ASSIGN=ROOT/'admission_assignments.csv'; STRICT=ROOT/'strict_evaluations.csv'
LANES={'evolutionary_repair':8602,'evolutionary_random_control':8601,'local_mcts_repair':4915,'local_mcts_random_control':4915,'llm_typed_repair':3687,'llm_random_repair_control':3686,'typed_random_fresh':4915,'typed_ast_fresh':4915,'orthogonal_exile_fresh':4916}
POLICIES=('GLOBAL_QUALITY','STRATIFIED_DIVERSITY','HYBRID_QUALITY_DIVERSITY'); SEEDS=(5201,5209)
PANEL_STRICT_BUDGETS={'main':744,'bbo_micro':24}
MATCHED_REPAIR_LANES=(
 ('evolutionary_repair','evolutionary_random_control'),
 ('local_mcts_repair','local_mcts_random_control'),
 ('llm_typed_repair','llm_random_repair_control'),
)
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
 d=hashlib.sha256()
 with p.open('rb') as h:
  for c in iter(lambda:h.read(1048576),b''):d.update(c)
 return d.hexdigest().upper()
def payload(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest().upper()
def git(*a):return subprocess.check_output(['git',*a],cwd=REPO,text=True).strip()
def rel(p):return str(p.relative_to(REPO)).replace('\\','/')
def write_gz(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('wb') as raw:
  with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as z:
   with io.TextIOWrapper(z,encoding='utf-8',newline='\n') as t:
    for r in rows:t.write(json.dumps(r,sort_keys=True,separators=(',',':'),default=str)+'\n')
def read_gz(path):
 with gzip.open(path,'rt',encoding='utf-8') as h:return [json.loads(x) for x in h if x.strip()]
def validate_config(c):
 assert c['proposal_budget']==49152 and sum(c['proposal_mix'].values())==49152 and sum(LANES.values())==49152
 assert c['strict_budget']==2304 and c['strict_budget_per_admission_policy']==768 and tuple(c['fixed_seeds'])==SEEDS
 assert c['admission_policies']['HYBRID_QUALITY_DIVERSITY']=={'quality_share':.6,'diversity_share':.4}
 assert sum(PANEL_STRICT_BUDGETS.values())==768
 assert c['panel_strict_budget_per_policy']==PANEL_STRICT_BUDGETS
 assert c['matched_repair_controls']==dict(MATCHED_REPAIR_LANES)
def repair_action(blocker,ordinal):
 if blocker=='COST_ONLY':return ('reduce_turnover','window',(24,48,72,168)[ordinal%4])
 if blocker=='NET_LCB_NEAR_ZERO':return ('improve_net_lcb','interaction',('none','residual','condition')[ordinal%3])
 if blocker=='BENCHMARK_INCREMENT_ONLY':return ('orthogonalize_benchmark','interaction','residual')
 return ('typed_random_repair','primitive',None)

def survivor_flags(row):
 """Return the frozen survivor gates without changing their thresholds."""
 gates={
  'HARD_GATE':bool(row['hard_gate_pass']),
  'IC_LCB':float(row['ic_lcb'])>0,
  'NET_LCB':float(row['net_lcb'])>0,
  'BENCHMARK_INCREMENT':float(row['benchmark_incremental_lcb'])>0,
  'WORST_BLOCK':float(row['worst_horizon_net_mean'])>-.001,
 }
 return gates,all(gates.values()),sum(not value for value in gates.values())==1

def failed_gates(row):
 gates,_,_=survivor_flags(row)
 return '|'.join(key for key,value in gates.items() if not value)

def blocker_distance(row,blocker):
 """Signed distance to the parent blocker: positive means the gate is passed."""
 if blocker=='BENCHMARK_INCREMENT_ONLY':return float(row['benchmark_incremental_lcb'])
 if blocker in {'COST_ONLY','NET_LCB_NEAR_ZERO'}:return float(row['net_lcb'])
 if blocker=='STABILITY_ONLY':return float(row['worst_horizon_net_mean'])+.001
 if blocker=='CONCENTRATION_ONLY':return .25-float(row['max_weight_mean'])
 if blocker=='STRUCTURAL_UNREPAIRABLE':return 1. if bool(row['hard_gate_pass']) else -1.
 return min(float(row['ic_lcb']),float(row['net_lcb']),float(row['benchmark_incremental_lcb']),float(row['worst_horizon_net_mean'])+.001)

def mcts_action_count(blocker):
 return 4 if blocker=='COST_ONLY' else (3 if blocker=='NET_LCB_NEAR_ZERO' else 1)

def select_local_mcts_action(state,blocker):
 """Frozen UCB rule with an exploration floor and a <50% root-action cap."""
 count=mcts_action_count(blocker);slot=state.setdefault(blocker,{'visits':[0]*count,'value':[0.]*count})
 total=sum(slot['visits'])
 unvisited=[index for index,visits in enumerate(slot['visits']) if visits==0]
 if unvisited:return unvisited[0]
 cap=max(1,math.ceil((total+1)*.45))
 eligible=[index for index,visits in enumerate(slot['visits']) if visits<cap] or list(range(count))
 return max(eligible,key=lambda index:(slot['value'][index]/slot['visits'][index]+1.2*math.sqrt(math.log(total+1)/slot['visits'][index]),-index))

def update_local_mcts(state,blocker,index,feedback):
 slot=state[blocker];slot['visits'][index]+=1
 target=feedback['benchmark_increment_lcb'] if blocker=='BENCHMARK_INCREMENT_ONLY' else feedback['net_lcb']
 slot['value'][index]+=float(feedback['survivor_near_miss_score'])+1000.*float(np.nan_to_num(target,nan=-.01))

def local_mcts_state_frame(state):
 rows=[]
 for blocker,slot in sorted(state.items()):
  total=sum(slot['visits'])
  for index,(visits,value) in enumerate(zip(slot['visits'],slot['value'])):
   action,parameter,choice=repair_action(blocker,index)
   rows.append({'blocker_type':blocker,'action_index':index,'action':action,'parameter':parameter,'choice':choice,'visits':visits,'root_visit_share':visits/max(1,total),'mean_gate_directed_value':value/max(1,visits),'policy_persisted':False})
 return pd.DataFrame(rows)
def apply_repair(parent,registry,lane,seed,ordinal,blocker,random_control=False,action_index=None):
 child=mutate_program(replace(parent,lane_id=lane,algorithm=lane),registry,seed=seed,ordinal=ordinal)
 action,slot,value=repair_action(blocker,ordinal if action_index is None else action_index)
 if random_control:action='random_mutation_control';return child,action
 if slot=='window':
  w=int(value);child=replace(child,window=w,long_window=max(w+1,168 if w<168 else 336),parent_identity=program_identity(parent))
 elif slot=='interaction':child=replace(child,interaction=str(value),parent_identity=program_identity(parent))
 return child,f'{action}:{slot}={value}'
def parent_specs():
 rows=read_gz(epoch1r.PACK);specs={x['proposal_id']:ProgramSpec(**x['spec']) for x in rows};parents=pd.read_csv(PARENTS)
 usable=parents[parents.blocker_type!='STRUCTURAL_UNREPAIRABLE'].copy();return usable,specs
def generate_spec(lane,ordinal,seed,registry,parents,specs,mcts_action_index=None):
 if lane in {'typed_random_fresh','typed_ast_fresh','orthogonal_exile_fresh'}:
  base='orthogonal_exile' if lane=='orthogonal_exile_fresh' else ('typed_ast' if lane=='typed_ast_fresh' else 'typed_random')
  spec=make_program(registry,lane_id=base,panel_id='main',algorithm=lane,seed=seed,ordinal=ordinal)
  return replace(spec,lane_id=lane,lineage_namespace=f'runtime_only/epoch2/{lane}/seed_{seed}'),'', 'FRESH'
 parent_row=parents.iloc[ordinal%len(parents)];parent=specs[parent_row.proposal_id]
 random_control=lane.endswith('control')
 spec,action=apply_repair(parent,registry,lane,seed,ordinal,str(parent_row.blocker_type),random_control,mcts_action_index)
 if lane=='local_mcts_repair':
  # Multi-step typed repair, with deterministic action exploration floor.
  second_index=None if mcts_action_index is None else mcts_action_index+1
  spec,second_action=apply_repair(spec,registry,lane,seed+17,ordinal+1,str(parent_row.blocker_type),False,second_index);action=f'mcts_two_step:{action}->{second_action}'
 if lane=='llm_typed_repair':
  distance=parent_row.distance_benchmark_increment if str(parent_row.blocker_type)=='BENCHMARK_INCREMENT_ONLY' else parent_row.distance_net_lcb
  prompt=f'current={canonical_program_json(parent)};failed_gate={parent_row.failed_gate};blocker_distance={distance};allowed=window,interaction,primitive,threshold,direction;forbidden=unapproved_fields,new_data_permissions,reward_only_request'
  action='llm_typed_'+action;spec=replace(spec,repaired=True,raw_template=prompt)
 return spec,str(parent_row.frozen_parent_row_id),action
def evaluate_sketch(spec,panel,benchmark,cache):
 key=(panel.panel_id,canonical_program_json(spec))
 if key not in cache:
  try:
   rec,w=signal_record(spec,materialize_program(spec,panel),panel,np.ones(len(panel.timestamps),bool));fb=asdict(development_feedback(w,panel,benchmark));cache[key]=(rec,fb)
  except Exception as e:cache[key]=(None,{'limited_scalar':-999.,'survivor_near_miss_score':0.,'early_gate_pass':False,'gate_reasons':type(e).__name__})
 return cache[key]
def freeze():
 c=load(CONFIG);validate_config(c);cal=load(CAL);tax=load(TAX)
 if cal['decision']!='SURVIVOR_CONTRACT_CALIBRATED_REACHABLE' or cal['planted_pass_rate']<.8 or cal['null_pass_rate']>.2:raise RuntimeError('calibration gate failed')
 if tax['parent_rows']!=84:raise RuntimeError('parent pack drift')
 if subprocess.run(['git','diff','--quiet'],cwd=REPO).returncode:raise RuntimeError('freeze requires committed implementation')
 files=[CONFIG,CAL,TAX,PARENTS,REPO/'alphafactory_crypto/nextgen_epoch.py',REPO/'alphafactory_crypto/search_revision.py',Path(__file__),REPO/'tests/test_epoch2.py',ROOT/'epoch2_implementation_test_output.txt']
 m={'experiment_id':'20260712_crypto_epoch2_001','status':'EPOCH2_DESIGN_FROZEN_NOT_STARTED','repo_sha':git('rev-parse','HEAD'),'inputs_sha256':{rel(p):sha(p) for p in files},'calibration':cal,'taxonomy':tax,'proposal_budget':49152,'lane_budgets':LANES,'fixed_seeds':list(SEEDS),'strict_budget':2304,'strict_per_policy':768,'panel_strict_budget_per_policy':PANEL_STRICT_BUDGETS,'admission_policies':c['admission_policies'],'hybrid_ratio':'60_QUALITY_40_DIVERSITY','shared_exact_evaluation_cache':True,'cost_bps':5.0,'survivor_contract':'hard_gate AND ic_lcb>0 AND net_lcb>0 AND benchmark_increment_lcb>0 AND worst_block>-0.001','benchmark_contract':'Epoch-1R frozen simple development benchmarks; panels remain separately ranked','diagnostic_components':{'cem':'early_gate_eligible_elite_only_no_separate_budget','surrogate':'fixed_two_seed_cross_fit_no_selection_use'},'mcts_contract':'local_two_step_blocker_repair_with_deterministic_action_exploration_floor_and_matched_random_control','estimated_runtime_seconds':5400,'oos_grade':'NONE','bias_audit':'HOLD_RESEARCH','performance_started':False,'forward_read':False,'candidate_promotion':False,'cross_epoch_memory':False,'online_change':False}
 m['frozen_manifest_sha256']=payload(m);ROOT.mkdir(parents=True,exist_ok=True);FROZEN.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf-8');print(json.dumps({'status':m['status'],'sha':m['frozen_manifest_sha256'],'repo':m['repo_sha']},indent=2))
def verify():
 m=load(FROZEN);x=m.pop('frozen_manifest_sha256');assert payload(m)==x;m['frozen_manifest_sha256']=x
 for p,h in m['inputs_sha256'].items():assert sha(REPO/p)==h
 return m
def diversity_order(df):
 buckets={k:deque(g.sort_values(['near_score','quality','proposal_id'],ascending=[False,False,True]).proposal_id) for k,g in df.groupby(['mechanism_id','behaviour_cluster'],sort=True)};out=[]
 while any(buckets.values()):
  for k in sorted(buckets):
   if buckets[k]:out.append(buckets[k].popleft())
 return out

def proposal_role_diagnostics(df):
 rows=[]
 for lane,group in df.groupby('lane_id',sort=True):
  legal=group[group.legal]
  mechanism_share=legal.mechanism_id.value_counts(normalize=True)
  primitive_share=legal.primitive.value_counts(normalize=True)
  action_share=legal.repair_action.value_counts(normalize=True)
  rows.append({
   'component':'PROPOSAL_ROLE','lane_id':lane,'proposal_rows':len(group),
   'legal_rate':float(group.legal.mean()),
   'mechanism_entropy':normalized_entropy(legal.mechanism_id),
   'primitive_entropy':normalized_entropy(legal.primitive),
   'action_entropy':normalized_entropy(legal.repair_action),
   'top_mechanism_share':float(mechanism_share.iloc[0]) if len(mechanism_share) else 0.,
   'top_primitive_share':float(primitive_share.iloc[0]) if len(primitive_share) else 0.,
   'top_action_share':float(action_share.iloc[0]) if len(action_share) else 0.,
   'selection_used':False,
  })
 return pd.DataFrame(rows)

def cem_diagnostic(df):
 """Diagnostic exploit view only; it consumes no proposal or strict budget."""
 eligible=df[
  df.legal & df.early_gate_pass & (df.sketch_net_lcb>-.00010) &
  (df.sketch_positive_block_fraction>=.40) & (df.sketch_turnover_mean<=1.20)
 ].copy()
 rows=[]
 for (lane,seed),source in df.groupby(['lane_id','seed'],sort=True):
  pool=eligible[(eligible.lane_id==lane)&(eligible.seed==seed)]
  elite=pool.sort_values(['near_score','quality','proposal_id'],ascending=[False,False,True]).head(max(1,math.ceil(len(pool)*.10))) if len(pool) else pool
  ms=elite.mechanism_id.value_counts(normalize=True);ps=elite.primitive.value_counts(normalize=True)
  rows.append({
   'component':'CEM_DIAGNOSTIC','lane_id':lane,'seed':seed,'source_rows':len(source),
   'early_gate_eligible_rows':len(pool),'elite_rows':len(elite),
   'elite_top_mechanism_share':float(ms.iloc[0]) if len(ms) else 0.,
   'elite_top_primitive_share':float(ps.iloc[0]) if len(ps) else 0.,
   'elite_mechanism_entropy':normalized_entropy(elite.mechanism_id),
   'elite_primitive_entropy':normalized_entropy(elite.primitive),
   'separate_budget':False,'selection_used':False,
  })
 return pd.DataFrame(rows)

def surrogate_crossfit(strict):
 """Two-seed cross-fit of feasibility targets; never used by admission or evaluation."""
 unique=strict.sort_values(['proposal_id','admission_policy']).drop_duplicates('proposal_id').copy()
 unique['gate_feasible']=(unique.hard_gate_pass & (unique.net_lcb>0)).astype(float)
 unique['near_distance']=unique[['ic_lcb','net_lcb','benchmark_incremental_lcb']].min(axis=1)
 unique['pareto_feasible']=(unique.hard_gate_pass & (unique.net_lcb>-.00010) & (unique.benchmark_incremental_lcb>-.00010) & (unique.worst_horizon_net_mean>-.001)).astype(float)
 predictions=[]
 targets=('gate_feasible','near_distance','pareto_feasible')
 for test_seed in SEEDS:
  train=unique[unique.seed!=test_seed];test=unique[unique.seed==test_seed]
  global_means={target:float(train[target].mean()) if len(train) else 0. for target in targets}
  grouped=train.groupby(['mechanism_id','repair_action'],dropna=False)[list(targets)].agg(['mean','count'])
  for row in test.itertuples():
   key=(row.mechanism_id,row.repair_action)
   record={'proposal_id':row.proposal_id,'test_seed':test_seed,'mechanism_id':row.mechanism_id,'repair_action':row.repair_action,'selection_used':False}
   for target in targets:
    if key in grouped.index:
     mean=float(grouped.loc[key,(target,'mean')]);count=int(grouped.loc[key,(target,'count')])
    else:mean=global_means[target];count=len(train)
    uncertainty=math.sqrt(max(0.,mean*(1.-mean))/max(1,count)) if target!='near_distance' else float(train[target].std(ddof=0)/math.sqrt(max(1,count)))
    record[f'predicted_{target}']=mean;record[f'uncertainty_{target}']=uncertainty;record[f'actual_{target}']=float(getattr(row,target))
   predictions.append(record)
 return pd.DataFrame(predictions)
def run():
 f=verify();started=time.perf_counter();registry=epoch1.load_json(epoch1.MECHANISMS);parents,specmap=parent_specs()
 main=epoch0.load_main_panel();bbo=epoch0.load_bbo_panel(main);panels={'main':main,'bbo_micro':bbo}
 sketch_panels={key:epoch0.sketch_panel(panel,4) for key,panel in panels.items()}
 _,best=epoch0._run_benchmarks(panels,5.,5);sketch_bench={key:value[::4] for key,value in best.items()}
 cache={};rows=[];specs={};mcts_state={}
 for lane,count in LANES.items():
  for i in range(count):
   seed=SEEDS[i%2];ordinal=i//2;mcts_index=None;mcts_blocker=None
   if lane=='local_mcts_repair':
    mcts_blocker=str(parents.iloc[ordinal%len(parents)].blocker_type);mcts_index=select_local_mcts_action(mcts_state,mcts_blocker)
   spec,parent,action=generate_spec(lane,ordinal,seed,registry,parents,specmap,mcts_index);pid=candidate_identity(spec)
   panel=sketch_panels[spec.panel_id];rec,fb=evaluate_sketch(spec,panel,sketch_bench[spec.panel_id],cache);specs[pid]=spec
   if lane=='local_mcts_repair':update_local_mcts(mcts_state,mcts_blocker,mcts_index,fb)
   rows.append({
    'proposal_id':pid,'panel_id':spec.panel_id,'lane_id':lane,'seed':seed,'ordinal':ordinal,
    'parent_row_id':parent,'repair_action':action,'mechanism_id':spec.mechanism_id,
    'primitive':spec.primitive,'hypothesis':spec.economic_hypothesis,
    'canonical':canonical_program_json(spec),'legal':bool(rec and rec.legal),
    'sketch_exact':rec.exact_identity if rec else '',
    'behaviour_cluster':rec.behaviour_cluster if rec else '',
    'quality':fb['limited_scalar'],'near_score':fb['survivor_near_miss_score'],
    'early_gate_pass':fb['early_gate_pass'],'gate_reasons':fb['gate_reasons'],
    'sketch_net_lcb':fb.get('net_lcb',float('nan')),
    'sketch_worst_block':fb.get('worst_block',float('nan')),
    'sketch_positive_block_fraction':fb.get('positive_block_fraction',0.),
    'sketch_turnover_mean':fb.get('turnover_mean',float('inf')),
    'sketch_benchmark_increment_lcb':fb.get('benchmark_increment_lcb',float('nan')),
    'spec':asdict(spec),
   })
 if len(rows)!=49152:raise ValueError('proposal drift')
 write_gz(PACK,rows)
 df=pd.DataFrame([{k:v for k,v in row.items() if k!='spec'} for row in rows])
 role_diagnostic=proposal_role_diagnostics(df);role_diagnostic.to_csv(ROOT/'search_role_diagnostics.csv',index=False)
 cem=cem_diagnostic(df);cem.to_csv(ROOT/'cem_diagnostic.csv',index=False)
 mcts_visits=local_mcts_state_frame(mcts_state);mcts_visits.to_csv(ROOT/'local_mcts_root_visits.csv',index=False)

 # Rank main and scoped BBO separately; the short BBO panel never competes with the main panel.
 full={};assign=[]
 for panel_id,panel_quota in PANEL_STRICT_BUDGETS.items():
  legal=df[(df.panel_id==panel_id)&df.legal].copy()
  quality=list(legal.sort_values(['near_score','quality','proposal_id'],ascending=[False,False,True]).proposal_id)
  diversity=diversity_order(legal)
  for policy in POLICIES:
   quality_count=round(panel_quota*.60) if policy=='HYBRID_QUALITY_DIVERSITY' else (panel_quota if policy=='GLOBAL_QUALITY' else 0)
   source=(quality[:quality_count]+[pid for pid in diversity if pid not in set(quality[:quality_count])]) if policy=='HYBRID_QUALITY_DIVERSITY' else (quality if policy=='GLOBAL_QUALITY' else diversity)
   seen=set();selected=[]
   for pid in source:
    if len(selected)>=panel_quota:break
    if pid not in full:
     spec=specs[pid];record,_=signal_record(spec,materialize_program(spec,panels[panel_id]),panels[panel_id],np.ones(len(panels[panel_id].timestamps),bool));full[pid]=record
    exact=full[pid].exact_identity
    if exact and exact not in seen:seen.add(exact);selected.append(pid)
   if len(selected)!=panel_quota:raise RuntimeError(f'natural identity underfill before strict: {panel_id}/{policy}={len(selected)}/{panel_quota}')
   for rank,pid in enumerate(selected):
    record=full[pid]
    assign.append({'admission_policy':policy,'panel_id':panel_id,'proposal_id':pid,'rank':rank,'exact_identity':record.exact_identity,'activation_identity':record.activation_identity,'full_behaviour_cluster':record.behaviour_cluster})
 assignments=pd.DataFrame(assign);assignments.to_csv(ASSIGN,index=False)

 proposal_base=df.set_index('proposal_id').to_dict('index');strict_cache={};strict_rows=[]
 for assignment in assignments.itertuples():
  pid=assignment.proposal_id;spec=specs[pid];panel=panels[assignment.panel_id]
  cache_key=(assignment.panel_id,assignment.exact_identity)
  if cache_key not in strict_cache:
   weights=rank_weights(materialize_program(spec,panel))
   vector=asdict(multiobjective_evaluate(weights,panel,complexity=complexity(spec),behaviour_novelty=0.,benchmark_net=best[assignment.panel_id],cost_bps=5.,minimum_assets=5))
   feedback=asdict(development_feedback(weights,panel,best[assignment.panel_id]))
   _,survivor,near_miss=survivor_flags(vector)
   strict_cache[cache_key]={
    **vector,'development_scalar':feedback['limited_scalar'],
    'feedback_stability_lcb':feedback['stability_lcb'],
    'feedback_positive_block_fraction':feedback['positive_block_fraction'],
    'survivor':survivor,'near_miss':near_miss,'failed_gates':failed_gates(vector),
   }
  strict_rows.append({
   'admission_policy':assignment.admission_policy,'exact_identity':assignment.exact_identity,
   'activation_identity':assignment.activation_identity,'full_behaviour_cluster':assignment.full_behaviour_cluster,
   **proposal_base[pid],**strict_cache[cache_key],
  })
 strict=pd.DataFrame(strict_rows);strict.to_csv(STRICT,index=False)

 # Parent -> child blocker change is reported separately from scalar change.
 parent_lookup=parents.set_index('frozen_parent_row_id').to_dict('index');attribution=[]
 for row in strict[strict.parent_row_id!=''].to_dict('records'):
  parent=parent_lookup[row['parent_row_id']];blocker=str(parent['blocker_type'])
  before=blocker_distance(parent,blocker);after=blocker_distance(row,blocker)
  attribution.append({
   'admission_policy':row['admission_policy'],'proposal_id':row['proposal_id'],'lane_id':row['lane_id'],
   'parent_row_id':row['parent_row_id'],'repair_action':row['repair_action'],'blocker_type':blocker,
   'parent_failed_gate':parent['failed_gate'],'child_failed_gates':row['failed_gates'],
   'blocker_distance_before':before,'blocker_distance_after':after,'blocker_distance_delta':after-before,
   'target_gate_improved':after>before,'target_gate_passed':after>0,
   'parent_scalar':float(parent['development_scalar']),'child_scalar':float(row['development_scalar']),
   'scalar_improved':float(row['development_scalar'])>float(parent['development_scalar']),
   'survivor':row['survivor'],'near_miss':row['near_miss'],
  })
 attribution_frame=pd.DataFrame(attribution);attribution_frame.to_csv(ROOT/'repair_child_attribution.csv',index=False)
 lineage=attribution_frame.groupby(['lane_id','repair_action'],sort=True).agg(
  children=('proposal_id','count'),survivors=('survivor','sum'),near_misses=('near_miss','sum'),
  blocker_improvement_rate=('target_gate_improved','mean'),target_gate_pass_rate=('target_gate_passed','mean'),
  blocker_distance_delta_median=('blocker_distance_delta','median'),scalar_improvement_rate=('scalar_improved','mean'),
 ).reset_index();lineage.to_csv(ROOT/'repair_lineage_attribution.csv',index=False)

 surrogate=surrogate_crossfit(strict);surrogate.to_csv(ROOT/'surrogate_crossfit_diagnostic.csv',index=False)
 policy_rows=[]
 for policy_name,group in strict.groupby('admission_policy',sort=True):
  counts=group.full_behaviour_cluster.value_counts()
  policy_rows.append({'admission_policy':policy_name,'rows':len(group),'exact_identities':group.exact_identity.nunique(),'survivors':int(group.survivor.sum()),'near_misses':int(group.near_miss.sum()),'positive_net_lcb':int((group.net_lcb>0).sum()),'behaviour_clusters':group.full_behaviour_cluster.nunique(),'n_eff':effective_count(group.full_behaviour_cluster),'top_cluster_share':float(counts.iloc[0]/len(group)),'hypotheses':group.hypothesis.nunique(),'mechanisms':group.mechanism_id.nunique()})
 policy=pd.DataFrame(policy_rows);policy.to_csv(ROOT/'admission_policy_comparison.csv',index=False)
 lane_rows=[]
 for lane_name,group in strict.groupby('lane_id',sort=True):
  counts=group.full_behaviour_cluster.value_counts()
  lane_rows.append({'lane_id':lane_name,'rows':len(group),'survivors':int(group.survivor.sum()),'near_misses':int(group.near_miss.sum()),'positive_net_lcb':int((group.net_lcb>0).sum()),'net_lcb_mean':float(group.net_lcb.mean()),'behaviour_clusters':group.full_behaviour_cluster.nunique(),'n_eff':effective_count(group.full_behaviour_cluster),'top_cluster_share':float(counts.iloc[0]/len(group))})
 lane=pd.DataFrame(lane_rows);lane.to_csv(ROOT/'lane_comparison.csv',index=False)

 comparisons=[]
 for adaptive,control in MATCHED_REPAIR_LANES:
  left=strict[strict.lane_id==adaptive];right=strict[strict.lane_id==control]
  left_attr=attribution_frame[attribution_frame.lane_id==adaptive];right_attr=attribution_frame[attribution_frame.lane_id==control]
  wins=sum((left.survivor.mean()>right.survivor.mean(),left.near_miss.mean()>right.near_miss.mean(),left_attr.blocker_distance_delta.median()>right_attr.blocker_distance_delta.median()))
  comparisons.append({'adaptive_lane':adaptive,'control_lane':control,'adaptive_rows':len(left),'control_rows':len(right),'adaptive_survivor_rate':float(left.survivor.mean()),'control_survivor_rate':float(right.survivor.mean()),'adaptive_near_miss_rate':float(left.near_miss.mean()),'control_near_miss_rate':float(right.near_miss.mean()),'adaptive_blocker_delta_median':float(left_attr.blocker_distance_delta.median()),'control_blocker_delta_median':float(right_attr.blocker_distance_delta.median()),'adaptive_behaviour_clusters':left.full_behaviour_cluster.nunique(),'control_behaviour_clusters':right.full_behaviour_cluster.nunique(),'verdict':'ADAPTIVE_SUCCESS' if wins>=2 else 'NO_ADAPTIVE_SUCCESS'})
 adaptive_compare=pd.DataFrame(comparisons);adaptive_compare.to_csv(ROOT/'adaptive_vs_matched_controls.csv',index=False)

 survivors=int(strict.survivor.sum());near=int(strict.near_miss.sum());pos=int((strict.net_lcb>0).sum());unique_queries=len(strict_cache)
 adaptive_success=int((adaptive_compare.verdict=='ADAPTIVE_SUCCESS').sum())
 mcts_row=role_diagnostic[role_diagnostic.lane_id=='local_mcts_repair'].iloc[0]
 mcts_concentration=max(float(mcts_row.top_mechanism_share),float(mcts_row.top_primitive_share))
 median_blocker_delta=float(attribution_frame.blocker_distance_delta.median())
 decision='FROZEN_DEVELOPMENT_EPOCH2_COMPLETED' if survivors>0 else 'FROZEN_DEVELOPMENT_EPOCH2_PARTIALLY_COMPLETED'
 if survivors>0 and adaptive_success>0 and mcts_concentration<.5426:recommendation='PREPARE_ROTATING_CHALLENGE_EPOCH'
 elif survivors==0 and pos>2 and median_blocker_delta>0:recommendation='REVISE_SURVIVOR_CONTRACT_WITHOUT_OOS_ACCESS'
 else:recommendation='REVISE_BLOCKER_DIRECTED_SEARCH_AND_REPEAT'
 outputs=[PACK,ASSIGN,STRICT,ROOT/'search_role_diagnostics.csv',ROOT/'cem_diagnostic.csv',ROOT/'local_mcts_root_visits.csv',ROOT/'repair_child_attribution.csv',ROOT/'repair_lineage_attribution.csv',ROOT/'surrogate_crossfit_diagnostic.csv',ROOT/'admission_policy_comparison.csv',ROOT/'lane_comparison.csv',ROOT/'adaptive_vs_matched_controls.csv']
 policy_counts={str(key):int(value) for key,value in assignments.groupby('admission_policy').size().items()}
 m={'experiment_id':f['experiment_id'],'decision':decision,'recommendation':recommendation,'frozen_manifest_sha256':f['frozen_manifest_sha256'],'proposal_rows':len(df),'logical_strict_rows':len(strict),'shared_cache_queries':unique_queries,'policy_counts':policy_counts,'survivors':survivors,'near_misses':near,'positive_net_lcb':pos,'adaptive_successes':adaptive_success,'mcts_top_concentration':mcts_concentration,'median_blocker_distance_delta':median_blocker_delta,'runtime_seconds':time.perf_counter()-started,'outputs':[{'path':rel(path),'sha256':sha(path)} for path in outputs],'forward_status':'FORWARD_SEALED','candidate_promotion':False,'a7mem_updated':False,'cross_epoch_memory':False,'online_change':False,'additional_budget':False,'oos_claim':False}
 # JSON cannot encode tuple keys; retain the panel allocation as explicit records.
 m['panel_policy_counts']=[{'panel_id':panel,'admission_policy':policy_name,'rows':int(count)} for (panel,policy_name),count in assignments.groupby(['panel_id','admission_policy']).size().items()]
 report=['# Epoch-2 Compact Result','',f"Decision: `{decision}`",f"Recommendation: `{recommendation}`",'',policy.to_markdown(index=False),'',adaptive_compare.to_markdown(index=False),'',f'- Shared exact evaluation queries: {unique_queries} / 2304 logical strict rows',f'- Median parent-to-child blocker distance delta: {median_blocker_delta:.8g}',f'- Local MCTS top mechanism/primitive concentration: {mcts_concentration:.6f}','- `FORWARD_SEALED`','- `NO_CANDIDATE_PROMOTION`','- `NO_CROSS_EPOCH_ADAPTIVE_MEMORY`']
 result_path=ROOT/'EPOCH2_COMPACT_RESULT.md';result_path.write_text('\n'.join(report)+'\n',encoding='utf-8');m['outputs'].append({'path':rel(result_path),'sha256':sha(result_path)})
 RUN.write_text(json.dumps(m,indent=2,sort_keys=True,default=str)+'\n',encoding='utf-8');print(json.dumps({k:m[k] for k in ('decision','recommendation','proposal_rows','logical_strict_rows','shared_cache_queries','survivors','near_misses','positive_net_lcb','adaptive_successes','mcts_top_concentration','median_blocker_distance_delta','runtime_seconds')},indent=2))
def check():
 f=verify();m=load(RUN);assert m['frozen_manifest_sha256']==f['frozen_manifest_sha256'] and m['proposal_rows']==49152 and m['logical_strict_rows']==2304
 assert all(v==768 for v in m['policy_counts'].values());assert not any(m[k] for k in ('candidate_promotion','a7mem_updated','cross_epoch_memory','online_change','additional_budget','oos_claim'))
 strict=pd.read_csv(STRICT);assignments=pd.read_csv(ASSIGN)
 if len(strict)!=2304 or len(assignments)!=2304:raise ValueError('strict execution/assignment drift')
 if assignments.groupby(['panel_id','admission_policy']).exact_identity.apply(lambda values:values.duplicated().any()).any():raise ValueError('duplicate exact identity vote')
 observed={(row.panel_id,row.admission_policy):int(row.rows) for row in pd.DataFrame(m['panel_policy_counts']).itertuples()}
 expected={(panel,policy):quota for panel,quota in PANEL_STRICT_BUDGETS.items() for policy in POLICIES}
 if observed!=expected:raise ValueError(f'panel policy budget drift: {observed}')
 if m['shared_cache_queries']>2304:raise ValueError('shared exact cache query overflow')
 for x in m['outputs']:assert sha(REPO/x['path'])==x['sha256']
 print('PASS_FROZEN_DEVELOPMENT_EPOCH2_VALID')
def main():
 a=argparse.ArgumentParser();a.add_argument('action',choices=('freeze','run','check'));x=a.parse_args()
 try:{'freeze':freeze,'run':run,'check':check}[x.action]()
 except Exception as e:
  ROOT.mkdir(parents=True,exist_ok=True);FAILURE.write_text(json.dumps({'action':x.action,'status':'FAILED_VISIBLE_NOT_DELETED','error_type':type(e).__name__,'error':str(e),'forward_read':False,'candidate_promotion':False},indent=2)+'\n');raise
if __name__=='__main__':main()
