# The EnviroMech domain model

This file is the design record for what EnviroMech knows. mechmaker
wrote the skeleton. The `design-mech-schema` skill fills it in, and every
later schema change updates it. Sections marked TODO are not done.

## What a record is

One record is one observation.

TODO: Define an observation in two or three sentences. Say what counts
as one and what does not. Name the nearest things that are *not* records
here, and where they go instead (a field on a record, another Mech, nowhere).

## Identity

Records mint `enviromech:<slug>` identifiers. No ontology keys them.

The filename stem is derived from `name`: lowercase, runs of non-alphanumerics
become one underscore.

TODO: State the granularity rule. When are two candidates one record, and
when are they two? When is a subtype its own record?

## Sections

TODO: For each section of a record, give its purpose, its ontology, and one
worked example. Start from the scaffold below and cut what the domain does
not need.

| Section | Ontology | Purpose |
|---|---|---|
| `biological_processes` | GO under `GO:0008150`, checked with `ols:go` | TODO |
| `cell_types` | CL under `CL:0000000`, checked with `ols:cl` | TODO |
| `anatomical_entities` | UBERON under `UBERON:0001062`, checked with `ols:uberon` | TODO |
| `chemical_entities` | CHEBI under `CHEBI:24431`, checked with `ols:chebi` | TODO |
| `phenotypes` | HP under `HP:0000118`, checked with `ols:hp` | TODO |
| `diseases` | MONDO under `MONDO:0000001`, checked with `ols:mondo` | TODO |
| `organisms` | NCBITaxon under `NCBITaxon:1`, checked with `ols:ncbitaxon` | TODO |
| `evidence` | PMID, DOI | Record-level citations |
| `discussions` | none | Open questions and knowledge gaps (mech_shared) |
| `datasets` | accessions | Public datasets (mech_shared) |

## Sources

TODO: What feeds curation: literature queries, databases, existing
knowledge bases, ontologies. Each source goes in
`curation/source_queue.tsv` with its license.

## Out of scope

TODO: What this Mech will not record, and why.

## Related Mechs

TODO: Mechs whose records this one links to or overlaps with. See
https://monarch-initiative.github.io/mechregistry/.
