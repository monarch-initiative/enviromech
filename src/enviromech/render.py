"""Render the static record browser into pages/.

    python -m <slug>.render           # write pages/, to look at locally

pages/ is not committed. `just docs-build` renders the same pages into the
site under /records/, so the published browser always matches the records.
Edit the templates in src/<slug>/templates/ or the layout rules below, never
the files in pages/. Colors, title, columns and hidden sections come from
conf/site.yaml.

The browser has a list view per record kind; the first, the AOPs, is the landing
page at index.html, and records of different kinds are never listed together. A
kind's view has its own columns, because an AOP, a
Key Event and an Observation are not described by the same ones: see
`views` and `list_cells` below, and `kind_columns` in conf/site.yaml.

A record page is laid out from the shape of the data, with names and help
text from the schema:

  - simple values (text, numbers, dates, links) go in an overview table;
  - a list of small, uniform objects is a table, one row per item, with
    its quotes folded into the last column;
  - any other object is a card, titled by its preferred term or name, with
    its quotes in view; so is every curated mention (a preferred_term);
  - evidence is a quote card: source, title, support, snippet; the
    description's own evidence folds under the description;
  - discussions are cards with their kind and status;
  - curation history is a table, folded away.

A field's label is its schema `title` if it has one, else its name with
underscores as spaces. Its schema description is shown as help. URLs and
CURIEs are links.
"""

from __future__ import annotations

import argparse
import re
import sys
from functools import cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

from . import site
from .aop_graph import graphs
from .paths import (
    AOPS_DIR,
    ASSAYS_DIR,
    EVIDENCE_DIR,
    KERS_DIR,
    KEY_EVENTS_DIR,
    MECH_NAME,
    PACKAGE_DIR,
    PAGES_DIR,
    RECORD_NOUN,
    REPO_ROOT,
    REPO_URL,
    SCHEMA_PATH,
    TEST_GUIDELINES_DIR,
)
from .validate import iter_records, load

CURIE_BASES = {
    "PMID": "https://pubmed.ncbi.nlm.nih.gov/",
    "DOI": "https://doi.org/",
    "PMC": "https://www.ncbi.nlm.nih.gov/pmc/articles/",
    "WIKIPEDIA": "https://en.wikipedia.org/wiki/",
}
CURIE = re.compile(r"^[A-Za-z][A-Za-z0-9_.]*:[^\s]+$")
URL = re.compile(r"^https?://\S+$")
# Keys whose CURIE values are identifiers to link, not text.
ID_KEYS = {"id", "reference", "accession", "infores", "category", "predicates", "mapping_reference"}
# Keys that name an object, in the order tried for a card's title.
TITLE_KEYS = ("preferred_term", "name", "title", "label", "category", "infores", "relation", "id")
# Most columns a list of objects may have and still show as a table.
MAX_TABLE_COLUMNS = 6
# Longest text a table cell may hold before the list shows as cards.
MAX_CELL_TEXT = 90
# The record kinds the browser shows, in the order their list views are
# offered: an AOP is the top of a pathway, the Key Events sit under it, and the
# Observations are the kind the rest of the tooling is built around. Assays,
# test guidelines and event components have no pages of their own, so they have
# no view either; a Key Event's page names its assays, and an event component is
# reached from the Key Event that uses it.
KINDS = ("AOP", "Key Event", "KER", "Evidence", "Method", "Observation")


def curie_url(curie: str) -> str:
    prefix, _, local = str(curie).partition(":")
    if prefix == "url":
        return local
    if prefix in CURIE_BASES:
        return CURIE_BASES[prefix] + local
    return f"https://bioregistry.io/{curie}"


@cache
def schema_info() -> tuple[dict[str, tuple[str | None, str | None]], dict[str, str]]:
    """({slot: (title, description)}, {enum value: its description, or itself}) from the schema."""
    try:
        from linkml_runtime.utils.schemaview import SchemaView

        sv = SchemaView(str(SCHEMA_PATH))
    except Exception:  # a schema that does not load still gets a browser, with plain labels
        return {}, {}
    slots = {name: (s.title, s.description) for name, s in sv.all_slots().items()}
    values: dict[str, str] = {}
    for enum in sv.all_enums().values():
        for value, pv in (enum.permissible_values or {}).items():
            values.setdefault(value, pv.description or value)
    return slots, values


# Sections and list-view columns a page derives from other records or by
# counting, which the schema does not name.
DERIVED_LABELS = {
    "aops": "AOPs",
    "aop_wiki_id": "AOP-Wiki id",
    "key_events": "Key Events",
    "ke_relationships": "Key Event Relationships",
    "level": "Biological level",
    "dismech_nodes": "dismech nodes",
    "dismech_models": "dismech models",
}


def label(key: str) -> str:
    title = schema_info()[0].get(key, (None, None))[0]
    if title:
        return title
    if key in DERIVED_LABELS:
        return DERIVED_LABELS[key]
    text = str(key).replace("_", " ")
    return text[:1].upper() + text[1:]


def help_text(key: str) -> str | None:
    return schema_info()[0].get(key, (None, None))[1]


# ---------------------------------------------------------------- values


def is_evidence(v) -> bool:
    return isinstance(v, dict) and "reference" in v and "supports" in v


def is_term(v) -> bool:
    return isinstance(v, dict) and set(v) == {"id", "label"}


def is_scalar(v) -> bool:
    return v is None or isinstance(v, (str, int, float, bool))


def link(href: str, text: str) -> Markup:
    return Markup('<a href="{}">{}</a>').format(href, text)


def ref_text(ref: str, keep: int = 64) -> str:
    """A reference as link text: a url: reference without its scheme, shortened in the middle."""
    text = re.sub(r"^url:https?://", "", ref)
    if len(text) <= keep:
        return text
    head = keep * 2 // 5
    return text[:head] + "…" + text[-(keep - head - 1):]


def enum_text(value: str) -> str:
    """An enum value as words: UPPER_SNAKE and CamelCase alike (MolecularInitiatingEvent)."""
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", str(value)).replace("_", " ").lower()


def badge(value: str, kind: str = "") -> Markup:
    text = enum_text(value)
    tip = schema_info()[1].get(str(value)) or str(value)
    cls = f"badge {kind} v-{str(value).lower()}".strip()
    return Markup('<span class="{}" title="{}">{}</span>').format(cls, tip, text)


def scalar(v, key: str = "") -> Markup:
    if v is None:
        return Markup("")
    if isinstance(v, Markup):  # already rendered, such as a link between two records
        return v
    if isinstance(v, bool):
        return Markup("yes" if v else "no")
    text = str(v)
    if URL.match(text):
        return link(text, text)
    if key in ID_KEYS and CURIE.match(text):
        return link(curie_url(text), text)
    if text in schema_info()[1]:
        return badge(text)
    return escape(text)


def term(v: dict) -> Markup:
    anchor = link(curie_url(v["id"]), v["label"])
    return Markup('<span class="term">{} <code>{}</code></span>').format(anchor, v["id"])


def value(v, key: str = "") -> Markup:
    """Any value, inline: for table cells and overview rows."""
    if is_term(v):
        return term(v)
    if is_evidence(v):
        return evidence_list([v])
    if isinstance(v, dict):
        return card(v)
    if isinstance(v, list):
        if all(is_scalar(x) for x in v):
            return Markup(" ").join(Markup('<span class="chip">{}</span>').format(scalar(x, key)) for x in v)
        return items(key, v)
    return scalar(v, key)


# ---------------------------------------------------------------- blocks


def evidence_list(items_: list) -> Markup:
    out = []
    for e in items_:
        ref = str(e.get("reference", ""))
        head = [Markup('<a href="{}" title="{}">{}</a>').format(curie_url(ref), ref, ref_text(ref))]
        if e.get("reference_title"):
            head.append(Markup('<span class="src-title">{}</span>').format(e["reference_title"]))
        tags = [badge(e["supports"], "support")]
        if e.get("evidence_source"):
            tags.append(badge(e["evidence_source"], "source"))
        body = []
        if e.get("snippet"):
            body.append(Markup("<blockquote>{}</blockquote>").format(e["snippet"]))
        if e.get("explanation"):
            body.append(Markup('<p class="explanation">{}</p>').format(e["explanation"]))
        out.append(Markup('<div class="quote"><div class="quote-head">{} {}</div>{}</div>').format(
            Markup(" ").join(head), Markup(" ").join(tags), Markup("").join(body)))
    return Markup('<div class="quotes">{}</div>').format(Markup("").join(out))


def card_title(v: dict) -> tuple[str | None, str | None]:
    for k in TITLE_KEYS:
        if is_scalar(v.get(k)) and v.get(k) not in (None, ""):
            return k, str(v[k])
    return None, None


def card(v: dict, skip: tuple = ()) -> Markup:
    # One rendered sentence, such as a Key Event Relationship.
    if set(v) == {"line"} and isinstance(v["line"], Markup):
        return Markup(
            '<div class="card"><table class="kv"><tr><td>{}</td></tr></table></div>').format(v["line"])
    title_key, title = card_title(v)
    parts = []
    if title:
        parts.append(Markup('<h3 class="card-title">{}</h3>').format(scalar(title, title_key)))
    if is_term(v.get("term")):
        parts.append(Markup('<p class="card-term">{}</p>').format(term(v["term"])))
    if v.get("description") and is_scalar(v["description"]):
        parts.append(Markup('<p class="card-desc">{}</p>').format(scalar(v["description"])))
    rows, blocks = [], []
    for k, x in v.items():
        if k in (title_key, "description", "evidence", *skip) or (k == "term" and is_term(x)):
            continue
        if x in (None, "", []):
            continue
        if is_scalar(x) or is_term(x) or (isinstance(x, list) and all(is_scalar(i) for i in x)):
            rows.append(Markup("<tr><th>{}</th><td>{}</td></tr>").format(label(k), value(x, k)))
        else:
            blocks.append(Markup('<div class="sub"><h4>{}</h4>{}</div>').format(label(k), value(x, k)))
    if rows:
        parts.append(Markup('<table class="kv">{}</table>').format(Markup("").join(rows)))
    parts.extend(blocks)
    if v.get("evidence"):
        parts.append(evidence_list(v["evidence"]))
    # A card holding its own sections (files, a license) gets the full row.
    cls = "card wide" if blocks else "card"
    return Markup('<div class="{}">{}</div>').format(cls, Markup("").join(parts))


def tabular(rows: list) -> list[str] | None:
    """The columns, if a list of objects reads best as a table; else None."""
    if not rows or not all(isinstance(r, dict) for r in rows):
        return None
    # Curated mentions read best as cards, with their quotes in view.
    if any("preferred_term" in r for r in rows):
        return None
    cols: list[str] = []
    for r in rows:
        for k, x in r.items():
            if k == "evidence":
                continue
            if not (is_scalar(x) or is_term(x)):
                return None
            if isinstance(x, str) and len(x) > MAX_CELL_TEXT:
                return None
            if k not in cols:
                cols.append(k)
    return cols if 1 < len(cols) <= MAX_TABLE_COLUMNS else None


def table(key: str, rows: list, cols: list[str]) -> Markup:
    has_ev = any(r.get("evidence") for r in rows)
    head = Markup("").join(Markup("<th>{}</th>").format(label(c)) for c in cols)
    if has_ev:
        head += Markup("<th>Evidence</th>")
    body = []
    for r in rows:
        cells = Markup("").join(Markup('<td data-label="{}">{}</td>').format(label(c), value(r.get(c), c))
                                for c in cols)
        if has_ev:
            ev = r.get("evidence") or []
            cells += Markup('<td data-label="Evidence">{}</td>').format(Markup(
                '<details><summary>{} quote{}</summary>{}</details>').format(
                len(ev), "" if len(ev) == 1 else "s", evidence_list(ev)) if ev else "")
        body.append(Markup("<tr>{}</tr>").format(cells))
    return Markup('<div class="table-wrap"><table class="data"><thead><tr>{}</tr></thead>'
                  '<tbody>{}</tbody></table></div>').format(head, Markup("").join(body))


def plain_card(x) -> Markup:
    return card(x) if isinstance(x, dict) else Markup('<div class="card">{}</div>').format(value(x))


def items(key: str, v: list) -> Markup:
    if all(is_evidence(x) for x in v):
        return evidence_list(v)
    if all(is_term(x) for x in v):
        return Markup(" ").join(term(x) for x in v)
    cols = tabular(v)
    if cols:
        return table(key, v, cols)
    return Markup('<div class="cards">{}</div>').format(
        Markup("").join(plain_card(x) for x in v))


def discussions(v: list) -> Markup:
    out = []
    for d in v:
        tags = Markup(" ").join(badge(d[k], k) for k in ("kind", "status") if d.get(k))
        body = [Markup('<p class="prompt">{}</p>').format(d.get("prompt", ""))]
        for k in ("rationale", "resolution_note", "notes"):
            if d.get(k):
                body.append(Markup('<p><strong>{}.</strong> {}</p>').format(label(k), d[k]))
        if d.get("attaches_to"):
            about = ", ".join(map(str, d["attaches_to"]))
            body.append(Markup('<p class="muted">About: {}</p>').format(about))
        if d.get("evidence"):
            body.append(evidence_list(d["evidence"]))
        out.append(Markup('<div class="card discussion"><div class="card-tags">{}</div>{}</div>').format(
            tags, Markup("").join(body)))
    return Markup('<div class="cards">{}</div>').format(Markup("").join(out))


def history(v: list) -> Markup:
    rows = Markup("").join(
        Markup('<tr><td data-label="Date">{}</td><td data-label="Curator">{}</td>'
               '<td data-label="Action">{}</td><td data-label="What changed">{}</td></tr>').format(
            str(e.get("timestamp", ""))[:10], e.get("curator", ""),
            badge(e["action"]) if e.get("action") else "", e.get("description", ""))
        for e in v)
    return Markup('<details class="history"><summary>{} change{}</summary><div class="table-wrap">'
                  '<table class="data"><thead><tr><th>Date</th><th>Curator</th><th>Action</th>'
                  '<th>What changed</th></tr></thead><tbody>{}</tbody></table></div></details>').format(
        len(v), "" if len(v) == 1 else "s", rows)


HEADER_KEYS = ("id", "name", "description", "description_evidence", "status", "record_term", "synonyms")


def record_body(data: dict, hidden: list[str]) -> dict:
    """The parts of a record page: overview rows, then sections."""
    overview, sections = [], []
    for k, v in data.items():
        if k in HEADER_KEYS or k in hidden or v in (None, "", [], {}):
            continue
        if is_scalar(v) or is_term(v):
            overview.append((label(k), help_text(k), value(v, k)))
            continue
        if k == "discussions":
            html = discussions(v)
        elif k == "curation_history":
            html = history(v)
        elif isinstance(v, list):
            html = items(k, v)
        elif isinstance(v, dict):
            html = card(v)
        else:
            html = value(v, k)
        sections.append({"key": k, "label": label(k), "help": help_text(k), "html": html,
                         "count": len(v) if isinstance(v, list) else None})
    ev = data.get("description_evidence") or []
    lead = evidence_list(ev) if ev else None
    return {"overview": overview, "sections": sections,
            "description_evidence": lead, "description_quotes": len(ev)}


def cell(v) -> str:
    """How a record field shows in the front-page table, as plain text."""
    if isinstance(v, dict):
        named = v.get("label") or v.get("preferred_term") or v.get("id")
        if named:
            return str(named)
        # A small statement such as {"purpose": "DAIRY"}: show its first plain value.
        plain = [x for x in v.values() if isinstance(x, (str, int, float))]
        return cell(plain[0]) if plain else ""
    if isinstance(v, list):
        return ", ".join(cell(x) for x in v)
    if isinstance(v, str) and v in schema_info()[1]:
        return enum_text(v)
    return "" if v is None else str(v)


def key_events_by_event_id(records: list[dict]) -> dict:
    """The Key Event records, by AOP-Wiki id.

    A record with no `event.id` is left out. EMOD makes the id an identifier,
    so a Key Event file cannot validate without one, but the browser renders
    the working tree rather than a validated corpus: a half-written record has
    no id yet, and filing it under `None` would make it the match for every
    reference that names no Key Event at all.
    """
    out = {}
    for r in records:
        if r["data"]["kind"] != "Key Event":
            continue
        event_id = (r["data"].get("event") or {}).get("id")
        if event_id is not None:
            out[event_id] = r
    return out


# ---------------------------------------------------------------- list views


def kind_slug(kind: str) -> str:
    """The page name of a kind's list view: "Key Event" -> "key-events"."""
    return kind.lower().replace(" ", "-") + "s"


def plural(noun: str, count: int) -> str:
    return noun if count == 1 else f"{noun}s"


def list_cells(records: list[dict]) -> None:
    """Fill each record's `cells`: the list-view values no field of it holds.

    A list view's columns name fields of the record (conf/site.yaml,
    `kind_columns`), reaching into a nested one with dots. These are the rest:
    how many Key Events, Key Event Relationships, dismech nodes and dismech
    models a record has, the level a Key Event sits at, the outcome of
    screening it, and the AOPs it appears in with its role in each. They are
    plain text, as every list-view cell is.

    Run this before the cross-linking, which replaces AOP-Wiki ids with links.
    """
    stem_by_event_id = {
        event_id: r["stem"] for event_id, r in key_events_by_event_id(records).items()
    }
    in_aops: dict[str, list[str]] = {}
    for r in records:
        if r["data"]["kind"] != "AOP":
            continue
        aop = r["data"].get("aop") or {}
        # An AOP's title runs to a line of prose; its short name is what fits
        # in a cell beside every other Key Event's AOPs.
        name = str(aop.get("short_name") or r["data"].get("name") or r["stem"])
        for member in aop.get("events") or []:
            # EMOD leaves event_id optional, so a member may name no Key Event
            # at all; that must match no record rather than the first one
            # missing an id of its own.
            event_id = member.get("event_id")
            stem = stem_by_event_id.get(event_id) if event_id is not None else None
            if stem is None:  # a Key Event the AOP names but no record holds
                continue
            role = enum_text(member.get("type") or "")
            in_aops.setdefault(stem, []).append(f"{name} ({role})" if role else name)
    ker_in_aops: dict[int, list[str]] = {}
    for r in records:
        if r["data"]["kind"] == "AOP":
            aop = r["data"].get("aop") or {}
            name = str(aop.get("short_name") or r["data"].get("name") or r["stem"])
            for rel in aop.get("ke_relationships") or []:
                ker_in_aops.setdefault(rel.get("relationship_id"), []).append(name)
    for r in records:
        data = r["data"]
        cells: dict[str, str] = {}
        if data["kind"] == "KER":
            cells["relationship_id"] = str(r["ker"]["id"])
            cells["aops"] = ", ".join(ker_in_aops.get(r["ker"]["id"], []))
            cells["provenance"] = str(data.get("provenance") or "")
            cells["quantitative"] = "yes" if data.get("response_relationship") else ""
        elif data["kind"] == "Method":
            assay = data.get("assay") or {}
            cells["test_guidelines"] = ", ".join(data.get("guideline_names") or [])
            cells["key_events"] = ", ".join(f"KE {e}" for e in assay.get("events") or [])
        elif data["kind"] == "AOP":
            aop = data.get("aop") or {}
            graph = r.get("graph") or {}
            cells["aop_wiki_id"] = str(aop.get("id", ""))
            cells["provenance"] = str(data.get("provenance") or "")
            cells["key_events"] = str(len(aop.get("events") or []))
            cells["ke_relationships"] = str(len(aop.get("ke_relationships") or []))
            # The graph counts the nodes and models the AOP's Key Events
            # aggregate, each once however many Key Events reach it.
            cells["dismech_nodes"] = str(len(graph.get("nodes") or []))
            cells["dismech_models"] = str(len(graph.get("models") or []))
        elif data["kind"] == "Key Event":
            event = data.get("event") or {}
            sources = (data.get("aggregation") or {}).get("source_nodes") or []
            cells["aop_wiki_id"] = str(event.get("id", ""))
            cells["provenance"] = str(data.get("provenance") or "")
            cells["level"] = cell((event.get("biological_organization_id") or {}).get("term"))
            cells["aops"] = ", ".join(in_aops.get(r["stem"], []))
            cells["level_screening"] = cell((data.get("level_screening") or {}).get("outcome"))
            cells["dismech_nodes"] = str(len(sources))
            cells["dismech_models"] = str(len({
                model["model_ref"] for source in sources
                for model in source.get("models") or []
                if model.get("model_ref")  # an unnamed model is not another model
            }))
        elif data["kind"] == "Evidence":
            up = str(data.get("upstream_observation") or "")
            down = str(data.get("downstream_observation") or "")
            cells["observations"] = (f"{up} \u2192 {down}" if up and down else up or down)
        elif data["kind"] == "Observation":
            cells["key_events"] = str(len((data.get("observation") or {}).get("events") or []))
        r["cells"] = cells


def column_value(record: dict, column: str) -> str:
    """A record's value for one list-view column, as plain text.

    Its `cells` first, so a derived value wins over a field of the same name;
    then the record's own fields, reaching into a nested one with dots
    (`event.short_name`). A column the record has nothing for is empty.
    """
    if column in record.get("cells", {}):
        return record["cells"][column]
    value = record["data"]
    for part in column.split("."):
        if not isinstance(value, dict):
            return ""
        value = value.get(part)
    return cell(value)


def column_label(column: str) -> str:
    """The heading of a list-view column: a dotted path is named by its last step."""
    return label(column.rsplit(".", 1)[-1])


def views(records: list[dict], settings: dict) -> list[dict]:
    """The browser's list views, one per record kind that has records.

    The first is the landing page, index.html. Each has its own columns from
    `kind_columns`, falling back to `index_columns`.
    """
    unknown = sorted(set(settings["kind_columns"]) - set(KINDS))
    if unknown:
        raise SystemExit(
            f"conf/site.yaml: kind_columns names no record kind {unknown}; "
            f"the kinds are {list(KINDS)}"
        )
    out = []
    for kind in KINDS:
        held = [r for r in records if r["data"]["kind"] == kind]
        if not held:  # no records of this kind: no view, and no dead link to one
            continue
        # The first view is the landing page. Records of different kinds are never
        # listed together: their columns differ, and the mix is confusing.
        out.append({"slug": "index" if not out else kind_slug(kind), "kind": kind, "heading": f"{kind}s",
                    "columns": settings["kind_columns"].get(kind) or settings["index_columns"],
                    "records": held})
    for view in out:
        held = view["records"]
        view["count"] = len(held)
        view["noun"] = plural(view["kind"], view["count"])
        statuses: dict[str, int] = {}
        for r in held:
            if r["data"].get("status"):
                statuses[str(r["data"]["status"])] = statuses.get(str(r["data"]["status"]), 0) + 1
        view["kinds"] = []
        view["statuses"] = sorted(statuses.items())
    return out


def cross_link(records: list[dict]) -> None:
    """Link each Observation to the Key Events it bears on, and back.

    An Observation names its Key Events by AOP-Wiki id, in observation.events.
    Where a Key Event record has that id, the number becomes a link to its
    page. Each Key Event's page gains the list of Observations that name it;
    that list is not in the Key Event's file, it is derived here.
    """
    by_event_id = key_events_by_event_id(records)
    bearing: dict[str, list[Markup]] = {}
    for r in records:
        observation = r["data"].get("observation")
        if r["data"]["kind"] != "Observation" or not isinstance(observation, dict):
            continue
        linked = []
        for event_id in observation.get("events") or []:
            # An id of None names no Key Event, so it must match no record.
            target = by_event_id.get(event_id) if event_id is not None else None
            if target is None:
                linked.append(event_id)
                continue
            linked.append(link(f"{target['stem']}.html", f"KE {event_id}: {target['data']['name']}"))
            bearing.setdefault(target["stem"], []).append(
                link(f"{r['stem']}.html", str(r["data"].get("name", r["stem"])))
            )
        if linked:
            r["data"] = {**r["data"], "observation": {**observation, "events": linked}}
    for r in records:
        if r["stem"] in bearing:
            r["data"] = {**r["data"], "observations": bearing[r["stem"]]}


def cross_link_aops(records: list[dict]) -> None:
    """Link each AOP to its Key Events, and each Key Event to the AOPs it is in.

    An AOP names its Key Events in EMOD's aop.events, each by its AOP-Wiki id
    (event_id) with its role (type). Where a Key Event record has that id, the
    number becomes a link to its page. Each Key Event's page gains the list of
    AOPs that name it, with its role in each; that list is not in the Key
    Event's file, it is derived here.
    """
    by_event_id = key_events_by_event_id(records)
    kers = {r["ker"]["id"]: r for r in records if r["data"]["kind"] == "KER"}
    member_of: dict[str, list[Markup]] = {}
    for r in records:
        aop = r["data"].get("aop")
        if r["data"]["kind"] != "AOP" or not isinstance(aop, dict):
            continue
        linked = []
        for member in aop.get("events") or []:
            # EMOD leaves event_id optional, so a member may name no Key Event
            # at all; that must match no record.
            event_id = member.get("event_id")
            target = by_event_id.get(event_id) if event_id is not None else None
            if target is None:
                linked.append(member)
                continue
            text = f"KE {member['event_id']}: {target['data']['name']}"
            linked.append({**member, "event_id": link(f"{target['stem']}.html", text)})
            role = enum_text(member.get("type") or "")
            name = str(r["data"]["name"])
            back = link(f"{r['stem']}.html", f"{name} ({role})" if role else name)
            member_of.setdefault(target["stem"], []).append(back)
        relationships = []
        for rel in aop.get("ke_relationships") or []:
            relationships.append(ker_line(rel, kers, by_event_id))
            if rel.get("relationship_id") in kers:
                directness = (rel.get("directness_id") or {}).get("term")
                name = str(r["data"]["name"])
                back = link(f"{r['stem']}.html", f"{name} ({directness})" if directness else name)
                member_of.setdefault(kers[rel["relationship_id"]]["stem"], []).append(back)
        # One card each, below the events, as the events are.
        relationships = [{"line": x} if isinstance(x, Markup) else x for x in relationships]
        r["data"] = {**r["data"], "aop": {**aop, "events": linked, "ke_relationships": relationships}}
    for r in records:
        if r["stem"] in member_of:
            r["data"] = {**r["data"], "aops": member_of[r["stem"]]}


def ker_line(rel: dict, kers: dict, by_event_id: dict) -> Markup | dict:
    """One AOP-Wiki KER as a line: "3637: Upstream leads to Downstream (adjacent)".

    The endpoints come from the Key Event Relationship record, whose page the
    number links to; the directness is the AOP's own. With no record for the
    id, the entry is left as it is.
    """
    ker = kers.get(rel.get("relationship_id"))
    if ker is None:
        return rel
    directness = (rel.get("directness_id") or {}).get("term")
    tail = Markup(" ({})").format(directness) if directness else Markup("")
    return Markup("{}: {} leads to {}{}").format(
        link(f"{ker['stem']}.html", rel["relationship_id"]),
        event_link(ker["ker"]["upstream"], by_event_id),
        event_link(ker["ker"]["downstream"], by_event_id), tail)


def event_link(event_id, by_event_id: dict) -> Markup:
    """A Key Event by its title, linked to its page when it has one."""
    target = by_event_id.get(event_id)
    if target is None:
        return Markup("KE {}").format(event_id)
    return link(f"{target['stem']}.html", target["data"]["name"])


def cross_link_evidence(records: list[dict]) -> None:
    """Link each Evidence record to its two observations and its KER, and back.

    An Evidence record names an upstream observation, a downstream observation
    and the Key Event Relationship they support, each by record id. Those become
    links; the KER's page gains the Evidence supporting it, and each
    observation's page the Evidence that pairs it. None of those back-links is
    in a file; they are derived here. Each Evidence record also gets the small
    paired-observation graph its page draws.
    """
    obs_by_id = {r["data"].get("id"): r for r in records
                 if r["data"]["kind"] == "Observation" and r["data"].get("id")}
    ker_by_id = {r["data"].get("id"): r for r in records
                 if r["data"]["kind"] == "KER" and r["data"].get("id")}
    supporting: dict[str, list[Markup]] = {}
    pairing: dict[str, list[Markup]] = {}
    for r in records:
        data = r["data"]
        if data["kind"] != "Evidence":
            continue
        up = obs_by_id.get(data.get("upstream_observation"))
        down = obs_by_id.get(data.get("downstream_observation"))
        ker = ker_by_id.get(data.get("relationship"))

        def side(obs, fallback):
            if obs is None:
                return {"label": str(fallback or ""), "href": None}
            return {"label": str(obs["data"]["name"]), "href": f"{obs['stem']}.html"}

        r["evidence_graph"] = {
            "upstream": side(up, data.get("upstream_observation")),
            "downstream": side(down, data.get("downstream_observation")),
            "ker": ({"label": str(ker["data"]["name"]), "href": f"{ker['stem']}.html"}
                    if ker else {"label": str(data.get("relationship") or ""), "href": None}),
        }
        shown = dict(data)
        if up:
            shown["upstream_observation"] = link(f"{up['stem']}.html", str(up["data"]["name"]))
        if down:
            shown["downstream_observation"] = link(f"{down['stem']}.html", str(down["data"]["name"]))
        if ker:
            shown["relationship"] = link(f"{ker['stem']}.html", str(ker["data"]["name"]))
        r["data"] = shown
        back = link(f"{r['stem']}.html", str(data["name"]))
        if ker:
            supporting.setdefault(ker["stem"], []).append(back)
        for obs in (up, down):
            if obs is not None:
                pairing.setdefault(obs["stem"], []).append(back)
    for r in records:
        if r["stem"] in supporting:
            r["data"] = {**r["data"], "evidence": supporting[r["stem"]]}
        if r["stem"] in pairing:
            r["data"] = {**r["data"], "evidence_pairings": pairing[r["stem"]]}


def name_assays(records: list[dict]) -> None:
    """Show each Key Event's assays and test guidelines by name, not by id.

    A Key Event names its assays in event.assays and its guidelines in
    event.test_guidelines, EMOD's own slots, by id; the assays and guidelines are
    records under data/assays/ and data/test_guidelines/, with no pages of their
    own. Each id is replaced by the assay's title and its guidelines, or by the
    guideline's short title.
    """
    guidelines = {}
    for path in iter_records(TEST_GUIDELINES_DIR):
        guideline = (load(path) or {}).get("test_guideline") or {}
        guidelines[guideline.get("id")] = guideline.get("short_title") or str(guideline.get("id"))
    assays = {}
    for path in iter_records(ASSAYS_DIR):
        assay = (load(path) or {}).get("assay") or {}
        named = [guidelines.get(g, str(g)) for g in assay.get("test_guidelines") or []]
        title = assay.get("title") or str(assay.get("id"))
        text = f"{title} ({', '.join(named)})" if named else title
        assays[assay.get("id")] = link(f"{path.stem}.html", text)
    for r in records:
        event = r["data"].get("event")
        if r["data"]["kind"] != "Key Event" or not isinstance(event, dict):
            continue
        if not (event.get("assays") or event.get("test_guidelines")):
            continue
        named_event = dict(event)
        if event.get("assays"):
            named_event["assays"] = [assays.get(a, str(a)) for a in event["assays"]]
        if event.get("test_guidelines"):
            named_event["test_guidelines"] = [guidelines.get(g, str(g)) for g in event["test_guidelines"]]
        r["data"] = {**r["data"], "event": named_event}


def ker_and_method_records(records: list[dict]) -> list[dict]:
    """The KER and Method (assay) records, as records of their own kinds.

    A KER is titled by its two Key Events, "Upstream leads to Downstream". A
    Method is an assay record: its page reads the description, then a card of
    its Key Events and test guidelines, then the mapping reference and the
    curator's notes (`body` below replaces the generic layout). Neither shows
    its id: an enviromech: CURIE resolves nowhere, and a KER's is in its title.
    """
    guidelines = {}
    for path in iter_records(TEST_GUIDELINES_DIR):
        guideline = (load(path) or {}).get("test_guideline") or {}
        guidelines[guideline.get("id")] = guideline.get("short_title") or str(guideline.get("id"))
    by_event_id = key_events_by_event_id(records)
    out = []
    for path in iter_records(KERS_DIR):
        data = load(path) or {}
        if not isinstance(data, dict):
            continue
        relationship = data.get("ke_relationship") or {}
        up, down = relationship.get("upstream_event_id"), relationship.get("downstream_event_id")

        def title(event_id):
            target = by_event_id.get(event_id)
            return target["data"]["name"] if target else f"KE {event_id}"

        shown = dict(data)
        shown["ke_relationship"] = {
            "upstream_event_id": event_link(up, by_event_id),
            "downstream_event_id": event_link(down, by_event_id)}
        ker = {"id": relationship.get("id"), "upstream": up, "downstream": down}
        out.append({"stem": path.stem, "ker": ker, "data": {
            "kind": "KER", "name": f"{title(up)} leads to {title(down)}", **shown}})
    for path in iter_records(ASSAYS_DIR):
        data = load(path) or {}
        if not isinstance(data, dict):
            continue
        raw = data.get("assay") or {}
        assay = dict(raw)
        if assay.get("events"):
            assay["events"] = [
                link(f"{by_event_id[e]['stem']}.html", f"KE {e}: {by_event_id[e]['data']['name']}")
                if e in by_event_id else e for e in assay["events"]]
        names = [guidelines.get(g, str(g)) for g in raw.get("test_guidelines") or []]
        if names:
            assay["test_guidelines"] = names
        facts = {k: assay[k] for k in ("events", "test_guidelines") if assay.get(k)}
        closing = record_body({k: data[k] for k in ("mapping_reference", "notes") if data.get(k)}, [])
        body = {"overview": [], "sections": [], "description_evidence": None, "description_quotes": 0,
                "detail": card(facts) if facts else None, "footer": closing["overview"]}
        out.append({"stem": path.stem, "body": body, "data": {
            "kind": "Method", "name": raw.get("title") or path.stem, "description": raw.get("description"),
            "assay": raw, "guideline_names": names,
            **{k: v for k, v in data.items() if k not in ("id", "assay")}}})
    return out


def build() -> dict[Path, str]:
    settings = site.load()
    errors = site.problems(settings)
    if errors:
        raise SystemExit("conf/site.yaml: " + "; ".join(errors))
    env = Environment(
        loader=FileSystemLoader(PACKAGE_DIR / "templates"),
        autoescape=select_autoescape(["html"]),
        keep_trailing_newline=True,
    )
    env.filters.update(curie_url=curie_url, cell=cell, label=label, scalar=scalar, badge=badge, term=term,
                       column_label=column_label)
    env.globals.update(column_value=column_value)
    records = []
    for path in iter_records():
        data = load(path) or {}
        if not isinstance(data, dict):  # not a record; just validate reports it
            continue
        records.append({"stem": path.stem, "data": {"kind": "Observation", **data}})
    # Key Events are a second record kind (issue #4). A Key Event has no name
    # of its own: its page and its row are titled by the Event's title.
    for path in iter_records(KEY_EVENTS_DIR):
        data = load(path) or {}
        if not isinstance(data, dict):
            continue
        title = (data.get("event") or {}).get("title") or path.stem
        records.append({"stem": path.stem, "data": {"kind": "Key Event", "name": title, **data}})
    # AOPs are a third record kind, titled by the AOP's title.
    for path in iter_records(AOPS_DIR):
        data = load(path) or {}
        if not isinstance(data, dict):
            continue
        title = (data.get("aop") or {}).get("title") or path.stem
        records.append({"stem": path.stem, "data": {"kind": "AOP", "name": title, **data}})
    # KERs and Methods (assays) are records of their own kinds, with their own views.
    records.extend(ker_and_method_records(records))
    # Evidence records pair an upstream and a downstream observation onto a KER,
    # titled by the KER they support so the row reads as evidence for a chain.
    ker_name = {r["data"].get("id"): r["data"]["name"]
                for r in records if r["data"]["kind"] == "KER" and r["data"].get("id")}
    for path in iter_records(EVIDENCE_DIR):
        data = load(path) or {}
        if not isinstance(data, dict):
            continue
        rel = data.get("relationship")
        chain = ker_name.get(rel)
        name = f"Evidence for {chain}" if chain else (f"Evidence ({rel})" if rel else path.stem)
        records.append({"stem": path.stem, "data": {"kind": "Evidence", "name": name, **data}})
    # The pathway graph is built from the records as loaded, before cross-linking
    # turns AOP-Wiki ids into links.
    aop_graphs = graphs(
        {r["stem"]: r["data"] for r in records if r["data"]["kind"] == "AOP"},
        {r["stem"]: r["data"] for r in records if r["data"]["kind"] == "Key Event"},
        {path.stem: load(path) or {} for path in iter_records(ASSAYS_DIR)},
        {path.stem: load(path) or {} for path in iter_records(TEST_GUIDELINES_DIR)},
    )
    for r in records:
        if r["stem"] in aop_graphs and r["data"]["kind"] == "AOP":
            r["graph"] = aop_graphs[r["stem"]]
    # The list-view cells are read from the records as loaded, before
    # cross-linking turns AOP-Wiki ids into links.
    list_cells(records)
    cross_link(records)
    cross_link_aops(records)
    cross_link_evidence(records)
    name_assays(records)
    records.sort(key=lambda r: str(r["data"].get("name", r["stem"])).lower())
    all_views = views(records, settings)
    ctx = {"mech_name": MECH_NAME, "record_noun": RECORD_NOUN, "repo_url": REPO_URL,
           "site": settings, "views": all_views}
    out = {}
    listing = env.get_template("list.html")
    for view in all_views:
        out[PAGES_DIR / f"{view['slug']}.html"] = listing.render(view=view, **ctx)
    tmpl = env.get_template("record.html")
    for r in records:
        body = r.get("body") or record_body(r["data"], settings["hidden_sections"])
        out[PAGES_DIR / "records" / f"{r['stem']}.html"] = tmpl.render(record=r, body=body, **ctx)
    css = env.get_template("style.css").render(theme=settings["theme"], **site.colors(settings))
    out[PAGES_DIR / "style.css"] = css
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.parse_args(argv)
    wanted = build()
    existing = set(PAGES_DIR.rglob("*.html")) | set(PAGES_DIR.rglob("*.css")) if PAGES_DIR.exists() else set()
    for p in existing - set(wanted):
        p.unlink()
    for p, text in wanted.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    print(f"Wrote {len(wanted)} files to {PAGES_DIR.relative_to(REPO_ROOT)}/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
