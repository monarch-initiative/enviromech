# AOP-Wiki data errors

Problems found in AOP-Wiki's own records while curating EnviroMech. Each entry is
something in the AOP-Wiki record itself, not a difference between AOP-Wiki and
EnviroMech or dismech. The record that found it keeps the detail; this page collects
them in one place so they can be reported upstream together.

**How to add an entry.** Add a row to the table for the kind of problem, with the
entity's AOP-Wiki id, what is wrong, the XML export snapshot it was read from, and the
EnviroMech record that recorded it. A Key Event's term problems are also recorded on
its record, under `term_findings`; a level problem found by the
[`screen-aop-key-event`](https://github.com/monarch-initiative/enviromech/tree/main/.claude/skills/screen-aop-key-event)
skill is recorded under `level_screening`.

**Kinds of problem.**

- **Obsolete term:** a bound ontology term has been obsoleted by its ontology.
- **Internal inconsistency:** two parts of one record disagree, such as a title and an
  event component, or an assigned level and the record's own description.
- **Missing term:** a field the Event's description clearly calls for is empty.
- **Questionable term:** a term is bound, but a different one fits the Event better.
  These are curator judgements and need confirming before they are reported.

Status is `open` until reported to AOP-Wiki, then `reported` with a link, then `fixed`
once a later export carries the correction.

## Obsolete terms

| Entity | Problem | Snapshot | Recorded in | Status |
|---|---|---|---|---|
| KE 1542, Inhibition, Mitochondrial complex III | Biological object GO:0005750 is obsolete ("obsolete mitochondrial respiratory chain complex III"), replaced by GO:0045275. Checked against OLS on 2026-10-03. | 2026-10-03 | `data/key_events/KE-1542.yaml` | open |

## Internal inconsistencies

| Entity | Problem | Snapshot | Recorded in | Status |
|---|---|---|---|---|
| KE 177, Increase, Mitochondrial dysfunction | The title says "Increase"; the event component's action is "functional change". | 2026-10-03 | `data/key_events/KE-177.yaml` | open |

## Missing terms

| Entity | Problem | Snapshot | Recorded in | Status |
|---|---|---|---|---|
| KE 177, Increase, Mitochondrial dysfunction | The event component has no biological process; only the object (mitochondrion, GO:0005739) and the action. | 2026-10-03 | `data/key_events/KE-177.yaml` | open |
| KE 890, Degeneration of dopaminergic neurons of the nigrostriatal pathway | No cell term, although the Event is about dopaminergic neurons (CL:0000700). | 2026-10-03 | `data/key_events/KE-890.yaml` | open |
| KE 896, Parkinsonian motor deficits | The event component has no biological process, and the Event has no cell or organ term. | 2026-10-03 | `data/key_events/KE-896.yaml` | open |

## Questionable terms

| Entity | Problem | Snapshot | Recorded in | Status |
|---|---|---|---|---|
| KE 890, Degeneration of dopaminergic neurons of the nigrostriatal pathway | The organ term is corpus striatum, while the title and the process concern the nigrostriatal pathway, whose dopaminergic cell bodies are in the substantia nigra (UBERON:0002038). | 2026-10-03 | `data/key_events/KE-890.yaml` | open |
| KE 896, Parkinsonian motor deficits | The event component's object is a MeSH disease heading (D020734, Parkinsonian disorders); a phenotype term such as HP:0001300 (Parkinsonism) would describe the motor deficit. | 2026-10-03 | `data/key_events/KE-896.yaml` | open |

## Not yet checked

No Key Event has been through the level screen yet; all six records are
`NOT_SCREENED`. KE 890's record notes that its assigned level, Organ, is worth
screening: the Event is the loss of a cell population and has no cell term.
