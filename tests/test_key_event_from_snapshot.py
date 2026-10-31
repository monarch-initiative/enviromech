"""Key Event records started from an aop_wiki_cli snapshot cache, by scripts/key_event_from_snapshot.py."""

import importlib.util
import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PROCESS = {"source": "GO", "source_id": "GO:0032980", "term": "keratinocyte activation"}
spec = importlib.util.spec_from_file_location(
    "key_event_from_snapshot", REPO_ROOT / "scripts/key_event_from_snapshot.py"
)
kes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kes)


def test_paragraphs_keep_every_cell_of_a_mixed_row():
    html = (
        "<p>Methods <sup><a href='#cite_note-1'>[1]</a></sup>.</p>"
        "<table><tr><td>Method</td><td><p>Reference</p></td></tr>"
        "<tr><td><p>DPRA</p></td><td>TG 442C</td></tr></table>"
    )
    assert kes.paragraphs(html) == ["Methods [1].", "Method; Reference", "DPRA; TG 442C"]


def test_paragraphs_read_a_nested_table_once():
    html = "<table><tr><td><table><tr><td>MRI</td><td>Jiang 2014</td></tr></table></td></tr></table>"
    assert kes.paragraphs(html) == ["MRI; Jiang 2014"]


def test_paragraphs_keep_text_beside_a_block_and_drop_comments():
    html = "<div>Lead text<!--[if supportLists]--><p>Inner</p>tail</div>"
    assert kes.paragraphs(html) == ["Lead text", "Inner", "tail"]


def test_folded_text_reads_back_as_the_paragraphs():
    texts = ["word " * 40, "second paragraph"]
    loaded = yaml.safe_load("\n".join(["event:", *kes.folded("definition", texts)]))
    assert loaded["event"]["definition"] == "\n".join(t.strip() for t in texts)


def event(**extra):
    base = {
        "ke_id": "9001",
        "title": "Activation, Example cells",
        "short_name": "Activation, Example cells",
        "level_of_biological_organization": "Cellular",
        "cell_term": {"source": "CL", "term": "keratinocyte"},
        "organ_term": {"source": None, "term": None},
        "ecs": [{
            "biological_process": PROCESS,
            "biological_object": {},
            "biological_action": {"source_id": "1", "term": "increased"},
        }],
        "description": "<p>A description.</p>",
        "measurement_method": "",
    }
    base.update(extra)
    return base


def write_component(directory: Path, cid: int) -> None:
    directory.mkdir(exist_ok=True)
    (directory / f"EC-{cid:04d}.yaml").write_text(yaml.safe_dump({
        "id": f"enviromech:ec-{cid:04d}",
        "event_component": {
            "id": cid,
            "biological_process_id": PROCESS,
            "biological_action_id": {"term": "increased"},
        },
    }))


def test_record_reuses_the_id_of_a_matching_component(tmp_path):
    write_component(tmp_path / "ec", 8)
    lines, missing = kes.record(event(), "2026-10-03", kes.component_ids(tmp_path / "ec"))
    loaded = yaml.safe_load("\n".join(lines))
    assert missing == []
    assert loaded["id"] == "aop.events:9001"
    assert loaded["aop_wiki_snapshot"] == "2026-10-03"
    assert loaded["event"]["event_components"][0]["id"] == 8
    assert loaded["event"]["cell_term_id"] == {"source": "CL", "term": "keratinocyte"}
    assert "organ_term_id" not in loaded["event"]
    assert loaded["event"]["definition"] == "A description."
    assert "measured_or_detected" not in loaded["event"]


def test_record_names_a_component_with_no_record(tmp_path):
    lines, missing = kes.record(event(), "2026-10-03", kes.component_ids(tmp_path))
    assert "id" not in yaml.safe_load("\n".join(lines))["event"]["event_components"][0]
    assert missing == [{
        "biological_process_id": PROCESS,
        "biological_action_id": {"term": "increased"},
    }]


def test_snapshot_date_is_read_from_the_cache_name(tmp_path):
    path = tmp_path / "all_events_10-03-2026.json"
    path.write_text(json.dumps({}))
    assert kes.snapshot_date(path) == "2026-10-03"
