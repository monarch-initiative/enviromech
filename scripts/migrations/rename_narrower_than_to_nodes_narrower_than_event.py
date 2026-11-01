"""Rename the AggregationRelationEnum value narrower_than.

The old name said that something was narrower without saying which side, which
was readable only from the value's description. The new name,
nodes_narrower_than_event, names both sides, and leaves room for
nodes_broader_than_event to be added later without the pair being ambiguous.

The value is the only thing this touches. Key Event records carry a header
comment that a YAML round-trip would drop, so the substitution is textual and
every other byte of the file is left alone; the check below parses each file
before and after and refuses to write unless the aggregation_relation value is
the only thing that moved.

Prose that names the old value in a rationale or in notes is a curator's
sentence, not a field, so it is not rewritten here. Run `rg narrower_than data`
afterwards and fix what is left by hand.

    uv run python scripts/migrations/rename_narrower_than_to_nodes_narrower_than_event.py
    uv run python scripts/migrations/rename_narrower_than_to_nodes_narrower_than_event.py --apply
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

OLD = "narrower_than"
NEW = "nodes_narrower_than_event"
REPO_ROOT = Path(__file__).resolve().parents[2]
RECORD_DIRS = ("data/key_events", "data/aops", "data/observations")


def relation_of(text: str) -> str | None:
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        return None
    aggregation = data.get("aggregation")
    if not isinstance(aggregation, dict):
        return None
    return aggregation.get("aggregation_relation")


def changed_elsewhere(before: str, after: str) -> bool:
    """True when anything other than the relation value differs."""
    a = yaml.safe_load(before)
    b = yaml.safe_load(after)
    if isinstance(a, dict) and isinstance(a.get("aggregation"), dict):
        a["aggregation"]["aggregation_relation"] = NEW
    return a != b


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the files")
    args = parser.parse_args()

    changed = 0
    for directory in RECORD_DIRS:
        for path in sorted((REPO_ROOT / directory).glob("*.yaml")):
            before = path.read_text(encoding="utf-8")
            if relation_of(before) != OLD:
                continue
            after = before.replace(
                f"aggregation_relation: {OLD}\n", f"aggregation_relation: {NEW}\n"
            )
            if relation_of(after) != NEW:
                print(f"REFUSED {path}: substitution did not take", file=sys.stderr)
                return 1
            if changed_elsewhere(before, after):
                print(f"REFUSED {path}: something other than the value moved", file=sys.stderr)
                return 1
            changed += 1
            print(f"{'rewrote' if args.apply else 'would rewrite'} {path.relative_to(REPO_ROOT)}")
            if args.apply:
                path.write_text(after, encoding="utf-8")

    if not changed:
        print(f"no record carries aggregation_relation: {OLD}")
    elif not args.apply:
        print(f"\n{changed} record(s); re-run with --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
