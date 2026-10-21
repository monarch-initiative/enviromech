# Research artifacts

This directory is **not** an established EnviroMech convention. It exists on the
`tds-nonmammalian-androgen-research` branch only, as a holding place so that a
deep-research run does not disappear when the DisMech worktree that produced it
is removed.

Deep research is off in this repository. `docs/WORKFLOWS.md`:

> Off. Answer `deep_research` in Copier to add `just research` and pass provider
> keys to the curating agents.

So there is no `just research`, no reference-validation recipe for a research
artifact, and no decision recorded about where such artifacts belong or whether
they should be committed at all. That question is open in
[issue #12](https://github.com/monarch-initiative/enviromech/issues/12), and
should be settled before this branch is merged or this layout is copied.

## What is here

A deep-research run asking which non-mammalian models of androgen signalling
could support the pathograph nodes of DisMech's `Testicular_Dysgenesis_Syndrome`
entry. It was produced in DisMech and proposed there in
[dismech#15060](https://github.com/monarch-initiative/dismech/pull/15060), which
was closed without merging: the run's surviving candidates are exposure-outcome
associations rather than disease-mechanism models, which is EnviroMech's subject
rather than DisMech's.

| File | What it is |
| --- | --- |
| `Testicular_Dysgenesis_Syndrome-nonmammalian-androgen-models-deep-research-openscientist.md` | The report, with frontmatter recording provider, date and `template_sha` |
| `…​.md.citations.md` | The run's citation list |
| `…​_artifacts/final_report.html`, `…​/final_report.pdf` | The provider's own rendered output, unmodified |
| `../templates/disease_nonmammalian_models_research.md` | The prompt the run used |

The template is kept because the report's `template_sha` pins it by blob hash
(`13f64a54d8d53e7eabcee8336fb164856c6fea48`), so removing it would break the
report's provenance. It is a frozen one-off and not reusable as it stands: its
body hardcodes the TDS node list, and only `{disease_name}` and `{mondo_id}` are
placeholders. A generalised version of it lives in DisMech
([dismech#15058](https://github.com/monarch-initiative/dismech/pull/15058)).

## Reading it

Two things in the report are known to need care, both recorded in issue #12:

- It asserts that avian phallus reduction is androgen-independent, citing
  PMID:23746636, in four places. That abstract contains no mention of androgen or
  testosterone. The paper describes a non-androgenic mechanism for a homologous
  structure; it does not establish androgen-independence. The provider output is
  left unmodified here on purpose — the correction belongs in a curation record,
  not in a rewrite of what the provider returned.
- Its candidate triage distinguishes correlational findings in contaminated
  populations from controlled in-ovo exposures. That distinction is load-bearing
  for the alligator candidate, where the controlled studies did not reproduce the
  population findings, and it should not be flattened when records are written.
