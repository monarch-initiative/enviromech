# Adopting mechmaker: schema clashes and questions

Working notes for the `mechmaker` branch, started 2026-10-03. The goal is to bring
elements of [mechmaker](https://github.com/monarch-initiative/mechmaker) (validation
gates, evidence and history model, term checks, exports, skills, workflows) into
EnviroMech while keeping [decision 3](explanation/design-decisions.md#3-base-schema):
the EMOD schema is imported unchanged.

Each clash below says what was observed, proposes ways to resolve it, and ends with a
question for review. Answers belong in the
[decision register](explanation/design-decisions.md) once made.

## The template is integrated (2026-10-03)

The mechmaker template has been run onto this repository and merged with what was
here. `just qc` passes 10 gates and `just qc-full` 13, on macOS. The sections below
this one are the earlier investigation; where they disagree with this section, this
section is current.

**What the template added.** The Python package under `src/enviromech/` (validation,
evidence, terms, history, reports, exports, the record browser, the docs build), the
vendored `mech_shared.yaml` and `history.yaml`, `tests/`, `conf/`, `cache/`,
`history/`, `curation/`, `registry/`, the curation skills under `.claude/skills/`,
the `.github/` workflows (QC, the weekly sweep, the docs site, the comment guard),
`AGENTS.md`, `CONTRIBUTING.md`, `LICENSE-data.md` (CC BY 4.0), and `docs/DOMAIN.md`,
`docs/CURATION.md` and `docs/WORKFLOWS.md`.

**What was merged by hand.** Nine files existed on both sides.

| File | Result |
|---|---|
| `README.md`, `docs/index.md`, `LICENSE` | EnviroMech's kept |
| `src/enviromech/schema/enviromech.yaml` | The template's schema, with the EMOD import, EnviroMech's fields on `ObservationRecord`, and the Key Event, Causal Agent and aggregation classes added. The template's `Term`, `EvidenceItem` and status enums replace EnviroMech's copies |
| `CLAUDE.md` | The template's, with EnviroMech's sections on the decision register, EMOD, ids and documentation added |
| `justfile` | The template's, plus `emod-schema`, `validate-key-events` and `check-ids` |
| `pyproject.toml` | The template's, plus the pinned linkml-aop dependency |
| `mkdocs.yml`, `.gitignore` | The template's, plus EnviroMech's pages and ignore rules |

**What changed in the records.** Each Observation has a short `name`, with its sentence
moved to `description`, a `creation_date` and a `curation_history`. The files are named
after the name, as the template requires. `evidence` is required: an Observation with no source is not
recorded.

**Where EnviroMech differs from the template.**

- **Two record kinds.** The tooling covers Observations. Key Events are validated
  against the schema by `just validate-key-events`, added to `just qc`, counted by
  `just report`, and given pages in the record browser, which lists both kinds; these
  are changes to EnviroMech's copy of `report.py`, `render.py`, `docs.py` and the
  browser's front-page template. The rest is
  [issue #4](https://github.com/monarch-initiative/enviromech/issues/4).
- **Exports are YAML and JSON only.** RDF fails on EMOD's integer identifiers and the
  SQL-based formats do not find the tables they expect for EMOD's nested classes.
  Three tests in `tests/test_export.py` are marked as expected failures for this.
- **`just qc` has two extra gates:** Key Event schema validation and the Observation
  and Assay id check. It lacks the template's "site is current" gate, because
  `pages/` is not committed here; the docs build renders the browser from the records.
- **`just install`** also copies the EMOD schema out of the installed linkml-aop.

**Two mechmaker bugs were fixed on the way,** on the `docs-pages-by-kind` branch of
mechmaker, not yet pushed. Both stopped a Mech passing its own checks on macOS: schema
pages whose names differ only by case overwrote each other, and two recipes used a
bash 4 option that macOS's bash 3.2 lacks. `.copier-answers.yml` records the local
commit `0.1.1-5-gf1ffe9a`; `just update-template` will not work until that branch is on
GitHub.

**The earlier questions.** Q1, Q2 and Q6 are moot: the plain import works and the
importer that objected is not used. Q5 and Q8 are settled by what was built. Q4 and Q7
are answered by limiting the exports. Still open:

- **Q3.** EMOD's term fields (`source_id`, `term`) and the `Term` objects on
  `causal_agent` and `phenotype_term` are not checked against any ontology. The
  template's descriptor slots (`chemical_entities`, `phenotypes`, `diseases` and the
  rest) are checked, and are on the record but unused.
- **Q9 to Q11.** The proposals for linkml-aop and the role of SOMA.
- `docs/DOMAIN.md` and `docs/CURATION.md` are the template's starting text and need
  writing for EnviroMech.

## How the clashes were found

A scratch Mech was generated from mechmaker at `0.1.1-4-g83c34c9` with EnviroMech's
names: record class `ExposureOutcomeAssociation` (an assumption, see Q8), ontologies
GO, CHEBI, HP, MONDO, CL, UBERON and NCBITaxon, and no pathograph classes. The EMOD schema was
`aop_emod_linkml.yaml` from linkml-aop `main`, fetched 2026-10-03 (SHA-256 beginning
`d3c188f12073`). Three things were run:

1. mechmaker's own importer, `just import-schema`, in both modes.
2. A plain LinkML import: the EMOD file placed beside the Mech schema and added to
   `imports`, then `just qc`.
3. A test record that inlines one EMOD `Event` (KE 1908, copied from
   `src/data/examples/`), taken through validation, export and rendering.

| Check | Result |
|---|---|
| `import-schema --mode reference` | Refused: "the source defines names the Mech's checks depend on: label, term" |
| `import-schema` copy mode, dry run | Accepted with no renames: 42 classes, 3 slots, 10 enums copied |
| Plain LinkML import, schema load | Works: 59 classes, 209 slots, each `term`, `label`, `id` resolves per class |
| JSON Schema, lint, Python tests | Pass (lint gives 142 warnings, all EMOD attributes without descriptions) |
| Schema validation of the test record | Passes |
| Term validation of the test record | Passes, but checks nothing in the EMOD part (Q3) |
| RDF export (JSON-LD, Turtle) | Fails: `Unknown CURIE prefix: @base` (Q4) |
| SQL and CSV export | Fails: `gen-sqltables made no table 'Event_event_components'` (Q7) |
| Record browser, compliance, report | Run |
| Docs build | Fails on macOS, with or without EMOD (Q5) |

Not tested: the reference (quote) validator against a record with EMOD content, KGX
export, any agent workflow, and EnviroMech's own `KeyEventAggregation` classes inside
a Mech schema. By name alone those classes do not collide with anything mechmaker
defines.

## Clashes and questions

### Q1. `term`: eleven EMOD classes and the Mech's term slot

**Observed.** EMOD defines `term` as an attribute of `BiologicalAction`,
`BiologicalObject`, `BiologicalProcess`, `LevelOfBiologicalOrganization`, `CellTerm`,
`ConfidenceLevel`, `Directness`, `LifeStageTerm`, `OrganTerm`, `SexTerm` and
`TaxonTerm`. In a Mech, `term` is a top-level slot whose value is a `Term` object
(`id` CURIE plus `label`), and the term validator and several scripts read it.
mechmaker's importer refuses reference mode for this reason. LinkML itself has no
problem: an attribute is scoped to its class, and after a plain import
`BiologicalObject.term` is still a string and `Descriptor.term` is still a `Term`.

**Options.**

- **A. Change nothing in EMOD; import by hand.** Add the EMOD file to `imports`
  as EnviroMech does today, and skip `import-schema`. Works now.
- **B. Relax mechmaker's importer** so a name that the source defines only as a class
  attribute is not treated as a clash. A change in mechmaker, not in EMOD; it would make
  reference mode usable for EMOD and for any other schema generated from a database.
- **C. Rename in linkml-aop**, for example `term` to `term_label`. The names mirror
  EMOD database columns, so the rename has to live in `curate_emod_linkml.py` and be
  reapplied at each regeneration, and it changes every existing EMOD record.

**Recommended:** A now, B as a mechmaker issue. C buys nothing that A and B do not.

**Question:** is a rename in linkml-aop wanted for its own sake (Q3 gives a reason it
might be), or is A plus B enough?

### Q2. `label` on `License`

**Observed.** One EMOD attribute, `License.label`. Same mechanism as Q1: blocked by the
importer, harmless in LinkML.

**Options.** As Q1. If anything is renamed upstream, `License.label` to
`license_label` is the smallest change of all; EnviroMech has no use for `License`
records yet.

**Question:** treat with Q1 (no rename), or rename this one upstream since it is cheap?

### Q3. EMOD lookup terms are not checked against any ontology

**Observed.** This is the real difference behind Q1. A Mech binds a term as
`{id: GO:0003341, label: cilium movement}` under a dynamic enum, and
linkml-term-validator checks the id exists, sits under the right root and carries that
label. EMOD writes the same fact as
`{id: 1, source: GO, source_id: GO:0003341, term: cilium movement}`, where
`source_id` and `term` are plain strings. In the test record, `source_id` was changed
to the nonexistent `HP:9999999` with the label "Made up label": `just validate`
passed with "Total checks: 0".

**Options.**

- **A. A check in EnviroMech.** A small script walks every EMOD lookup object in a
  record and checks `source_id` and `term` against the ontology named by `source`,
  using the Mech's cache and `conf/oak_config.yaml`. EMOD stays unchanged.
- **B. Bindings in linkml-aop.** Give `source_id` the range `uriorcurie` and add
  dynamic-enum bindings per lookup class (GO, HP, CL, UBERON, NCBITaxon and so on), so
  linkml-term-validator checks EMOD records anywhere, not only here.
- **C. Wrap, do not inline.** EnviroMech records never inline EMOD lookup objects; they
  use Mech descriptors, and a conversion writes EMOD objects when exporting to EMOD.
  This moves away from "imports EMOD unchanged and adds only what is needed".

**Recommended:** A first, since it needs no upstream change and gives the check
immediately; propose B to linkml-aop, since a made-up CURIE is a problem for every
EMOD user.

**Question:** which of A, B, C? And for B, is linkml-aop open to bindings on its
lookup classes?

### Q4. `id`: integer identifiers on all 43 EMOD classes

**Observed.** Every EMOD class has `id` as an integer identifier, the database primary
key. A Mech record's `id` is a CURIE. The two coexist in the schema, but the RDF
export of the test record fails: an integer cannot be made into an IRI
(`Unknown CURIE prefix: @base`). The register already lists the other half of this
problem as open: a hand-written record cannot know the integers EMOD assigned, so the
two examples in `src/data/examples/` invent some.

**Options.**

- **A. CURIE identifiers in linkml-aop.** `id` becomes `uriorcurie` with a declared
  prefix per kind (Bioregistry lists AOP-Wiki prefixes such as `aop.events`; check
  them before adopting), and the database key moves to a separate, optional integer
  attribute. This also fixes the open decision, for the classes that have AOP-Wiki ids.
  Lookup tables (`BiologicalProcess` and the like) have no public id; their identity
  would be the ontology CURIE now in `source_id`.
- **B. Leave EMOD; reference, do not inline.** EnviroMech names an Event by a CURIE in
  its own slot and stops inlining EMOD objects. Loses the computable comparison
  `KeyEventAggregation` was built for.
- **C. Leave EMOD; drop RDF exports** (`jsonld`, `ttl`) from EnviroMech until A lands.
  JSON and YAML still export.

**Recommended:** C now, A as the upstream proposal. SOMA already does A: its
`KeyEvent.id` is a `uriorcurie` and the AOP-Wiki id is a separate `aopwiki_id` string
(see below).

**Question:** is changing `id` in linkml-aop on the table? If not, B or C?

### Q5. `Evidence` (EMOD class) and `evidence` (Mech slot): two evidence models

**Observed.** No LinkML clash: one is a class, the other a slot. They are two
different models. EMOD's `Evidence` links an upstream and a downstream `Observation`
to a `Citation` for a Key Event Relationship. A Mech's `evidence` slot holds
`EvidenceItem` objects: a reference, an exact quoted snippet, the direction of support
and the kind of study, with the quote checked against the fetched source. How
EnviroMech represents evidence is an open decision in the register.

A side effect: the generated schema pages `Evidence.md` and `evidence.md` differ only
by case, so one overwrites the other on macOS. The docs build already fails on macOS
without EMOD, because mechmaker's own `Term` class and `term` slot collide the same
way. It should pass on Linux, where CI runs; that was not tested.

**Options.**

- **A. Both, with separate jobs.** `EvidenceItem` for every claim EnviroMech curates
  (quote-checked). EMOD `Evidence` only for content carried over from AOP-Wiki, as the
  source recorded it.
- **B. Add quoted evidence to EMOD.** Propose an `EvidenceItem`-shaped class and an
  `evidence` slot on `Event` and `KeRelationship` in linkml-aop. SOMA does this on its
  own `KeyEvent` and `KeyEventRelationship`.
- **C. EMOD `Evidence` only.** No quote checking; gives up mechmaker's main gate.

**Recommended:** A, recorded as a register entry; B as a later upstream proposal once
A has been used on real records.

**Question:** A, B or C? Separately: the macOS docs failure is a mechmaker bug; should
it be filed there?

### Q6. `name`, `description`, `notes`

**Observed.** EMOD defines `name` on 3 classes, `description` on 9 and `notes` on 1,
all as attributes. mechmaker does not protect these; it calls them core names and
expects sharing. After a plain import each stays scoped to its class and nothing
failed. The only difference is the URI: the Mech's `name` is `schema:name`, EMOD's
`Stressor.name` is `http://example.org/aopwiki-emod/name`.

**Options.** No change needed for validation. For RDF, see Q9.

**Question:** agreed that these need no action beyond Q9?

### Q7. SQL and CSV exports fail

**Observed.** With RDF formats removed, `just export` still fails:
`gen-sqltables made no table 'Event_event_components'; the layout is not as expected`.
The cause was not established. It may be how mechmaker's export expects multivalued
inlined slots to appear as join tables, set against EMOD classes that already carry
their own foreign keys (`EventComponent.event_id`).

**Options.**

- **A.** Export YAML and JSON only for now.
- **B.** Investigate and fix in mechmaker's `export.py`.

**Question:** does EnviroMech need SQL, SQLite or CSV exports early? If not, A, and B
waits.

### Q8. What the records are

**Answered 2026-10-03.** mechmaker's template generates tooling for one record class,
but the pattern allows several kinds, each in its own directory, as dismech has.
EnviroMech will have six entities. Against EMOD as it stands:

| Entity | EMOD today | Gap |
|---|---|---|
| Key Event, of three types: MIE, AO, intermediate KE | `Event`. The type is not on the Event; it is `AopToEvent.type`, a free string, so one Event can be an MIE in one AOP and a KE in another | No enum for the type (Q8a) |
| AOP: a chain of Key Events, with branches and loops, constrained to one MIE and one AO per level of biological organization | `Aop`, with `AopToEvent` and `AopToKeRelationship` | The constraint cannot be written in LinkML; it needs a check script (Q8b) |
| Key Event Relationship | `KeRelationship` | `biological_plausibility` and `empirical_support` are free-text strings |
| Observation: evidence for claims supporting a Key Event | `Observation`, linked to Events, Citations, an Assay and a Stressor | No quoted snippet (Q5) |
| Concordance evidence for a KER, typed temporal, dose or incidence | `Evidence`: an upstream and a downstream `Observation`, a `Citation` and the KER. The right shape under a general name | No type; no quoted snippet |
| Biological plausibility for a KER | Only the free-text `KeRelationship.biological_plausibility` | No class at all |

**Layout, agreed 2026-10-03.** Four kinds of file:

- **Observations.** One file each, since an Observation can exist before any Key Event
  (an exposure-outcome association with no known mechanism). It names its Causal Agent
  inline and links to the Key Events it supports, if any.
- **Key Events.** Each file includes its `KeyEventAggregation` section. It does not
  list its Observations (see Q13).
- **Key Event Relationships.** Each file holds its concordance evidence and biological
  plausibility. A concordance evidence item names its upstream and downstream
  Observations by id.
- **AOPs.** Each file names its Key Events, with their roles, and its KERs by id.

Each evidence-layer object carries mechmaker `EvidenceItem` quotes, which is where the
quote check attaches. No kind has to exist before another. AOP-Wiki already holds many Key Events, and
people map out putative AOPs from observations they have in mind before the
observation details are documented. So a Key Event or an AOP may have no Observations
yet, and that is a state to report, not an error. Key Event and Observation
examples are developed in tandem: Key Events seeded from the AOP-Wiki XML export
through `aop_wiki_cli`, Observations curated from the literature, so the link between
the two is tested from the start.

**Sub-questions, answered 2026-10-03.**

- **Q8a. MIE, AO or KE is a role within an AOP,** as in EMOD and AOP-Wiki, not a
  property of the Event. One Key Event record can be an MIE in one AOP and an
  intermediate KE in another. The role is stored on the AOP's link to the Event.
- **Q8b. An AOP has at most one AO at each level of biological organization.** It
  may have one AO at the individual level and one at the population level, but not two
  at the population level. The MIE needs no per-level rule: a Molecular Initiating Event is at the
  molecular level by definition, and an AOP has one. Both rules need a check script:
  one MIE per AOP, at the molecular level; at most one AO per level.
- **Q8c. The new classes start in EnviroMech.** Typed concordance evidence (temporal,
  dose, incidence) and biological plausibility are defined in `enviromech.yaml`, tried
  on real records, and proposed to linkml-aop once settled, as decision 3 says.
- **Q8d. Exposure-outcome associations are Observations.** An association with no
  known mechanism is recorded as an Observation that is not yet linked to a Key Event.
  No seventh entity.
- **Q8d. The stressor is called a Causal Agent.** It can be a drug treatment, a
  chemical in the environment, or a biological entity applied in an experiment. EMOD
  already uses the name on `ExperimentSetup.causal_agent_id`, whose range is
  `Stressor`. A Causal Agent has no file of its own: an Observation names it inline.
  A list of every Causal Agent used in Observation records is kept. Proposed: the list
  is generated from the records, not maintained by hand, so it cannot drift from them.
- **Q8d. `KeyEventAggregation` goes inside the Key Event's file,** as the section
  saying where the Event came from and why the lumping is sound.

### Q9. EMOD's namespace is a placeholder

**Observed.** The EMOD schema's `id` is `http://example.org/aopwiki-emod`, and no
class or slot declares a URI or a mapping. Every EMOD element therefore exports under
`example.org`.

**Options.** Propose a stable namespace in linkml-aop (a w3id.org path), and later
`class_uri` or `exact_mappings` for the main classes. No EnviroMech change.

**Question:** raise this in linkml-aop now, together with Q4, or leave it until RDF
exports matter?

### Q10. Lint warnings

**Observed.** 142 lint warnings, all "does not have recommended slot 'description'" on
EMOD attributes. The Mech's lint ignores warnings, so nothing fails.

**Options.** Descriptions added upstream over time, drawing on linkml-aop's
`definition_rationale.md`; or nothing.

**Question:** worth an upstream issue, or ignore?

## First records: AOP 587 (2026-10-03)

Draft Key Event and Observation records for AOP 587, *Inhibition of the mitochondrial
complex III of nigro-striatal neurons leads to parkinsonian motor deficits*, written
before the mechmaker tooling is in place. All are `DRAFT`; none has been reviewed.

**Schema.** `enviromech.yaml` imports the EMOD schema from linkml-aop, which is a
dependency pinned to a commit in `pyproject.toml`. `just install` copies the schema out
of the installed package to where the import finds it. It was first a sibling checkout,
then for a few hours a vendored copy; neither is used now. The pin is the head of
linkml-aop PR #10, which makes `id` optional on the term lookup and event component
classes, and should move to `main` once that PR is merged. It adds
`KeyEventRecord`, `KeyEventScreening`, `ObservationRecord`, `CausalAgent`, `Term` and
`EvidenceItem`. `Term` and `EvidenceItem` have the same shape as mechmaker's, so
adopting mechmaker later replaces them without changing records.

**Key Events** (`data/key_events/`), read from the 2026-10-03 AOP-Wiki XML export with
`aop_wiki_cli`. Each file carries the Event's structured properties plus its description
(`definition`) and how it is measured (`measured_or_detected`), with the HTML removed;
tables in the source become running text. AOP-Wiki's "All rights reserved" licence is
scoped to an AOP's own document record, not to Key Events or Key Event Relationships.
`KE-1908.yaml` and `KE-1909.yaml` are the two earlier `KeyEventAggregation` examples,
rewritten as Key Event files with an `aggregation` section.

| File | Event | Level | Role in AOP 587 | Found on the way |
|---|---|---|---|---|
| `KE-1542.yaml` | Inhibition, Mitochondrial complex III | Molecular | MIE | Its object term GO:0005750 is obsolete, replaced by GO:0045275 |
| `KE-177.yaml` | Increase, Mitochondrial dysfunction | Cellular | KE | No biological process; title says "Increase", action is "functional change" |
| `KE-890.yaml` | Degeneration of dopaminergic neurons of the nigrostriatal pathway | Organ | KE | No cell term; organ term is corpus striatum |
| `KE-896.yaml` | Parkinsonian motor deficits | Individual | AO | Object is a MeSH disease heading; no process |

The role is shown here for reference. It is not in the files: it belongs to the AOP's
record, which does not exist yet.

**Observations** (`data/observations/`). Every snippet passes
linkml-reference-validator against the cached source.

| File | Observation | Bears on | Source |
|---|---|---|---|
| `OBS-0001.yaml` | Trifluralin exposure is associated with Parkinson disease | KE 896 | PMID:37193692 |
| `OBS-0002.yaml` | Levodopa reduces the motor symptoms of Parkinson disease | KE 896 | PMID:41317111, PMID:25981231 |
| `OBS-0003.yaml` | Trifluralin is directly toxic to iPSC-derived dopaminergic neurons | KE 890 | PMID:37193692 |
| `OBS-0004.yaml` | Trifluralin causes mitochondrial dysfunction in those neurons | KE 177 | PMID:37193692 |

**Questions these records raise.**

- **Q12. Placeholder ids. Answered 2026-10-03, then superseded the same day:** negative
  integers were used at first. linkml-aop PR #10 then made `id` optional on the term
  and event component classes, and records leave it out there. Observations and Assays
  keep a required id; EnviroMech assigns those itself, as positive integers.
- **Q13. One direction for the link. Answered 2026-10-03:** the link is written on the
  Observation only, in EMOD's own `Observation.events`. The list of Observations for a
  Key Event is generated, so the two cannot disagree. This replaces the earlier layout,
  in which a Key Event also named its Observations.
- **Q14. `KeyEventAggregation` inside the Key Event file. Answered 2026-10-03:** done.
  The class lost its own `id` and `event_id` and is now the `aggregation` section of a
  `KeyEventRecord`.
- **Q15. Sources for OBS-0002. Answered 2026-10-03:** keep both meta-analyses. The
  graphic does not name its systematic reviews; these two were found by a PubMed
  search.
- **Q16. OBS-0001's quote is partial. Answered 2026-10-03:** keep it as a partial
  draft. Since then the reason has gone: linkml-reference-validator 0.3.0 caches the
  paper's full text from PMC, and the sentence naming trifluralin now passes the check.
  It is added as a second evidence item; the abstract quote stays, marked PARTIAL.
- **OBS-0004. Answered 2026-10-03:** keep it, although it is not in the graphic. It is
  the only Observation so far that bears on KE 177.
- **Q17. The pathway fit.** None of these Observations tests complex III inhibition.
  They support the later Key Events, which AOP 587 shares with AOP 3 and others, not
  the step that makes AOP 587 distinct.

Not done: the level screen in the `screen-aop-key-event` skill. Its command,
`event-content-internal-alignment`, is on an unmerged branch of `aop_wiki_cli`, so each
Key Event is marked `NOT_SCREENED`.

## Proposed changes to EMOD, in one place

All of these are proposals for linkml-aop, none is needed to start, and none is made
here (decision 3).

| # | Change | Fixes | Cost |
|---|---|---|---|
| 1 | `id` as `uriorcurie` with declared prefixes; database key kept as a separate integer | Q4, and the register's open decision on lookup ids | Changes every EMOD record; needs the curation script |
| 2 | `source_id` as `uriorcurie` with dynamic-enum bindings per lookup class | Q3 | Additive |
| 3 | A stable schema namespace in place of `example.org` | Q9 | One line, but changes every URI |
| 4 | A quoted-snippet `EvidenceItem` and `evidence` slot on `Event` and `KeRelationship` | Q5 | Additive |
| 5 | Rename `term` and `label` attributes | Q1, Q2 only if mechmaker's importer is not relaxed | Changes every record; least value |

One change belongs in mechmaker instead: do not treat source attributes as clashes in
reference mode (Q1), and fix the case-only page collision in the docs build (Q5).

## The SOMA schema, for comparison

[somamech](https://github.com/EHS-Data-Standards/somamech) (read at `d8f40d9`,
2026-10-02) keeps no schema of its own. It depends on the `soma-schema` package from
[EHS-Data-Standards/soma](https://github.com/EHS-Data-Standards/soma) (read at
`v0.2.4`). It was not generated by mechmaker: it is a `linkml-project-copier` project
onto which the dismech pattern was ported by hand (its `docs/PORT_PLAN.md`).

| | EMOD (linkml-aop) | SOMA (`aop_framework.yaml`) | mechmaker Mech |
|---|---|---|---|
| Origin | Generated from the EMOD MySQL database | Hand-written | Template |
| Identifier | Integer primary key | `uriorcurie`, plus `aopwiki_id` as a string | CURIE |
| Key Event terms | Lookup objects: integer id, `source`, `source_id`, `term` | `biological_process`, `occurs_in_cell_type`, `occurs_in_anatomy` as bare CURIEs; `biological_object` a string | `Term` object, `id` plus `label`, bound to a dynamic enum |
| Evidence | `Evidence` linking observations to a `Citation` | `EvidenceItem` with `reference`, `snippet`, `supports`, `evidence_source`, `explanation`, checked by linkml-reference-validator | The same `EvidenceItem` shape |
| Root | None | `Container`, one file per publication | One record class, one file per record |
| AOP coverage | 43 classes: AOPs, Events, KERs, assays, observations, stressors, harmonization | 6 classes: `KeyEvent`, `MolecularInitiatingEvent`, `KeyEventRelationship`, `AdverseOutcome`, `AdverseOutcomePathway`, `NamedThing` | Optional pathograph nodes and edges |

What this shows:

- **SOMA has already made two of the changes proposed for EMOD:** CURIE identifiers
  with the AOP-Wiki id alongside (proposal 1), and quote-checked evidence on Key Events
  and Key Event Relationships (proposal 4). They are a working precedent in the same
  organization as linkml-aop.
- **SOMA would clash with mechmaker more directly than EMOD does.** It defines
  `EvidenceItem`, `EvidenceSourceEnum`, `EvidenceSupportEnum` and the slots `evidence`,
  `reference`, `reference_title`, `snippet`, `supports`, `evidence_source` and
  `explanation` as top-level elements with the same names as mechmaker's. These are true
  duplicate definitions, not class-scoped attributes. This was found by comparing names;
  the import was not run.
- **SOMA's `EvidenceSupportEnum` means something else.** In SOMA it is an OECD-style
  strength grade (`strong`, `moderate`, `weak`); in a Mech it is the direction of
  support. Decision 4 declines authored strength grades, so the SOMA enum should not be
  carried into EnviroMech under either name.
- **The two `BiologicalActionEnum`s differ.** EMOD's values include `occurrence`,
  `functional change` and `abnormal`; SOMA's include `impaired`, `activated` and
  `inhibited`. A mapping would be needed before records move between them.

**Question (Q11):** what role should SOMA play for EnviroMech: a precedent to cite
when proposing changes to linkml-aop, a second source knowledge base alongside
dismech (its `kb/publications/` records carry Key Events with quoted evidence), or a
schema to align with directly? The last would reopen decision 3.

## Suggested order once the questions are answered

1. Q8, since it names everything.
2. Q1 option A, Q4 option C, Q7 option A: enough to bring in the mechmaker tooling
   shell with a pinned, vendored EMOD file and a passing `just qc` on Linux.
3. Q5 and Q3: the evidence and term gates.
4. The upstream proposals to linkml-aop and the two mechmaker fixes, as separate
   issues.
