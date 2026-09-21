# Updating the linkml-aop schema for new EMOD tables

Work record for bringing [`src/linkml_aop/schema/aop_emod_linkml.yaml`](https://github.com/EHS-Data-Standards/linkml-aop/blob/main/src/linkml_aop/schema/aop_emod_linkml.yaml) in
[EHS-Data-Standards/linkml-aop](https://github.com/EHS-Data-Standards/linkml-aop) up to date
with tables added to `aopwiki_emod_web_app/app/models.py` since the
`inputs/emod_3-26-26_linkml.yml` schemauto snapshot. Started 2026-09-18.

- **linkml-aop branch:** `update-schema-new-emod-tables` (cut from `origin/main`, no upstream set)
- **Status:** steps 1–4 complete; steps 5–6 pending. Nothing committed yet.

## Pipeline

```
EMOD MySQL DB ──schemauto──▶ aop_wiki_emod_linkml.yml ──copy──▶ linkml-aop/inputs/emod_<date>_linkml.yml
                                                                     │
                                          curate_emod_linkml.py ◀────┘
                                                                     │
                                          src/linkml_aop/schema/aop_emod_linkml.yaml
```

schemauto introspects the live database, not `models.py`, so the DB must be migrated to
the current alembic head before generation.

## Step 1 — Bring the EMOD DB to the current schema (done)

In `aopwiki_emod_web_app`:

- Created local `.env` and `frontend/.env` from the `.sample` files with generated,
  local-only MySQL passwords (both files are gitignored).
- Started Docker and brought up only the `mysql` and `api` services; the frontend is not
  needed.
- Ran `docker compose exec api uv run alembic upgrade head` against an **empty** database.
  All 17 migrations applied cleanly, ending at `e426e452227d`.
- `alembic check` reported no drift between `models.py` and the migrated DB. The DB has 81
  tables: the 80 in `models.py` plus `alembic_version`.

**Why an empty DB:** schemauto reads table structure only, so no production data or SQL
dump is needed to generate the schema.

## Step 2 — Generate the base schema (done)

- Created `outputs/linkml_schemas/` (the generation script writes there but the directory
  did not exist; `outputs/` is gitignored).
- Ran `shell_scripts/generate_linkml_schema.sh`, producing
  `outputs/linkml_schemas/aop_wiki_emod_linkml.yml` with 81 classes.

Compared with the March input, 16 tables are new and none were removed. Five of the new
ones (`assignments`, `entity_counts`, `event_stressors`, `oecd_metrics`, `roles`) plus
`alembic_version` were already listed in `WIKI_TABLES_TO_DROP`. The other ten are handled
in step 4.

Column-level changes to tables that existed in March:

| Table | Added | Removed |
|---|---|---|
| `aops` | `has_references`, `has_structured_methods`, `project_129` | |
| `assays` | `classification` | `citation_id` (replaced by the `assay_citations` join table) |
| `citations` | `publisher` | |
| `events` | `aop_oecd_endorsed_count`, `aop_oecd_program_count`, `aop_open_for_adoption_count` | |
| `observations` | `biological_object_str`, `experiment_setup_id` | |
| `relationships` | `has_tabulated_evidence` | |

## Step 3 — Copy into linkml-aop (done)

- Created branch `update-schema-new-emod-tables` from `origin/main` and removed its upstream
  so a push cannot target `main`.
- Copied the generated file to `inputs/emod_9-18-26_linkml.yml` (byte-identical).

**Why the web-app copy matters:** the curation script rewrites its input file in place to
strip dropped tables. The file in `aopwiki_emod_web_app/outputs/` is the untouched original.
All dry runs were done against a scratch copy of the input.

## Step 4 — Update curation constants in `curate_emod_linkml.py` (done)

### Tables dropped (`WIKI_TABLES_TO_DROP`)

Added `aop_batch_imports`, `can_event_merge_groups`, and `can_event_merge_group_members`.

- `can_event_merge_groups` and `aop_batch_imports`: curator decision — not part of the
  data model being published.
- `can_event_merge_group_members`: its only purpose is joining merge groups to events; with
  the groups table dropped it would reference a class that no longer exists.

### `batch_import_id` dropped from every class

Added a `DROPPED_ATTRS_ALL_CLASSES = ["batch_import_id"]` constant, applied in `main()`
alongside the per-class `DROPPED_ATTRS`. Removed the now-unused `batch_import_id` entries
from `CURATED_RANGES`.

**Why:** curator decision. `batch_import_id` is EMOD import bookkeeping (which batch loaded
a row), not a property of the biology or evidence being modelled.

### Join-table classification

| Join table | Bucket | Resulting references |
|---|---|---|
| `experiment_setup_cell_terms` | `PURE_PIVOT_UNIDIRECTIONAL` | `ExperimentSetup.cell_terms → CellTerm` |
| `aop_assays` | `BIDIRECTIONAL_INVERSE` | `Aop.assays` ↔ `Assay.aops` |
| `assay_citations` | `BIDIRECTIONAL_INVERSE` | `Assay.citations` ↔ `Citation.assays` |
| `test_guideline_assays` | `BIDIRECTIONAL_INVERSE` | `TestGuideline.assays` ↔ `Assay.test_guidelines` |
| `test_guideline_events` | `BIDIRECTIONAL_INVERSE` | `TestGuideline.events` ↔ `Event.test_guidelines` |
| `event_target_families` *(moved)* | `BIDIRECTIONAL_INVERSE` | `Event.bio_target_families` ↔ `BioTargetFamily.events` |
| `assay_target_families` *(moved)* | `BIDIRECTIONAL_INVERSE` | `Assay.bio_target_families` ↔ `BioTargetFamily.assays` |
| `citation_biological_target_families` *(moved)* | `BIDIRECTIONAL_INVERSE` | `Citation.bio_target_families` ↔ `BioTargetFamily.citations` |
| `observation_citations` *(moved)* | `BIDIRECTIONAL_INVERSE` | `Observation.citations` ↔ `Citation.observations` |

**Why:** the script keeps a join table as its own class (`SEMANTIC_JOIN_TABLES`) only when
it carries attributes beyond its two foreign keys. Once `batch_import_id` is dropped, all
eight bidirectional tables above hold nothing but their two foreign keys, so they collapse
to direct references. The four marked *moved* were previously in `SEMANTIC_JOIN_TABLES`
solely because of `batch_import_id`. `BIDIRECTIONAL_INVERSE` matches how the existing
`event_assays` and `observation_events` are handled. `experiment_setup_cell_terms` is
unidirectional, following the `assay_taxon_terms` pattern for ontology-term lists.

The remaining `SEMANTIC_JOIN_TABLES` (the `*_life_stages`, `*_sexes`, `*_taxons`,
`aop_stressors`, `aop_events`, `aop_relationships` tables) carry real attributes such as
`confidence_id`, so they stay as classes.

`CURATED_RANGES` blocks for the eight collapsed tables were removed, since those tables no
longer produce classes.

### Foreign-key ranges (`CURATED_RANGES`)

**Why curated ranges are required:** `convert_class_block` strips every `range:` line
schemauto generates unless `CURATED_RANGES` supplies a replacement. An uncurated foreign key
therefore silently becomes a plain string, even though schemauto emitted the correct range.

Added:

| Class | Attribute | Range |
|---|---|---|
| `experiment_setups` | `assay_id` | `assays` |
| `experiment_setups` | `causal_agent_id` | `stressors` |
| `test_guidelines` | `citation_id` | `citations` |
| `observations` | `experiment_setup_id` | `experiment_setups` |
| `observations` | `stressor_id` | `stressors` — curator decision: observations point directly to `Stressor` |

Fixed stale keys that matched no column, so the range was being stripped:

| Class(es) | Was | Now | Why |
|---|---|---|---|
| 11 join tables: `aop_`, `event_`, and `relationship_` × `life_stages` / `sexes` / `taxons`, plus `aop_stressors` and `aop_relationships` | `evidence_id` | `confidence_id` | `models.py`, the initial migration, and the DB all use `confidence_id` (FK to `confidence_levels.id`). The `evidence_id` key dates from the first WIP commit and never matched, so the schema on `main` has `confidence_id` as an untyped string. It now gets `range: ConfidenceLevel`. |
| `evidences` | `reference_id` | `citation_id` | `evidences` has no `reference_id` column; `citation_id` is the FK to `citations`. Curator decision: `Evidence` points to `Citation`. |

### Verification (dry run on a scratch copy)

- 54 classes in the output.
- No duplicate attribute keys; no `range:` pointing at a missing class or enum.
- No `batch_import_id` on any class.
- `gen-python` accepts the schema.
- `linkml-lint` reports warnings only (missing descriptions and enum value naming); no
  errors.
- No example data or tests in `src/data/` or `tests/` reference the removed classes.

### Leftover config that does nothing (not changed)

These predate this work and have no effect on output:

- `CURATED_RANGES["assays"]` keys `reference_id` and `taxon_term_id` — no longer columns on
  `assays` (replaced by `assay_citations` and `assay_taxon_terms`).
- `CURATED_RANGES["statuses"]` — no `statuses` table exists.
- `CLASS_RENAMES` entries for `assay_target_families`, `citation_biological_target_families`,
  and `event_target_families` — those tables no longer become classes.

## Step 5 — Descriptions and enums (in progress)

- Added class-level description support: a `class_definitions` dict (keyed by table name)
  in `aop_definitions_and_enums.py`, written by `curate_emod_linkml.py` as a folded
  `description: >-` on the class. The script previously supported attribute descriptions
  only.
- `TestGuideline` definition adopted. Its rationale and sources are recorded in
  `src/docs/dev/definition_rationale.md`, which is the home for the reasoning
  behind every definition.

Remaining: add descriptions in `src/linkml_aop/curation/aop_definitions_and_enums.py` for
`TestGuideline`, `ExperimentSetup`, and the new attributes listed in step 2. This also
clears most of the new `linkml-lint` "recommended" warnings (229 on `main`, 252 in the
first dry run).

## Step 6 — Regenerate and verify (pending)

```bash
uv run python -m linkml_aop.scripts.curate_emod_linkml inputs/emod_9-18-26_linkml.yml src/linkml_aop/schema/aop_emod_linkml.yaml
just test    # validates src/data/examples/
just site    # regenerates datamodel + docs
```

Review the schema diff before committing. Note that the first command also rewrites
`inputs/emod_9-18-26_linkml.yml` in place (strips dropped tables).

## Documentation gaps found

- The web-app README names the output `aop_wiki_emod_linkml.yml`; linkml-aop inputs use a
  dated name. Neither README mentions the rename.
- The linkml-aop README says to edit `aop_definitions_and_enums.py`, but table drops,
  join-table classification, and FK ranges live in the constants of
  `curate_emod_linkml.py`.
- Neither README says that uncurated foreign keys lose their range.
- `generate_linkml_schema.sh` writes to `outputs/linkml_schemas/`, which it does not create.
