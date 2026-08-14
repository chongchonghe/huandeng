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

## What you get

`##` starts a slide, `#` starts a section, `. . .` reveals the rest of it on the
next keypress. Layout comes from classes in `theme.scss`:

| | |
| --- | --- |
| `::: {.fig}` + `[..]{.credit}` | figure with a source credit; `.caption` above it, `.below` under it |
| `::: {.columns-3-2}` | split a slide into columns; also `-1-1`, `-2-1`, `-1-2`, `-2-3`, `-1-1-1` |
| `::: {.media-row}` | a labelled strip of images, on one line |
| `::: {.highlight}` | the callout for the one sentence a slide is about |
| `[..]{.alert}`, `.small`, `.tiny`, `.center`, `.muted` | inline emphasis and sizing |
| `<video class="r-stretch" …>` | video, sized to whatever height the slide has left |

Reveal.js brings `.incremental`, `.fragment`, `.absolute`, `.r-stack` and `{background-color=".."}` on top of that.

## Where to look next

- **[`../demo/`](../demo/)** — every one of those working, with commentary. The reference deck.
- **[`../demo/README.md`](../demo/README.md)** — the figure and video details, what `make check` looks for, and the Quarto traps worth knowing before you hit them.

## One rule

After any slide edit, run `make check`. A reveal.js slide that holds too much does not error and does not shrink — the surplus hangs off the bottom edge, where your browser window is tall enough to hide it and the projector is not.
