# Crypto A7G-1 May Failure Forensic Audit

- generated_at: `2026-05-19T14:04:54Z`
- decision: `PASS_A7G1_FORENSIC_COMPLETED_HOLD_FUNDING_LINE`
- blockers: `[]`
- warnings: `[]`

## Scope

No new search, no formula changes, no gate tuning. This audit decomposes fresh May 2026 losses after the corrected basis contract from A7G-0.

## Loss Concentration

| object | May total | positive hour rate | top3 loss share | top10 loss share |
|---|---:|---:|---:|---:|
| `FundingCore` | -0.0990 | 0.382 | 0.053 | 0.147 |
| `Core4` | -0.1156 | 0.375 | 0.049 | 0.138 |

## Worst Components

| object | component | net sum | gross | funding drag | fee | turnover | mean funding |
|---|---|---:|---:|---:|---:|---:|---:|
| `Core4` | `crypto_a4_1h_004` | -0.1693 | -0.1312 | -0.0075 | 0.0461 | 46.1298 | 0.000019 |
| `Core4` | `crypto_a4_1h_002` | -0.1542 | -0.1019 | -0.0078 | 0.0606 | 60.5742 | 0.000019 |
| `FundingCore` | `funding_persistence_h12` | -0.1478 | -0.1438 | -0.0097 | 0.0142 | 14.2008 | 0.000019 |
| `FundingCore` | `funding_rate_h12` | -0.1206 | -0.1149 | -0.0092 | 0.0153 | 15.3258 | 0.000019 |
| `Core4` | `crypto_a4_1h_003` | -0.0899 | -0.0669 | -0.0032 | 0.0262 | 26.1587 | 0.000019 |
| `FundingCore` | `funding_rate_h6` | -0.0752 | -0.0656 | -0.0052 | 0.0148 | 14.8258 | 0.000019 |
| `FundingCore` | `funding_persistence_h6` | -0.0513 | -0.0431 | -0.0056 | 0.0139 | 13.8674 | 0.000019 |
| `Core4` | `crypto_a4_1h_001` | -0.0480 | -0.0167 | -0.0048 | 0.0361 | 36.0691 | 0.000019 |

## Worst Symbols

| object | symbol | net sum | gross | funding drag | fee | turnover | abs pos |
|---|---|---:|---:|---:|---:|---:|---:|
| `FundingCore` | `BCHUSDT` | -0.3182 | -0.3259 | -0.0110 | 0.0035 | 3.5455 | 457.33 |
| `Core4` | `BCHUSDT` | -0.2786 | -0.2738 | -0.0069 | 0.0118 | 11.8442 | 265.00 |
| `Core4` | `DOGEUSDT` | -0.1782 | -0.1677 | -0.0020 | 0.0125 | 12.5139 | 367.00 |
| `Core4` | `LINKUSDT` | -0.1600 | -0.1461 | -0.0037 | 0.0176 | 17.6081 | 324.00 |
| `FundingCore` | `ADAUSDT` | -0.1424 | -0.1416 | -0.0050 | 0.0057 | 5.7455 | 424.00 |
| `FundingCore` | `LINKUSDT` | -0.1318 | -0.1289 | -0.0024 | 0.0054 | 5.3788 | 239.33 |
| `FundingCore` | `DOGEUSDT` | -0.1251 | -0.1216 | -0.0014 | 0.0050 | 4.9803 | 277.33 |
| `FundingCore` | `SOLUSDT` | -0.1035 | -0.0998 | -0.0012 | 0.0049 | 4.8970 | 215.33 |
| `FundingCore` | `BNBUSDT` | -0.0881 | -0.0858 | -0.0018 | 0.0042 | 4.2273 | 197.33 |
| `Core4` | `SOLUSDT` | -0.0814 | -0.0693 | -0.0015 | 0.0136 | 13.6111 | 290.33 |
| `Core4` | `ADAUSDT` | -0.0790 | -0.0656 | -0.0033 | 0.0168 | 16.7500 | 356.67 |
| `FundingCore` | `AVAXUSDT` | -0.0528 | -0.0458 | -0.0011 | 0.0082 | 8.1955 | 457.33 |
| `Core4` | `ETHUSDT` | -0.0277 | -0.0183 | -0.0028 | 0.0123 | 12.3108 | 262.33 |
| `Core4` | `AVAXUSDT` | -0.0135 | 0.0065 | 0.0001 | 0.0199 | 19.9142 | 325.00 |
| `FundingCore` | `ETHUSDT` | 0.0022 | 0.0021 | -0.0036 | 0.0037 | 3.7303 | 339.33 |
| `Core4` | `BNBUSDT` | 0.0084 | 0.0201 | -0.0012 | 0.0129 | 12.9151 | 292.67 |

## Regime Buckets

| object | bucket field | bucket | ann mean | DD | hours | share |
|---|---|---|---:|---:|---:|---:|
| `FundingCore` | `funding_abs_mean_bucket` | `low` | -1.2116 | -0.1393 | 399 | 0.907 |
| `FundingCore` | `funding_abs_mean_bucket` | `mid` | -9.3595 | -0.0529 | 41 | 0.093 |
| `FundingCore` | `basis_abs_mean_bucket` | `high` | -1.8896 | -0.0485 | 132 | 0.300 |
| `FundingCore` | `basis_abs_mean_bucket` | `low` | 2.7883 | -0.0218 | 36 | 0.082 |
| `FundingCore` | `basis_abs_mean_bucket` | `mid` | -2.6401 | -0.1223 | 272 | 0.618 |
| `FundingCore` | `vol_ret12_abs_mean_bucket` | `high` | 0.0810 | -0.0369 | 72 | 0.164 |
| `FundingCore` | `vol_ret12_abs_mean_bucket` | `low` | -2.2299 | -0.1404 | 265 | 0.602 |
| `FundingCore` | `vol_ret12_abs_mean_bucket` | `mid` | -2.7386 | -0.0529 | 103 | 0.234 |
| `Core4` | `funding_abs_mean_bucket` | `low` | -2.1322 | -0.1481 | 399 | 0.907 |
| `Core4` | `funding_abs_mean_bucket` | `mid` | -3.9470 | -0.0312 | 41 | 0.093 |
| `Core4` | `basis_abs_mean_bucket` | `high` | -1.3963 | -0.0458 | 132 | 0.300 |
| `Core4` | `basis_abs_mean_bucket` | `low` | 2.5003 | -0.0199 | 36 | 0.082 |
| `Core4` | `basis_abs_mean_bucket` | `mid` | -3.3761 | -0.1188 | 272 | 0.618 |
| `Core4` | `vol_ret12_abs_mean_bucket` | `high` | -3.6700 | -0.0361 | 72 | 0.164 |
| `Core4` | `vol_ret12_abs_mean_bucket` | `low` | -1.8250 | -0.1308 | 265 | 0.602 |
| `Core4` | `vol_ret12_abs_mean_bucket` | `mid` | -2.5703 | -0.0392 | 103 | 0.234 |

## Decision

- If losses are broad across components and symbols, the funding line remains paused for alpha proof.
- If losses are dominated by a small component/symbol/hour set, the next valid work is a predeclared risk-control audit, not search.
