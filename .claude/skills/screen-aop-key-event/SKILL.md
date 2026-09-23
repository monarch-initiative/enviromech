---
name: screen-aop-key-event
description: >
  Screen one AOP-Wiki Key Event for internal errors before its structured
  properties are used to look for matching dismech pathograph nodes. Use when
  reusing an existing Key Event in an EnviroHealthMech pathway, when a Key
  Event's level of biological organization looks wrong for its description, when
  deciding whether a level difference between AOP-Wiki and dismech is a real
  modelling difference or an error in the AOP-Wiki record, or before writing a
  KeyEventAggregation record.
---

# Screen an AOP-Wiki Key Event before comparing it with dismech

An EnviroHealthMech pathway reuses an existing Key Event rather than inventing
one, and reusing it means inheriting its structured properties. The level of
biological organization is the one that then decides curation work: it governs
which dismech pathophysiology nodes can be aggregated into that Key Event, and a
`KeyEventAggregation` record checks each source node against it.

So an error in the Event propagates. If the Event's assigned level does not match
its own description, a curator either rejects a dismech node that does fit,
accepts one that does not, or records a level mismatch that reads as a difference
between two knowledge bases when it is a defect in one of them. **KE 1909**
*Mucociliary Clearance, Decreased* is the worked case: AOP-Wiki assigns it
Individual, its description is about tracheal and small-airway clearance, and
dismech's matching node is `TISSUE`.

This procedure screens one Key Event first. It is a **clean-up step, and its
output is a report for a person to read** - neither pass returns a verdict.

## Prerequisites

- A clone of [`aop_wiki_cli`](https://github.com/gingin77/aop_wiki_cli) with a
  dated AOP-Wiki XML snapshot already collected. Check what exists before
  choosing a date; a missing date downloads and parses the ~50 MB export.
- Anthropic credentials for step 3 only. Step 2 is offline.
- The level definitions come from the AOP-Wiki EMOD LinkML schema in
  `linkml-aop`, which `aop_wiki_cli` depends on. Both passes read them, so a
  result is only as good as the definition it was judged against.

```bash
cd ~/Developer/aop_wiki_cli
export AOP_WIKI_CLI_DATA_DIR=~/Developer/aop_wiki_cli   # never a dismech checkout
ls outputs/cache/                                       # snapshot dates available
```

## Step 1 - Record which Key Event and why

Write down the Key Event ID, the snapshot date, and the EnviroHealthMech pathway
it is being screened for. Every judgement below is relative to that Event as the
snapshot holds it, and a later snapshot may differ.

## Step 2 - Run the deterministic check (offline, free)

```bash
uv run aop-wiki-cli event-content-internal-alignment --date <MM-DD-YYYY> --ke-ids <KE_ID>
```

It compares the Event's assigned level with its description, searching for words
drawn from each level's definition in the schema. A subset run writes its own
timestamped files under `outputs/event_alignment/<date>/`, so it never overwrites
a whole-snapshot report. Read the CSV: it carries the title, the assigned level,
the cue words found, and the description text.

Four outcomes:

| Result | What it means | Go to step 3? |
|---|---|---|
| **flag** | The description has no words for the assigned level and does have words for another | **Yes** |
| **note** | The description has text but no level words at all | **Yes** - this is where keywords are weakest |
| **unchecked** | The Event has no description | No - see below |
| no finding | The description carries words for the assigned level | No |

**A `note` is not a weaker flag; it is a blind spot.** KE 97 *Alkylation, DNA* is
the case: DNA adducts, alkylated nucleotides, phosphate diester groups, and not
one word shared with the Molecular definition. The keyword pass could only report
that it recognised nothing. Escalate these.

**An `unchecked` Event cannot be screened at all.** 962 of the 1,598 Events in the
09-03-2026 snapshot have no description. Record that its level is unconfirmed and
rests on the Event title alone, and carry that into whatever uses it.

## Step 3 - Escalate to the model review (one API request)

```bash
uv run --env-file .env aop-wiki-cli event-level-llm-review --date <MM-DD-YYYY> --ke-ids <KE_ID>
```

This asks a model the question the definitions ask, giving it those definitions
as the criterion, plus two rules from the AOP Developers' Handbook v2.8: a Key
Event is defined within a single level, and the level is where the change
*happens*, not where it is *measured*.

Credentials are not read from `.env` automatically, which is what `--env-file`
is for; `set -a && . ./.env && set +a` does the same for a whole shell. A failed
request is recorded as an `error` finding rather than crashing the run.

| Result | Meaning |
|---|---|
| `events_model_agreed: 1`, no findings | The model reads the description as fitting the assigned level |
| **flag** naming another level | The model reads a different level, with quotes and reasoning |
| **flag** for spanning levels | The level fits, but the description crosses levels, which the Handbook rule forbids |
| **note** | The model could not tell from the description |

Each finding records the model, the time, and a digest of the definitions it was
judged against, so a result made against an older revision of the definitions is
distinguishable from a current one.

## Step 4 - Decide, and write the decision down

The two passes disagreeing is informative, not a failure: the keyword pass
recognising nothing while the model finds clear alignment is the KE 97 pattern,
and it points at a gap in the level definition rather than at a bad Event.

| Screened outcome | What it means for the pathway |
|---|---|
| Both agree the level fits | Proceed. Use the Event's level when checking dismech nodes for aggregation |
| The model names a different level | **Do not inherit the assigned level.** A level difference with dismech here is probably an AOP-Wiki error. Record the Event ID, both levels, and the model's quoted evidence |
| The description spans levels | The Event may need splitting upstream. Say so rather than aggregating dismech nodes across two levels |
| Model cannot tell, or no description | The level is unconfirmed. Record that, and do not let a `KeyEventAggregation` level check rest on it |

Record the outcome wherever the pathway work lives, with the snapshot date and
the definitions digest. A screened Event should not need screening twice.

**When a screen finds an error in AOP-Wiki's own record**, it belongs in the
inventory of AOP-Wiki data errors that dismech issue
[#10773](https://github.com/monarch-initiative/dismech/issues/10773) collects.

## What this does not do

- It does not check taxa, sex or life stage. Those checks exist in
  `event_content_internal_alignment` but are commented out, because the
  permissible values of `SexTermEnum` and `LifeStageTermEnum` carry no
  definitions to read.
- It does not validate a `KeyEventAggregation` record. That is a separate check,
  over EnviroHealthMech's own records rather than over AOP-Wiki's.
- It does not judge whether the Event is the right one for the pathway. It
  checks the Event against itself.
