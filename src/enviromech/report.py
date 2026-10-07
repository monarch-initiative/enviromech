"""Corpus statistics, counted from the records themselves.

    python -m <slug>.report [--json]

Quote numbers from this, never from prose.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

from .paths import KEY_EVENTS_DIR, MECH_NAME, RECORDS_DIR, REPO_ROOT
from .validate import iter_records, load


def _walk(obj, counts: Counter) -> None:
    if isinstance(obj, dict):
        if "reference" in obj and "supports" in obj:
            counts["evidence_items"] += 1
            if obj.get("snippet"):
                counts["evidence_with_snippet"] += 1
        if "preferred_term" in obj:
            counts["descriptors"] += 1
            if obj.get("term"):
                counts["descriptors_bound"] += 1
        for v in obj.values():
            _walk(v, counts)
    elif isinstance(obj, list):
        for v in obj:
            _walk(v, counts)


def key_events() -> dict:
    """Counts of the Key Event records: how many, by review status, and by the
    outcome of screening their level of biological organization."""
    paths = iter_records(KEY_EVENTS_DIR)
    status: Counter = Counter()
    screening: Counter = Counter()
    aggregated = 0
    for p in paths:
        data = load(p) or {}
        status[data.get("status", "UNSET")] += 1
        screening[(data.get("level_screening") or {}).get("outcome", "UNSET")] += 1
        aggregated += 1 if data.get("aggregation") else 0
    return {
        "key_events_dir": str(KEY_EVENTS_DIR.relative_to(REPO_ROOT)),
        "key_events": len(paths),
        "key_events_by_status": dict(sorted(status.items())),
        "key_events_by_level_screening": dict(sorted(screening.items())),
        "key_events_with_aggregation": aggregated,
    }


def compute() -> dict:
    paths = iter_records()
    status: Counter = Counter()
    counts: Counter = Counter()
    for p in paths:
        data = load(p) or {}
        if not isinstance(data, dict):  # not a record; just validate reports it
            continue
        status[data.get("status", "UNSET")] += 1
        counts["mechanism_nodes"] += len(data.get("mechanisms") or [])
        counts["discussions"] += len(data.get("discussions") or [])
        _walk(data, counts)
    return {
        "mech": MECH_NAME,
        "records_dir": str(RECORDS_DIR.relative_to(REPO_ROOT)),
        "records": len(paths),
        "by_status": dict(sorted(status.items())),
        **{k: counts[k] for k in sorted(counts)},
        **key_events(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    stats = compute()
    if args.json:
        print(json.dumps(stats, indent=2))
    else:
        for k, v in stats.items():
            print(f"{k:30} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
