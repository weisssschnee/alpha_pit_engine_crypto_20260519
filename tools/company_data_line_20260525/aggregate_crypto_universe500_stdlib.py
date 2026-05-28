from __future__ import annotations
import argparse, csv, gzip, json, os, zipfile
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

ROOT = Path(r'D:\HermesWorker\GDrive\AlphaFactory_CryptoData')
METRIC_FIELDS = ['sum_open_interest','sum_open_interest_value','count_toptrader_long_short_ratio','sum_toptrader_long_short_ratio','count_long_short_ratio','sum_taker_long_short_vol_ratio']

def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')

def parse_dt_hour(s: str) -> str:
    # input: 2024-11-07 12:35:00
    return s[:13] + ':00:00'

def ms_to_hour(ms: str) -> str:
    dt = datetime.fromtimestamp(int(ms)/1000, tz=timezone.utc)
    return dt.strftime('%Y-%m-%d %H:00:00')

def safe_float(x):
    try: return float(x)
    except Exception: return None

def read_zip_csv(path: Path):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if not n.endswith('/')]
        if not names: return
        with z.open(names[0]) as fh:
            txt = (line.decode('utf-8','replace') for line in fh)
            yield from csv.DictReader(txt)

def symbol_from_dir(path: Path) -> str:
    for p in path.parts[::-1]:
        if p.startswith('symbol='):
            return p.split('=',1)[1]
    return ''

def write_gz_csv(path: Path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with gzip.open(tmp, 'wt', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    tmp.replace(path)

def aggregate_metrics(root: Path, tag: str):
    src_roots = [
        root/'raw'/'binance_vision'/'metrics_daily_universe300',
        root/'raw'/'binance_vision'/'metrics_daily_universe500_pruned_remaining_top500',
    ]
    out_root = root/'silver'/'binance_vision'/'metrics_1h_universe500_v1'
    manifest = root/'manifests'/f'metrics_1h_universe500_v1_{tag}.csv'
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open('w', encoding='utf-8', newline='') as mf:
        mw = csv.DictWriter(mf, fieldnames=['time','symbol','zip_files','rows_1h','min_timestamp','max_timestamp','path','status','error'])
        mw.writeheader()
        symbol_dirs = []
        for sr in src_roots:
            if sr.exists():
                symbol_dirs.extend([p for p in sr.iterdir() if p.is_dir() and p.name.startswith('symbol=')])
        total = len(symbol_dirs)
        for i, sdir in enumerate(sorted(symbol_dirs, key=lambda p:p.name), 1):
            sym = symbol_from_dir(sdir)
            agg = {}
            zips = sorted(sdir.rglob('*.zip'))
            status='ok'; err=''
            try:
                for zp in zips:
                    for row in read_zip_csv(zp):
                        ts = parse_dt_hour(row.get('create_time',''))
                        if not ts.strip(): continue
                        cur = agg.setdefault(ts, {'symbol': sym, 'timestamp': ts, 'n_5m': 0})
                        cur['n_5m'] += 1
                        # last observable in the hour, file rows are chronological. Also keep simple mean for robustness.
                        for f in METRIC_FIELDS:
                            v = safe_float(row.get(f,''))
                            if v is None: continue
                            cur[f + '_last'] = v
                            cur[f + '_sum_for_mean'] = cur.get(f + '_sum_for_mean', 0.0) + v
                            cur[f + '_count_for_mean'] = cur.get(f + '_count_for_mean', 0) + 1
                out_rows=[]
                for ts in sorted(agg):
                    r=agg[ts]
                    out={'symbol':sym,'timestamp':ts,'n_5m':r.get('n_5m',0)}
                    for f in METRIC_FIELDS:
                        out[f + '_last'] = r.get(f + '_last','')
                        c = r.get(f + '_count_for_mean',0)
                        out[f + '_mean'] = (r.get(f + '_sum_for_mean',0.0)/c) if c else ''
                    out_rows.append(out)
                fields=['symbol','timestamp','n_5m'] + [f+suf for f in METRIC_FIELDS for suf in ['_last','_mean']]
                out_path = out_root/f'symbol={sym}'/'part.csv.gz'
                write_gz_csv(out_path, out_rows, fields)
                min_ts = out_rows[0]['timestamp'] if out_rows else ''
                max_ts = out_rows[-1]['timestamp'] if out_rows else ''
                mw.writerow({'time':utc_now(),'symbol':sym,'zip_files':len(zips),'rows_1h':len(out_rows),'min_timestamp':min_ts,'max_timestamp':max_ts,'path':str(out_path),'status':status,'error':err})
            except Exception as e:
                status='error'; err=repr(e)[:500]
                mw.writerow({'time':utc_now(),'symbol':sym,'zip_files':len(zips),'rows_1h':0,'min_timestamp':'','max_timestamp':'','path':'','status':status,'error':err})
            mf.flush()
            if i % 25 == 0:
                print(f'progress metrics_1h {i}/{total}', flush=True)
    report = root/'reports'/f'metrics_1h_universe500_v1_{tag}.json'
    report.write_text(json.dumps({'generated_at':utc_now(),'manifest':str(manifest),'out_root':str(out_root),'symbols':total}, indent=2), encoding='utf-8')
    print('metrics_1h_manifest=' + str(manifest), flush=True)

def aggregate_monthly(root: Path, tag: str):
    out_root = root/'silver'/'binance_vision'/'monthly_market_funding_1h_top300_v1'
    manifest = root/'manifests'/f'monthly_market_funding_1h_top300_v1_{tag}.csv'
    roots = {
        'fundingRate': root/'raw'/'binance_vision'/'fundingRate_monthly_universe300',
        'markPriceKlines': root/'raw'/'binance_vision'/'markPriceKlines_monthly_universe300',
        'indexPriceKlines': root/'raw'/'binance_vision'/'indexPriceKlines_monthly_universe300',
        'premiumIndexKlines': root/'raw'/'binance_vision'/'premiumIndexKlines_monthly_universe300',
    }
    symbols=set()
    for rr in roots.values():
        if rr.exists(): symbols.update(symbol_from_dir(p) for p in rr.iterdir() if p.is_dir())
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open('w', encoding='utf-8', newline='') as mf:
        mw=csv.DictWriter(mf, fieldnames=['time','symbol','rows','min_timestamp','max_timestamp','path','status','error'])
        mw.writeheader()
        for i,sym in enumerate(sorted(symbols),1):
            byts=defaultdict(lambda:{'symbol':sym})
            status='ok'; err=''
            try:
                for dataset, rr in roots.items():
                    sdir=rr/f'symbol={sym}'
                    if not sdir.exists(): continue
                    for zp in sorted(sdir.rglob('*.zip')):
                        for row in read_zip_csv(zp):
                            if dataset=='fundingRate':
                                ts=ms_to_hour(row.get('calc_time','0'))
                                byts[ts]['timestamp']=ts
                                byts[ts]['funding_interval_hours']=row.get('funding_interval_hours','')
                                byts[ts]['last_funding_rate']=row.get('last_funding_rate','')
                            else:
                                ts=ms_to_hour(row.get('open_time','0'))
                                byts[ts]['timestamp']=ts
                                prefix={'markPriceKlines':'mark','indexPriceKlines':'index','premiumIndexKlines':'premium'}[dataset]
                                for f in ['open','high','low','close','count']:
                                    byts[ts][prefix+'_'+f]=row.get(f,'')
                fields=['symbol','timestamp','funding_interval_hours','last_funding_rate'] + [p+'_'+f for p in ['mark','index','premium'] for f in ['open','high','low','close','count']]
                rows=[]
                for ts in sorted(byts):
                    r={k:byts[ts].get(k,'') for k in fields}
                    rows.append(r)
                out_path=out_root/f'symbol={sym}'/'part.csv.gz'
                write_gz_csv(out_path, rows, fields)
                mw.writerow({'time':utc_now(),'symbol':sym,'rows':len(rows),'min_timestamp':rows[0]['timestamp'] if rows else '','max_timestamp':rows[-1]['timestamp'] if rows else '','path':str(out_path),'status':status,'error':err})
            except Exception as e:
                mw.writerow({'time':utc_now(),'symbol':sym,'rows':0,'min_timestamp':'','max_timestamp':'','path':'','status':'error','error':repr(e)[:500]})
            mf.flush()
            if i % 25 == 0:
                print(f'progress monthly_1h {i}/{len(symbols)}', flush=True)
    report=root/'reports'/f'monthly_market_funding_1h_top300_v1_{tag}.json'
    report.write_text(json.dumps({'generated_at':utc_now(),'manifest':str(manifest),'out_root':str(out_root),'symbols':len(symbols)}, indent=2), encoding='utf-8')
    print('monthly_1h_manifest=' + str(manifest), flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['metrics','monthly','all'], default='all')
    ap.add_argument('--root', default=str(ROOT))
    ap.add_argument('--tag', default=datetime.utcnow().strftime('%Y%m%d_%H%M%S'))
    args=ap.parse_args()
    root=Path(args.root)
    if args.mode in ('metrics','all'):
        aggregate_metrics(root,args.tag)
    if args.mode in ('monthly','all'):
        aggregate_monthly(root,args.tag)

if __name__ == '__main__':
    main()
