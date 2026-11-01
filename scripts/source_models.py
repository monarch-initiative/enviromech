"""Print the dismech models linked to a node, as the models list of a source_nodes item.

    python scripts/source_models.py ENTRY "NODE NAME" [--dismech-root DIRECTORY]

A source node in a Key Event record's aggregation can carry the models dismech
links to that node, so a query can go from the Key Event to the node to the model.
dismech points the link the other way, from the model to the node, so finding a
node's models means scanning every model in the entry. That walk is dismech's own,
dismech.model_links.iter_model_links, imported from the checkout at --dismech-root
(default $DISMECH_ROOT, else ~/Developer/dismech) rather than repeated here; the
model's reference key is read through dismech.entity_refs, the resolver dismech
uses for the same grammar.

For each link in kb/disorders/ENTRY.yaml whose target is the node, from the
curated sections only (experimental_models, animal_models, computational_models;
not the model systems of a proposed experiment), it writes:

- model_ref, ENTRY:SECTION#KEY in dismech's cross-entry grammar, where KEY is the
  model's name or, for an unnamed animal model, its species or genotype;
- model_section and model_name, the readable parts of model_ref;
- source_relationship, the link's relationship, verbatim, when it has one.

The output is the models: block, to paste into the source_nodes item for the node.
Nothing about a model's fidelity, limitations, readouts, divergences or evidence
is copied.
"""

import argparse
import importlib
import os
import sys
from collections.abc import Iterable
from pathlib import Path

import yaml

DEFAULT_DISMECH = Path("~/Developer/dismech")


def dismech_root(given: Path | None) -> Path:
    return (given or Path(os.environ.get("DISMECH_ROOT") or DEFAULT_DISMECH)).expanduser()


def dismech_modules(root: Path):
    """dismech's model_links and entity_refs modules, imported from the checkout."""
    src = root / "src"
    if not (src / "dismech" / "model_links.py").exists():
        raise SystemExit(f"{src / 'dismech' / 'model_links.py'} does not exist; "
                         "set DISMECH_ROOT to a dismech checkout")
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    return importlib.import_module("dismech.model_links"), importlib.import_module("dismech.entity_refs")


def load_entry(root: Path, entry: str) -> dict:
    path = root / "kb" / "disorders" / f"{entry}.yaml"
    if not path.exists():
        raise SystemExit(f"no dismech entry {path}")
    return yaml.safe_load(path.read_text()) or {}


def model_key(model: dict, section: str, entity_refs) -> str | None:
    """The value dismech's resolver matches a SECTION#KEY reference on, for this model."""
    _, key_slots = entity_refs.SECTION_KEYS[section]
    for slot in key_slots:
        value = model.get(slot)
        if isinstance(value, str) and value:
            return value
    return None


def link_target(link: dict, entity_refs) -> str | None:
    """The node name a link targets: a plain name, or the name in a pathophysiology# ref."""
    target = link.get("target")
    parsed = entity_refs.parse_entity_ref(target)
    if parsed is None:
        return target if isinstance(target, str) else None
    if parsed.file is None and entity_refs.canonical_kind(parsed.kind) == "pathophysiology":
        return parsed.name
    return None


def model_items(entry: str, data: dict, node: str, sites: Iterable,
                entity_refs) -> tuple[list[dict], list[str]]:
    """The models items for the node, and comments on links that could not be written."""
    items, comments = [], []
    for site in sites:
        if site.proposed or link_target(site.link, entity_refs) != node:
            continue
        section = site.path_prefix
        key = model_key(site.model, section, entity_refs)
        if key is None:
            comments.append(f"{section}[{site.model_index}] links to the node but has no name, "
                            "species or genotype to reference it by")
            continue
        item = {
            "model_ref": f"{entry}:{section}#{key}",
            "model_section": section,
            "model_name": key,
        }
        if site.link.get("relationship"):
            item["source_relationship"] = str(site.link["relationship"])
        if not entity_refs.resolve_entity_ref(data, f"{section}#{key}"):
            comments.append(f"{item['model_ref']} does not resolve in dismech")
        items.append(item)
    return items, comments


def models_for_node(root: Path, entry: str, node: str) -> tuple[list[dict], list[str]]:
    model_links, entity_refs = dismech_modules(root)
    data = load_entry(root, entry)
    names = [n.get("name") for n in data.get("pathophysiology") or []]
    if node not in names:
        listed = "\n  ".join(str(n) for n in names)
        raise SystemExit(f"{entry} has no pathophysiology node named {node!r}. Its nodes:\n  {listed}")
    sites = model_links.iter_model_links(data, include_proposed=False)
    return model_items(entry, data, node, sites, entity_refs)


def render(items: list[dict], comments: list[str]) -> str:
    lines = [f"# {c}" for c in comments]
    if not items:
        lines.append("# dismech links no curated model to this node")
        return "\n".join(lines) + "\n"
    body = yaml.safe_dump({"models": items}, sort_keys=False, allow_unicode=True, width=1000)
    return "\n".join(lines + [body.rstrip("\n")]) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("entry", help="dismech entry slug, e.g. Contact_Dermatitis")
    parser.add_argument("node", help="the node's name, exactly as dismech spells it")
    parser.add_argument("--dismech-root", type=Path, help="dismech checkout (default $DISMECH_ROOT)")
    args = parser.parse_args(argv)
    items, comments = models_for_node(dismech_root(args.dismech_root), args.entry, args.node)
    print(render(items, comments), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
