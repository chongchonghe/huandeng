---
name: slide-deck
description: Write or edit slides in this repo's Typst + Touying decks. Use when adding or changing slides, starting a new talk, inserting a figure with a source credit, adding a movie or GIF or an image sequence, exporting to PDF/HTML/PPTX, or debugging a slide that overflows or paginates wrongly. Covers the repo's own helpers (fig, movie, side-by-side, head-table) which are NOT part of stock Touying.
---

# Slide deck

This repo's decks are Typst + Touying with a layer of local helpers. Stock Touying knowledge is in
`.agents/skills/touying-author/`; **this skill covers what is local and therefore unguessable.**

Authoritative source is always the code: `template/globals.typ` defines every helper below.
Read it rather than trusting this summary if the two disagree.

## Structure

A deck is four things and contains no build script:

| | |
| --- | --- |
| `content.typ` | the slides — normally the only file you touch |
| `globals.typ` | shared helpers; imported by the other two, imports neither |
| `main.typ` | theme, fonts, colours, title and outline slides |
| `attach/` | images, referenced as `attach/foo.png` |

Optional: `movie-frames/` (image sequences), `fonts/` (bundled `.otf`).

## Local helpers

**These live in `template/globals.typ`, and therefore in any deck copied from it.** Each
deck owns its own `globals.typ`, so a deck copied from an older template may not have them, and may
define its own instead. **Check the deck's own `globals.typ` before using anything below.**


```typst
// Figure with an academic source credit. Credit is 60% size, grey, right-aligned to the
// FIGURE's edge (not the slide's). First argument takes a path or any content.
// `caption:` goes ABOVE the figure — house default. `below:` is the exception.
#fig("attach/x.png", width: 70%, credit: [He et al. 2025])
#fig("attach/x.png", caption: [Setup], below: [Result], credit: [Smith 2024])

// An image sequence: flip-book in the PDF, real video in HTML and PPTX.
#movie("zoom")              // sampled to a 24-page budget
#movie("zoom", every: 10)   // cadence
#movie("zoom", every: 1)    // every frame

// Layout
#side-by-side(columns: (3fr, 2fr))[left][right]   // splits a slide body, no new slide
#img-row(a, b, c)                                  // horizontal strip, absolute widths only
#caption[Figure 1: ...]                            // centred grey line
#head-table(columns: 3, ..)                        // bold header row
#plain-table(columns: 3, ..)                       // borderless, no header
```

`#slide(composer: ..)` also gives columns but always begins a **new slide** — use `#side-by-side`
inside a slide body.

## Workflows

**New talk** — `cp -r template talks/2027-my-talk`, then edit `content.typ`. The template ships with
an empty `attach/` and `movie-frames/`, so nothing follows you in but the fonts and a `Makefile`.

**Add a movie or GIF** — `uv run python tools/build-slides.py <deck> --add-movie clip.mp4`. Frames
land in `movie-frames/<name>/`; then `#movie("<name>")`. GIF uses the identical command.

**A movie of dense simulation output** — add `--frame-format jpg`. Frames are PNG by default, which
is right for line plots and terminal captures but roughly *ten times* the size for a turbulent
colour field; one real ten-movie deck came to 105 MB as PNG and 53 MB as JPEG at larger
dimensions. A sequence is all one format — the encoder globs a single suffix. `--fps` and
`--max-width` are the other two levers, and they cost quality, so reach for `jpg` first.

**Add a folder of frames you already have** — drop it in `movie-frames/<name>/`, then
`--sync-frames`. The directory name is the movie name.

**Build and export** — every deck has a `Makefile`: `make` for the PDF (Typst only, no Python),
`make watch` to recompile on save, `make check`, `make all` for the three formats. From the repo
root instead: `uv run python tools/build-slides.py <deck>` for all three, `--pdf`/`--html`/`--pptx`
individually, and `make check` to verify every deck at once. Prefer `make` over a hand-typed `typst
compile`, which is easy to run without `--font-path fonts` and thus silently repaginate.

## House style

Learned from a real author's corrections to a dozen slides an assistant had drafted while porting a
deck from PowerPoint. Every one of these fixed a default instinct that was wrong, so apply them up
front rather than waiting to be told.

- **Figures are drawn too small by default.** In that pass every width the author touched went
  *up*: 62→90, 72→90, 42→62, 46→56, 62→82, 92→100. A figure is the content of the slide, not an
  illustration beside it — start near the width the slide allows and come down only if something
  actually collides. When a later fitting pass pushes one back down, it is buying room for a caption
  or fixing an overflow, not expressing a preference for small.
- **Captions go *above* the figure**, and the API now enforces it: `fig`'s argument is `caption:`,
  which always renders above, with `below:` kept for the genuine exception. Four of four were
  flipped by hand before that. **A deck copied before the rename still takes `above:`**, because
  each deck owns its `globals.typ` and a finished talk is frozen. Check the deck's own helper
  before writing either name.
- **Align figures on their tops, not their centres.** A slide is read top to bottom, so panels of
  unequal height should hang from a common line — otherwise a short one floats and its caption
  drifts out of line with its neighbours'. `side-by-side` already does this; `img-row` does since
  the same change. A hand-written `#grid` of figures needs `align: top` written out.
- **A caption says what the panel shows, and nothing else.** "Linear wave analysis", "Supercritical
  radiative shock". Provenance goes in `credit:`; a statement about the whole slide goes in the
  slide body. Two of the author's own corrections were exactly this: "work in prep." was cut from a
  caption, and a sentence describing the whole method was lifted out of one into the body.
- **Do not pad around figures.** The author's comment: *"usually a vspace is not required because
  images have their intrinsic margins."* `fig` already places its own gaps by hand. Four `#v(0.2em)`
  / `#v(0.3em)` spacers were deleted and none added; the only survivors are `#v(0em)` and
  `#v(-0.4em)`, both *removing* space.
- **Left-align prose and panel labels.** Centre titles and the figures themselves, not sentences.
  `#align(center)[Previous codes: operator-split]` became `#align(left)[Previous codes,
  operator-split:]` — note the trailing colon, which makes a label read as one.
- **Shrinking text is the last lever, not the first** — see the same rule in `AGENTS.md`. Every
  size the author touched went up (0.62→0.7, 0.62→0.72, 0.74→0.9) and two shrink wrappers were
  deleted outright; the vertical room came from the layout instead.
- **Name people with their affiliation** when a photo credits a collaborator: "A. Researcher (PhD
  student, Some University)", not the bare name.
- **Bold the letter a symbol stands for** rather than quoting the word: `a #strong("T")ransport and
  a #strong("S")ource term` beats `a "transport" and a "source" term` when the equation above uses
  $T$ and $S$.

## Fixing what does not fit

Change the slide before the theme. A smaller font on that slide, a narrower figure, less text — all
in `content.typ`. Touch `globals.typ` or `main.typ` only if the default is wrong for *any* deck, or
if you would otherwise repeat the same fix on slide after slide. Adding a helper that merely
re-sizes an existing one is the sign you should have fixed the slide.

## Traps

- **Overflow is silent.** Typst breaks an over-tall slide across two pages rather than erroring.
  `build-slides.py <deck> --check` catches it: it counts the pages the source should produce (1 per
  section and per `==` slide, plus one per reveal step), compares with the built PDF, and names the
  slide whose pages share a title but not a slide counter. Fix by shrinking the image or the text.
  A deck that breaks a slide deliberately pins the real number with `--expect N`.
- **A new slide-starting helper must be taught to `--check`.** The estimator counts slides by
  matching `==`, `=` and the known slide functions; adding one (as `statement-slide` was) without
  adding it to that list makes the check under-count by one per call and cry wolf.
- **A bare `---` in prose becomes a page break.** That is Touying's default and the template keeps
  it deliberately (documented as "adds a page under the same title"), so an em-dash written as
  `---` mid-paragraph silently cuts the slide. Either avoid it in prose or disable it per deck with
  `config-common(horizontal-line-to-pagebreak: false)`, which is the right call for a prose-heavy
  deck.
- **`#set text(size: ..)` written into a slide body is file-scoped, not slide-scoped** — it leaks
  into every later slide. Put it inside `#[ .. ]` or one `side-by-side` column. This compounds and
  is easy to miss: five bare `#set text(size: 0.86em)` down a deck leave the last slides at 0.5em,
  which reads as "the theme is a bit small" rather than as a bug. Worse, it hides overflow —
  shrunken slides fit, so `--check` stays green until you scope the sets and four slides overflow
  at once. Grep for `^#set text` before believing a deck is clean — but the grep is only suggestive
  either way: a properly scoped `#[` block whose body is written flush-left matches it too, and an
  indented leak does not. Read the surrounding lines. The scoped idiom is worth knowing: inside
  `#[ .. ]` or one `side-by-side` column, *successive* `#set text` calls each retarget the remainder
  of that block, so a label and the equation under it can take different sizes with no wrapper
  around either.
- **A stretched figure is a wrong figure, and nothing errors.** Never set `fit: "stretch"`; giving
  an `image` both `width:` and `height:` crops instead (Typst defaults to `fit: "cover"`), which
  loses data just as quietly. The subtler source is video: a non-square sample aspect ratio means the
  stored frame is not the displayed frame, so naive frame extraction distorts every frame — in one
  real ten-video deck three were affected, worst case 2.5x. `--add-movie` now
  corrects for it, and `--check` audits every drawn image against its own pixel dimensions.
  When you lay movies out in a grid, **make each column's `fr` its panel's aspect ratio** — that
  gives them one common height without distorting any of them. Re-ingesting a movie can therefore
  change the right column widths: check the new frame dimensions rather than keeping the old `fr`.
- **`~` is a non-breaking space, not a tilde.** `~23%` renders as " 23%". Write "about 23%", or
  `$tilde$` for the maths symbol.
- **Hyphens are legal inside Typst identifiers**, so `#mycode-SF` parses as one name and fails with
  `unknown variable: mycode-SF` rather than substituting `#mycode` and printing `-SF`. Define the
  whole token as its own binding.
- **The CLI and the Python wheel are different Typst versions** (0.14.2 vs 0.15.0 here), so `typst
  compile` can succeed where `build-slides.py` fails. `dot.circle` is the live example: deprecated
  in 0.14, removed in 0.15, and the wheel reports it only as `unknown symbol modifier`. Trust
  `build-slides.py` — it is what builds the deck.
- **`layout did not converge within 5 attempts`** is a *warning*, not an error, and the PDF it
  produces can still be correct — verify with `--check` rather than assuming either way.
  One 80-page deck emits it under the University theme and builds correctly anyway;
  `template/` and `demo/`, same theme, do not. It appears on long decks whose footer displays
  `utils.last-slide-number`: the total feeds back into layout, and a page count that shifts as it
  settles can take more than five passes to fix. Reverting individual slides does not silence it.
- **Related, reported but unconfirmed:** two stacked relative `em` text sizes on one slide are said
  to surface the same non-convergence as `label <foo> does not exist in the document` — an error
  pointing somewhere unrelated. Not reproduced here; treat it as a lead, not as established.
- **Typst cannot list a directory**, which is why `movie-frames/manifest.json` exists and is
  committed. Regenerate with `--sync-frames`.
- **Percentages inside an `auto` grid column have nothing to resolve against** — use absolute
  widths in `#img-row`.
- **`uni-slide` replaces the theme's `slide`** in both `template/` and `demo/`, because University
  hardcodes the footer's colour fills and they cannot be turned off by configuration.
  `uni-section-slide` is in `template/` only — `demo/` has no section slides to fix. A deck on a
  different theme needs neither.
- **`#slide` takes no `title:`** in either University or `uni-slide` — passing one is a hard error
  (`unexpected named arguments`). Use `#empty-slide[..]` for a slide without chrome.
- **`#show: appendix` freezes only the slide *total*, not the current counter**, so backup slides
  read "36 / 34" unless you also set `config-common(freeze-slide-counter: true)`.

## Verifying

Render pages to PNG with PyMuPDF and **look at them**. Check the page total. A clean compile says
nothing about whether a slide is legible or whether content spilled.
