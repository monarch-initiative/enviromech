"""AOPs, the third record kind: counted by the report and shown in the browser."""

import json
import re

from enviromech import render, report
from enviromech.aop_graph import aop_graph, graphs
from enviromech.paths import AOPS_DIR, KEY_EVENTS_DIR, PAGES_DIR
from enviromech.validate import iter_records, load

AOPS = iter_records(AOPS_DIR)


def test_report_counts_aops():
    stats = report.compute()
    assert stats["aops"] == len(AOPS)
    assert sum(stats["aops_by_status"].values()) == len(AOPS)


def test_browser_has_a_page_for_every_aop():
    pages = render.build()
    index = pages[PAGES_DIR / "index.html"]
    assert f"{len(AOPS)} AOP" in index
    for path in AOPS:
        title = load(path)["aop"]["title"].strip()
        page = pages[PAGES_DIR / "records" / f"{path.stem}.html"]
        assert f"<h1>{title}" in page.replace("&#39;", "'")
        assert f'href="records/{path.stem}.html"' in index


def test_aops_and_key_events_link_to_each_other():
    """An AOP's page links to each Key Event it names, and that Key Event's
    page links back with its role, although only the AOP's file records it."""
    pages = render.build()
    by_event_id = {load(p)["event"]["id"]: p.stem for p in iter_records(KEY_EVENTS_DIR)}
    linked = 0
    for path in AOPS:
        for member in load(path)["aop"]["events"]:
            stem = by_event_id.get(member["event_id"])
            if stem is None:
                continue
            assert f'href="{stem}.html"' in pages[PAGES_DIR / "records" / f"{path.stem}.html"]
            back = pages[PAGES_DIR / "records" / f"{stem}.html"]
            assert f'href="{path.stem}.html"' in back
            assert f"({render.enum_text(member['type'])})" in back
            linked += 1
    assert linked, "no AOP names a Key Event that has a record"


def test_enum_values_read_as_words():
    assert render.enum_text("MolecularInitiatingEvent") == "molecular initiating event"
    assert render.enum_text("NOT_SCREENED") == "not screened"


# The pathway graph on an AOP's page: Key Events, dismech nodes, models (issue #42).

KEY_EVENTS = {p.stem: load(p) for p in iter_records(KEY_EVENTS_DIR)}
GRAPHS = graphs({p.stem: load(p) for p in AOPS}, KEY_EVENTS)
BY_EVENT_ID = {data["event"]["id"]: data for data in KEY_EVENTS.values()}


def _expected(aop_path):
    """Nodes and models the AOP's Key Event records hold, and their links."""
    nodes, models, ke_node, node_model = set(), set(), [], set()
    for member in load(aop_path)["aop"]["events"]:
        record = BY_EVENT_ID.get(member["event_id"]) or {}
        for source in (record.get("aggregation") or {}).get("source_nodes") or []:
            nodes.add(source["source_node_ref"])
            ke_node.append((member["event_id"], source["source_node_ref"]))
            for model in source.get("models") or []:
                models.add(model["model_ref"])
                node_model.add((source["source_node_ref"], model["model_ref"]))
    return nodes, models, ke_node, node_model


def test_every_key_event_is_drawn_from_mie_to_ao():
    for path in AOPS:
        graph = GRAPHS[path.stem]
        events = load(path)["aop"]["events"]
        assert sorted(k["number"] for k in graph["key_events"]) == sorted(e["event_id"] for e in events)
        roles = [k["role"] for k in graph["key_events"]]
        assert roles[0] == "MIE" and roles[-1] == "AO"


def test_nodes_and_models_appear_once_with_every_link():
    for path in AOPS:
        graph = GRAPHS[path.stem]
        nodes, models, ke_node, node_model = _expected(path)
        node_ids = [n["id"] for n in graph["nodes"]]
        model_ids = [m["id"] for m in graph["models"]]
        assert len(node_ids) == len(set(node_ids)) and len(model_ids) == len(set(model_ids))
        assert {i.removeprefix("node:") for i in node_ids} == nodes
        assert {i.removeprefix("model:") for i in model_ids} == models
        assert sorted((int(link["source"].removeprefix("ke:")), link["target"].removeprefix("node:"))
                      for link in graph["ke_node"]) == sorted(ke_node)
        assert {(link["source"].removeprefix("node:"), link["target"].removeprefix("model:"))
                for link in graph["node_model"]} == node_model


def test_aop40_shares_a_node_between_two_key_events_and_shows_its_gaps():
    graph = GRAPHS["AOP-40"]
    targets = [link["target"] for link in graph["ke_node"]]
    assert any(targets.count(t) > 1 for t in targets), "no node is drawn for two Key Events"
    gaps = [k["number"] for k in graph["key_events"] if not k["relation"]]
    assert 827 in gaps
    assert all(n["has_models"] == any(link["source"] == n["id"] for link in graph["node_model"])
               for n in graph["nodes"])


def test_an_aop_with_no_aggregations_draws_its_key_events_alone():
    record = {"aop": {"events": [{"event_id": 1, "type": "AdverseOutcome"},
                                 {"event_id": 2, "type": "MolecularInitiatingEvent"}]}}
    graph = aop_graph(record, {2: ("KE-2", {"event": {"id": 2, "title": "A start"}})})
    assert [k["number"] for k in graph["key_events"]] == [2, 1]
    assert graph["key_events"][1]["has_record"] is False
    assert graph["nodes"] == graph["models"] == graph["ke_node"] == graph["node_model"] == []


def test_aop_pages_embed_the_graph_and_its_script():
    pages = render.build()
    for path in AOPS:
        page = pages[PAGES_DIR / "records" / f"{path.stem}.html"]
        found = re.search(r'<script type="application/json" id="pathway-data">(.*?)</script>', page, re.S)
        assert found, f"{path.stem} has no pathway data"
        assert json.loads(found.group(1)) == GRAPHS[path.stem]
        assert 'id="pathway-figure"' in page and "createElementNS" in page
    for stem in KEY_EVENTS:
        assert 'id="pathway-data"' not in pages[PAGES_DIR / "records" / f"{stem}.html"]
