"""dismech models as the models list of a source node, by scripts/source_models.py, and
the model checks of scripts/check_source_nodes.py.

The script imports dismech's own iter_model_links and entity_refs from a dismech
checkout rather than repeating them, so the tests that run it need one, at
$DISMECH_ROOT (or ~/Developer/dismech), and are skipped without it, as in CI. The
comparison of a recorded list with dismech's current one needs no checkout and is
tested on its own.
"""

import importlib.util
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source_models = _load("source_models")
check_source_nodes = _load("check_source_nodes")
ENTRY = "Contact_Dermatitis"
PRIMING = "Allergen-specific T-cell priming"
ROOT = source_models.dismech_root(None)
needs_dismech = pytest.mark.skipif(
    not (ROOT / "src" / "dismech" / "model_links.py").exists()
    or not (ROOT / "kb" / "disorders" / f"{ENTRY}.yaml").exists(),
    reason=f"no dismech checkout at {ROOT}",
)


def ke272_models() -> list[dict]:
    record = yaml.safe_load((REPO_ROOT / "data/key_events/KE-272.yaml").read_text())
    return record["aggregation"]["source_nodes"][0]["models"]


def model(ref: str, relationship: str | None = "MEASURES") -> dict:
    entry, rest = ref.split(":", 1)
    section, name = rest.split("#", 1)
    item = {"model_ref": ref, "model_section": section, "model_name": name}
    if relationship:
        item["source_relationship"] = relationship
    return item


LLNA = f"{ENTRY}:animal_models#Mouse local lymph node assay"
TCELL = f"{ENTRY}:experimental_models#Human T-cell priming assay"


def test_an_unchanged_list_has_no_differences():
    items = [model(TCELL, "RECAPITULATES"), model(LLNA)]
    assert check_source_nodes.model_differences(ENTRY, items, items, lambda ref: True) == []


def test_a_removed_or_renamed_model_is_reported():
    found = check_source_nodes.model_differences(ENTRY, [model(LLNA)], [], lambda ref: False)
    assert found == [f"model {LLNA}: renamed or removed in dismech"]


def test_a_model_no_longer_linked_to_the_node_is_reported():
    found = check_source_nodes.model_differences(ENTRY, [model(LLNA)], [], lambda ref: True)
    assert found == [f"model {LLNA}: no longer linked to this node in dismech"]


def test_a_changed_relationship_is_reported_once():
    found = check_source_nodes.model_differences(
        ENTRY, [model(LLNA, "MEASURES")], [model(LLNA, "PERTURBS")], lambda ref: True)
    assert found == [f"model {LLNA}: source_relationship 'MEASURES' here, 'PERTURBS' in dismech"]


def test_a_newly_linked_model_and_a_bad_ref_are_reported():
    bad = model(LLNA) | {"model_name": "Something else"}
    found = check_source_nodes.model_differences(
        ENTRY, [bad], [model(LLNA), model(TCELL, "RECAPITULATES")], lambda ref: True)
    assert f"model {LLNA!r} does not agree with model_section and model_name" in found
    assert f"model {TCELL}: dismech now also links it to this node (RECAPITULATES)" in found


def test_rendering_an_empty_list_says_so():
    assert source_models.render([], []) == "# dismech links no curated model to this node\n"


def test_rendered_list_loads_back_without_wrapping_long_refs():
    long = model(f"{ENTRY}:experimental_models#" + "A very long model name " * 6)
    out = source_models.render([long], [])
    assert yaml.safe_load(out) == {"models": [long]}
    assert len(out.splitlines()) == 5


@needs_dismech
def test_the_ke272_models_are_reproduced_from_dismech():
    items, comments = source_models.models_for_node(ROOT, ENTRY, PRIMING)
    assert items == ke272_models()
    assert comments == []


@needs_dismech
def test_a_node_with_no_linked_model_gives_an_empty_list():
    items, _ = source_models.models_for_node(ROOT, ENTRY, "Covalent hapten-protein adduct formation")
    assert items == []


@needs_dismech
def test_an_unknown_node_lists_the_entrys_nodes():
    with pytest.raises(SystemExit, match="Skin innate immune activation"):
        source_models.models_for_node(ROOT, ENTRY, "No such node")


@needs_dismech
def test_the_drift_check_passes_ke272_and_notes_a_node_with_no_list(tmp_path):
    record = yaml.safe_load((REPO_ROOT / "data/key_events/KE-272.yaml").read_text())
    node = record["aggregation"]["source_nodes"][0]
    bare = {k: v for k, v in node.items() if k != "models"}
    for name, item in (("KE-1.yaml", node), ("KE-2.yaml", bare)):
        (tmp_path / name).write_text(yaml.safe_dump({"aggregation": {"source_nodes": [item]}}))
    problems, checked, notes = check_source_nodes.check_with_notes(tmp_path, ROOT)
    assert checked == 2
    assert not [p for p in problems if "model" in p]
    assert notes == [f"KE-2.yaml: {ENTRY}#{PRIMING}: no models list; dismech links 2 curated model(s)"]
