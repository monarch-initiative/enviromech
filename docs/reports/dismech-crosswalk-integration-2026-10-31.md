# Using dismech's AOP crosswalk script from EnviroMech

**Date:** 2026-10-31
**Status:** steps 1, 2, 3 and the drift check in step 5 are built; step 4 holds the decisions
still open, and one item in step 5 is left for later.
**Depends on:** [dismech#16232](https://github.com/monarch-initiative/dismech/pull/16232),
which adds `scripts/aop_dismech_crosswalk.py`. Merged on 2026-11-01 as `aef740d7b8a`.
**For:** [#14](https://github.com/monarch-initiative/enviromech/issues/14), the AOP 40
crosswalk, and every AOP after it.

## What the dismech script gives us

`scripts/aop_dismech_crosswalk.py` reads the Key Events of an AOP from the
`aop-wiki-cli` cache and, for chosen dismech entries, reports:

- the pathophysiology nodes and phenotypes that match each Key Event, and the basis
  for each match: a shared component `term`, a `conforms_to` module node, a cell-type
  or location `label`, or the title's words (`name`). The last two are weak;
- whether the node's `biological_scale` agrees with the Event's level;
- for the Key Event Relationships among the Events, whether the entry's causal edges
  assert them.

A match is a candidate, not a mapping. Choosing the node, the relation and the
rationale stays a curator's judgement, recorded in a `KeyEventRecord`'s `aggregation`.

The script stays in dismech, and EnviroMech runs it from a dismech checkout, the same
way it uses dismech's `aop-wiki` skill. Nothing is copied here.

## Checked already

Run from this repository, the script works in dismech's own environment:

```bash
D=~/Developer/dismech   # a checkout with the script on it
uv run --project "$D" python "$D/scripts/aop_dismech_crosswalk.py" --root "$D" \
    --data-dir ~/Developer/aop_wiki_cli --date 10-03-2026 \
    --aop 40 --entry Contact_Dermatitis --format json
```

For AOP 40 against `Contact_Dermatitis` it gives the candidates found by hand for #14:
KE 272 on `Allergen-specific T-cell priming` (GO:0042110, level differs), KE 826 on the
irritant-arm keratinocyte node, KE 398 only on cell-type labels, and nothing for KE 396
or KE 827.

## Next steps, in order

### 1. A recipe that runs the crosswalk (built)

`just crosswalk AOP ENTRY...` runs the script against a dismech checkout and an
`aop-wiki-cli` data directory, and writes `build/crosswalk/AOP-<id>.json` and `.txt`,
which are not committed. It needs a dismech checkout at or after `aef740d7b8a`, the merge
of dismech#16232.

- **Where the two checkouts are.** Read from `$DISMECH_ROOT` and
  `$AOP_WIKI_CLI_DATA_DIR`, defaulting to `~/Developer/dismech` and
  `~/Developer/aop_wiki_cli`. dismech's own `repo_root()` already honours
  `DISMECH_ROOT`.
- **The snapshot date.** Taken from the AOP record's `aop_wiki_snapshot` (ISO) and
  converted to the `MM-DD-YYYY` the script and `aop-wiki-cli` take, so the crosswalk
  always runs against the snapshot the records were read from.
- **Provenance.** The recipe records the dismech commit it ran against
  (`git -C "$DISMECH_ROOT" rev-parse HEAD`) beside the output, and refuses to run if
  that checkout has uncommitted changes to `kb/`.
- **Not in `just qc`.** It needs two sibling checkouts that CI does not have.

### 2. A script that turns a chosen match into a `source_nodes` item (built)

`just source-node ENTRY "NODE"`, `scripts/source_node.py`.


Writing a `SourceNode` by hand means copying the node's name, level, process and
object terms with their labels, and the entry's URI, from the dismech YAML. A small
script here takes an entry and a node name and prints the item, ready to paste into a
record's `aggregation`, as `KE-272.yaml` has it:

- `source_node_ref` in dismech's `<entry>:pathophysiology#<node>` grammar;
- `source_entry_uri` from the entry name;
- `source_level` verbatim, and `biological_organization_id` mapped from it
  (`MOLECULAR` to Molecular, `CELLULAR` to Cellular, `TISSUE` to Tissue, `ORGANISM` to
  Individual);
- `processes` and `objects` from the node's GO, CL and UBERON bindings, with their
  labels;
- `biological_action_id` from a process modifier, when there is one.

It reads the entry's YAML from the dismech checkout, which is content, not dismech
code. It leaves `rationale`, `aggregation_relation` and `level_mismatch_note` to the
curator. It is tested on fixtures; the existing `KE-272.yaml` node is the expected
output for its case. Against dismech today it reproduces four of the five existing
`source_nodes` items exactly; the fifth is the drift case in step 5.

### 3. A skill for the crosswalk itself (built)

`.claude/skills/crosswalk-key-event/SKILL.md`.


A `crosswalk-key-event` skill, for the judgement part. It is EnviroMech's own, because
it ends in an EnviroMech record; it points at dismech's `aop-wiki` skill for the data
rather than copying it. Its steps:

1. Screen the Event's level first (`screen-aop-key-event`). Where the screen disputes
   the level (KE 272, KE 827), compare nodes against the screened level, not the
   script's `level` column, which uses AOP-Wiki's.
2. Run `just crosswalk`. Read the bases: a `term` or `conforms_to` match is a lead, a
   `label` or `name` match alone is not.
3. Read each candidate node in the entry, and its neighbours. The script cannot see
   that a node sits in the wrong arm of the pathograph (KE 826's case).
4. Choose the relation, write the rationale in the curator's own words, and fill
   `level_mismatch_note` when the levels differ.
5. Where no node corresponds, leave `aggregation` unset and say why in `notes`,
   citing any dismech knowledge-gap discussion (KE 827's case).
6. Validate, and write a history record.

### 4. Decisions needed before the AOP 40 crosswalk can finish

- **A relation for a node broader than the Event.** `AggregationRelationEnum` has
  `constitutes` and `narrower_than`. KE 398's closest node is wider than the Event, and
  neither value fits. Adding a value is an `extend-schema` change.
- **KE 396.** dismech's covalent-binding node, asked for in monarch-initiative/dismech#16068,
  was added by monarch-initiative/dismech#16226 on 2026-10-31:
  `Covalent hapten-protein adduct formation`, at `MOLECULAR`. Against dismech `aef740d7b8a`
  the crosswalk finds it for KE 396 on the `name` basis only: the node does not bind the
  Event's component terms (GO:0005515, CHEBI:59739). The aggregation is still to be written.

### 5. Later

- **A drift check (built).** `just check-source-nodes`, `scripts/check_source_nodes.py`,
  resolves every dismech source node in `data/key_events/` against the current dismech
  checkout and reports nodes that were renamed, removed, or whose level or terms changed
  since the aggregation was written. Its first run finds one: dismech's
  `Primary_Ciliary_Dyskinesia` node `Ciliary Dysfunction`, aggregated into KE 1908, now
  also binds three GO cellular components and three UBERON locations. Whether KE 1908's
  aggregation should take them is a curation decision, left open.
- **The dismech commit in the script's own output (not done).** Step 1 records it from
  the outside. If more consumers appear, the script could print it itself; that would be a
  dismech change.

## Not planned

- A copy of `aop_dismech_crosswalk.py`, or of its parkinsonism rules, in this
  repository. There is one script, in dismech, and EnviroMech runs it there; a second
  copy here would drift from it.
- Writing aggregations automatically from the script's output. The output is a list of
  candidates, and the AOP 40 run shows why: its one `direct` KER, 834, rests on a
  cell-type label match in the irritant arm.
