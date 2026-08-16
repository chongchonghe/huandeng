# Talk template

Copy this folder, then write.

```bash
cp -r quarto/template talks/2027-my-talk
cd talks/2027-my-talk
make preview
```

| | |
| --- | --- |
| `talk.qmd` | your slides — normally the only file you touch |
| `_quarto.yml` | slide size, theme, and every deck-wide option |
| `theme.scss` | the look: colours, type, the layout classes |
| `fonts.html` | ships Fira Sans with the deck; see the note inside |
| `guides.html` | the **X** key: draws the 1280 × 720 slide boundary while you write |
| `attach/` | images and video, referenced as `attach/foo.png` |
| `fonts/` | Fira Sans, so the deck renders the same anywhere |
| `ref.bib` | citations, if the talk has any |

Fill in the YAML block at the top of `talk.qmd` first: title, author, institute, and the `footer` line, which is the only place the short forms appear.

## Building

```bash
make            # render out/talk.html — Quarto alone, nothing else needed
make preview    # the same, in a browser that reloads as you save
make check      # render, then look at every slide
make all        # HTML, PDF and PPTX
make standalone # one self-contained .html to email
```

`make pdf` writes two files, printed from the built deck in headless Chromium — no LaTeX anywhere:

| | |
| --- | --- |
| `out/talk.pdf` | one page per **step**, so builds and flip-books survive; present from this |
| `out/talk-one-page-per-slide.pdf` | one page per slide, fully built; the handout |

A `<video>` prints as one still frame. For an animation that survives on paper, use an `.r-stack` of image frames with `::: {.fragment .fade-in-then-out}` on each after the first — every frame then gets its own PDF page.

`make pptx` rasterises that PDF into `out/talk.pptx`, one full-bleed image per slide at 3840 px wide — a source pixel behind every pixel of a 4K projector. Nothing is editable in PowerPoint; in exchange the deck arrives looking like itself, which Pandoc's native writer cannot manage because the layout is CSS. For a different size, run the tool directly with `--width 5120` or `--width 1920`.

## What you get

`##` starts a slide, `#` starts a section, `. . .` reveals the rest of it on the
next keypress. Layout comes from classes in `theme.scss`:

| | |
| --- | --- |
| `::: {.fig}` + `[..]{.credit}` | figure with a source credit; `.caption` above it, `.below` under it |
| `::: {.columns}` | a 50/50 split — prefer this one, it is the class Pandoc understands, so PPTX gets real columns |
| `::: {.columns-3-2}` | other ratios; also `-2-1`, `-1-2`, `-2-3`, `-1-1-1` |
| `::: {.media-row}` | a labelled strip of images, on one line |
| `::: {.highlight}` | the callout for the one sentence a slide is about |
| `[..]{.alert}`, `.small`, `.tiny`, `.center`, `.muted` | inline emphasis and sizing |
| `<video class="r-stretch" …>` | video, sized to whatever height the slide has left |

Reveal.js brings `.incremental`, `.fragment`, `.absolute`, `.r-stack` and `{background-color=".."}` on top of that.

## Where to look next

- **[`../demo/`](../demo/)** — every one of those working, with commentary. The reference deck.
- **[`../demo/README.md`](../demo/README.md)** — the figure and video details, what `make check` looks for, and the Quarto traps worth knowing before you hit them.

## One rule

After any slide edit, run `make check`. A reveal.js slide that holds too much does not error and does not shrink — the surplus hangs into the margin and is then cut off by the window edge, and a 16:10 laptop shows about 57 slide-px of it where a 16:9 projector shows 15. So a slide can look merely tight while you write it and be cut on stage. Press **X** to see the boundary while you work.
