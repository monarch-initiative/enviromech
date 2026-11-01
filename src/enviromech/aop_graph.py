"""The data behind an AOP page's pathway graph: Key Events, dismech nodes, models.

An AOP record names its Key Events (aop.events, each an AOP-Wiki id with its role).
Each Key Event record may aggregate dismech nodes (aggregation.source_nodes), and
each node may list the dismech models linked to it (models). This module joins the
three into one graph for the record browser to draw, so a reader can follow a Key
Event to the dismech nodes it is made of, and on to the methods that measure,
perturb or reproduce them.

Nothing here is curated: every value is read from the records, and a gap in them
shows as a gap in the graph. A Key Event with no record, or with no aggregation,
is still drawn, and a node with no models is marked so.

Key Event Relationships are not drawn yet. The AOP record names them by id only;
their upstream and downstream Key Events are not in any record until EnviroMech has
Key Event Relationship records. The Key Events are laid out in the order the AOP
record lists them.
"""

from __future__ import annotations

ROLE_ORDER = {"MolecularInitiatingEvent": 0, "KeyEvent": 1, "AdverseOutcome": 2}
ROLE_TEXT = {"MolecularInitiatingEvent": "MIE", "KeyEvent": "KE", "AdverseOutcome": "AO"}
SECTION_TEXT = {
    "experimental_models": "experimental",
    "animal_models": "animal",
    "computational_models": "computational",
}


def _text(value) -> str:
    return " ".join(str(value).split()) if value else ""


def aop_graph(aop_record: dict, key_events: dict[int, tuple[str, dict]]) -> dict:
    """The graph for one AOP record.

    ``key_events`` maps an AOP-Wiki Key Event id to (record stem, record data).
    The result is plain data, ready to embed in a page as JSON.
    """
    aop = aop_record.get("aop") or {}
    members = sorted(
        enumerate(aop.get("events") or []),
        key=lambda pair: (ROLE_ORDER.get(pair[1].get("type"), 1), pair[0]),
    )
    graph = {"key_events": [], "nodes": [], "models": [], "ke_node": [], "node_model": []}
    nodes: dict[str, dict] = {}
    models: dict[str, dict] = {}
    for _, member in members:
        event_id = member.get("event_id")
        stem, record = key_events.get(event_id, (None, {}))
        event = record.get("event") or {}
        aggregation = record.get("aggregation") or {}
        level = (event.get("biological_organization_id") or {}).get("term")
        graph["key_events"].append({
            "id": f"ke:{event_id}",
            "number": event_id,
            "label": _text(event.get("title")) or f"KE {event_id}",
            "role": ROLE_TEXT.get(member.get("type"), ""),
            "level": level or "",
            "href": f"{stem}.html" if stem else "",
            "relation": aggregation.get("aggregation_relation") or "",
            "rationale": _text(aggregation.get("rationale")),
            "has_record": stem is not None,
        })
        for source in aggregation.get("source_nodes") or []:
            ref = source.get("source_node_ref") or f"{source.get('source_entry')}#{source.get('node_name')}"
            node_id = f"node:{ref}"
            if node_id not in nodes:
                nodes[node_id] = {
                    "id": node_id,
                    "label": _text(source.get("node_name")),
                    "entry": source.get("source_entry") or "",
                    "level": source.get("source_level") or "",
                    "href": source.get("source_entry_uri") or "",
                    "notes": _text(source.get("notes")),
                    "has_models": bool(source.get("models")),
                }
            graph["ke_node"].append({
                "source": f"ke:{event_id}",
                "target": node_id,
                "relation": aggregation.get("aggregation_relation") or "",
            })
            for model in source.get("models") or []:
                model_id = f"model:{model.get('model_ref')}"
                if model_id not in models:
                    models[model_id] = {
                        "id": model_id,
                        "label": _text(model.get("model_name")),
                        "section": SECTION_TEXT.get(model.get("model_section"))
                        or model.get("model_section") or "",
                        "ref": model.get("model_ref") or "",
                        "href": source.get("source_entry_uri") or "",
                    }
                link = {"source": node_id, "target": model_id,
                        "relationship": model.get("source_relationship") or ""}
                if link not in graph["node_model"]:
                    graph["node_model"].append(link)
    graph["nodes"] = list(nodes.values())
    graph["models"] = list(models.values())
    return graph


def graphs(aop_records: dict[str, dict], key_event_records: dict[str, dict]) -> dict[str, dict]:
    """The graph for every AOP record, keyed by the AOP record's stem."""
    by_event_id = {
        (data.get("event") or {}).get("id"): (stem, data) for stem, data in key_event_records.items()
    }
    return {stem: aop_graph(data, by_event_id) for stem, data in aop_records.items()}
