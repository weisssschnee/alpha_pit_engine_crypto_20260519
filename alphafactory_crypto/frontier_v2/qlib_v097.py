from __future__ import annotations

import importlib.metadata
import copy
import hashlib
import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .release import canonical_sha256, sha256_file


@dataclass
class QlibResult:
    challenger_weights: pd.DataFrame
    control_weights: pd.DataFrame
    predictions: pd.DataFrame
    native_metrics: pd.DataFrame
    native_reports: pd.DataFrame
    training_ledger: pd.DataFrame
    manifest: dict[str, Any]


QLIB_SOURCE_FILES = (
    "contrib/data/loader.py",
    "contrib/data/handler.py",
    "contrib/model/gbdt.py",
    "contrib/strategy/signal_strategy.py",
    "contrib/eva/alpha.py",
    "contrib/evaluate.py",
)


def verify_upstream(config: dict[str, Any]) -> dict[str, Any]:
    dependency_path = str(Path(config["dependency_path"]).resolve())
    if dependency_path not in sys.path:
        sys.path.insert(0, dependency_path)
    import qlib

    version = importlib.metadata.version("pyqlib")
    if version != config["version"]:
        raise RuntimeError(f"Qlib version mismatch: {version}")
    source_root = Path(config["source_root"])
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source_root, text=True).strip()
    if commit != config["git_commit"]:
        raise RuntimeError("Qlib source commit mismatch")
    installed_root = Path(qlib.__file__).resolve().parent
    hashes: list[dict[str, str]] = []
    for relative in QLIB_SOURCE_FILES:
        installed = installed_root / relative
        upstream = source_root / "qlib" / relative
        installed_sha = sha256_file(installed)
        upstream_sha = sha256_file(upstream)
        if installed_sha != upstream_sha:
            raise RuntimeError(f"installed Qlib source differs from v0.9.7: {relative}")
        hashes.append({"file": relative, "sha256": installed_sha})
    return {
        "package_version": version,
        "package_path": str(installed_root),
        "source_commit": commit,
        "source_clean": not bool(
            subprocess.check_output(["git", "status", "--porcelain"], cwd=source_root, text=True).strip()
        ),
        "verified_module_bundle_sha256": canonical_sha256(hashes),
        "verified_modules": hashes,
        "lightgbm_version": importlib.metadata.version("lightgbm"),
    }


def prepare_provider(
    daily: pd.DataFrame,
    config: dict[str, Any],
    run_root: Path,
) -> dict[str, Any]:
    csv_root = (run_root / "qlib_source_csv").resolve()
    provider_root = (run_root / "qlib_provider").resolve()
    cache_manifest = run_root / "qlib_provider_cache_manifest.json"
    prepared_sources: list[tuple[str, pd.DataFrame, str, str]] = []
    input_records: list[dict[str, Any]] = []
    for symbol, block in daily.sort_values(["symbol", "date"], kind="mergesort").groupby("symbol", sort=True):
        frame = block[["date", "open", "high", "low", "close", "vwap", "volume"]].copy()
        frame["date"] = pd.to_datetime(frame.date, utc=True).dt.strftime("%Y-%m-%d")
        frame["symbol"] = symbol
        frame["change"] = block.close.pct_change(fill_method=None).to_numpy()
        frame["factor"] = 1.0
        path = csv_root / f"{symbol.lower()}.csv"
        rendered = frame.to_csv(index=False, lineterminator="\n")
        digest = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
        prepared_sources.append((symbol, frame, rendered, digest))
        input_records.append({"symbol": symbol, "semantic_sha256": digest, "rows": len(frame)})
    input_bundle_sha256 = canonical_sha256(input_records)
    dump_script = Path(config["source_root"]) / "scripts" / "dump_bin.py"
    command = [
        str(Path(__import__("sys").executable)),
        str(dump_script),
        "dump_all",
        f"--data_path={csv_root}",
        f"--qlib_dir={provider_root}",
        "--freq=day",
        "--max_workers=1",
        "--date_field_name=date",
        "--symbol_field_name=symbol",
        "--include_fields=open,high,low,close,vwap,volume,factor,change",
    ]
    expected_symbols = {str(symbol).lower() for symbol, _, _, _ in prepared_sources}

    def source_values_match(symbol: str, expected: pd.DataFrame) -> bool:
        path = csv_root / f"{symbol.lower()}.csv"
        if not path.is_file():
            return False
        try:
            actual = pd.read_csv(path)
        except (OSError, ValueError):
            return False
        if list(actual.columns) != list(expected.columns) or len(actual) != len(expected):
            return False
        for column in ("date", "symbol"):
            if not actual[column].astype(str).equals(expected[column].astype(str).reset_index(drop=True)):
                return False
        numeric_columns = [column for column in expected.columns if column not in {"date", "symbol"}]
        return bool(
            np.allclose(
                actual[numeric_columns].to_numpy(dtype=float),
                expected[numeric_columns].to_numpy(dtype=float),
                rtol=1e-12,
                atol=1e-15,
                equal_nan=True,
            )
        )

    source_cache_valid = csv_root.is_dir() and all(
        source_values_match(symbol, frame) for symbol, frame, _, _ in prepared_sources
    )
    provider_structure_valid = (
        provider_root.is_dir()
        and (provider_root / "calendars" / "day.txt").is_file()
        and (provider_root / "instruments" / "all.txt").is_file()
        and all((provider_root / "features" / symbol).is_dir() for symbol in expected_symbols)
    )
    if source_cache_valid and provider_structure_valid:
        source_records = [
            {
                "symbol": symbol,
                "path": str(csv_root / f"{symbol.lower()}.csv"),
                "sha256": sha256_file(csv_root / f"{symbol.lower()}.csv"),
                "rows": len(frame),
            }
            for symbol, frame, _, _ in prepared_sources
        ]
        provider_files = sorted(path for path in provider_root.rglob("*") if path.is_file())
        provider_records = [
            {
                "path": path.relative_to(provider_root).as_posix(),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
            for path in provider_files
        ]
        payload = {
            "csv_root": str(csv_root),
            "provider_root": str(provider_root),
            "input_bundle_sha256": input_bundle_sha256,
            "source_csv_bundle_sha256": canonical_sha256(source_records),
            "provider_bundle_sha256": canonical_sha256(provider_records),
            "source_files": source_records,
            "provider_files": provider_records,
            "dump_command": command,
            "dump_stdout_tail": "",
            "dump_stderr_tail": "",
            "cache_status": "VERIFIED_CACHE_HIT" if cache_manifest.exists() else "VERIFIED_INTERRUPTED_RUN_RECOVERY",
        }
        cache_manifest.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return payload

    for path in (csv_root, provider_root):
        if path.exists():
            if run_root.resolve() not in path.parents:
                raise PermissionError(f"refusing to replace path outside run root: {path}")
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
    for symbol, frame, _, _ in prepared_sources:
        frame.to_csv(csv_root / f"{symbol.lower()}.csv", index=False, lineterminator="\n")
    source_records = [
        {
            "symbol": symbol,
            "path": str(csv_root / f"{symbol.lower()}.csv"),
            "sha256": sha256_file(csv_root / f"{symbol.lower()}.csv"),
            "rows": len(frame),
        }
        for symbol, frame, _, _ in prepared_sources
    ]
    completed = subprocess.run(
        command,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=True,
    )
    provider_files = sorted(path for path in provider_root.rglob("*") if path.is_file())
    provider_records = [
        {"path": path.relative_to(provider_root).as_posix(), "sha256": sha256_file(path), "size_bytes": path.stat().st_size}
        for path in provider_files
    ]
    payload = {
        "csv_root": str(csv_root),
        "provider_root": str(provider_root),
        "input_bundle_sha256": input_bundle_sha256,
        "source_csv_bundle_sha256": canonical_sha256(source_records),
        "provider_bundle_sha256": canonical_sha256(provider_records),
        "source_files": source_records,
        "provider_files": provider_records,
        "dump_command": command,
        "dump_stdout_tail": (completed.stdout or "")[-2000:],
        "dump_stderr_tail": (completed.stderr or "")[-2000:],
        "cache_status": "MATERIALIZED",
    }
    cache_manifest.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def _control_handler_config(start: str, end: str, fit_start: str, fit_end: str) -> dict[str, Any]:
    from qlib.contrib.data.loader import Alpha158DL

    expressions, names = Alpha158DL.get_feature_config(
        {
            "kbar": {},
            "price": {"windows": [0], "feature": ["OPEN", "HIGH", "LOW", "VWAP"]},
            "rolling": {},
        }
    )
    return {
        "instruments": "all",
        "start_time": start,
        "end_time": end,
        "data_loader": {
            "class": "QlibDataLoader",
            "kwargs": {
                "config": {
                    "feature": (expressions[:13], names[:13]),
                    "label": (["Ref($close, -2)/Ref($close, -1) - 1"], ["LABEL0"]),
                },
                "freq": "day",
            },
        },
        "infer_processors": [],
        "learn_processors": [
            {"class": "DropnaLabel"},
            {"class": "CSZScoreNorm", "kwargs": {"fields_group": "label"}},
        ],
    }


def _extract_position_weights(positions: Any, symbols: list[str]) -> pd.DataFrame:
    if isinstance(positions, dict):
        items = list(positions.items())
    elif isinstance(positions, pd.Series):
        items = list(positions.items())
    elif isinstance(positions, pd.DataFrame):
        if "position" in positions.columns:
            items = list(positions.position.items())
        elif positions.shape[1] == 1:
            items = list(positions.iloc[:, 0].items())
        else:
            raise TypeError("unrecognized Qlib positions dataframe")
    else:
        raise TypeError(f"unrecognized Qlib positions type: {type(positions)}")
    rows: list[pd.Series] = []
    for date, position in items:
        if hasattr(position, "get_stock_weight_dict"):
            weights = position.get_stock_weight_dict(only_stock=False)
        elif isinstance(position, dict):
            weights = position
        else:
            raise TypeError(f"unrecognized Qlib position object: {type(position)}")
        row = pd.Series(0.0, index=symbols, name=pd.Timestamp(date, tz="UTC") if pd.Timestamp(date).tzinfo is None else pd.Timestamp(date).tz_convert("UTC"))
        for symbol, weight in weights.items():
            normalized = str(symbol).upper()
            if normalized in row.index:
                row.loc[normalized] = float(weight)
        rows.append(row)
    return pd.DataFrame(rows).sort_index()


def _fit_variant(
    config: dict[str, Any],
    splits: dict[str, Any],
    provider_root: Path,
    run_root: Path,
    *,
    variant: str,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any], pd.DataFrame, dict[str, Any]]:
    import qlib
    from qlib.config import REG_US
    from qlib.contrib.data.handler import Alpha158
    from qlib.contrib.eva.alpha import calc_ic
    from qlib.contrib.evaluate import backtest_daily, risk_analysis
    from qlib.contrib.model.gbdt import LGBModel
    from qlib.contrib.strategy import TopkDropoutStrategy
    from qlib.data.dataset import DatasetH
    from qlib.data.dataset.handler import DataHandlerLP
    from qlib.workflow import R

    provider_start = splits["provider_start"]
    provider_end = splits["provider_end"]
    train_start, train_end = splits["train"]
    valid_start, valid_end = splits["valid"]
    test_start, test_end = splits["development_holdout"]
    handler_cache = run_root / f"qlib_handler_{variant.lower()}.pkl"
    if handler_cache.exists():
        handler = DataHandlerLP.load(handler_cache)
        feature_count = 158 if variant == "FULL_ALPHA158" else 13
    else:
        if variant == "FULL_ALPHA158":
            handler = Alpha158(
                instruments="all",
                start_time=provider_start,
                end_time=provider_end,
                fit_start_time=train_start,
                fit_end_time=train_end,
            )
            feature_count = 158
        elif variant == "FIRST_13_CONTROL":
            full_cache = run_root / "qlib_handler_full_alpha158.pkl"
            if not full_cache.exists():
                raise FileNotFoundError("full Alpha158 handler cache is required before the matched control")
            from qlib.contrib.data.loader import Alpha158DL

            handler = copy.deepcopy(DataHandlerLP.load(full_cache))
            _, official_names = Alpha158DL.get_feature_config(
                {
                    "kbar": {},
                    "price": {"windows": [0], "feature": ["OPEN", "HIGH", "LOW", "VWAP"]},
                    "rolling": {},
                }
            )
            selected = set(official_names[:13])
            for attribute in ("_data", "_infer", "_learn"):
                frame = getattr(handler, attribute)
                keep = [
                    column
                    for column in frame.columns
                    if column[0] == "label" or (column[0] == "feature" and column[1] in selected)
                ]
                setattr(handler, attribute, frame.loc[:, keep].copy())
            feature_count = 13
        else:
            raise ValueError(variant)
        handler.to_pickle(handler_cache, dump_all=True)
    dataset = DatasetH(
        handler=handler,
        segments={
            "train": (train_start, train_end),
            "valid": (valid_start, valid_end),
            "test": (test_start, test_end),
        },
    )
    model_kwargs = dict(config["model"])
    num_boost_round = int(model_kwargs.pop("num_boost_round"))
    early_stopping_rounds = int(model_kwargs.pop("early_stopping_rounds"))
    model = LGBModel(
        num_boost_round=num_boost_round,
        early_stopping_rounds=early_stopping_rounds,
        **model_kwargs,
    )
    evals_result: dict[str, Any] = {}
    started = time.perf_counter()
    with R.start(experiment_name="crypto_frontier_v2_qlib", recorder_name=variant.lower()):
        model.fit(dataset, evals_result=evals_result, verbose_eval=0)
        prediction = model.predict(dataset, segment="test")
    fit_runtime = time.perf_counter() - started
    prediction.name = "score"
    raw_label = dataset.prepare("test", col_set="label", data_key=DataHandlerLP.DK_R).iloc[:, 0]
    ic, ric = calc_ic(prediction, raw_label)
    strategy = TopkDropoutStrategy(
        signal=prediction,
        topk=int(config["topk"]),
        n_drop=int(config["n_drop"]),
    )
    report, positions = backtest_daily(
        start_time=test_start,
        end_time=test_end,
        strategy=strategy,
        account=float(config["account"]),
        benchmark=config["benchmark"],
        exchange_kwargs={
            "freq": "day",
            "limit_threshold": None,
            "deal_price": "close",
            "open_cost": float(config["open_cost"]),
            "close_cost": float(config["close_cost"]),
            "min_cost": float(config["min_cost"]),
            "trade_unit": 1,
        },
    )
    native_net_excess = report["return"] - report["bench"] - report["cost"]
    native_risk = risk_analysis(native_net_excess, freq="day")
    native_metrics = {
        "variant": variant,
        "IC": float(ic.mean()),
        "ICIR": float(ic.mean() / ic.std(ddof=1)),
        "Rank_IC": float(ric.mean()),
        "Rank_ICIR": float(ric.mean() / ric.std(ddof=1)),
        **{f"net_excess_{key}": float(value) for key, value in native_risk.risk.items()},
    }
    symbols = sorted(prediction.index.get_level_values("instrument").str.upper().unique())
    position_weights = _extract_position_weights(positions, symbols)
    decision_weights = position_weights.copy()
    decision_weights.index = decision_weights.index - pd.Timedelta(days=1)
    prediction_dates = pd.DatetimeIndex(prediction.index.get_level_values("datetime").unique()).tz_localize("UTC")
    decision_weights = decision_weights.loc[decision_weights.index.intersection(prediction_dates)]
    if decision_weights.empty:
        raise RuntimeError("Qlib native positions could not be aligned to prediction dates")
    pred_frame = prediction.rename("score").reset_index()
    pred_frame["instrument"] = pred_frame.instrument.str.upper()
    pred_frame["variant"] = variant
    report_frame = report.reset_index().rename(columns={report.index.name or "index": "date"})
    report_frame["variant"] = variant
    ledger = {
        "variant": variant,
        "feature_count": feature_count,
        "fit_runtime_seconds": fit_runtime,
        "best_iteration": int(model.model.best_iteration),
        "train_rows": int(len(dataset.prepare("train", col_set="feature", data_key=DataHandlerLP.DK_I))),
        "valid_rows": int(len(dataset.prepare("valid", col_set="feature", data_key=DataHandlerLP.DK_I))),
        "development_holdout_rows": int(len(prediction)),
        "evals_result": json.dumps(evals_result, sort_keys=True),
    }
    return decision_weights, pred_frame, native_metrics, report_frame, ledger


def run_qlib_native(
    daily: pd.DataFrame,
    config: dict[str, Any],
    splits: dict[str, Any],
    run_root: Path,
) -> QlibResult:
    verification = verify_upstream(config)
    provider = prepare_provider(daily, config, run_root)
    import qlib
    from qlib.config import REG_US
    from qlib.contrib.data.loader import Alpha158DL

    qlib.init(
        provider_uri=provider["provider_root"],
        region=REG_US,
        kernels=int(config["provider_workers"]),
        joblib_backend=str(config["joblib_backend"]),
    )
    expressions, names = Alpha158DL.get_feature_config(
        {
            "kbar": {},
            "price": {"windows": [0], "feature": ["OPEN", "HIGH", "LOW", "VWAP"]},
            "rolling": {},
        }
    )
    if len(expressions) != 158 or len(names) != 158:
        raise RuntimeError("Qlib Alpha158 expression contract drift")

    results = {}
    for variant in ("FULL_ALPHA158", "FIRST_13_CONTROL"):
        results[variant] = _fit_variant(
            config,
            splits,
            Path(provider["provider_root"]),
            run_root,
            variant=variant,
        )
    full_weights, full_pred, full_native, full_report, full_ledger = results["FULL_ALPHA158"]
    control_weights, control_pred, control_native, control_report, control_ledger = results["FIRST_13_CONTROL"]
    manifest = {
        "status": "NATIVE_CODE_REPRODUCED_WITH_CRYPTO_ADAPTATIONS",
        "reproduction_id": config["source_id"],
        "classification": "NATIVE_REPRODUCED",
        "upstream_verification": verification,
        "provider": provider,
        "native_contract": {
            "feature_expression_count": len(expressions),
            "feature_expression_sha256": canonical_sha256(list(zip(names, expressions))),
            "label": "Ref($close, -2)/Ref($close, -1) - 1",
            "learn_processors": ["DropnaLabel", "CSZScoreNorm(label)"],
            "model": "Qlib LGBModel with official Alpha158 workflow parameters",
            "portfolio_mapping": f"Qlib TopkDropoutStrategy topk={config['topk']} n_drop={config['n_drop']}",
            "native_evaluator": "Qlib IC/RankIC plus order/cash/position backtest and 238-day risk_analysis",
        },
        "matched_control": config["matched_control"],
        "adaptations": config["adaptations"],
        "upstream_parity": {
            "official_dump_bin_used": True,
            "official_Alpha158_used": True,
            "official_LGBModel_used": True,
            "official_TopkDropoutStrategy_used": True,
            "official_risk_analysis_used": True,
            "installed_source_matches_tag": True,
        },
        "scope_limit": "native Qlib code path reproduced on a fixed crypto core10 adaptation; original CSI300 benchmark performance is not reproduced",
        "forward_read": False,
        "challenge_read": False,
        "candidate_promotion": False,
    }
    return QlibResult(
        challenger_weights=full_weights,
        control_weights=control_weights,
        predictions=pd.concat([full_pred, control_pred], ignore_index=True),
        native_metrics=pd.DataFrame([full_native, control_native]),
        native_reports=pd.concat([full_report, control_report], ignore_index=True),
        training_ledger=pd.DataFrame([full_ledger, control_ledger]),
        manifest=manifest,
    )
