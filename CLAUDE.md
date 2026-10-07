# CLAUDE.md

Operational guidance for Claude Code and other agents in this repository.
`AGENTS.md` points here.

## What this is

EnviroMech (Environmental Health Mechanisms Knowledge Base) is a Mech: an AI agent-curated,
ontology-grounded, evidence-backed knowledge base. EnviroMech records how exposures to chemicals and other hazards relate to adverse effects, from associations with no known mechanism to mature Adverse Outcome Pathways.

**Naming:** write the project name as **EnviroMech** in anything a person reads (docs,
prose, titles). Lowercase `enviromech` is only for identifiers: the repository and
directory name, paths, and package names.

There are two kinds of record, one YAML file each:

- **Observations**, under `data/observations/`, class `ObservationRecord`. This is the
  record kind the mechmaker tooling is built around: every command covers Observations.
- **Key Events**, under `data/key_events/`, class `KeyEventRecord`. They are checked
  against the schema by `just validate-key-events`, which `just qc` runs, counted by
  `just report`, and shown in the record browser. `just validate`, `just compliance`,
  the term checks and the exports do not cover them yet; how they should be validated
  is issue #4.

Both classes are in `src/enviromech/schema/enviromech.yaml`.

The pattern comes from [DisMech](https://github.com/monarch-initiative/dismech).
The registry of Mechs is [MechRegistry](https://github.com/monarch-initiative/mechregistry).

## Design decisions

Before making structural, scope, schema, or evidence choices, consult the decision
register at [`docs/explanation/design-decisions.md`](docs/explanation/design-decisions.md).
Cite a recorded decision when it is relevant. If one looks wrong or stale, surface it
rather than silently contradicting it. EnviroMech inherits some of dismech's design
principles but **not** its schema principles, so do not carry a dismech schema
convention over without checking the register.

[`docs/mechmaker.md`](docs/mechmaker.md) records how the mechmaker template was adopted
here, what was changed from it, and the questions still open.

Read before changing domain content:

- `docs/DOMAIN.md`: what a record is, what it is not, identity, granularity.
- `docs/CURATION.md`: evidence rules, the curation loop, review.
- `curation/source_queue.tsv`: the sources that feed curation, ranked.

## Commands

```bash
just                   # list every recipe
just install           # uv sync, then copy the EMOD schema out of the pinned linkml-aop
just qc                # the offline gate CI blocks on
just qc-full           # qc plus terms and quotes for every record (network)
just validate FILE     # closed schema, ontology terms, verbatim quotes (an Observation)
just validate-key-events   # closed schema, every Key Event record
just check-ids         # the Observation and Assay ids EnviroMech assigns
just new-record ...    # scaffold a record (dry-run unless --apply)
just import-schema SRC --record-class C   # start the schema from an existing one (dry-run unless --apply)
just new-history ...   # scaffold a history record (dry-run unless --apply)
just add-evidence FILE --at PLACE --ref REF --snippet "..."   # checked evidence (dry-run unless --apply)
just convert scripts/convert_X.py --limit 5   # convert an existing knowledge base (dry-run unless --apply)
just fetch-reference PMID:NNN   # fetch and cache a source; read it before quoting it
just fill-titles [FILE...]      # fill missing reference_title from the cache (dry-run unless --apply)
just search-term PREFIX "text"  # search an ontology through its configured adapter, e.g. GO
just term-ancestors CURIE       # where a term sits; use when an enum root rejects it
just term-parents CURIE         # direct is-a parents
just check-identity [FILE...]   # record ids follow the identity enum's rule (network, in qc-full)
just report            # corpus statistics
just compliance        # completeness per record, lowest first
just export            # every format in conf/export.yaml, into build/export/, each read back
just load TARGET       # fill a database in conf/load.yaml (MongoDB, Neo4j); --replace to overwrite
just labels            # create the GitHub labels the workflows use
just docs-serve        # the documentation site at http://127.0.0.1:8000
just site-check        # check conf/site.yaml: colors, theme, contrast
```

Quote counts from `just report` or a live command, never from prose.

## The schema and EMOD

`enviromech.yaml` imports the AOP-Wiki EMOD schema,
[`aop_emod_linkml.yaml`](https://github.com/EHS-Data-Standards/linkml-aop/blob/main/src/linkml_aop/schema/aop_emod_linkml.yaml)
from [EHS-Data-Standards/linkml-aop](https://github.com/EHS-Data-Standards/linkml-aop),
unchanged, and adds what EnviroMech needs around it. A class that earns a place in EMOD
moves to linkml-aop; changes to the EMOD classes are made there, never by overriding
them here.

linkml-aop is a dependency, pinned to a commit in `pyproject.toml`. `just install`
copies its `aop_emod_linkml.yaml` to `src/enviromech/schema/`, where the import finds
it. That copy is not tracked and is never edited; to take a newer linkml-aop, change
the commit in `pyproject.toml` and run `just install` again.

A record holds an EMOD `Event` or `Observation` under `event:` or `observation:`, with
EnviroMech's own fields around it.

**Ids.** Terms, event components and levels of biological organization carry no `id`:
linkml-aop makes it optional on those classes, and the term itself identifies them.
Never invent one. A Key Event's `id` under `event:` is its AOP-Wiki id. Observations
and Assays keep a required integer `id`, because other EMOD classes refer to them by
it. EnviroMech creates its own Observations and Assays, so it assigns these ids itself,
as positive integers: an Observation's is the number in its record id
(`enviromech:obs-0003` has `observation.id: 3`), and an Assay's is unique among Assays,
shared when two Observations use the same Assay. `just check-ids` enforces both. The
AOP-Wiki database ids for levels of biological organization and for biological actions
are kept for reference in `aop_wiki_cli`, in `src/aop_wiki_cli/database_ids.py`.

**Exports.** `conf/export.yaml` lists YAML and JSON only. The RDF and SQL formats
cannot write inlined EMOD objects yet; the tests for them are marked as expected
failures in `tests/test_export.py`.

## Rules that matter most

- **Never guess a CURIE.** Look it up with `just search-term` and
  `just term-info`. An unverified ontology term, PMID or accession is worse
  than none. Leave `term` unset, keep `preferred_term`, and open a
  `CURATION_TODO` discussion.
- **A label is the ontology's label.** `term.label` must match the ontology
  exactly. Put nuance in `preferred_term`, never in `label`.
- **A snippet is a verbatim quote.** Fetch the source with
  `just fetch-reference`, copy the text, and add it with `just add-evidence`,
  which checks the quote before writing. Paraphrase goes in `explanation`.
  `just validate-references` fails a paraphrase, and it should.
- **Bind the most specific accurate term.** If only a broad term fits, bind
  it and say so in `notes`. Do not bind a narrow term because it exists.
- **Declare every prefix.** Each CURIE prefix a record uses has its full
  URI in the schema's `prefixes`. The RDF exports depend on it, and
  `just export` fails on a prefix with no URI.
- **Closed schema.** An unknown field is an error. If the schema lacks a
  place for something real, use the `extend-schema` skill. Do not stuff it
  into `notes`.
- **An agent takes a record no further than `PROPOSED`.** It starts `DRAFT`
  and becomes `PROPOSED` when complete and valid. Promotion to `REVIEWED`
  is a human decision, recorded as a human `REVIEW` event.
- **Record what you did.** Every change appends a `curation_history` event
  to the record, and every session adds a history record with
  `just new-history ... --apply`. Fill `--details`.

## Files not to edit here

- `src/enviromech/schema/mech_shared.yaml` and
  `src/enviromech/schema/history.yaml` are vendored byte-identical from
  the Mech fleet canon. A test checks their hashes. Change them upstream.
- `pages/` is generated by `just render`, for a local look, and not
  committed. Edit `src/enviromech/templates/` instead. A Mech made
  from an older template may still track it: `git rm -r --cached pages`.
- `docs/elements/`, `docs/schema/`, `docs/records/`, `docs/structure.md`,
  `docs/corpus.md` and `.mkdocs.site.yml` are generated by `just docs-build`
  and not committed. Colors and layout settings live in `conf/site.yaml`. Improve a schema
  page by improving the schema's descriptions.
- `cache/` and `references_cache/` are written by the validators. Commit
  them. Never hand-edit a row.
- `.copier-answers.yml` is written by Copier. Run `just update-template` to
  pull template changes from mechmaker.

## Skills

Project skills live in `.claude/skills/`. Use them.

| Skill | Use it to |
|---|---|
| `curate-record` | create or improve one record end to end |
| `ontology-terms` | choose, bind, check or repair a term |
| `evidence-references` | find a source, quote it, validate the quote |
| `review-record` | audit one record without editing it |
| `extend-schema` | change the data model and migrate records |
| `source-queue` | triage the sources that feed curation |
| `github-workflows` | turn on, configure, adapt or debug the GitHub workflows |
| `site-design` | change how the documentation site and record browser look |
| `screen-aop-key-event` | screen an AOP-Wiki Key Event's level before its properties are used |


## Documentation

Every page under `docs/` is listed in the `mkdocs.yml` nav. `docs/explanation/` holds
the reasoning behind the project, starting with the decision register; `docs/how-to/`
holds curation procedures; `docs/reports/` holds dated working notes and analyses.

## Workflows

`docs/WORKFLOWS.md` lists every GitHub workflow, on or off. Turn workflows on or off through Copier, never by copying
files; see the `github-workflows` skill.

## Git

Branch before the first edit. One pull request per coherent change. The pull
request is the human review gate. Do not merge without approval.
