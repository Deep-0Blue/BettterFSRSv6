from bettter_fsrs.parse.anki_sqlite import RevlogQuery, load_revlog_entries
from bettter_fsrs.parse.convert import anki_to_fsrs_items, convert_card_revlog_to_fsrs_items
from bettter_fsrs.parse.revlog import filter_out_manual, remove_revlog_before_last_first_learn
from bettter_fsrs.types import RevlogEntry, RevlogReviewKind


def test_load_revlog_from_sqlite(anki_db_path):
    entries = load_revlog_entries(anki_db_path, RevlogQuery())
    assert len(entries) == 4
    assert all(1 <= e.button_chosen <= 4 for e in entries)


def test_convert_card_produces_long_term_items(card_revlog_sequence):
    items = convert_card_revlog_to_fsrs_items(
        card_revlog_sequence,
        next_day_starts_at_hours=0,
        timezone="UTC",
    )
    assert len(items) == 2
    assert items[-1][1].reviews[-1].delta_t == 5


def test_filter_manual_reschedules():
    entries = [
        RevlogEntry(
            id=1,
            cid=1,
            usn=0,
            button_chosen=3,
            interval=-600,
            last_interval=-60,
            ease_factor=0,
            taken_millis=1,
            review_kind=RevlogReviewKind.LEARNING,
        ),
        RevlogEntry(
            id=2,
            cid=1,
            usn=-1,
            button_chosen=0,
            interval=302,
            last_interval=302,
            ease_factor=2150,
            taken_millis=0,
            review_kind=RevlogReviewKind.MANUAL,
        ),
        RevlogEntry(
            id=3,
            cid=1,
            usn=0,
            button_chosen=3,
            interval=10,
            last_interval=1,
            ease_factor=2500,
            taken_millis=1,
            review_kind=RevlogReviewKind.REVIEW,
        ),
    ]
    filtered = filter_out_manual(entries)
    assert len(filtered) == 2
    assert filtered[-1].review_kind == RevlogReviewKind.REVIEW


def test_remove_before_last_learn():
    entries = [
        RevlogEntry(
            id=10,
            cid=1,
            usn=0,
            button_chosen=3,
            interval=44,
            last_interval=14,
            ease_factor=2000,
            taken_millis=1,
            review_kind=RevlogReviewKind.REVIEW,
        ),
        RevlogEntry(
            id=20,
            cid=1,
            usn=0,
            button_chosen=3,
            interval=-600,
            last_interval=-60,
            ease_factor=2500,
            taken_millis=1,
            review_kind=RevlogReviewKind.LEARNING,
        ),
    ]
    trimmed = remove_revlog_before_last_first_learn(entries)
    assert len(trimmed) == 1
    assert trimmed[0].review_kind == RevlogReviewKind.LEARNING


def test_anki_to_fsrs_items_integration(anki_db_path):
    entries = load_revlog_entries(anki_db_path)
    items = anki_to_fsrs_items(entries, next_day_starts_at_hours=0, timezone="UTC")
    assert len(items) >= 1
    assert all(item.current().delta_t > 0 for item in items)
