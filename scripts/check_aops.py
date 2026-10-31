"""Check the rules on an AOP's Key Events that the schema cannot express.

    python scripts/check_aops.py [AOP_DIRECTORY [KEY_EVENT_DIRECTORY]]

For every AOP record under AOP_DIRECTORY (default data/aops), reading each Key
Event's level of biological organization from its record under
KEY_EVENT_DIRECTORY (default data/key_events):

- the record id is aop:<number> and aop.id is that number;
- the AOP has at least one Key Event, in aop.events;
- every Key Event named has a record, and is named once;
- the AOP has exactly one Molecular Initiating Event, and it is at the
  Molecular level;
- the AOP has at most one Adverse Outcome at each level of biological
  organization.

Exits 1 and lists every problem if any check fails.
"""

import re
import sys
from collections import Counter
from pathlib import Path

import yaml

RECORD_ID = re.compile(r"^aop:(\d+)$")
MIE = "MolecularInitiatingEvent"
AO = "AdverseOutcome"


def levels(directory: Path) -> dict[int, str | None]:
    """Each Key Event record's AOP-Wiki id (event.id), and its level of biological organization."""
    found: dict[int, str | None] = {}
    for path in sorted(directory.glob("*.yaml")):
        event = (yaml.safe_load(path.read_text()) or {}).get("event") or {}
        found[event.get("id")] = (event.get("biological_organization_id") or {}).get("term")
    return found


def check(directory: Path, key_events: Path) -> list[str]:
    problems: list[str] = []
    level_of = levels(key_events)

    for path in sorted(directory.glob("*.yaml")):
        record = yaml.safe_load(path.read_text()) or {}
        name = path.name

        match = RECORD_ID.match(str(record.get("id", "")))
        aop_id = (record.get("aop") or {}).get("id")
        if not match:
            problems.append(f"{name}: record id {record.get('id')!r} is not aop:<number>")
        elif int(match.group(1)) != aop_id:
            problems.append(
                f"{name}: aop.id is {aop_id!r} but the record id {record['id']} gives {int(match.group(1))}"
            )

        members = (record.get("aop") or {}).get("events") or []
        if not members:
            problems.append(f"{name}: aop.events names no Key Event")
        for event, count in Counter(m.get("event_id") for m in members).items():
            if count > 1:
                problems.append(f"{name}: Key Event {event} is named {count} times")
        for m in members:
            if m.get("event_id") not in level_of:
                problems.append(f"{name}: Key Event {m.get('event_id')} has no record under {key_events}")

        mies = [m.get("event_id") for m in members if m.get("type") == MIE]
        if len(mies) != 1:
            problems.append(f"{name}: an AOP has one Molecular Initiating Event, found {len(mies)}: {mies}")
        for event in mies:
            level = level_of.get(event)
            if event in level_of and level != "Molecular":
                problems.append(
                    f"{name}: the Molecular Initiating Event {event} is at level {level!r}, not Molecular"
                )

        aos_by_level: dict[str | None, list[int]] = {}
        for m in members:
            if m.get("type") == AO and m.get("event_id") in level_of:
                aos_by_level.setdefault(level_of[m["event_id"]], []).append(m["event_id"])
        for level, events in aos_by_level.items():
            if len(events) > 1:
                problems.append(
                    f"{name}: at most one Adverse Outcome per level, "
                    f"found {len(events)} at {level!r}: {events}"
                )

    return problems


def main() -> int:
    directory = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/aops")
    key_events = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/key_events")
    problems = check(directory, key_events)
    for problem in problems:
        print(f"ERROR {problem}")
    count = len(list(directory.glob("*.yaml")))
    print(f"{count} AOP record(s) checked, {len(problems)} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
