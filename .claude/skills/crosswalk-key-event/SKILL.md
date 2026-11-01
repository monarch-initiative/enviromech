---
name: crosswalk-key-event
description: >-
  Cross-walk an AOP's Key Events onto dismech pathograph nodes and record the
  result in each Key Event record's aggregation: find candidate nodes with
  dismech's crosswalk script, judge them, choose the aggregation_relation,
  write the rationale and any level mismatch, or record that no node
  corresponds. Use when mapping Key Events to dismech nodes, writing or
  reviewing a KeyEventAggregation, or checking aggregations that dismech has
  since changed. Not for screening a Key Event's level (screen-aop-key-event)
  or for changing the schema (extend-schema).
---

# Cross-walk Key Events onto dismech nodes

A Key Event record's `aggregation` says which dismech pathophysiology nodes the
Event is made of, and argues that the aggregation does not misrepresent the
biology. Finding candidate nodes is mechanical; deciding is not. This skill does
the first with tools and the second by reading.

The candidate finder is dismech's `scripts/aop_dismech_crosswalk.py`. It stays in
dismech, and this repository runs it in a dismech checkout; do not copy it here.
For how it reaches AOP-Wiki data, read dismech's `aop-wiki` skill in that checkout
(`.claude/skills/aop-wiki/SKILL.md`), not a copy.

`KE-396.yaml` is the worked example of a one-node `nodes_narrower_than_event`, `KE-272.yaml`
of a correspondence with a level mismatch, and `KE-398.yaml` of `overlaps`
across two nodes; `KE-1908.yaml` and `KE-1909.yaml` are lumpings of two nodes.
`KE-826.yaml` and `KE-827.yaml` show what to record when no node fits.

## Before starting

- A dismech checkout with the script, at `$DISMECH_ROOT` (default
  `~/Developer/dismech`), and an `aop-wiki-cli` data directory holding the AOP
  record's snapshot, at `$AOP_WIKI_CLI_DATA_DIR` (default `~/Developer/aop_wiki_cli`).
- The AOP record under `data/aops/` and a record for each of its Key Events under
  `data/key_events/`.
- The dismech entry or entries the crosswalk is for, by slug. Every judgement below
  is relative to them; write them down.

## Step 1 - Screen each Key Event's level

Run `screen-aop-key-event` on each Event that has not been screened, and record the
outcome in `level_screening`. The level decides which nodes can fit, and AOP-Wiki's
is sometimes wrong (KE 272 is assigned Organ and reads as Cellular).

## Step 2 - Find the candidates

```bash
just crosswalk <aop-id> <entry> [<entry> ...]
```

It runs against the snapshot the AOP record names, records the dismech commit, and
writes `build/crosswalk/AOP-<id>.json` and `.txt`. Read the `.txt`. For each Key
Event it lists the matching nodes and phenotypes, each with its basis and level:

| Basis | What it means | Weight |
|---|---|---|
| `term` | the node binds a term the Event's components name | a lead |
| `conforms_to` | the node conforms to a module node that binds one | a lead |
| `label` | a cell type or location shares the Event's cell or organ label | where, not what: no lead on its own |
| `name` | the title's words are in the node's name | weakest |

The `level` column compares the node's `biological_scale` with **AOP-Wiki's** level.
Where step 1 disputed that level, compare against the screened level yourself.

A Key Event with no candidates is a finding, not a failure. So is one whose
components AOP-Wiki left empty: it can only be found by reading.

## Step 3 - Read the candidates in the entry

Open the dismech entry and read each candidate node with its `description`, its
upstream and downstream nodes, and the entry's `discussions`. The script cannot see:

- **which arm of the pathograph a node is in.** KE 826's only keratinocyte node sits
  in the irritant arm, downstream of barrier disruption, while the Event is
  hapten-driven. Same level, same process term, wrong cause.
- **knowledge gaps.** dismech records missing steps as `KNOWLEDGE_GAP` discussions
  (`no_node_for_covalent_haptenation`). A gap attached near the Event is often the
  answer.
- **nodes it did not match.** A node with no bindings can still be the right one;
  scan the entry's node names.

## Step 4 - Decide, per Key Event

**A node, or a set of nodes, corresponds.** Choose the `aggregation_relation`:

- `constitutes`: the nodes together are the Event, nothing more and nothing less.
- `nodes_narrower_than_event`: each node is a narrower case of the Event; the
  Event covers biology they do not assert. The value names both sides because the
  comparison has a direction; a value that needs none, such as `constitutes` or
  `overlaps`, does not.
- `nodes_broader_than_event`: each node contains the Event and asserts biology
  beyond it. The mirror of the previous value.
- `overlaps`: neither side contains the other, or the set is mixed, its nodes
  standing in different relations to the Event (KE 398). It is the weakest value,
  so use it only when none of the other three holds for every node, and say in the
  rationale which part of each node is inside the Event and which is outside.

The relation is asserted for the whole set, so a directional value needs every
node to stand in that relation. One broader node beside one partly-overlapping
node is `overlaps`, not `nodes_broader_than_event`.

A node that binds a process belonging to a neighbouring Key Event is asserting
biology outside this Event, so `nodes_narrower_than_event` does not hold for it (KE 272's
node also binds dendritic cell antigen presentation, which is KE 398's).

Then write the record's `aggregation` (step 5).

**No node corresponds.** Leave `aggregation` unset. Say in `notes` which node came
closest, why it does not fit, and which dismech knowledge gap or open pull request
covers the missing step, if one does.

## Step 5 - Write the aggregation

For each chosen node:

```bash
just source-node <entry> "<node name>"
```

prints the `source_nodes` item: the reference, level, terms with their labels and
URI as dismech records them, with the node's description as a comment. Paste it
under `aggregation.source_nodes`, and add the node's `notes` (what dismech curates on
it that bears on the Event). Then add the models dismech links to the node:

```bash
just source-models <entry> "<node name>"
```

prints the node's `models` list: each curated model dismech links to the node, by
its cross-entry reference, with the link's `relationship` as `source_relationship`.
Paste it into the node's item, before its `notes`. It is copied, not judged: list
every model the script prints, and none it does not. Model systems of a proposed
experiment are left out, as dismech leaves them off the node. A model linked to two
aggregated nodes is listed under each. If the script prints that dismech links no
model, leave `models` out.

Then write, in your own words:

- **`rationale`**: why these nodes are this one measurable change. Compare the
  Event's components, not its title, with the nodes' terms (KE 1908 rests on its
  component because its title asserts a direction the nodes do not). A rationale that
  restates the title or the relation fails review.
- **`level_mismatch_note`**: present only when a node's level differs from the
  Event's. Name the node, both levels, and which reading the evidence supports,
  citing the level screen.
- **`internal_edges`**: every causal edge dismech draws between two of the
  aggregated nodes.
- **`notes`**: that the aggregation is asserted for the Event, not for any one AOP,
  when the Event sits in several.

Update the record's header comment to cite the dismech commit the crosswalk ran
against (it is in the `.json`'s `run` block).

## Step 6 - Check and record

```bash
just validate-key-events
just check-ids
just check-source-nodes    # every aggregated node against today's dismech
just qc
```

Add a history record with `just new-history --kind record --slug KE-<id>
--path data/key_events/KE-<id>.yaml ...`, naming the dismech commit and the
snapshot. Leave the record's `status` where it is; an agent takes a record no
further than `PROPOSED`.

## Later: when dismech changes

`just check-source-nodes` reports aggregated nodes that dismech has renamed,
removed, or re-bound since the aggregation was written, and, for a node with a
`models` list, models renamed, removed, re-linked or newly linked. A node with no
`models` list gets a NOTE with the number of models dismech links to it. A difference is a prompt to
re-read the node, not an instruction to copy the new terms: decide whether the
aggregation still holds, update it or its notes, and record that in a history
record.
