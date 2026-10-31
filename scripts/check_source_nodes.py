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
  scripts/source_node.py would write for the node today.

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


def check(directory: Path, root: Path) -> tuple[list[str], int]:
    problems, checked = [], 0
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
    return problems, checked


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("directory", nargs="?", type=Path, default=Path("data/key_events"))
    parser.add_argument("--dismech-root", type=Path, help="dismech checkout (default $DISMECH_ROOT)")
    args = parser.parse_args(argv)
    root = source_node.dismech_root(args.dismech_root)
    if not (root / "kb" / "disorders").is_dir():
        raise SystemExit(f"{root} is not a dismech checkout (no kb/disorders/)")
    problems, checked = check(args.directory, root)
    for problem in problems:
        print(f"DIFF {problem}")
    print(f"{checked} dismech source node(s) checked against {root}, {len(problems)} difference(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
