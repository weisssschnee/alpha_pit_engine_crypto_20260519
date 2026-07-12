from __future__ import annotations
import gzip,hashlib,json,sys
from pathlib import Path
import pandas as pd
REPO=Path(__file__).resolve().parents[1]; ROOT=REPO/'runtime/epoch2_calibration_20260712'
STRICT=REPO/'runtime/nextgen_epoch1r_20260712/strict_evaluations.csv'; PACK=REPO/'runtime/nextgen_epoch1r_20260712/proposal_pack.jsonl.gz'
PARENTS=ROOT/'frozen_near_miss_parent_pack.csv'; TAXONOMY=ROOT/'near_miss_blocker_taxonomy.csv'; SUMMARY=ROOT/'blocker_summary.csv'; MANIFEST=ROOT/'taxonomy_manifest.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def classify(r):
    failed=[]
    if not r.hard_gate_pass: failed.append('HARD_GATE')
    if r.ic_lcb<=0: failed.append('IC_LCB')
    if r.net_lcb<=0: failed.append('NET_LCB')
    if r.benchmark_incremental_lcb<=0: failed.append('BENCHMARK_INCREMENT')
    if r.worst_horizon_net_mean<=-.001: failed.append('WORST_BLOCK')
    if len(failed)>1:return 'MULTI_GATE_FAILURE','|'.join(failed)
    f=failed[0]
    if f=='NET_LCB' and r.gross_mean>0 and r.net_mean<=0:return 'COST_ONLY',f
    if f=='NET_LCB':return 'NET_LCB_NEAR_ZERO' if r.net_lcb>-.0002 else 'STRUCTURAL_UNREPAIRABLE',f
    if f=='BENCHMARK_INCREMENT':return 'BENCHMARK_INCREMENT_ONLY',f
    if f=='WORST_BLOCK':return 'STABILITY_ONLY',f
    if f=='HARD_GATE' and 'CONCENTRATION' in str(r.hard_gate_reasons):return 'CONCENTRATION_ONLY',f
    if f=='IC_LCB':return 'IC_LCB_NEAR_ZERO' if r.ic_lcb>-.05 else 'STRUCTURAL_UNREPAIRABLE',f
    return 'STRUCTURAL_UNREPAIRABLE',f
def run():
    strict=pd.read_csv(STRICT); near=strict[strict.survivor_near_miss].copy()
    specs={}
    with gzip.open(PACK,'rt',encoding='utf-8') as h:
        for line in h:
            x=json.loads(line); specs[x['proposal_id']]=x
    rows=[]
    for r in near.itertuples():
        typ,failed=classify(r); x=specs[r.proposal_id]; s=x['spec']
        rows.append({**r._asdict(),'frozen_parent_row_id':f'{r.arm}|{r.proposal_id}','failed_gate':failed,'blocker_type':typ,'distance_ic_lcb':r.ic_lcb,'distance_net_lcb':r.net_lcb,
          'distance_benchmark_increment':r.benchmark_incremental_lcb,'distance_worst_block':r.worst_horizon_net_mean+.001,
          'parent_identity':s['parent_identity'],'primitive':s['primitive'],'field_a':s['field_a'],'field_b':s['field_b'],
          'repair_priority':1 if typ in {'COST_ONLY','NET_LCB_NEAR_ZERO','BENCHMARK_INCREMENT_ONLY','STABILITY_ONLY'} else 2 if typ=='CONCENTRATION_ONLY' else 3})
    out=pd.DataFrame(rows).sort_values(['repair_priority','blocker_type','proposal_id']); out.to_csv(TAXONOMY,index=False)
    out.to_csv(PARENTS,index=False)
    summary=out.groupby(['blocker_type','failed_gate','repair_priority']).size().reset_index(name='candidates').sort_values(['repair_priority','candidates'],ascending=[True,False]); summary.to_csv(SUMMARY,index=False)
    assert len(out)==84 and out.frozen_parent_row_id.nunique()==84
    m={'status':'EPOCH2_NEAR_MISS_PARENTS_FROZEN','parent_rows':84,'unique_proposal_ids':int(out.proposal_id.nunique()),'unique_exact_identities':int(out.exact_identity.nunique()),'source_strict_sha256':sha(STRICT),'source_proposal_pack_sha256':sha(PACK),'parent_pack_sha256':sha(PARENTS),'taxonomy_sha256':sha(TAXONOMY),'summary_sha256':sha(SUMMARY),'selection_replayed':False,'performance_reoptimized':False,'forward_read':False,'memory_updated':False}
    MANIFEST.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(json.dumps(m,indent=2)); print(summary.to_string(index=False))
if __name__=='__main__':run()
