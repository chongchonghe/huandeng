# Demo deck

Every feature of the Quarto flavour, working, with commentary. **Read it; do not start from it** — start from [`../template/`](../template/), which is the same machinery with the sample assets stripped out.

Built on [Quarto](https://quarto.org/) and [reveal.js](https://revealjs.com/). It is a port of the Typst + Touying [`demo/`](../../demo/) at the repository root, slide for slide, so you can read the two side by side and see what each toolchain makes easy.

## Files

| File | Purpose |
| --- | --- |
| `_quarto.yml` | Every deck-wide option: slide size, theme, slide level, the title slide's background. The analogue of `main.typ`. |
| `demo.qmd` | The slides. This is the file you edit day to day. |
| `theme.scss` | The look, and every layout class the slides use. Quarto compiles it on top of reveal's default theme. |
| `fonts.html` | Seven `@font-face` rules, injected into `<head>`. They cannot live in `theme.scss` — see [Fonts](#fonts-are-shipped-with-the-deck). |
| `attach/` | Images and video. Reference them as `attach/foo.png`. |
| `fonts/` | Fira Sans, so the deck renders identically off this machine. |
| `ref.bib` | Two references, for the citations slide. |

The deck holds no build logic: `make` is `quarto render`, and everything that needs a browser comes from the shared `../tools/build-slides.py`.

## Writing slides

- `#` starts a section and emits a divider slide
- `##` starts a slide (`slide-level: 2` in `_quarto.yml`)
- `---` adds a slide with no title
- `. . .` reveals the rest of the slide on the next keypress
- `{.class}` and `{key="value"}` on a heading configure that one slide
- `::: {.class}` … `:::` wraps a block; nest by adding colons to the outer fence

## Figures and source credits

Academic slides need a source on every borrowed figure. `.fig` shrink-wraps the image, so the credit sits tight against the image's own bottom-right corner rather than the slide's:

```markdown
::: {.fig}
![](attach/shock.png){width="420px"}

[He et al. 2025]{.credit}
:::
```

A caption goes **above**: a slide is read top to bottom, so it should say what the panel is before the eye reaches it. `.below` is there for the exception — the second half of a paired label, or a note that belongs to the image rather than to the slide.

| part | | |
| --- | --- | --- |
| `[..]{.caption}` | above the image | 80% size, grey, centred on the figure |
| `[..]{.credit}` | under the image | 60% size, grey, right-aligned to the figure's edge |
| `[..]{.below}` | under the credit | 80% size, grey, centred |

Two things make this work, and both are worth knowing before you change them:

- **Size images inside `.fig` in `px` or `pt`, never `%`.** `.fig` is `width: fit-content`, so it sizes itself to the image; a percentage inside it has nothing to resolve against.
- **The labels are `width: 0; min-width: 100%`.** A zero-width child contributes nothing to the parent's intrinsic width, then stretches back out to whatever the image settled on — so a long caption cannot widen the box and drag the credit away from the image's right edge.

For a caption on something `.fig` does not wrap — a table, a Mermaid diagram, a row of images — use `::: {.caption-line}`.

## Rows and grids of figures

`.media-row` is a two-column grid: a label, then a nowrap flex row of images.

```markdown
:::: {.media-row}
::: {.media-label}
FLD:
:::
::: {.media-items}
![](attach/a.png){height="98px"} ![](attach/b.png){height="98px"}
:::
::::
```

Pandoc puts every image written on one Markdown line into a single `<p>`, so that `<p>` has to be a flex row too or the images line-wrap. That is why `theme.scss` styles `.media-items p` as well as `.media-items`.

Stacked rows each size their own label column, so they only line up if you tell them to share a width. Custom properties inherit, so a plain wrapper is enough:

```markdown
::: {style="--label-width: 250px"}
… three .media-row blocks …
:::
```

## Video

The Typst deck samples a folder of PNG frames into a PDF flip-book, because PDF has no video. Here the deck *is* a browser, so there is no pipeline at all: put an `.mp4` in `attach/` and write a `<video>` tag.

```html
<video class="r-stretch video-center" src="attach/clip.mp4"
       controls data-autoplay muted loop></video>
```

- `data-autoplay` — reveal starts it when the slide arrives and rewinds it on the way out
- `controls` — a scrub bar, for when someone asks you to go back
- `muted` — what browsers require before they will autoplay anything
- `r-stretch` — reveal sizes it to the height the slide has left. It must be the **last** element on the slide, and must not be wrapped in a div

For two clips that have to keep their true relative scale, `.video-pair` with `style="flex: <pixel width>"` on each, and a width on the row itself so the taller one stays on the slide.

**Never give a video both a width and a height.** A stretched simulation frame still looks like a plausible figure, which is exactly why nobody catches it. `make check` compares every drawn video and image against its own pixel dimensions and fails past 2%.

### What each format gets

| Format | What you get |
| --- | --- |
| HTML | the deck: real video, fragments, speaker view, the lot |
| standalone HTML | the same in one file, video and fonts and MathJax inlined |
| PDF | two of them — one page per step, and one page per slide. See [Two PDFs, and why](#two-pdfs-and-why). Video prints as its first frame |
| PPTX | Pandoc's re-flow of the Markdown — the text and the images, none of the layout |

## Export

```bash
make            # out/demo.html
make all        # + out/demo.pdf and out/demo.pptx
make standalone # + out/demo-standalone.html
make png        # out/png/slide-001.png …
make check      # look at every slide and say what is wrong
```

Or from the repository root:

```bash
uv run --extra quarto python quarto/tools/build-slides.py quarto/demo
uv run --extra quarto python quarto/tools/build-slides.py quarto/demo --check
```

`--pdf`, `--png` and `--check` drive a headless Chromium through Playwright, because a browser has to lay the slides out before there is anything to measure or print. The rest is `quarto render` with different flags, and you can type those yourself.

## Slide geometry

**There is a frame, and it is exactly 1280 × 720.** `width` and `height` in `_quarto.yml` define a fixed coordinate space; reveal lays every slide out in that box and then scales the whole box uniformly to fit the window. That is the determinism guarantee: `{width="385px"}` is 385/1280 of the screen on any display, at any resolution, and nothing re-flows when the window changes size. Press **X** in the deck (or load it with `?guides`) to draw the boundary and a 24 px keep-clear inset.

`margin: 0.04` removes 4% of the window *in total* — half on each side — before the scale is computed:

```
scale = min(windowWidth / 1280, windowHeight / 720) × (1 − margin)
```

Measured, on the deck as configured:

| window | scale | slide box | empty border, each side |
| --- | --- | --- | --- |
| 1920 × 1080 (16:9) | 1.44 | 1843 × 1037 | 38 px  ·  22 px (= **15 slide-px**) |
| 2560 × 1440 (16:9) | 1.92 | 2458 × 1382 | 51 px  ·  29 px (= **15 slide-px**) |
| 1600 × 1000 (16:10) | 1.20 | 1536 × 864 | 32 px  ·  68 px (= **57 slide-px**) |
| 1440 × 900 (16:10) | 1.08 | 1382 × 778 | 29 px  ·  61 px (= **57 slide-px**) |
| 1512 × 982 (MacBook, 3:2) | 1.13 | 1452 × 816 | 30 px  ·  83 px (= **73 slide-px**) |

The vertical figure is the trap. Reveal does not clip content to the slide box and does not shrink it — the surplus is drawn into that border and cut off by the window edge. On a 16:9 screen only 15 slide-px of it survive; on the 16:10 or 3:2 laptop you are probably writing on, 57 to 73 do. **A slide that looks merely tight while you write it is cut on the projector.** The numbers depend only on aspect ratio, not resolution: a 4K projector is no more forgiving than a 1080p one.

The footer and the slide number live in that same border, below the box, so they never collide with slide content — but on a 16:9 screen they sit within about 15 slide-px of it.

### When the deck does not fill the screen

Three different things look identical — a small deck in a wide empty border — and only one of them is `margin`. Press **X**: the label along the bottom of the box reports all three at once.

```
1280 × 720 · window 1512 × 982 · ar 1.54 · scale 1.13 · fill 41%
```

1. **`fill` is low.** The slide box fills the screen; the *slide* is half empty. This is by far the commonest case — across this demo the median slide uses 61% of the box height, and the emptiest uses 22%. No reveal setting touches it: put more on the slide, make the figures bigger, or raise `$presentation-font-size-root` in `theme.scss` (30 px here, against a 720 px box).
2. **`ar` is not 1.78.** A 16:9 deck on a 16:10 or 3:2 laptop letterboxes — the box is as large as it can be and the leftover is unavoidable. It is not visible on a white slide, because the page behind is white too; it *is* visible while presenting on a display that is not 16:9. Nothing to fix: the deck is built for the projector, not the laptop.
3. **`CAPPED by max-scale` appears.** Reveal refuses to scale past 2× by default, so past about 2560 CSS px wide the deck stops growing and sits in a border that no `margin` will close — at 3200 × 1800 that is a 320 px border left and right. `max-scale: 5` in `_quarto.yml` removes the ceiling; nothing in the deck is a bitmap, so there is no reason to keep it.

### Two PDFs, and why

`make pdf` writes both, from one render:

| file | pages, on this demo | for |
| --- | --- | --- |
| `out/demo.pdf` | 55 — **one page per step** | presenting from, and archiving what the room saw. A build arrives a piece at a time; a flip-book animates. |
| `out/demo-one-page-per-slide.pdf` | 34 — one page per slide, fully built | the handout, and reading the deck back to check it |

Reveal reads config overrides off the query string, so this costs one browser pass each and no second render: `?print-pdf&pdfSeparateFragments=true` for the first, plain `?print-pdf` for the second.

**A `<video>` prints as one still frame.** A page cannot play anything, and nothing can be done about that. When an animation has to survive on paper, use a **flip-book** instead — an `.r-stack` of image frames, each after the first wrapped in `::: {.fragment .fade-in-then-out}`. In the live deck it steps in place like a movie; in `demo.pdf` each frame gets its own page, so twelve frames come out as twelve consecutive pages you can hold an arrow key down through. That is the Quarto flavour's equivalent of the Typst side's `#movie`, and the demo's "A flip-book, in place" slide is the worked example.

### Where the PDF comes from

Quarto has several unrelated PDF paths, and reveal.js is not one of them. `format: pdf` and `format: beamer` go through Pandoc to **LaTeX** (LuaLaTeX by default here) and need a TeX installation; `format: typst` goes through the Typst binary Quarto bundles. `format: revealjs` has **no PDF format at all** — it is a web page, and the PDF comes from printing that page in a browser through reveal's own `?print-pdf` layout. `--pdf` automates exactly that, in headless Chromium.

**So do not reach for `quarto render talk.qmd --to pdf`.** It does not fail; it quietly renders the Markdown as a LaTeX *article* and throws the deck away. Measured on the template: `--to pdf` gives 2 pages of US Letter portrait (612 × 792 pt), where `make pdf` gives 6 pages at 998 × 561 pt, one per slide.

`--to typst` is the same trap without the LaTeX. Quarto's stock `typst` format is a *document* format — an alternative to `format: pdf`, not to `revealjs` — so it also flows the Markdown into a continuous document: slide boundaries gone (6 slides became 4 pages), theme gone, columns collapsed, and `::: notes` printed into the body where an audience would read them. Setting `papersize: presentation-16-9` makes the paper 841.89 × 473.56 pt without making the content slides.

### Typst slides from the same .qmd, via Touying

A Quarto extension **does** bridge `.qmd` to Touying, and it produces genuine slides — [`kazuyanagimoto/quarto-clean-typst`](https://github.com/kazuyanagimoto/quarto-clean-typst), which wraps the [`touying-quarto-clean`](https://typst.app/universe/package/touying-quarto-clean/) Typst package:

```bash
quarto add kazuyanagimoto/quarto-clean-typst
quarto render talk.qmd --to clean-typst
```

Measured on `template/`: 841.89 × 473.56 pt, a title slide, section divider slides for `#` headings, slide numbers, and one page per `##` — no LaTeX and no browser anywhere. It is a real option, and it is worth knowing it exists.

What it is **not** is a PDF of *this* deck. Run on this demo, **34 slides came out as 58 pages** — and Touying's own counter reads "53", so not even the deck agrees with itself. What survives the Markdown round trip, and what does not:

| | |
| --- | --- |
| survives | headings, bullets, tables, code blocks with highlighting, ordinary maths, citations — and Mermaid, which Quarto renders to an image Typst can embed |
| **silently lost** | **video** — `<video>` produces nothing at all, leaving a caption under blank space |
| **silently broken** | **`\class{fragment}{..}` maths** — the whole `$$…$$` prints as raw LaTeX source on the slide |
| re-flowed | every `.columns-*` collapses and the slide then splits across 2–4 pages, stranding `.credit` lines and captions on pages of their own under a repeated title |
| dropped | `.highlight`, `.fig`, `.media-row`, `.absolute`, `.r-stack` (each fragment becomes its own page), the footer, and `theme.scss` entirely — the output wears the extension's Clean theme |
| leaked | `::: notes` printed into the body, where an audience reads it |

None of that is a bug in the extension. Every layout class in this flavour is CSS, and Touying cannot read CSS; the video and fragment cases are simply things a PDF cannot do.

So it is a **third flavour**, not an exporter: same Markdown, different deck. If you want a deck built by Typst, `template/` at the repository root is the supported route and gives you the full Touying API rather than what survives a Markdown round trip.

None of this affects `make pdf`, which has never touched LaTeX: it renders the deck to HTML and prints that page in headless Chromium.

### In the PDF, overflow paginates instead of cutting

Reveal's `?print-pdf` mode wraps each slide in a `.pdf-page` whose height is a whole number of printed pages. A slide that holds too much comes out **two pages tall — the title alone on one page, the body on the next** — which is exactly the silent split the Typst decks get. `--pdf` measures those boxes before printing and names any slide that spills:

```
wrote out/talk.pdf
  3 pages for 2 slides:
    slide 2 (A slide that spills) spills onto 2 pages
```

The PDF page is 997.92 × 561.12 pt — 16:9 to within a rounding error, one page per slide, so it projects with no letterboxing.

### Guaranteeing what the room sees

- **Run `make check`.** It is the only one of these that does not depend on you noticing.
- **Write with the guides on** (`X`). The boundary is the thing you cannot otherwise see.
- **Fonts ship with the deck**, so the metrics that decide where every line breaks cannot change on another machine. That is what `fonts.html` and `fonts/` are for.
- **Present fullscreen (`F`) on a 16:9 display** and the box maps to the screen exactly. On a 16:10 or 4:3 display reveal letterboxes rather than re-flowing — the slide is smaller, never different.
- **If you want no browser in the loop at all, present `out/<deck>.pdf`.** It is one page per slide at 16:9, and `--pdf` has already confirmed no slide split.

## What `make check` looks for

Run it after any slide edit. It walks the built deck one slide at a time and reports:

- **Content past any edge of the slide.** The failure this exists for: a reveal.js slide that holds too much does not error and does not shrink. The surplus hangs into the margin and is then cut by the window edge, and how much survives depends on the window's aspect ratio — see [Slide geometry](#slide-geometry). Sideways is worse: a `.media-items` row is `flex-wrap: nowrap`, so one image too many silently slides off the right.
- **Figures drawn at the wrong aspect ratio**, past 2%. Give an image a width *or* a height, never both.
- **Images that did not load** — a typo in a path is otherwise a blank rectangle you may not notice until the room does.
- **The slide count**, against `--expect N` if you pin one.

Two categories of false alarm are suppressed deliberately, and both are worth knowing if you extend the checker: MathJax lays equations out with spans whose boxes reach well above the ink, and anything inside an ancestor that clips its own overflow — a numbered code block, most obviously — cannot be seen sticking out of it anyway.

## Live preview

```bash
make preview
```

Quarto serves the deck and reloads the browser on every save. There is no editor extension to install.

## Fonts are shipped with the deck

The theme is set in **Fira Sans**, which is not installed on most machines. Rather than depend on that, every deck carries its own copy: `fonts/` holds seven weights, about 1.6 MB, [OFL](https://openfontlicense.org/) and redistributable.

The `@font-face` rules are in `fonts.html`, not in `theme.scss`, and that is not a stylistic choice. Quarto compiles the theme into `<deck>_files/libs/revealjs/dist/theme/`, five directories deep, and a relative `url()` inside a stylesheet resolves against *the stylesheet's* location — so `fonts/FiraSans-Regular.otf` written in `theme.scss` is looked for next to reveal's own theme files and quietly 404s. A `<style>` element in the document resolves against *the document*, which is `out/demo.html`, and `out/fonts/` is exactly where `_quarto.yml`'s `resources:` puts them.

Without the fonts the deck still renders, in whatever sans-serif the machine happens to have, at different metrics, with every line breaking somewhere else. It is a silent failure, which is why it is worth this much explanation.

## Things that surprised us

- **`quarto render` renders nothing** in a project unless `project.render` lists the inputs. `render: ["*.qmd"]` in `_quarto.yml` is what makes `output-dir: out` take effect at all; rendering a single file by name ignores `output-dir` and writes beside the source.
- **reveal caps every image at 95% of its container.** Inside a shrink-to-fit container — an `.r-stack` grid cell, a flex item, a `.fig` — that container is already the image's own width, so the cap squeezes the width by 5% while an explicit `height` holds firm, and the figure comes out stretched. `theme.scss` raises the cap to 100% and leaves the overflow question to `make check`.
- **Slide backgrounds have to be attributes, not CSS.** reveal paints them on a layer of its own, behind and outside the 4% margin, so a `background` in `theme.scss` stops at the margin. `{background-color="#0a6ebd"}` on the heading, or `title-slide-attributes:` in `_quarto.yml` for the title slide.
- **`\class{fragment}{..}` builds an equation up** one term per keypress, and costs nothing but a keypress — unlike Typst's `#pause`, which spends a PDF page each time.
- **`\color{red}{..}`, never `\textcolor`.** The web maths renderer does not define the latter and prints it as literal red error text.
- **Maths comes from a CDN** in a normal render. `make standalone` inlines it along with everything else, which is the version to hand to someone who may be offline.
- **`.gitignore` can eat a source file that happens to share a suffix with an output.** `guides.html` and `reference.pptx` are source; `*.html` and `*.pptx` in a deck folder are otherwise build products. The glob swallowed both, nobody noticed for several commits because the working tree still had them, and a fresh clone died with `unable to open file guides.html` before rendering a single slide. The negations are in `.gitignore` now — and the lesson is that a deck is only really self-contained once you have cloned it somewhere else and built it.
