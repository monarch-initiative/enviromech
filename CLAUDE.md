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

The import resolves against a sibling `linkml-aop` checkout. That is a placeholder for a
pinned dependency, not a design choice; the schema file says so at the top.

Validate the example records with `just validate-examples`.

## Skills

Claude Code skills live in `.claude/skills/`, one directory per skill, each holding a
`SKILL.md` with frontmatter whose `name` matches the directory.

- **screen-aop-key-event**: use before an AOP-Wiki Key Event's structured properties are
  used to look for matching dismech nodes. Runs the offline alignment check in
  `aop_wiki_cli`, escalates to the model review when the Event's level and its own
  description do not line up, and says what each outcome means for the pathway.

## Scripts

Scripts live in `scripts/` and run through the `justfile`. They execute under the sibling
dismech checkout's environment (`uv run --project ../dismech`), the same placeholder
arrangement the schema uses for its linkml-aop import; `DISMECH_ROOT` points elsewhere.
Searching dismech's disorders and nodes on EnviroMech's behalf belongs here, not in
dismech.

- `just resolve-source-node "<entry>:<section>#<name>"` resolves a dismech node reference
  and emits the `SourceNode` block for it, with the node's GO/CL/UBERON descriptors
  re-typed as EMOD term objects. It copies every bound term; prune to what the Event is
  about and write `notes` by hand. Genes are reported, not copied, because EMOD has no
  gene object source.
- `just check-source-nodes <file>...` checks every `source_nodes[]` entry of a
  `KeyEventAggregation` record against dismech: the reference resolves, `source_entry`,
  `node_name` and `source_level` agree with it, and no term is on the record that dismech
  does not bind to that node. Terms the record omits are listed, not failed.
- `just validate-examples` validates `src/data/examples/` against the schema.

## Documentation

- `docs/` is hand-written, tracked source for the documentation site.
- Every page under `docs/` is listed in the `mkdocs.yml` nav.
- `docs/explanation/` holds the reasoning behind the project, starting with the decision
  register.
- `docs/how-to/` holds curation procedures.
- `docs/reports/` holds dated working notes and analyses.
