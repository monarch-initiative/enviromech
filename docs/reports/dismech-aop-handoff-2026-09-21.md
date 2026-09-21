# Handoff: dismech AOP work relevant to EnviroHealthMech

**Date:** 2026-09-21
**From:** a Claude Code session working in `monarch-initiative/dismech`
**For:** the next session working in this repository, and @gingin77

This brief lists the AOP work already done in dismech that EnviroHealthMech should build
on rather than repeat. Everything listed was checked on the date above: each path exists,
and each issue's state and assignee were read from GitHub. Local paths assume the dismech
checkout at `/Users/ginniehench/Developer/dismech`.

## The task that prompted this

The goal is a set of **airway inflammation pathways** for EnviroHealthMech. Each one is
built from mechanisms already curated in dismech's disease entries and modules, and
written as instances of the classes in linkml-aop's
[`aop_emod_linkml.yaml`](https://github.com/EHS-Data-Standards/linkml-aop/blob/main/src/linkml_aop/schema/aop_emod_linkml.yaml).

Most of the method already exists in dismech: chain selection, matching nodes to Events,
triaging Key Event Relationship (KER) evidence, and assembling a network from shared
Events. Three things are new:

1. Applying that method to airway entries. None of dismech's airway files has any AOP
   content yet.
2. Writing a derived pathway as EMOD instance YAML that validates against the linkml-aop
   schema. Every derivation so far is a Markdown table.
3. Deciding where that output lives here and how it is maintained. That decision belongs
   in [the decision register](../explanation/design-decisions.md), which should cite the
   dismech alignment page rather than re-derive it.

## Read first

| Item | What it gives you |
|---|---|
| `projects/AOP_EMOD_ALIGNMENT.md` | The framework comparison. The table under "What enables integration now" is the dismech-to-EMOD mapping; do not rebuild it. Also covers weight-of-evidence structure, the toxicokinetic boundary, "an AOP is a publication unit, not a mechanism boundary", and two worked use cases (lead, liver fibrosis NAM) |
| `projects/AOP_EMOD_ALIGNMENT/putative-aops-from-dismech-2026-09-10.md` | Two dismech pathographs worked through into AOP form: `Left_Ventricular_Noncompaction_8` and `Skeletal_Fluorosis`. The closest existing template for what this repository will produce |
| `docs/reports/aop-derivable-measurable-chains-2026-09-10.md` | Which dismech chains can seed AOPs. Its main result is that node readouts are scarce and edge evidence is not. Regenerate with `just aop-chain-census`, run from the dismech checkout |
| `projects/AOP_EMOD_ALIGNMENT/openscientist-lead-aop-network.md` | An OpenScientist report assembling the eight lead AOPs into a network. Its assessment is in `assessments/openscientist-assessment-by-claude-code.yaml`; read the assessment before trusting the report |
| `projects/AOP_EMOD_ALIGNMENT/working-notes-2026-08-12.md` | Working notes behind the alignment page. Detail, not conclusions |
| `projects/TDAR_AOP.md` and `projects/TDAR_AOP/findings-to-actions.md` | A second comparison, of the AOPs ending at impaired T-cell dependent antibody response. The section "Findings that are AOP-only" lists seven findings with no dismech action, which are the ones relevant here |

Network JSON for both comparisons sits in each project's `artifacts/` folder.

## Issues

| Issue | State | What it is |
|---|---|---|
| [#10454](https://github.com/monarch-initiative/dismech/issues/10454) | open, assigned to @gingin77 | Proposes a project collecting use cases where a KER was checked against primary literature. The first use case, KER3445, is written up in full in the issue |
| [#10773](https://github.com/monarch-initiative/dismech/issues/10773) | open, unassigned | An inventory of AOP-Wiki data errors found during curation |
| [#10272](https://github.com/monarch-initiative/dismech/issues/10272) | open, assigned to @gingin77 | The six open schema questions from the alignment page. See the correction below |
| [#10395](https://github.com/monarch-initiative/dismech/issues/10395) | open, assigned to @gingin77 | A proposed "Phenocopy" tab on dismech disease pages. It asks for a dismech feature, but what it records is an exposure-outcome association, which is what EnviroHealthMech holds |

**Stay in dismech:** [#11950](https://github.com/monarch-initiative/dismech/issues/11950),
[#11951](https://github.com/monarch-initiative/dismech/issues/11951) and
[#11907](https://github.com/monarch-initiative/dismech/issues/11907). They curate AOP Key
Events into dismech modules.

**Can probably be closed:** [#10687](https://github.com/monarch-initiative/dismech/issues/10687)
is still open, but PR #10760, which added the "not a mechanism boundary" section it asks
for, merged on 2026-09-05. Closing it is @gingin77's call.

## Skills to port

`aop-wiki`, `ker-evidence-triage` and `mie-ker-capture`, from dismech's
`.claude/skills/`. **Port them from `main`.** The version there came in with PR #10464 and
describes the installable `aop-wiki-cli` with its `--data-dir` option, which is the
current command surface.

When porting, replace the dismech-specific parts:

- **Evidence rule.** The skills say AOP-Wiki is never a dismech reference, because dismech
  has no fetcher for it. EnviroHealthMech has not decided its own evidence rule, so do not
  carry that rule over as a decision.
- **Paths and recipes.** Replace `kb/disorders/`, `references_cache/` and `just` recipes,
  which do not exist here.
- **Data directory.** Keep the warning that `aop-wiki-cli` writes `outputs/`, `xml_inputs/`
  and `logs/` into the current directory when no data directory is set. Point
  `AOP_WIKI_CLI_DATA_DIR` outside this repository too.

## Correction: the schema questions are not split between EMOD and dismech

An earlier note said questions 3–6 in #10272 are about EMOD and questions 1–2 about
dismech. The alignment page frames **all six** as dismech schema questions, each titled
"Should dismech's schema…". Their relevance here differs:

- **Question 3**, declaring the `aop.*` prefixes, is about dismech's prefix map only.
- **Questions 4 and 5**, a population level and species applicability, are gaps EMOD does
  not have. `BiologicalOrganizationEnum` includes `Population`, and Events, KERs and AOPs
  all carry taxon, sex and life-stage links. They matter here only when importing from
  dismech: those values will be missing from dismech-derived content and cannot be
  filled in from it.
- **Question 6**, marking a node as toxicokinetic, bears directly on EnviroHealthMech. The
  EMOD `Event` definition excludes exposure events. Every dismech entry examined so far
  lands its exposures on an absorption or intake node two hops upstream of the first
  molecular Event. An exporter has to decide which nodes to leave out, and nothing in
  dismech marks them.

## Airway starting points in dismech

Surveyed on 2026-09-21. These counts move with every curation PR.

**Ready to derive:**
- **`Deployment-Related_Constrictive_Bronchiolitis`** is the strongest. It has 13 nodes,
  a `biological_scale` on every node, all five `fibrotic_response` anchors, and three
  ECTO-bound exposures linked with `TRIGGERS`.
- **`Primary_Ciliary_Dyskinesia`** has a scale on every node and conforms to
  `ciliopathy_dysfunction`. Its mucociliary arm lines up with AOP-Wiki KE 1908 (cilia
  beat frequency, decreased) and KE 1909 (mucociliary clearance, decreased).
- **The `Cystic_Fibrosis` airway arm** runs from CFTR dysfunction through airway surface
  liquid depletion and mucus plugging to bronchiectasis. It parallels AOPs 424 and 425,
  but only 2 of its 29 nodes have a scale.
- **The `Alpha_1_Antitrypsin_Deficiency` lung arm** has a scale on every node and
  conforms to `emphysema_protease_antiprotease_imbalance`.

**Not ready:** `Asthma` has no scales. `Cough_Variant_Asthma` has no causal edges.
`Bronchiectasis` and `Hypersensitivity_Pneumonitis` have no scales and no module links.

**Gap:** dismech has no module for type 2 airway inflammation, mucus hypersecretion,
mucociliary clearance failure or airway remodeling. Filling these would give the reusable
Events that join airway pathways into a network. That work belongs in dismech, where it
runs under dismech's validation and review agents. EnviroHealthMech would then consume
the checked result.

The 2026-09-03 AOP-Wiki snapshot holds 39 Events with airway or lung terms in their titles.
The related AOPs include 148, 411, 424 and 425.

## Facts about AOPs worth carrying over

Corrections @gingin77 has made in earlier sessions. They are not all written down in the
files above.

- **KERs are not required on both sides of a Key Event.** Some AOPs place Key Events in
  sequence with no KER defined between them.
- **A putative AOP may leave its Molecular Initiating Event unnamed.** A putative AOP can
  name its MIE, but it does not have to: a partial AOP with unknown Key Events is still
  useful. So a derived pathway with no MIE is not blocked. The gap between exposure and
  the first molecular interaction becomes the hypothesis, and candidate MIEs should be
  marked plausible, never asserted as established mechanism.
- **EMOD's status.** EMOD is being adopted by the AOP community, but its details are not
  OECD-endorsed and remain open to change. @gingin77 is first author of the EMOD 3.0
  preprint (arXiv 2605.21645), so her statements about EMOD are primary sources.
- **Terms for the frameworks.** Use the "AOP-Wiki v2.8 data model" and "AOP EMOD". Do not
  coin shorthand labels for either.
