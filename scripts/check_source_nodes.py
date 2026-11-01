"""Check every dismech source node in the Key Event records against dismech today.

    python scripts/check_source_nodes.py [KEY_EVENT_DIRECTORY] [--dismech-root DIRECTORY]

A Key Event record's aggregation copies what dismech recorded for each node when the
aggregation was written. dismech keeps curating, so a node can later be renamed,
removed, or have its level or terms change, and the copy no longer describes it.
For each source node with source_knowledge_base dismech, in the Key Event records
under KEY_EVENT_DIRECTORY (default data/key_events), this reads the node from the
dismech checkout at --dismech-root (default $DISMECH_ROOT, else ~/Developer/dismech)
and reports:

- a node or entry that no longer exists;
- a source_node_ref that does not agree with source_entry and node_name;
- a source_level, process, object, action or confidence that differs from what
  scripts/source_node.py would write for the node today;
- for a node with a models list, a model_ref that does not agree with its
  model_section and model_name, a model that was renamed or removed (its ref no
  longer resolves), a model that no longer links to the node or links to it with
  another relationship, and a curated model dismech now links to the node that the
  list does not have. These read dismech through scripts/source_models.py, which
  imports dismech's own iter_model_links and entity_refs from the checkout.

Each assay record's model_matches under data/assays is checked too: a
model_ref that no longer resolves in dismech is reported, since the match then
names a model that was renamed or removed.

A node with no models list is not compared, since absence means the list has not
been written; the report notes how many models dismech links to it.

A difference is not always an error: the curator may have left a term out on
purpose, and notes should then say so. The report is for a curator to read. Exits 1
if anything differs. Not part of just qc: CI has no dismech checkout.
"""

import argparse
import importlib.util
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("source_node", HERE / "source_node.py")
source_node = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(source_node)
_spec = importlib.util.spec_from_file_location("source_models", HERE / "source_models.py")
source_models = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(source_models)

COMPARED = ("source_level", "biological_organization_id", "processes", "objects",
            "biological_action_id", "source_confidence")


def _ids(terms: list[dict] | None) -> set[str]:
    return {t.get("source_id") for t in terms or []}


def differences(recorded: dict, current: dict) -> list[str]:
    found = []
    for key in COMPARED:
        was, now = recorded.get(key), current.get(key)
        if key in ("processes", "objects"):
            added, dropped = sorted(_ids(now) - _ids(was)), sorted(_ids(was) - _ids(now))
            if added:
                found.append(f"{key}: dismech now also binds {', '.join(added)}")
            if dropped:
                found.append(f"{key}: dismech no longer binds {', '.join(dropped)}")
            labels = {t["source_id"]: t.get("term") for t in now or []}
            for t in was or []:
                if t.get("source_id") in labels and labels[t["source_id"]] != t.get("term"):
                    found.append(
                        f"{key}: {t['source_id']} is labelled {labels[t['source_id']]!r} in dismech, "
                        f"{t.get('term')!r} here"
                    )
        elif was != now:
            found.append(f"{key}: {was!r} here, {now!r} in dismech")
    return found


def _model_key(item: dict) -> tuple:
    return item.get("model_ref"), item.get("source_relationship")


def model_differences(entry: str, recorded: list[dict], current: list[dict],
                      resolves) -> list[str]:
    """Differences between a node's recorded models and what dismech links to it today.

    ``current`` is what scripts/source_models.py writes for the node now, and
    ``resolves`` says whether a SECTION#KEY reference resolves in the entry.
    """
    found, changed = [], set()
    now = {_model_key(i) for i in current}
    now_refs = {i["model_ref"]: i.get("source_relationship") for i in current}
    for item in recorded:
        ref, section, name = item.get("model_ref"), item.get("model_section"), item.get("model_name")
        if ref != f"{entry}:{section}#{name}":
            found.append(f"model {ref!r} does not agree with model_section and model_name")
        if _model_key(item) in now:
            continue
        local = ref.split(":", 1)[1] if ref and ":" in ref else ref
        if not resolves(local):
            found.append(f"model {ref}: renamed or removed in dismech")
        elif ref in now_refs:
            changed.add(ref)
            found.append(f"model {ref}: source_relationship {item.get('source_relationship')!r} here, "
                         f"{now_refs[ref]!r} in dismech")
        else:
            found.append(f"model {ref}: no longer linked to this node in dismech")
    was = {_model_key(i) for i in recorded}
    for item in current:
        if _model_key(item) not in was and item["model_ref"] not in changed:
            found.append(f"model {item['model_ref']}: dismech now also links it to this node "
                         f"({item.get('source_relationship')})")
    return found


def check(directory: Path, root: Path, *, models: bool | None = None) -> tuple[list[str], int]:
    """Differences across the records, and the number of nodes checked.

    ``models`` turns the model checks on or off; by default they run when ``root``
    has dismech's code (src/dismech/model_links.py), which they import.
    """
    return check_with_notes(directory, root, models=models)[:2]


def check_with_notes(directory: Path, root: Path, *, models: bool | None = None
                     ) -> tuple[list[str], int, list[str]]:
    if models is None:
        models = (root / "src" / "dismech" / "model_links.py").exists()
    if models:
        _, entity_refs = source_models.dismech_modules(root)
    problems, checked, notes = [], 0, []
    for path in sorted(directory.glob("*.yaml")):
        record = yaml.safe_load(path.read_text()) or {}
        for recorded in (record.get("aggregation") or {}).get("source_nodes") or []:
            if recorded.get("source_knowledge_base") != "dismech":
                continue
            checked += 1
            entry, name = recorded.get("source_entry"), recorded.get("node_name")
            where = f"{path.name}: {entry}#{name}"
            if recorded.get("source_node_ref") != f"{entry}:pathophysiology#{name}":
                problems.append(f"{where}: source_node_ref {recorded.get('source_node_ref')!r} "
                                "does not agree with source_entry and node_name")
            try:
                node = source_node.find_node(root, entry, name)
            except SystemExit as gone:
                problems.append(f"{where}: {str(gone).splitlines()[0]}")
                continue
            current, _ = source_node.source_node(entry, node)
            problems += [f"{where}: {d}" for d in differences(recorded, current)]
            if not models:
                continue
            linked, _ = source_models.models_for_node(root, entry, name)
            if "models" not in recorded:
                if linked:
                    notes.append(f"{where}: no models list; dismech links {len(linked)} curated model(s)")
                continue
            data = source_models.load_entry(root, entry)
            problems += [f"{where}: {d}" for d in model_differences(
                entry, recorded["models"], linked,
                lambda ref, data=data: entity_refs.resolve_entity_ref(data, ref))]
    return problems, checked, notes


def check_model_matches(assays: Path, root: Path) -> tuple[list[str], int]:
    """Assay records' model_matches whose model_ref no longer resolves in dismech."""
    if not assays.is_dir() or not (root / "src" / "dismech" / "model_links.py").exists():
        return [], 0
    _, entity_refs = source_models.dismech_modules(root)
    problems, checked, entries = [], 0, {}
    for path in sorted(assays.glob("*.yaml")):
        record = yaml.safe_load(path.read_text()) or {}
        for match in record.get("model_matches") or []:
            ref = match.get("model_ref") or ""
            entry, _, local = ref.partition(":")
            checked += 1
            if entry not in entries:
                try:
                    entries[entry] = source_models.load_entry(root, entry)
                except SystemExit as gone:
                    problems.append(f"{path.name}: {ref}: {gone}")
                    entries[entry] = None
                    continue
            if entries[entry] is not None and not entity_refs.resolve_entity_ref(entries[entry], local):
                problems.append(f"{path.name}: matched model {ref}: renamed or removed in dismech")
    return problems, checked


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("directory", nargs="?", type=Path, default=Path("data/key_events"))
    parser.add_argument("--dismech-root", type=Path, help="dismech checkout (default $DISMECH_ROOT)")
    args = parser.parse_args(argv)
    root = source_node.dismech_root(args.dismech_root)
    if not (root / "kb" / "disorders").is_dir():
        raise SystemExit(f"{root} is not a dismech checkout (no kb/disorders/)")
    problems, checked, notes = check_with_notes(args.directory, root)
    matched_problems, matched = check_model_matches(args.directory.parent / "assays", root)
    problems += matched_problems
    for problem in problems:
        print(f"DIFF {problem}")
    for note in notes:
        print(f"NOTE {note}")
    print(f"{checked} dismech source node(s) and {matched} matched model(s) checked against {root}, "
          f"{len(problems)} difference(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
