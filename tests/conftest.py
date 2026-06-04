from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from bettter_fsrs.types import FSRSItem, FSRSReview, RevlogEntry, RevlogReviewKind


@pytest.fixture
def sample_fsrs_items() -> list[FSRSItem]:
    return [
        FSRSItem(
            reviews=[
                FSRSReview(rating=4, delta_t=0),
                FSRSReview(rating=3, delta_t=3),
            ]
        ),
        FSRSItem(
            reviews=[
                FSRSReview(rating=4, delta_t=0),
                FSRSReview(rating=3, delta_t=5),
                FSRSReview(rating=3, delta_t=10),
            ]
        ),
        FSRSItem(
            reviews=[
                FSRSReview(rating=3, delta_t=0),
                FSRSReview(rating=3, delta_t=2),
                FSRSReview(rating=1, delta_t=4),
            ]
        ),
    ]


@pytest.fixture
def anki_db_path(tmp_path: Path) -> Path:
    db = tmp_path / "collection.anki21"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE cards (
            id INTEGER PRIMARY KEY,
            nid INTEGER NOT NULL,
            did INTEGER NOT NULL,
            ord INTEGER NOT NULL,
            mod INTEGER NOT NULL,
            usn INTEGER NOT NULL,
            type INTEGER NOT NULL,
            queue INTEGER NOT NULL,
            due INTEGER NOT NULL,
            ivl INTEGER NOT NULL,
            factor INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            lapses INTEGER NOT NULL,
            left INTEGER NOT NULL,
            odue INTEGER NOT NULL,
            odid INTEGER NOT NULL,
            flags INTEGER NOT NULL,
            data TEXT NOT NULL
        );
        CREATE TABLE revlog (
            id INTEGER PRIMARY KEY,
            cid INTEGER NOT NULL,
            usn INTEGER NOT NULL,
            ease INTEGER NOT NULL,
            ivl INTEGER NOT NULL,
            lastIvl INTEGER NOT NULL,
            factor INTEGER NOT NULL,
            time INTEGER NOT NULL,
            type INTEGER NOT NULL
        );
        """
    )
    cid = 1001
    conn.execute(
        "INSERT INTO cards VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            cid,
            1,
            1,
            0,
            0,
            -1,
            2,
            2,
            0,
            10,
            2500,
            2,
            0,
            0,
            0,
            0,
            0,
            "",
        ),
    )
    # Two learning steps same day, then review 5 days later (UTC, 0h rollover).
    base = 1_700_000_000_000
    rows = [
        (base, cid, -1, 3, -600, -600, 0, 2000, 0),
        (base + 60_000, cid, -1, 3, -600, -600, 2500, 1500, 0),
        (base + 5 * 86_400_000, cid, -1, 3, 10, 1, 2500, 1800, 1),
        (base + 15 * 86_400_000, cid, -1, 2, 20, 10, 2500, 2200, 1),
    ]
    conn.executemany(
        "INSERT INTO revlog (id,cid,usn,ease,ivl,lastIvl,factor,time,type) VALUES (?,?,?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()
    conn.close()
    return db


@pytest.fixture
def card_revlog_sequence() -> list[RevlogEntry]:
    base = 1_700_000_000_000
    cid = 42
    return [
        RevlogEntry(
            id=base,
            cid=cid,
            usn=-1,
            button_chosen=3,
            interval=-600,
            last_interval=-600,
            ease_factor=0,
            taken_millis=1000,
            review_kind=RevlogReviewKind.LEARNING,
        ),
        RevlogEntry(
            id=base + 86_400_000,
            cid=cid,
            usn=-1,
            button_chosen=3,
            interval=1,
            last_interval=-600,
            ease_factor=2500,
            taken_millis=1000,
            review_kind=RevlogReviewKind.LEARNING,
        ),
        RevlogEntry(
            id=base + 6 * 86_400_000,
            cid=cid,
            usn=-1,
            button_chosen=3,
            interval=5,
            last_interval=1,
            ease_factor=2500,
            taken_millis=1000,
            review_kind=RevlogReviewKind.REVIEW,
        ),
    ]
