# Things to clarify

Open questions about what EnviroMech is, collected so they can be worked through and
their answers recorded in the [decision register](../explanation/design-decisions.md).
Started 2026-09-22. Nothing here is decided.

## 1. What is the core unit of EnviroMech?

The unit is the thing a record *is*: what gets an identifier, what a curator creates, what
evidence ultimately hangs from, and what a user finds when they search. One candidate is a
**pathway**.

The register already says something that bears on this. [Decision 2](../explanation/design-decisions.md#2-relationship-to-dismech)
states that in EnviroMech "the association itself is the thing recorded", and that
mechanisms attach to it. A pathway as the core unit would need to be reconciled with that
entry, or the entry revised.

### Pathway: pros

- **It matches the base schema.** The EMOD schema ([decision 3](../explanation/design-decisions.md#3-base-schema))
  is organized around Adverse Outcome Pathways, so a pathway unit needs the least
  translation.
- **It matches how the risk-assessment community already reads mechanisms.** AOP-Wiki
  users, OECD reviewers and regulators recognize the MIE → Key Events → Adverse Outcome
  shape.
- **It carries the mechanism, not just the association.** A pathway says *how* an
  exposure leads to an outcome, which is what makes hypothesis generation and the choice
  of new approach methods (NAMs) assays possible.
- **Pathways compose.** Shared Key Events link pathways into networks, so separate records
  can be assembled into a larger picture without being merged.
- **It has a known maturity model.** Putative, qualitative and quantitative AOPs already give
  a vocabulary for how developed a pathway is.

### Pathway: cons

- **An association with no known mechanism has no pathway.** Decision 1 puts such
  associations in scope. With a pathway as the unit, they would need a degenerate
  pathway (exposure → outcome, nothing between) or a second kind of record.
- **AOPs are deliberately stressor-agnostic.** An AOP starts at the MIE, and stressors are
  attached as examples. EnviroMech records exposures, and a real exposure event is not a
  Key Event (decision 1), so the exposure would sit outside the unit rather than in it.
- **A pathway is a publication unit, not a mechanism boundary.** Work in dismech found one
  Key Event Relationship routinely appears in many AOPs, and two relationships in the same
  AOP need not belong to the same mechanism (dismech
  [#10687](https://github.com/monarch-initiative/dismech/issues/10687)). Where one pathway
  ends and another begins is an authoring choice, so the unit's boundaries would be
  arbitrary and its content duplicated.
- **Evidence attaches to steps, not to pathways.** Weight of evidence is assessed per KER.
  Any pathway-level confidence has to be derived, and a well-supported pathway can contain
  a weakly supported step.
- **Identity is hard.** It is unclear when two pathways are the same pathway, when an
  edited pathway becomes a new one, or how a pathway is versioned as steps are added.
- **Linear chains understate branching.** Real mechanisms fan in and out; a pathway either
  simplifies that or becomes a network, and a network is a different unit.

### Still to settle

- What does a user search *from*: an exposure, an outcome, a mechanism step?
- What must exist before a record can be created at all?
- What does the chosen unit do with an association that later acquires a mechanism?

## 2. Which knowledge repositories and knowledge bases does EnviroMech need to differentiate itself from?

For each one, the question is: what does it already hold, and what would EnviroMech
add that it does not? The descriptions below come from general knowledge and have not yet
been checked against each source.

### Mechanism and pathway resources

- **AOP-Wiki / AOP-KB** (OECD). The curated AOPs themselves, with Key Events, KERs and
  weight-of-evidence narratives. It is EnviroMech's schema lineage, so the difference
  most needs stating here.
- **AOP-DB** (US EPA). Links AOP-Wiki content to genes, chemicals, diseases, pathways and
  species.
- **Effectopedia**. A platform for building and sharing AOPs, including quantitative ones.
- **dismech**. Mechanisms organized around disease entries, with exposures recorded as
  environmental factors of a disease (decision 2 states the difference).
- **Reactome, WikiPathways, KEGG**. Normal molecular and cellular pathways, not
  exposure-to-adverse-outcome pathways.

### Chemical–gene–disease association resources

- **Comparative Toxicogenomics Database (CTD)**. Curated chemical–gene, chemical–disease
  and gene–disease interactions from the literature, plus inferred chemical–disease links
  and exposure-study data. Probably the closest existing resource to the association layer
  in decision 1.
- **Monarch Initiative knowledge graph**. Integrates associations across many sources using
  Biolink, including some from the resources above.

### Toxicity data and screening resources

- **CompTox Chemicals Dashboard, ToxCast, Tox21** (US EPA and partners). Chemical
  identity plus high-throughput bioactivity data, with no curated mechanism chain from
  exposure to outcome.
- **ToxRefDB** (US EPA). In vivo animal toxicity study results.

### Authoritative hazard assessments

- **IARC Monographs, US EPA IRIS, NTP OHAT**. Expert hazard and risk conclusions for
  specific agents, including the key characteristics of carcinogens framework.
- **HAWC** (Health Assessment Workspace Collaborative). A tool for doing the systematic
  reviews behind such assessments.

### Exposure resources

- **Exposome-Explorer** (IARC). Biomarkers of exposure and their measured concentrations.
- **ECTO**. An ontology of exposures, not a knowledge base, but it sets how exposures are
  named.

### AI and text-mining approaches

- **AOP-helpFinder**. Text mining that links stressors to AOP events from the literature,
  the nearest existing approach to "AI-curated literature sources" for AOP content.

### Still to settle

- Which of these does EnviroMech consume, which does it link to, and which does it
  overlap with?
- For the closest ones (AOP-Wiki, AOP-DB, CTD, dismech, AOP-helpFinder), what one-sentence
  difference would a reviewer accept?
- Are there others this list is missing?
