# Exports

## The targets

From inside a deck:

```bash
make              # out/<deck>.html          Quarto alone, nothing else needed
make preview      # the same, reloading on every save
make check        # render, then look at every slide
make png          # out/png/slide-001.png …  one per slide, to read
make pdf          # both PDFs
make pptx         # slide images
make standalone   # one self-contained .html
make all          # HTML + PDFs + PPTX
make gallery      # every theme rendered side by side — out/gallery.html
make clean        # delete out/
```

From the repository root, `make check` verifies every deck at once. `uv run python
tools/build-slides.py <deck> [--check|--pdf|--png|--pptx|--standalone|--html]` is the same tool
directly.

`make` and `make preview` need only Quarto, so they still work in a deck copied anywhere. Everything
else needs Python and Chromium.

**Do not run `make clean` after working** — leave the built HTML for the author to look at.

## What each output is

| output | what it is |
| --- | --- |
| `out/<deck>.html` | the deck, with its assets beside it. What you present. |
| `out/<deck>-standalone.html` | the same in one file — fonts, images, video and MathJax inlined. Email this; it opens offline. |
| `out/<deck>.pdf` | **one page per step**. Builds arrive a piece at a time, flip-books animate. Present from this if you cannot use a browser. |
| `out/<deck>-one-page-per-slide.pdf` | one page per slide, fully built. The handout, and what to read when checking a deck. |
| `out/<deck>.pptx` | one full-bleed slide image per page at 3840 px. Not editable; pixel-identical to the deck. |

Both PDFs come from **one render**: reveal reads config overrides off the query string, so
`?print-pdf&pdfSeparateFragments=true` and plain `?print-pdf` give the two paginations without
re-rendering. `--pdf` also reports any slide that splits onto two pages.

`--pptx` rasterises the per-step PDF. `--width` sets sharpness as a pixel width (default 3840, a 4K
projector); `--dpi` overrides it outright.

## What does not survive

- **Video prints as one still frame.** A page cannot play anything. For an animation that survives,
  use a flip-book — see `media.md`.
- **`\class{fragment}` maths** does not survive any non-browser export.
- Anything that is CSS — the column grids, `.fig` credits, `.media-row`, `.highlight`, `.absolute` —
  survives the browser exports and nothing else.

## Only a browser can render this deck

The layout is CSS. Three separate attempts to produce a PDF or PPTX by another route all failed the
same way. **Read `trash/README.md` before proposing any of them again** — it has the measurements.

| route | what happened |
| --- | --- |
| `quarto render --to pdf` | Pandoc → LuaLaTeX. Renders the Markdown as a LaTeX **article**: 2 pages of US Letter portrait against `make pdf`'s 6 pages at 16:9. The deck is gone. |
| `quarto render --to typst` | Same shape without the LaTeX — a document format, not a slide format. `papersize: presentation-16-9` gives 16:9 paper and still one continuous flow. |
| `kazuyanagimoto/quarto-clean-typst` (Touying bridge) | Makes *real* slides, but on this demo 34 slides became **58 pages**: columns collapse, `.fig` credits strand, video renders as nothing, `\class{fragment}` maths prints as raw LaTeX, `::: notes` prints into the body. |
| Pandoc's native PPTX writer | Reaches the theme fonts and colours through a `reference-doc` and no further. A bulleted outline wearing none of the design. |

So `--pdf` prints the built deck in headless Chromium through reveal's own `?print-pdf` layout, and
`--pptx` rasterises that PDF. No LaTeX is involved at any point, and never has been.

## Requirements

```bash
uv sync
uv run playwright install chromium
```

No Node.js. The usual route to a reveal.js PDF is `decktape`, which needs npm; driving reveal's own
print layout through Playwright does the same job with the dependency the checker needs anyway.
