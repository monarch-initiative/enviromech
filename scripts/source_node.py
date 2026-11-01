"""Print a dismech pathograph node as a source_nodes item for a Key Event record.

    python scripts/source_node.py ENTRY "NODE NAME" [--dismech-root DIRECTORY]

Once a curator has chosen the dismech node a Key Event aggregates (just crosswalk
lists the candidates), the item under the record's aggregation.source_nodes is a
copy of what dismech records for that node. This script makes the copy, from
kb/disorders/ENTRY.yaml in the dismech checkout at --dismech-root (default
$DISMECH_ROOT, else ~/Developer/dismech):

- source_node_ref in dismech's cross-entry grammar, ENTRY:pathophysiology#NODE;
- source_entry, source_entry_uri, node_name;
- source_level, the node's biological_scale verbatim, and
  biological_organization_id, that scale mapped onto EMOD's levels;
- processes, from biological_processes and molecular_functions;
- objects, from cell_types, locations, cellular_components and chemical_entities;
- biological_action_id, when every process modifier maps onto the same EMOD action;
- source_confidence, the node's mechanism_confidence, when it has one.

Every term carries its source, id and label. The node's description is printed as a
comment above the item. What a curator decides is left out: the
aggregation_relation, the rationale, the level_mismatch_note and the notes.

It reads dismech's content only, never its code.
"""

import argparse
import os
import sys
from pathlib import Path

import yaml

DEFAULT_DISMECH = Path("~/Developer/dismech")
ENTRY_URI = "https://dismech.monarchinitiative.org/pages/disorders/{entry}.html"
# dismech biological_scale -> EMOD level of biological organization. dismech's TISSUE
# covers tissue and organ; Tissue is the nearer reading.
LEVEL_FOR_SCALE = {
    "MOLECULAR": "Molecular",
    "CELLULAR": "Cellular",
    "TISSUE": "Tissue",
    "ORGANISM": "Individual",
}
# dismech ModifierEnum -> EMOD BiologicalActionEnum. The other modifiers
# (DYSREGULATED, GAIN_OF_FUNCTION, LOSS_OF_FUNCTION, ABSENT) have no one EMOD action.
ACTION_FOR_MODIFIER = {"INCREASED": "increased", "DECREASED": "decreased", "ABNORMAL": "abnormal"}
PROCESS_FIELDS = ("biological_processes", "molecular_functions")
OBJECT_FIELDS = ("cell_types", "locations", "cellular_components", "chemical_entities")


def dismech_root(given: Path | None) -> Path:
    return (given or Path(os.environ.get("DISMECH_ROOT") or DEFAULT_DISMECH)).expanduser()


def find_node(root: Path, entry: str, name: str) -> dict:
    path = root / "kb" / "disorders" / f"{entry}.yaml"
    if not path.exists():
        raise SystemExit(f"no dismech entry {path}")
    nodes = (yaml.safe_load(path.read_text()) or {}).get("pathophysiology") or []
    for node in nodes:
        if node.get("name") == name:
            return node
    names = "\n  ".join(n.get("name", "") for n in nodes)
    raise SystemExit(f"{entry} has no pathophysiology node named {name!r}. Its nodes:\n  {names}")


def terms(node: dict, fields: tuple[str, ...]) -> list[dict]:
    found, seen = [], set()
    for field in fields:
        for item in node.get(field) or []:
            term = item.get("term") or {}
            curie = term.get("id")
            if not curie or curie in seen:
                continue
            seen.add(curie)
            found.append({"source": curie.split(":", 1)[0], "source_id": curie, "term": term.get("label")})
    return found


def action(node: dict) -> tuple[str | None, str | None]:
    """The EMOD action the node's process modifiers give, or None and the reason."""
    modifiers = {
        item.get("modifier") for field in PROCESS_FIELDS for item in node.get(field) or []
    } - {None}
    if not modifiers:
        return None, "dismech binds no modifier to the node's processes"
    actions = {ACTION_FOR_MODIFIER.get(m) for m in modifiers}
    if len(actions) == 1 and None not in actions:
        return actions.pop(), None
    return None, f"the node's process modifiers ({', '.join(sorted(modifiers))}) give no one EMOD action"


def source_node(entry: str, node: dict) -> tuple[dict, list[str]]:
    """The source_nodes item, and the comments to print above it."""
    name = node["name"]
    item = {
        "source_knowledge_base": "dismech",
        "source_node_ref": f"{entry}:pathophysiology#{name}",
        "source_entry": entry,
        "source_entry_uri": ENTRY_URI.format(entry=entry),
        "node_name": name,
    }
    comments = []
    scale = node.get("biological_scale")
    if scale:
        item["source_level"] = scale
        if scale in LEVEL_FOR_SCALE:
            item["biological_organization_id"] = {"term": LEVEL_FOR_SCALE[scale]}
        else:
            comments.append(f"no biological_organization_id: dismech scale {scale!r} has no EMOD level")
    else:
        comments.append("dismech records no biological_scale for this node")
    for key, fields in (("processes", PROCESS_FIELDS), ("objects", OBJECT_FIELDS)):
        found = terms(node, fields)
        if found:
            item[key] = found
    emod_action, reason = action(node)
    if emod_action:
        item["biological_action_id"] = {"term": emod_action}
    else:
        comments.append(f"no biological_action_id: {reason}")
    if node.get("mechanism_confidence"):
        item["source_confidence"] = str(node["mechanism_confidence"])
    return item, comments


def render(item: dict, comments: list[str], description: str | None) -> str:
    lines = []
    if description:
        lines.append(f"# dismech description: {' '.join(description.split())}")
    lines += [f"# {c}" for c in comments]
    body = yaml.safe_dump([item], sort_keys=False, allow_unicode=True, width=100)
    return "\n".join(lines + [body.rstrip("\n")]) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("entry", help="dismech entry slug, e.g. Contact_Dermatitis")
    parser.add_argument("node", help="the node's name, exactly as dismech spells it")
    parser.add_argument("--dismech-root", type=Path, help="dismech checkout (default $DISMECH_ROOT)")
    args = parser.parse_args(argv)
    node = find_node(dismech_root(args.dismech_root), args.entry, args.node)
    item, comments = source_node(args.entry, node)
    print(render(item, comments, node.get("description")), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
