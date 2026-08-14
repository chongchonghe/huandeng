# Talk template

Copy this folder, then write.

```bash
cp -r template talks/2027-my-talk
cd talks/2027-my-talk
typst watch --font-path fonts main.typ out/talk.pdf
```

| | |
| --- | --- |
| `content.typ` | your slides — normally the only file you touch |
| `main.typ` | title, author, theme, colours, footer |
| `globals.typ` | the helpers; shared API, rarely edited |
| `attach/` | images, referenced as `attach/foo.png`; ships only `placeholder.png` |
| `movie-frames/` | one directory of PNGs per movie — starts empty |
| `fonts/` | Fira Sans + Fira Math, so the deck renders the same anywhere |

Fill in `config-info` in `main.typ` first: title, author, institution, short title. The footer reads
`author (short-institution) · short-title · page`.

## Building

```bash
# PDF only — no Python, no build script
typst compile --font-path fonts main.typ out/talk.pdf

# PDF + HTML + PPTX
uv run python tools/build-slides.py talks/2027-my-talk
```

`--font-path fonts` is not optional: without it Typst falls back to another font and the deck
repaginates.

## What you get

`==` starts a slide, `=` starts a section, `#pause` reveals the rest of the slide on the next page.
Helpers in `globals.typ`:

| | |
| --- | --- |
| `#fig(src, credit: [..])` | figure with a source credit; `caption:` above it, `below:` under it |
| `#movie("name")` | an image sequence: flip-book in the PDF, real video in HTML and PPTX |
| `#side-by-side(columns: ..)` | split a slide body into columns |
| `#head-table` / `#plain-table` | tables with and without a header row |
| `#img-row`, `#caption` | a strip of images; a centred grey line |

## Where to look next

- **[`demo/`](../demo/)** — every one of those working, with commentary. The reference deck.
- **[`demo/README.md`](../demo/README.md)** — the movie pipeline, exports, reproducibility, and the
  Touying traps worth knowing before you hit them.

## One rule

After any slide edit, rebuild and check the page count. An overflowing slide does not error — Typst
silently breaks it across two pages.
