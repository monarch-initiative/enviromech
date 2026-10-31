"""Event component ids: EnviroMech's own, checked by scripts/check_ids.py."""

import importlib.util
from pathlib import Path

import yaml

from enviromech.paths import REPO_ROOT

spec = importlib.util.spec_from_file_location("check_ids", REPO_ROOT / "scripts/check_ids.py")
check_ids = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_ids)

MITOCHONDRION = {
    "biological_object_id": {"source": "GO", "source_id": "GO:0005739", "term": "mitochondrion"},
    "biological_action_id": {"term": "functional change"},
}
DECREASED = {
    "biological_process_id": {
        "source": "VT",
        "source_id": "VT:0001947",
        "term": "mucociliary clearance trait",
    },
    "biological_action_id": {"term": "decreased"},
}


def write(directory: Path, name: str, record: dict) -> None:
    directory.mkdir(exist_ok=True)
    (directory / name).write_text(yaml.safe_dump(record))


def component(tmp_path: Path, record_id: str, number, described: dict) -> None:
    write(
        tmp_path / "event_components",
        f"{record_id}.yaml",
        {"id": record_id, "event_component": {"id": number, **described}},
    )


def key_event(tmp_path: Path, number: int, components: list[dict]) -> None:
    write(
        tmp_path / "key_events",
        f"KE-{number}.yaml",
        {"id": f"aop.events:{number}", "event": {"id": number, "event_components": components}},
    )


def problems(tmp_path: Path) -> list[str]:
    for name in ("event_components", "key_events"):
        (tmp_path / name).mkdir(exist_ok=True)
    return check_ids.check_event_components(tmp_path / "event_components", tmp_path / "key_events")


def test_matching_ids_pass(tmp_path):
    component(tmp_path, "enviromech:ec-0001", 1, MITOCHONDRION)
    component(tmp_path, "enviromech:ec-0002", 2, DECREASED)
    key_event(tmp_path, 177, [{"id": 1, **MITOCHONDRION}])
    key_event(tmp_path, 178, [{"id": 1, **MITOCHONDRION}, {"id": 2, **DECREASED}])
    assert problems(tmp_path) == []


def test_id_not_the_record_number_fails(tmp_path):
    component(tmp_path, "enviromech:ec-0001", 2, MITOCHONDRION)
    assert any("gives 1" in p for p in problems(tmp_path))


def test_bad_record_id_fails(tmp_path):
    component(tmp_path, "enviromech:0001", 1, MITOCHONDRION)
    assert any("is not enviromech:ec-<number>" in p for p in problems(tmp_path))


def test_same_combination_twice_fails(tmp_path):
    component(tmp_path, "enviromech:ec-0001", 1, MITOCHONDRION)
    component(tmp_path, "enviromech:ec-0002", 2, MITOCHONDRION)
    assert any("already recorded as id 1" in p for p in problems(tmp_path))


def test_key_event_component_without_id_fails(tmp_path):
    key_event(tmp_path, 177, [MITOCHONDRION])
    assert problems(tmp_path) == ["KE-177.yaml: an event component has no id"]


def test_key_event_component_with_unknown_id_fails(tmp_path):
    key_event(tmp_path, 177, [{"id": 7, **MITOCHONDRION}])
    assert any("id 7 has no record" in p for p in problems(tmp_path))


def test_key_event_component_differing_from_its_record_fails(tmp_path):
    component(tmp_path, "enviromech:ec-0001", 1, MITOCHONDRION)
    key_event(tmp_path, 177, [{"id": 1, **DECREASED}])
    assert any("differs from" in p for p in problems(tmp_path))
