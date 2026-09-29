# Tentative To Do

Work that is drafted but not started. Each item says what exists today, what is
missing, and where the pieces would live.

## Break the dismech `mie-ker-capture` skill into components

dismech's `mie-ker-capture` skill is the only written method for going from a set of
AOP-Wiki Key Events to curated causal edges. It is eight steps in one procedure: fix the
Key Event set and the entity; run the KER lookup; read the JSON; split by role and filter
by relevance; triage KER evidence; assemble chains and find where they land; verify each
edge; record what was not curated. It was written for dismech's case, a Molecular
Initiating Event with no dismech counterpart, and every step assumes the disease entity
is already chosen.

EnviroMech runs the same method in the other direction, from an Event to the dismech
nodes that constitute it, and needs the steps as separate, reusable pieces. The split as
it stands:

| Component | State |
|---|---|
| Screen one Key Event for internal errors before its properties are used | Exists here: the `screen-aop-key-event` skill |
| Find dismech nodes from a Key Event's structured properties (process, object, action, level) across the whole corpus | Missing. Today a curator reads one already-chosen entry's node names (skill step 6). Planned as `scripts/find_source_nodes.py`: exact-CURIE hits first, label and synonym overlap second, output a ranked candidate list for a person to read. KE 1908 shows why it lists rather than decides: the Event binds `HP:0012262` and the matching nodes bind `GO:0003341`. Ontology closure is a later tier and needs a local build |
| Resolve a chosen node reference into a `SourceNode` block, and check a record against dismech | Exists here: `scripts/resolve_source_node.py`, `just resolve-source-node`, `just check-source-nodes` |
| Triage KER evidence and let it set priority (skill step 5) | Exists in dismech as the `ker-evidence-triage` skill; not yet referenced from here |
| Run the KER lookup and read its JSON by role (skill steps 2 to 4) | Exists in `aop_wiki_cli`; the skill's wrapping prose is dismech-specific |
| Assemble chains and decide where they land; verify edges; record what was not curated (skill steps 6 to 8) | dismech-shaped. What the EnviroMech equivalent is depends on the open decisions in the register about what a pathway record here is |

Order of work: the node-finding script first, since it is the one piece with no home
anywhere. Then a short EnviroMech procedure that points at the existing pieces by name
rather than restating them.
