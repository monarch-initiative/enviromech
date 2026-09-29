# Exposures in dismech do not reach their inflammasome nodes

**Date:** 2026-09-24
**For:** sessions working in this repository, and @gingin77
**Source:** the dismech checkout at `/Users/ginniehench/Developer/dismech`, `main` at `17609e989b`, clean tree

Twenty-two dismech disease entries carry both an NLRP3, inflammasome or pyroptosis
pathophysiology node and one or more environmental factors. Across the 54 disease-exposure
pairs that produces, **not one exposure names the inflammasome node as its target**.

This is a candidate input for EnviroMech work on inflammasome-mediated exposure outcomes.
It says where dismech already holds the exposure and the mechanism in the same file without
joining them, which is the join EnviroMech is organized around.

## Method

Over `kb/disorders/` and `kb/comorbidities/`, select pathophysiology nodes whose `name`
matches `nlrp3|inflammasome|pyroptos`, case-insensitively, in files that also carry an
`environmental:` block. For each environmental factor, read its
`influences_mechanisms[].target` values, then walk `pathophysiology[].downstream[].target`
edges from each target to see whether the inflammasome node is reachable and at what
distance. Distance 0 would be a direct link, and there are none.

Two limits worth stating. The node selection is a name search, so entries modelling
inflammasome biology under a name that omits those three words are missed. Reachability
follows `downstream` edges only, not `sequelae` or `reports_on`.

## The table

"Directly associated" means the exposure's own `influences_mechanisms` target *is* the
inflammasome node. Step counts are the shortest causal path found from the exposure's
actual target to that node.

| Disease | Inflammasome node | Environmental factor | Directly associated? |
|---|---|---|---|
| Asbestosis | NLRP3 inflammasome activation | Occupational asbestos inhalation | No. Reaches it in 3 steps via biopersistent asbestos fiber deposition (TRIGGERS) |
| Atrial Fibrillation | Fibroblast NLRP3 Inflammasome Activation | Hypertension; Obesity; Obstructive Sleep Apnea; Tobacco Smoking; Alcohol Exposure; Hyperthyroidism | No. All six reach the pathograph, none reaches this node |
| Bronchiectasis | Inflammasome Activation and IL-1beta Signaling | Pollution; Smoking | No. Neither declares any mechanism link |
| CINCA Syndrome | NLRP3 gain-of-function mutation; Constitutive NLRP3 inflammasome activation | Cold exposure | No. No mechanism link declared |
| Chorioamnionitis | NLRP3 Inflammasome Activation and Pyroptosis | Obstetric Instrumentation and Prolonged Labor | No. Reaches it in 3 steps via vaginal dysbiosis and cervical barrier breach (TRIGGERS) |
| Chorioamnionitis | same | Oral and Periodontal Infection | No. Reaches it in 2 steps via ascending microbial invasion (PREDISPOSES) |
| Chronic Obstructive Pulmonary Disease | NLRP3 Inflammasome Activation | Smoking; Air Pollution; Occupational Dust and Chemicals | No. All three link elsewhere, none reaches this node |
| Coal Workers Pneumoconiosis | NF-kappaB and NLRP3 Inflammasome Activation | Occupational inhalation of respirable coal mine dust | No. Reaches it in 3 steps via dust deposition and retention (TRIGGERS) |
| Coal Workers Pneumoconiosis | same | Cigarette smoking | No. Links to impaired gas exchange, which does not reach this node |
| Coccidioidomycosis | Spherule rupture-triggered inflammasome activation and neutrophil recruitment | Arid and semi-arid soil exposure; Dust storm and windblown dust events | No. Both reach it in 2 steps via arthroconidia inhalation (TRIGGERS) |
| Coccidioidomycosis | same | TNF-alpha inhibitor therapy | No. Links to adaptive immunity, which does not reach this node |
| Familial Cold Autoinflammatory Syndrome | NLRP3 gain-of-function mutation; Constitutive NLRP3 inflammasome activation; NLRP1 inflammasome activation | Generalized cold exposure | No. No mechanism link declared |
| Familial Mediterranean Fever | Gasdermin D-Mediated Pyroptosis | Physical Exertion; Emotional Stress | No. Neither declares a mechanism link |
| Gout | Inflammasome Activation | Red Meat and Organ Meat Intake; Shellfish Intake; Beer Intake; Fructose-Sweetened Soft Drink Intake | No. All four reach it in 2 steps via hyperuricemia (EXACERBATES) |
| Gout | same | Dehydration; Diuretics | No. Neither declares a mechanism link |
| Hypertensive Heart Disease | Inflammasome Activation | Uncontrolled Hypertension | No. Reaches it in 2 steps via increased cardiac workload (TRIGGERS) |
| Ischemic Stroke | Microglial NLRP3 Inflammasome Activation in the Ischemic Penumbra | Vascular and metabolic risk-factor burden | No. No mechanism link declared |
| Multiple Sclerosis | Microglial NLRP3 Inflammasome Activation | Vitamin D Deficiency; Epstein-Barr Virus Infection | No. Both link to Th1/Th17 neuroinflammation, which does not reach this node |
| Obstructive Sleep Apnea | NLRP3 Inflammasome Activation | Alcohol Consumption; Sedatives; Supine Sleep Position; Nasal Congestion | No. None declares a mechanism link |
| Pericarditis | Inflammasome activation in pericardial tissue | Mediastinal irradiation; End-stage renal disease and uraemia; Cardiac injury and surgery | No, but closest in the set. All three reach it in 1 step via pericardial injury from a heterogeneous trigger (TRIGGERS) |
| Post-Traumatic Epilepsy | Neuroinflammation and Inflammasome Activation | Traumatic Brain Injury | No. No mechanism link declared |
| Preeclampsia | NLRP3 Inflammasome Activation and Inflammatory Cascade | Gestational phthalate exposure; Micro- and nanoplastic particle exposure | No. Both reach it in 1 step via defective trophoblast invasion |
| Preeclampsia | same | Gestational bisphenol A exposure | No. Links to anti-angiogenic factor release, which does not reach this node |
| Rosacea | NLRP3 Inflammasome Activation | Ultraviolet B radiation; Corticosteroid treatment | No. Both reach it in 3 steps via skin barrier dysfunction (EXACERBATES) |
| Shigellosis | Inflammasome sensing and pyroptotic inflammation | Contaminated water or food; Poor sanitation and hygiene | No. Both link to bacterial invasion, which does not reach this node |
| Silicosis | NLRP3 Inflammasome Assembly and Caspase-1 Activation; Macrophage Pyroptosis and Silica Re-uptake | Occupational Respirable Crystalline Silica Exposure | No. Reaches it in 2 steps via alveolar macrophage phagocytosis of silica (TRIGGERS) |
| Ulcerative Colitis | NLRP3 Inflammasome-Mediated Pyroptosis | Appendectomy; Smoking; NSAIDs; Infections; Stress | No. None declares a mechanism link |

## How the 54 pairs split

| Relationship to the inflammasome node | Pairs |
|---|---|
| Reaches it through the causal chain | 19 |
| Linked to the pathograph, but no path to this node | 16 |
| No mechanism link declared at all | 19 |

## Two cases to look at first

**Cold exposure in the cryopyrin-associated syndromes.** Familial Cold Autoinflammatory
Syndrome and CINCA both record cold exposure with no mechanism link, and in the former cold
is the defining trigger, sitting in the same file as a constitutive NLRP3 activation node.
The exposure and the mechanism it acts on are both curated and are not joined.

**The canonical particle diseases.** Silicosis and asbestosis are textbook particle-driven
inflammasome diseases. Both do wire the exposure into the pathograph, and both still route
to the inflammasome node through two or three intermediate steps rather than naming it.
These are the cases where the mechanistic literature is strongest, so they set the ceiling
for what dismech currently asserts about an exposure-to-inflammasome link.

## What this does not establish

The absence of a direct link is not evidence that a direct link is wrong. dismech routes
exposures to the mechanism step the cited evidence supports, and an intermediate step is
often the honest target. This report says where the join is absent, not where it is owed.
