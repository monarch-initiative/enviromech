---
name: aop-evidence
description: >
  Collect the Key Event sequence and the Key Event Relationship weight of
  evidence of one or more AOPs from the AOP-Wiki XML export, deterministically,
  with a script. Use when asked what Key Events an AOP contains and in what
  order, how strong the evidence behind its KERs is, how complete its records
  are, whether a set of AOPs forms a network, or where an AOP's causal chain is
  broken. Use it before curating a Key Event record or a KeyEventAggregation
  from an AOP, and before quoting any weight-of-evidence rating.
---

# Collect AOP Key Event sequences and KER evidence

Run the script. Do not read these values out of prose by hand, and do not ask a
model to grade an AOP's evidence.

```bash
export AOP_WIKI_XML=/path/to/aop-wiki-xml-YYYY-MM-DD
just aop-evidence 18,51,305,307,344
just aop-evidence 344 --format json --out build/aop-344.json
```

The script is [`scripts/aop_evidence.py`](../../../scripts/aop_evidence.py). It
takes `--xml`, `--aops`, `--format md|json` and `--out`. It exits 1 and names any
requested AOP the export does not contain, so a silently short answer is not
possible.

`aop_wiki_cli` ([gingin77/aop_wiki_cli](https://github.com/gingin77/aop_wiki_cli))
owns the download of the export. Get a snapshot from it, record the snapshot date
next to any number you report, and point `AOP_WIKI_XML` at the file. Never
re-download or re-parse the export with new code here.

## Why a script, and not reading the record

**Weight of evidence is a structured field of the export, and prose disagrees
with it.** On each AOP's own copy of a relationship the export carries
`<evidence>` (High, Moderate, Low, Not Specified), `<adjacency>` and
`<quantitative-understanding-value>`. Those are what EMOD's
`AopToKeRelationship` holds as `confidence_id`, `directness_id` and
`quantitative_understanding_id`.

An AOP's `overall-assessment` also contains a hand-written HTML table grading the
same relationships, and the two sources do not agree. AOP 18 grades two of its
relationships "weak" and "very weak", words that are not in the export's
vocabulary at all, while the structured values for the same two are Moderate and
Low. Reading the table gives a different answer from reading the field, and the
field is the one to carry. The script flags every AOP whose table uses words
outside the vocabulary, in `assessment_table_vocabulary_differs`.

**A rating belongs to the pair (AOP, KER), not to the KER.** KER2124 is High in
AOPs 305 and 344 and Moderate in AOP 307. Never report a KER's weight of
evidence without naming the AOP it was read from.

**The KER-level `weight-of-evidence/value` field is prose, not a grade,** and it
is empty on 2088 of 2381 relationships. An empty `weight_of_evidence` does not
mean unrated; check `<evidence>` on the AOP.

**Three paths in the export are easy to get wrong**, and getting one wrong
returns empty rather than failing:

| What you want | Where it is |
|---|---|
| biological plausibility | `weight-of-evidence/biological-plausibility`, nested |
| empirical support | `weight-of-evidence/emperical-support-linkage`, nested, **misspelled in the export** |
| quantitative understanding prose | `quantitative-understanding/description`, nested |

## Reading the output

**The sequence** runs from the Molecular Initiating Event along the adjacent
relationships, with ties broken by Key Event id so two runs agree. Roles are the
export's own: an AOP may declare more than one Adverse Outcome, and AOP 307
declares no Molecular Initiating Event at all.

**"Where the chain does not hold together"** is the part to read before trusting
a pathway. Four findings:

- an initiating event with no adjacent relationship out of it. In AOP 51 the
  initiating event is in no relationship at all, so that AOP is a set of Key
  Events, not a chain.
- an Adverse Outcome with no adjacent relationship into it, meaning the AOP has
  no step-by-step route to its own outcome. True of AOPs 305, 307 and 344.
- an intermediate Key Event with no adjacent relationship into it.
- an event in no relationship at all.

**"Prose blocks filled"** counts the eleven prose fields a relationship can
carry. A High rating on a relationship with nothing filled in is a curator's
assertion with no written argument behind it, and four of AOP 51's six
relationships are Moderate with zero of eleven filled. Report the rating and the
count together or the rating misleads.

## What the script does not give you

- **Key Event essentiality.** EMOD's `AopToEvent` has `essentiality_id`, but the
  export carries no value for it. The AOP's
  `key-event-essentiality-summary` prose is the only source, and a person has to
  read it. The script reports only whether that summary exists.
- **Any judgement about the biology.** The script reports what AOP-Wiki says. An
  AOP is a hypothesis, and `oecd_status` empty means no OECD review happened, not
  that one failed. Carry that uncertainty forward.
- **The dismech crosswalk.** Matching a Key Event to dismech pathograph nodes is
  separate work; use `screen-aop-key-event` first, then write the
  `KeyEventAggregation`. Only `pathophysiology` nodes are candidates.
- **References.** An AOP, Key Event or KER page is not a citable reference. Cite
  the primary literature in the record's `references`, through
  `evidence-references`.

## Where this should end up

The three per-AOP relationship fields belong in `aop_wiki_cli`'s own AOP
collector, which keeps only adjacency today. When they are there, this script
should shrink to a call. Until then it reads the export directly, and that is the
only reason it parses anything.
