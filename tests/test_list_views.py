"""A list view per record kind, beside the mixed one over every record (issue #53)."""

import re
from functools import cache

import pytest

from enviromech import render, site
from enviromech.paths import AOPS_DIR, KEY_EVENTS_DIR, PAGES_DIR
from enviromech.validate import iter_records

SETTINGS = site.load()


@cache
def pages():
    """The whole browser, built once and only if a test asks for it."""
    return render.build()
# How many records each kind has, read from the directories themselves.
HELD = {
    "AOP": len(iter_records(AOPS_DIR)),
    "Key Event": len(iter_records(KEY_EVENTS_DIR)),
    "Observation": len(iter_records()),
}


def view_page(slug):
    return pages()[PAGES_DIR / f"{slug}.html"]


def headings(page):
    return re.findall(r'data-col="\d+">(.*?)</button>', page)


def rows(page):
    body = re.search(r"<tbody>(.*?)</tbody>", page, re.S).group(1)
    return [
        [re.sub(r"<[^>]+>", "", cell).strip()
         for cell in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        for row in re.findall(r"<tr>(.*?)</tr>", body, re.S)
    ]


# ---------------------------------------------------------------- the views


def test_every_kind_with_records_gets_a_view_of_its_own():
    assert view_page("index")  # the mixed view stays, as the front page
    for kind in render.KINDS:
        assert view_page(render.kind_slug(kind)), kind


def test_a_view_holds_only_its_own_kind_and_all_of_it():
    for kind, n in HELD.items():
        page = view_page(render.kind_slug(kind))
        assert len(rows(page)) == n, kind
        assert f"{n} {kind}" in page
    assert len(rows(view_page("index"))) == sum(HELD.values())


def test_each_view_has_the_columns_its_kind_needs():
    aops, key_events = view_page("aops"), view_page("key-events")
    assert headings(aops) == [render.column_label(c) for c in SETTINGS["kind_columns"]["AOP"]]
    assert "Key Event Relationships" in headings(aops)
    assert "AOP-Wiki id" in headings(key_events) and "Biological level" in headings(key_events)
    # The kinds' columns differ; the mixed view keeps the generic ones.
    assert headings(aops) != headings(key_events)
    assert headings(view_page("index")) == [render.column_label(c) for c in SETTINGS["index_columns"]]


def test_the_committed_settings_give_every_kind_its_columns():
    assert set(SETTINGS["kind_columns"]) == set(render.KINDS) == set(HELD)


def test_every_page_links_to_every_view_and_marks_the_one_shown():
    slugs = ["index", *(render.kind_slug(k) for k in render.KINDS)]
    for slug in slugs:
        page = view_page(slug)
        for other in slugs:
            assert f'href="{other}.html"' in page
        assert f'href="{slug}.html" aria-current="page"' in page


def test_a_record_page_links_back_to_its_own_kind():
    page = pages()[PAGES_DIR / "records" / "KE-396.html"]
    assert 'href="../key-events.html" aria-current="page"' in page
    assert 'href="../index.html"' in page and 'href="../aops.html"' in page


def test_a_kind_with_no_records_gets_no_view():
    one = [{"stem": "obs-1", "data": {"kind": "Observation", "name": "An observation"}}]
    assert [v["slug"] for v in render.views(one, SETTINGS)] == ["index", "observations"]


def test_kind_columns_naming_no_record_kind_is_refused():
    settings = {**SETTINGS, "kind_columns": {"Assay": ["name"]}}
    with pytest.raises(SystemExit, match="kind_columns names no record kind"):
        render.views([], settings)


# ---------------------------------------------------------------- the cells

RECORDS = [
    {"stem": "AOP-1", "graph": {"nodes": [{"id": "node:x"}], "models": [{"id": "m"}, {"id": "n"}]},
     "data": {"kind": "AOP", "name": "A long pathway title", "aop": {
         "id": 1, "short_name": "Short name",
         "events": [{"event_id": 9, "type": "MolecularInitiatingEvent"},
                    {"event_id": 7, "type": "AdverseOutcome"}],
         "ke_relationships": [{"relationship_id": 2}]}}},
    {"stem": "KE-9", "data": {
        "kind": "Key Event", "name": "A start",
        "event": {"id": 9, "biological_organization_id": {"term": "Molecular"}},
        "level_screening": {"outcome": "LEVEL_FITS"},
        "aggregation": {"source_nodes": [
            {"source_node_ref": "Entry:pathophysiology#A node",
             "models": [{"model_ref": "one"}, {"model_ref": "one"}]}]}}},
    {"stem": "obs-1", "data": {"kind": "Observation", "name": "An observation",
                               "observation": {"events": [9, 7]}}},
]


@pytest.fixture
def derived():
    records = [{**r, "data": dict(r["data"])} for r in RECORDS]
    render.list_cells(records)
    return {r["stem"]: r for r in records}


def test_an_aop_counts_its_key_events_relationships_nodes_and_models(derived):
    cells = derived["AOP-1"]["cells"]
    assert cells["aop_wiki_id"] == "1"
    assert cells["key_events"] == "2" and cells["ke_relationships"] == "1"
    assert cells["dismech_nodes"] == "1" and cells["dismech_models"] == "2"


def test_a_key_event_names_its_level_screening_aops_and_nodes(derived):
    cells = derived["KE-9"]["cells"]
    assert cells["aop_wiki_id"] == "9"
    assert cells["level"] == "molecular" and cells["level_screening"] == "level fits"
    # The AOP's short name, with this Key Event's role in it.
    assert cells["aops"] == "Short name (molecular initiating event)"
    # One node, and its two mentions of one model count once.
    assert cells["dismech_nodes"] == "1" and cells["dismech_models"] == "1"


def test_a_key_event_in_no_aop_has_no_aops_and_no_nodes():
    records = [{"stem": "KE-5", "data": {"kind": "Key Event", "name": "Alone", "event": {"id": 5}}}]
    render.list_cells(records)
    assert records[0]["cells"]["aops"] == ""
    assert records[0]["cells"]["dismech_nodes"] == "0"


def test_an_aop_member_naming_no_key_event_matches_no_record():
    """EMOD leaves event_id optional, so None must match nothing, not a record
    that is itself missing an id."""
    records = [
        {"stem": "KE-unnumbered", "data": {"kind": "Key Event", "name": "No id", "event": {}}},
        {"stem": "AOP-1", "data": {"kind": "AOP", "name": "A pathway", "aop": {
            "events": [{"type": "KeyEvent"}]}}},  # a member with no event_id
    ]
    render.list_cells(records)
    assert records[0]["cells"]["aops"] == ""


def test_a_model_with_no_reference_does_not_count_as_a_model():
    records = [{"stem": "KE-9", "data": {
        "kind": "Key Event", "name": "A start", "event": {"id": 9},
        "aggregation": {"source_nodes": [
            {"source_node_ref": "Entry:pathophysiology#A node",
             "models": [{"model_ref": "one"}, {"model_section": "animal_models"}]}]}}}]
    render.list_cells(records)
    assert records[0]["cells"]["dismech_models"] == "1"


def test_an_observation_counts_the_key_events_it_bears_on(derived):
    assert derived["obs-1"]["cells"]["key_events"] == "2"


def test_a_column_reaches_into_a_nested_field_with_dots(derived):
    record = derived["AOP-1"]
    assert render.column_value(record, "name") == "A long pathway title"
    assert render.column_value(record, "aop.short_name") == "Short name"
    assert render.column_value(record, "aop.events.0") == ""  # a list is not walked into
    assert render.column_value(record, "nothing.here") == ""


def test_a_derived_value_wins_over_a_field_of_the_same_name(derived):
    """`key_events` is a count, although `event.assays`-style fields are read as they are."""
    record = derived["obs-1"]
    assert record["data"]["observation"]["events"] == [9, 7]
    assert render.column_value(record, "key_events") == "2"


def test_a_column_heading_names_the_last_step_of_a_dotted_path():
    assert render.column_label("aop.short_name") == "Short name"
    assert render.column_label("aop_wiki_id") == "AOP-Wiki id"
    assert render.column_label("ke_relationships") == "Key Event Relationships"
