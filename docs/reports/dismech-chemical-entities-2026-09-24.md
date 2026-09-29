# Chemical annotation in dismech is curated but not rendered

**Date:** 2026-09-24
**For:** sessions working in this repository, and @gingin77
**Checked against:** the dismech checkout at `/Users/ginniehench/Developer/dismech`, `main` at `17609e989b`

dismech holds several hundred ontology-bound chemical annotations. Almost none of them
appear on a rendered dismech page, and none appear in a pathograph. Anyone who goes
looking for dismech's chemical content by browsing the site will conclude it has none.

This matters here because EnviroMech is organized around the exposure, where dismech is
organized around the disease. When EnviroMech draws on dismech for chemical content, that
content has to be read out of the YAML. The pages are not a usable index of it.

## What is curated

`chemical_entities` is declared on exactly two classes in `src/dismech/schema/dismech.yaml`:
`Pathophysiology` and `ExperimentalPerturbation`. Counted across `kb/disorders/` and
`kb/modules/`:

| Holder | Blocks | Files |
|---|---|---|
| `Pathophysiology` | 656 | 337 |
| `ExperimentalPerturbation` | 9 | 2 |

337 of 3,094 disorder entries carry at least one block, about 11% of the corpus. One
module of 178 carries one: `parp_parg_macrodomain_viral_evasion`, a single NAD(+) binding.

## What is rendered

Across both page templates, `chemical_entities` appears once. It is a tag row on a
proposed experiment's perturbation in the disorder template. Nothing renders the slot on a
pathophysiology node card, and the module template does not mention it at all.

The consequence of those two facts together is the sharp part. Of the two classes that can
carry a chemical, the renderer covers the one holding 9 of the 665 blocks. The class
holding the other 656 is not covered anywhere.

The module page compounds it: it builds aggregate summary cards for cell types and
biological processes, with no chemical counterpart, so a module chemical has no home on the
page even outside the graph.

## Why none of it reaches the pathograph

A chemical entity is not a pathograph node type, on a module or a disorder. The string
`chemical_entities` does not occur in `src/dismech/graph.py`. The node-type set is fixed at
pathophysiology, phenotype, environmental, genetic, treatment, biochemical, experimental
model, animal model, computational model, and orphan. A chemical is a descriptor slot
hanging off a pathophysiology node, the same structural status as `cell_types` and
`biological_processes`.

It is weaker than those two even as annotation. The graph builder lifts `cell_types`,
`biological_processes` and `molecular_functions` into each node's hover metadata.
`chemical_entities` is not in that list, so a chemical on a node does not surface in the
pathograph as hover text either.

## What this does not establish

Whether the gap is a deliberate scoping choice or an unfinished renderer is not stated
anywhere in the dismech code or its decision register, and the dismech issue tracker has
not been searched for it. Treat the gap as observed behaviour, not as a recorded decision.
