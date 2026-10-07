"""Collect the Key Event sequence and the KER evidence of named AOPs.

Reads the AOP-Wiki XML export and writes, for each requested AOP, the ordered
Key Events with their roles and the Key Event Relationships with the weight of
evidence AOP-Wiki records for them.

Every value here is a **structured field of the export**, not a reading of
prose. The export carries, on each AOP's own copy of a relationship:

    <adjacency>                        adjacent | non-adjacent
    <evidence>                         High | Moderate | Low | Not Specified
    <quantitative-understanding-value> High | Moderate | Low | Not Specified

Those three are what EMOD's AopToKeRelationship holds as directness_id,
confidence_id and quantitative_understanding_id, and `evidence` is the weight
of evidence. Reading a rating out of the prose of an overall-assessment table
instead is not reproducible and gives different answers: AOP 18's hand-written
table grades two of its relationships "weak" and "very weak", words that are
not in the export's vocabulary and do not agree with its Moderate and Low.
Where the two disagree the structured value is the one to carry, and
`assessment_table_vocabulary_differs` flags the AOPs where a curator should
look.

A relationship's rating belongs to the pair (AOP, KER), not to the KER: KER2124
is High in AOPs 305 and 344 and Moderate in AOP 307. The output is keyed that
way.

The export carries no essentiality value, although EMOD's AopToEvent has a
field for it, so essentiality is absent here and has to be read from the
AOP's prose by a person.

`aop_wiki_cli` (gingin77/aop_wiki_cli) owns the download of the export and the
full entity model. This script reads the export directly because it needs three
per-AOP relationship fields that `collect_aops_from_xml` does not keep; those
belong upstream, and this script should shrink to a call once they are there.

Usage:
    python scripts/aop_evidence.py --xml PATH --aops 18,51,305,307,344
    python scripts/aop_evidence.py --xml PATH --aops 344 --format json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any

# The prose blocks a relationship record can carry, by the name this script
# reports and the path the export puts them at. Emptiness is reported per
# relationship so that a High rating sitting on an empty record is visible.
#
# Two of these paths are easy to get wrong. The prose blocks are nested under
# weight-of-evidence and quantitative-understanding, not direct children of the
# relationship; and the export misspells empirical support as
# "emperical-support-linkage", so the correct spelling silently matches nothing.
KER_PROSE_FIELDS = {
    "description": "description",
    "weight_of_evidence": "weight-of-evidence/value",
    "biological_plausibility": "weight-of-evidence/biological-plausibility",
    "empirical_support": "weight-of-evidence/emperical-support-linkage",
    "uncertainties": "weight-of-evidence/uncertainties-or-inconsistencies",
    "quantitative_description": "quantitative-understanding/description",
    "response_relationship": "quantitative-understanding/response-response-relationship",
    "time_scale": "quantitative-understanding/time-scale",
    "known_loops": "quantitative-understanding/feedforward-feedback-loops",
    "modulating_factors": "known-modulating-factors",
    "evidence_collection_strategy": "evidence-collection-strategy",
}

# Words an overall-assessment table may use that are not in the export's
# structured vocabulary. Their presence means the two sources disagree.
NON_STRUCTURED_GRADES = ("very weak", "weak", "strong")

STRUCTURED_GRADES = ("High", "Moderate", "Low", "Not Specified")


def strip_html(text: str | None) -> str:
    """Flatten AOP-Wiki's embedded HTML to one line of plain text."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()


def element_text(parent: ET.Element | None, ns: str, path: str) -> str:
    """Plain text at a child path, or the empty string when it is absent.

    The path may be nested ("weight-of-evidence/value"); each step is given the
    export's namespace, which ElementTree will not do on its own.
    """
    if parent is None:
        return ""
    return strip_html(parent.findtext("/".join(ns + step for step in path.split("/"))))


def read_export(xml_path: Path) -> tuple[ET.Element, str]:
    """Parse the export and return its root with the namespace prefix."""
    root = ET.parse(xml_path).getroot()
    namespace = root.tag.split("}")[0] + "}" if "}" in root.tag else ""
    return root, namespace


def wiki_id_map(root: ET.Element, ns: str, reference_tag: str) -> dict[str, str]:
    """Map each entity's export UUID to its AOP-Wiki id.

    The export identifies entities by UUID and records the AOP-Wiki id only in
    the vendor-specific block, so every id in the output goes through here.
    """
    vendor = root.find(ns + "vendor-specific")
    if vendor is None:
        return {}
    return {
        reference.get("id"): reference.get("aop-wiki-id")
        for reference in vendor.findall(ns + reference_tag)
        if reference.get("id") and reference.get("aop-wiki-id")
    }


def collect_key_events(root: ET.Element, ns: str) -> dict[str, dict[str, str]]:
    """Every Key Event in the export, keyed by AOP-Wiki id."""
    by_uuid = wiki_id_map(root, ns, "key-event-reference")
    events: dict[str, dict[str, str]] = {}
    for element in root.findall(ns + "key-event"):
        wiki_id = by_uuid.get(element.get("id"))
        if not wiki_id:
            continue
        events[wiki_id] = {
            "ke_id": wiki_id,
            "uuid": element.get("id"),
            "title": element_text(element, ns, "title"),
            "short_name": element_text(element, ns, "short-name"),
            "level": element_text(element, ns, "biological-organization-level"),
        }
    return events


def collect_relationships(root: ET.Element, ns: str) -> dict[str, dict[str, Any]]:
    """Every Key Event Relationship in the export, keyed by AOP-Wiki id.

    Carries the relationship's own prose blocks, which are shared by every AOP
    that uses it, but not the rating, which is per AOP.
    """
    by_uuid = wiki_id_map(root, ns, "key-event-relationship-reference")
    kers: dict[str, dict[str, Any]] = {}
    for element in root.findall(ns + "key-event-relationship"):
        wiki_id = by_uuid.get(element.get("id"))
        if not wiki_id:
            continue
        title = element.find(ns + "title")
        empty = [
            name for name, path in KER_PROSE_FIELDS.items() if not element_text(element, ns, path)
        ]
        empirical_raw = element.findtext(
            f"{ns}weight-of-evidence/{ns}emperical-support-linkage"
        )
        kers[wiki_id] = {
            "ker_id": wiki_id,
            "uuid": element.get("id"),
            "upstream_uuid": element_text(title, ns, "upstream-id"),
            "downstream_uuid": element_text(title, ns, "downstream-id"),
            "empty_prose_fields": empty,
            "populated_prose_fields": [f for f in KER_PROSE_FIELDS if f not in empty],
            "has_tabulated_evidence": "<table" in (empirical_raw or ""),
        }
    return kers


def order_key_events(roles: dict[str, str], edges: list[tuple[str, str]]) -> list[str]:
    """Order Key Events from the initiating events along the adjacent edges.

    Kahn's algorithm with ties broken by numeric AOP-Wiki id, so the order is
    the same on every run. Events the adjacent edges never order are appended by
    id; `describe_structure` is what says which those are and why it matters.
    """
    nodes = set(roles) | {end for edge in edges for end in edge}
    successors: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = {node: 0 for node in nodes}
    for upstream, downstream in sorted(set(edges)):
        successors[upstream].append(downstream)
        in_degree[downstream] += 1

    def by_id(ids: list[str]) -> list[str]:
        return sorted(set(ids), key=lambda value: (int(value) if value.isdigit() else 0, value))

    ready = by_id([node for node in nodes if in_degree[node] == 0])
    order: list[str] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for successor in sorted(successors[node]):
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                ready.append(successor)
        ready = by_id(ready)
    return order + [node for node in by_id(list(nodes)) if node not in order]


def describe_structure(
    roles: dict[str, str], edges: list[tuple[str, str]], all_edges: list[tuple[str, str]]
) -> dict[str, list[str]]:
    """Report where an AOP's chain does not hold together.

    `edges` are the adjacent relationships, `all_edges` every relationship. The
    distinction is the point: an AOP whose adverse outcome is reached only by a
    non-adjacent relationship has no step-by-step route to its own outcome, and
    an initiating event with no adjacent relationship out of it is attached to
    the pathway in name only.
    """
    nodes = set(roles) | {end for edge in all_edges for end in edge}
    adjacent_out = {upstream for upstream, _ in edges}
    adjacent_in = {downstream for _, downstream in edges}
    any_out = {upstream for upstream, _ in all_edges}
    any_in = {downstream for _, downstream in all_edges}

    def by_id(ids: set[str]) -> list[str]:
        return sorted(ids, key=lambda value: (int(value) if value.isdigit() else 0, value))

    return {
        "events_in_no_relationship": by_id(
            {node for node in nodes if node not in any_out and node not in any_in}
        ),
        "initiating_events_without_adjacent_outflow": by_id(
            {ke for ke, role in roles.items() if role == "MIE" and ke not in adjacent_out}
        ),
        "adverse_outcomes_without_adjacent_inflow": by_id(
            {ke for ke, role in roles.items() if role == "AO" and ke not in adjacent_in}
        ),
        "intermediate_events_without_adjacent_inflow": by_id(
            {
                ke
                for ke, role in roles.items()
                if role == "KE" and ke not in adjacent_in and ke in nodes
            }
        ),
    }


def collect_aop(
    element: ET.Element,
    ns: str,
    wiki_id: str,
    events: dict[str, dict[str, str]],
    kers: dict[str, dict[str, Any]],
    ke_by_uuid: dict[str, str],
    ker_by_uuid: dict[str, str],
) -> dict[str, Any]:
    """One AOP: its status, its ordered Key Events, and its rated relationships."""
    roles: dict[str, str] = {}
    for uuid in [
        child.get("key-event-id")
        for child in element.findall(ns + "key-events/" + ns + "key-event")
    ]:
        if (ke := ke_by_uuid.get(uuid)) :
            roles[ke] = "KE"
    for tag, role in (("molecular-initiating-event", "MIE"), ("adverse-outcome", "AO")):
        for child in element.findall(ns + tag):
            if (ke := ke_by_uuid.get(child.get("key-event-id"))) :
                roles[ke] = role

    rows: list[dict[str, Any]] = []
    edges: list[tuple[str, str]] = []
    all_edges: list[tuple[str, str]] = []
    for relationship in element.findall(ns + "key-event-relationships/" + ns + "relationship"):
        ker_id = ker_by_uuid.get(relationship.get("id"))
        ker = kers.get(ker_id, {})
        upstream = ke_by_uuid.get(ker.get("upstream_uuid", ""), "")
        downstream = ke_by_uuid.get(ker.get("downstream_uuid", ""), "")
        adjacency = element_text(relationship, ns, "adjacency")
        if upstream and downstream:
            all_edges.append((upstream, downstream))
            if adjacency == "adjacent":
                edges.append((upstream, downstream))
        rows.append(
            {
                "ker_id": ker_id,
                "upstream_ke": upstream,
                "upstream_title": events.get(upstream, {}).get("title", ""),
                "downstream_ke": downstream,
                "downstream_title": events.get(downstream, {}).get("title", ""),
                "adjacency": adjacency,
                "weight_of_evidence": element_text(relationship, ns, "evidence"),
                "quantitative_understanding": element_text(
                    relationship, ns, "quantitative-understanding-value"
                ),
                "empty_prose_fields": ker.get("empty_prose_fields", []),
                "populated_prose_fields": ker.get("populated_prose_fields", []),
                "has_tabulated_evidence": ker.get("has_tabulated_evidence", False),
            }
        )
    rows.sort(key=lambda row: (int(row["ker_id"]) if (row["ker_id"] or "").isdigit() else 0))

    order = order_key_events(roles, edges)
    structure = describe_structure(roles, edges, all_edges)
    assessment = element.find(ns + "overall-assessment")
    weight_text = element_text(assessment, ns, "weight-of-evidence-summary").lower()
    differs = sorted({word for word in NON_STRUCTURED_GRADES if word in weight_text})

    return {
        "aop_id": wiki_id,
        "title": element_text(element, ns, "title"),
        "short_name": element_text(element, ns, "short-name"),
        "oecd_status": element_text(element.find(ns + "status"), ns, "oecd-status"),
        "wiki_license": element_text(element.find(ns + "status"), ns, "wiki-license"),
        "sequence": [
            {
                "ke_id": ke,
                "role": roles.get(ke, "KE"),
                "title": events.get(ke, {}).get("title", ""),
                "level": events.get(ke, {}).get("level", ""),
            }
            for ke in order
        ],
        "structure": structure,
        "relationships": rows,
        "has_weight_of_evidence_summary": bool(weight_text),
        "has_essentiality_summary": bool(
            element_text(assessment, ns, "key-event-essentiality-summary")
        ),
        "assessment_table_vocabulary_differs": differs,
    }


def collect(xml_path: Path, aop_ids: list[str]) -> dict[str, Any]:
    """Collect every requested AOP, in the order given."""
    root, ns = read_export(xml_path)
    events = collect_key_events(root, ns)
    kers = collect_relationships(root, ns)
    ke_by_uuid = {event["uuid"]: ke for ke, event in events.items()}
    ker_by_uuid = {ker["uuid"]: key for key, ker in kers.items()}
    aop_by_uuid = wiki_id_map(root, ns, "aop-reference")

    found: dict[str, dict[str, Any]] = {}
    for element in root.findall(ns + "aop"):
        wiki_id = aop_by_uuid.get(element.get("id"))
        if wiki_id in aop_ids:
            found[wiki_id] = collect_aop(
                element, ns, wiki_id, events, kers, ke_by_uuid, ker_by_uuid
            )
    missing = [aop for aop in aop_ids if aop not in found]
    return {
        "export": xml_path.name,
        "requested_aops": aop_ids,
        "missing_aops": missing,
        "aops": {aop: found[aop] for aop in aop_ids if aop in found},
    }


def as_markdown(result: dict[str, Any]) -> str:
    """Render the collection as Markdown, one section per AOP."""
    lines = [
        "# AOP Key Event sequences and KER evidence",
        "",
        f"Export: `{result['export']}`. "
        f"AOPs requested: {', '.join(result['requested_aops'])}.",
        "",
        "Generated by `scripts/aop_evidence.py`. Regenerate against the same export with:",
        "",
        "```bash",
        f"just aop-evidence {','.join(result['requested_aops'])}",
        "```",
        "",
        "Weight of evidence and quantitative understanding are the export's own "
        "structured values for the pair (AOP, KER). They are not read from prose, "
        "which grades the same relationships differently.",
        "",
    ]
    if result["missing_aops"]:
        lines += [f"**Not found in this export:** {', '.join(result['missing_aops'])}", ""]

    for aop in result["aops"].values():
        lines += [
            f"## AOP {aop['aop_id']}: {aop['title']}",
            "",
            f"OECD status: {aop['oecd_status'] or 'none recorded'}. "
            f"Licence: {aop['wiki_license'] or 'none recorded'}.",
            "",
            "### Key Event sequence",
            "",
            "| Order | Role | Key Event | Title | Level |",
            "|---|---|---|---|---|",
        ]
        for position, event in enumerate(aop["sequence"], start=1):
            lines.append(
                f"| {position} | {event['role']} | KE{event['ke_id']} | "
                f"{event['title']} | {event['level']} |"
            )
        findings = {
            "events_in_no_relationship": "in no relationship at all",
            "initiating_events_without_adjacent_outflow": (
                "a Molecular Initiating Event with no adjacent relationship out of it"
            ),
            "adverse_outcomes_without_adjacent_inflow": (
                "an Adverse Outcome with no adjacent relationship into it"
            ),
            "intermediate_events_without_adjacent_inflow": (
                "an intermediate Key Event with no adjacent relationship into it"
            ),
        }
        reported = [
            (", ".join(f"KE{ke}" for ke in aop["structure"][key]), phrase)
            for key, phrase in findings.items()
            if aop["structure"][key]
        ]
        if reported:
            lines += ["", "**Where the chain does not hold together:**", ""]
            lines += [f"- {events}: {phrase}" for events, phrase in reported]
        lines += [
            "",
            "### Key Event Relationships",
            "",
            "| KER | Edge | Adjacency | Weight of evidence | Quantitative understanding "
            "| Prose blocks filled | Tables |",
            "|---|---|---|---|---|---|---|",
        ]
        for row in aop["relationships"]:
            filled = len(row["populated_prose_fields"])
            total = filled + len(row["empty_prose_fields"])
            lines.append(
                f"| KER{row['ker_id']} | KE{row['upstream_ke']} → KE{row['downstream_ke']} "
                f"| {row['adjacency']} | {row['weight_of_evidence'] or '—'} "
                f"| {row['quantitative_understanding'] or '—'} | {filled}/{total} "
                f"| {'yes' if row['has_tabulated_evidence'] else 'no'} |"
            )
        notes = []
        if not aop["has_weight_of_evidence_summary"]:
            notes.append("no weight-of-evidence summary")
        if not aop["has_essentiality_summary"]:
            notes.append("no Key Event essentiality summary")
        if aop["assessment_table_vocabulary_differs"]:
            notes.append(
                "the overall assessment grades relationships with words outside the "
                "export's vocabulary ("
                + ", ".join(aop["assessment_table_vocabulary_differs"])
                + "), so its table and the structured values disagree"
            )
        if notes:
            lines += ["", "**Caveats:** " + "; ".join(notes) + "."]
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--xml", required=True, type=Path, help="path to the AOP-Wiki XML export"
    )
    parser.add_argument(
        "--aops", required=True, help="comma-separated AOP-Wiki ids, for example 305,307"
    )
    parser.add_argument(
        "--format", choices=("md", "json"), default="md", help="output format (default md)"
    )
    parser.add_argument("--out", type=Path, help="write to this file instead of stdout")
    args = parser.parse_args(argv)

    if not args.xml.is_file():
        parser.error(f"no such export: {args.xml}")
    aop_ids = [part.strip() for part in args.aops.split(",") if part.strip()]
    if not aop_ids:
        parser.error("--aops listed no ids")

    result = collect(args.xml, aop_ids)
    rendered = (
        json.dumps(result, indent=2, sort_keys=True)
        if args.format == "json"
        else as_markdown(result)
    )
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(rendered)
    if result["missing_aops"]:
        print(
            f"warning: not in this export: {', '.join(result['missing_aops'])}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
