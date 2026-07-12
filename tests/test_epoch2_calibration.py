import scripts.crypto_epoch2_calibration as calibration

def test_survivor_contract_requires_all_five_gates():
    base={"hard_gate_pass":True,"ic_lcb":.1,"net_lcb":.1,"benchmark_incremental_lcb":.1,"worst_horizon_net_mean":0}
    assert calibration.survivor(base)==(True,[])
    for key in ("ic_lcb","net_lcb","benchmark_incremental_lcb"):
        failed=dict(base); failed[key]=0
        assert not calibration.survivor(failed)[0]

def test_calibration_outputs_are_isolated():
    assert "epoch2_calibration" in str(calibration.ROOT)
