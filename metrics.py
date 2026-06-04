from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass

import numpy as np

from bettter_fsrs.types import FSRSItem


@dataclass(frozen=True, slots=True)
class BinAggregate:
    predicted_sum: float = 0.0
    actual_sum: float = 0.0
    count: float = 0.0
    weight: float = 0.0


def log_loss(
    predictions: np.ndarray,
    labels: np.ndarray,
    weights: np.ndarray | None = None,
) -> float:
    """Weighted binary cross-entropy (matches fsrs-rs BCELoss Reduction::Auto)."""
    if len(predictions) == 0:
        raise ValueError("Cannot compute log loss on empty data")

    p = np.clip(predictions.astype(np.float64), 1e-7, 1.0 - 1e-7)
    y = labels.astype(np.float64)
    w = np.ones_like(y) if weights is None else weights.astype(np.float64)
    loss = -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))
    return float(np.sum(loss * w) / np.sum(w))


def rmse_bins(
    predictions: np.ndarray,
    labels: np.ndarray,
    items: list[FSRSItem],
    weights: np.ndarray | None = None,
) -> float:
    """RMSE of binned predicted vs empirical recall (fsrs-rs r_matrix)."""
    if len(predictions) != len(labels) or len(predictions) != len(items):
        raise ValueError("predictions, labels, and items must have equal length")

    matrix: dict[tuple[int, int, int], BinAggregate] = defaultdict(BinAggregate)
    default_w = 1.0
    for idx, item in enumerate(items):
        bin_key = item.r_matrix_index()
        agg = matrix[bin_key]
        w = default_w if weights is None else float(weights[idx])
        matrix[bin_key] = BinAggregate(
            predicted_sum=agg.predicted_sum + float(predictions[idx]),
            actual_sum=agg.actual_sum + float(labels[idx]),
            count=agg.count + 1.0,
            weight=agg.weight + w,
        )

    if not matrix:
        return float("nan")

    total = 0.0
    weight_sum = 0.0
    for agg in matrix.values():
        pred_mean = agg.predicted_sum / agg.count
        real_mean = agg.actual_sum / agg.count
        total += (pred_mean - real_mean) ** 2 * agg.weight
        weight_sum += agg.weight
    return math.sqrt(total / weight_sum) if weight_sum else float("nan")


def recency_weights(n: int) -> np.ndarray:
    """Recency weights used by fsrs-rs evaluate()."""
    if n == 0:
        return np.array([])
    length = max(n - 1, 1)
    idx = np.arange(n, dtype=np.float64)
    return 0.25 + 0.75 * (idx / length) ** 3
