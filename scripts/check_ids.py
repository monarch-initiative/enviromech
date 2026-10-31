"""Check the ids EnviroMech assigns to Observations, Assays and event components.

    python scripts/check_ids.py [DIRECTORY [EVENT_COMPONENT_DIRECTORY [KEY_EVENT_DIRECTORY]]]

EnviroMech assigns these ids itself, for two different reasons:

- Observations and Assays exist only in EMOD, not in the production AOP-Wiki,
  so the AOP-Wiki XML does not contain them, and EMOD has no XML export to take
  them from. EnviroMech creates its own, and gives them ids.
- Event components are in the AOP-Wiki XML, but the XML does not give their ids.

Because no outside source assigns these ids, this script is the only check that
they are well formed and that no two records share one.

Observations and Assays. Every Observation record under DIRECTORY (default
data/observations) is checked:

- an Observation's id is a positive integer and is the number in its record id
  (enviromech:obs-0003 has observation.id 3), so no two Observations share one;
- an Assay's id is a positive integer;
- one Assay id names one Assay: two records that give the same id describe the
  Assay identically;
- one Assay has one id: two records that describe an Assay identically give it
  the same id.

Event components. Every event component record under EVENT_COMPONENT_DIRECTORY
(default data/event_components) is checked, with the Key Event records under
KEY_EVENT_DIRECTORY (default data/key_events) that use them:

- an event component's id is the number in its record id (enviromech:ec-0001
  has event_component.id 1), so no two share one;
- one combination of action, object and process has one record;
- every event component in a Key Event record has an id, that id has a record,
  and the component is written exactly as that record writes it.

Exits 1 and lists every problem if any check fails.
"""

import re
import sys
from pathlib import Path

import yaml

RECORD_ID = re.compile(r"^enviromech:obs-(\d+)$")
COMPONENT_ID = re.compile(r"^enviromech:ec-(\d+)$")


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
                    f"{name}: observation.id is {obs_id} but the record id {record['id']} "
                    f"gives {int(match.group(1))}"
                )
            if obs_id in observation_files:
                problems.append(
                    f"{name}: observation.id {obs_id} is already used by {observation_files[obs_id]}"
                )
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
                f"{name}: the same Assay has id {id_by_assay[key][0]} in {id_by_assay[key][1]} "
                f"and {assay_id} here"
            )
        id_by_assay.setdefault(key, (assay_id, name))

    return problems


def check_event_components(directory: Path, key_events: Path) -> list[str]:
    problems: list[str] = []
    component_by_id: dict[int, tuple[dict, str]] = {}
    id_by_component: dict[str, tuple[int, str]] = {}

    for path in sorted(directory.glob("*.yaml")):
        record = yaml.safe_load(path.read_text()) or {}
        name = path.name
        component = record.get("event_component") or {}
        component_id = component.get("id")
        match = COMPONENT_ID.match(str(record.get("id", "")))
        if not match:
            problems.append(f"{name}: record id {record.get('id')!r} is not enviromech:ec-<number>")
            continue
        if component_id != int(match.group(1)) or isinstance(component_id, bool):
            problems.append(
                f"{name}: event_component.id is {component_id!r} but the record id {record['id']} "
                f"gives {int(match.group(1))}"
            )
            continue
        if component_id in component_by_id:
            problems.append(
                f"{name}: event_component.id {component_id} is already used by "
                f"{component_by_id[component_id][1]}"
            )
            continue
        described = {k: v for k, v in component.items() if k != "id"}
        key = yaml.safe_dump(described, sort_keys=True)
        if key in id_by_component:
            problems.append(
                f"{name}: the same event component is already recorded as id "
                f"{id_by_component[key][0]} in {id_by_component[key][1]}"
            )
        component_by_id[component_id] = (described, name)
        id_by_component.setdefault(key, (component_id, name))

    for path in sorted(key_events.glob("*.yaml")):
        record = yaml.safe_load(path.read_text()) or {}
        name = path.name
        for component in (record.get("event") or {}).get("event_components") or []:
            component_id = component.get("id")
            described = {k: v for k, v in component.items() if k != "id"}
            if component_id is None:
                problems.append(f"{name}: an event component has no id")
            elif component_id not in component_by_id:
                problems.append(f"{name}: event component id {component_id} has no record under {directory}")
            elif component_by_id[component_id][0] != described:
                problems.append(
                    f"{name}: event component {component_id} differs from {component_by_id[component_id][1]}"
                )

    return problems


def main() -> int:
    directory = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/observations")
    components = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/event_components")
    key_events = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("data/key_events")
    problems = check(directory) + check_event_components(components, key_events)
    for problem in problems:
        print(f"ERROR {problem}")
    count = len(list(directory.glob("*.yaml")))
    component_count = len(list(components.glob("*.yaml")))
    print(
        f"{count} Observation record(s) and {component_count} event component record(s) checked, "
        f"{len(problems)} id problem(s)."
    )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
