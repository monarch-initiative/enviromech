# EnviroMech design decisions

This is the **decision register** for EnviroMech. It records the deliberate design and
scope choices that shape the project, so that people and AI agents can find *why it is
built this way* in one place instead of re-deriving it.

**How to use this document**

- **Agents:** consult this before making structural, scope, schema, or evidence
  decisions. Cite a recorded decision when it is relevant to a change. Do not silently
  contradict one; if a decision looks wrong or stale, surface it.
- **People:** to change a decision, update this document in the same change that
  enacts it, and say why.
- This document describes decisions. Where a decision is enforced by a file, that file is
  canonical and is linked from the entry.

The structure follows dismech's
[design decisions register](https://github.com/monarch-initiative/dismech/blob/main/docs/explanation/design-decisions.md).

## 1. What EnviroMech is

**Decision:** EnviroMech is a repository of environmental health mechanisms built from
AOPs and AI-curated literature sources from DisMech. It records how exposures to
chemicals and other hazards external to the body relate to adverse outcomes, whatever the
strength of the evidence behind them:

- associations between an exposure and an adverse effect, with no known mechanism;
- hypothesized mechanisms proposed to explain such associations;
- mature Adverse Outcome Pathways, used in chemical safety risk assessment decisions,
  whose mechanisms carry substantial evidential support.

How well supported a record is must be readable from its evidence, confidence, and
provenance, recorded as separate things, and observation, testable Key Events, and
inferred mechanism are kept distinct throughout.

**Rationale:** exposure-outcome knowledge exists at every level of support, and a
regulatory decision and an exploratory hypothesis draw on the same literature. Holding
them together lets a hypothesis be read against established pathways, and lets an
established AOP serve as context for a new association. dismech has shown that
AI-curated mechanism content can be kept auditable when it is validated against a schema
and its evidence against its sources; EnviroMech applies that approach to environmental
health. Its pathways extend principles of the Adverse Outcome Pathway (AOP) framework: a
real-world exposure event is not a Key Event, and the Molecular Initiating Event it would
trigger is rarely observable at the time of exposure, so the structure has to separate
what was observed from what is inferred.

**Status:** adopted.

## 2. Relationship to dismech

**Decision:** EnviroMech inherits some of dismech's design principles, those governing
how content is curated and validated, but not its schema.

**Rationale:** dismech is organized around disease entries. An exposure is recorded as an
`environmental:` factor of a curated disease, and a disease is in scope when it has "a
mechanistic story worth modeling". dismech can record an exposure-disease association
without a mechanism (328 of its 1,194 environmental factors had no mechanism link on
2026-09-21), but only inside a disease entry that already exists, and the association has
no identity of its own. EnviroMech makes the association itself the thing recorded: it can
exist before any curated disease entry or known mechanism, it can be found starting from
the exposure, and hypothesized and established mechanisms attach to it. That difference in
what the knowledge base is organized around is why dismech's schema cannot be reused
as-is.

**Open:** which dismech principles are inherited, and which schema principles EnviroMech
departs from, are not yet recorded individually. Each should get its own entry here, with
its reason, as it is decided.

**Status:** adopted; details open.

## 3. Base schema

**Decision:** EnviroMech's schema, `src/enviromech/schema/enviromech.yaml`, imports the
AOP-Wiki EMOD schema in [EHS-Data-Standards/linkml-aop](https://github.com/EHS-Data-Standards/linkml-aop),
[`src/linkml_aop/schema/aop_emod_linkml.yaml`](https://github.com/EHS-Data-Standards/linkml-aop/blob/main/src/linkml_aop/schema/aop_emod_linkml.yaml),
unchanged, and adds only the classes EnviroMech needs while they are being worked out. A
class that earns a place in EMOD moves to linkml-aop; a class specific to deriving
pathways from external knowledge bases stays here.

**Rationale:** the EMOD schema already models Adverse Outcome Pathways, Key Events,
Assays, Observations, and Evidence, and its stated purpose includes providing a basis for
pathways derived by automated approaches such as text mining. Building on it avoids a
second, diverging model of the same concepts.

**Consequence:** changes to the EMOD classes are made in linkml-aop, never by overriding
them here. Its class definitions and the reasoning behind them are in EHS-Data-Standards/linkml-aop's
[`src/docs/dev/definition_rationale.md`](https://github.com/EHS-Data-Standards/linkml-aop/blob/main/src/docs/dev/definition_rationale.md).

**Status:** adopted.

## 4. `oecd_status` is a curation tag, not an evidence measure

**Decision:** `oecd_status` (from the EMOD schema) is treated as a tag that may be used to
group AOPs for curation. It is not a measure of evidence, confidence, or provenance, and
must not stand in for any of them.

**Rationale:** OECD status is assigned rather than derived. dismech's evidence model
declines authored strength grades for the same reason, preferring strength derived from
typed, source-anchored evidence.

**Status:** adopted.

## 5. AOP records use linkml-aop's own AOP classes

**Decision:** an AOP record holds its Key Events and Key Event Relationships in EMOD's
`Aop.events` (`AopToEvent`) and `Aop.ke_relationships` (`AopToKeRelationship`), naming
each by its AOP-Wiki id, with the Key Event's role in `AopToEvent.type`
(`KeyEventTypeEnum`). EnviroMech has no AOP classes of its own beyond `AopRecord`, which
adds the record's identifier and provenance around the `Aop`. More generally, once an
AOP-framework modelling choice is settled, it is made in linkml-aop first, and EnviroMech
uses it.

**Rationale:** linkml-aop is meant to be the core model for anyone working with AOPs in
the EMOD standard, so a choice made only in EnviroMech would leave other users without
it. Until [linkml-aop#13](https://github.com/EHS-Data-Standards/linkml-aop/pull/13)
(merged 2026-10-31), `Aop.events` held each Event in full, so EnviroMech's first AOP
records used their own classes, naming Key Events by CURIE (`aop.events:1542`) with a
`role`. linkml-aop#13 made those links references by id and gave the role an enum, so the
EnviroMech classes repeated EMOD's with different names, and they were removed.

**Consequence:** a record names Key Events and relationships by bare AOP-Wiki number
(`event_id: 1542`), not by CURIE; the record browser builds the link. Rules the schema
cannot express, such as one Molecular Initiating Event per AOP, stay in EnviroMech's
`scripts/check_aops.py`.

**Status:** adopted 2026-10-31.

## Open and deferred decisions

- Which dismech design principles EnviroMech inherits (see entry 2).
- Which dismech schema principles EnviroMech departs from, and why (see entry 2).
- Which of the classes sketched in `enviromech.yaml` belong in EMOD, and when the
  linkml-aop import is pinned rather than resolved against a sibling checkout (see entry 3).
- How evidence, confidence, and provenance are represented, building on dismech's
  evidence model (including its SEPIO export) and ongoing Monarch discussions of the same
  questions.
- How a record written outside the EMOD database identifies the lookup terms it uses.
  The EMOD schema was generated from the EMOD MySQL database, so every class, including
  `LevelOfBiologicalOrganization`, `BiologicalProcess`, `BiologicalObject` and
  `BiologicalAction`, carries the table's integer primary key as a required identifier.
  A hand-written record has to supply those integers, and has no way to know the ones the
  EMOD database assigned. Settled for EnviroMech's records 2026-10-03: linkml-aop PR #10 makes
  `id` optional on the term lookup and event component classes, and records leave it
  out there. `Observation` and `Assay` keep a required id, because other EMOD classes
  refer to them by it. EnviroMech creates its own Observations and Assays, so it assigns
  those ids itself, as positive integers; they are EnviroMech's numbers, not database
  ids. Revised 2026-10-31 for event components: linkml-aop keeps a required id on
  `EventComponent`, so that one combination of action, object and process can be
  shared by Key Events. EnviroMech assigns it, as for Observations: each combination has
  a record under `data/event_components/` with an id such as `enviromech:ec-0001`, and
  the component's `id` is the number in it. These are EnviroMech's numbers, not EMOD
  database ids, and may coincide with them; other users of linkml-aop who need event
  component ids can follow the same rule.
