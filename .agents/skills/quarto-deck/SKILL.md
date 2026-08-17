---
name: quarto-deck
description: Build, edit and troubleshoot Quarto + reveal.js slide decks in this repo. Use when adding or changing slides in a .qmd, starting a new talk, inserting a figure with a source credit, adding video or animation, writing equations, exporting to HTML/PDF/PPTX, changing the theme, or debugging a slide whose content runs off the edge. Bundles the reference docs, so this needs no web lookup.
---

# Quarto deck

Slide decks in Quarto Markdown, rendered by reveal.js, with a layer of local CSS classes and one
shared Python tool. This skill and its `docs/` cover the machinery. For the *words* — how terse a
bullet should be, how to write an equation for a reader, what to verify before stating a number —
invoke **quarto-academic-style**, which builds on this one. Skills do not load each other; ask for
it by name.

Authoritative source is always the code: the deck's own `theme.scss` defines every class, and
`demo/demo.qmd` demonstrates every one of them under `make check`. Read those rather than trusting
a summary if the two ever disagree.

## Use the bundled docs

Read only the file the task needs; do not load the whole tree.

| read | when you are |
| --- | --- |
| `docs/slides.md` | structuring a deck — headings, `slide-level`, per-slide attributes, fragments, auto-animate, speaker notes |
| `docs/layout.md` | placing things — columns, `.absolute` and centring, `.r-stack`, emphasis classes, tables |
| `docs/figures.md` | inserting a figure — `.fig`, credits, sizing, aspect ratio, rows and grids of images |
| `docs/media.md` | adding video, a GIF, or an animation that survives the PDF |
| `docs/math.md` | writing equations — the renderer's quirks, colour, multi-line, building up |
| `docs/citations.md` | citing anything, and the References slide you must not forget |
| `docs/theme.md` | changing the look — `theme.scss`, fonts, the title slide, adding a class |
| `docs/geometry.md` | something does not fit, or the deck looks small on screen |
| `docs/exports.md` | producing HTML, PDF, PPTX — and why other routes were abandoned |

The worked examples are not vendored here: `demo/demo.qmd` and `demo/theme.scss` in this repository
are the reference, and unlike a copy they are build-verified on every commit.

## Structure

A deck is six things and contains no build logic:

| | |
| --- | --- |
| `talk.qmd` | the slides — normally the only file you touch |
| `_quarto.yml` | slide size, slide level, theme, title-slide background |
| `theme.scss` | the look, and every local class |
| `fonts.html` | the deck's own copy of Fira Sans, injected into `<head>` |
| `guides.html` | the **X** key: draws the 1280×720 slide boundary while you write |
| `attach/` | images and video, referenced as `attach/foo.png` |

Plus `fonts/`, `ref.bib` and a `Makefile`. **Each deck owns its own copies** — a deck copied from an
older template may lack a class you expect. Check that deck's `theme.scss` first.

## The local classes

These are not stock Quarto. Full detail in `docs/layout.md` and `docs/figures.md`.

```markdown
::: {.fig}                       figure + academic source credit
[What it shows]{.caption}        above    ·  [He et al. 2025]{.credit}  right, at the figure's edge
![](attach/x.png){width="420px"} px or pt, never % inside .fig
[After 10 Myr]{.below}           under the credit
:::

:::: {.columns}                  50/50 — prefer this; Pandoc maps it to a real PPTX two-column slide
:::: {.columns-3-2}              also -2-1, -1-2, -2-3, -1-1-1

:::: {.media-row}                a labelled strip of images on one line
::: {.media-label} FLD: :::
::: {.media-items} ![](a.png){height="98px"} ![](b.png){height="98px"} :::
::::

::: {.highlight}                 the one sentence the slide is about
::: {.caption-line}              a caption for something .fig does not wrap
::: {.video-pair}                two clips at their true relative scale
[..]{.alert}  [..]{.muted}  .small  .tiny  .center  .no-header
## Thanks! {.focus .center background-color="#0a6ebd"}
```

Reveal's own `.incremental`, `.fragment`, `. . .`, `.absolute`, `.r-stack`, `.r-stretch`,
`{background-color=".."}` and `{auto-animate="true"}` work on top of these.

## Workflows

**New talk** — `cp -r template talks/2027-my-talk`, then edit `talk.qmd`. Fill in the YAML block
first: title, author, institute, and `footer`, the only place the short forms appear.

**Write and look** — `make preview` from the deck; Quarto serves it and reloads on every save.
Press **X** to see the slide boundary.

**Build** — `make` for the HTML, `make all` for everything, `make check` after any slide edit.
Details and the full target list in `docs/exports.md`.

## Rules that prevent silent breakage

Each of these fails without an error message.

1. **After ANY slide edit, run `make check`.** An over-full slide neither errors nor shrinks — the
   surplus hangs off the edge, and a 16:10 laptop shows about 57 slide-px of it where a 16:9
   projector shows 15. So it can look merely tight while you write and be cut on stage. Sideways is
   worse: a `.media-items` row runs off the right with no cue at all. `docs/geometry.md`.
2. **Give an image a width *or* a height, never both.** A stretched scientific figure still looks
   plausible, which is why nobody catches it. `make check` fails past 2%. `docs/figures.md`.
3. **`@font-face` lives in `fonts.html`, not `theme.scss`.** A relative font URL cannot work from a
   compiled Quarto theme; the deck silently falls back to another typeface and re-flows every line.
   `docs/theme.md`.
4. **`\color{red}{..}`, never `\textcolor`.** The renderer here does not define the latter and
   prints it as literal red error text. `docs/math.md`.
5. **A References slide is mandatory if you cite anything** — otherwise the bibliography lands
   outside every section and reveal paints it over every slide. `docs/citations.md`.
6. **Never `--to pdf`, `--to typst`, or Pandoc's PPTX writer.** They do not fail; they quietly
   produce a document that is not your deck. `docs/exports.md` and `trash/README.md`.
7. **A `.gitignore` glob can eat a source file.** `fonts.html` and `guides.html` share a suffix with
   build output. `guides.html` went missing for several commits this way. Add a negation for any new
   source file whose extension collides, and verify with a fresh clone.
8. **Edit `talk.qmd`.** `theme.scss` is shared API and `_quarto.yml` is configuration; changing
   either affects every slide.
9. **Never edit `template/` to write a talk.** Copy it into `talks/` first.

## Style that is not personal taste

The house preferences live in **quarto-academic-style**. These few are just how the toolchain works
best:

- **Prefer Markdown and Pandoc attributes over raw HTML.** `![](x.png){width="200pt"}`, not an
  `<img style="..">`. Reach for HTML only where Quarto cannot express the intent — `data-autoplay`
  on a `<video>` is the usual case.
- **Intra-slide subheadings start at `####`.** `##` is the slide title; `###` competes with it.
- **Fix fitting problems in the slide, not the theme**, and reach for the layout before the font
  size. `docs/geometry.md`.
- **Keep comments that record intent or preserve recoverable material** —
  `<!-- Keep this derivation hidden unless the backup slide is restored. -->`. Delete empty ones and
  conversion artefacts.

## Verifying

`make png` writes one PNG per slide to `out/png/`, and **look at them**. A clean render says nothing
about whether a slide is legible or whether content spilled off the edge.
