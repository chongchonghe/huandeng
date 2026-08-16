# 幻灯 Huandeng — Quarto flavour

**The same idea as the [Typst decks](../README.md) at the repository root, built on [Quarto](https://quarto.org/) and [reveal.js](https://revealjs.com/) instead: slides in plain Markdown, a checker for the failures that do not raise an error, and agent skills so an LLM can help without taking the wheel.**

The two flavours are siblings, not versions. Neither is deprecated, and a deck written in one is never converted into the other — you pick per talk.

## Quick start

```bash
brew install --cask quarto                          # or see quarto.org
git clone https://github.com/chongchonghe/huandeng.git
cd huandeng
cp -r quarto/template talks/my-talk                 # your copy — leave the template alone
cd talks/my-talk
make preview
```

A browser opens on the deck and reloads every time you save. Edit `talk.qmd`, and it is your deck.

| | |
| --- | --- |
| `make` | render `out/talk.html` |
| `make preview` | the same, reloading as you save |
| `make check` | render, then look at every slide for the things that fail silently |
| `make all` | also write a PDF and a PowerPoint file |
| `make standalone` | one self-contained `.html` you can email |
| `make png` | one PNG per slide, so you can read them |

`make` and `make preview` need nothing but Quarto. The rest need Python and a headless browser — see [Requirements](#requirements).

Read [`demo/`](demo/) for every feature working at once, and [`demo/README.md`](demo/README.md) for the detail.

## Which flavour should I use?

Both produce a deck you present from, a page you can send to anyone, and a PowerPoint for the conference that insists on one. They differ in what they are good at.

| | Typst + Touying | Quarto + reveal.js |
| --- | --- | --- |
| **the deck you present** | a PDF — opens anywhere, needs nothing | a web page — needs a browser, which every machine has |
| **video** | a sampled flip-book in the PDF, real video in the HTML | real video everywhere, from an `.mp4` you drop in `attach/` |
| **layout** | a real programming language, and a compiler that reports overflow | CSS, which is more familiar and far more flexible |
| **maths** | native, no renderer, no network | MathJax, from a CDN unless you build `standalone` |
| **build** | one fast binary, no browser | Quarto for the HTML; a browser for the PDF and the checks |
| **a reveal costs** | a PDF page each | nothing |
| **diagrams** | `fletcher`, drawn by the compiler | Mermaid, built into Quarto |
| **it is best at** | a deck that must open on someone else's laptop in ten years | a deck with video, animation, or a layout you want to fiddle with |

If you are writing a conference talk with three simulation movies in it, this flavour is easier. If you are writing lecture notes you will hand out as a PDF and reuse for a decade, use the Typst one.

## What you get

| | |
| --- | --- |
| **One source, five outputs** | HTML, a single self-contained HTML, two PDFs and a PPTX — from the same `talk.qmd` |
| **A PDF that keeps the builds** | `make pdf` writes one page per *step* to present from, and one page per slide to hand out. Printed in headless Chromium, so it is the deck you wrote — no LaTeX anywhere |
| **Video that needs no pipeline** | an `.mp4` in `attach/` and one `<video>` tag; reveal starts it on the slide and rewinds it on the way out. For an animation that survives the PDF too, a flip-book of frames steps in place live and takes one page per frame on paper |
| **A checker for silent failures** | a reveal.js slide that holds too much does not error and does not shrink — it hangs off the edge, and how much of that the room sees depends on the screen's aspect ratio. `make check` catches it, catches figures drawn at the wrong aspect ratio, and catches images that never loaded |
| **A visible slide boundary** | every slide is laid out in exactly 1280 &times; 720 and scaled to the screen; press **X** to draw that box while you write. See [Slide geometry](demo/README.md#slide-geometry) |
| **Figures with academic credits** | `::: {.fig}` puts the credit against the figure's own edge, not the slide's |
| **Agent skills** | `quarto-deck` for authoring; `slide-deck` and `pptx-to-typst` remain for the Typst flavour |
| **Decks that do not rot** | every deck owns its copies of the theme, the fonts and the assets, so it still renders years later, moved anywhere |

## Layout

```
quarto/
  tools/build-slides.py   the browser-backed half: --check, --pdf, --png
  template/               the starting point. Copy it; never edit it in place.
  demo/                   every feature, working, as a reference deck
  Makefile                make check verifies every Quarto deck at once
talks/                    yours — shared with the Typst flavour, gitignored
```

A deck is `talk.qmd` + `_quarto.yml` + `theme.scss` + `fonts.html` + `attach/`, plus a `Makefile` that wraps the commands above and holds no build logic of its own.

## Requirements

- **[Quarto](https://quarto.org/docs/get-started/)** for the HTML. Nothing else is needed if that is all you want.
- **Python 3.13, [uv](https://docs.astral.sh/uv/), and Chromium** for `make check`, `make pdf` and `make png`:

  ```bash
  uv sync --extra quarto
  uv run --extra quarto playwright install chromium
  ```

  Chromium is about 150 MB and is kept out of the base dependencies, so a Typst-only checkout never downloads it.
- **ffmpeg**, only if you need to convert a video into something a browser will play.

There is no Node.js requirement. The usual way to get a PDF out of reveal.js is `decktape`, which needs npm; driving reveal's own `?print-pdf` layout through Playwright does the same job with a dependency the checker needs anyway.

## Every deck is self-contained

The same rule as the Typst flavour, for the same reason. `theme.scss`, `_quarto.yml`, `fonts.html`, `fonts/` and every asset are **copies**, not imports, and no deck reads anything outside its own directory.

The cost is real: improving `template/` does not reach a talk you already copied, and carrying a fix across means copying it in by hand. What you buy is that a finished talk is frozen. A deck you gave in 2026 renders identically in 2030, on a different machine, after the template has moved on — because nothing it depends on can change underneath it.

`out/` is not committed and never needs to be.

## Credits

Built on [Quarto](https://quarto.org/) and [reveal.js](https://revealjs.com/). Fonts are [Fira Sans](https://github.com/mozilla/Fira), SIL OFL.

MIT licensed. See [LICENSE](../LICENSE).
