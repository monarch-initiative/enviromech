# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project overview

EnviroHealthMech is an environmental health mechanisms repository built from AI-curated
literature sources, following the approach of
[dismech](https://github.com/monarch-initiative/dismech). See `docs/index.md`.

**Naming:** write the project name as **EnviroHealthMech** in anything a person reads (docs,
prose, titles). Lowercase `ehmech` is only for identifiers: the repository and
directory name, paths, and package names.

## Design decisions

Before making structural, scope, schema, or evidence choices, consult the decision
register at [`docs/explanation/design-decisions.md`](docs/explanation/design-decisions.md).
Cite a recorded decision when it is relevant. If one looks wrong or stale, surface it
rather than silently contradicting it.

In particular: EnviroHealthMech inherits some of dismech's design principles but **not** its schema
principles, so do not carry a dismech schema convention over without checking the
register.

## Schema

EnviroHealthMech has no schema of its own. Its base schema is
[`src/linkml_aop/schema/aop_emod_linkml.yaml`](https://github.com/EHS-Data-Standards/linkml-aop/blob/main/src/linkml_aop/schema/aop_emod_linkml.yaml)
in [EHS-Data-Standards/linkml-aop](https://github.com/EHS-Data-Standards/linkml-aop). Schema changes belong in linkml-aop.

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
