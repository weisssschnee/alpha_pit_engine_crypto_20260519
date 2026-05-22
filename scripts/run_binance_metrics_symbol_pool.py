#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
DEFAULT_DOWNLOADER = DATA_ROOT / "scripts" / "download_build_binance_metrics_history.py"
DEFAULT_LOG_DIR = DATA_ROOT / "logs" / "binance_metrics_symbol_pool"
DEFAULT_REPORT_DIR = DATA_ROOT / "reports"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def write_status(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser(description="Retry-safe concurrent Binance metrics downloader by symbol.")
    ap.add_argument("--symbols", nargs="+", required=True)
    ap.add_argument("--start", default="2024-01-01")
    ap.add_argument("--end", default="2026-05-21")
    ap.add_argument("--max-concurrent", type=int, default=12)
    ap.add_argument("--sleep", type=float, default=0.005)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--retries", type=int, default=8)
    ap.add_argument("--backoff", type=float, default=1.0)
    ap.add_argument("--tag", default=datetime.now().strftime("%Y%m%d_%H%M%S"))
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--downloader", default=str(DEFAULT_DOWNLOADER))
    ap.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    ap.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR))
    args = ap.parse_args()

    python = Path(args.python)
    downloader = Path(args.downloader)
    log_dir = Path(args.log_dir) / args.tag
    report_dir = Path(args.report_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    status_path = report_dir / f"binance_metrics_symbol_pool_status_{args.tag}.json"

    pending = [s.upper() for s in args.symbols]
    running: dict[str, dict] = {}
    completed: dict[str, dict] = {}
    failed: dict[str, dict] = {}
    started_at = utc_now()

    def snapshot() -> dict:
        return {
            "decision": "A7AC2B_BINANCE_METRICS_SYMBOL_POOL_RUNNING"
            if (pending or running)
            else (
                "PASS_A7AC2B_BINANCE_METRICS_SYMBOL_POOL_COMPLETED"
                if not failed
                else "HOLD_A7AC2B_BINANCE_METRICS_SYMBOL_POOL_FAILED"
            ),
            "generated_at": utc_now(),
            "started_at": started_at,
            "tag": args.tag,
            "range": {"start": args.start, "end": args.end},
            "python": str(python),
            "downloader": str(downloader),
            "max_concurrent": args.max_concurrent,
            "executes_download": True,
            "executes_search": False,
            "authorizes_alpha_proof": False,
            "pending": pending,
            "running": {
                k: {
                    "pid": v["proc"].pid,
                    "out_log": str(v["out_log"]),
                    "err_log": str(v["err_log"]),
                    "started_at": v["started_at"],
                }
                for k, v in running.items()
            },
            "completed": completed,
            "failed": failed,
            "counts": {
                "pending": len(pending),
                "running": len(running),
                "completed": len(completed),
                "failed": len(failed),
                "total": len(args.symbols),
            },
        }

    write_status(status_path, snapshot())

    while pending or running:
        while pending and len(running) < args.max_concurrent:
            symbol = pending.pop(0)
            out_log = log_dir / f"{symbol}.out.log"
            err_log = log_dir / f"{symbol}.err.log"
            cmd = [
                str(python),
                "-u",
                str(downloader),
                "--symbols",
                symbol,
                "--start",
                args.start,
                "--end",
                args.end,
                "--sleep",
                str(args.sleep),
                "--timeout",
                str(args.timeout),
                "--retries",
                str(args.retries),
                "--backoff",
                str(args.backoff),
                "--skip-existing",
                "--tag",
                f"{args.tag}_{symbol}",
            ]
            outf = out_log.open("wb")
            errf = err_log.open("wb")
            proc = subprocess.Popen(cmd, stdout=outf, stderr=errf)
            running[symbol] = {
                "proc": proc,
                "out_log": out_log,
                "err_log": err_log,
                "stdout_handle": outf,
                "stderr_handle": errf,
                "started_at": utc_now(),
            }
            print("started", symbol, proc.pid, flush=True)
            write_status(status_path, snapshot())

        for symbol, info in list(running.items()):
            rc = info["proc"].poll()
            if rc is None:
                continue
            info["stdout_handle"].close()
            info["stderr_handle"].close()
            row = {
                "returncode": rc,
                "out_log": str(info["out_log"]),
                "err_log": str(info["err_log"]),
                "started_at": info["started_at"],
                "finished_at": utc_now(),
            }
            if rc == 0:
                completed[symbol] = row
                print("completed", symbol, flush=True)
            else:
                failed[symbol] = row
                print("failed", symbol, rc, flush=True)
            del running[symbol]
            write_status(status_path, snapshot())

        time.sleep(5)

    write_status(status_path, snapshot())
    print("status=" + str(status_path), flush=True)
    print("log_dir=" + str(log_dir), flush=True)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
