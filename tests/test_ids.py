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


# Assays and test guidelines (issue #45): a Key Event's event.assays and an Assay's
# events must agree, and every id must have a record.


def assay_setup(tmp_path: Path, *, assay_events=(396,), event_assays=(5,), assay_guidelines=(1,),
                event_guidelines=(1,), assay_record_id="enviromech:assay-0005", assay_number=5,
                observation_assay=None) -> list[str]:
    assay = {"id": assay_number, "title": "DPRA", "events": list(assay_events)}
    if assay_guidelines:
        assay["test_guidelines"] = list(assay_guidelines)
    write(tmp_path / "assays", "ASSAY-0005.yaml",
          {"id": assay_record_id, "assay": assay, "mapping_reference": "PMID:38385441"})
    write(tmp_path / "test_guidelines", "TG-0001.yaml",
          {"id": "enviromech:tg-0001", "test_guideline": {"id": 1, "short_title": "OECD TG 442C"}})
    event = {"id": 396, "title": "Covalent Binding, Protein", "assays": list(event_assays)}
    if event_guidelines:
        event["test_guidelines"] = list(event_guidelines)
    write(tmp_path / "key_events", "KE-396.yaml", {"id": "aop.events:396", "event": event})
    (tmp_path / "observations").mkdir(exist_ok=True)
    if observation_assay is not None:
        write(tmp_path / "observations", "obs.yaml",
              {"observation": {"id": 1, "assay_id": {"id": observation_assay, "title": "other"}}})
    return check_ids.check_assays(tmp_path / "assays", tmp_path / "test_guidelines",
                                  tmp_path / "key_events", tmp_path / "observations")


def test_matching_assays_pass(tmp_path):
    assert assay_setup(tmp_path) == []


def test_the_real_records_pass():
    root = REPO_ROOT / "data"
    assert check_ids.check_assays(root / "assays", root / "test_guidelines",
                                  root / "key_events", root / "observations") == []


def test_assay_id_not_the_record_number_fails(tmp_path):
    found = assay_setup(tmp_path, assay_number=6, event_assays=(6,))
    assert any("assay.id is 6 but the record id" in p for p in found)


def test_key_event_naming_an_unknown_assay_fails(tmp_path):
    found = assay_setup(tmp_path, event_assays=(5, 9))
    assert any("assay id 9 has no record" in p for p in found)


def test_one_direction_only_fails(tmp_path):
    found = assay_setup(tmp_path, event_assays=(), event_guidelines=())
    assert any("does not list assay 5 in event.assays" in p for p in found)
    (tmp_path / "b").mkdir()
    found = assay_setup(tmp_path / "b", assay_events=())
    assert any("does not list Key Event 396 in assay.events" in p for p in found)


def test_guidelines_must_be_those_of_the_assays(tmp_path):
    found = assay_setup(tmp_path, event_guidelines=())
    assert any("are not the guidelines of its assays" in p for p in found)


def test_unknown_guideline_fails(tmp_path):
    found = assay_setup(tmp_path, assay_guidelines=(2,), event_guidelines=(2,))
    assert any("test guideline id 2 has no record" in p for p in found)


def test_assay_id_already_an_observations_assay_fails(tmp_path):
    found = assay_setup(tmp_path, observation_assay=5)
    assert any("already the Assay of obs.yaml" in p for p in found)
