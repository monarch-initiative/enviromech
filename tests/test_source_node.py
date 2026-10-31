"""dismech nodes as source_nodes items, by scripts/source_node.py, and the drift check
over them, by scripts/check_source_nodes.py.

The dismech side is tests/data/dismech, two nodes of Contact_Dermatitis laid out as a
dismech checkout. KE-272.yaml's source node was written from the first of them, so it
is the expected output.
"""

import importlib.util
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DISMECH = REPO_ROOT / "tests" / "data" / "dismech"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source_node = _load("source_node")
check_source_nodes = _load("check_source_nodes")
PRIMING = "Allergen-specific T-cell priming"


def ke272_node() -> dict:
    record = yaml.safe_load((REPO_ROOT / "data/key_events/KE-272.yaml").read_text())
    return record["aggregation"]["source_nodes"][0]


def test_the_ke272_source_node_is_reproduced_apart_from_the_curators_notes():
    node = source_node.find_node(DISMECH, "Contact_Dermatitis", PRIMING)
    item, comments = source_node.source_node("Contact_Dermatitis", node)
    expected = {k: v for k, v in ke272_node().items() if k != "notes"}
    assert item == expected
    assert comments == ["no biological_action_id: dismech binds no modifier to the node's processes"]


def test_rendered_item_loads_back_and_carries_the_description(capsys):
    assert source_node.main(["Contact_Dermatitis", PRIMING, "--dismech-root", str(DISMECH)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("# dismech description: During sensitization")
    assert yaml.safe_load(out)[0]["node_name"] == PRIMING


def test_a_node_with_no_scale_or_terms_says_so():
    innate = "Skin innate immune activation during sensitization"
    node = source_node.find_node(DISMECH, "Contact_Dermatitis", innate)
    item, _ = source_node.source_node("Contact_Dermatitis", node)
    assert item["source_level"] == "TISSUE"
    assert item["biological_organization_id"] == {"term": "Tissue"}
    assert "processes" not in item
    item, comments = source_node.source_node("X", {"name": "Bare"})
    assert "source_level" not in item
    assert "dismech records no biological_scale for this node" in comments


@pytest.mark.parametrize(
    "modifiers, expected",
    [
        (["DECREASED"], "decreased"),
        (["ABNORMAL", "ABNORMAL"], "abnormal"),
        (["INCREASED", "DECREASED"], None),
        (["DYSREGULATED"], None),
    ],
)
def test_action_from_process_modifiers(modifiers, expected):
    node = {"name": "N", "biological_processes": [
        {"term": {"id": f"GO:000000{i}", "label": "p"}, "modifier": m} for i, m in enumerate(modifiers)
    ]}
    assert source_node.action(node)[0] == expected


def test_an_unknown_node_lists_the_entrys_nodes():
    with pytest.raises(SystemExit, match="Skin innate immune activation"):
        source_node.find_node(DISMECH, "Contact_Dermatitis", "No such node")


def write_record(directory: Path, node: dict) -> None:
    directory.mkdir(exist_ok=True)
    (directory / "KE-1.yaml").write_text(yaml.safe_dump({"aggregation": {"source_nodes": [node]}}))


def test_drift_check_passes_a_node_that_has_not_changed(tmp_path):
    write_record(tmp_path, ke272_node())
    assert check_source_nodes.check(tmp_path, DISMECH) == ([], 1)


def test_drift_check_reports_changed_terms_labels_and_level(tmp_path):
    node = ke272_node()
    node["source_level"] = "TISSUE"
    node["processes"] = [{"source": "GO", "source_id": "GO:0042110", "term": "an old label"}]
    write_record(tmp_path, node)
    problems, checked = check_source_nodes.check(tmp_path, DISMECH)
    assert checked == 1
    assert any("source_level: 'TISSUE' here, 'CELLULAR' in dismech" in p for p in problems)
    assert any("dismech now also binds GO:0002468" in p for p in problems)
    assert any("GO:0042110 is labelled 'T cell activation' in dismech" in p for p in problems)


def test_drift_check_reports_a_renamed_node_and_a_bad_ref(tmp_path):
    node = ke272_node()
    node["node_name"] = "Renamed node"
    write_record(tmp_path, node)
    problems, _ = check_source_nodes.check(tmp_path, DISMECH)
    assert any("does not agree with source_entry and node_name" in p for p in problems)
    assert any("has no pathophysiology node named 'Renamed node'" in p for p in problems)


def test_drift_check_skips_other_knowledge_bases(tmp_path):
    write_record(tmp_path, {"source_knowledge_base": "elsewhere", "source_entry": "X", "node_name": "Y"})
    assert check_source_nodes.check(tmp_path, DISMECH) == ([], 0)
