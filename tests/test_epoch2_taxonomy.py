from types import SimpleNamespace
from scripts.crypto_epoch2_taxonomy import classify
def row(**kw):
 d=dict(hard_gate_pass=True,ic_lcb=.1,net_lcb=.1,benchmark_incremental_lcb=.1,worst_horizon_net_mean=0,gross_mean=.1,net_mean=.1,hard_gate_reasons='');d.update(kw);return SimpleNamespace(**d)
def test_blocker_types_are_gate_directed():
 assert classify(row(net_lcb=-.0001))[0]=='NET_LCB_NEAR_ZERO'
 assert classify(row(net_lcb=-.0001,gross_mean=.1,net_mean=-.1))[0]=='COST_ONLY'
 assert classify(row(benchmark_incremental_lcb=-.1))[0]=='BENCHMARK_INCREMENT_ONLY'
 assert classify(row(worst_horizon_net_mean=-.002))[0]=='STABILITY_ONLY'
