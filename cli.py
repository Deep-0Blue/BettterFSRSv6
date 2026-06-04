"""CLI entry point for benchmarking."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bettter_fsrs.benchmark.evaluate import evaluate_items
from bettter_fsrs.fsrs.improved import BetterFSRS6
from bettter_fsrs.parse.anki_sqlite import RevlogQuery, load_revlog_entries
from bettter_fsrs.parse.convert import anki_to_fsrs_items


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark FSRS-6 baseline and optional BetterFSRS6 on an Anki collection."
    )
    parser.add_argument("collection", type=Path, help="Path to collection.anki2 / .anki21")
    parser.add_argument("--timezone", default="Asia/Shanghai")
    parser.add_argument("--fit", action="store_true", help="Fit BetterFSRS6 (requires scipy)")
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args(argv)

    revlogs = load_revlog_entries(args.collection, RevlogQuery())
    items = anki_to_fsrs_items(revlogs, timezone=args.timezone)
    if not items:
        print("No FSRS items from revlog.", file=sys.stderr)
        return 1

    baseline = evaluate_items(items)
    report = {
        "n_revlog_rows": len(relogs),
        "n_fsrs_items": baseline.n_items,
        "baseline": {"log_loss": baseline.log_loss, "rmse_bins": baseline.rmse_bins},
    }
    print(f"Revlog rows: {len(revlogs)}")
    print(f"FSRS items:  {baseline.n_items}")
    print(f"Baseline log_loss:  {baseline.log_loss:.6f}")
    print(f"Baseline rmse_bins: {baseline.rmse_bins:.6f}")

    if args.fit:
        model = BetterFSRS6.fit(items)
        cmp = model.compare_to_baseline()
        report["better"] = {
            "log_loss": cmp["fitted"].log_loss,
            "rmse_bins": cmp["fitted"].rmse_bins,
            "parameters": model.w,
        }
        print(f"Better  log_loss:  {cmp['fitted'].log_loss:.6f}")
        print(f"Better  rmse_bins: {cmp['fitted'].rmse_bins:.6f}")

    if args.output_json:
        args.output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
