# Two fixes for mechmaker: a generated Mech fails its checks on macOS

These two patches are for [monarch-initiative/mechmaker](https://github.com/monarch-initiative/mechmaker).
They are here because the account that wrote them has read-only access to mechmaker and
could not push a branch. They apply cleanly to mechmaker `main` at `83c34c9`.

A freshly generated Mech cannot pass `just qc` or `just qc-full` on macOS. CI runs on
Linux, so neither failure shows there. Both were found while adopting the template in
EnviroMech on a Mac.

## To apply

```bash
git switch -c macos-fixes main
git am 0001-*.patch 0002-*.patch
just test && just test-generated
```

## 1. Schema pages that differ only by case overwrite each other

`0001-Docs-put-schema-pages-in-a-folder-per-kind-so-case-c.patch`

Every Mech has a `Term` class and a `term` slot. LinkML's gen-doc writes one page per
element into `docs/elements/`, so their pages are `Term.md` and `term.md`: one file on a
filesystem that ignores case. The second overwrites the first, the strict docs build
fails on the links to the lost page, and `just qc` stops at the docs gate.

The patch generates with `subfolder_type_separation`, which gives classes, slots, enums
and types a folder each. Two elements of one kind whose names differ only by case would
still collide, so the generated Mech's `test_schema.py` now refuses them.

To reproduce on a Mac: generate any Mech from `main` and run `just docs-build`. It
aborts in strict mode with broken links to `elements/term.md`.

## 2. Two recipes need bash 4

`0002-Justfile-list-records-with-find-so-the-recipes-run-o.patch`

`validate-terms-all` and `validate-references-all` gather records with
`shopt -s globstar` and a `**` glob. macOS ships bash 3.2, where the `shopt` line fails
and the recipe stops before checking anything, so `just qc-full` fails at both gates.

The patch lists the records with `find`.

To reproduce on a Mac: in any generated Mech, run `just validate-terms-all`. It fails
with `shopt: globstar: invalid shell option name`.

## Checks run

- `just test`: 166 passed.
- `just test-generated`: 9 passed, run after each of the two commits.
- A scratch Mech generated before the change fails `just docs-build` on macOS with 9
  broken-link warnings; with the change it builds with none.
- EnviroMech, generated from the patched template, passes `just qc` (10 gates) and
  `just qc-full` (13 gates) on macOS.
- `scripts/gen_docs.py` produces no changes to the generated documentation pages.

## Note for existing Mechs

The schema pages move from `docs/elements/<Name>.md` to `docs/elements/classes/<Name>.md`,
`slots/`, `enums/` and `types/`. `docs/elements/index.md` stays where it is, and it is
the only schema page the template's nav and docs link to. A Mech that links to an
individual element page by hand needs to update that link after `just update-template`.
