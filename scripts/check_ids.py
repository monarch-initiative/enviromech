"""Check the ids EnviroMech assigns to Observations and Assays.

    python scripts/check_ids.py [DIRECTORY]

EnviroMech creates its own Observations and Assays, so it assigns their integer
ids itself, and nothing else keeps them apart. This checks every Observation
record under DIRECTORY (default data/observations):

- an Observation's id is a positive integer and is the number in its record id
  (enviromech:obs-0003 has observation.id 3), so no two Observations share one;
- an Assay's id is a positive integer;
- one Assay id names one Assay: two records that give the same id describe the
  Assay identically;
- one Assay has one id: two records that describe an Assay identically give it
  the same id.

Exits 1 and lists every problem if any check fails.
"""

import re
import sys
from pathlib import Path

import yaml

RECORD_ID = re.compile(r"^enviromech:obs-(\d+)$")


def check(directory: Path) -> list[str]:
    problems: list[str] = []
    observation_files: dict[int, str] = {}
    assay_by_id: dict[int, tuple[dict, str]] = {}
    id_by_assay: dict[str, tuple[int, str]] = {}

    for path in sorted(directory.glob("*.yaml")):
        record = yaml.safe_load(path.read_text()) or {}
        name = path.name
        observation = record.get("observation") or {}

        obs_id = observation.get("id")
        match = RECORD_ID.match(str(record.get("id", "")))
        if not isinstance(obs_id, int) or isinstance(obs_id, bool) or obs_id < 1:
            problems.append(f"{name}: observation.id must be a positive integer, found {obs_id!r}")
        else:
            if not match:
                problems.append(f"{name}: record id {record.get('id')!r} is not enviromech:obs-<number>")
            elif int(match.group(1)) != obs_id:
                problems.append(
                    f"{name}: observation.id is {obs_id} but the record id {record['id']} gives {int(match.group(1))}"
                )
            if obs_id in observation_files:
                problems.append(f"{name}: observation.id {obs_id} is already used by {observation_files[obs_id]}")
            else:
                observation_files[obs_id] = name

        assay = observation.get("assay_id")
        if assay is None:
            continue
        assay_id = assay.get("id")
        if not isinstance(assay_id, int) or isinstance(assay_id, bool) or assay_id < 1:
            problems.append(f"{name}: assay_id.id must be a positive integer, found {assay_id!r}")
            continue
        described = {k: v for k, v in assay.items() if k != "id"}
        key = yaml.safe_dump(described, sort_keys=True)

        if assay_id in assay_by_id and assay_by_id[assay_id][0] != described:
            problems.append(
                f"{name}: assay id {assay_id} describes a different Assay in {assay_by_id[assay_id][1]}"
            )
        assay_by_id.setdefault(assay_id, (described, name))

        if key in id_by_assay and id_by_assay[key][0] != assay_id:
            problems.append(
                f"{name}: the same Assay has id {id_by_assay[key][0]} in {id_by_assay[key][1]} and {assay_id} here"
            )
        id_by_assay.setdefault(key, (assay_id, name))

    return problems


def main() -> int:
    directory = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/observations")
    problems = check(directory)
    for problem in problems:
        print(f"ERROR {problem}")
    count = len(list(directory.glob("*.yaml")))
    print(f"{count} Observation record(s) checked, {len(problems)} id problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
