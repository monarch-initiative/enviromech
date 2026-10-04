# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project overview

EnviroMech is an environmental health mechanisms repository built from AI-curated
literature sources, following the approach of
[dismech](https://github.com/monarch-initiative/dismech). See `docs/index.md`.

**Naming:** write the project name as **EnviroMech** in anything a person reads (docs,
prose, titles). Lowercase `enviromech` is only for identifiers: the repository and
directory name, paths, and package names.

## Design decisions

Before making structural, scope, schema, or evidence choices, consult the decision
register at [`docs/explanation/design-decisions.md`](docs/explanation/design-decisions.md).
Cite a recorded decision when it is relevant. If one looks wrong or stale, surface it
rather than silently contradicting it.

In particular: EnviroMech inherits some of dismech's design principles but **not** its schema
principles, so do not carry a dismech schema convention over without checking the
register.

## Schema

EnviroMech's schema is [`src/enviromech/schema/enviromech.yaml`](src/enviromech/schema/enviromech.yaml).
It imports the AOP-Wiki EMOD schema,
[`src/linkml_aop/schema/aop_emod_linkml.yaml`](https://github.com/EHS-Data-Standards/linkml-aop/blob/main/src/linkml_aop/schema/aop_emod_linkml.yaml)
from [EHS-Data-Standards/linkml-aop](https://github.com/EHS-Data-Standards/linkml-aop),
unchanged, and adds only what EnviroMech needs while it is being worked out. The
division of work: a class that earns a place in EMOD moves to linkml-aop; a class
specific to deriving pathways from external knowledge bases stays here. Changes to the
EMOD classes themselves are made in linkml-aop, never by overriding them here.

linkml-aop is a dependency, pinned to a commit in `pyproject.toml`. `just install`
installs it and copies its `aop_emod_linkml.yaml` to
`src/enviromech/schema/aop_emod_linkml.yaml`, where the import finds it. That copy is
not tracked and is never edited; to take a newer linkml-aop, change the commit in
`pyproject.toml` and run `just install` again.

Records are one YAML file each: Key Events under `data/key_events/` (class
`KeyEventRecord`) and Observations under `data/observations/` (class
`ObservationRecord`). A Key Event's file holds its `KeyEventAggregation` section, when
it has one. The commands need [uv](https://docs.astral.sh/uv/) and
[just](https://just.systems/):

```bash
just install              # once, and after changing the linkml-aop pin
just validate             # every record against the schema
just check-ids            # the Observation and Assay ids EnviroMech assigns
just validate-references  # every evidence snippet against its cached source
just qc                   # all three; what a change must pass
```

`just validate-references` checks every evidence snippet word for word against the cited source,
cached under `references_cache/`. Read a source from the cache before quoting it; never
write a snippet from memory. Terms, event components and levels of biological organization carry no `id`:
linkml-aop makes it optional on those classes, and the term itself identifies them.
Never invent one. A Key Event's `id` under `event:` is its AOP-Wiki id.

Observations and Assays keep a required integer `id`, because other EMOD classes refer
to them by it. EnviroMech creates its own Observations and Assays, so it assigns these
ids itself, as positive integers. An Observation's is the number in its record id
(`enviromech:obs-0003` has `observation.id: 3`). An Assay's must be unique among
Assays; when two Observations use the same Assay they give it the same id. These are
EnviroMech's numbers, not database ids. `just check-ids` enforces both rules.

The database ids for levels of biological organization and for biological actions are
kept for reference in `aop_wiki_cli`, in `src/aop_wiki_cli/database_ids.py`.

## Skills

Claude Code skills live in `.claude/skills/`, one directory per skill, each holding a
`SKILL.md` with frontmatter whose `name` matches the directory.

- **screen-aop-key-event**: use before an AOP-Wiki Key Event's structured properties are
  used to look for matching dismech nodes. Runs the offline alignment check in
  `aop_wiki_cli`, escalates to the model review when the Event's level and its own
  description do not line up, and says what each outcome means for the pathway.

## Documentation

- `docs/` is hand-written, tracked source for the documentation site.
- Every page under `docs/` is listed in the `mkdocs.yml` nav.
- `docs/explanation/` holds the reasoning behind the project, starting with the decision
  register.
- `docs/how-to/` holds curation procedures.
- `docs/reports/` holds dated working notes and analyses.
