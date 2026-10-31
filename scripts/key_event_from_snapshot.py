"""Write the start of a Key Event record from an aop_wiki_cli snapshot cache.

    python scripts/key_event_from_snapshot.py EVENTS_JSON KE_ID [EVENT_COMPONENT_DIRECTORY]

EVENTS_JSON is the events cache aop_wiki_cli writes for one AOP-Wiki XML export,
outputs/cache/<MM-DD-YYYY>/all_events_<MM-DD-YYYY>.json, and the snapshot date is
read from its name. The record is printed, through the Event block, to standard
output; redirect it to data/key_events/KE-<id>.yaml:

- id, status DRAFT, the snapshot date and the Event's AOP-Wiki page;
- the Event's title, short name, level of biological organization, cell and
  organ terms, and event components, as AOP-Wiki records them;
- its description as definition, and how it is measured as
  measured_or_detected, with the HTML removed. Each block element becomes a
  paragraph and each table row a paragraph of its cells joined by "; ".
  Citation markers such as [1] are kept as text; HTML comments are dropped.
  Every word of the field's text is kept, and none is read twice.

An event component takes the id of the record under EVENT_COMPONENT_DIRECTORY
(default data/event_components) with the same action, object and process. A
component with no such record is printed without an id, and named on stderr,
so the record fails validation until one is added.

What a curator adds is not printed: the header comment, level_screening,
term_findings, aggregation and notes.
"""

import json
import re
import sys
import textwrap
from pathlib import Path

import yaml
from bs4 import BeautifulSoup
from bs4.element import PreformattedString

BLOCKS = ["p", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "div", "dt", "dd"]
CACHE_NAME = re.compile(r"all_events_(\d{2})-(\d{2})-(\d{4})\.json$")
WIDTH = 88
FIELDS = ("biological_process_id", "biological_object_id", "biological_action_id")
CACHE_KEYS = dict(zip(FIELDS, ("biological_process", "biological_object", "biological_action"), strict=True))


def tidy(text: str) -> str:
    text = " ".join(text.split())
    return re.sub(r"\s+([,.;:)])", r"\1", text).replace("( ", "(")


def paragraphs(html: str | None) -> list[str]:
    """The text of an AOP-Wiki HTML field, one string per paragraph.

    Every piece of text is read once: text between blocks, or beside a nested
    block, is a paragraph of its own, and a table row is read whole.
    """
    found: list[str] = []
    pending: list[str] = []

    def flush() -> None:
        text = tidy(" ".join(pending))
        pending.clear()
        if text:
            found.append(text)

    def walk(node) -> None:
        for child in node.children:
            name = getattr(child, "name", None)
            if isinstance(child, PreformattedString):
                continue  # comments, CDATA and declarations are not text
            if name is None:
                pending.append(str(child))
            elif name == "tr" and not child.find("table"):
                flush()
                cells = [tidy(c.get_text(" ")) for c in child.find_all(["td", "th"])]
                text = "; ".join(c for c in cells if c)
                if text:
                    found.append(text)
            elif name in BLOCKS or child.find(BLOCKS + ["tr"]):
                flush()
                walk(child)
                flush()
            else:
                pending.append(child.get_text(" "))

    walk(BeautifulSoup(html or "", "html.parser"))
    flush()
    return found


def folded(key: str, texts: list[str], indent: int = 2) -> list[str]:
    """A folded block scalar whose value is the paragraphs joined by newlines."""
    pad = " " * (indent + 2)
    lines = [" " * indent + f"{key}: >-"]
    for i, text in enumerate(texts):
        if i:
            lines.append("")
        lines += textwrap.wrap(
            text, WIDTH - len(pad), initial_indent=pad, subsequent_indent=pad,
            break_long_words=False, break_on_hyphens=False,
        )
    return lines


def lookup(term: dict) -> dict:
    """An EMOD term lookup with only the fields AOP-Wiki filled."""
    return {f: term[f] for f in ("source", "source_id", "term") if term.get(f)}


def component(ec: dict) -> dict:
    """An aop_wiki_cli event component in EMOD's field names, without an id."""
    found = {}
    for field, key in CACHE_KEYS.items():
        term = lookup(ec.get(key) or {})
        if field == "biological_action_id":
            term = {"term": term["term"]} if term.get("term") else {}
        if term.get("term"):
            found[field] = term
    return found


def component_ids(directory: Path) -> dict[str, int]:
    """Each event component record's combination, keyed by its JSON, and its id."""
    ids = {}
    for path in sorted(directory.glob("*.yaml")):
        ec = (yaml.safe_load(path.read_text()) or {}).get("event_component") or {}
        combination = {f: lookup(ec[f]) for f in FIELDS if f in ec}
        ids[json.dumps(combination, sort_keys=True)] = ec.get("id")
    return ids


def snapshot_date(events_json: Path) -> str:
    match = CACHE_NAME.search(events_json.name)
    if not match:
        raise SystemExit(f"cannot read a snapshot date from {events_json.name}")
    month, day, year = match.groups()
    return f"{year}-{month}-{day}"


def record(event: dict, snapshot: str, ids: dict[str, int]) -> tuple[list[str], list[dict]]:
    """The record's lines, and the components that have no record."""
    ke = event["ke_id"]
    lines = [
        f"id: aop.events:{ke}",
        "status: DRAFT",
        f'aop_wiki_snapshot: "{snapshot}"',
        f"source_uri: https://aopwiki.org/events/{ke}",
        "event:",
        f"  id: {ke}",
        f"  title: {json.dumps(event['title'], ensure_ascii=False)}",
        f"  short_name: {json.dumps(event['short_name'], ensure_ascii=False)}",
        "  biological_organization_id:",
        f"    term: {event['level_of_biological_organization']}",
    ]
    for field, key in (("cell_term_id", "cell_term"), ("organ_term_id", "organ_term")):
        term = lookup(event.get(key) or {})
        if term.get("term"):
            lines += [f"  {field}:"] + [f"    {f}: {v}" for f, v in term.items()]

    missing = []
    components = [component(ec) for ec in event.get("ecs") or []]
    if components:
        lines.append("  event_components:")
    for ec in components:
        cid = ids.get(json.dumps(ec, sort_keys=True))
        if cid is None:
            missing.append(ec)
        entry = ([f"id: {cid}"] if cid is not None else []) + [
            line for field, term in ec.items()
            for line in [f"{field}:"] + [f"  {f}: {v}" for f, v in term.items()]
        ]
        lines += ["  - " + entry[0]] + ["    " + line for line in entry[1:]]

    for key, source in (("definition", "description"), ("measured_or_detected", "measurement_method")):
        texts = paragraphs(event.get(source))
        if texts:
            lines += folded(key, texts)
    return lines, missing


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    events_json, ke = Path(sys.argv[1]), sys.argv[2]
    directory = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("data/event_components")
    events = json.loads(events_json.read_text())
    if ke not in events:
        print(f"ERROR KE {ke} is not in {events_json}", file=sys.stderr)
        return 1
    lines, missing = record(events[ke], snapshot_date(events_json), component_ids(directory))
    print("\n".join(lines))
    for ec in missing:
        print(f"NOTE KE {ke}: no record under {directory} for the component {ec}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
