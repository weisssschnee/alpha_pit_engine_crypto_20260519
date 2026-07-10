from __future__ import annotations

import base64
import hashlib
import zlib
from typing import Any

import numpy as np


def canonicalize_weight_orientation(weights: np.ndarray) -> np.ndarray:
    values = np.asarray(weights, dtype=np.float64)
    canonical = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0).copy()
    nonzero = np.flatnonzero(canonical)
    if nonzero.size and canonical.ravel()[nonzero[0]] < 0:
        canonical *= -1.0
    # Multiplying by -1 creates negative zero, which must not split an exact identity.
    canonical[canonical == 0.0] = 0.0
    return canonical


def exact_weight_fingerprint(weights: np.ndarray) -> str:
    canonical = np.ascontiguousarray(canonicalize_weight_orientation(weights), dtype="<f8")
    payload = f"{canonical.shape[0]}x{canonical.shape[1]}|".encode("ascii") + canonical.tobytes(order="C")
    return hashlib.sha256(payload).hexdigest()


def quantized_weight_fingerprint(weights: np.ndarray, decimals: int = 10) -> str:
    canonical = np.ascontiguousarray(np.round(canonicalize_weight_orientation(weights), decimals), dtype="<f8")
    payload = f"{canonical.shape[0]}x{canonical.shape[1]}|q{decimals}|".encode("ascii") + canonical.tobytes(order="C")
    return hashlib.sha256(payload).hexdigest()


def weight_similarity_sketch(weights: np.ndarray, size: int = 512) -> str:
    flat = canonicalize_weight_orientation(weights).ravel(order="C")
    if flat.size == 0:
        sample = np.zeros(size, dtype=np.float32)
    else:
        indices = np.linspace(0, flat.size - 1, min(size, flat.size), dtype=np.int64)
        sample = flat[indices].astype(np.float32, copy=False)
        norm = float(np.linalg.norm(sample))
        if norm > 1e-12:
            sample = sample / norm
    return base64.b64encode(zlib.compress(sample.tobytes(order="C"), level=6)).decode("ascii")


def decode_weight_similarity_sketch(payload: str) -> np.ndarray:
    if not payload:
        return np.asarray([], dtype=np.float32)
    return np.frombuffer(zlib.decompress(base64.b64decode(payload.encode("ascii"))), dtype=np.float32).copy()


def sketch_correlation(left: str, right: str) -> float:
    x = decode_weight_similarity_sketch(left)
    y = decode_weight_similarity_sketch(right)
    if x.size == 0 or y.size == 0 or x.size != y.size:
        return float("nan")
    x_std = float(np.std(x))
    y_std = float(np.std(y))
    if x_std <= 1e-12 or y_std <= 1e-12:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def signal_identity_payload(weights: np.ndarray) -> dict[str, Any]:
    return {
        "signal_weight_exact_fingerprint": exact_weight_fingerprint(weights),
        "signal_weight_quantized_fingerprint": quantized_weight_fingerprint(weights),
        "signal_weight_similarity_sketch": weight_similarity_sketch(weights),
    }
