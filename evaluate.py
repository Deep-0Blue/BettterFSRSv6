from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from bettter_fsrs.benchmark.metrics import log_loss, recency_weights, rmse_bins
from bettter_fsrs.fsrs.core import DEFAULT_PARAMETERS, FSRS6
from bettter_fsrs.parse.anki_sqlite import RevlogQuery, load_revlog_entries
from bettter_fsrs.parse.convert import anki_to_fsrs_items
from bettter_fsrs.types import FSRSItem


@dataclass(frozen=True, slots=True)
class ModelEvaluation:
    log_loss: float
    rmse_bins: float
    n_items: int


def evaluate_items(
    items: Sequence[FSRSItem],
    parameters: Sequence[float] | None = None,
    *,
    use_recency_weights: bool = True,
) -> ModelEvaluation:
    if not items:
        raise ValueError("Need at least one FSRS item to evaluate")

    model = FSRS6(parameters or DEFAULT_PARAMETERS)
    preds: list[float] = []
    labels: list[int] = []
    ordered_items: list[FSRSItem] = list(items)

    for item in ordered_items:
        preds.append(model.predict_item(item))
        labels.append(0 if item.current().rating == 1 else 1)

    pred_arr = np.array(preds, dtype=np.float64)
    label_arr = np.array(labels, dtype=np.int64)
    weights = recency_weights(len(items)) if use_recency_weights else None

    return ModelEvaluation(
        log_loss=log_loss(pred_arr, label_arr, weights),
        rmse_bins=rmse_bins(pred_arr, label_arr, ordered_items, weights),
        n_items=len(items),
    )


def benchmark_collection(
    db_path: str | Path,
    parameters: Sequence[float] | None = None,
    *,
    query: RevlogQuery | None = None,
    timezone: str = "Asia/Shanghai",
) -> ModelEvaluation:
    """End-to-end: Anki SQLite → FSRS items → metrics."""
    revlogs = load_revlog_entries(db_path, query)
    items = anki_to_fsrs_items(revlogs, timezone=timezone)
    return evaluate_items(items, parameters)
