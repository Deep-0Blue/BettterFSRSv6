from __future__ import annotations

import math
from dataclasses import dataclass
from enum import IntEnum


class RevlogReviewKind(IntEnum):
    LEARNING = 0
    REVIEW = 1
    RELEARNING = 2
    FILTERED = 3
    MANUAL = 4
    RESCHEDULED = 5


@dataclass(frozen=True, slots=True)
class RevlogEntry:
    """One row from Anki's revlog table."""

    id: int
    cid: int
    usn: int
    button_chosen: int
    interval: int
    last_interval: int
    ease_factor: int
    taken_millis: int
    review_kind: RevlogReviewKind

    @classmethod
    def from_row(cls, row: tuple) -> RevlogEntry:
        return cls(
            id=row[0],
            cid=row[1],
            usn=row[2],
            button_chosen=row[3],
            interval=row[4],
            last_interval=row[5],
            ease_factor=row[6],
            taken_millis=row[7],
            review_kind=RevlogReviewKind(row[8]),
        )


@dataclass(frozen=True, slots=True)
class FSRSReview:
    rating: int
    delta_t: int


@dataclass(slots=True)
class FSRSItem:
    reviews: list[FSRSReview]

    def history(self) -> list[FSRSReview]:
        return self.reviews[:-1]

    def current(self) -> FSRSReview:
        return self.reviews[-1]

    def long_term_review_cnt(self) -> int:
        return sum(1 for r in self.reviews if r.delta_t > 0)

    def r_matrix_index(self) -> tuple[int, int, int]:
        """Calibration bin index used by fsrs-rs (delta_t, length, lapse)."""
        delta_t = float(self.current().delta_t)
        delta_t_bin = int(
            round(
                2.48
                * (3.62 ** math.floor(math.log(max(delta_t, 1e-9), 3.62)))
                * 100.0
            )
        )
        length = float(self.long_term_review_cnt() + 1)
        length_bin = int(round(1.99 * (1.89 ** math.floor(math.log(length, 1.89)))))
        lapse = sum(
            1 for r in self.history() if r.rating == 1 and r.delta_t > 0
        )
        if lapse == 0:
            return delta_t_bin, length_bin, 0
        lapse_bin = int(
            round(1.65 * (1.73 ** math.floor(math.log(float(lapse), 1.73))))
        )
        return delta_t_bin, length_bin, lapse_bin


@dataclass(frozen=True, slots=True)
class MemoryState:
    stability: float
    difficulty: float
