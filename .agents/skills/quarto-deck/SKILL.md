---
name: quarto-deck
description: Write or edit slides in this repo's Quarto + reveal.js decks (the quarto/ flavour). Use when adding or changing slides in a .qmd, starting a new Quarto talk, inserting a figure with a source credit, adding video or a GIF, exporting to HTML/PDF/PPTX, or debugging a slide whose content runs off the edge. Covers the repo's own theme classes (fig, credit, media-row, columns-N-M) which are NOT part of stock Quarto.
---

# Quarto deck

This repo has two flavours. **Typst + Touying** at the root (`template/`, `demo/`) and **Quarto +
reveal.js** under `quarto/`. They are siblings, not versions: pick per talk, never convert one into
the other. For the Typst flavour use the **slide-deck** skill instead — nothing below applies to it.

A deck here is Quarto Markdown plus a layer of local CSS classes. Stock Quarto knowledge is
[online](https://quarto.org/docs/presentations/revealjs/); **this skill covers what is local and
therefore unguessable.**

Authoritative source is always the code: `quarto/template/theme.scss` defines every class below.
Read it rather than trusting this summary if the two disagree.

## Structure

A deck is five things and contains no build logic:

| | |
| --- | --- |
| `talk.qmd` | the slides — normally the only file you touch |
| `_quarto.yml` | slide size, slide level, theme, title-slide background |
| `theme.scss` | the look, and every class below |
| `fonts.html` | seven `@font-face` rules, injected into `<head>` |
| `guides.html` | the **X** key: draws the 1280x720 slide boundary while you write |
| `attach/` | images and video, referenced as `attach/foo.png` |

Plus `fonts/`, `ref.bib` and a `Makefile`. **Each deck owns its own copies** — a deck copied from an
older template may not have a class you expect. Check that deck's `theme.scss` before using
anything.

## Local classes

```markdown
<!-- Figure with an academic source credit. `.fig` shrink-wraps the image, so the
     credit lines up with the FIGURE's right edge, not the slide's.
     `.caption` goes ABOVE — house default. `.below` is the exception. -->
::: {.fig}
[What it shows]{.caption}

![](attach/x.png){width="420px"}

[He et al. 2025]{.credit}

[After 10 Myr]{.below}
:::

<!-- Columns. Also -1-1, -2-1, -1-2, -2-3, -1-1-1. -->
:::: {.columns-3-2}
::: {.column}
left
:::
::: {.column}
right
:::
::::

<!-- A labelled strip of images on one line. -->
:::: {.media-row}
::: {.media-label}
FLD:
:::
::: {.media-items}
![](attach/a.png){height="98px"} ![](attach/b.png){height="98px"}
:::
::::

::: {.highlight}     <!-- the one sentence the slide is about -->
::: {.caption-line}  <!-- a caption for something .fig does not wrap -->
::: {.video-pair}    <!-- two clips, style="flex: <pixel width>" on each -->
[..]{.alert} [..]{.small} [..]{.tiny} [..]{.muted}
## Thanks! {.focus .center background-color="#0a6ebd"}
```

**Size images inside `.fig` in `px` or `pt`, never `%`** — `.fig` is `width: fit-content`, so a
percentage inside it has nothing to resolve against.

Reveal's own `.incremental`, `.fragment`, `.absolute`, `.r-stack`, `.r-stretch`, `. . .`,
`{background-color=".."}` and `{auto-animate="true"}` all work on top of these.

## Workflows

**New talk** — `cp -r quarto/template talks/2027-my-talk`, then edit `talk.qmd`. Fill in the YAML
block first: title, author, institute, and `footer`, which is the only place the short forms appear.

**Write and look** — `make preview` from the deck. Quarto serves it and reloads on every save.

**Add video** — drop the `.mp4` in `attach/` and write the tag. There is no pipeline and no frame
extraction; that machinery belongs to the Typst flavour, which needs it because PDF has no video.

```html
<video class="r-stretch video-center" src="attach/clip.mp4"
       controls data-autoplay muted loop></video>
```

`r-stretch` must be the **last element on the slide** and must not be wrapped in a div — wrapping
breaks its sizing. For a video beside text, drop `r-stretch` and give it an explicit height.

**Build and export** — every deck has a `Makefile`: `make` for the HTML (Quarto only, no Python),
`make preview`, `make check`, `make png`, `make all` for HTML + PDF + PPTX, `make standalone` for
one self-contained file.

`make pdf` writes **two** files from one render, both printed in headless Chromium — no LaTeX ever:
`out/<deck>.pdf` is one page per *step* (builds arrive a piece at a time, flip-books animate) and
`out/<deck>-one-page-per-slide.pdf` is one page per slide, fully built, for reading and handouts.

**An animation that survives the PDF** is a flip-book, not a video: an `.r-stack` of image frames
with `::: {.fragment .fade-in-then-out}` on each after the first. Live it steps in place; in the
per-step PDF each frame takes its own page. A `<video>` prints as one still frame and nothing can
change that. This is the Quarto flavour's answer to the Typst side's `#movie` — see the demo's
"A flip-book, in place" slide. Use JPEG for frames of dense simulation output; PNG is roughly ten
times the size for no visible gain.

From the repo root instead:
`uv run --extra quarto python quarto/tools/build-slides.py <deck> [--check|--pdf|--png|--pptx|--standalone]`,
and `make check` at the root verifies both flavours at once.

**Convert a PowerPoint or Keynote deck** — there is no Quarto-specific importer. Use
**pptx-to-typst** to extract the media correctly (it reads PowerPoint's own crop rectangles and
corrects video pixel aspect ratio), then re-typeset the text as Markdown rather than Typst.

## House style

The **quarto-revealjs-styles** skill, if installed, carries the author's slide-writing style —
terse bullets, narrative in `::: notes`, readable equations. It applies here unchanged. The
figure-specific rules from the Typst flavour also carry over, because they are about slides, not
about Typst:

- **Figures are drawn too small by default.** A figure is the content of a slide, not an
  illustration beside it. Start near the width the slide allows and come down only if something
  collides.
- **Captions go above the figure**; provenance goes in `.credit`; a statement about the whole slide
  goes in the slide body, not in a caption.
- **Align figures on their tops**, not their centres — `.media-row` and `.columns-*` already do.
- **Left-align prose and panel labels.** Centre titles and figures, not sentences.
- **Shrinking text is the last lever, not the first.** Fix the layout — two columns instead of two
  rows, a shorter sentence, one less bullet — before reaching for `.small`.

## Fixing what does not fit

Change the slide before the theme. A `.small` on that one block, a narrower figure, less text — all
in the `.qmd`. Touch `theme.scss` or `_quarto.yml` only if the default is wrong for *any* deck, or
if you would otherwise repeat the same fix on slide after slide.

Reveal.js does **not** shrink an over-full slide, and `auto-stretch` is off. There is no automatic
rescue: what does not fit hangs off the edge.

## Traps

- **Overflow is silent, and what you see is not what the room sees.** A slide that holds too much
  does not error and does not shrink. Every slide is laid out in a box of exactly 1280x720, scaled
  uniformly to the screen; content past that box hangs into the small margin reveal keeps around it
  and is then cut by the window edge. A 16:10 laptop window leaves about 57 slide-px of that margin
  showing, a 16:9 projector only 15 — so a slide can look merely tight while you write it and be cut
  on stage. Printed, it splits across two PDF pages instead, title on one and body on the next.
  Sideways is worse: `.media-items` is `flex-wrap: nowrap`, so one image too many slides off the
  right with no visual cue at all. `make check` walks the built deck in a headless browser and
  reports all of it; press **X** to see the boundary while you write. Run `make check` after any
  slide edit.
- **A stretched figure is a wrong figure, and nothing errors.** Give an image a width *or* a height,
  never both. `make check` compares every drawn image and video against its own pixel dimensions and
  fails past 2%.
- **reveal caps every image at 95% of its container.** Inside a shrink-to-fit container — an
  `.r-stack` grid cell, a flex item, a `.fig` — the container is already the image's own width, so
  the cap squeezes the width by 5% while an explicit `height` holds firm, and the figure comes out
  stretched. `theme.scss` raises the cap to 100%; a deck copied from an older template may not have
  that fix.
- **Slide backgrounds must be attributes, not CSS.** reveal paints them on a layer of its own,
  behind and outside the 4% margin, so `background:` in `theme.scss` stops at the margin and leaves
  a white frame. Use `{background-color="#0a6ebd"}` on the heading, or `title-slide-attributes:` in
  `_quarto.yml` for the title slide.
- **`quarto render` renders nothing** in a project unless `project.render` lists the inputs.
  `render: ["*.qmd"]` is what makes `output-dir: out` take effect; rendering a single file by name
  ignores `output-dir` and writes beside the source.
- **A relative font URL in `theme.scss` cannot work.** Quarto compiles the theme into
  `<deck>_files/libs/revealjs/dist/theme/`, five levels deep, and `url()` resolves against the
  stylesheet, not the document. Hence `fonts.html` and `include-in-header`. Move those rules into
  the SCSS and the deck silently falls back to another typeface and re-flows every line.
- **`\color{red}{..}`, never `\textcolor`.** The web maths renderer does not define the latter and
  prints it as literal red error text.
- **`\class{fragment}{..}`** builds an equation up one term per keypress. Unlike Typst's `#pause` it
  costs no page — the whole equation stays one slide.
- **Maths comes from a CDN** in a normal render. `make standalone` inlines it with everything else;
  that is the build to hand to someone who may be offline.
- **PPTX is Pandoc's re-flow of the Markdown**, not the deck. Columns, fragments and the theme do
  not survive. It is a delivery format, not a source format.
- **Never `quarto render <deck>.qmd --to pdf`, and never `--to typst`.** `revealjs` has no PDF
  format: the deck is a web page and its PDF comes from printing that page through reveal's
  `?print-pdf` layout, which is what `make pdf` does in headless Chromium — no LaTeX anywhere, ever.
  `--to pdf` does not fail; it quietly renders the Markdown as a LaTeX *article* and throws the deck
  away (measured: 2 pages of US Letter portrait against `make pdf`'s 6 pages at 16:9). Quarto's
  stock `--to typst` is the same trap without the LaTeX — a document format, so slide boundaries,
  theme and columns all go, and `::: notes` gets printed into the body.
- **A .qmd → Touying bridge does exist**, and it makes real slides:
  `quarto add kazuyanagimoto/quarto-clean-typst` then `--to clean-typst` gives 841.89 x 473.56 pt,
  one page per `##`, section dividers, slide numbers, no LaTeX and no browser. But it is a *third
  flavour*, not an exporter for this deck. Run on `quarto/demo`, 34 slides became **58 pages**: every
  layout class here is CSS, so columns collapse and slides split 2–4 ways, `.fig` credits strand on
  pages of their own, `.highlight`/`.media-row`/`.absolute`/`.r-stack` drop, `::: notes` prints into
  the body, and the output wears the extension's theme. Two failures are silent and would reach the
  room: **video renders as nothing** (a caption over blank space) and **`\class{fragment}{..}` maths
  prints as raw LaTeX source**. Mermaid does survive. For a deck genuinely built by Typst, use the
  Typst + Touying flavour at the repository root — the full Touying API instead of what survives a
  Markdown round trip.
- **`.qmd` YAML and `_quarto.yml` merge**, with the `.qmd` winning. Deck-wide options belong in
  `_quarto.yml`; only this talk's identity — title, author, date, footer — belongs in the `.qmd`.
- **`---` in a `.qmd` starts a new slide**, exactly as in the Typst flavour a bare `---` starts a
  new page. Do not write an em dash as `---` in prose.
- **`make check` needs Chromium**: `uv sync --extra quarto && uv run --extra quarto playwright
  install chromium`. `make` and `make preview` need only Quarto.
- **"The deck does not fill the screen" is usually not `margin`.** `margin` removes that fraction of
  the *window* in total, half a side — 0.04 is a 38px border at 1920 wide, nothing like a "huge"
  one. Press **X** and read the label: low `fill %` means the slide itself is half empty (the
  common case, and no setting fixes it); `ar` far from 1.78 means the screen is not 16:9 and the
  letterboxing is unavoidable; `CAPPED by max-scale` means reveal's 2x scale ceiling is holding the
  deck small on a large display, which `max-scale: 5` in `_quarto.yml` removes.

## Verifying

`make png` writes one PNG per slide to `out/png/`, and **look at them**. A clean render says nothing
about whether a slide is legible or whether content spilled off the edge.
