# BettterFSRSv6

Hey guys this is a modular toolkit to **parse Anki SQLite revlogs**, run a **baseline FSRS-6 benchmark** (log-loss + binned RMSE), and **fit a personalized BetterFSRS6** on your review history.

## Install

```bash
cd BettterFSRSv6
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick start

```bash
# Baseline FSRS-6 metrics on your collection
python scripts/benchmark.py ~/.local/share/Anki2/User\ 1/collection.anki21

# Also fit personalized weights (needs scipy)
python scripts/benchmark.py path/to/collection.anki21 --fit
```

## Python API

```python
from bettter_fsrs import (
    BetterFSRS6,
    FSRS6,
    benchmark_collection,
    evaluate_items,
)
from bettter_fsrs.parse import anki_to_fsrs_items, load_revlog_entries

revlogs = load_revlog_entries("collection.anki21")
items = anki_to_fsrs_items(revlogs, timezone="UTC")

baseline = evaluate_items(items)  # log_loss, rmse_bins
model = BetterFSRS6.fit(items)
```

## Layout

| Module | Role |
|--------|------|
| `bettter_fsrs/parse/` | SQLite revlog reader, filters, Anki → FSRS item conversion |
| `bettter_fsrs/fsrs/core.py` | FSRS-6 inference (default 21 weights) |
| `bettter_fsrs/fsrs/improved.py` | L-BFGS-B personalization on your logs |
| `bettter_fsrs/benchmark/` | log-loss & RMSE (bins), matching fsrs-rs evaluation |

## Metrics

- **log_loss**: recency-weighted binary cross-entropy between predicted retrievability and recall (rating ≠ Again).
- **rmse_bins**: weighted RMSE of mean predicted vs mean actual recall per calibration bin (delta_t, review count, lapse count).

## Tests

```bash
pytest -q
```

## License

MIT — see [LICENSE](LICENSE).
