import numpy as np
import pytest

from bettter_fsrs.benchmark.evaluate import evaluate_items
from bettter_fsrs.benchmark.metrics import log_loss, recency_weights, rmse_bins
from bettter_fsrs.fsrs.improved import BetterFSRS6
from bettter_fsrs.types import FSRSItem, FSRSReview


def test_log_loss_perfect_prediction():
    p = np.array([0.9, 0.1])
    y = np.array([1, 0])
    loss = log_loss(p, y)
    expected = -(np.log(0.9) + np.log(0.9)) / 2
    assert loss == pytest.approx(expected, rel=1e-5)


def test_rmse_bins_zero_when_prediction_matches_rate():
    item = FSRSItem(reviews=[FSRSReview(4, 0), FSRSReview(3, 5)])
    items = [item, item]
    preds = np.array([1.0, 1.0])
    labels = np.array([1, 1])
    score = rmse_bins(preds, labels, items)
    assert score == pytest.approx(0.0, abs=1e-6)


def test_recency_weights_shape():
    w = recency_weights(5)
    assert len(w) == 5
    assert w[0] < w[-1]


def test_evaluate_items_returns_metrics(sample_fsrs_items):
    result = evaluate_items(sample_fsrs_items, use_recency_weights=False)
    assert result.n_items == len(sample_fsrs_items)
    assert result.log_loss > 0
    assert result.rmse_bins >= 0


def test_better_fsrs_improves_or_matches_baseline(sample_fsrs_items):
    # Expand synthetic set for optimizer
    items = sample_fsrs_items * 40
    model = BetterFSRS6.fit(items, max_iterations=30, sample_size=None)
    cmp = model.compare_to_baseline()
    assert cmp["fitted"].log_loss <= cmp["baseline"].log_loss + 1e-6
