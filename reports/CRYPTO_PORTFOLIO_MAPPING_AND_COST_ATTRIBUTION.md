# Crypto Portfolio Mapping and Cost Attribution

Status: `PORTFOLIO_MAPPING_CAUSAL_SHARE_NOT_IDENTIFIED`; synthetic collapse/amplification mechanisms are confirmed.

## Implemented mapping

The accepted closure uses one `rank_weights` mapping in B1S, Epoch-0, Epoch-1R and Epoch-2:

1. cross-sectionally rank every timestamp;
2. center ranks, forcing zero net exposure;
3. normalize by cross-sectional L1 magnitude;
4. clip at `max_abs_weight=0.20`;
5. renormalize to gross exposure 1.

Source: `crypto-frontier-provenance-closure-20260714:alphafactory_crypto/b1s_canary.py#rank_weights;git_blob=7e38a554b9a7870814efa48900c9a9eb150f8af0;sha256=40C210975F619A66EDEF61B2155DB823ED9BC78CD54415939139E885C86D2FA3`. The post-clip renormalization can undo the nominal cap: the deterministic five-asset case requests `0.20` but ends at max absolute weight `0.272727272727`.

## Deterministic non-market diagnostics

| Case | Raw signal change | Mapped consequence |
|---|---:|---:|
| Common-mode shift | L1 `700` | weight turnover `0` |
| Positive scale change | L1 `108` | weight turnover `0` |
| Confidence-gap reshaping with ranks fixed | not a portfolio measure | weight turnover `0` |
| One finite sparse event | n/a | mapped gross `0` |
| Small cross-sectional rank flip | L1 `1.02` | weight turnover `0.185185185185` |

The mapping therefore:

- removes common-mode directional level and positive scale/confidence information;
- forces zero net and unit gross whenever the cross section has dispersion (`zero_net_max_abs=8.33e-17`, gross=[0.9999999999999999, 0.9999999999999999]);
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

Source: `crypto-frontier-provenance-closure-20260714:alphafactory_crypto/b1s_canary.py#_portfolio_series;git_blob=7e38a554b9a7870814efa48900c9a9eb150f8af0;sha256=40C210975F619A66EDEF61B2155DB823ED9BC78CD54415939139E885C86D2FA3` and `crypto-frontier-provenance-closure-20260714:alphafactory_crypto/nextgen_epoch.py#portfolio_series;git_blob=00a045f71bdbbb61b53e8c9d1705da8fd02f1b2f;sha256=B376E5A9C3E7035F07DCBC7B67C3BFF70BC5B08357C2529817AD5F99633C5337`.

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
