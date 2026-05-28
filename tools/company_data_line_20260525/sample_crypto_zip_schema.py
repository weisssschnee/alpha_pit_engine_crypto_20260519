import zipfile, csv, os, glob, json
roots = [
 r'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\raw\binance_vision\metrics_daily_universe300',
 r'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\raw\binance_vision\metrics_daily_universe500_pruned_remaining_top500',
 r'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\raw\binance_vision\fundingRate_monthly_universe300',
 r'D:\HermesWorker\GDrive\AlphaFactory_CryptoData\raw\binance_vision\markPriceKlines_monthly_universe300'
]
for root in roots:
    files = glob.glob(root + r'\**\*.zip', recursive=True)
    print('ROOT', os.path.basename(root), 'files', len(files))
    if not files: continue
    f = files[0]
    print('SAMPLE', f)
    with zipfile.ZipFile(f) as z:
        name=z.namelist()[0]
        with z.open(name) as fh:
            text=fh.read(1000).decode('utf-8','replace')
            print(text.splitlines()[:5])
