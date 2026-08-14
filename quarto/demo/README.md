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
| PDF | one page per slide, printed through reveal's own `?print-pdf` layout; video appears as its poster frame |
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

## What `make check` looks for

Run it after any slide edit. It walks the built deck one slide at a time and reports:

- **Content past any edge of the slide.** The failure this exists for: a reveal.js slide that holds too much does not error and does not shrink. The surplus simply hangs below the bottom edge, invisible in a tall browser window and plainly visible on a projector. Sideways is worse — a `.media-items` row is `flex-wrap: nowrap`, so one image too many silently slides off the right.
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
