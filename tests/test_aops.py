"""AOP records: the rules on an AOP's Key Events, checked by scripts/check_aops.py."""

import importlib.util
from pathlib import Path

import yaml

from enviromech.paths import REPO_ROOT

spec = importlib.util.spec_from_file_location("check_aops", REPO_ROOT / "scripts/check_aops.py")
check_aops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_aops)

LEVELS = {1: "Molecular", 2: "Cellular", 3: "Individual", 4: "Individual", 5: "Population"}


def write(directory: Path, name: str, record: dict) -> None:
    directory.mkdir(exist_ok=True)
    (directory / name).write_text(yaml.safe_dump(record))


def corpus(tmp_path: Path, roles: list[tuple[int, str]]) -> list[str]:
    key_events = tmp_path / "key_events"
    for number, level in LEVELS.items():
        write(
            key_events,
            f"KE-{number}.yaml",
            {
                "id": f"aop.events:{number}",
                "event": {"id": number, "biological_organization_id": {"term": level}},
            },
        )
    aops = tmp_path / "aops"
    write(
        aops,
        "AOP-9.yaml",
        {
            "id": "aop:9",
            "aop": {"id": 9, "events": [{"event_id": n, "type": role} for n, role in roles]},
        },
    )
    return check_aops.check(aops, key_events)


def test_the_corpus_passes():
    assert check_aops.check(REPO_ROOT / "data/aops", REPO_ROOT / "data/key_events") == []


def test_a_linear_aop_passes(tmp_path):
    assert corpus(tmp_path, [(1, "MolecularInitiatingEvent"), (2, "KeyEvent"), (3, "AdverseOutcome")]) == []


def test_one_adverse_outcome_at_each_of_two_levels_passes(tmp_path):
    roles = [(1, "MolecularInitiatingEvent"), (3, "AdverseOutcome"), (5, "AdverseOutcome")]
    assert corpus(tmp_path, roles) == []


def test_no_molecular_initiating_event_fails(tmp_path):
    [problem] = corpus(tmp_path, [(2, "KeyEvent"), (3, "AdverseOutcome")])
    assert "one Molecular Initiating Event, found 0" in problem


def test_two_molecular_initiating_events_fail(tmp_path):
    problems = corpus(tmp_path, [(1, "MolecularInitiatingEvent"), (2, "MolecularInitiatingEvent")])
    assert any("one Molecular Initiating Event, found 2" in p for p in problems)


def test_a_molecular_initiating_event_off_the_molecular_level_fails(tmp_path):
    [problem] = corpus(tmp_path, [(2, "MolecularInitiatingEvent"), (3, "AdverseOutcome")])
    assert "'Cellular', not Molecular" in problem


def test_two_adverse_outcomes_at_one_level_fail(tmp_path):
    roles = [(1, "MolecularInitiatingEvent"), (3, "AdverseOutcome"), (4, "AdverseOutcome")]
    [problem] = corpus(tmp_path, roles)
    assert "at most one Adverse Outcome per level, found 2 at 'Individual'" in problem


def test_a_key_event_with_no_record_fails(tmp_path):
    [problem] = corpus(tmp_path, [(1, "MolecularInitiatingEvent"), (99, "AdverseOutcome")])
    assert "Key Event 99 has no record" in problem


def test_a_key_event_named_twice_fails(tmp_path):
    [problem] = corpus(tmp_path, [(1, "MolecularInitiatingEvent"), (3, "KeyEvent"), (3, "AdverseOutcome")])
    assert "Key Event 3 is named 2 times" in problem


def test_an_aop_with_no_key_events_fails(tmp_path):
    problems = corpus(tmp_path, [])
    assert any("aop.events names no Key Event" in p for p in problems)
