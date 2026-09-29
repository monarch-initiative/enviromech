#!/usr/bin/env python3
"""Resolve a dismech node reference into a ``SourceNode`` block.

A ``KeyEventAggregation`` names each aggregated node by ``source_node_ref``,
written in dismech's cross-entry reference grammar::

    Primary_Ciliary_Dyskinesia:pathophysiology#Ciliary Dysfunction

This script looks that reference up in a dismech checkout and emits the
``SourceNode`` block the schema describes: the node's values *copied from the
source*, with its GO, CL and UBERON descriptors re-typed as the EMOD
``BiologicalProcess`` and ``BiologicalObject`` classes so they can be compared
with the Event's ``event_components``. The two committed examples were built by
hand; this is the step that lets them be checked instead of trusted.

    just resolve-source-node "Primary_Ciliary_Dyskinesia:pathophysiology#Ciliary Dysfunction"
    just check-source-nodes src/data/examples/KeyEventAggregation-KE1908.yaml

It runs under dismech's own environment (``uv run --project <dismech>``) and
imports dismech's reference parser, so the grammar is dismech's, not a copy.
The dismech checkout is a sibling directory by default, the same placeholder
arrangement the schema uses for its linkml-aop import.

What it emits is a starting point, not a finished block. It copies every
descriptor the node binds; the curator prunes to what the Event is about, and
writes ``notes``. The integer ``id`` values on the EMOD term classes are local
placeholders (see the decision register entry on identifying lookup terms
outside the EMOD database): the level and action tables below copy the numbers
the committed examples use, and process/object ids are numbered per run.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import pathlib
import subprocess
import sys
from typing import Any

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Where a dismech entry can live, in lookup order, with the page path its
# rendered site uses for the source_entry_uri.
ENTRY_ROOTS = (
    ("kb/disorders", "disorders"),
    ("kb/modules", "modules"),
    ("kb/comorbidities", "comorbidities"),
)
PAGE_BASE = "https://dismech.monarchinitiative.org/pages"

# dismech biological_scale -> EMOD LevelOfBiologicalOrganization.
# Integer ids are placeholders copied from the committed examples (Cellular 2,
# Tissue 3, Individual 5); the rest follow BiologicalOrganizationEnum order.
# ORGANISM -> Individual crosses vocabularies and is reported when used.
LEVELS: dict[str, tuple[int, str]] = {
    "MOLECULAR": (1, "Molecular"),
    "CELLULAR": (2, "Cellular"),
    "TISSUE": (3, "Tissue"),
    "ORGANISM": (5, "Individual"),
}

# dismech Descriptor.modifier -> EMOD BiologicalActionEnum, only where the two
# vocabularies say the same thing. DYSREGULATED, ABSENT, GAIN_OF_FUNCTION and
# LOSS_OF_FUNCTION have no exact counterpart and are left for the curator.
# Integer ids are placeholders copied from the committed examples.
ACTIONS: dict[str, tuple[int, str]] = {
    "INCREASED": (1, "increased"),
    "DECREASED": (2, "decreased"),
    "ABNORMAL": (4, "abnormal"),
}

# dismech node slots that carry EMOD BiologicalProcess terms, and the prefixes
# EMOD's BiologicalProcessSourceEnum admits.
PROCESS_SLOTS = ("biological_processes", "molecular_functions")
PROCESS_SOURCES = {"GO", "HP", "MP", "NBO", "VT", "MESH", "PCO", "MI", "IDO", "NCI", "RBO"}

# dismech node slots that carry EMOD BiologicalObject terms, and the prefixes
# BiologicalObjectSourceEnum admits. Genes (hgnc:) are deliberately not here:
# EMOD has no gene source, so they cannot be re-typed and are reported instead.
OBJECT_SLOTS = ("cell_types", "locations", "cellular_components", "chemical_entities", "protein_complexes")
OBJECT_SOURCES = {"GO", "CHEBI", "CL", "PR", "UBERON", "FMA", "MESH", "PCO", "MP", "TAIR"}


def dismech_root(explicit: pathlib.Path | None) -> pathlib.Path:
    root = explicit or pathlib.Path(os.environ.get("DISMECH_ROOT", REPO_ROOT.parent / "dismech"))
    root = root.resolve()
    if not (root / "kb").is_dir():
        sys.exit(f"error: no kb/ under {root}; pass --dismech or set DISMECH_ROOT")
    return root


def import_dismech(root: pathlib.Path):
    sys.path.insert(0, str(root / "src"))
    try:
        from dismech import entity_refs  # noqa: PLC0415
        from dismech.yaml_io import safe_load_path  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - environment problem
        sys.exit(f"error: cannot import dismech from {root / 'src'}: {exc}")
    return entity_refs, safe_load_path


def git_stamp(root: pathlib.Path) -> str:
    try:
        sha = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        sha = "unknown"
    return f"dismech {sha}, read {_dt.date.today().isoformat()}"


def find_entry(root: pathlib.Path, slug: str) -> tuple[pathlib.Path, str] | None:
    for kb_dir, page_dir in ENTRY_ROOTS:
        path = root / kb_dir / f"{slug}.yaml"
        if path.is_file():
            return path, page_dir
    return None


def curie_prefix(term: dict[str, Any] | None) -> str | None:
    if not isinstance(term, dict):
        return None
    curie = term.get("id")
    if not isinstance(curie, str) or ":" not in curie:
        return None
    return curie.split(":", 1)[0].upper()


def emod_terms(node: dict[str, Any], slots: tuple[str, ...], admitted: set[str],
               first_id: int, report: list[str]) -> list[dict[str, Any]]:
    """Re-type dismech descriptors in ``slots`` as EMOD term objects."""
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    next_id = first_id
    for slot in slots:
        for desc in node.get(slot) or []:
            if not isinstance(desc, dict):
                continue
            term = desc.get("term")
            prefix = curie_prefix(term)
            if prefix is None:
                report.append(f"{slot}: {desc.get('preferred_term')!r} has no bound term; skipped")
                continue
            if prefix not in admitted:
                report.append(f"{slot}: {term['id']} ({prefix}) is not an EMOD source for this class; skipped")
                continue
            if term["id"] in seen:
                continue
            seen.add(term["id"])
            out.append({
                "id": next_id,
                "source": prefix,
                "source_id": term["id"],
                "term": term.get("label"),
            })
            next_id += 1
    return out


def action_for(node: dict[str, Any], report: list[str]) -> dict[str, Any] | None:
    modifiers: list[str] = []
    for slot in PROCESS_SLOTS:
        for desc in node.get(slot) or []:
            if isinstance(desc, dict) and desc.get("modifier"):
                modifiers.append(str(desc["modifier"]))
    distinct = sorted(set(modifiers))
    if not distinct:
        report.append("no modifier on any bound process; biological_action_id left for the curator")
        return None
    if len(distinct) > 1:
        report.append(f"processes carry different modifiers {distinct}; biological_action_id left for the curator")
        return None
    mapped = ACTIONS.get(distinct[0])
    if mapped is None:
        report.append(f"modifier {distinct[0]} has no exact BiologicalActionEnum value; biological_action_id left for the curator")
        return None
    return {"id": mapped[0], "term": mapped[1]}


def resolve(ref: str, root: pathlib.Path, entity_refs, safe_load_path) -> tuple[dict[str, Any] | None, list[str]]:
    """Return (SourceNode block, report lines). The block is None when the ref does not resolve."""
    report: list[str] = []
    parsed = entity_refs.parse_entity_ref(ref)
    if parsed is None or parsed.file is None:
        return None, [f"{ref!r} is not a cross-entry reference of the form <entry>:<section>#<name>"]
    if parsed.kind not in entity_refs.SECTION_KEYS:
        return None, [f"section {parsed.kind!r} is not one dismech's entity_refs knows"]
    slot, key_slots = entity_refs.SECTION_KEYS[parsed.kind]

    found = find_entry(root, parsed.file)
    if found is None:
        return None, [f"no dismech entry named {parsed.file!r} under {', '.join(k for k, _ in ENTRY_ROOTS)}"]
    path, page_dir = found
    data = safe_load_path(path)

    matches = [
        item for item in entity_refs.section_items(data, slot)
        if isinstance(item, dict) and any(item.get(k) == parsed.name for k in key_slots)
    ]
    if not matches:
        return None, [f"{parsed.file}: no {slot} item named {parsed.name!r}"]
    if len(matches) > 1:
        report.append(f"{len(matches)} {slot} items named {parsed.name!r}; using the first")
    node = matches[0]

    block: dict[str, Any] = {
        "source_knowledge_base": "dismech",
        "source_node_ref": ref,
        "source_entry": parsed.file,
        "source_entry_uri": f"{PAGE_BASE}/{page_dir}/{parsed.file}.html",
        "node_name": parsed.name,
    }
    scale = node.get("biological_scale")
    if scale:
        block["source_level"] = scale
        level = LEVELS.get(str(scale))
        if level:
            block["biological_organization_id"] = {"id": level[0], "term": level[1]}
            if scale == "ORGANISM":
                report.append("biological_scale ORGANISM mapped to EMOD Individual; check the Event's level")
        else:
            report.append(f"biological_scale {scale!r} has no EMOD level mapping")
    else:
        report.append("node carries no biological_scale; source_level and biological_organization_id omitted")

    processes = emod_terms(node, PROCESS_SLOTS, PROCESS_SOURCES, 101, report)
    objects = emod_terms(node, OBJECT_SLOTS, OBJECT_SOURCES, 201, report)
    if processes:
        block["processes"] = processes
    if objects:
        block["objects"] = objects
    action = action_for(node, report)
    if action:
        block["biological_action_id"] = action
    if node.get("mechanism_confidence"):
        block["source_confidence"] = node["mechanism_confidence"]
    genes = [g.get("preferred_term") for g in node.get("genes") or [] if isinstance(g, dict)]
    if genes:
        report.append(f"node binds genes {genes}; EMOD has no gene object source, so they are not copied")
    return block, report


def check_file(path: pathlib.Path, root: pathlib.Path, entity_refs, safe_load_path) -> int:
    """Check every source_nodes[] entry of a KeyEventAggregation against dismech."""
    data = yaml.safe_load(path.read_text())
    failures = 0
    for i, node in enumerate(data.get("source_nodes") or []):
        ref = node.get("source_node_ref")
        label = f"{path.name} source_nodes[{i}]"
        if not ref:
            print(f"FAIL {label}: no source_node_ref")
            failures += 1
            continue
        block, report = resolve(ref, root, entity_refs, safe_load_path)
        if block is None:
            print(f"FAIL {label}: {ref}\n     " + "\n     ".join(report))
            failures += 1
            continue
        problems = []
        for key in ("source_entry", "node_name", "source_level"):
            if key in node and node[key] != block.get(key):
                problems.append(f"{key} is {node[key]!r} in the record, {block.get(key)!r} in dismech")
        recorded = {p.get("source_id") for p in node.get("processes") or []} | {o.get("source_id") for o in node.get("objects") or []}
        source = {p["source_id"] for p in block.get("processes") or []} | {o["source_id"] for o in block.get("objects") or []}
        for curie in sorted(recorded - source):
            problems.append(f"{curie} is on the record but dismech does not bind it to this node")
        if problems:
            print(f"FAIL {label}: {ref}\n     " + "\n     ".join(problems))
            failures += 1
        else:
            omitted = sorted(source - recorded)
            extra = f" (record omits {len(omitted)} bound term(s): {', '.join(omitted)})" if omitted else ""
            print(f"OK   {label}: {ref}{extra}")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("refs", nargs="*", help="one or more <entry>:<section>#<name> references")
    ap.add_argument("--dismech", type=pathlib.Path, help="dismech checkout (default: ../dismech or $DISMECH_ROOT)")
    ap.add_argument("--check", type=pathlib.Path, action="append", default=[],
                    help="a KeyEventAggregation YAML file whose source_nodes to check against dismech; repeatable")
    args = ap.parse_args()
    if not args.refs and not args.check:
        ap.error("give at least one reference or --check FILE")

    root = dismech_root(args.dismech)
    entity_refs, safe_load_path = import_dismech(root)

    failures = 0
    for path in args.check:
        failures += check_file(path, root, entity_refs, safe_load_path)

    if args.refs:
        blocks: list[dict[str, Any]] = []
        for ref in args.refs:
            block, report = resolve(ref, root, entity_refs, safe_load_path)
            for line in report:
                print(f"note [{ref}]: {line}", file=sys.stderr)
            if block is None:
                failures += 1
                continue
            blocks.append(block)
        if blocks:
            print(f"# Copied from {git_stamp(root)}. Term ids are local placeholders.")
            print(yaml.safe_dump({"source_nodes": blocks}, sort_keys=False, allow_unicode=True, width=100), end="")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
