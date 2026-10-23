# AOP 8 evaluation (OpenScientist, 2026-10-23)

**Date:** 2026-10-23
**From:** an OpenScientist autonomous run, job `3e130f60-ab89-4321-92d1-409be1844239`,
commissioned from a Claude Code session working in `monarch-initiative/dismech`
**For:** whoever adopts AOP 8, and [#13](https://github.com/monarch-initiative/enviromech/issues/13)

## Read this first

Everything below the rule is the provider's report, committed verbatim so the branch does
not depend on the provider keeping the job. It is **AI-generated and not reviewed by a
person.** Two things were established by checking its citations against the sources, and
both qualify how it should be read.

**The Baze 2025 quote in Finding 9 is altered.** It closes its parenthesis after
`545 pmol/10^6 cells` where the source continues `over control, respectively)`.
Substantively accurate, but it is not a verbatim quote and must not be copied into a
record snippet as written.

**The report's framing of human relevance is weaker than it sounds.** It presents Baze
2025 as supplying "the species-concordance axis that AOP human relevance requires."
That study's human result is flatly negative — "None of the compounds, at any tested
concentration, affected these parameters in PHH." The CAR/PXR effect on T4 clearance was
rat-only. Read alongside Sauer 2020 and Crofton & Zoeller's own rating of medium
confidence in interspecies concordance, the human arm of the upstream half is not merely
unquantified but unsupported. That is why AOP 8 is recorded here as a hypothesis rather
than as dismech disease mechanism.

Otherwise the citations hold: all six upstream PMIDs resolve, every title matches its
claim, and the quoted sentences verify as exact substrings for Craft 2002, Martin 2012,
Judzinska 2026 and Sauer 2020. Those six are cached in `references_cache/` on this
branch. Papers the report cites for the terminal branch are **not** cached.

One note on provenance for the missing-KE recommendation (carrier-mediated TH uptake,
MCT8/OATP1C1), since it is the run's own contribution rather than something read off
AOP-Wiki: the run's transcripts show it proposed at the end of iteration 1 from the
model's prior knowledge, before any search, with the supporting literature gathered in
iteration 3 by a PubMed query written to find it. The two papers do support the claim,
but it was a confirmed prior rather than a finding that emerged from the literature.

The per-iteration transcripts and the run's figure are not committed; they are
recoverable from the provider by job id while that job remains available.

---

# AOP #8 Evaluation: Thyroid Hormone Catabolism via Hepatic Nuclear Receptor Activation and Adverse Neurodevelopmental (Auditory) Outcomes

## Summary

Adverse Outcome Pathway (AOP) #8 describes a mode of action in which chemicals that activate hepatic xenobiotic nuclear receptors (AhR, CAR, PXR) upregulate Phase II thyroid hormone (TH) catabolism, producing developmental hypothyroxinemia that disrupts a critical window of cochlear development and ultimately causes permanent hearing loss. This evaluation — built on the original Crofton & Zoeller 2005 mode-of-action review ([PMID: 16417043](https://pubmed.ncbi.nlm.nih.gov/16417043/)) and 20 subsequent primary and review papers — assessed which Key Events (KEs) are measurable, which Key Event Relationships (KERs) are quantitatively supported versus plausibility-grade, where KEs can be lumped for simplicity, and what measurable events are missing.

The headline conclusion is that **nearly every node of AOP 8 is measurable with an established assay**; the deficiency is not an absence of methods but the AOP's failure to (a) list the discrete cochlear measurement endpoints it already subsumes under a generic "cochlear damage" KE, and (b) include a mechanistically pivotal, measurable TH tissue-uptake step (MCT8/OATP1C1 transport at brain barriers). The KERs are quantitatively strongest in the upstream-to-middle portion of the pathway and weakest — resting on biological plausibility plus causal essentiality/rescue rather than fitted dose-response — at the auditory terminus that actually defines AOP 8.

Specifically, the CAR/PXR activation → hepatic TH clearance → ↓serum T4 branch now has quantitative in vitro (New Approach Methodology, NAM) support including a measurable rat-versus-human species difference (Baze et al. 2025), and the ↓serum-T4 → ↓brain-TH link is quantitatively characterized — though the latter data were generated in a sibling TPO-inhibition AOP and converge with AOP 8 only at the shared ↓serum-T4 node. The terminal brain-TH → cochlear damage → hearing loss branch is supported by strong biological plausibility, genetic necessity (TRβ knockouts), and stressor-reversal (T4 replacement attenuates PCB-induced hearing loss), but only ordinal — not fitted response-response — dose relationships. Recommended simplifications include lumping the UGT/SULT catabolism and MRP2/OATP efflux steps into one "hepatic TH clearance" KE, collapsing the three HPT-axis feedback nodes into a single ↑TSH modulating factor, and bundling the rodent-specific thyroid-pathology chain — while explicitly resisting the lumping of ↓serum vs ↓tissue TH (which transport and local deiodination can decouple) and of cochlear damage vs hearing loss (structural KE vs functional adverse outcome).

---

## Direct Answers to the Four Research Questions

**Q1 — Which KEs have methods of measurement?** Essentially all of them. Roughly 7 KEs have established, validated assays (the MIE, hepatic catabolism, hepatic efflux, serum T4/T3, brain/tissue TH, hearing-loss AO, and HPT feedback/TSH). One KE (altered cochlear development) is measurable but under-specified in the AOP, and one pivotal measurable step (MCT8/OATP1C1 TH uptake) is missing entirely. See the KE-by-KE inventory table below.

**Q2 — Which KERs have the strongest evidence; how quantitative?** The upstream-to-middle KERs are quantitative and dose-resolved (↑hepatic clearance → ↓serum T4 → ↓brain TH). The terminal branch (brain TH → cochlear damage → hearing loss) rests on biological plausibility plus genetic essentiality and rescue, with only ordinal dose-response — not fitted response-response modeling.

**Q3 — Which KEs can be lumped?** The UGT/SULT catabolism and MRP2/OATP efflux steps can merge into one "hepatic TH clearance" KE; the three HPT-feedback receptor nodes can collapse into one ↑TSH modulating factor; and the rodent thyroid-pathology chain can be bundled. Resist lumping ↓serum vs ↓tissue TH, and cochlear damage vs hearing loss.

**Q4 — What measurable events are missing?** Carrier-mediated TH uptake (MCT8/OATP1C1) at brain barriers, local deiodinase (Dio2/Dio3) activity, discrete cochlear maturation markers (Prestin, KCNQ4, Kir4.1/KCNJ10, otoferlin, endocochlear potential), and a genetic-susceptibility modulating factor.

---

## Key Findings

### Finding 1 — The upstream hepatic KERs are quantitative and dose-resolved

The segment of AOP 8 running from nuclear-receptor activation through increased Phase II catabolism to decreased serum T4 is the best-quantified portion of the entire pathway. Craft et al. 2002 ([PMID: 12151633](https://pubmed.ncbi.nlm.nih.gov/12151633/)) dosed PCB126 across 0.03–300 µg/kg/day and observed dose-dependent hepatic T4-glucuronidation induction — **13-fold in rats** — with parallel UGT1A Western-blot confirmation, and up to 50% serum T4 reduction; PCB153 reduced T4 by up to 80%. The verified quote establishes the quantitative linkage directly: *"T(4) glucuronidation was increased approximately 2- to 3-fold in both rats and mice treated with PCB153. PCB126 increased T(4) glucuronidation 13-fold in rats but only marginally (20%) in mice at the highest doses. Western blot analysis confirmed the PCB126-induced changes in expression of UGT1A in rats."*

Martin et al. 2012 ([PMID: 22187485](https://pubmed.ncbi.nlm.nih.gov/22187485/)) complemented this with transport-level quantitation: *"Aroclor-1254, PCB-118, TCDD, and PCB-126 (TCDD-type congener) increased biliary excretion of T(4)-glucuronide by 850, 756, 710, and 573%, respectively, corresponding to marked induction of hepatic UDP-glucuronosyltransferase (UGT) activity toward T(4)."* Together these provide congener- and dose-resolved KER support with numeric effect sizes, confirming both the measurability and the quantitation of the hepatic catabolism node.

### Finding 2 — The downstream KER rests on plausibility and genetic necessity, and "cochlear damage" hides measurable molecular events

The terminal relationship (↓tissue TH → cochlear damage → hearing loss) is supported not by chemical dose-response modeling but by genetic causal (necessity) evidence and biological plausibility. Global TRβ (*Thrb*) deletion causes severe early-onset deafness (Ng 2015, [PMID: 26241124](https://pubmed.ncbi.nlm.nih.gov/26241124/); Dettling 2014, [PMID: 24012852](https://pubmed.ncbi.nlm.nih.gov/24012852/)). Local cochlear TH control is itself measurable: type 2 deiodinase amplifies T3 while type 3 deiodinase protects development — *"the serum supply of thyroid hormone is augmented within the cochlea itself by type 2 deiodinase, which amplifies the level of T(3), the active form of thyroid hormone, before the onset of hearing"* (Ng 2009, [PMID: 19095741](https://pubmed.ncbi.nlm.nih.gov/19095741/)).

TH regulates specific, measurable outer-hair-cell ion-channel and motor genes: *"TH enhances the expression of the motor protein prestin via liganded TH receptor beta (TRbeta) while in contrast the expression of the potassium channel KCNQ4 is repressed by unliganded TRalpha1"* (Winter 2007, [PMID: 17520268](https://pubmed.ncbi.nlm.nih.gov/17520268/)). The critical developmental window is also sharply defined: *"T3 given only at P0 or P1 resulted in deafness in adult mice, thus revealing a transient period of susceptibility to long-term damage in the neonatal auditory system"* (Peeters 2015, [PMID: 25737207](https://pubmed.ncbi.nlm.nih.gov/25737207/)). The causal chemical link closing the loop is the T4-replacement rescue of Aroclor-1254-induced hearing loss (Goldey & Crofton 1998, [PMID: 9848116](https://pubmed.ncbi.nlm.nih.gov/9848116/)). The key implication: the single lumped "cochlear damage" KE conceals several discrete, individually measurable molecular events.

### Finding 3 — A measurable, pivotal step is missing: carrier-mediated TH uptake (MCT8/OATP1C1)

AOP 8 omits the transporter step that sits between the ↓serum-TH and ↓tissue-TH KEs and can decouple them. *"Studies in the recently generated mct8-deficient zebrafish and Mct8/Oatp1c1 double knockout mice have put forward the current paradigm of impaired TH uptake at the level of the blood-brain barrier during peri- and postnatal development as being the main pathophysiological mechanism"* (Vancamp & Darras 2018, [PMID: 29183795](https://pubmed.ncbi.nlm.nih.gov/29183795/)). In humans, MCT8 loss causes Allan–Herndon–Dudley Syndrome with severe psychomotor deficits. Critically, this machinery is directly measurable: *"In situ hybridisation revealed expression of the TH transporters monocarboxylate transporter 8 (MCT8) and 10 (MCT10), organic anion transporting polypeptide 1C1 (OATP1C1) and L-type amino acid transporter 1 (LAT1) and the inactivating type 3 deiodinase (D3) in the choroid plexus"* (Van Herck 2015, [PMID: 25745816](https://pubmed.ncbi.nlm.nih.gov/25745816/)). Because transport plus local Dio2/Dio3 activity can dissociate serum T4 from tissue T3, the AOP's ↓serum → ↓tissue-TH KER is a biomarker-based surrogate rather than a tight quantitative identity.

### Finding 4 — MIE assays are well-established, but the human-relevant quantitative boundaries are undefined

A systematic review of AOP-anchored (Q)SAR/NAM models identified **178 predictive models**, dominated by the measurable MIE endpoints — *"The distribution of models across endpoints reveals that the most dominant endpoints are PXR (72), TTR (45), and TPO (21)"* (Judzinska et al. 2026, [PMID: 41915611](https://pubmed.ncbi.nlm.nih.gov/41915611/)). Standardized assays therefore exist for nuclear-receptor activation (PXR/CAR/AhR reporter assays), serum-binding displacement (TTR), and TH synthesis (TPO inhibition). However, a key relevance gap persists: *"None of the human studies established a link between substance-mediated liver enzyme induction and increased serum thyroid hormone clearance, let alone further to child neurodevelopment"* (Sauer et al. 2020, [PMID: 33305658](https://pubmed.ncbi.nlm.nih.gov/33305658/)). This directly echoes Crofton & Zoeller 2005's identified data gaps on human fetal UGT inducibility and interspecies UGT-induction sensitivity.

### Finding 5 — Several KEs can be lumped; two apparent simplifications should be resisted

Structural analysis of the AOP 8 graphic against KE definitions and supporting literature yields defensible lumps and important cautions. **Defensible lumps:** (1) "↑Phase II catabolism (UGT/SULT)" + "↑Hepatic transport (MRP2/OATP biliary efflux)" → a single KE, "Increased hepatic clearance/elimination of thyroid hormone," because they are mechanistically coupled and measured together as biliary T4-glucuronide excretion — *"increased biliary excretion of T(4)-glucuronide by 850, 756, 710, and 573%, respectively, corresponding to marked induction of hepatic UDP-glucuronosyltransferase (UGT) activity"* (Martin 2012, [PMID: 22187485](https://pubmed.ncbi.nlm.nih.gov/22187485/)). (2) The three HPT-feedback receptor nodes (pituitary TRH-R, thyroidal TSH-R, hypothalamic TR) are not routinely measured and act as one compensatory loop → collapse into a single modulating factor, "HPT-axis compensatory feedback (↑TSH)." (3) The rodent-specific chain (↑TSH → thyroid hyperplasia → histopathology/weight) is a parallel, non-neurological branch → bundle as one rodent-specific outcome node. **Lumps to resist:** "↓serum T4/T3" and "↓tissue [TH]" must remain separate because MCT8/OATP1C1 transport and local Dio2/Dio3 can decouple them (Finding 3); and "cochlear damage" vs "hearing loss" must remain separate as KE vs adverse outcome (structural vs functional).

### Finding 6 — KER quantitation is strongest in the middle; the AOP-8-specific terminus is essentiality-grade

The serum-T4 → brain-TH KER is the most quantitatively characterized node. O'Shaughnessy et al. 2018 ([PMID: 30085217](https://pubmed.ncbi.nlm.nih.gov/30085217/)) ran a PTU dose-response (0.1–10 ppm), measuring T4/T3 in serum and brain at GD20 and PN14, concluding *"these results show that serum T4 is a good predictor of brain THs."* Hassan et al. 2017 ([PMID: 28973696](https://pubmed.ncbi.nlm.nih.gov/28973696/)) built an explicit quantitative AOP: *"The present study developed a quantitative adverse outcome pathway where serum thyroxin (T4) reduction following inhibition of thyroperoxidase in the thyroid gland are described and related to deficits in fetal brain TH and the development of a brain malformation, cortical heterotopia."*

**Critical caveat:** this qAOP uses a *TPO-inhibition* MIE, not AOP 8's nuclear-receptor/hepatic-catabolism MIE — so these quantitative KERs are imported from a sibling thyroid-AOP branch and converge with AOP 8 only at the shared ↓serum-T4 node. The AOP-8-specific terminus is supported by essentiality/rescue and ordinal dose-response, not fitted modeling: Goldey & Crofton 1998 showed developmental Aroclor 1254 (8 mg/kg) — *"Circulating T4 concentrations were dramatically depleted in the PCB-S group relative to CO-S"* ([PMID: 9848116](https://pubmed.ncbi.nlm.nih.gov/9848116/)) — with T4 replacement attenuating the hearing loss; and Poon/Schantz 2011 ([PMID: 21873374](https://pubmed.ncbi.nlm.nih.gov/21873374/)) showed *"DPOAE amplitudes were decreased and thresholds were elevated in the 6 mg/kg PCB group"* but not at 3 mg/kg — i.e., ordinal dose-response without a fitted curve tying brain-TH quantitatively to threshold shift.

### Finding 7 — The lumped "cochlear damage" KE hides discrete, measurable maturation events — and a genetic modulating factor

The cochlear-development literature defines concrete, individually measurable TH-dependent endpoints with no current home in the AOP: outer-hair-cell (OHC) functional maturation (DPOAE; Prestin/SLC26A5 and KCNQ4 immunostaining), endocochlear potential and stria vascularis maturation (electrophysiology; KCNJ10/Kir4.1), and synaptic/afferent remodeling (otoferlin, neurofilament, synaptophysin). Fang et al. 2012 ([PMID: 22143287](https://pubmed.ncbi.nlm.nih.gov/22143287/)) motivate this — *"The sensitivity of cochlear development and function to thyroid hormone (TH) mandates understanding TH action in this sensory organ"* — and identify specific endpoints: *"The development of outer hair cell (OHC) function is delayed, but Prestin and KCNQ4 immunostaining appear normal in mature Prop1(df) mutants."* The same study reveals a measurable modulating factor absent from AOP 8: *"Despite the same lack of detectable serum TH, these mutants have very different hearing abilities: Prop1(df) mutants are mildly affected, while Pou1f1(dw) mutants are completely deaf."* Genetic background decouples serum TH from the auditory outcome, paralleling the transport (Finding 3) and local-deiodinase (Finding 2) gaps at the tissue-delivery level.

### Finding 8 — Consolidated KE-by-KE methods-of-measurement inventory

| Key Event | Method(s) of measurement | Status |
|---|---|---|
| **MIE — AhR / CAR / PXR activation** | Nuclear-receptor reporter/transactivation assays; induction markers Cyp1a1 (AhR), Cyp2b (CAR), Cyp3a (PXR) by qPCR/activity; 178 (Q)SAR/NAM models (PXR=72, TTR=45, TPO=21) | ✅ Established |
| **KE1 — ↑Hepatic Phase-II catabolism (UGT/SULT)** | Hepatic *Ugt1a/Sult* mRNA (qPCR), UGT enzyme activity, T4-glucuronidation assay | ✅ Established |
| **KE1b — ↑Hepatic efflux transport (MRP2/OATP)** | Biliary T4-glucuronide excretion; transporter mRNA/protein | ✅ Established |
| **KE2 — ↓Serum T4/T3** | Total/free T4, T3, TSH (RIA/ELISA/LC-MS/MS); standard rodent AND human biomarker | ✅ Established |
| **KE3 — ↓Brain/tissue TH** | Brain T4/T3 (LC-MS/MS); TH-responsive transcripts; serum T4 predicts brain TH | ✅ Established |
| **KE4 — Altered cochlear development** | DPOAE/ABR; Prestin, KCNQ4, Kir4.1/KCNJ10, otoferlin immunostaining; endocochlear-potential recording — *not currently defined in the AOP* | ⚠️ Partially specified |
| **AO — Permanent hearing loss** | ABR / DPOAE thresholds; human audiometry | ✅ Established |
| **Modulating — HPT-axis feedback (↑TSH)** | Serum TSH; thyroid histopathology/weight (rodent branch) | ✅ Established |
| **★ MISSING — Carrier-mediated TH uptake (MCT8/OATP1C1)** | In situ hybridization + qPCR of MCT8/MCT10/OATP1C1/LAT1; Dio2/Dio3 | ❌ Absent from AOP |

Thus essentially every node of AOP 8 is in principle measurable — the deficiency is the AOP's failure to list methods for the cochlear KE and to include the transport step, not an absence of methods.

### Finding 9 — New hepatocyte data make the CAR/PXR branch quantitative and expose a rat-vs-human species difference

Baze et al. 2025 ([PMID: 39909212](https://pubmed.ncbi.nlm.nih.gov/39909212/)) provide the first quantitative, AOP-8-MIE-specific KER data. In cryopreserved primary Wistar rat hepatocytes, daily exposure to CAR/PXR reference activators *"phenobarbital, 5-Pregnen-3β-ol-20-one-16α-carbonitrile (PCN) or dexamethasone increased T4 clearance over the last 24 h exposure (up to 60 %, 79 % and 67 % over control, respectively) and secretion of T4-glucuronide (T4-G; up to 463, 661 and 545 pmol/10^6 cells)."* This operationalizes the hepatic-clearance KE as a continuous, measurable in vitro endpoint and upgrades the AOP-8-specific upstream branch from mechanistic plausibility to quantitative data. The study's title — *"Marked differences in thyroxine (T4) metabolism following in vitro exposure of Wistar rat and human hepatocytes to several reference CAR/PXR nuclear receptor activators"* — supplies the species-concordance axis that AOP human relevance requires, beginning to fill Crofton & Zoeller's interspecies-UGT-sensitivity gap. It also implies the MIE is empirically anchored chiefly by CAR/PXR (phenobarbital-type) inducers, with AhR-mediated T4 reduction less directly demonstrated — so lumping AhR/CAR/PXR into one MIE box is pragmatic but the three are not equally evidenced.

---

## Mechanistic Model / Interpretation

The pathway, with measurability and evidence grade annotated at each node:

```
 MIE: AhR / CAR / PXR activation
   │   [MEASURABLE: reporter assays; Cyp1a1/Cyp2b/Cyp3a qPCR; 178 (Q)SAR models]
   │   KER evidence: CAR/PXR quantitative in vitro (Baze 2025); AhR less direct
   ▼
 KE1: ↑ Hepatic TH clearance  = UGT/SULT catabolism  +  MRP2/OATP biliary efflux
   │   [MEASURABLE: Ugt/Sult qPCR, UGT activity, biliary T4-glucuronide]   ◄── LUMP THESE
   │   KER evidence: QUANTITATIVE, dose-resolved (Craft 2002; Martin 2012)
   ▼
 KE2: ↓ Serum T4/T3   ───────────────┐  (HPT feedback: ↑TSH)  ◄── LUMP 3 feedback nodes
   │   [MEASURABLE: RIA/ELISA/LC-MS/MS] │                           into one modulator
   │   KER evidence: QUANTITATIVE        └──► rodent thyroid hyperplasia/histopath
   │                                          (parallel non-neuro branch ◄── LUMP)
   ▼
 ★ MISSING KE: Carrier-mediated TH uptake (MCT8 / OATP1C1 at brain barriers)
   │   [MEASURABLE: ISH + qPCR of MCT8/MCT10/OATP1C1/LAT1; Dio2/Dio3]
   │   Can DECOUPLE serum from tissue TH  →  KEEP KE2 and KE3 SEPARATE
   ▼
 KE3: ↓ Brain / cochlear tissue TH  (local Dio2 amplify / Dio3 protect)
   │   [MEASURABLE: brain T4/T3 LC-MS/MS; TH-responsive transcripts]
   │   KER evidence: QUANTITATIVE but borrowed from TPO-inhibition sibling qAOP
   ▼
 KE4: Altered cochlear development  ◄── UNDER-SPECIFIED: hides discrete sub-events
   │   • OHC maturation: Prestin (TRβ), KCNQ4 (TRα1)   [DPOAE, immunostaining]
   │   • Endocochlear potential / stria: Kir4.1/KCNJ10 [electrophysiology]
   │   • Synaptic remodeling: otoferlin shift           [immunostaining]
   │   • Critical window P0/P1 (apoptosis)
   │   Modulating factor: genetic background (Prop1 vs Pou1f1) ◄── MISSING
   │   KER evidence: PLAUSIBILITY + genetic necessity (TRβ KO) + rescue (T4)
   ▼
 AO: Permanent hearing loss   ◄── KEEP SEPARATE from KE4 (functional vs structural)
       [MEASURABLE: ABR/DPOAE thresholds; human audiometry]
       KER evidence: ORDINAL dose-response (Poon 2011); rescue (Goldey 1998)
```

The central interpretive message is a **gradient of evidence quality along the pathway**. Upstream (MIE → hepatic clearance → ↓serum T4), the KERs are quantitative, dose-resolved, and now — thanks to Baze 2025 — anchored to AOP 8's own CAR/PXR MIE with human-relevant species data. In the middle (↓serum → ↓brain TH), quantitation is excellent but partly borrowed from a TPO-inhibition sibling AOP that shares only the ↓serum-T4 node. At the terminus (brain TH → cochlea → hearing loss) — the branch that uniquely defines AOP 8 — evidence shifts to biological plausibility, genetic necessity, and stressor-reversal rescue, with only ordinal dose-response. The pathway is thus "quantitative in the middle, plausibility-grade at the ends that matter most for the auditory AO."

| KER | Evidence type | Quantitation grade | Key support |
|-----|--------------|--------------------|-------------|
| MIE (CAR/PXR) → ↑hepatic clearance | In vitro dose/response | **Quantitative** (NAM) | Baze 2025 (PMID 39909212) |
| MIE (AhR) → ↑hepatic clearance | Mechanistic | Plausibility/measurable | Craft 2002 (PMID 12151633) |
| ↑Hepatic clearance → ↓serum T4 | In vivo dose-response | **Quantitative** | Craft 2002; Martin 2012 |
| ↓Serum T4 → ↓brain TH | In vivo dose-response | **Quantitative** (borrowed) | O'Shaughnessy 2018; Hassan 2017 |
| ↓Brain TH → cochlear damage | Genetic necessity + rescue | Essentiality / ordinal | TRβ KO; Goldey 1998 |
| Cochlear damage → hearing loss | Plausibility + dose-order | Ordinal | Poon 2011 (PMID 21873374) |

---

## Evidence Base

| PMID | Paper (abbreviated) | Role in this evaluation |
|------|---------------------|-------------------------|
| [16417043](https://pubmed.ncbi.nlm.nih.gov/16417043/) | *Crofton & Zoeller 2005 — MOA: hearing loss from PHAHs* | Foundational MOA; defines data gaps (human fetal UGT inducibility, interspecies UGT sensitivity) |
| [12151633](https://pubmed.ncbi.nlm.nih.gov/12151633/) | *Craft 2002 — hypothyroxinemia & enzyme induction, rat vs mouse* | Quantitative dose-resolved hepatic catabolism → ↓serum T4 (Finding 1) |
| [22187485](https://pubmed.ncbi.nlm.nih.gov/22187485/) | *Martin 2012 — PCB congeners, glucuronidation & biliary excretion* | Couples catabolism + efflux as one biliary readout (Findings 1, 5) |
| [39909212](https://pubmed.ncbi.nlm.nih.gov/39909212/) | *Baze 2025 — T4 metabolism, rat vs human hepatocytes, CAR/PXR* | Quantitative AOP-8-specific MIE KER + species difference (Finding 9) |
| [30085217](https://pubmed.ncbi.nlm.nih.gov/30085217/) | *O'Shaughnessy 2018 — predictive hormone measures in cortex* | Serum T4 predicts brain TH (Finding 6) |
| [28973696](https://pubmed.ncbi.nlm.nih.gov/28973696/) | *Hassan 2017 — quantitative AOP, TPO inhibition* | qAOP serum→brain→cortical heterotopia; TPO-MIE caveat (Finding 6) |
| [9848116](https://pubmed.ncbi.nlm.nih.gov/9848116/) | *Goldey & Crofton 1998 — T4 replacement attenuates hearing loss* | Causal rescue/essentiality for terminal branch (Findings 2, 6) |
| [21873374](https://pubmed.ncbi.nlm.nih.gov/21873374/) | *Poon/Schantz 2011 — PCB/PBDE cochlear function* | Ordinal DPOAE dose-response (Finding 6) |
| [19095741](https://pubmed.ncbi.nlm.nih.gov/19095741/) | *Ng 2009 — type 3 deiodinase in cochlea* | Local cochlear deiodinase as measurable event (Finding 2) |
| [17520268](https://pubmed.ncbi.nlm.nih.gov/17520268/) | *Winter 2007 — TRα1 and OHC ion channels* | Prestin/KCNQ4 as measurable cochlear endpoints (Findings 2, 7) |
| [25737207](https://pubmed.ncbi.nlm.nih.gov/25737207/) | *Peeters 2015 — apoptosis timecourse, T3* | Critical P0/P1 window (Finding 2) |
| [26241124](https://pubmed.ncbi.nlm.nih.gov/26241124/) | *Ng 2015 — TRβ1 and age-related hearing loss* | Genetic necessity of TRβ (Finding 2) |
| [24012852](https://pubmed.ncbi.nlm.nih.gov/24012852/) | *Dettling 2014 — TRα/TRβ in hair cells* | Receptor-isoform roles; TRβ deafness originates outside hair cells (Finding 2) |
| [22143287](https://pubmed.ncbi.nlm.nih.gov/22143287/) | *Fang 2012 — Prop1 genetic protection* | Discrete cochlear endpoints + genetic modulating factor (Finding 7) |
| [29183795](https://pubmed.ncbi.nlm.nih.gov/29183795/) | *Vancamp & Darras 2018 — MCT8 zebrafish to human* | Missing TH-uptake step at BBB (Finding 3) |
| [25745816](https://pubmed.ncbi.nlm.nih.gov/25745816/) | *Van Herck 2015 — transporters/deiodinases at brain barriers* | Uptake machinery is measurable (Finding 3) |
| [41915611](https://pubmed.ncbi.nlm.nih.gov/41915611/) | *Judzinska 2026 — AOP-anchored computational models* | 178 (Q)SAR/NAM models; PXR/TTR/TPO dominate (Findings 4, 8) |
| [33305658](https://pubmed.ncbi.nlm.nih.gov/33305658/) | *Sauer 2020 — human parameters for TH testing strategy* | Human-relevance/quantitative-boundary gap (Finding 4) |

Papers that **challenge or qualify** the pathway are as important as those that support it. Sauer 2020 challenges the human relevance of the hepatic-catabolism arm (no human study links enzyme induction to TH clearance to neurodevelopment). Fang 2012 challenges the sufficiency of serum TH as a predictor by demonstrating genetic-background decoupling. Hassan 2017, while providing the best quantitation, challenges the attribution of that quantitation to AOP 8 because its MIE is TPO inhibition, not nuclear-receptor activation.

---

## Supported and Refuted Hypotheses

- **Supported:** Nearly all KEs are measurable (Finding 8). The middle KERs are quantitative; the terminal branch is plausibility/essentiality-grade (Finding 6). Specific lumps improve parsimony without losing mechanistic resolution (Finding 5). The TH-uptake, deiodinase, and cochlear-marker steps are measurable and missing (Findings 3, 7).
- **Refuted / cautioned:** The AOP should **not** treat ↓serum T4 as a sufficient quantitative predictor of the cochlear AO (transport, local deiodination, and genetic susceptibility intervene). The quantitative qAOP evidence should **not** be assumed to validate AOP 8's nuclear-receptor MIE branch — it validates a TPO-inhibition sibling branch that shares only the ↓serum-T4 node (though in vitro CAR/PXR hepatocyte data, Baze 2025, now quantify the AOP-8-specific upstream KER directly). The three MIE receptors are **not equally evidenced**: CAR/PXR (phenobarbital-type) induction of TH clearance is well demonstrated, whereas AhR-mediated T4 reduction is comparatively indirect.

---

## Limitations and Knowledge Gaps

1. **MIE heterogeneity.** AhR, CAR, and PXR are lumped into one MIE box, but the quantitative evidence (Baze 2025) is overwhelmingly for CAR/PXR (phenobarbital-type) inducers; AhR-mediated T4 reduction as a driver of the catabolism KE is less directly demonstrated.
2. **Imported middle-pathway quantitation.** The best response-response modeling (O'Shaughnessy 2018, Hassan 2017) derives from a TPO-inhibition sibling AOP and connects to AOP 8 only at ↓serum-T4. AOP 8's own nuclear-receptor MIE lacks an equivalently complete serum-to-brain model.
3. **Terminal branch is not dose-modeled.** The brain-TH → cochlear-damage → hearing-loss relationship is anchored by genetic necessity and rescue, with only ordinal chemical dose-response; no study fits a continuous brain-TH-to-threshold-shift curve.
4. **Missing transport node.** Carrier-mediated TH uptake (MCT8/OATP1C1) and local Dio2/Dio3 can decouple serum from tissue TH, so the ↓serum → ↓tissue KER is a surrogate, not an identity. This node is measurable yet absent.
5. **Under-specified cochlear KE.** The generic "cochlear damage" KE lacks defined measurement methods even though specific markers (Prestin, KCNQ4, Kir4.1/KCNJ10, otoferlin, endocochlear potential) exist.
6. **Unrepresented modulating factors.** Genetic background (Fang 2012) and the narrow P0/P1 critical window materially alter the outcome at identical serum-TH levels but are not represented.
7. **Human relevance / exposure.** Whether ambient human exposures reach the magnitude of fetal hypothyroxinemia required for hearing loss remains unresolved (Crofton & Zoeller 2005; Sauer 2020).
8. **Scope of analysis.** This evaluation is a literature/structural synthesis of the AOP graphic and KE definitions; no primary dataset was provided.

---

## Proposed Follow-up Experiments / Actions (for the AOP adopter)

1. **Restructure the hepatic nodes.** Merge "↑Phase II catabolism (UGT/SULT)" and "↑hepatic efflux (MRP2/OATP)" into one KE, *Increased hepatic clearance of thyroid hormone*, with biliary T4-glucuronide excretion as the defining method.
2. **Add the TH-uptake KE.** Insert a new measurable KE between ↓serum TH and ↓tissue TH: *Decreased carrier-mediated TH uptake at brain/cochlear barriers (MCT8/OATP1C1)*, with ISH/qPCR of MCT8, MCT10, OATP1C1, LAT1 and Dio2/Dio3 as methods.
3. **Decompose the cochlear KE.** Replace generic "cochlear damage" with explicitly defined, measurable sub-events (or attach methods): OHC maturation (DPOAE; Prestin/KCNQ4 immunostaining), endocochlear potential/stria vascularis (Kir4.1/KCNJ10; electrophysiology), and synaptic remodeling (otoferlin). Annotate the P0/P1 critical window.
4. **Collapse feedback and rodent branches.** Represent the three HPT-feedback receptor nodes as one *↑TSH compensatory feedback* modulating factor, and bundle the rodent thyroid-hyperplasia/histopathology chain as one rodent-specific node, flagged as non-neurological.
5. **Represent modulating factors.** Add genetic susceptibility (background strain) and developmental timing as explicit modulating factors on the terminal KERs, citing the Prop1-vs-Pou1f1 decoupling.
6. **Generate the missing quantitation.** Commission a developmental rodent study with graded CAR/PXR-activator dosing that simultaneously measures serum T4, brain/cochlear T4/T3, cochlear molecular markers, and ABR/DPOAE thresholds to fit a continuous brain-TH-to-threshold-shift dose-response and close the terminal-branch gap.
7. **Advance human relevance.** Extend the Baze 2025 rat-vs-human hepatocyte NAM to a panel of AhR/CAR/PXR activators to quantify interspecies UGT-induction sensitivity — directly addressing the Crofton & Zoeller and Sauer data gaps — and seek human cohort data linking enzyme induction to TH clearance.

---

*Report compiled from 10 autonomous investigation iterations, 9 confirmed findings, and 21 reviewed papers.*
