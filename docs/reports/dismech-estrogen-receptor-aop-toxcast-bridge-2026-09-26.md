# The estrogen receptor is the widest AOP-to-dismech join with nothing on the dismech side

**Date:** 2026-09-26
**For:** sessions working in this repository, and @gingin77
**Source:** the dismech checkout at `/Users/ginniehench/Developer/dismech`, `main` at `94591e52d4`, clean tree; the AOP-Wiki XML snapshot `aop-wiki-xml-2026-09-15` at `/Users/ginniehench/Developer/aop_wiki_cli/xml_inputs/`

Twenty-six of the 597 Adverse Outcome Pathways in the current AOP-Wiki snapshot declare an
estrogen-receptor-related molecular initiating event. That is more than the androgen
receptor (16) or the aryl hydrocarbon receptor (23), and comparable to the entire thyroid
axis (25) despite that axis spanning seven distinct target proteins. On the dismech side,
57 disease entries carry a pathophysiology node that invokes estrogen, and **exactly one
node in the whole corpus binds an estrogen receptor gene**.

So this is the widest available exposure-to-mechanism join in the two corpora, and the
receptor that both sides are organized around is absent from the dismech pathograph. That
is the join EnviroMech exists to make, which is why it is recorded here rather than in the
dismech issue about estrogen coverage — mapping AOPs onto dismech entries is this
project's scope, not that issue's.

## Why the estrogen receptor and not another target

Three facts, each independently sourced, and they do not all point the same way.

The **regulatory** case is the strongest. The Food Quality Protection Act of 1996 amended
the Federal Food, Drug, and Cosmetic Act to require EPA to screen for substances that
"may have an effect in humans that is similar to an effect produced by a naturally
occurring estrogen" (21 U.S.C. 346a(p)(1), quoted in 80 FR 35350, 2015-06-19). Androgen
and thyroid screening entered through the advisory committee that designed the program,
not through the statute. OECD maintains three validated guidelines for the receptor —
TG 455 transactivation, TG 493 recombinant receptor binding, TG 440 uterotrophic bioassay
— two of them performance-based.

The **high-throughput** case is why this matters for ToxCast specifically. Judson and
colleagues built the first ToxCast pathway model on the estrogen receptor, integrating 18
in vitro assays (PMID:26272952), and EPA accepted it as an alternative to three EDSP
Tier 1 assays including an in vivo study (PMID:26066997). The androgen receptor model that
followed used 11 assays (PMID:27933809). CERAPP ran on the receptor first
(PMID:26908244); CoMPARA applied the same method to androgen four years later
(PMID:32074470).

The **counter-fact**, which should be stated whenever the other two are: none of the 26
ER-MIE pathways carries WPHA/WNT endorsement. The OECD-endorsed endocrine set is androgen
receptor, aromatase, thyroperoxidase, deiodinase and the sodium-iodide symporter. The
strongest ER pathways sit at *Under Review* (AOP 30, AOP 503) or *Under Development*
(AOP 314, AOP 440), and the two oldest and most-cited ones, AOP 29 and AOP 52, carry no
status at all. "Most studied" and "most formally endorsed" point in opposite directions
here.

## The AOPs that land on existing dismech entries

These are the candidates where an AOP adverse outcome already has a dismech entry, so the
mapping is a join rather than new curation. Statuses are from the snapshot.

| AOP | Title | Status | Candidate dismech entry |
|---:|---|---|---|
| 200 | Estrogen receptor activation leading to breast cancer | none | `ER_Positive_Breast_Cancer`, `Breast_Carcinoma` |
| 503 | Activation of uterine estrogen receptor-alfa leading to endometrial adenocarcinoma, via epigenetic modulation | Under Review | `Endometrial_Carcinoma`, `Endometrial_Endometrioid_Adenocarcinoma` |
| 167 | Early-life estrogen receptor agonism leading to endometrial adenosquamous carcinoma via promotion of sine oculis homeobox 1 progenitor cells | none | `Endometrial_Carcinoma` |
| 639 | Activation, estrogen receptor alpha leads to precocious puberty via increased kisspeptin release | none | `Central_Precocious_Puberty` |
| 637 | Activation, estrogen receptor alpha leads to increased uterine weight via earlier proliferation of cells of the uterine lining | none | `Uterine_Leiomyoma`, `Adenomyosis` |
| 29 | Estrogen receptor agonism leading to reproductive dysfunction | none | reproductive entries generally |
| 30 | Estrogen receptor antagonism leading to reproductive dysfunction | Under Review | reproductive entries generally |
| 440 | Hypothalamus estrogen receptors activity suppression leading to ovarian cancer via ovarian epithelial cell hyperplasia | Under Development | `Ovarian_Endometrioid_Carcinoma` |
| 493 | ERa inactivation alters AT expansion and functions and leads to insulin resistance and metabolically unhealthy obesity | none | metabolic entries |
| 497 | ERa inactivation alters mitochondrial functions and insulin signalling in skeletal muscle and leads to insulin resistance and metabolic syndrome | none | `Sarcopenia`, metabolic entries |
| 314 | Binding to estrogen receptor (ER)-α in immune cells leading to exacerbation of systemic lupus erythematosus (SLE) | Under Development | lupus entries |

The remaining fifteen are ecotoxicological (fish fecundity, sex ratios, renal failure in
oviparous species), GPER-mediated, or cover outcomes dismech does not carry. They are not
a mapping target now.

The eight distinct initiating events behind all 26, with reuse counts:

| Uses | Key event | Title |
|---:|---|---|
| 8 | KE 1065 | Activation, estrogen receptor alpha |
| 7 | KE 111 | Agonism, Estrogen receptor |
| 3 | KE 112 | Antagonism, Estrogen receptor |
| 2 | KE 1046 | Suppression, Estrogen receptor (ER) activity |
| 2 | KE 2029 | protein-coupled estrogen receptor 1 (GPER) activation |
| 2 | KE 2126 | Estrogen receptor alpha inactivation |
| 1 | KE 1710 | Binding to estrogen receptor (ER)-α in immune cells |
| 1 | KE 2141 | Disruption, Estrogen receptor |

KE 1065 and KE 111 are the eighth and tenth most reused initiating events in the whole
wiki. The AOP-Wiki record for KE 111 names OECD TG 455, TG 457 and TG 440 in its own
measurement-methodology field, so the wiki anchors this event to the validated guideline
stack directly.

## What blocks the ToxCast side

dismech issues #12682 and #12858 cover adding ToxCast as a structured reference source and
mapping its assay endpoints onto pathograph nodes. ESR1 is the most heavily assayed target
in the panel, and no dismech pathograph node names it, so the single highest-volume
assay-to-node mapping has no target to land on.

That gap is being tracked on the dismech side as an estrogen signalling project, including
a per-node backfill worklist of fourteen nodes that bind `GO:0030520` while naming no gene.
Nothing here duplicates it. What this note adds is the reason the gap matters beyond
dismech's own completeness: it is simultaneously the widest AOP join and the widest ToxCast
join, and closing it serves both.

A caution carried over from that work. Matching an assay to a node on a shared gene symbol
produces wrong mappings more often than right ones, and the estrogen receptor is the worst
case for it because antagonist and agonist assays share the gene. Several of the fourteen
dismech nodes are *loss*-of-signalling claims (`Heart_Failure`, `Triple_Negative_Breast_Cancer`),
so an agonist hit-call maps to them with the sign reversed.

## Method

AOP counts were derived by parsing `<molecular-initiating-event key-event-id>` out of the
snapshot XML, joining each id to its `<key-event><title>`, and selecting titles matching
`estrogen` case-insensitively; numeric AOP and KE ids were resolved through the
`<vendor-specific>` reference maps. Family comparisons used the same method with
`androgen receptor`, `aryl hydrocarbon|AhR`, `thyroperoxidase|thyroid hormone receptor|sodium.iodide|deiodinase`,
and `PPAR|peroxisome prolifer`. OECD status came from each AOP's `<oecd-status>` element.

A count of this kind depends on where the family boundary is drawn. AOP 616 carries a
composite initiating event spanning ERα, ERβ, AR and CYP19A1 whose title does not contain
the word estrogen, so it is excluded here; including it gives 27 from 9 key events.
Re-derive rather than quoting these figures.

Every PMID was confirmed against PubMed for identifier and exact title on 2026-09-26.
dismech coverage figures come from a census script written against `94591e52d4`; they move
with every curation PR.
