---
name: site-design
description: >-
  Change how the EnviroMech documentation site and record browser look:
  colors, light or dark mode, title, footer, the columns of the browser's
  front page, the sections shown on record pages, and deeper changes to the
  page templates. Use when asked to restyle, rebrand, recolor or reorganize
  the site, or when the site is hard to read.
---

# Site design

Most changes are one line in `conf/site.yaml`. Start there. Edit the page
templates only for what the settings cannot do.

## Settings: `conf/site.yaml`

| Setting | What it does | Values |
|---|---|---|
| `title` | Title of the record browser's front page | text |
| `palette` | Main color: docs header, browser header band, links | red, pink, purple, deep-purple, indigo, blue, light-blue, cyan, teal, green, light-green, lime, yellow, amber, orange, deep-orange, brown, grey, blue-grey |
| `accent` | Hover and focus color | the palette names except brown, grey, blue-grey |
| `banner` | The record browser's header band and links, `#rrggbb`; the docs site is not affected | a hex color; leave out to use `palette` |
| `highlight` | Left edge of cards and of the top box on a record page, the selected tab and page number, the dismech boxes in the graph | a hex color; leave out to use the banner color |
| `tint` | Wash behind counts and chips | a hex color; leave out to derive it from `highlight` |
| `hover` | Background of a hovered link | a hex color; leave out for none |
| `theme` | Light or dark pages, for both sites | `auto` (follows the visitor's system), `light`, `dark` |
| `index_columns` | Columns of the front page, which lists every record, in order; the first links to the record | record field names, e.g. `name`, `id`, `status` |
| `kind_columns` | Columns of each record kind's own list view; a kind left out uses `index_columns` | a mapping of record kind (`AOP`, `Key Event`, `Observation`) to its column names |
| `hidden_sections` | Record sections left off browser record pages; the data keeps them | record field names |
| `footer` | Footer on every browser page | text |

The names are Material for MkDocs' own, so one name colors both sites.

After any change:

```bash
just site-check     # validates the file and reports contrast
just docs-serve     # look at both sites at http://127.0.0.1:8000
```

## Choosing colors

- Pick for the domain, not for decoration. A palette the maintainers
  already use (a lab or project color) is a good choice.
- Readability is handled for links: the browser darkens or lightens the
  palette color until it reaches 4.5:1 against the page, and picks black or
  white header text, whichever reads better. `just site-check` shows the
  final colors. The docs site uses Material's own pairings, which for a few
  light palettes (cyan, light-green, and similar) put white text under 3:1
  on the header; prefer a darker palette if the docs header must be
  readable.
- Ask the person before changing an established color. It is part of how
  people recognize the site.

## Earlier color schemes

Each scheme the site has had is a commit on the `ui-updates` branch (PR #58),
so it can be looked at and brought back. The page surface (background, borders,
text) is in `style.css`, not in `site.yaml`, so a scheme is the settings below
plus that file's colors at the same commit.

| Scheme | Commit | Settings | Page surface |
|---|---|---|---|
| **AOP-Wiki: charcoal and green** (current) | the commit that added it | `banner #3b3f3f`, `highlight #b5d5a7`, `tint #e3f0dc`, `hover #e3f0dc`, `theme light` | off-white `#fafaf7`, grey borders `#d6d6d6` |
| **Green and lilac** (tag `theme-green-lilac`) | `a276d98` | `banner #2f5d1f` (the logo's dark green), `highlight #4b2f7f` (dark purple), `theme light` | pale sage `#f3f6ee`, sage borders `#d4dcc6` |
| SAAOP green on ivory | `eb724c9` | `banner #297c2b`, `theme light` | pale ivory `#fbf7ec` |
| Original | `e712e54` (`main`) | `palette indigo`, `accent indigo`, `theme auto` | grey `#f6f6f8`, with a dark scheme |

To look at one without touching your work, make a second checkout and open its
pages:

```bash
git worktree add ../enviromech-theme theme-green-lilac    # or a commit from the table
cd ../enviromech-theme && just render && open pages/index.html
```

To bring one back, copy its values from the table into `conf/site.yaml` and the
page surface colors into the `light` block at the top of `style.css`. Do not
check out the old files over the current ones: `site.py` and `style.css` have
had other fixes since, and the old copies would undo them.

The tag is local to the checkout that made it. If the branch is squash-merged
the commit hashes above stop resolving, so push the tag (`git push origin
theme-green-lilac`) or keep a branch at that commit.

The AOP-Wiki logo also has a pastel yellow (`#ffe599`) and red (`#ee9b9b`)
that this scheme does not use yet; its green (`#b5d5a7`) and charcoal
(`#333838`) are the ones in use.

## Beyond the settings

A record page is laid out from the shape of the data and the schema, by
`src/enviromech/render.py`. Its docstring lists the rules: an overview
table for simple values, tables for lists of small uniform objects, cards
for curated mentions and richer objects, quote cards for evidence.

Field labels come from the schema. To rename one on the page, give the slot
a `title` in the schema; do not special-case it in a template. Its
`description` is the help text under the section heading, so a thin page
is fixed by improving the schema.

The page frames are Jinja templates in `src/enviromech/templates/`:

| File | Page |
|---|---|
| `list.html` | one list view: sortable, filterable. Rendered once per view, to `index.html` and to one page per record kind |
| `record.html` | one record: header, overview, section menu, sections |
| `style.css` | the stylesheet; colors arrive as variables from `conf/site.yaml` |

To change how a kind of value is drawn (say, show a list as cards rather
than a table), change the rule in `render.py` and keep its docstring true.

## The list views

The browser has one list view per record kind, and the mixed view over every
record as its front page. `render.views` builds them; `render.KINDS` is the
ordered list of kinds that get one, and a kind with no records gets no view.
`kind_columns` in `conf/site.yaml` gives each kind its columns, because an AOP
and a Key Event are not described by the same ones. A column names a field of
the record and may reach into a nested one with dots (`event.short_name`); a
column no field holds is derived in `render.list_cells` — the counts
(`key_events`, `ke_relationships`, `dismech_nodes`, `dismech_models`), a Key
Event's `level`, `level_screening` and `aop_wiki_id`, and the `aops` it appears
in with its role in each. To add a column of a kind the records do not hold,
derive it there and give it a heading in `DERIVED_LABELS`; everything the
schema does name takes its heading from the schema, as above.

Changing `KINDS` changes the views. Assays, test guidelines and event
components are record kinds with no pages of their own, so they are not in it:
a row of theirs would link nowhere. Giving them views means giving them record
pages first, and counting them in `report.py` so the browser and
`docs/corpus.md` agree.

Rules:

- Keep colors in `conf/site.yaml`. In `style.css`, use the `var(--...)`
  names, never a new literal color.
- Keep every link relative. The site is hosted under a path, and the
  record browser sits inside the docs site at `/records/`.
- After editing a template or `render.py`, look at the result with
  `just docs-serve` at desktop and phone widths. `pages/` is not committed;
  the docs build renders the browser fresh.

The docs site's layout is `mkdocs.yml`; its pages are `docs/`. Never edit
`.mkdocs.site.yml`, `site/`, or `docs/records/`: they are generated.

If a request needs a setting that does not exist yet (a logo, a second
table layout), add it to `conf/site.yaml`, read it in `site.py` and the
templates, document it in this skill, and say so in the pull request.
