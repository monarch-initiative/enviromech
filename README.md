# EnviroHealthMech

An environmental health mechanisms repository built from AI-curated literature sources,
recording how exposures to chemicals and other hazards relate to adverse effects
represented as phenotypes and diseases, ranging from associations with no known mechanism
to mature Adverse Outcome Pathways.
It follows the approach of the
[Disorder Mechanisms Knowledge Base (dismech)](https://github.com/monarch-initiative/dismech).

What EnviroHealthMech holds, and how it differs from dismech, is described on the
documentation site's [home page](docs/index.md).

## Status

Early setup. The repository currently holds documentation only; no curated content yet.

## Schema

EnviroHealthMech does not yet have a schema of its own. Its base schema is the AOP-Wiki EMOD
schema from [EHS-Data-Standards/linkml-aop](https://github.com/EHS-Data-Standards/linkml-aop):
[`src/linkml_aop/schema/aop_emod_linkml.yaml`](https://github.com/EHS-Data-Standards/linkml-aop/blob/main/src/linkml_aop/schema/aop_emod_linkml.yaml).
Changes to that schema are made in linkml-aop.

## Repository structure

* [docs/](docs/) - documentation site source (hand-written, tracked)
  * [explanation/design-decisions.md](docs/explanation/design-decisions.md) - why the
    project is built the way it is: scope, relationship to dismech, schema choice, and
    decisions still open
* [mkdocs.yml](mkdocs.yml) - documentation site configuration; every page under `docs/`
  is listed in its nav
* [CLAUDE.md](CLAUDE.md) - instructions for AI agents working in this repository

## Documentation

The documentation site is built with [MkDocs](https://www.mkdocs.org/) and the
[Material](https://squidfunk.github.io/mkdocs-material/) theme. To preview it locally,
with both installed:

```bash
mkdocs serve
```

## Contributing

Before proposing a structural, scope, schema, or evidence change, read
[`docs/explanation/design-decisions.md`](docs/explanation/design-decisions.md). A change
to a recorded decision should update that document in the same change, with the reason.
