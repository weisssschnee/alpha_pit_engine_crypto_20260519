"""Lightweight field information qualification over existing authorities.

This module compiles existing registries into a token view, loads only requested
field slices, and computes development-only information diagnostics.  It is not
a feature authority, feature store, model trainer, or economic evaluator.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from alphafactory_crypto.broad_search.panel18m import RawPanelStore


@dataclass(frozen=True, slots=True)
class FieldBatch:
    token_ids: tuple[str, ...]
    values: np.ndarray
    masks: np.ndarray


@dataclass(frozen=True, slots=True)
class FieldBatchProvider:
    """Load field, asset, and time subsets without a dense feature universe."""

    field_ids: tuple[str, ...]
    asset_count: int
    time_count: int
    store: RawPanelStore | None = None
    cube: np.ndarray | None = None
    source_time_slice: slice | None = None

    @classmethod
    def from_raw_panel(
        cls, store: RawPanelStore, time_slice: slice | None = None
    ) -> "FieldBatchProvider":
        assets, timestamps = store.shape
        source = time_slice or slice(0, timestamps)
        start = int(source.start or 0)
        stop = int(source.stop if source.stop is not None else timestamps)
        return cls(
            tuple(store.metadata["field_ids"]), assets, stop - start,
            store=store, source_time_slice=slice(start, stop),
        )

    @classmethod
    def from_cube(
        cls, field_ids: Sequence[str], cube: np.ndarray
    ) -> "FieldBatchProvider":
        values = np.asarray(cube)
        if values.ndim != 3 or values.shape[1] != len(field_ids):
            raise ValueError("cube must have shape (assets, fields, timestamps)")
        return cls(tuple(field_ids), values.shape[0], values.shape[2], cube=values)

    def load(
        self,
        token_ids: Sequence[str],
        asset_indices: Sequence[int] | np.ndarray | slice,
        time_slice: slice,
    ) -> FieldBatch:
        if not isinstance(time_slice, slice):
            raise TypeError("time_slice must be a slice")
        positions = []
        for token_id in token_ids:
            field_id = token_id.removeprefix("FIELD:")
            if field_id not in self.field_ids:
                raise KeyError(field_id)
            positions.append(self.field_ids.index(field_id))
        assets = np.arange(self.asset_count)[asset_indices]
        if self.store is not None:
            source_start = int((self.source_time_slice or slice(0)).start or 0)
            local_start = int(time_slice.start or 0)
            local_stop = int(time_slice.stop if time_slice.stop is not None else self.time_count)
            source_slice = slice(source_start + local_start, source_start + local_stop, time_slice.step)
            arrays = [
                np.asarray(self.store.field(self.field_ids[pos])[assets, source_slice])
                for pos in positions
            ]
            values = np.stack(arrays, axis=1)
        elif self.cube is not None:
            values = np.asarray(self.cube[assets][:, positions, time_slice])
        else:  # pragma: no cover - constructor invariants protect this path
            raise RuntimeError("provider has no backing store")
        return FieldBatch(tuple(token_ids), values, np.isfinite(values))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def compile_token_catalog(repo_root: Path, config: Mapping[str, Any]) -> pd.DataFrame:
    """Compile one traceable view; source registries remain authoritative."""

    paths = config["inputs"]
    inventory = pd.read_csv(repo_root / paths["inventory"], low_memory=False)
    base = pd.read_csv(repo_root / paths["aggtrades_base"], low_memory=False)
    derived = pd.read_csv(repo_root / paths["aggtrades_derived"], low_memory=False)
    lineage = pd.read_csv(repo_root / paths["lineage"], low_memory=False)

    base_by_id = base.set_index("field_name", drop=False).to_dict("index")
    derived_by_id = derived.set_index("derived_feature_id", drop=False).to_dict("index")
    lineage_by_id = lineage.set_index("field_id", drop=False).to_dict("index")
    rows: list[dict[str, Any]] = []
    for item in inventory.to_dict("records"):
        field_id = str(item["field_id"])
        base_row = base_by_id.get(field_id, {})
        derived_row = derived_by_id.get(field_id, {})
        lineage_row = lineage_by_id.get(field_id, {})
        is_derived = bool(derived_row)
        dependencies = str(
            derived_row.get("base_fields")
            or lineage_row.get("source_fields")
            or item.get("source_field")
            or field_id
        )
        transform = str(derived_row.get("transform") or "IDENTITY")
        window = derived_row.get("window_hours")
        scope = str(
            derived_row.get("cross_symbol_scope")
            or base_row.get("cross_symbol_scope")
            or "same_symbol"
        )
        lag = (
            derived_row.get("feature_available_lag_bars")
            if is_derived
            else base_row.get("feature_available_lag_bars")
        )
        token_id = (
            f"FIELD:{dependencies}|TRANSFORM:{transform.upper()}|"
            f"WINDOW:{int(window)}H|SCOPE:{scope.upper()}"
            if is_derived
            else f"FIELD:{field_id}"
        )
        status = str(item.get("registry_status") or "")
        blocker = ""
        if "FORBID" in status or "BLOCK" in status:
            blocker = status
        elif "HOLD" in status:
            blocker = status
        elif not bool(item.get("runtime_loaded", False)):
            blocker = "NOT_RUNTIME_LOADED"
        rows.append(
            {
                "token_id": token_id,
                "token_kind": "DERIVED" if is_derived else "BASE_OR_REGISTERED",
                "field_id": field_id,
                "base_dependencies": dependencies,
                "family": str(
                    derived_row.get("production_family")
                    or base_row.get("field_family")
                    or item.get("feature_family")
                    or "unknown"
                ),
                "source": str(item.get("source_field") or base_row.get("field_source") or ""),
                "semantic_role": str(item.get("consumer_lane") or ""),
                "scope": scope,
                "observable_lag": str(item.get("PIT/source_lag") or lag or ""),
                "pit_source_status": str(lineage_row.get("lineage_status") or "UNVERIFIED"),
                "availability_scope": str(base_row.get("availability_scope") or ""),
                "generator_enabled": bool(base_row.get("generator_enabled", is_derived)),
                "runtime_loaded": bool(item.get("runtime_loaded", False)),
                "search_allowed": bool(item.get("search_allowed", False)),
                "input_approval": status,
                "blocker": blocker,
                "transform": transform,
                "window_hours": window,
                "interaction_type": str(derived_row.get("production_family") or ""),
                "availability_mask_required": bool(
                    derived_row.get("requires_agg_features_available_mask", False)
                    or base_row.get("requires_agg_features_available_mask", False)
                ),
                "authority_ref": str(lineage_row.get("source_path") or ""),
            }
        )
    result = pd.DataFrame(rows)
    if result["field_id"].nunique() != len(result):
        raise ValueError("inventory field identities are not unique")
    return result.sort_values(["token_kind", "field_id"], kind="stable").reset_index(drop=True)


def quantile_edges(values: np.ndarray, bins: int = 16) -> np.ndarray:
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if finite.size < 2 or np.nanmin(finite) == np.nanmax(finite):
        return np.asarray([], dtype=float)
    edges = np.unique(np.quantile(finite, np.linspace(0.0, 1.0, bins + 1)[1:-1]))
    return edges.astype(float)


def apply_bins(values: np.ndarray, edges: np.ndarray) -> np.ndarray:
    out = np.full(np.asarray(values).shape, -1, dtype=np.int16)
    finite = np.isfinite(values)
    if edges.size:
        out[finite] = np.searchsorted(edges, np.asarray(values)[finite], side="right")
    elif finite.any():
        out[finite] = 0
    return out


def discrete_entropy(values: np.ndarray) -> float:
    data = np.asarray(values)
    data = data[data >= 0]
    if not data.size:
        return 0.0
    counts = np.bincount(data.astype(int))
    probabilities = counts[counts > 0] / counts.sum()
    return float(-(probabilities * np.log(probabilities)).sum())


def discrete_mi(left: np.ndarray, right: np.ndarray) -> float:
    x = np.asarray(left, dtype=int)
    y = np.asarray(right, dtype=int)
    valid = (x >= 0) & (y >= 0)
    if valid.sum() < 2:
        return 0.0
    x, y = x[valid], y[valid]
    table = np.zeros((int(x.max()) + 1, int(y.max()) + 1), dtype=np.int64)
    np.add.at(table, (x, y), 1)
    total = table.sum()
    joint = table / total
    px = joint.sum(axis=1, keepdims=True)
    py = joint.sum(axis=0, keepdims=True)
    expected = px @ py
    nonzero = joint > 0
    return float((joint[nonzero] * np.log(joint[nonzero] / expected[nonzero])).sum())


def cross_fitted_ridge_residual(
    known_values: np.ndarray,
    target: np.ndarray,
    eligible: np.ndarray,
    month_ids: np.ndarray,
    ridge: float = 1e-3,
) -> np.ndarray:
    """Leave-one-month-out ridge using sufficient statistics, without HPO."""

    x = np.asarray(known_values, dtype=float)
    y = np.asarray(target, dtype=float)
    valid_x = np.where(np.isfinite(x), x, np.nan)
    med = np.nanmedian(valid_x, axis=(0, 2), keepdims=True)
    scale = np.nanstd(valid_x, axis=(0, 2), keepdims=True)
    scale = np.where(np.isfinite(scale) & (scale > 1e-12), scale, 1.0)
    x = np.nan_to_num((x - med) / scale, nan=0.0)
    residual = np.full_like(y, np.nan, dtype=float)
    months = tuple(sorted(set(month_ids.tolist())))
    sufficient: dict[Any, tuple[np.ndarray, np.ndarray]] = {}
    for month in months:
        mask = eligible[:, month_ids == month] & np.isfinite(y[:, month_ids == month])
        xm = np.moveaxis(x[:, :, month_ids == month], 1, -1)[mask]
        ym = y[:, month_ids == month][mask]
        design = np.column_stack([np.ones(len(xm)), xm])
        sufficient[month] = (design.T @ design, design.T @ ym)
    total_xx = sum(value[0] for value in sufficient.values())
    total_xy = sum(value[1] for value in sufficient.values())
    penalty = np.eye(total_xx.shape[0]) * ridge
    penalty[0, 0] = 0.0
    for month in months:
        xx, xy = sufficient[month]
        beta = np.linalg.solve(total_xx - xx + penalty, total_xy - xy)
        local = month_ids == month
        design = np.concatenate(
            [np.ones((x.shape[0], 1, local.sum())), x[:, :, local]], axis=1
        )
        prediction = np.einsum("aft,f->at", design, beta)
        residual[:, local] = y[:, local] - prediction
    residual[~eligible] = np.nan
    return residual


def _sample_coordinates(mask: np.ndarray, maximum: int) -> tuple[np.ndarray, np.ndarray]:
    coordinates = np.argwhere(mask.T)
    if len(coordinates) > maximum:
        positions = np.linspace(0, len(coordinates) - 1, maximum, dtype=int)
        coordinates = coordinates[positions]
    return coordinates[:, 1], coordinates[:, 0]


def information_census(
    *,
    context_id: str,
    provider: FieldBatchProvider,
    field_ids: Sequence[str],
    field_meta: Mapping[str, Mapping[str, Any]],
    target: np.ndarray,
    residual_target: np.ndarray,
    eligible: np.ndarray,
    timestamps: np.ndarray,
    bin_fit_slice: slice,
    bins: int = 16,
    maximum_samples: int = 200_000,
    null_shifts_hours: Sequence[int] = (168, 336, 504, 672, 840, 1008, 1176, 1344),
) -> pd.DataFrame:
    target_edges = quantile_edges(target[:, bin_fit_slice][eligible[:, bin_fit_slice]], bins)
    residual_edges = quantile_edges(
        residual_target[:, bin_fit_slice][eligible[:, bin_fit_slice]], bins
    )
    target_bins = apply_bins(target, target_edges)
    residual_bins = apply_bins(residual_target, residual_edges)
    months = pd.to_datetime(timestamps, utc=True).to_period("M").astype(str).to_numpy()
    asset_sample, time_sample = _sample_coordinates(eligible & np.isfinite(target), maximum_samples)
    rows: list[dict[str, Any]] = []
    redundancy_values: dict[str, np.ndarray] = {}
    for field_id in field_ids:
        values = provider.load(
            [f"FIELD:{field_id}"], slice(None), slice(0, provider.time_count)
        ).values[:, 0, :].astype(float)
        fit_mask = eligible[:, bin_fit_slice] & np.isfinite(values[:, bin_fit_slice])
        edges = quantile_edges(values[:, bin_fit_slice][fit_mask], bins)
        value_bins = apply_bins(values, edges)
        sampled_x = value_bins[asset_sample, time_sample]
        sampled_y = target_bins[asset_sample, time_sample]
        sampled_residual = residual_bins[asset_sample, time_sample]
        observed_mi = discrete_mi(sampled_x, sampled_y)
        residual_mi = discrete_mi(sampled_x, sampled_residual)
        nulls = [
            discrete_mi(sampled_x, np.roll(target_bins, shift, axis=1)[asset_sample, time_sample])
            for shift in null_shifts_hours
            if shift < target_bins.shape[1]
        ]
        null_median = float(np.median(nulls)) if nulls else 0.0
        block_values = []
        for month in sorted(set(months.tolist())):
            local = months == month
            mask = eligible[:, local] & np.isfinite(values[:, local]) & np.isfinite(target[:, local])
            if mask.sum() >= 100:
                block_values.append(discrete_mi(value_bins[:, local][mask], target_bins[:, local][mask]))
        missing = (~np.isfinite(values)).astype(np.int16)
        missing_mi = discrete_mi(
            missing[asset_sample, time_sample], sampled_y
        )
        finite_eligible = eligible & np.isfinite(values)
        meta = field_meta.get(field_id, {})
        rows.append(
            {
                "context_id": context_id,
                "field_id": field_id,
                "token_id": f"FIELD:{field_id}",
                "family": str(meta.get("family") or "unknown"),
                "coverage_ratio": float(finite_eligible.sum() / max(eligible.sum(), 1)),
                "eligible_assets": int(np.any(finite_eligible, axis=1).sum()),
                "effective_time_blocks": len(block_values),
                "normalized_value_entropy": discrete_entropy(sampled_x) / max(np.log(bins), 1.0),
                "missing_mask_entropy": discrete_entropy(missing[asset_sample, time_sample]),
                "target_mutual_information": observed_mi,
                "residual_mutual_information": residual_mi,
                "permutation_null_median": null_median,
                "mutual_information_excess": observed_mi - null_median,
                "residual_mi_excess": residual_mi - null_median,
                "missing_mask_target_mi": missing_mi,
                "block_median": float(np.median(block_values)) if block_values else 0.0,
                "block_q25": float(np.quantile(block_values, 0.25)) if block_values else 0.0,
                "positive_block_ratio": float(
                    np.mean(np.asarray(block_values) > null_median)
                ) if block_values else 0.0,
                "availability_scope": str(meta.get("availability_scope") or ""),
                "pit_source_status": str(meta.get("pit_source_status") or "UNVERIFIED"),
                "runtime_loaded": bool(meta.get("runtime_loaded", False)),
                "missingness_flag": (
                    "MISSINGNESS_DOMINATED"
                    if missing_mi > max(observed_mi, residual_mi)
                    else ""
                ),
            }
        )
        redundancy_values[field_id] = values[asset_sample, time_sample]

    result = pd.DataFrame(rows).set_index("field_id", drop=False)
    frame = pd.DataFrame(redundancy_values)
    correlation = frame.corr(method="spearman", min_periods=100)
    parents = {field: field for field in field_ids}

    def find(item: str) -> str:
        while parents[item] != item:
            parents[item] = parents[parents[item]]
            item = parents[item]
        return item

    def union(left: str, right: str) -> None:
        a, b = find(left), find(right)
        if a != b:
            parents[max(a, b)] = min(a, b)

    for i, left in enumerate(field_ids):
        for right in field_ids[i + 1 :]:
            value = correlation.loc[left, right]
            if pd.notna(value) and abs(value) >= 0.95:
                union(left, right)
    for field in field_ids:
        peers = correlation.loc[field].drop(index=field).abs().dropna()
        result.loc[field, "max_redundancy_spearman"] = float(peers.max()) if len(peers) else 0.0
        result.loc[field, "redundancy_cluster_id"] = f"{context_id}:{find(field)}"
        if (
            result.loc[field, "coverage_ratio"] < 0.7
            and result.loc[field, "missing_mask_target_mi"] > 0
        ):
            result.loc[field, "missingness_flag"] = "COVERAGE_IDENTITY_RISK"
    return result.reset_index(drop=True)


def role_for_family(family: str) -> str:
    name = family.lower()
    if any(value in name for value in ("flow", "large_trade", "price_micro")):
        return "alpha_signal"
    if any(value in name for value in ("activity", "liquidity", "volume")):
        return "liquidity_control"
    if any(value in name for value in ("funding", "crowding", "position")):
        return "regime"
    if any(value in name for value in ("cross_symbol", "cross_asset", "listing_age")):
        return "risk_control"
    return "latent_representation"


def build_core_pack(
    census: pd.DataFrame,
    token_catalog: pd.DataFrame,
    *,
    minimum_size: int = 80,
    target_size: int = 120,
    maximum_size: int = 160,
) -> list[dict[str, Any]]:
    scored = census.copy()
    scored["score"] = (
        scored["residual_mi_excess"]
        + 0.5 * scored["mutual_information_excess"]
        + 0.25 * scored["block_q25"]
        - 0.05 * scored["max_redundancy_spearman"]
    )
    adequate = scored.loc[
        (scored["coverage_ratio"] >= 0.7)
        & (scored["normalized_value_entropy"] > 0.05)
        & (scored["missingness_flag"] == "")
    ].copy()
    baseline = adequate.loc[adequate["runtime_loaded"]].sort_values("score", ascending=False)
    remainder = adequate.loc[~adequate.index.isin(baseline.index)].sort_values(
        ["family", "score"], ascending=[True, False]
    )
    selected = list(baseline.to_dict("records"))
    groups = {key: group.to_dict("records") for key, group in remainder.groupby("family")}
    while groups and len(selected) < min(75, target_size):
        for family in sorted(tuple(groups)):
            if groups[family]:
                selected.append(groups[family].pop(0))
            if not groups[family]:
                groups.pop(family)
            if len(selected) >= min(75, target_size):
                break

    selected_ids = {row["field_id"] for row in selected}
    allowed = {
        ("Delta", 4), ("Delta", 24), ("Delta", 72),
        ("ZScore", 24), ("ZScore", 72),
        ("TSMean", 4), ("TSMean", 24), ("Decay", 24),
    }
    derived = token_catalog.loc[token_catalog["token_kind"] == "DERIVED"].copy()
    candidates = []
    base_scores = adequate.set_index("field_id")["score"].to_dict()
    for row in derived.to_dict("records"):
        dependencies = [part.strip() for part in str(row["base_dependencies"]).split(";")]
        key = (str(row["transform"]), int(row["window_hours"]))
        if key not in allowed or not dependencies or not set(dependencies).issubset(selected_ids):
            continue
        candidates.append(
            {
                **row,
                "score": float(np.mean([base_scores.get(field, 0.0) for field in dependencies]))
                - 0.0001 * len(dependencies),
            }
        )
    candidates.sort(key=lambda row: (-row["score"], row["field_id"]))

    output: list[dict[str, Any]] = []
    seen_tokens: set[str] = set()
    for row in selected:
        token_id = f"FIELD:{row['field_id']}"
        if token_id in seen_tokens:
            continue
        output.append(
            {
                "token_id": token_id,
                "field_id": row["field_id"],
                "token_kind": "BASE",
                "context_id": row["context_id"],
                "family": row["family"],
                "role": role_for_family(row["family"]),
                "materialization": "CURRENT_CONTEXT_AVAILABLE",
                "evidence_score": float(row["score"]),
                "redundancy_cluster_id": row["redundancy_cluster_id"],
            }
        )
        seen_tokens.add(token_id)
    for row in candidates:
        if len(output) >= target_size:
            break
        if row["token_id"] in seen_tokens:
            continue
        output.append(
            {
                "token_id": row["token_id"],
                "field_id": row["field_id"],
                "token_kind": "DERIVED",
                "context_id": "CORE3_MICROSTRUCTURE_PILOT",
                "family": row["family"],
                "role": "interaction" if ";" in row["base_dependencies"] else role_for_family(row["family"]),
                "materialization": "LAZY_AFTER_CONTEXT_QUALIFICATION",
                "evidence_score": float(row["score"]),
                "base_dependencies": row["base_dependencies"],
                "transform": row["transform"],
                "window_hours": int(row["window_hours"]),
            }
        )
        seen_tokens.add(row["token_id"])
    if len(output) < minimum_size:
        raise ValueError(f"qualified core pack underfilled: {len(output)} < {minimum_size}")
    return output[:maximum_size]


def payload_sha256(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()
