# Draft entry for the EnviroMech decision register

Working draft, kept beside the register and left off the site. Written in the
register's format (`explanation/design-decisions.md`) so it can be dropped in once the
decision is picked. The **rationale is settled**; the **decision is not** — five candidate
framings are listed below and one has to be chosen before this is a register entry
rather than a note.

Provenance: surfaced while working dismech issue #10395 (toxicologic phenocopies),
which is where an agent asserted that a toxic phenocopy is an AOP whose adverse
outcome is a genetic disease's phenotype set. Examining that claim produced the
material below. The phenocopy side of the work lives in dismech's
`projects/PHENOCOPIES.md` and is not repeated here.

---

## N. What an adverse outcome is, and is not

**Decision:** *(unpicked — see the options below.)*

**Rationale:**

In the context of an AOP, an adverse outcome is a specialised type of key event,
defined by the criterion under which it was selected, which is informed by the
context the AOP is designed to serve.

The AOP-Wiki Handbook's Table 1 gives that criterion explicitly. An adverse outcome
is

> A specialised type of key event that is generally accepted as being of regulatory
> significance on the basis of correspondence to an established protection goal or
> equivalence to an apical endpoint in an accepted regulatory guideline toxicity
> test.

Two things follow from the wording. The adverse outcome is a **key event**, exactly
parallel to the molecular initiating event, which the same table defines as the
specialised key event that starts the AOP. And it is defined by **acceptance
against a criterion**, not by an intrinsic property of the biology, since the
definition turns on what is "generally accepted as being of regulatory
significance".

The founding literature says the same at the level of biological organisation.
Ankley et al. place the adverse outcome at "a biological level of organization
relevant to risk assessment" ([PMID:20821501](https://pubmed.ncbi.nlm.nih.gov/20821501/));
Villeneuve et al. sharpen it to "a level of biological organization of regulatory
relevance" ([PMID:25466378](https://pubmed.ncbi.nlm.nih.gov/25466378/)).

**The Handbook does not, however, require an AOP's own purpose to be regulatory.**
Its Context subsection under AOP Development Strategy asks developers to record the
"key research question(s) **or** regulatory needs being addressed", and names
documenting "biology based on specialized expertise" among the envisaged uses that
inform an AOP's development.

So the framework permits an AOP developed for a non-regulatory purpose while
defining its terminal node by regulatory significance. An adverse outcome adopted
from an existing AOP therefore arrives carrying a selection criterion that the
adopting project did not apply and does not necessarily share.

**Why this bears on EnviroMech specifically.** Register entry 3 takes the AOP-Wiki
EMOD schema as the base schema, so every pathway EnviroMech records terminates in a
node whose definition carries that criterion. Register entry 1 scopes EnviroMech
from bare exposure–outcome associations through to mature AOPs, which is broader
than the criterion. The two are not in conflict, but the gap between them is
currently unstated.

**Consequences worth recording whichever option is chosen:**

- A single phenotype may well satisfy the Table 1 criterion. Developmental
  malformation and reduced fertility are apical endpoints in guideline studies, so
  phenotypes are not excluded from being adverse outcomes.
- A *set* of phenotypes cannot be one, because a key event is a single measurable
  change in biological or physiological state.
- An adverse outcome is a node, not a pathway. Conflating one with a whole AOP is a
  category error independent of what the node turns out to be.

**Status:** draft; rationale settled, decision open.

---

## The decision options

Not mutually exclusive except for option E, which is the alternative to all of them.
A governs records EnviroMech writes; B governs outcomes it imports; C constrains the
node's shape; D adds metadata and forbids nothing.

| | Decision, as it would be stated | What it constrains | What it rules out |
|---|---|---|---|
| **A** | An adverse outcome is not a disease entry. EnviroMech does not use one as a container for a disease's phenotype set; where a record corresponds to a curated disease, it references that disease rather than absorbing it. | Scope, and the boundary with dismech | Importing a disease's phenotype set as a terminal node |
| **B** | Where an adverse outcome corresponds to a curated disease, the correspondence is recorded as a typed cross-reference, never as an identity. | How an existing AOP-Wiki outcome is reused | Asserting that an outcome and a disease are the same thing |
| **C** | An adverse outcome names a single endpoint at a stated level of biological organisation. A candidate spanning several levels, or several co-occurring features, is split. | The shape of the node itself | A set-valued terminus |
| **D** | Each adverse outcome records the criterion under which it was selected, distinguishing outcomes imported from AOP-Wiki under regulatory relevance from outcomes coined in EnviroMech under some other criterion. | Required metadata | Nothing; it makes the criterion visible rather than forbidding anything |
| **E** | Recorded as open: the framework's adverse outcome carries a regulatory selection criterion that EnviroMech's scope does not share, and how EnviroMech handles that is undecided. | Nothing yet | Nothing |

---

## Supporting findings not part of the entry

Kept here so they are not lost, but they do not belong in a register entry.

- **The equation is not citable.** PubMed returns zero records for `phenocopy AND
  "adverse outcome pathway"`. The nearest relevant work is the EPA's Adverse Outcome
  Pathway Database ([PMID:29454060](https://pubmed.ncbi.nlm.nih.gov/29454060/),
  [PMID:34253739](https://pubmed.ncbi.nlm.nih.gov/34253739/)), which links key-event
  genes to disease associations and variant frequencies. That supports gene-level
  overlap and a susceptibility framing, not an identity between an adverse outcome
  and a disease's phenotype set.
- **"Context of use" is legitimate but borrowed vocabulary.** It comes from the
  method-credibility frameworks (ASME V&V 40, FDA, EMA method qualification) rather
  than from the AOP methodology papers, and PubMed pairs it with "adverse outcome
  pathway" in only a handful of records. It is used centrally in
  [PMID:42382173](https://pubmed.ncbi.nlm.nih.gov/42382173/), which lists defining
  context of use as a first-order roadmap item alongside quantitative key event
  relationships. The AOP literature's own phrase for the same idea is
  "fit for purpose" ([PMID:30908812](https://pubmed.ncbi.nlm.nih.gov/30908812/)),
  and the two are used together rather than as alternatives.
- **Villeneuve's principle 1 is "AOPs are not chemical specific."** Relevant if
  EnviroMech ever records an agent-specific relation inside a pathway rather than at
  the stressor-to-MIE junction, but not needed for this entry.
