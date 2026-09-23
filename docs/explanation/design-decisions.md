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
AI-curated literature sources. It records how exposures to chemicals and other hazards
external to the body relate to adverse effects, represented as phenotypes and diseases,
whatever the strength of the
evidence behind them:

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

**Decision:** EnviroMech has no schema of its own for now. Its base schema is the
AOP-Wiki EMOD schema in [EHS-Data-Standards/linkml-aop](https://github.com/EHS-Data-Standards/linkml-aop),
[`src/linkml_aop/schema/aop_emod_linkml.yaml`](https://github.com/EHS-Data-Standards/linkml-aop/blob/main/src/linkml_aop/schema/aop_emod_linkml.yaml).

**Rationale:** the EMOD schema already models Adverse Outcome Pathways, Key Events,
Assays, Observations, and Evidence, and its stated purpose includes providing a basis for
pathways derived by automated approaches such as text mining. Building on it avoids a
second, diverging model of the same concepts.

**Consequence:** changes to that schema are made in linkml-aop, not here. Its class
definitions and the reasoning behind them are in EHS-Data-Standards/linkml-aop's
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

## Open and deferred decisions

- Which dismech design principles EnviroMech inherits (see entry 2).
- Which dismech schema principles EnviroMech departs from, and why (see entry 2).
- Whether and when EnviroMech gets a schema of its own, extending or importing the
  linkml-aop schema.
- How evidence, confidence, and provenance are represented, building on dismech's
  evidence model (including its SEPIO export) and ongoing Monarch discussions of the same
  questions.
