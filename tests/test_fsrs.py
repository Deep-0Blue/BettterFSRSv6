import math

import pytest

from bettter_fsrs.fsrs.core import DEFAULT_PARAMETERS, FSRS6
from bettter_fsrs.types import FSRSItem, FSRSReview, MemoryState


def test_default_parameters_length():
    assert len(DEFAULT_PARAMETERS) == 21


def test_retrievability_at_zero_elapsed():
    model = FSRS6()
    r = model.retrievability(stability=2.0, elapsed_days=0.0)
    assert r == pytest.approx(1.0)


def test_forward_matches_first_rating_init():
    model = FSRS6()
    state = model.memory_state_after_history([FSRSReview(rating=3, delta_t=0)])
    assert state.stability == pytest.approx(DEFAULT_PARAMETERS[2])
    assert state.difficulty == pytest.approx(
        DEFAULT_PARAMETERS[4] - math.exp(DEFAULT_PARAMETERS[5] * 2) + 1.0
    )


def test_predict_item_is_probability(sample_fsrs_items):
    model = FSRS6()
    for item in sample_fsrs_items:
        p = model.predict_item(item)
        assert 0.0 < p < 1.0


def test_step_after_recall_increases_stability():
    model = FSRS6()
    state = MemoryState(stability=5.0, difficulty=5.0)
    next_state = model._step(5, 3, state, nth=2)
    assert next_state.stability > state.stability


def test_memory_state_with_history():
    model = FSRS6()
    reviews = [
        FSRSReview(rating=4, delta_t=0),
        FSRSReview(rating=3, delta_t=5),
        FSRSReview(rating=3, delta_t=10),
    ]
    state = model.memory_state_after_history(reviews)
    assert state.stability >= 0.001
    assert 1.0 <= state.difficulty <= 10.0
